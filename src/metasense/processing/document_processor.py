"""Text extraction and normalization (design component: Text Extraction / Document Processor).

Supported in this baseline: plain text/Markdown (stdlib), PDF (pypdf), DOCX (python-docx).
Extraction never raises raw library exceptions to callers; failures become ExtractionError.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass, field

from ..application.validation import ValidatedInput


class ExtractionError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message}


@dataclass
class ExtractedDocument:
    text: str
    lines: list[str]
    extractor: str
    word_count: int
    warnings: list[str] = field(default_factory=list)


# pypdf logs recoverable structure problems (e.g. "EOF marker not found") to stderr; the pipeline
# reports real failures as structured errors, so keep pypdf quiet below ERROR.
logging.getLogger("pypdf").setLevel(logging.ERROR)

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_LIGATURES = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl"}


def normalize_text(raw: str) -> str:
    """Whitespace/ligature normalization that does not change wording.

    - Unicode NFC, common ligatures expanded, non-breaking spaces -> spaces
    - C0 control characters removed (keeps \\n and \\t)
    - Hyphenated line breaks joined ("evalu-\\nation" -> "evaluation")
    - Runs of spaces/tabs collapsed; >2 blank lines collapsed to one blank line
    """
    text = unicodedata.normalize("NFC", raw)
    text = _CONTROL.sub("", text)  # I-028: NUL and other C0 control bytes from math fonts
    for lig, rep in _LIGATURES.items():
        text = text.replace(lig, rep)
    text = text.replace(" ", " ").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _read_text(path) -> tuple[str, list[str]]:
    data = path.read_bytes()
    try:
        return data.decode("utf-8"), []
    except UnicodeDecodeError:
        return data.decode("latin-1"), ["Input was not valid UTF-8; decoded as Latin-1."]


def _read_pdf(path) -> tuple[str, list[str]]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # dependency problem is reported, not hidden
        raise ExtractionError("E_DEPENDENCY", "pypdf is not installed (pip install -r requirements.txt)") from exc
    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            raise ExtractionError("E_ENCRYPTED", "PDF is encrypted; password-protected files are not supported.")
        pages = [page.extract_text() or "" for page in reader.pages]
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError("E_PARSE", f"PDF could not be parsed: {type(exc).__name__}: {exc}") from exc
    warnings = []
    empty = sum(1 for p in pages if not p.strip())
    if empty:
        warnings.append(f"{empty} of {len(pages)} PDF page(s) produced no text (possibly scanned images; OCR not implemented).")
    return "\n".join(pages), warnings


def _read_docx(path) -> tuple[str, list[str]]:
    try:
        import docx  # python-docx
    except ImportError as exc:
        raise ExtractionError("E_DEPENDENCY", "python-docx is not installed (pip install -r requirements.txt)") from exc
    try:
        document = docx.Document(str(path))
    except Exception as exc:
        raise ExtractionError("E_PARSE", f"DOCX could not be parsed: {type(exc).__name__}: {exc}") from exc
    parts = [p.text for p in document.paragraphs]
    warnings = []
    if document.tables:
        warnings.append(f"{len(document.tables)} table(s) ignored; table text extraction not implemented.")
    return "\n".join(parts), warnings


_READERS = {"text": ("plain-text", _read_text), "pdf": ("pypdf", _read_pdf), "docx": ("python-docx", _read_docx)}


def extract(validated: ValidatedInput, min_words: int = 50) -> ExtractedDocument:
    name, reader = _READERS[validated.kind]
    raw, warnings = reader(validated.path)
    text = normalize_text(raw)
    words = len(text.split())
    if words == 0:
        raise ExtractionError("E_NO_TEXT", "No extractable text found in the document.")
    if words < min_words:
        warnings.append(f"Only {words} words extracted (< {min_words}); results will be unreliable.")
    return ExtractedDocument(text=text, lines=text.split("\n"), extractor=name, word_count=words, warnings=warnings)
