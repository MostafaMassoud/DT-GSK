"""CEC2013LSGO data loading, transforms, and group infrastructure.

Loads shift vectors, permutation vectors, rotation matrices, group sizes,
and weights from a SHA-256-verified ``data.pkl`` blob (mirrors the
CEC2013 / CEC2017 / CEC2020 layout).  Provides LSGO-specific transforms:
  - :func:`transform_osz` — oscillation (ALL dimensions, unlike CEC2013)
  - :func:`transform_asy` — asymmetry
  - :func:`lambda_transform` — ill-conditioning scaling

Data layout (in the pickle)
---------------------------
``data.pkl`` is a single pickled dict mapping ``"F{id}-{kind}"`` to
``('__np_array__', dtype_str, shape, raw_bytes)`` leaf tuples::

    {
        "F1-xopt":  ('__np_array__', '<f8', (1000,),  <bytes>),
        ...
        "F4-xopt":  ('__np_array__', '<f8', (1000,),  <bytes>),
        "F4-p":     ('__np_array__', '<i8', (1000,),  <bytes>),  # 0-indexed
        "F4-s":     ('__np_array__', '<i8', (7,),     <bytes>),
        "F4-w":     ('__np_array__', '<f8', (7,),     <bytes>),
        "F4-R25":   ('__np_array__', '<f8', (25, 25), <bytes>),
        "F4-R50":   ('__np_array__', '<f8', (50, 50), <bytes>),
        "F4-R100":  ('__np_array__', '<f8', (100, 100), <bytes>),
        ...
    }

Key conventions:
* The permutation vector is **already 0-indexed** in the pickle — the
  loader returns it unchanged.
* Rotation matrices are stored in their **original** (non-transposed)
  row-major form.  The NumPy fallback path applies ``.T`` for the BLAS
  matmul, while the Numba kernels consume the row-major layout directly.
* See :mod:`.make_data_pkl` for the one-shot text→pickle converter.

SECURITY: ``data.pkl`` is loaded via ``pickle.loads()`` after SHA-256
integrity verification.  The hash check prevents use of tampered files,
but pickle deserialization can still execute arbitrary code embedded in
a valid-hash file.  Only use ``data.pkl`` files from trusted sources
(re-generate from text via :mod:`.make_data_pkl` if in doubt).  Never
replace with files from untrusted origins.
"""

from __future__ import annotations

import hashlib
import os
import pickle
import threading
from dataclasses import dataclass

import numpy as np

__all__ = [
    # Constants
    "DIMENSION", "DIMENSION_OVERLAP", "OVERLAP",
    # Data loaders
    "load_xopt", "load_xopt_vec", "load_perm", "load_sizes",
    "load_weights", "load_rotation",
    # Group infrastructure
    "GroupInfo", "GroupInfoFlat", "load_group_info", "load_group_flat",
    # Transforms
    "transform_osz", "transform_asy", "lambda_transform",
    # Utilities
    "clear_caches", "clear_derived_caches", "verify_data_integrity",
]

_DATA_PATH = os.path.join(os.path.dirname(__file__), "data.pkl")
_EXPECTED_SHA256 = "1b79d4caa2b4a4a244bbbda115e833a09b4965091b664515314aea44810743dd"

DIMENSION = 1000
DIMENSION_OVERLAP = 905
OVERLAP = 5

# ---------------------------------------------------------------------------
# Numba kernels (graceful fallback)
# ---------------------------------------------------------------------------
try:
    from ._numba import (
        transform_osz_nb as _osz_nb,
        transform_asy_nb as _asy_nb,
        lambda_transform_nb as _lambda_nb,
    )
except ImportError:
    _osz_nb = None
    _asy_nb = None
    _lambda_nb = None


# ---------------------------------------------------------------------------
# Data loading -- single SHA-256-verified data.pkl, lazy reconstructed
# ---------------------------------------------------------------------------
def _reconstruct(obj: object) -> object:
    """Recursively convert ('__np_array__', dtype, shape, bytes) -> ndarray."""
    if isinstance(obj, tuple) and len(obj) == 4 and obj[0] == "__np_array__":
        return np.frombuffer(obj[3], dtype=obj[1]).reshape(obj[2]).copy()
    if isinstance(obj, dict):
        return {k: _reconstruct(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(_reconstruct(v) for v in obj)
    return obj


def _load_data_blob() -> dict:
    """Read ``data.pkl``, verify SHA-256, return reconstructed dict."""
    with open(_DATA_PATH, "rb") as fh:
        blob = fh.read()
    if hashlib.sha256(blob).hexdigest() != _EXPECTED_SHA256:
        raise RuntimeError(
            f"CEC2013LSGO data.pkl integrity check failed. "
            f"Expected SHA-256 {_EXPECTED_SHA256[:16]}..., "
            f"file may be corrupted or tampered."
        )
    return _reconstruct(pickle.loads(blob))


_DATA: dict[str, np.ndarray] = _load_data_blob()


# Audit REPRO-CRIT-1: freeze every ndarray inside ``_DATA`` so an
# accidental in-place mutation by a downstream caller (e.g. composite
# kernels that briefly alias the shift vector for diagnostic plotting)
# cannot poison subsequent NFE evaluations.  ``ndarray.flags.writeable
# = False`` is a zero-cost guard that the NumPy and Numba kernels respect
# (assignment raises ``ValueError`` instead of silently corrupting state).
# The lazy ``_xopt_cache`` / ``_perm_cache`` / ... entries built later are
# zero-copy views into these frozen master arrays, so they inherit the
# read-only flag automatically.
for _v in _DATA.values():
    if isinstance(_v, np.ndarray):
        _v.flags.writeable = False
del _v


# ---------------------------------------------------------------------------
# Lazy per-function caches (zero-copy views into _DATA)
# ---------------------------------------------------------------------------
# Audit M-5: thread-safety for free-threaded CPython 3.13t (--disable-gil).
#
# On a stock CPython build the GIL makes ``dict.get`` / ``dict[k] = v``
# atomic, so the lazy-populate pattern "check -> build -> assign" is
# already race-free.  Under 3.13t (no-GIL) that guarantee vanishes: two
# worker threads calling ``load_rotation(F8, 50)`` simultaneously could
# both observe "not cached", both run the SHA-256 + orthogonality check,
# and both write the same key.  Worst case it wastes ~1 ms on duplicate
# work; real bug is that observers reading via ``.get`` could briefly
# see a partially-written ``GroupInfo`` / ``GroupInfoFlat`` dataclass if
# a dict resize happens mid-insert.
#
# ``_CACHE_LOCK`` is a single **reentrant** lock shared by all 8 caches:
# ``load_group_info`` internally calls ``load_sizes`` / ``load_weights``
# / ``load_perm`` / ``load_rotation`` / ``load_xopt(_vec)``, each of
# which also acquires the same lock.  A non-reentrant ``Lock`` would
# self-deadlock on the very first cold build.  The populate paths are
# rare (once per (func_id, sub_dim) pair, at most ~30 distinct keys
# total across the whole CEC2013LSGO suite) so there is no contention
# worth fighting with per-cache locks.  The fast read path stays
# lock-free: we check ``dict.get`` outside the lock, and only take it on
# the "not present" branch.  Inside the lock we re-check so two threads
# that both missed do not both populate.
_CACHE_LOCK = threading.RLock()

_xopt_cache: dict[int, np.ndarray] = {}
_xopt_vec_cache: dict[int, list[np.ndarray]] = {}
_perm_cache: dict[int, np.ndarray] = {}
_sizes_cache: dict[int, np.ndarray] = {}
_weights_cache: dict[int, np.ndarray] = {}
_rot_cache: dict[tuple[int, int], np.ndarray] = {}
_group_cache: dict[tuple[int, int], GroupInfo] = {}
_group_flat_cache: dict[tuple[int, int], GroupInfoFlat] = {}


def _ensure_f64(x: np.ndarray) -> np.ndarray:
    """Return C-contiguous float64 view (zero-copy when already correct)."""
    return np.ascontiguousarray(x, dtype=np.float64)


def load_xopt(func_id: int) -> np.ndarray:
    """Load global shift vector ``O`` for function F{func_id}.

    Looks up ``F{id}-xopt`` in the SHA-256-verified ``data.pkl`` blob.
    For F1-F12/F15 (D=1000): 1000 values.  For F13-F14 (overlap, D=905):
    concatenated per-group shifts (total = sum of group sizes).

    F14 (conflicting overlap) stores per-group independent shifts
    end-to-end in its xopt file; use :func:`load_xopt_vec` to split
    them into individual per-group vectors.

    Results are cached in ``_xopt_cache`` — subsequent calls return the
    same array (zero-copy).

    Parameters
    ----------
    func_id : int
        Function number (1-15).

    Returns
    -------
    (D,) float64
        Shift vector, C-contiguous.
    """
    if not (1 <= func_id <= 15):
        raise ValueError(f"load_xopt: func_id must be 1-15, got {func_id}")
    cached = _xopt_cache.get(func_id)
    if cached is not None:
        return cached
    with _CACHE_LOCK:
        cached = _xopt_cache.get(func_id)
        if cached is not None:
            return cached
        key = f"F{func_id}-xopt"
        if key not in _DATA:
            raise KeyError(f"load_xopt: missing entry {key!r} in data.pkl")
        arr = _ensure_f64(_DATA[key])
        _xopt_cache[func_id] = arr
        return arr


def load_xopt_vec(func_id: int) -> list[np.ndarray]:
    """Load per-group shift vectors (conflicting overlap functions).

    For F14, the shift file contains *independent* per-group shift vectors
    concatenated end-to-end (C++ ``readOvectorVec``), so overlapping
    dimensions receive *different* shift values from different groups,
    creating optimization conflicts.  This function splits the flat
    xopt array into a list of per-group vectors using group sizes.

    Contrast with F13 (conforming): a single global shift vector is
    indexed by each group's permutation — shared dimensions get the
    *same* shift value.

    Parameters
    ----------
    func_id : int
        Function number (typically 14).

    Returns
    -------
    list of (s_i,) float64 arrays
        One shift vector per group, C-contiguous.
    """
    cached = _xopt_vec_cache.get(func_id)
    if cached is not None:
        return cached
    with _CACHE_LOCK:
        cached = _xopt_vec_cache.get(func_id)
        if cached is not None:
            return cached
        sizes = load_sizes(func_id)
        all_vals = load_xopt(func_id)
        vecs = []
        c = 0
        for s in sizes:
            vecs.append(np.ascontiguousarray(all_vals[c:c + s], dtype=np.float64))
            c += s
        _xopt_vec_cache[func_id] = vecs
        return vecs


def load_perm(func_id: int) -> np.ndarray:
    """Load permutation vector ``P`` (already 0-indexed).

    Looks up ``F{id}-p`` in the SHA-256-verified ``data.pkl`` blob — the
    permutation is **pre-converted** to 0-indexed at build time, so no
    per-call ``val - 1`` adjustment is needed.

    The permutation maps consecutive indices to scattered columns of the
    population matrix, creating the random grouping structure.  Group
    *i* uses columns ``P[start:end]`` where ``start``/``end`` are derived
    from cumulative group sizes.  For overlapping functions (F13-F14),
    consecutive groups share ``overlap`` indices.

    Parameters
    ----------
    func_id : int
        Function number (4-14, functions with group structure).

    Returns
    -------
    (D,) int (np.intp)
        0-based permutation vector.
    """
    cached = _perm_cache.get(func_id)
    if cached is not None:
        return cached
    with _CACHE_LOCK:
        cached = _perm_cache.get(func_id)
        if cached is not None:
            return cached
        key = f"F{func_id}-p"
        if key not in _DATA:
            raise KeyError(f"load_perm: missing entry {key!r} in data.pkl")
        arr = np.ascontiguousarray(_DATA[key], dtype=np.intp)
        _perm_cache[func_id] = arr
        return arr


def load_sizes(func_id: int) -> np.ndarray:
    """Load group sizes ``s[]`` for function F{func_id}.

    Looks up ``F{id}-s`` in the SHA-256-verified ``data.pkl`` blob.
    Typical values in CEC2013LSGO are 25, 50, or 100.  For 7-group
    functions (F4-F7), sizes sum to 300 (remainder is 700-dim separable).
    For 20-group functions (F8-F11), sizes sum to 1000.

    Parameters
    ----------
    func_id : int
        Function number (4-14).

    Returns
    -------
    (G,) int (np.intp)
        Per-group dimensionalities.
    """
    cached = _sizes_cache.get(func_id)
    if cached is not None:
        return cached
    with _CACHE_LOCK:
        cached = _sizes_cache.get(func_id)
        if cached is not None:
            return cached
        key = f"F{func_id}-s"
        if key not in _DATA:
            raise KeyError(f"load_sizes: missing entry {key!r} in data.pkl")
        arr = np.ascontiguousarray(_DATA[key], dtype=np.intp)
        _sizes_cache[func_id] = arr
        return arr


def load_weights(func_id: int) -> np.ndarray:
    """Load group weights ``w[]`` for function F{func_id}.

    Looks up ``F{id}-w`` in the SHA-256-verified ``data.pkl`` blob.
    Each weight scales the corresponding group's contribution to the
    total fitness: ``total = sum(w[i] * base_func(rotated_group_i))``.

    Parameters
    ----------
    func_id : int
        Function number (4-14).

    Returns
    -------
    (G,) float64
        Per-group multiplicative weights.
    """
    cached = _weights_cache.get(func_id)
    if cached is not None:
        return cached
    with _CACHE_LOCK:
        cached = _weights_cache.get(func_id)
        if cached is not None:
            return cached
        key = f"F{func_id}-w"
        if key not in _DATA:
            raise KeyError(f"load_weights: missing entry {key!r} in data.pkl")
        arr = _ensure_f64(_DATA[key])
        _weights_cache[func_id] = arr
        return arr


def load_rotation(func_id: int, sub_dim: int) -> np.ndarray:
    """Load orthogonal rotation matrix ``R`` of size ``(sub_dim, sub_dim)``.

    Looks up ``F{id}-R{sub_dim}`` in the SHA-256-verified ``data.pkl``
    blob.  Typical sub_dim values: 25, 50, 100.  All groups of the same
    size within a function share the same rotation matrix (e.g., all
    50-dim groups of F8 use ``F8-R50``).

    The matrix is stored as-loaded (row-major, non-transposed).  The
    NumPy fallback path transposes it for BLAS matmul (``z @ R.T``);
    the Numba fused kernels use the original layout for inline
    ``R @ z`` computation per row.

    On first load, the matrix is verified to be orthogonal (audit M-02
    lsgo): ``R @ R.T ≈ I`` to within ``1e-9``.  A non-orthogonal rotation
    breaks the function-class invariants of the rotated CEC functions
    (the condition number, the global optimum location, and the basin
    geometry all assume an orthogonal change of basis), so we fail
    loudly here rather than silently shipping a corrupted benchmark.

    Parameters
    ----------
    func_id : int
        Function number (4-14).
    sub_dim : int
        Group dimensionality (25, 50, or 100).

    Returns
    -------
    (sub_dim, sub_dim) float64
        Orthogonal rotation matrix, C-contiguous.

    Raises
    ------
    RuntimeError
        If the loaded matrix is not orthogonal.
    """
    cache_key = (func_id, sub_dim)
    cached = _rot_cache.get(cache_key)
    if cached is not None:
        return cached
    with _CACHE_LOCK:
        # AUDIT-25: the lock is held during the O(sub_dim^3) orthogonality
        # matmul below (``R @ R.T``).  This is acceptable because:
        #   1. The check runs at most once per (func_id, sub_dim) pair --
        #      subsequent calls hit the cache and never enter this block.
        #   2. The worst case is sub_dim=100, costing ~1 ms for a single
        #      (100, 100) matmul -- negligible compared to benchmark
        #      evaluation time.
        #   3. There are at most ~30 distinct (func_id, sub_dim) keys
        #      across the entire CEC2013LSGO suite, so total lock-held
        #      time over the lifetime of a worker is < 30 ms.
        #   4. The lock is reentrant (RLock), so nested calls from
        #      load_group_info -> load_rotation do not deadlock.
        # Moving the matmul outside the lock would introduce a TOCTOU race
        # where two threads could both validate and store the same key,
        # wasting work but not causing correctness issues.  Keeping it
        # inside is simpler and the cost is negligible.
        cached = _rot_cache.get(cache_key)
        if cached is not None:
            return cached
        key = f"F{func_id}-R{sub_dim}"
        if key not in _DATA:
            raise KeyError(
                f"load_rotation: missing entry {key!r} in data.pkl"
            )
        R = _ensure_f64(_DATA[key])
        # Audit M-02 (lsgo): orthogonality assert at first load.
        # Cost is O(sub_dim^3) for one (100, 100) matmul = ~1 ms,
        # paid once per (func_id, sub_dim) pair (max ~30 pairs total).
        gram = R @ R.T
        identity = np.eye(sub_dim, dtype=np.float64)
        max_dev = float(np.max(np.abs(gram - identity)))
        if max_dev > 1e-9:
            raise RuntimeError(
                f"load_rotation: F{func_id} R{sub_dim} is not orthogonal "
                f"(max |R @ R.T - I| = {max_dev:.3e}, tol=1e-9). "
                f"This breaks the rotated-function class invariants; "
                f"data.pkl may be corrupted -- regenerate via "
                f"make_data_pkl.py."
            )
        _rot_cache[cache_key] = R
        return R


# ---------------------------------------------------------------------------
# Pre-computed group information
# ---------------------------------------------------------------------------

@dataclass
class GroupInfo:
    """Pre-computed group indexing for partially-separable functions.

    Holds Python-level data structures used by the NumPy fallback path
    in :func:`composite._eval_groups_*`.  Each group's column indices,
    pre-transposed rotation matrix, and pre-sliced shift vector are
    stored as Python lists of arrays — convenient for indexing but
    requiring a Python loop to iterate.

    Attributes
    ----------
    n_groups : int
        Number of non-separable groups (7 for F4-F7, 20 for F8-F14).
    sizes : (G,) int array
        Per-group dimensionality (25, 50, or 100 in LSGO).
    weights : (G,) float64
        Per-group multiplicative weight ``w[i]``.
    group_indices : list of (s_i,) int arrays
        0-based column indices selecting group *i*'s dimensions from the
        full population matrix.  For overlapping functions (F13-F14),
        consecutive groups share ``overlap`` indices.
    rotation_matrices_T : list of (s_i, s_i) float64 arrays
        Pre-transposed rotation matrices ``R.T`` for BLAS matmul path:
        ``z_rot = z_group @ R_T``  ≡  ``R @ z_group.T`` per row.
    sep_indices : (S,) int array or None
        0-based column indices for the separable remainder (F4-F7 only,
        700 dims).  ``None`` for 20-group and overlapping functions.
    xopt_groups : list of (s_i,) float64 arrays
        Pre-cached ``xopt[group_indices[i]]`` shift slices.  For F14
        (conflicting overlap), these are per-group independent shifts
        loaded via :func:`load_xopt_vec`.
    xopt_sep : (S,) float64 or None
        Pre-cached ``xopt[sep_indices]`` for the separable remainder.
    """
    n_groups: int
    sizes: np.ndarray
    weights: np.ndarray
    group_indices: list[np.ndarray]
    rotation_matrices_T: list[np.ndarray]
    sep_indices: np.ndarray | None
    xopt_groups: list[np.ndarray]
    xopt_sep: np.ndarray | None


@dataclass
class GroupInfoFlat:
    """Pre-flattened group data for Numba fused group kernels.

    All per-group arrays are concatenated into flat contiguous buffers
    so that a single ``@njit(parallel=True)`` call can process every
    group without returning to Python.

    This mirrors :class:`GroupInfo` but replaces Python lists of arrays
    with flat NumPy arrays plus offset tables — the only data types that
    Numba's ``prange`` can consume directly.

    Attributes
    ----------
    n_groups : int
        Number of groups.
    idx_flat : (T,) int64
        Concatenated 0-based column indices for all groups.
        ``idx_flat[group_starts[g]:group_starts[g+1]]`` → group *g*.
    xopt_flat : (T,) float64
        Concatenated per-group shift values, aligned with *idx_flat*.
    rot_flat : (R,) float64
        Concatenated row-major rotation matrices.
        ``rot_flat[rot_offsets[g] : rot_offsets[g+1]]`` → flattened
        ``R_g`` of shape ``(s_g, s_g)`` in row-major order.
    rot_offsets : (G+1,) int64
        Cumulative element counts: ``rot_offsets[g+1] - rot_offsets[g]
        = s_g * s_g``.
    group_starts : (G+1,) int64
        Cumulative dimension counts: ``group_starts[g+1] - group_starts[g]
        = s_g``.
    weights : (G,) float64
        Per-group multiplicative weights.
    sep_indices : (S,) int64 or None
        0-based column indices for the separable remainder (F4-F7 only,
        S=700).  ``None`` for 20-group and overlapping functions.
        Used by fused separable-remainder kernels to avoid M×S temporary
        allocations from Python-level fancy indexing.
    sep_xopt : (S,) float64 or None
        Pre-sliced shift values for the separable remainder, aligned
        with *sep_indices*.
    """
    n_groups: int
    idx_flat: np.ndarray
    xopt_flat: np.ndarray
    rot_flat: np.ndarray
    rot_offsets: np.ndarray
    group_starts: np.ndarray
    weights: np.ndarray
    sep_indices: np.ndarray | None
    sep_xopt: np.ndarray | None


def load_group_info(func_id: int, overlap: int = 0) -> GroupInfo:
    """Build and cache :class:`GroupInfo` for a partially-separable function.

    Loads permutation, group sizes, weights, rotation matrices, and shift
    vectors, then assembles them into a :class:`GroupInfo` dataclass with
    pre-sliced arrays ready for the NumPy fallback evaluation path.

    Group indexing follows the C++ reference: consecutive groups take
    consecutive segments of the permutation vector.  With ``overlap > 0``
    (F13-F14), each group's start is shifted back by ``i * overlap``,
    so consecutive groups share ``overlap`` trailing/leading dimensions.

    Rotation matrices are stored **transposed** (``R.T``) for the NumPy
    BLAS matmul path: ``z_rot = z_group @ R_T`` computes the same result
    as the C++ ``multiply(vector, matrix, dim)`` which does ``R @ z``.

    Parameters
    ----------
    func_id : int
        Function number (4-14).
    overlap : int
        Dimension overlap between consecutive groups.  0 for F4-F11,
        5 for F13-F14.

    Returns
    -------
    GroupInfo
        Cached group data (same object returned on repeated calls).
    """
    if not (1 <= func_id <= 15):
        raise ValueError(
            f"load_group_info: func_id must be 1-15, got {func_id}"
        )
    key = (func_id, overlap)
    cached = _group_cache.get(key)
    if cached is not None:
        return cached
    with _CACHE_LOCK:
        cached = _group_cache.get(key)
        if cached is not None:
            return cached
        sizes = load_sizes(func_id)
        weights = load_weights(func_id)
        perm = load_perm(func_id)
        n_groups = len(sizes)

        group_indices: list[np.ndarray] = []
        rotation_matrices_T: list[np.ndarray] = []
        c = 0  # cumulative raw offset into permutation vector
        for i in range(n_groups):
            # Overlap adjustment: each successive group's window slides
            # back by i*overlap positions so that the LAST `overlap`
            # indices of group i are the FIRST `overlap` of group i+1.
            #
            # Example (overlap=5, sizes=[50,50,...]):
            #   Group 0: perm[0:50]      → dims 0-49
            #   Group 1: perm[45:95]     → dims 45-94 (shares 45-49)
            #   Group 2: perm[90:140]    → dims 90-139 (shares 90-94)
            #
            # Total unique dims = sum(sizes) - (n_groups-1)*overlap = 905
            start = c - i * overlap
            end = c + sizes[i] - i * overlap
            idx = perm[start:end].copy()
            group_indices.append(idx)
            R = load_rotation(func_id, int(sizes[i]))
            rotation_matrices_T.append(np.ascontiguousarray(R.T, dtype=np.float64))
            c += sizes[i]

        # Separable remainder (only for F4-F7 with s_size=7)
        if overlap == 0:
            total_grouped = int(np.sum(sizes))
            if total_grouped < DIMENSION:
                sep_indices = perm[total_grouped:].copy()
            else:
                sep_indices = None
        else:
            sep_indices = None

        # Pre-cache xopt slices per group (avoids full M*1000 shift)
        if func_id == 14:
            # Conflicting overlap: per-group shift vectors
            xopt_vec = load_xopt_vec(func_id)
            xopt_groups = [_ensure_f64(xopt_vec[i]) for i in range(n_groups)]
            xopt_sep = None
        else:
            xopt = load_xopt(func_id)
            xopt_groups = [_ensure_f64(xopt[idx]) for idx in group_indices]
            if sep_indices is not None:
                xopt_sep = _ensure_f64(xopt[sep_indices])
            else:
                xopt_sep = None

        # Audit AUDIT-24: freeze every derived array stored in GroupInfo so
        # that an accidental in-place mutation by a downstream caller cannot
        # poison the cached data.  The parent arrays (_DATA values) are already
        # frozen, but .copy() / _ensure_f64 / R.T create new writable buffers.
        for _arr in group_indices:
            _arr.flags.writeable = False
        for _arr in rotation_matrices_T:
            _arr.flags.writeable = False
        if sep_indices is not None:
            sep_indices.flags.writeable = False
        for _arr in xopt_groups:
            _arr.flags.writeable = False
        if xopt_sep is not None:
            xopt_sep.flags.writeable = False

        gi = GroupInfo(
            n_groups=n_groups,
            sizes=sizes,
            weights=weights,
            group_indices=group_indices,
            rotation_matrices_T=rotation_matrices_T,
            sep_indices=sep_indices,
            xopt_groups=xopt_groups,
            xopt_sep=xopt_sep,
        )
        _group_cache[key] = gi
        return gi


def load_group_flat(func_id: int, overlap: int = 0) -> GroupInfoFlat:
    """Build and cache :class:`GroupInfoFlat` for Numba fused group kernels.

    Converts :class:`GroupInfo` (Python lists of arrays) into flat
    contiguous buffers.  Rotation matrices are stored in **original**
    (non-transposed) row-major form so that the Numba kernel computes
    ``R @ z`` via ``sum_j z[j] * rot_flat[offset + i*d + j]`` — the
    same convention as the C++ ``multiply(vector, matrix, dim)``.

    Parameters
    ----------
    func_id : int
        Function number (4-14).
    overlap : int
        Overlap between consecutive groups (5 for F13-F14, 0 otherwise).

    Returns
    -------
    GroupInfoFlat
        Pre-flattened, C-contiguous, Numba-ready arrays.
    """
    if not (1 <= func_id <= 15):
        raise ValueError(
            f"load_group_flat: func_id must be 1-15, got {func_id}"
        )
    key = (func_id, overlap)
    cached = _group_flat_cache.get(key)
    if cached is not None:
        return cached
    with _CACHE_LOCK:
        cached = _group_flat_cache.get(key)
        if cached is not None:
            return cached
        gi = load_group_info(func_id, overlap)

        # Concatenate group column indices and shift values
        idx_flat = np.concatenate(gi.group_indices)
        xopt_flat = np.concatenate(gi.xopt_groups)

        # Concatenate rotation matrices: store R (not R.T) in row-major.
        # gi.rotation_matrices_T[i] holds R_i.T, so .T gives back R_i.
        rot_parts: list[np.ndarray] = []
        for RT in gi.rotation_matrices_T:
            R_orig = np.ascontiguousarray(RT.T, dtype=np.float64)
            rot_parts.append(R_orig.ravel())
        rot_flat = np.concatenate(rot_parts)

        # Offset tables for variable-size groups
        sizes = np.array([len(idx) for idx in gi.group_indices], dtype=np.int64)
        group_starts = np.zeros(gi.n_groups + 1, dtype=np.int64)
        np.cumsum(sizes, out=group_starts[1:])

        rot_sizes = sizes * sizes  # s_i^2 elements per rotation matrix
        rot_offsets = np.zeros(gi.n_groups + 1, dtype=np.int64)
        np.cumsum(rot_sizes, out=rot_offsets[1:])

        # Separable remainder (F4-F7 only: 700-dim non-grouped portion)
        if gi.sep_indices is not None:
            sep_idx = np.ascontiguousarray(gi.sep_indices, dtype=np.int64)
            sep_xo = np.ascontiguousarray(gi.xopt_sep, dtype=np.float64)
        else:
            sep_idx = None
            sep_xo = None

        gif = GroupInfoFlat(
            n_groups=gi.n_groups,
            idx_flat=np.ascontiguousarray(idx_flat, dtype=np.int64),
            xopt_flat=np.ascontiguousarray(xopt_flat, dtype=np.float64),
            rot_flat=np.ascontiguousarray(rot_flat, dtype=np.float64),
            rot_offsets=np.ascontiguousarray(rot_offsets, dtype=np.int64),
            group_starts=np.ascontiguousarray(group_starts, dtype=np.int64),
            weights=np.ascontiguousarray(gi.weights, dtype=np.float64),
            sep_indices=sep_idx,
            sep_xopt=sep_xo,
        )
        _group_flat_cache[key] = gif
        return gif


# ---------------------------------------------------------------------------
# Cache management
# ---------------------------------------------------------------------------

def clear_derived_caches() -> None:
    """Release the 8 lazy **derived** caches -- NOT the raw data.pkl blob.

    **This function only drops derived/computed caches.**  The
    ~1.25 MB raw ``_DATA`` payload that was loaded, SHA-256 verified
    and frozen at module import time is **left in place** so the next
    lookup can repopulate the derived caches without re-reading disk.
    If you need to free ``_DATA`` as well (e.g. to force a fresh
    integrity check against a freshly rewritten ``data.pkl``), drop
    the entire ``cec2013lsgo.transforms`` module from ``sys.modules``
    instead.

    What gets cleared
    -----------------
    The 8 ``_*_cache`` dicts used by the data loaders and group
    builders:

    * ``_xopt_cache``       -- per-function shift vectors
    * ``_xopt_vec_cache``   -- per-group shift vectors (F14)
    * ``_perm_cache``       -- 0-indexed permutation vectors
    * ``_sizes_cache``      -- per-function group size arrays
    * ``_weights_cache``    -- per-function group weight arrays
    * ``_rot_cache``        -- (func_id, sub_dim) rotation matrices
    * ``_group_cache``      -- GroupInfo Python-side structures
    * ``_group_flat_cache`` -- GroupInfoFlat Numba-side flat buffers

    After clearing, the next function evaluation rebuilds the affected
    lazy structures from ``_DATA`` at negligible cost (microseconds
    per key) -- every cache key is hit at most once per process.

    Why ``_DATA`` is not cleared
    ----------------------------
    1. It is small (~1.25 MB) compared to the derived caches (~50 MB
       when all 15 functions have been evaluated).
    2. Re-loading it would re-trigger the SHA-256 integrity check on
       disk, which is wasted work in steady state.
    3. The derived caches re-populate from ``_DATA`` lazily on the
       next call -- if ``_DATA`` were dropped, the first re-fill would
       have to re-read and re-verify the pickle, which is far slower
       than the lazy lookup it was meant to replace.

    Audit L-4 lsgo: ``clear_caches`` was renamed ``clear_derived_caches``
    after the audit flagged the old name as misleading -- calling
    ``clear_caches()`` suggested *all* cached state would be reset,
    including ``_DATA`` itself, which is not the case.  The old name
    is kept as a backward-compatible alias.
    """
    # Audit M-5: take the same cache lock used by the lazy populate
    # paths so a concurrent ``load_*`` call cannot observe a half-cleared
    # dict set under 3.13t free-threaded CPython.
    with _CACHE_LOCK:
        _xopt_cache.clear()
        _xopt_vec_cache.clear()
        _perm_cache.clear()
        _sizes_cache.clear()
        _weights_cache.clear()
        _rot_cache.clear()
        _group_cache.clear()
        _group_flat_cache.clear()


# Audit L-4 lsgo: backward-compat alias.  The old name is still the
# one in ``__all__`` (below) so existing callers keep working; new
# code should prefer ``clear_derived_caches`` for clarity.
clear_caches = clear_derived_caches


# ---------------------------------------------------------------------------
# Data integrity verification (SHA-256)
# ---------------------------------------------------------------------------

def verify_data_integrity() -> None:
    """Re-verify the SHA-256 of ``data.pkl`` against ``_EXPECTED_SHA256``.

    The check already runs automatically at module import via
    :func:`_load_data_blob`, so this function is mostly redundant.  It
    exists as a public API for tests and runtime sanity checks that want
    to confirm the on-disk pickle has not been swapped between import
    and a later evaluation.

    Raises
    ------
    FileNotFoundError
        If ``data.pkl`` cannot be opened.
    RuntimeError
        If the file's SHA-256 does not match :data:`_EXPECTED_SHA256`,
        indicating corruption or tampering.

    Notes
    -----
    Mirrors the same single-pickle integrity model used by CEC2013,
    CEC2017, and CEC2020.  Replaces the legacy 75-text-file checksum
    table — :func:`make_data_pkl.main` re-builds the pickle from the
    upstream raw text distribution and prints the new SHA-256 if the
    layout ever changes.
    """
    with open(_DATA_PATH, "rb") as fh:
        blob = fh.read()
    if hashlib.sha256(blob).hexdigest() != _EXPECTED_SHA256:
        raise RuntimeError(
            f"CEC2013LSGO data.pkl integrity check failed. "
            f"Expected SHA-256 {_EXPECTED_SHA256[:16]}..., "
            f"file may be corrupted or tampered."
        )


# ---------------------------------------------------------------------------
# Transform helpers — vectorised for (M, N) batches
# ---------------------------------------------------------------------------

def transform_osz(z: np.ndarray) -> np.ndarray:
    r"""Oscillation transform :math:`T_\text{osz}` — ALL dimensions.

    .. math::
        \hat{z}_i = \begin{cases}
            \text{sign}(z_i) \cdot \exp\!\bigl(\hat{x} + 0.049
                \sin(c_1\hat{x}) + \sin(c_2\hat{x})\bigr)
                & \text{if } z_i \neq 0 \\
            0 & \text{if } z_i = 0
        \end{cases}

    where :math:`\hat{x} = \ln|z_i|`, and
    :math:`(c_1,c_2) = (10, 7.9)` for :math:`z_i > 0`,
    :math:`(c_1,c_2) = (5.5, 3.1)` for :math:`z_i < 0`.

    **LSGO-specific**: applies to **every** dimension.  Standard
    CEC2013 only transforms the first and last elements.

    **C++ reference**: ``Benchmarks::T_osz`` in ``Benchmarks.cpp``.

    Parameters
    ----------
    z : (M, N) float64

    Returns
    -------
    (M, N) float64
        Transformed array (new allocation, input not modified).
    """
    if _osz_nb is not None:
        return _osz_nb(_ensure_f64(z))

    nonzero = z != 0.0
    safe_z = np.where(nonzero, z, 1.0)
    hat = np.log(np.abs(safe_z))
    c1 = np.where(z > 0, 10.0, 5.5)
    c2 = np.where(z > 0, 7.9, 3.1)
    sx = np.sign(z)
    return np.where(
        nonzero,
        sx * np.exp(hat + 0.049 * (np.sin(c1 * hat) + np.sin(c2 * hat))),
        0.0,
    )


def transform_asy(z: np.ndarray, beta: float) -> np.ndarray:
    r"""Asymmetry transform :math:`T_\text{asy}`.

    .. math::
        \hat{z}_i = \begin{cases}
            z_i^{\,1 + \beta \cdot \frac{i}{N-1} \cdot \sqrt{z_i}}
                & \text{if } z_i > 0 \\
            z_i & \text{otherwise}
        \end{cases}

    Only positive elements are transformed.  The exponent increases with
    dimension index *i*, so later dimensions are more strongly distorted.
    In LSGO, :math:`\beta = 0.2` for all functions that use this transform.

    **C++ reference**: ``Benchmarks::T_asy`` in ``Benchmarks.cpp``.

    Parameters
    ----------
    z : (M, N) float64
        Input (not modified).
    beta : float
        Asymmetry strength (0.2 for LSGO).

    Returns
    -------
    (M, N) float64
        Transformed array (new allocation).
    """
    if _asy_nb is not None:
        return _asy_nb(_ensure_f64(z), beta)

    N = z.shape[1]
    mask = z > 0
    idx = np.arange(N, dtype=np.float64)
    safe = np.where(mask, z, 1.0)
    exponent = 1.0 + beta * idx / max(N - 1, 1) * np.sqrt(safe)
    return np.where(mask, np.power(safe, exponent), z)


def lambda_transform(z: np.ndarray, alpha: float) -> np.ndarray:
    r"""Ill-conditioning scaling transform :math:`\Lambda(\alpha)`.

    .. math::
        \hat{z}_i = z_i \cdot \alpha^{0.5 \cdot i/(N-1)}

    Creates a condition number of :math:`\sqrt{\alpha}` across dimensions.
    In LSGO, :math:`\alpha = 10` for rastrigin and ackley (condition
    number ≈ 3.16).  Not used by schwefel_1_2 or elliptic.

    **C++ reference**: ``Benchmarks::Lambda`` in ``Benchmarks.cpp``.

    Parameters
    ----------
    z : (M, N) float64
    alpha : float
        Conditioning base (10 for LSGO).

    Returns
    -------
    (M, N) float64
        Scaled array (new allocation).
    """
    if _lambda_nb is not None:
        return _lambda_nb(_ensure_f64(z), alpha)

    N = z.shape[1]
    idx = np.arange(N, dtype=np.float64)
    scale = np.power(alpha, 0.5 * idx / max(N - 1, 1))
    return z * scale
