# HS5 walkthrough plan (5–7 minutes, record yourself, in your own words)

Use a fresh folder on your own laptop. Do not use the folder you develop in, so the recording shows a real first install.

| Time | Show | Say (in your own words) |
|---|---|---|
| 0:00–0:40 | GitHub page of the repository, README top, tag `v0.2.3` | What MetaSense does in one sentence, and which version you are showing |
| 0:40–2:00 | Terminal: `git clone …`, `python -m venv .venv`, activate, `pip install -e . -r requirements-dev.txt`, `metasense doctor` | The prerequisites (Python 3.10–3.13, nothing else). Point at `doctor` PASS |
| 2:00–3:00 | `metasense analyze data/sample/paper_complete.txt`, `paper_weak.txt`, `empty.txt` | Compare each result with the README §4 table. Explain exit code 1 for the empty file |
| 3:00–3:40 | `metasense analyze data/sample/paper_weak.txt --out reports/`, open the `.md` report | Every finding cites a line of the paper. Read one citation aloud |
| 3:40–4:30 | `python -m pytest -q`, `python scripts/check_packaging.py` | Number of tests, what the hardening tests cover, why the packaging check exists (D-09) |
| 4:30–5:30 | `evidence/20261102_hs5_hardening/README.md` friction table; `pass_py310_v022.log` failure, then `pass_py310.log` pass | What the clean pass found and how v0.2.3 fixed it |
| 5:30–6:30 | GitHub Actions page (after pushing) | Whether CI is green on Windows/macOS and in Docker. If it is not, say so and show the error |
| 6:30–7:00 | README "Limitations" | The score is not a validated quality measure yet. Say what still remains |

If something fails while you record, keep it in the video and say what you did about it. That is evidence too.
