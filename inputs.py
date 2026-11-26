"""Fetch public inputs into a private cache and record byte-level provenance."""

from pathlib import Path
from datetime import date
import hashlib
import json
import os
import requests

CACHE = Path(os.environ.get("BSC_CACHE", ".cache"))
OUT = Path("results")
OUT.mkdir(exist_ok=True)


def source(url, name=None):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (name or url.rsplit("/", 1)[-1])
    if not path.exists():
        with requests.get(url, stream=True, timeout=(20, 180)) as response:
            response.raise_for_status()
            temporary = path.with_suffix(path.suffix + ".partial")
            with temporary.open("wb") as handle:
                for block in response.iter_content(1024 * 1024):
                    handle.write(block)
            temporary.replace(path)
    with path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    manifest = Path("data/sources.json")
    rows = (
        json.loads(manifest.read_text(encoding="utf-8-sig"))
        if manifest.exists()
        else {}
    )
    if path.name in rows and rows[path.name]["sha256"] != digest:
        raise ValueError(f"Source bytes changed for {path.name}")
    rows.setdefault(
        path.name,
        dict(
            url=url,
            sha256=digest,
            bytes=path.stat().st_size,
            verified=str(date.today()),
        ),
    )
    manifest.write_text(json.dumps(rows, indent=2) + "\n")
    return path
