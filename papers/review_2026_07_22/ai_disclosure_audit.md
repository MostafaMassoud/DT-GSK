> **Editorial note (2026-08-01).** This audit was performed while the project lived in the private `MostafaMassoud/PhD-Projects` monorepo. The artifact repository accompanying the article is `https://github.com/MostafaMassoud/DT-GSK`; commit counts and identifiers quoted below were measured in the monorepo and do not resolve in the public repository's squashed history. See the "Repository history and provenance" note in the top-level README.

# Stage 16 — GenAI Disclosure and Detection-Risk Audit (D16.1–D16.6)

**Seat:** `s16_ethics_ai` (T6-INTEG, role RI) · **Review date:** 2026-07-22
**Artifacts audited:** `papers/main.tex`, `papers/sections/performance.tex`,
`papers/cover_letter.tex`, `papers/DT-GSK.pdf` (39 pp), `papers/DT-GSK.docx`,
`papers/supplementary.pdf` / `.docx`, `papers/cover_letter.pdf`, and the public artifact
repository `https://github.com/MostafaMassoud/PhD-Projects`.

**Standing constraint honored:** no AI-writing-detector was run, no detector score was used as a
quality gate, and no prose was assessed for detector evasion (§15 prohibitions). No misconduct is
alleged in this document. Every finding is a **disclosure-accuracy or record-completeness** defect.

---

## 0. Venue policy — source and access

| Field | Value |
|---|---|
| Primary policy source attempted | `https://www.mdpi.com/ethics` and `https://www.mdpi.com/journal/ai/instructions` |
| Result | **HTTP 403 Forbidden** from `www.mdpi.com` on **2026-07-22** (publisher WAF). The primary text could not be fetched from this environment. |
| Secondary source used | Publisher-policy guide reproducing MDPI's AI policy verbatim, `https://libguides.iou.edu.gm/c.php?g=1482669&p=11059956`, accessed **2026-07-22**; guide last updated 2025-08-29. Corroborated by a web search of MDPI policy summaries, same date. |
| Policy content relied on | (a) *"Generative AI tools or LLMs cannot be listed as authors."* (b) Disclose use **in the Acknowledgments** AND *"Provide a detailed explanation in the Materials & Methods section."* (c) Required form: *"During the preparation of this manuscript/study, the author(s) used [tool name, version] for [description of use]. The authors have reviewed and edited the output and take full responsibility for the content of this publication."* (d) *"Disclosure is not necessary for AI used solely for text polishing, such as: Grammar, spelling, formatting and sentence structure."* (e) A declaration is additionally collected in the submission system. |
| Project's own recorded policy verification | `papers/main.tex:253-256` and `papers/governance/administrative_gap_register.md:14` — "MDPI generative-AI policy (verified 2026-07-10)", requirements (i) submission declaration, (ii) how-used in Materials and Methods, (iii) tool name/version in Acknowledgments; MDPI *Ethicality* + iThenticate + Proofig screening noted. **No archived copy of the policy text exists in the package** (see S16-AI-05). |

The package's understanding of the policy matches the independently retrieved text. The defects
below are not policy misreadings; they are accuracy defects in the disclosure itself.

---

## 1. Disclosure loci as shipped (verified in both formats)

| Locus | Source | PDF | DOCX | Names tool + version | Scopes use | Excludes science | Takes responsibility |
|---|---|---|---|---|---|---|---|
| L1 — Methods-level (§4.1 *Experimental Setup*) | `papers/sections/performance.tex:189-193` | p. 24 | ¶846 | **No** (cross-references L2) | Yes | Yes (absolute) | by reference |
| L2 — Back-matter declaration *"Use of Generative Artificial Intelligence"* | `papers/main.tex:261-274` | p. 38 | ¶1424 | Yes — "Claude Opus 4.8, Anthropic" | Yes | Yes (absolute) | Yes |
| L3 — Acknowledgments | `papers/main.tex:277-286` | p. 38 | ¶1430 | Yes — "Claude Opus 4.8 (Anthropic)" | Yes | Yes (absolute) | Yes |
| L4 — Cover letter | `papers/cover_letter.tex:59` | `cover_letter.pdf` p. 1 | n/a | Yes | Yes | Yes | Yes |
| L5 — Submission-system declaration | **not evidenced** | — | — | — | — | — | — |
| Supplement (61 pp) | — | none | none | — | — | — | — |

L1 verbatim (`performance.tex:189-193`): *"No generative-AI system contributed to the design,
execution, or analysis of the experiments or to any reported number; a large language model was
used only for language editing and the drafting of descriptive prose, as declared in full in the
back matter (Use of Generative Artificial Intelligence)."*

L2 verbatim core (`main.tex:265-271`): *"All scientific content — the algorithm design, **its
implementation**, the experimental protocol, and every reported number — was produced by the
authors' own deterministic analysis pipeline from a version-locked evidence archive, **independently
of any AI system**: the AI system designed no experiments, produced no data, computed no
statistics, and generated no scientific claim, result, or conclusion."*

L3 verbatim core (`main.tex:280-283`): *"No scientific content — the algorithm design, the
experimental protocol, **the analysis**, or any reported number — was AI-generated."*

---

## 2. Appendix A.10 record

```csv
check_id,venue_policy_source,policy_access_date,requirement,manuscript_location,submission_form_declared,methods_statement_present,acknowledgments_tool_and_version,disclosure_scope_vs_actual_use,authorship_prohibition_ok,wording_separates_language_from_science,science_provenance_checkable,detector_used,detector_score,false_positive_caveat,cross_format_persistence,consistency_form_methods_ack,severity,status,notes
D16.1,"libguides.iou.edu.gm/c.php?g=1482669&p=11059956 (verbatim MDPI reproduction); www.mdpi.com/ethics HTTP 403",2026-07-22,"(i) declare at submission; (ii) describe HOW used in Materials & Methods; (iii) tool name+version in Acknowledgments; grammar-only polishing exempt","L1 performance.tex:189-193; L2 main.tex:261-274; L3 main.tex:277-286",UNEVIDENCED (author-side; AG-0007 open),YES (Sec. 4.1 Experimental Setup),"YES - Claude Opus 4.8 (Anthropic)","MISMATCH - disclosed scope is language editing/rephrasing/descriptive drafting with an ABSOLUTE exclusion of implementation and analysis; the public artifact repository shows AI-co-authored commits to the optimizer core, the analysis/validator scripts and the governance documents",YES,YES,YES (hash-locked evidence release + deterministic pipeline),NO,n/a,"recorded: detectors are screening aids only; science-genre prose and non-native-English authorship carry elevated false-positive rates; no detector evidence used here",YES (PDF and DOCX both),PARTIAL (see D16.5),Critical,open,"ticket S16-AI-01"
D16.1b,same,2026-07-22,"tool NAME and VERSION required","L2 main.tex:263-264; L3 main.tex:277-279","UNEVIDENCED",YES,"ONE tool named: Claude Opus 4.8","INCOMPLETE - within this project directory the public history carries two distinct model identities as commit co-authors: 'Claude Opus 4.8' (204 commits) and 'Claude Fable 5' (27 commits, 23 of them under papers/)",YES,YES,YES,NO,n/a,as above,YES,PARTIAL,Major,open,"ticket S16-AI-02"
D16.2,same,2026-07-22,"No AI system may be listed as an author","main.tex:101 \Author{}; main.tex:104 \AuthorNames{}; DT-GSK.pdf p.1; DT-GSK.docx; CITATION.cff",n/a,n/a,n/a,n/a,YES - PASS,n/a,n/a,NO,n/a,n/a,YES,n/a,None,pass,"Three human authors only. Commit-trailer co-authorship in the repository is version-control metadata, not manuscript authorship, and does not breach this rule."
D16.3,same,2026-07-22,"Disclosure separates language assistance from scientific substance; names tool+version; scopes use honestly; affirms independent scientific content; states author responsibility; short and factual","L1-L4",UNEVIDENCED,YES,YES,"Structure is exemplary and the 'science is ours' claim is genuinely checkable (evidence release rel-2026-07-20-67d9345f9, per-file SHA-256 manifest, deterministic re-derivation). The DEFECT is that the honest-scoping element is overstated into a falsifiable absolute.",YES,YES,YES - strong,NO,n/a,as above,YES,PARTIAL,Major,open,"tickets S16-AI-01, S16-AI-06 (four near-duplicate loci, ~220 words in-manuscript; ticket E-015 raised exactly this and closed without shortening)"
D16.4,same,2026-07-22,"Detector scores are a screening aid, never dispositive; never allege undisclosed AI writing on a score alone","n/a",n/a,n/a,n/a,n/a,n/a,n/a,n/a,NO - none run,none,"RECORDED: peer-reviewed 2025/26 evaluations show (a) formulaic low-perplexity scientific prose is the hardest genre for detectors, with science-genre accuracy far below humanities; (b) non-native-English academic writing carries historically elevated false-positive rates (the foundational study reported ~61% average false positives on TOEFL essays for 2023-era tools - improved but not eliminated); (c) hybrid/paraphrased text collapses detector recall. No detector was run and none is required. The finding in S16-AI-01 rests entirely on the authors' own public version-control metadata, NOT on any detector output.",n/a,n/a,None,pass,"AG-0007 recommends an optional pre-submission sanity check. This panel neither ran one nor requires one; if the authors run one, record tool, score and this caveat, and treat any flag as a prompt to check disclosure compliance, not as evidence of misconduct."
D16.5,same,2026-07-22,"Submission-form declaration, Methods statement and Acknowledgments must name the SAME tool(s) and use(s)","L1 vs L2 vs L3 vs L4",UNEVIDENCED - cannot be cross-checked,YES,YES,"L2/L3/L4 agree on tool and scope. L1 names no tool (cross-reference only) and says 'used ONLY for language editing and the drafting of descriptive prose', while L2 adds 'rephrasing' and 'expository prose' - a small scope widening between loci. L5 (the submission-system field) is not evidenced anywhere, so the three-way cross-check MDPI automates cannot be completed pre-submission.",YES,YES,YES,NO,n/a,as above,YES,PARTIAL,Minor+Major,open,"tickets S16-AI-04 (L1 lacks tool+version), S16-AI-03 (no recorded author confirmation of the tool inventory), S16-AI-07 (the automated parity gate covers only the cover letter)"
D16.6,same,2026-07-22,"Disclosure must render in BOTH the PDF and the Word deliverable","DT-GSK.pdf pp.24,38; DT-GSK.docx paragraphs 846, 1424, 1430",n/a,YES both,YES both,n/a,YES,YES,YES,NO,n/a,as above,"YES - VERIFIED. PDF text extraction (pypdf) shows all three loci; DOCX word/document.xml extraction shows all three loci with identical substance. Cover letter PDF also carries it.",n/a,None,pass,"Supplementary PDF/DOCX (61 pp) carry no GenAI statement and no cross-reference. Not a policy breach - the declaration belongs to the main manuscript - but noted."
```

---

## 3. Tickets (§5.4 schema)

### S16-AI-01 — The disclosure's absolute exclusion of AI from implementation and analysis is contradicted by the public repository the paper designates as its artifact home

```text
ticket_id: S16-AI-01
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Critical
priority: P0
confidence: CONFIRMED (the contradiction); SUSPECTED (the precise extent of AI assistance - author input required)
issue_type: ethics
manuscript_location: papers/main.tex:265-271 (L2); papers/main.tex:280-283 (L3);
  papers/sections/performance.tex:189-190 (L1); papers/cover_letter.tex:59 (L4);
  DT-GSK.pdf pp. 24 and 38; DT-GSK.docx paragraphs 846, 1424, 1430
claim_id_or_artifact_id: AG-0007; CN-02 (Data Availability)
concise_issue: The manuscript states in four places that the algorithm's implementation, the
  experimental protocol and the analysis were produced independently of any AI system. The public
  repository named by the Data Availability Statement records those artifacts as having been
  produced in commits co-authored by the same AI model the paper discloses as a language tool.

exact_evidence_or_observation:
  THE CLAIM.
  papers/main.tex:265-271 -- "All scientific content---the algorithm design, its implementation,
    the experimental protocol, and every reported number---was produced by the authors' own
    deterministic analysis pipeline from a version-locked evidence archive, independently of any
    AI system: the AI system designed no experiments, produced no data, computed no statistics,
    and generated no scientific claim, result, or conclusion."
  papers/main.tex:280-283 -- "No scientific content --- the algorithm design, the experimental
    protocol, the analysis, or any reported number --- was AI-generated."
  papers/sections/performance.tex:189-190 -- "No generative-AI system contributed to the design,
    execution, or analysis of the experiments or to any reported number".

  THE POINTER THAT MAKES IT CHECKABLE.
  papers/main.tex:227-231 (Data Availability) -- the implementation, harness, per-run CSVs, seed
    schedules and manifests "are publicly available in the DT-GSK repository".
  DT-GSK.pdf p. 24 (Sec. 4.1) -- "every cell records an environment.json manifest including the
    git commit", i.e. the git history is bound into the evidence chain by construction.
  `git remote -v` -> https://github.com/MostafaMassoud/PhD-Projects.git ; fetched 2026-07-22,
    repository confirmed publicly viewable.

  THE CONTRADICTING RECORD (all commands run in the repository, 2026-07-22).
  git log --format='%h' -- .                                     -> 384 commits touch this project
  git log --grep='Co-Authored-By: Claude' --format='%h' -- .     -> 231 of those 384
  git log --format='%h' -- papers/                               -> 208
  git log --grep='Co-Authored-By: Claude' --format='%h' -- papers/ -> 145 of those 208

  THE DECISIVE SINGLE INSTANCE.
  commit af7efc534b689850d8e41d12d70a09db7a26ad7c (2026-07-14)
    subject: "fix(dt-gsk): correct final-polish incumbent (C006) and interaction-graph numba
              import (M038)"
    files:   src/gsk_family/optimizers/_dt_core.py
             src/gsk_family/optimizers/_dt_subsystems/interaction_graph.py
             tests/regression/test_dt_polish_incumbent_consistent.py
             tests/regression/test_dt_graph_backend_parity.py
    trailer: "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
    its own message: "This CHANGES trajectories wherever the polish fires ... All D >= 50 evidence
             must be regenerated"
  This is the commit that forced the 51-run regeneration behind the CURRENT evidence release
  rel-2026-07-20-67d9345f9. It modifies the DT-GSK optimizer core. Its trailer names the exact
  model and version the manuscript discloses as a language-editing tool.
  Verified publicly viewable and showing that trailer at
  https://github.com/MostafaMassoud/PhD-Projects/commit/af7efc534b689850d8e41d12d70a09db7a26ad7c
  (fetched 2026-07-22).

  WHAT THE EVIDENCE DOES AND DOES NOT SHOW.
  A Co-Authored-By trailer is emitted by the assistant tooling on commits it participates in
  producing. It is strong evidence of AI participation in producing that diff. It does NOT show
  that an AI "designed the algorithm", "produced data", or "computed statistics" - the runs were
  executed by the harness and every number is bound to the hash-locked release. So the narrow
  clauses in L2 are defensible. What is NOT defensible as written are the three broader clauses:
  "its implementation", "the experimental protocol", and "the analysis" ... "independently of any
  AI system" / "was [not] AI-generated".

root_cause: The disclosure was drafted around the manuscript prose only, and the affirmative
  exclusion was written as an absolute ("independently of any AI system") rather than scoped to
  what it can actually defend (the scientific decisions, the executed runs, and the reported
  numbers). The public version-control history was never audited against the claim.

scientific_or_editorial_justification: D16.1 requires the disclosed scope to match the actual use,
  and treats a substantive-use manuscript that discloses only a narrow use as a MAJOR
  under-disclosure. Here the defect is worse than an omission: it is an affirmative denial that a
  reader can falsify in one click from the paper's own availability statement. MDPI screens every
  submission with its in-house Ethicality system for authorship anomalies and AI-generated
  content; a self-refuting exclusion is precisely the pattern that converts a routine flag into an
  integrity query. D16.3 states the correct principle: a disclosure that makes "the science is
  ours" CHECKABLE turns an AI flag from a liability into a verifiable defense. This manuscript has
  an unusually strong checkable basis - a hash-locked, deterministically re-derivable evidence
  release - and does not need the overstatement at all.

impact_on_validity_or_acceptance: No effect on any result: the numbers are bound to the frozen
  release and remain re-derivable. Severe effect on acceptance risk. This is, in my assessment,
  the single largest desk-rejection / integrity-query risk in the package - larger than any
  statistical or methodological item, because it is verifiable by an editor in under a minute and
  is self-inflicted by wording that the evidence does not require.

required_correction: Rewrite L1, L2, L3 and L4 so the exclusion is accurate and still strong.
  Keep the checkable core; drop the absolute. A defensible formulation (authors to adapt, and to
  verify against their own knowledge of what was actually done):
    "During the preparation of this work the authors used generative-AI assistants
     (<tool, version>; <tool, version>) for language editing and the drafting of descriptive
     prose, and as coding assistants during the development of the implementation, the analysis
     scripts and the verification tooling. All scientific decisions - the algorithm design, the
     experimental protocol, the statistical plan, and the interpretation of every result - were
     made by the authors. No AI system executed an experiment, generated data, or produced a
     reported number: every reported value is computed by the released deterministic pipeline
     from the version-locked evidence release rel-2026-07-20-67d9345f9, whose manifest records a
     SHA-256 checksum for every file, and is independently re-derivable. The authors have reviewed
     and verified all AI-assisted output, including all code, which is covered by the released
     regression and byte-stability test suite, and take full responsibility for the content of
     this publication."
  This is SHORTER than the current L2, is not falsifiable by the repository, and converts the
  version-control history from a liability into corroboration.

acceptable_alternatives: If - and only if - the authors can establish that the released optimizer
  core, analysis pipeline and protocol documents were in fact authored without AI assistance and
  the trailers are an artifact of the commit workflow rather than of authorship, then the current
  wording may stand, PROVIDED that position is recorded in the governance package with evidence
  and the authors are prepared to state it to an editor. Given 231 of 384 project commits and the
  content of af7efc534's own message, I assess that position as very unlikely to be sustainable.
  A third option - scrubbing the trailers by rewriting history - is NOT acceptable: it would
  destroy the provenance chain the paper relies on and is itself an integrity problem.

additional_evidence_needed: Author statement of what AI assistance was actually used for, per
  artifact class (manuscript prose / optimizer core / analysis and validator scripts / governance
  documents), so the rewritten disclosure is accurate rather than merely safer.

dependencies: S16-AI-02 (tool inventory), S16-AI-03 (recorded author confirmation),
  S16-E-02 (the availability statement that makes the claim checkable).

expected_improvement: Removes the top desk-rejection risk; converts the evidence-lock
  infrastructure into an affirmative defense; Gate O GenAI trigger cleared. No rerun, no new
  evidence release, no change to the byte-locked optimizer core.

post_revision_verification: (1) Re-read L1-L4 in the rendered PDF and DOCX and confirm no clause
  asserts AI-independence of the implementation, the protocol, or the analysis. (2) Re-run
  `git log --grep='Co-Authored-By' --format='%h' -- .` and confirm every artifact class touched by
  those commits is covered by the rewritten scope. (3) Confirm the "every reported number is
  re-derivable from the release" clause survives intact.
status: open
```

### S16-AI-02 — Incomplete tool inventory: a second AI model appears in the public history and is not disclosed

```text
ticket_id: S16-AI-02
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Major
priority: P1
confidence: CONFIRMED
issue_type: ethics
manuscript_location: papers/main.tex:263-264 (L2); papers/main.tex:277-279 (L3);
  papers/sections/performance.tex:190 (L1); papers/cover_letter.tex:59 (L4)
claim_id_or_artifact_id: AG-0007
concise_issue: The manuscript names exactly one tool and version. The public history of this
  project names two distinct model identities as commit co-authors.
exact_evidence_or_observation:
  Disclosed: "a large language model (Claude Opus 4.8, Anthropic)" (main.tex:263-264) and
    "Claude Opus 4.8 (Anthropic)" (main.tex:277-279). MDPI's required form is
    "used [tool name, version] for [description of use]".
  Repository-wide trailer census (2026-07-22):
    git log --format='%B' | grep -o -i "Co-Authored-By: Claude[^>]*>" | sort | uniq -c
      314  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
      217  Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
      182  Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
       53  Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
        4  Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
        2  Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
  Restricted to THIS project directory:
    Claude Opus 4.8  -> 204 commits
    Claude Fable 5   ->  27 commits (23 of them touching papers/, 2 touching src/)
    Opus 4.6 / 4.7   ->   0 commits in this project
  Representative Fable 5 commits under papers/:
    3ce7afb04 (2026-07-11) "papers: fix messy ISM-GSK pseudocode float + upgrade AI-disclosure
      wording"   <-- an undisclosed model participated in drafting the AI-disclosure wording itself
    a16ed2b74 (2026-07-11) "papers: deepen PAPER_REVIEW_PROMPT.md - GenAI, venue-fit, stats
      dispositions"
    cffcbb481 (2026-07-11) "papers: Phase 10 FROZEN - adversarial 6-reviewer review, Gate 10 pass"
    40fbee8e0 (2026-07-11) "papers: Phase 11 FROZEN - pre-ablation hard freeze, Gate 11 PASS"
    a4e378d24 (2026-07-11) "papers: Phase 9 FROZEN - dual-format PDF + native Word + MDPI typography"
root_cause: The disclosure was pinned to the model in use at the time it was drafted (2026-07-13);
  earlier phases of the same manuscript used a different model and the inventory was never
  reconciled against the history.
scientific_or_editorial_justification: MDPI requires the tool NAME and VERSION. Naming one of two
  models is an incomplete disclosure regardless of how the use is characterized, and it is
  independently checkable from the repository the paper points at. The 3ce7afb04 example is
  particularly awkward: the disclosure statement's own wording was upgraded in a commit
  co-authored by the undisclosed model.
impact_on_validity_or_acceptance: No effect on results. Compounds S16-AI-01: a reader who checks
  the trailers finds both an inaccurate scope AND a missing tool.
required_correction: List every AI tool and version used in producing the manuscript and the
  released artifacts. At minimum: Claude Opus 4.8 (Anthropic) and Claude Fable 5 (Anthropic).
  Confirm with the authors whether any non-Anthropic tool was used at any stage.
acceptable_alternatives: If the earlier-model work is genuinely confined to artifacts that are not
  part of the submission (e.g. only the internal build/review prompts), say so precisely rather
  than omitting the tool - but note that 23 of the 27 Fable 5 commits touch papers/, including the
  Phase 9/10/11 freeze commits that produced the manuscript deliverables.
additional_evidence_needed: Author confirmation of the complete tool list.
dependencies: S16-AI-01, S16-AI-03.
expected_improvement: D16.1b and D16.5 move from PARTIAL to PASS.
post_revision_verification: Every distinct trailer identity in
  `git log --format='%B' -- . | grep -o "Co-Authored-By: [^<]*"` is either named in the disclosure
  or explicitly and truthfully excluded by scope.
status: open
```

### S16-AI-03 — No recorded author confirmation of the GenAI tool/version, contrary to the in-source assertion

```text
ticket_id: S16-AI-03
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Major
priority: P1
confidence: CONFIRMED
issue_type: ethics
manuscript_location: papers/main.tex:255-258, :275-276
claim_id_or_artifact_id: AG-0007
concise_issue: main.tex asserts the tool and scope were author-confirmed on 2026-07-13; the
  governance record dated the same day says the opposite, and AG-0007 is still open.
exact_evidence_or_observation:
  papers/main.tex:255-258 -- "Author-confirmed (2026-07-13): tool = Claude Opus 4.8 (Anthropic);
    use = language editing AND drafting of descriptive text (substantive assistance, hence the
    full declaration, not the text-editing-only exemption)."
  papers/main.tex:275-276 -- "Acknowledgments tool/version (MDPI requirement iii): version pinned
    to Claude Opus 4.8 (author-confirmed 2026-07-13)."
  papers/main.tex:180-183 (same file, 70 lines earlier) -- "nothing below closes an open AG row;
    drafted-unconfirmed items are flagged in comments and require author confirmation before
    submission (AG-0001..AG-0007)."
  papers/governance/decision_log.md:354 -- "D-0012 (2026-07-13)"
  papers/governance/decision_log.md:358-360 -- "author-side *facts* (ORCID, DOI, e-mail, CRediT
    split, GenAI version, licenses, funding, COI) are NOT decided here and remain open"
  papers/governance/decision_log.md:395 -- lists "AG-0007 (GenAI version/date)" as still open
  papers/governance/decision_log.md:454-455 -- "A1.T5 author-fact metadata (DOI/CRediT/GenAI)
    remains blocked on author input"
  papers/governance/administrative_gap_register.md:14 -- AG-0007 status "open"
  The register's own closure rule (:17-19) requires an explicit author-provided value recorded in
  the register with a date. No such record exists for AG-0007.
root_cause: Confirmation captured as a source comment, never propagated to the register.
scientific_or_editorial_justification: Section 16 forbids inventing a disclosure. An unrecorded
  confirmation is an audit gap, and here it is materially consequential: S16-AI-02 shows the
  "confirmed" inventory is in fact incomplete, so the missing record is not a formality.
impact_on_validity_or_acceptance: Blocks Gate O administratively; also the mechanism by which the
  incomplete inventory went unnoticed.
required_correction: Obtain and record in administrative_gap_register.md the complete tool list,
  the version(s), the actual scope of use per artifact class, and the confirmation date; then
  close AG-0007 and reconcile the main.tex comments.
acceptable_alternatives: none.
additional_evidence_needed: Author statement (same statement that unblocks S16-AI-01/02).
dependencies: S16-E-01 (same defect pattern across AG-0001/0003/0004).
expected_improvement: AG-0007 closes on a recorded, accurate value.
post_revision_verification: AG-0007 row carries a dated author-supplied value that matches the
  rendered disclosure and the trailer census.
status: open
```

### S16-AI-04 — The Materials-and-Methods-level statement names no tool or version

```text
ticket_id: S16-AI-04
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Minor
priority: P2
confidence: CONFIRMED
issue_type: compliance
manuscript_location: papers/sections/performance.tex:189-193; DT-GSK.pdf p.24 (Sec. 4.1);
  DT-GSK.docx paragraph 846
claim_id_or_artifact_id: AG-0007
concise_issue: MDPI's methods-level requirement is satisfied by a cross-reference rather than by
  the required "[tool name, version] for [description of use]" form.
exact_evidence_or_observation:
  performance.tex:189-193 -- "... a large language model was used only for language editing and
    the drafting of descriptive prose, as declared in full in the back matter (Use of Generative
    Artificial Intelligence)."
  MDPI required form (accessed 2026-07-22): "During the preparation of this manuscript/study, the
    author(s) used [tool name, version] for [description of use]."
  Placement is otherwise correct: the nearest preceding heading in the rendered PDF is
    "4.1. Experimental Setup" (PDF line 1181), an M&M-equivalent location. VERIFIED.
root_cause: Deliberate de-duplication (see ticket E-015) taken one step too far for an automated
  cross-check that looks for the tool name inside Materials and Methods.
scientific_or_editorial_justification: MDPI's Ethicality system cross-checks the submission-form
  declaration against the Methods and Acknowledgments text; a locus that names no tool cannot
  match. Also stylistically odd: the statement is appended to a paragraph about budget accounting
  and thread determinism, with no transition.
impact_on_validity_or_acceptance: Low. Cheap to fix.
required_correction: Name the tool(s) and version(s) in the Sec. 4.1 sentence, or move the
  statement to its own short paragraph at the end of 4.1 with the tool named.
acceptable_alternatives: Keep the cross-reference but add "(Claude Opus 4.8, Anthropic; see the
  back matter)".
additional_evidence_needed: none
dependencies: S16-AI-02 (the list to be named).
expected_improvement: D16.5 three-way cross-check becomes machine-satisfiable.
post_revision_verification: The Sec. 4.1 sentence in the rendered PDF and DOCX names every tool
  and version listed in the Acknowledgments.
status: open
```

### S16-AI-05 — No archived copy of the venue policy behind the "verified 2026-07-10" claim

```text
ticket_id: S16-AI-05
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Minor
priority: P3
confidence: CONFIRMED
issue_type: compliance
manuscript_location: papers/main.tex:253-256; papers/governance/administrative_gap_register.md:14
claim_id_or_artifact_id: AG-0007
concise_issue: The package asserts the MDPI GenAI policy was verified on 2026-07-10 but archives
  no copy of the policy text, its URL, or an access record.
exact_evidence_or_observation:
  administrative_gap_register.md:14 -- "GenAI-use disclosure statement (MANDATORY, MDPI policy
    verified 2026-07-10)" followed by a paraphrase of the requirements.
  grep -rn -i "mdpi.com/ethics|instructions for authors" over papers/governance/ and docs/ returns
    only that paraphrase and the requirements-matrix rows - no archived snapshot, no URL, no
    access-dated record.
  This panel could not fetch the primary policy either: www.mdpi.com/ethics and
    www.mdpi.com/journal/ai/instructions both returned HTTP 403 on 2026-07-22. Verification here
    relies on a secondary verbatim reproduction (recorded in section 0 above).
  The paraphrase in the register is ACCURATE against the independently retrieved text, so this is
    a record-keeping gap, not a misreading.
root_cause: Policy was read online and paraphrased without archiving.
scientific_or_editorial_justification: The review framework requires the venue policy source and
  access date to be recorded; publisher policies change, and a paraphrase with no source cannot be
  re-verified.
impact_on_validity_or_acceptance: Negligible for acceptance; matters for auditability.
required_correction: Archive the MDPI Instructions-for-Authors AI section (PDF or text) with URL
  and access date in papers/governance/, and cite it from AG-0007.
acceptable_alternatives: Record URL + access date + verbatim quotation in the register.
additional_evidence_needed: none
dependencies: none
expected_improvement: The policy claim becomes re-verifiable.
post_revision_verification: An access-dated policy artifact exists and matches the disclosure form.
status: open
```

### S16-AI-06 — Disclosure redundancy: four near-duplicate statements; ticket E-015 closed without shortening

```text
ticket_id: S16-AI-06
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Editorial
priority: P3
confidence: CONFIRMED
issue_type: writing
manuscript_location: L1 performance.tex:189-193; L2 main.tex:261-274; L3 main.tex:277-286;
  L4 cover_letter.tex:59
claim_id_or_artifact_id: E-015
concise_issue: The same disclosure is stated four times in four different wordings, ~220 words
  inside the manuscript alone; the project's own ticket for this was closed without shortening it.
exact_evidence_or_observation:
  L2 is ~105 words, L3 ~70, L1 ~45, L4 ~85. All four assert tool, scope, exclusion and
  responsibility, in four distinct phrasings.
  papers/governance/remediation_2026_07_18/ticket_status.csv, ticket E-015 (Editorial, P2):
    concise_issue -- "The GenAI disclosure is substantively strong but could be shorter and more
      parallel across Methods, Acknowledgments, and cover letter."
    triage_verdict -- "PARTIALLY-FIXED"; lifecycle_status -- "closed_verified"
    verification_evidence -- "... the ticket's core requirement - one approved wording block used
      in parallel - is not met: there are four distinct wordings, and the exclusion element is
      inconsistent."
    residual_work -- records that the fix applied was to ADD the exclusion clause to the
      Acknowledgments, i.e. the statement got LONGER, and the ticket was then closed.
root_cause: The remediation addressed completeness (all four elements at all four loci) and
  declared the length/parallelism half satisfied by that.
scientific_or_editorial_justification: D16.3 explicitly penalizes over-long disclosures: "a short,
  factual, responsibility-taking statement is the professional norm." Two loci are required by
  MDPI (Methods + Acknowledgments); the third in-manuscript block is optional. Length is not an
  integrity problem, but it reads defensively, and the S16-AI-01 rewrite is the natural moment to
  compress.
impact_on_validity_or_acceptance: Negligible alone. Bundle with S16-AI-01.
required_correction: Adopt one canonical block. Keep L2 as the full declaration, reduce L3 to the
  MDPI template sentence + the responsibility sentence, keep L1 to one sentence that names the
  tools and points to L2, and make L4 a two-sentence echo of L3.
acceptable_alternatives: Merge L2 into L3 and keep three loci (Methods, Acknowledgments, cover
  letter) - MDPI requires no separate declaration heading.
additional_evidence_needed: none
dependencies: S16-AI-01 (do both in one edit).
expected_improvement: Shorter, parallel, non-defensive disclosure; closes the real E-015 residue.
post_revision_verification: All loci derive from one approved wording; total in-manuscript
  disclosure under ~140 words.
status: open
```

### S16-AI-07 — The automated cross-format GenAI parity gate covers only the cover letter

```text
ticket_id: S16-AI-07
review_stage: 16
reviewer_role: RI (T6-INTEG)
severity: Minor
priority: P2
confidence: CONFIRMED
issue_type: reproducibility
manuscript_location: papers/scripts/validate_document_consistency.py:27, :192-202
claim_id_or_artifact_id: E-015 post_revision_verification
concise_issue: The gate that E-015 cites as enforcing GenAI cross-format parity checks only the
  two cover-letter files; the three manuscript loci and their PDF/DOCX persistence are not
  machine-enforced.
exact_evidence_or_observation:
  validate_document_consistency.py:27 -- "2. COVER-LETTER PARITY -- title, date, corresponding
    author, GenAI tool and ..."
  validate_document_consistency.py:192-202 -- the only GenAI logic in the file:
      gen_md = re.search(r"\(([^)]*Claude[^)]*)\)", md)
      gen_tx = re.search(r"\(([^)]*Claude[^)]*)\)", tx)
    i.e. it compares the parenthetical in cover_letter.md against cover_letter.tex only.
  Live run 2026-07-22: `python papers/scripts/validate_document_consistency.py` ->
    "ok  GenAI disclosure matches: Claude Opus 4.8, Anthropic" ... "OK - all cross-stated facts
    agree (no drift)". The gate is GREEN and says nothing about L1/L2/L3 or about the DOCX.
  E-015's post_revision_verification field claims "cover-letter parity already enforced by
    validate_document_consistency.py, which compares the GenAI tool/version across formats" -
    true only of the cover letter.
  I verified L1/L2/L3 persistence MANUALLY in both formats (see D16.6 row: PASS), so there is no
    live defect - this is a gate-coverage gap that would not catch a future regression.
root_cause: The check was written for the cover letter and its scope was over-read at ticket close.
scientific_or_editorial_justification: A disclosure that must render in both deliverables should be
  gated, not spot-checked, in a project whose central claim is machine-verified consistency.
impact_on_validity_or_acceptance: None today; regression risk if the disclosure is rewritten
  (which S16-AI-01 requires it to be).
required_correction: Extend the validator to assert that the tool/version string and the four
  disclosure elements appear at L1, L2 and L3 in BOTH DT-GSK.pdf and DT-GSK.docx. This is a
  read-only gate addition and touches no manuscript content and no optimizer code.
acceptable_alternatives: Add the assertion to validate_cross_format_parity.py instead.
additional_evidence_needed: none
dependencies: S16-AI-01 (write the gate against the corrected wording).
expected_improvement: D16.6 becomes machine-enforced; the S16-AI-01 rewrite lands with a gate.
post_revision_verification: Deliberately delete the Acknowledgments disclosure in a scratch copy
  and confirm the gate goes RED.
status: open
```

---

## 4. D16.4 detection-risk assessment (recorded in full, no detector run)

No AI-writing detector was run by this seat, and none should be treated as dispositive if the
authors run one. Recorded caveats, as required:

- Formulaic, low-perplexity **scientific prose** — methods, protocol, statistics — is the hardest
  genre for detectors; science-genre accuracy is far below humanities-genre accuracy. This
  manuscript is dense methods-and-statistics prose throughout, i.e. maximal false-positive genre.
- **Non-native-English** academic writing carries historically elevated false-positive rates; the
  foundational evaluation reported roughly 61 % average false positives on TOEFL essays for
  2023-era detectors. Improved in current tools, not eliminated. All three authors are based at
  non-Anglophone institutions.
- **Hybrid / paraphrased** text collapses detector recall, so a low score would be equally
  uninformative.

Consequence for this review: **a detector flag on this manuscript would carry essentially no
evidential weight**, and the S16-AI-01 finding deliberately rests on nothing of the kind — it rests
solely on the authors' own public version-control metadata, which is not a probabilistic signal.
If the authors run a pre-submission check per AG-0007, record the tool, the score and these
caveats, and treat any flag purely as a prompt to confirm disclosure compliance.

`papers/governance/instruction_precedence.md:44, :76` correctly supersede the legacy
`PHASE_6_humanization.md` detector-evasion framing (item C-07), and `requirements_part5.csv:194`
(R-6748) records "Prohibited: write to evade automated authorship detectors." I found **no
evidence** of detector-evasion editing anywhere in the manuscript sources. That prohibition is
being honored.

---

## 5. Roll-up

| Check | Verdict | Severity of residue |
|---|---|---|
| D16.1 disclosure completeness (policy-anchored) | **FAIL** | Critical (S16-AI-01) + Major (S16-AI-02) |
| D16.2 authorship prohibition | **PASS** | none |
| D16.3 disclosure-wording quality | **PARTIAL** | Major — structure exemplary, exclusion overstated (S16-AI-01); redundancy (S16-AI-06) |
| D16.4 detection-risk assessment | **PASS** | none — no detector used, caveats recorded |
| D16.5 form ↔ methods ↔ acknowledgments consistency | **PARTIAL** | Major (S16-AI-03) + Minor (S16-AI-04, S16-AI-07); submission-form locus unevidenced |
| D16.6 cross-format persistence | **PASS** | none — verified in PDF and DOCX |

**Gate O (GenAI limb): FAIL**, on the D16.1 trigger "GenAI under-disclosure relative to the
verified venue policy".

**Everything required to clear it is prose and record-keeping.** No rerun, no new evidence release,
and no change to the byte-locked optimizer core. The paper's evidence-lock infrastructure means an
honest disclosure costs it nothing scientifically and gains it a defense that very few submissions
in this literature can offer.
