#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Aggregate DT-GSK scaffold-ablation cells into the rank-summary matrix.

Reads the per-cell summaries produced by ``scripts/run_ablation.py``::

    <ablation-root>/<cell>/dt-gsk/cec2017/summary/dt-gsk_cec2017_D<dim>.csv

and writes the mean-Friedman-rank matrix the paper cites::

    results/ablation/ablation_matrix_rank_summary.csv

Columns: ``cell, mean_rank, delta_rank_vs_full, best_count, n_funcs,
wilcoxon_p, holm_p, significant`` -- one row per cell.  Ranks come from the
per-function Mean error across all cells (lower is better); the full-vs-cell
paired Wilcoxon is Holm-corrected across the disabled-component cells.

All statistics reuse ``gsk_family.analysis.statistics`` so this roll-up is
consistent with the rest of the paper's panel.  Nothing is fabricated: if no
cells are found the script reports that and exits without writing.

Usage::

    python papers/scripts/generate_ablation_matrix.py --dimension 30
    python papers/scripts/generate_ablation_matrix.py \
        --ablation-root benchmarks/cec_reference_results/_ablation/scaffold --full-cell baseline
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from gsk_family.analysis.statistics import (
    friedman_rank,
    holm_correction,
    load_summary,
    wilcoxon_paired,
)

_REPO = Path(__file__).resolve().parents[2]


def _cell_summary_dir(ablation_root: Path, cell: str, suite: str) -> Path:
    return ablation_root / cell / "dt-gsk" / suite / "summary"


def _load_cell_means(summary_dir: Path, suite: str, dim: int) -> dict[int, float] | None:
    """{func_id: Mean error} for a cell. cec2011 merges across its native-dim summaries."""
    if not summary_dir.exists():
        return None
    if suite == "cec2011":
        merged: dict[int, float] = {}
        for p in sorted(summary_dir.glob("dt-gsk_cec2011_D*.csv")):
            for fid, stats in load_summary(p).items():
                if "Mean" in stats:
                    merged[fid] = float(stats["Mean"])
        return merged or None
    path = summary_dir / f"dt-gsk_{suite}_D{dim}.csv"
    if not path.exists():
        return None
    return {fid: float(s["Mean"]) for fid, s in load_summary(path).items() if "Mean" in s}


def _discover_cells(ablation_root: Path, suite: str, dim: int) -> dict[str, dict[int, float]]:
    """Return {cell_name: {func_id: mean}} for every cell with the required summary."""
    found: dict[str, dict[int, float]] = {}
    if not ablation_root.exists():
        return found
    for child in sorted(p for p in ablation_root.iterdir() if p.is_dir()):
        means = _load_cell_means(_cell_summary_dir(ablation_root, child.name, suite), suite, dim)
        if means:
            found[child.name] = means
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate DT-GSK ablation cells into a rank matrix.")
    parser.add_argument("--ablation-root",
                        default="benchmarks/cec_reference_results/_ablation/scaffold",
                        help="Root holding per-cell output (default: the promoted immutable "
                             "benchmarks/cec_reference_results/_ablation/scaffold; overlay cells "
                             "live under .../_ablation/overlay).")
    parser.add_argument("--suite", default="cec2017", choices=["cec2017", "cec2011", "cec2013"],
                        help="Benchmark suite (default: cec2017). cec2011 merges native dims.")
    parser.add_argument("--dimension", type=int, default=30,
                        help="Ablation dimension (default: 30; ignored for cec2011).")
    parser.add_argument("--full-cell", default="baseline",
                        help="Name of the full-scaffold reference cell (default: baseline).")
    parser.add_argument("--out", default=None,
                        help="Output CSV path (default: "
                             "results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv).")
    args = parser.parse_args(argv)

    suite = args.suite
    tag = suite if suite == "cec2011" else f"{suite}_D{args.dimension}"
    default_out = f"results/ablation/ablation_matrix_rank_summary_{tag}.csv"
    out_arg = args.out or default_out

    ablation_root = (_REPO / args.ablation_root) if not Path(args.ablation_root).is_absolute() else Path(args.ablation_root)
    means = _discover_cells(ablation_root, suite, args.dimension)
    where = suite if suite == "cec2011" else f"{suite} D{args.dimension}"
    if len(means) < 2:
        print(f"Found {len(means)} ablation cell(s) with a {where} summary under "
              f"{ablation_root}. Need >= 2 to rank. Run scripts/run_ablation.py first. Nothing written.")
        return 0
    if args.full_cell not in means:
        print(f"Full-scaffold cell '{args.full_cell}' not found among {sorted(means)}. "
              "Pass --full-cell with a present cell name. Nothing written.")
        return 0

    cells = means  # {cell: {func: mean}}
    common = sorted(set.intersection(*(set(m) for m in means.values())))
    if not common:
        print("No common function ids across cells; nothing written.")
        return 0

    ordered = list(cells)  # stable order
    friedman_data = {cell: [means[cell][f] for f in common] for cell in ordered}
    fried = friedman_rank(friedman_data)
    ranks = fried.avg_ranks

    # best-case counts: lowest Mean per function.
    best_count = {cell: 0 for cell in ordered}
    for i, _f in enumerate(common):
        vals = [(friedman_data[cell][i], cell) for cell in ordered]
        best_count[min(vals, key=lambda t: t[0])[1]] += 1

    # full-vs-cell paired Wilcoxon (Holm-corrected across disabled cells).
    full_vec = np.asarray(friedman_data[args.full_cell], dtype=float)
    raw_p: dict[str, float] = {}
    for cell in ordered:
        if cell == args.full_cell:
            continue
        cell_vec = np.asarray(friedman_data[cell], dtype=float)
        try:
            raw_p[cell] = float(wilcoxon_paired(full_vec, cell_vec).p_value)
        except Exception:  # pragma: no cover - degenerate (all-equal) pairs
            raw_p[cell] = float("nan")
    labels = [c for c in ordered if c != args.full_cell]
    finite = [(c, raw_p[c]) for c in labels if np.isfinite(raw_p[c])]
    holm_adj: dict[str, float] = {}
    holm_sig: dict[str, bool] = {}
    if finite:
        holm = holm_correction([p for _, p in finite], [c for c, _ in finite])
        for comp in holm.comparisons:
            holm_adj[str(comp["label"])] = float(comp["p_adjusted"])
            holm_sig[str(comp["label"])] = bool(comp["significant"])

    full_rank = ranks[args.full_cell]
    out_path = (_REPO / out_arg) if not Path(out_arg).is_absolute() else Path(out_arg)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cell", "mean_rank", "delta_rank_vs_full", "best_count",
                    "n_funcs", "wilcoxon_p", "holm_p", "significant"])
        for cell in sorted(ordered, key=lambda c: ranks[c]):  # best (lowest) rank first
            is_full = cell == args.full_cell
            w.writerow([
                cell,
                f"{ranks[cell]:.4f}",
                "0.0000" if is_full else f"{ranks[cell] - full_rank:+.4f}",
                best_count[cell],
                len(common),
                "" if is_full else (f"{raw_p[cell]:.4g}" if np.isfinite(raw_p.get(cell, float('nan'))) else "nan"),
                "" if is_full else (f"{holm_adj[cell]:.4g}" if cell in holm_adj else "nan"),
                "" if is_full else ("yes" if holm_sig.get(cell) else "no"),
            ])

    print(f"Wrote {out_path}")
    print(f"  cells={len(ordered)}  funcs={len(common)}  full='{args.full_cell}' "
          f"(rank {full_rank:.3f})  Friedman p={fried.p_value:.3g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
