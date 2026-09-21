from __future__ import annotations

import gzip
import io
import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from zipfile import BadZipFile, ZipFile


@dataclass
class WaczValidation:
    """Result of validating a WACZ archive: pass/fail plus diagnostic detail."""

    valid: bool
    errors: list[str]
    warnings: list[str]
    files: list[str]
    urls: list[str]


def validate_wacz(path: Path, expected_url: str | None = None) -> WaczValidation:
    """Validate a WACZ archive's structure and, if given, confirm it captured `expected_url`.

    Checks the zip is readable and uncorrupted, and that it contains a
    datapackage, a WARC payload, and a pages index. Also collects the set of
    captured URLs from the pages/CDX indexes.
    """
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
            corrupt_file = zf.testzip()
            if corrupt_file:
                errors.append(f"WACZ contains a corrupt file: {corrupt_file}")
            if not any(name.endswith("datapackage.json") for name in files):
                errors.append("WACZ datapackage.json is missing")
            if not any(name.endswith((".warc", ".warc.gz")) for name in files):
                errors.append("WACZ does not contain a WARC payload")
            if not any(name.endswith("pages.jsonl") for name in files):
                errors.append("WACZ pages index is missing")

            captured_urls: set[str] = set()
            for name in files:
                if name.endswith("pages.jsonl"):
                    _collect_jsonl_urls(zf.read(name), captured_urls)
                elif name.endswith((".cdx", ".cdxj")):
                    _collect_cdx_urls(zf.read(name), captured_urls)
                elif name.endswith((".cdx.gz", ".cdxj.gz")):
                    _collect_cdx_urls(gzip.decompress(zf.read(name)), captured_urls)
            urls = sorted(captured_urls)
            if not urls:
                warnings.append("No captured URLs were found in WACZ indexes")
            if expected_url and _canonical_url(expected_url) not in {
                _canonical_url(url) for url in captured_urls
            }:
                errors.append(f"Expected URL was not found in WACZ indexes: {expected_url}")
    except (BadZipFile, EOFError, OSError):
        return WaczValidation(False, ["WACZ is not a valid zip archive"], warnings, files, urls)
    return WaczValidation(not errors, errors, warnings, files, urls)


def _canonical_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _collect_jsonl_urls(data: bytes, urls: set[str]) -> None:
    for line in io.BytesIO(data):
        try:
            item = json.loads(line)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        url = item.get("url") if isinstance(item, dict) else None
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            urls.add(url)


def _collect_cdx_urls(data: bytes, urls: set[str]) -> None:
    for raw_line in io.BytesIO(data):
        line = raw_line.decode("utf-8", "replace")
        json_start = line.find("{")
        if json_start < 0:
            continue
        try:
            item = json.loads(line[json_start:])
        except json.JSONDecodeError:
            continue
        url = item.get("url") if isinstance(item, dict) else None
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            urls.add(url)
