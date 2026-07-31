"""CEC2013 composition functions F21-F28.

Cross-reference: ``test_func.c`` -- ``cf01`` (line 821) through ``cf08``
(line 957), weight computation ``cf_cal`` (line 1047).

Weighted compositions of base functions.  Each component is evaluated with its
own shift vector and rotation matrices, then the results are combined using
distance-based weights (matching the C ``cf_cal`` function exactly).

Weight formula per component *k* (C ``cf_cal``, line 1061)::

    w_k = (1 / sqrt(dist_sq)) * exp(-dist_sq / (2 * N * delta_k^2))
    w_k = INF  when dist_sq == 0  (x is exactly at the component's optimum)

The final value is: ``f = sum((w_k / sum_w) * (fit_k + bias_k))``.

Note: C adds bias *before* computing weights (``fit[i]+=bias[i]`` at
line 1055) then sums ``w[i]/w_sum*fit[i]`` (line 1082).  We add bias
in the final weighted sum instead -- mathematically identical because
weights depend only on distance to shift vectors, not on fitness values.

Composition structure (from C switch at lines 213-244)
------------------------------------------------------

====  ======  ======  ==========================================  =================
F#    cf0X    r_flag  Components (base func, lambda)              deltas
====  ======  ======  ==========================================  =================
F21   cf01    1       rosen(1.0), dif_pow(1e-6), bent(1e-26),     10,20,30,40,50
                      discus(1e-6), sphere(0.1, r=0)
F22   cf02    0       3x schwefel(1.0)                             20,20,20
F23   cf03    1       3x schwefel(1.0)                             20,20,20
F24   cf04    1       schwefel(0.25), rast(1.0), weier(2.5)        20,20,20
F25   cf05    1       schwefel(0.25), rast(1.0), weier(2.5)        10,30,50
F26   cf06    1       schwefel(0.25), rast(1.0), ellip(1e-7),      10,10,10,10,10
                      weier(2.5), griew(10.0)
F27   cf07    1       griew(100), rast(10), schw(2.5),             10,10,10,20,20
                      weier(25), sphere(0.1, r=0)
F28   cf08    1       grie_ros(2.5), schaff(0.0025), schw(2.5),   10,20,30,40,50
                      escaff(0.0005), sphere(0.1, r=0)
====  ======  ======  ==========================================  =================

Note: In F21/F27/F28, the last component (sphere) has ``r_flag=0`` hardcoded
in the C source (e.g., ``sphere_func(x,&fit[4],nx,&Os[4*nx],&Mr[4*nx*nx],0)``
at line 841), overriding the ``r_flag=1`` passed to the outer ``cf0X`` function.

Rotation matrix indexing
~~~~~~~~~~~~~~~~~~~~~~~~
Each component *i* receives ``&Mr[i*nx*nx]`` as its ``Mr`` pointer.
Functions that use two rotations (bent_cigar, schaffer_F7, ackley,
weierstrass, rastrigin, katsuura, bi_rastrigin, escaffer6) access both
``Mr[0..nx^2-1]`` (M1) and ``Mr[nx^2..2*nx^2-1]`` (M2) relative to that
pointer.  So component *i*'s M1 = rotation[i] and M2 = rotation[i+1].

Performance notes
~~~~~~~~~~~~~~~~~
- Shift vectors and deltas/biases arrays are cached per (N, function_id)
  in ``_comp_meta_cache`` to avoid re-creating them on every evaluation.
- Component lists are module-level tuples (immutable) to avoid list
  rebuilding overhead.
"""

from __future__ import annotations

import threading

import numpy as np

from . import basic
from .transforms import INF, get_rotation, get_rotation_T, get_shift

try:
    from ._numba import cf_cal_nb as _cf_cal_nb
except ImportError:
    _cf_cal_nb = None

# Serial (parallel=False) twins + the thread-local routing flag for opted-in
# optimizers (see _numba_serial.py / _kernel_mode.py).  Outside a
# serial_kernel_scope() the _cf_cal call site takes the batch branch unchanged.
try:
    from . import _numba_serial as _ns
    from ._kernel_mode import serial_kernels_active as _serial_kernels_active
except ImportError:
    _ns = None

    def _serial_kernels_active() -> bool:
        """Fallback when the serial-kernel modules are unavailable."""
        return False


# ---------------------------------------------------------------------------
# cf_cal -- composition weight calculation (broadcasting + numba dispatch)
# ---------------------------------------------------------------------------

def _cf_cal(
    x: np.ndarray,
    comp_shifts_N: np.ndarray,
    deltas: np.ndarray,
    biases: np.ndarray,
    fit_values: np.ndarray,
) -> np.ndarray:
    """Composition weight calculation -- matches C ``cf_cal`` exactly.

    C reference: ``cf_cal`` (lines 1047-1085).

    Audit H-01 (cec2013) — w_max==0 fallback semantics
    --------------------------------------------------
    Both the C source and this Python implementation use ``INF = 1.0e99``
    (a finite sentinel, NOT IEEE ``inf``) when ``dist_sq == 0``.  This
    yields three regimes that match bit-for-bit:

    1. **Single component at distance 0**: ``w[k] = INF``, all others get
       a finite ``exp(...)/sqrt(dist_sq)`` weight.  After normalization
       ``w[k] / w_sum ≈ 1`` and the rest collapse to ``≈ 0`` -- the
       finite-sentinel approach gives the same answer the C reference
       does (and avoids ``inf - inf`` NaNs that a true IEEE ``inf``
       would produce).
    2. **Multiple components at distance 0**: each gets ``w = INF``;
       after normalization each gets weight ``1/k_zero`` where
       ``k_zero`` is the number of zero-distance components.  This
       matches the C arithmetic exactly (``INF/(k*INF) = 1/k`` is
       evaluated in finite double-precision).
    3. **All weights identically zero**: only possible at the boundary
       of double-precision overflow when ``exp(-dist_sq/...)`` underflows
       and we get ``w = 0/sqrt(dist_sq) = 0``.  Both Python and C fall
       back to a uniform weighting in this case (assigning ``w[k] = 1``
       for all *k*); the ``all_zero`` branch below mirrors the C source.

    No code change is needed -- the Python branch above already matches
    the C reference -- but the audit finding flagged the semantics as
    non-obvious, so this docstring captures the correctness argument
    next to the code that implements it.

    Parameters
    ----------
    x : (M, N)
        Population matrix.
    comp_shifts_N : (K, N)
        Shift vectors already sliced to N columns.
    deltas : (K,)
        Delta (sigma) values per component.
    biases : (K,)
        Per-component bias offsets.
    fit_values : (K, M)
        Raw fitness from each component.

    Returns
    -------
    (M,) -- weighted composition fitness values.
    """
    # Numba fast path.
    # H2-CEC2013: callers pass *comp_shifts_N* / *deltas* / *biases* from
    # ``_get_comp_meta`` (already contiguous float64), and *fit_values* from
    # ``np.empty``.  Only *x* needs the contiguity guard.
    if _cf_cal_nb is not None:
        cf_kernel = _ns.cf_cal_nb if _serial_kernels_active() else _cf_cal_nb
        return cf_kernel(
            np.ascontiguousarray(x, dtype=np.float64),
            comp_shifts_N,   # from _get_comp_meta: contiguous float64
            deltas,          # from _get_comp_meta: contiguous float64
            biases,          # from _get_comp_meta: contiguous float64
            fit_values,      # from np.empty: contiguous float64
        )

    M, N = x.shape
    K = len(deltas)

    # Audit MED-PERF (cec2013): expand ``|x - s|^2 = |x|^2 - 2 x.s + |s|^2``
    # so we never materialise the ``(K, M, N)`` diff tensor.  At K=5 / M=100
    # / N=100 the old broadcast allocated a 400 KB temp on every NFE; the
    # expansion does the same arithmetic with three matmuls plus two
    # ``einsum``s and a clamp for floating-point cancellation.
    cs = comp_shifts_N  # H2-CEC2013: already contiguous float64 from caller
    x_norm_sq = np.einsum("ij,ij->i", x, x)               # (M,)
    cs_norm_sq = np.einsum("ij,ij->i", cs, cs)            # (K,)
    cross = cs @ x.T                                       # (K, M)
    dist_sq = x_norm_sq[np.newaxis, :] - 2.0 * cross + cs_norm_sq[:, np.newaxis]
    np.maximum(dist_sq, 0.0, out=dist_sq)                  # clamp FP cancellation

    # Weights: w_i = (1/sqrt(dist_sq)) * exp(-dist_sq / (2*N*delta^2))
    nonzero = dist_sq != 0.0
    safe_dist = np.where(nonzero, dist_sq, 1.0)
    w = np.where(
        nonzero,
        (1.0 / np.sqrt(safe_dist))
        * np.exp(-dist_sq / (2.0 * N * deltas[:, np.newaxis] ** 2)),
        INF,
    )  # (K, M)

    # Normalize weights
    w_sum = np.sum(w, axis=0)  # (M,)
    all_zero = w_sum == 0.0
    if np.any(all_zero):
        w[:, all_zero] = 1.0
        w_sum[all_zero] = float(K)

    # Weighted sum of (fit + bias)
    fit = fit_values + biases[:, np.newaxis]  # (K, M)
    return np.sum((w / w_sum) * fit, axis=0)  # (M,)


# ---------------------------------------------------------------------------
# Cached composition metadata per (N, function_id)
# ---------------------------------------------------------------------------
# Cache contract:
# * **Bounded size.** Keys are ``(N, func_id, deltas, biases, lambdas)``
#   with N in {2, 5, 10, 20, 30, 50, 100} and func_id in 21..28 --
#   bounded at 56 entries for the lifetime of any process.  No eviction
#   needed.
# * **Thread safety.** Audit AUDIT-06: use a reentrant lock for thread
#   safety under free-threaded CPython 3.13t (--disable-gil), mirroring
#   the CEC2013LSGO ``_CACHE_LOCK`` pattern.
# * **Lifetime / invalidation.** Process-global, never invalidated.  Cleared
#   only by tests via ``_comp_meta_cache.clear()``.
_CACHE_LOCK = threading.RLock()
_comp_meta_cache: dict[
    tuple,
    tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
] = {}


def _get_comp_meta(
    N: int,
    func_id: int,
    K: int,
    deltas: tuple[float, ...],
    biases: tuple[float, ...],
    lambdas: tuple[float, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return cached (comp_shifts_N, deltas_arr, biases_arr, lambdas_arr).

    Parameters
    ----------
    N : int
        Dimension.
    func_id : int
        Unique function identifier (21-28) for cache key.
    K : int
        Number of components.
    deltas : tuple of float
        Delta values per component.
    biases : tuple of float
        Bias values per component.
    lambdas : tuple of float
        Per-component scaling factors (broadcast over the (K, M) fit matrix).

    Returns
    -------
    comp_shifts_N : (K, N) ndarray
    deltas_arr : (K,) ndarray
    biases_arr : (K,) ndarray
    lambdas_arr : (K, 1) ndarray -- shaped for broadcasting against (K, M) fit.
    """
    # Audit AUDIT-10: include deltas, biases, and lambdas in the cache key
    # so that hypothetical callers with the same (N, func_id) but different
    # parameter tuples do not receive stale cached arrays.
    key = (N, func_id, deltas, biases, lambdas)
    if key not in _comp_meta_cache:
        with _CACHE_LOCK:
            if key not in _comp_meta_cache:
                comp_shifts_N = np.array(
                    [get_shift(N, i) for i in range(K)], dtype=np.float64,
                )
                _comp_meta_cache[key] = (
                    comp_shifts_N,
                    np.array(deltas, dtype=np.float64),
                    np.array(biases, dtype=np.float64),
                    np.array(lambdas, dtype=np.float64).reshape(K, 1),
                )
    return _comp_meta_cache[key]


# ---------------------------------------------------------------------------
# Helper to evaluate a composition function
# ---------------------------------------------------------------------------

def _eval_composition(
    x: np.ndarray,
    func_id: int,
    components: tuple,
    deltas: tuple[float, ...],
    biases: tuple[float, ...],
) -> np.ndarray:
    """Evaluate a composition function.

    Parameters
    ----------
    x : (M, N)
        Population matrix.
    func_id : int
        Function identifier 21-28 (for cache key).
    components : tuple of (func, needs_m2, r_flag, lam)
        Component specification tuples.  Each contains:
        - func: callable -- base function from basic module
        - needs_m2: bool -- whether the function requires a second rotation
        - r_flag: int -- rotation flag (0 or 1)
        - lam: float -- scaling lambda for the component
    deltas : tuple of float
        Delta (sigma) values per component.
    biases : tuple of float
        Bias values per component.

    Returns
    -------
    (M,) -- composition fitness (before adding the f* offset).
    """
    M, N = x.shape
    K = len(components)

    # Get cached metadata (avoids recreating arrays each call).  ``lambdas``
    # is extracted from the per-component tuple at the call site below so we
    # can pass it to the cache key once and apply it as a single vectorized
    # post-loop multiply rather than K scalar multiplies inside the hot loop.
    lambdas_tuple = _LAMBDAS_MAP.get(id(components))
    if lambdas_tuple is None:
        lambdas_tuple = tuple(c[3] for c in components)
    comp_shifts_N, deltas_arr, biases_arr, lambdas_arr = _get_comp_meta(
        N, func_id, K, deltas, biases, lambdas_tuple,
    )

    fit = np.empty((K, M), dtype=np.float64)

    for i, (func, needs_m2, r_flag, _lam) in enumerate(components):
        Os_i = comp_shifts_N[i]
        M1_i = get_rotation(N, i)
        M1_T_i = get_rotation_T(N, i)
        if needs_m2:
            M2_i = get_rotation(N, i + 1)
            M2_T_i = get_rotation_T(N, i + 1)
            fit[i] = func(x, Os_i, M1_i, M2_i, r_flag,
                          M1_T=M1_T_i, M2_T=M2_T_i)
        else:
            fit[i] = func(x, Os_i, M1_i, r_flag, M1_T=M1_T_i)

    # Vectorized lambda application -- one broadcast multiply over (K, M)
    # instead of K separate scalar multiplies inside the loop above.
    fit *= lambdas_arr

    return _cf_cal(x, comp_shifts_N, deltas_arr, biases_arr, fit)


# ---------------------------------------------------------------------------
# Component specifications (module-level tuples, built once)
# ---------------------------------------------------------------------------
# Each entry: (func, needs_m2, r_flag, lambda)
# needs_m2=True means the function signature includes M2 parameter.

_COMP_F21 = (
    (basic.rosenbrock_func,  False, 1, 10000.0 / 1e4),
    (basic.dif_powers_func,  False, 1, 10000.0 / 1e10),
    (basic.bent_cigar_func,  True,  1, 10000.0 / 1e30),
    (basic.discus_func,      False, 1, 10000.0 / 1e10),
    (basic.sphere_func,      False, 0, 10000.0 / 1e5),
)

_COMP_F22 = (
    (basic.schwefel_func, False, 0, 1.0),
    (basic.schwefel_func, False, 0, 1.0),
    (basic.schwefel_func, False, 0, 1.0),
)

_COMP_F23 = (
    (basic.schwefel_func, False, 1, 1.0),
    (basic.schwefel_func, False, 1, 1.0),
    (basic.schwefel_func, False, 1, 1.0),
)

_COMP_F24 = (
    (basic.schwefel_func,    False, 1, 1000.0 / 4e3),
    (basic.rastrigin_func,   True,  1, 1000.0 / 1e3),
    (basic.weierstrass_func, True,  1, 1000.0 / 400.0),
)

_COMP_F25 = (
    (basic.schwefel_func,    False, 1, 1000.0 / 4e3),
    (basic.rastrigin_func,   True,  1, 1000.0 / 1e3),
    (basic.weierstrass_func, True,  1, 1000.0 / 400.0),
)

_COMP_F26 = (
    (basic.schwefel_func,    False, 1, 1000.0 / 4e3),
    (basic.rastrigin_func,   True,  1, 1000.0 / 1e3),
    (basic.ellips_func,      False, 1, 1000.0 / 1e10),
    (basic.weierstrass_func, True,  1, 1000.0 / 400.0),
    (basic.griewank_func,    False, 1, 1000.0 / 100.0),
)

_COMP_F27 = (
    (basic.griewank_func,    False, 1, 10000.0 / 100.0),
    (basic.rastrigin_func,   True,  1, 10000.0 / 1e3),
    (basic.schwefel_func,    False, 1, 10000.0 / 4e3),
    (basic.weierstrass_func, True,  1, 10000.0 / 400.0),
    (basic.sphere_func,      False, 0, 10000.0 / 1e5),
)

_COMP_F28 = (
    (basic.grie_rosen_func,  False, 1, 10000.0 / 4e3),
    (basic.schaffer_F7_func, True,  1, 10000.0 / 4e6),
    (basic.schwefel_func,    False, 1, 10000.0 / 4e3),
    (basic.escaffer6_func,   True,  1, 10000.0 / 2e7),
    (basic.sphere_func,      False, 0, 10000.0 / 1e5),
)

# Pre-built lambdas tuples -- avoids per-NFE tuple(c[3] for c in components).
_LAMBDAS_F21 = tuple(c[3] for c in _COMP_F21)
_LAMBDAS_F22 = tuple(c[3] for c in _COMP_F22)
_LAMBDAS_F23 = tuple(c[3] for c in _COMP_F23)
_LAMBDAS_F24 = tuple(c[3] for c in _COMP_F24)
_LAMBDAS_F25 = tuple(c[3] for c in _COMP_F25)
_LAMBDAS_F26 = tuple(c[3] for c in _COMP_F26)
_LAMBDAS_F27 = tuple(c[3] for c in _COMP_F27)
_LAMBDAS_F28 = tuple(c[3] for c in _COMP_F28)

# Mapping from component tuple id to pre-built lambdas tuple.
_LAMBDAS_MAP: dict[int, tuple[float, ...]] = {
    id(_COMP_F21): _LAMBDAS_F21,
    id(_COMP_F22): _LAMBDAS_F22,
    id(_COMP_F23): _LAMBDAS_F23,
    id(_COMP_F24): _LAMBDAS_F24,
    id(_COMP_F25): _LAMBDAS_F25,
    id(_COMP_F26): _LAMBDAS_F26,
    id(_COMP_F27): _LAMBDAS_F27,
    id(_COMP_F28): _LAMBDAS_F28,
}


# ---------------------------------------------------------------------------
# F21-F28
# ---------------------------------------------------------------------------

def f21(x: np.ndarray) -> np.ndarray:
    """F21: Composition 1.  f* = 700.

    C reference: ``cf01`` (lines 821-843).

    Components: rosenbrock(d=10), dif_powers(d=20), bent_cigar(d=30),
                discus(d=40), sphere(d=50, r=0).

    Note: sphere has ``r_flag=0`` hardcoded in C (line 841).
    """
    return _eval_composition(
        x, 21, _COMP_F21,
        deltas=(10, 20, 30, 40, 50),
        biases=(0, 100, 200, 300, 400),
    ) + 700.0


def f22(x: np.ndarray) -> np.ndarray:
    """F22: Composition 2.  f* = 800.

    C reference: ``cf02`` (lines 845-861).

    Components: 3x schwefel (all d=20, r_flag=0).
    """
    return _eval_composition(
        x, 22, _COMP_F22,
        deltas=(20, 20, 20),
        biases=(0, 100, 200),
    ) + 800.0


def f23(x: np.ndarray) -> np.ndarray:
    """F23: Composition 3.  f* = 900.

    C reference: ``cf03`` (lines 863-879).

    Components: 3x schwefel (all d=20, r_flag=1).
    """
    return _eval_composition(
        x, 23, _COMP_F23,
        deltas=(20, 20, 20),
        biases=(0, 100, 200),
    ) + 900.0


def f24(x: np.ndarray) -> np.ndarray:
    """F24: Composition 4.  f* = 1000.

    C reference: ``cf04`` (lines 881-899).

    Components: schwefel(d=20), rastrigin(d=20), weierstrass(d=20).
    """
    return _eval_composition(
        x, 24, _COMP_F24,
        deltas=(20, 20, 20),
        biases=(0, 100, 200),
    ) + 1000.0


def f25(x: np.ndarray) -> np.ndarray:
    """F25: Composition 5.  f* = 1100.

    C reference: ``cf05`` (lines 901-919).

    Components: schwefel(d=10), rastrigin(d=30), weierstrass(d=50).
    """
    return _eval_composition(
        x, 25, _COMP_F25,
        deltas=(10, 30, 50),
        biases=(0, 100, 200),
    ) + 1100.0


def f26(x: np.ndarray) -> np.ndarray:
    """F26: Composition 6.  f* = 1200.

    C reference: ``cf06`` (lines 921-941).

    Components: schwefel(d=10), rastrigin(d=10), elliptic(d=10),
                weierstrass(d=10), griewank(d=10).
    """
    return _eval_composition(
        x, 26, _COMP_F26,
        deltas=(10, 10, 10, 10, 10),
        biases=(0, 100, 200, 300, 400),
    ) + 1200.0


def f27(x: np.ndarray) -> np.ndarray:
    """F27: Composition 7.  f* = 1300.

    C reference: ``cf07`` (lines 943-963).

    Components: griewank(d=10), rastrigin(d=10), schwefel(d=10),
                weierstrass(d=20), sphere(d=20, r=0).

    Note: sphere has ``r_flag=0`` hardcoded in C.
    """
    return _eval_composition(
        x, 27, _COMP_F27,
        deltas=(10, 10, 10, 20, 20),
        biases=(0, 100, 200, 300, 400),
    ) + 1300.0


def f28(x: np.ndarray) -> np.ndarray:
    """F28: Composition 8.  f* = 1400.

    C reference: ``cf08`` (lines 965-987).

    Components: grie_rosen(d=10), schaffer_F7(d=20), schwefel(d=30),
                escaffer6(d=40), sphere(d=50, r=0).

    Note: sphere has ``r_flag=0`` hardcoded in C.
    """
    return _eval_composition(
        x, 28, _COMP_F28,
        deltas=(10, 20, 30, 40, 50),
        biases=(0, 100, 200, 300, 400),
    ) + 1400.0
