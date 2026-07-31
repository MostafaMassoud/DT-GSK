"""Validate generated GSK results against reference evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

from gsk_family.runners.verification import verify_run_directory


DEFAULT_REFERENCE_ROOT = Path("benchmarks/cec_reference_results")


def _validate_references(root: str | Path) -> int:
    """Validate that a reference root exists and contains CSV tables."""
    path = Path(root)
    if not path.exists():
        print(f"reference root not found: {path}")
        print("validation requires the bundled comparator references from a source checkout or package data.")
        return 1
    # count suite evidence only - underscore-prefixed subtrees are companion
    # releases (_ablation, _oracle, _paper_tables, _releases), not suites
    csv_files = [p for p in path.rglob("*.csv")
                 if not any(part.startswith("_")
                            for part in p.relative_to(path).parts)]
    if not csv_files:
        print(f"no reference CSV files found under: {path}")
        print("validation cannot run without comparator CSV evidence.")
        return 1
    print(f"reference root: {path}")
    print(f"csv files: {len(csv_files)}")
    print("use --compare RUN_DIR REFERENCE_ROOT to compare generated summaries")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Validate available reference assets."""
    parser = argparse.ArgumentParser(description="Validate GSK result/reference inputs.")
    parser.add_argument(
        "--references",
        default=None,
        help=f"Reference result root to inspect; defaults to {DEFAULT_REFERENCE_ROOT}.",
    )
    parser.add_argument(
        "--compare",
        nargs=2,
        metavar=("RUN_DIR", "REFERENCE_ROOT"),
        help="Compare generated run output against imported references.",
    )
    parser.add_argument(
        "--verify",
        nargs=2,
        metavar=("RUN_DIR", "REFERENCE_ROOT"),
        help="Alias for --compare; writes verification.json.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--reduced", action="store_true", help="Treat run as reduced-budget.")
    mode.add_argument("--full", action="store_true", help="Treat run as full-budget.")
    args = parser.parse_args(argv)

    compare_args = args.compare or args.verify
    if compare_args:
        reduced = True if args.reduced else False if args.full else None
        result = verify_run_directory(compare_args[0], compare_args[1], reduced_budget=reduced)
        print(f"verdict: {result.verdict}")
        print(f"functions_checked: {result.functions_checked}")
        print(f"hard_failures: {result.hard_failures}")
        print(f"missing_reference: {result.missing_reference}")
        wins, ties, losses = result.win_tie_loss
        print(f"win_tie_loss: {wins}/{ties}/{losses}")
        if result.functions_checked == 0:
            print("no comparable generated/reference functions were checked; validation is inconclusive.")
            return 1
        return 1 if result.verdict == "DEVIATES" else 0

    return _validate_references(args.references or DEFAULT_REFERENCE_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
