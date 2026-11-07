"""Helper functions for web API calls and downloads."""
import time
from pathlib import Path

import requests

from .config import CKAN_BASES, USER_AGENT

HEADERS = {"User-Agent": USER_AGENT}


def get_json(url, params=None, retries=3, timeout=120):
    """GET request with a simple retry; returns the JSON."""
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            if attempt == retries:
                raise
            print(f"  Error ({e}); retrying in {5 * attempt}s ...")
            time.sleep(5 * attempt)


def ckan_resources(package: str) -> list:
    """Reads all resources of a dataset via the CKAN API (package_show)."""
    last_error = None
    for base in CKAN_BASES:
        try:
            data = get_json(f"{base}/package_show", params={"id": package})
            resources = data.get("result", {}).get("resources", [])
            if resources:
                return resources
        except Exception as e:  # try the next platform
            last_error = e
    raise RuntimeError(f"Dataset '{package}' not found ({last_error})")


def resource_url(res: dict) -> str:
    return res.get("download_url") or res.get("url") or ""


def download(url: str, target: Path, chunk=1 << 20) -> Path:
    """Downloads a (large) file as a stream and shows the progress."""
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".part")
    with requests.get(url, headers=HEADERS, stream=True, timeout=300) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        loaded, next_report = 0, 0
        with open(tmp, "wb") as f:
            for block in r.iter_content(chunk_size=chunk):
                f.write(block)
                loaded += len(block)
                if loaded >= next_report:
                    if total:
                        print(f"  {loaded / 1e6:,.0f} / {total / 1e6:,.0f} MB", end="\r")
                    next_report += 50 * chunk
    tmp.replace(target)
    print(f"  downloaded: {target.name} ({loaded / 1e6:,.0f} MB)        ")
    return target
