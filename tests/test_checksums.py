from pathlib import Path

from postpreserve.checksums import generate_manifest


def test_manifest_deterministic(tmp_path: Path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("a", encoding="utf-8")
    b.write_text("b", encoding="utf-8")
    manifest = generate_manifest(tmp_path, [b, a])
    assert "a.txt" in manifest.splitlines()[0]
    assert "b.txt" in manifest.splitlines()[1]

