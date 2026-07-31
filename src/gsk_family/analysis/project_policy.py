"""Project-level optimizer and comparator policy for the analysis layer.

Dependency-free single source of truth for the GSK-family optimizer ids and the
reference-comparator panel consumed by the statistical-analysis modules.
Vendored and adapted from the source DT-GSK project; ``RUNNABLE_OPTIMIZERS``
reflects this project's seven locally executable optimizers.
"""

from __future__ import annotations

RUNNABLE_OPTIMIZERS: tuple[str, ...] = (
    "gsk",
    "agsk",
    "apgsk",
    "fdb-agsk",
    "atmals-gsk",
    "egsk",
    "dt-gsk",
)
"""Optimizers this repository can execute locally (egsk also stays a reference comparator)."""

PROPOSED_OPTIMIZER = "dt-gsk"
BASELINE_OPTIMIZER = "gsk"

REFERENCE_COMPARATORS: tuple[str, ...] = (
    "gsk",
    "agsk",
    "apgsk",
    "fdb-agsk",
    "egsk",
    "atmals-gsk",
)
"""GSK-family comparators available as committed reference statistics (egsk is now also runnable)."""

GSK_FAMILY_REFERENCE_COMPARATORS = REFERENCE_COMPARATORS

_NORMALIZATION_ALIASES: dict[str, str] = {
    "dt_gsk": "dt-gsk",
    "dtgsk": "dt-gsk",
    "fdbagsk": "fdb-agsk",
    "fdb_agsk": "fdb-agsk",
    "atmals_gsk": "atmals-gsk",
    "atmalsgsk": "atmals-gsk",
}


def normalize_algorithm_id(value: str) -> str:
    """Return a lowercase canonical algorithm/comparator identifier."""
    key = str(value).strip().lower()
    return _NORMALIZATION_ALIASES.get(key, key.replace("_", "-"))


def is_runnable_optimizer(value: str) -> bool:
    """Return True when *value* names a locally executable optimizer."""
    return normalize_algorithm_id(value) in RUNNABLE_OPTIMIZERS


def require_runnable_optimizer(value: str) -> str:
    """Normalize *value* or raise ValueError if it is reference-only."""
    alg = normalize_algorithm_id(value)
    if alg not in RUNNABLE_OPTIMIZERS:
        allowed = ", ".join(RUNNABLE_OPTIMIZERS)
        raise ValueError(f"Unsupported runnable optimizer {value!r}; choose: {allowed}")
    return alg


def is_reference_comparator(value: str) -> bool:
    """Return True when *value* is in the GSK-family reference panel."""
    return normalize_algorithm_id(value) in REFERENCE_COMPARATORS
