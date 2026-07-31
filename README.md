# GSK Family Python

This repository is the Python implementation of the GSK-family optimization
project. It contains optimizer implementations, benchmark adapters, experiment
runners, validation tools, reproducibility controls, generated documentation,
and reference-compatible benchmark evidence used for comparison.

Work directly in this repository root -- the `02-GSK_Family_Python_v1.1` project
folder.

Do not create a separate generated workspace, mirror folder, or agent-only
project tree. All normal coding, testing, documentation, benchmark, and review
work should happen inside this repository.

## Quick Start

Install in editable mode with the dev extra, run a tiny smoke cell to confirm
the toolchain, then launch one full CEC2017 sweep:

```powershell
# 1. Install (editable, with test/lint/docs tooling)
python -m pip install -e ".[dev]"

# 2. Smoke run (a few seconds): one optimizer, one function, tiny budget
python run.py --root . --optimizer gsk --suite sphere --function 1 --dimension 4 --runs 1 --max-evaluations 80 --overwrite

# 3. Full CEC2017 sweep: safe two-worker baseline, graphs on, explicit recompute
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
```

For the complete command set -- every CEC suite, config launchers, targeted
runs, validation, and the speed/memory backend guide -- see
[runbook.md](runbook.md).

## What This Project Contains

The project provides a Python-first implementation of the GSK optimizer family
with CEC benchmark support and production-grade research tooling. Alongside the
`gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`, and `egsk` baselines it ships
`dt-gsk`, this project's own proposed method (Interaction-Structure Memory
Gaining-Sharing Knowledge Optimization), which adds a dimension-aware
interaction-structure memory to the gaining-sharing scaffold.

Implemented optimizer IDs (seven runnable algorithms):

| Optimizer ID | Short description |
|---|---|
| `gsk` | Base gaining-sharing-knowledge algorithm. |
| `agsk` | Adaptive parameter pools over GSK. |
| `apgsk` | Adaptive parameters tuned for engineering optimization. |
| `fdb-agsk` | AGSK with the fitness-distance-balance guiding mechanism. |
| `atmals-gsk` | Auto-tuning memory-based adaptive local search GSK. |
| `egsk` | Enhanced GSK (dual adaptive KF, fixed senior partition, interior-point refinement). MATLAB port; also a reference comparator. |
| `dt-gsk` | **This project's proposed method** -- Dimension-Tiered Gaining-Sharing Knowledge. |

`dt-gsk` is the byte-identical migration of the source DT-GSK v2.1 optimizer;
its vendored core lives under `src/gsk_family/optimizers/_dt_core.py` (with
`_dt_profiles.py`, `_dt_rng.py`, and the `_dt_subsystems/` package) behind the
adapter `src/gsk_family/optimizers/dt_gsk.py`. It uses the same unified Threefry
RNG and shared `get_cec_seed` schedule as the rest of the family, and
self-initializes a `5*D` population (`np_init_mult * dim`, with
`np_init_mult = 5`) -- a documented fair-start exception described in
[Seed Policy](docs/reference/seed_policy.md).

On the CEC2017 family panel (51 runs, 29 functions with F2 excluded, error vs
optimum), DT-GSK is **#1 in the GSK family by both mean and median** -- ranked
#1 at D10/D50/D100 and #1 overall, with D30 led only by the strong `egsk`
baseline (the runner-up overall). It ships
the **deep-stall multi-start** (a default-on standard mechanism): when the
incumbent stalls for a quarter of the budget the working population fully
re-initializes while a preserved global-best can never lose ground, which fixes
the lone catastrophic basin trap (CEC2017 F30 D10) and is byte-identical on
non-stalling runs. See [FINAL_RELEASE_REPORT.md](FINAL_RELEASE_REPORT.md) for the
per-dimension ranks and statistics.

> `egsk` is now a **runnable** optimizer ID -- it ships a real kernel
> (`src/gsk_family/optimizers/egsk.py`, a faithful MATLAB port whose
> interior-point refinement uses `scipy`-SLSQP in place of `fmincon`, validated
> as statistically equivalent), so `--optimizer egsk` works. It **also** remains
> a GSK-family reference comparator: the published statistical panel reports
> `egsk` from the committed **Python (`scipy`-SLSQP) port** CSVs (the comparator
> of record), not a MATLAB `fmincon` reference.

Supported benchmark suites (six):

| Suite ID | Scope |
|---|---|
| `sphere` | Trivial smoke objective for toolchain checks. |
| `cec2011` | Real-world application problems; native per-problem dimensions. |
| `cec2013` | 28 functions; dimensions 10/30/50; the second family-comparison suite (51 runs, full 7-optimizer reference panel). |
| `cec2013lsgo` | Large-scale global optimization; 15 functions at D=1000. |
| `cec2017` | 30 functions; dimensions 10/30/50/100 (the scored set excludes F2). |
| `cec2020` | 10 functions; dimensions 5/10/15/20. |

The CEC2017 *scored* set excludes F2 (so it covers F1 and F3-F30) because the
benchmark maintainers withdrew F2 for numerical-instability reasons; this
exclusion is applied automatically by the statistical-analysis suite.

Main capabilities:

- Direct command-line experiment execution through `python run.py`.
- YAML-driven campaign execution through `configs/*.yml`.
- True multi-core execution through a self-healing process backend that recovers
  from worker crashes instead of hanging.
- Python/Numba CEC benchmark evaluator used by default for all normal runs.
- Conservative two-worker default for automatic parallel runs, with documented
  campaign commands spelling out `--parallel --workers 2` so users can raise
  concurrency intentionally.
- Numba-aware startup reporting and nested-thread control.
- Function-by-function console summary output.
- Deterministic seed schedules and fair-start population handling.
- Result writers for summaries, metadata, seed schedules, profile data, and
  validation evidence.
- Read-only imported reference evidence under `benchmarks/cec_reference_results`
  -- the single source of truth for all paper data and statistics, carrying the
  full 7-optimizer panel (proposed `dt-gsk` included) for `cec2017`, `cec2011`,
  and `cec2013`.
- Full Markdown documentation organized into themed `docs/` subfolders, plus a
  generated static HTML site.

## Root Files

The project root keeps a deliberate set of Markdown files -- three operating
documents, a newcomer map, the governance/standards set, and the release report:

- [README.md](README.md): this detailed root landing page.
- [SKILL.md](SKILL.md): project-specific agent operating instructions.
- [runbook.md](runbook.md): concise copy-paste build-and-run command reference
  (install, run every CEC suite, smoke tests, full sweeps, and the
  speed/memory backend guide).
- [REPO_MAP.md](REPO_MAP.md): one-screen orientation map for a newcomer.

Governance and standards (the authoritative project rules):

- [PROJECT_RULES.md](PROJECT_RULES.md): the project "constitution" — workspace,
  evidence integrity, reproducibility, byte-identity, version-control policy,
  and the green-gates rule; links the rest.
- [ARCHITECTURE.md](ARCHITECTURE.md): package map, layering, and data flow.
- [DESIGN_GUIDE.md](DESIGN_GUIDE.md): design principles and how to extend.
- [BENCHMARK_RULES.md](BENCHMARK_RULES.md): suite/experiment protocol and the
  RNG/seed regime.
- [CODING_STANDARD.md](CODING_STANDARD.md): code conventions enforced by the gates.
- [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md): Numba, thread pinning, parallel
  backend, the floating-point-regime sentinel, and memory rules.

The release report is [FINAL_RELEASE_REPORT.md](FINAL_RELEASE_REPORT.md): the
per-dimension DT-GSK ranks, statistics, and the publication-readiness decision.

The full documentation package lives in `docs/`, where the canonical guides are
organized into themed subfolders (see [Documentation Structure](#documentation-structure)
below) rather than as a flat set of top-level files. The review and audit prompts
live under [`docs/prompt/`](docs/prompt/project-review.md).

Important root files:

- `run.py`: canonical source-checkout runner.
- `pyproject.toml`: package metadata, dependency ranges, package discovery,
  and console scripts.
- `MANIFEST.in`: source-distribution inclusion and exclusion rules.
- `CITATION.cff`: citation metadata.
- `.gitignore`: generated-output and cache ignore rules.

## Code Author and Algorithm References

Code author:

- **Mostafa Masoud**
- Email: `moustafa.masoud@gmail.com`

When using this project in reports, papers, theses, or benchmark comparisons,
cite the Python project metadata in [CITATION.cff](CITATION.cff) and cite the
original paper for each optimizer that appears in the experiment.

| Optimizer ID | Algorithm reference |
|---|---|
| `gsk` | Mohamed, A. W.; Hadi, A. A.; Mohamed, A. K. "Gaining-sharing knowledge based algorithm for solving optimization problems: a novel nature-inspired algorithm." International Journal of Machine Learning and Cybernetics, 11, 1501-1529, 2020. DOI: [10.1007/s13042-019-01053-x](https://doi.org/10.1007/s13042-019-01053-x). |
| `agsk` | Mohamed, A. W.; Hadi, A. A.; Mohamed, A. K.; Awad, N. H. "Evaluating the performance of adaptive gaining-sharing knowledge based algorithm on CEC 2020 benchmark problems." 2020 IEEE Congress on Evolutionary Computation (CEC), 1-8, 2020. DOI: [10.1109/CEC48606.2020.9185901](https://doi.org/10.1109/CEC48606.2020.9185901). |
| `apgsk` | Mohamed, A. W.; Abutarboush, H. F.; Hadi, A. A.; Mohamed, A. K. "Gaining-sharing knowledge based algorithm with adaptive parameters for engineering optimization." IEEE Access, 9, 65934-65946, 2021. DOI: [10.1109/ACCESS.2021.3076091](https://doi.org/10.1109/ACCESS.2021.3076091). |
| `fdb-agsk` | Bakir, H.; Duman, S.; Guvenc, U.; Kahraman, H. T. "Improved adaptive gaining-sharing knowledge algorithm with FDB-based guiding mechanism for optimization of optimal reactive power flow problem." Electrical Engineering, 105, 3121-3160, 2023. DOI: [10.1007/s00202-023-01803-9](https://doi.org/10.1007/s00202-023-01803-9). |
| `atmals-gsk` | Alfadli, N. M.; Oun, E. M.; Mohamed, A. W. "Auto-Tuning Memory-Based Adaptive Local Search Gaining-Sharing Knowledge-Based Algorithm for Solving Optimization Problems." Algorithms, 18(7), 398, 2025. DOI: [10.3390/a18070398](https://doi.org/10.3390/a18070398). |
| `dt-gsk` | This project's proposed method (Dimension-Tiered Gaining-Sharing Knowledge Optimization) by Mostafa Masoud. Paper "DT-GSK: Dimension-Tiered Adaptive Control and Deterministic Refinement for Gaining-Sharing Knowledge Optimization" forthcoming; cite the project metadata in [CITATION.cff](CITATION.cff) until then. |

## Repository Map

```text
02-GSK_Family_Python_v1.1/
  README.md
  SKILL.md
  runbook.md
  REPO_MAP.md
  PROJECT_RULES.md  ARCHITECTURE.md  DESIGN_GUIDE.md
  BENCHMARK_RULES.md  CODING_STANDARD.md  PERFORMANCE_RULES.md
  FINAL_RELEASE_REPORT.md
  run.py
  pyproject.toml
  MANIFEST.in
  CITATION.cff
  benchmarks/
  configs/
  docs/
  results/
  scripts/
  src/gsk_family/
  tests/
```

Directory roles:

- `benchmarks/`: Python CEC runtime (`cec_suite_python`) and imported reference
  evidence.
- `configs/`: reusable experiment and validation campaign configurations.
- `docs/`: canonical source Markdown, organized into themed subfolders --
  `getting-started/` (user guide, tutorial, runbook, configuration,
  troubleshooting, explainer), `reference/` (architecture, API, optimizer
  interface, module dependencies, workflows, result schema, seed policy,
  benchmark protocol and mapping, diagrams, project structure, glossary),
  `algorithms/` (per-optimizer notes), `development/` (developer, contributor,
  maintenance, extension, and code-reading guides, the EGSK port spec, and
  `history/` with archived records of completed work), `research/` (researcher
  handbook, reproducibility, performance, validation report, numerical
  examples), `prompt/` (the review and audit prompts), and `html/` (generated
  site). The folder root also holds `index.md` and `LICENSES.md`.
- `docs/html/`: generated static HTML documentation site.
- `results/`: generated experiment and validation output.
- `scripts/`: CEC campaign launchers, the DT-GSK ablation driver
  (`run_ablation.py`), the documentation builder, and developer utilities.
- `src/gsk_family/`: importable Python package.
- `tests/`: unit, smoke, regression, performance, and documentation checks.

### Documentation Structure

The `docs/` tree groups the canonical Markdown into themed subfolders. The
generated HTML site is rendered from these sources into `docs/html/`.

```text
docs/
  index.md                 # documentation landing page / table of contents
  LICENSES.md              # third-party license notices
  getting-started/         # user_guide, tutorial, runbook, configuration,
                           #   troubleshooting, explainer
  reference/               # architecture, api, python_optimizer_interface,
                           #   module_dependencies, workflows, result_schema,
                           #   seed_policy, benchmark_protocol,
                           #   benchmark_mapping, diagrams, project_structure,
                           #   glossary
  algorithms/              # gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk
  development/             # developer_guide, contributor_guide,
                           #   maintenance_guide, extension_guide,
                           #   code_reading_guide, egsk_port_spec,
                           #   history/ (archived completed-work records)
  research/                # researcher_handbook, reproducibility, performance,
                           #   validation_report, numerical_examples
  prompt/                  # project-review, documentation-review,
                           #   documentation-deep-upgrade, publication-polish
  html/                    # generated static HTML site
```

## Installation

Install in editable mode from the project root:

```powershell
python -m pip install -e ".[dev]"
```

Or install just the libraries with plain `pip` -- no editable package, so use
`python run.py` rather than the `gsk-*` console scripts:

```powershell
python -m pip install -r requirements.txt       # runtime only
python -m pip install -r requirements-dev.txt    # runtime + dev tooling
```

The project is tested against the dependency ranges declared in
`pyproject.toml`. The important runtime stack includes:

- Python `>=3.10,<3.14`
- NumPy
- SciPy
- pandas
- matplotlib
- PyYAML
- Numba

Use the dev extra for tests, linting, type checks, and documentation commands.

## Canonical Runner

Use `python run.py` as the canonical source-checkout runner.

Show help:

```powershell
python run.py --help
```

Run the default smoke configuration:

```powershell
python run.py --root . --config configs/smoke.yml
```

Run a tiny direct smoke cell:

```powershell
python run.py --root . --optimizer gsk --suite sphere --function 1 --dimension 4 --runs 1 --max-evaluations 80 --overwrite
```

Run the full CEC2017 all-optimizer campaign with the safe documented baseline:

```powershell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
```

This command keeps `--parallel --workers 2` visible so the resource choice is
clear to anyone copying it. It also keeps PNG plot generation explicit with
`--convergence-graphs`; replace that with `--no-convergence-graphs` when you
only need convergence CSV files. Increase `--workers N` only when the machine
has enough free CPU and memory for the larger campaign.

For example, on a dedicated workstation you may raise the worker count:

```powershell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 4 --convergence-graphs --overwrite
```

`--overwrite` recomputes matching cells and replaces existing per-run rows for
those cells. Omit `--overwrite` when you want the runner to resume and skip
completed cells.

For ready-to-paste commands covering every CEC suite, the YAML config
launchers, targeted single-function runs, reference-table reproduction, and
recovery on slow or crashing machines, see [runbook.md](runbook.md).

## Runner Defaults

Default behavior to preserve:

- Parallel execution is enabled unless `--serial` is passed.
- Automatic worker count defaults to 2 on machines with at least two logical
  cores, or 1 on a single-core machine.
- Documentation and runbooks use explicit `--parallel --workers 2` campaign
  commands so copied commands do not unexpectedly consume a large machine.
- Automatic CEC2017 composition cells (`F21`-`F30`) still have an upper safety
  cap of 8 workers if the automatic count is raised in code in the future.
- `--workers N` is the explicit user override for higher or lower concurrency.
- Benchmark backend defaults to `auto`, which uses the Python/Numba evaluator.
- Console logging is enabled by default.
- Console progress is function-by-function.
- One `Fxx` summary row is printed only after all runs for that function finish.
- Finalization prints `[finalize]` progress bars while reports, metadata, and
  verification files are written.
- Convergence graph PNG generation is opt-in with `--convergence-graphs` or
  `convergence_graphs: true`; curve CSVs are still written when PNG graphs are
  not requested.
- Per-run heartbeat/progress lines should not appear inside the summary table.
- Generated experiment output defaults to `results/_run_all/`.
- Imported reference evidence must remain read-only during normal runs.
- Numba runtime status should be reported at startup when relevant.
- Auto Numba thread handling should avoid nested thread oversubscription during
  parallel execution.

## Console Output Contract

For a campaign, the console should clearly show:

- run-all style campaign header;
- suite, function, dimension, run count, seed policy, random generator, and
  parallel status;
- worker count and Numba runtime information;
- optimizer section headers;
- per-dimension summary tables;
- one completed function row at a time;
- finalization progress bars after the function table;
- optional reference-comparison status when requested;
- final pass/warn/fail summary.

The console should not print noisy per-run progress lines while a function is
still running. The intended behavior is to show the function result when the
complete run batch is done, then show compact finalization progress outside the
table while artifacts are written.

## Result Output

Generated output normally goes under:

```text
results/_run_all/<optimizer>/<suite>/
```

Typical output includes:

- per-run result files;
- function summary tables;
- aggregate summaries;
- `seed_schedule.csv`;
- `environment.json`;
- optional `profile.json`;
- checkpoint or generation-log artifacts when enabled;
- median-run convergence curve CSVs and optional rendered PNG graphs;
- validation and comparison reports when requested.

Never write generated experiment output into:

```text
benchmarks/cec_reference_results/
```

That directory is imported reference evidence and should be treated as
read-only unless the user explicitly asks for reference-evidence maintenance.

## Documentation

The complete, per-folder catalog lives in [docs/index.md](docs/index.md); the
themed folders are summarized under [Documentation Structure](#documentation-structure)
above.

Task-oriented how-to index (pick your goal):

| I want to... | Start here |
|---|---|
| Run my first experiment | [Tutorial](docs/getting-started/tutorial.md) -> [User Guide](docs/getting-started/user_guide.md) |
| Copy-paste a full sweep command | [runbook.md](runbook.md) |
| Understand a config file | [Configuration](docs/getting-started/configuration.md) |
| Fix an install or run error | [Troubleshooting](docs/getting-started/troubleshooting.md) |
| Learn how an optimizer works | the [algorithm guides](docs/algorithms/gsk.md) |
| Reproduce or validate results | [Reproducibility](docs/research/reproducibility.md) -> [Validation Report](docs/research/validation_report.md) |
| Compare algorithms statistically | [Statistical Analysis](docs/research/statistical_analysis.md) |
| Add an optimizer/suite/CLI | [Extension Guide](docs/development/extension_guide.md) |
| Look up an output file's columns | [Result Schema](docs/reference/result_schema.md) |

Main documentation entry points:

- [docs/index.md](docs/index.md)
- [docs/getting-started/user_guide.md](docs/getting-started/user_guide.md)
- [docs/getting-started/tutorial.md](docs/getting-started/tutorial.md)
- [docs/getting-started/runbook.md](docs/getting-started/runbook.md)
- [docs/getting-started/configuration.md](docs/getting-started/configuration.md)
- [docs/reference/project_structure.md](docs/reference/project_structure.md)
- [docs/reference/architecture.md](docs/reference/architecture.md)
- [docs/reference/api.md](docs/reference/api.md)
- [docs/reference/seed_policy.md](docs/reference/seed_policy.md)
- [docs/research/reproducibility.md](docs/research/reproducibility.md)
- [docs/research/performance.md](docs/research/performance.md)
- [docs/reference/benchmark_protocol.md](docs/reference/benchmark_protocol.md)
- [docs/research/validation_report.md](docs/research/validation_report.md)
- [docs/development/developer_guide.md](docs/development/developer_guide.md)
- [docs/development/contributor_guide.md](docs/development/contributor_guide.md)
- [docs/getting-started/troubleshooting.md](docs/getting-started/troubleshooting.md)

Generated HTML site:

- [docs/html/index.html](docs/html/index.html)

Rebuild generated HTML after Markdown, docstring, API, report, or navigation
changes:

```powershell
python scripts\build_docs_html.py
```

Canonical Markdown documentation under `docs/` is rendered into the generated
HTML site under `docs/html/`.

## Validation

List available optimizers, benchmarks, and reference evidence:

```powershell
gsk-list --optimizers --benchmarks --references benchmarks/cec_reference_results
```

Validate imported reference evidence:

```powershell
gsk-validate --references benchmarks/cec_reference_results
```

Compare generated output with imported references:

```powershell
gsk-validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

Validation must be truthful:

- missing generated/reference pairs should not appear as passing checks;
- all-skipped comparisons should exit nonzero;
- reduced validation should be documented as reduced evidence;
- full-budget campaigns should be documented separately from smoke checks.

## Statistical analysis

Generate the paper-grade GSK-family comparison (Friedman ranks, Nemenyi
critical-difference diagrams, pairwise Wilcoxon signed-rank tests with Holm
correction, and Vargha-Delaney/Cliff's effect sizes) for the proposed optimizer
(`dt-gsk` by default) against the committed reference comparators:

```powershell
gsk-stats --suite CEC2017 --dims 10,30,50,100
```

The suite builds the **7-algorithm GSK-family panel**: the proposed optimizer
(`dt-gsk` by default) plus the six committed reference comparators (`gsk`,
`agsk`, `apgsk`, `fdb-agsk`, `egsk`, `atmals-gsk`). All seven algorithms --
the proposed `dt-gsk` included -- are loaded **reference-first** from the
committed panel `benchmarks/cec_reference_results/<suite>/<optimizer>/`, the
single source of truth for paper statistics; a locally reproduced run under
`results/_run_all/<optimizer>/<suite>/summary/` is used only as a fallback for
cells the reference tree lacks. Outputs (text report, Friedman-rank
CSV, LaTeX fragments, and CD/rank PNGs) are written to
`results/_run_all/_analysis/<suite>/`. The implementation lives under
`src/gsk_family/analysis/` (`gsk-stats` / `cli/stats.py`). See
[Statistical Analysis](docs/research/statistical_analysis.md) for the full method
(Friedman, Nemenyi CD, Wilcoxon/Holm, A12/Cliff's delta, win/tie/loss, BCa
bootstrap) and the data-source layout.

To stream the per-dimension Wilcoxon + Friedman analysis live during a run, add
the opt-in `--stats` flag to `python run.py`/`gsk-run` (default off; it skips
vanilla `gsk`; the native-dimension `cec2011` emits a single per-suite rollup
panel).

### Paper review pack

The `papers/` tree holds the LaTeX sources and the advisor review-pack builder.
Regenerate the single-PDF review pack with:

```powershell
python papers/scripts/generate_review_pack.py
```

This writes `papers/DT-GSK-CEC2017-review.pdf` (matplotlib `PdfPages`, no LaTeX
required for the review pack): a headline dashboard, 7-algorithm CEC2017/CEC2011
mean tables, and 7-algorithm GSK-family convergence grids (GSK, AGSK, APGSK,
FDB-AGSK, eGSK, ATMALS-GSK, DT-GSK). It reads checkpoint CSVs from the committed
comparator evidence and the reproduced `dt-gsk` run; missing curves are never
fabricated and are logged to `papers/DT-GSK-CEC2017-review_missing.log`. See
[papers/README.md](papers/README.md) for the full layout.

## Reproducibility

The project preserves reproducibility through:

- explicit seed policies;
- deterministic run-index schedules;
- fair-start populations;
- recorded environment metadata;
- result schemas that include enough information to replay or audit a run;
- serial/parallel determinism checks;
- generated seed schedules.

Seed compatibility wording is intentionally limited to seed-policy
documentation. It means Python imitates the original seed labels and formulas
for traceable comparison. It does not mean the external reference runtime is
required for normal execution.

## Random Number Generators

The Python runtime ships three deterministic generators, selected by the
`rand_generator` label. Each reproduces the corresponding external reference
*random stream* bit-for-bit, and `threefry` is the default. (Bit-for-bit *table*
reproduction under the `reference` policy is the narrower, per-optimizer claim
scoped under "Reference parity" below: bit-exact for GSK/AGSK/APGSK/ATMALS-GSK,
with FDB-AGSK diverging on the floating-point residual.)

- `threefry` -- Threefry-4x64-20 counter-based generator, reproducing
  `rng(seed, 'threefry')`. Key `(0, 0, 0, 0)`; counter
  `counter[j] = ((S + 2j + 1) << 32) | (S + 2j)` for `j = 0..3`; four doubles per
  block via `(word >> 11) * 2^-53`; the low counter word advances by one per block.
- `twister` -- MT19937, reproducing `rng(seed, 'twister')`. Seeded with the
  reference `init_genrand(seed)` recurrence; each double uses two 32-bit outputs
  via `genrand_res53`.
- `seed` -- mcg16807 (Park-Miller v4), reproducing
  `RandStream('mcg16807', 'Seed', seed)`. Seeded
  `x0 = (seed << 16) mod (2^31 - 2^15)`, then `x <- 16807 * x mod (2^31 - 1)` and
  `u = x / (2^31 - 1)`.

The seedings and conversions were reverse-engineered from the reference generator
state and verified against reference draws to machine epsilon. All three fill
matrices column-major to match the reference `rand(m, n)` layout (a `(k, m, n)`
request equals `k` successive column-major `(m, n)` draws) and share the integer
rules `randi(imax) = floor(imax * rand) + 1` and `randperm(n) = argsort(rand(n))`.

Reference parity, validated against the imported `cec2017` generation logs under
the unified seed schedule:

- GSK, AGSK, APGSK, and ATMALS-GSK reproduce the reference convergence to ~1e-13
  relative (machine precision) across functions and dimensions; the only residual
  is the irreducible floating-point difference between the Numba benchmark kernels
  and the reference objective implementation.

The legacy v5 `state` generator (swb2712) is intentionally not bundled: its output
combines a subtract-with-borrow cache (lags 27/12) with a second 53-bit generator
whose state is not recoverable from floating-point introspection, so it cannot be
reproduced bit-for-bit. Requesting any unsupported label raises a clear error.
Implementations live in `src/gsk_family/common/threefry_rng.py` and
`src/gsk_family/common/reference_rng.py`; known-answer tests in
`tests/unit/test_rng.py` lock each stream.

## Performance And Parallelism

Performance-sensitive areas:

- benchmark objective evaluation;
- optimizer inner loops;
- random-number generation;
- population and donor construction;
- rank/sort operations;
- local search for optimizers that support it;
- generation-log writing;
- validation I/O;
- Numba JIT warmup;
- nested Python-worker and Numba-thread interaction.

Performance tuning must preserve:

- seed schedules;
- RNG draw order where behavior depends on it;
- evaluation counts;
- bounds repair behavior;
- result schema;
- output naming;
- deterministic serial/parallel result ordering;
- reference-facing behavior.

### Parallel Backend Behavior

The default `process` backend is true multi-core: each cell runs in a separate
process pool, so work scales across physical cores without the GIL contention
that a thread pool would impose on the JIT-compiled inner loops.

- It self-heals on worker crashes. If a worker dies mid-run, the pool is rebuilt
  and the affected work is retried; if a cell still cannot complete in parallel,
  it falls back to running serially. A run therefore finishes rather than
  hanging.
- The automatic process-worker count is intentionally small: 2 workers on
  machines with at least two logical cores, otherwise 1 worker.
- For CEC2017 composition cells (`F21`-`F30`), automatic process runs retain an
  upper memory-safety cap of 8 workers. Explicit `--workers N` values are still
  treated as the user's chosen speed/memory tradeoff.
- `--workers N` bounds the number of concurrent processes, which bounds peak
  memory. Start from `--workers 2`; raise it only on machines with enough spare
  CPU and RAM.
- Avoid `--parallel-backend thread`. Calling the parallel Numba kernels from
  many Python threads can deadlock, and the threaded path does not scale for
  these GIL-bound loops anyway. Use the default process backend, or `--serial`
  for a single-process run.

See [runbook.md](runbook.md) for the slow/crashing recovery commands and
[docs/research/performance.md](docs/research/performance.md) for the detailed
performance analysis.

Use reduced smoke campaigns for fast iteration and full campaign commands only
when long runs are explicitly requested.

## Quality Checks

Documentation smoke tests:

```powershell
python -m pytest tests\smoke\test_documentation_commands.py -q
```

Lint:

```powershell
python -m ruff check .
```

Full tests:

```powershell
python -m pytest -q
```

Profile-lock validation:

```powershell
python scripts\validate_profile_lock.py --root .
```

Preferred broad verification sequence:

```powershell
python -m pytest -q
python -m ruff check .
python scripts\validate_profile_lock.py --root .
python scripts\build_docs_html.py
```

If a command is too expensive for the current task, record the exact deferred
command and the reason for deferral.

## Maintenance Rules

When editing this project:

- prefer existing project patterns;
- avoid unrelated refactors;
- keep optimizer algorithm logic stable unless algorithm work is requested;
- keep docs and generated HTML synchronized;
- keep root Markdown intentional;
- avoid global working-directory mutation;
- use absolute paths or root-relative paths safely;
- protect imported reference evidence;
- remove generated caches after broad test or lint runs;
- preserve deterministic behavior during performance tuning.

## Agent Operating Files

Root agent files:

- [SKILL.md](SKILL.md): project-specific agent operating contract.
- [runbook.md](runbook.md): copy-paste command reference for installs, smoke
  tests, full sweeps, and backend recovery.

The review and audit prompts live under [`docs/prompt/`](docs/prompt/project-review.md)
(four files): `project-review.md` (full-project audit),
`documentation-review.md` (docs consistency gate + inline docstring/comment review),
`documentation-deep-upgrade.md` (deep docs upgrade), and
`publication-polish.md` (the pre-publication release-hardening pass).

Use these files before major review, tuning, validation, documentation,
release, or cleanup work.
