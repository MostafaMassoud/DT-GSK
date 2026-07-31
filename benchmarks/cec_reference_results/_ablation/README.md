# `_ablation` — component-study evidence (abl-rel-2026-07-20)

**Generated from `manifest.json` — regenerate with the finalization tooling
rather than editing by hand** (this file drifted from the manifest once;
the manifest is the authority for every number below).

Immutable evidence for the two component studies reported in Supplementary
Materials §S6: the scaffold remove-one ablation (**X-ABL-01**) and the direct
SGSM/ISM-overlay isolation (**X-ABL-02**). Release **`abl-rel-2026-07-20`** supersedes
`abl-rel-2026-07-16` (which superseded `abl-rel-2026-07-13`): the complete **51-run** regeneration with the post-fix binary
(C006 final-polish incumbent + M038 graph-backend corrections; see the
supersession note in `manifest.json`).

**Totals:** 1,297 files / 468 MB —
scaffold 882, overlay 404,
analysis 11.

## Layout

```text
_ablation/
  manifest.json                 SHA-256 authority over every file below
  scaffold/<cell>/dt-gsk/cec2017/{summary/, curves/}   7 remove-one cells
  overlay/<cell>/dt-gsk/<suite>/{summary/, curves/}    4 isolation cells x 2 suites
  overlay/analysis/             promoted analysis (rank matrices, contrasts
                                JSONs, per-function means, findings/validation)
```

Cells: scaffold = baseline, no_ace, no_arch, no_bse, no_linkage,
no_localsearch, no_psr (ISM **off** in every cell). Overlay = full, no_sgsm,
no_adaptive, no_finalpolish (single-toggle vs `full`).

## X-ABL-01 — scaffold remove-one (CEC2017, D10/30/50/100, 51 runs)

interaction_graph_enabled=false in EVERY cell (SGSM/ISM interaction-structure memory OFF). This is a remove-one scaffold ablation CONDITIONAL on SGSM off; it CANNOT establish SGSM's own effect (that is campaign X-ABL-02, running separately). Remove-one deltas are conditional contributions given all other components enabled and SGSM off, NOT independent causal effects.

## X-ABL-02 — SGSM-overlay isolation (51 runs)

CEC2013 D50 (28 functions) plus the primary-suite CEC2017
D50/D100 panels. Headline (see `overlay/analysis/overlay_findings.md` and the
contrasts JSONs):

- CEC2017 D50: At CEC2017 D50 (51 runs) the direct SGSM isolation (full vs no_sgsm) shows NO significant standalone benefit (Holm p=0.983); the ISM-dependent final polish contrast has Holm p=0.00183 (significant).
- CEC2017 D100: At CEC2017 D100 (51 runs) the direct SGSM isolation (full vs no_sgsm) shows NO significant standalone benefit (Holm p=0.897); the ISM-dependent final polish contrast has Holm p=0.00523 (significant).
- CEC2013 D50: At CEC2013 D50 (SGSM-active tier; 51-run rerun) the DIRECT SGSM isolation (full vs no_sgsm) shows NO significant standalone benefit (Holm p=0.647; W/T/L 13/3/12). Adaptive gate Holm p=0.235; eigenframe final polish Holm p=0.00173 (significant).

## Amendments

- **A1** (2026-07-17): documentation-only; zero data files changed — overlay_findings.md + overlay_validation.md regenerated against the 51-run results and re-hashed (2 entries); overlay_finding.honesty placeholder replaced with the 51-run re-evaluation; curves_and_genlogs_note refreshed (2026-07-16 promotion; repair-root reference retired); studies.X-ABL-02_sgsm_overlay.counts_scope clarification added

## Immutability

Never edit data files under this tree. Corrections arrive as a superseding
release id (data) or as a dated amendment recorded in `manifest.json`
(documentation). Verify any file against `manifest.json`'s SHA-256 before
using it; the hash basis is the mint-time working-tree bytes (see the root
README's line-ending note).

<!-- Documentation-only amendment 2026-07-31 (A2, per this file's own
     drift warning): the title and supersession lines above were refreshed
     to the manifest's release_id abl-rel-2026-07-20; manifest.json remains
     the authority and no data byte changed. -->
