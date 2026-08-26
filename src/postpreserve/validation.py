from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from zipfile import ZipFile

from .checksums import sha256_file
from .packaging import PACKAGE_FILES
from .wacz import validate_wacz


def validate_package(path: Path) -> dict:
    package_dir = path
    if path.is_file() and path.suffix == ".zip":
        with ZipFile(path) as zf:
            temp_dir = path.parent / f".{path.stem}.unpacked"
            if temp_dir.exists():
                import shutil

                shutil.rmtree(temp_dir)
            temp_dir.mkdir(parents=True)
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
    wacz_result = validate_wacz(package_dir / "data/web/post.wacz")
    metadata_valid = False
    metadata = {}
    meta_path = package_dir / "metadata/metadata.json"
    if meta_path.exists():
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        metadata_valid = bool(metadata.get("identifier"))
    else:
        metadata_valid = False
    return {
        "identifier": metadata.get("identifier") if meta_path.exists() else None,
        "validation_date": datetime.now(UTC).isoformat(),
        "package_structure_valid": not missing,
        "metadata_valid": metadata_valid,
        "wacz_valid": wacz_result.valid,
        "screenshot_valid": (
            (package_dir / "data/representations/screenshot.png").exists()
            and (package_dir / "data/representations/screenshot.png").stat().st_size > 0
        ),
        "checksums_valid": checksums_valid,
        "unexpected_files": unexpected,
        "missing_files": missing,
        "warnings": warnings + wacz_result.warnings,
        "errors": errors + wacz_result.errors,
        "final_status": "complete"
        if not errors and metadata_valid and wacz_result.valid and checksums_valid
        else "partial",
    }
