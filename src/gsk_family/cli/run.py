"""Run experiments from the Python GSK package."""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
from typing import cast

from gsk_family.benchmark_adapter.protocol import normalize_suite
from gsk_family.runners.config import ExperimentConfig, load_config
from gsk_family.runners.run_experiment import run_experiment


def _comma_or_repeat(values: list[str] | None) -> list[str] | None:
    """Normalize repeated or comma-separated CLI values."""
    if not values:
        return None
    out: list[str] = []
    for value in values:
        out.extend(part for part in value.split(",") if part)
    return out


def _expand_positive_int_selector(token: str, *, name: str) -> list[int]:
    """Expand one positive-integer selector token.

    Selectors accept either a single integer (``7``) or an inclusive range
    (``1:30``). Ranges are intentionally simple so command-line experiments
    remain explicit and reproducible.
    """
    text = token.strip()
    if ":" not in text:
        value = int(text)
        if value <= 0:
            raise ValueError(f"{name} values must be positive integers.")
        return [value]

    parts = text.split(":")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f"{name} range must use START:STOP syntax, got {token!r}.")
    start = int(parts[0])
    stop = int(parts[1])
    if start <= 0 or stop <= 0:
        raise ValueError(f"{name} range endpoints must be positive integers.")
    if start > stop:
        raise ValueError(f"{name} range start must be <= stop, got {token!r}.")
    return list(range(start, stop + 1))


def _positive_int_selectors(
    values: list[str] | None,
    *,
    default: str,
    name: str,
) -> list[int]:
    """Normalize repeated, comma-separated, and ranged integer selectors."""
    selected: list[int] = []
    for token in _comma_or_repeat(values) or [default]:
        try:
            selected.extend(_expand_positive_int_selector(token, name=name))
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
    return selected


def _dimension_selectors(values: list[str] | None, *, default: str) -> list[int] | str:
    """Normalize CLI dimension selectors, including native/default/all keywords."""
    tokens = _comma_or_repeat(values)
    if not tokens:
        return _positive_int_selectors(None, default=default, name="dimension")

    keywords = {"native", "default", "all"}
    normalized = [token.strip().lower() for token in tokens]
    keyword_tokens = [token for token in normalized if token in keywords]
    if keyword_tokens:
        if len(tokens) != 1 or normalized[0] not in keywords:
            raise SystemExit("dimension keywords native/default/all cannot be combined with numeric dimensions.")
        return normalized[0]
    return _positive_int_selectors(values, default=default, name="dimension")


def _cec2017_run_all_functions(suite: str, functions: list[int]) -> list[int]:
    """Mirror the run-all CEC2017 policy by excluding withdrawn F2 from 1:30."""
    if normalize_suite(suite) == "cec2017" and functions == list(range(1, 31)):
        return [func for func in functions if func != 2]
    return functions


def _rooted(root: Path, value: str) -> str:
    """Resolve a config path relative to a CLI root when it is not absolute."""
    path = Path(value)
    if path.is_absolute():
        return str(path)
    return str(root / path)


def _apply_root(config: ExperimentConfig, root: str | None) -> ExperimentConfig:
    """Apply a base root to all path fields in an experiment config."""
    if not root:
        return config
    base = Path(root)
    return replace(
        config,
        data_root=_rooted(base, config.data_root),
        reference_root=_rooted(base, config.reference_root),
        output_root=_rooted(base, config.output_root),
    )


def _build_parser() -> argparse.ArgumentParser:
    """Build the `gsk-run` argument parser."""
    parser = argparse.ArgumentParser(description="Run GSK-family Python experiments.")
    parser.add_argument("--config", help="YAML config file.")
    parser.add_argument("--root", default=None, help="Base path for relative config roots.")
    parser.add_argument("--optimizer", action="append", help="Optimizer id; repeat or comma-separate.")
    parser.add_argument("--suite", help="Benchmark suite.")
    parser.add_argument(
        "--dimension",
        "--dimensions",
        action="append",
        help="Dimension selector; repeat, comma-separate, use START:STOP, or use native/default/all.",
    )
    parser.add_argument(
        "--function",
        "--functions",
        dest="functions",
        action="append",
        help="Function selector; repeat, comma-separate, or use START:STOP.",
    )
    parser.add_argument("--runs", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--seed-policy", default=None)
    parser.add_argument("--rand-generator", default=None)
    parser.add_argument("--max-evaluations", type=int, default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--reference-root", default=None)
    parser.add_argument("--data-root", default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--parallel", action="store_true")
    parser.add_argument("--serial", action="store_true", help="Disable default parallel execution.")
    parser.add_argument(
        "--parallel-backend",
        choices=("process", "thread"),
        default=None,
        help="Parallel backend. 'process' (default) uses true multi-core workers; "
        "'thread' is GIL-bound and mainly for tiny/debug runs.",
    )
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument(
        "--numba-threads",
        type=int,
        default=None,
        help="Numba threads per process. Default 0/omitted auto-caps threads for parallel runs.",
    )
    parser.add_argument("--warmup", action="store_true")
    parser.add_argument(
        "--warmup-scope",
        choices=("selected", "suite"),
        default=None,
        help="Warm only selected cells or every default cell in the suite.",
    )
    parser.add_argument("--profile", action="store_true")
    parser.add_argument(
        "--console-log",
        action="store_true",
        help="Force console progress logging on.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable default console progress logging.",
    )
    parser.add_argument(
        "--generation-logs",
        action="store_true",
        help="Force per-checkpoint generation log CSVs on.",
    )
    parser.add_argument(
        "--no-generation-logs",
        action="store_true",
        help="Disable default per-checkpoint generation log CSVs.",
    )
    parser.add_argument(
        "--dt-diagnostics",
        action="store_true",
        help=(
            "Enable DT-GSK per-generation state telemetry (one JSONL trace per "
            "cell: operator-credit/ACE entropy, tier activity, realized "
            "population schedule, restart and local-search events). "
            "Observational only -- draws no RNG and never affects the optimizer "
            "config or its hash, so results stay byte-identical. DT-GSK only; "
            "off by default because traces are large (see --dt-diagnostics-all-fields)."
        ),
    )
    parser.add_argument(
        "--no-dt-diagnostics",
        action="store_true",
        help="Disable DT-GSK per-generation state telemetry.",
    )
    parser.add_argument(
        "--dt-diagnostics-all-fields",
        action="store_true",
        help=(
            "With --dt-diagnostics, record the FULL per-generation log (~127 "
            "fields, about 4x larger) instead of the default compact "
            "root-cause subset. The compact subset already carries every field "
            "the paper's adaptation figures use."
        ),
    )
    parser.add_argument(
        "--convergence-graphs",
        action="store_true",
        help="Generate convergence graph PNG files.",
    )
    parser.add_argument(
        "--no-convergence-graphs",
        action="store_true",
        help="Disable convergence graph PNG generation; curve CSV files are still written.",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        default=False,
        help="Print per-dimension Wilcoxon+Friedman statistical analysis during the run.",
    )
    parser.add_argument(
        "--benchmark-fp-mode",
        choices=("default", "strict"),
        default=None,
        help="Benchmark floating-point mode. 'strict' uses fixed-order CEC2017 F1/F12/F13 evaluation.",
    )
    parser.add_argument(
        "--benchmark-backend",
        choices=("auto", "python"),
        default=None,
        help="Benchmark evaluator backend. 'auto' and 'python' both use the Python evaluator.",
    )
    return parser


def _direct_config(args: argparse.Namespace) -> dict[str, object]:
    """Create an experiment mapping from direct CLI arguments."""
    if not args.suite:
        raise SystemExit("--suite is required when --config is not provided.")
    # Omitting --functions / --dimension means "the whole suite, as the suite
    # defines it", NOT function 1 at D=10. The old defaults ("1" and "10") made a
    # bare `run.py --optimizer X --suite Y` quietly execute a single cell and then
    # print PASS, which is indistinguishable from a completed sweep in the console
    # output. Deferring to the keyword lets runners/config.py resolve per suite:
    # cec2017 -> 29 functions (F2 excluded), cec2013 -> 28, cec2011 -> 22,
    # cec2020 -> 10, cec2013lsgo -> 15 at NATIVE dimensions (905 for F13/F14).
    if args.functions:
        functions: object = _cec2017_run_all_functions(
            args.suite, _positive_int_selectors(args.functions, default="1", name="function")
        )
    else:
        functions = "default"
    mapping: dict[str, object] = {
        "optimizers": _comma_or_repeat(args.optimizer) or ["gsk"],
        "suite": args.suite,
        "functions": functions,
        "dimensions": _dimension_selectors(args.dimension, default="default")
        if args.dimension
        else "default",
        "data_root": "benchmarks/cec_suite_python",
        "reference_root": "benchmarks/cec_reference_results",
        "output_root": "results/_run_all",
    }
    if args.runs is not None:
        mapping["runs"] = args.runs
    if args.seed is not None:
        mapping["seed"] = args.seed
    if args.seed_policy is not None:
        mapping["seed_policy"] = args.seed_policy
    if args.rand_generator is not None:
        mapping["rand_generator"] = args.rand_generator
    if args.max_evaluations is not None:
        mapping["max_evaluations"] = args.max_evaluations
    if args.output_root is not None:
        mapping["output_root"] = args.output_root
    if args.reference_root is not None:
        mapping["reference_root"] = args.reference_root
    if args.data_root is not None:
        mapping["data_root"] = args.data_root
    if args.overwrite:
        mapping["overwrite"] = True
    if args.serial:
        mapping["parallel"] = False
    if args.parallel:
        mapping["parallel"] = True
    if args.parallel_backend is not None:
        mapping["parallel_backend"] = args.parallel_backend
    if args.workers is not None:
        mapping["workers"] = args.workers
    if args.numba_threads is not None:
        mapping["numba_threads"] = args.numba_threads
    if args.warmup:
        mapping["warmup"] = True
    if args.warmup_scope is not None:
        mapping["warmup_scope"] = args.warmup_scope
    if args.profile:
        mapping["profile"] = True
    if args.quiet:
        mapping["console_log"] = False
    if args.console_log:
        mapping["console_log"] = True
    if args.generation_logs:
        mapping["generation_logs"] = True
    if args.no_generation_logs:
        mapping["generation_logs"] = False
    if _dt_diagnostics_requested(args):
        mapping["optimizer_options"] = _apply_dt_diagnostics(
            cast("dict[str, object] | None", mapping.get("optimizer_options")), args
        )
    if args.convergence_graphs:
        mapping["convergence_graphs"] = True
    if args.no_convergence_graphs:
        mapping["convergence_graphs"] = False
    if args.stats:
        mapping["statistical_analysis"] = True
    if args.benchmark_fp_mode is not None:
        mapping["benchmark_fp_mode"] = args.benchmark_fp_mode
    if args.benchmark_backend is not None:
        mapping["benchmark_backend"] = args.benchmark_backend
    return mapping


def _dt_diagnostics_requested(args: argparse.Namespace) -> bool:
    """True when any DT-GSK telemetry switch was given on the command line."""
    return bool(
        getattr(args, "dt_diagnostics", False)
        or getattr(args, "no_dt_diagnostics", False)
        or getattr(args, "dt_diagnostics_all_fields", False)
    )


def _apply_dt_diagnostics(
    options: dict[str, object] | None, args: argparse.Namespace
) -> dict[str, object]:
    """Merge the DT-GSK telemetry switches into an ``optimizer_options`` mapping.

    These keys are runner/adapter-level ONLY: they are not ``DTGSKConfig``
    fields and never enter the optimizer config or its hash, so enabling
    telemetry leaves the numerics byte-identical (the core's
    ``generation_callback`` is observational -- it draws no RNG and evaluates
    no objective).
    """
    opts = dict(options or {})
    if getattr(args, "no_dt_diagnostics", False):
        opts["dt_diagnostics"] = False
    elif getattr(args, "dt_diagnostics", False):
        opts["dt_diagnostics"] = True
        opts["dt_diagnostics_include_all_fields"] = bool(
            getattr(args, "dt_diagnostics_all_fields", False)
        )
    elif getattr(args, "dt_diagnostics_all_fields", False):
        opts["dt_diagnostics_include_all_fields"] = True
    return opts


def main(argv: list[str] | None = None) -> int:
    """Run configured experiments."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.parallel and args.serial:
        parser.error("--parallel and --serial cannot be used together.")
    if args.console_log and args.quiet:
        parser.error("--console-log and --quiet cannot be used together.")
    if args.generation_logs and args.no_generation_logs:
        parser.error("--generation-logs and --no-generation-logs cannot be used together.")
    if args.convergence_graphs and args.no_convergence_graphs:
        parser.error("--convergence-graphs and --no-convergence-graphs cannot be used together.")

    if args.config:
        config = load_config(args.config)
        config = _apply_root(config, args.root)
        # Experiment-shape CLI flags compose ON TOP of --config. Previously these
        # were silently dropped in the --config path, so e.g.
        #   --config lsgo.yml --max-evaluations 30000 --functions 1 --runs 1
        # ran the config's FULL budget over ALL functions instead of the intended
        # smoke -- a genuine footgun. Selectors reuse the no-config helpers so the
        # override semantics are identical to the direct-CLI path.
        if args.functions is not None:
            funcs = _cec2017_run_all_functions(
                config.suite,
                _positive_int_selectors(args.functions, default="1", name="function"),
            )
            config = replace(config, functions=tuple(funcs))
        if args.dimension is not None:
            dims = _dimension_selectors(args.dimension, default="10")
            config = replace(config, dimensions=dims if isinstance(dims, str) else tuple(dims))
        if args.runs is not None:
            config = replace(config, runs=args.runs)
        if args.max_evaluations is not None:
            config = replace(config, max_evaluations=args.max_evaluations)
        if args.seed is not None:
            config = replace(config, seed=args.seed)
        if args.seed_policy is not None:
            config = replace(config, seed_policy=args.seed_policy)
        if args.rand_generator is not None:
            config = replace(config, rand_generator=args.rand_generator)
        if args.data_root is not None:
            config = replace(config, data_root=args.data_root)
        if args.reference_root is not None:
            config = replace(config, reference_root=args.reference_root)
        if args.output_root:
            config = replace(config, output_root=args.output_root)
        if args.overwrite:
            config = replace(config, overwrite=True)
        if args.serial:
            config = replace(config, parallel=False)
        if args.parallel:
            config = replace(config, parallel=True)
        if args.parallel_backend is not None:
            config = replace(config, parallel_backend=args.parallel_backend)
        if args.workers is not None:
            config = replace(config, workers=args.workers, workers_auto=False)
        if args.numba_threads is not None:
            config = replace(config, numba_threads=args.numba_threads)
        if args.warmup:
            config = replace(config, warmup=True)
        if args.warmup_scope is not None:
            config = replace(config, warmup_scope=args.warmup_scope)
        if args.profile:
            config = replace(config, profile=True)
        if args.quiet:
            config = replace(config, console_log=False)
        if args.console_log:
            config = replace(config, console_log=True)
        if args.generation_logs:
            config = replace(config, generation_logs=True)
        if args.no_generation_logs:
            config = replace(config, generation_logs=False)
        if _dt_diagnostics_requested(args):
            config = replace(
                config,
                optimizer_options=_apply_dt_diagnostics(config.optimizer_options, args),
            )
        if args.convergence_graphs:
            config = replace(config, convergence_graphs=True)
        if args.no_convergence_graphs:
            config = replace(config, convergence_graphs=False)
        if args.stats:
            config = replace(config, statistical_analysis=True)
        if args.benchmark_fp_mode is not None:
            config = replace(config, benchmark_fp_mode=args.benchmark_fp_mode)
        if args.benchmark_backend is not None:
            config = replace(config, benchmark_backend=args.benchmark_backend)
        run_experiment(config)
        return 0

    mapping = _direct_config(args)
    if args.root:
        root = Path(args.root)
        for key in ("data_root", "reference_root", "output_root"):
            if key in mapping:
                mapping[key] = _rooted(root, str(mapping[key]))

    run_experiment(mapping)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
