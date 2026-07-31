# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Generate CEC2011 seven-curve family-overlay convergence grids (CR-0001).

Complete supplement grids (fig:sconv-cec2011) covering all 22
real-world problems at their native dimensions (budget 150,000 FEs,
n = 25 runs), drawn under pre-registrations P1/P2/P3 of
``papers/build_prompt_phases/phase_04/exhibit_plan.csv`` (implemented
in ``papers/scripts/_convergence_common.py``).

Layout
------
    papers/figures/convergence/cec2011_a.{pdf,png}  ->  F1..F8   (4x2)
    papers/figures/convergence/cec2011_b.{pdf,png}  ->  F9..F16  (4x2)
    papers/figures/convergence/cec2011_c.{pdf,png}  ->  F17..F22 (3x2)

Every panel overlays the full 7-algorithm GSK-family (P1 order: GSK,
AGSK, APGSK, FDB-AGSK, ATMALS-GSK, eGSK, DT-GSK); every curve is the
per-checkpoint MEAN across all runs (P2), read from
``benchmarks/cec_reference_results/cec2011/<alg>/gen_logs/``.

CEC2011 reports raw objective values; problems F2/F5/F6/F10 have
negative optima, so those panels fall back from the log y-axis to a
linear axis with an in-panel disclosure (documented in the companion
log).  Missing algorithms are disclosed in-panel and in
``papers/figures/convergence/cec2011_missing.log`` -- never fabricated.

Re-generate via::

    python papers/scripts/generate_cec2011_convergence.py
"""
from __future__ import annotations

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
    legend_handles,
    plot_family_panel,
    save_figure,
    write_missing_log,
)

_SUITE = "cec2011"
_MISSING_LOG = OUT_DIR / "cec2011_missing.log"

# CEC2011 native dimensions per problem (fixed by the benchmark
# definition; matches the ``_D<native>`` key in every checkpoint
# filename across all seven algorithms).
_NATIVE_DIM: dict[int, int] = {
    1: 6,    2: 30,   3: 1,    4: 1,    5: 30,   6: 30,
    7: 20,   8: 7,    9: 126,  10: 12,  11: 120, 12: 240,
    13: 6,   14: 13,  15: 15,  16: 40,  17: 140, 18: 96,
    19: 96,  20: 96,  21: 26,  22: 22,
}


def _render_grid(
    func_ids: list[int],
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
        dim = _NATIVE_DIM[fid]
        plot_family_panel(
            axes_flat[idx], _SUITE, fid, dim,
            missing=missing, panel_counts=panel_counts,
            panel_key=f"{out_stem.name}:F{fid}_D{dim}",
            title=f"F{fid} (D={dim})",
        )
    for idx in range(len(func_ids), n_rows * n_cols):
        axes_flat[idx].axis("off")

    handles, labels = legend_handles()
    # SE-005: ncol=7 overruns the 443.88 pt canvas and exact_size=True clips it,
    # losing the DT-GSK label (last in the fixed order). Two rows fit.
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8,
               frameon=False, columnspacing=1.1, handlelength=2.6)
    fig.tight_layout(h_pad=1.4, w_pad=2.0, rect=(0, 0.085, 1, 1))
    for p in save_figure(fig, out_stem, exact_size=True):
        print(f"wrote {p}")
    plt.close(fig)


def main() -> None:
    missing: list[tuple[str, int, int]] = []
    panel_counts: dict[str, int] = {}

    # N-011: see generate_cec2013_convergence.py -- 8.4 in wide against a
    # 6.165 in text block meant every grid was scaled by 0.734 at placement,
    # dropping 9 pt source text to ~6.6 pt on the page. Sized to the box now,
    # heights scaled by the same factor so panel aspect and grouping are kept.
    groups = [
        ("a", list(range(1, 9)),   4, 2, (6.165, 7.41)),
        ("b", list(range(9, 17)),  4, 2, (6.165, 7.41)),
        ("c", list(range(17, 23)), 3, 2, (6.165, 5.72)),
    ]
    for suffix, fids, n_rows, n_cols, figsize in groups:
        _render_grid(
            fids, OUT_DIR / f"cec2011_{suffix}",
            n_rows=n_rows, n_cols=n_cols, figsize=figsize,
            missing=missing, panel_counts=panel_counts,
        )

    write_missing_log(_MISSING_LOG, "CEC2011", missing, panel_counts)


if __name__ == "__main__":
    main()
