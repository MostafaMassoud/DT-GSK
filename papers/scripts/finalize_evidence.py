#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""One-command finalization of the post-fix (C006 + M038) evidence campaign.

Runs the COMPLETE chain from raw staging to rebuilt paper artifacts:

    P0  preflight        verify every staging bundle is complete (row counts,
                         cells, provenance) and every pipeline tool is patched
    P1  audit-promotion  RETIRED (2026-07-18): per-release audit copies under
                         _releases/ are no longer minted -- git history is the
                         audit record. No-op; the promotion that populates the
                         read-path is P2. scripts/promote_evidence.py remains an
                         optional MANUAL audit-copy tool.
    P2  flat-refresh     replace benchmarks/cec_reference_results/<suite>/dt-gsk
                         (the layout gsk-stats and every paper script read)
    P3  ablation         (re)build _ablation scaffold+overlay cells (51 runs)
                         and the overlay analysis, then mint manifest.json
                         with a superseding release id. Works whether the old
                         _ablation tree is still on disk or was deleted: the
                         manifest template + narrative docs are recovered from
                         git history when absent.
    P4  oracle           no-op by design: the exploratory oracle study
                         (former S6.7) and the _oracle release were removed
                         from the paper (2026-07-18), so the manuscript cites
                         no oracle evidence. If _oracle is present it is
                         verified; if absent (the expected state) it is left
                         absent -- never restored.
    P5  stats            gsk-stats x3 in --strict-source mode (flat-layout
                         integrity verification)
    P6  release+phase6   regenerate papers/governance/evidence_release_manifest
                         .json (fresh SHA-256 tree walk; comparators must be
                         byte-identical), then run phase6_run_analysis.py under
                         GSK_REL_ID/GSK_ANCHOR -> papers/analysis/<new-id>/
    P7  paper-tables     promote results/paper_tables -> _paper_tables, then
                         generate_word_sources.py
    P8  phase12          regenerate scaffold rank matrices + descriptive
                         deltas, re-mint ablation_results_manifest.json,
                         render SA01/SA02/fig via generate_ablation_exhibits.py
    P9  downstream       every table/figure generator (latex tables, T16 BCa,
                         robustness, convergence x3, Nemenyi, rank charts,
                         trace, NLPSR, params panel, overlay effects x2,
                         artifact binding)
    P10 builds           deterministic PDF (double-build hash check),
                         supplementary, DOCX x2 + validators
    P11 gates            pytest, ruff, profile lock, docs html; check_manifest
                         expected-fail -> _pending_refreeze.json
    P12 report           old-vs-new headline diff + human follow-up checklist
                         -> results/_finalize/finalize_report.md

Usage::

    python papers/scripts/finalize_evidence.py --dry-run      # preflight only
    python papers/scripts/finalize_evidence.py                # full chain
    python papers/scripts/finalize_evidence.py --from-phase P6
    python papers/scripts/finalize_evidence.py --from-phase P6  # re-mint only

Progress is checkpointed in results/_finalize/state.json: a re-invocation
skips completed phases (the minted release ids are stable across resumes).
Staging under results/ is never deleted - releases are refreshed by copy.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import json
import math
import os
import shutil
import stat
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

REF = ROOT / "benchmarks" / "cec_reference_results"
ABL = REF / "_ablation"
SCAF = ABL / "scaffold"
OV = ABL / "overlay"
ANA = OV / "analysis"
ORACLE = REF / "_oracle"
PT_REF = REF / "_paper_tables"
PT_STAGING = ROOT / "results" / "paper_tables"

STAGE_RUNALL = ROOT / "results" / "_run_all" / "dt-gsk"
STAGE_SCAFFOLD = ROOT / "results" / "_ablation"
STAGE_OV17 = ROOT / "results" / "_ablation_sgsm_cec2017_51"
STAGE_OV13 = ROOT / "results" / "_ablation_sgsm_51"

PHASE12 = ROOT / "papers" / "build_prompt_phases" / "phase_12"
ABLRES = PHASE12 / "ablation_results"
GOV = ROOT / "papers" / "governance"

FIN = ROOT / "results" / "_finalize"
STATE_PATH = FIN / "state.json"
LOG_PATH = FIN / "finalize.log"

OLD_REL_ID = "rel-2026-07-10-262fc16c9"

#: The release the submitted manuscript cites by name. It is frozen, published
#: and permanently referenced; it is never re-run, re-minted or superseded.
FROZEN_PRIMARY_REL_ID = "rel-2026-07-20-67d9345f9"

#: Opt-in for the two phases that would rewrite the primary namespace.
PRIMARY_REMINT_ENV = "GSK_ALLOW_PRIMARY_REMINT"

# Primary-suite staging contract (runs already fixed by protocol: 51/51/25).
# "curves" = expected representative curve count (one per function x dim);
# gen_logs mirror curves 1:1 in the flat evidence layout.
CEC2011_DIMS = [1, 6, 7, 12, 13, 15, 20, 22, 26, 30, 40, 96, 120, 126, 140, 240]
SUITES = {
    "cec2017": {"dims": [10, 30, 50, 100], "funcs": 29, "runs": 51,
                "per_run_rows": 5916, "curves": 116,
                "summaries": [f"dt-gsk_cec2017_D{d}.csv" for d in (10, 30, 50, 100)]},
    "cec2013": {"dims": [10, 30, 50], "funcs": 28, "runs": 51,
                "per_run_rows": 4284, "curves": 84,
                "summaries": [f"dt-gsk_cec2013_D{d}.csv" for d in (10, 30, 50)]},
    "cec2011": {"dims": CEC2011_DIMS, "funcs": 22, "runs": 25,
                "per_run_rows": 550, "curves": 22,
                "summaries": (["dt-gsk_cec2011.csv"]
                              + [f"dt-gsk_cec2011_D{d}.csv" for d in CEC2011_DIMS])},
}
PROV_FILES = ["environment.json", "phase0_protocol.json", "run_config.json",
              "seed_schedule.csv", "verification.json"]
SCAFFOLD_CELLS = ["baseline", "no_ace", "no_arch", "no_bse",
                  "no_linkage", "no_localsearch", "no_psr"]
OVERLAY_CELLS = ["full", "no_sgsm", "no_adaptive", "no_finalpolish"]
ABL_RUNS = 51

PDF_EPOCH = "1783468800"          # frozen SOURCE_DATE_EPOCH for the PDFs

_LOG_FH = None


# --------------------------------------------------------------------------- #
# infrastructure
# --------------------------------------------------------------------------- #
def log(msg: str) -> None:
    line = msg.rstrip("\n")
    print(line, flush=True)
    if _LOG_FH is not None:
        _LOG_FH.write(line + "\n")
        _LOG_FH.flush()


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def base_env(extra: dict | None = None) -> dict:
    env = os.environ.copy()
    for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "NUMBA_NUM_THREADS"):
        env[k] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env.pop("VISIO_OLE_FLOWCHARTS", None)
    if extra:
        env.update(extra)
    return env


def run_py(rel_script: str, *args: str, env_extra: dict | None = None,
           module: bool = False, allow_fail: bool = False) -> tuple[int, str]:
    """Run a project python script (or -m module); echo + log its tail."""
    cmd = [sys.executable]
    cmd += ["-m", rel_script] if module else [str(ROOT / rel_script)]
    cmd += list(args)
    log(f"    $ {' '.join(Path(c).name if os.sep in c else c for c in cmd)}")
    r = subprocess.run(cmd, cwd=str(ROOT), env=base_env(env_extra),
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    out = (r.stdout or "") + (("\n" + r.stderr) if r.stderr else "")
    if _LOG_FH is not None:
        _LOG_FH.write(out + "\n")
        _LOG_FH.flush()
    if r.returncode != 0 and not allow_fail:
        tail = "\n".join(out.strip().splitlines()[-25:])
        raise RuntimeError(f"{rel_script} exited {r.returncode}:\n{tail}")
    return r.returncode, out


def git_head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT),
                          capture_output=True, text=True,
                          check=True).stdout.strip()


def _git_commits_touching(rel_posix: str, limit: int = 25) -> list[str]:
    """Commits (newest first) that touched a repo path, cwd-relative."""
    r = subprocess.run(["git", "rev-list", "-n", str(limit), "HEAD", "--",
                        f"./{rel_posix}"], cwd=str(ROOT),
                       capture_output=True, text=True)
    return [c for c in r.stdout.split() if c]


def git_show_last(rel_posix: str) -> bytes | None:
    """Bytes of a tracked file from the most recent commit that contains it
    (survives an already-committed deletion)."""
    for c in _git_commits_touching(rel_posix):
        r = subprocess.run(["git", "show", f"{c}:./{rel_posix}"],
                           cwd=str(ROOT), capture_output=True)
        if r.returncode == 0:
            return r.stdout
    return None


def git_restore_tree(rel_posix: str) -> bool:
    """Restore a deleted tracked file or directory tree into the working tree
    from the most recent commit that contains it. Index is left untouched."""
    for c in _git_commits_touching(rel_posix):
        ls = subprocess.run(["git", "ls-tree", "-r", c, "--", f"./{rel_posix}"],
                            cwd=str(ROOT), capture_output=True, text=True)
        if ls.returncode == 0 and ls.stdout.strip():
            r = subprocess.run(["git", "restore", "--source", c, "--worktree",
                                "--", f"./{rel_posix}"], cwd=str(ROOT),
                               capture_output=True, text=True)
            if r.returncode == 0:
                return True
    return False


def rmtree_force(path: Path) -> None:
    def _onerr(fn, p, exc):
        os.chmod(p, stat.S_IWRITE)
        fn(p)
    if path.exists():
        shutil.rmtree(path, onerror=_onerr)


def count_rows(csv_path: Path) -> int:
    with csv_path.open(encoding="utf-8", newline="") as fh:
        return max(0, sum(1 for _ in fh) - 1)


def per_run_dim_counts(csv_path: Path) -> dict[int, int]:
    out: dict[int, int] = {}
    with csv_path.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            d = int(r["dimension"])
            out[d] = out.get(d, 0) + 1
    return out


def load_state() -> dict:
    if STATE_PATH.is_file():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict) -> None:
    FIN.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=1) + "\n", encoding="utf-8")


def copy_cell_tree(src: Path, dst: Path, summary_whitelist: list[str],
                   flat_top: bool,
                   require: dict[str, int] | None = None) -> dict[str, int]:
    """Copy a run bundle. flat_top lifts summary/* to the top (flat layout);
    otherwise the summary/ subdir is preserved (ablation release layout).
    `require` maps count keys to exact expected values, verified BEFORE the
    destructive swap - an incomplete bundle must never replace a good tree."""
    counts = {"summary": 0, "curves": 0, "gen_logs": 0, "ignored": 0}
    tmp = dst.parent / (dst.name + ".__new__")
    rmtree_force(tmp)
    top = tmp if flat_top else tmp / "summary"
    top.mkdir(parents=True, exist_ok=True)
    src_summary = src / "summary"
    for f in sorted(src_summary.iterdir()):
        if f.is_file() and f.name in summary_whitelist:
            shutil.copy2(f, top / f.name)
            counts["summary"] += 1
        elif f.is_file():
            counts["ignored"] += 1
    src_curves = src / "curves"
    if src_curves.is_dir():
        (tmp / "curves").mkdir(exist_ok=True)
        for f in sorted(src_curves.glob("*.csv")):
            shutil.copy2(f, tmp / "curves" / f.name)
            counts["curves"] += 1
    if flat_top:
        src_logs = src / "gen_logs"
        if src_logs.is_dir():
            (tmp / "gen_logs").mkdir(exist_ok=True)
            for f in sorted(src_logs.glob("*.csv")):
                shutil.copy2(f, tmp / "gen_logs" / f.name)
                counts["gen_logs"] += 1
    if require:
        bad = {k: (counts[k], want) for k, want in require.items()
               if counts[k] != want}
        if bad:
            rmtree_force(tmp)
            raise RuntimeError(
                f"{src} -> {dst.name}: staged bundle incomplete, refusing the "
                f"tree swap: " + ", ".join(
                    f"{k}={got} (want {want})" for k, (got, want) in bad.items()))
    rmtree_force(dst)
    tmp.rename(dst)
    return counts


def summary_whitelist(suite: str) -> list[str]:
    return PROV_FILES + ["per_run.csv"] + SUITES[suite]["summaries"]


# --------------------------------------------------------------------------- #
# P0 preflight
# --------------------------------------------------------------------------- #
def _check_bundle_extras(src: Path, problems: list[str], label: str, *,
                         curves_expect: int | None = None,
                         genlogs_expect: int | None = None,
                         summary_rows: dict[str, int] | None = None) -> None:
    """Depth checks beyond file presence: curve/gen_log inventories and
    summary row counts. Without these, a partially-staged bundle would pass
    preflight and the destructive tree swaps would mint a shrunken release."""
    if curves_expect is not None:
        d = src / "curves"
        got = len(list(d.glob("*.csv"))) if d.is_dir() else 0
        if got != curves_expect:
            problems.append(f"{label}: curves/*.csv = {got} "
                            f"(want {curves_expect})")
    if genlogs_expect is not None:
        d = src / "gen_logs"
        got = len(list(d.glob("*.csv"))) if d.is_dir() else 0
        if got != genlogs_expect:
            problems.append(f"{label}: gen_logs/*.csv = {got} "
                            f"(want {genlogs_expect})")
    if summary_rows:
        for name, want in summary_rows.items():
            p = src / "summary" / name
            if p.is_file() and count_rows(p) != want:
                problems.append(f"{label}: summary/{name} rows "
                                f"{count_rows(p)} (want {want})")


def check_staging_bundle(src: Path, suite: str, problems: list[str],
                         label: str, dim_expect: dict[int, int], *,
                         curves_expect: int | None = None,
                         genlogs_expect: int | None = None) -> None:
    s = src / "summary"
    if not s.is_dir():
        problems.append(f"{label}: missing {s}")
        return
    for name in SUITES[suite]["summaries"] + PROV_FILES + ["per_run.csv"]:
        if not (s / name).is_file():
            problems.append(f"{label}: missing summary/{name}")
    pr = s / "per_run.csv"
    if pr.is_file():
        got = per_run_dim_counts(pr)
        for d, want in dim_expect.items():
            if got.get(d, 0) != want:
                problems.append(
                    f"{label}: per_run rows D{d} = {got.get(d, 0)} (want {want})")
        extra = set(got) - set(dim_expect)
        if extra:
            problems.append(f"{label}: per_run has unexpected dims {sorted(extra)}")
    spec = SUITES[suite]
    _check_bundle_extras(
        src, problems, label,
        curves_expect=curves_expect, genlogs_expect=genlogs_expect,
        summary_rows={n: spec["funcs"]
                      for n in spec["summaries"] if "_D" in n})


def phase_P0(state: dict, dry: bool) -> None:
    problems: list[str] = []

    # tool-patch guards: refuse to run against unpatched scripts
    guards = [
        ("papers/scripts/phase6_run_analysis.py", "GSK_REL_ID"),
        ("papers/scripts/generate_word_sources.py", "GSK_REL_ID"),
        ("papers/scripts/generate_t16_bca.py", "GSK_REL_ID"),
        ("papers/scripts/generate_nemenyi_cd.py", "GSK_REL_ID"),
        ("papers/scripts/generate_rank_charts.py", "GSK_REL_ID"),
        ("papers/scripts/posthoc_robustness_cec2017.py", "GSK_REL_ID"),
        ("papers/scripts/generate_artifact_binding.py", "GSK_REL_ID"),
        ("papers/scripts/regen_cec2017_contrasts.py", "GSK_OVL_SUITE"),
        ("papers/scripts/ablation_overlay_effects.py", "GSK_OVL_SUITE"),
        ("papers/scripts/generate_ablation_exhibits.py", "GSK_ABL_RUNS"),
        ("papers/build_prompt_phases/phase_07/validate_exhibits.py", "GSK_REL_ID"),
    ]
    for rel, needle in guards:
        p = ROOT / rel
        if not p.is_file() or needle not in p.read_text(encoding="utf-8"):
            problems.append(f"tool not patched for env overrides: {rel} ({needle})")
    csel = ROOT / "papers/build_prompt_phases/phase_05/curve_selection.csv"
    if "dtgsk_standing" not in csel.read_text(encoding="utf-8").splitlines()[0]:
        problems.append("phase_05/curve_selection.csv header still pre-rename")

    # primary suites
    for suite, spec in SUITES.items():
        per_dim = {d: spec["funcs"] * spec["runs"] for d in spec["dims"]}
        if suite == "cec2011":
            # per_run for cec2011 records per-problem rows at their native dims;
            # only the total is contracted.
            src = STAGE_RUNALL / suite
            s = src / "summary"
            if not s.is_dir():
                problems.append(f"{suite}: missing {s}")
            else:
                for name in spec["summaries"] + PROV_FILES + ["per_run.csv"]:
                    if not (s / name).is_file():
                        problems.append(f"{suite}: missing summary/{name}")
                pr = s / "per_run.csv"
                if pr.is_file() and count_rows(pr) != spec["per_run_rows"]:
                    problems.append(f"{suite}: per_run rows {count_rows(pr)} "
                                    f"(want {spec['per_run_rows']})")
                _check_bundle_extras(
                    src, problems, suite,
                    curves_expect=spec["curves"],
                    genlogs_expect=spec["curves"],
                    summary_rows={"dt-gsk_cec2011.csv": spec["funcs"]})
        else:
            check_staging_bundle(STAGE_RUNALL / suite, suite, problems,
                                 suite, per_dim,
                                 curves_expect=spec["curves"],
                                 genlogs_expect=spec["curves"])

    # scaffold cells (CEC2017, 4 dims, 51 runs; curves promoted, gen_logs not)
    for cell in SCAFFOLD_CELLS:
        src = STAGE_SCAFFOLD / cell / "dt-gsk" / "cec2017"
        check_staging_bundle(src, "cec2017", problems, f"scaffold/{cell}",
                             {d: 29 * ABL_RUNS for d in (10, 30, 50, 100)},
                             curves_expect=116)

    # overlay cells: cec2017 D50/D100 and cec2013 D50
    for cell in OVERLAY_CELLS:
        src = STAGE_OV17 / cell / "dt-gsk" / "cec2017"
        s = src / "summary"
        if not s.is_dir():
            problems.append(f"overlay17/{cell}: missing {s}")
        else:
            for name in ["per_run.csv", "dt-gsk_cec2017_D50.csv",
                         "dt-gsk_cec2017_D100.csv"] + PROV_FILES:
                if not (s / name).is_file():
                    problems.append(f"overlay17/{cell}: missing summary/{name}")
            pr = s / "per_run.csv"
            if pr.is_file():
                got = per_run_dim_counts(pr)
                for d in (50, 100):
                    if got.get(d, 0) != 29 * ABL_RUNS:
                        problems.append(f"overlay17/{cell}: per_run rows D{d} = "
                                        f"{got.get(d, 0)} (want {29 * ABL_RUNS})")
            _check_bundle_extras(
                src, problems, f"overlay17/{cell}", curves_expect=58,
                summary_rows={"dt-gsk_cec2017_D50.csv": 29,
                              "dt-gsk_cec2017_D100.csv": 29})
        src = STAGE_OV13 / cell / "dt-gsk" / "cec2013"
        s = src / "summary"
        if not s.is_dir():
            problems.append(f"overlay13/{cell}: missing {s}")
        else:
            for name in ["per_run.csv", "dt-gsk_cec2013_D50.csv"] + PROV_FILES:
                if not (s / name).is_file():
                    problems.append(f"overlay13/{cell}: missing summary/{name}")
            pr = s / "per_run.csv"
            if pr.is_file():
                got = per_run_dim_counts(pr)
                if got.get(50, 0) != 28 * ABL_RUNS:
                    problems.append(f"overlay13/{cell}: per_run rows D50 = "
                                    f"{got.get(50, 0)} (want {28 * ABL_RUNS})")
            _check_bundle_extras(
                src, problems, f"overlay13/{cell}", curves_expect=28,
                summary_rows={"dt-gsk_cec2013_D50.csv": 28})

    # frozen inputs: present on disk, or recoverable from git history
    if not (ORACLE / "manifest.json").is_file():
        log("  NOTE: _oracle is absent by design (the oracle study was removed "
            "from the paper 2026-07-18); P4 is a no-op.")
    if not (ABL / "manifest.json").is_file() and not _git_commits_touching(
            "benchmarks/cec_reference_results/_ablation/manifest.json"):
        problems.append("_ablation/manifest.json absent on disk AND in git "
                        "history - no metadata template to mint from")
    if not (ROOT / "papers" / "analysis" / OLD_REL_ID).is_dir():
        problems.append(f"old analysis bundle papers/analysis/{OLD_REL_ID} "
                        "missing (needed for the P12 diff report)")
    if not (GOV / "evidence_release_manifest.json").is_file():
        problems.append("papers/governance/evidence_release_manifest.json missing")

    if problems:
        log("P0 PREFLIGHT FAILED - the campaign staging is not complete:")
        for p in problems:
            log(f"  - {p}")
        raise SystemExit(2)

    # self-healing checkpoints: if a completed phase's outputs were deleted
    # again (the user may clear evidence trees between runs), re-run it
    # instead of letting a later phase crash on the missing inputs.
    completed = set(state.get("completed", []))
    healed = []
    if "P2" in completed and any(not (REF / s / "dt-gsk").is_dir()
                                 for s in SUITES):
        healed += ["P2"]
    if "P3" in completed and not (ABL / "manifest.json").is_file():
        healed += ["P3"]
    if "P4" in completed and not (ORACLE / "manifest.json").is_file():
        healed += ["P4"]
    if "P7" in completed and not (PT_REF / "provenance.json").is_file():
        healed += ["P7"]
    if healed:
        # everything downstream of the earliest healed phase must also re-run
        ids = [pid for pid, _, _ in PHASES]
        cut = min(ids.index(p) for p in healed)
        cleared = sorted(completed & set(ids[cut:]))
        completed -= set(ids[cut:])
        state["completed"] = sorted(completed)
        log(f"  self-heal: outputs of {'/'.join(healed)} were deleted after "
            f"completion - re-running {', '.join(cleared)}")

    # mint stable release ids once
    head = git_head()
    if "new_rel_id" not in state:
        today = _dt.date.today().isoformat()
        state["new_rel_id"] = f"rel-{today}-{head[:9]}"
        state["new_abl_id"] = f"abl-rel-{today}"
        state["anchor"] = head
    log(f"  preflight OK; release ids: {state['new_rel_id']} / "
        f"{state['new_abl_id']} (anchor {state['anchor'][:9]})")
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=str(ROOT),
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        log("  NOTE: working tree is dirty; anchor_commit records HEAD as of "
            "now - commit the finalized artifacts afterwards (see P12 report).")


# --------------------------------------------------------------------------- #
# P1 audit promotion
# --------------------------------------------------------------------------- #
def phase_P1(state: dict, dry: bool) -> None:
    # Per-release audit copies under _releases/ were RETIRED (2026-07-18):
    # git history is the audit record (evidence_rerun_runbook.md Sec. 5.1).
    # This phase no longer mints them. The promotion that actually populates the
    # read-path is P2 (flat-refresh), which copies staging straight into
    # <suite>/dt-gsk and never depended on this phase. scripts/promote_evidence
    # .py remains available as an optional MANUAL audit-copy tool, but is no
    # longer invoked automatically.
    state["audit_promotion"] = "RETIRED (git history is the audit record)"
    log("  audit copies to _releases/ are retired (git history is the audit "
        "record); the flat-tree promotion is P2. Nothing to do.")


# --------------------------------------------------------------------------- #
# P2 flat-layout refresh
# --------------------------------------------------------------------------- #
def _refuse_primary_remint(phase: str, what: str) -> None:
    """Abort unless the operator has explicitly opted into rewriting the
    frozen primary namespace.

    P2 overwrites benchmarks/cec_reference_results/<suite>/dt-gsk in place and
    P6 mints a NEW release id over the same tree. Both were correct during the
    2026-07 campaign; both are now destructive, because the manuscript,
    supplement and archived release all cite FROZEN_PRIMARY_REL_ID by name and
    reproduce against those exact bytes. The CEC2020 and CEC2013LSGO evidence
    is promoted into SEPARATE, non-superseding underscore releases instead.
    """
    if os.environ.get(PRIMARY_REMINT_ENV) == "1":
        log(f"  !! {phase}: {PRIMARY_REMINT_ENV}=1 -- proceeding against the "
            f"frozen primary namespace at the operator's explicit request.")
        return
    raise SystemExit(
        f"{phase} REFUSED: it would {what}, but {FROZEN_PRIMARY_REL_ID} is "
        f"frozen, published and cited by name in the manuscript, the "
        f"supplement and the archived release -- its bytes are what readers "
        f"reproduce against.\n"
        f"New suites are promoted into separate underscore releases, not by "
        f"re-minting this one.\n"
        f"If you genuinely intend to rewrite the primary namespace, re-run "
        f"with {PRIMARY_REMINT_ENV}=1 and record the authorization in "
        f"papers/governance/decision_log.md first."
    )


def phase_P2(state: dict, dry: bool) -> None:
    _refuse_primary_remint(
        "P2", "overwrite benchmarks/cec_reference_results/<suite>/dt-gsk in place")
    for suite, spec in SUITES.items():
        src = STAGE_RUNALL / suite
        dst = REF / suite / "dt-gsk"
        wl = summary_whitelist(suite)
        counts = copy_cell_tree(src, dst, wl, flat_top=True,
                                require={"summary": len(wl),
                                         "curves": spec["curves"],
                                         "gen_logs": spec["curves"]})
        log(f"  {suite}/dt-gsk refreshed: {counts['summary']} summary, "
            f"{counts['curves']} curves, {counts['gen_logs']} gen_logs "
            f"({counts['ignored']} staging extras ignored)")


# --------------------------------------------------------------------------- #
# P3 ablation release refresh + manifest re-mint
# --------------------------------------------------------------------------- #
def _run_matrix(root: Path, suite: str, dim: int, full_cell: str, out: Path,
                expect_cells: set[str]) -> None:
    """Run generate_ablation_matrix with a no-op guard: the tool exits 0 even
    when it writes nothing (e.g. a cell dropped out of discovery), which
    would leave a stale prior-campaign CSV to be minted as fresh."""
    if out.exists():
        out.chmod(stat.S_IWRITE)
        out.unlink()
    run_py("papers/scripts/generate_ablation_matrix.py",
           "--ablation-root", str(root), "--suite", suite,
           "--dimension", str(dim), "--full-cell", full_cell,
           "--out", str(out))
    if not out.is_file():
        raise RuntimeError(f"ablation matrix wrote nothing for {suite} D{dim} "
                           f"({out.name}) - cell discovery incomplete?")
    with out.open(encoding="utf-8", newline="") as fh:
        cells = {r["cell"].strip() for r in csv.DictReader(fh)}
    if cells != expect_cells:
        raise RuntimeError(f"{out.name}: cells {sorted(cells)} != expected "
                           f"{sorted(expect_cells)}")


def _refresh_overlay_analysis(state: dict) -> None:
    """Generate the canonical overlay analysis set (rank summary +
    per-function means per suite/dim, contrasts per suite) unconditionally -
    the tree may have been deleted, so nothing is name-gated on what exists."""
    import generate_ablation_matrix as gam  # noqa: PLC0415

    ANA.mkdir(parents=True, exist_ok=True)
    for suite, dims in (("cec2017", [50, 100]), ("cec2013", [50])):
        for dim in dims:
            out = ANA / f"ablation_overlay_rank_summary_{suite}_D{dim}.csv"
            _run_matrix(OV, suite, dim, "full", out, set(OVERLAY_CELLS))
            means = gam._discover_cells(OV, suite, dim)
            funcs = sorted(set.intersection(*(set(m) for m in means.values())))
            disabled = [c for c in OVERLAY_CELLS if c != "full"]
            out = ANA / f"overlay_per_function_means_{suite}_D{dim}.csv"
            if out.exists():
                out.chmod(stat.S_IWRITE)
            with out.open("w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["function"] + [f"{c}_mean" for c in OVERLAY_CELLS]
                           + [f"wtl_full_vs_{c}" for c in disabled])
                for f in funcs:
                    row = [f] + [f"{means[c][f]:.10e}" for c in OVERLAY_CELLS]
                    for c in disabled:
                        fm, cm = means["full"][f], means[c][f]
                        row.append("W" if fm < cm else ("L" if fm > cm else "T"))
                    w.writerow(row)
        # contrasts JSONs (full CEC2013-parity schema) + manifest checksum
        # refresh (the regen tool skips the refresh gracefully if the manifest
        # is absent; the re-mint below rebuilds it either way)
        run_py("papers/scripts/regen_cec2017_contrasts.py",
               env_extra={"GSK_OVL_SUITE": suite,
                          "GSK_OVL_DIMS": ",".join(str(d) for d in dims),
                          "GSK_OVL_RUNS": str(ABL_RUNS)})


def _set_runs_recursive(obj, old=25, new=ABL_RUNS) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "runs" and v == old:
                obj[k] = new
            else:
                _set_runs_recursive(v, old, new)
    elif isinstance(obj, list):
        for v in obj:
            _set_runs_recursive(v, old, new)


def _remint_ablation_manifest(state: dict) -> None:
    # tolerate CRLF-materialized checkouts (core.autocrlf smudges the LF blob
    # on Windows); the re-mint below rewrites the file in canonical LF form
    raw = (ABL / "manifest.json").read_bytes().decode("utf-8").replace("\r\n", "\n")
    man = json.loads(raw)
    # guard against self-supersession on a P3 re-run: if the on-disk manifest
    # is already our own output, the true predecessor is what IT superseded
    old_release = man.get("release_id", "unknown")
    if old_release == state["new_abl_id"]:
        old_release = man.get("supersedes_release", "unknown")
    state.setdefault("abl_supersedes", old_release)
    old_release = state["abl_supersedes"]

    def _origin(rel_path: str) -> str:
        """The actual staging origin of a re-promoted file (provenance must
        describe the 51-run bytes, not the superseded campaign's sources)."""
        parts = rel_path.split("/")
        if parts[0] == "scaffold":
            return (f"results/_ablation/{parts[1]}/dt-gsk/cec2017 "
                    "(51-run rerun promoted by finalize_evidence.py)")
        if parts[0] == "overlay" and parts[1] == "analysis":
            return ("regenerated from the promoted 51-run overlay evidence "
                    "by finalize_evidence.py")
        if parts[0] == "overlay":
            root = ("results/_ablation_sgsm_cec2017_51" if "cec2017" in parts
                    else "results/_ablation_sgsm_51")
            return (f"{root}/{parts[1]} "
                    "(51-run rerun promoted by finalize_evidence.py)")
        return "51-run rerun promoted by finalize_evidence.py"

    kept, dropped, refreshed = [], [], 0
    seen = set()
    for f in man["files"]:
        disk = ABL / f["path"]
        if not disk.is_file():
            dropped.append(f["path"])
            continue
        new_sha = sha256(disk)
        if new_sha != f["sha256"]:
            f["sha256"] = new_sha
            f["size_bytes"] = disk.stat().st_size
            refreshed += 1
            # the bytes changed: the old source/source_class describe the
            # superseded 25-run campaign and would be false provenance
            if "source" in f:
                f["source"] = _origin(f["path"])
            if "source_class" in f:
                f["source_class"] = "rerun_51"
        kept.append(f)
        seen.add(f["path"])

    def _candidates() -> list[tuple[str, str, dict]]:
        out = []
        for cell in SCAFFOLD_CELLS:
            base = SCAF / cell / "dt-gsk" / "cec2017"
            for cur in sorted((base / "curves").glob("*.csv")):
                out.append((cur.relative_to(ABL).as_posix(), "scaffold",
                            {"kind": "curve"}))
            for name in summary_whitelist("cec2017"):
                p = base / "summary" / name
                if p.is_file():
                    out.append((p.relative_to(ABL).as_posix(), "scaffold", {}))
        for cell in OVERLAY_CELLS:
            for suite in ("cec2017", "cec2013"):
                base = OV / cell / "dt-gsk" / suite
                if not base.is_dir():
                    continue
                for cur in sorted((base / "curves").glob("*.csv")):
                    out.append((cur.relative_to(ABL).as_posix(), "overlay",
                                {"kind": "curve"}))
                for name in summary_whitelist(suite):
                    p = base / "summary" / name
                    if p.is_file():
                        out.append((p.relative_to(ABL).as_posix(), "overlay", {}))
        for p in sorted(ANA.iterdir()):
            if p.is_file():
                out.append((p.relative_to(ABL).as_posix(), "overlay_analysis", {}))
        return out

    added = 0
    for rel_path, group, extra in _candidates():
        if rel_path in seen:
            continue
        disk = ABL / rel_path
        entry = {"path": rel_path, "group": group, **extra,
                 "size_bytes": disk.stat().st_size, "sha256": sha256(disk),
                 "source": _origin(rel_path)}
        kept.append(entry)
        seen.add(rel_path)
        added += 1
    man["files"] = kept

    # metadata: supersession + run counts + row-count verification
    new_abl = state["new_abl_id"]
    man["supersedes_release"] = old_release
    man["release_id"] = new_abl
    man["supersession_note"] = (
        f"{new_abl} supersedes {old_release}: complete 51-run regeneration of "
        "the scaffold (X-ABL-01) and overlay (X-ABL-02) cells with the "
        "post-freeze code fixes applied (C006 final-polish stale-incumbent fix "
        "+ M038 interaction-graph numba import fix; bit-identical arithmetic "
        "for the graph, trajectory-changing for the D>=50 polish). All cells "
        "rerun at 51 runs (previously 25); overlay analysis regenerated from "
        "the new runs; prior release recoverable via git history.")
    man["git_head_51run_rerun"] = state["anchor"]
    _set_runs_recursive(man.get("studies", {}))

    rcv: dict = {"scaffold": {}, "overlay": {}, "overlay_cec2017": {}}
    for cell in SCAFFOLD_CELLS:
        pr = SCAF / cell / "dt-gsk" / "cec2017" / "summary" / "per_run.csv"
        got = per_run_dim_counts(pr)
        ok = all(got.get(d, 0) == 29 * ABL_RUNS for d in (10, 30, 50, 100))
        rcv["scaffold"][cell] = {
            "by_dim": {str(d): got.get(d, 0) for d in (10, 30, 50, 100)},
            "n_funcs_per_dim": {str(d): 29 for d in (10, 30, 50, 100)},
            "all_51_runs": ok, "ok": ok}
        if not ok:
            raise RuntimeError(f"scaffold {cell}: row-count verification failed")
    for cell in OVERLAY_CELLS:
        pr = OV / cell / "dt-gsk" / "cec2013" / "summary" / "per_run.csv"
        got = per_run_dim_counts(pr)
        ok = got.get(50, 0) == 28 * ABL_RUNS
        rcv["overlay"][cell] = {"by_dim": {"50": got.get(50, 0)},
                                "n_funcs_per_dim": {"50": 28},
                                "all_51_runs": ok, "ok": ok}
        pr = OV / cell / "dt-gsk" / "cec2017" / "summary" / "per_run.csv"
        got = per_run_dim_counts(pr)
        ok = all(got.get(d, 0) == 29 * ABL_RUNS for d in (50, 100))
        rcv["overlay_cec2017"][cell] = {
            "by_dim": {str(d): got.get(d, 0) for d in (50, 100)},
            "n_funcs_per_dim": {str(d): 29 for d in (50, 100)},
            "all_51_runs": ok, "ok": ok}
        if not (rcv["overlay"][cell]["ok"] and rcv["overlay_cec2017"][cell]["ok"]):
            raise RuntimeError(f"overlay {cell}: row-count verification failed")
    man["row_count_verification"] = rcv

    # findings blocks from the freshly regenerated contrasts JSONs
    def _findings(suite: str, dims: list[int]) -> tuple[dict, dict]:
        analysis, finding = {}, {}
        for dim in dims:
            j = json.loads((ANA / f"overlay_contrasts_{suite}_D{dim}.json")
                           .read_text(encoding="utf-8"))
            analysis[f"D{dim}"] = j["friedman_omnibus"]
            ns = j["contrasts"]["no_sgsm"]["holm"]
            fp = j["contrasts"]["no_finalpolish"]["holm"]
            dr = j["contrasts"]["no_sgsm"]["direction"]["delta_rank_vs_full"]
            finding[f"D{dim}"] = {
                "sgsm_significant_benefit": ns["significant_at_0.05"],
                "no_sgsm_holm_p": ns["p_holm"],
                "no_sgsm_delta_rank_vs_full": dr,
                "finalpolish_significant": fp["significant_at_0.05"],
                "finalpolish_holm_p": fp["p_holm"],
                "headline": (
                    f"At {suite.upper()} D{dim} (51 runs) the direct SGSM "
                    f"isolation (full vs no_sgsm) "
                    + ("shows a Holm-significant effect"
                       if ns["significant_at_0.05"]
                       else "shows NO significant standalone benefit")
                    + f" (Holm p={ns['p_holm']:.3g}); the ISM-dependent final "
                    f"polish contrast has Holm p={fp['p_holm']:.3g}"
                    + (" (significant)." if fp["significant_at_0.05"]
                       else " (not significant)."))}
        return analysis, finding

    # cec2013 blocks keep their pre-registered shape (test/multiplicity/
    # ranking/correction_trigger_mapping survive verbatim); only the
    # data-derived values are replaced from the regenerated contrasts JSON
    j13 = json.loads((ANA / "overlay_contrasts_cec2013_D50.json")
                     .read_text(encoding="utf-8"))
    oa = man.get("overlay_analysis")
    if isinstance(oa, dict) and "test" in oa:
        oa["friedman_omnibus"] = j13["friedman_omnibus"]
        oa["contrasts"] = {
            c: {"p_raw": d["holm"]["p_raw"], "p_holm": d["holm"]["p_holm"],
                "significant_at_0.05": d["holm"]["significant_at_0.05"],
                "delta_rank_vs_full": d["direction"]["delta_rank_vs_full"],
                "wtl_full_vs_cell": d["wtl_full_vs_cell"]}
            for c, d in j13["contrasts"].items()}
    else:
        man["overlay_analysis"] = _findings("cec2013", [50])[0]
    of = man.get("overlay_finding")
    if isinstance(of, dict) and "correction_trigger_mapping" in of:
        ns = j13["contrasts"]["no_sgsm"]
        ag = j13["contrasts"]["no_adaptive"]
        fp = j13["contrasts"]["no_finalpolish"]
        of["sgsm_significant_d50_benefit"] = ns["holm"]["significant_at_0.05"]
        of["adaptive_gate_significant"] = ag["holm"]["significant_at_0.05"]
        of["final_polish_significant"] = fp["holm"]["significant_at_0.05"]
        w = ns["wtl_full_vs_cell"]
        of["headline"] = (
            "At CEC2013 D50 (SGSM-active tier; 51-run rerun) the DIRECT SGSM "
            "isolation (full vs no_sgsm) "
            + ("shows a Holm-significant effect"
               if ns["holm"]["significant_at_0.05"]
               else "shows NO significant standalone benefit")
            + f" (Holm p={ns['holm']['p_holm']:.3g}; W/T/L "
            f"{w['wins_full_better']}/{w['ties']}/{w['losses_full_worse']}). "
            f"Adaptive gate Holm p={ag['holm']['p_holm']:.3g}; eigenframe "
            f"final polish Holm p={fp['holm']['p_holm']:.3g}"
            + (" (significant)." if fp["holm"]["significant_at_0.05"]
               else " (not significant)."))
        if isinstance(of.get("honesty"), str) and not of["honesty"].startswith("["):
            of["honesty"] = ("[25-run-era statement; re-evaluate against the "
                             "51-run rerun] " + of["honesty"])
    else:
        man["overlay_finding"] = _findings("cec2013", [50])[1]
    man["overlay_analysis_cec2017"], man["overlay_finding_cec2017"] = \
        _findings("cec2017", [50, 100])

    if isinstance(man.get("baseline_d100_composition"), dict) and \
            "superseded_by_51run_rerun" not in man["baseline_d100_composition"]:
        man["baseline_d100_composition"] = {
            "superseded_by_51run_rerun": True,
            "note": ("the 25-run baseline D100 cell composition described below "
                     "was replaced by the single-batch 51-run rerun of "
                     f"{new_abl}; retained for audit only"),
            "previous": man["baseline_d100_composition"]}

    man["totals"] = {"files": len(man["files"]),
                     "bytes": sum(f["size_bytes"] for f in man["files"])}
    groups: dict = {}
    for f in man["files"]:
        g = groups.setdefault(f["group"], {"files": 0, "bytes": 0})
        g["files"] += 1
        g["bytes"] += f["size_bytes"]
    man["groups"] = groups

    # study-level file/byte counts must describe the NEW file set
    x1 = man.get("studies", {}).get("X-ABL-01_scaffold")
    if isinstance(x1, dict):
        sc = [f for f in man["files"] if f["group"] == "scaffold"]
        x1["files"] = len(sc)
        x1["bytes"] = sum(f["size_bytes"] for f in sc)
    x2 = man.get("studies", {}).get("X-ABL-02_sgsm_overlay")
    if isinstance(x2, dict):
        # the top-level X-ABL-02 counts describe the CEC2013 D50 panel
        # (curves excluded, matching the original field semantics)
        c13 = [f for f in man["files"] if f["group"] == "overlay"
               and "/cec2013/" in f["path"] and "/curves/" not in f["path"]]
        a13 = [f for f in man["files"] if f["group"] == "overlay_analysis"
               and ("cec2013" in f["path"] or f["path"].endswith(".md"))]
        x2["cell_files"] = len(c13)
        x2["analysis_files"] = len(a13)
        x2["files"] = len(c13) + len(a13)
        x2["bytes"] = sum(f["size_bytes"] for f in c13 + a13)

    # verification records only what THIS re-mint establishes (the carried
    # read-only / prior-manifest-reverified claims would be false)
    man["verification"] = {
        "files_verified": len(man["files"]),
        "sha256_recomputed_from_disk": True,
        "rerun_51_refresh": {"refreshed": refreshed, "added": added,
                             "dropped": len(dropped),
                             "dropped_paths": dropped},
    }

    if man["supersedes_release"] == man["release_id"]:
        raise RuntimeError("refusing to mint a self-superseding _ablation "
                           "manifest (release chain corruption)")
    out = ABL / "manifest.json"
    out.chmod(stat.S_IWRITE)
    out.write_bytes(json.dumps(man, indent=1, ensure_ascii=False).encode("utf-8"))
    bad = [f["path"] for f in man["files"] if sha256(ABL / f["path"]) != f["sha256"]]
    if bad:
        raise RuntimeError(f"_ablation manifest self-check failed: {bad[:5]}")
    log(f"  _ablation manifest re-minted as {new_abl}: {refreshed} refreshed, "
        f"{added} added, {len(dropped)} dropped; self-check OK "
        f"({len(man['files'])} files)")


def phase_P3(state: dict, dry: bool) -> None:
    # Deletion tolerance: if the user cleared _ablation, recover the manifest
    # (metadata template + supersession chain) and the two narrative analysis
    # docs from git history. The data cells are fully rebuilt from staging.
    base_rel = "benchmarks/cec_reference_results/_ablation"
    for rel in ("manifest.json", "overlay/analysis/overlay_findings.md",
                "overlay/analysis/overlay_validation.md"):
        dst = ABL / rel
        if dst.is_file():
            continue
        blob = git_show_last(f"{base_rel}/{rel}")
        if blob is None:
            if rel == "manifest.json":
                raise RuntimeError(
                    "_ablation/manifest.json absent on disk and in git history")
            log(f"  WARNING: _ablation/{rel} unrecoverable from git - it will "
                "drop out of the minted manifest")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(blob)
        log(f"  recovered _ablation/{rel} from git history")

    wl17 = summary_whitelist("cec2017")
    for cell in SCAFFOLD_CELLS:
        src = STAGE_SCAFFOLD / cell / "dt-gsk" / "cec2017"
        dst = SCAF / cell / "dt-gsk" / "cec2017"
        c = copy_cell_tree(src, dst, wl17, flat_top=False,
                           require={"summary": len(wl17), "curves": 116})
        log(f"  scaffold/{cell}: {c['summary']} summary + {c['curves']} curves")
    for cell in OVERLAY_CELLS:
        src = STAGE_OV17 / cell / "dt-gsk" / "cec2017"
        dst = OV / cell / "dt-gsk" / "cec2017"
        # overlay cec2017 runs cover D50/D100 only -> 8 of the 10 whitelist
        # names exist (no D10/D30 summaries)
        c = copy_cell_tree(src, dst, wl17, flat_top=False,
                           require={"summary": len(wl17) - 2, "curves": 58})
        log(f"  overlay/{cell}/cec2017: {c['summary']} summary + {c['curves']} curves")
        src = STAGE_OV13 / cell / "dt-gsk" / "cec2013"
        dst = OV / cell / "dt-gsk" / "cec2013"
        wl13 = PROV_FILES + ["per_run.csv", "dt-gsk_cec2013_D50.csv"]
        c = copy_cell_tree(src, dst, wl13, flat_top=False,
                           require={"summary": len(wl13), "curves": 28})
        log(f"  overlay/{cell}/cec2013: {c['summary']} summary + {c['curves']} curves")
    _refresh_overlay_analysis(state)
    _remint_ablation_manifest(state)


# --------------------------------------------------------------------------- #
# P4 oracle integrity check (no rerun staged; stays pre-fix + disclosed)
# --------------------------------------------------------------------------- #
def phase_P4(state: dict, dry: bool) -> None:
    if not (ORACLE / "manifest.json").is_file():
        # The oracle study (former S6.7) and _oracle were removed from the paper
        # (2026-07-18); the manuscript cites no oracle evidence, so absence is
        # the correct, expected state and P4 never restores it.
        state["oracle_disposition"] = "ABSENT (oracle study removed from paper 2026-07-18)"
        log("  _oracle is absent by design (oracle study removed from the "
            "manuscript); nothing to verify or restore.")
        return
    state.setdefault("oracle_disposition", "present, verified")
    man = json.loads((ORACLE / "manifest.json").read_text(encoding="utf-8"))
    files = man.get("files", {})
    items = files.items() if isinstance(files, dict) else \
        ((f["path"], f) for f in files)

    def _hash_matches(p: Path, want: str) -> bool:
        # The oracle manifest binds mint-time bytes with a MIXED line-ending
        # basis, and git's autocrlf materializes text files differently per
        # checkout - so accept the raw bytes or either EOL normalization.
        data = p.read_bytes()
        lf = data.replace(b"\r\n", b"\n")
        for variant in (data, lf, lf.replace(b"\n", b"\r\n")):
            if hashlib.sha256(variant).hexdigest() == want:
                return True
        return False

    bad = []
    n = 0
    for rel_path, meta in items:
        p = ORACLE / rel_path
        want = meta.get("sha256") if isinstance(meta, dict) else None
        if not p.is_file() or (want and not _hash_matches(p, want)):
            bad.append(rel_path)
        n += 1
    if bad:
        raise RuntimeError(f"_oracle release integrity check failed: {bad}")
    log(f"  _oracle intact ({n} tracked files verified). The oracle study was "
        "removed from the manuscript (2026-07-18); this check runs only when an "
        "_oracle release happens to be present, and the paper cites none of it.")


# --------------------------------------------------------------------------- #
# P5 strict-source stats over the refreshed flat layout
# --------------------------------------------------------------------------- #
def phase_P5(state: dict, dry: bool) -> None:
    wrapper = ("from gsk_family.cli.stats import main; import sys; "
               "sys.exit(main(sys.argv[1:]))")
    for suite in ("CEC2017", "CEC2013", "CEC2011"):
        out_dir = FIN / f"stats_{suite.lower()}"
        cmd = [sys.executable, "-c", wrapper, "--suite", suite,
               "--strict-source", "--no-figures", "--out", str(out_dir)]
        log(f"    $ gsk-stats --suite {suite} --strict-source")
        r = subprocess.run(cmd, cwd=str(ROOT), env=base_env(),
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        if _LOG_FH is not None:
            _LOG_FH.write((r.stdout or "") + (r.stderr or "") + "\n")
        if r.returncode != 0:
            tail = "\n".join(((r.stdout or "") + (r.stderr or ""))
                             .strip().splitlines()[-20:])
            raise RuntimeError(f"gsk-stats {suite} failed:\n{tail}")


# --------------------------------------------------------------------------- #
# P6 evidence release manifest + phase6 analysis bundle
# --------------------------------------------------------------------------- #
def _classify(rel_path: str) -> str:
    parts = rel_path.split("/")
    name = parts[-1]
    if len(parts) == 1 and name == "README.md":
        return "tree_readme"
    if "curves" in parts[:-1]:
        return "curve_csv"
    if "gen_logs" in parts[:-1]:
        return "gen_log_csv"
    fixed = {"per_run.csv": "per_run", "environment.json": "environment_json",
             "phase0_protocol.json": "phase0_protocol_json",
             "run_config.json": "run_config_json",
             "seed_schedule.csv": "seed_schedule",
             "verification.json": "verification_json"}
    if name in fixed:
        return fixed[name]
    if name.endswith(".csv"):
        return "summary_csv"
    return "other_" + (name.rsplit(".", 1)[-1] if "." in name else "unknown")


def phase_P6(state: dict, dry: bool) -> None:
    _refuse_primary_remint(
        "P6", "re-mint evidence_release_manifest.json under a NEW release id "
              "and re-run phase6 analysis over the primary suites")
    old = json.loads((GOV / "evidence_release_manifest.json")
                     .read_text(encoding="utf-8"))

    entries = []
    readme = REF / "README.md"
    if readme.is_file():
        entries.append(("README.md", readme))
    for suite_dir in sorted(p for p in REF.iterdir()
                            if p.is_dir() and not p.name.startswith("_")):
        for f in sorted(suite_dir.rglob("*")):
            if f.is_file():
                entries.append((f.relative_to(REF).as_posix(), f))
    entries.sort(key=lambda t: t[0])

    files, class_counts, suites_agg = [], {}, {}
    for rel_path, p in entries:
        cls = _classify(rel_path)
        if cls.startswith("other_"):
            raise RuntimeError(f"unclassifiable file in evidence tree: {rel_path}")
        size = p.stat().st_size
        files.append({"path": rel_path, "size_bytes": size, "sha256": sha256(p)})
        class_counts[cls] = class_counts.get(cls, 0) + 1
        parts = rel_path.split("/")
        if len(parts) >= 3:
            s = suites_agg.setdefault(parts[0], {"files": 0, "bytes": 0,
                                                 "optimizers": {}})
            s["files"] += 1
            s["bytes"] += size
            o = s["optimizers"].setdefault(parts[1], {"files": 0, "bytes": 0,
                                                      "classes": {}})
            o["files"] += 1
            o["bytes"] += size
            o["classes"][cls] = o["classes"].get(cls, 0) + 1

    # Integrity guard: every comparator EVIDENCE file outside */dt-gsk/* must be
    # byte-identical, because a silent change there would alter reported numbers
    # without any record of it.
    #
    # Documentation is held to a different rule. No reported number derives from
    # the evidence tree's README, and pooling it with the data made this guard
    # fire on a CORRECT documentation update: the README stopped describing the
    # oracle study and the _releases audit copies, both of which are retired --
    # as P1 and P4 of this same script already state. A gate that blocks on that
    # trains its operator to bypass it, which is worse than the drift it guards.
    # So a documentation *change* is reported loudly and allowed; a documentation
    # file going *missing* is still treated as drift.
    DOC_FILES = {"README.md"}
    new_by_path = {f["path"]: f["sha256"] for f in files}
    diffs: list[str] = []
    doc_changes: list[str] = []
    for f in old["files"]:
        if "/dt-gsk/" in f["path"]:
            continue
        got = new_by_path.get(f["path"])
        if got == f["sha256"]:
            continue
        entry = f["path"] + (" (missing)" if got is None else " (changed)")
        if f["path"] in DOC_FILES and got is not None:
            doc_changes.append(entry)
        else:
            diffs.append(entry)
    for d in doc_changes:
        print(f"  NOTE documentation changed since the previous release: {d}")
        print("       no reported number derives from it; all comparator "
              "evidence files verified byte-identical")
    if diffs:
        raise RuntimeError(
            "comparator evidence files changed - refusing to mint a release over "
            f"unexplained evidence drift: {diffs[:10]}")

    # guard against self-supersession on a P6 re-run: if the on-disk manifest
    # is already our own output, the true predecessor is what IT superseded
    prev = old["release_id"]
    if prev == state["new_rel_id"]:
        prev = old.get("supersedes_release") or OLD_REL_ID
    state.setdefault("rel_supersedes", prev)
    prev = state["rel_supersedes"]
    man = {
        "schema": old["schema"],
        "release_id": state["new_rel_id"],
        "anchor_commit": state["anchor"],
        "evidence_root": old["evidence_root"],
        "release_scope": old["release_scope"],
        "supersedes_release": prev,
        "supersession_note": (
            f"{state['new_rel_id']} supersedes {prev}: dt-gsk "
            "cells regenerated with the post-freeze code fixes (C006 "
            "final-polish stale-incumbent + M038 interaction-graph numba "
            "import); comparator cells verified byte-identical to the prior "
            "release during minting."),
        "creation_record": {
            "created_utc": _dt.datetime.now(_dt.timezone.utc)
            .isoformat(timespec="seconds"),
            "created_by": "papers/scripts/finalize_evidence.py (phase P6)",
            "phase": "post-fix evidence finalization",
            "generator": "papers/scripts/finalize_evidence.py",
            "command": "python papers/scripts/finalize_evidence.py"},
        "totals": {"files": len(files),
                   "bytes": sum(f["size_bytes"] for f in files),
                   "file_class_counts": class_counts},
        "suites": suites_agg,
        "files": files,
    }
    (GOV / "evidence_release_manifest.json").write_bytes(
        json.dumps(man, indent=1, ensure_ascii=False).encode("utf-8"))
    log(f"  evidence_release_manifest.json re-minted: {len(files)} files, "
        f"comparators byte-verified vs {old['release_id']}")

    run_py("papers/scripts/phase6_run_analysis.py",
           env_extra={"GSK_REL_ID": state["new_rel_id"],
                      "GSK_ANCHOR": state["anchor"],
                      "GSK_STRICT_SOURCE": "1"})
    log(f"  phase6 bundle written: papers/analysis/{state['new_rel_id']}")


# --------------------------------------------------------------------------- #
# P7 _paper_tables promotion + word sources
# --------------------------------------------------------------------------- #
def _remint_paper_tables_manifest(state: dict) -> None:
    """Re-mint _paper_tables/manifest.json against the freshly promoted
    tables. Without this, the manifest keeps binding the SUPERSEDED release's
    hashes - a false release record (audit finding F1)."""
    man_path = PT_REF / "manifest.json"
    old = json.loads(man_path.read_text(encoding="utf-8")) \
        if man_path.is_file() else {}
    prov = json.loads((PT_REF / "provenance.json").read_text(encoding="utf-8"))
    rel = state["new_rel_id"]
    if prov.get("release_id") != rel:
        raise RuntimeError("_paper_tables/provenance.json does not bind the "
                           "campaign release - promote before re-minting")

    tracked = sorted(PT_REF.glob("T*.csv")) + [PT_REF / "provenance.json"]
    files = [{"path": p.name, "size_bytes": p.stat().st_size,
              "sha256": sha256(p)} for p in tracked]
    by_name = {f["path"]: f["sha256"] for f in files}
    chain = {}
    for name, exp in prov.get("exports", {}).items():
        chain[name] = {
            "promoted_sha256": by_name.get(name),
            "bundle_sources": exp.get("sources", []),
            "bundle_source_sha256": exp.get("source_sha256", {}),
            "derivation": exp.get("derivation", ""),
        }
    prev_rel = old.get("release_id")
    if prev_rel == rel:                       # re-run: keep the true chain
        prev_rel = old.get("supersedes_release")
    man = {
        "schema": "paper_tables_promotion_manifest/v2-flat",
        "release_id": rel,
        "anchor_commit": state["anchor"],
        "study_id": "X-PT-01",
        "restructured_utc": old.get("restructured_utc"),
        "restructure_note": old.get("restructure_note"),
        "path_convention": ("Every 'path' is relative to this manifest's "
                            "directory (benchmarks/cec_reference_results/"
                            "_paper_tables/)."),
        "git_head_promotion": git_head(),
        "tool": "papers/scripts/finalize_evidence.py (P7 promotion + manifest re-mint)",
        "process": old.get("process",
                           "PAPER_BUILD_PROMPT.md Section 2.4 controlled "
                           "staging-to-evidence promotion (paper table inputs)"),
        "note": ("These are the AUTHORITATIVE, machine-readable table-input "
                 "CSVs (T1-T16) that the paper's rendered LaTeX/Word tables "
                 "are generated from. They were exported EXCLUSIVELY from the "
                 f"controlled analysis bundle papers/analysis/{rel}/ by the "
                 "Phase 6 exporter and promoted here byte-identically."),
        "source_bundle": {
            "path": f"papers/analysis/{rel}",
            "release_id": rel,
            "anchor_commit": state["anchor"],
            "generator": prov.get("generator",
                                  "papers/scripts/phase6_run_analysis.py"),
            "command": prov.get("command",
                                "python papers/scripts/phase6_run_analysis.py"),
        },
        "supersedes_release": prev_rel,
        "supersession_note": (
            f"{rel} tables supersede the {prev_rel} export: full re-export "
            "from the 51-run post-fix analysis bundle (C006 + M038 "
            "corrections). Prior manifest recoverable via git history."
            if prev_rel else None),
        "verification": {
            "byte_verified": True,
            "files_verified": len(files),
            "sha256_recomputed_from_disk": True,
            "mismatches": 0,
            "provenance_release_id_verified": True,
        },
        "totals": {"files": len(files),
                   "bytes": sum(f["size_bytes"] for f in files)},
        "table_provenance_chain": chain,
        "files": files,
    }
    if man_path.exists():
        man_path.chmod(stat.S_IWRITE)
    man_path.write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
    log(f"  _paper_tables/manifest.json re-minted for {rel} "
        f"({len(files)} files hashed)")


def phase_P7(state: dict, dry: bool) -> None:
    prov = PT_STAGING / "provenance.json"
    if not prov.is_file():
        raise RuntimeError("results/paper_tables/provenance.json missing - "
                           "phase6 (P6) must run first")
    j = json.loads(prov.read_text(encoding="utf-8"))
    if j.get("release_id") != state["new_rel_id"]:
        raise RuntimeError(f"staged paper tables bind {j.get('release_id')}, "
                           f"expected {state['new_rel_id']}")
    staged = sorted(PT_STAGING.glob("T*.csv")) + [prov]
    PT_REF.mkdir(parents=True, exist_ok=True)
    for oldf in list(PT_REF.glob("T*.csv")) + [PT_REF / "provenance.json"]:
        if oldf.exists():
            oldf.chmod(stat.S_IWRITE)
            oldf.unlink()
    for f in staged:
        shutil.copy2(f, PT_REF / f.name)
    log(f"  _paper_tables promoted ({len(staged)} files, release "
        f"{state['new_rel_id']})")
    _remint_paper_tables_manifest(state)
    run_py("papers/scripts/generate_word_sources.py",
           env_extra={"GSK_REL_ID": state["new_rel_id"]})


# --------------------------------------------------------------------------- #
# P8 phase_12 scaffold analysis + exhibits
# --------------------------------------------------------------------------- #
def _regen_descriptive_deltas(fried_p: dict[str, float]) -> None:
    """Reimplementation of the retired phase-12 descriptive_deltas.py, using
    the semantics recorded in ablation_descriptive_deltas_cec2017.json."""
    # Template reads are crash-safe: this function overwrites its own inputs,
    # so a previously interrupted write must fall back to the git blob rather
    # than silently degrade labels or crash unexplained.
    old_csv = ABLRES / "ablation_descriptive_deltas_cec2017.csv"
    rel12 = "papers/build_prompt_phases/phase_12/ablation_results"

    def _labels_from(text: str) -> dict[str, str]:
        out: dict[str, str] = {}
        for r in csv.DictReader(text.splitlines()):
            if r.get("cell") and r.get("component_removed"):
                out.setdefault(r["cell"], r["component_removed"])
        return out

    labels = _labels_from(old_csv.read_text(encoding="utf-8")
                          if old_csv.is_file() else "")
    need = [c for c in SCAFFOLD_CELLS if c != "baseline"]
    if any(c not in labels for c in need):
        blob = git_show_last(f"{rel12}/ablation_descriptive_deltas_cec2017.csv")
        if blob is not None:
            labels.update({k: v for k, v in
                           _labels_from(blob.decode("utf-8")).items()
                           if k not in labels})
    missing = [c for c in need if c not in labels]
    if missing:
        raise RuntimeError("component_removed labels unrecoverable for "
                           f"{missing} (deltas template lost)")

    old_json_path = ABLRES / "ablation_descriptive_deltas_cec2017.json"
    try:
        old_json = json.loads(old_json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        blob = git_show_last(f"{rel12}/ablation_descriptive_deltas_cec2017.json")
        if blob is None:
            raise RuntimeError("deltas JSON template unreadable on disk and "
                               "unrecoverable from git") from None
        old_json = json.loads(blob.decode("utf-8"))

    def _per_run(cell: str) -> dict[int, dict[int, list[float]]]:
        # dim -> func -> per-run error vector (run order as recorded)
        pr = SCAF / cell / "dt-gsk" / "cec2017" / "summary" / "per_run.csv"
        out: dict[int, dict[int, list[float]]] = {}
        with pr.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                d, f = int(r["dimension"]), int(r["function"])
                out.setdefault(d, {}).setdefault(f, []).append(float(r["error"]))
        return out

    base = _per_run("baseline")
    rank_rows: dict[int, dict[str, dict]] = {}
    for d in (10, 30, 50, 100):
        rank_rows[d] = {}
        p = ABLRES / f"ablation_matrix_rank_summary_cec2017_D{d}.csv"
        with p.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                rank_rows[d][r["cell"].strip()] = r

    rows = []
    for d in (10, 30, 50, 100):
        for cell in [c for c in SCAFFOLD_CELLS if c != "baseline"]:
            cellpr = _per_run(cell)
            funcs = sorted(set(base[d]) & set(cellpr[d]))
            b_mean = {f: statistics.fmean(base[d][f]) for f in funcs}
            c_mean = {f: statistics.fmean(cellpr[d][f]) for f in funcs}
            n_active = sum(1 for f in funcs if base[d][f] != cellpr[d][f])
            hurt = sum(1 for f in funcs if c_mean[f] > b_mean[f])
            helped = sum(1 for f in funcs if c_mean[f] < b_mean[f])
            tie = len(funcs) - hurt - helped
            rels = [(c_mean[f] - b_mean[f]) / abs(b_mean[f]) * 100.0
                    for f in funcs if b_mean[f] != 0.0]
            med = round(statistics.median(rels), 4) if rels else 0.0
            pos = [c_mean[f] / b_mean[f] for f in funcs
                   if b_mean[f] > 0.0 and c_mean[f] > 0.0]
            geo = round(math.exp(statistics.fmean(math.log(v) for v in pos)), 5) \
                if pos else float("nan")
            rk = rank_rows[d][cell]
            rows.append({
                "dimension": d, "cell": cell,
                "component_removed": labels[cell],
                "n_funcs": len(funcs), "n_active_funcs": n_active,
                "removal_hurt": hurt, "removal_helped": helped, "tie": tie,
                "median_rel_change_pct": med,
                "geomean_error_ratio_vs_baseline": geo,
                "mean_rank": float(rk["mean_rank"]),
                "delta_rank_vs_full": float(rk["delta_rank_vs_full"]),
                "best_count": int(float(rk["best_count"])),
                "wilcoxon_p": rk["wilcoxon_p"], "holm_p": rk["holm_p"],
                "holm_significant": rk["significant"]})

    hdr = ["dimension", "cell", "component_removed", "n_funcs",
           "n_active_funcs", "removal_hurt", "removal_helped", "tie",
           "median_rel_change_pct", "geomean_error_ratio_vs_baseline",
           "mean_rank", "delta_rank_vs_full", "best_count", "wilcoxon_p",
           "holm_p", "holm_significant"]
    # atomic replace: these files double as this function's own templates,
    # so a torn write must never be observable
    tmp = old_csv.with_suffix(".csv.__new__")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=hdr)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, old_csv)

    new_json = {k: old_json[k] for k in old_json if k != "rows"}
    new_json["release"] = fried_p["__release__"]
    new_json["runs"] = ABL_RUNS
    new_json["analysis_note"] = ("regenerated from the 51-run rerun by "
                                 "papers/scripts/finalize_evidence.py using the "
                                 "semantics block above")
    new_json["rows"] = rows
    tmp = old_json_path.with_suffix(".json.__new__")
    tmp.write_text(json.dumps(new_json, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, old_json_path)


def phase_P8(state: dict, dry: bool) -> None:
    import generate_ablation_matrix as gam  # noqa: PLC0415
    from gsk_family.analysis.statistics import friedman_rank  # noqa: PLC0415

    for d in (10, 30, 50, 100):
        _run_matrix(SCAF, "cec2017", d, "baseline",
                    ABLRES / f"ablation_matrix_rank_summary_cec2017_D{d}.csv",
                    set(SCAFFOLD_CELLS))

    fried_p: dict[str, float] = {"__release__": state["new_abl_id"]}
    for d in (10, 30, 50, 100):
        means = gam._discover_cells(SCAF, "cec2017", d)
        funcs = sorted(set.intersection(*(set(m) for m in means.values())))
        data = {c: [means[c][f] for f in funcs] for c in sorted(means)}
        fried_p[f"D{d}"] = float(f"{friedman_rank(data).p_value:.3g}")

    _regen_descriptive_deltas(fried_p)

    # re-mint ablation_results_manifest.json (fresh SHA-256 of every source)
    sig_rows = []
    per_dim_max: dict[int, tuple[str, float, bool]] = {}
    for d in (10, 30, 50, 100):
        p = ABLRES / f"ablation_matrix_rank_summary_cec2017_D{d}.csv"
        with p.open(encoding="utf-8", newline="") as fh:
            best: tuple[str, float, bool] | None = None
            for r in csv.DictReader(fh):
                cell = r["cell"].strip()
                if cell == "baseline":
                    continue
                delta = float(r["delta_rank_vs_full"])
                sig = r["significant"].strip().lower() == "yes"
                if sig:
                    sig_rows.append({"dimension": d, "cell": cell,
                                     "delta_rank_vs_full": delta,
                                     "holm_p": float(r["holm_p"])})
                if best is None or delta > best[1]:
                    best = (cell, delta, sig)
            per_dim_max[d] = best

    deltas_rows = json.loads(
        (ABLRES / "ablation_descriptive_deltas_cec2017.json")
        .read_text(encoding="utf-8"))["rows"]
    n_active_vals = [r["n_active_funcs"] for r in deltas_rows]
    null_cells = [f"D{r['dimension']}/{r['cell']}" for r in deltas_rows
                  if r["n_active_funcs"] == 0]
    unfavorable = [r for r in sig_rows if r["delta_rank_vs_full"] < 0]

    abl_evi_man = ABL / "manifest.json"
    manifest = {
        "schema": "ablation_results_manifest/v1",
        "study_id": state["new_abl_id"],
        "created_utc": _dt.datetime.now(_dt.timezone.utc)
        .isoformat(timespec="seconds"),
        "git_head": state["anchor"],
        "suite": "cec2017", "dims": [10, 30, 50, 100], "runs": ABL_RUNS,
        "n_funcs": 29,
        "immutable_release": {
            "root": "benchmarks/cec_reference_results/_ablation/scaffold",
            "evidence_manifest":
                "benchmarks/cec_reference_results/_ablation/manifest.json",
            "evidence_manifest_sha256": sha256(abl_evi_man)},
        "analysis_tools": {
            "rank_matrix": ("papers/scripts/generate_ablation_matrix.py "
                            "(Friedman mean-rank + full-vs-cell paired "
                            "Wilcoxon, Holm within dimension)"),
            "descriptive_and_identifiability": (
                "papers/scripts/finalize_evidence.py "
                "(_regen_descriptive_deltas; same semantics as the retired "
                "phase-12 descriptive_deltas.py, recorded in the deltas JSON)")},
        "sgsm_scope": ("interaction_graph_enabled=false in every cell (SGSM "
                       "OFF); conditional remove-one deltas; not independent "
                       "causal effects; no cross-dimension averaging where "
                       "signs differ; Holm correction within dimension."),
        "friedman_p_by_dimension": {k: v for k, v in fried_p.items()
                                    if k != "__release__"},
        "holm_significant_contrasts": sig_rows,
        "headline_largest_conditional_degradation_by_dim": {
            f"D{d}": f"{c} ({dv:+.2f}, "
                     f"{'Holm-significant' if s else 'not significant'})"
            for d, (c, dv, s) in per_dim_max.items()},
        "identifiability": (
            f"all disabled cells engaged >=1 function per dimension "
            f"(n_active {min(n_active_vals)}-{max(n_active_vals)} of 29); "
            "no null-contrast cells." if not null_cells else
            f"NULL-CONTRAST CELLS PRESENT: {null_cells} - review required"),
        "correction_exception_G0": (
            "NOT TRIGGERED - all Holm-significant deltas favorable (removal "
            "degrades); manuscript run-count/values update is part of this "
            "51-run finalization campaign (see finalize_report.md)."
            if not unfavorable else
            "TRIGGER REVIEW - unfavorable Holm-significant contrast(s) "
            f"(removal improves): {unfavorable}; human governance review "
            "required before any claim is retained"),
    }
    tracked = [f"ablation_results/ablation_matrix_rank_summary_cec2017_D{d}.csv"
               for d in (10, 30, 50, 100)]
    tracked += ["ablation_results/ablation_descriptive_deltas_cec2017.csv",
                "ablation_results/ablation_descriptive_deltas_cec2017.json",
                "ablation_findings.md", "ablation_execution_manifest.json"]
    manifest["files"] = [
        {"path": t, "sha256": sha256(PHASE12 / t),
         "size_bytes": (PHASE12 / t).stat().st_size} for t in tracked]
    (ABLRES / "ablation_results_manifest.json").write_text(
        json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    log(f"  phase_12 manifest re-minted (study {state['new_abl_id']}, "
        f"{len(sig_rows)} Holm-significant contrasts)")
    if unfavorable:
        log("  WARNING: G0 correction exception TRIGGERED - see manifest")

    run_py("papers/scripts/generate_ablation_exhibits.py",
           env_extra={"GSK_ABL_RUNS": str(ABL_RUNS),
                      "GSK_ABL_RELID": state["new_abl_id"]})


# --------------------------------------------------------------------------- #
# P9 downstream table/figure generators
# --------------------------------------------------------------------------- #
def phase_P9(state: dict, dry: bool) -> None:
    rel_env = {"GSK_REL_ID": state["new_rel_id"],
               "GSK_ANCHOR": state["anchor"]}
    jobs: list[tuple[str, list[str], dict]] = [
        ("papers/scripts/generate_latex_tables.py", [], rel_env),
        # SA04 function inventory: derived from the benchmark suite definition
        # (not from the release), so it carries no rel_env -- but it is
        # regenerated here so the table can never drift from the suite.
        ("papers/scripts/generate_function_inventory.py", [], {}),
        # Comparator parameter table (papers/generated/comparator_params.tex):
        # read from the shipped optimizer modules, likewise release-independent,
        # regenerated here so it cannot drift from the code it documents.
        ("papers/scripts/generate_comparator_params.py", [], {}),
        ("papers/scripts/generate_t16_bca.py", [], rel_env),
        ("papers/scripts/posthoc_robustness_cec2017.py", [], rel_env),
        ("papers/scripts/generate_full_convergence.py", [], rel_env),
        ("papers/scripts/generate_cec2011_convergence.py", [], rel_env),
        ("papers/scripts/generate_cec2013_convergence.py", [], rel_env),
        ("papers/scripts/generate_nemenyi_cd.py", [], rel_env),
        ("papers/scripts/generate_rank_charts.py", [], rel_env),
        # generate_trace_figures.py and generate_adaptive_params_panel.py are
        # NOT run: they are diagnostic-only tools whose inputs are quarantined
        # per-generation gen-log runs (EG-005) that this campaign does not
        # produce, and whose outputs the manuscript never consumes (no .tex
        # reference; papers/figures/traces/ holds only .gitkeep).
        ("papers/scripts/generate_nlpsr_trajectory.py", [], rel_env),
        ("papers/scripts/ablation_overlay_effects.py", [],
         {"GSK_OVL_SUITE": "cec2017", "GSK_OVL_DIMS": "50,100"}),
        ("papers/scripts/ablation_overlay_effects.py", [],
         {"GSK_OVL_SUITE": "cec2013", "GSK_OVL_DIMS": "50"}),
        ("papers/scripts/generate_artifact_binding.py", [], rel_env),
    ]
    failures = []
    for script, args, env_extra in jobs:
        try:
            run_py(script, *args, env_extra=env_extra)
        except RuntimeError as e:
            failures.append(f"{script} ({env_extra.get('GSK_OVL_SUITE', '')}): {e}")
            log(f"  FAILED: {script}")
    if failures:
        raise RuntimeError("P9 generator failures:\n" + "\n\n".join(failures))


# --------------------------------------------------------------------------- #
# P10 deterministic builds
# --------------------------------------------------------------------------- #
def phase_P10(state: dict, dry: bool) -> None:
    pdf_env = {"SOURCE_DATE_EPOCH": PDF_EPOCH, "FORCE_SOURCE_DATE": "1"}
    main_pdf = ROOT / "papers" / "DT-GSK.pdf"
    stray = ROOT / "papers" / "DT-GSK.new.pdf"

    # clear a leftover from a previous locked-viewer attempt, or the check
    # below re-fires forever even after the viewer is closed
    stray.unlink(missing_ok=True)
    run_py("papers/scripts/build_pdf.py", env_extra=pdf_env)
    if stray.exists():
        raise RuntimeError("papers/DT-GSK.new.pdf produced - the PDF is open "
                           "in a viewer; close it and resume with "
                           "--from-phase P10")
    h1 = sha256(main_pdf)
    run_py("papers/scripts/build_pdf.py", env_extra=pdf_env)
    if stray.exists():
        raise RuntimeError("papers/DT-GSK.new.pdf produced on the second "
                           "build - close the PDF viewer and resume with "
                           "--from-phase P10")
    h2 = sha256(main_pdf)
    if h1 != h2:
        raise RuntimeError(f"main PDF not deterministic: {h1[:12]} vs {h2[:12]}")
    log(f"  DT-GSK.pdf deterministic (sha256 {h1[:16]}...)")

    supp_pdf = ROOT / "papers" / "supplementary.pdf"
    run_py("papers/scripts/build_supplementary.py", "--rebuild-bib",
           env_extra=pdf_env)
    s1 = sha256(supp_pdf)
    run_py("papers/scripts/build_supplementary.py", env_extra=pdf_env)
    s2 = sha256(supp_pdf)
    if s1 != s2:
        log(f"  WARNING: supplementary PDF hash changed across rebuilds "
            f"({s1[:12]} vs {s2[:12]}) - inspect before release")
    else:
        log(f"  supplementary.pdf deterministic (sha256 {s2[:16]}...)")

    # DOCX uses the builder's own default epoch - do not leak the PDF epoch
    run_py("papers/scripts/build_docx.py")
    run_py("papers/scripts/build_docx.py", "--supplementary")
    run_py("papers/scripts/validate_docx.py", str(ROOT / "papers" / "DT-GSK.docx"))
    run_py("papers/scripts/validate_docx.py",
           str(ROOT / "papers" / "supplementary.docx"))


# --------------------------------------------------------------------------- #
# P11 gates + freeze-manifest disposition
# --------------------------------------------------------------------------- #
def phase_P11(state: dict, dry: bool) -> None:
    rc, _ = run_py("pytest", "-q", module=True)
    log("  pytest: green")
    run_py("ruff", "check", "src", "tests", "scripts", module=True)
    log("  ruff: clean")
    run_py("scripts/validate_profile_lock.py", "--root", ".")
    run_py("scripts/build_docs_html.py")

    rc, out = run_py("papers/scripts/check_manifest.py", allow_fail=True)
    if rc == 0:
        log("  check_manifest: PASS (unexpected after an evidence rerun - "
            "verify the freeze manifest actually tracks the changed files)")
    else:
        # check_manifest prints "N/M match [...]" plus "missing : [...]" /
        # "changed : [...]" lines - capture those, they ARE the refreeze list
        mismatched = [ln.strip() for ln in out.splitlines()
                      if ln.strip().startswith(("missing :", "changed :"))
                      or " match " in ln]
        pend = {
            "generated_utc": _dt.datetime.now(_dt.timezone.utc)
            .isoformat(timespec="seconds"),
            "release_id": state["new_rel_id"],
            "reason": ("EXPECTED failure: the hand-minted "
                       "main_manuscript_freeze_manifest.json still binds the "
                       "pre-rerun bytes. Refreeze is a HUMAN byte-surgical "
                       "step (CRLF + 2-space indent; edit hashes in place, "
                       "never rewrite the file)."),
            "checker_exit": rc,
            "checker_findings": mismatched[:50],
        }
        (GOV / "_pending_refreeze.json").write_text(
            json.dumps(pend, indent=1) + "\n", encoding="utf-8")
        log(f"  check_manifest: expected FAIL (exit {rc}) - wrote "
            "papers/governance/_pending_refreeze.json for the manual refreeze")

    rc, out = run_py("papers/scripts/validate_evidence_bindings.py",
                     allow_fail=True)
    state["bindings_exit"] = rc
    verdict = ("clean" if rc == 0 else
               "failures EXPECTED until the manuscript prose is updated to "
               "the new numbers (runbook Sec. 6)")
    log(f"  validate_evidence_bindings: exit {rc} ({verdict})")


# --------------------------------------------------------------------------- #
# P12 headline diff report
# --------------------------------------------------------------------------- #
def _read_ranks(bundle: Path, name: str) -> dict[str, str]:
    p = bundle / name
    out: dict[str, str] = {}
    if not p.is_file():
        return out
    with p.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return out
    alg_col = next((c for c in rows[0] if "alg" in c.lower()), None)
    rank_col = next((c for c in rows[0] if "mean_rank" in c.lower()), None)
    if not alg_col or not rank_col:
        return out
    for r in rows:
        out[r[alg_col].strip()] = r[rank_col].strip()
    return out


def phase_P12(state: dict, dry: bool) -> None:
    new_rel = state["new_rel_id"]
    old_b = ROOT / "papers" / "analysis" / OLD_REL_ID
    new_b = ROOT / "papers" / "analysis" / new_rel

    lines = [
        "# Evidence finalization report",
        "",
        f"- generated: {_dt.datetime.now(_dt.timezone.utc).isoformat(timespec='seconds')}",
        f"- primary release: {OLD_REL_ID}  ->  **{new_rel}** "
        f"(anchor {state['anchor'][:9]})",
        f"- ablation release: -> **{state['new_abl_id']}** (51 runs)",
        f"- oracle release: {state.get('oracle_disposition', 'present')} "
        "(pre-fix exploratory, disclosed; no rerun apparatus exists)",
        "",
        "## Headline mean ranks (dt-gsk / egsk), old -> new",
        "",
        "| exhibit | old dt-gsk | new dt-gsk | old egsk | new egsk |",
        "|---|---|---|---|---|",
    ]
    exhibits = (
        [("cec2017 overall", "cec2017/friedman_ranks_cec2017_overall.csv")]
        + [(f"cec2017 D{d}", f"cec2017/friedman_ranks_cec2017_D{d}.csv")
           for d in (10, 30, 50, 100)]
        + [(f"cec2013 D{d}", f"cec2013/friedman_ranks_cec2013_D{d}.csv")
           for d in (10, 30, 50)]
    )
    # cec2011 rank file name can vary; glob it
    for b, tag in ((old_b, "old"), (new_b, "new")):
        for p in sorted((b / "cec2011").glob("friedman_ranks*.csv")) \
                if (b / "cec2011").is_dir() else []:
            rel = f"cec2011/{p.name}"
            if ("cec2011 " + p.name, rel) not in exhibits:
                exhibits.append((f"cec2011 {p.name}", rel))
        break
    for label, rel in exhibits:
        o = _read_ranks(old_b, rel)
        n = _read_ranks(new_b, rel)
        lines.append(f"| {label} | {o.get('dt-gsk', '?')} | "
                     f"{n.get('dt-gsk', '?')} | {o.get('egsk', '?')} | "
                     f"{n.get('egsk', '?')} |")

    lines += ["", "## Overlay isolation (51 runs)", ""]
    for suite, dims in (("cec2017", [50, 100]), ("cec2013", [50])):
        for dim in dims:
            p = ANA / f"overlay_contrasts_{suite}_D{dim}.json"
            try:
                j = json.loads(p.read_text(encoding="utf-8"))
                ns = j["contrasts"]["no_sgsm"]["holm"]
                fp = j["contrasts"]["no_finalpolish"]["holm"]
                lines.append(
                    f"- {suite} D{dim}: no_sgsm Holm p = {ns['p_holm']:.4g} "
                    f"({'SIGNIFICANT' if ns['significant_at_0.05'] else 'null'}); "
                    f"no_finalpolish Holm p = {fp['p_holm']:.4g} "
                    f"({'significant' if fp['significant_at_0.05'] else 'null'})")
            except (OSError, KeyError, json.JSONDecodeError):
                lines.append(f"- {suite} D{dim}: contrasts JSON unreadable")
    eff = ROOT / "papers/analysis/ablation_overlay/ism_isolation_effects_cec2017.csv"
    if eff.is_file():
        with eff.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                if r["cell"] == "no_sgsm" and r["ism_runtime_overhead_pct"]:
                    lines.append(f"- ISM runtime overhead cec2017 "
                                 f"D{r['dimension']}: "
                                 f"{r['ism_runtime_overhead_pct']}%")

    lines += ["", "## Scaffold ablation (51 runs)", ""]
    try:
        m = json.loads((ABLRES / "ablation_results_manifest.json")
                       .read_text(encoding="utf-8"))
        lines.append(f"- Friedman p by dimension: "
                     f"{json.dumps(m['friedman_p_by_dimension'])}")
        for c in m["holm_significant_contrasts"]:
            lines.append(f"- Holm-significant: D{c['dimension']} {c['cell']} "
                         f"(delta {c['delta_rank_vs_full']:+.2f}, "
                         f"Holm p {c['holm_p']:.3g})")
        lines.append(f"- G0: {m['correction_exception_G0'].split(' - ')[0]}")
    except (OSError, KeyError, json.JSONDecodeError):
        lines.append("- phase_12 manifest unreadable")

    lines += [
        "",
        "## Remaining HUMAN steps (cannot be automated)",
        "",
        "1. Manuscript prose: re-verify/update every hand-written headline "
        "number against the new bundle (runbook "
        "docs/development/evidence_rerun_runbook.md Sec. 6): overall 2.48/7, "
        "per-dim ranks, 17-7-0 pairwise tally, CEC2011 3.36 vs 2.52 "
        "(Holm p = 0.042), CEC2013 2.80, head-to-head W-T-L records, "
        "Nemenyi CD statements, runtime/limitations wording.",
        "2. Run-count prose: S6.5/S6.6 and any main-text mention of '25 runs' "
        "for ablation/overlay must become 51 runs (tables/captions already "
        "regenerate via GSK_ABL_RUNS).",
        "3. Retire the 'evidence-pending' caveats added on 2026-07-14 once "
        "the numbers are re-verified.",
        "4. Narrative docs bound by hash only - update their 25-run numbers "
        "to the 51-run results manually: "
        "papers/build_prompt_phases/phase_12/ablation_findings.md and "
        "benchmarks/cec_reference_results/_ablation/overlay/analysis/"
        "overlay_findings.md + overlay_validation.md.",
        "4b. _ablation/manifest.json: the X-ABL-02 'honesty' statement was "
        "marked '[25-run-era statement; re-evaluate...]' and the "
        "pre-registered correction_trigger_mapping was kept verbatim - "
        "re-evaluate both against the 51-run contrasts and rewrite the "
        "honesty text by hand.",
        "5. Freeze manifest: byte-surgical refreeze of "
        "main_manuscript_freeze_manifest.json (CRLF + 2-space; see "
        "papers/governance/_pending_refreeze.json).",
        "6. Commit everything; note that anchor_commit "
        f"({state['anchor'][:9]}) was HEAD at finalization time - record the "
        "promotion commit in the release notes (phase6's environment_record "
        "stores git_head_at_run separately).",
        "7. Update _index/BENCHMARK_EVIDENCE_INDEX.md for the new release ids.",
    ]
    report = FIN / "finalize_report.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"  report written: {report.relative_to(ROOT)}")
    log("")
    for ln in lines:
        log(ln)


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #
PHASES = [
    ("P0", "preflight (staging + tool-patch checks)", phase_P0),
    ("P1", "audit-promotion RETIRED (git history is the audit record)", phase_P1),
    ("P2", "flat-layout dt-gsk refresh (3 suites)", phase_P2),
    ("P3", "_ablation refresh + manifest re-mint (51 runs)", phase_P3),
    ("P4", "_oracle integrity check (no-op; oracle study retired)", phase_P4),
    ("P5", "gsk-stats x3 --strict-source", phase_P5),
    ("P6", "evidence_release_manifest + phase6 bundle", phase_P6),
    ("P7", "_paper_tables promotion + word sources", phase_P7),
    ("P8", "phase_12 scaffold analysis + exhibits", phase_P8),
    ("P9", "downstream table/figure generators", phase_P9),
    ("P10", "deterministic PDF/DOCX builds + validators", phase_P10),
    ("P11", "green gates + freeze-manifest disposition", phase_P11),
    ("P12", "headline diff report", phase_P12),
]


def main() -> int:
    global _LOG_FH
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="run the P0 preflight checks only; change nothing")
    ap.add_argument("--from-phase", metavar="P#",
                    help="re-run from this phase (clears its checkpoint and "
                         "all later ones)")
    ap.add_argument("--skip-oracle", action="store_true",
                    help="if _oracle was deleted, leave it deleted instead of "
                         "restoring it from git history (S6.7 then cites "
                         "evidence absent from the repo)")
    ap.add_argument("--list", action="store_true", help="list phases and exit")
    args = ap.parse_args()

    if args.list:
        for pid, desc, _ in PHASES:
            print(f"  {pid:4s} {desc}")
        return 0

    FIN.mkdir(parents=True, exist_ok=True)
    _LOG_FH = LOG_PATH.open("a", encoding="utf-8")
    _LOG_FH.write(f"\n===== finalize_evidence {_dt.datetime.now().isoformat()} "
                  f"argv={sys.argv[1:]} =====\n")

    state = load_state()
    state["skip_oracle"] = bool(args.skip_oracle)   # re-set on every run
    completed = set(state.get("completed", []))
    ids = [pid for pid, _, _ in PHASES]
    if args.from_phase and args.from_phase not in ids:
        print(f"unknown phase {args.from_phase}; use --list")
        return 2

    if args.dry_run:
        # dry-run must be side-effect free: preview the --from-phase clearing
        # in memory only, never persist state
        log("DRY RUN - preflight only")
        phase_P0(state, dry=True)
        preview = set(state.get("completed", []))
        if args.from_phase:
            preview -= set(ids[ids.index(args.from_phase):])
        log("dry run complete; no changes made. Phase plan:")
        for pid, desc, _ in PHASES:
            mark = "done" if pid in preview else "    "
            log(f"  [{mark}] {pid:4s} {desc}")
        return 0

    if args.from_phase:
        cut = ids.index(args.from_phase)
        completed -= set(ids[cut:])
        state["completed"] = sorted(completed)
        save_state(state)

    for pid, desc, fn in PHASES:
        if pid != "P0" and pid in completed:
            log(f"[{pid}] {desc} - already completed, skipping")
            continue
        log(f"[{pid}] {desc}")
        fn(state, dry=False)
        if pid == "P0":
            # P0's self-heal may have cleared checkpoints - resync
            completed = set(state.get("completed", []))
        else:
            completed.add(pid)
        state["completed"] = sorted(completed)
        save_state(state)
    log("")
    log("FINALIZATION COMPLETE - review results/_finalize/finalize_report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
