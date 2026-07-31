"""Reference-result loading and generated-result verification."""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def ensure_output_root_allowed(output_root: str | Path, reference_root: str | Path) -> None:
    """Refuse writes into the imported reference-result tree."""
    out = Path(output_root).resolve()
    ref = Path(reference_root).resolve()
    if out == ref or ref in out.parents:
        raise ValueError(
            "Refusing to write generated experiment output into "
            f"reference results: {out}"
        )


STAT_COLUMNS = ("Best", "Median", "Mean", "Worst", "SD")
MISSING_TOKENS = {"", "-", "na", "n/a", "nan", "none", "null"}
NEGATIVE_ERROR_FLOOR = -1e-6
GROSS_FACTOR = 1e6
REFERENCE_TRIVIAL_FLOOR = 1e-8


@dataclass(frozen=True)
class SummaryCell:
    """One function row from a summary table."""

    function: int
    stats: dict[str, float | None]
    source: str
    original_label: str


@dataclass(frozen=True)
class SummaryTable:
    """Loaded summary table."""

    optimizer: str
    suite: str
    dimension: int | None
    path: str
    cells: dict[int, SummaryCell]


@dataclass(frozen=True)
class VerificationFailure:
    """One verification finding."""

    kind: str
    function: int
    dimension: int | None
    message: str
    hard: bool = False


@dataclass(frozen=True)
class VerificationResult:
    """Reference comparison result compatible with runner JSON output."""

    optimizer: str
    suite: str
    verdict: str
    reduced_budget: bool
    functions_checked: int
    hard_failures: int
    win_tie_loss: tuple[int, int, int]
    missing_reference: int
    thresholds: dict[str, float]
    failures: list[VerificationFailure] = field(default_factory=list)
    generated_dir: str = ""
    reference_root: str = ""
    #: Why the verdict is what it is when no comparison happened. ``None`` for
    #: genuine CONSISTENT/DEVIATES verdicts; ``"NO_REFERENCE"`` when every
    #: attempted comparison found no reference row, so nothing was verified.
    reason: str | None = None

    def to_json_dict(self) -> dict[str, Any]:
        """Return JSON-serializable verification payload."""
        payload = asdict(self)
        payload["win_tie_loss"] = list(self.win_tie_loss)
        return payload


def normalize_function_label(label: Any) -> int:
    """Normalize labels such as ``1``, ``F1`` or ``f1`` to an integer id."""
    text = str(label).strip()
    match = re.fullmatch(r"(?:function\s*)?[Ff]?0*(\d+)", text, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"Cannot parse function label {label!r}.")
    value = int(match.group(1))
    if value <= 0:
        raise ValueError(f"Function id must be positive, got {label!r}.")
    return value


def parse_optional_float(value: Any) -> float | None:
    """Parse a table cell, returning ``None`` for missing reference values."""
    text = str(value).strip()
    if text.lower() in MISSING_TOKENS:
        return None
    parsed = float(text)
    if not math.isfinite(parsed):
        return None
    return parsed


def _dimension_from_name(path: Path) -> int | None:
    """Extract a dimension suffix such as `_D10` from a summary filename."""
    match = re.search(r"_D0*(\d+)$", path.stem, flags=re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def _read_summary_table(path: str | Path, optimizer: str, suite: str) -> SummaryTable:
    """Read a CSV summary table into normalized function cells."""
    csv_path = Path(path)
    cells: dict[int, SummaryCell] = {}
    with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "Function" not in reader.fieldnames:
            raise ValueError(f"Summary table {csv_path} is missing a Function column.")
        for row in reader:
            if not row:
                continue
            original_label = str(row.get("Function", "")).strip()
            if not original_label:
                continue
            function = normalize_function_label(original_label)
            stats = {name: parse_optional_float(row.get(name, "")) for name in STAT_COLUMNS}
            cells[function] = SummaryCell(
                function=function,
                stats=stats,
                source=str(csv_path),
                original_label=original_label,
            )
    return SummaryTable(
        optimizer=optimizer,
        suite=suite,
        dimension=_dimension_from_name(csv_path),
        path=str(csv_path),
        cells=cells,
    )


def _candidate_reference_tables(
    reference_root: str | Path,
    optimizer: str,
    suite: str,
    dimension: int | None,
) -> list[Path]:
    """Return matching reference table candidates for a generated dimension."""
    base = Path(reference_root) / suite / optimizer
    if not base.exists():
        return []
    direct = list(base.glob("*.csv"))
    dimension_matches: list[Path] = []
    rollups: list[Path] = []
    for path in direct:
        dim = _dimension_from_name(path)
        stem = path.stem.lower()
        if dimension is not None and dim == dimension:
            dimension_matches.append(path)
        elif dim is None and stem == f"{optimizer}_{suite}".lower():
            rollups.append(path)
    return sorted(dimension_matches) or sorted(rollups)


def load_reference_table(
    reference_root: str | Path,
    optimizer: str,
    suite: str,
    dimension: int | None,
) -> SummaryTable | None:
    """Load the best matching imported reference summary table."""
    candidates = _candidate_reference_tables(reference_root, optimizer, suite, dimension)
    if not candidates:
        return None
    return _read_summary_table(candidates[0], optimizer, suite)


def load_generated_tables(run_dir: str | Path) -> tuple[dict[str, Any], list[SummaryTable]]:
    """Load generated summary tables for a run directory."""
    root = Path(run_dir)
    summary = root / "summary" if (root / "summary").is_dir() else root
    env_path = summary / "environment.json"
    env: dict[str, Any] = {}
    if env_path.exists():
        env = json.loads(env_path.read_text(encoding="utf-8"))

    optimizer = str(env.get("optimizer") or root.parent.name)
    suite = str(env.get("suite") or root.name)
    tables: list[SummaryTable] = []
    for path in sorted(summary.glob(f"{optimizer}_{suite}_D*.csv")):
        tables.append(_read_summary_table(path, optimizer, suite))
    if not tables:
        for path in sorted(summary.glob("*.csv")):
            if path.name in {"per_run.csv", "seed_schedule.csv"}:
                continue
            tables.append(_read_summary_table(path, optimizer, suite))
    return env, tables


def _is_reduced_budget(env: dict[str, Any], override: bool | None) -> bool:
    """Infer whether a generated run should be treated as reduced budget."""
    if override is not None:
        return override
    max_override = int(env.get("max_nfes_override") or 0)
    runs = int(env.get("runs") or 0)
    return max_override > 0 or (runs > 0 and runs < 25)


def _known_optimum_stats(env: dict[str, Any]) -> bool:
    """Return True when generated stats are error-vs-optimum values."""
    return str(env.get("statistics_basis", "")).lower() == "error_vs_optimum"


def _numeric_generated_stats(cell: SummaryCell) -> dict[str, float]:
    """Return generated statistics as finite floats or raise a hard error."""
    numeric: dict[str, float] = {}
    for name, value in cell.stats.items():
        if value is None or not math.isfinite(value):
            raise ValueError(f"Generated statistic {name} is missing or non-finite.")
        numeric[name] = float(value)
    return numeric


def _compare_mean(gen_mean: float, ref_mean: float) -> int:
    """Compare generated and reference means with a small numeric tolerance."""
    tolerance = max(1e-12, 1e-9 * max(1.0, abs(ref_mean)))
    if gen_mean < ref_mean - tolerance:
        return -1
    if gen_mean > ref_mean + tolerance:
        return 1
    return 0


def compare_generated_to_references(
    run_dir: str | Path,
    reference_root: str | Path,
    *,
    reduced_budget: bool | None = None,
) -> VerificationResult:
    """Compare generated summary tables to imported reference summaries."""
    env, generated_tables = load_generated_tables(run_dir)
    optimizer = str(env.get("optimizer") or Path(run_dir).parent.name)
    suite = str(env.get("suite") or Path(run_dir).name)
    reduced = _is_reduced_budget(env, reduced_budget)
    known_optimum = _known_optimum_stats(env)

    failures: list[VerificationFailure] = []
    missing_reference = 0
    checked = 0
    wins = ties = losses = 0

    reference_cache: dict[int | None, SummaryTable | None] = {}
    for table in generated_tables:
        ref_table = reference_cache.setdefault(
            table.dimension,
            load_reference_table(reference_root, optimizer, suite, table.dimension),
        )
        for function, gen_cell in sorted(table.cells.items()):
            try:
                gen_stats = _numeric_generated_stats(gen_cell)
            except ValueError as exc:
                failures.append(
                    VerificationFailure(
                        kind="non_finite_generated",
                        function=function,
                        dimension=table.dimension,
                        message=str(exc),
                        hard=True,
                    )
                )
                continue

            if known_optimum and min(gen_stats.values()) < NEGATIVE_ERROR_FLOOR:
                failures.append(
                    VerificationFailure(
                        kind="negative_error_floor",
                        function=function,
                        dimension=table.dimension,
                        message="Generated known-optimum statistics include impossible negative error.",
                        hard=True,
                    )
                )

            if ref_table is None or function not in ref_table.cells:
                missing_reference += 1
                failures.append(
                    VerificationFailure(
                        kind="missing_reference",
                        function=function,
                        dimension=table.dimension,
                        message="No matching reference summary row found.",
                        hard=False,
                    )
                )
                continue

            ref_cell = ref_table.cells[function]
            ref_mean = ref_cell.stats.get("Mean")
            if ref_mean is None:
                missing_reference += 1
                failures.append(
                    VerificationFailure(
                        kind="missing_reference",
                        function=function,
                        dimension=table.dimension,
                        message="Reference mean is missing.",
                        hard=False,
                    )
                )
                continue

            checked += 1
            comparison = _compare_mean(gen_stats["Mean"], ref_mean)
            if comparison < 0:
                wins += 1
            elif comparison > 0:
                losses += 1
            else:
                ties += 1

            if (
                known_optimum
                and not reduced
                and abs(ref_mean) > REFERENCE_TRIVIAL_FLOOR
                and gen_stats["Mean"] > GROSS_FACTOR * abs(ref_mean)
            ):
                failures.append(
                    VerificationFailure(
                        kind="gross_deviation",
                        function=function,
                        dimension=table.dimension,
                        message=(
                            "Generated mean exceeds gross full-budget threshold "
                            f"({gen_stats['Mean']} vs reference {ref_mean})."
                        ),
                        hard=True,
                    )
                )

    hard_count = sum(1 for failure in failures if failure.hard)
    # A verdict must never claim more than the comparison performed. When not a
    # single function could be compared because no reference rows exist (the
    # suite has no committed reference bank), "CONSISTENT" would be vacuously
    # true and actively misleading -- the CEC2013LSGO banks carried exactly that
    # verdict with 15 missing_reference findings each (deviation record D-8.1),
    # and the pre-registered CEC2020 analysis plan (Addendum 1, Section 11)
    # forbids it for the promoted releases. Hard failures still dominate:
    # non-finite or negative-error checks run without any reference.
    if hard_count:
        verdict, reason = "DEVIATES", None
    elif checked == 0 and missing_reference > 0:
        verdict, reason = "NOT_VERIFIED", "NO_REFERENCE"
    else:
        verdict, reason = "CONSISTENT", None
    return VerificationResult(
        optimizer=optimizer,
        suite=suite,
        verdict=verdict,
        reason=reason,
        reduced_budget=reduced,
        functions_checked=checked,
        hard_failures=hard_count,
        win_tie_loss=(wins, ties, losses),
        missing_reference=missing_reference,
        thresholds={
            "negative_error_floor": NEGATIVE_ERROR_FLOOR,
            "gross_factor": GROSS_FACTOR,
            "reference_trivial_floor": REFERENCE_TRIVIAL_FLOOR,
        },
        failures=failures,
        generated_dir=str(Path(run_dir)),
        reference_root=str(Path(reference_root)),
    )


def write_verification_json(result: VerificationResult, path: str | Path) -> None:
    """Write a verification result JSON file."""
    Path(path).write_text(json.dumps(result.to_json_dict(), indent=2, sort_keys=True), encoding="utf-8")


def verify_run_directory(
    run_dir: str | Path,
    reference_root: str | Path,
    *,
    reduced_budget: bool | None = None,
    output_path: str | Path | None = None,
) -> VerificationResult:
    """Compare a run directory and write ``verification.json``."""
    result = compare_generated_to_references(
        run_dir,
        reference_root,
        reduced_budget=reduced_budget,
    )
    if output_path is None:
        root = Path(run_dir)
        summary = root / "summary" if (root / "summary").is_dir() else root
        output_path = summary / "verification.json"
    write_verification_json(result, output_path)
    return result
