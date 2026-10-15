"""Collect summary CSVs into one panel folder that ``gsk-stats`` can compare.

``gsk-stats`` reads every algorithm from the committed panel under
``benchmarks/cec_reference_results/`` first, so your own runs are not analysed
by default. This script builds a panel folder for one suite: it copies the
committed per-dimension summary CSVs, then copies your own summary CSVs on top.
Each of your files replaces the committed file for the same optimizer and
dimension; every optimizer or dimension you did not run keeps its committed
result. Point ``gsk-stats --reference-root`` at the folder afterwards.

Run from the repository root (standard library only, no install needed)::

    python scripts/build_stats_panel.py --suite cec2017 --results my_results --out my_panel
    gsk-stats --suite cec2017 --reference-root my_panel --out comparison_mine/cec2017

``--results`` is the ``--output-root`` you gave ``run.py`` (the folder holding
``<optimizer>/<suite>/summary/``). Re-running the script rebuilds the suite's
panel from scratch. It warns when one of your files lacks functions that the
committed file has, and when your last run used another number of runs or a
cut evaluation budget (read from ``summary/run_config.json``).
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path
from typing import Any

MARKER = ".built_by_build_stats_panel"
SUITES = ("cec2011", "cec2013", "cec2013lsgo", "cec2017", "cec2020")


def summary_name_matches(name: str, optimizer: str, suite: str) -> bool:
    """Return True for ``<opt>_<suite>_D<dim>.csv``, or for CEC2011 only the rollup ``<opt>_<suite>.csv``."""
    if suite == "cec2011":
        return name == f"{optimizer}_{suite}.csv"  # gsk-stats reads only the CEC2011 rollup
    return name.startswith(f"{optimizer}_{suite}_D") and name.endswith(".csv")


def _read_json(path: Path) -> dict[str, Any]:
    """Return the JSON object in *path*, or an empty dict if it is missing or unreadable."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def function_ids(path: Path) -> set[int]:
    """Return the function ids listed in a summary CSV (its ``Function`` column)."""
    with path.open(newline="", encoding="utf-8") as handle:
        return {int(row["Function"]) for row in csv.DictReader(handle) if row.get("Function")}


def committed_files(reference_root: Path, suite: str) -> dict[str, list[Path]]:
    """Map each optimizer in the committed panel to its summary CSVs."""
    found: dict[str, list[Path]] = {}
    for opt_dir in sorted(p for p in (reference_root / suite).iterdir() if p.is_dir()):
        files = sorted(f for f in opt_dir.iterdir() if f.is_file() and summary_name_matches(f.name, opt_dir.name, suite))
        if files:
            found[opt_dir.name] = files
    return found


def own_files(results_root: Path, suite: str) -> dict[str, list[Path]]:
    """Map each optimizer in a ``run.py`` output root to its summary CSVs for *suite*."""
    found: dict[str, list[Path]] = {}
    if not results_root.is_dir():
        return found
    for opt_dir in sorted(p for p in results_root.iterdir() if p.is_dir()):
        summary = opt_dir / suite / "summary"
        if not summary.is_dir():
            continue
        files = sorted(f for f in summary.iterdir() if f.is_file() and summary_name_matches(f.name, opt_dir.name, suite))
        if files:
            found[opt_dir.name] = files
    return found


def build_panel(suite: str, results_root: Path, reference_root: Path, out_root: Path) -> int:
    """Build ``<out_root>/<suite>/`` and print what was used. Returns an exit code."""
    suite = suite.lower()
    if not (reference_root / suite).is_dir():
        print(f"committed panel not found: {reference_root / suite}")
        print("  this needs a full clone of the repository (the folder benchmarks/cec_reference_results/).")
        return 1
    ref, out = reference_root.resolve(), out_root.resolve()
    if out == ref or ref in out.parents:
        print(f"refusing to write inside the committed panel {reference_root}; choose another --out.")
        return 1
    mine = own_files(results_root, suite)
    if not mine:
        print(f"no summary CSVs for {suite} found under {results_root}/<optimizer>/{suite}/summary/")
        print("  check --results (the --output-root you gave run.py) and --suite.")
        return 1

    target = out_root / suite
    if target.exists():
        if not (target / MARKER).is_file():
            print(f"refusing to overwrite {target}: it was not built by this script; choose another --out.")
            return 1
        shutil.rmtree(target)
    target.mkdir(parents=True)
    (target / MARKER).write_text("Built by scripts/build_stats_panel.py; safe to delete.\n", encoding="utf-8")

    committed = committed_files(reference_root, suite)
    for optimizer, files in committed.items():
        (target / optimizer).mkdir(exist_ok=True)
        for path in files:
            shutil.copy2(path, target / optimizer / path.name)

    used: list[str] = []
    warnings: list[str] = []
    for optimizer, files in mine.items():
        mine_cfg = _read_json(results_root / optimizer / suite / "summary" / "run_config.json")
        ref_cfg = _read_json(reference_root / suite / optimizer / "run_config.json")
        if mine_cfg.get("max_nfes_override"):
            warnings.append(
                f"{optimizer}: your last run used a non-default budget (--max-evaluations "
                f"{mine_cfg['max_nfes_override']}); its means are not comparable with the committed ones"
            )
        if mine_cfg and ref_cfg and mine_cfg.get("runs") != ref_cfg.get("runs"):
            warnings.append(
                f"{optimizer}: your last run used {mine_cfg.get('runs')} run(s) per function, "
                f"the committed panel {ref_cfg.get('runs')}"
            )
        (target / optimizer).mkdir(exist_ok=True)
        for path in files:
            published = reference_root / suite / optimizer / path.name
            if published.is_file():
                have, want = function_ids(path), function_ids(published)
                if not want <= have:
                    warnings.append(
                        f"{path.name}: your file has {len(have & want)} of the {len(want)} functions in "
                        "the committed file; gsk-stats compares only the functions all algorithms share"
                    )
            shutil.copy2(path, target / optimizer / path.name)
            used.append(f"{optimizer}/{path.name}")

    kept = sum(len(files) for files in committed.values())
    print(f"panel written to {target}")
    print(f"  your files used ({len(used)}):")
    for name in used:
        print(f"    {name}")
    print(f"  committed files copied first: {kept} (yours replace those with the same name)")
    for warning in warnings:
        print(f"  WARNING {warning}")
    print("next:")
    root_arg = f'"{out_root}"' if " " in str(out_root) else str(out_root)
    print(f"  gsk-stats --suite {suite} --reference-root {root_arg} --out comparison_mine/{suite}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and build the panel."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0].replace("``", ""))
    parser.add_argument("--suite", required=True, type=str.lower, choices=SUITES, help="Benchmark suite.")
    parser.add_argument("--results", default="my_results", help="Your run.py --output-root (default: my_results).")
    parser.add_argument("--out", default="my_panel", help="Panel folder to write (default: my_panel).")
    parser.add_argument(
        "--reference-root",
        default=str(Path(__file__).resolve().parents[1] / "benchmarks" / "cec_reference_results"),
        help="Committed panel (default: benchmarks/cec_reference_results in this repository).",
    )
    args = parser.parse_args(argv)
    return build_panel(args.suite, Path(args.results), Path(args.reference_root), Path(args.out))


if __name__ == "__main__":
    sys.exit(main())
