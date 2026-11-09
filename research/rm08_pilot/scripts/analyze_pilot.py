"""RM-08 step 4: compute M1-M7 and decision rules D1-D4 from a pilot evidence folder.

    python research/rm08_pilot/scripts/analyze_pilot.py evidence/<run>_rm08_pilot
Writes <run>/analysis/{per_document.csv, headings.csv, citations.csv, summary.json, summary.md}.
Pure standard library; reads only files written by run_pilot.py plus the labels.
"""
from __future__ import annotations

import csv
import json
import re
import statistics
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
METH = {"methodology", "experiments"}


def norm(s: str) -> list[str]:
    s = unicodedata.normalize("NFKC", s).lower().replace("ﬁ", "fi")
    s = re.sub(r"^\s*(?:[0-9]+|[a-h]|[ivx]+)\.?\s+", "", s)  # leading number / letter / roman
    return re.findall(r"[a-z0-9]+", s)


def same_heading(a: str, b: str) -> bool:
    wa, wb = norm(a), norm(b)
    k = min(4, len(wa), len(wb))
    return k > 0 and wa[:k] == wb[:k]


def line_starts(lines: list[str], title: str) -> bool:
    wt = norm(title)[:4]
    if not wt:
        return False
    for ln in lines:
        wl = norm(ln)
        if wl[:len(wt)] == wt and len(ln.strip()) < 120:
            return True
    return False


def heading_scores(det: list[dict], gold: list[str]) -> dict:
    top = [s for s in det if s["label"] != "front_matter" and s["level"] == 1]
    matched_gold = [g for g in gold if any(same_heading(g, s["heading"]) for s in top)]
    true_det = [s for s in top if any(same_heading(g, s["heading"]) for g in gold)]
    return {"gold_n": len(gold), "det_top_n": len(top), "matched_gold": len(matched_gold),
            "true_det": len(true_det),
            "recall": len(matched_gold) / len(gold) if gold else None,
            "precision": len(true_det) / len(top) if top else None,
            "spurious_examples": [s["heading"] for s in top if s not in true_det][:6]}


def meth_sections(rep_sections: list[dict]) -> list[str]:
    return [s["heading"] for s in rep_sections if s["label"] in METH]


def main() -> int:
    run = Path(sys.argv[1])
    an = run / "analysis"
    an.mkdir(exist_ok=True)
    recs = json.loads((run / "run_records.json").read_text())
    gold = json.loads((HERE / "labels" / "g1_structure.json").read_text())
    g2 = {r["doc_id"]: r for r in csv.DictReader((HERE / "labels" / "methodology_labels.csv").open(encoding="utf-8"))}
    rubric_ids = [f"C{i}" for i in range(1, 9)]

    per_doc, head_rows, cite_rows = [], [], []
    for rec in recs:
        doc = rec["doc_id"]
        d = run / doc
        gtitles = [h["title"] for h in gold[doc]["headings"]]
        repA = json.loads((d / "A_cli_stdout.json").read_text())
        repB = json.loads((d / "B_cli_stdout.json").read_text())
        repB2 = json.loads((d / "B2_cli_stdout.json").read_text())
        linesA = (d / "A_extracted_pypdf.txt").read_text().split("\n")
        linesB = (d / "B_pdftotext_layout.txt").read_text(errors="replace").split("\n")
        linesB2 = (d / "B2_pdftotext.txt").read_text(errors="replace").split("\n")

        # M2 extraction fidelity
        recA = sum(line_starts(linesA, g) for g in gtitles)
        recB = sum(line_starts(linesB, g) for g in gtitles)
        recB2 = sum(line_starts(linesB2, g) for g in gtitles)
        wA = repA["extraction"]["word_count"]
        wB2 = repB2["extraction"]["word_count"]
        lig = sum(t.count(c) for t in linesA for c in "ﬁﬂﬀﬃﬄ")

        # M3 heading detection
        hs = {"A": heading_scores(repA["sections"], gtitles), "B": heading_scores(repB["sections"], gtitles),
              "B2": heading_scores(repB2["sections"], gtitles), "C": heading_scores(rec["C"]["sections"], gtitles)}
        for cond, h in hs.items():
            head_rows.append({"doc_id": doc, "condition": cond, **{k: v for k, v in h.items() if k != "spurious_examples"},
                              "spurious_examples": " | ".join(h["spurious_examples"])})

        # M4 methodology detection (paper level and section level)
        lab = g2[doc]
        g2_secs = [x.strip() for x in (lab["g2_main_sections"] + ";" + lab["g2_supporting_sections"]).split(";") if x.strip()]
        def meth(rep_secs):
            ms = meth_sections(rep_secs)
            hit = any(same_heading(m, g) for m in ms for g in g2_secs)
            return {"detected": bool(ms), "sections": ms, "matches_g2_section": hit}
        mA, mB, mB2 = meth(repA["sections"]), meth(repB["sections"]), meth(repB2["sections"])
        mC = meth(rec["C"]["sections"])

        # M5 citation integrity (condition A)
        joined = " ".join(l.strip() for l in linesA)
        sec_by_line = [(s["start_line"], s["end_line"], s["heading"]) for s in repA["sections"]]
        crit = repA["assessment"]["criteria"]
        seen = set()
        rx = json.loads((Path(sys.argv[0]).resolve().parents[3] / "src/metasense/resources/rubric.json").read_text())
        patterns = {c["id"]: c["indicators"] for c in rx["criteria"]}
        for c in crit:
            for e in c["evidence"]:
                q = e["quote"].rstrip("…").strip()
                q_present = q[:200] in joined
                start_ok = any(q[:25] in linesA[i] or linesA[i].strip()[:25] in q
                               for i in range(max(0, e["line"] - 1), min(len(linesA), e["line"] + 1)) if linesA[i].strip())
                ind_ok = re.search(e["indicator"], e["quote"], re.I) is not None
                sec = next((h for a, b, h in sec_by_line if a <= e["line"] <= b), None)
                key = (e["line"], e["quote"])
                dup = key in seen
                seen.add(key)
                cite_rows.append({"doc_id": doc, "criterion": c["id"], "indicator": e["indicator"], "line": e["line"],
                                  "quote_in_text": q_present, "line_consistent": start_ok, "indicator_matches_quote": ind_ok,
                                  "section_consistent": sec == e["section"], "duplicate_of_earlier_citation": dup,
                                  "in_references_or_appendix_flag": bool(re.search(r"^(references|bibliography)$", (e["section"] or "").strip(), re.I)),
                                  "cited_section": e["section"]})
        statuses = {c["id"]: c["status"] for c in crit}
        per_doc.append({
            "doc_id": doc, "stratum": rec["stratum"], "sha256_ok": rec["sha256_matches_manifest"],
            "A_status": rec["A"]["status"], "A_exit": rec["A"]["exit_code"], "B_status": rec["B"]["status"], "B2_status": rec["B2"]["status"],
            "A_words": wA, "B2_words": wB2, "word_ratio_A_over_B2": round(wA / wB2, 3) if wB2 else None, "ligature_chars_A": lig,
            "A_warnings": " | ".join(repA["extraction"]["warnings"]),
            "gold_source": gold[doc]["source"], "gold_top_n": len(gtitles),
            "recoverable_A": recA, "recoverable_B": recB, "recoverable_B2": recB2,
            "recall_A": hs["A"]["recall"], "recall_B": hs["B"]["recall"], "recall_B2": hs["B2"]["recall"], "recall_C": hs["C"]["recall"],
            "precision_A": hs["A"]["precision"], "det_top_A": hs["A"]["det_top_n"],
            "g2": lab["g2_label"], "g2_main": lab["g2_main_sections"],
            "meth_A": mA["detected"], "meth_A_sections": " | ".join(mA["sections"][:5]), "meth_A_matches_g2": mA["matches_g2_section"],
            "meth_B": mB["detected"], "meth_B2": mB2["detected"], "meth_C": mC["detected"], "meth_C_matches_g2": mC["matches_g2_section"],
            "unrecognized_C": " | ".join(rec["C"]["unrecognized"]),
            "score_A": repA["assessment"]["completeness_score"], **{f"A_{k}": v for k, v in statuses.items()},
            "cli_cold_ms": rec["A"]["cli_wall_ms_cold"], "pipeline_ms_cold": rec["A"]["pipeline_total_ms"],
            "pipeline_ms_warm_median": statistics.median(rec["A"]["pipeline_ms_warm"]),
        })

    def write(name, rows):
        with (an / name).open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader(); w.writerows(rows)
    write("per_document.csv", per_doc); write("headings.csv", head_rows); write("citations.csv", cite_rows)

    # ---- aggregates
    n = len(per_doc)
    ok = sum(p["A_status"] == "ok" and p["A_exit"] == 0 for p in per_doc)
    tot_gold = sum(p["gold_top_n"] for p in per_doc)
    rec_sum = {k: sum(p[f"recoverable_{k}"] for p in per_doc) for k in ("A", "B", "B2")}
    hr = {c: (sum(r["matched_gold"] for r in head_rows if r["condition"] == c),
              sum(r["true_det"] for r in head_rows if r["condition"] == c),
              sum(r["det_top_n"] for r in head_rows if r["condition"] == c)) for c in ("A", "B", "B2", "C")}
    heads = {c: {"recall": round(m / tot_gold, 3), "precision": round(t / dn, 3) if dn else None,
                 "matched": m, "gold": tot_gold, "detected_top": dn} for c, (m, t, dn) in hr.items()}
    def m4(cond, docs):
        rows = [p for p in docs if p["g2"] in ("yes", "no")]
        agree = sum((p[f"meth_{cond}"]) == (p["g2"] == "yes") for p in rows)
        return {"agree": agree, "n": len(rows)}
    emp = [p for p in per_doc if p["stratum"] in ("E1", "E2")]
    m4res = {c: {"all": m4(c, per_doc), "empirical": m4(c, emp)} for c in ("A", "B", "B2", "C")}
    sec_match = {c: sum(p[f"meth_{c}_matches_g2"] for p in per_doc if p["g2"] == "yes") for c in ("A", "C")}
    n_yes = sum(p["g2"] == "yes" for p in per_doc)
    cites = len(cite_rows)
    integ = {k: sum(r[k] for r in cite_rows) for k in ("quote_in_text", "line_consistent", "indicator_matches_quote", "section_consistent", "duplicate_of_earlier_citation")}
    all_ok = sum(r["quote_in_text"] and r["line_consistent"] and r["indicator_matches_quote"] and r["section_consistent"] for r in cite_rows)
    times_cold = [p["pipeline_ms_cold"] for p in per_doc]
    times_warm = [p["pipeline_ms_warm_median"] for p in per_doc]
    dist = {}
    for p in per_doc:
        s = p["stratum"]
        for cid in rubric_ids:
            dist.setdefault(s, {}).setdefault(p[f"A_{cid}"], 0)
            dist[s][p[f"A_{cid}"]] += 1

    D1 = ok / n >= 0.95 and all_ok / cites >= 0.99
    D2 = rec_sum["A"] / tot_gold >= 0.90
    D3 = heads["C"]["recall"] - heads["A"]["recall"]
    D4 = m4res["A"]["empirical"]["agree"] / m4res["A"]["empirical"]["n"] if m4res["A"]["empirical"]["n"] else 0
    summary = {
        "run": run.name, "documents": n,
        "M1_processing": {"ok": ok, "n": n, "rate": round(ok / n, 3)},
        "M2_extraction": {"gold_top_headings": tot_gold, "recoverable": rec_sum,
                          "rate": {k: round(v / tot_gold, 3) for k, v in rec_sum.items()},
                          "word_ratio_A_over_B2_median": statistics.median(p["word_ratio_A_over_B2"] for p in per_doc),
                          "word_ratio_range": [min(p["word_ratio_A_over_B2"] for p in per_doc), max(p["word_ratio_A_over_B2"] for p in per_doc)]},
        "M3_headings": heads,
        "M4_methodology": m4res, "M4_section_match_on_g2_yes": {**sec_match, "n_yes": n_yes},
        "M5_citations": {"n": cites, **integ, "all_checks_pass": all_ok, "rate": round(all_ok / cites, 4) if cites else None},
        "M6_latency_ms": {"cold_median": statistics.median(times_cold), "cold_max": max(times_cold),
                          "warm_median": statistics.median(times_warm), "warm_max": max(times_warm),
                          "cli_cold_max": max(p["cli_cold_ms"] for p in per_doc)},
        "M7_rubric_status_by_stratum": dist,
        "decisions": {"D1_reference_usable": D1, "D2_pypdf_adequate": D2, "D3_C_minus_A_recall": round(D3, 3),
                      "D3_attribution": "extraction/layout" if D3 >= 0.20 else "rule coverage",
                      "D4_transfer_agreement_empirical": round(D4, 3), "D4_transfers": D4 >= 0.80},
    }
    (an / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
