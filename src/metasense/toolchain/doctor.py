"""Toolchain/environment validation (`metasense doctor`).

Checks Python version, required package imports and versions, file permissions for
output folders, environment variables, and the expected project layout
(reusing the RU-05 configuration checker in config_check.py).
"""
from __future__ import annotations

import importlib
import importlib.metadata as md
import os
import platform
import sys
import tempfile
from pathlib import Path

from .config_check import run_checks

REQUIRED_PACKAGES = [("pypdf", "pypdf"), ("docx", "python-docx")]
OPTIONAL_PACKAGES = [("pytest", "pytest")]
MIN_PYTHON = (3, 10)
ENV_VARS = {"METASENSE_MAX_BYTES": "optional; positive integer, overrides the 20 MB input limit"}


def _check(name, status, detail):
    return {"name": name, "status": status, "detail": detail}


def run_doctor(root: Path) -> dict:
    checks = []
    py_ok = sys.version_info[:2] >= MIN_PYTHON
    checks.append(_check("python_version", "pass" if py_ok else "fail",
                         f"{platform.python_version()} ({sys.executable}); requires >= {'.'.join(map(str, MIN_PYTHON))}"))
    checks.append(_check("platform", "info", platform.platform()))
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    checks.append(_check("virtual_environment", "pass" if in_venv else "warn",
                         sys.prefix if in_venv else "Not running inside a virtual environment"))

    for module, dist in REQUIRED_PACKAGES + OPTIONAL_PACKAGES:
        required = (module, dist) in REQUIRED_PACKAGES
        try:
            importlib.import_module(module)
            checks.append(_check(f"import:{dist}", "pass", md.version(dist)))
        except Exception as exc:  # ImportError or broken install
            checks.append(_check(f"import:{dist}", "fail" if required else "warn", f"{type(exc).__name__}: {exc}"))

    for folder in ("reports", "evidence"):
        path = root / folder
        try:
            path.mkdir(exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path, delete=True) as fh:
                fh.write(b"ok")
            checks.append(_check(f"writable:{folder}", "pass", str(path)))
        except OSError as exc:
            checks.append(_check(f"writable:{folder}", "fail", str(exc)))

    for path in ("src/metasense/resources/rubric.json", "config/project_layout.json"):
        p = root / path
        checks.append(_check(f"readable:{path}", "pass" if p.is_file() and os.access(p, os.R_OK) else "fail", str(p)))

    for var, note in ENV_VARS.items():
        checks.append(_check(f"env:{var}", "info", f"{'set' if var in os.environ else 'not set'} — {note}"))

    layout = run_checks(root / "config" / "project_layout.json", root)
    for c in layout["checks"]:
        checks.append(_check(f"layout:{c['name']}", c["status"], c["kind"]))

    failed = sum(c["status"] == "fail" for c in checks)
    warned = sum(c["status"] == "warn" for c in checks)
    return {"status": "fail" if failed else ("warning" if warned else "pass"),
            "summary": {"failed": failed, "warnings": warned, "total": len(checks)}, "checks": checks}
