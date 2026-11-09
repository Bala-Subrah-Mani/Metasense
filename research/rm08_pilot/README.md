# RM-08 pilot: real-paper transfer test of the frozen rule-based reference

Start with `PROTOCOL.md` (pre-registered, commit 268f90d), then `DEVIATIONS.md`.

| Step | Script | Output |
|---|---|---|
| 1 Select papers (seed 699) | `scripts/select_papers.py --sources <clones> --out <pdf-dir>` | `inputs/manifest.csv` (provenance, URL, licence, SHA-256) |
| 2 Reference structure G1 | `scripts/build_gold_structure.py <pdf-dir>` | `labels/g1_structure.json` |
| 2b Methodology labels G2 | hand-written (AI-drafted, student verification pending) | `labels/methodology_labels.csv` |
| 3 Run conditions A/B/B2/C with frozen v0.2.1 | `<frozen-venv>/bin/python scripts/run_pilot.py --pdfs <pdf-dir>` | `evidence/20261025T202233Z_rm08_pilot/` |
| 4 Analysis M1–M7, D1–D4 | `scripts/analyze_pilot.py evidence/20261025T202233Z_rm08_pilot` | `.../analysis/summary.json`, `per_document.csv`, `headings.csv`, `citations.csv` |
| 5 Post hoc relevance audit | hand-labelled (AI-drafted) | `labels/citation_relevance_audit.csv` |

## Re-creating the inputs
PDFs are not redistributed. Clone with `git clone --filter=blob:none --no-checkout https://github.com/mlresearch/v202 mlresearch_v202`
(likewise `v206`, `v195`, and `openjournals/joss-papers` as `openjournals_joss-papers`), then run step 1. The script checks out only the
selected files. The SHA-256 values in the manifest confirm you have byte-identical inputs. Repository commits used: see `inputs/manifest.csv`.

## Frozen reference environment
```bash
git archive v0.2.1 | tar -x -C frozen/src && rm -rf frozen/src/build     # build/ removal: see D-09 / DEV-04
python -m venv frozen/venv && (cd frozen/src && ../venv/bin/pip install -r requirements.txt .)
frozen/venv/bin/metasense version    # must print 0.2.1
```
Gold-structure step needs `pymupdf` and `pypdf` in the system interpreter. Condition B needs Poppler `pdftotext` (24.02.0 used).
