"""Result output writers for experiment runs."""

from __future__ import annotations

import csv
import json
import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from gsk_family.stats import compute_error, format_scientific, statistic_values, summarize
from gsk_family.types import OptimizerResult, RunRecord


logger = logging.getLogger(__name__)


CHECKPOINT_FRACTIONS = (
    0.01,
    0.02,
    0.03,
    0.05,
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
    1.0,
)


@dataclass(frozen=True)
class RunArtifact:
    """Optimizer result plus problem metadata needed by output writers."""

    record: RunRecord
    result: OptimizerResult
    statistics_basis: str
    optimum: float
    target_error: float
    max_nfes: int


def output_dirs(output_root: str | Path, optimizer: str, suite: str) -> dict[str, Path]:
    """Return schema directories for an optimizer/suite output tree."""
    root = Path(output_root) / optimizer / suite
    return {
        "root": root,
        "summary": root / "summary",
        "curves": root / "curves",
        "graphs": root / "curves" / "graphs",
        "gen_logs": root / "gen_logs",
    }


def ensure_output_dirs(output_root: str | Path, optimizer: str, suite: str) -> dict[str, Path]:
    """Create and return schema directories."""
    dirs = output_dirs(output_root, optimizer, suite)
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def read_existing_per_run(path: str | Path) -> list[dict[str, str]]:
    """Read existing per-run rows, returning an empty list when absent."""
    csv_path = Path(path)
    if not csv_path.exists():
        return []
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_per_run(path: str | Path, rows: list[dict[str, Any]]) -> None:
    """Write per-run rows."""
    fieldnames = [
        "optimizer",
        "suite",
        "function",
        "dimension",
        "run",
        "seed",
        "best_fitness",
        "error",
        "nfes",
        "termination",
        "runtime_seconds",
    ]
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_record_to_row(record: RunRecord) -> dict[str, Any]:
    """Convert a run record to a CSV row."""
    return {
        "optimizer": record.optimizer,
        "suite": record.suite,
        "function": record.function,
        "dimension": record.dimension,
        "run": record.run,
        "seed": record.seed,
        "best_fitness": f"{record.best_fitness:.10e}",
        "error": "NaN" if math.isnan(record.error) else f"{record.error:.10e}",
        "nfes": record.nfes,
        "termination": record.termination,
        "runtime_seconds": f"{record.runtime_seconds:.6f}",
    }


def write_seed_schedule(path: str | Path, rows: list[Any]) -> None:
    """Write seed schedule rows with the documented schema."""
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Dim", "Function", "Run", "Seed"])
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "Dim": int(row.dim),
                    "Function": int(row.function),
                    "Run": int(row.run),
                    "Seed": int(row.seed),
                }
            )


def _artifact_value(artifact: RunArtifact) -> float:
    """Return the statistic basis value for a one-run artifact."""
    values = statistic_values(
        np.array([artifact.record.best_fitness]),
        optimum=artifact.optimum,
        target_error=artifact.target_error,
        statistics_basis=artifact.statistics_basis,
    )
    return float(values[0])


_SUMMARY_HEADER = ["Function", "Best", "Median", "Mean", "Worst", "SD"]


def _read_existing_summary(path: Path) -> dict[int, list[str]]:
    """Return ``{function: row}`` from an existing summary CSV, or ``{}``.

    Rows are returned as the raw strings already on disk so they can be written
    back byte-for-byte (BUG-RESUME-01): recomputing an untouched function from
    ``per_run.csv`` would perturb Mean/SD in the 10th significant digit, because
    the per-run table stores values rounded to ``%.10e`` while the artifact path
    summarises full float64. Measured on real data: Best/Median/Worst always
    match, Mean/SD differed in 5 of 20 fields. Preserving the bytes keeps a
    resume from silently rewriting released numbers.
    """
    if not path.is_file():
        return {}
    out: dict[int, list[str]] = {}
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
            if header != _SUMMARY_HEADER:
                return {}
            for row in reader:
                if len(row) == len(_SUMMARY_HEADER):
                    out[int(row[0])] = list(row)
    except (OSError, ValueError):
        return {}
    return out


def write_summary_tables(
    summary_dir: str | Path,
    optimizer: str,
    suite: str,
    artifacts: list[RunArtifact],
    *,
    bank_counts: dict[tuple[int, int], int] | None = None,
    bank_values: dict[tuple[int, int], list[float]] | None = None,
) -> None:
    """Write per-dimension CEC-style summary tables.

    BUG-RESUME-01 (2026-07-25). ``artifacts`` holds only the runs executed in
    THIS session, so on a resume this function used to (a) truncate the file to
    the resumed functions, dropping every untouched one, and (b) summarise a
    partially-resumed function over its new runs alone -- 6 of 25 runs reported
    as if they were the whole cell. Both are silent corruptions of a released
    artifact.

    Fixes, in order of preference per cell:

    * **untouched function** -- its existing on-disk row is carried over
      verbatim, so a resume never perturbs a number it did not recompute;
    * **fully covered by this session** (``bank_counts`` says the bank holds no
      more runs than we have artifacts for) -- summarised from the artifacts,
      exactly as before, at full float64 precision;
    * **partially resumed** -- summarised from ``bank_values`` (all runs recorded
      in ``per_run.csv``), which is the only complete source once earlier runs'
      in-memory values are gone. Accepts 10th-significant-digit drift on
      Mean/SD; strictly better than statistics over an arbitrary subset.

    ``bank_counts``/``bank_values`` are optional so existing callers and tests
    keep working; without them the artifact-only behaviour is preserved for
    covered cells and untouched rows are still carried over.
    """
    by_dim_func: dict[tuple[int, int], list[RunArtifact]] = {}
    for artifact in artifacts:
        key = (artifact.record.dimension, artifact.record.function)
        by_dim_func.setdefault(key, []).append(artifact)

    by_dim: dict[int, list[tuple[int, Any]]] = {}
    for (dim, func), group in sorted(by_dim_func.items()):
        values = np.array([_artifact_value(item) for item in group], dtype=float)
        # Partially resumed cell: the bank holds runs this session did not
        # execute, so the artifacts alone are an incomplete sample. Fall back to
        # the full recorded set from per_run.csv.
        if bank_counts is not None and bank_values is not None:
            banked = int(bank_counts.get((dim, func), len(group)))
            if banked > len(group):
                complete = bank_values.get((dim, func))
                if complete:
                    values = np.array(complete, dtype=float)
        stats = summarize(values)
        by_dim.setdefault(dim, []).append((func, stats))

    summary_path = Path(summary_dir)
    if suite == "cec2011":
        rollup_path = summary_path / f"{optimizer}_{suite}.csv"
        # BUG-RESUME-01: same merge as the per-dimension tables below -- CEC2011
        # has one rollup instead of per-dim files, and it truncated identically.
        merged_rollup = _read_existing_summary(rollup_path)
        for rows in by_dim.values():
            for func, stats in rows:
                merged_rollup[int(func)] = [
                    str(int(func)),
                    format_scientific(stats.best),
                    format_scientific(stats.median),
                    format_scientific(stats.mean),
                    format_scientific(stats.worst),
                    format_scientific(stats.sd),
                ]
        with rollup_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(_SUMMARY_HEADER)
            for func in sorted(merged_rollup):
                writer.writerow(merged_rollup[func])

    for dim, rows in by_dim.items():
        file_path = summary_path / f"{optimizer}_{suite}_D{dim}.csv"
        # BUG-RESUME-01: start from whatever is already on disk so functions this
        # session never touched survive, then overwrite only the ones we
        # recomputed. Previously this opened "w" and wrote `rows` only, erasing
        # every untouched function.
        merged = _read_existing_summary(file_path)
        for func, stats in rows:
            merged[int(func)] = [
                str(int(func)),
                format_scientific(stats.best),
                format_scientific(stats.median),
                format_scientific(stats.mean),
                format_scientific(stats.worst),
                format_scientific(stats.sd),
            ]
        with file_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(_SUMMARY_HEADER)
            for func in sorted(merged):
                writer.writerow(merged[func])


def _trace_values(artifact: RunArtifact) -> np.ndarray:
    """Return best-so-far convergence values in the documented statistic basis.

    The written curve/checkpoint schema is best-so-far, so the trace is clamped
    with a running minimum before use. For the strictly greedy optimizers this
    is a byte-identical no-op; it guards restart-based optimizers whose
    reported working incumbent can regress after a full re-initialization.
    """
    if artifact.statistics_basis == "raw_objective":
        values = artifact.result.convergence.best_fitness.copy()
    else:
        values = np.array(
            [
                compute_error(value, artifact.optimum, artifact.target_error)
                for value in artifact.result.convergence.best_fitness
            ],
            dtype=float,
        )
    if values.size:
        values = np.minimum.accumulate(values)
    return values


def _value_at_eval(artifact: RunArtifact, checkpoint: int) -> float:
    """Return the best trace value available at a checkpoint evaluation."""
    nfes = artifact.result.convergence.nfes
    values = _trace_values(artifact)
    index = int(np.searchsorted(nfes, checkpoint, side="right") - 1)
    if index < 0:
        index = 0
    return float(values[index])


def write_curves_and_logs(
    dirs: dict[str, Path],
    optimizer: str,
    artifacts: list[RunArtifact],
    *,
    write_generation_logs: bool = False,
    write_convergence_graphs: bool = False,
) -> None:
    """Write median-run curves, optional checkpoint logs, and optional graphs."""
    by_cell: dict[tuple[int, int], list[RunArtifact]] = {}
    for artifact in artifacts:
        by_cell.setdefault((artifact.record.function, artifact.record.dimension), []).append(artifact)

    for (func, dim), group in sorted(by_cell.items()):
        values = np.array([_artifact_value(item) for item in group], dtype=float)
        median = float(np.median(values))
        median_index = int(np.argmin(np.abs(values - median)))
        median_artifact = group[median_index]
        curve_path = dirs["curves"] / f"Figure_F{func}_D{dim}_Run#{median_artifact.record.run}.csv"
        trace = _trace_values(median_artifact)
        with curve_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["Eval", "BestError", "Log10Error"])
            for nfe, value in zip(median_artifact.result.convergence.nfes, trace):
                log_value = "" if value <= 0 or not np.isfinite(value) else f"{math.log10(value):.16e}"
                writer.writerow([int(nfe), f"{value:.16e}", log_value])

        if write_generation_logs:
            checkpoints = [
                max(1, int(round(median_artifact.max_nfes * frac)))
                for frac in CHECKPOINT_FRACTIONS
            ]
            log_path = dirs["gen_logs"] / f"CheckpointErrors_{optimizer}_F{func}_D{dim}.csv"
            with log_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Run", "Seed", *[f"E{checkpoint}" for checkpoint in checkpoints]])
                for artifact in sorted(group, key=lambda item: item.record.run):
                    writer.writerow(
                        [
                            artifact.record.run,
                            artifact.record.seed,
                            *[
                                f"{_value_at_eval(artifact, checkpoint):.16g}"
                                for checkpoint in checkpoints
                            ],
                        ]
                    )

        graph_path = dirs["graphs"] / f"Figure_F{func}_D{dim}.png"
        if not write_convergence_graphs:
            graph_path.unlink(missing_ok=True)
            continue

        try:
            import matplotlib

            # Headless backend: never create Tk widgets. The default GUI backend
            # (e.g. TkAgg) crashes at interpreter teardown with "main thread is
            # not in main loop" / "Tcl_AsyncDelete: async handler deleted by the
            # wrong thread" when figures are produced by a runner that also
            # drives a worker pool. Agg is process/thread safe and file-only.
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            plt.figure()
            plt.plot(median_artifact.result.convergence.nfes, trace)
            plt.xlabel("Evaluations")
            plt.ylabel("Best error" if median_artifact.statistics_basis != "raw_objective" else "Best fitness")
            plt.title(f"{optimizer} {median_artifact.record.suite} F{func} D{dim}")
            plt.tight_layout()
            plt.savefig(graph_path)
            plt.close()
        except Exception as exc:  # pragma: no cover - plotting is best-effort
            logger.debug("Skipped convergence graph for F%s D%s: %s", func, dim, exc)


def write_environment(path: str | Path, payload: dict[str, Any]) -> None:
    """Write environment metadata JSON, preserving the caller's key order."""
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")


def write_profile(path: str | Path, payload: dict[str, Any]) -> None:
    """Write optional performance profile metadata."""
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
