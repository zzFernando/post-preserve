from pathlib import Path
from zipfile import ZipFile

from postpreserve.wacz import validate_wacz


def test_validate_wacz(tmp_path: Path):
    wacz = tmp_path / "post.wacz"
    with ZipFile(wacz, "w") as zf:
        zf.writestr("datapackage.json", '{"name":"x"}')
    result = validate_wacz(wacz)
    assert result.valid

