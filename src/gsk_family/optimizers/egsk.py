"""Enhanced Gaining-Sharing Knowledge (eGSK) optimizer.

Faithful Python port of the MATLAB reference
``01-GSK_Family_MATLAB_v1.0/gsk_family/src/optimizers/egsk/{egsk_optimize,
egsk_gained_shared_senior, egsk_ip_refine}.m`` (Jawad, Roshdy & Mohamed,
https://doi.org/10.1016/j.rico.2025.100542).

EGSK = base GSK plus three enhancements:

1. **Dual adaptive knowledge factors** ``KF1`` (junior) and ``KF2`` (senior),
   constant ``0.5`` until the late stage (``g >= 0.75 * G_Max``), then recomputed
   per individual from a triangular membership over ranked-fitness anchors.
2. A **fixed 10/90 senior partition** -- equal to the shared senior helper with
   ``p = 0.1`` (``round(NP*0.9) == round(NP*(1-0.1))`` for every NP), so the
   existing :func:`gained_shared_senior_r1r2r3` is reused.
3. **Interior-point local refinement** that, in the late stage, polishes the
   incumbent. The MATLAB reference uses ``fmincon`` (SQP, Optimization Toolbox);
   this port substitutes :func:`scipy.optimize.minimize` (``method="SLSQP"``),
   the closest open equivalent. Because ``fmincon`` and ``SLSQP`` are different
   solvers, results are validated by **statistical equivalence** against the
   reference CSVs, not byte-identity (the GSK population search itself is
   byte-faithful via the shared kernel + Threefry RNG).

The per-generation random-draw order matches the rest of the family (junior
donors -> senior donors -> one ``(3, NP, dim)`` mask block), so the GSK core
reproduces the reference stream; the IP-refine draws no random numbers.
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from gsk_family.benchmark_adapter.problem import BenchmarkProblem
from gsk_family.common.donors import (
    gained_shared_junior_r1r2r3,
    gained_shared_senior_r1r2r3,
)
from gsk_family.common.numeric_compat import stable_argsort
from gsk_family.common.population import (
    gsk_initial_population_from_options,
    gsk_restore_rng_after_initialization,
)
from gsk_family.common.rng import RandomContext
from gsk_family.optimizers._kernels import gsk_build_trial
from gsk_family.types import ConvergenceTrace, OptimizerOptions, OptimizerResult

_MISSING = object()

# eGSK reference constants (egsk_optimize.m:106-141).
_DEFAULT_NP = 100
_SENIOR_P = 0.1            # fixed 10/90 partition
_KR = 1.0                 # Knowledge Ratio
_K = 10.0                 # Knowledge Rate (scalar)
_KF_INIT = 0.5            # initial junior/senior knowledge factors
_LATE_STAGE_FRAC = 0.75   # late-stage trigger g >= 0.75 * G_Max
_IP_FE_FRAC = 2.0e-3      # IP budget = ceil(2e-3 * max_nfes)
_VAL_2_REACH = 1e-8       # reference target tolerance when none provided


def _option_value(options: Any, name: str, default: Any = _MISSING) -> Any:
    """Read an optimizer option from object, dict, or nested values mapping."""
    if options is None:
        if default is _MISSING:
            raise ValueError(f"options.{name} is required.")
        return default
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


def _scan_best_with_index(
    candidates: np.ndarray,
    fitness: np.ndarray,
    n_count: int,
    best_fitness: float,
    best_x: np.ndarray,
    best_row: int,
) -> tuple[float, np.ndarray, int]:
    """eGSK best-so-far scan that also tracks the producing row (``NO_i``).

    Equivalent to the reference ``for i = 1:n`` loop: the argmin of the first
    ``n_count`` rows updates the incumbent (and its row index) only when it
    strictly improves the running best; ``np.argmin`` returns the first
    occurrence, matching the loop's tie-handling.
    """
    if n_count <= 0:
        return best_fitness, best_x, best_row
    local = fitness[:n_count]
    idx = int(np.argmin(local))
    value = float(local[idx])
    if value < best_fitness:
        return value, candidates[idx, :].copy(), idx
    return best_fitness, best_x, best_row


def _triangular_membership(
    x: np.ndarray, a: np.ndarray, b: np.ndarray, c: np.ndarray
) -> np.ndarray:
    """Reference triangular membership (egsk_optimize.m:235-263), vectorized.

    ``y = (x-a)/(b-a)`` on ``[a, b]``, ``(c-x)/(c-b)`` on ``[b, c]``, else ``0``.
    ``a``/``b``/``c`` may be per-individual vectors (KF1) or scalars (KF2). The
    degenerate-denominator behaviour (0/0 -> NaN) is preserved exactly; the
    caller then applies the reference clamp ``y(y>=1)=0; y(y<=0)=0``.
    """
    a = np.broadcast_to(np.asarray(a, dtype=np.float64), x.shape)
    b = np.broadcast_to(np.asarray(b, dtype=np.float64), x.shape)
    c = np.broadcast_to(np.asarray(c, dtype=np.float64), x.shape)
    with np.errstate(divide="ignore", invalid="ignore"):
        left = (x - a) / (b - a)
        right = (c - x) / (c - b)
    y = np.zeros_like(x)
    on_left = (a <= x) & (x <= b)
    on_right = (b <= x) & (x <= c)
    y = np.where(on_left, left, np.where(on_right, right, y))
    return y


def _clamp_kf(kf: np.ndarray) -> np.ndarray:
    """Reference clamp: zero out memberships >= 1 or <= 0 (egsk_optimize.m:245-246).

    Degenerate triangular anchors (equal fitnesses -> ``0/0``) yield non-finite
    memberships. The reference leaves them NaN; its NaN-ignoring ``min`` then
    rejects the resulting NaN trial, so the individual keeps its parent. This
    port instead maps non-finite memberships to ``0`` -- behaviourally a no-move
    (trial == parent) -- which is equivalent for selection while keeping the
    Python benchmark adapter's finite-value contract intact.
    """
    kf = np.array(kf, dtype=np.float64, copy=True)
    kf[kf >= 1.0] = 0.0
    kf[kf <= 0.0] = 0.0
    kf[~np.isfinite(kf)] = 0.0
    return kf


def _egsk_ip_refine(
    best_x: np.ndarray,
    best_fitness: float,
    nfes: int,
    problem: BenchmarkProblem,
    max_nfes: int,
) -> tuple[np.ndarray, float, int]:
    """Interior-point refinement (egsk_ip_refine.m) via scipy SLSQP.

    Substitutes ``fmincon(...,'sqp')`` with ``scipy.optimize.minimize(method=
    "SLSQP")`` -- the same role (bounded gradient-based local polish), a
    different solver. Budget is ``ceil(2e-3 * max_nfes)`` function evaluations
    (matching ``MaxFunEvals``), capped by the remaining global budget; every
    objective call (function + finite-difference gradient) is counted into
    ``nfes`` exactly as ``details.funcCount`` is in the reference. Draws no RNG.
    """
    try:
        from scipy.optimize import minimize
    except Exception:  # pragma: no cover - scipy is a declared dependency
        return best_x, best_fitness, nfes

    ip_fe = int(np.ceil(_IP_FE_FRAC * max_nfes))
    budget = min(ip_fe, max_nfes - nfes)
    if budget <= 0:
        return best_x, best_fitness, nfes

    dim = int(problem.dim)
    state = {"count": 0, "best_f": float(best_fitness), "best_x": np.asarray(best_x, dtype=np.float64).copy()}

    class _BudgetExceeded(Exception):
        """Internal sentinel raised when the IP-refine evaluation budget is reached."""

    def objective(z: np.ndarray) -> float:
        """Evaluate one candidate, count the call, and track the best seen."""
        if state["count"] >= budget:
            raise _BudgetExceeded
        state["count"] += 1
        val = float(np.asarray(problem.evaluate(np.asarray(z, dtype=np.float64).reshape(1, dim))).reshape(-1)[0])
        if np.isfinite(val) and val < state["best_f"]:
            state["best_f"] = val
            state["best_x"] = np.asarray(z, dtype=np.float64).copy()
        return val

    bounds = list(zip(np.asarray(problem.lb, dtype=np.float64).tolist(),
                      np.asarray(problem.ub, dtype=np.float64).tolist()))
    import warnings
    try:
        with warnings.catch_warnings():
            # SLSQP may step marginally outside bounds and clip; benign.
            warnings.simplefilter("ignore", RuntimeWarning)
            minimize(
                objective,
                np.asarray(best_x, dtype=np.float64).reshape(-1).copy(),
                method="SLSQP",
                bounds=bounds,
                options={"maxiter": max(1, budget), "ftol": 1e-12},
            )
    except _BudgetExceeded:
        pass
    except Exception:  # pragma: no cover - solver robustness
        pass

    nfes += int(state["count"])
    return state["best_x"], float(state["best_f"]), nfes


def optimize(problem: BenchmarkProblem, options: OptimizerOptions | dict[str, Any]) -> OptimizerResult:
    """Run the Enhanced GSK optimizer (faithful eGSK port)."""
    seed = int(_option_value(options, "seed"))
    rand_generator = str(_option_value(options, "rand_generator", "twister"))
    pop_size = int(_option_value(options, "np", _DEFAULT_NP))

    if problem.max_nfes <= 0:
        raise ValueError(f"problem.max_nfes must be positive, got {problem.max_nfes}.")
    if problem.dim <= 0:
        raise ValueError(f"problem.dim must be positive, got {problem.dim}.")
    if pop_size <= 0:
        raise ValueError(f"np must be positive, got {pop_size}.")

    start = time.perf_counter()
    rng = RandomContext(seed, rand_generator)

    dim = int(problem.dim)
    max_nfes = int(problem.max_nfes)
    lb = np.asarray(problem.lb, dtype=np.float64)
    ub = np.asarray(problem.ub, dtype=np.float64)
    has_optimum = not np.isnan(problem.optimum)
    val_2_reach = float(problem.target_error) if not np.isnan(problem.target_error) else _VAL_2_REACH
    g_max = max_nfes // pop_size

    kf1 = np.full(pop_size, float(_option_value(options, "kf1", _KF_INIT)), dtype=np.float64)
    kf2 = np.full(pop_size, float(_option_value(options, "kf2", _KF_INIT)), dtype=np.float64)
    kr = float(_option_value(options, "kr", _KR))
    k_rate = float(_option_value(options, "k", _K))

    popold = gsk_initial_population_from_options(options, rng, pop_size, lb, ub, dim=dim)
    gsk_restore_rng_after_initialization(options, rng)
    pop = popold.copy()
    del popold        # W-CL2: single population buffer from here on

    fitness = np.asarray(problem.evaluate(pop), dtype=np.float64).reshape(-1)
    if fitness.shape != (pop_size,):
        raise ValueError(f"problem.evaluate returned shape {fitness.shape}; expected ({pop_size},).")
    if not np.all(np.isfinite(fitness)):
        raise ValueError("Initial population fitness contains non-finite values.")

    nfes = 0
    best_fitness = float("1e300")
    best_x = pop[0, :].copy()
    best_row = 0
    n_init = min(pop_size, max_nfes - nfes)
    best_fitness, best_x, best_row = _scan_best_with_index(pop, fitness, n_init, best_fitness, best_x, best_row)
    nfes += n_init

    conv_nfes: list[int] = []
    conv_best: list[float] = []
    conv_nfes.append(int(nfes))
    conv_best.append(float(best_fitness))

    generation = 0
    _rand_buf = np.empty((3, pop_size, dim), dtype=np.float64)  # W1.2 reuse
    while nfes < max_nfes:
        generation += 1
        # Junior dimensionality schedule (scalar K -> scalar count broadcast).
        junior_count = int(np.ceil(dim * (1.0 - generation / g_max) ** k_rate)) if g_max > 0 else 0
        junior_prob = float(junior_count) / float(dim)

        # W-CL2 (2026-07-25): dead double-buffer copy removed -- single array,
        # in-place masked scatters at selection (pop is read-only until then;
        # trial is freshly allocated).
        ind_best = stable_argsort(fitness)
        rg1, rg2, rg3 = gained_shared_junior_r1r2r3(ind_best, rng, validate=False)
        r1, r2, r3 = gained_shared_senior_r1r2r3(ind_best, _SENIOR_P, rng, validate=False)

        rand_block = np.asarray(rng.random((3, pop_size, dim)), dtype=np.float64)
        # W1.2 (2026-07-25): copy the F-order planes once into a persistent
        # C-buffer -- same doubles, same (i,j); the kernel-side coercion becomes
        # a free pass-through (see gsk.py).
        np.copyto(_rand_buf[0], rand_block[0])
        np.copyto(_rand_buf[1], rand_block[1])
        np.copyto(_rand_buf[2], rand_block[2])
        trial = gsk_build_trial(
            pop, fitness, rg1, rg2, rg3, r1, r2, r3,
            kf_junior=kf1, kf_senior=kf2,
            junior_prob=junior_prob,
            rand_split=_rand_buf[0], rand_kr_junior=_rand_buf[1], rand_kr_senior=_rand_buf[2],
            kr=kr, lb=lb, ub=ub,
        )

        children_fitness = np.asarray(problem.evaluate(trial), dtype=np.float64).reshape(-1)
        if children_fitness.shape != (pop_size,):
            raise ValueError(f"problem.evaluate returned shape {children_fitness.shape}; expected ({pop_size},).")
        if not np.all(np.isfinite(children_fitness)):
            raise ValueError("Child population fitness contains non-finite values.")

        n_count = min(pop_size, max_nfes - nfes)
        best_fitness, best_x, best_row = _scan_best_with_index(
            trial, children_fitness, n_count, best_fitness, best_x, best_row
        )
        nfes += n_count

        # Population-level selection twist (egsk_optimize.m:216-226), as written.
        if float(np.sum(fitness)) < float(np.sum(children_fitness)):
            child_better = children_fitness < fitness          # ties keep the parent
            pop[child_better, :] = trial[child_better, :]
            fitness = np.minimum(fitness, children_fitness)
        else:
            parent_better = fitness < children_fitness          # ties keep the child
            # In-place complement of the former copy-then-restore: rows where
            # parent_better keep pop, all other rows take trial -- identical
            # selected values, one full NP*D copy removed.
            pop[~parent_better, :] = trial[~parent_better, :]
            fitness = np.minimum(children_fitness, fitness)

        # Late stage: adapt KF1/KF2 and optionally run the IP refinement.
        if generation >= _LATE_STAGE_FRAC * g_max:
            kf1 = _clamp_kf(_triangular_membership(fitness, fitness[rg1], fitness[rg3], fitness[rg2]))
            a2 = float(fitness[int(np.min(r1))])    # reference quirk: min over the INDEX vector
            b2 = float(fitness[int(np.min(r2))])
            c2 = float(fitness[int(np.min(r3))])
            kf2 = _clamp_kf(_triangular_membership(fitness, a2, b2, c2))

            if (not has_optimum) or (best_fitness > float(problem.optimum) + val_2_reach):
                if float(np.std([a2, b2, c2])) * 1e-2 <= 1.0:
                    best_x, best_fitness, nfes = _egsk_ip_refine(best_x, best_fitness, nfes, problem, max_nfes)
                    pop[best_row, :] = best_x
                    fitness[best_row] = best_fitness

        conv_nfes.append(int(nfes))
        conv_best.append(float(best_fitness))

    if np.isnan(problem.optimum):
        error = float("nan")
    else:
        error = float(best_fitness - float(problem.optimum))
        if not np.isnan(problem.target_error) and error < float(problem.target_error):
            error = 0.0

    return OptimizerResult(
        optimizer="egsk",
        suite=problem.suite,
        func_id=int(problem.func_id),
        dim=dim,
        seed=seed,
        best_x=best_x,
        best_fitness=float(best_fitness),
        error=float(error),
        nfes=int(nfes),
        termination="max_evaluations",   # the reference never stops early
        convergence=ConvergenceTrace(
            nfes=np.asarray(conv_nfes, dtype=np.int64),
            best_fitness=np.asarray(conv_best, dtype=np.float64),
        ),
        runtime_seconds=float(time.perf_counter() - start),
        params={
            "np": pop_size,
            "kf1_init": float(_option_value(options, "kf1", _KF_INIT)),
            "kf2_init": float(_option_value(options, "kf2", _KF_INIT)),
            "kr": kr,
            "k": k_rate,
            "senior_p": _SENIOR_P,
            "late_stage_trigger": _LATE_STAGE_FRAC,
            "ip_fe": int(np.ceil(_IP_FE_FRAC * max_nfes)),
            "ip_solver": "scipy-SLSQP",
            "generations": generation,
        },
        notes="IP refinement uses scipy SLSQP as the fmincon-SQP substitute (statistical-equivalence port).",
    )
