import pytest

from metasense.application.validation import validate_input
from metasense.processing.document_processor import extract, normalize_text


def test_normalize_joins_hyphenated_line_breaks_and_ligatures():
    assert normalize_text("evalu-\nation of ﬁles") == "evaluation of files"


def test_normalize_collapses_whitespace_but_keeps_paragraphs():
    out = normalize_text("a   b\t c\n\n\n\nd")
    assert out == "a b c\n\nd"


@pytest.mark.parametrize("name,extractor", [
    ("paper_complete.txt", "plain-text"),
    ("paper_complete.pdf", "pypdf"),
    ("paper_complete.docx", "python-docx"),
])
def test_all_formats_extract_same_word_count(sample_dir, name, extractor):
    doc = extract(validate_input(sample_dir / name))
    assert doc.extractor == extractor
    # Same source text in three formats should give (nearly) the same word count.
    reference = extract(validate_input(sample_dir / "paper_complete.txt")).word_count
    assert abs(doc.word_count - reference) <= reference * 0.02


def test_short_document_produces_warning(tmp_path):
    p = tmp_path / "short.txt"
    p.write_text("Methods\nWe did a thing.", encoding="utf-8")
    doc = extract(validate_input(p))
    assert any("words extracted" in w for w in doc.warnings)
