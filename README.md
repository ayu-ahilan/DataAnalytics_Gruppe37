# When and where are trains late?
**Train delays in Switzerland compared across language regions and times of day**

Data Analytics HS2026 (ZHAW), **Group 37**: Marc Stump, Ayushan Ahilan

## Research question
Which factors influence whether a train arrives **≥ 3 minutes late** (SBB definition), and do these factors differ between **German-speaking Switzerland and Romandy** and between **peak and off-peak hours**?

## Data sources (all collected by ourselves via web APIs)
| # | Source | Access | Join |
|---|---|---|---|
| 1 | Actual data v2 (“Ist-Daten”, opentransportdata.swiss) | CKAN API `package_show` → daily CSV | — |
| 2 | Service points / atlas (opentransportdata.swiss) | CKAN API → CSV | via `bpuic` (station number) |
| 3 | Open-Meteo Historical Weather API | REST API (JSON) | via `bpuic` + hour of the scheduled arrival |

Collected period: 14–27 October 2026, 13 operating days (no file was published for 19 October 2026).

## Coverage of the requirements
| Requirement | Where |
|---|---|
| Data collection via web API | `src/collect_*.py`, notebook 01 |
| Integration of ≥ 2 sources incl. documentation (keys, losses) | notebook 02 (integration funnel) |
| Storage in SQLite + SQL queries from Python | `src/db.py`, notebooks 01–03 |
| Non-graphical and graphical EDA | notebook 03 |
| Classification with group comparison (region, time of day) | notebook 04 |
| Measures of fit (accuracy, precision, recall, F1, ROC-AUC) and interpretation | notebook 04 |
| **Bonus:** geodata / maps | notebook 05 |
| **Bonus:** chi-squared test, ANOVA, correlation (with p-values) | notebook 05 |
| **Bonus:** k-means clustering | notebook 05 |
| **Bonus:** public GitHub repository | https://github.com/ayu-ahilan/DataAnalytics_Gruppe37 |
| Documentation of AI usage | `docs/AI_usage.md` |

## Folder structure
```
DataAnalytics_Gruppe37/
├── run_collection.py        # runs the complete data collection
├── requirements.txt         # required Python packages
├── src/                     # reusable code (collection, database, features)
├── notebooks/               # 01 collection → 02 integration → 03 EDA → 04 model → 05 bonus
├── data/                    # SQLite database (generated, not in Git)
├── outputs/                 # charts, tables and maps for the presentation
└── docs/                    # AI documentation, presentation notes
```

## Database schema (`data/train_delays.sqlite`)
| Table | Content | Key columns |
|---|---|---|
| `stops` | one row per train stop at a Swiss station (actual data) | `operating_day`, `trip_id`, `bpuic`, `arr_scheduled`, `arr_delay_min`, `arr_status`, `cancelled` |
| `stations` | station master data | `bpuic`, `name`, `lat`, `lon`, `canton`, `region` |
| `weather` | hourly weather for the 100 busiest stations | `bpuic`, `time`, `temperature`, `precipitation`, `snowfall`, `wind` |
| `analysis` | integrated table for the analysis (created in notebook 02) | all of the above, one row per arrival |
| `load_log` | log of the data collection (what was loaded when) | `source`, `key` |

## How to run
**1. Install the packages** (once, in the terminal inside the project folder):
```bash
pip install -r requirements.txt
```

**2. Collect the data** (approx. 30–90 min, needs about 1 GB of free disk space):
```bash
python run_collection.py
```
Options: `--days 7` for fewer days, `--start 2026-10-14 --end 2026-10-27` for a fixed period.
After an interruption simply restart: days that are already loaded are skipped.

**3. Run the notebooks in order** (in VS Code or with `jupyter notebook`):
`02_integration_sqlite` → `03_eda` → `04_classification_model` → `05_clustering_geo_tests`

The charts for the slides are saved automatically in `outputs/`.

## Notes
- The daily actual data files are only available online for about 7 weeks. The data used here can therefore no longer be downloaded again; the database is submitted with the materials ZIP on Moodle.
- The weather data (ERA5) is published with a delay of about 5 days. The script therefore only loads days that are at least 6 days old.
- Attribution (licence opendata.swiss “BY”): data from opentransportdata.swiss and Open-Meteo.com (CC BY 4.0).
