# Paper tables (X-PT-01)

The authoritative, machine-readable **table-input CSVs** (`T1.csv` .. `T16.csv`)
that the paper's rendered LaTeX/Word tables are generated from, plus the
`provenance.json` that pins each table to its upstream analysis-bundle source.

```
_paper_tables/
  README.md       <- this file
  manifest.json   <- SHA-256 manifest over the 17 files below
  provenance.json <- per-table upstream bundle sources + source SHA-256
  T1.csv .. T16.csv
```

The tables sit **flat** under `_paper_tables/` (the release-id directory level was
removed in the Stage-1 restructure). The release id is a **logical identifier** in
`manifest.json` and `provenance.json`, not a directory level. On every finalization
run, `finalize_evidence.py` (phase P7) replaces the CSVs from the fresh Phase-6
export **and re-mints `manifest.json`** so the recorded hashes always match the
promoted bytes.

- **Release id:** `rel-2026-07-16-78f075cb0` (anchor commit `78f075cb0`) — the
  51-run post-fix export, superseding `rel-2026-07-10-262fc16c9` (recoverable via
  git history)
- **Study id:** `X-PT-01`
- **Totals:** see `manifest.json` `totals` (17 files; byte count changes per export)

---

## How to locate a file

Every `path` in `manifest.json` is **relative to this directory**
(`benchmarks/cec_reference_results/_paper_tables/`). A generator resolves a table
as `<_paper_tables>/T<n>.csv` -- e.g. `T4.csv`. There is no suite/dim
subdirectory: the suite and dimension are encoded per table (below), not in the
path.

## Table map

| Table | Suite / dim | Content |
|---|---|---|
| `T1.csv`  | CEC2011        | GSK / DT-GSK descriptive stats (best_fitness basis) |
| `T2.csv`  | CEC2017 D10    | GSK / DT-GSK descriptive stats |
| `T3.csv`  | CEC2017 D30    | GSK / DT-GSK descriptive stats |
| `T4.csv`  | CEC2017 D50    | GSK / DT-GSK descriptive stats |
| `T5.csv`  | CEC2017 D100   | GSK / DT-GSK descriptive stats |
| `T6.csv`  | CEC2011        | GSK Wilcoxon+Holm + R+/R- and W/T/L re-derived from means |
| `T7.csv`  | CEC2017 D10    | panel Mean/SD (P1 order) |
| `T8.csv`  | CEC2017 D30    | panel Mean/SD (P1 order) |
| `T9.csv`  | CEC2017 D50    | panel Mean/SD (P1 order) |
| `T10.csv` | CEC2017 D100   | panel Mean/SD (P1 order) |
| `T11.csv` | CEC2013 D10    | GSK / DT-GSK descriptive stats |
| `T12.csv` | CEC2013 D30    | GSK / DT-GSK descriptive stats |
| `T13.csv` | CEC2013 D50    | GSK / DT-GSK descriptive stats |
| `T14.csv` | CEC2013 D10/30/50 | GSK Wilcoxon+Holm + R+/R-/W-T-L re-derived from means |
| `T15.csv` | CEC2017 D10/30/50/100 | function-level Wilcoxon+Holm + W/T/L and across-function A12 |
| `T16.csv` | CEC2017        | Friedman ranks (per-dimension + overall) |

(T21/T22 parametric-sensitivity tables are intentionally NOT present: no
admissible sensitivity release exists, per EG-006.)

---

## Upstream trace

These CSVs were exported **exclusively** from the controlled analysis bundle
`papers/analysis/rel-2026-07-16-78f075cb0/` (the `phase6_run_analysis.py` export
step, Phase 6 task 23). `provenance.json` records, for every table, its bundle
source file(s) + each source's SHA-256; `manifest.json` carries the same in
`table_provenance_chain`, re-verified at promotion. The exports read only
descriptive-stats, function-level Wilcoxon-Holm, and Friedman-rank bundle files.

The upstream analysis bundle itself is not copied here; it is the derivation
source, and each table's dependence on it is pinned by recorded SHA-256.

---

## Manifest

`manifest.json` (schema `paper_tables_promotion_manifest/v2-flat`) is the single
source of truth for this folder: per-file `path` / `size_bytes` / `sha256`, the
`table_provenance_chain`, the source-bundle checksum anchors, and the CR-0006
currency note. It supersedes `paper_tables_manifest.json`. It lists the 17
evidence files (T1-T16 + provenance.json); it does not list itself or this README.
