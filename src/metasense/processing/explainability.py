"""Explainable feedback (design component: Explainability Module).

Every criterion receives an explanation that cites the rule applied and the evidence
(line number + quote) that triggered it, plus a recommendation when not 'present'.
Target from the design review: 100% of criteria have an explanation.
"""
from __future__ import annotations

from .assessment_engine import CriterionResult


def explain(results: list[CriterionResult], rubric: dict) -> list[dict]:
    recs = {c["id"]: c["recommendation"] for c in rubric["criteria"]}
    mins = {c["id"]: c["min_indicators"] for c in rubric["criteria"]}
    out = []
    for r in results:
        need = mins[r.id]
        scope = "the methodology section(s)" if r.scope == "methodology" else "the document"
        if r.status == "present":
            why = (f"Rated PRESENT: {len(r.indicators_found)} distinct indicator(s) found in {scope} "
                   f"(threshold {need}).")
        elif r.status == "weak":
            if r.indicators_found:
                why = (f"Rated WEAK: {len(r.indicators_found)} indicator(s) found in {scope}, "
                       f"below the threshold of {need}.")
            else:
                why = (f"Rated WEAK: indicator(s) found only outside {scope} "
                       f"({len(r.indicators_outside_scope)} found elsewhere).")
        else:
            why = f"Rated MISSING: no indicator for this criterion was found in {scope}."
        cites = [f"line {e.line} [{e.section}]: \"{e.quote}\"" for e in r.evidence[:3]]
        out.append({
            "criterion": r.id,
            "name": r.name,
            "status": r.status,
            "explanation": why,
            "evidence": cites,
            "recommendation": None if r.status == "present" else recs[r.id],
        })
    return out
