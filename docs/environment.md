# Environment Notes (updated for v0.2.3)

> v0.2.3 clean-environment passes: Python 3.10.20 and 3.13.16 on Linux, see `evidence/20261102_hs5_hardening/`.
> Windows and macOS are covered by CI once the repository is pushed (`.github/workflows/ci.yml`).


## Validated environment (evidence: `evidence/20261019T101812Z_run2_retest/T01_versions.txt`, `T02_*`)
| Item | Value |
|---|---|
| OS | Ubuntu 24.04.5 LTS, Linux 6.18 x86_64 (isolated cloud container) |
| Python | 3.13.16 (system interpreter used only to create the venv) |
| Virtual env | Fresh `python -m venv .validation-venv` per run |
| pip | 26.2.1 inside venv |
| Runtime deps | pypdf 5.1.0, python-docx 1.1.2 (+ lxml 6.1.3, typing_extensions 4.16.0 transitively) |
| Dev deps | pytest 8.3.3, reportlab 4.2.5 (sample generation only) |
| Git | 2.43.0 |
| GPU / acceleration | Not required. The rule-based baseline is CPU-only (max 391 ms for a 13,335-word PDF) |

Full frozen list: `T02_pip_freeze.txt` (13 packages).

## Not yet validated
- **Windows 10/11 and macOS** (I-017). The code uses `pathlib` and has no POSIX-only calls, and `run_validation.py` handles the `Scripts\python.exe` venv layout. This has not been run there yet. Run `python scripts/run_validation.py --label windows` and commit the evidence folder.
- Python 3.11 and 3.12 (3.10 and 3.13 are verified; CI also covers 3.10 and 3.13 only).

## Environment variables
| Variable | Required | Purpose | State |
|---|---|---|---|
| `PYTHONPATH=src` | Only when running without `pip install -e .` | Lets `python -m metasense` find the package | Documented |
| `METASENSE_MAX_BYTES` | No | Override the 20 MB input limit | Wired and validated in v0.2.2 (`E_CONFIG` on invalid values) |

There are no secrets, API keys or network calls in this baseline. `.env.example` documents the optional variables; a real `.env` must never be committed (it is in `.gitignore`).

## File access and permissions
- Reads: input file, packaged rubric (`src/metasense/resources/rubric.json`), `config/project_layout.json`.
- Writes: only the directory passed to `--out`, plus `evidence/` and `logs/` from scripts. `metasense doctor` checks that `reports/` and `evidence/` are writable.
- Input files are never modified. Their SHA-256 is recorded in each report for traceability.

## Packaging notes
- Install with `pip install -e .` for development. Non-editable `pip install .` also works from v0.2.1, after the fix for D-07 (`evidence/defect_repro/D07_*`).
- `requirements.txt` pins exact versions for reproducibility, and `pyproject.toml` declares compatible ranges.
