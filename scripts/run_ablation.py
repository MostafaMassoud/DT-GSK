#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Run the DT-GSK scaffold ablation on CEC2017.

Each ablation *cell* disables exactly one scaffold mechanism via
``optimizer_options`` (every mechanism defaults to ``True`` in the locked
profile).  SGSM is disabled throughout the scaffold ablation
(``interaction_graph_enabled: false`` in every cell) -- the SGSM overlay is
ablated separately on the CEC2013 hold-out, not here.

The CLI (``run.py``) accepts optimizer options only through a YAML ``--config``,
so this driver writes one config per cell under ``configs/_ablation/`` and
invokes the runner for each.  Per-cell output lands in its own directory so
cells never overwrite one another::

    <output-root>/<cell>/dt-gsk/cec2017/summary/dt-gsk_cec2017_D<dim>.csv

Aggregate the cells afterwards with
``papers/scripts/generate_ablation_matrix.py``.

Examples
--------
    # write configs only, inspect before launching
    python scripts/run_ablation.py --dimension 30 --dry-run

    # run the default cell set at D=30, n=25
    python scripts/run_ablation.py --dimension 30 --runs 25 --workers 2

    # run a subset
    python scripts/run_ablation.py --only baseline,no_linkage,no_bse

The default cell set is the baseline (full scaffold, SGSM off) plus one
disable-one-component cell per mechanism.  Extend ``CELLS`` to match the exact
16-cell design reported in the paper; confirm each toggle's semantics in
``src/gsk_family/optimizers/_dt_profiles.py`` (some mechanisms have paired
flags, e.g. ``psr_enabled`` vs ``sp_nlpsr_enabled``).
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from gsk_family.cli.run import main as run_main

_REPO = Path(__file__).resolve().parents[1]
_CONFIG_DIR = _REPO / "configs" / "_ablation"

# SGSM stays OFF in every scaffold-ablation cell.
_SGSM_OFF: dict[str, Any] = {"interaction_graph_enabled": False}

# The six major scaffold mechanisms the ablation isolates (optimizer_options flag,
# short name, label). Each defaults to True in the locked profile; one cell disables
# each, plus a full-scaffold baseline -> 7 configs. Each maps to a GSK limitation the
# paper names: ACE + NLPSR (fixed parameters), BSE (stagnation), Linkage
# (non-separability), Nelder-Mead (no local search), plus the elite archive.
MECHANISMS: list[tuple[str, str, str]] = [
    ("ace_enabled", "ace", "ACE knowledge control"),
    ("psr_enabled", "psr", "NLPSR population reduction"),
    ("bse_enabled", "bse", "Budget-Safe Escape"),
    ("linkage_blockwise_enabled", "linkage", "Linkage-aware crossover"),
    ("local_search_enabled", "localsearch", "coordinate local search"),
    ("arch_enabled", "arch", "Elite archive"),
]
# Excluded extras -- add a tuple back to MECHANISMS to ablate one too:
#   ("argp_enabled", "argp", "ARGP pool pruning")                     -- minor control tweak
#   ("final_polish_enabled", "finalpolish", "Eigenframe polish")      -- SGSM-dependent; belongs in the SGSM-overlay ablation
#   ("deep_stall_restart_enabled", "deepstall", "Deep-stall restart") -- overlaps BSE (stagnation)


def _build_cells(mode: str) -> dict[str, dict[str, Any]]:
    """{cell_name: optimizer_options overrides} for the chosen ablation direction.

    remove-one (default): ``baseline`` = full scaffold; each ``no_<m>`` cell
      disables one mechanism (isolates its marginal contribution).
    add-one (ATMALS-style): ``base`` = bare GSK (all mechanisms off); each
      ``only_<m>`` cell enables exactly one.
    """
    cells: dict[str, dict[str, Any]] = {}
    if mode == "add-one":
        all_off = {flag: False for flag, _, _ in MECHANISMS}
        cells["base"] = dict(all_off)
        for flag, short, _ in MECHANISMS:
            cells[f"only_{short}"] = {**all_off, flag: True}
    else:  # remove-one
        cells["baseline"] = {}
        for flag, short, _ in MECHANISMS:
            cells[f"no_{short}"] = {flag: False}
    return cells


def _cell_state(overrides: dict[str, Any]) -> dict[str, bool]:
    """Effective on/off state of every mechanism for a cell (defaults True)."""
    return {flag: bool(overrides.get(flag, True)) for flag, _, _ in MECHANISMS}


def _print_cell_header(idx: int, total: int, cell: str, overrides: dict[str, Any]) -> None:
    """Compact per-cell header: the one thing the runner's banner omits --
    which scaffold mechanisms are on/off for this ablation cell."""
    state = _cell_state(overrides)
    changed = [short for flag, short, _ in MECHANISMS if not state[flag]]
    tag = "full scaffold" if not changed else "disabled: " + ", ".join(changed)
    parts = [f"{short}={'ON ' if state[flag] else 'off'}" for flag, short, _ in MECHANISMS]
    print("\n" + f" ABLATION CELL {idx}/{total}: {cell} ({tag}) ".center(72, "#"))
    print("  " + " ".join(parts))


def _cell_config(
    cell: str,
    overrides: dict[str, Any],
    *,
    suite: str,
    dimensions: list[int] | str,
    runs: int,
    workers: int,
    serial: bool,
    output_root: str,
    seed: int,
) -> dict[str, Any]:
    """Build the YAML config mapping for one ablation cell."""
    options = dict(_SGSM_OFF)
    options.update(overrides)
    return {
        "optimizers": ["dt-gsk"],
        "suite": suite,
        "functions": "default",          # suite default set (cec2017 excludes F2)
        "dimensions": dimensions if isinstance(dimensions, str) else list(dimensions),
        "runs": runs,
        "seed": seed,
        "seed_policy": "unified",
        "rand_generator": "threefry",
        "parallel": not serial,
        "workers": workers,
        "generation_logs": False,
        "convergence_graphs": False,
        "overwrite": True,
        "output_root": f"{output_root}/{cell}",
        "optimizer_options": options,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the DT-GSK scaffold ablation.")
    parser.add_argument("--mode", default="remove-one", choices=["remove-one", "add-one"],
                        help="remove-one (default): disable one mechanism from the full scaffold. "
                             "add-one: enable one from bare GSK (ATMALS-GSK-style).")
    parser.add_argument("--suite", default="cec2017", choices=["cec2017", "cec2011", "cec2013"],
                        help="Benchmark suite (default: cec2017). cec2011 uses native dims "
                             "(--dimension ignored); matches ATMALS-GSK's two-suite protocol.")
    parser.add_argument("--dimension", default="30",
                        help="Ablation dimension(s), comma-separated (default: 30; ignored for "
                             "cec2011). Example: --dimension 10,30,50,100.")
    parser.add_argument("--runs", type=int, default=25, help="Runs per cell (default: 25).")
    parser.add_argument("--workers", type=int, default=2, help="Parallel workers (default: 2).")
    parser.add_argument("--serial", action="store_true", help="Run serially (overrides --workers).")
    parser.add_argument("--seed", type=int, default=20240620, help="Base seed (default: 20240620).")
    parser.add_argument(
        "--output-root", default="results/_ablation",
        help="Root for per-cell output (default: results/_ablation).",
    )
    parser.add_argument(
        "--only", default=None,
        help="Comma-separated subset of cell names to run (default: all cells for the mode).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the enabled/disabled matrix and write configs, but do not launch runs.",
    )
    args = parser.parse_args(argv)

    all_cells = _build_cells(args.mode)

    if args.suite == "cec2011":
        dims_field: list[int] | str = "native"
        if args.dimension not in (None, "30"):
            print(f"note: --dimension {args.dimension} ignored for cec2011 (native problem dims).")
    else:
        try:
            parsed = [int(d) for d in str(args.dimension).split(",") if d.strip()]
        except ValueError:
            parser.error(f"--dimension must be comma-separated integers, got {args.dimension!r}")
        if not parsed:
            parser.error("--dimension must list at least one dimension.")
        dims_field = parsed

    if args.only:
        wanted = [c.strip() for c in args.only.split(",") if c.strip()]
        unknown = [c for c in wanted if c not in all_cells]
        if unknown:
            parser.error(f"unknown cell(s): {', '.join(unknown)}. Known: {', '.join(all_cells)}")
        cells = {c: all_cells[c] for c in wanted}
    else:
        cells = all_cells

    total = len(cells)
    print(f"Ablation mode='{args.mode}'  suite={args.suite}  cells={total}  runs={args.runs}")

    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    for idx, (cell, overrides) in enumerate(cells.items(), 1):
        cfg = _cell_config(
            cell, overrides,
            suite=args.suite, dimensions=dims_field, runs=args.runs, workers=args.workers,
            serial=args.serial, output_root=args.output_root, seed=args.seed,
        )
        cfg_path = _CONFIG_DIR / f"{cell}.yml"
        cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
        _print_cell_header(idx, total, cell, overrides)
        if args.dry_run:
            print(f"  (dry-run) config -> {cfg_path}")
            continue
        rc = run_main(["--config", str(cfg_path), "--root", "."])
        if rc != 0:
            failures.append(cell)
            print(f"[{cell}] runner returned {rc}")

    if args.dry_run:
        print(f"\nDry run: wrote {len(cells)} cell config(s) to {_CONFIG_DIR}.")
        return 0
    if failures:
        print(f"\nCompleted with failures in: {', '.join(failures)}")
        return 1
    print(f"\nAblation complete: {len(cells)} cell(s) on {args.suite} under {args.output_root}/.")
    agg = f"--ablation-root {args.output_root} --suite {args.suite}"
    if args.suite != "cec2011":
        agg += f" --dimension <one of {args.dimension}>"
    print(f"Aggregate with: python papers/scripts/generate_ablation_matrix.py {agg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
