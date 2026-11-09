"""RM-09: re-score RM-08 heading recall/precision (M3) with the extended matcher (appendix letters A-Z,
small-caps re-joined), to quantify the measurement error found in the error analysis.
Writes research/rm09_memo/results/rm08_matcher_correction.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "research" / "rm08_pilot" / "scripts"))
from analyze_pilot import same_heading  # noqa: E402
from error_analysis_spurious_headings import norm_ext  # noqa: E402

RUN = ROOT / "evidence" / "20261025T202233Z_rm08_pilot"


def same_ext(a: str, b: str) -> bool:
    wa, wb = norm_ext(a), norm_ext(b)
    k = min(4, len(wa), len(wb))
    return k > 0 and wa[:k] == wb[:k]


def main() -> int:
    gold = json.loads((ROOT / "research/rm08_pilot/labels/g1_structure.json").read_text())
    recs = {r["doc_id"]: r for r in json.loads((RUN / "run_records.json").read_text())}
    out = {}
    for cond in ("A", "C"):
        tot = m_orig = m_ext = det = tp_ext = 0
        per = {}
        for doc, g in gold.items():
            secs = (json.loads((RUN / doc / "A_cli_stdout.json").read_text())["sections"] if cond == "A"
                    else recs[doc]["C"]["sections"])
            top = [s for s in secs if s["level"] == 1 and s["label"] != "front_matter"]
            titles = [h["title"] for h in g["headings"]]
            mo = sum(any(same_heading(t, s["heading"]) for s in top) for t in titles)
            me = sum(any(same_ext(t, s["heading"]) or same_heading(t, s["heading"]) for s in top) for t in titles)
            tp = sum(any(same_ext(t, s["heading"]) or same_heading(t, s["heading"]) for t in titles) for s in top)
            tot += len(titles); m_orig += mo; m_ext += me; det += len(top); tp_ext += tp
            per[doc] = {"gold": len(titles), "matched_original": mo, "matched_extended": me}
        out[cond] = {"gold": tot, "recall_original": round(m_orig / tot, 3), "recall_extended": round(m_ext / tot, 3),
                     "matched_original": m_orig, "matched_extended": m_ext, "detected_top": det,
                     "precision_extended": round(tp_ext / det, 3), "per_document": per}
    (ROOT / "research/rm09_memo/results/rm08_matcher_correction.json").write_text(json.dumps(out, indent=2))
    for c in out:
        print(c, {k: v for k, v in out[c].items() if k != "per_document"})
        print("  changed:", {d: v for d, v in out[c]["per_document"].items() if v["matched_original"] != v["matched_extended"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
