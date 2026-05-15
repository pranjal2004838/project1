import time
from scrapers.reddit_scraper import scrape_reddit_leads
from ai.freelance_scorer import score_freelance_lead, generate_freelance_message
from database.db_client import DatabaseClient

def run_freelance_scan(db: DatabaseClient):
    print("[*] Starting Freelance Leads scan...")
    
    # Scrape leads
    raw_leads = scrape_reddit_leads()
    print(f"[*] Found {len(raw_leads)} raw leads from Reddit.")
    
    items_passed = 0
    for i, lead in enumerate(raw_leads):
        try:
            # Score lead
            analysis = score_freelance_lead(lead)
            
            lead.update({
                "score": analysis.get("score", 0),
                "service_match": analysis.get("service_match", ""),
                "urgency": analysis.get("urgency", "low"),
                "pain_point": analysis.get("pain_point", ""),
                "disqualify_reason": analysis.get("disqualify_reason"),
                "pass": 1 if analysis.get("pass") else 0
            })
            
            if lead["pass"]:
                items_passed += 1
                
            # Automatically generate message for ALL leads as requested
            print(f"[*] Generating message for lead: {lead.get('title')[:30]}...")
            msg_data = generate_freelance_message(lead)
            lead["generated_message"] = msg_data.get("message", "")
            
            # Save to DB
            db.insert_lead("leads", lead)
            
            # Rate limit
            if i < len(raw_leads) - 1:
                time.sleep(4.1)
                
        except Exception as e:
            print(f"[!] Error processing lead {lead.get('url')}: {e}")
            
    print(f"[*] Freelance scan complete. Found {len(raw_leads)}, Passed: {items_passed}")
    return len(raw_leads), items_passed
