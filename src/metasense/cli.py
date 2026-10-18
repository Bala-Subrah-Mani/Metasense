"""Command-line interface for MetaSense."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .engine import run_checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="metasense",
        description="Check MetaSense project configuration and expected directory structure."
    )
    parser.add_argument("--config", default="config/metasense.json", help="Path to JSON config.")
    parser.add_argument("--root", default=".", help="Project root directory.")
    parser.add_argument("--json", action="store_true", help="Print full JSON report.")
    parser.add_argument("--strict", action="store_true", help="Treat missing optional directories as failures.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = run_checks(Path(args.config), Path(args.root), strict=args.strict)
    except ValueError as exc:
        print(f"MetaSense error: {exc}")
        return 1
    except Exception as exc:  # Defensive CLI boundary; details remain visible for debugging.
        print(f"MetaSense unexpected error: {type(exc).__name__}: {exc}")
        return 2

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"MetaSense {report['version']} — {report['status'].upper()}")
        print(f"Root: {report['root']}")
        print(f"Checks: {report['summary']['passed']} passed, "
              f"{report['summary']['warnings']} warnings, "
              f"{report['summary']['failed']} failed "
              f"(total {report['summary']['total_checks']})")
        for check in report["checks"]:
            print(f"[{check['status'].upper():7}] {check['kind']}: {check['name']}")
    return 0 if report["status"] != "fail" else 1
