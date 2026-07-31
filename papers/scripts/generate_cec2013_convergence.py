# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Generate CEC2013 seven-curve family-overlay convergence grids (CR-0001).

Second-comparison-suite supplement grids (fig:sconv-cec2013-d30)
covering all 28 CEC2013 functions at one dimension (default D=30, the
only pre-registered CEC2013 convergence dimension per P4), drawn under
pre-registrations P1/P2/P3 of
``papers/build_prompt_phases/phase_04/exhibit_plan.csv`` (implemented
in ``papers/scripts/_convergence_common.py``).

Layout
------
    papers/figures/convergence/cec2013_a.{pdf,png}  ->  F1..F8    (4x2)
    papers/figures/convergence/cec2013_b.{pdf,png}  ->  F9..F16   (4x2)
    papers/figures/convergence/cec2013_c.{pdf,png}  ->  F17..F24  (4x2)
    papers/figures/convergence/cec2013_d.{pdf,png}  ->  F25..F28  (2x2)

Every panel overlays the full 7-algorithm GSK-family (P1 order: GSK,
AGSK, APGSK, FDB-AGSK, ATMALS-GSK, eGSK, DT-GSK); every curve is the
per-checkpoint MEAN error across all runs (P2), read from
``benchmarks/cec_reference_results/cec2013/<alg>/gen_logs/``.  Missing
algorithms are disclosed in-panel and in
``papers/figures/convergence/cec2013_missing.log`` -- never fabricated.

Re-generate via::

    python papers/scripts/generate_cec2013_convergence.py --dimension 30
"""
from __future__ import annotations

import argparse
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

_SUITE = "cec2013"
_N_FUNCS = 28


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
    # SE-005: ncol=7 overruns the 443.88 pt canvas and exact_size=True clips it,
    # losing the DT-GSK label (last in the fixed order). Two rows fit.
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8,
               frameon=False, columnspacing=1.1, handlelength=2.6)
    fig.tight_layout(h_pad=1.4, w_pad=2.0, rect=(0, 0.085, 1, 1))
    for p in save_figure(fig, out_stem, exact_size=True):
        print(f"wrote {p}")
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate CEC2013 family-overlay convergence grids.")
    parser.add_argument("--dimension", type=int, default=30,
                        help="Dimension to plot (default: 30).")
    args = parser.parse_args(argv)
    dim = args.dimension

    missing: list[tuple[str, int, int]] = []
    panel_counts: dict[str, int] = {}

    # N-011: widths were 8.4 in against a 6.165 in (443.86 pt) text block, so
    # \includegraphics scaled every grid by 6.165/8.4 = 0.734 and 9 pt source
    # text reached the page at ~6.6 pt. Sized to the box now (heights scaled by
    # the same factor to preserve panel aspect), so nothing is downscaled and
    # the group structure -- and therefore the supplement wiring -- is unchanged.
    groups = [
        ("a", list(range(1, 9)),   4, 2, (6.165, 7.41)),
        ("b", list(range(9, 17)),  4, 2, (6.165, 7.41)),
        ("c", list(range(17, 25)), 4, 2, (6.165, 7.41)),
        ("d", list(range(25, _N_FUNCS + 1)), 2, 2, (6.165, 3.96)),
    ]
    for suffix, fids, n_rows, n_cols, figsize in groups:
        _render_grid(
            fids, dim, OUT_DIR / f"cec2013_{suffix}",
            n_rows=n_rows, n_cols=n_cols, figsize=figsize,
            missing=missing, panel_counts=panel_counts,
        )

    write_missing_log(OUT_DIR / "cec2013_missing.log", f"CEC2013 D={dim}",
                      missing, panel_counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
