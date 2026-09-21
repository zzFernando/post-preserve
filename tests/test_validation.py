from pathlib import Path
from zipfile import ZipFile

from postpreserve.packaging import write_manifest
from postpreserve.validation import validate_package

VALID_PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"


def test_validate_zip_package(tmp_path: Path):
    pkg = tmp_path / "pkg"
    (pkg / "data/web").mkdir(parents=True)
    (pkg / "data/representations").mkdir(parents=True)
    (pkg / "metadata").mkdir(parents=True)
    (pkg / "documentation").mkdir(parents=True)
    with ZipFile(pkg / "data/web/post.wacz", "w") as zf:
        zf.writestr("datapackage.json", '{"name":"x"}')
        zf.writestr("archive/data.warc.gz", b"warc")
        zf.writestr(
            "pages/pages.jsonl",
            '{"url":"https://www.instagram.com/p/EXAMPLE/"}\n',
        )
    (pkg / "data/representations/screenshot.png").write_bytes(VALID_PNG)
    (pkg / "metadata/metadata.json").write_text(
        '{"identifier":"PP-IG-2026-000001",'
        '"normalized_url":"https://www.instagram.com/p/EXAMPLE/"}',
        encoding="utf-8",
    )
    (pkg / "metadata/source-metadata.json").write_text("{}", encoding="utf-8")
    (pkg / "metadata/capture-report.json").write_text("{}", encoding="utf-8")
    (pkg / "documentation/README.txt").write_text("x", encoding="utf-8")
    (pkg / "package-validation.json").write_text("{}", encoding="utf-8")
    write_manifest(pkg)
    result = validate_package(pkg)
    assert result["final_status"] == "complete"
    assert result["screenshot_valid"]


def test_validate_package_rejects_fake_png(tmp_path: Path):
    pkg = tmp_path / "pkg"
    (pkg / "data/representations").mkdir(parents=True)
    (pkg / "data/representations/screenshot.png").write_bytes(b"PNG")

    result = validate_package(pkg)

    assert not result["screenshot_valid"]
    assert result["final_status"] == "partial"
    assert "Screenshot is too small to be a valid PNG" in result["errors"]
