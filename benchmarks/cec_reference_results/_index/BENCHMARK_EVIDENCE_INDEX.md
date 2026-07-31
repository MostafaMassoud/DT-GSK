# BENCHMARK EVIDENCE INDEX — where every paper number comes from

> **Location note (2026-07-28).** This living index moved from the evidence
> root into `_index/` so the root holds only manifest-bound release files
> (`check_manifest --strict-inventory` now reaches zero unlisted). All
> relative paths below are stated relative to
> `benchmarks/cec_reference_results/`, unchanged. The frozen root
> `README.md` (byte-bound by the primary release manifest, hence not
> editable) still links to the old location; the file's NAME is unchanged.
> External baseline tables (mos, decc-g, shade-ils) moved the same day to
> `_external_baselines/` with EV-09 provenance sidecars -- out of paper
> scope per CR-0019.

Single navigation source for `benchmarks/cec_reference_results/`, the DT-GSK
manuscript's evidence tree. This file is deliberately **not** hash-bound (it is
a living document, updated with every release); every number it quotes is
authoritative only in the manifest it points at.

**State: post-fix 51-run finalization of 2026-07-16** (C006 final-polish
incumbent + M038 graph-backend corrections, commit `af7efc534`; campaign +
finalization chain: `scripts/run_campaign.py` → `papers/scripts/finalize_evidence.py`).

## §0 Release ledger — the one table to consult first

| Evidence class | Path | Release id | Manifest (hash authority) | Schema | Hash basis |
|---|---|---|---|---|---|
| Primary suites (7-algorithm panel) | `cec2011/ cec2013/ cec2017/` | `rel-2026-07-20-67d9345f9` | `papers/governance/evidence_release_manifest.json` (3,403 files) | `evidence_release_manifest/v1` | mint-time working-tree bytes (CRLF on this checkout) |
| Ablation + overlay | `_ablation/` | `abl-rel-2026-07-20` (51 runs; amendment A1 2026-07-17) | `_ablation/manifest.json` (1,297 files) | `ablation_evidence_manifest/v2-unified` | mint-time bytes (LF) |
| CEC2020 family panel | `cec2020/` | `cec2020-rel-2026-07-29-5867abe1e` | `papers/governance/evidence_release_manifest_cec2020.json` (336 files) | `suite_evidence_manifest/v1` | mint-time bytes; separate, non-superseding (curves + session logs excluded in-manifest; verification verdicts NOT_VERIFIED/NO_REFERENCE by design) |
| CEC2013LSGO family panel | `cec2013lsgo/` | `lsgo-rel-2026-07-28-ff1a046ef` | `papers/governance/evidence_release_manifest_cec2013lsgo.json` (173 files) | `suite_evidence_manifest/v1` | mint-time bytes; separate, non-superseding (curves + session logs excluded in-manifest; verification verdicts NOT_VERIFIED/NO_REFERENCE by design -- no external ground truth exists) |
| Paper-table export (T1–T16) | `_paper_tables/` | `rel-2026-07-20-67d9345f9` | `_paper_tables/manifest.json` (17 files) | `paper_tables_promotion_manifest/v2-flat` | mint-time bytes |

**Resolve release ids programmatically** (each manifest's `release_id` field);
never hardcode them in tools — every pipeline script takes `GSK_REL_ID` /
`GSK_ABL_RELID` / `GSK_OVL_*` env overrides.

## §1 Primary suites — the panel every headline number rests on

Seven optimizers (`gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk`) ×
three suites, flat layout `<suite>/<optimizer>/`:

- **CEC2017** (primary): 29 functions (F2 excluded), D10/30/50/100, 51 runs →
  `per_run.csv` = 5,916 rows per optimizer.
- **CEC2013** (second comparison): 28 functions, D10/30/50, 51 runs → 4,284 rows.
- **CEC2011** (real-world): 22 problems, native dims, 25 runs → 550 rows;
  ships a combined table plus 16 per-native-dim slices.

Each cell: per-dimension aggregate CSVs, `per_run.csv`, `curves/` (one
representative per function × dim: 116/84/22), `gen_logs/`
(checkpoint-error logs, same counts), and five provenance files
(`environment/phase0_protocol/run_config/seed_schedule/verification`).
Consumed by `gsk-stats --strict-source` and `papers/scripts/phase6_run_analysis.py`
→ the analysis bundle `papers/analysis/rel-2026-07-20-67d9345f9/`.
In the 2026-07-16 re-mint, every non-dt-gsk file was **byte-verified unchanged**
against the prior release; only the dt-gsk cells were regenerated.

## §2 Ablation + overlay (`_ablation/`, 51 runs)

- **X-ABL-01 scaffold remove-one**: 7 cells × CEC2017 × D10/30/50/100.
  Four Holm-significant (all favorable) contrasts: ACE at D10; local search,
  NLPSR, and BSE at D30. Analysis staging for the paper's SA01/SA02:
  `papers/build_prompt_phases/phase_12/ablation_results/` (§6).
- **X-ABL-02 overlay isolation**: 4 single-toggle cells × {CEC2017 D50/D100,
  CEC2013 D50}. SGSM null everywhere (Holm p = 0.983 / 0.897 / 0.647);
  final polish Holm-significant everywhere (p = 0.002 / 0.005 / 0.002).
  Narrative + validation: `overlay/analysis/overlay_findings.md`,
  `overlay_validation.md`; machine-readable: `overlay_contrasts_*.json`,
  `ablation_overlay_rank_summary_*.csv`, `overlay_per_function_means_*.csv`.
- **Amendment A1 (2026-07-17, documentation-only)**: recorded in
  `manifest.json` `amendments`.

## §3 Paper-table export (`_paper_tables/`)

T1–T16 + `provenance.json`, exported exclusively from the Phase-6 bundle and
promoted by finalize P7, which also re-mints `manifest.json` (the manifest can
no longer lag the tables). Table map: `_paper_tables/README.md`.

## §4 Promotion audit record — git history

The per-release audit copies previously under `_releases/` were removed
(2026-07-18); **git history is the audit record** of every promotion — the same
stance already accepted for the pre-fix `rel-2026-07-10` release, which never had
an audit copy. The flat tree remains the read path and
`evidence_release_manifest.json` binds it.

## §5 Pinned exceptions — paper inputs that live OUTSIDE this tree

**Single-source guarantee (2026-07-18).** The manuscript depends *exclusively* on
this evidence tree as its raw source. `papers/scripts/phase6_run_analysis.py`
enforces a strict-source guard that **forbids** `results/`, and
`validate_evidence_bindings.py` binds every spot-checked reported number here
(30 PASS / 0 FAIL). The transient run-staging tree `results/` (613 MB, never read
by the paper) was **removed on 2026-07-18** and remains recoverable from git
history; a future run simply re-creates it under the same path. The only
intentional out-of-tree artifacts are the *derived* analysis caches listed below —
each generated from this tree and carrying a recorded SHA-256 chain back to it, so
each is a cache of the derivation, never an independent source.

The paper's numbers resolve from this tree **plus** these derived-analysis
locations (each carries its own recorded SHA-256 chain back to this tree):

| Dependency | Role | Chain |
|---|---|---|
| `papers/analysis/lsgo-rel-2026-07-28-ff1a046ef/` | phase6b analysis bundle for the LSGO release (registered families incl. the confirmatory paired layer and effect sizes) | self-manifested: `analysis_manifest.json` + `analysis_checksums.sha256`; driver self-check reproduces the Amendment 1 pins |
| `papers/analysis/cec2020-rel-2026-07-29-5867abe1e/` | phase6b analysis bundle for the CEC2020 release (full registered confirmatory battery, 784 statistical rows) | self-manifested: `analysis_manifest.json` + `analysis_checksums.sha256` |
| `papers/analysis/rel-2026-07-20-67d9345f9/` | Phase-6 analysis bundle (statistics, ranks, BCa, robustness inputs) | generated strict-source from §1; per-file hashes in its own manifest/checksum records |
| `papers/build_prompt_phases/phase_12/ablation_results/` | SA01/SA02 staging (rank matrices + descriptive deltas) | `ablation_results_manifest.json` binds `_ablation/manifest.json`'s SHA-256 |
| `papers/analysis/ablation_overlay/ism_isolation_*.csv` | Table A17 effect sizes + ISM overhead | regenerated from §2 per-run data |
| `papers/analysis/posthoc_robustness/*.csv` | §S2 endpoint/permutation robustness | regenerated from §1 per-run data |

Diagnostic per-generation GenLogs (EG-005) exist **nowhere**: quarantined,
disclosed in the manuscript; the two diagnostic-only figure tools that read
them are excluded from the pipeline and their outputs are not part of the
manuscript.

## §6 Conventions a reader must know (frozen — documented, not "fixed")

1. **Three nesting layouts** (flat suites / ablation cells / audit copies) —
   see the root `README.md`; frozen by manifest hashes + ~28 consumer scripts.
2. **Curves are human-curated evidence**: `Figure_F<f>_D<d>_Run#<r>.csv`
   (the `#` is deliberate; no script parses these names). Convergence figures
   are generated from `gen_logs/CheckpointErrors_*.csv` instead.
3. **cec2011 dual tables** (combined + per-native-dim) are source-faithful imports.
4. **Hash basis is checkout-EOL-dependent** (no `.gitattributes` pin yet):
   verify EOL-tolerantly on non-Windows checkouts; a `-text` pin + one-time
   re-mint is planned post-submission.
