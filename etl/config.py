# config.py
from pathlib import Path

DATA_DIR = Path("data_raw")
OUT_DIR = Path("data_out")
DATA_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)

# ---- YouTube API ----
YOUTUBE_API_KEY = "AIzaSyDNMg6GL6H_mWwERLih_UD7AoxDvYRe-Ak"

# Official channel / playlists (Genshin Impact official)
GENSHIN_YT_CHANNEL = "UCiS882YPwZt1NfaM0gR0D9Q"  # GenshinImpact official
CHAR_DEMO_PLAYLIST = "PLqWr7dyJNgLLcg4CLu_gDuqjRy2VH0zIn"  # Character Demo playlist

# Influencer channels (edit list as needed)
#INFLUENCER_CHANNEL_IDS = [
  
#]

# Time windows
PRE_BANNER_DAYS = 14
TRAILER_WINDOW_DAYS = 7

from pathlib import Path

# Directory paths
DATA_DIR = Path("data_raw")
OUT_DIR = Path("data_out")
