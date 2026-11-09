"""HS5 hardening tests: hostile or malformed inputs, configuration errors, and the v0.2.2 output fixes."""
import io
import os
import random
import zipfile

import pytest

from metasense.application.validation import ValidationError, configured_max_bytes, validate_input
from metasense.application.workflow import run_pipeline
from metasense.cli import main
from metasense.processing import assessment_engine as ae
from metasense.processing.document_processor import normalize_text
from metasense.processing.section_detector import detect_sections


# ---------- malformed documents must give a structured error, never a traceback
def test_truncated_pdf_is_reported_not_crashed(tmp_path):
    p = tmp_path / "broken.pdf"
    p.write_bytes(b"%PDF-1.7\n1 0 obj << /Type /Catalog >>\n%% truncated here")
    r = run_pipeline(p)
    assert r["status"] in ("error", "ok")
    if r["status"] == "error":
        assert r["error"]["code"] in ("E_PARSE", "E_NO_TEXT")


def test_encrypted_pdf_is_rejected(tmp_path):
    from pypdf import PdfWriter
    w = PdfWriter()
    w.add_blank_page(width=200, height=200)
    w.encrypt(user_password="secret", owner_password="owner")
    p = tmp_path / "locked.pdf"
    with p.open("wb") as fh:
        w.write(fh)
    r = run_pipeline(p)
    assert r["status"] == "error" and r["error"]["code"] in ("E_ENCRYPTED", "E_PARSE")


def test_zip_that_is_not_docx_is_reported(tmp_path):
    p = tmp_path / "fake.docx"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("hello.txt", "not a word document")
    p.write_bytes(buf.getvalue())
    r = run_pipeline(p)
    assert r["status"] == "error" and r["error"]["code"] == "E_PARSE"


def test_non_utf8_text_is_decoded_with_warning(tmp_path):
    p = tmp_path / "latin1.txt"
    p.write_bytes(("2. Methods\nWe used 40 samples from the café dataset. " * 5).encode("latin-1"))
    r = run_pipeline(p)
    assert r["status"] == "ok"
    assert any("Latin-1" in w for w in r["extraction"]["warnings"])


@pytest.mark.parametrize("seed", range(5))
def test_random_bytes_never_crash_cli(tmp_path, seed, capsys):
    rnd = random.Random(seed)
    p = tmp_path / f"noise{seed}.txt"
    p.write_bytes(bytes(rnd.randrange(256) for _ in range(2000)))
    code = main(["analyze", str(p)])
    assert code in (0, 1)  # 2 would mean an unexpected exception reached the CLI boundary
    assert "Traceback" not in capsys.readouterr().out


# ---------- configuration
def test_env_limit_applies(tmp_path, monkeypatch):
    p = tmp_path / "a.txt"
    p.write_text("x" * 500)
    monkeypatch.setenv("METASENSE_MAX_BYTES", "100")
    with pytest.raises(ValidationError) as exc:
        validate_input(p)
    assert exc.value.code == "E_TOO_LARGE"


@pytest.mark.parametrize("bad", ["abc", "-5", "0", "1.5"])
def test_invalid_env_limit_is_a_config_error(monkeypatch, bad):
    monkeypatch.setenv("METASENSE_MAX_BYTES", bad)
    with pytest.raises(ValidationError) as exc:
        configured_max_bytes()
    assert exc.value.code == "E_CONFIG"


def test_unset_env_uses_default(monkeypatch):
    monkeypatch.delenv("METASENSE_MAX_BYTES", raising=False)
    assert configured_max_bytes() == 20 * 1024 * 1024


@pytest.mark.skipif(os.name == "nt" or os.geteuid() == 0, reason="permission bits not enforced for root/Windows")
def test_unreadable_file_is_reported(tmp_path):
    p = tmp_path / "secret.txt"
    p.write_text("text")
    p.chmod(0)
    try:
        with pytest.raises(ValidationError) as exc:
            validate_input(p)
        assert exc.value.code == "E_UNREADABLE"
    finally:
        p.chmod(0o600)


# ---------- v0.2.2 output fixes
def test_control_characters_are_removed():  # I-028
    assert normalize_text("a\x00b\x12c\td\ne") == "abc d\ne"


def _assess(lines, rubric_path):
    secs, _ = detect_sections(lines)
    return {r.id: r for r in ae.assess(ae.split_sentences(lines, secs), ae.load_rubric(rubric_path))}


def test_quote_window_shows_the_matched_word(rubric_path):  # D-10
    long = "We describe the setting in great detail " * 10 + "and we report precision for every run."
    res = _assess(["2. Methods", long], rubric_path)
    ev = res["C4"].evidence[0]
    assert "precision" in ev.quote and len(ev.quote) <= 222


def test_one_citation_per_sentence(rubric_path):  # I-021
    s = "The dataset contains 500 papers collected from arXiv under a CC BY licence."
    res = _assess(["2. Methods", s], rubric_path)
    quotes = [(e.line, e.quote) for e in res["C2"].evidence]
    assert len(quotes) == len(set(quotes)) == 1
    assert len(res["C2"].indicators_found) >= 2  # several indicators still counted
