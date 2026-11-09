import pytest

from metasense.processing.section_detector import classify_heading, detect_sections


@pytest.mark.parametrize("heading,label", [
    ("Methodology", "methodology"),
    ("Methods", "methodology"),
    ("Research Design", "methodology"),
    ("Experimental Setup", "methodology"),
    ("Experiments", "experiments"),
    ("Related Work", "related_work"),
    ("Threats to Validity", "threats_to_validity"),
    ("Proposed Framework", "unknown"),
])
def test_classify_heading(heading, label):
    assert classify_heading(heading) == label


@pytest.mark.parametrize("line", ["3. Methodology", "III. METHODOLOGY", "## Methodology", "METHODOLOGY", "3 Methodology"])
def test_heading_styles_are_detected(line):
    sections, _ = detect_sections(["", line, "We collected data."])
    assert any(s.label == "methodology" for s in sections)


def test_subsections_inherit_parent_label():
    lines = ["3. Methodology", "Intro text.", "3.1 Data Collection", "We collected 10 papers."]
    sections, unknown = detect_sections(lines)
    sub = [s for s in sections if s.heading == "Data Collection"][0]
    assert sub.label == "methodology" and sub.inherited
    assert unknown == []


def test_unknown_top_level_heading_is_reported():
    sections, unknown = detect_sections(["1. Proposed Framework", "Body text here."])
    assert unknown == ["Proposed Framework"]


def test_numbered_sentence_is_not_a_heading():
    sections, _ = detect_sections(["1. We first downloaded every repository from the mirror."])
    assert [s.label for s in sections] == ["front_matter"]


def test_line_ranges_are_contiguous():
    lines = ["Title", "", "1. Introduction", "Text.", "2. Methods", "Text.", "3. Results", "Text."]
    sections, _ = detect_sections(lines)
    for a, b in zip(sections, sections[1:]):
        assert a.end_line == b.start_line - 1
    assert sections[-1].end_line == len(lines)


def test_d03_heading_without_blank_line_is_detected():
    sections, _ = detect_sections(["2. Methods", "We did things.", "References", "[1] A paper."])
    assert [s.label for s in sections][-1] == "references"
