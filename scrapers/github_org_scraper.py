import os
import time
from github import Github
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def search_small_orgs_and_founders(query_term="startup", min_members=2, max_members=15):
    """
    Search for small GitHub organizations and their members (founders).
    Useful for both Internship and Cold Email tabs.
    """
    if not GITHUB_TOKEN:
        print("[!] GITHUB_TOKEN not found.")
        return []

    g = Github(GITHUB_TOKEN)
    results = []
    
    # Search for organizations
    # Note: GitHub API doesn't have a direct "member count" filter in search,
    # so we search for orgs and then check member counts.
    org_query = f"{query_term} type:org"
    orgs = g.search_users(org_query)
    
    for i, org in enumerate(orgs):
        if i >= 20: break # Limit for scan speed
        
        try:
            # Check member count (public members)
            members = org.get_public_members()
            member_count = sum(1 for _ in members)
            
            if min_members <= member_count <= max_members:
                # Check recent activity in repos
                repos = org.get_repos(sort="updated")
                latest_repo = None
                for repo in repos:
                    latest_repo = repo
                    break
                
                if latest_repo and (time.time() - latest_repo.updated_at.timestamp() < 30 * 24 * 3600):
                    results.append({
                        "name": org.login,
                        "company": org.name if org.name else org.login,
                        "description": org.bio if org.bio else latest_repo.description,
                        "url": org.blog if org.blog and org.blog.startswith("http") else f"https://github.com/{org.login}",
                        "source": "github_org",
                        "stack": latest_repo.language,
                        "activity_signal": f"Active repo: {latest_repo.name} (Updated: {latest_repo.updated_at.strftime('%Y-%m-%d')})",
                        "founder_name": org.name if org.name else org.login
                    })
        except Exception as e:
            continue
            
        time.sleep(1)
        
    return results
