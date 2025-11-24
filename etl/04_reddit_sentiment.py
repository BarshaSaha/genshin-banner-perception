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
        return {"reddit_posts_14d_pre": 0, "reddit_sentiment_14d_pre": 0.0}

    analyzer = SentimentIntensityAnalyzer()

    banner_start = pd.to_datetime(banner_start)
    start_dt = banner_start - pd.Timedelta(days=PRE_BANNER_DAYS)

    posts = []
    for sub in SUBREDDITS:
        for post in r.subreddit(sub).search(character, time_filter="month", limit=500):
            created = dt.datetime.fromtimestamp(post.created_utc)
            if created < start_dt.to_pydatetime() or created > banner_start.to_pydatetime():
                continue
            content = (post.title or "") + " " + (getattr(post, "selftext", "") or "")
            score = analyzer.polarity_scores(content)["compound"]
            posts.append(score)

    return {
        "reddit_posts_14d_pre": len(posts),
        "reddit_sentiment_14d_pre": sum(posts)/len(posts) if posts else 0.0
    }

def run(banner_clean_path=None):
    if banner_clean_path is None:
        banner_clean_path = DATA_DIR / "banner_history_clean.csv"

    df_banner = pd.read_csv(banner_clean_path)
    rows = []
    for _, r in df_banner.iterrows():
        char = r["character_5star"]
        start = r["banner_start"]
        out = fetch_reddit(char, start)
        rows.append({
            "patch_version": r.get("patch_version"),
            "character_5star": char,
            "banner_start": start,
            **out
        })

    out_df = pd.DataFrame(rows)
    out_path = DATA_DIR / "reddit_sentiment_14d_pre.csv"
    out_df.to_csv(out_path, index=False)
    print(f"[INFO] Saved Reddit reference file → {out_path}")
    return out_df

def main():
    run()

if __name__ == "__main__":
    main()
