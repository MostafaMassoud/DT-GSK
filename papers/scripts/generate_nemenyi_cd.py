"""Generate Nemenyi critical-difference (CD) diagrams for the CEC2017
GSK-family Friedman mean ranks at D = 10, 30, 50, and 100.

Phase 7 evidence lock: the UNROUNDED mean ranks are read exclusively
from the frozen Phase 6 analysis bundle::

    papers/analysis/rel-2026-07-10-262fc16c9/cec2017/friedman_ranks_cec2017_D<dim>.csv

(never from a rendered ``.tex`` table).  The critical difference is
cross-checked against the bundle's companion
``nemenyi_cd_cec2017_D<dim>.csv``; a mismatch is a hard failure.

A CD diagram is only emitted for a dimension whose Friedman omnibus
``p_value`` (as recorded in the bundle) is significant at
``alpha = 0.05``; a non-significant omnibus is disclosed on stdout and
the dimension is skipped (post-hoc without omnibus is inadmissible).

The critical difference is the Nemenyi two-tailed post-hoc threshold::

    CD = q_alpha * sqrt(k * (k + 1) / (6 * N))

where ``k`` is the number of algorithms, ``N`` is the number of
benchmark functions (blocks), and ``q_alpha`` is the studentized range
quantile for Nemenyi's test at level ``alpha``.  For ``k = 7`` and
``alpha = 0.05`` the standard table value is ``q_0.05 ~ 2.949``
(Demsar 2006, Table 5).

Output (vector PDF primary + >=200 dpi PNG alternate, deterministic
metadata)::

    papers/figures/nemenyi/nemenyi_cd_cec2017_D<dim>.pdf
    papers/figures/nemenyi/nemenyi_cd_cec2017_D<dim>.png

Usage::

    python papers/scripts/generate_nemenyi_cd.py
"""
from __future__ import annotations

import csv
import math
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import _fig_style
_fig_style.apply()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PAPER_DIR = SCRIPT_DIR.parent
RELEASE_ID = os.environ.get("GSK_REL_ID", "rel-2026-07-16-78f075cb0")
BUNDLE_DIR = PAPER_DIR / "analysis" / RELEASE_ID / "cec2017"
FIG_DIR = PAPER_DIR / "figures" / "nemenyi"

DIMS = [10, 30, 50, 100]
ALPHA = 0.05
PNG_DPI = 300  # >= 200 dpi per Phase 7 output contract

# P1 panel order (pre-registered) with paper-facing display labels
# (Phase 4 terminology glossary: eGSK capitalization, FDB-AGSK hyphen).
DISPLAY_NAME = {
    "gsk": "GSK",
    "agsk": "AGSK",
    "apgsk": "APGSK",
    "fdb-agsk": "FDB-AGSK",
    "atmals-gsk": "ATMALS-GSK",
    "egsk": "eGSK",
    "dt-gsk": "DT-GSK",
}

# ---------------------------------------------------------------------------
# Nemenyi test: studentized-range critical values at alpha = 0.05
# (two-tailed), Demsar 2006 Table 5 for k <= 10, extended via the
# Studentized-Range distribution for k = 11..20 as a defensive margin so
# the figure still renders if the panel ever grows beyond the current
# 7-algorithm GSK family.
# ---------------------------------------------------------------------------
Q_ALPHA_005_TABLE = {
    2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850,
    7: 2.949, 8: 3.031, 9: 3.102, 10: 3.164,
    11: 3.219, 12: 3.268, 13: 3.313, 14: 3.354, 15: 3.391,
    16: 3.426, 17: 3.458, 18: 3.489, 19: 3.517, 20: 3.544,
}

# ATMALS-GSK 2025 ranking-plot palette: a single deep-blue accent for
# the proposed algorithm and a uniform slate grey for every comparator.
HEADLINE_COLOUR = "#000000"  # solid black — DT-GSK highlight (fixed P3 convention: DT-GSK is black in every figure)
COHORT_COLOUR = "#6E7B8B"    # slate grey — all comparators


# ---------------------------------------------------------------------------
# Bundle readers
# ---------------------------------------------------------------------------
def read_friedman_ranks(dim: int) -> tuple[dict[str, float], int, float]:
    """Read unrounded mean ranks, block count, and omnibus p for one dim.

    Returns
    -------
    (ranks, n_blocks, p_value) where ``ranks`` maps display label ->
    unrounded mean rank.
    """
    path = BUNDLE_DIR / f"friedman_ranks_cec2017_D{dim}.csv"
    if not path.is_file():
        raise SystemExit(
            f"HARD FAIL: required Phase 6 bundle input missing: {path}."
        )
    ranks: dict[str, float] = {}
    n_blocks: int | None = None
    p_value: float | None = None
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            alg = row["algorithm"].strip()
            label = DISPLAY_NAME.get(alg, alg)
            ranks[label] = float(row["mean_rank"])
            n_blocks = int(row["n_blocks"])
            p_value = float(row["p_value"])
    if not ranks or n_blocks is None or p_value is None:
        raise SystemExit(f"HARD FAIL: no usable rows in {path}.")
    return ranks, n_blocks, p_value


def read_bundle_cd(dim: int) -> float:
    """Read the pre-computed critical difference from the bundle."""
    path = BUNDLE_DIR / f"nemenyi_cd_cec2017_D{dim}.csv"
    if not path.is_file():
        raise SystemExit(
            f"HARD FAIL: required Phase 6 bundle input missing: {path}."
        )
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit(f"HARD FAIL: empty bundle file {path}.")
    cds = {float(r["critical_difference"]) for r in rows}
    if len(cds) != 1:
        raise SystemExit(f"HARD FAIL: inconsistent CD values in {path}: {cds}.")
    return cds.pop()


# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
def compute_cd(k: int, n: int, q_alpha: float) -> float:
    """Return the Nemenyi critical difference at level alpha."""
    return q_alpha * math.sqrt(k * (k + 1) / (6.0 * n))


def render_cd_diagram(
    ranks: dict[str, float],
    cd: float,
    dim: int,
    n_blocks: int,
    out_stem: Path,
    *,
    figsize: tuple[float, float] | None = None,
) -> None:
    """Render a Demsar-style horizontal CD bar chart (PDF + PNG).

    The chart shows each algorithm's mean rank as a horizontal bar and
    a critical-difference scale bar in a buffer strip above the
    top-ranked row.  Bars are sorted with the best-ranked algorithm at
    the top.
    """
    k_algs = len(ranks)
    if figsize is None:
        figsize = (6.4, max(3.4, 0.38 * k_algs + 1.6))
    fig, ax = plt.subplots(figsize=figsize)
    within_cd = _draw_cd_on_ax(ax, ranks, cd, dim, n_blocks)
    fig.tight_layout()
    pdf_path = out_stem.with_suffix(".pdf")
    png_path = out_stem.with_suffix(".png")
    # Deterministic artifacts: strip the PDF CreationDate timestamp.
    fig.savefig(pdf_path, bbox_inches="tight",
                metadata={"CreationDate": None})
    fig.savefig(png_path, bbox_inches="tight", dpi=PNG_DPI)
    plt.close(fig)

    best_lbl = min(ranks.items(), key=lambda kv: kv[1])[0]
    print(f"  wrote {pdf_path}")
    print(f"  wrote {png_path}")
    print(f"  CD = {cd:.4f}  (k={k_algs}, q_0.05={Q_ALPHA_005_TABLE[k_algs]:.3f})")
    print(f"  within one CD of best ({best_lbl}): {', '.join(within_cd)}")


def _draw_cd_on_ax(ax, ranks: dict[str, float], cd: float, dim: int,
                   n_blocks: int, *, compact: bool = False,
                   show_xlabel: bool = True) -> list[str]:
    """Draw one Demsar-style CD bar chart onto ``ax``; return the
    within-one-CD-of-best cohort labels (best rank at the top)."""
    # Sort: best rank (smallest) at the top of the figure
    sorted_pairs = sorted(ranks.items(), key=lambda kv: kv[1])
    labels = [p[0] for p in sorted_pairs]
    values = [p[1] for p in sorted_pairs]
    k_algs = len(labels)

    palette = [
        HEADLINE_COLOUR if lbl == "DT-GSK" else COHORT_COLOUR
        for lbl in labels
    ]

    # Headline rank (smallest, index 0) and the within-one-CD cohort.
    best_rank = values[0]
    within_cd = [lbl for lbl, r in zip(labels, values) if r - best_rank <= cd]

    y = np.arange(len(labels))
    ax.barh(
        y, values,
        color=palette, edgecolor="white", linewidth=0.4, height=0.68,
    )

    # Outside-bar rank values.
    x_max = max(values)
    offset = x_max * 0.012
    for yi, val in zip(y, values):
        ax.text(
            val + offset, yi, f"{val:.2f}",
            va="center", ha="left", fontsize=9 if compact else 10,
            color="#202020",
        )

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10 if compact else 11)
    ax.invert_yaxis()  # best rank at the top
    if show_xlabel:
        # Compact panels drop the parenthetical: at ~2.9 in the full string
        # clips at the canvas edge under bbox_inches="tight"; the caption
        # carries "(lower is better)" once for the whole figure.
        ax.set_xlabel("Mean Friedman rank" if compact
                      else "Mean Friedman rank (lower is better)",
                      fontsize=9 if compact else 10)
    ax.set_xlim(0, x_max * 1.22)
    ax.grid(axis="x")
    ax.set_axisbelow(True)

    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_linewidth(0.8)

    # CD scale bar in a buffer strip above the top-ranked row.
    top_buffer = 1.7
    ax.set_ylim(top=-top_buffer)

    cd_bar_y = -0.85
    cd_label_y = -1.35
    cap = 0.13
    ax.plot(
        [best_rank, best_rank + cd],
        [cd_bar_y, cd_bar_y],
        color=HEADLINE_COLOUR, linewidth=2.0, solid_capstyle="butt",
    )
    for xi in (best_rank, best_rank + cd):
        ax.plot(
            [xi, xi], [cd_bar_y - cap, cd_bar_y + cap],
            color=HEADLINE_COLOUR, linewidth=2.0,
        )
    ax.text(
        (best_rank + best_rank + cd) / 2.0,
        cd_label_y,
        f"CD = {cd:.2f}",
        ha="center", va="center", fontsize=9 if compact else 10.5,
        color=HEADLINE_COLOUR,
    )

    if compact:
        # The 2x2 grid panels are ~2.9 in wide: the full parameter string
        # (k, N, alpha, suite) overprinted the neighbouring panel and made the
        # figure unreadable.  Panel titles carry ONLY the dimension; every
        # shared parameter lives once in the LaTeX caption.
        ax.set_title(f"$D = {dim}$", fontsize=10.5, pad=10)
    else:
        ax.set_title(
            "Nemenyi Critical Difference  "
            f"(CEC2017, $D = {dim}$, $k = {k_algs}$, $N = {n_blocks}$, "
            f"$\\alpha = {ALPHA}$)",
            fontsize=10, pad=12,
        )
    return within_cd


def render_cd_grid(panels: list[tuple[dict[str, float], float, int, int]],
                   out_stem: Path) -> None:
    """Render the per-dimension CD diagrams as one 2x2 vector panel
    (PDF + PNG), so the main text carries a single consolidated figure."""
    # SE-013: the grid was drawn at 11.4 in and embedded at 	extwidth
    # (443.88 pt = 6.165 in), a 0.525 scale that rendered 8-10 pt text at
    # 4.2-5.2 pt on the page. Draw at the embedded width so 1 pt = 1 pt.
    # 6.1 in matches the 6.165 in text block (placement scale ~1.0), which
    # gives each panel ~2.9 in of width: enough for the y labels and a single
    # bottom-row x label without cross-panel collisions.
    fig, axes = plt.subplots(2, 2, figsize=(6.1, 4.6))
    for i, (ax, (ranks, cd, dim, n_blocks)) in enumerate(
            zip(axes.flat, panels)):
        _draw_cd_on_ax(ax, ranks, cd, dim, n_blocks, compact=True,
                       show_xlabel=(i >= 2))
    # Hide any unused axes (defensive; expected exactly 4 significant dims).
    for ax in axes.flat[len(panels):]:
        ax.set_visible(False)
    fig.tight_layout(h_pad=1.6, w_pad=1.8)
    pdf_path = out_stem.with_suffix(".pdf")
    png_path = out_stem.with_suffix(".png")
    fig.savefig(pdf_path, bbox_inches="tight", metadata={"CreationDate": None})
    fig.savefig(png_path, bbox_inches="tight", dpi=PNG_DPI)
    plt.close(fig)
    print(f"  wrote {pdf_path}  (2x2 consolidated grid, {len(panels)} panels)")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    panels = []
    for dim in DIMS:
        print(f"D = {dim}:")
        ranks, n_blocks, p_value = read_friedman_ranks(dim)
        if p_value >= ALPHA:
            print(
                f"  DISCLOSED SKIP: Friedman omnibus not significant at "
                f"alpha={ALPHA} (p={p_value:.4g}); no CD diagram emitted "
                f"for D={dim}."
            )
            continue

        k_algs = len(ranks)
        if k_algs < 2:
            raise SystemExit(
                f"Need >= 2 algorithms to compute CD, got {k_algs}: "
                f"{list(ranks.keys())}"
            )
        if k_algs not in Q_ALPHA_005_TABLE:
            raise SystemExit(
                f"No tabulated q_alpha for k={k_algs}; extend "
                f"Q_ALPHA_005_TABLE (supported: k=2..{max(Q_ALPHA_005_TABLE)})."
            )
        q_alpha = Q_ALPHA_005_TABLE[k_algs]
        cd = compute_cd(k_algs, n_blocks, q_alpha)

        # Cross-check against the bundle's pre-computed CD.
        bundle_cd = read_bundle_cd(dim)
        if not math.isclose(cd, bundle_cd, rel_tol=1e-6, abs_tol=1e-9):
            raise SystemExit(
                f"HARD FAIL: recomputed CD {cd!r} disagrees with bundle CD "
                f"{bundle_cd!r} for D={dim}."
            )

        out_stem = FIG_DIR / f"nemenyi_cd_cec2017_D{dim}"
        render_cd_diagram(ranks, cd, dim, n_blocks, out_stem)
        panels.append((ranks, cd, dim, n_blocks))

    if panels:
        print("Consolidated 2x2 grid:")
        render_cd_grid(panels, FIG_DIR / "nemenyi_cd_cec2017_grid")


if __name__ == "__main__":
    main()
