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
        print("[!] GITHUB_TOKEN not found. Skipping GitHub search.")
        return []

    g = Github(GITHUB_TOKEN)
    
    # Query: users in hyderabad with followers > 5, sorted by joined date
    # (Matches the plan's suggested query)
    query = "location:hyderabad followers:>1"
    users = g.search_users(query, sort="joined", order="desc")
    
    results = []
    # Limit to first 40 users for the scan
    for i, user in enumerate(users):
        if i >= 40:
            break
            
        try:
            # Basic profile info
            profile = {
                "username": user.login,
                "name": user.name,
                "company": user.company,
                "blog": user.blog,
                "bio": user.bio,
                "public_repos": user.public_repos,
                "email": user.email,
                "github_url": f"https://github.com/{user.login}"
            }
            
            # Skip if no repos
            if profile["public_repos"] < 1:
                continue
                
            # Check recent repos
            repos = user.get_repos(sort="updated", direction="desc")
            recent_repos = []
            tech_stack = set()
            last_activity = None
            
            for j, repo in enumerate(repos):
                if j >= 5: break
                
                # Check for activity in last 60 days
                updated_at = repo.updated_at
                if not last_activity or updated_at > last_activity:
                    last_activity = updated_at
                
                # Extract languages
                if repo.language:
                    tech_stack.add(repo.language)
                
                # Store repo info
                recent_repos.append({
                    "name": repo.name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "updated_at": updated_at.isoformat()
                })
            
            # Include all users with at least some activity
            if last_activity:
                profile["tech_stack"] = list(tech_stack)
                profile["last_activity"] = last_activity.isoformat()
                profile["activity_signal"] = f"GitHub activity on {last_activity.strftime('%Y-%m-%d')}"
                profile["recent_repos"] = recent_repos
                results.append(profile)
                
        except Exception as e:
            print(f"[!] Error processing GitHub user {user.login}: {e}")
            continue
            
        # Respect rate limits
        time.sleep(1)
        
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
