import os
from dotenv import load_dotenv

# Try to load .env from the devpresence dir and root dir
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_WORKSPACE_IDS = os.getenv("SLACK_WORKSPACE_IDS", "").split(",")

TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
ENABLE_AUTO_POST = os.getenv("ENABLE_AUTO_POST", "false").lower() == "true"
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

PROFILE = """
Developer: Pranjal Jha, 3rd year ECE student at JNTUH Hyderabad
Skills: React, Flutter, Node.js, MongoDB, MySQL, Firebase, TypeScript, PHP, REST APIs, WordPress
Experience: 3 years freelancing, 30+ international projects on Fiverr
Open Source: Merged PRs in Mozilla, Zulip, OpenFoodFacts (SvelteKit + Perl repos)
Available: Immediately, remote, open to internship/contract/freelance
Contact: github.com/pranjal2004838 | pranjaljha703@gmail.com
"""

OPPORTUNITY_KEYWORDS = [
    "looking for developer", "need a developer", "hiring developer",
    "need flutter developer", "looking for react dev", "freelance developer needed",
    "need someone to build", "need an app built", "website developer needed",
    "android developer needed", "iOS developer needed", "need web developer",
    "budget for developer", "paid developer", "contract developer",
    "internship developer", "remote developer needed", "full stack needed",
    "need help with my app", "need help with my website",
    "can anyone build", "who can help me build", "MVP developer needed",
    "looking for someone to code", "need coding help",
]

EXCLUDE_KEYWORDS = [
    "unpaid", "equity only", "for free", "volunteer", "no budget",
    "just starting", "learning project", "we're students"
]