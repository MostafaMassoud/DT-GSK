# Stage 16 — Ethics, Research-Integrity and Publication-Practice Audit

**Seat:** `s16_ethics_ai` (T6-INTEG, role RI)
**Review date:** 2026-07-22
**Package audited (verified against the repo, not from memory):**

| Variable | Value verified this session |
|---|---|
| `git HEAD` | `45248eb31af7b01567c251f2a5da4f36e92d6030` (`git rev-parse HEAD`) |
| `authoritative_commit` (submission manifest) | `abd2fa2f25c8426247b43c85bcb3d82041d00976` |
| `evidence_release` | `rel-2026-07-20-67d9345f9` |
| `PDF_OUTPUT` | `papers/DT-GSK.pdf`, 39 pp (pypdf page count) |
| `SUPPLEMENTARY_FILE` | `papers/supplementary.pdf`, 61 pp; `papers/supplementary.docx` |
| `WORD_OUTPUT` | `papers/DT-GSK.docx` (138 940 extracted chars) |
| Cover letter | `papers/cover_letter.pdf`, 2 pp, dated 25 July 2026 |
| `TARGET_JOURNAL` | *Algorithms* (MDPI) |
| Remediation ledger | `papers/governance/remediation_2026_07_18/ticket_status.csv` — **80/80** rows terminal (70 `closed_verified`, 10 `superseded_with_evidence`, **0 open**) |
| Public artifact repository | `https://github.com/MostafaMassoud/PhD-Projects` — **confirmed publicly viewable 2026-07-22** |

**Scope note.** This seat covers ethics, research integrity, publication practice, and the
GenAI disclosure checks D16.1–D16.6. The GenAI checks are recorded in the companion artifact
`papers/review_2026_07_22/ai_disclosure_audit.md` (Appendix A.10 schema); this file records the
ethics and integrity matrix and the non-GenAI tickets. Nothing in this review used or requested an
AI-writing-detector score as a quality gate (§15 prohibition), and no misconduct is alleged
anywhere in this document. Every finding below is a **disclosure-accuracy or record-completeness**
defect, evidenced by file:line or command output.

---

## 1. Ethics and integrity matrix

Legend: **PASS** = verified compliant · **FAIL** = verified defect · **BLOCKED** = cannot be
closed without author-supplied information or a tool this panel does not have · **N/A** = not
applicable to this study type.

| # | Requirement | Verdict | Evidence | Required author confirmation |
|---|---|---|---|---|
| 1 | Ethics committee / IRB approval | **N/A (correctly declared)** | `papers/main.tex:221` `Institutional Review Board Statement. Not applicable.`; renders in PDF (p. 38) and DOCX (¶1416). Purely computational benchmark study; no human/animal subjects. | None |
| 2 | Informed consent | **N/A (correctly declared)** | `papers/main.tex:224`; renders in PDF and DOCX (¶1418). | None |
| 3 | Privacy / de-identification / data protection | **N/A** | No personal data collected. All released CSVs are optimizer traces. | None |
| 4 | Human / animal / clinical / sensitive / proprietary / indigenous data | **N/A** | CEC2017, CEC2011 and CEC2013 are synthetic and engineering-parameter suites; no proprietary datasets are redistributed (`git ls-files benchmarks/cec_suite_python` = 59 files, all code). | None |
| 5 | Prospective / trial registration | **N/A** | Not a clinical study. *Positive note:* the project operates a frozen analysis plan and a hash-locked evidence release, which is functionally stronger than the norm for this literature. | None |
| 6 | Biosafety / dual-use / security | **N/A** | Bound-constrained numerical optimization; no dual-use surface. | None |
| 7 | Author qualification and contribution statement | **BLOCKED** | CRediT block present (`papers/main.tex:209-215`) and renders in both formats. But `papers/main.tex:202` asserts "CRediT roles CONFIRMED by the authors (2026-07-13)" while `papers/governance/administrative_gap_register.md:10` still records AG-0001 as *"CRediT split … to be confirmed before submission"*, and `papers/governance/decision_log.md:358-360` (D-0012, **same date 2026-07-13**) states these facts "are NOT decided here and remain open". See **S16-E-01**. | Written confirmation of the CRediT split, esp. H.S.M.R. |
| 8 | Ghost / guest / omitted authorship risk | **BLOCKED (moderate)** | H.S.M.R.'s sole CRediT role is *writing — review and editing* (`papers/main.tex:212-213`); she is also a co-author of `jawad2024egsk`, the comparator that beats DT-GSK at D=30 and on CEC2011. The combination is defensible under ICMJE criterion 2 but is not evidenced in the package. See **S16-E-05**. No AI system is listed as an author anywhere (verified in `\Author{}` `papers/main.tex:101`, PDF title page, DOCX, `CITATION.cff`) — D16.2 PASS. | Confirm each author meets all four ICMJE criteria |
| 9 | Conflicts of interest | **BLOCKED (content is exemplary)** | `papers/main.tex:288-298` discloses that A.W.M. originated baseline GSK and co-authored AGSK/APGSK/eGSK/ATMALS-GSK, that H.S.M.R. co-authored eGSK, and that M.E.M. is A.W.M.'s PhD student. This is unusually candid and is the correct disclosure. **But** `papers/main.tex:286-287` marks the wording "drafted-unconfirmed; requires author confirmation", AG-0004 is `open`, and D-0012 lists COI as not decided. See **S16-E-01**. Separately: no evidence found that any author sits on the *Algorithms* editorial board (web check 2026-07-22, negative), but one comparator (`alfadli2025atmals`, *Algorithms* 18(7):398) was published in the target journal by A.W.M. — worth a line in the submission-form COI field. | Author sign-off on the COI text; declaration of any editorial-board/guest-editor role at MDPI |
| 10 | Funding and sponsor role | **BLOCKED** | `papers/main.tex:218` `\funding{This research received no external funding.}` and `:296-298` ("no funding body influenced …"). `papers/main.tex:217` claims author confirmation 2026-07-13; AG-0003 is still `open` and D-0012 contradicts it. See **S16-E-01**. | Written confirmation of "no external funding" from all three authors / institutions |
| 11 | Duplicate submission / redundant publication | **BLOCKED (declared, unverifiable here)** | `papers/cover_letter.tex:59` declares originality and no concurrent submission. No preprint/arXiv record exists in the repo. Not independently verifiable by this panel. | Confirm no preprint, and declare any PhD-thesis chapter overlap (M.E.M. is a doctoral candidate) |
| 12 | Salami slicing | **PASS** | The removed oracle/estimator study and the BLADE forks were deleted from the project (`7dbb4bceb`), not spun out; the supplement carries the component work rather than a second paper. No fragmentation observed. | None |
| 13 | Plagiarism / patchwriting | **BLOCKED** | No similarity-screening record exists in the package (`grep -rn -i "ithenticate\|turnitin\|copyleaks"` over `papers/` and `docs/` returns only policy prose). The project's own round-1 review flagged this: `papers/governance/REVIEW_2026-07-13_round1_report.md:70` — *"MIN-11 Self-citation/text-recycling exposure (A.W.M. co-authored 5/6 comparators) — run iThenticate pre-submission"*. Exposure is real: `papers/sections/related_work.tex` paraphrases six family papers, five of them by the authors. See **S16-E-06**. | Run a pre-submission similarity report and archive it |
| 14 | Citation manipulation | **PASS (with note)** | 9 of 57 bib entries are A.W.M.-authored (15.8 %): `mohamed2020gaining, mohamed2020agsk, apgsk2021, mohamed2021novel, mohamed2017lshadespacma, jawad2024egsk, alfadli2025atmals, chalabi2023mogsk, nomer2021gskrl`. For a study whose entire scope is *the GSK family he founded*, this is proportionate, not coercive. Exactly one citation to the target journal (`alfadli2025atmals`) — no coercive-citation pattern. | None |
| 15 | Image or data manipulation | **PASS** | Every figure is script-generated from the frozen release (`papers/scripts/generate_*.py`, `papers/governance/table_figure_source_map.csv`); no photographic or gel-type imagery exists, so the Proofig-class risk surface is empty. | None |
| 16 | Undisclosed exclusions / result switching | **PASS (exemplary)** | Adverse and missing-data facts are disclosed *in the abstract and cover letter*, not buried: the ISM isolation null (`papers/main.tex` abstract; `papers/cover_letter.tex:53`), the Holm-significant D=30/CEC2011 loss to eGSK, the APGSK per-run availability gap (PDF p. 24 + footnote 1), and CEC2017 configuration-selection exposure. This is the strongest integrity feature of the package. | None |
| 17 | Retractions / corrections / expressions of concern in cited work | **PASS** | All 51 DOI-bearing bib entries queried against the Crossref REST API on 2026-07-22 (`api.crossref.org/works/{doi}`): **49 resolved, 0 carrying any `updated-by` retraction/correction/EoC marker, 0 of type `retraction`**. 2 returned HTTP 404 — those are DOI-accuracy defects, see row 18. | None |
| 18 | Reference accuracy (fabricated/erroneous-reference screen) | **FAIL** | Two DOIs in `papers/references.bib` do not resolve at the DOI handle API (verified 2026-07-22, `doi.org/api/handles/…` → 404): (a) **rendered in the PDF bibliography as reference 27** — `kolda2003directsearch`, `papers/references.bib:613`, prints `doi:10.1137/S0036144502428893`; the correct DOI is `10.1137/S003614450242889` (Crossref: *Optimization by Direct Search…*, SIAM Review — resolves, handle responseCode 1). (b) uncited entry `zhou2021iade`, `papers/references.bib:379`, `10.1109/TGCN.2021.3104883`; the correct DOI is `10.1109/TGCN.2021.3111909` (Crossref title/volume/page match). See **S16-E-04**. | None (mechanical fix) |
| 19 | Software / dataset / figure licenses | **FAIL (minor)** | `papers/main.tex:246-252` states the licence position as settled (MIT for code, CC BY 4.0 for derived data, upstream terms for CEC definitions) and this matches `docs/LICENSES.md`. But `docs/LICENSES.md` "Before publication or redistribution" items **1** (confirm the copyright line) and **3** (reconcile Attribution with the originating research codebase) are still open TODOs in the shipped file, and `src/gsk_family/optimizers/fdb_agsk.py:1` carries no attribution to Bakir et al. or to the source MATLAB — contrast `src/gsk_family/optimizers/egsk.py:1-8`, which does it correctly. See **S16-E-07**. Third-party paper PDFs are correctly **not** committed (`git ls-files reference_papers/` = 3 files, all metadata). | Confirm the copyright line / rights-holder |
| 20 | Generative-AI disclosure required by the journal | **FAIL** | See `ai_disclosure_audit.md`. Headline: the affirmative exclusion "the algorithm design, **its implementation**, the experimental protocol, and every reported number … [was produced] **independently of any AI system**" (`papers/main.tex:265-271`) is contradicted by the public repository that the Data Availability Statement designates as the artifact home. **S16-AI-01**, Critical. | Restate the scope of AI assistance accurately; name every tool/version |
| 21 | Truthful data / code availability claim | **FAIL / BLOCKED** | `papers/main.tex:227-231` asserts the artifacts "are publicly available in the DT-GSK repository" but prints **no URL and no DOI**, and no repository by that name exists: the actual public host is `https://github.com/MostafaMassoud/PhD-Projects` (a multi-project doctoral workspace, 2 156 commits), with DT-GSK at `00-GSK-Family/02-GSK_Family_Python_v1.1`. AG-0006 (`administrative_gap_register.md:15`) leaves the durable archive URL/DOI open. See **S16-E-02**. Gate O fails explicitly for an inaccurate availability statement. | Mint a Zenodo (or equivalent) DOI for the release and print a resolvable locator |
| 22 | Rendered placeholders in submission artifacts | **FAIL (upload block)** | The submitted PDF title page (p. 1, lines 6–7) and the DOCX print `[H.S.M.R. institutional e-mail — to be added at submission]` (`papers/main.tex:112`). Honest and clearly marked — the correct choice over fabrication — but it blocks upload. ORCIDs are `0000-0000-0000-0000` placeholders at `papers/main.tex:96-98`; **verified they do not render** (the `\Author{}` macro does not reference them), so no fabricated identifier reaches the PDF. See **S16-E-03**. | Real institutional e-mail + three real ORCID iDs |

**Matrix roll-up:** 6 PASS · 6 N/A · 5 FAIL · 6 BLOCKED (author-side).

---

## 2. Gate O — Ethics and Publication Integrity

**Verdict: FAIL (scientific integrity of the disclosure) + BLOCKED (administrative).**

Gate O fails on two of its own enumerated triggers:

1. *"GenAI under-disclosure relative to the verified venue policy"* — **S16-AI-01** / **S16-AI-02**.
2. *"inaccurate availability statement"* — **S16-E-02**.

and is additionally BLOCKED on *"required author confirmation"* for funding, COI, CRediT and the
GenAI tool inventory (**S16-E-01**).

Gate O does **not** fail for: a named AI author (none — D16.2 PASS), manipulated evidence (none
found), an unresolved plagiarism concern (none raised; screening merely not yet run), a fabricated
declaration (no fabricated value found — every unknown is an explicitly marked placeholder), or a
detector-based misconduct allegation (none made).

**Minimum path to Gate O PASS.** All of it is text-and-record work; none of it requires a rerun,
a new evidence release, or any change to the byte-locked optimizer core.

1. Rewrite the three GenAI loci so the exclusion is scientifically accurate (S16-AI-01) and names
   every tool/version that appears in the public history (S16-AI-02).
2. Print a resolvable repository URL + archive DOI in the Data Availability Statement (S16-E-02).
3. Obtain and **record in `administrative_gap_register.md`** the author confirmations for AG-0001,
   AG-0003, AG-0004, AG-0005, AG-0007 (S16-E-01), and remove the contradictory in-source
   "CONFIRMED (2026-07-13)" comments or make them point at the recorded confirmations.
4. Replace the placeholder e-mail and the placeholder ORCIDs (S16-E-03).
5. Fix the two DOIs (S16-E-04).
6. Run and archive a similarity report (S16-E-06).

---

## 3. Tickets (§5.4 schema)

### S16-E-01 — Administrative declarations asserted as author-confirmed are recorded as unconfirmed

```text
ticket_id: S16-E-01
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Major
priority: P1
confidence: CONFIRMED
issue_type: ethics
manuscript_location: papers/main.tex:180-183, :202, :217, :255-258, :275-276, :286-287
claim_id_or_artifact_id: AG-0001, AG-0003, AG-0004, AG-0007
concise_issue: main.tex simultaneously states that nothing in the back matter closes an open
  administrative-gap row AND that four specific rows were author-confirmed on 2026-07-13; the
  governance package of record says they are not confirmed.
exact_evidence_or_observation:
  papers/main.tex:180-183 -- "Administrative metadata per papers/governance/
    administrative_gap_register.md: nothing below closes an open AG row; drafted-unconfirmed
    items are flagged in comments and require author confirmation before submission
    (AG-0001..AG-0007)."
  CONTRADICTED IN THE SAME FILE BY:
  papers/main.tex:202 -- "Author Contributions: CRediT roles CONFIRMED by the authors (2026-07-13)."
  papers/main.tex:217 -- "AG-0003: funding CONFIRMED by the authors (2026-07-13): no external funding."
  papers/main.tex:255-258 -- "Author-confirmed (2026-07-13): tool = Claude Opus 4.8 (Anthropic);
    use = language editing AND drafting of descriptive text"
  papers/main.tex:275-276 -- "version pinned to Claude Opus 4.8 (author-confirmed 2026-07-13)."
  AND BY THE GOVERNANCE RECORD OF THE SAME DATE:
  papers/governance/decision_log.md:354  -- "D-0012 (2026-07-13)"
  papers/governance/decision_log.md:358-360 -- "author-side *facts* (ORCID, DOI, e-mail, CRediT
    split, GenAI version, licenses, funding, COI) are NOT decided here and remain open in
    administrative_gap_register.md (AG-0001..0007)."
  papers/governance/decision_log.md:392-396 -- lists AG-0001, AG-0003, AG-0004, AG-0007 as
    "Author-facts still open".
  papers/governance/decision_log.md:454-455 -- "Deferred / open: A1.T5 author-fact metadata
    (DOI/CRediT/GenAI) remains blocked on author input (AG-0001..0007)".
  papers/governance/administrative_gap_register.md:10-14 -- AG-0001 "narrowed", AG-0003 "open"
    (Statement UNCONFIRMED by the authors/institution), AG-0004 "open" (Wording and completeness
    UNCONFIRMED by the authors), AG-0007 "open".
  The register's own closure rule (administrative_gap_register.md:17-19): "each row closes only
    with an explicit author-provided value recorded here (with date)". No such record exists.
root_cause: Author confirmations were (plausibly) given in conversation and written into the
  LaTeX source as comments, but never propagated to the register that the project designates as
  the sole closure locus; the register and the decision log were not updated.
scientific_or_editorial_justification: Section 16 forbids inventing a funding source, contributor
  role, or conflict statement, and treats missing verified administrative information as a block
  on upload readiness. A declaration whose confirmation cannot be evidenced is exactly that block.
impact_on_validity_or_acceptance: No effect on the science. Blocks Gate O and upload readiness;
  a publisher query on the funding or COI statement would have no auditable answer.
required_correction: Record each confirmation (item, exact wording, confirming author, date) in
  administrative_gap_register.md and set the row status; then either delete the in-source
  "CONFIRMED" comments or rewrite them to cite the register row. Resolve the main.tex:180-183 vs
  :202/:217/:255-258/:275-276 contradiction in one direction.
acceptable_alternatives: If confirmations have NOT in fact been obtained, keep the statements but
  mark them unconfirmed in the ledger and treat submission as blocked until they are.
additional_evidence_needed: Author sign-off on funding, COI wording, CRediT split, GenAI tool list.
dependencies: S16-AI-02 (the GenAI tool inventory to be confirmed is itself incomplete).
expected_improvement: Gate O administrative BLOCKED -> PASS; removes a desk-query risk.
post_revision_verification: grep main.tex for "CONFIRMED by the authors" and check every hit
  resolves to a dated row in administrative_gap_register.md; confirm no AG row remains "open" that
  the manuscript asserts as closed.
status: open
```

### S16-E-02 — Data Availability Statement claims public availability with no resolvable locator

```text
ticket_id: S16-E-02
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Major
priority: P1
confidence: CONFIRMED
issue_type: compliance
manuscript_location: papers/main.tex:227-252; DT-GSK.pdf p.38; DT-GSK.docx paragraph 1420-1422
claim_id_or_artifact_id: CN-02; AG-0006
concise_issue: The statement asserts artifacts are "publicly available in the DT-GSK repository"
  but prints no URL and no DOI, and no repository of that name exists.
exact_evidence_or_observation:
  papers/main.tex:227-231 -- "... are publicly available in the DT-GSK repository."
  papers/main.tex:232-233 -- "% AG-0006 / R-0004: the durable archive URL/DOI and the submission
    account are author-side items; do not fabricate a URL here."
  `git remote -v` -> origin https://github.com/MostafaMassoud/PhD-Projects.git
  Fetched 2026-07-22: that repository IS public, but it is a multi-project doctoral workspace
    (top-level 00-GSK-Family, 00-Papers, MATLAB and Python trees, 2156 commits on main); DT-GSK
    lives at 00-GSK-Family/02-GSK_Family_Python_v1.1. There is no "DT-GSK repository".
  papers/governance/administrative_gap_register.md:15 -- AG-0006 open.
  No Zenodo/figshare DOI anywhere in the package.
root_cause: The durable-archive step was correctly deferred as an author-side item and never done;
  the prose was written as if it had been.
scientific_or_editorial_justification: MDPI requires a data-availability statement that lets a
  reader actually reach the data. Gate O fails explicitly for an inaccurate availability statement.
impact_on_validity_or_acceptance: High desk-risk. The whole reproducibility contribution (C3) rests
  on the reader being able to reach the release; an unreachable locator undercuts the paper's
  strongest claim.
required_correction: Deposit the release (or a manifest-verified snapshot) in a DOI-issuing archive
  and print "available at <URL> (DOI: <doi>)"; correct "the DT-GSK repository" to the true path.
acceptable_alternatives: Print the GitHub URL plus the exact subdirectory and the anchor commit
  67d9345f9502a9a584e645fa8948f60a61d70e29 if a DOI cannot be minted before submission.
additional_evidence_needed: The archive DOI.
dependencies: none
expected_improvement: Gate O availability trigger cleared; C3 becomes reader-verifiable.
post_revision_verification: Resolve the printed URL/DOI from a clean network session and confirm
  the manifest checksums match.
status: open
```

### S16-E-03 — Rendered placeholder in the submitted title page

```text
ticket_id: S16-E-03
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Major (upload readiness; administrative, not scientific)
priority: P1
confidence: CONFIRMED
issue_type: compliance
manuscript_location: papers/main.tex:112 ; DT-GSK.pdf p.1 lines 6-7 ; DT-GSK.docx
claim_id_or_artifact_id: AG-0002, AG-0005
concise_issue: A bracketed placeholder for the second author's e-mail is typeset on the title page
  of both submission deliverables.
exact_evidence_or_observation:
  papers/main.tex:112 -- "moustafa.masoud@gmail.com (M.E.M.); [H.S.M.R.\ institutional e-mail ---
    to be added at submission] (H.S.M.R.); aliwagdy@gmail.com (A.W.M.)"
  DT-GSK.pdf extracted p.1: "... [H.S.M.R. institutional e-mail - to be added at submission]
    (H.S.M.R.); aliwagdy@gmail.com (A.W.M.)"
  papers/main.tex:96-98 -- \orcidauthorA/B/C = 0000-0000-0000-0000. VERIFIED these do NOT render
    (the \Author{} macro at :101 does not reference them), so no fabricated ORCID reaches the PDF.
  The two rendered author e-mails are personal Gmail addresses against institutional affiliations.
root_cause: AG-0002/AG-0005 author-side items still open.
scientific_or_editorial_justification: Not fabrication -- the marked placeholder is the correct
  handling of an unknown -- but MDPI requires a contact e-mail and ORCID for each author.
impact_on_validity_or_acceptance: Certain editorial query or desk return if uploaded as-is.
required_correction: Insert H.S.M.R.'s institutional e-mail and the three real ORCID iDs.
acceptable_alternatives: none (values cannot be invented).
additional_evidence_needed: Author-supplied e-mail and ORCIDs.
dependencies: S16-E-01 (record the values in the gap register when supplied).
expected_improvement: Removes the last rendered placeholder from the submission set.
post_revision_verification: Re-extract PDF page 1 and grep for "[" / "0000-0000".
status: open
```

### S16-E-04 — Non-resolving DOI in the rendered bibliography

```text
ticket_id: S16-E-04
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Major
priority: P2
confidence: CONFIRMED
issue_type: citation
manuscript_location: papers/references.bib:613 (rendered as reference 27 in DT-GSK.pdf);
  papers/references.bib:379 (uncited entry)
claim_id_or_artifact_id: kolda2003directsearch ; zhou2021iade
concise_issue: A DOI printed in the reference list does not resolve; a second, uncited entry
  carries a different non-resolving DOI.
exact_evidence_or_observation:
  Rendered PDF reference 27: "Kolda, T.G.; Lewis, R.M.; Torczon, V. Optimization by Direct Search:
    New Perspectives on Some Classical and Modern Methods. SIAM Review 2003, 45, 385-482.
    doi:10.1137/S0036144502428893."
  Verified 2026-07-22:
    api.crossref.org/works/10.1137/S0036144502428893  -> HTTP 404
    doi.org/api/handles/10.1137/S0036144502428893     -> HTTP 404
    api.crossref.org/works/10.1137/S003614450242889   -> OK, "Optimization by Direct Search: New
      Perspectives on Some Classical and Modern Methods", SIAM Review
    doi.org/api/handles/10.1137/S003614450242889      -> responseCode 1 (resolves)
  i.e. the printed DOI carries one spurious trailing digit.
  Uncited entry papers/references.bib:379 zhou2021iade doi 10.1109/TGCN.2021.3104883 -> 404 at both
    Crossref and the DOI handle API; Crossref bibliographic search returns the correct DOI
    10.1109/TGCN.2021.3111909 (IEEE Trans. Green Commun. Netw. 5(4):1747-1760). Confirmed this
    entry is NOT cited (no occurrence of "3104883" or "IADE" in the extracted PDF text).
  Whole-bibliography sweep: 51 DOI-bearing entries queried at Crossref; 49 resolved with zero
    retraction/correction/expression-of-concern markers; only these two failed.
root_cause: Transcription error in two bib entries; no DOI-resolution check in the build gates.
scientific_or_editorial_justification: MDPI's Ethicality screen flags fabricated or manipulated
  references; a dead DOI in the printed list is a false-positive magnet and, independently, sends
  readers nowhere.
impact_on_validity_or_acceptance: No effect on results. Real integrity-screen and credibility risk.
required_correction: Set kolda2003directsearch doi = 10.1137/S003614450242889; set zhou2021iade
  doi = 10.1109/TGCN.2021.3111909 or delete the uncited entry; rebuild.
acceptable_alternatives: Drop the DOI field from the Kolda entry (the citation is otherwise complete
  and correct) -- inferior, since MDPI style prints DOIs.
additional_evidence_needed: none
dependencies: The rebuild re-triggers the manuscript freeze/manifest step.
expected_improvement: 51/51 DOIs resolve; reference-integrity screen clean.
post_revision_verification: Re-run the Crossref/handle sweep over papers/references.bib; require
  0 non-resolving DOIs. Recommend adding this as a build gate.
status: open
```

### S16-E-05 — Authorship-criteria evidence for the second author

```text
ticket_id: S16-E-05
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Moderate
priority: P2
confidence: SUSPECTED (needs author input; not verifiable from artifacts)
issue_type: ethics
manuscript_location: papers/main.tex:203-215 ; papers/governance/administrative_gap_register.md:10
claim_id_or_artifact_id: AG-0001
concise_issue: The second author's only recorded contribution is "writing -- review and editing",
  and the governance record still lists her CRediT split as unconfirmed.
exact_evidence_or_observation:
  papers/main.tex:212-213 -- H.S.M.R. appears only in "writing---review and editing".
  papers/main.tex:204-207 (comment) -- "H.S.M.R. contributes manuscript review, critical revision,
    and language editing (writing--review & editing)".
  administrative_gap_register.md:10 -- AG-0001 "narrowed ... remaining: per-author CRediT role
    split (esp. H.S.M.R.) to be confirmed before submission".
  Context that a reviewer will notice: H.S.M.R. is a co-author of jawad2024egsk, the eGSK
    comparator that outranks DT-GSK at D=30 and on CEC2011 (papers/main.tex:291-292 COI).
root_cause: Author-side confirmation never recorded.
scientific_or_editorial_justification: ICMJE/COPE require substantial contribution AND drafting or
  critical revision AND approval AND accountability. Critical revision satisfies criterion 2, so
  the authorship is defensible -- but the package contains no evidence of criteria 1 and 4, and
  the reviewer-visible relationship to a comparator makes an unevidenced role a live question.
  This is NOT an allegation of guest authorship; it is a request for the standard confirmation.
impact_on_validity_or_acceptance: Low-moderate. An editor query is plausible.
required_correction: Record explicit confirmation that each listed author meets all four ICMJE
  criteria, and (if applicable) broaden H.S.M.R.'s CRediT roles to what she actually did.
acceptable_alternatives: Keep the single role if that is genuinely the contribution, with the
  criteria confirmation recorded.
additional_evidence_needed: Author statement.
dependencies: S16-E-01
expected_improvement: Closes AG-0001; removes an authorship query.
post_revision_verification: AG-0001 row shows a dated author-supplied value.
status: open
```

### S16-E-06 — No text-similarity screening record

```text
ticket_id: S16-E-06
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Moderate
priority: P2
confidence: CONFIRMED (absence verified); risk level SUSPECTED
issue_type: ethics
manuscript_location: package-level; papers/sections/related_work.tex
claim_id_or_artifact_id: MIN-11
concise_issue: The package contains no similarity report, and the project's own earlier review
  identified a specific text-recycling exposure that was never screened.
exact_evidence_or_observation:
  papers/governance/REVIEW_2026-07-13_round1_report.md:70 -- "MIN-11 Self-citation/text-recycling
    exposure (A.W.M. co-authored 5/6 comparators) -- run iThenticate pre-submission; add
    self-cites at any reused phrasing."
  grep -rn -i "ithenticate|turnitin|copyleaks|proofig" over papers/ and docs/ returns only policy
    prose (administrative_gap_register.md:14, instruction_precedence.md) -- no run record.
  papers/sections/related_work.tex describes six family algorithms, five authored/co-authored by
    the present authors; MIN-11 was never re-verified after the Phase 8 rewrite.
root_cause: Screening is a pre-submission author-side action; it was scheduled and not performed.
scientific_or_editorial_justification: MDPI runs iThenticate on every submission. Self-plagiarism
  in a related-work section describing one's own prior algorithms is the single most likely source
  of a similarity flag in this manuscript, and it is cheap to pre-empt.
impact_on_validity_or_acceptance: Moderate. A high similarity index triggers an integrity query
  even when every reused sentence is properly cited.
required_correction: Run a similarity check before upload; where phrasing is reused from the
  authors' own prior papers, cite the source explicitly or paraphrase; archive the report.
acceptable_alternatives: Institutional Turnitin/iThenticate access if available.
additional_evidence_needed: The report.
dependencies: none
expected_improvement: Converts an unknown into a documented, defensible number.
post_revision_verification: Archived report with an access date in papers/governance/.
status: open
```

### S16-E-07 — Open licensing TODOs and a missing port attribution in the public code

```text
ticket_id: S16-E-07
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Moderate
priority: P2
confidence: CONFIRMED
issue_type: compliance
manuscript_location: papers/main.tex:246-252 ; docs/LICENSES.md ; src/gsk_family/optimizers/fdb_agsk.py:1
claim_id_or_artifact_id: CN-02
concise_issue: The manuscript states the licence position as settled while the licence file it
  points at still carries unactioned pre-publication TODOs, and one third-party algorithm port
  ships without source attribution.
exact_evidence_or_observation:
  papers/main.tex:246-252 -- "The released DT-GSK code is distributed under the MIT License (see
    the repository LICENSE file), and our own derived data and analysis artifacts under ...
    CC BY 4.0 ...; the CEC2017/CEC2011/CEC2013 benchmark definitions remain under their respective
    upstream terms."
  docs/LICENSES.md "Before publication or redistribution": item 1 "Confirm the copyright line and
    year ... against the final author list"; item 3 "Reconcile the Attribution section with the
    originating research codebase and benchmark suite license/citation statements." Both still
    open. Header note: "verify copyright line before final submission".
  src/gsk_family/optimizers/fdb_agsk.py:1 -- docstring is """FDB-AGSK optimizer.""" only; no
    attribution to Bakir, Duman, Guvenc & Kahraman (2023) or to the source MATLAB.
    Contrast src/gsk_family/optimizers/egsk.py:1-8, which names the MATLAB source files, the
    authors and the DOI -- the correct pattern.
  Positive: reference_papers/*.pdf are NOT committed (git ls-files reference_papers/ = 3 metadata
    files), so no third-party copyrighted PDFs are redistributed. Verified.
root_cause: Pre-publication licence checklist not executed; one port header written tersely.
scientific_or_editorial_justification: The manuscript makes a licence assertion about a public
  repository; the repository's own licence file says the assertion is not yet verified. FDB-AGSK
  is the one comparator authored by an independent third party, so it is the one whose attribution
  matters most.
impact_on_validity_or_acceptance: Low for acceptance, non-trivial for post-publication rights.
required_correction: Execute docs/LICENSES.md items 1 and 3 and delete them from the TODO list;
  add an attribution docstring to fdb_agsk.py naming Bakir et al. (2023) and the MATLAB source.
acceptable_alternatives: none
additional_evidence_needed: Institutional rights-holder position (if any).
dependencies: S16-E-01 (copyright line is an author-side fact).
expected_improvement: Licence claim in the paper becomes true of the repository as shipped.
post_revision_verification: docs/LICENSES.md carries no open pre-publication items; grep each
  optimizer module for a source-attribution header.
status: open
```

### S16-E-08 — Governing prompt §1.5 is stale relative to the repository (recorded per instruction)

```text
ticket_id: S16-E-08
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Moderate
priority: P2
confidence: CONFIRMED
issue_type: compliance
manuscript_location: papers/PAPER_REVIEW_PROMPT.md §1.5 (line 118 ff., dated 2026-07-20)
claim_id_or_artifact_id: remediation ledger
concise_issue: The review prompt's embedded status snapshot understates ledger closure and
  predates the R-01..R-14 remediation entirely.
exact_evidence_or_observation:
  PAPER_REVIEW_PROMPT.md §1.5 -- "the 80-ticket remediation ledger ... stands at 73/80 fully
    closed ... and seven terminal / machine-gated / author-gated tickets remain open (RT-001 the
    live runtime blocker; C-008 -> C-001 the terminal freeze+commit; N-009 / N-021 / M-007 / E-012
    partial-or-author)".
  Repository now (papers/governance/remediation_2026_07_18/ticket_status.csv, 80 rows):
    Counter({'closed_verified': 70, 'superseded_with_evidence': 10}) -- ZERO open.
    N-009 closed_utc 2026-07-21; N-021 closed_utc 2026-07-21; M-007 closed_utc 2026-07-21.
  §1.5 contains no reference to R-01..R-14 (the 2026-07-21/22 remediation), and no mention of
    tests/regression/test_budget_crossing_semantics.py.
root_cause: The prompt's snapshot was written 2026-07-20 and not refreshed after the 07-21/22 work.
scientific_or_editorial_justification: §1.4 precedence puts current project state above the
  prompt's embedded snapshot; a stale snapshot risks a reviewer re-opening closed tickets or
  reporting phantom blockers.
impact_on_validity_or_acceptance: None on the manuscript. Governance-hygiene defect.
required_correction: Refresh §1.5 to the 80/80 state and record the R-01..R-14 pass, or stamp the
  section as historical and point to ticket_status.csv as authoritative.
acceptable_alternatives: Delete the embedded snapshot and require the panel to read the ledger.
additional_evidence_needed: none
dependencies: none
expected_improvement: Prompt and repository agree; no phantom blockers.
post_revision_verification: §1.5 counts match ticket_status.csv.
status: open
```

### S16-E-09 — Cover letter is forward-dated

```text
ticket_id: S16-E-09
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Editorial
priority: P3
confidence: CONFIRMED
issue_type: production
manuscript_location: papers/cover_letter.tex:35 ; papers/cover_letter.pdf p.1
claim_id_or_artifact_id: -
concise_issue: The cover letter is dated 25 July 2026, three days after the review date and after
  the manuscript freeze.
exact_evidence_or_observation: papers/cover_letter.tex:35 -- "25 July 2026". Current date
  2026-07-22; freeze anchor abd2fa2f25c8 predates it. validate_document_consistency.py confirms
  the md/tex dates agree with each other, so both are forward-dated consistently.
root_cause: Date set to a planned submission date.
scientific_or_editorial_justification: Harmless if submission happens on that date; a letter dated
  after the actual upload date reads as careless.
impact_on_validity_or_acceptance: Negligible.
required_correction: Set the date to the actual submission date at upload.
acceptable_alternatives: none
additional_evidence_needed: none
dependencies: none
expected_improvement: Cosmetic.
post_revision_verification: Date equals upload date.
status: open
```

---

## 4. Verified-clean findings worth stating explicitly

An adversarial review should also record what it tried to break and could not.

- **No fabricated administrative value anywhere.** Every unknown is a marked placeholder or an
  explicit "do not fabricate" comment (`main.tex:94-95`, `:107`, `:232-233`). This is the correct
  behavior and the reason S16-E-01/03 are *blocks*, not integrity failures.
- **No AI author.** Verified in `\Author{}`, `\AuthorNames{}`, the PDF title page, the DOCX, and
  `CITATION.cff`. D16.2 PASS.
- **No retracted or corrected reference.** 49/51 DOIs verified live at Crossref with zero update
  markers.
- **No third-party copyrighted PDFs in the public repository.** `reference_papers/*.pdf` are
  untracked; `docs/LICENSES.md` states the policy explicitly and it is honored.
- **Adverse results are advertised, not buried.** The ISM null is in the abstract, the conclusions
  and the cover letter; the eGSK D=30/CEC2011 loss is in the abstract. Under an integrity rubric
  this is the package's strongest feature and should be preserved verbatim through any revision.
- **The already-remediated items in this seat's lane were closed correctly.** R-09: the cover
  letter's rendered text contains no reviewer placeholder (verified by extracting
  `cover_letter.pdf`: 0 occurrences of "Reviewer"; the surviving `% AUTHOR-FILL` block at
  `cover_letter.tex:73-78` is a comment and does not typeset), and the byte-stability claim is
  narrowed ("byte-stable determinism for DT-GSK in the declared supported environment"). R-08: the
  cover letter and abstract present exactly three contributions with ISM as a supporting mechanism.

---

## 5. Required author confirmations (consolidated)

| Item | Register row | Blocking |
|---|---|---|
| Funding statement ("no external funding") | AG-0003 | Gate O |
| Conflict-of-interest wording and completeness; any MDPI editorial-board/guest-editor role | AG-0004 | Gate O |
| CRediT split, especially H.S.M.R.; ICMJE four-criteria confirmation for all three authors | AG-0001 | Gate O |
| H.S.M.R. institutional e-mail | AG-0005 | Upload |
| Three real ORCID iDs | AG-0002 | Upload |
| Complete GenAI tool/version inventory and the scope of AI assistance actually used | AG-0007 | Gate O (see `ai_disclosure_audit.md`) |
| Durable archive URL/DOI for the evidence release | AG-0006 | Gate O |
| Copyright line / rights-holder for the MIT grant | `docs/LICENSES.md` | Post-publication rights |
| Confirmation of no preprint and of any PhD-thesis overlap | — | Duplicate-publication declaration |
| Similarity-report result | MIN-11 | Gate O risk mitigation |
