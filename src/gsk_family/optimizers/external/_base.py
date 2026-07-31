"""Shared substrate for the seven external baseline optimizers.

Every external baseline plugs into the project's optimizer contract through this
module. It provides, once, the three things all of them need and that the
master plan makes non-negotiable:

1. **Family-identical RNG ownership.** Randomness is drawn ONLY through the
   family's :class:`~gsk_family.common.rng.RandomContext` (the same
   threefry/twister generators, the same ``seed_policy`` seed, and the runner's
   "fair start" post-initialization RNG state). The Gaussian and Cauchy variates
   the DE/ES baselines need — which ``RandomContext`` does not expose natively —
   are synthesized *from the family's own uniform stream* here (inverse-CDF), so
   each baseline run is reproducible and replayable on the identical seed streams
   as the 24 family algorithms. The reference code's native RNG is never used for
   the campaign; it is consulted only for ``reference_parity`` cross-checks.

2. **Budget-exact evaluation accounting.** :class:`BudgetEvaluator` counts every
   single objective call (population batches AND single-point local-search
   probes), tracks the best-so-far, records a bounded convergence trace, and
   exposes ``remaining()`` so an algorithm truncates its final batch exactly —
   the family's own budget discipline.

3. **Family-schema results.** :func:`build_result` returns an
   :class:`~gsk_family.types.OptimizerResult` identical in shape to the
   family's, so the existing analysis/statistics compare family-vs-baseline with
   no special-casing.

Design invariant: this module and the baselines under it are additive. They read
the family contract but mutate nothing the family owns.
"""

# VENDORED from 05-Human-Inspired-Family_Python_v0.1
#   src/human_inspired_family/optimizers/external/_base.py
#   source sha256: 59be4f42456a39cd
# Re-synced 2026-07-26 after project 05 edited this file post-vendoring.
# 05's changes were: np.clip(u, lo, hi) -> np.maximum(u, lo) in the
# inverse-CDF normal path (the upper bound is unreachable -- verified over
# 2,000,000 threefry draws, max 0.9999997237, so the two forms are
# result-identical); a 'decc-g' fair-start population entry; and dropping an
# unused Callable import. ONLY the import namespace is rewritten here.
# ONE deliberate divergence: build_result drops the telemetry kwarg, because
# this project's OptimizerResult has no telemetry field -- see _telemetry_shim.
# Do not edit the body here -- amend at the source and re-vendor.

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np
from scipy.special import ndtri  # inverse standard-normal CDF (exact, 1 uniform -> 1 normal)

from gsk_family.common.rng import RandomContext, restore_after_initialization
from gsk_family.optimizers.external._telemetry_shim import TelemetryRecorder
from gsk_family.stats import compute_error
from gsk_family.types import ConvergenceTrace, OptimizerOptions, OptimizerResult

# ---------------------------------------------------------------------------
# Profiles (master plan §0.3): faithful paper reconstruction / reference-code
# parity / the common publication campaign (external conditions only).
# ---------------------------------------------------------------------------
Profile = Literal["paper_default", "reference_parity", "publication"]
DEFAULT_PROFILE: Profile = "publication"


def resolve_profile(options: OptimizerOptions) -> Profile:
    """Return the active profile from ``options.values`` (default ``publication``)."""
    value = _values(options).get("profile", DEFAULT_PROFILE)
    if value not in ("paper_default", "reference_parity", "publication"):
        raise ValueError(f"unknown external-optimizer profile: {value!r}")
    return value  # type: ignore[return-value]


def _values(options: OptimizerOptions | dict[str, Any]) -> dict[str, Any]:
    """Options ``values`` mapping, tolerating a bare dict (parity harness convenience)."""
    if isinstance(options, dict):
        return options
    return options.values or {}


def param(options: OptimizerOptions | dict[str, Any], name: str, default: Any) -> Any:
    """Read a per-algorithm parameter override from ``options.values`` (else default)."""
    return _values(options).get(name, default)


def fair_start_size(optimizer_id: str, dim: int) -> int | None:
    """Native initial-population size each external draws through the family fair start.

    Single source of truth: the runner draws exactly this many rows for the fair-start
    ``initial_population`` (so every optimizer — family and external — draws its native
    population from the *same* seeded ``RandomContext`` at stream position 0, sharing the
    identical leading uniforms), and each baseline consumes them as its initial state.
    These MUST match the size each baseline computes internally on the no-``initial_population``
    (smoke) path. Returns ``None`` for non-external ids (runner falls back to its default).
    """
    d = int(dim)
    sizes = {
        "cmaes": 1,                                                  # only the initial mean (X0[0])
        "lshade": int(round(18.0 * d)),                             # N_init = round(18·D)
        "jso": max(4, int(round(25.0 * np.log(d) * np.sqrt(d)))),   # N_init = round(25·ln D·√D), floored at N_min (D=1)
        "lshade-spacma": int(round(18.0 * d)),                     # NP = 18·D
        "shade-ils": 100,                                          # SHADE population
        "ebowithcmar": 18 * d + (4 + int(np.floor(3 * np.log(d)))),  # PS1 + PS2
        "mos-cec2013lsgo": 400,                                    # CEC2013-winner pop-total
        "decc-g": 100,                                             # paper Section 4.1 population
    }
    return sizes.get(optimizer_id)


# ---------------------------------------------------------------------------
# Family RNG ownership + variate synthesis on the family's uniform stream
# ---------------------------------------------------------------------------
def make_rng(options: OptimizerOptions) -> RandomContext:
    """Create the family RNG for this run and honor the runner's fair start.

    Uses ``options.seed`` + ``options.rand_generator`` (the ``seed_policy`` choice)
    and restores the post-initialization RNG state the runner captured, so the
    baseline consumes the identical seed stream the family would after a fair start.
    """
    rng = RandomContext(int(options.seed), options.rand_generator)
    restore_after_initialization(rng, options.rng_state_after_initialization)
    return rng


# Open-interval clamp bounds for the inverse-CDF (hoisted: these are constants,
# not per-call values — recomputing them was pure overhead on the >1M-call/run
# resample-heavy paths). Bit-identical to the previous inline np.nextafter calls.
_U_LO = float(np.nextafter(0.0, 1.0))  # smallest double strictly > 0
_U_HI = float(np.nextafter(1.0, 0.0))  # largest double strictly < 1


def standard_normal(rng: RandomContext, size: int | tuple[int, ...] | None = None) -> np.ndarray | float:
    """Draw N(0, 1) from the family's uniform stream (inverse-CDF; 1 uniform -> 1 normal).

    Using the inverse standard-normal CDF keeps a clean 1:1 draw accounting and
    keeps every bit of randomness inside the seeded family stream. The endpoints
    0 and 1 (which map to ±inf) are nudged into the open interval.

    The ``size=None`` scalar path skips the array round-trip (asarray/np.clip on a
    0-d array) that dominated the GA-mutation retry loops at D=1000 — same single
    ``rng.random(None)`` stream consumption, same clamp comparisons, and ``ndtri``
    is the identical scipy ufunc kernel for scalars and arrays, so the returned
    double is bit-identical to the previous path.
    """
    if size is None:
        u = float(rng.random(None))
        # keep strictly in (0, 1); RandomContext.random() is [0, 1)
        if u < _U_LO:
            u = _U_LO
        elif u > _U_HI:
            u = _U_HI
        return float(ndtri(u))
    u = np.asarray(rng.random(size), dtype=np.float64)
    np.clip(u, _U_LO, _U_HI, out=u)
    return ndtri(u)


class NormalStream:
    """Chunked N(0,1) source for rejection loops — bit-identical to scalar draws.

    Loops that draw "one normal, retry if rejected" (the GA Gaussian mutation at
    D=1000 issues >1.5M such draws per run, ~15% of MOS wall time) pay a Python
    call plus a scalar ``ndtri`` ufunc dispatch per draw. This peeks a chunk of
    uniforms, converts them with ONE vectorized ``ndtri``, hands them out in
    order, and consumes from the generator exactly the number actually used
    (``close()``), so the stream position and every returned double match the
    scalar path exactly. Falls back to scalar draws on generators without
    look-ahead.

    Use as a context manager so the consumption is always settled::

        with NormalStream(rng) as draw:
            value = draw()
    """

    __slots__ = ("_rng", "_chunk", "_buf", "_used", "_scalar", "_out")

    def __init__(self, rng: RandomContext, chunk: int = 32) -> None:
        """Bind to ``rng``; ``chunk`` uniforms are converted per refill."""
        self._rng = rng
        self._chunk = int(chunk)
        self._buf: np.ndarray | None = None
        self._out: list[float] = []
        self._used = 0
        self._scalar = False

    def __enter__(self) -> "NormalStream":
        """Enter the batched-draw scope."""
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        """Consume exactly the draws that were handed out."""
        self.close()

    def __call__(self) -> float:
        """Return the next N(0,1) value from the family stream."""
        if self._scalar:
            return float(standard_normal(self._rng))
        buf = self._buf
        if buf is None or self._used >= buf.size:
            # Settle what this chunk consumed before peeking the next one.
            if buf is not None:
                self._rng.skip_doubles(self._used)
                self._used = 0
            peeked = self._rng.peek_doubles(self._chunk)
            if peeked is None:                      # generator without look-ahead
                self._scalar = True
                self._buf = None
                return float(standard_normal(self._rng))
            u = np.clip(np.asarray(peeked, dtype=np.float64), _U_LO, _U_HI)
            buf = self._buf = ndtri(u)
            # tolist() reproduces each double exactly (same C double -> PyFloat
            # path as float(buf[i])), so handing out from the list mirror skips
            # the per-draw numpy-scalar conversion bit-identically. ``_buf``
            # stays the ndarray: the refill check above needs ``buf.size``.
            self._out = buf.tolist()
        value = self._out[self._used]
        self._used += 1
        return value

    def close(self) -> None:
        """Consume the draws handed out so far; safe to call more than once."""
        if self._buf is not None and self._used:
            self._rng.skip_doubles(self._used)
        self._buf = None
        self._used = 0


def normal(rng: RandomContext, loc: float, scale: float, size: int | tuple[int, ...] | None = None):
    """Draw N(loc, scale²) from the family stream."""
    return loc + scale * standard_normal(rng, size)


def cauchy(rng: RandomContext, loc: float, scale: float, size: int | tuple[int, ...] | None = None):
    """Draw Cauchy(loc, scale) from the family stream (inverse-CDF; 1 uniform each).

    This is the F-memory sampler for the SHADE lineage: ``F = randc(M_F, 0.1)``.
    """
    u = np.asarray(rng.random(size), dtype=np.float64)
    # ``rng.random`` draws from [0, 1) by generator contract, so the upper guard
    # ``nextafter(1.0, 0.0)`` can never bind and only the lower one is reachable
    # (at exactly u == 0.0). ``np.maximum`` therefore returns the same doubles as
    # the two-sided ``np.clip`` on every value this function can ever see, at
    # ~1 us less per call (1.57 -> 0.52 us at size=1) — and cauchy is drawn
    # ~1100x per run by the whole SHADE lineage (lshade, jso, lshade-spacma).
    np.maximum(u, np.nextafter(0.0, 1.0), out=u)
    c = loc + scale * np.tan(np.pi * (u - 0.5))
    return float(c) if np.ndim(c) == 0 else c


# ---------------------------------------------------------------------------
# Budget-exact evaluation
# ---------------------------------------------------------------------------
class BudgetExhausted(Exception):
    """Raised when an evaluation is attempted with no remaining budget."""


# Cached-checkpoint sentinel once the trace grid is exhausted: strictly above any
# reachable nfes (max_nfes plus at most one batch of overshoot), so the fast-path
# compare in ``_maybe_record`` stays False forever without an emptiness check.
_GRID_DONE = 2**62


@dataclass
class BudgetEvaluator:
    """Count every objective call, track best-so-far, record a bounded trace.

    The algorithm owns budget control (checks :meth:`remaining` and truncates its
    final batch); this evaluator enforces exactness defensively and records the
    convergence trace on a log-spaced NFE grid so local-search-heavy baselines
    (SHADE-ILS, MOS) cannot blow up memory at ``D=1000``.
    """

    problem: Any
    max_nfes: int
    trace_points: int = 1024

    nfes: int = 0
    best_fitness: float = float("inf")
    best_x: np.ndarray | None = None
    _conv_nfes: list[int] = field(default_factory=list)
    _conv_best: list[float] = field(default_factory=list)
    _next_grid_i: int = 0
    _grid: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.int64))
    # Python-int mirrors of the hot budget/trace state (set in __post_init__):
    # int-vs-int compares on the million-call probe paths, truth-identical to
    # the numpy-scalar/attribute-walk originals (int64 -> int is exact).
    _max_nfes_int: int = 0
    _grid_list: list[int] = field(default_factory=list)
    _next_threshold: int = 0

    def __post_init__(self) -> None:
        """Build the log-spaced NFE checkpoint grid (first + last always kept)."""
        n = max(2, int(self.trace_points))
        grid = np.unique(
            np.round(np.geomspace(1, max(1, self.max_nfes), num=n)).astype(np.int64)
        )
        self._grid = grid
        self._max_nfes_int = int(self.max_nfes)
        self._grid_list = grid.tolist()  # int64 -> Python int, exact
        self._next_threshold = self._grid_list[0]

    # -- budget queries ----------------------------------------------------
    def remaining(self) -> int:
        """Objective evaluations left in the budget (>= 0)."""
        return max(0, self._max_nfes_int - self.nfes)

    def is_exhausted(self) -> bool:
        """True once the evaluation budget is fully spent."""
        # max(0, M - n) <= 0  iff  n >= M for ints: same boolean, no max()/call.
        return self.nfes >= self._max_nfes_int

    # -- evaluation --------------------------------------------------------
    def evaluate(self, population: np.ndarray) -> np.ndarray:
        """Evaluate a ``(N, D)`` population; count N calls; update best + trace."""
        pop = np.atleast_2d(np.asarray(population, dtype=np.float64))
        n = pop.shape[0]
        if n == 0:
            return np.empty(0, dtype=np.float64)
        if self.is_exhausted():
            raise BudgetExhausted(f"budget {self.max_nfes} already spent")
        fitness = np.asarray(self.problem.evaluate(pop), dtype=np.float64).reshape(-1)
        if fitness.shape[0] != n:
            raise ValueError(f"problem.evaluate returned {fitness.shape[0]} values for {n} rows")
        self.nfes += n
        if n == 1:
            # single-row fast path (the LS dispatch pattern: millions of calls at
            # D=1000) — argmin over one element is index 0, so this is the exact
            # same comparison/update with the index search skipped.
            f0 = fitness[0]
            if f0 < self.best_fitness:
                self.best_fitness = float(f0)
                self.best_x = pop[0].copy()
        else:
            i = int(np.argmin(fitness))
            if fitness[i] < self.best_fitness:
                self.best_fitness = float(fitness[i])
                self.best_x = pop[i].copy()
        self._maybe_record()
        return fitness

    def evaluate_one(self, x: np.ndarray) -> float:
        """Evaluate a single ``(D,)`` point (local-search probe). Counts one call.

        Inlines the ``n == 1`` bookkeeping of :meth:`evaluate` (the LS probe
        pattern: millions of calls at ``D=1000``), skipping the redundant
        atleast_2d/shape/branch dispatch of the batch path. Same coercion (so
        ``problem.evaluate`` receives the identical array object), same check
        order, same compares/updates/records — the run is bit-identical.
        """
        row = np.asarray(x, dtype=np.float64).reshape(1, -1)
        if self.nfes >= self._max_nfes_int:
            raise BudgetExhausted(f"budget {self.max_nfes} already spent")
        fitness = np.asarray(self.problem.evaluate(row), dtype=np.float64).reshape(-1)
        if fitness.shape[0] != 1:
            raise ValueError(f"problem.evaluate returned {fitness.shape[0]} values for 1 rows")
        self.nfes += 1
        f0 = fitness[0]
        if f0 < self.best_fitness:
            self.best_fitness = float(f0)
            self.best_x = row[0].copy()
        self._maybe_record()
        return float(f0)

    def _maybe_record(self) -> None:
        """Append the best-so-far whenever nfes crosses the next log-spaced checkpoint."""
        if self.nfes < self._next_threshold:
            return
        # Crossed at least one checkpoint: advance past every threshold <= nfes
        # (same walk as before), refresh the cached next one, and record once.
        grid = self._grid_list
        n = len(grid)
        i = self._next_grid_i
        while i < n and self.nfes >= grid[i]:
            i += 1
        self._next_grid_i = i
        self._next_threshold = grid[i] if i < n else _GRID_DONE
        self._conv_nfes.append(int(self.nfes))
        self._conv_best.append(float(self.best_fitness))

    def convergence(self) -> ConvergenceTrace:
        """Return the recorded trace, guaranteeing a final point at the true nfes."""
        nfes = list(self._conv_nfes)
        best = list(self._conv_best)
        if not nfes or nfes[-1] != self.nfes:
            nfes.append(int(self.nfes))
            best.append(float(self.best_fitness))
        return ConvergenceTrace(
            nfes=np.asarray(nfes, dtype=np.int64),
            best_fitness=np.asarray(best, dtype=np.float64),
        )


# ---------------------------------------------------------------------------
# Result assembly (family schema)
# ---------------------------------------------------------------------------
def build_result(
    optimizer_id: str,
    problem: Any,
    options: OptimizerOptions,
    ev: BudgetEvaluator,
    *,
    start_time: float,
    termination: str = "max_evaluations",
    params: dict[str, Any] | None = None,
    notes: str = "",
    telemetry: Any | None = None,
) -> OptimizerResult:
    """Assemble an ``OptimizerResult`` in the exact family schema.

    ``telemetry`` is accepted for signature parity with the project-05 original
    but is DROPPED here: this project's
    :class:`~gsk_family.types.OptimizerResult` has no ``telemetry`` field (the
    GSK family exposes per-generation state through ``generation_callback``
    instead). The parameter is kept so the vendored algorithm bodies need no
    edit; see ``_telemetry_shim``. This is the only behavioural adaptation.
    """
    if ev.best_x is None:
        raise RuntimeError(f"{optimizer_id}: no evaluation was performed")
    error = compute_error(ev.best_fitness, float(problem.optimum), float(problem.target_error))
    return OptimizerResult(
        optimizer=optimizer_id,
        suite=problem.suite,
        func_id=int(problem.func_id),
        dim=int(problem.dim),
        seed=int(options.seed),
        best_x=np.asarray(ev.best_x, dtype=np.float64),
        best_fitness=float(ev.best_fitness),
        error=float(error),
        nfes=int(ev.nfes),
        termination=termination,
        convergence=ev.convergence(),
        runtime_seconds=float(time.perf_counter() - start_time),
        params=dict(params or {}),
        notes=notes,
    )


def make_recorder(problem: Any, options: OptimizerOptions, counting_rule: str) -> TelemetryRecorder:
    """Create the family ``TelemetryRecorder`` for a baseline run (data parity §3.7).

    Baselines feed this recorder (``record_initial`` then per-generation
    ``record_generation``) so their GISR / diversity / per-generation records — and
    thus the cross-optimizer RLSR/GISR/diversity/convergence analysis — are produced
    exactly as for the family. ``diversity_points`` is threaded from ``options`` like
    the family (0 = dense; >0 thins the per-generation snapshot for LSGO).
    """
    return TelemetryRecorder(
        max_nfes=int(problem.max_nfes),
        lb=problem.lb,
        ub=problem.ub,
        counting_rule=counting_rule,
        diversity_points=int(_values(options).get("diversity_points", 0)),
    )


def start_run(problem: Any, options: OptimizerOptions) -> tuple[RandomContext, BudgetEvaluator, float]:
    """Common run preamble: validate, build the family RNG, and the evaluator."""
    if problem.max_nfes <= 0:
        raise ValueError(f"problem.max_nfes must be positive, got {problem.max_nfes}")
    if problem.dim <= 0:
        raise ValueError(f"problem.dim must be positive, got {problem.dim}")
    rng = make_rng(options)
    ev = BudgetEvaluator(problem=problem, max_nfes=int(problem.max_nfes))
    return rng, ev, time.perf_counter()
