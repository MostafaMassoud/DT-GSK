"""DECC-G: cooperative coevolution with random grouping and adaptive weighting.

Reference
---------
Yang, Z., Tang, K., & Yao, X. (2008). *Large scale evolutionary optimization using
cooperative coevolution*. Information Sciences 178(15), 2985-2999.
https://doi.org/10.1016/j.ins.2008.02.017

PROVENANCE AND FIDELITY
-----------------------
Written for this project against the paper. A third-party reference implementation
(github "decc" by Moesio Filho, MIT, 2023) was consulted as a cross-check, but is
NOT the basis of this port: its own README states the implementations "might
slightly differ from the original papers", and a line-level read found one
structural deviation that matters here -- it runs the weighting step ONCE after the
main loop terminates, whereas Algorithm 2 of the paper applies weighting at the end
of EVERY cycle. Weighting is the paper's central contribution (it is what makes the
"-G" variant differ from plain DECC), so that deviation is not cosmetic. This
implementation follows the paper.

Algorithm (paper, Section 3):
  1. Randomly permute the n decision variables into m subcomponents of size s.
  2. Optimise each subcomponent in turn with SaNSDE for a fixed FE allowance,
     evaluating through the shared context vector (the current best individual).
  3. Apply adaptive weighting: co-adapt one weight per subcomponent with DE for
     the best, worst and a random individual.
  4. Repeat from 1 until the budget is exhausted (a NEW random grouping each cycle
     -- this is what gives interacting variables a chance to land together).

BUDGET DISCIPLINE
-----------------
Every evaluation goes through ``_base.BudgetEvaluator``, which is hard-capped at
``problem.max_nfes``. Each phase truncates to ``ev.remaining()`` before evaluating,
so the run stops exactly at the budget rather than overshooting -- matching the
family's budget-exact contract and the CEC2013LSGO protocol.

Not part of the seven-method GSK-family panel. Unlike MOS and SHADE-ILS this module
is **not vendored**: it is first-party code written from the source paper, with no
author-code oracle to check it against (see docs/development/DECC_G_port_record.md,
which records the five bring-up defects found and fixed by reading the paper). It
exists so the large-scale comparison can be run first-party under identical
conditions. Corrected 2026-07-28: this docstring previously said "vendored alongside
MOS and SHADE-ILS", contradicting the port record.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from gsk_family.types import OptimizerOptions, OptimizerResult

from . import _base

# Paper defaults (Section 4.1): population 100, subcomponent size 100 -> m = n/s.
_DEFAULT_NP = 100
_DEFAULT_GROUP_SIZE = 100
#: Number of cycles (paper Section 5.1: "the number of cycles in DECC-G to be 50").
#: The per-subcomponent FE allowance is DERIVED from this and the total budget
#: rather than fixed, because the cycle count is what the paper actually pins --
#: it is the N in Theorem 1's regrouping-probability analysis. Fixing the
#: allowance instead (an earlier revision used 500) silently produced ~476 cycles
#: at a 3e6 budget, i.e. ten times the paper's regrouping rate and a tenth of its
#: search depth per subcomponent.
_DEFAULT_CYCLES = 50
#: Weight-vector search bounds and DE control parameters (paper Section 3.3).
_WEIGHT_LO, _WEIGHT_HI = -5.0, 5.0
_WEIGHT_NP = 15
_WEIGHT_FES = 100
_WEIGHT_F = 0.5
_WEIGHT_CR = 0.9


def _random_groups(dim: int, group_size: int, rng: Any) -> list[np.ndarray]:
    """Randomly permute ``dim`` indices into contiguous groups of ``group_size``.

    Re-drawn every cycle: random grouping is the mechanism by which interacting
    variables are eventually placed in the same subcomponent (paper Section 3.1).
    """
    perm = np.asarray(rng.permutation(dim), dtype=np.int64)
    n_groups = max(1, int(np.ceil(dim / group_size)))
    if n_groups == 1:
        # DEGENERATE: one subcomponent holds every variable, so the per-cycle
        # re-permutation changes nothing and the co-adaptation weight vector has
        # length 1. What runs is SaNSDE on the full vector with a scalar rescale
        # -- not DECC-G. This fires whenever dim <= group_size (note: dim == 100
        # with the default group_size 100 is degenerate too, not just dim < 100).
        # Raised rather than warned because the result would carry the DECC-G
        # label while being a different algorithm; see production_deviation_record
        # D-8.x and decision_log D-0025.
        raise ValueError(
            f"DECC-G random grouping is degenerate at dim={dim} with "
            f"group_size={group_size}: it yields a single subcomponent, so "
            f"regrouping is a no-op and the run is SaNSDE with adaptive "
            f"weighting, not DECC-G. DECC-G is meaningful only when "
            f"dim > group_size (this project runs it on CEC2013LSGO at "
            f"D=905/1000, giving 10 subcomponents). Pass a smaller "
            f"optimizer_options.group_size if a decomposed run at this "
            f"dimension is genuinely intended."
        )
    return [g for g in np.array_split(perm, n_groups) if g.size > 0]


def _sansde(
    sub_pop: np.ndarray,
    sub_fit: np.ndarray,
    evaluate_sub: Any,
    rng: Any,
    lo: np.ndarray,
    hi: np.ndarray,
    max_fes: int,
    state: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, int]:
    """SaNSDE on one subcomponent; returns (population, fitness, FEs used).

    Self-adaptive NSDE (Yang, Tang & Yao 2008b), the sub-optimiser DECC-G uses:
    two mutation strategies selected by an adapting probability ``p``, F drawn
    per-individual from either N(0.5, 0.3) or a Cauchy, and CR self-adapted from a
    running mean of successful values. ``state`` carries the adaptation across
    cycles for this subcomponent index, as the paper's learning period requires.
    """
    np_size, sub_dim = sub_pop.shape
    used = 0
    p = state.setdefault("p", 0.5)
    crm = state.setdefault("crm", 0.5)
    cr_success: list[float] = state.setdefault("cr_success", [])
    ns1 = nf1 = ns2 = nf2 = 0

    # CR ~ N(CRm, 0.1), per SaDE's scheme adopted by SaNSDE (paper Section 4.1.3).
    cr = np.clip(crm + 0.1 * _base.standard_normal(rng, np_size), 0.0, 1.0)

    while used < max_fes:
        batch = min(np_size, max_fes - used)
        if batch <= 0:
            break

        # --- NSDE mutation, paper Eq. (7) ---------------------------------
        # ONE mutation structure -- DE/rand/1 with base x_r1 and differential
        # d = x_r2 - x_r3 -- and TWO ways of drawing the scaling factor:
        #     v_i = x_r1 + d * N(0.5, 0.5)   with probability p
        #     v_i = x_r1 + d * Cauchy(0, 1)  otherwise
        # SaNSDE adapts p (the Gaussian/Cauchy balance) from observed success.
        # NOTE: an earlier revision of this file used two *different* strategies
        # (rand/1 vs current-to-best/1), which is SaDE's structure, not SaNSDE's.
        idx = np.empty((np_size, 3), dtype=np.int64)
        for i in range(np_size):
            choices = rng.permutation(np_size)
            idx[i] = [c for c in choices if c != i][:3]
        d = sub_pop[idx[:, 1]] - sub_pop[idx[:, 2]]
        use1 = np.asarray(rng.random(np_size)) < p
        f_gauss = 0.5 + 0.5 * _base.standard_normal(rng, np_size)
        f_cauchy = np.tan(np.pi * (np.asarray(rng.random(np_size)) - 0.5))
        f = np.where(use1, f_gauss, f_cauchy)[:, None]
        donor = sub_pop[idx[:, 0]] + f * d

        # --- binomial crossover ---
        mask = np.asarray(rng.random((np_size, sub_dim))) < cr[:, None]
        jrand = np.asarray(rng.integers(0, sub_dim, size=np_size), dtype=np.int64)
        mask[np.arange(np_size), jrand] = True
        trial = np.where(mask, donor, sub_pop)
        np.clip(trial, lo, hi, out=trial)

        trial_fit = evaluate_sub(trial[:batch])
        used += batch

        improved = trial_fit < sub_fit[:batch]
        for i in np.nonzero(improved)[0]:
            cr_success.append(float(cr[i]))
            if use1[i]:
                ns1 += 1
            else:
                ns2 += 1
        for i in np.nonzero(~improved)[0]:
            if use1[i]:
                nf1 += 1
            else:
                nf2 += 1
        sub_pop[:batch][improved] = trial[:batch][improved]
        sub_fit[:batch][improved] = trial_fit[improved]

        # --- self-adaptation of p and crm (paper Eq. 8-10) ---
        denom1 = ns1 * (ns2 + nf2)
        denom2 = ns2 * (ns1 + nf1) + denom1
        if denom2 > 0:
            p = float(np.clip(denom1 / denom2, 0.05, 0.95))
        if cr_success:
            crm = float(np.clip(np.mean(cr_success), 0.0, 1.0))
            cr_success.clear()
        cr = np.clip(crm + 0.1 * _base.standard_normal(rng, np_size), 0.0, 1.0)

    state["p"], state["crm"] = p, crm
    return sub_pop, sub_fit, used


def _weight_step(
    individual: np.ndarray,
    groups: list[np.ndarray],
    ev: Any,
    rng: Any,
    lb: np.ndarray,
    ub: np.ndarray,
) -> tuple[np.ndarray, float, int] | None:
    """Co-adapt one weight per subcomponent for a single individual (Section 3.3).

    The weight vector has one entry per subcomponent, so this is an m-dimensional
    DE search regardless of the problem's dimensionality -- the mechanism that lets
    DECC-G correct the scale of a whole subcomponent at once.
    Returns ``None`` when the budget cannot fund even the initial population.
    """
    m = len(groups)
    if ev.remaining() < _WEIGHT_NP:
        return None

    def apply(weights: np.ndarray) -> np.ndarray:
        """Scale each group of the individual by its weight, then clip to bounds."""
        out = np.repeat(individual[None, :], weights.shape[0], axis=0)
        for gi, g in enumerate(groups):
            out[:, g] *= weights[:, gi][:, None]
        return np.clip(out, lb, ub)

    w_pop = np.asarray(rng.random((_WEIGHT_NP, m))) * (_WEIGHT_HI - _WEIGHT_LO) + _WEIGHT_LO
    w_pop[0, :] = 1.0  # keep the unweighted individual in the pool
    w_fit = ev.evaluate(apply(w_pop))
    used = w_pop.shape[0]

    while used < _WEIGHT_FES and ev.remaining() > 0:
        batch = min(_WEIGHT_NP, _WEIGHT_FES - used, ev.remaining())
        if batch <= 0:
            break
        idx = np.empty((_WEIGHT_NP, 3), dtype=np.int64)
        for i in range(_WEIGHT_NP):
            choices = rng.permutation(_WEIGHT_NP)
            idx[i] = [c for c in choices if c != i][:3]
        donor = w_pop[idx[:, 0]] + _WEIGHT_F * (w_pop[idx[:, 1]] - w_pop[idx[:, 2]])
        mask = np.asarray(rng.random((_WEIGHT_NP, m))) < _WEIGHT_CR
        jrand = np.asarray(rng.integers(0, m, size=_WEIGHT_NP), dtype=np.int64)
        mask[np.arange(_WEIGHT_NP), jrand] = True
        trial = np.clip(np.where(mask, donor, w_pop), _WEIGHT_LO, _WEIGHT_HI)

        trial_fit = ev.evaluate(apply(trial[:batch]))
        used += batch
        better = trial_fit < w_fit[:batch]
        w_pop[:batch][better] = trial[:batch][better]
        w_fit[:batch][better] = trial_fit[better]

    best = int(np.argmin(w_fit))
    return apply(w_pop[best : best + 1])[0], float(w_fit[best]), used


def optimize(problem: Any, options: OptimizerOptions) -> OptimizerResult:
    """Run DECC-G on ``problem`` under this project's budget-exact harness."""
    rng, ev, start = _base.start_run(problem, options)
    recorder = _base.make_recorder(problem, options, counting_rule="every_evaluation")

    dim = int(problem.dim)
    np_size = int(_base.param(options, "np", _DEFAULT_NP))
    group_size = int(_base.param(options, "group_size", _DEFAULT_GROUP_SIZE))
    n_cycles = int(_base.param(options, "cycles", _DEFAULT_CYCLES))
    lb = np.asarray(problem.lb, dtype=np.float64)
    ub = np.asarray(problem.ub, dtype=np.float64)

    # Derive the per-subcomponent SaNSDE allowance from the pinned cycle count.
    # Each cycle spends, per subcomponent, np FEs re-baselining through the context
    # vector plus the SaNSDE allowance; plus three weighting searches per cycle.
    n_groups_est = max(1, int(np.ceil(dim / group_size)))
    per_cycle = max(1, int(problem.max_nfes) // max(1, n_cycles))
    weight_cost = 3 * (_WEIGHT_NP + _WEIGHT_FES)
    sansde_fes = int(_base.param(
        options, "sansde_fes",
        max(np_size, (per_cycle - weight_cost) // n_groups_est - np_size),
    ))

    pop = lb + (ub - lb) * np.asarray(rng.random((np_size, dim)))
    # BudgetEvaluator does NOT auto-truncate -- the algorithm owns budget control.
    # A budget smaller than the population is degenerate but must still not
    # overspend, so evaluate what the budget affords and park the rest at +inf
    # (never selected as best; the main loop then exits on remaining() == 0).
    n_init = min(np_size, ev.remaining())
    fitness = np.full(np_size, np.inf, dtype=np.float64)
    if n_init > 0:
        fitness[:n_init] = ev.evaluate(pop[:n_init])
    recorder.record_initial(pop, ev.best_fitness, ev.nfes)

    sansde_state: dict[int, dict[str, Any]] = {}
    cycle = 0
    while ev.remaining() > 0:
        cycle += 1
        groups = _random_groups(dim, group_size, rng)

        # ---- optimise each subcomponent through the shared context vector ----
        for gi, g in enumerate(groups):
            if ev.remaining() <= 0:
                break
            context = pop[int(np.argmin(fitness))].copy()

            def evaluate_sub(sub: np.ndarray, _g: np.ndarray = g) -> np.ndarray:
                """Evaluate subcomponent vectors substituted into the context vector."""
                full = np.repeat(context[None, :], sub.shape[0], axis=0)
                full[:, _g] = sub
                return ev.evaluate(full)

            # Baseline MUST be re-evaluated through the context vector. The
            # individuals' own full-vector fitnesses are not commensurable with
            # context-substituted trials, and using them makes SaNSDE's greedy
            # test meaningless and corrupts the fitness array.
            if ev.remaining() < np_size:
                break
            sub_pop = pop[:, g].copy()
            sub_fit = evaluate_sub(sub_pop)

            allow = min(sansde_fes, ev.remaining())
            if allow > 0:
                sub_pop, sub_fit, _used = _sansde(
                    sub_pop, sub_fit, evaluate_sub, rng,
                    lb[g], ub[g], allow, sansde_state.setdefault(gi, {}),
                )
            # Within this subcomponent the context is fixed, so every entry of
            # sub_fit is measured on the same footing: adopt them wholesale, which
            # is the standard cooperative-coevolution bookkeeping.
            pop[:, g] = sub_pop
            fitness = sub_fit

        recorder.record_generation(
            pop, best_fitness=ev.best_fitness, nfes=ev.nfes,
            generated=int(np_size), accepted_improved=0, fitness=fitness,
        )
        if ev.remaining() <= 0:
            break

        # ---- adaptive weighting, EVERY cycle: best, worst, random ----
        targets = [int(np.argmin(fitness)), int(np.argmax(fitness)),
                   int(rng.integers(0, np_size))]
        for t in targets:
            if ev.remaining() <= 0:
                break
            got = _weight_step(pop[t], groups, ev, rng, lb, ub)
            if got is None:
                break
            new_x, new_f, _ = got
            if new_f < fitness[t]:
                pop[t] = new_x
                fitness[t] = new_f

    return _base.build_result(
        optimizer_id="decc-g",
        problem=problem,
        options=options,
        ev=ev,
        start_time=start,
        params={
            "np": np_size, "group_size": group_size, "sansde_fes": sansde_fes,
            "weight_np": _WEIGHT_NP, "weight_fes": _WEIGHT_FES,
            "cycles_target": n_cycles, "cycles_run": cycle,
        },
        notes="DECC-G (Yang, Tang & Yao 2008); random grouping + per-cycle adaptive weighting",
        telemetry=recorder.finalize(),
    )
