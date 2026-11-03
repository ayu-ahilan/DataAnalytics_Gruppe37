"""Datenquelle 2: Haltestellen-Stammdaten (Service Points, atlas/SBB).

Liefert pro Haltestelle Koordinaten (WGS84), Kanton und Gemeinde.
Daraus wird die Sprachregion abgeleitet (siehe regions.py).
"""
import io
import zipfile
from pathlib import Path

import pandas as pd

from . import config
from .db import log_load
from .http_utils import ckan_resources, download, resource_url
from .regions import assign_region, kanton_abk

QUELLE = "stationen"

# Moegliche Spaltennamen (die Exporte haben sich ueber die Jahre veraendert)
KANDIDATEN = {
    "bpuic": ["number", "servicepointnumber", "bpuic", "didok", "uic"],
    "name": ["designationofficial", "designation", "name", "bezeichnung"],
    "lat": ["wgs84north", "geolocation_wgs84north", "lat", "latitude", "y_wgs84"],
    "lon": ["wgs84east", "geolocation_wgs84east", "lon", "lng", "longitude", "x_wgs84"],
    "kanton": ["cantonabbreviation", "cantonabbr", "canton", "cantonname", "kanton"],
    "gemeinde": ["municipalityname", "municipality", "gemeinde", "localityname"],
}


def _find_col(cols, kandidaten):
    norm = {c.lower().replace("_", "").replace(".", ""): c for c in cols}
    for k in kandidaten:
        k2 = k.replace("_", "")
        if k2 in norm:
            return norm[k2]
    return None


def _choose_resource():
    for paket in config.SERVICEPOINT_PACKAGES:
        try:
            res = ckan_resources(paket)
        except RuntimeError:
            continue
        urls = [resource_url(r) for r in res]
        for muster in ("actual-date-swiss-service-point", "swiss", "actual_date", "actual-date"):
            treffer = [u for u in urls if muster in u.lower() and u.lower().endswith((".csv", ".zip"))]
            if treffer:
                return treffer[0]
    raise RuntimeError("Keine Service-Point-CSV gefunden.")


def read_service_points(path: Path) -> pd.DataFrame:
    if str(path).lower().endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
            raw = z.read(name).decode("utf-8-sig", errors="replace")
    else:
        raw = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    kopf = raw.split("\n", 1)[0]
    sep = ";" if kopf.count(";") > kopf.count(",") else ","
    return pd.read_csv(io.StringIO(raw), sep=sep, dtype=str, low_memory=False)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    spalten = {k: _find_col(df.columns, v) for k, v in KANDIDATEN.items()}
    fehlend = [k for k in ("bpuic", "lat", "lon") if spalten[k] is None]
    if fehlend:
        raise ValueError(f"Spalten {fehlend} nicht gefunden. Vorhanden: {list(df.columns)}")

    out = pd.DataFrame({
        "bpuic": pd.to_numeric(df[spalten["bpuic"]].str.strip().str[:7], errors="coerce"),
        "name": df[spalten["name"]] if spalten["name"] else None,
        "lat": pd.to_numeric(df[spalten["lat"]], errors="coerce"),
        "lon": pd.to_numeric(df[spalten["lon"]], errors="coerce"),
        "kanton": df[spalten["kanton"]].map(kanton_abk) if spalten["kanton"] else "",
        "gemeinde": df[spalten["gemeinde"]] if spalten["gemeinde"] else None,
    })
    # Kurznummern (z.B. 3000) zu 7-stelligen Nummern (8503000) ergaenzen
    kurz = out["bpuic"] < 100_000
    out.loc[kurz, "bpuic"] = 8_500_000 + out.loc[kurz, "bpuic"]
    out = out[(out["bpuic"] >= 8_500_000) & (out["bpuic"] < 8_600_000)]
    out = out.dropna(subset=["lat", "lon"]).drop_duplicates("bpuic")
    out["bpuic"] = out["bpuic"].astype("int64")
    out["region"] = [assign_region(k, g) for k, g in zip(out["kanton"], out["gemeinde"])]
    return out.reset_index(drop=True)


def save(df: pd.DataFrame, conn):
    conn.execute("DELETE FROM stationen")
    df.astype(object).where(df.notna(), None).to_sql("stationen", conn, if_exists="append", index=False)
    conn.commit()


def collect(conn):
    print("Stationen: Service-Point-Datei ueber CKAN-API suchen ...")
    url = _choose_resource()
    datei = config.RAW_DIR / Path(url.split("?")[0]).name
    download(url, datei)
    roh = read_service_points(datei)
    df = transform(roh)
    save(df, conn)
    log_load(conn, QUELLE, "aktuell", len(roh), len(df))
    print(f"  {len(roh):,} Service Points gelesen, {len(df):,} Schweizer Haltestellen mit Koordinaten gespeichert")
    print(df["region"].value_counts().to_string())
    return df
