# Benchmark-tree source wiring for paper table inputs (X-PT-01)

**Purpose.** Make the paper depend on the immutable benchmark tree, not on the
mutable `results/` staging area. The authoritative table-input CSVs (T1–T16 +
`provenance.json`) have been promoted, byte-identically and read-only, into:

```
benchmarks/cec_reference_results/_paper_tables/rel-2026-07-10-262fc16c9/
    T1.csv … T16.csv          (16 files)
    provenance.json           (per-table bundle-source chain)
    paper_tables_manifest.json (promotion manifest, SHA-256 per file + release chain)
```

This note documents the **mapping** from the staging path each generator reads
today to the promoted benchmark path. It is a **documentation-only** wiring
record: generator code is **not** rewired in this stage (the redirect is a
one-line constant change per generator, deferred so it can be reviewed and
re-frozen as its own controlled step). The promoted subtree is a byte-identical
mirror of `results/paper_tables/`, so either path yields identical exhibits.

## Path mapping

| From (staging, current) | To (promoted benchmark tree, authoritative) |
|---|---|
| `results/paper_tables/T{1..16}.csv` | `benchmarks/cec_reference_results/_paper_tables/rel-2026-07-10-262fc16c9/T{1..16}.csv` |
| `results/paper_tables/provenance.json` | `benchmarks/cec_reference_results/_paper_tables/rel-2026-07-10-262fc16c9/provenance.json` |

## Generators that read the table inputs (consumers) and the constant to redirect

Every consumer localises the staging root in a single module-level constant.
Redirecting the paper to the benchmark tree is a one-line edit per file (repoint
the constant at the promoted subtree); no reader logic changes.

| Generator | Reads | Constant to repoint | Output |
|---|---|---|---|
| `papers/scripts/generate_latex_tables.py` | T1–T16 | `RESULTS_DIR` (L21) | `papers/tables/T01–T16.tex` (primary LaTeX tables) |
| `papers/scripts/generate_word_sources.py` | T1–T16 + `provenance.json` | `STAGING` (L42) | `papers/tables/word_sources/*.json` |
| `papers/scripts/generate_artifact_binding.py` | `provenance.json`, T*.csv staging paths, T16.csv | inline `ROOT / "results/paper_tables/…"` (L116, L200, L371) | `papers/governance/artifact_binding.csv` |
| `papers/scripts/generate_rank_charts.py` | T16.csv | `STAGING_DIR` (L38) | rank charts |
| `papers/scripts/generate_parametric_tables.py` | `_IN` dir (T21/T22 — disclosed-unavailable, EG-006; not exported) | `_IN` (L19) | parametric tables (gap-handled) |
| `papers/build_prompt_phases/phase_07/validate_exhibits.py` | staging dir (validation) | `STAGING` (L55) | exhibit validation report |

`papers/scripts/phase6_run_analysis.py` **writes** (does not read) the staging
CSVs — it is the export **producer** (`export_paper_tables()`, "task 23"). It
stays pointed at `results/paper_tables/` as the export target; the promotion is a
downstream immutable copy of that export, so the producer is unchanged.

## Provenance chain (why the benchmark path is authoritative)

```
frozen analysis bundle                results/paper_tables/            promoted benchmark subtree
papers/analysis/rel-2026-07-10-       (phase6 export, Phase 6 task 23)  benchmarks/cec_reference_results/
262fc16c9/  (immutable release)  ───►  T1–16.csv + provenance.json  ──►  _paper_tables/rel-2026-07-10-262fc16c9/
  descriptive_stats_* /                (staging; mutable)               (read-only, SHA-256 manifest,
  friedman_ranks_* /                                                     per-table bundle-source chain)
  wilcoxon_holm_*  (function-level)
```

`paper_tables_manifest.json` records, per table, the bundle source file(s) and
their SHA-256 (`table_provenance_chain`), plus the bundle's own
`analysis_checksums.sha256` as the release-level integrity anchor — so every
promoted table traces back to the immutable release. All 33 bundle-source hashes
recorded in `provenance.json` were re-verified against the current on-disk bundle
at promotion time (0 mismatches).

## CR-0006 currency

The promoted T1–T16 are the **current post-CR-0006** versions; **no re-export was
required**. CR-0006 (A2-004 apgsk CEC2017 D10/D30/D50 per-run recovery, decision
D-0011) changed only apgsk **run-level** bundle files (`wilcoxon_run`,
`effect_sizes`, `bca_ci`, `cost`, `headline_bca`, exploratory-BH, robustness
r02/r05/r06). None of T1–T16's sources are run-level — they read
`descriptive_stats_*`, function-level `wilcoxon_holm_*`, and `friedman_ranks_*`
only, all byte-identical across CR-0006. CR-0006 Stage 2 explicitly records
`results/paper_tables/T*.csv + provenance.json: unchanged (no re-export needed)`;
`git status` on `results/paper_tables/` is clean.
