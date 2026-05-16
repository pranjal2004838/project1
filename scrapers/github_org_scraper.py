import os
import time
import random
from github import Github
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Queries rotated randomly so results change every scan
STARTUP_QUERIES = [
    "founder in:bio language:JavaScript",
    "founder in:bio language:TypeScript",
    "founder in:bio language:Python",
    "CEO startup in:bio language:JavaScript",
    "CTO startup in:bio",
    "building saas in:bio",
    "indie hacker in:bio",
    "bootstrapped in:bio language:JavaScript",
    "solo founder in:bio",
    "product founder in:bio language:TypeScript",
]

INTERNSHIP_QUERIES = [
    "startup in:bio language:JavaScript",
    "startup in:bio language:Python",
    "saas in:bio language:JavaScript",
    "building app in:bio language:TypeScript",
    "early stage startup in:bio",
    "seed stage in:bio language:JavaScript",
    "series a in:bio language:Python",
    "engineer startup in:bio",
]


def search_small_orgs_and_founders(query_term="startup", min_members=1, max_members=20):
    """
    Search for GitHub users/orgs with startup or founder keywords.
    Randomizes queries every call so results vary across scans.
    """
    if not GITHUB_TOKEN:
        print("[!] GITHUB_TOKEN not found. Returning empty.")
        return []

    g = Github(GITHUB_TOKEN)
    results = []

    # Pick queries based on type with randomization
    if query_term == "founder":
        query_pool = STARTUP_QUERIES
    else:
        query_pool = INTERNSHIP_QUERIES

    # Random sample of queries each scan
    selected_queries = random.sample(query_pool, min(3, len(query_pool)))

    # Add a time-based seed so different days give different results
    time_offset = int(time.time()) % 7  # 0-6, changes every ~day
    page_num = time_offset  # Use different page offsets

    seen_logins = set()

    for query in selected_queries:
        try:
            users = g.search_users(query)
            count = 0
            # Skip 'page_num' results to get fresh results each day
            skip = random.randint(0, 5)
            for i, user in enumerate(users):
                if i < skip:
                    continue
                if count >= 8:
                    break
                if user.login in seen_logins:
                    continue
                seen_logins.add(user.login)
                count += 1

                try:
                    # Skip users with too few or too many repos (not a startup)
                    if user.public_repos < 2 or user.public_repos > 200:
                        continue

                    repos = user.get_repos(sort="updated")
                    latest_repo = None
                    language = None
                    for repo in repos:
                        latest_repo = repo
                        language = repo.language
                        break

                    if latest_repo:
                        results.append({
                            "name": user.login,
                            "company": user.name or user.company or user.login,
                            "description": user.bio or (latest_repo.description or f"Active developer with {user.public_repos} repos building: {latest_repo.name}"),
                            "url": user.blog if user.blog and user.blog.startswith("http") else f"https://github.com/{user.login}",
                            "linkedin_url": _extract_linkedin_from_bio(user.bio or ""),
                            "github_url": f"https://github.com/{user.login}",
                            "source": "github_user",
                            "stack": language or "Unknown",
                            "activity_signal": f"Last active: {latest_repo.updated_at.strftime('%Y-%m-%d')} on {latest_repo.name}",
                            "founder_name": user.name or user.login,
                            "urgency_signal": f"Active GitHub user with {user.public_repos} public repos",
                            "contact_type": "github",
                            "contact_url": f"https://github.com/{user.login}",
                        })
                except Exception:
                    continue

                time.sleep(0.5)

        except Exception as e:
            print(f"[!] GitHub search error for '{query}': {e}")

    random.shuffle(results)
    print(f"[*] GitHub org/founder scraper found {len(results)} results.")
    return results


def _extract_linkedin_from_bio(bio: str) -> str:
    """Try to extract a LinkedIn URL from the bio text."""
    import re
    match = re.search(r'linkedin\.com/in/[\w\-]+', bio, re.IGNORECASE)
    if match:
        return "https://" + match.group(0)
    return ""
