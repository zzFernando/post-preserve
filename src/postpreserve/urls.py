from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse, urlunparse


@dataclass(frozen=True)
class NormalizedURL:
    """A validated Instagram post/reel URL, canonicalized to its shortcode form."""

    original: str
    normalized: str
    platform: str
    shortcode: str
    source_identifier: str


def normalize_instagram_url(url: str) -> NormalizedURL:
    """Validate an Instagram post/reel URL and normalize it to https://www.instagram.com/<kind>/<shortcode>/.

    Raises ValueError if the URL isn't a recognized Instagram post/reel link.
    """
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("URL must use http or https")
    host = parsed.netloc.lower()
    if host not in {"instagram.com", "www.instagram.com", "m.instagram.com"}:
        raise ValueError("Unsupported host")
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise ValueError("Unrecognized Instagram post URL")
    kind, shortcode = parts[0], parts[1]
    if kind not in {"p", "reel", "reels"}:
        raise ValueError("Unsupported Instagram URL type")
    normalized = urlunparse(("https", "www.instagram.com", f"/{kind}/{shortcode}/", "", "", ""))
    return NormalizedURL(
        original=url,
        normalized=normalized,
        platform="instagram",
        shortcode=shortcode,
        source_identifier=shortcode,
    )
