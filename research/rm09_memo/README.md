# RM-09 Results and Limitations Memo: analysis artefacts (2026-10-27)

All inputs come from the RM-08 pilot run `evidence/20261025T202233Z_rm08_pilot` (development set). Nothing in `src/` was changed.

| Script | Output | Purpose |
|---|---|---|
| `scripts/error_analysis_spurious_headings.py` | `results/spurious_headings_classified.csv`, `results/spurious_summary.json` | Focused error analysis: cause and detector rule for each of 1,661 spurious headings |
| `scripts/rm08_matcher_correction.py` | `results/rm08_matcher_correction.json` | Re-scores RM-08 M3 with an extended matcher (appendix letters A–Z, small caps re-joined): correction of a measurement error |
| `scripts/ablation_heading_filter.py` | `results/ablation_heading_filter.json` | What-if post-filters F1–F3 on detected headings (development set only, not an evaluation) |
| `scripts/make_figures.py` | `figures/fig2_spurious_causes.png`, `figures/fig3_recall_by_stratum.png` | Memo figures 2–3 |
| (HTML, rendered) | `figures/fig1_failure_path.html/.png` | Failure-path diagram linking limitations to pipeline components |

The error-analysis scripts need the regenerated extracted text (`A_extracted_pypdf.txt`, not committed for copyright reasons; see the pilot README).
