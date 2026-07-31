# PHASE 0 — Environment, Audit & Provenance Ledger

> **⚑ Revision 2 addendum applies to this phase.** Before executing, read [ADDENDUM_R2_cec2013_and_ablation.md](ADDENDUM_R2_cec2013_and_ablation.md) §R2.C — a CEC2013 family panel and the CEC2017 scaffold ablation add tasks to this phase, and the addendum overrides this file where they disagree.

**Objective:** Before a single sentence of the manuscript is touched, build a complete, machine-checkable inventory of every paper asset (tables, figures, sections, bib) and every piece of numerical evidence behind it, so that Phase 1 can scope the paper against evidence that is *known* to exist and be current — not assumed.

> This file expands **Phase 0** of `papers/PAPER_BUILD_PROMPT.md` into concrete, grounded micro-steps. It produces three artifacts (`asset_map.md`, `data_ledger.csv`, an evidence-readiness note) and hands off to `papers/build_prompt_phases/PHASE_1_scope.md`. Phase 0 changes **nothing** in the manuscript, results, or reference data — it only *reads, hashes, and records*.

All commands assume the current directory is the repo root:

```
D:\AI\PhD-Projects\00-GSK-Family\02-GSK_Family_Python_v1.1
```

Windows is primary (PowerShell), with Bash equivalents where useful. Use `python` (not `python3`).

---

## Prerequisites

- [ ] A **clean checkout** with no uncommitted changes to code, `benchmarks/`, or `results/`. Confirm with:

  ```powershell
  git status --porcelain
  git rev-parse HEAD
  ```

  ```bash
  git status --porcelain
  git rev-parse HEAD
  ```

  If `git status --porcelain` prints anything under `benchmarks/`, `results/_run_all/`, `src/`, `optimizers/`, or `papers/tables|figures`, **stop and reconcile** before auditing — a dirty tree makes provenance meaningless.

- [ ] Record the exact commit now; this is the **anchor SHA** every "reproducible from" claim in the paper will cite:

  ```powershell
  $ANCHOR = git rev-parse HEAD
  "anchor_commit=$ANCHOR"
  ```

Nothing else is required — Phase 0 is the first phase and consumes only what is already in the tree.

---

## Inputs (concrete dirs/files read; none written outside `papers/build_prompt_phases/`)

Manuscript surface (`papers/`):
- `papers/main.tex`, `papers/supplementary.tex`, `papers/cover_letter.tex`, `papers/PAPER_BUILD_PROMPT.md`
- `papers/Definitions/mdpi.cls`, `papers/Definitions/journalnames.tex`
- `papers/sections/{introduction,literature_review,proposed_algorithm,performance,conclusions,supplementary_content}.tex`
- `papers/tables/T01.tex … T16.tex`, `papers/tables/T16_bca.tex`, `papers/tables/T21.tex`, `papers/tables/T22.tex`
- `papers/figures/{convergence,diagrams,flowchart,ranks,taxonomy,traces}/`
- `papers/references.bib` (must mirror `reference_papers/references.bib`)

Evidence surface (repo):
- `results/_run_all/<optimizer>/<suite>/summary/` — per-run aggregates, `environment.json`, `run_config.json`, `seed_schedule.csv`, `phase0_protocol.json`, `verification.json`, `per_run.csv`, `<optimizer>_<suite>_D<dim>.csv`
- `results/_run_all/<optimizer>/<suite>/curves/` — convergence CSVs (feed `scripts/plot_convergence_from_curves.py`)
- `results/_analysis/` — aggregated stats / figure inputs
- `benchmarks/cec_suite_python/{cec2011,cec2013,cec2013lsgo,cec2017,cec2020}/` — evaluators + data (evidence generators)
- `benchmarks/cec_reference_results/{cec2011,cec2013,cec2013lsgo,cec2017,cec2020}/` — **READ-ONLY** reference CSVs + `environment.json`; never edit. **Primary evidence, flat per-optimizer layout**: `<suite>/<optimizer>/<opt>_<suite>_D<dim>.csv` (+ `per_run.csv`, `curves/`, `gen_logs/`, `environment.json` / `run_config.json` / `seed_schedule.csv` / `verification.json` / `phase0_protocol.json`). The **full 7-optimizer panel exists for cec2017, cec2011, and cec2013**; cec2020 (agsk only) and cec2013lsgo (decc-g, mos) are partial context suites. The analysis loader (`result_loader.load_algorithm`) resolves every cell from here **first**; `results/_run_all/` is only a fallback.

Policy / provenance surface:
- `src/gsk_family/analysis/project_policy.py` — `RUNNABLE_OPTIMIZERS`, `REFERENCE_COMPARATORS`
- `src/gsk_family/runners/seed_policy.py` — `get_cec_seed(...)`
- `src/gsk_family/optimizers/_dt_core.py`, `src/gsk_family/optimizers/_dt_subsystems/`, `src/gsk_family/optimizers/_dt_rng.py`, `src/gsk_family/optimizers/_dt_profiles.py` — byte-identity-locked ISM core

---

## Tasks

The 7-algorithm family panel (fixed, do not add/remove members in Phase 0):

```
gsk   agsk   apgsk   fdb-agsk   atmals-gsk   egsk   dt-gsk(proposed)
```

Conventions to enforce while auditing:
- **CEC2017:** 51 runs, **F2 excluded**, D ∈ {10, 30, 50, 100}
- **CEC2011:** 25 runs (native dims)
- **CEC2013:** 51 runs, 28 functions, D ∈ {10, 30, 50}
- Seed: `get_cec_seed(20240620, dim, func, run) % 2147483646 + 1` (`src/gsk_family/runners/seed_policy.py`)

---

### 0.1 — Asset map (`asset_map.md`)

Goal: one row per `papers/` file classified **keep / rewrite / regenerate**, and for every table and figure the *exact* backing evidence identified and confirmed present.

**Step 0.1.a — Enumerate every manuscript file.**

```powershell
Get-ChildItem -Recurse -File papers `
  | Where-Object { $_.FullName -notmatch '\\build_prompt_phases\\' } `
  | Select-Object @{n='rel';e={Resolve-Path -Relative $_.FullName}}, Length, LastWriteTime `
  | Sort-Object rel
```

```bash
find papers -type f -not -path 'papers/build_prompt_phases/*' -printf '%p\t%s\t%TY-%Tm-%Td\n' | sort
```

Expected: `main.tex`, `supplementary.tex`, `cover_letter.tex`, `PAPER_BUILD_PROMPT.md`, `README.md`, the 6 `sections/*.tex`, the tables listed above, and the six `figures/` subfolders.

**Step 0.1.b — Confirm the `\input` spine matches the declared order.** Extract include order from `main.tex` and `supplementary.tex`:

```powershell
Select-String -Path papers\main.tex,papers\supplementary.tex -Pattern '\\input\{([^}]+)\}' `
  | ForEach-Object { $_.Matches.Groups[1].Value }
```

```bash
grep -oE '\\input\{[^}]+\}' papers/main.tex papers/supplementary.tex
```

Expected `main.tex` body order: `sections/introduction` → `literature_review` → `proposed_algorithm` → `performance` → `conclusions`. Expected supplement: `sections/supplementary_content`. Flag any `\input` that points to a file **not** on disk, and any on-disk section/table **not** referenced by an `\input`.

**Step 0.1.c — Map each `tables/T*.tex` to its backing result file(s).** The tables are pre-rendered LaTeX `tabular` bodies (e.g. `T01.tex` opens with `\begin{tabular}{lrrrrrrrrrr}` and cites `\bestval{...}` around winning cells). They contain **no** `\input`/CSV hook, so the mapping must be reconstructed from column headers + generator. For each `T*.tex`:

1. Read the header row to recover which **optimizers**, **suite**, **dimension**, and **statistic** (Best/Median/Worst/Mean/SD, or ranks, or p-values) it renders.

   ```powershell
   Get-ChildItem papers\tables\T*.tex | ForEach-Object {
     "`n=== $($_.Name) ==="
     Get-Content $_.FullName -TotalCount 6
   }
   ```

   ```bash
   for f in papers/tables/T*.tex; do echo "=== $f ==="; head -6 "$f"; done
   ```

2. Identify the generator. LaTeX table bodies in this project are emitted by `src/gsk_family/analysis/latex_tables.py` (driven off the analysis layer / `results/_analysis/`). Locate the emitter for each table id:

   ```powershell
   Select-String -Path src\gsk_family\analysis\latex_tables.py -Pattern 'T0?\d|T1\d|T2\d|bestval|tabular' -Context 0,1
   ```

   ```bash
   grep -nE 'T[0-9]{2}|bestval|tabular|to_latex' src/gsk_family/analysis/latex_tables.py
   ```

3. Resolve the source CSV(s) under `benchmarks/cec_reference_results/<suite>/<optimizer>/` (the primary reference panel), `results/_run_all/<optimizer>/<suite>/summary/` (fallback reproductions), or `results/_analysis/` (cross-optimizer stats) and **confirm each exists and is newer than or equal to** the `.tex` it feeds. Record `stale` if any backing CSV's `LastWriteTime` is **older** than the table's, or if the anchor commit touched the CSV after the table was generated.

Record for each table row of `asset_map.md`:
`table_id | suite | dim | optimizers_shown | statistic | backing_source(s) | source_exists(Y/N) | source_current(Y/N/stale) | class(keep/rewrite/regenerate)`

> Note discovered in audit prep: the tables directory holds `T01–T16`, `T16_bca`, `T21`, `T22`. **`T17–T20` are absent.** Do not assume they exist — either they were renumbered/dropped or are pending. Flag the gap explicitly in `asset_map.md` and defer the keep/scope decision to Phase 1; do not fabricate them.

**Step 0.1.d — Map each figure to its generator + source CSV(s).** For every PDF/PNG under `papers/figures/*`:

```powershell
Get-ChildItem -Recurse -File papers\figures | Select-Object @{n='rel';e={Resolve-Path -Relative $_.FullName}}, LastWriteTime
```

```bash
find papers/figures -type f | sort
```

- `figures/convergence/*` → generated by the paper generators `papers/scripts/generate_full_convergence.py` (CEC2017), `generate_cec2011_convergence.py`, and `generate_cec2013_convergence.py`, which read curves/gen_logs from `benchmarks/cec_reference_results/<suite>/<optimizer>/` (reference-first); `scripts/plot_convergence_from_curves.py` renders single-cell PNGs from a `--root`'s `curves/*.csv`. Open the script headers/argparse to confirm which curves dir + optimizers each reads:

  ```powershell
  Select-String -Path scripts\plot_convergence_from_curves.py -Pattern 'add_argument|curves|glob|read_csv|savefig'
  ```

  ```bash
  grep -nE 'add_argument|curves|glob|read_csv|savefig' scripts/plot_convergence_from_curves.py
  ```

- `figures/ranks/*` → rank/CD-style plots; source = aggregated stats in `results/_analysis/` via `src/gsk_family/analysis/figures.py`.
- `figures/{diagrams,flowchart,taxonomy}/*` → **authored** vector art (no result CSV). Class these `keep` unless the design changes; they have **no data source** and must not be tagged `regenerate` for data reasons.
- `figures/traces/*` → parity/diagnostic traces; source = `scripts/parity_trace.py` / `scripts/analyze_dt_diagnostics.py` outputs. Confirm which by grepping the scripts' `savefig`/output paths.

Record for each figure row:
`figure_path | generator_script | source_csv(s) | source_exists(Y/N) | data_backed(Y/N) | class`.

---

### 0.2 — Data ledger (`data_ledger.csv`)

Goal: one row per **(optimizer × suite × dimension)** cell across the 7-panel, recording where the evidence lives, how much of it there is, and whether it is complete. This is the single source of truth for what the paper can honestly claim.

**Step 0.2.a — Enumerate what actually exists under `_run_all`.**

```powershell
Get-ChildItem results\_run_all -Directory | ForEach-Object {
  $opt = $_.Name
  Get-ChildItem $_.FullName -Directory | ForEach-Object { "$opt/$($_.Name)" }
}
```

```bash
for o in results/_run_all/*/; do for s in "$o"*/; do echo "$(basename "$o")/$(basename "$s")"; done; done
```

Expected present at anchor: **all seven optimizers** (`gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`, `egsk`, `dt-gsk`), each with `cec2011`, `cec2013`, and `cec2017` subtrees (plus an `_analysis/` dir). These `_run_all` trees are local reproductions — the committed reference panel under `benchmarks/cec_reference_results/` is the primary evidence, so a residual `_run_all` gap is not a paper blocker when the reference cell exists; record both sources in the ledger and route any genuine gap in Step 0.2.d.

**Step 0.2.b — For each existing cell, read provenance from the summary dir.** Each `results/_run_all/<optimizer>/<suite>/summary/` contains `environment.json`, `run_config.json`, `seed_schedule.csv`, `phase0_protocol.json`, `verification.json`, `per_run.csv`, and `<optimizer>_<suite>_D<dim>.csv`. Pull the fields:

```powershell
Get-ChildItem results\_run_all\*\*\summary\run_config.json | ForEach-Object {
  $j = Get-Content $_.FullName -Raw | ConvertFrom-Json
  [pscustomobject]@{
    path      = Resolve-Path -Relative $_.FullName
    optimizer = $j.optimizer
    suite     = $j.suite
    dims      = ($j.dims -join ';')
    n_runs    = $j.n_runs
    seed      = $j.seed_policy
    commit    = $j.commit_sha
  }
} | Format-Table -AutoSize
```

```bash
for f in results/_run_all/*/*/summary/run_config.json; do
  echo "=== $f ==="
  python -c "import json,sys; d=json.load(open(sys.argv[1])); print({k:d.get(k) for k in ('optimizer','suite','dims','n_runs','seed_policy','commit_sha')})" "$f"
done
```

> Field names above are the *expected* keys — confirm them against an actual `run_config.json` before scripting the loop, and adjust the key names to match. Do not invent keys that are not present.

**Step 0.2.c — Verify counts against convention.** For each cell, cross-check `n_runs` and the per-dim CSV row count:
- CEC2017 → `n_runs == 51`, **F2 excluded** (the F-list should skip F2), D covers {10,30,50,100}.
- CEC2011 → `n_runs == 25` (native dims).
- CEC2013 → `n_runs == 51`, 28 functions, D covers {10,30,50}.
- Seed policy string must resolve to `get_cec_seed(20240620, dim, func, run) % 2147483646 + 1`.

```powershell
Get-ChildItem results\_run_all\*\*\summary\per_run.csv | ForEach-Object {
  $n = (Import-Csv $_.FullName | Measure-Object).Count
  "$([IO.Path]::GetFileName((Split-Path $_.FullName -Parent -Resolve)))  rows=$n  ($($_.FullName))"
}
```

```bash
for f in results/_run_all/*/*/summary/per_run.csv; do echo "$f  rows=$(($(wc -l < "$f")-1))"; done
```

Flag any cell where the row count is inconsistent with `runs × functions × dims` for its suite.

**Step 0.2.d — Build the full 7×suites×dims matrix and mark every gap.** Emit `data_ledger.csv` with header:

```
optimizer,suite,dimension,n_runs,seed_policy,source_path,commit_sha,status
```

`status` ∈ `{present, missing, count_mismatch, stale}`. Then decide **per gap**:
- **Regenerate** — the panel needs the cell and it is producible with an in-repo runner. Write a regeneration ticket naming the exact script:
  - CEC2017 → `python scripts\run_all_cec2017.py` (also `run_all_cec2011.py`, `run_all_cec2013.py`, `run_all_cec2013lsgo.py`, `run_all_cec2020.py` for other suites); family sweep → `python scripts\run_gsk_family.py`.
  - Ticket must state optimizer, suite, dims, expected n_runs, and the anchor commit to run at. **Phase 0 does not run these** — it only files the ticket.
  - Every ticket must carry the **doubled-suite `output_root` trap** warning: the runner writes to `<output_root>/<optimizer>/<suite>/`, so `--output-root` (or `output_root:` in the YAML) must point at the tree that *contains* the suite folders, never at a suite folder itself — otherwise you create a nested `<suite>/<opt>/<suite>/…` tree.
- **Rescope** — the paper will not claim that cell; note it so Phase 1 narrows scope accordingly.

Cross-reference `src/gsk_family/analysis/project_policy.py`: an optimizer in `RUNNABLE_OPTIMIZERS` can be regenerated; one only in `REFERENCE_COMPARATORS` must be sourced from `benchmarks/cec_reference_results/` (read-only) rather than re-run.

```powershell
Select-String -Path src\gsk_family\analysis\project_policy.py -Pattern 'RUNNABLE_OPTIMIZERS|REFERENCE_COMPARATORS' -Context 0,8
```

```bash
grep -nA8 -E 'RUNNABLE_OPTIMIZERS|REFERENCE_COMPARATORS' src/gsk_family/analysis/project_policy.py
```

> Panel note: `benchmarks/cec_reference_results/` carries the **full 7-optimizer panel** for cec2017, cec2011, **and** cec2013 in the flat layout — every optimizer (the proposed `dt-gsk` included) with its own summaries, `per_run.csv`, `curves/`, `gen_logs/`, and provenance JSONs. The task here is to **audit that committed panel**, not to regenerate or re-locate it. In the ledger, distinguish `source_path` under `cec_reference_results/` (reference, primary) from `_run_all/` (own reproductions, fallback), and never plan to *edit* the former.

---

### 0.3 — Reproducibility scaffolding

Goal: lock the three things every reproducibility claim depends on — the FP-regime sentinel, the profile lock, and the anchor commit.

**Step 0.3.a — Confirm the FP-regime sentinel in each `environment.json`.** The CEC2017 canonical FP-regime prefix is `8bda40d8…`. Read the sentinel from every summary and reference `environment.json` and confirm the CEC2017 ones carry the canonical prefix:

```powershell
Get-ChildItem -Recurse -File -Filter environment.json results\_run_all, benchmarks\cec_reference_results | ForEach-Object {
  $j = Get-Content $_.FullName -Raw | ConvertFrom-Json
  [pscustomobject]@{ path = Resolve-Path -Relative $_.FullName; fp = $j.fp_regime_sentinel }
} | Format-Table -AutoSize
```

```bash
find results/_run_all benchmarks/cec_reference_results -name environment.json | while read f; do
  echo "$f -> $(python -c "import json,sys;print(json.load(open(sys.argv[1])).get('fp_regime_sentinel'))" "$f")"
done
```

> Confirm the actual JSON key holding the sentinel by inspecting one file first; adjust `fp_regime_sentinel` to the real key. Any CEC2017 `environment.json` whose sentinel does **not** start with `8bda40d8` is a **hard stop** — the run was produced under a different FP regime and cannot be pooled with the canonical set.

**Step 0.3.b — Confirm the profile lock passes.** The ISM core is byte-identity-locked (`src/gsk_family/optimizers/_dt_core.py`, `src/gsk_family/optimizers/_dt_subsystems/`, `src/gsk_family/optimizers/_dt_rng.py`, `src/gsk_family/optimizers/_dt_profiles.py`).

```powershell
python scripts\validate_profile_lock.py --root .
```

```bash
python scripts/validate_profile_lock.py --root .
```

Expected: a pass/OK exit (exit code 0). A failure here means the proposed algorithm's frozen profile drifted — resolve before any paper number is trusted.

**Step 0.3.c — Record the anchor commit for "reproducible from" claims.** Persist the anchor SHA captured in Prerequisites into the evidence-readiness note; every headline number in the paper cites this SHA:

```powershell
git rev-parse HEAD
git show -s --format='%H %ci %s' HEAD
```

```bash
git rev-parse HEAD
git show -s --format='%H %ci %s' HEAD
```

**Step 0.3.d — Sanity green-gate (read-only confirmation).** Confirm the tree is green so the audit rests on a healthy build. These are checks, not fixes:

```powershell
python -m pytest -q
python -m ruff check .
python scripts\build_docs_html.py
```

```bash
python -m pytest -q
python -m ruff check .
python scripts/build_docs_html.py
```

Record pass/fail of each in the readiness note. A red gate does not block Phase 0's inventory work, but it **must** be surfaced as a risk to Phase 1.

---

### 0.4 — Citation snapshot

Goal: freeze the citation universe so the paper can only cite within the 57 locked keys, and confirm the bib parses.

**Step 0.4.a — Dump and count the bib keys.** `papers/references.bib` must contain exactly **57** entries and mirror `reference_papers/references.bib`.

```powershell
$keys = Select-String -Path papers\references.bib -Pattern '^@\w+\{([^,]+),' `
  | ForEach-Object { $_.Matches.Groups[1].Value }
"count=$($keys.Count)"
$keys | Sort-Object | Set-Content papers\build_prompt_phases\_bibkeys.txt
```

```bash
grep -oE '^@[A-Za-z]+\{[^,]+,' papers/references.bib | sed -E 's/^@[A-Za-z]+\{//; s/,$//' | sort > papers/build_prompt_phases/_bibkeys.txt
wc -l papers/build_prompt_phases/_bibkeys.txt   # expect 57
```

**Step 0.4.b — Confirm the two bib files agree.** Diff the key sets of `papers/references.bib` vs `reference_papers/references.bib`:

```powershell
$a = Select-String papers\references.bib -Pattern '^@\w+\{([^,]+),' | ForEach-Object { $_.Matches.Groups[1].Value } | Sort-Object
$b = Select-String reference_papers\references.bib -Pattern '^@\w+\{([^,]+),' | ForEach-Object { $_.Matches.Groups[1].Value } | Sort-Object
Compare-Object $a $b
```

```bash
diff <(grep -oE '^@[A-Za-z]+\{[^,]+' papers/references.bib | sed -E 's/^@[A-Za-z]+\{//' | sort) \
     <(grep -oE '^@[A-Za-z]+\{[^,]+' reference_papers/references.bib | sed -E 's/^@[A-Za-z]+\{//' | sort)
```

Expected: no differences. Any divergence is a provenance defect — `papers/references.bib` is the manuscript copy and must mirror the locked master. (The authoritative full list is Appendix A of `papers/PAPER_BUILD_PROMPT.md`; cross-check the dumped keys against it.)

**Step 0.4.c — Confirm the bib parses.** A minimal parse check without a full LaTeX build:

```powershell
python -c "import re; t=open('papers/references.bib',encoding='utf-8').read(); print('entries=', len(re.findall(r'^@', t, re.M)))"
```

```bash
python -c "import re; t=open('papers/references.bib',encoding='utf-8').read(); print('entries=', len(re.findall(r'^@', t, re.M)))"
```

If BibTeX is available, a stricter check is `bibtex`/`biber` dry-run — otherwise the regex entry count plus the diff in 0.4.b is sufficient for Phase 0.

**Step 0.4.d — Establish the cite-set-is-subset invariant.** Record in the readiness note that any key later `\cite{}`-d in `papers/sections/*.tex` MUST appear in `_bibkeys.txt`. (Enforcement runs in later phases; Phase 0 only fixes the universe of 57.)

---

## Worked examples

**A — Coverage matrix over `_run_all` (Python; prints panel × suite × dim presence).**

```python
# scratch script; reads only, prints a matrix. Run from repo root: python this.py
import os, glob, json

PANEL  = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk", "dt-gsk"]
DIMS   = [10, 30, 50, 100]
root   = os.path.join("results", "_run_all")

print(f"{'optimizer':<12} {'suite':<10} " + " ".join(f"D{d:<4}" for d in DIMS))
for opt in PANEL:
    suites = sorted(os.path.basename(p) for p in glob.glob(os.path.join(root, opt, "*")))
    if not suites:
        print(f"{opt:<12} {'<MISSING>':<10} " + " ".join(" -   " for _ in DIMS))
        continue
    for suite in suites:
        cells = []
        for d in DIMS:
            csv = glob.glob(os.path.join(root, opt, suite, "summary", f"{opt}_{suite}_D{d}.csv"))
            cells.append(" Y   " if csv else " -   ")
        print(f"{opt:<12} {suite:<10} " + " ".join(cells))
```

Expected at anchor: `Y` rows for **all seven optimizers** on `cec2017` (plus `cec2011`/`cec2013` suite rows; CEC2013 dims stop at D50). This matrix covers only the `_run_all` fallback tree — sweep `benchmarks/cec_reference_results/<suite>/<optimizer>/` (flat layout, no `summary/` subdir) the same way for the primary panel.

**B — List tables and pull their header + winner-cell hooks (Bash).**

```bash
for f in papers/tables/T*.tex; do
  echo "=== $f ==="
  head -4 "$f"                            # column headers -> optimizers/statistic
  echo "  bestval cells: $(grep -o '\\bestval' "$f" | wc -l)"
  echo "  win/lose/tie : + $(grep -o '\\wmark' "$f" | wc -l)  - $(grep -o '\\lmark' "$f" | wc -l)  ~ $(grep -o '\\emark' "$f" | wc -l)"
done
```

This recovers, per table, which optimizers appear (header), how many winning cells are marked (`\bestval`), and any pairwise win/loss/tie tallies (`\wmark`/`\lmark`/`\emark`) — enough to infer suite/dim/statistic for the asset map.

**C — Provenance one-liner per summary (Bash).**

```bash
for f in results/_run_all/*/*/summary/environment.json; do
  echo "$f"
  python -c "import json,sys; d=json.load(open(sys.argv[1])); print('  ', {k:d.get(k) for k in list(d)[:8]})" "$f"
done
```

Use it to eyeball the real JSON keys (FP sentinel, commit, dims, runs) before hard-coding key names in the ledger loops.

---

## Pitfalls & anti-patterns

- **Trusting a `T*.tex` whose backing CSV is stale.** The tables are frozen LaTeX bodies with numbers baked in; they do **not** update when a CSV changes. Always compare the table's `LastWriteTime` (and the anchor commit's touch history) against its source before classing it `keep`. When in doubt, class `regenerate`.
- **Editing anything under `benchmarks/cec_reference_results/`.** These are READ-ONLY, SHA-256-auditable reference CSVs. Phase 0 reads and hashes them; it never writes them. A comparator's evidence lives here by design.
- **Assuming the reference panel is partial or `dt-gsk`-only.** It is not: the flat, full 7-optimizer panel exists under `benchmarks/cec_reference_results/` for cec2017, cec2011, and cec2013. Every claim traces to a reference cell first; `_run_all` reproductions are fallback evidence, not the source of truth — audit the committed panel instead of planning to regenerate it.
- **Fabricating tables `T17–T20`.** They are absent from `papers/tables/`. Record the gap; do not invent them or renumber the survivors.
- **Pooling runs across FP regimes.** A CEC2017 run whose `environment.json` sentinel does not begin `8bda40d8` was produced under a different floating-point regime and must not be mixed with the canonical set.
- **Inventing key names / paths / script names.** If a `run_config.json` field is named differently than assumed, use the real name. Only the scripts and paths enumerated in Inputs/Tasks exist — do not reference a runner or CLI that is not listed.
- **Citing outside the 57 keys.** The citation universe is frozen in `_bibkeys.txt`; the paper's cite-set must be a subset. Do not add references in Phase 0.
- **Treating authored figures as data-backed.** `figures/{diagrams,flowchart,taxonomy}` have no result CSV; never tag them `regenerate` for data-staleness reasons.
- **Auditing on a dirty tree.** Uncommitted changes under `results/`, `benchmarks/`, or `optimizers/` void provenance; reconcile first (Prerequisites).

---

## Exit gate

Do not proceed to Phase 1 until **all** boxes are checked and the named evidence exists:

- [ ] **Every table** in `papers/tables/` has an identified backing source that is confirmed present **and current**, or a filed regeneration ticket. — evidence: `asset_map.md` (table rows with `source_exists`/`source_current`/`class`).
- [ ] **Every figure** in `papers/figures/` has an identified generator + source (or is marked authored/no-data), source confirmed present or ticketed. — evidence: `asset_map.md` (figure rows).
- [ ] **The `\input` spine** matches the declared order and every referenced section/table exists. — evidence: `asset_map.md` (spine section).
- [ ] **Data ledger complete:** one row per (optimizer × suite × dim) across the 7-panel, every gap marked `missing`/`count_mismatch`/`stale` with a `regenerate`/`rescope` decision. — evidence: `data_ledger.csv`.
- [ ] **Run-count conventions verified** where cells are present (CEC2017 = 51, F2 excluded; CEC2011 = 25; CEC2013 = 51, D ∈ {10,30,50}). — evidence: `data_ledger.csv` `status` column.
- [ ] **FP-regime sentinel confirmed** on every CEC2017 `environment.json` (canonical `8bda40d8…`). — evidence: readiness note (sentinel table).
- [ ] **Profile lock passes** (`validate_profile_lock.py --root .` exit 0). — evidence: readiness note (command + exit code).
- [ ] **Anchor commit recorded** for all "reproducible from" claims. — evidence: readiness note (`anchor_commit=<sha>`).
- [ ] **Green gates recorded** (`pytest -q`, `ruff check .`, `build_docs_html.py` pass/fail). — evidence: readiness note.
- [ ] **Bib frozen & parses:** 57 keys dumped to `_bibkeys.txt`, `papers/references.bib` mirrors `reference_papers/references.bib`, entry count = 57. — evidence: `_bibkeys.txt` + readiness note (diff result).

Write the three artifacts under `papers/build_prompt_phases/`:
- `asset_map.md`
- `data_ledger.csv`
- `PHASE_0_readiness.md` (the evidence-readiness note: sentinel table, profile-lock result, anchor SHA, green-gate results, bib diff)

---

## Hand-off

Phase 0 passes the following to **`papers/build_prompt_phases/PHASE_1_scope.md`**:

1. `asset_map.md` — the keep/rewrite/regenerate classification of every `papers/` asset and its resolved (or ticketed) evidence source.
2. `data_ledger.csv` — the authoritative (optimizer × suite × dim) coverage matrix with per-gap `regenerate`/`rescope` decisions and per-gap regeneration tickets (naming `scripts/run_all_*.py` / `run_gsk_family.py`).
3. `PHASE_0_readiness.md` — FP-regime sentinel confirmation, `validate_profile_lock.py` result, the **anchor commit SHA**, green-gate results, and the bib-mirror diff.
4. `_bibkeys.txt` — the frozen 57-key citation universe that Phase 1's scope must stay within.

Phase 1 consumes these to define what the paper *can* honestly claim (scope = the union of `present` ledger cells plus cells with an approved regeneration ticket), and inherits the anchor SHA + FP sentinel as the provenance baseline for every downstream number.
