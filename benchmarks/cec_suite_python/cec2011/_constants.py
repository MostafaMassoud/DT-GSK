"""CEC2011 shared numerical constants.

Audit CRIT-07: a single source of truth for the infeasibility penalty
returned when a problem hits a non-finite intermediate value (singular
matrix, ODE failure, Lambert non-convergence, log-of-non-positive,
etc.).  Previously every problem file had its own ``return 1e30`` /
``return 1.0e30`` literal sprinkled in -- this caused (a) silent drift
when one site was updated and the others were not, and (b) a one-site
typo (``1e29``) that broke Friedman ranking until caught.
"""

from __future__ import annotations

#: Standard infeasibility penalty for CEC2011.  Matches the original
#: reference convention used by the CEC2011 organisers' tech report.
#:
#: Audit L-5 rationale: ``1e30`` is deliberately chosen to be
#:
#: 1. **Finite**, not ``np.inf`` or ``np.nan``.  Friedman ranks, mean /
#:    median aggregation, and Wilcoxon signed-rank all break as soon as
#:    a single run produces ``inf`` or ``nan`` (rank propagation, mean
#:    becomes NaN, Wilcoxon rejects the sample).  A finite "large"
#:    value ranks as "worst" without poisoning the statistic.
#: 2. **Far above any finite CEC2011 fitness** -- the largest feasible
#:    value across the 22 problems is ~1e7 (F9 Energy Brokerage worst
#:    case), so ``1e30`` is ~23 orders of magnitude above any real
#:    result.  That gap keeps infeasible evaluations strictly
#:    dominated in every comparison.
#: 3. **Well below the float64 overflow boundary** (~1.8e308).  A
#:    downstream penalised sum like ``1e30 * NP`` for NP=200 remains
#:    ~2e32, nowhere near ``inf``.  The original reference uses the same
#:    magnitude for the same reasons.
#:
#: **Do not change this value.**  If you think you need a larger
#: penalty (e.g. to force a harder rank collapse), the correct fix is
#: to fix the upstream feasibility check that let the NaN slip through,
#: not to increase the sentinel.
NAN_PENALTY: float = 1e30
