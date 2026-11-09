# Supervisor Meeting Record: RU-06 Scope and Sequencing

> **Status: NOT YET HELD.** Fill in this record after the meeting. Do not complete the decision
> fields in advance. The "student proposal" column shows what will be put forward, not what was agreed.

- Date / time / format: ____________________
- Attendees: ____________________
- Evidence shown: `evidence/20261019T101812Z_run2_retest/summary.md`, `docs/issue_log.md`, a live `metasense analyze` demo

| # | Decision needed | Evidence | Student proposal | Supervisor decision | Owner / due |
|---|---|---|---|---|---|
| 1 | Rubric: approve the 8 provisional criteria and equal weights for the midpoint? | `src/metasense/resources/rubric.json`; T-11 | Keep 8 criteria and equal weights until the pilot annotation is done | | |
| 2 | Scope rule when no methodology heading is found (I-014) | T-11: 3 of 6 disagreements | Fall back to whole-document scope and mark the result "low confidence" | | |
| 3 | Keep the first NLP pass rule-based until the midpoint, and start the semantic classifier after it? | T-07 recall 0.70; T-11 I-015 | Yes. Use the rule-based baseline as the comparison point the design review requires | | |
| 4 | Supported formats for the midpoint: TXT/PDF/DOCX, no OCR | I-019 | Yes; scanned PDFs out of scope until after the midpoint | | |
| 5 | Pilot dataset: size, source, licensing, second annotator | I-009, I-018 | 30 open-access CS papers (arXiv licence recorded), 10 double-annotated | | |
| 6 | Defer dashboard, authentication and database until after the midpoint; demo through the CLI and Markdown reports | Not started | Yes | | |
| 7 | Sequencing to midpoint | — | (1) real-paper extraction test, (2) pilot annotation, (3) scope fix (I-014), (4) semantic fallback for headings (I-013), (5) minimal upload page | | |

Notes / other decisions:

____________________________________________________________
