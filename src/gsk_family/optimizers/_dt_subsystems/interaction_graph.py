"""Deterministic success-graph structural memory for DT-GSK.

This module implements a lightweight, non-learning interaction memory that is
updated from successful moves and can be used in shadow mode for diagnostics,
for learned linkage blocks, and for block-aware local-search subspace
selection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Iterable

import numpy as np

try:
    from ._numba_accel import (
        ig_scatter_add_fast,
        ig_symmetrise_nonneg_fast,
        ig_symmetrise_signed_fast,
        ig_symmetrise_inplace_fast,
        ig_apply_decay_fast,
        ig_build_adj_topk_fast,
        ig_component_rowsum_fast,
    )
except ImportError:
    ig_scatter_add_fast = None
    ig_symmetrise_nonneg_fast = None
    ig_symmetrise_signed_fast = None
    ig_symmetrise_inplace_fast = None
    ig_apply_decay_fast = None
    ig_build_adj_topk_fast = None
    ig_component_rowsum_fast = None


@dataclass(slots=True)
class InteractionGraphState:
    dim: int
    matrix: np.ndarray
    signed_matrix: np.ndarray
    diag: np.ndarray
    support: np.ndarray
    blocks: tuple[np.ndarray, ...]
    block_confidence: np.ndarray
    overall_confidence: float
    nontrivial_dims: int = 0
    updates: int = 0
    refresh_count: int = 0
    last_refresh_gen: int = 0
    # Rolling history of ``overall_confidence`` written once per refresh. Used
    # only by the adaptive-gate path (``ig_adaptive_threshold``); the static
    # gate path reads nothing from this buffer so its presence is a no-op for
    # any variant that keeps ``interaction_confidence_adaptive=False``.
    confidence_history: list[float] = field(default_factory=list)
    # A3: per-state cache for ``ig_adaptive_threshold``. The function is pure
    # in ``(confidence_history, params)`` and is called once per generation,
    # while ``confidence_history`` only grows on refresh (~1 append per 5
    # gens). Caching by ``(refresh_count, params)`` cuts the per-gen
    # ``np.quantile`` cost without changing any returned value.
    _adaptive_thr_cache_key: tuple | None = None
    _adaptive_thr_cache_val: float = 0.0
    # H1/H2/H3: per-state reusable buffers to avoid per-call allocation in
    # hot paths. Lazily allocated on first use, then reused via ``fill(0.0)``.
    # Shapes are fixed by ``state.dim``; ``_abs_x_buf`` grows as needed by NP.
    # Bit-identical because content is fully overwritten before read on every
    # call (zero-filled at top of ``ig_update_from_accepted`` / per-refresh).
    _agg_buf: np.ndarray | None = None
    _agg_signed_buf: np.ndarray | None = None
    _agg_diag_buf: np.ndarray | None = None
    _agg_support_buf: np.ndarray | None = None
    _adj_bool_buf: np.ndarray | None = None
    _abs_x_buf: np.ndarray | None = None


@dataclass(slots=True)
class InteractionGraphStats:
    density: float
    max_weight: float
    mean_weight: float
    nonzero_edges: int
    block_count: int
    mean_block_confidence: float
    nontrivial_dim_fraction: float
    orphan_dim_fraction: float
    refresh_count: int


_DEF_TOL = 1e-15

# H2: module-level cache for the boolean adjacency working buffer, keyed by
# ``d``. ``_build_adjacency_from_topk`` is called once per IG refresh with a
# fixed ``d`` = state.dim, so a single buffer is reused thousands of times
# per trajectory. Bit-identical: the buffer is fully ``fill(False)``-reset
# before any writes, so no stale state leaks. Keys are small positive ints.
_ADJ_BOOL_CACHE: dict[int, np.ndarray] = {}


def _adj_bool_scratch(d: int) -> np.ndarray:
    buf = _ADJ_BOOL_CACHE.get(d)
    if buf is None:
        buf = np.empty((d, d), dtype=bool)
        _ADJ_BOOL_CACHE[d] = buf
    return buf

# A2: module-level cache for ``np.triu_indices(k, k=1)`` by block size ``k``.
# Block sizes cluster on a small range (``min_block_size``..``max_block_size``,
# typically 2..12), so the same ``triu_indices`` result is returned many times
# per refresh. ``np.triu_indices`` returns newly-allocated arrays on every
# call; caching by ``k`` gives identical arrays (bit-identical indexing) while
# eliminating the rebuild cost. Keys are small positive ints, so the dict is
# tiny and grows bounded by ``max_block_size``.
_TRIU_K1_CACHE: dict[int, tuple[np.ndarray, np.ndarray]] = {}


def _triu_k1_cached(k: int) -> tuple[np.ndarray, np.ndarray]:
    idx = _TRIU_K1_CACHE.get(k)
    if idx is None:
        idx = np.triu_indices(k, k=1)
        _TRIU_K1_CACHE[k] = idx
    return idx


# B2: cache the ``ones(k, k) with zero diagonal`` template used as the
# support increment mask in ``ig_update_from_accepted``. The mask depends
# only on the block size ``k``; ``sample_w`` applies as a scalar multiplier
# at write time. Keys are small positive ints bounded by ``state.dim``, so
# the dict stays small. The cached array is treated as read-only by callers
# (only referenced in ``sample_w * template`` which allocates a fresh result),
# so sharing does not leak aliasing.
_ONES_MINUS_I_CACHE: dict[int, np.ndarray] = {}


def _ones_minus_identity(k: int) -> np.ndarray:
    arr = _ONES_MINUS_I_CACHE.get(k)
    if arr is None:
        arr = np.ones((k, k), dtype=np.float64)
        np.fill_diagonal(arr, 0.0)
        _ONES_MINUS_I_CACHE[k] = arr
    return arr


def ig_init(dim: int) -> InteractionGraphState:
    d = int(dim)
    if d <= 0:
        raise ValueError(f"dim must be positive (got {dim!r})")
    return InteractionGraphState(
        dim=d,
        matrix=np.zeros((d, d), dtype=np.float64),
        signed_matrix=np.zeros((d, d), dtype=np.float64),
        diag=np.zeros((d,), dtype=np.float64),
        support=np.zeros((d, d), dtype=np.float64),
        blocks=tuple(),
        block_confidence=np.zeros((0,), dtype=np.float64),
        overall_confidence=0.0,
        nontrivial_dims=0,
        updates=0,
        refresh_count=0,
        last_refresh_gen=0,
    )



def _symmetrise_nonneg(W: np.ndarray) -> np.ndarray:
    # NB-1: fused njit element-wise symmetrise (bit-identical to the NumPy
    # body below).  Every caller -- the per-gen ``state.matrix``/``support``
    # symmetrise (ig_update_from_accepted), ``_normalised_graph``, and the
    # ``ig_extract_blocks`` k×k submatrix path -- routes through here, so the
    # kernel-vs-fallback choice is uniform across all call sites.
    if ig_symmetrise_nonneg_fast is not None:
        A = np.ascontiguousarray(W, dtype=np.float64)
        return ig_symmetrise_nonneg_fast(A)
    A = np.asarray(W, dtype=np.float64)
    A = 0.5 * (A + A.T)
    np.maximum(A, 0.0, out=A)
    np.fill_diagonal(A, 0.0)
    return A



def _symmetrise_signed(W: np.ndarray) -> np.ndarray:
    if ig_symmetrise_signed_fast is not None:
        A = np.ascontiguousarray(W, dtype=np.float64)
        return ig_symmetrise_signed_fast(A)
    A = np.asarray(W, dtype=np.float64)
    A = 0.5 * (A + A.T)
    np.fill_diagonal(A, 0.0)
    return A



def _apply_decay(state: InteractionGraphState, decay: float) -> None:
    decay_f = float(decay)
    if ig_apply_decay_fast is not None:
        ig_apply_decay_fast(
            state.matrix,
            state.signed_matrix,
            state.support,
            state.diag,
            decay_f,
        )
    else:
        state.matrix *= decay_f
        state.signed_matrix *= decay_f
        state.diag *= decay_f
        state.support *= decay_f



def ig_apply_restart_decay(state: InteractionGraphState, *, factor: float) -> InteractionGraphState:
    if not isinstance(state, InteractionGraphState):
        raise TypeError("state must be InteractionGraphState")
    fac = float(factor)
    if not math.isfinite(fac) or fac < 0.0 or fac > 1.0:
        raise ValueError(f"factor must be in [0, 1] (got {factor!r})")
    state.matrix *= fac
    state.signed_matrix *= fac
    state.diag *= fac
    state.support *= fac
    return state



def ig_update_from_accepted(
    state: InteractionGraphState,
    *,
    displacements: np.ndarray,
    improvements: np.ndarray,
    decay: float,
    lr: float,
    sample_weights: np.ndarray | None = None,
) -> InteractionGraphState:
    """Update the interaction graph from successful moves.

    Passive decay is applied on every eligible call, even when no accepted moves
    are present. ``sample_weights`` allows callers to downweight or exclude
    specific accepted moves, e.g. DE-arm offspring or LS-derived updates.
    """
    if not isinstance(state, InteractionGraphState):
        raise TypeError("state must be InteractionGraphState")
    decay_f = float(decay)
    lr_f = float(lr)
    if not math.isfinite(decay_f) or decay_f < 0.0 or decay_f > 1.0:
        raise ValueError(f"decay must be in [0, 1] (got {decay!r})")
    if not math.isfinite(lr_f) or lr_f < 0.0:
        raise ValueError(f"lr must be finite and >= 0 (got {lr!r})")

    _apply_decay(state, decay_f)

    X = np.asarray(displacements, dtype=np.float64)
    imp = np.asarray(improvements, dtype=np.float64).reshape(-1)
    if X.size == 0 or imp.size == 0:
        return state
    if X.ndim != 2 or X.shape[1] != state.dim:
        raise ValueError("displacements must have shape (n, dim)")
    if X.shape[0] != imp.size:
        raise ValueError("displacements and improvements must have matching first dimension")

    if sample_weights is None:
        samp_w = np.ones((X.shape[0],), dtype=np.float64)
    else:
        samp_w = np.asarray(sample_weights, dtype=np.float64).reshape(-1)
        if samp_w.size != X.shape[0]:
            raise ValueError("sample_weights must match number of displacements")

    # H1: pre-allocated per-state aggregation buffers. Zero-fill instead of
    # ``np.zeros_like`` avoids 4 per-call allocations (4 × d×d matrix +
    # 1 × d vector). Bit-identical — buffers are fully zero-filled before any
    # reads, and the write/read pattern inside the loop is unchanged.
    if state._agg_buf is None or state._agg_buf.shape != state.matrix.shape:
        state._agg_buf = np.empty_like(state.matrix)
        state._agg_signed_buf = np.empty_like(state.signed_matrix)
        state._agg_diag_buf = np.empty_like(state.diag)
        state._agg_support_buf = np.empty_like(state.support)
    agg = state._agg_buf
    agg_signed = state._agg_signed_buf
    agg_diag = state._agg_diag_buf
    agg_support = state._agg_support_buf
    agg.fill(0.0)
    agg_signed.fill(0.0)
    agg_diag.fill(0.0)
    agg_support.fill(0.0)
    used = 0

    # D3: hoist ``np.abs(X)`` out of the loop — X is read-only inside the loop
    # body, so we compute the full absolute matrix once and slice rows as
    # views. Saves an ``np.abs`` per iteration without changing FP order.
    # H3: reuse per-state ``_abs_x_buf`` when NP/D fit the previous allocation.
    # Uses ``np.abs(X, out=...)`` to write into the buffer without allocation.
    _buf = state._abs_x_buf
    if _buf is None or _buf.shape[0] < X.shape[0] or _buf.shape[1] != X.shape[1]:
        state._abs_x_buf = np.empty(X.shape, dtype=np.float64)
        _buf = state._abs_x_buf
    abs_X = _buf[: X.shape[0]]
    np.abs(X, out=abs_X)

    # G3: numba fast-path for the scatter-add inner loop. The FP-sensitive
    # reductions (``denom = np.sum(a[idx])``) and the division that produces
    # ``vec_abs``/``vec_signed`` stay in NumPy so numpy's pairwise-summation
    # semantics are preserved exactly. The numba kernel only performs the
    # rank-1 outer-product scatter-adds whose target slots are disjoint
    # within one sample, so iteration order is irrelevant to the result.
    _scatter_fast = ig_scatter_add_fast
    for i in range(X.shape[0]):
        base_w = float(imp[i])
        sample_w = float(samp_w[i])
        if not math.isfinite(base_w) or base_w <= 0.0:
            continue
        if not math.isfinite(sample_w) or sample_w <= 0.0:
            continue
        w = base_w * sample_w
        a = abs_X[i]
        # D3: consolidate ``mask = a > TOL`` + ``np.any(mask)`` + ``np.flatnonzero(mask)``
        # into a single ``flatnonzero``. ``np.any`` is equivalent to ``idx.size > 0``
        # but costs one extra reduction over the boolean mask.
        idx = np.flatnonzero(a > _DEF_TOL)
        if idx.size == 0:
            continue
        denom = float(np.sum(a[idx]))
        if denom <= _DEF_TOL or not math.isfinite(denom):
            continue
        vec_abs = a[idx] / denom
        vec_signed = X[i, idx] / denom
        if _scatter_fast is not None:
            _scatter_fast(idx, w, sample_w, vec_abs, vec_signed,
                          agg, agg_signed, agg_diag, agg_support)
        else:
            agg_diag[idx] += w * vec_abs
            if idx.size >= 2:
                # B2: hoist np.ix_ into a single tuple reused for all three
                # writes, and reuse a cached ones-minus-identity template for
                # the support mask. These avoid duplicate indexing builds and
                # per-sample ones() allocation without changing FP order.
                sub_abs = np.outer(vec_abs, vec_abs)
                sub_signed = np.outer(vec_signed, vec_signed)
                np.fill_diagonal(sub_abs, 0.0)
                np.fill_diagonal(sub_signed, 0.0)
                sub_support = _ones_minus_identity(idx.size)
                _ij = np.ix_(idx, idx)
                agg[_ij] += w * sub_abs
                agg_signed[_ij] += w * sub_signed
                agg_support[_ij] += sample_w * sub_support
        used += 1

    if used > 0 and lr_f > 0.0:
        state.matrix += lr_f * agg
        state.signed_matrix += lr_f * agg_signed
        state.diag += lr_f * agg_diag
        state.support += agg_support
        # MEM2-1: symmetrise the three DxD state arrays in place (no rebind, no
        # fresh allocation) instead of ``state.X = _symmetrise_*(state.X)``.
        # The arrays are zero-init float64 + accumulated by ``+=`` so they stay
        # C-contiguous; the njit kernel reads both mirror cells before writing
        # either (read-before-write) so the result is bit-identical to the old
        # free-function path.  No reader outside this module touches these three
        # arrays, so dropping the rebind breaks nothing.
        if ig_symmetrise_inplace_fast is not None:
            ig_symmetrise_inplace_fast(state.matrix, True)
            ig_symmetrise_inplace_fast(state.signed_matrix, False)
            ig_symmetrise_inplace_fast(state.support, True)
        else:
            # numba-absent fallback: _symmetrise_* already builds a scratch via
            # 0.5*(A + A.T) (A.T aliases A, but the RHS is fully evaluated into a
            # new array before assignment), so this is bit-identical; assign back
            # into the same attribute.
            state.matrix = _symmetrise_nonneg(state.matrix)
            state.signed_matrix = _symmetrise_signed(state.signed_matrix)
            state.support = _symmetrise_nonneg(state.support)
        state.updates += used
    return state



def _normalised_graph(W: np.ndarray) -> np.ndarray:
    A = _symmetrise_nonneg(W)
    max_w = float(np.max(A)) if A.size else 0.0
    if max_w <= 0.0 or not math.isfinite(max_w):
        return np.zeros_like(A)
    # MEM2-3: divide in place into the buffer we solely own (the fresh array from
    # _symmetrise_nonneg) instead of allocating a new array.  Same elementwise
    # A[k]/max_w opcode -> bit-identical.  (NOT A *= 1.0/max_w, which would change
    # the bit pattern via reciprocal-then-multiply.)
    np.divide(A, max_w, out=A)
    return A



def _build_adjacency_from_topk(Wn: np.ndarray, *, edge_floor: float, max_group_size: int) -> list[list[int]]:
    d = int(Wn.shape[0])
    if d == 0:
        return []
    # ``Wn`` is produced by ``_normalised_graph`` -> ``_symmetrise_nonneg``,
    # which already zeros the diagonal. Skip the redundant ``Wn.copy()`` +
    # ``np.fill_diagonal`` (a d*d allocation per refresh) and read ``Wn``
    # directly. The function only reads ``_W``, never mutates it.
    _W = Wn
    # D1: boolean adjacency matrix in place of d Python sets. Avoids ~1M
    # ``set.add`` + ``int(j)`` conversions per refresh. ``np.flatnonzero``
    # returns indices in ascending order (identical to ``sorted(set)``),
    # and ``|= adj_bool.T`` symmetrizes in one vectorised op. Bit-identical
    # because: (a) which indices go into row i is identical (same per-row
    # keep computation), (b) final dedup/sort semantics preserved.
    # H2: reuse a module-level scratch buffer keyed by ``d`` — avoids
    # allocating a ``d*d`` bool matrix per refresh.
    adj_bool = _adj_bool_scratch(d)
    adj_bool.fill(False)
    _floor_f = float(edge_floor)
    _top_k_cap = max(0, int(max_group_size) - 1)
    if ig_build_adj_topk_fast is not None:
        ig_build_adj_topk_fast(_W, _floor_f, int(max_group_size), adj_bool)
    else:
        _row_maxes = _W.max(axis=1)
        _thresholds = np.maximum(_floor_f, _row_maxes * 0.5)
        for i in range(d):
            row_max = float(_row_maxes[i])
            if row_max <= 0.0:
                continue
            row = _W[i]
            keep = np.flatnonzero(row >= _thresholds[i])
            if keep.size == 0:
                keep = np.argsort(-row, kind="stable")[:_top_k_cap]
                keep = keep[row[keep] > 0.0]
            else:
                if keep.size > _top_k_cap:
                    order = np.argsort(-row[keep], kind="stable")
                    keep = keep[order[:_top_k_cap]]
            if keep.size > 0:
                adj_bool[i, keep] = True
    np.fill_diagonal(adj_bool, False)
    adj_bool |= adj_bool.T
    # D2: one ``np.nonzero`` + ``np.searchsorted`` replaces d per-row
    # ``flatnonzero`` calls. ``np.nonzero`` on a 2D bool matrix returns
    # (rows, cols) sorted lexicographically by (row, col), so ``cols`` is
    # already in ascending order within each row — identical to
    # ``sorted(set)``. Bit-identical.
    rows_nz, cols_nz = np.nonzero(adj_bool)
    offsets = np.searchsorted(rows_nz, np.arange(d + 1))
    return [cols_nz[offsets[i]:offsets[i + 1]].tolist() for i in range(d)]



def _connected_components(adj: list[list[int]]) -> list[list[int]]:
    n = len(adj)
    seen = [False] * n
    comps: list[list[int]] = []
    for start in range(n):
        if seen[start]:
            continue
        stack = [start]
        seen[start] = True
        comp: list[int] = []
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        comps.append(sorted(comp))
    return comps



def _split_component(Wn: np.ndarray, comp: Iterable[int], *, max_group_size: int) -> list[np.ndarray]:
    # C4: keep ``rem`` as a sorted numpy array throughout the loop instead
    # of rebuilding via Python list comprehension + ``np.asarray`` each
    # iteration. Since Wn indexing, lexsort, and the final ``sort`` are
    # unchanged, the selected seed / group / adjacency are bit-identical.
    _rem_arr = np.sort(np.fromiter((int(v) for v in comp), dtype=np.int64))
    groups: list[np.ndarray] = []
    if _rem_arr.size <= int(max_group_size):
        return [_rem_arr]
    _top_k_cap = max(0, int(max_group_size) - 1)
    # CR-0009: contiguous view for the zero-alloc row-sum kernel (no-op when Wn
    # is already C-contiguous). Layout only -- values are unchanged, so the
    # reduction stays bit-identical.
    _Wn_c = np.ascontiguousarray(Wn)
    while _rem_arr.size > 0:
        # B1: ``np.lexsort`` replaces Python ``sort(key=lambda x: (-x[0], x[1]))``
        # for the others-ordering. Seed selection uses np.argmax below.
        # stable mergesort; Python's sort is Timsort — also stable. With
        # ``-_row_sums`` as primary and ``_rem_arr`` as tiebreaker, both
        # sorts produce the same ordering given identical FP inputs, so the
        # selected seed and the top-k ``others`` stay bit-identical.
        # H5: ``Wn[a][:, a]`` avoids the ``np.ix_`` build cost — numpy fancy
        # indexing twice is cheaper than ``np.ix_`` plus advanced 2-D indexing
        # for the small ``|_rem_arr|`` sizes we see here. Bit-identical result.
        # CR-0009: zero-allocation naive row-sum, bit-identical to the fancy-
        # indexed NumPy reduction (which NumPy evaluates naively, left-to-right
        # in _rem_arr order). Verified 848/848 unit + end-to-end D50/D100/D1000.
        # The NumPy form is retained verbatim as the numba-absent fallback.
        if ig_component_rowsum_fast is not None:
            _row_sums = ig_component_rowsum_fast(_Wn_c, _rem_arr)
        else:
            _row_sums = Wn[_rem_arr][:, _rem_arr].sum(axis=1)
        seed = int(_rem_arr[int(np.argmax(_row_sums))])

        _others_arr = _rem_arr[_rem_arr != seed]
        if _others_arr.size > 0:
            _others_vals = Wn[seed, _others_arr]
            _other_order = np.lexsort((_others_arr, -_others_vals))
            _sorted_others = _others_arr[_other_order][:_top_k_cap]
            # H4: ``np.empty + assignment`` eliminates the ``np.concatenate``
            # allocation + the scalar-wrap ``np.asarray([seed])``. Since
            # ``_sorted_others`` is already int64 (from slicing ``_rem_arr``),
            # the ``.astype`` wrap is also a no-op.
            group_arr = np.empty(1 + _sorted_others.size, dtype=np.int64)
            group_arr[0] = seed
            group_arr[1:] = _sorted_others
        else:
            group_arr = np.asarray([seed], dtype=np.int64)
        group_arr = np.sort(group_arr)
        groups.append(group_arr)
        # CPX-4: both arrays are sorted unique and ``group_arr`` is a subset
        # of ``_rem_arr``. ``setdiff1d`` preserves the sorted order here and
        # is byte-identical to the previous ``~np.isin`` mask, but avoids the
        # heavier membership path inside the D>=100 SGSM refresh loop.
        _rem_arr = np.setdiff1d(_rem_arr, group_arr, assume_unique=True)
    return groups



def _block_stability(prev_blocks: tuple[np.ndarray, ...], block: np.ndarray) -> float:
    if not prev_blocks:
        return 0.0
    bset = set(int(v) for v in np.asarray(block, dtype=np.int64).tolist())
    if not bset:
        return 0.0
    best = 0.0
    for prev in prev_blocks:
        pset = set(int(v) for v in np.asarray(prev, dtype=np.int64).tolist())
        inter = len(bset & pset)
        if inter <= 0:
            continue
        union = len(bset | pset)
        if union <= 0:
            continue
        best = max(best, float(inter) / float(union))
    return best


def _block_stability_from_psets(prev_psets: tuple[frozenset[int], ...], bset: frozenset[int]) -> float:
    """Same as ``_block_stability`` but with pre-built frozensets.

    Callers in ``ig_extract_blocks`` build ``prev_psets`` once per refresh and
    ``bset`` once per block, avoiding rebuilding the ``prev`` sets on every
    inner call. Bit-identical to ``_block_stability`` because Jaccard =
    |A∩B|/|A∪B| is set-order-independent and the same max is selected.
    """
    if not prev_psets or not bset:
        return 0.0
    best = 0.0
    for pset in prev_psets:
        inter = len(bset & pset)
        if inter <= 0:
            continue
        union = len(bset | pset)
        if union <= 0:
            continue
        best = max(best, float(inter) / float(union))
    return best



def ig_extract_blocks(
    state: InteractionGraphState,
    *,
    edge_floor: float,
    min_block_size: int,
    max_block_size: int,
    gen: int | None = None,
) -> InteractionGraphState:
    if not isinstance(state, InteractionGraphState):
        raise TypeError("state must be InteractionGraphState")
    min_b = int(min_block_size)
    max_b = int(max_block_size)
    if min_b < 2:
        raise ValueError("min_block_size must be >= 2")
    if max_b < min_b:
        raise ValueError("max_block_size must be >= min_block_size")

    prev_blocks = tuple(np.asarray(b, dtype=np.int64) for b in state.blocks)
    Wn = _normalised_graph(state.matrix)
    if not np.any(Wn > 0.0):
        state.blocks = tuple()
        state.block_confidence = np.zeros((0,), dtype=np.float64)
        state.overall_confidence = 0.0
        state.nontrivial_dims = 0
        state.refresh_count += 1
        if gen is not None:
            state.last_refresh_gen = int(gen)
        hist = state.confidence_history
        hist.append(0.0)
        if len(hist) > 256:
            del hist[: len(hist) - 256]
        return state

    adj = _build_adjacency_from_topk(Wn, edge_floor=float(edge_floor), max_group_size=max_b)
    comps = _connected_components(adj)
    blocks: list[np.ndarray] = []
    for comp in comps:
        if len(comp) < min_b:
            continue
        if len(comp) <= max_b:
            blocks.append(np.asarray(comp, dtype=np.int64))
        else:
            blocks.extend(_split_component(Wn, comp, max_group_size=max_b))

    # A1: Precompute ``prev_psets`` once per refresh so ``_block_stability``
    # inner loop does not rebuild Python sets on every call. 10 prev_blocks x
    # 10 current blocks -> 100 stability calls per refresh, so hoisting saves
    # ~90 redundant set constructions per extract.
    # F1: ``pb`` is already ``np.ndarray`` int64 (built above), so both the
    # ``np.asarray`` wrap and the ``int(v) for v`` generator are redundant —
    # ``pb.tolist()`` already returns Python ints. Bit-identical frozenset.
    prev_psets = tuple(frozenset(pb.tolist()) for pb in prev_blocks)

    pairs: list[tuple[np.ndarray, float]] = []
    nontrivial_dims = 0
    for block in blocks:
        # E1: blocks are constructed as either ``np.asarray(comp, dtype=int64)``
        # with ``comp`` from ``_connected_components`` (unique by DFS design), or
        # from ``_split_component`` (unique-by-construction). So ``np.unique``
        # is redundant — replace with ``np.asarray`` (no-op when dtype matches).
        b = np.asarray(block, dtype=np.int64)
        if b.size < min_b:
            continue
        if b.size > max_b:
            b = b[:max_b]
        # Hoist per-block shared computation: ``np.ix_`` and ``np.triu_indices``
        # were each evaluated three times (once for rel/raw/support). They
        # depend only on ``b``/``b.size``, so compute once per block and reuse.
        # A2: ``triu_indices`` is cached module-level by ``k`` — identical
        # arrays returned on repeat calls, so indexing is bit-identical.
        ix = np.ix_(b, b)
        triu_idx = _triu_k1_cached(int(b.size)) if b.size > 1 else None

        sub_rel = Wn[ix]
        tri_rel = sub_rel[triu_idx] if triu_idx is not None else np.zeros((0,), dtype=np.float64)
        rel_density = float(np.mean(tri_rel)) if tri_rel.size else 0.0

        sub_raw = state.matrix[ix]
        tri_raw = sub_raw[triu_idx] if triu_idx is not None else np.zeros((0,), dtype=np.float64)
        raw_signal = float(np.mean(tri_raw)) if tri_raw.size else 0.0
        abs_signal = 1.0 - math.exp(-max(0.0, raw_signal))

        sub_sup = state.support[ix]
        tri_sup = sub_sup[triu_idx] if triu_idx is not None else np.zeros((0,), dtype=np.float64)
        support_signal = float(np.mean(tri_sup)) if tri_sup.size else 0.0
        support_weight = 1.0 - math.exp(-max(0.0, support_signal))

        # F1: ``b`` is np.int64 array → ``b.tolist()`` returns Python ints,
        # so ``int(v)`` is redundant. Drop the genexp wrap.
        bset = frozenset(b.tolist())
        stability = _block_stability_from_psets(prev_psets, bset)
        conf = rel_density * math.sqrt(max(0.0, abs_signal * support_weight)) * (0.5 + 0.5 * stability)
        pairs.append((b, float(conf)))
        nontrivial_dims += int(b.size)

    pairs.sort(key=lambda bc: (int(bc[0][0]), int(bc[0].size)))
    if pairs:
        blocks_sorted = tuple(b for b, _ in pairs)
        conf_arr = np.asarray([c for _, c in pairs], dtype=np.float64)
        weights = np.asarray([float(b.size) for b, _ in pairs], dtype=np.float64)
        coverage = float(nontrivial_dims) / float(max(1, state.dim))
        overall = float(np.average(conf_arr, weights=weights)) * math.sqrt(max(0.0, coverage))
    else:
        blocks_sorted = tuple()
        conf_arr = np.zeros((0,), dtype=np.float64)
        overall = 0.0
        nontrivial_dims = 0

    state.blocks = blocks_sorted
    state.block_confidence = conf_arr
    state.overall_confidence = overall
    state.nontrivial_dims = int(nontrivial_dims)
    state.refresh_count += 1
    if gen is not None:
        state.last_refresh_gen = int(gen)
    # Append to rolling confidence history (adaptive-gate support). Cap at
    # 256 entries — enough to cover any reasonable adaptive window while
    # keeping memory trivial. The static-gate path does not read this buffer.
    hist = state.confidence_history
    hist.append(float(overall))
    if len(hist) > 256:
        del hist[: len(hist) - 256]
    return state



def ig_ready(
    state: InteractionGraphState,
    *,
    confidence_min: float,
    min_updates: int,
    min_refreshes: int,
    min_nontrivial_dims: int,
) -> bool:
    if not isinstance(state, InteractionGraphState):
        raise TypeError("state must be InteractionGraphState")
    return bool(
        state.blocks
        and int(state.updates) >= int(min_updates)
        and int(state.refresh_count) >= int(min_refreshes)
        and int(state.nontrivial_dims) >= int(min_nontrivial_dims)
        and float(state.overall_confidence) >= float(confidence_min)
    )


def ig_adaptive_threshold(
    state: InteractionGraphState,
    *,
    static_threshold: float,
    percentile: float,
    floor: float,
    min_samples: int,
    window: int,
    absolute_min: float = 0.0,
) -> float:
    """Return the effective confidence threshold for a gate site.

    When the rolling confidence history on ``state`` has fewer than
    ``min_samples`` entries, the function returns ``static_threshold`` — so the
    adaptive path behaves exactly like the shipped static gate during warm-up.

    Once enough refreshes have accumulated, the returned value is the
    ``percentile``-quantile of the last ``window`` entries, clipped below by
    ``floor``. This engages linkage/LS whenever the current overall confidence
    is at or above the recent typical level (or better than ``percentile`` of
    recent refreshes), without letting the gate open on pathologically low
    noise landscapes (the hard ``floor``).

    **Absolute-minimum safeguard (C1, added 2026-04-19).** When
    ``absolute_min > 0``, the rolling median of the windowed history is
    compared against ``absolute_min``. If the rolling median is below the
    safeguard threshold, the function reverts to ``static_threshold`` rather
    than returning the quantile-based value. This prevents the adaptive rule
    from opening the gate when the *entire* recent confidence history is
    low-quality — e.g. on rugged hybrid/composition landscapes at D=100 where
    quantile-over-noise can still clear ``floor`` and spuriously activate
    SGSM on misleading learned structure. Default ``0.0`` preserves the
    original v1 adaptive behaviour for backwards compatibility.

    The function is a pure read on ``state.confidence_history``; it does not
    mutate anything. The caller passes the returned scalar into ``ig_ready``
    as ``confidence_min``.
    """
    if not isinstance(state, InteractionGraphState):
        raise TypeError("state must be InteractionGraphState")
    hist = state.confidence_history
    n = len(hist)
    # A3: Short-circuit via per-state cache keyed on (refresh_count, params).
    # ``confidence_history`` is appended to exactly once per ``ig_extract_blocks``
    # call, and ``refresh_count`` increments in lockstep. Between refreshes the
    # function is a pure function of ``(static_threshold, percentile, floor,
    # min_samples, window, absolute_min)`` — all scalars hashed in the key.
    # Bit-identical because the cache stores the exact float returned last.
    cache_key = (
        int(state.refresh_count),
        n,
        float(static_threshold),
        float(percentile),
        float(floor),
        int(min_samples),
        int(window),
        float(absolute_min),
    )
    if state._adaptive_thr_cache_key == cache_key:
        return state._adaptive_thr_cache_val
    ms = int(min_samples)
    if n < max(1, ms):
        out = float(static_threshold)
        state._adaptive_thr_cache_key = cache_key
        state._adaptive_thr_cache_val = out
        return out
    w = int(window)
    if w <= 0 or w >= n:
        view = hist
    else:
        view = hist[-w:]
    abs_min = float(absolute_min)
    if abs_min > 0.0:
        # Compute rolling median over the view. If the history has been
        # persistently low-quality, trust the learned structure less and
        # revert to the conservative static threshold.
        view_arr = np.asarray(view, dtype=np.float64)
        rolling_med = float(np.median(view_arr)) if view_arr.size else 0.0
        if rolling_med < abs_min:
            out = float(static_threshold)
            state._adaptive_thr_cache_key = cache_key
            state._adaptive_thr_cache_val = out
            return out
    q = float(percentile)
    if q <= 0.0:
        thr = min(view)
    elif q >= 1.0:
        thr = max(view)
    else:
        thr = float(np.quantile(np.asarray(view, dtype=np.float64), q))
    out = float(max(float(floor), thr))
    state._adaptive_thr_cache_key = cache_key
    state._adaptive_thr_cache_val = out
    return out



def ig_expand_blocks_with_singletons(state: InteractionGraphState, *, dim: int | None = None) -> list[np.ndarray]:
    if not isinstance(state, InteractionGraphState):
        raise TypeError("state must be InteractionGraphState")
    d = int(state.dim if dim is None else dim)
    covered = np.zeros((d,), dtype=bool)
    groups: list[np.ndarray] = []
    for block in state.blocks:
        b = np.asarray(np.unique(block), dtype=np.int64)
        if b.size == 0:
            continue
        groups.append(b)
        covered[b] = True
    missing = np.flatnonzero(~covered)
    for m in missing.tolist():
        groups.append(np.asarray([int(m)], dtype=np.int64))
    groups.sort(key=lambda arr: (int(arr[0]), int(arr.size)))
    return groups



def ig_select_local_search_dims(
    state: InteractionGraphState,
    *,
    recent_displacements: np.ndarray | None,
    top_blocks: int,
    dim_cap: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return selected dimension indices, selected block ids, and block scores."""
    if not isinstance(state, InteractionGraphState):
        raise TypeError("state must be InteractionGraphState")
    if not state.blocks:
        return np.zeros((0,), dtype=np.int64), np.zeros((0,), dtype=np.int64), np.zeros((0,), dtype=np.float64)
    k_blocks = max(1, int(top_blocks))
    cap = max(1, int(dim_cap))
    recent = None
    if recent_displacements is not None:
        recent = np.asarray(recent_displacements, dtype=np.float64)
        if recent.ndim == 1:
            recent = recent.reshape(1, -1)
        if recent.ndim != 2 or recent.shape[1] != state.dim:
            raise ValueError("recent_displacements must have shape (n, dim)")
        recent = np.abs(recent)
    scores = []
    for bi, block in enumerate(state.blocks):
        b = np.asarray(block, dtype=np.int64)
        base = float(state.block_confidence[bi]) if bi < state.block_confidence.size else 0.0
        diag_term = float(np.mean(state.diag[b])) if b.size > 0 else 0.0
        act = 0.0
        if recent is not None and recent.size > 0:
            act = float(np.mean(np.sum(recent[:, b], axis=1)) / max(1, b.size))
        score = (base + 1e-12) * (diag_term + act + 1e-12)
        scores.append((score, int(bi), b))
    scores.sort(key=lambda t: (-t[0], int(t[1]), int(t[2][0]) if t[2].size else -1))

    chosen_mask = np.zeros((state.dim,), dtype=bool)
    chosen_blocks: list[int] = []
    chosen_scores: list[float] = []
    chosen_dims: list[int] = []
    for score, bi, block in scores:
        if len(chosen_blocks) >= k_blocks:
            break
        new_mask = ~chosen_mask[block]
        if not np.any(new_mask):
            continue
        if len(chosen_dims) >= cap:
            break
        room = cap - len(chosen_dims)
        new_dims = block[new_mask][:room]
        if new_dims.size == 0:
            continue
        chosen_dims.extend(int(v) for v in new_dims.tolist())
        chosen_mask[new_dims] = True
        chosen_blocks.append(int(bi))
        chosen_scores.append(float(score))
        if len(chosen_dims) >= cap:
            break
    dims = np.asarray(sorted(chosen_dims), dtype=np.int64)
    return dims, np.asarray(chosen_blocks, dtype=np.int64), np.asarray(chosen_scores, dtype=np.float64)



def ig_build_local_search_basis(
    state: InteractionGraphState,
    *,
    dims: np.ndarray,
    recent_displacements: np.ndarray | None,
    k: int,
) -> tuple[np.ndarray, str]:
    if not isinstance(state, InteractionGraphState):
        raise TypeError("state must be InteractionGraphState")
    sel = np.asarray(np.unique(np.asarray(dims, dtype=np.int64)), dtype=np.int64)
    if sel.size == 0 or int(k) <= 0:
        return np.zeros((0, state.dim), dtype=np.float64), "interaction_blocks_empty"
    k_use = min(int(k), int(sel.size))

    recent = None
    if recent_displacements is not None:
        recent = np.asarray(recent_displacements, dtype=np.float64)
        if recent.ndim == 1:
            recent = recent.reshape(1, -1)
        if recent.ndim != 2 or recent.shape[1] != state.dim:
            raise ValueError("recent_displacements must have shape (n, dim)")

    if recent is not None and recent.shape[0] >= 2 and sel.size >= 2:
        sub = recent[:, sel]
        try:
            _u, s, vt = np.linalg.svd(sub, full_matrices=False)
        except np.linalg.LinAlgError:
            vt = None
            s = None
        if vt is not None and s is not None and vt.size > 0:
            rank = min(k_use, int(vt.shape[0]))
            if rank > 0 and np.any(np.abs(vt[:rank]) > _DEF_TOL):
                basis = np.zeros((rank, state.dim), dtype=np.float64)
                basis[:, sel] = vt[:rank, :]
                return basis, "interaction_blocks_pca"

    if sel.size >= 2:
        sub_signed = _symmetrise_signed(state.signed_matrix[np.ix_(sel, sel)])
        if np.any(np.abs(sub_signed) > _DEF_TOL):
            try:
                evals, evecs = np.linalg.eigh(sub_signed)
            except np.linalg.LinAlgError:
                evals = None
                evecs = None
            if evals is not None and evecs is not None:
                order = np.argsort(-np.abs(evals), kind="stable")
                keep = order[np.abs(evals[order]) > _DEF_TOL][:k_use]
                if keep.size > 0:
                    basis = np.zeros((int(keep.size), state.dim), dtype=np.float64)
                    basis[:, sel] = evecs[:, keep].T
                    return basis, "interaction_blocks_signed"

    basis = np.zeros((k_use, state.dim), dtype=np.float64)
    basis[np.arange(k_use), sel[:k_use]] = 1.0
    return basis, "interaction_blocks_axes"



def ig_stats(state: InteractionGraphState) -> InteractionGraphStats:
    Wn = _normalised_graph(state.matrix)
    d = int(state.dim)
    tri = Wn[np.triu_indices(d, k=1)] if d > 1 else np.zeros((0,), dtype=np.float64)
    nz = tri[tri > 0.0]
    density = float(nz.size) / float(max(1, tri.size))
    max_w = float(np.max(nz)) if nz.size else 0.0
    mean_w = float(np.mean(nz)) if nz.size else 0.0
    frac = float(int(state.nontrivial_dims)) / float(max(1, d))
    orphan = max(0.0, 1.0 - frac)
    return InteractionGraphStats(
        density=density,
        max_weight=max_w,
        mean_weight=mean_w,
        nonzero_edges=int(nz.size),
        block_count=int(len(state.blocks)),
        mean_block_confidence=float(np.mean(state.block_confidence)) if state.block_confidence.size else 0.0,
        nontrivial_dim_fraction=frac,
        orphan_dim_fraction=orphan,
        refresh_count=int(state.refresh_count),
    )


__all__ = [
    "InteractionGraphState",
    "InteractionGraphStats",
    "ig_apply_restart_decay",
    "ig_build_local_search_basis",
    "ig_expand_blocks_with_singletons",
    "ig_extract_blocks",
    "ig_init",
    "ig_ready",
    "ig_select_local_search_dims",
    "ig_stats",
    "ig_update_from_accepted",
]
