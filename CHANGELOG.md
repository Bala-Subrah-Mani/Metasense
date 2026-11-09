# Changelog

## 0.2.3 — 2026-11-02 (HS5 reproducibility fix, tag `v0.2.3`)
- Found by the clean-environment pass on Python 3.10.20: `scripts/check_packaging.py` crashed because `venv.create()`
  copies the interpreter, and a venv made that way from inside another venv on a relocatable (uv) Python could not
  find its standard library (I-029). The script now runs `python -m venv`, the same command the README uses.
- README: expected test count corrected (86 passed as a normal user; 1 test is skipped only as root/Windows);
  troubleshooting rows for `dubious ownership`, a globally installed copy shadowing the venv, and I-029.
- No change to the package code or to any score.

## 0.2.2 — 2026-11-02 (HS5 hardening release, tag `v0.2.2`)
- Fixes: `METASENSE_MAX_BYTES` now works and is validated (I-016, new code `E_CONFIG`). Evidence quotes are centred
  on the matched word (D-10). Each sentence is cited once (I-021). Control characters are stripped (I-028).
  Unreadable files report `E_UNREADABLE`. pypdf's recoverable warnings no longer reach stderr.
- Packaging: no `build/` directory in the tag (D-09); `scripts/check_packaging.py`; Dockerfile; CI on 3 OSes × 2 Pythons.
- Docs: README rewritten (prerequisites, install for 3 platforms, expected outputs, configuration, troubleshooting);
  `docs/RUNBOOK.md`, `docs/DATA.md`, `.env.example`, `CITATION.cff`, `requirements-research.txt`.
- Tests: 19 hardening tests (malformed, encrypted, non-UTF-8 and random-byte inputs; configuration errors; output fixes).
- Scores on all samples are unchanged from v0.2.1.

## 0.2.1 — 2026-10-19 (RU-06 retest baseline, tag `v0.2.1`)
Fixes for the defects found in validation run 1 (see `docs/issue_log.md`):
D-01 C8 open-source false positive · D-02 generic C3 indicator · D-03 headings without blank line
(PDF/DOCX) · D-04 dataset-size phrasing · D-05 stale layout config · D-06 weak format test ·
D-07 rubric not packaged (non-editable install crashed). Rubric v0.2-provisional.
D-08 (repo hygiene): stray `build/` directory removed after the tag.

## 0.2.0 — 2026-10-19 (RU-06 baseline, tag `v0.2.0`)
- The MetaSense processing pipeline replaces the RU-05 starter: validation, TXT/PDF/DOCX extraction,
  section detection, rubric assessment, weakness detection, explanations, JSON/MD reports.
- `metasense analyze | doctor | version` CLI.
- Synthetic sample corpus, labelled heading set, known-answer labels.
- 64 pytest tests; `scripts/run_validation.py` evidence runner (T-01…T-11).

## 0.1.0 — 2026-10-18 (RU-05 starter)
- Environment/config checker generated as a starter package. It was not the MetaSense pipeline; now retained as `doctor`.
