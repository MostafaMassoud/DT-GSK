"""CEC2017 composition functions F21–F30.

Cross-reference: ``cec17_func.cpp`` (Noor Awad, 2016-2017), composition
functions ``cf01``–``cf10`` (C++ lines 1330–1534) and ``cf_cal`` (line 1645).

Weighted compositions. Each component is a basic function evaluated with its own
shift and rotation, then weighted by distance to each component's optimum.

Weight calculation matches C++ cf_cal (line 1660):
    ``w[i] = (1/sqrt(dist_sq)) * exp(-dist_sq / (2*N*delta[i]²))``
Zero distance → 1e99 (matching C++ INF = 1e99, line 28).

Lambda scaling factors normalize different base functions to comparable ranges::

  Function       Lambda               C++ pattern
  ──────────     ──────────────       ──────────────
  elliptic       10000 / 1e10         fit[i]=10000*fit[i]/1e+10
  ackley         1000 / 100           fit[i]=1000*fit[i]/100
  griewank       1000 / 100           fit[i]=1000*fit[i]/100
  happycat       1000 / 1e3           fit[i]=1000*fit[i]/1e+3
  discus         10000 / 1e10         fit[i]=10000*fit[i]/1e+10
  rastrigin      10000 / 1e3          fit[i]=10000*fit[i]/1e+3
  hgbat          10000 / 1000         fit[i]=10000*fit[i]/1000
  schwefel       10000 / 4e3          fit[i]=10000*fit[i]/4e+3
  bent_cigar     10000 / 1e30         fit[i]=10000*fit[i]/1e+30
  escaffer6      10000 / 2e7          fit[i]=10000*fit[i]/2e+7
  rosenbrock     1.0 (no scaling)     (no fit assignment)

F29 and F30 are composition-of-hybrids (cf09, cf10 in C++).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable

from . import basic, hybrid
from .transforms import rotations_cf, rotations_cf_T, shift_rotate, shifts_cf, shuffles_cf

INF = 1.0e99

try:
    from ._numba import cf_cal_fast as _cf_cal_fast
except ImportError:
    _cf_cal_fast = None

# Serial (parallel=False) twin + the thread-local routing flag for opted-in
# optimizers (see _numba_serial.py / _kernel_mode.py).  Outside a
# serial_kernel_scope() the _cf_cal call site takes the batch branch unchanged.
try:
    from . import _numba_serial as _ns
    from ._kernel_mode import serial_kernels_active as _serial_kernels_active
except ImportError:
    _ns = None

    def _serial_kernels_active() -> bool:
        return False


# L5: composition metadata cache.  Each f21..f30 calls _eval_composition with
# fixed Python-list literals for deltas/biases/lambdas; converting them to
# float64 arrays on every NFE re-allocates K-element arrays millions of times
# per run.  Cache by ``comp_idx`` so each composition pays the conversion cost
# exactly once per process.  This mirrors ``cec2013/composition.py``'s
# ``_comp_meta_cache``.
#
# Cache design contract
# ---------------------
# * **Bounded size.** Keys are integer ``comp_idx`` values in 0..9 (10 entries
#   for F21..F30).  ``f29``/``f30`` use ``comp_idx`` 8 and 9, which do not
#   collide with the 0..7 ``_eval_composition`` slots.  No eviction needed.
# * **Per-comp_idx uniqueness.** ``_eval_composition`` and
#   ``_eval_comp_hybrid`` both call ``_get_comp_meta`` but pass disjoint
#   ``comp_idx`` ranges, so a single shared cache cannot collide.  The
#   ``lambdas`` slot is unused (passed as ``[]``) by ``_eval_comp_hybrid``,
#   which writes a third-tuple element of an empty ``np.array``; that is fine
#   because the hybrid path never reads it back.
# * **Thread safety.** Each value is a deterministic function of its key, so a
#   benign last-write-wins race under multi-threaded access produces the same
#   arrays.  Relies on the GIL for dict atomicity.
# * **Lifetime / invalidation.** Process-global, never invalidated.  Cleared
#   only by tests via ``_comp_meta_cache.clear()``.
_comp_meta_cache: dict[
    int, tuple[np.ndarray, np.ndarray, np.ndarray]
] = {}

# H2: contiguous (K, N) slices of ``shifts_cf[comp_idx][:, :N]``.
# ``shifts_cf`` stores (K, >=N) arrays where the extra columns are unused;
# the Numba kernel ``_cf_cal_nb`` needs a contiguous (K, N) matrix.
# Caching the slice avoids an ``np.ascontiguousarray`` allocation on every
# composition-function NFE.  The cache is bounded: at most 10 comp_idx
# values × 4 benchmark dims = 40 entries.  Thread-safe because each value
# is a deterministic function of its key and dict ops are GIL-atomic.
_cf_shifts_c_cache: dict[tuple[int, int], np.ndarray] = {}


def _get_cf_shifts_c(comp_idx: int, N: int) -> np.ndarray:
    """Return a cached, contiguous ``(K, N)`` component-shift slice."""
    key = (comp_idx, N)
    cached = _cf_shifts_c_cache.get(key)
    if cached is None:
        cached = np.ascontiguousarray(
            shifts_cf[comp_idx][:, :N], dtype=np.float64
        )
        _cf_shifts_c_cache[key] = cached
    return cached


def _get_comp_meta(
    comp_idx: int,
    deltas: list[float],
    biases: list[float],
    lambdas: list[float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return cached float64 arrays for a composition's deltas/biases/lambdas."""
    cached = _comp_meta_cache.get(comp_idx)
    if cached is None:
        cached = (
            np.asarray(deltas, dtype=np.float64),
            np.asarray(biases, dtype=np.float64),
            np.asarray(lambdas, dtype=np.float64),
        )
        _comp_meta_cache[comp_idx] = cached
    return cached


def _cf_cal(
    x: np.ndarray, component_shifts: np.ndarray,
    deltas: np.ndarray, biases: np.ndarray, fit_values: np.ndarray,
) -> np.ndarray:
    """Composition weight calculation — matches C++ cf_cal exactly.

    H2: callers now pass *component_shifts* as a pre-sliced, contiguous
    ``(K, N)`` array (via ``_get_cf_shifts_c``), and *deltas*/*biases* are
    contiguous ``float64`` from the L5 cache, and *fit_values* is a fresh
    ``np.zeros``.  Only *x* needs the ``np.ascontiguousarray`` guard.
    """
    M, N = x.shape

    if _cf_cal_fast is not None:
        cf_kernel = _ns.cf_cal_fast if _serial_kernels_active() else _cf_cal_fast
        return cf_kernel(
            np.ascontiguousarray(x, dtype=np.float64),
            component_shifts,   # H2: already contiguous (K, N) from caller
            deltas,             # L5 cache: contiguous float64
            biases,             # L5 cache: contiguous float64
            fit_values,         # np.zeros: contiguous float64
        )

    K = len(deltas)

    # Add biases to fit values — vectorized over all K components at once.
    # biases is (K,), fit_values is (K, M); broadcasting adds bias per row.
    fit = fit_values + biases[:, np.newaxis]  # (K, M)

    # Compute squared Euclidean distances from each individual to each
    # component's shift vector.  Audit HIGH-PERF-03: previous version
    # built a (K, M, N) ``diff`` tensor (~80 MB at K=10, M=1000, N=100);
    # we now expand ``|x - s|^2 = |x|^2 - 2 x·s + |s|^2`` so the largest
    # temporary is (K, M).  Numerically equivalent for finite inputs.
    cs = component_shifts[:K]                             # (K, N) — pre-sliced
    x_norm_sq = np.einsum('ij,ij->i', x, x)              # (M,)
    cs_norm_sq = np.einsum('ij,ij->i', cs, cs)           # (K,)
    cross = cs @ x.T                                     # (K, M)
    dist_sq = (
        x_norm_sq[np.newaxis, :]
        - 2.0 * cross
        + cs_norm_sq[:, np.newaxis]
    )                                                    # (K, M)
    # Floating-point cancellation can drop dist_sq slightly below zero
    # when x ≈ shift; clamp so the sqrt below is well defined.
    np.maximum(dist_sq, 0.0, out=dist_sq)

    # Weight formula: w_i = (1/dist_i) * exp(-dist_i² / (2*N*δ_i²))
    # Vectorized with np.where to handle dist==0 → INF.
    # Audit round-2: pre-compute safe_dist_sq once to avoid redundant mask
    # application, and use w_sum==0 instead of w_max==0 (saves one reduction).
    delta2 = (2.0 * N * deltas ** 2)[:, np.newaxis]     # (K, 1)
    nonzero = dist_sq != 0.0
    safe_dist_sq = np.where(nonzero, dist_sq, 1.0)      # reused below
    w = np.where(
        nonzero,
        (1.0 / np.sqrt(safe_dist_sq))
        * np.exp(-dist_sq / delta2),  # B1: delta2 always positive (from module-level constants)
        INF,
    )  # (K, M)

    # Normalize weights
    w_sum = np.sum(w, axis=0)  # (M,)

    # Handle case where all weights are 0 (shouldn't happen but match C++)
    all_zero = w_sum == 0.0
    if np.any(all_zero):
        w[:, all_zero] = 1.0
        w_sum[all_zero] = K

    # Weighted sum — fully vectorized dot over K components.
    f = np.sum((w / w_sum) * fit, axis=0)  # (M,)
    return f


def _eval_composition(
    x: np.ndarray, comp_idx: int, func_list: list[Callable[..., np.ndarray]],
    deltas: list[float], biases: list[float], lambdas: list[float],
    shift: np.ndarray | None = None, rotation: np.ndarray | None = None,
) -> np.ndarray:
    """Evaluate a composition function.

    Parameters
    ----------
    x : (M, N)
    comp_idx : 0-based index into shifts_cf/rotations_cf (0=F21, ..., 9=F30)
    func_list : list of basic function callables
    deltas : list of delta (σ) values controlling weight spread
    biases : list of per-component bias offsets
    lambdas : list of lambda multipliers (applied to fit values)
    shift : optional override for component shifts — (K, >=N) array
    rotation : optional override for component rotations — (K, N, N) array
    """
    M, N = x.shape
    K = len(func_list)

    # Defensive length check -- the four parallel lists must agree on K so
    # the per-component loop below cannot silently truncate or skip elements.
    if not (len(deltas) == K and len(biases) == K and len(lambdas) == K):
        raise ValueError(
            f"_eval_composition: list-length mismatch for comp_idx={comp_idx}: "
            f"len(func_list)={K}, len(deltas)={len(deltas)}, "
            f"len(biases)={len(biases)}, len(lambdas)={len(lambdas)}"
        )

    all_shifts = shift if shift is not None else shifts_cf[comp_idx]
    all_rots = rotation if rotation is not None else rotations_cf[N][comp_idx]
    all_rots_T = None if rotation is not None else rotations_cf_T[N][comp_idx]

    # L5: pull deltas/biases/lambdas as cached float64 arrays so each NFE
    # avoids three small ``np.asarray`` allocations.  Safe because every
    # f21..f30 wrapper passes the same Python-list literals on every call.
    deltas_arr, biases_arr, lambdas_arr = _get_comp_meta(
        comp_idx, deltas, biases, lambdas
    )

    fit = np.empty((K, M), dtype=np.float64)  # B9: empty — every row assigned in loop

    for i, func in enumerate(func_list):
        s_i = all_shifts[i]
        R_i = all_rots[i]

        if func is basic.bi_rastrigin:
            # bi_rastrigin has custom shift/rotate
            R_T_i = all_rots_T[i] if all_rots_T is not None else None
            fit[i] = func(x, shift=s_i, rotation=R_i, apply_shift=True, rotation_T=R_T_i)
        elif func is basic.schaffer_F7:
            # Standalone schaffer uses shift only
            y = x - s_i[:N]
            fit[i] = func(y)
        else:
            R_T_i = all_rots_T[i] if all_rots_T is not None else None
            z = shift_rotate(x, s_i, R_i, rotation_T=R_T_i)
            fit[i] = func(z)

        # Apply lambda scaling
        fit[i] *= lambdas_arr[i]

    # H2: pass a contiguous (K, N) shift slice so ``_cf_cal`` can skip the
    # per-call ``np.ascontiguousarray`` copy.  Test overrides bypass the cache.
    if shift is not None:
        shifts_c = np.ascontiguousarray(shift[:, :N], dtype=np.float64)
    else:
        shifts_c = _get_cf_shifts_c(comp_idx, N)

    return _cf_cal(x, shifts_c, deltas_arr, biases_arr, fit)


# C3: module-level function tuples — avoids rebuilding a fresh Python list on
# every NFE.  Each ``_eval_composition`` / ``_eval_comp_hybrid`` call now passes
# an immutable tuple reference instead of a per-call list literal.
_F21_FUNCS = (basic.rosenbrock, basic.elliptic, basic.rastrigin)
_F22_FUNCS = (basic.rastrigin, basic.griewank, basic.schwefel)
_F23_FUNCS = (basic.rosenbrock, basic.ackley, basic.schwefel, basic.rastrigin)
_F24_FUNCS = (basic.ackley, basic.elliptic, basic.griewank, basic.rastrigin)
_F25_FUNCS = (basic.rastrigin, basic.happycat, basic.ackley, basic.discus, basic.rosenbrock)
_F26_FUNCS = (basic.expanded_schaffers_f6, basic.schwefel, basic.griewank,
              basic.rosenbrock, basic.rastrigin)
_F27_FUNCS = (basic.hgbat, basic.rastrigin, basic.schwefel, basic.bent_cigar,
              basic.elliptic, basic.expanded_schaffers_f6)
_F28_FUNCS = (basic.ackley, basic.griewank, basic.discus, basic.rosenbrock,
              basic.happycat, basic.expanded_schaffers_f6)
_F29_FUNCS = (hybrid.f15, hybrid.f16, hybrid.f17)
_F30_FUNCS = (hybrid.f15, hybrid.f18, hybrid.f19)


def f21(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F21: CF1 — rosenbrock(δ=10), elliptic(δ=20)*1e4/1e10, rastrigin(δ=30).
    Bias=2100."""
    return _eval_composition(
        x, 0,
        _F21_FUNCS,
        deltas=[10, 20, 30],
        biases=[0, 100, 200],
        lambdas=[1.0, 10000.0 / 1e10, 1.0],
        shift=shift, rotation=rotation,
    ) + 2100.0


def f22(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F22: CF2 — rastrigin(δ=10), griewank(δ=20)*1e3/100, schwefel(δ=30).
    Bias=2200."""
    return _eval_composition(
        x, 1,
        _F22_FUNCS,
        deltas=[10, 20, 30],
        biases=[0, 100, 200],
        lambdas=[1.0, 1000.0 / 100.0, 1.0],
        shift=shift, rotation=rotation,
    ) + 2200.0


def f23(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F23: CF3 — rosenbrock(δ=10), ackley(δ=20)*1e3/100, schwefel(δ=30), rastrigin(δ=40).
    Bias=2300."""
    return _eval_composition(
        x, 2,
        _F23_FUNCS,
        deltas=[10, 20, 30, 40],
        biases=[0, 100, 200, 300],
        lambdas=[1.0, 1000.0 / 100.0, 1.0, 1.0],
        shift=shift, rotation=rotation,
    ) + 2300.0


def f24(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F24: CF4 — ackley(δ=10)*1e3/100, elliptic(δ=20)*1e4/1e10,
    griewank(δ=30)*1e3/100, rastrigin(δ=40). Bias=2400."""
    return _eval_composition(
        x, 3,
        _F24_FUNCS,
        deltas=[10, 20, 30, 40],
        biases=[0, 100, 200, 300],
        lambdas=[1000.0 / 100.0, 10000.0 / 1e10, 1000.0 / 100.0, 1.0],
        shift=shift, rotation=rotation,
    ) + 2400.0


def f25(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F25: CF5 — rastrigin(δ=10)*1e4/1e3, happycat(δ=20)*1e3/1e3,
    ackley(δ=30)*1e3/100, discus(δ=40)*1e4/1e10, rosenbrock(δ=50).
    Bias=2500."""
    return _eval_composition(
        x, 4,
        _F25_FUNCS,
        deltas=[10, 20, 30, 40, 50],
        biases=[0, 100, 200, 300, 400],
        lambdas=[10000.0 / 1e3, 1000.0 / 1e3, 1000.0 / 100.0, 10000.0 / 1e10, 1.0],
        shift=shift, rotation=rotation,
    ) + 2500.0


def f26(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F26: CF6 — escaffer6(δ=10)*1e4/2e7, schwefel(δ=20), griewank(δ=20)*1e3/100,
    rosenbrock(δ=30), rastrigin(δ=40)*1e4/1e3.
    Bias=2600."""
    return _eval_composition(
        x, 5,
        _F26_FUNCS,
        deltas=[10, 20, 20, 30, 40],
        biases=[0, 100, 200, 300, 400],
        lambdas=[10000.0 / 2e7, 1.0, 1000.0 / 100.0, 1.0, 10000.0 / 1e3],
        shift=shift, rotation=rotation,
    ) + 2600.0


def f27(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F27: CF7 — hgbat(δ=10)*1e4/1e3, rastrigin(δ=20)*1e4/1e3,
    schwefel(δ=30)*1e4/4e3, bent_cigar(δ=40)*1e4/1e30,
    elliptic(δ=50)*1e4/1e10, escaffer6(δ=60)*1e4/2e7.
    Bias=2700."""
    return _eval_composition(
        x, 6,
        _F27_FUNCS,
        deltas=[10, 20, 30, 40, 50, 60],
        biases=[0, 100, 200, 300, 400, 500],
        lambdas=[10000.0 / 1000.0, 10000.0 / 1e3, 10000.0 / 4e3,
                 10000.0 / 1e30, 10000.0 / 1e10, 10000.0 / 2e7],
        shift=shift, rotation=rotation,
    ) + 2700.0


def f28(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
) -> np.ndarray:
    """F28: CF8 — ackley(δ=10)*1e3/100, griewank(δ=20)*1e3/100,
    discus(δ=30)*1e4/1e10, rosenbrock(δ=40), happycat(δ=50)*1e3/1e3,
    escaffer6(δ=60)*1e4/2e7.
    Bias=2800."""
    return _eval_composition(
        x, 7,
        _F28_FUNCS,
        deltas=[10, 20, 30, 40, 50, 60],
        biases=[0, 100, 200, 300, 400, 500],
        lambdas=[1000.0 / 100.0, 1000.0 / 100.0, 10000.0 / 1e10,
                 1.0, 1000.0 / 1e3, 10000.0 / 2e7],
        shift=shift, rotation=rotation,
    ) + 2800.0


def _eval_comp_hybrid(
    x: np.ndarray, comp_idx: int, hybrid_funcs: list[Callable[..., np.ndarray]],
    deltas: list[float], biases: list[float], hybrid_biases: list[float],
    shift: np.ndarray | None = None, rotation: np.ndarray | None = None,
    shuffle: np.ndarray | None = None,
) -> np.ndarray:
    """Evaluate composition of hybrids.

    Parameters
    ----------
    hybrid_funcs : list of (hybrid_func, bias_to_subtract) — hybrids subtract their own bias
    hybrid_biases : list of biases from the hybrid functions to subtract
    shift : optional override for component shifts
    rotation : optional override for component rotations
    shuffle : optional override for component shuffles
    """
    M, N = x.shape
    K = len(hybrid_funcs)

    # Defensive length check -- the four parallel lists must agree on K so
    # the per-component zip below cannot silently truncate or skip elements.
    if not (len(deltas) == K and len(biases) == K and len(hybrid_biases) == K):
        raise ValueError(
            f"_eval_comp_hybrid: list-length mismatch for comp_idx={comp_idx}: "
            f"len(hybrid_funcs)={K}, len(deltas)={len(deltas)}, "
            f"len(biases)={len(biases)}, len(hybrid_biases)={len(hybrid_biases)}"
        )

    all_shifts = shift if shift is not None else shifts_cf[comp_idx]
    all_rots = rotation if rotation is not None else rotations_cf[N][comp_idx]
    if shuffle is not None:
        all_shuffles_data = shuffle
    elif N in shuffles_cf and comp_idx in shuffles_cf[N]:
        all_shuffles_data = shuffles_cf[N][comp_idx]
    else:
        raise ValueError(
            f"No shuffle data for comp_idx={comp_idx}, D={N}. "
            f"Available dims: {sorted(shuffles_cf.keys())}"
        )

    # L5: cached deltas/biases arrays.  Lambdas are unused here so we pass an
    # empty list — the cache key is unique per ``comp_idx`` (8/9 for F29/F30
    # vs 0..7 for F21..F28) so there is no collision with ``_eval_composition``.
    deltas_arr, biases_arr, _ = _get_comp_meta(comp_idx, deltas, biases, [])

    fit = np.empty((K, M), dtype=np.float64)  # B9: empty — every row assigned in loop

    for i, (hfunc, hbias) in enumerate(zip(hybrid_funcs, hybrid_biases, strict=True)):
        s_i = all_shifts[i]
        R_i = all_rots[i]
        ss_i = all_shuffles_data[i]
        # Call hybrid with component-specific shift/rotation/shuffle
        # Subtract the hybrid's own bias since cf_cal adds composition bias
        fit[i] = hfunc(x, shift=s_i, rotation=R_i, shuffle=ss_i) - hbias

    # H2: contiguous shift slice for _cf_cal (same pattern as _eval_composition).
    if shift is not None:
        shifts_c = np.ascontiguousarray(shift[:, :N], dtype=np.float64)
    else:
        shifts_c = _get_cf_shifts_c(comp_idx, N)

    return _cf_cal(x, shifts_c, deltas_arr, biases_arr, fit)


def f29(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        shuffle: np.ndarray | None = None,
) -> np.ndarray:
    """F29: CF9 — composition of hf05(δ=10), hf06(δ=30), hf07(δ=50).
    Bias=2900."""
    return _eval_comp_hybrid(
        x, 8,
        _F29_FUNCS,
        deltas=[10, 30, 50],
        biases=[0, 100, 200],
        hybrid_biases=[1500.0, 1600.0, 1700.0],
        shift=shift, rotation=rotation, shuffle=shuffle,
    ) + 2900.0


def f30(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        shuffle: np.ndarray | None = None,
) -> np.ndarray:
    """F30: CF10 — composition of hf05(δ=10), hf08(δ=30), hf09(δ=50).
    Bias=3000."""
    return _eval_comp_hybrid(
        x, 9,
        _F30_FUNCS,
        deltas=[10, 30, 50],
        biases=[0, 100, 200],
        hybrid_biases=[1500.0, 1800.0, 1900.0],
        shift=shift, rotation=rotation, shuffle=shuffle,
    ) + 3000.0
