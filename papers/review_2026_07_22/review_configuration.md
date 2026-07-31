# Review Configuration — Stages 0 and 1 (seat `s0-1_preflight`)

**Artifact:** `papers/review_2026_07_22/review_configuration.md`
**Companion:** `papers/review_2026_07_22/requirements_compliance_matrix.csv`
**Governing prompt:** `papers/PAPER_REVIEW_PROMPT.md` (4422 lines) — stage mandate lines 1247–1334, ticket schema lines 1104–1130, DT-GSK profile §10 lines 3160–3518, prohibited shortcuts §15 line 3977.
**Seat mandate:** Stage 0 (preflight, authority extraction, version freeze) + Stage 1 (package completeness and technical intake).
**Posture:** READ-ONLY on manuscript, code, and governance. No file outside `papers/review_2026_07_22/` was written. Two validators that emit CSVs were redirected to the session scratchpad rather than their default governance paths.

---

## 1. Frozen review snapshot (§Stage 0 check 11)

| Field | Value | How verified |
|---|---|---|
| `REVIEW_ID` | `DTGSK-REV-2026-07-22 / seat s0-1_preflight` | assigned by orchestrator |
| `REVIEW_DATE` | 2026-07-22 | session date |
| `REVIEW_SNAPSHOT_COMMIT` | **`45248eb31af7b01567c251f2a5da4f36e92d6030`** (`git rev-parse HEAD`) | `git rev-parse HEAD` |
| `PROJECT_TITLE` | DT-GSK: Dimension-Tiered Adaptive Control and Deterministic Refinement for Gaining-Sharing Knowledge Optimization | `papers/cover_letter.tex:53`; rendered title page |
| `MANUSCRIPT_VERSION` | `v1.0` (default first-submission id) | `papers/governance/submission_package_manifest.json:4-5` |
| `MANUSCRIPT_FILE` | `papers/DT-GSK.pdf` (39 pp, 695,943 B, sha256 `34362769…`) + `papers/DT-GSK.docx` (1,037,004 B, sha256 `1ad8c3b2…`) | `check_manifest.py` → `15/15 match`; page count from `fitz` page objects **and** `papers/main.log` "Output written on main.pdf (39 pages" |
| `SUPPLEMENTARY_FILE` | `papers/supplementary.pdf` (61 pp, 1,155,151 B, sha256 `9d0d3cf9…`) + `papers/supplementary.docx` (8,735,071 B, sha256 `a9a64295…`) | same |
| `COVER_LETTER` | `papers/cover_letter.pdf` (2 pp, 113,413 B, sha256 `7313e38f…`) | same |
| `CANONICAL SOURCE` | `papers/main.tex` + `papers/sections/{introduction,related_work,proposed_algorithm,performance,conclusions}.tex` + `papers/supplementary.tex` + `papers/references.bib` | `main.tex:173-177` `\input` list; all five files pinned in the freeze manifest |
| `GOVERNING_PROTOCOL` (build) | `papers/PAPER_BUILD_PROMPT.md` — **7,864 lines**, mtime 2026-07-21 | `wc -l` |
| `GOVERNING_PROTOCOL` (review) | `papers/PAPER_REVIEW_PROMPT.md` — 4,422 lines, mtime 2026-07-21 | `wc -l` |
| `GOVERNANCE_AND_GATE_ARTIFACTS` | `papers/governance/` — 60 files (see §4 for two unresolved path bindings) | directory listing |
| `TARGET_JOURNAL` | *Algorithms* (MDPI), article type `article` | `papers/main.tex:5` class option; `submission_package_manifest.json:6`; `phase_04/journal_decision.md` (D-0010, author-ratified) |
| `TARGET_QUARTILE_STATUS` | Q2 declared; quartile evidence is a 2026-07-10 decision-log record, **not re-verified in this session** (§15 forbids asserting quartile without current verification) | `governance/decision_log.md:267-291` |
| `AUTHOR_GUIDELINES_SOURCE` | `phase_04/journal_requirements.md` — **`verified_online = FALSE`**, HTTP 403 on 2026-07-10, flagged "MUST be re-verified … before submission" | `journal_requirements.md:12,30-32,66` |
| `RAW_OR_IMMUTABLE_EVIDENCE_ROOT` | `benchmarks/cec_reference_results/`, release **`rel-2026-07-20-67d9345f9`**, anchor `67d9345f9502a9a584e645fa8948f60a61d70e29`, 3,403 files, 712,437,624 B | `governance/evidence_release_manifest.json` header + `totals` |
| `DERIVED_ANALYSIS_BUNDLE` | `papers/analysis/rel-2026-07-20-67d9345f9/` incl. `primary_stats/statistical_results.csv` | directory listing |
| `ABLATION RELEASE` | `abl-rel-2026-07-20` | `benchmarks/cec_reference_results/_ablation/manifest.json` `release_id` |
| `STATISTICAL_ANALYSIS_PLAN` | `papers/build_prompt_phases/phase_05/statistical_analysis_plan.md` — **not** at the §10.1 bound path | `find` |
| `CLAIM_EVIDENCE_MATRIX` | `papers/governance/claims_evidence_matrix.csv` (32,852 B, pinned) | freeze manifest |
| `REPRODUCIBILITY_PACKAGE` | `papers/governance/reproducibility_manifest.json` — **bound to the superseded 07-10 release** (ticket S01-002) | file inspection |
| `MANUSCRIPT FREEZE ANCHOR (declared)` | `abd2fa2f25c8426247b43c85bcb3d82041d00976` | `main_manuscript_freeze_manifest.json:5` |
| `MANUSCRIPT FREEZE ANCHOR (actual, by content)` | **`45248eb31`** — the declared anchor does not reproduce the pinned bytes (ticket S01-001) | `git show <anchor>:…` sha256 comparison, §3 below |

**Snapshot rule.** This review is frozen at `45248eb31`. Any later change requires a new review-version identifier and a revision log entry; findings below are not carried forward automatically.

---

## 2. Authority order actually in force (§1.4, as applied by this seat)

The orchestrator's instruction and §1.4 combine to the following operative precedence. Rank 2b is the local override that this review must apply and record:

1. **Latest explicit author/project requirement** — the standing constraints in `governance/_pending_refreeze.json:6-11`: *no optimizer-core edit (byte-locked; correct the paper, not the code); no comparator edit; no rerun; no new evidence release*.
2. **Governing development prompt and frozen protocol** — `papers/PAPER_BUILD_PROMPT.md`; phase gates in `governance/phase_gate_register.csv` (13 rows, phases 0–12, **all `FROZEN`**).
   **2b. Local override in force:** the review prompt's own §1.5 snapshot (lines 118–602, dated 2026-07-20) **predates** the 2026-07-21/22 R-01…R-14 remediation and is demoted below the observed repository state. Where §1.5 or §10.7's RT-001 bullet contradicts the repo, the repo governs. Recorded as ticket **S01-006**.
3. **Immutable empirical evidence + producing code** — release `rel-2026-07-20-67d9345f9`; optimizer core byte-locked.
4. **Frozen analysis plan** — `phase_05/statistical_analysis_plan.md` (59 pre-registered families).
5. **Official current journal requirements** — *unavailable this session*: the Phase-4 record is `verified_online=false`; not re-fetched (no browsing performed for this seat).
6. **Verified literature sources** — `reference_papers/` + `reference_inventory.csv`; 57 admissible keys.
7. **Generated tables/figures/statistical reports** — `papers/analysis/rel-2026-07-20-67d9345f9/`, `papers/tables/T*.tex`.
8. **Manuscript prose.**
9. **Comments, filenames, planning notes, memory** — includes `supplementary.tex:6` (ticket S01-008).

---

## 3. Three-way source ↔ PDF ↔ Word desync test (§Stage 0 check 8)

**Result: the three artifacts DO resolve to one scientific state. No three-way desync.** The Stage-0 hard-fail condition is **not** met. Evidence:

| Test | Command / method | Result |
|---|---|---|
| Hash-pin integrity | `python papers/scripts/check_manifest.py` | `15/15 match []`, exit 0 |
| Newest source edit reaches the PDF | probe `"crossing falls only on the terminal"` / `"confers no search advantage"` (added to `sections/performance.tex` at `45248eb31`) | present in `DT-GSK.pdf` |
| Newest source edit reaches the DOCX | same probes against `word/document.xml` (tags stripped) | present in `DT-GSK.docx` |
| Cross-format parity | `validate_cross_format_parity.py --csv <scratchpad>` | **579 rows, FAIL = 0**, exit 0; output **byte-identical** to the committed `governance/cross_format_consistency.csv` |
| Value bindings | `validate_evidence_bindings.py --csv <scratchpad>` | exit 0, 0 FAIL |
| Build hygiene | `validate_build_hygiene.py` | exit 0 — no unresolved references, no control characters, no retired content |
| Provenance claims | `validate_provenance_claims.py` (R-07 hardened) | exit 0 on **source and rendered** artifacts |
| Document consistency | `validate_document_consistency.py` | exit 0 — S1–S6 contiguous, 6 actual supplement sections, cover-letter `.md`↔`.tex` parity |
| Runtime provenance | `validate_runtime_provenance.py` | exit 0 — single host, single worker count |

**But the freeze *record* is desynchronised from its declared anchor** — see ticket **S01-001**. The `anchor_commit`/`authoritative_commit` in both manifests is `abd2fa2f2`, while the pinned hashes are those of `45248eb31`:

```
papers/sections/performance.tex   @abd2fa2f2 6d7b6258…  |  pinned & @HEAD fd7dbbac…
papers/DT-GSK.pdf                 @abd2fa2f2 5d1f095b…  |  pinned & @HEAD 34362769…
papers/DT-GSK.docx                @abd2fa2f2 647028d5…  |  pinned & @HEAD 1ad8c3b2…
papers/governance/citation_usage_map.csv  changed in the same commit
```

A third party checking out the declared anchor and running `check_manifest.py` obtains **11/15**, not 15/15.

---

## 4. Missing / unresolvable inputs and their downstream effect (§1.3, §Stage 0 check 7)

| Missing or unresolvable input | §10.1 bound path | Actual location | Downstream effect | Disposition |
|---|---|---|---|---|
| Statistical analysis plan | `papers/governance/statistical_analysis_plan.md` | `papers/build_prompt_phases/phase_05/statistical_analysis_plan.md` | Stage 9 must follow the real path; a literal reading of §10.1 reports a missing input | Ticket **S01-009**, not blocking |
| Exhibit plan | `papers/governance/exhibit_plan.csv` | `papers/build_prompt_phases/phase_04/exhibit_plan.csv` (71 rows per Phase-4 gate row) | same | Ticket **S01-009**, not blocking |
| External-gate mapping | `papers/governance/` (unnamed) | **not found anywhere in the tree** (`find -iname "*external_gate*" -o -iname "*gate_mapping*"` → 0 hits) | §10.1's "external-gate mapping" audit cannot be performed | Ticket **S01-009**; record as missing input, do not fabricate |
| Live MDPI *Algorithms* author instructions | official journal page | `phase_04/journal_requirements.md` records HTTP 403, `verified_online=false` | Stage 17 journal-compliance checks (length cap, blinding model, supplement file rules, declaration ordering) rest on search-derived evidence; §15 forbids asserting the quartile without current verification | Recorded; author/Stage-17 action, not a scientific defect |
| Repository DOI / Zenodo identifier, ORCID iDs, corresponding-author institutional e-mail | Data-Availability statement, title page | absent by design | Data-availability statement points to "the DT-GSK repository" with no resolvable identifier | **Explicitly out of scope** per prompt §1.5.4 — recorded, **no ticket raised, no gate failed** |
| Compliance status column in the build's RTM | `governance/requirements_traceability_matrix.csv` | schema is `requirement_id,line_no,summary,phase,artifact,validation,owner` — no status field | The §10.1 "MAY be seeded from the RTM" path yields traceability only, not status; this review's matrix was built independently | Recorded (see also **S01-005**) |

---

## 5. Package completeness table (Stage 1 required output)

| Expected artifact | Present | Version / identity | Status | Blocking consequence if absent |
|---|---|---|---|---|
| Main manuscript PDF | yes | 39 pp, sha256 `34362769…` | **PASS** | Gate A |
| Main manuscript DOCX | yes | sha256 `1ad8c3b2…`, 17 native `w:tbl`, 753 OMML blocks | **PASS** | Gate P |
| Supplement PDF | yes | 61 pp, sha256 `9d0d3cf9…` | **PASS** | Gate A |
| Supplement DOCX | yes | sha256 `a9a64295…`, 26 native `w:tbl`, 640 OMML blocks | **PASS** | Gate P |
| Cover letter PDF | yes | 2 pp, venue = *Algorithms* (MDPI), no reviewer placeholder | **PASS** | admin |
| Canonical LaTeX sources | yes | 5 section files, all `\input` from `main.tex:173-177` | **PASS** | Gate A |
| Bibliography | yes | `main.bbl` 40 entries, `supplementary.bbl` 8, `references.bib` 57 entries = 57 allowed keys; `main.blg` 0 warnings | **PASS** | Gate C |
| Tables | yes | T01–T16, T16_bca, SA01, SA02 — **every file is `\input` by a built document**; no orphan | **PASS** | Gate M |
| Figures | yes | 7 figure directories; the only raster images in either PDF are the four 355×234 MDPI template badges on p.1 — all manuscript figures are vector | **PASS** | Gate M |
| Equation numbering / cross-references | yes | 0 `??` tokens in either rendered PDF; `validate_build_hygiene` reports no unresolved references | **PASS** | Gate M |
| Layout integrity | yes | **0 Overfull `\hbox`** in `main.log` and `supplementary.log` (107 hits are Underfull badness only) | **PASS** | Gate M |
| Tracked changes / comments / hidden text | absent | both DOCX: `w:ins` 0, `w:del` 0, `w:commentRangeStart` 0, `w:vanish` 0, `w:moveFrom/To` 0; `word/comments.xml` is a 625-byte empty stub (0 `w:comment`). The 294/110 hits are `w:instrText` — required working fields | **PASS** | Gate P |
| DOCX OMML `&` leak (R-03) | clean | 0 of 753 (main) and 0 of 640 (supplement) `m:oMath` blocks contain a literal `&amp;` | **PASS** | Gate P |
| Placeholders / scaffold tokens | absent | scanned all three PDFs for `TODO TBD TK XXX FIXME "lorem ipsum" [cite] 0000-0000-0000-0000 "Author, Year" -dirty` → 0 hits. The one hex-looking token in `DT-GSK.pdf` is `a18070398` = the legitimate DOI `10.3390/a18070398` in reference [x] | **PASS** | Gate N |
| Machine identifiers in reader-facing text | main + cover letter clean; supplement concentrates them in the provenance appendix (7 release ids, 1×40-hex anchor, module hashes, Merkle digest) | all inside the S5 chronological-provenance appendix adopted by M-031 | **PASS with observation** — see §7 hand-off | Gate N |
| Declarations back matter | yes | Author Contributions (CRediT), Funding, IRB, Informed Consent, Data Availability, Conflicts of Interest, Abbreviations, GenAI disclosure (Claude Opus 4.8, Anthropic), Acknowledgments | **PASS** | Gate O |
| Supplementary-materials back-matter listing | yes | `main.tex:186-200` `\supplementary{}` lists S1–S6 | **PARTIAL** — under-describes S6 (ticket S01-010) | Gate A/C |
| Supplement object references | resolve | main text cites S2, S3, S5, S6, S6.5, S6.6, S6.7 — all exist (S6.6 "Conditional-Benefit Analysis by Function Class"; S6.7 "Implementation Caveats"); **no reference to the removed oracle study; the token "oracle" appears 0 times in either rendered document** | **PASS** | Gate C/J |
| Orphan / superseded source files | none in the build path | `papers/sections/` contains exactly the 5 files `main.tex` inputs; `papers/tables/` contains exactly the 19 inputs used; `papers/DT-GSK_visio.docx` (declared excluded) is **absent from disk and from `git ls-files`** | **PASS** (ticket S01-011 is a record-hygiene nit) | Gate A |
| Anonymization | author names present | correct for MDPI's declared single-blind model; the model itself is **unverified** (`journal_requirements.md:66`) | **PASS, conditional on §4 row 4** | Gate O |
| Build-gate register | yes | 13 rows, phases 0–12, all `state = FROZEN` with entry/validation/acceptance/exit evidence — §10.1's Gate-A precondition is satisfied | **PASS** | Gate A |

---

## 6. Tickets (§5.4 schema)

### S01-001 — Freeze manifest anchor does not reproduce the frozen package

```text
ticket_id: S01-001
review_stage: Stage 0
reviewer_role: SE (seat s0-1_preflight)
severity: Major
priority: P1
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/governance/main_manuscript_freeze_manifest.json:5 ; papers/governance/submission_package_manifest.json:8
claim_id_or_artifact_id: manuscript freeze anchor abd2fa2f25c8426247b43c85bcb3d82041d00976
concise_issue: The declared anchor/authoritative commit is two commits behind the bytes the manifest pins, so the declared anchor does not reproduce the submission package.
exact_evidence_or_observation: |
  git rev-parse HEAD = 45248eb31af7b01567c251f2a5da4f36e92d6030
  manifest anchor_commit = abd2fa2f25c8426247b43c85bcb3d82041d00976
  git show abd2fa2f2:<papers>/sections/performance.tex | sha256sum -> 6d7b62580e2267e5...  (manifest pins fd7dbbaca981da46...)
  git show abd2fa2f2:<papers>/DT-GSK.pdf              -> 5d1f095b19635fc5...  (manifest pins 3436276946abd7dd...)
  git show abd2fa2f2:<papers>/DT-GSK.docx             -> 647028d5347443e5...  (manifest pins 1ad8c3b2129b1f65...)
  git show --stat 45248eb31 confirms performance.tex, DT-GSK.pdf, DT-GSK.docx, citation_usage_map.csv,
  and both manifests changed in that commit; the hash fields were updated, the anchor field was not.
  check_manifest.py at HEAD = 15/15; at the declared anchor it would be 11/15.
root_cause: A freeze manifest cannot name its own commit, so the project uses a follow-up stamping commit (dbc824782 did exactly this for abd2fa2f2). The 2026-07-22 17:51 amendment re-minted the hashes but no stamping commit followed.
scientific_or_editorial_justification: Stage 0 check 8 and §10.3 require that the source, PDF, and Word deliverable resolve to one identified frozen state. They do resolve to one state (HEAD), but the identifier published for that state points elsewhere, so the freeze is not independently verifiable by a third party.
impact_on_validity_or_acceptance: No reported number is affected. It defeats external verification of the freeze and would produce an 11/15 manifest failure for any reviewer or archivist who resolves the package by the published anchor.
required_correction: Add a stamping commit that sets main_manuscript_freeze_manifest.anchor_commit and submission_package_manifest.authoritative_commit to the commit that actually carries the pinned bytes (45248eb31 or its stamping successor), mirroring dbc824782.
acceptable_alternatives: Record both fields explicitly as "content anchor" (hashes) and "stamp commit" (pointer), and state in the freeze_statement that the pointer is stamped one commit later.
additional_evidence_needed: none
dependencies: must precede the authoritative submission commit; interacts with S01-007
expected_improvement: The published anchor reproduces 15/15 on a clean checkout.
post_revision_verification: git checkout <new anchor> && python papers/scripts/check_manifest.py -> 15/15, exit 0.
status: open
```

### S01-002 — Reproducibility manifest is bound to a twice-superseded evidence release

```text
ticket_id: S01-002
review_stage: Stage 0
reviewer_role: SE / REP
severity: Major
priority: P1
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/governance/reproducibility_manifest.json (root anchor_commit; phase12_reproducibility.evidence_release)
claim_id_or_artifact_id: REPRODUCIBILITY_PACKAGE binding (§10.1), determinism contract (§10.3)
concise_issue: The determinism/reproducibility manifest still declares release rel-2026-07-10-262fc16c9 and anchor 262fc16c9..., two supersessions behind the shipped evidence release.
exact_evidence_or_observation: |
  reproducibility_manifest.json : anchor_commit = 262fc16c91fbe5608a1a0b0c5df3cbcd009edc21
                                  phase12_reproducibility.evidence_release = rel-2026-07-10-262fc16c9
  evidence_release_manifest.json: release_id = rel-2026-07-20-67d9345f9
                                  anchor_commit = 67d9345f9502a9a584e645fa8948f60a61d70e29
                                  supersedes_release = rel-2026-07-16-78f075cb0 ; totals.files = 3403
  main_manuscript_freeze_manifest.json / submission_package_manifest.json: evidence_release = rel-2026-07-20-67d9345f9
root_cause: The 07-16 and 07-20 re-mints (C006/M038 fixes, 51-run regeneration) updated the evidence and freeze manifests but not the reproducibility manifest.
scientific_or_editorial_justification: §10.1 requires reproducibility_manifest.json to agree with the §10.3 release checksums, and §10.3 requires the achieved reproducibility level to be recorded per artifact class against the SELECTED immutable release. As written, the attestation certifies evidence that has since been regenerated.
impact_on_validity_or_acceptance: The published reproducibility contract does not cover the shipped evidence. A reproducibility reviewer following the manifest would attempt to rebuild from a release the paper does not use.
required_correction: Update the manifest's anchor_commit and evidence_release to rel-2026-07-20-67d9345f9 / 67d9345f9502..., and re-record the per-artifact-class reproducibility levels against that release (or add an explicit supersession block naming which levels were re-verified and which carry forward unchanged).
acceptable_alternatives: Append a dated supersession section rather than rewriting, provided the current release is unambiguously identified as the one in force.
additional_evidence_needed: confirmation of which artifact classes were re-verified at the 07-20 re-mint (the freeze manifest asserts deterministic double-builds for the three PDFs only).
dependencies: none
expected_improvement: §10.1 bullet 3 and §10.3 determinism-contract checks become verifiable.
post_revision_verification: Diff the manifest's declared release against evidence_release_manifest.json release_id; both must read rel-2026-07-20-67d9345f9.
status: open
```

### S01-003 — Controlled-analysis-area binding in `project_configuration.md` names the wrong release

```text
ticket_id: S01-003
review_stage: Stage 0
reviewer_role: SE / REP
severity: Major
priority: P1
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/governance/project_configuration.md:98, :104, :175 (and :85-89 for the second defect)
claim_id_or_artifact_id: DERIVED_ANALYSIS_BUNDLE binding (§10.1); exhibit source-binding rule (§10.11)
concise_issue: The governance file that DEFINES the admissible controlled analysis area still binds it to papers/analysis/rel-2026-07-10-262fc16c9/, while every shipped exhibit is sourced from papers/analysis/rel-2026-07-20-67d9345f9/.
exact_evidence_or_observation: |
  project_configuration.md:98  "BOUND (Phase 2, 2026-07-10): <release_id> = rel-2026-07-10-262fc16c9"
  project_configuration.md:104 "Controlled analysis area: papers/analysis/rel-2026-07-10-262fc16c9/"
  project_configuration.md:175 "Release ID: rel-2026-07-10-262fc16c9 (bound in Phase 2 ...)"
  governance/artifact_binding.csv: 50 occurrences of rel-2026-07-20-67d9345f9
  papers/analysis/ contains rel-2026-07-10-262fc16c9, rel-2026-07-16-78f075cb0, rel-2026-07-20-67d9345f9
  Second defect, same file, :85-89: "R-0004 (cover-letter venue mismatch) is DEFERRED, not resolved:
    papers/cover_letter.md/.tex/.pdf still address Swarm and Evolutionary Computation and MUST be rewritten"
    -- false since 2026-07-11: cover_letter.tex:1-6 reads "Cover letter -- Algorithms (MDPI). R-0004 clearance
    (2026-07-11) ... The prior Swarm-and-Evolutionary-Computation letter is superseded".
root_cause: project_configuration.md is a Phase-2 document that was never updated through the two evidence re-mints or the R-0004 clearance.
scientific_or_editorial_justification: §10.11 permits exhibit generators to read only "the controlled analysis area papers/analysis/<release_id>/ RECORDED IN project_configuration.md". On the governance record's own terms the shipped exhibits are therefore sourced outside the recorded controlled area. Separately, a governance file asserting a resolved conflict is still open is a false state record.
impact_on_validity_or_acceptance: Record-level, not evidence-level: validate_evidence_bindings.py exits 0 with 0 FAIL, so the numbers themselves are correctly bound. The defect is that the compliance evidence contradicts the practice, which an evidence-integrity reviewer will read as an unenforced boundary.
required_correction: Re-bind §5 of project_configuration.md to rel-2026-07-20-67d9345f9 with a dated supersession note naming the two prior bindings; mark R-0004 CLEARED (2026-07-11, D-0010) at :85-89.
acceptable_alternatives: Add a "current binding" header block at the top of §5 that supersedes the historical Phase-2 text without deleting it.
additional_evidence_needed: none
dependencies: S01-002 (same class of staleness)
expected_improvement: §10.11 source-binding audit and §10.1 governance-consistency audit both become passable on the record.
post_revision_verification: grep for rel-2026-07-10 in project_configuration.md returns only text explicitly marked historical; the "Controlled analysis area" line names the 07-20 bundle.
status: open
```

### S01-004 — §10.14 page-count evidence is stale; shipped main text is at or over its own binding hard cap

```text
ticket_id: S01-004
review_stage: Stage 0 / Stage 1
reviewer_role: SE, supported by JCO
severity: Major
priority: P1
confidence: Confirmed (measurements) / Low (which of two B1 accountings the author intends)
issue_type: compliance
manuscript_location: papers/governance/phase_gate_register.csv (Phase 8, 9, 11 rows); papers/build_prompt_phases/phase_04/page_budget.md:24,103-107
claim_id_or_artifact_id: §10.14 page-limit hard rule; budget bound B1
concise_issue: The last recorded gate measurement is 35 pp total / B1 = 32 against a hard cap of 34; the shipped PDF is 39 pp with B1 = 34 (or 35 under a stricter reading), and no gate row records the shipped build.
exact_evidence_or_observation: |
  page_budget.md:24  B1 = "total typeset pages, main text INCLUDING exhibits, EXCLUDING references and back
                     matter -- target 28-34 pages; hard cap 34"; :104 "Headroom to hard cap ~2.1 pages".
  phase_gate_register.csv Phase 8 : "pdf compiled 34 pages total / B1=31 main-text pages (28-34 band,
                     <=34 hard cap PASS)" ; supplement "32 pages".
  phase_gate_register.csv Phase 11: "main B1=32pp<=34 cap PASS (35pp total incl refs+back matter),
                     supplement 32pp".
  phase_gate_register.csv Phase 9 : no page-count row found (grep over the row for /page/ returns none).
  SHIPPED (measured this session, PyMuPDF + main.log): DT-GSK.pdf = 39 pages; supplementary.pdf = 61 pages.
  Back matter begins on p.35 ("Author Contributions"); "Conflicts of Interest"/"Abbreviations" on p.36;
  "References" on p.37; LastPage = 39 (papers/main.aux \newlabel{LastPage}{{5.0.0.1}{39}}).
  => B1 = 34 counting whole pages before the back matter, or 35 if p.35 counts as main text (it still
  carries the closing Conclusions/limitations prose). Cap = 34.
root_cause: Four pages of main text and 29 pages of supplement were added after the Phase-11 packaging measurement (Phase-12 ablation integration, three external review rounds, R-01..R-14), with no re-measurement written back to the register.
scientific_or_editorial_justification: §10.14 requires (a) the main manuscript not to exceed the bound limit, (b) page counts measured from the compiled PDF at the Phase 8/9/11 gates with a row recorded for each, and (d) the measured evidence recorded in the review record. (b) and (d) are unmet for the shipped build; (a) is unverifiable from the record and is at best at zero margin.
impact_on_validity_or_acceptance: Not a scientific defect and not a desk-reject risk at MDPI (no published journal page cap; journal_requirements.md:30). It is an unmet hard rule of the governing framework, and the declared 2.1-page headroom no longer exists, so any further addition breaches the cap.
required_correction: Measure B1 and B2 on the shipped 39-page PDF, record a page-count row in phase_gate_register.csv for the current packaging state, and either (i) confirm B1 <= 34 under an explicitly stated counting rule, or (ii) migrate non-essential main-text material to the supplement per §10.14 (never by shrinking figures or cutting declarations), or (iii) file a change request formally revising B1 with the exemplar justification restated.
acceptable_alternatives: A change request that re-bases B1 on the current MDPI evidence is acceptable provided it is recorded before submission and does not silently retire the rule.
additional_evidence_needed: The author's intended B1 counting convention for a page that carries both closing main text and the first back-matter heading; the current B2 prose word count (no post-Phase-11 measurement exists; the 12,000-word cap is unverified).
dependencies: none
expected_improvement: §10.14 becomes verifiable on the shipped artifact rather than on a four-page-stale measurement.
post_revision_verification: A phase_gate_register.csv row stating "<n> pages total / B1=<m>" for DT-GSK.pdf sha256 3436276946abd7dd..., with m <= the then-current cap, plus a B2 word count against the 12,000 bound.
status: open
```

### S01-005 — Requirements traceability matrix line anchors no longer resolve

```text
ticket_id: S01-005
review_stage: Stage 0
reviewer_role: SE
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/governance/requirements_traceability_matrix.csv (2,153 rows, mtime 2026-07-14)
claim_id_or_artifact_id: §10.1 "MAY be seeded from requirements_traceability_matrix.csv"
concise_issue: Requirement ids are R-<line_no> into PAPER_BUILD_PROMPT.md, but the prompt has been edited since the RTM was minted, so the ids point at the wrong lines.
exact_evidence_or_observation: |
  papers/PAPER_BUILD_PROMPT.md is now 7,864 lines (mtime 2026-07-21). RTM max line_no = 7,469;
  phase_gate_register.csv (Phase 2) records "max line_no 7759 == total" for the then-current prompt.
  Spot checks against the CURRENT file:
    R-21   summary "Act as a coordinated multidisciplinary research team ..." -> line 21 is BLANK
    R-4131 summary "All generated outputs plus PHASE_6_gate_report.md ..."    -> line 4131 is BLANK
    R-6851 summary "DoD: reproducibility level recorded per artifact class"   -> line 6851 is
           "| 3 Dataset integrity | Gate 2 (Phase 2 review gate) |"
  Sample of the first 400 RTM rows: 175 summaries relocatable elsewhere in the file with offsets
  {+57 (25), +69 (18), +86 (43), +95 (36), +155 (15), +253 (13), ...}; 225 not verbatim-locatable.
  The RTM also has no status/verification-result column (schema: requirement_id,line_no,summary,phase,
  artifact,validation,owner), so it cannot be used as a compliance record even after re-indexing.
root_cause: The governing build prompt was revised after the traceability index was generated; the index was not regenerated.
scientific_or_editorial_justification: Stage 0 check 3 requires extracting every mandatory requirement from the governing development prompt. The project's own index into that prompt is the natural evidence for that extraction and it no longer resolves, so no compliance claim citing an R-<n> id is checkable.
impact_on_validity_or_acceptance: Internal traceability only; no manuscript claim depends on it. It does mean this review's compliance matrix had to be built independently rather than seeded (§10.1 permits seeding only after spot-verification, which fails here).
required_correction: Regenerate requirements_traceability_matrix.csv against the current PAPER_BUILD_PROMPT.md, or pin the RTM to the prompt revision it indexes (record that revision's hash in the CSV header or a sidecar).
acceptable_alternatives: Freeze a copy of the indexed prompt revision alongside the RTM.
additional_evidence_needed: none
dependencies: none
expected_improvement: Requirement ids resolve; §10.1 seeding path becomes usable.
post_revision_verification: Re-run the spot check: for a random sample of 20 rows, PAPER_BUILD_PROMPT.md line <line_no> contains the row's summary text.
status: open
```

### S01-006 — The governing review prompt's own §1.5 / §10.7 snapshot is stale (recorded per orchestrator instruction)

```text
ticket_id: S01-006
review_stage: Stage 0
reviewer_role: SE
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/PAPER_REVIEW_PROMPT.md §1.5 (lines 118-602, dated 2026-07-20); §10.7 final bullet (line 3299); §10.9 removal note (lines 3342-3345); §1.5 re-derivation instruction (line 124)
claim_id_or_artifact_id: review input contract
concise_issue: The prompt's embedded project snapshot predates the 2026-07-21/22 R-01..R-14 remediation and contradicts the repository on the ledger state, the runtime-table remedy, the freeze-manifest structure, and a supplement section number.
exact_evidence_or_observation: |
  (a) LEDGER. §1.5 asserts "73/80 fully closed ... seven terminal / machine-gated / author-gated tickets
      remain open (RT-001; C-008 -> C-001; N-009 / N-021 / M-007 / E-012)".
      REPO: governance/remediation_2026_07_18/ticket_status.csv = 80 rows, lifecycle_status
      {closed_verified: 70, superseded_with_evidence: 10} -- zero non-terminal rows.
  (b) RUNTIME TABLE. §10.7's RT-001 bullet says the runtime table is "being brought into single-environment
      comparability by re-timing all six comparators on one idle machine (scripts/retime_comparators.py)"
      and "mixes two measurement sessions ... provisionally frozen".
      REPO: the shipped Table 16 (DT-GSK.pdf p.33) is titled "Measured per-run wall-clock time of DT-GSK on
      CEC2017" and contains four DT-GSK rows only; validate_runtime_provenance.py reports one cell
      (dt-gsk, 2026-07-18T18:23:52, commit 251fc8cb8, host HUAWEI-MMASOUD) and prints "The DT-GSK-only
      runtime table is single-session". RT-001 was resolved by narrowing the table's SCOPE, not by re-timing
      the comparators the prompt describes. The prompt's instruction "do not certify them as a settled
      single-environment comparison" no longer matches a table that makes no comparison.
  (c) FREEZE MANIFEST. §1.5 line 124 tells the panel to re-derive the snapshot from "the append-only
      *_refreeze blocks of main_manuscript_freeze_manifest.json (through abstract_retrim_and_F_hygiene_refreeze)".
      REPO: _pending_refreeze.json:39 records that the manifest was "minted FRESH (15 files ...;
      68 *_refreeze history blocks retired)"; no *_refreeze block exists in the current manifest.
  (d) SUPPLEMENT NUMBERING. §10.9 warns that any reference to "the former §S6.7 oracle / estimator-fidelity
      study" is a dangling-reference defect. REPO: S6.7 has been REUSED for "Implementation Caveats: Two
      Corrected Defects and Their Evidence Trail" (supplementary.pdf p.60) and is legitimately cited twice by
      the main text (p.32, p.33). The token "oracle" occurs 0 times in both rendered documents -- the removal
      is clean, but a reviewer following §10.9 literally would misread the live S6.7 citations as dangling.
  (e) RELEASE ID. §1.5 is correct here: rel-2026-07-20-67d9345f9 / abl-rel-2026-07-20 match the repo.
root_cause: The snapshot was written on 2026-07-20 and the D2-review remediation landed on 2026-07-21/22.
scientific_or_editorial_justification: §1.4 ranks the current project requirement above the governing prompt's embedded snapshot; leaving the contradiction unrecorded invites later seats to re-raise closed items (b, d) or to accept a stale ledger count (a).
impact_on_validity_or_acceptance: Process risk only. Item (b) additionally hands Stage 8/9 a real scope question: with a DT-GSK-only runtime table, the manuscript reports no comparator overhead comparison, and §10.13 lists "missing non-objective overhead analysis" as a rejection risk. That adjudication belongs to Stage 8/9, not to this seat.
required_correction: Re-date §1.5 to the 2026-07-22 state (ledger 80/80 terminal; R-01..R-14 applied; runtime table narrowed to DT-GSK-only; freeze manifest freshly minted with no refreeze blocks; S6.7 re-used). Correct §10.7's RT-001 bullet and §10.9's S6.7 removal note.
acceptable_alternatives: Append a §1.5.0-D block rather than rewriting, provided it is marked as governing.
additional_evidence_needed: none
dependencies: none
expected_improvement: Later review seats stop re-litigating closed items and stop trusting a superseded ledger count.
post_revision_verification: §1.5 ledger figures equal the ticket_status.csv counts; §10.7 describes the shipped table; §10.9 names the correct removed-content location.
status: open
```

### S01-007 — Residual stale statements inside the re-minted freeze record

```text
ticket_id: S01-007
review_stage: Stage 0
reviewer_role: SE
severity: Minor
priority: P2
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/governance/main_manuscript_freeze_manifest.json:16, :100 ; papers/governance/_pending_refreeze.json:15, :51
claim_id_or_artifact_id: freeze attestation block
concise_issue: Three statements inside the freeze record describe the state before the 2026-07-22 17:51 amendment.
exact_evidence_or_observation: |
  (a) build_environment.docx_note = "committed deterministic renders via papers/scripts/build_docx.py;
      not re-emitted this pass" -- but git show --stat 45248eb31 shows DT-GSK.docx changed
      (Bin 1036876 -> 1037004 bytes) in the same commit that re-minted this manifest, and the manifest's
      own pinned DOCX hash was updated in that diff (647028d5... -> 1ad8c3b2...).
  (b) validator_outputs_at_freeze.validate_cross_format_parity = "0 (578 rows, FAIL=0)" -- the shipped build
      produces 579 rows: the committed governance/cross_format_consistency.csv has 579 data rows and my
      independent regeneration to scratchpad was byte-identical to it (FAIL=0, exit 0).
  (c) _pending_refreeze.json:15 R-03 still reads "build-path fix DONE, rebuild pending", although the same
      file's resolution field and my own DOCX scan (0 literal '&' in 753 + 640 m:oMath blocks) show the
      rebuild landed; and the ledger's closed_utc is 2026-07-22T00:00:00Z, i.e. BEFORE the 17:51 amendment,
      which therefore has no refreeze-ledger entry at all.
root_cause: The amendment updated hashes and the freeze_statement but not the attestation and note fields, and did not reopen/close the refreeze ledger.
scientific_or_editorial_justification: A freeze attestation is evidence; internally contradicted evidence weakens the whole provenance chain even when each individual gate passes.
impact_on_validity_or_acceptance: Low. All named gates independently re-verify GREEN in this session.
required_correction: Refresh docx_note and the validator_outputs_at_freeze block from a fresh run at the final commit, and add a short ledger entry covering the 45248eb31 amendment.
acceptable_alternatives: Delete the row-count from the parity attestation and keep only the FAIL count, which is the property that matters.
additional_evidence_needed: none
dependencies: S01-001 (fix in the same stamping commit)
expected_improvement: The attestation block matches a re-run at the final commit.
post_revision_verification: Re-run all seven validators at the stamped commit; every recorded output equals the observed output.
status: open
```

### S01-008 — Supplement source header still names the superseded 07-16 release

```text
ticket_id: S01-008
review_stage: Stage 0
reviewer_role: SE
severity: Minor
priority: P3
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/supplementary.tex:6
claim_id_or_artifact_id: R-06 (supplement release identity)
concise_issue: The hash-pinned supplement source still carries a header comment asserting the superseded release as the provenance of every empirical value.
exact_evidence_or_observation: |
  papers/supplementary.tex:1-6 (comment block):
    "%% ... Every empirical value traces to evidence release rel-2026-07-16-78f075cb0."
  R-06 corrected the RENDERED identity and did so correctly: supplementary.pdf p.44 item 7 reads
    "Current release (anchor 67d9345f9). The evidence accompanying this article is release
     rel-2026-07-20-67d9345f9 (anchor commit 67d9345f9502a9a584e645fa8948f60a61d70e29; 3,403 files),
     which supersedes rel-2026-07-16-78f075cb0."
  and p.43 item 6 explicitly demotes the 07-16 release to "a link in the provenance chain".
  The hardened validate_provenance_claims.py exits 0 because it strips comments -- correct behaviour, but it
  means the stale line is invisible to the gate.
root_cause: R-06 targeted rendered surfaces; the source header was not in its scope.
scientific_or_editorial_justification: §1.4 ranks comments last, so this is not an authority conflict; but the line sits inside a file pinned by the freeze manifest and states a false provenance for the whole supplement.
impact_on_validity_or_acceptance: Not reader-facing; no gate fails. It is an incomplete closure of R-06 in the source.
required_correction: Update the header comment to rel-2026-07-20-67d9345f9 (or to a non-versioned phrase deferring to the provenance appendix) and re-mint the supplementary.tex hash. Note the file is NOT currently pinned by name in the freeze manifest, so no manifest edit is required -- see the note in S01-012.
acceptable_alternatives: Delete the release clause from the comment entirely.
additional_evidence_needed: none
dependencies: none
expected_improvement: Every occurrence of the superseded id in a current-state artifact is either removed or explicitly labelled historical.
post_revision_verification: grep -n "rel-2026-07-16" papers/supplementary.tex returns only lines whose surrounding text marks the release as superseded.
status: open
```

### S01-009 — §10.1 governance-package path bindings do not resolve

```text
ticket_id: S01-009
review_stage: Stage 0
reviewer_role: SE
severity: Minor
priority: P2
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/PAPER_REVIEW_PROMPT.md §10.1 binding table (lines 3172-3180); papers/governance/
claim_id_or_artifact_id: GOVERNANCE_AND_GATE_ARTIFACTS binding
concise_issue: Two of the artifacts the profile binds to papers/governance/ live elsewhere, and one named artifact does not exist anywhere.
exact_evidence_or_observation: |
  MISSING at the bound path, present elsewhere:
    papers/governance/statistical_analysis_plan.md -> papers/build_prompt_phases/phase_05/statistical_analysis_plan.md
    papers/governance/exhibit_plan.csv             -> papers/build_prompt_phases/phase_04/exhibit_plan.csv
  NOT FOUND anywhere: the "external-gate mapping" artifact
    (find . -iname "*external_gate*" -o -iname "*gate_mapping*" -> 0 hits outside .git)
  PRESENT as bound: project_configuration.md, claims_evidence_matrix.csv, reference_inventory.csv,
    evidence_cards/, phase_gate_register.csv, reproducibility_manifest.json, artifact_binding.csv,
    cross_format_consistency.csv, word_validation_report.md, requirements_traceability_matrix.csv,
    presentation_conventions.md.
root_cause: The build framework keeps phase deliverables under papers/build_prompt_phases/<phase>/; the review profile's binding table assumes a flat governance directory.
scientific_or_editorial_justification: §1.3 requires every missing input to be recorded with its downstream effect and forbids inference. Two of the three are locatable, so the affected gates are not blocked; the third must be recorded as genuinely absent.
impact_on_validity_or_acceptance: Low. A seat that follows §10.1 literally will report a missing statistical analysis plan and a missing exhibit plan, which would be a false finding.
required_correction: Either add pointer stubs at the bound paths, or amend the §10.1 binding table to the real locations; for the external-gate mapping, either produce it or record it as an accepted absence with a scope note.
acceptable_alternatives: A single governance/README.md index mapping each §10.1 binding to its real path.
additional_evidence_needed: whether the "external-gate mapping" was ever a required build deliverable or is a review-profile-only concept.
dependencies: none
expected_improvement: Downstream seats resolve every §10.1 binding on the first attempt.
post_revision_verification: Every path in the §10.1 binding table resolves to an existing file.
status: open
```

### S01-010 — `\supplementary{}` package listing under-describes Supplement S6

```text
ticket_id: S01-010
review_stage: Stage 1
reviewer_role: JCO
severity: Minor
priority: P3
confidence: Confirmed
issue_type: production
manuscript_location: papers/main.tex:186-200 (\supplementary{...}); rendered back matter
claim_id_or_artifact_id: three-way main-text <-> conclusions <-> supplement agreement (Stage 1)
concise_issue: The MDPI supplementary-materials listing describes S6 as a remove-one decomposition plus an ISM isolation, omitting the two S6 subsections the main text sends readers to.
exact_evidence_or_observation: |
  main.tex:196-200 describes S6 as "a supplement-only component-contribution study --- a scaffold remove-one
  decomposition and a direct isolation of the interaction-structure memory ... (S6)".
  Actual supplement subsections (supplementary.pdf, headings extracted):
    S6.1 Remove-One Design | S6.2 Statistical Treatment | S6.3 Findings (Conditional, ISM Off)
    S6.4 What This Study Does Not Establish | S6.5 ISM-Overlay Isolation: Direct Component Study
    S6.6 Conditional-Benefit Analysis by Function Class (Post-Hoc)
    S6.7 Implementation Caveats: Two Corrected Defects and Their Evidence Trail
  Main text cites the two omitted ones: p.3 "(Supplementary Materials, Sections S6.5 and S6.6)";
  p.32 "The isolated compute cost ... is quantified in the Supplementary Material (Section S6.7)";
  p.33 "The isolated interaction-structure-memory overhead is reported in ... Section S6.7."
  The S1-S6 top-level inventory itself is consistent (validate_document_consistency.py: labels contiguous
  S1..S6, 6 actual sections, exit 0).
root_cause: The \supplementary block was authored when S6 had four subsections; S6.6 and S6.7 were added later.
scientific_or_editorial_justification: Stage 1 requires the package listing of supplementary contents to match what the supplement contains AND what the main text asserts it contains. A reader following the p.32/p.33 overhead pointer finds a section the package listing never announced.
impact_on_validity_or_acceptance: Editorial completeness of the MDPI back matter; no claim is affected.
required_correction: Extend the S6 clause to name the function-class analysis and the implementation-caveats/evidence-trail subsection.
acceptable_alternatives: Replace the enumerated S6 description with a subsection list "S6.1-S6.7".
additional_evidence_needed: none
dependencies: none
expected_improvement: Package listing, main text, and supplement agree three ways.
post_revision_verification: Every S6.x subsection cited in the main text appears in, or is covered by, the \supplementary listing.
status: open
```

### S01-011 — Stale exclusion record in the submission package manifest

```text
ticket_id: S01-011
review_stage: Stage 1
reviewer_role: JCO
severity: Editorial
priority: P3
confidence: Confirmed
issue_type: production
manuscript_location: papers/governance/submission_package_manifest.json:51-57
claim_id_or_artifact_id: excluded_from_package
concise_issue: The manifest lists papers/DT-GSK_visio.docx with a byte count and an outstanding instruction to remove it; the file no longer exists.
exact_evidence_or_observation: |
  submission_package_manifest.json:53-55 "path": "papers/DT-GSK_visio.docx", "bytes": 1641812,
    "reason": "... author to `git rm` before the authoritative commit."
  ls papers/DT-GSK_visio.docx -> No such file or directory
  git ls-files | grep -i visio -> only revision_log.md, revision_tickets.csv, build_visio_flowcharts.py,
    embed_visio_ole.py (no .docx)
root_cause: The removal happened; the record was not updated.
scientific_or_editorial_justification: Stage 1 requires the package to contain no obsolete or contradictory file record that could mislead packaging.
impact_on_validity_or_acceptance: None. Recorded so the accidental-submission check is closed on the record, not just in fact.
required_correction: Mark the entry "removed 2026-07-2x (commit <sha>)" or drop it.
acceptable_alternatives: none needed
additional_evidence_needed: none
dependencies: none
expected_improvement: The exclusion register reflects reality.
post_revision_verification: The manifest either omits the entry or marks it satisfied.
status: open
```

### S01-012 — Supplement `.tex` source is not pinned by the freeze manifest (observation → ticket)

```text
ticket_id: S01-012
review_stage: Stage 0
reviewer_role: SE
severity: Minor
priority: P2
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/governance/main_manuscript_freeze_manifest.json "files" array (15 entries)
claim_id_or_artifact_id: freeze coverage
concise_issue: The manifest pins the five main-text section sources, main.tex, references.bib, three governance CSVs, and all five rendered deliverables -- but NOT papers/supplementary.tex, the canonical source of the 61-page supplement.
exact_evidence_or_observation: |
  Pinned (15): main.tex; sections/{introduction,related_work,proposed_algorithm,performance,conclusions}.tex;
  DT-GSK.pdf; DT-GSK.docx; supplementary.pdf; supplementary.docx; cover_letter.pdf;
  governance/{claims_evidence_matrix.csv, citation_usage_map.csv, artifact_binding.csv}; references.bib.
  Absent: papers/supplementary.tex (125,152 B), papers/cover_letter.tex, papers/tables/*.tex.
  Consequence: supplementary.tex can be edited without check_manifest.py detecting it; only the rendered
  supplement PDF/DOCX hashes would move, and only if someone rebuilds.
root_cause: The 2026-07-21 fresh mint enumerated the main-manuscript sources plus rendered outputs.
scientific_or_editorial_justification: §10.12 requires "one canonical semantic source" for the manuscript; the supplement's canonical source is outside the freeze envelope, so a source<->PDF desync in the supplement is not detectable by the project's own integrity check.
impact_on_validity_or_acceptance: No current desync exists (the shipped supplementary.pdf/.docx are pinned and parity is 0 FAIL). The gap is in the detector, not the artifact.
required_correction: Add papers/supplementary.tex (and, for completeness, papers/cover_letter.tex and papers/tables/*.tex) to the pinned file list at the next mint.
acceptable_alternatives: Pin a single SHA-256 over the concatenated table/source set rather than 20 individual rows.
additional_evidence_needed: none
dependencies: S01-001, S01-008 (all three are fixed at the next mint)
expected_improvement: check_manifest.py detects any edit to the supplement source.
post_revision_verification: Modify one byte of papers/supplementary.tex in a scratch checkout; check_manifest.py must report a mismatch.
status: open
```

---

## 7. Verified-correct closures and clean checks (recorded so later seats do not re-open them)

Confirmed **correctly and completely closed** by direct inspection of the shipped artifacts:

| Item | Verification |
|---|---|
| R-01 (Eq. 4 per-phase signs) | `s_J` and `s_S` render in `DT-GSK.pdf` (4 and 5 occurrences); the sign convention is in body text, not a comment |
| R-03 (DOCX OMML literal `&`) | 0 of 753 (`DT-GSK.docx`) and 0 of 640 (`supplementary.docx`) `m:oMath` blocks contain `&amp;` |
| R-04 (restart invariant) | "deep-stall" ×16 with "resampl*" ×6 in the rendered main text |
| R-05 (budget-crossing semantics) | rendered in `performance.tex` → PDF **and** DOCX: "That crossing falls only on the terminal generation …", "confers no search advantage" |
| R-06 (supplement release identity) | rendered supplement p.44 names `rel-2026-07-20-67d9345f9` as current and demotes 07-10/07-16 to labelled provenance links. **Rendered layer correct**; only the source header remains stale (S01-008) |
| R-07 (hardened provenance gate) | `validate_provenance_claims.py` exits 0 on source *and* rendered artifacts; comment stripping demonstrably active (it does not fire on `supplementary.tex:6`) |
| R-08 (ISM not a fourth contribution) | conclusions p.35: "…rather than as a fourth claimed contribution"; C1–C3 labels only |
| R-09 (cover letter) | 0 reviewer placeholders; byte-stability language present and scoped |
| R-10 (typo) | "credit credit" → 0 occurrences |
| R-11 (bounds notation) | per-coordinate / coordinate-wise phrasing ×5 |
| R-12 (phase-gate write-back) | Phase 12 row `state = FROZEN` |
| R-14 (budget-crossing probe) | `tests/regression/test_budget_crossing_semantics.py` exists (151 lines, added at `dbc824782`) and is cited in `performance.tex` as a `%`-comment evidence pointer |

Clean checks with no finding: seven-method panel present (GSK, AGSK, APGSK, FDB-AGSK, ATMALS-GSK, eGSK, DT-GSK — `papers/tables/T16.tex`); 0 overfull hboxes; 0 unresolved references; no tracked changes/comments/hidden text; no placeholder tokens; no orphan section or table source; the excluded Visio working file is genuinely gone; the removed oracle study leaves **no** dangling reference (token "oracle" absent from both rendered documents).

**Observation handed to Stage 13/15 (not ticketed by this seat).** §10.17.4 permits "a *single*, deliberately placed archival identifier … in the Data-Availability / reproducibility statement". The rendered supplement's provenance appendix contains 7 release ids, one 40-hex anchor commit, four module hashes and a Merkle digest. All of it is concentrated in the S5 chronological-provenance appendix adopted deliberately under ticket M-031, and the main text and cover letter are clean, so this seat treats it as compliant-by-design. Whether that density is the "once, in the appropriate place" §10.17.4 intends is a Stage 13/15 presentation judgement, not a Stage 0/1 package-integrity question.

**Second hand-off.** The runtime table is now DT-GSK-only (S01-006 item b). §10.13 lists "missing non-objective overhead analysis" among the hard rejection risks. Stage 8/9 must decide whether a single-algorithm runtime table satisfies that control now that the comparator re-timing described in §10.7 was replaced by a scope narrowing.

---

## 8. Stage decisions

**Stage 0 — Review preflight, authority extraction, version freeze: `PASS` (with 4 open P1 tickets).**
No hard-fail condition of lines 1284–1291 is met. Specifically: the manuscript and supporting results come from one consistent version (§3); source, PDF and Word all resolve to one frozen scientific state; the documented post-freeze re-freezes left no stale existence/availability/comparability statement in the rendered artifacts (R-05/R-06 verified closed); no orphan or superseded source file carrying prohibited or contradictory content remains in the build path; the governing prompt is located; central evidence is identified (`rel-2026-07-20-67d9345f9`); the article type (`article`, MDPI *Algorithms*) is compatible with the structure; and no prior draft is under review. The four P1 tickets (S01-001…S01-004) are **record-level** defects in the freeze pointer, the reproducibility manifest, the analysis-area binding, and the page-count evidence. **S01-001 must be closed before the package is archived or distributed under the declared anchor**, at which point it would become a reproducibility hard-fail.

**Stage 1 — Package completeness and technical intake / `Gate A — Package Integrity`: `PASS`.**
One authoritative manuscript state is identifiable (worktree at `45248eb31`, pinned 15/15) and every essential file is readable and complete. §10.1's Gate-A precondition is satisfied: `phase_gate_register.csv` carries an evidenced `FROZEN` row for every build gate 0–12.

**Conditional element.** Journal-side verification (Stage 0 check 6) is **`BLOCKED` on an external input**: the official MDPI *Algorithms* instructions were unreachable at Phase 4 (HTTP 403) and were not re-fetched in this session. Length policy, blinding model, supplement file rules and declaration ordering therefore rest on search-derived evidence. Per §1.3 this is *administratively* blocked, not scientifically incomplete, and it does not gate Stage 0 or Gate A; it must be discharged by Stage 17 before submission.

---

## 9. Commands run (all read-only; two redirected away from governance)

```
git rev-parse HEAD ; git log --oneline -8 ; git show --stat 45248eb31 dbc824782
git show <commit>:<path> | sha256sum                       # anchor-vs-pinned hash comparison
python papers/scripts/check_manifest.py                    # 15/15, exit 0
python papers/scripts/validate_build_hygiene.py            # exit 0
python papers/scripts/validate_provenance_claims.py        # exit 0
python papers/scripts/validate_document_consistency.py     # exit 0
python papers/scripts/validate_runtime_provenance.py       # exit 0
python papers/scripts/validate_cross_format_parity.py --csv <scratchpad>/xfmt.csv   # 579 rows, FAIL=0
python papers/scripts/validate_evidence_bindings.py  --csv <scratchpad>/bind.csv    # exit 0, 0 FAIL
# PyMuPDF/zipfile inspection of the three PDFs and both DOCX (page counts, text probes,
# placeholder scan, image resolutions, OMML/tracked-change/comment scan)
```

The two `--csv` validators default to writing `papers/governance/cross_format_consistency.csv` and an evidence-binding CSV; both were redirected to the session scratchpad so that no file outside `papers/review_2026_07_22/` was modified. The redirected parity output was compared to the committed governance CSV and found byte-identical.
