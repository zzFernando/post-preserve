from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import BadZipFile, ZipFile


@dataclass
class WaczValidation:
    valid: bool
    errors: list[str]
    warnings: list[str]
    files: list[str]
    urls: list[str]


def validate_wacz(path: Path, expected_url: str | None = None) -> WaczValidation:
    errors: list[str] = []
    warnings: list[str] = []
    files: list[str] = []
    urls: list[str] = []
    if not path.exists() or path.stat().st_size == 0:
        return WaczValidation(False, ["WACZ is missing or empty"], warnings, files, urls)
    try:
        with ZipFile(path) as zf:
            files = sorted(zf.namelist())
            if not files:
                errors.append("WACZ archive is empty")
            manifest_candidates = [
                n for n in files if n.endswith("datapackage.json") or n.endswith("index.cdxj")
            ]
            if not manifest_candidates:
                warnings.append("Common WACZ index files were not found")
            for name in files:
                if name.endswith((".json", ".cdxj", ".warc", ".warc.gz")) and expected_url:
                    try:
                        data = zf.read(name).decode("utf-8", "ignore")
                    except Exception:
                        continue
                    if expected_url in data and expected_url not in urls:
                        urls.append(expected_url)
    except BadZipFile:
        return WaczValidation(False, ["WACZ is not a valid zip archive"], warnings, files, urls)
    return WaczValidation(not errors, errors, warnings, files, urls)
