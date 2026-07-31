# Promotion integrity verification

**Date:** 2026-07-11 · **git HEAD:** 7f0ebcb4c · **repo root:** `D:/AI/PhD-Projects`
· **evidence root:** `benchmarks/cec_reference_results/`
· `PYTHONIOENCODING=utf-8`

Independent recomputation of every promoted manifest, byte-identity checks against the
staging sources, and git-state confirmation that no primary or scaffold evidence
changed. Verifier: `scratchpad/verify_integrity.py` (streamed SHA-256, no reuse of the
promotion tool's own hashes).

## Result — PASS (all classes)

| Check | Expected | Observed | Status |
|---|---|---|---|
| Overlay manifest hashes recompute | 33/33 | 33/33 | PASS |
| Overlay promoted vs source byte-identical | 33/33 | 33/33 | PASS |
| Overlay files missing | 0 | 0 | PASS |
| Paper-tables manifest hashes recompute | 17/17 | 17/17 | PASS |
| Paper-tables promoted vs `results/paper_tables/` byte-identical | 17/17 | 17/17 | PASS |
| Paper-tables files missing | 0 | 0 | PASS |
| Scaffold manifest hashes recompute | 75/75 | 75/75 | PASS |
| Scaffold files missing | 0 | 0 | PASS |
| Primary tree tracked modifications/deletions | 0 | 0 | PASS |
| Scaffold cells tracked modifications/deletions | 0 | 0 | PASS |

## Detail

### 1. Overlay — X-ABL-02
`_ablation/abl-rel-2026-07-11/_overlay/overlay_evidence_manifest.json`
(SHA-256 `00d2915fd36b8ad9201b445fb63b1304fd8be4ca49c61c98595029d943c151b5`).
All 33 promoted files re-hash to their manifest `sha256` with matching `size_bytes`,
and each promoted file is byte-identical to its recorded `results/_ablation_sgsm/...`
source. Seed schedule byte-identical across all 4 cells
(`b2150782…4798218`); each cell has 700 per_run rows.

### 2. Paper tables — X-PT-01
`_paper_tables/rel-2026-07-10-262fc16c9/paper_tables_manifest.json`
(SHA-256 `954627a794854cbfd505228d9dcce73e39ab7b62cf0e0814525c3c9e5319d99d`).
All 17 promoted files (T1–T16 + provenance.json) re-hash correctly and are
byte-identical to `results/paper_tables/`. Upstream `table_provenance_chain`
bundle-source SHA-256s were recorded at promotion time (33 refs, 0 mismatches) against
`papers/analysis/rel-2026-07-10-262fc16c9/`.

### 3. Scaffold ablation — X-ABL-01 (untouched)
`_ablation/abl-rel-2026-07-11/ablation_evidence_manifest.json`
(SHA-256 `82e0d5256353e6736a5d09e3d458a43c8e67c0c0aad0c296d33434bb0213ac76`).
All 75 files re-hash to their manifest values — the frozen scaffold subtree was not
altered by the overlay/table promotions. The overlay added only a NEW sibling
`_overlay/` subtree and a NEW cross-index `ablation_evidence_manifest_overlay.json`
alongside it; the 7 scaffold cells, their per-cell files, and the scaffold manifest are
unchanged.

### 4. Immutability — git state
`git status --porcelain benchmarks/cec_reference_results` shows **only untracked (`??`)
additions** and **zero** modified/deleted (`M`/`D`) lines:

```
?? .../_ablation/abl-rel-2026-07-11/_overlay/
?? .../_ablation/abl-rel-2026-07-11/ablation_evidence_manifest_overlay.json
?? .../_paper_tables/
```

No existing primary optimizer entry (7 optimizers × 3 suites + aux) and no scaffold cell
was modified or deleted. Promotion was purely additive into new versioned subtrees, per
the immutable-evidence discipline (deterministic copy + SHA-256 manifest, read-only).

## Completeness — evidence NOT under `benchmarks/`

The four paper evidence classes (primary, scaffold ablation, SGSM overlay, paper tables)
are all present and checksummed under `benchmarks/cec_reference_results/`. The only
paper-related artifact not copied into this tree is the traced upstream analysis bundle
`papers/analysis/rel-2026-07-10-262fc16c9/` — the descriptive-stats / Wilcoxon-Holm /
Friedman intermediates from which T1–T16 are derived. This is by design: the tables are
the promoted authoritative inputs, and their dependence on the bundle is pinned by
recorded per-source SHA-256 (re-verified at promotion, 0 mismatches). It is a derivation
source, not independently paper-cited evidence.
