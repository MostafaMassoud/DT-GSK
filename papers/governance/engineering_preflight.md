# Engineering preflight report (Phase 0, task 6)

Master framework: `papers/PAPER_BUILD_PROMPT.md` — Phase 0 "Run non-destructive
engineering preflight" (task 6). Governance root: `papers/governance/`
(Section 3 preamble, Section 12.4).

| Field | Value |
|---|---|
| date | 2026-07-10 |
| project_root | `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1` |
| git_root | `D:/AI/PhD-Projects` |
| anchor_commit | `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21` (branch `main`; verified with `git rev-parse HEAD` immediately before command 1) |
| working directory (all commands) | `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1` |
| shell | Git Bash (POSIX) on Windows 11; interpreter invoked as `python` per framework Windows convention |
| toolchain observed | Python 3.10.11, pytest 9.0.2, ruff 0.15.5 |
| output capture | each command's combined stdout+stderr captured to a session scratch file; SHA-256 computed with `sha256sum` over the captured text |

## Load-contamination notice (active staging campaign)

The DT-GSK scaffold ablation campaign (`scripts/run_ablation.py`) was RUNNING
on this machine throughout the preflight, writing to `results/_ablation/<cell>/`
(baseline mid-D100; `no_ace/`, `no_psr/` present; log stamps 2026-07-10).
Consequences recorded here:

- All wall times below are contaminated by campaign CPU load and MUST NOT be
  used as performance baselines; they demonstrate command viability only.
- Per Section 0.3 of the framework, `results/` is staging-only, so the
  campaign's churn is NON-BLOCKING. It is recorded as the active-campaign
  dirty-path entry in `project_configuration.md` and as risk register row
  "live staging campaign during preflight". The preflight did not read from,
  wait on, or touch `results/_ablation/`.
- Commands were run strictly sequentially (never in parallel) to avoid adding
  load spikes on top of the campaign.

## Documented deviation: `pip show` instead of `pip install -e ".[dev]"`

The framework's Phase 0 task 6 lists `python -m pip install -e ".[dev]"` as the
first expected command form and states: "If installation changes lock files,
revert or document before continuing." Running an installer mid-campaign could
mutate the interpreter environment used by the live ablation processes
(dependency re-resolution, entry-point rewrite). The preflight therefore
VERIFIED the existing editable install with `python -m pip show gsk-family`
instead of re-installing. This is a documented deviation under the framework's
own revert-or-document permission; the verification confirms the editable
install already points at the project root, which is the state
`pip install -e` would produce. No environment mutation occurred.

---

## Command 1 — verify editable install (deviation, see above)

| Field | Value |
|---|---|
| command | `python -m pip show gsk-family` |
| cwd | `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1` |
| date | 2026-07-10 |
| exit code | 0 |
| wall time | 7 s (campaign-contaminated) |
| output SHA-256 | `6a997a5430fa20e0c0365af449b794d0e4bc0a6516eb26cb291fb3abf2d60fe6` |

Key output lines:

```text
WARNING: Ignoring invalid distribution -rd-gsk (c:\ai\python\python310\lib\site-packages)
Name: gsk-family
Version: 0.1.0
Editable project location: D:\AI\PhD-Projects\00-GSK-Family\02-GSK_Family_Python_v1.1
Requires: matplotlib, numba, numpy, pandas, PyYAML, scipy
```

Finding: the editable install exists and points at the project root — the
exact state `pip install -e` would establish. Note the pip warning about a
stale invalid distribution `-rd-gsk` in site-packages (a broken leftover
metadata directory, likely from an interrupted install of a `*rd-gsk` package).
It does not affect `gsk-family` resolution or any command below; recorded as a
non-blocking environment-hygiene observation.

## Command 2 — test suite

| Field | Value |
|---|---|
| command | `python -m pytest -q` |
| cwd | `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1` |
| date | 2026-07-10 |
| exit code | 0 |
| wall time | 182 s total; pytest self-reported 179.70 s (campaign-contaminated — expected slower than an idle-machine run) |
| output SHA-256 | `341f2b36fcb2e44cf7b621aa4c0fdbb43a94bea7c114b96b9995a125c44c977c` |

Key output lines:

```text
324 passed, 2 warnings in 179.70s (0:02:59)
```

Finding: exactly the expected 324 passed, 0 failed. The 2 warnings are
non-fatal `UserWarning`s from
`src/gsk_family/optimizers/_dt_core.py:2200`
("linkage_block_size_by_dim has no entry for dim=4; falling back to
block_size=1 from nearest configured dim=1") raised by tests exercising an
unconfigured toy dimension; they do not affect benchmark dimensions
(10/30/50/100) and are non-blocking.

## Command 3 — lint

| Field | Value |
|---|---|
| command | `python -m ruff check .` |
| cwd | `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1` |
| date | 2026-07-10 |
| exit code | 0 |
| wall time | < 1 s |
| output SHA-256 | `82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18` |

Key output lines:

```text
All checks passed!
```

## Command 4 — profile lock validation

| Field | Value |
|---|---|
| command | `python scripts/validate_profile_lock.py --root .` |
| cwd | `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1` |
| date | 2026-07-10 |
| exit code | 0 |
| wall time | < 1 s |
| output SHA-256 | `dc812de0954695a70b5fd6ebfec9bfa859deed369f12ee768d07abb364369ffa` |

Key output lines:

```text
Profile-lock validation passed for 3 configs.
```

## Command 5 — docs HTML build

| Field | Value |
|---|---|
| command | `python scripts/build_docs_html.py` |
| cwd | `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1` |
| date | 2026-07-10 |
| exit code | 0 |
| wall time | 1 s |
| output SHA-256 | `349b6c3f0c8936837696f9ca88475c5a2f66c332a33f0750f509acb630b87ee2` |

Key output lines:

```text
HTML docs written to docs\html
Markdown pages: 55
API modules: 51
```

Non-destructiveness check: `git status --porcelain -- docs scripts` was
captured immediately before and immediately after this command; both snapshots
are empty. The generator is idempotent at the anchor commit — it rewrote
`docs/html` byte-identically and dirtied no repository path. No scientific
artifact was touched.

## Command 6 — experiment runner CLI

| Field | Value |
|---|---|
| command | `python run.py --root . --help` |
| cwd | `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1` |
| date | 2026-07-10 |
| exit code | 0 |
| wall time | 4 s (campaign-contaminated interpreter/import startup) |
| output SHA-256 | `da3df33466e1f5c6105c1bd6c80a154b9cceb3f7df46df9982db92b4468af0b9` |

Key output lines (first ~20 lines of help, as evidence):

```text
usage: run.py [-h] [--config CONFIG] [--root ROOT] [--optimizer OPTIMIZER]
              [--suite SUITE] [--dimension DIMENSION] [--function FUNCTIONS]
              [--runs RUNS] [--seed SEED] [--seed-policy SEED_POLICY]
              [--rand-generator RAND_GENERATOR]
              [--max-evaluations MAX_EVALUATIONS] [--output-root OUTPUT_ROOT]
              [--reference-root REFERENCE_ROOT] [--data-root DATA_ROOT]
              [--overwrite] [--parallel] [--serial]
              [--parallel-backend {process,thread}] [--workers WORKERS]
              [--numba-threads NUMBA_THREADS] [--warmup]
              [--warmup-scope {selected,suite}] [--profile] [--console-log]
              [--quiet] [--generation-logs] [--no-generation-logs]
              [--convergence-graphs] [--no-convergence-graphs] [--stats]
              [--benchmark-fp-mode {default,strict}]
              [--benchmark-backend {auto,python}]

Run GSK-family Python experiments.

options:
  -h, --help            show this help message and exit
  --config CONFIG       YAML config file.
  --root ROOT           Base path for relative config roots.
```

## Command 7 — registry listing

| Field | Value |
|---|---|
| command | `gsk-list --optimizers --benchmarks --references benchmarks/cec_reference_results` |
| cwd | `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1` |
| date | 2026-07-10 |
| exit code | 0 |
| wall time | < 1 s |
| output SHA-256 | `7e6e8a68642959d29abb5bb9f6a98dec0f18b0c2ca139abbddd9fa3d083c9020` |

Full output (short enough to record verbatim):

```text
optimizers:
  gsk
  agsk
  apgsk
  atmals-gsk
  egsk
  fdb-agsk
  dt-gsk
benchmarks:
  cec2011
  cec2013
  cec2013lsgo
  cec2017
  cec2020
smoke problems:
  sphere
references:
  cec2011: 441 csv files
  cec2013: 1211 csv files
  cec2013lsgo: 2 csv files
  cec2017: 1666 csv files
  cec2020: 4 csv files
```

Finding: all 7 family optimizers (including `dt-gsk` and the runnable `egsk`)
and all 5 benchmark suites are registered; the read-only reference root
`benchmarks/cec_reference_results/` is readable and populated
(cec2011: 441, cec2013: 1211, cec2013lsgo: 2, cec2017: 1666, cec2020: 4 CSV
files).

---

## Verdict table

| # | Command | Exit | Wall time | Verdict | Notes |
|---|---|---|---|---|---|
| 1 | `python -m pip show gsk-family` | 0 | 7 s | PASS | Documented deviation: verify instead of `pip install -e ".[dev]"` (no mid-campaign environment mutation). Non-blocking pip warning: stale invalid distribution `-rd-gsk` in site-packages. |
| 2 | `python -m pytest -q` | 0 | 182 s (pytest: 179.70 s) | PASS | Exactly 324 passed as expected; 2 non-fatal `UserWarning`s (`_dt_core.py:2200`, dim=4 linkage fallback). Timing campaign-contaminated. |
| 3 | `python -m ruff check .` | 0 | < 1 s | PASS | "All checks passed!" |
| 4 | `python scripts/validate_profile_lock.py --root .` | 0 | < 1 s | PASS | 3 configs validated. |
| 5 | `python scripts/build_docs_html.py` | 0 | 1 s | PASS | Idempotent: docs/scripts git-clean before AND after; 55 Markdown pages, 51 API modules. |
| 6 | `python run.py --root . --help` | 0 | 4 s | PASS | Runner CLI resolves and parses; full option surface present. |
| 7 | `gsk-list --optimizers --benchmarks --references benchmarks/cec_reference_results` | 0 | < 1 s | PASS | 7 optimizers, 5 suites, reference CSV counts recorded. |

## Blocker assessment

Zero nonzero exits. No blockers. Two non-blocking observations for the risk /
assumption registers:

1. Stale invalid distribution `-rd-gsk` in
   `c:\ai\python\python310\lib\site-packages` (pip warning only; does not
   affect `gsk-family` resolution). Environment hygiene item; do not clean
   mid-campaign.
2. `_dt_core.py` dim=4 linkage-block-size fallback `UserWarning` in two
   tests (toy dimension only; benchmark dimensions unaffected).

## Post-preflight repository verification

`git status --porcelain` re-run after command 7 (Phase 0 verification
procedure): the only dirty paths remain the live `results/_ablation/` staging
outputs of the running campaign (modified `baseline` summary CSVs plus
untracked curves/log/summary files under `baseline/`, `no_ace/`, `no_psr/`),
plus the untracked `papers/governance/` directory created to hold Phase 0
governance artifacts. No scientific artifact (`papers/sections/*.tex`,
`papers/references.bib`, `src/`, `benchmarks/`, tracked `results/` evidence)
was modified by the preflight. HEAD unchanged at
`262fc16c91fbe5608a1a0b0c5df3cbcd009edc21`.
