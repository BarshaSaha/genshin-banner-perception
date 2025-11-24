import pandas as pd
import re

WIKI_URL = "https://genshin-impact.fandom.com/wiki/Character/List#Playable_Characters"

def scrape_character_list():
    # read all tables that pandas can see
    tables = pd.read_html(WIKI_URL)

    playable = None
    for t in tables:
        cols = [str(c).lower() for c in t.columns]
        if any("name" in c for c in cols) and any(("quality" in c or "rarity" in c) for c in cols):
            playable = t.copy()
            break

    if playable is None:
        raise ValueError("Playable Characters table not found in the online page.")

    # Normalize column names for matching
    colmap = {c.lower(): c for c in playable.columns.astype(str)}

    def pick(*keys):
        for k in keys:
            for lc, orig in colmap.items():
                if k in lc:
                    return orig
        return None

    name_c   = pick("name")
    qual_c   = pick("quality", "rarity")
    elem_c   = pick("element", "vision")
    weap_c   = pick("weapon")
    reg_c    = pick("region", "nation")
    model_c  = pick("model type", "body type", "model")
    date_c   = pick("release date", "release")
    ver_c    = pick("version", "introduced in", "release version")

    out = pd.DataFrame({
        "Name": playable[name_c] if name_c else None,
        "Quality": playable[qual_c] if qual_c else None,
        "Element": playable[elem_c] if elem_c else None,
        "Weapon": playable[weap_c] if weap_c else None,
        "Region": playable[reg_c] if reg_c else None,
        "Model Type": playable[model_c] if model_c else None,
        "Release Date": playable[date_c] if date_c else None,
        "Version": playable[ver_c] if ver_c else None,
    })

    # Clean whitespace
    for c in out.columns:
        out[c] = out[c].astype(str).str.replace("\u00a0", " ").str.strip()
        out[c] = out[c].replace({"nan": None})

    out.to_csv(DATA_DIR / "character_list.csv", index=False, encoding="utf-8")
    print(f"[INFO] Exported {len(out)} characters → {DATA_DIR/'character_list.csv'}")
    return out

