"""Build the MDPI graphical abstract for the DT-GSK manuscript.

Original artwork drawn from scratch with matplotlib (no manuscript figure is
reused, per MDPI's GA rules). Every statement in the image is taken from the
shipped abstract: configuration selected by problem dimension, an adaptive
scaffold at every tier with the GSK vector-update equations retained, a
deterministic budget-exact final refinement at D >= 50, and the evaluation
scope (seven-member GSK family, five CEC suites, one budget-fair paired
protocol). No rank or superiority claim appears -- those carry Holm caveats
a graphical abstract cannot.

Output: papers/submission/DT-GSK-graphical-abstract.png at 2200 x 1120 px
(twice MDPI's 1100 x 560 minimum, same ratio), Arial text, PNG.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "papers" / "submission" / "DT-GSK-graphical-abstract.png"

plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.hashsalt"] = "dt-gsk-ga"

# palette
INK = "#1c2733"          # near-black text
MUTED = "#5c6b7a"        # secondary text
PANEL = "#f4f7fa"        # panel fill
EDGE = "#c9d4de"         # panel edge
T_LOW = "#8fb8de"        # low-D tier
T_MID = "#4f8fc0"        # mid-D tier
T_HIGH = "#1f5f8b"       # high-D tier
ACCENT = "#e8a33d"       # refinement amber
GREEN = "#3f8e63"        # evaluation green
ARROW = "#3a4a5a"

FIG_W, FIG_H, DPI = 11.0, 5.6, 200  # 2200 x 1120 px

fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=DPI)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 110)
ax.set_ylim(0, 56)
ax.axis("off")
ax.set_facecolor("white")
fig.patch.set_facecolor("white")


def box(x, y, w, h, fc, ec, lw=1.2, r=1.4, alpha=1.0, ls="-"):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0,rounding_size={r}",
                       fc=fc, ec=ec, lw=lw, alpha=alpha, linestyle=ls,
                       mutation_aspect=1.0)
    ax.add_patch(p)
    return p


def arrow(x1, y1, x2, y2, color=ARROW, lw=2.4, rad=0.0, style="-|>", ms=16):
    a = FancyArrowPatch((x1, y1), (x2, y2),
                        arrowstyle=style, mutation_scale=ms,
                        color=color, lw=lw,
                        connectionstyle=f"arc3,rad={rad}",
                        shrinkA=0, shrinkB=0)
    ax.add_patch(a)


# ------------------------------------------------------------------ header
ax.text(3.0, 52.6, "DT-GSK", fontsize=21, fontweight="bold", color=INK,
        va="center", ha="left")
ax.text(16.6, 52.6,
        "Dimension-Tiered Adaptive Configuration Selection and Deterministic "
        "Refinement\nfor Gaining-Sharing Knowledge-Based Optimization Algorithm",
        fontsize=9.6, color=MUTED, va="center", ha="left", linespacing=1.25)
ax.plot([3, 107], [49.4, 49.4], color=EDGE, lw=1.2)

# ------------------------------------------------- panel 1: dimension axis
P1_X, P1_Y, P1_W, P1_H = 3.0, 8.5, 27.5, 37.5
box(P1_X, P1_Y, P1_W, P1_H, PANEL, EDGE)
ax.text(P1_X + P1_W / 2, P1_Y + P1_H - 3.0, "One decision before the run",
        fontsize=10.5, fontweight="bold", color=INK, ha="center", va="center")
ax.text(P1_X + P1_W / 2, P1_Y + P1_H - 6.2,
        "the problem dimension D picks the tier",
        fontsize=9, color=MUTED, ha="center", va="center")

# vertical D axis with tier bands
AX_X = P1_X + 5.2
AX_Y0, AX_Y1 = P1_Y + 3.5, P1_Y + P1_H - 9.5
ax.plot([AX_X, AX_X], [AX_Y0, AX_Y1], color=INK, lw=1.6)
ax.plot([AX_X - 0.7, AX_X, AX_X + 0.7], [AX_Y1 - 1.2, AX_Y1, AX_Y1 - 1.2],
        color=INK, lw=1.6)
ax.text(AX_X, AX_Y1 + 1.4, "D", fontsize=9.5, fontweight="bold", color=INK,
        ha="center", va="center", fontstyle="italic")

bands = [
    (0.00, 0.30, T_LOW, "low D", "base scaffold only\n(dimension-gated\nsubsystems inactive)"),
    (0.34, 0.62, T_MID, "mid D", "tier profile for the\nmiddle regime"),
    (0.66, 1.00, T_HIGH, "high D", "tier profile plus the\nfinal refinement"),
]
BH = AX_Y1 - AX_Y0 - 2.0
for f0, f1, c, lab, desc in bands:
    y0 = AX_Y0 + f0 * BH
    h = (f1 - f0) * BH
    box(AX_X + 1.6, y0, 6.2, h, c, c, r=0.9)
    ax.text(AX_X + 4.7, y0 + h / 2, lab, fontsize=9.5, fontweight="bold",
            color="white", ha="center", va="center")
    ax.text(AX_X + 9.2, y0 + h / 2, desc, fontsize=8.2, color=INK,
            ha="left", va="center", linespacing=1.25)

for frac, t in [(0.05, "10"), (0.44, "30"), (0.66, "50"), (0.92, "100")]:
    y = AX_Y0 + frac * BH
    ax.plot([AX_X - 0.8, AX_X], [y, y], color=INK, lw=1.2)
    ax.text(AX_X - 1.2, y, t, fontsize=8, color=INK, ha="right", va="center")

# ------------------------------------------------- panel 2: the optimizer
P2_X, P2_Y, P2_W, P2_H = 36.5, 8.5, 33.0, 37.5
box(P2_X, P2_Y, P2_W, P2_H, PANEL, EDGE)
ax.text(P2_X + P2_W / 2, P2_Y + P2_H - 3.0, "One optimizer, tier-selected setup",
        fontsize=10.5, fontweight="bold", color=INK, ha="center", va="center")

# configuration card
box(P2_X + 2.5, P2_Y + 22.5, P2_W - 5, 7.6, "white", T_MID, lw=1.5)
ax.text(P2_X + P2_W / 2, P2_Y + 28.1, "tier-selected configuration",
        fontsize=9.5, fontweight="bold", color=T_HIGH, ha="center", va="center")
ax.text(P2_X + P2_W / 2, P2_Y + 25.1,
        "resolved from D before the first evaluation,\nthen frozen and hash-locked",
        fontsize=8.2, color=MUTED, ha="center", va="center", linespacing=1.25)

arrow(P2_X + P2_W / 2, P2_Y + 22.3, P2_X + P2_W / 2, P2_Y + 19.6)

# GSK scaffold card
box(P2_X + 2.5, P2_Y + 9.0, P2_W - 5, 10.4, "white", T_MID, lw=1.5)
ax.text(P2_X + P2_W / 2, P2_Y + 17.1, "adaptive GSK scaffold",
        fontsize=9.5, fontweight="bold", color=T_HIGH, ha="center", va="center")
ax.text(P2_X + P2_W / 2, P2_Y + 13.6,
        "junior and senior gaining-sharing phases;\n"
        "the GSK vector-update equations are retained\n"
        "at every tier",
        fontsize=8.2, color=INK, ha="center", va="center", linespacing=1.3)

arrow(P2_X + P2_W / 2, P2_Y + 8.8, P2_X + P2_W / 2, P2_Y + 6.4)

# refinement card (amber)
box(P2_X + 2.5, P2_Y + 1.6, P2_W - 5, 4.8, "#fdf3e2", ACCENT, lw=1.6)
ax.text(P2_X + P2_W / 2, P2_Y + 4.7, "deterministic final refinement",
        fontsize=9.5, fontweight="bold", color="#a86a12", ha="center", va="center")
ax.text(P2_X + P2_W / 2, P2_Y + 2.7,
        "budget-exact, runs once at D ≥ 50",
        fontsize=8.2, color=INK, ha="center", va="center")

# ------------------------------------------------- panel 3: evaluation
P3_X, P3_Y, P3_W, P3_H = 75.5, 8.5, 31.5, 37.5
box(P3_X, P3_Y, P3_W, P3_H, PANEL, EDGE)
ax.text(P3_X + P3_W / 2, P3_Y + P3_H - 3.0, "One budget-fair paired protocol",
        fontsize=10.5, fontweight="bold", color=INK, ha="center", va="center")
ax.text(P3_X + P3_W / 2, P3_Y + P3_H - 6.2,
        "seven GSK-family algorithms, re-executed",
        fontsize=9, color=MUTED, ha="center", va="center")

suites = [
    ("CEC 2017", "primary"),
    ("CEC 2011", "corroborative"),
    ("CEC 2013", "corroborative"),
    ("CEC 2020", "pre-registered"),
    ("CEC 2013 LSGO", "large-scale"),
]
CH_Y = P3_Y + P3_H - 10.6
for i, (name, role) in enumerate(suites):
    y = CH_Y - i * 4.6
    box(P3_X + 2.5, y - 1.7, 15.0, 3.5, "white", GREEN, lw=1.3, r=1.0)
    ax.text(P3_X + 10.0, y, name, fontsize=8.6, fontweight="bold",
            color=GREEN, ha="center", va="center")
    ax.text(P3_X + 18.6, y, role, fontsize=8.0, color=MUTED,
            ha="left", va="center")

ax.text(P3_X + P3_W / 2, P3_Y + 2.9,
        "matched budgets, paired seeds, nonparametric tests;\n"
        "all findings scoped to the GSK family",
        fontsize=8.2, color=INK, ha="center", va="center", linespacing=1.3)

# ------------------------------------------------- connecting arrows
arrow(P1_X + P1_W + 0.4, 27.2, P2_X - 0.4, 27.2, lw=3.0, ms=20)
arrow(P2_X + P2_W + 0.4, 27.2, P3_X - 0.4, 27.2, lw=3.0, ms=20, color=GREEN)

# footer strip
ax.text(55, 4.2,
        "Configuration chosen by dimension, not one operating point for "
        "every problem size",
        fontsize=9.6, color=INK, fontstyle="italic", ha="center", va="center")

OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=DPI, facecolor="white",
            metadata={"Software": None})
plt.close(fig)

from PIL import Image  # noqa: E402

im = Image.open(OUT)
print(f"wrote {OUT}  ({im.width} x {im.height} px)")
assert im.width >= 1100 and im.height >= 560, "below MDPI minimum"
assert abs(im.width / im.height - 1100 / 560) < 0.01, "wrong aspect ratio"
print("MDPI size check: OK (minimum 1100 x 560, ratio preserved)")
