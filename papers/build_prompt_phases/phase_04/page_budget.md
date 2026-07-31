# DT-GSK — Word/Page Budget (Phase 4, task 7)

**Phase 4 deliverable (claim-freeze input to Gate 4).** Date: 2026-07-10.
Companion to `phase_04/outline.md`. Venue: MDPI *Algorithms*, article type Article
(repo-proven, `papers/main.tex` line 5).

## 1. What the journal agent found (recorded verbatim in substance)

- `verified_online: false` (official page returned HTTP 403 on 2026-07-10; re-verify
  before submission).
- **No hard journal page limit found.** MDPI general guidance (search-derived): contact
  the Editorial Office below ~3,000 or above ~12,000 words. Free-format initial
  submission offered; supplement accepted and encouraged; supplement file-type/size
  specifics UNKNOWN — verify before submission.
- Therefore the framework's **Section 1.5 hard page-limit rule binds to a SELF-IMPOSED
  budget** defined in this file, measured from the compiled PDF at Phases 8/9/11.

## 2. Self-imposed budget (BINDING — **caps SUPERSEDED by CR-0008, 2026-07-22, then CR-0021, 2026-07-31**)

> **Superseded.** The B1 and B2 hard caps below (34 pages / 12,000 words) were set at
> Phase 4 on a projected page count and are **no longer the binding limits**. The
> shipped 2026-07-22 build measures **B1 = 36 pages** and **B2 ≈ 19,536 words**;
> `change_request_register.csv` **CR-0008** raised the caps to **B1 = 40 pages** and
> **B2 = 20,000 words**, with the measurement method and justification recorded there
> and the measurement itself recorded in the Phase-12 row of
> `phase_gate_register.csv`.
> **CR-0021 (2026-07-31):** the five-suite build (CR-0019 scope) measures B1 = 41 pp / B2 = 22,821 tokens; caps re-set to **B1 = 44 pages** and **B2 = 24,000 words** — see `change_request_register.csv` CR-0021. MDPI *Algorithms* imposes no page or word limit, so these
> caps are internal reviewer-attention discipline, not venue compliance. The overrun
> was **not** resolved by shrinking exhibits — SE-005 and SE-013 require the opposite.
> The targets and rationale below are retained as the dated Phase-4 record.

Two coupled numbers, both required because "page" is layout-dependent:

| Bound | Value | Basis |
|---|---|---|
| **B1 — total typeset pages, main text INCLUDING exhibits, EXCLUDING references and back matter** | **target 28–34 pages; hard cap 34** | Justified vs exemplars: original GSK = 29 pages with 28 tables (table-dominated — the density we avoid, not the length); ATMALS-GSK = 64 pages with no supplement (the explicit anti-pattern, Dim 1/14/20); eGSK's page count is not recorded in the conventions register, but its supplement-heavy split is the structural model. 28–34 pages ≈ GSK's length with a modern supplement split and far below ATMALS-GSK. |
| **B2 — main-text prose word count (incl. abstract and captions' prose, excl. references)** | **target ~10,200 words; hard cap 12,000** | 12,000 = MDPI contact-the-office threshold (search-derived); 10,200 is the outline sum below. |
| **B3 — prose-only typeset pages (excl. exhibits, excl. references)** | **~16–22 pages** | This is the figure referenced in `phase_04/journal_requirements.md` ("~16-22 typeset pages main text, excluding references"). Reconciliation: B3 (prose-only) + exhibit pages (~13–14, Section 4) = B1 (28–34 incl. exhibits). The two documents state the same budget at two levels of aggregation; B1 is the number the Section 1.5 hard-limit rule enforces. |

Conversion assumption for planning only: MDPI *Algorithms* single-column layout,
~500–550 words per full text page. All page figures below are estimates; the binding
measurements are made on the compiled PDF at Phases 8, 9, and 11.

## 3. Word budget per section (sums to total)

| Unit | Words | Est. prose pages |
|---|---:|---:|
| Abstract | 200 | 0.4 |
| 1 Introduction | 1,000 | 1.8 |
| 2 Related Work (2.1: 850 / 2.2: 250 / 2.3: 400) | 1,500 | 2.7 |
| 3 Proposed DT-GSK (3.1: 450 / 3.2: 300 / 3.3: 800 / 3.4: 650 / 3.5: 350 / 3.6: 200 / 3.7: 250 / 3.8: 300) | 3,300 | 6.0 |
| 4 Experimental Study (4.1: 600 / 4.2: 850 / 4.3: 450 / 4.4: 400 / 4.5: 350 / 4.6: 250 / 4.7: 500) | 3,400 | 6.2 |
| 5 Conclusions (incl. ~200-word headed limitations paragraph) | 650 | 1.2 |
| Back matter (Author Contributions, Funding, Data Availability, COI) | 150 | 0.3 |
| **TOTAL prose** | **10,200** | **~18.6** |

10,200 words is inside the MDPI 3,000–12,000 comfort band and inside B3 (~16–22 prose
pages at 500–550 w/p).

References are EXCLUDED from B1/B3: ≤ 57 admissible keys → est. 2.5–3.5 pages.
Supplement is excluded from all main-text budgets (no length cap recorded; verify
file-type/size rules before submission).

## 4. Per-exhibit space estimates (main text)

Planning rates: **numeric tables 0.4–0.8 page** (29-function five-statistic tables at
the high end, compressed via siunitx/small font toward ~0.6); **full-width figures ~0.5
page** (multi-panel figures up to ~0.9, never > 1 page in main text per Dim 16);
**typeset algorithm floats ~0.7 page each**.

The itemization below uses the exhibit-plan IDs (`phase_04/exhibit_plan.csv` is the
single exhibit registry; outline X-IDs cross-map per outline §3 preamble). Gate-4 QA
reconciliation: the former separate base-GSK float, the ×4 main-text per-function
five-statistic tables, the CEC2011 main-text convergence subset, and the main-text
mechanism-trajectory figure were removed (single A1 float; T01-D* → S1; CEC2011
convergence → S3; F-TRACE/F-ADAPT → S3, diagnostic-gated), and the three conceptual
figures + display-equation allowance previously omitted are now budgeted.

| Exhibit (plan ID) | Type | Est. pages |
|---|---|---:|
| A1 DT-GSK pseudocode (§3, single algorithm float) | algorithm | 0.7 |
| E1a–E12 display-equation allowance (§3, 13 equations) | equations | 0.8 |
| T-NOTATION (X1) nomenclature/symbol table (§3.1) | table | 0.4 |
| T-FAMREV (X2) GSK-family review summary (§2.1) | table | 0.6 |
| T-WORKED (X3) worked numeric example, tier gating (§3) | table | 0.4 |
| T-PARAMS (X4) parameter table + provenance (§3.7) | table | 0.7 |
| T-PANEL (X5) panel roster, 7 algorithms (§3.7/§4.1) | table | 0.5 |
| F-ARCH (X6) architecture figure (§3.2) | figure | 0.5 |
| F-SGSM-MECH mechanism illustration (§3.4) | figure | 0.4 |
| F-GATING dimension-tier gating chart (§3.6) | figure | 0.4 |
| F-TAXONOMY related-work positioning (§2.2) | figure | 0.4 |
| T07-PROTOCOL protocol/reproducibility summary (§4.1) | table | 0.4 |
| T01-SUM CEC2017 condensed headline summary (§4.2.1–2) | table | 0.4 |
| F05-RANKBAR companion rank bar chart (§4.2.2, Dim 16) | figure | 0.4 |
| T05 combined Friedman table, eGSK layout (§4.2.3) | table | 0.3 |
| F01 Nemenyi CD diagrams, 4-panel (§4.2.3) | figure | 0.8 |
| T02 Wilcoxon+Holm summary (§4.2.3) | table | 0.8 |
| T03 A12/Cliff's + BCa summary (§4.2.3) | table | 0.5 |
| F02-MAIN-D30 convergence grid, 4 panels (§4.5) | figure | 0.9 |
| F02-MAIN-D100 convergence grid, 4 panels (§4.5) | figure | 0.9 |
| F03 rank-vs-dimension trend (§4.2.3) | figure | 0.4 |
| T04 CEC2011 panel results (§4.3) | table | 0.5 |
| F04-CEC2011 rank figure (§4.3) | figure | 0.4 |
| T06 CEC2013 summary (§4.4) | table | 0.5 |
| T-RUNTIME runtime/overhead table (§4.6) | table | 0.3 |
| **Exhibit subtotal (25 main exhibits)** | | **~13.3** |

## 5. Total and headroom

| Component | Pages |
|---|---:|
| Prose (Section 3 table) | ~18.6 |
| Exhibits (Section 4 table, 25 main exhibits incl. equation allowance) | ~13.3 |
| **Projected main-text total (B1 scope)** | **~31.9** |
| B1 target band / hard cap | 28–34 / 34 |
| Headroom to hard cap | ~2.1 pages |

The projection sits in the upper half of the band by design: the overflow valve
(Section 6) is the correction mechanism, never loosening the cap.

## 6. Overflow valve — supplement-migration rule (framework Section 8.6, default-to-supplement)

If the compiled PDF exceeds 34 pages (B1) at Phase 8/9/11, or any Dim 14/16 density cap
is breached, material migrates to the supplement in this fixed order (each step
re-measured before the next):

1. `F-TAXONOMY` related-work positioning figure → replaced by its four-dimension
   comparison stated in §2.2 prose (novelty_scope.md remains the source).
2. `T06` CEC2013 summary table → S2 (main text keeps the CEC2013 statistics rows in
   T05/T02, so the claim remains auditable in place).
3. One of the two main convergence grids (`F02-MAIN-D30` kept as the unfavorable-case
   carrier; `F02-MAIN-D100` → S3 first if both cannot fit).
4. `T03` A12/BCa summary → S4, replaced by a 3–4-line summary within `T02`.
5. `T-WORKED` worked-example table → S5 with a one-sentence in-text summary.
6. `F04-CEC2011` rank figure → S2 (T04 retains the rank column in place).

**Never migrated (Dim 12/15/20 floors — central claims auditable without the
supplement):** the compact panel summary per suite, `<T02>` Wilcoxon+Holm summary,
`<T05>` combined Friedman table, `<F01>` CD diagrams, and at least one in-paper
convergence figure. The ablation study is not part of this valve: it is
`DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY` (S6) and never appears in the main text at any
budget.

## 7. Word-layout parity note (BINDING at Phase 9)

MDPI produces both PDF and Word-derived layouts, and the repo's own Phase 9 checks
include a DOCX rendering. The budget is therefore checked in **BOTH** formats at
Phase 9: B2 (word count) is layout-independent and is the primary cross-format
invariant; B1 (pages) is measured on the compiled LaTeX PDF as the format of record,
and the DOCX rendering is checked for gross divergence (> ~15% page-count difference
triggers a re-audit of exhibit sizing, not a budget change). Any budget breach found in
either format at Phase 9 invokes the Section 6 valve; the caps themselves change only
via a change-request entry in `papers/governance/change_request_register.csv`.

## 8. Measurement protocol

- Phase 8 (draft): compile PDF, record B1/B2/B3 in the phase gate report.
- Phase 9 (polish): re-measure in PDF and DOCX (Section 7); apply valve if needed.
- Phase 11 (pre-submission): final measurement; B1 ≤ 34 and B2 ≤ 12,000 are gate
  conditions.
