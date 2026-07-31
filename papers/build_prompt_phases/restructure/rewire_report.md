# Stage 2 rewire report — paper-building consumers → benchmark evidence

Repoint every PAPER-BUILDING generator to read its inputs from the promoted,
frozen benchmark evidence (`benchmarks/cec_reference_results/`) instead of the
volatile `results/` staging that producers write. Data is byte-identical
(Stage 1 moved/renamed only); only source **paths** change.

Repo root / cwd: `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1`

## Concurrency note (important)

During this task, `HEAD` advanced from `9b2224119` to
`6917e21d7 "scripts: repoint artifact-binding + ablation-matrix to benchmarks/"`.
That commit had **already repointed 2 of the 8 consumers**
(`generate_artifact_binding.py`, `generate_ablation_matrix.py`). I reconciled:
I reverted a now-redundant edit I had started on `generate_artifact_binding.py`
(HEAD's version is correct) and did **not** re-do `generate_ablation_matrix.py`.
I made no commits (not requested); the 6 remaining consumers are edited in the
working tree. The concurrent agent also **refactored `generate_latex_tables.py`
in place** while I worked (removing its scaffold-ablation-table block); my
`RESULTS_DIR` benchmark repoint is preserved on top and the file re-verifies
clean. Because both of us touch the same working-tree files, the final committed
state depends on that agent; the verified state below is as of this session's
last check.

## Files rewired (old → new per file)

Base path abbreviations: `RES = results/paper_tables`,
`BENCH = benchmarks/cec_reference_results/_paper_tables`.

### 1. papers/scripts/generate_latex_tables.py  — EDITED (this session) + refactored by the concurrent agent
- `RESULTS_DIR` constant (my repoint, intact): `PROJECT_ROOT/"results"/"paper_tables"` → `PROJECT_ROOT/"benchmarks"/"cec_reference_results"/"_paper_tables"`
- not-found `FileNotFoundError` message: `RES/` → `BENCH/` (+ mentions promote step)
- module docstring: `RES/` → `BENCH/`
- SUPERSEDED: I had left the `results/ablation/` scaffold-ablation-table scan in place (it reads `generate_ablation_matrix.py`'s output, not a paper_tables input, and Phase 7 ran it with `--skip-ablation`). While I worked, the concurrent agent **removed that whole block** (the `--skip-ablation` flag, the `results/ablation/` scan, `gen_ablation_table`, `_ABLATION_LABELS`), delegating SA01/SA02 entirely to `generate_ablation_exhibits.py`. The file now has **no `results/` reference at all**; my benchmark repoint sits on top of that refactor. Re-verified: compiles, ruff-clean, no orphaned refs, T*.tex byte-identical.

### 2. papers/scripts/generate_word_sources.py  — EDITED (this session)
- `STAGING` constant: `RES` → `BENCH`
- docstring "Admissible inputs" block: `RES/T{1..16}.csv` / provenance → `BENCH/…`
- `RELEASE_NOTE` provenance pointer: `RES/provenance.json` → `BENCH/provenance.json`
- `BUNDLE` (`papers/analysis/…`) for T16_bca: UNCHANGED (bundle input, authoritative)

### 3. papers/scripts/generate_rank_charts.py  — EDITED (this session)
- `STAGING_DIR` constant: `RES` → `BENCH` (feeds only the legacy `friedman_gsk_family` bar from `T16.csv`)
- docstring + `_require` hard-fail message: `RES/T16.csv` / `RES/` → `BENCH/…`
- `BUNDLE_DIR` (`papers/analysis/…`) for the other 3 charts: UNCHANGED (bundle input)

### 4. papers/scripts/generate_parametric_tables.py  — EDITED (this session)
- `_IN` constant: `_REPO/"results"/"paper_tables"` → `_REPO/"benchmarks"/"cec_reference_results"/"_paper_tables"`
- Note: T21/T22 CSVs exist in neither staging nor benchmark, so this script is **not generated** (raises `FileNotFoundError` on `BENCH/T21.csv`, identical behaviour to before). Repointed for consistency only.

### 5. papers/scripts/generate_artifact_binding.py  — ALREADY DONE in HEAD (commit 6917e21d7)
- `provenance_sources()`: `ROOT/"results/paper_tables/provenance.json"` → `ROOT/REF/"_paper_tables"/"provenance.json"`
- table_spec loop `staging`: `f"results/paper_tables/{csv_name}"` → `f"{REF}/_paper_tables/{csv_name}"`
- legacy friedman `srcs`: `["results/paper_tables/T16.csv"]` → `[f"{REF}/_paper_tables/T16.csv"]`
- (`REF = "benchmarks/cec_reference_results"` already existed.) I reverted my redundant `PAPER_TABLES` constant; left HEAD's version untouched.

### 6. papers/scripts/generate_ablation_matrix.py  — ALREADY DONE in HEAD (commit 6917e21d7)
- `--ablation-root` default: `"results/_ablation"` → `"benchmarks/cec_reference_results/_ablation/scaffold"`
- help text + usage docstring updated; overlay cells documented as living under `.../_ablation/overlay`
- output default (`results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv`): UNCHANGED (producer-written output, correctly not repointed)

### 7. papers/scripts/generate_ablation_exhibits.py  — EDITED (output-neutral, this session)
- **No functional read-path change** — and this is correct. This script reads the release-bound rank matrices from `papers/build_prompt_phases/phase_12/ablation_results/` (each verified against a manifest SHA-256), which is **not** `results/` staging and was not moved by Stage 1. The scaffold benchmark tree contains no `*rank_summary*` matrices (confirmed), so it cannot and must not read from `benchmarks/_ablation`.
- Added an **output-neutral clarifying comment** above `_ABL_DIR` documenting that the promoted evidence these matrices aggregate (logical release id `abl-rel-2026-07-11`) now physically resides at `benchmarks/cec_reference_results/_ablation/scaffold` after the Stage-1 restructure, and that `generate_ablation_matrix.py` reads that benchmark tree.
- The `abl-rel-2026-07-11` strings that flow into SA01/SA02.tex (`_PROV`) and the word_sources JSON (`notes`) were left **verbatim**: they mirror `ablation_results_manifest.json`'s `immutable_release.root` (JSON data I must not alter, and which this script re-emits into its output manifest). Changing them would alter committed SA01/SA02 exhibits and diverge from that manifest. Verified: SA01.tex, SA02.tex, SA01.json, SA02.json, the figure, and `ablation_exhibits_manifest.json` all regenerate **byte-identical**.

### 8. papers/build_prompt_phases/phase_07/validate_exhibits.py  — EDITED (this session)
- `STAGING` constant: `RES` → `BENCH`
- docstring + in-report "Authoritative sources" prose: `RES/` → `BENCH/`
- `BUNDLE` and `REFERENCE_ROOT` (`benchmarks/cec_reference_results/…` gen_logs): UNCHANGED

## Producers left alone (NOT rewired) — confirmed untouched

All clean in the working tree (absent from `git status`), still pointing at `results/` staging:
- `papers/scripts/phase6_run_analysis.py`
- `scripts/promote_evidence.py`
- `scripts/run_ablation.py`
- `papers/scripts/generate_review_pack.py`

## Verification (mandatory byte-identity) — ALL PASS

| Regenerated exhibit | Method | Result |
|---|---|---|
| `papers/tables/T01–T16.tex` | `generate_latex_tables.py` (no args; reads BENCH) | `git diff` **empty** — byte-identical |
| Rank charts `papers/figures/ranks/*.{pdf,png}` | `generate_rank_charts.py` (reads BENCH T16.csv + bundle) | `git diff` **empty** — byte-identical |
| Ablation matrices `…D{10,30,50,100}.csv` | `generate_ablation_matrix.py` (NEW default root, no arg) → scratchpad | **byte-identical** to committed `phase_12/ablation_results/…` (all 4 dims) |
| SA01/SA02 `.tex`+`.json`, figure, manifest | `generate_ablation_exhibits.py` | `git diff` **empty** — byte-identical |

Determinism was pre-checked from the unedited code first (T*.tex and rank
charts both regenerate byte-identically), so the post-edit empty diffs isolate
the path change as the only variable. Staging vs benchmark `_paper_tables`
CSVs + `provenance.json` were confirmed byte-identical up front.

Corroborating (value/checksum-preserving, path-only changes; committed outputs
restored so the tree carries only script edits):
- `generate_word_sources.py`: runs from BENCH; only `source_csv` + `RELEASE_NOTE` paths change (`RES`→`BENCH`); `source_sha256` unchanged.
- `generate_artifact_binding.py` (HEAD): runs from BENCH (55 rows); regenerated `source_paths` carry `BENCH` (0 `results/paper_tables`); `source_checksums` preserved (data byte-identical). Committed CSV still shows staging paths and will update on next regeneration.

## Finding surfaced (PRE-EXISTING, NOT caused by this rewire)

`validate_exhibits.py` now reports `FAIL — 1 mismatch` while the committed
`exhibit_validation_report.md` says `PASS — 0 mismatches`. Isolated and proven
**path-independent**: pointing `STAGING` back at `results/paper_tables` gives the
**identical** mismatch. It is a generator/validator label drift on the T14
`p_holm` **row label** (values match): `generate_latex_tables.py` renders
`p_holm` → `$p_{\text{Holm}}$` in `T14.tex`, but the validator's replicated
`_fmt_t14_metric` lacks that rule and expects raw `p_holm`. The committed report
is stale relative to the current committed `T14.tex`. Out of scope for the
repoint; committed report left as-is. Flagging for a separate fix.

## ruff

`ruff check` — **All checks passed** on all 8 consumers (the 6 edited this
session + the 2 repointed in HEAD).
