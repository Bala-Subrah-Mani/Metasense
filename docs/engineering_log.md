# Engineering Log

| Date (UTC) | Activity | Commit / artifact | Result |
|---|---|---|---|
| 2026-10-18 | RU-05 starter package uploaded | 1c39f7d | Environment checker only; no paper processing |
| 2026-10-19 | Implemented rule-based pipeline per RU-04/RU-05 module layout | 7a77866 (`v0.2.0`) | Runs on TXT/PDF/DOCX |
| 2026-10-19 10:16 | Validation run 1 (fresh venv) | `evidence/20261019T101632Z_run1` | T-08 FAIL (1 test), D-01…D-06 found |
| 2026-10-19 10:17 | Reproduced D-07 (non-editable install) | `evidence/defect_repro/D07_non_editable_install.txt` | exit 2 |
| 2026-10-19 | Fixed D-01…D-07, added 3 regression tests | e4ec8ad (`v0.2.1`) | — |
| 2026-10-19 10:18 | Validation run 2 retest (fresh venv) | `evidence/20261019T101812Z_run2_retest` | 9 PASS, 2 MEASURED, 67/67 tests |
| 2026-10-19 | README, environment notes, issue log, AI log, meeting agenda updated | this commit | — |
| _pending_ | Run on student's own machine (I-017) | `evidence/<ts>_<os>/` | |
| _pending_ | Supervisor meeting | `docs/supervisor_meeting_RU06.md` | |
