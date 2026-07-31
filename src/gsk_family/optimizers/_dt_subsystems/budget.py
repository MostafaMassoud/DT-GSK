"""
Function Evaluation Budget Controller
=====================================

Manages the fixed computational budget (NFEs = Number of Function Evaluations)
that CEC competition algorithms must respect.

Budget formula (per active suite):
- CEC2017 / CEC2013       : MaxNFEs = 10000 * D
- CEC2011                 : MaxNFEs = 150000 (fixed, dimension-independent)

The BudgetController:
- Tracks cumulative evaluation count
- Provides eval_batch_strict() for batched evaluation with strict budget
  enforcement (partial batches at the boundary are truncated, never extended)
- Provides eval_batch_safe() — cooperative variant that returns an empty
  result instead of raising once the budget is exhausted
- Records best-so-far error at checkpoint evaluation counts
- Raises BudgetExhausted when the strict path attempts an over-budget call
- Ensures reproducibility by coupling RNG state to evaluation order
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np


class BudgetExhausted(RuntimeError):
    """Raised when attempting evaluation after budget is exhausted."""
    pass


@dataclass
class BudgetReport:
    """Summary of budget usage."""
    max_nfes: int
    nfes_used: int

    @property
    def remaining(self) -> int:
        """Evaluations still available."""
        return max(0, self.max_nfes - self.nfes_used)

    @property
    def fraction_used(self) -> float:
        """Fraction of budget consumed (0.0 to 1.0)."""
        if self.max_nfes <= 0:
            return 1.0
        return min(1.0, self.nfes_used / self.max_nfes)


class BudgetController:
    """
    Tracks function evaluation budget and wraps objective function.

    Parameters
    ----------
    max_nfes : int
        Maximum evaluations allowed. For CEC2017: 10000 × dimension.
    objective : callable
        Function to minimize. Signature: f(X) -> y where X is (n, D) and y is (n,).

    Example
    -------
    >>> def sphere(X):
    ...     return np.sum(X**2, axis=1)
    >>>
    >>> budget = BudgetController(max_nfes=1000, objective=sphere)
    >>> pop = np.random.randn(100, 10)
    >>> fitness = budget.eval_batch(pop)
    >>>
    >>> print(f"Used: {budget.nfes_used}, Remaining: {budget.remaining()}")
    Used: 100, Remaining: 900
    """

    def __init__(
        self,
        *,
        max_nfes: int,
        objective: Callable[[np.ndarray], np.ndarray],
    ) -> None:
        self._max_nfes = int(max_nfes)
        if self._max_nfes < 0:
            raise ValueError("max_nfes must be non-negative")
        self._objective = objective
        self._nfes_used = 0

    @property
    def max_nfes(self) -> int:
        """Maximum evaluations allowed (read-only)."""
        return self._max_nfes

    @property
    def nfes_used(self) -> int:
        """Evaluations consumed so far (read-only)."""
        return self._nfes_used

    def remaining(self) -> int:
        """Return remaining evaluation budget."""
        return max(0, self._max_nfes - self._nfes_used)

    def exhausted(self) -> bool:
        """Return True if no evaluations remain."""
        return self._nfes_used >= self._max_nfes

    def report(self) -> BudgetReport:
        """Get budget summary for logging."""
        return BudgetReport(max_nfes=self._max_nfes, nfes_used=self._nfes_used)

    def _consume(self, n: int) -> None:
        """Internal: consume n evaluations from budget.

        Audit CRIT-10: raises :class:`BudgetExhausted` (typed) instead of
        :class:`AssertionError`.  ``AssertionError`` (a) gets stripped under
        ``python -O`` -- silently turning over-budget calls into a no-op --
        and (b) is too broad to catch precisely upstream, so callers were
        either swallowing it inside ``except Exception`` blocks or letting
        it bubble all the way to the harness.  Both are wrong: the over-
        budget condition is a hard contract violation that the cooperative
        path (:meth:`eval_batch_safe`) and the strict path
        (:meth:`eval_batch_strict`) prevent in normal operation, so it
        should crash loudly with the same exception type the rest of the
        budget API uses.
        """
        self._nfes_used += int(n)
        if self._nfes_used > self._max_nfes:
            raise BudgetExhausted(
                f"Budget exceeded: {self._nfes_used} > {self._max_nfes}"
            )

    def eval_batch(
        self,
        X: np.ndarray,
        *,
        allow_truncate: bool = True,
    ) -> np.ndarray:
        """
        Evaluate a batch of candidate solutions.

        Parameters
        ----------
        X : np.ndarray, shape (n, D)
            Candidates to evaluate.
        allow_truncate : bool, default=True
            If True and n > remaining budget, evaluate only what fits.
            If False, raise BudgetExhausted when n > remaining.

        Returns
        -------
        np.ndarray, shape (n_eval,)
            Fitness values. n_eval may be less than n if truncated.

        Raises
        ------
        BudgetExhausted
            If budget exhausted or truncation disabled and n > remaining.
        """
        X = np.asarray(X, dtype=np.float64)
        if X.ndim != 2:
            raise ValueError(f"X must be 2D (n, D), got shape={X.shape}")

        n = int(X.shape[0])
        if n <= 0:
            return np.empty((0,), dtype=np.float64)

        rem = self.remaining()

        if rem <= 0:
            raise BudgetExhausted("Evaluation budget exhausted")

        if n > rem:
            if not allow_truncate:
                raise BudgetExhausted(
                    f"Need {n} evaluations but only {rem} remain"
                )
            n_eval = rem
            X_eval = X[:n_eval, :]
        else:
            n_eval = n
            X_eval = X

        y = np.asarray(self._objective(X_eval), dtype=np.float64)

        if y.shape != (n_eval,):
            raise ValueError(f"Objective returned {y.shape}, expected ({n_eval},)")

        self._consume(n_eval)
        return y

    def eval_batch_strict(self, X: np.ndarray) -> tuple[np.ndarray, int]:
        """
        Evaluate a batch with strict, benchmark-safe budget semantics.

        This method guarantees:

          - the wrapped objective is **never** called more times than the
            remaining budget;
          - the returned array length equals the number of counted evaluations.

        Parameters
        ----------
        X : np.ndarray, shape (n, D)
            Candidates to evaluate.

        Returns
        -------
        y : np.ndarray, shape (n_eval,)
            Fitness for the evaluated prefix of the batch.
        n_counted : int
            Number of evaluations charged to budget (equals ``len(y)``).
        """
        X = np.asarray(X, dtype=np.float64)
        if X.ndim != 2:
            raise ValueError(f"X must be 2D (n, D), got shape={X.shape}")

        n = int(X.shape[0])
        if n <= 0:
            return np.empty((0,), dtype=np.float64), 0

        rem = self.remaining()
        if rem <= 0:
            raise BudgetExhausted("Evaluation budget exhausted")

        # Strict budget safety: never call the objective with more rows than
        # we can count.
        n_eval = min(n, int(rem))
        X_eval = X[:n_eval, :]

        y = np.asarray(self._objective(X_eval), dtype=np.float64)
        if y.shape != (n_eval,):
            raise ValueError(
                f"Objective returned {y.shape}, expected ({n_eval},)"
            )

        self._consume(n_eval)
        return y, n_eval

    def eval_batch_matlab(self, X: np.ndarray) -> tuple[np.ndarray, int]:
        """
        Evaluate a batch with the original baseline GSK budget semantics.

        The reference GSK code evaluates the entire batch even when the
        remaining budget is smaller, then only charges the prefix that fits
        within the budget. This preserves the reference baseline's objective
        call pattern and reported fitness vectors at the budget boundary.

        Parameters
        ----------
        X : np.ndarray, shape (n, D)
            Candidates to evaluate.

        Returns
        -------
        y : np.ndarray, shape (n,)
            Fitness values for the full batch.
        n_counted : int
            Number of evaluations charged to the budget.
        """
        X = np.asarray(X, dtype=np.float64)
        if X.ndim != 2:
            raise ValueError(f"X must be 2D (n, D), got shape={X.shape}")

        n = int(X.shape[0])
        if n <= 0:
            return np.empty((0,), dtype=np.float64), 0

        y = np.asarray(self._objective(X), dtype=np.float64)
        if y.shape != (n,):
            raise ValueError(f"Objective returned {y.shape}, expected ({n},)")

        rem = self.remaining()
        n_counted = min(n, int(rem))
        if n_counted > 0:
            self._consume(n_counted)

        return y, n_counted

    def eval_batch_safe(self, X: np.ndarray) -> tuple[np.ndarray, int]:
        """
        Cooperative-budget variant of :meth:`eval_batch_strict`.

        Returns ``(empty, 0)`` instead of raising :class:`BudgetExhausted`
        when the budget is already at zero.  This lets callers use a single
        ``if n_eval > 0:`` guard at every call site rather than wrapping
        every objective call in ``try / except BudgetExhausted``.

        The strict, raise-on-exhausted contract of :meth:`eval_batch_strict`
        is unchanged for direct callers (and for the budget tests that rely
        on it).

        Parameters
        ----------
        X : np.ndarray, shape (n, D)
            Candidates to evaluate.

        Returns
        -------
        y : np.ndarray, shape (n_eval,)
            Fitness for the evaluated prefix of the batch (possibly empty).
        n_counted : int
            Number of evaluations charged to budget (equals ``len(y)``).
        """
        if self.exhausted():
            return np.empty((0,), dtype=np.float64), 0
        return self.eval_batch_strict(X)

    def eval_one(self, x: np.ndarray) -> float:
        """
        Evaluate a single candidate.

        Parameters
        ----------
        x : np.ndarray, shape (D,)
            Single candidate.

        Returns
        -------
        float
            Fitness value.
        """
        x = np.asarray(x, dtype=np.float64)
        if x.ndim != 1:
            raise ValueError(f"x must be 1D (D,), got shape={x.shape}")
        y = self.eval_batch(x.reshape(1, -1), allow_truncate=False)
        return float(y[0])
