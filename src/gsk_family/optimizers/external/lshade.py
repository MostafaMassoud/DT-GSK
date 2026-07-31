"""L-SHADE — source-faithful, Tanabe & Fukunaga 2014 (CEC), DOI 10.1109/CEC.2014.6900380.

= SHADE 1.1 + Linear Population Size Reduction. Originally ported paper-first from
``reference_code/external_baseline_algorithms/lshade/VERSION_FREEZE.md``; on
2026-07-20 (user-directed) aligned to the authors' shipped MATLAB at
``reference_code/external_baseline_algorithms/lshade_matlab/lshade.m`` — the artifact
that actually produced the committed reference tables, which supersedes the paper's
ParamILS table wherever the two disagree. NO iL-SHADE / jSO / cnEpSin behavior.

Settings per the shipped code: **H=5** (l.25) and **r_arc=1.4** (l.24) — the
CEC2014-competition values, NOT the paper's ParamILS pair (6 / 2.6);
N_init=round(18·D) (l.26), N_min=4 (l.29), p=0.11 (l.23), memory init 0.5 (l.82-83),
CR~N(M_CR,0.1) clamp[0,1] with ⊥→0 (l.100-104), F~Cauchy(M_F,0.1) resample-≤0
truncate-1 (l.107-115), weighted-Lehmer memory for BOTH CR and F (l.182, 188),
midpoint bound repair (boundConstraint.m), **parent wins ties** (l.170:
``min([fitness, children], [], 2)`` returns index 1 on equality), archive+success on
strict < (l.162), **archive dedup** (updateArchive.m ``unique(rows)``), LPSR Eq(10)
delete-worst (l.196-209), M_CR terminal value ⊥ (l.185-186).

RNG through the family stream (`_base`); telemetry: native DE GISR
(accepted_improved = strictly-improving trials) + diversity, per §3.7.
"""

# VENDORED from 05-Human-Inspired-Family_Python_v0.1
#   src/human_inspired_family/optimizers/external/lshade.py
#   source sha256: df93a8a180119c26
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

_BOT = np.nan  # ⊥ terminal value for M_CR (freeze §8)
_COUNTING_RULE = (
    "GISR denominator = trial vectors generated per generation (= N_G); numerator = "
    "trials with f(u) < f(x_i) (strict improvement, Alg.2 l.16). Native DE replacement "
    "success rate."
)


def _mean_wl(s: np.ndarray, w: np.ndarray) -> float:
    """Weighted Lehmer (power-2) mean, Eq (7): Σ w·S² / Σ w·S."""
    num = float(np.sum(w * s * s))
    den = float(np.sum(w * s))
    return num / den if den != 0.0 else 0.0


def optimize(problem, options: OptimizerOptions) -> OptimizerResult:
    """Run the 2014 canonical L-SHADE under the family contract."""
    rng, ev, start = _base.start_run(problem, options)
    D = int(problem.dim)
    lb = np.asarray(problem.lb, dtype=np.float64).reshape(-1)
    ub = np.asarray(problem.ub, dtype=np.float64).reshape(-1)
    max_nfes = int(problem.max_nfes)

    H = int(_base.param(options, "H", 5))          # shipped code l.25 (paper table: 6)
    r_ninit = float(_base.param(options, "r_ninit", 18.0))
    n_init = int(round(r_ninit * D))
    n_min = 4
    r_arc = float(_base.param(options, "r_arc", 1.4))   # shipped code l.24 (paper table: 2.6)
    p_rate = float(_base.param(options, "p", 0.11))

    # ---- initialization (fair start on the family stream) ----------------
    if options.initial_population is not None:
        pop = np.asarray(options.initial_population, dtype=np.float64).reshape(-1, D)[:n_init].copy()
    else:
        pop = lb + np.asarray(rng.random((n_init, D)), dtype=np.float64) * (ub - lb)
    N = pop.shape[0]
    fitness = ev.evaluate(pop)
    m_cr = np.full(H, 0.5)
    m_f = np.full(H, 0.5)
    k_pos = 0
    archive = np.empty((0, D), dtype=np.float64)
    arc_cap = int(round(n_init * r_arc))

    recorder = _base.make_recorder(problem, options, _COUNTING_RULE)
    recorder.record_initial(pop, ev.best_fitness, ev.nfes)

    while not ev.is_exhausted():
        n_trials = min(N, ev.remaining())            # budget-exact final generation
        # ---- per-trial control params (draw order r_i -> CR -> F, freeze §6) ----
        r_idx = np.asarray(rng.integers(0, H, n_trials), dtype=np.int64)
        cr = np.asarray(_base.normal(rng, 0.0, 1.0, n_trials)) * 0.1 + m_cr[r_idx]
        np.clip(cr, 0.0, 1.0, out=cr)
        cr[np.isnan(m_cr[r_idx])] = 0.0              # ⊥ cell -> CR=0
        f = np.asarray(_base.cauchy(rng, 0.0, 1.0, n_trials)) * 0.1 + m_f[r_idx]
        for _ in range(100):                          # resample while F <= 0 (Eq 2)
            bad = f <= 0.0
            if not bad.any():
                break
            f[bad] = np.asarray(_base.cauchy(rng, 0.0, 1.0, int(bad.sum()))) * 0.1 + m_f[r_idx[bad]]
        f = np.minimum(f, 1.0)                         # truncate to 1

        # ---- current-to-pbest/1 with archive (Eq 3) ----
        order = np.argsort(fitness, kind="stable")
        p_num = max(2, int(round(N * p_rate)))        # freeze U1
        pbest = order[:p_num][np.asarray(rng.integers(0, p_num, n_trials), dtype=np.int64)]
        idx = np.arange(n_trials)
        r1 = np.asarray(rng.integers(0, N - 1, n_trials), dtype=np.int64)
        r1[r1 >= idx] += 1                             # r1 != i, uniform on [0,N)\{i}
        pa = np.vstack([pop, archive]) if archive.shape[0] else pop
        npa = pa.shape[0]
        r2 = np.asarray(rng.integers(0, npa, n_trials), dtype=np.int64)
        for _ in range(100):                           # r2 != i and != r1
            clash = (r2 == idx) | (r2 == r1)
            if not clash.any():
                break
            r2[clash] = np.asarray(rng.integers(0, npa, int(clash.sum())), dtype=np.int64)
        base = pop[:n_trials]
        v = base + f[:, None] * (pop[pbest] - base) + f[:, None] * (pop[r1] - pa[r2])

        # ---- boundary correction: midpoint with parent (Eq 4) ----
        below = v < lb
        above = v > ub
        v = np.where(below, (lb + base) / 2.0, v)
        v = np.where(above, (ub + base) / 2.0, v)

        # ---- binomial crossover (Eq 5) ----
        cross = np.asarray(rng.random((n_trials, D)), dtype=np.float64) <= cr[:, None]
        j_rand = np.asarray(rng.integers(0, D, n_trials), dtype=np.int64)
        cross[idx, j_rand] = True
        u = np.where(cross, v, base)

        # ---- evaluate + selection ----
        u_fit = ev.evaluate(u)
        parent_fit = fitness[:n_trials]
        improved = u_fit < parent_fit                  # strict: selection, archive, success
        survive = improved                             # parent wins ties (MATLAB l.170)
        n_improved = int(np.count_nonzero(improved))

        recorder.record_generation(
            pop, best_fitness=ev.best_fitness, nfes=ev.nfes, generated=int(n_trials),
            accepted_improved=n_improved, fitness=fitness,
        )

        if n_improved:
            archive = np.vstack([archive, base[improved]])
            archive = np.unique(archive, axis=0)       # updateArchive.m dedup
            df = np.abs(u_fit[improved] - parent_fit[improved])
            w = df / df.sum() if df.sum() > 0 else np.full(df.size, 1.0 / df.size)
            s_cr = cr[improved]
            s_f = f[improved]
            # memory update (Algorithm 1)
            if np.isnan(m_cr[k_pos]) or float(s_cr.max()) == 0.0:
                m_cr[k_pos] = _BOT
            else:
                m_cr[k_pos] = _mean_wl(s_cr, w)
            m_f[k_pos] = _mean_wl(s_f, w)
            k_pos = (k_pos + 1) % H

        # apply survival
        pop[:n_trials] = np.where(survive[:, None], u, base)
        fitness[:n_trials] = np.where(survive, u_fit, parent_fit)

        # archive cap
        if archive.shape[0] > arc_cap:
            keep = np.asarray(rng.permutation(archive.shape[0]), dtype=np.int64)[:arc_cap]
            archive = archive[keep]

        if n_trials < N:
            break                                      # budget exhausted this generation

        # ---- LPSR (Eq 10; delete worst when N_{G+1} < N_G) ----
        n_new = int(round(((n_min - n_init) / max_nfes) * ev.nfes + n_init))
        n_new = max(n_min, min(n_new, N))
        if n_new < N:
            keep = np.argsort(fitness, kind="stable")[:n_new]
            pop = pop[keep].copy()
            fitness = fitness[keep].copy()
            N = n_new
            arc_cap = int(round(N * r_arc))
            if archive.shape[0] > arc_cap:
                sel = np.asarray(rng.permutation(archive.shape[0]), dtype=np.int64)[:arc_cap]
                archive = archive[sel]

    return _base.build_result(
        "lshade", problem, options, ev, start_time=start,
        params={"profile": _base.resolve_profile(options), "H": H, "N_init": n_init,
                "N_min": n_min, "r_arc": r_arc, "p": p_rate},
        notes="L-SHADE 2014 canonical (SHADE1.1 + LPSR); paper=Tanabe&Fukunaga 2014.",
    )
