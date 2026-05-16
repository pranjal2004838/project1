from duckduckgo_search import DDGS
import time
import re
import random

# Exclude job portals and recruitment sites — we want startup websites directly
EXCLUDED_SITES = [
    'linkedin.com', 'naukri.com', 'internshala.com', 'indeed.com',
    'glassdoor.com', 'foundit.in', 'shine.com', 'monster.com',
    'timesjobs.com', 'apna.co'
]

# Rotating query pools for Hyderabad + Bangalore
HYD_STARTUP_QUERIES = [
    "funded tech startup Hyderabad 2024 2025 react OR flutter",
    "early stage startup Hyderabad hiring developer site:thehub.io OR site:f6s.com",
    "Hyderabad startup product launch 2025 saas OR app",
    "\"Hyderabad\" \"seed funded\" startup tech 2025",
    "\"bootstrapped\" startup Hyderabad developer react OR node",
    "T-Hub startup Hyderabad tech product 2024 2025",
    "\"pre-seed\" startup Hyderabad mobile app OR web app",
    "Hyderabad startup hiring react developer 2025",
]

BLORE_STARTUP_QUERIES = [
    "funded tech startup Bangalore 2024 2025 react OR flutter",
    "early stage startup Bengaluru saas product 2025",
    "\"Bangalore\" \"seed funded\" startup tech 2025",
    "\"bootstrapped\" startup Bangalore react OR node developer",
    "\"pre-seed\" startup Bengaluru mobile app 2025",
    "NSRCEL OR IIM Bangalore startup tech product 2025",
    "Koramangala startup hiring developer react OR flutter 2025",
    "Bangalore startup hiring react developer 2025",
]

# Directories and lists of startups
DIRECTORY_QUERIES = [
    "site:thehub.io startup Hyderabad OR Bangalore tech",
    "site:f6s.com startup Hyderabad tech react",
    "site:crunchbase.com startup Hyderabad seed 2025",
    "site:tracxn.com startup Hyderabad tech 2024 OR 2025",
    "\"early stage\" OR \"seed stage\" startup Hyderabad technology 2025",
    "startup india Hyderabad OR Bangalore saas product technical team",
]


def search_hyderabad_startups():
    """
    Uses DuckDuckGo to find Hyderabad AND Bangalore startups.
    Randomizes queries so results change every scan.
    Returns a list of potential companies with their context.
    """
    print("[*] Searching for Hyderabad + Bangalore startups via DuckDuckGo...")
    results = []
    seen_urls = set()

    # Mix of Hyderabad, Bangalore, and directory queries
    all_queries = HYD_STARTUP_QUERIES + BLORE_STARTUP_QUERIES + DIRECTORY_QUERIES
    selected_queries = random.sample(all_queries, min(6, len(all_queries)))

    with DDGS() as ddgs:
        for query in selected_queries:
            try:
                search_results = ddgs.text(query, max_results=10)
                for r in search_results:
                    url = r.get('href', '')
                    if not url:
                        continue
                    # Skip job portals
                    if any(site in url for site in EXCLUDED_SITES):
                        continue
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    title = r.get('title', '')
                    snippet = r.get('body', '')

                    # Determine city
                    city = "Bangalore" if any(kw in (title + snippet + query).lower() for kw in ["bangalore", "bengaluru", "blore", "koramangala"]) else "Hyderabad"

                    # Extract company name from title
                    company_match = re.search(r'^([^|-]+)', title)
                    company_name = company_match.group(1).strip() if company_match else title[:60]

                    results.append({
                        "company_name": company_name,
                        "description": snippet,
                        "company_url": url,
                        "source": "search",
                        "city": city,
                        "activity_signal": f"Found via: {query[:60]}...",
                        "tech_stack": [],
                    })

                time.sleep(random.uniform(1.0, 2.0))
            except Exception as e:
                print(f"[!] Search error for '{query}': {e}")

    random.shuffle(results)
    print(f"[*] Hyderabad+Bangalore search found {len(results)} startups")
    return results
