"""Zuordnung von Bahnhoefen zu Sprachregionen.

Grundregel: Zuordnung ueber den Kanton. In den zweisprachigen Kantonen
(BE, FR, VS) wird fuer die wichtigsten Bahnhofsgemeinden die Mehrheitssprache
ueber eine Ausnahmeliste korrigiert. Diese Vereinfachung wird in der
Praesentation als Limitation erwaehnt.
"""
import unicodedata

KANTON_REGION = {
    # Romandie
    "GE": "Romandie", "VD": "Romandie", "NE": "Romandie", "JU": "Romandie",
    "FR": "Romandie", "VS": "Romandie",
    # Tessin (italienischsprachig)
    "TI": "Tessin",
    # Deutschschweiz (inkl. GR, wo Romanisch/Italienisch Minderheiten sind)
    "ZH": "Deutschschweiz", "BE": "Deutschschweiz", "LU": "Deutschschweiz",
    "UR": "Deutschschweiz", "SZ": "Deutschschweiz", "OW": "Deutschschweiz",
    "NW": "Deutschschweiz", "GL": "Deutschschweiz", "ZG": "Deutschschweiz",
    "SO": "Deutschschweiz", "BS": "Deutschschweiz", "BL": "Deutschschweiz",
    "SH": "Deutschschweiz", "AR": "Deutschschweiz", "AI": "Deutschschweiz",
    "SG": "Deutschschweiz", "GR": "Deutschschweiz", "AG": "Deutschschweiz",
    "TG": "Deutschschweiz",
}

KANTON_NAME_ABK = {
    "zurich": "ZH", "zuerich": "ZH", "bern": "BE", "berne": "BE", "luzern": "LU",
    "uri": "UR", "schwyz": "SZ", "obwalden": "OW", "nidwalden": "NW", "glarus": "GL",
    "zug": "ZG", "fribourg": "FR", "freiburg": "FR", "solothurn": "SO",
    "basel-stadt": "BS", "basel-landschaft": "BL", "schaffhausen": "SH",
    "appenzell ausserrhoden": "AR", "appenzell innerrhoden": "AI",
    "st. gallen": "SG", "sankt gallen": "SG", "graubunden": "GR", "graubuenden": "GR",
    "grisons": "GR", "aargau": "AG", "thurgau": "TG", "ticino": "TI", "tessin": "TI",
    "vaud": "VD", "waadt": "VD", "valais": "VS", "wallis": "VS", "neuchatel": "NE",
    "neuenburg": "NE", "geneve": "GE", "genf": "GE", "jura": "JU",
}

# Ausnahmen in zweisprachigen Kantonen (Gemeindename -> Region)
GEMEINDE_AUSNAHMEN = {
    # Oberwallis: deutschsprachig
    "brig-glis": "Deutschschweiz", "visp": "Deutschschweiz", "naters": "Deutschschweiz",
    "leuk": "Deutschschweiz", "raron": "Deutschschweiz", "zermatt": "Deutschschweiz",
    "tasch": "Deutschschweiz", "st. niklaus": "Deutschschweiz", "stalden (vs)": "Deutschschweiz",
    "fiesch": "Deutschschweiz", "goms": "Deutschschweiz", "bitsch": "Deutschschweiz",
    "steg-hohtenn": "Deutschschweiz", "gampel-bratsch": "Deutschschweiz",
    "lalden": "Deutschschweiz", "salgesch": "Deutschschweiz", "ausserberg": "Deutschschweiz",
    # Deutschfreiburg
    "dudingen": "Deutschschweiz", "schmitten (fr)": "Deutschschweiz",
    "wunnewil-flamatt": "Deutschschweiz", "kerzers": "Deutschschweiz",
    "murten": "Deutschschweiz", "gurmels": "Deutschschweiz", "tafers": "Deutschschweiz",
    # Berner Jura: franzoesischsprachig
    "moutier": "Romandie", "saint-imier": "Romandie", "tavannes": "Romandie",
    "tramelan": "Romandie", "reconvilier": "Romandie", "sonceboz-sombeval": "Romandie",
    "la neuveville": "Romandie", "court": "Romandie", "corgemont": "Romandie",
    "cortebert": "Romandie", "courtelary": "Romandie", "villeret": "Romandie",
    "valbirse": "Romandie", "malleray": "Romandie",
}


def _norm(text) -> str:
    if text is None:
        return ""
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return text.strip().lower()


def kanton_abk(kanton) -> str:
    """Gibt das Kantonskuerzel zurueck (akzeptiert Kuerzel oder Namen)."""
    k = str(kanton or "").strip()
    if k.upper() in KANTON_REGION:
        return k.upper()
    return KANTON_NAME_ABK.get(_norm(k), "")


def assign_region(kanton, gemeinde) -> str:
    g = _norm(gemeinde)
    if g in GEMEINDE_AUSNAHMEN:
        return GEMEINDE_AUSNAHMEN[g]
    return KANTON_REGION.get(kanton_abk(kanton), "Unbekannt")
