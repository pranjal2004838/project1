import json
from scrapers.hyderabad.github_hyd_scraper import search_hyderabad_github_users, format_github_user_as_startup
from scrapers.hyderabad.thub_scraper import scrape_thub_portfolio
from ai.hyderabad_scorer import score_hyderabad_startup, generate_hyderabad_email
from database.db_client import DatabaseClient
import time

def run_hyderabad_scan(db: DatabaseClient):
    """
    Coordinates the Hyderabad Stealth Hunter scan.
    1. Scrapes GitHub (Hyderabad location)
    2. Scrapes T-Hub Portfolio
    3. Scores results with Gemini
    4. Saves to DB
    """
    print("[*] Starting Hyderabad Stealth Hunter scan...")
    all_results = []
    
    # 1. GitHub
    print("[*] Searching GitHub for Hyderabad founders...")
    github_users = search_hyderabad_github_users()
    for user in github_users:
        all_results.append(format_github_user_as_startup(user))
        
    # 2. T-Hub
    print("[*] Scraping T-Hub portfolio...")
    thub_startups = scrape_thub_portfolio()
    all_results.extend(thub_startups)
    
    # 3. Scoring & Saving
    print(f"[*] Found {len(all_results)} potential startups. Scoring with Gemini...")
    
    items_passed = 0
    for i, startup in enumerate(all_results):
        try:
            # Check if already exists and was passed (avoid re-scoring to save tokens)
            # For simplicity, we re-score for now or check URL
            
            # Prepare data for Gemini
            scoring_data = {
                "company_name": startup.get("company_name", "Unknown"),
                "source": startup.get("source", "unknown"),
                "description": startup.get("description", ""),
                "tech_stack": json.dumps(startup.get("tech_stack", [])),
                "company_size": startup.get("company_size", "unknown"),
                "last_activity": startup.get("last_activity", "unknown"),
                "company_url": startup.get("company_url", ""),
                "github_url": startup.get("github_url", "")
            }
            
            # Call Gemini
            analysis = score_hyderabad_startup(scoring_data)
            
            # Merge analysis back into startup data
            startup.update({
                "score": analysis.get("score", 0),
                "fit_reason": analysis.get("fit_reason", ""),
                "stack_overlap": json.dumps(analysis.get("stack_overlap", [])),
                "urgency_signal": analysis.get("urgency_signal", ""),
                "disqualify_reason": analysis.get("disqualify_reason"),
                "pass": 1 if analysis.get("pass") else 0
            })
            
            if startup["pass"]:
                items_passed += 1
                
            # Automatically generate email using the updated startup dict
            print(f"[*] Generating email for startup: {startup.get('company_name')}...")
            email_data = generate_hyderabad_email(startup)
            startup["generated_subject"] = email_data.get("subject", "")
            startup["generated_message"] = email_data.get("message", "")
                
            # Convert tech_stack to JSON string for DB
            if "tech_stack" in startup and isinstance(startup["tech_stack"], list):
                startup["tech_stack"] = json.dumps(startup["tech_stack"])
            
            # Save to DB
            db.insert_lead("hyderabad_startups", startup)
            
            # Rate limiting sleep (4.1s as per plan)
            if i < len(all_results) - 1:
                time.sleep(4.1)
                
        except Exception as e:
            print(f"[!] Error scoring startup {startup.get('company_name')}: {e}")
            continue
            
    print(f"[*] Scan complete. Found {len(all_results)}, Passed: {items_passed}")
    return len(all_results), items_passed
