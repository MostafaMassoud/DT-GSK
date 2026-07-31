# Stage 14 — Section-by-Section Scientific and Editorial Review

Seat: `s14_sections` (Stage 14; lead AE, supported by RW; team ECB with T5-WRITE)
Date: 2026-07-22
Governing prompt: `papers/PAPER_REVIEW_PROMPT.md` lines 2241–2393 (mandate), 1104–1148 (ticket schema), 3160–3522 (DT-GSK profile), 3977–3998 (prohibited shortcuts).

## 0. Package actually reviewed (verified against the repo, not from memory)

| Item | Verified value | How verified |
|---|---|---|
| git HEAD | `45248eb31af7b01567c251f2a5da4f36e92d6030` | `git rev-parse HEAD` |
| HEAD subject | `papers: state budget-crossing fairness verification in the manuscript; re-mint freeze` | `git log --oneline -3` |
| Manuscript freeze anchor | `abd2fa2f2` (prior commit `dbc824782` stamps it) | `git log` |
| `check_manifest.py` | `15/15 match []` | executed read-only |
| `validate_provenance_claims.py` | `[provenance] OK - prose matches the manifests` (exit 0) | executed read-only |
| `validate_cross_format_parity.py` | `TOTAL rows=579 FAIL=0` | executed read-only |
| `validate_document_consistency.py` | `OK - all cross-stated facts agree` | executed read-only |
| `validate_build_hygiene.py` | `OK - no unresolved references, control characters, or retired content` | executed read-only |
| Evidence release | `rel-2026-07-20-67d9345f9` (anchor `67d9345f9502a9a584e645fa8948f60a61d70e29`) | `papers/analysis/rel-2026-07-20-67d9345f9/`, rendered supplement p. ~S5 |
| `DT-GSK.pdf` | 39 pp (footer "N of 39"), 16 numbered tables, 6 figures, Algorithm 1, 40 references | PyMuPDF page count + rendered scan |
| `supplementary.pdf` | 61 pp, S1–S6 with S6.1–S6.7 | `pdftotext` heading scan |
| `cover_letter.pdf` | 2 pp, dated 25 July 2026 | `pdftotext` |
| DOCX (main) | 17 native `w:tbl`, 753 OMML, 0 literal `&` OMML markers | zip/XML inspection |
| DOCX (supplement) | 26 native `w:tbl`, 640 OMML, 0 literal `&` OMML markers | zip/XML inspection |
| Target journal | *Algorithms* (MDPI) | `main.tex` documentclass + cover letter |

## 0.1 Remediation verification (R-01 … R-14) — did the closures actually land?

| Ticket | Verdict | Evidence |
|---|---|---|
| R-01 per-phase signs `s_J`/`s_S` | **CLOSED INCOMPLETELY** | `phase_03/equations.tex` E3 now defines both signs inside the numbered display and restates the convention in rendered text; `phase_03/notation_table.tex:54` adds the `$s_J,s_S$` row. **But** `sections/proposed_algorithm.tex:71` still says `$s\in\{+1,-1\}$` — rendered `DT-GSK.pdf` (extract line 385) prints "`s ∈ {+1, −1} is the sign of the fitness comparison`". A symbol `s` is used in prose that appears in no equation and no notation row. → ticket **S14-010** |
| R-02 registry drift E3/E4/E8 | CLOSED | E4 comment/rendering states permutation-chunk (non-contiguous) blocks; E3 states the senior arrangement `(x_{R1}-x_{R3}) + s_S(x_{R2}-x_i)`; E8 renders `f(v_i) ≤ f(x_i)` with ties accepted, matched by Algorithm 1 step 15 ("Greedily keep each **no-worse** trial") and §3.1 prose |
| R-03 DOCX OMML `&` markers | CLOSED | 0 literal `&amp;` inside `<m:oMath>` in both DOCX (scripted count) |
| R-04 restart invariant | CLOSED | `proposed_algorithm.tex:203–210` states elitism-except-deep-stall and the separately held `x^{gb}`; matches Algorithm 1 steps 22–23 and Table 4 caption |
| R-05 budget-crossing semantics | CLOSED | `performance.tex:164–178` discloses DT-GSK strict truncation vs. the six reference-faithful ports' terminal-batch overrun with in-budget-prefix counting, and states all seven are charged exactly MaxFES; the fairness verification is stated in the rendered PDF |
| R-06 supplement release identity | CLOSED (one source-only residue) | Rendered supplement states `rel-2026-07-20-67d9345f9` as current and marks `rel-2026-07-16-78f075cb0` superseded. **Residue:** `supplementary.tex:6` header comment still asserts "Every empirical value traces to evidence release rel-2026-07-16-78f075cb0" (not reader-facing). → ticket **S14-022** |
| R-07 provenance validator | CLOSED, with a **coverage gap** | Validator runs GREEN and has a `--self-test`. It does **not** check freeze-manifest *filenames* in reader-facing captions, which is why **S14-003** survived it |
| R-08 ISM null not a 4th contribution | CLOSED | Abstract: "The contributions are the dimension-tiered adaptive control, the budget-exact refinement, and a reproducible within-family evaluation … not a single-component gain."; Conclusions: "…rather than as a fourth claimed contribution." C1–C3 only in the Introduction bullets and the cover letter |
| R-09 cover letter | CLOSED | No reviewer block typeset (author-fill note is a LaTeX comment, `cover_letter.tex:73–78`); byte-stability narrowed to "byte-stable determinism for DT-GSK in the declared supported environment" |
| R-10 typo / R-11 vector bounds | CLOSED | `notation_table.tex:39` `$[\ell,u]^D$ … ($\ell,u$ scalar, or per-coordinate $\ell_j,u_j$)`; `proposed_algorithm.tex:51–55` states the per-coordinate box with the uniform special case; Table 10 row "bounds — uniform scalar (ℓ,u) — per-coordinate on CEC2011" |
| R-12 phase-gate write-back / R-13 de-packing | CLOSED (spot-checked) | `phase_gate_register.csv` rows present with evidence; §3.7/§4.1 read as unpacked prose |
| R-14 budget-crossing probe | CLOSED | `tests/regression/test_budget_crossing_semantics.py` referenced in the `performance.tex` evidence comment; the manuscript now states the poisoning result in prose |

## 0.2 Prompt staleness recorded (as instructed)

`PAPER_REVIEW_PROMPT.md` §1.5 is dated 2026-07-20 and predates the 07-21/22 remediation. Beyond that, three **section-10** statements are also stale or unbindable against the repo as it stands. These are recorded, not acted on as manuscript defects (ticket **S14-027**):

1. **§10.1 artifact binding is broken.** The table at line 3177 binds `STATISTICAL_ANALYSIS_PLAN` to `papers/governance/statistical_analysis_plan.md`. That file **does not exist**. The frozen plan is at `papers/build_prompt_phases/phase_05/statistical_analysis_plan.md` (verified by `find`). Any seat that resolves the binding literally will report a missing governance artifact.
2. **§10.7 RT-001 describes a remedy that was not executed.** The prompt (line 3299) says the runtime table is being brought into single-environment comparability "by re-timing all six comparators on one idle machine (`scripts/retime_comparators.py`)" and that the review should "confirm rather than re-discover" its completion. The comparators were **not** re-timed. The actual resolution was the opposite: `tab:runtime` (Table 16) now tabulates **DT-GSK only**, and the caption/prose disclaim any cross-algorithm runtime comparison. The released `cost_cec2017.csv` still carries all seven rows with `comparability=NOT-COMPARABLE-ACROSS-ALGORITHMS (RT-001 …)`. The state is *resolved-by-removal*, not *resolved-by-re-timing*. See **S14-011** for the scientific consequence.
3. **§10.9's narrowing describes a brevity the manuscript no longer respects.** The note (lines 3327–3340) sanctions the advertised ISM null "**now briefly**: one abstract sentence plus the introduction's supporting-component paragraph". The null is in fact stated in at least seven reader-facing places plus twice in the cover letter (enumerated in **S14-012**). Per the instruction not to re-raise the advertised null as a §10.9 leak, this is filed as a redundancy/scope ticket, not a compliance failure.

Where §1.5 or §10 contradicts the repo, the repo governs (§1.4 precedence) and I reviewed the repo.

---

# 1. Section-by-section review

Location convention: `file:line` for sources, `PDF p.N` for the rendered main manuscript, `S<n>.<m>` for supplement sections.

---

## 14.1 Title

**purpose.** Name the subject (a GSK-family optimizer), the central contribution (dimension-tiered control + a deterministic refinement), and bound the scope for indexing.

**strengths.**
- Accurate at the tested scope. "Dimension-Tiered Adaptive Control and Deterministic Refinement" names exactly C2 and C1, and nothing the evidence cannot carry.
- Free of every proscribed term in the §14.1 list. No "robust", "efficient", "large-scale", "high-dimensional", "state-of-the-art", "general", no superlative, no "novel".
- 14 words, single colon, acronym expanded in the same line — MDPI-conformant and citable.
- The earlier title that named the null was removed per §10.9's removal note; the supplement title (`supplementary.tex:79`) matches the main title exactly (verified string-equal on the substantive part).

**critical_or_major_findings.** None.

**moderate_minor_findings.**
- The title's expansion of the acronym is implicit: "DT-GSK" is glossed as "Dimension-Tiered Gaining-Sharing Knowledge" only in the abstract and abbreviations table, while the title reads "Dimension-Tiered Adaptive Control … for Gaining-Sharing Knowledge Optimization". Harmless, but a reader meeting the title alone cannot decode "DT". (Minor, editorial.)

**missing_content.** Nothing required.

**claims_to_narrow.** None.

**recommended_structure.** Keep as is.

**example_revision_only_after_fact_check.** Not needed.

**score_1_to_5:** **4**

---

## 14.2 Abstract

**purpose.** State the gap, the mechanism, the verified evaluation scope, one bound headline number, the qualifications, and a conclusion within evidence.

**Verified facts.** 197 words (limit 200 for *Algorithms*) — computed by stripping macros/comments from `main.tex:127–153`. Zero citations. One headline number (2.48). Every number checked: `friedman_ranks_cec2017_overall.csv` gives dt-gsk `2.482759`, egsk `2.961207`; per-dimension firsts at D10/D50/D100 and second at D30 confirmed from `friedman_ranks_cec2017_D{10,30,50,100}.csv`.

**strengths.**
- Genuine loss-visibility parity (§10.7): the unfavorable cells (second at D=30, second on CEC2011 with a Holm-significant loss, never Nemenyi-separable from eGSK) sit in the *same* paragraph as the headline, not after it.
- Development-suite exposure is disclosed **in the abstract** ("CEC2017 was configuration-selection exposed; CEC2011 and CEC2013 are corroborative"). Very few benchmark papers do this; it is the strongest single editorial decision in the manuscript.
- The contribution sentence explicitly denies a single-component gain, closing R-08.
- Panel scoping is stated twice (in-sentence and as a closing sentence), foreclosing the §10.5 over-generalisation.

**critical_or_major_findings.** None at abstract level; the abstract inherits **S14-005** (the Introduction's stronger "answers in the negative" is *not* in the abstract, which correctly says "no detectable standalone benefit").

**moderate_minor_findings.**
- **S14-013 (Moderate).** The headline number is not scoped to CEC2017 in the sentence that carries it. `main.tex:138–142` reads: "Against six GSK-family baselines **on CEC2017 (primary), CEC2011, and CEC2013** … DT-GSK attains the best overall Friedman mean rank in the seven-algorithm GSK-family panel (2.48 …)". 2.48 is a CEC2017-only aggregate (`friedman_ranks_cec2017_overall.csv`); on CEC2011 DT-GSK is **second** (3.36 vs eGSK 2.52). "first at three of four dimensions" is the only cue that the suite is CEC2017. The next sentence repairs it, but the first reading over-states.
- **S14-013b (Minor).** "It is second behind eGSK at $D=30$ and on CEC2011 (**a Holm-significant loss**)" — the parenthetical is true only of CEC2011 ($p_\mathrm{Holm}=4.2\times10^{-2}$); at D=30 the outcome is **not** significant ($p_\mathrm{Holm}=0.199$, Table 14). The ambiguity runs against the authors' own interest but is still an inaccuracy.
- **S14-014 (Minor).** "the two are **never** Nemenyi-separable" is unbounded across all three suites. The manuscript prints a Nemenyi CD only for CEC2017 (1.67, §4.2.3 + Fig. 4) and mentions CEC2011's 1.92 in passing (§4.3). No CEC2013 CD appears anywhere in main text or supplement. I recomputed from the release and the claim **does** hold on CEC2013 (k=7, N=28 → CD=1.703; largest DT-GSK–eGSK gap is 1.464 at D=10), so the statement is true — but it is not verifiable from the manuscript.

**missing_content.** Nothing mandatory. (No uncertainty interval accompanies 2.48; acceptable, since the BCa intervals are declared descriptive and live in S2.)

**claims_to_narrow.**
- "best overall Friedman mean rank" → "best overall CEC2017 Friedman mean rank".
- "never Nemenyi-separable" → "never Nemenyi-separable on CEC2017" (or print the CEC2013/CEC2011 CDs).

**recommended_structure.** Unchanged; the current order (gap → mechanism → scope → headline+counterweights → exposure → null → contributions → scope bound) is correct.

**example_revision_only_after_fact_check.**
> before: "…DT-GSK attains the best overall Friedman mean rank in the seven-algorithm GSK-family panel (2.48, a descriptive across-dimension mean), first at three of four dimensions. It is second behind eGSK at $D=30$ and on CEC2011 (a Holm-significant loss), and the two are never Nemenyi-separable."
> after: "…DT-GSK attains the best overall **CEC2017** Friedman mean rank in the seven-algorithm GSK-family panel (2.48, a descriptive mean over the four dimensions), first at three of the four. It is second behind eGSK at $D=30$ — a difference the paired test does not resolve — and second on CEC2011, where the loss to eGSK is Holm-significant; on CEC2017 the two are never Nemenyi-separable."
> (word count after edit: 203 → trim "a budget-fair paired protocol" to "a budget-fair protocol" to stay ≤200.)

**score_1_to_5:** **3**

---

## 14.3 Keywords

**purpose.** Indexing and discoverability.

**Verified facts.** Ten keywords (`main.tex:156–167`), identical in the supplement. MDPI *Algorithms* asks for three to ten — at the cap but conformant.

**strengths.** Mixes method terms (adaptive operator selection, population-size reduction), evaluation terms (CEC benchmark suites, nonparametric statistical comparison) and an integrity term (reproducibility). Good spread across the reader populations the paper serves.

**critical_or_major_findings.** None.

**moderate_minor_findings.**
- **S14-023 (Minor).** Two keywords are near-verbatim title strings — "dimension-tiered adaptive control" and "deterministic final refinement" — which §14.3 discourages: they consume slots without adding retrieval paths, because title words are already indexed.
- **S14-023b (Minor).** "interaction-structure memory" is coined by this paper; nobody will search it. The established retrieval terms for this object are *linkage learning* and *variable interaction learning*.

**missing_content.** No keyword covers the sub-field a reader would search from: *linkage learning*, *differential evolution*, or *derivative-free / direct search* (the polish is a compass search). One of these should replace a title-duplicating slot.

**claims_to_narrow.** None.

**recommended_structure.** Swap "dimension-tiered adaptive control" → "linkage learning"; swap "deterministic final refinement" → "direct search". Keep the remaining eight.

**example_revision_only_after_fact_check.** Not needed beyond the swap above.

**score_1_to_5:** **4**

---

## 14.4 Introduction (§1, PDF pp. 1–4)

**purpose.** Establish the regime, summarise the prior state fairly, state a precise gap, declare bounded contributions, and set scope.

**strengths.**
- The funnel is genuinely argued, not formulaic: the CEC regime → the survey call for fewer metaphors and more statistical rigour [3,4] → an explicit commitment to stay inside one family. That is a real motivation, not throat-clearing.
- Each cited variant's weakness is mapped to a named DT-GSK subsystem — a rare and useful piece of exposition.
- The gap is scoped to the cited lineage, twice ("Within this cited family"; §2.3 "a bounded review of the GSK lineage rather than an exhaustive systematic search"). This is exactly the §10.2 novelty bound.
- C1–C3 are bounded rather than inflated: C1 volunteers that the isolation cannot separate the learned basis from the endgame; C2 labels NLPSR "explicitly not claimed as new" and uses "we did not find … among the surveyed GSK variants" instead of "first"; C3's within-family scope is defended as a design choice **and** its exceptions named.
- The roadmap is content-bearing (names what each section specifies), not a table of contents in prose.

**critical_or_major_findings.**
- **S14-005 (Major, P1, Confirmed).** `introduction.tex:72–74` / PDF p. 3: "Whether such a signal, once recovered, improves the optimizer is a hypothesis this paper tests --- and, for GSK at these dimensions, **answers in the negative**." This asserts a *proven* negative. The supplement that supplies the evidence explicitly refuses that reading: S6.6 (`supplementary.tex:2117–2118`) says "This is a **failure to detect an effect under this design, not a demonstration that none exists**", and S6.6 adds "absent a formal equivalence test, this evidence is consistent with zero rather than establishing it" (`:2114–2115`). The very same Introduction later gets it right ("the present component isolation **does not establish** a consistent standalone performance contribution", `:135`). Under §10.9's narrowing, an overstated null is explicitly still a reportable defect.
- **S14-006 (Major, P1, Confirmed).** `introduction.tex:135` states a **post-hoc, explicitly non-pre-registered** result without its exploratory label: "the function-class analysis reveals no systematic advantage on the hybrid or composition categories (Supplementary Materials, Sections S6.5 and S6.6)." S6.6 opens "we ask **post hoc** (this analysis was not pre-registered)" and its Table A-caption reads "**Exploratory; not part of the pre-registered isolation**." Importing an exploratory result into the Introduction stripped of that label is a preregistration-discipline defect (§10.7 multiplicity-family hygiene, by analogy with the BH labelling rule the paper itself obeys in §4.2.3).
- **S14-029 (Moderate→Major, P2, Confirmed).** `introduction.tex:50–62`: "Each documented weakness in this lineage **maps onto** a named subsystem of the algorithm proposed here… And the weakness that no descendant addresses … **is targeted by** the interaction-structure memory (ISM)." Read forward, this promises that ISM answers the identified weakness. The paper's own component evidence returns a null for ISM and the manuscript demotes it to "supporting mechanism". The rhetorical set-up and the finding point in opposite directions and the Introduction never reconciles them; the reconciliation paragraph at `:135` arrives *after* the contribution bullets, so a skimming reader takes the promise and not the retraction.

**moderate_minor_findings.**
- **S14-012 partial (Moderate).** The Introduction carries **two** ISM paragraphs (before the bullets, `:63–82`; after the bullets, `:135`), where §10.9's narrowing sanctions one. The second paragraph also restates the C1 bullet's basis-isolation caveat and §3.4's "supporting mechanism" framing almost clause for clause — near-duplicate content under §10.17.5.
- (Minor) The C3 bullet is 11 lines of continuous prose in the rendered PDF and mixes three distinct things (RNG substreams, seed pairing/config lock, and the panel roster + suites). It is the one place where the manuscript's otherwise controlled sentence length breaks down.
- (Minor) `introduction.tex:29–32` poses the design question as "can a GSK-family algorithm learn … which coordinates … improve together, and can it exploit that record across the tested dimension tiers". The paper answers "not detectably" to the exploitation half — so the paper's stated *central research question* is the one whose answer is null, while the delivered contribution is the scaffold. That mismatch is the root of S14-029 and of §14.13's "bundle of modules without a clear scientific thesis" risk.

**missing_content.** No explicit RQ/hypothesis numbering. §14.4 asks for explicit research questions; here they are prose questions in two places (`:29–32` and `:79–82`) that are never referred to again by name. Section 4 is not ordered by them either (see §14.9). Adding RQ1–RQ3 labels and echoing them in §4 headings would cost ~5 lines and materially improve navigability.

**claims_to_narrow.**
1. "answers in the negative" → "does not, under this design, produce a detectable improvement".
2. "the function-class analysis reveals no systematic advantage" → add "an exploratory, post-hoc breakdown (not pre-registered) finds …".
3. "Each documented weakness … maps onto a named subsystem" → "Each documented weakness … motivates a named subsystem" (motivation, not delivery).

**recommended_structure.** Move the post-bullet ISM paragraph (`:135`) to *immediately before* the contribution bullets and merge it with the `:63–82` paragraph, so the honest framing is read before, not after, C1–C3. This also collapses the duplication flagged in S14-012.

**example_revision_only_after_fact_check.**
> before: "Whether such a signal, once recovered, improves the optimizer is a hypothesis this paper tests --- and, for GSK at these dimensions, answers in the negative."
> after: "Whether such a signal, once recovered, improves the optimizer is the hypothesis this paper tests. Under the design used here, and at the dimensions where the memory is active, no standalone improvement was detected; the result is a bounded non-detection rather than a demonstration that no such effect exists."

**score_1_to_5:** **3**

---

## 14.5 Related Work (§2, PDF pp. 4–9)

**purpose.** Synthesise the family by concept, position the closest external work, and derive the gap.

**strengths.**
- Organised by *what is adapted* (scalar control → donor policy → composite designs) rather than chronologically or as a bibliography catalogue. This is a genuine synthesis and is the strongest-written section of the paper.
- Table 1 (family review) and Table 2 (structure-learning taxonomy) do complementary work: Table 1 bounds the family claim, Table 2 bounds the novelty claim on four named axes (trigger, evaluation cost, what is learned, how exploited).
- Limitations attributed to each variant are source-accurate and card-bound. Spot-checked `alfadli2025atmals.md` and `jawad2024egsk` claims: the ATMALS "D=10 competitive-only" and the eGSK "significantly worse than AGSK at D=10" statements match the evidence cards.
- §2.2 is unusually honest about ISM's own boundaries: "the distinction is not the type of object but the accepted-move-only, signed, decaying accumulation"; "ISM is not claimed to recover the objective's true interaction structure or to confer rotational invariance". This pre-empts the §10.13 "SGSM not distinguished from differential grouping / covariance adaptation / eigenvector operators" rejection risk.
- Citation hygiene is clean: all 40 main-text `\cite` keys are in `allowed_citation_keys.txt` and in `references.bib`; no `\nocite{*}`; 17 bib entries are uncited (permitted by §10.2).

**critical_or_major_findings.**
- **S14-004 (Major, P1, Confirmed)** originates here and lands in §4. `related_work.tex:89–93` reports, correctly and card-bound: "Within the GSK family as measured in that study, **[ATMALS-GSK] ranks first on CEC2017 with eGSK second**" (evidence card `alfadli2025atmals.md:40`: ATMALS-GSK 2.24 first, eGSK 2.84 second; ATMALS-GSK first at D=30/50/100). This manuscript's own re-run (Table 13 / `friedman_ranks_cec2017_*.csv`) inverts that completely: ATMALS-GSK 4.36 overall (**5th of 7**), eGSK 2.96 (2nd); per-dimension ATMALS-GSK 5.29 / 4.19 / 4.31 / 3.66 against eGSK 4.24 / 2.29 / 2.62 / 2.69 — eGSK ahead at every dimension. The manuscript states the published ordering in §2 and the opposite ordering in §4 and **never reconciles them**, in the main text, the supplement, `comparability_audit.md`, or `negative_findings.md` (all greppped). See §14.9/§14.10 for the required correction.

**moderate_minor_findings.**
- (Minor) Table 2's caption asserts "linkage blocks re-extracted **every fifth generation**", while §3.4 (`proposed_algorithm.tex:474–477`) says blocks are re-extracted "every 5 generations --- at $D\ge100$, every 10 and 20 generations respectively" and `:511` says "refreshed every 20 generations ($D{<}50$) or 10 ($D\ge50$)". Three different cadence statements are in play (5 / 10 / 20 by tier and by object). They are reconcilable — the graph, the block extraction, and the crossover-block refresh are different objects — but a reader cannot tell that from the text. (Moderate on clarity; not a numerical error.)
- (Minor) §2.2's DG cost is given as "$O(n^2/m)$ objective evaluations" in prose but "$O(n^{2}/m)$" nowhere in Table 2, which says only "dedicated objective evaluations for the probing stage". Harmonising would strengthen the cost contrast that is the section's core argument.
- (Minor) §2.3 first paragraph repeats §2.1's closing claim ("none learns or exploits the interaction structure…") almost verbatim for the third time in the section. §10.17.5 near-duplicate content.

**missing_content.**
- No non-GSK *empirical* comparator is discussed as a candidate and rejected with a reason. §2.2 positions DG/CMA-ES/eigenvector-DE conceptually, but the reader is never told why none of them was *run*. The Conclusions and S5.4 admit the omission; §2 is where the design decision should be argued.

**claims_to_narrow.** None outstanding — §2 is already the most carefully bounded section.

**recommended_structure.** Add two sentences at the end of §2.2 explaining why the closest external methods are positioned rather than benchmarked (protocol incompatibility / budget accounting / scope), so the omission reads as a decision rather than a gap.

**example_revision_only_after_fact_check.** Deferred: the reason for not running a non-GSK baseline is an author-side fact I cannot verify.

**score_1_to_5:** **4**

---

## 14.6 Problem formulation / background (§3.1 Notation and Base-GSK Recap, PDF pp. 9–11)

**purpose.** Fix the problem class, the notation, and the boundary between inherited and new material.

**strengths.**
- The inherited/new boundary is stated crisply and early (`proposed_algorithm.tex:17–31`, `:82–88`): four inherited elements named, one relaxation named (≤ tie handling), and the claim boundary ("no new base operator is claimed").
- Optimization direction, domain, budget, and the per-coordinate box are all explicit; the outcome direction (minimisation, lower error better, lower rank better) is consistent everywhere I checked.
- Notation is split into a core table plus per-subsystem tables placed at first use (N-015). At 19 rows the core table is readable; this is a real improvement over a single front-loaded key.
- The equation registry (E1a–E12) is transcribed from code with per-equation code anchors, and the ACE update (E6) is unusually honest — it prints all three branches including the "hold π" case, and names the Euclidean simplex projection rather than a floor-and-renormalise.

**critical_or_major_findings.** None.

**moderate_minor_findings.**
- **S14-010 (Moderate, P2, Confirmed).** Notation break between prose and equation. `proposed_algorithm.tex:69–74` (PDF extract line 385): "where $KF$ scales the step and **$s\in\{+1,-1\}$** is the sign of the fitness comparison…". Eq. (4) defines **$s_J$** and **$s_S$**; `notation_table.tex:54` lists **$s_J,s_S$**. Bare `s` is defined nowhere. This is the residue of R-01 and violates the §10.17.6 requirement that symbols be consistent across notation table, equations, prose, and pseudocode.
- (Minor) `proposed_algorithm.tex:88–92` cross-references "Eqs. (1)–(4), (8), and (9)" by label; in the rendered PDF these become (1)–(4), (8), (9). Correct, but the paragraph is a bare enumeration of which equation belongs to which section and reads as machine-generated bookkeeping (§10.17.1 templated cadence). It could be replaced by the "Eq." column that Table 4 already carries.

**missing_content.**
- The senior-phase partition semantics ("split-bottom 0.10 at $D\ge50$", Table 5) is a *modification* of the inherited operator but is not described in §3.1's inherited/new accounting, which names only the crossover mask, the ≤ tie rule, the $KR$ floor, the DE arm, the senior partition, and NP. "the senior partition" is listed but never explained — the reader learns what changed only from a parenthetical in Table 5. One sentence is needed.

**claims_to_narrow.** None.

**recommended_structure.** Keep. Replace the equation-inventory paragraph with a pointer to Table 4's "Subsystem (Eq.)" column.

**example_revision_only_after_fact_check.**
> before: "…and $s\in\{+1,-1\}$ is the sign of the fitness comparison between the individual and the knowledge source its phase compares against --- the random peer $R_3$ in the junior phase and the middle-group source $R_2$ in the senior phase --- exactly as in the published operator."
> after: "…and the per-phase sign — $s_J$ in the junior phase, which compares the random peer $x_{R_3}$ against $x_i$, and $s_S$ in the senior phase, which compares the middle-group source $x_{R_2}$ against $x_i$ — takes $+1$ when the compared source is fitter, exactly as in the published operator (Eq. (4))."

**score_1_to_5:** **4**

---

## 14.7 Proposed method (§3.2–§3.8, PDF pp. 11–22)

**purpose.** Specify the method completely enough to reimplement; state design rationale, parameters, safeguards, complexity, cost, and the exact test of each contribution.

**strengths.**
- **Specification completeness is the paper's best asset.** Every mechanism has trigger, timing, parameters, cost, and a tier gate; the frozen configuration is tabulated (Table 10 core + S5.7 per-subsystem detail); the loop order is stated three ways (numbered prose list, Algorithm 1, Fig. 2) and they agree step for step (checked all 13 steps).
- Dimension-tier gating is stated once and then held (`:212–221`), and Table 5 gives the activation matrix. This is exactly the discipline §10.6 asks for.
- Honest labelling throughout: NLPSR "explicitly not claimed as new"; ACE "is not an instance of those algorithms, and no regret bound is claimed"; the polish "no convergence guarantee is claimed"; "We claim no complexity improvement over GSK".
- Dead/dormant code is disclosed rather than hidden (`:504–505`, `:519–524`, `:627–633`): the ISM-block subspace local search is implemented-but-disabled, a trust-region governor was removed at freeze, a linkage-reliability gate is never instantiated. This directly closes the historical ISM-C001 concern.
- The determinism subsection separates three reproducibility levels (RNG-substream isolation / same-environment trajectory repeatability / artifact byte-identity) and scopes all three to DT-GSK only. That three-way distinction is more careful than most published reproducibility statements.
- Algorithm 1 renders cleanly at 25 numbered steps with four labelled phases and booktabs-style framing; no overflow, no double-print (verified on the rendered page).

**critical_or_major_findings.**
- **S14-003 (Major, P1, Confirmed).** Table 10's caption (rendered PDF p. 20; source `phase_03/parameter_table.tex:14–15`) states: "**Hash-frozen in `algorithm_freeze_manifest.json`**." The supplement flatly contradicts this (`supplementary.tex:1123–1134`): "The four SHA-256 prefixes recorded in the original freeze manifest are therefore **historical**: they pin the pre-fix sources under their pre-rename filenames and **do not match the shipped modules**. A current manifest, `algorithm_freeze_manifest_2026-07-19.json`, was minted from the post-fix source…". Both files exist (`papers/build_prompt_phases/phase_03/`). The main manuscript therefore points a reader at a **superseded** authority for the shipped configuration's hash freeze. `validate_provenance_claims.py` passes because its authority-context rule covers release IDs, not manifest filenames — so this is exactly the class of defect R-07 was hardened against, one file-name away.

**moderate_minor_findings.**
- (Moderate) §3.8's budget-crossing paragraph (`:783–787`) describes **DT-GSK's** truncation only ("only the prefix that fits is evaluated and charged, so runs are MaxFES-exact by construction"), while the comparators' different semantics appear 300 lines later in §4.1. A reader of §3 alone will assume all seven behave identically. One cross-reference sentence in §3.8 fixes it.
- (Moderate) **Cadence statements conflict across §3.4** — see §14.5 above. `:474–477` (graph every generation; blocks every 5; at D≥100 every 10 and 20) vs `:511` (blocks "refreshed every 20 generations ($D{<}50$) or 10 ($D\ge50$)") vs Table 2 caption ("every fifth generation"). At minimum these must be labelled by object (graph update / block extraction / crossover-mask refresh) and by tier in one place.
- **S14-018 (Minor).** Tables 4, 5 and the notation tables use justified `p{}` columns, producing visible inter-word rivers in the first column of Table 4: "Inherited  GSK  core", "4.        ISM interaction-structure memory", "5.   Local   search", "7.  High-*D*  controllers (basin      memory,". §10.17.1/§10.17.7 (visual-communication quality). Fix: `>{\raggedright\arraybackslash}p{...}`.
- **S14-019 (Minor).** Algorithm 1 line-wrap defects (rendered PDF p. 10): step 12 wraps twice and its right-aligned "▷ Eq. (5)" annotation lands on the **third** line; step 14's comment wraps so that "non-selectable" starts flush at the **left margin**, below the step-number column, reading as a stray line. §10.17.2 requires "wrapped-line hanging that never collides with the margin".
- **S14-020 (Minor).** Figures 1 and 2 (the two flowcharts) render in Computer Modern while the body is the MDPI Palatino-family font — a visible typographic seam on two full-page exhibits. Standalone TikZ builds default to CM; the fix is to load the same text font in the flowchart preamble.
- (Minor) Figure 1 occupies a full page (p. 11) with roughly a third of the page blank, in a 39-page manuscript. §10.17.7 explicitly targets "a listing that leaves large unused page regions".
- **S14-026 (Minor).** Table 10's footnote points to "Supplementary Material, **Section S5**" for the per-subsystem constants; the actual location is **S5.7** ("Frozen Parameters: Per-Subsystem Detail"). S5 is 30 pages. Also, exposing the raw filename `algorithm_freeze_manifest.json` in a reader-facing caption is an internal engineering noun under §10.17.4.

**missing_content.**
- **The exact test of each contribution is not stated in §3** (a literal §14.7 requirement). C1's test lives in S6.5, C2's in S6.1–S6.3, C3's in S5. §3 gestures at them ("examined in a remove-one component study in the Supplementary Materials") but never says *what would falsify* each contribution. Two sentences per contribution would close this.
- No worked example or trace for the ISM update. Table 9 is a three-row narrative; the reader never sees what a linkage block looks like. Table 7 does this well for NLPSR; the equivalent for ISM is absent.

**claims_to_narrow.**
- Table 10 caption "Hash-frozen in `algorithm_freeze_manifest.json`" → name the current manifest, or drop the filename and say "hash-frozen in the repository's current freeze manifest; see Supplementary Material S5.2 for the manifest chronology".
- `:598` "so it cannot corrupt any reported result" — true as stated (strict-improvement accept), but "corrupt" is stronger than needed; "cannot worsen" is the accurate verb.

**recommended_structure.** Keep the ordering. Move the budget-crossing comparator disclosure sentence from §4.1 into §3.8 (or cross-reference), and consolidate the three ISM cadence statements into one sentence in §3.4 plus one row in Table 5.

**example_revision_only_after_fact_check.**
> before (Table 10 caption): "No tuning is required or permitted at run time. Hash-frozen in `algorithm_freeze_manifest.json`."
> after: "No tuning is required or permitted at run time. The shipped configuration and its implementing sources are hash-frozen and machine-checked on every run; the freeze-manifest chronology, including the superseded original manifest, is given in Supplementary Material S5.2."

**score_1_to_5:** **4**

---

## 14.8 Experimental setup (§4.1, PDF pp. 22–25)

**purpose.** Make the study checkable: scope, runs, seeds, budgets, comparator provenance, tuning, environment, failures, statistics, availability.

**strengths.**
- **Development-suite exposure disclosed, and disclosed early** (`performance.tex:103–111`), with the reasoning that CEC2017 standing "should accordingly be read as development-suite performance". S5.3 goes further and admits that intermediate candidate configurations were compared before promotion and are *not* in the immutable release. Very few benchmark papers make this admission.
- The APGSK evidence gap is disclosed "up front" with the recovery footnote handled exactly as §10.7's recovery-versus-comparability disposition requires: the seed-deterministic recovery is acknowledged, the frozen function-level basis is conservatively retained, and no claim is upgraded.
- The comparator budget-crossing asymmetry (R-05) is disclosed **and** the fairness verification stated: strict truncation leaves "the returned solution, its fitness, and the charged budget bit-identical for all seven optimizers".
- The self-initialization exception is stated three times (protocol table, pairing paragraph, §3.8) and never softened; the pairing key is correctly redefined as seed/problem/run rather than shared $X_0$.
- The seed formula is printed in full, and the recomputation audit (70,813 rows, 0 mismatches) is stated with its denominator.
- The tie-band's scale-dependence is confronted rather than defended: "a coarse convention across functions of very different scales, so the win/tie/loss tallies are a *descriptive* companion only" — plus a sensitivity analysis in S5.5.
- The comparator-kernel FP-probe gap is disclosed as a residual limitation rather than glossed.

**critical_or_major_findings.**
- **S14-001 (Major, P1, Confirmed)** — the effect-size paragraph, detailed in §14.9 below, originates here (`performance.tex:209–231`) and is internally self-contradictory: the same paragraph says "**the tabulated effect size is the matched-pairs rank-biserial correlation $r$**" and, eleven lines later, "**The tabulated $A_{12}$ is computed over the 29 per-function mean errors**". Only one quantity is tabulated (it is $r$; `papers/tables/T15.tex` header row is `$p$, $p_\mathrm{Holm}$, $+$, $\approx$, $-$, $r$, Dec.`).
- **S14-002 (Major, P1, Confirmed)** — the tie-correction paragraph (`:250–262`) declares "the Friedman statistic uses the tie-corrected rank variance that underlies the Iman--Davenport $F$" and invites the reader to check ("Both are released per panel in `friedman_ranks_*.csv` so the correction can be checked directly"). The omnibus p-values actually printed for CEC2017 and CEC2013 are the **uncorrected** column. Full evidence in §14.9.

**moderate_minor_findings.**
- (Moderate) The Holm family is declared as "six simultaneous comparators at that dimension" — correct — but the §4.1 statement never says what the family is for **CEC2011** and **CEC2013**. §4.3 later says "at the same family size" (6) and §4.4 quotes Holm-corrected CEC2013 values; the reader must infer. §10.7 requires every family's size to be stated.
- (Minor) "the analysis pipeline (SciPy 1.15.3) runs restricted so that it can read only that release" — the mechanism (strict-source guard) is named nowhere in the main text, and the sentence reads as an assertion. One clause naming the guard (as S5 does) would make it checkable.
- (Minor) The paragraph on GenAI (`:189–193`) sits inside *Environment and determinism*, where it has no topical home; it belongs with the declarations or as its own labelled paragraph.
- (Minor) Failure handling is specified for CEC2011 (the $10^{30}$ infeasibility penalty) but nothing is said about failed/aborted runs on CEC2017/CEC2013 — were there any? §14.8 asks explicitly for "failures". The release presumably has none, but the manuscript should say so.

**missing_content.**
- **Comparator implementation provenance is asserted, not evidenced.** Table 11 says five comparators use "published reference constants; in-repository re-run", but the manuscript gives no pointer to where those constants are recorded or how faithfulness was checked. `comparability_audit.md` has the per-optimizer commit table; one sentence citing it would convert an assertion into a checkable claim — and it is the natural place to pre-empt **S14-004**.

**claims_to_narrow.** None beyond S14-001/S14-002 corrections.

**recommended_structure.** Split the statistical-protocol paragraph into (a) tests and families, (b) effect sizes, (c) intervals and correction diagnostics. It currently runs 36 source lines and is where both major statistical defects hide.

**example_revision_only_after_fact_check.** See §14.9.

**score_1_to_5:** **4**

---

## 14.9 Results (§4.2–§4.6, PDF pp. 25–34)

**purpose.** Present all primary evidence in a defensible order, before interpretation, with uncertainty and effect visible and adverse findings retained.

**Numbers independently re-verified against `papers/analysis/rel-2026-07-20-67d9345f9/` (all agree unless noted):**

| Manuscript statement | Source | Verdict |
|---|---|---|
| Overall ranks 2.48 (DT-GSK) / 2.96 (eGSK) | `friedman_ranks_cec2017_overall.csv` (2.482759 / 2.961207) | ✔ |
| Per-dim 2.88 / 2.50 / 2.21 / 2.34; eGSK D30 2.29 | `friedman_ranks_cec2017_D*.csv` | ✔ |
| W/T/L vs GSK 22-4-3, 19-2-8, 22-0-7, 20-0-9 | `T15.tex` | ✔ |
| W/T/L vs eGSK 11-2-16, 13-0-16, 12-0-17 | `T15.tex` | ✔ |
| 17 wins / 7 ties / 0 losses of 24 | recount of `T15.tex` decision columns (3+5+5+4 wins; 3+1+1+2 ties) | ✔ |
| Global-Holm sensitivity: 15 of 24 survive; the two lost are ATMALS-GSK D10 (0.0362) and GSK D30 (0.0295) | `T15.tex` + `global_holm_sensitivity_cec2017.csv` | ✔ |
| CD = 1.67, $q_{0.05}$ = 2.949 | $2.949\sqrt{7\cdot8/(6\cdot29)}=1.6730$ | ✔ |
| CEC2011: 3.36 vs eGSK 2.52; $F=4.27$, $p=6.0\times10^{-4}$; loss $p_\mathrm{Holm}=4.2\times10^{-2}$; GSK head-to-head $R^+=159$, $R^-=51$, $p=0.0458$, $p_\mathrm{Holm}=0.137$, 13-2-7 | `friedman_ranks_cec2011.csv`, `T06.tex` | ✔ |
| CEC2013 overall 2.80 / eGSK 3.41; per-dim 2.41 / 3.38 / 2.61; D30 third behind eGSK 3.07 and ATMALS-GSK 3.34 | `friedman_ranks_cec2013_*.csv` | ✔ |
| Class ranks (hybrid 1.60/1.80/2.30; simple multimodal 2.07/3.29/2.29/1.71; composition 3.70/2.85/2.50/2.90) | `class_ranks_cec2017.csv` | ✔ |
| Runtime 4.93 / 13.04 / 23.30 / 41.59 s; CEC2013 4.45–34.26 s; CEC2011 80.64 s | `cost_cec2017.csv` (dt-gsk rows) | ✔ |
| **CEC2017 omnibus "$p\le2.6\times10^{-8}$"** | corrected max is $1.16\times10^{-9}$; **$2.577\times10^{-8}$ is the D10 *uncorrected* p** | ✘ |
| **CEC2013 omnibus $3.3\times10^{-7}$ / $2.2\times10^{-3}$ / $9.2\times10^{-6}$ and caption "$p\le2.3\times10^{-3}$"** | corrected are $5.3\times10^{-8}$ / $1.09\times10^{-3}$ / $2.9\times10^{-6}$; the printed values are the **uncorrected** column | ✘ |
| **"$A_{12}$ effect sizes" in Table 14** | Table 14 has **no** $A_{12}$ column; it has rank-biserial $r$ | ✘ |

**strengths.**
- **Loss-visibility parity is genuinely achieved.** Every favourable cell is qualified in the same paragraph: the first places at $D\ge50$ are explicitly said to be "earned by consistency against the whole panel, not by dominating eGSK"; the non-monotone rank trend is stated; the D=100-vs-GSK non-significance is stated; the D=10 first place is decomposed into which three wins carry it.
- The "Overall" column is correctly labelled a descriptive aggregation "with no cross-dimension test attached", and the Iman–Davenport attribution is explicitly restricted to the per-dimension omnibus — exactly the §10.7 descriptive-overall-rank disposition.
- BCa intervals are correctly downgraded to *descriptive rank-stability* intervals with the reason given (they resample fixed midranks rather than re-ranking).
- The robustness battery discloses **divergences** rather than burying them: median re-ranking swaps two comparator pairs and turns the D=100 first place into an exact tie with eGSK; disputed-cell exclusion swaps GSK and FDB-AGSK at D=30. The manuscript states these and then explicitly says "panel orderings between comparators are not fully robust". This is a §10.7 robustness-divergence disclosure done right.
- The convergence subsection retains the mandated adverse case (F26 at D=30) and discusses it at length rather than skipping it, including the uncomfortable detail that DT-GSK's best run never reaches the attractor every comparator's best run reaches.
- $p<10^{-4}$ is reported as bounded, never "0.0000" (verified in T15).

**critical_or_major_findings.**

- **S14-001 (Major, P1, Confirmed) — the manuscript describes a table column that does not exist, and contradicts itself about which effect size is tabulated.**
  Evidence: `papers/tables/T15.tex` header is `$p$ & $p_{\mathrm{Holm}}$ & $+$ & $\approx$ & $-$ & $r$ & Dec.`; the released `wilcoxon_holm_cec2017_D*.csv` carries a `rank_biserial` column and **no** `a12` column (verified by header read); Table 14's caption correctly says "the matched-pairs rank-biserial effect size $r$".
  Yet: `performance.tex:361–364` "Table 14 reports … win/tie/loss counts, **$A_{12}$ effect sizes**, and Holm decisions"; `:364–368` "**The $A_{12}$ column** is computed over the 29 per-function means…"; `:405–411` quotes "$A_{12}$ of 0.490, 0.505, and 0.472" for the eGSK cells, where Table 14 prints $r=-0.286$, $-0.002$, $-0.057$; `:425–426` "the largest effect is against APGSK at $D=100$ ($A_{12}=0.712$)", where Table 14 prints $r=+0.977$.
  I recomputed the quoted $A_{12}$ values from the release (unpaired $A_{12}$ over the 29 per-function means from `descriptive_stats_cec2017_D*.csv`): 0.4905, 0.5054, 0.4721, 0.7122 — so **the numbers are correct and re-derivable**, but they are printed in **no exhibit** of the paper or supplement, and the prose attributes them to a column that was replaced by rank-biserial in the M-027 migration. The migration updated the table and the caption but only half the prose.
  Impact: a reviewer who opens Table 14 to check "the $A_{12}$ column" will not find it; a reviewer who compares the two effect-size sentences in §4.1 will find them contradictory; and "the largest effect" is asserted on a scale the reader cannot see. No inference changes (the signs agree), which is why this is Major and not Critical.

- **S14-002 (Major, P1, Confirmed) — the printed omnibus p-values are the uncorrected column, while the text declares the corrected statistic and invites the reader to check the released CSVs.**
  Evidence (all from `friedman_ranks_*.csv`, columns `p_value` vs `p_value_uncorrected`):

  | Cell | printed | corrected `p_value` | uncorrected `p_value_uncorrected` |
  |---|---|---|---|
  | CEC2017, bound used at `:317` and in the Table 13 caption `:338` | $\le 2.6\times10^{-8}$ | max over D is $1.16\times10^{-9}$ | **D10 = $2.577\times10^{-8}$** |
  | CEC2013 D10 `:623` | $3.3\times10^{-7}$ | $5.32\times10^{-8}$ | **$3.264\times10^{-7}$** |
  | CEC2013 D30 `:625` | $2.2\times10^{-3}$ | $1.090\times10^{-3}$ | **$2.242\times10^{-3}$** |
  | CEC2013 D50 `:626` | $9.2\times10^{-6}$ | $2.909\times10^{-6}$ | **$9.212\times10^{-6}$** |
  | CEC2013 caption `:599` | $\le 2.3\times10^{-3}$ | max is $1.09\times10^{-3}$ | **$2.242\times10^{-3}$** |
  | **CEC2011 `:529–530`** | $F=4.27$, $p=6.0\times10^{-4}$ | **$F=4.2669$, $p=6.008\times10^{-4}$** ✔ | $F=3.669$, $p=2.16\times10^{-3}$ |

  So CEC2011 quotes the **corrected** pair and CEC2017/CEC2013 quote the **uncorrected** one — the manuscript is inconsistent with itself across suites, and inconsistent with `:250–253` ("the Friedman statistic uses the tie-corrected rank variance that underlies the Iman--Davenport $F$"). The direction is conservative ($C\le1$ so correction only lowers $p$) and no decision changes — which the manuscript itself asserts at `:258–261` and which I confirmed. Nonetheless the printed numbers do not match the column the reader is told to check.
  Corroborating: the tie-correction diagnostics quoted at `:256–257` ($C=0.890$ at D10 covering 9 of 29 functions; $C=0.979$ at D30; $C=1$ exactly at D50/D100) **are** correct (0.889778 / 0.979064 / 1.0 / 1.0; `n_tied_functions` 9/3/0/0). The defect is confined to the omnibus p-values.

- **S14-004 (Major, P1, Confirmed) — the re-run inverts a comparator's published in-family standing and the manuscript never reconciles it.** Detail in §14.5; the results-side facts are Table 13 (ATMALS-GSK 5.29/4.19/4.31/3.66, overall 4.36, 5th of 7) against the source's own Table 18 (ATMALS-GSK 2.24 first, first at D=30/50/100). §4 reports the numbers and moves on. `negative_findings.md` (Phase 6) records nine adverse findings but not this one; `comparability_audit.md` mentions ATMALS-GSK only for its lack of hidden LS evaluations. A reviewer of a paper whose comparators were largely authored by two of its authors will read an unexplained 3-rank demotion of the strongest published competitor as the single most damaging fact in the submission. It is very probably innocuous (different panel composition, a genuinely different budget-fair protocol, no local-search budget exemption) — but it must be said out loud.

**moderate_minor_findings.**
- **S14-011 (Moderate).** No comparative non-objective overhead figure appears anywhere. §4.6 reports DT-GSK's own wall-clock and disclaims cross-algorithm comparison (correct, given the two measurement sessions), but the reader is left with no answer at all to "what does the scaffold cost relative to base GSK?" The released `cost_cec2017.csv` shows DT-GSK 4.93 s vs GSK 0.55 s at D=10 (≈9×) and DT-GSK 41.59 s vs GSK 40.98 s at D=100 (≈1.0×) — i.e. the honest picture is *unfavourable at low D and favourable at high D*, so the omission is not selective, but §10.13 lists "missing non-objective overhead analysis" as a hard rejection risk and §14.10 requires cost and trade-offs to be explicit. This is the scientific consequence of the RT-001 resolve-by-removal recorded in §0.2.
- (Minor) §4.2.1 discusses three of the four CEC2017 function classes and silently omits **unimodal** (F1, F3), where the release shows DT-GSK 4.00 (7-way tie) at D=10, 2.50 at D=50 and 2.00 (best) at D=100. Omitting a favourable class is not a loss-visibility problem, but §14.9 asks that all primary evidence appear.
- (Minor) §4.2.3's sentence "the largest effect is against APGSK at $D=100$" would remain true under $r$ (+0.977 is the largest tabulated), so the fix for S14-001 does not disturb the claim — worth noting for the remediation.
- (Minor) The results are ordered by suite (CEC2017 → CEC2011 → CEC2013) rather than by research question, and the Introduction's two prose questions are never answered by name. §14.9 asks that "order follows research questions".
- (Minor) §4.5's F26/D=30 discussion is excellent but the parallel adverse case at $D=100$ (F26 "comparable") is reported as bare numbers with no interpretation, so the section's one interpretive paragraph is single-sided.

**missing_content.**
- A short "what did not reproduce" paragraph. The paper has a robustness subsection and a negative-findings discipline; the natural home for S14-004 is a two-to-four-sentence paragraph at the end of §4.2 comparing the re-run panel standings against the comparators' published in-family standings, saying which reproduce (eGSK's D=10 weakness does — Table 13 gives eGSK 4.24, 6th of 7 at D=10, matching `jawad2024egsk`'s own reported D=10 deficit) and which do not.

**claims_to_narrow.**
- Replace "$A_{12}$" with "$r$" wherever Table 14 is described, or reinstate an $A_{12}$ column; do not describe both as "the tabulated effect size".
- Re-quote every omnibus p from the `p_value` column, or state explicitly "uncorrected values are quoted; the tie-corrected values are smaller and are released in `friedman_ranks_*.csv`".

**recommended_structure.** Insert the reconciliation paragraph (S14-004) at the end of §4.2.2, immediately after the panel table, where the reader first meets the surprising ordering.

**example_revision_only_after_fact_check.**
> before: "Table 14 reports the across-function Wilcoxon tests with Holm correction, win/tie/loss counts, $A_{12}$ effect sizes, and Holm decisions … The $A_{12}$ column is computed over the 29 per-function means, on the same unit as the Wilcoxon test, and is therefore distinct from the run-level $A_{12}$ reported in the effect-size workbook; the two are not interchangeable."
> after: "Table 14 reports the across-function Wilcoxon tests with Holm correction, win/tie/loss counts, the matched-pairs rank-biserial effect size $r$, and Holm decisions … $r$ is the effect size aligned with the paired test: it is computed from the same signed-rank sums, so its sign and the test agree by construction. The distributional companion $A_{12}$, computed over the same 29 per-function means, is released with the analysis bundle; a third, run-level $A_{12}$ appears in the effect-size workbook, and the three are not interchangeable."
>
> before (S14-004, new text — the numbers below are all from Table 13 and the cited evidence cards):
> after: "One panel ordering differs from the comparators' published self-assessments and should be stated plainly. Under this protocol ATMALS-GSK ranks fifth of seven overall (4.36) and behind eGSK at every dimension, whereas its own study reports it first within the GSK family on CEC2017 with eGSK second [10]. eGSK, by contrast, reproduces the low-dimension weakness its authors report [9] (4.24 at $D=10$, fifth of seven here and its worst dimension). We cannot attribute the ATMALS-GSK difference from these data: the panel composition, the shared-initialization protocol, and the uniform budget accounting all differ from the original study, and no re-tuning of any comparator was performed. We therefore read the ATMALS-GSK cells as its performance under *this* protocol and not as a re-assessment of the published result."

**score_1_to_5:** **3**

---

## 14.10 Discussion (§4.7, PDF pp. 33–34)

**purpose.** Interpret rather than repeat; consider alternative explanations; label mechanism claims correctly; compare fairly with the literature; make cost explicit; bound generalisation; address instability.

**strengths.**
- Mechanism language is correctly labelled throughout: "stated here as plausibility, not as a measured component contribution"; "this reading associates the high-dimension behavior with the bundled tier configuration rather than with any isolated component"; "per-component causal attribution is deliberately not claimed in this paper". This is precisely the §10.13 "mechanism explanations based only on final performance" defence.
- The "one calibrated statement" paragraph is a model of disciplined summarising: it states the two-of-three-suites result, the eGSK mid-dimension advantage, and the CEC2011 Holm-significant loss in one sentence, then attaches the robustness qualification.
- No-free-lunch is invoked correctly — as a bound on generalisation, not as an excuse.
- Contradictory/unstable results are addressed (non-monotone trend, comparator ordering instability under median re-ranking).

**critical_or_major_findings.**
- **S14-008 (Major, P2, Confirmed).** §14.10 requires that alternative explanations be considered. The single most obvious alternative explanation for the headline standing is never named: that it may rest on (i) the deterministic endgame — a generic direct-search technique — and (ii) configuration selection on the development suite, rather than on any component the paper claims as new. The evidence for the shape of this concern is in the supplement (S6.5 identifies the final-polish contrast as the only isolated Holm-significant one at these tiers; S6.5 further states the significant effect is "the compass endgame, not the learned basis specifically"; S5.3 states the configuration was selected on CEC2017). §10.9 forbids importing the favourable polish result into the main text, so the fix is **not** to state it: the fix is a result-free paragraph naming the competing explanations and pointing to where the component evidence lives. As written, the Discussion enumerates what is *not* claimed but never states what the leading rival account *is*, which reads as avoidance rather than caution.
- **S14-004 (Major, P1)** — "comparison with literature is fair" is a §14.10 requirement, and the ATMALS-GSK inversion is a literature comparison the Discussion does not make. See §14.9.

**moderate_minor_findings.**
- **S14-011 (Moderate)** — "cost and trade-offs are explicit" is a §14.10 requirement. The Discussion never mentions cost at all; §4.6 gives DT-GSK's absolute times and no comparison. See §14.9.
- (Moderate) The Discussion is a set of four labelled paragraphs (*By function class*, *By dimension*, *By aggregate counts*, then the calibrated statement) whose first three largely re-present §4.2's numbers with an interpretive clause attached. §14.10 warns against repetition; roughly half the Discussion's sentences restate figures already given two pages earlier (e.g. 11-2-16 / 13-0-16 / 12-0-17 appears in §4.2.2, §4.7, **and** the Conclusions; 2.88/2.50/2.21/2.34 appears in §4.2.2, §4.2.3, §4.7 and the Conclusions).
- (Minor) "the mechanisms of Section 3 are proposed and fully specified" is used as a hedge for a plausibility claim; "proposed and fully specified" says nothing about whether the mechanism produced the effect, so as a hedge it is a non-sequitur. The honest hedge is the one used two lines later ("stated here as plausibility").

**missing_content.**
- No practical-meaning paragraph. §14.10 asks for practical meaning without speculation: who should use DT-GSK, at what dimensions, at what compute cost, and when a comparator would be preferable (on this evidence: eGSK at $D=30$ and on real-world formulations). The paper has the evidence for such a paragraph and does not write it.

**claims_to_narrow.** None outstanding — the Discussion's existing claims are already tightly scoped.

**recommended_structure.** Replace the third labelled paragraph (*By aggregate counts*, which is largely repetition) with two new paragraphs: (a) alternative explanations (result-free, per S14-008), and (b) practical meaning and cost.

**example_revision_only_after_fact_check.**
> new paragraph (result-free; states no component outcome, per §10.9): "Two alternative readings of this standing deserve statement rather than dismissal. First, the configuration was selected on CEC2017, so part of the primary-suite margin may reflect selection rather than design; the two suites held out from selection place DT-GSK second (CEC2011) and first overall (CEC2013), which bounds but does not eliminate that concern. Second, the tier configuration bundles several mechanisms that activate together at $D\ge50$, and a deterministic direct-search endgame of the kind used here is a long-established technique; the component evidence bearing on how the bundle divides is reported in Supplementary Material S6, and this paper attributes no share of the standing to any individual mechanism."

**score_1_to_5:** **3**

---

## 14.11 Limitations and threats to validity (Conclusions ¶ *Limitations* + Supplement S5.4)

**purpose.** Visible, un-neutralised treatment of the validity threats listed in §14.11.

**Coverage audit against the §14.11 checklist** (✔ = treated; ~ = partial; ✘ = absent):

| Threat | Where | Verdict |
|---|---|---|
| Construct validity (endpoint/metric choice) | S5.5 tie-band sensitivity; §4.1 tie-rule caveat | ✔ |
| Internal validity (self-init asymmetry, dev-suite exposure) | S5.4 seventh + eighth; S5.3 | ✔ in supplement, **~ in main text** |
| Statistical conclusion validity | S5.4 closing paragraph; §4.2.3 | ✔ |
| External validity / benchmark scope | S5.4 third + fifth | ✔ |
| Comparator scope | S5.4 third + seventh | ✔ |
| Sample size / stochastic variation / power | S5.4 closing ("29-function and 22-problem blocks") | ~ (no power statement) |
| Tuning / development leakage | S5.3 + S5.4 eighth | ✔ (unusually good) |
| Implementation & environment differences | S5.4 fourth + sixth | ✔ |
| Missing / failed observations | S5.4 closing (APGSK gap) | ✔ |
| Multiplicity / analytical flexibility | §4.2.3 global-Holm sensitivity; S5.4 closing | ✔ |
| Computational cost | S5.4 fourth (comparability only) | **~ — no overhead figure; see S14-011** |
| Reproducibility limitations | S5.4 sixth (single-thread precondition) | ✔ |
| Literature-corpus limitations | §2.3 survey-scope paragraph | ✔ |
| Ethics / privacy | n/a, declared | ✔ |
| Absence / limits of mechanism evidence | S5.4 eighth (three attribution gaps) | ✔ |

**strengths.**
- **Nothing is neutralised by promotional language.** S5.4's first limitation says "The rank deficit is real." Full stop. The seventh admits the authorship relationship *and* the absence of any external baseline in the same sentence. The eighth admits that the evidence-bearing runs carry no component-level evaluation ledger, so "the standalone null is … 'no detectable benefit under this design' and not a demonstration that the memory was active and neutral". This is a stronger self-criticism than most reviewers would extract.
- The self-init fairness asymmetry is stated with its direction of consequence ("most consequential at low dimension, where DT-GSK runs essentially the scaffold") rather than merely acknowledged.
- The main-text outline explicitly forwards to the full statements rather than replacing them.

**critical_or_major_findings.** None.

**moderate_minor_findings.**
- **S14-009 (Moderate, P2, Confirmed).** The Conclusions say "**Eleven** limitations bound these findings, stated in full … in the Supplementary Material, Section S5" (`conclusions.tex:66`, rendered p. 35). S5.4 enumerates **eight** ordinals (First…Eighth) plus one unnumbered closing paragraph. A reader who follows the pointer to find eleven finds eight. The count is reachable only by splitting conjunctions inside the Conclusions' own outline; it matches no enumeration in either document.
- **S14-009b (Moderate).** The **self-initialization fairness asymmetry** — arguably the most consequential internal-validity threat, since no DT-GSK cell begins from the shared $X_0$ — appears in S5.4's seventh limitation and in §4.1, but is **absent from the Conclusions' limitations outline**. §14.12 requires the conclusion to include the main limitation/boundary; a reader of the main text alone gets the eGSK port, the $D=100$ ceiling and the single host, but not the initialization asymmetry.
- **S14-015 (Minor).** S5.4's preamble (`supplementary.tex:1174–1176`) says "The wording is the wording of the conclusions in the submitted manuscript --- **moved rather than rewritten**, so that nothing is softened in transit." The Conclusions in fact carry a *different*, shorter outline; the two texts do not correspond sentence for sentence. The claim is true of a relocation event (N-020) but false as a description of the shipped pair, and a reviewer who compares them will see the mismatch.
- (Minor) No statistical power statement anywhere. With $n=29$ blocks a Wilcoxon signed-rank across functions has limited power against small consistent effects; the manuscript's several "no significant difference" cells against eGSK would benefit from an explicit acknowledgement that non-significance here is weak evidence of equivalence (which S6.6 makes for the ablation but §4/S5.4 do not make for the panel).

**missing_content.** A one-line power/equivalence caveat attached to the eGSK non-significant cells.

**claims_to_narrow.** "Eleven limitations" → either renumber S5.4 to eleven items or say "the limitations summarised here are stated in full, item by item, in Supplementary Material S5.4".

**recommended_structure.** Number S5.4's items 1–N with headings, and make the Conclusions outline follow the same order and count.

**example_revision_only_after_fact_check.**
> before: "Eleven limitations bound these findings, stated in full with their numeric evidence in the Supplementary Material, Section S5. In outline: …"
> after: "Eight limitations bound these findings; each is stated in full, with its numeric evidence, in Supplementary Material S5.4. In outline: … **DT-GSK self-initializes rather than consuming the shared initial population, a disclosed fairness asymmetry that is not separately bounded and matters most at low dimension.** …"

**score_1_to_5:** **4**

---

## 14.12 Conclusion (§5, PDF pp. 34–36)

**purpose.** Restate only established findings, answer the questions, give exact scope, state the main boundary, introduce nothing new, avoid overstatement, propose realistic future work.

**strengths.**
- Every headline number carries its counterweight in the same sentence or the next: the 2.48 aggregate is immediately followed by the losing head-to-heads, the non-separability, the CEC2011 loss, and the CEC2013 D=30 third place.
- Scope is exact: "within the seven-algorithm GSK-family panel", the descriptive-aggregate label, the four-independent-Holm-families qualifier.
- Future work is tied to identified gaps rather than generic: the activation boundary below $D\ge50$ (tied to the mid-dimension deficit), decomposition-style scaling (tied to the $D=100$ ceiling), non-GSK baselines (tied to the panel-scope limitation).
- The Data-Availability pointer and the determinism claim are both correctly scoped ("in the declared supported environment").

**critical_or_major_findings.**
- **S14-006 (Major, P1, Confirmed) — the Conclusions introduce a result that appears nowhere in the Results or Discussion, and strip its exploratory label.** `conclusions.tex:91–93`: "A breakdown by function class shows this null holds even on the hybrid and composition functions, so the aggregate null is not explained by the separable-problem subset." That is S6.6's by-class conditional-benefit analysis, which S6.6 itself labels "*post hoc* (this analysis was not pre-registered)" and "Exploratory; not part of the pre-registered isolation", and whose own conclusion is hedged ("This is a failure to detect an effect under this design, not a demonstration that none exists"). Section 4 never mentions this analysis. §14.12 explicitly prohibits introducing a new result in the conclusion; §10.7 requires exploratory analyses to be separately labelled.

**moderate_minor_findings.**
- **S14-009 (Moderate)** — "Eleven limitations", see §14.11.
- **S14-012 partial (Moderate)** — the Conclusions devote a full paragraph (`:84–102`) to the ISM null, on top of the abstract sentence and the Introduction paragraph that §10.9's narrowing sanctions. The paragraph is also the fourth main-text restatement of "no detectable standalone benefit" (after the abstract, §3.3 `:270–272`, and §4.7 `:826–829`).
- (Minor) The first paragraph says "with an interaction-structure memory as a supporting mechanism" and the **immediately following sentence** begins "A supporting mechanism is the interaction-structure memory:" — a verbatim-adjacent restatement in consecutive sentences (§10.17.5 near-duplicate content). This is the most visible single writing tell in the manuscript.
- (Minor) The Conclusions repeat 11-2-16 / 13-0-16 / 12-0-17 and 2.88/2.50/2.21/2.34 verbatim from §4, where the file header comment states the intent was "values mirror Section 4 (paraphrased, **not repeated verbatim**)". The stated policy is not met.
- (Minor) "a boundary on the idea that structure can be learned cheaply" is a broader statement than the evidence (one algorithm family, one memory design, $D\le100$, one exploitation scheme). "a boundary on this way of learning structure cheaply in the GSK family" is the defensible form.

**missing_content.**
- The research questions posed in §1 are not answered by name. §14.12 requires the conclusion to answer the research questions; it answers the *empirical standing* question but not the design question ("can a GSK-family algorithm learn … which coordinates improve together, and can it exploit that record…"), which is the one with the null answer.

**claims_to_narrow.**
1. Remove the by-class sentence from the Conclusions, or label it exploratory and first present it in §4.
2. "a boundary on the idea that structure can be learned cheaply" → bound to the family and design.

**recommended_structure.** Four movements are already present (recap → findings → limitations → component evidence + future work). Merge the duplicated "supporting mechanism" sentences and move the by-class claim out.

**example_revision_only_after_fact_check.**
> before: "The isolation finds no detectable standalone benefit at the memory's active tiers, at a tier-dependent compute overhead. A breakdown by function class shows this null holds even on the hybrid and composition functions, so the aggregate null is not explained by the separable-problem subset."
> after: "The isolation finds no detectable standalone benefit at the memory's active tiers, at a tier-dependent compute overhead. An exploratory, post-hoc breakdown by function class — not part of the pre-registered isolation — is reported in the Supplement and does not identify a subset on which the picture changes."

**score_1_to_5:** **3**

---

## 14.13 Declarations and availability (back matter, PDF pp. 36–37)

**purpose.** Authorship, CRediT, funding, conflicts, ethics, consent, data/code availability, acknowledgments, GenAI disclosure — from verified information only.

**strengths.**
- **The conflicts-of-interest statement is exemplary and self-damaging in the right way.** It names A.W.M. as the originator of GSK and co-author of AGSK/APGSK/eGSK/ATMALS-GSK, names H.S.M.R. as an eGSK co-author, names the supervisor–student relationship, and states that these are also evident from the authorship line. Most submissions in this position under-disclose; this one over-discloses.
- The GenAI disclosure implements all three MDPI requirements (declaration, methods-level description of *how*, tool+version in the Acknowledgments) and is mirrored in §4.1 and the cover letter with consistent wording ("Claude Opus 4.8, Anthropic" in all four places — verified by `validate_document_consistency.py`).
- CRediT roles are complete and specific; funding, IRB and consent statements are present and correctly "Not applicable".
- The Data Availability statement is careful: it distinguishes the immutable evidence release, the checksummed analysis bundle, and the separate ablation release, and it names the licences (MIT for code, CC BY 4.0 for derived data, upstream terms for the benchmark definitions) — a level of licence precision most submissions omit.

**critical_or_major_findings.**
- **S14-007 (Major, P1, Confirmed) — a bracketed editorial placeholder is rendered on the title page of the submission PDF and DOCX.** PDF p. 1 affiliation block: "moustafa.masoud@gmail.com (M.E.M.); **[H.S.M.R. institutional e-mail — to be added at submission]** (H.S.M.R.); aliwagdy@gmail.com (A.W.M.)". Source `main.tex:112`. §10.17.4 explicitly names "any bracketed editorial note left in the text" as prohibited in reader-facing surfaces; MDPI requires an e-mail for every author. This is a desk-return risk, not a scientific defect, and it is tracked as AG-0002 — but it is *in the compiled deliverable*, and the package is otherwise being presented as submission-ready.
- **S14-007b (Major, P1).** `main.tex:96–98` defines three all-zero ORCIDs (`0000-0000-0000-0000`). They are **not** rendered (verified: no ORCID icons on the title page), so this is a source-only issue — but the same AG-0002 gate governs both, and MDPI collects ORCIDs at submission. Confirm both before upload.

**moderate_minor_findings.**
- (Moderate) The Data Availability statement says the artifacts "are publicly available in the DT-GSK repository" but gives **no URL and no DOI**, with a source comment noting the durable archive is an author-side item (AG-0006/R-0004). A "publicly available" claim with no locator is not actionable, and MDPI's data-availability policy expects a repository link or an explicit statement of why none exists.
- (Minor) The Data Availability statement runs to ~250 words across four topics (artifacts, evidence release, configuration lock, licences). MDPI style is a short statement; consider moving the configuration-lock sentence into §3.7 where it already appears.
- (Minor) The abbreviations table lists **EMA** and **EWMA** as separate entries; EWMA is used exactly once in the manuscript (in §2.1, describing ATMALS-GSK) and EMA elsewhere. Two acronyms for one concept in one paper is a terminology inconsistency.
- (Minor) `\authorcontributions` omits "resources" and "funding acquisition" — correct given no funding, but CRediT completeness reviewers sometimes query it. No action needed.
- **S14-025 (Minor).** `main.tex:15` and `supplementary.tex:28` disable MDPI submit-mode line numbering (`\let\linenumbers\relax`). The class emits line numbers in *submit* mode precisely so reviewers can cite lines; removing them makes the reviewer's job harder and diverges from the journal's own template output. The stated reason (avoiding the accept-mode logo) does not require suppressing line numbers.

**missing_content.** A repository URL or archival DOI in the Data Availability statement (author-side).

**claims_to_narrow.** "are publicly available in the DT-GSK repository" → either add the locator or say "will be deposited at [archive] upon acceptance; the DOI will be supplied at proof stage".

**recommended_structure.** Keep. Fill AG-0002 and AG-0006 before upload.

**example_revision_only_after_fact_check.** Deferred — the e-mail, ORCIDs, and repository URL are author-side facts I must not invent.

**score_1_to_5:** **3**

---

## 14.14 Supplementary material (61 pp, S1–S6)

**purpose.** Navigable, cross-referenced, standalone where required, not a hiding place for contrary primary results.

**strengths.**
- **The supplement is not used to hide anything adverse — the reverse.** The single unfavourable headline (the CEC2011 Holm-significant loss to eGSK) is in the *main* text; the supplement carries the *favourable* component result that §10.9 requires to stay there. That is the correct polarity and worth saying explicitly.
- Standalone-readable: a shared protocol block at the head restates the suites, budgets, run counts, tests and panel order, and every caption is self-contained.
- S5.2's freeze chronology (M-031) is an unusually good piece of provenance writing: seven numbered steps from the original freeze through the two defects, the source fixes with their locking regression tests, the module rename, the full regeneration, and both release supersessions — with the explicit admission that the original manifest's hashes are historical and do not match the shipped modules.
- S5.3 (configuration selection) volunteers that intermediate candidate configurations existed and are **not** in the immutable release, and labels the disclosure an author-attested development-history note rather than dressing it as evidence.
- S6.7 discloses two implementation defects, their measured consequences, and the fact that the pre-fix and post-fix ISM overhead ratios barely moved — with the reasoning why ("the compiled kernels accelerated the memory-on and memory-off arms alike"), which forestalls the obvious suspicion.
- S6.6 is careful in exactly the places the main text is not: post-hoc labelling, "no formal equivalence test", "a failure to detect an effect under this design".

**critical_or_major_findings.** None internal to the supplement.

**moderate_minor_findings.**
- **S14-016 (Minor).** S5.7's opening (`supplementary.tex:1376–1378`) says tier boundaries are "$D<20$, $20\le D<50$ and $D\ge 50$ (with a further $D\ge 100$ extension), as in **the main-text dimension-gating figure**". It is Table 5, not a figure; and the main text presents four tiers ($D<20$ / 20–49 / 50–99 / $\ge$100), not three-plus-an-extension. Both are dangling/inconsistent references.
- **S14-017 (Minor).** The main text points to "Supplementary Material, Section S6.7" for "the isolated compute cost of the interaction-structure memory" (`performance.tex:753–754` and the Table 16 caption). S6.7 is titled "Implementation Caveats: Two Corrected Defects and Their Evidence Trail". It *does* restate the overhead figures (+57.3 % / +36.3 % / +30.3 %), so the pointer is not dangling — but the primary statement of that result is **S6.5**, and a reader following the pointer lands in a defect-provenance section. S5.4's fourth limitation makes the same S6.7 reference.
- **S14-021 (Minor).** The `\supplementary{}` block in `main.tex:186–200` describes S6 as "a scaffold remove-one decomposition and a direct isolation of the interaction-structure memory" and omits **S6.6** (by-class conditional benefit) and **S6.7** (implementation caveats) — even though S6.6's result is asserted in both the Introduction and the Conclusions. The supplement's own abstract *does* list the by-class breakdown, so the two descriptions of the same object disagree.
- **S14-022 (Minor).** `supplementary.tex:6` header comment still binds the supplement to `rel-2026-07-16-78f075cb0`. Source-only; rendered text is correct (R-06 closed).
- (Minor, §10.17.4 tension) Reader-facing supplement prose contains three hash-suffixed release IDs, four short module SHA-256 prefixes, a full 40-hex anchor commit (twice), and two manifest filenames. §10.17.4 permits "a *single*, deliberately placed archival identifier … in the Data-Availability / reproducibility statement". All of these sit inside the reproducibility appendix, which is the sanctioned location, and the chronology genuinely needs them — but the density is at the edge of the control, and the main text is correctly clean of them.
- (Minor) S6.5's assertion "\dtgsk{}'s family-best standing rests on the complete dimension-tiered system" is an inference about the *primary* result drawn inside the ablation section; it is defensible but it is the supplement editorialising about the main study.

**missing_content.**
- No supplement table of contents. At 61 pages with 26 tables and dozens of figures, a one-page contents list would materially help.
- S5.4's limitations are not individually labelled/numbered, which is what makes S14-009's count mismatch possible.

**claims_to_narrow.** None.

**recommended_structure.** Add a contents page; number S5.4's limitations; retarget the ISM-overhead pointer to S6.5 (with "see also S6.7 for the measurement provenance").

**example_revision_only_after_fact_check.** Not required.

**score_1_to_5:** **4**

---

## 14.15 Cover letter (2 pp)

**purpose.** Same claim ceiling as the manuscript; no unverified novelty, journal flattery, guaranteed impact, or off-matrix claims.

**strengths.**
- The claim ceiling is respected. The headline is explicitly scoped ("best overall **CEC2017** Friedman mean rank on the seven-algorithm GSK-family panel", with the descriptive-aggregate label and eGSK's 2.96 given) — in fact the cover letter scopes the number to CEC2017 **better than the abstract does** (see S14-013).
- The byte-stability claim is narrowed to "for DT-GSK in the declared supported environment" (R-09 closed).
- The reviewer-suggestion placeholder is gone; the author-fill instruction survives only as a LaTeX comment, and it correctly notes that comparator-paper authors should be avoided given the declared relationship.
- No journal flattery beyond a single substantiated fit sentence; no impact prediction; no "guaranteed"; the conflicts and the GenAI use are both disclosed proactively.
- The three contributions match C1–C3 exactly, and the ISM is presented as a supporting mechanism, not a fourth contribution.

**critical_or_major_findings.** None.

**moderate_minor_findings.**
- **S14-012 partial (Moderate).** The ISM null is stated **twice**, in consecutive paragraphs: "its direct isolation is reported transparently as a controlled negative result (no significant standalone benefit at its active tiers)" (¶2) and "the isolation finds no detectable standalone benefit from the memory at its active tiers" (¶3). In a two-page letter this reads as padding, and §10.9 lists the cover letter among the surfaces the prohibition governs (the narrowing sanctions the null's *disclosure*, not its repetition).
- **S14-028 (Minor).** Dated **25 July 2026**, three days after the review date. Intentional (the date is parity-checked against `cover_letter.md` by `validate_document_consistency.py`), but a cover letter dated in the future is an avoidable oddity if the submission slips.
- (Minor) "To our knowledge, DT-GSK attains the best overall CEC2017 Friedman mean rank…" — "to our knowledge" is the wrong hedge for a number the authors computed themselves; it invites the reading that a broader priority claim is being made. Delete it.
- (Minor) The letter does not mention the supplementary material or the data/code availability, both of which editors use for desk triage.

**missing_content.** One sentence naming the supplement and the evidence release/repository.

**claims_to_narrow.** Drop "To our knowledge"; state the null once.

**example_revision_only_after_fact_check.**
> before: "To our knowledge, DT-GSK attains the best overall CEC2017 Friedman mean rank on the seven-algorithm GSK-family panel (2.48, …)"
> after: "Under a release-locked, budget-fair protocol, DT-GSK attains the best overall CEC2017 Friedman mean rank on the seven-algorithm GSK-family panel (2.48, …)"

**score_1_to_5:** **4**

---

## 14.16 Exemplar parity and presentation conventions (§10.15)

**Evidence found.** `papers/governance/presentation_conventions.md` exists and is referenced by `phase_gate_register.csv` row 4, whose validation evidence records "terminology + presentation conventions (**22 dims x 3 exemplars**) FROZEN" — i.e. the registered 22-dimension comparative review against GSK (`mohamed2020gaining`), eGSK (`jawad2024egsk`) and ATMALS-GSK (`alfadli2025atmals`) carries pass evidence at Gate 4, as §10.15 requires. Dimensions up to "Dimension 22" are present in the conventions file. The exemplars are used as calibration references only — no mechanical copying of text, structure or claims was detected: the manuscript's section spine (5 sections + S1–S6), its exhibit inventory and its statistical presentation differ substantially from all three exemplars.

**Parity observations (deviations, with justification status):**

| Dimension | DT-GSK | Exemplar practice | Justified? |
|---|---|---|---|
| Base-algorithm flowchart | Fig. 1 reproduces the base GSK flowchart in the GSK paper's style, with Fig. 2 as the matched DT-GSK pair | GSK paper's Fig. 1 | ✔ deliberate parity, and the base-vs-proposed pair is exactly what §10.17.6 recommends |
| Pseudocode form | `algorithm`+`algpseudocode`, boxed float, 25 numbered steps, 4 labelled phases | GSK/eGSK use framed numbered pseudocode | ✔ |
| Per-function tables in main text | Deferred to S1/S2; main text carries panel summaries only | All three exemplars typeset large per-function tables in the main text | ✔ justified in §4.2.1 and by the page budget; the deferral is stated, not silent |
| CD diagram form | Mean-rank plots **with a CD reference span**, not the clique-connected Demšar diagram | ATMALS-GSK/eGSK use conventional CD diagrams | ~ justified in `performance.tex:238–240` ("non-separable groups are identified in the text"), but a reviewer used to the standard diagram may query it |
| Effect size | Rank-biserial $r$ in the table, $A_{12}$ in the workbook | Exemplars report $A_{12}$ | **✘ unjustified as written** — the deviation is real and defensible, but the prose still describes the exemplar's measure; see S14-001 |
| Runtime comparison table | DT-GSK only | ATMALS-GSK tabulates per-algorithm runtime | ~ justified by the two-session caveat, but see S14-011 |
| Line numbering in submit mode | suppressed | MDPI template default | **✘ unjustified** — see S14-025 |
| Figure typography | Flowcharts in Computer Modern; body in the MDPI text font | Exemplars keep one font | **✘ unjustified** — see S14-020 |

**score_1_to_5:** **4**

---

# 2. Ticket register (§5.4 schema)

Every ticket below carries file:line or command-output evidence. `CONFIRMED` = I verified it against the artifact; `SUSPECTED` = needs author input.

---

```text
ticket_id: S14-001
review_stage: Stage 14.8 / 14.9 (Experimental setup; Results)
reviewer_role: AE (Stage-14 seat s14_sections)
severity: Major
priority: P1
confidence: Confirmed
issue_type: exhibit
manuscript_location: papers/sections/performance.tex:209-231 (statistical protocol); :361-372, :405-411, :422-427 (Sec. 4.2.3); rendered DT-GSK.pdf p. 26 (Table 14)
claim_id_or_artifact_id: TAB-T15 / AN-PW-2017-D10..D100 / M-027
concise_issue: The manuscript repeatedly describes an "A12 column" in Table 14 that does not exist, quotes A12 values that appear in no exhibit, and contradicts itself in one paragraph about which effect size is tabulated.
exact_evidence_or_observation: papers/tables/T15.tex header row is "$p$ & $p_{\mathrm{Holm}}$ & $+$ & $\approx$ & $-$ & $r$ & Dec."; the released wilcoxon_holm_cec2017_D*.csv carries column `rank_biserial` and no `a12`. Table 14's caption correctly says "the matched-pairs rank-biserial effect size $r$". But performance.tex:361-364 says Table 14 reports "$A_{12}$ effect sizes"; :364-368 says "The $A_{12}$ column is computed over the 29 per-function means"; :405-411 quotes "$A_{12}$ of 0.490, 0.505, and 0.472" where the table prints r = -0.286, -0.002, -0.057; :425-426 quotes "$A_{12} = 0.712$" where the table prints r = +0.977. Within one paragraph, :210-213 says "the tabulated effect size is the matched-pairs rank-biserial correlation $r$" and :221-226 says "The tabulated $A_{12}$ is computed over the 29 per-function mean errors". I recomputed the quoted A12s from descriptive_stats_cec2017_D*.csv (unpaired A12 over 29 per-function means): 0.4905, 0.5054, 0.4721, 0.7122 — correct, but printed nowhere in the paper or supplement.
root_cause: The M-027 migration replaced the A12 column with rank-biserial in the generated table and updated the caption, but only partially updated the prose that describes and quotes it.
scientific_or_editorial_justification: Sec. 14.9 requires that all primary evidence appear and that effect be visible; Sec. 10.7 requires the frozen plan's named effect measure to match what is reported; Sec. 10.11 forbids exhibit/prose mismatch. A reader cannot verify a quantity the manuscript attributes to a nonexistent column.
impact_on_validity_or_acceptance: No inference changes (r and A12 agree in sign for every quoted cell), but a statistical reviewer will treat a self-contradictory effect-size paragraph as evidence of uncontrolled revision, and will be unable to check "the largest effect" claim.
required_correction: (a) Replace every prose reference to "the A12 column" / "A12 effect sizes" in Sec. 4.2.3 with $r$; (b) rewrite the Sec. 4.1 effect-size paragraph so exactly one measure is called "tabulated" and the other two (across-function A12, run-level A12) are named as released companions; (c) either reinstate an A12 column in Table 14 or re-express the quoted eGSK/APGSK magnitudes in $r$; (d) if the A12 values are retained, add "released with the analysis bundle" so the reader knows where to find them.
acceptable_alternatives: Add a second effect-size column ($r$ and $A_{12}$ side by side) to Table 14 and keep the prose as is, provided the Sec. 4.1 self-contradiction is still resolved.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Table 14 and its prose describe the same quantity; every quoted effect size is locatable in an exhibit.
post_revision_verification: Re-render Table 14; grep the rendered PDF for "A_{12}"/"A12" and confirm every occurrence resolves to a printed column or an explicitly named released artifact; confirm the Sec. 4.1 paragraph names exactly one tabulated measure.
status: open
```

```text
ticket_id: S14-002
review_stage: Stage 14.8 / 14.9
reviewer_role: AE (s14_sections)
severity: Major
priority: P1
confidence: Confirmed
issue_type: statistics
manuscript_location: papers/sections/performance.tex:317, :338 (CEC2017); :599, :623, :625, :626 (CEC2013); cf. :529-530 (CEC2011) and :250-262 (declared protocol)
claim_id_or_artifact_id: AN-OMNI-2017-D10..D100 / AN-OMNI-2013-D10..D50 / AN-OMNI-2011-NATIVE / M-026
concise_issue: The printed Friedman/Iman-Davenport omnibus p-values for CEC2017 and CEC2013 are the tie-UNcorrected values, while the manuscript declares the tie-corrected statistic is used and invites the reader to check the released CSVs (whose primary p_value column is the corrected one). CEC2011 quotes the corrected value, so the manuscript is also inconsistent across suites.
exact_evidence_or_observation: From papers/analysis/rel-2026-07-20-67d9345f9/*/friedman_ranks_*.csv — CEC2017 D10 p_value=1.1597e-09 vs p_value_uncorrected=2.5769e-08 (manuscript prints "p <= 2.6e-8" at :317 and :338); CEC2013 D10 5.3218e-08 vs 3.2640e-07 (manuscript prints 3.3e-7); D30 1.0897e-03 vs 2.2423e-03 (manuscript prints 2.2e-3, and the caption bound "p <= 2.3e-3"); D50 2.9085e-06 vs 9.2124e-06 (manuscript prints 9.2e-6). CEC2011: manuscript prints F=4.27, p=6.0e-4, which IS the corrected pair (4.266899 / 6.0079e-04); the uncorrected pair is 3.6688 / 2.16e-03. Declared protocol at :250-253: "the Friedman statistic uses the tie-corrected rank variance that underlies the Iman--Davenport $F$"; at :261-262: "Both are released per panel in friedman_ranks_*.csv so the correction can be checked directly."
root_cause: The M-026 tie-correction retrofit regenerated the CSVs and the Sec. 4.1 diagnostics paragraph (whose C values 0.890 / 0.979 / 1.0 / 1.0 and tie counts 9 / 3 / 0 / 0 I verified as correct) but the omnibus p-values quoted in Sec. 4.2.2 / 4.4 and in two captions were not re-pulled from the new primary column.
scientific_or_editorial_justification: Sec. 10.7 requires a machine-readable row for every reported statistic and that reported values match the frozen analysis outputs; Sec. 10.11 forbids prose/exhibit-to-source drift. The manuscript explicitly tells the reader to check the CSVs, so the mismatch is discoverable by any diligent reviewer.
impact_on_validity_or_acceptance: No decision changes — C <= 1 so correction can only lower p, and the manuscript's own claim at :258-261 that every omnibus decision is identical under both forms is correct. The damage is credibility: the paper prints numbers that disagree with the column it points at, and treats CEC2011 differently from CEC2017/CEC2013.
required_correction: Re-quote every omnibus p from the `p_value` (corrected) column in Sec. 4.2.2, Sec. 4.4, and both table captions; OR state explicitly at each site that the uncorrected value is quoted as the conservative bound and give the corrected one alongside. Whichever is chosen must be applied to all three suites uniformly.
acceptable_alternatives: Report both, e.g. "p = 5.3e-8 (uncorrected 3.3e-7)".
additional_evidence_needed: None.
dependencies: None. (No rerun required; the corrected values are already in the released CSVs.)
expected_improvement: Every printed omnibus p reproduces from the named column; the three suites are treated identically.
post_revision_verification: Re-run validate_evidence_bindings.py and additionally diff every printed omnibus p against the `p_value` column of the corresponding friedman_ranks_*.csv.
status: open
```

```text
ticket_id: S14-003
review_stage: Stage 14.7 (Proposed method)
reviewer_role: AE (s14_sections)
severity: Major
priority: P1
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/build_prompt_phases/phase_03/parameter_table.tex:14-15 (Table 10 caption); rendered DT-GSK.pdf p. 20
claim_id_or_artifact_id: ART-PARAMS / T-PARAMS
concise_issue: The main-text parameter table claims the shipped configuration is "Hash-frozen in algorithm_freeze_manifest.json", but the supplement states that manifest is historical and its hashes do not match the shipped modules.
exact_evidence_or_observation: Table 10 caption: "No tuning is required or permitted at run time. Hash-frozen in \texttt{algorithm\_freeze\_manifest.json}." Supplement S5.2 (supplementary.tex:1123-1134): "The four SHA-256 prefixes recorded in the original freeze manifest are therefore \textbf{historical}: they pin the pre-fix sources under their pre-rename filenames and do \emph{not} match the shipped modules. A current manifest, \texttt{algorithm\_freeze\_manifest\_2026-07-19.json}, was minted from the post-fix source...". Both files exist under papers/build_prompt_phases/phase_03/. validate_provenance_claims.py passes because its authority-context rule covers release IDs, not manifest filenames.
root_cause: The M-031 provenance rewrite corrected the supplement but the main-text caption, generated from the frozen phase_03 artifact, still names the pre-fix manifest.
scientific_or_editorial_justification: Sec. 10.3 requires source release IDs and checksums to be recorded accurately; Sec. 10.17.4 additionally flags raw internal filenames in reader-facing captions. A reader directed to a superseded manifest will find hashes that do not match the shipped code and will conclude the freeze claim is false.
impact_on_validity_or_acceptance: Directly undermines the C3 reproducibility contribution, which is one of the paper's three claimed contributions. A reviewer who checks this will lose confidence in the whole provenance chain.
required_correction: Change the caption to name the current manifest, or (preferred, per Sec. 10.17.4) drop the filename and point to Supplementary Material S5.2 for the manifest chronology.
acceptable_alternatives: Keep the filename but add "(superseded; see S5.2 for the current manifest)".
additional_evidence_needed: None.
dependencies: Coordinate with the seat auditing Gate A/Sec. 10.3, since the same fix should extend validate_provenance_claims.py to cover manifest filenames.
expected_improvement: No reader-facing pointer to a superseded authority; the validator's coverage gap closed.
post_revision_verification: Re-render Table 10; extend validate_provenance_claims.py to flag any reader-facing occurrence of a superseded manifest filename and confirm it goes RED on the pre-fix bytes and GREEN after.
status: open
```

```text
ticket_id: S14-004
review_stage: Stage 14.5 / 14.9 / 14.10
reviewer_role: AE (s14_sections)
severity: Major
priority: P1
confidence: Confirmed
issue_type: experimental-design
manuscript_location: papers/sections/related_work.tex:89-93 and Table 1 (published standing); papers/sections/performance.tex Table 13 / tables/T16.tex (measured standing); no reconciliation anywhere
claim_id_or_artifact_id: EC:alfadli2025atmals / AN-OMNI-2017-D10..D100 / TAB-T16
concise_issue: The study's re-run inverts ATMALS-GSK's published in-family CEC2017 standing (first overall in its own paper; fifth of seven here, behind eGSK at every dimension) and the manuscript never mentions, let alone explains, the discrepancy.
exact_evidence_or_observation: Evidence card papers/governance/evidence_cards/alfadli2025atmals.md:40 — "Friedman family ranking (Table 18, p. 56): overall — ATMALS-GSK 2.24 (1st), eGSK 2.84 (2nd) ... ATMALS-GSK ranks first at D = 30 (1.84), 50 (1.93), 100 (1.82)". related_work.tex:89-91 faithfully reports this. This study (tables/T16.tex, friedman_ranks_cec2017_*.csv): ATMALS-GSK 5.29 / 4.19 / 4.31 / 3.66, overall 4.36 (5th of 7); eGSK 4.24 / 2.29 / 2.62 / 2.69, overall 2.96 (2nd). eGSK is ahead of ATMALS-GSK at every dimension. Greps of performance.tex, conclusions.tex, supplementary.tex, comparability_audit.md and phase_06/negative_findings.md return no mention of the reversal.
root_cause: Panel-standing reconciliation against the comparators' own published results was never part of the reporting plan; negative_findings.md tracks adverse findings about DT-GSK, not about comparator reproduction.
scientific_or_editorial_justification: Sec. 14.10 requires fair comparison with the literature; Sec. 10.13 lists unfair comparator provenance among the hard rejection risks. The paper both reports a competitor's published claim and produces the opposite result under "published reference constants" without comment.
impact_on_validity_or_acceptance: High. Five of six comparators were authored or co-authored by two of the present authors (disclosed). An unexplained three-rank demotion of the strongest published competitor is the single most likely trigger for a reviewer accusation of comparator under-tuning, and the manuscript currently offers no defence.
required_correction: Add a short reconciliation paragraph at the end of Sec. 4.2.2 that (i) states which comparators reproduce their published in-family standing (eGSK's D=10 weakness does: 4.24, fifth of seven and its worst dimension here) and which do not (ATMALS-GSK), (ii) lists the protocol differences that could account for it (panel composition including DT-GSK and APGSK, shared-X0 initialization, uniform budget accounting with no local-search exemption, the CEC2017 budget and run count actually used), and (iii) states explicitly that no comparator was re-tuned and that these cells are read as performance under this protocol, not as a re-assessment of the published result. Cite comparability_audit.md for the per-optimizer producer commits.
acceptable_alternatives: If the authors can point to a protocol difference that plainly explains it (e.g. a differing local-search budget convention documented in benchmark_protocol_audit_part2.md), state that specific cause instead of the general list.
additional_evidence_needed: Author confirmation of the ATMALS-GSK port's parameter set against alfadli2025atmals, and of whether its local search is charged to MaxFES in both settings.
dependencies: Coordinate with the Sec. 10.4 / 10.13 seat (comparator protocol scope).
expected_improvement: The most damaging unexplained fact in the results becomes a disclosed, bounded protocol difference.
post_revision_verification: Confirm the new paragraph is present in the rendered PDF and that its statements about eGSK's and ATMALS-GSK's published standings match their evidence cards verbatim.
status: open
```

```text
ticket_id: S14-005
review_stage: Stage 14.4 (Introduction)
reviewer_role: AE (s14_sections)
severity: Major
priority: P1
confidence: Confirmed
issue_type: claim-scope
manuscript_location: papers/sections/introduction.tex:72-74; rendered DT-GSK.pdf p. 3
claim_id_or_artifact_id: X-ABL-02 (S6.5 isolation null)
concise_issue: The Introduction asserts the ISM hypothesis is "answered in the negative", converting an underpowered non-detection into a proven negative that the supplying supplement explicitly disclaims.
exact_evidence_or_observation: introduction.tex:72-74 — "Whether such a signal, once recovered, improves the optimizer is a hypothesis this paper tests --- and, for GSK at these dimensions, answers in the negative." Supplement S6.6 (supplementary.tex:2117-2118): "This is a failure to detect an effect under this design, not a demonstration that none exists."; :2114-2115: "absent a formal equivalence test, this evidence is consistent with zero rather than establishing it." The same Introduction gets it right at :135 ("the present component isolation does not establish a consistent standalone performance contribution").
root_cause: Rhetorical compression in the funnel paragraph, written before the honest framing paragraph was added at :135.
scientific_or_editorial_justification: PAPER_REVIEW_PROMPT Sec. 10.9 (narrowed) states the advertised null is reportable "if a main-text sentence overstates it"; overstating a null as proven is the symmetric defect to overstating a favorable effect. Sec. 16 preferred language: "The current design does not identify the component's independent causal effect."
impact_on_validity_or_acceptance: A reviewer who reads the Introduction's flat negative and then the supplement's equivalence-test caveat will conclude the main text is not calibrated to its own evidence — which is corrosive precisely because the rest of the manuscript is unusually well calibrated.
required_correction: Replace "answers in the negative" with a non-detection formulation naming the design bound.
acceptable_alternatives: "and, under the design used here, does not detect an improvement at the dimensions where the memory is active."
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Introduction, abstract, discussion and supplement all state the same strength of claim.
post_revision_verification: Grep the rendered PDF for "in the negative" and for any other unhedged negative assertion about ISM; confirm each surviving statement uses "no detectable" / "does not establish" phrasing.
status: open
```

```text
ticket_id: S14-006
review_stage: Stage 14.4 / 14.12
reviewer_role: AE (s14_sections)
severity: Major
priority: P1
confidence: Confirmed
issue_type: statistics
manuscript_location: papers/sections/introduction.tex:135; papers/sections/conclusions.tex:91-93; rendered DT-GSK.pdf pp. 4 and 35
claim_id_or_artifact_id: Path-1 subset re-analysis (S6.6)
concise_issue: A post-hoc, explicitly non-pre-registered by-class analysis is stated in the Introduction and the Conclusions without its exploratory label, and appears in the Conclusions as a result that never appears in the Results section.
exact_evidence_or_observation: conclusions.tex:91-93 — "A breakdown by function class shows this null holds even on the hybrid and composition functions, so the aggregate null is not explained by the separable-problem subset." introduction.tex:135 — "the function-class analysis reveals no systematic advantage on the hybrid or composition categories (Supplementary Materials, Sections S6.5 and S6.6)". Supplement S6.6 (supplementary.tex:2068-2069): "we ask \emph{post hoc} (this analysis was not pre-registered)"; Table A caption :2085-2086: "Exploratory; not part of the pre-registered isolation." Grep confirms Sec. 4 (performance.tex) never mentions the by-class ISM breakdown.
root_cause: The by-class analysis was added late (Path-1 re-analysis) and was wired into the framing sections without the labelling discipline the supplement applies to it.
scientific_or_editorial_justification: Sec. 14.12 forbids introducing a new result in the conclusion. Sec. 10.7 (multiplicity-family hygiene) requires exploratory analyses to be separately labelled wherever reported — a rule the manuscript already obeys for its Benjamini-Hochberg companion at performance.tex:503-507.
impact_on_validity_or_acceptance: An unlabelled post-hoc subgroup analysis used to strengthen a headline framing is a standard reviewer trigger, and it is used here to reinforce the "controlled negative result" claim.
required_correction: (a) In both the Introduction and the Conclusions, label the by-class analysis exploratory/post-hoc and not pre-registered; (b) either remove it from the Conclusions entirely or first present it in Sec. 4 so the Conclusions restates rather than introduces it.
acceptable_alternatives: Remove the by-class sentence from both framing sections and leave it in S6.6, where it is correctly labelled.
additional_evidence_needed: None.
dependencies: Interacts with S14-012 (over-advertising of the null).
expected_improvement: No unlabelled exploratory result in the framing sections; the Conclusions introduce nothing new.
post_revision_verification: Grep the rendered PDF for "function class" / "by class" outside Sec. 4 and confirm every occurrence carries an exploratory label or has been removed.
status: open
```

```text
ticket_id: S14-007
review_stage: Stage 14.13 (Declarations)
reviewer_role: AE (s14_sections)
severity: Major
priority: P1
confidence: Confirmed
issue_type: production
manuscript_location: papers/main.tex:112 (affiliation block) and :96-98 (ORCIDs); rendered DT-GSK.pdf p. 1 and DT-GSK.docx
claim_id_or_artifact_id: AG-0002
concise_issue: A bracketed editorial placeholder for an author e-mail is rendered on the title page of the compiled submission PDF and DOCX; three all-zero ORCIDs remain in the source.
exact_evidence_or_observation: Rendered DT-GSK.pdf p. 1: "moustafa.masoud@gmail.com (M.E.M.); [H.S.M.R. institutional e-mail --- to be added at submission] (H.S.M.R.); aliwagdy@gmail.com (A.W.M.)". Source main.tex:112. main.tex:96-98 defines \orcidauthorA/B/C = 0000-0000-0000-0000 (verified not rendered on the title page, so source-only).
root_cause: AG-0002 is an author-side gap deliberately left open, but the placeholder was left inside the rendered deliverable rather than kept as a comment.
scientific_or_editorial_justification: Sec. 10.17.4 explicitly prohibits "any bracketed editorial note left in the text" and all-zero ORCIDs anywhere a reader sees them. MDPI requires an e-mail address for every author at submission.
impact_on_validity_or_acceptance: Desk-return risk. It is the first thing an editorial assistant sees and it signals an unfinished submission.
required_correction: Supply H.S.M.R.'s institutional e-mail and the three real ORCIDs before upload; do not fabricate either. If the e-mail cannot be obtained, MDPI permits omitting the address for non-corresponding authors — remove the bracketed note rather than shipping it.
acceptable_alternatives: Omit the e-mail entirely for the non-corresponding author (still no bracketed note).
additional_evidence_needed: Author-side (e-mail, ORCIDs).
dependencies: AG-0002, AG-0006 (repository URL/DOI) should be closed in the same pass.
expected_improvement: A title page with no placeholders.
post_revision_verification: Grep the rendered PDF and both DOCX for "[", "to be added", "0000-0000"; confirm zero reader-facing hits.
status: open
```

```text
ticket_id: S14-008
review_stage: Stage 14.10 (Discussion)
reviewer_role: AE (s14_sections)
severity: Major
priority: P2
confidence: Confirmed
issue_type: claim-scope
manuscript_location: papers/sections/performance.tex:787-875 (Sec. 4.7, entire)
claim_id_or_artifact_id: IN-01 / IN-02 / LM-01
concise_issue: The Discussion never names the leading alternative explanation for the reported standing, so its extensive list of things it does not claim reads as avoidance rather than caution.
exact_evidence_or_observation: Sec. 4.7 states four times what is not attributed ("stated here as plausibility, not as a measured component contribution"; "per-component causal attribution is deliberately not claimed"; "this reading associates the high-dimension behavior with the bundled tier configuration rather than with any isolated component"; "none of these findings is offered as evidence of field-wide superiority") but never states what the competing account of the standing is. The two candidates are visible in the project's own artifacts: S5.3 (supplementary.tex:1154-1169) records that the configuration was selected on CEC2017; S6.5 (supplementary.tex:2048-2056) records that within the added mechanisms only one contrast is isolated and significant at these tiers and that the effect attaches to the endgame phase as a whole rather than to the learned basis.
root_cause: Sec. 10.9 forbids importing the favorable component result into the main text, and the drafting resolved this by saying nothing at all rather than by writing a result-free statement of the alternative.
scientific_or_editorial_justification: Sec. 14.10 requires alternative explanations to be considered. Sec. 10.9's own remedy is a "result-free deferral" — neutral co-activation plus a pointer without direction — which permits naming a rival explanation as long as no outcome is stated.
impact_on_validity_or_acceptance: This is the manuscript's central Q1 vulnerability (Sec. 10.13: "contribution framed as a bundle of modules without a clear scientific thesis"; "mechanism explanations based only on final performance"). Leaving the rival account unstated does not remove it from the reviewer's mind; it removes the authors' chance to bound it.
required_correction: Add one result-free paragraph to Sec. 4.7 naming (i) development-suite selection exposure and (ii) the bundled co-activation at D>=50 including a deterministic direct-search endgame of a long-established type, and pointing to Supplementary Material S6 for the component evidence — stating no direction, no p-value, no rank, no effect for any component.
acceptable_alternatives: Place the paragraph in Sec. 5 immediately before the future-work sentences.
additional_evidence_needed: None.
dependencies: Must be drafted so it does not violate Sec. 10.9 (no favorable component outcome may be stated or implied).
expected_improvement: The Discussion pre-empts rather than invites the strongest reviewer objection.
post_revision_verification: Apply the Sec. 10.9 leak test to the new paragraph sentence by sentence ("does removing all knowledge of the ablation change whether this sentence is true or supported?"); the answer must be no for every sentence. Re-run the no_ablation_scan check in validate_cross_format_parity.py.
status: open
```

```text
ticket_id: S14-009
review_stage: Stage 14.11 / 14.12
reviewer_role: AE (s14_sections)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: writing
manuscript_location: papers/sections/conclusions.tex:66-81; papers/supplementary.tex:1179-1263 (S5.4)
claim_id_or_artifact_id: LM-01..LM-05 / N-020
concise_issue: The Conclusions claim "Eleven limitations" but the supplement enumerates eight; and the self-initialization fairness asymmetry, present in S5.4, is missing from the Conclusions outline.
exact_evidence_or_observation: conclusions.tex:66 — "Eleven limitations bound these findings, stated in full with their numeric evidence in the Supplementary Material, Section S5." S5.4 enumerates First, Second, Third, Fourth, Fifth, Sixth, Seventh, Eighth (eight ordinals) plus one unnumbered closing paragraph. S5.4's seventh limitation (supplementary.tex:1231-1236) states "DT-GSK's self-initialization ... means that no DT-GSK cell begins from the shared initial population ... a disclosed fairness asymmetry that is not separately bounded and is most consequential at low dimension"; no counterpart appears in the Conclusions outline.
root_cause: The N-020 relocation moved the limitations to S5.4 and left a hand-written outline in the Conclusions whose item count was never reconciled with the destination.
scientific_or_editorial_justification: Sec. 14.12 requires the conclusion to include the main limitation or boundary; Sec. 14.11 requires internal-validity threats to be visible. A count that matches no enumeration is an auditable inconsistency.
impact_on_validity_or_acceptance: Low scientific impact, moderate credibility impact — a reviewer who counts will find the mismatch immediately, and the omitted item is the study's principal fairness asymmetry.
required_correction: Number S5.4's limitations explicitly; make the Conclusions outline state the same count and the same order; add the self-initialization asymmetry to the outline.
acceptable_alternatives: Drop the numeral: "The limitations summarised here are stated in full, item by item, in Supplementary Material S5.4."
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Main-text and supplement limitation inventories agree in count, order and content.
post_revision_verification: Count the ordinals in S5.4 in the rendered supplement and compare with the numeral in the rendered Conclusions; confirm the self-init item appears in both.
status: open
```

```text
ticket_id: S14-010
review_stage: Stage 14.6 (Background/notation)
reviewer_role: AE (s14_sections)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: writing
manuscript_location: papers/sections/proposed_algorithm.tex:69-74; rendered DT-GSK.pdf (Sec. 3.1, extract line 385)
claim_id_or_artifact_id: R-01 / E3 / ART-NOTATION
concise_issue: R-01 split the gaining-sharing sign into per-phase s_J and s_S in the equation and the notation table, but the prose still uses a single undefined symbol s.
exact_evidence_or_observation: Rendered PDF: "where KF scales the step and s in {+1, -1} is the sign of the fitness comparison between the individual and the knowledge source its phase compares against". Equation (4) (phase_03/equations.tex, E3) defines s_J and s_S and no bare s. notation_table.tex:54 lists "$s_J,s_S$ & junior/senior comparison sign (Eq. 4)". No notation row defines s.
root_cause: R-01 updated the equation registry and notation table but not the Sec. 3.1 prose that reads on them.
scientific_or_editorial_justification: Sec. 10.17.6 requires symbols to be consistent across the notation table, equations, prose, pseudocode and companion exhibits. A symbol used in prose and defined nowhere is a reimplementation hazard, which is the exact failure mode R-01 was raised to fix.
impact_on_validity_or_acceptance: Low scientific impact; but it leaves R-01 half-closed and is trivially visible to any reader who checks the notation table.
required_correction: Rewrite the sentence to use s_J and s_S and to state which donor each compares (junior: x_{R3}; senior: x_{R2}).
acceptable_alternatives: None — the equation cannot revert to a single s, since the two phases compare different donors.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: One sign convention, three consistent surfaces (equation, notation table, prose).
post_revision_verification: Grep the rendered PDF and DOCX for a standalone "s ∈ {+1" and confirm zero hits; confirm s_J and s_S each appear in prose, equation and notation table.
status: open
```

```text
ticket_id: S14-011
review_stage: Stage 14.9 / 14.10 / 14.11
reviewer_role: AE (s14_sections)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: evidence
manuscript_location: papers/sections/performance.tex:735-784 (Sec. 4.6); Sec. 4.7 (no cost paragraph); supplementary.tex:1202-1212 (S5.4 fourth limitation)
claim_id_or_artifact_id: AN-COST-2017 / LM-04 / RT-001
concise_issue: The manuscript gives no comparative non-objective overhead figure of any kind, so the reader cannot judge the scaffold's cost relative to the base algorithm it extends.
exact_evidence_or_observation: Sec. 4.6 tabulates DT-GSK only (4.93 / 13.04 / 23.30 / 41.59 s) and states "we do not tabulate a cross-algorithm wall-clock comparison and make no runtime-superiority claim". Sec. 4.7 contains no cost sentence. The released cost_cec2017.csv carries all seven algorithms with comparability="NOT-COMPARABLE-ACROSS-ALGORITHMS (RT-001: panel not measured as one session ...)": at D=10 gsk 0.55 vs dt-gsk 4.93 (~9x); at D=100 gsk 40.98 vs dt-gsk 41.59 (~1.0x), with atmals-gsk 82.68 and egsk 71.29 both above DT-GSK. PAPER_REVIEW_PROMPT Sec. 10.7 (line 3299) describes an RT-001 remedy of re-timing all six comparators via scripts/retime_comparators.py; that was not executed — the table was narrowed to DT-GSK instead.
root_cause: RT-001 was resolved by removing the comparator columns rather than by the re-timing the governing prompt anticipated, and no replacement statement of relative cost was added.
scientific_or_editorial_justification: Sec. 14.10 requires cost and trade-offs to be explicit; Sec. 10.13 lists "missing non-objective overhead analysis" among the hard rejection risks. The paper's own thesis is that its overhead is "bookkeeping, not extra objective evaluations", which is a comparative claim with no comparative evidence attached.
impact_on_validity_or_acceptance: A reviewer will ask "how much does this cost relative to GSK?" and find no answer anywhere. Note the honest picture is mixed, not unfavourable — DT-GSK is the slowest at D=10 and among the fastest at D=100 — so the omission costs the authors as much as it protects them.
required_correction: Add two or three sentences (Sec. 4.6 and/or Sec. 4.7) giving the order-of-magnitude relative cost with the session caveat attached, e.g. that DT-GSK's per-run time is several times the base algorithm's at D=10 and comparable at D=100, explicitly labelled as indicative because the sessions differ; OR add an FES-normalised or generation-normalised overhead measure that is session-independent.
acceptable_alternatives: Re-time the panel in one session (the original RT-001 remedy) — but this is a new measurement campaign and the standing constraint is NO rerun, so the disclosure route is preferred.
additional_evidence_needed: None if the indicative-disclosure route is taken.
dependencies: Must not be phrased so as to constitute a cross-algorithm runtime comparison the data cannot support; keep the "no runtime-superiority claim" sentence.
expected_improvement: The reader gets a bounded answer to the cost question instead of none.
post_revision_verification: Confirm the new text states the session caveat in the same sentence as any ratio, and that the "no runtime-superiority claim" sentence survives verbatim.
status: open
```

```text
ticket_id: S14-012
review_stage: Stage 14.2 / 14.4 / 14.7 / 14.10 / 14.12 / 14.15
reviewer_role: AE (s14_sections)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: writing
manuscript_location: main.tex:146-151 (abstract) and :197-199 (supplementary block); introduction.tex:72-74 and :135; proposed_algorithm.tex:270-272; performance.tex:826-829; conclusions.tex:84-102; cover_letter.tex:55 and :57
claim_id_or_artifact_id: X-ABL-02
concise_issue: The ISM isolation null is restated in at least seven reader-facing places in the manuscript plus twice in the cover letter, against a governing narrowing that sanctions "one abstract sentence plus the introduction's supporting-component paragraph".
exact_evidence_or_observation: (1) abstract main.tex:146-147 "A direct isolation finds no detectable standalone benefit ... a controlled negative result"; (2) supplementary-materials block main.tex:197-199 "(which finds no significant standalone benefit at its active tiers)"; (3) introduction.tex:74 "answers in the negative"; (4) introduction.tex:135 "does not establish a consistent standalone performance contribution"; (5) proposed_algorithm.tex:270-272 "finds no significant standalone benefit at the memory's active tiers"; (6) performance.tex:826-829 "finds no significant standalone benefit at its active tiers"; (7) conclusions.tex:89-102 (a full paragraph); (8)+(9) cover_letter.tex:55 and :57, in consecutive paragraphs. PAPER_REVIEW_PROMPT Sec. 10.9 narrowing (lines 3327-3331): "now briefly: one abstract sentence plus the introduction's supporting-component paragraph".
root_cause: Successive honesty passes each added a disclosure without removing the prior one.
scientific_or_editorial_justification: Sec. 10.17.5 requires removal of near-duplicate content and sentences that paraphrase an adjacent sentence. Per the seat instruction, the advertised null is NOT re-raised here as a Sec. 10.9 leak; this is a redundancy and scope ticket only.
impact_on_validity_or_acceptance: Repetition of a negative finding nine times reads as either anxiety or padding, and it crowds out the positive contributions in the reader's summary of the paper.
required_correction: Reduce to the sanctioned scope: keep the abstract sentence, one Introduction statement (merged), one Sec. 3.4 pointer, and one Conclusions statement; delete the duplicates in the supplementary-materials block, Sec. 4.7, and the cover letter's second occurrence.
acceptable_alternatives: Keep the Sec. 4.7 instance and drop the Sec. 3.4 one, if the authors prefer the disclosure at the point of interpretation.
additional_evidence_needed: None.
dependencies: Interacts with S14-005 (which fixes occurrence 3) and S14-006.
expected_improvement: The null is stated where it does work and nowhere else.
post_revision_verification: Grep the rendered PDF, DOCX and cover letter for "standalone benefit" and confirm the surviving count matches the agreed scope.
status: open
```

```text
ticket_id: S14-013
review_stage: Stage 14.2 (Abstract)
reviewer_role: AE (s14_sections)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: claim-scope
manuscript_location: papers/main.tex:138-145; rendered DT-GSK.pdf p. 1
claim_id_or_artifact_id: AN-RANKAGG-2017-OVERALL / RS-01 NARROWED
concise_issue: The abstract's headline number is not scoped to CEC2017 in the sentence that carries it, and the "Holm-significant loss" parenthetical ambiguously attaches to the D=30 result as well as to CEC2011.
exact_evidence_or_observation: main.tex:138-142 — "Against six GSK-family baselines on CEC2017 (primary), CEC2011, and CEC2013 under a budget-fair paired protocol, DT-GSK attains the best overall Friedman mean rank in the seven-algorithm GSK-family panel (2.48, a descriptive across-dimension mean), first at three of four dimensions." 2.48 is CEC2017-only (friedman_ranks_cec2017_overall.csv); on CEC2011 DT-GSK is second (3.36 vs 2.52). main.tex:143-144 — "It is second behind eGSK at $D = 30$ and on CEC2011 (a Holm-significant loss)": the D=30 outcome is NOT Holm-significant (p_Holm = 0.199, Table 14); only the CEC2011 loss is (4.2e-2).
root_cause: Compression to fit the 200-word MDPI abstract limit (currently 197 words).
scientific_or_editorial_justification: Sec. 14.2 requires that the abstract contain no stronger claim than the body and that results be correctly bound. The first defect over-states favourably, the second over-states unfavourably; both are inaccuracies.
impact_on_validity_or_acceptance: The abstract is what most readers and all indexers see. A three-suite framing around a one-suite number is the kind of imprecision a Q1 reviewer flags in the first paragraph of their report.
required_correction: Insert "CEC2017" into the headline clause; separate the D=30 and CEC2011 statements so the significance qualifier attaches only to CEC2011.
acceptable_alternatives: Move the suite list to a separate sentence so the rank claim stands alone.
additional_evidence_needed: None.
dependencies: The revision must stay <= 200 words; a compensating trim is identified in Sec. 14.2 above.
expected_improvement: Every abstract number is bound to its suite and its significance status.
post_revision_verification: Re-count abstract words; confirm each abstract sentence still maps to a claim-audit row and that none is stronger than the body.
status: open
```

```text
ticket_id: S14-014
review_stage: Stage 14.2 / 14.9
reviewer_role: AE (s14_sections)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: evidence
manuscript_location: papers/main.tex:144-145 (abstract); papers/sections/performance.tex Sec. 4.4 (no CD reported)
claim_id_or_artifact_id: AN-OMNI-2013-D10..D50
concise_issue: The abstract's unqualified "never Nemenyi-separable" spans all three suites, but the manuscript prints a Nemenyi critical difference only for CEC2017 and mentions CEC2011's in passing; no CEC2013 CD appears anywhere.
exact_evidence_or_observation: Abstract: "and the two are never Nemenyi-separable." Main text prints CD = 1.67 for CEC2017 (Sec. 4.2.3, Fig. 4) and CD = 1.92 for CEC2011 inside a parenthesis at performance.tex:538-539. Sec. 4.4 (CEC2013) reports no CD. The claim nonetheless HOLDS: nemenyi_cd_cec2013_D{10,30,50}.csv exist in the release, and for k=7, N=28 the CD is 1.703 while the largest DT-GSK--eGSK gap is 1.464 (D=10).
root_cause: The CEC2013 section was written as a compact "second comparison suite" report and omitted the post-hoc geometry.
scientific_or_editorial_justification: Sec. 14.2 requires abstract claims to be verifiable from the body.
impact_on_validity_or_acceptance: Minimal, but a reviewer checking the abstract's universal will not find the CEC2013 leg.
required_correction: Either scope the abstract claim ("on CEC2017") or add the CEC2013 CD (and the largest DT-GSK--eGSK gap) as one clause in Sec. 4.4.
acceptable_alternatives: Either is sufficient.
additional_evidence_needed: None — the CSV is already in the release.
dependencies: None.
expected_improvement: The abstract's universal is checkable from the body.
post_revision_verification: Confirm the rendered Sec. 4.4 contains the CEC2013 CD, or that the abstract carries the suite qualifier.
status: open
```

```text
ticket_id: S14-015
review_stage: Stage 14.11 / 14.14
reviewer_role: AE (s14_sections)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: writing
manuscript_location: papers/supplementary.tex:1173-1177
claim_id_or_artifact_id: N-020
concise_issue: S5.4's preamble claims its text is the conclusions' wording "moved rather than rewritten", but the Conclusions carry a different, shortened outline.
exact_evidence_or_observation: supplementary.tex:1174-1176 — "The wording is the wording of the conclusions in the submitted manuscript --- moved rather than rewritten, so that nothing is softened in transit." The shipped Conclusions (conclusions.tex:65-81) is an "In outline:" summary that shares almost no sentences with S5.4.
root_cause: The sentence describes the N-020 relocation event and was not updated when the Conclusions were re-summarised.
scientific_or_editorial_justification: Sec. 14.14 requires the supplement's self-description to be accurate.
impact_on_validity_or_acceptance: Negligible scientifically; an easy inconsistency for a reviewer to spot and cite.
required_correction: Rewrite as a statement of intent rather than of identity, e.g. "These statements were relocated here from the conclusions during preparation and are reproduced without softening; the conclusions retain a summary outline."
acceptable_alternatives: Delete the sentence.
additional_evidence_needed: None.
dependencies: S14-009 (same paragraph pair).
expected_improvement: The supplement's self-description matches the shipped pair.
post_revision_verification: Read the two paragraphs side by side and confirm the description is now true.
status: open
```

```text
ticket_id: S14-016
review_stage: Stage 14.14 (Supplementary)
reviewer_role: AE (s14_sections)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: exhibit
manuscript_location: papers/supplementary.tex:1376-1378 (S5.7 opening)
claim_id_or_artifact_id: ART-PARAMS
concise_issue: S5.7 refers to a "main-text dimension-gating figure" that is a table, and describes three tiers plus an extension where the main text defines four tiers.
exact_evidence_or_observation: supplementary.tex:1376-1378 — "the tier boundaries are $D<20$, $20\le D<50$ and $D\ge 50$ (with a further $D\ge 100$ extension), as in the main-text dimension-gating figure." The main text's Table 5 (tab:dim-gating) defines four tiers: $D<20$ / 20-49 / 50-99 / $D\ge100$. There is no dimension-gating figure.
root_cause: Residue of an earlier exhibit plan in which the gating pattern was a figure.
scientific_or_editorial_justification: Sec. 10.11 requires exhibits to be cited by their exact type and label; Sec. 14.14 requires full cross-referencing.
impact_on_validity_or_acceptance: Minor navigational defect.
required_correction: Change "figure" to "Table 5 (tab:dim-gating)" and align the tier description to the four-tier statement.
acceptable_alternatives: None.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: One tier vocabulary across both documents.
post_revision_verification: Confirm the rendered supplement cites Table 5 by number and lists four tiers.
status: open
```

```text
ticket_id: S14-017
review_stage: Stage 14.9 / 14.14
reviewer_role: AE (s14_sections)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: exhibit
manuscript_location: papers/sections/performance.tex:753-754 and the Table 16 caption :767-769; papers/supplementary.tex:1212
claim_id_or_artifact_id: S6.5 / S6.7 / AN-COST-2017
concise_issue: Three pointers send the reader to S6.7 for "the isolated compute cost of the interaction-structure memory"; S6.7 is titled "Implementation Caveats: Two Corrected Defects and Their Evidence Trail" and the primary statement of that result is S6.5.
exact_evidence_or_observation: performance.tex:753-754 "The isolated compute cost of the interaction-structure memory is quantified in the Supplementary Material (Section S6.7)"; Table 16 caption :767-769 same; supplementary.tex:1212 same. Rendered supplement heading list: S6.5 "ISM-Overlay Isolation: Direct Component Study" (states +57.3% / +36.3% / +30.3%), S6.7 "Implementation Caveats..." (restates the same three figures as measurement provenance).
root_cause: The overhead figures were re-measured under the M038 fix and the pointers were retargeted to the defect-provenance subsection instead of the results subsection.
scientific_or_editorial_justification: Sec. 14.14 requires the supplement to be fully cross-referenced; a pointer that resolves to the provenance of a number rather than the number's home is imprecise.
impact_on_validity_or_acceptance: Navigational only; not a dangling reference.
required_correction: Retarget to S6.5, optionally "see also S6.7 for the measurement provenance".
acceptable_alternatives: Keep S6.7 and add "(measurement provenance; the figures are reported in S6.5)".
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Pointers resolve to where the result is stated.
post_revision_verification: Follow each rendered pointer and confirm it lands on the subsection that states the figures.
status: open
```

```text
ticket_id: S14-018
review_stage: Stage 14.7 (presentation; Sec. 10.17.1 / 10.17.7)
reviewer_role: AE (s14_sections)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: exhibit
manuscript_location: papers/sections/proposed_algorithm.tex:135 (Table 4 tabular spec), :236 (Table 5), plus the phase_03 notation tables; rendered DT-GSK.pdf pp. 13-14
claim_id_or_artifact_id: T-ARCH / T-DIMGATE / ART-NOTATION
concise_issue: Justified p{} columns produce large inter-word gaps in the first column of the architecture and gating tables.
exact_evidence_or_observation: Rendered p. 13, Table 4 first column: "Inherited    GSK    core", "1.      NLPSR    schedule", "4.                ISM interaction-structure memory", "5.        Local    search", "7.    High-D    controllers (basin        memory,". Same pattern in Table 5 and the notation tables.
root_cause: LaTeX p{} columns justify by default; no \raggedright was applied.
scientific_or_editorial_justification: Sec. 10.17.1 and 10.17.7 require clean, human-legible, visually balanced exhibits; rivers in a narrow column are a classic machine-typeset tell.
impact_on_validity_or_acceptance: Presentation only, but on the two most-read method tables.
required_correction: Change p{...} to >{\raggedright\arraybackslash}p{...} for all narrow text columns.
acceptable_alternatives: Widen the first column.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: No inter-word rivers; tables read as authored.
post_revision_verification: Re-render and inspect pp. 13-14 at 150 dpi.
status: open
```

```text
ticket_id: S14-019
review_stage: Stage 14.7 (Sec. 10.17.2)
reviewer_role: AE (s14_sections)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: exhibit
manuscript_location: build_prompt_phases/phase_03/algorithm_pseudocode.tex (Algorithm 1 steps 12 and 14); rendered DT-GSK.pdf p. 10
claim_id_or_artifact_id: ART-PSEUDOCODE / alg:dt-gsk
concise_issue: Two pseudocode steps wrap so that the continuation line starts at the left margin and the right-aligned equation annotation lands on a continuation line.
exact_evidence_or_observation: Rendered p. 10 — step 12 wraps across three lines with "> Eq. (5)" on the third; step 14's comment wraps so that "non-selectable" begins flush at the left margin below the step-number column, reading as a stray line rather than a continuation.
root_cause: Long single-line steps with right-aligned \Comment annotations in algpseudocode.
scientific_or_editorial_justification: Sec. 10.17.2 requires "wrapped-line hanging that never collides with the margin"; Sec. 10.17.6 requires each line to carry a single primary logical operation.
impact_on_validity_or_acceptance: Presentation only; the content is correct and matches the loop order.
required_correction: Split step 12 into two steps (form the block mask; apply the KR mask to the remainder) and move step 14's comment to a short right-aligned note or a following unnumbered line; re-render and confirm no continuation starts at the margin.
acceptable_alternatives: Add explicit hanging indentation for continuation lines.
additional_evidence_needed: None.
dependencies: Any split must preserve step order and behaviour (Sec. 10.17.6 behaviour preservation) and stay consistent with the 13-step prose list and Fig. 2.
expected_improvement: A pseudocode block that parses at a glance.
post_revision_verification: Re-render p. 10; verify the step count and order still match proposed_algorithm.tex:184-202 and Fig. 2.
status: open
```

```text
ticket_id: S14-020
review_stage: Stage 14.7 (Sec. 10.17.7)
reviewer_role: AE (s14_sections)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: exhibit
manuscript_location: papers/figures/concept/fig_gsk_flowchart.pdf and fig_dtgsk_flowchart.pdf (sources fig_*_src.tex); rendered DT-GSK.pdf pp. 11-12
claim_id_or_artifact_id: FIG-ARCH / fig:gsk-flowchart / fig:dtgsk-flowchart
concise_issue: The two flowcharts render in Computer Modern while the manuscript body uses the MDPI text font, producing a visible typographic seam across two full-page figures.
exact_evidence_or_observation: Rendered p. 11: box text ("Begin", "Initialize population size NP...", "Is the termination criterion satisfied?") is Computer Modern; the caption and body on the same page are not. Same on p. 12.
root_cause: The standalone TikZ sources do not load the document's text font.
scientific_or_editorial_justification: Sec. 10.17.1/10.17.7 require a consistent, authored visual standard across all artifacts.
impact_on_validity_or_acceptance: Presentation only, but on the paper's two largest exhibits.
required_correction: Load the same text font package in the flowchart standalone preambles and regenerate; no content change.
acceptable_alternatives: Render the flowcharts inline in the document rather than as external PDFs.
additional_evidence_needed: None.
dependencies: Regeneration must not alter any box text (Sec. 10.17.6 behaviour preservation).
expected_improvement: One typographic voice across body and figures.
post_revision_verification: Re-render pp. 11-12 and compare glyph shapes against the body text; diff the box text before and after.
status: open
```

```text
ticket_id: S14-021
review_stage: Stage 14.14
reviewer_role: AE (s14_sections)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: writing
manuscript_location: papers/main.tex:186-200 (\supplementary block)
claim_id_or_artifact_id: M-003 (supplement-description drift validator)
concise_issue: The main text's supplementary description omits S6.6 (by-class conditional benefit) and S6.7 (implementation caveats), although S6.6's result is asserted in both the Introduction and the Conclusions, and the supplement's own abstract does list it.
exact_evidence_or_observation: main.tex:196-200 describes S6 as "a scaffold remove-one decomposition and a direct isolation of the interaction-structure memory (which finds no significant standalone benefit at its active tiers)". Rendered supplement headings: S6.1-S6.7, including S6.6 "Conditional-Benefit Analysis by Function Class (Post-Hoc)" and S6.7 "Implementation Caveats: Two Corrected Defects and Their Evidence Trail". supplementary.tex:120-122 (supplement abstract) does list "a by-class conditional-benefit breakdown". validate_document_consistency.py passes because it checks only that S1..S6 labels are contiguous and count-matched at section level.
root_cause: The \supplementary block was written before S6.6/S6.7 were added and the M-003 validator checks section-level labels only.
scientific_or_editorial_justification: Sec. 14.14 requires the supplement inventory to be accurate and fully cross-referenced.
impact_on_validity_or_acceptance: Minor, but it is the same omission that lets S14-006's unlabelled exploratory result pass unnoticed.
required_correction: Add the by-class breakdown (labelled exploratory) and the implementation-caveats subsection to the \supplementary description.
acceptable_alternatives: Describe S6 at subsection granularity in one clause.
additional_evidence_needed: None.
dependencies: S14-006.
expected_improvement: The two descriptions of S6 agree.
post_revision_verification: Extend validate_document_consistency.py to compare the \supplementary description against subsection headings, not only section labels.
status: open
```

```text
ticket_id: S14-022
review_stage: Stage 14.14
reviewer_role: AE (s14_sections)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/supplementary.tex:6 (file header comment)
claim_id_or_artifact_id: R-06
concise_issue: The supplement's source header still asserts the superseded release as the binding evidence release.
exact_evidence_or_observation: supplementary.tex:6 — "%% Every empirical value traces to evidence release rel-2026-07-16-78f075cb0." The rendered supplement correctly states rel-2026-07-20-67d9345f9 as current (S5.2 item 7 and the release subsection). Source-only; not reader-facing.
root_cause: R-06 corrected the rendered text but not the file header.
scientific_or_editorial_justification: Sec. 10.3 requires the source release ID to be recorded accurately wherever it is recorded; a stale header will mislead the next maintainer.
impact_on_validity_or_acceptance: None on the submission; maintenance hazard only.
required_correction: Update the header comment to rel-2026-07-20-67d9345f9.
acceptable_alternatives: Delete the release ID from the header and point to S5.2.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: No stale release ID anywhere in the manuscript sources.
post_revision_verification: Grep all papers/*.tex and papers/sections/*.tex for "rel-2026-07-16" and "rel-2026-07-10" and confirm every remaining occurrence is inside the deliberate S5.2 chronology.
status: open
```

```text
ticket_id: S14-023
review_stage: Stage 14.3 (Keywords)
reviewer_role: AE (s14_sections)
severity: Minor
priority: P3
confidence: High
issue_type: writing
manuscript_location: papers/main.tex:156-167; papers/supplementary.tex:131-142
claim_id_or_artifact_id: n/a
concise_issue: Two of ten keyword slots duplicate title strings, and the paper's coined term occupies a third; no established retrieval term for the underlying concept is present.
exact_evidence_or_observation: Keywords include "dimension-tiered adaptive control" and "deterministic final refinement", both near-verbatim from the title "DT-GSK: Dimension-Tiered Adaptive Control and Deterministic Refinement for Gaining-Sharing Knowledge Optimization"; "interaction-structure memory" is coined by this paper. Absent: "linkage learning", "variable interaction", "direct search", "differential evolution".
root_cause: Keywords were derived from the title and the contribution names.
scientific_or_editorial_justification: Sec. 14.3 asks for specificity, discoverability, non-duplication of title terms where advisable, and established field vocabulary.
impact_on_validity_or_acceptance: Discoverability only.
required_correction: Replace the two title-duplicating keywords with "linkage learning" and "direct search"; keep "interaction-structure memory" (it is the paper's object) but ensure at least one established synonym is present.
acceptable_alternatives: Any two established field terms that reach the relevant reader populations.
additional_evidence_needed: None.
dependencies: Keep main and supplement keyword lists identical.
expected_improvement: Better indexing reach at no cost.
post_revision_verification: Confirm both documents carry the same list and the count is <= 10.
status: open
```

```text
ticket_id: S14-024
review_stage: Stage 14.9
reviewer_role: AE (s14_sections)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: evidence
manuscript_location: papers/sections/performance.tex:287-303 (Sec. 4.2.1); :790-798 (Sec. 4.7 By function class)
claim_id_or_artifact_id: AN-CLASS-2017
concise_issue: The unimodal function class is silently omitted from the class-wise results and discussion; three of four CEC2017 classes are reported.
exact_evidence_or_observation: Sec. 4.2.1 discusses hybrid, simple multimodal and composition. class_ranks_cec2017.csv also contains "unimodal" (F1, F3): DT-GSK 4.00 (seven-way tie) at D=10, 2.50 at D=30, 2.50 at D=50, 2.00 (best) at D=100.
root_cause: The two-function class was presumably judged uninformative (all seven tie at D=10).
scientific_or_editorial_justification: Sec. 14.9 requires all primary evidence to appear; a silently dropped class invites the question of why.
impact_on_validity_or_acceptance: Low, and the omitted evidence is favourable, so there is no selective-reporting concern — but the omission should be stated.
required_correction: Add one clause noting the unimodal class (n = 2) and that all seven algorithms tie at the reporting floor at D = 10, so the class carries little discriminative information.
acceptable_alternatives: State the omission and its reason in the Sec. 4.2.1 opening sentence.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: All four classes accounted for.
post_revision_verification: Confirm the rendered Sec. 4.2.1 mentions all four CEC2017 classes.
status: open
```

```text
ticket_id: S14-025
review_stage: Stage 14.13 / 14.16
reviewer_role: AE (s14_sections)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: production
manuscript_location: papers/main.tex:15; papers/supplementary.tex:28
claim_id_or_artifact_id: n/a
concise_issue: MDPI submit-mode line numbering is disabled, removing the line references reviewers use to cite the manuscript.
exact_evidence_or_observation: main.tex:11-15 — "Suppress MDPI class 'submit' mode line numbers ... \let\linenumbers\relax"; the rendered PDF has no line numbers. The stated reason is avoiding the accept-mode journal logo, which does not require suppressing line numbers.
root_cause: A workaround for the missing accept-mode logo was applied more broadly than needed.
scientific_or_editorial_justification: Sec. 14.16 exemplar/template parity; the journal's own submit-mode output carries line numbers precisely for review.
impact_on_validity_or_acceptance: Reviewers frequently request a line-numbered version; shipping without one adds a round trip.
required_correction: Restore \linenumbers in submit mode (keeping the accept-mode logo workaround), or supply a line-numbered PDF alongside the submission.
acceptable_alternatives: Keep as is if the journal's submission system adds line numbers itself — verify before deciding.
additional_evidence_needed: Confirmation of the journal's current submission-system behaviour (author-side).
dependencies: None.
expected_improvement: Reviewer-citable line numbers.
post_revision_verification: Re-render and confirm line numbers appear without breaking the header suppression.
status: open
```

```text
ticket_id: S14-026
review_stage: Stage 14.7 (Sec. 10.17.4)
reviewer_role: AE (s14_sections)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: writing
manuscript_location: build_prompt_phases/phase_03/parameter_table.tex:14-15 (caption) and its closing note; rendered DT-GSK.pdf p. 20
claim_id_or_artifact_id: ART-PARAMS
concise_issue: A raw internal JSON filename appears in a reader-facing caption, and the accompanying pointer sends the reader to a 30-page supplement section rather than the relevant subsection.
exact_evidence_or_observation: Table 10 caption: "Hash-frozen in \texttt{algorithm\_freeze\_manifest.json}." Closing note: "Per-subsystem constants ... are listed in Supplementary Material, Section S5." The per-subsystem constants are in S5.7.
root_cause: The frozen phase_03 artifact carries the build-time filename and a coarse pointer.
scientific_or_editorial_justification: Sec. 10.17.4 prohibits internal engineering nouns in reader-facing text and permits one deliberate archival identifier in the reproducibility statement only.
impact_on_validity_or_acceptance: Presentation and navigation; overlaps S14-003, which is the substantive half of the same caption.
required_correction: Fix jointly with S14-003: remove the filename, point to S5.2 for the manifest chronology and to S5.7 for the per-subsystem constants.
acceptable_alternatives: Keep the filename only if S14-003's correctness problem is fixed and the filename is the current one.
additional_evidence_needed: None.
dependencies: S14-003.
expected_improvement: A caption that reads as authored and points precisely.
post_revision_verification: Re-render Table 10; grep the rendered PDF for ".json" and confirm no reader-facing hits outside the reproducibility statement.
status: open
```

```text
ticket_id: S14-027
review_stage: Stage 14 (governing-source staleness; recorded per seat instruction)
reviewer_role: AE (s14_sections)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/PAPER_REVIEW_PROMPT.md:118-602 (Sec. 1.5), :3177 (Sec. 10.1 binding table), :3299 (Sec. 10.7 RT-001), :3327-3349 (Sec. 10.9 narrowing)
claim_id_or_artifact_id: n/a (review-instrument defect, not a manuscript defect)
concise_issue: Three section-10 controls no longer describe the repository as it stands, in addition to the acknowledged Sec. 1.5 snapshot staleness.
exact_evidence_or_observation: (a) Sec. 10.1's binding table maps STATISTICAL_ANALYSIS_PLAN to papers/governance/statistical_analysis_plan.md; that path does not exist (find returns only papers/build_prompt_phases/phase_05/statistical_analysis_plan.md). (b) Sec. 10.7 RT-001 states the runtime table is being fixed "by re-timing all six comparators on one idle machine (scripts/retime_comparators.py)" and instructs the review to confirm that completion; the comparators were NOT re-timed — Table 16 now tabulates DT-GSK only and disclaims cross-algorithm comparison, while cost_cec2017.csv retains all seven rows flagged NOT-COMPARABLE-ACROSS-ALGORITHMS. (c) Sec. 10.9's narrowing sanctions the null "briefly: one abstract sentence plus the introduction's supporting-component paragraph"; the shipped manuscript states it in at least seven reader-facing places plus twice in the cover letter (see S14-012).
root_cause: The review prompt was frozen on 2026-07-20 and the package moved past it on 07-21/22; RT-001's remedy was changed from re-timing to removal without a prompt amendment.
scientific_or_editorial_justification: Sec. 1.4 precedence makes the current project state authoritative, and the seat instruction requires prompt staleness to be recorded as a finding.
impact_on_validity_or_acceptance: No effect on the manuscript. Effect on the review: other seats resolving the Sec. 10.1 binding literally will report a missing governance artifact, and a seat following RT-001 literally will look for a re-timing that never happened.
required_correction: Amend the review prompt: repoint the STATISTICAL_ANALYSIS_PLAN binding; restate RT-001 as resolved-by-removal with the actual resolution recorded; update the Sec. 10.9 narrowing to the scope the manuscript actually ships (or keep the brevity requirement and let S14-012 enforce it).
acceptable_alternatives: Record the three deltas in a review-side addendum rather than editing the prompt.
additional_evidence_needed: None.
dependencies: Should be reconciled before the consensus pass so seats do not disagree on the baseline.
expected_improvement: All seats review against the same, current baseline.
post_revision_verification: Re-resolve every Sec. 10.1 binding path and confirm each exists.
status: open
```

```text
ticket_id: S14-028
review_stage: Stage 14.15 (Cover letter)
reviewer_role: AE (s14_sections)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: production
manuscript_location: papers/cover_letter.tex:35, :55, :73-78
claim_id_or_artifact_id: R-0004 / AG author-fill
concise_issue: The cover letter is dated three days in the future, uses an inapposite hedge on a self-computed number, and omits any mention of the supplement or data availability.
exact_evidence_or_observation: cover_letter.tex:35 "25 July 2026" (review date 2026-07-22; date parity with cover_letter.md is checked and passes). :55 "To our knowledge, DT-GSK attains the best overall CEC2017 Friedman mean rank..." — the rank is computed by the authors, so "to our knowledge" invites a priority reading. No sentence names the Supplementary Material or the evidence release/repository. :73-78 correctly keeps the reviewer-suggestion instruction as a non-rendered comment.
root_cause: Date set to the planned submission day; hedge carried over from an earlier priority-flavoured draft.
scientific_or_editorial_justification: Sec. 14.15 applies the manuscript's claim ceiling to the cover letter and removes unverified novelty framing.
impact_on_validity_or_acceptance: Minimal; editorial polish plus a small desk-triage improvement.
required_correction: Set the date to the actual submission date at upload; delete "To our knowledge"; add one sentence naming the Supplementary Material and the availability of code, data and the frozen evidence release.
acceptable_alternatives: None needed.
additional_evidence_needed: Actual submission date (author-side).
dependencies: S14-012 (remove the duplicated null statement in the same pass).
expected_improvement: A letter that dates correctly, claims precisely, and helps desk triage.
post_revision_verification: Re-run validate_document_consistency.py to confirm cover_letter.md and .tex stay in parity after the edits.
status: open
```

```text
ticket_id: S14-029
review_stage: Stage 14.4 (Introduction)
reviewer_role: AE (s14_sections)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: claim-scope
manuscript_location: papers/sections/introduction.tex:50-62; rendered DT-GSK.pdf p. 2
claim_id_or_artifact_id: BG-03 / MT-08
concise_issue: The Introduction's framing promises that each documented family weakness is answered by a named DT-GSK subsystem, including the one assigned to ISM, which the paper's own evidence does not support.
exact_evidence_or_observation: introduction.tex:50-51 — "Each documented weakness in this lineage maps onto a named subsystem of the algorithm proposed here." :59-62 — "And the weakness that no descendant addresses --- recombination that treats every coordinate independently of the run's own improvement history --- is targeted by the interaction-structure memory (ISM)." The paper subsequently demotes ISM to "a supporting mechanism, not a contribution" (proposed_algorithm.tex:28) and reports no detectable standalone benefit (S6.5). The retraction paragraph sits AFTER the contribution bullets (introduction.tex:135), so a reader takes the promise before the qualification.
root_cause: The mapping paragraph predates the demotion of ISM from contribution to supporting mechanism.
scientific_or_editorial_justification: Sec. 14.4 requires that the claimed novelty be bounded and contributions not inflated; Sec. 16 prefers "The current design does not identify the component's independent causal effect" over efficacy-implying framing.
impact_on_validity_or_acceptance: A reviewer who reads the Introduction as a promise and the Conclusions as a null will read the paper as having failed its own stated aim, when in fact its aim was reframed. Fixing the verb fixes the reading.
required_correction: Change "maps onto"/"is targeted by" to motivation verbs ("motivates", "is the design target of"), and move the qualifying ISM paragraph (:135) to immediately before the contribution bullets so the framing and the qualification are read together.
acceptable_alternatives: Keep the paragraph position and add a forward pointer at :62 ("with the outcome of that design choice reported below and in Supplementary Material S6").
additional_evidence_needed: None.
dependencies: S14-005, S14-012 (same paragraph cluster).
expected_improvement: The Introduction's promise matches the paper's delivery.
post_revision_verification: Read pp. 2-4 straight through and confirm no efficacy promise for ISM precedes its qualification.
status: open
```

---

# 3. Scorecard (Stage 14)

| Section | Score | One-line basis |
|---|---:|---|
| 14.1 Title | 4 | Accurate, unhedged-superlative-free, journal-appropriate; only the "DT" gloss is implicit |
| 14.2 Abstract | 3 | Excellent loss-visibility and exposure disclosure, but the headline number is unscoped and one significance qualifier misattaches |
| 14.3 Keywords | 4 | Well spread; two slots wasted on title duplicates and no established retrieval synonym |
| 14.4 Introduction | 3 | Strong funnel and bounded contributions, undermined by an overstated null and an unlabelled exploratory result |
| 14.5 Related work | 4 | Genuine concept-level synthesis and card-bound limitations; the ATMALS-GSK reversal originates here unreconciled |
| 14.6 Background / notation | 4 | Clear inherited/new boundary; one symbol (`s`) left undefined by an incomplete R-01 closure |
| 14.7 Proposed method | 4 | Reimplementable specification with honest labels and disclosed dormant code; one false provenance pointer and several presentation defects |
| 14.8 Experimental setup | 4 | Exemplary disclosure of development exposure, pairing, budget crossing and the APGSK gap; two statistical-reporting defects originate here |
| 14.9 Results | 3 | All primary numbers verify and adverse cells are stated alongside favourable ones, but the effect-size column and the omnibus p-values are misreported |
| 14.10 Discussion | 3 | Correct mechanism labelling and calibrated summary, but no alternative explanation, no cost, no literature reconciliation |
| 14.11 Limitations | 4 | Unusually unflinching and near-complete against the §14.11 checklist; count mismatch and one omitted item in the main-text outline |
| 14.12 Conclusion | 3 | Well-bounded restatement, but introduces a new exploratory result and mis-states the limitation count |
| 14.13 Declarations | 3 | Exemplary conflicts and GenAI disclosure; a rendered placeholder on the title page is a desk-return risk |
| 14.14 Supplementary | 4 | Navigable, standalone, adverse-result-honest; three imprecise pointers and an incomplete inventory |
| 14.15 Cover letter | 4 | Claim ceiling respected, no flattery or impact promise; one duplicated statement and a stray hedge |
| 14.16 Exemplar parity | 4 | 22-dimension review frozen with Gate 4 evidence; four deviations, three of them unjustified as written |

**Stage 14 aggregate (unweighted mean): 3.56 / 5.**

**Stage 14 verdict:** *Major revision.* The manuscript's scientific substance, disclosure discipline and reproducibility engineering are well above the norm for this literature — the development-suite exposure, the loss-visibility parity, and the retained negative result are all things most submissions in this space omit. The blockers are not scientific: they are (i) two statistical-reporting defects that make printed values disagree with the released artifacts (S14-001, S14-002), (ii) one false provenance pointer in the main text (S14-003), (iii) an unreconciled contradiction with a comparator's published standing (S14-004), (iv) two claim-calibration slips in the framing sections (S14-005, S14-006), (v) a missing alternative-explanation paragraph in the Discussion (S14-008), and (vi) a rendered placeholder on the title page (S14-007). All seven are correctable in text against the existing frozen evidence: **no rerun, no new evidence release, and no change to the byte-locked optimizer core is required by any ticket in this register.**
