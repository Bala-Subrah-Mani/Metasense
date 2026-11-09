"""RM-09 focused error analysis: why does the v0.2.1 section detector create spurious top-level headings?

Input : evidence/20261025T202233Z_rm08_pilot (A_cli_stdout.json + regenerated A_extracted_pypdf.txt per document)
Output: research/rm09_memo/results/spurious_headings_classified.csv, spurious_summary.json

A detected level-1 heading is *spurious* if it matches no G1 reference heading (same rule as the RM-08 analysis)
and is not a legitimate Abstract/References/Acknowledgments heading (which G1 omits).
Measurement correction (found during this analysis): the RM-08 matcher strips only appendix letters A-H, so real
appendix headings lettered I-Z (e.g. "M PROOF OF THEOREM 5") were counted as spurious. `matcher_miss_real_heading`
identifies these with an extended matcher (any single capital letter prefix) and they are reported separately.

Each remaining spurious heading is assigned ONE cause by deterministic rules applied in this order:
  code_comment             raw line starts with '#'  (Markdown rule fires on code comments)
  matcher_miss_real_heading matches a G1 heading once any single-letter prefix is stripped (measurement artefact)
  broken_real_heading      >= 2 alphabetic words, all belonging to one G1 heading (real heading split by extraction)
  math_or_symbol           <= 3 letters, or a math symbol, or letters < 60% of non-space characters
  running_head             ALL-CAPS, >= 2 words, repeated >= 3 times in the document (page header: authors/title)
  table_or_figure          check/cross marks, or digits >= 40% of non-space characters
  numbered_prose           starts with a number, >= 4 words incl. a lowercase word (list item / wrapped sentence)
  lower_level_heading      real sub-heading: lettered/numbered sub-section (e.g. "C.3.2.") or small-caps split ("D ETERMINISTIC")
  other_caps               remaining ALL-CAPS lines (table headers, figure labels)
  other                    anything else
The detector rule that fired is inferred from the raw line: markdown / numbered / all_caps / title_case.
"""
from __future__ import annotations

import collections
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research" / "rm08_pilot" / "scripts"))
from analyze_pilot import norm, same_heading  # noqa: E402

RUN = ROOT / "evidence" / "20261025T202233Z_rm08_pilot"
OUT = ROOT / "research" / "rm09_memo" / "results"
MATH = re.compile(r"[=≤≥∑∂ϵε×⊆·∈→−+^∥∞∫√≈≠<>|\\{}\[\]]")
NUMBERED = re.compile(r"^((?:\d+(?:\.\d+)*\.?)|(?:[IVXLC]+\.)|(?:[A-H]\.))\s+")


def norm_ext(t: str) -> list[str]:
    """Like norm() but also strips a leading single capital letter (appendix I-Z) or number,
    and re-joins letters split off by small-caps extraction ("V ARIATIONAL" -> "VARIATIONAL")."""
    t = re.sub(r"^\s*(?:[0-9]+(?:\.[0-9]+)*|[A-Z])\.?\s+", "", t)          # prefix first
    t = re.sub(r"(?<=\s)([A-Z]) (?=[A-Z]{2,})", r"\1", " " + t).strip()     # then small-caps re-join
    return norm(t)


def rule_fired(raw: str) -> str:
    s = raw.strip()
    if s.startswith("#"):
        return "markdown"
    if NUMBERED.match(s):
        return "numbered"
    if s.isupper():
        return "all_caps"
    return "title_case"


def main() -> int:
    gold = json.loads((ROOT / "research/rm08_pilot/labels/g1_structure.json").read_text())
    rows = []
    for doc in gold:
        rep = json.loads((RUN / doc / "A_cli_stdout.json").read_text())
        lines = (RUN / doc / "A_extracted_pypdf.txt").read_text(encoding="utf-8", errors="replace").split("\n")
        gold_words = [set(norm(g["title"])) for g in gold[doc]["headings"]]
        spurious = []
        for s in rep["sections"]:
            if s["level"] != 1 or s["label"] == "front_matter":
                continue
            if any(same_heading(g["title"], s["heading"]) for g in gold[doc]["headings"]):
                continue
            if s["label"] in ("abstract", "references", "acknowledgments"):
                continue
            spurious.append((s, lines[s["start_line"] - 1]))
        caps_counts = collections.Counter(s["heading"] for s, raw in spurious if raw.strip().isupper())
        for s, raw in spurious:
            text = raw.strip()
            nonspace = [c for c in text if not c.isspace()]
            letters = sum(c.isalpha() for c in nonspace)
            digits = sum(c.isdigit() for c in nonspace)
            words = norm(text)
            alpha_words = [w for w in words if re.search(r"[a-z]", w)]
            if text.startswith("#"):
                cause = "code_comment"
            elif any(norm_ext(g["title"])[:4] and norm_ext(g["title"])[:min(4, len(norm_ext(text)))] == norm_ext(text)[:4]
                     and len(norm_ext(text)) >= 2 for g in gold[doc]["headings"]):
                cause = "matcher_miss_real_heading"
            elif len(alpha_words) >= 2 and any(set(alpha_words) <= gw for gw in gold_words):
                cause = "broken_real_heading"
            elif letters <= 3 or MATH.search(text) or (nonspace and letters / len(nonspace) < 0.6):
                cause = "math_or_symbol"
            elif text.isupper() and len(text.split()) >= 2 and caps_counts[s["heading"]] >= 3:
                cause = "running_head"
            elif re.search(r"[✓✗]", text) or (nonspace and digits / len(nonspace) >= 0.4):
                cause = "table_or_figure"
            elif NUMBERED.match(text) and len(text.split()) >= 4 and re.search(r"\b[a-z]{3,}\b", text):
                cause = "numbered_prose"
            elif re.match(r"^[A-Z](\.\d+)+\.?\s", text):
                cause = "lower_level_heading"
            elif text.isupper():
                cause = "other_caps"
            else:
                cause = "other"
            rows.append({"doc_id": doc, "stratum": doc.split("-")[0], "line": s["start_line"], "raw_line": text[:120],
                         "detected_heading": s["heading"][:120], "rule_fired": rule_fired(text), "cause": cause})
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "spurious_headings_classified.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    by_cause = collections.Counter(r["cause"] for r in rows)
    by_rule = collections.Counter(r["rule_fired"] for r in rows)
    cause_rule = collections.Counter((r["cause"], r["rule_fired"]) for r in rows)
    by_stratum = collections.defaultdict(collections.Counter)
    for r in rows:
        by_stratum[r["stratum"]][r["cause"]] += 1
    summary = {"total_spurious": len(rows), "by_cause": dict(by_cause.most_common()), "by_rule": dict(by_rule.most_common()),
               "cause_x_rule": {f"{c}|{r}": n for (c, r), n in cause_rule.most_common()},
               "by_stratum": {k: dict(v) for k, v in by_stratum.items()},
               "per_document": dict(collections.Counter(r["doc_id"] for r in rows))}
    (OUT / "spurious_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
