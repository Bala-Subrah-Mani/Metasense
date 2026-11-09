from metasense.processing import assessment_engine as ae
from metasense.processing.explainability import explain
from metasense.processing.section_detector import detect_sections
from metasense.processing.weakness_detector import detect_weaknesses


def _run(text, rubric_path):
    lines = text.split("\n")
    sections, _ = detect_sections(lines)
    rubric = ae.load_rubric(rubric_path)
    sents = ae.split_sentences(lines, sections)
    results = ae.assess(sents, rubric)
    return {r.key: r for r in results}, sections, sents, rubric


def test_dataset_present_with_two_indicators_in_methodology(rubric_path):
    text = "2. Methodology\nThe dataset contains 500 papers collected from arXiv."
    res, *_ = _run(text, rubric_path)
    assert res["dataset"].status == "present"
    assert res["dataset"].evidence[0].line == 2


def test_methodology_scoped_indicator_outside_scope_is_weak(rubric_path):
    text = "1. Introduction\nWe report precision.\n2. Methods\nWe did things."
    res, *_ = _run(text, rubric_path)
    assert res["evaluation_metrics"].status == "weak"
    assert res["evaluation_metrics"].indicators_outside_scope


def test_missing_criterion_scores_zero(rubric_path):
    res, *_ = _run("2. Methods\nWe did things.", rubric_path)
    assert res["statistical_rigor"].status == "missing" and res["statistical_rigor"].score == 0


def test_references_section_is_ignored(rubric_path):
    text = "2. Methods\nWe did things.\nReferences\n[1] A study of precision and recall."
    res, *_ = _run(text, rubric_path)
    assert res["evaluation_metrics"].status == "missing"


def test_overall_score_bounds(rubric_path):
    res, *_ = _run("2. Methods\nNothing.", rubric_path)
    assert 0 <= ae.overall_score(list(res.values())) <= 100


def test_every_criterion_has_an_explanation(rubric_path):
    res, sections, sents, rubric = _run("2. Methods\nWe used various tools.", rubric_path)
    exps = explain(list(res.values()), rubric)
    assert len(exps) == len(rubric["criteria"])
    assert all(e["explanation"] for e in exps)
    assert all(e["recommendation"] for e in exps if e["status"] != "present")


def test_vague_language_and_missing_critical_are_flagged(rubric_path):
    res, sections, sents, rubric = _run("2. Methods\nWe used various tools with standard settings.", rubric_path)
    vague = ae.find_vague_language(sents, rubric)
    ws = detect_weaknesses(list(res.values()), sections, vague, 150)
    types = {w.type for w in ws}
    assert "language.vague" in types and "structure.short_methodology" in types
    assert any(w.severity == "high" and w.criterion == "C2" for w in ws)
