"""Packaging check (guards against D-09): build a wheel, install it NON-editably into a fresh venv,
and confirm that the installed CLI reports the source version and can analyse a sample.

    python scripts/check_packaging.py
Exit code 0 = pass, 1 = fail. Prints every command and its result.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd, **kw):
    print("$", " ".join(str(c) for c in cmd))
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    print((p.stdout + p.stderr).strip()[-1500:])
    return p


def main() -> int:
    expected = re.search(r'__version__\s*=\s*"([^"]+)"', (ROOT / "src/metasense/__init__.py").read_text()).group(1)
    if (ROOT / "build").exists():
        print("FAIL: a build/ directory exists in the source tree; delete it (it can leak stale code into wheels, D-09)")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # Use "python -m venv" in a subprocess, exactly like the README. venv.create() copies the interpreter
        # (symlinks=False) and, run from inside another venv on relocatable Python builds (e.g. uv's 3.10),
        # produces a venv that cannot find its standard library (found in the HS5 clean pass, I-029).
        if run([sys.executable, "-m", "venv", str(tmp / "venv")]).returncode:
            return 1
        py = tmp / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if run([py, "-m", "pip", "wheel", "--no-deps", "-w", str(tmp / "wheel"), str(ROOT)]).returncode:
            return 1
        wheel = next((tmp / "wheel").glob("metasense-*.whl"))
        if run([py, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt"), str(wheel)]).returncode:
            return 1
        exe = tmp / "venv" / ("Scripts/metasense.exe" if os.name == "nt" else "bin/metasense")
        v = run([exe, "version"], cwd=tmp)
        a = run([exe, "analyze", str(ROOT / "data/sample/paper_weak.txt")], cwd=tmp)
    ok = v.returncode == 0 and f"MetaSense {expected}" in v.stdout and a.returncode == 0
    print(f"{'PASS' if ok else 'FAIL'}: wheel {wheel.name}; expected version {expected}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
