"""SQLite-Datenbank: Verbindung, Schema und Lade-Protokoll."""
import sqlite3
from datetime import datetime
from pathlib import Path

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS halte (
    betriebstag        TEXT,     -- YYYY-MM-DD
    fahrt_id           TEXT,     -- FAHRT_BEZEICHNER
    betreiber          TEXT,     -- BETREIBER_ABK (z.B. SBB, BLS, SOB)
    linie              TEXT,     -- LINIEN_TEXT (z.B. IC1, S12)
    zugtyp             TEXT,     -- VERKEHRSMITTEL_TEXT (z.B. IC, IR, S, RE)
    bpuic              INTEGER,  -- 7-stellige Haltestellennummer
    haltestelle        TEXT,
    ankunft_soll       TEXT,
    ankunft_ist        TEXT,
    an_status          TEXT,     -- REAL / ESTIMATED / FORECAST / UNKNOWN
    abfahrt_soll       TEXT,
    abfahrt_ist        TEXT,
    ab_status          TEXT,
    an_delay_min       REAL,     -- Ankunftsverspaetung in Minuten
    ab_delay_min       REAL,     -- Abfahrtsverspaetung in Minuten
    faellt_aus         INTEGER,  -- 1 = Halt faellt aus
    zusatzfahrt        INTEGER   -- 1 = Zusatzfahrt
);
CREATE INDEX IF NOT EXISTS idx_halte_bpuic ON halte(bpuic);
CREATE INDEX IF NOT EXISTS idx_halte_tag   ON halte(betriebstag);

CREATE TABLE IF NOT EXISTS stationen (
    bpuic      INTEGER PRIMARY KEY,
    name       TEXT,
    lat        REAL,
    lon        REAL,
    kanton     TEXT,
    gemeinde   TEXT,
    region     TEXT      -- Deutschschweiz / Romandie / Tessin / Unbekannt
);

CREATE TABLE IF NOT EXISTS wetter (
    bpuic          INTEGER,
    zeit           TEXT,     -- lokale Stunde 'YYYY-MM-DD HH:00'
    temperatur     REAL,     -- Grad C
    niederschlag   REAL,     -- mm in der Stunde
    schneefall     REAL,     -- cm in der Stunde
    wind           REAL,     -- km/h
    PRIMARY KEY (bpuic, zeit)
);

CREATE TABLE IF NOT EXISTS sammel_log (
    quelle      TEXT,
    schluessel  TEXT,
    zeilen_roh  INTEGER,
    zeilen_gespeichert INTEGER,
    zeitpunkt   TEXT,
    PRIMARY KEY (quelle, schluessel)
);
"""


def get_connection(path=None) -> sqlite3.Connection:
    path = Path(path or DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def already_loaded(conn, quelle: str, schluessel: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sammel_log WHERE quelle=? AND schluessel=?", (quelle, schluessel)
    )
    return cur.fetchone() is not None


def log_load(conn, quelle: str, schluessel: str, zeilen_roh: int, zeilen_gespeichert: int):
    conn.execute(
        "INSERT OR REPLACE INTO sammel_log VALUES (?,?,?,?,?)",
        (quelle, schluessel, int(zeilen_roh), int(zeilen_gespeichert),
         datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
