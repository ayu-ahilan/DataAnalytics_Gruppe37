"""Central project configuration (Group 37, Data Analytics HS2026).

All paths and parameters in one place, so that scripts and notebooks
use the same settings.
"""
from pathlib import Path
import os

# --- Paths ---------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("DA37_DATA_DIR", PROJECT_ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"
DB_PATH = Path(os.environ.get("DA37_DB_PATH", DATA_DIR / "train_delays.sqlite"))
OUTPUT_DIR = Path(os.environ.get("DA37_OUTPUT_DIR", PROJECT_ROOT / "outputs"))

# --- Web APIs ------------------------------------------------------------------
# CKAN API of the Swiss open data platform for mobility (fallback: opendata.swiss)
CKAN_BASES = [
    "https://data.opentransportdata.swiss/api/3/action",
    "https://ckan.opendata.swiss/api/3/action",
]
ACTUAL_DATA_PACKAGE = "ist-daten-v2"                    # daily actual data of all public transport trips
SERVICEPOINT_PACKAGES = ["service-point-v2", "dienststellen-heute"]  # stations incl. coordinates
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"   # historical weather
USER_AGENT = "ZHAW-DataAnalytics-Group37 (student project)"

# --- Scope of the data collection ----------------------------------------------
N_DAYS = 14            # number of operating days (approx. 400-650 MB raw data each, deleted after filtering)
MIN_AGE_DAYS = 6       # weather data (ERA5) is published with a delay of approx. 5 days
TOP_N_STATIONS = 100   # analysis restricted to the 100 busiest stations (weather per station)
CHUNK_SIZE = 500_000   # rows per chunk when reading the large CSV files

# --- Domain definitions ---------------------------------------------------------
LATE_THRESHOLD_MIN = 3.0   # SBB definition: a train counts as late from 3 minutes of delay
PEAK_HOURS = set(range(6, 9)) | set(range(16, 19))   # peak hours 06:00-08:59 and 16:00-18:59
RANDOM_STATE = 37
