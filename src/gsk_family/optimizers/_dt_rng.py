"""Substream RNG layer for the migrated DT-GSK optimizer.

DT-GSK is reproducible only because it draws from a fixed set of **named,
independent substreams** (``init, core, ace, kexp, div, bse, arch, link, de,
control, flow, basin, trust``) derived from one run seed. Toggling any subsystem
must not perturb another subsystem's draws, which a single shared stream cannot
guarantee. This module vendors that substream-isolation layer from the source
DT-GSK project so the migrated optimizer reproduces the source trajectory
bit-for-bit.

The underlying Threefry-4x64-20 / MT19937 / mcg16807 generators are **reused from
the target's** :mod:`gsk_family.common.threefry_rng` and
:mod:`gsk_family.common.reference_rng` modules, which are byte-identical to the
source generators (same counter seeding ``((s+1)<<32)|s``, same ``(w>>11)*2**-53``
conversion, same column-major matrix fill). Only the named-substream layer
(:class:`RNGStreams`, :func:`_child_seed`) and the NumPy-``Generator``-like
:class:`ReferenceRNG` wrapper are vendored here.

This layer is deliberately kept under ``optimizers/`` and **does not** touch the
single-stream :class:`gsk_family.common.rng.RandomContext` used by the other
optimizers, so it cannot change their results.

Append-only contract: :data:`SUBSTREAM_NAMES` order is load-bearing because each
substream's child seed is assigned by position. The first nine names are
prefix-locked; new substreams may only be appended at the end.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

import numpy as np

from gsk_family.common.reference_rng import (
    DoublesStreamGenerator,
    Mcg16807Generator,
    TwisterGenerator,
)
from gsk_family.common.threefry_rng import ThreefryGenerator

MAX_SAFE_SEED: int = 2_147_483_646

_GENERATOR_ALIASES: dict[str, str] = {
    "threefry": "threefry",
    "twister": "twister",
    "seed": "mcg16807",
}


def normalize_generator_name(generator: str | None) -> str:
    """Return the canonical requested RNG label (DT-GSK default ``threefry``).

    Empty values resolve to ``"threefry"`` (matching the source DT-GSK default,
    which differs from ``common.rng``'s ``twister`` default). Unknown labels
    raise so runs cannot silently fall back to NumPy's default stream.
    """
    if generator is None or str(generator).strip() == "":
        return "threefry"
    requested = str(generator).strip().lower()
    if requested not in _GENERATOR_ALIASES:
        raise ValueError(
            f"Unsupported RNG generator {generator!r}; expected one of "
            f"{', '.join(sorted(_GENERATOR_ALIASES))}."
        )
    return requested


def effective_python_generator(generator: str | None) -> str:
    """Return the implementation name behind a public RNG label."""
    return _GENERATOR_ALIASES[normalize_generator_name(generator)]


class ReferenceRNG:
    """NumPy-``Generator``-like wrapper around a reference-compatible stream.

    Wraps one of the target's reference generators and exposes the draw surface
    DT-GSK relies on (``random`` with an ``out=`` C-order path, ``integers``
    with ``endpoint``, ``permutation``, ``choice``). Matrix draws follow the
    reference column-major convention.
    """

    # Matrix draws intentionally follow the reference column-major convention.
    uses_reference_matrix_order: bool = True

    def __init__(self, seed: int, generator: str | None = "threefry") -> None:
        """Build a single reference-compatible stream from ``seed``."""
        self.seed = int(seed)
        if self.seed < 0:
            raise ValueError(f"Seed must be non-negative, got {seed}.")
        self.requested_generator = normalize_generator_name(generator)
        effective = effective_python_generator(self.requested_generator)
        self.effective_generator = effective
        if effective == "threefry":
            self._rng: DoublesStreamGenerator = ThreefryGenerator(self.seed)
        elif effective == "twister":
            self._rng = TwisterGenerator(self.seed)
        else:
            self._rng = Mcg16807Generator(self.seed)

    def random(
        self,
        size: int | tuple[int, ...] | None = None,
        dtype: Any = np.float64,
        out: np.ndarray | None = None,
    ) -> np.ndarray | float:
        """Draw uniform doubles.

        ``out`` is provided for API compatibility with ``np.random.Generator``;
        it is filled in C order because NumPy's ``out`` contract is
        memory-order oriented, while regular shaped draws keep the reference
        column-major rule.
        """
        if out is not None:
            arr = np.asarray(out)
            arr.ravel(order="C")[:] = self._rng._draw(arr.size).astype(arr.dtype, copy=False)
            return out
        values = self._rng.random(size)
        if dtype is not None and dtype is not np.float64:
            return np.asarray(values, dtype=dtype)
        return values

    def integers(
        self,
        low: int,
        high: int | None = None,
        size: int | tuple[int, ...] | None = None,
        dtype: Any = np.int64,
        endpoint: bool = False,
    ) -> np.ndarray | int:
        """Reference-style integer draw ``lo + floor(span * rand)``."""
        if endpoint:
            if high is None:
                high = int(low)
                low = 0
            high = int(high) + 1
        values = self._rng.integers(int(low), None if high is None else int(high), size=size)
        if np.ndim(values) == 0:
            return int(values)
        return np.asarray(values, dtype=dtype)

    def permutation(self, n: int) -> np.ndarray:
        """Reference ``randperm`` equivalent: stable argsort of ``rand(n)``."""
        return self._rng.permutation(n)

    def choice(
        self,
        a: Any,
        size: int | tuple[int, ...] | None = None,
        replace: bool = True,
        p: Any = None,
    ) -> Any:
        """Uniform choice over ``range(a)`` or a 1-D array."""
        return self._rng.choice(a, size=size, replace=replace, p=p)

    def copy_state(self) -> dict[str, Any]:
        """Return a deep-copyable snapshot of this stream's state."""
        return {
            "seed": int(self.seed),
            "requested_generator": self.requested_generator,
            "effective_generator": self.effective_generator,
            "state": self._rng.copy_state(),
        }

    def restore_state(self, state: dict[str, Any]) -> None:
        """Restore a previously captured stream state."""
        snapshot = copy.deepcopy(state)
        self.requested_generator = str(
            snapshot.get("requested_generator", self.requested_generator)
        )
        self.effective_generator = str(
            snapshot.get("effective_generator", self.effective_generator)
        )
        self._rng.restore_state(snapshot["state"])


def _child_seed(seed: int, stream_index: int) -> int:
    """Return the deterministic child seed for a named DT-GSK substream.

    Stream 0 (``init``) gets the run seed verbatim; every other stream gets
    ``(seed + 1_000_003 * (index + 1)) % MAX_SAFE_SEED + 1``.
    """
    seed_i = int(seed)
    idx = int(stream_index)
    if idx == 0:
        return seed_i
    return (seed_i + 1_000_003 * (idx + 1)) % MAX_SAFE_SEED + 1


# Order matters: it defines the fixed substream contract for DT-GSK. Each
# substream's child seed is assigned by POSITION, so the order is load-bearing.
SUBSTREAM_NAMES: tuple[str, ...] = (
    "init",
    "core",
    "ace",
    "kexp",
    "div",
    "bse",
    "arch",
    "link",
    "de",
    "control",
    "flow",
    "basin",
    "trust",
)

_SUBSTREAM_PREFIX_LOCK: tuple[str, ...] = (
    "init", "core", "ace", "kexp", "div", "bse", "arch", "link", "de",
)
assert SUBSTREAM_NAMES[: len(_SUBSTREAM_PREFIX_LOCK)] == _SUBSTREAM_PREFIX_LOCK, (
    "SUBSTREAM_NAMES prefix must remain "
    f"{_SUBSTREAM_PREFIX_LOCK!r}; got {SUBSTREAM_NAMES!r}. "
    "New substreams may only be appended at the end."
)


@dataclass
class RNGStreams:
    """Independent reference-compatible substreams for DT-GSK."""

    init: ReferenceRNG
    core: ReferenceRNG
    ace: ReferenceRNG
    kexp: ReferenceRNG
    div: ReferenceRNG
    bse: ReferenceRNG
    arch: ReferenceRNG
    link: ReferenceRNG
    de: ReferenceRNG
    control: ReferenceRNG
    flow: ReferenceRNG
    basin: ReferenceRNG
    trust: ReferenceRNG

    @classmethod
    def from_seed(cls, seed: int, generator: str | None = "threefry") -> "RNGStreams":
        """Build all named substreams from one scheduled run seed."""
        gen = normalize_generator_name(generator)
        streams = [
            ReferenceRNG(_child_seed(int(seed), idx), gen)
            for idx, _name in enumerate(SUBSTREAM_NAMES)
        ]
        return cls(**dict(zip(SUBSTREAM_NAMES, streams, strict=True)))


def make_generator(seed: int, generator: str | None = "threefry") -> ReferenceRNG:
    """Build a single reference-compatible RNG stream."""
    return ReferenceRNG(int(seed), generator)


__all__ = [
    "MAX_SAFE_SEED",
    "SUBSTREAM_NAMES",
    "RNGStreams",
    "ReferenceRNG",
    "effective_python_generator",
    "make_generator",
    "normalize_generator_name",
]
