from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from gsk_family.common.numeric_compat import (
    compat_round_int,
    one_based_to_zero_based,
    stable_argsort,
)
from gsk_family.common.rng import RandomContext
from gsk_family.runners.run_experiment import run_experiment


def _sphere_config(output_root: Path, reference_root: Path) -> dict[str, object]:
    return {
        "optimizers": ["gsk"],
        "suite": "sphere",
        "functions": [1],
        "dimensions": [4],
        "runs": 2,
        "seed": 20240620,
        "seed_policy": "unified",
        "rand_generator": "threefry",
        "max_evaluations": 80,
        "overwrite": True,
        "parallel": False,
        "generation_logs": True,
        "data_root": str(output_root.parent / "cec_suite_python"),
        "reference_root": str(reference_root),
        "output_root": str(output_root),
        "optimizer_options": {"np": 20},
    }


def test_python_replay_exact_for_numeric_runner_artifacts(tmp_path: Path) -> None:
    ref_root = tmp_path / "references"
    out_a = tmp_path / "run_a"
    out_b = tmp_path / "run_b"

    run_experiment(_sphere_config(out_a, ref_root))
    run_experiment(_sphere_config(out_b, ref_root))

    root_a = out_a / "gsk" / "sphere"
    root_b = out_b / "gsk" / "sphere"
    deterministic_files = [
        Path("summary") / "gsk_sphere_D4.csv",
        Path("summary") / "seed_schedule.csv",
        Path("gen_logs") / "CheckpointErrors_gsk_F1_D4.csv",
    ]
    for relative in deterministic_files:
        assert (root_a / relative).read_bytes() == (root_b / relative).read_bytes()

    curves_a = sorted((root_a / "curves").glob("Figure_F1_D4_Run#*.csv"))
    curves_b = sorted((root_b / "curves").glob("Figure_F1_D4_Run#*.csv"))
    assert [path.name for path in curves_a] == [path.name for path in curves_b]
    assert curves_a[0].read_bytes() == curves_b[0].read_bytes()


def test_tiny_cec2017_reference_comparison_regression(tmp_path: Path) -> None:
    config = {
        "optimizers": ["gsk"],
        "suite": "cec2017",
        "functions": [1],
        "dimensions": [10],
        "runs": 1,
        "seed": 20240620,
        "seed_policy": "unified",
        "rand_generator": "threefry",
        "max_evaluations": 120,
        "overwrite": True,
        "parallel": False,
        "data_root": "benchmarks/cec_suite_python",
        "reference_root": "benchmarks/cec_reference_results",
        "output_root": str(tmp_path / "results"),
        "optimizer_options": {"np": 20},
    }

    run_experiment(config)

    verification_path = tmp_path / "results" / "gsk" / "cec2017" / "summary" / "verification.json"
    payload = json.loads(verification_path.read_text(encoding="utf-8"))
    assert payload["verdict"] == "CONSISTENT"
    assert payload["reduced_budget"] is True
    assert payload["functions_checked"] == 1
    assert payload["missing_reference"] == 0
    assert payload["hard_failures"] == 0
    assert payload["win_tie_loss"][2] == 1


def test_validation_ladder_translation_traps_are_executable() -> None:
    assert compat_round_int(2.5) == 3
    np.testing.assert_array_equal(one_based_to_zero_based([1, 3]), np.array([0, 2]))
    np.testing.assert_array_equal(
        stable_argsort(np.array([2.0, 1.0, 1.0])),
        np.array([1, 2, 0]),
    )

    rng_a = RandomContext(1234, "twister")
    rng_b = RandomContext(1234, "twister")
    np.testing.assert_allclose(rng_a.random((2, 3)), rng_b.random((2, 3)))
