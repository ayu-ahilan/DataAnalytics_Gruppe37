"""Assignment of stations to language regions.

Basic rule: assignment via the canton. In the bilingual cantons
(BE, FR, VS) the majority language of the most important station
municipalities is corrected via an exception list. This simplification
is mentioned as a limitation in the presentation.
"""
import unicodedata

GERMAN = "German-speaking"
ROMANDY = "Romandy"
TICINO = "Ticino"
UNKNOWN = "Unknown"

CANTON_REGION = {
    # Romandy (French-speaking)
    "GE": ROMANDY, "VD": ROMANDY, "NE": ROMANDY, "JU": ROMANDY, "FR": ROMANDY, "VS": ROMANDY,
    # Ticino (Italian-speaking)
    "TI": TICINO,
    # German-speaking Switzerland (incl. GR, where Romansh/Italian are minorities)
    "ZH": GERMAN, "BE": GERMAN, "LU": GERMAN, "UR": GERMAN, "SZ": GERMAN, "OW": GERMAN,
    "NW": GERMAN, "GL": GERMAN, "ZG": GERMAN, "SO": GERMAN, "BS": GERMAN, "BL": GERMAN,
    "SH": GERMAN, "AR": GERMAN, "AI": GERMAN, "SG": GERMAN, "GR": GERMAN, "AG": GERMAN,
    "TG": GERMAN,
}

# Canton names as they may appear in the source data (German, French, Italian, English)
CANTON_NAME_ABBR = {
    "zurich": "ZH", "zuerich": "ZH", "bern": "BE", "berne": "BE", "luzern": "LU",
    "uri": "UR", "schwyz": "SZ", "obwalden": "OW", "nidwalden": "NW", "glarus": "GL",
    "zug": "ZG", "fribourg": "FR", "freiburg": "FR", "solothurn": "SO",
    "basel-stadt": "BS", "basel-landschaft": "BL", "schaffhausen": "SH",
    "appenzell ausserrhoden": "AR", "appenzell innerrhoden": "AI",
    "st. gallen": "SG", "sankt gallen": "SG", "graubunden": "GR", "graubuenden": "GR",
    "grisons": "GR", "aargau": "AG", "thurgau": "TG", "ticino": "TI", "tessin": "TI",
    "vaud": "VD", "waadt": "VD", "valais": "VS", "wallis": "VS", "neuchatel": "NE",
    "neuenburg": "NE", "geneve": "GE", "genf": "GE", "geneva": "GE", "jura": "JU",
}

# Exceptions in bilingual cantons (municipality name -> region)
MUNICIPALITY_EXCEPTIONS = {
    # Upper Valais: German-speaking
    "brig-glis": GERMAN, "visp": GERMAN, "naters": GERMAN, "leuk": GERMAN, "raron": GERMAN,
    "zermatt": GERMAN, "tasch": GERMAN, "st. niklaus": GERMAN, "stalden (vs)": GERMAN,
    "fiesch": GERMAN, "goms": GERMAN, "bitsch": GERMAN, "steg-hohtenn": GERMAN,
    "gampel-bratsch": GERMAN, "lalden": GERMAN, "salgesch": GERMAN, "ausserberg": GERMAN,
    # German-speaking part of Fribourg
    "dudingen": GERMAN, "schmitten (fr)": GERMAN, "wunnewil-flamatt": GERMAN,
    "kerzers": GERMAN, "murten": GERMAN, "gurmels": GERMAN, "tafers": GERMAN,
    # Bernese Jura: French-speaking
    "moutier": ROMANDY, "saint-imier": ROMANDY, "tavannes": ROMANDY, "tramelan": ROMANDY,
    "reconvilier": ROMANDY, "sonceboz-sombeval": ROMANDY, "la neuveville": ROMANDY,
    "court": ROMANDY, "corgemont": ROMANDY, "cortebert": ROMANDY, "courtelary": ROMANDY,
    "villeret": ROMANDY, "valbirse": ROMANDY, "malleray": ROMANDY,
}


def _norm(text) -> str:
    if text is None:
        return ""
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return text.strip().lower()


def canton_abbr(canton) -> str:
    """Returns the canton abbreviation (accepts abbreviations or names)."""
    k = str(canton or "").strip()
    if k.upper() in CANTON_REGION:
        return k.upper()
    return CANTON_NAME_ABBR.get(_norm(k), "")


def assign_region(canton, municipality) -> str:
    m = _norm(municipality)
    if m in MUNICIPALITY_EXCEPTIONS:
        return MUNICIPALITY_EXCEPTIONS[m]
    return CANTON_REGION.get(canton_abbr(canton), UNKNOWN)
