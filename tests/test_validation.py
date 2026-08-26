from pathlib import Path

from postpreserve.validation import validate_package


def test_validate_zip_package(tmp_path: Path):
    pkg = tmp_path / "pkg"
    (pkg / "data/web").mkdir(parents=True)
    (pkg / "data/representations").mkdir(parents=True)
    (pkg / "metadata").mkdir(parents=True)
    (pkg / "documentation").mkdir(parents=True)
    (pkg / "data/web/post.wacz").write_bytes(b"PK\x03\x04")
    (pkg / "data/representations/screenshot.png").write_bytes(b"png")
    (pkg / "metadata/metadata.json").write_text(
        '{"identifier":"PP-IG-2026-000001"}',
        encoding="utf-8",
    )
    (pkg / "metadata/source-metadata.json").write_text("{}", encoding="utf-8")
    (pkg / "metadata/capture-report.json").write_text("{}", encoding="utf-8")
    (pkg / "documentation/README.txt").write_text("x", encoding="utf-8")
    (pkg / "manifest-sha256.txt").write_text("", encoding="utf-8")
    (pkg / "package-validation.json").write_text("{}", encoding="utf-8")
    result = validate_package(pkg)
    assert "missing_files" in result
