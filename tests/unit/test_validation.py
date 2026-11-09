import pytest

from metasense.application.validation import ValidationError, validate_input


def test_valid_text_file_is_accepted(sample_dir):
    v = validate_input(sample_dir / "paper_complete.txt")
    assert v.kind == "text" and v.size_bytes > 0


@pytest.mark.parametrize("name,kind", [("paper_complete.pdf", "pdf"), ("paper_complete.docx", "docx")])
def test_binary_formats_are_accepted(sample_dir, name, kind):
    assert validate_input(sample_dir / name).kind == kind


@pytest.mark.parametrize("name,code", [
    ("empty.txt", "E_EMPTY"),
    ("unsupported_format.rtf", "E_UNSUPPORTED_TYPE"),
    ("renamed_text.pdf", "E_CORRUPT"),
    ("does_not_exist.txt", "E_NOT_FOUND"),
])
def test_bad_inputs_are_rejected_with_code(sample_dir, name, code):
    with pytest.raises(ValidationError) as exc:
        validate_input(sample_dir / name)
    assert exc.value.code == code
    assert exc.value.message  # human-readable message always present


def test_size_limit_is_enforced(sample_dir):
    with pytest.raises(ValidationError) as exc:
        validate_input(sample_dir / "paper_complete.txt", max_bytes=100)
    assert exc.value.code == "E_TOO_LARGE"


def test_directory_is_rejected(sample_dir):
    with pytest.raises(ValidationError) as exc:
        validate_input(sample_dir)
    assert exc.value.code == "E_NOT_A_FILE"
