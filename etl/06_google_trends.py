# 06_google_trends.py
import pandas as pd
from pytrends.request import TrendReq
from config import PRE_BANNER_DAYS

def fetch_trends(character, banner_start):
    pytrend = TrendReq()
    start_dt = pd.to_datetime(banner_start) - pd.Timedelta(days=PRE_BANNER_DAYS*2)
    end_dt = pd.to_datetime(banner_start)

    timeframe = f"{start_dt.date()} {end_dt.date()}"
    pytrend.build_payload([character], timeframe=timeframe)
    df = pytrend.interest_over_time()

    if df.empty:
        return {"google_trends_mean_14d_pre": 0.0, "google_trends_peak_14d_pre": 0.0}

    # last 14 days before banner
    last14 = df.tail(PRE_BANNER_DAYS)
    return {
        "google_trends_mean_14d_pre": float(last14[character].mean()),
        "google_trends_peak_14d_pre": float(last14[character].max())
    }
