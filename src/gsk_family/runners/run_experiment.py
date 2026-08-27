"""Experiment runner for Python GSK-family experiments."""

from __future__ import annotations

import json
import math
import multiprocessing
import os
import platform
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.benchmark_adapter.protocol import (
    default_dimensions,
    default_function_ids,
    is_native_dimension_suite,
)
from gsk_family.analysis.statistical_tests import (
    StatAnalysisResult,
    format_cross_dim_summary,
    format_per_dim_tldr,
    run_statistical_analysis,
)
from gsk_family.common.rng import create_fair_start
from gsk_family.optimizers.agsk import optimize as optimize_agsk
from gsk_family.optimizers.apgsk import optimize as optimize_apgsk
from gsk_family.optimizers.atmals_gsk import optimize as optimize_atmals_gsk
from gsk_family.optimizers.egsk import optimize as optimize_egsk
from gsk_family.optimizers.fdb_agsk import optimize as optimize_fdb_agsk
from gsk_family.optimizers.gsk import optimize as optimize_gsk
from gsk_family.optimizers.dt_gsk import optimize as optimize_dt_gsk

# External SOTA baselines, vendored from 05-Human-Inspired-Family_Python_v0.1 so the
# CEC2013LSGO comparison can be run first-party (identical objective code, seed
# schedule, budget and protocol) instead of citing published means. Not part of the
# seven-method GSK-family panel; see optimizers/external/__init__.py.
from gsk_family.optimizers.external import (
    optimize_cmaes,
    optimize_decc_g,
    optimize_ebowithcmar,
    optimize_jso,
    optimize_lshade,
    optimize_lshade_spacma,
    optimize_mos,
    optimize_shade_ils,
)
from gsk_family.runners.config import ExperimentConfig, config_from_mapping
from gsk_family.runners.fp_regime import ensure_canonical_fp_regime
from gsk_family.runners.output import (
    CHECKPOINT_FRACTIONS,
    RunArtifact,
    ensure_output_dirs,
    read_existing_per_run,
    run_record_to_row,
    write_curves_and_logs,
    write_environment,
    write_per_run,
    write_profile,
    write_seed_schedule,
    write_summary_tables,
)
from gsk_family.runners.parallel import RunTask, effective_worker_count, execute_run_tasks
from gsk_family.runners.performance import (
    configure_numba_runtime,
    format_numba_runtime_line,
    warm_benchmark_cells,
    warmup_records_to_json,
)
from gsk_family.runners.seed_policy import (
    SeedScheduleRow,
    effective_rand_generator,
    seed_for_run,
)
from gsk_family.runners.verification import ensure_output_root_allowed, verify_run_directory
from gsk_family.runners.verification import load_reference_table
from gsk_family.stats import format_scientific, statistic_values, summarize
from gsk_family.types import OptimizerOptions, RunRecord


OPTIMIZER_FUNCTIONS = {
    "agsk": optimize_agsk,
    "apgsk": optimize_apgsk,
    "atmals-gsk": optimize_atmals_gsk,
    "egsk": optimize_egsk,
    "fdb-agsk": optimize_fdb_agsk,
    "gsk": optimize_gsk,
    "dt-gsk": optimize_dt_gsk,
    # External SOTA baselines -- NOT part of the seven-method GSK-family panel.
    "mos-cec2013lsgo": optimize_mos,
    "shade-ils": optimize_shade_ils,
    "decc-g": optimize_decc_g,
    "cmaes": optimize_cmaes,
    "ebowithcmar": optimize_ebowithcmar,
    "jso": optimize_jso,
    "lshade": optimize_lshade,
    "lshade-spacma": optimize_lshade_spacma,
}


_SEED_SCHEME_TEXT = (
    "unified: seed = mod(uint64(base_seed) + uint64(1000003)*uint64(dim) + "
    "uint64(1000033)*uint64(func) + uint64(1000037)*uint64(run), "
    "uint64(2147483646)) + 1; optimizer-independent fair cross-family schedule; "
    "generator resolved to threefry when available, otherwise twister; X0 drawn once in the runner"
)


def _runtime_provenance(project_root: Path) -> dict[str, Any]:
    """Collect Python-truthful provenance fields for environment metadata."""
    commit = ""
    try:
        completed = subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        commit = completed.stdout.strip()
    except Exception:  # pragma: no cover - git is optional at runtime
        commit = ""
    return {
        "python_version": platform.python_version(),
        "cpu_cores": os.cpu_count(),
        "computer": platform.node(),
        "platform": platform.platform(),
        "git_commit": commit,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def _run_config_optimizer_params(optimizer: str, options: dict[str, Any]) -> dict[str, Any]:
    """Return the resolved optimizer parameters recorded in ``run_config.json``."""
    if optimizer == "gsk":
        return {
            "pop_size": int(options.get("np", 100)),
            "KF": float(options.get("kf", options.get("KF", 0.5))),
            "KR": float(options.get("kr", options.get("KR", 0.9))),
            "K": int(options.get("k", options.get("K", 10))),
            "P": float(options.get("p", options.get("P", 0.1))),
        }
    if optimizer in {"agsk", "apgsk", "fdb-agsk"}:
        return {
            "NP_init": int(options.get("np_init", 100)),
            "min_pop_size": int(options.get("min_pop_size", 12)),
        }
    if optimizer == "dt-gsk":
        return {"profile": str(options.get("profile", "pub"))}
    return {"pop_size": int(options.get("np", 100))}


@dataclass
class ExperimentRunSummary:
    """Summary returned by ``run_experiment``."""

    output_dirs: list[Path] = field(default_factory=list)
    records: list[RunRecord] = field(default_factory=list)
    skipped_cells: list[dict[str, Any]] = field(default_factory=list)
    skipped_completed: int = 0
    runtime_seconds_total: float = 0.0


def _build_config(config: ExperimentConfig | dict[str, Any] | None, kwargs: dict[str, Any]) -> ExperimentConfig:
    """Merge direct keyword overrides and return a normalized config."""
    if isinstance(config, ExperimentConfig):
        if kwargs:
            merged = {**config.__dict__, **kwargs}
            if "workers" in kwargs and "workers_auto" not in kwargs:
                merged["workers_auto"] = False
            return config_from_mapping(merged)
        return config
    if isinstance(config, dict):
        merged = {**config, **kwargs}
        return config_from_mapping(merged)
    return config_from_mapping(kwargs)


def _resolve_cells(config: ExperimentConfig) -> list[tuple[int, int]]:
    """Resolve configured functions and dimensions into run cells."""
    functions = config.functions if isinstance(config.functions, tuple) else tuple()
    cells: list[tuple[int, int]] = []
    if config.dimensions == "native" or is_native_dimension_suite(config.suite):
        for func in functions:
            problem = make_problem(
                config.suite,
                func,
                None,
                config.max_evaluations,
                benchmark_fp_mode=config.benchmark_fp_mode,
            )
            cells.append((func, int(problem.dim)))
        return cells

    dims = config.dimensions
    if isinstance(dims, str):
        defaults = default_dimensions(config.suite)
        if isinstance(defaults, str):
            raise ValueError(f"{config.suite} requires native dimensions.")
        dims = defaults
    # Protocol-undefined combinations are dropped from the cross-product rather
    # than crashing at construction. cec2020 is the one suite whose function set
    # varies BY DIMENSION: Yue et al. 2019 SS2.1 defines F6/F7 for D=10/15/20
    # only, so `functions: all` over all four dims must not schedule them at
    # D=5 -- make_problem would (correctly) refuse the cell.
    excluded: frozenset[tuple[int, int]] = frozenset()
    if config.suite == "cec2020":
        from gsk_family.benchmark_adapter.factory import CEC2020_PROTOCOL_EXCLUDED_CELLS
        excluded = CEC2020_PROTOCOL_EXCLUDED_CELLS
    for func in functions:
        for dim in dims:
            if (int(func), int(dim)) in excluded:
                continue
            cells.append((int(func), int(dim)))
    return cells


def _execution_ordered_cells(config: ExperimentConfig, cells: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return reference-compatible dimension-major execution order for fixed-dimension suites."""
    if config.dimensions == "native" or is_native_dimension_suite(config.suite):
        return cells
    return sorted(cells, key=lambda item: (int(item[1]), int(item[0])))


def _resolve_suite_warmup_cells(config: ExperimentConfig) -> list[tuple[int, int]]:
    """Return the default suite grid used for publication warmup."""
    cells: list[tuple[int, int]] = []
    functions = default_function_ids(config.suite)
    dimensions = default_dimensions(config.suite)
    if dimensions == "native" or is_native_dimension_suite(config.suite):
        for func in functions:
            problem = make_problem(
                config.suite,
                func,
                None,
                config.max_evaluations,
                benchmark_fp_mode=config.benchmark_fp_mode,
            )
            cells.append((int(func), int(problem.dim)))
        return cells
    for func in functions:
        for dim in dimensions:
            cells.append((int(func), int(dim)))
    return cells


def _resolve_warmup_cells(config: ExperimentConfig, selected_cells: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return selected-cell or full-suite warmup cells."""
    if config.warmup_scope == "suite":
        return _resolve_suite_warmup_cells(config)
    return selected_cells


def _current_schedule_rows(config: ExperimentConfig, optimizer: str, cells: list[tuple[int, int]]) -> list[SeedScheduleRow]:
    """Build seed schedule rows for one optimizer over resolved cells."""
    rows: list[SeedScheduleRow] = []
    for func, dim in cells:
        for run in range(1, config.runs + 1):
            rows.append(
                SeedScheduleRow(
                    dim=int(dim),
                    function=int(func),
                    run=int(run),
                    seed=seed_for_run(
                        config.seed_policy,
                        optimizer,
                        config.suite,
                        config.seed,
                        int(dim),
                        int(func),
                        int(run),
                    ),
                )
            )
    return rows


def _row_key(row: dict[str, str]) -> tuple[int, int, int]:
    """Return the function, dimension, and run key for a per-run CSV row."""
    return (int(row["function"]), int(row["dimension"]), int(row["run"]))


def _bank_from_rows(
    rows: list[dict[str, Any]], statistics_basis: str
) -> tuple[dict[tuple[int, int], int], dict[tuple[int, int], list[float]]]:
    """Index per-run rows by ``(dim, func)`` for BUG-RESUME-01.

    ``per_run.csv`` is the authoritative bank: it merges prior runs on resume,
    while ``artifacts`` holds only this session's. Returning counts AND values
    lets the summary writer detect a partially-resumed cell (bank count exceeds
    artifact count) and summarise the complete set instead of the new subset.
    The basis selects the column that ``stats.statistic_values`` would return --
    ``best_fitness`` for raw_objective, the precomputed ``error`` otherwise.
    """
    field = "best_fitness" if statistics_basis == "raw_objective" else "error"
    counts: dict[tuple[int, int], int] = {}
    values: dict[tuple[int, int], list[float]] = {}
    for row in rows:
        try:
            key = (int(row["dimension"]), int(row["function"]))
            value = float(row[field])
        except (KeyError, TypeError, ValueError):
            continue
        counts[key] = counts.get(key, 0) + 1
        values.setdefault(key, []).append(value)
    return counts, values


def _matching_existing_rows(rows: list[dict[str, str]]) -> dict[tuple[int, int, int, int], dict[str, str]]:
    """Index existing per-run rows by cell and seed for resume behavior."""
    mapped: dict[tuple[int, int, int, int], dict[str, str]] = {}
    for row in rows:
        try:
            key = (*_row_key(row), int(row["seed"]))
        except (KeyError, ValueError):
            continue
        mapped[key] = row
    return mapped


def _run_record_from_result(result: Any, run: int) -> RunRecord:
    """Convert an optimizer result into a normalized runner record."""
    return RunRecord(
        optimizer=result.optimizer,
        suite=result.suite,
        function=result.func_id,
        dimension=result.dim,
        run=int(run),
        seed=result.seed,
        best_fitness=result.best_fitness,
        error=result.error,
        nfes=result.nfes,
        termination=result.termination,
        runtime_seconds=result.runtime_seconds,
    )


def _optimizer_population_size(optimizer: str, optimizer_options: dict[str, Any]) -> int:
    """Return the population size required for a fair-start payload."""
    if optimizer in {"agsk", "apgsk", "fdb-agsk"} and "np_init" in optimizer_options:
        return int(optimizer_options["np_init"])
    if "np" in optimizer_options:
        return int(optimizer_options["np"])
    return 100


def _run_one(
    config: ExperimentConfig,
    optimizer: str,
    func: int,
    dim: int,
    run: int,
    seed: int,
) -> RunArtifact:
    """Execute one optimizer/function/dimension/run cell."""
    if optimizer not in OPTIMIZER_FUNCTIONS:
        raise NotImplementedError(
            f"Optimizer {optimizer!r} is registered but has no execution function configured."
        )

    problem = make_problem(
        config.suite,
        func,
        dim,
        config.max_evaluations,
        benchmark_fp_mode=config.benchmark_fp_mode,
        benchmark_backend=_benchmark_backend_for_optimizer(config, optimizer),
        data_root=config.data_root,
    )
    generator = effective_rand_generator(config.seed_policy, optimizer, config.rand_generator)
    optimizer_options = dict(config.optimizer_options)
    if optimizer == "atmals-gsk" and "protocol" not in optimizer_options:
        if config.suite == "cec2011":
            optimizer_options["protocol"] = "cec2011"
        elif config.suite == "cec2017":
            optimizer_options["protocol"] = "cec2017"
    # Opt-in DT-GSK per-generation diagnostics: inject the per-cell output
    # directory + run number so the adapter writes one JSONL trace per cell.
    # Off by default; only touches this local options copy (run_config schema
    # and optimizer numerics are unchanged).
    if optimizer == "dt-gsk" and optimizer_options.get("dt_diagnostics", False):
        diag_dir = Path(config.output_root) / optimizer / config.suite / "diagnostics"
        optimizer_options["dt_diagnostics_dir"] = str(diag_dir)
        optimizer_options["dt_diagnostics_run"] = int(run)
    options = OptimizerOptions(seed=seed, rand_generator=generator, values=optimizer_options)

    if config.seed_policy == "unified":
        np_size = _optimizer_population_size(optimizer, optimizer_options)
        fair = create_fair_start(seed, generator, np_size, problem.dim, problem.lb, problem.ub)
        options.initial_population = fair.initial_population
        options.rng_state_after_initialization = fair.rng_state_after_initialization

    result = OPTIMIZER_FUNCTIONS[optimizer](problem, options)
    record = _run_record_from_result(result, run)
    return RunArtifact(
        record=record,
        result=result,
        statistics_basis=problem.statistics_basis,
        optimum=float(problem.optimum),
        target_error=float(problem.target_error),
        max_nfes=int(problem.max_nfes),
    )


def _task_from_schedule_row(optimizer: str, row: SeedScheduleRow) -> RunTask:
    """Convert a seed schedule row into a parallel-dispatch task."""
    return RunTask(
        optimizer=optimizer,
        function=int(row.function),
        dimension=int(row.dim),
        run=int(row.run),
        seed=int(row.seed),
    )


def _log_console(enabled: bool, message: str) -> None:
    """Write one flushed console progress line when console logging is enabled."""
    if enabled:
        print(message, flush=True)


def _progress_bar(completed: int, total: int, *, width: int = 24) -> str:
    """Return a compact ASCII progress bar suitable for PowerShell logs."""
    safe_total = max(1, int(total))
    safe_completed = max(0, min(int(completed), safe_total))
    filled = int(round(width * safe_completed / safe_total))
    percent = 100.0 * safe_completed / safe_total
    return f"[{'#' * filled}{'-' * (width - filled)}] {safe_completed}/{safe_total} {percent:5.1f}%"


def _log_finalize_progress(
    enabled: bool,
    optimizer: str,
    completed: int,
    total: int,
    label: str,
) -> None:
    """Print one finalization progress line outside the function summary table."""
    _log_console(enabled, f"[finalize] {optimizer.upper()} {_progress_bar(completed, total)} {label}")


def _format_number_list(values: list[int] | tuple[int, ...] | set[int]) -> str:
    """Return a reference-style bracketed integer list."""
    return "[" + " ".join(str(int(value)) for value in sorted(values)) + "]"


def _format_dimension_label(dimensions: list[int] | tuple[int, ...] | set[int]) -> str:
    """Return a compact dimension label."""
    dims = sorted(int(dim) for dim in dimensions)
    return str(dims[0]) if len(dims) == 1 else _format_number_list(dims)


def _excluded_functions(config: ExperimentConfig, functions_run: set[int]) -> list[int]:
    """Return functions excluded from a run-all style request."""
    if config.suite == "cec2017" and functions_run == set(default_function_ids(config.suite)):
        return [2]
    return []


def _statistical_analysis_enabled(config: ExperimentConfig, optimizer: str) -> bool:
    """Return True when the opt-in per-dim statistical analysis should run.

    Mirrors the reference runner's gating: only the advanced GSK-family
    optimizers (never vanilla ``gsk``) participate in the Wilcoxon + Friedman
    panel.  Both fixed-dimension suites (e.g. ``cec2017``) and the
    native-dimension ``cec2011`` rollup are supported now that CEC2011
    reference rollups are committed -- CEC2011 emits a single per-suite panel
    (see ``_emit_statistical_analysis`` and ``close_streaming_table``).
    """
    if not config.statistical_analysis:
        return False
    if optimizer == "gsk":
        return False
    return True


def _emit_statistical_analysis(
    config: ExperimentConfig,
    optimizer: str,
    dirs: dict[str, Path],
    dim: int,
    funcs_to_run: set[int],
) -> "StatAnalysisResult | None":
    """Run and print the per-dimension Wilcoxon + Friedman panel for one dim.

    Returns the ``StatAnalysisResult`` so the caller can accumulate it for the
    end-of-run cross-dimension summary, or ``None`` when the panel could not be
    built. Never raises: any failure is logged as a one-line skip notice so a
    statistical hiccup can never crash an experiment run.
    """
    try:
        is_cec2011 = config.suite == "cec2011"
        if is_cec2011:
            # CEC2011 uses native per-problem dimensions, so the reproduced run
            # and every reference are single rollups (<alg>_cec2011.csv, 22
            # problems) -- there is no per-dimension summary, and F2
            # (Lennard-Jones) is a legitimate problem so nothing is excluded.
            summary_csv = dirs["summary"] / f"{optimizer}_cec2011.csv"
            excluded: tuple[int, ...] = ()
        else:
            summary_csv = dirs["summary"] / f"{optimizer}_{config.suite}_D{dim}.csv"
            excluded = tuple(_excluded_functions(config, funcs_to_run)) or (2,)
        ref_base = Path(config.reference_root) / config.suite.lower()
        if not ref_base.is_dir() or not summary_csv.exists():
            return None
        # Validate the current run against the reference implementation of the
        # same optimizer when its reference results are committed (e.g. the
        # reference DT-GSK under benchmarks/cec_reference_results/<suite>/dt-gsk/).
        # Added as a "<OPT>-REF" comparator alongside the GSK-family panel.
        extra_comparators: dict[str, Path] = {}
        if is_cec2011:
            self_ref_csv = ref_base / optimizer / f"{optimizer}_cec2011.csv"
            if not self_ref_csv.exists():
                # Case-insensitive fallback (committed DT-GSK is _CEC2011.csv).
                self_ref_csv = ref_base / optimizer / f"{optimizer}_CEC2011.csv"
        else:
            self_ref_csv = ref_base / optimizer / f"{optimizer}_{config.suite.lower()}_D{dim}.csv"
        if self_ref_csv.exists():
            extra_comparators[f"{optimizer.upper()}-REF"] = self_ref_csv
        stat_report = run_statistical_analysis(
            new_summary_csv=summary_csv,
            ref_base_dir=ref_base,
            suite=config.suite,
            dim=dim,
            new_label=optimizer,
            excluded_funcs=excluded,
            zero_tol=1e-8,
            extra_comparators=extra_comparators or None,
        )
        for line in str(stat_report).splitlines():
            _log_console(config.console_log, line)
        tldr_text = format_per_dim_tldr(stat_report, suite=config.suite, log_path=None)
        if tldr_text:
            for line in tldr_text.splitlines():
                _log_console(config.console_log, line)
        return stat_report
    except Exception as exc:  # pragma: no cover - graceful degradation
        _log_console(
            config.console_log,
            f"[stats] skipped statistical analysis for {optimizer.upper()} D{dim}: {exc}",
        )
        return None


def _statistics_label(statistics_basis: str) -> str:
    """Return a human-readable statistics basis label."""
    return "raw objective" if statistics_basis == "raw_objective" else "error vs known optimum"


def _max_nfes_label(config: ExperimentConfig) -> str:
    """Return a reference-style budget label."""
    if config.max_evaluations > 0:
        return str(config.max_evaluations)
    if config.suite == "cec2017":
        return "suite default (e.g. 10000*D for cec2017)"
    return "suite default"


def _benchmark_backend_for_optimizer(config: ExperimentConfig, optimizer: str) -> str:
    """Return the actual benchmark evaluator backend for one optimizer run."""
    if config.suite == "sphere":
        return "python"
    if config.benchmark_backend == "auto":
        return "python"
    return config.benchmark_backend


def _benchmark_backend_summary(config: ExperimentConfig) -> str:
    """Return a concise backend summary for console/provenance output."""
    actual = {optimizer: _benchmark_backend_for_optimizer(config, optimizer) for optimizer in config.optimizers}
    if len(set(actual.values())) == 1:
        only = next(iter(actual.values()))
        return f"{config.benchmark_backend}->{only}" if config.benchmark_backend == "auto" else only
    pairs = ", ".join(f"{optimizer}:{backend}" for optimizer, backend in actual.items())
    return f"{config.benchmark_backend} ({pairs})"


def _statistics_basis_for_cells(config: ExperimentConfig, cells: list[tuple[int, int]]) -> str:
    """Return the statistics basis for the first resolved run cell."""
    if not cells:
        return "error_vs_optimum"
    func, dim = cells[0]
    return make_problem(
        config.suite,
        int(func),
        int(dim),
        config.max_evaluations,
        benchmark_fp_mode=config.benchmark_fp_mode,
    ).statistics_basis


def _artifact_value(artifact: RunArtifact) -> float:
    """Return the result value in the artifact statistics basis."""
    values = statistic_values(
        np.array([artifact.record.best_fitness], dtype=float),
        optimum=artifact.optimum,
        target_error=artifact.target_error,
        statistics_basis=artifact.statistics_basis,
    )
    return float(values[0])


def _stats_by_dimension(
    artifacts: list[RunArtifact],
    cell_wall_seconds: dict[tuple[int, int], float] | None = None,
) -> dict[int, dict[int, tuple[Any, float, list[RunArtifact]]]]:
    """Return summary statistics, per-function wall time, and artifacts by dim/function.

    ``Time/s`` is the wall-clock time for each (function, dimension) batch of runs
    (matching the reference ``cell_timer = tic`` row timing), not the sum of the
    per-run times. When ``cell_wall_seconds`` is absent it falls back to the sum.
    """
    grouped: dict[int, dict[int, list[RunArtifact]]] = {}
    for artifact in artifacts:
        grouped.setdefault(artifact.record.dimension, {}).setdefault(
            artifact.record.function,
            [],
        ).append(artifact)

    summarized: dict[int, dict[int, tuple[Any, float, list[RunArtifact]]]] = {}
    for dim, by_func in grouped.items():
        summarized[dim] = {}
        for func, group in sorted(by_func.items()):
            values = np.array([_artifact_value(item) for item in group], dtype=float)
            if cell_wall_seconds is not None and (func, dim) in cell_wall_seconds:
                total_time = float(cell_wall_seconds[(func, dim)])
            else:
                total_time = float(sum(item.record.runtime_seconds for item in group))
            summarized[dim][func] = (summarize(values), total_time, group)
    return summarized


def _stats_by_function(
    artifacts: list[RunArtifact],
    cell_wall_seconds: dict[tuple[int, int], float] | None = None,
) -> dict[int, tuple[Any, float, list[RunArtifact]]]:
    """Return summary statistics grouped by function across native dimensions."""
    grouped: dict[int, list[RunArtifact]] = {}
    for artifact in artifacts:
        grouped.setdefault(artifact.record.function, []).append(artifact)

    summarized: dict[int, tuple[Any, float, list[RunArtifact]]] = {}
    for func, group in sorted(grouped.items()):
        values = np.array([_artifact_value(item) for item in group], dtype=float)
        fallback_time_by_cell: dict[tuple[int, int], float] = {}
        for item in group:
            cell_key = (int(item.record.function), int(item.record.dimension))
            fallback_time_by_cell[cell_key] = fallback_time_by_cell.get(cell_key, 0.0) + float(
                item.record.runtime_seconds
            )
        total_time = sum(
            float(cell_wall_seconds.get(cell_key, fallback_time)) if cell_wall_seconds else fallback_time
            for cell_key, fallback_time in fallback_time_by_cell.items()
        )
        summarized[func] = (summarize(values), total_time, group)
    return summarized


def _config_lines(
    config: ExperimentConfig,
    optimizer: str,
    funcs_to_run: set[int],
    dims_to_run: set[int],
    output_dir: Path,
    project_root: Path,
    statistics_basis: str,
) -> list[str]:
    """Return detailed configuration lines matching the reference console style."""
    excluded = _excluded_functions(config, funcs_to_run)
    return [
        "",
        "========================================================================",
        "DETAILED CONFIGURATION",
        "========================================================================",
        f"optimizer       : {optimizer}",
        f"suite           : {config.suite.upper()}",
        f"funcs_to_run    : {_format_number_list(funcs_to_run)}",
        f"excluded        : {excluded[0] if len(excluded) == 1 else _format_number_list(excluded)}",
        f"dimensions      : {_format_dimension_label(dims_to_run)}",
        f"runs            : {config.runs}",
        f"base_seed       : {config.seed}",
        f"seed_policy     : {config.seed_policy}",
        f"rand_generator  : {config.rand_generator}",
        f"use_parallel    : {str(config.parallel).lower()}",
        f"parallel_backend: {config.parallel_backend}",
        f"workers         : {config.workers} ({'auto' if config.workers_auto else 'explicit'})",
        f"numba_threads   : {config.numba_threads if config.numba_threads > 0 else 'auto'}",
        f"generation_logs : {str(config.generation_logs).lower()}",
        f"graphs          : {str(config.convergence_graphs).lower()}",
        f"benchmark_fp    : {config.benchmark_fp_mode}",
        f"benchmark_backend: {_benchmark_backend_for_optimizer(config, optimizer)}"
        f" (requested={config.benchmark_backend})",
        f"max_nfes        : {_max_nfes_label(config)}",
        f"statistics      : {_statistics_label(statistics_basis)}",
        f"project_root    : {project_root.name}",
        f"output_dir      : {output_dir}",
        "========================================================================",
        "",
    ]


def _optimizer_options_line(config: ExperimentConfig, optimizer: str) -> str:
    """Return a concise optimizer-parameter line for the console table header."""
    options = config.optimizer_options
    if optimizer == "gsk":
        return (
            f"Pop={int(options.get('np', 100))}  "
            f"KF={float(options.get('kf', options.get('KF', 0.5))):g} "
            f"KR={float(options.get('kr', options.get('KR', 0.9))):g} "
            f"K={int(options.get('k', options.get('K', 10)))} "
            f"P={float(options.get('p', options.get('P', 0.1))):g}"
        )
    if optimizer in {"agsk", "apgsk", "fdb-agsk"}:
        return (
            f"NP_init={int(options.get('np_init', 100))}  "
            f"min_pop_size={int(options.get('min_pop_size', 12))}"
        )
    if optimizer == "dt-gsk":
        # DT-GSK sizes its initial population from the problem dimension
        # (``_dt_core``: ``pop_size`` None -> ``np_init_mult * dim``), so it
        # carries no ``np`` option at all. The shared fallback below reads the
        # dict default and therefore announced ``Pop=100`` -- a value no DT-GSK
        # run has ever used -- in the console banner of every campaign.
        return f"NP_init={int(options.get('np_init_mult', 5))}D"
    return f"Pop={int(options.get('np', 100))}"


def _dimension_summary_lines(
    config: ExperimentConfig,
    optimizer: str,
    dim: int,
    by_func: dict[int, tuple[Any, float, list[RunArtifact]]],
) -> list[str]:
    """Return the main per-dimension summary table."""
    first_group = next(iter(by_func.values()))[2]
    first_artifact = first_group[0]
    rows = _dimension_summary_header_lines(
        config,
        optimizer,
        dim,
        function_count=len(by_func),
        runs=config.runs,
        first_artifact=first_artifact,
    )
    for func, (stats, total_time, _group) in sorted(by_func.items()):
        rows.append(_dimension_summary_row(func, stats, total_time))
    rows.extend(_dimension_summary_footer_lines(by_func))
    return rows


def _native_function_summary_lines(
    config: ExperimentConfig,
    optimizer: str,
    by_func: dict[int, tuple[Any, float, list[RunArtifact]]],
) -> list[str]:
    """Return one CEC2011-style native-dimension summary table."""
    first_group = next(iter(by_func.values()))[2]
    rows = _native_function_summary_header_lines(
        config,
        optimizer,
        function_count=len(by_func),
        runs=config.runs,
        first_artifact=first_group[0],
    )
    for func, (stats, total_time, _group) in sorted(by_func.items()):
        rows.append(_dimension_summary_row(func, stats, total_time))
    rows.extend(_dimension_summary_footer_lines(by_func))
    return rows


def _dimension_summary_header_lines(
    config: ExperimentConfig,
    optimizer: str,
    dim: int,
    *,
    function_count: int,
    runs: int,
    first_artifact: RunArtifact,
) -> list[str]:
    """Return per-dimension summary table heading lines."""
    problem = make_problem(
        config.suite,
        first_artifact.record.function,
        dim,
        config.max_evaluations,
        benchmark_fp_mode=config.benchmark_fp_mode,
    )
    budget = int(first_artifact.max_nfes)
    lb = float(np.min(problem.lb))
    ub = float(np.max(problem.ub))
    target = float(first_artifact.target_error)
    target_text = "nan" if math.isnan(target) else f"{target:g}"
    return [
        "+----------------------------------------------------------+",
        f"| {optimizer} - {config.suite.upper()} - D={dim:<29}|",
        "+----------------------------------------------------------+",
        f"| {function_count} functions x {runs} runs | Budget: {budget:,} NFEs".ljust(59) + "|",
        f"| {_optimizer_options_line(config, optimizer)}".ljust(59) + "|",
        f"| Bounds: ({lb:.1f}, {ub:.1f})   Target error: {target_text}".ljust(59) + "|",
        "+----------------------------------------------------------+",
        "",
        "+--------+--------------+--------------+--------------+--------------+--------------+-------------+",
        "|  Func  |     Best     |    Median    |     Mean     |    Worst     |      SD      |   Time/s    |",
        "+--------+--------------+--------------+--------------+--------------+--------------+-------------+",
    ]


def _native_function_summary_header_lines(
    config: ExperimentConfig,
    optimizer: str,
    *,
    function_count: int,
    runs: int,
    first_artifact: RunArtifact,
) -> list[str]:
    """Return one native-dimension suite table header for CEC2011."""
    budget = int(first_artifact.max_nfes)
    basis = _statistics_label(first_artifact.statistics_basis)
    return [
        "+----------------------------------------------------------+",
        f"| {optimizer} - {config.suite.upper()} - native dimensions".ljust(59) + "|",
        "+----------------------------------------------------------+",
        f"| {function_count} functions x {runs} runs | Budget: {budget:,} NFEs".ljust(59) + "|",
        f"| {_optimizer_options_line(config, optimizer)}".ljust(59) + "|",
        f"| Statistics: {basis}".ljust(59) + "|",
        "+----------------------------------------------------------+",
        "",
        "+--------+--------------+--------------+--------------+--------------+--------------+-------------+",
        "|  Func  |     Best     |    Median    |     Mean     |    Worst     |      SD      |   Time/s    |",
        "+--------+--------------+--------------+--------------+--------------+--------------+-------------+",
    ]


def _dimension_summary_row(func: int, stats: Any, total_time: float) -> str:
    """Return one per-function summary row for a completed run batch."""
    return (
        "|  "
        f"F{func:02d}   |"
        f"  {format_scientific(stats.best, 2):>10}  |"
        f"  {format_scientific(stats.median, 2):>10}  |"
        f"  {format_scientific(stats.mean, 2):>10}  |"
        f"  {format_scientific(stats.worst, 2):>10}  |"
        f"  {format_scientific(stats.sd, 2):>10}  |"
        f"{total_time:10.1f}s  |"
    )


def _dimension_summary_footer_lines(
    by_func: dict[int, tuple[Any, float, list[RunArtifact]]],
) -> list[str]:
    """Return per-dimension summary table footer lines."""
    return [
        "+--------+--------------+--------------+--------------+--------------+--------------+-------------+",
        "",
        f"[OK] Updated {len(by_func)} function(s); wrote {sum(len(group) for _, _, group in by_func.values())} new run(s)",
        "",
    ]


def _comparison_lines(
    config: ExperimentConfig,
    optimizer: str,
    dim: int | None,
    by_func: dict[int, tuple[Any, float, list[RunArtifact]]],
) -> list[str]:
    """Return a reference-mean comparison table when matching references exist."""
    ref_table = load_reference_table(config.reference_root, optimizer, config.suite, dim)
    if ref_table is None:
        return []
    title_suffix = f" (D={dim})" if dim is not None else " (native)"
    title = f"Mean Comparison: {optimizer.upper()} vs {optimizer}_{config.suite}{title_suffix}"
    rows = [
        "+==============================================================================+",
        f"|{title:^78}|",
        "+==============================================================================+",
        "  Zero threshold: 1e-08;  near-solved (both < 1) shown as ~ and counted =",
        "",
        "+--------+--------------------+--------------+--------------+--------------+----------+",
        "|  Func  |"
        + f"{'Reference ' + optimizer.upper() + ' Mean':^20}"
        + "|"
        + f"{optimizer + ' Mean':^14}"
        + "|Delta(New-Old)|  % Improve   |  Status  |",
        "+--------+--------------------+--------------+--------------+--------------+----------+",
    ]
    improved = same = worse = 0
    for func, (stats, _total_time, _group) in sorted(by_func.items()):
        ref_cell = ref_table.cells.get(func)
        ref_mean = None if ref_cell is None else ref_cell.stats.get("Mean")
        if ref_mean is None:
            rows.append(
                "|  "
                f"F{func:02d}   |"
                f"{'missing':^20}|"
                f"{format_scientific(stats.mean, 2):^14}|"
                f"{'-':^14}|"
                f"{'-':^14}|"
                f"{'?':^10}|"
            )
            continue
        delta = float(stats.mean) - float(ref_mean)
        near_same = abs(delta) <= max(1e-8, 1e-9 * max(1.0, abs(float(ref_mean))))
        if near_same or (abs(float(ref_mean)) < 1 and abs(float(stats.mean)) < 1):
            status = "="
            same += 1
        elif delta < 0:
            status = "^"
            improved += 1
        else:
            status = "v"
            worse += 1
        pct = "-" if abs(float(ref_mean)) < 1e-12 else f"{(-delta / abs(float(ref_mean)) * 100):.1f}%"
        rows.append(
            "|  "
            f"F{func:02d}   |"
            f"{format_scientific(float(ref_mean), 2):^20}|"
            f"{format_scientific(stats.mean, 2):^14}|"
            f"{format_scientific(delta, 2):^14}|"
            f"{pct:^14}|"
            f"{status:^10}|"
        )
    rows.extend(
        [
            "+--------+--------------------+--------------+--------------+--------------+----------+",
            "",
            f"  Summary: ^ Improved: {improved}  = Same: {same}  v Worse: {worse}",
            "",
        ]
    )
    return rows


def _write_text(path: Path, lines: list[str]) -> None:
    """Write text lines with UTF-8 encoding."""
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


_SKIPPED_RUN_FIELDS = ("optimizer", "suite", "function", "dimension", "run", "seed", "reason", "traceback")


def _write_skipped_runs(path: Path, skipped_cells: list[dict[str, Any]]) -> None:
    """Persist every failed run with its exception text (full rewrite per call)."""
    import csv

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=_SKIPPED_RUN_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for cell in skipped_cells:
            writer.writerow(cell)


def _run_log_lines(
    optimizer: str,
    suite: str,
    dim: int,
    by_func: dict[int, tuple[Any, float, list[RunArtifact]]],
    timestamp: str,
) -> list[str]:
    """Return a detailed per-run log."""
    lines = [
        "=" * 110,
        f"DETAILED PER-RUN LOG   {optimizer.upper()}   {suite.upper()}   D{dim}",
        f"runs per function : {len(next(iter(by_func.values()))[2]) if by_func else 0}",
        f"functions         : {_format_number_list(sorted(by_func.keys()))}",
        f"statistics basis  : {_statistics_label(next(iter(by_func.values()))[2][0].statistics_basis) if by_func else ''}",
        f"generated         : {timestamp}",
        "=" * 110,
        "",
    ]
    for func, (_stats, _time, group) in sorted(by_func.items()):
        first = group[0]
        target = "nan" if math.isnan(first.target_error) else f"{first.target_error:g}"
        lines.append(
            f"----- F{func}  D{dim}  ({len(group)} runs)  optimum={first.optimum:g}  target_error={target} -----"
        )
        lines.append(
            f"{'Run':<6} {'Seed':<13} {'Best_Fitness':<24} {'Error':<24} {'NFEs':<13} {'Termination':<23} {'Runtime_s':<10}"
        )
        for artifact in sorted(group, key=lambda item: item.record.run):
            record = artifact.record
            lines.append(
                f"{record.run:<6} {record.seed:<13} "
                f"{record.best_fitness:<24.16e} {record.error:<24.16e} "
                f"{record.nfes:<13} {record.termination:<23} {record.runtime_seconds:<10.4f}"
            )
        lines.append("")
    return lines


def _native_run_log_lines(
    optimizer: str,
    suite: str,
    by_func: dict[int, tuple[Any, float, list[RunArtifact]]],
    timestamp: str,
) -> list[str]:
    """Return a detailed per-run log for native-dimension CEC2011 functions."""
    lines = [
        "=" * 110,
        f"DETAILED PER-RUN LOG   {optimizer.upper()}   {suite.upper()}   NATIVE DIMENSIONS",
        f"runs per function : {len(next(iter(by_func.values()))[2]) if by_func else 0}",
        f"functions         : {_format_number_list(sorted(by_func.keys()))}",
        f"statistics basis  : {_statistics_label(next(iter(by_func.values()))[2][0].statistics_basis) if by_func else ''}",
        f"generated         : {timestamp}",
        "=" * 110,
        "",
    ]
    for func, (_stats, _time, group) in sorted(by_func.items()):
        first = group[0]
        target = "nan" if math.isnan(first.target_error) else f"{first.target_error:g}"
        lines.append(
            f"----- F{func}  D{first.record.dimension}  ({len(group)} runs)  "
            f"optimum={first.optimum:g}  target_error={target} -----"
        )
        lines.append(
            f"{'Run':<6} {'Seed':<13} {'Best_Fitness':<24} {'Error':<24} {'NFEs':<13} {'Termination':<23} {'Runtime_s':<10}"
        )
        for artifact in sorted(group, key=lambda item: item.record.run):
            record = artifact.record
            lines.append(
                f"{record.run:<6} {record.seed:<13} "
                f"{record.best_fitness:<24.16e} {record.error:<24.16e} "
                f"{record.nfes:<13} {record.termination:<23} {record.runtime_seconds:<10.4f}"
            )
        lines.append("")
    return lines


def _write_compatibility_json(
    summary_dir: Path,
    config: ExperimentConfig,
    optimizer: str,
    funcs_to_run: set[int],
    dims_to_run: set[int],
    statistics_basis: str,
) -> None:
    """Write run_config.json and phase0_protocol.json compatibility artifacts."""
    excluded = _excluded_functions(config, funcs_to_run)
    seed_scheme = _SEED_SCHEME_TEXT
    dims_value: int | list[int] = sorted(dims_to_run)[0] if len(dims_to_run) == 1 else sorted(dims_to_run)
    run_config = {
        "alg_name": optimizer,
        "suite": config.suite.upper(),
        "base_seed": config.seed,
        "seed_policy": config.seed_policy,
        "seed_scheme": seed_scheme,
        "rand_generator": config.rand_generator,
        "initial_population_policy": "runner-generated shared X0 from get_cec_seed(base_seed,dim,func,run); post-initialization rng state restored inside optimizer",
        "stride_run": 1_000_037,
        "dim_stride": 1_000_003,
        "func_stride": 1_000_033,
        "runs": config.runs,
        "dims": dims_value,
        "funcs": list(range(1, 31)) if config.suite == "cec2017" else sorted(funcs_to_run),
        "exclude_funcs": excluded[0] if len(excluded) == 1 else excluded,
        "funcs_to_run": sorted(funcs_to_run),
        "max_nfes_override": config.max_evaluations,
        "statistics_basis": statistics_basis,
        "report_zero_tol": 1e-8,
        "benchmark_fp_mode": config.benchmark_fp_mode,
        "benchmark_backend": _benchmark_backend_for_optimizer(config, optimizer),
        "benchmark_backend_requested": config.benchmark_backend,
        "generation_logs": config.generation_logs,
        "convergence_graphs": config.convergence_graphs,
        "verbose": False,
        "use_parallel": config.parallel,
        "optimizer_options": config.optimizer_options,
    }
    run_config.update(config.optimizer_options)
    run_config.update(_run_config_optimizer_params(optimizer, config.optimizer_options))
    phase0 = {
        "base_seed": config.seed,
        "stride_run": 1_000_037,
        "dim_stride": 1_000_003,
        "func_stride": 1_000_033,
        "runs": config.runs,
        "dims": dims_value,
        "suite": config.suite.upper(),
        "excluded": excluded[0] if len(excluded) == 1 else excluded,
        "funcs_to_run": sorted(funcs_to_run),
        "seed_policy": {
            "scheme": seed_scheme,
            "run_id_origin": 1,
            "base_seed_field": "base_seed",
            "stride_field": "stride_run",
        },
        "rand_generator": config.rand_generator,
        "benchmark_fp_mode": config.benchmark_fp_mode,
        "benchmark_backend": _benchmark_backend_for_optimizer(config, optimizer),
        "benchmark_backend_requested": config.benchmark_backend,
        "generation_logs": config.generation_logs,
        "convergence_graphs": config.convergence_graphs,
        "initial_population_policy": run_config["initial_population_policy"],
        "optimizer_options": config.optimizer_options,
        "smoke": config.max_evaluations > 0 or config.runs < 25,
    }
    (summary_dir / "run_config.json").write_text(
        json.dumps(run_config, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    (summary_dir / "phase0_protocol.json").write_text(
        json.dumps(phase0, indent=2, sort_keys=False),
        encoding="utf-8",
    )


def _task_progress_line(
    optimizer: str,
    completed: int,
    total: int,
    task: RunTask,
    outcome: Any,
) -> str:
    """Return one compact completed-task progress line."""
    percent = 100.0 * completed / max(1, total)
    prefix = (
        f"[progress] {optimizer.upper()} {completed}/{total} ({percent:5.1f}%) "
        f"F{task.function:02d} D{task.dimension} run {task.run}"
    )
    if outcome.error is not None:
        return f"{prefix} failed: {outcome.error}"
    artifact = outcome.result
    if isinstance(artifact, RunArtifact):
        record = artifact.record
        value_label = "best" if artifact.statistics_basis == "raw_objective" else "error"
        return (
            f"{prefix} seed={record.seed} {value_label}={format_scientific(_artifact_value(artifact), 2)} "
            f"nfes={record.nfes} time={record.runtime_seconds:.1f}s"
        )
    return f"{prefix} done"


def _emit_compatibility_outputs(
    config: ExperimentConfig,
    optimizer: str,
    dirs: dict[str, Path],
    artifacts: list[RunArtifact],
    project_root: Path,
    *,
    cell_wall_seconds: dict[tuple[int, int], float] | None = None,
    emit_config_lines: bool = True,
    emit_dimension_lines: bool = True,
) -> None:
    """Write and print reference-style summary artifacts."""
    if not artifacts:
        return
    funcs_to_run = {artifact.record.function for artifact in artifacts}
    dims_to_run = {artifact.record.dimension for artifact in artifacts}
    statistics_basis = artifacts[0].statistics_basis
    by_dimension = _stats_by_dimension(artifacts, cell_wall_seconds)
    timestamp = time.strftime("%Y-%m-%d_%H.%M.%S")

    _write_compatibility_json(
        dirs["summary"],
        config,
        optimizer,
        funcs_to_run,
        dims_to_run,
        statistics_basis,
    )

    config_lines = _config_lines(
        config,
        optimizer,
        funcs_to_run,
        dims_to_run,
        dirs["root"],
        project_root,
        statistics_basis,
    )
    if emit_config_lines:
        for line in config_lines:
            _log_console(config.console_log, line)

    if config.suite == "cec2011":
        by_func_native = _stats_by_function(artifacts, cell_wall_seconds)
        summary_lines = list(config_lines)
        native_lines = _native_function_summary_lines(config, optimizer, by_func_native)
        comparison = _comparison_lines(config, optimizer, None, by_func_native)
        summary_lines.extend(native_lines)
        summary_lines.extend(comparison)
        summary_path = dirs["summary"] / f"{optimizer}_{config.suite}_log_{timestamp}.txt"
        runs_path = dirs["summary"] / f"{optimizer}_{config.suite}_runs_log_{timestamp}.txt"
        _write_text(summary_path, summary_lines)
        _write_text(runs_path, _native_run_log_lines(optimizer, config.suite, by_func_native, timestamp))
        if emit_dimension_lines:
            for line in native_lines + comparison:
                _log_console(config.console_log, line)
    else:
        for dim, by_func in sorted(by_dimension.items()):
            summary_lines = list(config_lines)
            dimension_lines = _dimension_summary_lines(config, optimizer, dim, by_func)
            comparison = _comparison_lines(config, optimizer, dim, by_func)
            summary_lines.extend(dimension_lines)
            summary_lines.extend(comparison)
            summary_path = dirs["summary"] / f"{optimizer}_D{dim}_log_{timestamp}.txt"
            runs_path = dirs["summary"] / f"{optimizer}_D{dim}_runs_log_{timestamp}.txt"
            _write_text(summary_path, summary_lines)
            _write_text(runs_path, _run_log_lines(optimizer, config.suite, dim, by_func, timestamp))
            if emit_dimension_lines:
                for line in dimension_lines + comparison:
                    _log_console(config.console_log, line)

    if config.convergence_graphs:
        graph_paths = {
            dirs["graphs"] / f"Figure_F{artifact.record.function}_D{artifact.record.dimension}.png"
            for artifact in artifacts
        }
        graph_count = sum(1 for path in graph_paths if path.exists())
        _log_console(
            config.console_log,
            f"Saved {graph_count} convergence graph(s) to {dirs['graphs']}",
        )
    else:
        _log_console(
            config.console_log,
            f"Convergence graph generation disabled; curve CSVs saved to {dirs['curves']}",
        )
    _log_console(config.console_log, f"run_experiment: wrote {dirs['root']}")


_PROCESS_WORKER_CFG: ExperimentConfig | None = None


def _init_process_worker(
    cfg: ExperimentConfig,
    numba_threads: int,
    expected_fp_sentinel: str | None = None,
) -> None:
    """Per-worker initializer: stash config, cap numba threads, warm JIT once.

    Runs once in each spawned worker process. Capping numba threads to
    ``cores // workers`` keeps total threads (workers x numba) within the core
    budget; the one-time warmup hides JIT compilation from the timed run loop.

    The FP-regime gate below is deliberately OUTSIDE any exception swallowing:
    a worker whose numba import silently failed would run every task in a
    second deterministic floating-point regime (NumPy fallback kernels; see
    ``gsk_family.runners.fp_regime``). Raising here kills the worker at spawn;
    the pool-rebuild logic retries and ultimately runs the cell on the
    parent's already-verified serial backend instead of mixing regimes.
    """
    global _PROCESS_WORKER_CFG
    _PROCESS_WORKER_CFG = cfg
    try:
        import numba

        numba.set_num_threads(max(1, int(numba_threads)))
    except Exception:  # pragma: no cover - handled by the regime gate below
        pass
    ensure_canonical_fp_regime(cfg.suite, expected_sentinel=expected_fp_sentinel)
    try:
        cells = _execution_ordered_cells(cfg, _resolve_cells(cfg))
        if cells:
            warm_benchmark_cells(
                cfg.suite,
                [cells[0]],
                cfg.max_evaluations,
                benchmark_fp_mode=cfg.benchmark_fp_mode,
            )
    except Exception:  # pragma: no cover - warmup is best-effort
        pass


def _process_run_task(task: RunTask) -> RunArtifact:
    """Top-level picklable worker: run one task using the per-process config."""
    cfg = _PROCESS_WORKER_CFG
    if cfg is None:
        raise RuntimeError("Process worker configuration was not initialized.")
    return _run_one(
        cfg,
        task.optimizer,
        int(task.function),
        int(task.dimension),
        int(task.run),
        int(task.seed),
    )


def run_experiment(config: ExperimentConfig | dict[str, Any] | None = None, **kwargs: Any) -> ExperimentRunSummary:
    """Run a configured experiment and write schema-compatible outputs."""
    cfg = _build_config(config, kwargs)
    workers_requested = int(cfg.workers)

    ensure_output_root_allowed(cfg.output_root, cfg.reference_root)
    start = time.perf_counter()
    summary = ExperimentRunSummary()
    project_root = Path.cwd().resolve()

    cells = _execution_ordered_cells(cfg, _resolve_cells(cfg))

    def cell_worker_count(function: int) -> int:
        """Return the process worker count for one benchmark function cell."""
        return effective_worker_count(
            workers_requested,
            suite=cfg.suite,
            function=int(function),
            parallel=cfg.parallel,
            parallel_backend=cfg.parallel_backend,
            workers_auto=cfg.workers_auto,
        )

    worker_cap_functions = sorted({func for func, _dim in cells if cell_worker_count(func) != workers_requested})
    worker_cap_applied = bool(worker_cap_functions)
    worker_cap_workers = min((cell_worker_count(func) for func in worker_cap_functions), default=workers_requested)
    numba_runtime = configure_numba_runtime(
        suite=cfg.suite,
        parallel=cfg.parallel,
        workers=cfg.workers,
        requested_threads=cfg.numba_threads,
    )
    # Canonical FP-regime gate (fail-closed): verifies every kernel module is
    # JIT-active in THIS process (covers the serial and thread backends, which
    # execute in-process) and fingerprints the regime. Worker processes verify
    # against this sentinel in _init_process_worker so a whole campaign runs
    # in one floating-point regime by construction. See gsk_family/runners/
    # fp_regime.py and docs/reference/fp_regime.md.
    fp_regime = ensure_canonical_fp_regime(cfg.suite)
    _log_console(
        cfg.console_log,
        f"\n==================== run_all ({cfg.suite.upper()}) ====================",
    )
    _log_console(
        cfg.console_log,
        (
            f"suite={cfg.suite}  functions={_format_number_list({func for func, _ in cells})}  "
            f"dims={_format_dimension_label({dim for _, dim in cells})}  runs={cfg.runs}  "
            f"seed_policy={cfg.seed_policy}  rng={cfg.rand_generator}  "
            f"fp={cfg.benchmark_fp_mode}  backend={_benchmark_backend_summary(cfg)}  "
            f"parallel={1 if cfg.parallel else 0}"
        ),
    )
    if worker_cap_applied:
        _log_console(
            cfg.console_log,
            (
                f"[parallel] automatic CEC2017 composition cap: "
                f"F{worker_cap_functions[0]:02d}-F{worker_cap_functions[-1]:02d} use "
                f"up to {worker_cap_workers} worker process(es); standard cells use {cfg.workers} "
                "to keep D=10 runs fast while reducing Numba/LLVM memory pressure "
                "(pass --workers N to override)."
            ),
        )
    warmup_cells = _resolve_warmup_cells(cfg, cells)
    if cfg.warmup:
        _log_console(
            cfg.console_log,
            f"[warmup] start scope={cfg.warmup_scope} cells={len(warmup_cells)}",
        )
    warmup_records = (
        warm_benchmark_cells(
            cfg.suite,
            warmup_cells,
            cfg.max_evaluations,
            benchmark_fp_mode=cfg.benchmark_fp_mode,
        )
        if cfg.warmup
        else []
    )
    warmup_json = warmup_records_to_json(warmup_records)
    warmup_seconds_total = float(sum(record.seconds for record in warmup_records))
    if cfg.warmup:
        _log_console(
            cfg.console_log,
            f"[warmup] done cells={len(warmup_records)} seconds={warmup_seconds_total:.3f}",
        )
    # Process backend = true multi-core (no GIL). A single task still runs
    # inline (execute_run_tasks serializes trivial cases), but a requested
    # process backend must NEVER silently drop to the thread pool: two
    # optimizer instances sharing one process raced inside the DT-GSK
    # interaction graph (flaky IndexError in _connected_components,
    # 2026-07-23, cec2013lsgo D905), and the pool-crash recovery below
    # already refuses thread fallback for the same reason. The old
    # ``estimated_tasks > cfg.workers`` heuristic did exactly that silent
    # drop for small campaigns.
    estimated_tasks = len(cfg.optimizers) * len(cells) * cfg.runs
    use_process = (
        cfg.parallel
        and cfg.parallel_backend == "process"
        and estimated_tasks > 1
    )
    worker_numba_threads = int(numba_runtime.get("numba_threads_active") or 1)
    max_pool_rebuilds = 3
    process_executor: ProcessPoolExecutor | None = None
    active_process_workers: int | None = None
    if use_process:
        active_process_workers = cell_worker_count(cells[0][0]) if cells else int(cfg.workers)
        process_executor = ProcessPoolExecutor(
            max_workers=int(active_process_workers),
            mp_context=multiprocessing.get_context("spawn"),
            initializer=_init_process_worker,
            initargs=(cfg, worker_numba_threads, fp_regime["sentinel"]),
        )

    optimizer_total = len(cfg.optimizers)
    for optimizer_index, optimizer in enumerate(cfg.optimizers, start=1):
        _log_console(cfg.console_log, f"\n----- [{optimizer_index}/{optimizer_total}] {optimizer.upper()} -----")
        if optimizer_index == 1:
            if cfg.parallel:
                backend_label = (
                    f"{active_process_workers or cfg.workers} worker process(es) (spawn)"
                    if process_executor is not None
                    else f"Python thread backend with {cfg.workers} worker(s)"
                )
                _log_console(cfg.console_log, "Starting parallel pool ...")
                _log_console(cfg.console_log, f"Parallel pool ready: {backend_label}.")
            _log_console(cfg.console_log, format_numba_runtime_line(numba_runtime))
        optimizer_start = time.perf_counter()
        dirs = ensure_output_dirs(cfg.output_root, optimizer, cfg.suite)
        summary.output_dirs.append(dirs["root"])

        schedule_rows = _current_schedule_rows(cfg, optimizer, cells)
        write_seed_schedule(dirs["summary"] / "seed_schedule.csv", schedule_rows)

        existing_rows = [] if cfg.overwrite else read_existing_per_run(dirs["summary"] / "per_run.csv")
        existing_by_key_seed = _matching_existing_rows(existing_rows)
        all_rows = list(existing_rows)
        artifacts: list[RunArtifact] = []
        skipped_cells: list[dict[str, Any]] = []
        tasks: list[RunTask] = []
        tasks_by_cell: dict[tuple[int, int], list[RunTask]] = {cell: [] for cell in cells}
        skipped_completed_by_cell: dict[tuple[int, int], int] = {}
        skipped_completed_for_optimizer = 0

        for row in schedule_rows:
            cell_key = (int(row.function), int(row.dim))
            key_seed = (row.function, row.dim, row.run, row.seed)
            if key_seed in existing_by_key_seed:
                summary.skipped_completed += 1
                skipped_completed_for_optimizer += 1
                skipped_completed_by_cell[cell_key] = skipped_completed_by_cell.get(cell_key, 0) + 1
                continue
            task = _task_from_schedule_row(optimizer, row)
            tasks.append(task)
            tasks_by_cell.setdefault(cell_key, []).append(task)

        statistics_basis = _statistics_basis_for_cells(cfg, cells)
        for line in _config_lines(
            cfg,
            optimizer,
            {func for func, _ in cells},
            {dim for _, dim in cells},
            dirs["root"],
            project_root,
            statistics_basis,
        ):
            _log_console(cfg.console_log, line)
        if skipped_completed_for_optimizer:
            _log_console(
                cfg.console_log,
                f"[resume] skipped {skipped_completed_for_optimizer} already completed run task(s).",
            )
        if tasks:
            _log_console(
                cfg.console_log,
                (
                    f"Dispatching {len(tasks)} run task(s) for {optimizer.upper()} "
                    f"function by function ..."
                ),
            )
        else:
            _log_console(cfg.console_log, "No new run task(s) to dispatch.")

        def run_task(task: RunTask) -> RunArtifact:
            """Execute a scheduled run task for the active optimizer loop."""
            return _run_one(cfg, task.optimizer, task.function, task.dimension, task.run, task.seed)

        function_count_by_dim: dict[int, int] = {}
        for _func, _dim in cells:
            function_count_by_dim[int(_dim)] = function_count_by_dim.get(int(_dim), 0) + 1
        use_native_function_table = cfg.suite == "cec2011"
        streaming_dim: int | None = None
        streaming_artifacts: list[RunArtifact] = []
        cell_wall_seconds: dict[tuple[int, int], float] = {}
        stats_funcs_to_run = {func for func, _ in cells}
        stats_per_dim_results: list[StatAnalysisResult] = []
        stats_enabled = _statistical_analysis_enabled(cfg, optimizer)

        def close_streaming_table() -> None:
            """Close the live function table for the active dimension or native suite."""
            nonlocal streaming_dim, streaming_artifacts
            if streaming_dim is None or not streaming_artifacts:
                return
            if use_native_function_table:
                by_func = _stats_by_function(streaming_artifacts, cell_wall_seconds)
                comparison_dim: int | None = None
            else:
                by_dimension = _stats_by_dimension(streaming_artifacts, cell_wall_seconds)
                by_func = by_dimension.get(streaming_dim, {})
                comparison_dim = streaming_dim
            for line in _dimension_summary_footer_lines(by_func):
                _log_console(cfg.console_log, line)
            for line in _comparison_lines(cfg, optimizer, comparison_dim, by_func):
                _log_console(cfg.console_log, line)
            # Incremental persistence: flush the per-dimension compatibility
            # outputs (reference-style summary tables, run logs, JSON, and the
            # graph-count notice) as soon as each dimension finishes, so partial
            # results survive an interrupted campaign.
            if artifacts:
                report_label = "CEC2011: writing reports" if use_native_function_table else f"D{streaming_dim}: writing reports"
                _log_finalize_progress(
                    cfg.console_log,
                    optimizer,
                    0,
                    2,
                    report_label,
                )
                _emit_compatibility_outputs(
                    cfg,
                    optimizer,
                    dirs,
                    artifacts,
                    project_root,
                    cell_wall_seconds=cell_wall_seconds,
                    emit_config_lines=False,
                    emit_dimension_lines=False,
                )
                complete_label = (
                    "CEC2011: reports complete"
                    if use_native_function_table
                    else f"D{streaming_dim}: reports complete"
                )
                _log_finalize_progress(
                    cfg.console_log,
                    optimizer,
                    2,
                    2,
                    complete_label,
                )
                # Opt-in per-dimension statistical analysis (gated to advanced
                # GSK-family optimizers). Runs after the per-dim summary CSV has
                # been flushed by the compatibility outputs above so the new
                # summary is on disk for comparison.
                if stats_enabled and not use_native_function_table and streaming_dim is not None:
                    stat_report = _emit_statistical_analysis(
                        cfg, optimizer, dirs, streaming_dim, stats_funcs_to_run
                    )
                    if stat_report is not None:
                        stats_per_dim_results.append(stat_report)
                # CEC2011 uses native per-problem dimensions, so its summary is a
                # single rollup (<opt>_cec2011.csv, 22 problems) rather than a
                # family of per-dim CSVs. Emit ONE Wilcoxon + Friedman panel here
                # (with dim=0 for display) once the rollup is on disk; the
                # >=2-dim cross-dimension block below correctly never fires for
                # this single-panel suite.
                elif stats_enabled and use_native_function_table:
                    stat_report = _emit_statistical_analysis(
                        cfg, optimizer, dirs, 0, stats_funcs_to_run
                    )
                    if stat_report is not None:
                        stats_per_dim_results.append(stat_report)
            streaming_dim = None
            streaming_artifacts = []

        for cell_index, (func, dim) in enumerate(cells, start=1):
            cell_tasks = tasks_by_cell.get((func, dim), [])
            skipped_for_cell = skipped_completed_by_cell.get((func, dim), 0)
            if skipped_for_cell and not cell_tasks:
                _log_console(
                    cfg.console_log,
                    (
                        f"[function] [{cell_index}/{len(cells)}] {optimizer.upper()} "
                        f"D{dim} F{func:02d} already complete; skipped {skipped_for_cell} run(s)."
                    ),
                )
                continue
            if not cell_tasks:
                continue

            cell_workers = cell_worker_count(func)
            if use_process and active_process_workers != cell_workers:
                try:
                    if process_executor is not None:
                        process_executor.shutdown(wait=True, cancel_futures=False)
                except Exception:  # pragma: no cover - best-effort normal pool resize
                    pass
                process_executor = ProcessPoolExecutor(
                    max_workers=int(cell_workers),
                    mp_context=multiprocessing.get_context("spawn"),
                    initializer=_init_process_worker,
                    initargs=(cfg, worker_numba_threads, fp_regime["sentinel"]),
                )
                active_process_workers = cell_workers

            cell_wall_start = time.perf_counter()
            cell_outcomes = []
            pool_rebuilds = 0
            while True:
                try:
                    outcomes = execute_run_tasks(
                        cell_tasks,
                        run_task,
                        parallel=cfg.parallel,
                        workers=cell_workers,
                        progress=None,
                        executor=process_executor,
                        process_fn=_process_run_task if process_executor is not None else None,
                    )
                    pool_broke = process_executor is not None and any(
                        isinstance(outcome.error, BrokenProcessPool) for outcome in outcomes
                    )
                except BrokenProcessPool:
                    outcomes, pool_broke = [], True
                if not pool_broke:
                    cell_outcomes = outcomes
                    break
                # A spawned worker died (intermittent Numba/spawn crash, or out of
                # memory). Tear the pool down. Never fall back to the THREAD backend:
                # parallel Numba kernels can deadlock when called from many Python
                # threads, which turns a recoverable crash into a hang.
                try:
                    if process_executor is not None:
                        process_executor.shutdown(wait=False, cancel_futures=True)
                except Exception:  # pragma: no cover - best-effort teardown of a dead pool
                    pass
                process_executor = None
                active_process_workers = None
                pool_rebuilds += 1
                if use_process and pool_rebuilds <= max_pool_rebuilds:
                    _log_console(
                        cfg.console_log,
                        f"[warn] a worker process died; rebuilding the pool and retrying "
                        f"(attempt {pool_rebuilds}/{max_pool_rebuilds}).",
                    )
                    process_executor = ProcessPoolExecutor(
                        max_workers=int(cell_workers),
                        mp_context=multiprocessing.get_context("spawn"),
                        initializer=_init_process_worker,
                        initargs=(cfg, worker_numba_threads, fp_regime["sentinel"]),
                    )
                    active_process_workers = cell_workers
                    continue
                # Repeated failures (or no process pool): run this cell on the reliable
                # serial backend, then rebuild a fresh pool for the next cell.
                _log_console(
                    cfg.console_log,
                    "[warn] worker pool unstable; running this cell on the serial backend.",
                )
                cell_outcomes = execute_run_tasks(
                    cell_tasks,
                    run_task,
                    parallel=False,
                    workers=1,
                    progress=None,
                    executor=None,
                    process_fn=None,
                )
                if use_process:
                    process_executor = ProcessPoolExecutor(
                        max_workers=int(cell_workers),
                        mp_context=multiprocessing.get_context("spawn"),
                        initializer=_init_process_worker,
                        initargs=(cfg, worker_numba_threads, fp_regime["sentinel"]),
                    )
                    active_process_workers = cell_workers
                break
            cell_wall_seconds[(func, dim)] = time.perf_counter() - cell_wall_start
            cell_artifacts: list[RunArtifact] = []
            cell_failed = 0
            for outcome in cell_outcomes:
                task = outcome.task
                if outcome.error is not None:
                    cell_failed += 1
                    # str(exc) alone can be EMPTY (MemoryError) -- always keep
                    # the type name, and the remote cause a process-pool
                    # future chains onto the re-raised exception.
                    error = outcome.error
                    reason = f"{type(error).__name__}: {error}".strip().rstrip(":")
                    tb_text = outcome.traceback_text or ""
                    # Append the innermost frame so the console line alone
                    # locates the crash; the full traceback goes to the CSV.
                    frames = [ln.strip() for ln in tb_text.splitlines() if ln.strip().startswith("File ")]
                    if frames:
                        reason += f" | at {frames[-1]}"
                    skipped = {
                        "optimizer": task.optimizer,
                        "suite": cfg.suite,
                        "function": task.function,
                        "dimension": task.dimension,
                        "run": task.run,
                        "seed": task.seed,
                        "reason": reason,
                        "traceback": tb_text,
                    }
                    skipped_cells.append(skipped)
                    summary.skipped_cells.append(skipped)
                    continue
                artifact = outcome.result
                if not isinstance(artifact, RunArtifact):
                    raise TypeError("Internal runner task did not return a RunArtifact.")
                cell_artifacts.append(artifact)
                artifacts.append(artifact)
                summary.records.append(artifact.record)
                all_rows.append(run_record_to_row(artifact.record))

            write_per_run(dirs["summary"] / "per_run.csv", all_rows)
            if cell_artifacts:
                if not use_native_function_table and streaming_dim is not None and streaming_dim != dim:
                    close_streaming_table()
                if streaming_dim is None:
                    streaming_dim = dim
                    if use_native_function_table:
                        header_lines = _native_function_summary_header_lines(
                            cfg,
                            optimizer,
                            function_count=len(cells),
                            runs=cfg.runs,
                            first_artifact=cell_artifacts[0],
                        )
                    else:
                        header_lines = _dimension_summary_header_lines(
                            cfg,
                            optimizer,
                            dim,
                            function_count=function_count_by_dim.get(dim, 1),
                            runs=cfg.runs,
                            first_artifact=cell_artifacts[0],
                        )
                    for line in header_lines:
                        _log_console(cfg.console_log, line)
                streaming_artifacts.extend(cell_artifacts)
                values = np.array([_artifact_value(artifact) for artifact in cell_artifacts], dtype=float)
                _log_console(
                    cfg.console_log,
                    _dimension_summary_row(
                        func, summarize(values), cell_wall_seconds.get((func, dim), 0.0)
                    ),
                )
                # Incremental persistence: flush this function's convergence
                # curves, checkpoint logs, and graph immediately, and refresh the
                # summary tables, so an interrupted campaign keeps every completed
                # function on disk instead of only at the end of the run.
                write_curves_and_logs(
                    dirs,
                    optimizer,
                    cell_artifacts,
                    write_generation_logs=cfg.generation_logs,
                    write_convergence_graphs=cfg.convergence_graphs,
                )
                _bank_counts, _bank_values = _bank_from_rows(all_rows, statistics_basis)
                write_summary_tables(
                    dirs["summary"], optimizer, cfg.suite, artifacts,
                    bank_counts=_bank_counts, bank_values=_bank_values,
                )
            elif cell_failed:
                _log_console(
                    cfg.console_log,
                    f"[function] [{cell_index}/{len(cells)}] {optimizer.upper()} D{dim} F{func:02d} failed {cell_failed} run(s).",
                )
            if cell_failed:
                # Surface WHY the runs failed. Before 2026-07-23 the reason
                # strings were collected into skipped_cells and then silently
                # dropped -- an 8-hour campaign died with nothing but "failed
                # 25 run(s)" on the console. Print the distinct reasons (most
                # frequent first) and persist every skipped run to a CSV next
                # to per_run.csv so post-mortems have evidence.
                reason_counts: dict[str, int] = {}
                for cell in skipped_cells:
                    if cell["function"] == func and cell["dimension"] == dim:
                        reason_counts[cell["reason"]] = reason_counts.get(cell["reason"], 0) + 1
                for reason, count in sorted(reason_counts.items(), key=lambda kv: -kv[1]):
                    _log_console(
                        cfg.console_log,
                        f"    [reason x{count}] {reason[:400]}",
                    )
                _write_skipped_runs(dirs["summary"] / "skipped_runs.csv", skipped_cells)
                if process_executor is not None and cell_tasks and cell_failed == len(cell_tasks):
                    # Every run in the cell failed with a clean exception (a
                    # MemoryError does NOT break the pool, so the BrokenProcessPool
                    # recovery above never triggers). Long-lived workers that hit a
                    # resource cliff stay poisoned and would fail every remaining
                    # cell -- exactly how the 2026-07-23 LSGO campaign lost
                    # F09-F15 after F08 died mid-cell. Force a fresh pool for the
                    # next cell; the loop-top resize path shuts this one down.
                    _log_console(
                        cfg.console_log,
                        "[warn] every run in this cell failed; recycling the worker "
                        "pool before the next cell.",
                    )
                    active_process_workers = None

        close_streaming_table()

        # Cross-dimension statistical summary: emitted once per optimizer after
        # all dimensions complete, when at least two dims contributed a panel.
        if stats_enabled and len(stats_per_dim_results) >= 2:
            try:
                cross_dim_text = format_cross_dim_summary(
                    stats_per_dim_results, new_label=optimizer, suite=cfg.suite
                )
                if cross_dim_text:
                    stamp = time.strftime("%Y-%m-%d_%H.%M.%S")
                    cross_dim_path = dirs["summary"] / f"{optimizer}_cross_dim_summary_{stamp}.txt"
                    _write_text(cross_dim_path, cross_dim_text.splitlines())
                    for line in cross_dim_text.splitlines():
                        _log_console(cfg.console_log, line)
            except Exception as exc:  # pragma: no cover - graceful degradation
                _log_console(
                    cfg.console_log,
                    f"[stats] skipped cross-dimension summary for {optimizer.upper()}: {exc}",
                )

        finalize_total = 4 + (1 if cfg.profile else 0)
        finalize_completed = 0
        _log_finalize_progress(
            cfg.console_log,
            optimizer,
            finalize_completed,
            finalize_total,
            "final optimizer files",
        )
        write_per_run(dirs["summary"] / "per_run.csv", all_rows)
        finalize_completed += 1
        _log_finalize_progress(
            cfg.console_log,
            optimizer,
            finalize_completed,
            finalize_total,
            "per-run table saved",
        )
        if artifacts:
            _bank_counts, _bank_values = _bank_from_rows(all_rows, statistics_basis)
            write_summary_tables(
                dirs["summary"], optimizer, cfg.suite, artifacts,
                bank_counts=_bank_counts, bank_values=_bank_values,
            )
        finalize_completed += 1
        _log_finalize_progress(
            cfg.console_log,
            optimizer,
            finalize_completed,
            finalize_total,
            "summary tables refreshed",
        )

        provenance = _runtime_provenance(project_root)
        requested_functions = (
            list(range(1, 31))
            if cfg.suite == "cec2017"
            else sorted({func for func, _ in cells})
        )
        # environment.json is the bank's PRODUCTION provenance: the git commit,
        # statistics basis and wall time of the invocation that actually created
        # runs. A zero-new-runs resume (every scheduled cell already banked)
        # must therefore leave it alone -- rewriting it here would replace the
        # production commit with the resume-time HEAD, null statistics_basis
        # (artifacts is empty), and record the no-op's wall time, silently
        # disabling the known-optimum hard checks in later verification passes
        # (verification reads statistics_basis from this file). Discovered
        # 2026-07-28 while auditing the stopped CEC2020 campaign; see
        # production_deviation_record.md D-8.5. The file is still written when
        # it does not exist yet, so no bank is ever left without provenance.
        environment_path = dirs["summary"] / "environment.json"
        if artifacts or not environment_path.exists():
            write_environment(
                environment_path,
                {
                "optimizer": optimizer,
                "suite": cfg.suite,
                "functions": requested_functions,
                "dimensions_requested": cfg.dimensions,
                "dimensions_run": sorted({dim for _, dim in cells}),
                "runs": cfg.runs,
                "base_seed": cfg.seed,
                "use_parallel": cfg.parallel,
                "rand_generator": cfg.rand_generator,
                "seed_policy": f"{cfg.seed_policy}: {_SEED_SCHEME_TEXT}",
                "initial_population_policy": "runner_supplied_X0"
                if cfg.seed_policy == "unified"
                else "optimizer_reference_draw",
                "max_nfes_override": cfg.max_evaluations,
                "statistics_basis": artifacts[0].statistics_basis if artifacts else None,
                "report_zero_tol": 1e-8,
                "optimizer_options": cfg.optimizer_options,
                "checkpoint_fractions": list(CHECKPOINT_FRACTIONS),
                "data_root": cfg.data_root,
                "benchmark_backend": _benchmark_backend_for_optimizer(cfg, optimizer),
                "benchmark_backend_requested": cfg.benchmark_backend,
                "reference_root": cfg.reference_root,
                "output_dir": str(dirs["root"]),
                "python_version": provenance["python_version"],
                "cpu_cores": provenance["cpu_cores"],
                "computer": provenance["computer"],
                "platform": provenance["platform"],
                "git_commit": provenance["git_commit"],
                "timestamp": provenance["timestamp"],
                "runtime_seconds_total": time.perf_counter() - start,
                "skipped_cells": skipped_cells,
                "optimizer_notes": [],
                "command": (
                    f"python run.py --root . --optimizer {optimizer} --suite {cfg.suite} "
                    f"--runs {cfg.runs} --seed {cfg.seed} --seed-policy {cfg.seed_policy} "
                    f"--rand-generator {cfg.rand_generator} --benchmark-fp-mode {cfg.benchmark_fp_mode} "
                    f"--benchmark-backend {cfg.benchmark_backend}"
                    f"{' --convergence-graphs' if cfg.convergence_graphs else ''}"
                ),
                "parallel_backend": cfg.parallel_backend,
                "workers": cfg.workers,
                "workers_auto": cfg.workers_auto,
                "workers_requested": workers_requested,
                "workers_effective": cfg.workers,
                "worker_cap_applied": worker_cap_applied,
                "worker_cap_functions": worker_cap_functions,
                "worker_cap_workers": worker_cap_workers if worker_cap_applied else None,
                "numba_runtime": numba_runtime,
                "fp_regime": fp_regime,
                "warmup_enabled": cfg.warmup,
                "warmup_scope": cfg.warmup_scope,
                "benchmark_warmup_seconds_total": warmup_seconds_total,
                "profile_enabled": cfg.profile,
                "console_log_enabled": cfg.console_log,
                "generation_logs_enabled": cfg.generation_logs,
                "convergence_graphs_enabled": cfg.convergence_graphs,
                "benchmark_fp_mode": cfg.benchmark_fp_mode,
            },
        )
        finalize_completed += 1
        _log_finalize_progress(
            cfg.console_log,
            optimizer,
            finalize_completed,
            finalize_total,
            "environment metadata saved",
        )
        if cfg.profile:
            write_profile(
                dirs["summary"] / "profile.json",
                {
                    "optimizer": optimizer,
                    "suite": cfg.suite,
                    "parallel": cfg.parallel,
                    "parallel_backend": cfg.parallel_backend,
                    "workers": cfg.workers,
                    "workers_auto": cfg.workers_auto,
                    "workers_requested": workers_requested,
                    "workers_effective": cfg.workers,
                    "worker_cap_applied": worker_cap_applied,
                    "worker_cap_functions": worker_cap_functions,
                    "worker_cap_workers": worker_cap_workers if worker_cap_applied else None,
                    "numba_runtime": numba_runtime,
                    "console_log_enabled": cfg.console_log,
                    "tasks_dispatched": len(tasks),
                    "tasks_completed": len(artifacts),
                    "tasks_skipped_or_failed": len(skipped_cells),
                    "optimizer_wall_seconds": float(time.perf_counter() - optimizer_start),
                    "benchmark_warmup_seconds_total": warmup_seconds_total,
                    "benchmark_warmup": warmup_json,
                    "warmup_scope": cfg.warmup_scope,
                    "generation_logs_enabled": cfg.generation_logs,
                    "convergence_graphs_enabled": cfg.convergence_graphs,
                    "benchmark_fp_mode": cfg.benchmark_fp_mode,
                    "benchmark_backend": _benchmark_backend_for_optimizer(cfg, optimizer),
                    "benchmark_backend_requested": cfg.benchmark_backend,
                    "run_runtime_seconds": [
                        {
                            "function": artifact.record.function,
                            "dimension": artifact.record.dimension,
                            "run": artifact.record.run,
                            "seed": artifact.record.seed,
                            "runtime_seconds": artifact.record.runtime_seconds,
                        }
                        for artifact in artifacts
                    ],
                },
            )
            finalize_completed += 1
            _log_finalize_progress(
                cfg.console_log,
                optimizer,
                finalize_completed,
                finalize_total,
                "profile metadata saved",
            )
        reduced_budget = cfg.max_evaluations > 0 or cfg.runs < 25
        verify_run_directory(
            dirs["root"],
            cfg.reference_root,
            reduced_budget=reduced_budget,
            output_path=dirs["summary"] / "verification.json",
        )
        finalize_completed += 1
        _log_finalize_progress(
            cfg.console_log,
            optimizer,
            finalize_completed,
            finalize_total,
            "verification complete",
        )
        _log_console(
            cfg.console_log,
            f"PASS  {optimizer.upper()}" if not skipped_cells else f"WARN  {optimizer.upper()} failed={len(skipped_cells)}",
        )

    if process_executor is not None:
        process_executor.shutdown(wait=True)

    summary.runtime_seconds_total = time.perf_counter() - start
    _log_console(
        cfg.console_log,
        "\n==================== done ====================",
    )
    _log_console(
        cfg.console_log,
        f"Results under: {Path(cfg.output_root)}",
    )
    return summary
