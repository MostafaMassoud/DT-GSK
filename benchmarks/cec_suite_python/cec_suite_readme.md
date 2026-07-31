# CEC Benchmark Suite Documentation

This directory contains the bundled benchmark libraries used by the human-inspired-family project.
No external CEC source tree is required for normal runs.

## Suite Roles

| Suite | Functions | Role in this repository | Paper campaign |
|---|---:|---|---|
| CEC2017 | 30 functions, F2 excluded in aggregates | Primary campaign suite (51 runs) | yes |
| CEC2011 | 22 real-world problems | Real-world campaign suite (25 runs) | yes |
| CEC2013LSGO | 15 large-scale functions | Large-scale campaign suite (25 runs, 3e6 FEs) | yes |
| CEC2013 | 28 functions | External hold-out; library-only in the current campaigns | no |
| CEC2020 | 10 functions | Library-only reserve suite | no |

All five suites are served by
`gsk_family.benchmark_adapter.factory.make_problem` (suite
protocol/metadata in `benchmark_adapter/protocol.py`) and runnable through
`run.py` (`src/gsk_family/cli/run.py`). In this project the scored paper
pipeline is **cec2017 (primary), cec2011, and cec2013** — the frozen evidence
release `rel-2026-07-20-67d9345f9` covers exactly those three. CEC2013LSGO has
complete 375-run campaign banks for all 10 algorithms (`family_cec2013lsgo.yml`
/ `baselines_cec2013lsgo.yml`) but is not yet in the paper's scored panel;
CEC2020 is a fully-validated context suite (`family_cec2020.yml` /
`baselines_cec2020.yml`).

## CEC2017

Role: primary campaign suite.

Paper settings:

- D=10, 30, 50, 100.
- n=51 independent runs.
- budget = 10000 * D evaluations.
- F2 is excluded from aggregate comparisons because it is deprecated for
  numerical instability.

Function groups:

| Range | Type |
|---|---|
| F1-F3 | unimodal |
| F4-F10 | multimodal |
| F11-F20 | hybrid |
| F21-F30 | composition and composition-of-hybrids |

Important implementation notes:

- F14/F20 emulate the C++ Schaffer F7 global-buffer quirk.
- F8 follows the reference behavior where the step modification is overwritten
  by the transform path.
- F9 Levy has its internal minimum at z=1, so `f(shift)` is near but not always
  exactly equal to the bias.
- Shift, rotation, and shuffle data are loaded from bundled `data.pkl` files.

## CEC2013

Role: external hold-out suite (library-only in the current campaigns; not part
of the paper pipeline).

Suite conventions (if run):

- D=10, 30, 50.
- n=51 independent runs.
- budget = 10000 * D evaluations.
- No function exclusions.

Function groups:

| Range | Type |
|---|---|
| F1-F5 | unimodal |
| F6-F20 | multimodal |
| F21-F28 | composition |

CEC2013 supports more dimensions internally, but D=100 is not included in the
paper hold-out because public GSK-family reference baselines are unavailable
for that cell.

## CEC2011

Role: real-world campaign suite — one of the three scored paper suites.

Paper settings:

- 22 fixed-dimension engineering problems.
- n=25 independent runs.
- fixed 150000 evaluations per run.
- No function exclusions.

Each function has its own dimension and bounds.  Use `cec2011_dim(func_id)` and
`cec2011_bounds(func_id)` rather than passing a shared dimension.

## CEC2020

Role: library-only reserve suite.

The CEC2020 port is tested, importable, and runnable through the adapter.  It
ships local Numba kernels for composition weights and shift/rotate fast paths.
It is not part of the paper campaign pipeline.

## CEC2013LSGO

Role: large-scale campaign suite — one of the three scored paper suites
(alongside CEC2017 and CEC2011).

Paper settings:

- 15 native large-scale functions; D=1000 (F13-F14 use D=905).
- n=25 independent runs (`configs/family_cec2013lsgo.yml` /
  `configs/baselines_cec2013lsgo.yml`).
- budget = 3,000,000 evaluations per run.

## Maintenance Notes

- Keep benchmark data files immutable unless regenerating from documented
  reference sources.
- Add parity or frozen-value tests for every behavior change in a benchmark
  transform, dispatcher, or Numba fast path.
- `gsk_family.benchmark_adapter.factory.make_problem` (with the
  suite protocol/metadata in `benchmark_adapter/protocol.py`) is the source of
  truth for suite registration; runs go through `run.py` (`src/gsk_family/cli/run.py`).


## Porting suites from the sibling project — the numba cache trap

When suite files are copied here from `05-Human-Inspired-Family_Python_v0.1`,
**delete every `__pycache__` directory that came with them.** Numba's on-disk
cache records, at compile time, the module path its environment must re-import;
project 05 resolves these suites under a different root, so its cached kernels
fail here at *load* time with
`ModuleNotFoundError: No module named 'cec2017'` (or another bare suite name).

The failure is treacherous because it presents as test failures, not as a cache
problem: on 2026-07-27 it made 7 of 42 golden-value pins "fail" and looked
exactly like the suite update had changed released numbers. A clean recompile
(`find benchmarks/cec_suite_python -name __pycache__ -exec rm -rf {} +`)
restored 42/42 hex-identical. Caches are gitignored, so this can only arrive
through direct file copies — which is precisely how suite updates arrive.
