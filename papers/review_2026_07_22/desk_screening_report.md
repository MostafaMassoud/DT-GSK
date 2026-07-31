# Desk Screening and Scientific Significance Report

**Seat:** `s2-4_desk_significance` — Stage 2 (Editor-in-Chief desk screening) + Stage 4
(scientific significance, originality, contribution boundary)
**Lead roles:** EIC (Stage 2, team ECB) and R1 (Stage 4, team T1-OPT)
**Review date:** 2026-07-22
**Target journal:** *Algorithms* (MDPI), article type Article
**Package reviewed (verified in-repo, not from the prompt):**

| Item | Verified value | How verified |
|---|---|---|
| git HEAD | `45248eb31` | `git log --oneline -3` |
| Package manifest anchor | `abd2fa2f25c8426247b43c85bcb3d82041d00976` | `papers/governance/submission_package_manifest.json` |
| Freeze manifest | 15/15 match | `python papers/scripts/check_manifest.py` → `15/15 match []` |
| Evidence release | `rel-2026-07-20-67d9345f9` | manifest `evidence_release` field |
| `papers/DT-GSK.pdf` | **39 pp**, 695,943 B, SHA-256 matches manifest | PyMuPDF + SHA-256 recompute |
| `papers/supplementary.pdf` | **61 pp**, 1,155,151 B, SHA-256 matches manifest | idem |
| `papers/cover_letter.pdf` | **2 pp**, SHA-256 matches manifest | idem |
| Main-text exhibits | 16 tables + 7 figures + 1 algorithm | text scan of rendered PDF |
| LaTeX build health | 0 Overfull boxes (107 Underfull) | `papers/main.log` |

This is an internal simulation of an editorial decision, not a prediction of the
journal's actual decision, and it carries no acceptance or quartile guarantee.

---

## 0. Governing-prompt staleness (mandated record)

Per the §1.4 precedence order, the current repository state outranks the prompt's
embedded §1.5 snapshot (dated 2026-07-20). Four confirmed contradictions:

| # | Prompt statement | Repository state | Evidence |
|---|---|---|---|
| S-1 | §1.5: "the 80-ticket remediation ledger … stands at **73/80** fully closed … **seven** terminal / machine-gated / author-gated tickets remain open (RT-001 …; C-008 → C-001 …; N-009 / N-021 / M-007 / E-012)" | **80/80 resolved**: 70 `closed_verified` + 10 `superseded_with_evidence`; **zero open** | `papers/governance/remediation_2026_07_18/ticket_status.csv` (status tally) |
| S-2 | §10.7 final bullet: RT-001 "**IN PROGRESS**"; the runtime table "mixes two measurement sessions and is **provisionally frozen**" pending re-timing all six comparators via `scripts/retime_comparators.py` | The remedy actually taken was **removal, not re-timing**: `tab:runtime` now reports **DT-GSK only** and states "we do not tabulate a cross-algorithm wall-clock comparison". The described re-timing did not land and is no longer the plan. | `papers/sections/performance.tex:740-746` and `:759-786` |
| S-3 | §1.5 / §1.5.0-C: "C-008 → C-001 the terminal freeze+commit" remains open | C-001 `closed_verified` at `383d7896be40`; a **later** freeze re-mint exists (manifest anchor `abd2fa2f2`, `check_manifest` 15/15) and the package manifest already records the **current** 39/61/2-page build | `ticket_status.csv` row C-001; `submission_package_manifest.json`; `check_manifest.py` |
| S-4 | §1.5 predates R-01…R-14 entirely | R-01…R-13 closed (Phase-12 gate note) and R-14 closed at `dbc824782`; the Phase-12 register row still says "R-14 … **optional and open**" and still describes the SGSM overlay as "CEC2013 D50 — full D50/D100+overhead design **DEFERRED**", although the supplement now reports CEC2017 D50/D100 **and** CEC2013 D50 | `papers/governance/phase_gate_register.csv` row 12 (`notes`, `validation_evidence`); `papers/supplementary.tex:1999-2023` |

S-4's second half is a *governance-record* staleness (Phase-12 row), not a prompt
defect; it is logged here because it is the register a desk editor's compliance
check would consult. It is ticketed as **DS-11**.

---

## 1. Stage 2 — the twelve EIC questions

**Q1. Does the paper clearly fit the verified aims and scope of *Algorithms* (MDPI)?**
**Yes, with one caveat about the scope record itself.** The manuscript is a fully
specified algorithm with a formal update rule set, complexity accounting, an
algorithm listing, a reproducible artifact chain, and nonparametric statistical
comparison — squarely inside an algorithms journal's remit. The manuscript is wired
to the journal's own class (`\documentclass[algorithms,article,submit,moreauthors,pdftex]`,
`papers/main.tex:9`). **Caveat:** the project's own journal record carries
`verified_online = FALSE` — the official instructions page returned HTTP 403 on
2026-07-10 and was never re-fetched
(`papers/build_prompt_phases/phase_04/journal_requirements.md`, §11 re-verification
checklist, all four items still open). Per §15 I do not certify the journal's
quartile or its current requirements from memory. Scope fit is judged from the
manuscript's content, which is unambiguous; the *administrative* requirement record
remains unverified and is an author-side pre-submission action.

**Q2. Is the problem important enough for the journal's readership?**
**Yes, moderately.** Bound-constrained black-box optimization under a hard evaluation
budget is a standard, well-populated topic. The paper's framing is unusually
well-chosen for the current climate: it opens by citing the field's own calls for
fewer metaphors and more rigorous, statistically tested analysis of *existing*
families (`introduction.tex:21-26`, `hussain2019metaheuristic`, `del2019bio`) and then
does exactly that — one family, one harness, one frozen protocol. Importance is
"solid contribution to a mature area", not "changes the field".

**Q3. Do the title and abstract communicate a credible contribution rather than a
generic method variant?**
**Yes.** The title names two mechanisms (dimension-tiered adaptive control;
deterministic refinement), not a metaphor. The abstract is disciplined: exactly one
headline number (2.48), the aggregate explicitly labelled *descriptive*, and three
unfavorable facts stated in the abstract itself (second at D=30 and on CEC2011 with a
Holm-significant loss; never Nemenyi-separable; CEC2017 configuration-selection
exposed) — `papers/main.tex:138-152`. That level of self-qualification in an abstract
is rare and reads as credible rather than promotional. It is also, deliberately, close
to self-undermining (see Q7 and risk R-07).
Two nits: the rendered abstract is **201 words** against the build's own `<=200`
rule (`main.tex:123`; no validator enforces it — `papers/scripts/` contains no
abstract word-count check) — ticket **DS-09**.

**Q4. Is the novelty plausible and distinguishable from the closest work?**
**Partly — and the manuscript itself is the source of the doubt.** Distinguishability
against the *outside-family* structure-learning lines is handled well and explicitly
(Table `tab:taxonomy`, `related_work.tex:223-247`: differential grouping, CMA-ES,
eigenvector DE, each separated on update trigger / evaluation cost / what is learned /
how exploited, with two explicit non-claims). Within the family, the labelling is
honest to a fault: NLPSR is "explicitly not claimed as new", ACE/BSE/archive/restart
"modify cited antecedents", and the sole positive originality claim in C2 is ARGP.
The problem is that after ISM was correctly demoted out of the contribution set, the
*remaining* novelty is (a) one untested rule (ARGP — **DS-03**), (b) a compass search
in a final budget slice whose only distinguishing feature (the learned basis) the
paper concedes is unisolated (`introduction.tex:95-100`), and (c) evaluation
infrastructure. Novelty is plausible at Q2 level; at Q1 level it is thin. See §2.

**Q5. Is the paper technically mature enough to send to reviewers?**
**Yes.** `check_manifest` 15/15; every submission artifact's SHA-256 matches the
package manifest; the LaTeX build has zero overfull boxes; the claim vocabulary is
clean (a scan for `state-of-the-art` / `novel` / `outperform` / `superior` /
`significantly better` over all five section files, the front matter and the cover
letter returns **no reader-facing overclaim** — every hit is either a BibTeX-key
comment, a bounded non-claim, or an explicit *denial* of the claim, e.g.
`related_work.tex:268` "it is **not** a state-of-the-art priority claim",
`proposed_algorithm.tex:601` "whether … outperforms coordinate axes is **not**
established"). Maturity is not the blocker; two text-level correctness defects are
(DS-02, DS-03).

**Q6. Are the experiments or analyses substantial enough for the article type?**
**Yes, comfortably.** Three suites (CEC2017 29×4 dims ×51 runs; CEC2011 22 problems
×25 runs; CEC2013 28×3 dims ×51 runs), seven algorithms, one frozen protocol, paired
seeds, Friedman + Iman–Davenport, Wilcoxon with Holm within enumerated families,
A12/Cliff's delta/rank-biserial, BCa intervals, pre-registered robustness variants,
plus a seven-cell scaffold remove-one study and a four-cell overlay isolation in the
supplement. This exceeds the typical evidence density for the article type.

**Q7. Are the claims appropriately scoped?**
**Yes — with one asymmetry.** Every comparative statement is panel-bounded, the
across-dimension aggregate is repeatedly labelled descriptive, no family-wise claim
is made across dimensions (`conclusions.tex:41-45`), and no field-wide claim appears
anywhere. The asymmetry: the **cover letter** — the first document a desk editor
reads — states the headline rank without any of the three qualifiers the abstract
carries (**DS-05**). Separately, two disclosures draw their inferential boundary in
the wrong place: the eGSK solver-port qualification concludes only that no *runtime*
claim is made, when the substituted component is an *optimization* mechanism
(**DS-06**), and the Conclusions' limitations outline omits the self-initialization
asymmetry, the one confound the supplement itself calls unbounded and worst at a
headline-contributing tier (**DS-07**).

**Q8. Are the language and figures sufficiently clear for scientific review?**
**Yes.** Prose is dense but expert-register and readable; 0 overfull boxes; 24
main-text exhibits over 35 main-text pages; the algorithm listing and the two
flowcharts (base GSK vs DT-GSK) are present and paired. No presentation defect rises
to a desk concern from this seat's vantage (Stage 13 owns the exhibit-level audit).

**Q9. Is there an obvious ethics, integrity, plagiarism, duplicate-publication, or
citation-manipulation concern?**
**No misconduct concern; one disclosed structural concern requiring editorial
handling.** The conflicts-of-interest statement (`main.tex:288-297`) discloses that
A.W.M. originated baseline GSK and co-authored AGSK, APGSK, eGSK and ATMALS-GSK, and
that H.S.M.R. co-authored eGSK — i.e. **five of the six comparators were authored or
co-authored by two of the three present authors**, and the paper reports beating them.
This is fully and prominently disclosed (COI statement, cover letter, supplement
limitation seven), which is the correct handling. The residual is *editorial*, not
ethical: reviewer selection is constrained, and the cover letter's own note "Authors of
the GSK-family comparator papers should be avoided given the declared relationship"
lives in a **non-rendered LaTeX comment** (`cover_letter.tex:73-78`), so the editor
never sees that request. Citation hygiene is clean: 57-key closed corpus,
`allowed_citation_keys.txt` enforced, no `\nocite{*}`, no decorative self-citation
padding detected in the reference list. GenAI use is disclosed at both required
locations with the tool version pinned.
*Descoping note:* per §1.5.4(ii) the absence of external non-GSK baselines is **out of
scope for this cycle** and is not raised here as a requirement, fairness gap, or
rejection risk. The item above concerns authorship concentration and reviewer
selection only.

**Q10. Is the manuscript within journal length and file requirements?**
**No — the project's own binding budget is breached, and the gate evidence is stale.**
This is the single most concrete desk-level defect and is ticketed as **DS-01**. See
§1.2 below for the measurement.

**Q11. Does the paper appear benchmark-specific, incrementally engineered, or overly
promotional without a broader scientific insight?**
**Benchmark-bound: yes and disclosed. Incrementally engineered: partly. Promotional:
no.** All evidence is CEC-suite evidence; CEC2011 supplies real-world problem
*formulations*, and the manuscript is explicit that this is "breadth of application
formulation, not evidence of deployment performance" (`performance.tex:64-66`) — an
unusually honest qualifier. The incrementalism charge has teeth: strip the promotional
wording (there is none to strip) and what remains is a composite of modified
antecedents plus one deterministic endgame. The broader scientific insight the paper
offers is the **controlled negative result** on cheap accepted-move structure learning
— genuine, but explicitly *not* counted as a contribution (§10.9 narrowing; R-08).

**Q12. Does the paper explain why the contribution matters beyond reporting more wins?**
**Partly.** The stated answer is: a reproducible, release-locked instrument plus a
falsifiable negative result. That is a real answer and it is well argued in the
Conclusions. It is undercut in three places: (a) the **stated bounded gap** is the ISM
gap the paper reports it did *not* close (**DS-04**); (b) the paper never converts its
own strongest practical finding into a recommendation — the shipped configuration
retains a component its own evidence shows costs +30–57 % wall-clock for no measurable
return (**DS-08**); and (c) C3 is framed as "we did rigorous engineering" rather than
"we built the instrument that made the negative result credible", which is the version
of C3 that actually answers Q12 (see §2.5).

### 1.2 Length measurement (§10.14 evidence, recorded in the review record)

| Bound | Binding value | Measured now | Verdict |
|---|---|---|---|
| **B1** — typeset main-text pages incl. exhibits, excl. references and back matter; **hard cap 34** (`phase_04/page_budget.md` §2, marked "BINDING") | ≤ 34 | Main text (Sections 1–5) runs **pp. 1–35**; back-matter block begins p. 35 at y≈445; `References` heading on p. 37. Under the Phase-11 arithmetic (total − reference pages) B1 = 39 − 3 = **36**; under "last main-text page" B1 = **35**. | **BREACH** (either convention) |
| **B2** — main-text prose incl. abstract and caption prose, excl. references; **hard cap 12,000** | ≤ 12,000 | prose 11,985 + captions 1,078 + abstract 201 = **≈ 13,264** (tables, equations, algorithm and figure interiors excluded) | **BREACH ≈ +10.5 %** |
| MDPI advisory threshold (`journal_requirements.md` §2, SEARCH-DERIVED) | contact Editorial Office if > 12,000 words | ≈ 13,264 | **crossed**; no record of the advised prior contact |
| Last recorded gate page-count row | Phase 11, 2026-07-11: "35 pages total / B1 = 32 … ≤ 34 hard cap PASS, ~2 pp headroom" | current build is **39 pp** | **stale by 4 pp** |

No `change_request_register.csv` row raises the cap; the pre-registered §6 overflow
valve (F-TAXONOMY → T06 → one convergence grid → T03 → T-WORKED → F04-CEC2011) was
never invoked; and the Phase-12 register row (updated 2026-07-22) records **no**
page count, contrary to §10.14's requirement of a page-count row at the Phase 8/9/11
gates. Exhibit count is *within* plan (24 actual vs 25 planned), so the +4 pages are
prose growth (11,985 vs the 10,200-word plan, +17 %), not exhibit growth — which means
the valve, whose steps all migrate *exhibits*, would be the wrong instrument. The
correct remedies are a documented cap change or prose compression.

### 1.3 Mandatory ranked desk-rejection risk list

Ranked by expected editorial cost (probability × impact).

---

**R-01 — A main-text sentence misstates what the supplementary component study covers.**
- probability: **medium-high**
- impact: **high** — credibility. A reviewer who follows the pointer finds the
  supplement contradicting the main text in its own limitations subsection; that
  converts a well-run study into "the authors overstate their own evidence".
- supporting observation: `proposed_algorithm.tex:267` claims "The individual
  contribution of **each** scaffold subsystem is examined in a remove-one component
  study"; `supplementary.tex:1970-1971` states "ARGP, the final polish, and the
  deep-stall restart **are untested here**", and `supplementary.tex:1843-1848` names
  the same three as "prespecified exclusions from this matrix".
- what would reduce the risk: replace "each scaffold subsystem" with the enumerated
  set actually tested (ACE, NLPSR, BSE, linkage, coordinate local search, archive) and
  name the three exclusions in the same sentence.
- fixable without new research: **yes** (one sentence).

**R-02 — The paper's stated research question is answered "no", and the stated
"bounded gap" is the one it did not close.**
- probability: **medium**
- impact: **high** — this is the `INSUFFICIENT NOVELTY OR SIGNIFICANCE` pathway, and
  §10.13's first named hard rejection risk ("contribution framed as a bundle of
  modules without a clear scientific thesis").
- supporting observation: `introduction.tex:28-32` poses the paper's "single design
  question" in ISM terms; `:73-74` answers it "in the negative";
  `related_work.tex:299-302` states "The bounded gap is therefore: *within the GSK
  operator style, exploit the interaction structure of the moves the run has already
  accepted …*"; the very next sentence (`:303-307`) lists contributions from which ISM
  is absent; and `:308-309` promises "Whether this closes the gap is an empirical
  question, answered … in Section 4" — but Section 4 reports panel standing, and the
  gap-closure evidence is a null in Supplement §S6.5.
- what would reduce the risk: restate the bounded gap in the terms the contributions
  actually address (dimension-resolved control and a budget-exact deterministic
  endgame inside an unchanged GSK operator core), demote the ISM formulation to the
  secondary hypothesis the paper tests and reports negative, and redirect the
  "answered in Section 4" pointer so it does not promise gap-closure evidence the
  section does not carry.
- fixable without new research: **yes** (three sentences in §2.3 + two in §1).

**R-03 — Both binding length bounds are breached and the gate evidence is 4 pages stale.**
- probability: **medium** (MDPI publishes no hard cap; the exposure is the >12,000-word
  advisory and an internal compliance failure, not an automatic return)
- impact: **medium** — an administrative return costs a submission cycle; the missing
  §10.14 gate row is a governance defect an auditor would flag.
- supporting observation: §1.2 above — B1 = 35–36 vs cap 34; B2 ≈ 13,264 vs cap 12,000;
  last recorded gate row 35 pp/B1 = 32 (2026-07-11); no cap-raising change request.
- what would reduce the risk: either (a) a `change_request_register.csv` row raising
  B1/B2 with the compiled-PDF justification and a fresh page-count row in
  `phase_gate_register.csv`, or (b) prose compression (Section 3 carries 4,058 prose
  words and Section 4 carries 4,268; the pre-registered valve migrates exhibits and so
  does not address the actual overrun), plus contacting the Editorial Office as MDPI
  advises for >12,000-word submissions.
- fixable without new research: **yes**.

**R-04 — The one originality-bearing element of a headline contribution is never tested.**
- probability: **medium**
- impact: **medium-high** — Gate D exposure; a reviewer asks "what evidence supports the
  part you claim is new?" and the answer is none.
- supporting observation: `introduction.tex:110-112` — "we did not find ARGP's
  acceptance-rate-gated arm-freezing rule among the surveyed GSK variants" is the only
  positive originality claim inside C2 (NLPSR is "explicitly not claimed as new";
  ACE/BSE/archive/restart "modify cited antecedents"). ARGP appears in neither
  component study (`supplementary.tex:1843-1848`, `:1970-1971`; the overlay isolation
  roster at `:1982-1993` contains only ISM, the adaptive gate, and the final polish).
  The deep-stall restart, also named in C2, is likewise untested. Meanwhile the
  coordinate local search — Holm-significant at D=30 and the single largest degradation
  at D=50 and D=100 (`supplementary.tex:1942-1945`) — is claimed in **no** contribution
  bullet.
- what would reduce the risk: narrow C2 so ARGP and the restart are presented as
  specified design choices with their isolation left open, and state that explicitly;
  optionally name the coordinate local search among the scaffold's evidenced elements.
- fixable without new research: **yes** (the stronger fix, an ARGP ablation cell, is
  barred by the standing NO-rerun constraint; the wording fix is sufficient and honest).

**R-05 — Comparator-authorship concentration constrains reviewer selection.**
- probability: **medium**
- impact: **medium** — not a rejection reason on its own (it is disclosed), but it
  slows assignment and invites a "self-benchmarking" reading.
- supporting observation: `main.tex:288-297` (COI) and `supplementary.tex:1226-1228`:
  five of six comparators authored or co-authored by two of the present authors. The
  authors' own request to avoid comparator-paper authors as reviewers sits in a
  **non-rendered** LaTeX comment (`cover_letter.tex:73-78`) and therefore never reaches
  the editor.
- what would reduce the risk: enter the excluded-reviewer request in the submission
  system (where MDPI collects it) and add one rendered sentence to the cover letter
  noting the relationship's implication for reviewer selection.
- fixable without new research: **yes** (author-side, administrative).

**R-06 — The cover letter states the headline without the abstract's qualifiers.**
- probability: **medium**
- impact: **medium** — the desk editor's first impression is formed from a
  strictly-more-favorable framing than the manuscript's own.
- supporting observation: `cover_letter.tex:55` gives 2.48 with "eGSK second at 2.96"
  and omits (i) CEC2017 development-exposure, (ii) the D = 30 second place and the
  Holm-significant CEC2011 loss to eGSK, (iii) Nemenyi non-separability — all three
  present in the abstract (`main.tex:143-146`).
- what would reduce the risk: one sentence in the letter carrying the same three
  qualifiers.
- fixable without new research: **yes**.

**R-07 — The headline advantage is not statistically separable from the closest
comparator, and the headline suite is development-exposed.**
- probability: **medium**
- impact: **medium** — a reviewer may read "best overall rank" as unsupported.
- supporting observation: `conclusions.tex:46-50` — all four rank gaps to eGSK lie
  inside the Nemenyi critical difference of 1.67, and the head-to-head records at
  D ≥ 30 are losing (11-2-16, 13-0-16, 12-0-17); `supplementary.tex:1239-1243` —
  CEC2017 "is *development-exposed* … so its standing is a performance estimate on a
  tuned-against suite rather than an untouched confirmatory one", and it is also the
  source of the headline rank.
- what would reduce the risk: nothing further — this is already disclosed in the
  abstract, the results, the discussion and the supplement, which is best practice.
  The residual risk is a reviewer's judgement call about whether a non-separable rank
  advantage on a tuned-against suite is a sufficient headline. Carrying the same
  qualifiers into the cover letter (R-06) is the only available mitigation.
- fixable without new research: **not applicable** (no defect; disclosed risk).

**R-08 — The eGSK port qualification bounds the wrong quantity.**
- probability: **low-medium**
- impact: **medium-high** — §10.13 names "unfair eGSK provenance or solver comparison"
  a hard rejection risk, and eGSK is precisely the comparator that beats DT-GSK where
  it loses.
- supporting observation: `performance.tex:33-39` and `conclusions.tex:71-74` both
  close the port disclosure with "… so **no runtime-superiority claim** is made"; the
  substituted component is eGSK's late SQP polish, an optimization mechanism whose
  substitution changes *solution quality*, not only wall-clock.
  `supplementary.tex:1768-1771` records "no numerical-equivalence claim between the two
  backends" but again draws only the runtime consequence;
  `supplementary.tex:1196-1198` covers it obliquely ("deltas reflect algorithmic
  differences **up to the port** … asymmetries").
- what would reduce the risk: one sentence stating that the substitution's effect on
  eGSK's solution quality is unquantified and of unknown sign, so **both** DT-GSK's
  wins and its losses against eGSK carry that residual.
- fixable without new research: **yes**.

**R-09 — Presentation load (24 exhibits over 35 main-text pages) reads as data-dense.**
- probability: **low**
- impact: **low**
- supporting observation: 16 tables + 7 figures + 1 algorithm in the main text; the
  plan allowed 25 exhibits at ~13.3 pages (`page_budget.md` §4), so this is on-plan.
- what would reduce the risk: the same exhibit-migration valve invoked for R-03 would
  also reduce density, if the authors choose that route.
- fixable without new research: **yes**.

**R-10 — A visible author-side placeholder on page 1 (recorded, NOT ticketed).**
- probability: **high if submitted as-is**; **not applicable** under this review's scope
- impact: **medium** (an editor sees an unfinished manuscript on the title page)
- supporting observation: `DT-GSK.pdf` p. 1 renders
  "[H.S.M.R. institutional e-mail — to be added at submission]"; `main.tex:96-98`
  carries all-zero placeholder ORCIDs.
- what would reduce the risk: author supplies the values before upload.
- fixable without new research: yes.
- **Scope note:** §1.5.4(i) places the ORCID iDs and the corresponding-author
  institutional e-mail explicitly **out of scope** — "ignore it, raise no ticket, fail
  no gate". No ticket is raised and no gate is failed on this item; it is listed only
  so that this risk register is not silently incomplete.

### 1.4 EIC disposition

> **`EDITORIAL REVISION BEFORE REVIEW`**

Reasoning. There is no scientific blocker: the evidence lock holds, the package
verifies (15/15), the statistical protocol is preregistered and disclosed, the claim
vocabulary is clean, and the unfavorable results are stated in the abstract itself.
It is nevertheless not ready to leave the editor's desk, because two defects are text
that a reviewer would find in the first hour and that would cost the manuscript
credibility disproportionate to their size — **DS-02** (a main-text sentence that
misdescribes the supplement's coverage) and **DS-03** (a headline contribution whose
only claimed-original element has no test) — and because the manuscript exceeds the
project's own binding length budget with no updated gate measurement (**DS-01**). All
three are correctable without new experiments, new analysis, or any change to the
byte-locked optimizer core. `OUT OF SCOPE`, `INSUFFICIENT NOVELTY OR SIGNIFICANCE`,
`METHOD OR EVIDENCE NOT MATURE`, and `INTEGRITY OR COMPLIANCE HOLD` are all
inappropriate on the evidence reviewed; `ASSESSMENT BLOCKED` does not apply — every
input this seat required was present and readable.

**Gate B — Desk review: PASS (conditional).** No desk-rejection defect was found that
*cannot* be corrected through the planned revision, which is the gate's stated failure
criterion. The conditions are DS-01, DS-02 and DS-03.

---

## 2. Stage 4 — significance, originality, contribution boundary

### 2.1 Required assessment

| Dimension | Assessment |
|---|---|
| Importance of the research problem | **Adequate.** Budgeted black-box optimization is mature and well-populated; the paper's value proposition is rigour inside an existing family, which the field's own surveys ask for (`introduction.tex:21-26`). |
| Specificity and reality of the stated gap | **Specific but misaimed.** §2.3 states three concrete deficiencies (structure blindness; endgame refinement without determinism/budget safety; regime-limited adaptation evidence), each traced to named variants. The summary sentence then collapses "the bounded gap" to deficiency 1 only (`related_work.tex:299-302`) — the one the contributions do not address. **DS-04.** |
| Is the gap supported by the reviewed literature rather than asserted? | **Yes.** Every gap element is card-bound to a specific cited variant with a specific limitation (Table `tab:family-review`), and the survey scope is stated as bounded and reproducible, explicitly "not a state-of-the-art priority claim" (`related_work.tex:263-269`). This is better than typical. |
| Does the contribution address the gap directly? | **Deficiencies 2 and 3: yes** (C1 answers the endgame-determinism gap; C2 answers the regime-limited-adaptation gap). **Deficiency 1: reported negative.** The misalignment is presentational, not evidential — see DS-04. |
| Conceptual contribution | Resolving GSK's control *by dimension tier* rather than at one operating point is a genuine conceptual frame and is what the title claims. It is asserted and instantiated but never tested *as such*: no cell contrasts the tiered configuration against a non-tiered one. The per-dimension component results (ACE dominant at D=10; NLPSR/local search/BSE at D=30; nothing Holm-significant at D=100) are consistent with the frame but do not test it. |
| Theoretical contribution | **None claimed** — correctly. No convergence guarantee, no regret transfer ("ACE is not claimed to instantiate any specific bandit policy, and no regret guarantee transfers to the drifting rewards of an evolutionary run", `related_work.tex:196-200`). |
| Methodological contribution | The 13-substream, prefix-locked RNG rail is the real methodological artifact: it is what makes toggling one subsystem leave every other subsystem's draw order byte-identical (`proposed_algorithm.tex:710-717`), and therefore what makes the component isolations exact rather than approximate. Under-sold — see §2.5. |
| Empirical contribution | Substantial and honestly bounded: three suites, seven algorithms, one frozen configuration, pre-registered robustness variants, losses stated alongside wins. |
| Practical contribution | **Weakest axis.** The paper produces an actionable finding and does not state it: ISM costs +57.3 % (CEC2017 D50), +36.3 % (D100), +30.3 % (CEC2013 D50) wall-clock (`supplementary.tex:2039-2042`) for Δrank +0.05/+0.16/+0.20 at Holm p = 0.98/0.90/0.65 and A12 = 0.51/0.50/0.42. A grep for `recommend`/`practitioner`/`disable`/`turn off` over the manuscript and supplement returns **zero hits**. **DS-08.** |
| Reproducibility contribution | **Strongest axis in absolute terms.** Immutable release with per-file SHA-256, hash-frozen single configuration, byte-stability regression test, paired optimizer-independent seed schedule, released analysis pipeline, package manifest verifying 15/15. |
| Originality of each component | See §2.3 matrix. Honest labelling throughout; one positive originality claim (ARGP) and it is untested (**DS-03**). |
| Degree of incrementalism | **Moderate-to-high.** Six of the eight subsystems modify cited antecedents; the composition and the dimension-tiering are the integrative novelty. |
| Does a new acronym disguise a familiar mechanism? | **Partly, in one place.** "Eigenframe final polish" is a deterministic compass/pattern search (`kolda2003directsearch`) run once in a final budget slice, on an eigenbasis whose advantage over coordinate axes the paper concedes is unestablished; the supplement's `no_sgsm` row — polish on coordinate axes — is null, so "the significant effect is the compass endgame, not the learned basis specifically" (`supplementary.tex:2053-2056`). The manuscript states this plainly rather than hiding it (`proposed_algorithm.tex:571-604`), so this is a *naming* problem, not a concealment problem. ACE→"bandit-style", ARGP, BSE, NLPSR are all disclosed as renamed/modified antecedents. |
| Meaningful integration or a collection of modules? | **Integration, but the argument for it is under-made.** The strongest integration argument available — that the components are *tier-resolved*, each dominant at a different dimension, and that the frozen configuration serves all tiers without per-suite tuning — is present in fragments across §3.6, §4.1 and the supplement's per-dimension component reading, but never assembled into one paragraph that says "this is why the tiering is the contribution". Assembling it is the single highest-value revision available. |
| Does the combination create a new scientific insight? | **Yes, one, and it is a negative:** cheap accepted-move structure learning yields no detectable standalone benefit to a GSK optimizer at D ≤ 100 while costing 30–57 % wall-clock. This is a real, falsifiable, reproducible boundary result. It is correctly *not* claimed as a fourth contribution (R-08 closed). |
| Does the manuscript explain why the method should work? | **Partly.** Mechanism rationales are given per subsystem and traced to the cited weakness each answers (`introduction.tex:50-62`). What is missing is a mechanism-level account of *why dimension tiering specifically* is the right response — the titular claim. |
| Does the evidence test the contribution, or only the final system? | **Mixed.** C1: tested and Holm-significant (`supplementary.tex:1999-2023`, `:2042-2047`) — though the isolation removes the whole endgame. C2: three of six named elements tested (ACE, NLPSR, BSE) plus linkage and the archive; **ARGP and the deep-stall restart untested** (DS-03). C3: not testable in this sense, but it is *demonstrated* by the fact that the isolations are exact. The tiering itself: untested. |
| Do the implications matter outside the benchmark? | **Weakly, and this is honest.** CEC2011 supplies real-world *formulations*, explicitly not deployment evidence (`performance.tex:64-66`); the evidence ceiling is D = 100. The one implication that would travel — "do not pay 30–57 % for ISM" — is unstated (DS-08). |
| Fair comparison with the closest prior work? | **Yes on protocol, with two disclosed asymmetries whose consequences are mis-bounded:** the eGSK SLSQP-for-`fmincon` port (DS-06) and DT-GSK's self-initialization, the one optimizer of seven that does not start from the shared X₀ (DS-07). Both are disclosed; both have their material consequence stated in the wrong place or in the wrong terms. |

### 2.2 Contribution decomposition

**C1 — an eigenframe final polish**

| Field | Value |
|---|---|
| contribution_id | C1 |
| stated_contribution | "A one-shot, RNG-free deterministic compass search executed on the eigenbasis of the ISM signed interaction matrix in the final budget slice (coordinate axes when the graph carries no signal)" (`introduction.tex:87-100`) |
| category | **combined** (deterministic direct search + a learned basis), with an original *budget-accounting* property |
| closest_prior_work | `kolda2003directsearch` (compass/pattern search); `guo2015eig` (eigenvector-based crossover on population covariance); `jawad2024egsk` (late SQP escape) |
| exact_difference | One-shot rather than iterated; RNG-free and deterministic rather than randomized; every probe charged through the strict budget path so the phase is budget-exact; basis is a *cumulative, accepted-move, signed* graph rather than an instantaneous population covariance |
| scientific_value | **Real but narrower than the name implies.** The only added mechanism at D ≥ 50 with an isolated, statistically significant effect |
| implementation_evidence | `proposed_algorithm.tex:571-604`, Eq. `eq:eigen-polish`, architecture row 8 |
| empirical_or_theoretical_test | **Yes, supplement only:** Δrank +1.14/+0.98/+1.18, Holm p = 0.002/0.005/0.002, A12 = 0.59/0.53/0.64 (`supplementary.tex:2010-2020` table; finding at `:2042-2047`). No theoretical guarantee claimed |
| cost_or_tradeoff | Consumes final-slice budget that would otherwise fund population search; requires the ISM machinery to be running to supply the basis |
| scope_limit | D ≥ 50 only; the *learned basis* is unisolated — the null `no_sgsm` row shows coordinate axes perform equally |
| reviewer_risk | "You named it after the component your own data says is doing none of the work." §10.9 forbids the supporting result appearing in the main text, so a main-text-only reader sees C1 claimed with no visible evidence and an advertised adjacent null |
| verdict | **RETAIN — NARROW and RENAME.** Lead with the property the evidence supports (budget-exact deterministic endgame, as the abstract already does: "the budget-exact refinement"); demote "eigenframe" to a descriptor of the basis choice, whose advantage is explicitly open |

**C2 — a dimension-tiered adaptive scaffold**

| Field | Value |
|---|---|
| contribution_id | C2 |
| stated_contribution | ACE (EMA credit-based selector over complete operator settings) with ARGP pruning; tier-floored NLPSR; hard-capped BSE from a distance-filtered archive; deep-stall restart preserving the global best (`introduction.tex:101-112`) |
| category | **adapted / combined**, with one element claimed **original_within_reviewed_scope** (ARGP) |
| closest_prior_work | `fialho2010adaptive`, `auer2002finite` (adaptive operator selection); `apgsk2021` (NLPSR — explicitly not claimed as new); `zhang2009jade`, `tanabe2013shade` (archive/escape lineage); multi-start restart (classical) |
| exact_difference | Tier-resolved activation from one frozen configuration; ARGP's acceptance-rate-gated, recoverable arm-freezing to a probability floor |
| scientific_value | Moderate. The *tiering* is the integrative idea; the parts are honestly labelled as modified antecedents |
| implementation_evidence | Architecture Table 4 rows 1, 2, 6; Eqs. `eq:ace-update`, `eq:nlpsr`, `eq:bse-cauchy`; frozen parameter table |
| empirical_or_theoretical_test | **Partial.** ACE (Holm-significant at D=10), NLPSR (at D=30), BSE (at D=30), linkage and archive (rank-neutral/sign-mixed) tested — `supplementary.tex:1928-1953`. **ARGP: no test anywhere. Deep-stall restart: no test anywhere** (`supplementary.tex:1843-1848`, `:1970-1971`). The tiering itself: no contrast |
| cost_or_tradeoff | Bookkeeping overhead (D=100 per-run 41.59 s); no additional objective evaluations |
| scope_limit | CEC2017 only for the component evidence; conditional (remove-one) deltas, ISM-off, non-additive, never averaged across dimensions |
| reviewer_risk | "The only part you claim is new is the only part you never tested" |
| verdict | **RETAIN — NARROW.** State explicitly that ARGP and the deep-stall restart are specified but not isolated; consider naming the coordinate local search, which carries measured effect and is currently claimed nowhere |

**C3 — a controlled, reproducible family evaluation**

| Field | Value |
|---|---|
| contribution_id | C3 |
| stated_contribution | 13-substream append-only prefix-locked RNG layer; paired optimizer-independent seeds; one checksum-verified configuration; a versioned immutable evidence release binding every reported number (`introduction.tex:113-132`) |
| category | **adapted** (each ingredient is established practice; the *composition and enforcement level* is unusual) |
| closest_prior_work | General reproducibility practice in evolutionary computation; no specific antecedent claimed or required |
| exact_difference | Enforcement: substream isolation means toggling one subsystem cannot disturb any other subsystem's draw order, so component re-evaluation is *exact* rather than approximate; a strict-source analysis pipeline that can read only the promoted release |
| scientific_value | **As stated: low** (a skeptical reviewer classifies this as competent method reporting). **As it should be stated: moderate** — it is the instrument that makes the negative result falsifiable rather than anecdotal |
| implementation_evidence | `proposed_algorithm.tex:705-720`; supplement §S5 (seed schedule, freeze manifest, release checksums); `check_manifest` 15/15 |
| empirical_or_theoretical_test | Not applicable; *demonstrated* by the exactness of the S6 isolations |
| cost_or_tradeoff | Byte-identical reproduction at D ≥ 50 requires single-threaded kernels, capping parallel speed-up exactly where per-run cost is largest (`supplementary.tex:1218-1224`) |
| scope_limit | One host, one environment, no second-environment verification cell |
| reviewer_risk | "Reproducibility is a requirement, not a contribution" |
| verdict | **RETAIN — REFRAME (do not remove).** Re-anchor C3 on what it bought: the instrument that produced a credible, falsifiable component-level negative result. This simultaneously repairs DS-04 |

**Not a contribution (correctly): ISM.** Verified consistent across every high-visibility
surface — abstract "The contributions are the dimension-tiered adaptive control, the
budget-exact refinement, and a reproducible within-family evaluation"
(`main.tex:146-151`); introduction "the paper's principal contributions remain … (C2),
… (C1), and … (C3)" (`introduction.tex:135`); conclusions "rather than as a fourth
claimed contribution" (`conclusions.tex:101-102`); cover letter "The paper makes three
contributions … A supporting mechanism — the interaction-structure memory"
(`cover_letter.tex:55`). **R-08 is correctly and completely closed.**

### 2.3 Novelty-and-significance matrix

| Element | Novelty within reviewed corpus | Evidence of benefit | Cost | Net significance |
|---|---|---|---|---|
| Dimension tiering (titular) | Moderate — the integrative idea | **Untested as such**; consistent with per-dimension component pattern | none beyond bookkeeping | Moderate, asserted |
| Deterministic budget-exact endgame (C1) | Moderate-low (compass search is classical; the budget-exactness and RNG-freedom are the differentiators) | **Holm-significant**, three cells (supplement) | final-slice budget | **Highest of the claimed set** |
| Learned eigenbasis for that endgame | Moderate (accepted-move signed graph vs population covariance) | **None** — `no_sgsm` (coordinate axes) is null | part of ISM's +30–57 % | ~Zero, and the paper says so |
| ACE credit-based selector | Low (adaptive operator selection, renamed) | Holm-significant at D=10 | bookkeeping | Moderate |
| ARGP arm-freezing | **The only positive originality claim** | **None — untested** | unmeasured | **Unresolved** |
| NLPSR (tier-floored) | Explicitly none claimed | Holm-significant at D=30 | none | Moderate (inherited) |
| BSE + diversity archive | Low (JADE/SHADE lineage) | BSE Holm-significant at D=30; archive sign-mixed | bookkeeping | Low-moderate |
| Deep-stall restart | Low (multi-start) | **None — untested** | resampling budget | Unresolved |
| Coordinate local search | Not claimed | Holm-significant at D=30; largest degradation at D=50/D=100 | charged evaluations | **Under-claimed** |
| Linkage-aware block crossover | Moderate | Rank-neutral / sign-mixed; removing it slightly **improves** D=100 (`supplementary.tex:1948-1949`) | ISM-dependent at D ≥ 50 | ~Zero |
| ISM (supporting mechanism) | Moderate-high as a *design* | **Null** (Δrank +0.05/+0.16/+0.20; Holm p 0.98/0.90/0.65) | **+57.3 % / +36.3 % / +30.3 %** | **Negative on cost-benefit; positive as a reported boundary result** |
| Evaluation-integrity layer (C3) | Low as novelty; high as enablement | Demonstrated by exact isolations | single-thread constraint at D ≥ 50 | Moderate |

### 2.4 Q1- and Q2-level questions

**Q1-level.**
- *Likely to change understanding, practice, or methodology?* — **No for the algorithm;
  marginally yes for the negative result.** The ISM boundary result should discourage a
  specific, otherwise-attractive design direction, which has real (if modest) value.
- *More than a small performance increment?* — **No.** The advantage over the closest
  comparator is never Nemenyi-separable, and the head-to-head records against eGSK at
  D ≥ 30 are losing.
- *Defensible mechanism, theory, analytical insight, or reproducible empirical finding?*
  — **Yes, the last one**, at an unusually high standard.
- *Evidence broad and deep enough for the claimed importance?* — **Yes**, because the
  claimed importance is modest and correctly bounded.
- *Would a skeptical expert still see a contribution with all promotional wording
  removed?* — **Yes, a reduced one.** There is no promotional wording to remove; what
  remains is a well-instrumented composite algorithm, one Holm-significant deterministic
  endgame, and a credible negative result.

**Verdict: not Q1-level on contribution merit** — not because anything is wrong, but
because the strongest measured effect belongs to a mechanism close to classical direct
search, the closest comparator is statistically inseparable, and the headline suite is
development-exposed.

**Q2-level.**
- *Technically sound and meaningfully useful?* — **Yes.**
- *Incremental contribution clearly specified and sufficiently validated?* — **Specified:
  yes, exceptionally.** **Validated: yes except ARGP and the deep-stall restart**
  (DS-03).
- *Scope and limitations honest?* — **Yes**, with three placement defects (DS-05, DS-06,
  DS-07) rather than honesty defects.

**Verdict: Q2-ready (MDPI *Algorithms*) after the DS-01…DS-08 text corrections.** No
new experiment, no new analysis, and no change to the byte-locked optimizer core is
required by any finding in this report.

**Gate D — Contribution merit: PASS (conditional on DS-03 and DS-04).** The central
contribution is neither unsupported nor materially indistinguishable from prior work,
and the article type is appropriate — no journal or article-type change is indicated.
The conditions are the C2 narrowing and the gap/contribution realignment.

### 2.5 Strongest and weakest contribution statements

**Strongest defensible contribution statement (the ceiling this evidence supports):**

> Within the seven-algorithm GSK-family panel, under one hash-frozen configuration and
> a budget-fair, release-locked paired protocol, resolving GSK's control by dimension
> tier and closing the run with a deterministic, budget-exact endgame attains the best
> descriptive across-dimension Friedman rank aggregate on two of three suites — without
> ever becoming Nemenyi-separable from the strongest comparator — and the byte-stable
> determinism layer makes per-component re-evaluation exact enough to return a
> falsifiable negative result: learning coordinate-pair structure from accepted moves at
> no extra objective evaluations yields no detectable standalone benefit to a GSK
> optimizer at D ≤ 100.

**Weakest contribution statement (what a hostile reviewer will write):**

> After the interaction-structure memory is correctly demoted out of the contribution
> set, C2 reduces to a composite of explicitly-inherited mechanisms plus one rule (ARGP)
> that the paper claims is new and never tests; C1 reduces to a compass search in the
> final budget slice, whose distinguishing feature — the learned basis — the authors
> concede is unisolated and whose null coordinate-axes control they report themselves;
> and C3 claims reproducibility infrastructure as a scientific contribution. The stated
> "bounded gap" is the one the paper reports it did not close.

Both statements are supportable from the same evidence. The gap between them is
almost entirely **framing**, which is why the recommended remedies are all text-level.

### 2.6 Per-bullet recommendation

| Bullet | Recommendation | Required action |
|---|---|---|
| **C1** | **RETAIN — NARROW + RENAME** | Lead on "budget-exact, RNG-free deterministic endgame" (the abstract's own phrasing); demote "eigenframe" to the basis descriptor; keep the existing concession that the learned basis is unisolated |
| **C2** | **RETAIN — NARROW** | State that ARGP and the deep-stall restart are specified but not isolated; consider naming the coordinate local search among the evidenced scaffold elements |
| **C3** | **RETAIN — REFRAME** | Re-anchor on enablement: the instrument that makes component re-evaluation exact and the negative result falsifiable |
| *(ISM)* | **KEEP OUT of the contribution set** | No change — verified correct on all four high-visibility surfaces |
| *(new)* | **DO NOT ADD a fourth bullet for the negative result** | §10.9/§10.13 and R-08; the current placement (abstract sentence + introduction paragraph + conclusions paragraph) is correct |

---

## 3. Tickets (§5.4 schema)

### DS-01

```text
ticket_id: DS-01
review_stage: Stage 2 (EIC desk screening)
reviewer_role: EIC / ECB
severity: Major
priority: P1
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/DT-GSK.pdf (whole); papers/build_prompt_phases/phase_04/page_budget.md Sec.2; papers/governance/phase_gate_register.csv rows 8/11/12
claim_id_or_artifact_id: Section 10.14 page-limit hard rule; budget bounds B1/B2
concise_issue: Both binding length bounds are breached and no page-count row exists for the current build.
exact_evidence_or_observation: DT-GSK.pdf = 39 pp (PyMuPDF). Main text (Sections 1-5) ends on p.35 (back-matter block "Supplementary Materials:" begins p.35 y=445; References heading p.37 y=356). B1 = 36 under the Phase-11 arithmetic (total minus 3 reference pages) or 35 under "last main-text page"; hard cap is 34 ("BINDING", page_budget.md Sec.2). B2 measured = prose 11,985 + captions 1,078 + abstract 201 = 13,264 words vs hard cap 12,000, and above MDPI's own >12,000-word "contact the Editorial Office" threshold (journal_requirements.md Sec.2). Last recorded gate page count: phase_gate_register.csv Phase 11 (2026-07-11) "35 pages total / B1=32 ... <=34 hard cap PASS"; the Phase-12 row (updated 2026-07-22) records no page count. No change_request_register.csv row raises the cap; the Sec.6 overflow valve was never invoked.
root_cause: Prose grew ~17% over plan (10,200 -> 11,985 words) across the 2026-07-16..07-22 remediation cycles while the measurement obligation stayed attached to Phases 8/9/11, which last ran on 2026-07-11.
scientific_or_editorial_justification: Section 10.14 requires the compiled-PDF page count at the Phase 8/9/11 gates with a register row for each, and requires overflow to be resolved only by supplement migration. Neither happened.
impact_on_validity_or_acceptance: No effect on validity. Editorial: MDPI publishes no hard cap, so the exposure is the crossed >12,000-word advisory (which asks for prior contact with the Editorial Office) plus an internal compliance failure that an auditor would flag.
required_correction: Either (a) file a change_request_register.csv row raising B1/B2 with justification and record a fresh page-count row in phase_gate_register.csv, or (b) compress prose (Sections 3 and 4 carry 4,058 and 4,268 prose words) and re-measure. Note the pre-registered valve migrates exhibits and therefore does not address a prose overrun. Either way, contact the Editorial Office as MDPI advises for >12,000-word submissions.
acceptable_alternatives: Migrate two exhibits per the valve to buy ~1 page (helps B1 only, not B2).
additional_evidence_needed: None.
dependencies: Any accepted text edit from DS-02..DS-08 changes the measurement; re-measure last.
expected_improvement: Restores Section 10.14 compliance and removes an administrative-return pathway.
post_revision_verification: Recompile; record B1, B2 and total pages in phase_gate_register.csv; confirm B1 <= the then-current cap and B2 <= 12,000 (or the documented raised cap).
status: open
```

### DS-02

```text
ticket_id: DS-02
review_stage: Stage 4 (contribution boundary) / Stage 2
reviewer_role: R1 / T1-OPT
severity: Major
priority: P1
confidence: Confirmed
issue_type: claim-scope
manuscript_location: papers/sections/proposed_algorithm.tex:267-269 (rendered DT-GSK.pdf Sec. 3.3)
claim_id_or_artifact_id: supplement coverage claim for X-ABL-01
concise_issue: The main text claims the remove-one study examines EACH scaffold subsystem; the supplement states three are untested.
exact_evidence_or_observation: proposed_algorithm.tex:267 -- "The individual contribution of each scaffold subsystem is examined in a remove-one component study in the Supplementary Materials". supplementary.tex:1970-1971 -- "ARGP, the final polish, and the deep-stall restart are untested here." supplementary.tex:1843-1848 -- "Three further frozen flags are prespecified exclusions from this matrix --- the ARGP pool-pruning control, the ISM-dependent final polish ..., and the deep-stall restart ... --- and no contribution of any sign is claimed for those three from this scaffold matrix." The main-text sentence immediately before (proposed_algorithm.tex:263-266) names ARGP and the deep-stall restart among the sub-mechanisms, so the coverage claim is contradicted for two of the six it has just named.
root_cause: The sentence predates the ablation-design exclusions and was not re-scoped when the prespecified exclusion list was fixed.
scientific_or_editorial_justification: Section 5.5 calibrates exactly this pattern -- a main-text cross-reference to supplementary coverage the supplement does not contain -- as Major, and Section 4.6 forbids language that overstates what the evidence covers.
impact_on_validity_or_acceptance: No number changes. Credibility: a reviewer following the pointer finds the supplement contradicting the main text in its own limitations subsection.
required_correction: Replace "each scaffold subsystem" with the tested set (ACE, NLPSR, BSE, the linkage-aware block crossover, the coordinate local search, and the diversity archive) and name the three exclusions in the same sentence. Result-free; states no outcome, so Section 10.9 is unaffected.
acceptable_alternatives: "a remove-one component study covering six of the scaffold's mechanisms (ARGP, the final polish and the deep-stall restart are outside its matrix)".
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Removes a confirmed main<->supplement contradiction; restores Gate C/J consistency for this cross-reference.
post_revision_verification: Re-read the rendered PDF sentence against supplementary.tex:1843-1848 and :1970-1971; confirm the enumerations agree exactly and that no outcome word entered the main text.
status: open
```

### DS-03

```text
ticket_id: DS-03
review_stage: Stage 4
reviewer_role: R1 / T1-OPT
severity: Major
priority: P1
confidence: Confirmed
issue_type: evidence
manuscript_location: papers/sections/introduction.tex:101-112 (contribution bullet C2)
claim_id_or_artifact_id: C2; MT-02/MT-03/MT-04/MT-06/MT-07
concise_issue: C2's only originality-bearing element (ARGP) -- and the deep-stall restart it also names -- have no empirical or theoretical test anywhere in the package.
exact_evidence_or_observation: introduction.tex:110-112 -- "ACE, NLPSR, BSE, the archive, and the restart modify cited antecedents; we did not find ARGP's acceptance-rate-gated arm-freezing rule among the surveyed GSK variants" (the sole positive originality claim in C2; NLPSR is separately "explicitly not claimed as new"). Neither component study tests it: supplementary.tex:1843-1848 (prespecified exclusions), :1970-1971 (untested here), and the overlay isolation roster at :1982-1993 contains only ISM, the adaptive confidence gate, and the final polish. The deep-stall restart is in the same exclusion list. Conversely the coordinate local search -- Holm-significant at D=30 and the largest degradation at D=50 and D=100 (supplementary.tex:1942-1945) -- is claimed in no contribution bullet.
root_cause: The contribution set was written from the design inventory; the ablation matrix was scoped by toggle-isolation feasibility (ARGP's arm-freezing overlaps ACE; the restart overlaps BSE). The two were never reconciled.
scientific_or_editorial_justification: Stage 4 requires that the evidence test the contribution and not only the final system. A novelty claim with no isolation, no theory, and no measured effect is unsupported at the bullet level even when the whole-system results are sound.
impact_on_validity_or_acceptance: Gate D exposure. A reviewer's first question about C2 -- "what supports the part you say is new?" -- currently has no answer.
required_correction: Narrow C2 so ARGP and the deep-stall restart are presented as specified design elements whose individual isolation is left open, and say so explicitly in the bullet. Optionally add the coordinate local search to the scaffold elements C2 names, since it carries measured effect and is currently claimed nowhere.
acceptable_alternatives: An ARGP remove-one cell would be the stronger fix, but it is barred by the standing NO-rerun / NO-new-release constraint; the wording narrowing is sufficient and honest.
additional_evidence_needed: None under the standing constraints.
dependencies: Interacts with DS-02 (same paragraph) and DS-04 (contribution framing).
expected_improvement: Aligns the claimed originality with the tested set; removes the sharpest available Gate-D objection.
post_revision_verification: Re-read C2 and confirm every element is either (a) labelled as modifying a cited antecedent, (b) supported by a named component result, or (c) explicitly marked specified-but-not-isolated.
status: open
```

### DS-04

```text
ticket_id: DS-04
review_stage: Stage 4 / Stage 2
reviewer_role: R1 / EIC
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: claim-scope
manuscript_location: papers/sections/related_work.tex:299-309; papers/sections/introduction.tex:28-32, :73-74
claim_id_or_artifact_id: BG-03; phase_04/thesis.md Sec.2 bounded-gap statement
concise_issue: The paper's stated "bounded gap" and its stated single design question are both ISM-shaped -- i.e. exactly the thing it reports it did not achieve -- while its three contributions address two different deficiencies.
exact_evidence_or_observation: related_work.tex:299-302 -- "The bounded gap is therefore: within the GSK operator style, exploit the interaction structure of the moves the run has already accepted, at high dimension, without spending any additional objective evaluations and without replacing the base operator." The next sentence (:303-307) lists the contributions: scaffold, deterministic polish, controlled evaluation -- ISM appears only as "a supporting mechanism". :308-309 then promises "Whether this closes the gap is an empirical question, answered within the seven-algorithm GSK-family panel in Section 4", but Section 4 reports panel standing; the gap-closure evidence is the Supplement S6.5 null. introduction.tex:28-32 poses the "single design question" in the same ISM terms and :73-74 answers it "in the negative". Section 2.3 does state three deficiencies, two of which C1 and C2 do address -- but the summary sentence collapses "the gap" to the first one only.
root_cause: Residue of the pre-demotion narrative: the gap statement was written when ISM was the headline contribution and was not re-aimed when the C1-C3 restructure demoted it.
scientific_or_editorial_justification: Stage 4 requires that the contribution address the stated gap directly, and Section 10.13's first hard rejection risk is a contribution framed as a bundle of modules without a clear scientific thesis. As written, an editor can read the paper as answering its own research question "no" and then claiming three unrelated things.
impact_on_validity_or_acceptance: No effect on any number. Significant effect on how the paper reads at the desk and on Gate D.
required_correction: Restate the bounded gap in the terms C1-C3 address (dimension-resolved control and a budget-exact deterministic endgame inside an unchanged GSK operator core); present the accepted-move-structure question as the secondary hypothesis the paper tests and reports negative; and redirect the "answered in Section 4" pointer so it does not promise gap-closure evidence Section 4 does not carry.
acceptable_alternatives: Keep the ISM-shaped question as the framing device but state immediately that the paper's contributions are the scaffold, the endgame and the evaluation, and that the structure question is reported as a bounded negative.
additional_evidence_needed: None.
dependencies: Pairs naturally with the C3 reframing in Section 2.5 of this report.
expected_improvement: Converts the strongest available "no clear thesis" objection into a coherent one-sentence thesis.
post_revision_verification: Read Sections 1 and 2.3 end-to-end and confirm the stated gap, the stated question, and the contribution bullets name the same objects.
status: open
```

### DS-05

```text
ticket_id: DS-05
review_stage: Stage 2
reviewer_role: EIC
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: claim-scope
manuscript_location: papers/cover_letter.tex:55 (rendered cover_letter.pdf p.1)
claim_id_or_artifact_id: RS-01 NARROWED; RS-10; negative_findings.md items 2-4
concise_issue: The cover letter states the headline rank without the three qualifiers the abstract carries.
exact_evidence_or_observation: cover_letter.tex:55 gives "the best overall CEC2017 Friedman mean rank ... (2.48, the unweighted mean of the four per-dimension ranks --- a descriptive aggregate; eGSK is second at 2.96), evaluated under a release-locked protocol". It omits (i) that CEC2017 was configuration-selection exposed, (ii) the D=30 second place and the Holm-significant CEC2011 loss to eGSK, (iii) that DT-GSK and eGSK are never Nemenyi-separable. All three are in the abstract (main.tex:143-146). The letter does disclose the ISM null, the panel bound, and the COI.
root_cause: The letter was written to the accepted claim set (CL-02) before the abstract's loss-disclosure pass and was not re-synchronised.
scientific_or_editorial_justification: Section 10.7's loss-visibility parity requires unfavorable cells material to a headline to be stated alongside it; Section 10.9 names the cover letter a governed surface. The manuscript already meets this standard -- the letter should not fall below it.
impact_on_validity_or_acceptance: The desk editor's first impression is formed from a strictly more favorable framing than the manuscript's own.
required_correction: Add one sentence carrying the same three qualifiers, in the letter's existing register.
acceptable_alternatives: Reuse the abstract's own two sentences verbatim.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Restores cover-letter/abstract disclosure parity.
post_revision_verification: Diff the letter's claim sentence against main.tex:138-152; confirm all three qualifiers are present in the rendered PDF.
status: open
```

### DS-06

```text
ticket_id: DS-06
review_stage: Stage 4
reviewer_role: R1 / T1-OPT
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: experimental-design
manuscript_location: papers/sections/performance.tex:33-39; papers/sections/conclusions.tex:71-74; papers/supplementary.tex:1202-1206, :1768-1771
claim_id_or_artifact_id: LM-04
concise_issue: The eGSK solver-port disclosure bounds runtime comparability but never states the consequence for solution quality.
exact_evidence_or_observation: performance.tex:33-39 -- "the eGSK panel cells derive from the committed reference results of the runnable eGSK port, whose late local polish uses SciPy-SLSQP, whereas the original reference implementation uses a fmincon-based SQP solver; cross-implementation runtime and environment comparability is therefore limited, and no runtime-superiority claim is made anywhere in this paper." conclusions.tex:71-74 repeats the same "so no runtime-superiority claim is made in either direction". supplementary.tex:1768-1771 adds "with no numerical-equivalence claim between the two backends" but again draws only the runtime consequence. The substituted component is eGSK's late SQP escape -- an optimization mechanism -- so the substitution's first-order effect is on eGSK's achieved solution quality. eGSK is the comparator that beats DT-GSK at CEC2017 D=30 and Holm-significantly on CEC2011, so the residual is material in both directions.
root_cause: The disclosure was drafted around the runtime table (LM-04) and inherited that scope when the table was later reduced to DT-GSK-only.
scientific_or_editorial_justification: Section 10.13 names "unfair eGSK provenance or solver comparison" a hard rejection risk; Section 4.6 forbids suppressing uncertainty about a comparison. Partial coverage exists (supplementary.tex:1196-1198 "up to the port ... asymmetries"; introduction.tex:126-132 "subject to those disclosed exceptions"), which is why this is Moderate and not Major.
impact_on_validity_or_acceptance: No number changes. A reviewer who notices that the closest comparator is a port with a substituted optimizer, and that the only stated consequence concerns wall-clock, will question the fairness framing.
required_correction: Add one sentence stating that the substitution's effect on eGSK's achieved solution quality is unquantified and of unknown sign, so both DT-GSK's wins and its losses against eGSK carry that residual.
acceptable_alternatives: Fold the sentence into the Conclusions limitations outline and the Section 4.1 provenance paragraph.
additional_evidence_needed: None (a numerical-equivalence study would require a MATLAB fmincon run and is barred by the NO-rerun constraint; the correction is a disclosure-scope fix, not a new experiment).
dependencies: None.
expected_improvement: Closes the fairness gap at the disclosure level and pre-empts the Section 10.13 objection.
post_revision_verification: Confirm the quality-side consequence appears in the main text (not only the supplement) and that no new comparative claim was introduced.
status: open
```

### DS-07

```text
ticket_id: DS-07
review_stage: Stage 4 / Stage 2
reviewer_role: R1 / EIC
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: claim-scope
manuscript_location: papers/sections/conclusions.tex:65-81 (headed Limitations outline)
claim_id_or_artifact_id: PR-06; LM-03
concise_issue: The main-text limitations outline omits the self-initialization asymmetry -- the one disclosed confound the supplement calls unbounded and worst at a headline-contributing tier.
exact_evidence_or_observation: performance.tex:117-124 discloses the mechanism: "DT-GSK is the one documented exception --- it self-initializes its own 5*D population ... Pairing is therefore by common seed/problem/run rather than by an identical starting population for DT-GSK." supplementary.tex:1231-1236 characterises it: "a disclosed fairness asymmetry that is not separately bounded and is most consequential at low dimension, where DT-GSK runs essentially the scaffold." The Conclusions limitations outline (conclusions.tex:65-81) lists eight items -- mid-dimension tier, D>=50 gating, panel-relative scope, the eGSK port, the D=100 ceiling, single host, comparator authorship, three attribution gaps, statistical scope -- and does not include it. D=10 (rank 2.88, first place) is one of the four cells averaged into the headline 2.48.
root_cause: The limitations outline was assembled from LM-01..LM-05; the self-init exception lives under PR-06 (protocol) and was never promoted into the limitations summary.
scientific_or_editorial_justification: Section 10.7's loss-visibility parity requires unfavorable material bearing on a headline to be stated alongside it; the outline explicitly claims to summarise the eleven limitations stated in full in S5, and this is one of them.
impact_on_validity_or_acceptance: The main-text-only reader gets the fact (Section 4.1) but not the two qualifiers that make it material.
required_correction: Add the item to the Conclusions limitations outline with both qualifiers ("not separately bounded"; "most consequential at low dimension").
acceptable_alternatives: Add the two qualifiers to the Section 4.1 paragraph instead, and cross-reference from the outline.
additional_evidence_needed: None.
dependencies: None; adds ~25 words, interacts with DS-01.
expected_improvement: Restores main<->supplement limitation parity on the one confound that touches the headline aggregate.
post_revision_verification: Check that the Conclusions outline enumerates the same limitation set as supplement S5.
status: open
```

### DS-08

```text
ticket_id: DS-08
review_stage: Stage 4
reviewer_role: R1 / T1-OPT
severity: Moderate
priority: P3
confidence: Confirmed
issue_type: claim-scope
manuscript_location: papers/supplementary.tex:2036-2060 (S6.5 discussion); absent from the whole package
claim_id_or_artifact_id: X-ABL-02; AN-COST
concise_issue: The package never states the practical recommendation its own evidence supports, and the shipped frozen configuration retains a component measured to cost 30-57% wall-clock for no measurable return.
exact_evidence_or_observation: supplementary.tex:2036-2042 -- ISM Delta-rank +0.05 (CEC2017 D50), +0.16 (D100), +0.20 (CEC2013 D50); Holm p = 0.98 / 0.90 / 0.65; A12 = 0.51 / 0.50 / 0.42; wall-time cost +57.3% / +36.3% / +30.3%, "so it costs a third to well over half again in wall-clock and buys no measurable accuracy return". Its two active channels are both unsupported: the polish eigenbasis (the no_sgsm row, polish on coordinate axes, is null -- ":2053-2056: the significant effect is the compass endgame, not the learned basis specifically") and the linkage blocks (":1948-1949: removing the linkage slightly improves rank at D=100"). A grep for recommend / practitioner / disable / turn off / switch off / default off across papers/supplementary.tex and papers/sections/*.tex returns zero hits.
root_cause: The isolation was designed to answer an attribution question; the operational consequence was never drawn.
scientific_or_editorial_justification: Stage 4 asks whether the practical implications matter outside the selected benchmark. Here they do, and the paper leaves the one transferable statement unmade. A reader who does deploy DT-GSK at D>=50 will pay the overhead by default.
impact_on_validity_or_acceptance: No number changes. It is the difference between a negative result that is merely reported and one that is useful.
required_correction: Add a one- or two-sentence operational note in Supplement S6.5, where the evidence lives: at D >= 50 the interaction-structure memory may be disabled for a 30-57% wall-clock saving with no measured accuracy cost at the tested dimensions, and this is the configuration a practitioner should prefer absent evidence at larger scales.
acceptable_alternatives: None in the main text -- placing a derived component recommendation there would re-enter Section 10.9 territory. Keep it supplement-side.
additional_evidence_needed: None.
dependencies: Must not alter the frozen configuration or any primary number; the algorithm core is byte-locked and no rerun is permitted, so this is text only.
expected_improvement: Converts a reported null into an actionable finding and strengthens the answer to "why does this matter beyond more wins".
post_revision_verification: Confirm the note is supplement-only, states no new comparative result, and changes no primary claim; re-run the main-text ablation-leak scan.
status: open
```

### DS-09

```text
ticket_id: DS-09
review_stage: Stage 2
reviewer_role: EIC
severity: Minor
priority: P2
confidence: Confirmed
issue_type: production
manuscript_location: papers/main.tex:127-153 (abstract); rendered DT-GSK.pdf p.1
claim_id_or_artifact_id: n/a
concise_issue: The rendered abstract is 201 words against the build's own <=200-word rule, and no validator enforces the rule.
exact_evidence_or_observation: main.tex:123 comment -- "Abstract (<=200 words; no citations; one headline result number ...)". PyMuPDF extraction of the rendered abstract between "Abstract:" and "Keywords:" yields 201 whitespace-delimited tokens. The Phase-8 gate recorded "abstract EXACTLY 200 words"; the count has since drifted. No abstract word-count check exists anywhere in papers/scripts/ (grep for abstract_word / word_count returns nothing).
root_cause: Post-Phase-8 abstract edits (oracle-sentence removal, bounded-null advert, contribution restatement) with no enforcing validator.
scientific_or_editorial_justification: MDPI limits the abstract to about 200 words; the project bound itself to <=200. Tokenization is convention-dependent (the two inline "D = 50"/"D = 30" render as three tokens each), so the true overrun may be zero under a different counting rule -- hence Minor, not Moderate.
impact_on_validity_or_acceptance: Negligible scientifically; a trivial submission-form rejection risk if the system enforces 200.
required_correction: Remove one word (or confirm the journal's counting rule).
acceptable_alternatives: Add a word-count assertion to the build validators so the rule is enforced rather than commented.
additional_evidence_needed: The journal's exact abstract-length rule, from the live instructions page (currently verified_online=false).
dependencies: DS-01 re-measurement.
expected_improvement: Removes a mechanical submission-form failure mode.
post_revision_verification: Re-extract the rendered abstract and count.
status: open
```

### DS-10

```text
ticket_id: DS-10
review_stage: Stage 2
reviewer_role: EIC
severity: Editorial
priority: P3
confidence: Confirmed
issue_type: writing
manuscript_location: papers/cover_letter.tex:55 (first substantive sentence)
claim_id_or_artifact_id: residual of M-034 (superseded "first GSK-family variant" priority claim)
concise_issue: "To our knowledge" attaches a priority hedge to a fact the authors measured themselves.
exact_evidence_or_observation: cover_letter.tex:55 -- "To our knowledge, DT-GSK attains the best overall CEC2017 Friedman mean rank on the seven-algorithm GSK-family panel (2.48 ...)". The rank is a computed property of the authors' own panel, not a literature-priority statement; "to our knowledge" implies a priority search over the wider literature that Section 10.2 and Section 10.5 forbid being claimed. M-034 closed the explicit "first GSK-family variant" priority claim as superseded; this reads as its residue.
root_cause: Leftover hedge from the pre-M-034 letter.
scientific_or_editorial_justification: Section 4.6 and Section 10.5: no wording may imply a field-wide or priority statement from a same-family panel.
impact_on_validity_or_acceptance: Minimal, but it is the letter's opening claim, and an alert editor reads a veiled priority claim.
required_correction: Delete "To our knowledge,".
acceptable_alternatives: "In our seven-algorithm GSK-family panel, DT-GSK attains ...".
additional_evidence_needed: None.
dependencies: Same sentence as DS-05.
expected_improvement: Removes an unnecessary priority flavour from the letter's first claim.
post_revision_verification: Re-read the rendered letter.
status: open
```

### DS-11

```text
ticket_id: DS-11
review_stage: Stage 2 (governance record supporting Gate B)
reviewer_role: EIC / ECB
severity: Minor
priority: P3
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/governance/phase_gate_register.csv row 12 (phase_id 12)
claim_id_or_artifact_id: Phase-12 gate record
concise_issue: The Phase-12 gate row, though timestamped 2026-07-22, carries two statements the repository has already overtaken and omits the required page-count row.
exact_evidence_or_observation: (a) notes -- "R-14 (counting/equivalence probes) optional and open", but R-14 was closed at commit dbc824782 ("papers: close R-14 (budget-crossing probe)") and its regression test tests/regression/test_budget_crossing_semantics.py exists. (b) validation_evidence -- "X-ABL-02 SGSM overlay CEC2013 D50 -- full D50/D100+overhead design DEFERRED to a follow-up supplement revision, disclosed in S6.6", but supplementary.tex:1999-2023 now reports CEC2017 D50, CEC2017 D100 and CEC2013 D50 with overhead percentages. (c) No page-count row for the 39-page build (Section 10.14) -- see DS-01.
root_cause: The row was appended to rather than rewritten at each re-freeze.
scientific_or_editorial_justification: Section 10.1 requires the governance artifacts to be internally consistent and Gate A/B to rest on evidenced rows.
impact_on_validity_or_acceptance: No manuscript effect; an auditor reading the register would draw two wrong conclusions about the shipped state.
required_correction: Refresh the Phase-12 row: mark R-14 closed with its commit, restate the overlay scope as delivered, and add the current page-count measurement.
acceptable_alternatives: Append a dated correction block rather than rewriting.
additional_evidence_needed: None.
dependencies: DS-01 supplies the page-count values.
expected_improvement: Register matches the shipped state.
status: open
```

---

## 4. Summary of gate verdicts owned by this seat

| Gate | Verdict | Basis |
|---|---|---|
| **B — Desk review** | **PASS (conditional)** | No desk-rejection defect that cannot be corrected by the planned revision. Conditions: DS-01, DS-02, DS-03. |
| **D — Contribution merit** | **PASS (conditional)** | The central contribution is neither unsupported nor materially indistinguishable from prior work; the article type and venue are appropriate. Conditions: DS-03, DS-04. |

**Category scores (§6.1), with evidence:**

| Category | Score | Evidence |
|---|---|---|
| Scope fit for the venue | **4** | Algorithmic contribution with full specification and reproducible artifact chain; journal record itself unverified online (`journal_requirements.md` verified_online=FALSE) |
| Novelty / originality | **3** | Honest labelling throughout; one positive originality claim (ARGP) untested; the distinguishing feature of C1 conceded unisolated |
| Significance / importance | **3** | Modest but real; the negative result is the transferable insight and is correctly not counted as a contribution |
| Claim scope discipline | **4** | Zero reader-facing overclaims across all sections and the cover letter; three placement defects (DS-05/06/07) rather than honesty defects |
| Contribution-evidence alignment | **2** | DS-02 and DS-03: a false coverage statement plus an untested originality claim inside a headline contribution |
| Editorial/administrative readiness | **3** | 15/15 manifest and clean build, against a breached binding length budget with stale gate evidence (DS-01) |

*No acceptance, quartile, or decision guarantee is offered. Every finding above is
correctable without new experiments, new analysis, or any change to the byte-locked
DT-GSK optimizer core, and none requires a new evidence release.*
