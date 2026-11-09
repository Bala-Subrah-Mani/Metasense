# RU-06 validation run 20261102T161235Z_repeat3_v021

- Commit under test: `e4ec8ad` (v0.2.1), tree clean: True
- Python 3.13.16 — Linux-6.18.44-fc-v185-x86_64-with-glibc2.39
- Clean venv: True

| ID | Check | Status | Observed | Evidence |
|---|---|---|---|---|
| T-01 | Python and pip versions | PASS | Python 3.13.16 on Linux 6.18.44-fc-v185 | T01_versions.txt |
| T-02 | Dependency installation (clean venv) | PASS | pip exit 0; 13 packages in freeze | T02_install.txt, T02_pip_freeze.txt |
| T-03 | Package import, startup, toolchain checks | PASS | version exit 0; doctor exit 0; MetaSense doctor — PASS ({'failed': 0, 'warnings': 0, 'total': 20}) | T03_startup_doctor.txt |
| T-04 | Valid sample input -> structured output | PASS | paper_complete.txt: score 100.0, 0 weaknesses, 22.28 ms; paper_complete.pdf: score 100.0, 0 weaknesses, 111.63 ms; paper_complete.docx: score 100.0, 0 weaknesses, 67.9 ms; paper_weak.txt: score 0.0, 10 weaknesses, 14.33 ms; paper_no_method_heading.txt: score 68.8, 5 weaknesses, 14.51 ms | T04_*.txt, T04_sample_outputs/ |
| T-05 | Empty input | PASS | REJECTED at stage 'validate': [E_EMPTY] Input file is empty (0 bytes): empty.txt | T05_empty_input.txt |
| T-06 | Unsupported / disguised file type | PASS | unsupported_format.rtf -> exit 1, E_UNSUPPORTED_TYPE; renamed_text.pdf -> exit 1, E_CORRUPT | T06_*.txt |
| T-07 | Methodology heading variants | MEASURED | Precision=1.000 Recall=0.696 F1=0.821; misses logged | T07_heading_variants.txt |
| T-08 | Unit / integration / smoke tests | PASS | 67 passed in 0.56s | T08_pytest.txt, T08_junit.xml |
| T-09 | Git baseline | PASS | commit e4ec8ad (v0.2.1); working tree clean at start of run | T09_git_baseline.txt |
| T-10 | Processing time and repeated-run consistency | PASS | max 331.8 ms (target <= 60 s); identical output across 5 runs: True; long PDF 13335 words | T10_performance_consistency.txt |
| T-11 | Known-answer check on sample papers | MEASURED | agreement 18/24; flag precision 0.75, recall 1.00 | T11_known_answer.txt |
