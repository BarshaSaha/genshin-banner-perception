import importlib

PIPELINE = [
    "01_banner_history",
    "02_revenue_genshinlab",
    "03_youtube_stats",
    "07_merge_panel",   # 04–06 are called INSIDE this script
]

def main():
    for module_name in PIPELINE:
        print(f"\n=== Running {module_name} ===")
        module = importlib.import_module(f"etl.{module_name}")

        # Prefer main(), fallback to run()
        if hasattr(module, "main"):
            module.main()
        elif hasattr(module, "run"):
            module.run()
        else:
            print(f"[WARN] No main() or run() found in {module_name}")

    print("\nPipeline complete.\n")

if __name__ == "__main__":
    main()

