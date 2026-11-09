"""Rule-based section detection (design component: Section Detector).

Baseline approach (deliberately transparent, to serve as the rule-based comparison
point required by the design review):
1. A line is a *heading candidate* if it is short and either numbered
   ("3.", "3.1", "III."), Markdown ("## "), ALL CAPS, or Title Case after a blank line.
2. The candidate's text is matched against a synonym table to assign a canonical label.
3. Numbered sub-headings with no label of their own inherit their parent's label.
4. Headings that look like headings but match nothing are labelled "unknown" and
   reported, so missed variants can be added later (test T-07).
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass

# Canonical label -> synonyms (lower-case, matched against the whole heading text).
SECTION_SYNONYMS: dict[str, list[str]] = {
    "abstract": ["abstract"],
    "introduction": ["introduction", "motivation", "overview"],
    "related_work": ["related work", "related works", "background", "literature review",
                     "prior work", "background and related work", "state of the art"],
    "methodology": ["methodology", "methods", "method", "materials and methods", "research design",
                    "research methodology", "research method", "research methods", "experimental setup",
                    "experimental design", "experiment setup", "study design", "approach",
                    "proposed approach", "proposed method", "our approach", "data and methods",
                    "evaluation methodology", "evaluation setup", "methods and materials",
                    "experimental methodology", "methodology and design"],
    "experiments": ["experiments", "experiment", "experimental evaluation", "empirical evaluation",
                    "evaluation", "experiments and results"],
    "results": ["results", "findings", "results and analysis", "analysis"],
    "discussion": ["discussion", "results and discussion"],
    "threats_to_validity": ["threats to validity", "limitations", "threats", "validity threats",
                            "limitations and threats to validity"],
    "conclusion": ["conclusion", "conclusions", "conclusion and future work", "future work",
                   "summary", "concluding remarks"],
    "references": ["references", "bibliography"],
    "acknowledgments": ["acknowledgments", "acknowledgements"],
}

# Labels whose body is treated as "methodology scope" by the assessment engine.
METHODOLOGY_LABELS = {"methodology", "experiments"}

_NUMBERING = re.compile(
    r"^(?P<num>(?:\d+(?:\.\d+)*\.?)|(?:[IVXLC]+\.)|(?:[A-H]\.))\s+(?P<title>.+)$"
)
_MARKDOWN = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.+)$")

_LOOKUP = {syn: label for label, syns in SECTION_SYNONYMS.items() for syn in syns}


@dataclass
class Section:
    heading: str
    label: str
    level: int
    start_line: int  # 1-based line number of the heading
    end_line: int  # 1-based, inclusive
    word_count: int = 0
    inherited: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


def _clean_title(title: str) -> str:
    title = title.strip().strip(":").strip()
    title = re.sub(r"\s+", " ", title)
    return title


def classify_heading(title: str) -> str:
    """Map a heading's text to a canonical label, or 'unknown'."""
    key = re.sub(r"[^a-z ]", "", _clean_title(title).lower()).strip()
    key = re.sub(r"\s+", " ", key)
    if key in _LOOKUP:
        return _LOOKUP[key]
    return "unknown"


def _heading_candidate(line: str, prev_blank: bool) -> tuple[str, int] | None:
    """Return (title, level) if the line looks like a heading, else None."""
    stripped = line.strip()
    if not stripped or len(stripped) > 80:
        return None
    md = _MARKDOWN.match(stripped)
    if md:
        return _clean_title(md.group("title")), len(md.group("hashes"))
    num = _NUMBERING.match(stripped)
    if num:
        title = _clean_title(num.group("title"))
        # Numbered list items in prose usually end with a period or are long sentences.
        if title.endswith(".") or len(title.split()) > 8:
            return None
        marker = num.group("num")
        level = marker.rstrip(".").count(".") + 1 if marker[0].isdigit() else 1
        return title, level
    words = stripped.split()
    if len(words) > 8 or stripped.endswith((".", ",", ";")):
        return None
    if stripped.isupper() and any(c.isalpha() for c in stripped):
        return _clean_title(stripped), 1
    # D-03 fix: PDF/DOCX extraction rarely leaves blank lines around headings, so a short
    # (<= 4 word) Title Case line is also accepted without a preceding blank line.
    title_case = all(w[0].isupper() or w.lower() in {"and", "of", "to", "the", "for", "in", "on"} for w in words if w[0].isalpha())
    if title_case and (prev_blank or len(words) <= 4):
        # Only accept if it maps to a known label, to avoid treating short title-cased
        # sentences/names as headings.
        title = _clean_title(stripped)
        if classify_heading(title) != "unknown":
            return title, 1
    return None


def detect_sections(lines: list[str]) -> tuple[list[Section], list[str]]:
    """Return (sections, unknown_headings). Text before the first heading is 'front_matter'."""
    sections: list[Section] = []
    unknown: list[str] = []
    parent_label = "front_matter"
    prev_blank = True
    for idx, line in enumerate(lines, start=1):
        cand = _heading_candidate(line, prev_blank)
        prev_blank = not line.strip()
        if cand is None:
            continue
        title, level = cand
        label = classify_heading(title)
        inherited = False
        if label == "unknown":
            if level > 1 and parent_label not in ("front_matter", "unknown"):
                label, inherited = parent_label, True
            else:
                unknown.append(title)
        if level == 1 and not inherited:
            parent_label = label
        if sections:
            sections[-1].end_line = idx - 1
        sections.append(Section(heading=title, label=label, level=level, start_line=idx, end_line=len(lines), inherited=inherited))

    if not sections or sections[0].start_line > 1:
        end = sections[0].start_line - 1 if sections else len(lines)
        sections.insert(0, Section(heading="(front matter)", label="front_matter", level=0, start_line=1, end_line=end))

    for sec in sections:
        body = lines[sec.start_line:sec.end_line] if sec.label != "front_matter" else lines[sec.start_line - 1:sec.end_line]
        sec.word_count = sum(len(l.split()) for l in body)
    return sections, unknown


def methodology_sections(sections: list[Section]) -> list[Section]:
    return [s for s in sections if s.label in METHODOLOGY_LABELS]
