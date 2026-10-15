# Runbook

> Generated from the root [runbook.md](../../runbook.md) by `scripts/build_runbook_html.py`; edit that file, not this one. This page is Part 1, the run-and-test guide. Part 2, the maintainer and paper-pipeline reference, is in the [root runbook](../../runbook.md#part-2-maintainer-and-paper-pipeline-reference), and a standalone formatted copy is [runbook.html](../../runbook.html).

How to install, test and run DT-GSK (the proposed Dimension-Tiered
Gaining-Sharing Knowledge algorithm) and the six GSK-family algorithms it is
compared with, on five CEC benchmark suites.

| If you want to | Read |
|---|---|
| Install, test and run the algorithms, and compare their results | [Part 1](#part-1-run-and-test-dt-gsk) (about 30 minutes to a first result, most of it installing and testing) |
| Rebuild the paper, run the revision experiments, or run the release gates | [Part 2](../../runbook.md#part-2-maintainer-and-paper-pipeline-reference) |

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

> **Every new terminal window:** go to the project folder and activate the environment again (`.venv\Scripts\activate` on Windows, `source .venv/bin/activate` on Linux or macOS) before running anything below.

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
