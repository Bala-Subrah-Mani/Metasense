import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_package_imports():
    import metasense
    from metasense.application import workflow  # noqa: F401
    from metasense.processing import assessment_engine, document_processor, section_detector  # noqa: F401
    assert metasense.__version__


def test_cli_version_runs_as_module():
    env_path = str(ROOT / "src")
    out = subprocess.run([sys.executable, "-m", "metasense", "version"], cwd=ROOT, capture_output=True, text=True,
                         env={"PYTHONPATH": env_path, "PATH": ""})
    assert out.returncode == 0 and "MetaSense" in out.stdout


def test_rubric_config_loads():
    from metasense.application.workflow import DEFAULT_RUBRIC
    from metasense.processing.assessment_engine import load_rubric
    rubric = load_rubric(str(DEFAULT_RUBRIC))
    assert len(rubric["criteria"]) == 8
