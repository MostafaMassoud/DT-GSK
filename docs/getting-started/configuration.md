# Configuration

> **What this page is.** A reference for configuring a run — every YAML field,
> its default, and the equivalent command-line flag.
> **Who it is for.** Anyone setting up a repeatable experiment campaign or
> tuning a single run.
> **After reading**, you will be able to write a valid config, understand each
> field's effect and default, and know when to override parallel execution.
> **Prerequisites:** you can already run the project (see the
> [Tutorial](tutorial.md)). Terms are defined in the
> [Glossary](../reference/glossary.md); seed behaviour is detailed in the
> [Seed Policy reference](../reference/seed_policy.md).

`gsk-run` accepts either a YAML configuration file or direct command-line
arguments. **Prefer YAML for campaigns** — it keeps every parameter in versioned
text, so a run is reproducible and reviewable. Use direct CLI flags for quick
one-off cells.

## Minimal YAML

A complete, valid config needs only a `suite`; everything else — including the
cells to run — has a default. This illustrative example runs one optimizer on the tiny
`sphere` problem:

```yaml
optimizers: [gsk]
suite: sphere
functions: [1]
dimensions: [4]
runs: 1
seed: 20240620
seed_policy: unified
rand_generator: threefry
max_evaluations: 120
output_root: results/_run_all
reference_root: benchmarks/cec_reference_results
data_root: benchmarks/cec_suite_python
benchmark_backend: auto
overwrite: true
convergence_graphs: false
```

Run a saved config file with:

```powershell
gsk-run --config configs/smoke.yml --root .
```

`--root .` rewrites relative `output_root`, `reference_root`, and `data_root`
values under the project root, so configs move between machines cleanly. (The
shipped `configs/smoke.yml` is a CEC2017 example and sets `parallel: false` for
a deterministic single-thread smoke; the block above is only a field
illustration.)

### Worked example: a reduced multi-optimizer config

The committed `configs/all_optimizers_cec2017_reduced.yml` shows the shape of a
real-but-fast campaign — several optimizers on one CEC2017 cell at a small
budget, with warmup, profiling, parallel `process` workers, and a shared
`optimizer_options` block:

```yaml
optimizers: [gsk, agsk, apgsk, atmals-gsk, fdb-agsk]
suite: cec2017
functions: [1]
dimensions: [10]
runs: 1
max_evaluations: 1000      # reduced budget; not a full-protocol claim
parallel: true
parallel_backend: process
workers: 2
warmup: true
profile: true
convergence_graphs: true
optimizer_options:
  np: 20
  np_init: 20
  min_pop_size: 12
  fdb_case: 1
  protocol: cec2017
```

```powershell
gsk-run --config configs/all_optimizers_cec2017_reduced.yml --root .
```

To include the proposed method, add `dt-gsk` to the `optimizers` list (it
self-initializes a `np_init_mult * D` population as a documented fair-start
exception, so it ignores the shared initial population rather than sharing it).
Full-budget statistics require the suite's full protocol budget — drop
`max_evaluations` (or set it to `0`) for a paper-grade run.

## Fields

The table lists each accepted key, its default, and what it does. Any key not
listed here is rejected, so typos fail fast rather than being silently ignored.
A mistyped key or a missing required `suite` is caught at load time with a
precise message instead of running a wrong configuration:

```text
ValueError: Unknown config key(s): optimzers.
ValueError: Config key 'suite' is required.
```

| Field | Default | Meaning |
|---|---|---|
| `optimizers` | `[gsk]` | Optimizer ids to run. Use ids from `gsk-list --optimizers`. |
| `suite` | *(required)* | Benchmark suite id: `sphere`, `cec2011`, `cec2013`, `cec2013lsgo`, `cec2017`, or `cec2020`. |
| `functions` | suite default | Function ids, or `all`. For CEC2017 the run-all default (1:30) excludes withdrawn F2. |
| `dimensions` | suite default | Dimension ids, or `native` for native-dimension suites. |
| `runs` | `1` | Independent runs per `(optimizer, dimension, function)` cell. |
| `seed` | `20240620` | Base integer seed. |
| `seed_policy` | `unified` | `unified` (default, fair cross-optimizer starts) or `reference` (reproduce published tables). Diagnostic values `native`/`derived` exist; see the [Seed Policy reference](../reference/seed_policy.md). |
| `rand_generator` | `threefry` | RNG backend label, usually `threefry` or `twister`. |
| `max_evaluations` | suite default | Optional reduced budget in NFEs. `0`/omitted uses the suite's full protocol budget. |
| `output_root` | `results/_run_all` | Generated result root. Must not be inside the reference tree. |
| `reference_root` | `benchmarks/cec_reference_results` | Imported reference-table root used by validation. |
| `data_root` | `benchmarks/cec_suite_python` | Python benchmark evaluator/data root. |
| `benchmark_backend` | `auto` | Evaluator backend. `auto` and `python` both use the Python/Numba evaluator. |
| `benchmark_fp_mode` | `default` | Benchmark floating-point regime: `default` or `strict` (see the [FP Regime reference](../reference/fp_regime.md)). |
| `overwrite` | `false` | Replace existing per-run rows for the same cells. |
| `parallel` | `true` | Dispatch independent run tasks across workers. |
| `parallel_backend` | `process` | `process` (default, true multi-core) or `thread` (GIL-bound; tiny/debug runs). |
| `workers` | `2` (`1` on a one-core machine) | Worker count for parallel runs; campaign commands should spell out `--parallel --workers 2`, and users can raise `N` explicitly when the machine has enough headroom. |
| `workers_auto` | `true` (`false` once `workers` is set) | Whether the worker count was auto-chosen; only automatic CEC2017 F21–F30 process runs are capped at 8 workers. |
| `numba_threads` | `0` (auto) | Numba threads per process. `0`/omitted auto-caps threads for parallel runs. |
| `warmup` | `false` | Preload benchmark cells before timed execution. |
| `warmup_scope` | `selected` | `selected` warms requested cells; `suite` warms the suite default grid. |
| `profile` | `false` | Write profile metadata. |
| `console_log` | `true` | Print progress to the console. |
| `generation_logs` | `true` | Write checkpoint generation-log CSV files. |
| `convergence_graphs` | `false` | Render convergence graph PNG files under `curves/graphs/` when true; curve CSV files are still written when this is false. |
| `statistical_analysis` | `false` | Stream the live per-dimension Wilcoxon + Friedman panel during the run (CLI: `--stats`). |
| `optimizer_options` | `{}` | Shared optimizer-specific options (see below). |

The defaults above are the dataclass defaults in
`src/gsk_family/runners/config.py`. The default backend is the **process** pool
and the automatic worker count is deliberately small: `2` when at least two
logical cores are available, otherwise `1`. The runbooks still show
`--parallel --workers 2` explicitly so copied campaign commands cannot
unexpectedly consume a shared workstation. For CEC2017 composition cells
(`F21`-`F30`) on the default process backend, automatic runs retain an upper cap
of 8 workers to reduce spawned-worker Numba/LLVM memory pressure if the code
default is increased in the future. The bundled smoke and validation profiles
may pin the `thread` backend (with a small worker count) for deterministic CI
artifacts.

`benchmark_backend: auto` is also the normal default. In that mode the runner
uses the Python/Numba evaluator. Set `benchmark_backend: python` only when you
want the choice recorded explicitly.

## Optimizer options

`optimizer_options` is a single shared block. Each optimizer reads only the keys
it understands and ignores the rest, which lets one all-optimizer config stay
simple while each optimizer keeps its own defaults.

```yaml
optimizer_options:
  np: 100
  np_init: 100
  min_pop_size: 12
  fdb_case: 1
  protocol: cec2017
  use_local_search: false
```

For the per-optimizer option schema and which keys each optimizer reads, see the
[Python Optimizer Interface](../reference/python_optimizer_interface.md).

### DT-GSK mechanism toggles (scaffold ablation)

Every DT-GSK scaffold mechanism defaults to `true` in the locked `pub`
profile (the SGSM interaction graph only in the `D>=50` tier), and each can be
disabled per run through `optimizer_options` — the
sanctioned, code-untouching way the scaffold ablation
(`scripts/run_ablation.py`) builds its cells: each cell sets exactly one of
these to `false` (plus a baseline cell with all of them on), and SGSM is held
off in every cell.

| `optimizer_options` key | Mechanism disabled when `false` |
|---|---|
| `ace_enabled` | ACE knowledge control |
| `psr_enabled` | NLPSR population-size reduction |
| `bse_enabled` | Budget-Safe Escape |
| `linkage_blockwise_enabled` | Linkage-aware block crossover |
| `local_search_enabled` | Endgame local search (coordinate-wise in the locked `pub` profile) |
| `arch_enabled` | Elite archive |
| `interaction_graph_enabled` | SGSM interaction graph (activates at `D>=50`; off in every scaffold-ablation cell) |

The ablation script writes one YAML per cell under `configs/_ablation/` — those
files are ordinary run configs whose only non-default block is
`optimizer_options`. See the [Runbook](runbook.md#dt-gsk-ablation) for the
end-to-end ablation pipeline.

## DT-GSK deep-stall full restart (multi-start)

DT-GSK ships with a **deep-stall full restart** as a standard, default-on
mechanism. It is on by default in the optimizer itself — no `optimizer_options`
entry is needed, so a normal run already includes it (though, like the ablation
switches above, each field can still be overridden per run via
`optimizer_options`); the fields below are the dataclass defaults in `DTGSKConfig`
(`src/gsk_family/optimizers/_dt_core.py`).

At the end of each generation DT-GSK updates a separate **global best** and
checks whether the working incumbent has been frozen for too long. When the
incumbent has not improved for at least `deep_stall_frac` of the budget, the
budget is at least `deep_stall_min_budget` NFEs, the per-restart cooldown has
elapsed, and the run is still before `deep_stall_stop_frac` of the budget, the
**entire working population is re-initialised uniformly** — a true multi-start.
The preserved global best means a restart can never lose ground (it is also what
`optimize()` returns), and it can escape a basin the budget-safe escape (BSE)
restart cannot, because BSE always keeps the incumbent elite — which, in a trap,
*is* the trapped solution. The mechanism draws RNG only when it actually fires,
so non-stalling runs are byte-identical to a run without it.

| Field | Default | Meaning |
|---|---|---|
| `deep_stall_restart_enabled` | `True` | Master switch for the deep-stall multi-start. |
| `deep_stall_frac` | `0.25` | Stall length (as a fraction of the budget) before a restart is allowed to fire. |
| `deep_stall_cooldown_frac` | `0.15` | Minimum gap between consecutive restarts, as a fraction of the budget. |
| `deep_stall_stop_frac` | `0.9` | Budget fraction past which restarts are suppressed (endgame protection). |
| `deep_stall_min_budget` | `20000` | Restarts are inert below this NFE budget, so tiny smoke/byte-stability runs stay unaffected. All real CEC budgets (10000·D for CEC2013/CEC2017, a fixed 150,000 for CEC2011, 3,000,000 for CEC2013-LSGO, and 50,000–10,000,000 per dimension for CEC2020) are far above it. |

This is why DT-GSK escapes the one catastrophic basin trap observed in the
study (CEC2017 F30 at D10) while holding the family's best descriptive mean
rank on the primary CEC2017 suite. Applying the restart
uniformly carries a disclosed D30 trade-off — it prematurely restarts a handful
of slow-converging multimodal functions — but DT-GSK at D30
is led only by the strong `egsk` baseline (the runner-up on that suite's
descriptive aggregate).

## Direct CLI equivalent

Direct CLI arguments build the same in-memory config as a YAML file. This is
convenient for a single cell:

```powershell
gsk-run --optimizer agsk --suite cec2020 --dimension 10 --function 1 --runs 1 --seed 20240620 --max-evaluations 1000 --overwrite
```

Selectors are flexible: `--function` and `--dimension` accept a single value
(`7`), a comma-separated list (`1,3,5`), a repeated flag, or an inclusive
`START:STOP` range (`1:30`).

A few flags toggle common behaviours:

| Behaviour | Default | Turn off with | Force on with |
|---|---|---|---|
| Console progress logging | on | `--quiet` (or `console_log: false`) | `--console-log` |
| Checkpoint generation logs | on | `--no-generation-logs` (or `generation_logs: false`) | `--generation-logs` |
| Convergence graph PNGs | off | `--no-convergence-graphs` (or `convergence_graphs: false`) | `--convergence-graphs` |
| Parallel execution | on | `--serial` (or `parallel: false`) | `--parallel` |
| Live statistical analysis | off | *(omit `--stats`)* | `--stats` |

`--console-log` / `--quiet` and `--convergence-graphs` /
`--no-convergence-graphs` are mutually exclusive pairs; passing both members of
a pair (or both `--parallel` and `--serial`) is rejected by the CLI. The
`--stats` flag is the CLI spelling of the `statistical_analysis` YAML field
(default `false`), and the live panel deliberately skips the `gsk` baseline;
the native-dimension `cec2011` suite is supported and emits a single per-suite
rollup panel (see [Statistical Analysis](../research/statistical_analysis.md)).

Console logging prints the campaign header, per-optimizer sections, the detailed
configuration before dispatch, per-function summary rows, final summary tables,
`[finalize]` progress bars while reports and metadata are written, and a
pass/warn status. Use `--quiet`/`console_log: false` only when output should be
suppressed.

Checkpoint generation logs produce the `gen_logs/CheckpointErrors_*` CSV files.
Disable them only for temporary runs that do not need those tables.

Convergence graph PNGs are rendered from the median-run curve CSV files into
`curves/graphs/` only when `--convergence-graphs` or `convergence_graphs: true`
is set. Without that opt-in, the median-run `curves/*.csv` files are still
written.

When parallel, the runner reports Numba availability and the active Numba thread
count at startup. Auto mode caps Numba's internal thread pool so multiple worker
processes do not oversubscribe the CPU. Set `--numba-threads N` /
`numba_threads: N` only when benchmarking a different worker/thread split; see
[Performance](../research/performance.md) for the rationale.

## Disabling parallel execution

Parallel is the default. Disable it only for serial debugging or a strict
single-thread reproducibility check.

In YAML:

```yaml
parallel: false
workers: 1
```

Or from the CLI:

```powershell
gsk-run --config configs/smoke.yml --root . --serial
```

Note that `--parallel` and `--serial` cannot be combined — the CLI rejects that
pairing.
