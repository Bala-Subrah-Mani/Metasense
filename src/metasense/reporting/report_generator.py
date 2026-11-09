"""Report generation (design component: Report Generator). JSON + Markdown outputs."""
from __future__ import annotations

import json
from pathlib import Path


def to_json(report: dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False)


def to_markdown(report: dict) -> str:
    lines = [f"# MetaSense assessment — {report['input']['file']}", ""]
    lines.append(f"- Run ID: `{report['run_id']}`  |  Version: {report['version']}  |  UTC: {report['timestamp_utc']}")
    if report["status"] != "ok":
        err = report["error"]
        lines += [f"- **Status: ERROR** at stage `{err['stage']}` — `{err['code']}`: {err['message']}", ""]
        return "\n".join(lines) + "\n"
    a = report["assessment"]
    lines += [
        f"- Extractor: {report['extraction']['extractor']}  |  Words: {report['extraction']['word_count']}",
        f"- Methodology section detected: **{'yes' if report['methodology_detected'] else 'no'}**",
        f"- Completeness score: **{a['completeness_score']} / 100** "
        f"(present {a['counts']['present']}, weak {a['counts']['weak']}, missing {a['counts']['missing']})",
        f"- Total processing time: {report['timings_ms']['total']} ms", "",
        "## Detected sections", "", "| Line | Heading | Label | Words |", "|---|---|---|---|",
    ]
    for s in report["sections"]:
        lines.append(f"| {s['start_line']} | {s['heading']} | {s['label']}{' (inherited)' if s['inherited'] else ''} | {s['word_count']} |")
    if report["unrecognized_headings"]:
        lines += ["", "Unrecognized headings: " + "; ".join(report["unrecognized_headings"])]
    lines += ["", "## Rubric assessment", ""]
    for e in report["explanations"]:
        lines.append(f"### {e['criterion']} {e['name']} — {e['status'].upper()}")
        lines.append(e["explanation"])
        for c in e["evidence"]:
            lines.append(f"- {c}")
        if e["recommendation"]:
            lines.append(f"- *Recommendation:* {e['recommendation']}")
        lines.append("")
    lines += ["## Weaknesses", ""]
    if not report["weaknesses"]:
        lines.append("None detected by the baseline rules.")
    for w in report["weaknesses"]:
        lines.append(f"- **{w['id']} [{w['severity']}]** {w['summary']}")
    lines += ["", f"> {report['disclaimer']}", ""]
    return "\n".join(lines)


def write_reports(report: dict, out_dir: Path | str) -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(report["input"]["file"]).stem
    jp, mp = out_dir / f"{stem}.metasense.json", out_dir / f"{stem}.metasense.md"
    jp.write_text(to_json(report) + "\n", encoding="utf-8")
    mp.write_text(to_markdown(report), encoding="utf-8")
    return jp, mp
