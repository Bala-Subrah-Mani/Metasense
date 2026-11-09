"""Repository hardening audit (HS5). Read-only.

Checks:
  A1 broken relative links/paths in tracked Markdown files
  A2 Python imports in src/ and scripts/ that are not stdlib, local, or declared in requirements files
  A3 tracked files that should not be versioned (build output, caches, archives, large binaries)
  A4 files referenced by README/docs that do not exist
  A5 naming consistency (project name spelling, version strings in package vs pyproject vs CHANGELOG)
  A6 presence of hardening assets (Dockerfile, .env.example, CI workflow, LICENSE, CITATION, data notes)
  A7 git hygiene (uncommitted changes, tags, remote state is reported by the caller)
Usage: python scripts/audit_repo.py [--json out.json]
Exit code: 0 always (this is an inventory, not a gate).
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STDLIB = set(getattr(sys, "stdlib_module_names", ()))


def tracked() -> list[str]:
    return subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True).stdout.splitlines()


def main() -> int:
    files = tracked()
    findings: list[dict] = []

    def add(check, severity, item, detail):
        findings.append({"check": check, "severity": severity, "item": item, "detail": detail})

    # A1 + A4: links and backticked paths in Markdown
    link_re = re.compile(r"\[[^\]]*\]\(([^)#\s]+)\)")
    path_re = re.compile(r"`((?:src|docs|scripts|data|config|tests|evidence|research|logs|reports)/[^`*<>\s]+)`")
    for md in [f for f in files if f.endswith(".md") and not f.startswith(("docs/archive_ru05", "logs/"))]:
        text = (ROOT / md).read_text(encoding="utf-8", errors="replace")
        for target in link_re.findall(text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (ROOT / Path(md).parent / target).exists() and not (ROOT / target).exists():
                add("A1", "medium", md, f"broken link -> {target}")
        for line in text.splitlines():
          if re.search(r"Former|does not exist|withdrawn", line):
              continue  # historical references that are deliberately recorded as removed or absent
          for target in path_re.findall(line):
            t = target.rstrip(".,;:)")
            if any(ch in t for ch in "<>*{}") or "…" in t:
                continue
            if not (ROOT / t).exists() and not list(ROOT.glob(t)) and not (ROOT / Path(md).parent / t).exists():
                add("A4", "low", md, f"referenced path not found -> {t}")

    # A2: undeclared third-party imports
    declared = set()
    for req in ("requirements.txt", "requirements-dev.txt", "requirements-research.txt"):
        p = ROOT / req
        if p.exists():
            for line in p.read_text().splitlines():
                m = re.match(r"\s*([A-Za-z0-9_.\-]+)", line)
                if m and not line.strip().startswith(("#", "-r")):
                    declared.add(m.group(1).lower().replace("-", "_"))
    alias = {"docx": "python_docx", "pymupdf": "pymupdf", "fitz": "pymupdf"}
    for py in [f for f in files if f.endswith(".py") and f.startswith(("src/", "scripts/", "research/", "tests/"))]:
        try:
            tree = ast.parse((ROOT / py).read_text(encoding="utf-8"))
        except SyntaxError as exc:
            add("A2", "high", py, f"syntax error: {exc}")
            continue
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module.split(".")[0]]
            for n in names:
                if n in STDLIB or n in ("metasense", "analyze_pilot", "error_analysis_spurious_headings",
                                         "rm08_matcher_correction", "__future__"):
                    continue
                if alias.get(n, n).lower() not in declared:
                    add("A2", "medium", py, f"third-party import '{n}' not declared in requirements files")

    # A3: files that should not be tracked
    for f in files:
        size = (ROOT / f).stat().st_size if (ROOT / f).exists() else 0
        if re.search(r"(^|/)(build|dist|__pycache__|\.pytest_cache)/", f) or f.endswith((".pyc", ".egg-info")):
            add("A3", "high", f, "build/cache output is tracked")
        elif f.endswith(".zip"):
            add("A3", "medium", f, f"archive tracked in repository ({size} bytes)")
        elif size > 2_000_000:
            add("A3", "low", f, f"large file ({size} bytes)")

    # A5: naming/version consistency
    init_v = re.search(r'__version__\s*=\s*"([^"]+)"', (ROOT / "src/metasense/__init__.py").read_text()).group(1)
    py_v = re.search(r'^version\s*=\s*"([^"]+)"', (ROOT / "pyproject.toml").read_text(), re.M).group(1)
    ch = (ROOT / "CHANGELOG.md").read_text()
    if init_v != py_v:
        add("A5", "high", "version", f"__init__ {init_v} != pyproject {py_v}")
    if f"## {init_v}" not in ch:
        add("A5", "medium", "CHANGELOG.md", f"no entry for current version {init_v}")
    readme = (ROOT / "README.md").read_text()
    for wrong in ("Metasense ", "metaSense", "Meta Sense"):
        if wrong in readme:
            add("A5", "low", "README.md", f"inconsistent project name spelling '{wrong.strip()}'")
    m = re.search(r"\*\*Status[^*]*\*\*", readme)
    if m and init_v not in m.group(0):
        add("A5", "medium", "README.md", f"status line does not name current version {init_v}: {m.group(0)[:80]}")

    # A6: hardening assets
    for asset, why in {
        "Dockerfile": "container spec for clean, OS-independent runs",
        ".env.example": "configuration template (documents optional variables; no secrets)",
        ".github/workflows/ci.yml": "CI smoke test on every push",
        "LICENSE": "redistribution terms",
        "CITATION.cff": "how to cite the artifact",
        "docs/DATA.md": "data provenance and redistribution limits",
        "docs/RUNBOOK.md": "execution runbook / architecture note",
    }.items():
        if not (ROOT / asset).exists():
            add("A6", "medium" if asset != "CITATION.cff" else "low", asset, f"missing: {why}")

    # A7: git hygiene
    status = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True).stdout
    if status.strip():
        add("A7", "medium", "working tree", f"{len(status.splitlines())} uncommitted change(s)")
    tags = subprocess.run(["git", "-C", str(ROOT), "tag"], capture_output=True, text=True).stdout.split()
    if f"v{init_v}" not in tags:
        add("A7", "medium", "tags", f"no tag for current version v{init_v} (tags: {', '.join(tags) or 'none'})")
    for tag in tags:
        built = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", tag, "--", "build"],
                               capture_output=True, text=True).stdout.strip()
        if built:
            add("A7", "high", f"tag {tag}", "tag contains a build/ directory (stale-install risk, D-09)")

    counts = {s: sum(f["severity"] == s for f in findings) for s in ("high", "medium", "low")}
    print(f"Repository audit: {len(findings)} findings  (high {counts['high']}, medium {counts['medium']}, low {counts['low']})")
    for f in findings:
        print(f"  [{f['severity']:6}] {f['check']} {f['item']}: {f['detail']}")
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps({"counts": counts, "findings": findings}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
