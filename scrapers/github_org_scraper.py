import os
import time
from github import Github
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def search_small_orgs_and_founders(query_term="startup", min_members=2, max_members=15):
    """
    Search for GitHub users/orgs with startup or founder keywords.
    Uses a direct user search query which is much more reliable than org member counting.
    """
    if not GITHUB_TOKEN:
        print("[!] GITHUB_TOKEN not found. Returning empty.")
        return []

    g = Github(GITHUB_TOKEN)
    results = []
    
    # Search for users with startup/founder related bios
    queries = [
        f"{query_term} in:bio language:JavaScript",
        f"{query_term} founder in:bio",
        f"cto in:bio language:Python",
    ]
    
    seen_logins = set()
    
    for query in queries:
        try:
            users = g.search_users(query)
            for i, user in enumerate(users):
                if i >= 10:
                    break
                if user.login in seen_logins:
                    continue
                seen_logins.add(user.login)
                
                try:
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
                            "company": user.name or user.login,
                            "description": user.bio or (latest_repo.description or f"Active developer with {user.public_repos} repos"),
                            "url": user.blog if user.blog and user.blog.startswith("http") else f"https://github.com/{user.login}",
                            "source": "github_user",
                            "stack": language or "Unknown",
                            "activity_signal": f"Last active: {latest_repo.updated_at.strftime('%Y-%m-%d')} on {latest_repo.name}",
                            "founder_name": user.name or user.login,
                            "urgency_signal": f"Active GitHub user with {user.public_repos} public repos"
                        })
                except Exception as e:
                    continue
                    
                time.sleep(0.5)
                
        except Exception as e:
            print(f"[!] GitHub search error for '{query}': {e}")
            
    print(f"[*] GitHub org/founder scraper found {len(results)} results.")
    return results
