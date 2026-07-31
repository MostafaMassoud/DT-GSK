"""ATMALS-GSK optimizer."""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from gsk_family.benchmark_adapter.problem import BenchmarkProblem
from gsk_family.common.bounds import gsk_bound_repair
from gsk_family.common.donors import gained_shared_junior_r1r2r3
from gsk_family.common.numeric_compat import compat_fix_int, compat_round_int, stable_argsort
from gsk_family.optimizers._kernels import gsk_build_trial
from gsk_family.common.population import (
    gsk_initial_population_from_options,
    gsk_restore_rng_after_initialization,
)
from gsk_family.common.rng import RandomContext
from gsk_family.optimizers.agsk import _append_convergence, _option_value, _scan_best
from gsk_family.optimizers.atmals_helpers import (
    AtmalsProbabilityMemory,
    atmals_power_roulette_select,
    atmals_senior_r1r2r3_cec2011,
    atmals_senior_r1r2r3_cec2017,
)
from gsk_family.stats import compute_error
from gsk_family.types import ConvergenceTrace, OptimizerOptions, OptimizerResult


def _array_option(options: Any, name: str, default: np.ndarray) -> np.ndarray:
    """Read an ATMALS numeric pool option or return a defensive default copy."""
    value = _option_value(options, name, None)
    if value is None:
        return default.astype(np.float64, copy=True)
    arr = np.asarray(value, dtype=np.float64).reshape(-1)
    if arr.size == 0:
        raise ValueError(f"{name} must not be empty.")
    return arr


def _validate_protocol(protocol: Any) -> str:
    """Validate the ATMALS protocol branch."""
    value = str(protocol).strip().lower()
    if value not in {"cec2017", "cec2011"}:
        raise ValueError(f"protocol must be 'cec2017' or 'cec2011', got {protocol!r}.")
    return value


def _best_half_mean(values: np.ndarray, pop_size: int) -> float:
    """Return the mean of the best half of a fitness-like vector."""
    sorted_values = np.sort(np.asarray(values, dtype=np.float64).reshape(-1), kind="stable")
    count = max(1, int(np.floor(pop_size / 2)))
    return float(np.mean(sorted_values[:count]))


def _mean_fit_signal(
    fitness: np.ndarray,
    *,
    problem: BenchmarkProblem,
    protocol: str,
) -> float:
    """Compute the ATMALS mean-fitness signal for a protocol branch."""
    if protocol == "cec2011" or np.isnan(problem.optimum):
        values = np.asarray(fitness, dtype=np.float64)
    else:
        values = np.abs(np.asarray(fitness, dtype=np.float64) - float(problem.optimum))
    return _best_half_mean(values, int(fitness.size))


def _local_search(
    trial: np.ndarray,
    best_x: np.ndarray,
    problem: BenchmarkProblem,
    rng: RandomContext,
    *,
    nls: int,
    pls: float,
    range_ls: float,
    protocol: str,
) -> np.ndarray:
    """Apply the ATMALS local perturbation around the current best vector."""
    pop_size, dim = trial.shape
    if nls <= 0:
        return trial
    # Intentional reference-parity draw: consume the same RNG sequence the
    # reference implementation draws here (a permutation slice) to keep the
    # stream aligned, even though the sliced indices are not used downstream.
    # Do NOT remove -- deleting it desynchronizes the RNG from the reference.
    _ = rng.permutation(pop_size)[:nls]
    out = trial.copy()
    lower = problem.lb
    upper = problem.ub
    eps = np.finfo(np.float64).eps
    for row in range(min(nls, pop_size)):
        out[row, :] = best_x
        for col in range(dim):
            if float(rng.random()) < (float(pls) / dim):
                out[row, col] = out[row, col] + (
                    (2.0 * float(rng.random()) - 1.0)
                    * float(range_ls)
                    * (upper[col] - lower[col])
                )
                if out[row, col] < lower[col]:
                    out[row, col] = lower[col] if protocol == "cec2017" else lower[col] + eps
                if out[row, col] > upper[col]:
                    out[row, col] = upper[col] if protocol == "cec2017" else upper[col] - eps
    return out


def _gsk_generation(
    popold: np.ndarray,
    fitness: np.ndarray,
    problem: BenchmarkProblem,
    rng: RandomContext,
    *,
    kf: float,
    kr: float,
    k_rate: float,
    generation: int,
    g_max: float,
    protocol: str,
) -> np.ndarray:
    """Generate one ATMALS GSK-style trial population."""
    pop_size, dim = popold.shape
    schedule_base = 1.0 - (float(generation) / float(g_max))
    junior_probability = float(np.ceil(dim * np.power(schedule_base, k_rate))) / float(dim)

    ind_best = stable_argsort(fitness)
    rg1, rg2, rg3 = gained_shared_junior_r1r2r3(ind_best, rng, validate=False)
    if protocol == "cec2017":
        r1, r2, r3 = atmals_senior_r1r2r3_cec2017(ind_best, 0.1, rng)
    else:
        r1, r2, r3 = atmals_senior_r1r2r3_cec2011(ind_best, rng)

    rand_block = np.asarray(rng.random((3, pop_size, dim)), dtype=np.float64)
    trial = gsk_build_trial(
        popold,
        fitness,
        rg1,
        rg2,
        rg3,
        r1,
        r2,
        r3,
        kf_junior=float(kf),
        kf_senior=float(kf),
        junior_prob=junior_probability,
        rand_split=rand_block[0],
        rand_kr_junior=rand_block[1],
        rand_kr_senior=rand_block[2],
        kr=float(kr),
        lb=problem.lb,
        ub=problem.ub,
    )
    return trial


def _cec2011_dim1_generation(
    popold: np.ndarray,
    fitness: np.ndarray,
    problem: BenchmarkProblem,
    rng: RandomContext,
) -> np.ndarray:
    """Generate the ATMALS CEC2011 one-dimensional fallback trial population."""
    pop_size, dim = popold.shape
    pop = popold.copy()
    ind_best = stable_argsort(fitness)
    r1, r2, r3 = atmals_senior_r1r2r3_cec2011(ind_best, rng)

    gained_senior = np.zeros_like(pop)
    senior_worse = fitness > fitness[r2]
    if np.any(senior_worse):
        gained_senior[senior_worse, :] = pop[senior_worse, :] + 0.5 * (
            pop[r1[senior_worse], :]
            - pop[senior_worse, :]
            + pop[r2[senior_worse], :]
            - pop[r3[senior_worse], :]
        )
    senior_other = ~senior_worse
    if np.any(senior_other):
        gained_senior[senior_other, :] = pop[senior_other, :] + 0.5 * (
            pop[r1[senior_other], :]
            - pop[r2[senior_other], :]
            + pop[senior_other, :]
            - pop[r3[senior_other], :]
        )

    gained_senior = gsk_bound_repair(gained_senior, pop, problem.lb, problem.ub)
    senior_mask = np.ones((pop_size, dim), dtype=bool)
    senior_mask &= np.asarray(rng.random((pop_size, dim))) <= 0.9
    trial = pop.copy()
    trial[senior_mask] = gained_senior[senior_mask]
    return trial


def optimize(problem: BenchmarkProblem, options: OptimizerOptions | dict[str, Any]) -> OptimizerResult:
    """Run the ATMALS-GSK optimizer."""
    seed = int(_option_value(options, "seed"))
    rand_generator = str(_option_value(options, "rand_generator", "twister"))
    protocol = _validate_protocol(_option_value(options, "protocol", "cec2017"))
    pop_size = int(_option_value(options, "np", 100))
    if pop_size < 12:
        raise ValueError(f"np must be at least 12 for ATMALS-GSK, got {pop_size}.")
    if problem.max_nfes <= 0:
        raise ValueError(f"problem.max_nfes must be positive, got {problem.max_nfes}.")

    kf_pool = _array_option(options, "kf_pool", np.arange(0.2, 0.8000001, 0.1))
    kr_pool = _array_option(options, "kr_pool", np.arange(0.85, 1.0000001, 0.01))
    k_pool = _array_option(options, "k_pool", np.arange(8.0, 30.0000001, 1.0))
    p_pool = _array_option(options, "p_pool", np.arange(0.05, 0.1500001, 0.01))
    pls_pool = _array_option(options, "pls_pool", np.arange(1.0, 2.0000001, 0.1))

    start = time.perf_counter()
    rng = RandomContext(seed, rand_generator)

    dim = int(problem.dim)
    max_nfes = int(problem.max_nfes)
    g_max = max_nfes / pop_size if protocol == "cec2011" else compat_fix_int(max_nfes / pop_size)

    kf = 0.5
    kr = 0.9
    k_rate = 10.0
    p_value = 0.1
    alpha = 0.98
    pls = 1.0
    nls = int(compat_round_int(0.05 * pop_size))
    rp_min = 3.0
    range_ls_max = 0.2
    range_ls_min = 1e-10

    prob_kf_memory = AtmalsProbabilityMemory.create(kf_pool, alpha)
    prob_kr_memory = AtmalsProbabilityMemory.create(kr_pool, alpha)
    prob_k_memory = AtmalsProbabilityMemory.create(k_pool, alpha)
    prob_p_memory = AtmalsProbabilityMemory.create(p_pool, alpha)
    prob_pls_memory = AtmalsProbabilityMemory.create(pls_pool, alpha)

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

    fitness = np.asarray(problem.evaluate(pop), dtype=np.float64).reshape(-1)
    if fitness.shape != (pop_size,):
        raise ValueError(
            f"problem.evaluate returned shape {fitness.shape}; expected ({pop_size},)."
        )
    if not np.all(np.isfinite(fitness)):
        raise ValueError("Initial population fitness contains non-finite values.")

    mean_fit = _mean_fit_signal(fitness, problem=problem, protocol=protocol)

    nfes = 0
    best_fitness = float("1e300")
    best_x = pop[0, :].copy()
    n_init = min(pop_size, max_nfes - nfes)
    best_fitness, best_x = _scan_best(pop, fitness, n_init, best_fitness, best_x)
    nfes += n_init

    conv_nfes: list[int] = []
    conv_best: list[float] = []
    _append_convergence(conv_nfes, conv_best, nfes, best_fitness)

    generation = 0
    while nfes < max_nfes:
        generation += 1
        if g_max == 0:
            raise ValueError("G_Max is zero; increase max_nfes or reduce np.")

        # W-CL1 (2026-07-25): the former full-population snapshot copied here
        # was dead -- popold is read-only until selection (_gsk_generation
        # copies it internally, _local_search touches only the fresh trial,
        # the dim-1 path is read-only), so the selection scatter writes popold
        # directly. Removes one full NP*D copy/gen (~506 us at D=1000).
        if protocol == "cec2011" and dim == 1:
            trial = _cec2011_dim1_generation(popold, fitness, problem, rng)
        else:
            trial = _gsk_generation(
                popold,
                fitness,
                problem,
                rng,
                kf=kf,
                kr=kr,
                k_rate=k_rate,
                generation=generation,
                g_max=float(g_max),
                protocol=protocol,
            )

        range_ls = range_ls_max - (range_ls_max - range_ls_min) * (
            generation / float(g_max)
        )
        trial = _local_search(
            trial,
            best_x,
            problem,
            rng,
            nls=nls,
            pls=pls,
            range_ls=range_ls,
            protocol=protocol,
        )

        children_fitness = np.asarray(problem.evaluate(trial), dtype=np.float64).reshape(-1)
        if children_fitness.shape != (pop_size,):
            raise ValueError(
                f"problem.evaluate returned shape {children_fitness.shape}; expected ({pop_size},)."
            )
        if not np.all(np.isfinite(children_fitness)):
            raise ValueError("Child population fitness contains non-finite values.")

        mean_fit_new = _mean_fit_signal(children_fitness, problem=problem, protocol=protocol)

        rp = rp_min + (range_ls_max - range_ls_min) * (generation / float(g_max))
        prob_kf = prob_kf_memory.update(kf, mean_fit, mean_fit_new)
        prob_kr = prob_kr_memory.update(kr, mean_fit, mean_fit_new)
        prob_k = prob_k_memory.update(k_rate, mean_fit, mean_fit_new)
        prob_p = prob_p_memory.update(p_value, mean_fit, mean_fit_new)
        prob_pls = prob_pls_memory.update(pls, mean_fit, mean_fit_new)

        kf = float(kf_pool[atmals_power_roulette_select(prob_kf, rp, rng)])
        kr = float(kr_pool[atmals_power_roulette_select(prob_kr, rp, rng)])
        k_rate = float(k_pool[atmals_power_roulette_select(prob_k, rp, rng)])
        p_value = float(p_pool[atmals_power_roulette_select(prob_p, rp, rng)])
        pls = float(pls_pool[atmals_power_roulette_select(prob_pls, rp, rng)])
        mean_fit = mean_fit_new

        n_count = min(pop_size, max_nfes - nfes)
        best_fitness, best_x = _scan_best(
            trial,
            children_fitness,
            n_count,
            best_fitness,
            best_x,
        )
        nfes += n_count

        child_is_better = fitness > children_fitness
        fitness = np.where(child_is_better, children_fitness, fitness)
        popold[child_is_better, :] = trial[child_is_better, :]

        _append_convergence(conv_nfes, conv_best, nfes, best_fitness)

    if np.isnan(problem.optimum):
        error = float("nan")
    elif problem.suite == "cec2017" and protocol == "cec2017":
        error = compute_error(
            best_fitness,
            float(problem.optimum),
            float(problem.target_error),
            absolute=True,
        )
    else:
        error = compute_error(best_fitness, float(problem.optimum), float(problem.target_error))

    return OptimizerResult(
        optimizer="atmals-gsk",
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
            "protocol": protocol,
            "np": pop_size,
            "kf_init": 0.5,
            "kr_init": 0.9,
            "k_init": 10.0,
            "p_gsk": 0.1,
            "kf_pool": kf_pool.tolist(),
            "kr_pool": kr_pool.tolist(),
            "k_pool": k_pool.tolist(),
            "p_pool": p_pool.tolist(),
            "pls_pool": pls_pool.tolist(),
            "alpha": alpha,
            "pls_init": 1.0,
            "nls": nls,
            "rp_min": rp_min,
            "rp_max": 5.0,
            "range_ls_max": range_ls_max,
            "range_ls_min": range_ls_min,
            "probability_memory": "compact_weighted_sum",
            "probability_memory_rows": int(prob_kf_memory.row_count),
            "generations": generation,
        },
        notes="",
    )
