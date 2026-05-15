from duckduckgo_search import DDGS
import time
import re

def search_hyderabad_startups():
    """
    Uses DuckDuckGo to find recent mentions of startups in Hyderabad.
    Returns a list of potential companies with their context.
    """
    print("[*] Searching for Hyderabad startups via DuckDuckGo...")
    results = []
    
    queries = [
        "early stage tech startups in Hyderabad 2024",
        "T-Hub Hyderabad startup list 2024",
        "newly funded startups Hyderabad",
        "Hyderabad startups hiring developers"
    ]
    
    seen_urls = set()
    
    with DDGS() as ddgs:
        for query in queries:
            try:
                # Get search results
                search_results = ddgs.text(query, max_results=10)
                for r in search_results:
                    url = r.get('href', '')
                    if url in seen_urls or any(x in url for x in ['linkedin.com', 'naukri.com', 'internshala.com']):
                        continue
                    seen_urls.add(url)
                    
                    # Basic extraction of company name from title/snippet
                    title = r.get('title', '')
                    snippet = r.get('body', '')
                    
                    # Try to find a company name (usually the first few words or before a dash)
                    company_match = re.search(r'^([^|-]+)', title)
                    company_name = company_match.group(1).strip() if company_match else title
                    
                    results.append({
                        "company_name": company_name,
                        "description": snippet,
                        "company_url": url,
                        "source": "search",
                        "activity_signal": f"Found via search: {query}",
                        "tech_stack": [] # Will be filled by Gemini analysis
                    })
                time.sleep(1)
            except Exception as e:
                print(f"[!] Search error for '{query}': {e}")
                
    return results
