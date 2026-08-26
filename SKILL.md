---
name: gsk-family-python
description: Deep project operating contract for working directly inside the DT-GSK repository root. Use whenever a task modifies, reviews, runs, validates, documents, benchmarks, tunes, packages, audits, cleans, or explains this project: GSK-family optimizer work (gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk), CEC benchmark campaigns (sphere, cec2011, cec2013, cec2013lsgo, cec2017, cec2020), the canonical runner and parallel-backend behavior, reference-matching RNG streams, byte-format result parity, documentation generation with its themed docs/ tree and HTML twins, reproducibility evidence, release polish, and the review-prompt suite.
---

# GSK Family Python — Operating Contract

This is the agent operating contract for the GSK Family Python project. Treat
the repository as production research software backing a PhD on the GSK
optimizer family. Preserve runnable behavior, documentation parity,
reproducibility evidence, result schemas, console output format, and any user
work already present. When in doubt, make the narrowest safe change and keep the
gates green.

## 1. What This Project Is

A pure-Python implementation of the **GSK (Gaining-Sharing Knowledge) optimizer
family** plus a self-contained Python port of several **CEC benchmark suites**.
It exists to run reproducible optimizer campaigns, to reproduce published
reference tables bit-for-bit from an external reference implementation, and to
produce the paper-grade statistical comparison that backs the proposed method
(`dt-gsk`).

- **Runnable optimizers (7):** `gsk`, `agsk`, `apgsk`, `fdb-agsk`,
  `atmals-gsk`, `egsk`, `dt-gsk`.
  - `dt-gsk` is **this project's proposed method** — Dimension-Tiered
    Gaining-Sharing Knowledge Optimization (the ISM interaction-structure
    memory survives as a component name only), byte-identically migrated from the source DT-GSK v2.1 tree.
    Its vendored core is `src/gsk_family/optimizers/_dt_core.py` (plus
    `_dt_profiles.py`, `_dt_rng.py`, and the `_dt_subsystems/` package); the
    family-facing adapter is `src/gsk_family/optimizers/dt_gsk.py`. It uses the
    unified threefry RNG and the shared `get_cec_seed` schedule like the rest of
    the family, but **self-initialises a `5*D` (`np_init_mult*D`) population** and
    therefore does not consume the runner's fair-start `initial_population` — a
    documented, intentional fair-start exception (see `dt_gsk.py` and
    `docs/algorithms/dt-gsk.md`).
  - **Result headline:** on the CEC2017 family panel (51 runs, 29 functions with
    F2 excluded), DT-GSK is **#1 in the GSK family by both mean and median** —
    #1 at D10/D50/D100 and #1 overall, with D30 led only by the strong `egsk`
    baseline (the runner-up overall). When
    citing a specific rank decimal, source it from `FINAL_RELEASE_REPORT.md`
    rather than hard-coding it. It ships a **default-on deep-stall multi-start**
    (`deep_stall_restart_enabled=True` in `DTGSKConfig`): when the incumbent
    stalls for `deep_stall_frac` (0.25) of the budget the working population fully
    re-initialises while a preserved global-best can never lose ground. This is a
    standard mechanism (not an `experimental_*` flag) that fixes the lone
    catastrophic basin trap (CEC2017 F30 D10) and stays byte-identical on
    non-stalling runs.
  - `egsk` is **both runnable and a reference comparator**: it now ships a real
    kernel (`optimizers/egsk.py`, MATLAB port with a `scipy`-SLSQP interior-point
    refinement substituting `fmincon`), so `--optimizer egsk` works. The
    statistical panel reports `egsk` from the committed `scipy`-SLSQP **port**
    CSVs (the comparator of record), not a MATLAB `fmincon` reference.
- **External SOTA baselines (8):** `mos-cec2013lsgo`, `shade-ils`, `decc-g`,
  `cmaes`, `ebowithcmar`, `jso`, `lshade`, `lshade-spacma`, in
  `src/gsk_family/optimizers/external/`. These are runnable too — the runner
  accepts all **15** ids — but the seven above are the statistical panel; these
  eight enter **no** panel, table, figure or claim, and the manuscript's scope
  stays GSK-family only. Three of them carry committed CEC2013LSGO banks under
  `benchmarks/cec_reference_results/_external_baselines/cec2013lsgo/` (`mos`,
  `shade-ils`, `decc-g`), retained as exploratory material and analysed nowhere
  in the paper. `optimizers/__init__.py` holds `FAMILY_OPTIMIZER_IDS` /
  `EXTERNAL_OPTIMIZER_IDS`, and `tests/test_registry_consistency.py` guards them
  against drift with `run_experiment.OPTIMIZER_FUNCTIONS`.
- **Suites (6):** `sphere`, `cec2011`, `cec2013`, `cec2013lsgo`, `cec2017`,
  `cec2020`. The CEC2017 **scored** set excludes F2 (functions F1, F3-F30)
  across D=10/30/50/100; the statistical loaders drop F2 accordingly.
  `cec2013` (28 functions, D=10/30/50, 51 runs) is the **second
  family-comparison suite**: a full 7-optimizer reference panel is committed
  for it alongside `cec2017` and `cec2011`.
- **Package:** `gsk_family` under `src/` (src-layout); `requires-python` is
  `>=3.10,<3.14` (`pyproject.toml`); the installed/running interpreter is
  CPython 3.10.
- **Runtime deps:** numpy, scipy, pandas, matplotlib, PyYAML, numba (see
  `pyproject.toml` / `requirements.txt` for pinned ranges).
- **Statistical + paper tooling:** the `src/gsk_family/analysis/` suite (driven
  by the `gsk-stats` console script / `src/gsk_family/cli/stats.py`) and the
  `papers/` review pack (`papers/scripts/generate_review_pack.py`). See §6 and
  the new statistical/paper section below.

## 2. Absolute Workspace Contract

Work **directly inside** the repository root — the DT-GSK
project folder.

Hard workspace rules:

- Do **not** create a separate agent project folder, worktree copy, or `.claude/`
  directory for this repo. This root is the shared working folder.
- Do **not** mirror the repository into a generated agent-only workspace or a
  nested temporary tree.
- Do **not** write generated experiment output into imported reference evidence
  (`benchmarks/cec_reference_results/`).
- Do **not** revert user changes unless explicitly asked.
- Do **not** delete retained evidence under `results/` unless explicitly asked.
- Do **not** edit the frozen manuscript under `papers/` outside a freeze pass.
  It is under change control (D-0045): a revision is a **new** pass, never an
  edit to the submitted state. Any change to a file tracked by
  `papers/governance/main_manuscript_freeze_manifest.json` (`main.tex`, the five
  `sections/*.tex`, `references.bib`, the built `.pdf`/`.docx` deliverables, and
  the three governance CSVs) voids that manifest until it is re-minted — so the
  derived figure/table generators in §6.2 are fine, but `build_pdf.py` and
  `build_docx.py` rebuild tracked deliverables and belong to a freeze pass.
- The append-only trees `papers/build_prompt_phases/`,
  `papers/review_2026_07_22/`, and `papers/governance/remediation_2026_07_18/`
  are **correct when stale** — do not "fix" them.
- Do **not** run `papers/scripts/finalize_evidence.py` (standing instruction);
  drive promotion manually.
- Agent (subagent) Bash calls reset the working directory between calls; always
  use **absolute paths** or `cd` into the root first.

## 3. Repository Layout

### 3.1 Root files

The project root holds a **current-state** file, an auto-loaded **session
brief**, three Markdown **operating** files, a newcomer **orientation map**, the
**governance** set, and the **release report** (do not add further root guides
or collapse these without an explicit request):

Current state — read before anything else:

- [`REVISION_STATUS.md`](REVISION_STATUS.md) — the single source of truth for
  *current* state: the editorial status of `algorithms-4507562`, which reviewer
  points are done vs open, the freeze pass, the open author decisions, and the
  verified trap table.
- `CLAUDE.md` — the short auto-loaded session brief; it points at
  `REVISION_STATUS.md` and carries the never-break invariants.

Operating files:

- `README.md` — landing page and command overview.
- `SKILL.md` — this operating contract (stays at the root).
- `runbook.md` — concise copy-paste command sheet (install, every suite, smoke,
  51-run sweeps, targeted runs, seed-policy reproduction, slow/crashing
  fallbacks). Keep it in sync with the runner contract below.
- [`REPO_MAP.md`](REPO_MAP.md) — one-screen newcomer orientation map (read order,
  top-level tree, the three invariants).

Governance / standards files (authored on request; the authoritative rules):

- [`PROJECT_RULES.md`](PROJECT_RULES.md) — the project "constitution" (workspace,
  evidence integrity, reproducibility, byte-identity, version-control policy, the
  green-gates rule). The rules hub linking the rest.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — package map, layering, data flow, the
  RNG/seed and results architecture.
- [`DESIGN_GUIDE.md`](DESIGN_GUIDE.md) — design principles + how to extend
  (add an optimizer/suite/CLI, the adapter pattern, the analysis layer).
- [`BENCHMARK_RULES.md`](BENCHMARK_RULES.md) — suite/experiment protocol (F2
  exclusion, dims, runs, budgets, CEC2011 per-dimension bounds, RNG/seed regime).
- [`CODING_STANDARD.md`](CODING_STANDARD.md) — code conventions enforced by the
  gates (ruff, the docstring gate + vendored exemptions, tests, docs-as-code).
- [`PERFORMANCE_RULES.md`](PERFORMANCE_RULES.md) — Numba, thread pinning for
  dt-gsk determinism, the parallel backend, workers, memory, incremental writes,
  and the fail-closed floating-point-regime sentinel.

Release report:

- [`FINAL_RELEASE_REPORT.md`](FINAL_RELEASE_REPORT.md) — the DT-GSK CEC2017
  per-dimension ranks, statistics, outlier audit, and publication-readiness
  decision.

Other root files: `run.py`, `pyproject.toml`, `requirements.txt`,
`requirements-dev.txt`, `MANIFEST.in`, `CITATION.cff`, `.gitignore`,
`.github/`.

> The deep-review prompts are **no longer at the root**. They live under
> `docs/prompt/` (see §3.4). Never reference them at root paths.

### 3.2 Source package `src/gsk_family/`

- `cli/` — console entry points (one `main()` per module): `run.py`, `list.py`,
  `validate.py`, `stats.py`. `stats.py` backs the `gsk-stats` console script and
  builds the GSK-family statistical comparison report.
- `runners/` — campaign machinery: `config.py` (config parsing / arg mapping),
  `run_experiment.py` (execution, backend self-healing), `parallel.py`
  (worker-count policy + scheduling), `output.py` (result writing + byte
  format), `seed_policy.py` (seed derivation; `SEED_POLICIES` tuple),
  `verification.py` (compare / validate), `performance.py` (profiling + runtime
  metadata), `fp_regime.py` (the fail-closed SHA-256 floating-point-regime
  sentinel; see [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md) and
  `docs/reference/fp_regime.md`).
- `optimizers/` — runnable adapters `gsk.py`, `agsk.py`, `apgsk.py`,
  `fdb_agsk.py`, `atmals_gsk.py`, `egsk.py`, `dt_gsk.py`. The `dt_gsk.py` adapter wraps a
  vendored core: `_dt_core.py`, `_dt_profiles.py`, `_dt_rng.py`, and the
  `_dt_subsystems/` package (`basin_memory.py`, `bound_constraint.py`,
  `budget.py`, `budget_policy.py`, `gained_shared_junior.py`,
  `gained_shared_senior.py`, `interaction_graph.py`, `_numba_accel.py`,
  `_dt_provenance.py`). Shared optimizer helpers: `_kernels.py`,
  `atmals_helpers.py`, `fdb_scores.py`. (`egsk.py` is a runnable MATLAB port; its
  panel cell is still reported from committed reference comparator data.)
- `common/` — shared building blocks: `rng.py` (`RandomContext`),
  `threefry_rng.py`, `reference_rng.py`, `population.py`, `bounds.py`,
  `donors.py`, `reduction.py`, `numeric_compat.py`.
- `benchmark_adapter/` — `factory.py`, `problem.py`, `protocol.py` (suite
  metadata, problem factory, benchmark interface).
- `analysis/` — the statistical + figure suite that powers `gsk-stats`:
  `family_report.py` (top-level report builder; `DEFAULT_PROPOSED`,
  `generate_family_report`), `statistical_tests.py` (Friedman ranks, pairwise
  Wilcoxon signed-rank, Holm correction, Vargha-Delaney A12 / Cliff's delta,
  win/tie/loss, BCa bootstrap), `result_loader.py` (`SUITE_DIMS`, mean-error
  loaders that drop CEC2017 F2), `figures.py` (Nemenyi critical-difference +
  rank PNGs), `latex_tables.py` (LaTeX fragments), `project_policy.py`
  (panel/comparator policy), and the `statistics.py` / `statistical_tests.py`
  primitives.
- `stats.py` — lightweight statistical summary helpers (distinct from the
  `analysis/` report suite).
- `types.py` — shared dataclasses / public data structures.

### 3.3 Non-source directories

- `benchmarks/cec_suite_python/` — active Python benchmark runtime (per-suite
  subpackages `cec2011`, `cec2013`, `cec2013lsgo`, `cec2017`, `cec2020`, each
  with packaged `data.pkl` where applicable). **Active code.**
- `benchmarks/cec_reference_results/` — imported, read-only reference evidence.
  **Immutable** unless the user requests provenance/data maintenance.
- `configs/` — 8 top-level YAML campaign configs + `README.md`:
  `smoke.yml`, `all_optimizers_smoke.yml`, `all_cec2017.yml`,
  `all_optimizers_cec2017_reduced.yml`, `all_cec2011.yml`, `agsk_cec2020.yml`,
  `golden_validation_smoke.yml`, `performance_campaign_smoke.yml`. Pass any of
  these to `--config` instead of long flag lists; the per-suite launchers in
  `scripts/` wrap them. Subfolders: `publish/` (the final publication campaign),
  `experimental/` (diagnostics), and the generated `_ablation/` (per-cell
  ablation configs written by `scripts/run_ablation.py`).
- `scripts/` — 14 launcher/tooling scripts + `README.md` (see §3.5).
- `docs/` — themed Markdown + generated HTML (see §3.4).
- `results/` — generated experiment and audit evidence (git-ignored content
  except retained evidence the user keeps).
- `tests/` — test tiers (see §8).

### 3.4 Documentation tree `docs/`

Markdown is organized into themed subfolders, not a flat `docs/*.md`:

- `docs/index.md`, `docs/LICENSES.md`, `docs/index.html` — landing + licenses.
- `docs/getting-started/` — `user_guide`, `tutorial`, `runbook`,
  `configuration`, `troubleshooting`, `explainer`.
- `docs/reference/` — `architecture`, `api`, `python_optimizer_interface`,
  `module_dependencies`, `workflows`, `result_schema`, `seed_policy`,
  `benchmark_protocol`, `benchmark_mapping`, `diagrams`, `project_structure`,
  `glossary`, plus the per-suite C++/Python equivalence reviews
  `cec2011_cpp_python_equivalence_review`, `cec2013_cpp_python_equivalence_review`,
  `cec2013lsgo_cpp_python_equivalence_review`,
  `cec2017_cpp_python_equivalence_review`,
  `cec2020_cpp_python_equivalence_review`.
- `docs/algorithms/` — `gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`,
  `egsk`, `dt-gsk` (one page per runnable optimizer).
- `docs/development/` — `README` (folder index), `developer_guide`,
  `contributor_guide`, `maintenance_guide`, `extension_guide`,
  `code_reading_guide`, `dt_gsk_core_reference`, `evidence_rerun_runbook`,
  `egsk_port_spec`, plus `history/` with the archived historical records
  (`dt_migration_plan`, `dt_trap_fix_plan`, `dt_reference_rootcause`,
  `dt2_oracle_program`).
- `docs/research/` — `researcher_handbook`, `reproducibility`, `performance`,
  `validation_report`, `numerical_examples`, `statistical_analysis` (the
  `gsk-stats` / statistical-suite reference page).
- `docs/prompt/` — the prompt suite (**4 files**): `project-review.md`
  (whole-project audit), `documentation-review.md` (docs consistency gate +
  inline docstring/comment review), `documentation-deep-upgrade.md` (deep docs
  upgrade), and `publication-polish.md` (release-hardening pass). The one-time
  DT-GSK migration/publish/doc-polish prompts were completed and removed.
- `docs/html/` — generated static site (see §7).

The root `runbook.md` is the quick copy-paste sheet;
`docs/getting-started/runbook.md` is the in-site page. Keep both consistent when
run commands change.

### 3.5 Scripts `scripts/`

Per-suite campaign launchers (parameters fixed inside `configs/*.yml`):

- `run_all_cec2017.py`, `run_all_cec2011.py`, `run_all_cec2020.py`,
  `run_all_cec2013.py`, `run_all_cec2013lsgo.py`
- `run_gsk_family.py` — generic family launcher.
- `run_ablation.py` — DT-GSK scaffold ablation driver: toggles six mechanisms
  (ACE, NLPSR, BSE, linkage-blockwise crossover, coordinate local search,
  elite archive) plus a baseline cell — 7 cells, with the SGSM interaction
  graph off in every cell. Flags: `--suite {cec2017,cec2011,cec2013}`
  (`cec2011` uses native dims), `--mode {remove-one,add-one}`, `--dimension`,
  `--runs` (default 25), `--workers`, `--only`, `--dry-run`. Writes generated
  configs to `configs/_ablation/<cell>.yml` and results to
  `results/_ablation/<cell>/dt-gsk/<suite>/`; aggregate the cells with
  `papers/scripts/generate_ablation_matrix.py`.

Tooling:

- `build_docs_html.py` — documentation HTML builder (run by the orchestrator;
  do not invoke it yourself when the orchestrator owns the HTML rebuild).
- `validate_profile_lock.py` — profile-lock guard (`--root .`).
- `parity_trace.py` — RNG / reference parity tracing helper.
- `wilcoxon_reference.py` — pairs the port's per-function statistic (mean error
  by default) against the imported reference table per optimizer and dimension,
  runs a Wilcoxon signed-rank test on the paired differences, and reports the
  win/tie/loss split, signed-rank sums, p-value, and significance verdict.
- `validate_egsk_vs_reference.py` — validates the runnable `egsk` kernel against
  the committed MATLAB-`fmincon` reference tables (statistical-equivalence check).
- `analyze_dt_diagnostics.py` — post-processes the opt-in dt-gsk diagnostics
  JSONL traces into per-subsystem summaries and wrong-basin candidates.
- `plot_convergence_from_curves.py` — renders convergence PNGs from committed
  curve CSVs without re-running a campaign.

> There are no removed per-phase runner/build scripts and no obsolete staged
> workflow. They were removed. Never reference them.

## 4. Canonical Runner Contract

`run.py` is the canonical source-checkout runner. It prepends `src/` to
`sys.path` and calls `gsk_family.cli.run:main`. Installed console entry points
(from `pyproject.toml [project.scripts]`, **5 total**):

| Console script | Module target | Purpose |
| --- | --- | --- |
| `gsk-run` (alias `gsk-family-run`) | `gsk_family.cli.run:main` | Run optimizer campaigns. |
| `gsk-list` | `gsk_family.cli.list:main` | List optimizers / benchmarks / references. |
| `gsk-validate` | `gsk_family.cli.validate:main` | Validate or compare against reference evidence. |
| `gsk-stats` | `gsk_family.cli.stats:main` | Build the GSK-family statistical comparison report. |

`gsk-stats` is documented in `docs/research/statistical_analysis.md`. The
console scripts and `python run.py` accept the same campaign flags; prefer
`python run.py` in a source checkout so `src/` is on `sys.path` without an
install.

Help (always check live flags before scripting a sweep):

```powershell
python run.py --help
```

Tiny direct smoke (seconds):

```powershell
python run.py --root . --optimizer gsk --suite sphere --function 1 --dimension 4 --runs 1 --max-evaluations 80 --overwrite
```

Config-driven smoke:

```powershell
python run.py --root . --config configs/smoke.yml
```

Full CEC2017, all optimizers, 51 runs:

```powershell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
```

(`--function 1:30` selects the CEC2017 range; the suite excludes F2, so the
**scored** set is F1, F3-F30 = 29 functions, and the statistical loaders drop
F2 from every panel.) `--overwrite` recomputes; omit it to **resume** (finished
cells are skipped). The root `runbook.md` has copy-paste sweeps for every suite
plus the fallbacks.

Common campaign flags (verify against `python run.py --help` before scripting):

- `--root .` — project root anchor (results land under `results/_run_all/`).
- `--optimizer a,b,c` — comma-separated runnable ids (now includes `egsk`).
- `--suite NAME` — one of the 6 suites.
- `--function 1:30` (range) or `--function 1,3,5` (explicit list).
- `--dimension 10,30,50,100` — comma-separated dimensions.
- `--runs N` — independent runs per cell (51 for a full statistical campaign).
- `--max-evaluations N` — explicit budget override (smoke runs only; full
  campaigns use the suite's protocol budget).
- `--parallel` / `--serial`, `--workers N`, `--parallel-backend {process,thread}`.
- `--convergence-graphs` / `--no-convergence-graphs`.
- `--overwrite` (recompute) vs. resume (default, finished cells skipped).
- `--seed-policy {reference,unified,native,derived}` (see §10).
- `--stats` (opt-in live statistical analysis; see below).
- `--benchmark-backend {auto,python}` (both use the Python evaluator) and
  `--benchmark-fp-mode {default,strict}`.

Do / don't for user-facing campaign commands:

- **Do** keep `--parallel --workers 2` visible so the resource choice is explicit
  and safe for shared machines.
- **Do** keep `--convergence-graphs` visible when rendered PNG curves are wanted;
  omit it for CSV-only curve output (median-run curve CSVs are always written).
- **Do** let users raise `--workers N` deliberately after they confirm CPU and
  memory headroom.
- **Don't** use `--serial` except for single-process troubleshooting (slowest
  path, always completes).
- **Don't** use `--parallel-backend thread` for real campaigns (diagnostic only;
  see §5).

The runner also accepts the opt-in `--stats` flag (default **off**, defined in
`src/gsk_family/cli/run.py`): when set, it streams the per-dimension
Wilcoxon + Friedman analysis live after each dimension completes (it skips
vanilla `gsk`; the native-dimension `cec2011` is supported and emits a single
per-suite rollup panel now that CEC2011 reference rollups are committed).
Without `--stats` the runner prints only the summary plus the
single-baseline mean comparison. `--stats` is for **live feedback during a
run**; it does not write the figure/CSV/LaTeX artifacts.

The standalone `gsk-stats` command is the way to produce the publication
artifacts **after** a run: a 7-algorithm Friedman panel with mean ranks,
pairwise Wilcoxon signed-rank tests with Holm correction and Vargha-Delaney /
Cliff's-delta effect sizes, Nemenyi critical-difference diagrams, rank charts,
and LaTeX fragments. It loads all seven algorithms — the proposed `dt-gsk`
included — **reference-first** from the committed panel
`benchmarks/cec_reference_results/<suite>/<optimizer>/` (the single source of
truth for paper statistics), falling back to
`results/_run_all/<optimizer>/<suite>/summary/` only for cells the reference
tree lacks, and writes to `results/_run_all/_analysis/<suite>/` (see §6.1 and
`docs/research/statistical_analysis.md`).

```powershell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 4 --convergence-graphs --overwrite
```

## 5. Parallelism, Workers, and Numba

Preserve these defaults (defined in `src/gsk_family/runners/parallel.py` and
`run_experiment.py`):

- Parallel execution is **on by default**; the default backend is **`process`**
  (true multi-core, no GIL contention).
- Convergence graph PNG generation is **off by default** for direct CLI runs.
  `--convergence-graphs` / `convergence_graphs: true` enables PNG rendering;
  median-run curve CSVs are still written when PNG graphs are not requested.
- Automatic worker count is intentionally conservative: 2 workers on machines
  with at least two logical CPU cores, otherwise 1 worker
  (`DEFAULT_WORKER_COUNT = 2`). This prevents a copied no-flag command from
  consuming a large shared workstation.
- Automatic CEC2017 composition cells (`F21`-`F30`) on the default `process`
  backend retain an effective memory-safety cap of 8 workers. The normal
  two-worker default is already below this cap, but the cap protects future
  automatic settings. Explicit `--workers N` values are treated as
  user-selected speed/memory overrides.

Override knobs (only when the user asks):

- `--workers N` — choose parallel concurrency intentionally. Start at 2 for
  shared machines; increase to 4, 8, or higher only after checking available CPU
  and memory.
- `--convergence-graphs` / `--no-convergence-graphs` — control rendered PNG
  convergence plots without affecting the required convergence CSV artifacts.
- `--serial` — single-process fallback; slowest path but always completes.
- `--parallel-backend {process,thread}` — **do not use `thread` for real
  campaigns.** Parallel Numba kernels can deadlock when driven from many Python
  threads. `thread` is diagnostic-only.

Backend self-healing (preserve, do not weaken):

- On a worker death (`BrokenProcessPool` from a transient Numba/spawn crash or
  OOM), the `process` backend tears down the pool, rebuilds it, and retries the
  cell up to a bounded number of attempts (currently 3).
- If rebuilds keep failing, that cell finishes on the **serial** backend, then a
  fresh pool is rebuilt for the next cell — so a campaign never hangs and never
  aborts on a transient crash.
- The `process` backend must **never** fall back to `thread` on a crash (that
  many-threads-into-parallel-Numba path can deadlock).

When tuning performance, preserve: seed schedules, RNG draw order where behavior
depends on it, evaluation counts, deterministic result ordering, output schema,
reference-facing behavior, and the self-heal / no-thread-fallback rules. Prefer
profiling evidence over intuition. Rationale lives in
`docs/research/performance.md`.

## 6. Statistical Analysis and Paper Review Pack

The statistical evidence backing the proposed method has two producers: the
`gsk-stats` console script (a CLI over `src/gsk_family/analysis/`) and the
`papers/` review pack. Both consume already-generated run output plus the
committed reference tables; neither re-runs an optimizer.

### 6.1 `gsk-stats` statistical suite

`gsk-stats` (`src/gsk_family/cli/stats.py` -> `analysis/family_report.py`)
builds the 7-algorithm **GSK-family panel**: 6 reference comparators (`gsk`,
`agsk`, `apgsk`, `fdb-agsk`, `egsk`, `atmals-gsk`) plus the proposed `dt-gsk`.
It produces Friedman ranks, a Nemenyi critical-difference diagram, pairwise
Wilcoxon signed-rank tests with Holm correction, Vargha-Delaney A12 / Cliff's
delta effect sizes, win/tie/loss splits, BCa bootstrap intervals, LaTeX table
fragments, and CD + rank PNGs.

- **Inputs:** **reference-first** — all seven algorithms (the proposed
  `dt-gsk` included) are read from the committed panel
  `benchmarks/cec_reference_results/<suite>/<optimizer>/`, the single source of
  truth for paper statistics; a locally reproduced run under
  `results/_run_all/<optimizer>/<suite>/summary/` is only a fallback for cells
  the reference tree lacks. Full panels are committed for CEC2017, CEC2011,
  and CEC2013.
- **Output:** `results/_run_all/_analysis/<suite>/` (override with `--out`).
- **Key flags:** `--suite` (default `CEC2017`), `--dims` (comma-separated;
  defaults to the suite's standard set via `analysis/result_loader.py`
  `SUITE_DIMS`), `--proposed` (default `dt-gsk`), `--results-root`,
  `--reference-root`, `--out`, `--alpha` (default `0.05`), `--no-figures`.
- The loaders **exclude CEC2017 F2** from every panel, matching the scored set.

```powershell
# After a full dt-gsk CEC2017 run, build the panel + figures + LaTeX
gsk-stats --suite CEC2017 --dims 10,30,50,100

# CEC2011 panel, tables only (skip matplotlib figures)
gsk-stats --suite CEC2011 --no-figures
```

Exit code is `1` when no usable data is found (e.g. the reference base or
reproduced summaries are missing) so the absence of evidence is never silently
reported as a pass.

### 6.2 `papers/` review pack

`python papers/scripts/generate_review_pack.py` renders the advisor review PDF
`papers/DT-GSK-CEC2017-review.pdf` using matplotlib `PdfPages` (**no LaTeX
required**; MiKTeX is only needed for the full `papers/main.tex` manuscript). It
draws the 7-algorithm convergence grids (GSK, AGSK, APGSK, FDB-AGSK, eGSK,
ATMALS-GSK, DT-GSK) from `CheckpointErrors_<alg>_F<k>_D<dim>.csv` curve files.

- Missing curves are logged to
  `papers/DT-GSK-CEC2017-review_missing.log` and **never fabricated** — a gap
  in the grid means the underlying run/curve is absent, not invented.
- Other `papers/scripts/` generators (e.g. `generate_nemenyi_cd.py`,
  `generate_rank_charts.py`, `generate_latex_tables.py`,
  `generate_full_convergence.py`, `generate_cec2011_convergence.py`,
  `generate_cec2013_convergence.py`, `generate_ablation_matrix.py`,
  `build_pdf.py`, `build_docx.py`) build individual figures/tables for the
  manuscript; treat their outputs as derived. The convergence-figure
  generators read curves and gen_logs from
  `benchmarks/cec_reference_results/<suite>/<optimizer>/`;
  `generate_ablation_matrix.py` aggregates the `scripts/run_ablation.py` cells
  into `results/ablation/` rank-summary CSVs that
  `generate_latex_tables.py` renders as `papers/tables/ablation_<tag>.tex`.

```powershell
# Advisor review pack -> papers/DT-GSK-CEC2017-review.pdf (no LaTeX needed)
python papers/scripts/generate_review_pack.py
```

## 7. Documentation Generation and HTML Twins

After **any** change to Markdown under `docs/`, to docstrings, to README
commands, to navigation, or to the review prompts, rebuild the static site and
**commit the regenerated `docs/html/` twins** alongside the source change:

```powershell
python scripts\build_docs_html.py
```

How it works (for accurate expectations):

- The builder walks **every** `docs/**/*.md` (`rglob("*.md")`) and also renders
  the package API from `src/`.
- Generated HTML page names are **flattened** to `<subfolder>_<page>.html`,
  preserving any literal hyphen in the subfolder name. Examples:
  `docs/reference/seed_policy.md` → `docs/html/reference_seed_policy.html`;
  `docs/algorithms/fdb-agsk.md` → `docs/html/algorithms_fdb-agsk.html`;
  `docs/prompt/project-review.md` → `docs/html/prompt_project-review.html`.

When adding or moving docs:

- Update `docs/index.md` (and `docs/reference/project_structure.md` if the
  structure changes).
- Update documentation smoke tests if expected file paths change.
- Update any audit scripts that assert required docs.
- Rebuild HTML and commit the twins; run the documentation smoke test (§8).

Keep these synchronized: source Markdown, generated HTML, API pages, search
index, README commands, root `runbook.md` ↔ `docs/getting-started/runbook.md`,
and the `docs/prompt/` review prompts.

## 8. Gates — Keep These Green

Run targeted checks for narrow edits; run the full sequence for broad changes.

**Tests** (the suite currently collects **324** tests across the tiers below;
re-check with `python -m pytest --collect-only -q` rather than hard-coding a
number into new docs):

```powershell
python -m pytest -q
```

Test tiers: `tests/unit/` (RNG known-answer tests, statistical primitives,
docstrings, figures, etc.), `tests/smoke/` (CLI smoke, the documentation-command
smoke), `tests/regression/`, `tests/performance/`, plus the top-level
`tests/test_imports.py`. The `slow` marker gates optional scalability checks
(`python -m pytest -m slow` to include them, `-m "not slow"` to skip).

Documentation smoke only (resolves the fixed required-doc list, including this
`SKILL.md` and the required `docs/prompt/` files):

```powershell
python -m pytest tests\smoke\test_documentation_commands.py -q
```

> The required-doc list lives in `tests/smoke/test_documentation_commands.py`.
> If a doc is added or moved, that list (and the matching `docs/html/` twins)
> must stay in sync or this gate fails.

**Lint** (Ruff, scoped to source/tests/scripts — matches CI; rules `E9`,`F`,
line length 120):

```powershell
python -m ruff check src tests scripts
```

**Docs build** (after any docs/docstring change — commit the `docs/html/`
twins):

```powershell
python scripts\build_docs_html.py
```

**Profile lock** (guards the locked run profile):

```powershell
python scripts\validate_profile_lock.py --root .
```

Optional selected type check (scoped to keep the broad command green under
NumPy 2.x churn):

```powershell
python -m mypy src/gsk_family/cli src/gsk_family/runners src/gsk_family/common
```

Preferred broad verification sequence:

```powershell
python -m pytest -q
python -m ruff check src tests scripts
python scripts\validate_profile_lock.py --root .
python scripts\build_docs_html.py
```

**Manuscript and evidence gates** — only when `papers/` or an evidence tree is
in scope. All three take optional arguments only, so they run bare:

```powershell
python papers\scripts\check_manifest.py
python papers\scripts\check_frozen_analysis.py
python papers\scripts\validate_provenance_claims.py
```

At freeze pass-40, `check_manifest.py` reads **15/15** against its default
`papers/governance/main_manuscript_freeze_manifest.json` (`--manifest` is
repeatable for the other governance manifests), and `check_frozen_analysis.py`
reads **115/115** byte-identical against the primary release. Note that
`check_manifest.py` hashes the **working tree**, not the committed blob —
confirm committed bytes with `git cat-file -s`.
`validate_provenance_claims.py` hashes `src/gsk_family/optimizers/_dt_core.py`
on a SHIPPED list, so **even a comment edit fails it**; §11 treats that vendored
core as reference-locked for the same reason. Never run
`papers/scripts/finalize_evidence.py`.

If a gate is too expensive to run, say exactly which command was deferred and
why.

## 9. Results and Byte-Format Parity

Default generated output tree:

```text
results/_run_all/<optimizer>/<suite>/
```

Each campaign writes per-run artifacts, function-level summaries,
optimizer/suite summaries, `seed_schedule.csv`, `environment.json`, an optional
`profile.json`, median-run convergence CSVs, convergence graph PNGs when
enabled, generation/checkpoint logs when enabled, and validation comparison
reports.

**Byte-format parity is intentional and load-bearing** — the console output and
`results/` files are deliberately mirrored to a sibling reference project so the
two can be diffed. Do not "normalize" these away (see
`src/gsk_family/runners/output.py`):

- `per_run.csv` best/error fields are formatted `%.10e`.
- Convergence-curve values are formatted `%.16e` (with a matching `log10`
  column).
- Preserve the `environment.json` key order and other documented format
  details.

Generated / derived locations (safe to clear as transient caches during polish,
**except** retained `results/` evidence which needs explicit consent):
`results/`, `docs/html/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`,
`__pycache__/`, `*.pyc`, `*.nbc`, `*.nbi`.

## 10. Seed Policies and the RNG Contract

`run.py`/`gsk-run` accept `--seed-policy` with choices
`("reference", "unified", "native", "derived")` (`src/gsk_family/runners/seed_policy.py`).

- **`unified`** — default. Matches reference means within statistical noise. The
  seed is the linear `get_cec_seed` modular formula over `(base, dim, func, run)`
  only — **optimizer-independent**, shared across the family; it is **not**
  hashed.
- **`reference`** — reproduces the published tables bit-for-bit for GSK, AGSK,
  APGSK, and ATMALS-GSK (FDB-AGSK diverges on the floating-point residual, see
  `docs/reference/seed_policy.md`); forces the per-optimizer reference seeding
  and generator label.
- **`native` / `derived`** — diagnostic variants using the hashed `derive_run_seed`
  derivation (a character-sum over the optimizer/suite names).

`RandomContext` (`src/gsk_family/common/rng.py`) supports exactly three
reference-matching generators selected by the `rand_generator` label; `threefry`
is the default and each reproduces its external reference stream bit-for-bit:

- `threefry` → Threefry-4x64-20 (`threefry_rng.py`): key `(0,0,0,0)`, counter
  `((S+2j+1) << 32) | (S+2j)`, four doubles/block via `(word >> 11) * 2^-53`.
- `twister` → MT19937 (`reference_rng.py`): `init_genrand(seed)` seeding,
  `genrand_res53` doubles.
- `seed` → mcg16807 / Park-Miller (`reference_rng.py`):
  `x0 = (seed << 16) mod (2^31 - 2^15)`, then `x <- 16807*x mod (2^31 - 1)`.

RNG rules:

- Matrix draws fill **column-major**; a `(k, m, n)` request is `k` successive
  column-major `(m, n)` draws. Integer draws use `floor(imax*rand) + 1`;
  permutations use `argsort(rand(n))`.
- Do **not** add NumPy bit generators (Philox, PCG64, plain MT19937) as labels.
  Any label outside `{threefry, twister, seed}` must raise "Unsupported RNG
  generator".
- The v5 `state` generator (swb2712) is intentionally absent and must not be
  re-added as a NumPy placeholder.
- Parity is bit-exact for the rand-only optimizers (GSK, AGSK, APGSK,
  ATMALS-GSK); residual gaps are benchmark floating-point only. FDB-AGSK
  (score-ranked selection) can diverge late on floating-point sensitivity, not
  RNG.
- Do not change any generator's seeding, conversion, or draw order without
  re-verifying against reference draws. Known-answer tests live in
  `tests/unit/test_rng.py`. The full derivation is documented in
  `docs/reference/seed_policy.md`.

## 11. Optimizer and Benchmark Rules

Optimizer edits:

- Keep algorithm logic stable unless an algorithmic change is explicitly
  requested. Preserve option names/defaults, the result dataclass structure,
  bounds-repair behavior, population init / fair-start handling, evaluation-budget
  accounting, and local-search behavior/metadata.
- `dt-gsk` is the **proposed method** and is byte-identically vendored from the
  source DT-GSK v2.1 tree (`_dt_core.py`, `_dt_profiles.py`, `_dt_rng.py`,
  `_dt_subsystems/`). Treat the vendored core as reference-locked: do not
  refactor it casually. Its `5*D` (`np_init_mult*D`) self-init is the documented
  fair-start exception (see `dt_gsk.py` notes and `docs/algorithms/dt-gsk.md`).
- `egsk` is **runnable** (`optimizers/egsk.py`, MATLAB port; `scipy`-SLSQP
  interior-point refinement substitutes `fmincon`) and **also** a reference
  comparator: the statistical panel reports its cells from the committed
  MATLAB-`fmincon` reference CSVs, not from a fresh local run.
- Keep optimizer tests aligned with behavior; update the matching
  `docs/algorithms/<id>.md` when behavior, options, or artifacts change.
  High-risk changes require targeted tests **and** doc updates.

Benchmark edits:

- `benchmarks/cec_suite_python/` is the active runtime tree;
  `benchmarks/cec_reference_results/` is immutable reference evidence.
  Generated results go under `results/`, never under reference evidence.
- Default `benchmark_backend=auto` uses the Python/Numba evaluator. Do not
  bypass the benchmark adapter from inside an optimizer.
- Keep suite metadata consistent across docs, configs, runner defaults, tests,
  and validation code. When changing benchmark behavior, verify function IDs,
  dimensions, native-dimension handling, optima/target errors, max-evaluation
  behavior, excluded/unsupported functions, and that Numba and non-Numba paths
  stay consistent.

## 12. Validation Rules

Validation must be truthful — never report a pass when functions were skipped.

```powershell
gsk-list --optimizers --benchmarks --references benchmarks/cec_reference_results
gsk-validate --references benchmarks/cec_reference_results
gsk-validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

(Source-checkout equivalent: `python -m gsk_family.cli.validate --references benchmarks/cec_reference_results`.)

Expectations to preserve: `gsk-validate` reports missing references clearly;
all-skipped validation exits **nonzero**; comparisons state how many
generated/reference pairs were checked; reduced validation is labeled as reduced
evidence; full-campaign evidence requires full-campaign commands.

## 13. Terminology and the Forbidden Token

Use Python-first terminology in active code and docs. Prefer: "imported
reference evidence", "external reference source", "reference-compatible",
"source evidence", "seed-policy exception", "Python runtime", "Python benchmark
adapter".

Do **not** imply that the external reference runtime is required for normal
Python execution, that reduced smoke checks prove full-budget equivalence, that
generated results are reference evidence, or that validation passed when all
functions were skipped.

**Platform-name rule:** the upstream numeric-computing platform's product name
is used in this repository **only for factual provenance** — naming the
lineage of the vendored eGSK reference port, and the seed-policy exception in
`docs/reference/seed_policy.md` that documents the reverse-engineered reference
streams. It must never be used to describe *this* project's own runtime, which
is pure Python: this implementation does not require, invoke, or depend on that
platform. (Earlier revisions of this rule banned the token outside
`seed_policy.md` altogether; that scope was never actually in force — the
provenance uses are legitimate and appear throughout the governance and
architecture documents — and it was corrected on 2026-08-01, audit finding
HYG-12.)

## 14. Editing, Review, and Reporting Protocol

Before editing: inspect the relevant files, check for user changes in the area,
learn local patterns, and pick the narrowest safe change.

During editing: reuse existing helper APIs; prefer structured parsers / project
helpers over ad hoc string handling; keep abstractions conservative; avoid
unrelated refactors; keep comments short; use `# noqa` only for intentional
compatibility or justified unused calculations.

After editing: run targeted tests; rebuild docs and commit the `docs/html/`
twins if docs/docstrings changed; clear transient caches only if polish was in
scope; summarize changed files, the validation commands run, and residual risks.

Reviews: lead with findings ordered by severity; give exact file paths and line
numbers; separate bugs from risks, missing tests, stale docs, and ideas; keep
the summary short; state clearly when nothing is wrong.

The `docs/prompt/` suite (**4 files**), and when to reach for each:

- Whole-project expert audit: `docs/prompt/project-review.md`.
- Documentation review: `docs/prompt/documentation-review.md` (Part I docs
  consistency-and-staleness gate; Part II inline docstring & comment review).
- Deep documentation upgrade: `docs/prompt/documentation-deep-upgrade.md`
  (raise `docs/` to a professional reference — numerical examples, flowcharts).
- Publication polish: `docs/prompt/publication-polish.md` (the pre-publication
  hardening pass — cleanup, doc modernization, release prep).

## 15. Quick Reference Card

```powershell
# Discover (5 console scripts: gsk-run/gsk-family-run, gsk-list, gsk-validate, gsk-stats)
python run.py --help
gsk-list --optimizers --benchmarks --references benchmarks/cec_reference_results

# Smoke (seconds)
python run.py --root . --optimizer gsk --suite sphere --function 1 --dimension 4 --runs 1 --max-evaluations 80 --overwrite

# Full CEC2017, all 7 runnable optimizers (egsk runs via the scipy-SLSQP port, but the paper panel reads egsk from committed reference CSVs; omit --overwrite to RESUME)
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite

# Same campaign, increased worker count (only after checking CPU/memory headroom)
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 4 --convergence-graphs --overwrite

# Live per-dimension Wilcoxon+Friedman during the run (opt-in)
python run.py --root . --optimizer agsk,apgsk,fdb-agsk,atmals-gsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30 --runs 51 --parallel --workers 2 --stats

# GSK-family statistical comparison artifacts AFTER a run (figures/CSV/LaTeX)
gsk-stats --suite CEC2017 --dims 10,30,50,100

# Advisor review pack -> papers/DT-GSK-CEC2017-review.pdf (no LaTeX needed)
python papers/scripts/generate_review_pack.py

# DT-GSK scaffold ablation (7 cells -> results/_ablation/; aggregate with generate_ablation_matrix.py)
python scripts/run_ablation.py --suite cec2017 --dimension 30 --runs 25 --workers 2

# Validate against imported reference evidence
gsk-validate --references benchmarks/cec_reference_results
gsk-validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results

# Gates
python -m pytest -q
python -m ruff check src tests scripts
python scripts\validate_profile_lock.py --root .
python scripts\build_docs_html.py

# Reproduce published tables bit-for-bit
python run.py <args> --seed-policy reference
```

Expected root Markdown inventory (exactly these thirteen, sorted):

```text
ARCHITECTURE.md
BENCHMARK_RULES.md
CLAUDE.md
CODING_STANDARD.md
DESIGN_GUIDE.md
FINAL_RELEASE_REPORT.md
PERFORMANCE_RULES.md
PROJECT_RULES.md
README.md
REPO_MAP.md
REVISION_STATUS.md
SKILL.md
runbook.md
```
