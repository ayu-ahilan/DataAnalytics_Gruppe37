"""Datenquelle 1: Ist-Daten des Schweizer OeV (opentransportdata.swiss).

Ablauf pro Betriebstag:
1. Download-URL ueber die CKAN-Web-API ermitteln
2. CSV (ca. 400-650 MB) herunterladen
3. In Chunks einlesen, nur Zugfahrten an Schweizer Haltestellen behalten
4. Verspaetungen berechnen und in SQLite (Tabelle 'halte') speichern
5. Rohdatei loeschen (Speicherplatz)
"""
import re
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from . import config
from .db import already_loaded, log_load
from .http_utils import ckan_resources, download, resource_url

QUELLE = "istdaten"
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})_istdaten\.csv", re.IGNORECASE)

BENOETIGTE_SPALTEN = [
    "BETRIEBSTAG", "FAHRT_BEZEICHNER", "BETREIBER_ABK", "PRODUKT_ID", "LINIEN_TEXT",
    "VERKEHRSMITTEL_TEXT", "ZUSATZFAHRT_TF", "FAELLT_AUS_TF", "BPUIC", "HALTESTELLEN_NAME",
    "ANKUNFTSZEIT", "AN_PROGNOSE", "AN_PROGNOSE_STATUS",
    "ABFAHRTSZEIT", "AB_PROGNOSE", "AB_PROGNOSE_STATUS", "DURCHFAHRT_TF",
]

STATUS_MAP = {
    "REAL": "REAL", "ESTIMATED": "ESTIMATED", "GESCHAETZT": "ESTIMATED",
    "FORECAST": "FORECAST", "PROGNOSE": "FORECAST", "": "FORECAST",
    "UNKNOWN": "UNKNOWN", "UNBEKANNT": "UNKNOWN",
}


# ---------------------------------------------------------------------------
# 1) Verfuegbare Tage ueber die Web-API abfragen
# ---------------------------------------------------------------------------
def list_available_days() -> dict:
    """{datum: download_url} aller aktuell publizierten Tagesdateien."""
    tage = {}
    for res in ckan_resources(config.ISTDATEN_PACKAGE):
        url = resource_url(res)
        m = DATE_RE.search(url) or DATE_RE.search(str(res.get("name", "")))
        if m and url:
            tage[date.fromisoformat(m.group(1))] = url
    return dict(sorted(tage.items()))


def choose_days(verfuegbar: dict, n_days=config.N_DAYS, min_age_days=config.MIN_AGE_DAYS,
                start=None, end=None) -> list:
    """Waehlt die zu ladenden Tage: entweder Zeitraum start-end oder die
    n_days juengsten Tage, die mindestens min_age_days alt sind."""
    tage = sorted(verfuegbar)
    if start or end:
        s = date.fromisoformat(str(start)) if start else date.min
        e = date.fromisoformat(str(end)) if end else date.max
        return [d for d in tage if s <= d <= e]
    grenze = date.today() - timedelta(days=min_age_days)
    return [d for d in tage if d <= grenze][-n_days:]


# ---------------------------------------------------------------------------
# 2) Aufbereitung einer Tagesdatei
# ---------------------------------------------------------------------------
def _detect_sep(path: Path) -> str:
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        kopf = f.readline()
    return ";" if kopf.count(";") > kopf.count(",") else ","


def normalize_bpuic(s: pd.Series) -> pd.Series:
    """BPUIC kann 7-stellig, 9-stellig (mit Kante) oder eine SLOID sein -> 7-stellige Zahl."""
    s = s.astype("string").str.strip()
    out = pd.Series(np.nan, index=s.index, dtype="float64")

    sloid = s.str.extract(r"sloid:(\d+)", expand=False)
    ist_sloid = sloid.notna()
    out[ist_sloid] = 8_500_000 + pd.to_numeric(sloid[ist_sloid], errors="coerce")

    ziffern = s.where(~ist_sloid).str.fullmatch(r"\d{7,9}").fillna(False).astype(bool)
    out[ziffern] = pd.to_numeric(s[ziffern].str[:7], errors="coerce")
    return out


def _to_dt(s: pd.Series) -> pd.Series:
    s = s.astype("string").str.strip()
    mit_sek = pd.to_datetime(s, format="%d.%m.%Y %H:%M:%S", errors="coerce")
    ohne_sek = pd.to_datetime(s, format="%d.%m.%Y %H:%M", errors="coerce")
    return mit_sek.fillna(ohne_sek)


def _bool(s: pd.Series) -> pd.Series:
    return s.astype("string").str.strip().str.lower().isin(["true", "1", "ja", "yes"])


def _fmt(s: pd.Series) -> pd.Series:
    return s.dt.strftime("%Y-%m-%d %H:%M:%S").astype(object).where(s.notna(), None)


def transform_chunk(df: pd.DataFrame) -> pd.DataFrame:
    """Filtert Zugfahrten an Schweizer Haltestellen und berechnet Verspaetungen."""
    df.columns = [c.strip().upper() for c in df.columns]
    fehlend = [c for c in BENOETIGTE_SPALTEN if c not in df.columns]
    if fehlend:
        raise ValueError(f"Spalten fehlen in der Ist-Daten-Datei: {fehlend}. "
                         f"Vorhanden: {list(df.columns)}")

    produkt = df["PRODUKT_ID"].astype("string").str.strip().str.lower()
    df = df[produkt.isin(["zug", "train"]) & ~_bool(df["DURCHFAHRT_TF"])].copy()

    df["bpuic"] = normalize_bpuic(df["BPUIC"])
    df = df[(df["bpuic"] >= 8_500_000) & (df["bpuic"] < 8_600_000)]  # nur Schweiz

    an_soll, an_ist = _to_dt(df["ANKUNFTSZEIT"]), _to_dt(df["AN_PROGNOSE"])
    ab_soll, ab_ist = _to_dt(df["ABFAHRTSZEIT"]), _to_dt(df["AB_PROGNOSE"])

    def status(col):
        return (df[col].astype("string").fillna("").str.strip().str.upper()
                .map(STATUS_MAP).fillna("UNKNOWN"))

    out = pd.DataFrame({
        "betriebstag": pd.to_datetime(df["BETRIEBSTAG"].astype("string").str.strip(),
                                      format="%d.%m.%Y", errors="coerce").dt.strftime("%Y-%m-%d"),
        "fahrt_id": df["FAHRT_BEZEICHNER"].astype("string"),
        "betreiber": df["BETREIBER_ABK"].astype("string").str.strip(),
        "linie": df["LINIEN_TEXT"].astype("string").str.strip(),
        "zugtyp": df["VERKEHRSMITTEL_TEXT"].astype("string").str.strip(),
        "bpuic": df["bpuic"].astype("int64"),
        "haltestelle": df["HALTESTELLEN_NAME"].astype("string").str.strip(),
        "ankunft_soll": _fmt(an_soll), "ankunft_ist": _fmt(an_ist), "an_status": status("AN_PROGNOSE_STATUS"),
        "abfahrt_soll": _fmt(ab_soll), "abfahrt_ist": _fmt(ab_ist), "ab_status": status("AB_PROGNOSE_STATUS"),
        "an_delay_min": ((an_ist - an_soll).dt.total_seconds() / 60).round(2),
        "ab_delay_min": ((ab_ist - ab_soll).dt.total_seconds() / 60).round(2),
        "faellt_aus": _bool(df["FAELLT_AUS_TF"]).astype(int),
        "zusatzfahrt": _bool(df["ZUSATZFAHRT_TF"]).astype(int),
    })
    # pandas-'string'-Typen in normale Objekte umwandeln (sqlite3-kompatibel)
    for c in out.columns:
        if str(out[c].dtype) in ("string", "str"):
            out[c] = out[c].astype(object).where(out[c].notna(), None)
    return out


def process_file(path: Path, conn, chunksize=config.CHUNK_SIZE) -> tuple:
    """Liest eine Tagesdatei in Chunks und speichert die Zug-Halte in SQLite."""
    sep = _detect_sep(path)
    zeilen_roh = zeilen_gespeichert = 0
    for chunk in pd.read_csv(path, sep=sep, dtype=str, chunksize=chunksize,
                             encoding="utf-8-sig", keep_default_na=False, na_values=[""],
                             low_memory=False):
        zeilen_roh += len(chunk)
        out = transform_chunk(chunk)
        if len(out):
            out.to_sql("halte", conn, if_exists="append", index=False)
            zeilen_gespeichert += len(out)
    conn.commit()
    return zeilen_roh, zeilen_gespeichert


# ---------------------------------------------------------------------------
# 3) Gesamter Ablauf
# ---------------------------------------------------------------------------
def collect(conn, n_days=config.N_DAYS, start=None, end=None, keep_raw=False):
    print("Ist-Daten: verfuegbare Tage ueber CKAN-API abfragen ...")
    verfuegbar = list_available_days()
    if not verfuegbar:
        raise RuntimeError("Keine Ist-Daten-Dateien gefunden.")
    print(f"  {len(verfuegbar)} Tage verfuegbar: {min(verfuegbar)} bis {max(verfuegbar)}")
    tage = choose_days(verfuegbar, n_days=n_days, start=start, end=end)
    print(f"  ausgewaehlt: {len(tage)} Tage ({tage[0]} bis {tage[-1]})" if tage else "  keine Tage ausgewaehlt")

    for tag in tage:
        key = tag.isoformat()
        if already_loaded(conn, QUELLE, key):
            print(f"[{key}] bereits geladen - uebersprungen")
            continue
        print(f"[{key}] Download ...")
        datei = config.RAW_DIR / f"{key}_istdaten.csv"
        if not datei.exists():
            download(verfuegbar[tag], datei)
        conn.execute("DELETE FROM halte WHERE betriebstag = ?", (key,))  # falls Abbruch
        roh, gespeichert = process_file(datei, conn)
        log_load(conn, QUELLE, key, roh, gespeichert)
        print(f"[{key}] {roh:,} Zeilen gelesen, {gespeichert:,} Zug-Halte gespeichert")
        if not keep_raw:
            datei.unlink(missing_ok=True)
    return tage
