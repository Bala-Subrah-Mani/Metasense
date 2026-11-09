# AI Usage Disclosure and Verification Log

## Disclosure
Generative AI tools were used during MetaSense development. The student remains responsible for
the project's technical decisions, for reviewing all AI-generated material, and for the accuracy of
what is submitted. AI was not used to fabricate results: every result reported for RU-06 comes from
the scripts in this repository and is stored in `evidence/` with timestamps and commit hashes.

| Date (UTC) | Tool | What it produced | Files / artifacts | How it was verified |
|---|---|---|---|---|
| 2026-10-18 | ChatGPT | RU-05 starter package (environment/config checker, not the MetaSense pipeline) | Former `src/metasense/checks.py`, `engine.py`, tests, templates | Its own build log only; the student never ran it. Superseded in RU-06 and kept as `metasense doctor` |
| 2026-10-11 | AI assistant (as disclosed in the RU-06 v1 report) | RU-06 v1 report text | Validation package v1 | Graded as lacking execution evidence |
| 2026-10-19 | Claude (Anthropic), agentic coding session | Rule-based pipeline code, rubric v0.1/v0.2 indicators, synthetic sample papers, labelled heading set, known-answer labels, tests, `run_validation.py`, defect fixes D-01…D-07, README/docs, draft RU-06 v2 report | All commits from `7a77866` onward (commit trailer `Co-Authored-By: Claude`) | Executed: 2 full validation runs in clean venvs (run1, run2_retest), 67 tests, D-07 reproduction/retest. See verification log below |

## Verification log (2026-10-19)
| What was checked | Method | Result | Evidence |
|---|---|---|---|
| Clean install from pinned requirements | Fresh venv + pip | exit 0 | `run2_retest/T02_install.txt` |
| Code executes end to end on TXT/PDF/DOCX | CLI on 5 samples | 5/5 `status: ok` | `run2_retest/T04_*` |
| Bad inputs handled | CLI on empty, `.rtf`, disguised `.pdf` | correct codes, exit 1 | `T05`, `T06` |
| Tests | pytest | 63/64 → 67/67 after fixes | `run1/T08_pytest.txt`, `run2_retest/T08_pytest.txt` |
| Determinism | 5 runs per file, hash of output | 1 distinct output per file | `T10_performance_consistency.txt` |
| AI-written labels are not independent | Self-review | **Not verified**: labels and rules come from the same source | Issue I-018 |

## Still to be done by the student before submission
- [ ] Read and understand every module in `src/metasense/` (be ready to explain it in the midpoint demo).
- [ ] Review `data/annotations/expected_assessments.json` and `heading_variants.csv`. Change any label you disagree with, then rerun `scripts/run_validation.py`.
- [ ] Run `python scripts/run_validation.py --label <your-os>` on your own computer and commit the evidence folder (I-017).
- [ ] Hold the supervisor meeting and complete `docs/supervisor_meeting_RU06.md`.
- [ ] Follow the course's disclosure rules. Cite Claude/ChatGPT use in the submission text as required.

## RM-08 midpoint research evidence review (2026-10-25)

Tool: Claude (Anthropic), agentic session; model configured as `claude-opus-5-5`. Every commit it produced carries a
`Co-Authored-By: Claude` trailer. The "Student decision / correction" column must be completed by the student. Entries marked
PENDING have not been reviewed by a human yet.

| # | AI activity | Affected material | Verification evidence | Student decision / correction |
|---|---|---|---|---|
| 1 | Proposed the narrowed question, decision rules and strata; drafted `PROTOCOL.md` | `research/rm08_pilot/PROTOCOL.md` (commit 268f90d) | Commit timestamp precedes selection (7225f54) and pilot run | PENDING: confirm question and thresholds, or record changes as deviations |
| 2 | Wrote selection, reference-structure, runner and analysis scripts | `research/rm08_pilot/scripts/*.py` | Re-running the scripts reproduces `inputs/manifest.csv` (SHA-256 per file) and `analysis/summary.json` | PENDING |
| 3 | Reproduced v0.2.1 and diagnosed the hash mismatch | `evidence/20261025T201553Z_reproduction_v021/` incl. `R01_*` | Field-level diff shows only `environment.platform` differs | PENDING |
| 4 | Found D-09 and chose the workaround (remove `build/`) | `evidence/defect_repro/D09_*`, DEV-04 | `metasense version` 0.2.0 → 0.2.1 after workaround | PENDING |
| 5 | Drafted G2 methodology labels from headings and section text | `labels/methodology_labels.csv` | Rationale per paper; ambiguous cases marked | PENDING: verify each label against the PDF |
| 6 | Post hoc relevance labels for 36 citations | `labels/citation_relevance_audit.csv` | Rationale per item | PENDING: re-label independently and report agreement |
| 7 | Interpreted results and drafted the 08 report, walkthrough plan and issue-log entries | Report, `WALKTHROUGH.md`, `docs/issue_log.md` §C | Numbers cross-checked against `summary.json`, `per_document.csv`, `citations.csv` | PENDING: the recorded walkthrough must be in your own words |

Not done by AI: recording the walkthrough, supervisor decisions, pushing to GitHub (requires the student's credentials or permission).

## RM-09 results and limitations memo (2026-10-27)

| # | AI activity (Claude) | Affected material | Verification | Student decision / correction |
|---|---|---|---|---|
| 1 | Wrote and ran the spurious-heading error analysis; its first version mislabelled repeated one-letter math symbols as running heads and was corrected before use | `research/rm09_memo/scripts/error_analysis_spurious_headings.py`, `results/spurious_*` | Deterministic rules; 7 samples per class inspected | PENDING |
| 2 | Found and quantified the RM-08 matcher limitation (appendix letters A–H only) | `results/rm08_matcher_correction.json`; memo "Results" | Per-document re-score; no decision rule changes | PENDING: confirm the correction is reported in the final report |
| 3 | Development-set filter ablation F1–F3 | `results/ablation_heading_filter.json` | Development set only | PENDING |
| 4 | Figures 1–3 and memo draft | `research/rm09_memo/figures/`, memo .docx | Values traced to result files | PENDING: edits |

## Thesis HS3 package (2026-11-02)

| # | AI activity (Claude) | Affected material | Verification | Student decision / correction |
|---|---|---|---|---|
| 1 | Third repeat of v0.2.1; input audit and repeat-comparison scripts | `evidence/20261102T161235Z_repeat3_v021/`, `evidence/20261102_hs3_input_audit/`, `research/hs3_pilot/scripts/` | Comparison script re-run reproduces `repeat_comparison.txt` | PENDING |
| 2 | Procedure notes, protocol changes PC-1…PC-6, HS3 memo draft | `research/hs3_pilot/README.md`, memo .docx | Values traced to run folders | PENDING |

## HS5 artifact hardening and reproducibility check (2026-11-02)

| # | AI activity (Claude) | Affected material | Verification | Student decision / correction |
|---|---|---|---|---|
| 1 | Wrote `scripts/audit_repo.py` and ran the before/after audits | `scripts/audit_repo.py`, `evidence/20261102_hs5_hardening/audit_*` | Findings checked by hand against the tree (e.g. tracked zip, missing files) | PENDING |
| 2 | Hardening code and 19 tests (I-016, D-10, I-021, I-028, `E_UNREADABLE`) | `src/metasense/application/validation.py`, `processing/*.py`, `tests/unit/test_hardening.py` | `pytest` 86 passed on 3.10 and 3.13 as a normal user | PENDING: read the diff of v0.2.1..v0.2.3 |
| 3 | Packaging: Dockerfile, CI workflow, `check_packaging.py`, `.env.example`, `CITATION.cff`, requirements-research | repository root, `.github/workflows/ci.yml` | `check_packaging` PASS; Docker and CI **not yet executed** | PENDING: push and confirm CI is green |
| 4 | Rewrote README; wrote `docs/DATA.md`, `docs/RUNBOOK.md` | docs | Expected outputs checked by the clean passes | PENDING |
| 5 | Ran the clean-environment passes as a separate account, found F1–F4, fixed I-029 (v0.2.3) | `evidence/20261102_hs5_hardening/` | Raw logs with exit codes; re-run after the fix | PENDING: repeat on your own machine if possible |
| 6 | Drafted the HS5 report and walkthrough plan | report .docx, `evidence/20261102_hs5_hardening/WALKTHROUGH.md` | Numbers traced to the logs | PENDING: record the walkthrough yourself |

Not done by AI: recording the walkthrough, the supervisor's answer on what would still block another student, pushing to GitHub.
