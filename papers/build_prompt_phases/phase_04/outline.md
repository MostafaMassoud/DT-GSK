# DT-GSK — Main-Manuscript Outline (Phase 4, task 7)

**Phase 4 deliverable (claim-freeze input to Gate 4).** Date: 2026-07-10.
Target: MDPI *Algorithms*, article type **Article** (repo-proven: class option `article`
in `papers/main.tex` line 5; official page returned HTTP 403 on 2026-07-10 — re-verify
before submission). Frozen venue per `phase_04/journal_decision.md`; cover-letter venue
conflict is risk R-0004, DEFERRED by user decision 2026-07-10 (referenced, not resolved).

**Inputs of record:** `phase_04/thesis.md`, `phase_04/contribution_matrix.md` (C1–C4),
`papers/governance/presentation_conventions.md` (FROZEN, CR-0002/CR-0003, Dimensions
1–22), `phase_04/journal_requirements.md`, `phase_04/journal_decision.md`,
`phase_03/*` (frozen method artifacts), `docs/algorithms/dt-gsk.md`,
`papers/governance/data_ledger.csv`, `papers/governance/allowed_citation_keys.txt` (57 keys).

**Numeric discipline (binding).** No empirical value is stated as fact anywhere in this
outline. All numeric slots are exhibit-bound placeholders (`<TXX:field>` / `<FXX:field>`,
registry in `contribution_matrix.md`) bound in Phase 6 from release
`rel-2026-07-10-262fc16c9`. The only permitted rank statements are the verified
family-panel ranks in `docs/algorithms/dt-gsk.md`, always marked "to be re-derived in
Phase 6 from release rel-2026-07-10-262fc16c9". All comparative wording is scoped
"within the GSK family panel".

**BINDING EXCLUSION — stated explicitly per the Phase 4 constraints:**
**There is NO ablation subsection anywhere in the main manuscript.** All
component-contribution evidence is `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY` and lives
exclusively in supplement section S6 (reserved below). Main-text mechanisms are
presented as *proposed and fully specified*; causal attribution is deferred.

---

## 0. Canonical source binding (Section 9.1 model)

The manuscript's canonical LaTeX sources are, and remain:

- `papers/main.tex` — MDPI class wiring (`Definitions/mdpi.cls`, class options
  `algorithms,article,submit,moreauthors,pdftex`), macros, includes.
- `papers/sections/*.tex` — one file per top-level section (Phase 8 rewrites in place).
- `papers/supplementary.tex` (+ `papers/sections/supplementary_content.tex`) — the
  supplement (S1–S6 below).

No new manuscript source files are introduced by this outline; Phase 8 rewrites the
existing files to this outline.

### 0.1 Audit of existing prose (AUDIT ONLY — Phase 8 rewrites; reuse as raw material)

| File | Size | What exists | Non-conforming items that MUST NOT propagate to Phase 8 |
|---|---|---|---|
| `papers/main.tex` | 9.9 KB | MDPI wiring, name macros (`\ismgsk` etc.), siunitx setup, title/authors | Title/abstract wording predates claim freeze; re-check against thesis.md |
| `papers/sections/introduction.tex` | 9.6 KB | Full introduction draft | Rewrite to Dim 3/5 (funnel ≤ 1.5 pp, contribution bullets C1–C4, no pre-Section-4 numbers) |
| `papers/sections/literature_review.tex` | 16.6 KB | Taxonomy subsection + 4-category GSK-variant typology + gaps subsection | Structure is close to Dim 6; needs the summary comparison table and per-variant critical sentences |
| `papers/sections/proposed_algorithm.tex` | 79.3 KB | All mechanism subsections, pseudocode, worked examples | Duplicate `\label{sec:alg:complexity}` at lines 1078 and 1470; "Theoretical Properties" subsection must be checked against the no-theoretical-convergence-claims exclusion (`phase_04/novelty_scope.md`) |
| `papers/sections/performance.tex` | 34.3 KB | Setup, per-suite results, statistics, convergence | **VIOLATIONS:** `\subsection{Component and Overlay Ablations}` (line 639) and `\subsection{Parametric Component Study}` (line 622) are main-text ablation/component content — must be removed (supplement-only, Phase 12); labels duplicated with supplementary_content.tex (`sec:exp:h2h`, `sec:exp:cec2011`, `sec:exp:gsk_family`, `sec:exp:ablation`, `sec:exp:traces`, `sec:exp:parametric`) |
| `papers/sections/conclusions.tex` | 5.1 KB | Conclusions draft | Rewrite to Dim 21 four-movement structure with headed limitations paragraph |
| `papers/sections/supplementary_content.tex` | 44.2 KB | Per-function tables, tuning disclosure, traces, ablation scaffolding | **VIOLATION:** `\subsection{CEC~2013: External Hold-Out}` (line 234) — prohibited terminology; must become "second comparison suite" |
| `papers/supplementary.tex` | 7.3 KB | Supplement wrapper | Relabel to the S1–S6 / A.n–B.n scheme (Dim 20) |

### 0.2 Reconciliation of task-requested homes with the frozen five-section spine

The presentation-conventions register (Dim 1, FROZEN under CR-0003) fixes a five-section
spine. The task-requested content homes map into it as follows (conformance, not
deviation):

| Requested home | Placement in frozen spine | Convention |
|---|---|---|
| Introduction | Section 1 | Dim 3, 5 |
| Related Work | Section 2 | Dim 4, 6 |
| DT-GSK method (notation, scaffold, SGSM, polish, complexity, accounting) | Section 3 | Dim 7, 8, 9, 10 |
| Experimental Setup | Section 4.1 | Dim 11 |
| Results and Analysis (per-suite) | Sections 4.2–4.6 | Dim 2, 12–16 |
| Discussion | Section 4.7 (consolidating discussion subsection) | Dim 17 |
| Limitations | Headed limitations paragraph inside Section 5 | Dim 18 |
| Conclusions | Section 5 | Dim 21 |
| Data/Code Availability | MDPI back matter (unnumbered) | Dim 19, 22 |

**One recorded justified improvement under CR-0003:** subsection 2.2 ("Structure
learning outside the GSK family") has no exemplar antecedent; it is added because the
bounded-gap argument (thesis.md §2) requires positioning C1/C2 against differential
grouping, CMA-ES, and eigenvector crossover, and the novelty-defense table in
`phase_04/novelty_scope.md` needs a main-text home. Recorded here as the justification;
no change-request needed because the register explicitly permits "a recorded justified
improvement".

---

## 1. Main-text outline

Abstract (unnumbered). ~200 words. Objective: problem, C1–C4 in one sentence each,
panel scope, suites, placeholder-bound headline (`<T05:friedman_rank_overall>` slot
wording; verified ranks only, marked for Phase-6 re-derivation). Conventions: Dim 3
(suite names must match intro/bullets exactly), Dim 5 (no numeric superiority claims).
Citations: none (MDPI abstract convention). Risk: overclaim — mitigated by
placeholder discipline and "within the GSK family panel" scoping.

### Section 1 — Introduction (~1,000 words; no numbered subsections)

Conventions: **Dim 3 (funnel ≤ ~1.5 pages), Dim 5 (contribution bullets), Dim 2
(roadmap as final paragraph, full sentences).**

Planned paragraph blocks:

1. **Funnel** (~350 w): optimization → metaheuristics (brief, no taxonomy tables) → GSK
   family → evidence-locatable weaknesses of family members, each mapped one-to-one to a
   named DT-GSK subsystem. Evidence: thesis.md §1–§2. Citations: yao1999evolutionary,
   hussain2019metaheuristic, mohamed2020gaining, wolpert1997nfl, awad2016problem,
   das2011cec2011. Risk: generic filler (ATMALS-GSK weakness) — cap enforced.
2. **Positioning teaser** (~200 w): why AGSK/APGSK/FDB-AGSK/eGSK/ATMALS-GSK do not
   already close the gap (scalar-parameter/donor-policy adaptation vs accepted-move
   interaction structure). Evidence: thesis.md §2. Citations: mohamed2020agsk,
   mohamed2021novel, fdbagsk2023, jawad2024egsk, alfadli2025atmals. Risk: "ISM is DG
   re-badged" — defer full defense to 2.2/2.3.
3. **Contribution bullets** (~250 w): exactly four bullets = C1, C2, C3, C4 from
   `contribution_matrix.md`; mechanism bullets first, validation bullet (C4 + protocol)
   last; persistent subsystem identifiers (ISM/SGSM, eigenframe polish, ACE, ARGP,
   NLPSR, BSE); validation bullet names panel + suites, carries NO numbers. Evidence:
   contribution_matrix.md. Citations: none new. Risk: naming drift — single grep-clean
   "DT-GSK" spelling (Dim 5).
4. **Roadmap** (~100 w): full-sentence roadmap (Dim 2).

### Section 2 — Related Work (GSK family) (~1,500 words)

Conventions: **Dim 6 (typology + summary table + critical sentences), Dim 4 (positioning
subsection, gaps as technical deficiencies within the family, no outcome claims).**

- **2.1 GSK-family enhancement typology** (~850 w). Objective: typology-organized
  review; every reviewed variant gets ≥ 1 critical sentence (what it does not solve);
  includes exhibit **X2**: summary table `variant | core mechanism | suites tested | key
  limitation`. Evidence: evidence cards in `papers/governance/evidence_cards/`.
  Citation shortlist (family + close context): mohamed2020gaining, mohamed2020agsk,
  mohamed2021novel, apgsk2021, apgsk_imode2024, fdbagsk2023, jawad2024egsk,
  alfadli2025atmals, nomer2021gskrl, zhong2021gskhho, navaneetha2022gskde,
  arini2022gjojos, jalali2021opposition, chalabi2023mogsk, ma2023mgskdpmo, pogsk2023,
  epd_gsk2024, hpe_agsk2025, liang2024gskwoa, nabahat2024hybrid, tang2024fowfo,
  zhou2021iade, brest2017single, awad2017ensemble, mohamed2017lshadespacma,
  storn1997differential. Risk: synthesis-free cataloguing (eGSK weakness) — critical
  sentence rule.
- **2.2 Structure learning outside the GSK family** (~250 w) — *recorded justified
  improvement, see 0.2*. Objective: bound the gap — DG's offline O(n²/m)-evaluation
  probing, CMA-ES covariance adaptation, per-generation eigenvector crossover vs ISM's
  zero-extra-objective-evaluation accepted-move graph (never worded "free"; compute cost
  cited from `phase_03/complexity_analysis.md`). Evidence: thesis.md §2; novelty table
  in `phase_04/novelty_scope.md`. Citations: omidvar2014dg, hansen2001cmaes, guo2015eig,
  kolda2003directsearch, nelder1965simplex. Risk: C1 novelty challenge — this is the
  four-dimension comparison home (update trigger, evaluation cost, what is learned, how
  exploited).
- **2.3 Positioning of DT-GSK against the GSK family** (~400 w). Objective: named gap
  subsection; each gap traceable to reviewed variants and tied to the subsystem that
  addresses it; NO outcome claims (gap argues need; Section 4 argues effect). Evidence:
  thesis.md §2; contribution_matrix.md. Citations: subset of 2.1 keys. Risk:
  ATMALS-style pre-results overclaim — banned wording enforced.

### Section 3 — Proposed DT-GSK (~3,300 words)

Conventions: **Dim 7 (recap → one subsection per mechanism → worked example → shared
machinery once), Dim 8 (frozen symbol table, numbered equations + "where" clauses,
constants justified or labeled frozen defaults), Dim 9 (typeset line-numbered
algorithms, Inputs/Output contracts, pseudocode = parameter table), Dim 10 (two
parameter tables as single source of truth).** All content drawn from the frozen
Phase-3 method artifacts (`phase_03/parameter_table.md`, `phase_03/complexity_analysis.md`,
`algorithm_freeze_manifest.json`), never re-derived. Exhibits: **X1** nomenclature/symbol
table; **X3** worked numeric example (tier gating/scheduling); **X4** DT-GSK parameter
table with provenance; **X5** panel-settings table (7 algorithms; = exhibit `T-PANEL`);
**A1** DT-GSK pseudocode (the SINGLE algorithm float, exhibit `A1`/`alg:dt-gsk`; the
inherited base-GSK operator is specified by equations `E1a`–`E3`, no second float);
**X6** architecture figure (= exhibit `F-ARCH`). Cross-map: X1=`T-NOTATION`,
X2=`T-FAMREV`, X3=`T-WORKED`, X4=`T-PARAMS`.

- **3.1 Notation and base-GSK recap** (~450 w). Objective: symbol table X1 + numbered
  junior/senior equations; inherited-unchanged framing (no new base operator claimed).
  Evidence: phase_03 method artifacts; contribution_matrix rejected rows 1–4.
  Citations: mohamed2020gaining, tanabe2014improving. Risk: notation drift (all three
  exemplars) — scripted notation audit is a pre-submission gate (Dim 8).
- **3.2 Architecture overview and execution order** (~300 w). Objective: X6 figure +
  explicit subsystem execution order in prose AND pseudocode (Dim 7.v); dimension-tier
  gating stated once. Evidence: docs/algorithms/dt-gsk.md; phase_03 artifacts.
  Citations: none new. Risk: "grab-bag" impression — tier-resolved single `pub` profile
  stated up front.
- **3.3 Dimension-tiered adaptive scaffold (C3)** (~800 w total). Objective: honest
  MOD/ORI labeling per sub-mechanism; "control, budget, structure-memory, and polish
  layered on the GSK scaffold" wording; NLPSR never claimed new.
  - 3.3.1 ACE bandit control (~200 w) — citations: mohamed2020agsk, tanabe2013shade,
    auer2002finite, fialho2010adaptive.
  - 3.3.2 ARGP pruning (~100 w; ORI) — citations: none beyond family context.
  - 3.3.3 NLPSR floor (~130 w; MOD, explicitly not new) — citations: mohamed2020agsk,
    tanabe2014improving.
  - 3.3.4 BSE + elite archive (~250 w; hard-capped budget safety) — citations:
    zhang2009jade, tanabe2013shade, storn1997differential.
  - 3.3.5 Deep-stall restart with global-best invariant (~120 w).
  Evidence: C3 row; `<T05:friedman_rank_D10>`, `<T05:friedman_rank_D30>` footprint
  stated only as evidence *plan*. Risk: "unclear individual value" — individual value
  explicitly `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY` (stated in one sentence, pointing
  to supplement S6).
- **3.4 Interaction-structure memory (ISM/SGSM) and linkage-aware exploitation (C1)**
  (~650 w). Objective: decaying (λ = 0.95) accepted-move pair graph;
  confidence/evidence gating; D ≥ 50 activation; exploitation via linkage blocks +
  top-k-block subspace; "no extra objective evaluations" with compute cost cited —
  never "free". Evidence: C1 row; phase_03/complexity_analysis.md. Citations:
  omidvar2014dg, guo2015eig, hansen2001cmaes, mohamed2020gaining. Risk: DG/CMA
  re-badge — 2.2 comparison table cross-referenced.
- **3.5 Eigenframe final polish (C2)** (~350 w). Objective: one-shot RNG-free compass
  search on the ISM eigenbasis; strict budget accounting; byte-identical
  whether it fires or not; no convergence guarantee claimed. Evidence: C2 row.
  Citations: kolda2003directsearch, nelder1965simplex, gao2012implementing. Risk:
  "local-search bolt-on" — differentiator = learned basis + determinism.
- **3.6 High-dimensional controllers (method detail, D ≥ 100)** (~200 w). Objective:
  A1/A2/FC4, basin memory, SP-NLPSR, TERRA documented as protections under C3's scope,
  NOT headline contributions (rejected row 14). Citations: none new. Risk: dilution of
  C1–C3 — explicitly demoted.
- **3.7 Parameter configuration and profile lock** (~250 w). Objective: X4 + X5 tables;
  tier-resolved `pub` profile, hash-frozen (`algorithm_freeze_manifest.json`); values =
  single source of truth for pseudocode and prose (Dim 9/10 cross-consistency gate).
  Evidence: phase_03/parameter_table.md; C4 row. Citations: family keys for comparator
  settings provenance (mohamed2020gaining, mohamed2020agsk, mohamed2021novel,
  fdbagsk2023, jawad2024egsk, alfadli2025atmals). Risk: ATMALS-style
  table-vs-pseudocode contradiction — mandatory cross-consistency check.
- **3.8 Complexity and evaluation accounting** (~300 w). Objective: per-generation
  compute cost of each subsystem (from `phase_03/complexity_analysis.md`); strict FES
  accounting path (every objective evaluation counted, BSE hard caps, polish budget
  slice); self-init documented as the fair-start protocol exception (rejected row 16 →
  protocol exhibit `<T07>`). Citations: mohamed2020gaining, david_order_statistics (if
  the frozen complexity artifact uses it; else drop). Risk: hidden-cost suspicion —
  compute cost stated, runtime exhibit promised in 4.6.

### Section 4 — Experimental Study (~3,400 words)

Conventions: **Dim 2 (identical per-suite rhythm; complexity/runtime as its own
subsection after all suites; orientation paragraph at section start), Dim 11 (full
protocol disclosure), Dim 12 (five-statistic + compact panel summary main-text floor),
Dim 13 (Wilcoxon+Holm — the recorded improvement over all three exemplars — plus
Friedman/Iman–Davenport), Dim 14 (table caps), Dim 15 (log-scaled in-paper convergence
subset, all 7 algorithms), Dim 16 (figure placement/pairing), Dim 17 (embedded
interpretation + consolidating discussion).**

- **4.1 Experimental setup** (~600 w). Objective: suites (CEC2017 primary; CEC2011
  real-world; CEC2013 **second comparison suite** — never "independent"/"holdout");
  F2 exclusion WITH stated reason; dimensions, run counts (51/25), MaxFES, error
  metric/zeroing threshold; 7-algorithm panel; all results from in-repository re-runs
  under identical protocol from release rel-2026-07-10-262fc16c9 (eGSK reference-CSV
  provenance note per data ledger); paired optimizer-independent seed schedule + shared
  X0 with the documented DT-GSK self-init exception; hardware/OS/language/libraries;
  statistics protocol with hypotheses stated once and software named. Exhibit:
  `<T07:protocol_reproducibility_summary>`. Evidence: thesis.md §4, §6; C4.
  Citations: awad2016problem, das2011cec2011, liang2013cec2013, wilcoxon1945individual,
  holm1979simple, friedman1937use, demsar2006statistical, vargha2000critique,
  efron1993introduction. Risk: parity challenge — in-repo re-runs + release id +
  per-cell checksums.
- **4.2 CEC2017 results** (~850 w). Rhythm: proposal five-statistic results →
  family-panel comparison → statistics (Dim 2).
  - 4.2.1 DT-GSK five-statistic results (~250 w): main text carries the condensed
    headline summary `T01-SUM` (per-dimension descriptive stats + W/T/L); the complete
    per-function five-statistic tables (`T01-D10..D100`, best/median/mean/worst/SD)
    live in S1 (Dim 12 floor satisfied by T01-SUM + statistics rows in place);
    class-wise narrative (unimodal/multimodal/hybrid/composition), no raw
    function-ID win lists.
  - 4.2.2 Family-panel comparison (~250 w): compact panel summary per Dim 12/14 is
    `T01-SUM` itself (aggregate per dimension; full per-function head-to-heads → S1);
    companion rank bar chart `F05-RANKBAR` (Dim 16); convergence subset
    `F02-MAIN-D30`/`F02-MAIN-D100` adjacent to claims (Dim 15).
  - 4.2.3 Statistical analysis (~350 w): `<T02:wilcoxon_holm_pairwise>` (R+, R−, p,
    W/T/L, decision at α = 0.05, Holm-corrected; p < 1e-4 bounding, never "0.0000");
    `<T03:a12_cliffs_bca>`; combined Friedman table `<T05>` (overall + per-dimension,
    Iman–Davenport; eGSK layout); Nemenyi CD diagrams `<F01>`; rank-vs-dimension trend
    `<F03>`. No pooled-dimension tests.
  Evidence: C1/C3 primary-evidence slots; verified ranks (#1 overall by mean+median;
  #1 D10/D50/D100; #2 D30 behind eGSK) stated ONLY with the Phase-6 re-derivation mark.
  Citations: statistics keys above. Risk: D30 unfavorable cell — named and discussed,
  not skipped (Dim 17).
- **4.3 CEC2011 results** (~450 w). Same internal rhythm compressed: `T04` panel
  results table + `F04-CEC2011` rank figure + Wilcoxon/Holm + Friedman rows (full
  inferential detail `T04-STATS` → S2; full convergence grids → S3, no CEC2011
  main-text convergence). Verified rank statement (#2 in family, Phase-6 re-derivation mark), stated
  alongside — not after — the favorable CEC2017 cells. Citations: das2011cec2011 +
  statistics keys. Risk: real-world generalization — scope wording.
- **4.4 CEC2013 second comparison suite** (~400 w). Same rhythm; `<T06>`. NEVER
  "independent"/"holdout"/"validation" (terminology binding; no development-history
  independence evidence). Citations: liang2013cec2013 + statistics keys. Risk:
  reviewers asking why a third suite — framed as breadth within the same protocol.
- **4.5 Convergence analysis** (~350 w). Objective: per-checkpoint mean-across-runs
  family-overlay curves (Section 6.7 default; pre-registered P2 in exhibit_plan.csv),
  pre-registered function selection (rule P5: featured dimensions D30 + D100), log-error
  y-axis, all 7 panel algorithms (`F02-MAIN-D30`/`F02-MAIN-D100`; full sets → S3).
  Mechanism-trajectory figures are supplement-designated (`F-TRACE`/`F-ADAPT`,
  diagnostic-release-gated) — behavior illustration only, NOT component-contribution
  evidence (Dim 15). Every convergence claim verifiable from an in-paper figure.
  Risk: claim-behind-supplement (GSK/eGSK weakness) — in-paper subset rule.
- **4.6 Runtime and complexity in practice** (~250 w). Objective: own subsection after
  all suites (Dim 2; fixes GSK's wedged placement); wall-clock/overhead exhibit
  grounding any later overhead statement (Dim 18.iii). Evidence: release environment
  records. Citations: none new. Risk: "hidden cost" — measured, not asserted.
- **4.7 Discussion** (~500 w). Objective: consolidating subsection structured by (i)
  function class, (ii) dimension scaling, (iii) aggregate counts; every sentence tied
  to a named exhibit; mechanism-*plausibility* wording only (design intent), NO measured
  component contributions (all `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`, one pointer
  sentence to S6); unfavorable cells (D30 vs eGSK; CEC2011 #2) named; superlatives
  without exhibits banned; scope always "within the GSK family panel". Citations:
  wolpert1997nfl (scope bounding). Risk: descriptive-only discussion (all three
  exemplars) — mechanism-plausibility frame.

**No 4.8. Explicitly: no ablation subsection, no parametric/component study, no
sensitivity study in Section 4 or anywhere in the main text.** (The existing
`performance.tex` subsections at lines 622 and 639 are removed in the Phase 8 rewrite.)

### Section 5 — Conclusions (~650 words)

Conventions: **Dim 21 (four movements), Dim 18 (headed limitations paragraph).**

1. Design recap, no metaphor re-narration (~150 w).
2. Quantitative summary via exhibit-bound placeholders; ratio computation defined at
   first use; ties/unfavorable cells stated alongside favorable; panel scope; verified
   ranks only, Phase-6 re-derivation mark (~150 w).
3. **Limitations (headed paragraph, ~200 w):** (i) mechanism-specific limitations with
   concrete failure modes (ISM needs accepted-move signal; polish is one-shot; D ≥ 50
   gating means low-D tiers rely on the scaffold alone); (ii) where DT-GSK does not
   lead (D30 behind eGSK; CEC2011 #2 — re-derivation mark); (iii) scope of validity
   (panel-relative, suites tested, D ≤ 100, no LSGO claim); any overhead limitation
   grounded in the 4.6 exhibit or not claimed.
4. Mechanism-anchored future work + code/data pointer (~150 w).

Citations: none new. Risk: verbatim repetition of Section 4 (ATMALS weakness) —
paraphrase rule + parallel-text audit (Dim 22).

### Back matter (unnumbered; MDPI apparatus, Dim 19/22) (~150 words)

Author Contributions; Funding; **Data Availability** (durable public code repository
reference, pinned evidence release rel-2026-07-10-262fc16c9, seed policy, per-run raw
results, environment/verification manifests — accurate, never boilerplate); Conflicts
of Interest. Evidence: C4. Risk: eGSK-style misleading data statement — accuracy rule.

---

## 2. Supplement outline (S1–S6; Dim 20 labeling: A.n tables, B.n figures, one artifact per campaign–dimension cell, cited by exact label)

Canonical source: `papers/supplementary.tex` (+ `papers/sections/supplementary_content.tex`).
Main text must remain auditable without the supplement (Dim 20 floor).

- **S1 — CEC2017 full per-function panel tables.** Per-dimension per-function
  7-algorithm head-to-heads (five statistics; A.n). Feeds 4.2.2. Placeholders: `<T01>`
  extensions.
- **S2 — CEC2011 and CEC2013 full per-problem panel tables.** Same scheme (A.n). Feeds
  4.3/4.4. Placeholders: `<T04>`, `<T06>` extensions.
- **S3 — Full convergence figure sets.** Complete function × dimension coverage, all 7
  algorithms, log-error axes (B.n; one artifact per campaign–dimension cell). Feeds 4.5.
  Placeholder: `<F02>` full sets.
- **S4 — Complete statistical workbooks.** Per-function Wilcoxon/Holm detail, full
  A12/Cliff's + BCa tables, win/tie/loss matrices, Friedman/Iman–Davenport detail.
  Feeds 4.2.3/4.3/4.4. Placeholders: `<T02>`, `<T03>`, `<T05>` extensions.
- **S5 — Reproducibility bundle.** Seed policy and paired schedule specification,
  environment/verification manifests, release manifest for rel-2026-07-10-262fc16c9,
  profile-lock detail, tuning-protocol disclosure (reusing audited
  `supplementary_content.tex` §Tuning material), self-init exception documentation.
  Feeds 4.1 and C4.
- **S6 — RESERVED: Ablation study. `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`.** Populated
  only at Phase 12 with exhibits SA01 (scaffold ablation matrix), SA02 (SGSM-overlay
  `full`/`no-adaptive`/`no-sgsm` cells), SA03 (full-vs-cell Wilcoxon/Holm). Until
  Phase 12 this section carries only its reservation notice. No main-text section
  depends on S6 for any claim.

---

## 3. CR-0003 conformance map (every main-text section → convention)

| Manuscript unit | Dimensions followed | Deviations/improvements |
|---|---|---|
| Abstract | 3, 5 | none |
| 1 Introduction | 2 (roadmap), 3, 5 | none |
| 2 Related Work | 4, 6 | 2.2 added — recorded justified improvement (see 0.2) |
| 3 Proposed DT-GSK | 7, 8, 9, 10 | none |
| 4.1 Setup | 11, 13 (protocol part) | none |
| 4.2–4.4 Per-suite results | 2, 12, 13, 14, 16 | Holm correction = the register's own recorded improvement over all three exemplars (Dim 13) |
| 4.5 Convergence | 15, 16 | none |
| 4.6 Runtime | 2 (own subsection after suites) | none |
| 4.7 Discussion | 17 | none |
| 5 Conclusions | 18, 21 | none |
| Back matter | 19, 22 | none |
| Supplement S1–S6 | 20 | none |
| Whole manuscript | 22 (cross-consistency + parallel-text audits), 8 (notation audit) | none |

---

## 4. Global bindings restated

1. **No ablation subsection in the main text** — S6 only, Phase 12 only.
2. All numbers are exhibit-bound placeholders until Phase 6; only the verified
   family-panel ranks may be repeated, always with the re-derivation mark.
3. All comparisons "within the GSK family panel"; no field-wide claims; CEC2013 is the
   "second comparison suite".
4. Citations only from `papers/governance/allowed_citation_keys.txt` (all shortlists
   above are subsets of the 57 keys).
5. Word budgets here are the working targets; page arithmetic and overflow policy live
   in `phase_04/page_budget.md`.
