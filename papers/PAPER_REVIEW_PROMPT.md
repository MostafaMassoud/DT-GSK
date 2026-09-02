<!--
  COMPREHENSIVE_Q1_Q2_MANUSCRIPT_REVIEW_PROMPT.md
  ================================================================
  Standalone post-completion framework for adversarial peer review,
  evidence verification, editorial assessment, revision control, and
  Q1/Q2 submission-readiness decisions.

  Intended use: only after a manuscript and its supporting package are
  substantially complete. This document reviews; it does not replace the
  governing manuscript-development framework or authorize fabrication of
  missing evidence.
-->

# Comprehensive Q1/Q2 Manuscript Review, Adversarial Peer-Review, and Submission-Readiness Prompt

> ### What this document is — please read before the rest
>
> This is an **internal, pre-submission quality-assurance instrument**. The
> authors wrote it to have their own manuscript attacked before a journal's
> reviewers saw it.
>
> **It is not the journal's peer review and did not substitute for it.** The
> phrase "adversarial peer-review" below describes the *posture* the instrument
> asks a reviewer to adopt — hostile, verification-first — not a formal review
> process or an editorial decision.
>
> **It directs auditing, never authorship.** A reviewer applying this document
> is required to re-read every printed statistic from the immutable analysis
> bundles rather than restate it from memory, to leave pre-registered wording
> untouched, and to have every finding independently verified against the live
> tree before it may be reported. It contains no instruction to write a claim, a
> result, or a conclusion, and no scientific content of the manuscript
> originates here.
>
> **Findings were adjudicated by the authors.** Applying this instrument
> produces a register of candidate findings; each was verified, and the authors
> decided what to act on. The registers are published beside this file in
> `papers/governance/` — including the findings that were *refuted* on
> verification, which is the point of recording them.
>
> **On AI assistance.** This instrument can be executed by a human team or with
> AI assistance; the authors used the latter. The manuscript's *Use of
> Generative Artificial Intelligence* statement is the authoritative disclosure
> of that use and its boundaries. Nothing in this document authorizes an AI
> system to generate scientific content, and §2 and §4 prohibit it explicitly.

## 0. Executive mandate

Act as a coordinated, multidisciplinary, independent review panel — organized as a *team of teams* of field-specialist expert teams (section 3) — evaluating a completed scholarly manuscript and its full supporting package before journal submission. **The declared submission target for this manuscript is a Q2 journal (MDPI *Algorithms*).** Hold the manuscript to the standard a strong Q2 venue applies, while aiming for publication quality competitive with higher-tier (Q1) venues wherever feasible; every corrective recommendation should be justified against Q2-journal best practice. Recognize that no review process can guarantee acceptance, quartile placement, or a particular editorial decision.

Your task is not to praise the manuscript, defend the authors, or perform a superficial language edit. Your task is to determine, with traceable evidence, whether the work is scientifically valid, sufficiently original, methodologically sound, statistically defensible, reproducible, clearly written, ethically compliant, correctly packaged, and realistically ready for submission.

The governing law is:

> **No claim may outrun its evidence, no conclusion may outrun its analysis, and no presentation choice may conceal a material limitation.**

Perform the review in independent stages, record every material concern as a structured ticket, simulate realistic editor and reviewer responses, reconcile disagreements through a documented consensus process, and apply strict quality gates. A manuscript may be classified as submission-ready only when every hard gate passes and no critical or major issue remains unresolved.

This is a **post-completion review prompt**. Do not begin by rewriting the paper. Audit the evidence, method, analyses, claims, and compliance first. Rewriting is permitted only after the scientific meaning of the relevant passage has been verified.

> **For this specific manuscript, read the dated current-status snapshot in §1.5 first.** It populates the input variables with current values, records which of the original objections are already **resolved and re-frozen** (so the panel verifies consistency instead of re-opening them), marks the honest ISM-isolation **null** as a standing finding to be checked for consistency rather than re-litigated, and scopes the remaining **author-side administrative gaps** so they are not mis-classified as scientific defects. The snapshot relaxes no gate.

---

## 1. Review invocation and input contract

### 1.1 Required review variables

At the beginning of the review, identify or populate the following variables. Never invent a missing value.

```text
REVIEW_ID:
REVIEW_DATE:
PROJECT_TITLE:
MANUSCRIPT_VERSION:
MANUSCRIPT_FILE_OR_TEXT:
SUPPLEMENTARY_FILE_OR_TEXT:
GOVERNING_PROTOCOL:
GOVERNANCE_AND_GATE_ARTIFACTS:
TARGET_JOURNAL:
TARGET_ARTICLE_TYPE:
TARGET_QUARTILE_STATUS: Q1 / Q2 / candidate not yet verified
AUTHOR_GUIDELINES_SOURCE:
REFERENCE_LIBRARY_OR_CLOSED_CORPUS:
RAW_OR_IMMUTABLE_EVIDENCE_ROOT:
DERIVED_ANALYSIS_BUNDLE:
SOURCE_CODE_AND_CONFIGURATION:
STATISTICAL_ANALYSIS_PLAN:
CLAIM_EVIDENCE_MATRIX:
FIGURE_AND_TABLE_SOURCES:
REPRODUCIBILITY_PACKAGE:
LATEX_SOURCE:
PDF_OUTPUT:
WORD_OUTPUT:
ADMINISTRATIVE_METADATA:
SPECIAL_PROJECT_CONSTRAINTS:
```

### 1.2 Minimum review package

The full review SHOULD receive, where applicable:

1. the main manuscript in an editable or parseable form;
2. the complete supplementary material;
3. the governing development prompt or protocol;
4. the producing project’s governance and gate artifacts (phase-gate register, project configuration, presentation-conventions specification, evidence cards, claims matrix, and reproducibility manifest); this project ships NO external-gate mapping — record its absence as expected, not as a missing input;
5. the target journal’s current official author instructions;
6. the bibliography and the underlying literature sources permitted by the project;
7. raw or immutable empirical evidence and its manifest;
8. analysis scripts, statistical outputs, and the frozen analysis plan;
9. method source code, configuration, and evaluator or data-processing code;
10. table and figure source data plus generator scripts;
11. reproducibility records, seeds, commands, environments, and checksums;
12. LaTeX/PDF and Microsoft Word versions when both are required; and
13. verified administrative declarations.

Missing administrative details do not stop scientific review. Missing evidence that affects a result, method, comparison, or conclusion blocks the affected gate.

### 1.3 Missing-input behavior

When an input is missing:

- record the exact missing item;
- identify the claims, sections, analyses, or deliverables it affects;
- continue every review task that remains valid;
- do not infer or fabricate the missing content;
- classify the affected gate as `BLOCKED`, not `PASS`;
- state the minimum evidence needed to unblock it; and
- distinguish `scientifically incomplete` from `scientifically complete but administratively blocked`.

### 1.4 Authority and precedence

Apply this precedence order unless the project explicitly defines a stricter one:

1. the latest explicit author or project requirement;
2. the governing development prompt and frozen protocol;
3. immutable empirical evidence and the exact code/configuration that produced it;
4. the preregistered or frozen analysis plan;
5. official current journal requirements for administrative and formatting matters;
6. verified literature sources;
7. generated tables, figures, and statistical reports;
8. manuscript prose;
9. comments, filenames, planning notes, and memory.

Never edit or reinterpret primary evidence merely to make it agree with the manuscript. Correct the derivative artifact or the claim.

---

## 1.5 Current-manuscript-status snapshot (current as of 2026-08-28)

> **HISTORICAL BANNER (superseded).** The 2026-07-25 CEC2013LSGO scope change this banner once announced was EXECUTED in full (five-suite manuscript, sections S7/S8, two additional evidence releases) and the freeze has since advanced to pass-27. Read the DEFINITIVE CURRENT STATE block below, then the newest layer (currently **section 1.5.0-Q**); sections 1.5.0-M/N/O record how the scope change was executed and are historical.

> ## DEFINITIVE CURRENT STATE — 2026-09-02 (pass-66 / v2.39; the manuscript is IN PRODUCTION at Algorithms: proofs returned, APC paid, pending publication. All revision batches APPLIED; resubmitted 2026-08-30, supplement re-sent 2026-09-01 and its Word twin 2026-09-02, both per editorial request. The published PDF prints DAS tag v2.37, so main.tex is deliberately NOT bumped past it) — read this first; it supersedes every layer below on any conflict
>
> This snapshot is maintained as dated provenance layers (§1.5.0 through §1.5.0-R). The single
> authoritative current state is stated here; the layers below are the dated record of how it was
> reached. Where any layer, §1.5.3 row, or §10.x profile item disagrees with this block, **this
> block governs**, and the newest relevant layer governs among the rest (currently **§1.5.0-R**).
>
> **Lifecycle:** submitted to *Algorithms* (MDPI) 2026-08-01 as pass-38 / tag **v2.13**, manuscript
> ID **algorithms-4507562** · decision **MAJOR REVISION** (two unsigned reviewers, ten points —
> dispositions and per-point verification duties in **§1.5.3-J**) · the revision is **COMPLETE and
> published to the public repository** (v2.14 → v2.39, including the round-two
> pass-49/50 batches: E5 boundary sensitivity, the canonical tie rule, the audit's P0/P1/P2
> corrections) but has **NOT yet been resubmitted through
> SuSy**. **The resubmission deadline is CONFIRMED as 2026-09-01** — also the author's planned
> date, so there is **zero slack**; a journal-offered extension was **DECLINED** (author,
> 2026-08-27). Do not propose asking for one.
>
> **Deliverables (all committed, deterministic, byte-verified):** `papers/DT-GSK.pdf` (**49 pp**) ·
> `papers/DT-GSK.docx` · `papers/supplementary.pdf` (**S1–S9, 83 pp**; S9.1 = basis isolation E1,
> S9.2 = matched population E2, S9.3 = tiered-vs-tier-constant E3, S9.4 = selected-constant
> sensitivity E4, S9.5 = dimension-boundary sensitivity E5; Tables
> **A43–A47**) · `papers/supplementary.docx` · `papers/cover_letter.pdf` · plus three **derived,
> gitignored** resubmission artifacts with generators: the marked main (50 pp) and marked
> supplementary manuscripts (read their page counts off the PDFs — they shift at every pass) — **preamble changes do not render**, so the retitle is
> invisible there; disclosed twice in the response letter — and `DT-GSK-change-register.pdf`
> (as-submitted vs as-revised, keyword-attributed to reviewer points — read the passage count off the register's own front page; redesigned layout with TOC, badges and color-coded panels), rebuilt by
> `papers/scripts/build_change_marked_pdf.py` / `build_change_register.py`.
>
> **Freeze:** pass-66, tag **v2.39** (v2.13 … v2.39 all resolve; the DAS names v2.13/v2.37), decision log through **D-0071**,
> change requests through **CR-0043**; next free ids **CR-0044 / D-0069** (verify free at apply
> time). `check_manifest` = **15/15 files + sources 2/2** — the `source_files` gate (pass-43)
> hashes `supplementary.tex` and `cover_letter.tex`, so an unbuilt source edit now fails the gate
> that pass-42 slipped through. Any manuscript edit voids the current pass → a new re-mint + a new superseding tag
> (every bump drags `CITATION.cff` — no leading `v` — `SUBMISSION_KIT.md`,
> `submission_package_manifest.json`, and the DAS tag in `main.tex`).
>
> **Post-cleanup state (2026-08-29, ordinary commits — freeze untouched):** the repository is
> **PRIVATE until upload day**; the response letter, both marked PDFs and the change register are
> untracked by design (D-0049) in `papers/submission/`; the private bundle's location, the two
> dangling-commit SHAs and their purge text now live only in the withheld
> `papers/review_2026_08_24/PRIVATE_OPS.md`; `results/_revision/` staging was quarantined outside
> the repository (promoted releases under `benchmarks/` are canonical). The cleanup commits were
> **left unpushed** — check `git status -sb` before trusting remote state.
>
> **Publication topology (SQUASH):** the public history is one commit per published state, so an
> `anchor_commit` in a governance record does **not** resolve on origin — `published_commit` does
> (disclosed in README). The never-push development-history branches were **bundled to
> the author's private history bundle outside the repository and deleted (2026-08-28)** — `main` is the
> only branch. The bundle carries the reviewer reports and copyrighted PDFs: **never fetch it
> into a repo with a public remote, never merge its refs, never copy it into the tree.** Withheld
> under **D-0049** (on disk, deliberately untracked): both reviewer reports, the point-by-point
> response, the decision e-mail, `AUTHOR_DATA_HANDOFF.md`. The pre-registration is **public on
> purpose** — it is what makes the adverse-wording-predates-outcomes claim checkable.
>
> **Evidence:** primary `rel-2026-07-20-67d9345f9` + `abl-rel-2026-07-20` + suite releases
> `lsgo-rel-2026-07-28-ff1a046ef` / `cec2020-rel-2026-07-29-5867abe1e` **+ the round-one revision
> release `rev-rel-2026-08-26-dd42d37eb`** (E1–E4, 32,451 runs) **+ the round-two release
> `rev2-rel-2026-08-28-203c78744`** (E5, 1,740 new runs; Amendment A4 registered before execution;
> each additive, non-superseding; the round-two analysis bundle carries E1–E3 under the canonical
> tie rule of Amendments A5–A6, one decision flip: E1 D100 now separated, Holm 0.0489) **+ the
> identity release `g1-rel-2026-08-28-65b3d39e6`** (D-0051 re-execution, promoted and cited at
> Table A45; the residual is a demonstrated build difference).
> `results/_g1_recheck/` is diagnostic staging —
> gitignored, cited nowhere; its promotion is **CLOSED** (author, 2026-08-28).
>
> **Scientific posture (do not drift):** two submitted claims were **falsified in revision and both
> corrections ship in the paper** (§1.5.3-J) — C1 is basis-neutral (*deterministic final polish*;
> the learned eigenbasis loses to plain coordinate axes at D = 50) and C2 is narrowed to D = 10/50
> (the 20 ≤ D < 50 tier is disclosed as mis-specified). **Zero occurrences of "adaptive control" or
> "eigenframe refinement" anywhere in the built artifacts.** The D = 50/100 rank claims are
> qualified as resting in part on the population rule (E2). ISM is a specified negative result.
> The aggregate rank is labelled descriptive. Any drift back toward the pre-revision story is a
> **critical integrity defect**. Line numbering is **OFF** (since 2026-07-24) and the `\texttt`
> count is **0** — the 07-23 "ACTIVE" notes in §1.5.0-J and §1.5.6 are historical record.
>
> **Verification rules for THIS instrument (new since 07-31):** extract rendered PDF text with
> **`pdftotext`, never pypdf** — pypdf silently drops the space between words and adjacent inline
> math and has already produced one spurious spacing defect (2026-08-28); confirm any suspected
> rendering defect with a second extractor AND the `.tex` source. Verify **HEAD blobs**, not only
> disk files (`git rev-parse HEAD:<path>` → `git cat-file -s`; Word-resave incidents
> `fa613cf`/`7804150`). DOCX epoch 1783641600 vs PDF 1783468800 + `FORCE_SOURCE_DATE=1` — a
> lingering env var silently breaks DOCX determinism. Author LaTeX/regex with exact-match file
> tools, never bash heredocs. Line endings are per file (this file is CRLF). Gate counts drift per
> pass — **run the gates; never assert a cached figure.**
>
> **CLOSED author decisions — do not re-raise, do not list as open:** the GitHub Support purge of
> the two off-ref commits (closed UNFILED, 2026-08-28); the deadline extension (declined); the
> D-0051 diagnostic promotion (closed); the larger CR-0015 disclosure (REJECTED on challenge —
> refutable from CR-0014/-0016/-0018; state the gap, never the causation); the A12 convention
> collision (closed — S6.5 per-function-averaged vs Table A43 pooled are two *named* statistics).
>
> **THE ONLY OPEN ITEMS ARE AUTHOR-SIDE AT THE PORTAL:** (1) resubmit through SuSy by
> **2026-09-01**; (2) re-enter the **new title and revised keywords** by hand — portal metadata
> does not update from the PDF, and the portal still showed the superseded title on 2026-08-27;
> (3) upload the two change documents and the response letter (which already names the unmarked
> retitle). Do NOT manufacture findings to fill a quota — the correct posture is independent
> verification of the closed items plus final resubmission polish.
>
> **Layer map (dated provenance, newest governs):** §1.5.0 (07-16, historical) · §1.5.0-B (07-18
> retitle) · §1.5.0-C (07-20 release ids) · §1.5.0-D (07-22/23 panel remediation) · §1.5.0-E/F/G/H/I
> (07-23 figure redesign, two ChatGPT rounds, two applied panels) · §1.5.0-J (07-24 R4 spec-fidelity) ·
> §1.5.0-K (07-24 portrait layout) · §1.5.0-L (07-24 in-venue positioning) · §1.5.0-M/N (07-25/28
> scope change, historical) · §1.5.0-O (07-29 five-suite executed) · §1.5.0-P (07-31 eight-seat
> panel + Amendment 3 + pass-26) · §1.5.0-Q (07-31 evening — pass-27, v2.2, repo split + hygiene) ·
> **§1.5.0-R (08-28 — submission → major revision → revision complete, then the
> same-day round-two batch E5/A4–A6 → pass-49 / v2.22; newest, governs)**.


This snapshot is reconciled to the 2026-07-23 state: the final retitle, the C1–C3 contribution restructure with **ISM demoted to a supporting mechanism**, the **oracle-study REMOVAL**, and the **completed** C006/M038 fix + 51-run evidence regeneration, all carried by the CURRENT release **`rel-2026-07-20-67d9345f9`** (primary; anchor commit `67d9345f9`) / **`abl-rel-2026-07-20`** (ablation), plus the M049 cross-format disposition and the docs consolidation. The manuscript is **BUILT and in final pre-submission remediation**, not from-scratch construction: the 80-ticket remediation ledger (`papers/governance/remediation_2026_07_18/ticket_status.csv`) stands at **80/80 TERMINAL** (70 `closed_verified` + 10 `superseded_with_evidence`; C-001 closed at `383d7896b`, 2026-07-21), **all quality gates are GREEN**, and **no ledger items remain open**. RT-001 is CLOSED under Decision 7 Option 3: the six-comparator re-timing was executed, FAILED the determinism gate (3,772 diffs), and Table 16 (`tab:runtime`) was narrowed to a DT-GSK-only single-session table — do not review the runtime table as in-progress or request a re-timing. The 2026-07-22 full-panel review (56 tickets, `papers/review_2026_07_22/issue_register.csv`) is remediated to completion: 47 actionable tickets closed, SE-006 rejected on evidence; the 2026-07-23 external ChatGPT review (16 items) is likewise closed (CR-001..013 fixed) — leaving **only the three author-side items SE-035, SE-049, and D-WORD-01** open. See **§1.5.0-F** for the newest governing layer and the DEFINITIVE CURRENT STATE block above for the single-source summary. §1.5.0 records the (now-historical) 2026-07-16 finalization campaign; §1.5.0-B records the 2026-07-18 structural editorial changes; **§1.5.0-C records the 2026-07-20 remediation status and still governs release ids; §1.5.0-D records the 2026-07-22/23 panel remediation and governs current phase and status.** All state current facts, not pending work; where an older row in §1.5.3 conflicts, §1.5.0 / §1.5.0-B / §1.5.0-C govern.

> **Read this before beginning.** This snapshot calibrates the review to the *current* state of this specific manuscript after (a) the A0–A4 submission-preparation program, (b) a **completed three-round adversarial convergence review** — Round 1 (six coordinated panels), then Rounds 2 and 3 (fresh independent panels) — (c) triage + remediation of a **130-ticket external ChatGPT Q2 review** whose genuinely-editable subset (~23 fixes over 6 batches) has been applied and re-frozen; (d) full remediation of a **second external ChatGPT deep-review (v2; 33 tickets)** — every editable method/stats/writing/production ticket (M003–M029) applied and re-frozen over 4 batches after verifying each code-level claim against the *current* frozen code, including **ISM-C001** (the subspace-LS description corrected to the **coordinate** local search that actually ran — Option A, **no rerun**) and **ISM-C002** (a benign, non-corrupting polish-incumbent staleness — no change needed); and (e) the **author-side sign-offs** (CRediT confirmed, GenAI version pinned to Claude Opus 4.8, funding confirmed, submission date set) — see §1.5.3 (last three rows) and §1.5.4.
>
> **Scope of THIS review (directives):** (i) Author-side submission metadata — the **DOI/Zenodo identifier, the ORCID iDs, and the corresponding-author institutional e-mail** — is **out of scope** (completed separately later); ignore it, raise no ticket, fail no gate (§1.5.4). (ii) **External, non-GSK baseline comparisons** (L-SHADE, CMA-ES, structure-learning/decomposition methods, etc.) are **out of scope for this cycle** and must **not** be treated as a missing requirement, fairness gap, or rejection risk; confine all comparator analysis to the seven-algorithm GSK family (§1.5.4). (iii) The **Author Contributions (CRediT)** section is **author-confirmed (2026-07-13)** and the **GenAI disclosure** now pins the tool version (**Claude Opus 4.8, Anthropic**), with funding confirmed and the submission date set; review these and the **code/data licenses** for professional presentation only — **not** as missing blockers (§1.5.4). (iv) **ISM-C001 is RESOLVED (Option A):** the frozen profile runs a **coordinate** local search at all tiers, and the manuscript now describes it as such — the ISM-block *subspace* variant is documented as implemented-but-not-enabled, and the ISM graph's two active consumers are the linkage crossover and the eigenframe polish. There is **no rerun**; the current `benchmarks/cec_reference_results` are the unchanged frozen base. **Do not re-raise the subspace-LS description as a method↔code mismatch** — verify the text matches the coordinate config (`build_pub_config`). ISM-C002 (one-generation-stale polish incumbent) is benign (greedy-accept + re-materialization prevent corruption) and needs no paper change. **All findings from all three rounds are resolved and re-frozen; the third round returned a "ready to submit" verdict with only author-side items open.** The manuscript is therefore **not an early draft**: it is at near-submission maturity, so the marginal value of a further review is **final publication polish, regression-checking the recent changes, and independent confirmation of the fixes** — not rediscovery of the original objections. This snapshot exists to prevent the panel from (a) re-opening issues already resolved and re-frozen, and (b) mis-classifying known author-side administrative gaps as scientific defects. It does **not** relax any gate: every standing finding below must still be **independently verified against the current build and evidence** — "resolved" means "verify it is resolved and consistent," never "take it on trust." Re-derive this snapshot from `papers/governance/decision_log.md` (entries D-0012…**D-0020**) and the `freeze_statement` chronology of `papers/governance/main_manuscript_freeze_manifest.json` — the manifest is now a FRESH mint at anchor `abd2fa2f2` whose `freeze_statement` chronicles the eleven 2026-07-22/23 re-freeze passes (through the ChatGPT CR round); the former append-only `*_refreeze` blocks were superseded by that re-mint — plus the ablation release manifest `benchmarks/cec_reference_results/_ablation/manifest.json` (resolve the CURRENT `release_id` from the manifest itself — now the 51-run `abl-rel-2026-07-20`; §1.5.0(g)/§1.5.0-C), before each new review round.

### 1.5.0 Completed finalization campaign (2026-07-15 → promoted 2026-07-16) — READ BEFORE ANYTHING BELOW

> **SUPERSEDED FOR RELEASE-ID AND STATUS PURPOSES BY §1.5.0-C (2026-07-20).** This
> section is a HISTORICAL record of the 2026-07-15/16 campaign, which minted
> `rel-2026-07-16-78f075cb0` / `abl-rel-2026-07-16`. Those ids have since been
> superseded by the CURRENT release **`rel-2026-07-20-67d9345f9`** (anchor
> `67d9345f9`) / **`abl-rel-2026-07-20`** (the post-M038 DT-GSK runtime-refresh re-mint,
> 2026-07-20 — §1.5.0-C; RT-001 itself was later CLOSED by narrowing `tab:runtime`
> to DT-GSK-only, §1.5.0-D). Every "the promoted release" reference in this section
> therefore resolves to the CURRENT id (via the manifest, per item (h)); the `07-16`
> ids below are the historical mint, not the current citation target.
>
> This section records a remediation session (triggered by a 97-finding external
> review) and the subsequent evidence-regeneration campaign, **now COMPLETE and
> promoted** to release `rel-2026-07-16-78f075cb0` / `abl-rel-2026-07-16`. Several
> rows in §1.5.3 still state the pre-campaign facts in their old form. **Where a
> row below conflicts with this section, this section governs.** Items (g)–(j)
> were the 2026-07-16 extension and are now finished (the releases are minted).

**(a) Two source defects were found and FIXED; the regeneration campaign is
COMPLETE AND PROMOTED (2026-07-16).** The finalized evidence is release `rel-2026-07-16-78f075cb0` (primary) + `abl-rel-2026-07-16` (ablation). Commit `af7efc534` corrects (1) **C006**
(= the "benign" ISM-C002 below): the final polish was entered with a stale
incumbent vector paired with a newer incumbent's fitness — reported results were
never corrupted (global-best shadow), but the polish, the one Holm-significant
component, ran handicapped; and (2) **M038**: the interaction graph imported a
non-existent module path, so every released run executed the un-accelerated
NumPy path (bit-identical results — verified — but the published **+54%/+37%
ISM wall-time overhead is the un-accelerated cost**; a pilot re-measure puts D50
near **+15%** [historical pilot estimate; the CURRENT backend-corrected overhead is
**+57.3% CEC2017 D50 / +36.3% D100 / +30.3% CEC2013 D50**, which became the published §S6.5 values upon the RT-001
closure — §1.5.0-C(d)]). Both are locked by new regression tests
(`tests/regression/test_dt_polish_incumbent_consistent.py`,
`test_dt_graph_backend_parity.py`) that fail on the pre-fix code. **Campaign
outcome (verify against the promoted release, do not assume):** all three
primary suites were rerun and row-count-verified (CEC2017/CEC2013 at 51 runs,
CEC2011 at 25), the 7-cell scaffold ablation and the 4-cell overlay isolation
were rerun at 51 runs, and the whole chain was finalized and **promoted to
`rel-2026-07-16-78f075cb0` / `abl-rel-2026-07-16`** (the `results/` staging that
fed it has since been removed — the promoted tree is the record). Every number
check therefore runs against the CURRENT bundle; resolve its id from the manifest
(h). The byte-surgical freeze-manifest re-freeze has since been COMPLETED and committed (anchor `abd2fa2f2`; `check_manifest` 15/15 — §1.5.0-D); historically it was the one step that could still be
pending — see FREEZE_STATE in §1.5.1 and item (j).

**(b) The oracle study (former §S6.7) is REMOVED from the paper — see §1.5.0-B(d).**
The 2026-07-15/16 campaign first re-scoped that subsection from "bounded" to
exploratory; on 2026-07-18 the author removed the whole subsection, both its tables,
its abstract sentence, its `_oracle` release, and its `dt2_oracle` lab code from the
manuscript and repository. Treat every "bounded null" / "oracle" / "headroom" /
"upper bound" instruction anywhere below as **RETIRED**: the manuscript now carries
only the ISM-isolation null (§S6.5), stated briefly. Any residual oracle reference is
a dangling-reference defect (§1.5.0-B(d)), not a scoping question.

**(c) The oracle release and lab code were REMOVED (2026-07-18) — see §1.5.0-B(d).**
The former `orc-rel-2026-07-14` release (`benchmarks/cec_reference_results/_oracle/`)
and the `benchmarks/dt2_oracle/` lab code were deleted from the repository when the
oracle study left the paper; git history is their audit record. The manuscript cites
neither. Do not audit `_oracle/` as paper evidence or expect it on disk.

**(d) The 21 cross-format validator FAILs are DISPOSITIONED (M049) — historical; the current gate reports 596 rows, FAIL=0.**
`papers/governance/cross_format_disposition.md`: every rendered Word-table number
reproduces from the semantic source at display precision (0 non-derivable cells);
the FAILs are a validator *expectation* defect ("DOCX = semantic full precision"
vs the actual display-rounded build), not content errors. Nothing was loosened.

**(e) Documentation was consolidated and verified against source.**
`docs/development/history/` and `docs/development/dt2/` are gone (contents merged
/ promoted; git retains history); new `docs/development/dt_gsk_core_reference.md`
and `evidence_rerun_runbook.md` are the live references. The algorithm guides and
all six getting-started guides were verified claim-by-claim against the code
(39 confirmed defects fixed — including both runbooks' instructions to run three
DELETED generators and a reference-regeneration recipe the runner now refuses).
The wrong expansion "DT-GSK (Interaction-Structure Memory GSK)" was corrected
repo-wide: **DT = Dimension-Tiered**; ISM names only the subsystem.

**(f) Counts that drifted:** the test suite now collects **488** (measured 2026-07-23; do not
hard-code); the abstract was **≈178 words** immediately after the 2026-07-18 oracle-sentence
removal (§1.5.0-B(e); verify against the built PDF). The title was changed again on
2026-07-18 to its FINAL form — **"DT-GSK: Dimension-Tiered Adaptive Configuration Selection and
Deterministic Refinement for Gaining-Sharing Knowledge Optimization"** (§1.5.0-B(a));
the intermediate title once quoted here, and the older "Oracle Upper Bound" title in
the §1.5.3 retitle row, are both historical.

**(g) The ablation AND overlay evidence is superseded by a 51-RUN re-mint
(supersedes every 25-run expectation below and in §10.10).** The scaffold
remove-one study (7 cells × D10/30/50/100) and the SGSM overlay isolation
(4 cells; CEC2017 D50/D100 + CEC2013 D50) were fully rerun at **51 runs per
cell** with the post-fix binary. On finalization (done 2026-07-16), `_ablation/manifest.json` was
re-minted as **`abl-rel-2026-07-16`** superseding `abl-rel-2026-07-13` (row-count
verification 51-based; provenance rewritten to the 51-run staging origins;
`kind:curve` taxonomy retained), and `ablation_results_manifest.json`
(phase_12) is re-minted with `runs: 51`. Exhibits SA01/SA02 and the abl-figure
regenerate with "51 runs" captions via `GSK_ABL_RUNS`. **Reviewers: expect 51
runs everywhere for ablation/overlay** (the "25 paired runs" phrases in the
1.5.3 rows are historical). The current 51-run §S6.5 isolation values are Holm
p = 0.983/0.897/0.647 (A₁₂ ≈ 0.51/0.50/0.42) for ISM and Holm p = 0.002/0.005/0.002
for the final polish — verify against the current release. (The former §S6.7 oracle
study, and any "orc-rel"/oracle/25-run-oracle language, are REMOVED — §1.5.0-B(d).)

**(h) Finalization is one checkpointed command chain; every pipeline tool is
release-parameterized — NEVER hardcode release ids when reviewing.**
`scripts/run_campaign.py` (resumable campaign driver; `--status` prints the
live completeness table) chains into `papers/scripts/finalize_evidence.py`
(phases P0–P12: preflight → audit-promotion [RETIRED 2026-07-18, no-op] →
flat-layout refresh → `_ablation` re-mint → `_oracle` integrity [no-op; oracle
removed] → strict-source stats →
`evidence_release_manifest.json` re-mint + phase6 bundle → `_paper_tables`
promotion + word sources → phase_12 + exhibits → all generators →
deterministic builds → gates → `results/_finalize/finalize_report.md`, the
old-vs-new headline diff). It minted **`rel-2026-07-16-78f075cb0`** superseding the
pre-fix `rel-2026-07-10-262fc16c9`, with comparator cells byte-verified unchanged. All
paper-pipeline tools take env overrides (`GSK_REL_ID`/`GSK_ANCHOR`,
`GSK_ABL_RUNS`/`GSK_ABL_RELID`, `GSK_OVL_SUITE`/`GSK_OVL_DIMS`/`GSK_OVL_RUNS`)
with historical ids as defaults in some tools (`generate_t16_bca.py` now defaults to the current release, re-pointed 2026-07-22). **Resolve the CURRENT primary release id
from `papers/governance/evidence_release_manifest.json` (`release_id` field)
and the current ablation id from `_ablation/manifest.json`; resolve the
analysis bundle as `papers/analysis/<that release_id>/`.** Any review step
that checks numbers against a hardcoded id from this document instead is
itself defective.

**(i) Claim-posture reframes (2026-07-16) — intentional, adversarially
verified, and PARED BACK; audit for evidence-match in BOTH directions.**
Wording-only edits (no number changed; BIND comments preserved) strengthened
the manuscript's posture. A 3-lens adversarial verification (25 findings)
then REVERTED the over-reaches, so the SURVIVING reframe set is exactly:
(1) C3 (the controlled family evaluation) and the Third limitation state the within-family panel as a **design
choice** — one code base / protocol / harness **confine implementation and
environment confounds to the disclosed exceptions** (the eGSK solver port and
the documented self-initialization), so deltas are attributable **chiefly**
to algorithmic differences, at the price of external calibration; (2) the
conclusions opener claims a **dimension-resolved characterization** rather
than uniform dominance; (3) the Eighth limitation leads with the
corroborative weight resting on **the two suites held out from configuration
selection** (the selection-scoped term — NOT "development-untouched" or
"independent", which the terminology glossary forbids) before disclosing
CEC2017's development exposure. **Deliberately REVERTED (do not expect, and
flag if resurrected): "bit-for-bit" re-derivability in the abstract/C3
(blocked wording — CN-02/MT-10 forbid comparator byte-stability claims; the
conditioned bit-for-bit language lives only where its single-threaded
precondition is stated); any "first direct isolation" priority claim
(vacuous — the mechanism exists only in this paper); "delimits this design
space" (a single-configuration null is not a mapped design space); the
abstract's panel descriptor without "GSK-family" (RS-01 makes the family
qualifier mandatory in every superiority sentence); and the Seventh
limitation's "internal-validity trade-off" clause (it pre-excused the COI
disclosure).** The abstract is therefore back at its pre-reframe text.
Reviewers: verify the surviving wordings match the evidence exactly and flag
drift in EITHER direction — silent claim upgrades AND needless re-hedging
both count as defects.

**(j) Items tracked-pending during the campaign — the finalization chain has since
run and promoted `rel-2026-07-16-78f075cb0`, so verify COMPLETION (not presence on a
tracker). All five tracked items, including the byte-surgical refreeze, are COMPLETE (§1.5.0-D) — confirm completion; historically the refreeze was the one that could still be
open (FREEZE_STATE, §1.5.1). Do NOT re-flag these as new findings:** (1) manuscript prose headline-number re-verification
against the new bundle (runbook §6: overall 2.48/7, per-dimension ranks,
17–7–0 tally, CEC2011 3.36 vs 2.52 Holm p=0.042, CEC2013 2.80, W-T-L records,
Nemenyi statements, runtime wording); (2) the byte-surgical freeze-manifest
refreeze (`papers/governance/_pending_refreeze.json` is written by the P11
gate); (3) 25→51 run-count updates in the hash-bound narrative docs
(`papers/build_prompt_phases/phase_12/ablation_findings.md`,
`_ablation/overlay/analysis/overlay_findings.md` + `overlay_validation.md`)
and in §S6.5/§S6.6 prose; (4) the X-ABL-02 `honesty` statement in
`_ablation/manifest.json` (marked "[25-run-era statement; re-evaluate…]") and
the pre-registered `correction_trigger_mapping` re-evaluation against the
51-run contrasts; (5) `BENCHMARK_EVIDENCE_INDEX.md` release-id refresh. Each
is on the finalize report's human-steps checklist; a reviewer's job is to
confirm completion or confirm tracking — re-discovering them is noise.

### 1.5.0-B Structural editorial changes (2026-07-18) — the retitle, the C1–C3 restructure with ISM demoted, and the oracle-study removal

> **Read this after §1.5.0 and before anything below.** On 2026-07-18 the author made three
> structural editorial decisions (applied to the sources and rebuilt into every artifact):
> the oracle study was **removed from the paper**, ISM was **demoted from a headline
> contribution to a supporting mechanism**, and the manuscript was **retitled**. §1.5.0 and
> §1.5.3 have been reconciled to these decisions; if any residual instruction anywhere still
> asks the panel to verify, reproduce, or scope the former §S6.7 oracle study, it is
> **RETIRED** — the study is not in the paper.

**(a) TITLE CHANGED (again — supersedes §1.5.0(d) and the §1.5.3 retitle row).** The
manuscript is now titled **"DT-GSK: Dimension-Tiered Adaptive Configuration Selection and Deterministic
Refinement for Gaining-Sharing Knowledge Optimization"** — it leads with the two supported
contributions (adaptive control = the dimension-tiered scaffold; deterministic refinement =
the eigenframe final polish) and no longer names ISM or the null. Updated in `main.tex`
(`\Title` + header comment), `supplementary.tex` (`\Title`), `cover_letter.tex`,
`cover_letter.md`; all artifacts rebuilt and text-verified (new title present, old absent).
There is no separate running-head/short-title macro. **Verify:** zero occurrences of
"Empirical Limits of Accepted-Move Interaction Learning" (and of the older "Oracle Upper
Bound" title) in any source or artifact.

**(b) CONTRIBUTIONS RESTRUCTURED C1–C4 → C1–C3; ISM DEMOTED.** The old headline **C1
(interaction-structure memory)** is no longer a contribution. Mapping: old C2 (eigenframe
final polish) → **new C1**; old C3 (dimension-tiered adaptive scaffold) → **new C2**; old
C4 (controlled, reproducible family evaluation) → **new C3**. The introduction's
contribution list has three bullets; the method-section headers are renumbered accordingly,
and the ISM section header now reads **"(Supporting Mechanism)"** (was "(Contribution
C1)"); the intro's stale "the memory that gives the proposed algorithm its name" sentence
is gone (DT = Dimension-Tiered). **Label caution:** any contribution label quoted in
§1.5.0/§1.5.3 (e.g. "C4 and the Third limitation") uses the OLD numbering.

**(c) ISM FRAMING — the null stays a null, stated briefly (author decision 2026-07-18,
Option (a)).** The author explicitly REJECTED reframing the null as "a small improvement"
after checking the isolation data (Δrank +0.05/+0.16/+0.20; Holm p 0.983/0.897/0.647;
A₁₂ 0.51/0.50 and **0.42 on CEC2013 D50 — trending AGAINST ISM**): calling that an
improvement would be selective reporting. The introduction now carries a short
supporting-component paragraph (final author-approved wording) whose operative sentences
are: ISM "provides candidate linkage blocks … and a candidate eigenbasis"; "the present
ablation does not establish a consistent standalone performance contribution"; ISM "is
therefore positioned as a **secondary exploratory mechanism** rather than as the primary
source of DT-GSK's performance standing"; and the "principal contributions remain the
dimension-tiered adaptive scaffold (C2), the deterministic final refinement stage (C1),
and the controlled, budget-fair evaluation framework (C3)." The abstract keeps ONE null
sentence ("A direct isolation finds no detectable standalone benefit …"). **Enforce:** any
sentence presenting ISM as a principal contribution, a performance driver, or a source of
improvement is a **critical** integrity defect; the §S6.5 isolation table remains the
evidence and is unchanged.

**(d) ORACLE STUDY REMOVED FROM THE PAPER (supersedes §1.5.0(b)/(c) and the §1.5.3 §S6.7
row).** Deleted from `supplementary.tex`: the whole "Controlled Oracle Study and Estimator
Fidelity" subsection (formerly §S6.7) with **both tables (formerly A20/A21)**, the S6
overview's mention of it, and the caveats subsection's dependent "deliberately not
regenerated" paragraph. Deleted from `main.tex`: the abstract's exploratory-mechanism
sentence. The supplement renumbered: **"Implementation Caveats" is now §S6.7** (formerly
§S6.8); §S6.5 (ISM-overlay isolation) and §S6.6 (by-class analysis) are unchanged. The
evidence release `orc-rel-2026-07-14` (`benchmarks/cec_reference_results/_oracle/`) and the
lab code `benchmarks/dt2_oracle/` were **removed from the repository (2026-07-18)**; the
paper cites neither. (The `_releases/` promotion-audit copies were removed the same day —
git history is the audit record.) **Do NOT:** expect or audit §S6.7 / Tables A20/A21;
treat the study's absence as missing evidence; re-introduce oracle content or
bound-language; or audit `_oracle/` as paper evidence. **Do:** flag ANY residual manuscript
reference to the removed study (`sec:supp:ablation:oracle`, `tab:oracle-upper`,
`tab:oracle-fidelity`, the word "oracle", "orc-rel") as a dangling-reference defect.
Source-verified at edit time: 0 "oracle" occurrences in `main.tex` + all `sections/*.tex`
+ `supplementary.tex`.

**(e) CONSEQUENTIAL WORDING.** Conclusions: "the headline mechanisms" → "the tier-gated
mechanisms" (consistency with the demotion). The abstract measured 178 words at that time (currently 204 rendered words on the built PDF — re-verify after any edit; the
oracle-sentence removal shortened it below the earlier 213); the bound result, both loss
caveats, Nemenyi-non-separability, the brief null, and panel scoping are retained —
re-verify their presence, and do not demand restoration of the old length.

**(f) ARTIFACTS REBUILT AND VERIFIED (2026-07-18).** From the edited sources: `DT-GSK.pdf`
(41 pp, clean compile), `DT-GSK.docx` (validator OK, `markers_left=0`), `supplementary.pdf`,
`supplementary.docx` (validator OK, `markers_left=0`), `cover_letter.pdf`, and both
regenerated pandoc shims. Text-extraction checks passed: 0 "oracle", new title present, old
title absent, three contribution labels, in every artifact.

**(g) REPOSITORY CONTEXT (not paper content).** The BLADE/BLADE-MAPS research line — a
post-freeze exploratory program that was never part of the manuscript — was fully removed
from the repository (commit `7dbb4bceb`); ignore any stale external notes that reference
it. The frozen optimizer core and all cited evidence releases are unchanged.

**(h) UPDATED VERIFICATION PRIORITIES for this pass (replaces §1.5.5 item 3; items
1–2b/4/6 stand).** (i) **Title-consistency sweep** — the new title, verbatim, across
`main.tex`, `supplementary.tex`, both cover letters, all rebuilt artifacts, and any
keyword/abbreviation list. (ii) **Contribution-renumber sweep** — no dangling "C4"; no
text that still calls ISM "C1" or a contribution; intro list ↔ method headers ↔
back-matter agree on C1=polish, C2=scaffold, C3=evaluation. (iii) **Dangling-reference
sweep** — zero references to the removed oracle labels; zero §S6.8 references (caveats is
now §S6.7); supplement numbering consistent. (iv) **ISM-framing sweep** — title →
abstract → intro → method → conclusions → §S6.5 as one chain: ISM never a principal
contribution, never an improvement; the null present, brief, and evidence-matched.
(v) **§10.9** — the SECOND supersession note governs (see §10.9): the null is still
advertised, now briefly; the favorable-result prohibition stays fully in force.

### 1.5.0-C Final pre-submission remediation status (2026-07-20) — GOVERNS RELEASE IDS; STATUS ITEMS SUPERSEDED BY §1.5.0-D

> **Read this after §1.5.0-B; it stated the 2026-07-20 facts and still governs the
> release ids.** Where §1.5.0 or a §1.5.3 row still presents the 2026-07-16 campaign's
> `rel-2026-07-16-78f075cb0` / `abl-rel-2026-07-16` as the promoted release, THIS
> section governs. Its STATUS items ((b)–(g)) were all resolved by 2026-07-23 and are
> restated below in their resolved form; §1.5.0-D is the governing status layer. The
> manuscript is **BUILT and submission-ready pending two author-side items**, so the
> review's marginal value is confirming the closed tickets and verifying the current
> build — the only open items are author-side SE-035, SE-049, and D-WORD-01 — not
> re-opening resolved objections.

**(a) CURRENT evidence releases (resolve from the manifests; do NOT hardcode).**
Primary **`rel-2026-07-20-67d9345f9`** (anchor commit `67d9345f9`; resolve from
`papers/governance/evidence_release_manifest.json` `release_id`); ablation
**`abl-rel-2026-07-20`** (resolve from `benchmarks/cec_reference_results/_ablation/manifest.json`
`release_id`, which records `supersedes_release: abl-rel-2026-07-16`); derived analysis
bundle **`papers/analysis/rel-2026-07-20-67d9345f9/`**. Provenance chain (historical —
do NOT cite the older ids as current): primary `rel-2026-07-10-262fc16c9` →
`rel-2026-07-16-78f075cb0` → `rel-2026-07-20-67d9345f9`; ablation `abl-rel-2026-07-13`
→ `abl-rel-2026-07-16` → `abl-rel-2026-07-20`. Every *scientific* column is byte-identical
across the 07-16 → 07-20 step; only `runtime_seconds` changed (item (d)).

**(b) Remediation ledger — 80/80 TERMINAL.** The 80-ticket ledger
`papers/governance/remediation_2026_07_18/ticket_status.csv` is fully terminal:
**70 `closed_verified` + 10 `superseded_with_evidence`**, zero open rows. C-001 closed
at `383d7896b` (2026-07-21). The historical 2026-07-20 reading of this section was
73/80 with seven pending; all seven have since closed — do not search for open ledger
items.

**(c) All quality gates GREEN (re-verified 2026-07-23) — verify against the current
build, do not assume.** The full roster, all expected to exit 0:
- `papers/scripts/validate_build_hygiene.py` — 0 unresolved refs / control chars / retired content;
- `papers/scripts/validate_cross_format_parity.py` — **0 FAIL across 596 rows** (PDF↔DOCX↔JSON);
- `papers/scripts/validate_provenance_claims.py` — prose matches the freeze manifests (hardened source+rendered; supports `--self-test`);
- `papers/scripts/validate_runtime_provenance.py` — runtime-table provenance;
- `papers/scripts/validate_document_consistency.py` — **exit 0** (any nonzero exit is a defect; suggested-reviewer names stay AUTHOR-supplied — MUST NOT be auto-generated, §1.5.4);
- `papers/scripts/validate_evidence_bindings.py` — every BIND comment resolves;
- `papers/scripts/validate_citation_controls.py` — **NEW (SE-025/D-0019)**: C1–C5 cross-checks over `citation_role_map.csv` / `citation_usage_map.csv` (119 data rows) / `word_citation_tag_map.csv`;
- `papers/scripts/validate_artifact_labels.py` — **NEW (SE-022)**: every `artifact_binding.csv` `manuscript_label` (61 rows) resolves to a defined label, traversing `\input` recursively;
- `papers/build_prompt_phases/phase_08/audit_manuscript.py` — exit 0 (its 2 `blocked_wording_hits` are negations of "state-of-the-art" — accepted);
- `papers/scripts/validate_docx.py <file>` — both DOCX **33 PASS / 0 FAIL**;
- `papers/scripts/check_manifest.py` — **15/15**, and the staged git index matches 15/15;
- environment attestation — green (M-030).

**(d) RT-001 — CLOSED by the opposite remedy (2026-07-21).** The six-comparator
re-timing (Option 2, `scripts/retime_comparators.py`) **was executed and FAILED the
determinism gate with 3,772 diffs** (≈ 1 ULP for gsk up to ~31% of runs for atmals-gsk),
so RT-001 was closed under **Decision 7 Option 3**: `tab:runtime` (Table 16) is narrowed
to a **DT-GSK-only, single-session** table. The body states explicitly that **no
comparator wall-clock is reported anywhere in the paper** and why (SE-044); runtime
pointers target §S6.5 with measurement provenance in §S6.7. The backend-corrected ISM
wall-time overheads (**+57.3% CEC2017 D50, +36.3% D100, +30.3% CEC2013 D50**) are the
published §S6.5 values. **Reviewers: `tab:runtime` is FINAL in its narrowed form —
verify the no-comparator-wall-clock statement and its rationale; do NOT request a
re-timing or a mixed-session comparison, and do NOT flag the DT-GSK-only scope as a
missing experiment (it is a recorded governance decision).**

**(e) Terminal freeze+commit sequence — DONE.** **C-008** and **C-001** are closed
(2026-07-21, commit `383d7896b`); the manifest has since been re-minted through the
**thirteen** 2026-07-22/23 remediation passes (committed anchor `abd2fa2f2`; **CRLF + 2-space,
edited in place** — never `read_text()`/`sed`, which normalize to LF and break the
hashes). `check_manifest.py` reports **15/15**, and the thirteenth- and fourteenth-pass
re-mints (§1.5.0-H) were **committed by the author on 2026-07-23**, so the staged index
matches. **Any `check_manifest` mismatch is a defect, not an administrative step.**

**(f) Remaining author-side items (the ONLY open items).** All ledger tickets are
terminal (item (b)). What survives is exactly: **SE-035** — the manuscript asserts
author confirmation of administrative items whose register rows are UNCONFIRMED
(suggested-reviewer names, JCR/Scopus quartile figures, benchmark-report access dates;
all AUTHOR-supplied, never auto-generated); **SE-049** — no similarity-screening record
(iThenticate/Turnitin; author-run); and **D-WORD-01** — the open-save-open pass in
desktop Microsoft Word. None blocks a scientific gate.

**(g) What this means for the review.** Confirm the closed tickets and the GREEN gates
against the CURRENT build; verify every headline number against
`papers/analysis/rel-2026-07-20-67d9345f9/` (§1.5.5 item 2a); treat the runtime table as
FINAL in its narrowed DT-GSK-only form (item (d)); and do NOT mis-classify the
author-side items (f) as scientific defects or desk-reject risks. Suggested-reviewer names, JCR/Scopus
quartiles, and benchmark access dates are author-supplied (§1.5.4) and must never be
auto-generated.

### 1.5.0-D Post-panel remediation completed (2026-07-22 → 2026-07-23) — GOVERNS CURRENT STATE; SUPERSEDES §1.5.0-C AND ALL EARLIER LAYERS WHERE THEY DISAGREE

> **Read this layer first.** The full PAPER_REVIEW_PROMPT panel review of 2026-07-22
> (artifacts in `papers/review_2026_07_22/`, register `issue_register.csv`, 56 tickets,
> initial weighted readiness 64.60/100) has been **remediated to completion**. Everything
> below reflects the shipped state as of 2026-07-23. Where §1.5.0-C, §1.5.0-B, §1.5.0,
> §10.x, or any stage instruction disagrees with this layer, **this layer governs.**

**(a) Register disposition — do not re-litigate closed tickets.** Of the 56 tickets:
6 were rejected by the panel's own Supervising Editor at filing; **47 are closed with
verified fixes**; **SE-006 was rejected here on a FLAWED test and later
re-confirmed and fixed — see §1.5.0-H.** (The rejection checked only `main.log`, which was
0 overfull; the panel review of 2026-07-23 found `supplementary.log` had a **218.99 pt
overfull** — Table A20 / `tab:parameters-detail` — clipping its Notes column. That table's
Notes column is now a wrapping `p{}` column and **both logs are 0 overfull**. Do not cite
"0 overfull" as a standing certification without re-running BOTH logs.) The remaining
author-side items are: **SE-035** (the manuscript asserts author confirmation
of administrative items whose register status is UNCONFIRMED — reviewer names, JCR/Scopus
figures, benchmark access dates) and **SE-049** (no similarity-screening record;
requires iThenticate/Turnitin, author-run). **SE-014 — formerly the register's only
`essential_before_submission` item — is CLOSED** (see (e)).

**(b) Statistics attribution is corrected; three post-outcome analysis changes are now
formally logged.** The manuscript no longer attributes the Wilcoxon p-values or the
Nemenyi critical difference to `scipy.stats`. The shipped text states: p-values come
from the in-repo `wilcoxon_paired` routine (normal approximation with continuity
correction), cross-checked against `scipy.stats.wilcoxon` in the released
`cross_check.json` (3 audited cells; statistic agreement to 1e-12; every α=0.05
decision agrees; disagreement would fail the release gate); the Nemenyi CD uses the
tabulated q_0.05(k=7)=2.949 of Demšar, not a SciPy call; SciPy is called directly only
for distribution tails. Decisions **D-0016..D-0018** in `decision_log.md` log
M-026 (tie-corrected Friedman; C≤1 so the correction can only increase the statistic;
both forms emitted), M-027 (matched-pairs rank-biserial r promoted to the tabulated
effect size; A12 demoted to descriptive companion), and M-028 (Holm family scope named)
as **post-outcome analysis changes** — disclosed, not presented as pre-registered.

**(c) Claims matrix realigned to the shipped contribution set.** The paper ships
**C1–C3 only** (C1 eigenframe polish; C2 dimension-tiered scaffold; C3 controlled
family evaluation). All five former "C4" references in `claims_evidence_matrix.csv`
are removed — the evaluation-integrity/RNG layer is infrastructure supporting C3, not a
numbered contribution. RS-08 now names the matched-pairs rank-biserial r as the
tabulated effect size. HL-01 (Highlights) is **NOT_APPLICABLE** — MDPI *Algorithms*
solicits no Highlights list and none is produced. Do not audit for a C4 or a Highlights
artifact.

**(d) Two evidence artifacts added WITHOUT any rerun** (both read/derive from the
promoted release; no optimizer executed). (1) **`papers/tables/SA03.tex`** +
`word_sources/SA03.json` → supplement table `tab:cec2013-pairwise`: the complete
six-comparator × three-dimension CEC2013 Wilcoxon–Holm matrix, typeset verbatim from
the released `wilcoxon_holm_cec2013_D{10,30,50}.csv`. **5 of 18 contrasts are
Holm-significant, all favoring DT-GSK** (GSK at all three dimensions; ATMALS-GSK and
eGSK at D=10). Win/tie/loss columns are deliberately absent — no released CEC2013
artifact records them, and the caption says so. (2)
**`papers/analysis/rel-2026-07-20-67d9345f9/cec2017/bca_rank_ci_cec2017.csv`** (28
rows): the BCa intervals on **Friedman mean ranks** behind Table `tab:bca-ci`
(T16_bca.tex), previously existing only inside typeset LaTeX. Estimand discipline: the
long-released `bca_ci_*.csv` files hold a **different quantity** (intervals on
per-function mean *differences*) — flag any text or reviewer note that conflates the
two. `generate_t16_bca.py` was re-pointed from the superseded rel-2026-07-16 default to
the promoted release **after verifying both releases reproduce the shipped
`T16_bca.tex` byte-identically**; no printed value moved.

**(e) Selection exposure is now quantified — by author attestation.** Decision
**D-0020**: **six** full-panel candidate configurations were examined during
development, including the one promoted. "Full panel" = run against all seven
algorithms on the full CEC2017 function set; excluded are smoke/debugging runs,
partial-function or partial-dimension pilots, single-component ablations and
sensitivity checks, failed configurations, and post-selection
validation/evidence-regeneration runs. Stated in `performance.tex` (one sentence) and
in the supplement's "Configuration Selection and Development Protocol" subsection
(full scope). **Provenance caveat, stated in the manuscript itself:** the figure is
author-attested and **not corroborated by any repository artifact** — the intermediate
candidates predate the immutable evidence release. A reviewer asking "show me the six"
gets that answer in writing; the correct adversarial question is whether the
*framing* is honest, not whether the artifacts exist (they do not, and the text says so).

**(f) Production state.** Page counts: **DT-GSK.pdf 41 pp · supplementary.pdf 63 pp
(12 true-landscape pages, CR-007) · cover_letter.pdf 2 pp**. MDPI submit-mode **line numbering is ACTIVE in both
documents** (the former `\let\linenumbers\relax` suppression is commented out; tested:
0 stray line-number tokens in `pdftotext` extraction, parity gate unaffected). The
internal page budget was formally raised by **CR-0008** (B1 hard cap 40 pp, B2 20,000
words; measured B1=37 pp after the 2026-07-23 figure redesign, B2≈19,536 full-token count; `page_budget.md` carries the
superseded banner; MDPI *Algorithms* imposes no venue limit). Word-vs-LaTeX geometry:
the DOCX text measure is **9.0% wider** (9,638 vs 8,845 twips) — an **approved,
recorded deviation** (`production_deviation_record.md` item D-4, with D-1 dated class
ACCEPTED, D-2 line numbering RESOLVED-RESTORED, D-3 suppressed submit-mode branding
ACCEPTED). `word_validation_report.md` **Section 9** carries the shipped hashes, object
counts, and the T1–T5 typographic specification (Palatino Linotype: Title 18 pt bold /
Author 11 pt bold / H1–H3 10 pt / Body 10 pt / Caption 9 pt). D-WORD-01 (open-save-open
in desktop Word) remains an author-side pre-submission step.

**(g) Gate roster — run ALL of these; all exit 0 at freeze.**
`validate_build_hygiene` · `validate_cross_format_parity` (**596 rows, FAIL=0**) ·
`validate_provenance_claims` (hardened source+rendered; supports `--self-test`) ·
`validate_runtime_provenance` · `validate_document_consistency` ·
`validate_evidence_bindings` · **`validate_citation_controls` (NEW — SE-025/D-0019:
cross-checks citation_role_map / citation_usage_map / word_citation_tag_map; C1–C5)** ·
**`validate_artifact_labels` (NEW — SE-022: every `artifact_binding.csv`
manuscript_label resolves to a defined label; traversal follows `\input` recursively)**
· `audit_manuscript` (phase_08; blocked_wording_hits=2 are both *negations* of
"state-of-the-art" — accepted) · `validate_docx.py <file>` (both DOCX **33 PASS / 0
FAIL**) · `check_manifest` (**15/15**, and the staged git index matches 15/15).
`artifact_binding.csv` now has **61 rows** (TAB-SA03 and AN-BCA-RANK-2017 added) and its
label column is fully repaired — the 2026-07-22 panel's finding of dangling labels is
FIXED and gated.

**(h) Writing state.** Sentence de-packing is complete for the length criterion:
**0 sentences above 55 words** in all five section files (the panel's figure of 98 and
an interim 70 were measurement artifacts — inline `%` comments merged adjacent
sentences; the corrected baseline was 61, now 0). Three residual ≥2-semicolon flags in
`performance.tex` are **accepted**: their semicolons separate parallel numeric list
items inside parentheses (comparator error values; per-dimension p / W-T-L triples)
where a comma would be ambiguous. The 13-step generation pipeline in
`proposed_algorithm.tex` is a true enumerated list. Do not re-open sentence length
without re-measuring with comment-aware tokenization.

**(i) Content corrections landed 2026-07-22/23 — verify consistency, do NOT re-raise:**
- GSK-RL (`nomer2021gskrl`) is characterised by its own tallies (14/5/10 at D=10;
  **16/4/9 at D=30** — better at 30), with instability localised to one function
  outside the training set. The former "unstable at D=30" adverse gloss is gone (SE-024).
- The novelty boundary is stated at ONE scope in all three places: the GSK-family
  variants cited in this paper (SE-024).
- The ISM null is a **failure to detect**, and the text states explicitly that no
  equivalence test or confidence bound was computed (SE-021); the intro no longer says
  "answers in the negative".
- The component-study omnibus is named as the tie-corrected Friedman **chi-square**
  approximation, not Iman–Davenport (SE-046); the r02 floor-sensitivity **surrogate** is
  disclosed in the main text (71,400 stored errors scanned; none in (0,1e-8)); the r05
  transition unit is stated (696 function×comparator×dimension cells, 51 paired runs).
- Runtime pointers target **S6.5** (measurement provenance in S6.7); the body states
  that **no comparator wall-clock is reported anywhere** and why (SE-044). RT-001 is
  CLOSED by the opposite remedy (re-timing ran, failed determinism with 3,772 diffs;
  Table 16 narrowed to DT-GSK-only). Do not request a re-timing.
- §S6.7 is **"Implementation Caveats"** — a reused number; the former oracle study is
  REMOVED and "oracle" occurs 0 times in both PDFs. A live S6.7 reference is correct.
- Reference 27's DOI is corrected (10.1137/S003614450242889); the Holm and Demšar note
  fields are self-contained (the MDPI .bst suppresses `url`, so "URL above"/"JSTOR
  record above" dangled) (SE-034).
- Figure 1's caption cites `mohamed2020gaining` as redrawn prior work; Figure 3's bars
  carry hatch patterns as a redundant non-colour channel; zero-height bars in the
  ablation rank-delta figure are marked with a caret and a "0" label (SE-045).
- `awad2016problem` has a citation_role_map row (B.4 suite definition);
  `literature_audit_report.md` carries a supersession banner — its "inadmissible"
  finding is historical (SE-025/D-0019).
- `project_configuration.md` is banner-corrected to the shipped release
  (rel-2026-07-20-67d9345f9) and the cleared cover-letter venue (MDPI *Algorithms*,
  R-0004 cleared 2026-07-11); `table_figure_source_map.csv` is RETIRED and
  `requirements_traceability_matrix.csv` HISTORICAL per `asset_map.md` (SE-022).

**(j) Updated adversarial priorities for the NEXT pass** (replaces §1.5.5's list where
they differ): (1) the six-candidate attestation — is the author-attested framing honest
and complete, and is the optimistic-selection discussion calibrated to n=6? (2) the
three accepted semicolon flags — genuinely list punctuation, or hiding clause joins?
(3) SA03 — re-derive the 5/18 Holm-significant count from the released CSVs; check the
caption's claim that no W/T/L exists in any released CEC2013 artifact; (4)
`bca_rank_ci_cec2017.csv` ↔ `T16_bca.tex` value agreement and the rank-vs-difference
estimand distinction anywhere intervals are discussed; (5) the D-4 Word-measure
deviation — is "approved deviation" defensible at a venue that re-typesets from source?
(6) SE-035/SE-049 as the only submission-gating author items; (7) freshly split
sentences — scan for orphaned fragments or broken cross-sentence references introduced
by the de-packing (two such fragments were caught and repaired during the pass; verify
none survive).

**(k) Do NOT expect or request:** a comparator re-timing (RT-001 closed); an oracle
study or §S6.7 oracle content; a Highlights list; a C4 contribution; suppressed line
numbers; the 34-page/12,000-word caps (superseded by CR-0008); a rerun of any
experiment or `finalize_evidence.py` (its P3 reruns 51 ablation cells); edits to the
byte-locked optimizer core (`_dt_core.py`, `_dt_subsystems/`, `_dt_rng.py`,
`_dt_profiles.py`, `dt_gsk.py` — "correct the paper, not the code").

### 1.5.0-E Figure-presentation redesign (2026-07-23) — GOVERNS FIGURE-QUALITY REVIEW; SUPERSEDES ANY EARLIER FIGURE STATE

> **All generated figures were redesigned on 2026-07-23** after reader feedback and a
> 9-agent visual audit of every shipped PNG. Where any earlier layer, stage, or §10
> profile item describes the figures, THIS layer is current. The redesign is
> **presentation-only**: every figure re-renders from the same released data; no number,
> rank, p-value, statistic, or claim changed, and the optimizer core was untouched.

**(a) One shared design module.** `papers/scripts/_fig_style.py` (NEW) is imported and
applied by every figure generator (`_convergence_common.py`, `generate_nemenyi_cd.py`,
`generate_rank_charts.py`, `generate_ablation_exhibits.py`, `generate_nlpsr_trajectory.py`).
It sets: the paper's **Palatino Linotype** typeface with STIX math (replacing matplotlib's
default DejaVu Sans — the single strongest "generated-chart" tell); a single hairline
**solid** grid well behind the data (the former dotted grid fought the dotted GSK curve);
soft dark-grey left/bottom spines only, outward ticks; frameless legends. Do NOT flag the
serif figure font, the absence of a top/right box, or the quiet grid as defects — they are
the deliberate house style.

**(b) No in-figure headline titles.** The duplicated bold internal titles were removed from
the rank-vs-dimension chart, both Friedman rank bar charts, the ablation delta bars, the
NLPSR schedule, and the Nemenyi panels (which keep only a small **regular-weight** dimension
tag, e.g. "D = 10"). The LaTeX caption is the single description of each figure. A missing
in-figure title is intended, not an omission.

**(c) Figure 4 (Nemenyi CD grid) was rebuilt.** The previous version overprinted its
full-parameter panel titles and x-labels across columns (unreadable). It is now a clean 2×2
of short D-tagged panels on a 6.1×4.6 in canvas, one bottom-row x-label, every shared
parameter (k, N, α, CD) stated once in the caption. DT-GSK is the black bar; comparators a
neutral slate.

**(d) Convergence figures.** A uniform log-y tick policy (`_tune_log_yticks`) replaces
matplotlib defaults, fixing the CEC2011 F3/F7 overprinting minor-label stacks, verbose
sub-decade labels, and single-labeled-tick axes. The "linear scale (negative objectives)"
note moved to the empty upper-right with a white backing box. Group-d supplement grids are
sized to their real 3-row height (the ~1.7 in blank band is gone). **Line weights were
thinned (final pass, 2026-07-23): comparators 1.1 pt, DT-GSK 1.65 pt (still 1.5× for
emphasis); comparators carry alpha 0.85 with rounded caps so overlapping curves layer
rather than tangle, DT-GSK opaque on top.** Greyscale safety: GSK darkened to #6E6E6E,
ATMALS-GSK to #B0568B, FDB-AGSK dash restructured, so the seven series separate in B/W.

**(e) Bar charts.** The grouped Friedman-rank bar chart is now clean **solid-colour** bars
with a thin edge — the dense colour+hatch encoding was retired as clutter. SE-045's
non-colour requirement is still met: the palette is Okabe-Ito (colour-blind-safe) and every
dimension group repeats the seven algorithms in the **fixed P1 order** (GSK, AGSK, APGSK,
FDB-AGSK, ATMALS-GSK, eGSK, DT-GSK), a positional greyscale channel documented in
`generate_rank_charts.py`. DT-GSK stays solid black. The **ablation** delta bars keep
distinct hatches (dark edge) because that supplement figure is greyscale-primary; its
zero line has axis room below for the negative deltas. Do NOT re-raise "Figure 3 is
colour-only" (SE-045) — position is the retained non-colour channel.

**(f) The two ISM-GSK legacy rows were removed from the supplement alias table**
(`tab:aliases`): **"ISM-GSK" now appears 0 times in any shipped source.** The ISM↔SGSM
component-alias rows remain, because those identifiers genuinely persist inside the released
CSVs and the algorithm freeze manifest (a reader auditing the release needs the mapping).
Do NOT flag a surviving ISM (component) mention as a stale method name — DT-GSK is the only
method name; ISM is the component name, deliberately retained.

**(g) Consequence.** The taller Figure 4 took the main PDF to **41 pp (B1 = 37)**, within
CR-0008's 40-pp cap. Every gate is re-verified green at this state (§1.5.0-D(g)).

### 1.5.0-F External ChatGPT review (2026-07-23) — CR-001..CR-013 remediated; GOVERNS METHOD-FIDELITY WORDING AND FIGURE-2

> A second external ChatGPT review of the shipped package returned a **D2 major-revision** decision
> with **16 register items (5 Major, 6 Moderate, 2 Minor, 3 author-blocked)** and **zero requests for
> a rerun, evidence regeneration, or any numerical change** — the reviewer explicitly confirmed the
> released data is settled. It also **withdrew its own biggest finding** (W-001: convergence "Mean
> error" is mislabeled) after verifying the plots genuinely show per-checkpoint means, and correctly
> rejected W-002..W-005 (external baselines, retiming, oracle restore, ISM-null-as-improvement). All
> **13 fixable items were verified against source and remediated on 2026-07-23**; where this layer
> disagrees with an earlier one on these loci, it governs.

**(a) Method-faithful wording (CR-001..005, the review's scientific core).**
- **CR-001** — the DT-GSK flowchart's selection box now reads **"greedily accept no-worse trials"**
  (the selector is `<=`; ties accepted), not "improving".
- **CR-002** — the ISM-update box and the high-visibility summary (`main.tex`) now say the graph learns
  from **"strictly improving accepted moves"** (code: `delta < 0.0`), not "accepted moves".
- **CR-003** — every "unchanged GSK core / operator core" instance is now **"unchanged GSK
  vector-update equations / operator"** (intro, related_work, proposed_algorithm x2, performance).
- **CR-004** — the GSK-RL paragraph is strictly factual: it reports 14/5/10 (D=10) and 16/4/9 (D=30)
  and localises the instability **to a single out-of-training function, not the D=30 panel** (whose
  tally is the stronger of the two). Do NOT re-raise "unstable at D=30".
- **CR-005** — "high-dimensional controllers / behaviour" is now **"upper-tier controllers" /
  "upper tested tiers (D=50, D=100)"** in the flowchart and four prose loci, consistent with the
  D=100 ceiling and the frozen terminology.
> NOTE ON FRAMING: the previous layers' "SE-024 fixed" claims were **incomplete, not regressions** —
> the prose and code were already correct; these CR items were **newly-surfaced loci** (the flowchart,
> a few summary lines, the public docs) that earlier passes had not touched. There was no reversion.

**(b) Figure 2 (DT-GSK flowchart), CR-006.** Redrawn: the DT-GSK-added boxes now carry a **light
shaded fill** (replacing the heavy bold outline), so the additions read as one group against the
plain GSK skeleton — cleaner hierarchy, less "wall of equal boxes". The caption says "light shaded
fill". Both the LaTeX source and the `dtgsk.json` Visio/DOCX twin were updated and the standalone PDF
recompiled. Do NOT re-raise the flowchart as over-dense.

**(c) Table typography.** **CR-008** — the NLPSR legend uses **NP_init** (manuscript notation), not
NP_0. **CR-009** — the Friedman rank table (T16) header is now compact **"10 / 30 / 50 / 100 /
Overall"** with the dimensions named in the caption, so the D100 cell can no longer wrap in the DOCX.

**(d) Supplement production.** **CR-007** — the 12 wide per-function tables are now **true landscape
pages** via `pdflscape` (each carries `/Rotate 90`), so readers no longer rotate the document
manually; the supplement is **63 pp** (was 61). **CR-010** — a `build_docx.py` post-pass gives every
table row `w:cantSplit` and every table's first row `w:tblHeader`, so dense pandoc-built tables no
longer split rows across a page break or lose their column headers on continuation pages. Both were
verified: cross-format parity holds (596 rows, 0 FAIL) and both DOCX validate 33 PASS / 0 FAIL.

**(e) Public documentation, CR-013.** `docs/algorithms/dt-gsk.md` and `docs/reference/glossary.md`
were synced to the manuscript's precise wording (strictly-improving ISM; upper-tier controllers).
The `ISM-GSK` name appears in the docs only as **historical rename provenance** ("renamed from
ISM-GSK, 2026-07-14"), which is correct; DT-GSK is the current name everywhere else.

**(f) DT-04 hard integrity rule — verified still satisfied.** DT-GSK is the only method name; ISM is
a supporting component (not C1/C2/C3); the isolation remains a failure to detect (never an
improvement); the oracle study stays removed. No CR touched any of this.

**(g) Remaining open — author-side only (unchanged).** **ADM-001** (SE-035 admin confirmations),
**ADM-002** (SE-049 similarity screening), **ADM-003** (D-WORD-01 desktop-Word open-save-open). None
is closable by editing; all three need the author.

### 1.5.0-G Second external ChatGPT review (2026-07-23, later) — completes the CR round; CORRECTS §1.5.0-F's premature "nothing open"

> A second external ChatGPT review (D2, 82.51/100, 10 tickets) of an **uploaded snapshot** returned a
> Critical "source/binary/freeze synchronization failure." Verified against the LIVE tree, that framing
> is a **packaging artifact of the uploaded ZIP**, not a defect here: `check_manifest.py` reports **15/15**
> and every gate is green. **However, the review correctly caught that §1.5.0-F's "Nothing else is open"
> was premature** — the CR round had fixed the prose and flowchart but **missed several table cells and
> docs lines**. Those residuals are now closed; this layer records the honest state.

**(a) METH-001 (Major) — RESOLVED.** The ISM "accepted moves" qualifier was missing from three tables
that the CR round did not touch: `tab:sgsm-mechanism` (caption + row 1), `tab:architecture` (row 4),
and `tab:taxonomy` (the "Update trigger" cell "on every accepted move"). All now read **"strictly
improving accepted moves"**, and the sgsm-mechanism caption carries the compact canonical eligibility
note: **ties do not update the ISM; DE-arm moves have update weight 0 in the frozen profile;
local-search displacements enter at weight 0.25** (code: `interaction_graph.py` skips non-positive
deltas; `_dt_core.py` passes `max(parent-child,0)`, `interaction_de_update_weight=0.0`,
`interaction_ls_update_weight=0.25`). The manuscript prose and the intro summary were already correct.

**(b) DOC-001 (Major) — RESOLVED.** `docs/algorithms/dt-gsk.md` and `docs/reference/glossary.md` had
residuals the previous docs pass missed: a genuine method error — selection described as **"only when
strictly better (unchanged GSK greedy selection)"**, corrected to **"no worse (`<=`; ties accepted)"**;
ISM eligibility "accepted moves" → **"strictly improving accepted moves"** with the weight note; ACE
credit "arms that produce accepted moves" → **"arms with the higher realised improvement (credit =
positive fitness delta)"**; and four residual **"high-D"** → **"upper-tier"**.

**(c) WORD-001 (Moderate) — RESOLVED (primary).** CR-007 rotated the wide tables in the PDF, but pandoc
dropped `pdflscape`, so the DOCX kept them portrait at ~4-5 pt. `build_docx.py` now has
`_landscape_wide_tables()`: every table with `>= 8` columns is bracketed by paragraph-level `w:sectPr`
breaks into a **true Word landscape section** (`w:pgSz w:orient="landscape"`, rotated margins), with the
caption pulled into the section — **13 landscape sections in the supplement DOCX, 1 in the main**
(the 15-column Wilcoxon-Holm table). Combined with the CR-010 `cantSplit`/repeat-header pass, the wide
tables are now readable and editable in Word. The one remaining sub-item — the 6-column dim-gating
table's role column packing tightly in Word — is a rendering nuance on a table that is fully legible in
the authoritative PDF; confirm it at the author-side D-WORD-01 step.

**(d) TERM-001 (Moderate) — mostly a stale-snapshot finding.** The claim of "High-D controllers" in
Table 4 row 7 and Table 5 is **NOT reproducible in the current source** (0 occurrences in any manuscript
`.tex`). One residual — `supplementary.tex` "high-dimension behavior" — was aligned to **"upper-tier
behavior"**.

**(e) AI-001 (Moderate) — [RECORD CORRECTED 2026-07-23, §1.5.0-I: this dismissal was FALSE.]**
This layer originally recorded: "the current cover letter has no GenAI paragraph at all". That was
wrong — `cover_letter.tex` **did** carry a GenAI paragraph (present since 2026-07-11), listing two
of the manuscript back-matter's three activity categories, so AI-001 was a REAL defect wrongly
dismissed. The third applied panel caught the false record (its gov seat traced the git history);
the letter now lists all three categories and the ISM sentence carries the strictly-improving
qualifier — see §1.5.0-I. Kept here uneuphemized as the layer's original error, per the
chronological-provenance convention.

**(f) PKG-001 / GOV-001 (Major) — the sync framing is a snapshot artifact; the underlying signal was
real and is now cleared.** The live tree is a single consistent 15/15 package. What was true: the
uploaded ZIP bundled mismatched source and artifact states, and §1.5.0-F over-claimed closure. Both are
now corrected — the residuals in (a)-(d) are fixed, all four deliverables were rebuilt, and the manifest
re-minted so the tree that is submitted is one coherent state. **Whatever is uploaded for the next review
must be a fresh export of THIS tree, not a re-bundled mix of older artifacts.**

**(g) Open items — still exactly three, all author-side.** ADM-001 = **SE-035** (admin confirmations),
ADM-002 = **SE-049** (similarity screening), ADM-003 = **D-WORD-01** (desktop-Word open-save-open, which
also confirms the new landscape sections and the dim-gating column). No editing can close these.

**(h) Lesson recorded.** A "fixed" wording ticket must be swept across **every surface** — prose,
flowchart, all table cells, captions, cover letter, and public docs — before it is marked closed. The
CR round's incompleteness (prose fixed, tables missed) is exactly this failure mode; the doc-to-code
semantic tests DOC-001 recommends would catch it mechanically and are worth adding.

### 1.5.0-H This prompt, APPLIED as an eight-seat expert panel (2026-07-23) — 9 findings closed, incl. two defects the CR rounds introduced; GOVERNS CURRENT STATE; newest

> After the deep-update above, the prompt was **applied to the live tree** as an eight-seat adversarial
> expert panel — **claims, method-vs-code, statistics, figures, cross-format, literature, writing,
> governance** — with every finding independently re-verified against live source before it was accepted
> (a workflow returned **CONFIRMED: 9 | REFUTED: 0**; the statistics, literature and writing seats
> returned clean). The panel's value was concrete: **two of the nine findings were defects the prior
> automated correction rounds had themselves introduced**, which only an independent adversarial pass
> caught. All nine are fixed; all four deliverables rebuilt; the manifest re-minted (thirteenth pass).

**(a) MAJOR — cross-format: the WORD-001 landscape fix was silently broken (self-introduced).**
`build_docx.py:_landscape_wide_tables._sectpr()` built the section's page size with
`pgsz = sp.find(qn("w:pgSz")) or etree.SubElement(sp, qn("w:pgSz"))`. An attribute-only lxml element is
**falsy**, so the `or` fallback **always appended a second `w:pgSz`** — schema-invalid section properties
that python-docx read back as **portrait**. So §1.5.0-G's "14 true Word landscape sections" was, in the
shipped DOCX, *portrait*. Fixed to mutate the existing element in place (`if pgsz is None: … = SubElement`);
verified python-docx now reads **13 supplement + 1 main** genuine landscape sections. (My first verification
was *also* wrong — `str(section.orientation).endswith("LANDSCAPE")` is always False because `str()` renders
`"LANDSCAPE (1)"`; the correct check is `== WD_ORIENT.LANDSCAPE`. The DOCX was fine; the check was buggy.)

**(b) MAJOR — governance: SE-006's "0 overfull hboxes" was false; a 219 pt clip had shipped.** The
SE-006 rejection (§1.5.0-D(a)) checked only `main.log` (genuinely 0 overfull) while `supplementary.log`
carried a **218.99 pt** Overfull `\hbox` in the per-subsystem parameter table (`tab:parameters-detail`,
`build_prompt_phases/phase_03/parameter_table_detail.tex`) — real content clipping at the page edge, a
desk-reject risk that had shipped undetected. **No gate caught it.** Remediation: (i) the table's three
columns are now wrapping `p{}` columns (3.0 / 5.4 / 4.8 cm), eliminating the 219 pt (and a residual
147 pt after a Notes-only first pass) portrait clip; (ii) the new CEC2013 pairwise matrix
(`tab:cec2013-pairwise`, Table SA03, 13 columns) is wrapped in `\resizebox{\textwidth}`, removing a 15 pt
overrun; (iii) a **permanent regression gate** was added to `validate_build_hygiene.py` — it now scans
**both** logs for `Overfull \hbox` beyond a **2 pt** tolerance and fails the build. Both logs are now
**0 pt over tolerance**. SE-006 is reclassified from "rejected" to **fixed**.

**(c) MODERATE — method-vs-code: the ISM eligibility note conflated two thresholds (self-introduced).**
A §1.5.0-G-era edit to `proposed_algorithm.tex` wrote the ISM eligibility as ties `|Δ| < 10^{-8}`, which
**conflates the win/tie/loss *reporting* band with the graph's own strict-positivity gate**. The code
updates the ISM only on `Δ < 0` (a strict improvement); `Δ ≤ 0` does not update, and the `10^{-8}` value
is the *reporting* tie rule, not the ISM gate. Corrected to state the strict-positivity gate explicitly
and disambiguate it from the reporting band.

**(d) MODERATE — claims: abstract Holm-significant-loss binding.** The abstract read "second behind eGSK
at D = 30 and on CEC2011 (a Holm-significant loss)", which let the parenthetical attach ambiguously.
Rebound to "second behind eGSK at D = 30, and second on CEC2011 where the loss is Holm-significant" — the
Holm-significant loss is now unambiguously the **CEC2011** result.

**(e) MINOR ×5 — swept across every surface (the §1.5.0-G(h) lesson, applied).** `docs/algorithms/dt-gsk.md`
and `docs/reference/glossary.md`: selection "strictly better" → **"no worse (`≤`; ties accepted)"**, the
mermaid accept node likewise; linkage blocks "contiguous" → **"arbitrary (non-contiguous)"**; ACE credit
"how many trials accepted" → **"summed fitness improvement (not an acceptance count)"**; ISM
"accepted moves" → **"strictly improving accepted moves"**. The flowchart twin
`figures/concept/flowchart_specs/dtgsk.json` and the dormant `sources/fig_architecture.drawio` /
phase-spec surfaces were synced to the same wording so no stale copy can resurface.

**(f) State after the panel.** Both LaTeX logs 0 overfull > 2 pt; all twelve gates exit 0 (build-hygiene
now including the overfull gate); cross-format parity **596 rows / 0 FAIL**; both DOCX **33 PASS / 0 FAIL**;
main **41 pp**, supplement **63 pp** (unchanged). Manifest re-minted as the **thirteenth pass**
(`generated_utc` 2026-07-23; 7 hashes updated: main.tex, proposed_algorithm.tex, both PDFs, both DOCX,
citation_usage_map.csv); `check_manifest.py` **15/15** on the working tree. Both DOCX were rebuilt at the
**canonical DOCX epoch `SOURCE_DATE_EPOCH=1783641600`** (the `_word_ooxml.DEFAULT_SOURCE_DATE_EPOCH`) —
this corrected a latent reproducibility slip in which the prior round's DOCX had inherited the *PDF* epoch
(1783468800) from the shell; content was unaffected (only docProps timestamps differ), and both DOCX now
reproduce byte-identically ×2 at the canonical epoch. All four artifacts verified reproducible: PDFs at
1783468800, DOCX at 1783641600. The thirteenth- and fourteenth-pass re-mints were subsequently
**committed by the author on 2026-07-23** (staged index 15/15).

**(g) Open items — still exactly three, all author-side.** **SE-035**, **SE-049**, **D-WORD-01** — unchanged
by this pass (no editing can close them). Nothing new was opened.

**(h) Lesson recorded.** An independent adversarial verification pass is worth running even when the tree
is "green": two of this round's nine findings were defects the automated CR rounds had *introduced* (the
pgSz duplication and the ISM `10^{-8}` conflation), and a third was a false all-clear (SE-006). None would
have surfaced from re-reading one's own edits. Every claimed layout fix should now be checked by a gate,
not by eye — which is why the overfull scan is now permanent.

### 1.5.0-I Third applied panel (2026-07-23, later) — 33 findings fixed incl. a FALSE §1.5.0-G(e) record; fifteenth-pass mint; GOVERNS CURRENT STATE; newest

> The prompt was applied a third time as the same eight-seat adversarially-verified panel over the
> live, committed tree: **33 CONFIRMED findings, 0 refuted** (1 major, 17 moderate, 15 minor). All 33
> are FIXED in the **fifteenth freeze pass**, whose `freeze_statement` entry carries the full item-by-item
> record; this layer summarizes what changes how the manuscript must now be reviewed.

**(a) MAJOR — the §1.5.0-G(e) dismissal of AI-001/METH-001 was FALSE (governance integrity).** The
cover letter **did** carry a GenAI paragraph (since 2026-07-11) listing two of the back-matter's three
activity categories; the "no GenAI paragraph at all" record could not be a stale-snapshot effect (gov
seat traced git history). Corrected: `cover_letter.tex`/`.md` now list **all three categories** and the
ISM sentence carries **"strictly improving"**; §1.5.0-G(e) carries a dated correction notice; the
manifest's twelfth-pass sentence stands as the historical record, corrected by the fifteenth-pass entry.

**(b) Claims/stats truth restored (no released number changed).** The early-stop parenthetical is
re-bound to its true axis (**AGSK 962 / APGSK 883** summed over suites; by suite **742 / 1,103** —
verified against the released per_run tables); the Section-4 opener mirrors the abstract's CEC2011
Holm-loss binding; the S6.5 overlay omnibus is relabeled the **classical (tie-uncorrected)** Friedman
chi-square (matching the released overlay JSONs; decisions unchanged); the Wilcoxon cross-check
sentence states what `cross_check.json` records (2 defined cells + 1 degenerate `p=1`); **T14 bounds
its D10 p as `<10^-4`** per the display policy (generator + word_sources + a tightly-scoped
parity-gate token); the SA03 caption discloses the post-tie effective *n*.

**(c) Method-spec corrections.** Archive capacity = **flat 200 at every D** (the `1.5·NP_init` sizing
is the inert no-cap fallback) on all three surfaces; the S5 escape paragraph is tier-qualified
(triple trigger at D≥20 / stall-only below; reseed 0.30·NP below D=50 / 0.10 above; jitter
`0.1·D^{-1/2}·span`; basin pool = 4× fall-through rows, D≥100 only); the α_psr note states the truth
(power-schedule-only, inert) — its first wording overflowed the table by 134 pt and was **caught by
the thirteenth-pass overfull gate**, then shortened.

**(d) Figures and DOCX production.** Every located log tick is now labeled (single-labeled axes
fixed); CEC2011 panels read **"Mean objective"**; S3 describes the four shipped sub-grids; NP_init
unified; the rank-trend caption names all seven algorithms; Figure 2's caption lists the coordinate
local search. The DOCX build restores **author-affiliation superscripts + the `*` correspondence
marker** (OMML `1,*` / `1` / `1,2,3`) and de-fuses the five bold run-in labels (Keywords + back-matter
statements).

**(e) Bibliography and writing.** `supplementary.bbl` regenerated — the SE-034 identifier notes are
finally inline in the supplement and **Hernández-Díaz** renders correctly everywhere; back-matter
supplement description re-bound to S6.5/S6.6/S6.7; heading punctuation unified to colons; unused
CI + W/T/L abbreviation rows dropped (W/T/L added to supplement Table A19, which uses it); nine
British spellings normalized; every pointer reads "Supplementary Materials".

**(f) Governance write-backs.** The 2026-07-22 review registers now record **48 rows resolved** with
evidence pointers (SE-035/SE-049 open; 5 accepted_risk untouched); `word_validation_report.md`
records the **executed** D-WORD-01 open-save (visual confirmation pending); the manifest's
`docx_note` contradiction is fixed and the **DOCX epoch 1783641600 is recorded in the manifest
itself**; the four stale "uncommitted pending commit" loci are retired.

**(g) State after the pass.** Supplement is now **64 pp** (S5 + SA03 wording growth; main 41 pp,
cover letter 2 pp). All five deliverables byte-reproducible ×2 at canonical epochs; parity **596
rows / 0 FAIL**; twelve gates green; fifteenth-pass mint **15/15** (uncommitted pending the author's
commit of this round). Open items: **SE-035**, **SE-049**, and the **D-WORD-01 visual confirmation**
of the reopened document — nothing else.

**(h) Lesson recorded.** Governance records are claims too: a review round that dismisses an external
finding must cite the evidence it checked (file + date), because §1.5.0-G(e) shows a dismissal can be
the defect. And the round's own gates catch the round's own regressions (the 134 pt α_psr overflow) —
keep fixing forward through gates, not by eye.

### 1.5.0-J ChatGPT R4 (live-tree D2 review) remediation (2026-07-24) — spec-fidelity pack fixed after code-trace; sixteenth-pass mint; GOVERNS CURRENT STATE; newest

> The fourth external review was the first to audit the **live D: tree** (not an uploaded ZIP), returning
> a 40-ticket D2. Its spec-fidelity findings were confirmed by an **eight-agent read-only code-trace of
> the byte-locked core** and every corrected sentence was sourced from the code, not the review. All
> code-fixable tickets are closed in the **sixteenth freeze pass**; the `freeze_statement` carries the
> item-by-item record.

**(a) Method-vs-code (the D2 core) — FIXED.** METH-001 (κ=0.45 is a *subspace-LS* gate, not a coordinate-LS
admission gate — the coordinate branch has none); METH-003 (the D≥100 upper-tier controllers are
**cross-cutting**, acting at population-reduction / trial-construction / acceptance / escape plus a
budget-ROI gate *on* the LS — not one post-LS stage; fixed in Algorithm 1, Figure 2 + re-rendered PDF,
the execution-order list, and both twins); METH-004 (the two event-driven ISM transitions — LS-success
injection at decay 1, post-restart halving + 5-gen cooldown — now documented); METH-005 (the **rendered
equations were already correct**; the errors were in `equation_registry.csv` — E9's `r_rst`→`r_c`,
E10's confidence fold-in removed — so the CSV was fixed, NOT the equations); METH-006 (the lumped
controller row expanded to explicit A1/A2/FC4 + restart-response rows, every scalar verified against
`_dt_profiles.py`); SPEC-001/002/003/004/005/006 all corrected from code.

**(b) STAT-001 — verified a FALSE ALARM in its strong form.** `build_docx` renders the `tab:bca-ci` DOCX
table from the **same frozen rank-CI `.tex`** as the PDF (parity compares DOCX↔.tex), so both formats
show the same estimand; the mean-difference JSON is a machine-readable companion whose stale "the .tex
is unused" note was corrected. No PDF/DOCX estimand mismatch ships.

**(c) Reproducibility — REPRO-001 FIXED at the root.** `check_manifest.py` now validates the recorded
**`bytes`** as well as the SHA-256 (surgical re-mints had updated hashes but not sizes — the actual
defect); this pass refreshed every tracked file's bytes, and the `reproducibility_manifest.json` +
`submission_package_manifest.json` deliverable hashes/bytes/pages were re-minted to the current
41/64-pp deliverables. SOFT-001: all five repo-wide Ruff errors fixed.

**(d) Presentation / scope — done, author-revertable.** Abstract trimmed to ~200 rendered words
(COMP-002). **C2 narrowed (STUDY-003):** it now states the dimension-tiering itself is not isolated by a
uniform-vs-tiered contrast, so C2 is the integrated frozen scaffold's performance as a package, not
evidence that tiering is individually causal — narrowing chosen over a new experiment (no rerun).

**(e) State.** Supplement **64 pp**, main **41 pp**, cover 2 pp; all five deliverables byte-reproducible
×2 at canonical epochs; cross-format parity **599 rows / 0 FAIL**; twelve gates green ×2 (idempotent);
`check_manifest` **15/15** on hashes AND bytes. No released number, rank, p-value, equation, or
α = 0.05 decision changed; optimizer core untouched; no experiment rerun.

**(f) Author-side remainder (ChatGPT R4).** *(Historical ticket text; superseded by §1.5.0-L(e) —
ATTEST-001 and REPRO-002 are now CLOSED, and COMP-001's packaging model changed.)* **ATTEST-001** and
the full-suite rerun need a *clean, uncontended* test run (the LSGO campaign was consuming CPU);
**REPRO-002** runbook refresh; **COMP-001** ≤120 MB submission bundle + persistent evidence deposition
(DOI); **PKG-003** commit + tag a clean release (the "dirty tree" is precisely this uncommitted round
plus the LSGO runner-diagnostic edits). Plus the standing **SE-035 / SE-049 / D-WORD-01**.

### 1.5.0-K Portrait-only layout + DOCX page numbers (2026-07-24, author request) — seventeenth–twentieth-pass mints; GOVERNS LAYOUT

> Author layout request: **every page vertical (portrait)**, **page numbers in the DOCX** like the PDF,
> **no blank pages**, and — final form — the wide comparison tables laid out **side-by-side** like the
> ATMALS-GSK reference (its Table 7). Done for both formats without changing any value.

**(a) Wide tables → portrait, side-by-side method groups.** The twelve landscape supplement pages (the
wide per-function head-to-head tables T01/T02–T05/T11–T13 and the panel tables T07–T10) are now portrait.
Each head-to-head table is a **single 11-column table** with the two methods in adjacent column groups —
`Function | GSK {Best·Median·Worst·Mean·SD} | DT-GSK (Proposed) {Best·Median·Worst·Mean·SD}` — **one
header carrying all five statistics** under each method (`\cmidrule`-separated), the better Mean per
function in bold, values in **E-notation** (`6.40E+02` — the same format the panel tables T07–T10 and the
Wilcoxon/Friedman tables already use). Each 11-column table is wrapped in `\resizebox{\textwidth}`
(portrait shrink-to-fit — the author's choice over landscape); T07–T10 likewise. `generate_word_sources`
emits the matching flat 11-column side-by-side DOCX source, and `build_docx` renders one grouped 11-column
Word table per suite, so cross-format parity is **1:1** and PDF and DOCX show identical E-notation. All
twelve `\begin{landscape}` wrappers were removed (now `[p]` float pages, so no table interrupts a
paragraph). *(Iterations of the same author request, each replaced on feedback: a column-split header
showing three of five statistics [seventeenth pass], an algorithm-per-row 7-column table [eighteenth],
the side-by-side layout [nineteenth, in the interim `$m \times 10^{e}$` form], and finally the switch to
E-notation for consistency with the other tables [twentieth].)*

**(b) DOCX portrait + page numbers + no blank pages.** `build_docx` **no longer emits landscape sections**
(removing the section breaks that produced the blank pages Word showed), and a new `_add_page_numbers()`
adds a centered **PAGE-field footer to every section**. The wide tables render portrait at the
column-count-stepped font (`_table_font_halfpt`).

**(c) Gate.** Cells are plain **E-notation** text, which `detex`/`canon_times` canonicalize directly. (The
nineteenth pass's `_fold_times` — added to fold the interim `$m \times 10^{e}$` form to sci-notation
before `detex` mangled `\times`→"imes" — is retained but now inert, since no table uses that form; the
trailing-empty-cell strip for column-split rows is likewise retained.)

**(d) State.** Supplement **56 pp** (was 60 — the side-by-side form is one row per function, not two),
main 41 pp, cover 2 pp; **0 landscape pages/sections** in any deliverable; DOCX page-numbered on every
page; all five byte-reproducible ×2; parity **599 rows / 0 FAIL**; twelve gates green; `check_manifest`
**15/15** (hashes + bytes; all three manifests re-minted). Presentation-only — no released number, rank,
p-value, equation, or claim changed; optimizer core and benchmark evidence untouched.

### 1.5.0-L Comparative positioning vs the in-venue precedent (2026-07-24) — twenty-first-pass mint; GOVERNS CURRENT STATE; newest

> A multi-seat comparative review against **ATMALS-GSK (Algorithms 2025, 18, 398)** — the same journal,
> same family, GSK-originator co-authored, therefore the precedent a referee is likeliest to hold in mind.
> Nine framing corrections, **all text-only; no released number changed**.

**(a) What the comparison established.** DT-GSK already leads the precedent on rigour and reproducibility:
ATMALS reports **uncorrected** per-dimension Wilcoxon (its own AGSK row is p = 0.44, n.s.), presents
per-function **win counts as "success ratios"** (75–78%), has **no post-hoc CD test and no effect sizes**,
**no complexity or runtime analysis at all**, an ablation at **D = 30 only**, and a Data Availability
Statement of *"available on request from the authors"*. It leads us on exactly one axis: **comparator
breadth** (5 GSK + 5 non-GSK vs our 6 GSK-family). The risk was therefore **under-selling**, not
under-delivering — so the fixes make existing rigour legible rather than adding claims.

**(b) The nine corrections.** P2 re-execution provenance (every panel member re-run in-repo, not quoted)
into the abstract + C3 · P10 three suites named in C3 · P6 the orthogonal-axis contrast (family adapts
parameter *values*; DT-GSK resolves control *by dimension*) · P3/P4 an explicit statistical-protocol
paragraph (Holm-within-dimension, tie-corrected Friedman, Nemenyi, mandatory effect size) plus two
reporting rules — no significance claim rests on an uncorrected *p*, and W/T/L counts are descriptive,
never significance · P1 the scope trade stated affirmatively in Limitations (breadth traded for internal
validity) · P7 reporting the null + the mid-dimension second place + the Holm-significant CEC2011 loss
named as part of what C3 is for (**the null stays a null**) · P8 remove-one design rationale at the
existing neutral pointer (**no ablation finding added to the main text**, §10.9 respected) · P9 runtime
identified as the empirical counterpart of the asymptotic model.

**(c) Deliberately NOT done.** External non-GSK baselines (author decision — out of scope this cycle;
mitigated by P1) and adaptation-trajectory figures (the ATMALS Figs 7/8/10/11 analogue): `gen_logs` hold
**only checkpoint errors**, no operator or tier state, so that figure **cannot** be built from the frozen
release and would require an instrumented rerun.

**(d) State.** Main **41 pp (unchanged)**, supplement 56 pp, cover 2 pp; parity **601 rows / 0 FAIL**
(two rows added by the new paragraph); 0 pt overfull; `validate_docx` 33/0 both; `check_manifest`
**15/15**; all deliverables byte-reproducible ×2. `supplementary.docx` was found re-written by a
desktop-Word open-save and regenerated to the deterministic build before minting.

**(e) Standing submission items — closures and the revised packaging model (2026-07-24).**

* **ATTEST-001 — CLOSED.** Full suite **488 passed / 0 failed, run twice** (233 s / 227 s) with the two
  runs agreeing, declared envelope OK (py 3.10.11, numpy 2.2.6, scipy 1.15.3, pandas 2.3.3,
  matplotlib 3.10.8), all six release gates exit 0, `green=True`. Recorded in
  `papers/governance/environment_attestation/attestation.json`. The machine was **not** idle (the LSGO
  campaign was running); correctness is not CPU-dependent and the suite agreed across runs, so the
  result stands — only the recorded durations are inflated.
* **REPRO-002 — CLOSED.** Seven documentation files still described **RT-001** as a live blocker / IN
  PROGRESS and instructed readers to run `scripts/retime_comparators.py`, when RT-001 had been executed,
  had **failed its determinism gate (3,772 differing rows)**, was not adopted, and was superseded by
  narrowing `tab:runtime` to DT-GSK-only single-session. All seven corrected; generated HTML docs
  regenerated (55 pages).
* **COMP-001 — packaging model REVISED by the author (this supersedes the ≤120 MB "submission bundle"
  framing in §1.5.0-K(f)).** Three distinct channels, and reviewers must not conflate them:
  1. **Journal submission** — the *five deliverables only* (~13 MB); code and evidence are **not**
     uploaded. Hashes in `submission_package_manifest.json`.
  2. **Archive of record** — the public repository at https://github.com/MostafaMassoud/DT-GSK,
     carrying the **full** evidence tree (`curves/` committed, author's decision) bound to the
     pinned evidence releases by SHA-256 manifests. This is what the Data Availability Statement
     cites and what reproduction should use. *(Revised 2026-08-01: D-0037 kept the repository
     private; D-0044, same day, made it public and cited the URL. No Zenodo deposit and no
     repository DOI exist; the article DOI is assigned by the journal.)*
  3. **Convenience reproduction pack** — `dist/dtgsk_reproduction_pack.zip` (21 MB), code + summary
     evidence, `curves/`+`gen_logs/` excluded so it stays a light download. **Not authoritative**; if it
     and the archived release disagree, the release wins.
  The DOI and repository locators are **author-supplied**; none is fabricated anywhere in the tree.
* **Open governance risk (author action).** The project currently lives inside the
  `MostafaMassoud/PhD-Projects` **monorepo (81,059 tracked files)** alongside unrelated PhD work,
  backups and books. Publishing that URL would point reviewers at the whole workspace, and a Zenodo DOI
  minted from it would permanently archive **all** of that unrelated material. A **dedicated
  standalone repository** for this project is strongly recommended before release. No file exceeds
  50 MB, so a 1.2 GB push is otherwise safe.

### 1.5.0-M CEC2013LSGO scope extension (2026-07-25, author decision) — RE-OPENS THE FREEZE; GOVERNS SCOPE REVIEW; newest

> **Read this before applying any earlier layer.** Layers A–L describe a manuscript whose empirical
> scope is exactly three suites and whose freeze is closed. The author has decided to **add the
> CEC2013LSGO large-scale suite to both the main paper and the Supplementary Material**. That
> re-opens `scientific_content_status: FROZEN_FOR_SUBMISSION` and supersedes every earlier statement
> that the scope is three suites or that no evidence release will change. The full dependency-ordered
> execution plan lives in `docs/development/LSGO_INTEGRATION_CAMPAIGN.md`; this layer states what the
> **review panel** must hold true while the campaign runs.

**(a) Status at the time of writing — nothing is integrated yet.** The manuscript remains built and
frozen at tag `dtgsk-submission-v1.0-2026-07-25` (commit `41726c544`), all seven administrative gaps
closed, 10/10 validators green, `check_manifest` 15/15. The LSGO data is **staging only**
(`results/_run_all/<alg>/cec2013lsgo/`), is **not** in any evidence release, and is **not** cited by
any manuscript claim. Six algorithms are complete at 375/375 runs; **dt-gsk is incomplete at 125/375**
(F1–F5 done, F6–F15 running). A panel applying this prompt today must review the **three-suite**
manuscript and treat LSGO as prospective scope, not as evidence.

**(b) The result is not favourable, and that is the central review question.** On LSGO the family is
not led by DT-GSK. Family-internal over the six complete algorithms (15 functions, mean rank of 6):
agsk 2.53, atmals-gsk 3.00, fdb-agsk 3.20, gsk 3.33, apgsk 4.20, egsk 4.73. On the five functions
dt-gsk has finished, the 8-way order including the published MOS baseline is MOS 2.40, atmals-gsk 3.20,
**dt-gsk 3.40**, fdb-agsk 4.60, agsk 4.80, gsk 5.20, egsk 6.00, apgsk 6.40. DT-GSK's one strong cell is
F4 (2nd of 8, the only family member near MOS). **The panel must not treat "DT-GSK does not lead at
D = 1000" as a defect to be fixed by presentation.** It is a finding. The reviewable questions are
whether it is reported honestly, whether it is positioned correctly against the paper's
dimension-tiering thesis, and whether including it is the right editorial choice at all.

**(c) BLOCKING — the Ackley-variant non-comparability (verified 2026-07-25).** `ackley_raw_scope`
exists in `benchmarks/cec_suite_python/cec2013lsgo/_kernel_mode.py` but is **unwired**: no reference
to it appears anywhere in `src/`, `configs/`, `tests/` or `papers/scripts/`. Every family cell ran the
**transformed** Ackley (T_osz, T_asy(0.2), Lambda(10)) — Molina's package form, the one SHADE-ILS used
— whereas LaTorre's published **MOS** table was measured on the **raw** `benchmark_func.m` form.
Evidence: on **F3** the family spans 2.001e+01–2.159e+01 against SHADE-ILS 2.01e+01 and MOS 1.69e-12;
on **F6**, family 1.052e+06–1.061e+06 against SHADE-ILS 1.02e+06 and MOS 1.43e+05; on **F10**, family
9.281e+07–9.401e+07 against SHADE-ILS 9.18e+07 and MOS 9.38e+05. The family coincides with SHADE-ILS
and sits one to thirteen orders from MOS on exactly the three Ackley-based functions — a different
objective, not a performance gap.
*Consequences the panel must enforce:* **F3, F6 and F10 may not be compared to MOS or DECC-G at all**;
they must be reported as "not comparable (objective variant)" with the reason stated. Any statement of
the form "MOS beats the family on 12 of 15" is **inadmissible**; over the 12 objective-comparable
functions the correct count is **9**. Ruling A-6 of the campaign plan governs: **disclose and restrict;
do not wire the raw scope; do not re-run.** A panel that finds an uncorrected 15-function MOS
comparison anywhere in the manuscript must raise it as **critical**.

**(d) BLOCKING — evidence-tree inventory divergence (verified 2026-07-25).** The primary namespace of
`benchmarks/cec_reference_results/` holds **3,406** files while `evidence_release_manifest.json` lists
**3,403**. The extras are `BENCHMARK_EVIDENCE_INDEX.md`, `cec2013lsgo/mos/mos_cec2013lsgo.csv` and
`cec2013lsgo/decc-g/decc-g_cec2013lsgo.csv`. `check_manifest.py` walks manifest→disk only, so **no gate
can detect a disk→manifest extra** — which is why the release verifies "3403/3403" and always will.
Two consequences: `README.md`'s "no run ever writes here" and the supplement's "no evidence file was
hand-edited" are **literally false today**; and because `cec2013lsgo/` is **not** underscore-prefixed,
`finalize_evidence.py` P6 would silently absorb those baseline tables into the primary manifest at the
next mint, merging two releases with no record. Must be closed before any promotion. The panel should
also treat the one-directional manifest check as a **gate defect** in its own right.

**(e) Release architecture — second release, never supersession.** `rel-2026-07-20-67d9345f9` is cited
verbatim in `main.tex:267` and `supplementary.tex:1193, 1202, 1829`; its `totals.files = 3403` is printed
at `supplementary.tex:1831` and its "21 (suite, optimizer) cells" at `:1833`. `finalize_evidence.py` P6
has **no extend mode** — it re-mints by supersession, which would void the cited Data Availability
identifier and trip `validate_provenance_claims.py`. LSGO must therefore be minted as a **separate
immutable release** under an **underscore-prefixed** path (`_cec2013lsgo/`), following the existing
`_ablation` / `abl-rel-2026-07-20` precedent described at `supplementary.tex:1913`.

**(f) Statistical scope — LSGO is its own family, never pooled.** n = 25 runs on LSGO against n = 51 on
the primary suites; the paper's headline aggregate (`AN-RANKAGG-2017-OVERALL`, Friedman mean rank 2.48
of 7) is **CEC2017-only** and must stay that way. Pooling LSGO into any cross-suite aggregate rank is a
category error and the panel must reject it. The LSGO analysis is also unavoidably **post-hoc**: the
data existed before its protocol was written. That must be disclosed in those words — the panel must
verify the manuscript does not imply pre-registration it does not have. A pre-commitment written
**before** the dt-gsk run completes is the one mitigation available and is tracked as campaign
Track 0B.

**(g) Budget pressure is real and binding.** Main text is **41 pp against a 40 pp internal cap**;
the supplement is 64 pp. LSGO cannot be added to the main text without harvesting space elsewhere.
The campaign ruling is **one** main-text table (T17) plus a compact subsection, with everything else in a
new supplement section **S7 appended after S6** (appending avoids renumbering, which would break every
existing cross-reference and BIND comment). `main.tex`'s `\supplementary{}` block enumerates S1–S6 and
is checked by the supplement-description drift validator (M-003) — it must be updated in the same pass.

**(h) What the panel must check once integration happens.** Every location that says "three suites" or
enumerates CEC2017/CEC2011/CEC2013 becomes false — known instances: `main.tex:218`, `main.tex:289`,
`introduction.tex:134`, `introduction.tex:158`, `performance.tex:9`, `performance.tex:959`. The abstract's
single bound number must be re-verified as still true and still CEC2017-scoped. `conclusions.tex` must
own the LSGO result rather than omit it. New claim rows are required in
`claims_evidence_matrix.csv`, and a change request is mandatory in `change_request_register.csv` for a
scope change of this magnitude.

**(i) Standing honesty constraints for this scope change (veto power).** Do not report family-internal
ranks alone while omitting the external baselines. Do not foreground F4 without stating the overall
standing. Do not describe DT-GSK as "competitive" at D = 1000 unless a stated statistical test supports
that specific word. Do not omit that six of seven algorithms had complete data before dt-gsk's leg
finished. Do not present the cross-implementation MOS/SHADE-ILS/DECC-G comparison without the
hardware-, implementation- and variant-difference caveats. If the honest conclusion is that DT-GSK does
not lead at D = 1000, **say so in the conclusions** — a paper that reports where its method stops
winning is stronger, not weaker, and a reviewer who finds that boundary themselves will discount
everything else.

**(j) The go/no-go gate is a genuine decision, not a formality.** The campaign plan (§G) defines
blocking criteria and two branch plans: **Branch A — include LSGO**, and **Branch B — defer LSGO to a
second paper**. Deferral remains fully legitimate: the current three-suite manuscript is complete,
frozen, gate-green and submission-ready today. A panel applying this prompt during the campaign should
evaluate **which branch the evidence supports**, and must not assume inclusion.

### 1.5.0-N Final empirical scope: five suites, family-internal panel, externals out (2026-07-27/28, author decision) — GOVERNS SCOPE REVIEW; SUPERSEDES §1.5.0-M WHERE THEY DISAGREE; newest

> **Read this before §1.5.0-M.** Layer M recorded a scope change *in flight* (CEC2013LSGO being added,
> with external large-scale baselines run for context). The author has since fixed the FINAL scope, and
> two of layer M's standing directives are now wrong. This layer states the settled position; M remains
> authoritative only for the Ackley-variant finding and the evidence-inventory finding, both of which
> this layer reinforces rather than relaxes.

**(a) The final analyzed scope.** Seven GSK-family algorithms — gsk, agsk, apgsk, fdb-agsk, atmals-gsk,
egsk, dt-gsk — on **five** suites: CEC2017 (29 functions, D = 10/30/50/100, 51 runs; primary), CEC2011
(22 real-world problems, native dimensions, 25 runs), CEC2013 (28 functions, D = 10/30/50, 51 runs),
CEC2020 (10 functions, D = 5/10/15/20 with F6/F7 undefined at D = 5, giving 38 cells, 30 runs, MaxFES
50k/1M/3M/10M) and CEC2013LSGO (15 functions, D = 1000 with F13/F14 at 905, 25 runs, 3e6 FES).
Registered under CR-0019.

**(b) Decision Gate 0 outcome: CEC2013 is KEPT** (author, 2026-07-28). The five-suite branch of
`docs/development/FINAL_PUBLICATION_PLAN.md` is in force; every task marked [DROP] there is void. A
panel must not raise CEC2013's presence as scope creep, nor its absence from any four-suite listing as
an inconsistency — four-suite phrasings predate this gate.

**(c) SUPERSEDED: the external-baseline mandate of §1.5.0-M, including its (i) veto.** Layer M directed
that the LSGO leg be reported against external baselines and vetoed reporting "family-internal ranks
alone while omitting the external baselines". **That directive is withdrawn.** The eight vendored
external optimizers (MOS, SHADE-ILS, DECC-G, CMA-ES, EBOwithCMAR, jSO, L-SHADE, LSHADE-SPACMA) appear
in **no** panel, table, figure, statistic or claim in this paper. Reviewers must NOT raise their
absence as a fairness gap, a missing requirement, or a rejection risk — this is now the same standing
exclusion §1.5.4 already applies to external comparators generally.

**(d) Why the withdrawal is not a weakening — the compensating mechanism (enforce this instead).** The
externals were run on our hardware, under our harness, against our transformed-Ackley variant; a
cross-implementation table built from them would carry uncontrolled hardware, implementation and
variant differences in exactly the direction that flatters the proposed method. The paper therefore
does something stricter: it **states the negative result outright**, citing PUBLISHED specialist
results rather than our own banks. Three sentences are load-bearing, are registered as claim rows
LM-06 / RS-13, and **may not be cut, softened, or demoted to the supplement for page budget**:
>
> (a) LSGO subsection scope sentence — the analysis is family-internal; dedicated large-scale
> optimizers such as SHADE-ILS and MOS report substantially stronger PUBLISHED results on this suite
> than any GSK-family member; no competitiveness with such specialists is claimed.
>
> (b) Conclusions limitation — at D = 1000 no member of the family, DT-GSK included, approaches what
> dedicated large-scale specialists report in the literature; the family's evidence of competitiveness
> ends at the dimensionalities of the bound-constrained suites.
>
> (c) Data Availability — the repository additionally contains validated implementations and complete
> result banks for several non-GSK baselines (including SHADE-ILS, MOS and DECC-G on CEC2013LSGO);
> these fall outside the analyzed scope and no comparability audit against the family is claimed.
>
A panel should verify these three sentences are PRESENT and unhedged. Their removal, not their
presence, is the reviewable defect. The repository-side counterpart is the status package under
`benchmarks/cec_reference_results/_external_baselines/`, whose README carries the same disclosure.

**(e) REINFORCED from §1.5.0-M: the Ackley-variant non-comparability.** CEC2013LSGO F3, F6 and F10 in
this project run the TRANSFORMED Ackley variant. The raw kernels exist inside the evaluator behind
the `ackley_raw_scope` context manager, but nothing ever activates them — no caller in `src/`,
`configs/`, `tests/`, `scripts/` or `papers/scripts/` references the scope, and `ackley_raw_active()`
returns False — so every committed bank ran the transformed chain. Under the final scope the raw
variant stays permanently INACTIVE, because its only purpose was comparability with published MOS
results — a comparison the paper no longer makes. Any sentence comparing our F3/F6/F10 values against published large-scale
results is a **blocking** defect, and this includes the sentences of (d): they cite published
specialist performance in general terms and must never be supported by our own transformed-variant
banks.

**(f) CEC2020 is PRE-REGISTERED — review it as such.** Its statistical analysis plan
(`papers/build_prompt_phases/phase_05/statistical_analysis_plan_addendum_cec2020_lsgo.md`) was
committed, with its SHA-256 recorded in `decision_log.md` (D-0021), **before any CEC2020 result
existed** — verified at signing: zero CEC2020 banks anywhere in the repository. A panel's job on this
suite is therefore comparison, not re-derivation: check that what is REPORTED matches what was
REGISTERED (hypotheses, analysis ids, tie rules, wording bank, the AGSK conflict-adjacency
disclosure), and treat any silent deviation as a blocking finding. CEC2020 is a comparator's home
regime — AGSK won that competition and its paper is a co-author's — so a non-leading DT-GSK result
here is a **predicted** boundary finding of the dimension-tiering thesis, disclosed in advance, and
must not be read as a defect or as a result that "does not count".

**(g) LSGO evidential tiers are binding and asymmetric.** The family Friedman ranks and per-function
means on LSGO were INSPECTED before registration; they are descriptive-after-inspection, carry no
confirmatory weight, and may never enter a headline. Only the run-level paired Wilcoxon + Holm layer
(never computed before registration) is confirmatory-with-disclosure. Prohibited LSGO wording:
"leads", "first", "scales to D = 1000", "competitive" without a named supporting test, and the F4/F8
wins stated without the F7/F15 last places.

**(h) Populated review variables (§1.5.1) are STALE against this layer** — in particular
`EMPIRICAL_SCOPE`, which still describes three built suites plus a prospective fourth. They are
updated once, in a single pass, after the manuscript surgery completes. Read §1.5.1 as historical
until then; where it conflicts with this layer, **this layer governs**.

### 1.5.0-O Five-suite manuscript EXECUTED; evidence complete; builds green (2026-07-29) — GOVERNS CURRENT STATE; SUPERSEDES §1.5.0-N's pending-work framing; newest

> **Read this first.** Layer N announced the five-suite scope; this layer records its
> COMPLETION. Every panel directive below reviews a finished, built, gate-green
> manuscript, not work in flight.

**(a) Evidence and analysis are COMPLETE.** All 35 suite-by-algorithm banks exist and
are promoted: 85,855 runs. Three evidence releases coexist under union
strict-inventory (zero unlisted): the frozen primary `rel-2026-07-20-67d9345f9`
(cec2017/cec2011/cec2013, 3,403 files, byte-guarded incl. its 115-file analysis
bundle), `lsgo-rel-2026-07-28-ff1a046ef` (173 files) and
`cec2020-rel-2026-07-29-5867abe1e` (336 files), plus `abl-rel-2026-07-20`. Every
registered SAP family is computed into committed, self-manifested analysis bundles;
the registered outcomes are recorded in the append-only Amendments 1--2 of the SAP
addendum (signing commit `5c9bfae82`, made before any CEC2020 result existed).

**(b) The empirical story, fixed by the registered pipeline.** CEC2017: first
(2.48 aggregate; the abstract's single bound number, CEC2017-fenced). CEC2013:
first (2.80). CEC2011: second behind eGSK, as frozen. CEC2020: **fourth of seven**
(aggregate 4.11; agsk 2.09 best) with the pre-committed [AGSK first] wording-bank
sentence applied verbatim and DT-GSK Holm-separated in five of twenty-four
across-function cells (three favourable, two unfavourable). CEC2013LSGO:
**tied-first descriptive with AGSK (3.13 each)**, no paired separation from any
comparator (vs AGSK exact p = 0.847), Holm-significantly better than all six on
F4/F8 and worse than all six on F7/F15 — always stated both ways — and the effect
layer bars any superiority claim over ATMALS-GSK. The recount sentence is
"first on two, tied-first on one, second on one, and fourth on one of the five
suites' descriptive family-rank aggregates". A panel must treat any deviation
from these standings in any surface as a BLOCKING defect.

**(c) Main-text completeness directives (new, review these as present-by-design).**
The main paper is parameter-complete and results-complete without the supplement:
the comparator parameter table (generated, read-from-source) now appears in the
main text as `tab:comparator-params-main` alongside DT-GSK's full frozen
configuration (`tab:parameters`); the final CEC2020 panel is main-text
`tab:cec2020-ranks` (per-dimension tie-corrected Friedman mean ranks, omnibus
chi-square, Iman--Davenport p, seeded permutation p, and the no-test descriptive
aggregate with the mandatory D5-reduced-set + MaxFES caption disclosure); the
final CEC2013LSGO family panel is main-text `tab:lsgo-ranks` (mean ranks with the
tied-first convention, plus the across-function Wilcoxon layer against DT-GSK with
exact and Holm p). S7/S8 carry the per-function detail, run-level tests, effect
sizes and robustness. Do not raise "parameters only in supplement" or "new-suite
results only in supplement" — both were deliberate additions on 2026-07-29.

**(d) Review mode for CEC2020 is registered-vs-reported.** The analysis plan,
tie rules, decision criteria and all three outcome sentences predate the first
datum; the panel's job is comparison against the registered text (addendum
Sections 2--4, 9; Amendments 1--2), never re-derivation. Known, accepted pattern
hits: the validat*+CEC2013 review flag fires on the Data Availability sentence
BY DESIGN (the sentence disclaims validation — decision_log D-0025); the
state-of-the-art blocked-wording scan hits two frozen disclaimer sentences
(related_work structure-blindness paragraph; the supplement's family-internal
limitation) — both adjudicated benign, they disclaim rather than claim.

**(e) Build state.** All five artifacts rebuilt deterministically on 2026-07-29
at the pinned epochs (PDF 1783468800 + FORCE_SOURCE_DATE=1; DOCX 1783641600),
each byte-identical across double builds; build hygiene OK (0 overfull > 2pt);
cross-format parity 717 rows / 0 FAIL; both DOCX validators 0 warnings;
provenance-claims validator green on source and rendered text; citation corpus 61
keys, C1--C5 green. The freeze manifest is EXPECTEDLY stale until the pass-24
re-mint (tag dtgsk-submission-v2.0); _pending_refreeze.json is the tracker.

### 1.5.0-P Eight-seat panel round executed; full fix batch applied; Amendment 3; pass-26 basis (2026-07-31) — GOVERNS CURRENT STATE; SUPERSEDES §1.5.0-O's build-state facts; newest

> **Read this first.** After the pass-24/25 freeze, an eight-seat expert panel
> applied this prompt end-to-end (record:
> `papers/governance/panel_review_register_2026-07-31.md`; verdict: unanimous
> MINOR REVISION; 0 defects in any number, standing, test, or registered
> outcome). The author directed "fix all"; the full register batch (I-1..I-23,
> E-1..E-9, U-2..U-6) is APPLIED, rebuilt, and gate-green. Facts below
> supersede older layers where they disagree.

**(a) Amendment 3 (2026-07-31) corrects the wording bank — the corrected
sentence is now the binding verbatim.** The registered [AGSK first] sentence's
subordinate clause "the CEC2020 competition it won" was a false literature
fact: AGSK was the CEC2020 **runner-up** (IMODE won), per the corpus's own
sanctioned source `apgsk2021` p. 65936. The dated, append-only Amendment 3
(`papers/build_prompt_phases/phase_05/statistical_analysis_plan_addendum_cec2020_lsgo_amendment_03.md`)
corrects the Section 9 variant and the Section 10 adjacency wording. The bank
sentence at its four loci (abstract; §4.5; conclusions; S8) now reads "the
CEC2020 competition in which it was the runner-up" with `\cite{apgsk2021}`
attached OUTSIDE the abstract — a panel must treat THAT wording as the
registered verbatim and must NOT flag "runner-up" as a bank deviation, nor
re-raise the old "it won" clause as required text. All binding standings are
unchanged (fourth, 4.1125; agsk first 2.0875; five-of-24 split).

**(b) Notable applied fixes a panel must not re-raise (verify, don't
rediscover).** S5.4's fifth limitation now states per-suite evidence ceilings
(D=1000 LSGO evidence acknowledged; component-isolation ceiling D<=100);
S5.3 is five-suite-scoped with the full held-out summary (CEC2020 fourth and
LSGO tied-first included); S5.10 attributes provenance to all three evidence
releases + the ablation release; the cover letter is re-fenced ("never
Nemenyi-separable at any CEC2017 dimension"), de-hyphenated (CEC2013LSGO),
GenAI-synced, and carries the runner-up wording; the COI block gained the
mechanical-mitigation sentence; the escape-gate claim is corrected to LS-only
(hook runtime-dead on the escape); the budget parentheticals in Algorithm 1 /
Table 2 are suite-neutral; kappa_ls is 0.45 at D>=50; the linkage
learned-vs-random split is per-row; AmE spelling unified (favorable/favors);
the S7 surface carries the registered low-power echo and the
relative-tie-band clause; the two suite-report bib `note` fields are deleted.

**(c) Current pinned facts.** GenAI disclosure pins **Claude Opus 4.6, 4.8
and 5.0 (Anthropic)** in BOTH the manuscript and the cover letter (the old
single-version pin in §1.5.0-B-era layers is historical). The rendered
abstract measures **204 words** on the built PDF (suite-role list now
"Suite roles: ..."; the CEC2011 Holm-significance attachment disambiguated).
Environment attestation records **603 tests x2, zero failures**; the
supplement prints 603. Production caps are CR-0021 (B1 44 pp / B2 24,000
words; measured 41 pp / 22,821 at filing). Test suite 601 passed + 2 skipped.
Parity 724 rows / 0 FAIL (one notation paragraph is PASS_FORMAT_DIFF
alnum-split-containment — a float+page-break extraction artifact, not drift).
Freeze: the batch voids pass-25; the pass-26 re-mint at this state is the
basis of tag `dtgsk-submission-v2.1-2026-07-31` (v2.0 retained, never moved;
neither pushed yet — the author pushes). Decision log through D-0028.
Author-directed addendum rows A-1/A-2 in the panel register are
algorithm-level limitations, NOT manuscript defects: A-2 (close the CEC2011
eGSK gap) is post-submission research and must never alter this submission.

### 1.5.0-Q Pass-27 DOCX header restoration; v2.2 basis; repo split, closures, and hygiene (2026-07-31 evening) — GOVERNS CURRENT STATE; SUPERSEDES §1.5.0-P's build-state facts; newest

> **Read this first.** Same-day continuation of §1.5.0-P. The author requested
> the MDPI header block (title / authors with affiliation superscripts /
> numbered affiliation / correspondence) render correctly in BOTH formats of
> the supplement; the PDF already complied, both DOCX did not. The fix batch
> below re-minted the freeze as **pass-27** (anchor `2f9631eb7`, D-0029) and
> the submission basis is now **tag `v2.2`**. Facts below supersede older
> layers where they disagree.

**(a) The DOCX header defects and their fix (a panel must verify, not
re-raise).** Two independent defects, both DOCX-only: (i) the two
post-processing passes that undo pandoc's metadata hoisting
(`_hoist_article_label`, `_affiliations_before_abstract`) were gated to the
main document — the first on the false premise that the supplement carries no
article-type label — so `supplementary.docx` rendered title/authors/abstract/
Article/affiliation, contradicted by its own PDF; (ii) pandoc builds the DOCX
title block from document METADATA and silently DROPS math there, so the
`$^{1,*}$` / `$^{1}$` affiliation superscripts vanished from the author and
affiliation lines in BOTH documents (revision ticket R3-11 requires that
mapping). Fix: gates removed; superscripts ride through pandoc as `@@SUP!X@@`
markers rebuilt into real `w:vertAlign` runs by
`PostProcessor._restore_header_superscripts` (each inheriting its source
run's `w:rPr`); `make_run` gained a `superscript` keyword; an unconsumed
marker aborts the build via `parts_document_residue`. Both DOCX verified
byte-identical across THREE consecutive builds at
`SOURCE_DATE_EPOCH=1783641600`. A reviewer must check the rendered header
block in all four artifacts and must NOT flag the marker machinery, the
`Microsoft Word 12.0.0` application signature, or the `^(1,*)`-style
superscript runs as defects.

**(b) Word-resave incidents and the committed-blob review rule.** Twice on
2026-07-31 the author's prescribed D-WORD-01 open-save probe produced
Word-rewritten packages that were then committed (`fa613cf`: main only;
`7804150`: both, briefly on origin). `check_manifest` hashes the WORKING TREE
and stayed 15/15 throughout — the substitution was invisible to every gate
and only a fresh clone would have shipped the wrong bytes to SuSy. Both were
superseded by deterministic rebuilds (`2f9631e`, `6a67c0b`) reproducing the
exact pass-27 hashes (no re-mint needed). Standing rule for every future
round: verify the HEAD blobs (`git rev-parse HEAD:<path>` → `git cat-file
-s` / hash) against the manifest in addition to the disk files, and treat a
DOCX whose `docProps/app.xml` reads Application "Microsoft Office Word" /
AppVersion 16.0000 (26/46 zip entries) as a resave — the deterministic build
reads "Microsoft Word 12.0.0" (27/47 entries).

**(c) Governance closures (verify, don't re-raise).** CR-0020 closed
2026-07-31 — register 21/21 APPROVED (61 citation keys, C1–C5 hold).
D-WORD-01 CLOSED — `word_validation_report.md` §10.2: author open-saved both
pass-27 documents without error and confirmed the §1 visual checklist
(fields, cross-references, wide tables); the multi-source CITATION cosmetic
form was not reported and the closure does not hang on it. R-0004 CLOSED —
author reviewed and approved the MDPI Algorithms cover letter 2026-07-31.
`word_validation_report.md` §10 also supersedes §9's artifact hashes/counts;
the bindings figure is now **250 BIND comments / 1,135 tokens / 1,135 PASS /
0 FAIL** after the pow10 spaced-channel fix (`ea63486`) — the squashed
channel concatenates adjacent table cells, so exact scientific-notation
matches ("1.8x10-11" followed by "4.3x10-10") failed the trailing-digit
guard; three values were reported pdf=NO docx=NO while present in both
formats. Any "267 BIND / 721 token" figure anywhere is three-suite-era.

**(d) Repository split and hygiene (affects reproducibility review).** The
project ships from this standalone repository (origin
`MostafaMassoud/DT-GSK`, single squashed history + this session's commits;
tags `v2.1`, `v2.2` on origin). The monorepo copy re-converged at
`faf93dd8d` with lineage tag `dtgsk-submission-v2.2-2026-07-31`; root
`README.md`/`CITATION.cff` deliberately differ (public-facing vs workspace).
`results/` was pruned of 477 family convergence-curve CSVs (1.606 GB) under
ruling A-11 — the LSGO/CEC2020 release manifests record the exclusion
explicitly (`curve_csvs_excluded`: 106 / 266) and the primary release's
1,554 curve entries all live in the promoted `benchmarks/` tree; the three
external-baseline banks (`shade-ils`, `mos-cec2013lsgo`, `decc-g`; 48 files
each) are UNTOUCHED per FINAL_PUBLICATION_PLAN §2.8(b). Tracked tree is now
1.306 GB, of which 1.21 GB is the immutable promoted evidence. README.md and
CITATION.cff were rewritten for the public audience (three authors, real
ORCIDs, five-suite standings table read from the release CSVs,
submitted-to-Algorithms status).

**(e) Known residues THIS round must adjudicate (pre-verified, not
rumors).** (i) `CITATION.cff` line 9 reads `version: "2.1"` — written when
v2.1 was the basis, now stale vs the v2.2 tag; repo-only fix, does not void
pass-27. (ii) SE-049: no similarity-screening record OR explicit
publisher-deferral note exists under `papers/governance/` — the 2026-07-22
round accepted either as closure and neither was filed. (iii)
`src/gsk_family/optimizers/fdb_agsk.py` still lacks the source-attribution
header SE-035 required (egsk.py has one; fdb_agsk.py is the other
third-party-derived comparator). (iv) The `.bak` file at the repo root
(127 KB, 2026-07-23) ships in the public tree — decide keep/remove. None of
these touches a manifest-tracked file.

**(f) Review posture for this round.** Registered-vs-reported mode
unchanged; Amendment 3's runner-up wording is the binding verbatim at its
four loci; standings are NEVER restated from memory (read the release CSVs);
frozen releases are never re-run; the pre-registration is append-only; a
finding is CONFIRMED only after adversarial verification against the live
tree. The marginal value of this round is final publication polish,
regression-checking the pass-27 changes, and public-facing repo readiness —
not rediscovery of resolved objections.

### 1.5.0-R Submission → major revision → revision complete (2026-08-01 → 2026-08-28) — NEWEST; GOVERNS

**Submission and decision.** Submitted 2026-08-01 as freeze pass-38 / tag v2.13 (ID
`algorithms-4507562`). Decision: **major revision**, two unsigned reviewers, ten points — the asks,
dispositions and per-point verification duties are §1.5.3-J. The reports, the point-by-point
response and the decision e-mail are withheld under D-0049; the pre-registration is public on
purpose. The ten-day window was first *inferred* as closing 2026-09-03; the author **confirmed the
real deadline as 2026-09-01** (2026-08-27) — the same day as the planned resubmission, zero slack —
and **declined** the journal's offered extension.

**The revision (passes 39–41 → v2.14, published as a squash).** Four pre-registered experiments
(E1–E4; **32,451 runs**, 22.2 h, zero failures) promoted as the additive, non-superseding release
`rev-rel-2026-08-26-dd42d37eb`, written up as Supplementary **S9.1–S9.4** / Tables **A43–A46**,
with the wording for every adverse outcome committed *before* the runs. Two submitted claims were
**falsified and the corrections ship in the paper**: the learned eigenbasis is beaten by plain
coordinate axes at D = 50 (Holm 1.4e-4, W/T/L 4/0/25 against) and not separated at D = 100, so C1
is claimed basis-neutrally as a *deterministic final polish* (which does beat no refinement at both
active dimensions); and the D = 10 parameter set beats the shipped one at D = 30 (Holm 0.0055), so
the 20 ≤ D < 50 tier is disclosed as mis-specified and C2 is narrowed to D = 10/50. E2 (matched
NP = 100, 5,916 paired runs) shows the family standing is not the population rule's artifact —
top-two at every dimension either way — but the rule costs first place at D = 50/100
(Holm 0.0064 / 0.0051), so those two rank claims are qualified. E4 (27 cells, exploratory,
descriptive-only): ordinals hold in 26/27; the one favourable flip lands on the tier E3 already
flags as mis-specified.

**Post-revision correction passes 42–48 (v2.15–v2.21).** Pass-42: twelve alleged defects verified
then counter-challenged — nine corrected, **C4 refuted (its proposed fix was a regression)**.
Pass-43: package self-consistency + the **source-hash gate** (`source_files` in the freeze
manifest; `check_manifest` prints `sources N/N` on its own line; negative-tested). Pass-44: three
wording items. Pass-45: a 97-agent application of THIS instrument found two **Major** main-text
defects the revision had missed (§3.5 still asserting the pre-revision basis position; an
evidence-discipline release count contradicting the DAS). **Calibration across four independent
rounds: the diagnoses are reliable, the prescriptions are not — 44/82 findings REFUTED and 75/82
proposed remedies unsafe as written. Challenge every proposed fix, not just the finding.**
Pass-46: eight tickets. Pass-47: S9 provenance + source anchors — and it **shipped a phantom
symbol** (`_ace_apply_credit`, which does not exist in `src/`) because its applier printed success
unconditionally; pass-48 repaired it with the verified `_ace_update_probs` (read the function
body, never trust the memo) and closed the specification gap the phantom concealed.

**Resubmission package — check-list item (II) DISCHARGED (2026-08-27/28).** Two false premises were
withdrawn: the manuscript does **not** carry any `\hl`/highlighting markup (nothing to collide
with), and latexdiff is **not** unusable — plain `latexdiff` lacks `Algorithm::Diff` but
**`latexdiff-so` bundles it** (plus the `ulem` package). Both change artifacts now exist with
generators (see the banner). Known limits, disclosed rather than discovered: **preamble changes do
not render** in the marked PDF (the retitle is named twice in the response letter instead), the
diff covers `main.tex` + sections — with `--doc supplementary` producing a marked-up Supplementary as well (added 2026-08-28) — and the
register's reviewer-point attribution is keyword-derived and self-declared non-authoritative — an
**S9.2/S9.3 transposition** in its rules already shipped once and is fixed (S9.2 = matched NP,
S9.3 = tiering; verify against the section titles, not from memory). The response letter also
gained a protocol-conformance note for E2 — the CEC protocols fix MaxFES (= 10^4·D at CEC2017,
identically at CEC2013) and specify **no population size**; never write "from CEC2017 onward",
and the note explicitly does not rebut the reviewer's concern.

**Instrument-facing traps added since 07-31:** extract rendered PDF text with `pdftotext`, never
pypdf (drops spaces around inline math; one spurious defect already filed and retracted,
2026-08-28). `paper-revisions/` (tracked, added by the author) archives each successive manuscript
version **including MDPI's own recompilation of v2.13** — a byte-different producer
(pdfTeX-1.40.25 vs MiKTeX 1.40.29), not a drifted copy; do not "fix" it. GitHub exposure records:
`docs/development/github_exposure_traffic_record.md` (clone counts captured 2026-08-27; six days
permanently unmeasured; purge request **closed unfiled** 2026-08-28 — do not re-raise).


### 1.5.1 Populated review variables (current baseline)

```text
PROJECT_TITLE:            DT-GSK: Dimension-Tiered Adaptive Configuration Selection
                          and Deterministic Refinement for Gaining-Sharing Knowledge
                          Optimization
                          (retitled 2026-07-18 — §1.5.0-B(a); again 2026-08-25 per
                          reviewer 1, journal round 1 — CR-0023 / D-0047. Historical
                          narration elsewhere in this file keeps the old title.)
TARGET_JOURNAL:          MDPI Algorithms
TARGET_ARTICLE_TYPE:     Article
TARGET_QUARTILE_STATUS:  Q2 (WoS CS Theory & Methods, IF 2.6); Scopus CiteScore
                         Q1 Numerical Analysis — the PhD requirement (Q1/Q2) is met
EMPIRICAL_SCOPE:         FIVE suites, family-only panel (7 GSK-family algorithms;
                         externals in no panel/table/claim -- CR-0019):
                         CEC2017 (primary; DT-GSK first, 2.48) + CEC2011 (second
                         behind eGSK) + CEC2013 (first, 2.80) + CEC2020
                         (pre-registered confirmatory; DT-GSK FOURTH of seven,
                         [AGSK first] wording-bank sentence verbatim) + CEC2013LSGO
                         (family-internal; tied-first descriptive with AGSK, no
                         paired separation). Registered outcomes in SAP Addendum 1
                         Amendments 1--2; review mode is registered-vs-reported
                         (1.5.0-O).
MANUSCRIPT_FILE_OR_TEXT: papers/DT-GSK.pdf  +  papers/DT-GSK.docx  (49 pp, round-one
                         revised state; the 46-pp / B1 = 41 figures were pass-27 values)
SUPPLEMENTARY_FILE:      papers/supplementary.pdf (S1–S9, 83 pp; S7 = CEC2013LSGO,
                         S8 = CEC2020, S9 = the five revision experiments E1–E5
                         with Tables A43–A47 (S9.5 boundary study added 2026-08-28),
                         earlier numbering untouched; portrait-only) + papers/supplementary.docx
GOVERNING_PROTOCOL:      papers/PAPER_BUILD_PROMPT.md
GOVERNANCE_AND_GATES:    papers/governance/ (main_manuscript_freeze_manifest.json,
                         reproducibility_manifest.json, decision_log.md,
                         claims_evidence_matrix.csv, administrative_gap_register.md,
                         cross_format_consistency.csv)
RAW_OR_IMMUTABLE_EVIDENCE_ROOT: benchmarks/cec_reference_results/ — the CURRENT
                         primary release is rel-2026-07-20-67d9345f9 (always RESOLVE
                         it from papers/governance/evidence_release_manifest.json
                         `release_id`; it supersedes rel-2026-07-16-78f075cb0, which
                         superseded the pre-fix rel-2026-07-10-262fc16c9 —
                         §1.5.0(h)/§1.5.0-C)
                         + the two separate, non-superseding suite releases
                         lsgo-rel-2026-07-28-ff1a046ef (cec2013lsgo/, manifest
                         papers/governance/evidence_release_manifest_cec2013lsgo.json)
                         and cec2020-rel-2026-07-29-5867abe1e (cec2020/, manifest
                         ..._cec2020.json) — 1.5.0-O(a); strict inventory is the
                         UNION of all three manifests
                         + .../_ablation/ (scaffold + SGSM overlay; CURRENT id
                         abl-rel-2026-07-20, the 51-run re-mint; resolve from
                         _ablation/manifest.json — §1.5.0(g))
                         + the round-one revision release
                         rev-rel-2026-08-26-dd42d37eb (E1–E4, 32,451 runs; additive,
                         non-superseding; every S9 number binds to it)
                         (The former .../_oracle/ release was REMOVED with the oracle
                         study on 2026-07-18 — §1.5.0-B(d); it is NOT on disk and is
                         NOT paper evidence. Do not expect or audit it.)
DERIVED_ANALYSIS_BUNDLE: papers/analysis/rel-2026-07-20-67d9345f9/ (frozen primary,
                         byte-guarded by check_frozen_analysis.py) ;
                         papers/analysis/lsgo-rel-2026-07-28-ff1a046ef/ and
                         papers/analysis/cec2020-rel-2026-07-29-5867abe1e/ (the two
                         new-suite bundles, each self-manifested via
                         analysis_manifest.json + analysis_checksums.sha256;
                         produced by papers/scripts/phase6b_run_analysis_newsuites.py,
                         whose built-in self-check reproduces the Amendment 1 pins) ;
                         papers/analysis/ablation_overlay/ ; papers/analysis/posthoc_robustness/ ;
                         papers/analysis/rev-rel-2026-08-26-dd42d37eb/ (round-one
                         revision bundle, self-manifested)
STATISTICAL_ANALYSIS_PLAN: papers/build_prompt_phases/phase_05/statistical_analysis_plan.md
                         + statistical_analysis_plan_addendum_cec2020_lsgo.md (signing
                         commit 5c9bfae82, append-only) + its Amendments 1--2 (first
                         computations, corrections, and the data-resolved outcome wording)
LATEX_SOURCE / PDF / WORD: present; builds are deterministic (see 1.5.4)
ADMINISTRATIVE_METADATA: CRediT/GenAI/funding/submission-date CONFIRMED; AG-0001..0007
                         ALL CLOSED (H.S.M.R. e-mail + all three ORCID iDs supplied
                         2026-07-25; GenAI pins Claude Opus 4.6/4.8/5.0). Remaining
                         author-side (2026-08-28): resubmit via SuSy by 2026-09-01;
                         re-enter the new title + revised keywords in the portal by
                         hand; upload the two change documents. The DAS NOW PRINTS
                         the repo URL and names v2.13 (submitted) / v2.22 (revised);
                         there is no Zenodo deposit and no repo DOI (D-0049) -- the
                         article DOI is assigned by the journal at acceptance
DETERMINISM:             main PDF SOURCE_DATE_EPOCH=1783468800 FORCE_SOURCE_DATE=1;
                         DOCX SOURCE_DATE_EPOCH=1783641600; all four artifacts bit-identical ×2
FREEZE_STATE:            Pass-49 (tag v2.22; v2.13..v2.22 all resolve; decision log
                         through D-0054, change requests through CR-0029; next free
                         ids CR-0034 / D-0059 -- verify free at apply time),
                         check_manifest 15/15 files PLUS sources 2/2 (source_files
                         gate, pass-43), COMMITTED AND PUSHED. Submission basis
                         v2.13; revised basis v2.22. anchor_commit values do NOT
                         resolve on origin (publication squash) -- published_commit
                         does. The manifest is CRLF + 2-space, edited surgically in
                         place -- never read_text()/sed/json.dump. Verify HEAD BLOBS
                         against the manifest as well as disk files (Word-resave
                         incidents fa613cf/7804150 -- see 1.5.0-Q(b)). Any mismatch
                         is a DEFECT. Gate counts drift per pass -- RUN the gates;
                         the 250/1,135 binding and 724-row parity figures once
                         printed here were pass-27 values. Abstract word count:
                         re-verify on the build, never assert a stale count.
```

### 1.5.2 Manuscript identity — what the paper now claims (and does not)

- **Headline (honest, panel-scoped):** DT-GSK attains the **best overall CEC2017 Friedman mean rank in the seven-algorithm GSK family (2.48/7)** — first at D=10/50/100, second at D=30 behind eGSK; second on CEC2011 (a Holm-significant loss). All comparative claims are **scoped to the GSK-family panel**; no field-wide claims are made.
- **Positioning (2026-07-18 — §1.5.0-B governs):** DT-GSK is presented as a **dimension-tiered adaptive-control and deterministic-refinement system** on the GSK scaffold; the title leads with the two supported contributions (adaptive control = scaffold, C2; deterministic refinement = eigenframe final polish, C1). The interaction-structure memory (ISM) is a **secondary exploratory mechanism / supporting implementation component** — NOT a headline contribution, NOT the organizing element, and NOT the performance driver.
- **eGSK comparator provenance:** the panel's eGSK cells are the **runnable Python scipy-SLSQP port** (not the MATLAB `fmincon` reference); no cross-backend numerical-equivalence or runtime-superiority claim is made.
- **ISM isolation — an honest null, reported briefly (2026-07-18 framing):** a direct 4-cell overlay isolation (51 runs per cell) finds **no significant standalone ISM contribution** at its active tiers (CEC2017 D50 Holm p=0.983, D100 p=0.897; CEC2013 D50 p=0.647; A₁₂ ≈ 0.51/0.50, and **0.42 on CEC2013 D50 — trending against ISM**), while the ISM-dependent final polish IS Holm-significant (Supplement §S6.5, unchanged). The former §S6.7 mechanism study is **REMOVED from the paper** (§1.5.0-B(d)); the null is now stated in ONE abstract sentence plus the introduction's supporting-component paragraph (§1.5.0-B(c)), and the paper claims NO ISM improvement. **Reviewers: flag any ‘small improvement’/‘helps’ reframing of the null, any principal-contribution framing of ISM, or any surviving reference to the removed oracle study as a critical integrity defect; do not re-raise the (brief) advertised null as a §10.9 leak.**

### 1.5.3 Standing findings — RESOLVED / ADDRESSED this session (verify consistency; do NOT re-raise as new criticism)

Map to the panel's own gates. For each, the correct reviewer action is the **verification** in the right-hand column — not re-opening the original objection.

| Item (original objection) | Gate / Team | Status + locus | Required verification this pass |
|---|---|---|---|
| **ISM never directly isolated** (the central objection) | K / T2-BENCH, T1-OPT | **RESOLVED.** Direct 4-cell overlay isolation on **CEC2017 D50+D100** (primary suite) + CEC2013 D50, **51 runs per cell** → **Supplement §S6.5 (`tab:ism-isolation`).** Honest **null**: no significant standalone ISM benefit (paired Wilcoxon Holm p = 0.983/0.897/0.647; A₁₂ ≈ 0.51/0.50/0.42 — the 0.42 trends *against* ISM), while the **eigenframe polish IS the significant** added mechanism (Holm p 0.002/0.005/0.002). The panels are in the **immutable 51-run release `abl-rel-2026-07-20`** (the current ablation release; see Finding #1 below), not `results/` staging. | Confirm the null is stated **consistently and briefly as a null** — no "improvement"/"helps" reframe, no principal-contribution framing of ISM — across main text (performance/introduction/conclusions), abstract, and supplement §S6.5; that **no passage over-attributes performance to ISM**; and that every §S6.5 number matches the promoted `_ablation/overlay/analysis/*cec2017*` bundle (mirrored by `papers/analysis/ablation_overlay/*.csv`). |
| **"High-Dimensional" overclaim (D≤100)** | C, D / T1-OPT, ECB | **RESOLVED.** The FINAL title is "DT-GSK: Dimension-Tiered Adaptive Configuration Selection and Deterministic Refinement for Gaining-Sharing Knowledge Optimization" (§1.5.0-B(a); DT = **Dimension-Tiered**). It names neither "high-dimensional", nor the oracle, nor ISM. | Confirm no residual "high-dimensional"-as-headline framing anywhere (title, abstract, keywords, cover letter), and that the final title appears verbatim across all sources and artifacts. |
| **Algorithm not independently reimplementable; operator constants missing** | F / T1-OPT | **ADDRESSED.** Complete operator specification inlined in **Supplement §S5.9** (`sec:repro:opspec`; §S5.4 is now "Limitations in Full") (full 5-arm ACE table, two-accumulator graph update + ℓ1 norm, graph→block extraction + confidence gate, eigenframe compass constants, Cauchy scale, RNG modulus). | Spot-check the inlined constants **against the hash-frozen code** (`src/gsk_family/optimizers/_dt_core.py`, `_dt_profiles.py`, `interaction_graph.py`, `_dt_rng.py`); confirm tier-labeling. |
| **Raw-error endpoint / normal-approx Wilcoxon not robust** | I / T3-STAT | **ADDRESSED (post-hoc).** **Supplement §S2** adds endpoint-invariance (raw/median/log10 — DT-GSK rank stable) and exact sign-flip permutation inference (0/24 Holm decisions change). | Confirm these are labeled **post-hoc / non-pre-registered** and do **not** silently replace the pre-registered primary; reproduce via `papers/scripts/posthoc_robustness_cec2017.py`. |
| **Reproducibility of headline numbers** | L / T3-STAT, T4-SOFT | **STANDING STRENGTH.** Deterministic builds ×2; 15/15 freeze; every isolation/robustness number bound to a committed producing script + CSV. | Re-run `check_manifest.py` (expect **15/15**) and one build ×2; confirm bit-identity. |
| **eGSK provenance (fmincon vs SLSQP)** | G / T3-STAT, T6-INTEG | **RESOLVED.** Disclosed as the SLSQP Python port throughout paper + docs. | Confirm no residual "fmincon reference comparator" wording. |
| **DOCX authored tables collapsed to 1×1 cells** (Round-1 MAJ-1/MAJ-2) | M, P / T4-SOFT, T5-WRITE | **RESOLVED.** The four expository main-text tables (taxonomy, architecture, dimension-gating, ISM-mechanism) that pandoc collapsed into single 1×1 cells carrying a dangling `FigureTable` style are now rebuilt as native multi-column `w:tbl` (`build_docx.py::_rebuild_collapsed_authored_tables`, with a math→Unicode / `\ref`→number cell converter); the dangling style is gone; `validate_docx.py` now **exits 0** (was exit 2). | Confirm the DOCX carries four proper multi-row/column tables matching the PDF and zero `FigureTable`-styled `w:tbl`; confirm validator exit 0 + `markers_left=0`. The in-Word visual spot-check is the sole author-side residue (§1.5.4). |
| **S6.5 CEC2017 rows cited from non-citable staging** (Round-2 Finding #1) | L / T3-STAT, T4-SOFT | **RESOLVED.** The CEC2017 D50/D100 overlay panels are in the immutable 51-run release `abl-rel-2026-07-20` (analysis bundle + raw runs SHA-256-checksummed); the §S6.5 BIND is repointed off `results/` staging; the CEC2017 contrasts JSON is at full CEC2013 schema parity (A₁₂ block). | Confirm every §S6.5 CEC2017 number reproduces from `_ablation/overlay/analysis/*cec2017*`; run the release self-check; confirm the BIND cites the release, not `results/`. |
| **Selection-exposure count unsourced** (Round-2 Finding #2) | I, O / T3-STAT, T6-INTEG | **RESOLVED.** S5.3 no longer asserts a specific unverifiable count ("six candidate configurations"); reframed as an author-attested development-history note explicitly **not** part of the immutable release; the performance.tex echo drops "the number of". | SUPERSEDED BY D-0020 (2026-07-23): the count is now DISCLOSED as **six** full-panel candidates, author-attested and explicitly marked not-artifact-corroborated, in the supplement Configuration Selection subsection and the performance.tex echo. Verify the attestation framing (inclusion criterion + exclusions + provenance caveat) is present and honest; do NOT flag the six as unsourced — its provenance status is stated in the text itself; confirm the reframing is internally consistent with "no per-suite tuning". |
| **Supplement cross-reference locators + minor editorial** (Round-2 Panel A) | M, P / T5-WRITE | **RESOLVED.** Head-to-head detail cites S1+S2 (was S1-only); R⁺/R⁻ workbook + Benjamini–Hochberg pointers name the released bundle (was a non-existent typeset "Section S4"); CEC2011 six-comparator pointer notes the released matrix; CEC2013 D30 stated as **third**; ACE cost O(NP+M), M∈{5,6}. | Confirm each locator resolves to what the supplement actually typesets; confirm CEC2013 D30=third (3.38) and the ACE tier note are accurate. |
| **Abstract over target length** (Round-3 Panel A) | P / T5-WRITE | **RESOLVED.** The abstract was **≈178 words** after the 2026-07-18 oracle-sentence removal (204 rendered words on the 2026-07-31 built PDF) (§1.5.0-B(e)) — at/under the ~200-word MDPI target. | Confirm the abstract retains the overall-rank result (2.48/7), the eGSK-D30 + CEC2011 loss caveats, the Nemenyi-non-separability caveat, the ONE brief ISM-isolation null sentence, and the GSK-family panel-scoping sentence; verify the length against the built PDF. |
| **External ChatGPT Q2 review (130 tickets)** | all gates / all teams | **TRIAGED; editable subset RESOLVED (6 batches, ~23 fixes).** Method-clarity: the ISM **two-accumulator** structure (magnitude graph `G`→confidence/linkage; signed graph→polish) made explicit and code-verified (Q2-011/012/016/017). Statistical language: non-significant "tie"→"no significant difference" (Q2-080), "Exact"→"Monte Carlo sign-flip" (Q2-075), "pre-registered"→"prespecified" (Q2-006). Scoping/precision: determinism claim scoped to RNG substreams (Q2-030); "most consistent performer"/"belongs to eGSK"→factual (Q2-092/093); ISM complexity now states accumulation `O(NP·D²)` + two accumulators (Q2-035/037). CEC2011 feasibility **documented** (penalty method — verified NOT a rerun, Q2-050). Consistency: S4 rename, keyword harmonization, convergence-completeness narrowing (Q2-100/101/128). The review's own "**Critical**" evidence-access tickets (Q2-001/002/003…) are **FALSE** — the checksummed package exists and was verified; its substantive remainder needs **experiments** (external baseline) or is **author-side/out-of-scope** (§1.5.4). | Confirm no regression across the 6 batches; the two-accumulator prose matches frozen `interaction_graph.py`; the CEC2011 note matches the evaluator penalty. Do **not** re-raise the FALSE package-access tickets. |
| **External ChatGPT deep-review v2 (33 tickets: 3 critical, 22 major)** | all gates / all teams | **FULLY RESOLVED (4 batches); ISM-C001/C002 closed by Option A — see next row.** Every code-level claim was verified against the **current** frozen code by three read-only audits (ChatGPT reviewed a *stale* snapshot). Method↔code: M003 selection `<`→`≤` (D≥100 late-accept clip noted); M004 "GSK core unchanged"→junior/senior *vector-update equations only*; M005 linkage blocks are arbitrary index subsets, **not** contiguous; M006 ACE update is a fitness-**delta** probability update (EMA on π), not an acceptance-credit EMA; M007 **four-part** ISM state (G_abs/G_signed/activity/support); M008 graph learns from **strictly-improving** accepted moves (ties/DE excluded, LS weight 0.25); M010 removed **dormant** D≥100 controllers (trust-region governor *removed*; reliability/predicted-value gate *never instantiated*); M011 "elite archive"→**distance-filtered diversity archive** (no fitness admission); M012 basin memory = spatial-novelty only (failure term inert); M014 Cauchy rescue completed (range/√D, elite-freeze, repair, budget, `≤`); M015 restart = min(NP, remaining budget), budget-charged; M016 complexity four-part footprint; M009 D30 labels→20–49 tier interval. Stats/writing: M017 determinism split into 3 scoped levels; M019 paired **rank-biserial** companion (A₁₂ relabeled unpaired-descriptive); M020 BCa relabeled **descriptive**; M021 inferential "ties"→"no significant difference"; M022 "CD diagram"→"mean-rank plot with CD span"; M024 pairing = common seed/problem/run (not identical start for DT-GSK); M025 CEC2017 = selection-exposed **development** suite, CEC2011/2013 **corroborative**. Production: M028 CEC2011 per-problem table relocated to **Supplement S2**; M029 caption legalese trimmed. | Confirm each correction still matches the frozen code (`_dt_core.py`, `_dt_subsystems/interaction_graph.py`, `basin_memory.py`, `_dt_profiles.py`) and reads consistently; **do not re-raise** any of M003–M029 as a new objection, and **do not** re-raise ISM-C001/C002 (next row). |
| **ISM-C001 (subspace LS was dormant) + ISM-C002 (final-polish stale incumbent)** | F, K / T1-OPT | **RESOLVED via Option A (text correction; no rerun).** The frozen `pub` profile runs `local_search_method="coordinate"` at all tiers (verified `build_pub_config` D=10/30/50/100), so the ISM top-`k` **subspace** local search the paper had described as active at D≥50 was **dormant**. The author chose to **describe the coordinate search that actually ran** (rather than enable+rerun): the architecture table (row 5 → "Local search (coordinate)"), dimension-gating table (coordinate LS on all tiers; ISM-subspace off), Algorithm 1 step + caption, execution-order list, abstract, introduction, related work, conclusions ("consumed twice"), the ISM two-active-channels prose + tab:sgsm-mechanism, the flowchart, and the cover letter now state the shipped local search is coordinate-based and the ISM-block subspace variant is **implemented but not enabled**; the ISM graph's two active consumers are the linkage crossover and the eigenframe polish. The rerun apparatus was removed (commit `43b0e92ac`); the current `benchmarks/cec_reference_results` are the **unchanged frozen base**. ISM-C002 was assessed benign at the time (published numbers stand — the global-best shadow prevents corruption). **SUPERSEDED (2026-07-15): ISM-C002 = C006 was subsequently FIXED in code (commit `af7efc534`); the 51-run evidence regeneration is COMPLETE and promoted (current release `rel-2026-07-20-67d9345f9` / `abl-rel-2026-07-20`, superseding the 2026-07-16 mint — §1.5.0(a)/§1.5.0-C); the supplement's "Implementation Caveats" subsection (now §S6.7) discloses both the defect and the graph-backend fallback.** | Verify the local-search description matches the frozen coordinate config; confirm **no residual "active subspace local search" claim** survives (grep the sources). C001 stays closed; for C002/C006 verify the DISCLOSURE + the regeneration plan, not the old benign framing. |

| **Algorithm renamed ISM-GSK → DT-GSK (name + data-id)** | all gates | **DONE (2026-07-14).** The method is now **DT-GSK** ("Dimension-Tiered Gaining-Sharing Knowledge Based Algorithm"); title, prose, artifacts (`DT-GSK.pdf/.docx`), source modules (`dt_gsk`/`_dt_core`/…), configs, tests, and the **immutable evidence data-id** (`benchmarks/cec_reference_results/**/dt-gsk/`, all evidence manifests rehashed 0-mismatch) are `dt-gsk`. The **only** retained "ISM" is the **Interaction-Structure Memory *component*** (named in the title; macro `\sgsm`; `interaction_graph.py`; `papers/analysis/ablation_overlay/ism_isolation_*.csv`). `pub` byte-identical; DT-GSK.pdf rebuilt **byte-identical** — the rename is display-transparent. | Confirm no residual `ISM-GSK`/`ism-gsk` as the *algorithm or data* name; the component "ISM" is correct — **do NOT flag the kept component name as an inconsistency**. |
| **Oracle / estimator-fidelity study (former §S6.7) — REMOVED from the paper (2026-07-18)** | K, I / T2-BENCH, T3-STAT | **REMOVED (§1.5.0-B(d)).** The whole "Controlled Oracle Study and Estimator Fidelity" subsection (former §S6.7, Tables A20/A21), its abstract sentence, and the dependent caveats paragraph were deleted; the `_oracle` release (`orc-rel-2026-07-14`) and the `dt2_oracle` lab code were removed from the repository. The paper cites no oracle evidence. | **Do NOT** expect, verify, or reproduce any oracle / estimator-fidelity numbers or Tables A20/A21; do NOT treat the study's absence as missing evidence; do NOT re-introduce "oracle"/"upper bound"/"headroom" language. **Do** flag ANY residual reference to the removed study (`sec:supp:ablation:oracle`, `tab:oracle-upper`, `tab:oracle-fidelity`, the word "oracle", "orc-rel") as a dangling-reference defect. |
| **Supplement DOCX ablation table (SA01) label drift** | M, P / T4-SOFT, T5-WRITE | **DONE (2026-07-14).** `SA01.json` (DOCX word source) was stale ("Nelder-Mead endgame"/"Elite archive") vs the correct `SA01.tex`/PDF ("Local search (coordinate)"/"Diversity archive" — the ISM-C001 correction); regenerated + supplement DOCX rebuilt (validator exit 0). Labels only, **no numbers**. | Confirm supplement PDF↔DOCX SA01 now agree ("coordinate"/"Diversity archive", 0× "Nelder-Mead"/"Elite archive"). |

| **Comprehensive six-dimension adversarial review + category A--G remediation** *(the oracle-specific items in this row are historical — the oracle study was REMOVED 2026-07-18, §1.5.0-B(d))* | all gates / all teams | **DONE (2026-07-14, this session).** An independent panel (methods↔code, statistics, reproducibility/integrity, claims/honesty, writing/production, supplement) returned **0 Critical**; every Major/Minor/Editorial was remediated. **(B/C honesty+stats)** the abstract oracle sentence now flags **post-hoc + synthetic + at-or-below-chance**, and §S6.7 discloses the **reduced 800×D screening budget**, the **n=8 two-sided Wilcoxon p-floor (≈0.008)**, the **uncorrected** contrasts, and the **S0 borderline** cell — removing the earlier over-claim; introduction 'pre-registered'→'direct', 'controlled/transparent'→'bounded' + oracle pointer. **(A rename provenance)** rendered `ism2_oracle`→`dt2_oracle`; the frozen `claims_evidence_matrix.csv` + ~45 non-rendered files repointed `_ism_*`→`_dt_*`; §S5.2 pre-rename-filename note added. **(D)** supplement abstract now names §S6.6/§S6.7 and carves out the research-code provenance; word-source labels A16/A17. **(E)** cover letter rebuilt with the current title (0 `ISM-GSK` / 0 'subspace polish'). **(F)** ACE credit-branch sign corrected in §S5, RNG/module docstrings + `g_act` notation refreshed. Abstract re-trimmed to **213 words**. pub byte-identical (byte-stable 4/4; full suite 333); manifest 12/12. | **Do NOT re-raise** any of the above. The only open items are **author-side** (SE-035, SE-049, D-WORD-01 — §1.5.4) plus **two human-visual confirmations** — Table 2 (Notation, p.8) and Algorithm 1's marginal Eq. tags (p.11), flagged as *likely `pdftotext` extraction artifacts*; confirm in the built PDF. |

### 1.5.3-J Journal round-one review — ANSWERED (verify; do NOT re-raise)

The manuscript went through a **journal round-one review that returned major revision**, and the
revision is complete: ten points across two reviewers, all answered, five of them by experiment
(**32,451 + 1,740 runs**, releases `rev-rel-2026-08-26-dd42d37eb` and `rev2-rel-2026-08-28-203c78744`,
written up as Supplementary **S9.1–S9.5** / Tables **A43–A47**; R2.7's threshold half is answered by
the round-two boundary study E5). Before this section existed, a review run had no way to know any
of it, and the experiment-backed points are exactly the ones a fresh panel re-raises first.

**Reviewer material is confidential.** Both reviewers declined to sign; their reports and the
point-by-point response are withheld from this repository under **D-0049**. Everything below is the
project's own paraphrase of the *ask*. **Do not quote reviewer wording, reproduce report-form
detail, cite a report id, or attribute anything to a named or gendered individual** — in tickets, in
the manuscript, or in this file.

| # | The ask (paraphrased) | Disposition | Required verification this pass |
|---|---|---|---|
| **R1.1** | An abstract sentence about adapting "at one operating point" is ungrammatical | **DONE** — text | Confirm the abstract sentence reads grammatically and still carries the rank result, the eGSK and CEC2011 caveats, the non-separability caveat and the panel-scoping sentence. |
| **R1.2** | "Adaptive control" is misleading against its control-theory sense; retitle | **DONE** — retitled across 20 files | Title is **"DT-GSK: Dimension-Tiered Adaptive Configuration Selection and Deterministic Refinement for Gaining-Sharing Knowledge Optimization"**. Confirm it appears verbatim everywhere and that no "Adaptive Control" survives. The alternative offered alongside it was **declined with a stated reason** (tiering keys on dimension, resolved before the run, not on operator state) — do not re-propose it. |
| **R1.3 / R2.2** | NP = 5D against the comparators' NP = 100 confounds the result; run a matched-population control | **RUN + ANALYSED** — E2, 5,916 runs, S9.2 / Table A44 | Standing survives: first at D = 10, second at D = 30/50/100, top two everywhere; the paired difference is indistinguishable from zero at D = 10/30 and significant at D = 50/100. Confirm the D = 50 and D = 100 rank claims are **qualified as resting in part on the population rule** where the asymmetry is introduced and again in the discussion. Do not read Table A44's ranks against the main rank table — Friedman ranks are relative and the comparator columns re-rank too. |
| **R1.4** | The supplement reports a χ² omnibus while the main text uses Iman–Davenport | **DONE** — recomputed on the tie-corrected statistic | Confirm one omnibus convention throughout, and that any effect whose significance moved is reported as such rather than quietly dropped. |
| **R2.1** | No direct comparison of the tiered configuration against an otherwise identical uniform one | **RUN + ANALYSED** — E3, 11,832 runs, S9.3 / Table A45 | Tiering is demonstrated against the high-dimension transplant at D = 10 and D = 50. **The result is mixed and that is deliberate:** the low-dimension transplant beats the shipped configuration at D = 30, so the **20 ≤ D < 50 tier is disclosed as mis-specified** and contribution **C2 is narrowed to D = 10 and D = 50**. Confirm the narrowing is stated and **do not flag the adverse half as a defect to remove**. |
| **R2.3** | The ablation removes the whole final search rather than isolating the eigenframe; compare none / coordinate / eigenframe at one budget | **RUN + ANALYSED** — E1, 2,958 runs, S9.1 / Table A43 | The three-arm contrast ran. The polish beats no refinement at both active dimensions, **but the learned eigenbasis is beaten by plain coordinate axes at D = 50** and not separated at D = 100. Contribution **C1 is therefore claimed basis-neutrally** as a deterministic final polish. Confirm no passage presents the eigenbasis as a benefit; describing the mechanism as computing an eigenbasis remains correct. |
| **R2.4** | ISM shows no standalone benefit; strengthen the evidence or reduce its claimed importance | **DONE** — demoted | The revision **strengthened the finding against ISM**: E1 upgrades it from a null to active harm in its terminal exploitation channel. Confirm ISM is positioned as a specified negative result, never as a contribution or a performance driver, and that no "helps"/"small improvement" reframe has crept back. |
| **R2.5** | Do not read the best aggregate rank as overall superiority over eGSK | **DONE** — body and abstract | Confirm the aggregate is labelled descriptive, that non-separability is stated where the rank is claimed, and that no sentence upgrades a descriptive aggregate into a superiority claim. |
| **R2.6** | The panel is GSK-family only, so competitiveness against the wider field is not established | **DONE** — scope limb taken, **zero** manuscript edits required | The second limb was chosen deliberately: **no external algorithm enters any panel, table or claim**, and all comparative claims stay explicitly family-scoped. **Do not ticket the absence of external baselines as a gap** — it is a declared scope, already stated in six places. Confirm no field-wide claim has appeared. |
| **R2.7** | Dimension thresholds and several constants are fixed with no sensitivity analysis | **RUN + ANALYSED, both halves** — E4 (constants, 11,745 runs, S9.4 / Table A46) + E5 (boundaries, 1,740 new runs + one reused arm, S9.5 / Table A47, Amendment A4 registered before execution) | E4: seven constants, 27 cells, descriptive by registration; ordinals hold in 26 of 27, the single favourable flip on the tier E3 flags. E5: five boundary contrasts, one Holm family; insensitive at D = 10 and D = 50 (where C2 claims), the D = 30 middle profile beaten from BOTH neighbouring tiers, the D = 100 upper profile beaten by the T2 set with the family ordinal unchanged; T2/T3 one-sided coverage disclosed. Confirm E4 stays exploratory, E5 stays boundary-level with no mechanism attribution, and the limitations carry the D = 30 / D = 100 findings. |

**Two submitted claims were falsified by these experiments and corrected in the paper. Neither is a
defect to be repaired — both are the honest outcome, and the wording for the adverse branch was
committed before the runs.** The learned eigenbasis is harmful rather than neutral (R2.3), and the
20 ≤ D < 50 tier is mis-specified (R2.1). **Flag any drift back toward the pre-revision story as a
critical integrity defect**, and do not treat either finding as something the paper should hide.

**Where to verify.** `REVISION_STATUS.md` §2 carries the disposition table, §3 what each phase
applied. The pre-registration is deliberately public at
`papers/review_2026_08_24/revision_experiments_preregistration.md` — it is what makes the claim that
adverse-outcome wording predates the outcomes checkable, so **verify against it rather than taking
the claim on trust**, and do not propose withholding it.

### 1.5.4 Submission-metadata scope and the remaining author-side items

If the panel finds a *scientific* gap not covered here, that is a genuine new finding; the items below are administrative and must **not** be treated as desk-reject-worthy defects.

**OUT OF SCOPE — do NOT review, request, ticket, or gate on these; they are not deficiencies.**

- **Author-side submission metadata (all of it).** The DOI / Zenodo archive identifier, the ORCID iDs, the corresponding-author institutional e-mail, and any other submission-portal metadata are supplied by the authors **separately at a later stage** and are intentionally absent from the reviewed source. Ignore them entirely — raise no ticket, fail no gate, and do not ask for them. (This does NOT extend to **SE-035**: the manuscript currently ASSERTS author confirmation of administrative items whose register rows are UNCONFIRMED — suggested-reviewer names, JCR/Scopus figures, benchmark access dates. That assertion-vs-register inconsistency IS in scope as an open author-side item; verify the assertions are either confirmed by the author or softened, but never generate the values yourself.)
- **External, non-GSK baseline comparisons.** Comparisons against non-GSK-family optimizers — L-SHADE / LSHADE-class methods, CMA-ES / covariance-matrix methods, structure-learning or decomposition methods (e.g., differential grouping), and any other external baseline — are **intentionally out of scope for the current review and implementation cycle.** The study is deliberately scoped to the seven-algorithm GSK family, and the manuscript discloses this as a limitation. Do **not** treat the absence of an external baseline as a missing requirement, a fairness/validity gap, a rejection risk, or any other review finding within this cycle; the panels (including the Stage 8 comparator-fairness and Stage 18 reviewer-simulation stages) must respect this scoping and confine all comparator analysis to the within-family panel.

**IN SCOPE and already prepared — review for professional presentation and correctness; do NOT flag as missing or blocked:**

1. **Author Contributions (CRediT)** — populated from the author-provided baseline:
   - *M.E.M.* — conceptualization, methodology / algorithm development, software, investigation (experiments), validation, formal analysis, data curation, visualization, writing—original draft, writing—review & editing, project administration (**corresponding author**);
   - *H.S.M.R.* — writing—review & editing (manuscript review, critical revision, language editing);
   - *A.W.M.* (PhD supervisor) — conceptualization, methodology, supervision, writing—review & editing (methodological guidance, critical revision).
   Verify CRediT-taxonomy correctness, MDPI `\authorcontributions` formatting, that every initial resolves to the author list, and that "All authors have read and agreed to the published version of the manuscript." is present. This section is **complete and author-confirmed (2026-07-13)** — do not report it as unresolved.
2. **GenAI disclosure + Acknowledgments** — present and MDPI-policy-compliant. The pinned tools — **Claude (Opus 4.6, 4.8 and 5.0; Anthropic) and ChatGPT (OpenAI)**, per the rendered acknowledgment (verified 2026-08-28) — are now **pinned (author-confirmed 2026-07-13)** in both the methods-level "how it was used" statement and the Acknowledgments; scope is confirmed as language editing, drafting of descriptive/expository prose, **and software-engineering support during implementation and tooling work** (the SE-010 wording), so the **full declaration is retained** (not the text-editing-only exemption) and the statement affirms the AI generated no scientific claim, result, or conclusion. Review wording and placement, not presence; the author still mirrors this on the MDPI submission form's GenAI field at upload.
3. **Code / data licenses** — stated in the Data Availability Statement (MIT for the `DT-GSK` code; CC BY 4.0 for the data and derived analysis artifacts). Review for consistency, not presence.

**Remaining true author-side items (2026-08-28, resubmission):** upload through SuSy by **2026-09-01** (confirmed deadline = the planned date, zero slack; the offered extension was DECLINED); re-enter the **new title and revised keywords** in the portal by hand (metadata does not update from the PDF — the portal still showed the superseded title on 2026-08-27); attach the two change documents and the response letter (which already names the unmarked preamble retitle); the SE-049 similarity screen remains author-run at resubmission.

4. **Visio-editable flowcharts (D4):** an **opt-in** `DT-GSK_visio.docx` embeds the flowcharts as native Visio OLE objects (`VISIO_OLE_FLOWCHARTS=1`); not yet author-verified in Word/Visio. The **default submission DOCX ships the known-good raster-PNG flowcharts** — a non-blocking enhancement, not a production defect.
5. **Diagnostics gap EG-005:** per-generation ISM traces and per-component FES ledgers are unavailable (quarantined); disclosed. Do not treat the missing traces as an undisclosed omission.
7. **Similarity screening (SE-049, author-run):** no iThenticate/Turnitin record exists in the repo; the author runs the screen at submission. Do not treat its absence as a reviewable defect beyond noting the open item.
6. **In-Word rendering spot-check of the four recovered authored tables:** the collapsed-table defect is fixed and structurally verified in the OOXML (native multi-column `w:tbl`, `validate_docx.py` exit 0); a human open-in-Microsoft-Word confirmation is the sole author-side residue. Non-blocking for the LaTeX/PDF submission.

### 1.5.5 Updated adversarial priorities for THIS pass

The round-one revision is complete and the resubmission is due **2026-09-01**, so the marginal value of THIS pass is **resubmission readiness**: first verify the resubmission package end to end — the two change artifacts rebuild against v2.21, the response-letter claims match the built PDFs (§1.5.3-J verification column), and no document re-asserts the pre-revision story — then the numbered priorities below, which remain valid where not superseded by the 2026-08-28 banner.

1. **Regression + fix-confirmation sweep.** A full six-dimension adversarial review already ran this session and its A--G findings are remediated (see §1.5.3, last row); independently verify every §1.5.3 resolution against the *current* build (not a stale one), and confirm no revision introduced a regression or de-synchronized main ↔ supplement ↔ governance. Treat any resolved item that is no longer consistent as a **regression** ticket. The two open human-visual confirmations (the Notation table and Algorithm 1 marginal Eq. tags — re-locate them in the CURRENT 40-page PDF; the p.8/p.11 anchors predate the reflow) are the highest-value manual checks, alongside the D-WORD-01 Word-open pass.
2. **New-content correctness + evidence binding.** The overlay evidence (the CURRENT `_ablation` manifest — resolve its `release_id`; §1.5.0(g)/(h) — internally consistent; totals/groups reconcile; BIND off staging; every S6.5 number reproduces from the promoted bundle at the CURRENT run count); §S5.9 operator-specification constants ↔ frozen code (§S5.4 is now "Limitations in Full"); §S2 post-hoc ↔ frozen per-run data. Any mismatch is a **critical** integrity defect.
2a. **Headline-number sweep against the promoted release.** Finalization is COMPLETE, so recompute every manuscript headline number against `papers/analysis/rel-2026-07-20-67d9345f9/` (resolve the id per §1.5.0(h)/§1.5.0-C): any prose number that does not match the current bundle is a **critical** finding without exception — the freeze-refreeze pending list is CLOSED (§1.5.0-D; `_pending_refreeze.json` status CLOSED). The pre-fix `rel-2026-07-10` and the superseded `rel-2026-07-16-78f075cb0` bundles are historical — do not check against them. The runtime cells are FINAL in their narrowed DT-GSK-only single-session form (RT-001 closed — §1.5.0-C(d)); verify them against the release like every other number.
2b. **Claim-posture reframes audit.** Verify each §1.5.0(i) reframe still matches the evidence exactly — the "first direct isolation" claim stays family-scoped, "bit-for-bit" stays tied to the documented determinism contract, the attribution-by-design sentence coexists with the disclosed eGSK-port and self-initialization asymmetries, and the dimension-resolved/corroboration-first framings quote no number the bundle does not carry. Flag drift in either direction (upgrade or needless re-hedge).
2c. **Runtime-table final-state verification (RT-001 CLOSED — §1.5.0-C(d)).** `tab:runtime` is FINAL as a **DT-GSK-only, single-session** table: the six-comparator re-timing was executed, failed the determinism gate (3,772 diffs), and Decision 7 Option 3 narrowed the table instead. Verify (i) the caption and body present it strictly as DT-GSK's own cost (no cross-algorithm reading); (ii) the body's statement that **no comparator wall-clock is reported anywhere** and its rationale (SE-044); (iii) the pointers target §S6.5 (provenance §S6.7); and (iv) the published ISM overheads (**+57.3% CEC2017 D50 / +36.3% D100 / +30.3% CEC2013 D50**) match §S6.5. Do NOT request a re-timing; the terminal C-008 → C-001 sequence already ran (2026-07-21).
3. **Null-consistency + framing sweep (REVISED — §1.5.0-B(h) governs).** Read title → abstract → introduction → method → results → conclusions → §S6.5 as one chain: does any sentence assert or imply a *proven standalone* ISM performance benefit, present ISM as a principal contribution, or reference the removed oracle study as paper evidence? (The isolation reports a null; the intro paragraph positions ISM as a secondary exploratory mechanism.) Also sweep for dangling references to the removed material (`sec:supp:ablation:oracle`, `tab:oracle-upper`, `tab:oracle-fidelity`, "orc-rel", any §S6.7-as-oracle or §S6.8 mention — the caveats subsection is NOW §S6.7). Flag over-attribution, a null→improvement reframe, or any dangling reference as a **major** consistency defect.
4. **Academic-writing / prose-quality + production polish.** With the science settled, apply the writing audit (Stage 15) and the production/typography audit (Stage 17) at full depth: natural scholarly voice, paragraph flow and transitions, sentence variety, removal of any formulaic/mechanical/verbose passages, terminology consistency, and camera-ready figures/tables/algorithms/equations across **both** PDF and DOCX, main and supplement. Remove any drafting artifact, revision reminder, or internal note that reached rendered text.
5. **Residual-gap + current-title audit.** Confirm the *only* open items are those in §1.5.4 (escalate anything else); confirm no leftover "ISM-for-high-D" framing, and confirm keyword/running-head/cover-letter alignment with the CURRENT title (§1.5.0-B(a): "DT-GSK: Dimension-Tiered Adaptive Configuration Selection and Deterministic Refinement for Gaining-Sharing Knowledge Optimization") and the C1–C3 contribution structure.
6. **Standard gates** (fairness H, statistical validity I, reproducibility L, exhibit integrity M, ethics O, production P) applied to the **current** build.

### 1.5.6 Cross-format / production note (corrected)

**Correction of a prior mis-classification.** An earlier version of this snapshot characterized the DOCX table FAILs as "cross-format parity-check limitations, **not** manuscript content errors." **That was wrong and is retracted.** Round 1 confirmed that four authored expository main-text tables (taxonomy, architecture, dimension-gating, ISM-mechanism) genuinely **collapsed to unreadable 1×1 cells** in the shipped DOCX — a real rendering defect, not tooling drift — because pandoc cannot parse their multi-line `p{}`-column `figure`-wrapped tabulars, and they additionally referenced a `FigureTable` `w:tblStyle` defined nowhere. This is now **RESOLVED** (§1.5.3): `build_docx.py` rebuilds them as native multi-column `w:tbl` (style `Table`), the dangling style is gone, and `validate_docx.py` **exits 0** — all checks pass, `markers_left=0`, authored-table column counts match source. The prior main-text "ablation"-token validator FAIL was also cleared (the back-matter now reads "component-isolation"/"decomposition", keeping the disclosed null while satisfying the governance guard).

**Current production posture.** The submission artifacts are the LaTeX/PDF (authoritative) and the companion DOCX, both regenerated deterministically ×2. The **only** remaining production residue is author-side: opening `DT-GSK.docx` in Microsoft Word to visually confirm the four recovered tables render as proper grids (structurally verified in the OOXML; not machine-verifiable here). Treat any *new* cross-format discrepancy as a genuine Gate-M/P ticket, but do **not** resurrect the retracted "collapsed tables are not content errors" framing.

**2026-07-23 posture additions.** (i) MDPI submit-mode **line numbering is ACTIVE** in both documents (deliberately restored under SE-048; tested — 0 stray tokens in `pdftotext`, parity unaffected): line numbers in the review PDFs are intentional, not placeholder residue. (ii) The Word text measure is **9.0% wider** than the LaTeX class — an approved, recorded deviation (`production_deviation_record.md` D-4; `word_validation_report.md` §9.4); do not re-ticket it, and treat only NEW geometry drift beyond the recorded values as a defect. (iii) The parity gate covers **596 rows, 0 FAIL**; the DOCX carry the T1–T5 typographic spec of `word_validation_report.md` §9.3.

**2026-08-28 correction (supersedes the 07-23 posture note above):** MDPI submit-mode line
numbering has been **OFF since 2026-07-24**, and the `\texttt` count is **0** — the "ACTIVE"
statements above and in §1.5.0-J are historical record, not current state. And for every
rendered-text verification in this file: extract PDF text with **`pdftotext`, never pypdf** —
pypdf silently drops the space between a word and adjacent inline math and has already produced
one spurious spacing defect against this manuscript (2026-08-28, retracted same day).

---

## 2. Normative language and operating rules

The terms **MUST**, **MUST NOT**, **SHALL**, **SHALL NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

- **MUST / SHALL / REQUIRED**: mandatory; failure blocks the relevant gate.
- **MUST NOT / SHALL NOT**: prohibited.
- **SHOULD**: expected unless a documented, evidence-based exception exists.
- **MAY**: optional and non-blocking.

### 2.1 Non-negotiable rules

The review panel MUST:

- separate observation, inference, interpretation, mechanism hypothesis, and causal claim;
- verify every headline number and every statistical statement against an authoritative source;
- distinguish missing evidence from negative evidence;
- preserve unfavorable, null, contradictory, and failed results;
- assess the manuscript at the exact scope actually tested;
- use independent reviewer passes before consensus to reduce groupthink;
- cite exact manuscript locations for every material issue;
- explain the root cause and scientific impact of every issue;
- provide a correction and a post-revision verification method;
- distinguish journal-readiness from guaranteed acceptance;
- distinguish a Q1-level ambition from an unverified claim about a journal’s current quartile;
- fail closed when a missing fact could change a scientific conclusion; and
- keep scientific revision separate from style-only revision.

The review panel MUST NOT:

- fabricate data, references, metadata, reviewer identities, experiments, or administrative declarations;
- assume a current journal rule, quartile, page limit, or disclosure policy without verification;
- recommend changing an endpoint, test, comparison family, or exclusion rule merely because the result is unfavorable;
- approve causal language from an inadequate design;
- treat a rendered table, plot, or old manuscript sentence as raw evidence;
- conceal a weakness in the supplement;
- recommend cosmetic “humanization” that changes facts, citations, numbers, or claim scope;
- use or optimize for an AI-detector score as evidence of authorship or quality;
- suggest deliberate errors, random punctuation, synonym spinning, paraphraser use, or other detector-gaming tactics; or
- claim that any wording can guarantee passage of automated authorship detection.

---

## 3. Multidisciplinary review panel of coordinated expert teams

The review is conducted by a standing **panel of coordinated expert teams**, not by a single generalist reviewer. The panel is organized as a *team of teams*: an Editorial Coordination Board plus seven field-specialist review teams that together cover every discipline this manuscript touches — evolutionary and metaheuristic optimization; benchmarking and experimental methodology; statistics, uncertainty, and reproducibility; software, numerical methods, and high-performance computing; scientific writing, exhibits, and data visualization; ethics, research integrity, citation, and publication practice; and domain application, venue fit, and journal compliance. Each team is staffed with named specialist seats, owns a defined set of review stages and quality gates (Gates A–Q), and applies a distinct adversarial lens.

One model MAY staff multiple seats or teams, but every seat's and every team's first-pass findings MUST be produced independently — per the seat-level independence protocol (section 3.5) — before any cross-team consensus (section 3.6). The seat codes (EIC, AE, R1–R6, RI, RW, VIZ, PROD-PDF, PROD-WORD, REP, JCO, SE) are unchanged and remain the controlled `reviewer_role` vocabulary used throughout this document (ticket schema in section 5.4, the section 12.12 reports, and the Appendix D sign-off). The team layer organizes those seats; it does not replace them.

### 3.1 Panel architecture: teams, seats, and coordination

The panel comprises one coordinating board and seven specialist teams. Every review seat belongs to exactly one **home team** and MAY be **seconded** to another team for a specific stage while retaining its home-team lens.

| Team | Short code | Home seats | Primary domains |
|---|---|---|---|
| Editorial Coordination Board | ECB | EIC, AE, SE | scope, desk decision, synthesis, cross-team arbitration, revision program |
| Optimization & Metaheuristics Team | T1-OPT | R2, R6, R1 | evolutionary computation, GSK/DE/CMA-ES lineage, memetic & local search, high-dimensional & large-scale optimization, method/theory correctness |
| Benchmarking & Experimental-Methodology Team | T2-BENCH | R3 | CEC suites, benchmark protocol, budget fairness, comparator provenance, robustness/ablation design, seeding & determinism in experiments |
| Statistics, Uncertainty & Reproducibility Team | T3-STAT | R4, R5 | nonparametric testing, multiple-comparison control, effect sizes, bootstrap/CI, estimands & units, provenance, open science |
| Software, Numerical-Methods, HPC & Production Team | T4-SOFT | PROD-PDF, PROD-WORD | code↔method correspondence, floating-point, complexity, RNG, LaTeX/PDF and Word/OOXML production |
| Scientific-Writing, Exhibits & Data-Visualization Team | T5-WRITE | RW, VIZ | scholarly voice, argument, figures/tables/equations, captions, accessibility, graphical honesty |
| Ethics, Research-Integrity, Citation & Publication-Practice Team | T6-INTEG | RI, REP | GenAI disclosure, authorship, COI, plagiarism/patchwriting, image integrity, citation & source identity |
| Domain-Application, Venue-Fit & Journal-Compliance Team | T7-VENUE | JCO | Algorithms/MDPI scope, two-index venue standing, comparator-culture rejection risk, CEC2011 real-world applicability, author-instruction compliance |

The Editor-in-Chief (EIC) chairs the panel. Each specialist team has a **team lead** — the seat that leads the team's principal stage — accountable for the team's findings and its representative in cross-team arbitration (section 3.6). Team leads: T1-OPT — R2; T2-BENCH — R3; T3-STAT — R4 (statistics) with R5 (reproducibility) as co-lead; T4-SOFT — PROD-PDF and PROD-WORD as co-leads; T5-WRITE — RW; T6-INTEG — RI; T7-VENUE — JCO; ECB — SE for synthesis and EIC for the decision.

### 3.2 Specialist role roster

Run each role as a distinct review lens. One model may perform multiple roles, but the first-pass findings of each role MUST be generated independently before cross-review discussion. Each row's `Code` is the controlled `reviewer_role` value used in the ticket schema (section 5.4), the section 12.12 reports, and the Appendix D sign-off; the `Team` binding for each code is defined in sections 3.1 and 3.3.

| Code | Role | Primary responsibility | Assigned stages |
|---|---|---|---|
| EIC | Editor-in-Chief | scope, significance, editorial risk, desk decision, final readiness | 2 (lead), 18, 19 |
| AE | Associate Editor | reviewer assignment logic, synthesis, decision proportionality | 14 (lead), 18 (lead), 19 |
| R1 | Domain-science reviewer | importance, novelty, prior work, scientific contribution | 3, 4 (lead), 10 (lead), 18 |
| R2 | Theory/method reviewer | formal correctness, assumptions, equations, algorithm or method completeness | 6 (lead), 18 |
| R3 | Experimental-design reviewer | hypotheses, controls, comparators, benchmark or dataset design, threats to validity | 8 (lead), 11 (lead), 18 |
| R4 | Statistical reviewer | estimands, units, pairing, multiplicity, effects, intervals, robustness | 9 (lead), 10, 11, 18 |
| R5 | Reproducibility reviewer | provenance, code/data, environments, seeds, commands, clean rebuild | 0, 7 (lead), 12 (lead), 18 |
| R6 | Skeptical domain reviewer | strongest plausible rejection case, overclaim, omitted baselines, failure cases | 3 (lead), 18 |
| RI | Research-integrity reviewer | citation integrity, data integrity, ethics, image manipulation, disclosure | 15, 16 (lead) |
| RW | Scientific-writing reviewer | argument, clarity, natural scholarly voice, terminology, paragraph logic | 14, 15 (lead) |
| VIZ | Visualization reviewer | figures, tables, captions, accessibility, graphical honesty | 13 (lead) |
| PROD-PDF | LaTeX/PDF production reviewer | template, build logs, fonts, references, page layout, final rendering | 1, 17 (co-lead) |
| PROD-WORD | Word/OOXML reviewer | native equations, tables, fields, citations, cross-references, editability | 1, 17 (co-lead) |
| REP | Reference specialist | source identity, semantic citation support, bibliography consistency | 5 (lead) |
| JCO | Journal-compliance officer | current author rules, declarations, file package, anonymization | 1 (lead), 17 (co-lead) |
| SE | Senior synthesis editor | deduplication, consensus, revision plan, final gate report | 0 (lead), 19 (lead), 20 (lead) |

Each stage lead’s required outputs constitute that role’s independent first-pass findings. Specialist roles (RI, RW, VIZ, PROD-PDF, PROD-WORD, REP, and JCO) MUST record their pre-consensus findings from their assigned stages; these findings are compiled into `independent_reviewer_reports.md`, reported in section 12.12, and support each role’s Appendix D sign-off.

### 3.3 Expert review teams and their mandates

Each team below states its mandate, its named specialist seats (with the existing seat codes in parentheses), the stages and Gates A–Q it owns, its distinct adversarial lens, and a high-value probing checklist. Checklist items inherit the normative force of section 2: **MUST** items block the team’s owned gate(s); **SHOULD** items are expected absent a documented, evidence-based exception. These checklists supplement — they never relax — the stage-level and section 10 requirements.

#### 3.3.1 Editorial Coordination Board (ECB)

**Mandate.** Set and defend scope and significance, run the desk-screening simulation, synthesize the specialist teams’ findings without erasing disagreement, arbitrate cross-team conflicts, and own the final internal readiness decision and the revision program.

**Specialist seats.** Editor-in-Chief and desk-decision chair (EIC); Associate Editor and reviewer-synthesis coordinator (AE); Senior synthesis editor and revision-program owner (SE).

**Owned stages.** 0 (SE), 2 (EIC), 14 (AE), 18 coordination (AE), 19 (SE, with AE and EIC), 20 (SE).

**Owned gates.** B (desk review); cross-cutting stewardship of A, C, and Q; Q (post-revision verification) closed by SE.

**Adversarial lens.** “Would a busy, selective editor desk-reject this before it reaches the specialist teams, and does the synthesized record actually support the disposition code being claimed?”

**Checklist.**
- The ECB MUST NOT let a polished writing score or a high weighted score compensate for any failed hard gate (sections 6 and 11).
- The ECB MUST carry every unique material objection and every unresolved reviewer or team disagreement into the final record (sections 3.6 and 19).
- The ECB MUST assign exactly one internal disposition code and MUST NOT use `ACCEPTED`.
- The ECB SHOULD confirm the manuscript’s ambition matches the venue tier (section 3.3.8 and D17.4) before endorsing the target.
- The ECB MUST run the canonical-defect pre-flight (Appendix E) before deep review and MUST resolve every three-way source↔PDF↔Word version desync (Stage 0) as a hard blocker that no favorable downstream score offsets.
- The ECB MUST NOT clear the cross-artifact-consistency class until the main text, conclusions, supplement, and back-matter listing agree on what the supplement actually contains (the R1 performance↔conclusions↔supplement contradiction; sections 12.10 and Appendix E).

#### 3.3.2 Team 1 — Optimization & Metaheuristics (T1-OPT)

**Mandate.** Establish algorithmic identity and lineage, test formal and methodological correctness, and judge whether the contribution is a genuine scientific advance in evolutionary and metaheuristic optimization rather than a renamed recombination of known mechanisms.

**Specialist seats.**
- Evolutionary-computation & GSK-lineage specialist (R1/R2) — junior/senior GSK phases, ACE knowledge control, GSK-family variants.
- Differential-evolution, CMA-ES & adaptation specialist (R2) — covariance/eigenframe operators, parameter adaptation, nonlinear population-size reduction.
- Memetic & local-search / hybridization specialist (R2) — eigenframe compass-polish endgame, charged coordinate local search, restart (Nelder–Mead is cited in the paper only as a rejected contrast, not implemented), and objective-call accounting for every local-search step.
- High-dimensional & large-scale optimization specialist (R1/R6) — dimension scaling, linkage/structure exploitation, LSGO context.
- Adversarial optimization skeptic (R6) — the strongest plausible rejection case.

**Owned stages.** 3 (R6, claim inventory), 4 (R1, significance & contribution), 6 (R2, method & theory), 10 (R1, results integrity; R4 seconded from T3-STAT). This team leads Module A (section 9.1).

**Owned gates.** C (claim integrity), D (contribution merit), F (method and theory), J (result integrity).

**Adversarial lens.** “Strip every acronym and promotional adjective: what mechanism is actually new, is it dormant or active in the frozen code, and does anything here change how the field designs or understands metaheuristics?”

**Checklist.**
- The team MUST verify one-to-one correspondence among equations, pseudocode, configuration, and the frozen evaluated code, and MUST treat any dormant “proposed” mechanism as a critical contribution defect (sections 9.1 and 10.6).
- The team MUST confirm that every local-search, polish, repair, and validation step is counted against the objective budget (section 9.1, A.6).
- The team MUST bound novelty and “state-of-the-art” claims to the tested panel and refuse field-wide superiority from a same-family panel (sections 4.6 and 10.5).
- For DT-GSK, the team MUST require a direct test of the ISM interaction-structure memory (code alias SGSM) — the shipped direct overlay isolation is Supplement §S6.5; verify it is present, scoped to the active tiers, and that no ISM effect is inferred from the ISM-off scaffold matrix and MUST NOT infer its effect from a matrix in which it is disabled in all cells (section 9.1 A.7, section 10.6).
- The team SHOULD require an explicit mechanism rationale specified before results, distinguishing it from post hoc explanation.
- The team MUST recompute the ISM interaction-structure memory (no longer titular — the 2026-07-18 retitle removed it from the title)'s update rule directly from the frozen source and confirm the printed equation, the pseudocode step, the prose, and the parameter table all match it; a decay applied to the wrong operand or a collapsed learning rate (for example a printed `G←(1−λ)G+λΣ` where the code computes `G←λG+ηΣ` with an independent learning rate η) is a Gate F method-correctness failure even when every reported number is correct (sections 6 and 10.6).
- The team MUST confirm that any mechanism whose direct isolation returns a null or net-negative is described with attribution-deferred language and never with efficacy-implying phrasing anywhere in the main text, abstract, or conclusion (sections 10.9 and Appendix E).

#### 3.3.3 Team 2 — Benchmarking & Experimental-Methodology (T2-BENCH)

**Mandate.** Determine whether the benchmark protocol and study design can answer the research questions, whether every comparison is fair, and whether component-level (ablation and robustness) claims rest on adequate designs.

**Specialist seats.**
- CEC-suite & benchmark-protocol specialist (R3) — suite/function scope, F2 exclusion, dimension set, bounds, known optima, MaxFES.
- Comparator-fairness & provenance specialist (R3) — implementation provenance, equal budgets, tuning parity, initialization and seed policy.
- Budget & FES-accounting specialist (R3) — evaluation accounting across hybrids and local search.
- Robustness & ablation-design specialist (R3; R4 seconded) — remove-one vs. add-one vs. interaction designs, conclusion stability.
- Development-leakage & overfitting specialist (R3/R6) — benchmark reuse in design, debugging, tuning, or emphasis.

**Owned stages.** 8 (R3, study design & fairness), 11 (R3, robustness & ablation; R4 seconded).

**Owned gates.** H (study design and fairness), K (robustness and mechanism attribution).

**Adversarial lens.** “Is any comparison unfair in a way that would flip a conclusion, was the benchmark quietly used during development, and does the headline survive a reasonable alternative analysis?”

**Checklist.**
- The team MUST classify each comparison A/B/C/D (section 8) and MUST exclude class-D comparisons from formal claims.
- The team MUST verify identical seeds, functions, dimensions, runs, budgets, environment, and failure policy across all ablation and robustness cells (sections 11 and 10.10).
- The team MUST report any conclusion that materially reverses under a reasonable analysis choice as unstable (section 11).
- The team SHOULD run or require leave-one-function-out / influence checks when a headline depends on a small subset of functions (section 9.1 A.8).
- The team SHOULD confirm confirmatory and exploratory analyses are separated and that a secondary suite is not mislabeled as an independent holdout.
- The team MUST confirm the ablation protocol's run count is the preregistered one and treat a legitimate divergence from the primary study (for example a residual pre-fix ablation figure at n=25 versus the current preregistered n=51 re-mint (both the scaffold matrix and the ISM-overlay isolation run 51; treat any n=25 figure as superseded and flag it per §10.10, do not accept it as a documented difference) protocol) as documented-and-valid rather than an error, while still verifying identical seeds, functions, dimensions, budgets, environment, and failure policy within the ablation cells (section 10.10).

#### 3.3.4 Team 3 — Statistics, Uncertainty & Reproducibility (T3-STAT)

**Mandate.** Verify that every inferential conclusion follows from a valid estimand, unit, test, multiplicity family, effect size, and interval; and that the evidence chain from immutable source to rendered claim is authentic, traceable, and independently regenerable.

**Specialist seats.**
- Estimand & experimental-unit specialist (R4) — unit of analysis, pseudoreplication, genuine pairing.
- Nonparametric-testing & multiple-comparison specialist (R4) — Friedman/Iman–Davenport, Nemenyi, Wilcoxon signed-rank, Holm families.
- Effect-size & bootstrap/CI specialist (R4) — A12, rank-biserial correlation, Cliff’s delta with explicit direction; BCa resampling hierarchy and deterministic seeding.
- Evidence-provenance & determinism specialist (R5) — immutable release, checksums, source locks, seed schedules.
- Reproducibility & open-science specialist (R5) — clean-room rebuild, environment, availability truthfulness, the delivery-level determinism contract.

**Owned stages.** 7 (R5, data/benchmark/evidence/provenance), 9 (R4, statistical validity), 12 (R5, reproducibility & open science). Seconds R4 into Stages 10 and 11.

**Owned gates.** G (evidence integrity), I (statistical validity), L (reproducibility).

**Adversarial lens.** “Are runs being treated as independent tasks, is any p-value or interval computed on the wrong unit or family, and can an independent team actually regenerate every headline number from the immutable release?”

**Checklist.**
- The team MUST confirm the observation and experimental units are valid and that run-level variability is not confused with across-function variability (sections 9 and 9.1 A.4).
- The team MUST verify multiplicity is corrected within an explicitly enumerated family and that raw and adjusted p-values are distinguished; Holm is primary and Benjamini–Hochberg is exploratory-only and separately labeled (sections 9 and 10.7).
- The team MUST verify ranks are computed from unrounded values and that BCa or other intervals resample at the correct hierarchy with a stated, deterministic seed (sections 4.3 and 10.7).
- The team MUST verify that no publication analysis falls back to staging (`results/`, `results/_run_all/`) and that the reproducibility manifest’s recorded delivery levels (analytical / visual / byte-for-byte) are supported by double-rebuild evidence (sections 10.3 and 12).
- The team SHOULD independently recompute a representative sample of descriptive summaries, ranks, tests, effects, intervals, and win/tie/loss counts (section 9).
- The team MUST apply the recovery-versus-comparability disposition (section 10.7) after any post-freeze data recovery: a **seed-deterministic** quantity (error, rank, Wilcoxon, effect size, BCa interval) recovered from a re-derivable pipeline is validly available and every remaining "does-not-exist / disclosed-unavailable / exists only at scope X" claim about it MUST be corrected, whereas a **non-deterministic wall-clock runtime** produced by a separate post-freeze re-run is NOT comparable to the frozen campaign and legitimately stays disclosed-unavailable; the team MUST verify the manuscript draws this line correctly and never conflates the two in either direction.

#### 3.3.5 Team 4 — Software, Numerical-Methods, HPC & Production (T4-SOFT)

**Mandate.** Verify code↔method correspondence at the implementation level, the numerical and floating-point regime, computational-cost and complexity accounting, RNG and determinism, and the fidelity and editability of the LaTeX/PDF and Word/OOXML production packages.

**Specialist seats.**
- Code↔method-correspondence specialist (R2/R5 seconded) — the implementation matches the equations, pseudocode, and configuration.
- Floating-point & numerical-stability specialist — sentinels, degenerate cases, environment consistency, platform variability.
- Complexity & HPC-cost specialist — asymptotic vs. measured time and memory, overhead separation, wall time under comparable environments.
- RNG & determinism specialist (R5 seconded) — seed formulas, deterministic replay, seeded resampling.
- LaTeX/PDF production engineer (PROD-PDF) and Word/OOXML production engineer (PROD-WORD) — build integrity, native OMML and native tables, cross-format typographic parity (Stage 17, T1–T5).

**Owned stages.** 1 production intake (with T7-VENUE), 17 production co-lead (PROD-PDF, PROD-WORD).

**Owned gates.** Co-owns P (journal and production compliance, production side) with T7-VENUE; contributes to M (native equations and tables), F (code correspondence), and L (numerical determinism).

**Adversarial lens.** “Does the shipped software actually compute what the paper says, are ‘negligible’ overhead and complexity claims measured, and will the Word export render like the LaTeX PDF without rasterized math or a substituted font?”

**Checklist.**
- The team MUST reject “free,” “negligible,” or “efficient” cost language unless directly measured and scoped (section 9.1 A.6).
- The team MUST verify Word equations are native OMML and tables are native `w:tbl`, never rasterized images, where a Word deliverable is required (section 13 and Stage 17).
- The team MUST execute — or document as a T5 deviation — the DOCX→PDF typographic-parity comparison against the LaTeX class specification (Stage 17 T1–T5, section 10.12).
- The team SHOULD confirm the RNG seed schedule yields deterministic replay to the extent the method supports it, and flag any platform or floating-point variability that affects reported values.
- The team MUST diff the ISM interaction-structure memory (no longer titular)'s printed update rule against the frozen implementation line-by-line — the retention/decay factor, its operand, whether an independent learning rate exists, and whether two parameters were silently collapsed — and ticket any mismatch as a paired Gate F / Gate M finding when the same rule is also drawn in a figure (section 10.6; the R1 EMA-equation defect).
- The team MUST confirm that any exhibit a reader or editor may need to change — every data table, and the step content of a schematic — ships as a native editable `w:tbl` in the Word deliverable and never as a rasterized image, including "figures" that are really tables (sections 10.17 and 13).

#### 3.3.6 Team 5 — Scientific-Writing, Exhibits & Data-Visualization (T5-WRITE)

**Mandate.** Ensure the manuscript reads as precise, original, expert scholarship and that every exhibit is necessary, accurate, legible, accessible, and honestly bound to evidence — without any fact drift or detector-gaming.

**Specialist seats.**
- Scholarly-voice & argumentation specialist (RW) — clarity, paragraph logic, calibrated hedging, terminology stability.
- Formulaic-pattern & authorship-integrity specialist (RW; RI seconded) — machine-like patterns, safe style-only revision, AI-detection integrity.
- Figure & data-visualization specialist (VIZ) — graphical honesty, scale and axis integrity, accessibility in grayscale and for common color-vision deficiencies.
- Table & equation-presentation specialist (VIZ) — statistic and dispersion labeling, significance symbols, native editable tables and equations.
- Caption & exhibit-binding specialist (VIZ) — source paths, generators, checksums, caption completeness.

**Owned stages.** 13 (VIZ, exhibits), 15 (RW, writing & authorship integrity), and support to AE at Stage 14.

**Owned gates.** M (exhibit integrity), N (writing and authorship integrity).

**Adversarial lens.** “Could any sentence be transplanted unchanged into an unrelated paper, does any figure’s scale or selection mislead, and does the prose polish mask an underdeveloped argument or an evidential weakness?”

**Checklist.**
- The team MUST NOT let any style-only edit change numerical values, claim scope, citations, equations, method behavior, experimental design, exhibit content, or limitations (section 15.4).
- The team MUST state that AI-text detectors are not an authorship or quality standard and MUST NOT recommend detector-evasion tactics (sections 2 and 15.5).
- The team MUST verify that no missing figure series or best-run selection is undisclosed and that genuinely comparable panels share scales (sections 13 and 10.8).
- The team SHOULD flag polished-but-empty prose and generic superlatives (“robust,” “efficient,” “state-of-the-art”) not directly supported by evidence.
- The team MUST verify that no exhibit leaks a raw BibTeX key, an internal registry ID (for example an evidence `E`-number), or any other build-internal token in place of the reader-facing citation or the printed equation/figure number, and that any internal-ID-to-printed-number mapping shown to reviewers is supplied as an explicit legend (sections 13 and Appendix E; the R1 taxonomy-figure and E-ID defects).
- The team MUST flag any `matplotlib`-styled “figure” that is actually a table (coloured ON/OFF cells, plotted text, a dense auto-generated box-and-arrow rail with a colour legend) and require its re-rendering as a clean native table or a simple labelled flowchart, and MUST flag a pseudocode block that overflows, collides, or double-prints as a Stage-13 ticket even when its content is correct (section 10.17).

#### 3.3.7 Team 6 — Ethics, Research-Integrity, Citation & Publication-Practice (T6-INTEG)

**Mandate.** Verify ethical, legal, and publication-integrity compliance — including GenAI disclosure, authorship, conflicts, plagiarism/patchwriting, and image integrity — and verify source identity, semantic citation support, and bibliography consistency within the permitted corpus.

**Specialist seats.**
- Research-ethics & approvals specialist (RI) — approvals, consent, privacy, dual-use, licenses.
- GenAI-disclosure & authorship specialist (RI) — checks D16.1–D16.6, the no-AI-author rule, and the detection-risk false-positive science.
- Plagiarism, patchwriting & image-integrity specialist (RI) — text-similarity, distinctive phrasing, image manipulation.
- Citation-integrity & source-identity specialist (REP) — existence, identity, and semantic support at the stated strength.
- Bibliography-consistency & corpus-boundary specialist (REP) — text↔bibliography agreement, closed-corpus compliance, no fabricated locators.

**Owned stages.** 5 (REP, literature & citation), 16 (RI, ethics & integrity). RI seconds into Stage 15.

**Owned gates.** E (literature and citation integrity), O (ethics and publication integrity).

**Adversarial lens.** “Is any reference fabricated, cited beyond what it establishes, or missing where it belongs; is any ethics or GenAI obligation under-disclosed relative to the current verified venue policy; and is any detector flag being mistaken for misconduct?”

**Checklist.**
- The team MUST NOT allege undisclosed AI writing from a detector score alone and MUST record any detector result with the false-positive caveat (section 16, D16.4).
- The team MUST treat a used citation without a verified local source as a critical compliance failure under a closed corpus (section 10.2), and MUST NOT invent any citation key, locator, approval number, or declaration (sections 2 and 16).
- The team MUST verify the GenAI disclosure is consistent across the submission form, Methods, and Acknowledgments and persists in both PDF and Word (D16.5–D16.6).
- The team SHOULD verify that no retraction, correction, or expression of concern affects cited work and that self-citation is not inflated.
- The team MUST scan the source tree for orphan or superseded section files that the canonical build does not include yet remain in the repository, and treat any that carry prohibited, contradictory, or stale content (an alternative mechanism name, a claimed isolation study, a stale exhibit) as a package-integrity and result-integrity risk that MUST be quarantined or removed before submission (sections 1, 10.11, and Appendix E; the R1 orphan-file defect).

#### 3.3.8 Team 7 — Domain-Application, Venue-Fit & Journal-Compliance (T7-VENUE)

**Mandate.** Verify that the manuscript is placed in a venue that will plausibly accept it and that it meets the venue’s current official rules, and judge the real-world and application relevance of the contribution (including CEC2011 native-problem applicability) to the target readership.

**Specialist seats.**
- Algorithms/MDPI scope & aims specialist (JCO) — article type and scope match to the venue’s actual published output.
- Venue-standing & two-index specialist (JCO) — JCR IF/quartile/category rank and Scopus CiteScore/percentile/SJR, ESCI vs. SCIE indexing, index-divergent quartiles (D17.1).
- Comparator-culture & rejection-risk specialist (JCO; R6 seconded) — reviewer expectations and narrow-panel rejection risk (D17.3 — external-baseline scope is OUT for this cycle per §1.5.4; confine the analysis to within-family comparator culture).
- Real-world-applicability specialist (R1 seconded) — CEC2011 native-problem relevance and generalization beyond synthetic benchmarks.
- Author-instruction & submission-package specialist (JCO) — declarations, file package, anonymization, reporting checklists, page and word limits.

**Owned stages.** 1 (JCO, package completeness & compliance), 17 (JCO co-lead, journal compliance). Contributes venue-fit findings (D17.1–D17.4) to Stage 2 and section 12.6.

**Owned gates.** A (package integrity, package side), and co-owns P (journal and production compliance, journal side) with T4-SOFT.

**Adversarial lens.** “Is the claimed quartile current and index-honest, will this venue’s reviewer culture reject a narrow comparator panel, and is the ‘real-world’ framing supported by an actual application rather than a synthetic benchmark?”

**Checklist.**
- The team MUST verify venue standing from current JCR and Scopus sources and MUST record the official source and access date; it MUST NOT rely on remembered metrics or policy (section 2, D17.1, Stage 17).
- The team MUST NOT describe benchmark performance as demonstrated real-world benefit without a real-world design (sections 9.5 and 4.6).
- The family-scoped (seven-algorithm GSK) comparator panel and the absence of external non-GSK baselines are **explicitly out of scope for this review cycle** (§1.5.4): they are a deliberate, disclosed scoping decision, **not** a rejection risk, fairness gap, or review finding. The team MUST NOT record, ticket, or gate on a "narrow panel / missing external baseline" concern in this cycle; confine all comparator analysis to the within-family panel.
- The team SHOULD recommend a laddered venue plan (primary plus two fallbacks) matched to the paper’s true competitive tier (D17.4).
- The team MUST verify that the manuscript's back-matter and submission-package listing of supplementary contents matches what the supplement file actually contains and what the main text and conclusions assert it contains; a paper that cites a supplementary study the supplement marks "not reported," or a conclusion that denies a component study the supplement in fact includes, is a package-completeness and claim-integrity failure that MUST be surfaced at intake (Stage 1; the R1 three-way inconsistency).

### 3.4 Team-to-gate ownership map

Each hard gate (section 11) has one accountable **owning team** and, where the work is intrinsically shared, one or more **contributing teams**. This map complements — and does not replace — the section 11 gate table or the section 11 gate-namespace crosswalk.

| Gate | Name | Owning team | Contributing team(s) |
|---|---|---|---|
| A | Package integrity | T7-VENUE | ECB, T4-SOFT |
| B | Desk review | ECB | T7-VENUE |
| C | Claim integrity | T1-OPT | ECB, T3-STAT |
| D | Contribution merit | T1-OPT | T7-VENUE |
| E | Literature/citation integrity | T6-INTEG | T1-OPT |
| F | Method/theory | T1-OPT | T4-SOFT |
| G | Evidence integrity | T3-STAT | T2-BENCH |
| H | Study design/fairness | T2-BENCH | T3-STAT |
| I | Statistical validity | T3-STAT | T2-BENCH |
| J | Result integrity | T1-OPT | T3-STAT, T5-WRITE |
| K | Robustness/attribution | T2-BENCH | T1-OPT, T3-STAT |
| L | Reproducibility | T3-STAT | T4-SOFT |
| M | Exhibit integrity | T5-WRITE | T4-SOFT |
| N | Writing/authorship integrity | T5-WRITE | T6-INTEG |
| O | Ethics/publication integrity | T6-INTEG | ECB |
| P | Journal/production compliance | T7-VENUE | T4-SOFT |
| Q | Post-revision verification | ECB | all teams |

An owning team is accountable for its gate’s `PASS` / `FAIL` / `BLOCKED` determination and its Appendix D sign-off; contributing teams supply evidence and MUST concur on any `PASS`. No team may pass its own gate over an unresolved critical or major objection from a contributing team (section 3.6).

### 3.5 Intra-team and cross-reviewer independence protocol

Independence operates at the seat level first, then the team level. For stages involving scientific judgment:

1. R1–R6 produce independent findings without reading one another’s conclusions.
2. Each reviewer states confidence and the evidence used.
3. AE compares agreements and disagreements.
4. SE resolves duplicates but never deletes a unique material objection.
5. A disagreement remains visible when evidence cannot resolve it.
6. EIC makes the final internal readiness decision from the complete record.

The same discipline applies across teams: each team’s first-pass findings MUST be recorded before it reads another team’s conclusions, and where two teams co-own or contribute to one gate (section 3.4), each records its position independently before reconciliation. A seconded seat contributes its specialist finding to the host stage but retains its home-team adversarial lens.

### 3.6 Cross-team consensus and arbitration protocol

Consensus is reached by an **arbitration council** chaired by the Editor-in-Chief (EIC) and composed of the team leads (section 3.1), with the Senior synthesis editor (SE) as recording synthesizer and the Associate Editor (AE) as proportionality assessor. The council convenes at Stage 19 and whenever two teams reach an unresolved conflict earlier.

1. **Evidence precedence, not vote.** Disagreements are resolved by the authority order of section 1.4 and the evidence classes of section 4.1, never by majority vote. A minority position backed by stronger evidence prevails.
2. **Gate priority over score.** Hard gates (section 11) are applied before the weighted score; no team’s favorable score may override another team’s substantiated gate failure.
3. **Ownership and escalation.** The owning team (section 3.4) proposes each gate status; a contributing team MAY file a **blocking dissent** with cited evidence, which the council MUST resolve or record as an open disagreement — it MUST NOT be silently overruled.
4. **Cross-cutting defects.** When one root cause produces symptoms across teams (for example, an evidence-lock breach affecting statistics, exhibits, and reproducibility), the council reassesses severity jointly and assigns a single owning ticket with cross-team dependencies (sections 19 and 20).
5. **Dissent preservation.** Every unresolved reviewer or team disagreement remains visible in `independent_reviewer_reports.md` and the final report (section 12.12); consensus never erases a unique material objection.
6. **Final decision.** The EIC issues the single internal disposition code (section 19) from the complete, reconciled record; the SE owns the dependency-aware revision roadmap (section 20) and the Gate Q closure.

The council’s authority is limited to this internal simulation; it does not predict or claim the actual journal decision.

---

## 4. Evidence and integrity constitution

### 4.1 Evidence classes

Classify every supporting source before using it.

| Class | Evidence type | Permitted use |
|---|---|---|
| G | Governing protocol or development prompt | project rules, evidence boundaries, required deliverables, frozen decisions |
| L | Verified literature | external scientific claims, definitions, prior methods, benchmark/statistical grounding |
| E | Raw or immutable empirical evidence | reportable measurements, comparisons, numerical conclusions |
| M | Method/code/configuration evidence | what the implemented method actually does, parameterization, evaluation accounting |
| S | Frozen statistical output | tests, effects, intervals, ranks, descriptive summaries derived from E |
| J | Official journal evidence | formatting, article type, declarations, submission package, current policy |
| A | Verified author-supplied information | authorship, affiliations, funding, conflicts, ethics, acknowledgments |
| R | Rendered artifacts | presentation verification only; never the authoritative source for regeneration |

One class cannot silently substitute for another. A manuscript sentence is not evidence for its own truth.

### 4.2 Claim-level traceability

Create or validate a claim inventory covering at least:

- title claims;
- every abstract sentence;
- stated research gap;
- contribution bullets;
- novelty claims;
- method properties;
- protocol statements;
- every headline result;
- statistical conclusions;
- discussion interpretations;
- limitation statements;
- conclusion claims;
- highlights and graphical abstract text (only where the venue solicits them; MDPI Algorithms solicits neither — HL-01 NOT_APPLICABLE — record N/A rather than ticketing absence);
- cover-letter scientific statements; and
- supplementary conclusions.

For each claim record:

```text
claim_id
normalized_claim
claim_type
manuscript_location
scope
evidence_class
source_or_artifact
support_strength: direct / partial / indirect / unavailable
assumptions
permitted_wording
prohibited_wording
reviewer_risk
disposition: accept / narrow / qualify / move / omit / block
verification_status
notes
```

This field list is identical to the canonical machine-readable claim-audit schema in Appendix A.2.

A high-visibility claim with `support_strength = unavailable` is a critical issue. Partial or indirect support requires narrowed wording and explicit limitations.

### 4.3 Quantitative integrity

For every number in the manuscript, supplement, abstract, conclusion, tables, figures, captions, and cover letter (Highlights: N/A for MDPI Algorithms):

- identify the authoritative full-precision value;
- verify the transformation and rounding rule;
- verify units, direction, denominator, sample size, and missing-data treatment;
- verify that the same value appears consistently across formats;
- verify that significance marks use the declared adjusted result;
- verify that ranks and ties were calculated from unrounded values; and
- verify that no value was estimated visually from a plot.

Any unexplained mismatch is at least major. A mismatch that changes a conclusion is critical.

### 4.4 Citation integrity

Every citation occurrence MUST be semantically appropriate. Check that:

- the cited source exists and its identity is verified;
- the source supports the adjacent claim at the stated strength;
- a source is not cited for a stronger proposition than it establishes;
- primary sources are preferred when available and permitted;
- citations are adjacent to the clauses they support;
- no source is included merely to inflate bibliography size;
- no blanket citation is used for unrelated assertions;
- references in text and bibliography agree;
- no citation key, author, year, title, venue, DOI, or page locator is invented; and
- absence from a closed corpus is not described as proof that no prior work exists.

### 4.5 Reproducibility and provenance

A headline result is not reproducible unless the review can identify, where applicable:

```text
evidence release or dataset version
source paths and checksums
repository commit and dirty-state information
method/configuration/evaluator hashes
suite or dataset version
function/task/sample scope
run count or sample size
seed formula and exact schedule
stopping rule or budget
preprocessing and exclusions
environment and numerical regime
analysis script and command
analysis parameters and RNG seed
derived output and checksum
table/figure binding
```

### 4.6 Honest interpretation

The review MUST reject or rewrite language that:

- generalizes beyond tested populations, tasks, dimensions, domains, or comparators;
- describes association as causation;
- treats statistical significance as practical importance;
- treats failure to reject as proof of equivalence;
- calls a method robust without adequate stress testing;
- calls overhead negligible without measurement;
- calls a method state-of-the-art without a suitable contemporary comparison;
- treats a same-family or narrow comparator panel as field-wide evidence; or
- suppresses uncertainty, losses, exceptions, or contradictory outcomes.

---

## 5. Issue classification, priority, confidence, and review tickets

### 5.1 Severity scale

| Severity | Definition | Submission effect |
|---|---|---|
| **Critical (C)** | invalidates a central claim, evidence boundary, ethics status, method, analysis, or reproducibility basis | submission prohibited until resolved |
| **Major (M)** | likely to cause rejection or require substantial scientific revision, new analysis, or new experiment | submission prohibited until resolved |
| **Moderate (O)** | meaningful weakness that reduces credibility, interpretability, or journal fit but may not invalidate the core | should be resolved before submission; any deferral needs written justification |
| **Minor (N)** | localized clarity, reporting, formatting, or completeness defect | resolve before final package when practical |
| **Editorial (E)** | wording, grammar, typographic, layout, or style issue with no scientific effect | batch correction permitted after scientific freeze |
| **Advisory (A)** | optional enhancement or future-work suggestion | non-blocking |

### 5.2 Priority scale

- `P0`: immediate stop; affected analysis or claim cannot be trusted.
- `P1`: mandatory before any submission.
- `P2`: mandatory before final packaging.
- `P3`: beneficial but non-blocking after documented review.
- `P4`: optional.

### 5.3 Confidence scale

- `Confirmed`: directly verified from authoritative evidence.
- `High`: strongly supported; little plausible ambiguity.
- `Medium`: likely, but an input or interpretation remains incomplete.
- `Low`: a plausible reviewer concern requiring author verification.

Low confidence does not justify omission. It changes the wording from a finding to a question or required check.

### 5.4 Mandatory ticket schema

Every identified issue MUST use this schema:

```text
ticket_id:
review_stage:
reviewer_role:
severity:
priority:
confidence:
issue_type: evidence / method / experimental-design / statistics / claim-scope / citation / reproducibility / exhibit / writing / ethics / compliance / production
manuscript_location:
claim_id_or_artifact_id:
concise_issue:
exact_evidence_or_observation:
root_cause:
scientific_or_editorial_justification:
impact_on_validity_or_acceptance:
required_correction:
acceptable_alternatives:
additional_evidence_needed:
dependencies:
expected_improvement:
post_revision_verification:
status: open / in_progress / resolved / accepted_risk / blocked
```

Do not close a ticket because text was changed. Close it only when the required verification passes.

### 5.5 Severity and priority calibration examples

These worked examples calibrate the section 5.1 severity and section 5.2 priority scales against defect patterns that actually occurred in an independent review (the R1 canonical set; Appendix E). Use them to resist both over-ticketing (inflating an editorial nit to Major) and under-ticketing (demoting a validity defect to Minor because “the numbers are right”).

- **Main-text ablation-result leak (Critical, P0).** A “neutral pointer” sentence that in fact states a component-effect result or null (for example, “a direct isolation … did not confirm a standalone benefit”) violates the section 10.9 prohibition and is Critical — as narrowed for this manuscript (§10.9): Critical applies to a FAVORABLE or efficacy-implying component result surfacing in the main text/abstract/conclusion (e.g., the Holm-significant final-polish effect, which must stay supplementary) or to a pointer citing a study the supplement does not contain; the deliberately-advertised ISM null is NOT a violation even though it is one sentence with no number: it discloses a governed-supplementary result in the main text and, when it also cites a supplement study the supplement says is absent, fails Gate C and Gate J at once. Priority P0 — stop and apply the result-free-deferral remedy.
- **Printed-equation vs. frozen-code mismatch (Major→Critical, P1).** A titular-mechanism update rule printed as `G←(1−λ)G+λΣ` where the code computes `G←λG+ηΣ` is Major when localized to one equation and Critical when it propagates to the pseudocode, prose, parameter table, and a mechanism figure, because a reader reimplementing from the paper builds the wrong operator. Correctness of every reported number does not lower the severity — the defect is in the method's printed specification (Gate F).
- **Stale existence claim after data recovery (Major, P1).** Still asserting a comparator's per-run data “does not exist / is disclosed-unavailable” in several locations after a post-freeze recovery made those seed-deterministic cells available is a false existence claim (Major). Separately, mislabeling a **non-deterministic post-freeze runtime** as “comparable” to the frozen campaign is its own Major integrity-of-comparison defect — do not collapse the two: the seed-deterministic cells must be corrected while the runtime legitimately stays disclosed-unavailable (section 10.7).
- **Raw BibTeX keys / internal registry IDs in an exhibit (Major, P2).** A figure printing `[omidvar2014dg]` instead of a formatted citation, or method figures labelled with evidence `E`-numbers off-by-one from the printed equation numbers, is Major — a camera-ready credibility and traceability failure that misdirects the reader to a non-existent or wrong referent — not Editorial. The fix is regeneration or an explicit legend, verified in the rendered PDF.
- **Orphan/superseded source file in the tree (Major, P2).** A section file built by nothing but still present and carrying a prohibited alternative mechanism name, an isolation claim, or a stale exhibit is Major because it can be submitted by accident and contradicts the shipped narrative; quarantine or delete and drop its manifest entry.
- **Three-way source↔PDF↔Word desync (Blocked/Critical, P0).** When the section sources, the compiled PDF, and the Word deliverable do not all correspond to one frozen scientific state, no single authoritative manuscript can be identified and Stage 0 hard-fails; this is Blocked until one state is established, not merely Major.
- **A `p = 0.0000` render where the plan mandates a bound (Moderate, P2).** Printing `p=0.0000` when the frozen analysis plan requires `<1.0e-4` changes no inference but is internally inconsistent with sibling tables and reads as machine output; fix to the bounded form. This is Moderate, not Critical — it neither invalidates a claim nor hides an adverse result.

---

## 6. Scoring model and internal readiness bands

### 6.1 Category scoring

Score each category from 1 to 5 and provide evidence for the score.

- `5 — exemplary`: publication-strength with no material weakness.
- `4 — strong`: minor non-blocking weaknesses only.
- `3 — adequate but vulnerable`: reviewer concern remains; revision required.
- `2 — major weakness`: central work is not submission-ready.
- `1 — invalid, absent, or misleading`.

Any category score of 3 or below creates at least one mandatory ticket. Scores never override a failed hard gate.

Appendix A.3 scorecard rows are recorded per reviewer. The consensus category score is the mean of the assigned reviewer scores for that category and MAY therefore be fractional; report consensus scores to two decimals.

### 6.2 Weighted readiness score

Use this internal diagnostic weighting:

| Category | Weight |
|---|---:|
| Journal fit and scientific significance | 8 |
| Novelty and contribution boundary | 12 |
| Theory, method, or algorithmic correctness | 14 |
| Experimental or study design | 14 |
| Statistical validity | 14 |
| Evidence and citation integrity | 8 |
| Results, discussion, and limitations | 8 |
| Robustness, sensitivity, and ablation logic | 6 |
| Reproducibility and open-science readiness | 7 |
| Writing, exhibits, and presentation | 5 |
| Ethics, journal compliance, and production package | 4 |
| **Total** | **100** |

Compute the weighted readiness score as:

```text
weighted_score = sum over categories of ( weight_c * score_c / 5 )
```

where `score_c` is the consensus category score from section 6.1. The result lies on a 0–100 scale (100 = every category exemplary).

The score is an internal readiness heuristic, not a prediction of acceptance.

### 6.3 Readiness bands

The **core scientific categories** are: Novelty and contribution boundary; Theory, method, or algorithmic correctness; Experimental or study design; Statistical validity; and Evidence and citation integrity. Category floors below apply to consensus category scores as defined in section 6.1.

- **Q1-ready candidate**: all hard gates pass; zero open critical or major tickets; weighted score at least 90; no core scientific category below 4.25; novelty, method, experimental design, and statistics each demonstrate explicit Q1-level strength.
- **Q2-ready candidate**: all hard gates pass; zero open critical or major tickets; weighted score at least 82; no core scientific category below 4.0.
- **Minor pre-submission revision**: core is defensible, but one or more moderate/minor items remain.
- **Major pre-submission revision**: at least one major issue, failed core category, or essential missing analysis/experiment.
- **Do not submit / redesign**: critical invalidity, unsupported central contribution, irreparable evidence problem, or ethical/integrity concern.
- **Scientifically ready, administratively blocked**: scientific gates pass but verified author/journal metadata or upload materials are incomplete.
- **Assessment blocked**: essential evidence is unavailable, so a responsible readiness decision cannot be made.

---

## 7. Mandatory review artifacts

Produce the following review outputs. When file-generation tools are available, write them as separate Markdown/CSV/JSON files; otherwise include them as clearly labeled sections in the final report.

| Artifact | Producing stage | Required content |
|---|---|---|
| `review_configuration.md` | Stage 0 | inputs, versions, target, scope, missing materials, authority order |
| `requirements_compliance_matrix.csv` | Stage 0 | every governing-prompt requirement mapped to manuscript evidence and status |
| `desk_screening_report.md` | Stage 2 | fit, novelty plausibility, obvious rejection risks, editorial disposition |
| `claim_audit.csv` | Stage 3 | claim-level support, scope, wording ceiling, disposition (Appendix A.2 schema) |
| `issue_register.csv` | all stages; consolidated by SE at Stage 19 | all tickets using the mandatory schema |
| `review_scorecard.csv` | Stage 19 | category scores, weights, evidence, gate dependencies |
| `method_and_theory_audit.md` | Stage 6 | assumptions, equations, algorithm/method completeness, code correspondence |
| `experimental_design_audit.md` | Stage 8 | hypotheses, controls, comparators, fairness, missing experiments |
| `missing_experiment_register.csv` | Stage 8 | evidence gaps, minimum valid designs, submission-necessity classification, affected claims (Appendix A.5 schema) |
| `statistical_audit.md` | Stage 9 | estimands, units, tests, multiplicity, effects, intervals, robustness |
| `evidence_and_reproducibility_audit.md` | Stages 7 and 12 | provenance, source locks, code/data, commands, rebuild status |
| `citation_and_literature_audit.md` | Stage 5 | source identity, semantic support, omissions, bias, bibliography consistency |
| `exhibit_audit.csv` | Stage 13 | table/figure/equation checks and source bindings |
| `section_review.md` | Stage 14 | title-to-declarations assessment with exact locations |
| `writing_integrity_audit.md` | Stage 15 | clarity, natural scholarly voice, formulaic patterns, safe example revisions |
| `ethics_and_compliance_audit.md` | Stage 16 | declarations, privacy, approvals, authorship, disclosure, journal rules |
| `ai_disclosure_audit.md` | Stage 16 | GenAI checks D16.1–D16.6: disclosure completeness/consistency/wording, authorship prohibition, detection-risk with false-positive caveat, cross-format persistence (Appendix A.10 schema) |
| `journal_compliance_matrix.csv` | Stage 17 | requirement-by-requirement journal compliance with official source and access date; includes venue-fit two-index standing and comparator-culture verdict (D17.1–D17.4) |
| `pdf_build_report.md` | Stage 17 | LaTeX/PDF build status, template, fonts, references, layout, page count |
| `word_validation_report.md` | Stage 17 | Word/OOXML native-content validation, fields, and documented approved deviations |
| `cross_format_consistency_report.md` | Stage 17 | cross-format parity of values, equations, exhibits, citations, declarations |
| `independent_reviewer_reports.md` | Stage 18 | EIC, AE, and R1–R6 reports plus the recorded pre-consensus findings of the specialist roles (RI, RW, VIZ, PROD-PDF, PROD-WORD, REP, JCO), before consensus |
| `predicted_reviewer_questions.md` | Stage 18 | likely Q1/Q2 objections and author response requirements |
| `revision_roadmap.md` | Stage 20 | dependency-aware correction order and verification plan |
| `post_revision_verification.csv` | Stage 20 | ticket-by-ticket recheck and regression status |
| `final_readiness_report.md` | Stage 19 (updated after Stage 20) | gate status, score, verdict, residual risks, submission recommendation |


---

## 8. Multi-stage review workflow

Execute every stage in order. A stage may be marked `NOT APPLICABLE` only with a written scientific justification. Do not let a polished writing score compensate for invalid methods, weak evidence, or incorrect statistics. Before the stage work, run the Appendix E canonical-defect pre-flight as a fast triage of the highest-value defect patterns; it supplements and never replaces the stages and gates.

### Stage 0 — Review preflight, authority extraction, and version freeze

#### Objective

Establish exactly what is being reviewed, which rules govern it, and whether all manuscript versions and supporting artifacts belong to the same scientific state.

Lead role(s): SE, supported by R5. Lead team: ECB (Editorial Coordination Board).

#### Required checks

1. Record the manuscript, supplement, code, data, and analysis versions or hashes.
2. Confirm that the PDF, Word, LaTeX, tables, figures, and supplement refer to the same manuscript version.
3. Extract every mandatory requirement from the governing development prompt, and audit the `GOVERNANCE_AND_GATE_ARTIFACTS` package (phase-gate register, project configuration, presentation-conventions specification, evidence cards, claims matrix, reproducibility manifest) as the authoritative source (no external-gate mapping exists in this project — expected, not missing) for verifying build-gate, exemplar, and presentation-conventions compliance; when the package is absent, apply the missing-input behavior of section 1.3.
4. Create `requirements_compliance_matrix.csv` with:

   ```text
   requirement_id
   source_location
   requirement_text
   mandatory_or_advisory
   manuscript_or_artifact_location
   verification_method
   status: pass / fail / partial / blocked / not_applicable
   reviewer
   notes
   ```

5. Identify conflicts among the manuscript, protocol, analysis plan, code, and evidence metadata.
6. Verify the current target journal and article type from official instructions when available.
7. Record every missing input and its downstream effect.
8. Detect three-way version desync. Where a freeze manifest or equivalent hash record exists (for example `papers/governance/main_manuscript_freeze_manifest.json`), verify that the canonical section sources, the compiled PDF, and the Word/DOCX deliverable each hash to the same frozen scientific state; a source newer than the PDF, or a PDF and DOCX built from different source revisions, is a desync. When no hash record exists, reconcile version strings, build epochs, and a sample of headline values across all three artifacts.
9. Reconcile post-freeze recoveries and refreezes. For every recorded refreeze or change request after the primary freeze (a recovered comparator bundle, a text-only narrowing, an exhibit regeneration), verify that (a) the manuscript's existence, availability, and comparability statements match the post-recovery state, and (b) any main-text change stayed within the documented narrow-only exception rather than upgrading a claim or back-porting a favorable result; record any statement the refreeze left stale (sections 10.7 and 10.9).
10. Scan for orphan and superseded source files. Identify section or exhibit sources present in the tree but built by nothing (not `\input`/`\include`d by the canonical build), and flag any that carry prohibited, contradictory, or stale content as accidental-submission and consistency risks (Stage 1 and section 10.11).
11. Freeze the review snapshot. Later changes require a new version identifier and a revision log.

#### Hard-fail conditions

- the manuscript and supporting results come from inconsistent versions;
- the canonical source, the compiled PDF, and the Word/DOCX deliverable do not all resolve to one frozen scientific state (a three-way source↔PDF↔Word desync);
- a documented post-freeze recovery or refreeze left a manuscript existence, availability, or comparability statement stale and uncorrected;
- an orphan or superseded source file carrying prohibited or contradictory content remains in the release tree where it could be submitted or built by accident;
- the governing prompt cannot be located when compliance with it is claimed;
- central evidence cannot be identified;
- the target article type is incompatible with the manuscript structure and no correction plan exists; or
- a prior draft is being reviewed while newer scientific outputs are cited.

#### Required output

`review_configuration.md`, the initial `requirements_compliance_matrix.csv`, and a `Stage 0: PASS / FAIL / BLOCKED` decision.

---

### Stage 1 — Package completeness and technical intake

#### Objective

Determine whether the manuscript package is complete enough for substantive review and whether obvious technical defects prevent reliable assessment.

Lead role(s): JCO, supported by PROD-PDF and PROD-WORD. Lead team: T7-VENUE (Domain-Application, Venue-Fit & Journal-Compliance), with T4-SOFT (Software, Numerical-Methods, HPC & Production) on production intake.

#### Required checks

- main manuscript opens and is complete;
- supplement opens and all cited supplementary objects exist;
- references resolve and bibliography is present;
- figures are legible and not placeholders;
- tables are complete and not clipped;
- equation numbering and cross-references resolve;
- tracked changes, comments, hidden text, template instructions, and author notes are absent from release files;
- filenames and versions are unambiguous;
- anonymization is correct for the target review model;
- administrative placeholders are isolated and labeled;
- data/code availability statements point to real or clearly pending artifacts;
- no required appendix, declaration, graphical abstract, highlight, or cover-letter component is silently missing;
- the package contains no obsolete or contradictory file that could be submitted accidentally — in particular, no orphan section or exhibit source that the canonical build does not include yet still carries a prohibited mechanism name, a claimed component study, or a stale figure (cross-check the Stage 0 orphan scan); and
- the manuscript's back-matter and package listing of supplementary contents matches what the supplement file actually contains and what the main text and conclusions assert it contains (the three-way main-text↔conclusions↔supplement agreement).

#### Required output

A completeness table listing every expected artifact, status, version, and blocking consequence.

#### Gate

`Gate A — Package Integrity` passes only when the scientific review can identify one authoritative manuscript state and every essential file is readable.

---

### Stage 2 — Editor-in-Chief desk screening

#### Objective

Simulate the first editorial decision before external peer review.

Lead role(s): EIC. Lead team: ECB (Editorial Coordination Board).

#### EIC review questions

1. Does the paper clearly fit the verified aims and scope of the target journal?
2. Is the problem important enough for the journal’s readership?
3. Does the title and abstract communicate a credible contribution rather than a generic method variant?
4. Is the novelty plausible and distinguishable from the closest work?
5. Is the paper technically mature enough to send to reviewers?
6. Are the experiments or analyses substantial enough for the article type?
7. Are the claims appropriately scoped?
8. Are the language and figures sufficiently clear for scientific review?
9. Is there an obvious ethics, integrity, plagiarism, duplicate-publication, or citation-manipulation concern?
10. Is the manuscript within journal length and file requirements?
11. Does the paper appear to be benchmark-specific, incrementally engineered, or overly promotional without a broader scientific insight?
12. Does the paper explain why the contribution matters beyond reporting more wins?

#### Mandatory desk-rejection risk list

Rank the ten most plausible desk-rejection reasons. For each, state:

```text
risk
probability: high / medium / low
impact
supporting observation
what would reduce the risk
whether the issue can be fixed without new research
```

#### EIC disposition

Choose exactly one:

- `SEND TO EXTERNAL REVIEW`;
- `EDITORIAL REVISION BEFORE REVIEW`;
- `OUT OF SCOPE`;
- `INSUFFICIENT NOVELTY OR SIGNIFICANCE`;
- `METHOD OR EVIDENCE NOT MATURE`;
- `INTEGRITY OR COMPLIANCE HOLD`; or
- `ASSESSMENT BLOCKED`.

This is an internal simulation, not a claim about the actual journal decision.

#### Required output

`desk_screening_report.md` containing the twelve EIC answers, the ranked desk-rejection risk list, and the chosen EIC disposition.

#### Gate

`Gate B — Desk Review` fails when the manuscript has a likely desk-rejection defect that cannot be corrected through the planned revision.

---

### Stage 3 — Claim inventory and evidence-ceiling audit

#### Objective

Identify every substantive claim and determine the strongest wording that the available evidence permits.

Lead role(s): R6, supported by R1. Lead team: T1-OPT (Optimization & Metaheuristics).

#### Procedure

1. Extract claims from all high-visibility locations first: title, abstract, contribution bullets, highlights and graphical abstract where the venue solicits them (MDPI Algorithms solicits neither — HL-01 NOT_APPLICABLE), discussion, conclusion, and cover letter.
2. Continue through the manuscript paragraph by paragraph.
3. Classify each claim as one of:

   ```text
   BACKGROUND
   DEFINITION
   PRIOR_WORK
   RESEARCH_GAP
   NOVELTY
   METHOD_PROPERTY
   THEORETICAL_RESULT
   IMPLEMENTATION
   PROTOCOL
   DESCRIPTIVE_RESULT
   STATISTICAL_RESULT
   COMPARATIVE_RESULT
   MECHANISM_INTERPRETATION
   CAUSAL_CLAIM
   PRACTICAL_IMPLICATION
   GENERALIZATION
   LIMITATION
   RECOMMENDATION
   ADMINISTRATIVE
   ```

4. Map the claim to literature, evidence, code, analysis, or official requirements.
5. Record support strength and assumptions.
6. Detect scope drift between body text and abstract/conclusion.
7. Detect the following overclaim patterns:
   - “novel” where only a new combination or name is shown;
   - “significantly better” without a valid test and multiplicity control;
   - “robust” without appropriate perturbation or cross-context evidence;
   - “efficient” without cost analysis;
   - “generalizable” without external validation;
   - “causes” or “contributes” from correlational or remove-one evidence alone;
   - “state-of-the-art” from a narrow or outdated comparator panel;
   - “high-dimensional” or “large-scale” without a field-appropriate tested scope;
   - “real-world” from synthetic benchmarks or one applied case;
   - “consistent” when material exceptions exist.
8. Assign one disposition: accept, narrow, qualify, move, omit, or block.

#### Required outputs

- `claim_audit.csv`;
- a list of claims that must be removed from the abstract or conclusion;
- a list of claims that need additional analysis or experiments; and
- a “claims ceiling” paragraph stating the strongest defensible overall conclusion.

#### Gate

`Gate C — Claim Integrity` passes only when every substantive claim has adequate support and all unavailable or misleading claims are removed or blocked.

---

### Stage 4 — Scientific significance, originality, and contribution boundary

#### Objective

Determine whether the work contributes enough scientific value for a Q1 or Q2 venue and whether the contribution is accurately distinguished from prior work.

Lead role(s): R1. Lead team: T1-OPT (Optimization & Metaheuristics).

#### Required assessment

Evaluate:

- importance of the research problem;
- specificity and reality of the stated gap;
- whether the gap is supported by the reviewed literature rather than asserted;
- whether the proposed contribution addresses the gap directly;
- conceptual, theoretical, methodological, empirical, practical, and reproducibility contributions separately;
- originality of each component;
- degree of incrementalism;
- whether a new acronym disguises a familiar mechanism;
- whether the work is a meaningful integration or merely a collection of modules;
- whether the combination creates a new scientific insight;
- whether the manuscript explains why the method should work;
- whether the evidence tests the contribution rather than only the final system;
- whether the practical or scientific implications matter outside the selected benchmark or dataset; and
- whether the manuscript compares itself fairly with the closest prior work (restricted to the permitted corpus when a closed literature corpus governs, per section 10.2).

#### Contribution decomposition

Create a table with:

```text
contribution_id
stated_contribution
category: inherited / reproduced / adapted / combined / original_within_reviewed_scope
closest_prior_work
exact_difference
scientific_value
implementation_evidence
empirical_or_theoretical_test
cost_or_tradeoff
scope_limit
reviewer_risk
verdict
```

#### Q1-level questions

- Is the contribution likely to change understanding, practice, or methodology in the field?
- Does it provide more than a small performance increment?
- Does it offer a defensible mechanism, theory, analytical insight, or reproducible empirical finding?
- Is the evidence broad and deep enough for the claimed importance?
- Would a skeptical expert still see a contribution if all promotional wording were removed?

#### Q2-level questions

- Is the method or study technically sound and meaningfully useful?
- Is the incremental contribution clearly specified and sufficiently validated?
- Are scope and limitations honest?

#### Required output

A novelty-and-significance matrix, the strongest contribution statement, the weakest contribution statement, and a recommendation to retain, merge, narrow, or remove each contribution bullet.

#### Gate

`Gate D — Contribution Merit` fails when the central contribution is unsupported, materially indistinguishable from prior work, or too weak for the target venue without a journal or article-type change.

---

### Stage 5 — Literature review, source identity, and citation audit

#### Objective

Verify that the manuscript is positioned accurately, fairly, and comprehensively within the literature permitted by the project.

Lead role(s): REP, supported by R1. Lead team: T6-INTEG (Ethics, Research-Integrity, Citation & Publication-Practice).

#### Source-identity audit

For every used source verify, as available:

- title;
- authors;
- year;
- venue and version;
- DOI or persistent identifier;
- readable full text;
- whether the cited version matches the claim;
- whether the source is primary, secondary, preprint, in press, or retracted/corrected; and
- whether it belongs to an approved closed corpus when such a corpus is mandatory.

#### Semantic citation audit

For every citation occurrence assess:

- what exact clause it is intended to support;
- whether it directly supports that clause;
- whether the wording is stronger than the source;
- whether multiple citations genuinely support the same proposition;
- whether the source is being used for background, method lineage, a finding, a definition, or a contrast;
- whether a direct original source is available;
- whether important limitations of the cited work are omitted; and
- whether a citation is decorative, irrelevant, or inserted only to satisfy a quota.

#### Coverage and balance audit

Check:

- closest competing methods;
- foundational work;
- current and influential work available within the permitted search boundary;
- opposing or negative findings;
- benchmark or dataset definitions;
- statistical-method sources;
- literature from all relevant subfields rather than only one research group;
- excessive self-citation or reciprocal citation patterns;
- unsupported claims of exhaustive review; and
- chronology-only summaries that do not synthesize relationships.

#### Related-work quality test

The related-work section should explain:

1. what each source contributes to the problem;
2. how groups of approaches differ;
3. where the specific unresolved gap lies;
4. how the present method differs; and
5. which limitations remain.

#### Patchwriting and attribution review

When source text is available, flag unusually close wording, structure, or distinctive phrasing. Do not make a legal plagiarism determination without adequate evidence. Require quotation, paraphrase, or attribution correction as appropriate.

#### Required outputs

`citation_and_literature_audit.md` containing:

- source-identity exceptions;
- citation-misuse list;
- missing-literature matrix;
- related-work restructuring recommendations; and
- bibliography consistency report.

#### Gate

`Gate E — Literature and Citation Integrity` fails for fabricated or unverifiable references, material semantic mis-citation, systematic literature bias that distorts novelty, or uncorrected unattributed borrowing.

---

### Stage 6 — Theory, mathematical correctness, and methodological completeness

#### Objective

Determine whether the method is formally correct, internally consistent, implementable, and sufficiently specified for expert scrutiny.

Lead role(s): R2. Lead team: T1-OPT (Optimization & Metaheuristics).

#### General method audit

Check that the manuscript defines:

- the research problem and objective;
- assumptions and applicability conditions;
- variables, symbols, indices, units, domains, and dimensions;
- inputs, outputs, initialization, update order, and stopping conditions;
- all parameters, defaults, ranges, and selection rationale;
- data preprocessing and transformation;
- boundary, failure, exception, missingness, and tie handling;
- computational resources and complexity;
- safeguards for numerical instability or degenerate cases;
- reproducibility-relevant random processes;
- dependencies on external libraries, solvers, or proprietary tools; and
- exactly what is inherited, modified, or original.

#### Mathematical audit

For each equation, theorem, proposition, derivation, or proof:

- verify every symbol is defined before or at first use;
- verify dimensions and units;
- verify equality, assignment, approximation, and sampling notation;
- derive or test the equation independently when feasible;
- check boundary cases and limiting behavior;
- check sign, index, transpose, normalization, and denominator correctness;
- check consistency with pseudocode and source code;
- check whether assumptions are necessary and stated;
- check that a proof establishes the actual claim and not a weaker one;
- identify skipped derivation steps that matter to validity; and
- distinguish analytical complexity from measured runtime or memory.

#### Algorithm or procedure audit

For an algorithmic paper, verify:

- complete top-level pseudocode;
- mechanism-level pseudocode where needed;
- one-to-one correspondence among equations, pseudocode, configuration, and code;
- direct recomputation of every titular or load-bearing update rule from the frozen source, confirming the printed equation, the pseudocode step, the prose, and the parameter table all encode the same operator — including which operand carries a decay/retention factor, whether a separate learning rate exists, and that no two distinct parameters were silently collapsed into one (a printed `G←(1−λ)G+λΣ` for a coded `G←λG+ηΣ` is a Gate F failure);
- update order and evaluation accounting;
- random-variable distributions;
- population, archive, memory, graph, or state initialization;
- budget-safe termination;
- objective-call accounting for local search, polish, validation, and repair;
- deterministic behavior under a fixed seed to the extent supported;
- hidden defaults and dormant branches;
- component interactions and dependencies; and
- complexity by component and cadence.

#### Methodological reproducibility question

Ask a competent independent expert: “Could this method be reimplemented without contacting the authors or inferring hidden rules?” If not, enumerate every missing specification.

#### Required outputs

`method_and_theory_audit.md` containing:

- equation and notation issue table;
- method-completeness table;
- pseudocode/code mismatch table;
- complexity and evaluation-accounting assessment;
- reimplementation blockers; and
- required corrections ranked by severity.

#### Gate

`Gate F — Method and Theory` fails for a material equation error, ambiguous central mechanism, uncounted budget, unverified implementation-method mismatch, unsupported proof, or non-reimplementable core procedure. A printed update rule for a titular mechanism that contradicts the frozen implementation (decay on the wrong operand, a missing or collapsed learning rate) is a method-correctness failure here even when every reported number is correct, because reimplementation from the paper would build the wrong operator.

---

### Stage 7 — Data, benchmark, evidence, and provenance audit

#### Objective

Verify that the evidence used in the manuscript is authentic, complete, correctly scoped, and traceable from raw source to rendered claim.

Lead role(s): R5. Lead team: T3-STAT (Statistics, Uncertainty & Reproducibility). Stage 7 findings feed the provenance sections of `evidence_and_reproducibility_audit.md` (completed at Stage 12).

#### Required checks

1. Identify the authoritative evidence release, dataset version, or source records.
2. Separate:
   - raw evidence;
   - validated derived evidence;
   - rendered artifacts.
3. Verify checksums or immutable identifiers where available.
4. Verify sample, task, function, dimension, site, period, or population coverage.
5. Reconcile expected and actual counts.
6. Detect duplicate records, duplicate seeds, missing runs, malformed rows, NaN/Inf values, truncation, and unexplained exclusions.
7. Verify preprocessing, transformation, normalization, imputation, outlier, and failure rules.
8. Verify data leakage, train/test contamination, benchmark reuse, or tuning leakage.
9. Verify provenance for imported versus locally generated evidence.
10. Verify licenses, consent, privacy, or access restrictions.
11. Verify no result loader or analysis process silently falls back to a staging or obsolete path.
12. Verify each table and figure has a source binding and generator.
13. Verify the manuscript does not reconstruct results from old tables or plotted points.
14. Verify contradictory source metadata is resolved through a new release or documented correction, never silent editing.

#### Evidence anomaly report

For each anomaly record:

```text
anomaly_id
source_path_or_record
anomaly_type
expected
observed
scope
possible_causes
impact
whether repair is scientifically permissible
required disposition
```

#### Gate

`Gate G — Evidence Integrity` fails for untraceable headline results, edited immutable evidence, unresolved sample/run discrepancies, undisclosed data leakage, or use of a prohibited empirical source.

---

### Stage 8 — Research design, experiments, benchmarks, and comparator fairness

#### Objective

Determine whether the study design can answer the stated research questions and whether comparisons are fair.

Lead role(s): R3. Lead team: T2-BENCH (Benchmarking & Experimental-Methodology).

#### Research-question audit

For each research question or hypothesis verify:

- it is explicit and falsifiable where appropriate;
- the endpoint or outcome directly addresses it;
- the experimental unit and observation unit are clear;
- the design has an appropriate control or comparison;
- sample size, task count, or run count is justified;
- the study includes enough variation to support the claimed scope;
- the design separates confirmatory and exploratory analyses;
- development and evaluation data or benchmarks are distinguished; and
- the conclusion answers the question without expansion.

#### Comparator fairness audit

For every comparator or control verify:

- correct and current-enough method version;
- authoritative implementation provenance;
- same objective, data, tasks, and preprocessing;
- identical or genuinely equivalent budgets;
- comparable parameter-tuning effort;
- compatible initialization and random-seed policy;
- identical boundary, missingness, failure, and stopping rules;
- fair hardware, language, solver, and parallelism interpretation;
- comparable outcome definitions and numerical floors;
- valid pairing when paired tests are used; and
- complete disclosure of deviations.

Classify each comparison:

- `A — directly comparable and inferentially valid`;
- `B — comparable with verified imported evidence`;
- `C — descriptively informative but not valid for the planned inference`;
- `D — non-comparable and must be excluded from formal claims`.

#### Missing-experiment analysis

Identify missing experiments under these categories:

- necessary to validate the central claim;
- necessary to rule out a simpler explanation;
- necessary for fair comparison;
- necessary for statistical power or uncertainty;
- necessary for robustness;
- necessary for external validity;
- necessary for mechanism attribution;
- useful but non-essential extension.

For each requested experiment record, using the canonical Appendix A.5 schema:

```text
experiment_id
research_question
current_evidence_gap
minimum_design
controls
scope
endpoint
analysis
expected_decision_impact
admissible_evidence_available
classification
claim_affected
priority
estimated_scientific_value
status
```

State in `current_evidence_gap` why the current evidence is insufficient, record in `admissible_evidence_available` whether existing admissible evidence can already answer the question, and set `classification` using the section 12.11 controlled vocabulary.

#### Required outputs

`experimental_design_audit.md` (hypotheses, controls, comparators, fairness, missing experiments) and `missing_experiment_register.csv` using the Appendix A.5 schema.

#### Gate

`Gate H — Study Design and Fairness` fails when the central research question cannot be answered by the design, comparator unfairness changes conclusions, required controls are absent, or evaluation data were materially used for tuning without disclosure and mitigation.

---

### Stage 9 — Statistical validity and uncertainty audit

#### Objective

Verify that every inferential conclusion follows from an appropriate estimand, unit of analysis, test, correction, effect size, and uncertainty interval.

Lead role(s): R4. Lead team: T3-STAT (Statistics, Uncertainty & Reproducibility).

#### Statistical design checklist

For every analysis identify:

```text
analysis_id
research_question
estimand
endpoint
observation_unit
experimental_unit
aggregation_before_testing
pairing_key
independence_assumptions
sample_size_or_task_count
missing_data_rule
failure_encoding
test
one_or_two_sided_alternative
multiplicity_family
correction
effect_size
effect_direction
uncertainty_interval
resampling_unit
RNG_seed
software_and_version
```

#### Core statistical checks

- Is the estimand meaningful and aligned with the claim?
- Is the unit of analysis scientifically valid?
- Is pseudoreplication avoided?
- Is pairing genuine rather than inferred from shared labels?
- Are repeated measurements or hierarchical structures modeled correctly?
- Are distributional assumptions tested or justified?
- Are nonparametric methods used correctly rather than automatically?
- Are one-sided tests justified before results were known?
- Is multiplicity defined by a clear hypothesis family?
- Is correction applied to the correct family?
- Are raw and adjusted p-values clearly distinguished?
- Is `p = 0` avoided?
- Are effect sizes directionally defined?
- Are confidence or credible intervals attached to headline effects?
- Is the bootstrap or resampling level correct?
- Is the RNG seeded and reproducible?
- Are ties, zeros, censoring, failures, and missing values handled explicitly?
- Are rank calculations based on full precision?
- Are power, precision, or practical detectability discussed?
- Are robustness checks pre-specified or labeled exploratory?
- Are non-significant results interpreted without claiming equivalence?
- Are Bayesian analyses supplied with prior justification and sensitivity checks where applicable?
- Are model diagnostics, residuals, convergence, calibration, or goodness-of-fit checks appropriate?

#### Stochastic-optimization statistical module

When reviewing evolutionary computation, metaheuristics, or stochastic optimization, additionally verify:

- run-level variability is not confused with across-function variability;
- benchmark functions or tasks, not repeated runs alone, support broad algorithm claims;
- Friedman or related omnibus tests use the correct task unit;
- Nemenyi or other post-hoc displays match the actual design;
- Wilcoxon signed-rank uses valid paired task observations and reports zero/tie handling;
- Holm or another approved correction is applied to a declared family;
- Vargha–Delaney A12, rank-biserial correlation, Cliff’s delta, or another effect size has explicit direction;
- effect-size interpretation thresholds are pre-specified in the frozen analysis plan, sourced from the approved corpus, and applied consistently, with qualitative effect labels matching the frozen thresholds;
- BCa or other bootstrap intervals resample at the correct hierarchy;
- win/tie/loss definitions are explicit and not substituted for inference;
- dimension pooling is avoided unless a defensible weighting and estimand are preregistered;
- failed runs are not silently removed; and
- mean/median, numerical floor, and transformation choices receive sensitivity checks.

#### Statistical cross-check

Independently recompute, where possible, a representative sample of:

- descriptive summaries;
- ranks;
- test statistics;
- raw and adjusted p-values;
- effect sizes;
- confidence intervals;
- win/tie/loss counts; and
- values cited in the abstract or conclusion.

#### Required output

`statistical_audit.md` with a machine-readable statistical-analysis register row for every reported statistic (Appendix A.7 schema) and a ticket for every invalid, irreproducible, or misleading inference.

#### Gate

`Gate I — Statistical Validity` fails for invalid units, pseudoreplication, invalid pairing, undisclosed multiplicity, incorrect p-values/effects/intervals, outcome-driven test changes, or a headline statistical claim that cannot be reproduced.

---

### Stage 10 — Results integrity, interpretation, and internal consistency

#### Objective

Verify that the results are complete, consistent, accurately reported, and interpreted at the proper level.

Lead role(s): R1, supported by R4. Lead team: T1-OPT (Optimization & Metaheuristics), with T3-STAT on statistical consistency.

#### Required checks

- every reported result maps to an authoritative analysis ID;
- abstract, body, tables, figures, supplement, and conclusion agree (Highlights: not applicable — MDPI Algorithms solicits none; HL-01 NOT_APPLICABLE);
- table values match source data and stated rounding;
- figure points, bands, legends, scales, and labels match source data;
- negative, null, failed, and adverse outcomes are visible;
- results are not selected because they look favorable;
- primary and exploratory findings are separated;
- observations are reported before explanations;
- statistical significance is not confused with practical value;
- effect magnitude and uncertainty are discussed;
- exceptions and sign reversals are not hidden in aggregate values;
- subgroup or class analyses are pre-specified or labeled exploratory;
- convergence or temporal patterns are not treated as causal mechanism proof;
- imported evidence is not described as reproduced;
- descriptive comparisons are not written as inferential conclusions;
- conclusions do not exceed the strongest verified result; and
- limitations that materially affect interpretation are adjacent to the relevant result.

#### Contradiction matrix

Create a table of all inconsistencies among:

```text
title
abstract
introduction contributions
method claims
experimental setup
results prose
tables
figures
supplement
discussion
limitations
conclusion
highlights (N/A this venue)
graphical abstract (N/A this venue)
cover letter
```

For each inconsistency, identify the authoritative version and the required correction.

#### Gate

`Gate J — Result Integrity` fails for selective reporting, irreconcilable numeric inconsistencies, misleading aggregation, hidden adverse results, or interpretation that exceeds the evidence.


---

### Stage 11 — Robustness, sensitivity, ablation, and alternative-explanation review

#### Objective

Determine whether the conclusions survive reasonable analytical choices and whether component-level explanations are supported by an appropriate design.

Lead role(s): R3, supported by R4. Lead team: T2-BENCH (Benchmarking & Experimental-Methodology), with T3-STAT on statistical robustness.

#### Robustness review

Check, where relevant:

- alternative central tendency or outcome summary;
- different defensible transformations or numerical floors;
- missing-data and failed-run encodings;
- exclusion of disputed or non-comparable cells;
- leave-one-task, leave-one-site, or influence analysis;
- alternative multiplicity-family definitions;
- alternative but justified model specifications;
- correction for class imbalance, confounding, or covariate choices;
- different random seeds or data splits;
- sensitivity to hyperparameters or thresholds;
- external dataset, benchmark, time period, or domain;
- computational environment and numerical precision; and
- whether the headline conclusion reverses under any reasonable choice.

A conclusion that materially reverses under a reasonable analysis choice MUST be described as unstable.

#### Sensitivity-versus-ablation distinction

- **Parameter sensitivity** asks whether results change across nearby parameter values.
- **Ablation** asks what happens when a component or mechanism is removed, added, or altered.
- **Interaction analysis** asks whether components behave non-additively.
- **Mechanism validation** may require direct diagnostics beyond performance differences.

Do not use one as a substitute for another.

#### Ablation adequacy audit

For each component claim identify the design:

- remove-one from full system;
- add-one to a base system;
- cumulative or incremental addition;
- direct on/off overlay;
- factorial or targeted interaction;
- diagnostic or trace evidence; or
- no direct component evidence.

Then determine what the design can support:

| Design | Generally supports | Does not establish by itself |
|---|---|---|
| Remove-one | conditional necessity or performance change within the full configuration | isolated utility or independent causality |
| Add-one | utility relative to the selected base | utility in all configurations |
| Cumulative chain | order-conditional increment | order-independent contribution |
| Direct on/off | effect of the specific toggle when all else is held constant | broader mechanism explanation without diagnostics |
| Factorial/interaction | specified interaction within the tested design | untested interactions or universal causality |
| Sensitivity | stability near selected values | component necessity |

#### Required component-review questions

- Was the algorithm or method frozen before ablation?
- Do toggles change exactly one intended mechanism?
- Are dependent components identifiable in isolation?
- Are seeds, samples, tasks, budgets, and environments identical across cells?
- Are runtime and resource costs reported alongside performance?
- Are negative, null, and dimension-dependent effects preserved?
- Is statistical multiplicity handled across ablation contrasts?
- Are causal terms proportionate to design?
- Are ablation results located where the governing prompt permits them?
- Does any main-text, abstract, or conclusion sentence encode an ablation result — including a null or a neutral-looking pointer that implies a direction — in violation of the section 10.9 leak test, and is every supplementary-study cross-reference matched by an actual supplement entry?

#### Required outputs

- robustness matrix;
- component-claim-to-design matrix;
- list of unsupported mechanism claims;
- sensitivity and interaction gaps;
- conclusion-stability statement; and
- prioritized additional studies.

#### Gate

`Gate K — Robustness and Mechanism Attribution` fails when the central conclusion is unstable, component claims rely on inadequate designs, or governing ablation-placement rules are violated.

---

### Stage 12 — Reproducibility, transparency, and open-science audit

#### Objective

Determine whether an independent team can understand, rerun, and verify the reported study.

Lead role(s): R5. Lead team: T3-STAT (Statistics, Uncertainty & Reproducibility).

#### Reproducibility levels

Assess separately:

1. **Computational repeatability** — same code, data, environment, and seeds reproduce the outputs.
2. **Independent analytical replication** — an independent implementation of the analysis yields the same scientific values (named to avoid collision with the producing project’s “analytical” rebuild level in the determinism-contract audit below).
3. **Method reproducibility** — the method is specified sufficiently for reimplementation.
4. **Empirical replicability** — a new execution or data collection under the same protocol supports compatible conclusions.
5. **Generalizability** — the conclusion survives new tasks, populations, or contexts.

Do not claim a higher level from evidence supporting only a lower one.

#### Determinism-contract audit

When the producing project defines a delivery-level determinism contract (as the DT-GSK build framework does), audit it explicitly in addition to the scholarly levels above: the contract’s three delivery levels — **analytical** (identical numbers and statistics from a rebuild of the same immutable release), **visual** (identical rendered content), and **byte-for-byte** (identical files after timestamp normalization) — are progressively stricter forms of level 1 computational repeatability and are distinct from level 2 independent analytical replication, and this project taxonomy supersedes the generic level names above for compliance purposes. Verify that the reproducibility manifest (`papers/governance/reproducibility_manifest.json`) exists and records the achieved delivery level per artifact class, and that double-rebuild evidence from the immutable release supports the recorded levels: analytical reproducibility everywhere, visual reproducibility for all exhibits, and byte-for-byte reproducibility wherever timestamp normalization applies.

#### Required audit

Verify:

- code availability and license;
- data availability, access restrictions, and license;
- complete environment specification;
- package versions and numerical libraries;
- random seeds and deterministic controls;
- exact commands for experiments, analyses, figures, tables, PDF, and Word;
- configuration files and frozen defaults;
- source/evidence checksums;
- evaluator or preprocessing version;
- clean-room build or execution instructions;
- separation of raw, derived, and rendered artifacts;
- figure and table regeneration;
- statistical output regeneration;
- the producing project’s reproducibility manifest and its recorded delivery level (analytical / visual / byte-for-byte) per artifact class, against double-rebuild evidence;
- handling of unavailable proprietary components;
- expected runtime, hardware, and storage needs;
- known platform or floating-point variability;
- repository cleanliness and release tags;
- README completeness;
- archived source sufficient for future revision; and
- whether data/code availability claims are true at review time.

#### Clean-room verification

When tools and resources permit:

1. copy only the declared release package to a clean location;
2. follow the documented instructions exactly;
3. regenerate critical statistics and selected exhibits;
4. rebuild manuscript outputs;
5. compare values and normalized content; and
6. record every undocumented manual step.

A process that works only in the authors’ original workspace is not independently reproducible.

#### Required output

`evidence_and_reproducibility_audit.md` containing a reproducibility scorecard, the list of undocumented steps, the clean-room result, the minimum release package needed for submission, and the Stage 7 provenance and anomaly findings.

#### Gate

`Gate L — Reproducibility` fails when central results cannot be regenerated, method details are missing, evidence provenance is incomplete, availability statements are inaccurate, or the producing project’s recorded delivery levels (analytical / visual / byte-for-byte) are missing or unsupported by rebuild evidence.

---

### Stage 13 — Figures, tables, equations, algorithms, and visual evidence audit

#### Objective

Verify that every exhibit is scientifically necessary, accurate, legible, accessible, and correctly bound to evidence.

Lead role(s): VIZ. Lead team: T5-WRITE (Scientific-Writing, Exhibits & Data-Visualization).

#### Universal exhibit questions

For every figure, table, equation block, algorithm, flowchart, or diagram:

- What question does it answer?
- Is it cited and discussed at the correct location?
- Is it redundant with another exhibit?
- Does it have an authoritative source and generator?
- Does the caption explain scope, metric, aggregation, sample/run count, uncertainty, and symbols?
- Are all labels, units, algorithms, dimensions, tasks, and legends correct?
- Is it legible at final journal size?
- Is the design accessible in grayscale and for common color-vision deficiencies?
- Does it avoid misleading scale, truncation, smoothing, 3-D effects, visual area distortion, or selective ranges?
- Does it disclose missing data or missing series?
- Does it use consistent algorithm/group ordering across the manuscript?
- Does it preserve unfavorable outcomes?
- Does it agree with the prose and supplement?

#### Figure-specific audit

Check:

- vector format where practical;
- embedded fonts where required;
- final-size label and line thickness;
- correct axis origin, transformation, and logarithmic zero handling;
- uncertainty bands or intervals where appropriate;
- no smoothing that changes interpretation;
- identical scales for genuinely comparable panels;
- non-color line/marker encodings;
- no cropped legends, labels, or data;
- no duplicated curves and no undisclosed missing curves — a missing series is acceptable only with an explicit caption-level absence note per the governing convergence profile (section 10.8);
- no best-run selection when an aggregate is required;
- representative-case selection follows a stated rule;
- no exhibit prints a raw BibTeX key, an internal registry ID (for example an evidence `E`-number), or any other build-internal token where a reader-facing citation or a printed equation/figure number belongs, and any internal-ID-to-printed-number correspondence shown to reviewers is carried by an explicit legend;
- no “figure” is actually a table (coloured ON/OFF cells, plotted text, a dense auto-generated box-and-arrow rail with a colour legend) — such an artifact is re-rendered as a clean native table or a simple labelled flowchart per section 10.17; and
- image manipulation is limited to scientifically legitimate global adjustments.

#### Table-specific audit

Check:

- statistic and dispersion are named;
- optimization or outcome direction is clear;
- sample/run count and denominator are shown;
- significance, effect, tie, missingness, and formatting symbols are defined;
- decisions are based on unrounded values;
- bolding or highlighting is accurate;
- decimal and scientific notation are consistent;
- table cells equal authoritative display values;
- large tables belong in the supplement when appropriate;
- no table is a screenshot; and
- Word tables are native and editable (`w:tbl`) when a Word submission is required, and any “figure-table” or schematic whose step content a reader or editor may need to change is likewise a native editable table rather than a rasterized image (section 10.17).

#### Equation and algorithm presentation audit

Check:

- equation numbering is complete and stable;
- every cross-reference resolves;
- symbols are consistent with the notation table;
- algorithms correspond to code and equations;
- line breaks do not alter mathematical meaning;
- Word equations are native OMML when required;
- no equation is flattened into an image;
- pseudocode is readable, complete, and not decorative;
- pseudocode is clean, eye-friendly, and row-based with hidden or minimal grid lines (booktabs top/mid/bottom rules only, no vertical rules, no full cell grid), with numbered steps, consistent indentation, hanging continuation lines that never collide with the margin, and logical phase grouping; a block that overflows, collides, or double-prints is a ticket even when its content is correct (section 10.17.2); and
- a complex algorithm is accompanied by a simple control-flow flowchart (a handful of boxes and arrows, optionally a base-vs-proposed pair) where it aids comprehension, and every printed equation label matches the notation table and the reader-facing equation number rather than an internal registry ID (section 10.17).

#### Required output

`exhibit_audit.csv` with one row per artifact (Appendix A.4 schema); exact correction instructions are carried in the tickets linked through `issue_ticket_ids`.

#### Gate

`Gate M — Exhibit Integrity` fails for a data-inaccurate figure/table, misleading visual encoding, unreadable central exhibit, broken equation, or image-based Word mathematics/table where native editability is required. A raw BibTeX key or internal registry ID printed in an exhibit in place of the reader-facing citation or equation number, and a central pseudocode block that overflows, collides, or double-prints, are Gate M failures even when the underlying data are correct.

---

### Stage 14 — Section-by-section scientific and editorial review

#### Objective

Evaluate every manuscript section according to its scientific function rather than grammar alone.

Lead role(s): AE, supported by RW. Lead team: ECB (Editorial Coordination Board), with T5-WRITE on section-level writing.

#### Stage 14.1 Title

Verify that the title:

- identifies the subject and central contribution;
- remains accurate at the tested scope;
- avoids unsupported superlatives;
- avoids terms such as “robust,” “efficient,” “large-scale,” “high-dimensional,” “state-of-the-art,” or “general” unless directly supported; and
- is concise enough for the target journal.

#### Stage 14.2 Abstract

Verify that the abstract contains:

- problem and precise gap;
- central method or contribution;
- verified evaluation scope;
- one or two correctly bound results when allowed;
- appropriate uncertainty or qualification;
- a conclusion within evidence; and
- no citation, abbreviation, result, or claim prohibited by the journal.

Every abstract sentence MUST have a claim-audit row. The abstract MUST NOT contain a stronger claim than the body.

#### Stage 14.3 Keywords

Check journal count, specificity, discoverability, non-duplication of title terms where advisable, and use of established field vocabulary.

#### Stage 14.4 Introduction

Verify:

- motivation is supported and specific;
- the problem matters to the target readership;
- the prior-state summary is fair;
- the gap is precise and evidence-backed;
- the research questions or hypotheses are explicit;
- contributions are distinct, testable, and not inflated;
- the claimed novelty is bounded;
- the manuscript’s scope is clear; and
- the roadmap is useful rather than formulaic.

#### Stage 14.5 Related work

Verify synthesis by concepts and relationships, clear closest-work comparison, balanced coverage, source-accurate limitations, and no bibliography catalogue.

#### Stage 14.6 Problem formulation or background

Verify definitions, assumptions, notation, outcome direction, domain, units, and separation between inherited material and new contribution.

#### Stage 14.7 Proposed method or methodology

Verify design rationale, formal specification, implementation correspondence, parameters, safeguards, complexity, resource cost, expected behavior, and exact test of each contribution.

#### Stage 14.8 Experimental or study setup

Verify research questions, evidence/dataset release, sample/task/function scope, inclusion/exclusion, run count, seeds, budgets, comparator versions, tuning, environment, failures, statistics, and availability.

#### Stage 14.9 Results

Verify order follows research questions, all primary evidence appears, results precede interpretation, uncertainty and effect are visible, adverse findings are retained, and the section does not merely narrate every cell.

#### Stage 14.10 Discussion

Verify:

- central findings are interpreted rather than repeated;
- alternative explanations are considered;
- mechanism explanations are correctly labeled;
- comparison with literature is fair;
- practical meaning is discussed without speculation;
- cost and trade-offs are explicit;
- generalization is bounded; and
- contradictory or unstable results are addressed.

#### Stage 14.11 Limitations and threats to validity

Require visible treatment of, where relevant:

- construct validity;
- internal validity;
- statistical conclusion validity;
- external validity;
- benchmark or dataset scope;
- comparator scope;
- sample size, stochastic variation, and power;
- tuning or development leakage;
- implementation and environment differences;
- missing or failed observations;
- multiplicity and analytical flexibility;
- computational cost;
- reproducibility limitations;
- literature-corpus limitations;
- ethics/privacy constraints; and
- absence or limits of mechanism evidence.

A limitation section that immediately neutralizes every limitation with promotional language is inadequate.

#### Stage 14.12 Conclusion

Verify that the conclusion:

- restates only established findings;
- answers the research questions;
- gives exact scope;
- includes the main limitation or boundary;
- introduces no new result, mechanism, citation, or promise;
- avoids universal or causal overstatement; and
- proposes realistic future work tied to identified gaps.

#### Stage 14.13 Declarations and availability

Verify authorship, contribution taxonomy, funding, conflicts, ethics, consent, data/code availability, acknowledgments, and tool/generative-AI disclosure using verified information only.

#### Stage 14.14 Supplementary material

Verify the supplement is navigable, standalone where required, fully cross-referenced, not used to hide contrary primary results, and contains complete supporting evidence, methods, tables, figures, analyses, and reproducibility details appropriate to its role.

#### Stage 14.15 Cover letter, highlights, and graphical abstract — DT-GSK profile: Highlights and a graphical abstract are NOT_APPLICABLE at MDPI Algorithms (HL-01); this stage applies to the cover letter only

Apply the same claim ceiling as the manuscript. Remove unverified novelty, journal flattery, guaranteed impact, or claims not present in the accepted claim matrix.

#### Stage 14.16 Exemplar parity and presentation conventions

When the DT-GSK profile (section 10) governs, verify that the manuscript passed the build framework’s exemplar-parity editorial check: a section-by-section comparison against `papers/governance/presentation_conventions.md` and the three presentation exemplars — GSK (`mohamed2020gaining`), eGSK (`jawad2024egsk`), and ATMALS-GSK (`alfadli2025atmals`) — across the registered 22-dimension comparative review. Ticket every unjustified deviation.

#### Required output

`section_review.md` — for every section provide:

```text
purpose
strengths
critical_or_major_findings
moderate_minor_findings
missing_content
claims_to_narrow
recommended_structure
example_revision_only_after_fact_check
score_1_to_5
```

---

### Stage 15 — Scientific writing, natural scholarly voice, and authorship-integrity audit

#### Objective

Ensure the manuscript reads as precise, original, expert scholarship while preserving every scientific fact and avoiding any attempt to game authorship-detection systems.

Lead role(s): RW, supported by RI. Lead team: T5-WRITE (Scientific-Writing, Exhibits & Data-Visualization), with T6-INTEG on authorship integrity.

#### Stage 15.1 Core writing criteria

Evaluate:

- clarity of the central argument;
- logical progression across sections and paragraphs;
- concrete, discipline-specific language;
- consistent technical terminology;
- sentence-length and syntactic variety driven by meaning;
- natural transitions earned by the argument;
- calibrated hedging;
- active verbs and clear agents where appropriate;
- appropriate use of first-person plural;
- readable equation and figure integration;
- paragraph focus;
- distinction among evidence, inference, and speculation;
- economy without loss of necessary detail;
- stable authorial voice; and
- language appropriate to an expert international readership.

#### Stage 15.2 Formulaic or machine-like patterns to flag

Flag patterns such as:

- repeated “Moreover,” “Furthermore,” “Additionally,” “Notably,” or “It is worth noting that” openings;
- mechanically identical paragraph lengths;
- repetitive claim–claim–claim paragraphs without evidence;
- excessive three-part lists or “First/Second/Third” ladders;
- generic statements that could appear unchanged in any paper;
- repeated phrases such as “plays a crucial role,” “paves the way,” “sheds light on,” or “significant improvement” without specifics;
- inflated abstract nouns where a direct verb is clearer;
- unnatural synonym variation for the same technical concept;
- constant passive voice that obscures responsibility;
- excessive self-reference such as “this study” in consecutive sentences;
- abrupt topic changes hidden by stock transitions;
- over-regular sentence rhythm;
- conclusion-like summaries repeated at the end of every subsection;
- vague intensifiers such as “remarkably,” “substantially,” or “considerably” without a quantified basis;
- generic limitations that do not name the actual scope; and
- polished but empty prose that provides no evidence or reasoning.

#### Stage 15.3 Authentic scholarly reasoning test

A passage reads as genuinely expert when it:

- names the actual method, dataset, benchmark, population, dimension, or result;
- explains why the observation matters;
- distinguishes plausible explanations;
- acknowledges a boundary or uncertainty;
- uses terminology consistently;
- cites the correct evidence; and
- could not be transplanted unchanged into an unrelated paper.

#### Stage 15.4 Safe revision protocol

For each sentence or paragraph needing substantial revision, provide:

```text
location
original_text_or_short_excerpt
problem
scientific_meaning_that_must_be_preserved
suggested_revision
why_the_revision_is_better
facts_numbers_citations_verified: yes / no
```

If facts, numbers, or citations are not verified, do not provide a definitive rewrite. Provide a revision template with placeholders.

A style-only edit MAY change wording, order, sentence boundaries, and transitions. It MUST NOT change:

- numerical values;
- statistical interpretation;
- claim scope;
- citations or source meaning;
- equations;
- method behavior;
- experimental design;
- table or figure content; or
- limitations.

#### Stage 15.5 Authorship and AI-detection integrity

The review MUST state clearly:

- automated AI-text detectors are not a reliable scientific quality or authorship standard;
- no detector result can prove who wrote a passage;
- the manuscript should be improved for clarity, originality, specificity, and intellectual ownership, not to deceive a detector;
- tool use must follow the target journal’s current disclosure policy;
- authors remain responsible for every claim, citation, calculation, and sentence; and
- intentional errors, random variation, synonym spinning, hidden characters, paraphraser loops, or fabricated anecdotes are prohibited.

Do not promise that the manuscript will “pass AI detection.” The acceptable goal is high-quality, genuinely reviewed, author-owned scholarly prose that naturally lacks repetitive templated patterns.

#### Stage 15.6 Writing audit outputs

Produce `writing_integrity_audit.md` containing:

- overall prose profile;
- recurring-pattern frequency table;
- terminology inconsistency list;
- paragraph-level coherence issues;
- the 20–30 highest-impact example revisions, or all when fewer exist;
- a list of generic sentences to remove or replace with evidence;
- a style-only revision checklist; and
- an authorship-integrity and disclosure note.

#### Gate

`Gate N — Writing and Authorship Integrity` fails when language obscures science, formulaic text materially harms credibility, claims become stronger during editing, or detector-evasion tactics are used.

---

### Stage 16 — Ethics, research integrity, and publication-practice review

#### Objective

Verify that the study and submission comply with ethical, legal, and publication-integrity requirements.

Lead role(s): RI. Lead team: T6-INTEG (Ethics, Research-Integrity, Citation & Publication-Practice).

#### Required checks

Assess, where applicable:

- ethics committee or institutional review approval;
- informed consent;
- privacy, de-identification, and data protection;
- use of human, animal, clinical, sensitive, proprietary, or indigenous data;
- prospective registration or trial registration;
- biosafety, dual-use, or security concerns;
- author qualification and contribution statements;
- ghost, guest, or omitted authorship risk;
- conflicts of interest;
- funding and sponsor role;
- duplicate submission or redundant publication;
- salami slicing;
- plagiarism and patchwriting;
- citation manipulation;
- image or data manipulation;
- undisclosed exclusions or result switching;
- retractions, corrections, or expressions of concern affecting cited work;
- software, dataset, and figure licenses;
- generative-AI or tool disclosure required by the journal; and
- truthful data/code availability claims.

Do not invent an approval number, funding source, contributor role, conflict statement, or disclosure. Missing verified administrative information is a block on upload readiness, not permission to guess.

#### Generative-AI authorship, disclosure, and AI-writing-detection review (deep procedure)

Integrity screening at major publishers is now automated and mandatory, and the review MUST treat generative-AI (GenAI) disclosure as a first-class integrity axis rather than a single checklist line. Current examples the review must account for: MDPI's in-house *Ethicality* system screens every submission for AI-generated or manipulated text, paper-mill activity, fabricated or manipulated references, citation manipulation, authorship anomalies, and AI-generated review reports, running alongside iThenticate text-similarity and image-integrity screening; Elsevier and Springer Nature apply COPE-aligned GenAI policies. Verify every item below against the venue's **currently-fetched official policy** (record source and access date); do not rely on remembered policy text.

- **D16.1 Disclosure-completeness (policy-anchored).** The prevailing COPE-aligned structure imposes three obligations: (i) a declaration of GenAI use **at submission** (the submission-system field); (ii) a description of **how** the tool was used, in Methods/Materials (or an equivalent methods-level statement for papers with no M&M section); and (iii) the tool **name and version** in the Acknowledgments. Superficial language-only editing (grammar, spelling, punctuation, formatting) is typically **exempt**; substantive drafting, rephrasing of technical content, or data/figure/analysis assistance is **not exempt** and must be disclosed. Flag a substantive-use manuscript that discloses only "grammar checking" as a **major** under-disclosure: under automated screening a detector flag plus minimal disclosure reads as evasive, whereas a flag plus honest disclosure is a non-event.
- **D16.2 Authorship prohibition.** No AI system may be listed as an author or co-author (it cannot take responsibility, assert conflicts of interest, or hold copyright). A named AI author is a **critical** block.
- **D16.3 Disclosure-wording quality.** The strongest disclosure **separates language assistance from scientific substance** and takes explicit author responsibility. Check that the statement (a) names the tool and, where required, its version; (b) scopes the use honestly (e.g., "language editing, rephrasing, and drafting of descriptive text"); (c) affirms that the scientific content — design, data, analysis, and every reported number — states precisely which scientific elements the AI system did not produce (experiment design, data, statistics, claims, conclusions) and honestly discloses all substantive assistance, including software-engineering support — the shipped SE-010 declaration is the model; do NOT demand a blanket "independently of any AI system" affirmation, which the manuscript deliberately removed as false; and (d) states the authors reviewed, verified, and take full responsibility. Reward disclosures that make the "the science is ours" claim **checkable** (e.g., an evidence-locked, deterministically re-derivable results pipeline): such a claim converts an AI flag from a liability into a verifiable defense. Penalize apologetic, vague, or over-long disclosures — a short, factual, responsibility-taking statement is the professional norm.
- **D16.4 Detection-risk assessment (with the false-positive science).** AI-writing detectors are a **screening aid, never dispositive**. The review MUST NOT allege undisclosed AI writing on a detector score alone, because peer-reviewed 2025/2026 evaluations establish that: formulaic, low-perplexity **scientific prose** (methods, protocol, statistics) is the hardest genre, with science-genre accuracy far below humanities; **non-native-English** academic writing carries historically-elevated false-positive rates (foundational work reported ~61% average false positives on TOEFL essays for 2023-era detectors — improved but not eliminated in current tools); and **hybrid** or paraphrased text collapses detector recall. If a detector is used, prefer the tool with the best independently-verified false-positive record, treat any flag as a prompt to check **disclosure compliance** (not as misconduct evidence), and record the tool, score, and the false-positive caveat. A methods paragraph flagged by a detector is not, by itself, a ticket.
- **D16.5 Consistency check.** The submission-form declaration, the Methods statement, and the Acknowledgments must name the **same** tool(s) and use(s); automated systems cross-check these, so a mismatch is a **major** ticket.
- **D16.6 Cross-format persistence.** The disclosure must render in **both** the PDF and Word deliverables; a disclosure present in only one format is an upload-readiness defect.

Record findings in `ai_disclosure_audit.md` using the Appendix A.10 schema.

#### Required output

`ethics_and_compliance_audit.md` containing an ethics and integrity matrix with `PASS / FAIL / BLOCKED / NOT APPLICABLE`, evidence, and required author confirmation; and `ai_disclosure_audit.md` (Appendix A.10) recording the six GenAI checks D16.1–D16.6 with the venue policy source and access date.

#### Gate

`Gate O — Ethics and Publication Integrity` fails for a material undisclosed ethics issue, fabricated declaration, manipulated evidence, plagiarism concern not resolved, inaccurate availability statement, a named AI author, GenAI under-disclosure relative to the verified venue policy, or a detector-based misconduct allegation made without corroboration.

---

### Stage 17 — Target-journal compliance and production-quality review

#### Objective

Verify current journal compliance and equality across all submission formats.

Lead role(s): JCO, PROD-PDF, and PROD-WORD (co-leads). Lead teams: T7-VENUE (journal compliance) and T4-SOFT (production).

#### Journal-instruction audit

Use current official journal guidance to verify:

- scope and article type;
- manuscript structure;
- title, abstract, keyword, word, and page limits;
- reference style;
- anonymization;
- figure and table limits and formats;
- graphical abstract and highlights;
- supplementary rules;
- data, code, ethics, conflict, funding, author-contribution, and AI-tool declarations;
- required reporting checklists;
- file-naming and upload requirements;
- Word versus LaTeX support;
- preprint or prior-publication policy;
- reviewer-suggestion rules; and
- accessibility or metadata requirements.

Record the official source and access date. Do not rely on remembered requirements. When the DT-GSK profile governs, additionally verify the hard page-limit rule of section 10.14.

#### Venue-fit, quartile, and comparator-culture verification (deep procedure)

Beyond mechanical instruction compliance, assess whether the manuscript is placed in a venue that will plausibly accept it, verified from **current** sources (never remembered metrics; record source and access date):

- **D17.1 Two-index standing.** Record the venue's current standing on **both** indices the author's institution may score: Web of Science (JCR Impact Factor + quartile + category rank, from the latest JCR release) and Scopus (CiteScore + percentile + SJR quartile). Note ESCI-versus-SCIE indexing and any quartile that **differs between indices** (a journal can be WoS-Q2 while Scopus-Q1, or the reverse). If the manuscript or cover letter states a quartile, verify it against the current source and flag any stale, index-ambiguous, or self-computed (non-JCR/non-Scopus) figure. Where the author's degree/institution accepts a Q1-or-Q2 threshold, confirm the venue clears it on at least one recognized index and state which.
- **D17.2 Scope and article-type fit.** Confirm the manuscript's contribution type matches the venue's **actual published output**, not merely its stated aims. For an algorithm or benchmark manuscript, verify the venue routinely publishes comparable work; direct **family/method precedent** in the venue is the strongest positive signal and should be cited in the assessment.
- **D17.3 Comparator-culture and rejection-risk.** Identify the venue's implicit reviewer expectations. A benchmark manuscript with a **family-scoped or otherwise narrow comparator panel** faces a high rejection risk at venues whose reviewers customarily demand strong external state-of-the-art comparators; record this as a top rejection risk with a concrete mitigation (broaden the panel, or foreground and defend the scope). Where the venue has direct precedent for the paper's exact comparator scope, record that as a de-risking signal that lowers the risk.
- **D17.4 Acceptance realism and laddering.** Where publisher-stated or independently reported, record the typical time-to-first-decision, open-access model and APC, and desk-rejection tendency, and judge whether the target is a realistic first choice or a fallback. Recommend a **laddered venue plan** (primary plus two fallbacks) matched to the paper's true competitive tier, and flag any mismatch between the paper's ambition and the chosen venue in either direction (over-reaching invites desk rejection; under-reaching wastes the contribution).

Findings feed the top-ten rejection risks (section 12.6) and, where the DT-GSK profile governs, section 10.13.

#### LaTeX/PDF review

Verify:

- correct current template/class (deviations recorded and ACCEPTED in `papers/governance/production_deviation_record.md` — D-1 dated vendored mdpi.cls, D-3 suppressed submit-mode branding — satisfy this check; only UNDOCUMENTED deviations are defects);
- clean build from a clean directory;
- zero undefined citations or references;
- no missing figures, fonts, or files;
- no harmful overfull/underfull boxes;
- correct page count;
- legible final-size exhibits;
- embedded fonts and acceptable figure formats;
- correct metadata and bookmarks;
- no hidden template instructions or comments; and
- visual inspection of every page.

#### Microsoft Word/OOXML review

When Word is a required deliverable, verify:

- all equations are native OMML (`m:oMath` or `m:oMathPara`);
- all tables are native `w:tbl` structures;
- captions are editable paragraphs;
- figure, table, algorithm, and equation numbering use live fields where required;
- cross-references use valid bookmarks and REF fields when required; a documented, journal-approved static-field deviation recorded in `word_validation_report.md` satisfies this check;
- citations and bibliography remain updateable when required;
- TOC and lists update correctly;
- section numbering uses styles/multilevel lists;
- alt text is present where required;
- diagrams have editable native or companion sources;
- Word opens, updates, saves, and reopens without repair;
- no equations or tables are screenshots;
- tracked changes, comments, hidden text, and placeholders are absent; and
- content matches LaTeX/PDF semantically.

#### Cross-format parity

Compare title, abstract, section order, equations, algorithms, table values, figures, captions, citations, references, cross-references, statistics, declarations, and supplement pointers across canonical source, PDF, and Word.

#### DOCX-to-PDF typographic and visual parity (deep procedure)

When both a LaTeX/PDF and a Word deliverable are required, the review must verify that the Word document reproduces the **typographic appearance** of the LaTeX PDF so closely that exporting the DOCX to PDF (author-side, via Word `Save As PDF` or a headless converter) yields a document visually consistent with the LaTeX PDF. This is a distinct axis from the semantic cross-format parity above and from the OOXML-editability review: here the object under test is **rendered appearance**, not content or editability.

**Honest scope (do not over- or under-ticket).** LaTeX and Word are different typesetting engines: even with identical fonts, sizes, and margins, **line breaks, hyphenation, and pagination will differ**, and native OMML math (typically Cambria Math) will not be pixel-identical to LaTeX math (e.g., Pazo/Computer Modern). These are unavoidable engine differences and MUST NOT be ticketed as defects. The parity target is **typography and layout family** — same font, size, weight, alignment, margins, page geometry, and table/figure styling — with a page-count delta within roughly ±1–2 pages. A **typography mismatch** (wrong font, size, weight, or alignment) IS a defect; an unavoidable line-break difference is not.

**T1 — Establish the ground truth.** Extract the target typography from the LaTeX class/template (for MDPI, `mdpi.cls`): body font family and size, body alignment (justified vs. ragged), page size and margins, title size, heading sizes and weights (section/subsection/subsubsection), and caption size. Record this as the parity specification. Do not assume; read the class.

**T2 — Inspect the Word styles against the specification.** Unzip the DOCX and read `word/styles.xml`. For each mapped style (`Normal`/body, `Heading 1`/`2`/`3`, `Title`, `Caption`, `Table`, `Bibliography`) verify: the font name on `w:rFonts` (`w:ascii`, `w:hAnsi`, `w:cs` all set to the specified family); the size on `w:sz` (half-points: 20 = 10 pt); the alignment on `w:jc` (`both` for justified body); and — critically — that bold/italic are read from the `w:val` attribute, not mere element presence (`<w:b w:val="0"/>` means **not** bold; a naive presence check misreads it). Confirm the mapped weights match the class (e.g., section bold, subsection italic, subsubsection regular where the class specifies that).

**T3 — Verify the reference template and font availability.** Confirm the reference/style template (e.g., `reference.docx`) encodes the T1 specification, and that the named body font is one that actually renders on the target platform (for example, Palatino Linotype is Windows-native; if the specified font is absent, Word substitutes and parity breaks — flag substitution risk and name the required font).

**T4 — Perform an actual export comparison when a renderer is available.** Export the DOCX to PDF (Microsoft Word or LibreOffice `--headless --convert-to pdf`) and compare page-by-page against the LaTeX PDF: body font/size/alignment, heading appearance, table shading and column layout, figure placement and sizing, caption style, and the page-count delta. Render representative pages of both to images and inspect side-by-side. Record concrete mismatches with page numbers.

**T5 — Deviation when no renderer is available.** If neither Word nor a headless converter is available in the review environment, the DOCX→PDF export comparison is recorded as a **documented deviation** in `word_validation_report.md` (the section 11 sole-exception mechanism): the style-level match from T2–T3 is verified, and the report states that the author-side open-in-Word / `Save As PDF` visual confirmation is a required pre-submission step. A style-level match is a strong but not complete substitute for the rendered comparison; say so explicitly.

**Defect classes to ticket (major unless noted).** Wrong body font family or size; body left-aligned where the class justifies; heading weight/style mismatch (bold vs. italic vs. regular); wrong title or caption size; wrong page size or margins (the Word text-measure difference is approved deviation D-4 — `production_deviation_record.md`, `word_validation_report.md` §9.4 — and is not ticketable; only NEW drift beyond the recorded values is a defect); equations rendered as images (**critical** — also fails the OOXML review); tables rendered as images (**critical**); page-count delta beyond ~±2 pages (signals a real style/layout error, not an engine difference); a specified font that is unavailable on the target platform with no substitution note.

#### Required output

`journal_compliance_matrix.csv`, `pdf_build_report.md`, `word_validation_report.md` (including the T1–T5 typographic-parity spec, the per-style styles.xml findings, and the DOCX→PDF export comparison or its documented deviation), and `cross_format_consistency_report.md` (the section 7 mandated artifacts), plus an exact list of upload-blocking defects.

#### Gate

`Gate P — Journal and Production Compliance` fails when the review relied on remembered, outdated, or unofficial instructions, or for a broken build, format divergence, non-editable required Word content, a DOCX-to-PDF typographic-parity failure (wrong body font, size, or alignment; heading weight/style mismatch; equations or tables rendered as images; page-count divergence signalling a layout error rather than an engine difference), missing declarations, or a page/file requirement violation. When current official journal guidance is unavailable, the gate is `BLOCKED` per section 1.3, and the minimum evidence needed to unblock it MUST be stated.

---

### Stage 18 — Independent Q1/Q2 reviewer simulation

#### Objective

Predict realistic peer-review objections before submission and expose issues that checklist-based review may miss.

Lead role(s): AE, with independent reports from EIC, AE, and R1–R6. Lead team: ECB (Editorial Coordination Board), drawing independent findings from all seven specialist teams.

#### Reviewer report format

Each reviewer MUST provide independently:

```text
reviewer_role
expertise
confidence
one-paragraph manuscript summary
overall assessment
three_to_five_specific_strengths
major_concerns
minor_concerns
questions_for_authors
required_additional_analyses_or_experiments
claims_that_must_be_narrowed
reproducibility_concerns
presentation_concerns
recommendation
score_1_to_5_by_assigned_categories
```

#### Required simulated reports

Record all reports, together with the specialist roles’ pre-consensus findings from their lead stages, in `independent_reviewer_reports.md`.

##### EIC report

Focus on fit, significance, novelty, desk-rejection risk, and whether external review is justified.

##### AE report

Focus on whether the evidence package can support a fair decision, how reviewer concerns interact, and what revision level is proportionate.

##### R1 — Domain-science reviewer

Challenge problem importance, literature gap, contribution distinction, baseline strength, and scientific implications.

##### R2 — Theory/method reviewer

Attempt to rederive the method, expose undefined assumptions, identify equation/pseudocode/code mismatches, and challenge complexity or mechanism rationale.

##### R3 — Experimental-design reviewer

Challenge benchmark/dataset choice, controls, comparator fairness, tuning, scope, failure policy, and external validity.

##### R4 — Statistical reviewer

Challenge estimands, units, independence, multiplicity, effects, intervals, robustness, and interpretation.

##### R5 — Reproducibility reviewer

Attempt to trace and rebuild headline results. Treat every undocumented manual step as a finding.

##### R6 — Skeptical domain reviewer

Construct the strongest plausible rejection argument. Specifically ask whether:

- the method is an incremental assembly of known mechanisms;
- improvements come from tuning or added computation;
- the comparator panel is too narrow;
- the benchmark was used during development;
- adverse cases are hidden;
- ablation is insufficient;
- the mechanism explanation is post hoc;
- statistical significance lacks practical importance;
- runtime or memory cost offsets gains;
- the result generalizes beyond the tested scope; and
- another simpler method could explain the outcome.

#### Predicted reviewer-question bank

Generate at least 25 likely questions tailored to the manuscript in `predicted_reviewer_questions.md`, including:

1. What exactly is new relative to the closest method?
2. Why is the identified gap scientifically important?
3. Which components are inherited, adapted, or original?
4. Does the method add computational or objective-evaluation cost?
5. Were the evaluation benchmarks, datasets, or test cases used during development?
6. How were hyperparameters selected and what was the tuning budget?
7. Why were these comparators selected, and which strong alternatives are missing?
8. Are comparator implementations and budgets genuinely fair?
9. What is the experimental unit?
10. Why is the chosen statistical test valid?
11. How is multiplicity controlled?
12. What is the practical effect size and uncertainty?
13. Do conclusions change under alternative reasonable analyses?
14. How are failed runs or missing observations treated?
15. Why is the reported convergence behavior representative?
16. What failure cases or dimensions weaken the method?
17. Does ablation isolate components or only show conditional differences?
18. Are component interactions tested?
19. Is the method reproducible from the paper and package?
20. Are source code, data, seeds, and exact commands available?
21. How sensitive are results to parameter values?
22. Does the method generalize beyond the chosen benchmark or dataset?
23. What are the time and memory trade-offs?
24. Which conclusion would change if one comparison cell were removed?
25. Why is this work appropriate for this journal rather than a narrower venue?

Add manuscript-specific questions beyond these defaults.

---

### Stage 19 — Cross-review validation, consensus, and editorial decision

#### Objective

Combine independent reviews without erasing disagreement or allowing majority opinion to overrule evidence.

Lead role(s): SE, with AE and EIC. Lead team: ECB (Editorial Coordination Board); the arbitration council of section 3.6 convenes here.

#### Consensus procedure

1. Merge duplicate tickets while preserving all supporting evidence.
2. Group tickets by dependency and root cause.
3. Identify reviewer agreements.
4. Identify disagreements and the evidence needed to resolve them.
5. Classify each requested new experiment or analysis using the section 12.11 controlled vocabulary: `essential_before_submission`, `recommended_for_q1`, `useful_for_q2`, or `optional_or_out_of_scope`.
6. Reassess severity when one defect creates multiple downstream symptoms.
7. Determine whether the manuscript’s central thesis survives all confirmed findings.
8. Produce a single dependency-aware revision roadmap.
9. Recalculate category scores only after consensus.
10. Apply hard gates before considering the weighted score.

#### Editorial consensus output

Provide:

- agreed strengths;
- agreed critical and major issues;
- unresolved reviewer disagreements;
- top ten rejection risks;
- minimum revision required for Q2 readiness;
- additional revision required for Q1 readiness;
- experiments or analyses that cannot be replaced by prose;
- claims that must be removed if new evidence is not produced;
- journal-fit alternatives when the target is unrealistic; and
- final internal disposition.

Record the consensus category scores in `review_scorecard.csv`, the consolidated ticket set in `issue_register.csv`, and the gate status, score, verdict, residual risks, and submission recommendation in `final_readiness_report.md` (updated after Stage 20 verification).

#### Internal disposition codes

Choose one:

- `D0 — ASSESSMENT BLOCKED`;
- `D1 — DO NOT SUBMIT / REDESIGN REQUIRED`;
- `D2 — MAJOR PRE-SUBMISSION REVISION`;
- `D3 — MINOR PRE-SUBMISSION REVISION`;
- `D4 — Q2-READY CANDIDATE`;
- `D5 — Q1-READY CANDIDATE`; or
- `D6 — SCIENTIFICALLY READY, ADMINISTRATIVELY BLOCKED`.

Never use `ACCEPTED`, because only a journal can accept a manuscript.

---

### Stage 20 — Revision planning, response preparation, and post-revision verification

#### Objective

Convert the review into an executable correction program and verify that revisions solve root causes without creating regressions.

Lead role(s): SE. Lead team: ECB (Editorial Coordination Board).

#### Revision order

Apply revisions in this dependency order:

1. evidence or integrity defects;
2. method, theory, or protocol defects;
3. experimental-design defects;
4. statistical-analysis defects;
5. claim and interpretation defects;
6. missing robustness, ablation, or cost evidence;
7. table and figure regeneration;
8. section restructuring;
9. citation corrections;
10. language and style;
11. journal formatting and production; and
12. final cross-format rebuild and package validation.

Do not polish prose around a claim that may later be removed.

#### Revision roadmap schema

Record the dependency-aware correction program in `revision_roadmap.md` with one entry per work item, using the canonical Appendix A.8 schema:

```text
work_item_id
source_ticket_ids
root_cause
required_action
scientific_or_editorial
owner_role
dependencies
required_inputs
artifacts_to_change
artifacts_to_regenerate
verification_command_or_method
completion_criterion
priority
status
```

#### Response-to-reviewers seed

For every ticket prepare, using the canonical Appendix A.9 schema:

```text
reviewer_or_ticket_id
concern
response_position: agree / partly_agree / disagree_with_evidence
analysis_or_evidence_reviewed
action_taken
exact_manuscript_change
new_analysis_or_experiment
verification_result
reason_if_not_implemented
status
```

Responses must be factual, courteous, and demonstrably reflected in all final formats.

#### Post-revision verification

After revision:

1. compare manuscript versions and generate a change log;
2. verify each ticket against its post-revision test;
3. rerun every affected analysis and generator;
4. verify no new unsupported claim appeared;
5. verify numbers and citations were not altered by style editing;
6. rerun section, exhibit, compliance, and cross-format checks;
7. rerun affected reviewer lenses;
8. perform regression review on dependent sections, abstract, conclusion, highlights, and cover letter;
9. mark each ticket resolved only with evidence; and
10. recompute gates and readiness score.

Record the ticket-by-ticket recheck and regression status in `post_revision_verification.csv`.

#### Final gate

`Gate Q — Post-Revision Verification` passes only when all critical and major tickets are resolved, every affected artifact is regenerated and validated, and no regression remains.


---

## 9. Domain-adaptive review modules

Apply the universal workflow above to every manuscript. Then activate every domain module relevant to the work. A multidisciplinary paper may require several modules.

### 9.1 Module A — Evolutionary computation, metaheuristics, and stochastic optimization

This module is mandatory for manuscripts concerning evolutionary computation, swarm intelligence, GSK-family methods, differential evolution, metaheuristics, continuous optimization, CEC benchmarks, or related stochastic optimizers.

#### A.1 Algorithm identity and contribution

Verify:

- exact algorithm name and version;
- inherited baseline mechanics;
- modified mechanisms;
- newly proposed mechanisms;
- whether the novelty is a mechanism, integration, parameter schedule, diagnostic, analysis, or merely a name;
- closest family and non-family methods;
- complete configuration of the reported final method;
- whether all active components are acknowledged;
- whether any supposedly proposed mechanism is dormant in the evaluated code;
- whether component rationale was specified before observing results; and
- whether the manuscript’s contribution bullets match the frozen implementation.

#### A.2 Benchmark protocol

For each suite × algorithm × dimension or problem cell verify:

- exact benchmark suite and implementation;
- function/problem inclusion and exclusion;
- dimension set;
- bounds and known optima;
- objective/error definition;
- number of independent runs;
- seed formula and schedule;
- initialization;
- boundary repair;
- stopping rule and MaxFES;
- objective-call accounting for every local-search or polish step;
- failure and timeout handling;
- numerical floor;
- floating-point environment or sentinel when relevant;
- evaluator hashes or version;
- convergence checkpoint definition; and
- immutable source path.

#### A.3 Comparator panel

Challenge:

- whether a same-family panel is presented as field-wide evidence;
- whether strong contemporary non-family optimizers are absent;
- whether imported and local implementations are mixed;
- whether MATLAB, Python, C/C++, or external-solver results are compared fairly;
- whether local search or hybrid methods receive equal objective budgets;
- whether tuning budgets are comparable;
- whether canonical implementations and parameter files are used; and
- whether a comparator with different numerical behavior is transparently qualified.

#### A.4 Descriptive and inferential reporting

Require, where the protocol supports them:

- best, median, mean, worst, SD, IQR, failure count, and n;
- clearly defined win/tie/loss counts;
- per-dimension or per-suite ranks;
- valid task-level omnibus comparison;
- paired post-hoc comparisons only when pairing is real;
- family-wise multiplicity control;
- effect sizes and uncertainty intervals;
- exact function denominator;
- robustness to mean versus median and error-floor choices; and
- disclosure of functions or dimensions where the proposed method is weak.

#### A.5 Convergence evidence

Verify:

- identical evaluation coordinates;
- same aggregation for all algorithms;
- all runs or a preregistered representative-run rule;
- uncertainty bands or a justified omission;
- no favorable cherry-picking;
- at least one difficult or adverse case;
- no smoothing that changes behavior;
- log-scale zero treatment;
- fixed algorithm order and style map; and
- complete supplementary grids when central claims depend on convergence.

#### A.6 Complexity and cost

Require separation among:

- objective-evaluation budget;
- algorithmic overhead;
- asymptotic time complexity;
- amortized complexity by cadence;
- persistent and temporary memory;
- wall time under a comparable environment;
- solver or language overhead; and
- optional instrumentation overhead.

Reject “free,” “negligible,” or “efficient” unless directly measured and scoped.

#### A.7 Ablation and mechanism claims

Verify the final algorithm is frozen before ablation. Require direct tests of the specific claimed mechanism rather than inferring its effect from bundled configurations; for DT-GSK manuscripts the load-bearing example is the SGSM (Success-Graph Structural Memory) interaction-structure memory — see section 10.6. Do not infer one component’s effect from a matrix in which the component is disabled in all cells. Distinguish conditional remove-one, isolated add-one, order-conditional incremental, and interaction effects.

#### A.8 Benchmark overfitting and development leakage

Ask:

- Which suites or functions influenced design, debugging, parameter selection, stopping rules, or manuscript emphasis?
- Is any suite incorrectly called a holdout or independent confirmation?
- Are difficult or weak cases visible?
- Does performance depend on a small subset of functions?
- Do leave-one-function-out ranks or influence checks change conclusions?
- Is a secondary suite genuinely external or only additional evidence?

#### A.9 Optimization-specific hard failures

Classify as critical or major, as appropriate:

- uncounted objective evaluations;
- invalid function exclusions;
- fabricated or reconstructed run values;
- ranks computed from rounded values;
- paired tests without valid pairing;
- pooling repeated runs as independent benchmark tasks;
- silent failed-run removal;
- mixed or unequal budgets;
- mechanism claims from inadequate ablation;
- field-wide superiority from a same-family panel; or
- use of staging output as publication evidence when the protocol prohibits it.

### 9.2 Module B — Machine learning, data science, and predictive modeling

Activate when the manuscript trains, validates, or compares predictive models.

Verify:

- dataset provenance, licensing, consent, and representativeness;
- train/validation/test separation;
- leakage through preprocessing, feature selection, normalization, tuning, or repeated test-set access;
- subject/site/time-level splitting where required;
- class imbalance and metric choice;
- baseline strength and hyperparameter tuning parity;
- nested cross-validation when appropriate;
- random seeds and repeated splits;
- calibration, discrimination, error analysis, and subgroup performance;
- uncertainty and statistical comparison across valid units;
- external validation;
- distribution shift and domain limitations;
- fairness, bias, privacy, and harm analysis;
- model-card or data-sheet completeness;
- computational cost and environmental reporting where material;
- prompt, model, API, checkpoint, and decoding versions for generative-AI studies; and
- reproducibility constraints caused by closed models or changing APIs.

Reject claims of general intelligence, clinical utility, fairness, interpretability, or causality without direct evidence.

### 9.3 Module C — Empirical software engineering and systems research

Verify:

- research questions and operational definitions;
- repository/project/sample selection;
- mining and filtering rules;
- construct validity of metrics;
- independence among commits, files, projects, developers, or repeated measurements;
- benchmark representativeness;
- baseline tools and versions;
- hardware, workload, compiler, operating system, and configuration;
- warm-up and repetition policy;
- performance variance and confidence intervals;
- flaky tests, failed builds, and missing projects;
- data leakage through benchmark design;
- qualitative coding protocol and inter-rater reliability when applicable;
- open artifact and executable container; and
- threats to internal, construct, conclusion, and external validity.

### 9.4 Module D — Mathematical, theoretical, or proof-centered manuscripts

Verify:

- novelty and relation to the strongest known results available in the permitted literature;
- definitions are non-circular and complete;
- assumptions are minimal and consistently used;
- theorem statements match proofs;
- lemmas are sufficient;
- edge cases and counterexamples are considered;
- constants, asymptotic regimes, and quantifiers are correct;
- computational experiments do not substitute for proof;
- proof sketches are labeled and complete enough for their role;
- notation is stable;
- examples illustrate rather than establish the theorem; and
- claimed generality does not exceed assumptions.

Attempt to construct counterexamples and test boundary cases.

### 9.5 Module E — Applied, clinical, human-subject, or real-world evaluation

Verify:

- population and setting;
- inclusion/exclusion criteria;
- ethics approval and consent;
- prospective versus retrospective design;
- power/sample-size rationale;
- randomization, blinding, and control conditions;
- missing data and attrition;
- confounding and causal-identification assumptions;
- clinically or practically meaningful endpoints;
- subgroup and fairness considerations;
- preregistration and protocol deviations;
- safety and adverse events;
- generalizability; and
- reporting guideline compliance.

Do not allow benchmark performance to be described as demonstrated real-world benefit without a real-world design.

---

## 10. Mandatory DT-GSK evidence-locked project profile

Activate this profile when reviewing a manuscript produced under the supplied **DT-GSK — Evidence-Locked Q1 Publication Production Framework** or an equivalent project contract. These controls are not optional stylistic preferences; they are inherited review requirements.

### 10.1 Governing-source compliance

The review MUST extract and audit every operative requirement from the governing build prompt. The manuscript must not be declared compliant merely because it appears polished. Create a line- or requirement-level compliance matrix and identify every superseded, unmet, partially met, or blocked requirement.

Verify build-gate, exemplar, and presentation-conventions compliance from the intake `GOVERNANCE_AND_GATE_ARTIFACTS` package (the producing project’s governance directory: phase-gate register, project configuration, presentation-conventions specification, evidence cards, claims matrix, and reproducibility manifest; no external-gate mapping exists in this project — its absence is expected, not an intake gap). When that package is absent, apply the missing-input behavior of section 1.3. Exemplar parity against the presentation-conventions specification and the three presentation exemplars (`mohamed2020gaining`, `jawad2024egsk`, `alfadli2025atmals`) is verified at Stage 14.16 across the registered 22-dimension comparative review; every unjustified deviation is a ticket.

Bind the generic section 1.1 review variables to the producing project’s concrete artifacts. These bindings are mandatory for this profile; Stage 0 and Stage 3 MUST validate these existing artifacts rather than create parallel ones:

| Section 1.1 variable | DT-GSK artifact binding |
|---|---|
| `GOVERNANCE_AND_GATE_ARTIFACTS` | `papers/governance/` — `project_configuration.md`, `claims_evidence_matrix.csv`, `reference_inventory.csv`, `evidence_cards/`, `phase_gate_register.csv`, `reproducibility_manifest.json`, `statistical_analysis_plan.md` (at `papers/build_prompt_phases/phase_05/`), `exhibit_plan.csv` (at `papers/build_prompt_phases/phase_04/`), `artifact_binding.csv`, `cross_format_consistency.csv`, `word_validation_report.md`, `requirements_traceability_matrix.csv`, `presentation_conventions.md`, and the external-gate mapping |
| `RAW_OR_IMMUTABLE_EVIDENCE_ROOT` | the selected immutable release inside `benchmarks/cec_reference_results/` (section 10.3) |
| `DERIVED_ANALYSIS_BUNDLE` | `papers/analysis/<release_id>/` (including `primary_stats/statistical_results.csv`) — the only admissible controlled analysis area; `results/` and `results/_run_all/` are staging and are never admissible |
| `STATISTICAL_ANALYSIS_PLAN` | `papers/build_prompt_phases/phase_05/statistical_analysis_plan.md` (the frozen plan) |
| `CLAIM_EVIDENCE_MATRIX` | `papers/governance/claims_evidence_matrix.csv` |
| `REFERENCE_LIBRARY_OR_CLOSED_CORPUS` | `references.bib` plus `reference_papers/<bibkey>.pdf`, `papers/governance/reference_inventory.csv`, and the evidence cards |
| `REPRODUCIBILITY_PACKAGE` | `papers/governance/reproducibility_manifest.json` plus release checksums and rebuild records |

Audit the governance artifacts themselves for existence, completeness, and internal consistency, at minimum:

- every publishable claim has a `claims_evidence_matrix.csv` row that resolves to corpus or evidence sources;
- `phase_gate_register.csv` records a `PASS` row with evidence for every build-framework gate (Gates 0–12); review `Gate A — Package integrity` MUST NOT pass while any build-gate row is missing or unevidenced; and
- `reproducibility_manifest.json` agrees with the release checksums recorded under section 10.3.

The review’s `requirements_compliance_matrix.csv` MAY be seeded from the existing `papers/review_2026_07_22/requirements_compliance_matrix.csv`; treat `papers/governance/requirements_traceability_matrix.csv` as a HISTORICAL register only (its line anchors are stale per `asset_map.md`), never as current state; seeding from it (and `source_line_traceability.csv` where present) after independent spot-verification of a sample of rows; seeding never substitutes for the audit.

### 10.2 Literature boundary

When the project uses a closed literature corpus:

- scientific citations MUST come only from the verified intersection of the bibliography and readable approved local sources;
- missing metadata MUST NOT be completed from memory or the web;
- expected bibliography size does not require every source to be cited;
- decorative citations and `\\nocite{*}` are prohibited;
- every citation occurrence must have a defensible semantic role; and
- novelty claims must be bounded to the reviewed corpus unless the governing evidence permits a broader statement.

A used citation without a verified local source is a critical compliance failure.

### 10.3 Empirical evidence lock

For publishable empirical claims:

- every empirical input MUST resolve under the selected immutable release inside `benchmarks/cec_reference_results/`;
- no publication analysis may silently fall back to `results/`, `results/_run_all/`, prior tables, figures, or manuscript prose;
- source release ID and checksums must be recorded;
- raw evidence must not be edited in place;
- corrected evidence requires a new versioned release and supersession record;
- source-use logs must prove the evidence boundary; and
- tables, plots, and prose must be regenerated from authoritative analysis outputs.

Any headline result sourced outside the permitted immutable release is critical.

Verify also the project’s determinism contract: `papers/governance/reproducibility_manifest.json` MUST exist and record the achieved reproducibility level per artifact class against the build framework’s three delivery levels (analytical / visual / byte-for-byte after timestamp normalization), and a double rebuild from the immutable release MUST achieve analytical reproducibility everywhere, visual reproducibility for all exhibits, and byte-for-byte reproducibility where timestamp normalization applies (see the Stage 12 determinism-contract audit). The project taxonomy supersedes the generic Stage 12 level names for compliance purposes.

### 10.4 Expected study scope and protocol checks

Verify rather than assume the exact final protocol, including the expected seven-method GSK-family panel:

```text
gsk
agsk
apgsk
fdb-agsk
atmals-gsk
eGSK / egsk as required by implementation labels
dt-gsk
```

Audit, when retained in the final protocol:

- CEC2017 function scope, F2 exclusion rule, D10/D30/D50/D100, and 51 runs;
- CEC2011 native-problem scope and 25 runs;
- CEC2013 function scope, D10/D30/D50, and 51 runs;
- seed policy and exact schedule;
- MaxFES and all local-search/polish objective calls;
- floating-point sentinel and environment consistency;
- comparator implementation provenance, especially eGSK solver differences;
- exact per-run row counts and uniqueness; and
- whether CEC2020 or CEC2013-LSGO is context-only rather than a formal seven-method panel.

Do not force expected values when verified evidence differs. Record the discrepancy and adjust scope.

### 10.5 Same-family claim boundary

The seven-method panel supports controlled GSK-family conclusions. It does not by itself establish field-wide or state-of-the-art superiority. Any broader claim requires an adequate, fair, contemporary non-family panel or must be removed.

### 10.6 Method and implementation correspondence

Verify the final evaluated DT-GSK profile and every active mechanism, including actual equivalents of:

- inherited GSK junior/senior phases;
- ACE knowledge control;
- nonlinear population-size reduction;
- budget-safe or stagnation escape;
- acceptance-gated pool pruning or archive logic;
- SGSM interaction-structure memory;
- linkage-aware block crossover;
- eigenframe or related final search;
- local search and Nelder–Mead endgame;
- final polish;
- deep-stall restart; and
- all cadence, gates, archives, safeguards, and termination logic.

For each mechanism verify existence, status, exact behavior, parameters, purpose, cost, and direct test. If code and prose disagree, the frozen evaluated code governs the reported experiments, and the manuscript must be corrected.

For every titular or load-bearing update rule (the SGSM interaction-graph exponential moving average is the DT-GSK exemplar), the review MUST read the frozen source and recompute the rule symbolically before accepting the printed equation: confirm which operand carries the retention/decay factor, whether a distinct learning rate is present, and that no two parameters were collapsed. The R1 review found the printed EMA `G←(1−λ)G+λΣ` contradicted `interaction_graph.py`, which applies `matrix*=decay; matrix+=lr*agg` — that is, `G←λG+ηΣ` with retention λ on the *old* graph and an independent learning rate η. Such a mismatch MUST be corrected consistently in the equation, the pseudocode step, the prose, and the parameter table, and MUST be cross-checked against Gate M wherever a mechanism figure draws the rule.

### 10.7 Statistics profile

Verify the final frozen analysis plan and at least:

- exact primary endpoint and numerical floor;
- function/task versus run-level units;
- valid pairing key;
- Friedman and any Iman–Davenport refinement when preregistered;
- Nemenyi display validity;
- Wilcoxon signed-rank validity and zero/tie treatment;
- Holm correction families;
- effect-size definition and direction, with the frozen plan naming which measures are reported (per D-0017 the tabulated effect size is the matched-pairs rank-biserial r, with A12 retained as a descriptive companion; Cliff’s delta only where sanctioned), interpretation thresholds pre-specified in the frozen analysis plan before analysis, and qualitative effect labels matching the frozen thresholds;
- seeded BCa or other interval design;
- exact function denominators;
- rank calculations from unrounded values;
- robustness to summary and floor choices; and
- a machine-readable row for every reported statistic (Appendix A.7 schema).

**Advanced dispositions the review must specifically verify (deep detail).** These recur in multi-algorithm benchmark manuscripts and are frequent silent-error sites:

- **Descriptive overall-rank versus pooled test.** An "overall" rank aggregated across dimensions or suites must be presented as a **descriptive mean of per-cell ranks**, not as the output of a single pooled omnibus test, unless a pooled block design is genuinely preregistered and valid. Flag any prose that attaches an Iman–Davenport or Friedman statistic to an overall row that is actually an unweighted mean of per-dimension ranks.
- **Per-run-gap disposition.** When a comparator's per-run data is missing for some cells (a real provenance defect), verify the plan pre-specifies the fallback: **function-level tests on per-function means** for those cells, with all per-run-dependent quantities (run-level Wilcoxon, A12/Cliff's delta, BCa) marked **disclosed-unavailable and never imputed**. A companion **matched-pairs rank-biserial correlation** derived from the same across-function Wilcoxon is the sanctioned effect size where per-run data is absent. (Per D-0017 the matched-pairs rank-biserial r is now the tabulated effect size study-wide, not only in per-run-gap cells; this gap-cell disposition remains valid for its scope.) Reject any silent imputation, substitution, or quiet dropping of the affected comparator.
- **Recovery-versus-comparability disposition (post-freeze data recovery).** When a comparator's previously missing cells are **recovered after the freeze**, the review MUST separate two kinds of quantity. **Seed-deterministic** quantities — final error, per-function means, ranks, Wilcoxon outcomes, A12/Cliff's delta, and BCa intervals computed from a deterministically re-derivable pipeline on the recovered per-run values — are **validly available**: every manuscript statement that still says these "do not exist," are "disclosed-unavailable," or "exist only at dimension/scope X" is now a **false existence claim** and MUST be corrected (Major). A **non-deterministic wall-clock runtime** obtained from a **separate post-freeze re-run** is NOT comparable to the frozen campaign's timings (different machine state, load, and scheduling) and legitimately **stays disclosed-unavailable**; labeling it "comparable" is itself a Major integrity-of-comparison defect. The review MUST verify the manuscript draws this line correctly — updating the recoverable seed-deterministic claims while keeping the runtime disclosed-unavailable — and MUST NOT conflate the two in either direction (neither suppressing valid recovered inference nor smuggling non-comparable runtime into a comparison). A one-line change-request footnote recording the recovery and its scope is the sanctioned disclosure; the recovered cells' permitted claim wording is not thereby upgraded.
- **Deterministic interval seeding.** The BCa (or other bootstrap) interval must use a **single, explicitly-constructed deterministic seed** (e.g., an entropy-list `SeedSequence` keyed by suite/dimension/function/comparator), a stated resample count, and the correct resampling unit (paired runs within function). Two contradictory seed constructions in the frozen artifacts, or an unseeded bootstrap, is a reproducibility defect.
- **Multiplicity-family hygiene.** Holm must be the primary correction within each explicitly-enumerated family; Benjamini–Hochberg may appear **only** as a separately-labeled exploratory analysis. Flag mixed correction families and any family whose size is not stated.
- **Robustness-divergence disclosure.** Where a preregistered robustness check (mean-versus-median re-ranking, floor sensitivity, leave-one-function-out, disputed-cell exclusion) **changes the ordering**, the divergence must be disclosed and the affected main-text rank claim qualified. Silent suppression of a robustness reversal is a major integrity ticket.
- **Loss-visibility parity.** Every unfavorable inferential cell material to a headline (a Holm-significant loss to a comparator, a win/tie/loss deficit despite a favorable mean rank, a non-separable critical-difference outcome) must be stated **alongside** — not after — the favorable cells it qualifies.
- **Runtime-table final state (project-specific; RT-001 CLOSED — §1.5.0-C(d)/§1.5.0-D).** The single-environment refresh was ATTEMPTED and abandoned on evidence: the six-comparator re-timing (`scripts/retime_comparators.py`) FAILED the determinism gate with 3,772 diffs, and Decision 7 Option 3 narrowed `tab:runtime` to a **DT-GSK-only, single-session** table instead. The review MUST verify: (i) the table and caption present DT-GSK's own cost only; (ii) the body states that **no comparator wall-clock is reported anywhere** and why (SE-044); (iii) pointers target §S6.5 with measurement provenance in §S6.7; (iv) the published ISM overheads (+57.3% CEC2017 D50 / +36.3% D100 / +30.3% CEC2013 D50) match §S6.5. Do NOT request a re-timing, do NOT flag the DT-GSK-only scope as a missing experiment (it is a recorded governance decision), and treat any prose implying a cross-algorithm runtime comparison as a defect. The general recovery-versus-comparability disposition above stands.

### 10.8 Convergence profile

> **House style (2026-07-23, §1.5.0-E governs).** These figures use the shared
> `_fig_style.py` design: Palatino serif, hairline solid grid, no in-figure title,
> thinned lines (comparators 1.1 pt / alpha 0.85, DT-GSK 1.65 pt opaque), and the
> uniform `_tune_log_yticks` log-y tick policy. Review legibility and data fidelity,
> not the deliberate serif-font / no-box / quiet-grid styling.

When the governing prompt requires seven-algorithm family overlays:

- every panel must contain one curve per algorithm or an explicit caption-level absence note;
- all algorithms must use the same checkpoint aggregation;
- the aggregation must be the preregistered statistic — by default the per-checkpoint mean error across all runs from the release’s `CheckpointErrors` logs, or the preregistered median+IQR alternative applied uniformly to every algorithm in the panel; aggregation bases must never be mixed within a panel without disclosure;
- any representative-run fallback (from `curves/`) is permitted only when an algorithm’s checkpoint logs are absent from the release and must be disclosed in the caption;
- main-text panel selection must follow the preregistered summary-statistic-derived selection rule, which governs which panels appear in the main text, not how curves are computed;
- one difficult or adverse case must be visible;
- complete per-function grids must appear in the supplement as required;
- algorithm order and style mapping must remain fixed; and
- missing curves must never be interpolated or silently omitted.

### 10.9 Main-manuscript ablation prohibition

The main manuscript, abstract, highlights and graphical abstract where the venue solicits them (MDPI Algorithms solicits neither — HL-01 NOT_APPLICABLE), conclusion, and cover letter MUST NOT contain ablation tables, figures, numerical results, p-values, effect sizes, ranks, or detailed component-effect conclusions when the governing project requires ablation to remain supplementary.

A neutral sentence directing readers to the supplementary ablation study MAY appear only when permitted by the target journal and the project’s final correction protocol. It must not state a result.

Any leaked ablation result in the main manuscript is a hard compliance failure.

**Leak test (exact).** Read every main-text, abstract, highlights, graphical-abstract, conclusion, and cover-letter sentence that touches a component or mechanism and ask: *does removing all knowledge of the ablation change whether this sentence is true or supported?* If yes, the sentence encodes an ablation result and violates this control — even when it prints no number. The failure mode the R1 review caught was a sentence framed as a neutral pointer that in fact stated a **null**: "a direct isolation … did not confirm a standalone benefit." A stated null, negative, or efficacy-implying outcome ("confirms the intended role of …", "isolating X improves …") is a leak; so is a cross-reference to a supplementary study the supplement itself does not contain.

**Result-free-deferral remedy.** The only compliant main-text treatment of a governed-supplementary component study is a **result-free deferral**: restate any efficacy-implying clause as neutral co-activation within its bundled tier, remove the outcome, and point to the Supplement **without** stating or implying the direction of the finding — no "did/did not confirm," no "improves/does not improve," no p-value, rank, or effect. The pointer's existence claim MUST match the supplement: do not cite an isolation study the supplement marks "in progress / not reported." A favorable ablation result is subject to the identical prohibition — the narrowing is symmetric and MUST NOT be used to back-port a favorable outcome into the main text (section 10.10).

> **NARROWED for this manuscript (author decisions 2026-07-14 → 2026-07-18; §1.5.0-B governs).**
> This prohibition is **narrowed to favorable component results only.** The ISM
> isolation **null** (Supplement §S6.5) is **deliberately advertised** — as of the
> 2026-07-22/23 remediation it is stated in several reader-facing places (abstract,
> introduction, conclusions, and the limitations material), all framed as a
> **failure to detect** with the absence of an equivalence bound stated explicitly
> (SE-021) — and this is **NOT** a §10.9 compliance failure. Review the framing's
> consistency across those places, not the count of mentions.
> Rationale under §1.4 precedence: §10.9 exists to stop a *favorable* component result
> being back-ported to inflate the contribution; disclosing a null moves in the
> opposite direction, and suppressing it would itself breach the governing law
> ("no presentation choice may conceal a material limitation").
>
> **What remains fully in force:** the prohibition binds for any *favorable* or
> efficacy-implying component result — including the Holm-significant final-polish
> effect, which MUST stay supplementary — and every main-text sentence touching the
> null MUST stay scoped to the evidence (§S6.5).
>
> **Removed content:** the former oracle / estimator-fidelity study is **deleted
> from the paper** (§1.5.0-B(d)); the title no longer names the null; "oracle" occurs
> **0 times** in both shipped PDFs. The §S6.7 NUMBER has since been REUSED for
> "Implementation Caveats: Two Corrected Defects and Their Evidence Trail" — a live
> §S6.7 reference is therefore CORRECT, not dangling. Only a reference to oracle
> CONTENT (estimator-fidelity tables, `tab:oracle-*`, "orc-rel") is a
> dangling-reference defect.
>
> **Reviewers: do NOT re-raise the (brief) advertised null as a §10.9 leak.** Report it
> only if a main-text sentence overstates it (asserts a *proven* or *favorable* ISM
> effect), which remains a defect.

### 10.10 Final ablation profile

Verify that ablation:

- began only after the algorithm, primary study, statistics, manuscript, PDF, and Word versions were frozen;
- used the identical frozen implementation;
- held seeds, functions, dimensions, runs, budgets, environment, and failure policy identical across all ablation cells per the preregistered ablation protocol (expected for the CURRENT 51-run re-mint: scaffold CEC2017 D10/D30/D50/D100 at n=51, overlay CEC2017 D50/D100 + CEC2013 D50 at n=51 — matching the primary study's power; the superseded pre-fix releases used n=25, which frozen historical companion docs may still quote — historical text, no open ticket);
- validated toggle isolation;
- separated scaffold remove-one, direct SGSM, isolated add-one, cumulative, and targeted interaction questions;
- reported performance, objective calls, runtime, uncertainty, convergence, and sensitivity as available;
- retained negative/null results;
- promoted validated raw output to a versioned immutable release before final analysis;
- analyzed only the promoted release, not staging; and
- used cautious identifiability language.

Ablation evidence may require a text-only narrowing of a main-manuscript rationale, but it must not be used to redesign the frozen algorithm or insert detailed ablation results into the main paper.

### 10.11 Exhibit and source-binding profile

Verify:

- no data-backed number is hand-edited;
- no exhibit is the source of another exhibit’s numerical values;
- table generators read only the controlled analysis area `papers/analysis/<release_id>/` recorded in `project_configuration.md`, never staging (`results/`, `results/_run_all/`) or prior exhibits;
- convergence generators implement the required panel design;
- all figures and tables have source paths, commands, release IDs, and checksums;
- T17–T20 or other numbering gaps are not filled merely for appearance;
- parameter sensitivity is not generated from unpromoted staging data; and
- conceptual diagrams do not imply unverified empirical behavior.

### 10.12 Dual-format profile

When the project requires PDF and Word:

- the manuscript must have one canonical semantic source;
- LaTeX/PDF and Word must agree on all scientific content;
- Word equations must be native OMML;
- Word tables must be native editable tables;
- numbering and cross-references must use working fields when required;
- citations and bibliography must be updateable when required;
- TOC and lists must update;
- Word must open-save-reopen without repair;
- no equation or table may be rasterized;
- cross-format validation must cover values, equations, labels, captions, citations, and declarations; and
- the Word document must reproduce the LaTeX PDF's typography (body font family and size, justified alignment, page geometry and margins, and heading/title/caption styles) per the Stage 17 T1–T5 DOCX-to-PDF parity procedure — except deviations recorded and approved in `papers/governance/production_deviation_record.md` (currently D-4: Word text measure 9.0% wider than the LaTeX class); verify the record rather than ticketing the deviation, so that a Word `Save As PDF` export is visually consistent with the LaTeX PDF — allowing only the unavoidable engine differences (line breaks, hyphenation, pagination within ~±1–2 pages, and non-identical native-OMML math rendering).

Exception: a journal-approved static-field fallback satisfies the working-fields and updateable-citations requirements only when the journal’s approval is documented and the fallback is recorded as a deviation in `papers/governance/word_validation_report.md`; verify that record rather than failing `Gate P` (mirrored in the Stage 17 Word/OOXML checklist).

### 10.13 DT-GSK hard rejection risks

Treat the following as high-probability Q1/Q2 rejection risks unless resolved:

- contribution framed as a bundle of modules without a clear scientific thesis;
- SGSM not sufficiently distinguished from differential grouping, covariance adaptation, or eigenvector operators;
- mechanism explanations based only on final performance;
- same-family panel overgeneralization;
- development leakage into CEC2013 or other claimed secondary evidence;
- unfair eGSK provenance or solver comparison;
- invalid pairing or pseudoreplication;
- inadequate effect-size and uncertainty reporting;
- missing non-objective overhead analysis;
- low-dimensional regressions hidden by aggregate ranks;
- unverified “high-dimensional,” “robust,” or “efficient” language;
- ablation design that cannot identify SGSM or dependent mechanisms;
- evidence fallback outside the immutable release;
- PDF/Word divergence; or
- language polish that masks, rather than resolves, evidential weakness.

### 10.14 Page-limit hard rule

Verify the build framework’s hard page-limit rule (build Section 1.5):

- the main manuscript does not exceed the limit in the Phase 4 verified journal record or, when the journal publishes no hard limit, the journal’s typical accepted article length;
- page counts are measured from the compiled PDF at the Phase 8/9/11 gates, with a page-count row recorded in `papers/governance/phase_gate_register.csv` for each of those gates;
- any overflow was resolved solely by migrating non-essential material to the supplement, never by shrinking figures below legibility, deleting required declarations, or compressing claims or prose; and
- the measured page-count evidence is recorded in the review record.

### 10.15 Presentation-conventions and exemplar-parity profile

Verify:

- `papers/governance/presentation_conventions.md` exists and records the structured comparative review of the three presentation exemplars — GSK (`mohamed2020gaining`), eGSK (`jawad2024egsk`), and ATMALS-GSK (`alfadli2025atmals`) — across the build framework’s registered 22 dimensions;
- the manuscript passes the section-by-section exemplar-parity editorial check against all three exemplars (executed at Stage 14.16), with every unjustified deviation from the register ticketed;
- the exemplars were used as calibration references only, never as content templates — no mechanical copying of text, structure, or claims;
- `jawad2024egsk` venue metadata follows the Phase 1 evidence card and is never invented or completed from memory; and
- the exemplar-parity check carries pass evidence in `papers/governance/phase_gate_register.csv`.

### 10.16 Team assignment for the DT-GSK profile

Map the section 10 controls to the review teams (section 3) so that each profile obligation has an accountable owner. This mapping creates no new controls; it assigns the existing ones and does not alter section 10.1–10.15.

| DT-GSK control | Owning team | Contributing team(s) |
|---|---|---|
| 10.1 Governing-source & governance-artifact audit | T7-VENUE | ECB, T3-STAT |
| 10.2 Closed-corpus literature boundary | T6-INTEG | T1-OPT |
| 10.3 Empirical evidence lock & determinism contract | T3-STAT | T2-BENCH, T4-SOFT |
| 10.4 Seven-method panel & protocol scope | T2-BENCH | T1-OPT |
| 10.5 Same-family claim boundary | T1-OPT | T7-VENUE |
| 10.6 Method/implementation correspondence (incl. SGSM) | T1-OPT | T4-SOFT |
| 10.7 Statistics profile & advanced dispositions | T3-STAT | T2-BENCH |
| 10.8 Convergence profile | T5-WRITE | T2-BENCH, T3-STAT |
| 10.9–10.10 Ablation prohibition & final ablation profile | T2-BENCH | T1-OPT, ECB |
| 10.11 Exhibit & source-binding profile | T5-WRITE | T3-STAT |
| 10.12 Dual-format profile | T4-SOFT | T7-VENUE |
| 10.13 DT-GSK hard rejection risks | ECB | all teams |
| 10.14 Page-limit hard rule | T7-VENUE | T5-WRITE |
| 10.15 Presentation-conventions & exemplar parity | T5-WRITE | ECB |

The arbitration council (section 3.6) reconciles any cross-team disagreement over a profile control before the corresponding review gate is set. The SGSM interaction-structure-memory identifiability question (section 10.6) is held jointly by T1-OPT (mechanism) and T2-BENCH (ablation design): neither may pass Gate F or Gate K over the other’s unresolved blocking dissent.

### 10.17 Human-authored presentation across every artifact

This control governs the **look and legibility of the whole paper**, not only its prose. It is owned by **T5-WRITE** (leads), with **T4-SOFT** co-owning the editability check and **ECB** arbitrating; it feeds Gates M (exhibit integrity) and N (writing/authorship integrity). It applies to Stages 13, 14, and 15.

**10.17.1 Human-authored requirement (all artifacts).** Every element a reader sees — prose, section architecture, figures, flowcharts, tables, the algorithm/pseudocode, and captions — MUST read as the work of a human expert, not as machine-generated output. The review MUST inspect each artifact and flag anything that reads as **AI-generated clutter**, including but not limited to:

- over-busy auto-generated diagrams — dense boxes/arrows/colour-coded rails/legends that a human author would have drawn as a simple flowchart or replaced with a clean table;
- `matplotlib`-styled "figure" grids that are really tables (coloured ON/OFF cells, plotted text) and MUST be rendered as ordinary tables;
- uniform templated prose: formulaic transitions, repeated sentence scaffolds, list-itis, hollow signposting, mechanical paragraph shapes;
- decorative complexity — visual busyness that adds no information.

The remedy is **simplification into clean, human-legible forms** (a plain table, a simple labelled flowchart, direct prose), **never** detector-evasion editing (section 15.5). Reviewers MUST distinguish legitimately formal, information-dense scientific writing and necessary technical detail from the machine-generated *look*: flag the clutter and the templated feel, not correct density. A false "this is AI" flag on sound expert writing is itself a review error.

**10.17.2 Pseudocode clarity (eye-friendly, row-based, hidden grid).** The main algorithm pseudocode MUST be clean, simple, and eye-friendly: numbered steps, consistent indentation, wrapped-line hanging that never collides with the margin, and logical phase grouping. It MAY be laid out as a **row-based** structure (an algorithmic-style numbered list or a stepwise table) with **grid/rule lines hidden or minimal** — booktabs-style top/mid/bottom rules only, no vertical rules and no full cell grid — so that no visual mess remains. A pseudocode block that overflows, collides, double-prints, or is otherwise hard to parse is a Stage-13 exhibit ticket even when its content is correct. A companion control-flow **flowchart** (kept simple: a handful of boxes and arrows, optionally a base-vs-proposed pair) SHOULD accompany a complex algorithm to aid comprehension.

**10.17.3 Native editability in the Word deliverable.** Where the project ships a Word (`.docx`) version, every **table** — and the step content of every schematic a reader or editor may need to change — MUST be a **native editable object** (a real `w:tbl`), not a flat rasterised image. Flowchart *diagrams* MAY ship as images, but their steps SHOULD also be available as a native editable table alongside. A table or figure-table that appears in Word only as a picture is a Gate-P (and Gate-M) ticket.

**10.17.4 No machine-generated identifiers, placeholders, or provenance artifacts in reader-facing text.** The manuscript MUST NOT expose, anywhere a reader sees it (body prose, captions, table cells, section headings, abstract, algorithm, appendices), the internal tokens of the build/evidence pipeline. The review MUST scan every rendered surface (PDF **and** Word, main **and** supplement) and flag, as a Gate-N/Gate-M ticket, each of the following — then require replacement with **natural, human-authored academic language**:

- **Raw build/release identifiers**: Git-style release tags and commit hashes, hash-suffixed release IDs (e.g. `rel-2026-07-10-262fc16c9`, `abl-rel-2026-07-11`, `-dirty` suffixes, 7–40-hex SHAs), pipeline/run IDs, and internal analysis-bundle directory paths (e.g. `papers/analysis/rel-.../cec2017/…`) used as reader-facing prose. A hash-suffixed tag repeated across the text reads unmistakably as machine output.
- **Mechanically repeated provenance stamps**: the *same* release/version string appended to every (or nearly every) figure and table caption. No human author stamps thirty captions with an identical build tag. Provenance MUST be stated **once**, in the appropriate place (the Methods/experimental-setup paragraph and/or the Data-Availability statement), in deliberate authored wording; the per-caption stamps MUST be removed or reduced to a natural phrase (e.g. "from the frozen benchmark results accompanying this article").
- **Placeholder / scaffold tokens**: `TODO`, `TBD`, `TK`, `XXX`, `FIXME`, `lorem ipsum`, `[cite]`, `\todo{…}`, dummy DOIs/URLs, all-zero ORCIDs (`0000-0000-0000-0000`), un-pinned "Author, Year" stand-ins, and any bracketed editorial note left in the text.
- **Internal engineering nouns leaking into prose**: internal profile/config names (e.g. a `pub` profile), dataclass/field names, function names presented as prose rather than as a deliberate reproducibility reference, exhibit/artifact registry codes (e.g. `T-PARAMS`, `AN-OMNI-…`, `E`-numbers off the printed equation number — see 10.17 and §13), and build-phase labels.
- **Over-templated machine cadence** already covered in 10.17.1 (formulaic transitions, repeated sentence scaffolds) — re-checked here as part of the same "does this read as authored?" pass.

**What is legitimate (do NOT flag):** a *single*, deliberately placed archival identifier — a Zenodo/OSF DOI, a repository URL, or one named frozen-release/commit reference — in the **Data-Availability / reproducibility statement**, where precision is expected and reads as authorship. The target is raw internal tags *scattered through prose and captions*, not the existence of one reproducibility pointer. As always (15.5) this is de-cluttering for authorship quality and reproducibility hygiene, **never** detection-evasion: the underlying data, release, and provenance remain fully recorded in the governance artifacts and cited once, precisely, in the manuscript.

The reviewer MUST enumerate every offending token with its file location and propose the exact natural-language replacement, and MUST verify after the fix that (a) no raw identifier remains in any reader-facing surface, (b) the provenance is still stated once and unambiguously, and (c) no number, claim, citation, or reproducibility pointer was weakened by the rewording.

**10.17.5 Whole-manuscript expert-authorship mandate.** The review MUST ensure that the *entire* manuscript meets the prose standard of experienced researchers writing in their own field. It MUST identify and eliminate the specific defects that fall short of that standard — templated cadence, hollow or inflated phrasing, redundant restatement, tonal seams, mechanical formatting, and leftover scaffolding — and MUST refine the language, transitions, and presentation to achieve a natural, fluent, publication-quality academic style — **while preserving the scientific content, technical accuracy, and the authors' intended meaning** (no fact, number, citation, claim, or scope may change; §§2.1, 15.5).

**The criterion is quality, not provenance.** This project discloses its use of generative-AI assistants in the manuscript's Use-of-Generative-AI statement, so the object of this control is never to make assisted writing appear unassisted, and no edit may be motivated by how a passage would score under an AI-text detector (`PAPER_BUILD_PROMPT.md` §0.3; §§15.5 and 18.4 here). Every defect enumerated below is a defect in wholly human-written prose too, and MUST be flagged on that ground alone — a reviewer who cannot name the language defect has not made a finding.

This is a **whole-document pass**, not a spot check: it applies to the title, abstract, keywords, every section, every caption, every table cell and algorithm line, the back matter, and the supplement, in **both** the PDF and the Word deliverable. Operationally, the reviewer MUST:

- **Read for a single human voice.** Flag tonal seams where the register shifts between paragraphs or sections (a symptom of text assembled from separately drafted passages, whoever or whatever drafted them), and require one consistent authorial voice throughout.
- **Break templated cadence.** Flag formulaic transitions and connective tics (*Moreover, Furthermore, Additionally, Notably, Importantly, It is worth noting, In conclusion, Overall*), repeated sentence scaffolds, uniform paragraph shapes (e.g. every paragraph opening with a topic sentence of identical form), and mechanical "First… Second… Third…" or "On the one hand… on the other hand…" laddering used as filler rather than genuine enumeration. Require varied, purposeful sentence and paragraph structure.
- **Cut hollow and inflated phrasing.** Flag empty intensifiers and clichés (*delve into, leverage, robust, seamless, plays a crucial/pivotal role, a rich tapestry, it is important to note, in today's world, paradigm shift*), throat-clearing preambles, and redundant restatement (the same point made twice in adjacent sentences or in both the intro and the body with no added information).
- **Remove near-duplicate content.** Flag boilerplate repeated across captions, repeated definitions, and sentences that paraphrase an adjacent sentence; consolidate to one clear statement.
- **Fix mechanical formatting tells.** Flag over-uniform bulleting/bolding, list-itis where prose is warranted, inconsistent hyphen/dash/quote styles, and any leftover scaffolding (bracketed notes, `TODO`/`TBD`, placeholder citations or ORCIDs, section stubs) — coordinating with §§10.17.1 and 10.17.4.
- **Naturalize transitions and flow.** Where paragraphs jump without a logical bridge, require substantive connective tissue that reflects the argument (cause, contrast, consequence), not a generic transition word.

The reviewer MUST propose concrete rewrites (before → after) for each flagged passage and MUST verify after revision that the prose still states exactly the same facts, numbers, and claims. **Guard against the opposite error:** legitimately formal, information-dense scientific writing, necessary technical detail, and genuine enumerated structure are NOT defects — flag the *named defect* (templated cadence, hollow phrasing, tonal seams, redundancy), not correct density or precise terminology. Flagging sound expert writing as defective — on a detector score, a hunch about provenance, or a stylistic preference — is itself a review error (§10.17.1). This mandate feeds **Gate N** (writing / authorship integrity) and is a Stage-15 deliverable; it is a de-cluttering-for-quality pass, **never** detection-evasion editing (§15.5).

**10.17.6 Algorithm, pseudocode, and flowchart presentation review.** The review MUST examine every algorithm, pseudocode listing, flowchart, and procedural diagram from **both** a technical and a visual-communication perspective, and MUST ensure each is scientifically accurate, publication-ready, and presented in a clear, consistent, reader-friendly way — matching the presentation standard of leading optimization papers (e.g. the original GSK paper), so a reader can grasp the algorithm flow at a glance without loss of technical precision.

- **Pseudocode legibility and structure.** The reviewer MUST rewrite (or ticket for rewrite) any pseudocode that is crowded, over-condensed, or hard to follow. The rewrite MUST: split complex statements into shorter, self-contained steps; limit each line to a single primary logical operation wherever practical; apply consistent indentation, spacing, alignment, and notation; group related operations into clearly labelled logical sections (e.g. initialisation / per-generation core / bookkeeping / finalisation); replace lengthy inline comments with short, meaningful step descriptions or a concise right-aligned note; and keep a visually balanced, uncluttered, eye-friendly layout with no dense text blocks and no horizontal crowding or line overflow. Numbering, symbols, and terminology MUST be consistent with the notation table, the equations, the prose, and the companion flowchart. This extends §10.17.2 and F.13.
- **Flowchart clarity.** The reviewer MUST ensure every flowchart is simple, clean, and uncluttered: remove redundant or decorative elements, use consistent shapes/symbols/terminology, keep the logical flow direct with no crossing or colliding arrows, and optimise the layout and sizing for readability (no overflow, no fill-colour clutter). Where a base-vs-proposed pair is shown, the two MUST use the same conventions so the differences read at a glance. This extends §10.17.1 and F.14.
- **Behaviour preservation.** Every such rewrite MUST preserve the exact algorithmic behaviour, step order (faithful to the code, §10.6), notation, and scientific content — it is a presentation improvement only; no step, condition, constant, or claim may change. Verify the rewritten listing/diagram still matches the code, the equations, the prose, and its companion exhibit, and re-render to confirm no overflow, collision, or double-print.

This control is owned by **T5-WRITE** (presentation) with **T1-OPT** co-owning the algorithmic-fidelity check; it feeds Gates **M** (exhibit integrity) and **N**, and applies to Stages 13–15.

**10.17.7 Visual-communication excellence for algorithms, pseudocode, and flowcharts.** The review MUST hold every algorithm, pseudocode listing, flowchart, and procedural diagram to an exceptional standard of visual communication, in addition to technical correctness:

- **Readability and layout.** Review every algorithm, pseudocode listing, flowchart, and procedural diagram not only for technical correctness but also for visual readability and communication quality. Ensure that each pseudocode listing is professionally formatted, visually balanced, and optimized for effortless reading. Eliminate crowded layouts, excessive text density, and inefficient use of page space by improving spacing, indentation, alignment, line breaks, and section organization. Make effective use of available whitespace to create an open, clean, and aesthetically balanced presentation while preserving publication efficiency. In particular, a listing that leaves large unused page regions while its text remains cramped MUST be re-balanced (e.g. wider line spacing, taller float placement) so it fills the available space in an open, uncrowded way; re-render to confirm the result is balanced and fits without overflow.
- **Decomposition and phase separation.** Break complex operations into smaller logical steps where appropriate, clearly separate major algorithm phases (for example with labelled section headers and blank-line separation between stages), and maintain consistent notation, formatting, and terminology throughout the manuscript. Every algorithm should be understandable at a glance without sacrificing technical precision or scientific accuracy.
- **Flowchart clarity.** Similarly, review all flowcharts to ensure they are simple, uncluttered, visually balanced, and easy to follow. Optimize node spacing, alignment, connector routing, and logical progression while removing unnecessary repetition and visual noise. Each figure should communicate the algorithm naturally and intuitively, following the presentation style of leading optimization papers.
- **Whole-manuscript visual standard.** Overall, ensure that the manuscript achieves an exceptional standard of visual communication, where algorithms, pseudocode, flowcharts, figures, tables, and all technical elements are not only scientifically rigorous but also highly readable, aesthetically polished, and suitable for publication in a top-tier Q1 journal.

Every re-balancing under this control is a presentation improvement only: no step, condition, constant, notation, or claim may change, and each rewritten listing/diagram MUST be re-rendered and re-verified against the code, the equations, the prose, and its companion exhibit (§10.17.6, §10.6). This control is owned by **T5-WRITE** with **T1-OPT** co-owning algorithmic fidelity; it feeds Gates **M** and **N**.

---

## 11. Quality gates and submission-readiness acceptance criteria

A high aggregate score cannot compensate for a failed hard gate. Record every gate as `PASS`, `FAIL`, `BLOCKED`, or `NOT APPLICABLE WITH JUSTIFICATION`.

| Gate | Name | Minimum acceptance criterion |
|---|---|---|
| A | Package integrity | one authoritative readable manuscript state; essential files present |
| B | Desk review | no unresolved likely desk-rejection defect |
| C | Claim integrity | every substantive claim supported and correctly scoped |
| D | Contribution merit | defensible significance and originality for the target |
| E | Literature/citation integrity | verified, semantically correct, balanced sources |
| F | Method/theory | correct, complete, internally consistent, reimplementable method |
| G | Evidence integrity | traceable, valid, immutable or controlled evidence |
| H | Study design/fairness | design answers RQs; controls and comparisons fair |
| I | Statistical validity | valid units, tests, corrections, effects, intervals |
| J | Result integrity | complete, consistent, non-selective reporting |
| K | Robustness/attribution | stable conclusions; adequate component and sensitivity logic |
| L | Reproducibility | central results and artifacts can be regenerated |
| M | Exhibit integrity | accurate, legible, honest, bound figures/tables/equations |
| N | Writing/authorship integrity | clear expert prose; no fact drift or detector gaming |
| O | Ethics/publication integrity | truthful approvals, authorship, declarations, availability |
| P | Journal/production compliance | current rules and cross-format package pass |
| Q | Post-revision verification | all critical/major issues closed with regression checks |

#### Gate-namespace crosswalk

Three gate namespaces coexist when the DT-GSK profile governs: review Gates A–Q (this section), the build framework’s phase Gates 0–12, and the externally specified Gates 1–14 mapped in the build framework’s Section 15.9. The build-framework anchors remain authoritative for build-side obligations; review Gates A–Q govern only this post-completion assessment. Cite gates with their namespace (for example, “build Gate 11”, never a bare “Gate 11”). Reconcile statuses with this crosswalk:

| Review gate | Build-framework gate(s) 0–12 | External gate(s) 1–14 |
|---|---|---|
| A Package integrity | 0, 12 | 14 |
| B Desk review | 4 | — |
| C Claim integrity | 4, 8 | 9 |
| D Contribution merit | 4 | 10 |
| E Literature/citation integrity | 1 | 1 |
| F Method/theory | 3 | 10 |
| G Evidence integrity | 2 | 2–4, 12 |
| H Study design/fairness | 2, 5 | 2 |
| I Statistical validity | 5, 6 | 5 |
| J Result integrity | 6, 7 | 6–8 |
| K Robustness/attribution | 11, 12 | 10–11 |
| L Reproducibility | 12 | 13 |
| M Exhibit integrity | 7 | 6–8 |
| N Writing/authorship integrity | 8, 10 | 11 |
| O Ethics/publication integrity | 10, 12 | 14 |
| P Journal/production compliance | 9 | 14 |
| Q Post-revision verification | — (review-side only) | — |

Per section 10.1, every build-framework gate row in `phase_gate_register.csv` must carry pass evidence before review `Gate A` can pass.

### 11.1 Absolute blockers

The manuscript MUST NOT be classified as submission-ready when any of the following remains:

- an open critical or major ticket;
- an unsupported title, abstract, contribution, headline result, or conclusion claim;
- a material method or equation error;
- a result that cannot be traced to authoritative evidence;
- an invalid experimental unit, pairing design, or primary statistical test;
- undisclosed multiplicity or selective reporting;
- unfair comparator conditions affecting conclusions;
- missing essential experiment or control;
- unresolved data, ethics, plagiarism, or image-integrity concern;
- code/data availability statement known to be false;
- a central reproducibility failure;
- a broken or misleading primary figure/table;
- a governing-prompt violation;
- a journal-required format or declaration failure;
- PDF/Word scientific inconsistency; or
- prohibited detector-evasion editing.

### 11.2 Conditional acceptance of moderate issues

A moderate issue may remain only when:

- it does not affect validity, central interpretation, ethics, or journal compliance;
- the reason for deferral is documented;
- the residual risk is visible in the final report;
- EIC and the relevant specialist agree it is non-blocking; and
- the manuscript contains any required qualification.

### 11.3 Q1 readiness test

A `Q1-READY CANDIDATE` decision additionally requires:

- a clearly important problem and non-trivial contribution;
- strong distinction from the closest work;
- evidence breadth and depth proportionate to the claims;
- no weak or missing load-bearing analysis;
- rigorous statistical and robustness treatment;
- reproducibility beyond minimum code release;
- candid limitations and adverse results;
- presentation comparable to strong papers in the target field; and
- a reviewer-resilient answer to “why does this matter beyond incremental performance?”

### 11.4 Q2 readiness test

A `Q2-READY CANDIDATE` decision requires a meaningful, technically sound, reproducible contribution with adequate experiments, valid statistics, honest scope, and clean presentation, even when the conceptual advance is more incremental than the Q1 threshold.


---

## 12. Required final review report format

Return the review in the exact order below. Do not hide critical findings behind a long summary. Use exact section, page, paragraph, equation, table, figure, algorithm, line, claim, or artifact identifiers wherever available.

### 12.1 Review metadata and scope

Report:

```text
review_id
review_date
project_title
manuscript_version
target_journal
target_article_type
target_quartile_status
materials_reviewed
materials_missing
governing_protocol
scientific_scope
review_limitations
```

### 12.2 Executive editorial verdict

Provide a direct 300–600 word assessment covering:

- what the paper claims to contribute;
- the strongest verified contribution;
- the central scientific weakness;
- the strongest likely rejection reason;
- whether the current evidence supports the thesis;
- the amount of revision required;
- the internal disposition code; and
- whether Q1 or Q2 readiness is realistic after the specified corrections.

Do not use vague encouragement. State the decision first.

### 12.3 Submission-readiness dashboard

Provide a compact table:

| Category | Score /5 | Weight | Weighted score | Gate | Critical/Major count | Status | Evidence summary |
|---|---:|---:|---:|---|---:|---|---|

Fill the `Gate` column (and the `gate` field of Appendix A.3 rows) from this fixed category-to-gate mapping; a category owning several gates lists all its gate letters:

| Category (section 6.2) | Gate(s) |
|---|---|
| Journal fit and scientific significance | B, D |
| Novelty and contribution boundary | D |
| Theory, method, or algorithmic correctness | F |
| Experimental or study design | H |
| Statistical validity | I |
| Evidence and citation integrity | E, G |
| Results, discussion, and limitations | J |
| Robustness, sensitivity, and ablation logic | K |
| Reproducibility and open-science readiness | L |
| Writing, exhibits, and presentation | M, N |
| Ethics, journal compliance, and production package | O, P |

Gates A, C, and Q are cross-cutting with no single category owner; they are reported only in the 12.4 gate report.

Then state the total score and readiness band. Remind the reader that hard gates override the score.

### 12.4 Gate report

List Gates A–Q with:

```text
gate
status
evidence
blocking_tickets
minimum_action_to_pass
reviewer_signoff
```

Report the Stage 0 decision (`PASS` / `FAIL` / `BLOCKED`) as a preliminary row ahead of `Gate A`, using the same fields, so a Stage 0 failure (for example, a manuscript/results version mismatch) never drops out of the readiness record. Stage 14 has no gate of its own: its critical section-level findings block `Gate C` when they concern claim support, `Gate J` when they concern result reporting, and `Gate N` when they concern writing quality.

### 12.5 Verified strengths

List only strengths that are demonstrably supported. For each strength state why it matters for the target journal and the evidence that confirms it.

### 12.6 Top ten rejection risks

Rank by combined probability and impact. Each risk must include the likely reviewer or editor wording and the precise mitigation.

### 12.7 Critical and major issue register

Present critical and major tickets first, ordered by dependency and priority. Do not mix them with minor copyediting.

### 12.8 Full issue register

Include all tickets in machine-readable or clearly tabular form using the mandatory schema.

### 12.9 Claim audit and claims ceiling

Include:

- high-visibility claim table;
- unsupported or overbroad claims;
- accepted claims;
- claims requiring new evidence;
- claims to move to the supplement;
- claims to omit; and
- the strongest defensible abstract/conclusion statement.

### 12.10 Scientific review by stage

Summarize Stages 0–17, including method, experiments, statistics, robustness, reproducibility, exhibits, section quality, writing, ethics, and journal compliance.

Also summarize explicitly:

- which section 9 domain modules were activated and their findings; and
- section 10 profile compliance when the DT-GSK profile governs — including the evidence lock (10.3), the seven-method panel checks (10.4), the main-manuscript ablation prohibition (10.9), and the 10.1 requirement-level compliance matrix, with `requirements_compliance_matrix.csv` status counts (pass / fail / partial / blocked / not_applicable — matching the Stage-0 schema and the artifact as built).

### 12.11 Missing experiments and analyses

Separate, using this controlled classification vocabulary (used verbatim in Stage 19 step 5 and in the `classification` field of Appendix A.5):

- `essential_before_submission` — essential before submission;
- `recommended_for_q1` — strongly recommended for Q1;
- `useful_for_q2` — useful for Q2 strengthening;
- `optional_or_out_of_scope` — optional future work or explicitly out of scope.

For each, provide the minimum valid design and the claim it would support or refute.

### 12.12 Independent reviewer reports

Present EIC, AE, and R1–R6 reports separately, together with the recorded pre-consensus findings of the specialist roles (RI, RW, VIZ, PROD-PDF, PROD-WORD, REP, JCO) from their lead stages. Preserve disagreements. These reports and findings feed the Appendix D sign-off table.

### 12.13 Predicted reviewer questions and response preparation

Provide at least 25 tailored questions, ranked by likelihood and severity. For each question state what evidence or revision would constitute a convincing response.

### 12.14 Writing and language report

Include:

- overall clarity assessment;
- recurring formulaic patterns;
- terminology problems;
- highest-impact sentence/paragraph revisions;
- generic or promotional phrases to remove;
- passages that need factual verification before rewriting;
- style-only revision rules; and
- authorship/tool-disclosure note.

### 12.15 Revision roadmap

Provide a dependency-aware work plan grouped into:

1. scientific blockers;
2. analysis and experiment work;
3. claim and interpretation corrections;
4. exhibit regeneration;
5. structural revision;
6. language revision;
7. journal/production work; and
8. final validation.

Each item must identify ticket IDs, artifacts, verification method, and completion criterion.

### 12.16 Final internal recommendation

Use exactly one disposition code from Stage 19. State:

- present readiness;
- expected readiness after required corrections;
- whether the target journal remains appropriate;
- whether a Q1 or Q2 claim is justified only as an aspiration;
- residual uncertainties; and
- the exact conditions for changing the decision.

### 12.17 Post-revision verification checklist

End with a ticket-linked checklist that can be rerun on the revised manuscript. Do not end with general encouragement or a promise of future work.

---

## 13. Reviewer rubrics

### 13.1 EIC and AE rubric

Score:

- journal fit;
- importance;
- novelty plausibility;
- evidence maturity;
- breadth and depth;
- likely reviewer burden;
- ethical/compliance readiness;
- presentation maturity;
- realistic revision path; and
- risk of immediate rejection.

### 13.2 Domain-science rubric

Score:

- problem specificity;
- gap validity;
- contribution distinction;
- relation to closest work;
- scientific insight;
- baseline strength;
- scope discipline;
- adverse-result transparency;
- practical or theoretical meaning; and
- field relevance.

### 13.3 Theory/method rubric

Score:

- assumptions;
- formal correctness;
- notation;
- completeness;
- pseudocode/procedure;
- implementation correspondence;
- numerical safeguards;
- complexity;
- evaluation accounting; and
- reimplementability.

### 13.4 Experimental-design rubric

Score:

- research questions;
- controls;
- sample/task scope;
- comparator fairness;
- tuning fairness;
- randomization/pairing;
- failure handling;
- external validity;
- development leakage; and
- missing experiment risk.

### 13.5 Statistical rubric

Score:

- estimand;
- unit of analysis;
- independence;
- test validity;
- multiplicity;
- effect sizes;
- uncertainty;
- robustness;
- reproducibility; and
- interpretation.

### 13.6 Reproducibility rubric

Score:

- evidence release integrity;
- data/code availability;
- seeds and configurations;
- environment;
- commands;
- deterministic analysis;
- source bindings;
- clean rebuild;
- documentation; and
- future revision package.

### 13.7 Editorial and visual rubric

Score:

- narrative coherence;
- section balance;
- paragraph focus;
- terminology;
- natural scholarly voice;
- table quality;
- figure quality;
- caption completeness;
- accessibility; and
- journal presentation.

### 13.8 Research-integrity rubric

Score:

- source identity;
- semantic citations;
- data integrity;
- transparency of exclusions;
- authorship;
- ethics;
- conflicts/funding;
- image integrity;
- disclosure; and
- availability truthfulness.

---

## 14. Common rejection patterns the review must actively seek

Do not assume these defects exist. Actively test for them.

1. A narrow engineering modification presented as a broad conceptual advance.
2. A research gap created by ignoring the closest work.
3. Novelty based mainly on a new acronym.
4. An algorithm description that does not match the executed code.
5. Hidden objective evaluations or unequal computational budgets.
6. Comparator implementations with different quality or provenance.
7. Benchmark or test-set leakage through development and tuning.
8. Repeated runs treated as independent scientific tasks.
9. Statistical testing without a declared multiplicity family.
10. P-values reported without effects or uncertainty.
11. Aggregate wins hiding systematic losses in important subgroups or dimensions.
12. A selected convergence plot that is not representative.
13. Ablation that cannot isolate the claimed mechanism.
14. Parameter sensitivity described as causal component evidence.
15. Runtime claims across incompatible hardware, languages, or solvers.
16. Reproducibility statements unsupported by a usable package.
17. Literature claims stronger than the cited sources.
18. An abstract or conclusion stronger than the results section.
19. Limitations written as a formality rather than an analytical boundary.
20. Supplementary material used to hide contrary primary evidence.
21. Figures or tables regenerated from stale or rendered artifacts.
22. Word and PDF versions containing different scientific content.
23. Generic, repetitive prose masking an underdeveloped argument.
24. Journal instructions assumed from an old template.
25. Tool or generative-AI use not disclosed when the journal requires disclosure.
26. Generative-AI use under-disclosed relative to the actual extent of assistance, or disclosed inconsistently across the submission form, Methods, and Acknowledgments (D16.1, D16.5).
27. *(Out of scope this cycle — see §1.5.4.)* The family-only comparator panel / absence of external non-GSK baselines is a deliberate, disclosed scoping decision and MUST NOT be raised as a rejection-risk pattern in this review cycle. (Retained here only so the pattern is not re-derived from scratch; it is explicitly excluded, not active.)
28. A stated venue quartile that is stale, self-computed, or true on only one index while implied to hold generally (D17.1).
29. An "overall" rank presented as a pooled omnibus test result when it is actually a descriptive mean of per-cell ranks (section 10.7).
30. A silently imputed, substituted, or dropped comparator where per-run evidence is missing, instead of the disclosed function-level fallback (section 10.7).
31. A Word deliverable whose typography (font, size, alignment, headings) does not match the LaTeX PDF, so a Word-exported PDF looks materially different from the submitted LaTeX PDF (Stage 17, T1–T5).
32. Equations or tables that are native in the PDF but rasterized as images in the Word version.
33. A "neutral pointer" sentence in the main text, abstract, or conclusion that actually states or implies an ablation/component result, in violation of the main-manuscript ablation prohibition as NARROWED in section 10.9 (favorable or efficacy-implying results only; the deliberately-advertised ISM null is compliant).
34. A stale existence or availability claim ("data does not exist / disclosed-unavailable / exists only at scope X") left uncorrected after a post-freeze data recovery made the seed-deterministic cells available (section 10.7).
35. A non-deterministic post-freeze wall-clock runtime mislabeled as "comparable" to a frozen campaign it cannot be compared to (section 10.7).
36. A printed update rule for a titular mechanism that contradicts the frozen code — decay applied to the wrong operand, or a learning rate collapsed into the retention factor — so reimplementation from the paper builds the wrong operator (sections 6 and 10.6).
37. A raw BibTeX key, or an internal registry ID (an evidence E-number) off-by-one from the printed equation number, appearing in a figure (sections 13 and 10.17).
38. An orphan or superseded source file, built by nothing but still in the tree, carrying a prohibited mechanism name, a claimed component study, or a stale exhibit that could be submitted by accident (sections 1 and 10.11).
39. A three-way source↔PDF↔Word version desync in which the three deliverables do not resolve to one frozen scientific state (Stage 0).
40. A main-text↔conclusions↔supplement↔back-matter contradiction about what the supplement contains — the paper cites supplementary evidence the supplement says is absent, or a conclusion denies a component study the supplement includes (Stages 1 and 14).
41. A raw machine-pipeline token exposed to the reader — a hash-suffixed release tag or commit SHA (`rel-YYYY-MM-DD-<hex>`), an internal analysis-bundle path, an identical build/version string mechanically stamped on many captions, a placeholder (`TODO`/`TBD`/all-zero ORCID/dummy DOI), or an internal profile/config/registry name presented as prose — that makes the manuscript read as machine-generated rather than author-written (section 10.17.4; pre-flight E9).

---

## 15. Prohibited review shortcuts

The review MUST NOT:

- provide only a generic checklist;
- summarize the manuscript without testing its claims;
- assign high scores without citing evidence;
- infer correctness from polished language;
- accept “standard protocol” without verifying the actual protocol;
- assume tables are correct because they look plausible;
- assume citations are valid because they are formatted correctly;
- ask for “more experiments” without specifying the decision-relevant design;
- rewrite scientific passages before verifying their facts;
- close issues based on author assurances alone when artifacts can be checked;
- combine all reviewer voices into one before independent passes;
- suppress minority reviewer concerns;
- recommend an analysis method merely because it is common;
- declare a journal Q1 or Q2 without current verification;
- predict acceptance probability as a fact;
- use AI-detector scores as a quality gate; or
- optimize prose for detector evasion.

---

## 16. Preferred calibrated language for the review

Use precise review language.

Prefer:

- “The evidence directly supports…”
- “The evidence supports this conclusion only for…”
- “This result is descriptive because valid pairing is unavailable.”
- “The current design does not identify the component’s independent causal effect.”
- “The conclusion reverses under the following reasonable analysis choice…”
- “The comparison is not fair because…”
- “This is a major submission risk because…”
- “The manuscript can resolve this without new experiments by…”
- “A new experiment is required because no existing admissible evidence answers…”
- “The strongest defensible wording is…”
- “The claim should be omitted if the requested evidence cannot be produced.”
- “The manuscript is a Q1-ready candidate under this internal rubric, not guaranteed to be accepted.”

Avoid:

- “looks good”;
- “seems novel” without comparison;
- “the statistics appear fine”;
- “humanize this” without defining the language defect;
- “make it pass AI detection”;
- “add more references” without identifying the missing concept;
- “run more experiments” without a design;
- “improve the discussion” without naming the missing reasoning; and
- “guaranteed acceptance.”

---

## 17. Final execution instruction

Begin at Stage 0 and proceed through Stage 20. Do not skip directly to language editing. Maintain an issue register throughout the review. Surface a critical or major defect as soon as it is confirmed, even before the full review is complete, but continue every independent review task that remains valid.

At the end:

1. produce every mandatory review artifact or its in-report equivalent;
2. provide the complete final report in the format of Section 12;
3. apply Gates A–Q;
4. assign one internal disposition code;
5. state the exact minimum path to Q2 readiness and the additional path to Q1 readiness;
6. distinguish scientific blockers from administrative blockers;
7. provide no acceptance guarantee; and
8. require a full post-revision verification cycle before changing the readiness decision.

### 17.1 Iterative convergence protocol (five independent passes → one master report)

Run the complete Stage 0–20 review as **five independent iterations**, not a single pass:

1. **Iteration 1** — full review from Stage 0; log every finding as a ticket (§5.4 / Appendix A.1).
2. **Iterations 2–5** — begin again from Stage 0, **assuming the previous iterations' findings are corrected.** Re-read the entire manuscript and supplement fresh and surface only **remaining or newly-exposed** issues, including any **regression** a fix could introduce and any main ↔ supplement ↔ governance de-synchronization. Do not re-report an already-logged item unless its fix is wrong or incomplete.
3. **Early convergence.** If two consecutive iterations surface no new *material* issue, declare convergence and stop early; state that convergence was reached and at which iteration. (This manuscript has already passed a three-round convergence review per §1.5, so rapid convergence — often with only Editorial-severity residue — is the expected outcome; a sudden burst of new Critical/Major findings is itself a signal to re-examine the finding, not necessarily the manuscript.)

Then consolidate **all** iterations into one **master report**:

- **De-duplicate** findings across iterations, keeping the sharpest statement of each;
- **Prioritize** the survivors (Critical → Major → Minor → Editorial), each carrying the full ticket fields — severity, category, exact location, detailed description, why it matters, recommended correction, and expected improvement after implementation;
- **List the mandatory corrections before submission** (every Critical and Major finding, plus any hard-gate blocker) *separately* from optional refinements;
- **Re-verification ledger:** record which §1.5.3 resolutions AND which 2026-07-22 register closures (SE-001..SE-050, `papers/review_2026_07_22/issue_register.csv`) were independently re-confirmed on the current build and whether any regressed;
- **Final publication-readiness verdict:** state whether the manuscript is ready to submit to a high-quality **Q2 journal** (MDPI *Algorithms*) or give the exact minimum remaining actions, cleanly separating **scientific blockers** from **author-side administrative blockers** (§1.5.4). Provide no acceptance, quartile, or decision guarantee.

The master report must be comprehensive, self-contained, and serve as the definitive roadmap for polishing the manuscript and all supplementary materials to the highest standard expected for a competitive Q2 journal.

The manuscript is submission-ready only when the evidence, method, statistics, interpretation, writing, ethics, exhibits, reproducibility, journal compliance, and final package all agree.

---

## Appendix A — Machine-readable schemas

### A.1 Issue register

```text
ticket_id,review_stage,reviewer_role,severity,priority,confidence,
issue_type,manuscript_location,claim_id_or_artifact_id,concise_issue,
exact_evidence_or_observation,root_cause,scientific_or_editorial_justification,
impact_on_validity_or_acceptance,required_correction,acceptable_alternatives,
additional_evidence_needed,dependencies,expected_improvement,
post_revision_verification,status
```

`issue_type` uses the controlled vocabulary defined in section 5.4.

### A.2 Claim audit

```text
claim_id,normalized_claim,claim_type,manuscript_location,scope,
evidence_class,source_or_artifact,support_strength,assumptions,
permitted_wording,prohibited_wording,reviewer_risk,disposition,
verification_status,notes
```

`support_strength` uses `direct / partial / indirect / unavailable` and `disposition` uses `accept / narrow / qualify / move / omit / block` — the controlled vocabularies defined in section 4.2, whose claim-record field list is identical to this schema.

### A.3 Scorecard

```text
category,reviewer,score_1_to_5,weight,weighted_score,evidence,
critical_count,major_count,gate,status,notes
```

### A.4 Exhibit audit

```text
artifact_id,type,document_location,research_question,source_paths,
generator,command,source_checksums,output_checksum,caption_complete,
value_or_point_validation,legibility,accessibility,cross_format_match,
issue_ticket_ids,status,notes
```

### A.5 Missing-experiment register

```text
experiment_id,research_question,current_evidence_gap,minimum_design,
controls,scope,endpoint,analysis,expected_decision_impact,
admissible_evidence_available,classification,claim_affected,priority,
estimated_scientific_value,status
```

`classification` uses the controlled vocabulary defined in section 12.11 (`essential_before_submission` / `recommended_for_q1` / `useful_for_q2` / `optional_or_out_of_scope`). `admissible_evidence_available` records whether existing admissible evidence can already answer the question; the section 16 preferred wording “A new experiment is required because no existing admissible evidence answers…” depends on this field.

### A.6 Post-revision verification

```text
ticket_id,revision_version,claimed_action,changed_artifacts,
verification_method,verification_evidence,dependent_checks,
regression_status,resolution_status,reviewer,notes
```

### A.7 Statistical-analysis register

```text
analysis_id,research_question,estimand,endpoint,observation_unit,
experimental_unit,aggregation_before_testing,pairing_key,
independence_assumptions,sample_size_or_task_count,missing_data_rule,
failure_encoding,test,one_or_two_sided_alternative,multiplicity_family,
correction,effect_size,effect_direction,uncertainty_interval,
resampling_unit,RNG_seed,software_and_version,reported_value,
recomputed_value,match_status,ticket_ids
```

### A.8 Revision roadmap

```text
work_item_id,source_ticket_ids,root_cause,required_action,
scientific_or_editorial,owner_role,dependencies,required_inputs,
artifacts_to_change,artifacts_to_regenerate,
verification_command_or_method,completion_criterion,priority,status
```

### A.9 Response-to-reviewers seed

```text
reviewer_or_ticket_id,concern,response_position,
analysis_or_evidence_reviewed,action_taken,exact_manuscript_change,
new_analysis_or_experiment,verification_result,
reason_if_not_implemented,status
```

### A.10 GenAI disclosure and detection-risk audit

```text
check_id,venue_policy_source,policy_access_date,requirement,
manuscript_location,submission_form_declared,methods_statement_present,
acknowledgments_tool_and_version,disclosure_scope_vs_actual_use,
authorship_prohibition_ok,wording_separates_language_from_science,
science_provenance_checkable,detector_used,detector_score,
false_positive_caveat,cross_format_persistence,
consistency_form_methods_ack,severity,status,notes
```

(`check_id` covers D16.1–D16.6; one row per requirement, plus one row per detector run. A detector score is recorded with its false-positive caveat and never used as sole evidence of misconduct.)

---

## Appendix B — Review decision template

```text
INTERNAL DISPOSITION:
CURRENT READINESS BAND:
WEIGHTED READINESS SCORE:
FAILED OR BLOCKED GATES:
OPEN CRITICAL TICKETS:
OPEN MAJOR TICKETS:
OPEN MODERATE TICKETS:
STRONGEST VERIFIED CONTRIBUTION:
CENTRAL SCIENTIFIC WEAKNESS:
TOP DESK-REJECTION RISK:
MINIMUM WORK FOR Q2 READINESS:
ADDITIONAL WORK FOR Q1 READINESS:
TARGET-JOURNAL FIT:
SCIENTIFIC STATUS:
ADMINISTRATIVE STATUS:
RESIDUAL UNCERTAINTY:
CONDITIONS FOR REASSESSMENT:
```

---

## Appendix C — Safe high-impact language-revision template

```text
REVISION ID:
LOCATION:
ORIGINAL EXCERPT:
SCIENTIFIC PURPOSE OF THE PASSAGE:
CONFIRMED FACTS AND EVIDENCE:
LANGUAGE DEFECT:
RISK IF UNCHANGED:
PROPOSED REVISION:
NUMBERS UNCHANGED: YES / NO / NOT APPLICABLE
CITATIONS UNCHANGED OR REVERIFIED: YES / NO / NOT APPLICABLE
CLAIM SCOPE UNCHANGED OR DELIBERATELY NARROWED: YES / NO
POST-REVISION CHECK:
```

---

## Appendix D — Final reviewer sign-off table

| Role | Scientific scope reviewed | Score | Open C/M issues | Sign-off | Conditions |
|---|---|---:|---:|---|---|
| EIC | fit, significance, final decision |  |  |  |  |
| AE | synthesis and proportionality |  |  |  |  |
| R1 | domain science |  |  |  |  |
| R2 | theory/method |  |  |  |  |
| R3 | experimental design |  |  |  |  |
| R4 | statistics |  |  |  |  |
| R5 | reproducibility |  |  |  |  |
| R6 | skeptical domain attack |  |  |  |  |
| RI | integrity and ethics |  |  |  |  |
| RW | writing and authorship integrity |  |  |  |  |
| VIZ | exhibits |  |  |  |  |
| PROD-PDF | PDF/LaTeX |  |  |  |  |
| PROD-WORD | Word/OOXML |  |  |  |  |
| REP | citations/references |  |  |  |  |
| JCO | journal compliance |  |  |  |  |
| SE | consensus and verification |  |  |  |  |

The final readiness decision requires all applicable roles to sign off, every hard gate to pass, and zero open critical or major issues.

---

## Appendix E — Canonical-defect pre-flight (lessons from review R1)

Run this pre-flight **first**, before the deep stage work, as a fast pass over the highest-value defect patterns actually observed in an independent six-reviewer review (R1) of an evidence-locked optimization manuscript. Each item states the **exact test** and the **remedy**. The pre-flight is diagnostic only: it never authorizes fabricating evidence, changing a frozen number, or editing the manuscript beyond the governed correction protocol. A pre-flight hit opens a ticket under the mandatory schema (section 5.4), routes to the owning team (section 3.4), and is severity-anchored against section 5.5; it does not by itself close, pass, or downgrade any gate. A clean pre-flight is necessary but not sufficient — proceed through Stages 0–20 and Gates A–Q regardless, and record any pre-flight hit that the deep review later resolves, with its resolution evidence, in the issue register.

**E1 — Main-text ablation-result leak (R1 C1; §10.9; Gates C/J).**
- *Test.* For every main-text, abstract, conclusion, and cover-letter sentence (highlights/graphical abstract: N/A at MDPI Algorithms) touching a component/mechanism, apply the §10.9 leak test: does removing all ablation knowledge change whether the sentence is supported? A stated FAVORABLE or efficacy-implying claim, or a "neutral pointer" that implies a direction is a leak — even with no number printed. Confirm every supplementary-study cross-reference is matched by an actual supplement entry.
- *Remedy (as NARROWED for this manuscript — §10.9/§1.5.0-D).* The deliberately-advertised ISM null (failure-to-detect framing, SE-021) is COMPLIANT; the prohibition binds favorable/efficacy-implying results. For those: result-free deferral (§10.9): neutralize to bundled-tier co-activation, remove the outcome and its direction, point to the Supplement without stating a result, and make the existence claim match the supplement. Verify zero ablation-token hits in the rendered PDF.

**E2 — Stale evidence-availability claim after recovery, and runtime non-comparability (R1 C5/C6; §10.7; Gates G/J).**
- *Test.* After any post-freeze recovery, enumerate every "does-not-exist / disclosed-unavailable / exists only at scope X" statement. Seed-deterministic recovered quantities (error, ranks, Wilcoxon, effect sizes, BCa) are now available — those statements are false and must be corrected. Separately, check that no non-deterministic post-freeze wall-clock runtime is labeled "comparable" to the frozen campaign.
- *Remedy.* Correct the seed-deterministic existence claims; for THIS manuscript the runtime question is settled — RT-001 closed by narrowing `tab:runtime` to DT-GSK-only single-session (no comparator wall-clock reported anywhere; §10.7) — so verify that final state rather than a disclosed-unavailable posture; add a one-line change-request footnote recording the recovery scope. Do not conflate the two quantities in either direction.

**E3 — Printed-equation vs. frozen-code mismatch (R1 C7; §10.6; Gates F/M).**
- *Test.* Read the frozen source for every titular/load-bearing update rule and recompute it symbolically. Confirm which operand carries the decay/retention factor, whether a separate learning rate exists, and that no two parameters were collapsed. Cross-check the equation, the pseudocode step, the prose, the parameter table, and any figure that draws the rule.
- *Remedy.* Correct all surfaces to the code's operator (the R1 fix: `G←(1−λ)G+λΣ` → `G←λG+ηΣ`). Verify in the rendered PDF and the Word deliverable.

**E4 — Exhibit tokens: raw BibTeX keys and internal registry IDs (R1 C8/C9; §§13, 10.17; Gate M).**
- *Test.* Inspect every figure/table for a raw BibTeX key, an evidence `E`-number, or any other build-internal token in place of a reader-facing citation or a printed equation/figure number; check internal-ID↔printed-number alignment.
- *Remedy.* Regenerate the exhibit with formatted citations/printed numbers, or add an explicit legend mapping internal IDs to printed numbers. Verify in the rendered PDF.

**E5 — Figures that are really tables; pseudocode legibility; native Word editability (R1 exhibit; §10.17; Gates M/P).**
- *Test.* Flag any `matplotlib`-styled "figure" that is a table (coloured ON/OFF cells, plotted text) or a dense auto-generated box-and-arrow rail; check that every data table and every schematic's step content ships as a native `w:tbl` in Word, not a rasterized image; check the main pseudocode is clean, row-based, hidden/minimal-grid, non-overflowing, non-colliding, phase-grouped, with an accompanying simple flowchart where it aids comprehension.
- *Remedy.* Re-render clutter as a clean native table or a simple labelled flowchart; fix pseudocode overflow/collision; supply native editable Word tables. This is simplification, never detector-evasion editing (§§15.5, 10.17).

**E6 — Orphan/superseded source files (R1 C4; §§1, 10.11; Gate A).**
- *Test.* List section/exhibit sources present in the tree but built by nothing; inspect each for prohibited mechanism names, claimed component studies, or stale exhibits.
- *Remedy.* Quarantine or git-remove the orphan and drop its manifest entry; confirm the canonical build is unaffected.

**E7 — Three-way source↔PDF↔Word desync (Stage 0; Gate A).**
- *Test.* Using the freeze manifest / hash record where available, confirm the canonical sources, the compiled PDF, and the Word/DOCX deliverable all resolve to one frozen scientific state; otherwise reconcile version strings, build epochs, and a sample of headline values.
- *Remedy.* Rebuild deterministically to one state; Stage 0 hard-fails until a single authoritative state is established.

**E8 — Cross-artifact consistency of the supplement claim (R1 C2/C3; Stages 1, 14; Gates C/J).**
- *Test.* Confirm the main text, conclusions, supplement file, and back-matter listing agree on what the supplement actually contains — no citation of an absent supplementary study, no conclusion denying a study the supplement includes.
- *Remedy.* Reconcile all four surfaces to the shipped supplement; re-verify in both PDF and Word.

**E9 — Machine-generated identifiers, placeholders, and provenance stamps in reader-facing text (§10.17.4; Gates N/M).** Scan every rendered surface (main + supplement, PDF + Word) for raw build/evidence tokens exposed to the reader: hash-suffixed release tags (`rel-YYYY-MM-DD-<hex>`, `abl-rel-…`, `-dirty`), commit SHAs, internal analysis-bundle paths, the *same* release string mechanically stamped on many captions, placeholder tokens (`TODO`/`TBD`/`XXX`/`lorem ipsum`/all-zero ORCIDs/dummy DOIs), and internal engineering nouns (config/profile names like a `pub` profile, exhibit/registry codes) presented as prose. Any such token in reader-facing text is an authorship-integrity defect: it makes the manuscript read as machine output.
- *Remedy.* Replace with natural authored language; state the release/provenance **once** in the Methods and/or Data-Availability statement as a single deliberate reference (a DOI/URL or one named frozen release), and remove the scattered per-caption stamps. De-cluttering for authorship quality, never detection-evasion (§15.5); the full provenance stays recorded in the governance artifacts. Re-verify no raw identifier remains and no number/claim/pointer was weakened.

| Pre-flight | R1 ticket(s) | Owning team (section 3.4) | Gate(s) | Governing section |
|---|---|---|---|---|
| E1 Ablation leak | C1 | T2-BENCH | C, J | 10.9 |
| E2 Stale availability / runtime | C5, C6 | T3-STAT | G, J | 10.7 |
| E3 Equation vs. code | C7 | T1-OPT | F, M | 10.6 |
| E4 Exhibit tokens | C8, C9 | T5-WRITE | M | 13, 10.17 |
| E5 Figure-tables / pseudocode / Word | — | T5-WRITE | M, P | 10.17 |
| E6 Orphan files | C4 | T6-INTEG | A | 1, 10.11 |
| E7 Three-way desync | — | ECB | A | Stage 0 |
| E8 Supplement consistency | C2, C3 | ECB | C, J | 1, 14 |
| E9 Machine identifiers / placeholders in prose | — | T5-WRITE, T6-INTEG | N, M | 10.17.4 |

**E10 — Measurement-artifact metrics (R2, SE-036).** A writing/production metric can be wrong because the MEASUREMENT is wrong, not the text: the panel's "98 over-long sentences" (and a later 70) were artifacts of tokenization that merged sentences across inline `%` comments; the comment-aware baseline was 61 (now 0 >55 words, with 3 accepted semicolon-list flags).
- *Test.* Before acting on any count-based finding (sentence lengths, word counts, occurrence tallies), re-derive the count with source-aware tokenization (strip comments, mask environments) and record the method beside the number.
- *Remedy.* Fix the measurement first; re-issue the finding only if it survives.

**E11 — Partial static scans producing confident false negatives (R2, SE-022).** A label/reference scan that reads only `sections/*.tex` misses everything defined in `\input`-ed files: four Phase-3 artifacts were wrongly declared label-less because the scan did not traverse `\input` (the labels live under `build_prompt_phases/phase_03/`).
- *Test.* Any tooling that asserts "X does not exist in the sources" MUST traverse the document graph exactly as LaTeX does (both roots, `\input` recursion — `validate_artifact_labels.py` is the reference implementation).
- *Remedy.* Re-run the corrected scan before recording an absence.

**E12 — Estimand conflation between same-named artifacts (R2, SE-046).** Two artifact families both called "BCa CI" carry DIFFERENT estimands: `bca_ci_*.csv` = intervals on per-function mean DIFFERENCES; `bca_rank_ci_cec2017.csv` (and Table `tab:bca-ci`) = intervals on Friedman MEAN RANKS.
- *Test.* Wherever an interval, effect size, or statistic is cited, confirm the estimand named in prose matches the artifact actually pointed to; flag any pointer that resolves to a different quantity than the sentence describes.
- *Remedy.* Re-point or re-word; never average over the distinction.

**E13 — Attestation-vs-artifact provenance discipline (R2, SE-014/D-0020).** Some disclosed facts rest on author attestation with NO corroborating repository artifact (the six full-panel candidate configurations; the intermediates predate the immutable release). The manuscript states this provenance status explicitly.
- *Test.* For every disclosed count or historical fact, classify its provenance (released artifact / governance record / author attestation) and verify the manuscript's stated provenance matches; an attested fact presented as artifact-backed is a Major integrity defect, and vice versa an artifact-backed fact needlessly hedged as attestation is a calibration defect.
- *Remedy.* Align the stated provenance with reality; never invent corroboration.

## Appendix F — Exhaustive per-dimension camera-ready quality checklist

This appendix is the consolidated, per-dimension checklist the review MUST complete before declaring a manuscript camera-ready. It complements — does not replace — the staged workflow (§8), the gates (§11), and the pre-flight (Appendix E); it exists so that **no aspect of a publication-ready manuscript is left unchecked**. Every item is a concrete, verifiable check. A failed item is a ticket (§5) routed to the owning team (§3.4) and gate (§11); every **MUST** is blocking, every **SHOULD** is a strong recommendation whose waiver must be justified in the report. Verify each item against **both** the rendered PDF and the Word deliverable, **main and supplement**. Record each dimension's verdict (pass / ticketed) in the final report (§12).

### F.1 Technical and scientific content
- Every technical statement is correct and matches the implementation/code (§10.6); no hand-wave substitutes for a verifiable mechanism.
- Each contribution is defined precisely, is genuinely novel (not a re-description of prior work), and is traceable to a specific method component and a specific result.
- Assumptions, preconditions, and the scope of applicability are stated wherever a claim depends on them.
- No internal contradiction among the method description, the equations, the pseudocode, the figures, and the reported behavior.

### F.2 Methodology
- The method can be reimplemented from the paper alone: every constant, schedule, gate, tier, and default is either stated or pointed to a single declared source of truth, and that source is faithful to the code.
- Design choices are motivated (why this mechanism, why this value/threshold) rather than merely asserted.
- The relationship to the base method and the closest prior methods is explicit — what is inherited verbatim, what is modified, what is new.
- Time/memory/evaluation overhead is stated and consistent with the design and the complexity analysis.

### F.3 Novelty and positioning
- The novelty claim is bounded and honest — not overclaimed (field-wide when the evidence is scoped) and not underclaimed.
- The work is positioned against the correct, current baselines, and explicitly states what it does NOT claim.
- Prior work is characterized fairly and accurately — no straw men; each cited method's actual capability is stated correctly.

### F.4 Validity of claims
- Every quantitative claim in the abstract, introduction, results, and conclusions is backed by a named exhibit and traces to the evidence (§4).
- Comparative claims are scoped exactly to what was tested; no extrapolation beyond the evaluated regime.
- Causal language appears only where a controlled comparison supports it; otherwise "consistent with"/"associated with".
- Negative, unfavorable, and null results are reported with the same prominence as favorable ones (§10.5 loss-visibility parity).

### F.5 Experimental design
- Benchmarks, dimensions, run counts, budgets, and metrics are field-standard, adequately powered, and justified.
- The protocol is fair — identical budgets/seeds/instances across methods, with any exception documented, not hidden.
- The statistical plan is appropriate (correct tests, multiple-comparison correction, effect sizes, uncertainty), pre-specified, and matches what is reported (§10.7).
- Reproducibility is documented (seeds, environment, deterministic pipeline); the exact release/archive is referenced once, deliberately, in the data-availability statement — never scattered (§10.17.4).

### F.6 Results
- Every reported number reproduces from the released evidence to the stated precision.
- Tables and figures agree with each other and with the prose; no cell, label, or aggregate drift.
- Aggregates are computed correctly and their construction (weighted vs unweighted, which cells) is stated.
- Sufficient granularity is shown (per-dimension/per-function) rather than only headline aggregates that could mask variance.

### F.7 Discussion
- Interprets results without overreach; distinguishes what is shown from what is suggested.
- Explains unfavorable or surprising results honestly rather than omitting them.
- Connects the empirical findings back to the mechanism and the stated contributions.

### F.8 Conclusions
- Restates what was established (scoped), introducing no new claim or number absent from the body.
- Limitations are explicit, specific, and substantive — not token disclaimers.
- Future work is concrete and follows from the stated limitations.

### F.9 Organization and logical flow
- The section structure is standard for the venue; each section does one job.
- Each section and paragraph follows logically from the previous; every forward/backward reference resolves and aids navigation.
- No orphaned, dangling, or duplicated material; no section that merely repeats another.

### F.10 Academic writing and readability
- One consistent scholarly voice throughout (§10.17.5); precise, economical, and active where appropriate.
- No AI-clutter connectives, hollow intensifiers, throat-clearing preambles, or templated cadence (§§10.17.1, 10.17.5).
- Sentence and paragraph structure and length vary; no mechanical uniformity.
- Grammar, spelling, punctuation, and article/preposition usage are correct throughout.

### F.11 Terminology and notation
- Every symbol is defined at first use and used consistently; a notation table exists for a symbol-heavy paper.
- Every acronym is expanded at first use and used consistently thereafter; no clashing or silently reused abbreviations.
- Naming is consistent across prose, equations, algorithm, figures, and tables — the same object carries one name.
- No internal code/engineering identifier is presented as prose (§10.17.4).

### F.12 Equations
- Every displayed equation is numbered, referenced, and correct, and matches the code it specifies (§10.6, E3).
- Symbols in equations match the notation table and the surrounding prose.
- Equation formatting is consistent (operators, subscripts, alignment); no oversized or overflowing math.
- No equation is orphaned (defined but never used) or used before definition without a forward pointer.

### F.13 Algorithms and pseudocode
- The pseudocode is clean, numbered, consistently indented, with no overflow, collision, or double-print, and reads as one legible block (§10.17.2).
- Its step order matches the code and the companion flowchart; equation anchors are the printed equation numbers, not internal registry IDs (E4).
- Inputs/outputs, preconditions, and termination are stated; the listing is reimplementable.
- It ships as native editable text (or a native table) in the Word deliverable, not a rasterized image (§10.17.3).

### F.14 Figures and flowcharts
- Every figure is legible at print size, carries axes/units/legends, uses a non-misleading baseline, and is graphically honest (§13).
- A "figure" that is really a table is rendered as a clean table (§10.17.1); a complex algorithm is paired with a simple, clean flowchart where it aids comprehension.
- Flowcharts avoid unnecessary fill/decoration and any arrow/box collision, and their control flow is faithful to the algorithm and the code.
- Focal-series and colour conventions are consistent across all figures — the proposed method reads identically everywhere — and no figure overflows the text area.
- No build-pipeline text (file paths, registry IDs, release tags, config names) is baked into any rendered image (§10.17.4, E9).

### F.15 Tables
- Every table is legible and fits the column/page, with consistent rules (booktabs; grouped rules for spec tables, light zebra for dense data tables) and consistent number formatting/precision.
- Best/highlighted cells are marked correctly and only where a superiority claim is warranted.
- Column headers, units, and footnotes are complete; no cell overflow or collision.
- Data tables ship as native editable objects in the Word deliverable (§10.17.3).

### F.16 Captions
- Every caption is self-contained (what the exhibit shows, the metric, the scope/runs, any qualifier) and matches the exhibit content.
- No mechanically repeated provenance stamp across captions, and no internal identifier (§10.17.4).
- Caption numbering is sequential and every in-text reference resolves to the correct printed number.

### F.17 Formatting and typography
- The venue template is used correctly; margins, fonts, spacing, and headings conform.
- Hyphen/en-dash/em-dash and quotation styles are consistent, as is the capitalization of section/figure/table references.
- No overfull/underfull boxes producing visible overflow; no widow/orphan lines that harm readability.
- No leftover draft artifacts — review-mode line numbers only where NOT intended (for this submission MDPI submit-mode line numbering is deliberately ACTIVE — SE-048; do not flag it as residue), `TODO`/`TBD`, or placeholder ORCIDs/DOIs — appear in the rendered text.

### F.18 Consistency (cross-artifact)
- Main text ↔ supplement ↔ figures ↔ tables ↔ captions ↔ any manifest agree on every shared number, claim, and scope (Appendix E, E7/E8).
- The same value/threshold is stated identically everywhere it appears; where a value varies by tier/condition, the variation is stated everywhere it appears.
- The PDF and Word deliverables resolve to one frozen scientific state.

### F.19 Citations and references
- Every in-text citation resolves to a reference and every reference is cited (or justified as a maintained corpus); the build log shows zero undefined citations.
- Reference entries are complete (authors, title, venue, year, DOI/URL where applicable), correctly typed, and consistently formatted in the venue style; no duplicate keys.
- Citations are accurate (the cited work supports the claim) and current; no missing seminal or closest-competitor work.
- Self-citation is proportionate and disclosed where it bears on the comparison.

### F.20 Supplementary material
- The supplement is consistent with the main text — nothing cited-but-absent or present-but-denied — is self-contained in its captions, and builds cleanly and deterministically.
- Its exhibits meet the same bar (editable Word tables, honest figures, no machine tokens outside a dedicated reproducibility appendix).
- The main text remains auditable without the supplement; the supplement adds detail, not new load-bearing claims.

### F.21 Overall presentation and prose quality
- The whole manuscript meets the prose standard of experienced researchers (§10.17.5): natural language, a coherent argument, no repetition, and no automation artifacts left in the text (raw identifiers, release labels, placeholders, templated structure).
- Every reader-facing surface (main + supplement, PDF + Word) is free of machine tokens (§10.17.4, E9); at most one deliberate archival reference is permitted, in the data-availability statement.
- The manuscript is coherent, technically accurate, visually polished, free of repetition, and aligned with Q1 standards — and nothing scientific was altered in achieving this (§15.5).

**Closing.** Completing this checklist is necessary but not sufficient for acceptance (§6): it certifies the camera-ready quality of the artifact, not the strength of the science. A clean sweep of F.1–F.21 with all gates (§11) green is the minimum bar for declaring the manuscript submission-ready.


---

## 18. Forensic deep-review layer (FDR) — twelve-role forensic pass with an authorship-defensibility audit (author-supplied master prompt, reviewed and tuned 2026-07-31)

### 18.0 Provenance, invocation, and precedence

**Provenance.** The author supplied a standalone "MASTER PROMPT:
MULTIDISCIPLINARY FORENSIC REVIEW OF A RESEARCH PAPER AND ITS SUPPLEMENTARY
MATERIAL" (2026-07-31) and directed that it be reviewed, tuned, and added to
this instrument. The original was written for an arbitrary chat-pasted
manuscript with no governance: it assumed the reviewer may freely rewrite the
title and abstract, invite new citations, and treat every fix as free. None
of that holds here. This section is the repo-native adaptation; §18.2 records
every material tuning decision so the delta from the author's original is
auditable.

**Invocation.** The FDR layer runs ON DEMAND — when the author asks for a
"forensic review" / "FDR pass" — or as the deep mode of a full panel round.
It COMPOSES WITH the §8 workflow and the §3 panel; it does not replace them.
It is heavier than the standard round: budget accordingly and execute it as a
real multi-agent panel with per-finding adversarial verification (the
project's practice), not as a single-context simulation — the original's
"simulate a panel meeting" instruction is superseded by actually convening
one.

**Precedence.** Subordinate to §1.4 (authority), the §1.5 snapshot and its
newest layer, §2 (non-negotiable rules), §4 (evidence constitution), §5
(classification), and §10 (the evidence-locked project profile). On any
conflict, those govern. This layer only ADDS review surface. It never relaxes
a gate, reopens a registered outcome, re-runs frozen evidence, or authorizes
an edit outside change control.

**Materials.** The submission is the repository, never a paste. Reviewable
materials: `papers/main.tex` + the five section files; `papers/supplementary.tex`;
the five rendered artifacts (both PDFs, both DOCX, `cover_letter.pdf`);
`papers/references.bib`; the governance registers; the frozen analysis
bundles under `papers/analysis/`; and the evidence-release manifests. Venue
facts are pre-filled from §1.5.1 (MDPI *Algorithms*; American English;
MDPI numbered references) and are never requested from the author. The
original's materials list is adjusted: no graphical abstract or Elsevier-style
highlights exist for this venue (their absence is NOT a finding); no
response-to-reviewers document exists pre-submission; the governance registers
ARE reviewable materials and their internal consistency is in scope.

### 18.1 Roster mapping — the twelve forensic roles on the standing panel

| # | FDR role (original) | Standing seat (§3) | Delta this layer adds |
|---|---|---|---|
| 1 | Editor-in-Chief, Q1 journal | ECB | desk-rejection-risk sweep as an explicit output |
| 2 | Senior domain expert | T1-OPT | challenge-novelty duty made adversarial by default |
| 3 | Methodology / experimental design | T2-BENCH | threats-to-validity taxonomy (internal/external) |
| 4 | Statistics and data analysis | T3-STAT | practical-vs-statistical significance split reported per claim |
| 5 | Algorithm / mathematical verification | T1-OPT + §8 math stage | the 17-point equation/algorithm checklist of §18.3 Pass 4 |
| 6 | Reproducibility / software engineering | T3-STAT repro seat | committed-blob rule (§1.5.0-Q(b)) is part of the audit |
| 7 | Senior academic writing editor | presentation seat | full-sentence-coverage language pass (§18.3 Pass 8) |
| 8 | Human-authenticity / authorship-defensibility editor | **NEW — defined by §18.4** | the layer's core addition; deepens F.21/§10.17.5 from a paragraph to a methodology |
| 9 | Citation and research-integrity auditor | citation seat + §4 | representation audit within the CLOSED corpus (§18.3 Pass 6) |
| 10 | Supplementary-material auditor | cross-format seat | semantic (validator-invisible) consistency audit |
| 11 | Skeptical peer reviewer | adversarial verifier fleet | refute-by-default verification of every finding |
| 12 | Revision strategist | ticket register + disposition machinery | staged plan with freeze-batching (§18.5 Part L) |

Every role produces findings independently; every finding is then
adversarially verified against the live tree before it may appear in the
report. A finding that fails verification is recorded as refuted, not
deleted.

### 18.2 Non-negotiable tuning deltas from the author's original

These are the points where the original, applied verbatim, would have
violated this project's governance. Each is binding for any FDR execution.

**(a) Frozen and registered text.** The manuscript is under a freeze
manifest, and specific sentences are REGISTERED VERBATIMS (the wording-bank
sentences as amended, currently through Amendment 3). The FDR may FLAG any
frozen or registered passage, but a rewrite of a registered verbatim is never
"replacement text" — it is a proposal for a new dated, append-only amendment,
and must be labeled as such. Rewrites of merely-frozen (non-registered) text
are proposals that, if adopted, void the current freeze pass and enter the
standard re-mint cycle.

**(b) Closed citation corpus.** The corpus is closed at the allowed-key list
(`papers/governance/allowed_citation_keys.txt`; C1–C5 lockstep). "Add a
citation" recommendations are phrased as CR-gated admission requests (the
CR-0020 pattern), never as edits. The original's placeholder
`[CITE THE PRIMARY SOURCE]` resolves ONLY through the lockstep: bibliographic
metadata comes from the source PDF, never from memory — which the original
itself requires, and which §4 already enforces. Existence checks are
performed against the evidence cards and reference PDFs in-repo, not by
recall.

**(c) Numbers from frozen CSVs only.** Every numerical verification reads
the frozen analysis bundles; no standing, p-value, rank, or effect size is
ever confirmed from memory (§10). Evidential-tier discipline applies
verbatim: omnibus/Nemenyi findings are never attributed to the paired layer,
descriptive-only surfaces never acquire confirmatory language, and the
CEC2020/LSGO caveat sentences are load-bearing.

**(d) Fix class and freeze consequence are mandatory columns.** The original
treats every correction as free. Here every finding must carry, in addition
to §5 severity/priority/confidence: `fix_class` = manuscript (voids the
current pass; requires re-mint + superseding tag) | repo-only (no re-mint) |
author-side (portal/account action) | none, and a one-clause freeze
consequence. A finding without a fix class is incomplete.

**(e) Severity taxonomy: use §5, map the original's.** The original's four
severities and P0–P3 map as: Critical→C, Major→M, Minor→N (or O when it
weakens credibility beyond one locus), Editorial→E; original P0→P0/P1,
P1→P1, P2→P2/P3, P3→P3/P4. Report in §5 vocabulary; do not run two
taxonomies side by side.

**(f) Verdict scale: use §6 bands.** The original's five-level verdict maps
onto the §6 readiness bands; its rule "never submission-ready with unresolved
Critical/P0 items" is already the §11 gate and stands. The panel-register
verdict vocabulary (READY / READY_WITH_NITS / MINOR_REVISION /
MAJOR_REVISION) is used for seat verdicts.

**(g) Verify, don't re-raise.** The original has no concept of a completed
review history. This project has closed rounds with registered dispositions.
A closed finding re-enters ONLY on demonstrated regression (show the closure,
then show the live tree contradicting it) — the standing rule of the §1.5
layers. Independent re-verification of closed items is encouraged;
re-litigation is not.

**(h) Disclosed GenAI assistance is not a finding.** The manuscript's GenAI
disclosure names Claude Opus 4.6, 4.8 and 5.0 (Anthropic) in the manuscript
and cover letter, per MDPI policy, with author-attested scope (AG-0007,
CLOSED). The §18.4 audit therefore audits DEFENSIBILITY, not detection, and
must never treat the disclosed assistance itself, or its stylistic traces, as
an integrity finding. What it hunts is prose the AUTHORS could not defend:
generic, unsupported, over-claimed, or evidence-free text — regardless of who
or what drafted it.

**(i) No applied rewrites of the title or abstract.** The original's Part K
("provide complete revised versions of: Title... Abstract...") is tuned:
title and abstract are frozen artifacts whose wording is partly registered.
Part-K rewrites for them are filed as PROPOSALS in the ticket register with
the fix-class machinery of (a); they are never presented as applied text.
For all other passages, Part-K replacement text is welcome and must meet the
§18.6 standards.

**(j) Metaheuristics checklist retained.** The original's
optimization-specific audit items (population size, FES budget, stopping
criterion, runs, bounds, constraint handling, initialization,
parameter-adaptation rules, final-local-search bias, equal budgets, official
benchmark code, mean/median/best/worst basis, numerical-precision treatment,
ranking procedures, published-results-vs-re-execution, equivalent execution
conditions) are all in scope and largely covered by §10; the FDR treats §10
as the binding instantiation and the original's list as the completeness
check against it.

### 18.3 The nine passes, mapped and tuned

- **Pass 1 — Submission map.** Seed from `claims_evidence_matrix.csv` and the
  §7 artifacts; VERIFY the map rather than rebuilding it, then flag any
  contribution whose evidence chain (theory / equation / algorithm /
  experiment / ablation / statistic / supplement) has a gap. New output: the
  Part-B table of §18.5.
- **Pass 2 — Scientific and logical review.** Per §8, plus the original's
  additions now made explicit duties: alternative-explanation analysis,
  correlation-vs-causation, empirical-results-are-not-proof, improvements
  scientifically meaningful (not merely numerically positive), and honest
  reporting of negative findings (this project's ISM null is the sanctioned
  exemplar, not a target).
- **Pass 3 — Methodological/experimental audit.** §10 profile + §18.2(j)
  checklist. Fairness findings must respect the disclosed, registered
  configuration asymmetries (the NP=5D fair-start exception and its
  disclosure set) rather than rediscovering them.
- **Pass 4 — Mathematical/algorithmic verification.** The original's 17-point
  checklist is adopted in full: symbol definitions; dimensional/logical
  consistency; index ranges; initialization; boundary cases; denominator
  safety; undefined/reused symbols; equations-vs-prose; equations-vs-
  pseudocode; pseudocode-vs-supplement; complexity plausibility;
  inputs/outputs; random operations and distributions defined; unambiguous
  update order; precise accept/reject/selection/archive/memory semantics;
  deterministic components described accurately; undocumented
  result-material implementation decisions. Output: the Part-H table with the
  original's five-value verification vocabulary (Verified from supplied
  material / Internally plausible but incompletely specified / Inconsistent /
  Incorrect / Cannot be verified). An equation is never "correct" merely
  because it is syntactically valid.
- **Pass 5 — Main–supplement consistency.** Run the validators FIRST
  (cross-format parity, doc-consistency, evidence bindings); the manual audit
  then covers what validators cannot see — semantic agreement of settings,
  scope statements, limitation lists, and interpretive claims across the two
  documents. Report per the original's conflict schema (both statements, why
  they conflict, which is more credible, what the author must verify, exact
  correction in EACH document); never silently prefer one version.
- **Pass 6 — Citation audit.** Within the closed corpus (§18.2(b)): does each
  citation support the exact claim at its locus; primary where appropriate;
  represented accurately; not overextended; not missing where attribution is
  required; consistent entries. Self-citation is audited for representation
  (the structural-forcing disclosure exists; verify it stays accurate), not
  re-litigated. Output: Part-J subsections and table.
- **Pass 7 — Authorship-defensibility audit.** §18.4, in full.
- **Pass 8 — Language pass.** Full sentence coverage per the original's item
  list, constrained by house style: American English (favorable/favors); no
  monospace/`\texttt` anywhere; line numbering stays disabled; E-notation
  table convention; terminology per `terminology_sheet.md`; captions
  self-contained. Every correction preserves technical meaning (§18.6).
- **Pass 9 — Readiness.** §6 bands, §11 gates, and the Part-N statement.

### 18.4 The authorship-defensibility audit (core addition)

#### 18.4.0 Doctrine

Never claim to prove whether any passage was written by AI or by a human.
Detector-style judgments are explicitly out of scope and unreliable on exactly
this manuscript's registers: formal academic English, non-native English
writing, heavily edited technical prose, repetitive methodological
description, and formulaic journal sections all produce false positives. The
audit's object is DEFENSIBILITY: after revision, the authors must be able to
explain and defend every sentence — in peer review, in a presentation, and in
a research-integrity inquiry. Never recommend: detector-gaming edits,
deliberate grammatical errors, arbitrary sentence-rhythm variation, informal
anecdotes in formal prose, or concealment/misrepresentation of the disclosed
AI assistance (§18.2(h)). Cosmetic synonym replacement is not a remedy for
anything.

#### 18.4.1 Pattern library

Evaluate patterns CUMULATIVELY and in context; no single feature is evidence
of anything. For each hit, identify the scientific weakness beneath the
wording — that weakness, not the style, is what gets fixed.

1. **Generic or content-light prose** — sentences that sound scholarly but
   commit to nothing: broad praise without evidence; restated importance;
   obvious facts as insights; claims that would fit any paper; abstract nouns
   where concrete findings belong. Live risk phrases for THIS domain include
   "provides valuable insights into...", "clearly demonstrate the
   effectiveness and robustness...", "opens new avenues...", and especially
   "achieves a good balance between exploration and exploitation" — flag any
   instance not tied to a measured result. Do not delete automatically;
   determine whether the claim can be made specific and evidenced, then make
   it so or remove it.
2. **Repetitive rhetorical templates** — recurring paragraph shapes
   (topic sentence / generic explanation / broad benefit / restated claim);
   transition monoculture (Furthermore/Moreover/Additionally/Consequently);
   near-identical paragraph endings; repeated superiority restatements;
   uniform sentence rhythm; habitual three-item lists; "not only... but
   also" chains; over-symmetrical phrasing.
3. **Polish without specificity** — fluent passages lacking numbers,
   conditions, mechanisms, citations, limitations, or a tie to a table,
   figure, or experiment. Polish is not the problem; polish that masks weak
   content is.
4. **Synonym churn** — one concept under many names
   (method/framework/model/architecture/scheme/strategy/mechanism;
   performance/efficacy/effectiveness/capability; renamed algorithmic
   components). One technically correct term, used consistently;
   `terminology_sheet.md` is the arbiter.
5. **Unnatural certainty** — proves / guarantees / always / universally /
   undoubtedly / clearly superior / completely eliminates / optimal /
   state-of-the-art. The blocked-wording machinery already gates some of
   these; the audit checks the rest against the evidence and scopes them.
   Never weaken a claim the evidence genuinely supports.
6. **Inflated novelty** — "for the first time", "completely novel paradigm",
   "revolutionary", "groundbreaking", "unprecedented", "unique". Priority
   claims need documentary support; otherwise recommend precise contribution
   language. (This manuscript's contribution language is registered — verify
   it has not drifted toward inflation, and equally that no fix has deflated
   a demonstrated claim.)
7. **Artificially balanced or exhaustive prose** — exhaustive application
   lists; every paragraph with exactly three benefits; conclusions replaying
   every section in order; literature reviews as mechanical summaries rather
   than critical synthesis.
8. **Voice and quality discontinuities** — abrupt shifts in terminology,
   English proficiency, sentence complexity, formatting, citation density,
   voice, notation, or technical depth. State the plausible non-misconduct
   explanations (multiple authors, revision history, translation, editorial
   passes) and recommend harmonization; never infer misconduct from
   discontinuity.
9. **Unsupported table interpretation** — robustness from one metric;
   superiority without a valid test; small deltas called substantial;
   losses ignored; favorable dimensions cherry-picked; "consistent" over
   materially varying results; "significant" without a significance test.
   The §10 statistical-scope rules are the binding instantiation.
10. **Generic conclusion and future work** — conclusion repeating the
    abstract; new claims at the end; promotional closings; omitted
    limitations; future work disconnected from observed results. Future-work
    items must trace to observed limitations (the A-1/A-2 addendum rows are
    the sanctioned pattern).

#### 18.4.2 Revision principles

For each flagged passage: identify the exact problem; explain why it reads
generic, formulaic, or disconnected; identify the scientific content that
belongs there; provide a revision grounded in the actual method or evidence
(or a placeholder per §18.5 Part E when the fact is the author's to supply);
preserve uncertainty and limitations; never fix by stylistic variation alone.

#### 18.4.3 Required outputs

(1) The Part-F pattern register (schema in §18.5) with per-hit risk
Low/Moderate/High — cumulative and contextual, never treated as proof.
(2) A repeated-phrase inventory: transitions, sentence openers, conclusion
phrases, superiority claims, novelty expressions, generic benefit statements,
exploration–exploitation claims, robustness statements, future-work phrases —
with frequencies and locations. (3) A voice-discontinuity list with
non-misconduct explanations and harmonization actions. (4) One overall
authenticity-risk rating (Low / Moderate / High / Very high) with its
reasoning, plus the explicit reminder that style alone can neither prove nor
disprove authorship.

### 18.5 Output contract — the original's Parts A–N on house artifacts

| Part | Content (original) | House disposition |
|---|---|---|
| A | Executive verdict, weakness headliners, authenticity risk, finding counts | header of the dated panel register + §12 report |
| B | Claim–evidence map (ID / claim / location / evidence / strength / missing / action) | cross-check against `claims_evidence_matrix.csv`; report only deltas and gaps |
| C | Critical+Major findings, full schema | §5 ticket schema + fix_class + freeze consequence (§18.2(d)) |
| D | Section-by-section review incl. sections needing no change | §12 format; "reviewed, no substantive change" entries are mandatory, with reasons |
| E | Line-by-line change register | schema retained (Change ID / doc / location / original / problem / explanation / severity / priority / action / replacement); no meaning-obscuring ellipses; whole-paragraph rebuilds say so and give the paragraph; unresolved facts get explicit placeholders (`[INSERT VERIFIED ...]`) that are NEVER invented |
| F | Authenticity pattern register + phrase inventory + discontinuities | §18.4.3 |
| G | Main–supplement consistency matrix | schema retained; validators first (§18.3 Pass 5) |
| H | Math/algorithm audit table | five-value verification vocabulary (§18.3 Pass 4) |
| I | Experimental/statistical audit table | §10-bound; CSVs only |
| J | Citation audit, seven subsections | closed-corpus rules (§18.2(b)); "requires verification", never "fabricated", absent proof |
| K | Rewritten high-risk passages | proposals-only for frozen/registered text (§18.2(i)); §18.6 standards |
| L | Four-stage prioritized revision plan | stages retained (integrity → methodology/reproducibility → structure/argument → language), with the house rule: all manuscript-voiding fixes BATCH into one anchor commit per re-mint cycle; each action carries dependencies and completion evidence |
| M | Author verification checklist | retained; every item maps to an author-side or repo-verifiable check; "every sentence understood and defendable by the authors" is the closing item |
| N | Final readiness statement | §6 band + remaining blockers + submission conditions + whether another cycle is needed + the authenticity tri-state (author-grounded / mostly authentic but formulaic in places / heavily generic) + the style-proves-nothing reminder |

### 18.6 Editing decision hierarchy and replacement-text standards

Decision hierarchy (in order): factual/scientific correctness → logical
correctness → missing evidence or qualification → contradictions → paragraph
structure → sentence clarity → redundancy → grammar/punctuation →
style/formatting harmony. Elegant prose never outranks accuracy.

For a sentence mixing valid and invalid content: preserve the valid part,
remove or qualify the invalid part, add an evidence placeholder where
required, and explain the change. For genuinely ambiguous text: state both
readings, identify the wording that causes the ambiguity, and revise to
remove it — never assume the intended reading.

All replacement text must be: technically accurate; direct; evidence-based;
grammatically correct; journal-appropriate; free of hype and vague praise;
terminologically and tense-consistent; scoped to the actual experiments;
defendable by the authors. Do not homogenize every sentence into one polished
register; do not introduce variation to imitate humanity; do not prefer rare
synonyms over standard technical terms; do not replace field terminology
because it recurs. House additions: registered verbatims are untouchable
(§18.2(a)); preserve every registered hedge and limitation; preserve the
negative-result framing (the ISM null is advertised by design).

### 18.7 The eighteen-question battery

Answer all, explicitly, before the report closes: (1) the actual contribution
in one precise sentence; (2) whether it genuinely differs from the closest
prior work; (3) which contribution claims are experimentally demonstrated;
(4) which are only argued or assumed; (5) whether the method addresses the
stated gap; (6) whether the comparisons are fair; (7) whether conclusions are
statistically AND practically justified; (8) whether the work is reproducible
from the committed artifacts — including the committed-blob check, not only
the working tree; (9) whether the main paper and supplement describe the same
study; (10) whether anything central is hidden in the supplement; (11)
whether any numerical results contradict; (12) whether any references are
questionable within the closed corpus; (13) which passages read generic or
mechanically produced; (14) what scientific weakness sits beneath each such
passage; (15) whether the authors could defend every sentence orally; (16)
the five most likely rejection reasons, mapped to the §14 pattern list; (17)
the exact revisions that most improve acceptance probability; (18) whether
the manuscript demonstrates authentic scientific reasoning rather than
generic academic language.

### 18.8 Detail standard

No summary reviews. Every problem carries: exact location (file:line or
document/section/paragraph-opening-words plus exhibit identifier — never
"somewhere in the methodology"); the problem; the explanation; the
consequence; severity, priority, confidence, fix class; the required change;
replacement text where textual; all locations needing synchronized revision;
and the author verification required. Repeated errors are reported as one
global pattern WITH every affected location enumerated. Unrelated issues are
never bundled to shorten the report. The §15 prohibited-shortcuts list
applies to this layer in full.

<!-- END OF COMPREHENSIVE MANUSCRIPT REVIEW PROMPT -->
