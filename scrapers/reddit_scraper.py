import requests
import time
import re
import random
from datetime import datetime

HN_ALGOLIA_URL = "https://hn.algolia.com/api/v1/search"

# High-intent keywords — someone actively LOOKING TO HIRE
HIRE_KEYWORDS = [
    'hire', 'hiring', 'looking for', 'need a developer', 'need developer',
    'need help with', 'need someone to', 'build me', 'fix my', 'freelance help',
    'upwork', 'fiverr', 'contractor', 'contract work', 'pay', 'paid',
    'budget', 'rate', 'per hour', 'per project',
    'react developer', 'flutter developer', 'node developer', 'fullstack',
    'web developer', 'app developer', 'wordpress developer', 'wix developer',
    'anyone who can', 'can someone help', 'can anyone build',
    'automate', 'automation', 'workflow', 'integrate', 'zap', 'zapier',
    'make.com', 'n8n', 'airtable', 'notion', 'crm', 'wix',
]

# Keywords that indicate it's a full-time job (EXCLUDE these)
FULLTIME_EXCLUSIONS = [
    'full-time', 'full time', 'salary', 'equity', 'pto', 'benefits',
    '40 hours', 'monday to friday', 'w2', 'h1b',
    'years of experience required', 'visa', 'relocation',
]

# Skills Pranjal can offer — expanded with automation
PRANJAL_SKILLS = [
    # Dev
    'react', 'flutter', 'firebase', 'node', 'nodejs', 'wordpress', 'wix',
    'api', 'saas', 'mvp', 'mobile app', 'web app', 'booking', 'dashboard',
    'automation', 'zapier', 'make.com', 'n8n', 'stripe', 'supabase',
    'typescript', 'crm', 'landing page', 'ecommerce', 'shopify',
    'next.js', 'nextjs', 'airtable', 'notion', 'webhook',
    # Automation-specific
    'workflow', 'integrate', 'automate', 'no-code', 'low-code',
    'make ', 'zapier', 'integromat', 'pipedream', 'activepieces',
    # Wix-specific
    'wix', 'wix studio', 'wix velo', 'squarespace', 'webflow',
    # App dev
    'app development', 'mobile development', 'android', 'ios',
]

def _is_full_time_job(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in FULLTIME_EXCLUSIONS)

def _has_hire_intent(title: str, body: str) -> bool:
    combined = (title + " " + body).lower()
    return any(kw in combined for kw in HIRE_KEYWORDS)

def _has_skill_match(title: str, body: str) -> bool:
    combined = (title + " " + body).lower()
    return any(kw in combined for kw in PRANJAL_SKILLS)


def scrape_reddit_leads(max_age_hours=168):
    """
    Multi-source freelance lead scraper with randomization.
    Covers: React/Flutter/Node dev, Wix, WordPress, automation (Zapier/Make/n8n).
    Results rotate every scan using random subreddit order and sort modes.
    """
    leads = []
    seen_urls = set()

    # ---- Source 1: Reddit ----
    try:
        headers = {
            "User-Agent": f"outreach-bot/1.0 (scan-{random.randint(1000,9999)})",
            "Accept": "application/json"
        }
        SUBREDDITS = [
            ("forhire", True),           # Always high-value, no skill filter needed
            ("slavelabour", True),        # Always high-value
            ("entrepreneur", False),
            ("smallbusiness", False),
            ("webdev", False),
            ("startups", False),
            ("zapier", True),             # Automation clients
            ("nocode", True),             # No-code clients (Wix, Webflow, Airtable)
            ("automation", True),         # Automation leads
            ("wix", True),               # Direct Wix clients
            ("wordpress", False),         # WordPress clients
        ]
        random.shuffle(SUBREDDITS)

        for sub, no_filter_needed in SUBREDDITS[:5]:  # 5 random subs each run
            sort = random.choice(["new", "hot"])
            url = f"https://www.reddit.com/r/{sub}/{sort}.json?limit=50&t=week"
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                posts = resp.json().get("data", {}).get("children", [])
                random.shuffle(posts)
                for post in posts:
                    pd = post.get("data", {})
                    title = pd.get("title", "")
                    body = pd.get("selftext", "")
                    post_url = f"https://www.reddit.com{pd.get('permalink', '')}"

                    if post_url in seen_urls:
                        continue
                    if _is_full_time_job(title + " " + body):
                        continue
                    if not no_filter_needed and not _has_hire_intent(title, body):
                        continue
                    if not no_filter_needed and not _has_skill_match(title, body):
                        continue

                    seen_urls.add(post_url)
                    leads.append({
                        "platform": "reddit",
                        "channel": f"r/{sub}",
                        "title": title,
                        "body": body[:600],
                        "url": post_url,
                        "author": pd.get("author", ""),
                        "posted_at": datetime.fromtimestamp(pd.get("created_utc", time.time())).isoformat()
                    })
            time.sleep(1.5)
    except Exception as e:
        print(f"[!] Reddit error: {e}")

    # ---- Source 2: HN Freelancer thread ----
    try:
        params = {
            "query": "Ask HN: Freelancer? Seeking work? Hired? Seeking freelancers?",
            "tags": "story",
            "hitsPerPage": 3,
        }
        resp = requests.get(HN_ALGOLIA_URL, params=params, timeout=10)
        if resp.status_code == 200:
            for hit in resp.json().get("hits", []):
                title = hit.get("title", "")
                if "seeking freelancers" in title.lower() or "hired" in title.lower():
                    item_id = hit.get("objectID", "")
                    comments_resp = requests.get(
                        f"https://hn.algolia.com/api/v1/items/{item_id}", timeout=10
                    )
                    if comments_resp.status_code == 200:
                        children = comments_resp.json().get("children", [])
                        random.shuffle(children)
                        for comment in children[:40]:
                            text = comment.get("text", "") or ""
                            clean_text = re.sub('<[^<]+?>', '', text)
                            if _has_skill_match("", clean_text) and len(clean_text) > 50:
                                url = f"https://news.ycombinator.com/item?id={comment.get('id', '')}"
                                if url not in seen_urls:
                                    seen_urls.add(url)
                                    leads.append({
                                        "platform": "hackernews",
                                        "channel": "HN Freelancer Thread",
                                        "title": clean_text[:120].strip(),
                                        "body": clean_text[:600],
                                        "url": url,
                                        "author": comment.get("author", ""),
                                        "posted_at": datetime.now().isoformat()
                                    })
        time.sleep(1)
    except Exception as e:
        print(f"[!] HN thread error: {e}")

    # ---- Source 3: DuckDuckGo — dev + automation + Wix queries ----
    try:
        from duckduckgo_search import DDGS

        FREELANCE_QUERIES = [
            # React / Flutter / Node
            '"looking for" "react developer" "freelance" -site:linkedin.com -site:indeed.com',
            '"hire" "flutter developer" "project" -site:linkedin.com',
            '"need a developer" "mvp" "startup" -site:linkedin.com',
            '"hiring" "contract" "react" OR "node" "short term" -site:indeed.com',
            # Wix
            '"need help" "wix" "website" "developer" OR "expert" -site:linkedin.com',
            '"wix developer" "hire" OR "freelance" OR "need" -site:linkedin.com',
            '"wix velo" "developer" "hire" OR "project"',
            '"wix studio" "help" OR "hire" 2024 OR 2025',
            # WordPress
            '"looking for" "wordpress developer" "budget" -site:linkedin.com',
            '"wordpress" "fix" OR "build" "freelancer" -site:linkedin.com',
            # Automation — Zapier / Make / n8n
            '"need help" "zapier" "automation" OR "workflow" -site:linkedin.com',
            '"looking for" "zapier" OR "make.com" OR "n8n" "expert" OR "developer"',
            '"automate" "zapier" OR "make" "business" "help" -site:linkedin.com',
            '"n8n" "workflow" "developer" OR "help" OR "hire"',
            '"make.com" "automation" "need help" OR "hire" -site:linkedin.com',
            '"business automation" "zapier" OR "make" "freelancer" OR "developer"',
            '"workflow automation" "hire" OR "freelance" "developer" 2024 OR 2025',
            '"crm automation" "zapier" OR "make" OR "n8n" "help"',
            # App development
            '"need a developer" "mobile app" "budget" -site:linkedin.com',
            '"build me an app" OR "build my app" "react native" OR "flutter"',
            '"app development" "freelancer" "budget" 2024 OR 2025 -site:indeed.com',
            # General high-intent
            '"can someone build" OR "who can build" "app" "react" OR "flutter" OR "node"',
            '"need a freelancer" "web development" 2024 OR 2025',
        ]
        selected_queries = random.sample(FREELANCE_QUERIES, min(5, len(FREELANCE_QUERIES)))

        with DDGS() as ddgs:
            for query in selected_queries:
                try:
                    results = ddgs.text(query, max_results=8)
                    for r in results:
                        url = r.get('href', '')
                        if not url or url in seen_urls:
                            continue
                        title = r.get('title', '')
                        snippet = r.get('body', '')
                        if _is_full_time_job(title + snippet):
                            continue
                        seen_urls.add(url)
                        leads.append({
                            "platform": "web",
                            "channel": "DuckDuckGo Search",
                            "title": title,
                            "body": snippet[:600],
                            "url": url,
                            "author": "",
                            "posted_at": datetime.now().isoformat()
                        })
                    time.sleep(1.5)
                except Exception as e:
                    print(f"[!] DDG query error: {e}")
    except Exception as e:
        print(f"[!] DDG error: {e}")

    random.shuffle(leads)
    print(f"[*] Total freelance leads scraped: {len(leads)}")
    return leads
