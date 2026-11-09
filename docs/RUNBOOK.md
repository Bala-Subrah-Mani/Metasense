# MetaSense runbook (v0.2.3)

## 1. Execution pathway
```text
paper file ──► validate (type, size, signature, METASENSE_MAX_BYTES)
           ──► extract text (txt/md: stdlib · pdf: pypdf · docx: python-docx) ──► normalise
           ──► detect sections (rules) ──► split sentences (keeps line numbers)
           ──► assess 8 rubric criteria (packaged rubric.json) ──► weaknesses ──► explanations
           ──► report: stdout summary | --json | --out DIR (*.metasense.json + *.metasense.md)
Errors at any stage ──► structured error (code, stage, message), exit 1, never a traceback
```

## 2. Packaging flow
```text
source (src/, pyproject.toml, requirements.txt)
  ├─ pip install -e .            → development (tests, scripts)
  ├─ pip wheel . → *.whl          → normal install (checked by scripts/check_packaging.py)
  ├─ docker build .               → container image (python:3.12-slim, non-root user)
  └─ git tag v0.2.3 + GitHub      → release; CI runs on Linux/Windows/macOS × Py 3.10/3.13
```

## 3. Configuration map
| Setting | Where | Default |
|---|---|---|
| Input size limit | env `METASENSE_MAX_BYTES` | 20 MB |
| Rubric | `src/metasense/resources/rubric.json` or `--rubric PATH` | packaged v0.2 rubric |
| Output folder | `--out DIR` | none (stdout only) |
| Project layout checked by `doctor` | `config/project_layout.json` | — |

## 4. Routine operations
| Task | Command |
|---|---|
| Health check | `metasense doctor` |
| Analyse a paper | `metasense analyze FILE --out reports/` |
| Full test suite | `python -m pytest -q` |
| Evidence run | `python scripts/run_validation.py --label NAME` |
| Packaging check | `python scripts/check_packaging.py` |
| Repository audit | `python scripts/audit_repo.py` |
| Clean-environment pass | see `evidence/20261102_hs5_hardening/README.md` |

## 5. Evidence and versions
| Folder | Version | Meaning |
|---|---|---|
| `evidence/20261019T101632Z_run1` | v0.2.0 | first execution (failures) |
| `evidence/20261019T101812Z_run2_retest` | v0.2.1 | retest after fixes |
| `evidence/20261025T201553Z_reproduction_v021`, `20261102T161235Z_repeat3_v021` | v0.2.1 | repeats |
| `evidence/20261025T202233Z_rm08_pilot` | v0.2.1 | real-paper pilot |
| `evidence/20261102_hs5_hardening` | v0.2.2, v0.2.3 | hardening audit, clean-environment passes, friction log |

## 6. Releasing
1. Update `__version__`, `pyproject.toml`, `CHANGELOG.md`. 2. Delete any `build/` folder. 3. `python -m pytest -q` and
`python scripts/check_packaging.py`. 4. `git tag -a vX.Y.Z` and `git push origin main --tags`.
