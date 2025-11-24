# 00_character_list.py
"""
Export character list from Genshin Impact Fandom Character/List page.

Priority:
1) Try ONLINE fetch from WIKI_URL
2) If blocked, fallback to:
   - data_raw/character_list_raw.csv
   - data_raw/character_list_raw.html

OUTPUT:
- data_raw/character_list.csv with columns:
  Name, Quality, Element, Weapon, Region, Model Type, Release Date, Version
"""

import re
import pandas as pd
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Make 'main' discoverable by run_all.py
__all__ = ["main"]

WIKI_URL = "https://genshin-impact.fandom.com/wiki/Character/List#Playable_Characters"

RAW_CSV = Path("data_raw/character_list_raw.csv")
RAW_HTML = Path("data_raw/character_list_raw.html")
OUT = Path("data_raw/character_list.csv")


# -----------------------------------------------------------
# Helpers
# -----------------------------------------------------------
def normalize(s):
    if not isinstance(s, str):
        return s
    s = s.replace("\u00a0", " ").replace("’", "'").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def parse_wikitable(table) -> pd.DataFrame:
    """
    Parse Fandom Character/List wikitable into the requested schema.
    Expected order:
      0 icon, 1 name, 2 quality, 3 element, 4 weapon,
      5 region, 6 model type, 7 release date, 8 version
    """
    rows = []
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 6:
            continue

        def get(i):
            return normalize(tds[i].get_text(strip=True)) if i < len(tds) else None

        rows.append({
            "Name": get(1),
            "Quality": get(2),
            "Element": get(3),
            "Weapon": get(4),
            "Region": get(5),
            "Model Type": get(6),
            "Release Date": get(7),
            "Version": get(8),
        })

    df = pd.DataFrame(rows).dropna(subset=["Name"])
    return df


# -----------------------------------------------------------
# Online fetch
# -----------------------------------------------------------
def try_fetch_online() -> pd.DataFrame | None:
    """Best-effort attempt to fetch Character/List from Fandom."""
    try:
        resp = requests.get(
            WIKI_URL,
            timeout=25,
            headers={"User-Agent": "Mozilla/5.0"}  # reduces basic bot blocks
        )
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        table = soup.find("table", {"class": re.compile("wikitable")})

        if table is None:
            print("[WARN] Online page loaded but no wikitable found.")
            return None

        df = parse_wikitable(table)
        return df if not df.empty else None

    except Exception as e:
        print(f"[WARN] Online fetch failed/blocked: {e}")
        return None


# -----------------------------------------------------------
# Offline fallbacks
# -----------------------------------------------------------
def parse_from_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    cols = {c.lower(): c for c in df.columns}

    def pick(*keys):
        for k in keys:
            if k in cols:
                return cols[k]
        return None

    name  = pick("name", "character", "playable character")
    qual  = pick("quality", "rarity")
    elem  = pick("element", "vision")
    weap  = pick("weapon", "weapon type")
    reg   = pick("region", "nation")
    model = pick("model type", "body type", "model")
    rel   = pick("release date", "release")
    ver   = pick("version", "release version", "introduced in")

    out = pd.DataFrame({
        "Name": df[name].map(normalize) if name else None,
        "Quality": df[qual].map(normalize) if qual else None,
        "Element": df[elem].map(normalize) if elem else None,
        "Weapon": df[weap].map(normalize) if weap else None,
        "Region": df[reg].map(normalize) if reg else None,
        "Model Type": df[model].map(normalize) if model else None,
        "Release Date": df[rel].map(normalize) if rel else None,
        "Version": df[ver].map(normalize) if ver else None,
    })

    return out.dropna(subset=["Name"])


def parse_from_html(path: Path) -> pd.DataFrame:
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", {"class": re.compile("wikitable")})

    if table is None:
        raise ValueError("No wikitable found in character_list_raw.html")

    return parse_wikitable(table)


# -----------------------------------------------------------
# Main
# -----------------------------------------------------------
def main():
    print("[INFO] Running 00_character_list...")

    # 1) ONLINE first
    df = try_fetch_online()
    src = "online wiki"

    # 2) FALLBACK to offline raw
    if df is None:
        if RAW_CSV.exists():
            df = parse_from_csv(RAW_CSV)
            src = str(RAW_CSV)
        elif RAW_HTML.exists():
            df = parse_from_html(RAW_HTML)
            src = str(RAW_HTML)
        else:
            raise FileNotFoundError(
                "No character list source available.\n"
                "Either allow online fetch OR provide:\n"
                "- data_raw/character_list_raw.csv\n"
                "- data_raw/character_list_raw.html"
            )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding="utf-8")

    print(f"[INFO] Parsed {len(df)} characters from {src} → {OUT}")


if __name__ == "__main__":
    main()

