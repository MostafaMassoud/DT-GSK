"""Unit tests for the opt-in DT-GSK per-generation diagnostics (Wave 1).

Diagnostics are default-off and observational: enabling them streams the core's
``DTGSKGenerationLog`` telemetry to a JSONL file without altering RNG order,
evaluations, or the returned result for a given seed.
"""

from __future__ import annotations

import json

import numpy as np

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.optimizers.dt_gsk import _sanitize_json_value, optimize
from gsk_family.types import OptimizerOptions


def _problem():
    return make_problem("cec2017", 5, dim=10, max_nfes_override=2000)


class TestDisabledIsBehaviorPreserving:
    def test_disabled_matches_no_options(self):
        prob = _problem()
        a = optimize(prob, OptimizerOptions(seed=12345, rand_generator="threefry"))
        b = optimize(
            _problem(),
            OptimizerOptions(seed=12345, rand_generator="threefry", values={"dt_diagnostics": False}),
        )
        assert a.best_fitness == b.best_fitness
        assert a.error == b.error
        assert a.nfes == b.nfes
        assert a.termination == b.termination
        assert np.array_equal(a.convergence.nfes, b.convergence.nfes)
        assert np.array_equal(a.convergence.best_fitness, b.convergence.best_fitness)

    def test_enabled_is_numerically_identical_to_disabled(self, tmp_path):
        # The strong guarantee: turning diagnostics ON must not perturb numerics.
        off = optimize(_problem(), OptimizerOptions(seed=777, rand_generator="threefry"))
        on = optimize(
            _problem(),
            OptimizerOptions(
                seed=777, rand_generator="threefry",
                values={"dt_diagnostics": True, "dt_diagnostics_dir": str(tmp_path), "dt_diagnostics_run": 3},
            ),
        )
        assert on.best_fitness == off.best_fitness
        assert on.error == off.error
        assert on.nfes == off.nfes
        assert on.termination == off.termination
        assert np.array_equal(on.convergence.nfes, off.convergence.nfes)
        assert np.array_equal(on.convergence.best_fitness, off.convergence.best_fitness)


class TestEnabledWritesDiagnostics:
    def test_one_parseable_jsonl_per_cell(self, tmp_path):
        prob = _problem()
        result = optimize(
            prob,
            OptimizerOptions(
                seed=12345, rand_generator="threefry",
                values={"dt_diagnostics": True, "dt_diagnostics_dir": str(tmp_path), "dt_diagnostics_run": 1},
            ),
        )
        files = list(tmp_path.glob("*.jsonl"))
        assert len(files) == 1
        assert files[0].name == "DTTrace_cec2017_F5_D10_R1_S12345.jsonl"

        lines = files[0].read_text(encoding="utf-8").splitlines()
        assert len(lines) >= 1
        first = json.loads(lines[0])
        for key in ("optimizer", "suite", "function", "dimension", "run", "seed", "max_nfes"):
            assert key in first
        assert first["suite"] == "cec2017" and first["function"] == 5 and first["dimension"] == 10
        assert first["seed"] == 12345
        for key in ("gen", "evals_used", "best_fitness", "ace_entropy", "diversity_ratio"):
            assert key in first

        last = json.loads(lines[-1])
        assert last["best_fitness"] == result.best_fitness
        assert result.nfes <= prob.max_nfes

    def test_disabled_writes_nothing(self, tmp_path):
        optimize(
            _problem(),
            OptimizerOptions(
                seed=1, rand_generator="threefry",
                values={"dt_diagnostics": False, "dt_diagnostics_dir": str(tmp_path)},
            ),
        )
        assert list(tmp_path.glob("*.jsonl")) == []

    def test_compact_subset_when_include_all_false(self, tmp_path):
        optimize(
            _problem(),
            OptimizerOptions(
                seed=2, rand_generator="threefry",
                values={
                    "dt_diagnostics": True, "dt_diagnostics_dir": str(tmp_path),
                    "dt_diagnostics_run": 1, "dt_diagnostics_include_all_fields": False,
                },
            ),
        )
        rec = json.loads(next(tmp_path.glob("*.jsonl")).read_text(encoding="utf-8").splitlines()[0])
        assert "gen" in rec and "ace_entropy" in rec
        # a full-only field should be absent in the compact subset
        assert "ace_sample_counts" not in rec


class TestSanitizeJsonValue:
    def test_non_finite_floats_become_strings(self):
        assert _sanitize_json_value(float("nan")) == "NaN"
        assert _sanitize_json_value(float("inf")) == "Infinity"
        assert _sanitize_json_value(float("-inf")) == "-Infinity"

    def test_numpy_and_containers(self):
        assert _sanitize_json_value(np.int64(5)) == 5
        assert _sanitize_json_value(np.float64(1.5)) == 1.5
        assert _sanitize_json_value(np.bool_(True)) is True
        assert _sanitize_json_value(np.array([1.0, 2.0])) == [1.0, 2.0]
        assert _sanitize_json_value((1, 2)) == [1, 2]
        out = _sanitize_json_value({"a": np.int64(1), "b": (np.float64(2.0),)})
        assert out == {"a": 1, "b": [2.0]}
        # the sanitized output must be json-serializable
        json.dumps(out)
