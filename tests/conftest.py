from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_dir() -> Path:
    return ROOT / "data" / "sample"


@pytest.fixture
def rubric_path() -> Path:
    return ROOT / "src" / "metasense" / "resources" / "rubric.json"
