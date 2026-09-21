from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path


def build_metadata(
    *,
    identifier: str,
    platform: str,
    platform_code: str,
    original_url: str,
    normalized_url: str,
    source_identifier: str,
    shortcode: str,
    post_type: str | None,
    page_title: str | None,
    capture_status: str,
    capture_tool: str,
    capture_tool_version: str | None,
    browser: str | None,
    browser_version: str | None,
    profile_name: str | None = None,
    profile_username: str | None = None,
    caption: str | None = None,
    publication_date: str | None = None,
    media_count_detected: int | None = None,
    media_count_captured: int | None = None,
    content_language: str | None = None,
    access_conditions: str | None = None,
    technical_notes: str | None = None,
) -> dict:
    """Assemble the metadata.json dict describing a captured post."""
    now = datetime.now(UTC).isoformat()
    return {
        "identifier": identifier,
        "platform": platform,
        "platform_code": platform_code,
        "original_url": original_url,
        "normalized_url": normalized_url,
        "source_identifier": source_identifier,
        "shortcode": shortcode,
        "post_type": post_type,
        "profile_name": profile_name,
        "profile_username": profile_username,
        "caption": caption,
        "publication_date": publication_date,
        "capture_date": now,
        "capture_started_at": now,
        "capture_finished_at": now,
        "capture_tool": capture_tool,
        "capture_tool_version": capture_tool_version,
        "browser": browser,
        "browser_version": browser_version,
        "media_count_detected": media_count_detected,
        "media_count_captured": media_count_captured,
        "content_language": content_language,
        "page_title": page_title,
        "capture_status": capture_status,
        "access_conditions": access_conditions,
        "technical_notes": technical_notes,
    }


def save_json(path: Path, payload: dict) -> None:
    """Write `payload` as pretty-printed JSON, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate_metadata(metadata: dict, schema_path: Path) -> list[str]:
    """Check `metadata` against the JSON schema at `schema_path` and return error messages."""
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for key in schema["required"]:
        if key not in metadata:
            errors.append(f"Missing required key: {key}")
    for key, rule in schema["properties"].items():
        if key not in metadata:
            continue
        value = metadata[key]
        if value is None:
            continue
        expected = rule["type"]
        if isinstance(expected, list):
            expected = [t for t in expected if t != "null"]
            if not expected:
                continue
            expected = expected[0]
        if expected == "string" and not isinstance(value, str):
            errors.append(f"{key} must be a string")
        if expected == "integer" and not isinstance(value, int):
            errors.append(f"{key} must be an integer")
    return errors
