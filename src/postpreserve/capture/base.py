from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class CaptureArtifacts:
    wacz_path: Path
    screenshot_path: Path | None
    metadata: dict
    source_metadata: dict
    capture_report: dict


class CaptureBackend:
    name = "base"

    def capture(
        self,
        *,
        url: str,
        workdir: Path,
        timeout_seconds: int,
        headed: bool,
        browser_profile,
    ) -> CaptureArtifacts:
        raise NotImplementedError
