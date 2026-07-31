"""SHADE-ILS — SHIPPED-CODE-ALIGNED port of Molina's shadeils (CEC/WCCI 2018, DOI 10.1109/CEC.2018.8477755).

ALIGNED 2026-07-25 to the author's shipped artifact
``reference_code/external_baseline_algorithms/shadeils-master/`` (shadeils.py + SHADE.py +
mts.py + DE.py), per ``docs/development/matlab_parity/shadeils_alignment_spec.md`` (22-delta
line-map, adversarially completeness-checked). This replaces the earlier deliberate PAPER
reconstruction (Cauchy F, forced jrand, 0.1·range SR, one-sided 0.1 restart, 2-phase loop) —
that variant is preserved in git history and its F15-reproduction property is documented in
the freeze record.

Shipped-iteration shape (3-phase, ihshadels, shadeils.py:289-386):
  [Global LS: evals_gs] -> [SHADE burst: evals_de] -> [Local LS: evals_ls]
with evals_gs/de/ls = min(50D,25000)/min(50D,25000)/min(10D,5000); restart after 3
consecutive whole-iteration improvements < threshold (default 0.05 = the artifact's
``ihshadels`` signature default; the shipped CLI default 0.01 is a documented ambiguity —
``restart_threshold`` is an explicit parameter here).

LS-POOL SEMANTICS — ``pool_mode`` parameter ('intent' default | 'quirk'):
The shipped ``PoolLast.update_prob`` contains ``np.argsort(dict.values())`` whose behavior is
python-era dependent: under the py2-era environment that produced the paper it picks the
LS with the LARGEST last improvement (ties -> 'grad'; the MATLAB oracle
``shadeils_core.m:291-302`` ports this INTENT), while under any modern py3 it degenerates to
always returning the first insertion-order key ('mts') after warm-up (the QUIRK — embodied by
both our author-python probe anchors and the independent IRRG re-run, arXiv:2206.04168).
'intent' (campaign default) matches the MATLAB oracle and the paper-era executions; 'quirk'
reproduces shipped-as-executed-today and is used to validate against the probe anchors.

Loose-vs-true accounting (oracle doctrine, spec C10): loop control uses the author's LOOSE
``totalevals`` ledger (center eval charged; init pop/second-center/post-Global re-eval/restart
disturbance uncharged; mts charged its nominal block; grad charged scipy funcalls; SHADE
charged numEvalFound = 24900 per full burst; restart charged 2*popsize). The TRUE 3e6-FE cap
is enforced solely by ``_base.BudgetEvaluator`` raising ``BudgetExhausted``, caught here at
the driver (MATLAB sentinel analog) — no per-phase truncation by remaining budget.

Engine note: the L-BFGS-B is scipy's (same engine as the shipped artifact — the fork is
irreducible only vs the MATLAB oracle's vendored C mex v3.0). Family RNG doctrine: threefry
streams, distribution-equivalent draws, no bit-matching with the shipped MT19937.
"""

# VENDORED from 05-Human-Inspired-Family_Python_v0.1
#   src/human_inspired_family/optimizers/external/shade_ils.py
#   source sha256: 9d983eff73f92fb6
# Imported 2026-07-25 to run MOS and SHADE-ILS natively on CEC2013LSGO under
# this project's harness, so the LSGO comparison is first-party rather than a
# published-table citation. ONLY the import namespace was rewritten; the
# algorithm bodies are byte-faithful to the source, which carries project 05's
# parity verdicts (shade-ils: FROZEN/user-signed 2026-07-24, author-code-faithful
# oracle, 14/15 within 2x of the published table; mos: 15/15 cells compared).
# Do not edit the algorithm bodies here -- amend at the source and re-vendor.

from __future__ import annotations

import warnings

import numpy as np
from scipy.optimize import fmin_l_bfgs_b

from gsk_family.types import OptimizerOptions, OptimizerResult

from . import _base

_COUNTING_RULE = (
    "GISR denominator = SHADE trial vectors generated per SHADE generation (= NP=100); "
    "numerator = trials with f(u) < f(x_i) (strict). Population-based DE replacement "
    "rate over the SHADE bursts; the single-point MTS-LS1 / L-BFGS-B intensifier phases "
    "advance nfes and best-so-far (captured in the convergence trace) but produce no "
    "population-generation records (memetic ILS)."
)


# ---------------------------------------------------------------------------
# PoolLast — shipped LS selector (shadeils.py:31-123) with dual update_prob
# ---------------------------------------------------------------------------
class _PoolLast:
    """Shipped ``PoolLast``: warm-up pair then a cached greedy pick.

    Warm-up: a shuffled copy of the options consumed from the END via ``pop()``
    (shadeils.py:44,66). Afterwards a CACHED pick ``self.new``, recomputed by
    ``improvement()`` only when the fed account is 0 or worse than the previous
    one for that option (shadeils.py:100-103). ``is_empty()`` is constant False
    in BOTH python eras (``np.all(dict_values == 0)`` never yields True), so the
    Global phase always runs — ported as always-run at the call site.
    """

    def __init__(self, rng, options: list[str], mode: str) -> None:
        """Arm the pool with a shuffled warm-up over ``options`` (shadeils.py:32-47)."""
        self.rng = rng
        self.mode = mode
        self.options = list(options)
        self.first = [self.options[int(j)] for j in rng.permutation(len(self.options))]
        self.new: str | None = None
        self.improvements: dict[str, float] = {o: 0.0 for o in self.options}

    def reset(self) -> None:
        """Re-arm a fresh shuffled warm-up pair (shadeils.py:49-54)."""
        self.first = [self.options[int(j)] for j in self.rng.permutation(len(self.options))]
        self.new = None
        self.improvements = {o: 0.0 for o in self.options}

    def get_new(self) -> str:
        """Warm-up pops from the END; then the cached pick (shadeils.py:59-71)."""
        if self.first:
            return self.first.pop()
        if self.new is None:
            self.new = self._update_prob()
        return self.new

    def improvement(self, obj: str, account: float) -> None:
        """Record an improvement ratio; maybe refresh the cached pick (shadeils.py:77-103)."""
        if account < 0:                      # unreachable on cec2013lsgo, ported anyway
            return
        previous = self.improvements[obj]
        self.improvements[obj] = account
        if self.first:
            return
        if not self.new:
            self.new = self._update_prob()
        elif account == 0 or account < previous:
            self.new = self._update_prob()

    def _update_prob(self) -> str:
        """Dual-mode pick — see the module docstring (spec C3 / D-1 + user decision).

        'quirk': py3-executed shipped behavior — ``np.argsort(dict.values())``
        degenerates to ``[0]`` so the first insertion-order key ('mts') is
        returned unconditionally (shadeils.py:120-123 as executed under py3).
        'intent': py2-era behavior = the MATLAB oracle (shadeils_core.m:291-302)
        — the option with the largest last improvement, ties -> 'grad'.
        All-zero improvements: the shipped py3 path is an ipdb crash branch
        (never exercised on this suite); uniform pick per the oracle :296-298.
        """
        vals = list(self.improvements.values())
        if all(v == 0 for v in vals):
            return self.options[int(self.rng.integers(0, len(self.options)))]
        if self.mode == "quirk":
            return self.options[0]
        best_val = max(vals)
        winners = [o for o in self.options if self.improvements[o] == best_val]
        return "grad" if "grad" in winners else winners[0]


def _ratio(previous: float, new: float) -> float:
    """Shipped ``get_ratio_improvement`` (shadeils.py:227-233): prev==0 -> 0."""
    if previous == 0:
        return 0.0
    return (previous - new) / previous


def _eval_batch_exact(ev, x: np.ndarray) -> np.ndarray:
    """Batch-evaluate with a budget-exact cap (MATLAB sentinel doctrine).

    ``BudgetEvaluator.evaluate`` counts the WHOLE batch and only refuses when
    already exhausted, so an uncapped 100-row generation near the cap would
    overrun the true budget. Here: if the batch no longer fits, consume exactly
    the remaining evaluations (ev still tracks any better best in the partial
    batch) and unwind via ``BudgetExhausted`` — nfes lands exactly on max_nfes.
    """
    rem = ev.remaining()
    if x.shape[0] > rem:
        if rem > 0:
            ev.evaluate(x[:rem])
        raise _base.BudgetExhausted("true FE cap reached mid-batch")
    return ev.evaluate(x)


# ---------------------------------------------------------------------------
# MTS-LS1 — shipped two-phase mtsls (mts.py:16-103), SR mutated in place
# ---------------------------------------------------------------------------
def _mtsls(ev, rng, lb, ub, sol, fitness, maxevals, sr):
    """Shipped mtsls: unconditional first sweep + improvement-sorted second phase.

    ``sr`` is halved IN PLACE on every failed dimension; final underflow reset
    ``sr[sr < 1e-15] = 0.2*(ub-lb)`` (mts.py:99-101). ``maxevals`` is the LOOSE
    nominal block — the first sweep ignores it entirely (mts.py:61-77); the true
    3e6 cap unwinds via ``BudgetExhausted`` from the evaluator.

    The per-dimension probe (shipped improve_dim, mts.py:16-37: -SR; on strict
    worsening +0.5*SR; tie = 1 eval) is inlined on a pair of per-call buffers
    ``cur``/``work`` that are equal except while coordinate ``i`` is being
    probed, replacing the shipped per-probe full-D copy+``np.clip`` with a
    scalar clamp of that coordinate. Bit-identical because every ``sol``
    reaching this function is in-bounds on every coordinate (init/restart rows,
    shade_clip trials, and grad/restart outputs are all constructed or clipped
    into [lb, ub]), so the shipped full-D clip only ever moved coordinate ``i``.
    PRECONDITION inherited from that invariant: a user-supplied
    ``initial_population`` must be in-bounds (the fair-start runner guarantees
    this).
    """
    dim = sol.shape[0]
    cur, cur_f = sol, fitness
    work = sol.copy()                        # differs from cur at most at coord i
    evaluate_one = ev.evaluate_one
    total = 0
    improvement = np.zeros(dim)

    if total < maxevals:
        for i in rng.permutation(dim).tolist():   # same draw, Python ints
            sr_i = sr[i]
            v = cur[i] - sr_i                # arm 1: -SR
            if v < lb[i]:
                v = lb[i]
            elif v > ub[i]:
                v = ub[i]
            work[i] = v
            f1 = evaluate_one(work)
            total += 1
            if f1 < cur_f:
                nf = f1
            elif f1 > cur_f:                 # exact tie: no accept, no second probe
                v = cur[i] + 0.5 * sr_i      # arm 2 restarts from cur (shipped re-copy)
                if v < lb[i]:
                    v = lb[i]
                elif v > ub[i]:
                    v = ub[i]
                work[i] = v
                f2 = evaluate_one(work)
                total += 1
                nf = f2 if f2 < cur_f else cur_f
            else:
                nf = cur_f
            gain = max(cur_f - nf, 0.0)
            improvement[i] = gain
            if gain > 0:
                cur, work = work, cur        # accept: swap buffers
                cur_f = nf
                work[i] = cur[i]             # resync the probed coordinate
            else:
                work[i] = cur[i]             # reject: undo the probe write
                sr[i] /= 2.0

        dim_sorted = np.argsort(improvement)[::-1]
        d = 0

    while total < maxevals:
        i = int(dim_sorted[d])
        sr_i = sr[i]
        v = cur[i] - sr_i                    # arm 1: -SR
        if v < lb[i]:
            v = lb[i]
        elif v > ub[i]:
            v = ub[i]
        work[i] = v
        f1 = evaluate_one(work)
        total += 1
        if f1 < cur_f:
            nf = f1
        elif f1 > cur_f:                     # exact tie: no accept, no second probe
            v = cur[i] + 0.5 * sr_i          # arm 2 restarts from cur (shipped re-copy)
            if v < lb[i]:
                v = lb[i]
            elif v > ub[i]:
                v = ub[i]
            work[i] = v
            f2 = evaluate_one(work)
            total += 1
            nf = f2 if f2 < cur_f else cur_f
        else:
            nf = cur_f
        gain = max(cur_f - nf, 0.0)
        improvement[i] = gain
        next_d = (d + 1) % dim
        next_i = int(dim_sorted[next_d])
        if gain > 0:
            cur, work = work, cur            # accept: swap buffers
            cur_f = nf
            work[i] = cur[i]                 # resync the probed coordinate
            if improvement[i] < improvement[next_i]:
                dim_sorted = np.argsort(improvement)[::-1]
        else:
            work[i] = cur[i]                 # reject: undo the probe write
            sr[i] /= 2.0
            d = next_d

    mask = sr < 1e-15
    sr[mask] = 0.2 * (ub - lb)[mask]
    return cur, cur_f


# ---------------------------------------------------------------------------
# SHADE burst — shipped SHADE.improve (SHADE.py:17-223)
# ---------------------------------------------------------------------------
def _shade_burst(pop, popfit, mem_f, mem_cr, H, ev, rng, lb, ub, recorder,
                 cbest_x, evals_de):
    """One SHADE burst on the persistent population; returns (best_x, best_f, loose_charge).

    Shipped semantics (spec A1-A11): unclipped Normal F and CR; strict-< crossover
    mask with NO forced jrand; per-individual p~U(2/N,0.2) with floor(p*N) heads;
    donor 'memory' rebuilt from the population each burst, appended with the CHILD
    on strict improvement (same-generation appends never donate), capped at 2N by
    random permutation; slot pointer k resets to 0 EVERY burst (A6) while MemF/MemCR
    persist; ``pop[0] = current_best`` with STALE fitness (A9 quirk B); replacement
    on <=, recording on <; loose charge = numEvalFound = 24900 for a full burst (A8).

    Hot-path arrays (gathers, mutation temporaries, trial vectors, donor memory)
    live in per-burst preallocated buffers written with ``out=``/``copyto`` in
    the exact per-element operation order of the original expressions, and the
    shade_clip repair only touches the violating entries — bit-identical, no
    per-generation allocation. The donor memory is a capacity buffer of exactly
    3N rows (2N cap + at most N appends per generation) with tracked length
    ``mlen``; ``mlen`` feeds the r2 draw and the trim exactly where
    ``memory.shape[0]`` did.
    """
    N, D = pop.shape
    pmin = 2.0 / N
    span = 0.2 - pmin                         # loop-invariant (same operands every gen)
    pop[0] = cbest_x                          # stale slot-0 fitness (SHADE.py:63-64)
    mem_buf = np.empty((3 * N, D))            # donor memory capacity buffer
    mem_alt = np.empty((3 * N, D))            # trim target (swapped, never overlapping)
    mem_buf[:N] = pop                         # donor memory = pop copy (SHADE.py:73)
    mlen = N
    mem_cap = 2 * N
    k = 0                                     # per-burst slot pointer (SHADE.py:84, A6)
    current_eval = 0
    num_eval_found = 0
    idx = np.arange(N)
    g1 = np.empty((N, D))                     # pop[pbest] gather / mutation accumulator
    g2 = np.empty((N, D))                     # pop[r1] gather / difference accumulator
    g3 = np.empty((N, D))                     # memory[r2] gather
    v = np.empty((N, D))                      # mutant
    u = np.empty((N, D))                      # trial
    cross = np.empty((N, D), dtype=bool)
    rng_random = rng.random
    rng_integers = rng.integers
    normal = _base.normal
    asarray = np.asarray

    while current_eval < evals_de:
        num_eval_found = current_eval         # SHADE.py:93-94 (reset every generation)
        m = mlen

        r_idx = asarray(rng_integers(0, H, N), dtype=np.int64)
        f = asarray(normal(rng, 0.0, 1.0, N)) * 0.1 + mem_f[r_idx]   # unclipped (A1)
        cr = asarray(normal(rng, 0.0, 1.0, N)) * 0.1 + mem_cr[r_idx]  # unclipped (A2)
        p = pmin + asarray(rng_random(N), dtype=np.float64) * span
        maxbest = (p * N).astype(np.int64)    # floor; p >= 2/N guarantees >= 2 (A4)

        order = np.argsort(popfit)
        sel = np.minimum((asarray(rng_random(N)) * maxbest).astype(np.int64), maxbest - 1)
        pbest = order[sel]

        r1 = asarray(rng_integers(0, N - 1, N), dtype=np.int64)
        r1[r1 >= idx] += 1                    # uniform over pop \ {i}
        # r2: uniform over memory positions excluding {i, r1} POSITIONALLY (A5)
        lo = np.minimum(idx, r1)
        hi = np.maximum(idx, r1)
        r2 = asarray(rng_integers(0, m - 2, N), dtype=np.int64)
        r2 += (r2 >= lo)
        r2 += (r2 >= hi)

        # v = base + f[:,None]*(pop[pbest] - base) + f[:,None]*(pop[r1] - memory[r2]),
        # decomposed into the identical left-to-right temporaries with out= buffers.
        base = pop
        fN = f[:, None]
        np.take(pop, pbest, axis=0, out=g1)
        np.take(pop, r1, axis=0, out=g2)
        np.take(mem_buf, r2, axis=0, out=g3)  # r2 < mlen always
        np.subtract(g1, base, out=g1)
        np.multiply(fN, g1, out=g1)
        np.add(base, g1, out=g1)
        np.subtract(g2, g3, out=g2)
        np.multiply(fN, g2, out=g2)
        np.add(g1, g2, out=v)

        # shade_clip (SHADE.py:211-223): same (base+bound)/2 scalar ops at the
        # violating entries only; the ub mask MUST be formed after the lb writes
        # (the original second where read the lb-fixed v).
        mask = v < lb
        if mask.any():
            bad = np.nonzero(mask)
            v[bad] = (base[bad] + lb[bad[1]]) / 2.0
        mask = v > ub
        if mask.any():
            bad = np.nonzero(mask)
            v[bad] = (base[bad] + ub[bad[1]]) / 2.0

        u_rand = asarray(rng_random((N, D)), dtype=np.float64)
        np.less(u_rand, cr[:, None], out=cross)   # strict <, no jrand (A3)
        np.copyto(u, base)
        np.copyto(u, v, where=cross)          # == np.where(cross, v, base)

        u_fit = _eval_batch_exact(ev, u)
        survive = u_fit <= popfit
        improved = u_fit < popfit
        n_improved = int(np.count_nonzero(improved))

        recorder.record_generation(
            pop, best_fitness=ev.best_fitness, nfes=ev.nfes, generated=int(N),
            accepted_improved=n_improved, fitness=popfit,
        )

        if n_improved:
            s_f = f[improved]
            s_cr = cr[improved]
            w = (popfit[improved] - u_fit[improved])
            total = float(w.sum())            # strict improvements => total > 0
            w = w / total
            f_new = float(np.clip(np.sum(w * s_f * s_f) / np.sum(w * s_f), 0.0, 1.0))
            cr_new = float(np.clip(np.sum(w * s_cr), 0.0, 1.0))
            mem_f[k] = f_new
            mem_cr[k] = cr_new
            k = (k + 1) % H
            # memory: append the CHILD values of strict improvers (A5)
            mem_buf[mlen:mlen + n_improved] = u[improved]
            mlen += n_improved

        pop[survive] = u[survive]
        popfit[survive] = u_fit[survive]

        if mlen > mem_cap:                    # limit_memory (SHADE.py:184-194)
            keep = asarray(rng.permutation(mlen), dtype=np.int64)[:mem_cap]
            np.take(mem_buf, keep, axis=0, out=mem_alt[:mem_cap])
            mem_buf, mem_alt = mem_alt, mem_buf
            mlen = mem_cap

        current_eval += N

    b = int(np.argmin(popfit))
    return pop[b].copy(), float(popfit[b]), num_eval_found


# ---------------------------------------------------------------------------
# apply_localsearch — shipped acceptance + loose charging (shadeils.py:139-168)
# ---------------------------------------------------------------------------
def _apply_ls(method, is_global, ev, rng, lb, ub, x, fx, maxevals, sr_state, bounds):
    """Run one LS block; accept iff fit <= current; return (x, f, loose_charge).

    'mts' charges the NOMINAL block (funcalls = maxevals, shadeils.py:160) and,
    per the shipped aliasing, a Global call mutates SR_global in place and then
    REBINDS SR_local to that same array (shadeils.py:157); a Local call mutates
    only SR_local. 'grad' = scipy fmin_l_bfgs_b with shipped options
    (approx_grad=1, maxfun=maxevals, everything else default; spec 1.3), charged
    its true funcalls; runs to scipy's own termination — only the true 3e6 cap
    (BudgetExhausted) unwinds it early. ``bounds`` is the scipy bounds list
    built once per run in :func:`optimize` (lb/ub never change; scipy does not
    mutate the list).
    """
    if method == "grad":
        # SCIPY-VERSION GUARD (engine-level, documented deviation). scipy's L-BFGS-B
        # Fortran core (`setulb`) can hand back an iterate a few ULPs outside the box;
        # modern scipy's ScalarFunction then aborts the whole call from inside the
        # optimization loop with ValueError("`x0` violates bound constraints") — verified
        # here with every x0 we pass strictly in-bounds and finite. The shipped artifact
        # ran on a scipy without that validation, so it simply continued. We cannot
        # reproduce "continue", so we end the LS block at the best point it had reached
        # (the pre-alignment port used the same unwind-and-keep-best strategy) and charge
        # the objective calls actually made. Without this, whole runs abort: 6/375 F8
        # runs died in the 2026-07-25 campaign. Triggers only on this roundoff edge.
        ncalls = 0
        best_f = fx
        best_x = x.copy()

        def _obj(z):
            """Objective wrapper: counts calls and tracks the best point seen."""
            nonlocal ncalls, best_f, best_x
            ncalls += 1
            fz = ev.evaluate_one(z)
            if fz < best_f:
                best_f = fz
                best_x = np.asarray(z, dtype=np.float64).copy()
            return fz

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            try:
                sol, fit, info = fmin_l_bfgs_b(
                    _obj, x0=np.clip(x, lb, ub), approx_grad=1,
                    bounds=bounds, maxfun=maxevals, disp=False,
                )
                funcalls = int(info["funcalls"])
                sol = np.clip(np.asarray(sol, dtype=np.float64), lb, ub)
            except ValueError:                     # scipy bound-validation abort
                sol, fit = np.clip(best_x, lb, ub), best_f
                funcalls = ncalls
    else:                                     # 'mts'
        sr = sr_state["global"] if is_global else sr_state["local"]
        sol, fit = _mtsls(ev, rng, lb, ub, x.copy(), fx, maxevals, sr)
        sr_state["local"] = sr                # shipped rebinding (shadeils.py:157)
        funcalls = maxevals
    if fit <= fx:                             # ties accept the new point
        return sol, float(fit), funcalls
    return x, fx, funcalls


def optimize(problem, options: OptimizerOptions) -> OptimizerResult:
    """Run shipped-code-aligned SHADE-ILS under the family contract."""
    rng, ev, start = _base.start_run(problem, options)
    D = int(problem.dim)
    lb = np.asarray(problem.lb, dtype=np.float64).reshape(-1)
    ub = np.asarray(problem.ub, dtype=np.float64).reshape(-1)
    grad_bounds = list(zip(lb.tolist(), ub.tolist()))  # scipy bounds: run-invariant
    max_nfes = int(problem.max_nfes)

    N = min(int(_base.param(options, "popsize", 100)), 100)      # shadeils.py:253
    H = int(_base.param(options, "H", min(N, 100)))              # main(): min(popsize,100)
    threshold = float(_base.param(options, "restart_threshold", 0.05))  # D-2 (CLI 0.01 ambiguity documented)
    pool_mode = str(_base.param(options, "pool_mode", "intent"))  # 'intent' | 'quirk' (see docstring)
    evals_gs = int(_base.param(options, "evals_gs", min(50 * D, 25000)))
    evals_de = int(_base.param(options, "evals_de", min(50 * D, 25000)))
    evals_ls = int(_base.param(options, "evals_ls", min(10 * D, 5000)))
    if pool_mode not in ("intent", "quirk"):
        raise ValueError(f"pool_mode must be 'intent' or 'quirk', got {pool_mode!r}")

    recorder = _base.make_recorder(problem, options, _COUNTING_RULE)

    mem_f = np.full(H, 0.5)
    mem_cr = np.full(H, 0.5)
    sr_state = {"global": 0.2 * (ub - lb), "local": None}
    sr_state["local"] = sr_state["global"]                        # reset_ls aliasing

    pool_global = _PoolLast(rng, ["mts", "grad"], pool_mode)
    pool = _PoolLast(rng, ["mts", "grad"], pool_mode)

    best_x = None
    best_f = np.inf
    totalevals = 0

    try:
        # ---- init (spec C2; shadeils.py:244-266) --------------------------
        center = (lb + ub) / 2.0
        ev.evaluate_one(center)               # first center eval — value unused by shipped flow
        totalevals = 1                                            # charged
        if options.initial_population is not None:                # fair-start doctrine
            pop = np.asarray(options.initial_population, dtype=np.float64).reshape(-1, D)[:N].copy()
        else:
            pop = lb + np.asarray(rng.random((N, D)), dtype=np.float64) * (ub - lb)
        popfit = _eval_batch_exact(ev, pop)                       # uncharged (loose)
        recorder.record_initial(pop, ev.best_fitness, ev.nfes)
        best_id = int(np.argmin(popfit))                          # FROZEN forever (A9 quirk A)
        center_f2 = ev.evaluate_one(center)                       # second center eval, uncharged
        if center_f2 < popfit[best_id]:
            pop[best_id] = center
            popfit[best_id] = center_f2
        cbest_x = pop[best_id].copy()
        cbest_f = float(popfit[best_id])
        best_x = cbest_x.copy()
        best_f = cbest_f
        num_worse = 0

        while totalevals < max_nfes:
            # ---- [A/B] Global LS (always runs: shipped is_empty() is constant False) ----
            previous_fitness = cbest_f
            method_global = pool_global.get_new()
            cbest_x, cbest_f, charge = _apply_ls(
                method_global, True, ev, rng, lb, ub, cbest_x, cbest_f, evals_gs,
                sr_state, grad_bounds)
            totalevals += charge
            pool_global.improvement(method_global, _ratio(previous_fitness, cbest_f))
            if cbest_f < best_f:
                best_x = cbest_x.copy()
                best_f = ev.evaluate_one(best_x)                  # re-eval, uncharged (C6)

            # ---- [E] region + local pool pick ----------------------------
            sr_state["local"] = sr_state["global"].copy()         # set_region_ls
            method = pool.get_new()

            # ---- [F] SHADE burst ------------------------------------------
            if cbest_f < popfit[best_id]:                         # conditional injection (A9 quirk A)
                pop[best_id] = cbest_x
                popfit[best_id] = cbest_f
            cbest_x, cbest_f, found = _shade_burst(
                pop, popfit, mem_f, mem_cr, H, ev, rng, lb, ub, recorder, cbest_x, evals_de)
            totalevals += found

            # ---- [G] Local LS ---------------------------------------------
            before_ls = cbest_f
            cbest_x, cbest_f, charge = _apply_ls(
                method, False, ev, rng, lb, ub, cbest_x, cbest_f, evals_ls,
                sr_state, grad_bounds)
            totalevals += charge
            pool.improvement(method, _ratio(before_ls, cbest_f))

            # ---- [H] global best (assignment only) ------------------------
            if cbest_f < best_f:
                best_f = cbest_f
                best_x = cbest_x.copy()

            # ---- [I] stagnation test (whole-iteration span, C7) ------------
            if previous_fitness == 0:
                ratio_improvement = 1.0
            else:
                ratio_improvement = (previous_fitness - cbest_f) / previous_fitness
            if ratio_improvement >= threshold:
                num_worse = 0
            else:
                num_worse += 1
                if method == "mts":                               # reset_ls(method) per increment
                    sr_state["global"] = 0.2 * (ub - lb)
                    sr_state["local"] = sr_state["global"]

            # ---- [J] restart (shadeils.py:357-379) -------------------------
            if num_worse >= 3:
                num_worse = 0
                posi = int(rng.integers(0, N))
                disturb = (np.asarray(rng.random(D), dtype=np.float64) * 0.02 - 0.01) * (ub - lb)
                new_x = np.clip(pop[posi] + disturb, lb, ub)      # two-sided ±1% (C8)
                new_f = ev.evaluate_one(new_x)                    # uncharged
                cbest_x, cbest_f = new_x, float(new_f)
                pop = lb + np.asarray(rng.random((N, D)), dtype=np.float64) * (ub - lb)
                popfit = _eval_batch_exact(ev, pop)               # 100 true FEs
                mem_f = np.full(H, 0.5)
                mem_cr = np.full(H, 0.5)
                totalevals += 2 * N                               # shipped duplicated charge (C9)
                pool_global.reset()
                pool.reset()
                sr_state["global"] = 0.2 * (ub - lb)              # reset_ls('all')
                sr_state["local"] = sr_state["global"]
                # best_id stays FROZEN (shipped never recomputes it)

            if totalevals >= max_nfes:
                break
    except _base.BudgetExhausted:
        pass                                                      # true 3e6 cap unwind (C10)

    return _base.build_result(
        "shade-ils", problem, options, ev, start_time=start,
        params={"profile": _base.resolve_profile(options), "popsize": N, "H": H,
                "restart_threshold": threshold, "pool_mode": pool_mode,
                "evals_gs": evals_gs, "evals_de": evals_de, "evals_ls": evals_ls},
        notes=("SHADE-ILS shipped-code-aligned (Molina shadeils-master); "
               f"pool_mode={pool_mode}; paper=Molina,LaTorre,Herrera 2018."),
        telemetry=recorder.finalize(),
    )
