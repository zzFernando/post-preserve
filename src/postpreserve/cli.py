from __future__ import annotations

import argparse
import json
from pathlib import Path

from .doctor import doctor
from .validation import validate_package
from .workflow import archive, inspect_wacz


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="postpreserve")
    sub = parser.add_subparsers(dest="command", required=True)

    archive_p = sub.add_parser("archive")
    archive_p.add_argument("url")
    archive_p.add_argument("--output", default="./workspace/output")
    archive_p.add_argument("--browser-profile")
    archive_p.add_argument("--timeout", type=int)
    archive_p.add_argument("--identifier")
    archive_p.add_argument("--headed", action="store_true")
    archive_p.add_argument("--keep-workdir", action="store_true")
    archive_p.add_argument("--log-level", default="INFO")
    archive_p.add_argument("--container-runtime")

    validate_p = sub.add_parser("validate")
    validate_p.add_argument("package")

    inspect_p = sub.add_parser("inspect")
    inspect_p.add_argument("wacz")

    doctor_p = sub.add_parser("doctor")
    doctor_p.add_argument("--browser-profile")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "archive":
        result = archive(
            args.url,
            Path(args.output),
            browser_profile=Path(args.browser_profile) if args.browser_profile else None,
            timeout=args.timeout,
            identifier=args.identifier,
            headed=args.headed,
            keep_workdir=args.keep_workdir,
            container_runtime=args.container_runtime,
        )
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "validate":
        print(json.dumps(validate_package(Path(args.package)), indent=2))
        return 0
    if args.command == "inspect":
        print(json.dumps(inspect_wacz(Path(args.wacz)), indent=2))
        return 0
    if args.command == "doctor":
        print(
            json.dumps(
                doctor(Path(args.browser_profile) if args.browser_profile else None),
                indent=2,
            )
        )
        return 0
    return 1
