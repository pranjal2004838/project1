import requests
import time
from datetime import datetime

SUBREDDITS = [
    "entrepreneur", "smallbusiness", "startups", "forhire", 
    "webdev", "flutterdev", "nocode", "SaaS", "indiehackers"
]

def scrape_reddit_leads(max_age_hours=48):
    """
    Scrapes relevant subreddits for potential freelance leads using Reddit's public JSON API.
    """
    print("[*] Scraping Reddit for freelance leads...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    
    leads = []
    current_time = time.time()
    
    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/new.json?limit=25"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 429:
                print(f"[!] Reddit Rate Limited. Skipping r/{sub}")
                time.sleep(5)
                continue
            response.raise_for_status()
            
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            for post in posts:
                post_data = post.get('data', {})
                created_utc = post_data.get('created_utc', 0)
                
                # Filter by age
                age_hours = (current_time - created_utc) / 3600
                if age_hours > max_age_hours:
                    continue
                    
                # Skip stickied posts and self-promo (basic filter)
                if post_data.get('stickied') or post_data.get('author') == 'AutoModerator':
                    continue
                
                title = post_data.get('title', '')
                body = post_data.get('selftext', '')
                
                # Very basic keyword pre-filter to save Gemini tokens
                combined = (title + " " + body).lower()
                keywords = ['hire', 'hiring', 'looking for', 'need', 'developer', 'freelance', 'build', 'app', 'website', 'wix', 'react', 'flutter']
                
                if any(kw in combined for kw in keywords):
                    leads.append({
                        "platform": "reddit",
                        "channel": f"r/{sub}",
                        "title": title,
                        "body": body[:1000], # Truncate long bodies
                        "url": f"https://www.reddit.com{post_data.get('permalink', '')}",
                        "author": post_data.get('author', ''),
                        "posted_at": datetime.fromtimestamp(created_utc).isoformat()
                    })
                    
        except Exception as e:
            print(f"[!] Error scraping r/{sub}: {e}")
            
        time.sleep(2) # Respectful delay between subreddits
        
    return leads
