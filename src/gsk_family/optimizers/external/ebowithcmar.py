"""EBOwithCMAR — source-faithful, Kumar, Misra & Singh 2017 (CEC), DOI 10.1109/CEC.2017.7969524.

The **CEC-2017 single-objective bound-constrained winner**. Its paper is LOW-confidence
(CMA machinery delegated to a citation; several equations degenerate), so this is a
**code-first port of the official MATLAB** staged in
``reference_code/external_baseline_algorithms/ebowithcmar/`` (EBO.m, EBO_BIN.m, Scout.m,
init_cma_par.m, LS2.m, han_boun.m, updateArchive.m, gnR1R2.m, bestt.m, Introd_Par.m).
Every UNRESOLVED item in the VERSION_FREEZE record is resolved by the MATLAB (tier-1).

**Dual-population hybrid**, run under the UMOEAs-II multi-operator framework:
  • **EA_1 (EBO / DE engine)** — ``PS1 = 18·D`` with **LPSR** toward 4; two mutation ops
    (criss-cross ``op_1`` / towards-best ``op_2``) chosen per-individual by an adaptive
    ``probDE1``; per-individual F (Cauchy memory + a tan-scheduled override in the first
    half), and a **per-dimension crossover rate** shaped by adaptive ``CR`` and ``T``
    (a circularly-shifted decaying-exponential profile). Success-history memories for
    F/CR/T/freq (weighted-Lehmer). Towards-best index via ``bestt`` (min of D random ranks).
  • **EA_2 (CMAR / CMA-ES "Scout")** — ``PS2 = 4+⌊3·ln D⌋``; modern CMA-ES (rank-one +
    rank-μ + CSA) with the paper's **custom bell samplers** ``M1/M2`` (asin-based variates,
    50/50) instead of Gaussian, and fitness-proportional recombination weights. Boundary
    handling only after 50 % of the budget (reflection ``2·lb − x``).

Per outer iteration: an adaptive ``[prob_DE, prob_CMAR]`` (from normalized quality +
diversity of the two sub-populations) gates which engine(s) run; a **cycle** of length
``CS`` recomputes the probabilities at ``CS+1`` and **shares information** at ``2·CS``
(EBO-best → reseed CMAR; CMAR-best → inject into EA_1). In the last 25 % of the budget a
**SQP local search** (``scipy`` SLSQP, the paper's ``fmincon('sqp')``) refines the best,
with a self-adjusting ``prob_ls`` (0.1 on success / 0.01 on failure).

Fidelity notes: the custom ``asin``/tan variates are reproduced exactly on the family's
uniform stream (they ARE the algorithm's sampling, not a Gaussian substitute); the
CMA fitness-weights (best→smallest weight, ~uniform on CEC-2017) and the memory-index
off-by-one between F/CR and T/freq are replicated verbatim from EBO.m. The reported best
is the algorithm's **feasible** ``bestx`` (the MATLAB gates the incumbent on bounds even
though out-of-bounds CMA samples are still evaluated in the first half).

Suites: cec2017 (D=10/30/50/100) + cec2011. Family RNG (``_base``) + budget-exact (every
batch truncated to the remaining budget) + native GISR telemetry from BOTH engines (§3.7).
"""

# VENDORED from 05-Human-Inspired-Family_Python_v0.1
#   src/human_inspired_family/optimizers/external/ebowithcmar.py
#   source sha256: 34864972298bf886
# Imported 2026-07-26 so external SOTA baselines can be run natively under this
# project's harness (identical objective code, seed schedule, budget, protocol)
# instead of citing published tables. ONLY the import namespace was rewritten;
# the algorithm body is byte-faithful to the source, which carries project 05's
# parity records under docs/development/matlab_parity/.
# NOT part of the seven-method GSK-family statistical panel.
# Do not edit the algorithm body here -- amend at the source and re-vendor.

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from gsk_family.types import OptimizerOptions, OptimizerResult

from . import _base

_SQRT_PI = float(np.sqrt(np.pi))
_COUNTING_RULE = (
    "GISR denominator = trial vectors generated per phase (EA_1: PS1 EBO trials, strict "
    "f(u)<f(x) replacements; EA_2: PS2 CMAR samples, improving on the pre-phase incumbent). "
    "Both dual-population engines contribute per-generation records; the terminal SQP local "
    "search advances nfes/best-so-far only (captured in the convergence trace)."
)


class _StopLS(Exception):
    """Unwind the SQP call once its budget (or the global budget) is spent."""


def _cs_gmax(n: int) -> tuple[int, int]:
    """Cycle length CS and generation cap Gmax by dimension (Introd_Par.m; code values)."""
    if n == 10:
        return 50, 2163
    if n == 30:
        return 100, 2745
    if n == 50:
        return 150, 3022
    return 150, 3401


def _asin_bell(rng, shape) -> np.ndarray:
    """``sqrt(pi)·(asin(U1) − asin(U2))`` — the symmetric asin-difference bell (EBO.m/Scout.m)."""
    u1 = np.asarray(rng.random(shape), dtype=np.float64)
    u2 = np.asarray(rng.random(shape), dtype=np.float64)
    return _SQRT_PI * (np.arcsin(u1) - np.arcsin(u2))


def _lehmer_w(s: np.ndarray, w: np.ndarray) -> float:
    """Weighted Lehmer (power-2) mean: Σw·s² / Σw·s (EBO.m memory update)."""
    den = float(np.sum(w * s))
    return float(np.sum(w * s * s)) / den if den != 0.0 else 0.0


# ---------------------------------------------------------------------------
# CMA-ES "Scout" state (init_cma_par.m; modern rank-one + rank-μ)
# ---------------------------------------------------------------------------
@dataclass
class _Cma:
    """Modern CMA-ES ("Scout") state: mean, step size, paths, covariance + eigen-basis."""

    xmean: np.ndarray
    xold: np.ndarray
    sigma: float
    insigma: float
    pc: np.ndarray
    ps: np.ndarray
    B: np.ndarray
    BD: np.ndarray
    C: np.ndarray
    diagD: np.ndarray
    chiN: float
    mu: int
    weights: np.ndarray
    mueff: float
    cc: float
    cs: float
    ccov1: float
    ccovmu: float
    damps: float


def _init_cma_par(ea2: np.ndarray, n: int, n2: int) -> _Cma:
    """Port of init_cma_par.m — CMA parameters seeded on the mean of EA_2."""
    xmean = np.mean(ea2, axis=0).astype(np.float64)
    insigma = 0.3
    diagD = np.ones(n)                                  # insigma/max(insigma) = 1
    B = np.eye(n)
    BD = B * diagD
    C = np.eye(n)
    chiN = n ** 0.5 * (1.0 - 1.0 / (4.0 * n) + 1.0 / (21.0 * n * n))
    mu = int(np.ceil(n2 / 2.0))
    w = np.log(max(mu, n / 2.0) + 0.5) - np.log(np.arange(1, mu + 1))
    mueff = float(np.sum(w) ** 2 / np.sum(w * w))
    w = w / np.sum(w)
    cc = (4.0 + mueff / n) / (n + 4.0 + 2.0 * mueff / n)
    cs = (mueff + 2.0) / (n + mueff + 3.0)
    ccov1 = 2.0 / ((n + 1.3) ** 2 + mueff)
    ccovmu = 2.0 * (mueff - 2.0 + 1.0 / mueff) / ((n + 2.0) ** 2 + mueff)
    damps = (0.5 + 0.5 * min(1.0, (0.27 * n2 / mueff - 1.0) ** 2)
             + 2.0 * max(0.0, np.sqrt((mueff - 1.0) / (n + 1.0)) - 1.0) + cs)
    return _Cma(xmean=xmean, xold=xmean.copy(), sigma=insigma, insigma=insigma,
                pc=np.zeros(n), ps=np.zeros(n), B=B, BD=BD, C=C, diagD=diagD, chiN=chiN,
                mu=mu, weights=w, mueff=mueff, cc=cc, cs=cs, ccov1=ccov1, ccovmu=ccovmu,
                damps=damps)


# ---------------------------------------------------------------------------
# Whole-run mutable state
# ---------------------------------------------------------------------------
@dataclass
class _St:
    """Whole-run mutable state shared by the EBO and Scout phases (populations, memories, archive, best)."""

    ea1: np.ndarray
    ea1old: np.ndarray
    eaobj1: np.ndarray
    ea2: np.ndarray
    eaobj2: np.ndarray
    probDE1: np.ndarray
    probSC: np.ndarray
    arc_pop: np.ndarray
    arc_NP: int
    hist_pos: int
    memsize: int
    m_f: np.ndarray
    m_cr: np.ndarray
    m_T: np.ndarray
    m_freq: np.ndarray
    cma: _Cma
    bestx: np.ndarray
    bestold: float
    PS1: int
    PS2: int
    prob_ls: float


def _han_boun_de(vi, lb, ub, x):
    """Boundary repair for DE (han_boun.m case 1): midpoint with the parent x."""
    vi = np.where(vi < lb, (x + lb) / 2.0, vi)
    vi = np.where(vi > ub, (x + ub) / 2.0, vi)
    return vi


def _han_boun_cma(arx, lb, ub, xref):
    """Boundary repair for CMA (han_boun.m case 2): reflect 2·bound − x, clamped."""
    below = arx < lb
    arx = np.where(below, np.minimum(ub, np.maximum(lb, 2.0 * lb - xref)), arx)
    above = arx > ub
    arx = np.where(above, np.maximum(lb, np.minimum(ub, 2.0 * lb - xref)), arx)
    return arx


def _round_half_away(x: float) -> int:
    """MATLAB ``round`` — half away from zero (Python's ``round`` is half to even)."""
    return int(np.floor(x + 0.5)) if x >= 0.0 else -int(np.floor(-x + 0.5))


_BESTT_CDF: dict[tuple[int, int], np.ndarray] = {}


def _bestt_cdf(m: int, dd: int) -> np.ndarray:
    """CDF of ``min(randperm(m, dd)) − 1`` (0-based rank), for inverse-transform sampling.

    ``randperm`` draws ``dd`` **distinct** ranks, so the minimum follows the
    hypergeometric-style law ``P(rank ≥ k) = C(m−k, dd)/C(m, dd)`` — NOT the
    min-of-``dd``-iid-uniforms law. Built from the exact recurrence
    ``S(0)=1, S(k+1) = S(k)·(m−k−dd)/(m−k)``; ``cdf[k] = 1 − S(k+1)``.
    Cached per ``(m, dd)``: both change only when LPSR shrinks PS1.
    """
    key = (m, dd)
    cached = _BESTT_CDF.get(key)
    if cached is not None:
        return cached
    hi = m - dd                                   # largest attainable 0-based rank
    cdf = np.empty(hi + 1, dtype=np.float64)
    s = 1.0
    for k in range(hi + 1):
        s *= (m - k - dd) / (m - k)               # S(k+1)
        cdf[k] = 1.0 - s
    cdf[hi] = 1.0                                 # exact tail (S(hi+1) == 0)
    _BESTT_CDF[key] = cdf
    return cdf


def _bestt(rng, pop_size: int, D: int) -> np.ndarray:
    """Port of bestt.m — per-individual towards-best index into the sorted EA_1.

    MATLAB (bestt.m:8) draws ``min(randperm(m, Dd))``: the minimum of ``Dd``
    **distinct** ranks. Sampling ``Dd`` **iid** ranks instead (the closed-form
    ``floor(m·(1−u^{1/Dd}))``) shifts the expected donor rank by ``Dd/(Dd+1)`` —
    about one rank, persistently less greedy for the whole run — so draw from the
    exact without-replacement law by inverse transform on the cached CDF.
    """
    if 2 * D > pop_size:
        dd = 1
        m = max(_round_half_away(0.1 * pop_size), 2)   # MATLAB round (bestt.m:5)
    else:
        dd = D
        m = pop_size
    u = np.asarray(rng.random(pop_size), dtype=np.float64)
    return np.searchsorted(_bestt_cdf(m, dd), u, side="right").astype(np.int64)


def _update_archive(st: _St, rng, added: np.ndarray) -> None:
    """Port of updateArchive.m — add replaced parents, dedup rows, random-trim to arc_NP."""
    if st.arc_NP == 0 or added.shape[0] == 0:
        return
    pool = np.vstack([st.arc_pop, added]) if st.arc_pop.shape[0] else added
    _, keep = np.unique(pool, axis=0, return_index=True)     # dedup rows (first occurrences)
    pool = pool[np.sort(keep)]
    if pool.shape[0] > st.arc_NP:
        sel = np.asarray(rng.permutation(pool.shape[0]), dtype=np.int64)[:st.arc_NP]
        pool = pool[sel]
    st.arc_pop = pool


def _gnr1r2(rng, ps1: int, npall: int):
    """Port of gnR1R2.m — r1,r3 ∈ [0,PS1), r2 ∈ [0,npall); r1≠r0, r2≠{r0,r1}, r3≠{r0,r1,r2}."""
    r0 = np.arange(ps1)
    r1 = np.asarray(rng.integers(0, ps1, ps1), dtype=np.int64)
    for _ in range(1000):
        pos = r1 == r0
        if not pos.any():
            break
        r1[pos] = np.asarray(rng.integers(0, ps1, int(pos.sum())), dtype=np.int64)
    r2 = np.asarray(rng.integers(0, npall, ps1), dtype=np.int64)
    for _ in range(1000):
        pos = (r2 == r1) | (r2 == r0)
        if not pos.any():
            break
        r2[pos] = np.asarray(rng.integers(0, npall, int(pos.sum())), dtype=np.int64)
    r3 = np.asarray(rng.integers(0, ps1, ps1), dtype=np.int64)
    for _ in range(1000):
        pos = (r3 == r0) | (r3 == r1) | (r3 == r2)
        if not pos.any():
            break
        r3[pos] = np.asarray(rng.integers(0, ps1, int(pos.sum())), dtype=np.int64)
    return r1, r2, r3


# ---------------------------------------------------------------------------
# EBO (DE) phase — port of EBO.m
# ---------------------------------------------------------------------------
def _ebo_phase(st, ev, rng, lb, ub, recorder, n, iter_, gmax, max_nfes):
    """One EBO/DE generation on EA_1 (port of EBO.m): mutate, adaptive crossover, select, adapt memories."""
    PS1 = st.PS1
    x = st.ea1
    fitx = st.eaobj1
    H = st.memsize

    mem_idx = np.asarray(rng.integers(0, H, PS1), dtype=np.int64)
    mu_sf, mu_cr = st.m_f[mem_idx], st.m_cr[mem_idx]
    mu_T, mu_freq = st.m_T[mem_idx], st.m_freq[mem_idx]

    # ---- CR ~ mu_cr + 0.1·asin-bell ; ⊥(-1)->0 ; clip[0,1] ----
    cr = mu_cr + 0.1 * _asin_bell(rng, PS1)
    cr[mu_cr == -1] = 0.0
    cr = np.clip(cr, 0.0, 1.0)
    # ---- F ~ Cauchy(mu_sf,0.1) ; resample<=0 ; min 1 ----
    F = mu_sf + 0.1 * np.tan(np.pi * (np.asarray(rng.random(PS1)) - 0.5))
    for _ in range(100):
        bad = F <= 0.0
        if not bad.any():
            break
        F[bad] = mu_sf[bad] + 0.1 * np.tan(np.pi * (np.asarray(rng.random(int(bad.sum()))) - 0.5))
    # EBO.m:24-27 loops until EVERY F > 0, so a non-positive F can never escape. Our loop
    # is capped at 100 rounds for termination safety, and the cap is genuinely reachable:
    # the tan-schedule override (EBO.m:65) can push the F memory strongly negative
    # (min(m_f) = -221.85 measured on F10 D=10), and at mu_sf = -221.85 the chance that
    # 101 Cauchy draws all land <= 0 is ~0.99. Without this floor the leaked value drives
    # a large-magnitude NEGATIVE F, reversing the mutation direction where the MATLAB
    # uses a small positive one. Snap any survivor to the smallest admissible F.
    np.maximum(F, np.finfo(np.float64).tiny, out=F)
    F = np.minimum(F, 1.0)
    # ---- T ~ mu_T + 0.05·asin-bell ; clip[0,0.5] ----
    T = mu_T + 0.05 * _asin_bell(rng, PS1)
    T = np.clip(T, 0.0, 0.5)
    # ---- freq ~ Cauchy(mu_freq,0.1) ; resample<=0 ; min 1 ----
    freq = mu_freq + 0.1 * np.tan(np.pi * (np.asarray(rng.random(PS1)) - 0.5))
    for _ in range(100):
        bad = freq <= 0.0
        if not bad.any():
            break
        freq[bad] = mu_freq[bad] + 0.1 * np.tan(np.pi * (np.asarray(rng.random(int(bad.sum()))) - 0.5))
    freq = np.minimum(freq, 1.0)
    # ---- first-half tan-scheduled F override (EBO.m l.60-67) ----
    if ev.nfes <= max_nfes / 2.0:
        if rng.random() < 0.5:
            F = 0.5 * (np.tan(2.0 * np.pi * 0.5 * iter_ + np.pi) * ((gmax - iter_) / gmax) + 1.0) * np.ones(PS1)
        else:
            F = 0.5 * (np.tan(2.0 * np.pi * freq * iter_) * (iter_ / gmax) + 1.0)

    # ---- per-dimension crossover-rate profile CR[i,:] from cr(i),T(i),l(i) ----
    if n == 1:
        CRm = cr.reshape(PS1, 1)
    else:
        half = n // 2
        if n % 2 == 0:
            d = np.concatenate([np.arange(half), np.arange(half)[::-1]])
        else:
            d = np.concatenate([np.arange(half), [half], np.arange(half)[::-1]])
        prof = cr[:, None] * np.exp(-(T[:, None] / n) * d[None, :])     # (PS1, n) decaying profile
        l0 = np.floor(n * np.asarray(rng.random(PS1))).astype(np.int64)  # circular start (0-based)
        roll = (np.arange(n)[None, :] - l0[:, None]) % n
        CRm = np.take_along_axis(prof, roll, axis=1)

    # ---- mutation: op_1 criss-cross / op_2 towards-best ----
    pop_all = np.vstack([x, st.arc_pop]) if st.arc_pop.shape[0] else x
    r1, r2, r3 = _gnr1r2(rng, PS1, pop_all.shape[0])
    bb = np.asarray(rng.random(PS1), dtype=np.float64)
    op_1 = bb <= st.probDE1[0]
    op_2 = ~op_1
    phix = x[_bestt(rng, PS1, n)]
    Fc = F[:, None]
    vi = x.copy()
    vi[op_1] = x[op_1] + Fc[op_1] * (x[r1[op_1]] - x[op_1] + x[r3[op_1]] - pop_all[r2[op_1]])
    vi[op_2] = x[op_2] + Fc[op_2] * (phix[op_2] - x[op_2] + x[r1[op_2]] - x[r3[op_2]])

    vi = _han_boun_de(vi, lb, ub, x)
    # ---- crossover (per-dimension CR + jrand) ----
    mask = np.asarray(rng.random((PS1, n)), dtype=np.float64) > CRm       # True -> take parent
    jr = np.floor(np.asarray(rng.random(PS1)) * n).astype(np.int64)
    mask[np.arange(PS1), jr] = False
    ui = np.where(mask, x, vi)

    # ---- evaluate (budget-capped final batch) ----
    n_eval = min(PS1, ev.remaining())
    fitx_new = fitx.copy()
    if n_eval > 0:
        fitx_new[:n_eval] = ev.evaluate(ui[:n_eval])
    I = fitx_new < fitx                                                  # strict improvement

    recorder.record_generation(
        x, best_fitness=ev.best_fitness, nfes=ev.nfes, generated=int(n_eval),
        accepted_improved=int(np.count_nonzero(I)), fitness=fitx,
    )

    diff = np.abs(fitx - fitx_new)
    goodCR, goodF, goodT, goodFreq = cr[I], F[I], T[I], freq[I]
    _update_archive(st, rng, x[I])
    # ---- probDE1 update (relative improvement per operator) ----
    # EBO.m:124 divides by |fitx|. CEC-2017 raw fitness is ≥ 100 by construction so
    # that is always safe there; cec2011 objectives can be exactly 0. Treat a zero
    # denominator as "no relative improvement" instead of letting inf/NaN reach probDE1.
    denom = np.abs(fitx)
    diff2 = np.zeros_like(denom)
    np.divide(np.maximum(0.0, fitx - fitx_new), denom, out=diff2, where=denom > 0.0)
    c1 = max(0.0, float(np.mean(diff2[op_1]))) if op_1.any() else 0.0
    c2 = max(0.0, float(np.mean(diff2[op_2]))) if op_2.any() else 0.0
    if c1 != 0.0 and c2 != 0.0:
        st.probDE1 = np.clip(np.array([c1, c2]) / (c1 + c2), 0.1, 0.9)
    else:
        st.probDE1 = np.array([0.5, 0.5])
    # ---- apply survival ----
    st.ea1old[I] = x[I]
    x[I] = ui[I]
    fitx[I] = fitx_new[I]
    # ---- memory update (weighted-Lehmer; F/CR at hist_pos, then T/freq at hist_pos+1) ----
    if goodCR.size > 0:
        w = diff[I] / np.sum(diff[I])
        hp = st.hist_pos
        st.m_f[hp] = _lehmer_w(goodF, w)
        if float(goodCR.max()) == 0.0 or st.m_cr[hp] == -1:
            st.m_cr[hp] = -1.0
        else:
            st.m_cr[hp] = _lehmer_w(goodCR, w)
        hp += 1
        if hp >= st.memsize:
            hp = 0
        st.m_T[hp] = _lehmer_w(goodT, w)
        if float(goodFreq.max()) == 0.0 or st.m_freq[hp] == -1:
            st.m_freq[hp] = -1.0
        else:
            st.m_freq[hp] = _lehmer_w(goodFreq, w)
        st.hist_pos = hp
    # ---- sort EA_1, record feasible best ----
    order = np.argsort(fitx, kind="stable")
    st.eaobj1 = fitx[order]
    st.ea1 = x[order]
    st.ea1old = st.ea1old[order]
    if st.eaobj1[0] < st.bestold and np.all(st.ea1[0] >= lb) and np.all(st.ea1[0] <= ub):
        st.bestold = float(st.eaobj1[0])
        st.bestx = st.ea1[0].copy()


# ---------------------------------------------------------------------------
# CMAR ("Scout") phase — port of Scout.m
# ---------------------------------------------------------------------------
def _scout_phase(st, ev, rng, lb, ub, recorder, n, iter_, max_nfes):
    """One modified-CMA-ES generation on EA_2 (port of Scout.m): asin-bell sample, evaluate, adapt m/C/sigma."""
    cma = st.cma
    PS2 = st.PS2
    prev_best = ev.best_fitness
    ea2_in0 = st.ea2[0].copy()                                          # input EA_2 best (MATLAB x(1,:))

    # ---- sample: M1 (asin-diff bell) or M2 (asin(2U-1)) with prob 0.5 (whole batch) ----
    if rng.random() < st.probSC[0]:
        arz = _asin_bell(rng, (n, PS2))                                  # M1
    else:
        u = np.asarray(rng.random((n, PS2)), dtype=np.float64)
        arz = _SQRT_PI * np.arcsin(2.0 * u - 1.0)                        # M2
    arx = cma.xmean[:, None] + cma.sigma * (cma.BD @ arz)                # (n, PS2)

    if ev.nfes >= 0.5 * max_nfes:                                        # bounds only after 50 %
        arxvalid = _han_boun_cma(arx.T, lb, ub, st.ea2).T
    else:
        arxvalid = arx
    # A coordinate with lb == ub is a FIXED parameter, not a search variable, so it is
    # pinned in BOTH halves — the half-budget gate above governs bound *repair* of live
    # variables, which is a different question. CEC-2017 has no zero-width dimension, so
    # the MATLAB never meets this case and is undefined here (same class as jSO's
    # ln(1)=0 population and np.mod(x,0) in the since-replaced IPOP port); on cec2011 T12, 24 of 240
    # coordinates are pinned and unrepaired samples breached them by up to 0.73.
    # Strictly inert wherever ub > lb, hence a no-op on every cec2017 cell.
    fixed = lb >= ub
    if fixed.any():
        arxvalid = np.array(arxvalid, copy=True)
        arxvalid[fixed, :] = lb[fixed, None]

    n_eval = min(PS2, ev.remaining())
    valid_rows = arxvalid.T[:n_eval]                                    # (n_eval, n) columns as rows
    fraw = ev.evaluate(valid_rows)
    idx_sel = np.argsort(fraw, kind="stable")
    # record + feasible best
    pos_ro = int(np.argmin(fraw))
    cand = arxvalid[:, pos_ro]
    if fraw[pos_ro] < st.bestold and np.all(cand >= lb) and np.all(cand <= ub):
        st.bestold = float(fraw[pos_ro])
        st.bestx = cand.copy()
    recorder.record_generation(
        valid_rows, best_fitness=ev.best_fitness, nfes=ev.nfes, generated=int(n_eval),
        accepted_improved=int(np.count_nonzero(fraw < prev_best)), fitness=fraw,
    )
    # new EA_2 = the evaluated valid points, sorted by fitness
    st.ea2 = valid_rows[idx_sel].copy()
    st.eaobj2 = fraw[idx_sel].copy()
    if n_eval < PS2:
        return                                                          # partial final batch: no CMA update

    arx = arx[:, idx_sel]
    arz = arz[:, idx_sel]

    # ---- recombination weights = normalized best-μ fitness values (Scout.m quirk) ----
    mu = cma.mu
    w = st.eaobj2[:mu].astype(np.float64).copy()                        # = sorted fraw[:mu]
    # Scout.m:51 guards only the overflow case, because CEC-2017 raw fitness is ≥ 100 so
    # sum(w) is always large and positive. cec2011 objectives may be negative or straddle
    # zero, making sum(w) vanish or flip sign -> NaN weights -> NaN samples -> the
    # evaluator's finiteness check raises. Shift into the positive orthant (order-
    # preserving, and inert wherever the MATLAB is defined), then fall back to the
    # reference's own degeneracy response: uniform weights.
    if not np.all(np.isfinite(w)):
        w = np.ones(mu)
    else:
        wmin = float(w.min())
        if wmin <= 0.0:
            w = w - wmin + 1.0
        s = float(np.sum(w))
        if not np.isfinite(s) or s <= 0.0 or s > 1e25:                  # Scout.m:51
            w = np.ones(mu)
    w = w / np.sum(w)                                                    # fliplr is a no-op on a vector
    cma.weights = w

    cma.xold = cma.xmean
    cma.xmean = arx[:, :mu] @ w                                          # cmean=1
    if ev.nfes >= 0.5 * max_nfes:
        cma.xmean = _han_boun_cma(cma.xmean[None, :], lb, ub, ea2_in0[None, :])[0]
    zmean = arz[:, :mu] @ w

    cma.ps = (1.0 - cma.cs) * cma.ps + np.sqrt(cma.cs * (2.0 - cma.cs) * cma.mueff) * (cma.B @ zmean)
    hsig = (np.linalg.norm(cma.ps) / np.sqrt(1.0 - (1.0 - cma.cs) ** (2 * iter_)) / cma.chiN
            < 1.4 + 2.0 / (n + 1.0))
    cma.pc = ((1.0 - cma.cc) * cma.pc
              + (hsig * np.sqrt(cma.cc * (2.0 - cma.cc) * cma.mueff) / cma.sigma) * (cma.xmean - cma.xold))
    if cma.ccov1 + cma.ccovmu > 0:
        arpos = (arx[:, :mu] - cma.xold[:, None]) / cma.sigma
        cma.C = ((1.0 - cma.ccov1 - cma.ccovmu) * cma.C
                 + cma.ccov1 * np.outer(cma.pc, cma.pc)
                 + cma.ccovmu * (arpos @ (w[:, None] * arpos.T)))
    cma.sigma = cma.sigma * float(np.exp(min(1.0, (np.linalg.norm(cma.ps) / cma.chiN - 1.0) * cma.cs / cma.damps)))

    # ---- lazy eigen-refresh of B, BD from C (Scout.m period) ----
    denom = cma.ccov1 + cma.ccovmu
    if denom > 0 and np.mod(iter_, 1.0 / denom / n / 10.0) < 1:
        cma.C = np.triu(cma.C) + np.triu(cma.C, 1).T
        if not np.all(np.isfinite(cma.C)):
            cma.C = np.eye(n)
            cma.pc = np.zeros(n)
            cma.ps = np.zeros(n)
        eigvals, cma.B = np.linalg.eigh(cma.C)
        if eigvals.min() <= 0:
            eigvals = np.where(eigvals < 0, 0.0, eigvals)
            tmp = eigvals.max() / 1e14
            cma.C = cma.C + tmp * np.eye(n)
            eigvals = eigvals + tmp
        if eigvals.max() > 1e14 * eigvals.min():
            tmp = eigvals.max() / 1e14 - eigvals.min()
            cma.C = cma.C + tmp * np.eye(n)
            eigvals = eigvals + tmp
        cma.diagD = np.sqrt(eigvals)
        cma.BD = cma.B * cma.diagD


# ---------------------------------------------------------------------------
# Terminal SQP local search — port of LS2.m (fmincon 'sqp' -> scipy SLSQP)
# ---------------------------------------------------------------------------
def _ls2(st, ev, rng, lb, ub, n, max_nfes):
    """Terminal SQP local search on the best (port of LS2.m: fmincon 'sqp' -> scipy SLSQP)."""
    ls_fe = int(np.ceil(0.02 * max_nfes))
    cap = min(ls_fe, ev.remaining())
    if cap <= 0:
        return
    used = [0]
    x0 = st.bestx.astype(np.float64).copy()
    f0 = st.bestold
    best_x = x0.copy()
    best_f = [f0]

    def obj(z):
        """Budget-counting objective wrapper for SLSQP (raises to unwind when spent)."""
        if used[0] >= cap or ev.is_exhausted():
            raise _StopLS()
        used[0] += 1
        fz = ev.evaluate_one(z)
        if fz < best_f[0]:
            best_f[0] = fz
            best_x[:] = z
        return fz

    bounds = [(float(lb[i]), float(ub[i])) for i in range(n)]
    res = None
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)   # SLSQP benign out-of-bounds probe
            # LS2.m:11-12 sets only Display/algorithm/UseParallel/MaxFunEvals, so fmincon
            # keeps its default TolFun=1e-6 and normally converges well before the FE cap.
            # ftol=1e-30 would disable that test and burn the full cap (20k evals at
            # D=100) on every call, draining the endgame budget away from EA_1/EA_2.
            res = minimize(obj, x0, method="SLSQP", bounds=bounds,
                           options={"maxiter": cap, "ftol": 1e-6})
    except (_StopLS, _base.BudgetExhausted):
        res = None                                           # cap unwound it: return unusable

    # LS2.m:14-25 judges success on fmincon's RETURNED point, not on the best point ever
    # probed (which would count finite-difference gradient probes). Fall back to best-seen
    # only when the FE cap aborted the solver and there is no return value to judge.
    if res is not None and np.isfinite(res.fun) and np.all(np.isfinite(res.x)):
        cand_f, cand_x = float(res.fun), np.asarray(res.x, dtype=np.float64)
    else:
        cand_f, cand_x = float(best_f[0]), best_x

    if cand_f < f0 and np.all(cand_x >= lb) and np.all(cand_x <= ub):
        st.bestold = cand_f
        st.bestx = cand_x.copy()
        # inject into EA_1, reseed CMAR on the new best (LS2 success branch)
        st.ea1[st.PS1 - 1] = st.bestx
        st.eaobj1[st.PS1 - 1] = st.bestold
        order = np.argsort(st.eaobj1, kind="stable")
        st.eaobj1 = st.eaobj1[order]
        st.ea1 = st.ea1[order]
        st.ea1old = st.ea1old[order]
        st.ea2 = np.repeat(st.ea1[0][None, :], st.PS2, axis=0)
        st.cma = _init_cma_par(st.ea2, n, st.PS2)
        st.cma.sigma = 1e-05
        st.eaobj2 = np.full(st.PS2, st.eaobj1[0])
        st.prob_ls = 0.1
    else:
        st.prob_ls = 0.01


def optimize(problem, options: OptimizerOptions) -> OptimizerResult:
    """Run EBOwithCMAR under the family contract."""
    rng, ev, start = _base.start_run(problem, options)
    n = int(problem.dim)
    lb = np.asarray(problem.lb, dtype=np.float64).reshape(-1)
    ub = np.asarray(problem.ub, dtype=np.float64).reshape(-1)
    max_nfes = int(problem.max_nfes)
    CS, gmax = _cs_gmax(n)

    PS1 = int(_base.param(options, "PS1", 18 * n))
    PS2 = int(_base.param(options, "PS2", 4 + int(np.floor(3 * np.log(n)))))
    min_pop = 4
    memsize = 6
    arch_rate = 2.6
    init_pop = PS1

    # ---- initialization (fair start on the family stream) ----
    total = PS1 + PS2
    if options.initial_population is not None:
        x = np.asarray(options.initial_population, dtype=np.float64).reshape(-1, n)[:total].copy()
    else:
        x = lb + np.asarray(rng.random((total, n)), dtype=np.float64) * (ub - lb)
    fitx = ev.evaluate(x)

    recorder = _base.make_recorder(problem, options, _COUNTING_RULE)
    recorder.record_initial(x, ev.best_fitness, ev.nfes)

    b = int(np.argmin(fitx))
    ea1 = x[:PS1].copy()
    eaobj1 = fitx[:PS1].copy()
    ea1old = x[np.asarray(rng.permutation(PS1), dtype=np.int64)].copy()
    ea2 = x[PS1:].copy()
    eaobj2 = fitx[PS1:].copy()

    st = _St(
        ea1=ea1, ea1old=ea1old, eaobj1=eaobj1, ea2=ea2, eaobj2=eaobj2,
        probDE1=np.array([0.5, 0.5]), probSC=np.array([0.5, 0.5]),
        arc_pop=np.empty((0, n), dtype=np.float64), arc_NP=int(round(arch_rate * PS1)),
        hist_pos=0, memsize=memsize,
        m_f=np.full(memsize, 0.7), m_cr=np.full(memsize, 0.5),
        m_T=np.full(memsize, 0.1), m_freq=np.full(memsize, 0.5),
        cma=_init_cma_par(ea2, n, PS2),
        bestx=x[b].copy(), bestold=float(fitx[b]), PS1=PS1, PS2=PS2, prob_ls=0.1,
    )

    iter_ = 0
    cy = 0
    indx = 0
    Probs = np.array([1.0, 1.0])

    while not ev.is_exhausted():
        iter_ += 1
        cy += 1
        # ---- cycle control: recompute phase probs / share information ----
        if cy == CS + 1:
            qual = np.array([st.eaobj1[0], st.eaobj2[0]])
            # EBO_BIN.m:81 `1 - qual./sum(qual)` presumes POSITIVE objectives (CEC-2017
            # raw fitness is >= 100). With a negative or zero objective the share flips
            # sign and the term ranks the WORSE engine higher — an inversion, not just a
            # NaN. Fall back to neutral, the same response this block already uses for
            # degenerate diversity below.
            if np.all(np.isfinite(qual)) and float(qual.min()) > 0.0:
                norm_qual = 1.0 - qual / np.sum(qual)
            else:
                norm_qual = np.array([0.5, 0.5])
            d1 = float(np.mean(np.linalg.norm(st.ea1[1:st.PS1] - st.ea1[0], axis=1))) if st.PS1 > 1 else 0.0
            d2 = float(np.mean(np.linalg.norm(st.ea2[1:st.PS2] - st.ea2[0], axis=1))) if st.PS2 > 1 else 0.0
            dv = np.array([d1, d2])
            norm_div = dv / np.sum(dv) if np.sum(dv) != 0 else np.array([0.5, 0.5])
            Probs = norm_qual + norm_div
            Probs = np.clip(Probs / np.sum(Probs), 0.1, 0.9)
            indx = int(np.argmax(Probs)) + 1                            # 1=EBO, 2=CMAR
            if Probs[0] == Probs[1]:
                indx = 0
        elif cy == 2 * CS:
            if indx == 1:                                               # EBO better -> reseed CMAR
                take = min(st.PS2, st.PS1)
                sel = np.asarray(rng.permutation(st.PS1), dtype=np.int64)[:take]
                st.ea2[:take] = st.ea1[sel]
                st.eaobj2[:take] = st.eaobj1[sel]
                st.cma = _init_cma_par(st.ea2, n, st.PS2)
                st.cma.sigma = st.cma.sigma * (1.0 - ev.nfes / max_nfes)
            else:                                                       # CMAR better -> inject into EA_1
                if np.all(st.ea2[0] > lb) and np.all(st.ea2[0] < ub):
                    st.ea1[st.PS1 - 1] = st.ea2[0]
                    st.eaobj1[st.PS1 - 1] = st.eaobj2[0]
                    order = np.argsort(st.eaobj1, kind="stable")
                    st.eaobj1 = st.eaobj1[order]
                    st.ea1 = st.ea1[order]
                    st.ea1old = st.ea1old[order]
            cy = 1
            Probs = np.array([1.0, 1.0])

        # ---- EBO (DE) phase, gated by Probs[0], with LPSR of PS1 ----
        if ev.nfes < max_nfes and rng.random() < Probs[0]:
            upd = _round_half_away(((min_pop - init_pop) / max_nfes) * ev.nfes + init_pop)
            if st.PS1 > upd:
                red = st.PS1 - upd
                if st.PS1 - red < min_pop:
                    red = st.PS1 - min_pop
                keep = st.PS1 - red
                st.ea1 = st.ea1[:keep]                                  # drop worst (sorted best-first)
                st.ea1old = st.ea1old[:keep]
                st.eaobj1 = st.eaobj1[:keep]
                st.PS1 = keep
                st.arc_NP = int(round(arch_rate * st.PS1))
                if st.arc_pop.shape[0] > st.arc_NP:
                    sel = np.asarray(rng.permutation(st.arc_pop.shape[0]), dtype=np.int64)[:st.arc_NP]
                    st.arc_pop = st.arc_pop[sel]
            _ebo_phase(st, ev, rng, lb, ub, recorder, n, iter_, gmax, max_nfes)

        # ---- CMAR (Scout) phase, gated by Probs[1] ----
        if ev.nfes < max_nfes and rng.random() < Probs[1]:
            _scout_phase(st, ev, rng, lb, ub, recorder, n, iter_, max_nfes)

        # ---- terminal SQP local search (last 25 % of the budget) ----
        if ev.nfes > 0.75 * max_nfes and rng.random() < st.prob_ls:
            _ls2(st, ev, rng, lb, ub, n, max_nfes)

    # report the algorithm's FEASIBLE incumbent (MATLAB gates bestx on bounds)
    ev.best_x = st.bestx
    ev.best_fitness = st.bestold
    return _base.build_result(
        "ebowithcmar", problem, options, ev, start_time=start,
        params={"profile": _base.resolve_profile(options), "PS1_init": init_pop, "PS2": PS2,
                "min_pop": min_pop, "memsize": memsize, "arch_rate": arch_rate,
                "CS": CS, "Gmax": gmax},
        notes="EBOwithCMAR 2017 (CEC-2017 winner; EBO/DE + CMAR + SQP); code-first port; paper=Kumar,Misra,Singh 2017.",
    )
