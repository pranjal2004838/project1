import requests
import time
import re
import random
from datetime import datetime, timedelta

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
    'wix', 'wordpress', 'zapier', 'make.com', 'make automation', 'n8n', 
    'automation', 'workflow', 'crm', 'integromat', 'app development',
    'mobile app', 'ios app', 'android app', 'business automation',
]

# Keywords that indicate it's a full-time job (EXCLUDE these)
FULLTIME_EXCLUSIONS = [
    'full-time', 'full time', 'salary', 'equity', 'pto', 'benefits',
    '40 hours', 'monday to friday', 'office', 'remote only', 'w2', 'h1b',
    'years of experience required', 'visa', 'relocation',
]

# Skills Pranjal can offer
PRANJAL_SKILLS = [
    'react', 'flutter', 'firebase', 'node', 'nodejs', 'wordpress', 'wix',
    'api', 'saas', 'mvp', 'mobile app', 'web app', 'booking', 'dashboard',
    'automation', 'zapier', 'make.com', 'stripe', 'supabase', 'typescript',
    'crm', 'landing page', 'ecommerce', 'shopify', 'next.js', 'nextjs',
    'n8n', 'make', 'workflows', 'workflow automation', 'business automation',
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
    Sources: Reddit r/forhire, r/entrepreneur, r/webdev, HackerNews freelancer thread.
    Results rotate every scan using random time offsets and subreddit ordering.
    """
    leads = []
    seen_urls = set()

    # ---- Source 1: Reddit (most relevant freelance subreddits) ----
    try:
        headers = {
            "User-Agent": f"outreach-bot/1.0 (scan-{random.randint(1000,9999)})",
            "Accept": "application/json"
        }
        # Rotate subreddit order so results vary each scan
        SUBREDDITS = [
            ("forhire", ["[hiring]", "hire", "need"]),
            ("slavelabour", ["task", "help", "need", "build"]),
            ("entrepreneur", ["looking for", "need a dev", "hire", "developer"]),
            ("smallbusiness", ["website", "developer", "app", "automate"]),
            ("webdev", ["hire", "freelance", "client", "looking for"]),
            ("startups", ["looking for", "technical co-founder", "need dev", "mvp"]),
        ]
        random.shuffle(SUBREDDITS)

        for sub, sub_keywords in SUBREDDITS[:4]:  # Pick 4 random subs each run
            # Use 'new' and 'hot' alternately
            sort_modes = ["new", "hot"]
            sort = random.choice(sort_modes)
            url = f"https://www.reddit.com/r/{sub}/{sort}.json?limit=50&t=week"
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                posts = resp.json().get("data", {}).get("children", [])
                random.shuffle(posts)  # Shuffle so same sub gives different top results
                for post in posts:
                    pd = post.get("data", {})
                    title = pd.get("title", "")
                    body = pd.get("selftext", "")
                    post_url = f"https://www.reddit.com{pd.get('permalink', '')}"

                    if post_url in seen_urls:
                        continue
                    if _is_full_time_job(title + " " + body):
                        continue
                    if not _has_hire_intent(title, body):
                        continue
                    # Must have at least some skill match
                    if not _has_skill_match(title, body) and sub not in ["forhire", "slavelabour"]:
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

    # ---- Source 2: HN Freelancer / Who wants to hire thread ----
    try:
        # HN "Ask HN: Freelancer? Seeking work? — Hired? Seeking freelancers?" threads
        # These monthly threads have BOTH sides — look for "seeking freelancers" posts
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
                        random.shuffle(children)  # Shuffle so we don't get the same comments
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

    # ---- Source 3: DuckDuckGo search for high-intent posts on the web ----
    try:
        from duckduckgo_search import DDGS
        # Rotate queries so results vary
        FREELANCE_QUERIES = [
            '"looking for" "react developer" "freelance" -site:linkedin.com -site:indeed.com',
            '"hire" "flutter developer" "project" -site:linkedin.com',
            '"need a developer" "mvp" "startup" -site:linkedin.com',
            '"looking for" "wordpress developer" "budget" -site:linkedin.com',
            '"need help" "web app" "react" OR "node" freelance -site:linkedin.com',
            '"need a freelancer" "web development" 2024 OR 2025',
            '"hiring" "contract" "react" "short term" -site:linkedin.com -site:indeed.com',
            '"can someone build" OR "who can build" "app" "react" OR "flutter"',
            '"looking for" "wix developer" OR "wix website" -site:indeed.com',
            '"hire" "zapier" OR "make.com" OR "n8n" "automation" OR "workflow"',
            '"need help with" "crm" OR "workflow" OR "automation" "zapier" OR "make"',
            '"hiring" "app developer" "flutter" OR "react native" OR "ios" OR "android"',
            '"looking for" "mobile app" "mvp" "developer"',
            '"need a freelancer" "n8n" OR "make.com" OR "zapier" OR "automation"',
        ]
        selected_queries = random.sample(FREELANCE_QUERIES, min(3, len(FREELANCE_QUERIES)))
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

    # Shuffle final results for variety
    random.shuffle(leads)
    print(f"[*] Total freelance leads scraped: {len(leads)}")
    return leads
