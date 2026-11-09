"""Input validation for documents submitted to MetaSense (design component: Validation Module).

Validation runs before any parsing so that bad inputs fail fast with a stable,
machine-readable error code and a human-readable message.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt": "text", ".md": "text", ".pdf": "pdf", ".docx": "docx"}
DEFAULT_MAX_BYTES = 20 * 1024 * 1024  # 20 MB; confirm limit with supervisor (see issue log)

# Magic-number signatures used to catch renamed or corrupt files.
_PDF_MAGIC = b"%PDF-"
_ZIP_MAGIC = b"PK\x03\x04"  # .docx is a ZIP container


class ValidationError(Exception):
    """Raised when an input document is rejected. ``code`` is stable for tests and logs."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class ValidatedInput:
    path: Path
    kind: str  # "text" | "pdf" | "docx"
    size_bytes: int


ENV_MAX_BYTES = "METASENSE_MAX_BYTES"


def configured_max_bytes() -> int:
    """Size limit from METASENSE_MAX_BYTES (positive integer bytes), else the 20 MB default.

    An invalid value is a configuration error and is reported, never silently ignored (I-016).
    """
    raw = os.environ.get(ENV_MAX_BYTES, "").strip()
    if not raw:
        return DEFAULT_MAX_BYTES
    if not raw.isdigit() or int(raw) <= 0:
        raise ValidationError("E_CONFIG", f"{ENV_MAX_BYTES} must be a positive integer number of bytes, got {raw!r}.")
    return int(raw)


def validate_input(path: Path | str, max_bytes: int | None = None) -> ValidatedInput:
    """Check existence, extension, size and file signature. Returns a ValidatedInput or raises."""
    if max_bytes is None:
        max_bytes = configured_max_bytes()
    path = Path(path)
    if not path.exists():
        raise ValidationError("E_NOT_FOUND", f"Input file not found: {path}")
    if not path.is_file():
        raise ValidationError("E_NOT_A_FILE", f"Input path is not a regular file: {path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValidationError(
            "E_UNSUPPORTED_TYPE",
            f"Unsupported file type '{ext or '(none)'}'. Supported types: {supported}.",
        )

    size = path.stat().st_size
    if size == 0:
        raise ValidationError("E_EMPTY", f"Input file is empty (0 bytes): {path.name}")
    if size > max_bytes:
        raise ValidationError(
            "E_TOO_LARGE", f"Input file is {size} bytes; limit is {max_bytes} bytes."
        )

    kind = SUPPORTED_EXTENSIONS[ext]
    if not os.access(path, os.R_OK):
        raise ValidationError("E_UNREADABLE", f"Input file is not readable (permission denied): {path.name}")
    try:
        with path.open("rb") as handle:
            head = handle.read(8)
    except OSError as exc:
        raise ValidationError("E_UNREADABLE", f"Input file cannot be read: {exc}") from exc

    if kind == "pdf" and not head.startswith(_PDF_MAGIC):
        raise ValidationError("E_CORRUPT", "File has a .pdf extension but no PDF signature.")
    if kind == "docx" and not head.startswith(_ZIP_MAGIC):
        raise ValidationError("E_CORRUPT", "File has a .docx extension but is not a DOCX (ZIP) container.")

    return ValidatedInput(path=path, kind=kind, size_bytes=size)
