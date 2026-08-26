from __future__ import annotations

import shutil
import sys
from pathlib import Path


def doctor(browser_profile=None) -> dict:
    return {
        "python_version": sys.version.split()[0],
        "docker_available": shutil.which("docker") is not None,
        "browsertrix_image_available": False,
        "writable_workspace": Path("workspace").exists() or _can_write(Path("workspace")),
        "disk_space_ok": True,
        "browser_profile": str(browser_profile) if browser_profile else None,
    }


def _can_write(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        marker = path / ".write-test"
        marker.write_text("ok", encoding="utf-8")
        marker.unlink()
        return True
    except Exception:
        return False
