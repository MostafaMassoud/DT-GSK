"""LSHADE-SPACMA — aligned to the authors' official MATLAB (LSHADE_SPACMA_1.0).

Mohamed, Hadi, Fattouh & Jambi 2017 (CEC), DOI 10.1109/CEC.2017.7969307. Originally
ported paper-first from ``reference_code/.../lshade_spacma/VERSION_FREEZE.md``; on
2026-07-20 (user-directed, to close the systematic D-scaling gap vs the paper's
tables) the port was re-aligned mechanism-by-mechanism to the official code at
``reference_code/external_baseline_algorithms/LSHADE_SPACMA_1.0/LSHADE_SPACMA.m``,
which supersedes the paper prose wherever the two disagree. Official-code semantics
now implemented (MATLAB line refs):

  • **CR memory = weighted Lehmer mean** (l.265; the paper prose says arithmetic —
    the proven F3 bistable-CR root cause, fixed earlier the same day).
  • **F memory updates in BOTH SPA phases** (l.259 is unconditional); phase 1 draws
    ``F ~ U(0.45, 0.55)`` (l.151) while the memory still learns; phase 2 draws
    ``F ~ Cauchy(M_F, 0.1)`` (l.159). No memory freeze/seed at the phase switch.
  • **FCP is an H=5 memory array** (``memory_1st_class_percentage``, l.100) selected
    per individual through the SAME ``mem_rand_index`` as CR/F (l.171) against a
    separate uniform draw; update ``slot ← 0.8·slot + 0.2·(Σdif₁/(Σdif₁+Σdif₂))``
    with clamp [0.2, 0.8] AFTER (l.269–271), only while hybridization is active.
  • **Population-coupled CMA** (l.311–348): ``xmean`` is the weighted mean of the
    CURRENT (post-selection, post-LPSR) population's best-μ — the CMA has no private
    trajectory. ``σ`` starts at **0.5** with ``xmean = rand(D,1)`` in the unit cube
    (l.103–104; the first adaptation step then jumps to population scale — the
    official transient). ``μ/weights/μ_eff`` refresh ONLY at LPSR shrink events
    (l.303–308) while ``cc, cs, c1, cμ, damps`` stay FROZEN at their init-N values
    (l.112–116) — the official mixed convention. ``hsig`` uses the squared-norm form
    with the ``2·nfes/N`` exponent (l.321). Eigen-refresh is LAZY on the
    ``nfes − eigeneval > N/((c1+cμ)·D·10)`` cadence (l.336), with no eigenvalue
    clamps and no σ floor.
  • **Hybridization is mortal** (l.199–202, 339–342): non-real CMA donors or a
    non-finite C kill the CMA permanently (flag→0, every individual becomes class 1
    forever); the killing generation is SKIPPED without evaluation (MATLAB
    ``continue``). No restarts. (Family-substrate note: MATLAB's complex donors
    arise from ``sqrt(negative eigenvalue)``; numpy's ``eigh`` keeps values real, so
    the equivalent trigger here is any negative eigenvalue at refresh, plus a
    non-finite-donor check before evaluation — the benchmark adapter, unlike
    MATLAB's mex, refuses NaN populations.)
  • **Ties favor the parent** (l.247: ``min([fitness, children], [], 2)`` keeps the
    parent on equality); success/archive/memory use the same strict inequality.
  • **Archive dedup** (updateArchive.m): duplicates removed on every insert, then
    random trim to ``round(1.4·N)``.

Constants (l.53–61): ``NP=18D``, ``N_min=4``, ``p=0.11``, ``arc_rate=1.4``, ``H=5``,
memories init 0.5, FCP init 0.5, L_Rate 0.8, ``max_nfes=10000·D``.

Family-contract deviations (deliberate, documented): randomness comes from the
family ``RandomContext`` stream (draws made for every row regardless of the class
split so the draw count is split-independent); the final generation is truncated to
the remaining budget (family budget-exactness; MATLAB evaluates the full batch and
discards overflow); midpoint bound repair per boundConstraint.m (identical rule).
"""

# VENDORED from 05-Human-Inspired-Family_Python_v0.1
#   src/human_inspired_family/optimizers/external/lshade_spacma.py
#   source sha256: b9379d7a03551edd
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

_BOT = np.nan  # ⊥ terminal value for M_CR (MATLAB -1; frozen slot -> CR=0)
_COUNTING_RULE = (
    "GISR denominator = trial vectors generated per generation (= NP_g; both the "
    "DE and CMA branches are evaluated in one unified U_G, Fig.1 l.22); numerator = "
    "trials with f(u) < f(x_i) (strict). Native shared-population replacement rate."
)


def _mean_wl(s: np.ndarray, w: np.ndarray) -> float:
    """Weighted Lehmer (power-2) mean — official update for BOTH M_F and M_CR
    (LSHADE_SPACMA.m l.259 and l.265)."""
    num = float(np.sum(w * s * s))
    den = float(np.sum(w * s))
    return num / den if den != 0.0 else 0.0


def _cma_weights(mu_float: float) -> tuple[np.ndarray, float, int]:
    """Official recombination weights: ``log(mu+1/2) - log(1:mu)`` with the
    PRE-floor ``mu = N/2`` inside the log and the range truncated at floor(mu)
    (MATLAB l.105-109 / l.304-308), normalized; returns (weights, mu_eff, mu)."""
    mu = int(np.floor(mu_float))
    w_raw = np.log(mu_float + 0.5) - np.log(np.arange(1, mu + 1))
    w = w_raw / w_raw.sum()
    mueff = float(w.sum() ** 2 / np.sum(w * w))  # == 1/sum(w^2) after normalize
    return w, mueff, mu


def optimize(problem, options: OptimizerOptions) -> OptimizerResult:
    """Run LSHADE-SPACMA (official-MATLAB semantics) under the family contract."""
    rng, ev, start = _base.start_run(problem, options)
    n = int(problem.dim)
    lb = np.asarray(problem.lb, dtype=np.float64).reshape(-1)
    ub = np.asarray(problem.ub, dtype=np.float64).reshape(-1)
    max_nfes = int(problem.max_nfes)
    half = max_nfes / 2.0                                    # SPA phase split

    H = int(_base.param(options, "H", 5))
    n_init = int(round(18.0 * n))                            # NP = 18·D
    n_min = 4
    r_arc = float(_base.param(options, "r_arc", 1.4))
    p_rate = float(_base.param(options, "p", 0.11))
    l_rate = float(_base.param(options, "l_rate", 0.8))      # FCP retention (L_Rate)
    fcp_lo, fcp_hi = 0.2, 0.8

    # ---- initialization (fair start on the family stream) ----------------
    if options.initial_population is not None:
        pop = np.asarray(options.initial_population, dtype=np.float64).reshape(-1, n)[:n_init].copy()
    else:
        pop = lb + np.asarray(rng.random((n_init, n)), dtype=np.float64) * (ub - lb)
    N = pop.shape[0]
    fitness = ev.evaluate(pop)

    m_cr = np.full(H, 0.5)
    m_f = np.full(H, 0.5)
    m_fcp = np.full(H, 0.5)                                  # memory_1st_class_percentage
    k_pos = 0
    archive = np.empty((0, n), dtype=np.float64)
    arc_cap = int(round(n_init * r_arc))

    # ---- official CMA state (l.102-127): unit-cube mean, sigma=0.5, frozen consts ----
    sigma = 0.5
    xmean = np.asarray(rng.random(n), dtype=np.float64)      # rand(D,1) in [0,1]^D
    w_cur, mueff, _mu = _cma_weights(N / 2.0)
    cc = (4.0 + mueff / n) / (n + 4.0 + 2.0 * mueff / n)     # frozen at init-N values
    cs = (mueff + 2.0) / (n + mueff + 5.0)
    c1 = 2.0 / ((n + 1.3) ** 2 + mueff)
    cmu = min(1.0 - c1, 2.0 * (mueff - 2.0 + 1.0 / mueff) / ((n + 2.0) ** 2 + mueff))
    damps = 1.0 + 2.0 * max(0.0, np.sqrt((mueff - 1.0) / (n + 1.0)) - 1.0) + cs
    pc = np.zeros(n)
    ps = np.zeros(n)
    B = np.eye(n)
    Dvec = np.ones(n)
    C = np.eye(n)
    invsqrtC = np.eye(n)
    eigeneval = 0
    chiN = np.sqrt(n) * (1.0 - 1.0 / (4.0 * n) + 1.0 / (21.0 * n * n))
    hyb = True                                               # Hybridization_flag

    recorder = _base.make_recorder(problem, options, _COUNTING_RULE)
    recorder.record_initial(pop, ev.best_fitness, ev.nfes)

    while not ev.is_exhausted():
        phase2 = ev.nfes > half                              # MATLAB: phase1 while nfes<=max/2
        n_trials = min(N, ev.remaining())                    # budget-exact final generation
        idx = np.arange(n_trials)

        # ---- control-parameter draws (r_i -> CR -> F -> class ratio) ----
        r_idx = np.asarray(rng.integers(0, H, n_trials), dtype=np.int64)
        cr = np.asarray(_base.normal(rng, 0.0, 1.0, n_trials)) * 0.1 + m_cr[r_idx]
        np.clip(cr, 0.0, 1.0, out=cr)
        cr[np.isnan(m_cr[r_idx])] = 0.0                      # ⊥ slot -> CR=0 (l.144-145)
        if not phase2:
            f = 0.45 + 0.1 * np.asarray(rng.random(n_trials), dtype=np.float64)  # l.151
        else:
            f = np.asarray(_base.cauchy(rng, 0.0, 1.0, n_trials)) * 0.1 + m_f[r_idx]  # l.159
            for _ in range(100):                             # resample while F <= 0
                bad = f <= 0.0
                if not bad.any():
                    break
                f[bad] = np.asarray(_base.cauchy(rng, 0.0, 1.0, int(bad.sum()))) * 0.1 + m_f[r_idx[bad]]
            f = np.minimum(f, 1.0)

        # ---- class split (l.171-174): slot FCP >= ratio -> class 1 (LSHADE) ----
        ratio = np.asarray(rng.random(n_trials), dtype=np.float64)
        is_lshade = m_fcp[r_idx] >= ratio
        if not hyb:
            is_lshade = np.ones(n_trials, dtype=bool)        # CMA dead: all class 1

        # ---- Engine A donors: current-to-pbest/1 + archive (all rows) ----
        order = np.argsort(fitness, kind="stable")
        p_num = max(2, int(round(N * p_rate)))
        pbest = order[:p_num][np.asarray(rng.integers(0, p_num, n_trials), dtype=np.int64)]
        r1 = np.asarray(rng.integers(0, N - 1, n_trials), dtype=np.int64)
        r1[r1 >= idx] += 1                                   # r1 != i, uniform (gnR1R2)
        pa = np.vstack([pop, archive]) if archive.shape[0] else pop
        npa = pa.shape[0]
        r2 = np.asarray(rng.integers(0, npa, n_trials), dtype=np.int64)
        for _ in range(100):                                 # r2 != i and != r1 (gnR1R2)
            clash = (r2 == idx) | (r2 == r1)
            if not clash.any():
                break
            r2[clash] = np.asarray(rng.integers(0, npa, int(clash.sum())), dtype=np.int64)
        base = pop[:n_trials]
        v_de = base + f[:, None] * (pop[pbest] - base) + f[:, None] * (pop[r1] - pa[r2])

        # ---- Engine B donors: v = m + σ·B·(D∘z) (l.194), all rows ----
        Z = np.asarray(_base.standard_normal(rng, (n_trials, n)), dtype=np.float64)
        v_cma = xmean + sigma * ((Z * Dvec) @ B.T)

        # ---- MATLAB l.199-202: non-real CMA donors kill hybridization and the
        # generation is skipped WITHOUT evaluation (continue). numpy equivalent:
        # non-finite donors on any selected class-2 row.
        if hyb and not np.all(np.isfinite(v_cma[~is_lshade])):
            hyb = False
            continue

        v = np.where(is_lshade[:, None], v_de, v_cma)

        # ---- boundary correction: midpoint with parent (boundConstraint.m) ----
        v = np.where(v < lb, (lb + base) / 2.0, v)
        v = np.where(v > ub, (ub + base) / 2.0, v)

        # ---- unified binomial crossover on ALL trials (l.208-211) ----
        cross = np.asarray(rng.random((n_trials, n)), dtype=np.float64) <= cr[:, None]
        j_rand = np.asarray(rng.integers(0, n, n_trials), dtype=np.int64)
        cross[idx, j_rand] = True
        u = np.where(cross, v, base)

        # ---- evaluate unified U_G + selection: ties favor the PARENT (l.247) ----
        u_fit = ev.evaluate(u)
        parent_fit = fitness[:n_trials]
        improved = u_fit < parent_fit                        # strict: success/archive/select
        n_improved = int(np.count_nonzero(improved))

        recorder.record_generation(
            pop, best_fitness=ev.best_fitness, nfes=ev.nfes, generated=int(n_trials),
            accepted_improved=n_improved, fitness=fitness,
        )

        gain = parent_fit - u_fit                            # dif = |f_p - f_c| on improved

        # ---- memory updates (one shared slot k_pos per successful generation) ----
        if n_improved:
            # archive first (l.245): parents of strictly-better children, deduped
            archive = np.vstack([archive, base[improved]])
            archive = np.unique(archive, axis=0)             # updateArchive.m dedup
            if archive.shape[0] > arc_cap:
                keep = np.asarray(rng.permutation(archive.shape[0]), dtype=np.int64)[:arc_cap]
                archive = archive[keep]

            df = gain[improved]
            wts = df / df.sum() if df.sum() > 0 else np.full(df.size, 1.0 / df.size)
            s_cr = cr[improved]
            s_f = f[improved]
            m_f[k_pos] = _mean_wl(s_f, wts)                  # BOTH phases (l.259)
            if np.isnan(m_cr[k_pos]) or float(s_cr.max()) == 0.0:
                m_cr[k_pos] = _BOT                           # l.262-263 (sticky ⊥)
            else:
                m_cr[k_pos] = _mean_wl(s_cr, wts)            # l.265 (weighted Lehmer)
            if hyb:                                          # FCP slot (l.268-272)
                w1 = float(np.sum(gain[improved & is_lshade]))
                w2 = float(np.sum(gain[improved & ~is_lshade]))
                if w1 + w2 > 0.0:
                    slot = m_fcp[k_pos] * l_rate + (1.0 - l_rate) * (w1 / (w1 + w2))
                    m_fcp[k_pos] = min(fcp_hi, max(fcp_lo, slot))
            k_pos = (k_pos + 1) % H

        # apply selection (parent survives ties)
        pop[:n_trials] = np.where(improved[:, None], u, base)
        fitness[:n_trials] = np.where(improved, u_fit, parent_fit)

        if n_trials < N:
            break                                            # budget exhausted mid-generation

        # ---- LPSR (l.279-309): shrink pop; refresh ONLY mu/weights/mueff ----
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
            w_cur, mueff, _mu = _cma_weights(N / 2.0)        # cc/cs/c1/cmu/damps stay frozen

        # ---- CMA adaptation from the population's best-μ (l.311-348) ----
        if hyb:
            mu = w_cur.size
            sel = np.argsort(fitness, kind="stable")[:mu]
            xold = xmean
            xmean = w_cur @ pop[sel]
            y = (xmean - xold) / sigma
            ps = (1.0 - cs) * ps + np.sqrt(cs * (2.0 - cs) * mueff) * (invsqrtC @ y)
            denom = 1.0 - (1.0 - cs) ** (2.0 * ev.nfes / N)
            hsig = 1.0 if float(np.sum(ps * ps)) / denom / n < 2.0 + 4.0 / (n + 1.0) else 0.0
            pc = (1.0 - cc) * pc + hsig * np.sqrt(cc * (2.0 - cc) * mueff) * y
            ysel = (pop[sel] - xold) / sigma                 # artmp (l.326)
            C = (
                (1.0 - c1 - cmu) * C
                + c1 * (np.outer(pc, pc) + (1.0 - hsig) * cc * (2.0 - cc) * C)
                + cmu * ((ysel.T * w_cur) @ ysel)
            )
            sigma = sigma * float(np.exp((cs / damps) * (np.linalg.norm(ps) / chiN - 1.0)))
            # lazy eigen refresh (l.336-346): nfes-based cadence, no clamps, mortal
            if ev.nfes - eigeneval > N / (c1 + cmu) / n / 10.0:
                eigeneval = ev.nfes
                C = np.triu(C) + np.triu(C, 1).T
                if not np.all(np.isfinite(C)):
                    hyb = False                              # l.339-342 permanent kill
                else:
                    eigvals, B_new = np.linalg.eigh(C)
                    if np.any(eigvals < 0.0):
                        hyb = False                          # MATLAB: complex D -> dead donors
                    else:
                        B = B_new
                        Dvec = np.sqrt(eigvals)
                        invsqrtC = (B / Dvec) @ B.T

    return _base.build_result(
        "lshade-spacma", problem, options, ev, start_time=start,
        params={"profile": _base.resolve_profile(options), "H": H, "N_init": n_init,
                "N_min": n_min, "r_arc": r_arc, "p": p_rate, "l_rate": l_rate,
                "FCP_final": [float(x) for x in m_fcp], "hybridization_alive": bool(hyb)},
        notes=("LSHADE-SPACMA aligned to official MATLAB LSHADE_SPACMA_1.0 "
               "(population-coupled CMA, H-slot FCP, mortal hybridization); "
               "paper=Mohamed,Hadi,Fattouh,Jambi 2017."),
    )
