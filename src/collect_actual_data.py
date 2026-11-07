"""Data source 1: actual data of Swiss public transport (opentransportdata.swiss).

Steps per operating day:
1. Determine the download URL via the CKAN web API
2. Download the CSV (approx. 400-650 MB)
3. Read it in chunks, keep only train trips at Swiss stations
4. Compute delays and store them in SQLite (table 'stops')
5. Delete the raw file (disk space)
"""
import re
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from . import config
from .db import already_loaded, log_load
from .http_utils import ckan_resources, download, resource_url

SOURCE = "actual_data"
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})_istdaten\.csv", re.IGNORECASE)

# Column names of the source file (defined by the data provider, therefore in German)
REQUIRED_COLUMNS = [
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
# 1) Query the available days via the web API
# ---------------------------------------------------------------------------
def list_available_days() -> dict:
    """{date: download_url} of all currently published daily files."""
    days = {}
    for res in ckan_resources(config.ACTUAL_DATA_PACKAGE):
        url = resource_url(res)
        m = DATE_RE.search(url) or DATE_RE.search(str(res.get("name", "")))
        if m and url:
            days[date.fromisoformat(m.group(1))] = url
    return dict(sorted(days.items()))


def choose_days(available: dict, n_days=config.N_DAYS, min_age_days=config.MIN_AGE_DAYS,
                start=None, end=None) -> list:
    """Chooses the days to load: either the period start-end or the
    n_days most recent days that are at least min_age_days old."""
    days = sorted(available)
    if start or end:
        s = date.fromisoformat(str(start)) if start else date.min
        e = date.fromisoformat(str(end)) if end else date.max
        return [d for d in days if s <= d <= e]
    cutoff = date.today() - timedelta(days=min_age_days)
    return [d for d in days if d <= cutoff][-n_days:]


# ---------------------------------------------------------------------------
# 2) Processing of one daily file
# ---------------------------------------------------------------------------
def _detect_sep(path: Path) -> str:
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        header = f.readline()
    return ";" if header.count(";") > header.count(",") else ","


def normalize_bpuic(s: pd.Series) -> pd.Series:
    """BPUIC can have 7 digits, 9 digits (with platform) or be an SLOID -> 7-digit number."""
    s = s.astype("string").str.strip()
    out = pd.Series(np.nan, index=s.index, dtype="float64")

    sloid = s.str.extract(r"sloid:(\d+)", expand=False)
    is_sloid = sloid.notna()
    out[is_sloid] = 8_500_000 + pd.to_numeric(sloid[is_sloid], errors="coerce")

    digits = s.where(~is_sloid).str.fullmatch(r"\d{7,9}").fillna(False).astype(bool)
    out[digits] = pd.to_numeric(s[digits].str[:7], errors="coerce")
    return out


def _to_dt(s: pd.Series) -> pd.Series:
    s = s.astype("string").str.strip()
    with_sec = pd.to_datetime(s, format="%d.%m.%Y %H:%M:%S", errors="coerce")
    without_sec = pd.to_datetime(s, format="%d.%m.%Y %H:%M", errors="coerce")
    return with_sec.fillna(without_sec)


def _bool(s: pd.Series) -> pd.Series:
    return s.astype("string").str.strip().str.lower().isin(["true", "1", "ja", "yes"])


def _fmt(s: pd.Series) -> pd.Series:
    return s.dt.strftime("%Y-%m-%d %H:%M:%S").astype(object).where(s.notna(), None)


def transform_chunk(df: pd.DataFrame) -> pd.DataFrame:
    """Filters train trips at Swiss stations and computes delays."""
    df.columns = [c.strip().upper() for c in df.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Columns missing in the actual data file: {missing}. "
                         f"Available: {list(df.columns)}")

    product = df["PRODUKT_ID"].astype("string").str.strip().str.lower()
    df = df[product.isin(["zug", "train"]) & ~_bool(df["DURCHFAHRT_TF"])].copy()

    df["bpuic"] = normalize_bpuic(df["BPUIC"])
    df = df[(df["bpuic"] >= 8_500_000) & (df["bpuic"] < 8_600_000)]  # Switzerland only

    arr_sched, arr_act = _to_dt(df["ANKUNFTSZEIT"]), _to_dt(df["AN_PROGNOSE"])
    dep_sched, dep_act = _to_dt(df["ABFAHRTSZEIT"]), _to_dt(df["AB_PROGNOSE"])

    def status(col):
        return (df[col].astype("string").fillna("").str.strip().str.upper()
                .map(STATUS_MAP).fillna("UNKNOWN"))

    out = pd.DataFrame({
        "operating_day": pd.to_datetime(df["BETRIEBSTAG"].astype("string").str.strip(),
                                        format="%d.%m.%Y", errors="coerce").dt.strftime("%Y-%m-%d"),
        "trip_id": df["FAHRT_BEZEICHNER"].astype("string"),
        "operator": df["BETREIBER_ABK"].astype("string").str.strip(),
        "line": df["LINIEN_TEXT"].astype("string").str.strip(),
        "train_type": df["VERKEHRSMITTEL_TEXT"].astype("string").str.strip(),
        "bpuic": df["bpuic"].astype("int64"),
        "stop_name": df["HALTESTELLEN_NAME"].astype("string").str.strip(),
        "arr_scheduled": _fmt(arr_sched), "arr_actual": _fmt(arr_act), "arr_status": status("AN_PROGNOSE_STATUS"),
        "dep_scheduled": _fmt(dep_sched), "dep_actual": _fmt(dep_act), "dep_status": status("AB_PROGNOSE_STATUS"),
        "arr_delay_min": ((arr_act - arr_sched).dt.total_seconds() / 60).round(2),
        "dep_delay_min": ((dep_act - dep_sched).dt.total_seconds() / 60).round(2),
        "cancelled": _bool(df["FAELLT_AUS_TF"]).astype(int),
        "extra_trip": _bool(df["ZUSATZFAHRT_TF"]).astype(int),
    })
    # convert pandas 'string' dtypes to plain objects (sqlite3-compatible)
    for c in out.columns:
        if str(out[c].dtype) in ("string", "str"):
            out[c] = out[c].astype(object).where(out[c].notna(), None)
    return out


def process_file(path: Path, conn, chunksize=config.CHUNK_SIZE) -> tuple:
    """Reads one daily file in chunks and stores the train stops in SQLite."""
    sep = _detect_sep(path)
    rows_raw = rows_saved = 0
    for chunk in pd.read_csv(path, sep=sep, dtype=str, chunksize=chunksize,
                             encoding="utf-8-sig", keep_default_na=False, na_values=[""],
                             low_memory=False):
        rows_raw += len(chunk)
        out = transform_chunk(chunk)
        if len(out):
            out.to_sql("stops", conn, if_exists="append", index=False)
            rows_saved += len(out)
    conn.commit()
    return rows_raw, rows_saved


# ---------------------------------------------------------------------------
# 3) Complete workflow
# ---------------------------------------------------------------------------
def collect(conn, n_days=config.N_DAYS, start=None, end=None, keep_raw=False):
    print("Actual data: querying available days via the CKAN API ...")
    available = list_available_days()
    if not available:
        raise RuntimeError("No actual data files found.")
    print(f"  {len(available)} days available: {min(available)} to {max(available)}")
    days = choose_days(available, n_days=n_days, start=start, end=end)
    print(f"  selected: {len(days)} days ({days[0]} to {days[-1]})" if days else "  no days selected")

    for day in days:
        key = day.isoformat()
        if already_loaded(conn, SOURCE, key):
            print(f"[{key}] already loaded - skipped")
            continue
        print(f"[{key}] downloading ...")
        file = config.RAW_DIR / f"{key}_istdaten.csv"
        if not file.exists():
            download(available[day], file)
        conn.execute("DELETE FROM stops WHERE operating_day = ?", (key,))  # in case of an earlier abort
        raw, saved = process_file(file, conn)
        log_load(conn, SOURCE, key, raw, saved)
        print(f"[{key}] {raw:,} rows read, {saved:,} train stops saved")
        if not keep_raw:
            file.unlink(missing_ok=True)
    return days
