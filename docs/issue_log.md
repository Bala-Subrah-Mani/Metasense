# Issue and Defect Log (RU-06)

Updated 2026-10-19 from validation runs `run1` (v0.2.0) and `run2_retest` (v0.2.1). The machine-readable copy is `issue_log.csv`.

## A. Defects observed in run 1 (v0.2.0) and their retest

| ID | Observed defect | How found (evidence) | Impact | Fix / workaround | Retest (run2, v0.2.1) |
|---|---|---|---|---|---|
| D-01 | C8 *Reproducibility* rated PRESENT for `paper_weak.txt` because "various **open-source** projects" matched the `open-source` indicator | T-11 mismatch; `run1/T04_sample_outputs/paper_weak_txt/*.json` evidence line 10 | False positive. A paper with no artifact gets credit | Indicator now requires that code/tool *is* open-sourced | **Closed**: C8 = missing, as expected. New regression test `test_d01_*` |
| D-02 | C3 *Experimental setup* rated WEAK for `paper_weak.txt` from the word "pipeline" in the abstract's disclaimer sentence | Explanation evidence cited an unrelated sentence (right label, wrong reason) | Misleading explanation | Removed generic `pipeline` indicator | **Closed**. C3 is now *missing* (human label: *weak*), see I-015 |
| D-03 | Unnumbered headings "Abstract" and "References" not detected in PDF/DOCX: extraction leaves no blank line before them | Unit test `test_references_section_is_ignored` FAILED (T-08 run1); section lists differ txt vs pdf/docx | References text leaks into Conclusion → possible false positives on real papers | Short (≤4 word) Title Case headings accepted without blank line | **Closed**: 67/67 tests pass. Section labels now identical across TXT/PDF/DOCX |
| D-04 | Dataset size not recognised when words separate number and noun ("12 open-source Python repositories") | T-11 mismatch (`paper_no_method_heading` C2 = missing) | False negative on dataset criterion | Allow up to 3 words between number and noun | **Partly closed**: indicator now matches (test `test_d04_*`). C2 still *weak* because of I-014 |
| D-05 | `config/project_layout.json` listed non-existent `results/` directory → doctor WARN | T-03 run1 doctor output | Noise in toolchain check | Replaced with `reports/`, `evidence/` | **Closed**: doctor PASS, 0 warnings |
| D-06 | Integration test compared only scores across formats, so it passed despite D-03 | Review of D-03 | Weak test oracle | Test now also compares section labels | **Closed** |
| D-07 | Non-editable install (`pip install .`) crashed: default rubric path pointed outside the package | Manual check, `evidence/defect_repro/D07_non_editable_install.txt` (exit 2) | Anyone installing normally gets a crash | Rubric moved to `src/metasense/resources/` as package data. Workaround before the fix: `--rubric config/rubric.json` | **Closed**: `D07_retest_after_fix.txt` (exit 0) |
| D-08 | Build artifacts (`build/lib/...`) from the D-07 reproduction were accidentally committed in e4ec8ad | `git status` during docs update | Repo hygiene only. Code under test is `src/` (package-dir), so run 2 results are unaffected | `build/` removed and added to `.gitignore` | **Closed** in docs commit |

## B. Open issues and risks (carried forward from RU-06 v1 and new)

| ID | Issue | Severity | Status after RU-06 | Next action |
|---|---|---|---|---|
| I-007 | Smoke test never actually executed (RU-06 v1) | High | **Closed**: two dated runs with raw logs | — |
| I-008 | Real PDF/DOCX extraction unverified | High | **Partly resolved**: works on generated single-column PDF/DOCX (543 words identical across formats). Real published papers untested | Run on 10 open-access CS papers (two-column ACM/IEEE) and log extraction failures |
| I-009 | Evaluation dataset not curated | High | Open. Only 3 synthetic papers and 38 headings exist | Define inclusion criteria, collect 30 open-access papers with licenses recorded, annotate pilot subset |
| I-010 | Rubric weights/categories unconfirmed | Medium | Open. Provisional rubric v0.2: 8 criteria, equal weights | Supervisor decision (meeting record) |
| I-011 | Dependency versions not finalized | Medium | **Partly resolved**: pinned and verified on Py 3.13/Linux. No NLP model chosen yet | Pin spaCy/transformer versions when introduced |
| I-012 | Human review needed for AI findings | High | **Mitigated in output**: disclaimer and line-cited evidence in every report | Carry into dashboard UI |
| I-013 | Heading recall 0.70: misses "Proposed Framework", "System Design", "Data Collection", "Study Procedure", "Research Approach", project-named and informal headings | Medium | Open, by design (synonym table was **not** tuned to the eval set to avoid overfitting) | Content-based fallback (sentence classifier) evaluated on an independent heading set |
| I-014 | With no methodology heading, methodology-scoped criteria are capped at *weak* (3 of 6 T-11 disagreements) | Medium | Open: needs a scope decision | Supervisor decision. Option: fall back to whole-document scope and lower confidence |
| I-015 | Keyword matching cannot detect vague mentions as *weak*; rates them *missing* (3 of 6 T-11 disagreements) | Medium | Open: a limit of the rule-based baseline | Address in the semantic NLP phase. Use vague-phrase hits as a signal |
| I-016 | `METASENSE_MAX_BYTES` declared but not wired | Low | Open | Wire in `validate_input` with a test |
| I-017 | Only validated on Linux/Python 3.13 cloud container | Medium | Open | Student to run `run_validation.py` on own Windows/macOS machine and commit evidence |
| I-018 | Heading set and known-answer labels drafted by the same party (AI-assisted) as the rules → optimistic bias | High | Open | Student re-labels independently; second annotator for pilot subset; report agreement |
| I-019 | No OCR, two-column handling or table extraction (warnings exist for empty pages/tables but are untested on real files) | Medium | Open | Test with real papers (I-008); evaluate `pdfplumber` / layout-aware extraction |
| I-020 | Completeness score could be misread as a quality verdict | Medium | Mitigated: `score_note` + disclaimer in report | User testing of wording in dashboard phase |
| I-021 | Explanations repeat the same sentence when several indicators match it (e.g., C2 on `paper_complete.pdf` cites line 18 three times) | Low | Open. Found while reviewing run 2 reports | De-duplicate evidence by sentence and list all indicators matched |
| I-022 | First run in a process is 5–7× slower (import/rubric load warm-up: 94 ms vs 13 ms for the PDF sample); `load_rubric` is 7.4 of 9.3 ms for small files | Low | Open. Observed in T-10 | Cache the compiled rubric when the web service is built |

Severity: High blocks a claim or a milestone; Medium degrades results; Low is cosmetic or convenience.

## C. Issues from the RM-08 real-paper pilot (2026-10-25, `evidence/20261025T202233Z_rm08_pilot`)

| ID | Observed | Evidence | Severity | Next action (owner: Bala) |
|---|---|---|---|---|
| D-09 | Non-editable install from tag v0.2.1 silently installs v0.2.0 modules from the committed `build/` tree | `evidence/defect_repro/D09_tag_install_stale_build.txt` | Critical (reproducibility, SC12) | Release v0.2.2 without `build/`; add a packaging test that checks `metasense version` after a non-editable install |
| D-10 | Evidence quotes are cut at 220 characters, sometimes before the matched indicator (10 of 186 citations), so the reader cannot see why the rule fired | `analysis/citations.csv` (indicator_matches_quote = False) | High (SC06) | Centre the quote window on the match |
| I-023 | Section detector precision on real papers is 0.056: math lines, table cells and ALL-CAPS running heads become top-level headings, and methodology scoping breaks | `analysis/headings.csv`, `summary.json` M3 | Critical for rubric validity | Running-head filter, minimum alphabetic ratio, font-aware heading cues (development set only) |
| I-024 | Methodology vocabulary misses common real headings ("Numerical Results", "Experimental Results", "Examples", "Verify ... in Practice"); heading-based detection agrees on 4/7 empirical papers | `analysis/per_document.csv` | High (FR4, SC02) | Content-based candidate (MS-MR-07); do not tune synonyms on final-evaluation papers |
| I-025 | Appendix headings formatted "Appendix A. Title" are not recognised | `T-filmus23a/A_extracted_pypdf.txt` lines 739, 1870, 3090 | Medium | Extend numbering pattern |
| I-026 | Rubric indicators fire on unrelated senses ("Recall that", variable "f1", affiliations in the front matter, arXiv URLs). In the audit, 21 of 36 first citations for C2–C4 were spurious, and theory papers score 68.8 against 56.2 for an empirical paper | `labels/citation_relevance_audit.csv`; M7 | Critical (completeness score not valid on real papers) | Rubric applicability gate (empirical papers only), sense-aware indicators, references/front-matter exclusion |
| I-027 | `pdftotext -layout` merges two columns: headings recoverable drop to 0.59. Reading-order mode reaches 0.90 and pypdf 0.85 | `summary.json` M2 | Medium | Keep the extractor fixed and identical for reference and candidate; decide pypdf vs reading-order pdftotext with the supervisor |
| I-028 | pypdf output for math-heavy PDFs contains control characters (e.g., 3,311 NUL bytes in T-filmus23a) | `T-filmus23a/A_extracted_pypdf.txt` | Low | Strip control characters in normalisation |
| I-MP-01 | Public GitHub still at 1c39f7d; tags v0.2.0/v0.2.1 and all RU-06/RM-08 commits exist only in the local repository | `git ls-remote origin` on 2026-10-25 | Critical (traceability) | Push branch and tags; record the push time and public URL in the evidence index |
| I-MP-02 | The run folder `evidence/20261019T180515Z_reviewcopy/` cited in the 07 report does not exist in any commit (`git log --all` returns nothing) | 07 report Appendix A; this repository | High | Withdraw that citation; only run1, run2_retest and the 2026-10-25 reproduction are authoritative |

## D. HS5 hardening and clean-environment pass (2026-11-02, `evidence/20261102_hs5_hardening/`)

Status changes. Older rows above are kept as they were written; this table is the current status.

| ID | Status on 2026-11-02 | Where |
|---|---|---|
| I-016 | Closed in v0.2.2: `METASENSE_MAX_BYTES` wired, invalid values give `E_CONFIG` | `tests/unit/test_hardening.py` |
| I-017 | Partly closed: Linux clean passes on Python 3.10.20 and 3.13.16; Windows/macOS run in CI, which starts once the repository is pushed | `evidence/20261102_hs5_hardening/` |
| I-021 | Closed in v0.2.2: each sentence is cited once per criterion | `test_one_citation_per_sentence` |
| I-028 | Closed in v0.2.2: control characters stripped during normalisation | `test_control_characters_are_removed` |
| D-09 | Closed from v0.2.2 on: tags contain no `build/`; `scripts/check_packaging.py` installs the wheel non-editably and checks the version. Tag v0.2.1 itself is not rewritten | `check_packaging` output in both pass logs |
| D-10 | Closed in v0.2.2: quote window centred on the matched word | `test_quote_window_shows_the_matched_word` |
| I-029 | **New, closed in v0.2.3.** `check_packaging.py` crashed on Python 3.10.20 (uv build): `venv.create()` copies the interpreter, and the copied venv could not find its standard library (`No module named 'encodings'`). Now uses `python -m venv` | `pass_py310_v022.log` (fail), `pass_py310.log` (pass) |
| I-030 | **New, documented.** Cloning from a folder owned by another user stops with git's `dubious ownership` error | README troubleshooting; `pass_attempt0_dubious_ownership.log` |
| I-031 | **New, documented.** An old globally installed editable copy of MetaSense masked a failed setup: commands kept working although nothing had been installed in the venv | README troubleshooting; `pass_attempt0_dubious_ownership.log` |
| I-032 | **New, open.** The Docker image could not be built here because the container registry is blocked in this environment; CI builds it | `docker_build_attempt.txt` |
| I-MP-01 | Open until the student pushes `main` and the tags | `git ls-remote origin` |
