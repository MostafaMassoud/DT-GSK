"""List GSK package capabilities."""

from __future__ import annotations

import argparse
from pathlib import Path

from gsk_family.benchmark_adapter.protocol import CEC_SUITES
from gsk_family.optimizers import OPTIMIZER_IDS


def _print_optimizers() -> None:
    """Print registered optimizer ids."""
    print("optimizers:")
    for optimizer in OPTIMIZER_IDS:
        print(f"  {optimizer}")


def _print_benchmarks() -> None:
    """Print supported benchmark and smoke suite ids."""
    print("benchmarks:")
    for suite in CEC_SUITES:
        print(f"  {suite}")
    print("smoke problems:")
    print("  sphere")


def _print_references(root: str) -> None:
    """Print a compact CSV inventory for an imported reference root."""
    path = Path(root)
    print("references:")
    if not path.exists():
        print(f"  missing: {path}")
        return
    # underscore-prefixed subtrees (_ablation, _oracle, _paper_tables,
    # _releases) are companion releases, not benchmark suites
    for suite_dir in sorted(item for item in path.iterdir()
                            if item.is_dir() and not item.name.startswith("_")):
        csv_count = sum(1 for _ in suite_dir.rglob("*.csv"))
        print(f"  {suite_dir.name}: {csv_count} csv files")


def main(argv: list[str] | None = None) -> int:
    """Print a compact capability summary."""
    parser = argparse.ArgumentParser(description="List GSK package capabilities.")
    parser.add_argument("--optimizers", action="store_true")
    parser.add_argument("--benchmarks", action="store_true")
    parser.add_argument("--references", nargs="?", const="benchmarks/cec_reference_results")
    args = parser.parse_args(argv)

    if not (args.optimizers or args.benchmarks or args.references):
        _print_optimizers()
        _print_benchmarks()
        return 0

    if args.optimizers:
        _print_optimizers()
    if args.benchmarks:
        _print_benchmarks()
    if args.references:
        _print_references(args.references)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
