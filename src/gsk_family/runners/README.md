# Runners

The runners package owns experiment orchestration and generated artifacts.

## Files

| File | Purpose |
|---|---|
| `config.py` | YAML and mapping normalization into `ExperimentConfig`. |
| `fp_regime.py` | Fail-closed floating-point-regime sentinel guard (see [`docs/reference/fp_regime.md`](../../../docs/reference/fp_regime.md)). |
| `output.py` | Per-run, summary, curve, log, environment, and profile writers. |
| `parallel.py` | Run-task dispatch: local thread pool, or a caller-owned process pool for the process backend. |
| `performance.py` | Benchmark warmup and profile serialization helpers. |
| `run_experiment.py` | Main experiment orchestration. |
| `seed_policy.py` | Seed formulas, fair-start schedules, and generator policy. |
| `verification.py` | Reference-table loading and generated-output comparison. |

Runner code can import optimizers and benchmark adapters. Optimizer modules
should not import runners.

