# Restructure Stage 3 — Byte-Identical Rebuild + No-Results-Dependency Verification

**Date:** 2026-07-12
**HEAD at verification:** `dfcacda07` (Stage 1 relocation + Stage 2 rewire committed by the
orchestrator; HEAD advanced during this run — see note 6).
**Verdict:** **PASS** — every mandated exhibit (T01–T16, rank charts, ablation matrix) is
byte-identical to the committed version, no consumer has an active `results/` staging input
dependency, both manifests re-verify with 0 mismatches, and the primary optimizer tree is
untouched. Three non-blocking findings (§7), all **pre-existing** and outside the mandated exhibit
set, are disclosed below (they do not affect any pass criterion).

---

## 1. Snapshot of committed exhibits

Working tree == HEAD for `papers/tables/` and `papers/figures/ranks/` (empty `git diff`), so the
committed exhibits were snapshotted directly (sha256) to the scratchpad before rebuilding:

- `papers/tables/*.tex` — 21 files (T01–T16, T21, T22, T16_bca, SA01, SA02)
- `papers/figures/ranks/*.png` — 8 PNGs (4 script-generated + 4 `.docx.png` companions)
- Ablation-matrix reference: `papers/build_prompt_phases/phase_12/ablation_results/ablation_matrix_rank_summary_cec2017_D30.csv`
  (`sha256 20b280eb…3bb9e0`)

## 2. Rebuild from the NEW benchmark sources — byte-identical result

Commands (`PYTHONIOENCODING=utf-8`):

```
python papers/scripts/generate_latex_tables.py            # see note 5 (no --skip-ablation flag)
python papers/scripts/generate_rank_charts.py
python papers/scripts/generate_ablation_matrix.py \
    --ablation-root benchmarks/cec_reference_results/_ablation/scaffold --full-cell baseline
```

Byte comparison (`cmp`) of every regenerated exhibit vs the snapshot / committed reference:

| Exhibit family | Files | Result |
|---|---|---|
| LaTeX tables T01–T16 (`generate_latex_tables.py`, reads `_paper_tables/`) | 16 | **16/16 IDENTICAL** |
| Rank PNGs `rank_vs_dim_cec2017`, `cec2017_mean_ranks`, `cec2011_ranks`, `friedman_gsk_family` | 4 | **4/4 IDENTICAL** |
| Ablation matrix `…_cec2017_D30.csv` (scaffold, full-cell=baseline) | 1 | **1/1 IDENTICAL** |
| **Total** | **21** | **21/21 byte-identical, 0 diffs** |

Cross-check: after regeneration, `git diff HEAD -- papers/tables papers/figures/ranks` is **empty**
— confirming the regenerated `.tex`, `.png` **and `.pdf`** all match committed bytes (rank charts
suppress the PDF `CreationDate`, so PDFs are deterministic too).

The ablation-matrix rebuild reproduced the committed D30 cell ranks exactly (7 cells, 29 funcs,
full='baseline' rank 3.207, Friedman p=5.46e-08). Its default output landed in `results/ablation/`
(an OUTPUT path, not a consumed input); it was compared byte-for-byte to the committed
`phase_12/ablation_results/` copy and then removed (verification-only artifact).

**Extended (non-mandated) consumer exercise.** For completeness the other rewired consumers were
also run (then the tree restored). `generate_ablation_exhibits.py` reproduced **SA01/SA02
byte-identical**. `generate_word_sources.py` and `generate_parametric_tables.py` surfaced
**pre-existing** issues — see Findings (§7) — that are outside the mandated exhibit set and are not
caused by the rewire.

## 3. No-results-dependency scan (8 consumers + phase_07 validator)

`grep -E "results/paper_tables|results/_ablation|results/_run_all"` over all eight consumers plus
`validate_exhibits.py`: **every hit is a comment, docstring, provenance note, or explicit negation
— none is an active `open()`/`Path()` data-load line.** The active input roots are, in every case,
the promoted benchmark evidence or the frozen analysis bundle:

| Consumer | Active input root |
|---|---|
| `generate_latex_tables.py` | `RESULTS_DIR = benchmarks/cec_reference_results/_paper_tables` (var name is legacy) |
| `generate_word_sources.py` | `STAGING = …/_paper_tables`, `BUNDLE = papers/analysis/rel-2026-07-10-262fc16c9` |
| `generate_rank_charts.py` | `STAGING_DIR = …/_paper_tables/T16.csv` + frozen bundle |
| `generate_parametric_tables.py` | `_IN = …/_paper_tables` |
| `generate_artifact_binding.py` | `REF = benchmarks/cec_reference_results`, `BUNDLE = papers/analysis/…` (zero `results/` refs) |
| `generate_ablation_matrix.py` | `--ablation-root` default `…/_ablation/scaffold`; writes OUTPUT to `results/ablation/` (allowed; note: no underscore, ≠ `results/_ablation`) |
| `generate_ablation_exhibits.py` | `papers/build_prompt_phases/phase_12/ablation_results/`, manifest-verified vs `…/_ablation/` |
| `phase_07/validate_exhibits.py` | `benchmarks/cec_reference_results/_paper_tables/` + bundle |

The `results/_ablation` grep hits inside `generate_ablation_matrix.py` / `generate_ablation_exhibits.py`
are false positives: they are the `cec_reference_results/_ablation` **benchmarks** substring.
`validate_exhibits.py` (just re-touched by `dfcacda07`, a T14 p_holm label fix) still asserts, as a
report string, *"No `results/_run_all`, no `results/_ablation`"* — no dependency introduced.

**Producers correctly still reference `results/` staging (NOT rewired, out of scope):**
`papers/scripts/phase6_run_analysis.py`, `scripts/promote_evidence.py`, `scripts/run_ablation.py`,
`papers/scripts/generate_review_pack.py`.

## 4. Manifest re-verification + primary tree untouched

Recomputed sha256 from disk for every entry in both manifests:

| Manifest | Entries | Matched | Mismatch | Missing | Σ bytes (manifest == disk) |
|---|---|---|---|---|---|
| `_ablation/manifest.json` | 1032 | 1032 | **0** | **0** | 348,959,053 == 348,959,053 |
| `_paper_tables/manifest.json` | 17 | 17 | **0** | **0** | 64,496 == 64,496 |

Disk reconciles: `_ablation` holds 1034 files = 1032 catalog + `manifest.json` + `README.md`;
`_paper_tables` holds 19 = 17 + manifest + README. (The "108 files" cited in prior stage reports is
the summary-level `groups` subset; the manifest's full `files` catalog is 1032, including
curves/gen_logs.)

**Primary optimizer tree untouched.** Across the whole restructure range `9b2224119..HEAD`
(commits `6917e21d7`, `a4f5324ad`, `8048f9b2e`, `dfcacda07`), classifying all 1195 changed
path-entries: `_ablation/` (1146), `_paper_tables/` (37), one top-level `BENCHMARK_EVIDENCE_INDEX.md`,
all **8 consumer scripts**, and 3 docs. **Zero** paths under any
`benchmarks/cec_reference_results/<suite>/<optimizer>/` primary tree were added, modified, deleted,
or renamed. Working tree carries no uncommitted primary-tree change.

## 5. Engineering

`python -m ruff check` on all 8 edited scripts → **"All checks passed!"** (exit 0).

## 6. Notes / deviations (honest disclosure)

1. **`--skip-ablation` flag does not exist.** `generate_latex_tables.py` takes no options; the
   scaffold-ablation supplement tables (SA01/SA02) are emitted by `generate_ablation_exhibits.py`,
   not this script — so running it plain is the exact equivalent of the intended "skip ablation".
   This is a task-command vs script-interface mismatch, not a rewire defect.
2. **All 8 consumers were repointed** (not 6). The two not covered by the Stage-2 rewire report
   (`generate_artifact_binding.py`, `generate_ablation_matrix.py`) were repointed in commit
   `6917e21d7`.
3. **HEAD advanced during verification** as the orchestrator/concurrent agents committed
   (`8048f9b2e` → `dfcacda07`) and edited unrelated manuscript prose (`papers/sections/performance.tex`).
   None of this touches the verified exhibits, manifests, or primary data.
4. The only residual working-tree churn is the pre-existing `results/_ablation_sgsm/*` producer
   staging (present at session start, unrelated to this restructure).

## 7. Findings (pre-existing; disclosed, non-blocking)

None of these is caused by the rewire, none is in the mandated exhibit set, and none violates a
pass criterion — but a reviewer running the full consumer suite should know:

1. **[MAJOR] `generate_parametric_tables.py` hard-fails (FileNotFoundError).** After being repointed
   to `benchmarks/cec_reference_results/_paper_tables`, it reads `T21.csv`/`T22.csv` — which are
   **absent from that directory and from the entire tree/history**. No tracked script writes them,
   and they were never committed. Pre-rewire it read `results/paper_tables` (also lacking them at
   `9b2224119`), so it was already non-functional; the rewire merely moved a missing target. The
   committed `T21.tex`/`T22.tex` are stale (Jun 29) legacy exhibits outside the Phase 6/7 build.
   *Fix:* either promote `T21.csv`/`T22.csv` into `_paper_tables`, or retire the legacy
   `generate_parametric_tables.py` / T21–T22 pipeline.

2. **[MINOR] Committed `papers/tables/word_sources/T{1..16}.json` carry the OLD provenance path.**
   They still record `"source_csv": "results/paper_tables/T*.csv"` and cite
   `results/paper_tables/provenance.json`. Regenerating with the rewired script updates only those
   strings to `benchmarks/cec_reference_results/_paper_tables/…`; **`source_sha256` is unchanged**
   (data byte-identical). The orchestrator committed the rewired scripts without regenerating these
   intermediates. *Fix:* regenerate `word_sources` in the Phase 9 Word build.

3. **[MINOR] Committed `word_sources/T16_bca.json` is stale vs the frozen bundle.** A fresh run
   changes apgsk CEC2017-D10 cells from `n/a / disclosed-unavailable` to `51 / 0.000000e+00 /
   "no CI (degenerate cell)"` — i.e. the committed JSON predates the CR-0006 apgsk data-loss
   recovery. `T16_bca` reads `papers/analysis/<release>/cec2017/headline_bca.csv` (the **unchanged
   bundle path**), so this staleness is unrelated to the `results/ → benchmarks/` rewire. *Fix:*
   regenerate T16_bca companion from the current bundle.

---

**Byte-identical after rewire: YES (mandated exhibits, 21/21). Zero results/ input dependency: YES.
Manifests verify: YES (0 mismatches). Primary tree untouched: YES.**
