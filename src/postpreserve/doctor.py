from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from .capture.scoop import PROJECT_ROOT, SCOOP_BIN

MIN_FREE_DISK_BYTES = 1024**3


def doctor() -> dict:
    """Check that the local environment has everything `archive` needs to run.

    Verifies Node/Python versions, Scoop and Chromium availability, workspace
    writability, and free disk space.
    """
    node_version = _command_output(["node", "--version"])
    node_major = int(node_version.lstrip("v").split(".")[0]) if node_version else 0
    scoop_available = SCOOP_BIN.exists()
    installed_browsers = _command_output(
        ["npx", "playwright", "install", "--list"], cwd=PROJECT_ROOT
    )
    chromium_available = bool(
        installed_browsers and "chromium_headless_shell" in installed_browsers
    )
    workspace = Path("workspace")
    workspace.mkdir(parents=True, exist_ok=True)
    free_disk_bytes = shutil.disk_usage(workspace).free
    return {
        "python_version": sys.version.split()[0],
        "node_version": node_version,
        "node_version_supported": 20 <= node_major <= 23,
        "scoop_available": scoop_available,
        "chromium_available": chromium_available,
        "writable_workspace": _can_write(workspace),
        "disk_space_ok": free_disk_bytes >= MIN_FREE_DISK_BYTES,
        "free_disk_bytes": free_disk_bytes,
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


def _command_output(command: list[str], cwd: Path | None = None) -> str | None:
    try:
        result = subprocess.run(
            command,
            check=False,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None
