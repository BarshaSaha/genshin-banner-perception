# 04_reddit_sentiment.py

# --- SAFE CONFIG LOADER ---
try:
    from .config_local import *
except ImportError:
    from .config import *
# ---------------------------

import pandas as pd
import datetime as dt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# praw import should be inside try if you want skip-safety
try:
    import praw
    PRAW_OK = True
except Exception as e:
    print(f"[Skip] praw not available: {e}")
    PRAW_OK = False

SUBREDDITS = ["Genshin_Impact", "GenshinImpactTips", "Genshin_Maining"]


def reddit_client():
    if not PRAW_OK:
        return None
    if not REDDIT_CLIENT_ID or "PENDING" in str(REDDIT_CLIENT_ID):
        return None
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent="genshin-banner-study"
    )


def fetch_reddit(character, banner_start):
    r = reddit_client()
    if r is None:
        return {
            "reddit_posts_14d_pre": 0,
            "reddit_sentiment_14d_pre": 0.0
        }
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
