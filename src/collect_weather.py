"""Datenquelle 3: Stuendliches Wetter pro Bahnhof (Open-Meteo Historical Weather API).

Fuer die TOP_N_STATIONS meistfrequentierten Bahnhoefe werden stuendliche
Werte (Temperatur, Niederschlag, Schneefall, Wind) fuer den Zeitraum der
Ist-Daten abgefragt. Die API erlaubt mehrere Koordinaten pro Request.
"""
import time
from datetime import date, timedelta

import pandas as pd

from . import config
from .db import log_load
from .http_utils import get_json

QUELLE = "wetter"
VARIABLEN = ["temperature_2m", "precipitation", "snowfall", "wind_speed_10m"]
UMBENENNUNG = {"temperature_2m": "temperatur", "precipitation": "niederschlag",
               "snowfall": "schneefall", "wind_speed_10m": "wind"}


def top_stations(conn, n=config.TOP_N_STATIONS) -> pd.DataFrame:
    """Die n Bahnhoefe mit den meisten Zug-Ankuenften (mit Koordinaten)."""
    sql = """
        SELECT h.bpuic, s.name, s.lat, s.lon, COUNT(*) AS anzahl_halte
        FROM halte h
        JOIN stationen s ON s.bpuic = h.bpuic
        WHERE h.ankunft_soll IS NOT NULL
        GROUP BY h.bpuic
        ORDER BY anzahl_halte DESC
        LIMIT ?
    """
    return pd.read_sql(sql, conn, params=(n,))


def parse_response(payload, bpuics) -> pd.DataFrame:
    """Wandelt die API-Antwort (ein Objekt oder Liste von Objekten) in eine Tabelle."""
    if isinstance(payload, dict):
        payload = [payload]
    teile = []
    for bpuic, loc in zip(bpuics, payload):
        h = loc["hourly"]
        df = pd.DataFrame({"zeit": h["time"], **{UMBENENNUNG[v]: h.get(v) for v in VARIABLEN}})
        df["zeit"] = pd.to_datetime(df["zeit"]).dt.strftime("%Y-%m-%d %H:00")
        df.insert(0, "bpuic", int(bpuic))
        teile.append(df)
    out = pd.concat(teile, ignore_index=True)
    # Zeitumstellung (doppelte Stunde im Oktober) -> erste Messung behalten
    return out.drop_duplicates(["bpuic", "zeit"])


def collect(conn, n=config.TOP_N_STATIONS, batch=20):
    tage = pd.read_sql("SELECT MIN(betriebstag) AS von, MAX(betriebstag) AS bis FROM halte", conn)
    if tage["von"].isna().all():
        raise RuntimeError("Zuerst Ist-Daten laden (Tabelle 'halte' ist leer).")
    von = tage["von"].iloc[0]
    bis = (date.fromisoformat(tage["bis"].iloc[0]) + timedelta(days=1)).isoformat()  # Fahrten nach Mitternacht

    stationen = top_stations(conn, n)
    print(f"Wetter: {len(stationen)} Bahnhoefe, Zeitraum {von} bis {bis}")
    conn.execute("DELETE FROM wetter")
    gesamt = 0
    for i in range(0, len(stationen), batch):
        teil = stationen.iloc[i:i + batch]
        params = {
            "latitude": ",".join(f"{x:.5f}" for x in teil["lat"]),
            "longitude": ",".join(f"{x:.5f}" for x in teil["lon"]),
            "start_date": von, "end_date": bis,
            "hourly": ",".join(VARIABLEN),
            "timezone": "Europe/Zurich",
        }
        df = parse_response(get_json(config.OPEN_METEO_URL, params=params), teil["bpuic"])
        df.to_sql("wetter", conn, if_exists="append", index=False)
        gesamt += len(df)
        print(f"  Bahnhoefe {i + 1}-{i + len(teil)}: {len(df):,} Stundenwerte")
        time.sleep(1.5)  # API schonen
    conn.commit()
    log_load(conn, QUELLE, f"{von}_{bis}", gesamt, gesamt)
    return gesamt
