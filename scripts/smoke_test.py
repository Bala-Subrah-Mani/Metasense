"""Run a real local smoke test and save its actual output and exit status."""
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
output_path = LOG_DIR / f"smoke_test_{stamp}.txt"

env = os.environ.copy()
env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
command = [sys.executable, "-m", "metasense", "--config", "config/metasense.json", "--root", "."]
start = datetime.now(timezone.utc).isoformat()
completed = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
end = datetime.now(timezone.utc).isoformat()

content = [
    "MetaSense Smoke Test Evidence",
    "Evidence type: ACTUAL EXECUTION captured by this script",
    f"Timestamp start (UTC): {start}",
    f"Timestamp end (UTC): {end}",
    f"Working directory: {ROOT}",
    f"Python executable: {sys.executable}",
    f"Command: {' '.join(command)}",
    "",
    "STDOUT:",
    completed.stdout.rstrip(),
    "",
    "STDERR:",
    completed.stderr.rstrip(),
    "",
    f"Exit status: {completed.returncode}",
]
output_path.write_text("\n".join(content) + "\n", encoding="utf-8")
print("\n".join(content))
print(f"\nEvidence saved to: {output_path.relative_to(ROOT)}")
raise SystemExit(completed.returncode)
