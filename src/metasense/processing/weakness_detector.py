"""Weakness detection (design component: Weakness Detector).

Turns assessment results and structural signals into a list of findings with a severity.
Severity rules (baseline):
  high   - a critical criterion is missing, or no methodology section was detected
  medium - a non-critical criterion is missing, a critical criterion is weak,
           or the methodology section is very short
  low    - a non-critical criterion is weak, or vague wording appears in the methodology
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .assessment_engine import CriterionResult, Evidence
from .section_detector import Section


@dataclass
class Weakness:
    id: str
    type: str
    severity: str
    criterion: str | None
    summary: str
    evidence: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def detect_weaknesses(results: list[CriterionResult], sections: list[Section], vague: list[Evidence],
                      min_method_words: int) -> list[Weakness]:
    found: list[Weakness] = []
    n = 0

    def add(type_, severity, criterion, summary, evidence=None):
        nonlocal n
        n += 1
        found.append(Weakness(f"W{n:02d}", type_, severity, criterion, summary, evidence or []))

    method = [s for s in sections if s.label in ("methodology", "experiments")]
    if not method:
        add("structure.no_methodology_section", "high", None,
            "No methodology-related section heading was detected; criteria scoped to the methodology "
            "can only be found outside it, so they are rated 'weak' at best.")
    else:
        words = sum(s.word_count for s in method)
        if words < min_method_words:
            add("structure.short_methodology", "medium", None,
                f"Methodology-related sections contain only {words} words (< {min_method_words}).",
                [{"section": s.heading, "line": s.start_line, "words": s.word_count} for s in method])

    for r in results:
        if r.status == "missing":
            sev = "high" if r.critical else "medium"
            add("criterion.missing", sev, r.id, f"{r.name}: no indicator found.")
        elif r.status == "weak":
            sev = "medium" if r.critical else "low"
            where = " (only outside the methodology section)" if r.indicators_outside_scope and not r.indicators_found else ""
            add("criterion.weak", sev, r.id, f"{r.name}: limited reporting{where}.",
                [asdict(e) for e in r.evidence])

    if vague:
        add("language.vague", "low", None,
            f"{len(vague)} vague phrase(s) in the methodology may hide missing detail.",
            [asdict(e) for e in vague[:5]])
    return found
