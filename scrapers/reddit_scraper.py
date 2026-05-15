import requests
import time
import os
from datetime import datetime

SUBREDDITS = [
    "entrepreneur", "smallbusiness", "startups", "forhire", 
    "webdev", "flutterdev", "nocode", "SaaS"
]

KEYWORDS = [
    'hire', 'hiring', 'looking for', 'need', 'developer', 
    'freelance', 'build', 'app', 'website', 'react', 'flutter',
    'wordpress', 'wix', 'help with', 'anyone know'
]

def scrape_reddit_leads(max_age_hours=72):
    """
    Scrapes relevant subreddits for potential freelance leads using Reddit's public JSON API.
    """
    print("[*] Scraping Reddit for freelance leads...")
    headers = {
        "User-Agent": "outreach-bot/0.1 (research tool)"
    }
    
    leads = []
    current_time = time.time()
    
    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/new.json?limit=50"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 429:
                print(f"[!] Reddit Rate Limited. Skipping r/{sub}")
                time.sleep(10)
                continue
            if response.status_code != 200:
                print(f"[!] Reddit returned {response.status_code} for r/{sub}. Skipping.")
                continue

            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            for post in posts:
                post_data = post.get('data', {})
                
                # Skip stickied posts and automoderator
                if post_data.get('stickied') or post_data.get('author') in ['AutoModerator', '[deleted]']:
                    continue
                
                title = post_data.get('title', '')
                body = post_data.get('selftext', '')
                
                # Basic keyword filter
                combined = (title + " " + body).lower()
                if any(kw in combined for kw in KEYWORDS):
                    created_utc = post_data.get('created_utc', 0)
                    leads.append({
                        "platform": "reddit",
                        "channel": f"r/{sub}",
                        "title": title,
                        "body": body[:1000],
                        "url": f"https://www.reddit.com{post_data.get('permalink', '')}",
                        "author": post_data.get('author', ''),
                        "posted_at": datetime.fromtimestamp(created_utc).isoformat()
                    })
                    
        except Exception as e:
            print(f"[!] Error scraping r/{sub}: {e}")
            
        time.sleep(2)  # Respectful delay
        
    print(f"[*] Reddit scraped. Found {len(leads)} potential leads.")
    return leads
