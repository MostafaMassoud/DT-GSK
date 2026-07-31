from __future__ import annotations

import importlib


def test_gsk_family_package_imports() -> None:
    import gsk_family

    assert gsk_family.__version__


def test_gsk_family_scaffold_modules_import() -> None:
    modules = [
        "gsk_family.benchmark_adapter.factory",
        "gsk_family.benchmark_adapter.problem",
        "gsk_family.benchmark_adapter.protocol",
        "gsk_family.cli.list",
        "gsk_family.cli.run",
        "gsk_family.cli.validate",
        "gsk_family.common.bounds",
        "gsk_family.common.donors",
        "gsk_family.common.numeric_compat",
        "gsk_family.common.population",
        "gsk_family.common.reduction",
        "gsk_family.common.rng",
        "gsk_family.optimizers.agsk",
        "gsk_family.optimizers.apgsk",
        "gsk_family.optimizers.atmals_gsk",
        "gsk_family.optimizers.fdb_agsk",
        "gsk_family.optimizers.gsk",
        "gsk_family.runners.config",
        "gsk_family.runners.output",
        "gsk_family.runners.parallel",
        "gsk_family.runners.performance",
        "gsk_family.runners.run_experiment",
        "gsk_family.runners.seed_policy",
        "gsk_family.runners.verification",
        "gsk_family.stats",
        "gsk_family.types",
    ]

    for module in modules:
        importlib.import_module(module)


def test_python_benchmark_suites_import() -> None:
    modules = [
        "benchmarks.cec_suite_python.cec2011",
        "benchmarks.cec_suite_python.cec2013",
        "benchmarks.cec_suite_python.cec2013lsgo",
        "benchmarks.cec_suite_python.cec2017",
        "benchmarks.cec_suite_python.cec2020",
    ]

    for module in modules:
        importlib.import_module(module)


def test_unified_seed_example() -> None:
    from gsk_family.runners.seed_policy import get_cec_seed

    assert get_cec_seed(20240620, 30, 7, 12) == 69241386
