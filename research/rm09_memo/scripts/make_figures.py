"""RM-09 figures 2 and 3 (matplotlib, print/light). Reads results/*.json written by the analysis scripts."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parents[1]
BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1f1f1f", "#6b6b6b", "#e6e6e3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": INK})

# ---- Figure 2: causes of spurious headings
s = json.loads((HERE / "results" / "spurious_summary.json").read_text())
names = {"math_or_symbol": "Math or symbol line", "running_head": "Running head (authors/title)",
         "numbered_prose": "Numbered prose / list item", "other_caps": "Other ALL-CAPS (table/figure labels)",
         "other": "Other", "code_comment": "Code comment (Markdown rule)", "matcher_miss_real_heading": "Real heading (matcher artefact)",
         "broken_real_heading": "Real heading split by extraction", "table_or_figure": "Table row (✓/✗, digits)",
         "lower_level_heading": "Real sub-heading"}
items = sorted(s["by_cause"].items(), key=lambda kv: kv[1])
fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=200)
bars = ax.barh([names[k] for k, _ in items], [v for _, v in items], color=BLUE, height=0.62)
total = s["total_spurious"]
for b, (_, v) in zip(bars, items):
    ax.text(b.get_width() + 12, b.get_y() + b.get_height() / 2, f"{v}  ({100 * v / total:.1f}%)", va="center", fontsize=8.5, color=INK)
ax.set_xlim(0, 1750)
ax.set_xlabel("Spurious top-level headings (all 12 documents)")
ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
fig.tight_layout(); fig.savefig(HERE / "figures" / "fig2_spurious_causes.png"); plt.close(fig)

# ---- Figure 3: heading recall by stratum, shipped path (A) vs oracle headings (C), extended matcher
c = json.loads((HERE / "results" / "rm08_matcher_correction.json").read_text())
strata = [("E1", "ICML 2023\n(5 papers)"), ("E2", "AISTATS 2023\n(3)"), ("T", "COLT 2023\ntheory (2)"), ("S", "JOSS\nsoftware (2)")]
def rec(cond, st):
    g = m = 0
    for d, v in c[cond]["per_document"].items():
        if d.split("-")[0] == st:
            g += v["gold"]; m += v["matched_extended"]
    return m, g
fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=200)
w = 0.36
for i, (st, lab) in enumerate(strata):
    for j, (cond, col, name) in enumerate((("A", BLUE, "A: PDF via pypdf (as shipped)"), ("C", ORANGE, "C: reference headings given as clean lines"))):
        m, g = rec(cond, st)
        x = i + (j - 0.5) * (w + 0.03)
        ax.bar(x, m / g, width=w, color=col, label=name if i == 0 else None)
        ax.text(x, m / g + 0.02, f"{m}/{g}", ha="center", fontsize=8, color=INK)
ax.set_xticks(range(len(strata)), [l for _, l in strata])
ax.set_ylim(0, 1.12); ax.set_ylabel("Top-level heading recall")
ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
ax.legend(frameon=False, fontsize=8.5, loc="upper right")
fig.tight_layout(); fig.savefig(HERE / "figures" / "fig3_recall_by_stratum.png"); plt.close(fig)
print("ok")
