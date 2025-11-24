# 07_merge_panel.py

# --- SAFE CONFIG LOADER ---
try:
    from .config_local import *
except ImportError:
    from .config import *
# ---------------------------

import pandas as pd
import importlib
from pathlib import Path

# Dynamically import modules with numeric names (Python cannot import 0-prefixed files directly)
twitter_mod = importlib.import_module("etl.05_twitter_sentiment")
reddit_mod = importlib.import_module("etl.04_reddit_sentiment")
trends_mod = importlib.import_module("etl.06_google_trends")

fetch_twitter = twitter_mod.fetch_twitter
fetch_reddit = reddit_mod.fetch_reddit
fetch_trends = trends_mod.fetch_trends

# =====================================================================
# UTILITIES
# =====================================================================

def safe_read_csv(path, required_cols=None):
    """Safely load CSV; if missing, return empty DataFrame with required cols."""
    path = Path(path)
    if not path.exists():
        print(f"[WARN] Missing file: {path}. Using empty DataFrame.")
        return pd.DataFrame(columns=required_cols or [])
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        print(f"[ERROR] Could not read {path}: {e}")
        return pd.DataFrame(columns=required_cols or [])


# =====================================================================
# MAIN MERGE FUNCTION
# =====================================================================

def run(output_path=None):
    print("[INFO] Merging panel dataset...")

    # ----------------------------
    # 1. Load banner history
    # ----------------------------
    banner_cols = [
        "patch_version","character_5star","banner_start","banner_end","banner_type"
    ]
    df_banner = safe_read_csv(DATA_DIR / "banner_history_clean.csv", required_cols=banner_cols)

    if df_banner.empty:
        print("[WARN] banner_history_clean.csv is empty; panel will be empty.")
        return pd.DataFrame()

    # ----------------------------
    # 2. Load revenue data
    # ----------------------------
    rev_cols = ["patch_version","revenue_ios","revenue_global"]
    df_rev = safe_read_csv(DATA_DIR / "revenue_genshinlab.csv", required_cols=rev_cols)

    # ----------------------------
    # 3. Load YouTube stats
    # ----------------------------
    y_cols = ["video_id","title","publishedAt","views","likes","comments","engagement_rate"]
    df_y = safe_read_csv(DATA_DIR / "youtube_stats.csv", required_cols=y_cols)

    # Merge YouTube stats by character name via a lookup in characters_master.csv
    df_char = safe_read_csv(DATA_DIR / "characters_master.csv")

    if not df_char.empty:
        # join demo + teaser stats
        df_y_demo = df_y.merge(df_char[["character_5star","demo_video_id"]],
                               left_on="video_id", right_on="demo_video_id", how="inner")
        df_y_demo = df_y_demo.groupby("character_5star", as_index=False).agg(
            demo_views=("views","max"),
            demo_likes=("likes","max"),
            demo_comments=("comments","max"),
            demo_engagement=("engagement_rate","max")
        )

        df_y_teas = df_y.merge(df_char[["character_5star","teaser_video_id"]],
                               left_on="video_id", right_on="teaser_video_id", how="inner")
        df_y_teas = df_y_teas.groupby("character_5star", as_index=False).agg(
            teaser_views=("views","max"),
            teaser_likes=("likes","max"),
            teaser_comments=("comments","max"),
            teaser_engagement=("engagement_rate","max")
        )

        df_youtube = df_y_demo.merge(df_y_teas, on="character_5star", how="outer")
    else:
        print("[WARN] characters_master.csv missing; YouTube panel empty.")
        df_youtube = pd.DataFrame(columns=["character_5star"])

    # ----------------------------
    # 4. Merge banner history + revenue + youtube
    # ----------------------------
    df_panel = (df_banner
        .merge(df_rev, on="patch_version", how="left")
        .merge(df_youtube, on="character_5star", how="left")
    )

    # ----------------------------
    # 5. Add online sentiment metrics (Twitter, Reddit, Trends)
    # ----------------------------
    twitter_posts = []
    twitter_sent = []
    reddit_posts = []
    reddit_sent = []
    trends_mean = []
    trends_peak = []

    for _, row in df_panel.iterrows():
        char = row["character_5star"]
        banner_start = row["banner_start"]

        # Twitter
        tw = fetch_twitter(char, banner_start)
        twitter_posts.append(tw["twitter_posts_14d_pre"])
        twitter_sent.append(tw["twitter_sentiment_14d_pre"])

        # Reddit
        rd = fetch_reddit(char, banner_start)
        reddit_posts.append(rd["reddit_posts_14d_pre"])
        reddit_sent.append(rd["reddit_sentiment_14d_pre"])

        # Google Trends
        tr = fetch_trends(char, banner_start)
        trends_mean.append(tr["google_trends_mean_14d_pre"])
        trends_peak.append(tr["google_trends_peak_14d_pre"])

    df_panel["twitter_posts_14d_pre"] = twitter_posts
    df_panel["twitter_sentiment_14d_pre"] = twitter_sent
    df_panel["reddit_posts_14d_pre"] = reddit_posts
    df_panel["reddit_sentiment_14d_pre"] = reddit_sent
    df_panel["google_trends_mean_14d_pre"] = trends_mean
    df_panel["google_trends_peak_14d_pre"] = trends_peak

    # ----------------------------
    # 6. Save final merged dataset
    # ----------------------------
    if output_path is None:
        output_path = OUT_DIR / "panel_dataset.csv"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df_panel.to_csv(output_path, index=False)

    print(f"[INFO] Panel dataset saved to {output_path}")
    return df_panel


def main():
    run()


if __name__ == "__main__":
    main()
