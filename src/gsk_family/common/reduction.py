"""Population reduction helpers."""

from __future__ import annotations

from typing import Any

import numpy as np

from gsk_family.common.numeric_compat import stable_argsort


def gsk_reduction_survivors(fitness: Any, num_remove: int) -> np.ndarray:
    """Return 0-based survivor row indices after worst-individual removal."""
    values = np.asarray(fitness, dtype=np.float64).reshape(-1)
    if values.size == 0:
        raise ValueError("fitness must contain at least one value.")
    if not np.all(np.isfinite(values)):
        raise ValueError("fitness contains non-finite values.")

    remove = int(num_remove)
    if remove < 0:
        raise ValueError(f"num_remove must be non-negative, got {num_remove}.")
    if remove > values.size:
        raise ValueError(
            f"num_remove cannot exceed population size {values.size}, got {remove}."
        )

    order = stable_argsort(values)
    survivors = np.sort(order[: values.size - remove], kind="stable")
    return survivors.astype(np.int64, copy=False)
