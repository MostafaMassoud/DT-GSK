# Phase 4 — Thesis, Contributions, Journal, Claims, and Manuscript-Plan Freeze — Gate Report

- **Phase:** 4 (PAPER_BUILD_PROMPT.md lines 3632–3874)
- **Anchor commit at execution:** `95bf5b7de` lineage (Phases 0–3 FROZEN)
- **Evidence release:** `rel-2026-07-10-262fc16c9`
- **Gate date:** 2026-07-10
- **Verdict:** **APPROVED — Phase 4 FROZEN**
- **Signatories:** P1 + P6 + P9 + P10 (framework Gate 4 quorum)

## 1. Signed freeze summary

### Target journal (task 1; decision D-0010)
**MDPI *Algorithms*** — repository-wired (`Definitions/mdpi.cls`, class option
`algorithms`, `main.tex:5`), frozen per the framework default + explicit user
instruction 2026-07-10. Official instructions page returned HTTP 403 at verification
time → `journal_requirements.md` records repo-proven facts + search-derived guidance
with `verified_online=false` and a mandatory before-submission re-verification.
**R-0004 (cover letter addresses Swarm and Evolutionary Computation) is DEFERRED**,
owner Phase 9/11; the stale letter must never be rendered/packaged as-is. Claims row
CL-01 is `BLOCKED_ON_R-0004`. Family-precedent note: ATMALS-GSK itself was published
in MDPI Algorithms (18(7):398, 2025) — recorded in the journal decision.

### Thesis (task 4)
Problem → bounded gap (GSK-family variants adapt parameters but do not learn/exploit
accepted-move interaction structure) → central mechanism (SGSM/ISM + eigenframe polish
on a dimension-tiered scaffold) → evaluation design (7-algorithm family panel;
CEC2017 primary + CEC2011 secondary real-world + CEC2013 second comparison suite;
release-locked) → strongest claim TYPE (family-panel rank superiority + scalability
trend; never field-wide) → reproducibility (byte-stable, profile-locked, promoted
release). Zero unverified numbers; the only rank statements quoted carry the
"re-derived in Phase 6" mark.

### Accepted contributions (tasks 2–3)
- **C1** Interaction-structure memory (ISM/SGSM) — ORIGINAL; zero-extra-objective-evaluation structure learning; absorbs linkage exploitation.
- **C2** Eigenframe final polish — ORIGINAL; deterministic RNG-free endgame on the learned eigenbasis.
- **C3** Dimension-tiered adaptive scaffold (ACE+ARGP+NLPSR+BSE+deep-stall/global-best) — MODIFIED/ORIGINAL composite, honestly labeled.
- **C4** Controlled reproducible family evaluation + byte-stable ablation infrastructure — ORIGINAL infrastructure.
Non-elevated phase_03 rows recorded with merge rationale. Component-causality claims
are `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY` throughout.

### Claims inventory (task 6)
`papers/governance/claims_evidence_matrix.csv`: **50 rows** (6 background, 11 method,
6 protocol incl. CEC2017 definition via `awad2016problem` per CR-0005, 11 primary-result
templates `PENDING_PHASE_6`, 3 interpretation, **5 limitations incl. seeded D30-#2-behind-eGSK
row**, 2 conclusion, 1 highlights, 2 cover-letter). RFC-4180 valid; all citation keys
⊆ the 57 admissible keys.

### Outline, budget, exhibits (tasks 7–8)
- `outline.md`: 5-section spine, 31 numbered units + supplement S1–S6 (S6 = RESERVED
  ablation, Phase-12-only). **No ablation subsection in main text** (explicit).
  Canonical source binding: `papers/main.tex` + `sections/*.tex` + `supplementary.tex`.
- `page_budget.md`: prose 10,200 words (~18.6 pp) + 25 main exhibits (~13.3 pp) =
  **~31.9 pp projected** vs hard cap 34 (headroom 2.1); B2 word cap 12,000;
  6-step supplement-migration valve; PDF+DOCX parity check binding at Phase 9.
- `exhibit_plan.csv`: **71 exhibits** (40 main / 28 supplement / 3 Phase-12-reserved)
  with binding pre-registrations P1–P8: 7-algorithm panel order, **per-checkpoint
  mean-across-runs convergence aggregation (CR-0001)**, fixed Okabe-Ito color/linestyle
  map, dimension sets per suite, and the **summary-statistic-derived main-text curve
  selection rule P5** (featured D30+D100, stratified by difficulty × DT-GSK standing,
  ≥1 hard + ≥1 unfavorable case, recorded before any rendering).
- `conceptual_figure_specs.md`: 4 approval-level specs (architecture, SGSM mechanism,
  tier gating, taxonomy), each with an explicit no-empirical-source statement —
  approved by this gate.

### Terminology + conventions (tasks 10, 12)
- `terminology_glossary.md` FROZEN: eGSK capitalization rule (CR-0003), CEC2013 =
  "second comparison suite", no fabricated acronym expansions (SGSM/TERRA/SP-NLPSR
  left unexpanded — none attested in evidence).
- `papers/governance/presentation_conventions.md` FROZEN (CR-0002/0003): all 22
  dimensions × three exemplars with adopted practice + weakness-to-avoid; two recorded
  improvements beyond all exemplars (Holm correction; cross-consistency audit).

### Novelty scope (tasks 5, 9)
`novelty_scope.md`: closest-work comparison strictly along 4 verified dimensions
(update trigger / evaluation cost / what is learned / how exploited) vs differential
grouping, CMA-ES/eigenvector crossover, adaptive operator selection, direct search;
**11-item explicit non-claims register**; evidence-role table (CEC2020/CEC2013-LSGO
context-only).

## 2. Adversarial QA (P1+P6+P9+P10 panel) and resolution
Initial verdict: **0 critical, 3 major, 2 minor** → all resolved this session:
1. ~~[major] page_budget arithmetic (13.5 vs actual 14.2)~~ → Section 4 rebuilt against
   the exhibit registry: 25 main exhibits, subtotal **13.3**, total **31.9**, headroom 2.1
   (re-verified by script: sums exact).
2. ~~[major] exhibit_plan vs outline/page_budget inconsistencies~~ → exhibit_plan.csv is
   now the single registry (71 rows, +T-FAMREV/T-WORKED/F05-RANKBAR); outline X-IDs
   cross-mapped; single algorithm float (A1 = DT-GSK); T01 full tables → S1; CEC2011
   convergence → S3 only.
3. ~~[major] convergence aggregation conflict (median-run vs mean-across-runs)~~ →
   **per-checkpoint mean-across-runs everywhere** (Section 6.7 default, pre-registration
   P2); outline §4.5 + conventions Dim 15 aligned; GSK's median-run practice recorded
   as NOT adopted.
4. ~~[minor] main-text mechanism-trajectory figure unbacked~~ → dropped from main budget;
   F-TRACE/F-ADAPT remain supplement-designated + diagnostic-release-gated.
5. ~~[minor] hansen2001cmaes card "EGSK"~~ → corrected to eGSK (1 token).
Verification script: exhibit CSV parses (71×9), claims CSV parses (50×9), budget sums
exact, no residual prohibited tokens (remaining "EGSK"/"median-run" occurrences are the
rules prohibiting them).

## 3. Gate 4 hard-failure checks (framework line 3871)
| Blocking condition | Status |
|---|---|
| Unsupported novelty | NONE — C1–C4 evidence-bounded; 11 explicit non-claims |
| Unbounded superiority | NONE — all wording "within the GSK family panel" |
| Unverified journal requirements | DISCLOSED — verified_online=false recorded with re-verification obligation (not a silent gap) |
| Planned main-text ablation | NONE — S6 reserved, X-ABL-* Phase-12-only, outline explicit |

## 4. Sign-off
- **P1:** APPROVED — every contribution traces to code + evidence.
- **P6:** APPROVED — narrative coherent, no overpromise, no invented numbers.
- **P9:** APPROVED — novelty wording bounded; citations ⊆ 57 admissible keys.
- **P10:** APPROVED — journal rules recorded with access date + verification status; R-0004 deferral binding on Phase 9/11.

**Gate 4 APPROVED. Phase 4 FROZEN 2026-07-10.** Later empirical results may narrow or
remove claims but may not silently expand them. Phase 5 entry (statistical-analysis
freeze) is unblocked.
