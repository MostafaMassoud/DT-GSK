#!/usr/bin/env python3
"""Promote a completed suite's family banks into the reference-results tree.

Implements REFERENCE_PROMOTION_PLAN.md (author-approved 2026-07-28): byte-
faithful, gate-checked promotion of `results/_run_all/<alg>/<suite>/` into
`benchmarks/cec_reference_results/<suite>/<alg>/`, minting a separate,
non-superseding release manifest per suite. The frozen primary release
(rel-2026-07-20-67d9345f9) is never touched.

Usage::

    python papers/scripts/promote_suite.py --suite cec2013lsgo --dry-run
    python papers/scripts/promote_suite.py --suite cec2013lsgo
    python papers/scripts/promote_suite.py --suite cec2020            # refuses
                                                                      # until its
                                                                      # completeness
                                                                      # gate passes

Every invocation re-runs the full preflight gate battery itself (shape, seed
formula + cross-algorithm pairing, budget, summary fidelity, provenance-file
presence), so promotion can never outrun verification. ``--dry-run`` prints the
complete copy/rewrite/exclusion plan and writes nothing.

What is promoted per algorithm (SAP Addendum 1 Section 11; deviation record
D-5/D-8): ``per_run.csv``, the per-dimension summary CSVs, the five provenance
files, and ``gen_logs/``. ``curves/`` and session logs (``*_log_*.txt``) are
EXCLUDED with the exclusion recorded in-manifest. ``skipped_runs.csv`` and
``*.csv.prebugfix`` files are carried under the ``deviation_record`` file class
for cec2013lsgo (they are the evidence behind D-5/D-6); for cec2020 their
presence FAILS the gate. The promoted ``verification.json`` is rewritten to an
honest ``NOT_VERIFIED``/``NO_REFERENCE`` verdict when the staged one is
vacuous (D-8.1); the staging copy is never modified. For cec2013lsgo a
``benchmark_variant.json`` sidecar records the transformed Ackley variant
(D-8.2).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "results" / "_run_all"
REF = ROOT / "benchmarks" / "cec_reference_results"
GOV = ROOT / "papers" / "governance"

ALGS = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk", "dt-gsk"]
PROV_FILES = ["environment.json", "phase0_protocol.json", "run_config.json",
              "seed_schedule.csv", "verification.json"]
SEED_MOD = 2_147_483_646
BASE_SEED = 20240620
FROZEN_PRIMARY = "rel-2026-07-20-67d9345f9"

#: SHA-256 of the pre-registration artifacts bound into every minted manifest.
PREREG = {
    "addendum": "papers/build_prompt_phases/phase_05/statistical_analysis_plan_addendum_cec2020_lsgo.md",
    "addendum_sha256": "4b351008bebf8f41413cca67703fcbad9562dd111befb9e76e81a032429dcea1",
    "amendment_01": "papers/build_prompt_phases/phase_05/statistical_analysis_plan_addendum_cec2020_lsgo_amendment_01.md",
    "amendment_01_sha256": "ef56c224c58a855ceff0771bbca133e60bb917795997ce5b8d4ab5d91cddab5b",
    "signing_commit": "5c9bfae82",
}

SUITES: dict[str, dict] = {
    "cec2013lsgo": {
        "tag": "lsgo",
        # Statistics basis, per benchmark_adapter.protocol: cec2013lsgo is a
        # RAW_OBJECTIVE suite (no unified optimum; its error column is NaN), so
        # its summary tables aggregate best_fitness. cec2020 is an
        # ERROR_VS_OPTIMUM suite and aggregates the floored error instead.
        # Comparing a summary against the wrong column makes every solved cell
        # look catastrophically wrong -- F1 at D=5 has error 0.0 and
        # best_fitness 100.0, i.e. a relative deviation of exactly 1.0.
        "stat_column": "best_fitness",
        "cells": 15, "runs": 25, "rows": 375,
        "dims_of": lambda f: 905 if f in (13, 14) else 1000,
        "summary_dims": [1000, 905],
        "budget_of": lambda dim: 3_000_000,
        "early_stop_ok": False,   # raw-objective suite: every run exhausts the budget
        "deviation_files_ok": True,
        "variant_sidecar": {
            "schema": "benchmark_variant/v1",
            "suite": "cec2013lsgo",
            "ackley_variant": "transformed",
            "functions_affected": [3, 6, 10],
            "detail": ("F3/F6/F10 evaluate the TRANSFORMED Ackley chain "
                       "(T_osz -> T_asy(0.2) -> Lambda(10) -> ackley), Molina-package "
                       "form as used by SHADE-ILS. Published raw-Ackley results "
                       "(e.g. the MOS table) are a different objective on these "
                       "functions and are never comparable to this bank."),
            "authority": "production_deviation_record.md D-8.2; SAP Addendum 1 Section 2",
        },
    },
    "cec2020": {
        "tag": "cec2020",
        "stat_column": "error",
        "cells": 38, "runs": 30, "rows": 1140,
        "dims_of": None,          # cross-product with protocol exclusion, below
        "summary_dims": [5, 10, 15, 20],
        "budget_of": lambda dim: {5: 50_000, 10: 1_000_000, 15: 3_000_000, 20: 10_000_000}[dim],
        "early_stop_ok": True,    # error suite: target_error_reached rows are legal
        "deviation_files_ok": False,
        "variant_sidecar": None,
    },
}

CEC2020_CELLS = [(f, d) for f in range(1, 11) for d in (5, 10, 15, 20)
                 if not (f in (6, 7) and d == 5)]


def sha256_of(path: Path) -> str:
    """Return the SHA-256 of one file."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def unified_seed(func: int, dim: int, run: int) -> int:
    """The unified seed schedule (seed_policy.get_cec_seed)."""
    return (BASE_SEED + 1000003 * dim + 1000033 * func + 1000037 * run) % SEED_MOD + 1


def git(*args: str) -> str:
    """Run git in the monorepo root and return stripped stdout."""
    out = subprocess.run(["git", "-C", str(ROOT)] + list(args),
                         capture_output=True, text=True)
    return out.stdout.strip()


class Gate:
    """Collects gate findings; any finding blocks promotion."""

    def __init__(self) -> None:
        self.failures: list[str] = []

    def check(self, ok: bool, message: str) -> None:
        if not ok:
            self.failures.append(message)

    def abort_if_failed(self, phase: str) -> None:
        if self.failures:
            lines = "\n".join(f"  - {f}" for f in self.failures)
            raise SystemExit(f"PROMOTION REFUSED at {phase}:\n{lines}")


def load_bank(suite: str, alg: str) -> list[dict]:
    """Read one staging bank's per_run rows."""
    path = STAGING / alg / suite / "summary" / "per_run.csv"
    if not path.is_file():
        raise SystemExit(
            f"PROMOTION REFUSED: {path} does not exist -- bank absent. "
            f"For cec2020 this means the campaign has not completed; promotion "
            f"stays locked until every bank passes the completeness gate."
        )
    return list(csv.DictReader(open(path, encoding="utf-8")))


def gate_banks(suite: str, spec: dict, gate: Gate) -> dict[str, list[dict]]:
    """The full preflight battery over all seven staging banks."""
    banks: dict[str, list[dict]] = {}
    for alg in ALGS:
        rows = load_bank(suite, alg)
        banks[alg] = rows
        cells = Counter((int(r["function"]), int(r["dimension"])) for r in rows)
        gate.check(len(rows) == spec["rows"],
                   f"{alg}: {len(rows)} rows, expected {spec['rows']}")
        gate.check(len(cells) == spec["cells"] and all(v == spec["runs"] for v in cells.values()),
                   f"{alg}: cell matrix incomplete ({len(cells)}/{spec['cells']} cells)")
        if suite == "cec2013lsgo":
            for (f, d) in cells:
                gate.check(d == spec["dims_of"](f), f"{alg}: F{f} at D={d} (wrong native dim)")
        else:
            gate.check(sorted(cells) == sorted(CEC2020_CELLS),
                       f"{alg}: cell set differs from the 38-cell protocol")
        run_ids = defaultdict(list)
        for r in rows:
            run_ids[(int(r["function"]), int(r["dimension"]))].append(int(r["run"]))
        gate.check(all(sorted(v) == list(range(1, spec["runs"] + 1)) for v in run_ids.values()),
                   f"{alg}: duplicate or missing run ids")
        for r in rows:
            f, d, run = int(r["function"]), int(r["dimension"]), int(r["run"])
            nfes, budget = int(float(r["nfes"])), spec["budget_of"](int(r["dimension"]))
            v = float(r[spec["stat_column"]])
            gate.check(math.isfinite(v) and v >= 0 or suite == "cec2013lsgo" and math.isfinite(v),
                       f"{alg}: non-finite/invalid {spec['stat_column']} at F{f} D{d} run {run}")
            gate.check(int(r["seed"]) == unified_seed(f, d, run),
                       f"{alg}: seed violates unified formula at F{f} D{d} run {run}")
            if spec["early_stop_ok"]:
                gate.check(nfes == budget or (nfes < budget and r["termination"] == "target_error_reached"),
                           f"{alg}: short run without target_error_reached at F{f} D{d} run {run}")
            else:
                gate.check(nfes == budget, f"{alg}: nfes {nfes} != budget {budget} at F{f} D{d} run {run}")
        summary_dir = STAGING / alg / suite / "summary"
        for pf in PROV_FILES:
            gate.check((summary_dir / pf).is_file(), f"{alg}: missing provenance file {pf}")
        for dim in spec["summary_dims"]:
            gate.check((summary_dir / f"{alg}_{suite}_D{dim}.csv").is_file(),
                       f"{alg}: missing per-dim summary D{dim}")
        if not spec["deviation_files_ok"]:
            strays = list(summary_dir.glob("skipped_runs.csv")) + list(summary_dir.glob("*.prebugfix"))
            gate.check(not strays,
                       f"{alg}: deviation files present where none are expected: "
                       f"{[s.name for s in strays]}")

    # Cross-algorithm pairing: identical seed per (function, dimension, run).
    ref = {(int(r["function"]), int(r["dimension"]), int(r["run"])): int(r["seed"])
           for r in banks[ALGS[0]]}
    mismatches = sum(
        1 for alg in ALGS[1:] for r in banks[alg]
        if ref.get((int(r["function"]), int(r["dimension"]), int(r["run"]))) != int(r["seed"])
    )
    gate.check(mismatches == 0, f"cross-algorithm seed pairing: {mismatches} mismatches")

    # Summary fidelity: per-dim summary means must match per_run recomputation.
    worst = 0.0
    for alg in ALGS:
        raw = defaultdict(list)
        for r in banks[alg]:
            raw[(int(r["function"]), int(r["dimension"]))].append(float(r[spec["stat_column"]]))
        for dim in spec["summary_dims"]:
            spath = STAGING / alg / suite / "summary" / f"{alg}_{suite}_D{dim}.csv"
            if not spath.is_file():
                continue
            for r in csv.DictReader(open(spath, encoding="utf-8")):
                fid = int(str(r.get("function") or r.get("Function")).strip().lstrip("Ff"))
                if (fid, dim) not in raw:
                    continue
                mean = float(r.get("mean") or r.get("Mean"))
                ref_mean = statistics.fmean(raw[(fid, dim)])
                if ref_mean != 0.0:
                    worst = max(worst, abs(mean - ref_mean) / abs(ref_mean))
                else:
                    worst = max(worst, abs(mean - ref_mean))
    gate.check(worst <= 5e-11, f"summary fidelity: worst rel deviation {worst:.3e} > 5e-11")
    return banks


def gate_cec2020_lock(gate: Gate) -> None:
    """Stage-2 unlock conditions beyond the shared battery (plan Section 4)."""
    for alg in ALGS:
        bank_dir = STAGING / alg / "cec2020"
        # git -C ROOT resolves pathspecs against ROOT, so pass ROOT-relative.
        status = git("status", "--porcelain", "--",
                     str(bank_dir.relative_to(ROOT)).replace("\\", "/"))
        gate.check(status == "",
                   f"{alg}: staging tree not committed (the author's single "
                   f"end-of-campaign commit is a promotion precondition); git "
                   f"reports changes under {bank_dir}")


def rewrite_verification(staged: dict) -> tuple[dict, bool]:
    """Return the promoted verification payload (honest verdict) and whether it changed."""
    vacuous = (staged.get("verdict") == "CONSISTENT"
               and int(staged.get("functions_checked", 0)) == 0
               and int(staged.get("missing_reference", 0)) > 0)
    if staged.get("verdict") == "DEVIATES":
        raise SystemExit("PROMOTION REFUSED: staged verification.json says DEVIATES")
    if vacuous or staged.get("verdict") == "NOT_VERIFIED":
        out = dict(staged)
        out["verdict"] = "NOT_VERIFIED"
        out["reason"] = "NO_REFERENCE"
        out["promotion_note"] = (
            "Verdict normalized at promotion per production_deviation_record.md "
            "D-8.1 and SAP Addendum 1 Section 11: no reference bank exists for "
            "this suite, so nothing was comparable and a CONSISTENT verdict "
            "would be vacuous. The staging copy is unmodified."
        )
        return out, True
    return dict(staged), False


def collect_plan(suite: str, spec: dict) -> list[dict]:
    """Build the per-file promotion plan: src, dst, file_class, transform."""
    plan: list[dict] = []
    for alg in ALGS:
        src_summary = STAGING / alg / suite / "summary"
        dst = REF / suite / alg
        for name in ["per_run.csv", "seed_schedule.csv", "environment.json",
                     "phase0_protocol.json", "run_config.json"]:
            plan.append({"src": src_summary / name, "dst": dst / name,
                         "class": "result_data" if name.endswith(".csv") else "provenance",
                         "transform": None})
        plan.append({"src": src_summary / "verification.json",
                     "dst": dst / "verification.json",
                     "class": "provenance", "transform": "verification"})
        for dim in spec["summary_dims"]:
            name = f"{alg}_{suite}_D{dim}.csv"
            plan.append({"src": src_summary / name, "dst": dst / name,
                         "class": "result_data", "transform": None})
        for gl in sorted((STAGING / alg / suite / "gen_logs").glob("*.csv")):
            plan.append({"src": gl, "dst": dst / "gen_logs" / gl.name,
                         "class": "result_data", "transform": None})
        if spec["deviation_files_ok"]:
            for dev in sorted(src_summary.glob("skipped_runs.csv")) + sorted(src_summary.glob("*.prebugfix")):
                plan.append({"src": dev, "dst": dst / dev.name,
                             "class": "deviation_record", "transform": None})
        if spec["variant_sidecar"]:
            plan.append({"src": None, "dst": dst / "benchmark_variant.json",
                         "class": "variant_sidecar", "transform": "variant"})
    return plan


def count_exclusions(suite: str) -> dict[str, int]:
    """Count the file classes deliberately not promoted."""
    curves = logs = 0
    for alg in ALGS:
        curves += len(list((STAGING / alg / suite / "curves").glob("*.csv")))
        logs += len(list((STAGING / alg / suite / "summary").glob("*_log_*.txt")))
    return {"curve_csvs_excluded": curves, "session_logs_excluded": logs}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--suite", required=True, choices=sorted(SUITES))
    ap.add_argument("--dry-run", action="store_true",
                    help="print the full plan and gate results; write nothing")
    args = ap.parse_args(argv)
    suite, spec = args.suite, SUITES[args.suite]

    dst_root = REF / suite
    if dst_root.exists():
        raise SystemExit(
            f"PROMOTION REFUSED: {dst_root} already exists. Promotions are "
            f"one-shot into a fresh directory; a re-promotion requires an "
            f"explicit revert of the prior mint first (plan Section 5 rollback)."
        )

    print(f"== promote_suite: {suite} ==")
    gate = Gate()
    gate_banks(suite, spec, gate)
    if suite == "cec2020":
        gate_cec2020_lock(gate)
    gate.abort_if_failed("preflight")
    print(f"preflight: PASS ({len(ALGS)} banks x {spec['rows']} rows; "
          f"pairing 0 mismatches)")

    plan = collect_plan(suite, spec)
    exclusions = count_exclusions(suite)
    head = git("rev-parse", "HEAD")
    release_id = f"{spec['tag']}-rel-{datetime.now(timezone.utc):%Y-%m-%d}-{head[:9]}"
    manifest_path = GOV / f"evidence_release_manifest_{suite}.json"

    n_by_class = Counter(p["class"] for p in plan)
    print(f"plan: {len(plan)} files -> {dst_root}  {dict(n_by_class)}")
    print(f"exclusions (recorded in-manifest): {exclusions}")
    print(f"release_id: {release_id}")
    print(f"manifest  : {manifest_path.relative_to(ROOT)}")

    if args.dry_run:
        for p in plan:
            src = p["src"].relative_to(ROOT) if p["src"] else "(generated)"
            note = f"  [{p['class']}]" + (f" transform={p['transform']}" if p["transform"] else "")
            print(f"  {src} -> {p['dst'].relative_to(ROOT)}{note}")
        print("DRY RUN: nothing written.")
        return 0

    # ---- execute ----------------------------------------------------------
    entries = []
    for p in plan:
        p["dst"].parent.mkdir(parents=True, exist_ok=True)
        if p["transform"] == "verification":
            staged = json.loads(p["src"].read_text(encoding="utf-8"))
            payload, _ = rewrite_verification(staged)
            p["dst"].write_text(json.dumps(payload, indent=2, sort_keys=True),
                                encoding="utf-8")
        elif p["transform"] == "variant":
            p["dst"].write_text(json.dumps(spec["variant_sidecar"], indent=2,
                                           ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            shutil.copyfile(p["src"], p["dst"])
            if sha256_of(p["src"]) != sha256_of(p["dst"]):
                raise SystemExit(f"PROMOTION ABORTED: copy divergence at {p['dst']}")
        entries.append({
            "path": p["dst"].relative_to(REF).as_posix(),
            "sha256": sha256_of(p["dst"]),
            "bytes": p["dst"].stat().st_size,
            "file_class": p["class"],
        })

    manifest = {
        "schema": "suite_evidence_manifest/v1",
        "release_id": release_id,
        "anchor_commit": head,
        "evidence_root": "benchmarks/cec_reference_results",
        "release_scope": [suite],
        "supersedes_release": None,
        "supersession_note": (
            f"Separate, non-superseding release. The primary release "
            f"{FROZEN_PRIMARY} (cec2017/cec2011/cec2013) is untouched and "
            f"remains authoritative for its suites."
        ),
        "preregistration": PREREG,
        "staging_source": {
            "root": f"results/_run_all/<alg>/{suite}/",
            "bank_production_commits": {
                alg: json.loads((STAGING / alg / suite / "summary" / "environment.json")
                                .read_text(encoding="utf-8")).get("git_commit")
                for alg in ALGS
            },
        },
        "exclusions": exclusions,
        "creation_record": {
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "created_by": "papers/scripts/promote_suite.py",
            "command": f"python papers/scripts/promote_suite.py --suite {suite}",
        },
        "totals": {"files": len(entries), "bytes": sum(e["bytes"] for e in entries)},
        "files": entries,
    }
    manifest_path.write_bytes(
        json.dumps(manifest, indent=2, ensure_ascii=False).replace("\n", "\r\n").encode("utf-8")
        + b"\r\n")

    # ---- post-verify ------------------------------------------------------
    reread = json.loads(manifest_path.read_text(encoding="utf-8"))
    bad = [e["path"] for e in reread["files"]
           if sha256_of(REF / e["path"]) != e["sha256"]]
    if bad:
        raise SystemExit(f"POST-VERIFY FAILED: {len(bad)} hash mismatches, e.g. {bad[:3]}")
    promoted_rows = sum(
        1 for alg in ALGS
        for _ in csv.DictReader(open(REF / suite / alg / "per_run.csv", encoding="utf-8"))
    )
    if promoted_rows != spec["rows"] * len(ALGS):
        raise SystemExit(f"POST-VERIFY FAILED: promoted per_run rows {promoted_rows}")
    print(f"post-verify: PASS ({len(entries)} files re-hashed; "
          f"{promoted_rows} per_run rows across {len(ALGS)} banks)")
    print(f"MINTED {release_id}")
    print("Next: run the union strict-inventory gate:")
    print("  python papers/scripts/check_manifest.py "
          "--manifest papers/governance/evidence_release_manifest.json "
          f"--manifest papers/governance/evidence_release_manifest_{suite}.json "
          "--strict-inventory")
    return 0


if __name__ == "__main__":
    sys.exit(main())
