from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlatformInfo:
    platform: str
    platform_code: str
    shortcode: str
    post_type: str | None = None


class PlatformAdapter:
    platform = "unknown"

    def identify(self, url: str) -> PlatformInfo:
        raise NotImplementedError
