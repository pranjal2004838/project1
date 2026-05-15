import requests
import time
import re
from datetime import datetime

HN_ALGOLIA_URL = "https://hn.algolia.com/api/v1/search"

HIRE_KEYWORDS = [
    'react', 'flutter', 'firebase', 'node', 'nodejs', 'wix', 'wordpress',
    'api', 'saas', 'mvp', 'mobile app', 'web app', 'booking', 'dashboard',
    'automation', 'zapier', 'stripe', 'supabase', 'typescript'
]

def scrape_reddit_leads(max_age_hours=168):
    """
    Scrapes HackerNews (Algolia API) and r/forhire for freelance leads.
    HackerNews is reliable and not rate-limited for cloud servers.
    """
    leads = []
    
    # ---- Source 1: Hacker News "who wants to hire a freelancer" posts ----
    try:
        print("[*] Scraping HackerNews for freelance leads...")
        
        # Search for recent posts mentioning our skills
        for keyword in ['react developer', 'flutter developer', 'node developer', 'wix developer']:
            params = {
                "query": keyword,
                "tags": "story",
                "numericFilters": f"created_at_i>{int(time.time()) - 30*24*3600}",
                "hitsPerPage": 20
            }
            resp = requests.get(HN_ALGOLIA_URL, params=params, timeout=10)
            if resp.status_code == 200:
                for hit in resp.json().get("hits", []):
                    title = hit.get("title", "")
                    if any(kw in title.lower() for kw in ["hiring", "hire", "looking for", "need"]):
                        leads.append({
                            "platform": "hackernews",
                            "channel": "HackerNews",
                            "title": title,
                            "body": hit.get("story_text", "")[:500] or title,
                            "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID','')}",
                            "author": hit.get("author", ""),
                            "posted_at": datetime.fromtimestamp(hit.get("created_at_i", time.time())).isoformat()
                        })
            time.sleep(1)
    except Exception as e:
        print(f"[!] HN error: {e}")

    # ---- Source 2: HN "Ask HN: Who wants to be hired" monthly thread ----
    try:
        params = {
            "query": "Ask HN: Freelancer? Seeking work?",
            "tags": "story",
            "hitsPerPage": 5
        }
        resp = requests.get(HN_ALGOLIA_URL, params=params, timeout=10)
        if resp.status_code == 200:
            for hit in resp.json().get("hits", []):
                if "freelancer" in hit.get("title", "").lower() or "seeking work" in hit.get("title", "").lower():
                    continue  # skip these — these are people seeking work, not hiring
        
        # Search HN for people looking to hire
        params2 = {
            "query": "who is hiring",
            "tags": "story",
            "hitsPerPage": 5
        }
        resp2 = requests.get(HN_ALGOLIA_URL, params=params2, timeout=10)
        if resp2.status_code == 200:
            for hit in resp2.json().get("hits", []):
                if "who is hiring" in hit.get("title", "").lower():
                    # Get comments of this thread
                    item_id = hit.get("objectID", "")
                    comments_resp = requests.get(
                        f"https://hn.algolia.com/api/v1/items/{item_id}", timeout=10
                    )
                    if comments_resp.status_code == 200:
                        children = comments_resp.json().get("children", [])[:30]
                        for comment in children:
                            text = comment.get("text", "") or ""
                            if any(kw in text.lower() for kw in HIRE_KEYWORDS):
                                leads.append({
                                    "platform": "hackernews",
                                    "channel": "HN Who's Hiring",
                                    "title": text[:100].strip(),
                                    "body": re.sub('<[^<]+?>', '', text)[:500],
                                    "url": f"https://news.ycombinator.com/item?id={comment.get('id', '')}",
                                    "author": comment.get("author", ""),
                                    "posted_at": datetime.now().isoformat()
                                })
                    break  # Only process the most recent hiring thread
    except Exception as e:
        print(f"[!] HN thread error: {e}")

    # ---- Source 3: Reddit (best-effort, may be blocked on cloud) ----
    try:
        print("[*] Trying Reddit for freelance leads...")
        headers = {"User-Agent": "outreach-research-bot/0.1"}
        SUBREDDITS = ["forhire", "entrepreneur", "startups", "webdev"]
        for sub in SUBREDDITS:
            url = f"https://www.reddit.com/r/{sub}/new.json?limit=30"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                for post in resp.json().get("data", {}).get("children", []):
                    pd = post.get("data", {})
                    title = pd.get("title", "")
                    body = pd.get("selftext", "")
                    if any(kw in (title + body).lower() for kw in ['hire', 'looking for', 'need developer', 'need help']):
                        leads.append({
                            "platform": "reddit",
                            "channel": f"r/{sub}",
                            "title": title,
                            "body": body[:500],
                            "url": f"https://www.reddit.com{pd.get('permalink', '')}",
                            "author": pd.get("author", ""),
                            "posted_at": datetime.fromtimestamp(pd.get("created_utc", time.time())).isoformat()
                        })
            time.sleep(2)
    except Exception as e:
        print(f"[!] Reddit error (may be blocked): {e}")

    print(f"[*] Total freelance leads scraped: {len(leads)}")
    return leads
