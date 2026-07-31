#!/usr/bin/env python3
"""Phase 6 deterministic analysis driver (frozen-plan execution).

Executes the pre-registered Phase 5 statistical analysis plan against the
immutable evidence release ``rel-2026-07-10-262fc16c9`` in strict-source mode.

Binding pre-registration artifacts (read-only):
    papers/build_prompt_phases/phase_05/statistical_analysis_plan.md
    papers/build_prompt_phases/phase_05/analysis_registry.csv        (59 rows)
    papers/build_prompt_phases/phase_05/analysis_output_schemas/*.schema.md
    papers/build_prompt_phases/phase_05/strict_source_execution.md
    papers/build_prompt_phases/phase_05/curve_selection_rule.md
    papers/build_prompt_phases/phase_05/robustness_plan.md
    papers/build_prompt_phases/phase_05/source_resolution_map.csv

Empirical inputs come exclusively from benchmarks/cec_reference_results/
(strict-source guard active; results/ and results/_ablation are forbidden).
Outputs go to papers/analysis/rel-2026-07-10-262fc16c9/ plus the single
permitted staging export results/paper_tables/ (Phase 6 task 23).

Determinism contract (strict_source_execution.md Sec. 5): fixed sort orders,
C-locale ``%.6e`` floats, literal ``n/a`` for disclosed-unavailable cells, no
timestamps inside output CSVs, BCa B=10000 with
``default_rng(SeedSequence([20240620, suite_ordinal, dim, func, cmp_p1]))``.

Usage:
    python papers/scripts/phase6_run_analysis.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import locale
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy.stats as sps

SCRIPT_DIR = Path(__file__).resolve().parent
PAPER_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = PAPER_DIR.parent
_SRC = PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Deterministic locale before any formatting (strict_source_execution.md Sec. 5).
os.environ["LC_ALL"] = "C"
os.environ["LANG"] = "C"
# Strict-source activation #1 (env var); #2 (set_strict_source) applied in main().
os.environ["GSK_STRICT_SOURCE"] = "1"

from gsk_family.analysis import result_loader as rl  # noqa: E402
from gsk_family.analysis.statistics import (  # noqa: E402
    benjamini_hochberg,
    bootstrap_bca_ci,
    friedman_rank,
    holm_correction,
    wilcoxon_paired,
)

# ---------------------------------------------------------------------------
# Frozen constants
# ---------------------------------------------------------------------------
# Release identity is env-overridable so the driver can produce a NEW release
# bundle after an evidence regeneration; the frozen defaults reproduce the
# original rel-2026-07-10 run exactly.
REL_ID = os.environ.get("GSK_REL_ID", "rel-2026-07-16-78f075cb0")
ANCHOR = os.environ.get("GSK_ANCHOR", "78f075cb0f68a80010d524bdcc390a69a0afc5cd")
REF_ROOT = PROJECT_ROOT / "benchmarks" / "cec_reference_results"
OUT_ROOT = PAPER_DIR / "analysis" / REL_ID
PHASE05 = PAPER_DIR / "build_prompt_phases" / "phase_05"
PHASE03 = PAPER_DIR / "build_prompt_phases" / "phase_03"
PAPER_TABLES = PROJECT_ROOT / "results" / "paper_tables"
SCRIPT_REL = "papers/scripts/phase6_run_analysis.py"
COMMAND = "python papers/scripts/phase6_run_analysis.py"

PANEL = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk", "dt-gsk"]
COMPARATORS = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk"]
PROPOSED = "dt-gsk"
SUITE_ORDER = ["cec2017", "cec2013", "cec2011"]
SUITE_ORDINAL = {"cec2017": 2017, "cec2013": 2013, "cec2011": 2011}
SUITE_DIMS = {"cec2017": [10, 30, 50, 100], "cec2013": [10, 30, 50], "cec2011": [0]}
CEC2017_FUNCS = [1] + list(range(3, 31))
CEC2013_FUNCS = list(range(1, 29))
CEC2011_PROBS = list(range(1, 23))
SUITE_FUNCS = {"cec2017": CEC2017_FUNCS, "cec2013": CEC2013_FUNCS, "cec2011": CEC2011_PROBS}
SUITE_FSET = {"cec2017": "F1,F3-F30", "cec2013": "F1-F28", "cec2011": "P1-P22"}
N_RUNS = {"cec2017": 51, "cec2013": 51, "cec2011": 25}
TIE_TOL = 1e-8
ALPHA = 0.05
B_BOOT = 10000
BASE_SEED = 20240620
# Demsar (2006) Table 5(a) two-tailed Nemenyi critical value q_{0.05} for k=7.
NEMENYI_Q_005_K7 = 2.949
APGSK_DISPUTED_DIMS = (10, 30, 50)  # pre-registered r04 disputed-cell-exclusion dims
# (plan R3): a fixed analytical choice, NOT a data-presence gap. Anomaly A2-004 was
# resolved under CR-0006 (cec2017/apgsk per_run.csv restored to full D10/D30/D50/D100
# coverage); run-level cell availability is now decided dynamically by per_run_absent().
CATEGORIES = [
    ("unimodal", [1, 3]),
    ("simple_multimodal", list(range(4, 11))),
    ("hybrid", list(range(11, 21))),
    ("composition", list(range(21, 31))),
]
CAT_OF = {f: name for name, fs in CATEGORIES for f in fs}
NA = "n/a"

STAT_COLUMNS = [
    "analysis_id", "rq_id", "suite", "dimension", "function_set", "algorithms",
    "metric", "unit_of_analysis", "n_observations", "pairing_key", "test",
    "test_statistic", "p_raw", "p_adjusted", "correction", "effect_size",
    "effect_direction", "ci_low", "ci_high", "ci_level", "resampling_unit",
    "n_resamples", "seed", "source_paths", "source_checksums",
    "evidence_release_id", "script", "command", "commit_sha", "interpretation",
    "status",
]

STAT_ROWS: list[dict] = []
MANIFEST_ENTRIES: list[dict] = []
NOTES: list[str] = []
GIT_HEAD = "unknown"

_SHA_CACHE: dict[str, str] = {}
_SUMMARY_CACHE: dict = {}
_PER_RUN_CACHE: dict = {}
_NATIVE_DIMS: dict[int, int] = {}


# ---------------------------------------------------------------------------
# Formatting / IO helpers
# ---------------------------------------------------------------------------
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


def I(v) -> str:
    """Format an integer; None -> literal n/a."""
    if v is None:
        return NA
    return str(int(v))


def sha256_of(path: Path) -> str:
    key = str(path)
    if key not in _SHA_CACHE:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        _SHA_CACHE[key] = h.hexdigest()
    return _SHA_CACHE[key]


def rel_ref(path: Path) -> str:
    """Release-relative posix path of an evidence file."""
    return path.resolve().relative_to(REF_ROOT.resolve()).as_posix()


def write_csv(path: Path, header: list[str], rows: list[list[str]],
              analysis_ids: list[str], generator: str = SCRIPT_REL) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    MANIFEST_ENTRIES.append({
        "path": path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix(),
        "sha256": _fresh_sha(path),
        "generator": generator,
        "analysis_ids": analysis_ids,
    })
    print(f"  wrote {path.relative_to(PROJECT_ROOT)} ({len(rows)} rows)")


def _fresh_sha(path: Path) -> str:
    _SHA_CACHE.pop(str(path), None)
    return sha256_of(path)


def write_json(path: Path, obj, analysis_ids: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        json.dump(obj, fh, indent=1, sort_keys=False)
        fh.write("\n")
    if analysis_ids is not None:
        MANIFEST_ENTRIES.append({
            "path": path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix(),
            "sha256": _fresh_sha(path),
            "generator": SCRIPT_REL,
            "analysis_ids": analysis_ids,
        })
    print(f"  wrote {path.relative_to(PROJECT_ROOT)}")


def add_stat(**kw) -> None:
    row = {c: NA for c in STAT_COLUMNS}
    row["evidence_release_id"] = REL_ID
    row["script"] = SCRIPT_REL
    row["command"] = COMMAND
    row["commit_sha"] = GIT_HEAD
    row["status"] = "ok"
    row["ci_level"] = NA
    for k, v in kw.items():
        if k not in STAT_COLUMNS:
            raise KeyError(k)
        row[k] = v
    STAT_ROWS.append(row)


# ---------------------------------------------------------------------------
# Data access layer (audited)
# ---------------------------------------------------------------------------
def summary_path(suite: str, alg: str, dim: int) -> Path:
    if suite == "cec2011":
        return REF_ROOT / suite / alg / f"{alg}_cec2011.csv"
    return REF_ROOT / suite / alg / f"{alg}_{suite}_D{dim}.csv"


def load_summary(suite: str, alg: str, dim: int) -> dict[int, dict[str, float]]:
    key = (suite, alg, dim)
    if key not in _SUMMARY_CACHE:
        path = summary_path(suite, alg, dim)
        stats = rl.load_summary_csv(path)  # audited chokepoint (role=summary_csv)
        if not stats:
            raise RuntimeError(f"summary CSV missing/unreadable: {path}")
        _SUMMARY_CACHE[key] = {
            fid: {"best": fs.best, "median": fs.median, "mean": fs.mean,
                  "worst": fs.worst, "sd": fs.sd}
            for fid, fs in stats.items()
        }
    return _SUMMARY_CACHE[key]


def load_per_run(suite: str, alg: str) -> dict:
    key = (suite, alg)
    if key not in _PER_RUN_CACHE:
        path = REF_ROOT / suite / alg / "per_run.csv"
        rl.audit_source_open(path, role="per_run_csv")
        endpoint_col = "best_fitness" if suite == "cec2011" else "error"
        endpoint: dict = {}
        runtime: dict = {}
        with open(path, "r", encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                func = int(row["function"])
                dim = int(row["dimension"])
                run = int(row["run"])
                endpoint.setdefault((dim, func), {})[run] = float(row[endpoint_col])
                rt = row.get("runtime_seconds", "").strip()
                runtime.setdefault((dim, func), {})[run] = (
                    float(rt) if rt and rt.lower() != "nan" else None
                )
                if suite == "cec2011":
                    prev = _NATIVE_DIMS.setdefault(func, dim)
                    if prev != dim:
                        raise RuntimeError(
                            f"cec2011 native-dimension conflict for P{func}: {prev} vs {dim}")
        _PER_RUN_CACHE[key] = {"endpoint": endpoint, "runtime": runtime,
                               "path": rel_ref(path)}
    return _PER_RUN_CACHE[key]


def endpoint_runs(suite: str, alg: str, dim: int, func: int) -> np.ndarray | None:
    """Per-run endpoint values ordered by run index; None when absent."""
    pr = load_per_run(suite, alg)
    if suite == "cec2011":
        dim = _NATIVE_DIMS[func]
    cell = pr["endpoint"].get((dim, func))
    if not cell:
        return None
    runs = sorted(cell)
    return np.array([cell[r] for r in runs], dtype=np.float64)


def paired_runs(suite: str, comp: str, dim: int, func: int):
    """(ism, comp) endpoint vectors paired by run index; None when unavailable."""
    x = endpoint_runs(suite, PROPOSED, dim, func)
    y = endpoint_runs(suite, comp, dim, func)
    if x is None or y is None or len(x) != len(y):
        return None
    return x, y


_SESSION_WINDOW_H = 72.0


def runtime_session_split(suite: str = "cec2017") -> str:
    """Panel cells measured outside one session window, as a short label.

    RT-001. Returns "" when the panel is coherent, otherwise a compact
    description of the outliers (e.g. ``dt-gsk +9.7d``). Only wall-clock
    comparisons are affected: every other reported quantity is reproducible from
    the frozen seeds and is indifferent to when a cell was measured.

    Mirrors papers/scripts/validate_runtime_provenance.py, which is the
    standalone gate; this inline copy exists so the analysis driver never emits a
    comparability claim it cannot support, even if the gate is not run.
    """
    stamps: dict[str, datetime] = {}
    for alg in PANEL:
        env = REF_ROOT / suite / alg / "environment.json"
        if not env.is_file():
            continue
        try:
            ts = json.loads(env.read_text(encoding="utf-8")).get("timestamp", "")
            stamps[alg] = datetime.fromisoformat(ts)
        except (ValueError, OSError):
            continue
    if len(stamps) < 2:
        return ""
    ordered = sorted(stamps.values())
    median = ordered[len(ordered) // 2]
    out = []
    for alg, t in stamps.items():
        gap_h = (t - median).total_seconds() / 3600.0
        if abs(gap_h) > _SESSION_WINDOW_H:
            out.append(f"{alg} {gap_h / 24:+.1f}d")
    return ", ".join(sorted(out))


def per_run_absent(suite: str, alg: str, dim: int) -> bool:
    """True iff the release carries no per-run endpoint rows for (suite, alg, dim).

    Dynamic replacement (CR-0006) for the former static APGSK_GAP_DIMS skip list:
    anomaly A2-004 is resolved, so cec2017/apgsk now has per-run rows at every
    dimension and this returns False there (the run-level cells are computed from
    the recovered per_run.csv). Any genuinely absent (suite, alg, dim) still
    returns True, preserving the disclosed-unavailable path. cec2011 keys its
    endpoints by native dimension, so presence is judged by the optimizer's
    per-run file carrying any rows (mirrors endpoint_runs' native-dim handling).
    """
    pr = load_per_run(suite, alg)
    if suite == "cec2011":
        return len(pr["endpoint"]) == 0
    return not any(d == dim for (d, _f) in pr["endpoint"])


def load_checkpoints(suite: str, alg: str, func: int, dim: int):
    path = REF_ROOT / suite / alg / "gen_logs" / f"CheckpointErrors_{alg}_F{func}_D{dim}.csv"
    if not path.is_file():
        return None
    rl.audit_source_open(path, role="checkpoint_log")
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    header = rows[0]
    cps = [int(c[1:]) for c in header[2:]]
    mat = np.array(
        [[float(v) if v.strip() != "" else np.nan for v in r[2:]] for r in rows[1:]],
        dtype=np.float64,
    )
    return cps, mat


# ---------------------------------------------------------------------------
# Statistical helpers (SAP-conformant; repo library reused where definitions match)
# ---------------------------------------------------------------------------
def _midranks(values: np.ndarray) -> np.ndarray:
    """Average-rank midranks (1-based) of values ascending, exact-value ties."""
    return sps.rankdata(values, method="average")


def rank_row(values: list[float]) -> np.ndarray:
    """Per-function panel ranks (1 = best), exact-value ties -> average rank."""
    return _midranks(np.asarray(values, dtype=np.float64))


def signed_rank_sums(d: np.ndarray):
    """(w_plus, w_minus, n) over nonzero diffs with midrank ties (repo convention)."""
    n = len(d)
    if n == 0:
        return 0.0, 0.0, 0
    ranks = _midranks(np.abs(d))
    w_plus = float(np.sum(ranks[d > 0]))
    w_minus = float(np.sum(ranks[d < 0]))
    return w_plus, w_minus, n


def wilcoxon_two_sided(x: np.ndarray, y: np.ndarray) -> dict:
    """Two-sided Wilcoxon signed-rank, SAP tie rule |d|<1e-8 -> zero (discarded).

    p-value from the repo tool of record
    (gsk_family.analysis.statistics.wilcoxon_paired: normal approximation with
    continuity correction; the method used is recorded per test).
    """
    d_all = x - y
    nz = np.abs(d_all) >= TIE_TOL
    n_zero = int(np.sum(~nz))
    xf, yf = x[nz], y[nz]
    res = wilcoxon_paired(xf, yf)
    d = xf - yf
    w_plus, w_minus, n = signed_rank_sums(d)
    if n == 0:
        direction = "none"
    elif w_minus > w_plus:
        direction = "favors_dt-gsk"   # negative diffs = ism error lower
    elif w_plus > w_minus:
        direction = "favors_comparator"
    else:
        direction = "none"
    # Matched-pairs rank-biserial, ORIENTED so that r > 0 favours dt-gsk.
    #
    # The differences are ERRORS (lower is better), so d = dt-gsk - comparator
    # is negative when dt-gsk wins and w_minus carries its advantage. The
    # textbook form (w_plus - w_minus)/(w_plus + w_minus) would therefore be
    # NEGATIVE for a dt-gsk win -- printing r = -0.865 beside "22 wins, Dec = +"
    # reads as a defect whatever the caption says. Negating aligns the sign with
    # the `direction` field in this same record and with the A12 > 0.5 convention
    # it replaces in Table 8. Magnitude is unchanged.
    rb = None if n == 0 else (w_minus - w_plus) / (w_plus + w_minus)
    return {
        "statistic": float(res.statistic), "p": float(res.p_value),
        "n_nonzero": n, "n_zero": n_zero, "w_plus": w_plus, "w_minus": w_minus,
        "direction": direction, "rank_biserial": rb,
        "method": "normal_approx_continuity(statistics.wilcoxon_paired)",
    }


def a12_band(x: np.ndarray, y: np.ndarray):
    """Vargha-Delaney A12 with the SAP Sec.7 tie band |d|<1e-8 counted half.

    A12 > 0.5 means x (dt-gsk) achieves strictly lower error more often.
    """
    diff = y[None, :] - x[:, None]
    ties = np.abs(diff) < TIE_TOL
    wins = (diff > 0) & ~ties
    a12 = (float(np.sum(wins)) + 0.5 * float(np.sum(ties))) / (len(x) * len(y))
    dlt = 2.0 * a12 - 1.0
    m = abs(a12 - 0.5)
    if m < 0.06:
        mag = "negligible"
    elif m < 0.14:
        mag = "small"
    elif m < 0.21:
        mag = "medium"
    else:
        mag = "large"
    return a12, dlt, mag


def wtl_means(mean_ism: dict, mean_comp: dict, funcs: list[int]):
    """W/T/L on per-function means, SAP tie rule |delta| < 1e-8 (pure, no rel band)."""
    w = t = lo = 0
    for f in funcs:
        d = mean_ism[f] - mean_comp[f]
        if abs(d) < TIE_TOL:
            t += 1
        elif d < 0:
            w += 1
        else:
            lo += 1
    return w, t, lo


def friedman_with_id(data: dict[str, list[float]]) -> dict:
    """Repo Friedman (tool of record) + Iman-Davenport F correction (decision).

    M-026: the REPORTED statistic is now tie-corrected. The 1e-8 success floor
    creates genuine exact ties (9 of 29 functions at CEC2017 D10), which shrink
    the rank variance and bias the uncorrected chi2 downwards. Since the
    correction divides by C <= 1 it can only increase significance, and it
    leaves mean ranks untouched -- so no rank, sign, or decision can flip as a
    result of adopting it (audit: 0 flips across all 8 published panels).

    ``f_id`` / ``p_id`` are therefore derived from the CORRECTED chi2. The
    uncorrected forms are retained under explicit ``*_uncorrected`` keys so the
    published historical values stay reproducible and auditable.
    """
    fr = friedman_rank(data)
    n, k = fr.n_problems, fr.n_algorithms

    def iman_davenport(chi2: float) -> tuple[float | None, float]:
        denom = n * (k - 1) - chi2
        if denom <= 1e-12:
            return None, 0.0
        f = (n - 1) * chi2 / denom
        return f, float(sps.f.sf(f, k - 1, (k - 1) * (n - 1)))

    chi2_unc = float(fr.statistic)
    chi2_cor = float(fr.statistic_tie_corrected)
    p_chi2_cor = float(fr.p_value_tie_corrected)
    # A fully-tied panel yields nan; fall back to the uncorrected pair rather
    # than propagating nan into a decision column. Both must fall back together.
    if not np.isfinite(chi2_cor):
        chi2_cor, p_chi2_cor = chi2_unc, float(fr.p_value)

    f_unc, p_unc = iman_davenport(chi2_unc)
    f_cor, p_cor = iman_davenport(chi2_cor)

    return {"mean_ranks": dict(fr.avg_ranks),
            # reported (tie-corrected)
            "chi2": chi2_cor, "p_chi2": p_chi2_cor,
            "f_id": f_cor, "p_id": p_cor,
            # audit companions (historical, tie-uncorrected)
            "chi2_uncorrected": chi2_unc, "p_chi2_uncorrected": float(fr.p_value),
            "f_id_uncorrected": f_unc, "p_id_uncorrected": p_unc,
            "tie_correction": float(fr.tie_correction),
            "n_tied_problems": int(fr.n_tied_problems),
            "n": n, "k": k}


def ordinals(mean_ranks: dict[str, float]) -> dict[str, int]:
    """Ordinal positions 1..k (ties share the smallest position)."""
    return {a: 1 + sum(1 for b in mean_ranks.values() if b < r - 1e-12)
            for a, r in mean_ranks.items()}


# ===========================================================================
# Step a: environment record
# ===========================================================================
def step_environment() -> None:
    global GIT_HEAD
    try:
        GIT_HEAD = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(PROJECT_ROOT),
            capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        GIT_HEAD = "unavailable"
    rel_manifest = json.loads(
        (PAPER_DIR / "governance" / "evidence_release_manifest.json").read_text(encoding="utf-8"))
    if rel_manifest["release_id"] != REL_ID or rel_manifest["anchor_commit"] != ANCHOR:
        raise RuntimeError("evidence_release_manifest.json does not match the frozen release id/anchor")
    freeze = json.loads((PHASE03 / "algorithm_freeze_manifest.json").read_text(encoding="utf-8"))
    try:
        import importlib.metadata as im
        mpl_ver = im.version("matplotlib")
    except Exception:
        mpl_ver = "not-installed"
    record = {
        "release_id": REL_ID,
        "anchor_commit": ANCHOR,
        "git_head_at_run": GIT_HEAD,
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": {"numpy": np.__version__,
                     "scipy": __import__("scipy").__version__,
                     "pandas": __import__("pandas").__version__,
                     "matplotlib": mpl_ver},
        "locale": {"LC_ALL": os.environ.get("LC_ALL"), "LANG": os.environ.get("LANG"),
                   "python_locale": list(locale.getlocale())},
        "thread_env": {k: os.environ.get(k) for k in (
            "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")},
        "pythonioencoding": os.environ.get("PYTHONIOENCODING"),
        "strict_source": {"env_GSK_STRICT_SOURCE": os.environ.get("GSK_STRICT_SOURCE"),
                          "programmatic_set_strict_source": True},
        "algorithm_freeze_hashes": freeze.get("frozen_core_sources"),
        "rng_policy": ("BCa: default_rng(SeedSequence([20240620, suite_ordinal, dimension, "
                       "function, comparator_P1_index])), B=10000; no other stochastic step"),
        "cwd": str(Path.cwd()),
        "argv": sys.argv,
    }
    write_json(OUT_ROOT / "environment_record.json", record, analysis_ids=["ENVIRONMENT"])


# ===========================================================================
# Step b: strict-source activation + negative tests
# ===========================================================================
def step_negative_tests() -> dict:
    rl.set_strict_source(True)
    results = {}
    probes = [
        ("results/_run_all path via audit_source_open",
         lambda: rl.audit_source_open(
             PROJECT_ROOT / "results" / "_run_all" / "dt-gsk" / "cec2017" / "summary" /
             "dt-gsk_cec2017_D10.csv", role="summary_csv")),
        ("results/_ablation path via audit_source_open",
         lambda: rl.audit_source_open(
             PROJECT_ROOT / "results" / "_ablation" / "baseline" / "dt-gsk" / "cec2017" /
             "summary" / "per_run.csv", role="per_run_csv")),
        ("load_reproduced() staging resolver",
         lambda: rl.load_reproduced("dt-gsk", "CEC2017", 10)),
    ]
    for name, fn in probes:
        try:
            fn()
        except rl.StrictSourceViolation:
            results[name] = "PASS (StrictSourceViolation raised)"
        else:
            results[name] = "FAIL (no StrictSourceViolation)"
    if any(v.startswith("FAIL") for v in results.values()):
        raise RuntimeError(f"strict-source negative test failed: {results}")
    audit_len = len(rl.get_source_audit())
    if audit_len != 0:
        raise RuntimeError("negative tests polluted the source audit log")
    print("  negative tests:", results)
    return results


# ===========================================================================
# Step c: source completeness pre-check
# ===========================================================================
def step_precheck_summaries(negative_tests: dict) -> dict:
    expected_funcs = {"cec2017": 29, "cec2013": 28, "cec2011": 22}
    summary_check = {}
    failures = []
    for suite in SUITE_ORDER:
        for alg in PANEL:
            for dim in SUITE_DIMS[suite]:
                stats = load_summary(suite, alg, dim)
                got = len(stats)
                want = expected_funcs[suite]
                ok = (got == want) and all(
                    stats[f]["mean"] is not None for f in SUITE_FUNCS[suite])
                label = f"{suite}/{alg}" + ("" if suite == "cec2011" else f"/D{dim}")
                summary_check[label] = {"functions": got, "expected": want,
                                        "status": "ok" if ok else "MISMATCH"}
                if not ok:
                    failures.append(label)
    pre = {"release_id": REL_ID, "anchor_commit": ANCHOR,
           "negative_tests": negative_tests,
           "summary_csv_check": summary_check, "summary_failures": failures}
    if failures:
        write_json(OUT_ROOT / "source_precheck.json", pre, analysis_ids=["PRECHECK"])
        raise RuntimeError(f"source pre-check failed for {failures}")
    return pre


def step_precheck_per_run(pre: dict) -> None:
    expected_rows = {
        # CR-0006: cec2017/apgsk per_run recovered to full coverage (5916 rows);
        # every optimizer now carries all four dimensions (A2-004 resolved).
        "cec2017": {alg: 5916 for alg in PANEL},
        "cec2013": {alg: 4284 for alg in PANEL},
        "cec2011": {alg: 550 for alg in PANEL},
    }
    per_run_check = {}
    failures = []
    for suite in SUITE_ORDER:
        for alg in PANEL:
            pr = load_per_run(suite, alg)
            got = sum(len(v) for v in pr["endpoint"].values())
            want = expected_rows[suite][alg]
            ok = got == want
            per_run_check[f"{suite}/{alg}"] = {
                "rows": got, "expected": want, "status": "ok" if ok else "MISMATCH"}
            if not ok:
                failures.append(f"{suite}/{alg}")
    pre["per_run_check"] = per_run_check
    pre["per_run_failures"] = failures
    pre["apgsk_cec2017_disposition"] = (
        "A2-004 RESOLVED under CR-0006 (2026-07-11): cec2017/apgsk per_run.csv restored "
        "to full D10/D30/D50/D100 coverage (validated deterministic reconstruction that "
        "reproduces the frozen apgsk summaries exactly, scripts/recover_apgsk_perrun.py); "
        "run-level quantities vs apgsk at CEC2017 D10/D30/D50 (Wilcoxon/A12/Cliff/BCa) are "
        "now computed from the recovered per_run.csv, no longer disclosed-unavailable")
    write_json(OUT_ROOT / "source_precheck.json", pre, analysis_ids=["PRECHECK"])
    if failures:
        raise RuntimeError(f"per_run pre-check failed for {failures}")


# ===========================================================================
# Step d: curve selection (BLIND; summary CSVs only; before any gen_log open)
# ===========================================================================
def step_curve_selection() -> dict:
    header = ["suite", "dimension", "function", "category", "difficulty_tercile",
              "dtgsk_standing", "selection_reason", "selected_for_main"]
    reserved = PHASE05 / "curve_selection.csv"
    existing_header = reserved.read_text(encoding="utf-8").strip().splitlines()[0]
    if existing_header.strip() != ",".join(header):
        raise RuntimeError("reserved curve_selection.csv header mismatch")

    priority = [("hard", "weak"), ("hard", "comparable"), ("moderate", "comparable"),
                ("easy", "strong"), ("hard", "strong"), ("moderate", "weak"),
                ("moderate", "strong"), ("easy", "weak"), ("easy", "comparable")]

    info: dict[int, dict[int, dict]] = {}
    selected: dict[int, dict[str, int]] = {}
    reasons: dict[tuple[int, int], str] = {}

    for dim in (30, 100):
        means = {alg: load_summary("cec2017", alg, dim) for alg in PANEL}
        strata: dict[int, dict] = {}
        score = {}
        for f in CEC2017_FUNCS:
            vals = [means[alg][f]["mean"] for alg in PANEL]
            score[f] = float(np.median(np.asarray(vals, dtype=np.float64)))
        order = sorted(CEC2017_FUNCS, key=lambda f: (score[f], f))
        terc = {}
        for pos, f in enumerate(order, start=1):
            terc[f] = "easy" if pos <= 10 else ("moderate" if pos <= 20 else "hard")
        for f in CEC2017_FUNCS:
            vals = np.asarray([means[alg][f]["mean"] for alg in PANEL], dtype=np.float64)
            ranks = _midranks(vals)
            r_ism = float(ranks[PANEL.index(PROPOSED)])
            standing = "strong" if r_ism <= 2 else ("comparable" if r_ism <= 5 else "weak")
            strata[f] = {"category": CAT_OF[f], "difficulty_tercile": terc[f],
                         "dtgsk_standing": standing}
        info[dim] = strata

        sel: dict[str, int] = {}
        for k, (tc, st) in enumerate(priority, start=1):
            for f in CEC2017_FUNCS:
                s = strata[f]
                if s["difficulty_tercile"] == tc and s["dtgsk_standing"] == st:
                    c = s["category"]
                    if c not in sel:
                        sel[c] = f
                        reasons[(dim, f)] = f"priority_{k}_({tc},{st})"
        if len(sel) != 4:
            raise RuntimeError(f"curve selection did not fill all 4 categories at D{dim}")
        selected[dim] = sel

    def _joint_flags():
        hard = weak = False
        for dim in (30, 100):
            for f in selected[dim].values():
                s = info[dim][f]
                hard = hard or s["difficulty_tercile"] == "hard"
                weak = weak or s["dtgsk_standing"] == "weak"
        return hard, weak

    repaired_slots: set[tuple[int, str]] = set()
    has_hard, has_weak = _joint_flags()

    def _replace(dim: int, f: int, tag: str):
        c = info[dim][f]["category"]
        old = selected[dim][c]
        reasons.pop((dim, old), None)
        selected[dim][c] = f
        reasons[(dim, f)] = tag
        repaired_slots.add((dim, c))

    if not has_hard and not has_weak:
        cands = [(dim, f) for dim in (30, 100) for f in CEC2017_FUNCS
                 if info[dim][f]["difficulty_tercile"] == "hard"
                 and info[dim][f]["dtgsk_standing"] == "weak"
                 and f not in selected[dim].values()]
        cands.sort(key=lambda t: (t[0], t[1]))
        if cands:
            _replace(cands[0][0], cands[0][1], "constraint_repair_joint")
            has_hard, has_weak = _joint_flags()
    if not has_hard:
        pr = {"weak": 0, "comparable": 1, "strong": 2}
        cands = [(pr[info[dim][f]["dtgsk_standing"]], dim, f)
                 for dim in (30, 100) for f in CEC2017_FUNCS
                 if info[dim][f]["difficulty_tercile"] == "hard"
                 and f not in selected[dim].values()]
        cands.sort()
        if cands:
            _replace(cands[0][1], cands[0][2], "constraint_repair_hard")
            has_hard, has_weak = _joint_flags()
    if not has_weak:
        pr = {"hard": 0, "moderate": 1, "easy": 2}
        cands = [(pr[info[dim][f]["difficulty_tercile"]], dim, f)
                 for dim in (30, 100) for f in CEC2017_FUNCS
                 if info[dim][f]["dtgsk_standing"] == "weak"
                 and f not in selected[dim].values()]
        cands.sort()
        placed = False
        for _, dim, f in cands:
            c = info[dim][f]["category"]
            if (dim, c) in repaired_slots:
                continue  # must not displace a step-2 slot
            _replace(dim, f, "constraint_repair_weak")
            placed = True
            break
        if not placed:
            NOTES.append(
                "curve selection: joint DT-GSK-weak constraint genuinely unsatisfiable "
                "(no weak function under the pre-registered standing definition at "
                "D30/D100); disclosed per curve_selection_rule.md Sec. 5.6 step 4")
        has_hard, has_weak = _joint_flags()

    joint = {"has_hard": has_hard, "has_weak": has_weak,
             "repairs": sorted(v for v in reasons.values() if v.startswith("constraint"))}

    all_rows = []
    for dim in (30, 100):
        for f in CEC2017_FUNCS:
            s = info[dim][f]
            sel = f in selected[dim].values()
            reason = reasons.get((dim, f), "not_selected") if sel else "not_selected"
            all_rows.append(["cec2017", str(dim), str(f), s["category"],
                             s["difficulty_tercile"], s["dtgsk_standing"],
                             reason, "TRUE" if sel else "FALSE"])
    n_true = sum(1 for r in all_rows if r[7] == "TRUE")
    if len(all_rows) != 58 or n_true != 8:
        raise RuntimeError(f"curve selection row contract violated: {len(all_rows)} rows, {n_true} TRUE")

    with open(reserved, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(all_rows)
    MANIFEST_ENTRIES.append({
        "path": reserved.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix(),
        "sha256": _fresh_sha(reserved), "generator": SCRIPT_REL,
        "analysis_ids": ["AN-CONV-2017-D30", "AN-CONV-2017-D100"]})
    print(f"  filled {reserved.relative_to(PROJECT_ROOT)} (58 rows, 8 selected)")

    for dim in (30, 100):
        rows = [r for r in all_rows if r[1] == str(dim)]
        write_csv(OUT_ROOT / "cec2017" / f"curve_selection_cec2017_D{dim}.csv",
                  header, rows, [f"AN-CONV-2017-D{dim}"])
    sel_summary = {str(d): dict(sorted(selected[d].items())) for d in (30, 100)}
    print(f"  selected panels: {sel_summary}; joint={joint}")
    return {"selected": sel_summary, "joint_constraint": joint}


# ===========================================================================
# Primary families
# ===========================================================================
MEANS: dict = {}
MEDIANS: dict = {}
FRIED: dict = {}
OVERALL: dict = {}
PW: dict = {}
PWRUN: dict = {}
WTL: dict = {}
A12S: dict = {}
BCAS: dict = {}
BH_DEC: dict = {}
GRID_MISMATCHES: list[str] = []


def _summary_sources(suite: str, dim: int):
    paths = [summary_path(suite, alg, dim) for alg in PANEL]
    return (";".join(rel_ref(p) for p in paths),
            ";".join(sha256_of(p) for p in paths))


def _per_run_sources(suite: str, comp: str):
    p1 = REF_ROOT / suite / PROPOSED / "per_run.csv"
    p2 = REF_ROOT / suite / comp / "per_run.csv"
    return (f"{rel_ref(p1)};{rel_ref(p2)}",
            f"{sha256_of(p1)};{sha256_of(p2)}")


def _rq_secondary(suite: str) -> str:
    return "RQ6" if suite in ("cec2013", "cec2011") else ""


def family_descriptive(suite: str) -> None:
    """descriptive_stats_* transcription + (cec2017) W/T/L + success rates."""
    metric_name = "error" if suite != "cec2011" else "best_fitness"
    for dim in SUITE_DIMS[suite]:
        rows = []
        for f in SUITE_FUNCS[suite]:
            out_dim = _NATIVE_DIMS[f] if suite == "cec2011" else dim
            for alg in PANEL:
                s = load_summary(suite, alg, dim)[f]
                rows.append([suite, str(out_dim), str(f), alg, F(s["best"]),
                             F(s["median"]), F(s["mean"]), F(s["worst"]), F(s["sd"]),
                             rel_ref(summary_path(suite, alg, dim))])
        name = (f"descriptive_stats_{suite}_D{dim}.csv" if suite != "cec2011"
                else "descriptive_stats_cec2011.csv")
        fam = f"AN-DESC-2017-D{dim}" if suite == "cec2017" else None
        ids = [fam] if fam else []
        write_csv(OUT_ROOT / suite / name,
                  ["suite", "dimension", "function", "algorithm", "best", "median",
                   "mean", "worst", "sd", "source_path"], rows, ids or ["DESC-TRANSCRIPTION"])

        means = {alg: {f: load_summary(suite, alg, dim)[f]["mean"] for f in SUITE_FUNCS[suite]}
                 for alg in PANEL}
        MEANS[(suite, dim)] = means
        MEDIANS[(suite, dim)] = {
            alg: {f: load_summary(suite, alg, dim)[f]["median"] for f in SUITE_FUNCS[suite]}
            for alg in PANEL}
        sp, sc = _summary_sources(suite, dim)

        for comp in COMPARATORS:
            w, t, lo = wtl_means(means[PROPOSED], means[comp], SUITE_FUNCS[suite])
            WTL[(suite, dim, comp)] = (w, t, lo)
            if fam:
                add_stat(analysis_id=fam, rq_id="RQ1", suite=suite, dimension=str(dim),
                         function_set=SUITE_FSET[suite],
                         algorithms=f"dt-gsk vs {comp}",
                         metric=f"win_tie_loss_per_function_mean_{metric_name}",
                         unit_of_analysis="function", n_observations=str(len(SUITE_FUNCS[suite])),
                         pairing_key="function_identity", test="none (descriptive)",
                         effect_direction=("favors_dt-gsk" if w > lo else
                                           ("favors_comparator" if lo > w else "none")),
                         source_paths=sp, source_checksums=sc,
                         interpretation=f"W={w};T={t};L={lo};tie_rule=|delta|<1e-8")
        if fam:
            add_stat(analysis_id=fam, rq_id="RQ1", suite=suite, dimension=str(dim),
                     function_set=SUITE_FSET[suite], algorithms="panel-7",
                     metric="five_statistic_descriptives",
                     unit_of_analysis="(function,algorithm) cell",
                     n_observations=str(len(SUITE_FUNCS[suite]) * 7),
                     pairing_key=NA, test="none (descriptive)",
                     source_paths=sp, source_checksums=sc,
                     interpretation="release summary transcription (best/median/mean/worst/sd)")
            # success rates vs the 1e-8 protocol target (per-run-derived)
            for alg in PANEL:
                if per_run_absent(suite, alg, dim):
                    add_stat(analysis_id=fam, rq_id="RQ1", suite=suite, dimension=str(dim),
                             function_set=SUITE_FSET[suite], algorithms=alg,
                             metric="success_rate_protocol_1e-8",
                             unit_of_analysis="run", pairing_key=NA,
                             test="none (descriptive)",
                             source_paths=sp, source_checksums=sc,
                             interpretation="per-run evidence absent from release (anomaly A2-004)",
                             status="disclosed-unavailable")
                    continue
                total = succ = 0
                for f in SUITE_FUNCS[suite]:
                    v = endpoint_runs(suite, alg, dim, f)
                    if v is None:
                        continue
                    total += len(v)
                    succ += int(np.sum(v <= TIE_TOL))
                prp = load_per_run(suite, alg)["path"]
                add_stat(analysis_id=fam, rq_id="RQ1", suite=suite, dimension=str(dim),
                         function_set=SUITE_FSET[suite], algorithms=alg,
                         metric="success_rate_protocol_1e-8",
                         unit_of_analysis="run", n_observations=str(total),
                         pairing_key=NA, test="none (descriptive)",
                         effect_size=F(succ / total if total else None),
                         source_paths=prp,
                         source_checksums=sha256_of(REF_ROOT / prp),
                         interpretation=f"successes={succ}/{total} (error<=1e-8)")


def family_omnibus(suite: str) -> None:
    dims = SUITE_DIMS[suite]
    for dim in dims:
        funcs = SUITE_FUNCS[suite]
        means = MEANS[(suite, dim)]
        data = {alg: [means[alg][f] for f in funcs] for alg in PANEL}
        res = friedman_with_id(data)
        FRIED[(suite, dim)] = res
        sp, sc = _summary_sources(suite, dim)
        fam = (f"AN-OMNI-2017-D{dim}" if suite == "cec2017" else
               (f"AN-OMNI-2013-D{dim}" if suite == "cec2013" else "AN-OMNI-2011-NATIVE"))
        rq = "RQ1" if suite == "cec2017" else "RQ6"
        name = (f"friedman_ranks_{suite}_D{dim}.csv" if suite != "cec2011"
                else "friedman_ranks_cec2011.csv")
        # M-026: reported columns are tie-corrected; the historical uncorrected
        # forms and the correction factor are appended so the published values
        # stay reproducible and a reader can verify the correction independently.
        rows = [[suite, str(dim), str(res["n"]), alg, F(res["mean_ranks"][alg]),
                 F(res["chi2"]), F(res["f_id"]), F(res["p_id"]),
                 F(res["tie_correction"]), str(res["n_tied_problems"]),
                 F(res["chi2_uncorrected"]), F(res["f_id_uncorrected"]),
                 F(res["p_id_uncorrected"])] for alg in PANEL]
        write_csv(OUT_ROOT / suite / name,
                  ["suite", "dimension", "n_blocks", "algorithm", "mean_rank",
                   "friedman_chi2", "iman_davenport_F", "p_value",
                   "tie_correction_C", "n_tied_functions",
                   "friedman_chi2_uncorrected", "iman_davenport_F_uncorrected",
                   "p_value_uncorrected"], rows, [fam])
        add_stat(analysis_id=fam, rq_id=rq, suite=suite, dimension=str(dim),
                 function_set=SUITE_FSET[suite], algorithms="panel-7",
                 metric="friedman_chi2", unit_of_analysis="function",
                 n_observations=str(res["n"]), pairing_key="function_identity",
                 test="friedman", test_statistic=F(res["chi2"]), p_raw=F(res["p_chi2"]),
                 correction="tie-corrected rank variance (single omnibus per family)",
                 source_paths=sp, source_checksums=sc,
                 interpretation=(
                     "chi-square approximation (statistics.friedman_rank), "
                     f"tie-corrected: C={res['tie_correction']:.6f} over "
                     f"{res['n_tied_problems']} tied function(s); "
                     f"uncorrected chi2={res['chi2_uncorrected']:.4f}"))
        add_stat(analysis_id=fam, rq_id=rq, suite=suite, dimension=str(dim),
                 function_set=SUITE_FSET[suite], algorithms="panel-7",
                 metric="iman_davenport_F", unit_of_analysis="function",
                 n_observations=str(res["n"]), pairing_key="function_identity",
                 test="iman_davenport", test_statistic=F(res["f_id"]), p_raw=F(res["p_id"]),
                 correction="tie-corrected chi2 (omnibus decision criterion, alpha=0.05)",
                 source_paths=sp, source_checksums=sc,
                 interpretation=(
                     ("significant" if res["p_id"] < ALPHA else "not significant")
                     + "; same decision uncorrected ("
                     + ("significant" if res["p_id_uncorrected"] < ALPHA
                        else "not significant")
                     + f", F={res['f_id_uncorrected']:.4f})"))
        for alg in PANEL:
            add_stat(analysis_id=fam, rq_id=rq, suite=suite, dimension=str(dim),
                     function_set=SUITE_FSET[suite], algorithms=alg,
                     metric="friedman_mean_rank", unit_of_analysis="function",
                     n_observations=str(res["n"]), pairing_key="function_identity",
                     test="none (rank point value)", effect_size=F(res["mean_ranks"][alg]),
                     source_paths=sp, source_checksums=sc,
                     interpretation="lower rank = better")
        # Conditional Nemenyi CD companion
        if res["p_id"] < ALPHA:
            cd = NEMENYI_Q_005_K7 * float(np.sqrt(7 * 8 / (6.0 * res["n"])))
            nname = (f"nemenyi_cd_{suite}_D{dim}.csv" if suite != "cec2011"
                     else "nemenyi_cd_cec2011.csv")
            nrows = [[suite, str(dim), str(res["n"]), "7", F(NEMENYI_Q_005_K7), F(cd),
                      alg, F(res["mean_ranks"][alg])] for alg in PANEL]
            write_csv(OUT_ROOT / suite / nname,
                      ["suite", "dimension", "n_blocks", "k", "q_alpha_005",
                       "critical_difference", "algorithm", "mean_rank"], nrows, [fam])
            add_stat(analysis_id=fam, rq_id=rq, suite=suite, dimension=str(dim),
                     function_set=SUITE_FSET[suite], algorithms="panel-7",
                     metric="nemenyi_critical_difference", unit_of_analysis="function",
                     n_observations=str(res["n"]), pairing_key="function_identity",
                     test="nemenyi_cd", test_statistic=F(cd),
                     correction="Nemenyi (q_0.05, k=7, Demsar 2006 Table 5a)",
                     source_paths=sp, source_checksums=sc,
                     interpretation="CD diagram inputs emitted (omnibus significant)")
        else:
            add_stat(analysis_id=fam, rq_id=rq, suite=suite, dimension=str(dim),
                     function_set=SUITE_FSET[suite], algorithms="panel-7",
                     metric="nemenyi_critical_difference", unit_of_analysis="function",
                     n_observations=str(res["n"]), pairing_key="function_identity",
                     test="nemenyi_cd",
                     source_paths=sp, source_checksums=sc,
                     interpretation="omnibus not significant; CD diagram omitted by pre-registration",
                     status="omitted-not-significant")

    if suite in ("cec2017", "cec2013"):
        fam = "AN-RANKAGG-2017-OVERALL" if suite == "cec2017" else "AN-RANKAGG-2013-OVERALL"
        overall = {alg: float(np.mean([FRIED[(suite, d)]["mean_ranks"][alg] for d in dims]))
                   for alg in PANEL}
        OVERALL[suite] = overall
        rows = [[suite, alg, F(overall[alg])] for alg in PANEL]
        write_csv(OUT_ROOT / suite / f"friedman_ranks_{suite}_overall.csv",
                  ["suite", "algorithm", "mean_rank"], rows, [fam])
        sp = ";".join(_summary_sources(suite, d)[0] for d in dims)
        sc = ";".join(_summary_sources(suite, d)[1] for d in dims)
        for alg in PANEL:
            add_stat(analysis_id=fam, rq_id="RQ1" if suite == "cec2017" else "RQ6",
                     suite=suite, dimension="overall", function_set=SUITE_FSET[suite],
                     algorithms=alg, metric="mean_of_per_dimension_friedman_mean_ranks",
                     unit_of_analysis="dimension", n_observations=str(len(dims)),
                     pairing_key=NA, test="none (descriptive aggregation; no test attached)",
                     effect_size=F(overall[alg]), source_paths=sp, source_checksums=sc,
                     interpretation="descriptive aggregation of per-dimension ranks; no test attached")
    else:
        OVERALL[suite] = dict(FRIED[(suite, 0)]["mean_ranks"])


def family_pw(suite: str) -> None:
    """Across-function function-level Wilcoxon + Holm (m=6)."""
    # M-027: release the PAIRED effect size (matched-pairs rank-biserial) and the
    # signed rank sums it derives from. Without these columns the primary table
    # foregrounds the UNPAIRED A12 as the effect size for a paired test, and the
    # supplement's claim that r is "reported alongside R+/R- in the released
    # per-comparison workbooks" is unsupported by the release.
    header = ["suite", "dimension", "function", "comparator", "test_level", "n_pairs",
              "statistic", "p_raw", "p_holm", "outcome", "availability",
              "rank_biserial", "w_plus", "w_minus", "n_zero", "direction"]
    for dim in SUITE_DIMS[suite]:
        funcs = SUITE_FUNCS[suite]
        means = MEANS[(suite, dim)]
        x = np.array([means[PROPOSED][f] for f in funcs], dtype=np.float64)
        results = {}
        for comp in COMPARATORS:
            y = np.array([means[comp][f] for f in funcs], dtype=np.float64)
            results[comp] = wilcoxon_two_sided(x, y)
        holm = holm_correction([results[c]["p"] for c in COMPARATORS], list(COMPARATORS),
                               alpha=ALPHA)
        p_holm = {str(c["label"]): float(c["p_adjusted"]) for c in holm.comparisons}
        rows = []
        sp, sc = _summary_sources(suite, dim)
        fam = (f"AN-PW-2017-D{dim}" if suite == "cec2017" else
               (f"AN-PW-2013-D{dim}" if suite == "cec2013" else "AN-PW-2011-NATIVE"))
        rq = "RQ2" if suite == "cec2017" else "RQ6"
        for comp in COMPARATORS:
            r = results[comp]
            sig = p_holm[comp] < ALPHA
            outcome = ("win" if (sig and r["direction"] == "favors_dt-gsk") else
                       ("loss" if (sig and r["direction"] == "favors_comparator") else "tie"))
            PW[(suite, dim, comp)] = {"p_raw": r["p"], "p_holm": p_holm[comp],
                                      "outcome": outcome, "statistic": r["statistic"],
                                      "direction": r["direction"],
                                      "rank_biserial": r["rank_biserial"],
                                      "w_plus": r["w_plus"], "w_minus": r["w_minus"],
                                      "n_zero": r["n_zero"]}
            rows.append([suite, str(dim), "0", comp, "across_functions_funclevel",
                         str(len(funcs)), F(r["statistic"]), F(r["p"]),
                         F(p_holm[comp]), outcome, "ok",
                         F(r["rank_biserial"]), F(r["w_plus"]), F(r["w_minus"]),
                         str(r["n_zero"]), r["direction"]])
            run_level_absent = per_run_absent(suite, comp, dim)
            add_stat(analysis_id=fam, rq_id=rq, suite=suite, dimension=str(dim),
                     function_set=SUITE_FSET[suite], algorithms=f"dt-gsk vs {comp}",
                     metric="wilcoxon_signed_rank_across_functions_on_means",
                     unit_of_analysis="function", n_observations=str(len(funcs)),
                     pairing_key="function_identity",
                     test="wilcoxon_signed_rank_two_sided",
                     test_statistic=F(r["statistic"]), p_raw=F(r["p"]),
                     p_adjusted=F(p_holm[comp]), correction="holm_m6",
                     # M-027: the paired effect size is ALWAYS emitted here. It was
                     # previously suppressed whenever run-level data existed, on the
                     # grounds that AN-EFF "carries" the effect -- but AN-EFF carries
                     # A12, which is UNPAIRED. Deferring a paired test's effect size
                     # to an unpaired statistic from another family is what left the
                     # primary table reporting A12 for a Wilcoxon signed-rank result.
                     effect_size=F(r["rank_biserial"]),
                     effect_direction=r["direction"],
                     ci_low=NA, ci_high=NA,
                     source_paths=sp, source_checksums=sc,
                     interpretation=(f"outcome={outcome};n_zero_discarded={r['n_zero']};"
                                     f"method={r['method']}"
                                     ";effect=matched-pairs rank-biserial r=(R+ - R-)/(R+ + R-)"
                                     f" from w_plus={r['w_plus']:.1f},w_minus={r['w_minus']:.1f};"
                                     "uncertainty interval DISCLOSED-UNAVAILABLE"
                                     + ("" if run_level_absent
                                        else ";unpaired A12 companion in AN-EFF family")))
        name = (f"wilcoxon_holm_{suite}_D{dim}.csv" if suite != "cec2011"
                else "wilcoxon_holm_cec2011.csv")
        write_csv(OUT_ROOT / suite / name, header, rows, [fam])


def family_pwrun(suite: str) -> None:
    """Per-function run-level Wilcoxon + Holm (across functions per comparator)."""
    header = ["suite", "dimension", "function", "comparator", "test_level", "n_pairs",
              "statistic", "p_raw", "p_holm", "outcome", "availability"]
    for dim in SUITE_DIMS[suite]:
        funcs = SUITE_FUNCS[suite]
        fam = (f"AN-PWRUN-2017-D{dim}" if suite == "cec2017" else
               (f"AN-PWRUN-2013-D{dim}" if suite == "cec2013" else "AN-PWRUN-2011-NATIVE"))
        rq = "RQ2" if suite == "cec2017" else "RQ6"
        cell: dict = {}
        for comp in COMPARATORS:
            if per_run_absent(suite, comp, dim):
                for f in funcs:
                    cell[(f, comp)] = None
                continue
            praw, labels = [], []
            per_func = {}
            for f in funcs:
                pair = paired_runs(suite, comp, dim, f)
                if pair is None:
                    raise RuntimeError(f"missing per-run pair {suite} D{dim} F{f} {comp}")
                r = wilcoxon_two_sided(pair[0], pair[1])
                per_func[f] = r
                praw.append(r["p"])
                labels.append(str(f))
            holm = holm_correction(praw, labels, alpha=ALPHA)
            adj = {str(c["label"]): float(c["p_adjusted"]) for c in holm.comparisons}
            for f in funcs:
                r = per_func[f]
                sig = adj[str(f)] < ALPHA
                outcome = ("win" if (sig and r["direction"] == "favors_dt-gsk") else
                           ("loss" if (sig and r["direction"] == "favors_comparator") else "tie"))
                cell[(f, comp)] = {"p_raw": r["p"], "p_holm": adj[str(f)],
                                   "outcome": outcome, "statistic": r["statistic"],
                                   "direction": r["direction"], "n_zero": r["n_zero"],
                                   "n_pairs": N_RUNS[suite]}
        PWRUN[(suite, dim)] = cell
        rows = []
        for f in funcs:
            out_dim = _NATIVE_DIMS[f] if suite == "cec2011" else dim
            for comp in COMPARATORS:
                r = cell[(f, comp)]
                if r is None:
                    rows.append([suite, str(out_dim), str(f), comp, "per_function_runlevel",
                                 NA, NA, NA, NA, NA, "disclosed-unavailable"])
                    add_stat(analysis_id=fam, rq_id=rq, suite=suite, dimension=str(dim),
                             function_set=f"F{f}", algorithms=f"dt-gsk vs {comp}",
                             metric="wilcoxon_signed_rank_runlevel",
                             unit_of_analysis="run", pairing_key="get_cec_seed(20240620,dim,func,run)",
                             test="wilcoxon_signed_rank_two_sided",
                             correction=f"holm_m{len(funcs)}",
                             source_paths=NA, source_checksums=NA,
                             interpretation="per-run evidence absent from release (anomaly A2-004)",
                             status="disclosed-unavailable")
                    continue
                rows.append([suite, str(out_dim), str(f), comp, "per_function_runlevel",
                             str(r["n_pairs"]), F(r["statistic"]), F(r["p_raw"]),
                             F(r["p_holm"]), r["outcome"], "ok"])
                sp, sc = _per_run_sources(suite, comp)
                add_stat(analysis_id=fam, rq_id=rq, suite=suite, dimension=str(dim),
                         function_set=f"F{f}", algorithms=f"dt-gsk vs {comp}",
                         metric="wilcoxon_signed_rank_runlevel",
                         unit_of_analysis="run", n_observations=str(r["n_pairs"]),
                         pairing_key="get_cec_seed(20240620,dim,func,run)",
                         test="wilcoxon_signed_rank_two_sided",
                         test_statistic=F(r["statistic"]), p_raw=F(r["p_raw"]),
                         p_adjusted=F(r["p_holm"]), correction=f"holm_m{len(funcs)}",
                         effect_direction=r["direction"],
                         source_paths=sp, source_checksums=sc,
                         interpretation=f"outcome={r['outcome']};n_zero_discarded={r['n_zero']}")
        name = (f"wilcoxon_run_{suite}_D{dim}.csv" if suite != "cec2011"
                else "wilcoxon_run_cec2011.csv")
        write_csv(OUT_ROOT / suite / name, header, rows, [fam])


def family_effect(suite: str) -> None:
    """A12/Cliff's delta + BCa 95% CI on paired mean differences."""
    eff_header = ["suite", "dimension", "function", "comparator", "n_runs", "a12",
                  "cliffs_delta", "magnitude", "availability"]
    bca_header = ["suite", "dimension", "function", "comparator", "n_runs", "mean_diff",
                  "ci_low", "ci_high", "B", "seed_scheme", "availability"]
    seed_lit = "SS[20240620,suite,dim,func,cmpP1]"
    ordinal = SUITE_ORDINAL[suite]
    for dim in SUITE_DIMS[suite]:
        funcs = SUITE_FUNCS[suite]
        fam = (f"AN-EFF-2017-D{dim}" if suite == "cec2017" else
               (f"AN-EFF-2013-D{dim}" if suite == "cec2013" else "AN-EFF-2011-NATIVE"))
        rq = "RQ3" if suite == "cec2017" else "RQ6"
        eff_rows, bca_rows = [], []
        for f in funcs:
            out_dim = _NATIVE_DIMS[f] if suite == "cec2011" else dim
            seed_dim = out_dim if suite == "cec2011" else dim
            for ci_idx, comp in enumerate(COMPARATORS):
                if per_run_absent(suite, comp, dim):
                    eff_rows.append([suite, str(out_dim), str(f), comp, NA, NA, NA, NA,
                                     "disclosed-unavailable"])
                    bca_rows.append([suite, str(out_dim), str(f), comp, NA, NA, NA, NA,
                                     NA, NA, "disclosed-unavailable"])
                    for metric in ("vargha_delaney_a12", "bca_ci_paired_mean_diff"):
                        add_stat(analysis_id=fam, rq_id=rq, suite=suite, dimension=str(dim),
                                 function_set=f"F{f}", algorithms=f"dt-gsk vs {comp}",
                                 metric=metric, unit_of_analysis="run",
                                 pairing_key="get_cec_seed(20240620,dim,func,run)",
                                 test="none (estimation)",
                                 source_paths=NA, source_checksums=NA,
                                 interpretation="per-run evidence absent from release (anomaly A2-004)",
                                 status="disclosed-unavailable")
                    continue
                x, y = paired_runs(suite, comp, dim, f)
                a12, dlt, mag = a12_band(x, y)
                A12S[(suite, dim, f, comp)] = a12
                eff_rows.append([suite, str(out_dim), str(f), comp, str(len(x)),
                                 F(a12), F(dlt), mag, "ok"])
                sp, sc = _per_run_sources(suite, comp)
                add_stat(analysis_id=fam, rq_id=rq, suite=suite, dimension=str(dim),
                         function_set=f"F{f}", algorithms=f"dt-gsk vs {comp}",
                         metric="vargha_delaney_a12", unit_of_analysis="run",
                         n_observations=str(len(x)),
                         pairing_key="get_cec_seed(20240620,dim,func,run)",
                         test="none (estimation)", effect_size=F(a12),
                         effect_direction=("favors_dt-gsk" if a12 > 0.5 else
                                           ("favors_comparator" if a12 < 0.5 else "none")),
                         source_paths=sp, source_checksums=sc,
                         interpretation=f"cliffs_delta={F(dlt)};magnitude={mag};"
                                        "A12>0.5 favors dt-gsk;ties |d|<1e-8 counted half")
                d = x - y
                mean_diff = float(np.mean(d))
                seed_list = [BASE_SEED, ordinal, seed_dim, f, ci_idx]
                if bool(np.all(d == d[0])):
                    lo = hi = None
                    avail = "no CI (degenerate cell)"
                    interp = "no CI (degenerate cell): all paired differences identical"
                else:
                    rng = np.random.default_rng(np.random.SeedSequence(seed_list))
                    lo, hi, _theta = bootstrap_bca_ci(d, n_boot=B_BOOT, alpha=ALPHA, rng=rng)
                    avail = "ok"
                    interp = "BCa 95% CI on paired mean difference (negative favors dt-gsk)"
                BCAS[(suite, dim, f, comp)] = {"mean_diff": mean_diff, "lo": lo, "hi": hi,
                                               "n": len(x), "seed": seed_list}
                bca_rows.append([suite, str(out_dim), str(f), comp, str(len(x)),
                                 F(mean_diff), F(lo), F(hi),
                                 str(B_BOOT) if avail == "ok" else NA,
                                 seed_lit if avail == "ok" else NA, avail])
                add_stat(analysis_id=fam, rq_id=rq, suite=suite, dimension=str(dim),
                         function_set=f"F{f}", algorithms=f"dt-gsk vs {comp}",
                         metric="bca_ci_paired_mean_diff", unit_of_analysis="run",
                         n_observations=str(len(x)),
                         pairing_key="get_cec_seed(20240620,dim,func,run)",
                         test="none (estimation)", effect_size=F(mean_diff),
                         effect_direction=("favors_dt-gsk" if mean_diff < 0 else
                                           ("favors_comparator" if mean_diff > 0 else "none")),
                         ci_low=F(lo), ci_high=F(hi), ci_level="0.95",
                         resampling_unit="paired runs within function",
                         n_resamples=str(B_BOOT) if avail == "ok" else NA,
                         seed="SeedSequence(" + json.dumps(seed_list) + ")" if avail == "ok" else NA,
                         source_paths=sp, source_checksums=sc,
                         interpretation=interp)
        ename = (f"effect_sizes_{suite}_D{dim}.csv" if suite != "cec2011"
                 else "effect_sizes_cec2011.csv")
        bname = (f"bca_ci_{suite}_D{dim}.csv" if suite != "cec2011"
                 else "bca_ci_cec2011.csv")
        write_csv(OUT_ROOT / suite / ename, eff_header, eff_rows, [fam])
        write_csv(OUT_ROOT / suite / bname, bca_header, bca_rows, [fam])


def family_convergence(suite: str, dims: list[int]) -> None:
    header = ["suite", "dimension", "function", "algorithm", "checkpoint_nfes",
              "mean_error", "n_runs", "availability"]
    for dim in dims:
        funcs = SUITE_FUNCS[suite]
        fam = (f"AN-CONV-2017-D{dim}" if suite == "cec2017" else
               ("AN-CONV-2013-D30" if suite == "cec2013" else "AN-CONV-2011-NATIVE"))
        rows = []
        n_expected = N_RUNS[suite]
        grid_identical = True
        missing: list[str] = []
        for f in funcs:
            d_native = _NATIVE_DIMS[f] if suite == "cec2011" else dim
            loaded = {}
            for alg in PANEL:
                got = load_checkpoints(suite, alg, f, d_native)
                if got is None:
                    missing.append(f"{alg}/F{f}/D{d_native}")
                    continue
                loaded[alg] = got
            grids = [tuple(v[0]) for v in loaded.values()]
            common = sorted(set(grids[0]).intersection(*[set(g) for g in grids[1:]]))
            if any(tuple(common) != g for g in grids):
                grid_identical = False
                GRID_MISMATCHES.append(f"{suite}/F{f}/D{d_native}")
            for alg in PANEL:
                if alg not in loaded:
                    continue
                cps, mat = loaded[alg]
                col = {cp: i for i, cp in enumerate(cps)}
                for cp in common:
                    vals = mat[:, col[cp]]
                    ok_mask = ~np.isnan(vals)
                    n_ok = int(np.sum(ok_mask))
                    mean_v = float(np.mean(vals[ok_mask]))
                    avail = "ok" if n_ok == n_expected else "disclosed-missing"
                    rows.append([suite, str(d_native), str(f), alg, str(cp),
                                 F(mean_v), str(n_ok), avail])
        name = (f"convergence_checkpoints_{suite}_D{dim}.csv" if suite != "cec2011"
                else "convergence_checkpoints_cec2011.csv")
        write_csv(OUT_ROOT / suite / name, header, rows, [fam])
        add_stat(analysis_id=fam, rq_id="RQ5", suite=suite,
                 dimension=str(dim) if suite != "cec2011" else "native",
                 function_set=SUITE_FSET[suite], algorithms="panel-7",
                 metric="per_checkpoint_mean_error_across_runs",
                 unit_of_analysis="(function,algorithm,checkpoint)",
                 n_observations=str(len(rows)), pairing_key="get_cec_seed shared schedule",
                 test="none (descriptive)",
                 source_paths=f"{suite}/{{alg}}/gen_logs/CheckpointErrors_*.csv",
                 source_checksums="see analysis_manifest.json / evidence_release_manifest.json",
                 interpretation=(f"grid_identical={grid_identical};missing_logs={len(missing)};"
                                 "no smoothing;no extrapolation"))
        if missing:
            NOTES.append(f"convergence {suite} D{dim}: missing logs disclosed: {missing}")


def family_trend_class_cost() -> None:
    # --- rank trend (AN-TREND-2017) -------------------------------------
    rows = []
    for dim in SUITE_DIMS["cec2017"]:
        mr = FRIED[("cec2017", dim)]["mean_ranks"]
        o = ordinals(mr)
        for alg in PANEL:
            rows.append(["cec2017", str(dim), alg, F(mr[alg]), str(o[alg])])
    write_csv(OUT_ROOT / "cec2017" / "rank_trend_cec2017.csv",
              ["suite", "dimension", "algorithm", "mean_rank", "ordinal_position"],
              rows, ["AN-TREND-2017"])
    add_stat(analysis_id="AN-TREND-2017", rq_id="RQ4", suite="cec2017",
             dimension="10;30;50;100", function_set=SUITE_FSET["cec2017"],
             algorithms="panel-7", metric="friedman_mean_rank_vs_dimension_trend",
             unit_of_analysis="dimension", n_observations="4",
             pairing_key=NA, test="none (descriptive; no extrapolation beyond D100)",
             source_paths="via AN-OMNI-2017-* ranks (no independent recomputation)",
             source_checksums="see friedman_ranks_cec2017_D*.csv",
             interpretation="descriptive trend rows in rank_trend_cec2017.csv")

    # --- class ranks (AN-CLASS-2017, exploratory) ------------------------
    rows = []
    for dim in SUITE_DIMS["cec2017"]:
        means = MEANS[("cec2017", dim)]
        ranks_by_func = {
            f: rank_row([means[alg][f] for alg in PANEL]) for f in CEC2017_FUNCS}
        sp, sc = _summary_sources("cec2017", dim)
        for cat, cat_funcs in CATEGORIES:
            cf = [f for f in cat_funcs if f in CEC2017_FUNCS]
            for ai, alg in enumerate(PANEL):
                mrank = float(np.mean([ranks_by_func[f][ai] for f in cf]))
                if alg == PROPOSED:
                    wtl_cells = (NA, NA, NA)
                else:
                    w, t, lo = wtl_means(means[PROPOSED], means[alg], cf)
                    wtl_cells = (str(w), str(t), str(lo))
                rows.append(["cec2017", str(dim), cat, str(len(cf)), alg, F(mrank),
                             wtl_cells[0], wtl_cells[1], wtl_cells[2]])
                add_stat(analysis_id="AN-CLASS-2017", rq_id="RQ4", suite="cec2017",
                         dimension=str(dim), function_set=cat, algorithms=alg,
                         metric="per_class_mean_rank", unit_of_analysis="function",
                         n_observations=str(len(cf)), pairing_key="function_identity",
                         test="none (exploratory descriptive; no per-class inference)",
                         effect_size=F(mrank), source_paths=sp, source_checksums=sc,
                         interpretation=("exploratory; W/T/L vs dt-gsk="
                                         + "/".join(wtl_cells)))
    write_csv(OUT_ROOT / "cec2017" / "class_ranks_cec2017.csv",
              ["suite", "dimension", "category", "n_functions", "algorithm",
               "mean_rank", "ism_wins", "ism_ties", "ism_losses"],
              rows, ["AN-CLASS-2017"])

    # --- cost (AN-COST-2017; descriptive; comparability-qualified) --------
    # RT-001. Runtime is the only reported quantity that is a property of the
    # machine and build rather than of the algorithm, so it is the only one that
    # can be invalidated by *when* a cell was measured. The values below are
    # always regenerated from the promoted evidence -- a derived artifact must
    # not silently disagree with its source -- but when the panel was not
    # measured as one session the comparability column says so, which is the
    # lever downstream table builds and reviewers actually read.
    split = runtime_session_split()
    rows = []
    comp_note = {
        "egsk": "provenance-qualified (SciPy-SLSQP Python port; comparability_audit.md Sec.4; "
                "no runtime-superiority claim)",
    }
    for suite in SUITE_ORDER:
        for dim in SUITE_DIMS[suite]:
            for alg in PANEL:
                if per_run_absent(suite, alg, dim):
                    rows.append([suite, str(dim), alg, NA, NA, NA, NA,
                                 "disclosed-unavailable"])
                    add_stat(analysis_id="AN-COST-2017", rq_id="RQ7", suite=suite,
                             dimension=str(dim), function_set=SUITE_FSET[suite],
                             algorithms=alg, metric="runtime_seconds_mean_sd",
                             unit_of_analysis="run", pairing_key=NA,
                             test="none (descriptive)", source_paths=NA, source_checksums=NA,
                             interpretation="per-run runtime absent (anomaly A2-004; gen_logs carry no runtime)",
                             status="disclosed-unavailable")
                    continue
                pr = load_per_run(suite, alg)
                vals = []
                for f in SUITE_FUNCS[suite]:
                    d = _NATIVE_DIMS[f] if suite == "cec2011" else dim
                    cell = pr["runtime"].get((d, f), {})
                    vals.extend(v for v in cell.values() if v is not None)
                arr = np.asarray(vals, dtype=np.float64)
                if split:
                    comp_status = (
                        "NOT-COMPARABLE-ACROSS-ALGORITHMS (RT-001: panel not measured "
                        f"as one session; outliers: {split}); cell value is accurate "
                        "for this algorithm alone")
                else:
                    comp_status = comp_note.get(
                        alg, "comparable-within-python-panel (comparability_audit.md Sec.1)")
                rows.append([suite, str(dim), alg, str(len(arr)), F(float(np.mean(arr))),
                             F(float(np.std(arr, ddof=1))), comp_status, "ok"])
                add_stat(analysis_id="AN-COST-2017", rq_id="RQ7", suite=suite,
                         dimension=str(dim), function_set=SUITE_FSET[suite],
                         algorithms=alg, metric="runtime_seconds_mean_sd",
                         unit_of_analysis="run", n_observations=str(len(arr)),
                         pairing_key=NA, test="none (descriptive)",
                         effect_size=F(float(np.mean(arr))),
                         source_paths=pr["path"],
                         source_checksums=sha256_of(REF_ROOT / pr["path"]),
                         interpretation=(f"sd={F(float(np.std(arr, ddof=1)))};"
                                         f"comparability={comp_status};no superiority claim"))
    write_csv(OUT_ROOT / "cec2017" / "cost_cec2017.csv",
              ["suite", "dimension", "algorithm", "n_runs", "mean_runtime_seconds",
               "sd_runtime_seconds", "comparability", "availability"],
              rows, ["AN-COST-2017"])


def family_global_holm_sensitivity() -> None:
    """AN-GHOLM-2017: what the 24-cell tally becomes under GLOBAL Holm control.

    M-028. The published decisions apply Holm within each dimension (family size
    6), so the 24-cell tally aggregates four independent families and is
    descriptive rather than family-wise controlled across dimensions. That is now
    stated wherever the tally appears -- but stating a limitation is weaker than
    quantifying it, so this family re-runs Holm over all 24 hypotheses at once and
    reports which cells would not survive.

    Nothing here restates a published decision: the within-dimension results
    remain the reported ones. This is a sensitivity companion, computed from the
    same p_raw values, and it needs no rerun.
    """
    cells = [(dim, comp, PW[("cec2017", dim, comp)])
             for dim in SUITE_DIMS["cec2017"] for comp in COMPARATORS]
    labels = [f"D{dim}:{comp}" for dim, comp, _ in cells]
    holm = holm_correction([c[2]["p_raw"] for c in cells], labels, alpha=ALPHA)
    p_global = {str(c["label"]): float(c["p_adjusted"]) for c in holm.comparisons}

    rows, n_within, n_global, n_lost = [], 0, 0, 0
    for (dim, comp, r), label in zip(cells, labels):
        pg = p_global[label]
        sig_within = r["p_holm"] < ALPHA
        sig_global = pg < ALPHA
        n_within += int(sig_within)
        n_global += int(sig_global)
        survives = "yes" if sig_global else ("no" if sig_within else "n/a")
        if sig_within and not sig_global:
            n_lost += 1
        outcome_global = ("win" if (sig_global and r["direction"] == "favors_dt-gsk")
                          else ("loss" if (sig_global and r["direction"] == "favors_comparator")
                                else "tie"))
        rows.append(["cec2017", str(dim), "0", comp, "across_functions_funclevel",
                     F(r["p_raw"]), F(r["p_holm"]), F(pg), r["outcome"],
                     outcome_global, survives, "ok"])
        sp, sc = _summary_sources("cec2017", dim)
        add_stat(analysis_id="AN-GHOLM-2017", rq_id="RQ2", suite="cec2017",
                 dimension=str(dim), function_set=SUITE_FSET["cec2017"],
                 algorithms=f"dt-gsk vs {comp}",
                 metric="wilcoxon_signed_rank_across_functions_global_holm",
                 unit_of_analysis="function",
                 n_observations=str(len(SUITE_FUNCS["cec2017"])),
                 pairing_key="function_identity",
                 test="wilcoxon_signed_rank_two_sided",
                 test_statistic=F(r["statistic"]), p_raw=F(r["p_raw"]),
                 p_adjusted=F(pg), correction="holm_m24_global_across_dimensions",
                 effect_size=F(r["rank_biserial"]), effect_direction=r["direction"],
                 source_paths=sp, source_checksums=sc,
                 interpretation=("sensitivity companion to AN-PW-2017-D*; the REPORTED "
                                 "decision is the within-dimension one (holm_m6); "
                                 f"survives_global_holm={survives}"))
    write_csv(OUT_ROOT / "cec2017" / "global_holm_sensitivity_cec2017.csv",
              ["suite", "dimension", "function", "comparator", "test_level",
               "p_raw", "p_holm_within_dimension", "p_holm_global_m24",
               "outcome_within_dimension", "outcome_global", "survives_global_holm",
               "availability"], rows, ["AN-GHOLM-2017"])
    print(f"  AN-GHOLM-2017: {n_within}/24 significant within-dimension, "
          f"{n_global}/24 under global Holm ({n_lost} lost)")


def family_exploratory_bh() -> None:
    """AN-EXP-BH-2017: BH-FDR relabeling of AN-PWRUN-2017-* (exploratory)."""
    header = ["suite", "dimension", "function", "comparator", "test_level", "n_pairs",
              "statistic", "p_raw", "p_bh", "outcome", "availability"]
    for dim in SUITE_DIMS["cec2017"]:
        cell = PWRUN[("cec2017", dim)]
        rows = []
        for comp in COMPARATORS:
            avail = [(f, cell[(f, comp)]) for f in CEC2017_FUNCS if cell[(f, comp)] is not None]
            if avail:
                bh = benjamini_hochberg([r["p_raw"] for _, r in avail],
                                        [str(f) for f, _ in avail], alpha=ALPHA)
                adj = {str(c["label"]): float(c["p_adjusted"]) for c in bh.comparisons}
            else:
                adj = {}
            for f in CEC2017_FUNCS:
                r = cell[(f, comp)]
                if r is None:
                    BH_DEC[(dim, f, comp)] = None
                    continue
                p_bh = adj[str(f)]
                sig = p_bh < ALPHA
                outcome = ("win" if (sig and r["direction"] == "favors_dt-gsk") else
                           ("loss" if (sig and r["direction"] == "favors_comparator") else "tie"))
                BH_DEC[(dim, f, comp)] = {"p_bh": p_bh, "outcome": outcome}
        for f in CEC2017_FUNCS:
            for comp in COMPARATORS:
                r = cell[(f, comp)]
                if r is None:
                    rows.append(["cec2017", str(dim), str(f), comp, "per_function_runlevel",
                                 NA, NA, NA, NA, NA, "disclosed-unavailable"])
                    continue
                b = BH_DEC[(dim, f, comp)]
                rows.append(["cec2017", str(dim), str(f), comp, "per_function_runlevel",
                             str(r["n_pairs"]), F(r["statistic"]), F(r["p_raw"]),
                             F(b["p_bh"]), b["outcome"], "ok"])
                sp, sc = _per_run_sources("cec2017", comp)
                add_stat(analysis_id="AN-EXP-BH-2017", rq_id="RQ8", suite="cec2017",
                         dimension=str(dim), function_set=f"F{f}",
                         algorithms=f"dt-gsk vs {comp}",
                         metric="wilcoxon_signed_rank_runlevel_bh",
                         unit_of_analysis="run", n_observations=str(r["n_pairs"]),
                         pairing_key="get_cec_seed(20240620,dim,func,run)",
                         test="wilcoxon_signed_rank_two_sided",
                         test_statistic=F(r["statistic"]), p_raw=F(r["p_raw"]),
                         p_adjusted=F(b["p_bh"]), correction="benjamini_hochberg_q0.05",
                         effect_direction=r["direction"],
                         source_paths=sp, source_checksums=sc,
                         interpretation=("exploratory FDR analysis; separate family; "
                                         f"not comparable to Holm results; outcome={b['outcome']}"))
        write_csv(OUT_ROOT / "cec2017" / f"wilcoxon_run_cec2017_D{dim}_exploratory_bh.csv",
                  header, rows, ["AN-EXP-BH-2017"])


# ===========================================================================
# Robustness battery (AN-ROB-2017-01..08; exploratory)
# ===========================================================================
ROB_DIR = OUT_ROOT / "cec2017" / "robustness"
ROB_SUMMARY: list[dict] = []


def _rob_emit(tag: str, fam: str, header: list[str], rows: list[list[str]],
              digest: str, verdict: str, element: str, variant: str,
              audit_before: int) -> None:
    write_csv(ROB_DIR / f"robustness_cec2017_{tag}.csv", header, rows, [fam])
    md = ROB_DIR / f"robustness_cec2017_{tag}_digest.md"
    md.write_text(digest + "\n", encoding="utf-8")
    MANIFEST_ENTRIES.append({
        "path": md.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix(),
        "sha256": _fresh_sha(md), "generator": SCRIPT_REL, "analysis_ids": [fam]})
    delta = rl.get_source_audit()[audit_before:]
    write_json(ROB_DIR / f"robustness_cec2017_{tag}_source_audit.json",
               {"new_opens": delta,
                "note": ("inputs otherwise served from the in-process cache of "
                         "audited release reads; full log in cec2017/source_use_log.json")},
               analysis_ids=[fam])
    add_stat(analysis_id=fam, rq_id="RQ8", suite="cec2017", dimension="all",
             function_set=SUITE_FSET["cec2017"], algorithms="panel-7",
             metric=f"robustness_{tag}", unit_of_analysis="check",
             pairing_key=NA, test="none (exploratory robustness; labels only)",
             source_paths="see robustness CSV / source audit",
             source_checksums="see analysis_manifest.json",
             interpretation=f"element={element};variant={variant};verdict={verdict}")
    ROB_SUMMARY.append({"check": tag, "suite": "cec2017", "variant": variant,
                        "element": element, "verdict": verdict})


def robustness_battery() -> None:
    ROB_DIR.mkdir(parents=True, exist_ok=True)
    dims = SUITE_DIMS["cec2017"]

    # ---- r01 (= plan R2): mean vs median re-ranking ----------------------
    audit0 = len(rl.get_source_audit())
    header = ["suite", "dimension", "row_type", "algorithm", "comparator",
              "mean_rank_primary", "ordinal_primary", "mean_rank_variant",
              "ordinal_variant", "wtl_primary", "wtl_variant", "verdict"]
    rows, div = [], []
    for dim in dims:
        prim = FRIED[("cec2017", dim)]["mean_ranks"]
        op = ordinals(prim)
        med = friedman_with_id({alg: [MEDIANS[("cec2017", dim)][alg][f] for f in CEC2017_FUNCS]
                                for alg in PANEL})["mean_ranks"]
        om = ordinals(med)
        for alg in PANEL:
            v = "agree" if op[alg] == om[alg] else "diverge"
            if v == "diverge":
                div.append(f"D{dim}:{alg} ordinal {op[alg]}->{om[alg]}")
            rows.append(["cec2017", str(dim), "rank", alg, NA, F(prim[alg]), str(op[alg]),
                         F(med[alg]), str(om[alg]), NA, NA, v])
        for comp in COMPARATORS:
            w1 = WTL[("cec2017", dim, comp)]
            w2 = wtl_means(MEDIANS[("cec2017", dim)][PROPOSED],
                           MEDIANS[("cec2017", dim)][comp], CEC2017_FUNCS)
            v = "agree" if w1 == w2 else "diverge"
            if v == "diverge":
                div.append(f"D{dim}:wtl vs {comp} {w1}->{w2}")
            rows.append(["cec2017", str(dim), "wtl", PROPOSED, comp, NA, NA, NA, NA,
                         f"{w1[0]}-{w1[1]}-{w1[2]}", f"{w2[0]}-{w2[1]}-{w2[2]}", v])
    verdict = "agree" if not div else "diverge"
    _rob_emit("r01_mean_vs_median", "AN-ROB-2017-01", header, rows,
              "# r01 mean vs median (plan R2)\n\nverdict: **" + verdict +
              "**\n\ndivergences:\n" + ("\n".join(f"- {d}" for d in div) or "- none"),
              verdict, "ordinal rank positions + W/T/L (C-a)", "median re-ranking", audit0)

    # ---- r02 (= plan R1): error-floor sensitivity ------------------------
    audit0 = len(rl.get_source_audit())
    count_subfloor = 0
    scanned = 0
    for suite in ("cec2017", "cec2013"):
        for alg in PANEL:
            pr = load_per_run(suite, alg)
            for cell in pr["endpoint"].values():
                for v in cell.values():
                    scanned += 1
                    if 0.0 < v < TIE_TOL:
                        count_subfloor += 1
    branch = "A" if count_subfloor > 0 else "B"
    rows = [["cec2017", "all", "scan", NA, NA, NA, NA, NA, NA, NA, NA,
             f"count_in_(0,1e-8)={count_subfloor}/{scanned};branch={branch}"]]
    div = []
    for dim in dims:
        means = MEANS[("cec2017", dim)]
        snapped = {alg: {f: (0.0 if means[alg][f] <= TIE_TOL else means[alg][f])
                         for f in CEC2017_FUNCS} for alg in PANEL}
        var = friedman_with_id({alg: [snapped[alg][f] for f in CEC2017_FUNCS]
                                for alg in PANEL})["mean_ranks"]
        prim = FRIED[("cec2017", dim)]["mean_ranks"]
        op, ov = ordinals(prim), ordinals(var)
        for alg in PANEL:
            v = "agree" if op[alg] == ov[alg] else "diverge"
            if v == "diverge":
                div.append(f"D{dim}:{alg}")
            rows.append(["cec2017", str(dim), "rank", alg, NA, F(prim[alg]), str(op[alg]),
                         F(var[alg]), str(ov[alg]), NA, NA, v])
        for comp in COMPARATORS:
            w1 = WTL[("cec2017", dim, comp)]
            w2 = wtl_means(snapped[PROPOSED], snapped[comp], CEC2017_FUNCS)
            v = "agree" if w1 == w2 else "diverge"
            if v == "diverge":
                div.append(f"D{dim}:wtl vs {comp}")
            rows.append(["cec2017", str(dim), "wtl", PROPOSED, comp, NA, NA, NA, NA,
                         f"{w1[0]}-{w1[1]}-{w1[2]}", f"{w2[0]}-{w2[1]}-{w2[2]}", v])
    verdict = "agree" if not div else "diverge"
    digest = ("# r02 error-floor sensitivity (plan R1)\n\n"
              f"Scan of stored per-run errors (cec2017 class-A cells + cec2013): "
              f"{count_subfloor} value(s) in the open interval (0, 1e-8) out of {scanned} "
              f"scanned -> branch {branch}.\n\n"
              "Branch B disclosure (pre-registered): raw sub-floor values are "
              "unrecoverable from the release (write-time flooring); the check is "
              "executed as the nearest admissible surrogate B1/B2 (tie handling at the "
              "floor; means <= 1e-8 snapped to 0 before ranking/W-T-L).\n\n"
              f"verdict: **{verdict}**\n\ndivergences:\n"
              + ("\n".join(f"- {d}" for d in div) or "- none"))
    _rob_emit("r02_floor_sensitivity", "AN-ROB-2017-02", header, rows, digest,
              verdict, "ranks + W/T/L at the protocol floor", f"branch {branch} (B1 vs B2)",
              audit0)

    # ---- r03 (= plan R4): leave-one-function-out Friedman ----------------
    audit0 = len(rl.get_source_audit())
    header3 = ["suite", "dimension", "algorithm", "mean_rank_full", "ordinal_full",
               "lofo_min_mean_rank", "lofo_max_mean_rank", "ordinal_change_omissions",
               "verdict"]
    rows, div = [], []
    for dim in dims:
        means = MEANS[("cec2017", dim)]
        rank_mat = np.array([rank_row([means[alg][f] for alg in PANEL])
                             for f in CEC2017_FUNCS])
        full = {alg: float(np.mean(rank_mat[:, i])) for i, alg in enumerate(PANEL)}
        of = ordinals(full)
        changes: dict[str, list[int]] = {alg: [] for alg in PANEL}
        lo = {alg: full[alg] for alg in PANEL}
        hi = {alg: full[alg] for alg in PANEL}
        for j, f in enumerate(CEC2017_FUNCS):
            keep = [i for i in range(len(CEC2017_FUNCS)) if i != j]
            sub = {alg: float(np.mean(rank_mat[keep, i])) for i, alg in enumerate(PANEL)}
            os_ = ordinals(sub)
            for alg in PANEL:
                lo[alg] = min(lo[alg], sub[alg])
                hi[alg] = max(hi[alg], sub[alg])
                if os_[alg] != of[alg]:
                    changes[alg].append(f)
        for alg in PANEL:
            v = "agree" if not changes[alg] else "diverge"
            if changes[alg] and alg == PROPOSED:
                div.append(f"D{dim}: dt-gsk ordinal sensitive to F{changes[alg]}")
            rows.append(["cec2017", str(dim), alg, F(full[alg]), str(of[alg]),
                         F(lo[alg]), F(hi[alg]),
                         ";".join(f"F{x}" for x in changes[alg]) or "none", v])
    verdict = "agree" if not div else "diverge"
    _rob_emit("r03_lofo_friedman", "AN-ROB-2017-03", header3, rows,
              "# r03 LOFO Friedman (plan R4)\n\nDT-GSK ordinal-position stability under "
              "leave-one-function-out.\n\nverdict: **" + verdict + "**\n\n" +
              ("\n".join(f"- {d}" for d in div) or "- none"),
              verdict, "DT-GSK ordinal position (C-a)", "29 LOFO replicates per dimension",
              audit0)

    # ---- r04 (= plan R3): disputed-cell exclusion -------------------------
    audit0 = len(rl.get_source_audit())
    header4 = ["suite", "dimension", "variant", "algorithm", "mean_rank_v1",
               "ordinal_v1", "mean_rank_variant", "ordinal_variant",
               "orderings_preserved", "verdict"]
    rows, div = [], []
    variants = [("v2_apgsk_excluded", "apgsk", APGSK_DISPUTED_DIMS),
                ("v2b_egsk_excluded", "egsk", tuple(dims))]
    for vname, excl, vdims in variants:
        for dim in vdims:
            means = MEANS[("cec2017", dim)]
            keep = [a for a in PANEL if a != excl]
            sub = friedman_with_id({alg: [means[alg][f] for f in CEC2017_FUNCS]
                                    for alg in keep})["mean_ranks"]
            prim = FRIED[("cec2017", dim)]["mean_ranks"]
            order_v1 = sorted(keep, key=lambda a: (prim[a], PANEL.index(a)))
            order_v2 = sorted(keep, key=lambda a: (sub[a], PANEL.index(a)))
            preserved = order_v1 == order_v2
            verdict_dim = "agree" if preserved else "diverge"
            if not preserved:
                div.append(f"{vname} D{dim}: ordering changed")
            for alg in PANEL:
                rows.append(["cec2017", str(dim), vname, alg, F(prim[alg]),
                             str(ordinals(prim)[alg]),
                             F(sub[alg]) if alg in sub else NA,
                             str(ordinals(sub)[alg]) if alg in sub else NA,
                             "yes" if preserved else "no", verdict_dim])
    verdict = "agree" if not div else "diverge"
    _rob_emit("r04_disputed_cell_exclusion", "AN-ROB-2017-04", header4, rows,
              "# r04 disputed-cell exclusion (plan R3)\n\nV1 = 7-algorithm panel; "
              "V2 = apgsk excluded (D10/D30/D50); V2b = eGSK excluded (all dims). "
              "Mechanical 7->6 rank rescaling with all pairwise orderings preserved "
              "counts as agreement (plan R3 narrowing). V3 not exercised (no Gate-2 CR)."
              "\n\nverdict: **" + verdict + "**\n\n" +
              ("\n".join(f"- {d}" for d in div) or "- none"),
              verdict, "descriptive rank aggregates (C-a)", "apgsk V1/V2 + eGSK exclusion",
              audit0)

    # ---- r05 (= plan R5): paired vs unpaired companion --------------------
    audit0 = len(rl.get_source_audit())
    header5 = ["suite", "dimension", "function", "comparator", "p_paired_raw",
               "p_paired_holm", "decision_paired", "p_unpaired_raw", "p_unpaired_holm",
               "decision_unpaired", "transition"]
    rows = []
    reversals, weakenings = 0, 0
    for dim in dims:
        cell = PWRUN[("cec2017", dim)]
        for comp in COMPARATORS:
            avail = [f for f in CEC2017_FUNCS if cell[(f, comp)] is not None]
            if not avail:
                continue
            pu, labels = [], []
            dir_u = {}
            for f in avail:
                x, y = paired_runs("cec2017", comp, dim, f)
                if np.all(x == x[0]) and np.all(y == y[0]) and abs(x[0] - y[0]) < TIE_TOL:
                    p = 1.0
                else:
                    p = float(sps.mannwhitneyu(x, y, alternative="two-sided",
                                               method="asymptotic").pvalue)
                a12, _, _ = a12_band(x, y)
                dir_u[f] = ("favors_dt-gsk" if a12 > 0.5 else
                            ("favors_comparator" if a12 < 0.5 else "none"))
                pu.append(p)
                labels.append(str(f))
            holm_u = holm_correction(pu, labels, alpha=ALPHA)
            adj_u = {str(c["label"]): float(c["p_adjusted"]) for c in holm_u.comparisons}
            for f, p_raw_u in zip(avail, pu):
                r = cell[(f, comp)]
                sig_u = adj_u[str(f)] < ALPHA
                dec_u = ("win" if (sig_u and dir_u[f] == "favors_dt-gsk") else
                         ("loss" if (sig_u and dir_u[f] == "favors_comparator") else "tie"))
                dec_p = r["outcome"]
                if dec_p == dec_u:
                    trans = "none"
                elif {dec_p, dec_u} == {"win", "loss"}:
                    trans = "sign_reversal"
                    reversals += 1
                elif dec_u == "tie":
                    trans = "sig_to_ns"
                    weakenings += 1
                else:
                    trans = "ns_to_sig"
                rows.append(["cec2017", str(dim), str(f), comp, F(r["p_raw"]),
                             F(r["p_holm"]), dec_p, F(p_raw_u), F(adj_u[str(f)]),
                             dec_u, trans])
    verdict = "agree" if reversals == 0 else "diverge"
    _rob_emit("r05_unpaired_companion", "AN-ROB-2017-05", header5, rows,
              "# r05 paired vs unpaired (plan R5)\n\nUnpaired Mann-Whitney companion "
              "(scipy.stats.mannwhitneyu, two-sided, asymptotic) to every per-function "
              "run-level Wilcoxon; Holm within identical families. Expected direction: "
              "unpaired less powerful under positive pairing correlation.\n\n"
              f"sign reversals: {reversals}; significant->n.s. transitions: {weakenings}\n\n"
              f"verdict: **{verdict}**", verdict,
              "per-function Holm decision triples (C-b)", "unpaired Mann-Whitney U", audit0)

    # ---- r06 (= plan R6): Holm vs BH --------------------------------------
    audit0 = len(rl.get_source_audit())
    header6 = ["suite", "dimension", "comparator", "n_functions", "n_sig_holm",
               "n_sig_bh", "n_decisions_differing", "differing_functions",
               "bh_removes_holm_rejection"]
    rows = []
    anomalies = 0
    for dim in dims:
        cell = PWRUN[("cec2017", dim)]
        for comp in COMPARATORS:
            avail = [f for f in CEC2017_FUNCS if cell[(f, comp)] is not None]
            if not avail:
                rows.append(["cec2017", str(dim), comp, NA, NA, NA, NA,
                             "disclosed-unavailable", NA])
                continue
            n_h = sum(1 for f in avail if cell[(f, comp)]["outcome"] != "tie")
            n_b = sum(1 for f in avail if BH_DEC[(dim, f, comp)]["outcome"] != "tie")
            diff = [f for f in avail
                    if cell[(f, comp)]["outcome"] != BH_DEC[(dim, f, comp)]["outcome"]]
            removed = any(cell[(f, comp)]["outcome"] != "tie"
                          and BH_DEC[(dim, f, comp)]["outcome"] == "tie" for f in avail)
            anomalies += int(removed)
            rows.append(["cec2017", str(dim), comp, str(len(avail)), str(n_h), str(n_b),
                         str(len(diff)), ";".join(f"F{f}" for f in diff) or "none",
                         "yes" if removed else "no"])
    _rob_emit("r06_holm_vs_bh", "AN-ROB-2017-06", header6, rows,
              "# r06 Holm vs BH (plan R6)\n\nExploratory - BH, not used for any claim. "
              "BH-vs-Holm differences are expected and are not divergences per se; "
              f"BH-removes-Holm-rejection anomalies: {anomalies}.",
              "n/a (exploratory)", "decision counts per (dim, comparator)",
              "Benjamini-Hochberg q=0.05 (AN-EXP-BH-2017)", audit0)

    # ---- r07 (= plan R7 cross-suite facet) --------------------------------
    audit0 = len(rl.get_source_audit())
    header7 = ["algorithm", "mean_rank_cec2017_overall", "ordinal_cec2017",
               "mean_rank_cec2013_overall", "ordinal_cec2013", "mean_rank_cec2011",
               "ordinal_cec2011", "verdict"]
    o17 = ordinals(OVERALL["cec2017"])
    o13 = ordinals(OVERALL["cec2013"])
    o11 = ordinals(OVERALL["cec2011"])
    rows = []
    for alg in PANEL:
        v = "agree" if (o17[alg] == o13[alg] == o11[alg]) else \
            ("qualitatively-consistent" if abs(o17[alg] - o13[alg]) <= 1
             and abs(o17[alg] - o11[alg]) <= 1 else "diverge")
        rows.append([alg, F(OVERALL["cec2017"][alg]), str(o17[alg]),
                     F(OVERALL["cec2013"][alg]), str(o13[alg]),
                     F(OVERALL["cec2011"][alg]), str(o11[alg]), v])
    ism_v = rows[PANEL.index(PROPOSED)][7]
    _rob_emit("r07_secondary_suite_effect", "AN-ROB-2017-07", header7, rows,
              "# r07 secondary-suite inclusion/exclusion (plan R7 cross-suite facet)\n\n"
              "Side-by-side overall orderings (cec2017 primary; cec2013 second comparison "
              "suite; cec2011 secondary real-world suite). This side-by-side IS the "
              "pre-registered answer to the inclusion/exclusion question.\n\n"
              f"DT-GSK verdict: **{ism_v}** (ordinals {o17[PROPOSED]}/{o13[PROPOSED]}/"
              f"{o11[PROPOSED]})", ism_v,
              "qualitative cross-suite ordering of DT-GSK", "with vs without secondary suites",
              audit0)

    # ---- r08 (= plan R7 pooled block-Friedman) -----------------------------
    audit0 = len(rl.get_source_audit())
    header8 = ["algorithm", "mean_rank_mean_of_dims", "ordinal_mean_of_dims",
               "mean_rank_pooled_blocks", "ordinal_pooled", "pooled_chi2",
               "pooled_iman_davenport_F", "pooled_p", "n_blocks", "verdict"]
    blocks = {alg: [] for alg in PANEL}
    for dim in dims:
        means = MEANS[("cec2017", dim)]
        for alg in PANEL:
            blocks[alg].extend(means[alg][f] for f in CEC2017_FUNCS)
    pooled = friedman_with_id(blocks)
    po = ordinals(pooled["mean_ranks"])
    oo = ordinals(OVERALL["cec2017"])
    rows, div = [], []
    for alg in PANEL:
        v = "agree" if po[alg] == oo[alg] else "diverge"
        if v == "diverge":
            div.append(f"{alg}: {oo[alg]}->{po[alg]}")
        rows.append([alg, F(OVERALL["cec2017"][alg]), str(oo[alg]),
                     F(pooled["mean_ranks"][alg]), str(po[alg]), F(pooled["chi2"]),
                     F(pooled["f_id"]), F(pooled["p_id"]), str(pooled["n"]), v])
    verdict = "agree" if not div else "diverge"
    _rob_emit("r08_overall_aggregation_variants", "AN-ROB-2017-08", header8, rows,
              "# r08 overall-aggregation variants (plan R7)\n\nPrimary descriptive "
              "unweighted mean of per-dimension Friedman mean ranks vs pooled "
              "(function,dimension)-block Friedman (116 blocks). The pooled block-Friedman "
              "appears ONLY here, never as the T05 overall row.\n\nverdict: **" + verdict +
              "**\n\n" + ("\n".join(f"- {d}" for d in div) or "- none"),
              verdict, "overall ordinal positions (C-a)", "pooled block-Friedman", audit0)

    # consolidated summary table (robustness_plan.md Section 4 template)
    lines = ["# Robustness summary - cec2017 (Phase 6 bound values)", "",
             "| Check | Suite | Variant compared | Primary conclusion element | Verdict |",
             "|---|---|---|---|---|"]
    for r in ROB_SUMMARY:
        lines.append(f"| {r['check']} | {r['suite']} | {r['variant']} | "
                     f"{r['element']} | {r['verdict']} |")
    md = ROB_DIR / "robustness_summary_cec2017.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    MANIFEST_ENTRIES.append({
        "path": md.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix(),
        "sha256": _fresh_sha(md), "generator": SCRIPT_REL,
        "analysis_ids": [f"AN-ROB-2017-0{i}" for i in range(1, 9)]})


# ===========================================================================
# headline_bca.csv (registry-defined equivalent: union of bca_ci_cec2017_D*)
# ===========================================================================
def emit_headline_bca() -> None:
    header = ["suite", "dimension", "function", "comparator", "n_runs", "mean_diff",
              "ci_low", "ci_high", "B", "seed_scheme", "availability"]
    rows = []
    for dim in SUITE_DIMS["cec2017"]:
        src = OUT_ROOT / "cec2017" / f"bca_ci_cec2017_D{dim}.csv"
        with open(src, "r", encoding="utf-8", newline="") as fh:
            rdr = csv.reader(fh)
            next(rdr)
            rows.extend(list(rdr))
    write_csv(OUT_ROOT / "cec2017" / "headline_bca.csv", header, rows,
              [f"AN-EFF-2017-D{d}" for d in SUITE_DIMS["cec2017"]])


# ===========================================================================
# Sensitivity evidence-gap row (pre-verified: no admissible release evidence)
# ===========================================================================
def sensitivity_gap_row() -> None:
    add_stat(analysis_id="EG-006-T-SENS", rq_id="RQ8", suite="cec2017", dimension="all",
             function_set=NA, algorithms="dt-gsk",
             metric="parameter_sensitivity", unit_of_analysis=NA,
             pairing_key=NA, test="none",
             source_paths="NONE RESOLVABLE (release carries no parametric sweep)",
             source_checksums=NA,
             interpretation=("disclosed-unavailable: no admissible parameter-sensitivity "
                             "evidence in rel-2026-07-10-262fc16c9 (EG-006, "
                             "evidence_gap_register.md); results/ staging never read"),
             status="evidence-gap")


# ===========================================================================
# Cross-implementation verification (task 17)
# ===========================================================================
def cross_check() -> None:
    items = []
    hard_fail = []

    def close(a, b, rtol=1e-9, atol=1e-12):
        return bool(abs(a - b) <= atol + rtol * max(abs(a), abs(b)))

    # --- Friedman: ranks + chi2 (scipy + direct formula) -------------------
    for suite, dim in [("cec2017", 10), ("cec2017", 100), ("cec2013", 30), ("cec2011", 0)]:
        funcs = SUITE_FUNCS[suite]
        means = MEANS[(suite, dim)]
        mat = np.array([[means[alg][f] for alg in PANEL] for f in funcs])
        ranks = np.array([sps.rankdata(row, method="average") for row in mat])
        mr_ref = {alg: float(np.mean(ranks[:, i])) for i, alg in enumerate(PANEL)}
        ours = FRIED[(suite, dim)]["mean_ranks"]
        ranks_agree = all(close(ours[a], mr_ref[a], rtol=1e-12) for a in PANEL)
        n, k = len(funcs), 7
        chi2_direct = (12.0 * n / (k * (k + 1))) * float(
            np.sum((np.mean(ranks, axis=0) - (k + 1) / 2.0) ** 2))
        chi2_scipy = float(sps.friedmanchisquare(
            *[mat[:, i] for i in range(k)]).statistic)
        # M-026: the REPORTED chi2 is now tie-corrected, so it is verified against
        # scipy's tie-corrected statistic; the retained uncorrected companion is
        # verified against the classical direct formula. Both are checked, which
        # is strictly stronger than the previous single comparison. (Before M-026
        # the repo reported the untied 1937 statistic and only that was checked,
        # so this cross-check failed on exactly the tied panels -- CEC2017 D10,
        # CEC2013 D30, CEC2011 -- and passed where C = 1.)
        chi2_ours = FRIED[(suite, dim)]["chi2"]
        chi2_ours_unc = FRIED[(suite, dim)]["chi2_uncorrected"]
        dec_ours = FRIED[(suite, dim)]["p_id"] < ALPHA
        p_scipy = float(sps.friedmanchisquare(*[mat[:, i] for i in range(k)]).pvalue)
        dec_scipy = p_scipy < ALPHA
        corrected_ok = close(chi2_ours, chi2_scipy, rtol=1e-9)
        uncorrected_ok = close(chi2_ours_unc, chi2_direct, rtol=1e-9)
        agree = ranks_agree and corrected_ok and uncorrected_ok and dec_ours == dec_scipy
        if not agree:
            hard_fail.append(f"friedman {suite} D{dim}")
        items.append({
            "check": "friedman", "cell": f"{suite}/D{dim}",
            "ranks_agree_exact": ranks_agree,
            "chi2_ours_tie_corrected": chi2_ours,
            "chi2_scipy_tie_corrected": chi2_scipy,
            "corrected_agree": bool(corrected_ok),
            "chi2_ours_uncorrected": chi2_ours_unc,
            "chi2_direct_formula": chi2_direct,
            "uncorrected_agree": bool(uncorrected_ok),
            "tie_correction_C": FRIED[(suite, dim)]["tie_correction"],
            "p_scipy": p_scipy,
            "decision_agree_alpha_0.05": bool(dec_ours == dec_scipy),
            "agree": bool(agree),
            "note": ("reported chi2 is tie-corrected and must match "
                     "scipy.stats.friedmanchisquare; the retained uncorrected "
                     "companion must match the classical 1937 direct formula; "
                     "ranks and the alpha=0.05 decision must agree")})

    # --- Holm adjustments (direct formula) ---------------------------------
    for suite, dim in [("cec2017", 30), ("cec2013", 10), ("cec2011", 0)]:
        praw = [PW[(suite, dim, c)]["p_raw"] for c in COMPARATORS]
        ours = [PW[(suite, dim, c)]["p_holm"] for c in COMPARATORS]
        m = len(praw)
        order = np.argsort(praw)
        adj = np.empty(m)
        running = 0.0
        for rank_idx, oi in enumerate(order):
            running = max(running, min(1.0, praw[oi] * (m - rank_idx)))
            adj[oi] = running
        agree = all(close(a, b, rtol=1e-12) for a, b in zip(ours, adj))
        if not agree:
            hard_fail.append(f"holm {suite} D{dim}")
        items.append({"check": "holm", "cell": f"{suite}/D{dim}/AN-PW family",
                      "ours": ours, "direct": adj.tolist(), "agree": bool(agree)})

    # --- A12 (direct formula + repo function) -------------------------------
    a12_cells = [("cec2017", 100, 5, "gsk"), ("cec2013", 30, 10, "agsk"),
                 ("cec2011", 0, 5, "egsk")]
    from gsk_family.analysis.statistics import vargha_delaney
    for suite, dim, f, comp in a12_cells:
        x, y = paired_runs(suite, comp, dim, f)
        ours = A12S[(suite, dim, f, comp)]
        diff = y[None, :] - x[:, None]
        direct = (float(np.sum(diff >= TIE_TOL)) + 0.5 * float(np.sum(np.abs(diff) < TIE_TOL))) \
            / (len(x) * len(y))
        repo = vargha_delaney(list(x), list(y)).a12
        agree = close(ours, direct, rtol=1e-12)
        if not agree:
            hard_fail.append(f"a12 {suite} D{dim} F{f} {comp}")
        items.append({"check": "a12", "cell": f"{suite}/D{dim}/F{f}/vs {comp}",
                      "ours": ours, "direct_formula_band": direct,
                      "repo_exact_tie_variant": repo, "agree": bool(agree),
                      "note": ("record uses the SAP Sec.7 tie band |d|<1e-8 counted half; "
                               "repo vargha_delaney counts exact-equality ties only")})

    # --- BCa interval (independent implementation, same resample indices) ---
    suite, dim, f, comp = "cec2017", 30, 17, "gsk"
    x, y = paired_runs(suite, comp, dim, f)
    d = x - y
    stored = BCAS[(suite, dim, f, comp)]
    if stored["lo"] is None:
        items.append({"check": "bca", "cell": f"{suite}/D{dim}/F{f}/vs {comp}",
                      "agree": True, "note": "degenerate cell; no CI to verify"})
    else:
        rng = np.random.default_rng(np.random.SeedSequence(stored["seed"]))
        n = len(d)
        idx = rng.integers(0, n, size=(B_BOOT, n))
        boots = np.sort(np.mean(d[idx], axis=1))
        theta = float(np.mean(d))
        frac = min(max(float(np.mean(boots < theta)), 1e-9), 1 - 1e-9)
        z0 = float(sps.norm.ppf(frac))
        jack = (d.sum() - d) / (n - 1)
        u = float(jack.mean()) - jack
        den = 6.0 * float(np.sum(u ** 2)) ** 1.5
        a_hat = float(np.sum(u ** 3)) / den if den > 0 else 0.0
        z_lo, z_hi = sps.norm.ppf(ALPHA / 2), sps.norm.ppf(1 - ALPHA / 2)
        alo = float(sps.norm.cdf(z0 + (z0 + z_lo) / (1 - a_hat * (z0 + z_lo))))
        ahi = float(sps.norm.cdf(z0 + (z0 + z_hi) / (1 - a_hat * (z0 + z_hi))))
        lo_ref = float(np.quantile(boots, min(max(alo, 0.0), 1.0), method="linear"))
        hi_ref = float(np.quantile(boots, min(max(ahi, 0.0), 1.0), method="linear"))
        agree = close(stored["lo"], lo_ref, rtol=1e-5, atol=1e-9) and \
            close(stored["hi"], hi_ref, rtol=1e-5, atol=1e-9)
        if not agree:
            hard_fail.append("bca cell")
        items.append({"check": "bca", "cell": f"{suite}/D{dim}/F{f}/vs {comp}",
                      "ours": [stored["lo"], stored["hi"]],
                      "independent_scipy_norm": [lo_ref, hi_ref], "agree": bool(agree),
                      "note": ("identical resample indices from the pre-registered seeded "
                               "stream; z0/acceleration recomputed with scipy.stats.norm")})

    # --- Wilcoxon statistic vs scipy ----------------------------------------
    for suite, dim, f, comp in [("cec2017", 30, 0, "gsk"), ("cec2017", 100, 1, "agsk"),
                                ("cec2011", 0, 3, "gsk")]:
        if f == 0:
            funcs = SUITE_FUNCS[suite]
            x = np.array([MEANS[(suite, dim)][PROPOSED][ff] for ff in funcs])
            y = np.array([MEANS[(suite, dim)][comp][ff] for ff in funcs])
            ours_p = PW[(suite, dim, comp)]["p_raw"]
            ours_w = PW[(suite, dim, comp)]["statistic"]
            cell = f"{suite}/D{dim}/across-functions vs {comp}"
        else:
            x, y = paired_runs(suite, comp, dim, f)
            r = PWRUN[(suite, dim)][(f, comp)]
            ours_p, ours_w = r["p_raw"], r["statistic"]
            cell = f"{suite}/D{dim}/F{f} run-level vs {comp}"
        dd = x - y
        nz = np.abs(dd) >= TIE_TOL
        if int(np.sum(nz)) == 0:
            items.append({"check": "wilcoxon", "cell": cell, "agree": True,
                          "note": "all differences below tie tolerance; p=1 by convention"})
            continue
        ref = sps.wilcoxon(x[nz], y[nz], zero_method="wilcox", correction=True,
                           alternative="two-sided", method="approx")
        agree_stat = close(ours_w, float(ref.statistic), rtol=1e-12)
        dec_agree = (ours_p < ALPHA) == (float(ref.pvalue) < ALPHA)
        if not (agree_stat and dec_agree):
            hard_fail.append(f"wilcoxon {cell}")
        items.append({"check": "wilcoxon", "cell": cell, "W_ours": ours_w,
                      "W_scipy": float(ref.statistic), "p_ours": ours_p,
                      "p_scipy": float(ref.pvalue),
                      "statistic_agree": bool(agree_stat),
                      "decision_agree_alpha_0.05": bool(dec_agree),
                      "agree": bool(agree_stat and dec_agree),
                      "note": ("repo p uses normal approximation with continuity "
                               "correction, no tie-variance correction; scipy approx "
                               "applies tie correction; W and alpha=0.05 decision must agree")})

    out = {"release_id": REL_ID, "items": items,
           "hard_disagreements": hard_fail,
           "overall": "agree" if not hard_fail else "DISAGREE"}
    write_json(OUT_ROOT / "cross_check.json", out, analysis_ids=["CROSS-CHECK"])
    if hard_fail:
        raise RuntimeError(f"cross-implementation verification failed: {hard_fail}")


# ===========================================================================
# Logs / manifests
# ===========================================================================
def write_source_logs(started: str, finished: str) -> None:
    audit = rl.get_source_audit()
    by_suite: dict[str, list] = {s: [] for s in SUITE_ORDER}
    for entry in audit:
        rel = Path(entry["path"]).resolve().relative_to(REF_ROOT.resolve())
        by_suite[rel.parts[0]].append(entry)
    for suite in SUITE_ORDER:
        log = {"release": REL_ID, "anchor_commit": ANCHOR,
               "command": COMMAND, "strict_source": True,
               "started_utc": started, "finished_utc": finished, "status": "ok",
               "opened": by_suite[suite]}
        write_json(OUT_ROOT / suite / "source_use_log.json", log, analysis_ids=["SOURCE-LOG"])
    bad = [e for e in audit
           if not Path(e["path"]).resolve().is_relative_to(REF_ROOT.resolve())]
    if bad:
        raise RuntimeError(f"source audit contains non-release paths: {bad}")


def write_run_manifests(curve_info: dict) -> None:
    repro = json.loads((PAPER_DIR / "governance" / "reproducibility_manifest.json")
                       .read_text(encoding="utf-8"))
    base = {
        "release_id": REL_ID, "anchor_commit": ANCHOR,
        "host_environment": repro.get("environment", {}),
        "runtime_versions": {"numpy": np.__version__,
                             "scipy": __import__("scipy").__version__,
                             "pandas": __import__("pandas").__version__},
        "command": COMMAND, "script": SCRIPT_REL, "git_head_at_run": GIT_HEAD,
        "conventions": [
            "floats C-locale %.6e; integers plain; disclosed-unavailable cells literal n/a",
            "sort: suite, dimension asc, function asc, algorithm/comparator in P1 order "
            "(gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk)",
            "cec2011 endpoint = best_fitness (error NaN by design, A2-017); "
            "native dims in dimension columns; dimension=0 sentinel for suite-level rows",
            "BCa: B=10000, default_rng(SeedSequence([20240620, suite_ordinal, dimension, "
            "function, comparator_P1_index])); cec2011 uses the problem's native dimension",
            "degenerate BCa cells (all paired differences identical): point estimate kept, "
            "ci cells n/a, availability='no CI (degenerate cell)' per SAP Sec.7",
            "Nemenyi q_0.05(k=7)=2.949 (Demsar 2006 Table 5a); CD emitted only when the "
            "Iman-Davenport omnibus p<0.05",
            "Wilcoxon: two-sided; |d|<1e-8 treated as zero-difference and discarded "
            "(zero_method='wilcox'); p via statistics.wilcoxon_paired (normal approximation "
            "with continuity correction) - method recorded per test",
            "W/T/L tie rule: pure |delta|<1e-8 (SAP Sec.4); the repo win_tie_loss "
            "relative-band variant is NOT used (SAP governs)",
            "A12 ties counted half within |d|<1e-8 (SAP Sec.7 explicit formula)",
            "cost SD uses ddof=1; cost file carries cec2017+cec2013+cec2011 rows "
            "(suite order cec2017, cec2013, cec2011)",
            "apgsk cec2017 D10/D30/D50 run-level cells (Wilcoxon/A12/Cliff/BCa) recovered "
            "under CR-0006 (A2-004 resolved; per_run.csv restored to full four-dimension "
            "coverage, validated against the frozen apgsk summaries) and computed here",
        ],
        "curve_selection": curve_info,
        "checkpoint_grid_mismatches": GRID_MISMATCHES or "none",
        "notes": NOTES or "none",
    }
    write_json(OUT_ROOT / "run_manifest.json", base, analysis_ids=["RUN-MANIFEST"])
    for suite in SUITE_ORDER:
        sub = dict(base)
        sub["suite"] = suite
        write_json(OUT_ROOT / suite / "run_manifest.json", sub, analysis_ids=["RUN-MANIFEST"])


def write_statistical_results() -> None:
    suite_rank = {s: i for i, s in enumerate(SUITE_ORDER)}
    comp_rank = {c: i for i, c in enumerate(PANEL)}

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
    rows = [[r[c] for c in STAT_COLUMNS] for r in STAT_ROWS]
    write_csv(OUT_ROOT / "primary_stats" / "statistical_results.csv",
              STAT_COLUMNS, rows, ["ALL-REGISTRY-FAMILIES"])


def write_manifest_and_checksums() -> None:
    lines = []
    for e in MANIFEST_ENTRIES:
        lines.append(f"{e['sha256']}  {e['path']}")
    (OUT_ROOT / "analysis_checksums.sha256").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    manifest = {"release_id": REL_ID, "anchor_commit": ANCHOR,
                "generator": SCRIPT_REL, "command": COMMAND,
                "git_head_at_run": GIT_HEAD, "outputs": MANIFEST_ENTRIES}
    with open(OUT_ROOT / "analysis_manifest.json", "w", encoding="utf-8", newline="") as fh:
        json.dump(manifest, fh, indent=1)
        fh.write("\n")
    print(f"  wrote analysis_manifest.json ({len(MANIFEST_ENTRIES)} outputs) + analysis_checksums.sha256")


def write_table_map() -> None:
    rows = [
        ("T01-SUM / T01-D10..D100", "cec2017/descriptive_stats_cec2017_D{10,30,50,100}.csv "
         "(+ W/T/L rows in primary_stats/statistical_results.csv, AN-DESC-2017-*)"),
        ("T02 / T02-FULL-D10..D100", "cec2017/wilcoxon_holm_cec2017_D{10,30,50,100}.csv + "
         "cec2017/wilcoxon_run_cec2017_D{10,30,50,100}.csv"),
        ("T03 / T03-FULL-D10..D100", "cec2017/effect_sizes_cec2017_D{10,30,50,100}.csv"),
        ("T-BCA", "cec2017/bca_ci_cec2017_D{10,30,50,100}.csv + cec2017/headline_bca.csv"),
        ("T05", "cec2017/friedman_ranks_cec2017_D{10,30,50,100}.csv + "
         "cec2017/friedman_ranks_cec2017_overall.csv"),
        ("F01-D10..D100", "cec2017/friedman_ranks_cec2017_D*.csv + "
         "cec2017/nemenyi_cd_cec2017_D*.csv (emitted only when omnibus significant)"),
        ("F02-MAIN-D30/D100", "papers/build_prompt_phases/phase_05/curve_selection.csv + "
         "cec2017/curve_selection_cec2017_D{30,100}.csv + "
         "cec2017/convergence_checkpoints_cec2017_D{30,100}.csv"),
        ("F02-SUP-CEC2017-D10..D100", "cec2017/convergence_checkpoints_cec2017_D*.csv"),
        ("F02-SUP-CEC2011", "cec2011/convergence_checkpoints_cec2011.csv"),
        ("F02-SUP-CEC2013-D30", "cec2013/convergence_checkpoints_cec2013_D30.csv"),
        ("F03", "cec2017/rank_trend_cec2017.csv"),
        ("F05-RANKBAR", "cec2017/friedman_ranks_cec2017_D*.csv"),
        ("T04 / F04-CEC2011", "cec2011/descriptive_stats_cec2011.csv + "
         "cec2011/friedman_ranks_cec2011.csv"),
        ("T04-STATS", "cec2011/wilcoxon_holm_cec2011.csv + cec2011/wilcoxon_run_cec2011.csv "
         "+ cec2011/effect_sizes_cec2011.csv + cec2011/bca_ci_cec2011.csv"),
        ("T06 / T06-FULL-D10..D50", "cec2013/friedman_ranks_cec2013_D{10,30,50}.csv + "
         "cec2013/friedman_ranks_cec2013_overall.csv + "
         "cec2013/descriptive_stats_cec2013_D{10,30,50}.csv"),
        ("T-RUNTIME", "cec2017/cost_cec2017.csv (comparability-qualified)"),
        ("T-SENS", "disclosed-unavailable (EG-006; evidence-gap row in "
         "primary_stats/statistical_results.csv)"),
        ("F-TRACE / F-ADAPT", "gated: no GenLog_* diagnostic release exists "
         "(source_resolution_map.csv); disclosed-unavailable"),
        ("X-ABL-01..03", "DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY; results/_ablation quarantined; "
         "NOT computed in Phase 6"),
        ("AN-CLASS-2017", "cec2017/class_ranks_cec2017.csv (exploratory)"),
        ("AN-ROB-2017-01..08", "cec2017/robustness/robustness_cec2017_r0{1..8}_*.csv"),
        ("AN-EXP-BH-2017", "cec2017/wilcoxon_run_cec2017_D*_exploratory_bh.csv"),
        ("T1-T16 legacy staging", "results/paper_tables/T{1..16}.csv "
         "(exported from this bundle; provenance.json alongside)"),
    ]
    lines = ["# Exhibit -> authoritative CSV map (Phase 6, release " + REL_ID + ")", "",
             "| Planned exhibit | Authoritative machine-readable source |", "|---|---|"]
    for a, b in rows:
        lines.append(f"| {a} | {b} |")
    p = OUT_ROOT / "table_to_csv_map.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    MANIFEST_ENTRIES.append({
        "path": p.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix(),
        "sha256": _fresh_sha(p), "generator": SCRIPT_REL, "analysis_ids": ["TABLE-MAP"]})
    print("  wrote table_to_csv_map.md")


# ===========================================================================
# Task 23: export T1-T16 staging CSVs to results/paper_tables/
# ===========================================================================
DISPLAY = {"gsk": "GSK", "agsk": "AGSK", "apgsk": "APGSK", "fdb-agsk": "FDBAGSK",
           "atmals-gsk": "ATMALS-GSK", "egsk": "EGSK", "dt-gsk": "DT-GSK"}
EXPORT_PROV: dict[str, dict] = {}


def _bundle_csv(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _export(name: str, header: list[str], rows: list[list[str]],
            sources: list[Path], derivation: str) -> None:
    path = PAPER_TABLES / name
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    EXPORT_PROV[name] = {
        "sources": [p.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
                    for p in sources],
        "source_sha256": {p.name: _fresh_sha(p) for p in sources},
        "derivation": derivation,
    }
    MANIFEST_ENTRIES.append({
        "path": path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix(),
        "sha256": _fresh_sha(path), "generator": SCRIPT_REL,
        "analysis_ids": [f"EXPORT-{name[:-4]}"]})
    print(f"  exported {path.relative_to(PROJECT_ROOT)}")


def _h2h_rows(desc_path: Path):
    data = _bundle_csv(desc_path)
    by_func: dict[int, dict[str, dict]] = {}
    for r in data:
        by_func.setdefault(int(r["function"]), {})[r["algorithm"]] = r
    rows = []
    for f in sorted(by_func):
        g, i = by_func[f]["gsk"], by_func[f]["dt-gsk"]
        rows.append([f"F{f}", g["best"], i["best"], g["median"], i["median"],
                     g["mean"], i["mean"], g["worst"], i["worst"], g["sd"], i["sd"]])
    return rows


def _rank_sums_from_means(means_i: dict, means_c: dict, funcs: list[int]):
    """(R_plus_ism_better, R_minus) on per-function means, ties |d|<1e-8 dropped."""
    d = np.array([means_c[f] - means_i[f] for f in funcs])  # >0 -> ism better
    nz = np.abs(d) >= TIE_TOL
    d = d[nz]
    if len(d) == 0:
        return 0.0, 0.0
    ranks = _midranks(np.abs(d))
    return float(np.sum(ranks[d > 0])), float(np.sum(ranks[d <= 0]))


def export_paper_tables() -> None:
    PAPER_TABLES.mkdir(parents=True, exist_ok=True)
    h2h_hdr = ["Func", "Best_GSK", "Best_ISM", "Median_GSK", "Median_ISM", "Mean_GSK",
               "Mean_ISM", "Worst_GSK", "Worst_ISM", "SD_GSK", "SD_ISM"]

    # T1 (cec2011 h2h) and T2-T5 (cec2017 h2h D10/30/50/100)
    p = OUT_ROOT / "cec2011" / "descriptive_stats_cec2011.csv"
    _export("T1.csv", h2h_hdr, _h2h_rows(p), [p],
            "GSK/DT-GSK columns of the descriptive_stats bundle (cec2011, best_fitness basis)")
    for i, dim in enumerate([10, 30, 50, 100], start=2):
        p = OUT_ROOT / "cec2017" / f"descriptive_stats_cec2017_D{dim}.csv"
        _export(f"T{i}.csv", h2h_hdr, _h2h_rows(p), [p],
                f"GSK/DT-GSK columns of the descriptive_stats bundle (cec2017 D{dim})")

    # T6: cec2011 Wilcoxon summary (GSK vs DT-GSK)
    ph = OUT_ROOT / "cec2011" / "wilcoxon_holm_cec2011.csv"
    pd_ = OUT_ROOT / "cec2011" / "descriptive_stats_cec2011.csv"
    wh = {r["comparator"]: r for r in _bundle_csv(ph)}
    desc = _bundle_csv(pd_)
    mi = {int(r["function"]): float(r["mean"]) for r in desc if r["algorithm"] == PROPOSED}
    mg = {int(r["function"]): float(r["mean"]) for r in desc if r["algorithm"] == "gsk"}
    rp, rm = _rank_sums_from_means(mi, mg, CEC2011_PROBS)
    w, t, lo = wtl_means(mi, mg, CEC2011_PROBS)
    dec = {"win": "+", "tie": "=", "loss": "-"}[wh["gsk"]["outcome"]]
    rows = [["R+", f"{rp:.10g}"], ["R-", f"{rm:.10g}"],
            ["p_value", f"{float(wh['gsk']['p_raw']):.10g}"],
            ["p_holm", f"{float(wh['gsk']['p_holm']):.10g}"],
            ["Wins(+)", str(w)], ["Ties(=)", str(t)], ["Losses(-)", str(lo)],
            ["Decision", dec]]
    _export("T6.csv", ["Metric", "Value"], rows, [ph, pd_],
            "GSK row of wilcoxon_holm_cec2011 + R+/R- and W/T/L re-derived from the "
            "descriptive_stats means (R+ = rank sum favoring DT-GSK; ties |d|<1e-8 dropped)")

    # T7-T10: 7-algorithm Mean/SD comparison per dim
    for i, dim in enumerate([10, 30, 50, 100], start=7):
        p = OUT_ROOT / "cec2017" / f"descriptive_stats_cec2017_D{dim}.csv"
        data = _bundle_csv(p)
        by_func: dict[int, dict[str, dict]] = {}
        for r in data:
            by_func.setdefault(int(r["function"]), {})[r["algorithm"]] = r
        hdr = ["Func"]
        for alg in PANEL:
            hdr += [f"{DISPLAY[alg]}_Mean", f"{DISPLAY[alg]}_SD"]
        rows = []
        for f in sorted(by_func):
            row = [f"F{f}"]
            for alg in PANEL:
                row += [by_func[f][alg]["mean"], by_func[f][alg]["sd"]]
            rows.append(row)
        _export(f"T{i}.csv", hdr, rows, [p],
                f"panel Mean/SD columns of descriptive_stats bundle (cec2017 D{dim}, P1 order)")

    # T11-T13: cec2013 h2h D10/30/50
    for i, dim in enumerate([10, 30, 50], start=11):
        p = OUT_ROOT / "cec2013" / f"descriptive_stats_cec2013_D{dim}.csv"
        _export(f"T{i}.csv", h2h_hdr, _h2h_rows(p), [p],
                f"GSK/DT-GSK columns of the descriptive_stats bundle (cec2013 D{dim})")

    # T14: cec2013 Wilcoxon summary (GSK vs DT-GSK) per dim
    srcs = []
    cols: dict[str, list[str]] = {m: [] for m in
                                  ["R+", "R-", "p_value", "p_holm", "Wins(+)", "Ties(=)",
                                   "Losses(-)", "Decision"]}
    for dim in [10, 30, 50]:
        ph = OUT_ROOT / "cec2013" / f"wilcoxon_holm_cec2013_D{dim}.csv"
        pdd = OUT_ROOT / "cec2013" / f"descriptive_stats_cec2013_D{dim}.csv"
        srcs += [ph, pdd]
        wh = {r["comparator"]: r for r in _bundle_csv(ph)}
        desc = _bundle_csv(pdd)
        mi = {int(r["function"]): float(r["mean"]) for r in desc if r["algorithm"] == PROPOSED}
        mg = {int(r["function"]): float(r["mean"]) for r in desc if r["algorithm"] == "gsk"}
        rp, rm = _rank_sums_from_means(mi, mg, CEC2013_FUNCS)
        w, t, lo = wtl_means(mi, mg, CEC2013_FUNCS)
        cols["R+"].append(f"{rp:.10g}")
        cols["R-"].append(f"{rm:.10g}")
        cols["p_value"].append(f"{float(wh['gsk']['p_raw']):.10g}")
        cols["p_holm"].append(f"{float(wh['gsk']['p_holm']):.10g}")
        cols["Wins(+)"].append(str(w))
        cols["Ties(=)"].append(str(t))
        cols["Losses(-)"].append(str(lo))
        cols["Decision"].append({"win": "+", "tie": "=", "loss": "-"}[wh["gsk"]["outcome"]])
    rows = [[m] + cols[m] for m in cols]
    _export("T14.csv", ["Metric", "D10", "D30", "D50"], rows, srcs,
            "GSK rows of wilcoxon_holm_cec2013_D* + R+/R-/W-T-L re-derived from "
            "descriptive_stats means (R+ favors DT-GSK)")

    # T15: cec2017 Wilcoxon GSK-family summary (per dim x comparator)
    srcs = []
    rows = []
    per_dim: dict[int, dict] = {}
    for dim in [10, 30, 50, 100]:
        ph = OUT_ROOT / "cec2017" / f"wilcoxon_holm_cec2017_D{dim}.csv"
        pdd = OUT_ROOT / "cec2017" / f"descriptive_stats_cec2017_D{dim}.csv"
        srcs += [ph, pdd]
        wh = {r["comparator"]: r for r in _bundle_csv(ph)}
        desc = _bundle_csv(pdd)
        means = {alg: {int(r["function"]): float(r["mean"]) for r in desc
                       if r["algorithm"] == alg} for alg in PANEL}
        per_dim[dim] = {"wh": wh, "means": means}
    # M-027: the CSV carries BOTH effect sizes. The rendered table shows the
    # PAIRED one (rank-biserial r, aligned with the Wilcoxon signed-rank test it
    # accompanies); A12 is unpaired and stays in the workbook as a labelled
    # descriptive companion. The workbook is not width-constrained, so nothing
    # is lost by keeping both.
    hdr = ["Algorithm"]
    for dim in [10, 30, 50, 100]:
        hdr += [f"D{dim}_p", f"D{dim}_p_holm", f"D{dim}_W", f"D{dim}_T", f"D{dim}_L",
                f"D{dim}_A12", f"D{dim}_r", f"D{dim}_Dec"]
    for comp in COMPARATORS:
        row = [DISPLAY[comp]]
        for dim in [10, 30, 50, 100]:
            wh = per_dim[dim]["wh"][comp]
            means = per_dim[dim]["means"]
            w, t, lo = wtl_means(means[PROPOSED], means[comp], CEC2017_FUNCS)
            xa = np.array([means[PROPOSED][f] for f in CEC2017_FUNCS])
            ya = np.array([means[comp][f] for f in CEC2017_FUNCS])
            a12, _, _ = a12_band(xa, ya)
            dec = {"win": "+", "tie": "=", "loss": "-"}[wh["outcome"]]
            rb = wh.get("rank_biserial", "")
            rb_s = f"{float(rb):.10g}" if rb not in ("", NA) else NA
            row += [f"{float(wh['p_raw']):.10g}", f"{float(wh['p_holm']):.10g}",
                    str(w), str(t), str(lo), f"{a12:.10g}", rb_s, dec]
        rows.append(row)
    _export("T15.csv", hdr, rows, srcs,
            "function-level Wilcoxon+Holm rows of wilcoxon_holm_cec2017_D*; W/T/L and "
            "across-function A12 on per-function means re-derived from descriptive_stats "
            "(A12>0.5 favors DT-GSK; ties |d|<1e-8 half); r is the matched-pairs "
            "rank-biserial (R+ - R-)/(R+ + R-) carried through from the Wilcoxon rows, "
            "the effect size ALIGNED with that paired test, oriented so r>0 favors DT-GSK (the raw textbook form is negative for a DT-GSK win because the differences are errors)")

    # T16: Friedman mean ranks per dim + overall
    srcs = [OUT_ROOT / "cec2017" / f"friedman_ranks_cec2017_D{d}.csv" for d in [10, 30, 50, 100]]
    srcs.append(OUT_ROOT / "cec2017" / "friedman_ranks_cec2017_overall.csv")
    ranks: dict[str, list[str]] = {alg: [] for alg in PANEL}
    for p in srcs:
        for r in _bundle_csv(p):
            ranks[r["algorithm"]].append(f"{float(r['mean_rank']):.6f}")
    rows = [[DISPLAY[alg]] + ranks[alg] for alg in PANEL]
    _export("T16.csv", ["Algorithm", "D10_MeanRank", "D30_MeanRank", "D50_MeanRank",
                        "D100_MeanRank", "Overall_MeanRank"], rows, srcs,
            "friedman_ranks bundle transcription (P1 row order; overall = descriptive "
            "mean of per-dimension ranks, no test attached)")

    prov = {"release_id": REL_ID, "anchor_commit": ANCHOR,
            "bundle": OUT_ROOT.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix(),
            "generator": SCRIPT_REL, "command": COMMAND,
            "note": ("results/paper_tables/ is rendered-input staging exported EXCLUSIVELY "
                     "from the controlled analysis bundle (Phase 6 task 23); "
                     "T21/T22 (parametric sensitivity) NOT exported: no admissible "
                     "sensitivity release exists (EG-006)"),
            "exports": EXPORT_PROV}
    write_json(PAPER_TABLES / "provenance.json", prov, analysis_ids=["EXPORT-PROVENANCE"])


# ===========================================================================
# Cleanup of prior outputs (no mixed-provenance output directory)
# ===========================================================================
def clean_outputs() -> None:
    import shutil
    for sub in ("cec2017", "cec2013", "cec2011", "primary_stats"):
        d = OUT_ROOT / sub
        if d.exists():
            shutil.rmtree(d)
    for name in ("environment_record.json", "source_precheck.json", "cross_check.json",
                 "analysis_manifest.json", "analysis_checksums.sha256",
                 "table_to_csv_map.md", "run_manifest.json"):
        p = OUT_ROOT / name
        if p.exists():
            p.unlink()
    if PAPER_TABLES.exists():
        for p in sorted(PAPER_TABLES.glob("T*.csv")) + [PAPER_TABLES / "provenance.json"]:
            if p.exists():
                p.unlink()


# ===========================================================================
def main() -> None:
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"Phase 6 deterministic analysis driver - release {REL_ID}")
    clean_outputs()
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    print("[a] environment record")
    step_environment()

    print("[b] strict-source activation + negative tests")
    rl.clear_source_audit()
    negative = step_negative_tests()

    print("[c] source completeness pre-check (summaries)")
    pre = step_precheck_summaries(negative)

    print("[d] CURVE SELECTION (blind; summary CSVs only; before any gen_log open)")
    curve_info = step_curve_selection()

    print("[c2] source completeness pre-check (per_run row counts)")
    step_precheck_per_run(pre)

    print("[e] primary families - cec2017")
    family_descriptive("cec2017")
    family_omnibus("cec2017")
    family_pw("cec2017")
    family_global_holm_sensitivity()   # M-028; needs PW for all four dimensions
    family_pwrun("cec2017")
    family_effect("cec2017")
    family_convergence("cec2017", SUITE_DIMS["cec2017"])

    print("[e] primary families - cec2013")
    family_descriptive("cec2013")
    family_omnibus("cec2013")
    family_pw("cec2013")
    family_pwrun("cec2013")
    family_effect("cec2013")
    family_convergence("cec2013", [30])

    print("[e] primary families - cec2011")
    family_descriptive("cec2011")
    family_omnibus("cec2011")
    family_pw("cec2011")
    family_pwrun("cec2011")
    family_effect("cec2011")
    family_convergence("cec2011", [0])

    print("[e] trend / class / cost")
    family_trend_class_cost()

    print("[e] exploratory BH duplicate")
    family_exploratory_bh()

    print("[e] robustness battery r01..r08")
    robustness_battery()

    print("[e] sensitivity evidence-gap row")
    sensitivity_gap_row()

    print("[g] headline_bca.csv")
    emit_headline_bca()

    print("[f] primary_stats/statistical_results.csv")
    write_statistical_results()

    print("[h] cross-implementation verification")
    cross_check()

    finished = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print("[i] source-use logs / manifests")
    write_source_logs(started, finished)
    write_run_manifests(curve_info)
    write_table_map()

    print("[j] export T1-T16 staging CSVs -> results/paper_tables/")
    export_paper_tables()

    write_manifest_and_checksums()

    n_files = len(MANIFEST_ENTRIES)
    n_stat = len(STAT_ROWS)
    print("")
    print("PHASE 6 DRIVER COMPLETE")
    print(f"  release:            {REL_ID}")
    print(f"  output files:       {n_files} (see analysis_manifest.json)")
    print(f"  statistical rows:   {n_stat} (primary_stats/statistical_results.csv)")
    print(f"  audited opens:      {len(rl.get_source_audit())} (all under benchmarks/cec_reference_results/)")
    print(f"  negative tests:     {negative}")
    print(f"  curve selection:    {curve_info}")
    print(f"  grid mismatches:    {GRID_MISMATCHES or 'none'}")
    print(f"  notes:              {NOTES or 'none'}")


if __name__ == "__main__":
    main()
