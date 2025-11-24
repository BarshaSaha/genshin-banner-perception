# 06_google_trends.py

# --- SAFE CONFIG LOADER ---
try:
    from .config_local import *
except ImportError:
    from .config import *
# ---------------------------

import pandas as pd

# Try importing pytrends safely
try:
    from pytrends.request import TrendReq
    TRENDS_OK = True
except Exception as e:
    print(f"[Skip] pytrends not available: {e}")
    TRENDS_OK = False


def fetch_trends(character, banner_start):
    if not TRENDS_OK:
        return {
            "google_trends_mean_14d_pre": 0.0,
            "google_trends_peak_14d_pre": 0.0
        }

    pytrend = TrendReq()

    banner_start = pd.to_datetime(banner_start)
    start_dt = banner_start - pd.Timedelta(days=PRE_BANNER_DAYS * 2)
    end_dt = banner_start

    timeframe = f"{start_dt.date()} {end_dt.date()}"
    pytrend.build_payload([character], timeframe=timeframe)

    df = pytrend.interest_over_time()

    if df.empty or character not in df.columns:
        return {
            "google_trends_mean_14d_pre": 0.0,
            "google_trends_peak_14d_pre": 0.0
        }

    last14 = df.tail(PRE_BANNER_DAYS)

    return {
        "google_trends_mean_14d_pre": float(last14[character].mean()),
        "google_trends_peak_14d_pre": float(last14[character].max())
    }


def main():
    print("[Info] Google Trends is computed inside 07_merge_panel.py")


if __name__ == "__main__":
    main()

