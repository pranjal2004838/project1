from duckduckgo_search import DDGS
import time
import re
import random


# LinkedIn profile URL patterns we want to extract
LINKEDIN_PROFILE_PATTERN = re.compile(r'linkedin\.com/in/[\w\-]+', re.IGNORECASE)
LINKEDIN_POST_PATTERN = re.compile(r'linkedin\.com/posts/[\w\-]+', re.IGNORECASE)

# =========================================================
# FREELANCE QUERIES — High-intent buyers posting on LinkedIn
# =========================================================
FREELANCE_QUERY_POOL = [
    # React / Flutter / Node dev
    'site:linkedin.com/posts "looking for a freelance" "react" OR "flutter" OR "node"',
    'site:linkedin.com/posts "need a developer" "freelance" OR "contractor"',
    'site:linkedin.com/posts "hiring freelancer" "web" OR "app" OR "mobile"',
    'site:linkedin.com/posts "need a react developer" OR "need a flutter developer"',
    'site:linkedin.com/posts "contract developer" "remote" "react" OR "node"',
    'site:linkedin.com/posts "short term" "developer" "project" "budget"',
    # Wix
    'site:linkedin.com/posts "wix developer" "help" OR "hire" OR "freelance"',
    'site:linkedin.com/posts "need help" "wix" OR "wix studio" "website"',
    'site:linkedin.com/posts "wix" "looking for" "developer" OR "expert"',
    # WordPress
    'site:linkedin.com/posts "wordpress developer" "freelance" OR "hire" OR "need"',
    'site:linkedin.com/posts "need help" "wordpress" "website" OR "plugin"',
    # Zapier / Make / n8n automation
    'site:linkedin.com/posts "zapier" "automation" "need help" OR "looking for"',
    'site:linkedin.com/posts "make.com" OR "integromat" "automation" "help" OR "hire"',
    'site:linkedin.com/posts "n8n" OR "n8n.io" "workflow" "developer" OR "help"',
    'site:linkedin.com/posts "business automation" "zapier" OR "make" "looking for"',
    'site:linkedin.com/posts "workflow automation" "hire" OR "freelance" OR "need"',
    'site:linkedin.com/posts "automate" "crm" OR "airtable" OR "notion" "developer"',
    # App dev
    'site:linkedin.com/posts "mobile app" "flutter" OR "react native" "freelance"',
    'site:linkedin.com/posts "build me an app" OR "need an app built" "developer"',
]

# =========================================================
# FOUNDER QUERIES — Real founders/CTOs with contact info
# =========================================================
FOUNDER_QUERY_POOL = [
    'site:linkedin.com/in "Founder" "CTO" "seed stage" "react" OR "flutter" OR "saas"',
    'site:linkedin.com/in "Co-Founder" "early stage startup" "tech"',
    'site:linkedin.com/in "Founder" "stealth startup" "software"',
    'site:linkedin.com/in "CEO" "Founder" "pre-seed" "mobile app" OR "web app"',
    'site:linkedin.com/in "Founder" "bootstrapped" "saas" OR "app"',
    'site:linkedin.com/in "indie hacker" "Founder" "product"',
    'site:linkedin.com/in "solo founder" "developer" "saas"',
    'site:linkedin.com/in "technical founder" "seed" "react" OR "node"',
]

# =========================================================
# INTERNSHIP QUERIES — Startups looking for interns/juniors
# =========================================================
INTERNSHIP_QUERY_POOL = [
    'site:linkedin.com/posts "hiring intern" "developer" "remote" "startup"',
    'site:linkedin.com/posts "software engineer intern" "early stage" OR "seed"',
    'site:linkedin.com/posts "looking for" "junior developer" "contract" OR "internship"',
    'site:linkedin.com/posts "react intern" OR "flutter intern" OR "node intern"',
    'site:linkedin.com/posts "internship" "react" OR "full stack" "startup" "paid"',
    'site:linkedin.com/posts "unpaid" OR "stipend" "developer intern" "startup"',
    'site:linkedin.com/posts "automation intern" OR "no-code intern" "startup"',
    'site:linkedin.com/posts "zapier" OR "make.com" "intern" OR "freelance" "startup"',
    'site:linkedin.com/posts "wix developer" OR "wordpress developer" "intern" OR "part-time"',
]

# =========================================================
# HYDERABAD QUERIES — Local Hyderabad + Bangalore startups
# =========================================================
HYDERABAD_QUERY_POOL = [
    'site:linkedin.com/in "Founder" "Hyderabad" "startup" "tech"',
    'site:linkedin.com/in "CTO" "Hyderabad" "SaaS" OR "app"',
    'site:linkedin.com/in "CEO" "Hyderabad" "early stage"',
    'site:linkedin.com/in "Founder" "Bangalore" "startup" "tech"',
    'site:linkedin.com/in "CTO" "Bengaluru" OR "Bangalore" "SaaS"',
    'site:linkedin.com/in "Co-Founder" "Bangalore" "pre-seed" OR "seed"',
    'site:linkedin.com/posts "Hyderabad startup" "hiring developer"',
    'site:linkedin.com/posts "Bangalore startup" "hiring developer" "react" OR "flutter"',
    'site:linkedin.com/in "Founder" "T-Hub" OR "THUB" "Hyderabad"',
    'site:linkedin.com/in "Founder" "NSRCEL" OR "IIM Bangalore" startup',
]


def _extract_linkedin_url(raw_url: str, title: str) -> str:
    """Extract clean LinkedIn profile URL from raw search URL."""
    # Try to pull out the clean linkedin.com/in/ or linkedin.com/posts/ URL
    match = LINKEDIN_PROFILE_PATTERN.search(raw_url)
    if match:
        return "https://www." + match.group(0)
    match = LINKEDIN_POST_PATTERN.search(raw_url)
    if match:
        return "https://www." + match.group(0)
    # If neither, return the raw URL (still a LinkedIn URL)
    if "linkedin.com" in raw_url:
        return raw_url
    return ""


def _extract_name_from_linkedin_title(title: str) -> str:
    """
    LinkedIn titles look like:
    'John Smith - Founder at Acme Corp | LinkedIn'
    'Jane Doe | CEO at TechStart | LinkedIn'
    """
    # Remove '| LinkedIn' suffix
    title = re.sub(r'\|\s*LinkedIn\s*$', '', title, flags=re.IGNORECASE).strip()
    title = re.sub(r'-\s*LinkedIn\s*$', '', title, flags=re.IGNORECASE).strip()

    # Split by ' - ' or ' | '
    parts = re.split(r'\s+[-|]\s+', title)
    if parts:
        return parts[0].strip()
    return title.strip()


def _extract_company_from_linkedin_title(title: str) -> str:
    """Extract company/role from LinkedIn title."""
    title = re.sub(r'\|\s*LinkedIn\s*$', '', title, flags=re.IGNORECASE).strip()
    parts = re.split(r'\s+[-|]\s+', title)
    if len(parts) >= 2:
        return " | ".join(parts[1:]).strip()
    return ""


def search_linkedin_leads(query_type="freelance"):
    """
    Uses DuckDuckGo X-Ray search to find LinkedIn profiles or posts.
    Randomizes queries so results vary each scan.
    Extracts proper LinkedIn URLs.
    """
    print(f"[*] Searching LinkedIn via DuckDuckGo for {query_type}...")
    results = []
    seen_urls = set()

    # Select the right query pool and pick random queries
    if query_type == "freelance":
        query_pool = FREELANCE_QUERY_POOL
        max_results_per_query = 8
    elif query_type == "hyderabad":
        query_pool = HYDERABAD_QUERY_POOL
        max_results_per_query = 8
    elif query_type == "internship":
        query_pool = INTERNSHIP_QUERY_POOL
        max_results_per_query = 8
    elif query_type == "founder":
        query_pool = FOUNDER_QUERY_POOL
        max_results_per_query = 8
    else:
        query_pool = FOUNDER_QUERY_POOL
        max_results_per_query = 5

    # Pick 3 random queries from the pool (changes each scan)
    selected_queries = random.sample(query_pool, min(3, len(query_pool)))

    with DDGS() as ddgs:
        for query in selected_queries:
            try:
                search_results = ddgs.text(query, max_results=max_results_per_query)
                for r in search_results:
                    raw_url = r.get('href', '')
                    if not raw_url or "linkedin.com" not in raw_url:
                        continue

                    clean_url = _extract_linkedin_url(raw_url, r.get('title', ''))
                    if clean_url in seen_urls or not clean_url:
                        continue
                    seen_urls.add(clean_url)

                    title = r.get('title', '')
                    snippet = r.get('body', '')

                    name = _extract_name_from_linkedin_title(title)
                    company_role = _extract_company_from_linkedin_title(title)

                    results.append({
                        "name": name,
                        "title": company_role or title,
                        "description": snippet,
                        "url": clean_url,  # Always a proper LinkedIn URL now
                        "linkedin_url": clean_url,
                        "source": "linkedin",
                        "platform": "linkedin"
                    })

                time.sleep(random.uniform(1.0, 2.5))  # Randomized delay
            except Exception as e:
                print(f"[!] LinkedIn Search error for '{query}': {e}")

    print(f"[*] LinkedIn search found {len(results)} results for {query_type}")
    return results
