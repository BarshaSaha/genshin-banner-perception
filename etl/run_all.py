# run_all.py
from banner_history import scrape_banner_history
from youtube_stats import run as yt_run
from merge_panel import build_panel

def main():
    scrape_banner_history()
    yt_run()
    build_panel()
    print("Done. See data_out/banners_panel_full.csv")

if __name__ == "__main__":
    main()
