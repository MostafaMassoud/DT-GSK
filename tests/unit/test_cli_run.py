from __future__ import annotations

from argparse import Namespace

import pytest

from gsk_family.cli.run import _direct_config


def _args(**overrides: object) -> Namespace:
    """Build a direct-run CLI namespace for unit tests."""
    defaults: dict[str, object] = {
        "config": None,
        "root": ".",
        "optimizer": ["gsk,agsk,apgsk,fdb-agsk,atmals-gsk"],
        "suite": "cec2017",
        "functions": ["1:30"],
        "dimension": ["10,30,50,100"],
        "runs": 51,
        "seed": None,
        "seed_policy": None,
        "rand_generator": None,
        "max_evaluations": None,
        "output_root": None,
        "reference_root": None,
        "data_root": None,
        "overwrite": False,
        "parallel": False,
        "serial": False,
        "parallel_backend": None,
        "workers": None,
        "numba_threads": None,
        "warmup": False,
        "warmup_scope": None,
        "profile": False,
        "console_log": False,
        "quiet": False,
        "generation_logs": False,
        "no_generation_logs": False,
        "convergence_graphs": False,
        "no_convergence_graphs": False,
        "stats": False,
        "benchmark_fp_mode": None,
        "benchmark_backend": None,
    }
    defaults.update(overrides)
    return Namespace(**defaults)


def test_direct_cli_expands_ranges_for_simple_cec2017_campaign() -> None:
    mapping = _direct_config(_args())

    assert mapping["optimizers"] == ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk"]
    assert mapping["suite"] == "cec2017"
    assert mapping["functions"] == [1, *range(3, 31)]
    assert mapping["dimensions"] == [10, 30, 50, 100]
    assert mapping["runs"] == 51
    assert "parallel" not in mapping
    assert "workers" not in mapping
    assert mapping["output_root"] == "results/_run_all"


def test_direct_cli_can_override_default_parallel_workers() -> None:
    mapping = _direct_config(_args(parallel=True, workers=12))

    assert mapping["parallel"] is True
    assert mapping["workers"] == 12


def test_direct_cli_accepts_native_dimension_keyword_for_cec2011() -> None:
    mapping = _direct_config(
        _args(
            suite="cec2011",
            functions=["1:22"],
            dimension=["native"],
            runs=25,
        )
    )

    assert mapping["suite"] == "cec2011"
    assert mapping["functions"] == list(range(1, 23))
    assert mapping["dimensions"] == "native"
    assert mapping["runs"] == 25


def test_direct_cli_accepts_numba_threads_override() -> None:
    mapping = _direct_config(_args(numba_threads=2))

    assert mapping["numba_threads"] == 2


def test_direct_cli_quiet_disables_default_console_log() -> None:
    mapping = _direct_config(_args(quiet=True))

    assert mapping["console_log"] is False


def test_direct_cli_can_disable_default_generation_logs() -> None:
    mapping = _direct_config(_args(no_generation_logs=True))

    assert mapping["generation_logs"] is False


def test_direct_cli_can_disable_default_convergence_graphs() -> None:
    mapping = _direct_config(_args(no_convergence_graphs=True))

    assert mapping["convergence_graphs"] is False


def test_direct_cli_can_force_default_convergence_graphs() -> None:
    mapping = _direct_config(_args(convergence_graphs=True))

    assert mapping["convergence_graphs"] is True


def test_direct_cli_accepts_benchmark_fp_mode() -> None:
    mapping = _direct_config(_args(benchmark_fp_mode="strict"))

    assert mapping["benchmark_fp_mode"] == "strict"


def test_direct_cli_rejects_invalid_ranges() -> None:
    with pytest.raises(SystemExit, match="function range start"):
        _direct_config(_args(functions=["30:1"]))


def test_direct_cli_rejects_mixed_dimension_keyword_and_numbers() -> None:
    with pytest.raises(SystemExit, match="dimension keywords"):
        _direct_config(_args(dimension=["native,10"]))
