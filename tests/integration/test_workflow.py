import json

import pytest

from metasense.application.workflow import run_pipeline
from metasense.cli import main
from metasense.reporting.report_generator import to_markdown, write_reports


@pytest.mark.parametrize("name", ["paper_complete.txt", "paper_complete.pdf", "paper_complete.docx"])
def test_complete_paper_end_to_end(sample_dir, name):
    r = run_pipeline(sample_dir / name)
    assert r["status"] == "ok"
    assert r["methodology_detected"] is True
    assert r["assessment"]["counts"]["missing"] == 0
    assert set(r["timings_ms"]) >= {"validate", "extract", "detect_sections", "assess", "explain", "total"}


def test_formats_agree(sample_dir):
    runs = [run_pipeline(sample_dir / f"paper_complete.{e}") for e in ("txt", "pdf", "docx")]
    assert len({r["assessment"]["completeness_score"] for r in runs}) == 1
    # D-06: compare detected section labels too, not only the score (run 1 missed D-03 this way)
    labels = [[s["label"] for s in r["sections"] if s["label"] != "front_matter"] for r in runs]
    assert labels[0] == labels[1] == labels[2]


def test_weak_paper_scores_lower_than_complete(sample_dir):
    weak = run_pipeline(sample_dir / "paper_weak.txt")
    full = run_pipeline(sample_dir / "paper_complete.txt")
    assert weak["assessment"]["completeness_score"] < full["assessment"]["completeness_score"]
    assert any(w["severity"] == "high" for w in weak["weaknesses"])


def test_missing_heading_is_reported(sample_dir):
    r = run_pipeline(sample_dir / "paper_no_method_heading.txt")
    assert r["methodology_detected"] is False
    assert any(w["type"] == "structure.no_methodology_section" for w in r["weaknesses"])


@pytest.mark.parametrize("name,code", [("empty.txt", "E_EMPTY"), ("unsupported_format.rtf", "E_UNSUPPORTED_TYPE")])
def test_rejections_return_structured_error(sample_dir, name, code):
    r = run_pipeline(sample_dir / name)
    assert r["status"] == "error" and r["error"]["code"] == code and r["error"]["stage"] == "validate"


def test_repeated_runs_are_deterministic(sample_dir):
    def strip(r):
        return {k: v for k, v in r.items() if k not in ("run_id", "timestamp_utc", "timings_ms")}
    runs = [json.dumps(strip(run_pipeline(sample_dir / "paper_weak.txt")), sort_keys=True) for _ in range(5)]
    assert len(set(runs)) == 1


def test_reports_written(sample_dir, tmp_path):
    r = run_pipeline(sample_dir / "paper_weak.txt")
    jp, mp = write_reports(r, tmp_path)
    assert json.loads(jp.read_text())["status"] == "ok"
    assert "Rubric assessment" in mp.read_text()
    assert "ERROR" in to_markdown(run_pipeline(sample_dir / "empty.txt"))


def test_cli_exit_codes(sample_dir, capsys):
    assert main(["analyze", str(sample_dir / "paper_complete.txt")]) == 0
    assert main(["analyze", str(sample_dir / "empty.txt")]) == 1
    out = capsys.readouterr().out
    assert "E_EMPTY" in out


def test_d01_open_source_data_is_not_artifact_availability(sample_dir):
    r = run_pipeline(sample_dir / "paper_weak.txt")
    c8 = next(c for c in r["assessment"]["criteria"] if c["id"] == "C8")
    assert c8["status"] == "missing"


def test_d04_count_with_intervening_words_counts_as_dataset_size(rubric_path):
    from metasense.processing import assessment_engine as ae
    from metasense.processing.section_detector import detect_sections
    lines = ["2. Methods", "We selected 12 open-source Python repositories from GitHub."]
    secs, _ = detect_sections(lines)
    res = ae.assess(ae.split_sentences(lines, secs), ae.load_rubric(rubric_path))
    c2 = next(r for r in res if r.id == "C2")
    assert any("papers" in i for i in c2.indicators_found)
