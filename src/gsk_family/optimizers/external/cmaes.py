"""CMA-ES — standard (μ/μ_W, λ)-CMA-ES with rank-one **and rank-μ** covariance update.

Matches the algorithm and default strategy constants of Hansen's ``cmaes.m`` v3.61.beta
— the MATLAB oracle this baseline is validated against (dual-language program). This is
the modern textbook CMA-ES (Hansen 2016 tutorial, arXiv:1604.00772, Algorithm 1), NOT the
stripped 2001 rank-one-only original.

VARIANT HISTORY (this file has changed variant three times by user decision):
2026-07-20 IPOP-CMA-ES → 2026-07-21 pure 2001 rank-one-only → **2026-07-22 standard
rank-μ (this)**. The 2001 rank-one-only variant could not condition C fast enough at
D=100 on the ill-conditioned/rotated cec2017 functions (F12/F13/F15/F19), so σ ran away
and it diverged to ~1e10 where cmaes.m converges to ~1e5-1e7 — a variant gap, not a bug.
The rank-μ term fixes that (and makes the python↔MATLAB comparison like-for-like).

Constants — cmaes.m defaults, line-referenced in the code (all functions of n, μ_eff):
weights ``w_i = ln(λ/2+½) − ln i`` normalized to Σw=1; ``μ_eff = (Σw)²/Σw²``;
``c_c=(4+μ_eff/n)/(n+4+2μ_eff/n)``; ``c_σ=(μ_eff+2)/(n+μ_eff+3)``; ``c_1=2/((n+1.3)²+μ_eff)``;
``c_μ=min(1−c_1, 2(μ_eff−2+1/μ_eff)/((n+2)²+μ_eff))``; ``d_σ=1+2·max(0,√((μ_eff−1)/(n+1))−1)+c_σ``.
Update per cmaes.m: p_σ (Eq 4) → Heaviside h_σ → p_c (Eq 2) → C = (1−c_1−c_μ+(1−h_σ)c_1c_c(2−c_c))·C
+ c_1·p_c p_cᵀ + c_μ·Σ w_i y_i y_iᵀ (Eq 3) → σ ·= exp(min(1, (‖p_σ‖²/n−1)/2·c_σ/d_σ)) (Eq 5).

RNG: the only stochastic source is per-offspring ``z_k ~ N(0,I)``, drawn through the
family's ``RandomContext`` (offspring-major order) via :func:`._base.standard_normal`.
Publication-profile policy (freeze §9): initial mean = the fair-start uniform point;
initial σ = 0.3·mean(ub−lb); stop = fixed evaluation budget; bounds = Hansen cmaes.m
v3.61 **adaptive-penalty boundary handler** (cmaes.m:963-1036). Each generation the
out-of-box offspring ``arx`` are kept as sampled; a clipped copy ``arxvalid =
clip(arx, lb, ub)`` is what gets evaluated (so the budget and the best-ever always track
a FEASIBLE point); a per-coordinate weighted quadratic penalty ``Σ_i w_i·(arxvalid−arx)²``
is added to the SELECTION fitness only; and the mean/paths/C then recombine the UNREPAIRED
``arx`` sorted by the penalized fitness. This replaced the earlier resample-until-feasible→
clip policy (2026-07-23) to make the python↔MATLAB cec2017 comparison like-for-like on the
high-D composition cells (F22-F26), where clip-only was optimistically biased.

Numerical safeguard (non-paper): a TolXUp-style divergence RE-SEED. If ``σ·max(D)`` runs
past ``1e7·σ₀`` or the state goes non-finite, the strategy is re-seeded (fresh uniform
mean on the family stream, σ=σ₀, C=I, paths zeroed) and the run continues to the FULL
budget (run-to-budget, matching the MATLAB adapter). With the rank-μ update this trigger
is effectively inert — it existed to contain the rank-one-only divergence and now rarely
fires. ``params['restarts']`` records any re-seeds; ``max_restarts`` no longer caps the run.
"""

# VENDORED from 05-Human-Inspired-Family_Python_v0.1
#   src/human_inspired_family/optimizers/external/cmaes.py
#   source sha256: 75b8e702d91415ae
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

# Divergence-restart scale (App. A TolXUp-style): when the step scale grows past this
# multiple of the initial sigma the strategy has diverged and is re-seeded. 1e7 leaves
# an enormous margin over any healthy trajectory (whose sigma *shrinks* as it
# converges), so the trigger is inert on the fingerprinted cells and engages only in
# the restart-less blow-up (see the module docstring safeguard section).
_DIVERGE_FACTOR = 1e7
_COUNTING_RULE = (
    "GISR denominator = lambda offspring sampled per generation; numerator = "
    "offspring improving on the pre-generation incumbent. CMA-ES has no trial-vs-"
    "parent replacement, so this is the documented offspring-improving-on-incumbent "
    "proxy (master plan section 3.7). Error/convergence/diversity are exact."
)


def optimize(problem, options: OptimizerOptions) -> OptimizerResult:
    """Run standard (mu/mu_W, lambda)-CMA-ES on ``problem`` under the family contract.

    Rank-one AND rank-mu covariance update, matching Hansen ``cmaes.m`` v3.61.beta
    defaults (see the module docstring). Corrected 2026-07-28: this line previously
    said "the 2001 canonical CMA-ES", describing the rank-one-only intermediate state
    that was superseded on 2026-07-22 and contradicting the module docstring.
    """
    rng, ev, start = _base.start_run(problem, options)
    n = int(problem.dim)
    lb = np.asarray(problem.lb, dtype=np.float64).reshape(-1)
    ub = np.asarray(problem.ub, dtype=np.float64).reshape(-1)

    # ---- strategy constants — Hansen cmaes.m v3.61 defaults (rank-μ standard CMA-ES) ----
    # Matches the MATLAB oracle this port is validated against, line-for-line:
    # cmaes.m:762 weights, :767 mueff, :768 normalize, :220 cs, :222 damps, :224 ccum,
    # :225 ccov1, :226 ccovmu, :663 chiN. (μ/μ_W, λ)-CMA-ES with rank-one + rank-μ.
    lam = int(_base.param(options, "lambda", 4 + int(np.floor(3 * np.log(n)))))
    mu = int(_base.param(options, "mu", lam // 2))
    w = np.log(lam / 2.0 + 0.5) - np.log(np.arange(1, mu + 1))   # cmaes.m:762 (mu = lam/2)
    mueff = float(w.sum() ** 2 / np.sum(w ** 2))                 # cmaes.m:767 variance-eff. μ
    w = w / w.sum()                                             # cmaes.m:768 normalize → Σw = 1
    cc = (4.0 + mueff / n) / (n + 4.0 + 2.0 * mueff / n)        # cmaes.m:224 pc cumulation
    cs = (mueff + 2.0) / (n + mueff + 3.0)                      # cmaes.m:220 σ cumulation
    c1 = 2.0 / ((n + 1.3) ** 2 + mueff)                         # cmaes.m:225 rank-one rate
    cmu = min(1.0 - c1,
              2.0 * (mueff - 2.0 + 1.0 / mueff) / ((n + 2.0) ** 2 + mueff))  # cmaes.m:226 rank-μ
    damps = 1.0 + 2.0 * max(0.0, np.sqrt((mueff - 1.0) / (n + 1.0)) - 1.0) + cs  # cmaes.m:222
    chiN = np.sqrt(n) * (1.0 - 1.0 / (4.0 * n) + 1.0 / (21.0 * n * n))  # cmaes.m:663

    # ---- initial state (freeze §2.1, §9.1-9.2) --------------------------
    if options.initial_population is not None:
        # fair start: a uniform-random box point on the family seed stream
        xmean = np.asarray(options.initial_population, dtype=np.float64).reshape(-1, n)[0].copy()
    else:
        xmean = lb + np.asarray(rng.random(n), dtype=np.float64) * (ub - lb)
    sigma = float(_base.param(options, "sigma0", 0.3 * float(np.mean(ub - lb))))
    sigma_init = sigma  # divergence-stop reference scale (see _DIVERGE_FACTOR)
    C = np.eye(n)
    B = np.eye(n)
    D = np.ones(n)                                   # standard deviations (sqrt eigenvalues)
    BD = B * D                                        # columns scaled
    pc = np.zeros(n)
    ps = np.zeros(n)

    # ---- adaptive-penalty boundary-handler state (cmaes.m:578-625) --------------
    # The handler is active whenever any bound is finite (always true for the CEC box).
    # weights start at zero; scale stays ones (flgscale=0, never rescaled); every
    # coordinate is bounded; dfithist seeds the Δ-fitness history at 1.0 until the first
    # sensible IQR scale replaces it; iniphase/validfitval gate the initial weighting.
    xmean = np.clip(xmean, lb, ub)                    # cmaes.m:585 initial point into bounds
    xold = xmean.copy()                               # previous-gen mean (sign(xmean-xold))
    bnd_weights = np.zeros(n)                          # bnd.weights
    bnd_scale = np.ones(n)                             # bnd.scale (flgscale=0 -> ones)
    bnd_isbounded = np.ones(n, dtype=bool)            # bnd.isbounded (all coords, finite box)
    bnd_dfithist: list[float] = [1.0]                 # bnd.dfithist (bounded-length history)
    bnd_validfitval = False                           # bnd.validfitval
    bnd_iniphase = True                               # bnd.iniphase

    # freeze §9.5 amended 2026-07-21 (user-mandated speed): eigen-refresh cadence per
    # Hansen's own production cmaes.m (`mod(countiter, 1/ccov/N/10) < 1`) instead of
    # every generation. At D=10 the period is <1 -> still every generation; at D=100 it
    # is ~5 generations, cutting a 100x100 eigh from each of ~59k generations.
    # lazy eigendecomposition gap (purecma lazy_gap_evals / cmaes.m): refresh B,D every
    # ~0.5/((c1+cmu)·n) generations so eig costs ≈ the per-generation update in ≥20-D.
    eig_every = int(_base.param(
        options, "eig_every_gen", max(1, int(0.5 / ((c1 + cmu) * n)))))

    # ---- loop-invariant hoists (2026-07-22 speed pass; bit-identical) -----------
    # Every value below is exactly the scalar/array the loop previously recomputed
    # per generation, hoisted with the SAME association order, so each per-
    # generation float op sequence is unchanged bit-for-bit.
    sq_cs = np.sqrt(cs * (2.0 - cs) * mueff)          # ps path coefficient
    sq_cc = np.sqrt(cc * (2.0 - cc) * mueff)          # pc path coefficient
    hsig_thresh = 1.4 + 2.0 / (n + 1.0)               # Heaviside threshold
    hsig_fix = c1 * cc * (2.0 - cc)                   # (1-hsig) variance-loss term
    c_decay = 1.0 - c1 - cmu                          # C decay base
    maxdx = (ub - lb) / 2.0                           # cmaes.m maxdx clamp bound
    rank_flat = min(mu + 1, lam) - 1                  # App. A flat-fitness rank
    # np.triu(C, k) is where(tri(n, n, k-1, bool), 0, C): precompute the two boolean
    # masks once so the eig-refresh symmetrization skips rebuilding them every call
    # (np.where with the same mask/operands returns bit-identical output).
    _tri_m1 = np.tri(n, n, -1, dtype=bool)            # mask for np.triu(C)
    _tri_m0 = np.tri(n, n, 0, dtype=bool)             # mask for np.triu(C, 1)
    recorder = _base.make_recorder(problem, options, _COUNTING_RULE)
    prev_best = float("inf")
    first = True
    n_restarts = 0
    max_restarts = int(_base.param(options, "max_restarts", 20))
    termination = "max_evaluations"
    g = 0
    while not ev.is_exhausted():
        # ---- divergence restart (non-paper numerical safeguard; module docstring) ----
        # On a pathological cell sigma/C can still overflow (the App. A step-size
        # inflation compounding on a hard rotated/ill-conditioned landscape) until the
        # state goes non-finite and the offspring batch turns all-NaN. When the step
        # scale has diverged, re-seed the strategy state (fresh uniform mean on the
        # family stream, sigma0, C=I, paths zeroed, lambda unchanged; boundary-handler
        # state reset below) and keep optimizing to the full budget. Healthy runs (sigma
        # shrinks) never approach the trigger, so the fingerprint cells stay bit-identical.
        step_scale = sigma * float(D.max())
        if (
            not np.isfinite(step_scale)
            or step_scale > _DIVERGE_FACTOR * sigma_init
            or not np.all(np.isfinite(xmean))
        ):
            # Divergence: re-seed the strategy state (fresh uniform mean, sigma0, C=I,
            # paths zeroed, lambda unchanged) and KEEP optimizing to the full budget.
            # P-3 fix 2026-07-22 (user decision, run-to-budget): the prior code broke out
            # of the loop once n_restarts hit a cap, abandoning 60-88% of the budget with
            # termination='divergence' — a run-to-budget protocol violation that also broke
            # comparability with the MATLAB adapter (MaxFunEvals is a TOTAL cap; cmaes.m
            # keeps running). Every re-seed is followed by a budget-consuming generation, so
            # the while(not exhausted) guard bounds the loop; n_restarts is recorded only.
            xmean = lb + np.asarray(rng.random(n), dtype=np.float64) * (ub - lb)
            sigma = sigma_init
            C = np.eye(n)
            B = np.eye(n)
            D = np.ones(n)
            BD = B * D
            pc = np.zeros(n)
            ps = np.zeros(n)
            # a re-seed is a fresh cmaes start: reset the boundary-handler state too
            xold = xmean.copy()
            bnd_weights = np.zeros(n)
            bnd_dfithist = [1.0]
            bnd_validfitval = False
            bnd_iniphase = True
            n_restarts += 1
        # ---- (A) sample λ offspring; evaluate the BOX-REPAIRED points (budget-exact) ---
        # cmaes.m adaptive-penalty handler: the offspring arx = X are kept out-of-box for
        # the mean/covariance update; only a clipped copy arxvalid = clip(X, lb, ub) is
        # evaluated, so the budget and the best-ever always track a FEASIBLE point. No
        # resample loop (removed 2026-07-23) — X is used exactly as sampled.
        n_off = min(lam, ev.remaining())
        Z = np.asarray(_base.standard_normal(rng, (n_off, n)), dtype=np.float64)
        X = xmean + sigma * (Z @ BD.T)                    # arx — kept out-of-box (Eq. 1)
        if not np.all(np.isfinite(X)):
            # sigma/C overflow made an offspring non-finite: skip this batch (no budget
            # spent) and let the top-of-loop guard re-seed. clip cannot rescue a NaN.
            xmean = np.full(n, np.nan)  # force the restart trigger
            continue
        Xvalid = np.clip(X, lb, ub)                        # arxvalid — the evaluated feasible copy
        fraw = ev.evaluate(Xvalid)                         # fitness.raw at arxvalid; best-ever is feasible
        # data-parity telemetry (§3.7): population = the λ feasible offspring; GISR proxy =
        # offspring improving on the pre-generation incumbent (raw feasible fitness).
        if first:
            recorder.record_initial(Xvalid, ev.best_fitness, ev.nfes)
            first = False
        else:
            recorder.record_generation(
                Xvalid, best_fitness=ev.best_fitness, nfes=ev.nfes, generated=int(n_off),
                accepted_improved=int(np.count_nonzero(fraw < prev_best)), fitness=fraw,
            )
        prev_best = ev.best_fitness
        if n_off < lam:
            break  # partial final generation: best is captured, no distribution update

        # ---- (A2) adaptive-penalty boundary handler (cmaes.m:963-1036) --------------
        # Builds the per-offspring penalty added to the SELECTION fitness fsel. The mean,
        # paths and C then recombine the UNREPAIRED arx (X) sorted by fsel — the box repair
        # never enters the distribution update, only its selection ranking.
        countiter = g + 1  # cmaes.m increments countiter at the loop top (:864); g is pre-increment here
        diagC = np.diag(C)
        mean_diagC = float(diagC.mean())
        # (1) IQR Δ-fitness scale (cmaes.m:1000-1013). numpy 'linear' percentile stands in
        #     for myprctile's midpoint interpolation (cross-language, not bit-exact by design).
        q25, q75 = np.percentile(fraw, [25.0, 75.0])
        val = (q75 - q25) / n / mean_diagC / (sigma * sigma)
        if not np.isfinite(val):
            val = max(bnd_dfithist)                        # non-finite range -> largest seen
        elif val == 0.0:
            val = min(v for v in bnd_dfithist if v > 0.0)  # all points out of bounds
        elif not bnd_validfitval:
            bnd_dfithist = []                              # first sensible value: drop the seed 1.0
            bnd_validfitval = True
        if len(bnd_dfithist) < 20.0 + 3.0 * n / lam:       # cmaes.m:1017 bounded history length
            bnd_dfithist.append(val)
        else:
            bnd_dfithist.pop(0)
            bnd_dfithist.append(val)
        # (2) which coordinates of the mean are out of bounds (xintobounds ti: +1 above ub,
        #     -1 below lb, 0 inside)
        tx = np.clip(xmean, lb, ub)
        ti = np.zeros(n)
        ti[xmean < lb] = -1.0
        ti[xmean > ub] = 1.0
        any_ti = bool(np.any(ti != 0.0))
        # (3) set initial weights while in the iniphase (cmaes.m:1025-1039)
        if bnd_iniphase and any_ti:
            bnd_weights[bnd_isbounded] = 2.0002 * float(np.median(bnd_dfithist))
            dd = diagC / mean_diagC                        # flgscale==0: remove mean scaling
            bnd_weights[bnd_isbounded] = bnd_weights[bnd_isbounded] / dd[bnd_isbounded]
            if bnd_validfitval and countiter > 2:
                bnd_iniphase = False
        # (4) increase weights where the mean drifts far out AND keeps moving out (cmaes.m:1042-1054)
        if any_ti:
            txd = xmean - tx
            far = np.abs(txd) > 3.0 * max(1.0, np.sqrt(n) / mueff) * sigma * np.sqrt(diagC)
            idx = (ti != 0.0) & far & (np.sign(txd) == np.sign(xmean - xold))
            bnd_weights[idx] = (1.2 ** min(1.0, mueff / 10.0 / n)) * bnd_weights[idx]
        # (5) per-offspring penalty (bnd.weights/bnd.scale)·(arxvalid-arx)² and fsel (cmaes.m:1063-1065)
        penalty = ((bnd_weights / bnd_scale) * (Xvalid - X) ** 2).sum(axis=1)
        fsel = fraw + penalty

        # ---- (B) select + weighted recombination (normalized weights, Σw = 1) ----
        g += 1
        order_full = np.argsort(fsel, kind="stable")   # penalized (selection) ranking; used by (H)
        order = order_full[:mu]
        xold = xmean
        Xsel = X[order]                            # arx (UNREPAIRED) — cmaes.m:1088 recombines arx
        xmean = Xsel.T @ w
        zmean = Z[order].T @ w                     # == D^-1 B' (xmean-xold)/σ  (cmaes.m:1089)

        # ---- (C) conjugate evolution path + Heaviside hσ (cmaes.m:1099-1100) ----
        ps = (1.0 - cs) * ps + sq_cs * (B @ zmean)
        ps_norm = float(np.linalg.norm(ps))
        hsig = ps_norm / np.sqrt(1.0 - (1.0 - cs) ** (2 * g)) / chiN < hsig_thresh

        # ---- (D) covariance evolution path (cmaes.m:1109-1110) ----------
        pc = (1.0 - cc) * pc + (hsig * sq_cc) * (BD @ zmean)

        # ---- (E) rank-one + rank-μ covariance update (cmaes.m:1209) -----
        # artmp = the μ selected steps y_i = (x_{i:λ} − xold)/σ (== BD·z_i).
        artmp = (Xsel - xold) / sigma
        C = ((c_decay + (1.0 - hsig) * hsig_fix) * C                     # decay + hσ variance fix
             + c1 * np.outer(pc, pc)                                     # rank-one
             + cmu * (artmp.T * w) @ artmp)                             # rank-μ: Σ w_i y_i y_iᵀ

        # ---- (F) CSA step-size (cmaes.m:1242 — DEFAULT ||ps||/chiN form, exp capped) ----
        # ALIGNED 2026-07-24 (match-review fork closure): this port previously executed the
        # ||ps||²/N "future variant" (cmaes.m:1239, Dirk Arnold 2000) — a branch cmaes.m SHIPS
        # but DISABLES (flg_future_setting=0, cmaes.m:230). The oracle therefore runs the
        # classic chiN form below; the two differ only at second order (O(1/4N) equilibrium
        # offset; 0/116 tail flags empirically), but the port's claim is "matches the EXECUTED
        # cmaes.m", so the executed branch it is. See match_review_5_externals.md.
        sigma = sigma * float(np.exp(min(1.0, (ps_norm / chiN - 1.0) * cs / damps)))

        # ---- (F2) maxdx step-size clamp (cmaes.m:602-605, 1378) ---------
        # Keep every coordinate's std σ·√C_ii within half its box width. Without this, on
        # hard high-D cells (F12/13/15/19 D=100) σ runs away → offspring all clip to the box
        # corners → flat fitness → the (H) kick inflates σ further → overflow to NaN. This is
        # the cmaes.m safeguard that makes the divergence/TolUpX trigger effectively inert (M-3).
        sqrtdiagC = np.sqrt(np.maximum(C.diagonal(), 1e-300))
        if np.any(sigma * sqrtdiagC > maxdx):
            sigma = float(np.min(maxdx / sqrtdiagC))

        # ---- (G) lazy eigen-refresh of B, D from C ---------------------
        if g % eig_every == 0:
            # enforce symmetry == np.triu(C) + np.triu(C, 1).T with the tri masks
            # precomputed (identical where/add ops -> bit-identical result)
            C = np.where(_tri_m1, 0.0, C) + np.where(_tri_m0, 0.0, C).T
            eigvals, B = np.linalg.eigh(C)
            ev_max = eigvals.max()
            ev_min = eigvals.min()
            if ev_max > 1e14 * max(ev_min, 1e-300):
                tmp = ev_max / 1e14 - ev_min
                C = C + tmp * np.eye(n)
                eigvals = eigvals + tmp
            eigvals = np.maximum(eigvals, 0.0)
            D = np.sqrt(eigvals)
            BD = B * D

        # ---- (H) minimal-variance / stagnation safeguard (App. A) -------
        # P-1 fix 2026-07-22 (user decision): the flat-fitness test now follows Hansen &
        # Ostermeier 2001 App. A (p.192) exactly — compare the BEST against the SORTED
        # (min(mu+1, lambda))-th best via the full ranking. The prior code indexed the
        # UNSORTED fitness at position min(mu,n_off)-1 (an arbitrary offspring, not the
        # ranked one) and used rank mu instead of mu+1 — two errors that fired the 1.4x
        # sigma kick spuriously (1,505x in the fingerprint cell), inflating sigma on
        # multimodal cells until the divergence guard tripped and abandoned the budget.
        # column index: previously col = 1 + int(g % n); (col - 1) % n == g % n exactly.
        if (
            sigma * float(D.min()) < 1e-15
            or fsel[order_full[0]] == fsel[order_full[rank_flat]]   # cmaes.m:1427 uses fitness.sel
            or np.array_equal(xmean, xmean + 0.2 * sigma * BD[:, g % n])
        ):
            sigma = 1.4 * sigma

    return _base.build_result(
        "cmaes", problem, options, ev, start_time=start,
        termination=termination,
        params={"profile": _base.resolve_profile(options), "lambda": lam, "mu": mu,
                "sigma0": float(0.3 * float(np.mean(ub - lb))), "mueff": mueff,
                "cc": cc, "c1": c1, "cmu": cmu, "cs": cs, "damps": damps,
                "restarts": n_restarts, "max_restarts": max_restarts},
        notes="standard (μ/μ_W,λ)-CMA-ES, rank-one+rank-μ; matches Hansen cmaes.m v3.61 constants.",
    )
