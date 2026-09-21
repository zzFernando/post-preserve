from pathlib import Path
from zipfile import ZipFile

from postpreserve.wacz import validate_wacz


def test_validate_wacz(tmp_path: Path):
    wacz = tmp_path / "post.wacz"
    with ZipFile(wacz, "w") as zf:
        zf.writestr("datapackage.json", '{"name":"x"}')
        zf.writestr("archive/data.warc.gz", b"warc")
        zf.writestr(
            "pages/pages.jsonl",
            '{"format":"json-pages-1.0"}\n'
            '{"url":"https://www.instagram.com/p/EXAMPLE/"}\n',
        )
    result = validate_wacz(wacz, "https://www.instagram.com/p/EXAMPLE/")
    assert result.valid
    assert result.urls == ["https://www.instagram.com/p/EXAMPLE/"]


def test_validate_wacz_rejects_missing_warc(tmp_path: Path):
    wacz = tmp_path / "post.wacz"
    with ZipFile(wacz, "w") as zf:
        zf.writestr("datapackage.json", '{"name":"x"}')
        zf.writestr("pages/pages.jsonl", '{"format":"json-pages-1.0"}\n')

    result = validate_wacz(wacz)

    assert not result.valid
    assert "WACZ does not contain a WARC payload" in result.errors
