"""Datensammlung starten (im Terminal im Projektordner ausfuehren):

    python run_collection.py               # Standard: 14 Tage, Top-100-Bahnhoefe
    python run_collection.py --days 7      # weniger Tage (schneller)
    python run_collection.py --start 2026-10-05 --end 2026-10-18

Das Skript kann jederzeit abgebrochen und erneut gestartet werden:
bereits geladene Tage werden uebersprungen.
"""
import argparse
import time

from src import collect_istdaten, collect_stations, collect_weather, config
from src.db import get_connection


def main():
    p = argparse.ArgumentParser(description="Datensammlung Gruppe 37")
    p.add_argument("--days", type=int, default=config.N_DAYS)
    p.add_argument("--start", default=None, help="YYYY-MM-DD")
    p.add_argument("--end", default=None, help="YYYY-MM-DD")
    p.add_argument("--top-n", type=int, default=config.TOP_N_STATIONS)
    p.add_argument("--keep-raw", action="store_true", help="Rohdateien nicht loeschen")
    p.add_argument("--skip-stations", action="store_true")
    p.add_argument("--skip-weather", action="store_true")
    a = p.parse_args()

    t0 = time.time()
    conn = get_connection()
    print(f"Datenbank: {config.DB_PATH}\n")

    if not a.skip_stations:
        collect_stations.collect(conn)
        print()
    collect_istdaten.collect(conn, n_days=a.days, start=a.start, end=a.end, keep_raw=a.keep_raw)
    print()
    if not a.skip_weather:
        collect_weather.collect(conn, n=a.top_n)

    print("\nZusammenfassung:")
    for tabelle in ("stationen", "halte", "wetter"):
        n = conn.execute(f"SELECT COUNT(*) FROM {tabelle}").fetchone()[0]
        print(f"  {tabelle:<10} {n:>12,} Zeilen")
    print(f"Dauer: {(time.time() - t0) / 60:.1f} Minuten")
    conn.close()


if __name__ == "__main__":
    main()
