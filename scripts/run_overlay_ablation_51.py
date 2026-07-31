#!/usr/bin/env python3
"""Run the SGSM-overlay direct-isolation ablation (X-ABL-02) at 51 runs per cell
--- instead of the 25-run default --- for CEC2017 (D50, D100) and CEC2013 (D50),
to match the primary panel's statistical power.

It reuses the frozen 4-cell overlay configs (full / no_sgsm / no_adaptive /
no_finalpolish), overrides only ``runs`` and ``output_root``, and writes the
51-run outputs to *_51 staging roots so the existing 25-run configs and results
are left completely untouched (both survive side by side, separate and
traceable). Paired design is preserved: all four cells of a suite share one
seed / runs / suite / dims and differ only in optimizer_options.

Single command:

    python scripts/run_overlay_ablation_51.py

Options: --dry-run (write the 51-run configs, print the plan, launch nothing);
--only full,no_sgsm (subset of cells); --suite cec2017 (restrict to one suite);
--workers N (override the frozen configs' worker count - throughput only,
results are worker-count independent).

51-run outputs:
    results/_ablation_sgsm_51/<cell>            (CEC2013 D50)
    results/_ablation_sgsm_cec2017_51/<cell>    (CEC2017 D50, D100)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG_DIR = ROOT / "configs" / "_ablation"
RUNS_51 = 51
CELLS = ["full", "no_sgsm", "no_adaptive", "no_finalpolish"]

# (label, config-stem template, 25-run root -> 51-run root)
SUITES = [
    ("cec2017", "overlay_{cell}_cec2017",
     "results/_ablation_sgsm_cec2017", "results/_ablation_sgsm_cec2017_51"),
    ("cec2013", "overlay_{cell}",
     "results/_ablation_sgsm", "results/_ablation_sgsm_51"),
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--suite", choices=["cec2017", "cec2013"], default=None,
                    help="Restrict to one suite (default: both).")
    ap.add_argument("--only", default=None,
                    help="Comma-separated subset of cells (default: all four).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Write the 51-run configs and print the plan; launch nothing.")
    ap.add_argument("--workers", type=int, default=None,
                    help="Override the frozen configs' worker count (default: "
                         "keep each config's value; throughput only).")
    args = ap.parse_args(argv)

    cells = [c.strip() for c in args.only.split(",")] if args.only else CELLS
    suites = [s for s in SUITES if (args.suite is None or s[0] == args.suite)]

    out_dir = CFG_DIR / "_51run"
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs: list[tuple[str, str, Path]] = []
    for label, stem_t, root25, root51 in suites:
        for cell in cells:
            src = CFG_DIR / f"{stem_t.format(cell=cell)}.yml"
            if not src.is_file():
                print(f"error: config not found: {src}"); return 2
            cfg = yaml.safe_load(src.read_text(encoding="utf-8"))
            cfg["runs"] = RUNS_51
            cfg["output_root"] = f"{root51}/{cell}"      # separate from the 25-run root
            if args.workers is not None:
                cfg["workers"] = args.workers
            dst = out_dir / f"{stem_t.format(cell=cell)}_51.yml"
            dst.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
            jobs.append((label, cell, dst))

    print(f"51-run SGSM-overlay ablation: {len(jobs)} cell(s) "
          f"({', '.join(sorted({j[0] for j in jobs}))}); runs={RUNS_51}.")
    for label, cell, dst in jobs:
        print(f"  {label:8s} {cell:15s} -> {yaml.safe_load(dst.read_text())['output_root']}")
    if args.dry_run:
        print(f"\nDry run: wrote {len(jobs)} config(s) to {out_dir}. Launched nothing.")
        return 0

    for i, (label, cell, dst) in enumerate(jobs, 1):
        print(f"\n=== [{i}/{len(jobs)}] {label} / {cell} (runs={RUNS_51}) ===")
        rc = subprocess.run([sys.executable, "run.py", "--config", str(dst), "--root", "."],
                            cwd=str(ROOT)).returncode
        if rc != 0:
            print(f"FAILED: {label}/{cell} (rc={rc}); stopping."); return rc

    print("\n51-run overlay ablation complete. Outputs under "
          "results/_ablation_sgsm_51/ (CEC2013 D50) and "
          "results/_ablation_sgsm_cec2017_51/ (CEC2017 D50,D100); the 25-run "
          "results/_ablation_sgsm[_cec2017]/ trees are untouched.\n"
          "Next (promotion, keeping 25-run and 51-run separate): move these into "
          "benchmarks/cec_reference_results/_ablation/overlay_51runs/<cell>/... "
          "(parallel to the 25-run overlay/), then aggregate each panel with\n"
          "  python papers/scripts/generate_ablation_matrix.py "
          "--ablation-root benchmarks/cec_reference_results/_ablation/overlay_51runs "
          "--suite cec2017 --dimension 50 --full-cell full")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
