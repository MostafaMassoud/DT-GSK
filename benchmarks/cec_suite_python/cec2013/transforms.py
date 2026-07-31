"""CEC2013 data loading and transform helpers.

Cross-reference: ``test_func.c`` (Jane Jing Liang, 27 Jan 2013),
helper functions ``shiftfunc`` (line 981), ``rotatefunc`` (line 990),
``oszfunc`` (line 1013), ``asyfunc`` (line 1003).

Loads shift vectors and rotation matrices from a SHA-256-verified
``data.pkl`` blob (mirrors the CEC2017 layout).  Provides vectorised
transform helpers matching the C implementation:

  - :func:`osz_func` -- oscillation (first/last dimensions only, C line 1019)
  - :func:`asy_func` -- asymmetry with C buffer-reuse semantics (C line 1003)
  - :func:`conditioning` -- ill-conditioning scaling (inline in C, e.g. line 384)

Data layout
-----------
``data.pkl`` is a single pickled dict with two keys::

    {
        "shift_flat": ndarray(1000,) float64,         # 10 x 100 flat
        "rotations": {
            2:   ndarray(10, 2, 2)   float64,
            5:   ndarray(10, 5, 5)   float64,
            ...
            100: ndarray(10, 100, 100) float64,
        },
    }

Each leaf is stored as ``('__np_array__', dtype_str, shape, raw_bytes)``
to dodge pickle's version-sensitive numpy serialisation; ``_reconstruct``
recovers the ndarrays at load time.  See ``make_data_pkl.py`` for the
one-shot text->pickle converter.

Data loading semantics
~~~~~~~~~~~~~~~~~~~~~~
The C code loads shift data with sequential ``fscanf`` (line 114)::

    OShift = malloc(nx * cf_num * sizeof(double));
    for (i = 0; i < cf_num * nx; i++)
        fscanf(fpt, "%lf", &OShift[i]);

Then accesses shift *i* at ``OShift[i*nx]``.  Because ``fscanf`` reads
sequentially regardless of line breaks, when ``nx < 100`` the shifts
cross file row boundaries.  For example, with nx=50:

  - shift 0 = flat[0:50]    (first 50 values of file row 0)
  - shift 1 = flat[50:100]  (last 50 values of row 0)
  - shift 2 = flat[100:150] (first 50 values of row 1)

We replicate this by storing the raw 1000-double flat array and slicing
``flat[:10*dim].reshape(10, dim)`` per dimension, rather than row-slicing
the (10, 100) matrix.

Rotation matrices are stored as ``(10, dim, dim)`` ndarrays per dim,
which matches the per-component slice ``&M[i*nx*nx]`` in the C code
(C line 91-101).  Row-major layout matches numpy's default C-order.

Numba acceleration
------------------
When numba is available, ``osz_func``, ``asy_func``, and ``conditioning``
dispatch to JIT-compiled kernels.  Otherwise pure NumPy fallback is used.

Caching strategy
~~~~~~~~~~~~~~~~
- **Shift data**: loaded once as flat 1-D array from ``data.pkl``, then
  reshaped per-dimension on first access.  Cached in ``_shift_dim_cache[dim]``.
- **Rotation matrices**: loaded once per dimension from ``data.pkl``,
  stored as ``(10, dim, dim)`` in ``_rotation_cache[dim]``.
- **Conditioning scale vectors**: cached per ``(dim, alpha)`` key in
  ``_cond_scale_cache`` to avoid recomputing ``alpha^(i/(2*(N-1)))``
  on every function call.

SECURITY: ``data.pkl`` is loaded via ``pickle.loads()`` after SHA-256
integrity verification.  The hash check prevents use of tampered files,
but pickle deserialization can still execute arbitrary code embedded in
a valid-hash file.  Only use ``data.pkl`` files from trusted sources
(re-generate from text via ``make_data_pkl.py`` if in doubt).  Never
replace with files from untrusted origins.
"""

from __future__ import annotations

import hashlib
import os
import pickle
import threading

import numpy as np

_DATA_PATH = os.path.join(os.path.dirname(__file__), "data.pkl")
_EXPECTED_SHA256 = "1af80d77ad6f92bc06b8b7e29e7d5373475ce1d65b1315d97ed891bf3875ef5b"
VALID_DIMS = frozenset({2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100})

# Composition "infinite weight" sentinel.  Matches C ``INF`` in test_func.c
# (line 18: ``#define INF 1.0e99``).  This is the single source of truth --
# ``composition.py`` imports it directly, and ``_numba.py`` defines a
# module-local copy that is asserted equal at import time (see ``_numba.py``).
INF: float = 1.0e99

# ---------------------------------------------------------------------------
# Numba kernels (graceful fallback)
# ---------------------------------------------------------------------------
try:
    from ._numba import asy_func_nb as _asy_nb
    from ._numba import conditioning_nb as _cond_nb
    from ._numba import osz_func_nb as _osz_nb
except ImportError:
    _osz_nb = None
    _asy_nb = None
    _cond_nb = None

# Serial (parallel=False) twins + the thread-local routing flag for opted-in
# optimizers (see _numba_serial.py / _kernel_mode.py).  Outside a
# serial_kernel_scope() the conditioning call site below takes the batch branch
# unchanged.  ``osz_func`` / ``asy_func`` are NOT routed: their kernels are
# already declared parallel-free in ``_numba.py``, so their "twin" is the same
# dispatcher object and a mode check could only ever pick the same binary.
try:
    from . import _numba_serial as _ns
    from ._kernel_mode import serial_kernels_active as _serial_kernels_active
except ImportError:
    _ns = None

    def _serial_kernels_active() -> bool:
        """Fallback when the serial-kernel modules are unavailable."""
        return False


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
            f"CEC2013 data.pkl integrity check failed. "
            f"Expected SHA-256 {_EXPECTED_SHA256[:16]}..., "
            f"file may be corrupted or tampered."
        )
    return _reconstruct(pickle.loads(blob))


_data = _load_data_blob()
_shift_flat: np.ndarray = np.ascontiguousarray(
    _data["shift_flat"], dtype=np.float64,
)
_rotations_all: dict[int, np.ndarray] = {
    int(d): np.ascontiguousarray(arr, dtype=np.float64)
    for d, arr in _data["rotations"].items()
}
del _data

# Audit REPRO-CRIT-1: freeze the master shift / rotation arrays so an
# accidental in-place mutation by a downstream caller cannot poison
# subsequent NFE evaluations.  ``ndarray.flags.writeable = False`` is a
# zero-cost guard that the NumPy and Numba kernels respect (assignment
# raises ``ValueError`` instead of silently corrupting state).  The
# per-dim caches built lazily below are zero-copy views into these
# frozen master arrays, so they inherit the read-only flag automatically.
_shift_flat.flags.writeable = False
for _rot_arr in _rotations_all.values():
    _rot_arr.flags.writeable = False

# Audit AUDIT-06: use a shared reentrant lock for thread safety under
# free-threaded CPython 3.13t (--disable-gil), mirroring the
# CEC2013LSGO ``_CACHE_LOCK`` pattern.  RLock is reentrant so that
# callers like ``_defaults`` (simple.py) which chain multiple cache
# lookups cannot self-deadlock.  The fast read path stays lock-free;
# only the "not present" branch acquires the lock with a double-check.
_CACHE_LOCK = threading.RLock()

_shift_dim_cache: dict[int, np.ndarray] = {}
_rotation_cache: dict[int, np.ndarray] = {}

# XS-01: Pre-transpose all rotation matrices at load time so downstream
# ``y @ rotation.T`` can use a C-contiguous right operand via
# ``y @ rotation_T_cache[dim][idx]``.
_rotation_T_all: dict[int, np.ndarray] = {}
for _d_key, _r_arr in _rotations_all.items():
    # _r_arr is (10, dim, dim); transpose last two axes → (10, dim, dim)
    _rt = np.ascontiguousarray(_r_arr.transpose(0, 2, 1))
    _rt.flags.writeable = False
    _rotation_T_all[_d_key] = _rt
del _d_key, _r_arr, _rt


def _get_shifts_for_dim(dim: int) -> np.ndarray:
    """Return (10, dim) shift matrix using C flat-sequential indexing.

    The C code reads ``10 * dim`` doubles sequentially from ``shift_data.txt``
    and accesses shift *i* at ``OShift[i*dim .. (i+1)*dim - 1]``.  This does
    **not** correspond to ``shift_data[row_i, :dim]`` when ``dim < 100``.
    """
    if dim not in _shift_dim_cache:
        with _CACHE_LOCK:
            if dim not in _shift_dim_cache:
                total = 10 * dim
                _shift_dim_cache[dim] = np.ascontiguousarray(
                    _shift_flat[:total].reshape(10, dim), dtype=np.float64,
                )
    return _shift_dim_cache[dim]


def _load_rotations(dim: int) -> np.ndarray:
    """Return rotation matrices for dimension *dim*: (10, dim, dim) contiguous.

    Data is loaded from ``data.pkl`` at module init; this function only
    enforces the per-dim cache and the VALID_DIMS gate.
    """
    if dim not in _rotation_cache:
        with _CACHE_LOCK:
            if dim not in _rotation_cache:
                if dim not in VALID_DIMS:
                    raise ValueError(
                        f"No rotation data for D={dim}. "
                        f"Valid dims: {sorted(VALID_DIMS)}"
                    )
                _rotation_cache[dim] = _rotations_all[dim]
    return _rotation_cache[dim]


def get_shift(dim: int, idx: int = 0) -> np.ndarray:
    """Return shift vector *idx* for dimension *dim*: length *dim*.

    Uses C flat-sequential indexing into ``shift_data.txt``.

    Parameters
    ----------
    dim : int
        Problem dimensionality (must be in VALID_DIMS for rotation data,
        but shift data supports any dim <= 100).
    idx : int
        Shift vector index, 0-9.

    Returns
    -------
    np.ndarray
        1-D float64 array of length *dim*.
    """
    return _get_shifts_for_dim(dim)[idx]


def get_rotation(dim: int, idx: int = 0) -> np.ndarray:
    """Return rotation matrix *idx* for dimension *dim*: (dim, dim).

    Parameters
    ----------
    dim : int
        Problem dimensionality (must be in VALID_DIMS).
    idx : int
        Matrix index, 0-9.

    Returns
    -------
    np.ndarray
        (dim, dim) orthogonal rotation matrix, C-contiguous float64.
    """
    return _load_rotations(dim)[idx]


def get_rotation_T(dim: int, idx: int = 0) -> np.ndarray:
    """Return the pre-transposed C-contiguous rotation matrix.

    XS-01: returns ``rotation_T`` such that ``y @ rotation_T`` is equivalent
    to ``y @ rotation.T`` but with a C-contiguous right operand for optimal
    BLAS throughput (the on-the-fly ``.T`` view forces a strided code path).

    Parameters
    ----------
    dim : int
        Problem dimensionality (must be in VALID_DIMS).
    idx : int
        Matrix index, 0-9.

    Returns
    -------
    np.ndarray
        (dim, dim) C-contiguous float64 matrix, read-only.
    """
    return _rotation_T_all[dim][idx]


# ---------------------------------------------------------------------------
# Transform helpers -- vectorised for (M, N) batches
# ---------------------------------------------------------------------------

def osz_func(x: np.ndarray) -> np.ndarray:
    """Oscillation transform -- first and last dimensions only.

    Middle dimensions are copied unchanged.  Matches C ``oszfunc`` exactly.

    C reference (lines 1013-1044)::

        for (j = 0; j < nx; j += max(1, nx-1))  // j = 0 and j = nx-1
        {
            if (x[i*nx+j] != 0)
                xx = log(fabs(x[i*nx+j]));
            if (x[i*nx+j] > 0) { c1=10; c2=7.9; sx=1; }
            else                { c1=5.5; c2=3.1; sx=-1; }
            y[i*nx+j] = sx * exp(xx + 0.049*(sin(c1*xx) + sin(c2*xx)));
        }

    Note: CEC2013 osz only transforms dimensions 0 and N-1 (not all).

    Parameters
    ----------
    x : (M, N)

    Returns
    -------
    (M, N) -- transformed array (new allocation).
    """
    if _osz_nb is not None:
        return _osz_nb(np.ascontiguousarray(x, dtype=np.float64))

    result = x.copy()
    N = x.shape[1]
    for dim_idx in (0, N - 1) if N > 1 else (0,):
        xi = x[:, dim_idx]
        nonzero = xi != 0.0
        safe_xi = np.where(nonzero, xi, 1.0)
        xx = np.log(np.abs(safe_xi))
        c1 = np.where(xi > 0, 10.0, 5.5)
        c2 = np.where(xi > 0, 7.9, 3.1)
        sx = np.sign(xi)
        result[:, dim_idx] = np.where(
            nonzero,
            sx * np.exp(xx + 0.049 * (np.sin(c1 * xx) + np.sin(c2 * xx))),
            0.0,
        )
    return result


def asy_func(
    x_in: np.ndarray, prev_buf: np.ndarray, beta: float,
) -> np.ndarray:
    """Asymmetry transform with C buffer-reuse semantics.

    For ``x_in[i] > 0``:
        output[i] = x_in[i] ** (1 + beta * i/(N-1) * sqrt(x_in[i]))
    For ``x_in[i] <= 0``:
        output[i] = prev_buf[i]  (previous buffer content)

    This is the most numerically sensitive transform in CEC2013.  Different
    matrix multiplication orderings (BLAS kernels) can produce ULP-level
    differences in x_in, which get exponentially amplified by the power
    function.  This is the root cause of the ~3e-4 relative differences
    observed in batch-vs-single consistency tests for F8 (Ackley) and
    similar functions with the asy transform.

    Parameters
    ----------
    x_in : (M, N) -- input array (read-only).
    prev_buf : (M, N) -- previous buffer content (used where x_in <= 0).
    beta : float -- asymmetry strength (typically 0.2 or 0.5).

    Returns
    -------
    (M, N) -- transformed array (new allocation).
    """
    N = x_in.shape[1]
    # Guard: N=1 → exponent is always 1.0 (idx=0, beta*0/(0)=0 by convention).
    # CEC2013 always has N≥2 but guard prevents ZeroDivisionError in Numba.
    if N == 1:
        return np.where(x_in > 0, x_in, prev_buf)

    if _asy_nb is not None:
        return _asy_nb(
            np.ascontiguousarray(x_in, dtype=np.float64),
            np.ascontiguousarray(prev_buf, dtype=np.float64),
            beta,
        )

    mask = x_in > 0
    idx = _get_asy_idx(N)
    # Use 1e-300 floor to avoid log(0) in power computation
    safe = np.maximum(x_in, 1e-300)
    exponent = 1.0 + beta * idx / (N - 1) * np.sqrt(safe)
    return np.where(mask, np.power(safe, exponent), prev_buf)


# ---------------------------------------------------------------------------
# Asymmetry -- per-dim index vector cache (thread-safe double-check locking)
# ---------------------------------------------------------------------------
_asy_idx_cache: dict[int, np.ndarray] = {}


def _get_asy_idx(N: int) -> np.ndarray:
    """Return cached arange(N, dtype=float64) for asy_func fallback."""
    if N not in _asy_idx_cache:
        with _CACHE_LOCK:
            if N not in _asy_idx_cache:
                _asy_idx_cache[N] = np.arange(N, dtype=np.float64)
    return _asy_idx_cache[N]


# ---------------------------------------------------------------------------
# Conditioning -- with per-(dim, alpha) scale vector cache
# ---------------------------------------------------------------------------
_cond_scale_cache: dict[tuple[int, float], np.ndarray] = {}


def _get_cond_scale(N: int, alpha: float) -> np.ndarray:
    """Return cached conditioning scale vector: alpha^(i / (2*(N-1))).

    Guard: N=1 returns [1.0] (exponent=0/0→0 by convention, so scale=1).
    CEC2013 always has N≥2 but guard prevents NaN if reused externally.

    Parameters
    ----------
    N : int
        Dimension.
    alpha : float
        Condition base (10 or 100).

    Returns
    -------
    np.ndarray
        1-D float64 array of length N.
    """
    key = (N, alpha)
    if key not in _cond_scale_cache:
        with _CACHE_LOCK:
            if key not in _cond_scale_cache:
                if N == 1:
                    _cond_scale_cache[key] = np.ones(1, dtype=np.float64)
                else:
                    idx = np.arange(N, dtype=np.float64)
                    _cond_scale_cache[key] = np.power(alpha, idx / (N - 1) / 2.0)
    return _cond_scale_cache[key]


def conditioning(x: np.ndarray, alpha: float = 10.0) -> np.ndarray:
    """Ill-conditioning: ``x_i *= alpha^(i / (2*(N-1)))``.

    C reference: inline scaling, e.g.::

        z[i] = y[i] * pow(10.0, 1.0*i/(nx-1)/2.0)    // Schaffer F7, line 384
        z[i] = y[i] * pow(100.0, 1.0*i/(nx-1)/2.0)   // Griewank, line 498

    The scale vector is cached per ``(N, alpha)`` so it is computed once
    and reused across all subsequent calls with the same parameters.

    Parameters
    ----------
    x : (M, N)
    alpha : float -- condition base (10 or 100).

    Returns
    -------
    (M, N) -- scaled array (new allocation).
    """
    N = x.shape[1]
    # Guard: N=1 → exponent is 0/(2*0) = 0/0; by convention scale=1.0 (identity).
    # Must be BEFORE Numba dispatch: conditioning_nb divides by float(N-1)=0.0 → NaN.
    if N == 1:
        return x.copy()

    if _cond_nb is not None:
        kernel = _ns.conditioning_nb if _serial_kernels_active() else _cond_nb
        return kernel(np.ascontiguousarray(x, dtype=np.float64), alpha)

    scale = _get_cond_scale(N, alpha)
    return x * scale
