from __future__ import annotations

from ..urls import normalize_instagram_url
from .base import PlatformAdapter, PlatformInfo


class InstagramAdapter(PlatformAdapter):
    platform = "instagram"

    def identify(self, url: str) -> PlatformInfo:
        normalized = normalize_instagram_url(url)
        post_type = (
            "reel"
            if "/reel/" in normalized.normalized or "/reels/" in normalized.normalized
            else "post"
        )
        return PlatformInfo("instagram", "IG", normalized.shortcode, post_type=post_type)
