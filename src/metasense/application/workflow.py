"""End-to-end orchestration of the baseline pipeline (design component: Application Layer).

validate -> extract -> detect sections -> split sentences -> assess -> detect weaknesses
-> explain -> structured result. Each stage is timed; any failure returns a structured
error result instead of a traceback, so the caller always receives a well-formed report.
"""
from __future__ import annotations

import hashlib
import platform
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .. import __version__
from ..processing import assessment_engine as ae
from ..processing.document_processor import ExtractionError, extract
from ..processing.explainability import explain
from ..processing.section_detector import detect_sections
from ..processing.weakness_detector import detect_weaknesses
from .validation import ValidationError, validate_input

from importlib import resources

# D-07 fix: the default rubric ships inside the package so non-editable installs work.
DEFAULT_RUBRIC = resources.files("metasense") / "resources" / "rubric.json"

DISCLAIMER = ("MetaSense output is AI-assisted decision support produced by a rule-based baseline. "
              "It indicates whether methodology elements are reported, not whether the research "
              "is correct. A human reviewer must verify every finding.")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_pipeline(input_path: Path | str, rubric_path: Path | str | None = None) -> dict:
    input_path = Path(input_path)
    rubric_path = Path(rubric_path) if rubric_path else Path(str(DEFAULT_RUBRIC))
    timings: dict[str, float] = {}
    report: dict = {
        "application": "MetaSense",
        "version": __version__,
        "run_id": uuid.uuid4().hex[:12],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "input": {"file": input_path.name},
        "status": "error",
    }
    t_all = time.perf_counter()

    def stage(name, fn, *args):
        t0 = time.perf_counter()
        try:
            return fn(*args)
        finally:
            timings[name] = round((time.perf_counter() - t0) * 1000, 2)

    try:
        validated = stage("validate", validate_input, input_path)
        report["input"].update({"type": validated.kind, "size_bytes": validated.size_bytes,
                                "sha256": _sha256(input_path)})
        doc = stage("extract", extract, validated)
        rubric = stage("load_rubric", ae.load_rubric, rubric_path)
        sections, unknown = stage("detect_sections", detect_sections, doc.lines)
        sentences = stage("split_sentences", ae.split_sentences, doc.lines, sections)
        results = stage("assess", ae.assess, sentences, rubric)
        vague = ae.find_vague_language(sentences, rubric)
        weaknesses = stage("detect_weaknesses", detect_weaknesses, results, sections, vague,
                           rubric.get("min_methodology_words", 150))
        explanations = stage("explain", explain, results, rubric)
    except (ValidationError, ExtractionError) as exc:
        report["error"] = {"stage": next(reversed(timings)), **exc.to_dict()}
        report["timings_ms"] = timings
        report["timings_ms"]["total"] = round((time.perf_counter() - t_all) * 1000, 2)
        return report

    counts = {s: sum(1 for r in results if r.status == s) for s in ("present", "weak", "missing")}
    report.update({
        "status": "ok",
        "extraction": {"extractor": doc.extractor, "word_count": doc.word_count,
                       "line_count": len(doc.lines), "warnings": doc.warnings},
        "rubric": {"id": rubric["rubric_id"], "version": rubric["rubric_version"]},
        "sections": [s.to_dict() for s in sections],
        "unrecognized_headings": unknown,
        "methodology_detected": any(s.label in ("methodology", "experiments") for s in sections),
        "assessment": {
            "completeness_score": ae.overall_score(results),
            "score_note": "Weighted share of rubric criteria reported (0-100). Not a quality or validity judgement.",
            "counts": counts,
            "criteria": [r.to_dict() for r in results],
        },
        "weaknesses": [w.to_dict() for w in weaknesses],
        "explanations": explanations,
        "disclaimer": DISCLAIMER,
    })
    timings["total"] = round((time.perf_counter() - t_all) * 1000, 2)
    report["timings_ms"] = timings
    return report
