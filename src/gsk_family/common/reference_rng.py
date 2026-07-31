"""Reference-matching ``twister`` (MT19937) and ``seed`` (mcg16807) generators.

These reproduce the external reference's non-threefry global generators so the
Python port can also reproduce reference data produced with them (the
``reference`` seed policy uses ``twister`` for the linear GSK variant and
``seed`` for the adaptive/product variants).

* ``twister`` -> MT19937 (mt19937ar) seeded with ``init_genrand(seed)`` and
  emitting doubles via ``genrand_res53`` (two 32-bit words per double); this is
  the generator selected by ``rng(seed, 'twister')``.
* ``seed`` -> the legacy v4 multiplicative congruential generator mcg16807
  (Park-Miller minimal standard, ``x <- 16807 * x mod (2^31 - 1)``), selected by
  ``RandStream('mcg16807', 'Seed', seed)``.

Matrix draws fill **column-major** to match ``rand(m, n)``; ``randi`` and
``randperm`` reuse the shared ``floor(imax*rand)+1`` / ``sort(rand(n))`` rules so
every generator exposes the same integer/permutation semantics as the reference.

Shared scalar/vector helpers live in :class:`DoublesStreamGenerator`; the twister,
seed, and threefry generators all subclass it and only supply the underlying
``_draw`` and their state snapshot.
"""

from __future__ import annotations

import copy
from typing import Any

import numpy as np

try:  # numba is a hard dependency, but keep a pure-NumPy fallback.
    from numba import njit

    _HAVE_NUMBA = True
except Exception:  # pragma: no cover - exercised only when numba is unavailable.
    _HAVE_NUMBA = False


class DoublesStreamGenerator:
    """Shared ``random``/``integers``/``permutation`` over a ``_draw`` stream."""

    def _draw(self, count: int) -> np.ndarray:
        """Return ``count`` consecutive uniform ``[0, 1)`` doubles."""
        raise NotImplementedError

    def random(self, size: int | tuple[int, ...] | None = None) -> np.ndarray | float:
        """Draw uniform ``[0, 1)`` values, column-major for matrix shapes."""
        if size is None:
            # Scalar fast path when the generator provides one (P3-RNG): avoids
            # the np.empty(1) allocation and array round trip of _draw(1)[0].
            # Same stream, same position -- see ThreefryGenerator.random_scalar.
            fast = getattr(self, "random_scalar", None)
            if fast is not None:
                return fast()
            return float(self._draw(1)[0])
        if isinstance(size, (int, np.integer)):
            return self._draw(int(size))
        shape = tuple(int(s) for s in size)
        count = 1
        for axis in shape:
            count *= axis
        flat = self._draw(count)
        if len(shape) <= 1:
            return flat.reshape(shape)
        return flat.reshape((*shape[:-2], shape[-1], shape[-2])).swapaxes(-1, -2)

    def integers(
        self,
        low: int,
        high: int | None = None,
        size: int | tuple[int, ...] | None = None,
    ) -> np.ndarray | int:
        """Reference-exact ``randi``: ``lo + floor(span * rand)`` per draw."""
        if high is None:
            lo, hi = 0, int(low)
        else:
            lo, hi = int(low), int(high)
        span = hi - lo
        if span <= 0:
            raise ValueError(f"integers requires high > low, got low={lo}, high={hi}.")
        draw = self.random(size)
        values = lo + np.floor(np.asarray(draw, dtype=np.float64) * span).astype(np.int64)
        values = np.clip(values, lo, hi - 1)
        if np.ndim(values) == 0:
            return int(values)
        return values

    def permutation(self, n: int) -> np.ndarray:
        """Reference-exact ``randperm``: ``argsort(rand(n))`` (0-based, n doubles)."""
        n_int = int(n)
        if n_int < 0:
            raise ValueError(f"Permutation length must be >= 0, got {n}.")
        if n_int == 0:
            return np.empty(0, dtype=np.int64)
        keys = np.asarray(self._draw(n_int), dtype=np.float64)
        return np.argsort(keys, kind="stable").astype(np.int64)

    def choice(
        self,
        a: Any,
        size: int | tuple[int, ...] | None = None,
        replace: bool = True,
        p: Any = None,
    ) -> Any:
        """Stream-deterministic choice over ``range(a)`` or a 1-D array."""
        if p is not None or not replace:
            raise NotImplementedError(
                "choice supports only replace=True with uniform weights."
            )
        population = np.arange(int(a)) if np.ndim(a) == 0 else np.asarray(a)
        idx = self.integers(0, population.shape[0], size=size)
        return population[idx]


# --------------------------------------------------------------------------- #
# MT19937 ("twister")                                                          #
# --------------------------------------------------------------------------- #

_MT_N = 624
_MT_M = 397


def _mt_init(seed: int) -> np.ndarray:
    """Seed the MT19937 state with the reference ``init_genrand`` recurrence."""
    mt: np.ndarray = np.empty(_MT_N, dtype=np.uint64)
    mt[0] = np.uint64(seed & 0xFFFFFFFF)
    for i in range(1, _MT_N):
        prev = int(mt[i - 1])
        mt[i] = np.uint64((1812433253 * (prev ^ (prev >> 30)) + i) & 0xFFFFFFFF)
    return mt


def _mt_fill_u32(mt: np.ndarray, mti: int, out: np.ndarray) -> int:
    """Fill ``out`` with tempered 32-bit words; twist as needed; return new mti."""
    matrix_a = np.uint64(0x9908B0DF)
    upper = np.uint64(0x80000000)
    lower = np.uint64(0x7FFFFFFF)
    mask = np.uint64(0xFFFFFFFF)
    one = np.uint64(1)
    zero = np.uint64(0)
    n = out.shape[0]
    for k in range(n):
        if mti >= _MT_N:
            for kk in range(_MT_N - _MT_M):
                y = (mt[kk] & upper) | (mt[kk + 1] & lower)
                mt[kk] = mt[kk + _MT_M] ^ (y >> one) ^ (matrix_a if (y & one) else zero)
            for kk in range(_MT_N - _MT_M, _MT_N - 1):
                y = (mt[kk] & upper) | (mt[kk + 1] & lower)
                mt[kk] = mt[kk + (_MT_M - _MT_N)] ^ (y >> one) ^ (matrix_a if (y & one) else zero)
            y = (mt[_MT_N - 1] & upper) | (mt[0] & lower)
            mt[_MT_N - 1] = mt[_MT_M - 1] ^ (y >> one) ^ (matrix_a if (y & one) else zero)
            mti = 0
        y = mt[mti]
        mti += 1
        y ^= y >> np.uint64(11)
        y ^= (y << np.uint64(7)) & np.uint64(0x9D2C5680)
        y ^= (y << np.uint64(15)) & np.uint64(0xEFC60000)
        y ^= y >> np.uint64(18)
        out[k] = y & mask
    return mti


if _HAVE_NUMBA:
    _mt_fill_u32 = njit(cache=True)(_mt_fill_u32)


class TwisterGenerator(DoublesStreamGenerator):
    """MT19937 reproducing the reference ``rng(seed, 'twister')`` stream."""

    def __init__(self, seed: int) -> None:
        """Seed MT19937 via the reference ``init_genrand`` recurrence."""
        self._mt = _mt_init(int(seed) & 0xFFFFFFFF)
        self._mti = _MT_N

    def _draw(self, count: int) -> np.ndarray:
        """Emit ``count`` doubles via ``genrand_res53`` (two words per double)."""
        if count <= 0:
            return np.empty(0, dtype=np.float64)
        words: np.ndarray = np.empty(2 * count, dtype=np.uint64)
        self._mti = int(_mt_fill_u32(self._mt, self._mti, words))
        high = (words[0::2] >> np.uint64(5)).astype(np.float64)
        low = (words[1::2] >> np.uint64(6)).astype(np.float64)
        return (high * 67108864.0 + low) * (1.0 / 9007199254740992.0)

    def copy_state(self) -> dict[str, Any]:
        """Return a deep-copyable MT19937 state snapshot."""
        return {"kind": "mt19937", "mt": [int(v) for v in self._mt], "mti": int(self._mti)}

    def restore_state(self, state: dict[str, Any]) -> None:
        """Restore a previously captured MT19937 state."""
        snapshot = copy.deepcopy(state)
        self._mt = np.asarray(snapshot["mt"], dtype=np.uint64)
        self._mti = int(snapshot["mti"])


# --------------------------------------------------------------------------- #
# mcg16807 ("seed", legacy v4)                                                 #
# --------------------------------------------------------------------------- #

_MCG_MODULUS = 2147483647  # 2**31 - 1
_MCG_MULTIPLIER = 16807
_MCG_SEED_MODULUS = 2147450880  # 2**31 - 2**15 (reference seeding fold: 2**31 == 2**15)


def _mcg_fill(state: int, out: np.ndarray) -> int:
    """Advance the Park-Miller stream into ``out`` (doubles); return new state."""
    modulus = _MCG_MODULUS
    multiplier = _MCG_MULTIPLIER
    scale = 1.0 / modulus
    x = state
    for k in range(out.shape[0]):
        x = (multiplier * x) % modulus
        out[k] = x * scale
    return x


if _HAVE_NUMBA:
    _mcg_fill = njit(cache=True)(_mcg_fill)


class Mcg16807Generator(DoublesStreamGenerator):
    """Legacy v4 mcg16807 (Park-Miller) generator for the ``seed`` label.

    Reverse-engineered from reference draws: the internal state is seeded as
    ``x0 = (seed << 16) mod (2**31 - 2**15)`` (the reference seeding folds the
    overflow with ``2**31 == 2**15``), then each draw advances
    ``x <- 16807 * x mod (2**31 - 1)`` and emits ``u = x / (2**31 - 1)``.
    """

    def __init__(self, seed: int) -> None:
        """Seed the multiplicative congruential state (``x0 = seed << 16``)."""
        x0 = (int(seed) << 16) % _MCG_SEED_MODULUS
        self._x = x0 if x0 != 0 else 1

    def _draw(self, count: int) -> np.ndarray:
        """Emit ``count`` doubles from the Park-Miller recurrence."""
        if count <= 0:
            return np.empty(0, dtype=np.float64)
        out: np.ndarray = np.empty(count, dtype=np.float64)
        self._x = int(_mcg_fill(self._x, out))
        return out

    def copy_state(self) -> dict[str, Any]:
        """Return a deep-copyable mcg16807 state snapshot."""
        return {"kind": "mcg16807", "x": int(self._x)}

    def restore_state(self, state: dict[str, Any]) -> None:
        """Restore a previously captured mcg16807 state."""
        self._x = int(copy.deepcopy(state)["x"])
