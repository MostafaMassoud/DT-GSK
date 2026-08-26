# Repository Map — start here

A one-screen orientation for a newcomer. For the full structural reference see
[ARCHITECTURE.md](ARCHITECTURE.md); for the *why* behind the design see
[DESIGN_GUIDE.md](DESIGN_GUIDE.md).

## What this project is

PhD research software for the **GSK optimizer family**. Three cooperating parts,
one pure-Python package:

1. **Optimizer runtime** — one contract, two groups. The **seven-algorithm family
   panel** that every published claim is scoped to (`gsk, agsk, apgsk, fdb-agsk,
   atmals-gsk, egsk`, and the proposed **`dt-gsk`**), plus eight **non-GSK
   externals** under `optimizers/external/` (`cmaes, decc-g, ebowithcmar, jso,
   lshade, lshade-spacma, mos-cec2013lsgo, shade-ils`). The externals are
   exploratory and sit **outside the panel**; no manuscript claim rests on them.
2. **CEC benchmark runtime** — five CEC suites (`cec2011, cec2013, cec2013lsgo,
   cec2017, cec2020`) turned into deterministic, reproducible result tables, plus
   a `sphere` smoke problem. See `benchmark_adapter/protocol.py`:
   `CEC_SUITES` is the five; `SUPPORTED_SUITES` adds `sphere`.
3. **Analysis & paper tooling** — the `gsk-stats` statistical panel and the
   `papers/` manuscript pipeline.

> **Current state** — the manuscript is under **major revision** at *Algorithms*
> (MDPI). Read [REVISION_STATUS.md](REVISION_STATUS.md) before changing anything
> under `papers/`; [CLAUDE.md](CLAUDE.md) is the short session entry point.

## Read order for a new developer

1. [README.md](README.md) — what it is and how to run it.
2. [ARCHITECTURE.md](ARCHITECTURE.md) — the structural map (layers, contract, flow).
3. [DESIGN_GUIDE.md](DESIGN_GUIDE.md) §1 — the six design principles.
4. Trace one run: `run.py` → `cli/run.py` → `runners/run_experiment.py` →
   `optimizers/gsk.py` → `runners/output.py`.

## Top-level tree

```
run.py                     Canonical entry point -> cli.run:main
pyproject.toml             Packaging, console scripts, tool config
CLAUDE.md                  Session entry point (auto-loaded; short, pointer-only)
REVISION_STATUS.md         CURRENT STATE: peer review, progress, next steps
REPO_MAP.md                This file
ARCHITECTURE.md            Structural map        DESIGN_GUIDE.md   Rationale & how-to
PROJECT_RULES.md           Governance "constitution"
CODING_STANDARD.md  BENCHMARK_RULES.md  PERFORMANCE_RULES.md   Domain standards
README.md  SKILL.md  runbook.md   Landing / agent contract / copy-paste commands
FINAL_RELEASE_REPORT.md    HISTORICAL: CEC2017 ranks, pre-submission (not current state)

src/gsk_family/            The package (each dir has its own README):
  cli/                     Console entry points (gsk-run, gsk-list, gsk-validate, gsk-stats)
  runners/                 Orchestration: config, run loop, process pool, seeds,
                           output writers, and fp_regime.py (FP-regime guard)
  optimizers/              The 7 family optimizers; dt-gsk = adapter + VENDORED locked
                           core (_dt_core.py, _dt_subsystems/, _dt_rng.py, _dt_profiles.py)
    external/              8 non-GSK optimizers (cmaes, decc-g, ebowithcmar, jso,
                           lshade, lshade-spacma, mos-cec2013lsgo, shade-ils).
                           Exploratory, outside the published panel.
  common/                  Shared blocks: RNGs, population, bounds, donors, reduction
  benchmark_adapter/       problem / factory / protocol — CEC suites behind one contract
  analysis/                Statistics core, loaders, family report, figures, LaTeX
  types.py  stats.py       Public dataclasses; error/summary helpers

benchmarks/
  cec_suite_python/        Benchmark data + Numba kernels (the default data_root)
  cec_reference_results/   READ-ONLY reference panel — single source of truth for
                           paper statistics. Full 7-optimizer panels on ALL FIVE
                           CEC suites; plus _ablation/ (1297 files), _revision/ (252 files,
                           round-1 revision experiments), _external_baselines/,
                           _paper_tables/, _index/. Never edit; never "regenerate".

configs/                   YAML experiment configs (+ experimental/, publish/,
                           generated _ablation/)
scripts/                   Campaign launchers, ablation driver (run_ablation.py),
                           docs builder, validators, diagnostics
papers/                    LaTeX manuscript + review-pack pipeline; governance/ holds
                           the decision log and the freeze manifests; analysis/ the
                           frozen analysis bundles; review_2026_08_24/ the reviewer
                           reports, pre-registration and response letter
word/                      Word-build assets (reference.docx, field_registry.csv)
reference_papers/          Bibliography bundle (references.bib + index). Most PDFs are
                           gitignored; Academic_Research_Guidelines/ IS tracked.
results/                   The only runner write target — _run_all/ (reproduced
                           results) and _revision/ (round-1 revision campaign
                           staging, git-tracked); analysis reads the reference
                           panel first
docs/                      Themed Markdown (getting-started/reference/algorithms/
                           development/research/prompt) + generated html/
tests/                     unit / smoke / regression / performance gates
```

## The three things you must never break

1. **The optimizer contract** — `optimize(problem, options) -> OptimizerResult`.
2. **The unified seed schedule** — `runners/seed_policy.get_cec_seed`.
3. **The byte-identity lock** on the vendored dt-gsk core
   (`optimizers/_dt_core.py`, `_dt_subsystems/`, `_dt_rng.py`,
   `_dt_profiles.py`) and the vendored stats core.

The test suite enforces all three. Green-gates before calling a change done:

```powershell
python -m pytest -q
python -m ruff check .
python scripts\validate_profile_lock.py --root .
python scripts\build_docs_html.py
```

## Reproducibility guarantees

Deterministic per cell (pure function of base seed, dim, function, run),
order-independent under parallelism, and pinned to one **floating-point regime**
by a fail-closed sentinel — see
[Floating-Point Regime Verification](docs/reference/fp_regime.md). Reference
evidence is read-only and SHA-256-auditable.
