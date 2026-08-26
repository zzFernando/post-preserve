from __future__ import annotations

from pathlib import Path

from .models import AppConfig


def load_default_config(path: Path | None = None) -> AppConfig:
    path = path or Path("config/default.yaml")
    text = path.read_text(encoding="utf-8")
    data = _parse_simple_yaml(text)
    capture = data.get("capture", {})
    package = data.get("package", {})
    quality = data.get("quality", {})
    identifiers = data.get("identifiers", {})
    return AppConfig(
        project_name=data.get("project", {}).get("name", "PostPreserve"),
        prefix=identifiers.get("prefix", "PP"),
        platform_codes=identifiers.get("platform_codes", {"instagram": "IG"}),
        capture=type(AppConfig().capture)(
            backend=capture.get("backend", "browsertrix"),
            timeout_seconds=int(capture.get("timeout_seconds", 180)),
            max_interactions=int(capture.get("max_interactions", 30)),
            headed=bool(capture.get("headed", False)),
        ),
        package=type(AppConfig().package)(
            checksum_algorithm=package.get("checksum_algorithm", "sha256"),
            output_format=package.get("output_format", "zip"),
        ),
        quality=type(AppConfig().quality)(
            require_wacz=bool(quality.get("require_wacz", True)),
            require_screenshot=bool(quality.get("require_screenshot", True)),
            require_valid_metadata=bool(quality.get("require_valid_metadata", True)),
        ),
    )


def _parse_simple_yaml(text: str) -> dict:
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    current = root
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        current = stack[-1][1]
        if line.endswith(":"):
            key = line[:-1].strip()
            current[key] = {}
            stack.append((indent, current[key]))
            continue
        key, value = line.split(":", 1)
        current[key.strip()] = _parse_scalar(value.strip())
    return root


def _parse_scalar(value: str):
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.isdigit():
        return int(value)
    return value.strip('"')
