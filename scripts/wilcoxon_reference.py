"""Wilcoxon signed-rank test: Python port vs imported reference table.

For each optimizer and dimension this pairs the port's per-function statistic
(mean error by default) against the reference table's value across the benchmark
functions, then runs a Wilcoxon signed-rank test on the paired differences. It
reports the win/tie/loss split, the signed rank sums, the p-value, and a
significance verdict at the chosen alpha.

This is a *suite-level* test on per-function summary statistics (the reference
tables store summaries, not per-run samples), so it answers "does the port's
central tendency systematically differ from the reference across the suite?" --
not the per-function 51-vs-51 rank-sum, which would need per-run reference data.

Example:
    python scripts/wilcoxon_reference.py --optimizers apgsk,fdb-agsk --dimensions 10,30,50,100
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, wilcoxon

STAT_COLUMN = {"mean": "Mean", "median": "Median"}


def _load_stat(path: Path, column: str) -> dict[int, float]:
    """Return {function_id: statistic} from a summary CSV, or {} if absent."""
    values: dict[int, float] = {}
    if not path.exists():
        return values
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            label = str(row.get("Function", "")).strip()
            cell = str(row.get(column, "")).strip()
            if not label or not cell:
                continue
            try:
                values[int(float(label))] = float(cell)
            except ValueError:
                continue
    return values


def _tolerance(reference: float) -> float:
    """Treat-as-tie band, matching the runner's near-same definition."""
    return max(1e-8, 1e-9 * max(1.0, abs(reference)))


def compare_pairs(
    port: dict[int, float], reference: dict[int, float]
) -> tuple[np.ndarray, np.ndarray, int, int, int]:
    """Pair functions present in both; return (port, ref) arrays and W/T/L counts.

    A function is a tie (and excluded from the test) when |port - ref| falls
    within the tolerance band. Lower error is better, so port < ref is a win.
    """
    port_vals: list[float] = []
    ref_vals: list[float] = []
    win = tie = loss = 0
    for func in sorted(set(port) & set(reference)):
        pv, rv = port[func], reference[func]
        if abs(pv - rv) <= _tolerance(rv):
            tie += 1
            continue
        port_vals.append(pv)
        ref_vals.append(rv)
        if pv < rv:
            win += 1
        else:
            loss += 1
    return np.asarray(port_vals), np.asarray(ref_vals), win, tie, loss


def signed_rank(port: np.ndarray, reference: np.ndarray) -> tuple[float, float, float]:
    """Return (R_minus, R_plus, p_value) for the two related samples.

    R_minus is the rank sum where the port is better (lower error); R_plus where
    it is worse. p_value is the two-sided Wilcoxon signed-rank result.
    """
    diffs = port - reference
    ranks = rankdata(np.abs(diffs))
    r_minus = float(ranks[diffs < 0].sum())
    r_plus = float(ranks[diffs > 0].sum())
    _stat, p_value = wilcoxon(port, reference, zero_method="wilcox", alternative="two-sided")
    return r_minus, r_plus, float(p_value)


def verdict(p_value: float, r_minus: float, r_plus: float, alpha: float) -> str:
    """Human-readable significance verdict."""
    if p_value >= alpha:
        return "no sig. diff (equivalent)"
    return "DIFFERS: port better" if r_minus > r_plus else "DIFFERS: port worse"


def run(
    optimizers: list[str],
    dimensions: list[int],
    suite: str,
    statistic: str,
    results_root: Path,
    reference_root: Path,
    alpha: float,
    out_path: Path | None,
) -> list[dict[str, object]]:
    """Compute and print the signed-rank comparison; return the result rows."""
    column = STAT_COLUMN[statistic]
    rows: list[dict[str, object]] = []
    for optimizer in optimizers:
        print(
            f"\n=== {optimizer.upper()}: Python {statistic} error vs reference "
            f"({suite}, Wilcoxon signed-rank, alpha={alpha}) ==="
        )
        header = (
            f"{'Dim':>5} | {'n*':>3} | {'better':>6} | {'tie':>3} | {'worse':>5} | "
            f"{'R-(better)':>10} | {'R+(worse)':>9} | {'p-value':>9} | verdict"
        )
        print(header)
        print("-" * len(header))
        pooled_port: list[float] = []
        pooled_ref: list[float] = []
        pooled_w = pooled_t = pooled_l = 0
        for dim in dimensions:
            port = _load_stat(
                results_root / optimizer / suite / "summary" / f"{optimizer}_{suite}_D{dim}.csv",
                column,
            )
            reference = _load_stat(
                reference_root / suite / optimizer / f"{optimizer}_{suite}_D{dim}.csv", column
            )
            port_arr, ref_arr, win, tie, loss = compare_pairs(port, reference)
            pooled_port.extend(port_arr.tolist())
            pooled_ref.extend(ref_arr.tolist())
            pooled_w += win
            pooled_t += tie
            pooled_l += loss
            if port_arr.size == 0:
                print(f"{dim:>5} | {'0':>3} | identical within tolerance (no test)")
                rows.append(
                    {"optimizer": optimizer, "dim": dim, "n": 0, "better": win,
                     "tie": tie, "worse": loss, "r_minus": "", "r_plus": "",
                     "p_value": "", "verdict": "identical"}
                )
                continue
            r_minus, r_plus, p_value = signed_rank(port_arr, ref_arr)
            note = verdict(p_value, r_minus, r_plus, alpha)
            print(
                f"{dim:>5} | {port_arr.size:>3} | {win:>6} | {tie:>3} | {loss:>5} | "
                f"{r_minus:>10.1f} | {r_plus:>9.1f} | {p_value:>9.3g} | {note}"
            )
            rows.append(
                {"optimizer": optimizer, "dim": dim, "n": int(port_arr.size), "better": win,
                 "tie": tie, "worse": loss, "r_minus": r_minus, "r_plus": r_plus,
                 "p_value": p_value, "verdict": note}
            )
        pooled_p = np.asarray(pooled_port)
        pooled_r = np.asarray(pooled_ref)
        if pooled_p.size:
            r_minus, r_plus, p_value = signed_rank(pooled_p, pooled_r)
            note = verdict(p_value, r_minus, r_plus, alpha)
            print("-" * len(header))
            print(
                f"{'all':>5} | {pooled_p.size:>3} | {pooled_w:>6} | {pooled_t:>3} | {pooled_l:>5} | "
                f"{r_minus:>10.1f} | {r_plus:>9.1f} | {p_value:>9.3g} | {note}"
            )
            rows.append(
                {"optimizer": optimizer, "dim": "all", "n": int(pooled_p.size), "better": pooled_w,
                 "tie": pooled_t, "worse": pooled_l, "r_minus": r_minus, "r_plus": r_plus,
                 "p_value": p_value, "verdict": note}
            )
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["optimizer", "dim", "n", "better", "tie", "worse",
                            "r_minus", "r_plus", "p_value", "verdict"],
            )
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nWrote {out_path}")
    return rows


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Wilcoxon signed-rank: port vs reference table.")
    parser.add_argument("--optimizers", default="apgsk,fdb-agsk")
    parser.add_argument("--dimensions", default="10,30,50,100")
    parser.add_argument("--suite", default="cec2017")
    parser.add_argument("--statistic", choices=sorted(STAT_COLUMN), default="mean")
    parser.add_argument("--results-root", type=Path, default=Path("results/_run_all"))
    parser.add_argument(
        "--reference-root", type=Path, default=Path("benchmarks/cec_reference_results")
    )
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--out", type=Path, default=None, help="Optional CSV output path.")
    args = parser.parse_args(argv)

    run(
        optimizers=[o.strip() for o in args.optimizers.split(",") if o.strip()],
        dimensions=[int(d) for d in args.dimensions.split(",") if d.strip()],
        suite=args.suite,
        statistic=args.statistic,
        results_root=args.results_root,
        reference_root=args.reference_root,
        alpha=args.alpha,
        out_path=args.out,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
