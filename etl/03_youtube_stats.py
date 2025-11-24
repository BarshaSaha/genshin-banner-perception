# 03_youtube_stats.py

# --- SAFE CONFIG LOADER ---
try:
    from .config_local import *   # use real local keys (not committed)
except ImportError:
    from .config import *         # fallback to public-safe config
# ---------------------------

import pandas as pd
from googleapiclient.discovery import build

def youtube_client():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def fetch_video_stats(video_ids):
    yt = youtube_client()
    stats = []

    # YouTube API allows max 50 IDs per request
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        req = yt.videos().list(
            part="snippet,statistics",
            id=",".join(chunk)
        )
        res = req.execute()

        for it in res.get("items", []):
            s = it.get("statistics", {})
            sn = it.get("snippet", {})
            stats.append({
                "video_id": it.get("id"),
                "title": sn.get("title"),
                "publishedAt": sn.get("publishedAt"),
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0))
            })

    return pd.DataFrame(stats)

def run(char_master_path=None):
    # Default path
    if char_master_path is None:
        char_master_path = DATA_DIR / "characters_master.csv"

    # Read character metadata
    cm = pd.read_csv(char_master_path)

    # Collect demo + teaser IDs
    video_ids = []

    if "demo_video_id" in cm.columns:
        video_ids.extend(cm["demo_video_id"].dropna().astype(str).tolist())

    if "teaser_video_id" in cm.columns:
        video_ids.extend(cm["teaser_video_id"].dropna().astype(str).tolist())

    # Remove duplicates
    video_ids = list(set([vid for vid in video_ids if isinstance(vid, str) and vid.strip()]))

    if len(video_ids) == 0:
        print("[WARN] No video IDs found in characters_master.csv")
        return None

    # Fetch stats
    df = fetch_video_stats(video_ids)

    # Add engagement rate safely
    df["engagement_rate"] = (df["likes"] + df["comments"]) / df["views"].replace(0, 1)

    # Save output
    out_path = DATA_DIR / "youtube_stats.csv"
    df.to_csv(out_path, index=False)
    print(f"[INFO] YouTube stats saved to {out_path}")

    return df

# Allow standalone execution
if __name__ == "__main__":
    run()
