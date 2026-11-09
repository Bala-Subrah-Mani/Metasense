# RM-08 pilot run 20261025T202233Z

Produced by `research/rm08_pilot/scripts/run_pilot.py` with the frozen v0.2.1 reference (see `run_environment.json`).
Analysis: `analysis/` (from `analyze_pilot.py`). Per document: `A_cli_stdout.json` (full report, condition A),
`A_reports/` (JSON + Markdown), `B_cli_stdout.json`, `B2_cli_stdout.json`, `A_cli_stderr.txt`.

Full extracted paper text (`A_extracted_pypdf.txt`, `B_pdftotext_layout.txt`, `B2_pdftotext.txt`) is **not committed**,
because most inputs are author-copyrighted. Regenerate it by re-running the pilot on inputs with the manifest's SHA-256 values,
and check the result against `extracted_text_sha256.csv`. Reports contain short quotes (≤ 220 characters) only.
