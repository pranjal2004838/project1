import requests
from database import SessionLocal, Opportunity
from config import DISCORD_WEBHOOK_URL, DRY_RUN

def post_discord(message: str, channel: str = None):
    if DRY_RUN:
        print(f"[DRY RUN] Discord POST: {message}")
        return True
        
    if not DISCORD_WEBHOOK_URL:
        print("Discord Webhook URL not set.")
        return False
        
    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("Posted to Discord successfully.")
        return True
    except Exception as e:
        print(f"Error posting to Discord: {e}")
        return False
