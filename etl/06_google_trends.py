# 06_google_trends.py

# --- SAFE CONFIG LOADER ---
try:
    from .config_local import *
except ImportError:
    from .config import *
# ---------------------------

import pandas as pd

try:
    from pytrends.request import TrendReq
    TRENDS_OK = True
except Exception as e:
    print(f"[Skip] pytrends not available: {e}")
    TRENDS_OK = False

def fetch_trends(character, banner_start):
    if not TRENDS_OK:
        return {"google_trends_mean_14d_pre": 0.0, "google_trends_peak_14d_pre": 0.0}

    pytrend = TrendReq()

    banner_start = pd.to_datetime(banner_start)
    start_dt = banner_start - pd.Timedelta(days=PRE_BANNER_DAYS * 2)
    end_dt = banner_start

    timeframe = f"{start_dt.date()} {end_dt.date()}"
    pytrend.build_payload([character], timeframe=timeframe)

    df = pytrend.interest_over_time()
    if df.empty or character not in df.columns:
        return {"google_trends_mean_14d_pre": 0.0, "google_trends_peak_14d_pre": 0.0}

    last14 = df.tail(PRE_BANNER_DAYS)
    return {
        "google_trends_mean_14d_pre": float(last14[character].mean()),
        "google_trends_peak_14d_pre": float(last14[character].max())
    }

def run(banner_clean_path=None):
    if banner_clean_path is None:
        banner_clean_path = DATA_DIR / "banner_history_clean.csv"

    df_banner = pd.read_csv(banner_clean_path)
    rows = []
    for _, r in df_banner.iterrows():
        char = r["character_5star"]
        start = r["banner_start"]
        out = fetch_trends(char, start)
        rows.append({
            "patch_version": r.get("patch_version"),
            "character_5star": char,
            "banner_start": start,
            **out
        })

    out_df = pd.DataFrame(rows)
    out_path = DATA_DIR / "google_trends_14d_pre.csv"
    out_df.to_csv(out_path, index=False)
    print(f"[INFO] Saved Google Trends reference file → {out_path}")
    return out_df

def main():
    run()

if __name__ == "__main__":
    main()

