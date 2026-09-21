from __future__ import annotations

import hashlib
import json
import shutil
import socket
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import ZIP_STORED, ZipFile

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCOOP_BIN = PROJECT_ROOT / "node_modules/.bin/scoop"
CAPTURE_SCRIPT = PROJECT_ROOT / "scripts/capture.mjs"


@dataclass
class CaptureArtifacts:
    wacz_path: Path
    screenshot_path: Path
    metadata: dict
    source_metadata: dict
    capture_report: dict


class ScoopBackend:
    """Small native capture backend: Node + Chromium, no Docker VM or image."""

    name = "scoop"

    def __init__(self, executable: Path | str | None = None) -> None:
        """Use `executable` as the Scoop binary, or the bundled node_modules build if omitted."""
        self.executable = str(executable or SCOOP_BIN)

    def capture(
        self,
        *,
        url: str,
        workdir: Path,
        timeout_seconds: int,
        headed: bool,
        browser_profile,
    ) -> CaptureArtifacts:
        """Capture `url` with Scoop, probing extra carousel slides for Instagram posts.

        Returns the merged WACZ/screenshot/metadata for the whole post.
        Raises if browser_profile is given (unsupported) or Scoop isn't installed.
        """
        if browser_profile:
            raise ValueError("Scoop does not support browser profiles; capture a public URL")
        if not Path(self.executable).exists() and shutil.which(self.executable) is None:
            raise FileNotFoundError("Scoop is not installed; run `pixi run setup`")

        workdir = workdir.resolve()
        primary = self._capture_once(
            url, workdir / "primary", timeout_seconds=timeout_seconds, headed=headed
        )
        captures = [primary]
        media_urls = {
            _media_key(item): item for item in _instagram_media_urls(primary.source_metadata)
        }

        # Instagram normally loads two neighboring carousel items. Probe every other
        # slide and keep only captures that add media; invalid indexes return quickly.
        if "/p/" in url and len(media_urls) > 1:
            for index in range(3, 21, 2):
                extra = self._capture_once(
                    f"{url}?img_index={index}",
                    workdir / f"slide-{index}",
                    timeout_seconds=timeout_seconds,
                    headed=headed,
                )
                found = {
                    _media_key(item): item for item in _instagram_media_urls(extra.source_metadata)
                }
                if not found.keys() - media_urls.keys():
                    break
                media_urls.update(found)
                captures.append(extra)

        wacz_path = workdir / "post.wacz"
        if len(captures) == 1:
            shutil.move(primary.wacz_path, wacz_path)
        else:
            _merge_wacz([capture.wacz_path for capture in captures], wacz_path)
        screenshot_path = workdir / "screenshot.png"
        shutil.copy2(primary.screenshot_path, screenshot_path)
        primary.source_metadata["media_urls"] = sorted(media_urls.values())
        primary.source_metadata["media_count_captured"] = len(media_urls)
        primary.wacz_path = wacz_path
        primary.screenshot_path = screenshot_path
        primary.capture_report["captures_merged"] = len(captures)
        return primary

    def _capture_once(
        self, url: str, workdir: Path, *, timeout_seconds: int, headed: bool
    ) -> CaptureArtifacts:
        workdir = workdir.resolve()
        attachments = workdir / "attachments"
        attachments.mkdir(parents=True, exist_ok=True)
        wacz_path = workdir / "post.wacz"
        summary_path = workdir / "source-metadata.json"
        command = [
            "node",
            str(CAPTURE_SCRIPT),
            url,
            str(wacz_path),
            str(summary_path),
            str(attachments),
            str(timeout_seconds * 1000),
            str(not headed).lower(),
            str(_free_port()),
        ]
        subprocess.run(command, cwd=PROJECT_ROOT, check=True, timeout=timeout_seconds + 30)

        screenshot = attachments / "screenshot.png"
        if not wacz_path.exists():
            raise FileNotFoundError("Scoop did not generate a WACZ file")
        if not screenshot.exists():
            raise FileNotFoundError("Scoop did not generate a screenshot")

        source_metadata = (
            json.loads(summary_path.read_text(encoding="utf-8"))
            if summary_path.exists()
            else {"url": url}
        )
        return CaptureArtifacts(
            wacz_path=wacz_path,
            screenshot_path=screenshot,
            metadata={"capture_tool": self.name},
            source_metadata=source_metadata,
            capture_report={"actions": [self.name], "status": "complete"},
        )


def _instagram_media_urls(summary: dict) -> list[str]:
    """Select original post media, excluding thumbnails and recommended posts."""
    return sorted(
        {
            url
            for url in summary.get("exchangeUrls", [])
            if isinstance(url, str) and "ig_cache_key=" in url and "_nc_sid=58cdad" in url
        }
    )


def _media_key(url: str) -> str:
    return Path(urlsplit(url).path).name


def _free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def _merge_wacz(inputs: list[Path], output: Path) -> None:
    """Add only missing carousel response records to the primary Scoop WACZ."""
    with ZipFile(inputs[0]) as primary:
        datapackage = json.loads(primary.read("datapackage.json"))
        index_name = next(name for name in primary.namelist() if name.endswith(".cdx"))
        index_lines = primary.read(index_name).splitlines()
        pages_name = next(name for name in primary.namelist() if name.endswith("pages.jsonl"))
        pages_data = primary.read(pages_name)
        warc_name = next(name for name in primary.namelist() if name.endswith(".warc.gz"))
        primary_warc = primary.read(warc_name)

    seen = {
        _media_key(entry["url"])
        for line in index_lines
        if (entry := _cdx_entry(line)) and _is_instagram_media(entry.get("url"))
    }
    supplement = bytearray()
    for path in inputs[1:]:
        with ZipFile(path) as archive:
            index_name = next(name for name in archive.namelist() if name.endswith(".cdx"))
            warc_cache: dict[str, bytes] = {}
            for line in archive.read(index_name).splitlines():
                entry = _cdx_entry(line)
                if not entry or not _is_instagram_media(entry.get("url")):
                    continue
                key = _media_key(entry["url"])
                if key in seen:
                    continue
                filename = entry["filename"]
                warc = warc_cache.setdefault(filename, archive.read(f"archive/{filename}"))
                offset, length = int(entry["offset"]), int(entry["length"])
                record = warc[offset : offset + length]
                entry.update(
                    filename="carousel.warc.gz",
                    offset=str(len(supplement)),
                    length=str(len(record)),
                )
                prefix = line.rpartition(b" {")[0]
                index_lines.append(
                    prefix + b" " + json.dumps(entry, separators=(",", ":")).encode("utf-8")
                )
                supplement.extend(record)
                seen.add(key)

    resources = {
        "indexes/index.cdx": b"\n".join(sorted(set(index_lines))) + b"\n",
        "pages/pages.jsonl": pages_data,
        "archive/data.warc.gz": primary_warc,
    }
    if supplement:
        resources["archive/carousel.warc.gz"] = bytes(supplement)
    datapackage["resources"] = [
        {
            "name": Path(path).name,
            "path": path,
            "hash": f"sha256:{hashlib.sha256(data).hexdigest()}",
            "bytes": len(data),
        }
        for path, data in resources.items()
    ]
    datapackage_data = json.dumps(datapackage, indent=2, ensure_ascii=False).encode("utf-8")
    digest_data = json.dumps(
        {
            "path": "datapackage.json",
            "hash": f"sha256:{hashlib.sha256(datapackage_data).hexdigest()}",
        },
        indent=2,
    ).encode("utf-8")

    with ZipFile(output, "w", compression=ZIP_STORED) as archive:
        for path, data in resources.items():
            archive.writestr(path, data)
        archive.writestr("datapackage.json", datapackage_data)
        archive.writestr("datapackage-digest.json", digest_data)


def _cdx_entry(line: bytes) -> dict | None:
    _prefix, separator, payload = line.rpartition(b" {")
    if not separator:
        return None
    try:
        return json.loads(b"{" + payload)
    except json.JSONDecodeError:
        return None


def _is_instagram_media(url) -> bool:
    return isinstance(url, str) and "ig_cache_key=" in url and "_nc_sid=58cdad" in url
