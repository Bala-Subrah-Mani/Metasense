"""RU-06 early implementation validation runner.

Usage (from the repository root):
    python scripts/run_validation.py            # creates a fresh venv in .validation-venv
    python scripts/run_validation.py --no-venv  # use the current interpreter instead

Runs T-01..T-11, saves every raw output under evidence/<RUN_ID>/, and writes
summary.md / summary.json. A test's status is computed from observed output only.
Nothing in this script edits source code or "fixes" results.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "data" / "sample"
VALID = ["paper_complete.txt", "paper_complete.pdf", "paper_complete.docx",
         "paper_weak.txt", "paper_no_method_heading.txt"]


def sh(cmd, cwd=ROOT, env=None, timeout=900):
    t0 = time.perf_counter()
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr, round(time.perf_counter() - t0, 2)


def record(path: Path, title: str, cmd, rc, out, err, secs, extra: str = "") -> None:
    shown = cmd if isinstance(cmd, str) else " ".join(str(c) for c in cmd)
    path.write_text(
        f"# {title}\n# captured_utc: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n"
        f"$ {shown}\n--- stdout ---\n{out.rstrip()}\n--- stderr ---\n{err.rstrip()}\n"
        f"--- exit code: {rc}   duration: {round(secs, 2)}s ---\n{extra}", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-venv", action="store_true")
    ap.add_argument("--label", default="")
    args = ap.parse_args()

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + (f"_{args.label}" if args.label else "")
    out = ROOT / "evidence" / run_id
    out.mkdir(parents=True)
    results = {}

    def result(tid, name, status, observed, files):
        results[tid] = {"test": name, "status": status, "observed": observed, "evidence": files}
        print(f"{tid} {status:8} {name}: {observed}")

    # ---- T-09 first, so the git state reflects the code under test, before evidence is written
    git_lines = []
    for cmd in (["git", "rev-parse", "HEAD"], ["git", "describe", "--tags", "--always", "--dirty"],
                ["git", "status", "--porcelain", "--", ".", ":(exclude)evidence"], ["git", "log", "--oneline", "-8"],
                ["git", "tag", "--list"], ["git", "remote", "-v"]):
        rc, so, se, _ = sh(cmd)
        git_lines.append(f"$ {' '.join(cmd)}\n{so.rstrip()}{se.rstrip()}\n(exit {rc})\n")
    (out / "T09_git_baseline.txt").write_text("\n".join(git_lines), encoding="utf-8")
    rc, head, _, _ = sh(["git", "rev-parse", "--short", "HEAD"])
    _, dirty, _, _ = sh(["git", "status", "--porcelain", "--", ".", ":(exclude)evidence"])
    _, describe, _, _ = sh(["git", "describe", "--tags", "--always", "--dirty"])
    clean = rc == 0 and not dirty.strip()
    commit = head.strip() if rc == 0 else "unknown"

    # ---- T-01 versions
    py = sys.executable
    lines = [f"python_executable: {py}", f"python_version: {platform.python_version()}",
             f"platform: {platform.platform()}", f"machine: {platform.machine()}"]
    for cmd in ([py, "-m", "pip", "--version"], ["git", "--version"]):
        rc_, so, se, _ = sh(cmd)
        lines.append(f"{' '.join(cmd[-2:])}: {(so or se).strip()} (exit {rc_})")
    (out / "T01_versions.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    ok = sys.version_info >= (3, 10)
    result("T-01", "Python and pip versions", "PASS" if ok else "FAIL",
           f"Python {platform.python_version()} on {platform.system()} {platform.release()}", ["T01_versions.txt"])

    # ---- T-02 clean-environment dependency install
    env = os.environ.copy()
    if args.no_venv:
        runner = py
        rc, so, se, secs = sh([py, "-m", "pip", "install", "-e", ".", "-r", "requirements-dev.txt"])
        record(out / "T02_install.txt", "Install into current interpreter (--no-venv)", "pip install -e . -r requirements-dev.txt", rc, so, se, secs)
    else:
        venv = ROOT / ".validation-venv"
        shutil.rmtree(venv, ignore_errors=True)
        rc0, so0, se0, s0 = sh([py, "-m", "venv", str(venv)])
        runner = str(venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python"))
        rc, so, se, secs = sh([runner, "-m", "pip", "install", "-e", ".", "-r", "requirements-dev.txt"])
        record(out / "T02_install.txt", "Fresh venv + pip install -e . -r requirements-dev.txt",
               f"{py} -m venv .validation-venv && .validation-venv/python -m pip install -e . -r requirements-dev.txt",
               rc, so0 + so, se0 + se, s0 + secs)
        rc = rc or rc0
    _, freeze, _, _ = sh([runner, "-m", "pip", "freeze", "--all"])
    (out / "T02_pip_freeze.txt").write_text(freeze, encoding="utf-8")
    result("T-02", "Dependency installation (clean venv)" if not args.no_venv else "Dependency installation",
           "PASS" if rc == 0 else "FAIL", f"pip exit {rc}; {len(freeze.splitlines())} packages in freeze",
           ["T02_install.txt", "T02_pip_freeze.txt"])

    # ---- T-03 startup + toolchain doctor (installed console entry point)
    rc1, so1, se1, s1 = sh([runner, "-m", "metasense", "version"])
    rc2, so2, se2, s2 = sh([runner, "-m", "metasense", "doctor"])
    record(out / "T03_startup_doctor.txt", "Startup + toolchain doctor", "metasense version ; metasense doctor",
           max(rc1, rc2), so1 + "\n" + so2, se1 + se2, s1 + s2)
    status = "PASS" if rc1 == 0 and rc2 == 0 else "FAIL"
    result("T-03", "Package import, startup, toolchain checks", status,
           f"version exit {rc1}; doctor exit {rc2}; {so2.splitlines()[0] if so2 else se2.strip()[:120]}", ["T03_startup_doctor.txt"])

    # ---- T-04 valid samples end-to-end (+ JSON/MD reports)
    sample_out = out / "T04_sample_outputs"
    obs, all_ok = [], True
    for name in VALID:
        dest = sample_out / name.replace(".", "_")
        rc, so, se, secs = sh([runner, "-m", "metasense", "analyze", str(SAMPLES / name), "--out", str(dest)])
        record(out / f"T04_{name.replace('.', '_')}.txt", f"Analyze {name}", f"metasense analyze data/sample/{name} --out ...", rc, so, se, secs)
        rep = dest / f"{Path(name).stem}.metasense.json"
        data = json.loads(rep.read_text())
        good = rc == 0 and data["status"] == "ok"
        all_ok &= good
        obs.append(f"{name}: score {data['assessment']['completeness_score']}, {len(data['weaknesses'])} weaknesses, {data['timings_ms']['total']} ms")
    result("T-04", "Valid sample input -> structured output", "PASS" if all_ok else "FAIL", "; ".join(obs),
           [f"T04_*.txt", "T04_sample_outputs/"])

    # ---- T-05 empty input
    rc, so, se, secs = sh([runner, "-m", "metasense", "analyze", str(SAMPLES / "empty.txt")])
    record(out / "T05_empty_input.txt", "Empty input", "metasense analyze data/sample/empty.txt", rc, so, se, secs)
    result("T-05", "Empty input", "PASS" if rc == 1 and "E_EMPTY" in so else "FAIL", so.strip().splitlines()[-1] if so else se[:120], ["T05_empty_input.txt"])

    # ---- T-06 unsupported / corrupt type
    ok6, obs6 = True, []
    for name, code in (("unsupported_format.rtf", "E_UNSUPPORTED_TYPE"), ("renamed_text.pdf", "E_CORRUPT")):
        rc, so, se, secs = sh([runner, "-m", "metasense", "analyze", str(SAMPLES / name)])
        record(out / f"T06_{name.replace('.', '_')}.txt", f"Rejected type: {name}", f"metasense analyze data/sample/{name}", rc, so, se, secs)
        ok6 &= rc == 1 and code in so
        obs6.append(f"{name} -> exit {rc}, {code if code in so else 'UNEXPECTED'}")
    result("T-06", "Unsupported / disguised file type", "PASS" if ok6 else "FAIL", "; ".join(obs6), ["T06_*.txt"])

    # ---- T-07 heading variants
    rc, so, se, secs = sh([runner, "scripts/eval_headings.py"])
    record(out / "T07_heading_variants.txt", "Heading-variant detection (labeled set)", "python scripts/eval_headings.py", rc, so, se, secs)
    metric = next((l for l in so.splitlines() if l.startswith("Precision=")), "no metrics")
    result("T-07", "Methodology heading variants", "MEASURED" if rc == 0 else "FAIL", metric + "; misses logged", ["T07_heading_variants.txt"])

    # ---- T-08 unit/integration/smoke tests
    rc, so, se, secs = sh([runner, "-m", "pytest", "-v", "-rA", f"--junitxml={out / 'T08_junit.xml'}"])
    record(out / "T08_pytest.txt", "pytest (unit + integration + smoke)", "python -m pytest -v -rA", rc, so, se, secs)
    tail = next((l for l in reversed(so.splitlines()) if " in " in l and ("passed" in l or "failed" in l)), "no summary")
    result("T-08", "Unit / integration / smoke tests", "PASS" if rc == 0 else "FAIL", tail.strip("= "), ["T08_pytest.txt", "T08_junit.xml"])

    # ---- T-09 git
    result("T-09", "Git baseline", "PASS" if clean else "FAIL",
           f"commit {commit} ({describe.strip()}); working tree {'clean' if clean else 'DIRTY'} at start of run", ["T09_git_baseline.txt"])

    # ---- T-10 performance + repeated-run consistency (in-process, same interpreter as venv)
    perf_code = (
        "import json,sys,hashlib\n"
        "from metasense.application.workflow import run_pipeline\n"
        "res={}\n"
        "for f in sys.argv[1:]:\n"
        "  ts=[];hs=set()\n"
        "  for i in range(5):\n"
        "    r=run_pipeline(f); ts.append(r['timings_ms']['total'])\n"
        "    s={k:v for k,v in r.items() if k not in ('run_id','timestamp_utc','timings_ms')}\n"
        "    hs.add(hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest()[:16])\n"
        "  res[f.split('/')[-1]]={'words':r.get('extraction',{}).get('word_count'),'ms_runs':ts,'ms_max':max(ts),'distinct_outputs':len(hs),'output_hash':sorted(hs)}\n"
        "print(json.dumps(res,indent=2))\n")
    files = [str(SAMPLES / n) for n in VALID + ["paper_long_perf.pdf"]]
    rc, so, se, secs = sh([runner, "-c", perf_code, *files])
    record(out / "T10_performance_consistency.txt", "5 runs per sample: latency (ms) and output determinism", "python -c <perf script> <samples>", rc, so, se, secs)
    try:
        perf = json.loads(so)
        worst = max(v["ms_max"] for v in perf.values())
        consistent = all(v["distinct_outputs"] == 1 for v in perf.values())
        status = "PASS" if rc == 0 and worst < 60000 and consistent else "FAIL"
        result("T-10", "Processing time and repeated-run consistency", status,
               f"max {worst:.1f} ms (target <= 60 s); identical output across 5 runs: {consistent}; "
               f"long PDF {perf['paper_long_perf.pdf']['words']} words", ["T10_performance_consistency.txt"])
    except Exception as exc:
        result("T-10", "Processing time and repeated-run consistency", "FAIL", f"could not parse: {exc}", ["T10_performance_consistency.txt"])

    # ---- T-11 known-answer check against expected_assessments.json
    expected = json.loads((ROOT / "data" / "annotations" / "expected_assessments.json").read_text())["papers"]
    rows, agree, total = [], 0, 0
    tp = fp = fn = 0
    for paper, labels in expected.items():
        rep = json.loads((sample_out / paper.replace(".", "_") / f"{Path(paper).stem}.metasense.json").read_text())
        got = {c["id"]: c["status"] for c in rep["assessment"]["criteria"]}
        for cid, (gold, why) in labels.items():
            total += 1
            agree += got[cid] == gold
            g_flag, p_flag = gold != "present", got[cid] != "present"
            tp += g_flag and p_flag
            fp += p_flag and not g_flag
            fn += g_flag and not p_flag
            mark = "ok " if got[cid] == gold else "XX "
            rows.append(f"{mark}{paper:30} {cid} expected={gold:8} observed={got[cid]:8} | {why}")
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    summary = (f"Status agreement: {agree}/{total} ({100 * agree / total:.1f}%)\n"
               f"Weakness flag (status != present): TP={tp} FP={fp} FN={fn} precision={prec:.3f} recall={rec:.3f}\n")
    (out / "T11_known_answer.txt").write_text(summary + "\n".join(rows) + "\n", encoding="utf-8")
    result("T-11", "Known-answer check on sample papers", "MEASURED",
           f"agreement {agree}/{total}; flag precision {prec:.2f}, recall {rec:.2f}", ["T11_known_answer.txt"])

    meta = {"run_id": run_id, "commit": commit, "describe": describe.strip(), "tree_clean": clean,
            "python": platform.python_version(), "platform": platform.platform(),
            "venv": not args.no_venv, "results": results}
    (out / "summary.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    md = [f"# RU-06 validation run {run_id}", "", f"- Commit under test: `{commit}` ({describe.strip()}), tree clean: {clean}",
          f"- Python {platform.python_version()} — {platform.platform()}", f"- Clean venv: {not args.no_venv}", "",
          "| ID | Check | Status | Observed | Evidence |", "|---|---|---|---|---|"]
    for tid, r in results.items():
        md.append(f"| {tid} | {r['test']} | {r['status']} | {r['observed']} | {', '.join(r['evidence'])} |")
    (out / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nEvidence folder: {out.relative_to(ROOT)}")
    return 0 if all(r["status"] in ("PASS", "MEASURED") for r in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
