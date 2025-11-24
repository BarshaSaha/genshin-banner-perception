# 05_twitter_sentiment.py

# --- SAFE CONFIG LOADER ---
try:
    from .config_local import *
except ImportError:
    from .config import *
# ---------------------------

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# TRY importing snscrape safely
try:
    import snscrape.modules.twitter as sntwitter
    SNSCRAPE_OK = True
except Exception as e:
    print(f"[Skip] snscrape not available: {e}")
    SNSCRAPE_OK = False

def fetch_twitter(character, banner_start):
    # If snscrape is missing/broken, return zeros instead of crashing
    if not SNSCRAPE_OK:
        return {
            "twitter_posts_14d_pre": 0,
            "twitter_sentiment_14d_pre": 0.0
        }

    analyzer = SentimentIntensityAnalyzer()
    start_dt = pd.to_datetime(banner_start) - pd.Timedelta(days=PRE_BANNER_DAYS)
    end_dt = pd.to_datetime(banner_start)

    query = f'"{character}" Genshin since:{start_dt.date()} until:{end_dt.date()}'
    tweets = []

    for tw in sntwitter.TwitterSearchScraper(query).get_items():
        score = analyzer.polarity_scores(tw.content)["compound"]
        tweets.append(score)

    return {
        "twitter_posts_14d_pre": len(tweets),
        "twitter_sentiment_14d_pre": sum(tweets)/len(tweets) if tweets else 0.0
    }

def main():
    print("[Info] Twitter sentiment is computed inside 07_merge_panel.py")

if __name__ == "__main__":
    main()

