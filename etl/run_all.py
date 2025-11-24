import importlib

PIPELINE = [
    "01_banner_history",
    "02_revenue_genshinlab",
    "03_youtube_stats",
    "04_reddit_sentiment",
    "05_twitter_sentiment",
    "06_google_trends",
    "07_merge_panel",
]

def main():
    for module_name in PIPELINE:
        print(f"=== Running {module_name} ===")
        module = importlib.import_module(f"etl.{module_name}")
        
        # Prefer main(), fallback to run()
        if hasattr(module, "main"):
            module.main()
        elif hasattr(module, "run"):
            module.run()
        else:
            print(f"[WARN] {module_name} has no main() or run() to execute.")
    print("\nPipeline complete!\n")

if __name__ == "__main__":
    main()
