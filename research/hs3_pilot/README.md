# HS3 pilot (thesis Hard Stop 3): procedure notes, protocol and changes

**Research question (from proposal / RU-04 design):** how can an AI-assisted framework extract methodological
components from CS papers and evaluate their completeness transparently?
**Highest-risk procedural assumption tested here:** that the rule-based instrument (design-review §3, implementation
baseline RU-05) can turn a paper into a *traceable, repeatable and interpretable* rubric assessment, so that later
evidence (Assignments 07/08) measures methodology reporting rather than pipeline noise.

## Inputs (all synthetic or mock; no human participants, no external data)
`data/sample/` — 3 synthetic papers (self-labelled as not real publications), 2 generated format copies, 1 generated
42-page load-test PDF, 3 mock invalid files. Known-answer labels: `data/annotations/expected_assessments.json`
(AI-drafted, **provisional**, not independent). Heading-variant set: `data/annotations/heading_variants.csv` (AI-drafted).
Input audit (types, signatures, UTF-8, self-labelling, SHA-256 vs 19 Oct): `evidence/20261102_hs3_input_audit/`.

## Procedure (version v0.2.1, commit e4ec8ad)
`python scripts/run_validation.py --label <name>` — fresh venv, pinned requirements, checks T-01…T-11.
Pass criteria were committed in code (7a77866, 10:16:29 UTC 19 Oct) before run 1 started (10:16:32 UTC).
T-07 and T-11 are *measurements* with no pre-set threshold.

## Usable vs revise (readiness rule)
Usable for the 07/08 evidence target if: all execution checks pass (T-01…T-06, T-08…T-10); invalid inputs fail with
the documented code; repeated runs give identical substantive output; every finding cites evidence.
Requires revision if: a known-answer disagreement is systematic (same cause in ≥ 2 cases) or a defect changes a score.

## Executions and repeat/retrace
| Run | Date | Code | Purpose |
|---|---|---|---|
| `evidence/20261019T101632Z_run1` | 19 Oct | v0.2.0 | first execution (1 test failed; defects D-01…D-07) |
| `evidence/20261019T101812Z_run2_retest` | 19 Oct | v0.2.1 | retest after fixes |
| `evidence/20261025T201553Z_reproduction_v021` | 25 Oct | v0.2.1 | clean-checkout repeat |
| `evidence/20261102T161235Z_repeat3_v021` | 2 Nov | v0.2.1 | third repeat, new host |
Comparison: `python research/hs3_pilot/scripts/compare_repeats.py` → `evidence/20261102_hs3_input_audit/repeat_comparison.txt`.
All repeats are **self-checks by the same procedure**, not independent replication.

## Protocol changes resulting from the pilot
| ID | Change | Reason (evidence) |
|---|---|---|
| PC-1 | Consistency comparison excludes `environment` metadata as well as run id, timestamp, timings | Rule-1 hashes differ across hosts only through the platform string (repeat_comparison.txt) |
| PC-2 | Known-answer labels must be verified by the student and a second annotator before any accuracy claim | Labels drafted by the same process as the rules (I-018) |
| PC-3 | Add explicit "weak vs missing" decision rule to the rubric definitions | 3 of 6 T-11 disagreements: vague mention rated missing (I-015) |
| PC-4 | Decide scope rule when no methodology heading is found (fallback + low-confidence flag) | 3 of 6 T-11 disagreements (I-014) |
| PC-5 | Next pilot must use real published papers with negative controls and a pre-registered protocol | All HS3 inputs are synthetic; transfer is the largest untested risk |
| PC-6 | Release v0.2.2 without the committed `build/` directory | Tag install yields stale code (D-09, found 25 Oct) |

## Single unresolved risk most likely to undermine the midpoint (08) evidence review
Transfer: heading-based detection and keyword indicators validated only on synthetic, conventionally structured text
may not work on real two-column published papers. (Tested later in `research/rm08_pilot/` — see its PROTOCOL.md.)
