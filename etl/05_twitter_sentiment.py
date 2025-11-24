# 05_twitter_sentiment.py
import pandas as pd
import snscrape.modules.twitter as sntwitter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import PRE_BANNER_DAYS

def fetch_twitter(character, banner_start):
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
