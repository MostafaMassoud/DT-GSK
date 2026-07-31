#!/usr/bin/env python3
"""Phase 6b deterministic analysis driver -- CEC2020 and CEC2013LSGO.

A PHYSICALLY SEPARATE sibling of ``papers/scripts/phase6_run_analysis.py``
(ruling R3, docs/development/FINAL_PUBLICATION_PLAN.md). It executes the
pre-registered addendum families for the two NEW suites and nothing else.

    papers/build_prompt_phases/phase_05/
        statistical_analysis_plan_addendum_cec2020_lsgo.md            (binding)
        statistical_analysis_plan_addendum_cec2020_lsgo_amendment_01.md

Why a separate file (R3, verbatim): ``phase6_run_analysis.py:74`` defaults
``GSK_REL_ID`` to the stale ``rel-2026-07-16-78f075cb0`` and its lines 84-95
hardcode the three frozen suites, so a bare invocation is a live footgun. That
file is NEVER edited and is never imported here. The shared statistical
primitives are imported from ``src/gsk_family/analysis/statistics.py``
(``friedman_rank`` M-026, ``holm_correction``, ``wilcoxon_paired``,
``bootstrap_bca_ci``) WITHOUT modification.

Structural guarantees (all enforced at runtime, not by convention):
  * Output guard -- every write resolves through :func:`assert_writable`, which
    refuses any path carrying a ``rel-*`` component. The frozen primary bundle
    ``papers/analysis/rel-2026-07-20-67d9345f9/`` (and its two predecessors)
    is therefore unreachable BY CONSTRUCTION, whatever ``--out-root`` says.
    The release ids this driver accepts must match ``(lsgo|cec2020)-rel-...``,
    which cannot collide with the frozen ``rel-*`` family.
  * Strict-source -- ``GSK_STRICT_SOURCE=1`` plus ``set_strict_source(True)``
    plus three negative probes; every empirical byte comes from
    ``benchmarks/cec_reference_results/<suite>/``.
  * F2-exclusion hazard (Amendment 1 Section A1.1, LATENT HAZARD, binding) --
    the papers-side helper ``statistical_tests.friedman_rank_test`` defaults
    ``excluded=(2,)``, a CEC2017-era convention that silently drops F2. Every
    function list in this driver is built by :func:`suite_funcs`, whose
    ``excluded`` argument is keyword-ONLY and has NO default, from the explicit
    per-suite ``excluded_functions`` entry (empty for both new suites). A
    startup guard asserts the hazard still exists upstream and that this driver
    never inherits it.
  * CEC2020 readiness -- CEC2020 mode refuses to run until all seven banks are
    complete (7 x 1,140 rows = 38 protocol cells x 30 runs), per addendum
    Section 11.
  * LSGO self-check -- the LSGO layers must REPRODUCE the values recorded in
    Amendment 1 Section A1.3 to the digit. They are hardcoded in
    :data:`PINNED_LSGO`; any difference raises :class:`DriverDefect`. A
    digit-level difference is a DEFECT IN THIS DRIVER, never a new result.

Determinism contract (mirrors phase6 Sec. 5 and tightens it): C locale,
``%.6e`` floats, literal ``n/a`` for disclosed-unavailable cells, fixed sort
orders (suite, dimension asc, function asc, P1 algorithm order), NO timestamps
anywhere in the bundle (phase6 keeps them in ``source_use_log.json``; dropping
them makes this bundle byte-reproducible), BCa B=10,000 with
``default_rng(SeedSequence([20240620, suite_ordinal, dim, func, cmp_P1_idx]))``,
omnibus permutation B=100,000 drawn in fixed 5,000-sample chunks from
``default_rng(SeedSequence([20240620, 2020, dim, 0, 99]))``.

Usage:
    python papers/scripts/phase6b_run_analysis_newsuites.py --suite cec2013lsgo
    python papers/scripts/phase6b_run_analysis_newsuites.py --suite cec2020
    python papers/scripts/phase6b_run_analysis_newsuites.py --suite both
    # dry proof run into a scratch tree (guard still active):
    python papers/scripts/phase6b_run_analysis_newsuites.py \
        --suite cec2013lsgo --out-root /tmp/scratch/lsgo_bundle
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import locale
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import scipy.stats as sps

SCRIPT_DIR = Path(__file__).resolve().parent
PAPER_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = PAPER_DIR.parent
_SRC = PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Deterministic locale before any formatting.
os.environ["LC_ALL"] = "C"
os.environ["LANG"] = "C"
# Strict-source activation #1 (env var); #2 (set_strict_source) applied in main().
os.environ["GSK_STRICT_SOURCE"] = "1"

from gsk_family.analysis import result_loader as rl  # noqa: E402
from gsk_family.analysis.statistics import (  # noqa: E402  (imported, never edited)
    bootstrap_bca_ci,
    friedman_rank,
    holm_correction,
    wilcoxon_paired,
)

# ---------------------------------------------------------------------------
# Frozen constants
# ---------------------------------------------------------------------------
SCRIPT_REL = "papers/scripts/phase6b_run_analysis_newsuites.py"
COMMAND_BASE = "python papers/scripts/phase6b_run_analysis_newsuites.py"

REF_ROOT = PROJECT_ROOT / "benchmarks" / "cec_reference_results"
ANALYSIS_ROOT = PAPER_DIR / "analysis"
GOV_DIR = PAPER_DIR / "governance"
PHASE05 = PAPER_DIR / "build_prompt_phases" / "phase_05"
RESULTS_ROOT = PROJECT_ROOT / "results"

# P1 order -- identical to phase6_run_analysis.py:84-86 (do not reorder).
PANEL = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk", "dt-gsk"]
COMPARATORS = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk"]
PROPOSED = "dt-gsk"
K_PANEL = len(PANEL)

#: The frozen primary bundle this driver must never be able to touch.
FROZEN_PRIMARY_RELEASE = "rel-2026-07-20-67d9345f9"
#: Release ids of the two new evidence bodies must match this; the frozen
#: family (``rel-*``) cannot match it, which is what makes the guard structural.
NEW_RELEASE_RE = re.compile(r"^(lsgo|cec2020)-rel-\d{4}-\d{2}-\d{2}-[0-9a-f]{9}$")

ALPHA = 0.05
TIE_TOL = 1e-8            # addendum Section 5 (absolute, everywhere)
B_BOOT = 10000            # AN-EFF-*
B_PERM = 100000           # AN-OMNI-2020-* permutation companion
PERM_CHUNK = 5000         # part of the determinism contract (fixed draw size)
BASE_SEED = 20240620
FLOOR_SENSITIVITY = (1e-6, 1e-8)   # AN-ROB-2020 variant 3
NA = "n/a"

#: Demsar (2006) Table 5(a) two-tailed Nemenyi q_{0.05}, PARAMETERIZED BY k.
#: phase6 hardcodes the k=7 value; here k is looked up and asserted, so a panel
#: size change can never silently produce a wrong-direction critical distance.
NEMENYI_Q_005: dict[int, float] = {
    2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850,
    7: 2.949, 8: 3.031, 9: 3.102, 10: 3.164,
}

#: Verbatim string required by addendum Section 4 (AN-PW) when n_eff < 6.
NOT_DECIDABLE = ("not decidable at alpha=0.05 "
                 "(exact two-sided floor 2/2^5 = 0.0625)")

#: Verbatim caption disclosure required by addendum Section 4
#: (AN-RANKAGG-2020-OVERALL). Carried as a CSV column so it cannot be dropped
#: silently between the pipeline and the exhibit.
RANKAGG_CAPTION = (
    "DESCRIPTIVE ONLY; no test is attached. The four per-dimension rank vectors "
    "are NOT on a common protocol: D5 uses a REDUCED TASK SET of 8 of the 10 "
    "functions (F6 and F7 are undefined at D=5, addendum Section 2), and MaxFES "
    "CHANGES BY DIMENSION (50,000 / 1,000,000 / 3,000,000 / 10,000,000 at "
    "D=5/10/15/20), so the aggregate mixes budget regimes."
)

LSGO_ACKLEY_DISCLOSURE = (
    "F3/F6/F10 evaluate the TRANSFORMED Ackley variant; results on those "
    "functions are NOT comparable to published raw-Ackley values and no such "
    "comparison is drawn (addendum Section 2)"
)
LSGO_TIER_DISCLOSURE = (
    "DESCRIPTIVE-AFTER-INSPECTION (addendum Section 6): the mean ranks, the "
    "omnibus and the W/T/L descriptives were inspected informally before the "
    "addendum was signed; they carry no confirmatory weight and never enter a "
    "headline"
)

# ---------------------------------------------------------------------------
# Per-suite configuration
# ---------------------------------------------------------------------------
# ``excluded_functions`` is EXPLICIT for every suite (Amendment 1 A1.1 hazard):
# neither new suite excludes anything. It is never defaulted, never inherited.
CEC2020_FUNCS_ALL = list(range(1, 11))
CEC2020_D5_FUNCS = [1, 2, 3, 4, 5, 8, 9, 10]      # F6/F7 undefined at D=5
CEC2020_COMMON8 = list(CEC2020_D5_FUNCS)          # AN-ROB-2020 variant 2
LSGO_FUNCS = list(range(1, 16))
LSGO_NATIVE_DIM = {f: (905 if f in (13, 14) else 1000) for f in LSGO_FUNCS}

SUITE_CFG: dict[str, dict] = {
    "cec2013lsgo": {
        "ordinal": 2113,                # "cec2013lsgo, distinct from 2013"
        "tag": "LSGO",
        "runs": 25,
        "expected_rows": 375,           # 15 cells x 25 runs
        "expected_cells": 15,
        "endpoint_column": "best_fitness",
        "basis": "raw_objective",
        "dim_keys": ["native"],
        "summary_dims": [1000, 905],
        "native_dim": LSGO_NATIVE_DIM,
        "funcs": {"native": LSGO_FUNCS},
        "excluded_functions": (),       # EXPLICIT -- see A1.1 hazard
        "fset": {"native": "F1-F15"},
        "permutation_omnibus": False,   # not registered for LSGO
        "manifest": "evidence_release_manifest_cec2013lsgo.json",
        "rel_env": "GSK_LSGO_REL_ID",
        "budget": {"native": 3_000_000},
    },
    "cec2020": {
        "ordinal": 2020,
        "tag": "2020",
        "runs": 30,
        "expected_rows": 1140,          # 38 protocol cells x 30 runs
        "expected_cells": 38,
        "endpoint_column": "error",
        "basis": "error",
        "dim_keys": [5, 10, 15, 20],
        "summary_dims": [5, 10, 15, 20],
        "native_dim": None,
        "funcs": {5: CEC2020_D5_FUNCS, 10: CEC2020_FUNCS_ALL,
                  15: CEC2020_FUNCS_ALL, 20: CEC2020_FUNCS_ALL},
        "excluded_functions": (),       # EXPLICIT -- see A1.1 hazard
        "fset": {5: "F1-F5,F8-F10", 10: "F1-F10", 15: "F1-F10", 20: "F1-F10"},
        "permutation_omnibus": True,
        "manifest": "evidence_release_manifest_cec2020.json",
        "rel_env": "GSK_CEC2020_REL_ID",
        "budget": {5: 50_000, 10: 1_000_000, 15: 3_000_000, 20: 10_000_000},
    },
}

# ---------------------------------------------------------------------------
# LSGO reproduction pins (Amendment 1 Section A1.3, dated 2026-07-28)
# ---------------------------------------------------------------------------
# These are NOT results. They are the already-computed, independently
# re-verified values that this driver must reproduce from the promoted release.
# Any difference is a DEFECT IN THIS DRIVER.
PINNED_LSGO = {
    # Section 6 / A1.1: family-only tie-corrected Friedman on per-function means
    "mean_ranks": {"gsk": 3.867, "agsk": 3.133, "apgsk": 4.933, "fdb-agsk": 3.933,
                   "atmals-gsk": 3.533, "egsk": 5.467, "dt-gsk": 3.133},
    "chi2": 15.3143, "p_chi2": 0.01795, "f_id": 2.8707, "p_id": 0.01358,
    # Layer 1 -- AN-PW-LSGO-NATIVE, exact 2^15 sign-flip enumeration
    "layer1_p_exact": {"gsk": 0.761536, "agsk": 0.846924, "apgsk": 0.055359,
                       "fdb-agsk": 0.083252, "atmals-gsk": 0.168823,
                       "egsk": 0.047913},
    "layer1_p_normal": {"gsk": 0.7548, "agsk": 0.8424, "apgsk": 0.0571,
                        "fdb-agsk": 0.0832, "atmals-gsk": 0.1641, "egsk": 0.0501},
    "layer1_p_holm": {"gsk": 1.0000, "agsk": 1.0000, "apgsk": 0.2875,
                      "fdb-agsk": 0.3330, "atmals-gsk": 0.5065, "egsk": 0.2875},
    "layer1_holm_significant": 0,   # Holm m=6 leaves nothing significant
    # Layer 2 -- AN-PWRUN-LSGO-NATIVE, Holm m=15 per comparator
    "layer2_wins_losses": {"gsk": (8, 6), "agsk": (9, 6), "apgsk": (11, 3),
                           "fdb-agsk": (11, 4), "atmals-gsk": (7, 6),
                           "egsk": (11, 4)},
    "layer2_win_functions": {
        "gsk": [2, 3, 4, 6, 8, 10, 12, 14],
        "agsk": [2, 3, 4, 5, 6, 8, 9, 10, 12],
        "apgsk": [1, 2, 3, 4, 5, 6, 8, 9, 11, 12, 14],
        "fdb-agsk": [1, 3, 4, 5, 6, 8, 9, 10, 11, 12, 14],
        "atmals-gsk": [4, 5, 8, 9, 10, 11, 14],
        "egsk": [1, 2, 3, 4, 6, 8, 10, 11, 12, 13, 14],
    },
    "layer2_loss_functions": {
        "gsk": [1, 5, 7, 9, 13, 15],
        "agsk": [1, 7, 11, 13, 14, 15],
        "apgsk": [7, 13, 15],
        "fdb-agsk": [2, 7, 13, 15],
        "atmals-gsk": [1, 2, 3, 7, 12, 15],
        "egsk": [5, 7, 9, 15],
    },
    # Cross-comparator regularities (descriptive)
    "win_all_functions": [4, 8],
    "lose_all_functions": [7, 15],
}

# Nemenyi power disclosure as written in addendum Section 7 -- recomputed and
# compared, never trusted. The critical difference is fully determined by k and
# N, so a mismatch is either a driver defect (large) or a last-digit rounding
# slip in the pre-registration TEXT (small). The two are separated by
# CD_TEXT_BAND and reported differently: a text slip is DISCLOSED, never
# silently absorbed, and never patched here.
ADDENDUM_NEMENYI_CD = {8: 3.185, 10: 2.849, 15: 2.327}
CD_EXACT_TOL = 5e-4       # reproduces the disclosed value
CD_TEXT_BAND = 2e-3       # last-digit text discrepancy; disclosed, not a defect

STAT_COLUMNS = [
    "analysis_id", "rq_id", "suite", "dimension", "function_set", "algorithms",
    "metric", "unit_of_analysis", "n_observations", "pairing_key", "test",
    "test_statistic", "p_raw", "p_adjusted", "correction", "effect_size",
    "effect_direction", "ci_low", "ci_high", "ci_level", "resampling_unit",
    "n_resamples", "seed", "source_paths", "source_checksums",
    "evidence_release_id", "script", "command", "commit_sha", "interpretation",
    "status",
]

# ---------------------------------------------------------------------------
# Mutable run state
# ---------------------------------------------------------------------------
STAT_ROWS: list[dict] = []
MANIFEST_ENTRIES: list[dict] = []
NOTES: list[str] = []
SELFCHECK: dict = {}
GIT_HEAD = "unknown"
REL_ID = "unset"
ANCHOR = "unset"
OUT_ROOT: Path = Path()
COMMAND = COMMAND_BASE

_SHA_CACHE: dict[str, str] = {}
_ENDPOINT_CACHE: dict = {}
_STATS_CACHE: dict = {}


class DriverDefect(RuntimeError):
    """Raised when a pinned, already-computed value fails to reproduce."""


class OutputGuardViolation(RuntimeError):
    """Raised when a write would land on a forbidden path."""


# ===========================================================================
# Guards
# ===========================================================================
def assert_release_id(rel_id: str) -> None:
    """The release id must belong to the two NEW evidence bodies."""
    if rel_id == FROZEN_PRIMARY_RELEASE or rel_id.startswith("rel-"):
        raise OutputGuardViolation(
            f"refusing release id '{rel_id}': this driver may never address the "
            f"frozen 'rel-*' analysis family (primary: {FROZEN_PRIMARY_RELEASE})")
    if not NEW_RELEASE_RE.match(rel_id):
        raise OutputGuardViolation(
            f"release id '{rel_id}' does not match "
            f"'(lsgo|cec2020)-rel-YYYY-MM-DD-<anchor9>'")


def assert_writable(path: Path) -> Path:
    """Every output path passes through here. No exceptions, no overrides.

    Refuses (a) any path with a ``rel-*`` component -- which is exactly the
    frozen bundle family ``papers/analysis/rel-2026-07-10|16|20-*`` -- (b)
    anything inside the immutable evidence tree, and (c) anything inside
    ``results/``. The proposed path must also stay inside the resolved
    ``OUT_ROOT`` of this run.
    """
    p = Path(path).resolve()
    for part in p.parts:
        if part.startswith("rel-"):
            raise OutputGuardViolation(
                f"refusing to write '{p}': component '{part}' belongs to the frozen "
                f"'rel-*' analysis family (primary {FROZEN_PRIMARY_RELEASE}); this "
                f"driver is structurally incapable of writing there")
    if p.is_relative_to(REF_ROOT.resolve()):
        raise OutputGuardViolation(f"refusing to write inside the evidence release: {p}")
    if RESULTS_ROOT.exists() and p.is_relative_to(RESULTS_ROOT.resolve()):
        raise OutputGuardViolation(f"refusing to write inside results/ staging: {p}")
    if OUT_ROOT != Path() and not p.is_relative_to(OUT_ROOT.resolve()):
        raise OutputGuardViolation(f"refusing to write outside the run's out-root: {p}")
    return p


def assert_exclusion_hazard_defused() -> dict:
    """Amendment 1 A1.1 LATENT HAZARD guard (binding on Phase 3).

    ``statistical_tests.friedman_rank_test`` defaults ``excluded=(2,)`` -- a
    CEC2017-era convention that silently drops F2 and, on the LSGO means, yields
    p = 0.0370 with the wrong ranks. This driver never calls that helper, and
    every function list it builds comes from an EXPLICIT per-suite exclusion
    list. Both halves are asserted here so the hazard cannot be re-introduced
    by a later edit without failing the run.
    """
    import inspect

    from gsk_family.analysis import statistical_tests as st

    sig = inspect.signature(st.friedman_rank_test)
    upstream_default = sig.parameters["excluded"].default
    if tuple(upstream_default) != (2,):
        NOTES.append(
            "statistical_tests.friedman_rank_test excluded-default changed upstream "
            f"({upstream_default!r}); Amendment 1 A1.1 text describes (2,)")
    for suite, cfg in SUITE_CFG.items():
        excl = cfg["excluded_functions"]
        if not isinstance(excl, tuple):
            raise RuntimeError(f"{suite}: excluded_functions must be an explicit tuple")
        if 2 in excl:
            raise RuntimeError(
                f"{suite}: F2 is a legitimate function on this suite; the CEC2017 "
                f"excluded=(2,) convention must never reach it (Amendment 1 A1.1)")
    return {"upstream_default_excluded": list(upstream_default),
            "driver_exclusions": {s: list(c["excluded_functions"])
                                  for s, c in SUITE_CFG.items()},
            "helper_used_by_this_driver": False,
            "status": "hazard defused (explicit exclusion lists everywhere)"}


def suite_funcs(suite: str, dim_key, *, excluded) -> list[int]:
    """The function list for one (suite, dimension) cell.

    ``excluded`` is keyword-only and has NO default: a caller cannot inherit the
    CEC2017 ``(2,)`` convention by omission (Amendment 1 A1.1).
    """
    if excluded is None:
        raise TypeError("suite_funcs: 'excluded' must be passed explicitly "
                        "(Amendment 1 A1.1 latent hazard)")
    base = SUITE_CFG[suite]["funcs"][dim_key]
    return [f for f in base if f not in tuple(excluded)]


# ===========================================================================
# Formatting / IO helpers (phase6 house conventions)
# ===========================================================================
def F(v) -> str:
    """Format a float as C-locale %.6e; None -> literal n/a."""
    if v is None:
        return NA
    x = float(v)
    if np.isnan(x):
        raise ValueError("refusing to write NaN into an output CSV")
    if x == 0.0:
        x = 0.0
    return "%.6e" % x


def sha256_of(path: Path) -> str:
    key = str(path)
    if key not in _SHA_CACHE:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        _SHA_CACHE[key] = h.hexdigest()
    return _SHA_CACHE[key]


def _fresh_sha(path: Path) -> str:
    _SHA_CACHE.pop(str(path), None)
    return sha256_of(path)


def rel_ref(path: Path) -> str:
    return path.resolve().relative_to(REF_ROOT.resolve()).as_posix()


def _manifest_path(path: Path) -> str:
    p = path.resolve()
    try:
        return p.relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def write_csv(path: Path, header: list[str], rows: list[list[str]],
              analysis_ids: list[str]) -> None:
    p = assert_writable(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    MANIFEST_ENTRIES.append({"path": _manifest_path(p), "sha256": _fresh_sha(p),
                             "generator": SCRIPT_REL, "analysis_ids": analysis_ids})
    print(f"  wrote {p.name} ({len(rows)} rows)")


def write_json(path: Path, obj, analysis_ids: list[str] | None = None) -> None:
    p = assert_writable(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as fh:
        json.dump(obj, fh, indent=1, sort_keys=False)
        fh.write("\n")
    if analysis_ids is not None:
        MANIFEST_ENTRIES.append({"path": _manifest_path(p), "sha256": _fresh_sha(p),
                                 "generator": SCRIPT_REL, "analysis_ids": analysis_ids})
    print(f"  wrote {p.name}")


def write_text(path: Path, text: str, analysis_ids: list[str]) -> None:
    p = assert_writable(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    MANIFEST_ENTRIES.append({"path": _manifest_path(p), "sha256": _fresh_sha(p),
                             "generator": SCRIPT_REL, "analysis_ids": analysis_ids})


def add_stat(**kw) -> None:
    row = {c: NA for c in STAT_COLUMNS}
    row["evidence_release_id"] = REL_ID
    row["script"] = SCRIPT_REL
    row["command"] = COMMAND
    row["commit_sha"] = GIT_HEAD
    row["status"] = "ok"
    for k, v in kw.items():
        if k not in STAT_COLUMNS:
            raise KeyError(k)
        row[k] = v
    STAT_ROWS.append(row)


# ===========================================================================
# Data access layer (audited, strict-source)
# ===========================================================================
def suite_root(suite: str) -> Path:
    return REF_ROOT / suite


def summary_paths(suite: str, alg: str, dim_key=None) -> list[Path]:
    """Promoted summary CSVs for one (algorithm, dimension cell).

    CEC2013LSGO splits ONE analysis cell across two files (D1000 and the
    natively-905 F13/F14), so ``native`` always resolves to both; their function
    sets are disjoint. CEC2020 repeats F1-F10 at every dimension, so a dimension
    key MUST select exactly one file -- merging them would silently overwrite
    each dimension's rows with the next one's.
    """
    cfg = SUITE_CFG[suite]
    if suite == "cec2013lsgo":
        dims = cfg["summary_dims"]
    elif dim_key is None:
        dims = cfg["summary_dims"]
    else:
        dims = [int(dim_key)]
    return [suite_root(suite) / alg / f"{alg}_{suite}_D{d}.csv" for d in dims]


def per_run_path(suite: str, alg: str) -> Path:
    return suite_root(suite) / alg / "per_run.csv"


def load_endpoints(suite: str, alg: str) -> dict:
    """{(dim, func): {run: endpoint}} plus seeds and runtimes, from per_run.csv.

    The endpoint column is the suite's registered basis: ``best_fitness`` (raw)
    for CEC2013LSGO -- its ``error`` column is not populated -- and ``error``
    for CEC2020.
    """
    key = (suite, alg)
    if key in _ENDPOINT_CACHE:
        return _ENDPOINT_CACHE[key]
    path = per_run_path(suite, alg)
    if not path.is_file():
        raise RuntimeError(f"per_run.csv missing from the release: {path}")
    rl.audit_source_open(path, role="per_run_csv")
    col = SUITE_CFG[suite]["endpoint_column"]
    endpoint: dict = {}
    seeds: dict = {}
    runtime: dict = {}
    with open(path, "r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            func, dim, run = int(row["function"]), int(row["dimension"]), int(row["run"])
            endpoint.setdefault((dim, func), {})[run] = float(row[col])
            seeds[(dim, func, run)] = int(row["seed"])
            rt = (row.get("runtime_seconds") or "").strip()
            runtime.setdefault((dim, func), {})[run] = (
                float(rt) if rt and rt.lower() != "nan" else None)
    out = {"endpoint": endpoint, "seeds": seeds, "runtime": runtime,
           "path": rel_ref(path), "rows": sum(len(v) for v in endpoint.values())}
    _ENDPOINT_CACHE[key] = out
    return out


def load_release_summary(suite: str, alg: str, dim_key) -> dict[int, dict]:
    """Promoted per-function summary rows for ONE analysis cell."""
    merged: dict[int, dict] = {}
    for p in summary_paths(suite, alg, dim_key):
        stats = rl.load_summary_csv(p)      # audited chokepoint (role=summary_csv)
        if not stats:
            raise RuntimeError(f"summary CSV missing/unreadable: {p}")
        for fid, fs in stats.items():
            merged[fid] = {"best": fs.best, "median": fs.median, "mean": fs.mean,
                           "worst": fs.worst, "sd": fs.sd}
    return merged


def cell_dim(suite: str, dim_key, func: int) -> int:
    """Physical dimension of a (dim_key, func) cell (LSGO F13/F14 sit at 905)."""
    nat = SUITE_CFG[suite]["native_dim"]
    return nat[func] if nat is not None else int(dim_key)


def endpoint_runs(suite: str, alg: str, dim_key, func: int) -> np.ndarray:
    cell = load_endpoints(suite, alg)["endpoint"].get((cell_dim(suite, dim_key, func), func))
    if not cell:
        raise RuntimeError(f"missing per-run cell {suite}/{alg} F{func} @{dim_key}")
    return np.array([cell[r] for r in sorted(cell)], dtype=np.float64)


def cell_stats(suite: str, alg: str, dim_key) -> dict:
    """Per-function mean/median computed from the PINNED per_run.csv inputs.

    Amendment 1 A1.3 pins the seven ``per_run.csv`` files by SHA-256, so the
    per-run values -- not the 10-significant-digit summary transcriptions -- are
    the inputs of record. The promoted summary CSVs are cross-checked against
    these in :func:`step_precheck` and any deviation is reported.
    """
    key = (suite, alg, dim_key)
    if key not in _STATS_CACHE:
        funcs = suite_funcs(suite, dim_key,
                            excluded=SUITE_CFG[suite]["excluded_functions"])
        d = {}
        for f in funcs:
            v = endpoint_runs(suite, alg, dim_key, f)
            d[f] = {"mean": float(np.mean(v)), "median": float(np.median(v)),
                    "best": float(np.min(v)), "worst": float(np.max(v)),
                    "sd": float(np.std(v, ddof=1)), "n": int(v.size)}
        _STATS_CACHE[key] = d
    return _STATS_CACHE[key]


def means_of(suite: str, dim_key) -> dict[str, dict[int, float]]:
    return {a: {f: s["mean"] for f, s in cell_stats(suite, a, dim_key).items()}
            for a in PANEL}


def medians_of(suite: str, dim_key) -> dict[str, dict[int, float]]:
    return {a: {f: s["median"] for f, s in cell_stats(suite, a, dim_key).items()}
            for a in PANEL}


def _summary_sources(suite: str, dim_key=None) -> tuple[str, str]:
    """Provenance for one analysis cell (or the whole suite when dim_key=None)."""
    paths = [p for a in PANEL for p in summary_paths(suite, a, dim_key)]
    return (";".join(rel_ref(p) for p in paths), ";".join(sha256_of(p) for p in paths))


def _per_run_sources(suite: str, comp: str) -> tuple[str, str]:
    p1, p2 = per_run_path(suite, PROPOSED), per_run_path(suite, comp)
    return f"{rel_ref(p1)};{rel_ref(p2)}", f"{sha256_of(p1)};{sha256_of(p2)}"


# ===========================================================================
# Statistical primitives
# ===========================================================================
def midranks(v: np.ndarray) -> np.ndarray:
    return sps.rankdata(v, method="average")


def exact_signflip_p(d: np.ndarray, tol: float = TIE_TOL) -> dict:
    """Two-sided EXACT sign-flip p over all 2^n signed-rank patterns.

    The enumeration is realized as an exact integer convolution over the
    (doubled, so integral) midranks of |d| -- mathematically identical to
    enumerating the 2^n equiprobable sign assignments, with exact integer
    counts and no sampling anywhere. Unlike ``scipy.stats.wilcoxon(
    method="exact")`` it remains defined when |d| carries ties (midranks are
    conditioned on, which is the correct permutation null); it agrees with
    scipy to the last bit when there are none -- verified over all 90
    LSGO run-level cells.

    Zeros ``|d| < tol`` are discarded first (addendum Section 5).
    """
    d = np.asarray(d, dtype=np.float64)
    keep = np.abs(d) >= tol
    n_zero = int(np.sum(~keep))
    dz = d[keep]
    n = int(dz.size)
    if n == 0:
        return {"p_exact": 1.0, "n_eff": 0, "n_zero": n_zero, "w_plus": 0.0,
                "w_minus": 0.0, "statistic": 0.0}
    r = midranks(np.abs(dz))
    r2 = np.rint(r * 2).astype(np.int64)         # midranks are half-integers
    total = int(r2.sum())
    counts = [0] * (total + 1)
    counts[0] = 1
    for w in r2.tolist():
        nxt = [0] * (total + 1)
        for s in range(total - w + 1):
            c = counts[s]
            if c:
                nxt[s] += c
                nxt[s + w] += c
        counts = nxt
    w_plus = float(np.sum(r[dz > 0]))
    w_minus = float(np.sum(r[dz < 0]))
    obs2 = int(round(min(w_plus, w_minus) * 2))
    cnt = 0
    for s, c in enumerate(counts):
        if c and (s <= obs2 or (total - s) <= obs2):
            cnt += c
    p = min(cnt / float(2 ** n), 1.0)
    return {"p_exact": p, "n_eff": n, "n_zero": n_zero, "w_plus": w_plus,
            "w_minus": w_minus, "statistic": float(min(w_plus, w_minus))}


def wilcoxon_record(x: np.ndarray, y: np.ndarray) -> dict:
    """Full two-sided Wilcoxon record: exact decision p + normal companion.

    ``p_decision`` is the EXACT sign-flip value (addendum Section 4). The
    normal-approximation p from the repo tool of record
    (``statistics.wilcoxon_paired``) is recorded alongside for continuity with
    the frozen suites, and the method used is recorded per row (SAP 6a) -- which
    is also how the exact/normal docstring-vs-code contradiction in
    ``statistics.py`` is neutralized here: nothing is inferred from the helper's
    documentation, both values are computed and labelled.
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    d = x - y
    keep = np.abs(d) >= TIE_TOL
    ex = exact_signflip_p(d)
    if int(np.sum(keep)) == 0:
        p_norm = 1.0
        stat_norm = 0.0
    else:
        res = wilcoxon_paired(x[keep], y[keep])
        p_norm = float(res.p_value)
        stat_norm = float(res.statistic)
    n = ex["n_eff"]
    w_plus, w_minus = ex["w_plus"], ex["w_minus"]
    if n == 0 or w_plus == w_minus:
        direction = "none"
    elif w_minus > w_plus:
        direction = "favors_dt-gsk"       # negative diffs => dt-gsk lower
    else:
        direction = "favors_comparator"
    rb = None if n == 0 else (w_minus - w_plus) / (w_plus + w_minus)
    decidable = n >= 6
    return {
        "p_decision": ex["p_exact"], "p_exact": ex["p_exact"], "p_normal": p_norm,
        "statistic": ex["statistic"], "statistic_normal": stat_norm,
        "n_eff": n, "n_zero": ex["n_zero"], "w_plus": w_plus, "w_minus": w_minus,
        "direction": direction, "rank_biserial": rb, "decidable": decidable,
        "decidability": "decidable" if decidable else NOT_DECIDABLE,
        "method": ("exact_signflip_enumeration_2^n (decision); "
                   "normal_approx_continuity(statistics.wilcoxon_paired) recorded"),
    }


def rank_matrix(means: dict[str, dict[int, float]], funcs: list[int]) -> np.ndarray:
    """(N x k) midrank matrix, rows = functions, columns = PANEL order."""
    mat = np.array([[means[a][f] for a in PANEL] for f in funcs], dtype=np.float64)
    return np.vstack([midranks(row) for row in mat])


def _chi2_from_ranks(rm: np.ndarray) -> float:
    n, k = rm.shape
    mr = rm.mean(axis=0)
    return float((12.0 * n / (k * (k + 1))) * np.sum((mr - (k + 1) / 2.0) ** 2))


def friedman_with_id(means: dict[str, dict[int, float]], funcs: list[int]) -> dict:
    """Tie-corrected Friedman (statistics.friedman_rank, M-026) + Iman-Davenport."""
    data = {a: [means[a][f] for f in funcs] for a in PANEL}
    fr = friedman_rank(data)
    n, k = fr.n_problems, fr.n_algorithms
    if k != K_PANEL:
        raise RuntimeError(f"panel size mismatch: friedman k={k}, PANEL k={K_PANEL}")

    chi2_unc = float(fr.statistic)
    chi2_cor = float(fr.statistic_tie_corrected)
    p_chi2_cor = float(fr.p_value_tie_corrected)
    undefined = not np.isfinite(chi2_cor)
    if undefined:                      # fully-tied family: never fabricate a value
        chi2_cor, p_chi2_cor = chi2_unc, float(fr.p_value)

    def iman_davenport(chi2: float):
        denom = n * (k - 1) - chi2
        if denom <= 1e-12:
            return None, 0.0
        f = (n - 1) * chi2 / denom
        return f, float(sps.f.sf(f, k - 1, (k - 1) * (n - 1)))

    f_cor, p_cor = iman_davenport(chi2_cor)
    f_unc, p_unc = iman_davenport(chi2_unc)

    rm = rank_matrix(means, funcs)
    mr_check = rm.mean(axis=0)
    for i, a in enumerate(PANEL):
        if abs(mr_check[i] - fr.avg_ranks[a]) > 1e-12:
            raise DriverDefect(
                f"rank cross-check failed for {a}: {mr_check[i]} vs {fr.avg_ranks[a]}")
    return {"mean_ranks": dict(fr.avg_ranks), "rank_matrix": rm,
            "chi2": chi2_cor, "p_chi2": p_chi2_cor, "f_id": f_cor, "p_id": p_cor,
            "chi2_uncorrected": chi2_unc, "p_chi2_uncorrected": float(fr.p_value),
            "f_id_uncorrected": f_unc, "p_id_uncorrected": p_unc,
            "tie_correction": float(fr.tie_correction),
            "n_tied_problems": int(fr.n_tied_problems),
            "statistic_undefined": undefined, "n": n, "k": k}


def permutation_friedman_p(rm: np.ndarray, seed_list: list[int]) -> dict:
    """Seeded within-block Monte-Carlo permutation p for the omnibus.

    B = 100,000 within-block permutations (each function's k values permuted
    independently, which permutes that block's midranks and preserves its tie
    structure -- so the tie correction C is invariant and comparing uncorrected
    statistics is identical to comparing corrected ones). Draws are taken in
    fixed 5,000-sample chunks from one seeded Generator; the chunk size is part
    of the determinism contract. p = (1 + #{stat_perm >= stat_obs}) / (B + 1).
    """
    n, k = rm.shape
    obs = _chi2_from_ranks(rm)
    rng = np.random.default_rng(np.random.SeedSequence(seed_list))
    ge = 0
    done = 0
    while done < B_PERM:
        b = min(PERM_CHUNK, B_PERM - done)
        block = np.broadcast_to(rm, (b, n, k)).copy()
        perm = rng.permuted(block, axis=2)
        mr = perm.mean(axis=1)
        stat = (12.0 * n / (k * (k + 1))) * np.sum((mr - (k + 1) / 2.0) ** 2, axis=1)
        ge += int(np.sum(stat >= obs - 1e-12))
        done += b
    return {"p_perm": (1 + ge) / (B_PERM + 1), "B": B_PERM, "ge": ge,
            "stat_obs": obs, "seed": seed_list}


def nemenyi_cd(k: int, n_blocks: int) -> tuple[float, float]:
    """Nemenyi critical difference, PARAMETERIZED BY k (never hardcoded)."""
    if k not in NEMENYI_Q_005:
        raise RuntimeError(f"no Demsar q_0.05 tabulated for k={k}")
    q = NEMENYI_Q_005[k]
    return q, q * float(np.sqrt(k * (k + 1) / (6.0 * n_blocks)))


#: SAP Section 7 disclosure string for the BCa-undefined case, verbatim.
DISCLOSURE_PERCENTILE = "percentile (BCa degenerate)"


def _bca_terms_defined(d: np.ndarray, seed_list: list[int]) -> tuple[bool, np.ndarray]:
    """Report whether BCa's bias/acceleration terms are defined for this cell.

    SAP Section 7 lists three degeneracy conditions. Two (all-identical
    differences, zero variance) are testable from the data. The third -- the
    bias-correction z0 or the acceleration a_hat being undefined -- is absorbed
    SILENTLY by ``bootstrap_bca_ci``: it clamps ``frac_below`` into
    ``[1e-9, 1-1e-9]`` (statistics.py) and sets ``a_hat = 0.0`` when the
    jackknife denominator vanishes, returning only ``(lo, hi, point)``. A caller
    therefore cannot tell a genuine BCa interval from a silently-rescued one.

    This re-derives the two terms from the SAME deterministic resampling the
    primitive performs (identical SeedSequence, identical ``rng.integers`` draw
    shape), so the diagnostic corresponds exactly to the interval that would be
    produced. The primitive itself is not modified -- ruling R3 forbids editing
    the shared statistics primitives from this driver.

    HOW OFTEN CAN THIS FIRE? For the MEAN statistic used here, provably never
    on a non-constant sample, so this guard is belt-and-braces rather than a
    live bug fix -- stated plainly so nobody later reads it as evidence that
    degenerate cells were found. Sketch: some resample (all copies of min(x))
    has mean below mean(x) and another (all copies of max(x)) has mean above it,
    so ``0 < frac_below < 1``; and ``sum(u**2) == 0`` iff every jackknife mean is
    equal, iff x is constant. Both terms are therefore undefined only when x is
    constant -- the case the caller already catches first. Measured over 399
    non-constant vectors spanning single spikes, heavy tails, near-constant and
    error-floor-like shapes, ``frac_below`` stayed within [0.252, 0.586].

    The guard is kept because the SAP names the condition, because the disclosure
    string would otherwise be unreachable dead text, and because a future
    estimator swap (a median or a trimmed mean, where the argument above fails)
    would silently lose the protection.

    Returns
    -------
    (ok, boots)
        ``ok`` is False when either term is undefined; ``boots`` is the
        bootstrap distribution of the mean, reusable for a percentile fallback.
    """
    x = np.asarray(d, dtype=np.float64).ravel()
    n = x.size
    rng = np.random.default_rng(np.random.SeedSequence(seed_list))
    idx = rng.integers(0, n, size=(B_BOOT, n))
    boots = x[idx].mean(axis=1)

    # z0 is undefined when every resample falls on one side of the estimate.
    frac_below = float(np.mean(boots < float(np.mean(x))))
    z0_defined = 0.0 < frac_below < 1.0

    # a_hat is undefined when the jackknife denominator vanishes.
    total = x.sum()
    jack_means = (total - x) / (n - 1)
    u = float(np.mean(jack_means)) - jack_means
    a_defined = 6.0 * float(np.sum(u ** 2)) ** 1.5 > 0.0

    return bool(z0_defined and a_defined), boots


def a12_band(x: np.ndarray, y: np.ndarray):
    """Vargha-Delaney A12 with the SAP Sec.7 tie band |d|<1e-8 counted half."""
    diff = y[None, :] - x[:, None]
    ties = np.abs(diff) < TIE_TOL
    wins = (diff > 0) & ~ties
    a12 = (float(np.sum(wins)) + 0.5 * float(np.sum(ties))) / (len(x) * len(y))
    dlt = 2.0 * a12 - 1.0
    m = abs(a12 - 0.5)
    mag = ("negligible" if m < 0.06 else "small" if m < 0.14
           else "medium" if m < 0.21 else "large")
    return a12, dlt, mag


def wtl_means(a: dict[int, float], b: dict[int, float], funcs: list[int],
              relative_band: bool = False):
    """W/T/L on per-function means; absolute band 1e-8 (SAP Sec.4) by default.

    ``relative_band=True`` selects the pre-registered LSGO robustness variant
    (raw magnitudes reach 1e+9, where 1e-8 absolute is below double precision).
    """
    w = t = lo = 0
    for f in funcs:
        d = a[f] - b[f]
        band = TIE_TOL
        if relative_band:
            band = max(TIE_TOL, 1e-10 * max(abs(a[f]), abs(b[f]), 1.0))
        if abs(d) < band:
            t += 1
        elif d < 0:
            w += 1
        else:
            lo += 1
    return w, t, lo


def ordinals(mean_ranks: dict[str, float]) -> dict[str, int]:
    return {a: 1 + sum(1 for b in mean_ranks.values() if b < r - 1e-12)
            for a, r in mean_ranks.items()}


def outcome_of(sig: bool, direction: str) -> str:
    if sig and direction == "favors_dt-gsk":
        return "win"
    if sig and direction == "favors_comparator":
        return "loss"
    return "tie"


# ===========================================================================
# Identity helpers
# ===========================================================================
def an_id(family: str, suite: str, dim_key=None) -> str:
    if suite == "cec2013lsgo":
        return f"AN-{family}-LSGO-NATIVE"
    return f"AN-{family}-2020-D{dim_key}"


def rq_of(suite: str) -> str:
    return "RQ6"          # both new suites are secondary/corroborative


def dim_label(suite: str, dim_key) -> str:
    return "native" if suite == "cec2013lsgo" else str(dim_key)


def tier_note(suite: str, family: str) -> str:
    if suite != "cec2013lsgo":
        return "pre-registered confirmatory (addendum Sections 3-4)"
    if family in ("OMNI", "DESC", "ROB"):
        return LSGO_TIER_DISCLOSURE
    if family == "PW":
        return "SUPPORTING-WITH-DISCLOSURE (addendum Section 4)"
    return "CONFIRMATORY-WITH-DISCLOSURE (addendum Sections 3-4, never computed before signing)"


# ===========================================================================
# Steps a-c: environment, negative tests, readiness/pre-check
# ===========================================================================
def step_environment(suites: list[str], hazard: dict) -> None:
    global GIT_HEAD
    try:
        GIT_HEAD = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(PROJECT_ROOT),
                                  capture_output=True, text=True,
                                  check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        GIT_HEAD = "unavailable"
    prereg = {}
    for name in ("statistical_analysis_plan_addendum_cec2020_lsgo.md",
                 "statistical_analysis_plan_addendum_cec2020_lsgo_amendment_01.md"):
        p = PHASE05 / name
        prereg[name] = sha256_of(p) if p.is_file() else "MISSING"
    record = {
        "release_id": REL_ID,
        "anchor_commit": ANCHOR,
        "suites": suites,
        "git_head_at_run": GIT_HEAD,
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": {"numpy": np.__version__,
                     "scipy": __import__("scipy").__version__},
        "locale": {"LC_ALL": os.environ.get("LC_ALL"), "LANG": os.environ.get("LANG"),
                   "python_locale": list(locale.getlocale())},
        "strict_source": {"env_GSK_STRICT_SOURCE": os.environ.get("GSK_STRICT_SOURCE"),
                          "programmatic_set_strict_source": True},
        "preregistration_sha256": prereg,
        "f2_exclusion_hazard": hazard,
        "output_guard": {"frozen_primary": FROZEN_PRIMARY_RELEASE,
                         "rule": "no output path may carry a 'rel-*' component",
                         "out_root": _manifest_path(OUT_ROOT)},
        "rng_policy": (
            "BCa: default_rng(SeedSequence([20240620, suite_ordinal, dimension, "
            "function, comparator_P1_index])), B=10000. Omnibus permutation: "
            "default_rng(SeedSequence([20240620, 2020, dimension, 0, 99])), "
            "B=100000 in fixed 5000-draw chunks. No other stochastic step."),
        "cwd": str(Path.cwd()),
        "argv": sys.argv,
    }
    write_json(OUT_ROOT / "environment_record.json", record, analysis_ids=["ENVIRONMENT"])


def step_negative_tests() -> dict:
    """Strict-source negative probes (phase6 step b, adapted to the new suites)."""
    rl.set_strict_source(True)
    results = {}
    probes = [
        ("results/_run_all path via audit_source_open",
         lambda: rl.audit_source_open(
             RESULTS_ROOT / "_run_all" / "dt-gsk" / "cec2013lsgo" / "summary" /
             "per_run.csv", role="per_run_csv")),
        ("results/_run_all cec2020 staging via audit_source_open",
         lambda: rl.audit_source_open(
             RESULTS_ROOT / "_run_all" / "dt-gsk" / "cec2020" / "summary" /
             "per_run.csv", role="per_run_csv")),
        ("load_reproduced() staging resolver",
         lambda: rl.load_reproduced("dt-gsk", "CEC2013LSGO", 1000)),
    ]
    for name, fn in probes:
        try:
            fn()
        except rl.StrictSourceViolation:
            results[name] = "PASS (StrictSourceViolation raised)"
        else:
            results[name] = "FAIL (no StrictSourceViolation)"
    # Output-guard negative probes: the frozen bundle must be unreachable.
    for label, target in (("papers/analysis/rel-2026-07-20-67d9345f9",
                           ANALYSIS_ROOT / FROZEN_PRIMARY_RELEASE / "x.csv"),
                          ("benchmarks/cec_reference_results",
                           REF_ROOT / "cec2013lsgo" / "x.csv"),
                          ("results/ staging", RESULTS_ROOT / "x.csv")):
        try:
            assert_writable(target)
        except OutputGuardViolation:
            results[f"write guard: {label}"] = "PASS (OutputGuardViolation raised)"
        else:
            results[f"write guard: {label}"] = "FAIL (write would be allowed)"
    if any(v.startswith("FAIL") for v in results.values()):
        raise RuntimeError(f"negative test failed: {results}")
    if len(rl.get_source_audit()) != 0:
        raise RuntimeError("negative tests polluted the source audit log")
    for name, verdict in results.items():
        print(f"    {verdict:45s} {name}")
    return results


def gate_suite_ready(suite: str) -> dict:
    """Refuse to analyse an incomplete suite. CEC2020's data is not ready yet."""
    cfg = SUITE_CFG[suite]
    want_rows, want_cells, want_runs = cfg["expected_rows"], cfg["expected_cells"], cfg["runs"]
    root = suite_root(suite)
    problems: list[str] = []
    banks: dict[str, dict] = {}
    if not root.is_dir():
        raise SystemExit(
            f"\nANALYSIS REFUSED -- {suite}: the promoted evidence tree "
            f"{_manifest_path(root)} does not exist.\n"
            f"  The {suite} campaign has not been promoted to a release. The "
            f"pre-registration (addendum Section 11) requires all seven banks at "
            f"{want_rows} rows each ({want_cells} protocol cells x {want_runs} runs) "
            f"before any {suite} statistic may be computed.\n"
            f"  Mint the release with: python papers/scripts/promote_suite.py "
            f"--suite {suite}\n")
    for alg in PANEL:
        p = per_run_path(suite, alg)
        if not p.is_file():
            problems.append(f"{alg}: per_run.csv ABSENT ({_manifest_path(p)})")
            banks[alg] = {"rows": 0, "cells": 0, "status": "ABSENT"}
            continue
        ep = load_endpoints(suite, alg)
        rows = ep["rows"]
        cells = len(ep["endpoint"])
        bad_runs = sorted(f"D{d}F{f}={len(v)}" for (d, f), v in ep["endpoint"].items()
                          if len(v) != want_runs)
        ok = (rows == want_rows and cells == want_cells and not bad_runs)
        banks[alg] = {"rows": rows, "cells": cells,
                      "status": "ok" if ok else "INCOMPLETE"}
        if not ok:
            problems.append(
                f"{alg}: {rows}/{want_rows} rows, {cells}/{want_cells} cells"
                + (f", short cells: {bad_runs[:6]}" if bad_runs else ""))
    if problems:
        detail = "\n".join(f"    - {p}" for p in problems)
        raise SystemExit(
            f"\nANALYSIS REFUSED -- {suite} banks are INCOMPLETE. The data is not "
            f"ready yet.\n"
            f"  Required (addendum Section 11): 7 banks x {want_rows} rows "
            f"({want_cells} protocol cells x {want_runs} runs).\n{detail}\n"
            f"  No {suite} statistic may be computed until every bank passes. "
            f"Re-run this driver after the campaign completes and the release is "
            f"minted.\n")
    return banks


def step_precheck(suite: str, negative: dict, banks: dict) -> None:
    """Row counts, seed pairing audit, and summary-vs-per-run agreement."""
    cfg = SUITE_CFG[suite]
    # --- pairing audit (addendum Section 12: precondition for every paired test)
    base = load_endpoints(suite, PROPOSED)["seeds"]
    mismatches: dict[str, int] = {}
    injective: dict[str, bool] = {}
    for alg in PANEL:
        s = load_endpoints(suite, alg)["seeds"]
        mismatches[alg] = sum(1 for k, v in s.items() if base.get(k) != v)
        injective[alg] = len(set(s.values())) == len(s)
    if any(mismatches.values()) or not all(injective.values()):
        raise RuntimeError(
            f"{suite}: pairing audit FAILED (seed mismatches={mismatches}, "
            f"injective={injective}); every run-level paired statistic is blocked")
    # --- summary CSV vs per-run agreement
    worst = 0.0
    worst_cell = None
    for alg in PANEL:
        for dim_key in cfg["dim_keys"]:
            summ = load_release_summary(suite, alg, dim_key)
            for f, s in cell_stats(suite, alg, dim_key).items():
                ref = summ.get(f, {}).get("mean")
                if ref is None:
                    raise RuntimeError(
                        f"{suite}/{alg}: summary CSV for {dim_label(suite, dim_key)} "
                        f"lacks F{f}")
                denom = max(abs(ref), abs(s["mean"]))
                rel = 0.0 if denom == 0.0 else abs(ref - s["mean"]) / denom
                if rel > worst:
                    worst, worst_cell = rel, f"{alg}/{dim_label(suite, dim_key)}/F{f}"
    if worst > 1e-6:
        raise RuntimeError(
            f"{suite}: promoted summary means disagree with per_run.csv "
            f"(max relative deviation {worst:.3e} at {worst_cell})")
    if worst > 1e-9:
        NOTES.append(f"{suite}: summary/per-run max relative deviation "
                     f"{worst:.3e} at {worst_cell} (transcription rounding)")
    pre = {
        "release_id": REL_ID, "anchor_commit": ANCHOR, "suite": suite,
        "negative_tests": negative,
        "bank_completeness": banks,
        "expected_rows_per_bank": cfg["expected_rows"],
        "pairing_audit": {"seed_mismatches_vs_dt-gsk": mismatches,
                          "seed_injective_within_bank": injective,
                          "authority": "addendum Section 12; "
                                       "seed_and_pairing_audit.md Sections 1-4"},
        "summary_vs_per_run": {"max_relative_deviation": worst,
                               "at": worst_cell,
                               "basis_of_record": "per_run.csv (pinned by "
                                                  "Amendment 1 A1.3 SHA-256)"},
        "per_run_sha256": {a: sha256_of(per_run_path(suite, a)) for a in PANEL},
    }
    write_json(OUT_ROOT / suite / "source_precheck.json", pre, analysis_ids=["PRECHECK"])


# ===========================================================================
# Families
# ===========================================================================
def family_descriptive(suite: str) -> None:
    """Per-function descriptives + W/T/L (transcription-grade, no test)."""
    cfg = SUITE_CFG[suite]
    metric = "best_fitness" if cfg["basis"] == "raw_objective" else "error"
    for dim_key in cfg["dim_keys"]:
        sp, sc = _summary_sources(suite, dim_key)
        funcs = suite_funcs(suite, dim_key, excluded=cfg["excluded_functions"])
        rows = []
        for f in funcs:
            for alg in PANEL:
                s = cell_stats(suite, alg, dim_key)[f]
                rows.append([suite, str(cell_dim(suite, dim_key, f)), str(f), alg,
                             F(s["best"]), F(s["median"]), F(s["mean"]),
                             F(s["worst"]), F(s["sd"]), str(s["n"])])
        write_csv(OUT_ROOT / suite / f"descriptive_stats_{suite}_{dim_label(suite, dim_key)}.csv",
                  ["suite", "dimension", "function", "algorithm", "best", "median",
                   "mean", "worst", "sd", "n_runs"], rows, ["DESC-TRANSCRIPTION"])
        means = means_of(suite, dim_key)
        for comp in COMPARATORS:
            w, t, lo = wtl_means(means[PROPOSED], means[comp], funcs)
            add_stat(analysis_id="DESC-TRANSCRIPTION", rq_id=rq_of(suite), suite=suite,
                     dimension=dim_label(suite, dim_key), function_set=cfg["fset"][dim_key],
                     algorithms=f"dt-gsk vs {comp}",
                     metric=f"win_tie_loss_per_function_mean_{metric}",
                     unit_of_analysis="function", n_observations=str(len(funcs)),
                     pairing_key="function_identity", test="none (descriptive)",
                     effect_direction=("favors_dt-gsk" if w > lo else
                                       ("favors_comparator" if lo > w else "none")),
                     source_paths=sp, source_checksums=sc,
                     interpretation=(f"W={w};T={t};L={lo};tie_rule=|delta|<1e-8;"
                                     + tier_note(suite, "DESC")))


def family_omnibus(suite: str) -> dict:
    """AN-OMNI-* (+ AN-RANKAGG-2020-OVERALL for CEC2020)."""
    cfg = SUITE_CFG[suite]
    fried: dict = {}
    for dim_key in cfg["dim_keys"]:
        sp, sc = _summary_sources(suite, dim_key)
        funcs = suite_funcs(suite, dim_key, excluded=cfg["excluded_functions"])
        means = means_of(suite, dim_key)
        res = friedman_with_id(means, funcs)
        fam = an_id("OMNI", suite, dim_key)
        dl = dim_label(suite, dim_key)

        perm = None
        if cfg["permutation_omnibus"]:
            perm = permutation_friedman_p(
                res["rank_matrix"], [BASE_SEED, cfg["ordinal"], int(dim_key), 0, 99])

        # Decision: Iman-Davenport at alpha=.05; the permutation p governs
        # boundary disagreements (addendum Section 4) -- disclosed per row.
        sig_id = (res["p_id"] is not None) and (res["p_id"] < ALPHA)
        if perm is not None:
            sig_perm = perm["p_perm"] < ALPHA
            disagree = sig_id != sig_perm
            significant = sig_perm if disagree else sig_id
            decision_note = (
                f"iman_davenport p={res['p_id']:.6f} ({'sig' if sig_id else 'n.s.'}); "
                f"permutation p={perm['p_perm']:.6f} ({'sig' if sig_perm else 'n.s.'}); "
                + ("BOUNDARY DISAGREEMENT -- permutation p governs (addendum Sec.4)"
                   if disagree else "procedures agree"))
        else:
            significant = sig_id
            decision_note = ("iman_davenport decision; no permutation companion "
                             "registered for this suite")

        header = ["suite", "dimension", "n_blocks", "k", "algorithm", "mean_rank",
                  "ordinal", "friedman_chi2", "iman_davenport_F", "p_value",
                  "p_permutation", "B_permutation", "permutation_seed",
                  "tie_correction_C", "n_tied_functions", "friedman_chi2_uncorrected",
                  "iman_davenport_F_uncorrected", "p_value_uncorrected",
                  "statistic_status", "evidential_tier"]
        ordn = ordinals(res["mean_ranks"])
        rows = [[suite, dl, str(res["n"]), str(res["k"]), alg,
                 F(res["mean_ranks"][alg]), str(ordn[alg]),
                 F(res["chi2"]), F(res["f_id"]), F(res["p_id"]),
                 F(perm["p_perm"]) if perm else NA,
                 str(B_PERM) if perm else NA,
                 ("SeedSequence(" + json.dumps(perm["seed"]) + ")") if perm else NA,
                 F(res["tie_correction"]), str(res["n_tied_problems"]),
                 F(res["chi2_uncorrected"]), F(res["f_id_uncorrected"]),
                 F(res["p_id_uncorrected"]),
                 "undefined (fully tied)" if res["statistic_undefined"] else "ok",
                 tier_note(suite, "OMNI")] for alg in PANEL]
        write_csv(OUT_ROOT / suite / f"friedman_ranks_{suite}_{dl}.csv",
                  header, rows, [fam])

        add_stat(analysis_id=fam, rq_id=rq_of(suite), suite=suite, dimension=dl,
                 function_set=cfg["fset"][dim_key], algorithms="panel-7",
                 metric="friedman_chi2_tie_corrected", unit_of_analysis="function",
                 n_observations=str(res["n"]), pairing_key="function_identity",
                 test="friedman", test_statistic=F(res["chi2"]), p_raw=F(res["p_chi2"]),
                 correction="tie-corrected rank variance (M-026)",
                 source_paths=sp, source_checksums=sc,
                 interpretation=(f"C={res['tie_correction']:.6f} over "
                                 f"{res['n_tied_problems']} tied block(s); "
                                 f"uncorrected chi2={res['chi2_uncorrected']:.4f}; "
                                 + tier_note(suite, "OMNI")))
        add_stat(analysis_id=fam, rq_id=rq_of(suite), suite=suite, dimension=dl,
                 function_set=cfg["fset"][dim_key], algorithms="panel-7",
                 metric="iman_davenport_F", unit_of_analysis="function",
                 n_observations=str(res["n"]), pairing_key="function_identity",
                 test="iman_davenport", test_statistic=F(res["f_id"]),
                 p_raw=F(res["p_id"]),
                 correction="omnibus decision criterion, alpha=0.05",
                 source_paths=sp, source_checksums=sc,
                 interpretation=(("significant" if significant else
                                  "not significant -- no separation demonstrated")
                                 + "; " + decision_note))
        if perm is not None:
            add_stat(analysis_id=fam, rq_id=rq_of(suite), suite=suite, dimension=dl,
                     function_set=cfg["fset"][dim_key], algorithms="panel-7",
                     metric="within_block_permutation_p", unit_of_analysis="function",
                     n_observations=str(res["n"]), pairing_key="function_identity",
                     test="monte_carlo_permutation_friedman",
                     test_statistic=F(perm["stat_obs"]), p_raw=F(perm["p_perm"]),
                     correction="none (companion to the omnibus)",
                     resampling_unit="values within each function block",
                     n_resamples=str(B_PERM),
                     seed="SeedSequence(" + json.dumps(perm["seed"]) + ")",
                     source_paths=sp, source_checksums=sc,
                     interpretation=("p=(1+#{stat_perm>=stat_obs})/(B+1); "
                                     "this p governs boundary disagreements "
                                     "(addendum Sec.4)"))
        for alg in PANEL:
            add_stat(analysis_id=fam, rq_id=rq_of(suite), suite=suite, dimension=dl,
                     function_set=cfg["fset"][dim_key], algorithms=alg,
                     metric="friedman_mean_rank", unit_of_analysis="function",
                     n_observations=str(res["n"]), pairing_key="function_identity",
                     test="none (rank point value)",
                     effect_size=F(res["mean_ranks"][alg]),
                     source_paths=sp, source_checksums=sc,
                     interpretation=f"lower rank = better; ordinal={ordn[alg]}")

        # Nemenyi companion -- k PARAMETERIZED; emitted only when significant.
        q, cd = nemenyi_cd(K_PANEL, res["n"])
        if significant:
            write_csv(OUT_ROOT / suite / f"nemenyi_cd_{suite}_{dl}.csv",
                      ["suite", "dimension", "n_blocks", "k", "q_alpha_005",
                       "critical_difference", "algorithm", "mean_rank"],
                      [[suite, dl, str(res["n"]), str(K_PANEL), F(q), F(cd), alg,
                        F(res["mean_ranks"][alg])] for alg in PANEL], [fam])
            add_stat(analysis_id=fam, rq_id=rq_of(suite), suite=suite, dimension=dl,
                     function_set=cfg["fset"][dim_key], algorithms="panel-7",
                     metric="nemenyi_critical_difference", unit_of_analysis="function",
                     n_observations=str(res["n"]), pairing_key="function_identity",
                     test="nemenyi_cd", test_statistic=F(cd),
                     correction=f"Nemenyi q_0.05(k={K_PANEL})={q} (Demsar 2006 Table 5a)",
                     source_paths=sp, source_checksums=sc,
                     interpretation=("CD diagram inputs emitted (omnibus significant); "
                                     "low-powered family, addendum Section 7"))
        else:
            add_stat(analysis_id=fam, rq_id=rq_of(suite), suite=suite, dimension=dl,
                     function_set=cfg["fset"][dim_key], algorithms="panel-7",
                     metric="nemenyi_critical_difference", unit_of_analysis="function",
                     n_observations=str(res["n"]), pairing_key="function_identity",
                     test="nemenyi_cd", test_statistic=F(cd),
                     correction=f"Nemenyi q_0.05(k={K_PANEL})={q} (Demsar 2006 Table 5a)",
                     source_paths=sp, source_checksums=sc,
                     interpretation=("omnibus not significant; CD diagram omitted by "
                                     "pre-registration; no separation demonstrated"),
                     status="omitted-not-significant")
        res["significant"] = significant
        res["perm"] = perm
        res["cd"] = cd
        fried[dim_key] = res

    if suite == "cec2020":
        fam = "AN-RANKAGG-2020-OVERALL"
        overall = {a: float(np.mean([fried[d]["mean_ranks"][a] for d in cfg["dim_keys"]]))
                   for a in PANEL}
        ordn = ordinals(overall)
        write_csv(OUT_ROOT / suite / f"friedman_ranks_{suite}_overall.csv",
                  ["suite", "algorithm", "mean_rank", "ordinal", "n_dimensions",
                   "caption_disclosure"],
                  [[suite, a, F(overall[a]), str(ordn[a]), str(len(cfg["dim_keys"])),
                    RANKAGG_CAPTION] for a in PANEL], [fam])
        for a in PANEL:
            add_stat(analysis_id=fam, rq_id=rq_of(suite), suite=suite, dimension="overall",
                     function_set="F1-F10 (D5: F1-F5,F8-F10)", algorithms=a,
                     metric="mean_of_per_dimension_friedman_mean_ranks",
                     unit_of_analysis="dimension", n_observations=str(len(cfg["dim_keys"])),
                     pairing_key=NA,
                     test="none (descriptive aggregation; no test is ever attached)",
                     effect_size=F(overall[a]), source_paths=_summary_sources(suite)[0],
                     source_checksums=_summary_sources(suite)[1],
                     interpretation=RANKAGG_CAPTION)
        fried["overall"] = overall
    return fried


def family_pw(suite: str) -> dict:
    """AN-PW-*: across-function Wilcoxon on per-function means, Holm m=6."""
    cfg = SUITE_CFG[suite]
    out: dict = {}
    header = ["suite", "dimension", "comparator", "test_level", "n_functions", "n_eff",
              "n_zero_discarded", "statistic", "p_exact", "p_normal_approx",
              "p_decision", "p_holm", "method_decision", "method_companion",
              "outcome", "direction", "rank_biserial", "w_plus", "w_minus",
              "wins", "ties", "losses", "decidability", "evidential_tier"]
    for dim_key in cfg["dim_keys"]:
        sp, sc = _summary_sources(suite, dim_key)
        funcs = suite_funcs(suite, dim_key, excluded=cfg["excluded_functions"])
        means = means_of(suite, dim_key)
        x = np.array([means[PROPOSED][f] for f in funcs], dtype=np.float64)
        recs = {}
        for comp in COMPARATORS:
            y = np.array([means[comp][f] for f in funcs], dtype=np.float64)
            recs[comp] = wilcoxon_record(x, y)
        holm = holm_correction([recs[c]["p_decision"] for c in COMPARATORS],
                               list(COMPARATORS), alpha=ALPHA)
        p_holm = {str(c["label"]): float(c["p_adjusted"]) for c in holm.comparisons}
        fam = an_id("PW", suite, dim_key)
        dl = dim_label(suite, dim_key)
        rows = []
        for comp in COMPARATORS:
            r = recs[comp]
            sig = r["decidable"] and p_holm[comp] < ALPHA
            outcome = outcome_of(sig, r["direction"])
            w, t, lo = wtl_means(means[PROPOSED], means[comp], funcs)
            out[(dim_key, comp)] = {**r, "p_holm": p_holm[comp], "outcome": outcome,
                                    "wtl": (w, t, lo)}
            rows.append([suite, dl, comp, "across_functions_funclevel", str(len(funcs)),
                         str(r["n_eff"]), str(r["n_zero"]), F(r["statistic"]),
                         F(r["p_exact"]), F(r["p_normal"]), F(r["p_decision"]),
                         F(p_holm[comp]), "exact_signflip_enumeration_2^n",
                         "normal_approx_continuity(statistics.wilcoxon_paired)",
                         outcome, r["direction"], F(r["rank_biserial"]),
                         F(r["w_plus"]), F(r["w_minus"]), str(w), str(t), str(lo),
                         r["decidability"], tier_note(suite, "PW")])
            add_stat(analysis_id=fam, rq_id=rq_of(suite), suite=suite, dimension=dl,
                     function_set=cfg["fset"][dim_key], algorithms=f"dt-gsk vs {comp}",
                     metric="wilcoxon_signed_rank_across_functions_on_means",
                     unit_of_analysis="function", n_observations=str(r["n_eff"]),
                     pairing_key="function_identity",
                     test="wilcoxon_signed_rank_two_sided_exact",
                     test_statistic=F(r["statistic"]), p_raw=F(r["p_decision"]),
                     p_adjusted=F(p_holm[comp]), correction="holm_m6",
                     effect_size=F(r["rank_biserial"]), effect_direction=r["direction"],
                     source_paths=sp, source_checksums=sc,
                     interpretation=(
                         f"outcome={outcome};W/T/L={w}/{t}/{lo};n_eff={r['n_eff']} after "
                         f"discarding {r['n_zero']} zero(s) |d|<1e-8;"
                         f"p_exact={r['p_exact']:.6f};p_normal={r['p_normal']:.6f};"
                         f"method={r['method']};{r['decidability']};"
                         + tier_note(suite, "PW")),
                     status="ok" if r["decidable"] else "not-decidable")
        write_csv(OUT_ROOT / suite / f"wilcoxon_holm_{suite}_{dl}.csv", header, rows, [fam])
    return out


def family_pwrun(suite: str) -> dict:
    """AN-PWRUN-*: per-function run-level Wilcoxon, Holm across functions."""
    cfg = SUITE_CFG[suite]
    out: dict = {}
    header = ["suite", "dimension", "function", "comparator", "test_level", "n_pairs",
              "n_eff", "n_zero_discarded", "statistic", "p_exact", "p_normal_approx",
              "p_decision", "p_holm", "holm_m", "method_decision", "outcome",
              "direction", "rank_biserial", "decidability", "evidential_tier"]
    for dim_key in cfg["dim_keys"]:
        funcs = suite_funcs(suite, dim_key, excluded=cfg["excluded_functions"])
        fam = an_id("PWRUN", suite, dim_key)
        dl = dim_label(suite, dim_key)
        m = len(funcs)
        rows = []
        for comp in COMPARATORS:
            per_func = {}
            for f in funcs:
                per_func[f] = wilcoxon_record(endpoint_runs(suite, PROPOSED, dim_key, f),
                                              endpoint_runs(suite, comp, dim_key, f))
            holm = holm_correction([per_func[f]["p_decision"] for f in funcs],
                                   [str(f) for f in funcs], alpha=ALPHA)
            adj = {str(c["label"]): float(c["p_adjusted"]) for c in holm.comparisons}
            sp, sc = _per_run_sources(suite, comp)
            for f in funcs:
                r = per_func[f]
                sig = r["decidable"] and adj[str(f)] < ALPHA
                outcome = outcome_of(sig, r["direction"])
                out[(dim_key, f, comp)] = {**r, "p_holm": adj[str(f)], "outcome": outcome}
                rows.append([suite, str(cell_dim(suite, dim_key, f)), str(f), comp,
                             "per_function_runlevel", str(cfg["runs"]), str(r["n_eff"]),
                             str(r["n_zero"]), F(r["statistic"]), F(r["p_exact"]),
                             F(r["p_normal"]), F(r["p_decision"]), F(adj[str(f)]),
                             str(m), "exact_signflip_enumeration_2^n", outcome,
                             r["direction"], F(r["rank_biserial"]), r["decidability"],
                             tier_note(suite, "PWRUN")])
                add_stat(analysis_id=fam, rq_id=rq_of(suite), suite=suite, dimension=dl,
                         function_set=f"F{f}", algorithms=f"dt-gsk vs {comp}",
                         metric="wilcoxon_signed_rank_runlevel",
                         unit_of_analysis="run", n_observations=str(r["n_eff"]),
                         pairing_key="get_cec_seed(20240620,dim,func,run)",
                         test="wilcoxon_signed_rank_two_sided_exact",
                         test_statistic=F(r["statistic"]), p_raw=F(r["p_decision"]),
                         p_adjusted=F(adj[str(f)]), correction=f"holm_m{m}",
                         effect_size=F(r["rank_biserial"]),
                         effect_direction=r["direction"],
                         source_paths=sp, source_checksums=sc,
                         interpretation=(
                             f"outcome={outcome};n_eff={r['n_eff']} after discarding "
                             f"{r['n_zero']} zero(s);p_exact={r['p_exact']:.6f};"
                             f"p_normal={r['p_normal']:.6f};{r['decidability']};"
                             "Holm across functions per (dimension,comparator); NO "
                             "correction across the six comparators (addendum Sec.4); "
                             + tier_note(suite, "PWRUN")),
                         status="ok" if r["decidable"] else "not-decidable")
        write_csv(OUT_ROOT / suite / f"wilcoxon_run_{suite}_{dl}.csv", header, rows, [fam])
    return out


def family_effect(suite: str) -> None:
    """AN-EFF-*: A12 / Cliff's delta + BCa 95% CI on paired mean differences."""
    cfg = SUITE_CFG[suite]
    ordinal = cfg["ordinal"]
    eff_header = ["suite", "dimension", "function", "comparator", "n_runs", "a12",
                  "cliffs_delta", "magnitude", "availability"]
    bca_header = ["suite", "dimension", "function", "comparator", "n_runs", "mean_diff",
                  "ci_low", "ci_high", "B", "seed", "availability"]
    for dim_key in cfg["dim_keys"]:
        funcs = suite_funcs(suite, dim_key, excluded=cfg["excluded_functions"])
        fam = an_id("EFF", suite, dim_key)
        dl = dim_label(suite, dim_key)
        eff_rows, bca_rows = [], []
        for f in funcs:
            phys = cell_dim(suite, dim_key, f)
            for ci_idx, comp in enumerate(COMPARATORS):
                x = endpoint_runs(suite, PROPOSED, dim_key, f)
                y = endpoint_runs(suite, comp, dim_key, f)
                a12, dlt, mag = a12_band(x, y)
                sp, sc = _per_run_sources(suite, comp)
                eff_rows.append([suite, str(phys), str(f), comp, str(len(x)),
                                 F(a12), F(dlt), mag, "ok"])
                add_stat(analysis_id=fam, rq_id=rq_of(suite), suite=suite, dimension=dl,
                         function_set=f"F{f}", algorithms=f"dt-gsk vs {comp}",
                         metric="vargha_delaney_a12", unit_of_analysis="run",
                         n_observations=str(len(x)),
                         pairing_key="get_cec_seed(20240620,dim,func,run)",
                         test="none (estimation)", effect_size=F(a12),
                         effect_direction=("favors_dt-gsk" if a12 > 0.5 else
                                           ("favors_comparator" if a12 < 0.5 else "none")),
                         source_paths=sp, source_checksums=sc,
                         interpretation=(f"cliffs_delta={F(dlt)};magnitude={mag};"
                                         "A12>0.5 favors dt-gsk;ties |d|<1e-8 half;"
                                         + tier_note(suite, "EFF")))
                d = x - y
                mean_diff = float(np.mean(d))
                seed_list = [BASE_SEED, ordinal, phys, f, ci_idx]
                if bool(np.all(d == d[0])):
                    lo = hi = None
                    avail = "no CI (degenerate cell)"
                    interp = "no CI (degenerate cell): all paired differences identical"
                else:
                    rng = np.random.default_rng(np.random.SeedSequence(seed_list))
                    bca_ok, boots = _bca_terms_defined(d, seed_list)
                    if bca_ok:
                        lo, hi, _pt = bootstrap_bca_ci(d, n_boot=B_BOOT, alpha=ALPHA, rng=rng)
                        avail = "ok"
                        interp = ("BCa 95% CI on the paired mean difference "
                                  "(negative favors dt-gsk)")
                    else:
                        # SAP Section 7 third degeneracy condition: the BCa
                        # bias/acceleration terms are undefined. bootstrap_bca_ci
                        # absorbs this silently (it clamps frac_below into
                        # [1e-9, 1-1e-9] and sets a_hat=0 when the jackknife
                        # denominator vanishes) and returns an ordinary-looking
                        # interval, so the caller must detect it. Fall back to the
                        # plain percentile interval and SAY SO, which is what the
                        # SAP prescribes.
                        lo = float(np.percentile(boots, 100.0 * ALPHA / 2.0))
                        hi = float(np.percentile(boots, 100.0 * (1.0 - ALPHA / 2.0)))
                        avail = DISCLOSURE_PERCENTILE
                        interp = (f"{DISCLOSURE_PERCENTILE}: BCa bias/acceleration "
                                  "terms undefined for this cell; percentile "
                                  "interval reported instead")
                bca_rows.append([suite, str(phys), str(f), comp, str(len(x)),
                                 F(mean_diff), F(lo), F(hi),
                                 str(B_BOOT) if avail == "ok" else NA,
                                 ("SeedSequence(" + json.dumps(seed_list) + ")")
                                 if avail == "ok" else NA, avail])
                add_stat(analysis_id=fam, rq_id=rq_of(suite), suite=suite, dimension=dl,
                         function_set=f"F{f}", algorithms=f"dt-gsk vs {comp}",
                         metric="bca_ci_paired_mean_diff", unit_of_analysis="run",
                         n_observations=str(len(x)),
                         pairing_key="get_cec_seed(20240620,dim,func,run)",
                         test="none (estimation)", effect_size=F(mean_diff),
                         effect_direction=("favors_dt-gsk" if mean_diff < 0 else
                                           ("favors_comparator" if mean_diff > 0 else "none")),
                         ci_low=F(lo), ci_high=F(hi),
                         ci_level="0.95" if avail == "ok" else NA,
                         resampling_unit="paired runs within function",
                         n_resamples=str(B_BOOT) if avail == "ok" else NA,
                         seed=("SeedSequence(" + json.dumps(seed_list) + ")")
                              if avail == "ok" else NA,
                         source_paths=sp, source_checksums=sc,
                         interpretation=interp + ";" + tier_note(suite, "EFF"),
                         status="ok" if avail == "ok" else "disclosed-degenerate")
        write_csv(OUT_ROOT / suite / f"effect_sizes_{suite}_{dl}.csv",
                  eff_header, eff_rows, [fam])
        write_csv(OUT_ROOT / suite / f"bca_ci_{suite}_{dl}.csv",
                  bca_header, bca_rows, [fam])


# ---------------------------------------------------------------------------
# Robustness
# ---------------------------------------------------------------------------
ROB_HEADER = ["suite", "variant", "dimension", "row_type", "algorithm", "comparator",
              "primary_value", "primary_ordinal", "variant_value", "variant_ordinal",
              "verdict", "note"]


def _rob_rank_rows(suite: str, variant: str, dim_key, primary: dict,
                   variant_ranks: dict, note: str, rows: list, div: list) -> None:
    op, ov = ordinals(primary), ordinals(variant_ranks)
    for alg in PANEL:
        v = "agree" if op[alg] == ov[alg] else "diverge"
        if v == "diverge":
            div.append(f"{variant}@{dim_label(suite, dim_key)}:{alg} "
                       f"ordinal {op[alg]}->{ov[alg]}")
        rows.append([suite, variant, dim_label(suite, dim_key), "rank", alg, NA,
                     F(primary[alg]), str(op[alg]), F(variant_ranks[alg]),
                     str(ov[alg]), v, note])


def family_robustness(suite: str, fried: dict, pw: dict) -> None:
    """AN-ROB-2020 (three variants) / AN-ROB-LSGO (three variants)."""
    cfg = SUITE_CFG[suite]
    fam = "AN-ROB-2020" if suite == "cec2020" else "AN-ROB-LSGO"
    rows: list[list[str]] = []
    div: list[str] = []
    digest: list[str] = [f"# {fam} (pre-registered robustness, addendum Section 4)", ""]

    # ---- variant 1 (both suites): mean vs median re-rank -------------------
    for dim_key in cfg["dim_keys"]:
        funcs = suite_funcs(suite, dim_key, excluded=cfg["excluded_functions"])
        med = medians_of(suite, dim_key)
        var = friedman_with_id(med, funcs)["mean_ranks"]
        _rob_rank_rows(suite, "mean_vs_median", dim_key, fried[dim_key]["mean_ranks"],
                       var, "median basis re-rank (mandatory for every rank statement)",
                       rows, div)
        for comp in COMPARATORS:
            w1 = pw[(dim_key, comp)]["wtl"]
            w2 = wtl_means(med[PROPOSED], med[comp], funcs)
            v = "agree" if w1 == w2 else "diverge"
            if v == "diverge":
                div.append(f"mean_vs_median@{dim_label(suite, dim_key)}:wtl vs {comp} "
                           f"{w1}->{w2}")
            rows.append([suite, "mean_vs_median", dim_label(suite, dim_key), "wtl",
                         PROPOSED, comp, "-".join(map(str, w1)), NA,
                         "-".join(map(str, w2)), NA, v, "W/T/L on the median basis"])

    if suite == "cec2020":
        # ---- variant 2: across-dimension aggregate variants ----------------
        primary_overall = fried["overall"]
        po = ordinals(primary_overall)
        variants = {}
        sub = [d for d in cfg["dim_keys"] if d != 5]
        variants["aggregate_D10_15_20_only"] = {
            a: float(np.mean([fried[d]["mean_ranks"][a] for d in sub])) for a in PANEL}
        common: dict[str, list[float]] = {a: [] for a in PANEL}
        for d in cfg["dim_keys"]:
            m = means_of(suite, d)
            r = friedman_with_id(m, CEC2020_COMMON8)["mean_ranks"]
            for a in PANEL:
                common[a].append(r[a])
        variants["aggregate_common8_all_dims"] = {a: float(np.mean(common[a]))
                                                  for a in PANEL}
        flips = []
        for name, vr in variants.items():
            vo = ordinals(vr)
            for alg in PANEL:
                v = "agree" if po[alg] == vo[alg] else "diverge"
                if v == "diverge":
                    div.append(f"{name}:{alg} ordinal {po[alg]}->{vo[alg]}")
                    if alg == PROPOSED:
                        flips.append(f"{name}: dt-gsk {po[alg]}->{vo[alg]}")
                rows.append([suite, name, "overall", "rank", alg, NA,
                             F(primary_overall[alg]), str(po[alg]), F(vr[alg]),
                             str(vo[alg]), v, "across-dimension aggregate variant"])
        if flips:
            NOTES.append("AN-ROB-2020: aggregate variant flips DT-GSK's ordinal "
                         f"({flips}); SAP Section 10 binding rule -- the headline "
                         "MUST carry the instability disclosure")
            digest.append(f"**INSTABILITY DISCLOSURE REQUIRED** (SAP Sec.10): {flips}")
        else:
            digest.append("Aggregate variants: DT-GSK's ordinal is stable "
                          "(no instability disclosure triggered).")

        # ---- variant 3: floor sensitivity 1e-6 vs 1e-8 ---------------------
        for floor in FLOOR_SENSITIVITY:
            for dim_key in cfg["dim_keys"]:
                funcs = suite_funcs(suite, dim_key, excluded=cfg["excluded_functions"])
                means = means_of(suite, dim_key)
                snapped = {a: {f: (0.0 if means[a][f] <= floor else means[a][f])
                               for f in funcs} for a in PANEL}
                var = friedman_with_id(snapped, funcs)["mean_ranks"]
                _rob_rank_rows(suite, f"floor_{floor:g}", dim_key,
                               fried[dim_key]["mean_ranks"], var,
                               f"success floor snapped at {floor:g}", rows, div)
    else:
        # ---- variant 2 (LSGO): relative vs absolute tie band ---------------
        for dim_key in cfg["dim_keys"]:
            funcs = suite_funcs(suite, dim_key, excluded=cfg["excluded_functions"])
            means = means_of(suite, dim_key)
            for comp in COMPARATORS:
                w1 = pw[(dim_key, comp)]["wtl"]
                w2 = wtl_means(means[PROPOSED], means[comp], funcs, relative_band=True)
                v = "agree" if w1 == w2 else "diverge"
                if v == "diverge":
                    div.append(f"relative_tie_band:wtl vs {comp} {w1}->{w2}")
                rows.append([suite, "relative_tie_band", dim_label(suite, dim_key),
                             "wtl", PROPOSED, comp, "-".join(map(str, w1)), NA,
                             "-".join(map(str, w2)), NA, v,
                             "relative band 1e-10*max(|a|,|b|,1) on the raw basis"])
        # ---- variant 3 (LSGO): leave-one-function-out Friedman -------------
        for dim_key in cfg["dim_keys"]:
            funcs = suite_funcs(suite, dim_key, excluded=cfg["excluded_functions"])
            means = means_of(suite, dim_key)
            prim = fried[dim_key]["mean_ranks"]
            po = ordinals(prim)
            for drop in funcs:
                kept = [f for f in funcs if f != drop]
                vr = friedman_with_id(means, kept)["mean_ranks"]
                vo = ordinals(vr)
                note = ("EXPLORATORY, inspection-informed deletion (addendum Sec.4)"
                        if drop in (7, 15) else "leave-one-function-out")
                for alg in PANEL:
                    v = "agree" if po[alg] == vo[alg] else "diverge"
                    if v == "diverge":
                        div.append(f"loo_F{drop}:{alg} ordinal {po[alg]}->{vo[alg]}")
                    rows.append([suite, f"loo_F{drop}", dim_label(suite, dim_key),
                                 "rank", alg, NA, F(prim[alg]), str(po[alg]),
                                 F(vr[alg]), str(vo[alg]), v, note])

    verdict = "agree" if not div else "diverge"
    digest.append("")
    digest.append(f"verdict: **{verdict}**")
    digest.append("")
    digest.append("divergences:")
    digest.extend(f"- {d}" for d in (div or ["none"]))
    if suite == "cec2013lsgo":
        digest.append("")
        digest.append("Tier: " + LSGO_TIER_DISCLOSURE)
    write_csv(OUT_ROOT / suite / "robustness" / f"robustness_{suite}.csv",
              ROB_HEADER, rows, [fam])
    write_text(OUT_ROOT / suite / "robustness" / f"robustness_{suite}_digest.md",
               "\n".join(digest), [fam])
    add_stat(analysis_id=fam, rq_id="RQ8", suite=suite, dimension="all",
             function_set="all registered", algorithms="panel-7",
             metric="robustness_battery", unit_of_analysis="check",
             pairing_key=NA, test="none (robustness; labels only)",
             n_observations=str(len(rows)),
             source_paths="see robustness CSV", source_checksums="see analysis_manifest.json",
             interpretation=f"verdict={verdict};divergences={len(div)};"
                            + tier_note(suite, "ROB"))


# ===========================================================================
# LSGO reproduction self-check (requirement: fail loudly on any digit)
# ===========================================================================
def selfcheck_lsgo(fried: dict, pw: dict, pwrun: dict) -> dict:
    """Reproduce Amendment 1 A1.3 exactly. Any difference is a DRIVER DEFECT."""
    fails: list[str] = []
    report: dict = {"authority": ("papers/build_prompt_phases/phase_05/"
                                  "statistical_analysis_plan_addendum_cec2020_lsgo"
                                  "_amendment_01.md Sections A1.1/A1.3"),
                    "rule": ("a digit-level difference is a DEFECT IN THIS DRIVER, "
                             "not a new result")}

    def cmp(label, got, want, tol):
        ok = got is not None and abs(float(got) - want) <= tol
        if not ok:
            fails.append(f"{label}: got {got!r}, pinned {want!r} (tol {tol})")
        return {"got": None if got is None else float(got), "pinned": want,
                "tol": tol, "ok": bool(ok)}

    res = fried["native"]
    report["omnibus"] = {
        "mean_ranks": {a: cmp(f"mean_rank[{a}]", res["mean_ranks"][a],
                              PINNED_LSGO["mean_ranks"][a], 5e-4) for a in PANEL},
        "chi2": cmp("chi2", res["chi2"], PINNED_LSGO["chi2"], 5e-4),
        "p_chi2": cmp("p_chi2", res["p_chi2"], PINNED_LSGO["p_chi2"], 5e-5),
        "f_id": cmp("iman_davenport_F", res["f_id"], PINNED_LSGO["f_id"], 5e-4),
        "p_id": cmp("p_iman_davenport", res["p_id"], PINNED_LSGO["p_id"], 5e-5),
    }

    layer1 = {}
    n_sig = 0
    for comp in COMPARATORS:
        r = pw[("native", comp)]
        layer1[comp] = {
            "p_exact": cmp(f"L1 p_exact[{comp}]", r["p_exact"],
                           PINNED_LSGO["layer1_p_exact"][comp], 5e-7),
            "p_normal": cmp(f"L1 p_normal[{comp}]", r["p_normal"],
                            PINNED_LSGO["layer1_p_normal"][comp], 5e-5),
            "p_holm": cmp(f"L1 p_holm[{comp}]", r["p_holm"],
                          PINNED_LSGO["layer1_p_holm"][comp], 5e-5),
            "outcome": r["outcome"],
        }
        if r["p_holm"] < ALPHA:
            n_sig += 1
    if n_sig != PINNED_LSGO["layer1_holm_significant"]:
        fails.append(f"L1 Holm-significant count: got {n_sig}, pinned "
                     f"{PINNED_LSGO['layer1_holm_significant']}")
    report["layer1_AN-PW-LSGO-NATIVE"] = layer1
    report["layer1_holm_significant"] = {"got": n_sig,
                                         "pinned": PINNED_LSGO["layer1_holm_significant"],
                                         "ok": n_sig == PINNED_LSGO["layer1_holm_significant"]}

    layer2 = {}
    funcs = LSGO_FUNCS
    for comp in COMPARATORS:
        wins = [f for f in funcs if pwrun[("native", f, comp)]["outcome"] == "win"]
        loss = [f for f in funcs if pwrun[("native", f, comp)]["outcome"] == "loss"]
        pw_, pl_ = PINNED_LSGO["layer2_wins_losses"][comp]
        ok_counts = (len(wins), len(loss)) == (pw_, pl_)
        ok_sets = (wins == PINNED_LSGO["layer2_win_functions"][comp]
                   and loss == PINNED_LSGO["layer2_loss_functions"][comp])
        if not ok_counts:
            fails.append(f"L2 counts[{comp}]: got {len(wins)}/{len(loss)}, pinned {pw_}/{pl_}")
        if not ok_sets:
            fails.append(f"L2 function sets[{comp}]: got won={wins} lost={loss}, "
                         f"pinned won={PINNED_LSGO['layer2_win_functions'][comp]} "
                         f"lost={PINNED_LSGO['layer2_loss_functions'][comp]}")
        layer2[comp] = {"wins": wins, "losses": loss,
                        "counts_got": [len(wins), len(loss)], "counts_pinned": [pw_, pl_],
                        "ok": bool(ok_counts and ok_sets)}
    report["layer2_AN-PWRUN-LSGO-NATIVE"] = layer2

    reg = {}
    for f in PINNED_LSGO["win_all_functions"]:
        got = [c for c in COMPARATORS if pwrun[("native", f, c)]["outcome"] == "win"]
        ok = len(got) == len(COMPARATORS)
        if not ok:
            fails.append(f"regularity: F{f} expected a Holm-significant dt-gsk WIN vs all "
                         f"six, got {got}")
        reg[f"F{f}_win_vs_all_six"] = {"got": got, "ok": bool(ok)}
    for f in PINNED_LSGO["lose_all_functions"]:
        got = [c for c in COMPARATORS if pwrun[("native", f, c)]["outcome"] == "loss"]
        ok = len(got) == len(COMPARATORS)
        if not ok:
            fails.append(f"regularity: F{f} expected a Holm-significant dt-gsk LOSS vs all "
                         f"six, got {got}")
        reg[f"F{f}_loss_vs_all_six"] = {"got": got, "ok": bool(ok)}
    report["cross_comparator_regularities"] = reg

    # Nemenyi power disclosure (addendum Section 7), k-parameterized.
    nem = {}
    for n_blocks, want in ADDENDUM_NEMENYI_CD.items():
        q, cd = nemenyi_cd(K_PANEL, n_blocks)
        delta = abs(cd - want)
        if delta <= CD_EXACT_TOL:
            verdict = "reproduces addendum Section 7"
        elif delta <= CD_TEXT_BAND:
            verdict = (
                f"TEXT DISCREPANCY (disclosed, not a driver defect): addendum "
                f"Section 7 records CD={want} for N={n_blocks}, which follows from "
                f"q=2.950; the tabulated two-tailed q_0.05(k={K_PANEL}) is {q} "
                f"(Demsar 2006 Table 5a), giving CD={cd:.6f}. The driver reports the "
                f"recomputed value and does not edit the pre-registration; quoting "
                f"{want} in the manuscript would need a dated amendment.")
            NOTES.append(f"AN-OMNI Nemenyi CD N={n_blocks}: addendum Section 7 says "
                         f"{want}, q_0.05(k={K_PANEL})={q} gives {cd:.6f} "
                         f"(last-digit text slip; disclosed, not corrected here)")
        else:
            verdict = "MISMATCH"
            fails.append(f"nemenyi CD k={K_PANEL} N={n_blocks}: got {cd}, "
                         f"addendum {want} (beyond a rounding discrepancy)")
        nem[f"N={n_blocks}"] = {"recomputed": cd, "addendum_section_7": want,
                                "q_alpha_005": q, "k": K_PANEL,
                                "abs_delta": delta, "verdict": verdict}
    report["nemenyi_power_disclosure"] = nem

    report["failures"] = fails
    report["status"] = "PASS" if not fails else "FAIL"
    write_json(OUT_ROOT / "cec2013lsgo" / "selfcheck_lsgo_pinned_values.json", report,
               analysis_ids=["SELFCHECK-LSGO"])
    add_stat(analysis_id="SELFCHECK-LSGO", rq_id=rq_of("cec2013lsgo"),
             suite="cec2013lsgo", dimension="native", function_set="F1-F15",
             algorithms="panel-7", metric="pinned_value_reproduction",
             unit_of_analysis="check", n_observations=str(len(fails) + 1),
             pairing_key=NA, test="none (self-check)",
             source_paths="Amendment 1 Section A1.3",
             source_checksums=sha256_of(
                 PHASE05 / "statistical_analysis_plan_addendum_cec2020_lsgo_amendment_01.md"),
             interpretation=f"status={report['status']};failures={len(fails)}",
             status="ok" if not fails else "DRIVER-DEFECT")
    if fails:
        detail = "\n".join(f"    - {f}" for f in fails)
        raise DriverDefect(
            "\nLSGO SELF-CHECK FAILED -- the driver does not reproduce the values "
            "recorded in Amendment 1 Section A1.3.\n"
            "A digit-level difference is a DEFECT IN THIS DRIVER, not a new result.\n"
            f"{detail}\n")
    return report


# ===========================================================================
# Bundle-level outputs
# ===========================================================================
def write_source_logs(suites: list[str]) -> None:
    audit = rl.get_source_audit()
    bad = [e for e in audit
           if not Path(e["path"]).resolve().is_relative_to(REF_ROOT.resolve())]
    if bad:
        raise RuntimeError(f"source audit contains non-release paths: {bad}")
    by_suite: dict[str, list] = {s: [] for s in suites}
    for entry in audit:
        rel = Path(entry["path"]).resolve().relative_to(REF_ROOT.resolve())
        if rel.parts[0] in by_suite:
            by_suite[rel.parts[0]].append(entry)
    for suite in suites:
        write_json(OUT_ROOT / suite / "source_use_log.json",
                   {"release": REL_ID, "anchor_commit": ANCHOR, "command": COMMAND,
                    "strict_source": True, "suite": suite, "status": "ok",
                    "n_opened": len(by_suite[suite]), "opened": by_suite[suite]},
                   analysis_ids=["SOURCE-LOG"])


def write_run_manifest(suites: list[str]) -> None:
    base = {
        "release_id": REL_ID, "anchor_commit": ANCHOR, "suites": suites,
        "script": SCRIPT_REL, "command": COMMAND, "git_head_at_run": GIT_HEAD,
        "preregistration": {
            "addendum": "papers/build_prompt_phases/phase_05/"
                        "statistical_analysis_plan_addendum_cec2020_lsgo.md",
            "amendment_01": "papers/build_prompt_phases/phase_05/"
                            "statistical_analysis_plan_addendum_cec2020_lsgo"
                            "_amendment_01.md",
            "signing_commit": "5c9bfae82",
        },
        "conventions": [
            "floats C-locale %.6e; integers plain; literal n/a for disclosed cells",
            "sort: suite, dimension asc, function asc, P1 algorithm order "
            "(gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk)",
            "no timestamps anywhere in the bundle (byte-reproducible)",
            "cec2013lsgo endpoint = best_fitness (raw basis; the error column is not "
            "populated on this suite); F13/F14 sit at their native D=905",
            "cec2020 endpoint = error with floor 1e-8; 38 protocol cells "
            "(F6/F7 undefined at D=5)",
            "per-function means/medians computed from per_run.csv (the inputs pinned "
            "by Amendment 1 A1.3), cross-checked against the promoted summary CSVs",
            "across-function Wilcoxon decision p = EXACT sign-flip enumeration over "
            "2^n patterns; the normal approximation (statistics.wilcoxon_paired) is "
            "recorded alongside; method recorded per row (SAP 6a)",
            "zeros |d| < 1e-8 discarded; n_eff reported after discard; n_eff < 6 -> "
            f"verbatim '{NOT_DECIDABLE}'",
            f"Nemenyi q_0.05 parameterized by k (k={K_PANEL} here, Demsar 2006 Table "
            "5a); CD emitted only when the omnibus is significant",
            "omnibus permutation companion (CEC2020 only): B=100000 within-block "
            "permutations, SeedSequence([20240620, 2020, dim, 0, 99]), fixed 5000-draw "
            "chunks, p=(1+ge)/(B+1); this p governs boundary disagreements",
            "BCa B=10000, SeedSequence([20240620, suite_ordinal, dimension, function, "
            "comparator_P1_index]); suite ordinals cec2020=2020, cec2013lsgo=2113",
            "F2 is NEVER excluded on either suite; every function list is built with "
            "an explicit exclusion argument (Amendment 1 A1.1 latent hazard)",
            "NO statistic pools suites (addendum Section 8, absolute)",
        ],
        "disclosures": {
            "cec2013lsgo_tier": LSGO_TIER_DISCLOSURE,
            "cec2013lsgo_objective": LSGO_ACKLEY_DISCLOSURE,
            "cec2020_rankagg_caption": RANKAGG_CAPTION,
            "power": ("k=7 Nemenyi CD is 3.185 (N=8), 2.849 (N=10), 2.327 (N=15): "
                      "these families are low-powered by construction; "
                      "non-significance is worded 'no separation demonstrated'"),
        },
        "notes": NOTES or "none",
    }
    write_json(OUT_ROOT / "run_manifest.json", base, analysis_ids=["RUN-MANIFEST"])


def write_statistical_results() -> None:
    comp_rank = {c: i for i, c in enumerate(PANEL)}
    suite_rank = {"cec2020": 0, "cec2013lsgo": 1}

    def _dim_key(v):
        try:
            return (0, int(v))
        except (TypeError, ValueError):
            return (1, 0)

    def _func_key(v):
        s = str(v)
        if s.startswith("F") and s[1:].isdigit():
            return (0, int(s[1:]))
        return (1, 0)

    def _alg_key(v):
        s = str(v)
        if s.startswith("dt-gsk vs "):
            return (1, comp_rank.get(s.split(" vs ")[1], 99))
        return (0, comp_rank.get(s, 99))

    STAT_ROWS.sort(key=lambda r: (
        suite_rank.get(r["suite"], 9), r["analysis_id"], _dim_key(r["dimension"]),
        _func_key(r["function_set"]), _alg_key(r["algorithms"]), r["metric"]))
    write_csv(OUT_ROOT / "primary_stats" / "statistical_results.csv", STAT_COLUMNS,
              [[r[c] for c in STAT_COLUMNS] for r in STAT_ROWS],
              ["ALL-ADDENDUM-FAMILIES"])


def write_manifest_and_checksums() -> None:
    p = assert_writable(OUT_ROOT / "analysis_checksums.sha256")
    p.write_text("\n".join(f"{e['sha256']}  {e['path']}" for e in MANIFEST_ENTRIES) + "\n",
                 encoding="utf-8")
    manifest = {"release_id": REL_ID, "anchor_commit": ANCHOR, "generator": SCRIPT_REL,
                "command": COMMAND, "git_head_at_run": GIT_HEAD,
                "output_root": _manifest_path(OUT_ROOT),
                "outputs": MANIFEST_ENTRIES}
    m = assert_writable(OUT_ROOT / "analysis_manifest.json")
    with open(m, "w", encoding="utf-8", newline="") as fh:
        json.dump(manifest, fh, indent=1)
        fh.write("\n")
    print(f"  wrote analysis_manifest.json ({len(MANIFEST_ENTRIES)} outputs) "
          f"+ analysis_checksums.sha256")


def clean_outputs(suites: list[str]) -> None:
    """No mixed-provenance output directory."""
    for suite in suites:
        d = OUT_ROOT / suite
        if d.exists():
            assert_writable(d)
            shutil.rmtree(d)
    for name in ("environment_record.json", "run_manifest.json",
                 "analysis_manifest.json", "analysis_checksums.sha256"):
        p = OUT_ROOT / name
        if p.exists():
            assert_writable(p)
            p.unlink()
    d = OUT_ROOT / "primary_stats"
    if d.exists():
        assert_writable(d)
        shutil.rmtree(d)


# ===========================================================================
# Release identity
# ===========================================================================
def resolve_release(suites: list[str]) -> tuple[str, str]:
    """Release id/anchor of the evidence body being analysed.

    Read from the minted manifest ``papers/governance/
    evidence_release_manifest_<suite>.json``; overridable per suite by env var.
    A missing manifest means the release was never minted -- refuse.
    """
    ids, anchors = [], []
    for suite in suites:
        cfg = SUITE_CFG[suite]
        env = os.environ.get(cfg["rel_env"], "").strip()
        mpath = GOV_DIR / cfg["manifest"]
        if env:
            rid, anc = env, os.environ.get("GSK_ANCHOR", "from-env")
        elif mpath.is_file():
            m = json.loads(mpath.read_text(encoding="utf-8"))
            rid, anc = m["release_id"], m["anchor_commit"]
            if suite not in m.get("release_scope", [suite]):
                raise SystemExit(f"{mpath.name}: release_scope does not cover {suite}")
            if m.get("supersedes_release") is not None:
                raise SystemExit(f"{mpath.name}: expected a non-superseding release")
        else:
            raise SystemExit(
                f"\nANALYSIS REFUSED -- {suite}: no evidence release manifest at "
                f"{_manifest_path(mpath)}.\n  The {suite} release has not been minted; "
                f"there is nothing admissible to analyse.\n")
        assert_release_id(rid)
        ids.append(rid)
        anchors.append(anc)
    if len(set(ids)) > 1:
        # Two separate, non-superseding releases: their bundles are separate too.
        raise SystemExit(
            "ANALYSIS REFUSED: the requested suites belong to different evidence "
            f"releases ({ids}); run the driver once per suite so each bundle carries "
            "exactly one release id (addendum Section 11: separate, non-superseding).")
    return ids[0], anchors[0]


# ===========================================================================
def run_suite(suite: str, negative: dict) -> None:
    print(f"\n[{suite}] readiness gate")
    banks = gate_suite_ready(suite)
    print("  banks ok: " + ", ".join(f"{a}={banks[a]['rows']}" for a in PANEL))

    print(f"[{suite}] source pre-check + pairing audit")
    step_precheck(suite, negative, banks)

    print(f"[{suite}] descriptives")
    family_descriptive(suite)
    print(f"[{suite}] AN-OMNI"
          + (" (+ AN-RANKAGG-2020-OVERALL)" if suite == "cec2020" else ""))
    fried = family_omnibus(suite)
    print(f"[{suite}] AN-PW")
    pw = family_pw(suite)
    print(f"[{suite}] AN-PWRUN")
    pwrun = family_pwrun(suite)
    print(f"[{suite}] AN-EFF")
    family_effect(suite)
    print(f"[{suite}] AN-ROB")
    family_robustness(suite, fried, pw)

    if suite == "cec2013lsgo":
        print(f"[{suite}] SELF-CHECK against Amendment 1 A1.3 pinned values")
        rep = selfcheck_lsgo(fried, pw, pwrun)
        SELFCHECK.update(rep)
        print("  self-check: PASS (all pinned values reproduced)")


def main() -> None:
    global OUT_ROOT, REL_ID, ANCHOR, COMMAND

    ap = argparse.ArgumentParser(
        description="Phase 6b analysis driver for CEC2020 and CEC2013LSGO "
                    "(pre-registered addendum families only).")
    ap.add_argument("--suite", required=True,
                    choices=["cec2020", "cec2013lsgo", "lsgo", "both"],
                    help="suite to analyse ('lsgo' is an alias for cec2013lsgo)")
    ap.add_argument("--out-root", default=None,
                    help="override the analysis bundle root (guard still active; "
                         "no 'rel-*' path is ever writable)")
    args = ap.parse_args()

    suites = (["cec2020", "cec2013lsgo"] if args.suite == "both"
              else ["cec2013lsgo" if args.suite == "lsgo" else args.suite])
    COMMAND = f"{COMMAND_BASE} --suite {args.suite}"

    print(f"Phase 6b analysis driver -- suites: {', '.join(suites)}")
    print("  [guard] F2-exclusion hazard (Amendment 1 A1.1)")
    hazard = assert_exclusion_hazard_defused()
    print(f"    {hazard['status']}")

    REL_ID, ANCHOR = resolve_release(suites)
    OUT_ROOT = (Path(args.out_root).resolve() if args.out_root
                else ANALYSIS_ROOT / REL_ID)
    assert_writable(OUT_ROOT)
    print(f"  release: {REL_ID} (anchor {ANCHOR[:9]})")
    print(f"  bundle : {_manifest_path(OUT_ROOT)}")

    clean_outputs(suites)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    print("  [guard] strict-source + write-guard negative tests")
    rl.clear_source_audit()
    negative = step_negative_tests()

    step_environment(suites, hazard)

    for suite in suites:
        run_suite(suite, negative)

    print("\n[bundle] statistical_results.csv / logs / manifests")
    write_statistical_results()
    write_source_logs(suites)
    write_run_manifest(suites)
    write_manifest_and_checksums()

    print("")
    print("PHASE 6B DRIVER COMPLETE")
    print(f"  release:          {REL_ID}")
    print(f"  suites:           {', '.join(suites)}")
    print(f"  output files:     {len(MANIFEST_ENTRIES)} (see analysis_manifest.json)")
    print(f"  statistical rows: {len(STAT_ROWS)} (primary_stats/statistical_results.csv)")
    print(f"  audited opens:    {len(rl.get_source_audit())} "
          f"(all under benchmarks/cec_reference_results/)")
    print(f"  lsgo self-check:  {SELFCHECK.get('status', 'not run')}")
    print(f"  notes:            {NOTES or 'none'}")


if __name__ == "__main__":
    main()
