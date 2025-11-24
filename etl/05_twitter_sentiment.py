# 05_twitter_sentiment.py

# --- SAFE CONFIG LOADER ---
try:
    from .config_local import *
except ImportError:
    from .config import *
# ---------------------------

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

try:
    import snscrape.modules.twitter as sntwitter
    SNSCRAPE_OK = True
except Exception as e:
    print(f"[Skip] snscrape not available: {e}")
    SNSCRAPE_OK = False

def fetch_twitter(character, banner_start):
    if not SNSCRAPE_OK:
        return {"twitter_posts_14d_pre": 0, "twitter_sentiment_14d_pre": 0.0}

    analyzer = SentimentIntensityAnalyzer()
    banner_start = pd.to_datetime(banner_start)
    start_dt = banner_start - pd.Timedelta(days=PRE_BANNER_DAYS)

    query = f'"{character}" Genshin since:{start_dt.date()} until:{banner_start.date()}'
    scores = []
    for tw in sntwitter.TwitterSearchScraper(query).get_items():
        scores.append(analyzer.polarity_scores(tw.content)["compound"])

    return {
        "twitter_posts_14d_pre": len(scores),
        "twitter_sentiment_14d_pre": sum(scores)/len(scores) if scores else 0.0
    }

def run(banner_clean_path=None):
    if banner_clean_path is None:
        banner_clean_path = DATA_DIR / "banner_history_clean.csv"

    df_banner = pd.read_csv(banner_clean_path)
    rows = []
    for _, r in df_banner.iterrows():
        char = r["character_5star"]
        start = r["banner_start"]
        out = fetch_twitter(char, start)
        rows.append({
            "patch_version": r.get("patch_version"),
            "character_5star": char,
            "banner_start": start,
            **out
        })

    out_df = pd.DataFrame(rows)
    out_path = DATA_DIR / "twitter_sentiment_14d_pre.csv"
    out_df.to_csv(out_path, index=False)
    print(f"[INFO] Saved Twitter reference file → {out_path}")
    return out_df

def main():
    run()

if __name__ == "__main__":
    main()
