"""Regenerate the PDF/DOCX sample inputs from data/sample/paper_complete.txt.

Requires the dev dependencies (reportlab, python-docx). The generated files are committed,
so this only needs to be run if the source text changes.
"""
from __future__ import annotations

from pathlib import Path

import docx
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample"


def paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n") if p.strip()]


def is_heading(p: str) -> bool:
    return len(p.split()) <= 6 and not p.endswith(".")


def make_docx(src: Path, dst: Path) -> None:
    d = docx.Document()
    for i, p in enumerate(paragraphs(src.read_text(encoding="utf-8"))):
        if i == 0:
            d.add_heading(p, level=0)
        elif is_heading(p):
            d.add_heading(p, level=2 if p[:3].count(".") >= 1 and p[1] == "." and p[2].isdigit() else 1)
        else:
            d.add_paragraph(p)
    d.save(str(dst))


def make_pdf(src: Path, dst: Path, repeat_body: int = 1) -> None:
    styles = getSampleStyleSheet()
    story = []
    paras = paragraphs(src.read_text(encoding="utf-8"))
    body = paras[1:]
    story.append(Paragraph(paras[0], styles["Title"]))
    for r in range(repeat_body):
        for p in body:
            style = styles["Heading2"] if is_heading(p) else styles["BodyText"]
            if r > 0 and is_heading(p):
                p = f"{p}"  # headings repeat; used only for the performance sample
            story.append(Paragraph(p.replace("&", "&amp;").replace("<", "&lt;"), style))
            story.append(Spacer(1, 4))
    SimpleDocTemplate(str(dst), pagesize=letter, title=paras[0], author="MetaSense synthetic sample").build(story)


if __name__ == "__main__":
    src = SAMPLE / "paper_complete.txt"
    make_docx(src, SAMPLE / "paper_complete.docx")
    make_pdf(src, SAMPLE / "paper_complete.pdf")
    make_pdf(src, SAMPLE / "paper_long_perf.pdf", repeat_body=25)
    print("Wrote paper_complete.docx, paper_complete.pdf, paper_long_perf.pdf")
