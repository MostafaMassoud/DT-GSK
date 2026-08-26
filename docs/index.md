# Documentation Index

> **What this page is.** The map of all project documentation, grouped by
> folder, with goal-based reading paths to get you to the right page fast.
> **Who it is for.** Everyone; start here.

Project documentation, grouped by folder. Browse the rendered site at
[html/index.html](html/index.html).

> **Project status (2026-08-25).** The manuscript was submitted to *Algorithms*
> (MDPI) as `algorithms-4507562` from freeze pass-38 / tag v2.13, and has
> received a **MAJOR REVISION** from two reviewers. Revision work is in
> progress — see **[REVISION_STATUS.md](../REVISION_STATUS.md)** for the current
> state, which reviewer points are closed, and what remains.
> Evidence releases are unchanged: `rel-2026-07-20-67d9345f9` (primary) and
> `abl-rel-2026-07-20` (ablation).
> The proposed method is **DT-GSK** (Dimension-Tiered Gaining-Sharing
> Knowledge); "ISM" names only its internal interaction-structure-memory
> mechanism, never the algorithm.

## Reading paths

Not sure where to start? Pick the goal that fits. Each path lists the pages in
the order they build on one another:

- **Just run it.** [Tutorial](getting-started/tutorial.md) -> [User Guide](getting-started/user_guide.md) -> [Runbook](getting-started/runbook.md).
- **Understand the algorithms.** [Explainer](getting-started/explainer.md) -> [GSK](algorithms/gsk.md) -> the variant guides ([AGSK](algorithms/agsk.md), [APGSK](algorithms/apgsk.md), [FDB-AGSK](algorithms/fdb-agsk.md), [ATMALS-GSK](algorithms/atmals-gsk.md), [EGSK](algorithms/egsk.md)) -> [DT-GSK](algorithms/dt-gsk.md) (the proposed method) -> [Numerical Examples](research/numerical_examples.md).
- **Reproduce or validate results.** [Researcher Handbook](research/researcher_handbook.md) -> [Reproducibility](research/reproducibility.md) -> [Validation Report](research/validation_report.md) -> the CEC C++/Python equivalence reviews under [Reference](#reference---reference).
- **Compare algorithms statistically.** [Statistical Analysis](research/statistical_analysis.md) -> [Benchmark Protocol](reference/benchmark_protocol.md) -> [Result Schema](reference/result_schema.md).
- **Contribute code.** [Code Reading Guide](development/code_reading_guide.md) -> [Developer Guide](development/developer_guide.md) -> [Extension Guide](development/extension_guide.md) -> [Contributor Guide](development/contributor_guide.md).
- **Look something up.** [Configuration](getting-started/configuration.md), [API Reference](reference/api.md), [Result Schema](reference/result_schema.md), [Glossary](reference/glossary.md), [Diagrams](reference/diagrams.md).

> The seven **runnable** optimizers are `gsk`, `agsk`, `apgsk`, `fdb-agsk`,
> `atmals-gsk`, `egsk`, and `dt-gsk`. The benchmark registry supports six
> **suites** -- the `sphere` suite plus five CEC suites (`cec2011`, `cec2013`,
> `cec2013lsgo`, `cec2017`, `cec2020`) -- of which three (`cec2011`, `cec2013`,
> `cec2017`) carry committed reference evidence. `egsk` is also a committed
> reference comparator, and the statistical panel reports its cells from that
> reference data.

## Getting Started - `getting-started/`

- [User Guide](getting-started/user_guide.md): install, list capabilities, run experiments, validate output, inspect results.
- [Tutorial](getting-started/tutorial.md): step-by-step first run, reduced CEC run, and result comparison.
- [Runbook](getting-started/runbook.md): operational commands for routine experiment work.
- [Configuration](getting-started/configuration.md): YAML fields, CLI overrides, and safe output paths.
- [Troubleshooting](getting-started/troubleshooting.md): common install, benchmark, and result issues.
- [Explainer](getting-started/explainer.md): conceptual overview for newcomers.

## Reference - `reference/`

- [Architecture](reference/architecture.md): runtime layout and ownership boundaries.
- [API Reference](reference/api.md): public modules, classes, functions, and CLI entry points.
- [Python Optimizer Interface](reference/python_optimizer_interface.md): optimizer contract and option schema.
- [Module Dependencies](reference/module_dependencies.md): dependency direction between package areas.
- [Workflows](reference/workflows.md): end-to-end execution paths from CLI to artifacts.
- [Result Schema](reference/result_schema.md): files written below `results/`.
- [Seed Policy](reference/seed_policy.md): deterministic seed formulas and fair starts.
- [Floating-Point Regime Verification](reference/fp_regime.md): the fail-closed sentinel that keeps every campaign in one numba-JIT floating-point regime.
- [Benchmark Protocol](reference/benchmark_protocol.md): suite metadata and evaluation conventions.
- [Benchmark Mapping](reference/benchmark_mapping.md): Python benchmark framework and its CEC reference results.
- [Diagrams](reference/diagrams.md): architecture, workflow, seed, validation, and testing flowcharts.
- [Project Structure](reference/project_structure.md): directory and file ownership map.
- [Glossary](reference/glossary.md): project terminology.
- [License and Provenance](LICENSES.md): licensing and provenance notes.

CEC C++/Python evaluator equivalence reviews (one per suite, documenting how the
bundled Python/Numba benchmark kernels line up with the originating C++
references):

- [CEC2011 Equivalence Review](reference/cec2011_cpp_python_equivalence_review.md)
- [CEC2013 Equivalence Review](reference/cec2013_cpp_python_equivalence_review.md)
- [CEC2013-LSGO Equivalence Review](reference/cec2013lsgo_cpp_python_equivalence_review.md)
- [CEC2017 Equivalence Review](reference/cec2017_cpp_python_equivalence_review.md)
- [CEC2020 Equivalence Review](reference/cec2020_cpp_python_equivalence_review.md)

## Algorithm Guides - `algorithms/`

One guide per runnable optimizer, in increasing order of elaboration over the
base gaining-sharing-knowledge scaffold:

- [GSK](algorithms/gsk.md): the base gaining-sharing-knowledge algorithm.
- [AGSK](algorithms/agsk.md): adaptive parameter pools over GSK.
- [APGSK](algorithms/apgsk.md): adaptive parameters tuned for engineering optimization.
- [FDB-AGSK](algorithms/fdb-agsk.md): AGSK with the fitness-distance-balance guiding mechanism.
- [ATMALS-GSK](algorithms/atmals-gsk.md): auto-tuning memory-based adaptive local search GSK.
- [EGSK](algorithms/egsk.md): enhanced GSK -- dual adaptive knowledge factors, a fixed senior partition, and interior-point refinement (runnable MATLAB port; also a reference comparator).
- [DT-GSK](algorithms/dt-gsk.md): **this project's proposed method** -- Dimension-Tiered Gaining-Sharing Knowledge, adding a dimension-aware interaction-structure memory to the scaffold.

## Development - `development/`

Living guides (see the [folder index](development/README.md)):

- [Developer Guide](development/developer_guide.md): day-to-day development guide.
- [Contributor Guide](development/contributor_guide.md): contribution rules.
- [Maintenance Guide](development/maintenance_guide.md): routine upkeep.
- [Extension Guide](development/extension_guide.md): adding an optimizer, suite, artifact, or CLI.
- [Code Reading Guide](development/code_reading_guide.md): how to inspect the codebase.
- [DT-GSK Core Reference](development/dt_gsk_core_reference.md): the vendored core and its byte-identity lock -- the locked files, the tests that hold them, the dimension tiers, determinism at `D >= 50`, and the facts that are routinely got wrong. Read before touching `optimizers/_dt_*`.
- [Evidence Re-run Runbook](development/evidence_rerun_runbook.md): regenerating the `D >= 50` DT-GSK evidence after a core behavior change -- affected-cell inventory, exact commands, and the manuscript edits that must follow.
- [EGSK Port Spec](development/egsk_port_spec.md): porting analysis and decision record for the EGSK MATLAB port (the algorithm guide is [EGSK](algorithms/egsk.md)).


## Research - `research/`

- [Researcher Handbook](research/researcher_handbook.md): reproducible experiment procedure and interpretation.
- [Reproducibility](research/reproducibility.md): environment, seeds, deterministic settings, and evidence policy.
- [Performance](research/performance.md): parallel backends, warmup, Numba, profiling, and measurement status.
- [Validation Report](research/validation_report.md): current parity evidence and remaining validation work.
- [EGSK Validation Appendix](research/egsk_validation_appendix.md): the paired port-vs-reference equivalence record for the Python EGSK optimizer (method, reproducible command, and measured agreement).
- [Numerical Examples](research/numerical_examples.md): small worked examples of init, seeds, bounds, fitness, statistics, and scheduling.
- [Statistical Analysis](research/statistical_analysis.md): the `gsk-stats` GSK-family comparison suite (Friedman ranks, Nemenyi CD, Wilcoxon/Holm, effect sizes, tables, and figures) plus the runner `--stats` live-report flag and the `papers/` review-pack workflow.

## Prompts - `prompt/`

- [Project Review](prompt/project-review.md): deep expert-team audit of the whole project (code, docs, tests, reproducibility).
- [Documentation Review](prompt/documentation-review.md): documentation consistency-and-accuracy gate (Part I) plus the inline docstring & comment review (Part II).
- [Documentation Deep Upgrade](prompt/documentation-deep-upgrade.md): the documentation-depth authoring spec (numerical examples, flowcharts, deep algorithm guides); the full-repo pass is complete — use it when adding a new page.
- [Publication Polish](prompt/publication-polish.md): the pre-publication hardening pass — repository-wide cleanup, documentation modernization, and Q1/GitHub/Zenodo release preparation.

## Python API

- [API Module Index](html/api_index.html): generated reference for every public module, class, and function, one page per module (also listed in the sidebar of the rendered site).
