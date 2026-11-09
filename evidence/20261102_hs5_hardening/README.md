# HS5 hardening and clean-environment reproducibility check (2026-11-02)

Release checked: **v0.2.3** (commit `b04d320`). Earlier attempts on v0.2.2 (commit `2618485`) are kept because they
found the problems that v0.2.3 fixes.

## What was done

1. **Repository audit before hardening:** `python scripts/audit_repo.py` gave 12 findings (`audit_before.txt/.json`).
2. **Hardening:** v0.2.2 added 19 tests for hostile and malformed input, wired `METASENSE_MAX_BYTES`, fixed D-10,
   I-021 and I-028, and added the Dockerfile, CI workflow, `.env.example`, `docs/DATA.md`, `docs/RUNBOOK.md`,
   `CITATION.cff` and `scripts/check_packaging.py`. The README was rewritten.
3. **Clean-environment passes.** A separate Unix account (`peer`) with an empty home directory, no pip cache and no
   access to the developer's checkout ran the README literally: clone, venv, install, `doctor`, the four sample
   commands from README §4, `pytest`, `check_packaging.py` and the full `run_validation.py`. The script is
   `peer_pass.sh`, and every command, its output and its exit code are in the logs. The clone came from a local
   bare mirror of `main` with its tags, because the public GitHub repository had not been pushed yet (I-MP-01).
4. **Fix and re-run.** The defects the passes found were fixed in v0.2.3, and both passes were run again from scratch.
5. **Repository audit after hardening:** `audit_after.txt/.json`, taken at commit `7d7baf0`. Two findings remain. The
   "uncommitted change" is the audit's own output file, which was being written as it ran. The other is tag `v0.2.1`, which
   still contains `build/` (D-09). Rewriting a published tag would break the earlier reports that cite it, so it
   stays as it is. It is documented, and the README points users to v0.2.3.

## Results on v0.2.3

| | Python 3.13.16 | Python 3.10.20 |
|---|---|---|
| Log | `pass_py313.log` | `pass_py310.log` |
| Clone to `doctor` PASS | 14 s | 22 s |
| Whole pass incl. full validation | 39 s | 71 s |
| `doctor` | PASS, 0 failed, 0 warnings | PASS, 0 failed, 0 warnings |
| README §4 expected outputs | all 5 match | all 5 match |
| `pytest` | 86 passed | 86 passed |
| `check_packaging.py` | PASS (wheel 0.2.3) | PASS (wheel 0.2.3) |
| `run_validation.py` T-01…T-11 | 9 PASS, 2 MEASURED | 9 PASS, 2 MEASURED |
| Evidence folder | `20261102T181346Z_peer_py313/` | `20261102T181444Z_peer_py310/` |

The five sample reports are identical across the two Python versions once the fields that vary by design are left
out (`run_id`, `timestamp_utc`, `timings_ms`, `environment`), see `cross_version_compare.txt`. On 3.10, pip also
installs `exceptiongroup` and `tomli` (pytest back-ports) and `setuptools`, so the freeze has 16 packages instead of 13.
The 86th test (unreadable file gives `E_UNREADABLE`) runs only as a normal user. It ran here; the developer's
account is root, where it is skipped.

## Friction log

| # | What happened | Seen in | Cause | Fix | Status |
|---|---|---|---|---|---|
| F1 | `git clone` stopped: *detected dubious ownership in repository* | `pass_attempt0_dubious_ownership.log` | The mirror folder belonged to root, and the clone ran as `peer` | `chown` of the mirror. README troubleshooting row added (I-030) | Documented |
| F2 | In that failed attempt, `metasense analyze` and `metasense version` still answered "0.2.2" although nothing had been installed | same log | An old editable install of MetaSense in the system Python (`/usr/local/bin/metasense`) pointed at the developer's checkout and shadowed the empty venv. A failed setup looked half-successful | Old install removed. The pass script now prints `which metasense` before installing and aborts if the clone fails. README row added (I-031) | Documented |
| F3 | `check_packaging.py` crashed on Python 3.10.20: `No module named 'encodings'` while creating its test venv | `pass_py310_v022.log` | `venv.create()` copies the interpreter (`symlinks=False`). Run from inside another venv on a relocatable Python build (uv), the copy cannot find its standard library. 3.13 was not affected | v0.2.3: the script runs `python -m venv`, the same command as the README (I-029) | **Fixed, re-run passes** |
| F4 | README promised `85 passed, 1 skipped`, but a normal user gets `86 passed` | `pass_py313_v022.log` | The skipped test needs a non-root account. The README number had been taken from the root account | README §4 now gives both numbers | Fixed |
| F5 | pip prints *A new release of pip is available* | all logs | pip 26.2.1 in a new venv | None needed. Harmless, and the README does not ask the user to upgrade pip | Accepted |
| F6 | `docker build` could not pull `python:3.12-slim` (*Forbidden*) | `docker_build_attempt.txt` | The container registry is blocked in this environment | The CI `docker` job builds the image and runs the tests in it. **The image has not been built yet** (I-032) | Open until CI runs |

## Not verified here

- Windows and macOS. The CI matrix covers them, but it runs only after `main` and the tags are pushed to GitHub (I-MP-01).
- The Docker image and Python 3.12 (the base image) (F6).
- A pass by another person on their own machine. `peer` is a separate account on the same computer. It is not a second person.

## Files

`WALKTHROUGH.md` is the plan for the recorded walkthrough. `peer_pass.sh` is the pass script. The `pass_*.log` files are raw logs. The `*_peer_*` folders hold the full
`run_validation.py` evidence. The audit files are `audit_before.*` and `audit_after.*`. The other records are
`docker_build_attempt.txt` and `cross_version_compare.txt`.
