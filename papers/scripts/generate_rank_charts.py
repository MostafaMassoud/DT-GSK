#!/usr/bin/env python3
"""Generate Friedman rank charts for the DT-GSK paper.

Phase 7 evidence lock -- inputs are read EXCLUSIVELY from:

* the frozen Phase 6 analysis bundle
  ``papers/analysis/rel-2026-07-10-262fc16c9/`` --
  ``cec2017/rank_trend_cec2017.csv`` (fig:rank-vs-dim),
  ``cec2017/friedman_ranks_cec2017_D<dim>.csv`` (fig:cec2017-ranks),
  ``cec2011/friedman_ranks_cec2011.csv`` (fig:cec2011-ranks); and
* the promoted benchmark export
  ``benchmarks/cec_reference_results/_paper_tables/T16.csv`` (itself
  exported exclusively from the same bundle, Phase 6 task 23, then
  promoted from results/paper_tables/ staging) for the legacy overall
  bar chart ``friedman_gsk_family``.

Outputs (vector PDF primary + >=200 dpi PNG alternate, deterministic
metadata) land in ``papers/figures/ranks/``.

Usage:
    python papers/scripts/generate_rank_charts.py
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import _fig_style
_fig_style.apply()

SCRIPT_DIR = Path(__file__).resolve().parent
PAPER_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = PAPER_DIR.parent

RELEASE_ID = os.environ.get("GSK_REL_ID", "rel-2026-07-16-78f075cb0")
BUNDLE_DIR = PAPER_DIR / "analysis" / RELEASE_ID
# Consumer input = the PROMOTED, frozen benchmark evidence (single source of
# truth), not the results/ staging that producers write.  Repointed from
# results/paper_tables -> benchmarks/cec_reference_results/_paper_tables.
# (Only the legacy friedman_gsk_family bar reads this; the other charts read
# the frozen analysis bundle above.)
STAGING_DIR = PROJECT_ROOT / "benchmarks" / "cec_reference_results" / "_paper_tables"

FIG_DIR = PAPER_DIR / "figures" / "ranks"

PNG_DPI = 300  # >= 200 dpi per Phase 7 output contract
PDF_METADATA = {"CreationDate": None}  # deterministic artifacts

# Shared design from _fig_style.apply(); this generator only pins the
# N-011 rule: "tight" re-crops on save, so the written file is not the
# declared figsize -- these came out 6.73 in against a 6.165 in text
# block and LaTeX scaled them by 0.916, dropping 7.2 pt source text to
# 6.6 pt. "standard" keeps figsize authoritative.
plt.rcParams.update({"savefig.bbox": "standard"})

# ---------------------------------------------------------------------------
# Pre-registered panel constants (exhibit_plan.csv P1/P3, binding)
# ---------------------------------------------------------------------------
# P1 panel order: fixed legend/table order in every exhibit.
PANEL_ORDER = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk", "dt-gsk"]

# Paper-facing display labels (Phase 4 terminology glossary: eGSK
# capitalization per CR-0003; FDB-AGSK hyphenated).
DISPLAY_NAME = {
    "gsk": "GSK",
    "agsk": "AGSK",
    "apgsk": "APGSK",
    "fdb-agsk": "FDB-AGSK",
    "atmals-gsk": "ATMALS-GSK",
    "egsk": "eGSK",
    "dt-gsk": "DT-GSK",
}

# P3 fixed algorithm -> color/linestyle map (Okabe-Ito; identical in
# every panel; dt-gsk solid black at 1.5x linewidth).
P3_COLOR = {
    "gsk": "#999999",
    "agsk": "#E69F00",
    "apgsk": "#56B4E9",
    "fdb-agsk": "#009E73",
    "atmals-gsk": "#CC79A7",
    "egsk": "#0072B2",
    "dt-gsk": "#000000",
}
P3_LINESTYLE = {
    "gsk": ":",                          # dotted
    "agsk": "--",                        # dashed
    "apgsk": "-.",                       # dash-dot
    "fdb-agsk": (0, (3, 1)),             # densely-dashed
    "atmals-gsk": (0, (8, 3)),           # long-dash
    "egsk": (0, (6, 2, 1, 2, 1, 2)),     # dash-dot-dot
    "dt-gsk": "-",                      # solid
}
# SE-045: the grouped bar chart encoded the seven algorithms by COLOUR ALONE, so
# it carried no information in greyscale print or to a colour-blind reader. These
# hatch patterns are a redundant channel on the same P1 order -- the palette is
# unchanged, nothing is re-coloured, and DT-GSK stays the solid-black anchor.
# SE-045 non-colour channel (reader feedback 2026-07-23): the grouped bar
# chart is colour-blind-safe by palette (Okabe-Ito) and greyscale-decodable by
# the fixed P1 bar order repeated in every dimension group -- GSK, AGSK, APGSK,
# FDB-AGSK, ATMALS-GSK, eGSK, DT-GSK, left to right -- so a reader can identify a
# bar by position without colour. Dense hatching (previously here) was retired as
# visual clutter; DT-GSK stays solid black as the proposed-method anchor.
# Audit 2026-07-23 (rank-vs-dimension line chart): AGSK/FDB-AGSK and
# APGSK/eGSK separated by hue alone with identical circle markers; in
# greyscale the pairs collapsed.  Distinct markers keep all seven series
# attributable (the chart has only four x positions, so markers stay clean).
P3_MARKER = {
    "gsk": "o", "agsk": "s", "apgsk": "^", "fdb-agsk": "D",
    "atmals-gsk": "v", "egsk": "P", "dt-gsk": "o",
}
BASE_LW = 1.4
P3_LINEWIDTH = {a: (1.5 * BASE_LW if a == "dt-gsk" else BASE_LW)
                for a in PANEL_ORDER}

# Single-panel ranking bar charts: DT-GSK highlighted in solid black to
# match the fixed P3 convention (DT-GSK is solid black in every
# multi-series panel), so the proposed method reads identically across all
# rank exhibits; the comparator pool is a neutral slate grey.
_COLOR_PROPOSED = "#000000"
_COLOR_OTHER = "#6E7B8B"

CEC2017_DIMS = [10, 30, 50, 100]


def _require(path: Path) -> Path:
    """Hard-fail (never silently skip) when a required input is absent."""
    if not path.is_file():
        raise SystemExit(
            f"HARD FAIL: required Phase 7 input missing: {path}. "
            "Admissible inputs are the frozen Phase 6 analysis bundle "
            f"{RELEASE_ID} and the promoted benchmark export "
            "benchmarks/cec_reference_results/_paper_tables/."
        )
    return path


def _save(fig: plt.Figure, stem: Path) -> None:
    """Save a figure as deterministic vector PDF + >=200 dpi PNG."""
    pdf_path = stem.with_suffix(".pdf")
    png_path = stem.with_suffix(".png")
    fig.savefig(pdf_path, format="pdf", metadata=PDF_METADATA)
    fig.savefig(png_path, format="png", dpi=PNG_DPI)
    plt.close(fig)
    print(f"  -> {pdf_path.name}")
    print(f"  -> {png_path.name}")


def _style_bar_axes(ax: plt.Axes) -> None:
    """Hairline x-grid only; thin spines; clean background."""
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_linewidth(0.8)


# ---------------------------------------------------------------------------
# Bundle readers
# ---------------------------------------------------------------------------
def read_friedman_bundle(path: Path) -> dict[str, float]:
    """Read algorithm -> unrounded mean rank from a bundle friedman CSV."""
    ranks: dict[str, float] = {}
    with _require(path).open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ranks[row["algorithm"].strip()] = float(row["mean_rank"])
    missing = [a for a in PANEL_ORDER if a not in ranks]
    if missing:
        raise SystemExit(
            f"HARD FAIL: {path} lacks panel algorithm(s) {missing}."
        )
    return ranks


def read_rank_trend(path: Path) -> dict[str, dict[int, float]]:
    """Read algorithm -> {dimension -> mean rank} from rank_trend CSV."""
    trend: dict[str, dict[int, float]] = {a: {} for a in PANEL_ORDER}
    with _require(path).open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            alg = row["algorithm"].strip()
            if alg in trend:
                trend[alg][int(row["dimension"])] = float(row["mean_rank"])
    for a in PANEL_ORDER:
        missing_dims = [d for d in CEC2017_DIMS if d not in trend[a]]
        if missing_dims:
            raise SystemExit(
                f"HARD FAIL: {path} lacks D={missing_dims} for '{a}'."
            )
    return trend


# ---------------------------------------------------------------------------
# Figure generators
# ---------------------------------------------------------------------------
def gen_rank_vs_dim() -> None:
    """fig:rank-vs-dim -- Friedman mean rank vs dimension (CEC2017)."""
    trend = read_rank_trend(BUNDLE_DIR / "cec2017" / "rank_trend_cec2017.csv")

    fig, ax = plt.subplots(figsize=(6.165, 3.8))
    x = np.arange(len(CEC2017_DIMS))
    for alg in PANEL_ORDER:  # P1 legend order
        ranks = [trend[alg][d] for d in CEC2017_DIMS]
        ax.plot(
            x, ranks,
            color=P3_COLOR[alg], linestyle=P3_LINESTYLE[alg],
            linewidth=P3_LINEWIDTH[alg],
            marker=P3_MARKER[alg], markersize=3.6,
            label=DISPLAY_NAME[alg],
        )

    ax.set_xticks(x)
    ax.set_xticklabels([f"D{d}" for d in CEC2017_DIMS])
    ax.set_xlabel("Problem dimension", fontsize=10)
    ax.set_ylabel("Mean Friedman rank\n(lower is better)", fontsize=10)
    # No internal headline: the LaTeX caption describes the chart.
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(
        loc="center left", bbox_to_anchor=(1.01, 0.5),
        frameon=False, fontsize=8,
    )

    fig.tight_layout()
    _save(fig, FIG_DIR / "rank_vs_dim_cec2017")


def gen_cec2017_rank_bars() -> None:
    """fig:cec2017-ranks -- grouped per-dimension mean-rank bar chart."""
    per_dim = {
        d: read_friedman_bundle(
            BUNDLE_DIR / "cec2017" / f"friedman_ranks_cec2017_D{d}.csv"
        )
        for d in CEC2017_DIMS
    }

    n_alg = len(PANEL_ORDER)
    n_dim = len(CEC2017_DIMS)
    group_w = 0.82
    bar_w = group_w / n_alg

    fig, ax = plt.subplots(figsize=(6.165, 3.8))
    x = np.arange(n_dim)
    for i, alg in enumerate(PANEL_ORDER):  # P1 order within each group
        vals = [per_dim[d][alg] for d in CEC2017_DIMS]
        ax.bar(
            x - group_w / 2 + (i + 0.5) * bar_w, vals, width=bar_w * 0.92,
            color=P3_COLOR[alg], edgecolor="#3A3A3A", linewidth=0.5,
            label=DISPLAY_NAME[alg],
        )

    ax.set_xticks(x)
    ax.set_xticklabels([f"D{d}" for d in CEC2017_DIMS])
    ax.set_xlabel("Problem dimension", fontsize=10)
    ax.set_ylabel("Mean Friedman rank\n(lower is better)", fontsize=10)
    # No internal headline: the LaTeX caption describes the chart.
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(
        loc="upper center", bbox_to_anchor=(0.5, -0.18),
        ncol=4, frameon=False, fontsize=8,
    )

    fig.tight_layout()
    _save(fig, FIG_DIR / "cec2017_mean_ranks")


def _gen_sorted_rank_barh(
    ranks_by_alg: dict[str, float], title: str, out_stem: Path,
) -> None:
    """Horizontal sorted mean-rank bar chart (ATMALS-2025 style)."""
    pairs = [(DISPLAY_NAME[a], ranks_by_alg[a]) for a in PANEL_ORDER]
    # Best (lowest rank) at the top: barh plots row 0 at the bottom, so
    # sort descending by rank.
    pairs.sort(key=lambda p: p[1], reverse=True)
    labels = [p[0] for p in pairs]
    values = [p[1] for p in pairs]

    n = len(labels)
    fig, ax = plt.subplots(figsize=(6.165, max(3.2, 0.42 * n)))
    colors = [
        _COLOR_PROPOSED if lbl == "DT-GSK" else _COLOR_OTHER
        for lbl in labels
    ]
    y_pos = np.arange(n)
    bars = ax.barh(y_pos, values, color=colors, edgecolor="white", height=0.72)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Mean Friedman rank (lower is better)", fontsize=10)
    # No internal headline (the LaTeX caption describes the chart); the
    # `title` parameter is retained for the console log only.
    _ = title

    x_max = max(values)
    offset = x_max * 0.012
    for bar, rank in zip(bars, values):
        ax.text(
            bar.get_width() + offset,
            bar.get_y() + bar.get_height() / 2,
            f"{rank:.2f}",
            va="center", ha="left", fontsize=8, color="#202020",
        )

    _style_bar_axes(ax)
    ax.set_xlim(0, x_max * 1.14)

    fig.tight_layout()
    _save(fig, out_stem)


def gen_cec2011_ranks() -> None:
    """fig:cec2011-ranks -- CEC2011 real-world-suite mean-rank bars."""
    ranks = read_friedman_bundle(
        BUNDLE_DIR / "cec2011" / "friedman_ranks_cec2011.csv"
    )
    _gen_sorted_rank_barh(
        ranks,
        "Friedman Ranking: GSK-Family Panel (CEC 2011, 22 Problems)",
        FIG_DIR / "cec2011_ranks",
    )


def gen_overall_bar_from_staging() -> None:
    """Legacy fig:friedman_bar_gsk -- overall CEC2017 rank bars (T16.csv)."""
    path = _require(STAGING_DIR / "T16.csv")
    # T16.csv carries staging display tags; map them back to panel keys.
    # The frozen staging CSV tags the proposed algorithm "DT-GSK" (its
    # immutable data label); "DT-GSK" is accepted too for regenerated tables.
    tag_to_key = {
        "GSK": "gsk", "AGSK": "agsk", "APGSK": "apgsk",
        "FDBAGSK": "fdb-agsk", "ATMALS-GSK": "atmals-gsk",
        "EGSK": "egsk", "DT-GSK": "dt-gsk",
    }
    ranks: dict[str, float] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = tag_to_key.get(row["Algorithm"].strip())
            if key is None:
                continue
            val = row["Overall_MeanRank"].strip()
            if not val or val.upper() == "N/A":
                continue
            ranks[key] = float(val)
    missing = [a for a in PANEL_ORDER if a not in ranks]
    if missing:
        raise SystemExit(f"HARD FAIL: {path} lacks panel rows {missing}.")
    _gen_sorted_rank_barh(
        ranks,
        "Friedman Ranking: GSK-Family Panel (CEC 2017, Overall)",
        FIG_DIR / "friedman_gsk_family",
    )


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Bundle:  {BUNDLE_DIR}")
    print(f"Staging: {STAGING_DIR}")
    print(f"Output:  {FIG_DIR}")
    print()

    print("fig:rank-vs-dim (rank_trend_cec2017.csv)")
    gen_rank_vs_dim()
    print("fig:cec2017-ranks (friedman_ranks_cec2017_D*.csv)")
    gen_cec2017_rank_bars()
    print("fig:cec2011-ranks (friedman_ranks_cec2011.csv)")
    gen_cec2011_ranks()
    print("fig:friedman_bar_gsk legacy overall chart (staging T16.csv)")
    gen_overall_bar_from_staging()

    print("\nDone.")


if __name__ == "__main__":
    main()
