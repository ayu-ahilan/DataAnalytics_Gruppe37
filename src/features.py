"""Loading the integrated analysis table and feature engineering.

Shared by notebooks 03-05, so that all analyses are based on exactly
the same data and definitions.
"""
import numpy as np
import pandas as pd

from . import config

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

TRAIN_TYPE_GROUPS = {
    "S": "S-Bahn", "SN": "S-Bahn",
    "R": "Regio", "RE": "RegioExpress", "PE": "RegioExpress",
    "IR": "InterRegio", "IRE": "InterRegio",
    "IC": "InterCity", "ICN": "InterCity",
    "EC": "International", "ICE": "International", "TGV": "International",
    "RJX": "International", "RJ": "International", "EN": "International", "NJ": "International",
}

NUM_FEATURES = ["hour", "temperature", "precipitation", "snowfall", "wind", "log_station_size"]
CAT_FEATURES = ["region", "train_type_group", "operator_group", "weekday"]
BIN_FEATURES = ["peak", "weekend", "rain"]


def load_analysis(conn, sample=None, random_state=config.RANDOM_STATE) -> pd.DataFrame:
    """Reads the table 'analysis' (created in notebook 02) and adds features."""
    df = pd.read_sql("SELECT * FROM analysis", conn)
    if sample and len(df) > sample:
        df = df.sample(sample, random_state=random_state)
    return add_features(df)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    t = pd.to_datetime(df["arr_scheduled"])
    df["date"] = pd.to_datetime(df["operating_day"])
    df["hour"] = t.dt.hour
    df["weekday_nr"] = t.dt.dayofweek
    df["weekday"] = pd.Categorical(df["weekday_nr"].map(dict(enumerate(WEEKDAYS))),
                                   categories=WEEKDAYS, ordered=True)
    df["weekend"] = (df["weekday_nr"] >= 5).astype(int)
    df["peak"] = (df["hour"].isin(config.PEAK_HOURS) & (df["weekend"] == 0)).astype(int)
    df["time_window"] = np.where(df["peak"] == 1, "Peak", "Off-peak")
    df["late"] = (df["arr_delay_min"] >= config.LATE_THRESHOLD_MIN).astype(int)
    df["rain"] = (df["precipitation"].fillna(0) >= 0.1).astype(int)

    df["train_type_group"] = (df["train_type"].fillna("").str.upper().str.strip()
                              .map(TRAIN_TYPE_GROUPS).fillna("Other"))
    top_operators = df["operator"].value_counts().head(6).index
    df["operator_group"] = df["operator"].where(df["operator"].isin(top_operators), "Other")

    size = df.groupby("bpuic")["bpuic"].transform("size")
    df["log_station_size"] = np.log(size)
    return df


def temporal_split(df: pd.DataFrame, test_share=0.3):
    """Temporal split: the last days are used as test data (more realistic than a random split)."""
    days = np.sort(df["operating_day"].unique())
    n_test = max(1, int(round(len(days) * test_share)))
    test_days = set(days[-n_test:])
    is_test = df["operating_day"].isin(test_days)
    return df[~is_test], df[is_test], sorted(test_days)
