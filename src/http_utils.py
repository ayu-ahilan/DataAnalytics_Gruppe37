"""Hilfsfunktionen fuer Web-API-Aufrufe und Downloads."""
import time
from pathlib import Path

import requests

from .config import CKAN_BASES, USER_AGENT

HEADERS = {"User-Agent": USER_AGENT}


def get_json(url, params=None, retries=3, timeout=120):
    """GET-Request mit einfachem Retry; gibt das JSON zurueck."""
    for versuch in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            if versuch == retries:
                raise
            print(f"  Fehler ({e}); neuer Versuch in {5 * versuch}s ...")
            time.sleep(5 * versuch)


def ckan_resources(package: str) -> list:
    """Liest ueber die CKAN-API (package_show) alle Ressourcen eines Datensatzes."""
    letzter_fehler = None
    for base in CKAN_BASES:
        try:
            data = get_json(f"{base}/package_show", params={"id": package})
            resources = data.get("result", {}).get("resources", [])
            if resources:
                return resources
        except Exception as e:  # naechste Plattform probieren
            letzter_fehler = e
    raise RuntimeError(f"Datensatz '{package}' nicht gefunden ({letzter_fehler})")


def resource_url(res: dict) -> str:
    return res.get("download_url") or res.get("url") or ""


def download(url: str, ziel: Path, chunk=1 << 20) -> Path:
    """Laedt eine (grosse) Datei gestreamt herunter und zeigt den Fortschritt."""
    ziel = Path(ziel)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    tmp = ziel.with_suffix(ziel.suffix + ".part")
    with requests.get(url, headers=HEADERS, stream=True, timeout=300) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        geladen, naechste_meldung = 0, 0
        with open(tmp, "wb") as f:
            for block in r.iter_content(chunk_size=chunk):
                f.write(block)
                geladen += len(block)
                if geladen >= naechste_meldung:
                    if total:
                        print(f"  {geladen / 1e6:,.0f} / {total / 1e6:,.0f} MB", end="\r")
                    naechste_meldung += 50 * chunk
    tmp.replace(ziel)
    print(f"  heruntergeladen: {ziel.name} ({geladen / 1e6:,.0f} MB)        ")
    return ziel
