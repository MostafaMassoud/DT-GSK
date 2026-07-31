# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Shared CR-0001 seven-curve family-overlay convergence helpers.

Implements the Phase 4 pre-registrations that bind every convergence
exhibit (PAPER_BUILD_PROMPT Section 6.7; phase_04/exhibit_plan.csv):

P1  Panel composition and fixed legend order:
    gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk.
P2  Aggregation: per-checkpoint arithmetic MEAN across all runs per
    algorithm, read from the release-mirrored reference tree
    ``benchmarks/cec_reference_results/<suite>/<alg>/gen_logs/
    CheckpointErrors_<alg>_F<k>_D<dim>.csv`` (identical basis for all
    seven curves; no smoothing, no extrapolation past termination).
    A missing algorithm is a disclosed absence (panel note + companion
    missing-log entry), never fabricated or interpolated.
P3  Fixed algorithm -> color/linestyle map (Okabe-Ito colorblind-safe,
    grayscale-distinguishable), identical in every panel; DT-GSK black
    solid at 1.5x linewidth drawn on top; one shared legend per grid;
    log-error y-axis with a display-only floor for exact zeros.

The display-only log floor is ``LOG_FLOOR`` (1e-14): several orders of
magnitude below the CEC success threshold of 1e-8, so per-checkpoint
means that are exactly 0.0 render as a line along the floor
("converged to machine zero") instead of truncating mid-plot.  The
floor never enters any reported statistic.  Panels whose data contain
negative values (CEC2011 raw objectives on F2/F5/F6/F10) fall back to
a linear y-axis with an in-panel disclosure note.
"""
from __future__ import annotations

import csv
from pathlib import Path

import math

import numpy as np
from matplotlib import ticker
from matplotlib.lines import Line2D

import _fig_style
_fig_style.apply()

REPO = Path(__file__).resolve().parents[2]
REFERENCE_ROOT = REPO / "benchmarks" / "cec_reference_results"
OUT_DIR = REPO / "papers" / "figures" / "convergence"

# P1: fixed panel composition and legend order.
PANEL_ORDER: tuple[str, ...] = (
    "gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk", "dt-gsk",
)

DISPLAY: dict[str, str] = {
    "gsk": "GSK",
    "agsk": "AGSK",
    "apgsk": "APGSK",
    "fdb-agsk": "FDB-AGSK",
    "atmals-gsk": "ATMALS-GSK",
    "egsk": "eGSK",
    "dt-gsk": "DT-GSK",
}

# P3: fixed color/linestyle map (color, matplotlib linestyle, linewidth).
# Line weights (reader feedback 2026-07-23: thinner, clearer, less cluttered).
# 1.1 pt comparators keep the panels light; DT-GSK stays 1.5x for emphasis but
# is no longer the heavy 2.18 pt anchor it was.
BASE_LW = 1.1
ISM_LW = round(BASE_LW * 1.5, 3)
STYLE: dict[str, tuple[str, object, float]] = {
    "gsk":        ("#6E6E6E", (0, (1, 1.4)),                BASE_LW),  # dotted (darkened: #999999 sank into the dotted grid in greyscale)
    "agsk":       ("#E69F00", (0, (4, 2.2)),                BASE_LW),  # dashed
    "apgsk":      ("#56B4E9", (0, (5, 1.8, 1, 1.8)),        BASE_LW),  # dash-dot
    "fdb-agsk":   ("#009E73", (0, (4, 1.4, 1.5, 1.4)),      BASE_LW),  # long-short dash (was (2.2,1): read as AGSK's dash in greyscale)
    "atmals-gsk": ("#B0568B", (0, (8, 2.6)),                BASE_LW),  # long-dash (darkened for a >40 greyscale-luminance gap to AGSK)
    "egsk":       ("#0072B2", (0, (5, 1.6, 1, 1.6, 1, 1.6)), BASE_LW),  # dash-dot-dot
    "dt-gsk":    ("#000000", "solid",                      ISM_LW),   # solid 1.5x
}

# Display-only floor for log-scale plotting of exact-zero mean errors.
LOG_FLOOR = 1e-14


def checkpoint_path(suite: str, alg: str, func: int, dim: int) -> Path:
    """Release-mirrored checkpoint CSV path for (suite, alg, func, dim)."""
    return (REFERENCE_ROOT / suite / alg / "gen_logs"
            / f"CheckpointErrors_{alg}_F{func}_D{dim}.csv")


def load_mean_curve(
    suite: str, alg: str, func: int, dim: int,
) -> tuple[np.ndarray, np.ndarray] | None:
    """P2 aggregation: per-checkpoint mean across all runs, or ``None``.

    Reads ``CheckpointErrors_<alg>_F<func>_D<dim>.csv`` (header
    ``Run,Seed,E<evals>,...``) and averages every ``E<evals>`` column
    over the run rows.  Returns ``(evals, mean_errors)`` as float
    arrays, or ``None`` when the file is absent/empty (the caller must
    disclose the absence -- never fabricate).
    """
    path = checkpoint_path(suite, alg, func, dim)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.reader(fh) if r]
    if len(rows) < 2:
        return None
    header, data = rows[0], rows[1:]
    e_cols = [(i, int(h[1:])) for i, h in enumerate(header)
              if h.startswith("E") and h[1:].isdigit()]
    if not e_cols:
        return None
    idx = [i for i, _ in e_cols]
    try:
        errs = np.asarray(
            [[float(r[i]) for i in idx] for r in data], dtype=float)
    except (ValueError, IndexError):
        return None
    if errs.size == 0:
        return None
    evals = np.asarray([b for _, b in e_cols], dtype=float)
    return evals, errs.mean(axis=0)


def native_dim_for(suite: str, alg: str, func: int) -> int | None:
    """Native dimension recorded in the checkpoint filename (CEC2011)."""
    hits = sorted((REFERENCE_ROOT / suite / alg / "gen_logs").glob(
        f"CheckpointErrors_{alg}_F{func}_D*.csv"))
    if not hits:
        return None
    return int(hits[0].stem.rsplit("_D", 1)[1])


def legend_handles() -> tuple[list[Line2D], list[str]]:
    """Shared-legend handles/labels in the fixed P1 order."""
    handles, labels = [], []
    for alg in PANEL_ORDER:
        color, ls, lw = STYLE[alg]
        handles.append(Line2D([], [], color=color, linestyle=ls,
                              linewidth=lw, solid_capstyle="round",
                              dash_capstyle="round"))
        labels.append(DISPLAY[alg])
    return handles, labels


def plot_family_panel(
    ax,
    suite: str,
    func: int,
    dim: int,
    *,
    missing: list[tuple[str, int, int]],
    panel_counts: dict[str, int],
    panel_key: str,
    title: str,
) -> None:
    """Draw one seven-curve family-overlay panel onto ``ax``.

    Curves are drawn in P1 order so DT-GSK (last) lands on top.
    Absent algorithms are appended to ``missing`` as
    ``(alg, func, dim)`` and disclosed with an in-panel note.  The
    number of series actually drawn is recorded in
    ``panel_counts[panel_key]``.
    """
    curves: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    absent: list[str] = []
    for alg in PANEL_ORDER:
        loaded = load_mean_curve(suite, alg, func, dim)
        if loaded is None:
            absent.append(alg)
            missing.append((alg, func, dim))
            continue
        curves[alg] = loaded

    # Log-error y-axis (P3) with the display-only floor for zeros;
    # linear fallback (disclosed) when any mean is negative (CEC2011
    # raw objectives on problems with negative optima).
    use_log = bool(curves) and all(
        float(np.min(y)) >= 0.0 for _, y in curves.values())

    for alg in PANEL_ORDER:
        if alg not in curves:
            continue
        x, y = curves[alg]
        yv = np.maximum(y, LOG_FLOOR) if use_log else y
        color, ls, lw = STYLE[alg]
        is_dt = alg == "dt-gsk"
        ax.plot(x, yv, color=color, linestyle=ls, linewidth=lw,
                alpha=1.0 if is_dt else 0.85,
                solid_capstyle="round", dash_capstyle="round",
                solid_joinstyle="round", dash_joinstyle="round",
                zorder=10 if is_dt else 4)

    if use_log:
        ax.set_yscale("log")
        _tune_log_yticks(ax)
    else:
        ax.set_yscale("linear")
        # Audit 2026-07-23: at (0.02, 0.03) this note sat exactly where the
        # descending negative-objective curves plateau (struck through in
        # CEC2011 F2/F5/F6/F10).  Upper-right is empty on those panels, and
        # the white box keeps it legible even if a curve passes underneath.
        ax.text(0.98, 0.95, "linear scale (negative objectives)",
                transform=ax.transAxes, fontsize=7, color="#666666",
                ha="right", va="top", zorder=11,
                bbox=dict(facecolor="white", alpha=0.85,
                          edgecolor="none", pad=1.2))
    if absent:
        note = "no data: " + ", ".join(DISPLAY[a] for a in absent)
        ax.text(0.5, 0.05, note, transform=ax.transAxes, fontsize=7,
                color="#B02418", ha="center")

    ax.set_xscale("linear")
    ax.ticklabel_format(axis="x", style="sci", scilimits=(0, 0),
                        useMathText=True)
    ax.xaxis.get_offset_text().set_fontsize(8)
    ax.set_title(title, fontsize=10)
    ax.tick_params(axis="both", labelsize=9)
    ax.grid(True, which="major")
    ax.set_axisbelow(True)
    ax.set_xlabel("FEs", fontsize=10)
    # CEC2011's endpoint is the raw best objective (no published optima on
    # several problems), so its panels must never be labeled "error" -- log
    # axis or not (panel review R3-09, 2026-07-23).
    ax.set_ylabel("Mean objective" if suite == "cec2011"
                  else "Mean error", fontsize=10)

    panel_counts[panel_key] = len(curves)


def save_figure(fig, out_stem: Path, *, png_dpi: int = 300,
                exact_size: bool = False) -> list[Path]:
    """Save vector PDF primary + PNG (>=200 dpi) alternate; return paths.

    ``exact_size`` honours the figure's declared ``figsize`` instead of
    re-cropping with ``bbox_inches="tight"``.

    N-011: the tight bbox re-crops on save, so the written file is NOT the size
    the caller asked for -- a 6.165 in figure came out 7.364 in wide. Because
    the supplement embeds these with ``width=\\textwidth``, LaTeX then scaled
    them by 6.165/7.364 = 0.837 and 9 pt tick labels reached the page at 7.5 pt.
    Sizing a figure to its placement box is futile while the save step silently
    resizes it. ``tight_layout`` already arranges the content, so for those grids
    the crop is redundant as well as harmful.
    """
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    pdf = out_stem.with_suffix(".pdf")
    png = out_stem.with_suffix(".png")
    bbox = None if exact_size else "tight"
    fig.savefig(pdf, bbox_inches=bbox, metadata={"CreationDate": None})
    fig.savefig(png, bbox_inches=bbox, dpi=png_dpi)
    return [pdf, png]


def write_missing_log(
    log_path: Path,
    suite_label: str,
    missing: list[tuple[str, int, int]],
    panel_counts: dict[str, int],
) -> None:
    """Companion disclosure log: absences + per-panel series counts.

    Deterministic content (no timestamps).  Written even when nothing
    is missing so the disclosure is affirmative, not silent.
    """
    lines = [
        f"{suite_label} family-overlay convergence -- disclosure log",
        "Aggregation (P2): per-checkpoint mean across all runs per"
        " algorithm, from benchmarks/cec_reference_results/ gen_logs.",
        f"Display-only log floor for exact zeros: {LOG_FLOOR:g}"
        " (never enters any reported statistic).",
        "",
        "== Missing curves (disclosed absences; never fabricated) ==",
    ]
    if not missing:
        lines.append("  (none -- all panels carry the full 7-algorithm"
                     " family overlay)")
    else:
        for alg, func, dim in sorted(set(missing)):
            lines.append(f"  {DISPLAY[alg]} ({alg}): F{func} D{dim}")
    lines.append("")
    lines.append("== Per-panel series counts ==")
    for key in sorted(panel_counts):
        lines.append(f"  {key}: {panel_counts[key]}/7")
    lines.append("")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {log_path}")


# Below this many decades a log axis is linear to within ~6%, so the panel is
# ticked over its true range instead of being padded out to half a decade.
# 0.05 sits in the empty gap between the four pathological panels (<=0.0093 dec)
# and the next narrowest (0.096 dec), so the audited 0.1--0.4 band is untouched.
_ULTRA_NARROW_DEC = 0.05
# Relative span at or below which the seven curves count as coincident rather
# than merely close; such panels keep the padded (flat) view.
_COINCIDENT_REL = 1e-3


def _tune_log_yticks(ax) -> None:
    """One consistent log-y tick policy for every convergence panel.

    Matplotlib's defaults produced three different failure modes across the
    grids (audit 2026-07-23): sub-decade panels sprouted stacks of verbose
    4-significant-digit minor labels (unreadable at ~1.5 in panel height, and
    they squeezed the axes box out of column alignment); 1--2-decade panels
    got exactly ONE labeled tick; wide-span panels grew dense unlabeled minor
    ticks that rendered as solid dark blocks at the spine ends.

    Policy: >=2 in-range decade majors -> label decades only, keep short
    unlabeled (2,5) minors.  Otherwise label the (1,2,5) sub-decade points
    compactly; narrow spans (<0.4 decades) are first padded to half a
    decade so at least two labeled ticks always exist.  Spans under
    ``_ULTRA_NARROW_DEC`` skip that padding and are ticked linearly over their
    true range instead -- padding them flattens real structure into a single
    line (see the in-body note) -- unless the curves have coincided to within
    ``_COINCIDENT_REL``, where the flat rendering is the honest one.
    Display-only: curve data is never altered, and no branch here changes an
    axis scale or a plotted value.
    """
    lo, hi = ax.get_ylim()
    if lo <= 0 or hi <= lo:
        return
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())
    n_dec = math.floor(math.log10(hi)) - math.ceil(math.log10(lo)) + 1
    if n_dec >= 2:
        ax.yaxis.set_major_locator(ticker.LogLocator(base=10.0, numticks=6))
        ax.yaxis.set_minor_locator(
            ticker.LogLocator(base=10.0, subs=(2.0, 5.0), numticks=12))
        ax.tick_params(axis="y", which="minor", length=2)
        return
    span = math.log10(hi) - math.log10(lo)
    # Ultra-narrow spans that nonetheless carry real structure: keep the data's
    # OWN range (audit 2026-07-24).  The half-decade padding below is a fixed
    # target, so it does not scale down for spans far under 0.4: CEC2013 F8
    # (rotated Ackley) covers 0.0046 decades at D=30, and inflating that to 0.5
    # compresses the entire 21.17 -> 20.94 descent into ~1% of panel height.
    # All seven curves then superimpose and the panel reads as a single flat
    # line -- a genuine-stagnation result rendered as a broken plot.  Under
    # ~0.05 decades a log axis is linear to within 6%, so decade-anchored ticks
    # buy nothing and plain linear ticks over the true range are exact enough.
    #
    # Guarded by a RELATIVE-span floor: when the curves agree to better than
    # _COINCIDENT_REL they have genuinely coincided (CEC2011 F3 D1: all seven
    # within 3.5e-6 of each other), and stretching that across a full panel
    # would amplify last-digit noise into apparent structure.  Those keep the
    # padded view below, where a flat line is the honest rendering.
    if span < _ULTRA_NARROW_DEC and (hi - lo) / lo >= _COINCIDENT_REL:
        ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=4, min_n_ticks=2))
        ax.yaxis.set_minor_locator(ticker.NullLocator())
        fmt = ticker.ScalarFormatter(useOffset=False)
        fmt.set_scientific(not 1e-3 <= abs(hi) < 1e5)
        ax.yaxis.set_major_formatter(fmt)
        ax.yaxis.get_offset_text().set_fontsize(8)
        return
    if span < 0.4:
        mid = math.sqrt(lo * hi)
        half = 10.0 ** 0.25
        lo, hi = mid / half, mid * half
        ax.set_ylim(lo, hi)
        span = 0.5
    subs = (1.0, 2.0, 3.0, 5.0, 7.0) if span < 0.8 else (1.0, 2.0, 5.0)
    ax.yaxis.set_major_locator(
        ticker.LogLocator(base=10.0, subs=subs, numticks=12))
    # minor_thresholds=(inf, inf): label EVERY located major tick. The default
    # (1, 0.4) blanks non-decade coefficients once the view exceeds one decade,
    # which shipped panels with exactly one labeled tick (R3-08, 2026-07-23) --
    # the very failure mode the docstring promises is fixed.
    ax.yaxis.set_major_formatter(ticker.LogFormatterSciNotation(
        base=10.0, minor_thresholds=(math.inf, math.inf)))
    ax.yaxis.set_minor_locator(ticker.NullLocator())
