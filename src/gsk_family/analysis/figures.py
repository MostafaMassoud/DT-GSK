"""Publication figures for the GSK-family statistical comparison.

Renders two matplotlib (Agg backend) figures directly from the structured
Friedman mean ranks produced by
:func:`gsk_family.analysis.statistical_tests.friedman_rank_test`:

* a Demsar-style **Nemenyi critical-difference (CD) diagram**, and
* a **Friedman mean-rank bar chart**.

Both consume a plain ``{algorithm: mean_rank}`` mapping so they stay decoupled
from result loading. The proposed algorithm (``dt-gsk`` by default) is drawn in
a deep-blue accent; every comparator uses a uniform slate grey, matching the
ATMALS-GSK 2025 ranking-plot palette ported from the source paper scripts.

The Nemenyi critical difference is the two-tailed post-hoc threshold::

    CD = q_alpha * sqrt(k * (k + 1) / (6 * N))

where ``k`` is the number of algorithms, ``N`` the number of benchmark
functions, and ``q_alpha`` the studentized-range quantile for Nemenyi's test
at level ``alpha`` (Demsar 2006, Table 5).
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Mapping

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (must follow matplotlib.use)
import numpy as np  # noqa: E402

# Studentized-range critical values for Nemenyi's test at alpha = 0.05
# (two-tailed). Demsar 2006 Table 5 for k <= 10, extended via the
# studentized-range distribution for k = 11..20 as a defensive margin.
Q_ALPHA_005_TABLE: dict[int, float] = {
    2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850,
    7: 2.949, 8: 3.031, 9: 3.102, 10: 3.164,
    11: 3.219, 12: 3.268, 13: 3.313, 14: 3.354, 15: 3.391,
    16: 3.426, 17: 3.458, 18: 3.489, 19: 3.517, 20: 3.544,
}

# ATMALS-GSK 2025 ranking-plot palette.
HEADLINE_COLOUR = "#1F4E9D"  # deep blue — proposed-algorithm highlight
COHORT_COLOUR = "#6E7B8B"    # slate grey — all comparators


def _normalize_label(label: str) -> str:
    """Return a comparison key with case and hyphens/underscores removed."""
    return label.replace("-", "").replace("_", "").upper()


def is_proposed(label: str, proposed: str = "dt-gsk") -> bool:
    """Return True when *label* names the proposed algorithm (case/hyphen/underscore-insensitive).

    The proposed algorithm is DT-GSK, with run identifier ``dt-gsk`` in both the
    released results and the display layer; ``DT-GSK``/``dt_gsk``/``dt-gsk`` all match.
    """
    return _normalize_label(label) == _normalize_label(proposed)


def nemenyi_critical_difference(k: int, n_funcs: int, q_alpha: float | None = None) -> float:
    """Return the Nemenyi critical difference for *k* algorithms over *n_funcs* problems.

    Parameters
    ----------
    k : int
        Number of algorithms in the panel.
    n_funcs : int
        Number of benchmark functions (paired problems).
    q_alpha : float, optional
        Studentized-range quantile. When omitted, the alpha = 0.05 value for
        *k* is looked up in :data:`Q_ALPHA_005_TABLE`.

    Returns
    -------
    float
        ``q_alpha * sqrt(k * (k + 1) / (6 * n_funcs))``.

    Raises
    ------
    ValueError
        If *k* < 2, *n_funcs* < 1, or no tabulated quantile exists for *k*.
    """
    if k < 2:
        raise ValueError(f"Need at least 2 algorithms for a CD, got k={k}.")
    if n_funcs < 1:
        raise ValueError(f"Need at least 1 function, got n_funcs={n_funcs}.")
    if q_alpha is None:
        if k not in Q_ALPHA_005_TABLE:
            raise ValueError(
                f"No tabulated q_alpha for k={k}; supported k=2..{max(Q_ALPHA_005_TABLE)}."
            )
        q_alpha = Q_ALPHA_005_TABLE[k]
    return q_alpha * math.sqrt(k * (k + 1) / (6.0 * n_funcs))


def _sorted_best_first(mean_ranks: Mapping[str, float]) -> tuple[list[str], list[float]]:
    """Return (labels, values) sorted by ascending mean rank (best first)."""
    pairs = sorted(mean_ranks.items(), key=lambda kv: kv[1])
    return [p[0] for p in pairs], [p[1] for p in pairs]


def render_cd_diagram(
    mean_ranks: Mapping[str, float],
    *,
    n_funcs: int,
    out_path: str | Path,
    suite: str = "CEC2017",
    dim: int | None = None,
    proposed: str = "dt-gsk",
    q_alpha: float | None = None,
) -> float:
    """Render a Demsar-style horizontal critical-difference diagram.

    Each algorithm's mean Friedman rank is drawn as a horizontal bar (best rank
    at the top) and a critical-difference scale bar is drawn in a buffer strip
    above the top-ranked row. The figure format follows ``out_path``'s suffix.

    Parameters
    ----------
    mean_ranks : Mapping[str, float]
        ``{algorithm: mean_rank}`` (lower rank is better).
    n_funcs : int
        Number of benchmark functions used to compute the ranks (the ``N`` in
        the CD formula).
    out_path : str or Path
        Destination figure path; the matplotlib format is inferred from its
        suffix (``.png``, ``.pdf``, ...).
    suite : str
        Benchmark suite label for the title.
    dim : int, optional
        Problem dimension for the title.
    proposed : str
        Name of the proposed algorithm to highlight.
    q_alpha : float, optional
        Override studentized-range quantile (see
        :func:`nemenyi_critical_difference`).

    Returns
    -------
    float
        The computed critical difference.
    """
    labels, values = _sorted_best_first(mean_ranks)
    k_algs = len(labels)
    cd = nemenyi_critical_difference(k_algs, n_funcs, q_alpha)

    palette = [HEADLINE_COLOUR if is_proposed(lbl, proposed) else COHORT_COLOUR for lbl in labels]
    best_rank = values[0]

    figsize = (6.4, max(3.4, 0.38 * k_algs + 1.6))
    fig, ax = plt.subplots(figsize=figsize)
    y = np.arange(k_algs)
    ax.barh(y, values, color=palette, edgecolor="white", linewidth=0.4, height=0.68)

    x_max = max(values)
    offset = x_max * 0.012
    for yi, val in zip(y, values):
        ax.text(val + offset, yi, f"{val:.2f}", va="center", ha="left", fontsize=8, color="#202020")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Mean Friedman rank (lower is better)", fontsize=10)
    ax.set_xlim(0, x_max * 1.22)
    ax.grid(axis="x", linestyle=":", alpha=0.35)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_linewidth(0.8)

    # CD scale bar in a buffer strip above the top-ranked row.
    ax.set_ylim(top=-1.7)
    cd_bar_y, cd_label_y, cap = -0.85, -1.35, 0.13
    ax.plot([best_rank, best_rank + cd], [cd_bar_y, cd_bar_y],
            color=HEADLINE_COLOUR, linewidth=2.0, solid_capstyle="butt")
    for xi in (best_rank, best_rank + cd):
        ax.plot([xi, xi], [cd_bar_y - cap, cd_bar_y + cap], color=HEADLINE_COLOUR, linewidth=2.0)
    ax.text((2 * best_rank + cd) / 2.0, cd_label_y, f"CD = {cd:.2f}",
            ha="center", va="center", fontsize=9, color=HEADLINE_COLOUR, fontweight="bold")

    dim_part = f"$D = {dim}$, " if dim is not None else ""
    ax.set_title(
        "Nemenyi Critical Difference  "
        f"({suite}, {dim_part}$k = {k_algs}$, $N = {n_funcs}$, $\\alpha = 0.05$)",
        fontsize=10, fontweight="bold", pad=12,
    )

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return cd


def render_rank_chart(
    mean_ranks: Mapping[str, float],
    *,
    out_path: str | Path,
    title: str = "Friedman Mean Ranks (GSK-family panel)",
    proposed: str = "dt-gsk",
) -> None:
    """Render a horizontal Friedman mean-rank bar chart (best rank at the top).

    Parameters
    ----------
    mean_ranks : Mapping[str, float]
        ``{algorithm: mean_rank}`` (lower rank is better).
    out_path : str or Path
        Destination figure path; the format is inferred from its suffix.
    title : str
        Chart title.
    proposed : str
        Name of the proposed algorithm to highlight.
    """
    labels, values = _sorted_best_first(mean_ranks)
    # barh plots row 0 at the bottom; reverse so the best rank sits on top.
    labels = list(reversed(labels))
    values = list(reversed(values))
    n = len(labels)

    fig, ax = plt.subplots(figsize=(6.8, max(3.2, 0.42 * n)))
    colors = [HEADLINE_COLOUR if is_proposed(lbl, proposed) else COHORT_COLOUR for lbl in labels]
    y_pos = np.arange(n)
    bars = ax.barh(y_pos, values, color=colors, edgecolor="white", height=0.72)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Mean Friedman Rank", fontsize=10)
    ax.set_title(title, fontsize=10, fontweight="bold", pad=8)

    x_max = max(values)
    offset = x_max * 0.012
    for bar, rank in zip(bars, values):
        ax.text(bar.get_width() + offset, bar.get_y() + bar.get_height() / 2,
                f"{rank:.2f}", va="center", ha="left", fontsize=8, color="#202020")

    ax.grid(axis="x", linestyle=":", alpha=0.35)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_linewidth(0.8)
    ax.set_xlim(0, x_max * 1.14)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
