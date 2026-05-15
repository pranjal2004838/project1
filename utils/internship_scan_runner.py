import time
from scrapers.github_org_scraper import search_small_orgs_and_founders
from ai.internship_scorer import score_internship_opportunity
from database.db_client import DatabaseClient

def run_internship_scan(db: DatabaseClient):
    print("[*] Starting Internship & Contract scan...")
    
    # Use the org scraper to find small active tech teams
    raw_opps = search_small_orgs_and_founders(query_term="startup")
    print(f"[*] Found {len(raw_opps)} potential companies.")
    
    items_passed = 0
    for i, opp in enumerate(raw_opps):
        try:
            # Score
            analysis = score_internship_opportunity(opp)
            
            opp.update({
                "score": analysis.get("score", 0),
                "fit_reason": analysis.get("fit_reason", ""),
                "urgency_signal": analysis.get("urgency_signal", ""),
                "pass": 1 if analysis.get("pass") else 0
            })
            
            if opp["pass"]:
                items_passed += 1
                
            # Save to DB
            # We need to map 'name' and 'company' correctly for the opportunities table
            db.execute_query(
                "INSERT INTO opportunities (name, company, source, url, stack, description, score, fit_reason, urgency_signal, pass) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (opp['name'], opp['company'], opp['source'], opp['url'], opp['stack'], opp['description'], opp['score'], opp['fit_reason'], opp['urgency_signal'], opp['pass']),
                commit=True
            )
            
            if i < len(raw_opps) - 1:
                time.sleep(4.1)
                
        except Exception as e:
            print(f"[!] Error processing opportunity: {e}")
            
    return len(raw_opps), items_passed
