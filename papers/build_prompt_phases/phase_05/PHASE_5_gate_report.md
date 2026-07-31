# Phase 5 — Statistical-Analysis, Protocol, and Exhibit-Design Freeze — Gate Report

- **Phase:** 5 (PAPER_BUILD_PROMPT.md lines 3877–4098)
- **Evidence release:** `rel-2026-07-10-262fc16c9` (read-only; schemas inspected, no outcome computed)
- **Gate date:** 2026-07-10
- **Verdict:** **APPROVED — Phase 5 FROZEN**
- **Signatories:** P3 + P4 + P5 + P9 (framework Gate 5 quorum)

## 1. What is now pre-registered (before any outcome inspection)

### Analysis families — `analysis_registry.csv`, 59 rows
- **CEC2017 (28):** descriptive ×4 dims, Friedman+Iman-Davenport omnibus ×4 (Nemenyi CD
  only if omnibus significant), across-function Wilcoxon+Holm (m=6) ×4, run-level
  per-function Wilcoxon ×4, A12/Cliff+BCa ×4, convergence aggregation ×4, rank-vs-dimension
  trend, per-category exploratory, cost.
- **CEC2013 (14)** and **CEC2011 native (5)** with the same machinery; CEC2011 endpoint =
  `best_fitness` (error undefined by design — pre-registered).
- **Robustness (8)** AN-ROB-2017-01..08 with a crosswalk to `robustness_plan.md` R1–R7 +
  pooled-aggregation check; **BH exploratory (1)** separately labeled, never headline.
- **Ablation (3)** — `PHASE_12_ONLY`, quarantined (see below).

### Key pre-registered dispositions (nothing left outcome-driven)
1. **apgsk CEC2017 D10/30/50 per-run gap** (anomaly A2-004): sole inferential basis =
   across-function Wilcoxon on per-function means; attached effect = **matched-pairs
   rank-biserial** from that same test; CI **disclosed-unavailable**, never imputed;
   all per-run-dependent quantities (run-level Wilcoxon, A12/Cliff, BCa) disclosed-unavailable.
2. **Overall rank rows** = descriptive mean of per-dimension Friedman mean ranks — NO
   cross-dimension pooled test (pooled block-Friedman lives only in robustness r08).
3. **BCa bootstrap**: B=10,000, 95%, deterministic entropy-list seeding
   `SeedSequence([20240620, suite_ordinal, dimension, function, comparator_P1_index])` —
   single construction, all documents agree.
4. **Curve selection**: fully deterministic, summary-statistic-only algorithm (terciles ×
   DT-GSK standing, 9-stratum fill priority, lowest-function tie-break, ≥1 hard + ≥1
   DT-GSK-weak constraint with deterministic repair), executed in Phase 6 **before any
   curve is rendered or viewed**; 58-row audit record, exactly 8 main-text selections.
5. **Multiplicity**: Holm primary in enumerated families (m=6 per suite×dimension
   across-function; per-(dim,comparator) across functions run-level); BH exploratory-only.
6. **Pseudoreplication prohibition**: across-function claims use function-level units.
7. **Strict-source execution**: every Phase 6 command under `GSK_STRICT_SOURCE=1`;
   allowed root = the release; outputs → `papers/analysis/rel-2026-07-10-262fc16c9/<suite>/`
   with `source_use_log.json`; deterministic naming
   `<family>_<suite>[_D<dim>][_<qualifier>].csv` with a closed 13-family vocabulary;
   sort order = suite, dimension, function, P1 panel order; floats `%.6e`; p-values
   floored at 1e-4 for display, unrounded in computation.
8. **Ablation quarantine**: scaffold remove-one (7 cells), SGSM overlay (4 cells incl. the
   pre-registered `no_finalpolish`), full/cell Wilcoxon+Holm families — all design-level,
   `PHASE_12_ONLY`; the live `results/_ablation` staging campaign is quarantined evidence;
   no outcome may be inspected before Phase 11 freeze.

### Claim bindings
`claims_evidence_matrix.csv` extended in place with a 10th `analysis_ids` column (50 rows,
byte-preserving append verified); every empirical claim row bound to ≥1 registry analysis;
orphan check clean both directions (`claim_analysis_binding_report.md`).

## 2. Adversarial QA (P3+P4+P5+P9) and resolution
Initial verdict: **1 critical, 6 major, 2 minor** — all cross-document authority conflicts
from parallel drafting; **all resolved and re-verified on disk**:
1. ~~T05 overall-row pooled test~~ → descriptive-only schema (critical fix).
2. ~~AN-ABL-POLISH unexecutable~~ → 4th overlay cell `no_finalpolish` pre-registered.
3. ~~Robustness double-registration~~ → crosswalk table; `robustness_plan.md` authoritative.
4. ~~Two BCa seed constructions~~ → single entropy-list form everywhere.
5. ~~Three naming vocabularies~~ → Sec.5 pattern + closed vocabulary; ~40 registry
   output_file cells normalized; stale-name grep = 0 hits.
6. ~~Three curve-selection formats~~ → 8-column authoritative format; 9th column forbidden.
7. ~~apgsk effect-attachment conflict~~ → rank-biserial + disclosed-unavailable CI.
8. ~~ARGP in scaffold list / eGSK casing~~ → corrected.
Final CSV checks: `registry rows 59 cols 10 bad []` · `claims rows 50 cols 10 bad []`.

## 3. Gate 5 hard-failure checks (framework line 4097)
| Blocking condition | Status |
|---|---|
| Invalid pairing | NONE — unified-seed pairing verified (seed_and_pairing_audit.md); per-run tests only where per-run data exists for both algorithms |
| Undefined multiplicity | NONE — every test in exactly one enumerated Holm family |
| Unbound claim | NONE — binding report orphan-clean both directions |
| Forbidden source | NONE — strict-source design mandatory; results/ + staging quarantined |
| Early ablation access | NONE — design-level only; quarantine explicit; no outcome touched |

## 4. Sign-off
- **P3:** APPROVED — units/estimands/hypothesis families independently coherent; no post-hoc choice remains open.
- **P4:** APPROVED — data resolution verified against the release schema; pairing available where claimed; apgsk gap dispositioned.
- **P5:** APPROVED — deterministic, source-guarded command design; single seeding construction; closed naming vocabulary.
- **P9:** APPROVED — planned wording matches method capability; ablation fully pre-registered, untouched.

**Gate 5 APPROVED. Phase 5 FROZEN 2026-07-10.** Any later primary-analysis change is a
logged confirmatory amendment or exploratory deviation (SAP change-control clause).
Phase 6 (primary evidence computation) is unblocked and MUST execute exactly this plan.
