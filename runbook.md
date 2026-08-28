# Runbook

Copy-paste commands for the DT-GSK repository. Run everything from
the repository root (the folder that contains `run.py`, `pyproject.toml`, and
`src/gsk_family/`). Every command below passes `--root .`, so it is portable
regardless of where the checkout lives on disk:

```powershell
# from the repository root (the directory holding run.py)
python run.py --root . --help
```

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

`gsk-list` is installed by the editable install (`pip install -e .`); from a
plain `pip` checkout call `python -m gsk_family.cli.list` instead.

## Setup

Editable install with the dev extra (enables the `gsk-*` console scripts plus
test, lint, and docs tooling), then run the test suite:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
```

Plain pip instead (libraries only, no editable package -- use `python run.py`
and the `python -m gsk_family.cli.*` module forms rather than the `gsk-*`
scripts):

```powershell
python -m pip install -r requirements.txt        # runtime only
python -m pip install -r requirements-dev.txt    # runtime + dev tooling
```

Requires CPython `>=3.10,<3.14`. The runtime stack is NumPy, SciPy, pandas,
matplotlib, PyYAML, and Numba (version ranges pinned in `pyproject.toml`).

## Journal Revision Experiments (one command)

The four reviewer-requested experiments from the *Algorithms* round-1 major
revision (D-0047, CR-0023). The other six reviewer points needed no runs and are
already applied.

**Rehearse first — 20 seconds, and it verifies itself:**

```powershell
python scripts\run_revision_experiments.py --smoke
```

Runs every leg *kind* through the identical code path at tiny scope (2
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
| | | **Total** | **32,451** |

Roughly 25–33 hours at 15 workers. Progress is printed and appended to
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
reference-seed, per-optimizer, targeted).

```powershell
# --- 1. Generate run data: the three benchmark campaigns ---
# --numba-threads 1 is NOT optional at D >= 50. run.py pins nothing by itself
# (only scripts/run_campaign.py does), and thread count sets the reduction order
# of the eigendecomposition behind the final polish, so an unpinned re-run is not
# comparable with a pinned one. It is NOT a promise that a pinned re-run
# reproduces archived bytes: D-0051 demonstrated the opposite across builds --
# a pinned re-execution reproduced the transplant arm on all 26 divergent cells
# and the archive on none. Pin it so a run is comparable with itself.
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 15 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2011 --function 1:22 --dimension native --runs 25 --parallel --workers 15 --numba-threads 1 --convergence-graphs --overwrite
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --parallel --workers 15 --numba-threads 1 --convergence-graphs --overwrite

# --- 1b. The two additional suites (five-suite scope, CR-0019): campaign launchers
#     with per-suite locked configs and resume support ---
python scripts/run_all_cec2020.py
python scripts/run_all_cec2013lsgo.py

# --- 2. DT-GSK scaffold ablation: CEC2017, all dimensions ---
python scripts/run_ablation.py --dimension 10,30,50,100 --runs 51 --workers 15

# --- 3. Statistical panels (per suite) ---
python -m gsk_family.cli.stats --suite CEC2017 --dims 10,30,50,100
python -m gsk_family.cli.stats --suite CEC2011
python -m gsk_family.cli.stats --suite CEC2013 --dims 10,30,50

# --- 3b. Registered CEC2020 + CEC2013LSGO batteries (phase6b; reads the two
#     promoted releases, reproduces Amendments 1-3's pinned values or fails) ---
python papers/scripts/phase6b_run_analysis_newsuites.py --suite both

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

# --- 7. Build the PDFs. The epoch is load-bearing: build_pdf.py sets nothing
#     itself and passes no env to pdflatex, so without these two variables the
#     artifacts carry the current date, are not byte-reproducible, and
#     check_manifest will not read 15/15 ---
$env:SOURCE_DATE_EPOCH = "1783468800"; $env:FORCE_SOURCE_DATE = "1"
python papers/scripts/build_pdf.py
python papers/scripts/build_supplementary.py
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

# --- 8b. Manuscript gate battery (the pass-41 battery, unchanged through pass-52). Every one must exit 0;
#     the three counted ones read 15/15, 115/115 and 761 rows / 0 FAIL ---
python papers/scripts/check_manifest.py
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
python run.py --root . --config configs/smoke.yml
```

## CEC2017 All Optimizers

Use a visible worker count in campaign commands. The safe baseline is
`--workers 2`; increase the number only when you know the machine has spare CPU
and memory and you are not running other heavy work. `--convergence-graphs`
opts in to rendered PNG plots; omit it when you only need the convergence CSV
files.

```powershell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
```

`--overwrite` recomputes matching cells. Omit it only when you intentionally
want to resume and skip finished cells.

## Other Full Sweeps

Benchmark backend defaults to `auto`, which uses the Python/Numba evaluator.
Use `--parallel --workers 2` as the safe baseline; raise `2` deliberately when
the machine has enough headroom.

```powershell
# CEC2020 - 10 functions, dims 5/10/15/20
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2020 --function 1:10 --dimension 5,10,15,20 --runs 30 --parallel --workers 2 --convergence-graphs --overwrite

# CEC2013 - 28 functions, dims 10/30/50
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite

# CEC2011 - native per-problem dims
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2011 --function 1:22 --dimension native --runs 25 --parallel --workers 2 --convergence-graphs --overwrite

# CEC2013-LSGO - D=1000, very expensive; shown for one optimizer
python run.py --root . --optimizer gsk --suite cec2013lsgo --function 1:15 --dimension 1000 --runs 25 --parallel --workers 2 --convergence-graphs --overwrite
```

## CEC2013 Family Panel

CEC2013 is the second GSK-family comparison suite: 28 functions, dims 10/30/50,
51 runs (CEC2013 competition standard). Run the full 7-optimizer panel (note:
`egsk` runs via the scipy-SLSQP port, and the statistical panel reads `egsk`
from the committed `scipy`-SLSQP port CSVs, the comparator of record):

```powershell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
```

Tight on memory -- one optimizer at a time (repeat per optimizer id):

```powershell
python run.py --root . --optimizer dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
```

Reproduce under the reference seed labels (to line up with imported reference
CSVs when validating):

```powershell
python run.py --root . --optimizer dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --seed-policy reference --parallel --workers 2 --overwrite
```

Outputs land under `results/_run_all/<optimizer>/cec2013/`. Then build the
CEC2013 family report (Friedman ranks, Nemenyi CD, pairwise Wilcoxon/Holm, effect
sizes) -- comparators are read from `benchmarks/cec_reference_results/cec2013/`:

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

Each launcher wraps the corresponding full-suite campaign so you do not have to
retype the long flag list. They live in `scripts/` (see
[scripts/README.md](scripts/README.md)):

```powershell
python scripts\run_all_cec2017.py
python scripts\run_all_cec2011.py
python scripts\run_all_cec2020.py
python scripts\run_all_cec2013.py
python scripts\run_all_cec2013lsgo.py
```

You can also drive campaigns directly from the YAML files in `configs/`:

```powershell
python run.py --root . --config configs/all_cec2017.yml
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
| `--overwrite` | Recompute matching cells; omit to resume and skip finished cells. |
| `--seed-policy reference` | Use the reference seed labels instead of the default unified schedule. |
| `--stats` | Stream per-dimension Wilcoxon + Friedman analysis live (opt-in; skips vanilla `gsk`; `cec2011` reports via its per-suite rollup). |

## Tight On Memory

Run one optimizer at a time with the same safe worker baseline. Omit
`--overwrite` only when you intentionally want to resume.

```powershell
python run.py --root . --optimizer gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
python run.py --root . --optimizer agsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
python run.py --root . --optimizer apgsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
python run.py --root . --optimizer fdb-agsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
python run.py --root . --optimizer atmals-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
python run.py --root . --optimizer egsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
python run.py --root . --optimizer dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite
```

Need more speed? Increase the worker count deliberately:

```powershell
python run.py --root . --optimizer gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 4 --convergence-graphs --overwrite
```

## Targeted Runs

```powershell
# One optimizer, one function, one dimension
python run.py --root . --optimizer agsk --suite cec2017 --function 5 --dimension 30 --runs 51 --parallel --workers 2 --convergence-graphs --overwrite

# Same run with reference seed policy
python run.py --root . --optimizer agsk --suite cec2017 --function 5 --dimension 30 --runs 51 --seed-policy reference --parallel --workers 2 --convergence-graphs --overwrite
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
gen_logs from there. A local reproduced run under `results/_run_all/` is used
only as a fallback when the reference tree lacks a cell.

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
