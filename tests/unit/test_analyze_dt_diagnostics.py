"""Unit tests for scripts/analyze_dt_diagnostics.py on synthetic JSONL traces."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "analyze_dt_diagnostics",
    Path(__file__).resolve().parents[2] / "scripts" / "analyze_dt_diagnostics.py",
)
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)


def _write_run(dir_: Path, *, func, dim, run, seed, n_gens, best_curve,
               diversity, stagnation_max, restarts, suite="cec2017"):
    """Write one synthetic DTTrace JSONL file."""
    lines = []
    for g in range(1, n_gens + 1):
        frac = g / n_gens
        lines.append(json.dumps({
            "optimizer": "dt-gsk", "suite": suite, "function": func, "dimension": dim,
            "run": run, "seed": seed, "max_nfes": 100000,
            "gen": g, "evals_used": g * 1000, "budget_frac": frac,
            "best_fitness": best_curve(g, n_gens),
            "stagnation_gens": min(stagnation_max, g),
            "diversity_ratio": diversity(frac),
            "ace_entropy": 1.2 - 0.5 * frac,
            "restarts_done": restarts, "restart_triggered": False,
            "boundary_hit_rate": 0.01,
            "local_search_triggered": True,
            "local_search_evals_used": 5, "local_search_improvements": 1,
            "local_search_roi": 0.2, "delayed_reward_lag10": 0.0 if restarts == 0 else 1.0,
            "linkage_learned_rows": 10, "linkage_learned_accepted": 3,
            "linkage_random_rows": 10, "linkage_random_accepted": 2,
            "terra_linkage_reliable": True,
        }))
    (dir_ / f"DTTrace_{suite}_F{func}_D{dim}_R{run}_S{seed}.jsonl").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def _build_cell(dir_: Path):
    # Four clean runs converging to ~400, one trapped run stuck at ~8e5.
    for r in range(1, 5):
        _write_run(
            dir_, func=30, dim=10, run=r, seed=1000 + r, n_gens=20,
            best_curve=lambda g, n: 1000.0 - 600.0 * (g / n),  # -> 400
            diversity=lambda f: 0.9 - 0.4 * f, stagnation_max=2, restarts=1,
        )
    _write_run(
        dir_, func=30, dim=10, run=27, seed=87242640, n_gens=20,
        best_curve=lambda g, n: 800000.0,                      # stuck
        diversity=lambda f: 0.02 if f < 0.5 else 0.02,         # early collapse
        stagnation_max=18, restarts=0,                         # no restart
    )


def _read_csv(path: Path):
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


class TestAnalyze:
    def test_writes_all_csvs_and_flags_only_the_trap(self, tmp_path):
        inp = tmp_path / "diag"
        inp.mkdir()
        _build_cell(inp)
        out = tmp_path / "analysis"
        counts = _MOD.analyze(inp, out)

        assert counts["runs"] == 5
        for name in (
            "diagnostics_summary.csv", "wrong_basin_candidates.csv", "local_search_roi.csv",
            "ace_entropy_summary.csv", "linkage_reliability_summary.csv",
            "diversity_population_summary.csv", "boundary_hit_summary.csv",
        ):
            assert (out / name).is_file(), name

        summary = _read_csv(out / "diagnostics_summary.csv")
        assert len(summary) == 5
        flagged = [r for r in summary if r["suspected_wrong_basin"] == "1"]
        assert len(flagged) == 1
        assert flagged[0]["run"] == "27"
        assert float(flagged[0]["final_best"]) == 800000.0

        candidates = _read_csv(out / "wrong_basin_candidates.csv")
        assert len(candidates) == 1 and candidates[0]["run"] == "27"
        # a true bad-outcome signal is necessary, plus a corroborating mechanism
        reasons = candidates[0]["reasons"].split(";")
        assert "final_best>>cell_median" in reasons
        assert len(reasons) >= 2
        # the new metrics are present and computed
        row = next(r for r in summary if r["run"] == "27")
        for col in ("ls_triggers", "ls_median_roi", "ls_waste_frac", "ls_hit_rate",
                    "learned_linkage_acc_rate", "random_linkage_acc_rate", "linkage_learned_advantage"):
            assert col in row
        assert float(row["learned_linkage_acc_rate"]) == 0.3  # 3 accepted / 10 rows
        assert float(row["random_linkage_acc_rate"]) == 0.2   # 2 accepted / 10 rows

    def test_benign_signals_alone_do_not_flag(self, tmp_path):
        # Five runs that all converge to ~400 (no bad outcome) but every run has
        # an early diversity collapse and no restart -- under the old ">=2 signals"
        # rule these would be flagged; the recalibrated rule must NOT flag them.
        inp = tmp_path / "diag"
        inp.mkdir()
        for r in range(1, 6):
            _write_run(
                inp, func=12, dim=10, run=r, seed=500 + r, n_gens=20,
                best_curve=lambda g, n: 1000.0 - 600.0 * (g / n),  # -> 400, all peers
                diversity=lambda f: 0.01,                          # collapsed throughout
                stagnation_max=2, restarts=0,                      # no restart
            )
        out = tmp_path / "analysis"
        counts = _MOD.analyze(inp, out)
        assert counts["runs"] == 5
        assert counts["wrong_basin_candidates"] == 0
        assert _read_csv(out / "wrong_basin_candidates.csv") == []

    def test_metadata_from_json_not_filename(self, tmp_path):
        inp = tmp_path / "diag"
        inp.mkdir()
        _write_run(
            inp, func=5, dim=30, run=2, seed=999, n_gens=5,
            best_curve=lambda g, n: 10.0, diversity=lambda f: 0.5, stagnation_max=1, restarts=1,
        )
        # rename the file so the name no longer encodes metadata
        f = next(inp.glob("*.jsonl"))
        f.rename(inp / "renamed.jsonl")
        runs = _MOD.load_runs(inp)
        assert list(runs.keys()) == [("cec2017", 5, 30, 2, 999)]


class TestLocalSearchMetrics:
    def test_hit_rate_distinguishes_from_waste_frac(self):
        # 10 LS triggers: 9 find nothing (roi 0, improvements 0), 1 lands an
        # improvement (roi 0.5, improvements 1). The per-trigger ls_waste_frac is
        # 0.9 ("looks useless"), but ls_hit_rate is 0.1 -- LS is net-useful, not
        # wasted. This is exactly the divergence the D10 config-only ablation
        # exposed: cutting LS left waste_frac high yet did not improve error.
        records = []
        for g in range(1, 11):
            improved = g == 10
            records.append({
                "suite": "cec2017", "function": 7, "dimension": 10, "run": 1, "seed": 5,
                "gen": g, "evals_used": g * 100, "budget_frac": g / 10,
                "best_fitness": 100.0 - (1.0 if improved else 0.0),
                "local_search_triggered": True,
                "local_search_evals_used": 5,
                "local_search_improvements": 1 if improved else 0,
                "local_search_roi": 0.5 if improved else 0.0,
            })
        s = _MOD.summarize_run(("cec2017", 7, 10, 1, 5), records)
        assert s["ls_triggers"] == 10
        assert s["ls_waste_frac"] == 0.9          # 9/10 triggers had non-positive ROI
        assert abs(s["ls_hit_rate"] - 0.1) < 1e-9  # but 1/10 actually improved
        assert s["total_local_search_improvements"] == 1

    def test_hit_rate_nan_when_no_triggers(self):
        records = [{
            "suite": "cec2017", "function": 1, "dimension": 10, "run": 1, "seed": 5,
            "gen": g, "evals_used": g * 100, "budget_frac": g / 5,
            "best_fitness": 10.0, "local_search_triggered": False,
        } for g in range(1, 6)]
        s = _MOD.summarize_run(("cec2017", 1, 10, 1, 5), records)
        assert s["ls_triggers"] == 0
        assert math.isnan(s["ls_hit_rate"])


class TestNumDecoding:
    def test_non_finite_strings(self):
        assert math.isnan(_MOD._num("NaN"))
        assert _MOD._num("Infinity") == math.inf
        assert _MOD._num("-Infinity") == -math.inf
        assert _MOD._num("3.5") == 3.5
        assert math.isnan(_MOD._num(None))
