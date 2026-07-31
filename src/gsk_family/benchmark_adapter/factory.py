"""Benchmark problem factory for the bundled CEC suites."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

# CEC suite data modules are imported lazily inside make_problem() so each
# worker process only loads the data blobs for the suite it actually runs.
# Importing every suite here multiplied per-process memory roughly 5x and could
# exhaust RAM (MemoryError) when many process-pool workers spawn at once.

from gsk_family.benchmark_adapter.problem import (
    BenchmarkProblem,
    as_fitness_vector,
    as_population,
)
from gsk_family.benchmark_adapter.protocol import (
    STAT_ERROR,
    STAT_RAW,
    default_function_ids,
    normalize_suite,
    suite_protocol,
    validate_dimension,
    validate_function_id,
)


CEC2017_DIMS = (10, 30, 50, 100)
CEC2020_DIMS = (5, 10, 15, 20)

#: Cells the CEC2020 PROTOCOL does not define, as opposed to cells whose data we
#: happen to lack. Yue, Price, Suganthan et al., Technical Report 201911 (Nov 2019),
#: Section 2.1 "Experimental Setting": "For F1-F5 and F8-F10 D = 5, 10, 15, 20; for
#: F6 and F7, D = 10, 15, 20." F6 and F7 are therefore undefined at D = 5 and must
#: not be run there -- results for them would not correspond to any competition cell.
#: Source: reference_papers/yue2020cec2020.pdf.
CEC2020_PROTOCOL_EXCLUDED_CELLS = frozenset({(6, 5), (7, 5)})

#: Cells refused for lack of verification. EMPTY since 2026-07-26: F1/F8 at
#: D5/D15 -- refused from the suite's beginning because the official data
#: distribution ships no shuffle_data_<id> availability-marker files for ids
#: 1/22 at those dims, so the MEX-faithful C++ loader could not construct them
#: and no ground truth existed -- were validated against the in-repo C++ oracle
#: (built with dummy markers, output proven bit-identical under two different
#: marker contents since ids 1/22 never consume shuffle). All four agreed with
#: this Python suite to worst rel 1.258e-15, three orders inside the committed
#: rel=1e-12 criterion, with the trusted D10/D20 cells as matching controls.
#: Pinned by tests/regression/test_cec2020_restored_cells.py. The mechanism is
#: kept for any future genuinely-unverified cell.
CEC2020_UNAVAILABLE_CELLS: frozenset[tuple[int, int]] = frozenset()
CEC2020_BUDGETS = {
    5: 50_000,
    10: 1_000_000,
    15: 3_000_000,
    20: 10_000_000,
}
BENCHMARK_FP_MODES = ("default", "strict")
BENCHMARK_BACKENDS = ("python",)


def normalize_benchmark_fp_mode(mode: str | None) -> str:
    """Normalize the benchmark floating-point evaluation mode."""
    if mode is None or str(mode).strip() == "":
        return "default"
    normalized = str(mode).strip().lower()
    if normalized not in BENCHMARK_FP_MODES:
        raise ValueError(
            f"benchmark_fp_mode must be one of {BENCHMARK_FP_MODES}, got {mode!r}."
        )
    return normalized


def normalize_benchmark_backend(backend: str | None) -> str:
    """Normalize the benchmark evaluator backend."""
    if backend is None or str(backend).strip() == "":
        return "python"
    normalized = str(backend).strip().lower()
    if normalized not in BENCHMARK_BACKENDS:
        raise ValueError(f"benchmark_backend must be one of {BENCHMARK_BACKENDS}, got {backend!r}.")
    return normalized


def _max_nfes(default: int, override: int | None) -> int:
    """Return the active evaluation budget after applying an optional override."""
    if override is None or int(override) == 0:
        return int(default)
    override_int = int(override)
    if override_int < 0:
        raise ValueError(f"max_nfes_override must be >= 0, got {override}.")
    return override_int


def _copy_bounds(bounds: tuple[Any, Any], dim: int) -> tuple[np.ndarray, np.ndarray]:
    """Return defensive one-dimensional lower and upper bound arrays."""
    lower, upper = bounds
    lb = np.asarray(lower, dtype=np.float64)
    ub = np.asarray(upper, dtype=np.float64)
    if lb.ndim == 0:
        lb = np.full(dim, float(lb), dtype=np.float64)
    if ub.ndim == 0:
        ub = np.full(dim, float(ub), dtype=np.float64)
    lb = lb.reshape(-1).copy()
    ub = ub.reshape(-1).copy()
    if lb.shape != (dim,) or ub.shape != (dim,):
        raise ValueError(f"Bounds must have shape ({dim},), got {lb.shape} and {ub.shape}.")
    return lb, ub


def _benchmark_evaluator(
    func: Callable[[object, object], object],
    suite: str,
    func_id: int,
    dim: int,
    *,
    benchmark_fp_mode: str = "default",
    serial_kernels: bool = False,
) -> Callable[[np.ndarray], np.ndarray]:
    """Wrap a suite evaluator with population and fitness shape validation.

    ``serial_kernels`` routes this problem's kernel calls to the suite's
    ``parallel=False`` twins, removing numba's per-launch workqueue tax (paid on
    every ``parallel=True`` call even at one thread). **Opt-in, default off**:
    the default path is byte-for-byte untouched, which is what keeps the
    FP-regime integrity sentinel invariant by construction.

    On cec2017 the twins are **R2, not bit-identical** (measured: 93.20% of rows
    bitwise, worst 13 ULP, relative <= ~3e-15; divergence tracks ``fastmath``).
    Callers with archived results MUST NOT opt in without a signed refreeze --
    see docs/development/ACCELERATION_CAMPAIGN_PROMPT.md §5.
    """
    fp_mode = normalize_benchmark_fp_mode(benchmark_fp_mode)

    if not serial_kernels:
        def evaluate(population: np.ndarray) -> np.ndarray:
            """Evaluate one population through the wrapped benchmark function."""
            pop = as_population(
                population, dim=dim, suite=suite, func_id=func_id,
                check_finite=False,   # T2: the suite dispatcher repeats this exact scan
            )
            if suite == "cec2017":
                values = func(pop, func_id, fp_mode=fp_mode)
            else:
                values = func(pop, func_id)
            return as_fitness_vector(
                values, expected_rows=pop.shape[0], suite=suite, func_id=func_id
            )

        return evaluate

    # Suites with serial twins, and the fidelity class MEASURED for each by
    # benchmarks/perf/twin_parity.py (2026-07-26, identical inputs to both):
    #   cec2013  100.0000% bitwise, 0 ULP  -> class (a) bit-identical
    #   cec2020  100.0000% bitwise, 0 ULP  -> class (a) bit-identical
    #   cec2017   98.4110% bitwise, 5 ULP  -> class (b) float-reassociation
    # cec2013/cec2020 carry no fastmath anywhere (their _numba.py states it is
    # "intentionally absent across this entire suite"), which is exactly why
    # their twins are bit-identical while cec2017's are not.
    # Default stays OFF for ALL of them: the frozen evidence release was produced
    # on the default path, and not changing what the default does is the cheapest
    # way to keep every released number valid.
    _SERIAL_SUITES = {"cec2017", "cec2013", "cec2020"}
    if suite not in _SERIAL_SUITES:
        raise ValueError(
            f"serial_kernels is not implemented for suite {suite!r}; refusing to "
            "construct a problem that would silently use the default path."
        )
    # Fail closed: if the twins cannot be built, raise at CONSTRUCTION rather
    # than silently evaluating on a different FP path than the caller asked for.
    import importlib

    _ns = importlib.import_module(f"benchmarks.cec_suite_python.{suite}._numba_serial")
    serial_kernel_scope = importlib.import_module(
        f"benchmarks.cec_suite_python.{suite}._kernel_mode"
    ).serial_kernel_scope

    _ns.warmup()

    def evaluate_serial(population: np.ndarray) -> np.ndarray:
        """Evaluate one population through the serial-twin kernels."""
        pop = as_population(
            population, dim=dim, suite=suite, func_id=func_id,
            check_finite=False,   # T2: the suite dispatcher repeats this exact scan
        )
        with serial_kernel_scope():
            values = (func(pop, func_id, fp_mode=fp_mode) if suite == "cec2017"
                      else func(pop, func_id))
        return as_fitness_vector(
            values, expected_rows=pop.shape[0], suite=suite, func_id=func_id
        )

    return evaluate_serial


def _sphere_problem(func_id: int, dim: int | None, max_nfes_override: int | None) -> BenchmarkProblem:
    """Create the pure-Python sphere smoke-test problem."""
    if func_id != 1:
        raise ValueError(f"sphere supports only function id 1, got {func_id}.")
    d = 10 if dim is None else int(dim)
    if d <= 0:
        raise ValueError(f"sphere dimension must be positive, got {d}.")
    lb = np.full(d, -100.0)
    ub = np.full(d, 100.0)

    def evaluate(population: np.ndarray) -> np.ndarray:
        """Evaluate sphere objective values for a population."""
        pop = as_population(population, dim=d, suite="sphere", func_id=1)
        return np.sum(pop * pop, axis=1, dtype=np.float64)

    return BenchmarkProblem(
        suite="sphere",
        func_id=1,
        dim=d,
        lb=lb,
        ub=ub,
        optimum=0.0,
        evaluate=evaluate,
        max_nfes=_max_nfes(10_000 * d, max_nfes_override),
        target_error=1e-8,
        statistics_basis=STAT_ERROR,
        name="Sphere",
        native_dim=d,
        notes="Pure Python smoke-test problem.",
    )


def make_problem(
    suite: str,
    func_id: int,
    dim: int | None = None,
    max_nfes_override: int | None = 0,
    *,
    benchmark_fp_mode: str = "default",
    benchmark_backend: str = "python",
    data_root: str | None = None,
    serial_kernels: bool = False,
) -> BenchmarkProblem:
    """Create a uniform optimizer-facing benchmark problem.

    ``serial_kernels`` (cec2017 only, **opt-in, default off**) routes kernel
    calls to ``parallel=False`` twins, removing numba's per-launch tax. It is an
    **R2 (tolerance)** path on cec2017 -- measured 93.20% of rows bitwise, worst
    13 ULP, relative <= ~3e-15 -- so results differ from the archived batch-path
    evidence. Never enable it for a cell with archived results without a signed
    refreeze (docs/development/ACCELERATION_CAMPAIGN_PROMPT.md §5).
    """
    suite_id = normalize_suite(suite)
    fp_mode = normalize_benchmark_fp_mode(benchmark_fp_mode)
    normalize_benchmark_backend(benchmark_backend)
    fid = validate_function_id(suite_id, func_id)
    protocol = suite_protocol(suite_id)

    if suite_id == "sphere":
        return _sphere_problem(fid, dim, max_nfes_override)

    if suite_id == "cec2011":
        from benchmarks.cec_suite_python.cec2011 import (
            cec2011_bounds,
            cec2011_dim,
            cec2011_fname,
            cec2011_func,
        )

        native_dim = cec2011_dim(fid)
        d = native_dim if dim is None else int(dim)
        if d != native_dim:
            raise ValueError(f"cec2011 F{fid} has native D={native_dim}, got D={d}.")
        lb, ub = _copy_bounds(cec2011_bounds(fid), d)
        return BenchmarkProblem(
            suite=suite_id,
            func_id=fid,
            dim=d,
            lb=lb,
            ub=ub,
            optimum=float("nan"),
            evaluate=_benchmark_evaluator(cec2011_func, suite_id, fid, d),
            max_nfes=_max_nfes(150_000, max_nfes_override),
            target_error=float("nan"),
            statistics_basis=STAT_RAW,
            name=cec2011_fname(fid),
            native_dim=native_dim,
            notes=protocol.notes,
        )

    if suite_id == "cec2013":
        from benchmarks.cec_suite_python.cec2013 import (
            cec2013_bounds,
            cec2013_fname,
            cec2013_fopt,
            cec2013_func,
        )
        from benchmarks.cec_suite_python.cec2013.transforms import VALID_DIMS as CEC2013_VALID_DIMS

        if dim is None:
            raise ValueError("cec2013 requires an explicit dimension.")
        valid_dims = tuple(sorted(int(d) for d in CEC2013_VALID_DIMS))
        d = validate_dimension(suite_id, dim, valid_dims)
        lb, ub = _copy_bounds(cec2013_bounds(d), d)
        return BenchmarkProblem(
            suite=suite_id,
            func_id=fid,
            dim=d,
            lb=lb,
            ub=ub,
            optimum=cec2013_fopt(fid),
            evaluate=_benchmark_evaluator(cec2013_func, suite_id, fid, d),
            max_nfes=_max_nfes(10_000 * d, max_nfes_override),
            target_error=1e-8,
            statistics_basis=STAT_ERROR,
            name=cec2013_fname(fid),
            native_dim=None,
            notes=protocol.notes,
        )

    if suite_id == "cec2013lsgo":
        from benchmarks.cec_suite_python.cec2013lsgo import (
            cec2013lsgo_bounds,
            cec2013lsgo_dim,
            cec2013lsgo_fname,
            cec2013lsgo_func,
        )

        native_dim = cec2013lsgo_dim(fid)
        d = native_dim if dim is None else int(dim)
        if d != native_dim:
            raise ValueError(f"cec2013lsgo F{fid} has native D={native_dim}, got D={d}.")
        lb, ub = _copy_bounds(cec2013lsgo_bounds(fid, d), d)
        return BenchmarkProblem(
            suite=suite_id,
            func_id=fid,
            dim=d,
            lb=lb,
            ub=ub,
            optimum=float("nan"),
            evaluate=_benchmark_evaluator(cec2013lsgo_func, suite_id, fid, d),
            max_nfes=_max_nfes(3_000_000, max_nfes_override),
            target_error=float("nan"),
            statistics_basis=STAT_RAW,
            name=cec2013lsgo_fname(fid),
            native_dim=native_dim,
            notes=protocol.notes,
        )

    if suite_id == "cec2017":
        from benchmarks.cec_suite_python.cec2017 import (
            cec2017_bounds,
            cec2017_fname,
            cec2017_fopt,
            cec2017_func,
        )

        if dim is None:
            raise ValueError("cec2017 requires an explicit dimension.")
        d = validate_dimension(suite_id, dim, CEC2017_DIMS)
        lb, ub = _copy_bounds(cec2017_bounds(d), d)
        notes = protocol.notes
        if fid == 2:
            notes = (notes + " Explicit F2 construction requested.").strip()
        if fp_mode == "strict":
            notes = (
                notes
                + " Strict fixed-order floating-point evaluator requested for sensitive CEC2017 cells."
            ).strip()
        return BenchmarkProblem(
            suite=suite_id,
            func_id=fid,
            dim=d,
            lb=lb,
            ub=ub,
            optimum=cec2017_fopt(fid),
            evaluate=_benchmark_evaluator(
                cec2017_func,
                suite_id,
                fid,
                d,
                benchmark_fp_mode=fp_mode,
                serial_kernels=serial_kernels,
            ),
            max_nfes=_max_nfes(10_000 * d, max_nfes_override),
            target_error=1e-8,
            statistics_basis=STAT_ERROR,
            name=cec2017_fname(fid),
            native_dim=None,
            notes=notes,
        )

    if suite_id == "cec2020":
        from benchmarks.cec_suite_python.cec2020 import (
            cec2020_bounds,
            cec2020_fname,
            cec2020_fopt,
            cec2020_func,
        )

        if dim is None:
            raise ValueError("cec2020 requires an explicit dimension.")
        d = validate_dimension(suite_id, dim, CEC2020_DIMS)
        if (fid, d) in CEC2020_PROTOCOL_EXCLUDED_CELLS:
            raise ValueError(
                f"cec2020 F{fid} is not defined at D={d} by the CEC2020 protocol "
                f"(Yue et al. 2019, Technical Report 201911, Section 2.1: F6 and F7 "
                f"are specified for D = 10, 15, 20 only). Running it would produce a "
                f"result that corresponds to no competition cell."
            )
        if (fid, d) in CEC2020_UNAVAILABLE_CELLS:
            raise ValueError(
                f"cec2020 F{fid} D={d} is unavailable in the reference data distribution."
            )
        lb, ub = _copy_bounds(cec2020_bounds(d), d)
        return BenchmarkProblem(
            suite=suite_id,
            func_id=fid,
            dim=d,
            lb=lb,
            ub=ub,
            optimum=cec2020_fopt(fid),
            evaluate=_benchmark_evaluator(cec2020_func, suite_id, fid, d),
            max_nfes=_max_nfes(CEC2020_BUDGETS[d], max_nfes_override),
            target_error=1e-8,
            statistics_basis=STAT_ERROR,
            name=cec2020_fname(fid),
            native_dim=None,
            notes=protocol.notes,
        )

    raise AssertionError(f"Unhandled suite {suite_id!r}.")


__all__ = [
    "BENCHMARK_BACKENDS",
    "BENCHMARK_FP_MODES",
    "CEC2017_DIMS",
    "CEC2020_BUDGETS",
    "CEC2020_DIMS",
    "CEC2020_PROTOCOL_EXCLUDED_CELLS",
    "CEC2020_UNAVAILABLE_CELLS",
    "default_function_ids",
    "make_problem",
    "normalize_benchmark_backend",
    "normalize_benchmark_fp_mode",
]
