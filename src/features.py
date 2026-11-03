"""Laden der integrierten Analysetabelle und Feature Engineering.

Wird von den Notebooks 03-05 gemeinsam verwendet, damit alle Analysen
auf exakt denselben Daten und Definitionen beruhen.
"""
import numpy as np
import pandas as pd

from . import config

WOCHENTAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

ZUGTYP_GRUPPEN = {
    "S": "S-Bahn", "SN": "S-Bahn",
    "R": "Regio", "RE": "RegioExpress", "PE": "RegioExpress",
    "IR": "InterRegio", "IRE": "InterRegio",
    "IC": "InterCity", "ICN": "InterCity",
    "EC": "International", "ICE": "International", "TGV": "International",
    "RJX": "International", "RJ": "International", "EN": "International", "NJ": "International",
}

NUM_FEATURES = ["stunde", "temperatur", "niederschlag", "schneefall", "wind", "log_station_groesse"]
CAT_FEATURES = ["region", "zugtyp_gruppe", "betreiber_gruppe", "wochentag"]
BIN_FEATURES = ["stosszeit", "wochenende", "regen"]


def load_analysis(conn, sample=None, random_state=config.RANDOM_STATE) -> pd.DataFrame:
    """Liest die Tabelle 'analyse' (erstellt in Notebook 02) und ergaenzt Features."""
    df = pd.read_sql("SELECT * FROM analyse", conn)
    if sample and len(df) > sample:
        df = df.sample(sample, random_state=random_state)
    return add_features(df)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    t = pd.to_datetime(df["ankunft_soll"])
    df["datum"] = pd.to_datetime(df["betriebstag"])
    df["stunde"] = t.dt.hour
    df["wochentag_nr"] = t.dt.dayofweek
    df["wochentag"] = pd.Categorical(df["wochentag_nr"].map(dict(enumerate(WOCHENTAGE))),
                                     categories=WOCHENTAGE, ordered=True)
    df["wochenende"] = (df["wochentag_nr"] >= 5).astype(int)
    df["stosszeit"] = (df["stunde"].isin(config.PEAK_HOURS) & (df["wochenende"] == 0)).astype(int)
    df["zeitfenster"] = np.where(df["stosszeit"] == 1, "Stosszeit", "Randzeit")
    df["verspaetet"] = (df["an_delay_min"] >= config.LATE_THRESHOLD_MIN).astype(int)
    df["regen"] = (df["niederschlag"].fillna(0) >= 0.1).astype(int)

    df["zugtyp_gruppe"] = (df["zugtyp"].fillna("").str.upper().str.strip()
                           .map(ZUGTYP_GRUPPEN).fillna("Andere"))
    top_betreiber = df["betreiber"].value_counts().head(6).index
    df["betreiber_gruppe"] = df["betreiber"].where(df["betreiber"].isin(top_betreiber), "Andere")

    groesse = df.groupby("bpuic")["bpuic"].transform("size")
    df["log_station_groesse"] = np.log(groesse)
    return df


def temporal_split(df: pd.DataFrame, test_anteil=0.3):
    """Zeitlicher Split: die letzten Tage dienen als Testdaten (realistischer als Zufallssplit)."""
    tage = np.sort(df["betriebstag"].unique())
    n_test = max(1, int(round(len(tage) * test_anteil)))
    test_tage = set(tage[-n_test:])
    ist_test = df["betriebstag"].isin(test_tage)
    return df[~ist_test], df[ist_test], sorted(test_tage)
