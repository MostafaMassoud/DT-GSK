"""CEC2017 transform layer.

Cross-reference: ``cec17_func.cpp`` data loading (lines 130-258).
Data files: ``input_data/M_{func_num}_D{nx}.txt`` (transformation matrices),
``input_data/shift_data_{func_num}.txt`` (shift vectors),
``input_data/shuffle_data_{func_num}_D{nx}.txt`` (permutations for hybrids).

Loads data.pkl at module level. Provides:
  - shift_rotate(x, shift, rotation)  for batch (M, N)
  - shuffle_and_partition(x, shuffle, partitions)  for hybrids

Data dicts:
  rotations[dim][func_idx]      → (N, N)
  rotations_cf[dim][comp_idx]   → (num_comp, N, N)
  shifts[func_idx]              → (100,) or (D,) for some
  shifts_cf[comp_idx]           → (num_comp, 100)
  shuffles[dim][func_idx]       → (N,) 0-indexed
  shuffles_cf[dim][comp_idx]    → (num_comp, N) 0-indexed

Note on "rotation" matrices:
  CEC2017 uses general transformation matrices (called ``M`` in C++),
  NOT necessarily orthogonal rotation matrices. The F1-F10 simple function
  matrices are typically non-orthogonal (``max |M@M.T - I| ~ 2-3``), while
  some hybrid matrices (e.g., F12, F13, F14, F17, F20) are truly orthogonal.
  This is a property of the original reference data files, not a data error.

SECURITY: data.pkl is loaded via pickle.loads() after SHA-256 integrity
verification. The hash check prevents use of tampered files, but pickle
deserialization can still execute arbitrary code embedded in a valid-hash
file. Only use data.pkl files from trusted sources (the original benchmark
distribution). Never replace with files from untrusted origins.

NOTE: This suite uses a custom serialization format for numpy arrays:
  ('__np_array__', dtype_str, shape_tuple, raw_bytes)
This avoids pickle's default numpy serialization which can be version-
sensitive. The _reconstruct() function converts these tuples back to
np.ndarray objects on load.
"""

from __future__ import annotations

import hashlib
import os
import pickle
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Sequence

_DATA_PATH = os.path.join(os.path.dirname(__file__), "data.pkl")
_EXPECTED_SHA256 = 'fe544853b079b1e7238e98c40c7c27748a94b62350d13f8a14808a7c4b8a4e15'


def _reconstruct(obj: object) -> object:
    """Recursively convert ('__np_array__', dtype, shape, bytes) → np.ndarray."""
    if isinstance(obj, tuple) and len(obj) == 4 and obj[0] == "__np_array__":
        return np.frombuffer(obj[3], dtype=obj[1]).reshape(obj[2]).copy()
    if isinstance(obj, dict):
        return {k: _reconstruct(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(_reconstruct(v) for v in obj)
    return obj


with open(_DATA_PATH, "rb") as _f:
    _pkl_bytes = _f.read()
    if hashlib.sha256(_pkl_bytes).hexdigest() != _EXPECTED_SHA256:
        raise RuntimeError(
            f'CEC2017 data.pkl integrity check failed. '
            f'Expected SHA-256 {_EXPECTED_SHA256[:16]}..., file may be corrupted or tampered.'
        )
    _data = _reconstruct(pickle.loads(_pkl_bytes))
    del _pkl_bytes

rotations    = _data["rotations"]
rotations_cf = _data["rotations_cf"]
shifts       = _data["shifts"]
shifts_cf    = _data["shifts_cf"]
shuffles     = _data["shuffles"]
shuffles_cf  = _data["shuffles_cf"]


# Audit REPRO-CRIT-1: freeze every loaded array so accidental in-place
# mutation by a downstream caller (e.g. an optimizer that briefly aliases
# a shift vector for diagnostic plotting) cannot poison subsequent NFE
# evaluations across the rest of the run.  ``ndarray.flags.writeable =
# False`` is a zero-cost guard that the NumPy and Numba kernels respect
# (assignment raises ``ValueError`` instead of silently corrupting state).
def _freeze_array(a: np.ndarray) -> None:
    a.flags.writeable = False


def _freeze_nested(obj: object) -> None:
    """Recursively mark every ndarray inside *obj* as read-only."""
    if isinstance(obj, np.ndarray):
        _freeze_array(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _freeze_nested(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _freeze_nested(v)


_freeze_nested(rotations)
_freeze_nested(rotations_cf)
_freeze_nested(shifts)
_freeze_nested(shifts_cf)
_freeze_nested(shuffles)
_freeze_nested(shuffles_cf)


def _iter_ndarrays(obj: object):
    if isinstance(obj, np.ndarray):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _iter_ndarrays(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _iter_ndarrays(v)


_DEFAULT_SHUFFLE_ROOT_IDS = frozenset(
    id(arr) for src in (shuffles, shuffles_cf) for arr in _iter_ndarrays(src)
)

# XS-01: Pre-transpose all rotation matrices at load time so the hot-path
# ``y @ rotation_T`` reads a C-contiguous right operand (no transpose view).
# ``np.T`` on a frozen array is a zero-copy view with reversed strides;
# ``np.ascontiguousarray`` materialises the C-order copy once at load time.
def _build_transposed_dict(src: dict) -> dict:
    """Return a nested dict mirroring *src* with every 2-D/3-D ndarray
    replaced by its C-contiguous transpose (last two axes swapped)."""
    out: dict = {}
    for key, val in src.items():
        if isinstance(val, dict):
            out[key] = _build_transposed_dict(val)
        elif isinstance(val, np.ndarray):
            if val.ndim == 2:
                t = np.ascontiguousarray(val.T)
            elif val.ndim == 3:
                t = np.ascontiguousarray(val.transpose(0, 2, 1))
            else:
                t = val  # scalars / 1-D — unlikely, keep as-is
            t.flags.writeable = False
            out[key] = t
        else:
            out[key] = val
    return out

rotations_T    = _build_transposed_dict(rotations)
rotations_cf_T = _build_transposed_dict(rotations_cf)


try:
    from ._numba import shift_rotate_fast as _sr_fast
    from ._numba import shift_rotate_strict_fast as _sr_strict_fast
except ImportError:
    _sr_fast = None
    _sr_strict_fast = None

# Serial (parallel=False) twins + the thread-local routing flag for opted-in
# optimizers (see _numba_serial.py / _kernel_mode.py).  Outside a
# serial_kernel_scope() both call sites below take the batch branch unchanged.
try:
    from . import _numba_serial as _ns
    from ._kernel_mode import serial_kernels_active as _serial_kernels_active
except ImportError:
    _ns = None

    def _serial_kernels_active() -> bool:
        return False


def _shift_rotate_strict_numpy(
    x: np.ndarray,
    shift: np.ndarray,
    rotation: np.ndarray | None,
    rotation_T: np.ndarray | None,
) -> np.ndarray:
    """Strict fixed-order shift/rotate fallback used by trace-lock mode."""
    arr = np.ascontiguousarray(x, dtype=np.float64)
    sh = np.ascontiguousarray(shift, dtype=np.float64)
    N = arr.shape[1]
    if rotation_T is not None:
        rt = np.ascontiguousarray(rotation_T, dtype=np.float64)
    elif rotation is not None:
        rt = np.ascontiguousarray(rotation.T, dtype=np.float64)
    else:
        return arr - sh[:N]

    out = np.empty((arr.shape[0], N), dtype=np.float64)
    for i in range(arr.shape[0]):
        for k in range(N):
            s = 0.0
            for j in range(N):
                s = s + float(arr[i, j] - sh[j]) * float(rt[j, k])
            out[i, k] = s
    return out


def shift_rotate(
    x: np.ndarray,
    shift: np.ndarray,
    rotation: np.ndarray | None,
    *,
    rotation_T: np.ndarray | None = None,
    strict: bool = False,
) -> np.ndarray:
    """Shift and rotate: ``z = (x - shift[:N]) @ rotation.T``.

    XS-01: when *rotation_T* is provided (a C-contiguous pre-transposed
    matrix), it is used directly, avoiding the on-the-fly ``.T`` view
    which may force the BLAS backend into a slower strided code path.

    Audit MED-CORRECT-01: previously the NumPy fallback path passed
    ``rotation`` straight to ``y @ rotation.T`` without normalising
    dtype/contiguity, so a callable handed a ``float32`` rotation matrix
    would silently fall onto a strided/mixed-dtype BLAS path that does
    not produce bit-identical results to the Numba path.  We now coerce
    the rotation to C-contiguous float64 before the matmul to keep both
    paths on the same BLAS code path.
    """
    if strict:
        if _sr_strict_fast is not None:
            x_fast = (
                x if x.dtype == np.float64 and x.flags.c_contiguous
                else np.ascontiguousarray(x, dtype=np.float64)
            )
            shift_fast = (
                shift if shift.dtype == np.float64 and shift.flags.c_contiguous
                else np.ascontiguousarray(shift, dtype=np.float64)
            )
            sr_strict = (
                _ns.shift_rotate_strict_fast if _serial_kernels_active() else _sr_strict_fast
            )
            return sr_strict(x_fast, shift_fast, rotation, rotation_T)
        return _shift_rotate_strict_numpy(x, shift, rotation, rotation_T)
    if _sr_fast is not None:
        x_fast = (
            x if x.dtype == np.float64 and x.flags.c_contiguous
            else np.ascontiguousarray(x, dtype=np.float64)
        )
        shift_fast = (
            shift if shift.dtype == np.float64 and shift.flags.c_contiguous
            else np.ascontiguousarray(shift, dtype=np.float64)
        )
        sr = _ns.shift_rotate_fast if _serial_kernels_active() else _sr_fast
        return sr(x_fast, shift_fast, rotation, rotation_T)
    N = x.shape[1]
    shift = np.asarray(shift, dtype=np.float64)
    y = x - shift[:N]
    if rotation is not None or rotation_T is not None:
        if rotation_T is not None:
            z = y @ rotation_T
        else:
            rotation = np.ascontiguousarray(rotation, dtype=np.float64)
            z = y @ rotation.T
    else:
        z = y
    return z


# L4: partition-index cache for ``shuffle_and_partition``.
# Each F11..F20 hybrid passes the same Python-list literal (e.g.
# ``[0.2, 0.4, 0.4]``) on every NFE, so the (np.ceil + np.cumsum) bookkeeping
# repeats with identical inputs millions of times per run.  Cache by
# ``(N, tuple(proportions))`` so each (dim, hybrid) pair pays the conversion
# cost exactly once per process.
#
# Cache design contract
# ---------------------
# * **Bounded size.** Keys are ``(N, proportions)``.  ``N`` is drawn from the
#   small set of supported benchmark dims (10, 30, 50, 100) and the hybrid
#   wrappers (F11-F20) only ever pass 10 distinct proportion tuples, so the
#   cache is bounded at ~40 entries for the lifetime of any process.  No
#   eviction logic is needed.
# * **Thread safety.** Each value is computed deterministically from its key,
#   so a benign last-write-wins race under multi-threaded access produces the
#   same array.  We rely on the GIL for the dict ``get`` / ``__setitem__``
#   atomicity rather than holding a lock on the hot path.
# * **Lifetime / invalidation.** Process-global, never invalidated.  Inputs
#   are pure functions of ``N`` and ``proportions``, so a stale entry is
#   impossible.  ``_partition_cache.clear()`` is safe to call from tests.
_partition_cache: dict[tuple[int, tuple[float, ...]], np.ndarray] = {}

# CEC-2: second-level cache for the *split index-groups* produced by
# ``np.split(shuffle, split_idx)``.  ``_partition_cache`` already removes the
# ``np.ceil``/``np.cumsum`` bookkeeping, but ``np.split`` itself still re-slices
# the frozen permutation into ``cf_num`` sub-arrays on *every* NFE.  Because the
# default hybrid shuffles and comp-hybrid shuffle roots are frozen,
# process-lifetime module constants (``writeable=False``, pinned by
# ``tests/test_cec_data_frozen.py``).  Their ``np.split`` output is a pure
# function of ``(root id, row data pointer, N, proportions)`` and can be
# memoised once per (dim, hybrid/component row).
#
# Cache design contract
# ---------------------
# * **Key.** ``(id(root), data_ptr, N, tuple(proportions))`` for loaded
#   benchmark shuffles only.  This supports both 1-D default hybrid shuffles
#   and row views from 2-D comp-hybrid shuffles without relying on temporary
#   view object ids.
# * **Bounded size.** Same ~40-entry bound as ``_partition_cache`` for the
#   default path (small dim set × 10 hybrid proportion tuples × the frozen
#   shuffle ids).  No eviction needed.
# * **Cached values are read-only index arrays.**  They are used only as
#   fancy-index operands in ``x[:, sg]`` and are never mutated, so a shared
#   cached entry cannot be corrupted by a caller.
# * **Override arrays bypass this cache.**  Ad-hoc caller-provided shuffles are
#   rare and may be short-lived.  They still use the cached split-index array,
#   but their actual split groups are recomputed to avoid stale object-id reuse.
_shuffle_groups_cache: dict[
    tuple[int, int, int, tuple[float, ...]],
    tuple[list[np.ndarray], tuple[tuple[int, int], ...]],
] = {}


# L4b: third-level cache, keyed by the hybrid's OWN identity ``(func_idx, N)``
# rather than by anything derived from the array on each call.
#
# ``_shuffle_groups_cache`` still had to *build* its key on every NFE:
# ``_array_root`` walks ``.base``, ``__array_interface__`` materialises a fresh
# dict just to read the data pointer, and ``tuple(proportions)`` re-hashes the
# proportion sequence -- ~1.0 us per evaluation, spent purely to look up a
# value that is a pure function of (hybrid, dim) on the default path.
#
# Cache design contract
# ---------------------
# * **Key.** ``(func_idx, N)``.  Populated ONLY from the default path (no
#   caller-supplied ``shuffle=`` override), where ``ss`` is by definition
#   ``shuffles[N][func_idx]``.
# * **Validated on read by identity.** The stored entry carries the exact
#   ``proportions`` and ``shuffle`` objects it was built from and is accepted
#   only if both are the *same objects* again (two ``is`` tests, ~0.02 us).
#   Monkeypatched or reloaded ``shuffles`` data therefore misses and recomputes
#   instead of serving a stale split.
# * **Bounded size.** 10 hybrids x 5 supported dims = at most 50 entries.
# * **Values are read-only index arrays**, used only as fancy-index operands.
_hybrid_groups_cache: dict[
    tuple[int, int], tuple[tuple[float, ...], np.ndarray, list[np.ndarray], tuple[tuple[int, int], ...]]
] = {}


def reset_shuffle_groups_cache() -> None:
    """Clear the CEC-2 split-group cache (and the partition-index cache).

    Safe to call at any time.  Intended for test teardown so that a recycled
    ``id(shuffle)`` from a GC'd override array can never serve a stale split.
    """
    _shuffle_groups_cache.clear()
    _partition_cache.clear()
    _hybrid_groups_cache.clear()


def _get_split_idx(N: int, proportions: list[float]) -> np.ndarray:
    """Return cumulative split indices for ``np.split``, cached by (N, props)."""
    key = (N, tuple(proportions))
    cached = _partition_cache.get(key)
    if cached is None:
        props = np.asarray(proportions, dtype=np.float64)
        sizes = np.ceil(props[:-1] * N).astype(np.intp)
        last = N - int(sizes.sum())
        if last < 0:
            raise ValueError(
                f"Partition proportions {proportions} sum too large for N={N}: "
                f"ceil sizes {sizes.tolist()} total {int(sizes.sum())} > {N}"
            )
        cached = np.cumsum(sizes)  # (cf_num-1,)
        _partition_cache[key] = cached
    return cached


def _array_root(a: np.ndarray) -> np.ndarray:
    root = a
    while isinstance(root.base, np.ndarray):
        root = root.base
    return root


def _shuffle_groups_cache_key(
    shuffle: np.ndarray,
    N: int,
    proportions: list[float],
) -> tuple[int, int, int, tuple[float, ...]] | None:
    root = _array_root(shuffle)
    if id(root) not in _DEFAULT_SHUFFLE_ROOT_IDS:
        return None
    data_ptr = int(shuffle.__array_interface__["data"][0])
    return (id(root), data_ptr, N, tuple(proportions))


def shuffle_and_partition(
                          x: np.ndarray,
                          shuffle: np.ndarray,
                          proportions: list[float],
) -> list[np.ndarray]:
    """Shuffle columns then partition into sub-vectors.

    Uses a cached cumulative-split-index array (see ``_partition_cache``) so
    the per-NFE work is reduced to per-group fancy-index extractions.

    H1 optimisation: instead of building the full ``(M, N)`` shuffled
    intermediate via ``x[:, shuffle]`` and then splitting it, we split the
    shuffle permutation itself and extract each group directly.  Each
    fancy-index ``x[:, sg]`` returns a contiguous ``(M, n_i)`` array, so
    the downstream basic-function ``np.ascontiguousarray`` calls become
    no-ops.  Total allocation is the same ``Σ(M, n_i) = (M, N)`` but the
    transient ``(M, N)`` copy is eliminated.

    Parameters
    ----------
    x : (M, N)
        Population matrix.
    shuffle : (N,) int array, 0-indexed
        Column permutation.
    proportions : list of floats summing to ~1.0
        Fraction of columns assigned to each sub-vector.

    Returns
    -------
    parts : list of (M, n_i) arrays
        One contiguous array per proportion entry.
    """
    N = x.shape[1]
    shuffle_arr = np.asarray(shuffle)
    shuffle_groups, bounds = _split_shuffle(shuffle_arr, N, proportions)
    return _extract_groups(x, shuffle_arr, shuffle_groups, bounds)


def _split_shuffle(
    shuffle_arr: np.ndarray,
    N: int,
    proportions: Sequence[float],
) -> tuple[list[np.ndarray], tuple[tuple[int, int], ...]]:
    """Return the per-group index split of ``shuffle_arr`` plus its slice bounds.

    CEC-2: memoise the per-group split of the (frozen) shuffle permutation.
    On the harness path ``shuffle`` is a process-lifetime constant, so
    ``np.split`` runs at most once per (dim, hybrid); on a cache hit we go
    straight to the per-group extractions.
    """
    cache_key = _shuffle_groups_cache_key(shuffle_arr, N, proportions)
    cached = _shuffle_groups_cache.get(cache_key) if cache_key is not None else None
    if cached is not None:
        return cached
    # Cumulative split indices for np.split: [n0, n0+n1, ...] — cached.
    split_idx = _get_split_idx(N, proportions)
    # Split the shuffle permutation once; store the read-only index groups.
    shuffle_groups = np.split(shuffle_arr, split_idx)
    bounds = _group_bounds(split_idx, N)
    if cache_key is not None:
        _shuffle_groups_cache[cache_key] = (shuffle_groups, bounds)
    return shuffle_groups, bounds


def _group_bounds(split_idx: np.ndarray, N: int) -> tuple[tuple[int, int], ...]:
    """Return the ``(start, stop)`` column bounds matching ``np.split`` groups."""
    edges = [0, *(int(v) for v in split_idx), N]
    return tuple((edges[i], edges[i + 1]) for i in range(len(edges) - 1))


def _extract_groups(
    x: np.ndarray,
    shuffle_arr: np.ndarray,
    shuffle_groups: list[np.ndarray],
    bounds: tuple[tuple[int, int], ...],
) -> list[np.ndarray]:
    """Gather one contiguous sub-array per index group.

    ``np.split`` partitions ``shuffle_arr`` end to end, so the concatenation of
    ``shuffle_groups`` IS ``shuffle_arr`` and ``x[:, shuffle_arr][:, a:b]``
    holds exactly the elements of ``x[:, shuffle_groups[i]]`` in the same
    order — pure data movement, no arithmetic, so the two spellings are
    bit-identical by construction.

    The single-gather form is used ONLY at ``M == 1`` (the member-sequential
    hot path).  There a ``(1, n_i)`` column slice of the ``(1, N)`` gather is
    still C-contiguous, so the downstream ``np.ascontiguousarray`` in the basic
    functions stays a no-op; at ``M > 1`` the same slice is strided and would
    force an extra copy, so the per-group gathers are kept.  The guard is
    therefore load-bearing.
    """
    if x.shape[0] == 1:
        full = x[:, shuffle_arr]
        return [full[:, a:b] for a, b in bounds]
    return [x[:, sg] for sg in shuffle_groups]


def hybrid_shuffle_groups(
    func_idx: int,
    N: int,
    proportions: Sequence[float],
    shuffle_arr: np.ndarray,
) -> tuple[list[np.ndarray], tuple[tuple[int, int], ...]]:
    """Return the split of a hybrid's DEFAULT shuffle, memoised by (func_idx, N).

    See ``_hybrid_groups_cache``.  Only the default path (no caller-supplied
    ``shuffle=``) may call this: ``shuffle_arr`` must be ``shuffles[N][func_idx]``.
    Both ``proportions`` and ``shuffle_arr`` are re-checked by identity, so a
    reloaded or monkeypatched data table can never serve a stale split.
    """
    cached = _hybrid_groups_cache.get((func_idx, N))
    if cached is not None and cached[0] is proportions and cached[1] is shuffle_arr:
        return cached[2], cached[3]
    shuffle_groups, bounds = _split_shuffle(shuffle_arr, N, proportions)
    _hybrid_groups_cache[(func_idx, N)] = (
        proportions, shuffle_arr, shuffle_groups, bounds,
    )
    return shuffle_groups, bounds


def partition_by_groups(
    x: np.ndarray,
    shuffle_arr: np.ndarray,
    shuffle_groups: list[np.ndarray],
    bounds: tuple[tuple[int, int], ...],
) -> list[np.ndarray]:
    """Public alias of :func:`_extract_groups` for the hybrid layer."""
    return _extract_groups(x, shuffle_arr, shuffle_groups, bounds)


# Clean up module scope
del _data
del _f
