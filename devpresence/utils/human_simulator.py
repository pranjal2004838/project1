import random
import time
from datetime import datetime
import pytz
from config import TIMEZONE

def human_delay(min_sec=2, max_sec=8):
    time.sleep(random.uniform(min_sec, max_sec))

def typing_delay(text: str):
    words = len(text.split())
    # Average human types 40 WPM
    time.sleep((words / 40) * 60 * random.uniform(0.7, 1.3))

DAILY_LIMITS = {
    "linkedin_posts": 2,
    "linkedin_comments": 15,
    "linkedin_dms": 10,
    "linkedin_connections": 20,
    "reddit_posts": 3,
    "reddit_comments": 20,
    "discord_messages": 10,
    "slack_messages": 5,
}

POST_TIMES = {
    "linkedin": ["08:30", "12:00", "18:00", "20:30"],
    "reddit": ["10:00", "14:00", "21:00"],
    "discord": ["11:00", "16:00", "22:00"],
}

def should_post_now(platform: str) -> bool:
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    current_time = f"{now.hour:02d}:{now.minute:02d}"
    
    if platform not in POST_TIMES:
        return True
    
    # Check if we are within 15 minutes of an optimal posting time
    for target_time in POST_TIMES[platform]:
        target_h, target_m = map(int, target_time.split(':'))
        minutes_diff = abs((now.hour * 60 + now.minute) - (target_h * 60 + target_m))
        if minutes_diff <= 15:
            return True
            
    return False

def rotate_user_agent() -> str:
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
    ]
    return random.choice(agents)
