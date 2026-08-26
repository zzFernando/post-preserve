from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CaptureConfig:
    backend: str = "browsertrix"
    timeout_seconds: int = 180
    max_interactions: int = 30
    headed: bool = False


@dataclass
class PackageConfig:
    checksum_algorithm: str = "sha256"
    output_format: str = "zip"


@dataclass
class QualityConfig:
    require_wacz: bool = True
    require_screenshot: bool = True
    require_valid_metadata: bool = True


@dataclass
class AppConfig:
    project_name: str = "PostPreserve"
    prefix: str = "PP"
    platform_codes: dict[str, str] = field(default_factory=lambda: {"instagram": "IG"})
    capture: CaptureConfig = field(default_factory=CaptureConfig)
    package: PackageConfig = field(default_factory=PackageConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)


@dataclass
class ArchiveRequest:
    url: str
    output_dir: Path
    browser_profile: Path | None = None
    timeout: int | None = None
    identifier: str | None = None
    headed: bool = False
    keep_workdir: bool = False
    log_level: str = "INFO"
    container_runtime: str | None = None


@dataclass
class CaptureResult:
    identifier: str
    platform: str
    original_url: str
    normalized_url: str
    workdir: Path
    wacz_path: Path | None
    screenshot_path: Path | None
    metadata_path: Path
    source_metadata_path: Path
    report_path: Path
    status: str
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)
