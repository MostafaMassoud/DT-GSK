"""CEC2017 hybrid functions F11–F20.

Pipeline for each hybrid:
  1. shift_rotate(x, shift[func_idx+10], rotation[func_idx+10]) → z
  2. shuffle:   z_s = z[:, shuffle_permutation]
  3. partition: split z_s into groups by proportions (ceil for all but last)
  4. evaluate:  each group feeds a different basic function (shrink baked in)
  5. sum+bias:  f(x) = Σ basic_func_i(part_i) + fid*100

Shift/rotation indices: F11 uses shift[10], rotation[10]; F20 uses shift[19], rotation[19].
Shuffle indices: F11 uses shuffles[N][0]; F20 uses shuffles[N][9].

Function composition (proportions):
  F11: zakharov(0.2)    + rosenbrock(0.4)  + rastrigin(0.4)
  F12: elliptic(0.3)    + schwefel(0.3)    + bent_cigar(0.4)
  F13: bent_cigar(0.3)  + rosenbrock(0.3)  + bi_rastrigin(0.4)
  F14: elliptic(0.2)    + ackley(0.2)      + schaffer_F7(0.2) + rastrigin(0.4)  [*quirk]
  F15: bent_cigar(0.2)  + hgbat(0.2)       + rastrigin(0.3)   + rosenbrock(0.3)
  F16: escaffer6(0.2)   + hgbat(0.2)       + rosenbrock(0.3)  + schwefel(0.3)
  F17: katsuura(0.1)    + ackley(0.2)      + grie_rosen(0.2)  + schwefel(0.2) + rastrigin(0.3)
  F18: elliptic(0.2)    + ackley(0.2)      + rastrigin(0.2)   + hgbat(0.2) + discus(0.2)
  F19: bent_cigar(0.2)  + rastrigin(0.2)   + grie_rosen(0.2)  + weierstrass(0.2) + escaffer6(0.2)
  F20: hgbat(0.1) + katsuura(0.1) + ackley(0.2) + rastrigin(0.2)
       + schwefel(0.2) + schaffer_F7(0.2)  [*quirk]

[*quirk] Schaffer F7 buffer bug (F14, F20):
  EMULATE_CPP_SCHAFFER_QUIRK controls whether schaffer_F7 reads from the FULL
  shuffled vector (C++ behavior, reads y[0..G_nx-1]) or from its assigned
  partition (mathematically correct). Default: True (emulate C++ bug).
  This flag is aligned with CEC2022's identical quirk.

Valid dimensions: F11-F19: {10, 30, 50, 100}; F20: {10, 20, 30, 50, 100}.
"""

from __future__ import annotations

import contextlib
import sys
import threading
import types
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Sequence

from . import basic
from .transforms import (
    _split_shuffle,
    hybrid_shuffle_groups,
    partition_by_groups,
    rotations,
    rotations_T,
    shift_rotate,
    shifts,
    shuffles,
)


# =============================================================================
# Audit CEC2017-M2: thread-local Schaffer F7 global-buffer-quirk flag.
# =============================================================================
#
# The flag used to be a mutable module-level global:
#
#     EMULATE_CPP_SCHAFFER_QUIRK: bool = True
#
# That was safe only under the current ``ProcessPoolExecutor(spawn)``
# harness, where each worker process has its own fresh import of
# ``cec2017.hybrid`` and nothing else ever touches the module.  The
# moment any caller lands a truly multi-threaded harness (e.g. a
# ``ThreadPoolExecutor`` of F14/F20 evaluations, or the shared-memory
# future shared-memory code paths, two threads could race on the
# mutable global and observe different values inside ``_hybrid_eval``
# — producing divergent F14/F20 fitnesses inside a single worker.
#
# This block moves the flag to a ``threading.local()`` slot and exposes
# it through:
#
# * a module-level ``EMULATE_CPP_SCHAFFER_QUIRK`` *property* (via the
#   ``_HybridModule`` class swap at the bottom of this block), which
#   preserves the backward-compatible attribute-access API used in
#   ``tests/test_cec2017.py::test_schaffer_quirk_flag``;
# * a ``schaffer_quirk(enabled)`` ``@contextmanager`` for new callers;
# * the existing ``set_schaffer_quirk(enabled)`` helper, which now
#   writes to the thread-local.
#
# Internal code in this file must read the flag via
# ``_schaffer_quirk_enabled()`` because ``LOAD_GLOBAL`` inside the
# module bypasses the class-level property (CPython looks up module
# globals in ``__dict__`` directly; it does **not** route through
# ``__getattribute__``).  External attribute access on the module
# object *does* route through the property.  The module-class swap is
# a documented Python pattern — see PEP 562 and the numpy/scipy
# module-level property examples.

_QUIRK_DEFAULT: bool = True
_quirk_tls = threading.local()


def _schaffer_quirk_enabled() -> bool:
    """Return the current per-thread Schaffer F7 quirk emulation flag."""
    return bool(getattr(_quirk_tls, "enabled", _QUIRK_DEFAULT))


def _schaffer_quirk_set(value: bool) -> None:
    """Write the per-thread Schaffer F7 quirk emulation flag."""
    _quirk_tls.enabled = bool(value)


@contextlib.contextmanager
def schaffer_quirk(enabled: bool) -> "Iterator[bool]":
    """Temporarily override the Schaffer F7 quirk flag on this thread.

    Preferred API for new callers.  Unlike ``set_schaffer_quirk``, this
    guarantees the previous value is restored even if the ``with`` body
    raises, and it only affects the calling thread.

    Parameters
    ----------
    enabled : bool
        ``True`` to emulate the compiled reference global-buffer bug (benchmark
        default), ``False`` for the mathematically correct behaviour.

    Yields
    ------
    bool
        The new value of the flag (= ``enabled``).

    Examples
    --------
    >>> with schaffer_quirk(False):
    ...     val = f14(x)   # mathematically-correct Schaffer path
    """
    if not isinstance(enabled, bool):
        raise TypeError(f"enabled must be bool, got {type(enabled).__name__}")
    prev = _schaffer_quirk_enabled()
    _schaffer_quirk_set(enabled)
    try:
        yield enabled
    finally:
        _schaffer_quirk_set(prev)


class _HybridModule(types.ModuleType):
    """Module subclass that routes ``EMULATE_CPP_SCHAFFER_QUIRK`` through
    the per-thread storage above.

    External callers (e.g. ``hybrid.EMULATE_CPP_SCHAFFER_QUIRK`` in
    ``tests/test_cec2017.py``) hit the descriptor; internal callers
    inside this file must use ``_schaffer_quirk_enabled()`` because
    module-level ``LOAD_GLOBAL`` bypasses the class ``__getattribute__``.
    """

    @property
    def EMULATE_CPP_SCHAFFER_QUIRK(self) -> bool:  # noqa: N802 (public API name)
        return _schaffer_quirk_enabled()

    @EMULATE_CPP_SCHAFFER_QUIRK.setter
    def EMULATE_CPP_SCHAFFER_QUIRK(self, value: bool) -> None:  # noqa: N802
        if not isinstance(value, bool):
            raise TypeError(
                "EMULATE_CPP_SCHAFFER_QUIRK must be bool, got "
                f"{type(value).__name__}"
            )
        _schaffer_quirk_set(value)


sys.modules[__name__].__class__ = _HybridModule
# End audit CEC2017-M2 block.
# =============================================================================


# Audit PERF-LOW-5: pre-bind the per-hybrid partition specs as
# module-level tuples (the cec2020 hybrid layer already does this -- see
# ``benchmarks/cec_suite_python/cec2020/hybrid.py:_F5_GP``/``_F6_GP``/``_F7_GP``).
# Each F11..F20 wrapper used to allocate a fresh ``[0.2, 0.4, 0.4]``-style
# Python list literal on every NFE, which the cached ``shuffle_and_partition``
# would then convert to ``tuple(proportions)`` to look up
# ``_partition_cache``.  Both the list allocation and the tuple
# conversion are pure constant work that can be hoisted to import time.
# Tuples are slightly preferred over lists here because the cache key is
# already ``tuple(proportions)`` and ``tuple(t)`` is an O(1) no-op when
# ``t`` is already a tuple, so the cache lookup short-circuits.
_F11_GP: tuple[float, ...] = (0.2, 0.4, 0.4)
_F12_GP: tuple[float, ...] = (0.3, 0.3, 0.4)
_F13_GP: tuple[float, ...] = (0.3, 0.3, 0.4)
_F14_GP: tuple[float, ...] = (0.2, 0.2, 0.2, 0.4)
_F15_GP: tuple[float, ...] = (0.2, 0.2, 0.3, 0.3)
_F16_GP: tuple[float, ...] = (0.2, 0.2, 0.3, 0.3)
_F17_GP: tuple[float, ...] = (0.1, 0.2, 0.2, 0.2, 0.3)
_F18_GP: tuple[float, ...] = (0.2, 0.2, 0.2, 0.2, 0.2)
_F19_GP: tuple[float, ...] = (0.2, 0.2, 0.2, 0.2, 0.2)
_F20_GP: tuple[float, ...] = (0.1, 0.1, 0.2, 0.2, 0.2, 0.2)


# Audit PERF-LOW-5: pre-bind the per-hybrid sub-function lists as
# module-level tuples too.  Each wrapper otherwise rebuilds the same
# ``[basic.zakharov, basic.rosenbrock, basic.rastrigin]`` literal on
# every NFE just to feed ``_hybrid_eval``, which then iterates with
# ``zip(parts, sub_funcs, strict=True)``.  ``zip`` accepts any iterable,
# so a tuple is a drop-in replacement that costs nothing per call.
_F11_FUNCS: tuple[Callable[..., np.ndarray], ...] = (
    basic.zakharov, basic.rosenbrock, basic.rastrigin,
)
_F12_FUNCS: tuple[Callable[..., np.ndarray], ...] = (
    basic.elliptic, basic.schwefel, basic.bent_cigar,
)
_F13_FUNCS: tuple[Callable[..., np.ndarray], ...] = (
    basic.bent_cigar, basic.rosenbrock, basic.bi_rastrigin,
)
_F14_FUNCS: tuple[Callable[..., np.ndarray], ...] = (
    basic.elliptic, basic.ackley, basic.schaffer_F7_inner, basic.rastrigin,
)
_F15_FUNCS: tuple[Callable[..., np.ndarray], ...] = (
    basic.bent_cigar, basic.hgbat, basic.rastrigin, basic.rosenbrock,
)
_F16_FUNCS: tuple[Callable[..., np.ndarray], ...] = (
    basic.expanded_schaffers_f6, basic.hgbat,
    basic.rosenbrock, basic.schwefel,
)
_F17_FUNCS: tuple[Callable[..., np.ndarray], ...] = (
    basic.katsuura, basic.ackley,
    basic.expanded_griewanks_plus_rosenbrock,
    basic.schwefel, basic.rastrigin,
)
_F18_FUNCS: tuple[Callable[..., np.ndarray], ...] = (
    basic.elliptic, basic.ackley, basic.rastrigin, basic.hgbat, basic.discus,
)
_F19_FUNCS: tuple[Callable[..., np.ndarray], ...] = (
    basic.bent_cigar, basic.rastrigin,
    basic.expanded_griewanks_plus_rosenbrock,
    basic.weierstrass, basic.expanded_schaffers_f6,
)
_F20_FUNCS: tuple[Callable[..., np.ndarray], ...] = (
    basic.hgbat, basic.katsuura, basic.ackley, basic.rastrigin,
    basic.schwefel, basic.schaffer_F7_inner,
)


def set_schaffer_quirk(enabled: bool) -> None:
    """Set the C++ Schaffer F7 buffer bug emulation flag on the current thread.

    Parameters
    ----------
    enabled : bool
        True = emulate C++ bug (default, for benchmark compatibility).
        False = mathematically correct behavior.

    Warning
    -------
    Changing this mid-experiment will alter benchmark values for any hybrid
    function that uses Schaffer F7 (F14, F20).  As of audit CEC2017-M2, the
    flag is per-thread, so a write from thread A will not affect thread B.
    Prefer the ``schaffer_quirk(...)`` context manager for new code — it
    restores the previous value on exit and is exception-safe.
    """
    import warnings
    if not isinstance(enabled, bool):
        raise TypeError(f"enabled must be bool, got {type(enabled).__name__}")
    _schaffer_quirk_set(enabled)
    warnings.warn(
        f"CEC2017 EMULATE_CPP_SCHAFFER_QUIRK set to {enabled}. "
        f"Benchmark values for Schaffer F7 hybrids will change.",
        stacklevel=2,
    )


def _get_defaults(
    func_idx: int, N: int,
    shift: np.ndarray | None = None,
    rotation: np.ndarray | None = None,
    shuffle: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None, np.ndarray]:
    """Load defaults for hybrid func_idx (0-based: 0=F11, ..., 9=F20)."""
    s = shift if shift is not None else shifts[func_idx + 10]  # F11=shift[10], etc.
    if rotation is not None:
        R = rotation
        R_T = None
    elif N in rotations and (func_idx + 10) in rotations[N]:
        R = rotations[N][func_idx + 10]
        R_T = rotations_T[N][func_idx + 10]
    else:
        raise ValueError(
            f"No rotation data for hybrid func_idx={func_idx}, D={N}. "
            f"Available dims: {sorted(rotations.keys())}"
        )
    if shuffle is not None:
        ss = shuffle
    elif N in shuffles and func_idx in shuffles[N]:
        ss = shuffles[N][func_idx]
    else:
        raise ValueError(
            f"No shuffle data for hybrid func_idx={func_idx}, D={N}. "
            f"Available dims: {sorted(shuffles.keys())}"
        )
    return s, R, R_T, ss


def _hybrid_eval(
    x: np.ndarray, func_idx: int,
    proportions: Sequence[float],
    sub_funcs: Sequence[Callable[..., np.ndarray]],
    shift: np.ndarray | None = None,
    rotation: np.ndarray | None = None,
    shuffle: np.ndarray | None = None,
    full_shuffled_for_schaffer: bool = False,
    strict_fp: bool = False,
) -> np.ndarray:
    """Generic hybrid evaluation.

    Parameters
    ----------
    x : (M, N)
    func_idx : 0-based hybrid index (0=F11, ..., 9=F20)
    proportions : sequence of partition proportions (tuple preferred -- see
        ``_F11_GP`` etc. -- so that the per-NFE cache lookup short-circuits)
    sub_funcs : sequence of callables from basic module
    shift, rotation, shuffle : optional overrides
    full_shuffled_for_schaffer : if True, pass full shuffled vector to schaffer_F7
    """
    N = x.shape[1]
    s, R, R_T, ss = _get_defaults(func_idx, N, shift, rotation, shuffle)

    # Step 1: shift + rotate (shrink=1.0, i.e. no extra scaling)
    z = shift_rotate(x, s, R, rotation_T=R_T, strict=strict_fp)

    # Step 2: shuffle + partition
    #
    # L4b: on the DEFAULT path (``shuffle is None``, i.e. ``ss`` is exactly
    # ``shuffles[N][func_idx]``) the split of the frozen permutation is a pure
    # function of ``(func_idx, N)``, so it is memoised under that key and the
    # ~1.0 us/NFE spent rebuilding ``_shuffle_groups_cache``'s array-derived
    # key (``.base`` walk + ``__array_interface__`` dict + ``tuple(props)``)
    # disappears.  Caller-supplied shuffles (the comp-hybrid rows passed by
    # ``composition.py``) keep the array-keyed cache.
    if shuffle is None:
        ss_arr = ss
        shuffle_groups, bounds = hybrid_shuffle_groups(func_idx, N, proportions, ss)
    else:
        ss_arr = np.asarray(ss)
        shuffle_groups, bounds = _split_shuffle(ss_arr, N, proportions)
    parts = partition_by_groups(z, ss_arr, shuffle_groups, bounds)

    # Step 3: evaluate each sub-function on its partition
    f = np.zeros(x.shape[0], dtype=np.float64)

    # Audit CEC2017-M2: read the quirk flag via the per-thread helper.
    # LOAD_GLOBAL cannot see the ``EMULATE_CPP_SCHAFFER_QUIRK`` property
    # defined on the ``_HybridModule`` class (module-level lookups go
    # straight through ``__dict__``), so we must call the helper by
    # name here.  External callers still see the attribute.
    quirk_on = _schaffer_quirk_enabled()

    for part, func in zip(parts, sub_funcs, strict=True):
        if (full_shuffled_for_schaffer and quirk_on
                and func is basic.schaffer_F7_inner):
            # C++ bug: schaffer reads from y[0..G_nx[i]-1] instead of partition.
            # H1: extract only the needed columns instead of building the full
            # (M, N) shuffled intermediate (``z[:, ss]``) up-front.
            f += basic.schaffer_F7_inner(z[:, ss[:part.shape[1]]])
        elif func is basic.bi_rastrigin:
            # bi_rastrigin in hybrid: apply_shift=False, but need shift for sign-flip.
            # NOTE: bi_rastrigin uses shift[:N] where N=part.shape[1] (partition size),
            # so only the first n_i shift elements drive the sign-flip.  This matches
            # the C++ which applies the sign-flip after partitioning.
            f += basic.bi_rastrigin(part, shift=s, rotation=None, apply_shift=False)
        elif strict_fp and func is basic.bent_cigar:
            f += basic.bent_cigar(part, strict=True)
        else:
            f += func(part)

    return f


def f11(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        shuffle: np.ndarray | None = None,
) -> np.ndarray:
    """F11: Hybrid 1 — zakharov(0.2), rosenbrock(0.4), rastrigin(0.4). Bias=1100."""
    return _hybrid_eval(x, 0, _F11_GP, _F11_FUNCS,
                        shift, rotation, shuffle) + 1100.0


def f12(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        shuffle: np.ndarray | None = None,
        *,
        strict_fp: bool = False,
) -> np.ndarray:
    """F12: Hybrid 2 — elliptic(0.3), schwefel(0.3), bent_cigar(0.4). Bias=1200."""
    return _hybrid_eval(x, 1, _F12_GP, _F12_FUNCS,
                        shift, rotation, shuffle, strict_fp=strict_fp) + 1200.0


def f13(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        shuffle: np.ndarray | None = None,
        *,
        strict_fp: bool = False,
) -> np.ndarray:
    """F13: Hybrid 3 — bent_cigar(0.3), rosenbrock(0.3), bi_rastrigin(0.4). Bias=1300."""
    return _hybrid_eval(x, 2, _F13_GP, _F13_FUNCS,
                        shift, rotation, shuffle, strict_fp=strict_fp) + 1300.0


def f14(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        shuffle: np.ndarray | None = None,
) -> np.ndarray:
    """F14: Hybrid 4 — elliptic(0.2), ackley(0.2), schaffer_F7(0.2), rastrigin(0.4).

    C++ Schaffer F7 buffer bug: reads full shuffled vector, not partition.
    Bias=1400.
    """
    return _hybrid_eval(x, 3, _F14_GP, _F14_FUNCS,
                        shift, rotation, shuffle,
                        full_shuffled_for_schaffer=True) + 1400.0


def f15(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        shuffle: np.ndarray | None = None,
) -> np.ndarray:
    """F15: Hybrid 5 — bent_cigar(0.2), hgbat(0.2), rastrigin(0.3), rosenbrock(0.3).
    Bias=1500."""
    return _hybrid_eval(x, 4, _F15_GP, _F15_FUNCS,
                        shift, rotation, shuffle) + 1500.0


def f16(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        shuffle: np.ndarray | None = None,
) -> np.ndarray:
    """F16: Hybrid 6 — escaffer6(0.2), hgbat(0.2), rosenbrock(0.3), schwefel(0.3).
    Bias=1600."""
    return _hybrid_eval(x, 5, _F16_GP, _F16_FUNCS,
                        shift, rotation, shuffle) + 1600.0


def f17(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        shuffle: np.ndarray | None = None,
) -> np.ndarray:
    """F17: Hybrid 7 — katsuura(0.1), ackley(0.2), grie_rosen(0.2), schwefel(0.2), rastrigin(0.3).
    Bias=1700."""
    return _hybrid_eval(x, 6, _F17_GP, _F17_FUNCS,
                        shift, rotation, shuffle) + 1700.0


def f18(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        shuffle: np.ndarray | None = None,
) -> np.ndarray:
    """F18: Hybrid 8 — elliptic(0.2), ackley(0.2), rastrigin(0.2), hgbat(0.2), discus(0.2).
    Bias=1800."""
    return _hybrid_eval(x, 7, _F18_GP, _F18_FUNCS,
                        shift, rotation, shuffle) + 1800.0


def f19(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        shuffle: np.ndarray | None = None,
) -> np.ndarray:
    """F19: Hybrid 9 — bent_cigar(0.2), rastrigin(0.2), grie_rosen(0.2),
    weierstrass(0.2), escaffer6(0.2). Bias=1900."""
    return _hybrid_eval(x, 8, _F19_GP, _F19_FUNCS,
                        shift, rotation, shuffle) + 1900.0


def f20(
        x: np.ndarray,
        shift: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        shuffle: np.ndarray | None = None,
) -> np.ndarray:
    """F20: Hybrid 10 — hgbat(0.1), katsuura(0.1), ackley(0.2),
    rastrigin(0.2), schwefel(0.2), schaffer_F7(0.2).

    C++ Schaffer F7 buffer bug: reads full shuffled vector, not partition.
    Bias=2000.
    """
    return _hybrid_eval(x, 9, _F20_GP, _F20_FUNCS,
                        shift, rotation, shuffle,
                        full_shuffled_for_schaffer=True) + 2000.0
