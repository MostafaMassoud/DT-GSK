#!/usr/bin/env python3
"""Analyze DT-GSK per-generation diagnostics (Wave 2).

Reads the JSONL traces written by the opt-in DT-GSK diagnostics
(``DTTrace_<suite>_F<func>_D<dim>_R<run>_S<seed>.jsonl``) and aggregates them
into root-cause summary CSVs. It is purely an offline reader -- it changes no
optimizer behavior and never modifies benchmark or reference files.

Usage
-----
    python scripts/analyze_dt_diagnostics.py \
        --input results/_run_all/dt-gsk/cec2017/diagnostics \
        --out   results/_run_all/dt-gsk/cec2017/diagnostics_analysis

Outputs (under ``--out``):
    diagnostics_summary.csv          one row per run (the master summary)
    wrong_basin_candidates.csv       runs flagged as suspected wrong-basin traps
    local_search_roi.csv             per-run local-search budget/return
                                     (prefer ls_hit_rate over ls_waste_frac --
                                     see the local-search note below)
    ace_entropy_summary.csv          per-run ACE entropy collapse signals
    linkage_reliability_summary.csv  learned-vs-random linkage acceptance
    diversity_population_summary.csv  diversity + population-size trajectory
    boundary_hit_summary.csv         boundary-hit pressure

Design notes
------------
- Metadata (suite/function/dimension/run/seed) is read from the JSON fields,
  not the file name, so renamed files still analyze correctly.
- Field access is defensive (missing telemetry fields default sensibly), so the
  analyzer works for any suite/dimension/function and tolerates the compact
  field subset.
- Non-finite floats encoded as ``"NaN"``/``"Infinity"``/``"-Infinity"`` (the
  diagnostics writer's encoding) are decoded back to floats.
- Wrong-basin flagging is general (never hard-coded to a specific function): a
  run is flagged when at least two independent signals fire, several of them
  relative to the per-cell (same suite/function/dimension) distribution.
- Local search: ``ls_waste_frac`` is a *per-trigger* statistic (fraction of
  triggers with non-positive ROI) and OVERSTATES uselessness at low D, where
  most individual triggers find nothing but the rare hits still net-help. Prefer
  ``ls_hit_rate`` (fraction of triggers that produced any improvement) when
  deciding whether LS is worth gating. A direct config-only ablation (cutting LS
  ~5x at D10) left ``ls_waste_frac`` high yet did NOT improve error -- it slightly
  worsened it -- because ``ls_hit_rate`` is ~0.09 > 0, i.e. LS is net-useful.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

# --- Tunable flagging thresholds (documented; not function-specific) ---
WRONG_BASIN_FINAL_BEST_RATIO = 10.0     # final_best > ratio * cell median final_best
WRONG_BASIN_STAGNATION_FRAC = 0.5       # max stagnation > frac of total generations
WRONG_BASIN_DIVERSITY_FLOOR = 0.05      # diversity_ratio collapsed below this...
WRONG_BASIN_DIVERSITY_EARLY_FRAC = 0.5  # ...before this budget fraction
WRONG_BASIN_DELAYED_REWARD_EPS = 1e-12  # |delayed_reward_lag10| treated as "no progress"
WRONG_BASIN_DELAYED_REWARD_FRAC = 0.8   # frac of late-budget gens with no delayed reward
WRONG_BASIN_CELL_SPREAD_RATIO = 50.0    # cell worst/median final_best ratio


def _num(value: Any) -> float:
    """Return a float for *value*, decoding the non-finite string encodings."""
    if isinstance(value, str):
        if value == "NaN":
            return math.nan
        if value == "Infinity":
            return math.inf
        if value == "-Infinity":
            return -math.inf
        try:
            return float(value)
        except ValueError:
            return math.nan
    if value is None:
        return math.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def iter_run_files(input_dir: Path):
    """Yield ``(key, records)`` for one trace file at a time (memory-bounded).

    Each ``DTTrace_*.jsonl`` is one run/cell; the file is streamed line-by-line
    so only a single run's records are resident at once. This is what keeps the
    analyzer scalable -- a full D=100 campaign is tens of GB of traces and must
    NOT all be loaded into memory.
    """
    for path in sorted(input_dir.rglob("*.jsonl")):
        records: list[dict[str, Any]] = []
        key = None
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                records.append(rec)
                if key is None:
                    key = (
                        rec.get("suite"), rec.get("function"), rec.get("dimension"),
                        rec.get("run"), rec.get("seed"),
                    )
        if key is None:
            continue
        records.sort(key=lambda r: r.get("gen", 0))
        yield key, records


def load_runs(input_dir: Path) -> dict[tuple, list[dict[str, Any]]]:
    """Return ``{key: records}`` (loads all into memory; use iter_run_files for scale)."""
    runs: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for key, records in iter_run_files(input_dir):
        runs[key].extend(records)
    return runs


def _last(records: list[dict[str, Any]], field: str, default: Any = math.nan) -> Any:
    for rec in reversed(records):
        if field in rec:
            return rec[field]
    return default


def _series(records: list[dict[str, Any]], field: str) -> list[float]:
    return [_num(r[field]) for r in records if field in r]


def _finite(values: list[float]) -> list[float]:
    return [v for v in values if math.isfinite(v)]


def _rate(records: list[dict[str, Any]], accepted_field: str, total_field: str) -> float:
    """Return sum(accepted) / sum(total) across generations (NaN when no rows)."""
    acc = sum(_finite(_series(records, accepted_field)))
    tot = sum(_finite(_series(records, total_field)))
    return (acc / tot) if tot > 0 else math.nan


def summarize_run(key: tuple, records: list[dict[str, Any]]) -> dict[str, Any]:
    """Reduce one run's generation records to the summary-row fields."""
    suite, func, dim, run, seed = key
    best = _finite(_series(records, "best_fitness"))
    diversity = _finite(_series(records, "diversity_ratio"))
    ace = _finite(_series(records, "ace_entropy"))
    stagn = _finite(_series(records, "stagnation_gens"))
    boundary = _finite(_series(records, "boundary_hit_rate"))
    ls_evals = _finite(_series(records, "local_search_evals_used"))
    ls_improv = _finite(_series(records, "local_search_improvements"))
    ls_roi = _finite(_series(records, "local_search_roi"))
    restart_flags = [bool(r.get("restart_triggered")) for r in records]
    # Learned-vs-random linkage ACCEPTANCE RATES (accepted/rows), which control for
    # how often each linkage type is used -- the fair comparison of their quality.
    learned_rate = _rate(records, "linkage_learned_accepted", "linkage_learned_rows")
    random_rate = _rate(records, "linkage_random_accepted", "linkage_random_rows")
    learned_advantage = (
        learned_rate - random_rate
        if math.isfinite(learned_rate) and math.isfinite(random_rate) else math.nan
    )
    # Per-trigger local-search ROI: only the generations where LS actually fired.
    ls_gens = [r for r in records if bool(r.get("local_search_triggered"))]
    ls_trig_roi = _finite([_num(r.get("local_search_roi")) for r in ls_gens])
    ls_median_roi = statistics.median(ls_trig_roi) if ls_trig_roi else math.nan
    ls_waste_frac = (sum(1 for x in ls_trig_roi if x <= 0) / len(ls_trig_roi)) if ls_trig_roi else math.nan
    # AGGREGATE local-search usefulness. ls_waste_frac (above) is a *per-trigger*
    # statistic -- the fraction of individual triggers that returned no positive
    # ROI. At low D most individual triggers find nothing (median ROI 0 ->
    # ls_waste_frac near 1.0), which READS like "LS is useless" but is misleading:
    # the rare triggers that DO land an improvement still net-help, so cutting LS
    # does not improve (and can worsen) the result. ls_hit_rate is the honest
    # aggregate -- the fraction of triggers that produced any improvement -- and
    # should be preferred over ls_waste_frac when judging whether LS is worth
    # gating. (Direct config-only ablation confirmed: cutting LS ~5x at D10 left
    # ls_waste_frac high but did not improve error, because ls_hit_rate ~0.09 > 0.)
    ls_improved_gens = sum(1 for r in ls_gens if _num(r.get("local_search_improvements", 0)) > 0)
    ls_hit_rate = (ls_improved_gens / len(ls_gens)) if ls_gens else math.nan
    terra_reliable = [bool(r.get("terra_linkage_reliable")) for r in records if "terra_linkage_reliable" in r]
    # Record-derived flag signals computed here so the records can be discarded
    # immediately afterward (the analyzer streams one run at a time).
    early_div = _finite([
        _num(r["diversity_ratio"]) for r in records
        if "diversity_ratio" in r and _num(r.get("budget_frac", 1.0)) < WRONG_BASIN_DIVERSITY_EARLY_FRAC
    ])
    late = [r for r in records if _num(r.get("budget_frac", 0.0)) > 0.5 and "delayed_reward_lag10" in r]
    stall_frac = (
        sum(1 for r in late if abs(_num(r["delayed_reward_lag10"])) < WRONG_BASIN_DELAYED_REWARD_EPS) / len(late)
        if late else math.nan
    )

    return {
        "suite": suite, "function": func, "dimension": dim, "run": run, "seed": seed,
        "_early_diversity_min": min(early_div) if early_div else math.nan,
        "_delayed_reward_stall_frac": stall_frac,
        "generations": len(records),
        "final_evals": int(_num(_last(records, "evals_used", 0)) or 0),
        "final_best": best[-1] if best else math.nan,
        "min_best": min(best) if best else math.nan,
        "max_stagnation_gens": int(max(stagn)) if stagn else 0,
        "min_diversity_ratio": min(diversity) if diversity else math.nan,
        "median_diversity_ratio": statistics.median(diversity) if diversity else math.nan,
        "min_ace_entropy": min(ace) if ace else math.nan,
        "median_ace_entropy": statistics.median(ace) if ace else math.nan,
        "restart_count": int(_num(_last(records, "restarts_done", 0)) or 0) or sum(restart_flags),
        "restart_generations": sum(restart_flags),
        "total_local_search_evals": int(sum(ls_evals)),
        "total_local_search_improvements": int(sum(ls_improv)),
        "ls_triggers": len(ls_gens),
        "ls_median_roi": ls_median_roi,
        "max_local_search_roi": max(ls_roi) if ls_roi else math.nan,
        "ls_waste_frac": ls_waste_frac,
        "ls_hit_rate": ls_hit_rate,
        "mean_boundary_hit_rate": statistics.mean(boundary) if boundary else math.nan,
        "max_boundary_hit_rate": max(boundary) if boundary else math.nan,
        "learned_linkage_acc_rate": learned_rate,
        "random_linkage_acc_rate": random_rate,
        "linkage_learned_advantage": learned_advantage,
        "terra_reliable_fraction": (sum(terra_reliable) / len(terra_reliable)) if terra_reliable else math.nan,
    }


def flag_wrong_basin(
    summary: dict[str, Any],
    cell_median_final: float,
    cell_spread_ratio: float,
) -> tuple[bool, list[str]]:
    """Return ``(flagged, reasons)`` from a run's summary + its cell context.

    Operates on the summary alone (the record-derived signals are precomputed in
    :func:`summarize_run`), so the analyzer can discard a run's records right
    after summarizing it.
    """
    reasons: list[str] = []
    fb = summary["final_best"]

    if math.isfinite(fb) and math.isfinite(cell_median_final) and cell_median_final > 0:
        if fb > WRONG_BASIN_FINAL_BEST_RATIO * cell_median_final:
            reasons.append("final_best>>cell_median")

    gens = max(1, summary["generations"])
    if summary["max_stagnation_gens"] > WRONG_BASIN_STAGNATION_FRAC * gens:
        reasons.append("long_stagnation")

    early_div = summary.get("_early_diversity_min", math.nan)
    if math.isfinite(early_div) and early_div < WRONG_BASIN_DIVERSITY_FLOOR:
        reasons.append("early_diversity_collapse")

    if summary["restart_count"] == 0:
        reasons.append("no_restart")
    elif "final_best>>cell_median" in reasons:
        reasons.append("restart_ineffective")

    stall = summary.get("_delayed_reward_stall_frac", math.nan)
    if math.isfinite(stall) and stall > WRONG_BASIN_DELAYED_REWARD_FRAC:
        reasons.append("delayed_reward_stalled")

    if math.isfinite(cell_spread_ratio) and cell_spread_ratio > WRONG_BASIN_CELL_SPREAD_RATIO:
        reasons.append("extreme_cell_spread")

    # A run is flagged only when it actually landed in a worse-than-peers basin
    # (a bad-OUTCOME signal is NECESSARY) AND at least one mechanism corroborates
    # it. This avoids false positives from benign signals that fire on healthy
    # runs (e.g. DT-GSK's by-design NLPSR diversity collapse).
    bad_outcome = {"final_best>>cell_median", "extreme_cell_spread"} & set(reasons)
    flagged = bool(bad_outcome) and len(set(reasons)) >= 2
    return (flagged, sorted(set(reasons)))


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def analyze(input_dir: Path, out_dir: Path) -> dict[str, int]:
    """Run the full analysis and write the CSVs. Returns simple counts."""
    out_dir.mkdir(parents=True, exist_ok=True)
    # Pass 1: stream one run/file at a time, reduce it to a summary, discard its
    # records. Only the (small) per-run summaries stay resident -- a full D=100
    # campaign is tens of GB of traces and must never be loaded all at once.
    summaries: list[dict[str, Any]] = [summarize_run(key, records) for key, records in iter_run_files(input_dir)]

    # Pass 2: per-cell (suite,function,dimension) distribution of final_best.
    by_cell: dict[tuple, list[float]] = defaultdict(list)
    for s in summaries:
        if math.isfinite(s["final_best"]):
            by_cell[(s["suite"], s["function"], s["dimension"])].append(s["final_best"])
    cell_median = {c: statistics.median(v) for c, v in by_cell.items() if v}
    cell_spread = {
        c: (max(v) / statistics.median(v)) if statistics.median(v) > 0 else math.nan
        for c, v in by_cell.items() if v
    }

    # Pass 3: flag using the summaries + cell context (no records needed).
    summary_rows: list[dict[str, Any]] = []
    wrong_rows: list[dict[str, Any]] = []
    for s in summaries:
        cell = (s["suite"], s["function"], s["dimension"])
        flagged, reasons = flag_wrong_basin(
            s, cell_median.get(cell, math.nan), cell_spread.get(cell, math.nan)
        )
        s = {**s, "suspected_wrong_basin": int(flagged)}
        summary_rows.append(s)
        if flagged:
            wrong_rows.append({**s, "reasons": ";".join(reasons)})

    summary_rows.sort(key=lambda r: (str(r["suite"]), r["dimension"] or 0, r["function"] or 0, r["run"] or 0))

    summary_cols = [
        "suite", "function", "dimension", "run", "seed", "generations", "final_evals",
        "final_best", "min_best", "max_stagnation_gens", "min_diversity_ratio",
        "median_diversity_ratio", "min_ace_entropy", "median_ace_entropy", "restart_count",
        "restart_generations", "total_local_search_evals", "total_local_search_improvements",
        "ls_triggers", "ls_median_roi", "max_local_search_roi", "ls_waste_frac", "ls_hit_rate",
        "mean_boundary_hit_rate", "max_boundary_hit_rate",
        "learned_linkage_acc_rate", "random_linkage_acc_rate", "linkage_learned_advantage",
        "terra_reliable_fraction", "suspected_wrong_basin",
    ]
    _write_csv(out_dir / "diagnostics_summary.csv", summary_cols, summary_rows)
    _write_csv(out_dir / "wrong_basin_candidates.csv", summary_cols + ["reasons"], wrong_rows)
    _write_csv(
        out_dir / "local_search_roi.csv",
        ["suite", "function", "dimension", "run", "ls_triggers", "total_local_search_evals",
         "total_local_search_improvements", "ls_median_roi", "max_local_search_roi",
         "ls_waste_frac", "ls_hit_rate"],
        summary_rows,
    )
    _write_csv(
        out_dir / "ace_entropy_summary.csv",
        ["suite", "function", "dimension", "run", "min_ace_entropy", "median_ace_entropy"],
        summary_rows,
    )
    _write_csv(
        out_dir / "linkage_reliability_summary.csv",
        ["suite", "function", "dimension", "run", "learned_linkage_acc_rate",
         "random_linkage_acc_rate", "linkage_learned_advantage", "terra_reliable_fraction"],
        summary_rows,
    )
    _write_csv(
        out_dir / "diversity_population_summary.csv",
        ["suite", "function", "dimension", "run", "min_diversity_ratio",
         "median_diversity_ratio", "max_stagnation_gens"],
        summary_rows,
    )
    _write_csv(
        out_dir / "boundary_hit_summary.csv",
        ["suite", "function", "dimension", "run", "mean_boundary_hit_rate", "max_boundary_hit_rate"],
        summary_rows,
    )
    return {"runs": len(summaries), "wrong_basin_candidates": len(wrong_rows)}


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run the analysis, print a one-line summary."""
    parser = argparse.ArgumentParser(description="Analyze DT-GSK diagnostics JSONL traces.")
    parser.add_argument("--input", required=True, help="Directory of DTTrace_*.jsonl files (searched recursively).")
    parser.add_argument("--out", required=True, help="Output directory for the analysis CSVs.")
    args = parser.parse_args(argv)

    input_dir = Path(args.input)
    if not input_dir.is_dir():
        print(f"input directory not found: {input_dir}")
        return 1
    counts = analyze(input_dir, Path(args.out))
    print(
        f"analyzed {counts['runs']} run(s); "
        f"{counts['wrong_basin_candidates']} suspected wrong-basin candidate(s); "
        f"wrote CSVs to {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
