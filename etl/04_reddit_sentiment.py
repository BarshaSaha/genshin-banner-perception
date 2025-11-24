# 04_reddit_sentiment.py

# --- SAFE CONFIG LOADER ---
try:
    from .config_local import *   # use real local keys (not committed)
except ImportError:
    from .config import *         # fallback to public-safe config
# ---------------------------


import pandas as pd
import datetime as dt
import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import PRE_BANNER_DAYS

# Fill with your keys
REDDIT_CLIENT_ID = "..."
REDDIT_CLIENT_SECRET = "..."
REDDIT_USER_AGENT = "genshin-banner-study"

SUBREDDITS = ["Genshin_Impact", "GenshinImpactTips", "Genshin_Maining"]

def reddit_client():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

def fetch_reddit(character, banner_start):
    r = reddit_client()
    analyzer = SentimentIntensityAnalyzer()
    start_dt = pd.to_datetime(banner_start) - pd.Timedelta(days=PRE_BANNER_DAYS)

    posts = []
    for sub in SUBREDDITS:
        for post in r.subreddit(sub).search(character, time_filter="month", limit=500):
            created = dt.datetime.fromtimestamp(post.created_utc)
            if created < start_dt.to_pydatetime() or created > pd.to_datetime(banner_start).to_pydatetime():
                continue
            score = analyzer.polarity_scores(post.title + " " + post.selftext)["compound"]
            posts.append([character, post.id, created, score])

    df = pd.DataFrame(posts, columns=["character_5star","post_id","created","sentiment"])
    return {
        "reddit_posts_14d_pre": len(df),
        "reddit_sentiment_14d_pre": df["sentiment"].mean() if len(df) else 0.0
    }

if __name__ == "__main__":
    pass
