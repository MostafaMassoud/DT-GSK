"""Experiment configuration parsing and normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import yaml

from gsk_family.benchmark_adapter.protocol import (
    all_function_ids,
    default_dimensions,
    default_function_ids,
    normalize_suite,
)
from gsk_family.benchmark_adapter.factory import normalize_benchmark_backend, normalize_benchmark_fp_mode
from gsk_family.optimizers import OPTIMIZER_IDS
from gsk_family.runners.parallel import default_worker_count
from gsk_family.runners.seed_policy import DEFAULT_BASE_SEED, normalize_optimizer_id, normalize_seed_policy


KNOWN_CONFIG_KEYS = {
    "optimizers",
    "suite",
    "functions",
    "dimensions",
    "runs",
    "seed",
    "seed_policy",
    "rand_generator",
    "max_evaluations",
    "overwrite",
    "parallel",
    "parallel_backend",
    "workers",
    "workers_auto",
    "numba_threads",
    "warmup",
    "warmup_scope",
    "profile",
    "console_log",
    "generation_logs",
    "convergence_graphs",
    "statistical_analysis",
    "benchmark_fp_mode",
    "benchmark_backend",
    "data_root",
    "reference_root",
    "output_root",
    "optimizer_options",
}


@dataclass(frozen=True)
class ExperimentConfig:
    """Normalized experiment request."""

    optimizers: tuple[str, ...]
    suite: str
    functions: tuple[int, ...] | str
    dimensions: tuple[int, ...] | str
    runs: int
    seed: int = DEFAULT_BASE_SEED
    seed_policy: str = "unified"
    rand_generator: str = "threefry"
    max_evaluations: int = 0
    overwrite: bool = False
    parallel: bool = True
    parallel_backend: str = "process"
    workers: int = field(default_factory=default_worker_count)
    workers_auto: bool = True
    numba_threads: int = 0
    warmup: bool = False
    warmup_scope: str = "selected"
    profile: bool = False
    console_log: bool = True
    generation_logs: bool = True
    convergence_graphs: bool = False
    statistical_analysis: bool = False
    benchmark_fp_mode: str = "default"
    benchmark_backend: str = "auto"
    data_root: str = "benchmarks/cec_suite_python"
    reference_root: str = "benchmarks/cec_reference_results"
    output_root: str = "results/_run_all"
    optimizer_options: dict[str, Any] = field(default_factory=dict)


def _as_sequence(value: Any, *, name: str) -> tuple[Any, ...] | str:
    """Normalize a config scalar/list selector into a tuple or keyword."""
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"default", "all", "native"}:
            return normalized
        raise ValueError(f"{name} must be a list or one of default/all/native, got {value!r}.")
    if isinstance(value, (list, tuple)):
        return tuple(value)
    raise ValueError(f"{name} must be a list or string, got {type(value).__name__}.")


def _int_tuple(values: tuple[Any, ...], *, name: str) -> tuple[int, ...]:
    """Validate a tuple of positive integer config values."""
    ints = tuple(int(value) for value in values)
    if any(value <= 0 for value in ints):
        raise ValueError(f"{name} values must be positive integers.")
    return ints


def normalize_functions(suite: str, functions: Any) -> tuple[int, ...]:
    """Resolve config function selection to explicit function IDs."""
    selected = _as_sequence(functions, name="functions")
    if selected in {"default", "native"}:
        return default_function_ids(suite)
    if selected == "all":
        return all_function_ids(suite)
    return _int_tuple(cast("tuple[Any, ...]", selected), name="functions")


def normalize_dimensions(suite: str, dimensions: Any) -> tuple[int, ...] | str:
    """Resolve config dimension selection."""
    selected = _as_sequence(dimensions, name="dimensions")
    defaults = default_dimensions(suite)
    if selected in {"default", "all"}:
        return defaults
    if selected == "native":
        return "native"
    return _int_tuple(cast("tuple[Any, ...]", selected), name="dimensions")


def _normalize_optimizers(value: Any) -> tuple[str, ...]:
    """Normalize and validate one or more optimizer ids."""
    if isinstance(value, str):
        raw = (value,)
    elif isinstance(value, (list, tuple)):
        raw = tuple(value)
    else:
        raise ValueError("optimizers must be a string or list.")
    opts = tuple(normalize_optimizer_id(str(item)) for item in raw)
    unknown = [opt for opt in opts if opt not in OPTIMIZER_IDS]
    if unknown:
        raise ValueError(f"Unsupported optimizer(s): {', '.join(unknown)}.")
    if not opts:
        raise ValueError("At least one optimizer is required.")
    return opts


def config_from_mapping(mapping: dict[str, Any]) -> ExperimentConfig:
    """Build a strict config object from a mapping."""
    unknown = sorted(set(mapping) - KNOWN_CONFIG_KEYS)
    if unknown:
        raise ValueError(f"Unknown config key(s): {', '.join(unknown)}.")
    if "suite" not in mapping:
        raise ValueError("Config key 'suite' is required.")

    suite = normalize_suite(str(mapping["suite"]))
    functions_raw = mapping.get("functions", "default")
    dimensions_raw = mapping.get("dimensions", default_dimensions(suite))
    runs = int(mapping.get("runs", 1))
    if runs <= 0:
        raise ValueError("runs must be positive.")
    workers_auto = bool(mapping.get("workers_auto", "workers" not in mapping))
    workers = int(mapping.get("workers", default_worker_count()))
    if workers <= 0:
        raise ValueError("workers must be positive.")
    numba_threads = int(mapping.get("numba_threads", 0))
    if numba_threads < 0:
        raise ValueError("numba_threads must be >= 0.")
    parallel_backend = str(mapping.get("parallel_backend", "process")).strip().lower()
    if parallel_backend not in {"thread", "process"}:
        raise ValueError("parallel_backend must be 'thread' or 'process'.")
    warmup_scope = str(mapping.get("warmup_scope", "selected")).strip().lower()
    if warmup_scope not in {"selected", "suite"}:
        raise ValueError("warmup_scope must be 'selected' or 'suite'.")

    return ExperimentConfig(
        optimizers=_normalize_optimizers(mapping.get("optimizers", ("gsk",))),
        suite=suite,
        functions=normalize_functions(suite, functions_raw),
        dimensions=normalize_dimensions(suite, dimensions_raw),
        runs=runs,
        seed=int(mapping.get("seed", DEFAULT_BASE_SEED)),
        seed_policy=normalize_seed_policy(mapping.get("seed_policy", "unified")),
        rand_generator=str(mapping.get("rand_generator", "threefry")),
        max_evaluations=int(mapping.get("max_evaluations", 0)),
        overwrite=bool(mapping.get("overwrite", False)),
        parallel=bool(mapping.get("parallel", True)),
        parallel_backend=parallel_backend,  # default "process": true multi-core (no GIL)
        workers=workers,
        workers_auto=workers_auto,
        numba_threads=numba_threads,
        warmup=bool(mapping.get("warmup", False)),
        warmup_scope=warmup_scope,
        profile=bool(mapping.get("profile", False)),
        console_log=bool(mapping.get("console_log", True)),
        generation_logs=bool(mapping.get("generation_logs", True)),
        convergence_graphs=bool(mapping.get("convergence_graphs", False)),
        statistical_analysis=bool(mapping.get("statistical_analysis", False)),
        benchmark_fp_mode=normalize_benchmark_fp_mode(mapping.get("benchmark_fp_mode", "default")),
        benchmark_backend=_normalize_config_benchmark_backend(mapping.get("benchmark_backend", "auto")),
        data_root=str(mapping.get("data_root", "benchmarks/cec_suite_python")),
        reference_root=str(mapping.get("reference_root", "benchmarks/cec_reference_results")),
        output_root=str(mapping.get("output_root", "results/_run_all")),
        optimizer_options=dict(mapping.get("optimizer_options", {}) or {}),
    )


def _normalize_config_benchmark_backend(value: Any) -> str:
    """Normalize the config-level benchmark backend selector."""
    normalized = str(value).strip().lower() if value is not None else "auto"
    if normalized == "auto":
        return normalized
    return normalize_benchmark_backend(normalized)


def load_config(path: str | Path) -> ExperimentConfig:
    """Load and validate a strict YAML experiment config."""
    config_path = Path(path)
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Config {config_path} must contain a YAML mapping.")
    return config_from_mapping(data)
