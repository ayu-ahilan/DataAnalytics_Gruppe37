# Wann und wo ist der Zug zu spät?
**Zugverspätungen in der Schweiz im Regionen- und Tageszeitvergleich**

Data Analytics HS2026 (ZHAW), **Gruppe 37**: Marc Stump, Ayushan Ahilan

## Forschungsfrage
Welche Faktoren beeinflussen, ob ein Zug mit **≥ 3 Minuten Verspätung** ankommt (SBB-Definition), und unterscheiden sich diese Faktoren zwischen **Deutschschweiz und Romandie** sowie zwischen **Stosszeiten und Randzeiten**?

## Datenquellen (alle selbst über Web-APIs gesammelt)
| # | Quelle | Zugriff | Verknüpfung |
|---|---|---|---|
| 1 | Ist-Daten v2 (opentransportdata.swiss) | CKAN-API `package_show` → Tages-CSV | — |
| 2 | Service Points / atlas (opentransportdata.swiss) | CKAN-API → CSV | über `bpuic` (Haltestellennummer) |
| 3 | Open-Meteo Historical Weather API | REST-API (JSON) | über `bpuic` + Stunde der Soll-Ankunft |

## Abdeckung der Anforderungen
| Anforderung | Wo |
|---|---|
| Datensammlung via Web-API | `src/collect_*.py`, Notebook 01 |
| Integration von ≥ 2 Quellen inkl. Dokumentation (Schlüssel, Verluste) | Notebook 02 (Integrations-Trichter) |
| Speicherung in SQLite + SQL-Abfragen aus Python | `src/db.py`, Notebooks 01–03 |
| Nicht-grafische und grafische EDA | Notebook 03 |
| Klassifikation mit Gruppenvergleich (Region, Tageszeit) | Notebook 04 |
| Gütemasse (Accuracy, Precision, Recall, F1, ROC-AUC) und Interpretation | Notebook 04 |
| **Bonus:** Geodaten/Karten | Notebook 05 |
| **Bonus:** Chi²-Test, ANOVA, Korrelation (mit p-Werten) | Notebook 05 |
| **Bonus:** k-Means-Clustering | Notebook 05 |
| **Bonus:** öffentliches GitHub-Repo | https://github.com/ayu-ahilan/DataAnalytics_Gruppe37 |
| Dokumentation KI-Nutzung | `docs/KI_Nutzung.md` |

## Ordnerstruktur
```
DataAnalytics_Gruppe37/
├── run_collection.py        # startet die ganze Datensammlung
├── requirements.txt         # benötigte Python-Pakete
├── src/                     # wiederverwendbarer Code (Sammlung, DB, Features)
├── notebooks/               # 01 Sammlung → 02 Integration → 03 EDA → 04 Modell → 05 Bonus
├── data/                    # SQLite-Datenbank (wird erzeugt, nicht im Git)
├── outputs/                 # Grafiken, Tabellen, Karten für die Präsentation
└── docs/                    # KI-Dokumentation, Präsentationsnotizen
```

## Anleitung
**1. Pakete installieren** (einmalig, im Terminal im Projektordner):
```bash
cd "~/Documents/5. Semester/DataAnalytics/DataAnalytics_Gruppe37"
pip install -r requirements.txt
```

**2. Daten sammeln** (ca. 30–90 Min., braucht ca. 1 GB freien Speicher):
```bash
python run_collection.py
```
Optionen: `--days 7` für weniger Tage, `--start 2026-10-05 --end 2026-10-18` für einen festen Zeitraum.
Bei einem Abbruch einfach neu starten: bereits geladene Tage werden übersprungen.

**3. Notebooks der Reihe nach ausführen** (in VS Code oder mit `jupyter notebook`):
`02_integration_sqlite` → `03_eda` → `04_modell_klassifikation` → `05_clustering_geo_tests`

Die Grafiken für die Folien landen automatisch in `outputs/`.

## Hinweise
- Die Ist-Daten-Tagesdateien bleiben nur ca. 7 Wochen online. Deshalb sollten die Daten **bald** gesammelt werden.
- Die Wetterdaten (ERA5) erscheinen mit ca. 5 Tagen Verzögerung. Darum lädt das Skript nur Tage, die mindestens 6 Tage alt sind.
- Quellenangabe (Lizenz opendata.swiss «BY»): Daten von opentransportdata.swiss sowie Open-Meteo.com (CC BY 4.0).
