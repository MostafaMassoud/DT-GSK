"""Parity trace harness: dump deterministic checkpoints for one optimizer cell.

This records, for a single (optimizer, suite, function, dimension, run), the
checkpoints needed to localize any divergence from the external reference
implementation: the raw random stream, the initial population, the per-
generation best-so-far trajectory, and the final result.

Run the matching trace on the reference side with the same seed and compare the
two JSON files. The first checkpoint that differs is the source of divergence.
With the ``threefry`` generator both stacks now share the same counter-based
Threefry-4x64-20 stream and the same column-major matrix fill, so the random
stream and initial population match bit-for-bit; any residual divergence is the
irreducible floating-point difference in the benchmark evaluation itself.

Usage:
    python scripts/parity_trace.py --optimizer gsk --suite cec2017 \
        --function 5 --dimension 10 --run 1 --output results/_parity/py_gsk.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
from typing import Any

import numpy as np

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.common.rng import RandomContext, effective_python_generator
from gsk_family.optimizers.agsk import optimize as optimize_agsk
from gsk_family.optimizers.apgsk import optimize as optimize_apgsk
from gsk_family.optimizers.atmals_gsk import optimize as optimize_atmals_gsk
from gsk_family.optimizers.fdb_agsk import optimize as optimize_fdb_agsk
from gsk_family.optimizers.gsk import optimize as optimize_gsk
from gsk_family.runners.seed_policy import effective_rand_generator, seed_for_run
from gsk_family.types import OptimizerOptions


OPTIMIZERS = {
    "gsk": optimize_gsk,
    "agsk": optimize_agsk,
    "apgsk": optimize_apgsk,
    "fdb-agsk": optimize_fdb_agsk,
    "atmals-gsk": optimize_atmals_gsk,
}

_DEFAULT_NP = 100


def _sha16(array: Any) -> str:
    """Return a short stable digest of a float64 array's exact bytes."""
    data = np.ascontiguousarray(np.asarray(array, dtype=np.float64)).tobytes()
    return hashlib.sha256(data).hexdigest()[:16]


def trace_cell(
    optimizer: str,
    suite: str,
    function: int,
    dimension: int,
    run: int,
    base_seed: int,
    seed_policy: str,
    rand_generator: str,
    benchmark_fp_mode: str,
) -> dict[str, Any]:
    """Trace deterministic checkpoints for one optimizer/suite/function/dim/run."""
    seed = seed_for_run(seed_policy, optimizer, suite, base_seed, dimension, function, run)
    generator = effective_rand_generator(seed_policy, optimizer, rand_generator)
    problem = make_problem(
        suite,
        function,
        dimension,
        0,
        benchmark_fp_mode=benchmark_fp_mode,
    )

    # Checkpoint A: raw random stream (first draws straight off the seeded generator).
    first_draws = np.asarray(RandomContext(seed, generator).random(12)).tolist()

    # Checkpoint B: initial population (the runner's fair-start draw).
    pop_rng = RandomContext(seed, generator)
    unit = np.asarray(pop_rng.random((_DEFAULT_NP, dimension)), dtype=np.float64)
    pop0 = problem.lb + unit * (problem.ub - problem.lb)

    # Checkpoint C: full run -> final result + per-generation best-so-far trajectory.
    options = OptimizerOptions(seed=seed, rand_generator=generator)
    result = OPTIMIZERS[optimizer](problem, options)
    convergence_best = result.convergence.best_fitness.tolist()

    return {
        "config": {
            "optimizer": optimizer,
            "suite": suite,
            "function": int(function),
            "dimension": int(dimension),
            "run": int(run),
            "base_seed": int(base_seed),
            "seed_policy": seed_policy,
            "requested_rand_generator": rand_generator,
            "effective_generator_label": generator,
            "effective_bit_generator": effective_python_generator(generator),
            "benchmark_fp_mode": benchmark_fp_mode,
            "derived_seed": int(seed),
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
        },
        "checkpoint_a_rng_first12": first_draws,
        "checkpoint_b_initial_population": {
            "shape": [int(_DEFAULT_NP), int(dimension)],
            "fill_order": "threefry fills column-major (Fortran), matching reference rand(np,dim)",
            "sha16": _sha16(pop0),
            "row0": pop0[0].tolist(),
            "col0": pop0[:, 0].tolist(),
        },
        "checkpoint_c_final": {
            "best_fitness": float(result.best_fitness),
            "error": float(result.error),
            "nfes": int(result.nfes),
            "generations": len(convergence_best),
            "best_so_far_trajectory": convergence_best,
        },
    }


def _build_parser() -> argparse.ArgumentParser:
    """Build the parity-trace argument parser."""
    parser = argparse.ArgumentParser(description="Trace deterministic optimizer checkpoints.")
    parser.add_argument("--optimizer", default="gsk", choices=sorted(OPTIMIZERS))
    parser.add_argument("--suite", default="cec2017")
    parser.add_argument("--function", type=int, default=5)
    parser.add_argument("--dimension", type=int, default=10)
    parser.add_argument("--run", type=int, default=1)
    parser.add_argument("--base-seed", type=int, default=20240620)
    parser.add_argument("--seed-policy", default="unified")
    parser.add_argument("--rand-generator", default="threefry")
    parser.add_argument(
        "--benchmark-fp-mode",
        choices=("default", "strict"),
        default="default",
        help="Benchmark floating-point mode for the traced cell.",
    )
    parser.add_argument("--output", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Trace one cell and print or write the checkpoint JSON."""
    args = _build_parser().parse_args(argv)
    payload = trace_cell(
        args.optimizer,
        args.suite,
        args.function,
        args.dimension,
        args.run,
        args.base_seed,
        args.seed_policy,
        args.rand_generator,
        args.benchmark_fp_mode,
    )
    text = json.dumps(payload, indent=2)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"parity trace written to {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
