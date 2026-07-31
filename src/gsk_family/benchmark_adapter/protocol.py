"""Benchmark suite protocol metadata."""

from __future__ import annotations

from dataclasses import dataclass


STAT_ERROR = "error_vs_optimum"
STAT_RAW = "raw_objective"

SUPPORTED_SUITES = (
    "sphere",
    "cec2011",
    "cec2013",
    "cec2013lsgo",
    "cec2017",
    "cec2020",
)

CEC_SUITES = (
    "cec2011",
    "cec2013",
    "cec2013lsgo",
    "cec2017",
    "cec2020",
)

RAW_OBJECTIVE_SUITES = {"cec2011", "cec2013lsgo"}
ERROR_VS_OPTIMUM_SUITES = {"cec2013", "cec2017", "cec2020"}


@dataclass(frozen=True)
class SuiteProtocol:
    """Static protocol metadata for a benchmark suite."""

    suite: str
    function_ids: tuple[int, ...]
    default_function_ids: tuple[int, ...]
    default_dimensions: tuple[int, ...] | str
    statistics_basis: str
    target_error: float
    notes: str = ""


def _range_tuple(start: int, stop: int) -> tuple[int, ...]:
    """Return an inclusive integer range as an immutable tuple."""
    return tuple(range(start, stop + 1))


SUITE_PROTOCOLS: dict[str, SuiteProtocol] = {
    "sphere": SuiteProtocol(
        suite="sphere",
        function_ids=(1,),
        default_function_ids=(1,),
        default_dimensions=(10,),
        statistics_basis=STAT_ERROR,
        target_error=1e-8,
        notes="Pure Python smoke-test problem.",
    ),
    "cec2011": SuiteProtocol(
        suite="cec2011",
        function_ids=_range_tuple(1, 22),
        default_function_ids=_range_tuple(1, 22),
        default_dimensions="native",
        statistics_basis=STAT_RAW,
        target_error=float("nan"),
        notes="Raw-objective statistics; adapter optimum is NaN.",
    ),
    "cec2013": SuiteProtocol(
        suite="cec2013",
        function_ids=_range_tuple(1, 28),
        default_function_ids=_range_tuple(1, 28),
        default_dimensions=(10, 30, 50),
        statistics_basis=STAT_ERROR,
        target_error=1e-8,
    ),
    "cec2013lsgo": SuiteProtocol(
        suite="cec2013lsgo",
        function_ids=_range_tuple(1, 15),
        default_function_ids=_range_tuple(1, 15),
        default_dimensions="native",
        statistics_basis=STAT_RAW,
        target_error=float("nan"),
        notes="Raw-objective statistics for comparability with imported references.",
    ),
    "cec2017": SuiteProtocol(
        suite="cec2017",
        function_ids=_range_tuple(1, 30),
        default_function_ids=(1,) + tuple(range(3, 31)),
        default_dimensions=(10, 30, 50, 100),
        statistics_basis=STAT_ERROR,
        target_error=1e-8,
        notes="F2 is implemented but excluded from default comparisons.",
    ),
    "cec2020": SuiteProtocol(
        suite="cec2020",
        function_ids=_range_tuple(1, 10),
        default_function_ids=_range_tuple(1, 10),
        default_dimensions=(5, 10, 15, 20),
        statistics_basis=STAT_ERROR,
        target_error=1e-8,
    ),
}


def normalize_suite(suite: str) -> str:
    """Return canonical lowercase suite id."""
    normalized = suite.strip().lower()
    if normalized not in SUITE_PROTOCOLS:
        raise ValueError(
            f"Unsupported suite {suite!r}; expected one of {', '.join(SUPPORTED_SUITES)}."
        )
    return normalized


def suite_protocol(suite: str) -> SuiteProtocol:
    """Return protocol metadata for a suite."""
    return SUITE_PROTOCOLS[normalize_suite(suite)]


def default_function_ids(suite: str) -> tuple[int, ...]:
    """Return the default function list for a suite."""
    return suite_protocol(suite).default_function_ids


def all_function_ids(suite: str) -> tuple[int, ...]:
    """Return all implemented public function IDs for a suite."""
    return suite_protocol(suite).function_ids


def default_dimensions(suite: str) -> tuple[int, ...] | str:
    """Return default dimensions for fixed-dimension suites or ``native``."""
    return suite_protocol(suite).default_dimensions


def is_native_dimension_suite(suite: str) -> bool:
    """Return True when dimensions are chosen per function."""
    return suite_protocol(suite).default_dimensions == "native"


def validate_function_id(suite: str, func_id: int) -> int:
    """Validate and return integer function ID."""
    fid = int(func_id)
    if fid != float(func_id):
        raise ValueError(f"Function id must be integer-valued, got {func_id!r}.")
    protocol = suite_protocol(suite)
    if fid not in protocol.function_ids:
        raise ValueError(
            f"{protocol.suite} function id must be in "
            f"{protocol.function_ids[0]}..{protocol.function_ids[-1]}, got {fid}."
        )
    return fid


def validate_dimension(suite: str, dim: int, valid: tuple[int, ...]) -> int:
    """Validate a fixed-dimension suite dimension."""
    d = int(dim)
    if d != float(dim):
        raise ValueError(f"Dimension must be integer-valued, got {dim!r}.")
    if d not in valid:
        raise ValueError(f"{normalize_suite(suite)} requires D in {list(valid)}, got D={d}.")
    return d
