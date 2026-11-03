"""Zentrale Konfiguration des Projekts (Gruppe 37, Data Analytics HS2026).

Alle Pfade und Parameter an einem Ort, damit Skripte und Notebooks
dieselben Einstellungen verwenden.
"""
from pathlib import Path
import os

# --- Pfade -------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("DA37_DATA_DIR", PROJECT_ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"
DB_PATH = Path(os.environ.get("DA37_DB_PATH", DATA_DIR / "zugverspaetung.sqlite"))
OUTPUT_DIR = Path(os.environ.get("DA37_OUTPUT_DIR", PROJECT_ROOT / "outputs"))

# --- Web-APIs ----------------------------------------------------------------
# CKAN-API der Open-Data-Plattform Mobilitaet Schweiz (Fallback: opendata.swiss)
CKAN_BASES = [
    "https://data.opentransportdata.swiss/api/3/action",
    "https://ckan.opendata.swiss/api/3/action",
]
ISTDATEN_PACKAGE = "ist-daten-v2"                       # taegliche Ist-Daten aller OeV-Fahrten
SERVICEPOINT_PACKAGES = ["service-point-v2", "dienststellen-heute"]  # Haltestellen inkl. Koordinaten
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"   # historisches Wetter
USER_AGENT = "ZHAW-DataAnalytics-Gruppe37 (Studierendenprojekt)"

# --- Umfang der Datensammlung -------------------------------------------------
N_DAYS = 14            # Anzahl Betriebstage (je ca. 400-650 MB Rohdaten, werden nach dem Filtern geloescht)
MIN_AGE_DAYS = 6       # Wetterdaten (ERA5) haben ca. 5 Tage Verzoegerung
TOP_N_STATIONS = 100   # Analyse auf die 100 meistfrequentierten Bahnhoefe (Wetter pro Bahnhof)
CHUNK_SIZE = 500_000   # Zeilen pro Chunk beim Einlesen der grossen CSV-Dateien

# --- Fachliche Definitionen ----------------------------------------------------
LATE_THRESHOLD_MIN = 3.0   # SBB-Definition: ab 3 Minuten Verspaetung gilt ein Zug als unpuenktlich
PEAK_HOURS = set(range(6, 9)) | set(range(16, 19))   # Stosszeiten 06:00-08:59 und 16:00-18:59
RANDOM_STATE = 37
