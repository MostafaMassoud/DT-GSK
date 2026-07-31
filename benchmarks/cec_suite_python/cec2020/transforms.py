"""CEC2020 transforms: data loading, shift-rotate, shuffle-and-partition.

SECURITY: data.pkl is loaded via pickle.loads() after SHA-256 integrity
verification. The hash check prevents use of tampered files, but pickle
deserialization can still execute arbitrary code embedded in a valid-hash
file. Only use data.pkl files from trusted sources (the original benchmark
distribution). Never replace with files from untrusted origins.
"""

from __future__ import annotations

import hashlib
import os
import pickle

import numpy as np

# ---- Load packed data ----
_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA_PATH = os.path.join(_HERE, "data.pkl")
_EXPECTED_SHA256 = '3f160a73dd9c7b2981883c27bd8973bac48361a181e2ff503fc79ce0c3cdb3a0'

with open(_DATA_PATH, "rb") as _f:
    _pkl_bytes = _f.read()
    if hashlib.sha256(_pkl_bytes).hexdigest() != _EXPECTED_SHA256:
        raise RuntimeError(
            f'CEC2020 data.pkl integrity check failed. '
            f'Expected SHA-256 {_EXPECTED_SHA256[:16]}..., file may be corrupted or tampered.'
        )
    _DATA = pickle.loads(_pkl_bytes)
    del _pkl_bytes


def _ascf64(arr: object) -> np.ndarray:
    """Force ndarray → C-contiguous float64 (audit HIGH-PERF-05).

    Pickle does not preserve memory layout: an array sliced from a
    larger buffer at packing time may deserialize as a non-C-contiguous
    view, which forces every Numba kernel and BLAS call to either
    materialize a copy or fall onto the strided GEMM path.  Normalising
    once at load time avoids the per-call cost.
    """
    return np.ascontiguousarray(arr, dtype=np.float64)


shifts = _ascf64(_DATA["shift"])           # (7, 100) for F1-F7
shifts_cf = _ascf64(_DATA["shift_cf"])     # (3, 10, 100) for F8-F10

rotations = {}
rotations_cf = {}
for key, val in _DATA.items():
    if key.startswith("M_cf_D"):
        rotations_cf[int(key[6:])] = _ascf64(val)
    elif key.startswith("M_D"):
        rotations[int(key[3:])] = _ascf64(val)

shuffles = {}
for key, val in _DATA.items():
    if key.startswith("shuffle_D"):
        # Permutations stay int (no float64 cast); only force contiguity.
        shuffles[int(key[9:])] = np.ascontiguousarray(val)

del _DATA


# Audit REPRO-CRIT-1: freeze every loaded array so accidental in-place
# mutation by a downstream caller cannot poison subsequent NFE
# evaluations across the rest of the run.  ``ndarray.flags.writeable =
# False`` is a zero-cost guard that the NumPy and Numba kernels respect
# (assignment raises ``ValueError`` instead of silently corrupting state).
shifts.flags.writeable = False
shifts_cf.flags.writeable = False
for _rot in rotations.values():
    _rot.flags.writeable = False
for _rot in rotations_cf.values():
    _rot.flags.writeable = False
for _sh in shuffles.values():
    _sh.flags.writeable = False
# Guard against empty dicts (no keys iterated → loop variables unbound).
try:
    del _rot, _sh
except NameError:
    pass


# XS-01: Pre-transpose all rotation matrices at load time so the hot-path
# ``y @ Mr_T`` reads a C-contiguous right operand (no transpose view).
# ``np.T`` on a frozen array is a zero-copy view with reversed strides;
# ``np.ascontiguousarray`` materialises the C-order copy once at load time.
# Mirrors the pattern established in ``cec2017/transforms.py``.
def _build_transposed_dict(src: dict) -> dict:
    """Return a dict mirroring *src* with every 2-D/3-D ndarray replaced by
    its C-contiguous transpose (last two axes swapped)."""
    out: dict = {}
    for key, val in src.items():
        if isinstance(val, np.ndarray):
            if val.ndim == 2:
                t = np.ascontiguousarray(val.T)
            elif val.ndim == 3:
                t = np.ascontiguousarray(val.transpose(0, 2, 1))
            else:
                t = val  # 1-D — keep as-is
            t.flags.writeable = False
            out[key] = t
        else:
            out[key] = val
    return out

rotations_T = _build_transposed_dict(rotations)
rotations_cf_T = _build_transposed_dict(rotations_cf)


# ---- Shared shrink rates (single source of truth for hybrid + composition) ----
# Shrink rates map [-100, 100] → the function's natural domain. For example:
#   rastrigin needs [-5.12, 5.12] → 5.12/100 = 0.0512
#   rosenbrock needs [-2.048, 2.048] → 2.048/100 = 0.02048
#   griewank needs [-600, 600] → 600/100 = 6.0
# Functions with rate 1.0 already operate in [-100, 100] naturally.
# The hybrid layer applies these via _apply(func, partition, shrink_rate).
# The composition layer applies these via shift_rotate's shrink parameter.
SHRINK_RATES = {
    'bent_cigar': 1.0,
    'schwefel': 1000.0 / 100.0,
    'rastrigin': 5.12 / 100.0,
    'ellips': 1.0,
    'ackley': 1.0,
    'happycat': 5.0 / 100.0,
    'hgbat': 5.0 / 100.0,
    'discus': 1.0,
    'rosenbrock': 2.048 / 100.0,
    'escaffer6': 1.0,
    'griewank': 600.0 / 100.0,
}


try:
    from ._numba import shift_rotate_2020_fast as _sr2020
except ImportError:
    _sr2020 = None


def shift_rotate(
                 x: np.ndarray,
                 Os: np.ndarray,
                 Mr: np.ndarray,
                 shrink: float,
                 s_flag: int,
                 r_flag: int,
                 *,
                 Mr_T: np.ndarray | None = None,
) -> np.ndarray:
    """Shift and rotate: mirrors C++ sr_func exactly.

    XS-01: when *Mr_T* is provided (a C-contiguous pre-transposed
    matrix), it is used directly on the NumPy fallback path, avoiding
    the on-the-fly ``.T`` view which may force the BLAS backend into
    a slower strided code path.  The Numba fast path now consumes
    *Mr_T* too, so both dispatch paths hit the same C-contiguous BLAS
    layout when the pre-transposed matrix is available.
    """
    if _sr2020 is not None:
        return _sr2020(x, Os, Mr, shrink, s_flag, r_flag, Mr_T)
    if s_flag:
        y = (x - Os) * shrink
    else:
        y = x * shrink
    # Audit PERF-LOW-2: ``y`` is already a fresh allocation — both
    # ``(x - Os) * shrink`` and ``x * shrink`` produce a brand-new
    # ndarray.  The previous ``y.copy()`` on the no-rotation branch was
    # therefore a redundant materialisation that doubled the per-NFE
    # allocation traffic for the rare CEC2020 calls that exercise the
    # NumPy fallback (Numba unavailable).  ``y @ Mr.T`` likewise returns
    # a fresh array, so the post-condition "result is independent of
    # ``x``" is preserved unconditionally.
    if r_flag:
        if Mr_T is not None:
            return y @ Mr_T
        return y @ Mr.T
    return y


# Audit LOW (CEC2020): partition-index cache for ``shuffle_and_partition``.
# Mirrors the ``_partition_cache`` pattern in ``cec2017/transforms.py``.  Each
# F4..F7 hybrid (and the F8..F10 composition layer) passes the same Python-list
# literal for ``Gp`` on every NFE; the ``np.ceil`` + ``np.cumsum`` bookkeeping
# repeats with identical inputs millions of times per DT-GSK run.  Cache by
# ``(D, tuple(Gp), oddball_first)`` so each (dim, hybrid, mode) tuple pays the
# conversion cost exactly once per process.
#
# Cache design contract
# ---------------------
# * **Bounded size.** Keys are ``(D, tuple(Gp), oddball_first)``.  D is drawn
#   from {10, 15, 20} for CEC2020 hybrids and CEC2020 ships ~5 distinct ``Gp``
#   tuples across F4..F10.  The cache is bounded at ~30 entries for the
#   lifetime of any process.  No eviction logic is needed.
# * **Thread safety.** Each value is computed deterministically from its key,
#   so a benign last-write-wins race under multi-threaded access produces the
#   same array.  Relies on the GIL for dict atomicity on the hot path.
# * **Lifetime / invalidation.** Process-global, never invalidated.  Inputs
#   are pure functions of ``D`` / ``Gp`` / ``oddball_first``.
_partition_cache: dict[tuple[int, tuple[float, ...], bool], np.ndarray] = {}


def _get_split_idx(D: int, Gp: list[float], oddball_first: bool) -> np.ndarray:
    """Return cumulative split indices for ``np.split``, cached by key."""
    key = (D, tuple(Gp), oddball_first)
    cached = _partition_cache.get(key)
    if cached is None:
        props = np.asarray(Gp, dtype=np.float64)
        if oddball_first:
            sizes = np.ceil(props[1:] * D).astype(np.intp)   # (K-1,)
            first = D - int(sizes.sum())
            if first < 0:
                raise ValueError(
                    f"Partition proportions {Gp} sum too large for D={D}"
                )
            G_nx = np.empty(len(Gp), dtype=np.intp)
            G_nx[0] = first
            G_nx[1:] = sizes
        else:
            sizes = np.ceil(props[:-1] * D).astype(np.intp)  # (K-1,)
            last = D - int(sizes.sum())
            if last < 0:
                raise ValueError(
                    f"Partition proportions {Gp} sum too large for D={D}"
                )
            G_nx = np.empty(len(Gp), dtype=np.intp)
            G_nx[:-1] = sizes
            G_nx[-1] = last
        cached = np.cumsum(G_nx[:-1])  # (K-1,)
        _partition_cache[key] = cached
    return cached


def shuffle_and_partition(
                          z: np.ndarray,
                          S: np.ndarray,
                          Gp: list[float],
                          oddball_first: bool = False,
) -> list[np.ndarray]:
    """Shuffle vector, then partition into sub-vectors per Gp proportions.

    Uses a cached cumulative-split-index array (see ``_partition_cache``) so
    the per-NFE work is reduced to a single fancy-index plus ``np.split``.

    Parameters
    ----------
    z : (M, D)
        Batch input (the dispatcher handles 1D→2D reshaping).
    S : (D,) int array
        Column permutation (0-indexed).
    Gp : list of float
        Fraction of columns per partition (should sum to ~1.0).
    oddball_first : bool, default False
        When True, the *first* group gets the remainder
        ``D - Σceil(others)`` (CEC2020 F5/F7 convention).
        When False, the *last* group gets the remainder
        (standard CEC2017/2020 convention).

    Returns
    -------
    parts : list of (M, n_i) arrays
        One array per Gp entry.
    """
    D = z.shape[-1]
    # C20-3: split the permutation first, then extract groups directly —
    # avoids the (M, D) transient from ``z[:, S]``.  Matches CEC2017 fix.
    split_idx = _get_split_idx(D, Gp, oddball_first)
    shuffle_groups = np.split(S, split_idx)
    return [z[:, sg] for sg in shuffle_groups]

try:
    del _f  # Release file handle opened in `with` block (may already be out of scope)
except NameError:
    pass
