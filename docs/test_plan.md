# Test Plan and Results (RU-06)

Run every check with `python scripts/run_validation.py`. Each status is computed by the script from observed output.
PASS/FAIL = pass criterion met or not. MEASURED = a measurement with no pass threshold at this stage.

| ID | Check | Pass criterion | Run 1 (v0.2.0) | Run 2 retest (v0.2.1) |
|---|---|---|---|---|
| T-01 | Python and pip versions | Python ≥ 3.10, commands succeed | PASS (3.13.16) | PASS |
| T-02 | Dependency install in a clean venv | `pip install -e . -r requirements-dev.txt` exit 0 | PASS (13 pkgs) | PASS |
| T-03 | Import, startup, toolchain doctor | `metasense version` and `doctor` exit 0, no FAIL checks | PASS (1 warning, D-05) | PASS (0 warnings) |
| T-04 | Valid samples → structured output | 5 samples: exit 0, `status: ok`, JSON+MD written | PASS | PASS |
| T-05 | Empty input | exit 1, `E_EMPTY` | PASS | PASS |
| T-06 | Unsupported / disguised type | `.rtf` → `E_UNSUPPORTED_TYPE`; text renamed `.pdf` → `E_CORRUPT` | PASS | PASS |
| T-07 | Methodology heading variants (38 labelled) | Measured; misses logged | P 1.00 / R 0.70 / F1 0.82 | unchanged (no tuning) |
| T-08 | pytest unit + integration + smoke | exit 0 | **FAIL** (63/64; D-03) | PASS (67/67) |
| T-09 | Git baseline | commit/tag recorded, clean tree | PASS (7a77866, v0.2.0) | PASS (e4ec8ad, v0.2.1) |
| T-10 | Latency + repeated-run consistency | max ≤ 60 s; 5 identical outputs per file | PASS (max 375 ms) | PASS (max 391 ms) |
| T-11 | Known-answer rubric labels (3 papers × 8 criteria) | Measured | 17/24 agree; flag P 0.70 R 0.78 | 18/24; flag P 0.75 R 1.00 |

T-01 to T-09 match the matrix proposed in RU-06 v1. T-10 and T-11 were added so that the design-review targets for processing time (≤ 60 s) and assessment consistency (≥ 95% repeated-run agreement) get an early check.

## Unit and integration coverage (67 tests)
- `tests/unit/test_validation.py`: accepted formats, 4 rejection codes, size limit, directory input
- `tests/unit/test_document_processor.py`: normalization, cross-format word counts, short-doc warning
- `tests/unit/test_section_detector.py`: synonym mapping, 5 heading styles, sub-section inheritance, unknown reporting, no false heading on numbered sentences, contiguous ranges, D-03 regression
- `tests/unit/test_assessment.py`: present/weak/missing logic, scope, references ignored, score bounds, 100% explanations, vague-language flag
- `tests/integration/test_workflow.py`: end-to-end for 3 formats, format agreement (score + labels), weak < complete, missing-heading finding, structured rejections, determinism, report writing, CLI exit codes, D-01/D-04 regressions
- `tests/smoke/test_startup.py`: imports, `python -m metasense version`, packaged rubric loads
- `tests/unit/test_toolchain_*.py`: RU-05 layout checker (retained for `doctor`)

## What these tests do NOT show
They show that the pipeline runs, rejects bad input in a controlled way, and is deterministic. They do not show
extraction or weakness-detection accuracy on real papers. Those need the curated, independently annotated dataset (I-009, I-018).
