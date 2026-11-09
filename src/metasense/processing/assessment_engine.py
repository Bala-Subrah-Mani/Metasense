"""Rubric-based assessment (design components: NLP Processor (baseline) + Assessment Engine).

For each rubric criterion the engine searches sentences for indicator patterns, records the
sentence and line number of every hit as evidence, and assigns present / weak / missing.
This is keyword/regex matching, not semantic understanding; it is the rule-based baseline
against which later NLP/transformer components will be compared.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .section_detector import METHODOLOGY_LABELS, Section

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(\[\"'])")


@dataclass
class Sentence:
    text: str
    line: int
    section_label: str
    section_heading: str


@dataclass
class Evidence:
    indicator: str
    line: int
    section: str
    quote: str


@dataclass
class CriterionResult:
    id: str
    key: str
    name: str
    status: str  # present | weak | missing
    score: int
    max_score: int
    weight: float
    critical: bool
    scope: str
    indicators_found: list[str] = field(default_factory=list)
    indicators_outside_scope: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def load_rubric(path: Path | str) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        rubric = json.load(handle)
    for crit in rubric["criteria"]:
        crit["_compiled"] = [(p, re.compile(p, re.IGNORECASE)) for p in crit["indicators"]]
    rubric["_vague"] = [(p, re.compile(p, re.IGNORECASE)) for p in rubric.get("vague_phrases", [])]
    return rubric


def split_sentences(lines: list[str], sections: list[Section]) -> list[Sentence]:
    """Split each section body into sentences, keeping the 1-based line where each starts."""
    out: list[Sentence] = []
    for sec in sections:
        first_body = sec.start_line if sec.label == "front_matter" else sec.start_line + 1
        buf, buf_line = [], None
        for ln in range(first_body, sec.end_line + 1):
            line = lines[ln - 1]
            if not line.strip():
                if buf:
                    out.extend(_flush(buf, buf_line, sec))
                buf, buf_line = [], None
                continue
            if buf_line is None:
                buf_line = ln
            buf.append((ln, line))
        if buf:
            out.extend(_flush(buf, buf_line, sec))
    return out


def _flush(buf, start_line, sec) -> list[Sentence]:
    # Join paragraph lines, remembering the char offset where each source line begins.
    text, offsets = "", []
    for ln, line in buf:
        offsets.append((len(text), ln))
        text += line + " "
    sentences, pos = [], 0
    for part in _SENT_SPLIT.split(text.strip()):
        idx = text.find(part, pos)
        pos = idx + len(part)
        line_no = start_line
        for off, ln in offsets:
            if off <= idx:
                line_no = ln
        sentences.append(Sentence(part.strip(), line_no, sec.label, sec.heading))
    return sentences


def _quote(text: str, limit: int = 220, match: re.Match | None = None) -> str:
    """Quote a sentence; if it is longer than `limit`, keep a window that contains the match (D-10)."""
    if len(text) <= limit:
        return text
    if match is None or match.end() <= limit - 1:
        return text[: limit - 1].rstrip() + "…"
    centre = (match.start() + match.end()) // 2
    start = max(0, min(centre - limit // 2, len(text) - (limit - 2)))
    end = min(len(text), start + limit - 2)
    return ("…" if start > 0 else "") + text[start:end].strip() + ("…" if end < len(text) else "")


def assess(sentences: list[Sentence], rubric: dict) -> list[CriterionResult]:
    scoring = rubric["scoring"]
    results = []
    for crit in rubric["criteria"]:
        in_scope: dict[str, Evidence] = {}
        out_scope: dict[str, Evidence] = {}
        for sent in sentences:
            if sent.section_label in ("references", "acknowledgments"):
                continue
            scoped = crit["scope"] == "document" or sent.section_label in METHODOLOGY_LABELS
            for pattern, rx in crit["_compiled"]:
                m = rx.search(sent.text)
                if m:
                    target = in_scope if scoped else out_scope
                    if pattern not in target:
                        target[pattern] = Evidence(pattern, sent.line, sent.section_heading, _quote(sent.text, match=m))
        out_only = [p for p in out_scope if p not in in_scope]
        if len(in_scope) >= crit["min_indicators"]:
            status = "present"
        elif in_scope or out_only:
            status = "weak"
        else:
            status = "missing"
        evidence, seen = [], set()
        for ev in list(in_scope.values()) + [out_scope[p] for p in out_only]:
            if (ev.line, ev.quote) in seen:  # I-021: cite each sentence once
                continue
            seen.add((ev.line, ev.quote))
            evidence.append(ev)
        results.append(CriterionResult(
            id=crit["id"], key=crit["key"], name=crit["name"], status=status,
            score=scoring[status], max_score=scoring["present"], weight=crit["weight"],
            critical=crit["critical"], scope=crit["scope"],
            indicators_found=list(in_scope), indicators_outside_scope=out_only,
            evidence=evidence[:5],
        ))
    return results


def overall_score(results: list[CriterionResult]) -> float:
    total = sum(r.weight * r.max_score for r in results)
    got = sum(r.weight * r.score for r in results)
    return round(100.0 * got / total, 1) if total else 0.0


def find_vague_language(sentences: list[Sentence], rubric: dict) -> list[Evidence]:
    hits = []
    for sent in sentences:
        if sent.section_label not in METHODOLOGY_LABELS:
            continue
        for pattern, rx in rubric["_vague"]:
            m = rx.search(sent.text)
            if m:
                hits.append(Evidence(pattern, sent.line, sent.section_heading, _quote(sent.text, match=m)))
    return hits
