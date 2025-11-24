# 00_character_list.py
"""
Export character list from Genshin Impact Fandom Character/List page.

Priority order:
1) Try ONLINE fetch from WIKI_URL (works on local machines)
2) If online fails/blocked (common in Codespaces), fallback to:
   - data_raw/character_list_raw.csv  (preferred)
   - data_raw/character_list_raw.html (if you saved the page)

OUTPUT:
- data_raw/character_list.csv
  Columns:
    Name, Quality, Element, Weapon, Region, Model Type, Release Date, Version

Notes:
- This script is designed to be reproducible for reviewers.
- Online scraping is best-effort only; offline raw files guarantee stability.
"""

import re
import pandas as pd
from pathlib import Path
import requests
from bs4 import BeautifulSoup

WIKI_URL = "https://genshin-impact.fandom.com/wiki/Character/List#Playable_Characters"

RAW_CSV = Path("data_raw/character_list_raw.csv")
RAW_HTML = Path("data_raw/character_list_raw.html")
OUT = Path("data_raw/character_list.csv")


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def normalize(s):
    if not isinstance(s, str):
        return s
    s = s.replace("\u00a0", " ").replace("’", "'").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def parse_wikitable(table) -> pd.DataFrame:
    """
    Parse a Fandom wikitable into your required schema.
    Assumes typical column order:
      0 icon, 1 name, 2 quality, 3 element, 4 weapon, 5 region,
      6 model type, 7 release date, 8 version
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


# ---------------------------------------------------------------------
# Online fetch (best effort)
# ---------------------------------------------------------------------
def try_fetch_online() -> pd.DataFrame | None:
    """
    Attempt to fetch Character/List live.
    Returns a DataFrame or None if blocked / layout mismatch.
    """
    try:
        resp = requests.get(
            WIKI_URL,
            timeout=25,
            headers={"User-Agent": "Mozilla/5.0"}  # helps avoid basic bot blocks
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        table = soup.find("table", {"class": re.compile("wikitable")})
        if table is None:
            return None

        df = parse_wikitable(table)
        return df if not df.empty else None

    except Exception as e:
        print(f"[WARN] Online fetch failed/blocked: {e}")
        return None


# ---------------------------------------------------------------------
# Offline fallbacks
# ---------------------------------------------------------------------
def parse_from_csv(path: Path) -> pd.DataFrame:
    """
    Parse a raw CSV export of the Character/List table.
    We detect columns by fuzzy matching typical Fandom headers.
    """
    df = pd.read_csv(path)
    cols = {c.lower(): c for c in df.columns}

    def pick(*keys):
        for k in keys:
            if k in cols:
                return cols[k]
        return None

    name_c  = pick("name", "character", "playable character")
    qual_c  = pick("quality", "rarity")
    elem_c  = pick("element", "vision")
    weap_c  = pick("weapon", "weapon type")
    reg_c   = pick("region", "nation")
    model_c = pick("model type", "body type", "model")
    rel_c   = pick("release date", "release")
    ver_c   = pick("version", "release version", "introduced in")

    out = pd.DataFrame({
        "Name": df[name_c].map(normalize) if name_c else None,
        "Quality": df[qual_c].map(normalize) if qual_c else None,
        "Element": df[elem_c].map(normalize) if elem_c else None,
        "Weapon": df[weap_c].map(normalize) if weap_c else None,
        "Region": df[reg_c].map(normalize) if reg_c else None,
        "Model Type": df[model_c].map(normalize) if model_c else None,
        "Release Date": df[rel_c].map(normalize) if rel_c else None,
        "Version": df[ver_c].map(normalize) if ver_c else None,
    })

    return out.dropna(subset=["Name"])


def parse_from_html(path: Path) -> pd.DataFrame:
    """Parse an offline-saved HTML page and extract the first wikitable."""
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")

    table = soup.find("table", {"class": re.compile("wikitable")})
    if table is None:
        raise ValueError("No wikitable found in character_list_raw.html")

    return parse_wikitable(table)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main():
    # 1) ONLINE first
    df = try_fetch_online()
    src = "online wiki"

    # 2) OFFLINE fallbacks if online blocked
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
                "Either:\n"
                "  - run locally (online fetch works), OR\n"
                "  - provide offline raw export:\n"
                "      data_raw/character_list_raw.csv\n"
                "      data_raw/character_list_raw.html"
            )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding="utf-8")

    print(f"[INFO] Parsed {len(df)} characters from {src} → {OUT}")


if __name__ == "__main__":
    main()

