# Stage-1 restructure — completeness check

**Scope.** Verifies that after the byte-identical restructure of
`benchmarks/cec_reference_results/_ablation/` and
`benchmarks/cec_reference_results/_paper_tables/`, **every datum the paper needs is
present** at its new path. Data was relocated with `git mv` (renames only, 0 content
changes); every SHA-256 in the two new `manifest.json` files was recomputed from the
on-disk relocated file and re-verified against the prior committed manifests
(0 mismatches).

**Verdict: COMPLETE — 0 failures. Nothing missing.**

---

## New structure

```
benchmarks/cec_reference_results/
  _ablation/
    README.md
    manifest.json                 # unified: 108 files, 3,011,471 bytes
    scaffold/                     # X-ABL-01 (CEC2017), 7 cells, 75 files, 2,608,778 bytes
      {baseline,no_ace,no_psr,no_bse,no_linkage,no_localsearch,no_arch}/dt-gsk/cec2017/summary/
      baseline/dt-gsk/cec2017/_d100_repair_provenance/
    overlay/                      # X-ABL-02 (CEC2013 D50), 4 cells, 33 files, 402,693 bytes
      {full,no_sgsm,no_adaptive,no_finalpolish}/dt-gsk/cec2013/summary/
      analysis/                   # 5 derived files (rank / means / contrasts / 2 md)
  _paper_tables/
    README.md
    manifest.json                 # 17 files, 64,496 bytes
    provenance.json
    T1.csv .. T16.csv
```

The former release-id directory levels (`_ablation/abl-rel-2026-07-11/`,
`_paper_tables/rel-2026-07-10-262fc16c9/`) and the old `_overlay/` name were removed;
release ids are retained as logical identifiers inside the manifests and READMEs. The
per-cell internals `<cell>/dt-gsk/<suite>/summary/...` are unchanged, so generators
that key off the summary layout keep resolving.

---

## Scaffold X-ABL-01 (CEC2017) — 7 cells x {D10,D30,D50,D100} summary + per_run

All 7 cells (`baseline, no_ace, no_psr, no_bse, no_linkage, no_localsearch, no_arch`)
present under `scaffold/<cell>/dt-gsk/cec2017/summary/`:

| Artifact | Expected | Result |
|---|---|---|
| `dt-gsk_cec2017_D10.csv` | 29 functions | 7/7 cells OK (29 rows each) |
| `dt-gsk_cec2017_D30.csv` | 29 functions | 7/7 cells OK (29 rows each) |
| `dt-gsk_cec2017_D50.csv` | 29 functions | 7/7 cells OK (29 rows each) |
| `dt-gsk_cec2017_D100.csv` | 29 functions | 7/7 cells OK (29 rows each) |
| `per_run.csv` | 2,900 rows (25 runs x 29 funcs x 4 dims) | 7/7 cells OK (2,900 rows each) |

`baseline/dt-gsk/cec2017/_d100_repair_provenance/` (validated-repair D100 provenance:
environment/phase0_protocol/run_config/verification JSON + seed_schedule) present.

## Overlay X-ABL-02 (CEC2013 D50) — 4 cells x D50 summary + per_run

All 4 cells (`full, no_sgsm, no_adaptive, no_finalpolish`) present under
`overlay/<cell>/dt-gsk/cec2013/summary/`:

| Artifact | Expected | Result |
|---|---|---|
| `dt-gsk_cec2013_D50.csv` | 28 functions | 4/4 cells OK (28 rows each) |
| `per_run.csv` | 700 rows (25 runs x 28 funcs) | 4/4 cells OK (700 rows each) |

`seed_schedule.csv` byte-identical across all 4 cells (fair-paired design).

## Overlay analysis (contrasts / rank / means)

All present under `overlay/analysis/`:

- `ablation_overlay_rank_summary_cec2013_D50.csv` — Friedman rank matrix (4 cell rows). OK
- `overlay_per_function_means_cec2013_D50.csv` — per-function mean-error matrix (28 func rows). OK
- `overlay_contrasts_cec2013_D50.json` — paired Wilcoxon + Holm contrasts. OK
- `overlay_validation.md`, `overlay_findings.md` — human-readable notes. OK

## Paper tables X-PT-01 — T1..T16 + provenance

- `T1.csv` .. `T16.csv` — all 16 present, flat under `_paper_tables/`. OK
- `provenance.json` — present; `exports` covers exactly `T1.csv`..`T16.csv`. OK
- Table -> suite/dim map documented in `_paper_tables/README.md`. (T21/T22 parametric
  tables intentionally absent — no admissible sensitivity release, EG-006.)

---

## Manifest integrity

| Manifest | Files | Bytes | Byte-identity vs prior committed manifest |
|---|---|---|---|
| `_ablation/manifest.json` | 108 | 3,011,471 | 108/108 SHA-256 match, 0 mismatches |
| `_paper_tables/manifest.json` | 17 | 64,496 | 17/17 SHA-256 match, 0 mismatches |

- All 108 + 17 manifest-listed paths exist on disk.
- Scaffold group total (2,608,778 bytes) and overlay group total (402,693 bytes) equal
  the prior committed per-study manifest totals exactly; paper-tables total (64,496 bytes)
  equals the prior `paper_tables_manifest.json` total exactly.
- Old release-id directories removed (`abl-rel-2026-07-11/`, `rel-2026-07-10-262fc16c9/`).

`_ablation/manifest.json` SHA-256 (Stage 1, pre-curves)
`a980dd35608e738dd37d9e9588760b77173bee1dd79eedd3f7ae42672bed104b`.
`_paper_tables/manifest.json` SHA-256
`6c5216232b946358060cc84b899c537d7edf89f36ebb67e5094eb0687e784ccf`.

---

## Stage 2 — convergence curves + gen_logs (2026-07-12)

After the byte-identical restructure, the per-run representative **convergence curves**
were promoted into every ablation cell so the immutable evidence tree carries the
convergence trace behind the ablation, not just the summary statistics:

- **924 curve CSVs** added (`.../curves/Figure_F<f>_D<d>_Run#<r>.csv`, one representative
  run per function per dimension): scaffold 7 cells x CEC2017 D{10,30,50,100} and overlay
  4 cells x CEC2013 D50. Baseline CEC2017 D100 curves are sourced from the validated D100
  repair root (matching the promoted `per_run` composition).
- All curve files are read-only; each is recorded in `_ablation/manifest.json` with its
  SHA-256 (`kind: "curve"`). Manifest totals updated **108 -> 1,032 files**.
- **gen_logs were not promoted because none exist**: the ablation campaigns were run with
  `generation_logs=false`, so no per-generation checkpoint CSVs were produced. The
  convergence evidence is carried entirely by the curve CSVs above. (See
  `_ablation/manifest.json:curves_and_genlogs_note`.)

**Generator single-source cleanup.** With the paper-table CSVs and ablation evidence now
all under `benchmarks/cec_reference_results/`, the last vestigial `results/` **read**-path
was removed from `papers/scripts/generate_latex_tables.py`: its dead scaffold-ablation
emitter (which scanned `results/ablation/` for `ablation_<tag>.tex`, never `\input` by the
paper and suppressed with `--skip-ablation` in production) was deleted. The paper's
scaffold-ablation tables SA01/SA02 are produced solely by
`generate_ablation_exhibits.py` from the manifest-verified frozen copy under
`papers/build_prompt_phases/phase_12/ablation_results/`. Regenerating T01-T16 after the
edit is byte-identical to the committed exhibits (0 diff).

Remaining `results/` mentions in `generate_ablation_matrix.py` are its **output**
`--out` default (`results/ablation/...`), i.e. where the regeneration tool *writes* a
derived rank matrix; it *reads* the immutable benchmark scaffold. No paper-building
consumer reads from `results/` staging.

---

## Missing / flagged

None. Every paper-required datum (scaffold 7x4 summaries + per_run + curves; overlay
4-cell D50 summaries + per_run + curves + analysis; paper tables T1-T16 + provenance) is
present with the expected row counts, and every relocated byte is identical to the
pre-restructure evidence.
