import time
import json
from scrapers.github_org_scraper import search_small_orgs_and_founders
from ai.cold_email_scorer import score_cold_email_target, generate_founder_cold_email
from database.db_client import DatabaseClient

def run_cold_email_scan(db: DatabaseClient):
    print("[*] Starting Cold Email Founder scan...")
    
    # Use the org scraper to find small active tech teams
    raw_targets = search_small_orgs_and_founders(query_term="founder")
    print(f"[*] Found {len(raw_targets)} potential founders/companies.")
    
    items_passed = 0
    for i, target in enumerate(raw_targets):
        try:
            # Score
            analysis = score_cold_email_target(target)
            
            target.update({
                "score": analysis.get("score", 0),
                "fit_reason": analysis.get("fit_reason", ""),
                "pass": 1 if analysis.get("pass") else 0
            })
            
            if target["pass"]:
                items_passed += 1
                
            # Automatically generate cold email
            print(f"[*] Generating cold email for: {target.get('founder_name')}...")
            email_data = generate_founder_cold_email(target)
            target["generated_subject"] = email_data.get("subject", "")
            target["generated_message"] = email_data.get("message", "")
                
            # Save to DB
            db.execute_query(
                "INSERT INTO cold_emails (founder_name, company_name, company_url, tech_stack, activity_signal, score, fit_reason, generated_subject, generated_message, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (target['founder_name'], target['company'], target['url'], target['stack'], target['activity_signal'], target['score'], target['fit_reason'], target['generated_subject'], target['generated_message'], 'new'),
                commit=True
            )
            
            if i < len(raw_targets) - 1:
                time.sleep(4.1)
                
        except Exception as e:
            print(f"[!] Error processing cold email target: {e}")
            
    return len(raw_targets), items_passed
