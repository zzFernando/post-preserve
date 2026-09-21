from pathlib import Path

from postpreserve.metadata import build_metadata, validate_metadata


def test_metadata_validation(tmp_path: Path):
    meta = build_metadata(
        identifier="PP-IG-2026-000001",
        platform="instagram",
        platform_code="IG",
        original_url="https://www.instagram.com/p/EXAMPLE/",
        normalized_url="https://www.instagram.com/p/EXAMPLE/",
        source_identifier="EXAMPLE",
        shortcode="EXAMPLE",
        post_type="post",
        page_title=None,
        capture_status="complete",
        capture_tool="scoop",
        capture_tool_version=None,
        browser=None,
        browser_version=None,
    )
    errors = validate_metadata(meta, Path("schemas/metadata.schema.json"))
    assert errors == []
