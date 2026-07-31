"""Render convergence-graph PNGs from already-committed curve CSVs (no re-run).

The runner writes one median-run curve CSV per cell
(``<results>/<optimizer>/<suite>/curves/Figure_F<f>_D<d>_Run#<n>.csv`` with
columns ``Eval, BestError, Log10Error``) and only renders the matching
``curves/graphs/Figure_F<f>_D<d>.png`` when ``--convergence-graphs`` was passed.
This script reproduces those PNGs from the existing CSVs — same data, same
median run, same labels/title — so you can generate the graphs after a run that
omitted the flag, without re-running the optimizer.

Example:
    python scripts/plot_convergence_from_curves.py --root results/_run_all/egsk/cec2017 results/_run_all/egsk/cec2011
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless, file-only backend (matches the runner)
import matplotlib.pyplot as plt  # noqa: E402

_NAME_RE = re.compile(r"Figure_F(\d+)_D(\d+)_Run#\d+\.csv$")


def _read_curve(path: Path) -> tuple[list[int], list[float]]:
    """Return (evals, best_errors) from a curve CSV."""
    evals: list[int] = []
    errors: list[float] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader)  # header: Eval, BestError, Log10Error
        for row in reader:
            if not row:
                continue
            evals.append(int(row[0]))
            errors.append(float(row[1]))
    return evals, errors


def plot_suite(suite_root: Path, optimizer: str) -> int:
    """Render every cell's PNG under <suite_root>/curves/graphs/. Returns count."""
    curves_dir = suite_root / "curves"
    graphs_dir = curves_dir / "graphs"
    graphs_dir.mkdir(parents=True, exist_ok=True)
    suite = suite_root.name
    ylabel = "Best fitness" if suite == "cec2011" else "Best error"

    count = 0
    for csv_path in sorted(curves_dir.glob("Figure_F*_D*_Run#*.csv")):
        match = _NAME_RE.search(csv_path.name)
        if not match:
            continue
        func, dim = int(match.group(1)), int(match.group(2))
        evals, errors = _read_curve(csv_path)
        plt.figure()
        plt.plot(evals, errors)
        plt.xlabel("Evaluations")
        plt.ylabel(ylabel)
        plt.title(f"{optimizer} {suite} F{func} D{dim}")
        plt.tight_layout()
        plt.savefig(graphs_dir / f"Figure_F{func}_D{dim}.png")
        plt.close()
        count += 1
    print(f"{suite_root}: wrote {count} graph(s) to {graphs_dir}")
    return count


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: render PNGs for each suite results root."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        nargs="+",
        required=True,
        help="One or more <results>/<optimizer>/<suite> directories.",
    )
    parser.add_argument(
        "--optimizer",
        default=None,
        help="Optimizer label for the title (default: inferred from the parent dir name).",
    )
    args = parser.parse_args(argv)

    total = 0
    for root in args.root:
        suite_root = Path(root)
        optimizer = args.optimizer or suite_root.parent.name
        total += plot_suite(suite_root, optimizer)
    print(f"Total: {total} convergence graph(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
