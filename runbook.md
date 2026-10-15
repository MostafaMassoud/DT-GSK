# Runbook

How to install, test and run DT-GSK (the proposed Dimension-Tiered
Gaining-Sharing Knowledge algorithm) and the six GSK-family algorithms it is
compared with, on five CEC benchmark suites. A formatted copy of this page,
easier to read and with copy buttons on every command, is
[runbook.html](runbook.html): open it in any web browser.

| If you want to | Read |
|---|---|
| Install, test and run the algorithms, and compare their results | [Part 1](#part-1-run-and-test-dt-gsk) (about 30 minutes to a first result, most of it installing and testing) |
| Rebuild the paper, run the revision experiments, or run the release gates | [Part 2](#part-2-maintainer-and-paper-pipeline-reference) |

## Part 1. Run and test DT-GSK

Type every command in a terminal, inside the project folder (the folder that
contains `run.py`). The commands are the same on Windows, Linux and macOS
unless a step says otherwise.

### Step 1. Get the code

You need Git (on Windows, install "Git for Windows" from
[git-scm.com](https://git-scm.com/downloads)).

```shell
git clone https://github.com/MostafaMassoud/DT-GSK.git
cd DT-GSK
```

On Windows, clone into a short folder (for example, type `cd C:\` before the
two commands above), because some file paths in the repository are long. The
download is about 340 MB, and the folder then needs about 1.7 GB of disk space,
mostly for the paper's published results, which Step 6 uses; the Python
environment of Step 2 adds about 0.6 GB.

### Step 2. Install Python and the requirements

Use **Python 3.10 (64-bit)**. All of the paper's results were produced with
Python 3.10.11; on Windows, use the 64-bit Windows installer of Python 3.10.11
from [python.org](https://www.python.org/downloads/release/python-31011/).
Python 3.11 to 3.13 are accepted but were not tested, and Python 3.14 is not
supported. MATLAB and a C compiler are not needed.

Create a virtual environment inside the project folder and activate it.

**Windows** (Command Prompt or PowerShell):

```powershell
py -3.10 -m venv .venv
.venv\Scripts\activate
```

If PowerShell says that running scripts is disabled, run this line and then
the activate line again (it affects only that window):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**Linux or macOS:**

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

The prompt now starts with `(.venv)`. Then, on every system:

```shell
python --version
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

`python --version` should print `Python 3.10.x`. The install downloads a few
hundred MB and can take several minutes; wait for the line that starts with
`Successfully installed`. It installs NumPy, SciPy, pandas, matplotlib, PyYAML
and Numba, the commands `gsk-run`, `gsk-list`, `gsk-stats` and `gsk-validate`,
and the test tools.

> **Every new terminal window:** go to the project folder and activate the
> environment again (`.venv\Scripts\activate` on Windows, `source
> .venv/bin/activate` on Linux or macOS) before running anything below.

### Step 3. Test the code

A quick check (about five to ten minutes the first time, while Numba compiles;
faster later):

```shell
python -m pytest -q tests/smoke
```

The full test suite (allow ten minutes or more the first time, while Numba
compiles its kernels; later runs are faster):

```shell
python -m pytest -q
```

Both should end with a line that says `passed` and no `failed`. Both also
report a few `warnings` (a `UserWarning` about `linkage_block_size_by_dim`),
and the full suite reports `2 skipped`; all of these are expected.

### Step 4. Run your first experiment

DT-GSK on one CEC2017 function, with a deliberately tiny budget:

```shell
python run.py --root . --optimizer dt-gsk --suite cec2017 --function 1 --dimension 10 --runs 1 --max-evaluations 2000 --output-root test_results
```

- The first run can pause for a minute or two while Numba compiles, both before and after it prints its settings. Later runs start in seconds.
- Near the end it prints `PASS  DT-GSK`. A little above that, a "Mean Comparison" table compares the test with the paper's result: its Status column shows `v`, and the Summary line under it ends with `v Worse: 1`. That is expected, because the test uses 2,000 evaluations instead of the full budget of 100,000.
- Keep test runs in their own folder (here `test_results`), never in your real results folder. A run skips every run it already finds in its folder, whatever budget produced it, so a short test left there would be kept as if it were a real result.

### Step 5. Run the algorithms on a benchmark suite

`run.py` is the only script you need. Its settings are command-line options:

| Option | Meaning |
|---|---|
| `--optimizer` | `gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`, `egsk` or `dt-gsk`; several are separated by commas |
| `--suite` | `cec2011`, `cec2013`, `cec2013lsgo`, `cec2017` or `cec2020` |
| `--function` | the functions to run, for example `1:30` (a range) or `1,3,5` |
| `--dimension` | the dimensions, for example `10,30,50,100`; `native` for CEC2011 and CEC2013LSGO, where each problem has its own fixed dimension |
| `--runs` | independent runs per function and dimension; always give it, because the default is 1 |
| `--parallel --workers 4` | runs 4 runs at the same time (without it, only 2); raise it to use more of your CPU cores, see [Use more CPU cores to run faster](#use-more-cpu-cores-to-run-faster) |
| `--numba-threads 1` | one thread per job, as in the paper; keep it |
| `--output-root my_results` | the folder where your results are written |

The evaluation budget of each suite (for example 10000 x D for CEC2017) and the
random seeds are set automatically to the paper's protocol, so do not add
`--max-evaluations` to a real run.

The paper's settings, all seven algorithms in one command per suite:

**CEC2017**: functions 1 to 30 (F2 is left out automatically, as in the
paper), D = 10, 30, 50, 100, 51 runs.

```shell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 4 --numba-threads 1 --output-root my_results
```

**CEC2011**: 22 real-world problems, each at its own fixed dimension, 25 runs.

```shell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2011 --function 1:22 --dimension native --runs 25 --parallel --workers 4 --numba-threads 1 --output-root my_results
```

**CEC2013**: 28 functions, D = 10, 30, 50, 51 runs.

```shell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --parallel --workers 4 --numba-threads 1 --output-root my_results
```

**CEC2020**: 10 functions, D = 5, 10, 15, 20, 30 runs (F6 and F7 are not
defined at D = 5 and are skipped there automatically, as in the paper).

```shell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2020 --function 1:10 --dimension 5,10,15,20 --runs 30 --parallel --workers 4 --numba-threads 1 --output-root my_results
```

**CEC2013LSGO**: 15 functions at D = 1000 (F13 and F14 at D = 905), 25 runs.
Two commands: the first runs the six other algorithms, the second runs DT-GSK
with its own settings file. Always run DT-GSK on this suite with the second
command only; added to the first, it would run with the wrong settings.

```shell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk --suite cec2013lsgo --function 1:15 --dimension native --runs 25 --parallel --workers 2 --numba-threads 1 --output-root my_results
python run.py --root . --config configs/dtgsk_cec2013lsgo.yml --workers 2 --output-root my_results
```

Good to know:

- **One algorithm only:** put a single name after `--optimizer`, for example `--optimizer dt-gsk`.
- **A smaller part:** change the values already in the command, for example `--dimension 10,30,50,100` to `--dimension 10`. Do not add a second `--dimension`, `--function` or `--optimizer` at the end: repeated options are added together, not replaced. For CEC2017, F2 is left out automatically only with exactly `1:30`; for a smaller set leave it out yourself, for example `--function 1,3:10`.
- **If a run stops** (a crash, a reboot, Ctrl-C), type the same command again: finished runs are kept and only the missing ones run. Do not add `--overwrite`, which deletes the algorithm's earlier results for that suite in the folder.

**Closest match to the paper at D = 50 and above.** In the same terminal,
before the `run.py` command, set six thread variables to 1:

**Windows PowerShell:**

```powershell
$env:OMP_NUM_THREADS=1; $env:MKL_NUM_THREADS=1; $env:OPENBLAS_NUM_THREADS=1; $env:VECLIB_MAXIMUM_THREADS=1; $env:NUMEXPR_NUM_THREADS=1; $env:NUMBA_NUM_THREADS=1
```

**Linux or macOS:**

```bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 NUMBA_NUM_THREADS=1
```

In Command Prompt, type `set OMP_NUM_THREADS=1`, then the same `set` line for each of `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS`, `NUMEXPR_NUM_THREADS` and `NUMBA_NUM_THREADS`.

#### Use more CPU cores to run faster

The commands above use `--workers 4`, so four runs go at the same time (without
`--workers`, the program uses only 2). If your computer has more cores, raise
this number and the run finishes sooner. The results stay exactly the same, as
long as `--numba-threads 1` is kept: each run's random seed depends only on the
function, the dimension and the run number, never on how many workers there
are.

**1. Find how many cores your computer has** (this works on every system):

```shell
python -c "import os; print(os.cpu_count())"
```

Other ways: `echo %NUMBER_OF_PROCESSORS%` in Command Prompt,
`$env:NUMBER_OF_PROCESSORS` in PowerShell, `nproc` on Linux, and
`sysctl -n hw.ncpu` on macOS.

**2. Choose the number of workers:**

- Start from your number of cores minus 2, so the computer stays responsive for other work.
- Do not go above the number of runs per function (51 for CEC2017 and CEC2013, 30 for CEC2020, 25 for CEC2011 and CEC2013LSGO). The program finishes all runs of one function before it starts the next, so extra workers would only wait.
- Some numbers use the cores better than their neighbours, because the runs of each function are shared out in rounds: for 51 runs choose 13, 17 or 26 workers; for 30 runs, 10 or 15; for 25 runs, 9 or 13. For example, 14 to 16 workers are no faster than 13 on CEC2017.
- Each worker is a separate program that needs its own memory, so make sure the computer has memory to spare, above all on CEC2013LSGO (about 2 GB per worker). If a run ends with `WARN <ALGORITHM> failed=N`, lower `--workers` and run the same command again; only the missing runs are repeated.

**3. Put your number after `--workers`.** For example, on a computer with 16
cores (16 minus 2 is 14, and for the 51 runs of CEC2017, 13 workers are as fast
as 14):

```shell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 13 --numba-threads 1 --output-root my_results
```

Full runs take a long time. Approximate time for all seven algorithms together,
measured on the authors' 22-core computer (yours may be slower):

| Suite | CPU-hours | With the workers shown above (4; 2 for CEC2013LSGO) | With 13 to 15 workers, as in the paper |
|---|---|---|---|
| CEC2011 | about 65 | about 16 hours | about 5 hours |
| CEC2013 | about 105 | about 1 day | about 7 hours |
| CEC2017 | about 260 | about 3 days | about 1 day |
| CEC2020 | about 260 | about 3 days | about 20 hours |
| CEC2013LSGO | about 960 | about 20 days | about 3 days with 13 workers, if the computer has about 32 GB of memory |

### Step 6. Compare the algorithms

**The comparison from the paper's published results** (nothing to run first):

```shell
gsk-stats --suite cec2017 --out comparison/cec2017
gsk-stats --suite cec2011 --out comparison/cec2011
gsk-stats --suite cec2013 --out comparison/cec2013
gsk-stats --suite cec2020 --out comparison/cec2020
gsk-stats --suite cec2013lsgo --out comparison/cec2013lsgo
```

Each command writes, into the folder after `--out`, a text report
(`<suite>_statistical_report.txt`) with the Friedman mean ranks of the seven
algorithms and, for DT-GSK against each other algorithm, the Wilcoxon
signed-rank test and the win/tie/loss counts; a CSV of the ranks; two LaTeX
tables; and figures. The p-values in the text report are not corrected for
multiple comparisons; the Holm-corrected ones are in
`<suite>_wilcoxon_summary.tex`. The CEC2011 results are labelled `D0`, meaning
each problem at its own dimension.

`gsk-stats` is a convenience tool, so its numbers are close to the paper's but
not always identical: it uses a simpler rule for tied pairs in the Wilcoxon
test, and on CEC2013LSGO it ranks the 13 functions at D = 1000, while the paper
pools all 15. So a few Wilcoxon decisions differ (for example CEC2013 at
D = 50, where `gsk-stats` shows three DT-GSK wins that the paper reports as
ties). The exact statistics reported in the paper are in the files
`friedman_ranks_*.csv` and `wilcoxon_holm_*.csv`, in the suite's subfolder (for
example `cec2017/`) of these folders under `papers/analysis/`:
`rel-2026-07-20-67d9345f9/` (CEC2011, CEC2013, CEC2017),
`cec2020-rel-2026-07-29-5867abe1e/` and `lsgo-rel-2026-07-28-ff1a046ef/`.

**Including your own runs.** `gsk-stats` reads the published results first, so
your runs are not used by the commands above. Collect them into a panel folder
first; your files replace the published ones for the same algorithm and
dimension, and everything you did not run keeps its published result:

```shell
python scripts/build_stats_panel.py --suite cec2017 --results my_results --out my_panel
gsk-stats --suite cec2017 --reference-root my_panel --out comparison_mine/cec2017
```

For another suite, replace `cec2017` everywhere in both lines. Wait until each
dimension you ran has finished for all functions (the script warns about a
partial file, and about a run with fewer runs or a smaller budget than the
published one), and compare `comparison_mine` with `comparison`, not with the
tables in the paper.

### Step 7. Find your results

Each algorithm writes to `my_results/<algorithm>/<suite>/summary/`:

| File | Contents |
|---|---|
| `per_run.csv` | one row per run: function, dimension, run, seed, best fitness, error, evaluations used and runtime |
| `<algorithm>_<suite>_D<d>.csv` | the Best, Median, Mean, Worst and SD of each function's error at dimension d (CEC2011 and CEC2013LSGO: of the objective value, so the `error` column of `per_run.csv` is `NaN` there; CEC2011 also writes `<algorithm>_cec2011.csv`, every problem you ran in one table) |
| `run_config.json`, `environment.json` | the exact settings and software versions of the run |

Convergence curves are in `my_results/<algorithm>/<suite>/curves/`. The paper's
own result for every run of every algorithm is in
`benchmarks/cec_reference_results/<suite>/<algorithm>/per_run.csv`.

### Troubleshooting

| Problem | What to do |
|---|---|
| `'git' is not recognized` | Install Git (Step 1) and open a new terminal. |
| `Filename too long` while cloning (Windows) | Clone into a short folder such as `C:\DT-GSK`, or run `git config --global core.longpaths true` first. |
| `'python' is not recognized`, or the wrong version | On Windows use `py -3.10` as in Step 2; `py --list` shows the installed versions. |
| `python3.10: command not found` (Linux or macOS) | Install Python 3.10 (Ubuntu: `sudo add-apt-repository ppa:deadsnakes/ppa`, then `sudo apt install python3.10 python3.10-venv`; macOS: the python.org installer; anywhere: pyenv), or use your system `python3` if `python3 --version` shows 3.11 to 3.13 (accepted, not tested). Then repeat Step 2. |
| `ensurepip is not available` when creating the environment (Debian or Ubuntu) | Install the venv module for that Python, for example `sudo apt install python3.10-venv` (or `python3.12-venv`), delete the `.venv` folder, and repeat Step 2. |
| `running scripts is disabled on this system` (PowerShell) | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again; or use Command Prompt. |
| `No module named 'gsk_family'`, or `gsk-stats` is not recognized | The environment is not active in this window: activate it (Step 2). If it still fails, run `python -m pip install -e ".[dev]"` again. |
| A run pauses for a minute or more after it starts, or after it prints its settings | Numba is compiling its kernels once; wait. |
| The "Mean Comparison" table shows `v` and `Worse` after a short test | Expected when `--max-evaluations` cuts the budget. |
| A run ends with `WARN <ALGORITHM> failed=N` instead of `PASS`, or stops with an error that mentions `skipped_runs.csv` (often a memory error, for example on CEC2013LSGO) | Lower `--workers` and run the same command again; only the missing runs are repeated. |
| `gsk-stats` says `reference directory not found` | If the message lists the suites it found, fix the spelling after `--suite`. Otherwise the published results are missing: use a full clone (Step 1), and run the command from the project folder. |

---

## Part 2. Maintainer and paper-pipeline reference

The rest of this runbook is the terse copy-paste reference behind the paper:
the revision experiments, the complete data-to-PDF pipeline, the release gates
and the freeze cycle, plus advanced run variants. Everything in Part 1 still
applies. Run everything from the repository root (the folder that contains
`run.py`, `pyproject.toml`, and `src/gsk_family/`); every command passes
`--root .`, so it is portable regardless of where the checkout lives on disk.

For the narrative version of these commands -- with rationale, defaults, the
console-output contract, and the parallel-backend guide -- see
[README.md](README.md). The two documents are kept consistent; this runbook is
the terse copy-paste companion.

**Optimizers (7 runnable):** `gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`,
`dt-gsk` (the proposed Dimension-Tiered Gaining-Sharing Knowledge), and `egsk`. `egsk` is
a runnable optimizer ID, but its statistical-panel cells still come from the
committed reference data under `benchmarks/cec_reference_results/`.
**Suites (6):** `cec2017`, `cec2011`, `cec2020`, `cec2013`, `cec2013lsgo`,
`sphere`.

## Discover Before You Run

```powershell
# Full CLI help (every flag, with defaults)
python run.py --root . --help

# What optimizers, benchmarks, and reference evidence are available
gsk-list --optimizers --benchmarks --references benchmarks/cec_reference_results
```

`gsk-list` is installed by the editable install (`pip install -e .`). From a
plain `pip` checkout, run `$env:PYTHONPATH = "src"` in the shell first and
then call `python -m gsk_family.cli.list` instead (see [Setup](#setup)).

## Setup

Editable install with the dev extra (enables the `gsk-*` console scripts plus
test, lint, and docs tooling), then run the test suite:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
```

Plain pip instead (libraries only, no editable package, so no `gsk-*`
scripts). `python run.py` and `scripts\run_gsk_family.py` work as they are,
because each adds `src/` to the import path itself. The
`python -m gsk_family.cli.*` module forms do not, and neither do most other
scripts that import `gsk_family` (for example the `scripts\run_all_*.py` and
`scripts\run_ablation.py` launchers, `papers\scripts\generate_ablation_matrix.py`
and `generate_ablation_exhibits.py`): they stop with
`ModuleNotFoundError: No module named 'gsk_family'` unless `src` is on
`PYTHONPATH`, so set it once per shell, from the repository root:

```powershell
python -m pip install -r requirements.txt        # runtime only
python -m pip install -r requirements-dev.txt    # runtime + dev tooling
$env:PYTHONPATH = "src"                          # for python -m gsk_family.cli.* and the scripts\ launchers
```

Requires CPython `>=3.10,<3.14`. The runtime stack is NumPy, SciPy, pandas,
matplotlib, PyYAML, and Numba (version ranges pinned in `pyproject.toml`).

## Journal Revision Experiments (one command)

The five reviewer-requested experiments from the Algorithms revision: E1-E4
from the round-1 major revision (D-0047, CR-0023), plus E5, added in round 2 and
pre-registered as **Amendment A4** before it executed. The other six round-1
reviewer points needed no runs and are already applied.

**Rehearse first — 20 seconds, and it verifies itself:**

```powershell
python scripts\run_revision_experiments.py --smoke
```

Runs every kind of leg through the identical code path at tiny scope (2
functions, 2 runs, one dimension, 3,000 evaluations), then checks that each leg
actually wrote the rows it promised and prints `SMOKE PASSED` or `SMOKE FAILED`.
Output goes to `results/_revision_smoke/`, which is gitignored and can never
reach the campaign tree. Do not start the real run until this is green.

**Then the real thing. This is the whole command:**

```powershell
python scripts\run_revision_experiments.py
```

Start it and leave it. It is **resumable**: after any interruption — Ctrl-C, a
reboot, a crashed leg — re-run the identical line and it continues from the
first incomplete cell instead of repeating finished work. Every leg is written
`overwrite: false`.

| Leg | Reviewer point | What it runs | Runs |
|---|---|---|---|
| E1 | R2.3 | Coordinate-basis final polish (the missing third arm) | 2,958 |
| E2 | R1.3 / R2.2 | DT-GSK at the comparators' `NP = 100` | 5,916 |
| E3 | R2.1 | Uniform vs tiered: the D=10 and D=100 parameter sets applied at every dimension | 11,832 |
| E4 | R2.7 | Parameter sensitivity, 27 one-factor cells | 11,745 |
| E5 | R2.7 | Dimension-boundary sensitivity, 4 executed cells (round 2, Amendment A4) | 1,740 |
| | | **Total** | **34,191** |

E5 registers **five** boundary cells but runs four. The fifth — boundary
20 -> 31, i.e. the low-tier parameter set applied at D = 30 — is identical by
construction to E3's uniform-low arm at D = 30 (51 runs per function), so it is
reused from the promoted round-1 release `rev-rel-2026-08-26-dd42d37eb` rather
than re-executed. E5's four executed cells use 15 runs per function, as E4 does.

Roughly 25–33 hours at 15 workers for E1–E4; E5's four cells add about five
percent to that. Progress is printed and appended to
`results/_revision/driver.log`, so a detached run can be followed with:

```powershell
Get-Content -Wait results\_revision\driver.log
```

Useful variants:

```powershell
python scripts\run_revision_experiments.py --smoke        # 20 s rehearsal, self-verifying
python scripts\run_revision_experiments.py --status       # progress table, runs nothing
python scripts\run_revision_experiments.py --dry-run      # the plan, runs nothing
python scripts\run_revision_experiments.py --only E1,E2   # a subset
python scripts\run_revision_experiments.py --only E5      # the round-2 leg alone
python scripts\run_revision_experiments.py --workers 8    # fewer workers
```

`--smoke` composes with the others, so `--smoke --dry-run` shows the rehearsal
plan without running it.

The smoke run prints per-function comparisons against the reference bank that
will look alarming — "Worse: 2", errors around 1e+09. That is expected and not a
failure: 3,000 evaluations against the reference's 100,000–1,000,000. Judge the
smoke by the `SMOKE PASSED` line, not by those tables.

Notes that matter:

- Output is staged under `results/_revision/`, **never** `benchmarks/`.
  Promotion into an evidence release is a separate, deliberate step.
- The driver pins `OMP`/`MKL`/`OPENBLAS`/`NUMBA` thread counts to 1 per worker.
  D >= 50 byte-stability depends on that; do not run the legs by hand without it.
- E3's override dictionaries are generated programmatically from
  `_dt_profiles.pub_overrides()`. Eighty-eight config keys differ between the
  D=10 and D=100 tiers — never transcribe them.
- **E1 is driven by `scripts/run_e1_basis_contrast.py`, not by a YAML config.**
  It needs the research hook `research_oracle_basis`, which the public adapter
  deliberately does not forward and which
  `tests/regression/test_dormant_mechanisms_unreachable.py` exists to keep
  unreachable from every config, profile, CLI and adapter path — that test also
  pins the adapter's source text, and `dt_gsk.py` is hash-gated by
  `validate_provenance_claims.py`. Expressing E1 as a config would break a
  regression test and a hash gate. The tripwire scans `src/gsk_family` only and
  its docstring records that reaching the hooks "requires a new evidence
  release", which is what E1 produces. Nothing under `src/` is modified.
- The pre-registration addendum is **signed**:
  `papers/review_2026_08_24/revision_experiments_preregistration.md`, dated
  2026-08-25, before any result from these experiments existed. It records that
  §1.4 of `papers/build_prompt_phases/phase_05/ablation_preregistration.md` —
  which binds that a mechanism be verified ON in the baseline at a dimension
  before a disable delta is claimed there — does **not** govern E1 or E3, and
  registers replacement rules rather than reinterpreting it: E1 holds enablement
  constant and substitutes the basis, E3 is a configuration transplant with its
  own binding rule. E3 licenses only "the tiered configuration does / does not
  outperform a tier-constant one at dimension d"; no E3 cell may be attributed to
  a single subsystem. E4 is registered **exploratory** — descriptive only, no
  hypothesis tests and no corrected p-values. The addendum is append-only: two
  amendments dated 2026-08-26 record an E4 perturbation-level deviation at D=100
  and a corrected E2 scope statement.

## After The Campaign (promotion, analysis, exhibits)

The campaign of record is already through this chain. Run it in this order:

```powershell
python papers/scripts/promote_revision_experiments.py --dry-run
python papers/scripts/promote_revision_experiments.py
python papers/scripts/analyze_revision_experiments.py
python papers/scripts/generate_revision_exhibits.py
```

- **Promotion** writes the flat, manifest-bound tree
  `benchmarks/cec_reference_results/_revision/` — release
  **`rev-rel-2026-08-26-dd42d37eb`**, 31 arms, 252 files, read-only — not the
  retired `_releases/<release-id>/` layout. `curves/` and per-session console
  logs are excluded by manifest, never silently dropped. Re-running against an
  existing tree verifies instead of re-copying, and adds only missing arms.
- **Analysis** is strict-source: it reads the promoted tree plus the two frozen
  releases it pairs with, never `results/`. It mints the self-manifested bundle
  `papers/analysis/rev-rel-2026-08-26-dd42d37eb/` and refuses to emit unless
  seed pairing verifies and its pinned known-answer battery reproduces.
- **Exhibits** render SA05--SA08 — Supplementary Section S9, Tables A43--A46 —
  and their Word twins from that bundle, from the same plain data in both
  formats.

The release is **additive and non-superseding**: the primary release
`rel-2026-07-20-67d9345f9` is untouched and `check_frozen_analysis` still reads
115/115 byte-identical.

## Full Paper Pipeline (in order)

The complete data-to-PDF sequence. `--workers 15` is shown (matches
`configs/publish/`); drop to the safe baseline `2` if memory-constrained (see
[Common Flags](#common-flags)). **Dependency order:** §1 data -> §3 stats ->
§5/§6 figures & tables -> §7 build; and §2 ablation -> §4 aggregate -> §6 table.
The granular sections below this one give variants (tight-on-memory,
reference-seed, per-optimizer, targeted). The numbered comments in the block
below (1 to 8d) are pipeline stages, not Part 1's Steps; the "see runbook.md
step 7" in `papers/scripts/build_change_marked_pdf.py` means stage 7 here
(Build the PDFs).

```powershell
# --- 1. Generate run data: the three benchmark campaigns ---
# Thread pinning is NOT optional at D >= 50. run.py pins nothing by itself
# (scripts/run_campaign.py sets the six variables below to 1, and
# scripts/run_revision_experiments.py sets five of them for its workers),
# and thread count sets floating-point reduction order in DT-GSK's Numba
# kernels, which --numba-threads 1 pins per worker, and in NumPy's BLAS/LAPACK
# calls (the eigendecomposition behind the final polish among them), which only
# the BLAS/OpenMP variables reach, and only when set before Python starts. An
# unpinned re-run is not comparable with a pinned one. It is NOT a promise that
# a pinned re-run reproduces archived bytes: D-0051 demonstrated the opposite
# across builds -- a pinned re-execution reproduced the transplant arm on all
# 26 divergent cells and the archive on none. Pin it so a run is comparable
# with itself.
# --overwrite rebuilds each optimizer's per_run.csv for the suite from scratch.
# After an interruption, re-run the same line WITHOUT it to resume; but an
# optimizer the interrupted run never reached still holds any earlier rows,
# which a resume keeps, so re-run that optimizer with --overwrite instead.
$env:OMP_NUM_THREADS=1; $env:MKL_NUM_THREADS=1; $env:OPENBLAS_NUM_THREADS=1
$env:VECLIB_MAXIMUM_THREADS=1; $env:NUMEXPR_NUM_THREADS=1; $env:NUMBA_NUM_THREADS=1
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 15 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2011 --function 1:22 --dimension native --runs 25 --parallel --workers 15 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --parallel --workers 15 --numba-threads 1 --convergence-graphs --overwrite

# --- 1b. The two additional suites (five-suite scope, CR-0019). CEC2020 runs its
#     locked family config and resumes. CEC2013LSGO takes two lines: DT-GSK reproduces
#     only under configs/dtgsk_cec2013lsgo.yml, and scripts/run_all_cec2013lsgo.py is a
#     one-cell GSK smoke, not a campaign ---
python scripts/run_all_cec2020.py --workers 15
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk --suite cec2013lsgo --function 1:15 --dimension native --runs 25 --parallel --workers 4 --numba-threads 1
python run.py --root . --config configs/dtgsk_cec2013lsgo.yml --workers 4

# --- 2. DT-GSK scaffold ablation: CEC2017, all dimensions ---
python scripts/run_ablation.py --dimension 10,30,50,100 --runs 51 --workers 15

# --- 3. Statistical panels (per suite). These report the COMMITTED panel in
#     benchmarks/cec_reference_results/, not step 1's output: results/_run_all/
#     is read only for a proposed-optimizer cell the panel lacks, and the panel
#     carries every cell. To analyse step 1's runs, see "Analysing your own
#     runs" under Statistical Analysis below ---
python -m gsk_family.cli.stats --suite CEC2017 --dims 10,30,50,100
python -m gsk_family.cli.stats --suite CEC2011
python -m gsk_family.cli.stats --suite CEC2013 --dims 10,30,50

# --- 3b. Registered CEC2020 + CEC2013LSGO batteries (phase6b; reads the two
#     promoted releases, reproduces Amendments 1-3's pinned values or fails).
#     One run per suite: the driver refuses --suite both, because the two
#     suites belong to different releases. --out-root keeps each re-run out of
#     the committed bundles under papers/analysis/, which it would otherwise
#     rewrite with this checkout's git head and working directory ---
python papers/scripts/phase6b_run_analysis_newsuites.py --suite cec2020 --out-root "$env:TEMP\phase6b_cec2020"
python papers/scripts/phase6b_run_analysis_newsuites.py --suite cec2013lsgo --out-root "$env:TEMP\phase6b_lsgo"

# --- 4. Aggregate the ablation (per dimension) ---
python papers/scripts/generate_ablation_matrix.py --dimension 10
python papers/scripts/generate_ablation_matrix.py --dimension 30
python papers/scripts/generate_ablation_matrix.py --dimension 50
python papers/scripts/generate_ablation_matrix.py --dimension 100

# --- 5. Figures ---
python papers/scripts/generate_full_convergence.py
python papers/scripts/generate_cec2011_convergence.py
python papers/scripts/generate_cec2013_convergence.py --dimension 30
python papers/scripts/generate_nemenyi_cd.py
python papers/scripts/generate_rank_charts.py
python papers/scripts/generate_trace_figures.py
python papers/scripts/generate_nlpsr_trajectory.py
python papers/scripts/generate_adaptive_params_panel.py

# --- 6. Tables (read frozen, checked-in evidence: benchmarks/cec_reference_results/_paper_tables/,
#     papers/analysis/rel-2026-07-20-67d9345f9/ and papers/analysis/rev-rel-2026-08-26-dd42d37eb/
#     — not results/ staging) ---
python papers/scripts/generate_latex_tables.py
python papers/scripts/generate_t16_bca.py
python papers/scripts/generate_revision_exhibits.py   # S9 exhibits SA05-SA08 = Tables A43-A46

# --- 7. Build the PDFs. Since pass-53 the epoch is pinned INSIDE the builders
#     (build_pdf.py:67, build_supplementary.py:42; pass-54's build_cover_letter.py
#     pins it too, at :43),
#     so do NOT export it here. Exporting it is now the only way to create the
#     hazard step 7b warns about, because the DOCX writer prefers an inherited
#     SOURCE_DATE_EPOCH over its own different default ---
python papers/scripts/build_pdf.py
python papers/scripts/build_supplementary.py
python papers/scripts/build_cover_letter.py   # cover_letter.pdf is files[10]
python papers/scripts/generate_review_pack.py

# --- 7b. Word twins, IN A FRESH SHELL. The DOCX epoch is a different number and
#     _word_ooxml.source_date_epoch() PREFERS an inherited SOURCE_DATE_EPOCH over
#     its 1783641600 default, so a shell still carrying the PDF's 1783468800
#     silently produces a non-reproducible DOCX that still passes every gate.
#     build_docx.py consumes the checked-in table sources under
#     papers/tables/word_sources/*.json; it does not regenerate them ---
Remove-Item Env:FORCE_SOURCE_DATE -ErrorAction SilentlyContinue
$env:SOURCE_DATE_EPOCH = "1783641600"
python papers/scripts/build_docx.py
python papers/scripts/build_docx.py --supplementary
# Both DOCX files are freeze-tracked. Build every artifact TWICE and byte-compare
# before trusting check_manifest.

# --- 8. Quality gates (code side) ---
python -m pytest -q
python -m ruff check .
python scripts\validate_profile_lock.py --root .
python scripts\build_docs_html.py

# --- 8b. Manuscript gate battery (the pass-41 battery; commit-field resolvability gated since pass-56). Every one must exit 0;
#     the three counted ones read 15/15, 115/115 and 755 rows / 0 FAIL ---
python papers/scripts/check_manifest.py
python papers/scripts/check_reproducibility_manifest.py  # ungated until pass-54;
#     the reproducibility manifest went stale INSIDE its own pass three times,
#     always by being refreshed before the artifacts were rebuilt. Run it AFTER
#     every rebuild, not with the mint.
python papers/scripts/check_frozen_analysis.py
python papers/scripts/validate_cross_format_parity.py
python papers/scripts/validate_document_consistency.py
python papers/scripts/validate_build_hygiene.py
python papers/scripts/validate_artifact_labels.py
python papers/scripts/validate_citation_cff.py
python papers/scripts/validate_citation_controls.py
python papers/scripts/validate_provenance_claims.py
python papers/scripts/validate_evidence_bindings.py
python papers/scripts/validate_docx.py papers/DT-GSK.docx
python papers/scripts/validate_docx.py papers/supplementary.docx
python scripts/check_package_contents.py  # builds sdist+wheel from `git archive HEAD`
#     and fails if either carries the evidence bank, papers/, or withheld
#     material. Added 2026-08-29 after a setuptools upgrade started honoring the
#     old recursive package-data glob and produced a 1.2 GB wheel.

# --- 8c. Freeze re-mint, after any change to one of the 15 files tracked in
#     papers/governance/main_manuscript_freeze_manifest.json. Re-mint it
#     byte-surgically -- CRLF, 2-space indent, both `sha256` and `bytes`
#     updated per file -- and verify the json.dumps(indent=2, ensure_ascii=False)
#     round-trip AND the trailing-byte convention against the ORIGINAL bytes
#     before rewriting; read_text()/write_text() normalize the line endings and
#     break every hash. Procedure of record:
#     docs/development/FINAL_PUBLICATION_PLAN.md (take the trailing bytes from
#     the file, not from that document -- this manifest does end with a
#     trailing CRLF) ---

# --- 8d. check_manifest hashes the WORKING TREE, not the committed blob, so a
#     re-saved binary can still pass 15/15. Close that blind spot by hand: each
#     size below must equal the `bytes` recorded for that file in the manifest ---
git cat-file -s HEAD:papers/DT-GSK.pdf
git cat-file -s HEAD:papers/DT-GSK.docx
git cat-file -s HEAD:papers/supplementary.pdf
git cat-file -s HEAD:papers/supplementary.docx
git cat-file -s HEAD:papers/cover_letter.pdf
```

## Smoke Test

A few seconds: one optimizer, one function, a tiny evaluation budget. Use this
to confirm the toolchain before launching a full sweep:

```powershell
python run.py --root . --optimizer gsk --suite sphere --function 1 --dimension 4 --runs 1 --max-evaluations 80 --overwrite
```

Or run a packaged smoke campaign from YAML:

```powershell
python run.py --root . --config configs/smoke.yml --output-root results/_smoke
```

The config runs one reduced-budget GSK CEC2017 cell (F1, `D = 10`, 1,000
evaluations) with `overwrite: true` and names `results/_run_all/` as its output
root. Keep `--output-root results/_smoke`: in the shared tree the run would
rebuild `results/_run_all/gsk/cec2017/summary/per_run.csv` from that one run,
and a later campaign run without `--overwrite` (such as
`scripts\run_all_cec2017.py`) would keep its reduced-budget row as run 1 of F1
at `D = 10`, because resume matches function, dimension, run and seed only.

## CEC2017 All Optimizers

Use a visible worker count in campaign commands. The safe baseline is
`--workers 2`; increase the number only when you know the machine has spare CPU
and memory and you are not running other heavy work. `--convergence-graphs`
opts in to rendered PNG plots; omit it when you only need the convergence CSV
files.

```powershell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --numba-threads 1 --convergence-graphs --overwrite
```

To resume after a crash or reboot, re-run the same line **without**
`--overwrite`: runs already recorded are skipped. With it, the runner rebuilds
each named optimizer's `per_run.csv` for the suite from this invocation alone,
discarding every earlier row, not only the cells the command names (see
[Common Flags](#common-flags)); this line names the whole suite, so nothing
outside it is lost. The optimizers run one after another, so an optimizer the
interrupted run never reached still holds whatever the tree held before, and a
resume would keep it; re-run that optimizer with `--overwrite` instead.
`--numba-threads 1` keeps the `D = 50` and `D = 100` cells comparable (see
[Full Paper Pipeline](#full-paper-pipeline-in-order) step 1).

## Other Full Sweeps

Benchmark backend defaults to `auto`, which uses the Python/Numba evaluator.
Use `--parallel --workers 2` as the safe baseline; raise `2` deliberately when
the machine has enough headroom. Each line pins one Numba thread per worker,
as the locked `configs/family_*.yml` campaigns do (`numba_threads: 1`), and
recomputes its suite from scratch (resuming is covered under
[CEC2017 All Optimizers](#cec2017-all-optimizers)). The CEC2020 and
CEC2013-LSGO lines write to `results/_rerun/`, because the tracked campaign
staging for those two suites already lives in `results/_run_all/` and
`--overwrite` would rebuild it.

```powershell
# CEC2020 - 10 functions, dims 5/10/15/20
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2020 --function 1:10 --dimension 5,10,15,20 --runs 30 --parallel --workers 2 --numba-threads 1 --convergence-graphs --output-root results/_rerun --overwrite

# CEC2013 - 28 functions, dims 10/30/50
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --parallel --workers 2 --numba-threads 1 --convergence-graphs --overwrite

# CEC2011 - native per-problem dims
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2011 --function 1:22 --dimension native --runs 25 --parallel --workers 2 --numba-threads 1 --convergence-graphs --overwrite

# CEC2013-LSGO - D=1000, very expensive; shown for one optimizer
python run.py --root . --optimizer gsk --suite cec2013lsgo --function 1:15 --dimension 1000 --runs 25 --parallel --workers 2 --numba-threads 1 --convergence-graphs --output-root results/_rerun --overwrite
```

## CEC2013 Family Panel

CEC2013 is the second GSK-family comparison suite: 28 functions, dims 10/30/50,
51 runs (CEC2013 competition standard). Run the full 7-optimizer panel (note:
`egsk` runs via the scipy-SLSQP port, and the statistical panel reads `egsk`
from the committed `scipy`-SLSQP port CSVs, the comparator of record):

```powershell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --parallel --workers 2 --numba-threads 1 --convergence-graphs --overwrite
```

Tight on memory -- one optimizer at a time (repeat per optimizer id):

```powershell
python run.py --root . --optimizer dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --parallel --workers 2 --numba-threads 1 --convergence-graphs --overwrite
```

The runs above land under `results/_run_all/<optimizer>/cec2013/`. Every
committed panel CSV is unified-seed (each `run_config.json` records
`seed_policy: unified`), so a `--seed-policy reference` run does not line up
with them. That policy switches a comparator to its original implementation's
own seed formula, for parity checks against that implementation, and leaves
`dt-gsk` on the unified seed under every policy (see
`docs/reference/seed_policy.md`). Give such a run its own output root, so its
rows never mix with or replace the runs in `results/_run_all/`:

```powershell
python run.py --root . --optimizer agsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --seed-policy reference --parallel --workers 2 --numba-threads 1 --output-root results/_reference_seed --overwrite
```

The CEC2013 family report (Friedman ranks, Nemenyi CD, pairwise Wilcoxon/Holm,
effect sizes) reads every optimizer, `dt-gsk` included, from
`benchmarks/cec_reference_results/cec2013/`, which carries all seven, so it
reports the committed panel rather than the runs above (see
[Statistical Analysis](#statistical-analysis) to analyse your own runs):

```powershell
python -m gsk_family.cli.stats --suite CEC2013 --dims 10,30,50
```

CEC2013 convergence-curve grids (28 functions at a chosen dimension; the script
finds the panel whether it lands in `benchmarks/cec_reference_results/cec2013/`
or a reproduced-run tree):

```powershell
python papers/scripts/generate_cec2013_convergence.py --dimension 30
```

The CEC2013 head-to-head (T11--T13) and Wilcoxon summary (T14) LaTeX tables are
emitted by the shared table generator, which reads the promoted evidence at
`benchmarks/cec_reference_results/_paper_tables/` and never touches `results/`
staging:

```powershell
python papers/scripts/generate_latex_tables.py
```

## Config Launchers

Only `run_all_cec2020.py` runs a paper campaign (`configs/family_cec2020.yml`).
`run_all_cec2017.py` and `run_all_cec2011.py` run `configs/all_cec2017.yml` and
`configs/all_cec2011.yml` (five optimizers without `egsk` and `dt-gsk`, 25 runs,
unpinned Numba threads). `run_all_cec2013.py` and `run_all_cec2013lsgo.py` are
one-cell GSK smokes (F1, 1 run, 1,000 evaluations, `--overwrite`, written under
`results/`). For the paper's settings use the commands in
[Part 1, Step 5](#step-5-run-the-algorithms-on-a-benchmark-suite). The launchers
live in `scripts/` (see [scripts/README.md](scripts/README.md)):

```powershell
python scripts\run_all_cec2017.py
python scripts\run_all_cec2011.py
python scripts\run_all_cec2020.py
python scripts\run_all_cec2013.py
python scripts\run_all_cec2013lsgo.py
```

You can also drive campaigns directly from the YAML files in `configs/`:

```powershell
python run.py --root . --config configs/all_cec2017.yml   # five-optimizer, 25-run template, not the paper's settings
python run.py --root . --config configs/all_optimizers_smoke.yml
python run.py --root . --config configs/all_optimizers_cec2017_reduced.yml
```

## Common Flags

| Flag | Effect |
|---|---|
| `--root .` | Project root; keeps the command portable across checkout locations. |
| `--optimizer a,b,c` | Comma-separated optimizer IDs to run. |
| `--suite NAME` | One of the six suites. |
| `--function 1:30` or `--function 5` | Function range (`lo:hi`) or single ID. |
| `--dimension 10,30,50,100` / `native` | Comma-separated dims; `native` uses each problem's intrinsic dimension (CEC2011). |
| `--runs 51` | Independent runs per cell (CEC2017 convention is 51; CEC2011 commonly 25). |
| `--max-evaluations N` | Override the evaluation budget (used by smoke cells). |
| `--parallel` / `--serial` | Process pool vs single process; parallel is the default unless `--serial`. |
| `--workers N` | Bound concurrent processes (and peak memory). Safe baseline `2`. |
| `--convergence-graphs` / `--no-convergence-graphs` | Render PNG curves, or write curve CSVs only. |
| `--numba-threads 1` | One Numba thread per worker process. `run.py` pins none by itself; keep it for DT-GSK at `D >= 50` (see [Full Paper Pipeline](#full-paper-pipeline-in-order) step 1). |
| `--overwrite` | Rebuild each named optimizer's `per_run.csv` for the suite from this invocation alone, discarding every earlier row, not only the named cells. Omit it to resume: recorded runs are skipped, matched on function, dimension, run and seed only (not budget or code version). |
| `--seed-policy reference` | Use the reference seed labels instead of the default unified schedule. |
| `--stats` | Stream per-dimension Wilcoxon + Friedman analysis live (opt-in; skips vanilla `gsk`; `cec2011` reports via its per-suite rollup). |

## Tight On Memory

Run one optimizer at a time with the same safe worker baseline. After a crash,
re-run the same line **without** `--overwrite` to resume: runs already recorded
are skipped.

```powershell
python run.py --root . --optimizer gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer agsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer apgsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer fdb-agsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer atmals-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer egsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --numba-threads 1 --convergence-graphs --overwrite
```

Need more speed? Increase the worker count deliberately:

```powershell
python run.py --root . --optimizer gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 4 --numba-threads 1 --convergence-graphs --overwrite
```

## Targeted Runs

A targeted run gets its own output root. With `--overwrite` in the shared
`results/_run_all/` tree it would rebuild that optimizer's whole `per_run.csv`
from this one cell, discarding every other cell already recorded there.

```powershell
# One optimizer, one function, one dimension
python run.py --root . --optimizer agsk --suite cec2017 --function 5 --dimension 30 --runs 51 --parallel --workers 2 --convergence-graphs --output-root results/_targeted --overwrite

# Same run with reference seed policy (a separate root again, so the two seed policies never mix)
python run.py --root . --optimizer agsk --suite cec2017 --function 5 --dimension 30 --runs 51 --seed-policy reference --parallel --workers 2 --convergence-graphs --output-root results/_targeted_reference_seed --overwrite
```

## Results And Validation

Stats, summaries, seed schedules, metadata, and convergence curves are written
under:

```text
results/_run_all/<optimizer>/<suite>/
```

Validate imported reference evidence:

```powershell
python -m gsk_family.cli.validate --references benchmarks/cec_reference_results
```

Compare generated results with imported references:

```powershell
python -m gsk_family.cli.validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

## Statistical Analysis

Paper-grade GSK-family comparison (Friedman ranks, Nemenyi CD, pairwise
Wilcoxon/Holm, effect sizes); outputs land under
`results/_run_all/_analysis/<suite>/`:

```powershell
python -m gsk_family.cli.stats --suite CEC2017 --dims 10,30,50,100
```

**Single source of truth.** All paper statistics -- including the proposed
`dt-gsk` -- are read from the committed reference panel
`benchmarks/cec_reference_results/<suite>/<optimizer>/` (flat layout:
`<optimizer>_<suite>_D<dim>.csv` + `per_run.csv` + `curves/` + `gen_logs/`).
The convergence-figure generators (§5 of the pipeline) also read curves and
gen_logs from there. For `gsk-stats`, a local reproduced run under
`results/_run_all/` is read only for the proposed optimizer, and only when the
reference tree lacks that cell; it never reads comparators from `results/`.
(The review pack below loads through `result_loader.load_comparison_set`,
which falls back to `results/` for any optimizer the reference tree lacks.)

**Analysing your own runs.** Because the committed panel is read first, a fresh
run of a cell it already carries does not change the report. Build a panel
folder in which your runs replace the committed files for the same optimizer
and dimension (everything you did not run keeps the committed file), then
point `--reference-root` at it; `--out` keeps the report apart from the default
`results/_run_all/_analysis/`:

```powershell
python scripts/build_stats_panel.py --suite cec2017 --results results/_run_all --out results/_own_panel
gsk-stats --suite cec2017 --reference-root results/_own_panel --out results/_own_panel/_analysis
```

**Regenerating reference data (avoid the doubled-suite trap).** The runner
**refuses** any `output_root` equal to or inside
`benchmarks/cec_reference_results` — `ensure_output_root_allowed` aborts at
startup, because the reference tree is the frozen evidence base. Regenerate into
a staging root under `results/` and promote the vetted bundle with
`scripts/promote_evidence.py` (promotion writes a versioned
`benchmarks/cec_reference_results/_releases/<release-id>/` subtree; it never
rewrites the flat live `<suite>/<optimizer>/` layout). The runner writes
`<output_root>/<optimizer>/<suite>/`, so point `output_root` at the containing
tree, **not** at a suite folder itself:

```powershell
# correct -> results/_refresh_staging/<optimizer>/<suite>/...
python run.py --root . --config <cfg>.yml   # with output_root: results/_refresh_staging
# WRONG (creates <root>/cec2017/<opt>/cec2017/...):
#   output_root: results/_refresh_staging/cec2017
```

Stream the per-dimension Wilcoxon + Friedman analysis live during a run with the
opt-in `--stats` flag (default off; it skips vanilla `gsk` — `cec2011` is
supported via its per-suite rollup):

```powershell
python run.py --root . --optimizer dt-gsk --suite cec2017 --dimension 10 --dimension 30 --stats
```

## Paper Review Pack

Build the advisor review PDF (matplotlib `PdfPages`, no LaTeX): a headline
dashboard, 7-algorithm CEC2017/CEC2011 mean tables, and 7-algorithm GSK-family
convergence grids. Missing convergence curves are logged, never fabricated.

```powershell
python papers/scripts/generate_review_pack.py
```

Writes `papers/DT-GSK-CEC2017-review.pdf` (and `..._missing.log`).

## DT-GSK Diagnostics

Opt-in per-generation telemetry for root-cause analysis (default off; observational
— it never changes RNG order, evaluations, or results). Enable it via
`optimizer_options.dt_diagnostics` in a YAML config; one JSONL trace is written
per cell under `<output_root>/dt-gsk/<suite>/diagnostics/`:

```yaml
optimizers: [dt-gsk]
suite: cec2017
functions: [4, 13, 19, 26, 30]
dimensions: [10, 30, 50, 100]
runs: 5
seed: 20240620
seed_policy: unified
rand_generator: threefry
parallel: true
workers: 2
generation_logs: true
convergence_graphs: false
overwrite: true
output_root: results/_experimental/dt_diag
optimizer_options:
  dt_diagnostics: true
  dt_diagnostics_include_all_fields: true
```

```powershell
python run.py --root . --config configs/experimental/dt_diag.yml
python scripts/analyze_dt_diagnostics.py --input results/_experimental/dt_diag/dt-gsk/cec2017/diagnostics --out results/_experimental/dt_diag/dt-gsk/cec2017/diagnostics_analysis
```

The analyzer writes `diagnostics_summary.csv`, `wrong_basin_candidates.csv`, and
per-subsystem summaries (ACE entropy, linkage reliability, diversity, local-search
ROI, boundary hits). Wrong-basin flagging is general — never hard-coded to a
function.

## DT-GSK Ablation (CEC2017)

The scaffold ablation isolates each DT-GSK mechanism on the full CEC2017 suite
(F1, F3--F30; n = 25) by toggling `optimizer_options` -- every mechanism defaults
to `True` in the locked profile, so a cell disables exactly one. The vendored ISM
core is byte-identity locked; these options are the sanctioned, code-untouching
way to configure it. **SGSM stays disabled throughout the scaffold ablation** --
the SGSM overlay is ablated separately (the CEC2013 hold-out, `full` /
`no-adaptive` / `no-sgsm` cells), not here.

Mechanism toggles (set to `false` to disable that cell's component):

| `optimizer_options` key | Mechanism |
|---|---|
| `ace_enabled` | ACE knowledge control |
| `psr_enabled` / `sp_nlpsr_enabled` | (NL)PSR population-size reduction |
| `bse_enabled` (`bse_cauchy_enabled`) | Budget-Safe Escape (+ Cauchy rescue) |
| `argp_enabled` | Acceptance-Rate Gated Pool Pruning |
| `linkage_blockwise_enabled` | Linkage-aware block crossover |
| `arch_enabled` | Elite archive |
| `local_search_enabled` | Coordinate endgame local search (`local_search_method` defaults to `coordinate`) |
| `final_polish_enabled` | Eigenframe final polish |
| `interaction_graph_enabled` | SGSM interaction graph (off for this ablation) |
| `deep_stall_restart_enabled` | Deep-stall full restart |

The pipeline is three scripts: `scripts/run_ablation.py` writes one config per
cell under `configs/_ablation/` and runs each to its own output dir;
`generate_ablation_matrix.py` rolls the cells up into the mean-Friedman-rank
matrix; `generate_ablation_exhibits.py` renders the supplement tables.

```powershell
# inspect the per-cell configs without running
python scripts/run_ablation.py --dimension 30 --dry-run

# run the default cell set (baseline + one disable-one cell per mechanism), n=25
python scripts/run_ablation.py --dimension 30 --runs 25 --workers 2

# or only a subset
python scripts/run_ablation.py --only baseline,no_linkage,no_bse

# aggregate the cells -> results/ablation/ablation_matrix_rank_summary_cec2017_D30.csv
python papers/scripts/generate_ablation_matrix.py --suite cec2017 --dimension 30

# render the scaffold-ablation supplement tables (SA01/SA02) -> papers/tables/SA01.tex, SA02.tex (\input in the supplement)
# (reads the manifest-verified frozen release copy, not the fresh results/ablation/ aggregate)
python papers/scripts/generate_ablation_exhibits.py
```

Per-cell output lands under `results/_ablation/<cell>/dt-gsk/<suite>/`. The
default set is the baseline (full scaffold, SGSM off) plus one disable-one cell
per mechanism; edit the `CELLS` dict in `scripts/run_ablation.py` to match the
full 16-cell design. Some mechanisms have paired flags (e.g. `psr_enabled` vs
`sp_nlpsr_enabled`, `bse_enabled` vs `bse_cauchy_enabled`) -- confirm the exact
semantics in `src/gsk_family/optimizers/_dt_profiles.py` before finalizing the
matrix.

Preview the enabled/disabled matrix for every cell without running:

```powershell
python scripts/run_ablation.py --dry-run          # remove-one (default)
python scripts/run_ablation.py --mode add-one --dry-run
```

`--mode` picks the ablation direction: **remove-one** (default) disables one
mechanism from the full scaffold; **add-one** enables one from bare GSK
(the ATMALS-GSK-style "enable one, keep the rest at base" design).

**Match ATMALS-GSK's protocol** with `--suite` (two suites) and, if you want its
exact direction, `--mode add-one`. ATMALS-GSK evaluated on CEC2017 (51 runs) and
CEC2011 (25 runs); run the ablation on both:

```powershell
# CEC2017 ablation at the main-study run count (51)
python scripts/run_ablation.py --suite cec2017 --dimension 10,30,50,100 --runs 51 --workers 15
# CEC2011 ablation (native dims; --dimension ignored)
python scripts/run_ablation.py --suite cec2011 --runs 25 --workers 15
python papers/scripts/generate_ablation_matrix.py --suite cec2011
```

Note: SGSM activates only at D >= 50, and CEC2011's native problem dims vary
widely, so the CEC2011 ablation mostly probes the scaffold mechanisms rather than
the SGSM overlay -- state that scope in the paper.

> The parameter-sensitivity study is a **separate** experiment, not ablation
> evidence. It is E4 of the round-1 revision campaign: 27 one-factor cells at
> D=30 and D=100, n = 15, promoted inside `rev-rel-2026-08-26-dd42d37eb` and
> reported as Table A46 (exhibit SA08). It is registered **exploratory** --
> descriptive only, no hypothesis tests and no corrected p-values. The older
> `results/dt-gsk/sweeps/parametric-study/` tree (n = 3) that T21/T22 would have
> come from is **absent** from this repository; that gap is EG-006 in
> `papers/governance/evidence_gap_register.md`, whose "omit" branch was
> exercised -- T21/T22 were never committed and the manuscript never cites them.

## Slow Or Crashing

If a campaign is thrashing memory or a worker keeps dying, step down the
concurrency before giving up on parallelism entirely:

```powershell
python run.py <args> --parallel --workers 2    # safe baseline
python run.py <args> --serial                  # single process, slowest but most robust
```

The default `process` backend self-heals: if a worker dies mid-run the pool is
rebuilt and the affected work is retried, falling back to serial for a cell that
still cannot complete -- so a run finishes rather than hanging. For CEC2017
composition cells (`F21`-`F30`) automatic process runs retain an upper
memory-safety cap of 8 workers; an explicit `--workers N` is treated as your
chosen speed/memory tradeoff.

Avoid `--parallel-backend thread` for real campaigns. Calling the parallel Numba
kernels from many Python threads can deadlock, and the threaded path does not
scale for these GIL-bound loops. Use the default process backend, or `--serial`.

## Quality Checks

```powershell
python -m pytest -q                                   # full test suite
python -m pytest tests\smoke\test_documentation_commands.py -q   # doc-path + command smoke
python -m ruff check .                                # lint
python scripts\validate_profile_lock.py --root .      # profile-lock validation
python scripts\build_docs_html.py                     # rebuild the HTML doc site
```


## Freeze-Pass Cycle (the passes-49..52 recipe)

Any edit to a hash-gated file (the 15 freeze files or the 2 hashed sources)
voids the current pass and takes a full cycle. The order below is the one that
worked four times in a row; deviations are where the recorded incidents live.

1. **Edit sources; rebuild the gated renders they feed.** Main PDF:
   `python papers/scripts/build_pdf.py`; DOCX: `build_docx.py`
   (+ `--supplementary` if supplementary.tex changed); supplement PDF:
   `build_supplementary.py`. Cover letter: `pdflatex` x2 in papers/ under
   `SOURCE_DATE_EPOCH=1783468800 FORCE_SOURCE_DATE=1`, then build twice and
   byte-compare (it must be deterministic).
2. **Commit the APPLY.** The marked PDFs and the change register diff
   `v2.13..HEAD` (committed refs, not the working tree), so they can only be
   rebuilt AFTER this commit: `build_change_marked_pdf.py --doc main` /
   `--doc supplementary`, then `build_change_register.py` — read the passage
   count it prints and sync it wherever it is quoted if it moved.
3. **Mint the freeze manifest** (papers/governance/main_manuscript_freeze_manifest.json,
   CRLF): byte-surgical text replacement, never json.dump; update sha256+bytes
   per changed file, generated_utc, anchor_commit = the apply commit, and the
   phase text. `check_manifest.py` must then read 15/15 AND sources 2/2.
4. **Update the package manifest** (submission_package_manifest.json, CRLF):
   sha256, bytes, pages, version id, note, authoritative_commit. **After
   writing, re-verify sha AND bytes against disk** — the pass-51 updater's
   size needle silently never matched and left stale byte counts that no gate
   checks (found and fixed in pass-52).
5. **Run the 13-gate ladder twice** (section 8b above plus profile-lock).
6. **File the governance pair** (next free CR-xxxx / D-xxxx — verify free at
   apply time), sync the status banners (REVISION_STATUS, CLAUDE.md,
   papers/PAPER_REVIEW_PROMPT.md), commit the close.
7. **Bump CITATION.cff BEFORE cutting the tag** (no leading v in the cff
   version; the tag-before-bump mistake was made twice and is caught by
   `validate_citation_cff.py`), then tag vN.NN and push main + tag.

The reviewer-facing response letter is untracked (D-0049) and outside the
freeze; its exact rebuild command — with the load-bearing
`Ligatures=NoCommon`, `HyphenChar=None` and letter-specific epoch — is
recorded in papers/submission/SUBMISSION_KIT.md. Sweep phrase-level policies
against the RENDER (pdftotext), never only the source: line-wrapped phrases
defeat source grep (pass-51 lesson).
