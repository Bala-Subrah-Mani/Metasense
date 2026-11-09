"""Command-line interface.

  metasense analyze <file> [--json] [--out DIR] [--rubric PATH]
  metasense doctor [--root DIR] [--json]
  metasense version

Exit codes: 0 success; 1 input rejected / checks failed; 2 unexpected error or bad usage.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="metasense", description="MetaSense research-methodology assessment (rule-based baseline).")
    sub = parser.add_subparsers(dest="command", required=True)

    an = sub.add_parser("analyze", help="Analyze a research paper (.txt, .md, .pdf, .docx).")
    an.add_argument("file")
    an.add_argument("--json", action="store_true", help="Print the full JSON report to stdout.")
    an.add_argument("--out", help="Directory to write <name>.metasense.json and .md reports.")
    an.add_argument("--rubric", help="Path to rubric JSON (default: config/rubric.json).")

    dr = sub.add_parser("doctor", help="Validate Python, dependencies, permissions and project layout.")
    dr.add_argument("--root", default=".")
    dr.add_argument("--json", action="store_true")

    sub.add_parser("version", help="Print version.")
    return parser


def _print_summary(report: dict) -> None:
    print(f"MetaSense {report['version']}  run {report['run_id']}  input {report['input']['file']}")
    if report["status"] != "ok":
        e = report["error"]
        print(f"REJECTED at stage '{e['stage']}': [{e['code']}] {e['message']}")
        return
    a = report["assessment"]
    print(f"Extracted {report['extraction']['word_count']} words via {report['extraction']['extractor']}")
    for w in report["extraction"]["warnings"]:
        print(f"  warning: {w}")
    meth = [s for s in report["sections"] if s["label"] in ("methodology", "experiments")]
    print(f"Sections: {len(report['sections'])}  methodology-related: "
          + (", ".join(f"'{s['heading']}' (line {s['start_line']})" for s in meth[:6]) or "NONE")
          + (f", ... (+{len(meth) - 6} more)" if len(meth) > 6 else ""))
    if report["unrecognized_headings"]:
        print(f"Unrecognized headings: {report['unrecognized_headings']}")
    print(f"Completeness score: {a['completeness_score']}/100  "
          f"(present {a['counts']['present']}, weak {a['counts']['weak']}, missing {a['counts']['missing']})")
    for c in a["criteria"]:
        print(f"  [{c['status'].upper():7}] {c['id']} {c['name']}")
    print(f"Weaknesses: {len(report['weaknesses'])}")
    for w in report["weaknesses"]:
        print(f"  {w['id']} [{w['severity']}] {w['summary']}")
    print(f"Processing time: {report['timings_ms']['total']} ms")


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "version":
            print(f"MetaSense {__version__} (Python {sys.version.split()[0]})")
            return 0
        if args.command == "doctor":
            from .toolchain.doctor import run_doctor
            result = run_doctor(Path(args.root).resolve())
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"MetaSense doctor — {result['status'].upper()} ({result['summary']})")
                for c in result["checks"]:
                    print(f"  [{c['status'].upper():5}] {c['name']}: {c['detail']}")
            return 1 if result["status"] == "fail" else 0

        from .application.workflow import run_pipeline
        from .reporting.report_generator import to_json, write_reports
        report = run_pipeline(args.file, args.rubric)
        if args.json:
            print(to_json(report))
        else:
            _print_summary(report)
        if args.out:
            jp, mp = write_reports(report, args.out)
            print(f"Reports written: {jp} ; {mp}", file=sys.stderr)
        return 0 if report["status"] == "ok" else 1
    except Exception as exc:  # CLI boundary: never show a bare traceback to users
        print(f"MetaSense unexpected error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
