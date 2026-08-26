from pathlib import Path

from postpreserve.workflow import inspect_wacz


def test_inspect_missing_wacz(tmp_path: Path):
    result = inspect_wacz(tmp_path / "missing.wacz")
    assert result["size"] == 0

