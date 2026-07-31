"""jSO — source-faithful, Brest, Maučec & Bošković 2017 (CEC), DOI 10.1109/CEC.2017.7969456.

jSO = iL-SHADE + jSO deltas, on the L-SHADE lineage. Implemented STRICTLY from
``reference_code/external_baseline_algorithms/jso/VERSION_FREEZE.md`` (§2 delta table,
Appendix constants). All UNRESOLVED items resolved per the record's recommendation:
M_F,init=0.3 (U1), p decreasing 0.25→0.125 (U2), clamps gated on nfes/max_nfes (U3),
per-generation memory/LPSR/p-update (U4), midpoint-reflection bounds (U5), N_init via
natural log (U6), archive rate 1.0 (U7).

jSO deltas over L-SHADE: current-to-pBest-**w**/1 (F_w on the pbest term only), H=5,
M_CR/M_F init 0.8/0.3 with a fixed 0.9 terminal memory slot, early CR floors + F cap,
N_init=round(25·ln(D)·√D), and the iL-SHADE **averaged** memory update
M ← mean(M_old, weightedLehmerMean(S)). Family RNG + budget-exact + native GISR
telemetry (§3.7).

Archive eviction (2026-07-24 amendment): the archive uses the **C++-faithful
incremental random-overwrite** of Brest's ``lshade.cc`` (l.236-244) — the one
mechanism sourced from the reference C++ rather than the paper. The paper states only
"randomly selected elements are deleted"; the batch-append + permutation-subsample
realisation of that wording produced a staler, over-diverse archive that left a heavy
F11 D30 exploitation tail (mean 6.88 / worst 61 vs the reference 3.04 / 9.19). The
incremental-overwrite form removes it (F11 D30 mean → 3.54, tail 4/51 → 1/51) with no
F30 D10 regression. See ``docs/development/matlab_parity/freeze_jso_cec2017.md``.
"""

# VENDORED from 05-Human-Inspired-Family_Python_v0.1
#   src/human_inspired_family/optimizers/external/jso.py
#   source sha256: 0ef98a4b129379e7
# Imported 2026-07-26 so external SOTA baselines can be run natively under this
# project's harness (identical objective code, seed schedule, budget, protocol)
# instead of citing published tables. ONLY the import namespace was rewritten;
# the algorithm body is byte-faithful to the source, which carries project 05's
# parity records under docs/development/matlab_parity/.
# NOT part of the seven-method GSK-family statistical panel.
# Do not edit the algorithm body here -- amend at the source and re-vendor.

from __future__ import annotations

import numpy as np

from gsk_family.types import OptimizerOptions, OptimizerResult

from . import _base

_BOT = -1.0  # ⊥ terminal value for M_CR (jSO Alg.1 line 14: if M_CR < 0 then CR=0)
_COUNTING_RULE = (
    "GISR denominator = trial vectors generated per generation (= NP_g); numerator = "
    "trials with f(u) < f(x_i) (strict, Alg.1 l.36). Native DE replacement success rate."
)


def _mean_wl(s: np.ndarray, w: np.ndarray) -> float:
    """Weighted Lehmer (power-2) mean: Sum(w*s^2) / Sum(w*s)."""
    num = float(np.sum(w * s * s))
    den = float(np.sum(w * s))
    return num / den if den != 0.0 else 0.0


def optimize(problem, options: OptimizerOptions) -> OptimizerResult:
    """Run jSO under the family contract."""
    rng, ev, start = _base.start_run(problem, options)
    D = int(problem.dim)
    lb = np.asarray(problem.lb, dtype=np.float64).reshape(-1)
    ub = np.asarray(problem.ub, dtype=np.float64).reshape(-1)
    max_nfes = int(problem.max_nfes)

    H = int(_base.param(options, "H", 5))
    n_min = 4
    # Brest's `g_pop_size = round(sqrt(D)*log(D)*25)` (main.cc l.64) degenerates to 0 at
    # D=1 because ln(1)=0. He only ever ran CEC-2017 (D>=10), so the formula is undefined
    # there; floor it at the algorithm's own N_min, which is also LPSR's target. Inert for
    # D>=2 (25 at D=2) — only cec2011 T03/T04 are D=1.
    n_init = max(n_min, int(round(25.0 * np.log(D) * np.sqrt(D))))   # D9 / U6
    r_arc = float(_base.param(options, "r_arc", 1.0))            # U7: jSO |A| ≤ NP
    p_max, p_min = 0.25, 0.125                                    # D3 / U2

    if options.initial_population is not None:
        pop = np.asarray(options.initial_population, dtype=np.float64).reshape(-1, D)[:n_init].copy()
    else:
        pop = lb + np.asarray(rng.random((n_init, D)), dtype=np.float64) * (ub - lb)
    N = pop.shape[0]
    fitness = ev.evaluate(pop)
    # Memory: ALL H slots are initialised to (0.8, 0.3) and ALL H are written in turn
    # (lshade.cc l.89-91, l.297-298). The 0.9 terminal is NOT a pinned slot — it is a
    # read-time short-circuit (l.127-129: `if (random_selected_period == memory_size-1)
    # { mu_sf = 0.9; mu_cr = 0.9; }`). The distinction matters: because the write index
    # cycles all H slots while slot H-1 is never read, Brest DISCARDS one update in five.
    m_cr = np.full(H, 0.8)
    m_f = np.full(H, 0.3)
    k_pos = 0
    archive = np.empty((0, D), dtype=np.float64)
    arc_cap = int(round(n_init * r_arc))

    recorder = _base.make_recorder(problem, options, _COUNTING_RULE)
    recorder.record_initial(pop, ev.best_fitness, ev.nfes)

    while not ev.is_exhausted():
        frac = ev.nfes / max_nfes                                # nfes fraction drives clamps/F_w/p (U3)
        n_trials = min(N, ev.remaining())
        r_idx = np.asarray(rng.integers(0, H, n_trials), dtype=np.int64)

        # Read-time terminal short-circuit (lshade.cc l.127-129): drawing slot H-1
        # yields mu = 0.9 for BOTH memories, whatever the stored value is.
        mu_cr = np.where(r_idx == H - 1, 0.9, m_cr[r_idx])
        mu_f = np.where(r_idx == H - 1, 0.9, m_f[r_idx])

        # ---- CR ~ Normal(M_CR,0.1), clamp [0,1], ⊥ -> 0, early floor (D7) ----
        cr = np.asarray(_base.normal(rng, 0.0, 1.0, n_trials)) * 0.1 + mu_cr
        np.clip(cr, 0.0, 1.0, out=cr)
        cr[mu_cr < 0.0] = 0.0
        if frac < 0.25:
            cr = np.maximum(cr, 0.7)
        elif frac < 0.5:
            cr = np.maximum(cr, 0.6)

        # ---- F ~ Cauchy(M_F,0.1), resample<=0, clip>1, early cap (D8) ----
        f = np.asarray(_base.cauchy(rng, 0.0, 1.0, n_trials)) * 0.1 + mu_f
        for _ in range(100):
            bad = f <= 0.0
            if not bad.any():
                break
            f[bad] = np.asarray(_base.cauchy(rng, 0.0, 1.0, int(bad.sum()))) * 0.1 + mu_f[bad]
        f = np.minimum(f, 1.0)
        if frac < 0.6:
            f = np.where(f > 0.7, 0.7, f)

        # ---- F_w weight on the pbest term (Eq.4, jSO-specific) ----
        fw_scale = 0.7 if frac < 0.2 else (0.8 if frac < 0.4 else 1.2)
        fw = fw_scale * f

        # ---- current-to-pBest-w/1 with archive (Eq.3); p decreasing (D3) ----
        # p decreases CONTINUOUSLY with the evaluation fraction (jSO paper Eq.8,
        # p = p_max - (p_max-p_min)*nfes/max). Brest's C++ instead refreshes p_num only
        # inside the LPSR branch (lshade.cc:320-322) — a step function. The two agree to
        # <=1 in p_num, and reproducing the step form is NOT worth it: combined with the
        # all-slots memory cycle it drives a bounds-corner trap on ~4% of F30 D=10 runs
        # (mean 3.2e4 vs the reference's 3.9e2, which shows zero such blow-ups), while the
        # continuous form matches the published table. Fidelity here is to the paper.
        p_rate = p_max - (p_max - p_min) * frac
        order = np.argsort(fitness, kind="stable")
        p_num = max(2, int(round(N * p_rate)))
        pbest = order[:p_num][np.asarray(rng.integers(0, p_num, n_trials), dtype=np.int64)]
        idx = np.arange(n_trials)
        # iL-SHADE guard (Brest lshade.cc l.164-166): during the FIRST HALF of the
        # budget the p-best donor may not be the target itself -- otherwise the
        # jF*(x_pbest - x_i) term vanishes and the trial degenerates to plain
        # x_i + F*(x_r1 - x_r2) with no elite attraction. Matters increasingly as
        # LPSR shrinks N (p_num -> 2, so a self-hit costs ~50% of trials).
        if frac < 0.5:
            for _ in range(100):
                self_hit = pbest == idx
                if not self_hit.any():
                    break
                pbest[self_hit] = order[:p_num][
                    np.asarray(rng.integers(0, p_num, int(self_hit.sum())), dtype=np.int64)
                ]
        r1 = np.asarray(rng.integers(0, N - 1, n_trials), dtype=np.int64)
        r1[r1 >= idx] += 1
        pa = np.vstack([pop, archive]) if archive.shape[0] else pop
        npa = pa.shape[0]
        r2 = np.asarray(rng.integers(0, npa, n_trials), dtype=np.int64)
        for _ in range(100):
            clash = (r2 == idx) | (r2 == r1)
            if not clash.any():
                break
            r2[clash] = np.asarray(rng.integers(0, npa, int(clash.sum())), dtype=np.int64)
        base = pop[:n_trials]
        v = base + fw[:, None] * (pop[pbest] - base) + f[:, None] * (pop[r1] - pa[r2])

        # ---- midpoint-reflection bounds (U5, inherited L-SHADE) ----
        v = np.where(v < lb, (lb + base) / 2.0, v)
        v = np.where(v > ub, (ub + base) / 2.0, v)

        # ---- binomial crossover ----
        cross = np.asarray(rng.random((n_trials, D)), dtype=np.float64) <= cr[:, None]
        j_rand = np.asarray(rng.integers(0, D, n_trials), dtype=np.int64)
        cross[idx, j_rand] = True
        u = np.where(cross, v, base)

        u_fit = ev.evaluate(u)
        parent_fit = fitness[:n_trials]
        survive = u_fit <= parent_fit
        improved = u_fit < parent_fit
        n_improved = int(np.count_nonzero(improved))

        recorder.record_generation(
            pop, best_fitness=ev.best_fitness, nfes=ev.nfes, generated=int(n_trials),
            accepted_improved=n_improved, fitness=fitness,
        )

        # ---- per-generation tail (U4): archive, memory (iL-SHADE avg), LPSR, p ----
        if n_improved:
            # Archive insertion — C++-faithful incremental random-overwrite
            # (Brest lshade.cc l.236-244): each replaced parent, in target order,
            # appends while |A| < arc_cap, then OVERWRITES a uniformly-random slot
            # (one draw per over-cap insertion), keeping |A| == arc_cap. This is the
            # authoritative jSO archive; it supersedes the earlier paper-form
            # ("randomly selected elements are deleted") batch-append + permutation-
            # subsample, which produced a staler, over-diverse archive that slowed the
            # exploitation phase and left a heavy F11 D30 tail (mean 6.88, worst 61) the
            # reference (mean 3.04, worst 9.19) does not have. Fix 2026-07-24: mean->3.54,
            # tail 4/51->1/51, no F30 D10 regression. PROVENANCE: this one mechanism is
            # sourced from Brest's C++, not the paper (see freeze_jso_cec2017.md amendment).
            _parents = base[improved]
            for _pj in range(_parents.shape[0]):
                if archive.shape[0] < arc_cap:
                    archive = np.vstack([archive, _parents[_pj:_pj + 1]])
                else:
                    archive[int(rng.integers(0, arc_cap))] = _parents[_pj]
            df = np.abs(u_fit[improved] - parent_fit[improved])
            w = df / df.sum() if df.sum() > 0 else np.full(df.size, 1.0 / df.size)
            s_cr, s_f = cr[improved], f[improved]
            # lshade.cc l.284: the only LIVE ⊥ trigger is `temp_sum_cr == 0`. The
            # `memory_cr[pos] == -1` disjunct tests the accumulator zeroed at l.264 and
            # then filled with Sum(w*cr^2) >= 0, so it can never hold -1 — dead code, and
            # ⊥ is therefore NOT an absorbing state. l.288-289 then average
            # UNCONDITIONALLY, so a ⊥ slot ends up holding (old_cr - 1)/2, not -1.
            new_cr = _BOT if float(s_cr.max()) == 0.0 else _mean_wl(s_cr, w)
            m_cr[k_pos] = 0.5 * (new_cr + m_cr[k_pos])           # l.289 (iL-SHADE average)
            m_f[k_pos] = 0.5 * (_mean_wl(s_f, w) + m_f[k_pos])   # l.288
            k_pos = (k_pos + 1) % H                              # l.297-298: cycles ALL H slots

        pop[:n_trials] = np.where(survive[:, None], u, base)
        fitness[:n_trials] = np.where(survive, u_fit, parent_fit)

        # Archive is bounded to arc_cap incrementally at insertion (above), matching
        # the C++; no separate subsample step (lshade.cc keeps |A| == arc_size live).

        if n_trials < N:
            break

        n_new = int(round(n_init - (n_init - n_min) / max_nfes * ev.nfes))   # LPSR (inherited)
        n_new = max(n_min, min(n_new, N))
        if n_new < N:
            keep = np.argsort(fitness, kind="stable")[:n_new]
            pop = pop[keep].copy()
            fitness = fitness[keep].copy()
            N = n_new
            arc_cap = int(round(N * r_arc))
            # LPSR archive shrink — truncate the count to the new arc_size
            # (lshade.cc l.316-317: `if (arc_ind_count > arc_size) arc_ind_count = arc_size`).
            if archive.shape[0] > arc_cap:
                archive = archive[:arc_cap]

    return _base.build_result(
        "jso", problem, options, ev, start_time=start,
        params={"profile": _base.resolve_profile(options), "H": H, "N_init": n_init,
                "N_min": n_min, "r_arc": r_arc, "p_max": p_max, "p_min": p_min},
        notes="jSO 2017 (iL-SHADE + jSO deltas); paper=Brest,Maucec,Boskovic 2017.",
    )
