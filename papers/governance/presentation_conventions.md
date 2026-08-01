# Presentation Conventions Register — DT-GSK Manuscript

**Status: FROZEN at Phase 4 (CR-0002, CR-0003).**
**Scope:** binding presentation conventions for the DT-GSK manuscript (target venue: MDPI *Algorithms*, repository-wired via `papers/Definitions/mdpi.cls`).
**Exemplars reviewed:** `mohamed2020gaining` (original GSK, Springer IJMLC), `alfadli2025atmals` (ATMALS-GSK, MDPI *Algorithms* — same venue as target), `jawad2024egsk` (eGSK, Elsevier RICO).

The three Section-8.7 exemplars are **calibration references, never content templates**. No sentence, table layout, figure, or argumentative structure is to be copied mechanically from any of them; they exist to calibrate what "publishable in this literature" looks like, where each one succeeds, and where each one demonstrably fails. For every presentation dimension below, the register records what each exemplar does, then fixes ONE adopted convention for DT-GSK that combines the strongest observed practices and improves on them where the improvement is justified (e.g., adding the multiple-comparison correction that all three exemplars omit). Where the adopted convention touches empirical content, it inherits the Phase-4 binding constraints: numeric slots are exhibit-bound placeholders (e.g., `<T05:friedman_rank_D30>`), comparative wording is always "within the GSK family panel", and any component-contribution material is `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY` with **no ablation subsection in the main manuscript**.

---

## 1. Paper structure

| Field | Convention |
|---|---|
| GSK practice | 4 top-level sections, deep numbering only inside experiments; 28 tables, 29 pages; survey folded into a ~5-page introduction; no related-work/discussion/limitations sections. |
| ATMALS-GSK practice | 5-section spine with disciplined 3-level numbering over 64 pages; but all raw tables in main text (~40-page experimental section), no supplement. |
| eGSK practice | 6 sections, clean 3-level numbering, component analysis isolated after headline comparisons; but Section 5 mistitled ("parametric study" for what is an ablation). |
| **ADOPTED for DT-GSK** | Five numbered top-level sections — 1 Introduction, 2 Related Work (GSK family), 3 Proposed DT-GSK, 4 Experimental Study, 5 Conclusions — with at most 3-level numbering and one addressable subsection per mechanism and per comparison campaign. Raw per-function grids and full convergence sets go to a systematically labeled supplement, keeping the main text well under the ATMALS-GSK extreme. Section titles must state exactly what the section contains. **No ablation subsection anywhere in the main manuscript** (ablation is `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`). |
| Weakness to avoid | ATMALS-GSK's supplement-free 40-page table wall; eGSK's misleading section title; GSK's missing related-work/limitations homes. |

## 2. Section ordering

| Field | Convention |
|---|---|
| GSK practice | Suite-by-suite symmetry (own results, then comparison, per suite); but algorithm complexity wedged between the two suites, breaking the flow. |
| ATMALS-GSK practice | Progressive comparison-widening (baseline → family → field → statistics → component study); double roadmap (end of Sec 1, start of Sec 4.1); component study arrives last, after statistics. |
| eGSK practice | Own-results-first → family comparison → field comparison → ablation; roadmap paragraph degrades into sentence fragments. |
| **ADOPTED for DT-GSK** | Order: introduction → related work → base-GSK recap → DT-GSK design → experimental setup → per-suite results with identical internal rhythm for CEC2017 and CEC2011 (proposal five-statistic results, then family-panel comparison, then statistics), then CEC2013 presented as the **second comparison suite** (never "independent"/"holdout") with the same rhythm → runtime/complexity as its **own** subsection after all suites → conclusions. Roadmap paragraph at the end of the introduction and a one-paragraph orientation at the start of the experimental section; both proofread as full sentences. |
| Weakness to avoid | GSK's complexity subsection interrupting the suite sequence; eGSK's fragmentary roadmap. |

## 3. Introduction strategy

| Field | Convention |
|---|---|
| GSK practice | Data-backed funnel, but ~4 pages of taxonomy tables inside the introduction; citation-count figures that date quickly. |
| ATMALS-GSK practice | Funnel lands on algorithm-specific weaknesses that map one-to-one onto the proposed mechanisms; but two pages of generic filler and a suite-name internal inconsistency. |
| eGSK practice | Fast funnel to a single concrete failure mode (premature convergence) that all modifications target; but no positioning against existing GSK variants. |
| **ADOPTED for DT-GSK** | A funnel of at most ~1.5 pages that moves: optimization → metaheuristics (brief, no taxonomy tables) → GSK family → the specific, evidence-locatable weaknesses of existing family members that DT-GSK's subsystems address, each weakness mapped one-to-one to a named subsystem. Include explicit positioning against the existing GSK variants in the panel (why AGSK/APGSK/FDB-AGSK/eGSK/ATMALS-GSK do not already close the gap). Every suite name mentioned in the introduction must match the abstract and the contribution bullets exactly. No result claims before Section 4 other than exhibit-bound placeholders. |
| Weakness to avoid | GSK's introduction bloat; ATMALS-GSK's abstract/intro suite inconsistency and generic filler; eGSK's missing variant positioning. |

## 4. Research-gap formulation

| Field | Convention |
|---|---|
| GSK practice | Quantified, visualized category-scarcity gap — verifiable but not a technical deficiency argument. |
| ATMALS-GSK practice | Three explicit gaps re-argued in a named positioning subsection (2.3); but asserted field-wide without evidence and closed with an outcome overclaim before results. |
| eGSK practice | Single unifying failure mode giving the paper coherence; but asserted in two sentences, disconnected from the 23-work review. |
| **ADOPTED for DT-GSK** | A named positioning subsection at the end of Related Work ("Positioning of DT-GSK against the GSK family") stating each gap as a concrete technical deficiency **within the GSK family panel**, each gap (i) traceable to the reviewed variants and (ii) tied to the specific DT-GSK subsystem that addresses it. No field-wide deficiency claims, no outcome claims of any kind inside the gap statement — the gap section argues need, Section 4 argues effect. |
| Weakness to avoid | ATMALS-GSK's pre-results "significantly outperforms" overclaim; eGSK's review/gap decoupling; GSK's metaphor-scarcity (rather than technical) gap. |

## 5. Contribution presentation

| Field | Convention |
|---|---|
| GSK practice | No contribution list; one crisp single-claim framing, but specific novelties hard to locate and cite. |
| ATMALS-GSK practice | Five bullets restated argumentatively in Sec 2.3; but naming drift ("ATM-GSK" vs "ATMALS-GSK") in the bullets and result claims embedded in the final bullet. |
| eGSK practice | No bulleted list, but persistent component IDs (eGSK_1/2/3) carried from method subsections into ablation tables and figures — exact contribution-to-evidence traceability. |
| **ADOPTED for DT-GSK** | An explicit bulleted contribution list (3–5 bullets) at the end of the introduction: mechanism contributions first, one validation bullet last. Each mechanism bullet names its subsystem with a persistent identifier used verbatim in the method section, the exhibits, and the (Phase-12, supplement-only) ablation. The algorithm name is "DT-GSK" everywhere — a single grep-clean spelling across abstract, bullets, body, tables, figures, and supplement. The validation bullet states scope ("within the GSK family panel", suites named) and carries **no** numeric or superiority claims — numbers live in exhibit-bound placeholders in Section 4. |
| Weakness to avoid | ATMALS-GSK's naming drift in the most-quoted paragraph and result claims inside contribution bullets; GSK's/eGSK's missing scannable list. |

## 6. Literature-review organization

| Field | Convention |
|---|---|
| GSK practice | Taxonomy-with-tables, highly skimmable, feeds the gap; but pure cataloguing of ~139 one-line entries with zero critical analysis. |
| ATMALS-GSK practice | Typology-driven family review (four named enhancement categories, each a numbered subsection) plus closing positioning subsection; but prose-only, no comparison table. |
| eGSK practice | Comprehensive chronological catalog of ~23 GSK works; but year-by-year with zero synthesis, never identifies open problems. |
| **ADOPTED for DT-GSK** | A typology-organized review of the GSK family (named enhancement categories as numbered subsections, in the ATMALS-GSK style) **plus** one compact summary table with columns variant | core mechanism | suites tested | key limitation — the table neither exemplar with a family review provides. Every reviewed variant gets at least one critical sentence (what it does not solve), and the review closes with the positioning subsection of Dimension 4. Citations only from `papers/governance/allowed_citation_keys.txt`. |
| Weakness to avoid | eGSK's synthesis-free chronological list; GSK's cataloguing without mechanism analysis; ATMALS-GSK's missing comparison table and near-empty typology category. |

## 7. Algorithm explanation

| Field | Convention |
|---|---|
| GSK practice | Metaphor → math → worked numeric example (Table 5) → pseudocode → flowchart pipeline; but repetitive metaphor narration and update rules never set as numbered equations. |
| ATMALS-GSK practice | One-subsection-per-mechanism decomposition with worked numeric illustration (Table 2) and visualizations of the tuning machinery itself (Figs 4–6); but near-duplicate text across mechanism subsections. |
| eGSK practice | Base-GSK recap with equations and worked-example table; one motivation paragraph per component; but unjustified design constants and component execution order recoverable only from the pseudocode figure. |
| **ADOPTED for DT-GSK** | Structure: (i) base-GSK recap subsection with numbered equations (drawn from the frozen Phase-3 method artifacts, not re-derived); (ii) one subsection per DT-GSK subsystem, each opening with a one-paragraph motivation and closing with its numbered display equations; (iii) one worked numeric example table for the dimension-scheduling/gating machinery; (iv) shared machinery stated **once** and cross-referenced, never re-narrated per subsection; (v) subsystem execution order stated explicitly in prose *and* in pseudocode; (vi) every design constant either justified in one sentence or explicitly labeled as a frozen default with its provenance. Metaphor language is used at most once, in the introduction. |
| Weakness to avoid | ATMALS-GSK's duplicated Gaussian-machinery text; GSK's metaphor repetition and equation-free update rules; eGSK's unjustified magic constants and prose-invisible execution order. |

## 8. Mathematical notation

| Field | Convention |
|---|---|
| GSK practice | Small parameter vocabulary with plain-language role sentences; but N vs NP, k vs K collisions and a table misprint. |
| ATMALS-GSK practice | Only 8 numbered equations with immediate inline definitions; but casing drift (Kf/KF, Kr/KR), a "PSL" typo, and an equation-vs-text direction contradiction (Eq 7). |
| eGSK practice | Consistent equation-then-"where"-clause pattern, nothing undefined at point of use; but K/k, K_r/k_r, N/NP drift and an unexplained 0.01 constant. |
| **ADOPTED for DT-GSK** | One frozen symbol table (nomenclature) fixed from the Phase-3 method artifacts before drafting; every symbol has exactly one casing and one meaning across prose, equations, tables, pseudocode, and figures. All update rules appear as numbered display equations, each immediately followed by a "where ..." sentence (eGSK pattern). No constant appears in an equation without a rationale sentence or an explicit frozen-default label. A scripted grep-level notation audit (symbol list vs manuscript) is a mandatory pre-submission gate. |
| Weakness to avoid | The N/NP and K/k collisions present in **all three** exemplars; ATMALS-GSK's formula/text direction contradiction. |

## 9. Pseudocode design

| Field | Convention |
|---|---|
| GSK practice | Line-numbered, compact, per-phase blocks plus flowchart; but set as figure images — glyphs degrade, one numbering slip. |
| ATMALS-GSK practice | Boxed algorithm environments with Inputs/Output contract headers and equation cross-references inside lines; but the initialization block contradicts the parameter table on four of five parameters. |
| eGSK practice | Pseudocode-plus-flowchart pairing; but bitmap figure, no line numbers, never referenced line-by-line from text. |
| **ADOPTED for DT-GSK** | Typeset, line-numbered `algorithm` environments (never bitmap figures): one for the base-GSK loop (recap) and one for DT-GSK, each opening with an explicit Inputs/Output contract block and citing equation numbers inside the relevant lines (ATMALS-GSK pattern). Any initialization values shown in pseudocode must be generated from / checked against the parameter table of Dimension 10 — a mandatory cross-consistency check, since ATMALS-GSK's failure here makes its configuration ambiguous. A flowchart may complement but never replace the typeset pseudocode. |
| Weakness to avoid | GSK's and eGSK's image-set pseudocode; ATMALS-GSK's pseudocode-vs-table parameter contradictions. |

## 10. Parameter documentation

| Field | Convention |
|---|---|
| GSK practice | One consolidated table for all 11 algorithms' settings with rationale notes; but no sensitivity analysis or tuning protocol for its own parameters. |
| ATMALS-GSK practice | Fixed-vs-adaptive parameter table with ranges, initial values, and discretization grids; but the grids conflict with the pseudocode and competitor settings are never tabulated. |
| eGSK practice | Full settings for the proposal and all family competitors, with explicit rationale for the competitor configuration chosen; but no sensitivity analysis despite a "parametric study" title. |
| **ADOPTED for DT-GSK** | Two tables: (i) an DT-GSK parameter table listing every parameter, its value/range, and one-line provenance (inherited GSK default vs DT-GSK-specific, with source in the frozen Phase-3 artifacts); (ii) a consolidated panel-settings table for all 7 family-panel algorithms with each competitor's configuration and its source stated (GSK/eGSK pattern). Values in these tables are the single source of truth — pseudocode and prose must match them exactly. Parameter-sensitivity or component-contribution evidence is **not** claimed in the main text; any such material is `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`. |
| Weakness to avoid | ATMALS-GSK's table-vs-pseudocode grid conflicts and missing competitor table; eGSK's sensitivity-free "parametric study" mislabel. |

## 11. Experimental setup

| Field | Convention |
|---|---|
| GSK practice | Exhaustive protocol disclosure — runs, FES budgets, error thresholding, f2 exclusion with reason, score formulas, hardware/software (no weakness noted). |
| ATMALS-GSK practice | Every protocol number anchored to the official CEC technical reports; comparator pool explicitly split family vs external; but no hardware/software/runtime, silent f2 omission, re-run-vs-copied unstated. |
| eGSK practice | Explicit CEC-2017 rule compliance with all constants in one subsection plus named platform; but external competitors' numbers copied from literature (parity unverifiable) and f2 exclusion unexplained. |
| **ADOPTED for DT-GSK** | One setup subsection stating, with citations to the official suite reports where applicable: suites (CEC2017, CEC2011, and CEC2013 as the second comparison suite), function counts including any exclusion **with its stated reason**, dimensions, run counts, FES budgets, error metric and zeroing threshold, and the full 7-algorithm family panel (gsk, agsk, apgsk, fdb-agsk, egsk, atmals-gsk, dt-gsk). State explicitly that all panel results are produced by in-repository re-runs under an identical protocol from release rel-2026-07-10-262fc16c9 (never literature-copied numbers presented as comparable), and name hardware, OS, language, and library environment. Comparative scope wording: "within the GSK family panel". |
| Weakness to avoid | ATMALS-GSK's missing platform and silent exclusions; eGSK's literature-copied competitor numbers without a parity caveat. |

## 12. Benchmark reporting

| Field | Convention |
|---|---|
| GSK practice | Five-statistic self-report (best/median/mean/worst/SD) making the paper reusable as a comparison source; class-wise narrative; but comparison tables drop to mean±SD and repeat the GSK column across paired tables. |
| ATMALS-GSK practice | Five-statistic head-to-heads plus complete per-function coverage at all dimensions, nothing cherry-picked; but everything in the main text and formatting slips inside tables. |
| eGSK practice | Five-statistic proposal-only tables in the main text with head-to-heads deferred to a labeled supplement; but no main-text head-to-head numbers at all, and run-on function-ID lists in prose. |
| **ADOPTED for DT-GSK** | Main text carries: (i) DT-GSK five-statistic tables (best/median/mean/worst/SD) per dimension per suite — placeholder-bound at Phase 4; (ii) one compact family-panel summary table per suite (mean±SD combined in one cell per algorithm, best bolded) so the central comparative claim is auditable without the supplement. Full per-function panel head-to-heads go to labeled supplement tables. Narrative is organized by function class (unimodal/multimodal/hybrid/composition) and by dimension; prose never enumerates raw function-ID win lists that duplicate a table or figure. All numeric cells are exhibit-ID placeholders until Phase 6. |
| Weakness to avoid | eGSK's supplement-only comparative evidence and f-list prose; GSK's duplicated proposal column across sibling tables; ATMALS-GSK's malformed table cells. |

## 13. Statistical testing

| Field | Convention |
|---|---|
| GSK practice | Wilcoxon with hypotheses, R+/R−, win/tie/loss, decision, software named; but no multiple-comparison correction across 50 tests and a p-value-free Friedman table. |
| ATMALS-GSK practice | Wilcoxon-per-dimension + Friedman-aggregate with plain-language success-ratio translation; but no post-hoc correction and p-values printed as "0.0000". |
| eGSK practice | Two complementary nonparametric tests with per-dimension granularity and honest reporting of an unfavorable 10D result; but no correction, decision symbols contradicting alpha, and a statistically questionable pooled-dimensions Wilcoxon. |
| **ADOPTED for DT-GSK** | Per suite and per dimension: Wilcoxon signed-rank vs each panel member reporting R+, R−, p, win/tie/loss, and decision at alpha = 0.05, **with Holm correction across the simultaneous pairwise comparisons** (the improvement all three exemplars omit); plus Friedman reporting the test statistic, p-value, and mean ranks. Null/alternative hypotheses stated once; test software/library named. No pooling of dimensions into a single test; decision symbols must be mechanically derived from corrected p-values; tiny p-values reported as bounded (e.g., p < 1e-4), never "0.0000". All values are exhibit-bound placeholders (e.g., `<T05:friedman_rank_D30>`); the only rank statements permitted at Phase 4 are the verified family-panel ranks in `docs/algorithms/dt-gsk.md`, marked "to be re-derived in Phase 6 from release rel-2026-07-10-262fc16c9". |
| Weakness to avoid | The correction-free multiple testing in **all three** exemplars; eGSK's alpha-contradicting decision symbols and pooled Wilcoxon; ATMALS-GSK's "0.0000" p-values; GSK's statistic-free Friedman table. |

## 14. Table density and readability

| Field | Convention |
|---|---|
| GSK practice | 11-algorithm field split into paired 6-column tables keeps columns legible; but the paper is table-dominated and sibling-table comparison requires page flipping. |
| ATMALS-GSK practice | Mean±SD combined in one cell keeps 6-algorithm comparisons to 7 columns; full headers repeated on "Cont." pages; but pages 21–55 are back-to-back tables. |
| eGSK practice | Compact combined Friedman layout (overall + per-dimension ranks in one small table); but typographic glitches inside tables erode trust. |
| **ADOPTED for DT-GSK** | The 7-algorithm panel fits one 8-column comparison table (function + 7 algorithms, mean±SD single cells) — never split the panel across sibling tables that force page flipping. Adopt eGSK's combined Friedman layout (overall rank + per-dimension mean ranks in one table). Follow MDPI "Cont." conventions with full headers repeated. Hard cap: main-text numeric tables limited to the proposal five-statistic tables, one panel summary per suite, and the statistics tables; everything else is supplement. Every table passes a formatting lint (consistent scientific notation, decimal separators, no stray values) before freeze. |
| Weakness to avoid | GSK's/ATMALS-GSK's table domination of the main text; GSK's split-panel page flipping; eGSK's and ATMALS-GSK's in-table typos. |

## 15. Convergence-plot design

| Field | Convention |
|---|---|
| GSK practice | Median-run curves — a robust representative choice — off-loaded to the supplement; but zero convergence figures in the main paper, making main-text claims unverifiable in place. |
| ATMALS-GSK practice | Complete per-function coverage plus distinctive parameter-trajectory figures showing the adaptation working; but baseline-only comparison, one dimension only, linear y-axes. |
| eGSK practice | Complete function × dimension coverage in the supplement; but zero in-paper curves and copy-paste duplicate claim paragraphs. |
| **ADOPTED for DT-GSK** | A representative in-paper subset: **per-checkpoint mean-across-runs family-overlay curves** (the Section 6.7 default aggregation, pre-registered as P2 in `phase_04/exhibit_plan.csv`; identical basis for all seven curves in every panel) on a small, pre-registered selection of functions per featured dimension (rule P5), **log-scaled error y-axis**, including all 7 panel algorithms (not baseline-only), placed adjacent to the claims they support. GSK's median-run practice is recorded but NOT adopted: one aggregation is chosen before rendering and applied everywhere (CR-0003 Δ11). Full per-function convergence coverage goes to labeled supplement figures. Mechanism-trajectory figures (ATMALS-GSK's adoptable idea) are **supplement-designated** (`F-TRACE`/`F-ADAPT`, diagnostic-release-gated) — behavior illustration only, never component-contribution evidence (that is `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`). Every main-text convergence claim must be verifiable from an in-paper figure. |
| Weakness to avoid | GSK's and eGSK's supplement-only convergence evidence behind main-text claims; ATMALS-GSK's linear axes and baseline-only curves; eGSK's duplicated claim paragraphs. |

## 16. Figure placement

| Field | Convention |
|---|---|
| GSK practice | Figures near first citation; every ranking table paired with a companion bar chart; but some figures redundant with tables and low chart production quality. |
| ATMALS-GSK practice | Rank bar charts immediately after the corresponding Friedman tables; but 3–4-page figures separate panels from captions. |
| eGSK practice | Parallel same-design-times-four-dimensions figure series, predictable navigation; but crowded pages (three figures + a table) and inconsistent, non-self-contained captions. |
| **ADOPTED for DT-GSK** | Place every figure at first mention. Pair each headline ranking table with a companion rank bar chart placed immediately after it (GSK/ATMALS-GSK pattern). Use parallel same-design figure series across dimensions (eGSK pattern) so cross-dimension reading is predictable. Layout limits: no more than two figures per page, no figure spanning more than one page in the main text (multi-page sets go to the supplement). Captions are self-contained declarative sentences with uniform grammar, and no figure merely re-plots a table without adding a comparative reading. |
| Weakness to avoid | ATMALS-GSK's caption-separated multi-page figures; eGSK's crowded pages and caption grammar drift; GSK's table-redundant charts and corrupted axis labels. |

## 17. Discussion depth

| Field | Convention |
|---|---|
| GSK practice | Multi-angle discussion (class-wise, dimension-wise, aggregate counts, runtime), each tied to a specific exhibit; but descriptive restatement with no mechanistic WHY and some over-broad claims. |
| ATMALS-GSK practice | Honest per-function-class commentary naming its own losses and anomalies; but mechanism-level causation deferred and never integrated, plus repetitive superlatives. |
| eGSK practice | Consistent dimension-scaling frame tying every block to the central claim; but purely descriptive, never costs its local search, never diagnoses its own 10D weakness. |
| **ADOPTED for DT-GSK** | Interpretation embedded per results block plus one consolidating discussion subsection, structured by (i) function class, (ii) dimension scaling, (iii) aggregate counts, each sentence tied to a named exhibit. Interpretation may link observed behavior to subsystem *design intent* (mechanism-plausibility wording); it may **not** assert measured component contributions — that evidence is `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`. Unfavorable cells are named and discussed, not skipped (including the D30 standing behind eGSK per the verified family-panel ranks, to be re-derived in Phase 6). All comparative statements are scoped "within the GSK family panel"; superlative adjectives without an exhibit behind them are banned. |
| Weakness to avoid | GSK's "not influenced by all these obstacles"-style overreach; ATMALS-GSK's superlative filler; eGSK's undiagnosed own weakness. |

## 18. Limitations

| Field | Convention |
|---|---|
| GSK practice | No limitations section; honest but scattered admissions, and a conclusion that reasserts superiority without restating where the algorithm is beaten. |
| ATMALS-GSK practice | Mechanism-specific limitations paragraph inside the conclusions; but no dedicated heading and the claimed overhead never quantified. |
| eGSK practice | No limitations section at all; the tuning dependency dropped as an unelaborated first sentence of the conclusions. |
| **ADOPTED for DT-GSK** | A dedicated, headed limitations paragraph in the conclusions consolidating: (i) mechanism-specific limitations of the DT-GSK design (each pointing at a concrete failure mode, ATMALS-GSK style); (ii) an explicit restatement of where DT-GSK does not lead within the family panel (D30 behind eGSK; CEC2011 standing) per the verified family-panel ranks marked "to be re-derived in Phase 6 from release rel-2026-07-10-262fc16c9"; (iii) scope-of-validity (panel-relative claims only, suites tested). Any computational-overhead limitation must be grounded in the manuscript's own runtime exhibit, or not claimed. |
| Weakness to avoid | GSK's scattered-then-forgotten admissions; ATMALS-GSK's unquantified overhead claim; eGSK's one-sentence non-sequitur caveat. |

## 19. Reproducibility

| Field | Convention |
|---|---|
| GSK practice | Public code link plus complete protocol and platform; but rot-prone personal URL, no seeds, no per-run data. |
| ATMALS-GSK practice | Re-implementable in principle from parameter grids and cited protocols; but no code, data "on request", and internal contradictions make the actually-used configuration ambiguous. |
| eGSK practice | Re-implementable from the text; but no code/seeds/raw results and a factually misleading "no data was used" declaration. |
| **ADOPTED for DT-GSK** | Full-artifact reproducibility WITH public hosting (revised again 2026-08-01, D-0044): the public repository at https://github.com/MostafaMassoud/DT-GSK carries the code, configuration, result data and the pinned evidence releases, bound by SHA-256 manifests; further materials on reasonable request. No Zenodo deposit and no repository DOI; the article DOI comes from the journal. |
| Weakness to avoid | eGSK's misleading data statement; ATMALS-GSK's configuration ambiguity; GSK's link rot and missing seeds/raw data. |

## 20. Supplementary-material usage

| Field | Convention |
|---|---|
| GSK practice | Clean division of labor (bulk plots to supplement); but supplement carries figures only and main-text claims depend entirely on it. |
| ATMALS-GSK practice | Fully self-contained main text — every number in one document; but at the cost of ~40 pages of raw tables that a supplement would halve. |
| eGSK practice | Systematic labeling (A.n tables, B.n figures, one artifact per campaign–dimension cell) with exact in-text pointers; but all head-to-head numbers and all convergence evidence supplement-only. |
| **ADOPTED for DT-GSK** | A systematically labeled supplement (eGSK's A.n/B.n one-artifact-per-campaign–dimension-cell scheme, cited by exact label at point of use) carrying: raw per-function panel tables, full convergence sets, per-run statistical workbooks, and — exclusively — the Phase-12 ablation study (`DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`). The main text always retains the panel summary tables, the statistics tables, and a representative convergence subset, so that **every central claim is auditable without downloading the supplement**. |
| Weakness to avoid | eGSK's/GSK's supplement-dependent central claims; ATMALS-GSK's refusal to use a supplement at all. |

## 21. Conclusion structure

| Field | Convention |
|---|---|
| GSK practice | Concrete multi-item future-work agenda plus code pointer; but re-narrates the metaphor and omits its own unfavorable CEC2011 ranking. |
| ATMALS-GSK practice | Quantitative conclusion with exact ratios and ranks, integrated limitations, concrete future work; but repeats Section 4.5 verbatim and lists a statistical tie among dominant results without comment. |
| eGSK practice | Memorable per-competitor success-percentage compression; but opens with a limitation non-sequitur, overclaims "best-performing" despite reported ties, and never defines the success-ratio computation. |
| **ADOPTED for DT-GSK** | Four movements: (i) one-paragraph recap of the DT-GSK design (no metaphor re-narration); (ii) quantitative summary via exhibit-bound placeholders — panel ranks and any summary ratio, with the ratio's computation **defined where first used**, ties and unfavorable cells stated alongside favorable ones, all scoped "within the GSK family panel" and rank statements limited to the verified family-panel ranks marked for Phase-6 re-derivation; (iii) the headed limitations paragraph (Dimension 18); (iv) specific, mechanism-anchored future work plus the code/data pointer. The summary paraphrases Section 4's findings rather than repeating its sentences verbatim. |
| Weakness to avoid | eGSK's undefined success ratio and tie-ignoring "best-performing" overclaim; GSK's omission of its unfavorable ranking; ATMALS-GSK's verbatim repetition and uncommented tie. |

## 22. Overall visual and editorial quality

| Field | Convention |
|---|---|
| GSK practice | Template discipline, sequential citation of every exhibit, systematic table+chart pairing; but numerous copy-editing lapses and image-set math degrading searchability. |
| ATMALS-GSK practice | Venue-level layout consistency at the exact target journal (caption discipline, boxed algorithms, "Cont." conventions); but a density of surviving cross-consistency errors showing no systematic audit was run. |
| eGSK practice | Complete modern back-matter apparatus (CRediT, COI, supplementary DOI, data availability); but surviving typos including a copy-paste error inside a results paragraph. |
| **ADOPTED for DT-GSK** | Follow the MDPI *Algorithms* template exactly as repository-wired (`papers/Definitions/mdpi.cls`, class option `algorithms` in `papers/main.tex`), mirroring ATMALS-GSK's venue conventions (caption style, boxed algorithms, "Cont." handling) and eGSK's full back-matter apparatus (Author Contributions, Funding, Data Availability, Conflicts of Interest). Institutionalize two mandatory pre-submission passes that no exemplar ran: (i) a cross-consistency audit — parameter tables vs pseudocode vs equations vs prose vs captions vs the frozen symbol table; (ii) a parallel-text pass over all same-design result narrations to catch copy-paste residue. All equations and pseudocode are typeset (searchable), never images. Every exhibit is cited in numeric order. |
| Weakness to avoid | ATMALS-GSK's unaudited cross-document inconsistencies; eGSK's copy-paste residue in results prose; GSK's image-set math and garbled labels. |

---

## Global weaknesses to avoid

1. **Overcrowded tables / table-dominated main text** — GSK (28 tables, sibling-table page flipping, taxonomy tables out of proportion) and ATMALS-GSK (~40 pages of back-to-back raw tables, no supplement). Countermeasure: Dimension 14 caps + Dimension 20 supplement scheme.
2. **Repetitive text** — GSK (metaphor re-narrated across Sections 2, 2.1, 2.2 and the conclusion), ATMALS-GSK (near-duplicate mechanism subsections 3.2.2–3.2.4, conclusion repeating Section 4.5 verbatim), eGSK (copy-paste convergence paragraphs, duplicated result narration producing the FOWFO error). Countermeasure: shared-machinery stated once; parallel-text audit pass (Dimension 22).
3. **Weak interpretation** — GSK (descriptive restatement, no mechanistic WHY), eGSK (never diagnoses its own 10D weakness or costs its local search), ATMALS-GSK (mechanism causation deferred and never integrated). Countermeasure: Dimension 17 mechanism-plausibility discussion tied to exhibits, with measured component contributions in the Phase-12 supplement only.
4. **Inconsistent notation** — all three exemplars: GSK (N/NP, k/K, Table 5 misprint), ATMALS-GSK (Kf/KF, Kr/KR, "PSL", Eq (7) formula/text contradiction, Table 1 vs Algorithm 4 grids), eGSK (K/k, K_r/k_r, N/NP, magic 0.01). Countermeasure: frozen symbol table + scripted notation audit (Dimension 8) and the pseudocode/table single-source rule (Dimensions 9–10).
5. **Underspecified experiments** — ATMALS-GSK (no hardware/software/runtime, silent f2 omission, re-run-vs-copied unstated) and eGSK (SOTA numbers copied from literature without parity verification, f2 exclusion unexplained). GSK is the positive reference here. Countermeasure: Dimension 11 full-disclosure setup with in-repository re-runs from release rel-2026-07-10-262fc16c9.
6. **Excessive visual density** — eGSK (three stacked figures plus a table on one page) and ATMALS-GSK (figures spanning 3–4 pages, panels separated from captions). Countermeasure: Dimension 16 layout limits (max two figures per page, no multi-page main-text figures).
7. **Unsupported claims** — ATMALS-GSK (Section 2.3 "significantly outperforms" before any results), eGSK ("best-performing" despite a reported statistical tie; main-text convergence claims verifiable only via supplement; undefined success ratio), GSK ("its performance is not influenced by all these obstacles"; conclusion omitting the unfavorable CEC2011 ranking). Countermeasure: every claim exhibit-bound; ties and losses reported alongside wins; scope always "within the GSK family panel"; numeric slots as placeholders until Phase 6.

---

**FROZEN at Phase 4 under CR-0002 (exemplar calibration) and CR-0003 (presentation-conventions register). Changes require a new change-request entry in `papers/governance/change_request_register.csv`.**
