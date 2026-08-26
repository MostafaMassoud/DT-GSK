#!/usr/bin/env python3
"""E1 (reviewer point R2.3): the coordinate-basis arm of the refinement contrast.

Reviewer 2 asks for "no refinement, coordinate-based refinement, and
eigenframe-based refinement under the same evaluation budget". Two of those
three arms already exist in the frozen ablation release at 51 paired runs,
D in {50, 100}:

    no refinement   configs/_ablation/_51run/overlay_no_finalpolish_cec2017_51.yml
    eigenframe      configs/_ablation/_51run/overlay_full_cec2017_51.yml

Only the middle arm is missing, and this script is it: the SHIPPED
configuration in every respect -- ISM live, linkage live, identical seeds and
budget -- with the final polish forced to search along the coordinate axes.

Why this is not a YAML config
-----------------------------
The core exposes the basis override as the keyword-only research hook
``research_oracle_basis``. ``dt_gsk.py`` deliberately does not forward it, and
``tests/regression/test_dormant_mechanisms_unreachable.py`` asserts the hook is
unreachable from every config, profile, CLI and adapter path -- including a
check on the adapter's own source text. ``dt_gsk.py`` is additionally hash-
pinned by ``papers/scripts/validate_provenance_claims.py``. Expressing E1 as a
config would therefore require breaking a regression test and a hash gate.

That tripwire scans ``src/gsk_family`` only, and its docstring states that
making the hooks reachable "requires a new evidence release" -- which is exactly
what E1 produces. So the override lives here, outside the shipped surface.
Nothing under ``src/`` is modified, and the shipped seed schedule, problem
factory and output writers are reused unchanged so these cells pair
cell-for-cell with the frozen bank.

Passing the identity matrix reproduces the axes fallback the polish already
uses when no graph signal exists, so the contrast against the released
eigenframe arm isolates the basis and nothing else.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import numpy as np  # noqa: E402

from gsk_family.benchmark_adapter.factory import make_problem  # noqa: E402
from gsk_family.optimizers._dt_core import dt_gsk_optimize  # noqa: E402
from gsk_family.optimizers._dt_profiles import build_pub_config  # noqa: E402
from gsk_family.runners.seed_policy import get_cec_seed  # noqa: E402
# Reuse the shipped adapter's own bounds resolver rather than reimplementing it,
# so the search box is identical to a normal run (scalar for uniform CEC2017
# bounds, per-dimension arrays where a suite needs them).
from gsk_family.optimizers.dt_gsk import _resolve_bounds  # noqa: E402

SUITE = "cec2017"
BASE_SEED = 20240620
# CEC2017 scored set: F1 and F3..F30 (F2 withdrawn as numerically unstable).
FUNCTIONS = [1] + list(range(3, 31))


def one_cell(func: int, dim: int, run: int, max_evals: int = 0) -> dict:
    """Run a single (function, dimension, run) cell and return its record.

    ``max_evals`` of 0 means the suite's own protocol budget, which is what the
    campaign uses. A positive value is for smoke runs only -- it produces cells
    that are NOT comparable to the frozen bank, and the caller is responsible
    for keeping them out of the campaign output tree.
    """
    seed = get_cec_seed(BASE_SEED, dim, func, run)
    problem = make_problem(SUITE, func, dim)
    budget = int(max_evals) if max_evals else int(problem.max_nfes)
    config = build_pub_config(
        dim, seed=seed, max_nfes=budget,
        bounds=_resolve_bounds(problem), rand_generator="threefry",
    )

    evals = {"n": 0}

    def objective(population: np.ndarray) -> np.ndarray:
        evals["n"] += int(np.asarray(population).shape[0])
        return np.asarray(problem.evaluate(population), dtype=np.float64)

    t0 = time.perf_counter()
    result = dt_gsk_optimize(
        objective=objective,
        config=config,
        # THE one difference from the shipped run: the polish searches the
        # coordinate axes instead of the learned eigenbasis.
        research_oracle_basis=np.eye(dim, dtype=np.float64),
    )
    runtime = time.perf_counter() - t0

    best = float(result.best_fitness if hasattr(result, "best_fitness") else result.best_f)
    optimum = float(getattr(problem, "optimum", 0.0) or 0.0)
    return {
        "function": func, "dimension": dim, "run": run, "seed": seed,
        "best_fitness": best, "error": max(best - optimum, 0.0),
        "evaluations": evals["n"], "runtime_seconds": round(runtime, 6),
    }


def _cell_star(args):
    return one_cell(*args)


def main() -> int:
    ap = argparse.ArgumentParser(description="E1 coordinate-basis refinement arm.")
    ap.add_argument("--workers", type=int, default=15)
    ap.add_argument("--output-root", required=True)
    ap.add_argument("--dims", default="50,100")
    ap.add_argument("--runs", type=int, default=51)
    ap.add_argument("--functions", default="",
                    help="comma-separated ids; default is the 29 scored functions")
    ap.add_argument("--max-evals", type=int, default=0,
                    help="0 = suite protocol budget. Non-zero is for SMOKE runs only; "
                         "the resulting cells do not pair with the frozen bank.")
    args = ap.parse_args()

    dims = [int(d) for d in args.dims.split(",") if d.strip()]
    funcs = ([int(f) for f in args.functions.split(",") if f.strip()]
             if args.functions else FUNCTIONS)
    out_root = Path(args.output_root)
    if not out_root.is_absolute():
        out_root = REPO / out_root
    summary_dir = out_root / "dt-gsk" / SUITE / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    per_run = summary_dir / "per_run.csv"

    # resume: skip any (func, dim, run) already recorded.
    # "Has content", not merely "exists": an interruption before the first flush
    # leaves an empty file behind, and treating that as an existing CSV would skip
    # writeheader() below and produce a headerless file whose first data row then
    # reads as the header on the next resume.
    has_rows = per_run.is_file() and per_run.stat().st_size > 0
    done: set[tuple[int, int, int]] = set()
    if has_rows:
        import csv
        with per_run.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                done.add((int(row["function"]), int(row["dimension"]), int(row["run"])))

    todo = [(f, d, r, args.max_evals) for d in dims for f in funcs
            for r in range(1, args.runs + 1) if (f, d, r) not in done]
    print(f"[e1] {len(done):,} cells present, {len(todo):,} to run, {args.workers} workers",
          flush=True)
    if not todo:
        print("[e1] nothing to do")
        return 0

    import csv
    header = ["function", "dimension", "run", "seed", "best_fitness",
              "error", "evaluations", "runtime_seconds"]
    new_file = not has_rows          # write the header unless real rows exist
    completed = 0
    t0 = time.time()
    with per_run.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=header)
        if new_file:
            writer.writeheader()
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(_cell_star, c): c for c in todo}
            for fut in as_completed(futures):
                cell = futures[fut]
                try:
                    writer.writerow(fut.result())
                except Exception as exc:              # noqa: BLE001
                    print(f"[e1] CELL FAILED {cell}: {exc}", flush=True)
                    continue
                completed += 1
                if completed % 200 == 0:
                    fh.flush()
                    rate = completed / max(time.time() - t0, 1e-9)
                    eta = (len(todo) - completed) / max(rate, 1e-9) / 60
                    print(f"[e1] {completed:,}/{len(todo):,}  ETA {eta:.0f} min", flush=True)

    (summary_dir / "run_config.json").write_text(json.dumps({
        "optimizer": "dt-gsk", "suite": SUITE, "profile": "pub",
        "arm": "coordinate-basis final polish (E1, reviewer point R2.3)",
        "optimizer_options": {},
        "research_override": "research_oracle_basis = I(dim)",
        "note": ("Shipped pub profile in every other respect: ISM live, linkage live, "
                 "unified seed schedule, suite protocol budget. The identity basis "
                 "reproduces the axes fallback the polish already uses when no graph "
                 "signal exists, so the contrast against the released eigenframe arm "
                 "isolates the basis alone."),
        "base_seed": BASE_SEED, "seed_policy": "unified",
        "rand_generator": "threefry", "runs": args.runs, "dimensions": dims,
        "functions": funcs,
        "max_evaluations": args.max_evals or "suite protocol budget",
        "smoke": bool(args.max_evals),
    }, indent=2) + "\n", encoding="utf-8")

    mins = (time.time() - t0) / 60
    print(f"[e1] wrote {completed:,} cells in {mins:.1f} min -> {per_run}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
