# Stage 18 — Independent Q1/Q2 reviewer simulation

**Seat:** `s18_reviewers` · **Review cycle:** 2026-07-22 · **Governing prompt:** `papers/PAPER_REVIEW_PROMPT.md` §Stage 18 (L2680–2792), schema §5.4 (L1104–1148), DT-GSK profile §10 (L3160–3522), independence protocol §3.5 (L916–944), prohibited shortcuts §15 (L3977).

**Package audited (verified against the repo, not the prompt snapshot):**

| Item | Verified value | How verified |
|---|---|---|
| git HEAD | `45248eb31` | `git log --oneline -3` |
| freeze manifest `anchor_commit` | `abd2fa2f25c8426247b43c85bcb3d82041d00976` | `papers/governance/main_manuscript_freeze_manifest.json` |
| `check_manifest.py` | `15/15 match []` | executed |
| evidence release | `rel-2026-07-20-67d9345f9` | `papers/analysis/rel-2026-07-20-67d9345f9/`, provenance validator |
| `DT-GSK.pdf` / `supplementary.pdf` / `cover_letter.pdf` | 39 / 61 / 2 pages | PyMuPDF `page_count` |
| `validate_provenance_claims.py` | exit 0, all `ok` | executed |
| `validate_document_consistency.py` | exit 0, all `ok` | executed |
| `validate_cross_format_parity.py` | 579 rows, `FAIL=0` | executed |
| `validate_build_hygiene.py` | exit 0 | executed |
| remediation ledger | **80/80 closed** (70 `closed_verified` + 10 `superseded_with_evidence`) | `papers/governance/remediation_2026_07_18/ticket_status.csv` |

**Independence protocol statement (§3.5).** Each of the eight seats below (EIC, AE, R1–R6) was drafted as a separate pass over the artifacts and **has not been harmonised**. Where two seats reach different severities on the same underlying fact, both wordings are preserved verbatim and the disagreement is recorded in §9 (Preserved disagreements). No seat's finding was deleted or softened to produce agreement. Cross-seat duplicate root causes are noted but not merged, per §3.5(4)–(5).

**Scope directives honoured.** Author-side submission metadata (DOI/Zenodo, ORCID iDs, H.S.M.R. institutional e-mail) is out of scope and raised no ticket. External non-GSK baselines are out of scope as a *requirement*; they are nonetheless recorded where a reviewer will predictably raise them as an interpretive limit (R1, R6), which the manuscript itself already discloses. The **deliberately advertised ISM isolation null is not re-raised as a §10.9 leak**; only its *footprint/proportion* is questioned (AE), which is a different control.

---

## 0. Verification of the 2026-07-21/22 remediation (R-01 … R-14)

Performed first, so that no seat re-discovers a closed defect. Verdicts are independent of the ledger's own claims.

| Ticket | Verdict | Evidence |
|---|---|---|
| **R-01** Eq. (4) per-phase signs | **CORRECTLY CLOSED** | `papers/build_prompt_phases/phase_03/equations.tex` E3 defines `s_J = +1 iff f(x_i) > f(x_R3)`, `s_S = +1 iff f(x_i) > f(x_R2)` *inside the numbered display*, and the convention is restated in rendered text below it (incl. "an exact tie takes −1"). Recomputed against the frozen kernel `src/gsk_family/optimizers/_dt_subsystems/_numba_accel.py:403–414`: junior `if fitness[i] > fitness[rg3]` → `+(pop[rg3]-pop[i])`, else `+(pop[i]-pop[rg3])`; senior `if fitness[i] > fitness[r2]` → `+(pop[r2]-pop[i])`, else reversed. Tie falls to the `else` branch = −1. **Equation, prose and code agree exactly.** Notation row present. |
| **R-02** registry E3/E4/E8 | **CORRECTLY CLOSED** | `equations.tex` E4 comment + display state permutation-chunk blocks ("arbitrary coordinate subsets, NOT contiguous index ranges"); E3 senior arrangement is `(x_R1 − x_R3) + s_S(x_R2 − x_i)` matching `_numba_accel.py:412`; E8 `f(v_i) ≤ f(x_i)` (ties accepted), consistent with `proposed_algorithm.tex:79–80`. |
| **R-03** DOCX OMML `&` markers | **CORRECTLY CLOSED** | Parsed `word/document.xml` of both DOCX: `DT-GSK.docx` 3,610 `m:t` runs / **0** literal `&amp;` inside math; `supplementary.docx` 2,220 runs / **0**. Native tables present (17 and 26 `w:tbl`); 753/640 `m:oMath`. |
| **R-04** restart invariant | **CORRECTLY CLOSED** | `sections/proposed_algorithm.tex:204–210`: "Every subsystem is elitist … with one deliberate exception: the deep-stall restart resamples the working population outright … The global best `x^gb` is held separately …, is never re-initialized, and is what the run returns". |
| **R-05** budget-crossing semantics | **CLOSED, with a scope caveat** (see S18-R2-02) | `sections/performance.tex:164–178` states DT-GSK truncates before evaluating and the six ports evaluate the terminal batch in full and count the in-budget prefix; "All seven optimizers are therefore held to exactly the same MaxFES charge." |
| **R-06** supplement release identity | **CORRECTLY CLOSED** | Rendered `supplementary.pdf` pp. 44 and 53 name `rel-2026-07-20-67d9345f9` (anchor `67d9345f9502…`) as the release accompanying the article and mark `rel-2026-07-16-78f075cb0` superseded. `validate_provenance_claims.py` §[1]/[1b] all `ok`. |
| **R-07** provenance validator hardening | **CORRECTLY CLOSED** | Executed; the run prints the authority-context rule, reads both rendered PDFs and both DOCX, and checks live module hashes and the change register (CR-0007, C006, M038). Exit 0. |
| **R-08** ISM not a fourth contribution | **CORRECTLY CLOSED** | `main.tex:147–152` (abstract) and `introduction.tex:86–135` carry C1–C3 only; ISM is "a supporting mechanism". `conclusions.tex:100–102` says the null is presented "rather than as a fourth claimed contribution". |
| **R-09** cover letter | **CORRECTLY CLOSED** | `cover_letter.tex` has no reviewer block (only a non-rendered author-fill comment at L73–78) and narrows byte-stability: "with byte-stable determinism for **DT-GSK** in the declared supported environment" (L55). |
| **R-10…R-13** | **CLOSED** | Vector bounds notation `∏_{j}[ℓ_j,u_j]` at `proposed_algorithm.tex:51–56`; phase-gate write-back present in `phase_gate_register.csv`; de-packed prose observed throughout §4. |
| **R-14** budget-crossing probe | **CLOSED, verification narrower than the manuscript states** (S18-R2-02) | `tests/regression/test_budget_crossing_semantics.py` exists, parametrised over all seven optimizers, but exercises **one** configuration: `suite="sphere"`, `func_id=1`, `_DIM=10`, `_NP=100`, `_MAX_NFES=1050`, `_SEED=20240620`. |

**Two closures are challenged below as incomplete:** `N-013`/`E-014` (page-overflow regression, S18-R5-01) and the terminal freeze `C-008`/`C-001` (stale anchor, S18-EIC-02). One closure — `RT-001` — was closed by a *different* remedy than the governing prompt anticipates, and its closure record contains an undisclosed material fact (S18-R5-02).

---

## 1. EIC report

```text
reviewer_role: Editor-in-Chief
expertise: journal fit, significance, novelty policy, desk-rejection risk, research integrity
confidence: High (package fully inspected; journal policy verified only against the project's own recorded evidence card, not re-verified live)
```

**Manuscript summary.** The paper proposes DT-GSK, a GSK-family metaheuristic that keeps the published junior/senior gaining-sharing vector updates unchanged and layers on (i) a dimension-tiered adaptive scaffold (credit-based operator selection with acceptance-gated pruning, tier-floored nonlinear population reduction, a hard-capped stagnation escape, a global-best-preserving deep-stall restart), (ii) a one-shot, RNG-free eigenframe compass polish in the final budget slice at `D ≥ 50`, and (iii) a determinism/evidence-lock layer. An interaction-structure memory (ISM) learned from strictly improving accepted moves supplies the polish basis and upper-tier crossover blocks; its direct isolation is reported as a controlled negative result. Evaluation is a seven-algorithm within-family panel on CEC2017 (primary, 29 functions × 4 dimensions × 51 runs), CEC2011 (22 problems × 25 runs) and CEC2013 (28 functions × 3 dimensions × 51 runs) under one frozen configuration.

**Overall assessment.** In scope and form this is a plausible *Algorithms* (MDPI) submission: an algorithmic contribution with a complete mechanism specification, an unusually strong reproducibility apparatus, and empirical claims that are deliberately bounded. **Desk-rejection risk is low but non-zero**, and it is concentrated in production/presentation rather than science: one supplement table physically runs off the page (S18-R5-01), and the main text points readers to a table column that does not exist (S18-R4-01). Neither is a scientific error; both are the kind of defect an MDPI production editor returns before review. The scientific desk risk is the familiar one for this genre — a same-family panel with five of six comparators co-authored by two of the present authors — which the manuscript discloses fully in the Conflicts of Interest and the limitations. I judge external review **justified**: the negative ISM result, the budget-fair protocol and the determinism layer are of interest independent of the ranking claim.

**Strengths (3–5).**
1. Claim discipline is genuinely above the norm for this literature: the headline is stated as a *descriptive* across-dimension mean of per-dimension Friedman ranks with the pooled-test misreading explicitly forbidden (`performance.tex:325–330`), and every unfavourable cell is stated beside the favourable one.
2. The evidence lock is real and machine-checked, not rhetorical: `check_manifest` 15/15, a hardened provenance validator that reads rendered PDF *and* DOCX, and 579 cross-format parity rows at `FAIL=0`.
3. A publishable negative result (ISM isolation null, with a post-hoc function-class breakdown confirming it is not a separable-subset artefact) is retained rather than buried.
4. Method↔code correspondence at the equation level is verifiable and, where I checked it (Eq. 4 against the frozen numba kernel), exact.
5. The conflict-of-interest disclosure is unusually candid and correctly placed.

**Major concerns.** S18-EIC-01 (stale governing snapshot — administrative), S18-EIC-02 (freeze anchor does not identify the shipped state), plus concurrence with S18-R5-01 and S18-R4-01 as desk-risk items.

**Minor concerns.** The cover letter's "To our knowledge, DT-GSK attains the best overall CEC2017 Friedman mean rank on the seven-algorithm GSK-family panel" attaches an epistemic hedge to a measured, self-computed quantity; it reads as a residue of a withdrawn priority claim (M-034). Recommend deleting "To our knowledge".

**Claims that must be narrowed.** None at EIC level beyond those the specialist seats name; the abstract does not attribute "2.48" to a suite (see R4).

**Recommendation:** *Minor revision* (internal disposition), external review justified.

**Scores.** Fit 5 · Significance 4 · Novelty 3 · Integrity 5 · Presentation 3 · Desk-readiness 3.

```text
ticket_id: S18-EIC-01
review_stage: 18
reviewer_role: EIC
severity: Moderate
priority: P3
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/PAPER_REVIEW_PROMPT.md §1.5 (L118–120), §10.7 final bullet (L3299)
claim_id_or_artifact_id: RT-001; remediation ledger
concise_issue: The governing review prompt's embedded status snapshot is stale and contradicts the repository on ledger status and on RT-001's disposition.
exact_evidence_or_observation: §1.5 (L120) states "73/80 fully closed" with "seven terminal / machine-gated / author-gated tickets … open (RT-001 the live runtime blocker; C-008 -> C-001 the terminal freeze+commit; N-009 / N-021 / M-007 / E-012)". papers/governance/remediation_2026_07_18/ticket_status.csv has 80 rows with lifecycle_status ∈ {closed_verified: 70, superseded_with_evidence: 10} and zero open rows; N-009, N-021, M-007, E-012, C-001, C-008 and RT-001 are all closed_verified. §10.7 (L3299) describes RT-001 as "IN PROGRESS", with the runtime table "being brought into single-environment comparability by re-timing all six comparators (scripts/retime_comparators.py)"; the ledger's RT-001 row records the opposite outcome: "RESOLVED via Decision 7 Option 3 (DT-GSK-only fallback). Option 2 … was executed 2026-07-21 … but FAILED the determinism gate".
root_cause: The prompt snapshot is dated 2026-07-20 and predates the 07-21/07-22 remediation; §1.4 precedence puts the repository above the snapshot.
scientific_or_editorial_justification: A review that applies §10.7's RT-001 instruction literally would certify a runtime table that no longer exists in the form described, and would leave open tickets that are closed.
impact_on_validity_or_acceptance: No effect on manuscript validity; material for review governance only.
required_correction: Refresh §1.5/§1.5.0-C and the §10.7 RT-001 bullet to the 2026-07-22 state, or mark them explicitly historical.
acceptable_alternatives: Add a dated "superseded by repository state" banner at §1.5.
additional_evidence_needed: none
dependencies: none
expected_improvement: Removes a standing contradiction between the governing prompt and the artefacts it governs.
post_revision_verification: Re-read §1.5/§10.7 against ticket_status.csv; counts must agree.
status: open
```

```text
ticket_id: S18-EIC-02
review_stage: 18
reviewer_role: EIC
severity: Major
priority: P1
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/governance/main_manuscript_freeze_manifest.json (field anchor_commit)
claim_id_or_artifact_id: C-008 / C-001 terminal freeze; Gate A (package integrity)
concise_issue: The manuscript freeze manifest's anchor_commit points at a commit that does not contain the frozen bytes it hashes, so the recorded freeze does not identify the shipped manuscript state.
exact_evidence_or_observation: main_manuscript_freeze_manifest.json records "anchor_commit": "abd2fa2f25c8426247b43c85bcb3d82041d00976". `git show --stat 45248eb31` (HEAD) shows that HEAD itself modified papers/sections/performance.tex (+11 lines), rebuilt papers/DT-GSK.pdf and papers/DT-GSK.docx, and amended this same manifest: the diff of the manifest in HEAD changes performance.tex sha256 6d7b6258…->fd7dbbac… (50,426 -> 51,044 bytes), DT-GSK.pdf 5d1f095b…->34362769…, DT-GSK.docx 647028d5…->1ad8c3b2…, and generated_utc 2026-07-22T00:00:00Z -> T12:00:00Z, while leaving anchor_commit untouched. `git diff --stat abd2fa2f25c8 HEAD -- papers/sections/ papers/DT-GSK.pdf` confirms performance.tex and DT-GSK.pdf differ between the recorded anchor and HEAD. check_manifest.py reports 15/15 because it compares hashes to the working tree, not to the anchor commit.
root_cause: The 2026-07-22 amendment re-hashed the changed files but did not re-stamp the anchor; the freeze statement's "Amended 2026-07-22" clause was added instead.
scientific_or_editorial_justification: The whole point of a freeze anchor is that a third party can check out one commit and obtain byte-identical submission artefacts. At abd2fa2f2 they obtain a different performance.tex and a different PDF.
impact_on_validity_or_acceptance: No reported number changes (the amendment is a text-only fairness paragraph). It is nevertheless a Gate A traceability failure and reopens the exact defect C-001 was raised for ("No single authoritative manuscript state can be identified").
required_correction: Re-stamp anchor_commit to the commit that contains the hashed bytes (45248eb31…, or the commit that lands this correction), and keep abd2fa2f2 only as a pre_amendment_base field.
acceptable_alternatives: Add an explicit "amended_at_commit" field and have check_manifest.py assert `git show <anchor_commit>:<path>` hashes equal the recorded sha256 for every row.
additional_evidence_needed: none
dependencies: none
expected_improvement: Restores one authoritative, checkable manuscript state.
post_revision_verification: For all 15 manifest rows, `git show <anchor_commit>:<path> | sha256sum` must equal the recorded hash; extend check_manifest.py to enforce it.
status: open
```

---

## 2. AE report

```text
reviewer_role: Associate Editor
expertise: evidence-package adequacy, proportionality of revision, reviewer-concern interaction
confidence: High
```

**Manuscript summary.** As above; from the AE chair the question is whether the shipped package lets six reviewers reach a fair decision without new experiments.

**Overall assessment.** The package is **sufficient for a fair decision**, and — importantly — every major concern raised by the six simulated reviewers below is answerable **without new runs**. That is unusual and it should be stated to the reviewers: the two heaviest-looking objections (comparator runtime, configuration-selection exposure) are *disclosure* problems, not missing-experiment problems, because the manuscript has already chosen to withhold the comparison (runtime) or to attest rather than archive (tuning history). The revision level proportionate to the confirmed defect set is **Minor revision**: one production fix, three text/traceability fixes, one governance fix. Nothing in my pass requires re-running the optimizer, and the standing "no rerun / no new evidence release" constraint is not in tension with any required correction.

**How the concerns interact.** Three seats (R4, R5, R2) converge on one root cause worth naming: *the manuscript's statistical and verification prose has drifted behind its own remediation*. M-027 replaced the tabulated `A12` with the aligned rank-biserial `r` but left five sentences describing an `A12` column (R4); M-026 introduced the tie-corrected Friedman but the printed CEC2013 omnibus p-values are still the uncorrected ones (R4); R-14 added a one-configuration probe but the manuscript describes it as a seven-optimizer verification (R2). These are individually small and collectively a pattern: **each fix updated the artefact and under-updated the prose**. I recommend the authors run a single "artefact→prose" sweep rather than three point fixes.

**Strengths.** (1) Every unfavourable inferential cell material to the headline is stated *alongside* the favourable ones, satisfying §10.7 loss-visibility parity — I checked the eGSK D≥30 head-to-heads, the CEC2011 Holm-significant loss, the CEC2013 D30 third place and the non-monotone rank trend, and all appear in the main text. (2) The robustness battery discloses its own divergences (median re-ranking swaps two comparator pairs; the D=100 first place becomes an exact tie under the median endpoint) instead of suppressing them. (3) The supplement's "Limitations in Full" is the conclusions' wording *moved, not rewritten*, and the count reconciles (7 + 3 attribution gaps + 1 statistical = the "Eleven limitations" of `conclusions.tex:66`).

**Major concerns.** Concurrence with S18-R4-01, S18-R5-01, S18-R5-02, S18-EIC-02.

**Minor concerns.** S18-AE-01 (below).

**Recommendation:** *Minor revision.* **Scores.** Evidence adequacy 4 · Fairness of package 4 · Proportionality 5 · Presentation 3.

```text
ticket_id: S18-AE-01
review_stage: 18
reviewer_role: AE
severity: Moderate
priority: P3
confidence: High
issue_type: claim-scope
manuscript_location: main.tex:146-152; introduction.tex:74, 135; proposed_algorithm.tex:271; performance.tex:826-829; conclusions.tex:84-102; cover_letter.tex:55, 57
claim_id_or_artifact_id: X-ABL-02 (S6.5 isolation null); §10.9 narrowing (PAPER_REVIEW_PROMPT.md L3327-3349)
concise_issue: The deliberately advertised ISM null now occupies six main-manuscript locations plus two cover-letter sentences, exceeding the "brief" allowance the §10.9 narrowing granted, and one location imports the §S6.6 post-hoc function-class result the narrowing scoped to §S6.5.
exact_evidence_or_observation: The narrowing (L3329-3331) permits the null "now briefly: one abstract sentence plus the introduction's supporting-component paragraph (§1.5.0-B(c))" and requires that "every main-text sentence touching the null MUST stay scoped to the evidence (§S6.5)". Observed: (a) abstract main.tex:146-147; (b) introduction.tex:74 "answers in the negative"; (c) introduction.tex:135, which additionally states "the function-class analysis reveals no systematic advantage on the hybrid or composition categories (… Sections S6.5 and S6.6)"; (d) proposed_algorithm.tex:271 (Methods); (e) performance.tex:826-829 (Discussion); (f) conclusions.tex:84-102, a full paragraph that also states "A breakdown by function class shows this null holds even on the hybrid and composition functions"; (g)+(h) cover_letter.tex:55 and :57.
root_cause: Successive honesty-directed edits each added a null restatement without a global budget for it.
scientific_or_editorial_justification: I am NOT calling this a §10.9 leak - the narrowing explicitly permits disclosing the null and forbids re-raising it as a leak. The control at issue is the narrowing's own scope: brevity and S6.5-scoping. Two locations now carry an S6.6 post-hoc result into the main text and the cover letter, which is a detailed component-effect conclusion outside the granted exemption.
impact_on_validity_or_acceptance: No validity impact. Two risks: a reviewer reads the repetition as the paper arguing against its own mechanism, and the ECB's own control is applied inconsistently.
required_correction: ECB adjudication. Either (a) re-confirm the wider footprint as an author decision and record it in decision_log.md as an explicit extension of §1.5.0-B(c), or (b) reduce to the sanctioned two locations plus the one Discussion pointer, and drop the S6.6 function-class clause from introduction.tex:135 and conclusions.tex:91-95 (it stays in the Supplement).
acceptable_alternatives: Keep all locations but scope each to "(Supplement S6.5)" and remove the S6.6-derived clauses from the main text and cover letter.
additional_evidence_needed: Author/ECB decision.
dependencies: none
expected_improvement: Restores a single consistent reading of the §10.9 narrowing.
post_revision_verification: Recount null-bearing sentences in the rendered PDF and cover letter against the recorded decision.
status: open
```

---

## 3. R1 — Domain-science reviewer

```text
reviewer_role: R1 (domain science: metaheuristics / GSK lineage)
expertise: population metaheuristics, GSK family, benchmark-driven algorithm design
confidence: High on the family positioning; Medium on the wider structure-learning literature (closed corpus)
```

**Manuscript summary.** See EIC. My question is whether the gap is real, whether it matters, and whether the panel is strong enough to make the answer interesting.

**Overall assessment.** The gap is stated more carefully than is usual in this literature and is, as bounded, correct: `related_work.tex:257–270` restricts the "none learns or exploits the interaction structure of accepted moves" claim to the six surveyed GSK variants and explicitly disclaims a state-of-the-art priority. I checked that the survey's own evidence is present (a comparative family table with per-variant adaptation targets) and that the NLPSR schedule is labelled "a variant of the APGSK NLPSR schedule, explicitly not claimed as new" (`introduction.tex:106–108`). That is the right standard.

Scientifically the paper is in an awkward but honest position: the mechanism that motivates the whole design question — "can a GSK-family algorithm learn, while it runs and at no extra objective evaluations, which coordinates improve together" (`introduction.tex:28–32`) — is answered **in the negative**, and the performance standing is therefore carried by C2/C1, which are explicitly "modifications of cited antecedents" plus one operator (ARGP) the authors could not find in the surveyed family. The paper knows this and says so. My concern is not dishonesty; it is that **the framing still leads with the question the evidence answers negatively**, which will read to some referees as a paper whose thesis failed and whose contribution was re-labelled afterwards.

**Strengths.** (1) The three-deficiency positioning (structure blindness, non-deterministic endgame refinement, regime-limited adaptation evidence) is each traced to a cited variant's own documented weakness rather than asserted. (2) Every inherited element is named and attributed, including the JADE/L-SHADE midpoint repair. (3) The scientific implication actually offered — a boundary result on cheap accepted-move structure learning for GSK at `D ≤ 100` — is a legitimate contribution to the family literature and is rare in a venue where negative results are usually dropped.

**Major concerns.** S18-R1-01.

**Minor concerns.** The introduction's design question (L28–32) and the title's promise ("Dimension-Tiered Adaptive Control and Deterministic Refinement") are not the same paper; a reader arriving from the abstract has to re-orient. Consider opening §1 with the control-resolution-by-dimension question and demoting the structure-learning question to the ISM paragraph, which is where the evidence lives.

**Required additional analyses.** None. I explicitly do **not** ask for external baselines: the manuscript's scope is a declared design choice, the limitation is stated twice, and adding an L-SHADE-class comparator would not change any claim the paper actually makes.

**Claims that must be narrowed.** None found beyond R4's.

**Recommendation:** *Minor revision.* **Scores.** Problem importance 4 · Gap identification 4 · Contribution distinction 3 · Baseline strength 3 · Scientific implication 4.

```text
ticket_id: S18-R1-01
review_stage: 18
reviewer_role: R1
severity: Moderate
priority: P2
confidence: High
issue_type: claim-scope
manuscript_location: introduction.tex:26-32 vs introduction.tex:73-76 and 135; conclusions.tex:96-102
claim_id_or_artifact_id: BG-03; MT-01; X-ABL-02
concise_issue: The paper's stated organising question is the one its own evidence answers negatively, while the contributions that carry the result are introduced as secondary to it.
exact_evidence_or_observation: introduction.tex:28-32 poses the single design question as "can a GSK-family algorithm learn, while it runs and at no extra objective evaluations, which coordinates of the search space improve together, and can it exploit that record". introduction.tex:73-74 then says "Whether such a signal, once recovered, improves the optimizer is a hypothesis this paper tests --- and, for GSK at these dimensions, answers in the negative", and introduction.tex:135 positions ISM as "a secondary exploratory mechanism". The contributions carrying the reported standing (C2 scaffold, C1 polish) are described in C2 as modifications of cited antecedents, with only ARGP's arm-freezing rule claimed as not found in the surveyed family (introduction.tex:110-112).
root_cause: The narrative was inherited from an earlier ISM-centred framing and re-scoped by C-004/M-005/M-006 without re-writing the opening question.
scientific_or_editorial_justification: A referee assessing "what is new relative to the closest method" will follow the organising question, reach the null, and conclude the paper's own thesis failed - even though the delivered contribution (dimension-resolved control + deterministic refinement + a reproducible within-family evaluation) is intact and separately motivated.
impact_on_validity_or_acceptance: No validity impact; a material acceptance risk at a venue where the first two paragraphs set the frame.
required_correction: Re-order §1 so the organising question is control resolution by dimension (which the evidence supports) and the structure-learning hypothesis is introduced as the paper's secondary, resolved-negative question. No claim, number or scope changes.
acceptable_alternatives: Keep the order but add one sentence after L32 stating that the paper's positive findings concern the scaffold and the polish and that the structure-learning question is answered negatively.
additional_evidence_needed: none
dependencies: none
expected_improvement: Aligns the reader's expectation with the evidence; removes the "failed thesis" reading.
post_revision_verification: Re-read §1 and the abstract in sequence; the contribution named first must be one the evidence supports.
status: open
```

---

## 4. R2 — Theory / method reviewer

```text
reviewer_role: R2 (theory and method specification)
expertise: operator derivation, pseudocode/code correspondence, complexity, determinism
confidence: Confirmed on the equations I re-derived; High elsewhere
```

**Manuscript summary.** See EIC. I attempted to rebuild the method from the printed specification alone.

**Overall assessment.** **The method is rederivable from the paper.** I reconstructed the junior/senior update from Eq. (4) and checked it symbolically against the frozen kernel: the per-phase signs, the donor arrangements (junior differences the two rank neighbours and compares `x_R3`; senior differences best/worst and compares the middle `x_R2`), and the tie disposition all match `_numba_accel.py:403–414` exactly. I checked the ACE update (Eq. 6) against its documented branches, the crossover mask (Eq. 5) against the "permutation chunks, not contiguous ranges" statement, greedy acceptance (Eq. 9) against `≤`, and the ISM EMA (Eq. 10) — `G ← λG + η Σ w_i φ(δ̂)φ(δ̂)ᵀ` — which correctly puts the retention factor on the *old* graph with an independent learning rate, i.e. the §10.6 exemplar defect is **not** present here. The complexity account is honest (`O(NP·D²)` accumulation, one `O(D³)` eigendecomposition, no complexity improvement claimed).

Two things I could not close: the manuscript describes a verification more broadly than the shipped test performs (S18-R2-02), and one architectural statement is under-specified for reimplementation (S18-R2-01).

**Strengths.** (1) Every equation carries a code anchor and an inherited/modified/original label, and the labels are accurate where I checked them. (2) The three reproducibility levels are separated (`proposed_algorithm.tex:717–728`) and byte-stability is correctly restricted: "All three cover DT-GSK and this repository's pipeline only; no byte-stability claim is made for the comparator implementations." (3) Dormant-but-shipped mechanisms are disclosed rather than hidden (ISM-block subspace local search implemented but not enabled; trust-region budget policy "present, runtime-inert"), with a regression test named for the dormancy.

**Major concerns.** S18-R2-01, S18-R2-02.

**Minor concerns.** Eq. (12) writes the polish as `x* ← CompassSearch(x*, V = eig(G_signed))` with no step schedule, no contraction factor and no stopping rule in the numbered display; the prose supplies "start 0.96" and "one-shot", and the operator specification is in Supplement S5.9. For a *titular* contribution (C1), the display is thinner than the ISM display it consumes.

**Required additional analyses.** None.

**Recommendation:** *Minor revision.* **Scores.** Method specification 4 · Equation/code correspondence 5 · Complexity treatment 4 · Determinism treatment 4.

```text
ticket_id: S18-R2-01
review_stage: 18
reviewer_role: R2
severity: Minor
priority: P3
confidence: High
issue_type: method
manuscript_location: papers/build_prompt_phases/phase_03/equations.tex E11 (eq:eigen-polish); sections/proposed_algorithm.tex:565-608
claim_id_or_artifact_id: MT-09 (C1 eigenframe final polish)
concise_issue: The titular C1 operator is the least completely specified equation in the registry: the printed display fixes only the basis, not the compass schedule that determines its behaviour.
exact_evidence_or_observation: E11 renders as `x* <- CompassSearch(x*, V = eig(G_signed))`. The initial step ("start 0.96"), the contraction rule, the per-direction probe order, the acceptance test and the termination condition appear only in prose and in the Supplement's operator specification, not in the numbered display or the notation table for this subsystem.
root_cause: The registry row was written as a one-line composition of an existing search primitive.
scientific_or_editorial_justification: Section 10.6 requires that every titular or load-bearing update rule be recomputable from the printed specification. A reader reimplementing C1 from Eq. (12) alone will not reproduce the operator; two implementations with different step schedules would both satisfy the printed rule.
impact_on_validity_or_acceptance: No effect on reported numbers. It weakens the paper's strongest reproducibility selling point precisely at its named contribution.
required_correction: Expand E11 (or add E11b) to display the step schedule and acceptance test, or add an explicit forward reference in the display's vicinity to the Supplement subsection that specifies it normatively.
acceptable_alternatives: A three-line algorithmic block for the compass loop inside Section 3.6.
additional_evidence_needed: none
dependencies: Must not alter the frozen operator (code is byte-locked); this is a printing change only.
expected_improvement: C1 becomes reimplementable from the paper at the same standard as C2 and the ISM.
post_revision_verification: Re-derive the polish from the printed text alone and diff the derived step sequence against _final_polish_compass.
status: open
```

```text
ticket_id: S18-R2-02
review_stage: 18
reviewer_role: R2
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: evidence
manuscript_location: sections/performance.tex:170-174
claim_id_or_artifact_id: R-14; tests/regression/test_budget_crossing_semantics.py
concise_issue: The manuscript states a panel-wide budget-crossing verification, but the shipped probe exercises exactly one synthetic problem at one dimension, one population size and one seed.
exact_evidence_or_observation: performance.tex:170-174 reads "That crossing falls only on the terminal generation, so the uncounted rows enter no incumbent and no later state; strictly truncating them was verified to leave the returned solution, its fitness, and the charged budget bit-identical for all seven optimizers, so the crossing confers no search advantage." The cited probe, tests/regression/test_budget_crossing_semantics.py, sets `suite="sphere"`, `func_id=1`, `_DIM = 10`, `_NP = 100`, `_MAX_NFES = 1050`, `_SEED = 20240620` and parametrises only over the seven optimizer modules. No CEC function, no D >= 50 cell, no CEC2011 problem, one seed.
root_cause: The test was designed for speed ("reproduce it in about a second"), and the manuscript sentence was written from the argument rather than from the test's scope.
scientific_or_editorial_justification: The structural argument (uncounted terminal rows never enter incumbent or state) is sound and probably general, but the sentence as printed asserts a verification, not an argument. The comparators whose crossing is least obviously bounded are exactly the ones with solver-internal or local-search evaluation paths (eGSK's SLSQP polish, ATMALS-GSK's randomized local search); at MaxFES = 1050 on a 10-D sphere it is not established that those paths are exercised at all.
impact_on_validity_or_acceptance: The fairness conclusion is very likely correct; the claim is nonetheless broader than its evidence, and a reproducibility referee who opens the test will say so.
required_correction: Either state the verification's scope in the sentence ("verified on a bounded probe in which MaxFES is not a multiple of the population size") or extend the probe to at least one CEC2017 cell at D = 50 or D = 100 and one CEC2011 problem, and assert there that the uncounted overrun is < NP and inert.
acceptable_alternatives: Move the sentence's evidence pointer into the text (a footnote naming the test and its configuration).
additional_evidence_needed: If the broader wording is kept: the extended probe. No optimizer change and no campaign rerun is required - the probe is a unit test.
dependencies: none
expected_improvement: The strongest fairness claim in the protocol section becomes exactly as strong as its evidence.
post_revision_verification: Re-read the sentence against the test's parametrisation; every optimizer/problem class it quantifies over must appear in the test ids.
status: open
```

---

## 5. R3 — Experimental-design reviewer

```text
reviewer_role: R3 (experimental design)
expertise: benchmark protocols, comparator fairness, tuning discipline, external validity
confidence: High
```

**Manuscript summary.** See EIC. I audited the protocol table, the pairing rule, the failure policy and the tuning disclosure.

**Overall assessment.** The protocol is **well designed and unusually transparent**, and two design decisions that are normally silent here are made explicit and correct: (i) CEC2017 is declared the *development* suite and the headline is labelled development-suite performance, with CEC2011/CEC2013 held out; (ii) the DT-GSK self-initialization exception is disclosed as a pairing asymmetry rather than smoothed over. The seed schedule is optimizer-independent and printed in full, with a 70,813-row recomputation audit. The CEC2011 infeasibility penalty (`10^30`) is stated and applied identically to all seven.

My substantive concern is that the **magnitude** of the selection exposure is undisclosed and unarchivable, which converts the single most important design question into an author attestation.

**Strengths.** (1) One frozen configuration across three suites with no per-suite tuning, hash-locked and validator-enforced. (2) The F2 exclusion is stated as a protocol adoption applied uniformly in every panel cell, not as a convenient drop. (3) The convergence-panel selection rule was prespecified and frozen before rendering and *mandates* an unfavourable case, which the paper then discusses at length (F26 at D=30) rather than skipping — I verified the F26 numbers against `descriptive_stats_cec2017_D30.csv` (DT-GSK mean 1.159e3 vs ATMALS 1.323e3; DT-GSK SD 7.53e1, smallest in panel; next smallest GSK 2.69e2) and they are exact.

**Major concerns.** S18-R3-01.

**Minor concerns.** The self-init asymmetry is disclosed but never bounded: the manuscript says it "is not separately bounded and is most consequential at low dimension" (`supplementary.tex:1231–1236`). A cheap, no-rerun bound exists — report the distribution of initial-population best fitness for DT-GSK vs the shared `X0` across seeds, which is already in the released per-run logs. I do **not** make this a required experiment.

**Required additional analyses (decision-relevant design).** One, and only if the authors wish to convert an attestation into evidence: archive the *count* and the *selection metric* of the candidate configurations compared during development (no rerun needed — it is a development-history record), so a referee can assess optimistic-selection magnitude.

**Claims that must be narrowed.** None; the development-suite label already does the necessary narrowing.

**Recommendation:** *Minor revision.* **Scores.** Benchmark choice 5 · Controls 4 · Comparator fairness 4 · Tuning discipline 3 · External validity 3.

```text
ticket_id: S18-R3-01
review_stage: 18
reviewer_role: R3
severity: Major
priority: P2
confidence: Confirmed
issue_type: experimental-design
manuscript_location: supplementary.tex:1148-1169 (S5 Configuration Selection and Development Protocol); sections/performance.tex:103-111
claim_id_or_artifact_id: R6-T03 (development-suite / selection-exposure disclosure); ART-PARAMS
concise_issue: The configuration-selection exposure is disclosed qualitatively but never quantified, and the supporting record is explicitly outside the immutable evidence release, so the headline suite's optimistic-selection magnitude cannot be assessed by any reader.
exact_evidence_or_observation: supplementary.tex:1157-1161 states "Before the final configuration was promoted, several full-panel candidate configurations were compared against the family panel during development; this selection exposure is disclosed here as an author-attested development-history note (the intermediate candidates are not part of the immutable evidence release), rather than absorbed silently." No count of candidates, no selection statistic, no search space, and no tuning budget is given anywhere in the manuscript or supplement. The companion claim that "no CEC2011 or CEC2013 result was consulted during configuration selection" (L1155-1157) is likewise an attestation (evidence class A) with no artefact under RAW_OR_IMMUTABLE_EVIDENCE_ROOT.
root_cause: Development-phase candidate evaluations were never promoted to a versioned release, so the record cannot be cited even though the exposure is acknowledged.
scientific_or_editorial_justification: "Several" spans a factor of ten in selection bias. The headline claim (best overall CEC2017 Friedman mean rank, 2.48) is a development-suite result; without the candidate count a referee cannot distinguish light configuration fixing from an effective multi-comparison search on the primary suite. This is the classic benchmark-tuning objection and the manuscript has invited it by being honest about the exposure.
impact_on_validity_or_acceptance: Does not invalidate the held-out CEC2011/CEC2013 standings, which is precisely why the disclosure works at all. It caps how far the CEC2017 headline can be relied on and is the single most likely target of a rejection argument on design grounds.
required_correction: State the number of candidate configurations compared, the statistic on which the final one was chosen, and whether comparison was on the full 29x4 grid or a subset. This is a development-history statement, not a new experiment.
acceptable_alternatives: If the count is genuinely unrecoverable, say so explicitly ("the number of candidates was not recorded") - an admitted gap is defensible; an unquantified "several" is not.
additional_evidence_needed: The development-history record (author-side); no rerun, no new evidence release.
dependencies: Interacts with R6's tuning-explanation argument.
expected_improvement: Converts the strongest design objection from unbounded to bounded.
post_revision_verification: The revised S5 subsection must state a number (or an explicit "not recorded") and a selection statistic; the claims matrix row must cite the development-history artefact or mark it author-attested.
status: open
```

---

## 6. R4 — Statistical reviewer

```text
reviewer_role: R4 (statistics)
expertise: nonparametric multi-algorithm comparison, multiplicity, effect sizes, resampling
confidence: Confirmed on every value I recomputed
```

**Manuscript summary.** See EIC. I recomputed the headline statistics from the released bundle.

**Overall assessment.** The statistical design is **sound and the arithmetic is right**. I independently recomputed or cross-checked: the CEC2017 overall mean rank (bundle 2.482759 → printed 2.48; eGSK 2.961207 → 2.96); all four per-dimension ranks (2.8793/2.5000/2.2069/2.3448 → 2.88/2.50/2.21/2.34); CEC2013 overall (2.797619 → 2.80; eGSK 3.410714 → 3.41); CEC2011 (DT-GSK 3.363636 → 3.36; eGSK 2.522727 → 2.52; Iman–Davenport F 4.266899 → 4.27, p 6.008e-4 → 6.0e-4); every T15 `r`, `p` and `p_Holm` cell against `wilcoxon_holm_cec2017_D*.csv`; the 17/7/0 tally and the 15-of-24 global-Holm sensitivity; the four DT-GSK–eGSK rank gaps against CD = 1.673; and the within-one-CD cohorts in the Nemenyi caption (at D=100 GSK falls outside by 0.017 rank units — correct, but tight). The estimand, unit of analysis, pairing key and multiplicity families are all stated correctly, and the "overall" row is explicitly *not* attached to a pooled omnibus.

Two reporting defects are nonetheless confirmed, and one of them is the kind a statistical referee will open with.

**Strengths.** (1) The Holm family is enumerated (size 6 per dimension) and the 24-cell tally is explicitly labelled descriptive, with a global-Holm sensitivity check supplied. (2) The BCa intervals are correctly demoted to *descriptive rank-stability* intervals because they resample fixed midranks — this is a subtlety most papers get wrong. (3) Benjamini–Hochberg appears only as a separately labelled exploratory companion. (4) The tie-corrected Friedman is implemented, the correction factors are printed per dimension (C = 0.890 at D10 over 9 tied functions, 0.979 at D30, exactly 1 at D50/D100), and both forms are released.

**Major concerns.** S18-R4-01, S18-R4-02, S18-R4-03.

**Minor concerns.** (a) The abstract attributes "2.48" to no suite: "Against six GSK-family baselines on CEC2017 (primary), CEC2011, and CEC2013 … DT-GSK attains the best overall Friedman mean rank in the seven-algorithm GSK-family panel (2.48 …)". 2.48 is CEC2017-only. One word ("on CEC2017") fixes it. (b) `performance.tex:754–756` reports a bare mean for the other suites — "80.64 s on CEC2011 (native dimensions)" — where `cost_cec2017.csv` gives `mean = 80.6418, sd = 119.3400, n = 550`. An SD larger than the mean means the pooled figure aggregates 22 problems of very different native dimension and cost, and a single number is not a useful summary of it; CEC2017 by contrast is reported with `± SD` throughout. Either give the SD (and say the pool is heterogeneous) or drop the CEC2011 mean. Minor, P3.

**Required additional analyses.** None. Every correction is a reporting correction against artefacts that already exist.

**Claims that must be narrowed.** The abstract's unattributed 2.48 (above).

**Recommendation:** *Minor revision.* **Scores.** Estimand/units 5 · Test validity 5 · Multiplicity 5 · Effect sizes 2 · Intervals 4 · Reporting consistency 2.

```text
ticket_id: S18-R4-01
review_stage: 18
reviewer_role: R4
severity: Major
priority: P1
confidence: Confirmed
issue_type: exhibit
manuscript_location: sections/performance.tex:361-373 (prose), :405-411, :422-427; Table 6 = tab:wilcoxon-holm, source papers/tables/T15.tex
claim_id_or_artifact_id: TAB-T15; M-027
concise_issue: The main inferential table has no A12 column, yet four passages of the surrounding prose describe and quote "the A12 column" of that table; the quoted A12 values appear in no exhibit in the paper or the supplement.
exact_evidence_or_observation: papers/tables/T15.tex header row is "$p$ & $p_{Holm}$ & $+$ & $\approx$ & $-$ & $r$ & Dec." in all four sub-panels, and the caption (performance.tex:381-383) correctly describes "the matched-pairs rank-biserial effect size $r$". The prose says: performance.tex:361-363 "Table~\ref{tab:wilcoxon-holm} reports the across-function Wilcoxon tests with Holm correction, win/tie/loss counts, $A_{12}$ effect sizes, and Holm decisions"; :365-367 "The $A_{12}$ column is computed over the 29 per-function means … distinct from the run-level $A_{12}$ …"; :221-226 "The tabulated $A_{12}$ is computed over the 29 per-function mean errors"; :409 "with $A_{12}$ of 0.490, 0.505, and 0.472"; :426 "the largest effect is against APGSK at $D = 100$ ($A_{12} = 0.712$)". Confirmed in the rendered PDF: extracted text shows "r Dec." as the table header (4 occurrences) while the body text at the same pages says "The A12 column is computed over the 29 …". I recomputed the quoted values from analysis/rel-2026-07-20-67d9345f9/cec2017/descriptive_stats_cec2017_D*.csv as across-function unpaired A12 on per-function means: 0.4905 (D30 vs eGSK), 0.5054 (D50), 0.4721 (D100), 0.7122 (D100 vs APGSK) - the numbers are CORRECT, they are simply not in any table.
root_cause: Ticket M-027 replaced the tabulated unpaired A12 with the aligned matched-pairs rank-biserial r in the exhibit and the caption, and the body prose was not updated with it.
scientific_or_editorial_justification: Section 10.11 and Gate M require that prose and exhibits refer to the same object. A referee following "the A12 column" finds an r column; a referee checking "A12 = 0.712" finds it nowhere. The paper simultaneously asserts that A12 IS tabulated (:221) and that r IS tabulated (:381) - an internal contradiction in the description of one table.
impact_on_validity_or_acceptance: No number is wrong and no inference changes. It is a first-page-of-the-review credibility hit on the manuscript's most-read table, and it makes four quantitative statements unverifiable from the paper.
required_correction: Rewrite the four passages to name the r column, and either (a) drop the A12 quotations, or (b) add A12 as an extra column (values already recomputable) or a supplement table, and cite that location.
acceptable_alternatives: Keep the A12 sentences but state explicitly that the across-function A12 values are reported in the text only and derived from the per-function means, with the derivation given.
additional_evidence_needed: none - values recomputed and confirmed.
dependencies: S18-R4-02 (the same values also lack a machine-readable row).
expected_improvement: Table 6 and its prose describe the same quantity; all four quoted effect sizes become traceable.
post_revision_verification: grep the rendered PDF for "A12"; every remaining occurrence must resolve to a location that actually prints A12.
status: open
```

```text
ticket_id: S18-R4-02
review_stage: 18
reviewer_role: R4
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: statistics
manuscript_location: sections/performance.tex:409, :426
claim_id_or_artifact_id: AN-EFF-2017-D30/D50/D100; primary_stats/statistical_results.csv
concise_issue: Four reported effect sizes have no machine-readable row in the frozen statistical-results table, contrary to the profile's requirement of one row per reported statistic.
exact_evidence_or_observation: Section 10.7 requires "a machine-readable row for every reported statistic (Appendix A.7 schema)". I searched papers/analysis/rel-2026-07-20-67d9345f9/primary_stats/statistical_results.csv (5,098 rows): every AN-EFF-2017-D* row has unit_of_analysis = "run" and metric = "vargha_delaney_a12" at per-function granularity; there is no row with the across-function A12 on per-function means. A search for effect_size beginning 7.122/0.712 returns zero rows; the 4.90/4.72/5.05-prefixed hits are run-level A12 for different comparator pairs (AN-EFF-2017-D30 dt-gsk vs egsk 4.901961e-01 and dt-gsk vs atmals-gsk 5.051903e-01, AN-EFF-2013-D30 dt-gsk vs agsk 4.721261e-01) - numerically adjacent but different statistics on a different unit, which makes the gap easy to miss and easy to mis-cite. The AN-PW-2017-D* rows record only the rank-biserial r and note "unpaired A12 companion in AN-EFF family".
root_cause: The across-function A12 is computed in the table/prose path (phase6_run_analysis.py) but never emitted as a statistical_results row.
scientific_or_editorial_justification: A reported statistic with no frozen row cannot be re-derived by the released pipeline and cannot be audited by the claims matrix; it is exactly the class of number the evidence lock exists to eliminate.
impact_on_validity_or_acceptance: Values are correct (independently recomputed), so no inference is affected; it is an evidence-traceability defect and a §10.7 non-conformance.
required_correction: Emit AN-EFF-*-FUNCLEVEL rows (unit_of_analysis = function, metric = vargha_delaney_a12_funclevel) for every comparator x dimension, or remove the four A12 quotations from the text.
acceptable_alternatives: Report the aligned rank-biserial r in those sentences instead - it already has frozen rows for every cell.
additional_evidence_needed: none (analysis-side emission only; no rerun of the optimizer, no new evidence release required if the analysis bundle is regenerated read-only from the same release).
dependencies: S18-R4-01.
expected_improvement: Restores one-row-per-statistic conformance.
post_revision_verification: Every numeric effect size in the rendered main text must match a row in statistical_results.csv on (analysis_id, dimension, algorithms, metric, unit_of_analysis).
status: open
```

```text
ticket_id: S18-R4-03
review_stage: 18
reviewer_role: R4
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: statistics
manuscript_location: sections/performance.tex:316-317 and caption :336-338 (CEC2017); :598-600 and :621-626 (CEC2013); :529-531 (CEC2011)
claim_id_or_artifact_id: AN-OMNI-2017-D10..D100; AN-OMNI-2013-D10/D30/D50; AN-OMNI-2011-NATIVE; M-026
concise_issue: The printed Friedman omnibus p-values mix the tie-corrected and tie-uncorrected forms across suites without disclosure, although the manuscript declares the tie-corrected statistic as primary.
exact_evidence_or_observation: The protocol paragraph (performance.tex:250-262) declares "the Friedman statistic uses the tie-corrected rank variance that underlies the Iman--Davenport F" and states the correction factors. Against friedman_ranks_*.csv: CEC2013 in-text values are the UNCORRECTED ones - printed 3.3e-7 / 2.2e-3 / 9.2e-6 at D10/D30/D50 (:622-626) versus corrected p_value 5.321814e-08 / 1.089721e-03 / 2.908506e-06 and p_value_uncorrected 3.264004e-07 / 2.242258e-03 / 9.212405e-06; the CEC2013 caption bound "p <= 2.3e-3" is likewise the uncorrected D30 value (corrected max 1.09e-3). CEC2017's bound "p <= 2.6e-8" (:317, :338) is the uncorrected D10 value 2.576884e-08 (corrected max 1.159690e-09). CEC2011 in contrast prints the CORRECTED pair (F = 4.266899 -> 4.27, p = 6.007858e-04 -> 6.0e-4; the uncorrected pair is 3.668834 / 2.160258e-03).
root_cause: M-026 added the tie correction to the analysis and released both forms, but the section prose was updated for CEC2011 and not for CEC2013/CEC2017.
scientific_or_editorial_justification: Every omnibus remains significant under either form, so no decision changes - but the manuscript argues in the same section that "the correction is material" and that both forms are released "so the correction can be checked directly". Printing the uncorrected values for one suite while declaring the corrected statistic primary is internally inconsistent and will be read as carelessness by any referee who opens friedman_ranks_cec2013_D30.csv.
impact_on_validity_or_acceptance: No inferential impact; a direct credibility hit in the statistics section, which is where this manuscript's main defence lives.
required_correction: Print the corrected p-values everywhere (or state explicitly, once, that the reported omnibus p is the conservative uncorrected value and that the corrected value is smaller), and make the two table-caption bounds consistent with whichever convention is chosen.
acceptable_alternatives: Report both, e.g. "p = 1.1e-3 (uncorrected 2.2e-3)".
additional_evidence_needed: none - both forms are already in the released CSVs.
dependencies: none
expected_improvement: One declared statistic, one printed statistic, across all three suites.
post_revision_verification: Every omnibus p in the rendered PDF must match the chosen column of friedman_ranks_<suite>_<dim>.csv.
status: open
```

---

## 7. R5 — Reproducibility reviewer

```text
reviewer_role: R5 (reproducibility)
expertise: artefact tracing, build determinism, evidence locks, gate coverage
confidence: Confirmed on the traces I ran
```

**Manuscript summary.** See EIC. I attempted to trace the headline results back to raw evidence and to rebuild the claim chain, treating every undocumented manual step as a finding.

**Overall assessment.** **Traceability from headline to release is excellent** and better than almost anything I see at this level: I resolved 2.48 → `friedman_ranks_cec2017_overall.csv` → `statistical_results.csv` rows carrying source paths, per-file SHA-256 source checksums, release id, script, command and commit; and the per-cell provenance chain is machine-validated by four independent gates that I ran and that all pass. The determinism vocabulary is properly stratified in §3.7 and correctly excludes the comparators.

Three defects survive. One is a **production regression introduced by a remediation fix and missed by every gate** (S18-R5-01). One is a **material reproducibility fact that the project has measured and the manuscript does not disclose** (S18-R5-02). The third is the freeze-anchor defect that the EIC seat also reached independently (S18-EIC-02) — I record my own concurrence rather than deferring to it.

**Strengths.** (1) Four read-only validators, all green, covering provenance, document consistency, cross-format parity (579 rows, 0 FAIL) and build hygiene. (2) The evidence-lock discipline holds under probing: `results/` staging is excluded and the analysis bundle records its own environment. (3) The post-freeze APGSK recovery is handled exactly as §10.7 requires — seed-deterministic cells acknowledged as recovered, the frozen function-level basis conservatively retained, nothing imputed.

**Major concerns.** S18-R5-01, S18-R5-02; concurrence with S18-EIC-02.

**Minor concerns.** `validate_build_hygiene.py` checks only unresolved references, control characters and retired content; nothing in the gate suite reads `Overfull \hbox` from the build logs or measures rendered geometry. That is why S18-R5-01 shipped.

**Required additional analyses.** None. Both major items are disclosure/production fixes.

**Recommendation:** *Minor revision.* **Scores.** Traceability 5 · Determinism claims 3 · Artefact completeness 4 · Gate coverage 3 · Production readiness 2.

```text
ticket_id: S18-R5-01
review_stage: 18
reviewer_role: R5
severity: Major
priority: P2
confidence: Confirmed
issue_type: exhibit
manuscript_location: papers/build_prompt_phases/phase_03/parameter_table_detail.tex (tab:parameters-detail, Table A19); rendered supplementary.pdf p.48
claim_id_or_artifact_id: ART-PARAMS detail; tickets N-013 and E-014
concise_issue: The supplement's frozen per-subsystem parameter table runs off the page: content extends past the right paper edge and cell text is cut off, a regression introduced by the N-013 fix and not caught by any gate.
exact_evidence_or_observation: supplementary.log line 1647: "Overfull \hbox (218.9852pt too wide) in paragraph at lines 19--68" inside build_prompt_phases/phase_03/parameter_table_detail.tex. Measured in the rendered PDF with PyMuPDF: page 48 of 61 has page width 595.28 pt, text right margin approx. 520.5 pt; 17 words extend past the margin and 7 words extend past the paper edge, e.g. 'stop' at x1 = 598.8, 'n' at 597.6, and three cells rendering as 'interaction_grap' (x1 = 596.4) and one as 'final_polish_sta' - i.e. \texttt{interaction_graph_min_dim=50} and the polish-start entry are truncated at the sheet boundary. Every other page of both PDFs is clean (max overshoot elsewhere 527.3 pt, inside the paper). The source uses `\begin{tabular}{lll}` with no fixed column widths. Ledger: N-013 closed by "the resizebox wrapper is removed; the 33 per-subsystem rows move to new parameter_table_detail.tex in Supplement S5", verified only for font size ("supplement detail 8.0pt"); E-014 closed with the recorded evidence "Supplement is overfull-clean: 0 Overfull, 8 Underfull", which is no longer true (1 Overfull of 218.99 pt).
root_cause: Removing \resizebox to satisfy the 8 pt table-text guidance (N-013) restored the table's natural width, which exceeds the supplement text block by ~219 pt; E-014's overfull count was measured before that change and never re-measured after it.
scientific_or_editorial_justification: Section 10.17.2/10.17.7 make an overflowing exhibit a ticket even when its content is correct, and here content is actually lost to the reader: the Notes column of the hash-frozen parameter table is unreadable, so the shipped configuration cannot be fully read from the supplement.
impact_on_validity_or_acceptance: No number is wrong. It is a visible production defect on a reproducibility-critical exhibit and a plausible desk-return trigger at MDPI.
required_correction: Re-lay Table A19 to fit the text block - p{} column widths with wrapping (preferred, keeps 8 pt), or landscape/sidewaystable, or split into two tables by subsystem. Re-render and re-measure; no parameter value may change.
acceptable_alternatives: Keep \small and set the Notes column as p{3.2cm} with \raggedright.
additional_evidence_needed: none
dependencies: The tabular is a frozen phase_03 artefact; the fix is a presentation change and must be re-hashed into the freeze manifest.
expected_improvement: Zero words past the text margin on every supplement page; the frozen parameters become fully legible.
post_revision_verification: (1) grep supplementary.log for "Overfull" -> 0; (2) re-measure every page with PyMuPDF: max word x1 <= right text margin; (3) reopen the DOCX and confirm the same table is a native w:tbl with no truncated cells. Add an "Overfull \hbox" assertion to validate_build_hygiene.py so this class cannot recur.
status: open
```

```text
ticket_id: S18-R5-02
review_stage: 18
reviewer_role: R5
severity: Major
priority: P1
confidence: Confirmed
issue_type: reproducibility
manuscript_location: sections/performance.tex:179-186; supplementary.tex:1216-1223 (sixth limitation); cf. sections/proposed_algorithm.tex:717-728
claim_id_or_artifact_id: RT-001 closure record; MT-11; CN-02
concise_issue: The project has measured, and the manuscript does not disclose, that the released comparator evidence is not bit-reproducible under the current code; and the experimental section's determinism sentence is scoped to "runs" in a paragraph that has just quantified over all seven optimizers.
exact_evidence_or_observation: papers/governance/remediation_2026_07_18/ticket_status.csv, ticket RT-001, residual_work field: "Option 2 (re-time the six comparators) was executed 2026-07-21 via scripts/retime_comparators.py (CEC2017, 51 runs, ~22h) but FAILED the determinism gate: 3,772 scientific-column diffs -- the 2026-07-08 comparator evidence (commit 31c5a04c4) is not bit-reproducible under current code (dc924dc48; version/FP drift amplified by chaotic search, worst for scipy/local-search atmals-gsk ~31% / egsk ~29%). Confirmed deterministic within-commit (fresh re-run == tonight 30/30), so NOT a bug." Neither the manuscript nor the supplement mentions this: the closest disclosure, supplementary.tex:1216-1223, stops at single-host/single-environment, uncaptured run-time NumPy/SciPy versions behind eGSK's SLSQP polish, and the single-thread precondition. Meanwhile performance.tex:169-180 reads "...bit-identical for all seven optimizers... Runs are budget-exact and repeat-identical", whereas proposed_algorithm.tex:727-728 correctly states "All three cover DT-GSK and this repository's pipeline only; no byte-stability claim is made for the comparator implementations."
root_cause: The finding arose during RT-001's abandoned Option 2 and was recorded in the ledger rather than routed into the manuscript's limitations.
scientific_or_editorial_justification: A reproducibility referee who checks out the shipped commit and re-runs a comparator will not reproduce the released comparator CSVs, and will find no statement in the paper that predicts this. The measured magnitude (about 29-31 percent of scientific columns for the two local-search comparators) is exactly the kind of material limitation the governing law says no presentation choice may conceal. The two sections' scopes must also agree.
impact_on_validity_or_acceptance: No reported number is affected - the frozen per-run CSVs are the record and the analysis re-derives from them deterministically. It is a disclosure and claim-scope defect, and an avoidable surprise for a referee.
required_correction: (1) Add one sentence to the sixth limitation: comparator evidence is deterministic within its producing commit but is not bit-reproducible across commits, with the measured scope. (2) Narrow performance.tex:179-186 explicitly ("DT-GSK runs are budget-exact and repeat-identical...") so it matches proposed_algorithm.tex:727-728.
acceptable_alternatives: State the producing commit per algorithm in the Data Availability statement or the release manifest, so cross-commit expectations are set correctly.
additional_evidence_needed: none - the measurement exists in the ledger; no rerun required.
dependencies: none
expected_improvement: The determinism claim is uniform across sections and the known limitation is on the record.
post_revision_verification: grep both rendered PDFs for "repeat-identical"/"byte-stable"; every occurrence must be scoped to DT-GSK or to the analysis pipeline, and the comparator cross-commit caveat must appear once in the limitations.
status: open
```

---

## 8. R6 — Skeptical domain reviewer

```text
reviewer_role: R6 (adversarial)
expertise: constructing the strongest defensible rejection argument
confidence: High
```

**Manuscript summary.** See EIC.

**The strongest rejection argument, stated in full.** *DT-GSK is a carefully engineered assembly of eight mechanisms, seven of which are acknowledged modifications of published antecedents, evaluated only against the family that its own senior author created, on a primary suite the configuration was selected against, with the one genuinely new idea in the paper measured and found to do nothing. What remains is a rank improvement of about half a rank unit over eGSK that is never statistically separable from eGSK at any dimension of the primary suite, that reverses at D=30 on two suites and loses with Holm significance on the third, and whose compute cost relative to the comparators the paper declines to report.* That is the case a hostile referee will make, and every clause of it is sourced from the manuscript itself.

**Now the honest rebuttal**, because a review that only prosecutes is not a review. (a) *Incremental assembly*: yes, and the paper says so — labels are per-mechanism, ARGP is the only claimed-not-found rule, and the C3 evaluation infrastructure is a real deliverable. (b) *Tuning or added computation*: the added computation is bookkeeping, not evaluations — the budget accounting is single-controller, single-counter, machine-checked, and the FES charge is identical across the panel. (c) *Benchmark used during development*: disclosed, labelled, and the two held-out suites are reported with their unfavourable cells. (d) *Adverse cases hidden*: no — the mandated unfavourable convergence case is discussed at length, the eGSK head-to-head losses are in the main text, and the robustness reversals are printed. (e) *Ablation insufficient*: the scaffold remove-one is conditional (ISM off in every cell) and the paper says so in a dedicated "What This Study Does Not Establish" subsection. (f) *Mechanism explanation post hoc*: the function-class reading is explicitly labelled "plausibility, not a measured component contribution". (g) *Simpler explanation*: the best simple alternative — that the standing is carried by the deterministic compass endgame alone — is *supported* by the supplement (the polish is the only isolated mechanism with a significant effect) and the paper concedes the basis question is unresolved.

So the rejection argument is strong but **not decisive**, and the manuscript has pre-empted most of it. The two clauses it has *not* neutralised are the compute-cost silence and the unquantified selection exposure.

**Strengths.** (1) The paper reports the mechanism that failed instead of dropping it — the single most credibility-positive decision in the package. (2) It refuses the field-wide claim explicitly and repeatedly. (3) It states that its own first places at D≥50 are "earned by consistency against the whole panel, not by dominating eGSK".

**Major concerns.** S18-R6-01 (compute cost); concurrence with S18-R3-01.

**Minor concerns.** "Deterministic refinement" in the title is doing more work than the evidence: the refinement is deterministic given the learned basis, but whether the *learned* basis beats coordinate axes is unresolved and the paper says so in three places. The title is defensible (determinism is a property of the operator, not a performance claim) — but expect a referee to press it.

**Required additional analyses.** One, and it is decision-relevant and cheap: a *basis contrast* for the polish (learned eigenbasis vs coordinate axes vs a matched random orthonormal basis at `D ∈ {50,100}`), which is the contrast that would convert C1 from "a deterministic endgame that helps" into "a *learned-basis* endgame that helps". I record this as **not required for this cycle** (it needs runs, and the no-rerun constraint stands) but as the highest-value next experiment; the manuscript already flags it as open in four places, which is the correct interim treatment.

**Claims that must be narrowed.** None beyond R4's; the paper's scoping is already tight.

**Recommendation:** *Minor revision* (I would not reject; I would press hard on cost and tuning). **Scores.** Novelty sufficiency 3 · Evidence sufficiency 4 · Adverse-case honesty 5 · Cost accounting 2 · Generalization 3.

```text
ticket_id: S18-R6-01
review_stage: 18
reviewer_role: R6
severity: Major
priority: P2
confidence: Confirmed
issue_type: evidence
manuscript_location: sections/performance.tex:735-784 (Section 4.5 and tab:runtime); supplementary.tex:1202-1212
claim_id_or_artifact_id: AN-COST-2017 (cost_cec2017.csv); LM-04; §10.13 "missing non-objective overhead analysis"
concise_issue: The manuscript reports no comparator wall-clock anywhere, so the reader cannot judge whether DT-GSK's rank advantage is bought with a compute premium - while the supplement simultaneously reports that one of DT-GSK's own subsystems costs 30-57 percent wall-time for no measurable accuracy return.
exact_evidence_or_observation: tab:runtime lists DT-GSK only (4.93 / 13.04 / 23.30 / 41.59 s at D = 10/30/50/100), with the caption stating "Comparator wall-clock was measured in a separate session and is not tabulated here, so no cross-algorithm runtime comparison is made". analysis/rel-2026-07-20-67d9345f9/cec2017/cost_cec2017.csv does contain every comparator cell (e.g. cec2017 D10: gsk 0.5545 s, atmals-gsk 1.4737 s, agsk 2.8211 s, egsk 3.3676 s, apgsk 3.9745 s, fdb-agsk 2.4043 s vs dt-gsk 4.93 s) but every row carries comparability = "NOT-COMPARABLE-ACROSS-ALGORITHMS (RT-001: panel not measured as one session…)". The ledger records that the remedy of re-timing the panel in one session was attempted on 2026-07-21 and abandoned because the comparator evidence is not bit-reproducible across commits. Supplement S6.5 reports the ISM's own wall-time cost as +57.3% (CEC2017 D50), +36.3% (D100) and +30.3% (CEC2013 D50) with A12 approx. 0.50 and Holm p = 0.98/0.90/0.65, i.e. "it costs a third to well over half again in wall-clock and buys no measurable accuracy return".
root_cause: A genuine measurement-comparability failure (RT-001) resolved by scope reduction rather than by re-measurement.
scientific_or_editorial_justification: Section 10.13 names missing non-objective overhead analysis as a hard rejection risk. The paper asks the reader to accept a rank improvement whose price is unstated, while itself demonstrating that at least one of its subsystems is pure overhead. The withheld numbers exist in the release and are order-of-magnitude relevant (the D10 cell alone spans 0.55 s to 4.93 s).
impact_on_validity_or_acceptance: No claim is falsified - the paper makes no runtime-superiority claim in either direction, which is the correct conservative posture. But a referee asking "what does this cost relative to the alternatives?" gets no answer, and the honest answer available from the release is unflattering.
required_correction: Report the comparator per-run wall-clock in the supplement as an explicitly NOT-COMPARABLE, session-qualified descriptive table (the qualification is already the CSV's own comparability string), so the order of magnitude is visible; keep the main-text no-comparison stance. Alternatively state, in the main text, the reason the comparison is withheld (separate sessions, comparator evidence not re-timable because it is not bit-reproducible across commits) rather than only that it is withheld.
acceptable_alternatives: Report an evaluation-normalized cost proxy that is machine-independent (e.g. non-objective operations per generation, or the D^2/D^3 term counts already derived in Section 3.8), which is comparable across sessions by construction.
additional_evidence_needed: none for the disclosure route - cost_cec2017.csv already holds all seven algorithms; a single-session re-timing would need runs and is out of scope for this cycle.
dependencies: RT-001 closure record; S18-R5-02 (same root cause: cross-commit non-reproducibility of comparator evidence).
expected_improvement: Closes the §10.13 overhead gap without any comparability overclaim.
post_revision_verification: The supplement must carry the seven-algorithm cost table with its comparability string reproduced verbatim in the caption, and the main text must state why no comparison is drawn.
status: open
```

---

## 9. Preserved disagreements (§3.5(5), §3.6(5))

Recorded, not resolved. No seat's position was altered.

| # | Disagreement | Positions |
|---|---|---|
| D-1 | Severity of the A12/`r` desync | **R4: Major, P1** — it is the main inferential table, four passages, and it makes quoted numbers unverifiable. **EIC: desk-risk item but Moderate in substance** — no number is wrong and one editing pass fixes it. **AE: Major** — symptom of a systemic artefact→prose drift, so severity should reflect the class, not the instance. *Unresolved; the higher severity (Major) is carried forward per evidence precedence, with the EIC's dissent visible.* |
| D-2 | Whether the compute-cost silence is a scientific or a presentational defect | **R6: Major scientific** (§10.13 named rejection risk). **R3: presentational** — the protocol charges an identical MaxFES to all seven, so the *scientific* comparison is budget-fair by construction and wall-clock is an engineering datum. **R5: reproducibility-adjacent** — the real defect is that the reason for withholding (cross-commit non-reproducibility) is undisclosed. *Unresolved; all three framings retained.* |
| D-3 | Whether the ISM should remain in the shipped algorithm at all | **R6:** a mechanism measured at +30–57% wall-time with a null effect is, on this evidence, a candidate for removal; keeping it while reporting it as null invites "why ship it?". **R2:** removal would change the frozen algorithm and would destroy C1's basis (the polish consumes the ISM eigenbasis); the paper's treatment — ship, disclose, isolate, report null — is the scientifically correct one. **R1:** concurs with R2 and adds that the null is itself the contribution. *Unresolved by design; no action requested — the code is byte-locked and this is a framing disagreement, not a defect.* |
| D-4 | Whether the advertised-null footprint needs reduction | **AE: yes, or an explicit ECB extension of §1.5.0-B(c).** **R1: no** — repetition of a negative result is the safe direction and reads as candour. **EIC: neutral**, but wants one recorded decision either way. *Unresolved; AE's ticket S18-AE-01 stands as an adjudication request, not a required edit.* |
| D-5 | Whether S18-R3-01 requires a number or an admission | **R3:** a number, or an explicit "not recorded". **R6:** an unquantified "several" is worse than no disclosure at all, because it signals the record exists and withholds it. **AE:** either is acceptable; the requirement is that the sentence stop being ambiguous. *Converging but not merged.* |

## 10. Consolidated finding index (this seat)

| Ticket | Sev | Pri | Conf | Owner seat | One line |
|---|---|---|---|---|---|
| S18-EIC-02 | Major | P1 | Confirmed | EIC (R5 concurs) | Freeze `anchor_commit` predates the bytes it hashes; Gate A traceability. |
| S18-R4-01 | Major | P1 | Confirmed | R4 | Prose cites an "A12 column" of a table that prints `r`; four quoted A12 values in no exhibit. |
| S18-R5-02 | Major | P1 | Confirmed | R5 | Comparator evidence measured non-reproducible across commits; undisclosed; §4 determinism sentence unscoped. |
| S18-R5-01 | Major | P2 | Confirmed | R5 | Supplement Table A19 runs off the paper edge; N-013/E-014 closed incompletely; no gate covers it. |
| S18-R3-01 | Major | P2 | Confirmed | R3 | Selection exposure disclosed as "several candidates", unquantified and unarchived. |
| S18-R6-01 | Major | P2 | Confirmed | R6 | No comparator wall-clock anywhere; §10.13 overhead gap. |
| S18-R4-03 | Moderate | P2 | Confirmed | R4 | CEC2013/CEC2017 omnibus p-values are the tie-*un*corrected form; CEC2011 is corrected. |
| S18-R4-02 | Moderate | P2 | Confirmed | R4 | Four reported A12 effect sizes have no `statistical_results.csv` row. |
| S18-R2-02 | Moderate | P2 | Confirmed | R2 | Budget-crossing verification claimed panel-wide; probe is one sphere cell at D=10. |
| S18-R1-01 | Moderate | P2 | High | R1 | Organising question is the one the evidence answers negatively. |
| S18-AE-01 | Moderate | P3 | High | AE | Advertised-null footprint exceeds the §10.9 narrowing's "brief" allowance; imports S6.6. |
| S18-EIC-01 | Moderate | P3 | Confirmed | EIC | Governing prompt §1.5/§10.7 snapshot is stale (73/80 vs 80/80; RT-001 disposition). |
| S18-R2-01 | Minor | P3 | High | R2 | C1's printed equation omits the compass schedule that defines the operator. |

**Nothing in this seat's findings requires a rerun, a new evidence release, or any change to the byte-locked optimizer core.** Eleven of thirteen are text or manifest edits; one (S18-R5-01) is a table re-lay; one (S18-R4-02) is an analysis-side emission that can be regenerated read-only from the existing release.
