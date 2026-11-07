"""Data source 2: station master data (service points, atlas/SBB).

Provides coordinates (WGS84), canton and municipality for every station.
The language region is derived from these (see regions.py).
"""
import io
import zipfile
from pathlib import Path

import pandas as pd

from . import config
from .db import log_load
from .http_utils import ckan_resources, download, resource_url
from .regions import assign_region, canton_abbr

SOURCE = "stations"

# Possible column names (the exports have changed over the years)
CANDIDATES = {
    "bpuic": ["number", "servicepointnumber", "bpuic", "didok", "uic"],
    "name": ["designationofficial", "designation", "name", "bezeichnung"],
    "lat": ["wgs84north", "geolocation_wgs84north", "lat", "latitude", "y_wgs84"],
    "lon": ["wgs84east", "geolocation_wgs84east", "lon", "lng", "longitude", "x_wgs84"],
    "canton": ["cantonabbreviation", "cantonabbr", "canton", "cantonname", "kanton"],
    "municipality": ["municipalityname", "municipality", "gemeinde", "localityname"],
}


def _find_col(cols, candidates):
    norm = {c.lower().replace("_", "").replace(".", ""): c for c in cols}
    for k in candidates:
        k2 = k.replace("_", "")
        if k2 in norm:
            return norm[k2]
    return None


def _choose_resource():
    for package in config.SERVICEPOINT_PACKAGES:
        try:
            res = ckan_resources(package)
        except RuntimeError:
            continue
        urls = [resource_url(r) for r in res]
        for pattern in ("actual-date-swiss-service-point", "swiss", "actual_date", "actual-date"):
            hits = [u for u in urls if pattern in u.lower() and u.lower().endswith((".csv", ".zip"))]
            if hits:
                return hits[0]
    raise RuntimeError("No service point CSV found.")


def read_service_points(path: Path) -> pd.DataFrame:
    if str(path).lower().endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
            raw = z.read(name).decode("utf-8-sig", errors="replace")
    else:
        raw = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    header = raw.split("\n", 1)[0]
    sep = ";" if header.count(";") > header.count(",") else ","
    return pd.read_csv(io.StringIO(raw), sep=sep, dtype=str, low_memory=False)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    cols = {k: _find_col(df.columns, v) for k, v in CANDIDATES.items()}
    missing = [k for k in ("bpuic", "lat", "lon") if cols[k] is None]
    if missing:
        raise ValueError(f"Columns {missing} not found. Available: {list(df.columns)}")

    out = pd.DataFrame({
        "bpuic": pd.to_numeric(df[cols["bpuic"]].str.strip().str[:7], errors="coerce"),
        "name": df[cols["name"]] if cols["name"] else None,
        "lat": pd.to_numeric(df[cols["lat"]], errors="coerce"),
        "lon": pd.to_numeric(df[cols["lon"]], errors="coerce"),
        "canton": df[cols["canton"]].map(canton_abbr) if cols["canton"] else "",
        "municipality": df[cols["municipality"]] if cols["municipality"] else None,
    })
    # complete short numbers (e.g. 3000) to 7-digit numbers (8503000)
    short = out["bpuic"] < 100_000
    out.loc[short, "bpuic"] = 8_500_000 + out.loc[short, "bpuic"]
    out = out[(out["bpuic"] >= 8_500_000) & (out["bpuic"] < 8_600_000)]
    out = out.dropna(subset=["lat", "lon"]).drop_duplicates("bpuic")
    out["bpuic"] = out["bpuic"].astype("int64")
    out["region"] = [assign_region(k, g) for k, g in zip(out["canton"], out["municipality"])]
    return out.reset_index(drop=True)


def save(df: pd.DataFrame, conn):
    conn.execute("DELETE FROM stations")
    df.astype(object).where(df.notna(), None).to_sql("stations", conn, if_exists="append", index=False)
    conn.commit()


def collect(conn):
    print("Stations: searching the service point file via the CKAN API ...")
    url = _choose_resource()
    file = config.RAW_DIR / Path(url.split("?")[0]).name
    download(url, file)
    raw = read_service_points(file)
    df = transform(raw)
    save(df, conn)
    log_load(conn, SOURCE, "current", len(raw), len(df))
    print(f"  {len(raw):,} service points read, {len(df):,} Swiss stations with coordinates saved")
    print(df["region"].value_counts().to_string())
    return df
