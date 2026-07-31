# DT-GSK — Revision Roadmap (Stage 20)

**Dependency-aware correction program · Supervising Editor · Editorial Coordination Board**
Companion to `issue_register.csv`, `review_scorecard.csv`, `final_readiness_report.md`, `post_revision_verification.csv`.

---

## Standing constraints (bind every work item)

1. **No rerun.** No optimizer executes. No evidence is regenerated from computation.
2. **No new evidence release.** `rel-2026-07-20-67d9345f9` and `abl-rel-2026-07-20` are terminal for this cycle.
3. **The DT-GSK optimizer core is byte-locked.** Where prose and frozen code disagree, **correct the paper** (section 10.6).
4. **Exhibit regeneration is permitted and required** — it reads the frozen release and produces no new evidence.
5. **Do not polish prose around a claim that may later be removed** (Stage 20 revision order). This is why W06 precedes W07, W08 and W15.
6. **Do not close a ticket because text changed.** Close it only when its `post_revision_verification.csv` row passes (section 5.4).

## Dependency graph

```
                      W06  thesis framing decision  (SE-030)
                        |
        +---------------+---------------+
        |               |               |
       W07            W08             W15   (language, LAST of the claim chain)
   effect size    claim narrowing
   + omnibus
        |
        +--> W09/W10/W11/W12  exhibit regeneration
                        |
   W02 protocol disclosure  W03 GenAI  W04 attestation  W05 stats governance
        |                       |          |               |
        +-----------------------+----------+---------------+
                                |
                     W13 structure   W14 budget
                                |
              W16 Word  W17 citations  W18 class  W19 governance
                                |
                     W01  freeze re-mint  (SE-003, SE-004)  <-- MUST BE LAST
                                |
                     W20  full rebuild + all gates + Gate Q
```

**W01 is listed first in the register by dependency class (evidence/integrity) but is EXECUTED LAST.** Re-stamping the freeze before the text edits land would immediately invalidate it. This is the single most important sequencing instruction in the roadmap.

---

## Work items (Appendix A.8 schema)

### W06 — Decide the thesis framing (do this first)

```text
work_item_id            : W06
source_ticket_ids       : SE-030, SE-015 (framing half), SE-021 (framing half)
root_cause              : The organising question and the stated gap are ISM-shaped; the ISM result is
                          the null. The narrative was built around ISM before the isolation returned
                          null and was re-scoped at the claim level but never at the framing level.
required_action         : Author-and-editor decision, then a targeted rewrite of the introduction's
                          organising question, the related-work gap sentence, and the conclusions'
                          opening frame. Recommended direction: organise around dimension-tiered
                          control plus a deterministic budget-exact endgame (what the evidence
                          supports), and present the ISM null as a bounded negative result inside that
                          frame. Add one result-free Discussion paragraph naming the alternatives the
                          design does not exclude (deterministic endgame close to classical direct
                          search; development-suite selection exposure).
scientific_or_editorial : editorial (framing) with scientific consequence for Gate D
owner_role              : EIC + corresponding author
dependencies            : none - this is the root of the claim chain
required_inputs         : final_readiness_report.md 12.2 and 12.9; supplementary S6.5/S6.6
artifacts_to_change     : papers/sections/introduction.tex, related_work.tex, conclusions.tex
artifacts_to_regenerate : DT-GSK.pdf, DT-GSK.docx (deferred to W20)
verification_method     : Read title -> abstract -> introduction -> method -> results -> conclusions
                          as one chain; confirm the organising question matches the supported evidence;
                          re-run the section 10.9 leak test on the Discussion paragraph (must be
                          result-free - no "did/did not confirm", no direction, no p-value or effect).
completion_criterion    : One coherent thesis readable end to end; the null appears as a bounded
                          negative result, never as the question the paper set out to answer.
priority                : P1
status                  : open
```

### W07 — Effect-size referent and omnibus columns

```text
work_item_id            : W07
source_ticket_ids       : SE-001, SE-007, SE-019, SE-042
root_cause              : M-027 migrated Table 14 from A12 to rank-biserial r and M-026 introduced the
                          tie correction; both updated the caption and the declaration but not the
                          results prose.
required_action         : (a) Settle one referent. Recommended: keep Table 14 as r, delete the four
                          A12 quotations or restate them as r values read off the table, and collapse
                          the duplicated rank-biserial definition at performance.tex:227-231 into the
                          single statement at :209-213. (b) Print the CORRECTED omnibus column for all
                          three suites and fix the CEC2013 caption bound. (c) Correct the
                          scale-invariance sentence: the Friedman ranking is invariant to per-function
                          monotone rescaling, the across-function Wilcoxon is not, and the tie band was
                          verified not to change any Holm decision. (d) State the R+/R- convention in
                          the caption and in the released workbook header.
scientific_or_editorial : scientific (printed specification)
owner_role              : R-stats + corresponding author
dependencies            : W06
required_inputs         : papers/analysis/rel-2026-07-20-67d9345f9/primary_stats/statistical_results.csv;
                          papers/tables/T15.tex; statistical_audit.md
artifacts_to_change     : papers/sections/performance.tex; optionally papers/tables/T15.tex and the
                          released effect-size workbook header
artifacts_to_regenerate : T15.tex only if the A12 column is restored; PDF/DOCX at W20
verification_method     : post_revision_verification.csv rows 3 and 4; extend
                          validate_evidence_bindings.py to compare every quoted statistic against a
                          released CSV column (this is the control whose absence let the defect survive
                          three review rounds).
completion_criterion    : Zero prose references to a column the table does not print; every printed
                          omnibus p equals the corrected column; one definition per statistic.
priority                : P1
status                  : open
```

### W02 — Protocol-disclosure paragraph (budget, population, determinism, eGSK)

```text
work_item_id            : W02
source_ticket_ids       : SE-002, SE-008, SE-009, SE-011, SE-047
root_cause              : Four fairness and reproducibility statements were written to describe
                          properties that hold for DT-GSK and were generalised over the panel.
required_action         : Rewrite one paragraph of Section 4.1 plus the Table 3 provenance note to
                          state, accurately: (a) no optimizer is charged more than MaxFES, and AGSK and
                          APGSK additionally stop at the 1e-8 target error in 1,845 of 75,250 released
                          runs, which cannot advantage them because the recorded error is already at
                          the reporting floor; (b) the executed population sizes - comparators NP=100
                          at every dimension, DT-GSK NP_init=5D - with the actual constant source
                          cited, plus a limitations sentence conceding the asymmetry is uncontrolled;
                          (c) the determinism property scoped to DT-GSK single-threaded, with a
                          one-sentence disclosure that comparator re-execution across producer commits
                          was measured NOT bit-reproducible (3,772 scientific-column diffs) and that the
                          frozen release is the single citable state; (d) the eGSK SLSQP substitution
                          extended from runtime to performance, with the class-B classification;
                          (e) the budget-crossing verification re-anchored on the structural
                          counted-prefix invariant, with the regression probe as its check.
scientific_or_editorial : scientific (disclosure; changes no number)
owner_role              : R-design + R-method + corresponding author
dependencies            : none (independent of W06); may proceed in parallel
required_inputs         : the termination census (1,845); the seven run_config.json files; the RT-001
                          closure record; experimental_design_audit.md
artifacts_to_change     : papers/sections/performance.tex; Table 3 (tab:panel); conclusions.tex
                          limitations
artifacts_to_regenerate : PDF/DOCX at W20
verification_method     : post_revision_verification.csv rows 5, 6, 11
completion_criterion    : Every fairness and reproducibility statement in the manuscript is true of the
                          shipped release when checked against it directly.
priority                : P1
status                  : open
```

### W03 — GenAI declaration

```text
work_item_id            : W03
source_ticket_ids       : SE-010
root_cause              : The declaration asserts an absolute exclusion ("its implementation ...
                          independently of any AI system") broader than the authors can support, while
                          the accurate and sufficient claims sit in the same sentence.
required_action         : Narrow to: AI assistance was used for language editing, drafting of
                          descriptive prose, and software-engineering support during development; no AI
                          system designed an experiment, produced or altered any datum, computed any
                          statistic, or generated any scientific claim, result or conclusion; every
                          reported number was produced by the authors' deterministic pipeline from the
                          version-locked archive. Name every model version used per MDPI's
                          [tool name, version] requirement. Apply IDENTICALLY at all four loci:
                          main.tex:265-271, main.tex:280-283 (Acknowledgments),
                          performance.tex:189-190, and the cover letter.
scientific_or_editorial : editorial with publication-integrity consequence (Gate O)
owner_role              : JCO + corresponding author
dependencies            : none
required_inputs         : the author's confirmed tool/version list; ai_disclosure_audit.md
artifacts_to_change     : papers/main.tex, papers/sections/performance.tex, papers/cover_letter.tex,
                          papers/cover_letter.md; papers/scripts/validate_document_consistency.py
artifacts_to_regenerate : PDF/DOCX/cover letter at W20
verification_method     : post_revision_verification.csv row 10; extend
                          validate_document_consistency.py:192-202 beyond the cover letter to the three
                          manuscript loci.
completion_criterion    : The declaration is accurate against the repository's own public metadata and
                          names every tool version; the validator covers all four loci.
priority                : P1
status                  : open
```

### W04 — Selection-exposure attestation (zero compute)

```text
work_item_id            : W04
source_ticket_ids       : SE-014 (MX-04, essential_before_submission)
root_cause              : A prior revision removed a specific unverifiable count without replacing it
                          with an attested one, leaving the disclosure weaker than before.
required_action         : Author attestation in supplement S5.3 (with the main-text echo): how many
                          full-panel candidate configurations were evaluated, on which cells, and by
                          what criterion the shipped profile was chosen. Retain the existing statement
                          that the search lies outside the immutable release. If the exact count is
                          unrecoverable, state an upper bound and say it is a bound.
scientific_or_editorial : scientific (multiplicity disclosure)
owner_role              : corresponding author
dependencies            : none
required_inputs         : author recollection and development history
artifacts_to_change     : papers/supplementary.tex S5.3; papers/sections/performance.tex echo
artifacts_to_regenerate : supplement PDF/DOCX at W20
verification_method     : post_revision_verification.csv row 14
completion_criterion    : A number (or an explicit bound), the cells, and the criterion all render.
priority                : P1
status                  : open
```

### W05 — Statistical governance backfill

```text
work_item_id            : W05
source_ticket_ids       : SE-020, SE-046
root_cause              : Analysis-plan governance stopped being updated once the numbers stabilised.
required_action         : Log D-0016..D-0018 for M-026/027/028 with dates and rationale; assign a SAP
                          ID to the AN-GHOLM-2017 family; add A.7 register rows for the three
                          pre-registered ablation families and the two post-hoc checks; correct the
                          scipy attribution to name the in-repo statistics.wilcoxon_paired and record
                          that it was cross-checked against SciPy and the exact test with 0 Holm
                          decision changes; emit the BCa rank intervals as a released CSV with register
                          rows and re-point the generator default off the superseded release; print the
                          CEC2013 pairwise matrix in the supplement; reconcile the "single release" vs
                          "distinct immutable ablation release" wording; state the ablation omnibus
                          statistic accurately and disclose the floor-sensitivity surrogate.
scientific_or_editorial : scientific (governance and reporting completeness; changes no number)
owner_role              : R-stats
dependencies            : W07 (effect-size decision determines one register row)
required_inputs         : statistical_audit.md; results_integrity_audit.md; the frozen SAP
artifacts_to_change     : papers/governance/decision_log.md; the A.7 register;
                          papers/analysis/rel-2026-07-20-67d9345f9/ derived outputs (read-only
                          re-derivation, no rerun); papers/supplementary.tex
artifacts_to_regenerate : the BCa interval CSV and the CEC2013 pairwise matrix (derived, not measured)
verification_method     : Assert every reported statistic has an A.7 row and every reported interval
                          has a released CSV row; assert decision_log.md covers every post-freeze
                          analysis change.
completion_criterion    : No reported statistic lacks a machine-readable row; no post-outcome change is
                          unlogged.
priority                : P2
status                  : open
```

### W08 — Claim narrowing

```text
work_item_id            : W08
source_ticket_ids       : SE-015, SE-016, SE-017, SE-021, SE-028, SE-043, SE-047
root_cause              : Claim wording drifted ahead of the evidence during narrative passes, and one
                          post-freeze data recovery was never reflected in the prose.
required_action         : Correct "each scaffold subsystem" and name the three ablation exclusions;
                          narrow C2 so its originality claim does not rest solely on an untested
                          element; add the parameter-sensitivity absence as a limitation; update the
                          APGSK availability sentence and the Figure 4 caption to the recovered cells
                          while keeping the runtime correctly unavailable; restate the ISM null as a
                          failure to detect under the stated design and import the S6.6 caveat into the
                          conclusions; fix the limitations count, add the self-initialization asymmetry,
                          and label the post-hoc class analysis exploratory wherever it appears outside
                          S6.6; scope or evidence the abstract's CEC2013 Nemenyi leg.
scientific_or_editorial : scientific (claim scope)
owner_role              : RI (claims) + corresponding author
dependencies            : W06
required_inputs         : claim_audit.csv; section 12.9 of the readiness report
artifacts_to_change     : introduction.tex, proposed_algorithm.tex, performance.tex, conclusions.tex,
                          supplementary.tex, main.tex abstract
artifacts_to_regenerate : PDF/DOCX at W20
verification_method     : post_revision_verification.csv rows 12, 13, 15; re-run the claim audit
                          against the revised text.
completion_criterion    : Every claim in section 12.9 reads as its "after correction" form; no false
                          existence claim survives.
priority                : P1
status                  : open
```

### W09 — Convergence figure regeneration

```text
work_item_id            : W09
source_ticket_ids       : SE-005
root_cause              : generate_full_convergence.py:150-151 places a seven-entry single-row legend
                          at fontsize=9 on a canvas narrower than the legend, and line 153 saves with
                          exact_size=True (bbox_inches=None) so matplotlib does not expand the box.
required_action         : Change to a wrapped legend (ncol=4, two rows) or a smaller legend font, and
                          save with bbox_inches='tight' or a widened canvas. Regenerate all 25 figures.
                          Re-measure every output.
scientific_or_editorial : editorial (presentation); NO data change - the figures read the same frozen
                          checkpoint logs
owner_role              : VIZ
dependencies            : none technically; schedule with W10-W12 as one regeneration batch
required_inputs         : the frozen release checkpoint logs (unchanged)
artifacts_to_change     : papers/scripts/generate_full_convergence.py
artifacts_to_regenerate : all 25 papers/figures/convergence/*.pdf, the DOCX rasters, PDF, DOCX
verification_method     : post_revision_verification.csv row 7 - for every figure PDF assert
                          min(x0) >= 0 and max(x1) <= page width over all extracted words. ADD THIS
                          ASSERTION TO validate_build_hygiene.py so the regression cannot recur.
completion_criterion    : Zero off-canvas glyphs in all 25 figures; all seven series labelled and
                          readable in Figures 6 and 7.
priority                : P1
status                  : open
```

### W10 — Figure 4 rescale · W11 — Table A19 · W12 — Exhibit consistency

```text
work_item_id            : W10
source_ticket_ids       : SE-013
required_action         : Regenerate generate_nemenyi_cd.py output at the embedded size so in-figure
                          text is >= 8 pt at \textwidth, and use a shared x-limit across the four
                          comparable panels so the constant CD = 1.67 renders at one physical length.
                          Do NOT resolve the page budget by shrinking this figure further (section
                          10.14 forbids it and W14 depends on the opposite).
owner_role              : VIZ · dependencies: none · priority: P1 · status: open
verification_method     : post_revision_verification.csv row 8; assert identical x-limits.

work_item_id            : W11
source_ticket_ids       : SE-006
required_action         : Re-typeset supplement Table A19 (landscape, reduced font, column re-flow, or
                          split) so the log reports zero overfull boxes and all seven Notes cells
                          render inside the text block. Extend validate_cross_format_parity to compare
                          CELL TEXT, not merely table presence - the current gate scored this content
                          loss as 0 FAIL.
owner_role              : PROD-PDF · dependencies: none · priority: P1 · status: open
verification_method     : post_revision_verification.csv row 9.

work_item_id            : W12
source_ticket_ids       : SE-026, SE-039, SE-045
required_action         : Fix T06 number formatting to match T14; repair the Table 4 row pointer;
                          resolve the Eq. (5) duplication between Tables 4 and 5; correct Figure 2's
                          "improving trials" to match Eq. (9) (ties accepted); widen Algorithm 1's
                          hanging indent so no continuation enters the number gutter; add S6.6 and S6.7
                          to \supplementary{}; fix the A14 float placement; add non-colour encoding to
                          Figure 3; cite the source in Figure 1's caption; annotate the zero-height bars
                          in B27; unify number formats; de-crowd the CEC2011 F3 panel; scope the
                          taxonomy caption's "every fifth generation" to D=50-99.
owner_role              : VIZ + T5-WRITE · dependencies: none · priority: P2 · status: open
verification_method     : Re-render and re-measure Algorithm 1 x-positions; grayscale render of
                          Figure 3; re-read Figure 2 against Eq. (9); assert every S/A/B identifier
                          cited in the main text appears in the supplementary listing.
```

### W13 — Structure · W14 — Budget

```text
work_item_id            : W13
source_ticket_ids       : SE-028 (structural half), SE-039
required_action         : Restructure the conclusions limitations to match S5.4; correct the "moved
                          rather than rewritten" claim; complete the supplementary listing.
owner_role              : R-sections · dependencies: W08 · priority: P2 · status: open

work_item_id            : W14
source_ticket_ids       : SE-018
required_action         : Re-measure B1 and B2 on the FINAL build (after all text edits, which move
                          both numbers), record a page-count row in phase_gate_register.csv, and either
                          raise the self-imposed cap with a recorded change request and a one-line
                          justification, or migrate non-essential main-text material to the supplement.
                          Resolve overflow ONLY by migration - never by shrinking figures (section
                          10.14; W09 and W10 require the opposite).
owner_role              : T7-VENUE · dependencies: W02, W06, W07, W08, W12, W15 · priority: P2
status                  : open
verification_method     : post_revision_verification.csv row 17.
```

### W15 — Language revision (after the claim chain)

```text
work_item_id            : W15
source_ticket_ids       : SE-036, SE-029
root_cause              : R-13 (sentence de-packing) was closed after touching two paragraphs.
required_action         : Complete the de-packing across the 98 sentences over 55 words; delete the ~16
                          transparency meta-clauses while keeping every disclosure intact; consolidate
                          the rank-biserial definition; fix the 16-caption boilerplate; settle on ONE
                          name for the C1 mechanism and use the title's term in the body; normalise the
                          four British strays; trim the abstract to <= 200 words; add the three abstract
                          qualifiers and remove "To our knowledge" from the cover letter.
scientific_or_editorial : editorial
owner_role              : RW
dependencies            : W06, W07, W08 - STRICTLY AFTER. Style editing over an undecided claim is how
                          numbers drift.
verification_method     : post_revision_verification.csv row 21 - diff every numeric token before and
                          after; zero changes permitted. Re-run the sentence-length and semicolon
                          census.
completion_criterion    : One name for C1; one definition per statistic; no fact, number, citation or
                          scope changed.
priority                : P2 · status: open
```

### W16–W19 — Production, citations, class, governance

```text
work_item_id            : W16   (SE-031, SE-032)
required_action         : Set w:pgMar in word/reference.docx to the mdpi.cls geometry (2.7/2.7/1.8/1.5
                          cm) and rebuild both DOCX; unify the back-matter declaration styling; make
                          the parity validator's TOC row CONDITIONAL and make display-equation parity
                          compare content rather than the equation number alone; regenerate
                          word_validation_report.md against the shipped DOCX with a T1-T5 typographic
                          specification.
owner_role              : PROD-WORD · dependencies: W20 rebuild ordering · priority: P2 · status: open
note                    : The two validator defects matter more than the margins. An unconditional PASS
                          row is the same "gate that cannot fail" class that R-07 was raised to remove;
                          it survived in a sibling validator.

work_item_id            : W17   (SE-023, SE-024, SE-025, SE-034)
required_action         : Add Alfredo G. Hernandez-Diaz to liang2013cec2013; correct the GSK-RL
                          characterisation to the source's own tallies and fix the tab:family-review
                          cross-reference; state the novelty boundary at ONE scope in all three places;
                          backfill the awad2016problem role-map row and remove the audit_manuscript.py
                          carve-out; banner literature_audit_report.md as superseded by CR-0005;
                          resync reference_inventory.csv from the source PDFs; fix the reference-27 DOI;
                          rewrite the two dangling note fields; add a validator that reads the three
                          citation-control files.
owner_role              : RI (literature) · dependencies: none · priority: P2 · status: open

work_item_id            : W18   (SE-048)
required_action         : Restore submit-mode line numbering for the review copy; update the D-0010
                          venue metrics; document the local mdpi.cls modifications.
owner_role              : T7-VENUE · dependencies: none · priority: P3 · status: open

work_item_id            : W19   (SE-022, SE-033, SE-035, SE-037, SE-038, SE-040, SE-041, SE-049, SE-050)
required_action         : Re-point project_configuration.md to rel-2026-07-20-67d9345f9 and the correct
                          venue; add the missing artifact_binding rows and remove the seven dead
                          labels; retire or regenerate table_figure_source_map.csv; re-anchor or mark
                          historical requirements_traceability_matrix.csv; reword the Data Availability
                          sentence so it asserts no currently-nonexistent repository; close the AG
                          register rows; add a source-attribution header to fdb_agsk.py; sync
                          cover_letter.md; update the two supplementary.tex comments; correct
                          docx_note, the parity count and the pending-refreeze status; re-run the
                          environment attestation from a clean tree; update the five stale claims-matrix
                          rows; record the similarity-screening decision; update PAPER_REVIEW_PROMPT
                          sections 1.5, 1.5.0-C(2c), 10.7 and 10.9 and re-point the section 10.1
                          bindings.
owner_role              : ECB · dependencies: W07 (claims-matrix row) · priority: P2-P3 · status: open
```

### W01 — Freeze re-mint and reproducibility route (EXECUTE LAST)

```text
work_item_id            : W01
source_ticket_ids       : SE-003, SE-004
root_cause              : (a) The 2026-07-22 amendment re-hashed three rows without re-stamping
                          anchor_commit and without a follow-up stamping commit. (b) core.autocrlf=true
                          with no .gitattributes makes the byte identity of five text artifacts
                          machine-local. (c) reproducibility_manifest.json and runbook.md were written
                          at Phase 12 and never re-pointed through two release re-mints.
required_action         : Add a .gitattributes pinning the text artifacts (or hash line-ending-
                          normalised content and state the normalisation in the manifest); re-point
                          reproducibility_manifest.json to rel-2026-07-20-67d9345f9 with the shipped
                          artifact hashes and a current double-rebuild record; rewrite runbook.md so
                          the stated sequence actually produces the shipped PDF and DOCX from the
                          release - it must include phase6_run_analysis.py (the sole producer of the
                          analysis bundle), build_docx.py, check_manifest and every validate_* gate,
                          must not route statistics through staging gsk_family.cli.stats, must state
                          --runs 51, and must not list the two generators whose input root
                          results/dt-gsk/ does not exist; re-stamp anchor_commit to the commit that
                          actually holds the pinned bytes and land a stamping commit.
scientific_or_editorial : scientific (traceability and reproducibility contract)
owner_role              : REP + ECB
dependencies            : ALL OTHER WORK ITEMS. Re-stamping before the text edits land invalidates the
                          freeze immediately.
required_inputs         : the final post-revision tree
artifacts_to_change     : .gitattributes, papers/governance/main_manuscript_freeze_manifest.json,
                          submission_package_manifest.json, reproducibility_manifest.json, runbook.md
artifacts_to_regenerate : the freeze envelope
verification_method     : post_revision_verification.csv rows 1 and 2 - extract
                          `git archive <new-anchor>` into an empty directory and run check_manifest.py
                          there; execute the corrected runbook end to end and diff the produced PDF
                          against papers/DT-GSK.pdf.
completion_criterion    : check_manifest reports 15/15 OUTSIDE the author's working tree, and the
                          runbook reproduces the shipped artifacts from the release.
priority                : P1
status                  : open
```

### W20 — Final rebuild and validation (Gate Q)

```text
work_item_id            : W20
source_ticket_ids       : all
required_action         : Deterministic double build of DT-GSK.pdf, supplementary.pdf,
                          cover_letter.pdf, DT-GSK.docx and supplementary.docx under
                          SOURCE_DATE_EPOCH; then run the full gate suite including the three NEW
                          assertions introduced by this revision (quoted-statistic-to-released-column,
                          figure off-canvas, cross-format cell text).
owner_role              : ECB
dependencies            : W01 (which itself depends on everything else)
verification_method     : post_revision_verification.csv row 22 plus the full regression sweep at
                          row 20 - re-run the section 10.9 leak test, re-read abstract, conclusions and
                          cover letter for new unsupported claims, and confirm no number changed during
                          the language pass (row 21).
completion_criterion    : All gates green; all 17 Major and 19 Moderate tickets closed with evidence;
                          zero regressions. Gate Q PASS.
priority                : P1
status                  : open
```

---

## Response-to-reviewers seed (Appendix A.9)

Prepared for every ticket in `post_revision_verification.csv`. The response posture, decided at consensus:

| Position | Tickets | Wording stance |
|---|---|---|
| `agree` | SE-001, SE-002, SE-005, SE-006, SE-007, SE-008 (disclosure half), SE-010, SE-012, SE-013, SE-015, SE-017, SE-023, SE-024, SE-034 and most Moderates | Concede plainly, state the exact change, cite the verification. Do not explain why the defect arose. |
| `partly_agree` | SE-009, SE-011, SE-016, SE-019, SE-021, SE-047 | Concede the wording defect; state precisely what the evidence does and does not support; where a seat's framing over-reached, say so with the counter-evidence. |
| `disagree_with_evidence` | SE-R01, SE-R02, SE-R03, SE-R04, SE-R05 | Only if an external referee raises them. Answer with the governing scope directive or the verified counter-evidence, courteously and once. |

**Three items must be fixed in the manuscript rather than defended in a response letter**, because no defence exists: the A12 column (SE-001), the MaxFES-equality sentence (SE-002), and the unlabelled proposed-method curve (SE-005). Two more should be fixed rather than defended because defending them costs more credibility than fixing them: the omnibus columns (SE-007) and the GenAI declaration (SE-010).

---

## Estimated effort

| Group | Items | Class | Estimate |
|---|---|---|---|
| Claim chain (W06, W07, W08) | 3 | text | 3–4 days, author-involved |
| Protocol disclosure (W02, W03, W04) | 3 | text + attestation | 1–2 days |
| Exhibits (W09–W12) | 4 | regeneration | 2–3 days |
| Statistics governance (W05) | 1 | derived outputs | 1–2 days |
| Structure, budget, language (W13–W15) | 3 | text | 2–3 days |
| Production, citations, governance (W16–W19) | 4 | mechanical | 2–3 days |
| Freeze and rebuild (W01, W20) | 2 | integrity | 1 day |
| **Total** | **20** | **no rerun, no new release, no core change** | **~2–3 weeks** |
