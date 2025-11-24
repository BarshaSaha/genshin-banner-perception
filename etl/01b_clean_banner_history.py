# 01b_clean_banner_history.py
"""
Clean banner_history_raw.csv into banner_history_clean.csv.

Inputs:
- data_raw/banner_history_raw.csv
  Expected 3 columns (no header) from your download:
    0: banner_info  (e.g., "Ballad in Goblets 2020-09-28")
    1: featured     (space-separated featured characters/weapons)
    2: duration     (e.g., "September 28, 2020 — October 18, 2020")

Outputs:
- data_raw/banner_history_clean.csv
  Columns:
    patch_version, character_5star, banner_start, banner_end, banner_type, banner_name

Key features:
- Automatically fetches current 5★ playable character list from
  https://genshin-impact.fandom.com/wiki/Character/List by filtering Quality == "5★"
- Caches that list locally to data_raw/five_star_list.json for reproducibility/offline runs
- Robust name normalization for apostrophes, non-breaking spaces, etc.
- Simple patch mapping by banner_start date (can be extended later)
"""

import re
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

RAW = Path("data_raw/banner_history_raw.csv")
OUT = Path("data_raw/banner_history_clean.csv")

FIVE_STAR_URL = "https://genshin-impact.fandom.com/wiki/Character/List"
CACHE_PATH = Path("data_raw/five_star_list.json")


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def normalize_name(s: str) -> str:
    """Normalize unicode punctuation/spaces to maximize matching."""
    if not isinstance(s, str):
        return s
    s = s.replace("\u00a0", " ")  # nbsp
    s = s.replace("’", "'")       # curly apostrophe
    s = re.sub(r"\s+", " ", s).strip()
    return s


def fetch_five_star_characters(force_refresh: bool = False) -> set:
    """
    Scrape Fandom Character/List and return set of 5★ playable character names.
    Uses disk cache to avoid repeated scraping.
    """
    if CACHE_PATH.exists() and not force_refresh:
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            pass  # fall through to re-fetch if cache broken

    resp = requests.get(FIVE_STAR_URL, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # Fandom uses a sortable wikitable; we scan rows and read "Quality" column.
    rows = soup.select("table.wikitable.sortable tr")
    five_star_set = set()

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        # Typical columns:
        # 0 Icon, 1 Name, 2 Quality, 3 Element, 4 Weapon, ...
        name = normalize_name(cols[1].get_text(strip=True))
        quality = cols[2].get_text(strip=True)

        if quality == "5★" and name:
            five_star_set.add(name)

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(five_star_set), f, ensure_ascii=False, indent=2)

    print(f"[INFO] Fetched {len(five_star_set)} 5★ characters.")
    return five_star_set


def clean_duration(range_str: str):
    """
    Parse 'September 28, 2020 — October 18, 2020' into (start_dt, end_dt).
    Returns pandas timestamps (or None, None).
    """
    if not isinstance(range_str, str) or "—" not in range_str:
        return None, None
    try:
        start_str, end_str = [x.strip() for x in range_str.split("—", 1)]
        start_dt = pd.to_datetime(start_str, errors="coerce")
        end_dt = pd.to_datetime(end_str, errors="coerce")
        return start_dt, end_dt
    except Exception:
        return None, None


def determine_patch_version(start_dt: pd.Timestamp) -> str:
    """
    Map banner start date to patch version.

    This is a pragmatic mapping based on version release dates.
    Extend freely if you need exact mapping for newer patches.
    """
    if pd.isna(start_dt):
        return None

    # List of (version, release_date) in ascending order.
    # Source: official patch release timeline; extend as needed.
    releases = [
        ("1.0", "2020-09-28"),
        ("1.1", "2020-11-11"),
        ("1.2", "2020-12-23"),
        ("1.3", "2021-02-03"),
        ("1.4", "2021-03-17"),
        ("1.5", "2021-04-28"),
        ("1.6", "2021-06-09"),
        ("2.0", "2021-07-21"),
        ("2.1", "2021-09-01"),
        ("2.2", "2021-10-13"),
        ("2.3", "2021-11-24"),
        ("2.4", "2022-01-05"),
        ("2.5", "2022-02-16"),
        ("2.6", "2022-03-30"),
        ("2.7", "2022-05-31"),
        ("2.8", "2022-07-13"),
        ("3.0", "2022-08-24"),
        ("3.1", "2022-09-28"),
        ("3.2", "2022-11-02"),
        ("3.3", "2022-12-07"),
        ("3.4", "2023-01-18"),
        ("3.5", "2023-03-01"),
        ("3.6", "2023-04-12"),
        ("3.7", "2023-05-24"),
        ("3.8", "2023-07-05"),
        ("4.0", "2023-08-16"),
        ("4.1", "2023-09-27"),
        ("4.2", "2023-11-08"),
        ("4.3", "2023-12-20"),
        ("4.4", "2024-01-31"),
        ("4.5", "2024-03-13"),
        ("4.6", "2024-04-24"),
        ("4.7", "2024-06-05"),
        ("4.8", "2024-07-17"),
        ("5.0", "2024-08-28"),
        ("5.1", "2024-10-09"),
        ("5.2", "2024-11-20"),
        ("5.3", "2025-01-01"),
        ("5.4", "2025-02-12"),
        ("5.5", "2025-03-26"),
    ]

    releases = [(v, pd.to_datetime(d)) for v, d in releases]

    current = None
    for v, d in releases:
        if start_dt >= d:
            current = v
        else:
            break
    return current


def infer_banner_type(banner_name: str) -> str:
    """
    Very light heuristic:
    - if contains 'rerun' in name, mark RERUN
    - else NEW
    You can overwrite later in analysis.
    """
    if isinstance(banner_name, str) and "rerun" in banner_name.lower():
        return "RERUN"
    return "NEW"


def extract_five_star(featured_text: str, five_star_set: set) -> str:
    """
    Detect 5★ character appearing in featured_text by substring matching.
    Sorts by length so multi-word names match first.
    """
    if not isinstance(featured_text, str):
        return None

    featured_text = normalize_name(featured_text)

    for name in sorted(five_star_set, key=len, reverse=True):
        if name in featured_text:
            return name
    return None


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main():
    if not RAW.exists():
        raise FileNotFoundError(f"Missing raw banner file at {RAW}")

    five_star_set = fetch_five_star_characters()

    df = pd.read_csv(RAW, header=None)
    if df.shape[1] < 3:
        raise ValueError("banner_history_raw.csv must have at least 3 columns.")

    df = df.iloc[:, :3]
    df.columns = ["banner_info", "featured", "duration"]

    cleaned_rows = []

    for _, row in df.iterrows():
        banner_info = normalize_name(str(row["banner_info"]))
        featured = row["featured"]
        duration = row["duration"]

        # Banner name is text before last space-date token if present
        # Example: "Ballad in Goblets 2020-09-28" -> "Ballad in Goblets"
        banner_name = re.sub(r"\s+\d{4}-\d{2}-\d{2}$", "", banner_info).strip()

        char5 = extract_five_star(featured, five_star_set)
        start_dt, end_dt = clean_duration(duration)

        if char5 is None or start_dt is None or pd.isna(start_dt):
            continue

        cleaned_rows.append({
            "patch_version": determine_patch_version(start_dt),
            "character_5star": char5,
            "banner_start": start_dt.date().isoformat(),
            "banner_end": end_dt.date().isoformat() if end_dt is not None and not pd.isna(end_dt) else None,
            "banner_type": infer_banner_type(banner_name),
            "banner_name": banner_name
        })

    out_df = pd.DataFrame(cleaned_rows)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUT, index=False)

    print(f"[INFO] Cleaned {len(out_df)} banner rows → {OUT}")


if __name__ == "__main__":
    main()
