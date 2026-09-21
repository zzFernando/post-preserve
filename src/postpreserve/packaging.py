from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile

from .checksums import generate_manifest

PACKAGE_FILES = [
    "data/web/post.wacz",
    "data/representations/screenshot.png",
    "metadata/metadata.json",
    "metadata/source-metadata.json",
    "metadata/capture-report.json",
    "documentation/README.txt",
    "manifest-sha256.txt",
    "package-validation.json",
]


def write_manifest(package_dir: Path) -> Path:
    """Write manifest-sha256.txt covering every file already in `package_dir`."""
    files = [
        p
        for p in package_dir.rglob("*")
        if p.is_file() and p.name not in {"manifest-sha256.txt", "package-validation.json"}
    ]
    manifest = generate_manifest(package_dir, files)
    path = package_dir / "manifest-sha256.txt"
    path.write_text(manifest, encoding="utf-8")
    return path


def write_validation_report(package_dir: Path, report: dict) -> Path:
    """Write `report` as package-validation.json inside `package_dir`."""
    path = package_dir / "package-validation.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def zip_package(package_dir: Path, zip_path: Path) -> Path:
    """Zip every file in `package_dir` into `zip_path`, preserving relative paths."""
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    # WACZ and PNG are already compressed. Storing them avoids a slow, useless second pass.
    with ZipFile(zip_path, "w", compression=ZIP_STORED) as zf:
        for path in sorted(package_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(package_dir).as_posix())
    return zip_path
