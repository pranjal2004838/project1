from apscheduler.schedulers.background import BackgroundScheduler
import time
from platforms.reddit.scanner import scan_reddit
from platforms.linkedin.scanner import scan_linkedin

def scan_all_platforms():
    print("Initiating full platform scan...")
    scan_reddit()
    scan_linkedin()
    print("Scan complete.")

def start_scheduler():
    scheduler = BackgroundScheduler()

    # Scan for opportunities every 30 minutes
    scheduler.add_job(scan_all_platforms, 'interval', minutes=30)
    
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to exit.")
    
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    start_scheduler()
