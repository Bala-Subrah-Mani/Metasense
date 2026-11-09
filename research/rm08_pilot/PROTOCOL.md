# RM-08 Pilot Protocol: Does the frozen rule-based reference transfer to real published papers?

Status: **pre-registered**. This file was committed before any pilot paper was selected or processed
(see `git log -- research/rm08_pilot/PROTOCOL.md`). Any later change is recorded under "Deviations" in `DEVIATIONS.md`.

## 1. Question, claim and type of evidence
- **Bridge from 07:** MS-MR-01 (source/evidence reconciliation), MS-MR-03 (real-paper extraction probe, about 10 eligible papers),
  MS-MR-05 (clean reproduction) and the frozen rule reference needed by MS-MR-06 and SC11.
- **Narrowed question:** Can MetaSense's frozen rule-based reference (tag `v0.2.1`, commit `e4ec8ad`) process real, published
  computer-science papers, recover their section structure and locate their methodology content reliably enough to serve
  as the fixed comparison baseline for SC11 and as the extraction front-end for the SC02/SC03 evaluation?
- **Method risk examined:** all v0.2.1 evidence came from synthetic, single-column inputs written by the rule author.
  The consequential assumption is that heading-based rules and pypdf extraction **transfer** to real two-column papers.
- **Type of evidence:** *procedural validation* of the method (the measurement instrument), **not** substantive evidence about
  the methodological quality of the papers or of the field.

## 2. Permitted inputs
Openly accessible papers retrieved through GitHub (the only scholarly source reachable from the execution environment;
arXiv is blocked by the environment's network policy):
- PMLR volume 202 (ICML 2023) and volume 206 (AISTATS 2023), repositories `mlresearch/v202`, `mlresearch/v206`: two-column, empirical ML.
- PMLR volume 195 (COLT 2023), `mlresearch/v195`: learning-theory papers. **Negative control** (no empirical methodology expected).
- Journal of Open Source Software (CC BY 4.0), `openjournals/joss-papers`: short software papers. **Unconventional control**.

PDFs are used for local analysis only and are **not redistributed** in the MetaSense repository. The manifest records the source
repository commit, path, official URL and SHA-256 so that every input can be re-retrieved and verified.
No human participants, no personal data, no paid services.

## 3. Selection rule (deterministic)
`random.Random(699).sample(sorted(candidate_ids), n)` per stratum, where candidates are the main-paper PDFs
(supplementary files excluded):
| Stratum | Source | n | Role |
|---|---|---|---|
| E1 | ICML 2023 (v202) | 5 | empirical, two-column |
| E2 | AISTATS 2023 (v206) | 3 | empirical, two-column |
| T | COLT 2023 (v195) | 2 | negative control (theory) |
| S | JOSS IDs 05000–05999 with JATS source | 2 | unconventional control (software paper) |
Total 12 documents (10 research papers + 2 software papers). Papers are not replaced after selection; a paper that fails to
process stays in the denominator.

## 4. Reference ("gold") structure — chosen to be independent of the rule author
- **G1 section structure:** the PDF's own outline (bookmarks written by the authors' LaTeX/hyperref). For JOSS, the section
  titles in the publisher's JATS XML. Only if neither exists is a heading list transcribed manually from the rendered pages;
  such papers are flagged.
- **G2 methodology label:** for each paper, which top-level G1 sections describe how the study was carried out
  (data, experimental setup, procedure, evaluation protocol). This is a human judgement and is recorded with a rationale in
  `labels/methodology_labels.csv`; it was drafted with AI assistance and requires the student's verification (see AI log).

## 5. Conditions (rival-explanation design)
- **A — as shipped:** `metasense analyze` v0.2.1 on the PDF (pypdf extraction).
- **B — alternative extractor:** the same v0.2.1 section detector and rubric on text from `pdftotext -layout` (Poppler).
- **C — oracle structure:** the v0.2.1 section detector applied to the G1 heading titles as clean lines.
If C succeeds where A fails, failures are attributed to extraction/layout; if C also fails, to the rules (synonym coverage).

## 6. Measures
| ID | Measure | Linked criterion |
|---|---|---|
| M1 | Per-document processing outcome (status ok, exit code, warnings) | SC01 |
| M2 | Extraction fidelity: words pypdf/pdftotext; share of G1 top-level headings recoverable as a line in extracted text | FR3, I-008/I-019 |
| M3 | Top-level heading recall and precision against G1 (A, B, C) | FR4 |
| M4 | Paper-level methodology detection agreement with G2 (A, B, C) | FR4, SC02 precursor |
| M5 | Citation-integrity audit of every evidence citation in A reports (quote present at cited line, indicator matches quote, section label consistent) | SC06 |
| M6 | Processing time per document (first and warm) | SC07 |
| M7 | Rubric status distribution by stratum (descriptive only; **no accuracy claim**, no independent rubric labels exist) | FR6/FR7 |

## 7. Decision rules (fixed before running)
- **D1 reference usability:** v0.2.1 is accepted as the frozen SC11 comparison reference iff M1 ≥ 95% (12/12 or 11/12 with documented cause) **and** M5 ≥ 99%.
- **D2 extractor adequacy:** pypdf is adequate for the evaluation iff ≥ 90% of G1 top-level headings are recoverable as lines (M2). Otherwise
  the better extractor is adopted for **both** reference and candidate, recorded as a deviation.
- **D3 attribution:** if C recall − A recall ≥ 0.20, heading failures are attributed mainly to extraction/layout; otherwise to rule coverage.
- **D4 transfer claim:** the heading-based methodology detector "transfers" iff M4 agreement ≥ 0.80 on the 8 empirical papers.
  Failing D4 does **not** fail the pilot: it is the consequential finding that motivates the semantic candidate (MS-MR-07).

## 8. Reproduction step (MS-MR-05, partial)
Before the pilot, re-run `scripts/run_validation.py` on a clean checkout of tag `v0.2.1` and compare the T-10 output hashes with
the 19 Oct run (`evidence/20261019T101812Z_run2_retest`). Identical hashes = the reported baseline is reproduced.

## 9. What this pilot cannot conclude
Rubric accuracy (SC02/SC03), usefulness (SC05), usability (SC10) and security (SC13). Results from 12 ML-venue documents do not
generalise to all of computer science.
