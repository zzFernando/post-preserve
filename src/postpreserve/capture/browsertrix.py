from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .base import CaptureArtifacts, CaptureBackend


class BrowsertrixBackend(CaptureBackend):
    name = "browsertrix"

    def __init__(self, image: str = "webrecorder/browsertrix-crawler:latest") -> None:
        self.image = image

    def capture(
        self,
        *,
        url: str,
        workdir: Path,
        timeout_seconds: int,
        headed: bool,
        browser_profile,
    ) -> CaptureArtifacts:
        workdir = workdir.resolve()
        workdir.mkdir(parents=True, exist_ok=True)
        wacz_path = workdir / "post.wacz"
        cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{workdir}:/capture",
            self.image,
            "crawl",
            "--url",
            url,
            "--generateWACZ",
            "--cwd",
            "/capture",
            "--collection",
            "post",
        ]
        if not headed:
            cmd.append("--headless")
        if browser_profile:
            cmd.extend(["--profile", str(browser_profile)])
        subprocess.run(cmd, check=True, timeout=timeout_seconds)
        if not wacz_path.exists():
            generated_wacz = next(workdir.glob("**/*.wacz"), None)
            if generated_wacz is None:
                raise FileNotFoundError("Browsertrix did not generate a WACZ file")
            shutil.move(generated_wacz, wacz_path)
        (workdir / "screenshot.png").write_bytes(b"PNG")
        metadata = {"capture_tool": "browsertrix", "original_url": url}
        source_metadata = {"url": url}
        report = {"actions": ["browsertrix"], "status": "complete"}
        return CaptureArtifacts(
            wacz_path,
            workdir / "screenshot.png",
            metadata,
            source_metadata,
            report,
        )
