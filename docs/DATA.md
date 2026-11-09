# Data: provenance, preparation and redistribution

| Data | Location | Origin | Can it be redistributed? |
|---|---|---|---|
| Synthetic sample papers (3 texts) | `data/sample/*.txt` | Written for this project; each states it is not a real publication | Yes (MIT) |
| Generated format copies and 42-page load test | `data/sample/paper_complete.{pdf,docx}`, `paper_long_perf.pdf` | Generated from `paper_complete.txt` by `scripts/make_samples.py` (needs `reportlab`) | Yes |
| Invalid/mock inputs | `data/sample/empty.txt`, `unsupported_format.rtf`, `renamed_text.pdf` | Hand-made to test rejection | Yes |
| Known-answer labels, heading variants | `data/annotations/` | AI-drafted, **provisional**, not independent ground truth | Yes |
| RM-08 pilot papers (12 PDFs) | **not in the repository** | PMLR volumes 202/206/195 (author copyright) and JOSS (CC BY 4.0) | **No** for PMLR papers. Only the manifest, checksums and derived metrics are shared |
| Full text extracted from pilot papers | **not in the repository** | Derived from the PDFs | **No**. SHA-256 in `evidence/20261025T202233Z_rm08_pilot/extracted_text_sha256.csv` |

## Re-creating the pilot inputs
1. `git clone --filter=blob:none --no-checkout https://github.com/mlresearch/v202 mlresearch_v202` (also `v206`, `v195`) and
   `git clone --filter=blob:none --no-checkout https://github.com/openjournals/joss-papers openjournals_joss-papers` into one folder.
2. `python research/rm08_pilot/scripts/select_papers.py --sources <that folder> --out <pdf folder>` (seed 699).
3. Check the SHA-256 of every PDF against `research/rm08_pilot/inputs/manifest.csv`. The source commits used are recorded there too.

## Preparation
No preprocessing is needed. MetaSense reads the files directly. Only born-digital PDFs work; scanned PDFs need OCR, which is not supported.
