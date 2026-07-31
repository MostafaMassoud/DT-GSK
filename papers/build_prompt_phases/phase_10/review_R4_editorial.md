# Review R4 — Editorial (Narrative, Clarity, Figures/Tables, Exemplar Parity)

**Reviewer:** R4 (editorial)
**Manuscript:** *An Interaction-Structure Memory for High-Dimensional Gaining-Sharing Knowledge Optimization* (DT-GSK), MDPI *Algorithms*, submit mode, 34 pp.
**Artifacts read:** `papers/DT-GSK.pdf` (full text + rendered pp. 4, 6, 10, 11, 12, 15, 22, 27); `papers/cover_letter.tex`; `papers/governance/presentation_conventions.md` (22-dimension exemplar register).
**Posture:** Adversarial Q1 reviewer. Reviewer-only; no artifact was edited.
**Overall recommendation:** MINOR REVISION.

---

## 1. Summary

This is a disciplined, unusually honest manuscript. The claim hygiene is exemplary: every comparative statement is scoped "within the GSK family panel," ties and losses are stated beside wins (the eGSK D30 second place, the CEC2011 Holm-significant loss, the CEC2013 D30 third place, the sub-0.5 A12 cell), the "Overall" Friedman aggregate is explicitly labelled a descriptive mean with "no omnibus test attached," no runtime-superiority claim is made, and no-free-lunch is cited to bound generality. The five-section spine, the frozen symbol table (Table 2), the typeset line-numbered Algorithm 1 with an Inputs/Output contract, the Holm correction, and the complete MDPI back-matter apparatus all match the adopted conventions. Algorithm 1 (the just-revised pseudocode float) reads cleanly and its step order matches the Section 3.2 prose one-to-one.

The problems are presentational, not scientific, and cluster in the exhibits. Two are material for a Q1 venue: (a) all four conceptual figures label equations with an undefined "E#" scheme that misaligns with the manuscript's own Eq. (1)–(13) numbering — and Figure 4's graphic even contradicts its own caption — and (b) the CEC2013 suite, a *headline* result ("overall #1, 2.80"), has no main-text table or figure at all, breaking the "identical internal rhythm" the Section 4 preamble promises and the per-suite panel-summary convention (Dim 12/16). The remainder are figure-content hygiene (raw BibTeX keys, leaked repository paths, the SGSM/ISM naming duplication) and layout polish. All are fixable without touching any frozen number or the algorithm.

---

## 2. What is verified good (evidence for high marks)

- **Claim scoping / no unsupported rhetoric (5/5).** Abstract, Section 4.7, and the Conclusions all bind comparatives to the panel and protocol; the single calibrated headline sentence in 4.7 ("most consistent performer across suites and dimensions ... while eGSK remains the stronger algorithm at the mid-dimension tier") is fully hedged and exhibit-anchored. The banned pre-results overclaim, the "best-performing"-despite-ties pattern, and field-wide superiority are all absent. This meets Dimensions 4, 17, 21 and the global "unsupported claims" countermeasure.
- **Algorithm 1 (p. 11).** Typeset, line-numbered, `Inputs(f, D, [ℓ,u], MaxFES, seed)` / `Returns xgb` contract in the header, equation cross-refs inside the lines (Eq. 6, 7, 3, 1, 2, 4, 5, 8, 9, 10, 11, 12, 13), step numbering (1)–(11)+(3b) identical to the Section 3.2 prose. Reads cleanly — the revision succeeded. (One layout blemish noted in T5.)
- **Table 1 (p. 4).** Four-column family review (variant | core mechanism | suites tested | key limitation), all six comparators, one critical limitation each — exactly the summary table Dimension 6 asks for and that no exemplar provided.
- **Convergence grid (Figs 13–14).** 2×2, 7-curve overlay, log-error axis, colour + linestyle (grayscale-safe), DT-GSK solid black, single shared legend, per-checkpoint mean-across-51-runs basis stated, an unfavorable case (F26) deliberately included and discussed. Meets Dimension 15.
- **Parameter cross-consistency (Table 2 / Table 4 / Figure 3 / prose / Algorithm 1).** Spot-checked Nmin (12/25 tiers), rrst (0.30/0.10), Rmax (4/2), κmin (0.55), λ (0.95), W (50) — all agree across the notation table, the parameter table, the activation matrix, and the pseudocode. The single-source-of-truth rule (Dim 9/10) is honored. This is the failure mode that sank ATMALS-GSK; it is clean here.
- **Back-matter.** Author Contributions, Funding, Data Availability (accurate, non-boilerplate, checksum-referenced), GenAI use disclosure, Conflicts of Interest (the A.W.M. authorship relationship is disclosed proactively), Abbreviations. Meets Dimensions 19, 22.

---

## 3. Findings (tickets)

### T1 — MAJOR (editorial): conceptual figures use an undefined "E#" equation scheme that misaligns with the manuscript's Eq. (1)–(13)
Figures 1, 2, 3, and 4 label equations "E1a/E1b/E2/E3, E4, E5, E6, E7, E8, E9, E10, E11, E12," but the manuscript numbers its display equations (1)–(13) and the body/pseudocode cite them as "Eq. (n)." The mapping is offset: figure **E4** = crossover mask = body **Eq. (5)**; **E5** = NLPSR = **Eq. (6)**; **E7** = midpoint repair = **Eq. (8)**; **E8** = greedy selection = **Eq. (9)**; **E9** = BSE = **Eq. (10)**; **E10** = ISM graph = **Eq. (11)**; **E11** = polish = **Eq. (12)**; **E12** = RNG = **Eq. (13)**. No legend anywhere defines the E-numbering, so every figure reference is an undefined cross-reference. It is actively misleading where the ranges coincide: "inherited GSK core (E1–E4, E7, E8)" (Fig. 3) invites a reader to read E4 as Eq. (4) (the gaining-sharing update), but "(E4)" elsewhere labels the *crossover mask* (Eq. 5), which is not purely inherited. **Worst instance:** Figure 4's *caption* correctly cites "Eq. (11) … Eq. (5) … Eq. (12)" while the *same figure's graphic* labels those identical objects "(E10) … (E4) … (E11)" and marks greedy selection "(E8 accepts)" (Eq. 9) — an internal contradiction inside one float. Verified by grep: the "E#" tokens occur *only* inside figures, never in body prose. This is precisely the "unaudited cross-document inconsistency" Dimension 22 institutes a pass to catch.
**Location:** Figures 1 (p. 6), 2 (p. 10), 3 (p. 12), 4 (p. 15); Fig. 4 caption vs. graphic.
**Suggested fix:** Regenerate the four figures with equation labels matching the manuscript numbering (E4→Eq. 5, E5→Eq. 6, E7→Eq. 8, E8→Eq. 9, E9→Eq. 10, E10→Eq. 11, E11→Eq. 12, E12→Eq. 13; keep E1–E3 as Eqs. 1–3/index rules), or drop equation labels from the figures entirely. Do the mapping carefully and re-verify caption↔graphic agreement. No numeric or algorithmic change.

### T2 — MAJOR (editorial): Figure 1 cites raw BibTeX keys instead of numeric references
The Figure 1 header labels the three comparison methods "(DG) [omidvar2014dg]," "(CMA-ES) [hansen2001cmaes]," "(DE) [guo2015eig]." In the body these are references [22], [23], [24]. Unresolved author-year `\cite` keys in a published figure are a formatting defect a copy-editor (and reviewer) will flag immediately, and they break the numeric citation style used everywhere else.
**Location:** Figure 1 header row (p. 6).
**Suggested fix:** Replace the raw keys with the resolved numeric labels [22]/[23]/[24] (or a short author name), regenerating the figure asset.

### T3 — MINOR (editorial): internal repository artifact paths leak into published figures
Reader-facing figure text exposes build-pipeline file paths that mean nothing to an external reader: Figure 1 footer "(novelty_scope.md Sections 1.1 1.3, card-bounded) … ISM compute cost per phase_03/complexity_analysis.md"; Figure 4 Stage-1 box "(compute cost per phase_03/complexity_analysis.md)"; Figure 3 footer "(algorithm_freeze_manifest.json)." (Table 4's caption `_dt_profiles.build_pub_config(dim)` and `algorithm_freeze_manifest.json` are borderline-acceptable as reproducibility identifiers but read as implementation leakage in the same spirit.)
**Location:** Figures 1 (p. 6), 3 (p. 12), 4 (p. 15); Table 4 caption (p. 16).
**Suggested fix:** Strip internal `.md`/`.json`/module paths from figure text; replace "per phase_03/complexity_analysis.md" with "(Section 3.8)". Keep only reader-meaningful pointers.

### T4 — MINOR (editorial): "SGSM" code alias duplicates the "ISM" name throughout the exhibits
The mechanism the paper names the interaction-structure memory (ISM) is repeatedly shown under its internal code alias "SGSM" — Table 2's block header "SGSM / eigenframe polish," Figure 2 ("SGSM-fed blocks," "SGSM interaction-structure memory," "SGSM top-k-block"), Figure 3, Figure 4's title, and the Abbreviations list, which even records "SGSM — code alias of the interaction-structure memory (unexpanded)." Carrying an unexpanded implementation alias into figures and tables contradicts Dimension 5 (single grep-clean spelling / persistent identifier) and Dimension 8 (one casing, one meaning per symbol), and is the exact naming-drift weakness the register flags in eGSK/ATMALS-GSK.
**Location:** Table 2 (p. 8), Figures 2/3/4 (pp. 10/12/15), Abbreviations (p. 32).
**Suggested fix:** Use "ISM" uniformly in all reader-facing exhibits. If the code alias must be preserved for the repository, mention it once in prose ("code alias `SGSM`") and nowhere else; remove it from figure/table labels.

### T5 — MINOR (editorial): CEC2013 headline result has no main-text exhibit, breaking the promised per-suite rhythm
Section 4's preamble states Sections 4.2–4.4 each carry "the same internal rhythm: descriptive results first, then the family-panel comparison, then the inferential statistics." CEC2017 delivers this (Table 7 + Figs 5/6 + Table 8) and CEC2011 largely does (Table 9 + Figure 12 + prose stats), but **CEC2013 (Section 4.4) contains no table and no figure** — its headline claims (overall #1 at 2.80; first/third/first per-dimension; omnibus p-values) live entirely in one prose paragraph pointing to the supplement. This violates the panel-summary-table-per-suite convention (Dim 12), the "each ranking table paired with a companion rank bar chart" convention (Dim 16), and the "every central claim auditable without the supplement" principle (Dim 20) — and it contradicts the manuscript's own "same internal rhythm" sentence. Because "CEC2013 overall #1" is a headline of the paper, it should not be the only suite with zero in-text evidence.
**Location:** Section 4.4 (pp. 25–26); Section 4 preamble (p. 18).
**Suggested fix:** Add one compact CEC2013 panel Friedman-rank summary table (7 algorithms × D10/D30/D50 + overall, mirroring Table 7) and/or a companion rank bar chart, surfacing the already-released rel-2026-07-10 numbers. Presentation only — no new analysis; do not alter the released values.

### T6 — MINOR (editorial): "critical-difference diagrams" are rendered as bar charts, not Demšar CD plots
Figures 7–10 are titled "Nemenyi Critical Difference" and the method text cites Demšar [37], but they are horizontal *bar charts* of mean rank with a single floating "CD = 1.67" bracket, not the canonical CD diagram (a rank axis with algorithms hung at their ranks and horizontal clique bars connecting statistically indistinguishable groups). The "within-one-CD-of-best cohort" is then *asserted in each caption* rather than drawn, forcing the reader to eyeball band membership. The information is present and the CD ruler is a defensible design, but a reviewer familiar with Demšar 2006 will note the mismatch between the label/citation and the graphic.
**Location:** Figures 7–10 (pp. 22–23).
**Suggested fix:** Either render true Demšar CD diagrams with clique bars, or retitle/caption these as "mean-rank bar charts with a critical-difference reference band" so the label matches the graphic; keep the cohort membership visually derivable.

### T7 — EDITORIAL: abstract is a single dense 199-word paragraph with an overloaded central sentence
The abstract is at the MDPI word limit (~199 words) but its second/third sentence chains five semicolon-separated clauses plus a five-item parenthetical ("(bandit operator control, acceptance-gated pruning, tier-floored population reduction, budget-safe escape, global-best-preserving restart)") before reaching any result, taxing readability at first impression. Content and scoping are correct; only parse-ability suffers.
**Location:** Abstract (p. 1).
**Suggested fix:** Split the mechanism sentence into two; move the five-item parenthetical into a shorter apposition. No content change.

---

## 4. Exemplar-parity ledger (vs. `presentation_conventions.md`)

| Dim | Convention | Verdict |
|---|---|---|
| 1 Structure | 5 numbered sections, no main-text ablation | MET |
| 2 Ordering | intro→related→method→experiments (per-suite rhythm)→runtime→conclusions; CEC2013 = "second comparison suite" | MET on ordering; **rhythm broken for CEC2013 (T5)** |
| 3 Introduction | ≤~1.5-pp funnel, variant positioning, suite-name consistency | MET (funnel ~1.5 pp + bullets; suites consistent) |
| 4 Research gap | named positioning subsection, need-only, panel-scoped | MET (Sec 2.3) |
| 5 Contributions | bulleted C1–C4, persistent IDs, single name spelling | Bullets MET; **SGSM/ISM duplication (T4)** |
| 6 Lit review | typology + summary table + one critical sentence each | MET (Table 1) |
| 7 Algorithm explanation | base recap, one subsystem/subsection, worked example, execution order in prose+pseudocode | MET (Table 3 worked example; order matches) |
| 8 Notation | one frozen symbol table, one casing/meaning | MET for symbols; **alias SGSM dilutes (T4)** |
| 9 Pseudocode | typeset, line-numbered, I/O contract, eq refs in lines | MET (Algorithm 1) |
| 10 Parameters | ISM table + panel roster; single source of truth | MET (Tables 4, 5); cross-consistent |
| 11 Setup | full protocol, in-repo reruns, environment named | MET (Sec 4.1, Table 6) |
| 12 Benchmark reporting | 5-stat tables + one panel summary **per suite** | **CEC2013 panel summary missing (T5)** |
| 13 Statistics | Wilcoxon+Holm, Friedman+ID, CD only if omnibus sig., bounded p | MET; **CD graphic convention (T6)** |
| 14 Table density | panel in one table, no page-flipping, formatting lint | MET |
| 15 Convergence | in-paper subset, log axis, all 7 curves, one aggregation | MET (Figs 13–14) |
| 16 Figure placement | at first mention, ranking table + companion chart, parallel series | MET for CEC2017/CEC2011; **CEC2013 has neither (T5)** |
| 17 Discussion | class/dimension/aggregate, exhibit-anchored, plausibility-only | MET (Sec 4.7) |
| 18 Limitations | dedicated headed paragraph, where-it-loses, scope | MET ("Limitations." run-in, five items) |
| 19 Reproducibility | release pin, seeds, per-run data, env, accurate data statement | MET |
| 20 Supplement | labeled S1–S5, central claims auditable in-text | MET except **CEC2013 (T5)** |
| 21 Conclusion | four movements, defined ratio, ties stated, no metaphor | MET |
| 22 Visual/editorial quality | cross-consistency + parallel-text passes; no image math | Equations/pseudocode typeset (MET); **figure E# vs Eq# and bibkey/path leaks show the cross-consistency pass did not cover figure internals (T1–T3)** |

Net: strong parity; unjustified deviations are T1 (Dim 22), T4 (Dim 5/8), T5 (Dim 12/16/20/2), T6 (Dim 13/16).

---

## 5. Scores

| Category | Score | Basis |
|---|---|---|
| Narrative, clarity & section balance | 4 | Well-organized, honest, balanced; dented by the CEC2013 prose-only subsection contradicting the "same rhythm" claim (T5) and a dense abstract (T7). |
| Figure & table legibility/quality | 3 | All exhibits render legibly, but figure *content* carries the E#/Eq# misalignment across all four conceptual figures (T1), raw BibTeX keys (T2), leaked repo paths (T3). |
| Caption completeness & cross-references | 3 | Captions are self-contained and release-stamped, but Figure 4's caption contradicts its own graphic and the E# labels are undefined cross-references (T1). |
| MDPI structure & language | 4 | Full spine + back-matter, clean language; residual implementation leakage (SGSM, repo paths) is the un-audited-residue weakness the venue penalizes. |
| Unsupported rhetoric / claim scoping | 5 | Every comparative claim panel-scoped; ties/losses stated beside wins; descriptive-aggregate and no-runtime-superiority caveats explicit; NFL cited. No overclaim found. |
| Exemplar parity | 3 | Strong overall adherence with four unjustified deviations (T1, T4, T5, T6), each ticketed. |

---

## 6. Recommendation

**MINOR REVISION.** The science, statistics, and claim scoping are frozen and disciplined; no finding touches a number or the algorithm. Priorities: T1 (figure equation labels — affects all four conceptual figures and includes an internal caption/graphic contradiction) and T5 (surface the CEC2013 headline result as a main-text exhibit). T2–T4, T6–T7 are copy-edit / asset-regeneration items. None is a barrier to acceptance once resolved.
