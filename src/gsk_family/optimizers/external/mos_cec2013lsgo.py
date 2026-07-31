"""MOS (CEC2013-LSGO winner) — source-faithful, LaTorre, Muelas & Peña 2013 (CEC).

The **CEC2013-LSGO competition winner**: an HRH Multiple-Offspring-Sampling hybrid of THREE
techniques on one shared population under the MOS participation/quality/allocation loop —
the CEC2013-LSGO-competition-winning MOS instantiation. Ported **code-first** from the reference
GAEDA C++ (github.com/arthurmrodriguez/Advanced-Metaheuristics-LSGO, MOS_CEC2013:
``cec2013.cfg`` / ``techs_cec2013.cfg`` + ``GARealOps.cc`` / ``solis.cc`` /
``ImprovPerDimManager.cc``) resolved against the paper (E-1460).

PARAMETER AUTHORITY (adjudicated 2026-07-24 vs the STAGED winner tree, SHA 3208074): the
``# mts-…``/``# sw-…`` lines in ``cec2013.cfg`` are COMMENTS — boost ``parse_config_file``
(GAEDAConfig.cc:469) never reads them — so the winner ran on the ``default_value`` constants
in **GAEDAConfig.cc:326-354**, which are the values below. Do not "fix" them back from the
cfg comments.

Techniques (``use-tech`` order = HRH relay GA → Solis-Wets → MTS-LS1-Reduced), on a shared
population of **400**:
  • **GA** (``GA_t1``): tournament-2 selection, **BLX-α** crossover (α=0.5, ``pcx=0.9``),
    **Gaussian mutation** (``pmut=0.01``; ~``pmut·D`` genes, each perturbed by
    ``N(0,1)·(ub−lb)`` with bound rejection); survivor selection = **PopElitism μ+λ**
    (population ∪ children, keep best N — PopElitism.cc:15-29; applied to fractional
    chunks too).
  • **Solis-Wets** (``LS_t1``): ``dif~N(0,δ)``; try ``x+(bias+dif)`` then ``x−(bias+dif)``;
    bias ``0.2·bias+0.4·(dif+bias)`` / ``bias−0.4·(dif+bias)`` / ``0.5·bias``; step
    ``δ×adjustSuccess(2.0)`` after 5 successes, ``δ×adjustFailed(0.5)`` after **3** failures;
    ``δ₀=1.2``. State (bias/δ/streaks) persists for the WHOLE RUN — never reset on incumbent
    adoption (C++ ``_swparams`` created once, MOSTechniqueLSObj.cc:172).
  • **MTS-LS1-Reduced** (``MTS_t1``): dimension subset covering ``searchProb=0.9`` of the
    RL improvement mass + ``minProb=0.05·D`` random others (**RLImprovPerDimManager**: values
    init 1.0, unexplored dims outrank all explored until every dim is touched, then EMA
    ``0.7·old+0.3·new``); dims swept in ASCENDING index order; probes ``x−1.0·SR`` /
    ``x+0.5·SR``; ``SR×=0.5`` on a stalled sweep, reset to ``0.4·range`` below 1e-14; SR +
    improve flag persist across blocks (per-genome ``_SR``/``_improve`` carried by lineage
    copies, GA1DArrayGenome.cc:268/342 — improve starts True); whole sweeps only (the C++
    per-call eval cap is dead code — budget enforced between sweeps).

MOS framework (``mos2`` driver = MOSEA2.cc): ``pop=400``, static ``stepFactor φ=36000``,
**Average Fitness Increment** quality, dynamic participation ``ξ=0.05``, ``minPart=0.2``,
plus the **improvement override** (MOSTechniqueSet.cc:471-523): after generation 10, when
the AFI-best set ≠ the most-improved set (``times_improved/(1500·participation)``; GA never
improves → can never win), the transfer runs on improvement ratios instead of AFI. NO
population restart exists in the winner config (restartRequired() ≡ false; MOSEA2.cc:138).
tournament-2 selection, budget 3e6.

Suite: cec2013lsgo (D=1000). Family RNG (``_base``) + budget-exact + native GISR telemetry
from the GA generations (§3.7). The two local searches are one-eval-at-a-time (faithful; the
LS share of the D=1000 budget is sequential, like the other LSGO baselines).
"""

# VENDORED from 05-Human-Inspired-Family_Python_v0.1
#   src/human_inspired_family/optimizers/external/mos_cec2013lsgo.py
#   source sha256: 758aa8d688258a15  (was b7422576536e1cda before the
#   2026-07-28 MTS-LS1 bounds fix, applied identically at the source and
#   re-vendored so the bodies stay byte-identical -- see D-8.6.1)
# Imported 2026-07-25 to run MOS and SHADE-ILS natively on CEC2013LSGO under
# this project's harness, so the LSGO comparison is first-party rather than a
# published-table citation. ONLY the import namespace was rewritten; the
# algorithm bodies are byte-faithful to the source, which carries project 05's
# parity verdicts (shade-ils: FROZEN/user-signed 2026-07-24, author-code-faithful
# oracle, 14/15 within 2x of the published table; mos: 15/15 cells compared).
# Do not edit the algorithm bodies here -- amend at the source and re-vendor.

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from gsk_family.types import OptimizerOptions, OptimizerResult

from . import _base


def _rel_inc(new: float, old: float) -> float:
    """AFI per-individual increment: |Δf/f_before| if improved, else 0 (computeFitnessIncrement)."""
    if new < old and old != 0.0:
        return abs((new - old) / old)
    return 0.0


def _update_participation(part: np.ndarray, qual: np.ndarray, xi: float, min_part: float) -> None:
    """DynamicParticipation.update — transfer participation loser→winner (in place)."""
    best_q = float(qual.max())
    best_ids = [j for j in range(qual.size) if qual[j] == best_q]
    if len(best_ids) == 0 or len(best_ids) == qual.size:
        return                                                          # all-best / all-equal: no change
    base = 0.0
    for j in range(qual.size):
        if j in best_ids:
            continue
        diff = (best_q - qual[j]) / (best_q - base)                     # relative quality gap
        ratio_inc = part[j] * xi * diff
        if part[j] - ratio_inc > min_part:
            shared = ratio_inc / len(best_ids)
            for b in best_ids:
                part[b] += shared
            part[j] -= ratio_inc
        elif part[j] > min_part:
            shared = (part[j] - min_part) / len(best_ids)
            for b in best_ids:
                part[b] += shared
            part[j] = min_part
    np.clip(part, 0.0, 1.0, out=part)


_COUNTING_RULE = (
    "GISR denominator = GA offspring generated per GA generation (= NP=400); numerator = "
    "children with f(child) < min(parent fitness) (strict). Population-based GA generations "
    "over the shared MOS population; the single-incumbent Solis-Wets and MTS-LS1-Reduced "
    "phases advance nfes/best-so-far (in the convergence trace) but produce no population records."
)


def _tournament(fitness: np.ndarray, rng, n: int) -> int:
    """unif_tournament:2 — the better of two uniformly-random individuals among ``n``."""
    a = rng.integers(0, n)
    b = rng.integers(0, n)
    return a if fitness[a] <= fitness[b] else b


# ---------------------------------------------------------------------------
# Technique 1 — GA (BLX-alpha crossover + Gaussian mutation, generational + elitism)
# ---------------------------------------------------------------------------
def _ga_evolve(pop, fitness, sr_arr, imp_arr, max_evals, ev, rng, lb, ub, recorder, pcx, pmut, alpha=0.5):
    """Run the GA technique for max_evals FEs; return (pop, fitness, sr_arr, imp_arr, AFI-quality).

    Per-genome SR/improve carriage (GA1DArrayGenome copy semantics): a child in aux slot k
    is a clone of pop[k] with only its GENES overwritten (GARealOps.cc:180-181), so it
    CARRIES pop[k]'s _SR/_improve into the mu+lambda pool.
    """
    N, D = pop.shape
    if max_evals <= 0:
        return pop, fitness, sr_arr, imp_arr, 0.0
    qual_acum = 0.0
    iters = 0
    total = 0
    span = ub - lb                                                  # span[i] == ub[i]-lb[i] bitwise
    nmut = pmut * D
    nm_base = int(nmut)
    nm_frac = nmut - nm_base
    # BLX scratch buffers, reused across children (each op below writes every element).
    w1 = np.empty(D, dtype=np.float64)
    w2 = np.empty(D, dtype=np.float64)
    w3 = np.empty(D, dtype=np.float64)
    w4 = np.empty(D, dtype=np.float64)
    while total < max_evals and not ev.is_exhausted():
        n_this = min(N, max_evals - total, ev.remaining())
        if n_this <= 0:
            break
        children = np.empty((n_this, D), dtype=np.float64)
        parent_best = np.empty(n_this, dtype=np.float64)
        for k in range(n_this):
            mom = _tournament(fitness, rng, N)
            dad = _tournament(fitness, rng, N)
            parent_best[k] = min(fitness[mom], fitness[dad])
            child = children[k]
            if rng.random() < pcx:                                  # BLX-alpha crossover
                p1, p2 = pop[mom], pop[dad]
                np.subtract(p1, p2, out=w1)
                np.abs(w1, out=w1)
                w1 *= alpha                                         # alpha*dist (shared by lo and hi)
                np.minimum(p1, p2, out=w2)
                w2 -= w1
                np.maximum(w2, lb, out=w2)                          # lo
                np.maximum(p1, p2, out=w3)
                w3 += w1
                np.minimum(w3, ub, out=w3)                          # hi
                np.subtract(w3, w2, out=w4)
                np.multiply(rng.random(D), w4, out=w4)              # u*(hi-lo)
                np.add(w2, w4, out=child)                           # lo + u*(hi-lo)
            else:
                np.copyto(child, pop[mom])
            # Gaussian mutation: ~pmut*D genes, each + N(0,1)*(ub-lb), bound-rejected
            nm = nm_base + (1 if rng.random() < nm_frac else 0)
            if nm > 0:
                genes = np.unique(np.asarray(rng.integers(0, D, nm), dtype=np.int64))
                # Batched normals (bit-identical to the scalar path; see
                # _base.NormalStream): this rejection loop is the run's hottest
                # RNG consumer (>1.5M scalar draws / ~15% of wall time at D=1000).
                with _base.NormalStream(rng) as draw_normal:
                    for idx in genes.tolist():
                        base = float(child[idx])                    # written only on break below
                        lbi = float(lb[idx])
                        ubi = float(ub[idx])
                        si = float(span[idx])
                        for _ in range(100):
                            nv = base + draw_normal() * si
                            if lbi <= nv <= ubi:
                                child[idx] = nv
                                break

        cf = ev.evaluate(children)
        denom = np.where(parent_best == 0.0, 1.0, np.abs(parent_best))
        inc = np.where(cf < parent_best, np.abs((cf - parent_best) / denom), 0.0)
        qual_acum += float(np.sum(inc)) / n_this
        iters += 1
        recorder.record_generation(
            pop, best_fitness=ev.best_fitness, nfes=ev.nfes, generated=int(n_this),
            accepted_improved=int(np.count_nonzero(cf < parent_best)), fitness=fitness,
        )
        # PopElitism (mu+lambda): population U children, keep the best N (PopElitism.cc:15-29).
        # Monotone — the incumbent can never be ejected; applies to fractional chunks too.
        # Children carry their aux-slot's SR/improve (clone of pop[k], genes overwritten).
        pool = np.concatenate([pop, children])
        poolf = np.concatenate([fitness, cf])
        poolsr = np.concatenate([sr_arr, sr_arr[:n_this]])
        poolim = np.concatenate([imp_arr, imp_arr[:n_this]])
        order = np.argsort(poolf, kind="stable")[:N]
        pop = pool[order]                                           # fancy indexing: fresh arrays
        fitness = poolf[order]
        sr_arr = poolsr[order]
        imp_arr = poolim[order]
        total += n_this
    return pop, fitness, sr_arr, imp_arr, qual_acum / iters if iters > 0 else 0.0


# ---------------------------------------------------------------------------
# Technique 2 — Solis & Wets (adaptive random-walk LS with bias)
# ---------------------------------------------------------------------------
@dataclass
class _SW:
    """Persistent Solis-Wets state (bias vector, step, success/failure streaks, incumbent).

    carried_SR/carried_imp = the incumbent genome's per-genome _SR/_improve, transported as
    CARGO only (soliswets never touches them) — the SW relay is how MTS's annealed SR
    travels through the population in the C++ (copy() carries _SR; LSElitism installs it).
    """
    bias: np.ndarray
    delta: float
    num_success: int
    num_failed: int
    current_x: np.ndarray | None
    current_f: float
    carried_SR: float = 0.0
    carried_imp: bool = True


def _sw_block(x, f, sw, max_iters, ev, rng, lb, ub, max_succ, max_fail, adj_succ, adj_fail):
    """One Solis-Wets budget block; returns (fit_inc, evals, n_improved, x, f). Mutates ``sw``."""
    x = x.copy()
    D = x.shape[0]
    fit_inc = 0.0
    evals = 0
    n_improved = 0                                                  # _times_improved feed (solis.cc:213,238)
    bias, delta = sw.bias, sw.delta
    nsucc, nfail = sw.num_success, sw.num_failed
    while evals < max_iters and not ev.is_exhausted():
        dif = _base.standard_normal(rng, D)                         # fresh float64 array
        dif *= delta
        x1 = x + bias                                               # fresh: adopted as x on success
        x1 += dif                                                   # keeps the (x+bias)+dif association
        np.clip(x1, lb, ub, out=x1)
        f1 = ev.evaluate_one(x1)
        evals += 1
        fit_inc += _rel_inc(f1, f)
        if f1 < f:                                                  # success (+)
            x, f = x1, f1
            t = dif + bias
            t *= 0.4
            bias = bias * 0.2                                       # rebind: never mutate pre-update bias
            bias += t                                               # = 0.2*bias + 0.4*(dif+bias)
            nsucc += 1
            nfail = 0
            n_improved += 1
        else:
            if evals >= max_iters or ev.is_exhausted():
                break
            x2 = x - bias
            x2 -= dif                                               # keeps the (x-bias)-dif association
            np.clip(x2, lb, ub, out=x2)
            f2 = ev.evaluate_one(x2)
            evals += 1
            fit_inc += _rel_inc(f2, f)
            if f2 < f:                                              # success (-)
                x, f = x2, f2
                t = dif + bias
                t *= 0.4
                bias = bias - t                                     # = bias - 0.4*(dif+bias)
                nsucc += 1
                nfail = 0
                n_improved += 1
            else:                                                   # failure
                # In place even when aliasing sw.bias: sw.bias is only reassigned
                # below and never read in between, so the mutation is invisible.
                bias *= 0.5
                nfail += 1
                nsucc = 0
        if nsucc >= max_succ:
            delta *= adj_succ
            nsucc = 0
        if nfail >= max_fail:
            delta *= adj_fail
            nfail = 0
    sw.bias, sw.delta, sw.num_success, sw.num_failed = bias, delta, nsucc, nfail
    return fit_inc, evals, n_improved, x, f


def _sw_evolve(pop, fitness, sr_arr, imp_arr, max_evals, sw, ev, rng, lb, ub, delta0, mx_s, mx_f, a_s, a_f):
    """Run Solis-Wets on the incumbent for max_evals FEs; return
    (pop, fitness, sr_arr, imp_arr, AFI-quality, n_improved).

    Incumbent rule (MOSTechniqueLSObj.cc:161-168): adopt the population best only when it is
    STRICTLY better than the lineage incumbent — adopting genes/fitness AND the genome's
    per-genome SR/improve cargo (copy() carries _SR/_improve). bias/delta/streaks are NEVER
    reset (C++ ``_swparams`` created once for the whole run, MOSTechniqueLSObj.cc:172).
    The SW product is installed back with its carried SR/improve (LSElitism).
    """
    if max_evals <= 0:
        return pop, fitness, sr_arr, imp_arr, 0.0, 0
    best_i = int(np.argmin(fitness))
    if sw.current_x is None or fitness[best_i] < sw.current_f:      # adopt genes/fitness + SR cargo
        g_x = pop[best_i].copy()
        g_f = float(fitness[best_i])
        sw.carried_SR = float(sr_arr[best_i])
        sw.carried_imp = bool(imp_arr[best_i])
    else:
        g_x = sw.current_x.copy()
        g_f = sw.current_f
    used = 0
    fit_inc_total = 0.0
    n_improved = 0
    while used < max_evals and not ev.is_exhausted():
        inc, e, ni, g_x, g_f = _sw_block(g_x, g_f, sw, max_evals - used, ev, rng, lb, ub, mx_s, mx_f, a_s, a_f)
        fit_inc_total += inc
        used += e
        n_improved += ni
        if e == 0:
            break
    sw.current_x = g_x.copy()
    sw.current_f = g_f
    # Installs mutate the input arrays in place: safe because every caller passes freshly
    # materialized arrays (fancy-indexed technique returns) and rebinds them to our return.
    pop[best_i] = g_x
    fitness[best_i] = g_f
    sr_arr[best_i] = sw.carried_SR
    imp_arr[best_i] = sw.carried_imp
    order = np.argsort(fitness, kind="stable")
    return pop[order], fitness[order], sr_arr[order], imp_arr[order], \
        fit_inc_total / used if used > 0 else 0.0, n_improved


# ---------------------------------------------------------------------------
# Technique 3 — MTS-LS1-Reduced (dimension-focused per-coordinate line search)
# ---------------------------------------------------------------------------
@dataclass
class _MTSR:
    """Persistent MTS-LS1-Reduced state.

    SR + improve model the C++ per-genome ``_SR``/``_improve`` of the technique's lineage
    genome (GA1DArrayGenome.cc:268-271 init SR=range/2, improve=1; :342-345 copy carries
    both): they persist across blocks, and on adoption of a STRICTLY-better pop best they
    are OVERWRITTEN by that genome's carried values (g.copy(pop->best()) copies _SR too) —
    see _mtsr_evolve. values/explored = the run-global RLImprovPerDimManager (values init
    1.0; first touch replaces, then EMA 0.7·old+0.3·new; unexplored dims outrank all
    explored — RLImprovPerDimManager.cc:11-40, alpha=0.7).
    """
    SR: float
    improve: bool
    current_x: np.ndarray | None
    current_f: float
    values: np.ndarray = field(default=None)
    explored: np.ndarray = field(default=None)


def _select_dims(values, explored, search_prob, num_other, rng):
    """RLImprovPerDimManager.dimPerfValues + getDimsWhichProbSumAThreshold: unexplored dims
    boosted above all explored (max+1); dims covering search_prob of the mass (highest
    first) + num_other random lower-mass dims (floor 1); returned ascending-sorted
    (GARealOps.cc:825)."""
    D = values.shape[0]
    if bool(explored.all()):
        v = values                                                 # read-only here: no copy needed
    else:
        v = values.copy()
        v[~explored] = float(values.max()) + 1.0                   # unexplored-first boost
    total = float(v.sum())
    probs = v / total if total > 0.0 else np.full(D, 1.0 / D)
    order = np.argsort(probs, kind="stable")                       # ascending
    desc = order[::-1]
    # np.add.accumulate is strictly sequential (out[i] = out[i-1] + pv[i]), reproducing the
    # scalar `cum += probs[order[i]]` walk bit-for-bit (probs >= +0.0, so out[0] == 0.0+pv[0]).
    cs = np.cumsum(probs[desc])
    exceed = cs > search_prob
    # Cut index: first prefix exceeding search_prob, else take all D (argmax alone would
    # return 0 on an all-False mask, hence the any() guard).
    k = int(np.argmax(exceed)) if bool(exceed.any()) else D - 1
    selected = desc[: k + 1].tolist()
    if num_other <= 0:
        num_other = 1                                              # ImprovPerDimManager.cc:68
    if k < D - 1:
        remaining = order[: D - 1 - k]
        perm = np.asarray(rng.permutation(remaining.shape[0]), dtype=np.int64)[:num_other]
        selected.extend(int(remaining[p]) for p in perm)
    return sorted(set(selected))


def _mtsr_sweep(x, score, m, ev, rng, lb, ub, adj_f, adj_min, m_l, m_r, s_prob, min_prob):
    """One COMPLETE MTS-LS1-Reduced sweep over the selected dims; returns
    (fit_inc, evals, n_improved, x, score). Mutates ``m``.

    The C++ per-call eval cap is dead code (6-arg extern-C called through a 7-arg pointer —
    ConfigFileParser.h:828/860, GARealOps.h:76/82 — so ``evals == maxIters`` never fires);
    each LS call is a full sweep and the block budget is enforced BETWEEN sweeps
    (MOSTechniqueLS.cc:187). Mid-sweep exit happens only on true global budget exhaustion
    (the family budget contract).
    """
    D = x.shape[0]
    x = x.copy()
    fit_inc = 0.0
    n_improved = 0
    if not m.improve:                                              # SR adaptation on a stalled sweep
        m.SR *= adj_f
        if m.SR < 1e-14:
            # SR is a SCALAR step scale (GA1DArrayGenome carries one _SR per
            # genome), so its reset needs one representative range. dim 0 is
            # exact for this port's validated regime -- CEC2013LSGO boxes are
            # per-variable uniform -- and remains the C++ behaviour.
            m.SR = (float(ub[0]) - float(lb[0])) * adj_min
    m.improve = False
    step_l = m_l * m.SR                                            # m.SR is sweep-invariant past here
    step_r = m_r * m.SR
    num_other = int(D * min_prob)
    dims = _select_dims(m.values, m.explored, s_prob, num_other, rng)
    values = m.values                                              # in-place writes persist on m
    explored = m.explored
    eval_one = ev.evaluate_one
    is_exhausted = ev.is_exhausted
    evals = 0
    for dim in dims:
        if is_exhausted():
            return fit_inc, evals, n_improved, x, score
        old_gene = float(x[dim])
        old_score = score
        at_min = old_gene == lb[dim]
        new_score = None
        if not at_min:
            x[dim] = max(old_gene - step_l, float(lb[dim]))
            new_score = eval_one(x)
            evals += 1
            score = new_score
            if new_score < old_score and old_score != 0.0:         # _rel_inc inlined
                fit_inc += abs((new_score - old_score) / old_score)
        if (not at_min) and (new_score == old_score):
            x[dim] = old_gene
            score = old_score
        else:
            if at_min or (new_score is not None and new_score > old_score):
                x[dim] = old_gene
                score = old_score
                if is_exhausted():
                    return fit_inc, evals, n_improved, x, score
                if old_gene != ub[dim]:
                    x[dim] = min(old_gene + step_r, float(ub[dim]))
                    new_score = eval_one(x)
                    evals += 1
                    score = new_score
                    if new_score < old_score and old_score != 0.0:  # _rel_inc inlined
                        fit_inc += abs((new_score - old_score) / old_score)
                    if not (new_score < old_score):
                        x[dim] = old_gene
                        score = old_score
                    else:
                        m.improve = True
                        n_improved += 1
            else:
                m.improve = True
                n_improved += 1
        # RLImprovPerDimManager.updateValue: first touch replaces, then EMA 0.7*old+0.3*new
        new_val = abs(new_score - old_score) if (new_score is not None and new_score < old_score) else 0.0
        values[dim] = new_val if not explored[dim] else 0.7 * values[dim] + 0.3 * new_val
        explored[dim] = True
    return fit_inc, evals, n_improved, x, score


def _mtsr_evolve(pop, fitness, sr_arr, imp_arr, max_evals, m, ev, rng, lb, ub,
                 adj_f, adj_min, m_l, m_r, s_prob, min_prob):
    """Run MTS-LS1-Reduced on the incumbent for max_evals FEs; return
    (pop, fitness, sr_arr, imp_arr, AFI-quality, n_improved).

    Incumbent rule (MOSTechniqueLS.cc:160-167): ``g.copy(pop->best())`` adopts the pop
    best's genes/fitness AND its per-genome ``_SR``/``_improve`` (copy carries both); only
    when the pop best is NOT strictly better does ``g.copy(*_currentGenome)`` restore the
    lineage's annealed state. So on adoption of a GA-born best, SR re-seeds at that
    genome's carried value (ctor default range/2 for most slots) — the mechanism that
    re-opens the coarse SR ladder; the SW relay preserves annealed SR through the pop.
    Whole sweeps only; block allocation enforced BETWEEN sweeps (MOSTechniqueLS.cc:187).
    """
    if max_evals <= 0:
        return pop, fitness, sr_arr, imp_arr, 0.0, 0
    best_i = int(np.argmin(fitness))
    if m.current_x is None or fitness[best_i] < m.current_f:        # adopt genes/fitness + SR/improve
        g_x = pop[best_i].copy()
        g_f = float(fitness[best_i])
        m.SR = float(sr_arr[best_i])
        m.improve = bool(imp_arr[best_i])
    else:
        g_x = m.current_x.copy()
        g_f = m.current_f
    used = 0
    fit_inc_total = 0.0
    n_improved = 0
    while used < max_evals and not ev.is_exhausted():
        inc, e, ni, g_x, g_f = _mtsr_sweep(g_x, g_f, m, ev, rng, lb, ub,
                                           adj_f, adj_min, m_l, m_r, s_prob, min_prob)
        fit_inc_total += inc
        used += e
        n_improved += ni
        if e == 0:
            break
    m.current_x = g_x.copy()
    m.current_f = g_f
    # Installs mutate the input arrays in place: safe because every caller passes freshly
    # materialized arrays (fancy-indexed technique returns) and rebinds them to our return.
    pop[best_i] = g_x
    fitness[best_i] = g_f
    sr_arr[best_i] = m.SR                                           # LSElitism installs g with its SR
    imp_arr[best_i] = m.improve
    order = np.argsort(fitness, kind="stable")
    return pop[order], fitness[order], sr_arr[order], imp_arr[order], \
        fit_inc_total / used if used > 0 else 0.0, n_improved


def optimize(problem, options: OptimizerOptions) -> OptimizerResult:
    """Run the CEC2013-winner MOS (GA + Solis-Wets + MTS-LS1-Reduced) under the family contract."""
    rng, ev, start = _base.start_run(problem, options)
    D = int(problem.dim)
    lb = np.asarray(problem.lb, dtype=np.float64).reshape(-1)
    ub = np.asarray(problem.ub, dtype=np.float64).reshape(-1)
    # dim-0 scalars: used ONLY for the scalar SR seed below. Until 2026-07-28
    # these were also handed to MTS-LS1-Reduced, which clipped its probes
    # against them -- correct on a per-variable-uniform box (every CEC2013LSGO
    # function) but a FEASIBILITY BUG on heterogeneous boxes: 12 of 22 CEC2011
    # problems then evaluated points outside the box, up to 16.8% of
    # evaluations, and the returned best_x could itself be infeasible. MTS now
    # receives the lb/ub vectors like the GA and Solis-Wets techniques always
    # did. Identity on a uniform box, so validated LSGO results are unchanged.
    lb0, ub0 = float(lb[0]), float(ub[0])

    N = int(_base.param(options, "pop_total", 400))
    phi = int(_base.param(options, "step_factor", 36000))
    xi = float(_base.param(options, "adjust", 0.05))
    min_part = float(_base.param(options, "min_part", 0.2))
    pcx = float(_base.param(options, "pcx", 0.9))
    pmut = float(_base.param(options, "pmut", 0.01))
    # AUTHORITATIVE constants = GAEDAConfig.cc:326-354 default_value() (staged winner tree,
    # SHA 3208074) — the `# sw-…`/`# mts-…` lines in cec2013.cfg are inert comments (boost
    # parse_config_file, GAEDAConfig.cc:469). Adjudicated 2026-07-24; do NOT restore the
    # cfg-comment values (2.4/0.75/5, 0.25, 0.025, ×2-grow) — they were never executed.
    sw_maxs, sw_maxf = 5, 3
    sw_adjs, sw_adjf, sw_delta0 = 2.0, 0.5, 1.2
    mt_adjf, mt_adjmin, mt_ml, mt_mr = 0.5, 0.4, 1.0, 0.5
    mt_sprob, mt_minprob = 0.9, 0.05

    # ---- init population (fair start on the family stream) ----
    if options.initial_population is not None:
        pop = np.asarray(options.initial_population, dtype=np.float64).reshape(-1, D)[:N].copy()
    else:
        pop = lb + np.asarray(rng.random((N, D)), dtype=np.float64) * (ub - lb)
    fitness = ev.evaluate(pop)
    order = np.argsort(fitness, kind="stable")
    pop, fitness = pop[order], fitness[order]

    recorder = _base.make_recorder(problem, options, _COUNTING_RULE)
    recorder.record_initial(pop, ev.best_fitness, ev.nfes)

    participation = np.array([1.0 / 3, 1.0 / 3, 1.0 / 3])           # [GA, SW, MTS-Reduced]
    quality = np.array([0.0, 0.0, 0.0])
    times_improved = np.array([0, 0, 0], dtype=np.int64)            # GA never increments (C++)
    gen = 0                                                         # completed MOS steps
    SR0 = 0.5 * (ub0 - lb0)                                         # GA1DArrayGenome ctor: range/2, improve=1
    sr_arr = np.full(N, SR0)                                        # per-genome _SR (carried by copies)
    imp_arr = np.ones(N, dtype=bool)                                # per-genome _improve
    sw = _SW(bias=np.zeros(D), delta=sw_delta0, num_success=0, num_failed=0, current_x=None, current_f=float("inf"),
             carried_SR=SR0, carried_imp=True)
    mtsr = _MTSR(SR=SR0, improve=True, current_x=None, current_f=float("inf"),
                 values=np.ones(D), explored=np.zeros(D, dtype=bool))

    # NOTE: no population restart — the winner config never restarts (restartRequired() is
    # false for GA/SW/MTS; MOSEA2.cc:138-167 restart path is dead code there).
    while not ev.is_exhausted():
        # Improvement override (MOSTechniqueSet.cc:471-523): after gen>10, when the AFI-best
        # set differs from the most-improved set (times_improved/(1500*participation); GA
        # always 0 -> can never win), the transfer arithmetic runs on improvement ratios.
        q_eff = quality
        if gen > 10:
            ratio_imp = times_improved.astype(np.float64) / (1500.0 * participation)
            best_afi = {j for j in range(3) if quality[j] == quality.max()}
            best_imp = {j for j in range(3) if ratio_imp[j] == ratio_imp.max()}
            if best_afi != best_imp:
                q_eff = ratio_imp
        _update_participation(participation, q_eff, xi, min_part)
        evals_to_share = min(phi, ev.remaining())
        if evals_to_share <= 0:
            break
        evals_per = np.floor(participation * evals_to_share / float(participation.sum())).astype(np.int64)
        while int(evals_per.sum()) < evals_to_share:
            evals_per[int(np.argmin(evals_per))] += 1

        pop, fitness, sr_arr, imp_arr, q_ga = _ga_evolve(pop, fitness, sr_arr, imp_arr, int(evals_per[0]),
                                                         ev, rng, lb, ub, recorder, pcx, pmut)
        pop, fitness, sr_arr, imp_arr, q_sw, ti_sw = _sw_evolve(pop, fitness, sr_arr, imp_arr, int(evals_per[1]),
                                                                sw, ev, rng, lb, ub,
                                                                sw_delta0, sw_maxs, sw_maxf, sw_adjs, sw_adjf)
        pop, fitness, sr_arr, imp_arr, q_mt, ti_mt = _mtsr_evolve(pop, fitness, sr_arr, imp_arr, int(evals_per[2]),
                                                                  mtsr, ev, rng, lb, ub,
                                                                  mt_adjf, mt_adjmin, mt_ml, mt_mr, mt_sprob, mt_minprob)
        quality = np.array([q_ga, q_sw, q_mt])
        times_improved = np.array([0, ti_sw, ti_mt], dtype=np.int64)
        gen += 1

    return _base.build_result(
        "mos-cec2013lsgo", problem, options, ev, start_time=start,
        params={"profile": _base.resolve_profile(options), "pop_total": N, "step_factor": phi,
                "adjust_xi": xi, "min_part": min_part, "pcx": pcx, "pmut": pmut,
                "part_final": [float(p) for p in participation]},
        notes="MOS CEC2013-LSGO winner (HRH GA + Solis-Wets + MTS-LS1-Reduced); code-first port; paper=LaTorre,Muelas,Pena 2013.",
        telemetry=recorder.finalize(),
    )
