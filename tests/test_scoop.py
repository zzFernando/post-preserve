import json
from pathlib import Path
from zipfile import ZipFile

from postpreserve.capture.scoop import ScoopBackend

VALID_PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"


def test_capture_runs_native_scoop_with_lightweight_options(monkeypatch, tmp_path: Path):
    executable = tmp_path / "scoop"
    executable.write_text("", encoding="utf-8")
    command = []

    def fake_run(cmd, **kwargs):
        command.extend(cmd)
        output = Path(cmd[3])
        output.write_bytes(b"wacz")
        summary = Path(cmd[4])
        summary.write_text(
            json.dumps(
                {
                    "url": cmd[2],
                    "exchangeUrls": [
                        "https://instagram.example/photo.jpg?ig_cache_key=x&_nc_sid=58cdad"
                    ],
                }
            ),
            encoding="utf-8",
        )
        attachments = Path(cmd[5])
        (attachments / "screenshot.png").write_bytes(VALID_PNG)

    monkeypatch.setattr("postpreserve.capture.scoop.subprocess.run", fake_run)
    monkeypatch.setattr("postpreserve.capture.scoop._free_port", lambda: 49152)
    artifacts = ScoopBackend(executable).capture(
        url="https://www.instagram.com/p/EXAMPLE/",
        workdir=tmp_path / "work",
        timeout_seconds=30,
        headed=False,
        browser_profile=None,
    )

    assert artifacts.wacz_path.read_bytes() == b"wacz"
    assert artifacts.screenshot_path.read_bytes() == VALID_PNG
    assert command[0] == "node"
    assert command[2] == "https://www.instagram.com/p/EXAMPLE/"
    assert command[7] == "true"
    assert "docker" not in command
    assert artifacts.source_metadata["media_count_captured"] == 1


def test_capture_rejects_browser_profile(tmp_path: Path):
    try:
        ScoopBackend(tmp_path / "scoop").capture(
            url="https://www.instagram.com/p/EXAMPLE/",
            workdir=tmp_path / "work",
            timeout_seconds=30,
            headed=False,
            browser_profile=tmp_path / "profile",
        )
    except ValueError as exc:
        assert "does not support browser profiles" in str(exc)
    else:
        raise AssertionError("Expected browser profile to be rejected")


def test_workflow_keeps_only_final_zip(monkeypatch, tmp_path: Path):
    from postpreserve.capture.scoop import CaptureArtifacts
    from postpreserve.workflow import archive

    url = "https://www.instagram.com/p/EXAMPLE/"

    def fake_capture(_self, *, workdir, **_kwargs):
        wacz = workdir / "post.wacz"
        with ZipFile(wacz, "w") as zf:
            zf.writestr("datapackage.json", "{}")
            zf.writestr("archive/data.warc.gz", b"warc")
            zf.writestr("pages/pages.jsonl", json.dumps({"url": url}) + "\n")
        screenshot = workdir / "screenshot.png"
        screenshot.write_bytes(VALID_PNG)
        return CaptureArtifacts(wacz, screenshot, {}, {"url": url}, {})

    monkeypatch.setattr("postpreserve.workflow.ScoopBackend.capture", fake_capture)
    result = archive(url, tmp_path, identifier="PP-IG-2026-000001")

    assert result["final_status"] == "complete"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["PP-IG-2026-000001.zip"]
