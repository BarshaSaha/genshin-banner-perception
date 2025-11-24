# etl/run_all.py
"""
Runs ETL modules in order.
Each module must expose a main() or run() function.
"""

import importlib

# --------------------------------------------------
# PIPELINE ORDER
# --------------------------------------------------
PIPELINE = [
    "00_character_list",
    "01_banner_history",
    "02_revenue_genshinlab",
    "03_youtube_stats",
    # "04_reddit_sentiment",   # optional
    # "05_twitter_sentiment",
    # "06_google_trends",
    "07_merge_panel",
]

# --------------------------------------------------
# EXECUTION LOGIC
# --------------------------------------------------
def main():
    for module_name in PIPELINE:
        print(f"\n=== Running {module_name} ===")

        try:
            module = importlib.import_module(f"etl.{module_name}")
        except Exception as e:
            print(f"[ERROR] cannot import {module_name}: {e}")
            continue

        try:
            if hasattr(module, "main"):
                module.main()
            elif hasattr(module, "run"):
                module.run()
            else:
                print(f"[WARN] No main() or run() found in {module_name}")
        except Exception as e:
            print(f"[ERROR in {module_name}] {e}")

    print("\nPipeline complete.\n")


if __name__ == "__main__":
    main()
