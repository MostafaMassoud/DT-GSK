"""Random-number context and fair-start helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from gsk_family.common.numeric_compat import as_1d_bounds
from gsk_family.common.reference_rng import Mcg16807Generator, TwisterGenerator
from gsk_family.common.threefry_rng import ThreefryGenerator


@dataclass(frozen=True)
class RandomContextInfo:
    """Metadata for the requested and effective Python RNG."""

    seed: int
    requested_generator: str
    effective_generator: str


@dataclass(frozen=True)
class FairStart:
    """Runner-owned initial population and post-initialization RNG state."""

    initial_population: np.ndarray
    rng_state_after_initialization: dict[str, Any]
    rng_info: RandomContextInfo


# Reference-matching generators. Each label reproduces the corresponding reference
# stream bit-for-bit: threefry (default), twister (MT19937), seed (mcg16807).
_GENERATOR_ALIASES = {
    "threefry": "threefry",
    "twister": "twister",
    "seed": "mcg16807",
}


def normalize_generator_name(generator: str | None) -> str:
    """Normalize a requested generator label."""
    if generator is None or str(generator).strip() == "":
        return "twister"
    requested = str(generator).strip().lower()
    if requested not in _GENERATOR_ALIASES:
        raise ValueError(
            f"Unsupported RNG generator {generator!r}; expected one of "
            f"{', '.join(sorted(_GENERATOR_ALIASES))}."
        )
    return requested


def effective_python_generator(generator: str | None) -> str:
    """Return the effective generator name used for a requested label."""
    return _GENERATOR_ALIASES[normalize_generator_name(generator)]


class RandomContext:
    """Wrapper around the reference-matching generators with helper draws."""

    def __init__(self, seed: int, generator: str | None = "twister") -> None:
        """Create a deterministic random context from a reference-facing label."""
        self.seed = int(seed)
        if self.seed < 0:
            raise ValueError(f"Seed must be non-negative, got {seed}.")
        requested = normalize_generator_name(generator)
        effective = effective_python_generator(requested)
        self.info = RandomContextInfo(
            seed=self.seed,
            requested_generator=requested,
            effective_generator=effective,
        )
        self._rng: ThreefryGenerator | TwisterGenerator | Mcg16807Generator
        if effective == "threefry":
            self._rng = ThreefryGenerator(self.seed)
        elif effective == "twister":
            self._rng = TwisterGenerator(self.seed)
        else:  # mcg16807
            self._rng = Mcg16807Generator(self.seed)

    def random(self, size: int | tuple[int, ...] | None = None) -> np.ndarray | float:
        """Draw uniform random values in [0, 1)."""
        return self._rng.random(size)

    def peek_doubles(self, count: int) -> np.ndarray | None:
        """Expose the next ``count`` uniforms without consuming them (or None).

        Additive helper for the vendored external baselines (``optimizers/external``),
        whose ``NormalStream`` vectorizes a rejection loop while consuming exactly as
        many uniforms as the scalar path would, keeping results bit-identical.
        Returns ``None`` on generators without look-ahead so callers keep a scalar
        fallback.  No family optimizer calls this; behaviour of every existing draw
        path is unchanged.
        """
        peek = getattr(self._rng, "peek_doubles", None)
        return None if peek is None else peek(count)

    def skip_doubles(self, count: int) -> None:
        """Consume ``count`` uniforms previously exposed by :meth:`peek_doubles`."""
        self._rng.skip_doubles(count)

    def integers(
        self,
        low: int,
        high: int | None = None,
        size: int | tuple[int, ...] | None = None,
    ) -> np.ndarray | int:
        """Draw integers using NumPy's exclusive-high semantics."""
        values = self._rng.integers(low, high=high, size=size)
        if np.ndim(values) == 0:
            return int(values)
        return np.asarray(values)

    def randi(
        self,
        low: int,
        high: int | None = None,
        size: int | tuple[int, ...] | None = None,
    ) -> np.ndarray | int:
        """reference-style inclusive integer draw.

        ``randi(imax)`` is represented by ``randi(imax)`` here and returns
        values in ``1..imax``. ``randi(low, high)`` returns ``low..high``.
        """
        if high is None:
            actual_low = 1
            actual_high = int(low)
        else:
            actual_low = int(low)
            actual_high = int(high)
        if actual_high < actual_low:
            raise ValueError(f"randi high must be >= low, got {actual_low}, {actual_high}.")
        return self.integers(actual_low, actual_high + 1, size=size)

    def permutation(self, n: int) -> np.ndarray:
        """Return a 0-based permutation equivalent to reference source ``randperm(n)``."""
        n_int = int(n)
        if n_int < 0:
            raise ValueError(f"Permutation length must be >= 0, got {n}.")
        return self._rng.permutation(n_int)

    def choice(self, a: Any, size: int | tuple[int, ...] | None = None, replace: bool = True, p: Any = None) -> Any:
        """Proxy to the underlying generator's ``choice``."""
        return self._rng.choice(a, size=size, replace=replace, p=p)

    def copy_state(self) -> dict[str, Any]:
        """Return a deep copy of the generator state."""
        return self._rng.copy_state()

    def restore_state(self, state: dict[str, Any]) -> None:
        """Restore a previously copied generator state."""
        self._rng.restore_state(state)


def init_population(
    rng: RandomContext,
    np_size: int,
    dim: int,
    lb: Any,
    ub: Any,
) -> np.ndarray:
    """Draw one uniform initial population within bounds."""
    np_int = int(np_size)
    dim_int = int(dim)
    if np_int <= 0:
        raise ValueError(f"Population size must be positive, got {np_size}.")
    if dim_int <= 0:
        raise ValueError(f"Dimension must be positive, got {dim}.")
    lower = as_1d_bounds(lb, dim=dim_int, name="lb")
    upper = as_1d_bounds(ub, dim=dim_int, name="ub")
    if np.any(lower > upper):
        raise ValueError("Lower bounds exceed upper bounds.")
    u = rng.random((np_int, dim_int))
    return lower + u * (upper - lower)


def create_fair_start(
    seed: int,
    generator: str,
    np_size: int,
    dim: int,
    lb: Any,
    ub: Any,
) -> FairStart:
    """Create runner-supplied X0 and capture post-initialization RNG state."""
    rng = RandomContext(seed, generator)
    x0 = init_population(rng, np_size, dim, lb, ub)
    return FairStart(
        initial_population=x0,
        rng_state_after_initialization=rng.copy_state(),
        rng_info=rng.info,
    )


def restore_after_initialization(rng: RandomContext, state: dict[str, Any] | None) -> None:
    """Restore a runner-captured post-initialization RNG state when provided."""
    if state is not None:
        rng.restore_state(state)
