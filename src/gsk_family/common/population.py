"""Population initialization helpers."""

from __future__ import annotations

from typing import Any

import numpy as np

from gsk_family.common.numeric_compat import ensure_2d_population
from gsk_family.common.rng import RandomContext, init_population, restore_after_initialization


def _option_value(options: Any, name: str) -> Any:
    """Read an option from either a dictionary or object attribute."""
    if options is None:
        return None
    if isinstance(options, dict):
        return options.get(name)
    return getattr(options, name, None)


def _bound_size(bounds: Any) -> int | None:
    """Return vector bound length, or None for scalar bounds."""
    arr = np.asarray(bounds)
    if arr.ndim == 0:
        return None
    return int(arr.reshape(-1).size)


def infer_dimension(lb: Any, ub: Any, *, dim: int | None = None, population: Any = None) -> int:
    """Infer a problem dimension from bounds and optional population data."""
    if dim is not None:
        dim_int = int(dim)
        if dim_int <= 0:
            raise ValueError(f"Dimension must be positive, got {dim}.")
        return dim_int

    sizes = [size for size in (_bound_size(lb), _bound_size(ub)) if size is not None]
    if population is not None:
        pop = np.asarray(population)
        if pop.ndim == 2:
            sizes.append(int(pop.shape[1]))
    if not sizes:
        return 1
    first = sizes[0]
    if first <= 0:
        raise ValueError("Dimension must be positive.")
    if any(size != first for size in sizes):
        raise ValueError(f"Inconsistent dimensions inferred from inputs: {sizes}.")
    return first


def gsk_init_population(
    rng: RandomContext,
    np_size: int,
    lb: Any,
    ub: Any,
    *,
    dim: int | None = None,
) -> np.ndarray:
    """Port of ``gsk_init_population.m`` using one population-sized draw."""
    dim_int = infer_dimension(lb, ub, dim=dim)
    return init_population(rng, int(np_size), dim_int, lb, ub)


def gsk_initial_population_from_options(
    options: Any,
    rng: RandomContext,
    np_size: int,
    lb: Any,
    ub: Any,
    *,
    dim: int | None = None,
) -> np.ndarray:
    """Use runner-provided fair-start population or draw normally."""
    initial_population = _option_value(options, "initial_population")
    dim_int = infer_dimension(lb, ub, dim=dim, population=initial_population)
    np_int = int(np_size)
    if np_int <= 0:
        raise ValueError(f"Population size must be positive, got {np_size}.")

    if initial_population is None:
        return gsk_init_population(rng, np_int, lb, ub, dim=dim_int)

    pop = ensure_2d_population(initial_population, dim=dim_int)
    if pop.shape[0] < np_int:
        raise ValueError(
            "initial_population must have at least "
            f"{np_int} rows, got {pop.shape[0]}."
        )
    return pop[:np_int, :].copy()


def gsk_restore_rng_after_initialization(options: Any, rng: RandomContext) -> None:
    """Restore post-initialization RNG state when a fair-start X0 is supplied."""
    initial_population = _option_value(options, "initial_population")
    state = _option_value(options, "rng_state_after_initialization")
    if initial_population is not None and state is not None:
        restore_after_initialization(rng, state)
