"""RM-09 what-if ablation on the DEVELOPMENT set (the 12 RM-08 documents; not an evaluation).
Applies candidate post-filters to v0.2.1's detected top-level headings and re-scores recall/precision
against G1 with the extended matcher. MetaSense code is not modified.
F1: keep only headings with >= 2 alphabetic words of >= 3 letters and letters >= 60% of non-space chars.
F2: F1 + drop ALL-CAPS headings that repeat >= 3 times in a document (running heads).
F3: F2, but never drop a heading the detector already mapped to a known section label (e.g. "Introduction").
"""
import json, re, sys, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))
from rm08_matcher_correction import same_ext
RUN = ROOT / "evidence" / "20261025T202233Z_rm08_pilot"

def f1(h):
    ns = [c for c in h if not c.isspace()]
    letters = sum(c.isalpha() for c in ns)
    return len(re.findall(r"[A-Za-z]{3,}", h)) >= 2 and ns and letters / len(ns) >= 0.6

gold = json.loads((ROOT / "research/rm08_pilot/labels/g1_structure.json").read_text())
res = {}
for name in ("none", "F1", "F2", "F3"):
    G = M = D = T = 0
    for doc, g in gold.items():
        secs = json.loads((RUN / doc / "A_cli_stdout.json").read_text())["sections"]
        top = [s for s in secs if s["level"] == 1 and s["label"] != "front_matter"]
        known = [s for s in top if s["label"] != "unknown"]
        if name in ("F1", "F2", "F3"):
            top = [s for s in top if f1(s["heading"]) or (name == "F3" and s["label"] != "unknown")]
        if name in ("F2", "F3"):
            cnt = collections.Counter(s["heading"] for s in top if s["heading"].isupper())
            top = [s for s in top if not (s["heading"].isupper() and cnt[s["heading"]] >= 3)
                   or (name == "F3" and s["label"] != "unknown")]
        titles = [h["title"] for h in g["headings"]]
        G += len(titles); D += len(top)
        M += sum(any(same_ext(t, s["heading"]) for s in top) for t in titles)
        T += sum(any(same_ext(t, s["heading"]) for t in titles) for s in top)
    res[name] = {"gold": G, "recall": round(M / G, 3), "matched": M, "detected": D, "precision": round(T / D, 3), "true_detected": T}
(ROOT / "research/rm09_memo/results/ablation_heading_filter.json").write_text(json.dumps(res, indent=2))
print(json.dumps(res, indent=2))
