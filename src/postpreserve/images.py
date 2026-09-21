from __future__ import annotations

import struct
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def validate_png(path: Path) -> list[str]:
    """Return validation errors for a PNG file without requiring Pillow."""
    if not path.exists():
        return ["Screenshot is missing"]
    if path.stat().st_size < 24:
        return ["Screenshot is too small to be a valid PNG"]

    with path.open("rb") as stream:
        header = stream.read(24)
    if header[:8] != PNG_SIGNATURE:
        return ["Screenshot does not have a valid PNG signature"]
    if header[12:16] != b"IHDR":
        return ["Screenshot is missing the PNG IHDR chunk"]

    width, height = struct.unpack(">II", header[16:24])
    if width == 0 or height == 0:
        return ["Screenshot has invalid dimensions"]
    return []
