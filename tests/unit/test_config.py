from __future__ import annotations

from pathlib import Path

import pytest

from gsk_family.runners.config import config_from_mapping, load_config
from gsk_family.runners.parallel import default_worker_count, effective_worker_count


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_config_rejects_unknown_keys() -> None:
    with pytest.raises(ValueError, match="Unknown config key"):
        config_from_mapping({"suite": "sphere", "mystery": True})


def test_config_resolves_default_functions_and_dimensions() -> None:
    config = config_from_mapping(
        {
            "optimizers": ["gsk"],
            "suite": "cec2017",
            "functions": "default",
            "dimensions": [10],
            "runs": 2,
        }
    )

    assert config.functions[0] == 1
    assert 2 not in config.functions
    assert config.dimensions == (10,)
    assert config.runs == 2
    assert config.parallel is True
    assert config.workers == default_worker_count()
    assert config.workers_auto is True
    assert config.convergence_graphs is False


def test_default_worker_count_uses_safe_two_worker_baseline() -> None:
    assert default_worker_count(20) == 2
    assert default_worker_count(10) == 2
    assert default_worker_count(2) == 2
    assert default_worker_count(1) == 1
    assert default_worker_count(0) == 1


def test_effective_worker_count_caps_automatic_cec2017_composition_cells() -> None:
    assert (
        effective_worker_count(
            13,
            suite="cec2017",
            function=1,
            parallel=True,
            parallel_backend="process",
            workers_auto=True,
        )
        == 13
    )
    assert (
        effective_worker_count(
            13,
            suite="cec2017",
            function=21,
            parallel=True,
            parallel_backend="process",
            workers_auto=True,
        )
        == 8
    )
    assert (
        effective_worker_count(
            13,
            suite="cec2017",
            function=21,
            parallel=True,
            parallel_backend="process",
            workers_auto=False,
        )
        == 13
    )
    assert (
        effective_worker_count(
            13,
            suite="sphere",
            function=1,
            parallel=True,
            parallel_backend="process",
            workers_auto=True,
        )
        == 13
    )


def test_config_accepts_phase9_performance_keys() -> None:
    config = config_from_mapping(
        {
            "optimizers": ["gsk"],
            "suite": "sphere",
            "functions": [1],
            "dimensions": [4],
            "runs": 1,
            "parallel": True,
            "parallel_backend": "thread",
            "workers": 2,
            "numba_threads": 1,
            "warmup": True,
            "warmup_scope": "suite",
            "profile": True,
            "console_log": False,
            "generation_logs": True,
            "convergence_graphs": False,
            "benchmark_fp_mode": "strict",
        }
    )

    assert config.parallel is True
    assert config.parallel_backend == "thread"
    assert config.workers == 2
    assert config.workers_auto is False
    assert config.numba_threads == 1
    assert config.warmup is True
    assert config.warmup_scope == "suite"
    assert config.profile is True
    assert config.console_log is False
    assert config.generation_logs is True
    assert config.convergence_graphs is False
    assert config.benchmark_fp_mode == "strict"


def test_config_rejects_bad_performance_keys() -> None:
    with pytest.raises(ValueError, match="workers"):
        config_from_mapping({"suite": "sphere", "workers": 0})
    with pytest.raises(ValueError, match="numba_threads"):
        config_from_mapping({"suite": "sphere", "numba_threads": -1})
    with pytest.raises(ValueError, match="parallel_backend"):
        config_from_mapping({"suite": "sphere", "parallel_backend": "mpi"})
    with pytest.raises(ValueError, match="warmup_scope"):
        config_from_mapping({"suite": "sphere", "warmup_scope": "everything"})
    with pytest.raises(ValueError, match="benchmark_fp_mode"):
        config_from_mapping({"suite": "sphere", "benchmark_fp_mode": "wild"})


def test_load_config_requires_yaml_mapping(tmp_path) -> None:
    path = tmp_path / "bad.yml"
    path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(ValueError, match="mapping"):
        load_config(path)


def test_all_optimizer_review_configs_load() -> None:
    smoke = load_config(PROJECT_ROOT / "configs" / "all_optimizers_smoke.yml")
    reduced = load_config(PROJECT_ROOT / "configs" / "all_optimizers_cec2017_reduced.yml")
    phase18 = load_config(PROJECT_ROOT / "configs" / "golden_validation_smoke.yml")
    phase19 = load_config(PROJECT_ROOT / "configs" / "performance_campaign_smoke.yml")

    assert smoke.optimizers == ("gsk", "agsk", "apgsk", "atmals-gsk", "fdb-agsk")
    assert smoke.suite == "sphere"
    assert smoke.parallel is True
    assert smoke.profile is True
    assert reduced.suite == "cec2017"
    assert reduced.max_evaluations == 1000
    assert phase18.suite == "cec2017"
    assert phase18.profile is True
    assert phase19.suite == "sphere"
    assert phase19.runs == 3
