"""Adaptive Gaining-Sharing Knowledge optimizer."""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from gsk_family.benchmark_adapter.problem import BenchmarkProblem
from gsk_family.common.donors import (
    gained_shared_junior_r1r2r3,
    gained_shared_senior_r1r2r3,
)
from gsk_family.common.numeric_compat import compat_round_int, stable_argsort
from gsk_family.common.population import (
    gsk_initial_population_from_options,
    gsk_restore_rng_after_initialization,
)
from gsk_family.common.reduction import gsk_reduction_survivors
from gsk_family.common.rng import RandomContext
from gsk_family.optimizers._kernels import gsk_build_trial
from gsk_family.types import ConvergenceTrace, OptimizerOptions, OptimizerResult


KF_POOL = np.array([0.1, 1.0, 0.5, 1.0], dtype=np.float64)
KR_POOL = np.array([0.2, 0.1, 0.9, 0.9], dtype=np.float64)
INITIAL_KW = np.array([0.85, 0.05, 0.05, 0.05], dtype=np.float64)
SENIOR_P = 0.05
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


def _draw_initial_k(pop_size: int, rng: RandomContext) -> np.ndarray:
    """Draw AGSK's mixed continuous/integer initial K vector."""
    kind = np.asarray(rng.random(pop_size), dtype=np.float64)
    k_vec = np.zeros(pop_size, dtype=np.float64)
    uniform_mask = kind < 0.5
    integer_mask = ~uniform_mask
    if np.any(uniform_mask):
        k_vec[uniform_mask] = np.asarray(rng.random(int(np.count_nonzero(uniform_mask))))
    if np.any(integer_mask):
        k_vec[integer_mask] = np.ceil(
            20.0 * np.asarray(rng.random(int(np.count_nonzero(integer_mask))))
        )
    return k_vec


def _select_parameter_slots(
    rng: RandomContext,
    pop_size: int,
    kw_ind: np.ndarray,
) -> np.ndarray:
    """Return 0-based AGSK parameter-pool slots from one rand(NP, 1) draw."""
    draw = np.asarray(rng.random(pop_size), dtype=np.float64)
    cumulative = np.cumsum(np.asarray(kw_ind, dtype=np.float64))
    return np.minimum(np.searchsorted(cumulative, draw, side="left"), 3).astype(
        np.int64,
        copy=False,
    )


def _improvement_credit(
    fitness: np.ndarray,
    children_fitness: np.ndarray,
    slots: np.ndarray,
) -> np.ndarray:
    """Compute AGSK ``All_Imp`` credit with the reference floor rule."""
    parent = np.asarray(fitness, dtype=np.float64).reshape(-1)
    child = np.asarray(children_fitness, dtype=np.float64).reshape(-1)
    slot_idx = np.asarray(slots, dtype=np.int64).reshape(-1)
    if parent.shape != child.shape or parent.shape != slot_idx.shape:
        raise ValueError("fitness, children_fitness, and slots must have matching shapes.")

    diff = np.abs(parent - child)
    child_is_better = parent > child
    all_imp = np.zeros(4, dtype=np.float64)
    for slot in range(4):
        mask = child_is_better & (slot_idx == slot)
        if np.any(mask):
            all_imp[slot] = float(np.sum(diff[mask]))

    total = float(np.sum(all_imp))
    if total == 0.0:
        return np.full(4, 0.25, dtype=np.float64)

    all_imp = all_imp / total
    imp_order = stable_argsort(all_imp)
    for idx in imp_order[:-1]:
        all_imp[idx] = max(float(all_imp[idx]), 0.05)
    all_imp[imp_order[-1]] = 1.0 - float(np.sum(all_imp[imp_order[:-1]]))
    return all_imp


def _target_population_size(
    nfes: int,
    max_nfes: int,
    max_pop_size: int,
    min_pop_size: int,
) -> int:
    """Compute AGSK's target population size for the current budget ratio."""
    ratio = float(nfes) / float(max_nfes)
    plan = (float(min_pop_size) - float(max_pop_size)) * (ratio ** (1.0 - ratio))
    return int(compat_round_int(plan + float(max_pop_size)))


def _reduce_population_after_generation(
    pop: np.ndarray,
    fitness: np.ndarray,
    k_vec: np.ndarray,
    *,
    pop_size: int,
    max_pop_size: int,
    min_pop_size: int,
    nfes: int,
    max_nfes: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int, np.ndarray | None]:
    """Apply AGSK population reduction after one generation.

    W1.3/W1.4 (2026-07-25): the callers now keep a SINGLE population buffer
    (the former pop/popold pair held byte-identical contents all generation),
    so this helper gathers once where it used to gather twice; the second
    gather and the ``np.arange`` allocated on every non-reducing generation
    were dead at all three call sites. Bit-identical: ``gsk_reduction_survivors``
    sees the same fitness vector, so the same rows survive with the same
    values; only dead work is removed. ``survivors`` is ``None`` when no
    reduction occurred (previously a discarded arange).
    """
    target_pop_size = _target_population_size(nfes, max_nfes, max_pop_size, min_pop_size)
    if pop_size <= target_pop_size:
        return pop, fitness, k_vec, pop_size, None

    reduction_count = pop_size - target_pop_size
    if pop_size - reduction_count < min_pop_size:
        reduction_count = pop_size - min_pop_size
    if reduction_count <= 0:
        return pop, fitness, k_vec, pop_size, None

    survivors = gsk_reduction_survivors(fitness, reduction_count)
    new_size = pop_size - reduction_count
    return (
        pop[survivors, :].copy(),
        fitness[survivors].copy(),
        k_vec[survivors].copy(),
        int(new_size),
        survivors,
    )


def _validate_population_options(np_init: int, min_pop_size: int) -> None:
    """Validate AGSK-family initial and minimum population sizes."""
    if np_init <= 0:
        raise ValueError(f"np_init must be positive, got {np_init}.")
    if min_pop_size < 11:
        raise ValueError(f"min_pop_size must be at least 11 for AGSK, got {min_pop_size}.")
    if np_init < min_pop_size:
        raise ValueError(f"np_init must be >= min_pop_size, got {np_init} < {min_pop_size}.")


def optimize(problem: BenchmarkProblem, options: OptimizerOptions | dict[str, Any]) -> OptimizerResult:
    """Run the Adaptive GSK optimizer."""
    seed = int(_option_value(options, "seed"))
    rand_generator = str(_option_value(options, "rand_generator", "twister"))
    np_default = int(_option_value(options, "np", 100))
    np_init = int(_option_value(options, "np_init", np_default))
    min_pop_size = int(_option_value(options, "min_pop_size", 12))

    _validate_population_options(np_init, min_pop_size)
    if problem.max_nfes <= 0:
        raise ValueError(f"problem.max_nfes must be positive, got {problem.max_nfes}.")
    if problem.dim <= 0:
        raise ValueError(f"problem.dim must be positive, got {problem.dim}.")

    start = time.perf_counter()
    rng = RandomContext(seed, rand_generator)

    dim = int(problem.dim)
    max_nfes = int(problem.max_nfes)
    pop_size = int(np_init)
    max_pop_size = int(pop_size)

    popold = gsk_initial_population_from_options(
        options,
        rng,
        pop_size,
        problem.lb,
        problem.ub,
        dim=dim,
    )
    gsk_restore_rng_after_initialization(options, rng)
    pop = popold.copy()
    del popold        # W1.3: single population buffer from here on

    fitness = np.asarray(problem.evaluate(pop), dtype=np.float64).reshape(-1)
    if fitness.shape != (pop_size,):
        raise ValueError(
            f"problem.evaluate returned shape {fitness.shape}; expected ({pop_size},)."
        )
    if not np.all(np.isfinite(fitness)):
        raise ValueError("Initial population fitness contains non-finite values.")

    nfes = 0
    best_fitness = float("1e300")
    best_x = np.zeros(dim, dtype=np.float64)

    n_init = min(pop_size, max_nfes - nfes)
    best_fitness, best_x = _scan_best(pop, fitness, n_init, best_fitness, best_x)
    nfes += n_init

    k_vec = _draw_initial_k(pop_size, rng)
    kw_ind: np.ndarray | None = None
    all_imp = np.zeros(4, dtype=np.float64)

    conv_nfes: list[int] = []
    conv_best: list[float] = []
    _append_convergence(conv_nfes, conv_best, nfes, best_fitness)

    terminated_on_target = False
    generation = 0

    _rand_buf = np.empty((3, pop_size, dim), dtype=np.float64)  # W1.2 reuse (max NP)
    while nfes < max_nfes:
        generation += 1

        if kw_ind is None or nfes < 0.1 * max_nfes:
            kw_ind = INITIAL_KW.copy()
        else:
            kw_ind = 0.95 * kw_ind + 0.05 * all_imp
            kw_ind = kw_ind / np.sum(kw_ind)

        slots = _select_parameter_slots(rng, pop_size, kw_ind)
        kf = KF_POOL[slots]
        kr = KR_POOL[slots]

        junior_dims = np.ceil(dim * np.power(1.0 - (nfes / max_nfes), k_vec)).astype(
            np.int64
        )

        # W1.3 (2026-07-25): dead pop/popold double-copy removed -- single
        # buffer, in-place masked scatter at selection (see gsk.py).
        ind_best = stable_argsort(fitness)
        rg1, rg2, rg3 = gained_shared_junior_r1r2r3(ind_best, rng, validate=False)
        r1, r2, r3 = gained_shared_senior_r1r2r3(ind_best, SENIOR_P, rng, validate=False)

        junior_probability = junior_dims / dim
        rand_block = np.asarray(rng.random((3, pop_size, dim)), dtype=np.float64)
        # W1.2 (2026-07-25): copy the F-order draw planes ONCE into a
        # persistent C-buffer (prefix-sliced for the NLPSR-shrinking NP) so
        # the kernel-side ascontiguousarray is a free pass-through instead
        # of a fresh strided allocation per plane per generation. Same
        # doubles, same (i,j) positions -- layout-only, draw untouched.
        np.copyto(_rand_buf[0, :pop_size], rand_block[0])
        np.copyto(_rand_buf[1, :pop_size], rand_block[1])
        np.copyto(_rand_buf[2, :pop_size], rand_block[2])
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
            rand_split=_rand_buf[0, :pop_size],
            rand_kr_junior=_rand_buf[1, :pop_size],
            rand_kr_senior=_rand_buf[2, :pop_size],
            kr=kr,
            lb=problem.lb,
            ub=problem.ub,
        )

        children_fitness = np.asarray(problem.evaluate(trial), dtype=np.float64).reshape(-1)
        if children_fitness.shape != (pop_size,):
            raise ValueError(
                f"problem.evaluate returned shape {children_fitness.shape}; expected ({pop_size},)."
            )
        if not np.all(np.isfinite(children_fitness)):
            raise ValueError("Child population fitness contains non-finite values.")

        n_count = min(pop_size, max_nfes - nfes)
        best_fitness, best_x = _scan_best(
            trial,
            children_fitness,
            n_count,
            best_fitness,
            best_x,
        )
        nfes += n_count

        all_imp = _improvement_credit(fitness, children_fitness, slots)

        child_is_better = fitness > children_fitness
        fitness = np.where(child_is_better, children_fitness, fitness)
        pop[child_is_better, :] = trial[child_is_better, :]

        pop, fitness, k_vec, pop_size, _ = _reduce_population_after_generation(
            pop,
            fitness,
            k_vec,
            pop_size=pop_size,
            max_pop_size=max_pop_size,
            min_pop_size=min_pop_size,
            nfes=nfes,
            max_nfes=max_nfes,
        )

        _append_convergence(conv_nfes, conv_best, nfes, best_fitness)

        if not np.isnan(problem.target_error) and not np.isnan(problem.optimum):
            if best_fitness - float(problem.optimum) < float(problem.target_error):
                terminated_on_target = True
                break

    if np.isnan(problem.optimum):
        error = float("nan")
    else:
        error = float(best_fitness - float(problem.optimum))
        if terminated_on_target:
            error = 0.0

    termination = "target_error_reached" if terminated_on_target else "max_evaluations"

    return OptimizerResult(
        optimizer="agsk",
        suite=problem.suite,
        func_id=int(problem.func_id),
        dim=dim,
        seed=seed,
        best_x=best_x,
        best_fitness=float(best_fitness),
        error=float(error),
        nfes=int(nfes),
        termination=termination,
        convergence=ConvergenceTrace(
            nfes=np.asarray(conv_nfes, dtype=np.int64),
            best_fitness=np.asarray(conv_best, dtype=np.float64),
        ),
        runtime_seconds=float(time.perf_counter() - start),
        params={
            "np_init": np_init,
            "min_pop_size": min_pop_size,
            "kf_pool": KF_POOL.tolist(),
            "kr_pool": KR_POOL.tolist(),
            "senior_p": SENIOR_P,
            "final_pop_size": pop_size,
            "generations": generation,
        },
        notes="",
    )
