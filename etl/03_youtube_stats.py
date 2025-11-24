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
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        req = yt.videos().list(part="snippet,statistics", id=",".join(chunk))
        res = req.execute()
        for it in res.get("items", []):
            s = it["statistics"]
            sn = it["snippet"]
            stats.append({
                "video_id": it["id"],
                "title": sn.get("title"),
                "publishedAt": sn.get("publishedAt"),
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0))
            })
    return pd.DataFrame(stats)

def run(char_master_path="data_raw/characters_master.csv"):
    cm = pd.read_csv(char_master_path)
    video_ids = pd.concat([
        cm["demo_video_id"].dropna(),
        cm["teaser_video_id"].dropna()
    ]).unique().tolist()

    df = fetch_video_stats(video_ids)
    df["engagement_rate"] = (df["likes"] + df["comments"]) / df["views"].replace(0, 1)
    df.to_csv(DATA_DIR / "youtube_stats.csv", index=False)
    return df

if __name__ == "__main__":
    run()
