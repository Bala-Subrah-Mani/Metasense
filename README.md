# MetaSense — CISC699 Assignment 05: Implementation Sprint I

**Package status:** Starter implementation created for the Assignment 05 feedback.  
**Project interpretation:** Because the uploaded feedback refers to a “MetaSense report” but does not include the original source code or a full technical specification, this ZIP implements MetaSense as a small, extensible environment-health and configuration-checking CLI. Confirm or replace this interpretation if the intended MetaSense application is different.

## What is included
- Python CLI that checks a JSON configuration and reports environment/configuration health.
- Structured JSON output and human-readable terminal output.
- Unit tests and a reproducible test command.
- Configuration example and sample input.
- Engineering log, risk/issue register, release/baseline records, sprint reflection, AI usage log.
- Evidence templates for dated baseline, actual terminal output, smoke tests, and release traceability.
- GitHub Actions workflow for running tests.
- Clear labels separating **actual execution evidence captured while assembling this ZIP** from **templates/examples that must be completed by the student**.

## Requirements
- Python 3.10 or newer
- No third-party runtime dependencies
- `pytest` is optional for the test suite; standard-library `unittest` is also supported

## Quick start

From this directory:

```bash
python -m metasense --config config/metasense.json
```

If Python cannot find the package from the project root, use:

```bash
PYTHONPATH=src python -m metasense --config config/metasense.json
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m metasense --config config/metasense.json
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

Optional pytest run:

```bash
python -m pytest -q
```

Run the smoke test and save a fresh evidence record:

```bash
python scripts/smoke_test.py
```

The smoke-test script writes a timestamped record to `logs/`. The record created during ZIP assembly is included as historical package-build evidence; run it again on your own machine to produce evidence for your actual environment.

## CLI behavior
The CLI loads the JSON configuration, validates required fields, checks configured directories, and returns:
- exit code `0` when checks pass;
- exit code `1` when configuration or environment checks fail;
- exit code `2` for command-line or unexpected runtime errors.

Use `--json` for machine-readable output and `--strict` to fail when optional directories are missing.

## Repository map

```text
MetaSense_CISC699_Assignment05/
├── .github/workflows/tests.yml
├── config/metasense.json
├── data/sample_environment.json
├── docs/
│   ├── architecture.md
│   ├── engineering_log.md
│   ├── risk_issue_register.csv
│   ├── release_baseline.md
│   ├── sprint_reflection.md
│   ├── test_plan.md
│   ├── ai_usage_log.md
│   └── evidence_templates/
├── logs/
├── results/
├── scripts/smoke_test.py
├── src/metasense/
├── tests/
├── .gitignore
├── CHANGELOG.md
├── pyproject.toml
└── README.md
```

## Evidence integrity
- `logs/ZIP_BUILD_TEST_EVIDENCE.txt` records the test run performed during assembly of this ZIP in the creation environment.
- Files under `docs/evidence_templates/` are **blank templates**, not proof that a test, Git commit, or release occurred.
- Do not represent the package-build timestamp as the time you ran the project locally.
- After extracting the ZIP, run the commands above and preserve your own terminal output, date/time, exit code, Python version, and Git commit hash if applicable.
- The included Git metadata is not initialized automatically. Initialize Git and make a baseline commit only after reviewing and running the files.

## Suggested first baseline steps
1. Review this starter interpretation and update project scope to match your approved proposal.
2. Run the application and tests in your own environment.
3. Save actual terminal output using the evidence template.
4. Review and update the risk register based on the implementation you verified.
5. Initialize Git, commit the reviewed files, and record the real commit hash in `docs/release_baseline.md`.
6. Update the sprint reflection and AI usage log to accurately reflect your own work and tool usage.

## Limitations
This is a small starter implementation, not a production monitoring agent. It does not collect telemetry automatically, access cloud APIs, store secrets, or claim security/compliance certification.
