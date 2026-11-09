"""HS3 repeat check: compares the substantive output of three executions of the same procedure (v0.2.1).
Rule 1 (as originally implemented): exclude run_id, timestamp_utc, timings_ms.
Rule 2 (revised 25 Oct): additionally exclude environment (host metadata).
Also compares the T-07 and T-11 measurement outputs and the test-suite result line."""
import glob, hashlib, json, os, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
RUNS = [("19 Oct", "20261019T101812Z_run2_retest"), ("25 Oct", "20261025T201553Z_reproduction_v021"), ("02 Nov", "20261102T161235Z_repeat3_v021")]
def h(j, excl): return hashlib.sha256(json.dumps({k: v for k, v in j.items() if k not in excl}, sort_keys=True).encode()).hexdigest()[:12]
def body(p):
    t = Path(p).read_text(); return t[t.index("--- stdout ---"):t.index("--- stderr")]
out = ["# HS3 repeat/retrace comparison across three executions of v0.2.1", ""]
docs = sorted(os.listdir(ROOT / "evidence" / RUNS[0][1] / "T04_sample_outputs"))
for rule, excl in (("Rule 1", {"run_id", "timestamp_utc", "timings_ms"}), ("Rule 2", {"run_id", "timestamp_utc", "timings_ms", "environment"})):
    out.append(f"## {rule}: excluded fields {sorted(excl)}")
    agree = 0
    for d in docs:
        hs = [h(json.loads(Path(glob.glob(str(ROOT / 'evidence' / r / 'T04_sample_outputs' / d / '*.json'))[0]).read_text()), excl) for _, r in RUNS]
        same = len(set(hs)) == 1; agree += same
        out.append(f"{d:30} " + "  ".join(f"{lab}:{x}" for (lab, _), x in zip(RUNS, hs)) + f"  identical={same}")
    out.append(f"-> {agree}/{len(docs)} identical across all three runs\n")
for name in ("T07_heading_variants.txt", "T11_known_answer.txt"):
    if name.startswith("T07"):
        bs = [body(ROOT / "evidence" / r / name) for _, r in RUNS]
    else:
        bs = [(ROOT / "evidence" / r / name).read_text() for _, r in RUNS]
    out.append(f"{name}: measurement content identical across runs = {len(set(bs)) == 1}")
for _, r in RUNS:
    t = (ROOT / "evidence" / r / "T08_pytest.txt").read_text()
    m = re.findall(r"=+ (\d+ passed[^=]*) =+", t)
    env = json.loads((ROOT / "evidence" / r / "summary.json").read_text())["platform"]
    out.append(f"{r}: pytest '{m[-1].strip() if m else '?'}'  platform {env}")
print("\n".join(out))
