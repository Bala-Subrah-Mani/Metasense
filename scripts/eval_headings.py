"""T-07: evaluate methodology-heading detection against the labeled heading-variant set.

Each heading is placed in a minimal document (blank line, heading, one body sentence) and
run through the real section detector. A heading counts as predicted-methodology if the
detector labels it 'methodology' or 'experiments'. Prints a confusion matrix, precision,
recall and F1, and every misclassified heading. Exit code 0 always (this is a measurement).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from metasense.processing.section_detector import METHODOLOGY_LABELS, detect_sections  # noqa: E402


def main() -> int:
    path = ROOT / "data" / "annotations" / "heading_variants.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    tp = fp = fn = tn = 0
    errors, details = [], []
    for row in rows:
        lines = ["", row["heading"], "This sentence is body text for the section."]
        sections, unknown = detect_sections(lines)
        heading_secs = [s for s in sections if s.label != "front_matter"]
        label = heading_secs[0].label if heading_secs else "not_detected_as_heading"
        pred = int(label in METHODOLOGY_LABELS)
        gold = int(row["gold_is_methodology"])
        tp += pred and gold
        fp += pred and not gold
        fn += (not pred) and gold
        tn += (not pred) and (not gold)
        details.append({"heading": row["heading"], "gold": gold, "pred": pred, "label": label})
        if pred != gold:
            errors.append(f"  {'FN' if gold else 'FP'}: {row['heading']!r} -> {label} ({row['note']})")
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    print(f"Heading-variant evaluation: {len(rows)} headings ({tp + fn} methodology, {fp + tn} other)")
    print(f"TP={tp} FP={fp} FN={fn} TN={tn}")
    print(f"Precision={precision:.3f} Recall={recall:.3f} F1={f1:.3f}")
    print("Misclassified:" if errors else "Misclassified: none")
    print("\n".join(errors))
    if "--json" in sys.argv:
        print(json.dumps({"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": precision,
                          "recall": recall, "f1": f1, "details": details}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
