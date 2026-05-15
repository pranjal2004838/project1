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
    query = "location:hyderabad followers:>5"
    users = g.search_users(query, sort="joined", order="desc")
    
    results = []
    # Limit to first 30 users for the scan to stay within rate limits and time
    for i, user in enumerate(users):
        if i >= 30:
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
            
            # Skip if no repos or no company/blog (less likely to be a founder/startup)
            if profile["public_repos"] < 3 or not (profile["company"] or profile["blog"]):
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
            
            # Final check: Must have been active recently (last 60 days)
            # and have some tech stack
            if last_activity and (time.time() - last_activity.timestamp() < 60 * 24 * 3600):
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
    """Convert GitHub profile data into the database format."""
    return {
        "company_name": profile["company"] if profile["company"] else profile["name"] if profile["name"] else profile["username"],
        "founder_name": profile["name"] if profile["name"] else profile["username"],
        "source": "github",
        "company_url": profile["blog"] if profile["blog"] and profile["blog"].startswith("http") else profile["github_url"],
        "github_url": profile["github_url"],
        "email": profile["email"],
        "tech_stack": profile["tech_stack"],
        "description": profile["bio"] if profile["bio"] else f"GitHub user with {profile['public_repos']} repos. Recent work: " + ", ".join([r['name'] for r in profile['recent_repos'][:2]]),
        "last_activity": profile["last_activity"],
        "activity_signal": profile["activity_signal"]
    }
