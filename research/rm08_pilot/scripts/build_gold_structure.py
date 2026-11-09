"""RM-08 step 2: reference section structure (G1), independent of MetaSense's rules.

Source priority (PROTOCOL.md section 4, with deviation DEV-02):
  JOSS  -> top-level <sec> titles in the publisher's JATS XML (body only)
  PDF outline present -> top-level outline entries written by the authors' LaTeX/hyperref
  no outline -> typographic headings: lines whose first span is 12 pt bold (NimbusRomNo9L-Medi in the
                ICML template) and start with a section number or appendix letter.
Requires PyMuPDF (pymupdf) and pypdf. Writes research/rm08_pilot/labels/g1_structure.json.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pymupdf
from pypdf import PdfReader

HERE = Path(__file__).resolve().parents[1]
NUM = re.compile(r"^(?P<num>[0-9]+|[A-H])\.?\s+(?P<title>.+)$")


def from_jats(path: Path) -> list[dict]:
    root = ET.fromstring(path.read_bytes())
    body = root.find(".//body")
    return [{"num": "", "title": re.sub(r"\s+", " ", s.findtext("title") or "").strip()} for s in body.findall("sec")]


def from_outline(pdf: Path) -> list[dict]:
    out = []
    for item in PdfReader(str(pdf)).outline:
        if isinstance(item, list):
            continue  # nested = sub-sections
        out.append({"num": "", "title": re.sub(r"\s+", " ", item.title).strip()})
    return out


def from_typography(pdf: Path) -> list[dict]:
    out = []
    for page in pymupdf.open(str(pdf)):
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                spans = [s for s in line["spans"] if s["text"].strip()]
                if not spans:
                    continue
                first = spans[0]
                text = " ".join(s["text"].strip() for s in spans)
                m = NUM.match(text)
                if (round(first["size"]) == 12 and ("Medi" in first["font"] or "Bold" in first["font"])
                        and m and len(text) < 100 and not re.match(r"^[0-9A-H]+\.[0-9]", text)):
                    out.append({"num": m.group("num"), "title": m.group("title").strip()})
    return out


def main() -> int:
    pdf_dir = Path(sys.argv[1])
    manifest = list(csv.DictReader((HERE / "inputs" / "manifest.csv").open(encoding="utf-8")))
    gold = {}
    for row in manifest:
        pdf = pdf_dir / f"{row['doc_id']}.pdf"
        if row["stratum"] == "S":
            heads, src = from_jats(pdf_dir / f"{row['doc_id']}.jats"), "jats"
        else:
            heads, src = from_outline(pdf), "pdf_outline"
            if not heads:
                heads, src = from_typography(pdf), "typography_12pt_bold"
        gold[row["doc_id"]] = {"source": src, "headings": heads}
        print(f"{row['doc_id']:22} {src:22} {len(heads):3}  {[h['title'][:28] for h in heads][:6]}")
    out = HERE / "labels" / "g1_structure.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(gold, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
