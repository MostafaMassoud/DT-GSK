"""Basin descriptor memory for TERRA-GSK novelty-aware restarts."""
from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np


@dataclass(slots=True)
class BasinDescriptor:
    center: np.ndarray
    fitness: float
    radius: float
    visits: int = 1
    failures: int = 0


@dataclass(slots=True)
class BasinMemory:
    """Small deterministic archive of basin descriptors, not DE donors."""

    max_size: int = 64
    min_distance: float = 0.05
    descriptors: list[BasinDescriptor] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.descriptors)

    def add(self, x: np.ndarray, fitness: float, span: np.ndarray, *, improved: bool = True) -> None:
        if self.max_size <= 0:
            return
        x = np.asarray(x, dtype=np.float64).copy()
        span = np.maximum(np.asarray(span, dtype=np.float64), 1e-30)
        if not self.descriptors:
            self.descriptors.append(BasinDescriptor(x, float(fitness), radius=max(float(self.min_distance), 1e-12), failures=0 if improved else 1))
            return
        centers = np.asarray([b.center for b in self.descriptors], dtype=np.float64)
        d = np.linalg.norm((centers - x[np.newaxis, :]) / span[np.newaxis, :], axis=1) / max(1.0, np.sqrt(float(x.size)))
        j = int(np.argmin(d))
        if float(d[j]) <= float(self.min_distance):
            b = self.descriptors[j]
            b.visits += 1
            if float(fitness) < float(b.fitness):
                b.center = x
                b.fitness = float(fitness)
            if not improved:
                b.failures += 1
            b.radius = max(float(b.radius), float(d[j]))
            return
        self.descriptors.append(BasinDescriptor(x, float(fitness), radius=max(float(self.min_distance), float(d[j])), failures=0 if improved else 1))
        if len(self.descriptors) > int(self.max_size):
            # Keep lower-fitness and less-failed basins; stable sort preserves determinism.
            order = sorted(range(len(self.descriptors)), key=lambda k: (self.descriptors[k].failures, self.descriptors[k].fitness, k))
            self.descriptors = [self.descriptors[k] for k in order[: int(self.max_size)]]

    def novelty_scores(
        self,
        X: np.ndarray,
        span: np.ndarray,
        *,
        failure_weight: float = 0.05,
    ) -> np.ndarray:
        """Score the candidate rows in ``X`` by basin novelty.

        ``failure_weight`` is the weight applied to the per-descriptor
        ``failures`` count.  The BMNP wiring sets this to a
        PTR-coupled value (0.05 in the routine phases, 0.15 in the
        escape phase) so the anti-restart-trap pressure is strongest
        when BSE is most likely to re-seed into a known failure basin.

        ``failure_weight = 0.05`` reproduces the original hand-tuned
        novelty score exactly -- this is the byte-stability default.
        """
        X = np.asarray(X, dtype=np.float64)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        if not self.descriptors:
            return np.ones((X.shape[0],), dtype=np.float64)
        span = np.maximum(np.asarray(span, dtype=np.float64), 1e-30)
        centers = np.asarray([b.center for b in self.descriptors], dtype=np.float64)
        fail = np.asarray([b.failures for b in self.descriptors], dtype=np.float64)
        scores = np.empty((X.shape[0],), dtype=np.float64)
        norm = max(1.0, np.sqrt(float(X.shape[1])))
        fw = float(failure_weight)
        for i, x in enumerate(X):
            d = np.linalg.norm((centers - x[np.newaxis, :]) / span[np.newaxis, :], axis=1) / norm
            # Distance from known basin plus a tunable penalty for failed basins.
            scores[i] = float(np.min(d + fw * fail))
        return scores

    def choose_novel(
        self,
        candidates: np.ndarray,
        span: np.ndarray,
        k: int,
        *,
        failure_weight: float = 0.05,
    ) -> np.ndarray:
        scores = self.novelty_scores(candidates, span, failure_weight=failure_weight)
        order = np.argsort(-scores, kind="stable")
        return order[: max(0, min(int(k), int(candidates.shape[0])))]


__all__ = ["BasinDescriptor", "BasinMemory"]
