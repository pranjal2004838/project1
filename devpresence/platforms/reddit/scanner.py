import praw
import os
from database import SessionLocal, Opportunity
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD, OPPORTUNITY_KEYWORDS, DRY_RUN

def get_reddit_client():
    if not (REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET):
        return None
    try:
        return praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
            user_agent="DevPresence/1.0 by u/" + (REDDIT_USERNAME or "unknown")
        )
    except:
        return None

def scan_reddit():
    print("Scanning Reddit...")
    reddit = get_reddit_client()
    if not reddit:
        print("Reddit credentials not set. Skipping.")
        return []

    subreddits = ["forhire", "slavelabour", "flutterdev", "reactjs", "startups"]
    found = []
    session = SessionLocal()

    try:
        for sub in subreddits:
            subreddit = reddit.subreddit(sub)
            for submission in subreddit.new(limit=20):
                # Simple keyword matching
                text_to_search = (submission.title + " " + submission.selftext).lower()
                
                is_match = any(word.lower() in text_to_search for word in OPPORTUNITY_KEYWORDS)
                is_hiring = "[hiring]" in submission.title.lower() if sub == "forhire" else True
                
                if is_match and is_hiring:
                    url = f"https://reddit.com{submission.permalink}"
                    if not session.query(Opportunity).filter_by(url=url).first():
                        opp = Opportunity(
                            platform="reddit",
                            url=url,
                            title=submission.title,
                            body=submission.selftext[:500],
                            author=str(submission.author)
                        )
                        session.add(opp)
                        session.commit()
                        found.append(opp)
                        print(f"Found opportunity: {submission.title}")
    except Exception as e:
        print(f"Error scanning reddit: {e}")
    finally:
        session.close()
    
    return found
