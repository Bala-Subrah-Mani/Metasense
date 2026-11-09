"""RM-08 step 3: run conditions A, B, B' and C on every manifest document with the FROZEN v0.2.1 reference.

Must be executed by the interpreter of a venv in which tag v0.2.1 is installed (see README in this folder):
    <frozen-venv>/bin/python research/rm08_pilot/scripts/run_pilot.py --pdfs <pdf-dir> --label rm08_pilot
Writes evidence/<UTC>_<label>/ with raw CLI outputs, reports, extracted text and run_records.json.
This script never modifies MetaSense code; it only calls it.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import metasense
from metasense.application.validation import validate_input
from metasense.application.workflow import run_pipeline
from metasense.processing.document_processor import extract
from metasense.processing.section_detector import METHODOLOGY_LABELS, detect_sections

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
BIN = Path(sys.executable).parent


def sh(cmd):
    t0 = time.perf_counter()
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr, round((time.perf_counter() - t0) * 1000, 1)


def tool_version(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return (p.stdout or p.stderr).strip().splitlines()[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdfs", required=True)
    ap.add_argument("--label", default="rm08_pilot")
    a = ap.parse_args()
    pdfs = Path(a.pdfs)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + a.label
    out = ROOT / "evidence" / run_id
    out.mkdir(parents=True)
    manifest = list(csv.DictReader((HERE / "inputs" / "manifest.csv").open(encoding="utf-8")))
    gold = json.loads((HERE / "labels" / "g1_structure.json").read_text(encoding="utf-8"))

    env = {
        "run_id": run_id, "started_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "metasense_version": metasense.__version__, "metasense_file": metasense.__file__,
        "python": platform.python_version(), "platform": platform.platform(),
        "pdftotext": tool_version(["pdftotext", "-v"]),
        "pip_freeze": subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.splitlines(),
        "git_head_of_research_scripts": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
    }
    records = []
    for row in manifest:
        doc = row["doc_id"]
        pdf = pdfs / f"{doc}.pdf"
        d = out / doc
        d.mkdir()
        rec = {"doc_id": doc, "stratum": row["stratum"]}
        sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
        rec["sha256_matches_manifest"] = sha == row["sha256"]

        # ---- Condition A: CLI as shipped (first call in a fresh process = cold timing)
        rc, so, se, ms = sh([str(BIN / "metasense"), "analyze", str(pdf), "--json", "--out", str(d / "A_reports")])
        (d / "A_cli_stdout.json").write_text(so, encoding="utf-8")
        (d / "A_cli_stderr.txt").write_text(se, encoding="utf-8")
        rec["A"] = {"exit_code": rc, "cli_wall_ms_cold": ms}
        try:
            rep = json.loads(so)
            rec["A"].update({"status": rep["status"], "error": rep.get("error"),
                             "pipeline_total_ms": rep.get("timings_ms", {}).get("total")})
        except json.JSONDecodeError:
            rec["A"].update({"status": "unparseable_output"})
        # extracted lines exactly as the pipeline sees them (for audits)
        try:
            ex = extract(validate_input(pdf))
            (d / "A_extracted_pypdf.txt").write_text(ex.text, encoding="utf-8")
        except Exception as exc:  # recorded, not hidden
            rec["A"]["extract_error"] = f"{type(exc).__name__}: {exc}"
        # warm in-process timings
        warm = []
        for _ in range(3):
            warm.append(run_pipeline(pdf)["timings_ms"]["total"])
        rec["A"]["pipeline_ms_warm"] = warm

        # ---- Condition B (protocol): pdftotext -layout ; B2 (sensitivity, DEV-03): pdftotext default reading order
        for cond, flags in (("B", ["-layout"]), ("B2", [])):
            txt = d / f"{cond}_pdftotext{'_layout' if flags else ''}.txt"
            rc_t, _, se_t, _ = sh(["pdftotext", *flags, "-enc", "UTF-8", str(pdf), str(txt)])
            rc, so, se, ms = sh([str(BIN / "metasense"), "analyze", str(txt), "--json"])
            (d / f"{cond}_cli_stdout.json").write_text(so, encoding="utf-8")
            rec[cond] = {"pdftotext_exit": rc_t, "exit_code": rc, "cli_wall_ms": ms}
            try:
                r = json.loads(so)
                rec[cond]["status"] = r["status"]
            except json.JSONDecodeError:
                rec[cond]["status"] = "unparseable_output"

        # ---- Condition C: oracle structure -> v0.2.1 section detector
        lines = []
        for h in gold[doc]["headings"]:
            lines += ["", f"{h['num']}. {h['title']}" if h["num"] else h["title"], "Body text of this section."]
        secs, unknown = detect_sections(lines)
        rec["C"] = {"sections": [s.to_dict() for s in secs], "unrecognized": unknown,
                    "methodology_detected": any(s.label in METHODOLOGY_LABELS for s in secs)}
        records.append(rec)
        print(f"{doc:22} A={rec['A'].get('status')}/{rec['A']['exit_code']} {rec['A']['cli_wall_ms_cold']:>7} ms  "
              f"B={rec['B']['status']} B2={rec['B2']['status']} C_meth={rec['C']['methodology_detected']}")

    env["finished_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (out / "run_environment.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
    (out / "run_records.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    shutil.copyfile(HERE / "inputs" / "manifest.csv", out / "manifest_used.csv")
    print(f"evidence: {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
