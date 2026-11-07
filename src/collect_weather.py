"""Data source 3: hourly weather per station (Open-Meteo Historical Weather API).

For the TOP_N_STATIONS busiest stations, hourly values (temperature,
precipitation, snowfall, wind) are queried for the period of the actual
data. The API accepts several coordinates per request.
"""
import time
from datetime import date, timedelta

import pandas as pd

from . import config
from .db import log_load
from .http_utils import get_json

SOURCE = "weather"
VARIABLES = ["temperature_2m", "precipitation", "snowfall", "wind_speed_10m"]
RENAME = {"temperature_2m": "temperature", "precipitation": "precipitation",
          "snowfall": "snowfall", "wind_speed_10m": "wind"}


def top_stations(conn, n=config.TOP_N_STATIONS) -> pd.DataFrame:
    """The n stations with the most train arrivals (with coordinates)."""
    sql = """
        SELECT s.bpuic, s.name, s.lat, s.lon, COUNT(*) AS n_stops
        FROM stops t
        JOIN stations s ON s.bpuic = t.bpuic
        WHERE t.arr_scheduled IS NOT NULL
        GROUP BY s.bpuic
        ORDER BY n_stops DESC
        LIMIT ?
    """
    return pd.read_sql(sql, conn, params=(n,))


def parse_response(payload, bpuics) -> pd.DataFrame:
    """Converts the API response (one object or a list of objects) into a table."""
    if isinstance(payload, dict):
        payload = [payload]
    parts = []
    for bpuic, loc in zip(bpuics, payload):
        h = loc["hourly"]
        df = pd.DataFrame({"time": h["time"], **{RENAME[v]: h.get(v) for v in VARIABLES}})
        df["time"] = pd.to_datetime(df["time"]).dt.strftime("%Y-%m-%d %H:00")
        df.insert(0, "bpuic", int(bpuic))
        parts.append(df)
    out = pd.concat(parts, ignore_index=True)
    # daylight saving time change (duplicate hour in October) -> keep the first value
    return out.drop_duplicates(["bpuic", "time"])


def collect(conn, n=config.TOP_N_STATIONS, batch=20):
    days = pd.read_sql("SELECT MIN(operating_day) AS first, MAX(operating_day) AS last FROM stops", conn)
    if days["first"].isna().all():
        raise RuntimeError("Load the actual data first (table 'stops' is empty).")
    first = days["first"].iloc[0]
    last = (date.fromisoformat(days["last"].iloc[0]) + timedelta(days=1)).isoformat()  # trips after midnight

    stations = top_stations(conn, n)
    print(f"Weather: {len(stations)} stations, period {first} to {last}")
    conn.execute("DELETE FROM weather")
    total = 0
    for i in range(0, len(stations), batch):
        part = stations.iloc[i:i + batch]
        params = {
            "latitude": ",".join(f"{x:.5f}" for x in part["lat"]),
            "longitude": ",".join(f"{x:.5f}" for x in part["lon"]),
            "start_date": first, "end_date": last,
            "hourly": ",".join(VARIABLES),
            "timezone": "Europe/Zurich",
        }
        df = parse_response(get_json(config.OPEN_METEO_URL, params=params), part["bpuic"])
        df.to_sql("weather", conn, if_exists="append", index=False)
        total += len(df)
        print(f"  stations {i + 1}-{i + len(part)}: {len(df):,} hourly values")
        time.sleep(1.5)  # be gentle with the API
    conn.commit()
    log_load(conn, SOURCE, f"{first}_{last}", total, total)
    return total
