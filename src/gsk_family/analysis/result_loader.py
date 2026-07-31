"""Unified result loading for DT-GSK paper table generation.

The paper compares DT-GSK against the **GSK family only**
(``gsk``, ``agsk``, ``apgsk``, ``fdb-agsk``, ``egsk``, ``atmals-gsk``);
the non-GSK metaheuristic comparator panel was removed when the paper
scope was narrowed to the GSK family.

Handles two reference CSV schema variants:
    Schema A (GSK-family): ``Function`` header, ``F1`` prefix, full stats
    Schema B (Classical):  ``Func`` header, numeric ID, often sparse

Also loads locally-reproduced results from the experiment runner, which
writes suite-partitioned summaries under
``results/_run_all/<optimizer>/<suite>/summary/<optimizer>_<suite>_D<dim>.csv``
(and a ``<optimizer>_<suite>.csv`` rollup for CEC2011) with a ``Function``
header and full stats.

Every loaded result carries a provenance tag per the experiment contract
(Section 4.4): reproduced_locally, imported_reference, derived_summary,
or unavailable.
"""

from __future__ import annotations

import csv
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from .project_policy import REFERENCE_COMPARATORS, normalize_algorithm_id

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Project root auto-detection
# ---------------------------------------------------------------------------
_THIS_DIR = Path(__file__).resolve().parent  # src/gsk_family/analysis/
_PROJECT_ROOT = _THIS_DIR.parents[2]  # project root
_BENCHMARKS_DIR = _PROJECT_ROOT / "benchmarks" / "cec_reference_results"
# Locally-reproduced runs land under the experiment runner's ``output_root``,
# which is ``results/_run_all`` (one subtree per optimizer/suite). This is the
# directory that directly contains the ``<optimizer>/`` folders.
_RESULTS_DIR = _PROJECT_ROOT / "results" / "_run_all"

# ---------------------------------------------------------------------------
# Provenance tags (Section 4.4 of experiment contract)
# ---------------------------------------------------------------------------
PROVENANCE_REPRODUCED = "reproduced_locally"
PROVENANCE_IMPORTED = "imported_reference"
PROVENANCE_DERIVED = "derived_summary"
PROVENANCE_UNAVAILABLE = "unavailable"
# Data reproduced locally but sourced via locked-headline fallback

# ---------------------------------------------------------------------------
# Strict-source guard (publication analyses; PAPER_BUILD_PROMPT.md Section 2.3)
# ---------------------------------------------------------------------------
# Publication analyses must read empirical data exclusively from the immutable
# evidence release under ``benchmarks/cec_reference_results/``. Strict mode is
# opt-in (default behaviour is unchanged) and is enabled either by the
# environment variable ``GSK_STRICT_SOURCE=1`` or programmatically via
# ``set_strict_source(True)`` (threaded from ``gsk-stats --strict-source``).
# In strict mode:
#   * ``load_reproduced`` / ``_reproduced_csv_path`` refuse to resolve any
#     ``results/`` staging path (raise ``StrictSourceViolation``);
#   * ``load_algorithm`` fails loudly when a requested cell is missing from
#     the reference release instead of falling back to staging;
#   * every file actually opened is checked to live inside the canonical
#     reference tree.
# Every opened evidence file is logged (module logger + collectable list)
# in both modes, so publication runs can emit a source-use audit.

STRICT_SOURCE_ENV = "GSK_STRICT_SOURCE"

_strict_source_override: Optional[bool] = None

# Collectable audit of every data file opened through this module (and, via
# ``audit_source_open``, by the statistical pipeline). Entries are dicts with
# keys ``path`` and ``role``.
_source_audit: List[Dict[str, str]] = []


class StrictSourceViolation(RuntimeError):
    """Raised when strict-source mode blocks a non-reference data source."""


def set_strict_source(enabled: Optional[bool]) -> None:
    """Programmatically force strict-source mode on/off.

    ``True``/``False`` override the environment variable; ``None`` restores
    deferral to ``GSK_STRICT_SOURCE``.
    """
    global _strict_source_override
    _strict_source_override = enabled


def strict_source_enabled() -> bool:
    """Return True when publication strict-source mode is active."""
    if _strict_source_override is not None:
        return _strict_source_override
    return os.environ.get(STRICT_SOURCE_ENV, "").strip().lower() in (
        "1", "true", "yes", "on",
    )


def get_source_audit() -> List[Dict[str, str]]:
    """Return a copy of the opened-evidence-path audit log."""
    return list(_source_audit)


def clear_source_audit() -> None:
    """Reset the opened-evidence-path audit log."""
    _source_audit.clear()


def audit_source_open(path: str | Path, role: str = "data") -> None:
    """Record (and, in strict mode, police) a data file that is being opened.

    Appends the resolved path to the collectable audit list and logs it. In
    strict mode, raises :class:`StrictSourceViolation` if the path lies
    outside the canonical immutable evidence tree
    (``benchmarks/cec_reference_results/``).
    """
    resolved = Path(path).resolve()
    strict = strict_source_enabled()
    if strict and not resolved.is_relative_to(_BENCHMARKS_DIR):
        raise StrictSourceViolation(
            f"strict-source mode ({STRICT_SOURCE_ENV}=1 / --strict-source): refusing to read "
            f"'{resolved}' because it lies outside the immutable evidence release "
            f"'{_BENCHMARKS_DIR}'. Publication analyses may only use "
            f"benchmarks/cec_reference_results/ (PAPER_BUILD_PROMPT.md Section 2.3)."
        )
    _source_audit.append({"path": str(resolved), "role": role})
    logger.info("evidence source opened [%s, strict=%s]: %s", role, strict, resolved)

# ---------------------------------------------------------------------------
# Comparison set definitions (from experiment contract Sections 4.1-4.3)
# ---------------------------------------------------------------------------
GSK_FAMILY: list[str] = list(REFERENCE_COMPARATORS)
CEC2011_COMPARATORS: list[str] = ["gsk", "atmals-gsk"]

# Component study variants (experiment contract Section 3.2).
# The last entry "ISM-GSK-LPSR" is a "swap-one-out" variant (not a leave-one-out):
# it replaces NLPSR's x^(1-x) schedule with a strictly linear population reduction
# schedule.  This isolates the specific NLPSR curve's contribution within the
# ablation study — it verifies that the nonlinear x^(1-x) shape matters, not
# just "having any population reduction at all."
COMPONENT_VARIANTS: list[str] = [
    "gsk",
    "ISM-GSK-noACE",
    "ISM-GSK-noPSR",
    "ISM-GSK-noBSE",
    "ISM-GSK-noLINK",
    "ISM-GSK-noARCH",
    "ISM-GSK-noLS",
    "ISM-GSK-noARGP",
    "ISM-GSK-LPSR",
    "dt-gsk",
]

# Paper aliases (contract Section 3.3)
PAPER_ALIASES: dict[str, str] = {
    "gsk": "GSK",
    "ISM-GSK-noACE": "DT-GSK-1",
    "ISM-GSK-noPSR": "DT-GSK-2",
    "ISM-GSK-noBSE": "DT-GSK-3",
    "ISM-GSK-noLINK": "DT-GSK-4",
    "ISM-GSK-noARCH": "DT-GSK-5",
    "ISM-GSK-noLS": "DT-GSK-6",
    "ISM-GSK-noARGP": "DT-GSK-7",
    "ISM-GSK-LPSR": "DT-GSK-8",
    "dt-gsk": "DT-GSK",
}

# Dimensions per suite
SUITE_DIMS: dict[str, list[int]] = {
    "CEC2017": [10, 30, 50, 100],
    "CEC2013": [10, 30, 50],
    "CEC2011": [0],  # mixed per-function dims; 0 is sentinel
}

# Functions excluded per suite
#
# CEC 2017: F2 is excluded by the benchmark maintainers themselves due to
# a documented numerical-instability issue in the reference implementation.
# CEC 2013: no F2 exclusion.  F2 is a legitimate CEC2013 function and
# should remain in hold-out/generalization reports unless a suite-specific
# protocol explicitly excludes it.
# CEC 2011: real-world application problems; F2 (Lennard--Jones potential)
# is a legitimate engineering problem with no numerical-instability issue,
# so no function is excluded here.
SUITE_EXCLUDED_FUNCS: dict[str, set[int]] = {
    "CEC2017": {2},
    "CEC2013": set(),
    "CEC2011": set(),
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FunctionStats:
    """Normalized per-function statistics."""

    best: Optional[float] = None
    median: Optional[float] = None
    mean: Optional[float] = None
    worst: Optional[float] = None
    sd: Optional[float] = None

    def has_mean(self) -> bool:
        """Return True if mean error is available."""
        return self.mean is not None

    def has_full_stats(self) -> bool:
        """Return True if all five statistics are available."""
        return all(
            v is not None
            for v in (self.best, self.median, self.mean, self.worst, self.sd)
        )

    def mean_sd_str(self, fmt: str = ".2E") -> str:
        """Format as 'Mean +/- SD' for paper tables."""
        if self.mean is None:
            return "N/A"
        m = format(self.mean, fmt)
        if self.sd is not None:
            s = format(self.sd, fmt)
            return f"{m} +/- {s}"
        return m


@dataclass(frozen=True)
class AlgorithmResult:
    """Normalized results for one algorithm at one suite/dimension."""

    algorithm: str
    suite: str
    dimension: int  # 0 for CEC2011 (per-function dims)
    provenance: str
    functions: Dict[int, FunctionStats]  # func_id -> stats
    source_path: str

    @property
    def func_ids(self) -> List[int]:
        """Sorted list of available function IDs."""
        return sorted(self.functions.keys())

    def mean_errors(
        self, excluded: Optional[set[int]] = None
    ) -> Dict[int, float]:
        """Return {func_id: mean_error} for functions with available mean.

        Compatible with ``wilcoxon_signed_rank()`` and
        ``friedman_rank_test()`` in ``gsk.statistical_tests``.
        """
        excl = excluded or set()
        return {
            fid: fs.mean
            for fid, fs in self.functions.items()
            if fid not in excl and fs.mean is not None
        }

    def __len__(self) -> int:
        """Return the number of functions with loaded statistics."""
        return len(self.functions)


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------
def _parse_func_id(raw: str) -> int:
    """Parse function ID from either 'F1' or '1' format."""
    raw = raw.strip()
    if raw.upper().startswith("F"):
        return int(raw[1:])
    return int(raw)


def _parse_float(raw: str) -> Optional[float]:
    """Parse a float, returning None for empty/missing values."""
    raw = raw.strip()
    if not raw or raw in ("N/A", "n/a", "—", "-", "nan", "NaN"):
        return None
    try:
        return float(raw)
    except (ValueError, TypeError):
        return None


def load_summary_csv(path: str | Path) -> Dict[int, FunctionStats]:
    """Load a per-function summary CSV, auto-detecting schema variant.

    Handles multiple schemas:
        Schema A: Function,Best,Median,Mean,Worst,SD  (F1 or numeric)
        Schema B: Func,Best,Median,Mean,Worst,SD       (numeric, sparse)
        Schema C: F,Min,Median,Max,Mean,Std            (eGSK convention)

    Parameters
    ----------
    path : str or Path
        Path to the summary CSV.

    Returns
    -------
    dict[int, FunctionStats]
        Mapping from function ID to normalised statistics.
        Empty dict if file does not exist or is unparseable.
    """
    result: Dict[int, FunctionStats] = {}
    path = Path(path)
    if not path.is_file():
        return result

    # Strict-source chokepoint: log every summary CSV actually opened and,
    # in strict mode, refuse paths outside the immutable evidence release.
    audit_source_open(path, role="summary_csv")

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return result

        # Detect function ID column name
        fn_col: Optional[str] = None
        for candidate in ("Function", "function", "Func", "func", "FuncID", "F"):
            if candidate in reader.fieldnames:
                fn_col = candidate
                break
        if fn_col is None:
            return result

        # Build column alias map for variant schemas (e.g. eGSK uses
        # Min/Max/Std instead of Best/Worst/SD).
        _COL_ALIASES: dict[str, tuple[str, ...]] = {
            "Best": ("Best", "best", "Min", "min"),
            "Median": ("Median", "median"),
            "Mean": ("Mean", "mean"),
            "Worst": ("Worst", "worst", "Max", "max"),
            "SD": ("SD", "sd", "Std", "std"),
        }

        def _resolve_col(row: dict, canonical: str) -> str:
            """Return the value string for *canonical* stat, checking aliases."""
            for alias in _COL_ALIASES.get(canonical, (canonical,)):
                val = row.get(alias, "")
                if val:
                    return val
            return ""

        for row in reader:
            try:
                fid = _parse_func_id(row[fn_col])
            except (ValueError, KeyError):
                continue

            result[fid] = FunctionStats(
                best=_parse_float(_resolve_col(row, "Best")),
                median=_parse_float(_resolve_col(row, "Median")),
                mean=_parse_float(_resolve_col(row, "Mean")),
                worst=_parse_float(_resolve_col(row, "Worst")),
                sd=_parse_float(_resolve_col(row, "SD")),
            )

    return result


# ---------------------------------------------------------------------------
# Path resolution helpers
# ---------------------------------------------------------------------------
def _reference_csv_path(
    alg: str, suite: str, dim: int,
    base_dir: Optional[Path] = None,
) -> Optional[Path]:
    """Resolve path to a reference result CSV in benchmarks/cec_reference_results/.

    Tries multiple naming conventions:
      {alg}_{suite}_D{dim}.csv,  {alg}_{suite}_D{dim}.txt,
      {alg}_{suite}.csv (CEC2011)
    """
    bdir = base_dir or _BENCHMARKS_DIR
    suite_lower = suite.lower()
    ref_alg = normalize_algorithm_id(alg)
    alg_dir = bdir / suite_lower / ref_alg

    if not alg_dir.is_dir():
        return None

    if suite_lower == "cec2011":
        for ext in (".csv", ".txt"):
            p = alg_dir / f"{ref_alg}_{suite_lower}{ext}"
            if p.is_file() and p.stat().st_size > 0:
                return p
    else:
        for ext in (".csv", ".txt"):
            p = alg_dir / f"{ref_alg}_{suite_lower}_D{dim}{ext}"
            if p.is_file() and p.stat().st_size > 0:
                return p

    return None


def _candidate_result_filenames(alg: str, suite: str, dim: int) -> list[str]:
    """Return accepted local result filenames for one algorithm/suite/dim."""
    suite_cases = list(dict.fromkeys((suite.lower(), suite, suite.upper())))
    if suite.lower() == "cec2011":
        return [f"{alg}_{suite_case}.csv" for suite_case in suite_cases]
    return [f"{alg}_{suite_case}_D{dim}.csv" for suite_case in suite_cases]


def _first_existing_summary(summary_dir: Path, alg: str, suite: str, dim: int) -> Optional[Path]:
    """Return the first matching CSV in ``summary_dir`` using stable precedence."""
    if not summary_dir.is_dir():
        return None
    for name in _candidate_result_filenames(alg, suite, dim):
        p = summary_dir / name
        if p.is_file():
            return p
    return None


def _reproduced_csv_path(
    alg: str, suite: str, dim: int,
    results_dir: Optional[Path] = None,
) -> Optional[Path]:
    """Resolve path to a locally reproduced result CSV under ``results/_run_all``.

    The experiment runner writes suite-partitioned outputs for every optimizer
    (DT-GSK included) under its ``output_root`` (``results/_run_all``):
      results/_run_all/{alg}/{suite}/summary/{alg}_{suite}_D{dim}.csv
    For CEC2011 the per-function rollup ``{alg}_{suite}.csv`` is used instead.

    ``results_dir`` (when given) overrides ``results/_run_all`` and is the
    directory that directly contains the ``<optimizer>/`` subtrees. A legacy
    flat ``<root>/{alg}/summary/`` layout is checked last so older local
    artifacts remain readable.

    In strict-source mode this resolver refuses to run at all: reproduced
    staging paths are never admissible for publication analyses.
    """
    if strict_source_enabled():
        raise StrictSourceViolation(
            f"strict-source mode ({STRICT_SOURCE_ENV}=1 / --strict-source): refusing to resolve a "
            f"reproduced staging path for '{alg}' {suite} D{dim} under "
            f"'{results_dir or _RESULTS_DIR}'. Publication analyses may only read the immutable "
            f"evidence release benchmarks/cec_reference_results/ (PAPER_BUILD_PROMPT.md Section 2.3)."
        )
    rdir = results_dir or _RESULTS_DIR
    suite_lower = suite.lower()

    # Canonical run_all layout: results/_run_all/<alg>/<suite>/summary/.
    p = _first_existing_summary(rdir / alg / suite_lower / "summary", alg, suite, dim)
    if p is not None:
        return p

    # Legacy flat fallback: <root>/<alg>/summary/.
    p = _first_existing_summary(rdir / alg / "summary", alg, suite, dim)
    if p is not None:
        return p

    return None


# ---------------------------------------------------------------------------
# High-level loading
# ---------------------------------------------------------------------------
def load_reference(
    alg: str, suite: str, dim: int,
    base_dir: Optional[Path] = None,
) -> Optional[AlgorithmResult]:
    """Load reference results from benchmarks/cec_reference_results/.

    Returns None if the file does not exist or is empty.
    """
    path = _reference_csv_path(alg, suite, dim, base_dir)
    if path is None:
        return None

    functions = load_summary_csv(path)
    if not functions:
        return None

    return AlgorithmResult(
        algorithm=alg,
        suite=suite,
        dimension=dim,
        provenance=PROVENANCE_IMPORTED,
        functions=functions,
        source_path=str(path),
    )




def load_reproduced(
    alg: str, suite: str, dim: int,
    results_dir: Optional[Path] = None,
) -> Optional[AlgorithmResult]:
    """Load locally reproduced results from the results/ directory.

    Returns None if the file does not exist. Raises
    :class:`StrictSourceViolation` in strict-source mode: reproduced staging
    data is never an admissible publication source (Section 2.3).
    """
    if strict_source_enabled():
        raise StrictSourceViolation(
            f"strict-source mode ({STRICT_SOURCE_ENV}=1 / --strict-source): load_reproduced() is "
            f"forbidden for publication analyses (requested '{alg}' {suite} D{dim}). Only the "
            f"immutable evidence release benchmarks/cec_reference_results/ is admissible "
            f"(PAPER_BUILD_PROMPT.md Section 2.3)."
        )
    path = _reproduced_csv_path(alg, suite, dim, results_dir)
    if path is None:
        return None

    functions = load_summary_csv(path)
    if not functions:
        return None

    return AlgorithmResult(
        algorithm=alg,
        suite=suite,
        dimension=dim,
        provenance=PROVENANCE_REPRODUCED,
        functions=functions,
        source_path=str(path),
    )


def load_algorithm(
    alg: str, suite: str, dim: int,
    results_dir: Optional[Path] = None,
    ref_base_dir: Optional[Path] = None,
) -> Optional[AlgorithmResult]:
    """Load results for an algorithm, trying reference first, then reproduced.

    The committed reference panel (``benchmarks/cec_reference_results/``) is
    the paper's single source of truth for every algorithm, the proposed
    method included; a locally reproduced run is only a fallback for cells
    the reference tree does not carry.

    In strict-source mode the fallback is disabled: a cell missing from the
    immutable evidence release raises :class:`StrictSourceViolation` (fail
    loudly, Section 2.3) instead of silently reading staging data.
    """
    result = load_reference(alg, suite, dim, ref_base_dir)
    if result is not None:
        return result
    if strict_source_enabled():
        raise StrictSourceViolation(
            f"strict-source mode ({STRICT_SOURCE_ENV}=1 / --strict-source): no reference result "
            f"for '{alg}' {suite} D{dim} under "
            f"'{(ref_base_dir or _BENCHMARKS_DIR)}'; the requested cell is missing from the "
            f"immutable evidence release and the results/ staging fallback is forbidden for "
            f"publication analyses (PAPER_BUILD_PROMPT.md Section 2.3)."
        )
    return load_reproduced(alg, suite, dim, results_dir)


def load_comparison_set(
    suite: str,
    dim: int,
    algorithms: Sequence[str],
    results_dir: Optional[Path] = None,
    ref_base_dir: Optional[Path] = None,
    require_mean: bool = False,
) -> Dict[str, AlgorithmResult]:
    """Load all algorithms in a comparison set.

    Parameters
    ----------
    suite : str
        Benchmark suite (e.g. 'CEC2017').
    dim : int
        Problem dimension (0 for CEC2011).
    algorithms : sequence of str
        Algorithm names to load.
    results_dir : Path, optional
        Override for reproduced results directory.
    ref_base_dir : Path, optional
        Override for reference results directory.
    require_mean : bool
        If True, skip algorithms without any mean values.

    Returns
    -------
    dict[str, AlgorithmResult]
        Successfully loaded algorithms.  Missing algorithms are
        silently omitted.
    """
    loaded: Dict[str, AlgorithmResult] = {}
    for alg in algorithms:
        result = load_algorithm(alg, suite, dim, results_dir, ref_base_dir)
        if result is None:
            continue
        if require_mean:
            means = result.mean_errors()
            if not means:
                continue
        loaded[alg] = result
    return loaded


def discover_reference_algorithms(
    suite: str, base_dir: Optional[Path] = None
) -> List[str]:
    """Discover all algorithm directories under benchmarks/cec_reference_results/{suite}/.

    Returns
    -------
    list[str]
        Sorted list of algorithm directory names.
    """
    bdir = base_dir or _BENCHMARKS_DIR
    suite_dir = bdir / suite.lower()
    if not suite_dir.is_dir():
        return []

    return sorted(
        d.name
        for d in suite_dir.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )


# ---------------------------------------------------------------------------
# Common function ID computation
# ---------------------------------------------------------------------------
def common_func_ids(
    results: Dict[str, AlgorithmResult],
    excluded: Optional[set[int]] = None,
    require_mean: bool = True,
) -> List[int]:
    """Find function IDs common to all algorithms in *results*.

    Parameters
    ----------
    results : dict[str, AlgorithmResult]
        Loaded algorithm results.
    excluded : set of int, optional
        Function IDs to exclude (e.g. {2} for CEC2017).
    require_mean : bool
        If True, only include functions where all algorithms have mean.

    Returns
    -------
    list[int]
        Sorted list of common function IDs.
    """
    excl = excluded or set()
    if not results:
        return []

    id_sets: list[set[int]] = []
    for ar in results.values():
        if require_mean:
            fids = {
                fid
                for fid, fs in ar.functions.items()
                if fid not in excl and fs.mean is not None
            }
        else:
            fids = {fid for fid in ar.functions if fid not in excl}
        id_sets.append(fids)

    common = id_sets[0]
    for s in id_sets[1:]:
        common &= s

    return sorted(common)


# ---------------------------------------------------------------------------
# Provenance reporting
# ---------------------------------------------------------------------------
def provenance_report(results: Dict[str, AlgorithmResult]) -> str:
    """Generate a machine-readable provenance summary.

    Returns a CSV-formatted string with columns:
    Algorithm, Suite, Dimension, Provenance, NumFunctions, SourcePath
    """
    lines = ["Algorithm,Suite,Dimension,Provenance,NumFunctions,SourcePath"]
    for alg in sorted(results.keys()):
        ar = results[alg]
        lines.append(
            f"{ar.algorithm},{ar.suite},{ar.dimension},"
            f"{ar.provenance},{len(ar.functions)},{ar.source_path}"
        )
    return "\n".join(lines)


def availability_matrix(
    suites_dims: Optional[Dict[str, list[int]]] = None,
    algorithms: Optional[list[str]] = None,
    results_dir: Optional[Path] = None,
    ref_base_dir: Optional[Path] = None,
) -> Dict[str, Dict[str, Optional[str]]]:
    """Check data availability across suites, dims, and algorithms.

    Returns a nested dict: {(suite, dim): {alg: provenance_or_None}}.
    Useful for reporting which tables can be generated.
    """
    sd = suites_dims or SUITE_DIMS
    all_algs = algorithms or (
        ["dt-gsk"] + GSK_FAMILY
    )

    matrix: Dict[str, Dict[str, Optional[str]]] = {}
    for suite, dims in sd.items():
        for dim in dims:
            key = f"{suite}_D{dim}" if dim > 0 else suite
            row: Dict[str, Optional[str]] = {}
            for alg in all_algs:
                result = load_algorithm(
                    alg, suite, dim, results_dir, ref_base_dir
                )
                row[alg] = result.provenance if result else None
            matrix[key] = row

    return matrix
