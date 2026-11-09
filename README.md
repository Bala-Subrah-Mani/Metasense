# MetaSense

**Checks how completely a computer-science research paper reports its methodology.**
Give MetaSense a paper (`.pdf`, `.docx`, `.txt` or `.md`). It finds the methodology section, checks eight
reporting criteria (research objective, dataset, experimental setup, evaluation metrics, baseline, statistical
rigor, threats to validity, reproducibility) and writes a JSON and Markdown report in which every finding quotes
the line of the paper that triggered it.

| | |
|---|---|
| Version | **0.2.3** (tag `v0.2.3`), rule-based research baseline |
| Status | Runs reliably and reproducibly; **the completeness score is not yet a valid quality measure on published papers** (see [Limitations](#limitations)) |
| Author | Bala Subrah Mani Naidu, CISC 699 graduate project |
| License | MIT ([LICENSE](LICENSE)) · How to cite: [CITATION.cff](CITATION.cff) |

---

## 1. Prerequisites

| Need | Version | Notes |
|---|---|---|
| Python | **3.10 – 3.13** | 3.10.20 and 3.13.16 verified in the clean-environment pass |
| pip | any recent | comes with Python |
| Git | any | only to clone; you can also download the ZIP from GitHub |
| OS | Linux, macOS, Windows | Linux verified locally; Windows/macOS run in CI (see §7) |
| Hardware | any laptop | CPU only, < 100 MB disk, no GPU, no network after install |
| Docker (optional) | 20+ | alternative to a Python install |

No accounts, API keys or internet access are needed to run MetaSense.

## 2. Install (about 2 minutes)

**Linux / macOS**
```bash
git clone https://github.com/Bala-Subrah-Mani/Metasense.git
cd Metasense
python3 -m venv .venv
source .venv/bin/activate
pip install -e . -r requirements-dev.txt
metasense doctor          # should end with: PASS (0 failed, 0 warnings)
```

**Windows (PowerShell)**
```powershell
git clone https://github.com/Bala-Subrah-Mani/Metasense.git
cd Metasense
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e . -r requirements-dev.txt
metasense doctor
```

**Docker** (no Python needed)
```bash
docker build -t metasense:0.2.3 .
docker run --rm metasense:0.2.3 analyze /app/data/sample/paper_weak.txt
docker run --rm -v "$PWD/my_papers:/data:ro" metasense:0.2.3 analyze /data/paper.pdf
```

## 3. Run

```bash
metasense analyze data/sample/paper_weak.txt                  # summary in the terminal
metasense analyze data/sample/paper_weak.txt --json           # full JSON report to the terminal
metasense analyze data/sample/paper_weak.txt --out reports/   # writes reports/paper_weak.metasense.json and .md
metasense analyze path/to/your_paper.pdf --out reports/       # your own paper
metasense version
```

Exit codes: `0` report produced · `1` input rejected (the message gives an error code) · `2` unexpected error (please open an issue).

## 4. Expected outputs

Running the commands above on the bundled samples must give exactly these results (run IDs and times will differ):

| Command | Expected result |
|---|---|
| `metasense analyze data/sample/paper_complete.txt` | `Completeness score: 100.0/100  (present 8, weak 0, missing 0)`, exit 0 |
| `metasense analyze data/sample/paper_weak.txt` | `Completeness score: 0.0/100  (present 0, weak 0, missing 8)`, 10 weaknesses, exit 0 |
| `metasense analyze data/sample/paper_no_method_heading.txt` | `Completeness score: 68.8/100  (present 4, weak 3, missing 1)`, `methodology-related: NONE`, exit 0 |
| `metasense analyze data/sample/empty.txt` | `REJECTED at stage 'validate': [E_EMPTY] ...`, exit 1 |
| `python -m pytest -q` | `86 passed` as a normal user (`85 passed, 1 skipped` as root or on Windows, where the file-permission test cannot run) |

A report looks like this (abridged):
```json
{ "version": "0.2.3", "status": "ok",
  "input": { "file": "paper_weak.txt", "sha256": "b8487684ef0c..." },
  "methodology_detected": true,
  "assessment": { "completeness_score": 0.0, "criteria": [ { "id": "C2", "status": "missing", ... } ] },
  "weaknesses": [ { "id": "W03", "severity": "high", "summary": "Dataset / data source description: no indicator found." } ],
  "explanations": [ { "criterion": "C1", "explanation": "Rated MISSING: ...", "evidence": [], "recommendation": "State the research objective ..." } ],
  "disclaimer": "MetaSense output is AI-assisted decision support ..." }
```

## 5. Configuration

All settings are optional environment variables. A template with comments is in [`.env.example`](.env.example).

| Variable | Default | Meaning |
|---|---|---|
| `METASENSE_MAX_BYTES` | `20971520` (20 MB) | Largest accepted input. Must be a positive integer, otherwise the run stops with `E_CONFIG`. |

The rubric (criteria, indicator patterns, weights) ships inside the package at
`src/metasense/resources/rubric.json`; use `--rubric my_rubric.json` to try a modified copy.

**External interfaces / API:** none. v0.2.3 makes no network calls and stores nothing outside the `--out` folder.
If a hosted model is added later, keys will be read from environment variables only (placeholder in `.env.example`) and never committed.

## 6. Test and reproduce

```bash
python -m pytest -q                                   # 86 tests: unit, integration, smoke, hardening
python scripts/check_packaging.py                     # builds a wheel, installs it non-editably, checks the version
python scripts/run_validation.py --label mymachine    # full evidence run T-01..T-11 into evidence/<UTC>_mymachine/
python scripts/audit_repo.py                          # repository hygiene audit
```
The pipeline is deterministic: it has no random components, so identical input and version give identical
findings. `run_validation.py` checks this by running every sample five times. The only seeded step in the project is
the paper selection of the research pilot (`seed = 699`, `research/rm08_pilot/scripts/select_papers.py`).

## 7. Continuous integration

`.github/workflows/ci.yml` runs on every push: tests, `doctor`, a sample analysis and the packaging check on
Ubuntu, Windows and macOS with Python 3.10 and 3.13, plus a Docker build and in-container test run.

## 8. Data

Everything in `data/` is synthetic and safe to redistribute. The research pilot used published papers that are
**not** redistributed. Provenance, licences, re-download steps and checksums are described in [`docs/DATA.md`](docs/DATA.md).

## 9. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `metasense: command not found` | venv not active, or package not installed | `source .venv/bin/activate` (Windows: `.venv\Scripts\Activate.ps1`), then `pip install -e .` |
| `ModuleNotFoundError: No module named 'metasense'` when running `python -m metasense` | not installed | `pip install -e .`, or run from the repo root with `PYTHONPATH=src` |
| `metasense doctor` shows `WARN virtual_environment` | running outside a venv | harmless; use a venv to keep dependency versions pinned |
| PowerShell: "running scripts is disabled" on `Activate.ps1` | execution policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, or use `.venv\Scripts\activate.bat` in cmd |
| `[E_UNSUPPORTED_TYPE]` | `.doc`, `.rtf`, `.odt`… | save as `.docx` or `.pdf` |
| `[E_CORRUPT]` | file extension does not match content | re-export the file |
| `[E_ENCRYPTED]` | password-protected PDF | remove the password first |
| `[E_TOO_LARGE]` | file over 20 MB | set `METASENSE_MAX_BYTES` higher |
| `[E_CONFIG]` | `METASENSE_MAX_BYTES` is not a positive integer | fix or unset the variable |
| Very few words extracted / warning about empty pages | scanned PDF (images only) | OCR is not supported; use a born-digital PDF |
| `fatal: detected dubious ownership in repository` when cloning | the repository folder belongs to another user (shared drive, copy made with `sudo`) | `git config --global --add safe.directory <path>`, or clone from GitHub instead |
| `metasense` runs even though you have not activated the venv, or reports a different version | an older copy is installed globally and shadows the venv | `which metasense` (Windows: `where metasense`); `pip uninstall metasense` outside the venv, then activate the venv |
| `check_packaging.py`: `No module named 'encodings'` / `ensurepip ... exit status 1` | v0.2.2 only: the script created its test venv with `venv.create()`, which breaks on relocatable Python builds (e.g. uv-installed 3.10) | fixed in v0.2.3 (the script now calls `python -m venv`); upgrade with `git pull` |
| `pip install .` gives an old version | stale `build/` folder (fixed in v0.2.2) | delete `build/`, reinstall; `scripts/check_packaging.py` detects this |

## 10. Repository map

```text
src/metasense/                package: validation, extraction, section detection, rubric, weaknesses, reports, CLI
src/metasense/resources/      rubric.json (packaged)
tests/                        unit / integration / smoke / hardening tests
data/sample/                  synthetic inputs (valid and deliberately invalid)
data/annotations/             AI-drafted known-answer labels (provisional)
scripts/                      run_validation, check_packaging, audit_repo, eval_headings, make_samples
evidence/                     dated, versioned run records (see docs/RUNBOOK.md §5)
research/                     pilot protocols and analyses (hs3_pilot, rm08_pilot, rm09_memo)
docs/                         RUNBOOK, DATA, environment, test plan, issue log, AI usage log
Dockerfile, .env.example, .github/workflows/ci.yml, CITATION.cff
```

## Limitations

MetaSense v0.2.3 is a transparent rule-based baseline. On 12 published papers it processed every file
(median 0.72 s), but its section detector produced many false headings, mostly from equations, and theory papers scored
higher than an empirical paper ([research/rm09_memo](research/rm09_memo)). **Do not use the completeness score to
judge papers.** Use the cited evidence as pointers for a human reviewer. Not yet supported: OCR, layout-aware
extraction, a web interface, and validated accuracy on independently labelled papers.
