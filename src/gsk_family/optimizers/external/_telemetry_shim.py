"""No-op telemetry recorder for the vendored external baselines.

Project 05 threads a full ``TelemetryRecorder`` (GISR / diversity / per-generation
records) through these algorithms because its cross-optimizer analysis consumes
those series. This project does not: the GSK-family optimizers expose
per-generation state through ``generation_callback`` instead, and the LSGO
comparison needs only the per-run ``best_fitness``.

Rather than port a telemetry subsystem this project has no consumer for, the
vendored algorithms keep their instrumentation call sites intact and feed them
into this shim, which accepts every call and records nothing. That keeps the
vendored bodies byte-faithful to their frozen, parity-verified originals — the
alternative, deleting the call sites, would fork the code and void the
line-mapped review those verdicts rest on.

``finalize`` returns ``None``, and ``build_result`` drops it, because this
project's :class:`~gsk_family.types.OptimizerResult` has no ``telemetry`` field.

If per-generation telemetry is ever wanted for these baselines, replace this
module with a real recorder exposing the same three methods; no algorithm code
needs to change.
"""

from __future__ import annotations

from typing import Any


class TelemetryRecorder:
    """Accept the family telemetry protocol and discard it.

    Mirrors the constructor keywords ``_base.make_recorder`` supplies so the
    vendored call site needs no edit.
    """

    def __init__(
        self,
        max_nfes: int | None = None,
        lb: Any = None,
        ub: Any = None,
        counting_rule: str | None = None,
        diversity_points: int = 0,
        **_ignored: Any,
    ) -> None:
        """Store nothing; the arguments are accepted for signature parity only."""
        self.max_nfes = max_nfes
        self.counting_rule = counting_rule
        self.diversity_points = diversity_points

    def record_initial(self, *_args: Any, **_kwargs: Any) -> None:
        """Discard the initial-population snapshot."""

    def record_generation(self, *_args: Any, **_kwargs: Any) -> None:
        """Discard a per-generation snapshot."""

    def finalize(self) -> None:
        """Return ``None`` -- this project's OptimizerResult carries no telemetry."""
        return None
