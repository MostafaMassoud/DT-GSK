"""DT-GSK optimizer adapter conforming to the gsk_family ``optimize()`` contract.

Bridges the vendored DT-GSK core (``_dt_core.dt_gsk_optimize`` with its
``DTGSKConfig``/``DTGSKResult`` types) to the project's uniform optimizer
contract ``optimize(problem, options) -> OptimizerResult``.

Design (see docs/development/dt_gsk_core_reference.md):

- The dimension-aware ``pub`` ``DTGSKConfig`` is built by
  :func:`gsk_family.optimizers._dt_profiles.build_pub_config`.
- ``problem.evaluate`` is wrapped as the batch objective; the core's
  ``BudgetController`` is the single evaluation cap, and ``nfes_used`` is
  reported as ``OptimizerResult.nfes``.
- DT-GSK seeds its own substream RNG from ``options.seed`` and draws its own
  initial population, so it does **not** consume the runner's fair-start
  ``initial_population``. This is a documented, intentional fair-start exception
  (it preserves DT-GSK's tuned, byte-identical initialization); the run remains
  fully deterministic for a given seed.
"""

from __future__ import annotations

import dataclasses
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from gsk_family.benchmark_adapter.problem import BenchmarkProblem
from gsk_family.optimizers._dt_core import DTGSKConfig, dt_gsk_optimize
from gsk_family.optimizers._dt_profiles import build_pub_config
from gsk_family.stats import compute_error
from gsk_family.types import ConvergenceTrace, OptimizerOptions, OptimizerResult

_MISSING = object()
_DTGSK_FIELDS = frozenset(f.name for f in dataclasses.fields(DTGSKConfig))
# Run-level fields resolved from the problem/options, not overridable via values.
_RESERVED_FIELDS = frozenset({"dim", "seed", "max_nfes", "bounds", "rand_generator"})


def _option_value(options: Any, name: str, default: Any = _MISSING) -> Any:
    """Read an optimizer option from object, dict, or nested values mapping."""
    if options is None:
        if default is _MISSING:
            raise ValueError(f"options.{name} is required.")
        return default
    if isinstance(options, dict):
        value = options.get(name, _MISSING)
        values = options.get("values", {})
    else:
        value = getattr(options, name, _MISSING)
        values = getattr(options, "values", {})
    if (value is _MISSING or value is None) and isinstance(values, dict):
        value = values.get(name, _MISSING)
    if value is _MISSING or value is None:
        if default is _MISSING:
            raise ValueError(f"options.{name} is required.")
        return default
    return value


def _values_dict(options: Any) -> dict[str, Any]:
    """Return the optimizer-specific ``values`` mapping from options."""
    if options is None:
        return {}
    if isinstance(options, dict):
        values = options.get("values", {})
    else:
        values = getattr(options, "values", {})
    return dict(values) if isinstance(values, dict) else {}


def _resolve_bounds(problem: BenchmarkProblem) -> tuple[Any, Any]:
    """Return the search box for DT-GSK.

    Uniform bounds collapse to scalar ``(lo, hi)`` floats (so CEC2017/sphere
    configs stay byte-identical to the source). Heterogeneous per-dimension
    bounds -- e.g. CEC2011 real-world problems where each variable has its own
    range -- are returned as ``(lb_array, ub_array)``; ``DTGSKConfig`` and its
    ``bounds_matrix`` consume either form.
    """
    lb = np.asarray(problem.lb, dtype=np.float64).reshape(-1)
    ub = np.asarray(problem.ub, dtype=np.float64).reshape(-1)
    if lb.size == 0 or ub.size == 0:
        raise ValueError("dt-gsk requires non-empty bounds.")
    if np.all(lb == lb[0]) and np.all(ub == ub[0]):
        return float(lb[0]), float(ub[0])
    return lb, ub


# Critical DTGSKGenerationLog fields kept when ``dt_diagnostics_include_all_fields``
# is false (a compact subset for root-cause triage).
_DIAG_CRITICAL_FIELDS: tuple[str, ...] = (
    "gen", "evals_used", "budget_frac", "pop_size", "best_fitness", "mean_fitness",
    "median_fitness", "worst_fitness", "fitness_std", "fitness_range",
    "accepted_offspring", "offspring_evaluated", "acceptance_rate", "best_improvement",
    "stagnation_gens", "diversity_radius", "diversity_ratio", "ace_entropy",
    "ace_top_entropy", "ace_bottom_entropy", "module_prob_mass", "modules_active",
    "restarts_done", "restart_triggered", "restart_cause", "archive_size",
    "local_search_triggered", "local_search_roi", "interaction_graph_active",
    "boundary_hit_rate", "stop_reason",
)


def _diagnostics_settings(options: Any) -> dict[str, Any] | None:
    """Return active DT-GSK diagnostics settings, or ``None`` when disabled.

    Diagnostics are opt-in (default off) and adapter/runner-level ONLY -- they
    are not ``DTGSKConfig`` fields and never affect the optimizer config or its
    hash. Active only when ``dt_diagnostics`` is true AND an output directory is
    provided (the runner injects it; direct callers pass it). When ``None`` the
    optimizer takes its default, byte-identical ``curve_callback`` path.
    """
    values = _values_dict(options)
    if not bool(values.get("dt_diagnostics", False)):
        return None
    out_dir = values.get("dt_diagnostics_dir")
    if not out_dir:
        return None
    return {
        "dir": str(out_dir),
        "run": int(values.get("dt_diagnostics_run") or 0),
        "format": str(values.get("dt_diagnostics_format", "jsonl")),
        "flush": bool(values.get("dt_diagnostics_flush", False)),
        "include_all_fields": bool(values.get("dt_diagnostics_include_all_fields", True)),
    }


def _sanitize_json_value(value: Any) -> Any:
    """Return a JSON-serializable view of *value*.

    Handles Python/NumPy scalars, NumPy arrays, tuples/lists, dicts, and
    non-finite floats. Non-finite floats are encoded as the strings ``"NaN"``,
    ``"Infinity"``, and ``"-Infinity"`` so the JSONL stays strictly valid (the
    standard library would otherwise emit bare ``NaN``/``Infinity`` tokens).
    """
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if value != value:
            return "NaN"
        if value == float("inf"):
            return "Infinity"
        if value == float("-inf"):
            return "-Infinity"
        return value
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return _sanitize_json_value(float(value))
    if isinstance(value, np.ndarray):
        return [_sanitize_json_value(v) for v in value.tolist()]
    if isinstance(value, (list, tuple)):
        return [_sanitize_json_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _sanitize_json_value(v) for k, v in value.items()}
    return value


def _run_with_diagnostics(
    objective: Any,
    config: DTGSKConfig,
    diag: dict[str, Any],
    problem: BenchmarkProblem,
    seed: int,
    rand_generator: str,
    conv_nfes: list[int],
    conv_best: list[float],
) -> Any:
    """Run DT-GSK while streaming per-generation telemetry to one JSONL file.

    Uses the core's ``generation_callback`` (which takes precedence over and
    is purely observational relative to ``curve_callback`` -- it draws no RNG
    and evaluates no objective). The convergence trace is derived from the
    per-generation ``best_fitness``, so the returned result is numerically
    identical to the default path for a given seed. One file per cell:
    ``DTTrace_<suite>_F<func>_D<dim>_R<run>_S<seed>.jsonl``.
    """
    out_dir = Path(diag["dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / (
        f"DTTrace_{problem.suite}_F{int(problem.func_id)}_D{int(problem.dim)}"
        f"_R{int(diag['run'])}_S{int(seed)}.jsonl"
    )
    meta = {
        "optimizer": "dt-gsk",
        "suite": problem.suite,
        "function": int(problem.func_id),
        "dimension": int(problem.dim),
        "run": int(diag["run"]),
        "seed": int(seed),
        "rand_generator": str(rand_generator),
        "max_nfes": int(problem.max_nfes),
    }
    include_all = diag["include_all_fields"]
    flush = diag["flush"]
    with path.open("w", encoding="utf-8", newline="\n") as handle:

        def generation_callback(log: Any) -> None:
            """Record the convergence point and serialize one generation log line.

            The JSONL record keeps the raw per-generation ``best_fitness`` (the
            working incumbent, which diagnostics analyze), but the convergence
            trace is clamped to the running minimum so it matches the default
            ``curve_callback`` path's best-so-far contract.
            """
            value = float(log.best_fitness)
            if conv_best and conv_best[-1] < value:
                value = conv_best[-1]
            conv_nfes.append(int(log.evals_used))
            conv_best.append(value)
            if include_all:
                fields = dataclasses.asdict(log)
            else:
                fields = {k: getattr(log, k) for k in _DIAG_CRITICAL_FIELDS if hasattr(log, k)}
            record = {**meta, **{k: _sanitize_json_value(v) for k, v in fields.items()}}
            handle.write(json.dumps(record) + "\n")
            if flush:
                handle.flush()

        return dt_gsk_optimize(
            objective=objective, config=config, generation_callback=generation_callback
        )


def optimize(problem: BenchmarkProblem, options: OptimizerOptions | dict[str, Any]) -> OptimizerResult:
    """Run the DT-GSK optimizer under the dimension-aware ``pub`` profile."""
    seed = int(_option_value(options, "seed"))
    rand_generator = str(_option_value(options, "rand_generator", "threefry"))
    dim = int(problem.dim)
    max_nfes = int(problem.max_nfes)
    if max_nfes <= 0:
        raise ValueError(f"problem.max_nfes must be positive, got {problem.max_nfes}.")
    if dim <= 0:
        raise ValueError(f"problem.dim must be positive, got {problem.dim}.")
    bounds = _resolve_bounds(problem)

    config = build_pub_config(
        dim, seed=seed, max_nfes=max_nfes, bounds=bounds, rand_generator=rand_generator
    )

    # Advanced per-run overrides of DTGSKConfig fields via options.values
    # (run-level fields are reserved and resolved from the problem/options).
    overrides = {
        key: value
        for key, value in _values_dict(options).items()
        if key in _DTGSK_FIELDS and key not in _RESERVED_FIELDS
    }
    if overrides:
        config = dataclasses.replace(config, **overrides)

    conv_nfes: list[int] = []
    conv_best: list[float] = []

    def curve_callback(evals_used: int, best_f: float) -> None:
        """Record one best-so-far convergence point.

        The core reports the *working* incumbent, which the deep-stall
        multi-start resets to a fresh random population when it fires (the
        preserved global best is restored into the returned result only after
        the loop). Clamp to the running minimum so the recorded trace honors
        the ``ConvergenceTrace`` best-so-far contract; observational only.
        """
        value = float(best_f)
        if conv_best and conv_best[-1] < value:
            value = conv_best[-1]
        conv_nfes.append(int(evals_used))
        conv_best.append(value)

    def objective(population: np.ndarray) -> np.ndarray:
        """Evaluate one population batch through the benchmark problem."""
        return np.asarray(problem.evaluate(population), dtype=np.float64).reshape(-1)

    diag = _diagnostics_settings(options)
    start = time.perf_counter()
    if diag is None:
        result = dt_gsk_optimize(objective=objective, config=config, curve_callback=curve_callback)
    else:
        # Opt-in per-generation diagnostics (observational; same result for a
        # given seed). Derives the convergence trace from the generation log.
        result = _run_with_diagnostics(
            objective, config, diag, problem, seed, rand_generator, conv_nfes, conv_best
        )
    runtime_seconds = float(time.perf_counter() - start)

    if not conv_nfes:
        conv_nfes.append(int(result.nfes_used))
        conv_best.append(float(result.best_f))

    error = compute_error(
        float(result.best_f), float(problem.optimum), float(problem.target_error)
    )
    termination = (
        "max_evaluations" if result.stop_reason == "budget_exhausted" else str(result.stop_reason)
    )

    return OptimizerResult(
        optimizer="dt-gsk",
        suite=problem.suite,
        func_id=int(problem.func_id),
        dim=dim,
        seed=seed,
        best_x=np.asarray(result.best_x, dtype=np.float64).reshape(-1),
        best_fitness=float(result.best_f),
        error=float(error),
        nfes=int(result.nfes_used),
        termination=termination,
        convergence=ConvergenceTrace(
            nfes=np.asarray(conv_nfes, dtype=np.int64),
            best_fitness=np.asarray(conv_best, dtype=np.float64),
        ),
        runtime_seconds=runtime_seconds,
        params={
            "profile": "pub",
            "np_init_mult": config.np_init_mult,
            "n_min": config.n_min,
            "KF": config.KF,
            "KR": config.KR,
            "Kexp": config.Kexp,
            "restarts_done": int(result.restarts_done),
            "max_nfes": int(result.max_nfes),
        },
        notes="self-init (fair-start exception)",
    )
