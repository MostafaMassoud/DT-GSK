# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Generate CEC2017 seven-curve family-overlay convergence grids (CR-0001).

Two exhibit families, both drawn under pre-registrations P1/P2/P3 of
``papers/build_prompt_phases/phase_04/exhibit_plan.csv`` (implemented in
``papers/scripts/_convergence_common.py``):

Main text (fig:conv-cec2017-d30 / fig:conv-cec2017-d100)
    One 2x2 grid per featured dimension containing exactly the four
    functions pre-registered by rule P5 and FROZEN in
    ``papers/build_prompt_phases/phase_05/curve_selection.csv``
    (``selected_for_main == TRUE``).  The selection file is the single
    source of truth: it is read, never re-derived; if it is missing or
    malformed this script HARD-FAILS.

    papers/figures/convergence/main_cec2017_D30.{pdf,png}
    papers/figures/convergence/main_cec2017_D100.{pdf,png}

Supplement (fig:sconv-cec2017-d<D>, complete per-function grids)
    Four 4x2 sub-figures per dimension covering all 29 functions
    (F2 excluded from CEC2017 per protocol); see PANEL_GROUPS below,
    which is the single source of truth for this partition:

    papers/figures/convergence/all_funcs_D<D>_a.{pdf,png}  ->  F1, F3..F9
    papers/figures/convergence/all_funcs_D<D>_b.{pdf,png}  ->  F10..F17
    papers/figures/convergence/all_funcs_D<D>_c.{pdf,png}  ->  F18..F25
    papers/figures/convergence/all_funcs_D<D>_d.{pdf,png}  ->  F26..F30

    for every D in {10, 30, 50, 100}.  The 4x2 geometry is required for
    legibility at the supplement's text-box size (see N-011 note in main()).

Every panel overlays the full 7-algorithm GSK-family (P1 order: GSK,
AGSK, APGSK, FDB-AGSK, ATMALS-GSK, eGSK, DT-GSK); every curve is the
per-checkpoint MEAN error across all runs (P2), read from
``benchmarks/cec_reference_results/cec2017/<alg>/gen_logs/``.  Missing
algorithms are disclosed in-panel and in the companion log
``papers/figures/convergence/cec2017_missing.log`` -- never fabricated.

Re-generate via::

    python papers/scripts/generate_full_convergence.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "matplotlib is required; install via `pip install matplotlib` "
        f"({exc})"
    )

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _convergence_common import (  # noqa: E402
    OUT_DIR,
    REPO,
    legend_handles,
    plot_family_panel,
    save_figure,
    write_missing_log,
)

_SUITE = "cec2017"
_DIMS = (10, 30, 50, 100)
_SELECTION_CSV = (REPO / "papers" / "build_prompt_phases" / "phase_05"
                  / "curve_selection.csv")
_MISSING_LOG = OUT_DIR / "cec2017_missing.log"

# Panel partition of the 29 scored CEC2017 functions across the supplement
# grids (F2 excluded per protocol).  Single source of truth: this module
# renders the panels and generate_artifact_binding.py imports PANEL_GROUPS to
# describe their provenance, so the two can no longer drift apart.  Changing
# the layout here requires re-running generate_artifact_binding.py.
PANEL_GROUPS: list[tuple[str, list[int]]] = [
    ("a", [1, 3, 4, 5, 6, 7, 8, 9]),      # F2 excluded per protocol
    ("b", list(range(10, 18))),
    ("c", list(range(18, 26))),
    ("d", list(range(26, 31))),
]
assert sum(len(f) for _, f in PANEL_GROUPS) == 29, (
    "all 29 scored functions must be covered")


def _load_main_selection() -> dict[int, list[int]]:
    """Read the FROZEN P5 selection; HARD FAIL if absent or malformed."""
    if not _SELECTION_CSV.exists():
        raise SystemExit(
            f"HARD FAIL: pre-registered selection file missing: "
            f"{_SELECTION_CSV} -- the P5 selection is read, never"
            " re-derived."
        )
    picks: dict[int, list[int]] = {}
    with _SELECTION_CSV.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("suite") != _SUITE:
                continue
            if str(row.get("selected_for_main", "")).strip().upper() != "TRUE":
                continue
            picks.setdefault(int(row["dimension"]), []).append(
                int(row["function"]))
    for dim, funcs in sorted(picks.items()):
        if len(funcs) != 4:
            raise SystemExit(
                f"HARD FAIL: curve_selection.csv lists {len(funcs)}"
                f" selected functions for D{dim} (expected exactly 4):"
                f" {sorted(funcs)}"
            )
        picks[dim] = sorted(funcs)
    if not picks:
        raise SystemExit(
            "HARD FAIL: curve_selection.csv contains no"
            " selected_for_main rows for cec2017."
        )
    return picks


def _render_grid(
    func_ids: list[int],
    dim: int,
    out_stem: Path,
    *,
    n_rows: int,
    n_cols: int,
    figsize: tuple[float, float],
    missing: list[tuple[str, int, int]],
    panel_counts: dict[str, int],
) -> None:
    """Render one family-overlay grid with a single shared legend."""
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    axes_flat = list(fig.axes)

    for idx, fid in enumerate(func_ids):
        plot_family_panel(
            axes_flat[idx], _SUITE, fid, dim,
            missing=missing, panel_counts=panel_counts,
            panel_key=f"{out_stem.name}:F{fid}_D{dim}",
            title=f"F{fid} (D={dim})",
        )
    for idx in range(len(func_ids), n_rows * n_cols):
        axes_flat[idx].axis("off")

    handles, labels = legend_handles()
    # SE-005: seven labels on one row overrun the 6.165 in (443.88 pt) canvas,
    # and save_figure(exact_size=True) skips bbox_inches="tight", so the overflow
    # is CLIPPED rather than re-cropped -- the last entry in the fixed P1 order is
    # DT-GSK, so the proposed method's own curve lost its label in every figure.
    # Two rows (ncol=4) fit inside the canvas; rect reserves the extra height.
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8,
               frameon=False, columnspacing=1.1, handlelength=2.4)
    # 0.075 was tuned for the 7.4 in canvas (= 0.56 in absolute); keep the
    # reserved legend strip constant in inches across the new per-group heights.
    fig.tight_layout(h_pad=1.4, w_pad=2.0,
                     rect=(0, min(0.14, 0.56 / figsize[1]), 1, 1))
    for p in save_figure(fig, out_stem, exact_size=True):
        print(f"wrote {p}")
    plt.close(fig)


def main() -> None:
    missing: list[tuple[str, int, int]] = []
    panel_counts: dict[str, int] = {}

    # ---- main-text grids (P5 frozen selection, 2x2 per featured dim) ----
    for dim, funcs in sorted(_load_main_selection().items()):
        _render_grid(
            funcs, dim, OUT_DIR / f"main_cec2017_D{dim}",
            # N-011: sized to the text block like the supplement grids below.
            n_rows=2, n_cols=2, figsize=(6.165, 4.55),
            missing=missing, panel_counts=panel_counts,
        )

    # ---- supplement grids (all 29 functions, every dimension) ----
    #
    # N-011. These were 5x2 at 8.4 x 12.6 in, embedded with
    # width=\textwidth,height=0.87\textheight,keepaspectratio. The supplement's
    # box is 443.86 pt (6.165 in) x 684.15 pt, so 0.87\textheight = 8.267 in and
    # the placement scale was min(6.165/8.4, 8.267/12.6) = 0.656 -- BOTH
    # dimensions overflowed, height worst. That mapped 9 pt source text to the
    # 5.9 pt measured in the rendered PDF, well under the ~8 pt readability bar.
    # Earlier font bumps could not fix it because the shrink happens at
    # placement, after the fonts are set.
    #
    # The figure is now sized to the box it is actually given, so the scale is
    # 1.0 and source point sizes survive to the page. 4x2 fits comfortably
    # (4 x 1.85 = 7.4 in < 8.267 in) and costs fewer extra pages than 3x2.
    for dim in _DIMS:
        for suffix, fids in PANEL_GROUPS:
            # Audit 2026-07-23: group "d" holds only 5 functions; on the fixed
            # 4x2 canvas the empty fourth row left a ~1.7 in blank band above a
            # detached bottom-anchored legend.  Size each grid to its real row
            # count (a-c stay 4x2 / 7.4 in; d becomes 3x2 / 5.55 in).
            rows = (len(fids) + 1) // 2
            _render_grid(
                fids, dim, OUT_DIR / f"all_funcs_D{dim}_{suffix}",
                n_rows=rows, n_cols=2, figsize=(6.165, 1.85 * rows),
                missing=missing, panel_counts=panel_counts,
            )

    write_missing_log(_MISSING_LOG, "CEC2017", missing, panel_counts)


if __name__ == "__main__":
    main()
