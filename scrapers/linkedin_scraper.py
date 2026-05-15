from duckduckgo_search import DDGS
import time
import re

def search_linkedin_leads(query_type="freelance"):
    """
    Uses DuckDuckGo X-Ray search to find LinkedIn profiles or posts.
    This bypasses the need for a LinkedIn API key and avoids account bans.
    """
    print(f"[*] Searching LinkedIn via DuckDuckGo for {query_type}...")
    results = []
    
    # Define queries based on the tab's intent
    if query_type == "freelance":
        queries = [
            'site:linkedin.com/posts "hiring" "react" "freelancer"',
            'site:linkedin.com/posts "looking for a developer" "flutter"',
            'site:linkedin.com/posts "need help with" "wordpress" "zapier"'
        ]
    elif query_type == "hyderabad":
        queries = [
            'site:linkedin.com/in "founder" "Hyderabad" "tech"',
            'site:linkedin.com/in "CTO" "Hyderabad" "startup"',
            'site:linkedin.com/posts "Hyderabad startup" "hiring"'
        ]
    elif query_type == "internship":
        queries = [
            'site:linkedin.com/posts "hiring intern" "react" "startup"',
            'site:linkedin.com/posts "software engineer intern" "early stage"',
            'site:linkedin.com/posts "looking for" "junior developer" "contract"'
        ]
    else:
        queries = ['site:linkedin.com/in "founder" "stealth startup"']

    with DDGS() as ddgs:
        for query in queries:
            try:
                search_results = ddgs.text(query, max_results=8)
                for r in search_results:
                    url = r.get('href', '')
                    if not url or "linkedin.com" not in url:
                        continue
                        
                    title = r.get('title', '')
                    snippet = r.get('body', '')
                    
                    # Clean up the name/title
                    # LinkedIn titles usually look like "Name - Company | LinkedIn" or "Post text..."
                    name_match = re.search(r'^([^|-]+)', title)
                    name = name_match.group(1).strip() if name_match else title

                    results.append({
                        "name": name,
                        "title": title,
                        "description": snippet,
                        "url": url,
                        "source": "linkedin",
                        "platform": "linkedin"
                    })
                time.sleep(1) # Delay to be respectful
            except Exception as e:
                print(f"[!] LinkedIn Search error for '{query}': {e}")
                
    return results
