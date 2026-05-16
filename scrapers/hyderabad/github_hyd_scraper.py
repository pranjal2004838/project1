import os
import time
import random
from github import Github
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Rotating query pools — randomized each scan so results change
HYD_QUERIES = [
    'location:Hyderabad "founder"',
    'location:Hyderabad "CTO"',
    'location:Hyderabad "startup"',
    'location:Hyderabad "CEO"',
    'location:Hyderabad "co-founder"',
    'location:Hyderabad "indie hacker"',
    'location:Hyderabad "saas"',
    'location:Hyderabad "product"',
]

BLORE_QUERIES = [
    'location:Bangalore "founder"',
    'location:Bangalore "CTO"',
    'location:Bangalore "startup"',
    'location:Bengaluru "founder"',
    'location:Bengaluru "CTO"',
    'location:Bangalore "CEO"',
    'location:Bangalore "co-founder"',
    'location:Bangalore "saas"',
]


def search_hyderabad_github_users():
    """
    Search GitHub for founders/CTOs in BOTH Hyderabad and Bangalore.
    Randomizes which queries run so results differ each scan.
    """
    if not GITHUB_TOKEN:
        print("[!] No GITHUB_TOKEN, skipping GitHub scan")
        return []

    g = Github(GITHUB_TOKEN)

    # Mix queries from both cities
    all_queries = HYD_QUERIES + BLORE_QUERIES
    selected_queries = random.sample(all_queries, min(5, len(all_queries)))

    seen_logins = set()
    results = []

    for q in selected_queries:
        try:
            users = g.search_users(q)
            count = 0
            # Skip a random number of initial results so we get freshness
            skip_count = random.randint(0, 8)

            for i, user in enumerate(users):
                if i < skip_count:
                    continue
                if count >= 8:
                    break
                if user.login in seen_logins:
                    continue
                seen_logins.add(user.login)
                count += 1

                try:
                    # Skip if too few or way too many repos (just a hobbyist or huge corp)
                    if user.public_repos < 2 or user.public_repos > 300:
                        continue

                    profile = {
                        "username": user.login,
                        "name": user.name,
                        "company": user.company,
                        "blog": user.blog,
                        "bio": user.bio,
                        "email": user.email,
                        "public_repos": user.public_repos,
                        "github_url": f"https://github.com/{user.login}",
                        "linkedin_url": _extract_linkedin_from_bio(user.bio or ""),
                        "city": _detect_city(q),
                    }

                    repos = user.get_repos(sort="updated", direction="desc")
                    tech_stack = set()
                    last_activity = None
                    recent_repos = []

                    for j, repo in enumerate(repos):
                        if j >= 5:
                            break
                        if not last_activity or repo.updated_at > last_activity:
                            last_activity = repo.updated_at
                        if repo.language:
                            tech_stack.add(repo.language)
                        recent_repos.append({"name": repo.name, "desc": repo.description or ""})

                    if last_activity:
                        profile["tech_stack"] = list(tech_stack)
                        profile["last_activity"] = last_activity.isoformat()
                        profile["activity_signal"] = f"GitHub active: {last_activity.strftime('%Y-%m-%d')}"
                        profile["recent_repos"] = recent_repos
                        results.append(profile)

                except Exception:
                    continue

        except Exception as e:
            print(f"[!] GitHub query error '{q}': {e}")

    random.shuffle(results)
    print(f"[*] Hyderabad+Bangalore GitHub found {len(results)} users")
    return results


def _detect_city(query: str) -> str:
    q_lower = query.lower()
    if "bangalore" in q_lower or "bengaluru" in q_lower:
        return "Bangalore"
    return "Hyderabad"


def _extract_linkedin_from_bio(bio: str) -> str:
    """Extract LinkedIn URL from bio if present."""
    import re
    match = re.search(r'linkedin\.com/in/[\w\-]+', bio, re.IGNORECASE)
    if match:
        return "https://www." + match.group(0)
    return ""


def format_github_user_as_startup(profile):
    """Convert GitHub profile data into the startup database format."""
    recent_repos = profile.get("recent_repos", [])
    repo_names = ", ".join([r['name'] for r in recent_repos[:2]]) if recent_repos else ""
    blog = profile.get("blog") or ""
    city = profile.get("city", "Hyderabad")

    # Prefer LinkedIn URL > Blog > GitHub
    contact_url = profile.get("linkedin_url") or (blog if blog.startswith("http") else "") or profile.get("github_url", "")

    company_name = profile.get("company") or profile.get("name") or profile.get("username", "Unknown")
    if city == "Bangalore":
        company_name = f"{company_name} (Bangalore)"

    return {
        "company_name": company_name,
        "founder_name": profile.get("name") or profile.get("username", ""),
        "source": "github",
        "company_url": contact_url,
        "github_url": profile.get("github_url", ""),
        "linkedin_url": profile.get("linkedin_url", ""),
        "email": profile.get("email") or "",
        "tech_stack": profile.get("tech_stack", []),
        "description": profile.get("bio") or (
            f"GitHub developer ({city}) with {profile.get('public_repos', 0)} repos. Recent: {repo_names}" if repo_names
            else f"Active GitHub developer in {city}"
        ),
        "last_activity": profile.get("last_activity", ""),
        "activity_signal": profile.get("activity_signal", ""),
        "company_size": "unknown",
        "city": city,
    }
