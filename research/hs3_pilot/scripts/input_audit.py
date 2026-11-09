"""HS3 input audit: checks every pilot input and proves it is byte-identical to the input used on 19 October.

For each file in data/sample/: SHA-256 now vs SHA-256 recorded inside the 19-Oct run-2 report (if one exists),
size, type by signature, UTF-8 decodability (text), whether the file labels itself as synthetic, headings present.
Writes the table to stdout as CSV and a JSON summary to the path given as argv[1].
"""
import csv, hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SAMPLE = ROOT / "data" / "sample"
RUN2 = ROOT / "evidence" / "20261019T101812Z_run2_retest" / "T04_sample_outputs"
PURPOSE = {
    "paper_complete.txt": "valid: all 8 criteria reported (synthetic)",
    "paper_complete.pdf": "valid: same text as PDF (synthetic, generated)",
    "paper_complete.docx": "valid: same text as DOCX (synthetic, generated)",
    "paper_weak.txt": "valid: vague methods (synthetic)",
    "paper_no_method_heading.txt": "valid: method under informal heading (synthetic)",
    "paper_long_perf.pdf": "valid: 42-page load test (synthetic, generated)",
    "empty.txt": "invalid: must be rejected E_EMPTY (mock)",
    "unsupported_format.rtf": "invalid: must be rejected E_UNSUPPORTED_TYPE (mock)",
    "renamed_text.pdf": "invalid: must be rejected E_CORRUPT (mock)",
}

def sig(b):
    if b[:5] == b"%PDF-": return "pdf"
    if b[:4] == b"PK\x03\x04": return "zip/docx"
    if not b: return "empty"
    return "text"

rows = []
for f in sorted(SAMPLE.iterdir()):
    b = f.read_bytes()
    sha = hashlib.sha256(b).hexdigest()
    rec = None
    d = RUN2 / f.name.replace(".", "_")
    if d.is_dir():
        j = next(d.glob("*.metasense.json"))
        rec = json.loads(j.read_text())["input"].get("sha256")
    text_ok, synthetic, headings = "", "", ""
    if sig(b) == "text":
        try:
            t = b.decode("utf-8"); text_ok = "yes"
            synthetic = "yes" if "synthetic sample paper" in t else "no"
            headings = len(re.findall(r"^(?:\d+\.\s+)?[A-Z][A-Za-z ]{2,40}$", t, re.M))
        except UnicodeDecodeError:
            text_ok = "no"
    rows.append({"file": f.name, "purpose": PURPOSE.get(f.name, "?"), "bytes": len(b), "signature": sig(b),
                 "utf8": text_ok, "self_labelled_synthetic": synthetic, "heading_like_lines": headings,
                 "sha256_now": sha[:16], "sha256_19oct_report": (rec or "")[:16],
                 "identical_to_19oct": ("yes" if rec == sha else "no") if rec else "n/a (no report)"})
w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
Path(sys.argv[1]).write_text(json.dumps(rows, indent=2))
