"""Start the data collection (run in the terminal inside the project folder):

    python run_collection.py               # default: 14 days, top 100 stations
    python run_collection.py --days 7      # fewer days (faster)
    python run_collection.py --start 2026-10-05 --end 2026-10-18

The script can be stopped and restarted at any time:
days that are already loaded are skipped.
"""
import argparse
import time

from src import collect_actual_data, collect_stations, collect_weather, config
from src.db import get_connection


def main():
    p = argparse.ArgumentParser(description="Data collection Group 37")
    p.add_argument("--days", type=int, default=config.N_DAYS)
    p.add_argument("--start", default=None, help="YYYY-MM-DD")
    p.add_argument("--end", default=None, help="YYYY-MM-DD")
    p.add_argument("--top-n", type=int, default=config.TOP_N_STATIONS)
    p.add_argument("--keep-raw", action="store_true", help="do not delete the raw files")
    p.add_argument("--skip-stations", action="store_true")
    p.add_argument("--skip-weather", action="store_true")
    a = p.parse_args()

    t0 = time.time()
    conn = get_connection()
    print(f"Database: {config.DB_PATH}\n")

    if not a.skip_stations:
        collect_stations.collect(conn)
        print()
    collect_actual_data.collect(conn, n_days=a.days, start=a.start, end=a.end, keep_raw=a.keep_raw)
    print()
    if not a.skip_weather:
        collect_weather.collect(conn, n=a.top_n)

    print("\nSummary:")
    for table in ("stations", "stops", "weather"):
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<10} {n:>12,} rows")
    print(f"Duration: {(time.time() - t0) / 60:.1f} minutes")
    conn.close()


if __name__ == "__main__":
    main()
