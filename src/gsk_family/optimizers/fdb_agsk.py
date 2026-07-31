"""FDB-AGSK optimizer."""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from gsk_family.benchmark_adapter.problem import BenchmarkProblem
from gsk_family.common.numeric_compat import compat_round_int, stable_argsort
from gsk_family.common.population import (
    gsk_initial_population_from_options,
    gsk_restore_rng_after_initialization,
)
from gsk_family.common.rng import RandomContext
from gsk_family.optimizers.agsk import (
    INITIAL_KW,
    KF_POOL,
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
from gsk_family.optimizers._kernels import gsk_build_trial
from gsk_family.optimizers.fdb_scores import (
    fdb_score_best,
    fdb_score_ranking,
    fdb_score_roulette,
)
from gsk_family.stats import compute_error
from gsk_family.types import ConvergenceTrace, OptimizerOptions, OptimizerResult


def _validate_fdb_case(value: Any) -> int:
    """Validate the FDB donor injection case number."""
    case = int(value)
    if case != float(value) or case not in {1, 2, 3, 4, 5}:
        raise ValueError(f"fdb_case must be an integer in 1..5, got {value!r}.")
    return case


def _base_junior_neighbors(ind_best: Any, *, validate: bool = True) -> tuple[np.ndarray, np.ndarray]:
    """Return rank-neighbor R1/R2 arrays before FDB R3 injection."""
    order = np.asarray(ind_best, dtype=np.int64).reshape(-1)
    pop_size = int(order.size)
    if pop_size < 4:
        raise ValueError("Junior donor helper requires NP >= 4.")
    if validate and not np.array_equal(np.sort(order), np.arange(pop_size, dtype=np.int64)):
        raise ValueError("ind_best must be a 0-based permutation of 0..NP-1.")

    idx = np.arange(pop_size, dtype=np.int64)
    rank_of = np.empty(pop_size, dtype=np.int64)
    rank_of[order] = idx

    r1 = np.empty(pop_size, dtype=np.int64)
    r2 = np.empty(pop_size, dtype=np.int64)

    best_mask = rank_of == 0
    worst_mask = rank_of == pop_size - 1
    middle_mask = ~(best_mask | worst_mask)

    r1[best_mask] = order[1]
    r2[best_mask] = order[2]
    r1[worst_mask] = order[pop_size - 3]
    r2[worst_mask] = order[pop_size - 2]

    middle_ranks = rank_of[middle_mask]
    r1[middle_mask] = order[middle_ranks - 1]
    r2[middle_mask] = order[middle_ranks + 1]
    return r1, r2


def _fdb_junior_r1r2r3(
    ind_best: Any,
    fdb_case: int,
    fdb_index: int | None,
    rfdb_index: int | None,
    rng: RandomContext,
    *,
    max_iterations: int = 1000,
    validate: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return junior donor arrays with FDB case-specific injections."""
    r1, r2 = _base_junior_neighbors(ind_best, validate=validate)
    pop_size = int(r1.size)
    idx = np.arange(pop_size, dtype=np.int64)

    if fdb_case in {1, 2}:
        r3 = np.floor(np.asarray(rng.random(pop_size)) * pop_size).astype(np.int64)
    elif fdb_case == 3:
        if fdb_index is None or rfdb_index is None:
            raise ValueError("fdb_case 3 requires FDB and RFDB indices.")
        r2 = np.full(pop_size, int(rfdb_index), dtype=np.int64)
        r3 = np.full(pop_size, int(fdb_index), dtype=np.int64)
    elif fdb_case == 4:
        if fdb_index is None or rfdb_index is None:
            raise ValueError("fdb_case 4 requires FDB and RFDB indices.")
        r1 = np.full(pop_size, int(rfdb_index), dtype=np.int64)
        r3 = np.full(pop_size, int(fdb_index), dtype=np.int64)
    elif fdb_case == 5:
        if fdb_index is None:
            raise ValueError("fdb_case 5 requires an FDB index.")
        r3 = np.full(pop_size, int(fdb_index), dtype=np.int64)
    else:
        raise ValueError(f"Unsupported fdb_case {fdb_case}.")

    for iteration in range(max_iterations + 1):
        collision = (r3 == r2) | (r3 == r1) | (r3 == idx)
        count = int(np.count_nonzero(collision))
        if count == 0:
            return r1, r2, r3
        if iteration >= max_iterations:
            raise RuntimeError("Cannot generate collision-free junior R3 donors.")
        r3[collision] = np.floor(np.asarray(rng.random(count)) * pop_size).astype(np.int64)

    raise AssertionError("Unreachable junior donor loop exit.")


def _sample_block(block: np.ndarray, pop_size: int, rng: RandomContext, *, name: str) -> np.ndarray:
    """Sample donor indices uniformly from one senior donor block."""
    values = np.asarray(block, dtype=np.int64).reshape(-1)
    if values.size == 0:
        raise ValueError(f"{name} donor block is empty.")
    draws = np.floor(np.asarray(rng.random(pop_size)) * values.size).astype(np.int64)
    return values[draws]


def _fdb_senior_r1r2r3(
    ind_best: Any,
    fdb_case: int,
    fdb_index: int | np.ndarray | None,
    rng: RandomContext,
    *,
    validate: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return senior donor arrays with FDB case-specific injections."""
    order = np.asarray(ind_best, dtype=np.int64).reshape(-1)
    pop_size = int(order.size)
    if validate and not np.array_equal(np.sort(order), np.arange(pop_size, dtype=np.int64)):
        raise ValueError("ind_best must be a 0-based permutation of 0..NP-1.")

    top_end = compat_round_int(pop_size * SENIOR_P)
    mid_end = compat_round_int(pop_size * (1.0 - SENIOR_P))
    if top_end <= 0 or mid_end <= top_end or mid_end >= pop_size:
        raise ValueError(
            "Senior donor partition contains an empty block: "
            f"NP={pop_size}, p={SENIOR_P}, top_end={top_end}, mid_end={mid_end}."
        )

    r1 = _sample_block(order[:top_end], pop_size, rng, name="R1")

    if fdb_case == 1:
        if fdb_index is None or isinstance(fdb_index, np.ndarray):
            raise ValueError("fdb_case 1 requires a scalar FDB index.")
        r2 = np.full(pop_size, int(fdb_index), dtype=np.int64)
        r3 = _sample_block(order[mid_end:], pop_size, rng, name="R3")
    elif fdb_case == 2:
        ranking = np.asarray(fdb_index, dtype=np.int64).reshape(-1)
        r2 = _sample_block(order[top_end:mid_end], pop_size, rng, name="R2")
        r3 = _sample_block(ranking[mid_end:], pop_size, rng, name="FDB R3")
    elif fdb_case in {3, 4, 5}:
        r2 = _sample_block(order[top_end:mid_end], pop_size, rng, name="R2")
        r3 = _sample_block(order[mid_end:], pop_size, rng, name="R3")
    else:
        raise ValueError(f"Unsupported fdb_case {fdb_case}.")

    return r1.astype(np.int64, copy=False), r2.astype(np.int64, copy=False), r3.astype(
        np.int64, copy=False
    )


def _fdb_indices(
    fdb_case: int,
    population: np.ndarray,
    fitness: np.ndarray,
    rng: RandomContext,
) -> tuple[int | np.ndarray | None, int | None]:
    """Select the FDB index payload required by the active FDB case."""
    if fdb_case == 1:
        return fdb_score_best(population, fitness, rng), None
    if fdb_case == 2:
        return fdb_score_ranking(population, fitness, rng), None
    if fdb_case in {3, 4}:
        return (
            fdb_score_best(population, fitness, rng),
            fdb_score_roulette(population, fitness, rng),
        )
    if fdb_case == 5:
        return fdb_score_best(population, fitness, rng), None
    raise ValueError(f"Unsupported fdb_case {fdb_case}.")


def optimize(problem: BenchmarkProblem, options: OptimizerOptions | dict[str, Any]) -> OptimizerResult:
    """Run the FDB-AGSK optimizer."""
    seed = int(_option_value(options, "seed"))
    rand_generator = str(_option_value(options, "rand_generator", "twister"))
    np_default = int(_option_value(options, "np", 100))
    np_init = int(_option_value(options, "np_init", np_default))
    min_pop_size = int(_option_value(options, "min_pop_size", 12))
    fdb_case = _validate_fdb_case(_option_value(options, "fdb_case", 1))

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
    best_x = pop[0, :].copy()

    n_init = min(pop_size, max_nfes - nfes)
    best_fitness, best_x = _scan_best(pop, fitness, n_init, best_fitness, best_x)
    nfes += n_init

    k_vec = _draw_initial_k(pop_size, rng)
    kw_ind: np.ndarray | None = None
    all_imp = np.zeros(4, dtype=np.float64)

    conv_nfes: list[int] = []
    conv_best: list[float] = []
    _append_convergence(conv_nfes, conv_best, nfes, best_fitness)

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
        fdb_index, rfdb_index = _fdb_indices(fdb_case, pop, fitness, rng)
        ind_best = stable_argsort(fitness)
        rg1, rg2, rg3 = _fdb_junior_r1r2r3(
            ind_best,
            fdb_case,
            None if isinstance(fdb_index, np.ndarray) else fdb_index,
            rfdb_index,
            rng,
            validate=False,
        )
        r1, r2, r3 = _fdb_senior_r1r2r3(ind_best, fdb_case, fdb_index, rng, validate=False)

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

    error = compute_error(best_fitness, float(problem.optimum), float(problem.target_error))

    return OptimizerResult(
        optimizer="fdb-agsk",
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
            "fdb_case": fdb_case,
            "np_init": np_init,
            "min_pop_size": min_pop_size,
            "kf_pool": KF_POOL.tolist(),
            "kr_pool": KR_POOL.tolist(),
            "final_pop_size": pop_size,
            "generations": generation,
        },
        notes="",
    )
