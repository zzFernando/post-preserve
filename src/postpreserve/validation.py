from __future__ import annotations

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from zipfile import ZipFile

from .checksums import sha256_file
from .images import validate_png
from .packaging import PACKAGE_FILES
from .wacz import validate_wacz


def validate_package(path: Path) -> dict:
    """Validate a preservation package (a directory or its zipped form).

    Checks required files are present, the checksum manifest matches the
    contents, metadata is well-formed, and the embedded WACZ/screenshot are
    valid. Returns a report dict with per-check booleans and a `final_status`
    of "complete" or "partial".
    """
    package_dir = path
    temp_context = None
    if path.is_file() and path.suffix == ".zip":
        temp_context = tempfile.TemporaryDirectory(prefix=f".{path.stem}.", dir=path.parent)
        temp_dir = Path(temp_context.name)
        with ZipFile(path) as zf:
            for member in zf.infolist():
                target = (temp_dir / member.filename).resolve()
                if not target.is_relative_to(temp_dir.resolve()):
                    raise ValueError(f"Unsafe path in package ZIP: {member.filename}")
            zf.extractall(temp_dir)
        package_dir = temp_dir
    errors: list[str] = []
    warnings: list[str] = []
    missing = [rel for rel in PACKAGE_FILES if not (package_dir / rel).exists()]
    unexpected = []
    if missing:
        errors.extend(f"Missing file: {m}" for m in missing)
    manifest = package_dir / "manifest-sha256.txt"
    checksums_valid = False
    if manifest.exists():
        expected = {}
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, rel = line.split("  ", 1)
            expected[rel] = digest
        actual = {}
        for file in package_dir.rglob("*"):
            if file.is_file() and file.name not in {
                "manifest-sha256.txt",
                "package-validation.json",
            }:
                actual[file.relative_to(package_dir).as_posix()] = sha256_file(file)
        checksums_valid = expected == actual
        if not checksums_valid:
            errors.append("Checksum manifest mismatch")
    else:
        errors.append("Missing manifest-sha256.txt")
    metadata_valid = False
    metadata = {}
    meta_path = package_dir / "metadata/metadata.json"
    if meta_path.exists():
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        metadata_valid = bool(metadata.get("identifier"))
    else:
        metadata_valid = False
    expected_url = metadata.get("normalized_url") if metadata_valid else None
    wacz_result = validate_wacz(package_dir / "data/web/post.wacz", expected_url)
    screenshot_errors = validate_png(package_dir / "data/representations/screenshot.png")
    errors.extend(screenshot_errors)
    screenshot_valid = not screenshot_errors
    result = {
        "identifier": metadata.get("identifier") if meta_path.exists() else None,
        "validation_date": datetime.now(UTC).isoformat(),
        "package_structure_valid": not missing,
        "metadata_valid": metadata_valid,
        "wacz_valid": wacz_result.valid,
        "screenshot_valid": screenshot_valid,
        "checksums_valid": checksums_valid,
        "unexpected_files": unexpected,
        "missing_files": missing,
        "warnings": warnings + wacz_result.warnings,
        "errors": errors + wacz_result.errors,
        "final_status": "complete"
        if not errors
        and metadata_valid
        and wacz_result.valid
        and screenshot_valid
        and checksums_valid
        else "partial",
    }
    if temp_context:
        temp_context.cleanup()
    return result
