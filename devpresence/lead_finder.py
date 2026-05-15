from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlparse, urlunparse, urlencode

from ddgs import DDGS

try:
    from config import GEMINI_API_KEY
except ModuleNotFoundError:
    from devpresence.config import GEMINI_API_KEY

OUTPUT_FILE = Path(__file__).resolve().parents[1] / "leads_found.txt"

ACTIVE_INTENT_PHRASES = [
    "looking for",
    "need",
    "hiring",
    "seeking",
    "recommend",
    "who can",
    "can someone",
    "need help",
    "request for",
    "wanted",
    "open to",
]

SERVICE_TERMS = [
    "booking app",
    "booking system",
    "management app",
    "management tool",
    "internal tool",
    "business dashboard",
    "dashboard",
    "wix",
    "wix store",
    "canva website",
    "canva designer",
    "coach",
    "consultant",
    "solopreneur",
    "ai saas",
    "saas mvp",
    "lovable",
    "supabase",
    "replit",
    "make.com",
    "zapier",
    "crm",
    "flutterflow",
    "flutterflow app",
    "stripe",
    "paypal",
    "razorpay",
    "api integration",
    "automation",
]

SEARCH_QUERIES = [
    'site:reddit.com "looking for a developer" "booking app"',
    'site:reddit.com "need help" "wix"',
    'site:reddit.com "hiring" "canva designer"',
    'site:reddit.com "looking for" "ai saas"',
    'site:reddit.com "need" "zapier" OR "make.com"',
    'site:reddit.com "looking for" "flutterflow"',
    'site:reddit.com "need help integrating" "stripe"',
    'site:linkedin.com/posts "looking for" "developer" "booking"',
    'site:linkedin.com/posts "looking for" "wix"',
    'site:linkedin.com/posts "looking for" "canva" "coach"',
    'site:linkedin.com/posts "hiring" "supabase" "replit"',
    'site:linkedin.com/posts "looking for" "zapier" "crm"',
    'site:discord.com/invite founders startup website builder',
    'site:join.slack.com founders startup website automation',
]


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    clean_query = urlencode(
        [(key, value) for key, value in parse_qsl(parsed.query) if not key.lower().startswith("utm_")]
    )
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, clean_query, ""))


def _guess_source(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "reddit.com" in host:
        return "reddit"
    if "linkedin.com" in host:
        return "linkedin"
    if "discord" in host:
        return "discord"
    if "slack" in host:
        return "slack"
    return host.replace("www.", "") or "web"


def _heuristic_score(title: str, snippet: str, url: str) -> tuple[int, bool, str]:
    combined = f"{title} {snippet} {url}".lower()
    score = 0

    if any(phrase in combined for phrase in ACTIVE_INTENT_PHRASES):
        score += 35
    if any(term in combined for term in SERVICE_TERMS):
        score += 40
    if any(domain in combined for domain in ["reddit.com", "linkedin.com", "discord", "slack"]):
        score += 10
    if any(term in combined for term in ["founder", "owner", "business", "startup", "coach", "consultant", "solopreneur"]):
        score += 10
    if any(term in combined for term in ["community", "invite", "group", "server", "workspace"]):
        score += 5

    score = min(score, 100)
    keep = score >= 50
    reason = "heuristic match" if keep else "too vague"
    return score, keep, reason


def _extract_json(text: str) -> Any:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return json.loads(cleaned)


def _gemini_refine(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not GEMINI_API_KEY or not candidates:
        return candidates

    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-3.1-pro-preview")

        prompt = (
            "You are ranking lead-search results for a freelance developer. "
            "STRICT RULES:\n"
            "1. DIRE NEED / STRONG BUYER INTENT: Keep ONLY leads where the person or business is explicitly asking for help, hiring right now, or stuck on an issue you can solve (custom apps, Wix, Canva, AI MVP, Automation). Reject vague chat, tutorials, or old discussions.\n"
            "2. STRICTLY WITHIN 2 DAYS: The snippet often contains a date (e.g. '1 day ago', '12 hours ago', 'Oct 12'). Keep ONLY if the timestamp proves it was posted within the last 48 hours. If it says '3 days ago', 'last week', a previous year, or if there is no proof of recent activity, you MUST reject it.\n"
            "3. PERSONALIZED MESSAGE: For every lead you keep, write a short, highly persuasive and personalized outreach template (about 2 sentences) addressing their exact problem (e.g., 'Hey, saw you're struggling with cart loading in Bubble. I specialize in fixing this quickly...').\n\n"
            "Return ONLY valid JSON as an array. Each object must contain: "
            "url, keep (true/false), score (0-100), category (opportunity/community/person), reason (explain why considering the 2-day limit and buyer intent), and personalized_message.\n\n"
            f"CANDIDATES:\n{json.dumps(candidates, ensure_ascii=False, indent=2)}"
        )
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.1, "max_output_tokens": 8000},
        )
        refined = _extract_json(response.text)
        if isinstance(refined, list):
            refined_by_url = {item.get("url"): item for item in refined if isinstance(item, dict) and item.get("url")}
            merged = []
            for candidate in candidates:
                refined_item = refined_by_url.get(candidate["url"])
                if refined_item:
                    candidate = {
                        **candidate,
                        "score": int(refined_item.get("score", candidate["score"])),
                        "keep": bool(refined_item.get("keep", candidate["keep"])),
                        "category": refined_item.get("category", candidate.get("category", "opportunity")),
                        "reason": refined_item.get("reason", candidate.get("reason", "")),
                        "personalized_message": refined_item.get("personalized_message", ""),
                    }
                merged.append(candidate)
            return merged
    except Exception:
        return candidates

    return candidates


def _collect_candidates() -> list[dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    ddgs = DDGS()

    for query in SEARCH_QUERIES:
        try:
            results = ddgs.text(query, max_results=10, timelimit='w')
            for result in results:
                url = result.get("href") or result.get("url")
                if not url:
                    continue
                url = _normalize_url(url)
                title = (result.get("title") or "").strip()
                snippet = (result.get("body") or result.get("snippet") or "").strip()
                source = _guess_source(url)
                score, keep, reason = _heuristic_score(title, snippet, url)
                candidate = {
                    "url": url,
                    "title": title,
                    "snippet": snippet,
                    "source": source,
                    "query": query,
                    "score": score,
                    "keep": keep,
                    "category": "opportunity",
                    "reason": reason,
                }
                existing = candidates.get(url)
                if not existing or candidate["score"] > existing["score"]:
                    candidates[url] = candidate
        except Exception as exc:
            print(f"[!] Search failed for query: {query}\n    {exc}")
        time.sleep(1)

    refined = _gemini_refine(list(candidates.values()))
    filtered = [item for item in refined if item.get("keep")]
    filtered.sort(key=lambda item: item.get("score", 0), reverse=True)
    return filtered


def _write_results(results: list[dict[str, Any]]) -> Path:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as handle:
        handle.write(f"DevPresence lead research run: {datetime.now().isoformat(timespec='seconds')}\n")
        handle.write(f"Total leads kept: {len(results)}\n\n")
        if not results:
            handle.write("No high-confidence leads found in this run.\n")
            return OUTPUT_FILE

        for index, result in enumerate(results, start=1):
            handle.write(f"{index}. [{result['source']}] {result.get('title') or 'Untitled'}\n")
            handle.write(f"   URL: {result['url']}\n")
            if result.get("snippet"):
                handle.write(f"   Snippet: {result['snippet']}\n")
            handle.write(f"   Score: {result.get('score', 0)} | Catego")
            if result.get("personalized_message"):
                handle.write(f"   Message template: {result['personalized_message']}\n")
            handle.write(f"   Score: {result.get('score', 0)} | Category: {result.get('category', 'opportunity')}\n")
            handle.write(f"   Match note: {result.get('reason', '')}\n\n")
    return OUTPUT_FILE


def run_lead_research() -> list[dict[str, Any]]:
    print(f"[*] Lead research started at {datetime.now().isoformat(timespec='seconds')}")
    print("[*] Searching Reddit, LinkedIn, Discord, Slack, and web-indexed communities...")
    results = _collect_candidates()
    output = _write_results(results)
    print(f"[*] Wrote {len(results)} high-confidence leads to {output}")
    return results
