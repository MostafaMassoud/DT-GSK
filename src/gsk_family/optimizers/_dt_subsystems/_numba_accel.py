"""
Numba-accelerated kernels for the DT-GSK optimizer's own hot paths.

This module holds the optimizer-side JIT kernels only â€” bound repair,
population radius, ACE simplex projection, junior/senior mutation, block/scalar
crossover masks, archive distance + batched insertion, ACE sampling and EMA
updates, PSR target, dim coverage, accept-rate top/bottom stats, and bincount.

Benchmark-suite kernels live next to their suites so that each suite is
a self-contained module:

* CEC2017      kernels â†’ ``benchmarks.cec_suite_python.cec2017._numba``
* CEC2013      kernels â†’ ``benchmarks.cec_suite_python.cec2013._numba``
* CEC2011      kernels â†’ ``benchmarks.cec_suite_python.cec2011._numba``
* CEC2020      kernels â†’ ``benchmarks.cec_suite_python.cec2020._numba``
* CEC2013LSGO kernels â†’ ``benchmarks.cec_suite_python.cec2013lsgo._numba``

Each suite exposes its own ``warmup()`` entry point which is invoked
from :func:`gsk.benchmark_factory.init_cec_worker` so every hot kernel
is JIT-cached before the first generation runs.

Parallel Strategy
-----------------
Every kernel whose outer loop iterates over *independent* population members
(``for i in range(M)`` or ``for i in range(NP)``) is compiled with
``parallel=True`` and uses ``prange`` for that outer loop.  This lets Numba
distribute the per-individual work across CPU cores automatically.

Kernels with data dependencies between iterations (cumulative sums, rank
lookups, CDF traversals, archive insertion with side-effects, etc.) keep
sequential ``range`` to preserve correctness.  These include
``_ace_project_probs_nb``, ``_ace_sample_nb``, ``_ace_update_full_nb``,
``_junior_r1r2r3_core_nb``, ``_senior_r1r2r3_nb``, ``_psr_target_nb``,
and ``_archive_consider_nb``.

Fastmath policy (I4)
--------------------
Per SKILL.md Section "Hard invariants" item 4, ``fastmath=True`` is
*prohibited* in any kernel whose output depends on a floating-point
reduction whose ordering affects the result (sums over a population,
variance / SD accumulators, acceptance-rate deltas, archive-distance
aggregations, etc.).  Such kernels are compiled with ``fastmath=False``
(the njit default) so that the bit-identical-to-reference CEC2017 D=10
parity target in ``gsk.gsk`` is preserved end-to-end.

Kernels that are *per-individual* and do not mix across population
members (e.g. bound repair, per-individual junior/senior mutation
applied element-wise, per-individual crossover mask generation) may
enable ``fastmath=True`` because their outputs are not order-sensitive
across individuals.  When in doubt, keep ``fastmath=False`` and
benchmark before enabling it; a reduction-sensitive slip here is
silent at compile time and only surfaces as a CEC parity drift.

Graceful fallback: if numba is unavailable, all ``*_fast`` exports are None.
"""
from __future__ import annotations
import numpy as np

try:
    from numba import njit, prange  # type: ignore[import-untyped]
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

PI = np.pi

# ===================== 1. bound_constraint =====================
if HAS_NUMBA:
    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def _bound_constraint_nb(vi, pop, lower, upper):
        """Repair out-of-bounds solutions using L-SHADE midpoint method.

        For each dimension j of each individual i, if vi[i,j] < lower[j],
        sets vi[i,j] = (pop[i,j] + lower[j]) / 2. Analogous for upper bound.

        Parameters
        ----------
        vi : ndarray, shape (NP, D) - mutant vectors, modified in-place
        pop : ndarray, shape (NP, D) - parent vectors (feasible)
        lower : ndarray, shape (D,) - lower bounds
        upper : ndarray, shape (D,) - upper bounds
        """
        n, d = vi.shape
        for i in prange(n):
            for j in range(d):
                if vi[i, j] < lower[j]:
                    vi[i, j] = (pop[i, j] + lower[j]) * 0.5
                elif vi[i, j] > upper[j]:
                    vi[i, j] = (pop[i, j] + upper[j]) * 0.5

    def bound_constraint_fast(vi, pop, lu):
        """Apply bound constraint repair to mutant population.

        Parameters
        ----------
        vi : ndarray, shape (NP, D) - mutant vectors, modified in-place
        pop : ndarray, shape (NP, D) - parent population
        lu : ndarray, shape (2, D) - row 0 = lower bounds, row 1 = upper bounds
        """
        _bound_constraint_nb(vi, pop, lu[0], lu[1])
else:
    bound_constraint_fast = None

# ===================== 2. population_radius =====================
if HAS_NUMBA:
    # Invariant I4 (SKILL.md): no fastmath=True in reduction-sensitive kernels.
    # This kernel sums per-row distances under prange; fastmath would relax
    # associativity across threads and make the scalar accumulator
    # non-deterministic.  Keep parallel, drop fastmath.
    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def _pop_radius_nb(pop, span):
        """Compute normalised mean distance from centroid (population radius).

        Returns a scalar in [0, 1] measuring how spread-out the population is
        relative to the search-space span.

        Parameters
        ----------
        pop : ndarray, shape (NP, D) - current population
        span : ndarray, shape (D,) - per-dimension search-space widths
        """
        n, d = pop.shape
        if n <= 1: return 0.0
        mu = np.empty(d)
        for j in range(d):
            s = 0.0
            for i in range(n): s += pop[i, j]
            mu[j] = s / n
        denom_sq = 0.0
        for j in range(d): denom_sq += span[j] * span[j]
        if denom_sq <= 0.0: return 0.0
        denom = np.sqrt(denom_sq)
        total_dist = 0.0
        for i in prange(n):
            dist_sq = 0.0
            for j in range(d):
                diff = pop[i, j] - mu[j]
                dist_sq += diff * diff
            total_dist += np.sqrt(dist_sq)
        rad = (total_dist / n) / denom
        if rad < 0.0: return 0.0
        if rad > 1.0: return 1.0
        return rad

    def population_radius_fast(pop, span):
        """Compute normalised population radius (scalar in [0, 1]).

        Parameters
        ----------
        pop : ndarray, shape (NP, D) - current population
        span : ndarray, shape (D,) - per-dimension search-space widths
        """
        return float(_pop_radius_nb(np.asarray(pop, dtype=np.float64), np.asarray(span, dtype=np.float64)))
else:
    population_radius_fast = None

# ===================== 3. ace_project_probs =====================
if HAS_NUMBA:
    @njit(cache=True, boundscheck=False, nogil=True)
    def _ace_project_probs_nb(v, p_min):
        """Project a vector onto the probability simplex with a minimum floor.

        Implements simplex projection (Duchi et al.) with per-element minimum
        probability p_min. Sequential because of sorting and prefix sums.

        Parameters
        ----------
        v : ndarray, shape (M,) - raw (unnormalised) weight vector
        p_min : float - minimum probability per element
        """
        n = v.shape[0]
        if n <= 0: return v.copy()
        if p_min < 0.0: p_min = 0.0
        if p_min * n >= 1.0:
            out = np.empty(n)
            for i in range(n): out[i] = 1.0 / n
            return out
        s = 1.0 - p_min * n
        a = np.empty(n)
        for i in range(n): a[i] = v[i] - p_min
        u = a.copy(); u.sort()
        for i in range(n // 2): u[i], u[n-1-i] = u[n-1-i], u[i]
        cssv = np.empty(n); cssv[0] = u[0]
        for j in range(1, n): cssv[j] = cssv[j-1] + u[j]
        rho = -1
        for j in range(n):
            t = (cssv[j] - s) / (j + 1)
            if u[j] - t > 0: rho = j
        if rho == -1:
            x = np.empty(n)
            for i in range(n): x[i] = s / n
        else:
            theta = (cssv[rho] - s) / (rho + 1)
            x = np.empty(n)
            for i in range(n):
                x[i] = a[i] - theta
                if x[i] < 0.0: x[i] = 0.0
        out = np.empty(n); tot = 0.0
        for i in range(n): out[i] = x[i] + p_min; tot += out[i]
        if tot <= 0.0 or not np.isfinite(tot):
            for i in range(n): out[i] = 1.0 / n
            return out
        for i in range(n): out[i] /= tot
        if p_min > 0.0:
            tot2 = 0.0
            for i in range(n):
                if out[i] < p_min: out[i] = p_min
                tot2 += out[i]
            for i in range(n): out[i] /= tot2
        return out

    def ace_project_probs_fast(p, p_min):
        """Project probability vector onto the simplex with minimum floor.

        Parameters
        ----------
        p : array-like - raw weight vector
        p_min : float - minimum probability per element
        """
        return _ace_project_probs_nb(np.asarray(p, dtype=np.float64).ravel(), float(p_min))
else:
    ace_project_probs_fast = None

# ===================== 4. archive distances =====================
if HAS_NUMBA:
    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def _archive_dists_nb(xs, n_stored, x, inv_span, inv_sqrt_d):
        """Compute normalised Euclidean distances from x to all archive members.

        Parameters
        ----------
        xs : ndarray, shape (capacity, D) - archive solutions
        n_stored : int - number of valid entries in xs
        x : ndarray, shape (D,) - query point
        inv_span : ndarray, shape (D,) - 1 / search-space width per dimension
        inv_sqrt_d : float - 1 / sqrt(D) for normalisation
        """
        if n_stored == 0: return np.empty(0, dtype=np.float64)
        d = x.shape[0]
        out = np.empty(n_stored, dtype=np.float64)
        for i in prange(n_stored):
            s = 0.0
            for j in range(d):
                diff = (xs[i, j] - x[j]) * inv_span[j]
                s += diff * diff
            out[i] = np.sqrt(s) * inv_sqrt_d
        return out

    def archive_dists_fast(xs, n_stored, x, inv_span, inv_sqrt_d):
        """Compute normalised distances from x to all archive members.

        Parameters
        ----------
        xs : ndarray - archive solutions
        n_stored : int - number of valid entries
        x : array-like - query point
        inv_span : ndarray - inverse per-dimension span
        inv_sqrt_d : float - inverse sqrt(D)
        """
        return _archive_dists_nb(xs, n_stored, np.asarray(x, dtype=np.float64).ravel(), inv_span, inv_sqrt_d)
else:
    archive_dists_fast = None

# ===================== 5. archive consider =====================
if HAS_NUMBA:
    @njit(cache=True, boundscheck=False, nogil=True)
    def _archive_consider_nb(xs, fs, n_stored, max_size, x, f, inv_span, inv_sqrt_d, dist_thresh):
        """Consider adding a solution to the diversity archive.

        Rejects if the solution is too close to any existing member (below
        dist_thresh). Otherwise adds at end or replaces the nearest member
        when archive is full. Sequential due to early-exit distance check.

        Parameters
        ----------
        xs : ndarray, shape (capacity, D) - archive solutions, modified in-place
        fs : ndarray, shape (capacity,) - archive fitness values, modified in-place
        n_stored : int - current number of stored solutions
        max_size : int - maximum archive capacity
        x : ndarray, shape (D,) - candidate solution
        f : float - candidate fitness
        inv_span : ndarray, shape (D,) - inverse per-dimension span
        inv_sqrt_d : float - inverse sqrt(D)
        dist_thresh : float - minimum distance for acceptance
        """
        if max_size <= 0: return False, n_stored
        if not np.isfinite(f): return False, n_stored
        dim = x.shape[0]
        min_dist = 1e30; min_j = -1
        for i in range(n_stored):
            s = 0.0
            for j in range(dim):
                diff = (xs[i, j] - x[j]) * inv_span[j]
                s += diff * diff
            d = np.sqrt(s) * inv_sqrt_d
            if d < dist_thresh: return False, n_stored
            if d < min_dist: min_dist = d; min_j = i
        if n_stored < max_size:
            for j in range(dim): xs[n_stored, j] = x[j]
            fs[n_stored] = f
            return True, n_stored + 1
        if min_j >= 0:
            for j in range(dim): xs[min_j, j] = x[j]
            fs[min_j] = f
            return True, n_stored
        return False, n_stored
    archive_consider_fast = _archive_consider_nb

    @njit(cache=True, boundscheck=False, nogil=True)
    def _archive_consider_batch_nb(
        xs, fs, n_stored, max_size,
        X_batch, F_batch,
        inv_span, inv_sqrt_d, dist_thresh,
    ):
        """Sequentially consider an entire batch in a single JIT call.

        H7: replaces a Python for-loop of per-candidate
        :func:`_archive_consider_nb` calls with a tight loop in nopython
        mode, eliminating Python/Numba boundary overhead per insertion.
        Each candidate is processed against the live archive (which may be
        modified by earlier candidates in the same batch), preserving the
        sequential semantics of the legacy loop.

        Parameters
        ----------
        xs, fs : (capacity, D)/(capacity,) â€” archive storage, in-place
        n_stored : int â€” initial number of entries
        max_size : int â€” capacity
        X_batch : (K, D) â€” candidate solutions
        F_batch : (K,) â€” candidate fitness values
        inv_span, inv_sqrt_d, dist_thresh : same as the single-candidate kernel

        Returns
        -------
        n_inserted : int64 â€” number of candidates that updated the archive
        n_stored_out : int64 â€” final number of entries in the archive
        """
        if max_size <= 0:
            return 0, n_stored
        n_cur = n_stored
        n_inserted = 0
        K = X_batch.shape[0]
        dim = X_batch.shape[1]
        for k in range(K):
            f = F_batch[k]
            if not np.isfinite(f):
                continue
            min_dist = 1e30
            min_j = -1
            rejected = False
            for i in range(n_cur):
                s = 0.0
                for j in range(dim):
                    diff = (xs[i, j] - X_batch[k, j]) * inv_span[j]
                    s += diff * diff
                d = np.sqrt(s) * inv_sqrt_d
                if d < dist_thresh:
                    rejected = True
                    break
                if d < min_dist:
                    min_dist = d
                    min_j = i
            if rejected:
                continue
            if n_cur < max_size:
                for j in range(dim):
                    xs[n_cur, j] = X_batch[k, j]
                fs[n_cur] = f
                n_cur += 1
                n_inserted += 1
            elif min_j >= 0:
                for j in range(dim):
                    xs[min_j, j] = X_batch[k, j]
                fs[min_j] = f
                n_inserted += 1
        return n_inserted, n_cur

    archive_consider_batch_fast = _archive_consider_batch_nb
else:
    archive_consider_fast = None
    archive_consider_batch_fast = None

# ===================== 6. build_junior_senior =====================
if HAS_NUMBA:
    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def _build_junior_senior_nb(pop, fitness, KF_i, Rg1, Rg2, Rg3, R1, R2, R3, vi_junior, vi_senior):
        """Build junior and senior mutant vectors for the DT-GSK mutation strategy.

        For each individual i, constructs both a junior and a senior donor
        vector using rank-based differential mutation with adaptive KF.

        Parameters
        ----------
        pop : ndarray, shape (NP, D) - current population
        fitness : ndarray, shape (NP,) - fitness values
        KF_i : ndarray, shape (NP,) - per-individual scale factor
        Rg1, Rg2, Rg3 : ndarray, shape (NP,) - junior random indices
        R1, R2, R3 : ndarray, shape (NP,) - senior random indices
        vi_junior : ndarray, shape (NP, D) - junior mutants, written in-place
        vi_senior : ndarray, shape (NP, D) - senior mutants, written in-place
        """
        n, d = pop.shape
        for i in prange(n):
            kf = KF_i[i]
            rg1=Rg1[i]; rg2=Rg2[i]; rg3=Rg3[i]
            if fitness[i] > fitness[rg3]:
                for j in range(d): vi_junior[i,j] = pop[i,j] + kf*(pop[rg1,j]-pop[rg2,j]+pop[rg3,j]-pop[i,j])
            else:
                for j in range(d): vi_junior[i,j] = pop[i,j] + kf*(pop[rg1,j]-pop[rg2,j]+pop[i,j]-pop[rg3,j])
            r1=R1[i]; r2=R2[i]; r3=R3[i]
            if fitness[i] > fitness[r2]:
                for j in range(d): vi_senior[i,j] = pop[i,j] + kf*(pop[r1,j]-pop[r3,j]+pop[r2,j]-pop[i,j])
            else:
                for j in range(d): vi_senior[i,j] = pop[i,j] + kf*(pop[r1,j]-pop[r3,j]+pop[i,j]-pop[r2,j])

    def build_junior_senior_fast(pop, fitness, KF_i, Rg1, Rg2, Rg3, R1, R2, R3, vi_junior, vi_senior):
        """Build junior and senior mutant vectors (wrapper).

        Parameters
        ----------
        pop : ndarray, shape (NP, D) - current population
        fitness : ndarray, shape (NP,) - fitness values
        KF_i : ndarray, shape (NP,) - per-individual scale factor
        Rg1, Rg2, Rg3 : ndarray - junior index arrays
        R1, R2, R3 : ndarray - senior index arrays
        vi_junior, vi_senior : ndarray - output mutant arrays
        """
        _build_junior_senior_nb(pop, fitness, KF_i, Rg1, Rg2, Rg3, R1, R2, R3, vi_junior, vi_senior)

    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def _build_junior_senior_with_repair_nb(
        pop, fitness, KF_i,
        Rg1, Rg2, Rg3, R1, R2, R3,
        lower, upper,
        vi_junior, vi_senior,
    ):
        """Fused junior/senior trial assembly + L-SHADE midpoint bound repair.

        Replaces the previous three-pass sequence
        ``build_junior_senior_fast â†’ bound_constraint(vi_junior) â†’
        bound_constraint(vi_senior)`` with a single (NP, D) traversal that
        evaluates each mutation formula and immediately clamps via the
        midpoint rule ``x_repaired = (x_parent + bound) / 2``.

        Parameters
        ----------
        pop, fitness, KF_i, Rg1, Rg2, Rg3, R1, R2, R3
            Same semantics as :func:`_build_junior_senior_nb`.
        lower, upper : float64[D]
            Per-dimension bounds.
        vi_junior, vi_senior : float64[NP, D]
            Output trial vectors written in place â€” already repaired on exit.
        """
        n, d = pop.shape
        for i in prange(n):
            kf = KF_i[i]
            rg1 = Rg1[i]; rg2 = Rg2[i]; rg3 = Rg3[i]
            jr_better = fitness[i] > fitness[rg3]
            r1 = R1[i]; r2 = R2[i]; r3 = R3[i]
            sr_better = fitness[i] > fitness[r2]
            for j in range(d):
                pij = pop[i, j]
                lj = lower[j]; uj = upper[j]
                # Junior trial
                if jr_better:
                    v = pij + kf * (pop[rg1, j] - pop[rg2, j] + pop[rg3, j] - pij)
                else:
                    v = pij + kf * (pop[rg1, j] - pop[rg2, j] + pij - pop[rg3, j])
                if v < lj:
                    v = 0.5 * (pij + lj)
                elif v > uj:
                    v = 0.5 * (pij + uj)
                vi_junior[i, j] = v
                # Senior trial
                if sr_better:
                    v = pij + kf * (pop[r1, j] - pop[r3, j] + pop[r2, j] - pij)
                else:
                    v = pij + kf * (pop[r1, j] - pop[r3, j] + pij - pop[r2, j])
                if v < lj:
                    v = 0.5 * (pij + lj)
                elif v > uj:
                    v = 0.5 * (pij + uj)
                vi_senior[i, j] = v

    def build_junior_senior_with_repair_fast(
        pop, fitness, KF_i,
        Rg1, Rg2, Rg3, R1, R2, R3,
        lower, upper,
        vi_junior, vi_senior,
    ):
        """Fused junior/senior trial + bound repair (wrapper)."""
        _build_junior_senior_with_repair_nb(
            pop, fitness, KF_i,
            Rg1, Rg2, Rg3, R1, R2, R3,
            lower, upper,
            vi_junior, vi_senior,
        )
else:
    build_junior_senior_fast = None
    build_junior_senior_with_repair_fast = None

# ===================== 7. build_masks_scalar =====================
if HAS_NUMBA:
    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def _build_masks_scalar_nb(rands_j, rands_jg, rands_sg, p_jun, kr, NP, D, D_J, D_S):
        """Build boolean junior/senior dimension masks for crossover.

        For each individual and dimension, assigns the dimension to either the
        junior or senior donor based on random draws and per-individual
        probabilities p_jun and kr.

        Parameters
        ----------
        rands_j : ndarray, shape (NP, D) - uniform random draws for junior selection
        rands_jg : ndarray, shape (NP, D) - uniform random draws for junior gate
        rands_sg : ndarray, shape (NP, D) - uniform random draws for senior gate
        p_jun : ndarray, shape (NP,) - per-individual junior probability
        kr : ndarray, shape (NP,) - per-individual crossover rate
        NP : int - population size
        D : int - dimensionality
        D_J : ndarray, shape (NP, D) - junior mask, written in-place
        D_S : ndarray, shape (NP, D) - senior mask, written in-place
        """
        for i in prange(NP):
            pj = p_jun[i]; k = kr[i]
            for j in range(D):
                if rands_j[i, j] <= pj:
                    D_J[i, j] = rands_jg[i, j] <= k; D_S[i, j] = False
                else:
                    D_J[i, j] = False; D_S[i, j] = rands_sg[i, j] <= k

    def build_masks_scalar_fast(rands_j, rands_jg, rands_sg, p_jun, kr, NP, D, D_J, D_S):
        """Build boolean junior/senior dimension masks (wrapper).

        Parameters
        ----------
        rands_j, rands_jg, rands_sg : ndarray - random draw matrices
        p_jun : ndarray - junior probabilities
        kr : ndarray - crossover rates
        NP, D : int - population size and dimensionality
        D_J, D_S : ndarray - output boolean masks
        """
        _build_masks_scalar_nb(rands_j, rands_jg, rands_sg, p_jun, kr, int(NP), int(D), D_J, D_S)
else:
    build_masks_scalar_fast = None

# ===================== 7b. build_masks_scalar_rows =====================
if HAS_NUMBA:
    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def _build_masks_scalar_rows_nb(
        rands_j,
        rands_jg,
        rands_sg,
        p_jun,
        kr,
        row_indices,
        n_rows,
        D,
        D_J,
        D_S,
    ):
        """Build scalar crossover masks for a selected subset of rows."""
        for ri in prange(n_rows):
            row = row_indices[ri]
            pj = p_jun[row]
            k = kr[row]
            for j in range(D):
                if rands_j[ri, j] <= pj:
                    D_J[row, j] = rands_jg[ri, j] <= k
                    D_S[row, j] = False
                else:
                    D_J[row, j] = False
                    D_S[row, j] = rands_sg[ri, j] <= k

    def build_masks_scalar_rows_fast(
        rands_j,
        rands_jg,
        rands_sg,
        p_jun,
        kr,
        row_indices,
        n_rows,
        D,
        D_J,
        D_S,
    ):
        """Build scalar masks directly into selected rows of D_J/D_S."""
        _build_masks_scalar_rows_nb(
            rands_j,
            rands_jg,
            rands_sg,
            p_jun,
            kr,
            row_indices,
            int(n_rows),
            int(D),
            D_J,
            D_S,
        )
else:
    build_masks_scalar_rows_fast = None

# ===================== 7c. build_masks_blockwise =====================
if HAS_NUMBA:
    @njit(cache=True, parallel=True, boundscheck=False, nogil=True)
    def _build_masks_blockwise_nb(
        rands_block_jun,
        rands_block_gate,
        p_jun_block,
        kr_block,
        block_row_indices,
        groups_flat,
        group_offsets,
        D_J,
        D_S,
    ):
        """Apply linkage-block crossover masks for the rows that draw a block path.

        Each block row (i.e. each row of ``rands_block_jun``) writes only to its
        own row of ``D_J``/``D_S``, so the outer loop is fully parallelisable
        across rows.  For each linkage group, every dimension in the group is
        flipped together (true linkage-aware crossover).

        Parameters
        ----------
        rands_block_jun, rands_block_gate : float64[n_block, n_groups]
            Per-(row, group) uniform draws used to decide junior vs senior and
            whether the gate fires.
        p_jun_block, kr_block : float64[n_block]
            Per-block-row junior probability and crossover rate.
        block_row_indices : int64[n_block]
            Original row index in ``D_J``/``D_S`` for each block row.
        groups_flat : int64[total_dims]
            Concatenated dimension indices for all linkage groups.
        group_offsets : int64[n_groups + 1]
            ``groups_flat[group_offsets[g]:group_offsets[g + 1]]`` is the
            dimension list for group ``g``.
        D_J, D_S : bool_[NP, D]
            Boolean masks written in place.  Caller is responsible for
            initialising them to all-False.
        """
        n_block = rands_block_jun.shape[0]
        n_groups = rands_block_jun.shape[1]
        for bi in prange(n_block):
            row = block_row_indices[bi]
            pj = p_jun_block[bi]
            k = kr_block[bi]
            for g in range(n_groups):
                gate_open = rands_block_gate[bi, g] <= k
                if not gate_open:
                    continue
                start = group_offsets[g]
                end = group_offsets[g + 1]
                if rands_block_jun[bi, g] <= pj:
                    for t in range(start, end):
                        D_J[row, groups_flat[t]] = True
                else:
                    for t in range(start, end):
                        D_S[row, groups_flat[t]] = True

    def build_masks_blockwise_fast(
        rands_block_jun,
        rands_block_gate,
        p_jun_block,
        kr_block,
        block_row_indices,
        groups_flat,
        group_offsets,
        D_J,
        D_S,
    ):
        """Apply blockwise linkage masks (wrapper).

        Inputs are the per-row flattened linkage descriptors built once by
        :func:`_build_phase4_masks` from a Python ``list[np.ndarray]``.
        """
        _build_masks_blockwise_nb(
            rands_block_jun,
            rands_block_gate,
            p_jun_block,
            kr_block,
            block_row_indices,
            groups_flat,
            group_offsets,
            D_J,
            D_S,
        )
else:
    build_masks_blockwise_fast = None

# ===================== 9. junior_r1r2r3 core =====================
if HAS_NUMBA:
    @njit(cache=True, boundscheck=False, nogil=True)
    def _junior_r1r2r3_core_nb(ind_best, r3_pool):
        """Generate junior mutation index triplets (R1, R2, R3).

        R1 and R2 are rank-adjacent neighbours.  R3 is drawn from a
        pre-allocated candidate pool: ``pool[i, 0]`` is the first attempt,
        ``pool[i, 1]`` the second, etc.  This pool is built in Python from
        the same Generator used by the pure-Python fallback, so both paths
        consume identical RNG draws.

        Parameters
        ----------
        ind_best : ndarray, shape (NP,) - indices sorted by fitness (best first)
        r3_pool : ndarray, shape (NP, MAX_R3_ATTEMPTS) - candidate R3 indices
        """
        NP = ind_best.shape[0]
        max_attempts = r3_pool.shape[1]
        rank_of = np.empty(NP, dtype=np.int64)
        for i in range(NP):
            rank_of[ind_best[i]] = i
        R1 = np.empty(NP, dtype=np.int64)
        R2 = np.empty(NP, dtype=np.int64)
        R3 = np.empty(NP, dtype=np.int64)
        for i in range(NP):
            r = rank_of[i]
            if r == 0:
                R1[i] = ind_best[1]
                R2[i] = ind_best[2]
            elif r == NP - 1:
                R1[i] = ind_best[NP - 3]
                R2[i] = ind_best[NP - 2]
            else:
                R1[i] = ind_best[r - 1]
                R2[i] = ind_best[r + 1]
        for i in range(NP):
            chosen = -1
            for a in range(max_attempts):
                cand = r3_pool[i, a]
                if cand != i and cand != R1[i] and cand != R2[i]:
                    chosen = cand
                    break
            if chosen < 0:
                # Linear scan fallback (statistically unreachable for NP > 4).
                for cand in range(NP):
                    if cand != i and cand != R1[i] and cand != R2[i]:
                        chosen = cand
                        break
            R3[i] = chosen
        return R1, R2, R3
    junior_r1r2r3_core_fast = _junior_r1r2r3_core_nb
else:
    junior_r1r2r3_core_fast = None

# ===================== 10. senior_r1r2r3 =====================
if HAS_NUMBA:
    @njit(cache=True, boundscheck=False, nogil=True)
    def _senior_r1r2r3_nb(ind_best, r1_rand, r2_rand, r3_rand, p):
        """Generate senior mutation index triplets from best/middle/worst groups.

        Partitions the ranked population into three groups and draws one index
        from each. Sequential due to group-boundary computation.

        Parameters
        ----------
        ind_best : ndarray, shape (NP,) - indices sorted by fitness
        r1_rand, r2_rand, r3_rand : ndarray, shape (NP,) - uniform random draws
        p : float - fraction defining group size
        """
        NP = ind_best.shape[0]
        n_grp = int(np.floor(np.abs(p * NP) + 0.5))
        if n_grp < 1: n_grp = 1
        if 2 * n_grp >= NP: n_grp = max(1, (NP - 1) // 2)
        lb = n_grp; lm = NP - 2*n_grp; lw = n_grp
        R1 = np.empty(NP, dtype=np.int64); R2 = np.empty(NP, dtype=np.int64); R3 = np.empty(NP, dtype=np.int64)
        for i in range(NP):
            i1 = int(np.ceil(r1_rand[i]*lb))-1
            if i1 < 0: i1 = 0
            if i1 >= lb: i1 = lb-1
            R1[i] = ind_best[i1]
            i2 = int(np.ceil(r2_rand[i]*lm))-1
            if i2 < 0: i2 = 0
            if i2 >= lm: i2 = lm-1
            R2[i] = ind_best[n_grp+i2]
            i3 = int(np.ceil(r3_rand[i]*lw))-1
            if i3 < 0: i3 = 0
            if i3 >= lw: i3 = lw-1
            R3[i] = ind_best[NP-n_grp+i3]
        return R1, R2, R3
    senior_r1r2r3_fast = _senior_r1r2r3_nb
else:
    senior_r1r2r3_fast = None

# ===================== 11. ace_sample_indices =====================
if HAS_NUMBA:
    @njit(cache=True, boundscheck=False, nogil=True)
    def _ace_sample_nb(probs, u):
        """Sample indices from a discrete distribution via inverse CDF.

        Sequential because of the prefix-sum CDF construction.

        Parameters
        ----------
        probs : ndarray, shape (M,) - probability vector (sums to 1)
        u : ndarray, shape (n,) - uniform random draws in [0, 1)
        """
        M = probs.shape[0]; n = u.shape[0]
        cdf = np.empty(M); cdf[0] = probs[0]
        for j in range(1, M): cdf[j] = cdf[j-1]+probs[j]
        cdf[M-1] = 1.0
        out = np.empty(n, dtype=np.int64)
        for i in range(n):
            v = u[i]
            if M == 2:
                out[i] = 0 if v <= cdf[0] else 1
            elif M == 3:
                if v <= cdf[0]:
                    out[i] = 0
                elif v <= cdf[1]:
                    out[i] = 1
                else:
                    out[i] = 2
            elif M == 4:
                if v <= cdf[0]:
                    out[i] = 0
                elif v <= cdf[1]:
                    out[i] = 1
                elif v <= cdf[2]:
                    out[i] = 2
                else:
                    out[i] = 3
            elif M == 5:
                if v <= cdf[0]:
                    out[i] = 0
                elif v <= cdf[1]:
                    out[i] = 1
                elif v <= cdf[2]:
                    out[i] = 2
                elif v <= cdf[3]:
                    out[i] = 3
                else:
                    out[i] = 4
            elif M == 6:
                if v <= cdf[0]:
                    out[i] = 0
                elif v <= cdf[1]:
                    out[i] = 1
                elif v <= cdf[2]:
                    out[i] = 2
                elif v <= cdf[3]:
                    out[i] = 3
                elif v <= cdf[4]:
                    out[i] = 4
                else:
                    out[i] = 5
            else:
                # Binary search with left-closed bins so exact CDF-boundary
                # draws match the pure-NumPy fallback's ``searchsorted(...,
                # side="left")`` semantics exactly.
                lo = 0
                hi = M - 1
                while lo < hi:
                    mid = (lo + hi) // 2
                    if v <= cdf[mid]:
                        hi = mid
                    else:
                        lo = mid + 1
                out[i] = lo
        return out
    ace_sample_fast = _ace_sample_nb
else:
    ace_sample_fast = None

# ===================== 12. ace_update_probs_full =====================
if HAS_NUMBA:
    @njit(cache=True, boundscheck=False, nogil=True)
    def _ace_update_full_nb(Kw, omega, c, p_min):
        """Update ACE strategy probabilities with momentum blending.

        Blends current weights Kw with a target derived from the omega
        improvement vector. Sequential because it delegates to the sequential
        _ace_project_probs_nb.

        Parameters
        ----------
        Kw : ndarray, shape (M,) - current strategy weights
        omega : ndarray, shape (M,) - strategy improvement signals
        c : float - learning rate (blend towards target)
        p_min : float - minimum probability floor
        """
        M = Kw.shape[0]; s = 0.0
        for i in range(M): s += omega[i]
        if not np.isfinite(s) or s == 0.0: return _ace_project_probs_nb(Kw.copy(), p_min)
        if s >= 0.0:
            s_imp = 0.0
            for i in range(M):
                if omega[i] < 0.0: s_imp += omega[i]
            if s_imp == 0.0 or not np.isfinite(s_imp): return _ace_project_probs_nb(Kw.copy(), p_min)
            target = np.empty(M)
            for i in range(M): target[i] = omega[i]/s_imp if omega[i] < 0.0 else 0.0
        else:
            target = np.empty(M)
            for i in range(M): target[i] = omega[i]/s
        target = _ace_project_probs_nb(target, p_min)
        out = np.empty(M)
        for i in range(M): out[i] = (1.0-c)*Kw[i] + c*target[i]
        return _ace_project_probs_nb(out, p_min)
    ace_update_full_fast = _ace_update_full_nb
else:
    ace_update_full_fast = None

# (sections 13-18 â€” CEC2017 base-function kernels and shift_rotate_fast â€”
# moved to benchmarks/cec_suite_python/cec2017/_numba.py.)

# ===================== 19. PSR target =====================
if HAS_NUMBA:
    @njit(cache=True, boundscheck=False, nogil=True)
    def _psr_target_nb(n_init, n_min, nfes_used, max_nfes, schedule_code, alpha):
        """Compute target population size for Population Size Reduction.

        Implements linear, non-linear, and alpha-decay schedules.
        Sequential scalar computation -- no parallelism needed.

        Parameters
        ----------
        n_init : int - initial population size
        n_min : int - minimum population size
        nfes_used : int - function evaluations consumed so far
        max_nfes : int - total budget of function evaluations
        schedule_code : int - 0=linear, 1=non-linear, 2=alpha-decay
        alpha : float - decay exponent (only used when schedule_code == 2)
        """
        if max_nfes <= 0: return max(n_min, n_init)
        frac = float(nfes_used)/float(max_nfes)
        if frac < 0.0: frac = 0.0
        if frac > 1.0: frac = 1.0
        if schedule_code == 0:
            desired = float(n_min-n_init)/float(max_nfes)*float(nfes_used)+float(n_init)
        elif schedule_code == 1:
            if frac <= 0.0: nl = 0.0
            elif frac >= 1.0: nl = 1.0
            else: nl = frac**(1.0-frac)
            desired = float(n_init)+float(n_min-n_init)*nl
        else:
            desired = float(n_min)+float(n_init-n_min)*(1.0-frac**alpha)
        return int(np.floor(desired+0.5))
    psr_target_fast = _psr_target_nb
else:
    psr_target_fast = None

# ===================== 20. dim_coverage =====================
if HAS_NUMBA:
    @njit(cache=True, parallel=True, fastmath=True, boundscheck=False, nogil=True)
    def _dim_coverage_nb(D_J, D_S, NP, D):
        """Compute per-individual fraction of dimensions covered by any mask.

        Parameters
        ----------
        D_J : ndarray, shape (NP, D) - junior boolean mask
        D_S : ndarray, shape (NP, D) - senior boolean mask
        NP : int - population size
        D : int - dimensionality
        """
        out = np.empty(NP, dtype=np.float64); inv_d = 1.0/D
        for i in prange(NP):
            c = 0
            for j in range(D):
                if D_J[i,j] or D_S[i,j]: c += 1
            out[i] = c*inv_d
        return out
    dim_coverage_fast = _dim_coverage_nb
else:
    dim_coverage_fast = None

# ===================== 20a. accept_and_top_bottom_stats =====================
# H3: replace 5 separate np.sum / np.logical_and calls in the main loop
# (`accepted`, `n_top`, `top_succ`, `bot_succ`, `top_reward_sum`,
# `bot_reward_sum`) with a single fused JIT pass.  All inputs are NP-sized
# bool/float arrays â€” sequential, no prange (NP is tiny: 12-200).
if HAS_NUMBA:
    @njit(cache=True, boundscheck=False, nogil=True)
    def _accept_top_bottom_stats_nb(improved, top_half_mask, relative_rewards):
        """Single-pass fused reduction over (improved, top_half_mask, rel_rewards).

        Returns
        -------
        accepted : int64       â€” total ``improved.sum()``
        n_top : int64          â€” total ``top_half_mask.sum()``
        top_succ : int64       â€” ``(improved & top_half_mask).sum()``
        bot_succ : int64       â€” ``(improved & ~top_half_mask).sum()``
        top_reward : float64   â€” ``relative_rewards[top_half_mask].sum()``
        bot_reward : float64   â€” ``relative_rewards[~top_half_mask].sum()``

        Replaces five separate ``np.sum``/``np.logical_and`` calls in the
        main optimization loop with one tight scalar pass.  Both halves are
        complementary (``bot_half = ~top_half``), so the inner branch costs
        a single bool test.
        """
        n = improved.shape[0]
        accepted = 0
        n_top = 0
        top_succ = 0
        bot_succ = 0
        top_reward = 0.0
        bot_reward = 0.0
        for i in range(n):
            imp_i = improved[i]
            if imp_i:
                accepted += 1
            if top_half_mask[i]:
                n_top += 1
                top_reward += relative_rewards[i]
                if imp_i:
                    top_succ += 1
            else:
                bot_reward += relative_rewards[i]
                if imp_i:
                    bot_succ += 1
        return accepted, n_top, top_succ, bot_succ, top_reward, bot_reward

    def accept_top_bottom_stats_fast(improved, top_half_mask, relative_rewards):
        """Wrapper for the fused (improved/top/reward) reduction."""
        return _accept_top_bottom_stats_nb(improved, top_half_mask, relative_rewards)

    @njit(cache=True, boundscheck=False, nogil=True)
    def _count_true_nb(mask):
        """Single-pass scalar count of True values in a 1D bool array."""
        n = mask.shape[0]
        c = 0
        for i in range(n):
            if mask[i]:
                c += 1
        return c

    def count_true_fast(mask):
        """Wrapper for fast bool-array popcount."""
        return _count_true_nb(mask)
else:
    accept_top_bottom_stats_fast = None
    count_true_fast = None

# ===================== 20b. ace_bincount_fused =====================
# H1: replace 9 separate ``np.bincount`` calls in the ACE update path with
# one tight scalar pass.  All inputs are NP-sized, so this collapses 9
# memory passes into 1 â€” at NP=200 that is 9 Ã— 200 = 1800 array reads
# down to 200 + 9 small writes per generation.
#
# Inputs (length NP):
#   s_idx        (int64)  â€” ACE entry index per individual
#   improved     (bool)   â€” was the trial accepted?
#   top_mask     (bool)   â€” top half of population
#   bot_mask     (bool)   â€” bottom half of population
#   rewards      (float64)â€” relative-improvement reward per individual
#
# Outputs (length M = ACE pool size, typically 5-7):
#   sample, success, reward
#   sample_top, sample_bot
#   success_top, success_bot
#   reward_top, reward_bot
#
# Bit-identical to the NumPy bincount path because the iteration order over
# ``s_idx`` is the same and float accumulation is performed in the same
# index sequence.  Safe for the seed-locked main loop.
if HAS_NUMBA:
    @njit(cache=True, boundscheck=False, nogil=True)
    def _ace_bincount_fused_nb(s_idx, improved, top_mask, bot_mask, rewards, M):
        """Single-pass fused 9-output bincount over ACE-related per-individual arrays."""
        n = s_idx.shape[0]
        sample = np.zeros(M, dtype=np.int64)
        success = np.zeros(M, dtype=np.int64)
        reward = np.zeros(M, dtype=np.float64)
        sample_top = np.zeros(M, dtype=np.int64)
        sample_bot = np.zeros(M, dtype=np.int64)
        success_top = np.zeros(M, dtype=np.int64)
        success_bot = np.zeros(M, dtype=np.int64)
        reward_top = np.zeros(M, dtype=np.float64)
        reward_bot = np.zeros(M, dtype=np.float64)

        for i in range(n):
            e = s_idx[i]
            r = rewards[i]
            imp_i = improved[i]
            top_i = top_mask[i]
            bot_i = bot_mask[i]

            sample[e] += 1
            reward[e] += r
            if imp_i:
                success[e] += 1

            if top_i:
                sample_top[e] += 1
                reward_top[e] += r
                if imp_i:
                    success_top[e] += 1

            if bot_i:
                sample_bot[e] += 1
                reward_bot[e] += r
                if imp_i:
                    success_bot[e] += 1

        return (
            sample, success, reward,
            sample_top, sample_bot,
            success_top, success_bot,
            reward_top, reward_bot,
        )

    def ace_bincount_fused_fast(s_idx, improved, top_mask, bot_mask, rewards, M):
        """Wrapper for the fused 9-output ACE bincount kernel."""
        return _ace_bincount_fused_nb(s_idx, improved, top_mask, bot_mask, rewards, int(M))
else:
    ace_bincount_fused_fast = None

# ===================== 20c. ig_scatter_add (G3) =====================
# Hybrid numba kernel for ``ig_update_from_accepted`` in
# ``gsk/interaction_graph.py``. Caller keeps the FP-sensitive reductions
# (``np.sum`` for ``denom``, ``np.flatnonzero`` for ``idx``, and the division
# that builds ``vec_abs`` / ``vec_signed``) in NumPy so the pairwise-sum
# semantics of ``denom`` are preserved exactly. This kernel only performs
# the two outer-product scatter-adds + the diagonal rank-1 add.
#
# Bit-identity notes
# ------------------
# * The scatter target slots are disjoint within a single sample (all
#   ``idx`` are distinct), so iteration order of (p, q) is irrelevant
#   for the result.
# * Inner multiply order is parenthesised as ``w * (va_p * va_q)`` to
#   match NumPy's ``w * sub_abs`` where ``sub_abs = np.outer(vec, vec)``.
# * ``fastmath=False``: no FP reassociation allowed â€” ``(a*b)*c`` and
#   ``a*(b*c)`` may differ bit-wise.
# * No ``parallel=True``: the outer sample loop runs sequentially so
#   cross-sample accumulation order is deterministic.
if HAS_NUMBA:
    @njit(cache=True, fastmath=False, boundscheck=False, nogil=True)
    def _ig_scatter_add_nb(idx, w, sample_w, vec_abs, vec_signed,
                            agg, agg_signed, agg_diag, agg_support):
        """Apply one sample's weighted rank-1 outer-product updates.

        Equivalent to the NumPy block::

            agg_diag[idx] += w * vec_abs
            if k >= 2:
                sub_abs = np.outer(vec_abs, vec_abs)
                sub_signed = np.outer(vec_signed, vec_signed)
                np.fill_diagonal(sub_abs, 0.0)
                np.fill_diagonal(sub_signed, 0.0)
                sub_support = ones_minus_identity(k)
                _ij = np.ix_(idx, idx)
                agg[_ij] += w * sub_abs
                agg_signed[_ij] += w * sub_signed
                agg_support[_ij] += sample_w * sub_support
        """
        k = idx.shape[0]
        # Diagonal update (all k).
        for p in range(k):
            jp = idx[p]
            agg_diag[jp] += w * vec_abs[p]
        # Off-diagonal outer-product scatter. Skip when k < 2.
        if k >= 2:
            for p in range(k):
                jp = idx[p]
                vap = vec_abs[p]
                vsp = vec_signed[p]
                for q in range(k):
                    if p == q:
                        continue
                    jq = idx[q]
                    agg[jp, jq] += w * (vap * vec_abs[q])
                    agg_signed[jp, jq] += w * (vsp * vec_signed[q])
                    agg_support[jp, jq] += sample_w

    ig_scatter_add_fast = _ig_scatter_add_nb
else:
    ig_scatter_add_fast = None

# ----------------------------------------------------------------------
# Section 20d (NB-1): fused interaction-graph symmetrise kernels.
# ----------------------------------------------------------------------
# Byte-identity contract (must hold vs the NumPy bodies in
# ``interaction_graph._symmetrise_nonneg`` / ``_symmetrise_signed``):
#
#   NumPy:   A = 0.5 * (W + W.T);  [nonneg: np.maximum(A, 0.0)];  diag = 0.0
#
# * Each output cell is ``0.5 * (W[i, j] + W[j, i])`` â€” exactly one IEEE add
#   followed by one multiply on the same two operands.  FP add is
#   commutative, so the (i, j) and (j, i) cells receive the identical value;
#   ``fastmath=False`` forbids any FMA / reassociation, so the bit pattern
#   matches NumPy's ``0.5 * (A + A.T)`` cell-for-cell.
# * The diagonal is forced to ``0.0`` in both paths.
# * nonneg clamps with ``max(v, 0.0)``; for the finite values produced by the
#   aggregator this equals ``np.maximum(v, 0.0)``.  (NaN is never produced on
#   the live path â€” the aggregator guards ``denom > TOL`` â€” so the
#   ``max(NaN, 0)`` vs ``np.maximum(NaN, 0)`` divergence is unreachable here.)
# * No ``parallel=True`` (see NB-3): a plain sequential nested loop; output is
#   a fresh contiguous array, matching the NumPy functions which return a new
#   array.
if HAS_NUMBA:
    @njit(cache=True, fastmath=False, boundscheck=False, nogil=True)
    def _ig_symmetrise_nonneg_nb(W):
        n = W.shape[0]
        A = np.empty((n, n), dtype=np.float64)
        for i in range(n):
            A[i, i] = 0.0
            for j in range(i + 1, n):
                v = 0.5 * (W[i, j] + W[j, i])
                if v < 0.0:
                    v = 0.0
                A[i, j] = v
                A[j, i] = v
        return A

    @njit(cache=True, fastmath=False, boundscheck=False, nogil=True)
    def _ig_symmetrise_signed_nb(W):
        n = W.shape[0]
        A = np.empty((n, n), dtype=np.float64)
        for i in range(n):
            A[i, i] = 0.0
            for j in range(i + 1, n):
                v = 0.5 * (W[i, j] + W[j, i])
                A[i, j] = v
                A[j, i] = v
        return A

    # MEM2-1: in-place symmetrise.  Identical arithmetic to the two kernels
    # above (one IEEE add + one multiply on the same operands, fastmath=False,
    # zero diagonal), but writes back into ``M`` instead of allocating a fresh
    # array -- so the per-update-gen DxD allocations in ig_update_from_accepted
    # are eliminated.  READ-BEFORE-WRITE is mandatory: both ``M[i, j]`` and
    # ``M[j, i]`` are read into the same expression *before* either cell is
    # written; the loop only visits ``j > i`` and never revisits a cell, so a
    # single per-iteration read suffices and no later read is corrupted.
    @njit(cache=True, fastmath=False, boundscheck=False, nogil=True)
    def _ig_symmetrise_inplace_nb(M, nonneg):
        n = M.shape[0]
        for i in range(n):
            for j in range(i + 1, n):
                a = M[i, j]
                b = M[j, i]
                v = 0.5 * (a + b)
                if nonneg and v < 0.0:
                    v = 0.0
                M[i, j] = v
                M[j, i] = v
            M[i, i] = 0.0

    # R3M-2/R3F-3: fuse SGSM passive-decay multiplies.  This is pure
    # elementwise ``x *= decay`` over three DxD matrices plus the D-vector
    # diagonal.  There is no reduction and fastmath stays False, so each cell
    # receives the same IEEE scalar multiply as the four NumPy ``*=`` calls in
    # ``interaction_graph._apply_decay``.
    @njit(cache=True, fastmath=False, boundscheck=False, nogil=True)
    def _ig_apply_decay_nb(matrix, signed_matrix, support, diag, decay):
        n = matrix.shape[0]
        m = matrix.shape[1]
        for i in range(n):
            diag[i] *= decay
            for j in range(m):
                matrix[i, j] *= decay
                signed_matrix[i, j] *= decay
                support[i, j] *= decay

    # ADJ-1: deterministic top-k adjacency builder for SGSM block extraction.
    # It matches ``np.argsort(-row, kind="stable")`` semantics by ordering
    # candidates as (weight desc, index asc), while avoiding 100 small NumPy
    # sorts per D=100 refresh.
    @njit(cache=True, fastmath=False, boundscheck=False, nogil=True)
    def _ig_build_adj_topk_nb(Wn, edge_floor, max_group_size, adj_bool):
        d = Wn.shape[0]
        top_k_cap = int(max_group_size) - 1
        if top_k_cap <= 0:
            return
        floor_f = float(edge_floor)
        for i in range(d):
            row_max = 0.0
            for j in range(d):
                v = Wn[i, j]
                if v > row_max:
                    row_max = v
            if row_max <= 0.0:
                continue
            threshold = row_max * 0.5
            if threshold < floor_f:
                threshold = floor_f

            keep_count = 0
            for j in range(d):
                if Wn[i, j] >= threshold:
                    keep_count += 1
            if keep_count == 0:
                selected = 0
                best_idx = np.empty(top_k_cap, dtype=np.int64)
                best_val = np.empty(top_k_cap, dtype=np.float64)
                for j in range(d):
                    v = Wn[i, j]
                    if v <= 0.0:
                        continue
                    pos = selected
                    if selected < top_k_cap:
                        selected += 1
                    else:
                        worst_val = best_val[top_k_cap - 1]
                        worst_idx = best_idx[top_k_cap - 1]
                        if v < worst_val or (v == worst_val and j >= worst_idx):
                            continue
                        pos = top_k_cap - 1
                    while pos > 0:
                        pv = best_val[pos - 1]
                        pi = best_idx[pos - 1]
                        if pv > v or (pv == v and pi < j):
                            break
                        if pos < top_k_cap:
                            best_val[pos] = best_val[pos - 1]
                            best_idx[pos] = best_idx[pos - 1]
                        pos -= 1
                    best_val[pos] = v
                    best_idx[pos] = j
                for t in range(selected):
                    adj_bool[i, best_idx[t]] = True
            elif keep_count <= top_k_cap:
                for j in range(d):
                    if Wn[i, j] >= threshold:
                        adj_bool[i, j] = True
            else:
                selected = 0
                best_idx = np.empty(top_k_cap, dtype=np.int64)
                best_val = np.empty(top_k_cap, dtype=np.float64)
                for j in range(d):
                    v = Wn[i, j]
                    if v < threshold:
                        continue
                    pos = selected
                    if selected < top_k_cap:
                        selected += 1
                    else:
                        worst_val = best_val[top_k_cap - 1]
                        worst_idx = best_idx[top_k_cap - 1]
                        if v < worst_val or (v == worst_val and j >= worst_idx):
                            continue
                        pos = top_k_cap - 1
                    while pos > 0:
                        pv = best_val[pos - 1]
                        pi = best_idx[pos - 1]
                        if pv > v or (pv == v and pi < j):
                            break
                        if pos < top_k_cap:
                            best_val[pos] = best_val[pos - 1]
                            best_idx[pos] = best_idx[pos - 1]
                        pos -= 1
                    best_val[pos] = v
                    best_idx[pos] = j
                for t in range(selected):
                    adj_bool[i, best_idx[t]] = True

    ig_symmetrise_nonneg_fast = _ig_symmetrise_nonneg_nb
    ig_symmetrise_signed_fast = _ig_symmetrise_signed_nb
    ig_symmetrise_inplace_fast = _ig_symmetrise_inplace_nb
    ig_apply_decay_fast = _ig_apply_decay_nb
    ig_build_adj_topk_fast = _ig_build_adj_topk_nb
else:
    ig_symmetrise_nonneg_fast = None
    ig_symmetrise_signed_fast = None
    ig_symmetrise_inplace_fast = None
    ig_apply_decay_fast = None
    ig_build_adj_topk_fast = None

# Zero-allocation within-set row-sum for interaction-graph block extraction
# (``interaction_graph._split_component``). CR-0009.
#
# ``_split_component`` re-derives the within-set row-sums
# ``Wn[rem][:, rem].sum(axis=1)`` on every greedy iteration to pick each block
# seed by ``argmax``. The shipped NumPy form materialises a fresh
# ``|rem| x |rem|`` submatrix per iteration -- the profiled D=1000 hot spot
# (~240 MB of copies per call, ~80% of LSGO wall time). This kernel computes
# the same row-sums reading ``Wn`` through ``idx`` with no submatrix allocation.
#
# Bit-identity notes
# ------------------
# * The reference is a FANCY-INDEXED reduction: ``Wn[idx][:, idx]`` is advanced
#   integer indexing, and NumPy evaluates ``.sum(axis=1)`` on that result with
#   its NAIVE strided loop (left-to-right in ``idx`` order), NOT the pairwise
#   SIMD path used for plain C-contiguous arrays. Verified with a crafted
#   ``[1e16, 1, 1, ...]`` row: the fancy form returns ``1e16`` (naive) while the
#   plain form returns ``1.0000000000001008e16`` (pairwise).
# * This kernel accumulates left-to-right in the same ``idx`` order, so it
#   reproduces the reference to the last bit -- confirmed on 848 real +
#   adversarial cases (max abs diff 0.0) and end-to-end (cec2017 F3/F5 D50,
#   F3 D100, LSGO F1 D1000: best_fitness all bit-identical).
# * ``fastmath=False`` forbids FP reassociation; no ``parallel`` so the
#   accumulation order is fixed and deterministic.
if HAS_NUMBA:
    @njit(cache=True, fastmath=False, boundscheck=False, nogil=True)
    def _ig_component_rowsum_nb(Wn, idx):
        """Within-set row-sums ``out[a] = sum_b Wn[idx[a], idx[b]]`` (naive order).

        Bit-identical to ``Wn[idx][:, idx].sum(axis=1)`` (fancy-indexed ->
        NumPy naive strided reduction) with no submatrix allocation.
        """
        m = idx.shape[0]
        out = np.zeros(m, dtype=np.float64)
        for a in range(m):
            ia = idx[a]
            s = 0.0
            for b in range(m):
                s += Wn[ia, idx[b]]
            out[a] = s
        return out

    ig_component_rowsum_fast = _ig_component_rowsum_nb
else:
    ig_component_rowsum_fast = None

# (sections 21-34 â€” CEC2017 schwefel/elliptic/.../cf_cal kernels â€”
# moved to benchmarks/cec_suite_python/cec2017/_numba.py.
# CEC2020 raw kernels and shift_rotate_2020_fast â€” moved to
# benchmarks/cec_suite_python/cec2020/_numba.py.)

# ===================== Warmup =====================

if HAS_NUMBA:

    @njit(cache=True, boundscheck=False, nogil=True)
    def _compose_trial_nb(pop, vi_junior, vi_senior, d_j, d_s, out):
        """Fused trial assembly: out = D_S ? senior : (D_J ? junior : pop).

        W2.2 (2026-07-25). Replaces ``np.copyto(ui, pop); ui[D_J] = vi_junior[D_J];
        ui[D_S] = vi_senior[D_S]`` -- a full NP*D copy plus TWO boolean
        fancy-index gather/scatter pairs (each materialising index arrays and
        masked temporaries) -- with one branchy pass and zero allocations.
        Microbenched: 2353 -> 469 us/gen at NP=100, D=1000 (80% saved).

        Bit-identical for EVERY mask combination, not only disjoint ones: the
        sequential writes end with vi_senior wherever D_S is True (it is
        written last), vi_junior where only D_J, pop where neither -- exactly
        this kernel's selection. Pure selection, no arithmetic.
        """
        n = pop.shape[0]
        d = pop.shape[1]
        for i in range(n):
            for j in range(d):
                if d_s[i, j]:
                    out[i, j] = vi_senior[i, j]
                elif d_j[i, j]:
                    out[i, j] = vi_junior[i, j]
                else:
                    out[i, j] = pop[i, j]

    compose_trial_fast = _compose_trial_nb
else:  # pragma: no cover - numba is a declared dependency
    compose_trial_fast = None


def warmup():
    """Trigger JIT compilation of all optimizer kernels with small dummy inputs.

    Called once per worker process by :func:`gsk.experiment.run_experiments`
    (and :func:`gsk.benchmark_factory.init_cec_worker`) so that subsequent
    calls to any ``*_fast`` function do not pay the compilation cost. Skipped
    gracefully when numba is not installed.

    Benchmark-suite kernels have their own ``warmup()`` entry points in
    ``benchmarks.cec_suite_python.cec{2017,2013,2011,2020,2013lsgo}._numba``;
    they are invoked from the same worker-init path so every hot kernel
    is JIT-cached before the first generation runs.
    """
    if not HAS_NUMBA: return
    n, d = 4, 3
    vi=np.random.randn(n,d).copy(); pop=np.random.randn(n,d); lu=np.array([[-100.]*d,[100.]*d])
    _bound_constraint_nb(vi,pop,lu[0],lu[1]); span=np.full(d,200.); _pop_radius_nb(pop,span)
    _compose_trial_nb(pop, vi, vi, np.zeros((n,d),dtype=np.bool_), np.ones((n,d),dtype=np.bool_), np.empty((n,d)))
    p=np.array([.2,.3,.5]); _ace_project_probs_nb(p,.05)
    xs=np.random.randn(5,d); x=np.random.randn(d); iv=np.full(d,1./200.); isd=1./np.sqrt(d)
    _archive_dists_nb(xs,3,x,iv,isd); fs=np.random.randn(5); _archive_consider_nb(xs,fs,2,5,x,1.,iv,isd,.05)
    _archive_consider_batch_nb(xs.copy(),fs.copy(),2,5,np.random.randn(2,d),np.random.randn(2),iv,isd,.05)
    fit=np.random.randn(n); idx=np.arange(n,dtype=np.int64); vj=np.empty((n,d)); vs=np.empty((n,d))
    kf=np.full(n,.5); _build_junior_senior_nb(pop,fit,kf,idx,idx,idx,idx,idx,idx,vj,vs)
    _build_junior_senior_with_repair_nb(pop,fit,kf,idx,idx,idx,idx,idx,idx,lu[0],lu[1],vj,vs)
    rj=np.random.rand(n,d); dj=np.zeros((n,d),dtype=np.bool_); ds=np.zeros((n,d),dtype=np.bool_)
    _build_masks_scalar_nb(rj,rj.copy(),rj.copy(),np.full(n,.5),np.full(n,.9),n,d,dj,ds)
    bj=np.random.rand(n,2); bg=np.random.rand(n,2); bri=np.arange(n,dtype=np.int64)
    gflat=np.array([0,1,2],dtype=np.int64); goff=np.array([0,1,3],dtype=np.int64)
    _build_masks_blockwise_nb(bj,bg,np.full(n,.5),np.full(n,.9),bri,gflat,goff,dj.copy(),ds.copy())
    ib=np.arange(n,dtype=np.int64); r3p=np.zeros((n,4),dtype=np.int64); _junior_r1r2r3_core_nb(ib,r3p)
    ur=np.random.rand(n); _senior_r1r2r3_nb(ib,ur,ur.copy(),ur.copy(),.1)
    _ace_sample_nb(p,ur); om=np.array([-.1,.2,-.3]); _ace_update_full_nb(p.copy(),om,.1,.05)
    _psr_target_nb(150,12,1000,300000,1,1.); _dim_coverage_nb(dj,ds,n,d)
    _imp=np.array([True,False,True,False],dtype=np.bool_); _top=np.array([True,True,False,False],dtype=np.bool_)
    _rew=np.array([1.0,2.0,3.0,4.0],dtype=np.float64)
    _accept_top_bottom_stats_nb(_imp,_top,_rew); _count_true_nb(_top)
    # Warm _ace_bincount_fused_nb (section 20b)
    _s_idx_w = np.array([0, 1, 0], dtype=np.int64)
    _imp_w = np.array([True, False, True])
    _top_w = np.array([True, True, False])
    _bot_w = np.array([False, False, True])
    _rew_w = np.array([0.1, 0.0, 0.2])
    _ace_bincount_fused_nb(_s_idx_w, _imp_w, _top_w, _bot_w, _rew_w, 2)
    # Warm _ig_scatter_add_nb (section 20c / G3)
    _ig_idx_w = np.array([0, 1, 2], dtype=np.int64)
    _ig_vec_a = np.array([0.2, 0.3, 0.5], dtype=np.float64)
    _ig_vec_s = np.array([0.1, -0.3, 0.5], dtype=np.float64)
    _ig_agg = np.zeros((4, 4), dtype=np.float64)
    _ig_sig = np.zeros((4, 4), dtype=np.float64)
    _ig_dia = np.zeros(4, dtype=np.float64)
    _ig_sup = np.zeros((4, 4), dtype=np.float64)
    _ig_scatter_add_nb(_ig_idx_w, 0.5, 0.25, _ig_vec_a, _ig_vec_s, _ig_agg, _ig_sig, _ig_dia, _ig_sup)
    # Warm NB-1 symmetrise kernels (section 20d).
    _ig_sym_w = np.array([[0.0, 1.0, -2.0],
                          [3.0, 0.0, 0.5],
                          [-1.0, 0.25, 0.0]], dtype=np.float64)
    _ig_symmetrise_nonneg_nb(_ig_sym_w)
    _ig_symmetrise_signed_nb(_ig_sym_w)
    # Warm MEM2-1 in-place symmetrise (writes into its argument -> use a copy).
    _ig_symmetrise_inplace_nb(_ig_sym_w.copy(), True)
    _ig_symmetrise_inplace_nb(_ig_sym_w.copy(), False)
    # Warm R3M-2/R3F-3 fused SGSM passive decay.
    _ig_decay_m = _ig_sym_w.copy()
    _ig_decay_s = _ig_sym_w.copy()
    _ig_decay_sup = np.abs(_ig_sym_w.copy())
    _ig_decay_diag = np.array([1.0, -0.5, 0.25], dtype=np.float64)
    _ig_apply_decay_nb(_ig_decay_m, _ig_decay_s, _ig_decay_sup, _ig_decay_diag, 0.95)
    _ig_adj = np.zeros((3, 3), dtype=np.bool_)
    _ig_build_adj_topk_nb(np.abs(_ig_sym_w), 1e-4, 2, _ig_adj)
    # Warm CR-0009 zero-alloc component row-sum kernel.
    _ig_rs_w = np.array([[1.0, 2.0, 3.0],
                         [2.0, 1.0, 4.0],
                         [3.0, 4.0, 1.0]], dtype=np.float64)
    _ig_component_rowsum_nb(_ig_rs_w, np.array([0, 2], dtype=np.int64))
