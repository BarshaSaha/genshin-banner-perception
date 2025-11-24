# 07_merge_panel.py

# --- SAFE CONFIG LOADER ---
try:
    from .config_local import *
except ImportError:
    from .config import *
# ---------------------------

import pandas as pd

import pandas as pd
import importlib

# Dynamically import modules with numeric names
twitter_mod = importlib.import_module("etl.05_twitter_sentiment")
reddit_mod = importlib.import_module("etl.04_reddit_sentiment")
trends_mod = importlib.import_module("etl.06_google_trends")

fetch_twitter = twitter_mod.fetch_twitter
fetch_reddit = reddit_mod.fetch_reddit
fetch_trends = trends_mod.fetch_trends


def build_panel():
    banners = pd.read_csv("data_raw/banner_history_clean.csv")  # cleaned from raw
    rev = pd.read_csv("data_raw/revenue_genshinlab.csv")
    chars = pd.read_csv("data_raw/characters_master.csv")
    yt = pd.read_csv("data_raw/youtube_stats.csv")

    # merge structural
    df = banners.merge(chars, on="character_5star", how="left")

    # merge revenue
    df = df.merge(rev, on=["patch","phase","character_5star"], how="left")
    df["log_revenue"] = (df["revenue_cn_ios_usd"]+1).apply(lambda x: __import__("math").log(x))

    # attach pre-banner perception
    perception_rows = []
    for _, row in df.iterrows():
        char = row["character_5star"]
        start = row["banner_start"]

        tw = fetch_twitter(char, start)
        rd = fetch_reddit(char, start)
        tr = fetch_trends(char, start)

        perception_rows.append({**tw, **rd, **tr})

    perc = pd.DataFrame(perception_rows)
    df = pd.concat([df.reset_index(drop=True), perc], axis=1)

    OUT_DIR.mkdir(exist_ok=True)
    df.to_csv(OUT_DIR / "banners_panel_full.csv", index=False)
    return df

if __name__ == "__main__":
    build_panel()
