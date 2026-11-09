"""Quick smoke test: toolchain doctor + one end-to-end analysis. Saves output to logs/."""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
env = os.environ.copy()
env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
lines, worst = [f"MetaSense smoke test {stamp} (UTC)", f"Python: {sys.executable}"], 0
for cmd in (["doctor"], ["analyze", "data/sample/paper_complete.txt"]):
    full = [sys.executable, "-m", "metasense", *cmd]
    p = subprocess.run(full, cwd=ROOT, env=env, text=True, capture_output=True)
    worst = max(worst, p.returncode)
    lines += ["", "$ " + " ".join(["python", "-m", "metasense", *cmd]), p.stdout.rstrip(), p.stderr.rstrip(), f"exit {p.returncode}"]
out = LOG_DIR / f"smoke_test_{stamp}.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
print(f"\nSaved: {out.relative_to(ROOT)}")
raise SystemExit(worst)
