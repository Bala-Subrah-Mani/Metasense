# Recorded walkthrough plan (target 8–9 minutes)

Record your own screen and voice while opening the files below. Explain each decision in your own words.
At the start, say the date and show `git log -1` so the recording is tied to a version. Fill in the
"Actual time" column after recording and paste it into the report's evidence index.

| Planned | Actual time | Show (open this) | Explain |
|---|---|---|---|
| 0:00–0:45 | | `research/rm08_pilot/PROTOCOL.md`; `git log --format='%h %cI %s' -- research/rm08_pilot/PROTOCOL.md` | The narrowed question from the 07 bridge (MS-MR-01/03/05). Why this is procedural validation, not substantive evidence. The protocol was committed (268f90d) before any paper was selected. |
| 0:45–1:45 | | `git ls-remote origin` vs `git tag`; `evidence/20261025T201553Z_reproduction_v021/summary.md` and `R01_compare_with_20261019_run2.txt`; `evidence/defect_repro/D09_tag_install_stale_build.txt` | Source reconciliation. The clean reproduction of v0.2.1. Why the first hash comparison failed (host metadata), and the revised SC04 comparison rule. D-09: the tag installs stale code. |
| 1:45–2:45 | | `research/rm08_pilot/inputs/manifest.csv`; `labels/g1_structure.json`; `labels/methodology_labels.csv` | Seeded selection, strata and controls, licences, SHA-256. Why the reference structure comes from PDF outlines, typography or JATS rather than your own labels. Which G2 labels you checked and any you changed. |
| 2:45–4:15 | | `evidence/20261025T202233Z_rm08_pilot/E1-strimel23a/A_cli_stdout.json`; then live: `metasense analyze <strimel pdf>` | Conditions A/B/B2/C. In strimel, the headings are all recovered but "Experimental Results" is not recognised as methodology. |
| 4:15–5:45 | | `analysis/summary.json` (decisions); `analysis/headings.csv` | D1–D4 outcomes. Why C vs A shows the main problem is rule coverage, not extraction. Why `-layout` failed (two columns merged). Precision 0.056 and where the spurious headings come from. |
| 5:45–7:00 | | `T-filmus23a/A_cli_stdout.json` (C4 "Recall that"); `labels/citation_relevance_audit.csv` | Negative-case inversion: theory papers score 68.8, an empirical paper 56.2. The 21/36 spurious citations. Why the completeness score is not yet valid on real papers. |
| 7:00–8:00 | | `research/rm08_pilot/DEVIATIONS.md`; `docs/issue_log.md` section C | Rival explanations and limits: AI-drafted labels, ML-only venues, matching rules, post hoc audit. What cannot yet be concluded. |
| 8:00–9:00 | | Report §5 plan; `docs/ai_usage_log.md` | Updated Weeks 9–14 plan and exit tests. What AI did, what you verified, and what you decided or corrected yourself. |
