from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file's contents, read in chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generate_manifest(root: Path, paths: list[Path]) -> str:
    """Build a `sha256  relative/path` manifest listing for the given files."""
    lines = []
    for path in sorted(paths, key=lambda p: str(p.as_posix())):
        rel = path.relative_to(root).as_posix()
        lines.append(f"{sha256_file(path)}  {rel}")
    return "\n".join(lines) + ("\n" if lines else "")

