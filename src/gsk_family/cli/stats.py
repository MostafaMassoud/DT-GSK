"""Generate the GSK-family statistical comparison report.

Builds the paper-grade statistical comparison of the proposed optimizer
(``dt-gsk`` by default) against the GSK-family reference comparators: a
7-algorithm Friedman panel with mean ranks, pairwise Wilcoxon signed-rank tests
with a Holm correction and Vargha-Delaney effect sizes, Nemenyi
critical-difference diagrams, rank charts, and LaTeX table fragments.

The proposed algorithm's per-function mean errors come from its locally
reproduced run under ``results/_run_all/<proposed>/<suite>/summary/``; the
comparators come from the committed reference tables under
``benchmarks/cec_reference_results/<suite>/``. Outputs are written to
``results/_run_all/_analysis/<suite>/`` unless ``--out`` is given.

Examples
--------
    gsk-stats --suite CEC2017 --dims 10,30,50,100
    gsk-stats --suite CEC2011 --no-figures
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from gsk_family.analysis.family_report import (
    DEFAULT_PROPOSED,
    generate_family_report,
)
from gsk_family.analysis.result_loader import (
    SUITE_DIMS,
    clear_source_audit,
    get_source_audit,
    set_strict_source,
)

DEFAULT_RESULTS_ROOT = Path("results/_run_all")
DEFAULT_REFERENCE_ROOT = Path("benchmarks/cec_reference_results")


def _parse_dims(value: str | None, suite: str) -> list[int]:
    """Parse a comma-separated dimension list, defaulting per suite."""
    if not value:
        return list(SUITE_DIMS.get(suite.upper(), [10, 30, 50, 100]))
    dims: list[int] = []
    for token in value.split(","):
        token = token.strip()
        if token:
            dims.append(int(token))
    return dims


def main(argv: list[str] | None = None) -> int:
    """Run the family statistical report. Returns 0 on success, 1 if no data."""
    parser = argparse.ArgumentParser(
        description="Generate the GSK-family statistical comparison report.",
    )
    parser.add_argument("--suite", default="CEC2017", help="Benchmark suite (default: CEC2017).")
    parser.add_argument(
        "--dims",
        default=None,
        help="Comma-separated dimensions (default: the suite's standard set).",
    )
    parser.add_argument(
        "--proposed",
        default=DEFAULT_PROPOSED,
        help=f"Proposed optimizer id anchoring the comparison (default: {DEFAULT_PROPOSED}).",
    )
    parser.add_argument(
        "--results-root",
        default=str(DEFAULT_RESULTS_ROOT),
        help=f"Reproduced-results root (default: {DEFAULT_RESULTS_ROOT}).",
    )
    parser.add_argument(
        "--reference-root",
        default=str(DEFAULT_REFERENCE_ROOT),
        help=f"Reference-results root (default: {DEFAULT_REFERENCE_ROOT}).",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output directory (default: <results-root>/_analysis/<suite>).",
    )
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance level (default: 0.05).")
    parser.add_argument("--no-figures", action="store_true", help="Skip matplotlib figure rendering.")
    parser.add_argument(
        "--strict-source",
        action="store_true",
        help=(
            "Publication mode: refuse any empirical input outside the immutable evidence "
            "release benchmarks/cec_reference_results/ (no results/ fallback; missing cells "
            "fail loudly) and write a source_use_audit.csv of every opened data file next to "
            "the report outputs."
        ),
    )
    args = parser.parse_args(argv)

    suite = args.suite
    dims = _parse_dims(args.dims, suite)
    results_root = Path(args.results_root)
    reference_root = Path(args.reference_root)
    out_dir = Path(args.out) if args.out else results_root / "_analysis" / suite.lower()

    ref_base = reference_root / suite.lower()
    if not ref_base.is_dir():
        print(f"reference directory not found: {ref_base}")
        print("statistical comparison requires the bundled GSK-family reference tables.")
        return 1

    strict = bool(args.strict_source)
    audit_path: Path | None = None
    if strict:
        set_strict_source(True)
        clear_source_audit()
    try:
        dim_results, written = generate_family_report(
            suite, dims, out_dir,
            results_root=results_root,
            reference_root=reference_root,
            proposed=args.proposed,
            make_figures=not args.no_figures,
            alpha=args.alpha,
        )
    finally:
        if strict:
            entries = get_source_audit()
            set_strict_source(None)
            # Emit the Section 2.3 source-use audit (every opened data file)
            # even when the run fails loudly mid-way.
            out_dir.mkdir(parents=True, exist_ok=True)
            audit_path = out_dir / "source_use_audit.csv"
            with audit_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["role", "path"])
                for entry in entries:
                    writer.writerow([entry["role"], entry["path"]])

    if not dim_results:
        print(f"no reproduced '{args.proposed}' summaries found under {results_root} for {suite}.")
        print(f"  searched dimensions: {dims}")
        print("  run the experiment pipeline for the proposed optimizer first (see runbook.md).")
        return 1

    print(f"GSK-family statistical report — {suite}")
    print(f"  proposed: {args.proposed}  |  dimensions analysed: {[r.dim for r in dim_results]}")
    for r in dim_results:
        if r.mean_ranks:
            order = sorted(r.mean_ranks.items(), key=lambda kv: kv[1])
            best, best_rank = order[0]
            p = r.stat_result.friedman_gsk_family.p_value
            print(f"  D{r.dim}: N={r.n_funcs}  Friedman p={p:.3g}  best={best} ({best_rank:.3f})")
        else:
            print(f"  D{r.dim}: Friedman panel unavailable (insufficient comparators)")
    print(f"  wrote {len(written)} artifact(s) to {out_dir}")
    if audit_path is not None:
        print(f"  strict-source mode: source-use audit written to {audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
