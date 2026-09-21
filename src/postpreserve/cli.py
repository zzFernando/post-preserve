from __future__ import annotations

import argparse
import json
from pathlib import Path

from .doctor import doctor
from .validation import validate_package
from .workflow import archive, inspect_wacz


def build_parser() -> argparse.ArgumentParser:
    """Build the `postpreserve` argument parser with its subcommands."""
    parser = argparse.ArgumentParser(prog="postpreserve")
    sub = parser.add_subparsers(dest="command", required=True)

    archive_p = sub.add_parser("archive")
    archive_p.add_argument("url")
    archive_p.add_argument("--output", default="./workspace/output")
    archive_p.add_argument("--timeout", type=int)
    archive_p.add_argument("--identifier")

    validate_p = sub.add_parser("validate")
    validate_p.add_argument("package")

    inspect_p = sub.add_parser("inspect")
    inspect_p.add_argument("wacz")

    sub.add_parser("doctor")
    return parser


def main(argv=None) -> int:
    """Entry point for the `postpreserve` CLI.

    Exit codes: 0 on success, 1 on failure/hard error, 2 for a partial result
    (e.g. an archive completed with validation warnings).
    """
    args = build_parser().parse_args(argv)
    if args.command == "archive":
        result = archive(
            args.url,
            Path(args.output),
            timeout=args.timeout,
            identifier=args.identifier,
        )
        print(json.dumps(result, indent=2))
        if result.get("final_status") == "complete":
            return 0
        return 1 if result.get("final_status") == "failed" else 2
    if args.command == "validate":
        print(json.dumps(validate_package(Path(args.package)), indent=2))
        return 0
    if args.command == "inspect":
        print(json.dumps(inspect_wacz(Path(args.wacz)), indent=2))
        return 0
    if args.command == "doctor":
        print(json.dumps(doctor(), indent=2))
        return 0
    return 1
