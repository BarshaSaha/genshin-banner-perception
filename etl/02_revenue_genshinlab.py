# 02_revenue_genshinlab.py

# --- SAFE CONFIG LOADER ---
try:
    from .config_local import *   # use real local keys (not committed)
except ImportError:
    from .config import *         # fallback to public-safe config
# ---------------------------


import pandas as pd
import requests
from config import DATA_DIR

GENSHINLAB_URL = "https://genshinlab.com/genshin-impact-revenue-chart/"

def scrape_revenue_genshinlab():
    # Many sites render via embedded JSON; if blocked, export manually once.
    # Fallback: user exports CSV from chart UI.
    # Here we simply store placeholder for manual export to keep pipeline robust.
    print("Export revenue CSV from GenshinLab chart UI and save as data_raw/revenue_genshinlab.csv")
    return None

if __name__ == "__main__":
    scrape_revenue_genshinlab()
