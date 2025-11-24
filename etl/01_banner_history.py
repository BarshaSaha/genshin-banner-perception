# 01_banner_history.py

# --- SAFE CONFIG LOADER ---
try:
    from .config_local import *   # use real local keys (not committed)
except ImportError:
    from .config import *         # fallback to public-safe config
# ---------------------------


import pandas as pd
import requests
from bs4 import BeautifulSoup
# from config import DATA_DIR

WIKI_URL = "https://genshin-impact.fandom.com/wiki/Wish/History"

def scrape_banner_history():
    html = requests.get(WIKI_URL).text
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table")
    rows = []

    for t in tables:
        for tr in t.find_all("tr")[1:]:
            tds = [td.get_text(" ", strip=True) for td in tr.find_all(["td","th"])]
            if len(tds) < 3:
                continue
            # heuristic parse: banner name + dates + 5★
            row_txt = " | ".join(tds)
            if "—" not in row_txt and "-" not in row_txt:
                continue
            rows.append(tds)

    df = pd.DataFrame(rows)
    df.to_csv(DATA_DIR / "banner_history_raw.csv", index=False)
    return df

if __name__ == "__main__":
    scrape_banner_history()
