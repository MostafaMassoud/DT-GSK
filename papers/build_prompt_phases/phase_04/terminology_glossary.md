# DT-GSK Manuscript — Frozen Terminology Register

**Phase 4 deliverable (task 10 — terminology freeze).**
Status: **FROZEN at Phase 4 (2026-07-10).** Any change to any entry in this register
requires a change request in `papers/governance/change_request_register.csv`; no phase
5–12 artifact may silently deviate. Every manuscript section, table caption, figure
caption, and supplement MUST use the exact spellings, capitalizations, and expansion
rules below.

Sources of record: `papers/build_prompt_phases/phase_03/notation_table.md`,
`phase_03/contribution_matrix.md`, `phase_03/parameter_table.md`,
`docs/algorithms/dt-gsk.md`, `papers/governance/evidence_cards/jawad2024egsk.md`,
`papers/PAPER_BUILD_PROMPT.md` (Phase 4 task 10, CR-0003 delta).

---

## 1. Method name

| Item | Frozen form |
|---|---|
| Short name | **DT-GSK** (all caps, single hyphen; never "ISM GSK", "IsmGsk", "ismgsk" in prose) |
| Expansion (first use, title, abstract) | **Dimension-Tiered Gaining-Sharing Knowledge** |
| First-use pattern | "Dimension-Tiered Gaining-Sharing Knowledge (DT-GSK)" once in the abstract and once at first body use; **DT-GSK** thereafter. |
| Optimizer id (code/data contexts only) | `dt-gsk` (lowercase, monospace; used only when naming files, CLI ids, or evidence paths) |
| Prohibited variant | The long form with a trailing "Optimization" (appears once in `docs/algorithms/dt-gsk.md:17`) is NOT the manuscript expansion — do not use it. |

## 2. GSK-family algorithm labels (frozen capitalization)

The comparison panel is exactly the **7-algorithm GSK-family panel**. Superiority
wording is always scoped: **"within the GSK family panel"** — never field-wide.

| Display label (prose, tables, figures) | Optimizer id (code/data only) | Notes |
|---|---|---|
| **GSK** | `gsk` | base algorithm (mohamed2020gaining) |
| **AGSK** | `agsk` | (mohamed2020agsk) |
| **APGSK** | `apgsk` | (mohamed2021novel); never "AP-GSK" |
| **FDB-AGSK** | `fdb-agsk` | hyphenated in prose; never "FDBAGSK" except inside verbatim quotes from jawad2024egsk, which prints "FDBAGSK" |
| **eGSK** | `egsk` | see CR-0003 rule below |
| **ATMALS-GSK** | `atmals-gsk` | all-caps ATMALS, hyphen, all-caps GSK |
| **DT-GSK** | `dt-gsk` | proposed method (Section 1) |

**CR-0003 capitalization rule (binding):** the algorithm name is written **eGSK**
— lowercase "e", uppercase "GSK" — **everywhere** (prose, tables, captions, headers,
including sentence-initial position), with a single exception: verbatim quotation of an
official cited title. The official published title (evidence card `jawad2024egsk`) is
"Enhanced Gaining-Sharing Knowledge-based algorithm" (Results in Control and
Optimization 19 (2025) 100542) — when that title is quoted, reproduce it exactly.
Never "EGSK", "Egsk", or "e-GSK" in manuscript text. (The repo directory/port name
`EGSK` and optimizer id `egsk` are code identifiers, permitted only in monospace
code/path contexts.)

## 3. Component names and acronyms (frozen)

First-use rule: each acronym is expanded **once** at first use in the main text in the
pattern "Expansion (ACRONYM)", and used bare thereafter. Abstract may use the bare
acronym only if also expanded at first body use. Supplement re-expands at its own first
use (supplements must be self-contained).

| Frozen name | Expansion at first use | One-line definition |
|---|---|---|
| **ACE** | Adaptive Control Engine (ACE) | EMA-credit multi-armed bandit over a 5-arm (+optional DE arm) pool of `(KF, KR, Kexp)` operator settings; probability floor 0.05; top/bottom acceptance memory at D≥20. |
| **NLPSR** | Nonlinear Population-Size Reduction (NLPSR) | Shrinks NP from `5·D` toward a tier-specific floor `N_min` along the nonlinear `x^(1−x)` schedule (a tier-floored variant of the APGSK NLPSR schedule — never claimed as new). |
| **ARGP** | Acceptance-Rate Gated Pruning (ARGP) | Freezes ACE arms whose windowed acceptance rate falls below a tier threshold after a warm-up fraction, concentrating draws on productive operators. |
| **BSE** | Budget-Safe Escape (BSE) | Triple-trigger stagnation detector (acceptance / diversity / signal floors) firing a Cauchy rescue plus an archive-seeded partial restart, hard-capped so it can never overshoot MaxFES. |
| **SGSM/ISM** | interaction-structure memory (ISM) | Zero-extra-objective-evaluation decaying (λ=0.95) coordinate-pair interaction graph learned from accepted moves (D≥50); confidence-gated; supplies linkage blocks and the local-search subspace. Manuscript-facing name: **interaction-structure memory (ISM)**. **SGSM** is the code/ablation-cell alias (`interaction_graph.py`, `no-sgsm` cell); no expansion of "SGSM" is attested in the evidence sources — do NOT invent one; write "SGSM/ISM" only when referencing code or ablation cells. Never call it "free" without the qualifier "no extra *objective* evaluations". |
| **eigenframe final polish** | (no acronym; lowercase in prose) | One-shot RNG-free deterministic compass search on the eigenbasis of the ISM signed interaction matrix in the final budget slice (D≥50); coordinate axes when no graph signal. Frozen spelling: "eigenframe final polish" (not "eigenspace"/"eigen-polish"). |
| **deep-stall restart** | deep-stall full restart (multi-start) at first use | Default-ON full re-initialisation of the working population when the incumbent is frozen for ≥0.25 of budget, with a preserved global-best so a restart can never lose ground. Short form thereafter: "deep-stall restart". |
| **linkage-aware block crossover** | (no acronym) | Replaces the per-coordinate KR mask, for ~70% of the population, with a contiguous block mask (block size 5 / 10 by dimension tier), periodically refreshed; ISM-supplied blocks at D≥50. |
| **elite archive** | (no acronym; lowercase) | Distance-thresholded archive of elites (≈1.5·NP_init, normalized-L2 threshold) used to seed BSE restarts. |
| **TERRA** | none — unexpanded proper name | D≥100 budget policy gating final-polish / high-D behaviour (`budget_policy.py`). No expansion is attested in the evidence sources; write "the TERRA budget policy" and do NOT fabricate an expansion. |
| **SP-NLPSR** | none — write "SP-NLPSR subspace floor" at first use | D≥100 controller keeping a minimum number of subspace samples (subspace floor companion to NLPSR). "SP" has no attested expansion — do not invent one. |
| **A1 / A2 / FC4** | descriptive apposition at first use | Controller ids, always paired with their frozen descriptors: **A1 late-accept clip**, **A2 frozen-streak broaden**, **FC4 linkage random-mix** (D≥100-gated). Never used bare on first mention. |
| **BudgetController** | code identifier, monospace `BudgetController` | The single evaluation cap through which every objective evaluation is counted; the run stops at MaxFES. Prose synonym: "the evaluation-budget controller". |
| **D≥100 controllers** | collective label | The set {A1, A2, FC4, basin memory, SP-NLPSR subspace floor, TERRA}; all D≥100-gated, no-op below. |

Prohibited wording (from `phase_03/contribution_matrix.md`): never describe the
gaining-sharing operator itself as novel; never claim NLPSR is new; contribution
language is "control, budget, structure-memory, and polish layered on the GSK
scaffold".

## 4. Benchmark-suite names

| Frozen name | Rule |
|---|---|
| **CEC2017** | Primary suite (29 functions, F1 & F3–F30, F2 excluded per protocol; D = 10/30/50/100). Never "CEC 2017" with a space in DT-GSK prose (quotes from cited papers excepted). |
| **CEC2011** | Real-world suite. Same no-space rule. |
| **CEC2013** | **Called "second comparison suite" — never "independent suite", "holdout suite", or "validation suite"** — unless development-history evidence is produced that supports independence (none is currently on record). |

**CEC2013 hold-out exception (preserved distinction):** the SGSM-overlay ablation is,
per `docs/algorithms/dt-gsk.md:473-474` and `phase_03/ablation_toggle_audit.md`,
"ablated separately on the **CEC2013 hold-out design** (`full` / `no-adaptive` /
`no-sgsm` cells)". The phrase "hold-out" is frozen there as the name of that ablation's
*experimental design* (which cells run on which suite), and may be used ONLY in that
ablation context — supplement-only, Phase-12-only (see §5). It is never a suite-level
independence claim, and the main manuscript still calls CEC2013 the "second comparison
suite".

## 5. Evidence terminology

| Frozen term | Meaning |
|---|---|
| **reference results** | The immutable empirical evidence tree `benchmarks/cec_reference_results/` (read-only; CR-0003 immutability prohibitions apply). |
| **evidence release rel-2026-07-10-262fc16c9** | The frozen release identifier. Every empirical number in the manuscript is derived (Phase 6) exclusively from this release. The already-verified family-panel rank statements (docs/algorithms/dt-gsk.md: #1 overall CEC2017 by mean+median; #1 at D10/D50/D100; #2 at D30 behind eGSK; #2 on CEC2011) are the only rank statements permitted in planning artifacts and are always marked "to be re-derived in Phase 6 from release rel-2026-07-10-262fc16c9". |
| **staging** | The `results/` working area for new or independently reproduced runs. Staging data is never citable in the manuscript; it enters evidence only via the controlled promotion pipeline (`scripts/promote_evidence.py`, Section 2.4) which mints a new release id. |
| **exhibit-bound placeholder** | Numeric-slot convention for all planned claims: `<TXX:field>` / `<FXX:field>` bound to an exhibit ID (e.g. `<T05:friedman_rank_D30>`); no empirical value is ever stated as fact before Phase 6 binding. |
| **DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY** | Marker for every component-contribution (ablation) claim. Ablation evidence is supplement-only and Phase-12-only; the main manuscript outline contains NO ablation subsection. |

## 6. Statistical terminology (frozen)

| Frozen term | Usage rule |
|---|---|
| **Friedman test / Friedman mean rank** | Rank aggregation across functions; report "Friedman mean rank" (not "average ranking"). |
| **Iman–Davenport correction** | En-dash compound (`Iman--Davenport` in LaTeX); the F-distributed correction applied to the Friedman statistic. |
| **Nemenyi critical difference (CD)** | Expand "critical difference (CD)" at first use; "Nemenyi CD" thereafter; CD diagrams are "critical-difference diagrams". |
| **Wilcoxon signed-rank test with Holm correction** | Paired per-function comparisons; always name the multiplicity correction ("Holm" / "Holm step-down"); short form "Wilcoxon + Holm" permitted in tables. |
| **Vargha–Delaney A12** | En-dash compound; symbol $A_{12}$ (subscript 12); effect size for stochastic superiority. |
| **Cliff's delta** | Apostrophe-s; symbol $\delta$ when symbolic. |
| **BCa bootstrap confidence interval** | Expand once: "bias-corrected and accelerated (BCa) bootstrap confidence interval (CI)"; "BCa CI" thereafter. |

Significance level, test direction, and n-runs wording are bound in the Phase 5
pre-registration; this register freezes only the names.

## 7. Symbols

Symbols are NOT re-registered here. The single canonical symbol source is
**`papers/build_prompt_phases/phase_03/notation_table.md`** (rendered as
`notation_table.tex`; OMML generated in Phase 9). Rules:

- Every symbol used in prose/equations must appear in that table; no synonym symbols.
- This register and the notation table must never conflict; on conflict, the notation
  table wins for symbols, this register wins for names/labels/capitalization.
- Code identifiers (`ISMGSKConfig`, `build_pub_config`, `interaction_graph_enabled`,
  `BudgetController`, …) are always monospace and are not italicised as math.

## 8. Venue terminology (fixed context)

Frozen target journal: **MDPI Algorithms** (repository-wired: `papers/Definitions/mdpi.cls`,
class option `algorithms`, `papers/main.tex` line 5). The cover-letter venue conflict
(Swarm and Evolutionary Computation) is **risk R-0004, DEFERRED by user decision
2026-07-10** — reference it, do not resolve it.

---

**FREEZE NOTICE.** This register is frozen as of Phase 4 (2026-07-10). Additions or
edits require an approved change request; Phase 10 QA checks manuscript conformance
against this file verbatim.
