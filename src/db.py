"""SQLite database: connection, schema and load log."""
import sqlite3
from datetime import datetime
from pathlib import Path

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS stops (
    operating_day      TEXT,     -- YYYY-MM-DD
    trip_id            TEXT,     -- FAHRT_BEZEICHNER
    operator           TEXT,     -- BETREIBER_ABK (e.g. SBB, BLS, SOB)
    line               TEXT,     -- LINIEN_TEXT (e.g. IC1, S12)
    train_type         TEXT,     -- VERKEHRSMITTEL_TEXT (e.g. IC, IR, S, RE)
    bpuic              INTEGER,  -- 7-digit station number
    stop_name          TEXT,
    arr_scheduled      TEXT,
    arr_actual         TEXT,
    arr_status         TEXT,     -- REAL / ESTIMATED / FORECAST / UNKNOWN
    dep_scheduled      TEXT,
    dep_actual         TEXT,
    dep_status         TEXT,
    arr_delay_min      REAL,     -- arrival delay in minutes
    dep_delay_min      REAL,     -- departure delay in minutes
    cancelled          INTEGER,  -- 1 = stop cancelled
    extra_trip         INTEGER   -- 1 = additional trip
);
CREATE INDEX IF NOT EXISTS idx_stops_bpuic ON stops(bpuic);
CREATE INDEX IF NOT EXISTS idx_stops_day   ON stops(operating_day);

CREATE TABLE IF NOT EXISTS stations (
    bpuic         INTEGER PRIMARY KEY,
    name          TEXT,
    lat           REAL,
    lon           REAL,
    canton        TEXT,
    municipality  TEXT,
    region        TEXT      -- German-speaking / Romandy / Ticino / Unknown
);

CREATE TABLE IF NOT EXISTS weather (
    bpuic          INTEGER,
    time           TEXT,     -- local hour 'YYYY-MM-DD HH:00'
    temperature    REAL,     -- degrees C
    precipitation  REAL,     -- mm in the hour
    snowfall       REAL,     -- cm in the hour
    wind           REAL,     -- km/h
    PRIMARY KEY (bpuic, time)
);

CREATE TABLE IF NOT EXISTS load_log (
    source      TEXT,
    key         TEXT,
    rows_raw    INTEGER,
    rows_saved  INTEGER,
    loaded_at   TEXT,
    PRIMARY KEY (source, key)
);
"""


def get_connection(path=None) -> sqlite3.Connection:
    path = Path(path or DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def already_loaded(conn, source: str, key: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM load_log WHERE source=? AND key=?", (source, key)
    )
    return cur.fetchone() is not None


def log_load(conn, source: str, key: str, rows_raw: int, rows_saved: int):
    conn.execute(
        "INSERT OR REPLACE INTO load_log VALUES (?,?,?,?,?)",
        (source, key, int(rows_raw), int(rows_saved),
         datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
