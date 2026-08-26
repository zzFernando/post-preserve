from pathlib import Path

from postpreserve.packaging import PACKAGE_FILES, write_manifest


def test_manifest_written(tmp_path: Path):
    for rel in PACKAGE_FILES[:-2]:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")
    path = write_manifest(tmp_path)
    assert path.exists()

