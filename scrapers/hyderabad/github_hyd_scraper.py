import os
import time
import requests
from github import Github
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def search_hyderabad_github_users():
    """
    Search for GitHub users in Hyderabad with recent activity.
    Returns a list of potential startup founders/early employees.
    """
    if not GITHUB_TOKEN:
        return []

    g = Github(GITHUB_TOKEN)
    
    queries = [
        'location:Hyderabad "founder"',
        'location:hyderabad "CTO"',
        'location:Hyderabad "startup"',
        'location:Hyderabad "CEO"'
    ]
    
    seen_logins = set()
    results = []
    
    for q in queries:
        try:
            users = g.search_users(q)
            for i, user in enumerate(users):
                if i >= 10: break 
                if user.login in seen_logins: continue
                seen_logins.add(user.login)
                
                try:
                    profile = {
                        "username": user.login,
                        "name": user.name,
                        "company": user.company,
                        "blog": user.blog,
                        "bio": user.bio,
                        "public_repos": user.public_repos,
                        "github_url": f"https://github.com/{user.login}"
                    }
                    
                    if profile["public_repos"] < 1:
                        continue
                        
                    repos = user.get_repos(sort="updated", direction="desc")
                    tech_stack = set()
                    last_activity = None
                    recent_repos = []
                    
                    for j, repo in enumerate(repos):
                        if j >= 3: break
                        if not last_activity or repo.updated_at > last_activity:
                            last_activity = repo.updated_at
                        if repo.language:
                            tech_stack.add(repo.language)
                        recent_repos.append({"name": repo.name})

                    if last_activity:
                        profile["tech_stack"] = list(tech_stack)
                        profile["last_activity"] = last_activity.isoformat()
                        profile["activity_signal"] = f"GitHub activity on {last_activity.strftime('%Y-%m-%d')}"
                        profile["recent_repos"] = recent_repos
                        results.append(profile)
                except:
                    continue
        except:
            continue
            
    return results

def format_github_user_as_startup(profile):
    """Convert GitHub profile data into the database format safely."""
    recent_repos = profile.get("recent_repos", [])
    repo_names = ", ".join([r['name'] for r in recent_repos[:2]]) if recent_repos else ""
    blog = profile.get("blog") or ""
    return {
        "company_name": profile.get("company") or profile.get("name") or profile.get("username", "Unknown"),
        "founder_name": profile.get("name") or profile.get("username", ""),
        "source": "github",
        "company_url": blog if blog.startswith("http") else profile.get("github_url", ""),
        "github_url": profile.get("github_url", ""),
        "email": profile.get("email") or "",
        "tech_stack": profile.get("tech_stack", []),
        "description": profile.get("bio") or (f"GitHub developer with {profile.get('public_repos', 0)} repos. Recent: {repo_names}" if repo_names else "Active GitHub developer"),
        "last_activity": profile.get("last_activity", ""),
        "activity_signal": profile.get("activity_signal", ""),
        "company_size": "unknown",
    }
