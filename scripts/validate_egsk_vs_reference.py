"""Reproducibility check: re-run the Python EGSK port against its own promoted evidence.

The committed EGSK cell (``benchmarks/cec_reference_results/cec2017/egsk/``) is
this project's **scipy-SLSQP port**, generated under the unified Threefry seed
schedule (``get_cec_seed(20240620, dim, func, run)``) and promoted into the
reference tree -- it is NOT an imported MATLAB ``fmincon`` table. Its per-run
checkpoint logs
(``gen_logs/CheckpointErrors_egsk_F<f>_D<d>.csv``, a ``Run, Seed, E...`` schema)
record the same final errors as the cell's ``per_run.csv`` (verified: identical
run count and mean).

Because the port is deterministic, re-running it at each recorded seed must
reproduce the committed final error byte-faithfully. This script performs that
paired reproduction check per cell: it reports Python vs committed mean/median,
the maximum absolute paired difference, the exact-match count (|delta| <= 1e-12),
and a two-sided paired Wilcoxon signed-rank p-value as a secondary drift signal.
A near-zero ``max_abs_diff`` confirms the promoted EGSK evidence is regenerable
from the current port. Byte-exact reproduction is ``|delta| <= 1e-12``; the SLSQP
interior-point polish carries ~1e-12 floating-point noise, so the summary treats
``max_abs_diff <= 1e-9`` as a faithful reproduction and reserves a **drift** flag
for larger, systematic differences -- port or environment drift (a ``scipy`` /
``numba`` / platform change), NOT a MATLAB-vs-Python effect (which would be orders
of magnitude larger; the archived fmincon gap was ~0.18 on F5/D10).

Provenance: the original one-time comparison of this SLSQP port against the
MATLAB ``fmincon`` reference -- which is not committed in this repo -- is archived
in ``docs/research/egsk_validation_appendix.md`` (Section 5) and is not
reproducible from the committed tree.

Example (bounded representative check):
    python scripts/validate_egsk_vs_reference.py --dims 10,30,50 \
        --funcs 1,3,5,7,9,11,15,21,27,30 --runs 15 --out egsk_reproduction.json

Full sweep (all CEC2017 dims, all scored functions, all committed runs):
    python scripts/validate_egsk_vs_reference.py --dims 10,30,50,100 \
        --funcs 1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 \
        --runs 51 --out egsk_reproduction_cec2017_full.json
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.optimizers.egsk import optimize as optimize_egsk
from gsk_family.types import OptimizerOptions

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _checkpoint_path(suite: str, func: int, dim: int) -> Path:
    """Return the reference per-run checkpoint CSV for one (func, dim) cell."""
    return (
        PROJECT_ROOT
        / "benchmarks"
        / "cec_reference_results"
        / suite
        / "egsk"
        / "gen_logs"
        / f"CheckpointErrors_egsk_F{func}_D{dim}.csv"
    )


def read_reference_cell(suite: str, func: int, dim: int, max_runs: int):
    """Return ``[(run, seed, final_error), ...]`` from the committed EGSK checkpoint CSV.

    The committed cell is the promoted scipy-SLSQP port (not a MATLAB import); the
    final E-column (highest eval budget) is taken as its per-run final error.
    """
    path = _checkpoint_path(suite, func, dim)
    rows: list[tuple[int, int, float]] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        final_col = len(header) - 1
        for record in reader:
            if not record:
                continue
            rows.append((int(record[0]), int(record[1]), float(record[final_col])))
            if len(rows) >= max_runs:
                break
    return rows


def run_python_egsk(suite: str, func: int, dim: int, seed: int) -> float:
    """Run the Python EGSK on one cell at a fixed seed and return its error."""
    budget = 10000 * dim
    problem = make_problem(suite, func, dim=dim, max_nfes_override=budget)
    result = optimize_egsk(problem, OptimizerOptions(seed=seed, rand_generator="threefry"))
    return float(result.error)


def validate_cell(suite: str, func: int, dim: int, max_runs: int) -> dict:
    """Run the paired comparison for one (func, dim) cell and return its summary."""
    reference = read_reference_cell(suite, func, dim, max_runs)
    py = np.array([run_python_egsk(suite, func, dim, seed) for _, seed, _ in reference])
    ref = np.array([final for _, _, final in reference])
    diff = py - ref
    n_exact = int(np.sum(np.isclose(py, ref, atol=1e-12, rtol=0.0)))
    if np.allclose(diff, 0.0):
        p_value = 1.0
    else:
        try:
            p_value = float(wilcoxon(py, ref, zero_method="wilcox").pvalue)
        except ValueError:
            p_value = float("nan")
    return {
        "func": func,
        "dim": dim,
        "n": len(reference),
        "py_mean": float(py.mean()),
        "ref_mean": float(ref.mean()),
        "py_median": float(np.median(py)),
        "ref_median": float(np.median(ref)),
        "max_abs_diff": float(np.max(np.abs(diff))),
        "n_exact": n_exact,
        "wilcoxon_p": p_value,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: run the paired validation over the requested grid."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", default="cec2017")
    parser.add_argument("--dims", default="10,30,50,100")
    parser.add_argument("--funcs", default="1,3,5,7,9,11,15,21,27,30")
    parser.add_argument("--runs", type=int, default=15)
    parser.add_argument("--out", default="egsk_validation.json")
    args = parser.parse_args(argv)

    dims = [int(token) for token in args.dims.split(",") if token]
    funcs = [int(token) for token in args.funcs.split(",") if token]

    cells: list[dict] = []
    for dim in dims:
        for func in funcs:
            cell = validate_cell(args.suite, func, dim, args.runs)
            cells.append(cell)
            print(
                f"F{cell['func']:>2} D{cell['dim']:<3} n={cell['n']:>2} "
                f"py_mean={cell['py_mean']:.4g} ref_mean={cell['ref_mean']:.4g} "
                f"max_abs_diff={cell['max_abs_diff']:.3g} "
                f"exact={cell['n_exact']}/{cell['n']} W_p={cell['wilcoxon_p']:.3f}"
            )

    Path(args.out).write_text(json.dumps(cells, indent=2), encoding="utf-8")
    n_cells = len(cells)
    # Byte-exact (<= 1e-12) is the ideal; the SLSQP interior-point polish carries
    # ~1e-12 floating-point noise, so a handful of runs may land just above that
    # while still being a faithful reproduction. REPRO_TOL separates that benign
    # noise from genuine drift (a real port/environment change is orders of
    # magnitude larger -- e.g. the archived fmincon gap was ~0.18 on F5/D10).
    REPRO_TOL = 1e-9
    n_exact = sum(1 for cell in cells if cell["n"] and cell["n_exact"] == cell["n"])
    n_repro = sum(1 for cell in cells if cell["max_abs_diff"] <= REPRO_TOL)
    worst = max((cell["max_abs_diff"] for cell in cells), default=0.0)
    print(
        f"\nWrote {args.out}: {n_repro}/{n_cells} cells reproduced within SLSQP FP "
        f"tolerance (max |delta| <= {REPRO_TOL:g}), of which {n_exact} byte-exact "
        f"(<= 1e-12); worst max_abs_diff = {worst:.3g}"
    )
    if n_repro < n_cells:
        print(
            "  DRIFT: cells above the reproduction tolerance indicate port/environment "
            "drift from the committed EGSK evidence (scipy/numba/platform), not a "
            "fmincon effect -- investigate before trusting the committed cell."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
