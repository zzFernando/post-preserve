from __future__ import annotations

import json
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

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


def assemble_package(source_dir: Path, package_dir: Path) -> list[Path]:
    package_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for rel in PACKAGE_FILES[:-2]:
        src = source_dir / rel
        if src.exists():
            dest = package_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if src.resolve() != dest.resolve():
                shutil.copy2(src, dest)
            copied.append(dest)
    return copied


def write_manifest(package_dir: Path) -> Path:
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
    path = package_dir / "package-validation.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def zip_package(package_dir: Path, zip_path: Path) -> Path:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for path in sorted(package_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(package_dir).as_posix())
    return zip_path
