"""Baseline Gaining-Sharing Knowledge optimizer."""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from gsk_family.benchmark_adapter.problem import BenchmarkProblem
from gsk_family.common.donors import (
    gained_shared_junior_r1r2r3,
    gained_shared_senior_r1r2r3,
)
from gsk_family.common.numeric_compat import compat_fix_int, stable_argsort
from gsk_family.common.population import (
    gsk_initial_population_from_options,
    gsk_restore_rng_after_initialization,
)
from gsk_family.common.rng import RandomContext
from gsk_family.optimizers._kernels import gsk_build_trial
from gsk_family.stats import compute_error
from gsk_family.types import ConvergenceTrace, OptimizerOptions, OptimizerResult


_MISSING = object()


def _option_value(options: Any, name: str, default: Any = _MISSING) -> Any:
    """Read an optimizer option from object, dict, or nested values mapping."""
    if options is None:
        if default is _MISSING:
            raise ValueError(f"options.{name} is required.")
        return default

    value = _MISSING
    if isinstance(options, dict):
        value = options.get(name, _MISSING)
        values = options.get("values", {})
    else:
        value = getattr(options, name, _MISSING)
        values = getattr(options, "values", {})

    if (value is _MISSING or value is None) and isinstance(values, dict):
        value = values.get(name, _MISSING)

    if value is _MISSING or value is None:
        if default is _MISSING:
            raise ValueError(f"options.{name} is required.")
        return default
    return value


def _scan_best(
    candidates: np.ndarray,
    fitness: np.ndarray,
    n_count: int,
    current_best: float,
    current_x: np.ndarray,
) -> tuple[float, np.ndarray]:
    """Update the best candidate from the first `n_count` evaluated rows."""
    if n_count <= 0:
        return current_best, current_x
    local_fitness = fitness[:n_count]
    idx = int(np.argmin(local_fitness))
    value = float(local_fitness[idx])
    if value < current_best:
        return value, candidates[idx, :].copy()
    return current_best, current_x


def _append_convergence(
    nfes_values: list[int],
    best_values: list[float],
    nfes: int,
    best_fitness: float,
) -> None:
    """Append one best-so-far convergence point."""
    nfes_values.append(int(nfes))
    best_values.append(float(best_fitness))


def optimize(problem: BenchmarkProblem, options: OptimizerOptions | dict[str, Any]) -> OptimizerResult:
    """Run the baseline GSK optimizer.

    This ports ``gsk_optimize.m`` while keeping the reference defaults,
    generation schedule, full-generation budget crossing, strict greedy
    selection, and end-of-run target-error zeroing.
    """
    seed = int(_option_value(options, "seed"))
    rand_generator = str(_option_value(options, "rand_generator", "twister"))
    np_size = int(_option_value(options, "np", 100))
    kf = float(_option_value(options, "kf", 0.5))
    kr = float(_option_value(options, "kr", 0.9))
    k_rate = float(_option_value(options, "k", 10.0))
    p_part = float(_option_value(options, "p", 0.1))

    if np_size <= 0:
        raise ValueError(f"np must be positive, got {np_size}.")
    if problem.max_nfes <= 0:
        raise ValueError(f"problem.max_nfes must be positive, got {problem.max_nfes}.")
    if problem.dim <= 0:
        raise ValueError(f"problem.dim must be positive, got {problem.dim}.")

    start = time.perf_counter()
    rng = RandomContext(seed, rand_generator)

    max_nfes = int(problem.max_nfes)
    dim = int(problem.dim)
    g_max = compat_fix_int(max_nfes / np_size)

    popold = gsk_initial_population_from_options(
        options,
        rng,
        np_size,
        problem.lb,
        problem.ub,
        dim=dim,
    )
    gsk_restore_rng_after_initialization(options, rng)
    pop = popold.copy()
    del popold        # W1.3: single population buffer from here on

    fitness = np.asarray(problem.evaluate(pop), dtype=np.float64).reshape(-1)
    if fitness.shape != (np_size,):
        raise ValueError(
            f"problem.evaluate returned shape {fitness.shape}; expected ({np_size},)."
        )
    if not np.all(np.isfinite(fitness)):
        raise ValueError("Initial population fitness contains non-finite values.")

    nfes = 0
    best_fitness = float("1e300")
    best_x = np.zeros(dim, dtype=np.float64)

    n_init = min(np_size, max_nfes - nfes)
    best_fitness, best_x = _scan_best(pop, fitness, n_init, best_fitness, best_x)
    nfes += n_init

    k_vec = np.full(np_size, k_rate, dtype=np.float64)
    conv_nfes: list[int] = []
    conv_best: list[float] = []
    _append_convergence(conv_nfes, conv_best, nfes, best_fitness)

    generation = 0
    _rand_buf = np.empty((3, np_size, dim), dtype=np.float64)  # W1.2 reuse
    while nfes < max_nfes:
        generation += 1
        schedule_base = 1.0 - (generation / g_max)
        d_junior = np.ceil(dim * np.power(schedule_base, k_vec)).astype(np.int64)

        # W1.3 (2026-07-25): the former `pop = popold.copy()` here and the
        # `popold = pop.copy()` at selection were byte-identical dead copies
        # (no writer between them; kernel and _scan_best read-only; `trial`
        # freshly allocated). Single buffer, in-place masked scatter below.
        # Microbenched: 2 full NP*D copies ~506 us/gen at D=1000.
        ind_best = stable_argsort(fitness)
        rg1, rg2, rg3 = gained_shared_junior_r1r2r3(ind_best, rng, validate=False)
        r1, r2, r3 = gained_shared_senior_r1r2r3(ind_best, p_part, rng, validate=False)

        # Same RNG draw order as the reference (split, then KR junior, KR senior);
        # one (3, NP, D) draw fills the same stream as three (NP, D) draws, and the
        # deterministic gained/repair/mask arithmetic runs in the kernel.
        junior_probability = d_junior / dim
        rand_block = np.asarray(rng.random((3, np_size, dim)), dtype=np.float64)
        # W1.2 (2026-07-25): rng.random((3,N,D)) returns F-order plane VIEWS;
        # gsk_build_trial's ascontiguousarray then strided-copied each plane
        # into a FRESH allocation every generation. Copy once here into a
        # persistent C-buffer instead: same doubles at the same (i,j)
        # positions (layout-only change, the draw itself is untouched), and
        # the kernel-side ascontiguousarray becomes a free pass-through.
        # Microbenched: saves ~331 us/gen at D=1000, neutral at D<=100.
        np.copyto(_rand_buf[0, :np_size], rand_block[0])
        np.copyto(_rand_buf[1, :np_size], rand_block[1])
        np.copyto(_rand_buf[2, :np_size], rand_block[2])
        rand_split = _rand_buf[0, :np_size]
        rand_kr_junior = _rand_buf[1, :np_size]
        rand_kr_senior = _rand_buf[2, :np_size]
        trial = gsk_build_trial(
            pop,
            fitness,
            rg1,
            rg2,
            rg3,
            r1,
            r2,
            r3,
            kf_junior=kf,
            kf_senior=kf,
            junior_prob=junior_probability,
            rand_split=rand_split,
            rand_kr_junior=rand_kr_junior,
            rand_kr_senior=rand_kr_senior,
            kr=kr,
            lb=problem.lb,
            ub=problem.ub,
        )

        children_fitness = np.asarray(problem.evaluate(trial), dtype=np.float64).reshape(-1)
        if children_fitness.shape != (np_size,):
            raise ValueError(
                f"problem.evaluate returned shape {children_fitness.shape}; expected ({np_size},)."
            )
        if not np.all(np.isfinite(children_fitness)):
            raise ValueError("Child population fitness contains non-finite values.")

        n_count = min(np_size, max_nfes - nfes)
        best_fitness, best_x = _scan_best(
            trial,
            children_fitness,
            n_count,
            best_fitness,
            best_x,
        )
        nfes += n_count

        child_is_better = children_fitness < fitness
        fitness = np.where(child_is_better, children_fitness, fitness)
        pop[child_is_better, :] = trial[child_is_better, :]

        _append_convergence(conv_nfes, conv_best, nfes, best_fitness)

    error = compute_error(best_fitness, float(problem.optimum), float(problem.target_error))

    return OptimizerResult(
        optimizer="gsk",
        suite=problem.suite,
        func_id=int(problem.func_id),
        dim=dim,
        seed=seed,
        best_x=best_x,
        best_fitness=float(best_fitness),
        error=float(error),
        nfes=int(nfes),
        termination="max_evaluations",
        convergence=ConvergenceTrace(
            nfes=np.asarray(conv_nfes, dtype=np.int64),
            best_fitness=np.asarray(conv_best, dtype=np.float64),
        ),
        runtime_seconds=float(time.perf_counter() - start),
        params={
            "np": np_size,
            "kf": kf,
            "kr": kr,
            "k": k_rate,
            "p": p_part,
        },
        notes="",
    )
