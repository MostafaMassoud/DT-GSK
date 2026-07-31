"""CEC2020 basic (leaf) functions — raw mathematical formulas.

Architecture difference from CEC2014/2017/2022:
  In CEC2020, shrink rates are NOT baked into these functions. The caller
  (hybrid._apply or composition._eval_component) is responsible for scaling
  input via shift_rotate's shrink parameter or manual multiplication.
  The docstrings note the EXPECTED shrink rate for reference only.

  CEC2014/2017/2022: basic_func(x) internally does x = x * shrink_rate
  CEC2020:           caller does z = shift_rotate(x, Os, Mr, shrink, ...) first

All functions use the axis=-1 convention (instead of axis=1), making them
compatible with both (M, D) batch input and (D,) single-vector input.
This is unique to CEC2020 — other suites use axis=1 for 2D-only input.

Functions provided (15 total, matching CEC2017/2022 base set plus schaffer_F7):
  bent_cigar, ellips, discus, rosenbrock, ackley, rastrigin, schwefel,
  griewank, weierstrass, katsuura, happycat, hgbat, grie_rosen,
  escaffer6, schaffer_F7
"""

import threading

import numpy as np

PI = np.pi
TWO_PI = 2.0 * PI
E = np.e

# ---------------------------------------------------------------------------
# C20-1: per-dimension coefficient caches for fallback (NumPy) paths.
# Thread-safe via double-check locking with _CACHE_LOCK.
# ---------------------------------------------------------------------------
_CACHE_LOCK = threading.RLock()

_elliptic_coeff_cache: dict[int, np.ndarray] = {}
_griewank_sqrt_cache: dict[int, np.ndarray] = {}
_katsuura_idx_cache: dict[int, np.ndarray] = {}

# Weierstrass: constant arrays independent of D (k_max=20 always)
_WEIER_AK_FB = np.array([0.5 ** k for k in range(21)], dtype=np.float64)
_WEIER_BK_FB = np.array([3.0 ** k for k in range(21)], dtype=np.float64)
_WEIER_OFFSETS_FB = 2.0 * PI * _WEIER_BK_FB
_WEIER_CORRECTION_FB = float(np.sum(_WEIER_AK_FB * np.cos(_WEIER_OFFSETS_FB * 0.5)))

# Katsuura: constant power-of-2 array (j=1..32)
_KATSUURA_POW2J_FB = np.array([2.0 ** (j + 1) for j in range(32)], dtype=np.float64)

# Numba-accelerated raw kernels (no baked-in shrink)
# Live in benchmarks/cec_suite_python/cec2020/_numba.py — same per-suite layout as
# CEC2017 / CEC2013 / CEC2011 / CEC2013LSGO.
try:
    from ._numba import (
        bent_cigar_raw_nb as _bc, ellips_raw_nb as _el, discus_raw_nb as _di,
        rosenbrock_raw_nb as _ro, ackley_raw_nb as _ac, rastrigin_raw_nb as _ra,
        schwefel_raw_nb as _sc, griewank_raw_nb as _gr, weierstrass_raw_nb as _we,
        katsuura_raw_nb as _ka, happycat_raw_nb as _hc, hgbat_raw_nb as _hg,
        grie_rosen_raw_nb as _gri, escaffer6_raw_nb as _es, schaffer_F7_raw_nb as _sf7,
    )
except ImportError:
    _bc=_el=_di=_ro=_ac=_ra=_sc=_gr=_we=_ka=_hc=_hg=_gri=_es=_sf7=None

def _c(x): return np.ascontiguousarray(x, dtype=np.float64)


def bent_cigar(z: np.ndarray) -> np.ndarray:
    """Bent Cigar. Expected caller shrink: 1.0."""
    if _bc is not None: return _bc(_c(z))
    z = np.asarray(z, dtype=np.float64)
    return z[..., 0]**2 + 1e6 * np.sum(z[..., 1:]**2, axis=-1)


def ellips(z: np.ndarray) -> np.ndarray:
    """High Conditioned Elliptic. Expected caller shrink: 1.0."""
    if _el is not None: return _el(_c(z))
    z = np.asarray(z, dtype=np.float64)
    D = z.shape[-1]
    # C20-1: cached conditioning coefficients.
    coeff = _elliptic_coeff_cache.get(D)
    if coeff is None:
        with _CACHE_LOCK:
            coeff = _elliptic_coeff_cache.get(D)
            if coeff is None:
                coeff = np.power(10.0, 6.0 * np.arange(D) / max(D - 1, 1))
                _elliptic_coeff_cache[D] = coeff
    return np.sum(coeff * z**2, axis=-1)


def discus(z: np.ndarray) -> np.ndarray:
    """Discus. Expected caller shrink: 1.0."""
    if _di is not None: return _di(_c(z))
    z = np.asarray(z, dtype=np.float64)
    return 1e6 * z[..., 0]**2 + np.sum(z[..., 1:]**2, axis=-1)


def rosenbrock(z: np.ndarray) -> np.ndarray:
    """Rosenbrock. Expected caller shrink: 2.048/100. Applies +1 origin shift."""
    if _ro is not None: return _ro(_c(z))
    z = np.asarray(z, dtype=np.float64)
    z = z + 1.0
    t1 = z[..., :-1]**2 - z[..., 1:]
    t2 = z[..., :-1] - 1.0
    return np.sum(100.0 * t1**2 + t2**2, axis=-1)


def ackley(z: np.ndarray) -> np.ndarray:
    """Ackley. Expected caller shrink: 1.0."""
    if _ac is not None: return _ac(_c(z))
    z = np.asarray(z, dtype=np.float64)
    D = z.shape[-1]
    s1 = np.sum(z**2, axis=-1)
    s2 = np.sum(np.cos(TWO_PI * z), axis=-1)
    return E - 20.0 * np.exp(-0.2 * np.sqrt(s1 / D)) - np.exp(s2 / D) + 20.0


def rastrigin(z: np.ndarray) -> np.ndarray:
    """Rastrigin. Expected caller shrink: 5.12/100."""
    if _ra is not None: return _ra(_c(z))
    z = np.asarray(z, dtype=np.float64)
    return np.sum(z**2 - 10.0 * np.cos(TWO_PI * z) + 10.0, axis=-1)


def schwefel(z: np.ndarray) -> np.ndarray:
    """Modified Schwefel. Expected caller shrink: 1000/100."""
    if _sc is not None: return _sc(_c(z))
    z = np.asarray(z, dtype=np.float64)
    D = z.shape[-1]
    z = z + 4.209687462275036e+002

    mask_hi = z > 500
    mask_lo = z < -500
    mask_mid = ~mask_hi & ~mask_lo

    f = np.zeros(z.shape[:-1])

    mod_hi = 500.0 - np.fmod(z, 500.0)
    pen_hi = ((z - 500.0) / 100.0)**2 / D
    f -= np.where(mask_hi, mod_hi * np.sin(np.sqrt(np.abs(mod_hi))), 0.0).sum(axis=-1)
    f += np.where(mask_hi, pen_hi, 0.0).sum(axis=-1)

    mod_lo = -500.0 + np.fmod(np.abs(z), 500.0)
    pen_lo = ((z + 500.0) / 100.0)**2 / D
    f -= np.where(mask_lo, mod_lo * np.sin(np.sqrt(np.abs(mod_lo))), 0.0).sum(axis=-1)
    f += np.where(mask_lo, pen_lo, 0.0).sum(axis=-1)

    f -= np.where(mask_mid, z * np.sin(np.sqrt(np.abs(z))), 0.0).sum(axis=-1)

    f += 4.189828872724338e+002 * D
    return f


def griewank(z: np.ndarray) -> np.ndarray:
    """Griewank. Expected caller shrink: 600/100."""
    if _gr is not None: return _gr(_c(z))
    z = np.asarray(z, dtype=np.float64)
    D = z.shape[-1]
    s = np.sum(z**2, axis=-1) / 4000.0
    # C20-1: cached 1/sqrt(i) coefficients.
    inv_sqrt = _griewank_sqrt_cache.get(D)
    if inv_sqrt is None:
        with _CACHE_LOCK:
            inv_sqrt = _griewank_sqrt_cache.get(D)
            if inv_sqrt is None:
                inv_sqrt = 1.0 / np.sqrt(np.arange(1, D + 1, dtype=np.float64))
                _griewank_sqrt_cache[D] = inv_sqrt
    p = np.prod(np.cos(z * inv_sqrt), axis=-1)
    return 1.0 + s - p


def weierstrass(z: np.ndarray) -> np.ndarray:
    """Weierstrass. Expected caller shrink: 0.5/100.

    Audit fix (cross M-04): the previous broadcast formed a (..., D, 21)
    temp that scales as M*D*K.  We accumulate the inner k-sum into a
    running 1-D buffer instead, dropping peak memory from O(M*D*K) to
    O(M*D).  Numerics are identical because the sum over k is
    associative.
    """
    if _we is not None: return _we(_c(z))
    z = np.asarray(z, dtype=np.float64)
    D = z.shape[-1]
    # C20-1: use precomputed coefficient arrays.
    z_plus = z + 0.5
    f = np.zeros(z.shape[:-1], dtype=np.float64)
    for k in range(21):
        f += _WEIER_AK_FB[k] * np.sum(np.cos(_WEIER_OFFSETS_FB[k] * z_plus), axis=-1)
    return f - D * _WEIER_CORRECTION_FB


def katsuura(z: np.ndarray) -> np.ndarray:
    """Katsuura. Expected caller shrink: 5/100.

    Audit fix (cross M-04): the previous broadcast formed a (..., D, 32)
    temp that scales as M*D*K.  We accumulate the inner j-sum directly
    into a (..., D) buffer, dropping peak memory from O(M*D*K) to O(M*D).
    Numerics are identical (sum over j is associative).
    """
    if _ka is not None: return _ka(_c(z))
    z = np.asarray(z, dtype=np.float64)
    D = z.shape[-1]
    tmp3 = D ** 1.2
    # C20-1: use precomputed powers of 2 and cached index array.
    temp = np.zeros(z.shape, dtype=np.float64)
    for jv in range(32):
        pw = _KATSUURA_POW2J_FB[jv]
        v = z * pw
        temp += np.abs(v - np.floor(v + 0.5)) / pw
    idx = _katsuura_idx_cache.get(D)
    if idx is None:
        with _CACHE_LOCK:
            idx = _katsuura_idx_cache.get(D)
            if idx is None:
                idx = np.arange(1, D + 1, dtype=np.float64)
                _katsuura_idx_cache[D] = idx
    factors = (1.0 + idx * temp) ** (10.0 / tmp3)
    prod_val = np.prod(factors, axis=-1)
    c = 10.0 / D / D
    return prod_val * c - c


def happycat(z: np.ndarray) -> np.ndarray:
    """HappyCat. Expected caller shrink: 5/100. Applies -1 origin shift."""
    if _hc is not None: return _hc(_c(z))
    z = np.asarray(z, dtype=np.float64)
    D = z.shape[-1]
    z = z - 1.0
    r2 = np.sum(z**2, axis=-1)
    s = np.sum(z, axis=-1)
    return np.power(np.abs(r2 - D), 0.25) + (0.5 * r2 + s) / D + 0.5


def hgbat(z: np.ndarray) -> np.ndarray:
    """HGBat. Expected caller shrink: 5/100. Applies -1 origin shift."""
    if _hg is not None: return _hg(_c(z))
    z = np.asarray(z, dtype=np.float64)
    D = z.shape[-1]
    z = z - 1.0
    r2 = np.sum(z**2, axis=-1)
    s = np.sum(z, axis=-1)
    return np.power(np.abs(r2**2 - s**2), 0.5) + (0.5 * r2 + s) / D + 0.5


def grie_rosen(z: np.ndarray) -> np.ndarray:
    """Griewank-Rosenbrock. Expected caller shrink: 5/100. Applies +1 origin shift."""
    if _gri is not None: return _gri(_c(z))
    z = np.asarray(z, dtype=np.float64)
    z = z + 1.0
    # Main pairs using vectorized slicing
    t1 = z[..., :-1]**2 - z[..., 1:]
    t2 = z[..., :-1] - 1.0
    temp = 100.0 * t1**2 + t2**2
    f = np.sum(temp**2 / 4000.0 - np.cos(temp) + 1.0, axis=-1)
    # Wrap-around: (x[-1], x[0])
    t1w = z[..., -1]**2 - z[..., 0]
    t2w = z[..., -1] - 1.0
    tempw = 100.0 * t1w**2 + t2w**2
    f += tempw**2 / 4000.0 - np.cos(tempw) + 1.0
    return f


def escaffer6(z: np.ndarray) -> np.ndarray:
    """Expanded Scaffer's F6. Expected caller shrink: 1.0."""
    if _es is not None: return _es(_c(z))
    z = np.asarray(z, dtype=np.float64)
    # Main pairs using vectorized slicing
    s2 = z[..., :-1]**2 + z[..., 1:]**2
    t1 = np.sin(np.sqrt(s2))**2
    t2 = (1.0 + 0.001 * s2)**2
    f = np.sum(0.5 + (t1 - 0.5) / t2, axis=-1)
    # Wrap-around
    sw = z[..., -1]**2 + z[..., 0]**2
    tw1 = np.sin(np.sqrt(sw))**2
    tw2 = (1.0 + 0.001 * sw)**2
    f += 0.5 + (tw1 - 0.5) / tw2
    return f


def schaffer_F7(z: np.ndarray) -> np.ndarray:
    """Schaffer's F7. Expected caller shrink: 1.0."""
    if _sf7 is not None: return _sf7(_c(z))
    z = np.asarray(z, dtype=np.float64)
    D = z.shape[-1]
    if D < 2:
        return np.zeros(z.shape[:-1])
    si = np.sqrt(z[..., :-1]**2 + z[..., 1:]**2)
    tmp = np.sin(50.0 * np.power(si, 0.2))
    f = np.sum(np.sqrt(si) + np.sqrt(si) * tmp**2, axis=-1)
    return f**2 / (D - 1)**2
