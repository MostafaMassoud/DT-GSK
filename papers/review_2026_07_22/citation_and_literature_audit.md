# Citation and Literature Audit — Stage 5

**Seat:** `s5_literature` (Stage 5 — literature review, source identity, citation audit)
**Lead role / team:** REP, supported by R1 · T6-INTEG (Ethics, Research-Integrity, Citation & Publication-Practice)
**Owning profile controls:** §10.2 (closed-corpus literature boundary), §10.5 (same-family claim boundary), §10.15 (`jawad2024egsk` venue metadata)
**Gate:** Gate E — Literature and Citation Integrity
**Date:** 2026-07-22
**Package audited:** git HEAD `45248eb31`; `papers/DT-GSK.pdf` 39 pp (verified via `pypdf`), `papers/supplementary.pdf` 61 pp, `papers/cover_letter.pdf` 2 pp; `papers/DT-GSK.docx`, `papers/supplementary.docx`; evidence release `rel-2026-07-20-67d9345f9`.
**Mode:** read-only. No manuscript, code, bibliography or governance file was modified. Only this artifact was written.

---

## 0. Executive verdict

**Gate E — Literature and Citation Integrity: PASS WITH CONDITIONS.**

Gate E fails only for (a) fabricated or unverifiable references, (b) material semantic mis-citation, (c) systematic literature bias that distorts novelty, or (d) uncorrected unattributed borrowing. **None of the four is present.** Every one of the 40 rendered references resolves to a locally readable, identity-verified source; I independently re-verified ten high-stakes related-work claims against the source PDFs rather than against the project's own evidence cards, and nine of ten reproduce exactly. There is no patchwriting. The self-citation concentration is high but structurally unavoidable for a within-family study and is disclosed twice, in the Conflicts-of-Interest statement and in the Limitations paragraph, with an accuracy I verified line by line.

The conditions are sixteen tickets below. The four that matter for submission are:

* **L-01** — the CEC2013 benchmark report reference **omits its fourth author** (Alfredo G. Hernández-Díaz). The printed reference list in both the PDF and the DOCX is factually wrong, and `reference_inventory.csv` certified this reference `verified` while recording `source_authors` identical to the (incorrect) bib field — i.e. the identity control did not independently read the title page for this row.
* **L-03 / L-04 / L-05** — three closed-corpus governance artifacts are stale or holed. Most seriously, `citation_role_map.csv` has **no row for `awad2016problem`**, the manuscript's most-used suite-definition citation (8 occurrences), and `literature_audit_report.md` still declares that same key **"WRONG DOCUMENT, inadmissible, blocked"** eleven days after CR-0005 resolved it. An auditor reading the governance directory as shipped would conclude Gate E fails; the underlying citation is in fact sound (I verified the local PDF myself).
* **L-06** — one confirmed adverse mischaracterization of a cited competitor (`nomer2021gskrl`), where the manuscript's clause contradicts that source's own result tallies and conclusion.
* **L-07** — the novelty boundary ("no GSK variant learns interaction structure") is stated at **three mutually inconsistent scopes** across the Introduction, §2.1 and §2.3, and §2.1's gap sentence sends the reader to a table that does not contain the variants it has just surveyed.

None of the sixteen requires new experiments, a rerun, or any change to the frozen optimizer core. All are text-, bibliography- or governance-artifact edits.

**Category score (Stage 5 scope): 4 — strong.** Minor non-blocking weaknesses only, with L-01 and L-03/L-04 to be cleared before packaging.

---

## 1. What I verified, and how

| Check | Method | Result |
|---|---|---|
| Corpus closure | `references.bib` keys vs `reference_papers/*.pdf` basenames | **57 : 57, exact one-to-one, 0 orphans in either direction** |
| Duplicate keys | parse of `references.bib` | 0 |
| `\nocite` | grep over `papers/*.tex`, `papers/sections/*.tex` | **0 occurrences** (§10.2 prohibition satisfied) |
| Cited-vs-printed, main | 40 distinct keys cited in `main.tex` + `sections/*.tex`; 40 `\bibitem` in `main.bbl` | **40 = 40, no cited-but-absent, no printed-but-uncited** |
| Cited-vs-printed, supplement | 8 keys cited in `supplementary.tex`; 8 in `supplementary.bbl` | **8 = 8, exact** |
| PDF↔DOCX bibliography parity | numbered-item extraction from `word/document.xml` | main **40 = 40**; supplement **8 = 8** |
| Citation-occurrence ledger | independent recount of every `\cite` occurrence vs `citation_usage_map.csv` | **117 = 117 rows**, all `in_allowed_57 = PASS`, all `in_build = yes` |
| Uncited bib entries | set difference | 17 (permitted — §10.2: "expected bibliography size does not require every source to be cited"); none of the 17 renders |
| Semantic verification | 10 load-bearing related-work claims re-derived from the **source PDFs**, not the evidence cards | 9 of 10 exact; 1 defect (L-06) |
| Patchwriting | related-work descriptions vs source abstracts/method sections | **none detected** — manuscript wording is independently authored and more technically specific than the sources |
| Author-list accuracy | automated surname cross-check of every cited entry against pp. 1–3 of its local PDF, plus manual title-page reads of the nine ≥4-author cited entries | one confirmed omission (L-01); two false positives (`Dem\v{s}ar` normalisation, `nelder1965simplex` image-only) |
| COI / self-citation accuracy | author list vs comparator authorship | **disclosure is exactly correct** (see §6) |

Semantic spot-checks that **reproduced exactly** against the source PDFs:

1. `mohamed2020gaining` — "first on the CEC2017 score metric against ten classical and recent metaheuristics" → Table 19: GSK Score 97.17, Ranking 1, over DE/AMO/SFS/TLBO/PSO/BBO/GA/GWO/ACO/ES = ten comparators. ✔
2. `mohamed2020gaining` — "third by Friedman rank on the 22 CEC2011 real-world problems" → Table 27: AMO 3.27 (1), SFS 3.48 (2), **GSK 3.80 (3)**. ✔
3. `jawad2024egsk` — "significantly worse than AGSK at *D* = 10" → Table 8, row `10 | eGSK vs AGSK | R+ 79 | R− 246 | p 0.025 | 9/4/16 | Dec. −`. ✔ (Note the source's own prose at p. 12 says "less than 0.05 except 10D", contradicting its own table; the manuscript correctly follows the table.)
4. `jawad2024egsk` — "leads at *D* ∈ {30,50,100}, competitive-only at *D* = 10" → Table 9 mean ranks 1.38 / 1.66 / 1.76, and abstract "exceptionally well … 30, 50, and 100 dimensions and is competitive in 10 dimensions". ✔
5. `alfadli2025atmals` — "ranks first on CEC2017 with eGSK second" → Table 18: ATMALS-GSK mean rank 2.24, Overall Rank 1; eGSK 2.84, Rank 2. ✔
6. `alfadli2025atmals` — "its authors acknowledge the computational overhead" → §6: "the introduction of memory-based mechanisms and local search strategies inevitably adds computational overhead, which might become significant in high-dimensional or real-time applications". ✔
7. `apgsk2021` — "comparisons against the CEC2020 winners show no statistically significant pairwise differences" → p. 65942: "From the Wilcoxon's test at 0.05 level of significance, it could be observed that there is no significant difference between all the algorithms." ✔
8. `fdbagsk2023` — "$1000\times D$ budget … at $D \in \{30,50,100\}$ … against AGSK variants only, with $D=10$ untested" → "1000*Dimension maximum function evaluations (maxFEs)"; "experimental studies conducted in 30/50/100 dimensions"; Table 4 "vs. AGSK". ✔
9. `hpe_agsk2025` — "groups its own improvements into population, hybrid, strategy, and composite categories" → p. 4: "The existing improvements of GSK can be divided into four parts: population improvement, hybrid method improvement, strategy improvement, and composite improvement." ✔
10. `omidvar2014dg` / `hansen2001cmaes` / `guo2015eig` — "$O(n^2/m)$ objective evaluations", evidence at $n=1000$, failure on overlapping/region-dependent separability; "~$n^2$ evaluations of adaptation time" for a significant shape change; "$O(D^3)$ per generation" → §III-B p. 6 / §8 p. 190 / p. 34 respectively. ✔

**Failed spot-check: `nomer2021gskrl` (ticket L-06).**

---

## 2. Source-identity exceptions

Every one of the 57 corpus entries has a local PDF, an evidence card and an inventory row. The exceptions below are cases where one of the Stage-5 identity criteria (title / authors / year / venue / DOI / **readable full text** / cited-version match / primary-vs-secondary) is only partially met. All are recorded, none is disqualifying, but three were **not** correctly recorded in the project's own artifacts.

| # | Key | Criterion at issue | Finding | Status |
|---|---|---|---|---|
| SI-1 | `liang2013cec2013` | **authors** | Local title page (PDF p. 2) reads "J. J. Liang¹, B. Y. Qu², P. N. Suganthan³, **Alfredo G. Hernández-Díaz⁴**". Bib and both rendered reference lists carry **three** authors. `reference_inventory.csv` records `source_authors` = `bib_authors` = the three-author form and certifies `identity_status = verified`. | **Ticket L-01 — open** |
| SI-2 | `efron1993introduction` | **readable full text** | Local file is a **60-page excerpt ending at book p. 43**. The BCa method lives in Ch. 14 §14.3 (book p. 184) and Ch. 22.4 (p. 325) — present only in the table of contents. The evidence card is explicit: "no technical property of BCa … can be supported by a locator from this corpus". Manuscript uses only the sanctioned **bare attribution**, so it is compliant today. | **Ticket L-09 — advisory / monitor** |
| SI-3 | `nelder1965simplex` | **readable full text** | `readability_status = image_only_no_text_layer`; identity verified visually; no verbatim quotation permitted. Cited twice for substantive method-lineage claims (`proposed_algorithm.tex:576`). No quotation is used. | **Ticket L-10 — recorded exception** |
| SI-4 | `omidvar2014dg` | **version match** | Local copy is the IEEE **author-accepted manuscript** ("VOL. X, NO. X", © 2013); the bib cites final TEVC 18(3):378–393. Card pins locators to manuscript pp. 1–16 and forbids citing 378–393 as verified. Rendered reference prints 378–393 — acceptable as the canonical published record, but no page-precise locator may be claimed. | Compliant; noted |
| SI-5 | `nomer2021gskrl` | **venue / year / DOI** | Local file is an **author version without conference branding**; NILES 2021 venue, year and DOI are not confirmable from the file. Card states this plainly. | Compliant; noted |
| SI-6 | `awad2016problem` | **document identity** (historical) | Previously the **wrong document** (Wu/Mallipeddi/Suganthan *constrained* report). **Resolved CR-0005 (2026-07-10).** I re-verified independently: local `awad2016problem.pdf`, sha256 `b69f52f047f6bca888787ac19f3f1224293000c0a2446bdd5c355795efa9684a`, title page reads "…Single Objective Real-Parameter Numerical Optimization" (no "Constrained"), N. H. Awad / M. Z. Ali / P. N. Suganthan / J. J. Liang / B. Y. Qu, NTU technical report, "Modified on October 15th 2016". **Correct document. Closure is genuine.** | Correctly closed — but see L-03, L-04 |
| SI-7 | `awad2016problem` | **author order** | Title page lists Suganthan **third**; bib uses the conventional Awad/Ali/Liang/Qu/Suganthan order. The evidence card explicitly notes and accepts this ("same authors"). Contrast SI-1, where a name is *missing*, not reordered. | Compliant; documented |
| SI-8 | `jawad2024egsk` | **year / venue** (§10.15) | Bib key says 2024; the entry correctly carries **2025**, *Results in Control and Optimization* **19**, 100542, doi `10.1016/j.rico.2025.100542`, and the rendered reference 9 prints 2025. I grepped every prose mention of eGSK: **no sentence labels it by year**, so the §10.15 "venue metadata follows the Phase 1 evidence card and is never invented" requirement is met. | **Compliant — §10.15 satisfied** |
| SI-9 | `zhou2021iade` | **DOI** | Inventory records `source_doi = (not printed in local file)`. Key is **uncited**, so no reader-facing effect. | Compliant; uncited |
| SI-10 | `david_order_statistics` | **readable full text** | `partial_text_title_page_only`. Key is **uncited** in both main and supplement, although the `references.bib` comment still labels it "(cited in Theorem 1 proof sketch)". | Stale comment — see L-12 |

---

## 3. Citation-misuse list

I assessed all **117** citation occurrences for semantic role, strength-vs-source, multiplicity, and omitted limitations. **116 are defensible.** The list below is exhaustive.

### 3.1 Confirmed misuse

**CM-1 — `nomer2021gskrl`, `related_work.tex:118-120` (ticket L-06).**
Manuscript: *"Strategy refinements range from historical-probability expansion of AGSK's adaptation to a reinforcement-learned controller for $KF$/$KR$ that **gains at low dimension but is reported unstable at $D = 30$**."*
Source, Tables I–II and §VI: GSK-RL is better on **14** / equal **5** / worse **10** at *D* = 10, and better on **16** / equal **4** / worse **9** at *D* = 30. By the source's own tallies GSK-RL performs **better at *D* = 30 than at *D* = 10** — the opposite of the manuscript's direction. Instability is reported for **one function (F26)** at *D* = 30, attributed to a function unseen in training, not to the dimension. The source's **Conclusion** states: *"showed a better performance on problems with 10 and 30 dimensions. However the algorithm performance start to degrade with problems with high dimensions."*
The manuscript's clause is traceable only to the source's abstract sentence ("performance started to degrade on 30 dimensional problems and it showed unstable behaviour on some functions that the controller has never been trained on before"), which the source's own results and conclusion contradict. Selecting the abstract's characterisation, flattening "one untrained function" into a dimension-level property, and omitting the conclusion is a **wording-stronger-than-source** defect that makes a competing GSK variant look worse than its own data supports. Note this cuts *against* the manuscript's interest — which is why it reads as a compression error rather than bias — but it is still a citation-integrity defect a reviewer familiar with that paper would raise.
*Remedy (text-only, ~15 words):* "…a reinforcement-learned controller for $KF$/$KR$ whose authors report degradation and unstable behaviour on functions unseen during training~\cite{nomer2021gskrl}."

### 3.2 Attribution-precision items (source *does* support the clause; the wording reads as attribution to a secondary source)

**CM-2 — `demsar2006statistical`, `performance.tex:234` and `supplementary.tex:187` (ticket L-08).**
*"a Friedman test~\cite{friedman1937use} with the Iman–Davenport correction~\cite{demsar2006statistical}"* and *"Nemenyi critical-difference (CD) analysis~\cite{demsar2006statistical}"*. Demšar (2006) §3.2.2 p. 11 does present both the Iman–Davenport $F_F$ refinement and the Nemenyi CD formula — the evidence card confirms this at exact locators — so the citation **supports the clause**. But the **direct original sources** (Iman & Davenport 1980; Nemenyi 1963) are not in the closed corpus and §10.2 forbids adding them from memory or the web. The remedy is therefore purely a wording change that makes the secondary-source role explicit, e.g. *"the Iman–Davenport $F$ refinement as presented by Demšar~\cite{demsar2006statistical}"*. Flagged because the Stage-5 semantic audit asks explicitly "whether a direct original source is available"; the honest answer here is *available in the field, not available in the permitted corpus*, and the manuscript should say so rather than appear to attribute the method to Demšar.

**CM-3 — `wolpert1997nfl`, `performance.tex:872-874` (ticket L-13).**
*"Consistent with no-free-lunch considerations, none of these findings is offered as evidence of field-wide superiority: every comparative claim in this paper is bounded to the cited suites, budgets, and the seven-algorithm GSK-family panel~\cite{wolpert1997nfl}."* The NFL citation is anchored at the **end** of the sentence, adjacent to "seven-algorithm GSK-family panel", a clause it does not support; it supports the earlier clause about field-wide superiority. The evidence-card sanctioned role ("empirical claims must be scoped to the benchmarked problem classes rather than 'all problems'") is exactly right — only the placement is wrong. Editorial.

### 3.3 Explicitly checked and found **not** to be misuse

* `auer2002finite` + `fialho2010adaptive` (`proposed_algorithm.tex:312`, `related_work.tex:198`) — cited for the *framing* of operator selection as a bandit problem, with the manuscript stating in **both** places that "ACE is not an instance of those algorithms, and no regret bound is claimed for it" / "no regret guarantee transfers to the drifting rewards of an evolutionary run". This is a model of correctly bounded lineage citation.
* `demsar2006statistical` for Nemenyi **display** — the card prohibits Nemenyi when the question is control-structure (DT-GSK vs each comparator). The manuscript uses **Holm** for the control family and **Nemenyi** only for the seven-way all-pairs rank display. Correct on both counts.
* `efron1993introduction` at `performance.tex:241` and `supplementary.tex:458` — bare attribution of the BCa method only; neither location characterises BCa mechanics ($z_0$, acceleration, coverage). Inside the card's sanctioned envelope. See SI-2.
* `hussain2019metaheuristic` + `del2019bio` (`introduction.tex:25`) — supporting "surveys ask for fewer new metaphors and for more rigorous, statistically tested analysis of the algorithm families that already exist". Both cards sanction exactly this framing role. Not decorative: the sentence is the paper's stated rationale for staying inside one family.
* `omidvar2014dg` (`conclusions.tex:107`) — future-work framing, "pairing the memory with decomposition-style scaling in **the differential-grouping line**". The phrase "the line" correctly signals a research direction rather than attributing later work (DG2/RDG) to the 2014 paper, which the card forbids.
* `storn1997differential`, `zhang2009jade`, `tanabe2013shade`, `tanabe2014improving` — all used for mechanism lineage (DE arm, archive, success-history, LPSR) with explicit non-novelty labels in the text ("a variant of the APGSK NLPSR schedule, explicitly not claimed as new"). Correct.
* `mohamed2021novel` — **uncited**, and a source comment at `proposed_algorithm.tex:288-290` records that a previous draft used it as the APGSK referent, which was wrong (it is a SHADE/LSHADE mutation paper) and was corrected to `apgsk2021`. That fix is verified correct in the current text.

---

## 4. Missing-literature matrix

**Scoping note.** Prompt §1.5.4 directive (ii) places **external, non-GSK baseline comparisons out of scope for this cycle** and forbids treating them as a missing requirement, fairness gap, or rejection risk. I have obeyed that: nothing below is raised as a missing comparison, a fairness gap, or a rejection risk. ML-1 is raised **only** as a text-level literature-coverage item, and is marked Advisory accordingly.

| # | Concept / subfield | Present in corpus? | Cited? | Assessment | Severity |
|---|---|---|---|---|---|
| ML-1 | **CEC2017 competition state of the art** — jSO (`brest2017single`), EBOwithCMAR (`awad2017ensemble`), LSHADE-SPACMA (`mohamed2017lshadespacma`) | **Yes — all three, verified PDFs, full evidence cards, all in `allowed_citation_keys.txt`** | **No — zero occurrences in main, supplement or cover letter** | Related Work never names the published winners of the very competition whose suite is the paper's primary evidence. The *claim* side is fully protected — `conclusions.tex:71-72` and `supplementary.tex:1196-1198` state "no claim is made relative to other metaheuristic families **or to CEC competition winners**, and none can be read from these results" — so there is no overclaim to correct. The gap is purely one of **coverage**: three vetted, admissible sources sit unused where two sentences would visibly strengthen the paper's positioning at zero evidentiary cost. | **Advisory** |
| ML-2 | **LSGO / decomposition beyond 2014** — DG2, RDG/RDG3, MA-SW-Chains, modern CC frameworks | **No** | n/a | The manuscript's large-scale framing rests on a single 2014 source. This is **corpus-forced** (§10.2 bars adding sources from memory or the web) and is handled correctly in the text: §2.2 bounds the evidence ceiling to *D* = 100 and states "no claim is made at differential grouping's $n = 1000$ scale", and §5 says "the differential-grouping **line**". No defect. If the corpus is ever widened, this is the first place to extend. | None (recorded) |
| ML-3 | **Statistical-method originals** — Iman & Davenport (1980), Nemenyi (1963), Cliff (1993) | **No** | n/a | Corpus-forced. Iman–Davenport and Nemenyi are correctly sourced through Demšar (see CM-2); Cliff's delta is **not reported anywhere** in the manuscript (verified by grep), so its absence from the corpus creates no gap — the manuscript reports matched-pairs rank-biserial $r$ plus $A_{12}$, both of which have direct originals in the corpus (`vargha2000critique`). | None |
| ML-4 | **CEC2020 suite definition** | No | n/a | CEC2020 is discussed only as *another paper's* evidence base ("AGSK's evidence is confined to the ten CEC2020 functions at $D \le 20$"), sourced from `mohamed2020agsk` / `apgsk2021` themselves. No suite-definition claim is made about CEC2020, so no tech report is required. | None |
| ML-5 | **Further GSK-family variants in corpus but uncited** — `apgsk_imode2024`, `nabahat2024hybrid`, `navaneetha2022gskde` | Yes (verified, admissible) | No | Permitted by §10.2 ("expected bibliography size does not require every source to be cited"), and each is an application/hybrid whose category §2.1 already covers by example. **However**, §2.3's claim that "the survey scope is explicit and reproducible" invites the reader to reconstruct the survey; three admissible family variants sitting outside it weakens that claim. Fold into L-07's remedy. | Minor (folded into L-07) |
| ML-6 | **Opposing / negative findings on the cited comparators** | n/a | — | Well handled. §2.1 records eGSK's *D* = 10 significant loss to AGSK, ATMALS's overhead admission, APGSK's non-significance vs the CEC2020 winners, FDB-AGSK's reduced budget and untested *D* = 10, and GSK-RL's degradation. The related work is unusually candid about the comparators' weaknesses. | None |
| ML-7 | **Benchmark / dataset definitions** | Yes | Yes | `awad2016problem` (CEC2017), `das2011cec2011`, `liang2013cec2013` all cited and all verified by me as the **correct documents** (CEC2013 = real-parameter single-objective, *not* the LSGO suite; CEC2011 = Das & Suganthan real-world). | None |

**No "unsupported claim of exhaustive review" was found.** The manuscript repeatedly and explicitly disclaims exhaustiveness ("a bounded review of the GSK lineage rather than an exhaustive systematic search of the wider metaheuristic literature"; "it is not a state-of-the-art priority claim over the wider literature"). This is exactly the §10.2 "novelty claims must be bounded to the reviewed corpus" requirement, met.

**No chronology-only summary was found.** §2.1 is organised by *what is adapted* (parameters → donor policy → composite memory/local search), not by year, and §2.2 is organised by four analytic axes. This is genuine synthesis.

---

## 5. Related-work restructuring recommendations

The related-work section passes four of the five quality tests outright. The fifth — "where the specific unresolved gap lies" — is where the defect is.

| Test | Verdict | Evidence |
|---|---|---|
| 1. What each source contributes | **Pass** | Each of the six panel variants gets a mechanism sentence, an evidence-scope sentence and a limitation sentence, all card-bound. |
| 2. How groups of approaches differ | **Pass** | Three-level organisation (parameter adaptation / donor policy / composite designs); §2.2's four-axis taxonomy table separates DG, CMA-ES, eigenvector-DE and ISM cleanly. |
| 3. Where the unresolved gap lies | **Fail — L-07** | The gap claim is made at three different scopes, and the exhibit pointer is wrong. See below. |
| 4. How the present method differs | **Pass** | §2.3's three named deficiencies map one-to-one onto C1/C2/C3, with explicit non-novelty labels (NLPSR "not claimed as new"). |
| 5. Which limitations remain | **Pass** | "the evidence ceiling is $D = 100$"; "ISM is not claimed to recover the objective's true interaction structure or to confer rotational invariance"; "no convergence guarantee is claimed". |

**R-REC-1 (from L-07) — reconcile the three novelty scopes.** The same claim is asserted over three different populations:

* `introduction.tex:64-68` — *"The common boundary of **the five variants** … Within this cited family, none learns — or exploits — the interaction structure…"* → **5 comparator descendants**.
* `related_work.tex:126-131` — *"Across **all of these lines** the adapted quantity is a scalar control parameter … Within the cited GSK family, none of these variants learns — or exploits — the interaction structure … (Table~\ref{tab:family-review})."* → the preceding paragraph surveys **nine further variants** (`hpe_agsk2025`, `epd_gsk2024`, `jalali2021opposition`, `pogsk2023`, `nomer2021gskrl`, `zhong2021gskhho`, `liang2024gskwoa`, `chalabi2023mogsk`, `ma2023mgskdpmo`), so the population here is **≈15**.
* `related_work.tex:263-265` — *"The survey scope is explicit and reproducible. **It covers the original GSK and the published GSK-family variants of Table~\ref{tab:family-review}.**"* → **6**.

Two consequences. First, the paper's *stated, reproducible* survey scope (6 papers) is **narrower than the scope it actually surveyed and actually claims over** (≈15) — this needlessly weakens the novelty claim, since a reviewer taking §2.3 at face value will judge a "no variant does X" claim against six papers. Second, `related_work.tex:131` closes the ≈15-variant gap sentence with `(Table~\ref{tab:family-review})`, but that table contains only the six panel algorithms — **none** of the nine variants the sentence is about. A reader who follows the pointer to check the claim finds the wrong exhibit.

*Recommended fix (two clauses, no new citations, no scope change to any result):*
> `related_work.tex:131` — replace `(Table~\ref{tab:family-review})` with a pointer to the surveyed set, e.g. "(the panel variants of Table~\ref{tab:family-review} and the further variants surveyed above)".
> `related_work.tex:263-265` — replace "It covers the original GSK and the published GSK-family variants of Table~\ref{tab:family-review}." with "It covers the original GSK, the six panel variants of Table~\ref{tab:family-review}, and the further published GSK-family variants surveyed in Section~\ref{sec:rel:family}."
> `introduction.tex:64-66` — replace "the five variants" with "the GSK-family variants surveyed in Section~\ref{sec:related}" so the three statements name one population.

**R-REC-2 (from ML-1) — two sentences on the out-of-family CEC2017 record.** At the end of §2.2, add a short passage acknowledging that the CEC2017 suite has published competition entrants (`brest2017single`, `awad2017ensemble`, `mohamed2017lshadespacma`) and stating in the same breath that this study does not compare against them, with the reason (one code base, one harness, one budget protocol) already articulated in C3. This converts a silence a reviewer will notice into an explicit, defended design choice, costs three already-vetted citations, and adds no claim. Strictly optional under §1.5.4 directive (ii).

**R-REC-3 (from CM-2) — name the secondary-source role once.** In `performance.tex`, change the Iman–Davenport and Nemenyi attributions so that Demšar is visibly the *presenting* source, not the originator.

---

## 6. Bibliography consistency report

### 6.1 Clean

* 57 entries, 57 local PDFs, **exact one-to-one**; 0 duplicate keys; **no `\nocite`**; no cited-but-unprinted or printed-but-uncited entry in either document; PDF↔DOCX bibliography parity exact (40/40 main, 8/8 supplement).
* DOI or a documented persistent-identifier substitute on every entry that has one. The two DOI-less journal entries (`demsar2006statistical`, `holm1979simple`) each carry a `url` **and** an explanatory `note` — good practice, but see BC-1.
* Techreport entries are correctly typed `@techreport`; the two GECCO/CEC/ICSI entries are correctly `@inproceedings`; `efron1993introduction` and `david_order_statistics` correctly `@book`.
* Rendered reference list is clean of raw BibTeX keys, internal registry IDs and placeholder tokens (§10.17.4 satisfied in the bibliography).

### 6.2 Defects

**BC-1 — dangling "above" self-references in the printed bibliography (ticket L-02, CONFIRMED, both formats).**
The MDPI `.bst` **suppresses the `url` field but prints the `note` field**. Result, in the rendered PDF at `DT-GSK.pdf` p. 38 and identically in `DT-GSK.docx`, `supplementary.pdf` and `supplementary.docx`:

> **34.** Holm, S. A Simple Sequentially Rejective Multiple Test Procedure. *Scandinavian Journal of Statistics* 1979, 6, 65–70. The 1979 issue predates CrossRef DOI assignment for this journal; **JSTOR record above** is the canonical stable identifier.
> **37.** Demšar, J. Statistical Comparisons of Classifiers over Multiple Data Sets. *Journal of Machine Learning Research* 2006, 7, 1–30. JMLR volumes from 2006 predate formal DOI assignment; **URL above** is the canonical publisher-hosted record.

There is no URL above — or anywhere. Verified in `main.bbl` (the `\newblock` carrying the note is present, the `url` is absent) and by string count in both `.docx` files (`"JSTOR record above"` ×1, `"URL above"` ×1 in each). A production editor will flag this. *Remedy:* rewrite both `note` fields to be self-contained and inline the identifier, e.g. `note = {JMLR volumes from 2006 predate formal DOI assignment; canonical record: https://www.jmlr.org/papers/v7/demsar06a.html}` — or move the URL into a field the style prints.

**BC-2 — omitted author on a load-bearing reference (ticket L-01, CONFIRMED).** See SI-1. `liang2013cec2013` drops Alfredo G. Hernández-Díaz. Cited twice in the main text (`performance.tex:66`, and the CEC2013 protocol) and once in the supplement; rendered as reference 32 in both formats.

**BC-3 — citation key ↔ entry-year mismatches (ticket L-11).** Keys are not reader-facing under the numeric MDPI style, so there is no rendered defect; these are maintenance hazards, and one has already caused a real wrong-referent citation that had to be fixed:

| Key | Key implies | Entry year | Note |
|---|---|---|---|
| `fialho2010adaptive` | 2010 | **2008** | Also: first author is **Da Costa**, not Fialho (correct in the entry and in rendered ref 25). |
| `mohamed2021novel` | 2021 | **2019** | Uncited. A prior draft used it as the APGSK referent — wrong paper; corrected to `apgsk2021`, see the comment at `proposed_algorithm.tex:288-290`. |
| `jawad2024egsk` | 2024 | **2025** | §10.15-relevant. Entry and rendered reference are correct; no prose labels eGSK by year. |

**BC-4 — field-usage quirks (ticket L-12).** `zhong2021gskhho` and `navaneetha2022gskde` place the article ID in the `number` field (`number = {e0250951}`, `number = {e7227}`) instead of the issue number; `liang2024gskwoa` omits the issue entirely. The MDPI style does not print `number`, so **nothing renders wrong today** — this is latent, and would surface under any style that prints issue numbers.

**BC-5 — stale in-file comment.** `references.bib:665` labels `david_order_statistics` as "cited in Theorem 1 proof sketch", but the key is uncited in both `main.bbl` and `supplementary.bbl`. Either restore the citation in the theorem's proof sketch or update the comment.

### 6.3 Governance-artifact consistency (§10.1 audit of the literature artifacts themselves)

| Artifact | State | Ticket |
|---|---|---|
| `references.bib` | Current and correct (modulo BC-2 … BC-5) | — |
| `allowed_citation_keys.txt` | **Current** — 57 keys, includes `awad2016problem` post-CR-0005 | — |
| `evidence_cards/` | **Current** — 57 cards; `awad2016problem.md` is a full ADMISSIBLE card with content certification, not the old blocked stub | — |
| `evidence_gap_register.md` | **Current** — EG-001 marked "RESOLVED CR-0005, 2026-07-10"; "NO remaining blocking literature gap" | — |
| `citation_usage_map.csv` | **Current** — 117 rows, matches my independent recount exactly, all PASS | — |
| `citation_role_map.csv` | **HOLED** — 56 rows; **no row for `awad2016problem`** | **L-03** |
| `literature_audit_report.md` | **STALE** — still declares `awad2016problem` inadmissible/blocked | **L-04** |
| `reference_inventory.csv` | **STALE** — 17 of 18 flagged rows describe a superseded `references.bib`; one row (`liang2013cec2013`) is substantively wrong | **L-05**, **L-01** |

On **L-05**, concretely: the inventory flags 18 rows as `minor_metadata_mismatch` / non-`readable`. I compared each row's `bib_*` columns against the **current** `references.bib`. **17 of 18 now match the `source_*` columns exactly** — i.e. the bibliography was corrected and the inventory was never updated. Examples: the row for `jawad2024egsk` still says the bib is "a @misc preprint/in-press placeholder (2024)" (it is a proper `@article` 2025 with DOI); `fialho2010adaptive` still says the entry "is typed @article with the GECCO proceedings name in the journal field" (it is `@inproceedings` with `booktitle`); `awad2017ensemble` still says "bib says 'with L-SHADE'" (the bib carries the correct source title). Only `zhou2021iade` remains genuinely divergent, and there the divergence is legitimate (`source_doi = (not printed in local file)`).

---

## 7. Citation-balance and publication-practice assessment

**Self-citation.** Of the 40 rendered references, **7 (17.5 %)** are co-authored by A. W. Mohamed: `mohamed2020gaining`, `mohamed2020agsk`, `apgsk2021`, `jawad2024egsk`, `alfadli2025atmals`, `chalabi2023mogsk`, `nomer2021gskrl`. By occurrence the figure is **41 of 117 (35.0 %)**. `jawad2024egsk` is additionally co-authored by H. S. M. Roshdy, the second author of this manuscript.

**Assessment: high, structurally unavoidable, and correctly disclosed — not a defect.** The paper's declared scope is a within-family study of the GSK lineage, and A. W. Mohamed originated GSK and co-authored four of the six comparators; a within-family paper cannot avoid citing them. Three independent factors rule out citation bias in the §10.2/Stage-5 sense:

1. **The disclosure is complete and I verified it is exactly accurate.** `main.tex:288-297` (Conflicts of Interest): *"Author A.W.M. is the originator of the baseline Gaining-Sharing Knowledge (GSK) algorithm and a co-author of the AGSK, APGSK, eGSK, and ATMALS-GSK variants used as within-family comparators in this paper; FDB-AGSK, a further comparator, is an independent third-party variant. Author H.S.M.R. is a co-author of the eGSK variant used as a comparator. Author M.E.M. is A.W.M.'s Ph.D. student."* I checked every element: FDB-AGSK is indeed Bakır/Duman/Guvenc/Kahraman with no overlap. The Limitations paragraph repeats it in the reader's path: *"Five of the six comparators were authored or co-authored by two of the present authors, and no external non-GSK baseline is included"* (`conclusions.tex:75-77`) — the count "five of six" is correct.
2. **The self-cited works are used adversely as often as favourably.** The manuscript reports that its own group's `jawad2024egsk` **beats DT-GSK** at CEC2017 *D* = 30, on CEC2013 *D* = 30, and with a Holm-significant win on CEC2011, and that the two are never Nemenyi-separable on CEC2017. §2.1 records limitations of AGSK, APGSK, eGSK and ATMALS-GSK drawn from those papers. This is the opposite of reciprocal citation inflation.
3. **No decorative citation and no citation-quota padding.** Every one of the 117 occurrences resolves to a card-sanctioned role; 17 corpus entries are simply not cited, and none is force-fitted into the text.

**One residual observation (not a ticket).** The COI statement carries a source comment `% AG-0004: conflict-of-interest wording drafted-unconfirmed; requires author confirmation before submission.` Author sign-off on that wording is the remaining step; the *content* is accurate as audited.

---

## 8. Tickets (mandatory §5.4 schema)

### L-01

```text
ticket_id: L-01
review_stage: Stage 5 — literature, source identity, citation audit
reviewer_role: REP / T6-INTEG (seat s5_literature)
severity: Moderate
priority: P1
confidence: Confirmed
issue_type: citation
manuscript_location: papers/references.bib:497-502 (@techreport liang2013cec2013); rendered reference 32 in papers/DT-GSK.pdf p.39 and papers/DT-GSK.docx; supplementary.bbl entry; cited at papers/sections/performance.tex:66 and papers/supplementary.tex:176
claim_id_or_artifact_id: liang2013cec2013 / reference_inventory.csv row `liang2013cec2013`
concise_issue: The CEC2013 benchmark-definition reference omits its fourth author, and the identity control certified the row `verified` while recording the source authors identical to the incorrect bib field.
exact_evidence_or_observation: |
  Local source title page, `reference_papers/liang2013cec2013.pdf` PDF p.2:
    "Problem Definitions and Evaluation Criteria for the CEC 2013 Special Session on Real-Parameter Optimization
     J. J. Liang1, B. Y. Qu2, P. N. Suganthan3, Alfredo G. Hernandez-Diaz4"
  references.bib: author = {Liang, J. J. and Qu, B. Y. and Suganthan, P. N.}   (three authors)
  Rendered PDF ref 32: "Liang, J.J.; Qu, B.Y.; Suganthan, P.N."               (three authors)
  reference_inventory.csv row: bib_authors == source_authors == "Liang, J. J. and Qu, B. Y. and Suganthan, P. N.";
                               identity_status = verified; notes = (empty)
  Automated cross-check of all 40 cited entries against pp.1-3 of their local PDFs found no other
  bib-author absent from its source; manual title-page reads of the nine cited entries with >=4 authors
  found no other omission. This case is isolated.
root_cause: The Phase-1 identity audit populated `source_authors` for this row from the bib entry rather than from the source title page, so the omission was invisible to the control that exists to catch exactly this.
scientific_or_editorial_justification: Stage 5's source-identity audit requires verification of authors against the source. A published reference list that drops a named author is an attribution error and a demonstrated failure of the verification control on a benchmark-definition citation that anchors an entire results suite.
impact_on_validity_or_acceptance: No experimental result is affected. It is a camera-ready attribution defect that a reviewer or MDPI production editor can catch, and it undermines confidence in the closed-corpus identity control that Gate E depends on.
required_correction: Add `Hern{\'a}ndez-D{\'i}az, Alfredo G.` as the fourth author in the `liang2013cec2013` bib entry; rebuild main.bbl/supplementary.bbl and both DOCX; update `reference_inventory.csv` `source_authors` from the title page and re-affirm `identity_status`.
acceptable_alternatives: None. The author list is either correct or it is not.
additional_evidence_needed: None — the local source is decisive.
dependencies: Bibliography rebuild touches both PDFs and both DOCX; sequence with L-02 so a single re-render clears both.
expected_improvement: Correct attribution in the printed reference list; the identity control's `source_authors` column becomes independently sourced for this row.
post_revision_verification: `pdftotext -layout papers/DT-GSK.pdf | sed -n '/^32\./,+3p'` shows four authors; the same string appears in `word/document.xml` of DT-GSK.docx; `reference_inventory.csv` row matches the title page.
status: open
```

### L-02

```text
ticket_id: L-02
review_stage: Stage 5
reviewer_role: REP / T6-INTEG (seat s5_literature)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: citation
manuscript_location: papers/references.bib:13 (demsar2006statistical note), :537 (holm1979simple note); rendered as refs 34 and 37 in papers/DT-GSK.pdf p.39 and DT-GSK.docx; refs 5 and 8 in supplementary.pdf / supplementary.docx
claim_id_or_artifact_id: main.bbl / supplementary.bbl
concise_issue: Two printed references contain dangling self-references ("JSTOR record above", "URL above") because the MDPI bibliography style prints the `note` field but suppresses the `url` field.
exact_evidence_or_observation: |
  main.bbl, holm1979simple:  "\newblock The 1979 issue predates CrossRef DOI assignment for this journal;
                              JSTOR record above is the canonical stable identifier."  (no \href, no url)
  main.bbl, demsar2006statistical: "\newblock JMLR volumes from 2006 predate formal DOI assignment;
                              URL above is the canonical publisher-hosted record."     (no \href, no url)
  Rendered PDF (pdftotext -enc UTF-8 -layout), lines 2255 and 2266: both notes print verbatim; no URL is printed
  anywhere in either entry.
  DOCX string counts: DT-GSK.docx "JSTOR record above" x1, "URL above" x1;
                      supplementary.docx "JSTOR record above" x1, "URL above" x1.
root_cause: `note` was written assuming the `url` field would render; the MDPI .bst drops `url` for @article.
scientific_or_editorial_justification: A reference that points the reader to an identifier that does not appear is a defective bibliographic record; it also defeats the very purpose of the note (supplying a persistent identifier where no DOI exists).
impact_on_validity_or_acceptance: No scientific effect. Camera-ready credibility; the persistent identifier the note promises is unavailable to the reader in all four rendered artifacts.
required_correction: Make both notes self-contained by inlining the identifier, e.g. `note = {JMLR volumes from 2006 predate formal DOI assignment; canonical record: https://www.jmlr.org/papers/v7/demsar06a.html}` and the analogous JSTOR URL for Holm; or switch to a field the style prints.
acceptable_alternatives: Delete the `note` fields entirely and accept a DOI-less entry (loses the persistent identifier — inferior).
additional_evidence_needed: None.
dependencies: Same rebuild as L-01.
expected_improvement: Both entries carry a resolvable identifier in all four rendered artifacts.
post_revision_verification: Zero occurrences of "above is the canonical" in the rendered text of DT-GSK.pdf, supplementary.pdf, DT-GSK.docx, supplementary.docx; the URL string is present in each.
status: open
```

### L-03

```text
ticket_id: L-03
review_stage: Stage 5
reviewer_role: REP / T6-INTEG (seat s5_literature)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/governance/citation_role_map.csv (56 rows); papers/governance/citation_usage_map.csv (awad2016problem rows)
claim_id_or_artifact_id: awad2016problem — §10.2 "every citation occurrence must have a defensible semantic role"
concise_issue: The citation role map has no row for `awad2016problem`, the manuscript's most-used suite-definition citation, so the §10.2 semantic-role control has a hole at exactly the load-bearing key; the project's own usage map records the gap inline but it was never closed.
exact_evidence_or_observation: |
  citation_role_map.csv: 56 data rows. Set difference against allowed_citation_keys.txt (57 keys):
      allowed but absent from role map -> ['awad2016problem']
      role map keys absent from allowed  -> []
  citation_usage_map.csv, awad2016problem rows carry:
      semantic_role = "CEC2017 suite-definition role (B.4; evidence card, CR-0005 resolved - role map row missing, stale)"
  awad2016problem occurrence count: 5 in main sources (introduction.tex:20, performance.tex:43, ...),
      3 in supplementary.tex (:167, :1817, :2071) = 8 total.
  papers/build_prompt_phases/phase_08/audit_manuscript.py:240 carries a hard-coded carve-out comment:
      "# citation_role_map.csv predates CR-0005 (2026-07-10): the ..."
  Substantively the citation is sound: I re-verified reference_papers/awad2016problem.pdf independently
  (sha256 b69f52f047f6bca888787ac19f3f1224293000c0a2446bdd5c355795efa9684a; title has no "Constrained";
  F1-F30; [-100,100]^D; MaxFES = 10^4*D), and evidence_cards/awad2016problem.md is a full ADMISSIBLE card.
root_cause: CR-0005 (2026-07-10) updated the inventory, the card, and `allowed_citation_keys.txt` but not the role map; the auditor was patched with a carve-out comment instead of the row being added.
scientific_or_editorial_justification: §10.2 requires a defensible semantic role for every citation occurrence, and §10.1 requires the governance artifacts to be internally consistent. A control with a documented hole at its highest-traffic key is not an effective control.
impact_on_validity_or_acceptance: No manuscript claim is wrong. It is a Gate E / §10.1 governance-integrity defect: the shipped artifact set cannot demonstrate role compliance for 8 of 117 citation occurrences.
required_correction: Add the `awad2016problem` row to `citation_role_map.csv` (group B.4; sanctioned uses and prohibited overextensions transcribed from `evidence_cards/awad2016problem.md` §3); remove the CR-0005 carve-out from `audit_manuscript.py:240`; regenerate `citation_usage_map.csv` so the `semantic_role` field no longer carries the "role map row missing, stale" parenthetical.
acceptable_alternatives: None — the row is required by the artifact's own contract (57 admissible keys).
additional_evidence_needed: None.
dependencies: Regenerating the usage map must leave the row count at 117 and all rows PASS.
expected_improvement: 57/57 role-map coverage; the §10.2 control is complete and machine-checkable.
post_revision_verification: `citation_role_map.csv` has 57 rows; set difference against `allowed_citation_keys.txt` is empty in both directions; no usage-map row contains the string "role map row missing".
status: open
```

### L-04

```text
ticket_id: L-04
review_stage: Stage 5
reviewer_role: REP / T6-INTEG (seat s5_literature)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/governance/literature_audit_report.md lines 21, 22, 33, 48, 55, 105, 154
claim_id_or_artifact_id: Phase-1 literature audit report vs CR-0005
concise_issue: The shipped literature-audit report still declares the CEC2017 suite-definition citation inadmissible and blocked, and still lists EG-001 as an open item, although CR-0005 resolved all of it on 2026-07-10. There is no supersession banner.
exact_evidence_or_observation: |
  literature_audit_report.md (Date: 2026-07-10, anchor 262fc16c9), current content:
    l.21  "| Runtime admissible set (`allowed_citation_keys.txt`) | **56** |"       -> repo has 57
    l.22  "| Inadmissible keys | 1 (`awad2016problem`) |"                            -> now admissible
    l.33  "| `major_mismatch` | 1 | **awad2016problem - WRONG DOCUMENT, inadmissible, blocked** |"
    l.48  "... Excluded; see EG-001 and the stub card."                              -> card is now a full ADMISSIBLE card
    l.55  "Suite-definition citations for CEC2017 are blocked (EG-001) ..."
    l.105 "| EG-001 | CEC2017 suite-definition citation (wrong local document) | **blocked** (interim narrow) |"
    l.154 "Open item carried forward: resolution of EG-001 ..."
  Contradicted by, in the same directory:
    evidence_gap_register.md:17  "## EG-001 - CEC2017 suite-definition citation (RESOLVED CR-0005, 2026-07-10)"
    evidence_gap_register.md:322 "EG-001 RESOLVED 2026-07-10 (CR-0005) - NO remaining blocking literature gap"
    evidence_cards/awad2016problem.md:1 "ADMISSIBLE (resolved CR-0005)"
    allowed_citation_keys.txt: 57 keys, includes awad2016problem
  The report also still describes jawad2024egsk as "bib is a @misc preprint placeholder (2024)" (l.60), superseded.
root_cause: CR-0005 updated the operational artifacts but the narrative report was left at its 2026-07-10 anchor with no supersession note.
scientific_or_editorial_justification: §10.1 requires governance artifacts to be audited for internal consistency, and Gate E depends on this report. As shipped, the literature audit asserts a Critical §10.2 compliance failure ("a used citation without a verified local source") that no longer exists.
impact_on_validity_or_acceptance: No manuscript claim is affected. A reviewer or auditor reading the governance package in file order would fail Gate E on the strength of this document alone.
required_correction: Add a dated supersession banner at the top recording CR-0005 and the resulting 56 -> 57 admissible-set change, and correct the seven listed lines (counts table, status table, EG-001 rows, the carried-forward open item, and the jawad2024egsk paragraph). Do not delete the historical record — mark it superseded.
acceptable_alternatives: Retain the 2026-07-10 report verbatim as a frozen historical artifact and add a separate current report, provided the historical one carries a prominent superseded banner.
additional_evidence_needed: None.
dependencies: State the same admissible-set count as L-03's remedy.
expected_improvement: The governance package presents one consistent literature-compliance state.
post_revision_verification: grep for "inadmissible", "blocked", "WRONG DOCUMENT" in literature_audit_report.md returns only text inside the clearly-marked historical/superseded block; the counts table reads 57.
status: open
```

### L-05

```text
ticket_id: L-05
review_stage: Stage 5
reviewer_role: REP / T6-INTEG (seat s5_literature)
severity: Minor
priority: P2
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/governance/reference_inventory.csv (18 rows with identity_status != verified or readability_status != readable)
claim_id_or_artifact_id: reference_inventory.csv
concise_issue: The inventory's `bib_*` columns and `identity_status` values describe a superseded `references.bib`; 17 of the 18 flagged rows have already been corrected in the bibliography and now match their `source_*` columns exactly.
exact_evidence_or_observation: |
  Programmatic comparison of every flagged row's source_year/source_doi against the CURRENT references.bib:
    NOW MATCHES SOURCE (inventory stale), 17 rows: jawad2024egsk, mohamed2021novel, jalali2021opposition,
      apgsk_imode2024, nabahat2024hybrid, zhong2021gskhho, navaneetha2022gskde, liang2024gskwoa,
      arini2022gjojos, hu2022qcsca, awad2017ensemble, kaveh2021pgo, nelder1965simplex,
      kolda2003directsearch, fialho2010adaptive, jones1995fitness, david_order_statistics
    STILL DIVERGENT, 1 row: zhou2021iade (source_doi = "(not printed in local file)" - legitimate, uncited key)
  Worked examples of the staleness:
    jawad2024egsk      inventory bib_year 2024, notes "@misc preprint/in-press placeholder"
                       -> current bib: @article, year 2025, doi 10.1016/j.rico.2025.100542
    fialho2010adaptive inventory notes "entry is typed @article with the GECCO proceedings name in the journal field"
                       -> current bib: @inproceedings with booktitle
    awad2017ensemble   inventory notes "Bib TITLE wording is wrong ... bib says 'with L-SHADE'"
                       -> current bib carries the correct source title
    mohamed2021novel   inventory bib_year 2021 / doi 10.1016/j.swevo.2019.100455
                       -> current bib: year 2019 / doi 10.1016/j.swevo.2018.10.006
root_cause: The bibliography was corrected through the change-request pipeline; the inventory's bib-side snapshot columns and status field were never re-synchronised.
scientific_or_editorial_justification: §10.1 requires governance artifacts to be complete and internally consistent. A reader of the inventory would conclude that 16 references still carry unresolved metadata mismatches.
impact_on_validity_or_acceptance: No manuscript claim affected. Governance hygiene; it also masks the one row (liang2013cec2013, ticket L-01) where the inventory is substantively wrong rather than merely stale.
required_correction: Re-derive the `bib_*` columns from the current `references.bib`, flip `identity_status` to `verified` for every row that now agrees with its source, and retain the resolution history in `notes` (do not discard it). Leave `zhou2021iade` flagged with its existing justification, and `nelder1965simplex` / `david_order_statistics` flagged on readability grounds only.
acceptable_alternatives: Add an `as_of_commit` column and a header note declaring the `bib_*` columns a frozen Phase-1 snapshot, making the semantics explicit rather than resynchronising.
additional_evidence_needed: None.
dependencies: Must be applied after L-01 so the liang2013cec2013 row is corrected, not merely resynchronised to a wrong bib.
expected_improvement: The inventory reports the actual current identity state of the corpus.
post_revision_verification: Re-run the bib-vs-inventory comparison; every remaining non-`verified` row has a live, source-attested reason.
status: open
```

### L-06

```text
ticket_id: L-06
review_stage: Stage 5
reviewer_role: REP / T6-INTEG (seat s5_literature)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: citation
manuscript_location: papers/sections/related_work.tex:117-120
claim_id_or_artifact_id: nomer2021gskrl (BG-02 related-work breadth)
concise_issue: The manuscript states that GSK-RL "gains at low dimension but is reported unstable at D = 30"; the source's own result tallies and conclusion contradict the direction of that claim.
exact_evidence_or_observation: |
  Manuscript, related_work.tex:117-120:
    "Strategy refinements range from historical-probability expansion of \agsk{}'s adaptation~\cite{hpe_agsk2025}
     to a reinforcement-learned controller for $KF$/$KR$ that gains at low dimension but is reported unstable
     at $D = 30$~\cite{nomer2021gskrl}."
  Source (reference_papers/nomer2021gskrl.pdf, author version):
    Table I / Sec.VI, D=10 : GSK-RL better 14, equal 5, worse 10  (of 29 functions)
    Table II / Sec.VI, D=30: GSK-RL better 16, equal 4, worse  9  (of 29 functions)   <- BETTER than at D=10
    Sec.VI, local p.5-6: "If we exclude the function F26 because it shows unstable behaviour for GSK-RL in 30
      dimensions, the GSK-RL performance will be significant over Basic GSK."   (instability = 1 function)
    Sec.VII CONCLUSION, local p.6: "The GSK-RL algorithm has been evaluated against Basic GSK and showed a
      better performance on problems with 10 and 30 dimensions. However the algorithm performance start to
      degrade with problems with high dimensions."
    Abstract, local p.1 (the only text supporting the manuscript's direction): "performed well on 10 dimensional
      problems but the performance started to degrade on 30 dimensional problems and it showed unstable
      behaviour on some functions that the controller has never been trained on before."
  The evidence card (evidence_cards/nomer2021gskrl.md Sec.8) sanctions "gains at low dimension and
  degradation/instability at D=30 and on unseen functions" - the card itself inherits the abstract's framing
  without reconciling it against the tallies it records at Sec.5.
root_cause: The clause was written from the source's abstract; the abstract contradicts the source's own tables and conclusion, and neither the card nor the prose reconciled them.
scientific_or_editorial_justification: The Stage-5 semantic audit asks whether the wording is stronger than the source and whether important limitations of the cited work are omitted. Here the manuscript adopts the least favourable of two contradictory statements in a competitor's paper, flattens single-function instability into a dimension-level property, and omits the source's own conclusion. Misrepresenting a rival adversely is a citation-integrity defect even when it does not benefit the manuscript's numbers.
impact_on_validity_or_acceptance: No DT-GSK result depends on this sentence. It is one clause in a breadth paragraph, but it is exactly the kind of item a reviewer who knows the cited paper will raise, and it weakens trust in the rest of a related-work section that is otherwise scrupulous.
required_correction: Restate scoped to what the source establishes, e.g. "...to a reinforcement-learned controller for $KF$/$KR$ whose authors report degradation at higher dimension and unstable behaviour on functions unseen during training~\cite{nomer2021gskrl}." Update evidence_cards/nomer2021gskrl.md Sec.8 to record the abstract-vs-results tension so the framing cannot be reintroduced.
acceptable_alternatives: Attribute explicitly ("its authors describe the D=30 behaviour as degraded and unstable, although the paper's own tallies favour GSK-RL at that dimension") - more precise but longer; or drop the performance clause and keep only the mechanism.
additional_evidence_needed: None - the local source is decisive.
dependencies: None.
expected_improvement: The related-work claim about a competing variant matches that variant's own evidence.
post_revision_verification: The revised sentence contains no dimension-level instability assertion; the card records both the abstract framing and the Table I/II tallies.
status: open
```

### L-07

```text
ticket_id: L-07
review_stage: Stage 5
reviewer_role: REP / T6-INTEG (seat s5_literature)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: claim-scope
manuscript_location: papers/sections/introduction.tex:64-68; papers/sections/related_work.tex:126-131; papers/sections/related_work.tex:257-269
claim_id_or_artifact_id: BG-03 (the "no GSK variant learns interaction structure" gap claim)
concise_issue: The paper's central novelty boundary is asserted at three mutually inconsistent scopes, and the gap sentence in Section 2.1 cross-references a table that does not contain the variants it has just surveyed.
exact_evidence_or_observation: |
  Scope A - introduction.tex:64-68:
    "The common boundary of the five variants is what they adapt: scalar control parameters, donor and
     selection policy, or the population's composition. Within this cited family, none learns --- or exploits ---
     the interaction structure of the moves the run has already accepted."          -> population = 5
  Scope B - related_work.tex:126-131 (closing Sec.2.1, after a paragraph surveying hpe_agsk2025, epd_gsk2024,
    jalali2021opposition, pogsk2023, nomer2021gskrl, zhong2021gskhho, liang2024gskwoa, chalabi2023mogsk,
    ma2023mgskdpmo - nine further variants):
    "Across all of these lines the adapted quantity is a scalar control parameter, a donor or selection policy,
     the population's composition, or a grafted foreign operator. Within the cited GSK family, none of these
     variants learns --- or exploits --- the interaction structure of the moves the run has already accepted
     (Table~\ref{tab:family-review})."                                              -> population = ~15
  Scope C - related_work.tex:263-265:
    "The survey scope is explicit and reproducible. It covers the original GSK and the published GSK-family
     variants of Table~\ref{tab:family-review}."                                    -> population = 6
  tab:family-review (related_work.tex:133-172) contains exactly six rows: GSK, AGSK, APGSK, FDB-AGSK,
  ATMALS-GSK, eGSK. It contains none of the nine variants that Scope B's sentence is about, so the
  cross-reference at line 131 sends the reader to the wrong exhibit to verify the claim.
  Additionally, three admissible GSK-family variants in the corpus (apgsk_imode2024, nabahat2024hybrid,
  navaneetha2022gskde) fall outside all three scopes while the paper calls its survey "reproducible".
root_cause: The bounded-gap wording was tightened separately in each of the three locations during successive remediation rounds without a single controlling definition of the surveyed population.
scientific_or_editorial_justification: The gap statement is the paper's novelty claim. A reproducibility statement (Scope C) that is narrower than the claim actually asserted (Scope B) both understates the work done and leaves the wider claim unsupported by any stated scope; the mis-pointed table reference defeats a reader's attempt to check it.
impact_on_validity_or_acceptance: The claim is defensible at the widest scope - I checked that all ~15 surveyed variants adapt parameters, donor/selection policy, population composition, or graft a foreign operator, and none learns accepted-move interaction structure. The defect is that the manuscript never says so consistently. A reviewer taking Sec.2.3 literally will judge a family-wide novelty claim against six papers.
required_correction: Define the surveyed population once and use it in all three locations. Concretely: (a) introduction.tex:64 - "the five variants" -> "the GSK-family variants surveyed in Section~\ref{sec:related}"; (b) related_work.tex:131 - replace "(Table~\ref{tab:family-review})" with a pointer covering both the panel table and the further variants; (c) related_work.tex:263-265 - "It covers the original GSK, the six panel variants of Table~\ref{tab:family-review}, and the further published GSK-family variants surveyed in Section~\ref{sec:rel:family}."
acceptable_alternatives: Narrow every occurrence to the six panel variants. Honest and internally consistent, but it discards nine variants of genuine survey work and makes the novelty claim thinner than the evidence supports - inferior.
additional_evidence_needed: A one-line decision on whether the three uncited corpus variants (apgsk_imode2024, nabahat2024hybrid, navaneetha2022gskde) are inside or outside the declared survey scope.
dependencies: None. Text-only; no claim, number or citation changes.
expected_improvement: One stated survey population, matching the scope at which the novelty claim is made, with a verifiable exhibit pointer.
post_revision_verification: All three locations name the same population; following the Sec.2.1 cross-reference reaches an exhibit or section that contains the variants under discussion.
status: open
```

### L-08 … L-16 (condensed schema — same fields, abbreviated for length)

```text
ticket_id: L-08
review_stage: Stage 5 | reviewer_role: REP/T6-INTEG | severity: Minor | priority: P2 | confidence: Confirmed
issue_type: citation
manuscript_location: papers/sections/performance.tex:234, :238; papers/supplementary.tex:187-189, :1853
concise_issue: The Iman-Davenport correction and the Nemenyi critical-difference test are cited to demsar2006statistical, which presents but did not originate them; the originals (Iman & Davenport 1980; Nemenyi 1963) are not in the closed corpus.
exact_evidence_or_observation: performance.tex:234 "a Friedman test~\cite{friedman1937use} with the Iman--Davenport correction~\cite{demsar2006statistical}"; :238 "Nemenyi critical-difference (CD) analysis~\cite{demsar2006statistical}". evidence_cards/demsar2006statistical.md findings 5 and 6 confirm both are presented at Demsar Sec.3.2.2 p.11 with exact locators, so the source DOES support the clause. Neither original is in references.bib or reference_papers/.
root_cause: Closed-corpus constraint (Sec.10.2 forbids adding sources from memory or the web), combined with wording that reads as origination rather than presentation.
scientific_or_editorial_justification: Stage 5 requires assessing "whether a direct original source is available". It is available in the field but not in the permitted corpus; the manuscript should make the secondary-source role visible rather than appear to attribute the methods to Demsar.
impact_on_validity_or_acceptance: No statistical result affected; attribution precision only.
required_correction: Reword to name the role, e.g. "the Iman--Davenport $F$ refinement as presented by Demsar~\cite{demsar2006statistical}" and "Nemenyi critical-difference analysis in the form given by~\cite{demsar2006statistical}".
acceptable_alternatives: Add the primary sources IF and ONLY IF readable local copies are supplied and inventoried; otherwise prohibited by Sec.10.2.
additional_evidence_needed: None. | dependencies: none
expected_improvement: Attribution is precise and the corpus boundary is visible to the reader.
post_revision_verification: No sentence attributes the origination of either method to demsar2006statistical.
status: open
```

```text
ticket_id: L-09
review_stage: Stage 5 | reviewer_role: REP/T6-INTEG | severity: Minor | priority: P3 | confidence: Confirmed
issue_type: evidence
manuscript_location: papers/sections/performance.tex:241; papers/supplementary.tex:458
concise_issue: Source-identity exception - the BCa chapter of the cited bootstrap textbook is not in the locally readable excerpt. The manuscript is compliant today (bare attribution only); recorded so any future edit cannot silently breach it.
exact_evidence_or_observation: evidence_cards/efron1993introduction.md l.8 "PARTIAL EXCERPT, 60 PDF pages only ... Nothing beyond book p.43 is present"; l.35-36 "Chapters 6-26 - including everything on bootstrap confidence intervals (bootstrap-t, percentile, and the BCa/ABC methods) - are NOT locally readable ... no technical property of BCa ... can be supported by a locator from this corpus"; l.53 permits "a bare attribution of the form 'the BCa method of Efron and Tibshirani (1993, Ch.14)'". Manuscript text at both locations names the method and describes only the authors' OWN procedure (n_boot, seeding, resampling unit) - inside the permitted envelope.
root_cause: Corpus holds a partial excerpt of the book.
scientific_or_editorial_justification: Stage 5 source-identity criterion "readable full text" is only partially met for a method-defining citation.
impact_on_validity_or_acceptance: None currently. Risk is prospective: any added sentence characterising BCa mechanics (z0, acceleration, second-order accuracy, coverage) would become an unsupported citation.
required_correction: None to the manuscript. Record the exception in the review record (done here) and add a one-line guard to evidence_gap_register.md so a future edit is caught.
acceptable_alternatives: Supply the full book or the Ch.14 pages to the corpus and re-inventory.
additional_evidence_needed: none | dependencies: none
expected_improvement: The exception is visible to future editors.
post_revision_verification: No manuscript sentence describes BCa internals.
status: accepted_risk
```

```text
ticket_id: L-10
review_stage: Stage 5 | reviewer_role: REP/T6-INTEG | severity: Minor | priority: P3 | confidence: Confirmed
issue_type: evidence
manuscript_location: papers/sections/proposed_algorithm.tex:573-576 (nelder1965simplex, twice)
concise_issue: Source-identity exception - the Nelder-Mead source has no text layer; identity was verified visually and no verbatim quotation is permitted from it.
exact_evidence_or_observation: reference_inventory.csv row nelder1965simplex: readability_status = "image_only_no_text_layer", identity_status = verified, admissible = yes. My automated surname cross-check flagged it (no extractable text) - consistent. Manuscript uses no quotation from it; the supported claims (simplex method; dimension-dependent behaviour; exclusion from the provably convergent class) are additionally carried by kolda2003directsearch, which is fully readable and whose card sanctions exactly those claims (pp.390, 429-430, 470).
root_cause: Scanned copy without OCR.
scientific_or_editorial_justification: "Readable full text" is a Stage-5 identity criterion; the exception must be recorded rather than assumed away.
impact_on_validity_or_acceptance: None - the substantive claims are double-sourced to a readable source.
required_correction: None. Recorded.
acceptable_alternatives: OCR the file or substitute a text-layer copy.
additional_evidence_needed: none | dependencies: none
expected_improvement: n/a
post_revision_verification: n/a
status: accepted_risk
```

```text
ticket_id: L-11
review_stage: Stage 5 | reviewer_role: REP/T6-INTEG | severity: Minor | priority: P2 | confidence: Confirmed
issue_type: citation
manuscript_location: papers/references.bib:70 (jawad2024egsk), :81 (mohamed2021novel), :630 (fialho2010adaptive)
concise_issue: Three citation keys encode a year that disagrees with their own entry, and one encodes the wrong first author. Not reader-facing under the numeric style, but one has already produced a wrong-referent citation.
exact_evidence_or_observation: fialho2010adaptive -> year = 2008, first author Da Costa (rendered ref 25 "Da Costa, L.; Fialho, A.; Schoenauer, M.; Sebag, M. ... 2008"); mohamed2021novel -> year = 2019; jawad2024egsk -> year = 2025 (rendered ref 9 correct). Evidence of realised harm: papers/sections/proposed_algorithm.tex:288-290 carries "% Phase 8 assembly citation fix: APGSK origin is apgsk2021 per governance/citation_role_map.csv (mohamed2021novel is a SHADE/LSHADE mutation paper, role B.2 -- wrong referent here)".
root_cause: Keys minted from provisional metadata before Phase-1 identity verification; never renamed after correction.
scientific_or_editorial_justification: Misleading keys are a maintenance hazard in a closed-corpus project where authors select citations by key.
impact_on_validity_or_acceptance: No rendered defect. Internal risk only.
required_correction: Either rename the keys to match their verified years (and update every \cite, the governance CSVs and the word tag map atomically), or - lower risk at this stage - add a one-line comment above each entry recording the key-vs-year divergence. Given the freeze, the comment is preferred.
acceptable_alternatives: Leave as-is with the divergence documented in reference_inventory.csv notes.
additional_evidence_needed: none | dependencies: renaming would touch the freeze manifest - not recommended pre-submission
expected_improvement: No future editor selects a citation by a misleading key.
post_revision_verification: Each of the three entries carries an explicit key-vs-year note.
status: open
```

```text
ticket_id: L-12
review_stage: Stage 5 | reviewer_role: REP/T6-INTEG | severity: Minor | priority: P3 | confidence: Confirmed
issue_type: citation
manuscript_location: papers/references.bib:333-343 (zhong2021gskhho), :345-355 (navaneetha2022gskde), :357-366 (liang2024gskwoa), :665-675 (david_order_statistics comment)
concise_issue: Latent BibTeX field-usage defects that the current style happens not to print, plus one stale in-file comment.
exact_evidence_or_observation: zhong2021gskhho has number = {e0250951} and pages = {e0250951} (issue is 5); navaneetha2022gskde has number = {e7227} and pages = {e7227} (issue is 21); liang2024gskwoa omits the issue. Rendered refs 17 and 18 print "PLoS ONE 2021, 16, e0250951" and "Mathematics 2024, 12, 636" - the MDPI style does not print `number`, so nothing is currently wrong on the page; reference_inventory.csv already records the zhong quirk. Separately, references.bib:665 comments "%% ---- Order statistics (cited in Theorem 1 proof sketch) ----" but david_order_statistics appears in neither main.bbl nor supplementary.bbl.
root_cause: Article-ID pasted into the issue field; comment not updated when the citation was dropped.
scientific_or_editorial_justification: Bibliography-consistency hygiene; latent breakage if the journal style changes at production.
impact_on_validity_or_acceptance: None today.
required_correction: Move the article IDs out of `number` into `pages` only (or supply the true issue numbers); add the issue number to liang2024gskwoa; correct or delete the david_order_statistics comment.
acceptable_alternatives: Defer to production copyediting.
additional_evidence_needed: none | dependencies: none
expected_improvement: Bibliography renders correctly under any style.
post_revision_verification: No `number` field contains an article ID; the stale comment is gone or accurate.
status: open
```

```text
ticket_id: L-13
review_stage: Stage 5 | reviewer_role: REP/T6-INTEG | severity: Editorial | priority: P3 | confidence: Confirmed
issue_type: citation
manuscript_location: papers/sections/performance.tex:872-874
concise_issue: The no-free-lunch citation is anchored to a clause it does not support.
exact_evidence_or_observation: "Consistent with no-free-lunch considerations, none of these findings is offered as evidence of field-wide superiority: every comparative claim in this paper is bounded to the cited suites, budgets, and the seven-algorithm GSK-family panel~\cite{wolpert1997nfl}." The citation sits after "seven-algorithm GSK-family panel"; the proposition wolpert1997nfl supports (per its card: "no optimizer is expected to dominate over ALL problems, hence empirical claims must be scoped to the benchmarked problem classes") is the earlier clause.
root_cause: End-of-sentence citation placement.
scientific_or_editorial_justification: Stage 5 requires each occurrence to support the exact clause it is attached to.
impact_on_validity_or_acceptance: None. Editorial precision.
required_correction: Move the citation to follow "no-free-lunch considerations~\cite{wolpert1997nfl}" at the head of the sentence.
acceptable_alternatives: none needed | additional_evidence_needed: none | dependencies: none
expected_improvement: Citation attaches to the clause it supports.
post_revision_verification: The citation follows the NFL clause.
status: open
```

```text
ticket_id: L-14
review_stage: Stage 5 | reviewer_role: REP/T6-INTEG | severity: Advisory | priority: P3 | confidence: Confirmed
issue_type: citation
manuscript_location: papers/sections/related_work.tex Sec.2.2 (proposed insertion point, after line 202)
concise_issue: Related Work contains no acknowledgment of the published CEC2017 competition entrants, although three such sources are in the approved corpus, fully verified, carded, and entirely uncited.
exact_evidence_or_observation: grep for "jSO", "EBOwithCMAR", "SPACMA", "LSHADE", "competition winner" across main.tex, sections/*.tex, supplementary.tex, cover_letter.tex returns no match in any body sentence. brest2017single, awad2017ensemble and mohamed2017lshadespacma are all in allowed_citation_keys.txt with identity_status verified, readable local PDFs and full evidence cards, and 0 citation occurrences. The CLAIM side is already protected: conclusions.tex:71-72 "with no claim against other metaheuristic families"; supplementary.tex:1196-1198 "no claim is made relative to other metaheuristic families or to CEC competition winners, and none can be read from these results".
root_cause: The within-family scope was applied to the citation set as well as to the comparator set.
scientific_or_editorial_justification: Stage 5's coverage-and-balance audit lists "closest competing methods" and "current and influential work available within the permitted search boundary". EXPRESSLY NOT raised as a missing comparison, fairness gap or rejection risk: prompt Sec.1.5.4 directive (ii) puts external non-GSK baselines out of scope for this cycle, and that directive is respected here. This is a text-level coverage item only.
impact_on_validity_or_acceptance: No claim is wrong. Positioning: a CEC-benchmark reviewer will notice that the suite's own competition record is unmentioned, and an explicit two-sentence acknowledgment converts a silence into a defended design choice at zero evidentiary cost.
required_correction: Optional. Two sentences at the end of Sec.2.2 naming the three entrants and stating that the study deliberately does not compare against them, with the C3 rationale (one code base, one protocol, one harness).
acceptable_alternatives: Take no action - fully permitted under Sec.1.5.4 directive (ii). This ticket is advisory and non-blocking.
additional_evidence_needed: none | dependencies: none
expected_improvement: Stronger positioning; three vetted corpus sources put to their sanctioned use.
post_revision_verification: If applied, the new sentences make no performance comparison and cite only corpus keys.
status: open
```

```text
ticket_id: L-15
review_stage: Stage 5 | reviewer_role: REP/T6-INTEG | severity: Advisory | priority: P3 | confidence: Confirmed
issue_type: compliance
manuscript_location: papers/scripts/ (validator set)
concise_issue: The Sec.10.2 closed-corpus citation controls are not enforced by any validator in the shipped gate set; the only consumer is a build-phase script outside the review gates, which is why L-03 persisted undetected.
exact_evidence_or_observation: Repository-wide grep for "allowed_citation_keys", "citation_role_map", "citation_usage_map" across *.py/*.ps1/*.sh outside papers/governance/ matches ONLY papers/build_prompt_phases/phase_08/audit_manuscript.py. None of papers/scripts/validate_*.py (build_hygiene, cross_format_parity, document_consistency, docx, evidence_bindings, provenance_claims, runtime_provenance) reads any of the three artifacts. I ran validate_document_consistency.py read-only: it passes and checks supplement inventory and cover-letter parity, not citations.
root_cause: Citation governance was executed as a build phase, not wired into the standing gate set.
scientific_or_editorial_justification: Sec.10.1 requires the governance artifacts to be auditable; a control with no automated check drifts, as L-03/L-04/L-05 demonstrate.
impact_on_validity_or_acceptance: Process risk, not a manuscript defect.
required_correction: Add a small read-only validator to papers/scripts/ asserting: (1) every \cite key is in allowed_citation_keys.txt; (2) every allowed key has a citation_role_map row; (3) citation_usage_map row count equals the recounted occurrence count; (4) main.bbl/supplementary.bbl key sets equal the cited sets; (5) no `note` field contains a dangling "above" reference (catches L-02 class).
acceptable_alternatives: Run audit_manuscript.py as a pre-submission gate and record its output in phase_gate_register.csv.
additional_evidence_needed: none | dependencies: L-03 should be fixed first, or the new validator fails on day one
expected_improvement: Sec.10.2 becomes machine-enforced.
post_revision_verification: The new validator is green and appears in the gate register.
status: open
```

```text
ticket_id: L-16
review_stage: Stage 5 | reviewer_role: REP/T6-INTEG | severity: Minor | priority: P2 | confidence: Confirmed
issue_type: compliance
manuscript_location: papers/PAPER_REVIEW_PROMPT.md Sec.1.5 (l.118), Sec.1.5.0-C item 2c (l.471), Sec.10.7 final bullet (l.3299)
concise_issue: MANDATED STALENESS RECORD - the governing prompt's embedded status snapshot predates the 2026-07-21/22 remediation and misstates the current package state.
exact_evidence_or_observation: |
  Prompt Sec.1.5 (dated 2026-07-20): "the 80-ticket remediation ledger ... stands at 73/80 fully closed ...
    and seven terminal / machine-gated / author-gated tickets remain open (RT-001 ...; C-008 -> C-001 ...)".
  Repo: papers/governance/remediation_2026_07_18/ticket_status.csv - 80 rows, lifecycle_status =
    {closed_verified: 70, superseded_with_evidence: 10}; ZERO open. C-001 records
    closed_by_commit = 383d7896be4034d25e46bf24da51c31dca6476e1, closed_utc = 2026-07-21.
  Prompt Sec.1.5.0-C item 2c and Sec.10.7 final bullet describe RT-001 as "IN PROGRESS" with the runtime table
    "provisionally frozen" pending a six-comparator re-timing. The manuscript resolved it differently, by scope
    narrowing: supplementary.tex:1203-1205 "The main-text runtime table reports \dtgsk{}'s own per-run cost only
    --- comparator timings came from a separate measurement session, so no cross-algorithm runtime comparison
    is drawn."
  Secondary: C-001's own closure evidence records "pages 38/60/2"; the current artifacts are 39/61/2
    (verified with pypdf), i.e. the manuscript grew by one page in main and one in the supplement during the
    2026-07-21/22 R-01..R-14 remediation after C-001 closed.
  Within this seat's scope, Sec.1.5's literature-relevant statement ("citation-usage map - deterministic,
    0 cite-key failures, 117 rows") is still ACCURATE - I recounted 117.
root_cause: The prompt snapshot is dated 2026-07-20 and was not re-derived after the 2026-07-21/22 remediation, exactly as Sec.1.4 precedence anticipates.
scientific_or_editorial_justification: Sec.1.4 makes the current project state outrank the prompt's embedded snapshot; recording the divergence is required so no seat reviews against superseded facts.
impact_on_validity_or_acceptance: No manuscript defect. Review-process hygiene. The page-count divergence is flagged for the Stage-0 / Gate-A seat, which owns package integrity - not raised as a ticket here.
required_correction: Re-derive Sec.1.5 / Sec.1.5.0-C / Sec.10.7's RT-001 bullet from the current ledger, freeze manifest and artifacts before the next review cycle; record RT-001's actual disposition (scope narrowing, not re-timing).
acceptable_alternatives: Add a dated "superseded as of 2026-07-22" banner to Sec.1.5 pointing to the ledger and the freeze manifest as authority.
additional_evidence_needed: none | dependencies: none
expected_improvement: Seats review against the actual package state.
post_revision_verification: Sec.1.5's ticket counts, RT-001 status and page counts match the repository.
status: open
```

---

## 9. Gate E determination

| Gate E failure condition | Present? | Evidence |
|---|---|---|
| Fabricated or unverifiable references | **No** | 57/57 keys resolve to a local PDF; all 40 rendered references identity-verified; the one historically wrong document (`awad2016problem`) was replaced under CR-0005 and I re-verified the replacement independently by sha256 and title-page content. |
| Material semantic mis-citation | **No** | 116 of 117 occurrences defensible; the single defect (L-06) is one clause in a breadth paragraph, affects no DT-GSK claim, and misstates a *competitor* adversely rather than inflating the manuscript. |
| Systematic literature bias distorting novelty | **No** | Self-citation is high (17.5 % of references, 35 % of occurrences) but structurally forced by the within-family design, fully disclosed in both the COI statement and the Limitations paragraph with verified accuracy, and used adversely as often as favourably. The novelty claim is explicitly bounded to the reviewed corpus at every occurrence, though inconsistently scoped (L-07). |
| Uncorrected unattributed borrowing | **No** | No patchwriting detected against any source abstract or method section. |

**Gate E: PASS WITH CONDITIONS.** Clear L-01 (incorrect printed attribution), L-02 (dangling bibliography notes), L-03 and L-04 (governance artifacts that, as shipped, assert a compliance failure that no longer exists), L-06 and L-07 before packaging. L-05, L-08 … L-16 may follow in the batch editorial pass.

**Minimum path to clearing this stage:** six text/bibliography edits (L-01, L-02, L-06, L-07, L-08, L-13) plus three governance-artifact updates (L-03, L-04, L-05). No new experiments, no rerun, no new evidence release, no change to the frozen optimizer core.

---

## 10. Files examined

Manuscript: `papers/main.tex`, `papers/sections/{introduction,related_work,proposed_algorithm,performance,conclusions}.tex`, `papers/supplementary.tex`, `papers/cover_letter.tex`, `papers/main.bbl`, `papers/supplementary.bbl`, `papers/references.bib`, `papers/DT-GSK.pdf`, `papers/supplementary.pdf`, `papers/cover_letter.pdf`, `papers/DT-GSK.docx`, `papers/supplementary.docx`.

Governance: `papers/governance/{reference_inventory.csv, allowed_citation_keys.txt, citation_role_map.csv, citation_usage_map.csv, literature_audit_report.md, evidence_gap_register.md}`, `papers/governance/evidence_cards/` (read in full: `awad2016problem`, `demsar2006statistical`, `efron1993introduction`, `hansen2001cmaes`, `omidvar2014dg`, `nomer2021gskrl`; supported-use sections: `hussain2019metaheuristic`, `del2019bio`, `wolpert1997nfl`, `kolda2003directsearch`), `papers/governance/remediation_2026_07_18/ticket_status.csv`, `papers/scripts/` (inventory; `validate_document_consistency.py` executed read-only).

Corpus sources read directly: `reference_papers/{awad2016problem, das2011cec2011, liang2013cec2013, mohamed2020gaining, mohamed2020agsk, apgsk2021, fdbagsk2023, jawad2024egsk, alfadli2025atmals, hpe_agsk2025, nomer2021gskrl, guo2015eig}.pdf`, plus automated first-page author extraction from all 40 cited sources.
