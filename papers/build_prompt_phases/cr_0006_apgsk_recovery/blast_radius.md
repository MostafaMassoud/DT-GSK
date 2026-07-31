# CR-0006 apgsk per-run recovery — Stage 1 blast-radius report

**Change request:** CR-0006 (apgsk CEC2017 per-run recovery, A2-004 fix)
**Date:** 2026-07-11
**Release under recompute:** `rel-2026-07-10-262fc16c9` (anchor `262fc16c9…`)
**Recompute git HEAD:** `35d3ced368baf21597af8d2719bd488d9643ee2b`
  (parent `4acb13378` = committed apgsk per-run recovery; frozen bundle was
  generated at `17fdefe3e1a823d90ca9f246b57fe5112e866d94`)
**Pre-recompute snapshot:** `…/scratchpad/cr0006_snapshot/bundle_before` (115 files)
  and `…/paper_tables_before` (17 files), per-file SHA-256 recorded.

---

## 0. TL;DR verdict

- **Recompute is CLEAN** (exit 0, no traceback; precheck, negative tests, and
  cross-implementation verification all PASS).
- **Blast radius is confined to apgsk run-level cells at CEC2017 D10/D30/D50 and
  their direct derivatives**, plus unavoidable run-provenance re-stamping.
- **Every `friedman_ranks_*`, `descriptive_stats_*`, `wilcoxon_holm_*`
  (function-level), `cross_check.json`, robustness r01/r03/r04/r07/r08, all
  CEC2013/CEC2011 run-level files, and all 17 `results/paper_tables/T*.csv`
  staging exports are BYTE-IDENTICAL.** Asserted positively below.
- **No unexplained change.** One item is FLAGGED for reconciliation (a manual
  "Gate 6" annotation on the r05 digest that the driver does not regenerate —
  pre-existing frozen-vs-driver divergence, not a CR-0006 data effect).
- **Main-text impact:** exactly one main-text *table* (the CEC2017 runtime/cost
  table, `sections/performance.tex` `tab:runtime`) has apgsk D10/D30/D50 "d.u."
  cells that become real; the run-level **effect-size** d.u.→real changes are
  **supplement-only**. No manuscript file was touched in this stage.

---

## 1. Manifest update (`papers/governance/evidence_release_manifest.json`)

Recomputed against the live restored file (independently verified equal):

| Field | Old | New |
|---|---|---|
| `cec2017/apgsk/per_run.csv` `size_bytes` | 151765 | **594925** |
| `cec2017/apgsk/per_run.csv` `sha256` | `d43f32f66b5f…9ccea8` | **`ac3419fe4c2f…7985f1`** |
| `totals.bytes` | 712038425 | **712481585** |
| `suites.cec2017.bytes` | 465736827 | **466179987** |
| `suites.cec2017.optimizers.apgsk.bytes` | 107773623 | **108216783** |
| `totals.file_class_counts.per_run` | 21 | 21 (unchanged — count, not bytes) |

- Byte delta = **+443160** applied to the file entry and to all three ancestor
  byte rollups (grand total → cec2017 suite → apgsk optimizer) for internal
  consistency. The manifest carries **no separate per-run byte-class total**; the
  per_run *count* (21 files) is unchanged.
- Added dated **`creation_record.cr_0006_recovery_note`** (recovery of A2-004,
  old/new hash+size, validation basis, out-of-scope siblings, +443160 rollups).
- Original `known_defect_note` left intact (append-only governance; still the
  accurate Phase-2 disposition for the still-D100-only siblings).
- JSON re-validated (`json.load` OK); no other entry touched.

## 2. Driver change (`papers/scripts/phase6_run_analysis.py`) — ruff-clean

The former **static** apgsk skip list `APGSK_GAP_DIMS = (10,30,50)` was a
hard-coded disclosed-unavailable list. Change (diff +40 / −15, `ruff` clean,
`py_compile` OK):

1. **New dynamic predicate** `per_run_absent(suite, alg, dim)` — returns True iff
   the release carries no per-run endpoint rows for that cell (cec2011 native-dim
   aware). Uses the cached, audited `load_per_run`; adds **no new source opens**.
2. **Five run-level skip sites** now call `per_run_absent(...)` instead of the
   static `suite=="cec2017" and alg=="apgsk" and dim in APGSK_GAP_DIMS`:
   success-rate (AN-DESC), AN-PW fallback effect size, AN-PWRUN, AN-EFF, AN-COST.
   For apgsk D10/D30/D50 the data now exists → cells are **computed**; genuinely
   absent cells would still fall through to the disclosed-unavailable path.
3. **r04 disputed-cell-exclusion kept as a FIXED tuple** (renamed
   `APGSK_DISPUTED_DIMS`). r04 is a pre-registered (plan R3) summary-means
   robustness variant, not a data-presence gate; keeping it fixed holds
   `AN-ROB-2017-04` byte-identical (confirmed §5).
4. **Precheck** `expected_rows["cec2017"]` 1479→5916 for apgsk (else the
   completeness gate would fail on the restored 5916 rows).
5. **Two stale disclosure notes** refreshed to CR-0006 state: the
   `apgsk_cec2017_disposition` (source_precheck.json) and the run_manifest
   `conventions[10]` string.

## 3. Recompute

`PYTHONIOENCODING=utf-8 python papers/scripts/phase6_run_analysis.py` → **exit 0**.
`output files: 129 · statistical rows: 5074 (was 4987) · audited opens: 1239 ·
negative tests: 3×PASS · grid mismatches: none · notes: none`. Full log in
`…/scratchpad/cr0006_snapshot/run_log_cr0006.txt`.
(First foreground attempt was killed by the 2-min tool timeout mid-run — the
recompute is deterministic and timing-independent; the background re-run
completed cleanly. A concurrent, unrelated `gsk_family.cli.run` ablation
benchmark by another session was left untouched.)

---

## 4. File-level blast radius

| Scope | Changed | Added | Removed |
|---|---|---|---|
| Analysis bundle (`papers/analysis/rel-2026-07-10-262fc16c9/`, 115 files) | **31** | 0 | 0 |
| Staging (`results/paper_tables/`, 17 files) | **0** | 0 | 0 |

`results/paper_tables/T1–T16.csv + provenance.json` are **entirely unchanged** —
they are exported from summary/function-level bundle sources only (even T15's
A12 is the means-based across-function A12, not the run-level A12).

---

## 5. The 31 changed bundle files — rows/cells changed, classified

### 5a. apgsk run-level PRIMARY (task-scoped, disclosed-unavailable → real)

Each CSV: **29 apgsk rows** (comparator=`apgsk`, F1,F3–F30) flip `n/a` /
`disclosed-unavailable` → measured; **0 non-apgsk rows differ** (verified).

| File | apgsk rows |
|---|---|
| `cec2017/wilcoxon_run_cec2017_D{10,30,50}.csv` | 29 each |
| `cec2017/effect_sizes_cec2017_D{10,30,50}.csv` | 29 each |
| `cec2017/bca_ci_cec2017_D{10,30,50}.csv` | 29 each |
| `cec2017/headline_bca.csv` | 87 (D10/30/50; D100 already real) |

Example (`wilcoxon_run_D30`, F1 apgsk): `…,n/a,…,disclosed-unavailable` →
`…,51,0.000000e+00,8.075024e-08,1.049753e-06,win,ok`.

### 5b. apgsk run-level DERIVED (apgsk-attributable; expected)

| File | What changed | Conclusion |
|---|---|---|
| `cec2017/cost_cec2017.csv` | 3 apgsk rows (D10/30/50 runtime): d.u.→real, e.g. D10 `1479, 3.974454e+00, 1.765920e+00` | feeds **main-text** runtime table |
| `cec2017/wilcoxon_run_cec2017_D{10,30,50}_exploratory_bh.csv` | 29 apgsk rows each, d.u.→real | supplement (AN-EXP-BH, RQ8) |
| `cec2017/robustness/…_r05_unpaired_companion.csv` | +87 apgsk rows (609→696) | verdict **agree** (unchanged) |
| `cec2017/robustness/…_r05_unpaired_companion_digest.md` | weakenings 8→11; **0 sign reversals**; verdict **agree** — plus a FLAGGED manual-note loss (§5e) | see §5e |
| `cec2017/robustness/…_r06_holm_vs_bh.csv` | 3 apgsk rows (D10/30/50): d.u.→real counts | r06 digest **byte-identical** (anomaly total unchanged) |
| `cec2017/robustness/…_r02_floor_sensitivity.csv` + `_digest.md` | scan denominator `0/66963`→`0/71400` (**+4437 = 3×1479** apgsk endpoints now scanned); sub-floor count **0**, **branch B** — both unchanged | apgsk-attributable; conclusion unchanged |

Every apgsk r05 transition is `ns_to_sig`/`sig_to_ns` — **never** a win↔loss
reversal — so the pre-registered R5 verdict rule (agree iff 0 sign reversals)
holds. `robustness_summary_cec2017.md` is **byte-identical**.

### 5c. `primary_stats/statistical_results.csv` (task-scoped)

- Rows 4987 → **5074**: **+87 rows added, all apgsk, all `AN-EXP-BH-2017`**
  (the exploratory-BH family emits stat rows only for available cells). 0 removed.
- **745 apgsk rows changed** in data columns (test stats, p-values, A12/Cliff,
  BCa, n_obs, `source_paths`, `source_checksums` (apgsk per_run
  `…d43f32f6`→`…ac3419fe`), interpretation, status).
- **4242 non-apgsk rows differ in EXACTLY ONE column: `commit_sha`** (0 differ in
  any data column — column-level verified). See §5d.

### 5d. Run-provenance re-stamp (metadata; every-run, not a data change)

git HEAD legitimately advanced (recovery committed as `4acb13378`, then
`35d3ced36`); the driver stamps the current HEAD/time.

| File(s) | Only-change |
|---|---|
| `primary_stats/statistical_results.csv` | `commit_sha` `17fdefe3…`→`35d3ced3…` (all 5074 rows) |
| `run_manifest.json` ×4 (top+cec2017/2013/2011) | `git_head_at_run` + CR-0006 `conventions[10]` note |
| `environment_record.json` | `git_head_at_run` only |
| `source_use_log.json` ×3 | `started_utc`/`finished_utc` only — **`opened` file-list identical**, non-timestamp body identical (⇒ no new source opens) |
| `analysis_manifest.json` | `git_head_at_run` + 29 changed-output SHAs (0 added/removed; **all 29 in the expected set**) |
| `analysis_checksums.sha256` | the 29 changed-output hash lines |
| `source_precheck.json` | apgsk per_run `rows`/`expected` 1479→5916 + CR-0006 disposition note (summary_csv_check & negative_tests unchanged) |

### 5e. FLAGGED — r05 digest manual-annotation loss (not a data effect)

The **frozen** `r05_unpaired_companion_digest.md` carried a post-Phase-6 manual
paragraph *"Completeness note (Gate 6): … 18 new significances … 8 emergent
losses … verdict-irrelevant …"*. This text is **not in the driver source**
(`grep` confirms), and my CR-0006 edits do **not** touch the r05 region. A clean
re-run regenerates the driver's canonical digest (9→7 lines) and therefore drops
that paragraph. **This is a pre-existing frozen-vs-driver divergence surfaced by
the recompute, independent of CR-0006.** Decision for a later stage: re-append
the Gate-6 note (with counts updated to the new 11 weakenings / recomputed
emergent losses) or accept the canonical driver output.

---

## 6. Positive byte-identity assertion (must-be-identical set)

Confirmed byte-identical (SHA-256 equal, snapshot vs recompute):

- **All `friedman_ranks_*`** (cec2017 D10/D30/D50/D100 + overall; cec2013 overall;
  cec2011) → primary Friedman ranks UNAFFECTED.
- **All `descriptive_stats_*`** (cec2017/cec2013/cec2011) → summary transcription
  UNAFFECTED.
- **All `wilcoxon_holm_*` (function-level)** (cec2017 D10/30/50/100; cec2013;
  cec2011) → function-level Wilcoxon/Holm UNAFFECTED.
- `nemenyi_cd_*`, `rank_trend_cec2017.csv`, `class_ranks_cec2017.csv`,
  `curve_selection_*`, all `convergence_checkpoints_*`, `README.md`,
  `table_to_csv_map.md`.
- **`cross_check.json`** (its probes use gsk/agsk/egsk, never apgsk).
- **Robustness r01, r03, r04, r07, r08** (CSVs + digests) — including the
  disputed-cell-exclusion r04.
- All **CEC2013 & CEC2011** run-level files (`wilcoxon_run_*`, `effect_sizes_*`,
  `bca_ci_*`) — non-apgsk suites untouched.
- All **17** `results/paper_tables/T*.csv` + `provenance.json`.

**All non-apgsk cells in changed files are byte-identical** (CSV data files: 0
non-apgsk differing rows; `primary_stats`: non-apgsk rows differ only in the
global `commit_sha` stamp; r02: only the apgsk-driven scan denominator; JSONs:
only provenance + the intended CR-0006 note edits).

---

## 7. Main-text vs supplement

- The apgsk **run-level effect-size / run-level Wilcoxon** d.u.→real changes
  (effect_sizes / bca_ci / wilcoxon_run D10/30/50) feed **supplement-only**
  full-per-dimension tables (T02-FULL, T03-FULL, T-BCA per-dim). The **main-text**
  effect-size exhibit (T15/T03) uses across-function A12 on per-function *means*
  (summary-based) and function-level Wilcoxon/Holm — **unaffected**. The main-text
  Friedman-rank BCa table is supplement-scoped and uses a different seed stream
  (`BASE_SEED=20260422`), not the phase6 paired-mean-diff BCa — **unaffected**.
- **One MAIN-TEXT table is affected:** the CEC2017 per-run runtime/cost table
  (`papers/sections/performance.tex`, `tab:runtime`, BIND `AN-COST-2017`) shows
  `\apgsk{} & d.u. & d.u. & d.u. & $47.11 \pm 14.43$`. Those three d.u. cells
  would become real (`cost_cec2017.csv` apgsk D10/30/50 = `3.97±1.77`,
  `12.xx±…`, `…`). Runtime is a run-level *cost* quantity, not an effect size.
- **Main-text PROSE** qualifications of the gap (`performance.tex` L114, 263, 315,
  743–744) become outdated and would need softening on rebuild.
- **This stage touched no `.tex`/`.docx`/`.pdf`** — the frozen manuscript is
  unchanged; the above is a hand-off list for the manuscript-rebuild stage.

---

## 8. Red-flag summary

- **Unexplained changes: NONE.** Every changed cell is either (a) an apgsk
  run-level cell at CEC2017 D10/D30/D50 (or its direct derivative), or (b) an
  apgsk-driven scan denominator (r02), or (c) run-provenance (commit_sha /
  git_head / timestamps / dependent hashes), or (d) an intended CR-0006 note edit.
- **1 item FLAGGED (§5e):** r05 digest loses a manual Gate-6 annotation the driver
  never generated — pre-existing frozen-vs-driver divergence, not a CR-0006 data
  change; needs an orchestrator decision.
- **Claims:** no claim upgraded — d.u. cells filled with their true measured
  values (completeness correction); disclosure wording left conservative.
