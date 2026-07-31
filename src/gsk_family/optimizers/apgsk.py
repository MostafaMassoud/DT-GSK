"""Adaptive-Parameters Gaining-Sharing Knowledge optimizer."""

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
from gsk_family.common.rng import RandomContext
from gsk_family.optimizers._kernels import gsk_build_trial
from gsk_family.optimizers.agsk import (
    INITIAL_KW,
    KR_POOL,
    SENIOR_P,
    _append_convergence,
    _draw_initial_k,
    _improvement_credit,
    _option_value,
    _reduce_population_after_generation,
    _scan_best,
    _select_parameter_slots,
    _validate_population_options,
)
from gsk_family.types import ConvergenceTrace, OptimizerOptions, OptimizerResult


KF_POOL = np.array([0.1, 1.0, 0.5, 1.0], dtype=np.float64)
KF_POOL_NEGATIVE = np.array([-0.15, -0.05, -0.05, -0.15], dtype=np.float64)


def _apgsk_kf_values(
    slots: np.ndarray,
    *,
    adaptive_phase: bool,
    adaptive_pool_draw: float | None,
    nfes: int,
    max_nfes: int,
) -> tuple[np.ndarray, bool]:
    """Return APGSK KF values and whether the negative pool was used."""
    slot_idx = np.asarray(slots, dtype=np.int64)
    use_negative = False
    if adaptive_phase:
        if adaptive_pool_draw is None:
            raise ValueError("adaptive_pool_draw is required in the adaptive phase.")
        use_negative = not (float(adaptive_pool_draw) >= 0.3 and nfes > 0.5 * max_nfes)
    pool = KF_POOL_NEGATIVE if use_negative else KF_POOL
    return pool[slot_idx], use_negative


def _stochastic_junior_dimension(dim: int, nfes: int, max_nfes: int, draw: float) -> int:
    """Return APGSK's scalar junior dimensionality schedule."""
    ratio = float(nfes) / float(max_nfes)
    exponent = 0.5 if float(draw) > ratio else 2.0
    value = compat_round_int(float(dim) * ((1.0 - ratio) ** exponent))
    return int(np.ceil(value))


def optimize(problem: BenchmarkProblem, options: OptimizerOptions | dict[str, Any]) -> OptimizerResult:
    """Run the APGSK optimizer."""
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

    # APGSK samples K like AGSK for RNG fidelity, but the reference junior
    # schedule below never uses it.
    k_vec = _draw_initial_k(pop_size, rng)
    kw_ind: np.ndarray | None = None
    all_imp = np.zeros(4, dtype=np.float64)

    conv_nfes: list[int] = []
    conv_best: list[float] = []
    _append_convergence(conv_nfes, conv_best, nfes, best_fitness)

    terminated_on_target = False
    generation = 0
    negative_kf_generations = 0
    positive_kf_generations = 0

    _rand_buf = np.empty((3, pop_size, dim), dtype=np.float64)  # W1.2 reuse (max NP)
    while nfes < max_nfes:
        generation += 1

        if kw_ind is None or nfes < 0.1 * max_nfes:
            kw_ind = INITIAL_KW.copy()
            adaptive_phase = False
        else:
            kw_ind = 0.95 * kw_ind + 0.05 * all_imp
            kw_ind = kw_ind / np.sum(kw_ind)
            adaptive_phase = True

        slots = _select_parameter_slots(rng, pop_size, kw_ind)
        kr = KR_POOL[slots]
        adaptive_pool_draw = float(rng.random()) if adaptive_phase else None
        kf, used_negative = _apgsk_kf_values(
            slots,
            adaptive_phase=adaptive_phase,
            adaptive_pool_draw=adaptive_pool_draw,
            nfes=nfes,
            max_nfes=max_nfes,
        )
        if used_negative:
            negative_kf_generations += 1
        else:
            positive_kf_generations += 1

        junior_dim = _stochastic_junior_dimension(
            dim,
            nfes,
            max_nfes,
            float(rng.random()),
        )

        # W1.3 (2026-07-25): dead pop/popold double-copy removed -- single
        # buffer, in-place masked scatter at selection (see gsk.py).
        ind_best = stable_argsort(fitness)
        rg1, rg2, rg3 = gained_shared_junior_r1r2r3(ind_best, rng, validate=False)
        r1, r2, r3 = gained_shared_senior_r1r2r3(ind_best, SENIOR_P, rng, validate=False)

        junior_probability = junior_dim / dim
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
        optimizer="apgsk",
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
            "kf_pool_negative": KF_POOL_NEGATIVE.tolist(),
            "kr_pool": KR_POOL.tolist(),
            "senior_p": SENIOR_P,
            "final_pop_size": pop_size,
            "generations": generation,
            "negative_kf_generations": negative_kf_generations,
            "positive_kf_generations": positive_kf_generations,
        },
        notes="",
    )
