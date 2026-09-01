# Decision Log

Section 3.1 schema: every autonomous decision, rationale, evidence, impact.
Section 12.3 autonomous decision protocol applies to each entry.
Append-only; one `## D-NNNN` block per decision.

## D-0001 — Reconciliation commit as anchor (Phase 0, 2026-07-10)

- **Decision**: Adopt commit `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21`
  (branch `main`) as `anchor_commit` for the entire publication production run.
- **Alternatives considered**: (a) anchor on the previous commit and treat the
  framework revision + generator fixes as dirty working-tree state; (b) create
  a fresh commit mid-preflight.
- **Rationale**: Immediately before Phase 0, the framework revision of
  `papers/PAPER_BUILD_PROMPT.md` together with generator fixes was reconciled
  into a single commit, leaving the tree clean except for live staging outputs
  (see D-0002). Anchoring on this reconciliation commit gives Phase 0 a state
  where the authoritative instructions and the code they govern are identical
  to what Git records — the "clean or explicitly reconciled repository state"
  expected outcome of Phase 0. Option (a) would have left the master framework
  itself unversioned at the anchor; option (b) would have interleaved
  scientific-path commits with governance preflight.
- **Evidence**: `git rev-parse HEAD` and `git rev-list -1 HEAD` both return
  `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21` (independent cross-check,
  2026-07-10); verbatim records in `reproducibility_manifest.json`.
- **Impact**: All Phase 0 artifacts cite this single commit; later phases
  verify against it. No scientific artifact modified by this decision.

## D-0002 — Live staging campaign is non-blocking (Phase 0, 2026-07-10)

- **Decision**: Treat the running DT-GSK scaffold ablation campaign
  (`scripts/run_ablation.py`, writing to `results/_ablation/<cell>/`:
  `baseline` mid-D100, `no_ace`, `no_psr`; log stamps 2026-07-10) as
  NON-BLOCKING for Phase 0. Do not wait for it; do not touch
  `results/_ablation/`; record its churn as the dirty-path list.
- **Alternatives considered**: (a) block Phase 0 until the campaign completes;
  (b) quarantine the staging outputs into a separate worktree.
- **Rationale**: Section 0.3 declares `results/` staging-only — never evidence
  without Section 2.4 promotion. Phase 0 task 1 blocks freezing only for dirty
  paths touching benchmark evidence, source code, configuration, tables,
  figures, or analysis; the scoped `git status --porcelain` shows dirty paths
  exclusively under `results/_ablation/`. Waiting would delay governance work
  that does not depend on staging; quarantine would perturb a running
  scientific campaign for no evidentiary gain.
- **Evidence**: Scoped `git status --porcelain -- .` snapshot (verbatim +
  SHA-256 in `reproducibility_manifest.json`; itemized in
  `project_configuration.md` Section 2).
- **Impact**: Dirty list is time-varying during preflight; recorded as risk
  R-0001. Any later use of ablation outputs requires Section 2.4 controlled
  promotion (Phase 12 is the sole ablation phase). Phase 0 gate is not held
  open for the campaign.

## D-0003 — No installation during toolchain discovery (Phase 0, 2026-07-10)

- **Decision**: Record `7z` (not on PATH) and `pypandoc` (not importable) as
  missing without installing either; register risks R-0002 and R-0003 naming
  the phases that need them (Phase 12 packaging; Phase 9 Word production).
- **Alternatives considered**: install the missing tools now.
- **Rationale**: Phase 0 task 5 requires recording versions "without installing
  unapproved software that could modify evidence". Both gaps have in-place
  mitigations already verified working: GNU tar 1.35 + certutil/Get-FileHash
  for archiving/checksums, and the pandoc 3.9.0.2 CLI + python-docx 1.2.0 for
  Word production, so no phase is hard-blocked today.
- **Evidence**: Verbatim `--version`/import-check outputs in
  `reproducibility_manifest.json` (environment.toolchain) and
  `project_configuration.md` Section 8.
- **Impact**: Phase 9/12 may raise a formal, documented install request if the
  mitigations prove insufficient; until then the toolchain is frozen as found.

## D-0004 — Engineering-preflight pip deviation formalized (Phase 0, 2026-07-10)

- **Decision**: Formally log (in this register, closing the reserved slot) the
  Task Group D deviation already documented in `engineering_preflight.md`:
  `python -m pip show gsk-family` was run INSTEAD of
  `python -m pip install -e ".[dev]"` for preflight command 1.
- **Alternatives considered**: run the installer as written.
- **Rationale**: Running an installer mid-campaign could mutate the interpreter
  environment used by the live ablation processes (dependency re-resolution,
  entry-point rewrite). Phase 0 task 6 permits this under its own
  revert-or-document clause; `pip show` verified the editable install already
  points at the project root — the exact state `pip install -e` would produce.
- **Evidence**: `engineering_preflight.md` (command 1: exit 0, output SHA-256
  `6a997a5430fa20e0c0365af449b794d0e4bc0a6516eb26cb291fb3abf2d60fe6`).
- **Impact**: No environment mutation during preflight; no lock file changed.
  Phase 2+ may re-run the full install form once no campaign is live.

## D-0005 — Condensed traceability schemas + part merge (Phase 0 gate assembly, 2026-07-10)

- **Decision**: Accept the condensed column sets used by the traceability
  parts and merge them as-is into the canonical files:
  `source_line_traceability.csv` = `line_no,classification,requirement_id,note`
  (5,880 rows; parts 0–5); `requirements_traceability_matrix.csv` =
  `requirement_id,line_no,summary,phase,artifact,validation,owner`
  (2,105 rows; parts 0–5). Single header each; `parts/` retained as
  construction evidence.
- **Alternatives considered**: (a) rewrite both files into the full Section 3.2
  column lists; (b) reject the parts and re-classify.
- **Rationale**: Every Section 3.2 informational requirement is preserved:
  `source_document` is a file-wide constant recorded in
  `project_configuration.md` Section 3 (`papers/PAPER_BUILD_PROMPT.md`);
  `line_text` is recoverable byte-exactly from the master at the anchor commit
  (`262fc16c91fbe5608a1a0b0c5df3cbcd009edc21`), avoiding a 5,880-row
  duplication of the master's text; classification values are exactly the
  Section 3.2 allowed set; per-line requirement linkage and per-requirement
  phase/artifact/validation/owner destinations are present. Validation confirms
  the Section 3.2 substance: every nonblank line classified exactly once, no
  `unmapped`/`partial`/`unknown` anywhere, no dangling or orphan
  requirement references. Option (a) would add bulk without information;
  option (b) would discard verified-complete work.
- **Evidence**: Gate 0 merge-validation run (2026-07-10): 5,880 rows ==
  5,880 nonblank master lines; 0 duplicate `line_no`; 0 missing; 0 extra;
  0 invalid classifications; 2,105 unique requirement IDs; 0 unmapped
  requirement rows; 0 dangling refs; 0 orphan requirements. Recorded in
  `PHASE_0_readiness.md`.
- **Impact**: Later phases resolving `line_text` MUST read the master at the
  anchor commit. Any consumer needing the literal Section 3.2 wide schema can
  derive it mechanically from these files plus the master; no information loss.

## D-0005b (2026-07-10) — Post-Gate-0 master-framework change requests CR-0001, CR-0002

> Id note: this decision and the traceability-schema decision above both went in
> as D-0005 during Phase 0. It is relabelled D-0005b at pass-54 rather than
> renumbered, because D-0006 through D-0059 are cited across the governance
> record and the manuscript bindings.

Two user requirements arrived after Gate 0 froze (Section 0.2 precedence item 1):
(1) seven-curve family-overlay convergence panels per function (CR-0001); (2)
presentation calibration against the GSK and ATMALS-GSK exemplars plus corpus
Q1/Q2 best practices (CR-0002). Both applied to the master framework via change
control; the Gate 0 source-line/requirements traceability is patched by a
targeted re-classification of the edited ranges (rerun of the affected Gate 0
validation), recorded in this run. Master grew 7472 -> 7585 lines.

## D-0006 (2026-07-10) — CR-0003 scope decision: amend, not rebuild

The 30-chapter user specification is satisfied by targeted amendment of the
existing evidence-locked framework (12 delta groups) rather than a rewrite:
a rebuild would orphan the frozen Gate-0 traceability (5,880 lines / 2,105
requirements) and the in-flight Phase 1 audit. The user-proposed
paper_outputs/ derived-tree is satisfied by the already-frozen equivalent
layout (papers/governance/, papers/analysis/<release_id>/, results/ staging,
papers/tables|figures) — equivalence to be recorded in Section 1.2 by CR-0003
rather than relocating frozen roots mid-run.

## D-0007 (2026-07-10) — CR-0004: bibliography metadata corrections from the Phase 1 identity audit

- **Decision**: Apply, via maintenance change request CR-0004, every
  bib-metadata correction recorded (from printed sources) in the `notes`
  column of the frozen Phase 1 `reference_inventory.csv` to
  `papers/references.bib`, propagate the byte-identical copy to
  `reference_papers/references.bib`, and surgically regenerate only the
  affected rows of `reference_papers/README.md` and
  `reference_papers/PAPERS_LIST.md`. Citation KEYS are unchanged without
  exception (including `mohamed2021novel`, whose year corrects to 2019, and
  `fialho2010adaptive`, whose author order corrects to Da Costa first).
- **Scope** (15 entries): wrong DOIs in `mohamed2021novel` (also year
  2021→2019 and third author → Jambi, Kamal M.), `apgsk_imode2024`
  (→ ctae231), `nabahat2024hybrid` (→ s42979-024-02674-y), `arini2022gjojos`
  (→ ACCESS.2022.3227510), `hu2022qcsca` (→ jcde/qwac119),
  `kolda2003directsearch` (→ 10.1137/S0036144502428893, truncated final
  digit); author-name corrections in `apgsk_imode2024`, `nabahat2024hybrid`,
  `arini2022gjojos`, `hu2022qcsca`, `jalali2021opposition`,
  `zhong2021gskhho`, `navaneetha2022gskde`, `liang2024gskwoa`,
  `zhou2021iade`, `kaveh2021pgo`; `awad2017ensemble` title corrected to
  '...with Euclidean Neighborhood for Solving CEC2017 Benchmark Problems'
  (the LSHADE-cnEpSin paper); `jawad2024egsk` converted from @misc
  preprint placeholder to the published @article (Results in Control and
  Optimization 19 (2025) 100542, DOI 10.1016/j.rico.2025.100542; printed
  title 'Enhanced Gaining-Sharing Knowledge-based algorithm', without
  'for Global Optimization'; key retained per its own in-bib note);
  `fialho2010adaptive` retyped @article→@inproceedings (GECCO proceedings
  name moves journal→booktitle) with source author order Da Costa, Fialho,
  Schoenauer, Sebag.
- **Alternatives considered**: (a) defer corrections to the manuscript
  bibliography phase — rejected: every downstream artifact (citation maps,
  README/PAPERS_LIST, Word bibliography) inherits the errors; (b) also
  rewrite the frozen `reference_inventory.csv` bib_* columns — rejected:
  Phase 1 artifacts are frozen; the inventory's notes column deliberately
  records the corrections against the audited (pre-correction) bib state.
- **Evidence**: `reference_inventory.csv` notes column (identity_status
  `minor_metadata_mismatch` rows, each verified against the local printed
  source); Phase 1 evidence cards; CR-0004 row in
  `change_request_register.csv`.
- **Impact**: Citation keys, `papers/sections/*.tex` \cite commands, and the
  allowed-citation-key list are unchanged; the cites-subset-of-bibkeys
  invariant re-verified after the edit. The two .bib copies re-verified
  byte-identical. Follow-up flagged for the writing phases: prose that
  labels eGSK by year ('eGSK 2024') must reconcile with the published year
  2025; `awad2016problem` remains BLOCKED (wrong local document) and is
  untouched by this CR.

## D-0008 (2026-07-10) — Phase 2 tasks 9 + 11–13: ledger/matrix built; schema extension; apgsk defect recorded

- **Decision**: (1) Build `data_ledger.csv` (174 rows: one per algorithm ×
  suite × dimension, + CEC2011 native-dim and rollup rows, + context-suite
  rows) and `experiment_matrix.csv` (70,813 rows: one per run from each cell's
  `per_run.csv`), with cell-level SHA-256 checksums, per-cell
  `environment.json` `git_commit`, and the placeholder
  `PENDING-RELEASE-ID(phase2-evidence_release_manifest)` until the Section 6.6
  manifest assigns the release ID. (2) Extend the Section 3.8 data-ledger
  schema with one trailing column `function_set_hash` (SHA-256/16 of the
  sorted function-ID list), per the executing brief's "+function-set hash"
  requirement; canonical column order is otherwise preserved. (3) Record the
  `cec2017/apgsk` metadata-overwrite defect as three DEFECT ledger rows
  (`blocked-pending-recovery-or-new-release`) instead of touching evidence.
- **Alternatives considered**: (a) encode the hash inside `function_set` —
  rejected (destroys readability and exact-schema greps); (b) reconstruct
  apgsk D10/30/50 per-run data from git history now — rejected (recovery must
  go through a new immutable release per Section 2.4, owned by the Phase 2
  gate, not a ledger task); (c) omit context suites — rejected (Section 4.3
  requires separate context-scope verification).
- **Evidence**: seed formula `(20240620 + 1000003·dim + 1000033·func +
  1000037·run) mod 2147483646 + 1` verified on all 70,813 rows (0 mismatches);
  key uniqueness verified (0 duplicates); coverage complete for all cells
  except `cec2017/apgsk` D10/30/50 (summary/curves/checkpoints present,
  per_run/seed/env cover D100 only, env timestamp 2026-07-08, commit
  `20cfed0acb…`); 1,507 rows terminate `target_error_reached` (agsk cec2017
  D10/D30; agsk+apgsk cec2013 all dims) — flagged to task 7 as an
  algorithm-specific budget-accounting difference.
- **Impact**: `papers/governance/data_ledger.csv`, `experiment_matrix.csv`,
  `asset_map.md`, `table_figure_source_map.csv`, `staging_inventory.md`
  created; `instruction_precedence.md` gains row C-11 (runbook
  `results/paper_tables/` "from the stats pass" claim STALE; sole sanctioned
  producer = Phase 6 task 23 export). T17–T20 recorded as an intentional gap.
  No evidence, manuscript, table, figure, or staging file modified.


## D-0009 (2026-07-10) — CR-0005: awad2016problem unblocked (correct CEC2017 definitions report supplied)

- **Decision**: Accept the user-supplied replacement
  `reference_papers/awad2016problem.pdf` (34 pp., sha256 `b69f52f0…`) as the
  correct Awad/Ali/Liang/Qu/Suganthan NTU 2016 bound-constrained CEC2017
  problem-definitions report; flip the key from BLOCKED to admissible via
  change request CR-0005 (Phase 1 reopened under change control only for this
  row); close evidence gap EG-001.
- **Evidence**: full-text content certification this session (title without
  "Constrained"; F1–F30; unimodal/multimodal/hybrid/composition; [-100,100];
  MaxFES = 10000·D; no constraint g/h machinery); CR-0005 row;
  `evidence_cards/awad2016problem.md` (full card, supersedes stub);
  `allowed_citation_keys.txt` 56 → 57.
- **Impact**: The CEC2017 suite-definition citation role (Appendix B.4) is now
  fillable; `awad2017ensemble`/`brest2017single` revert to corroborating
  participant descriptions. No remaining blocking literature gap.

## D-0010 (2026-07-10) — Phase 4 journal freeze: MDPI Algorithms; R-0004 cover-letter conflict DEFERRED

- **Decision**: Freeze the repository-wired provisional target — **MDPI
  *Algorithms*** (`papers/Definitions/mdpi.cls`, class option `algorithms`,
  `papers/main.tex` line 5) — as the Phase 4 target journal, per the framework
  Phase 4 task 1 default ("use the repository-wired target") and the explicit
  user instruction of 2026-07-10: "use the current plan's target and flag
  R-0004 for later."
- **R-0004 disposition**: the cover-letter venue mismatch (`cover_letter.md`/
  `.tex`/`.pdf` address Elsevier *Swarm and Evolutionary Computation*) is
  **DEFERRED, not resolved**. It remains an open risk owned by the
  finalization phases: before submission the cover letter MUST be rewritten
  for the frozen venue (or the venue decision revisited by the author via a
  new change request). Phase 9/11 must not render or package the stale
  cover letter as-is.
- **Alternatives considered**: (a) switch target to Swarm and Evolutionary
  Computation to match the cover letter — rejected: the framework default
  binds to the repository-wired template, and the user chose the current
  plan's target; (b) resolve the cover letter now — rejected: user explicitly
  deferred.
- **Impact**: Phase 4 `journal_requirements.md`/`journal_decision.md` record
  the frozen target and current official MDPI instructions (with access date
  and online-verification status); `page_budget.md` binds the Section 1.5
  hard page-limit rule to a self-imposed budget if MDPI states no hard cap;
  risk register R-0004 updated (owner → Phase 9/11, mitigation = deferred
  cover-letter rewrite gate).

## D-0010 addendum (2026-07-10, later same day) — Author ratification of the MDPI Algorithms target

- **Event**: After a live two-index verification of 15 candidate venues (2025 JCR
  + CiteScore/SJR, July 2026), the author explicitly confirmed: "keep Algorithms
  (MDPI) as target journal."
- **Effect**: D-0010 is upgraded from framework-default freeze to **author-ratified
  decision**. Supporting facts recorded at ratification: MDPI Algorithms 2025 JCR
  IF 2.6 (Q2 CS Theory & Methods), CiteScore 2024 4.5 (Q1 Numerical Analysis,
  19/88), ~18-day median first decision, APC 1,600 CHF, and direct family
  precedent — ATMALS-GSK (alfadli2025atmals) published in this exact journal
  (Algorithms 18(7):398, 2025) with a family-scoped comparison panel.
- **R-0004 unchanged**: the cover-letter rewrite for MDPI Algorithms remains
  deferred to Phase 9/11 (owner unchanged). AG-0006 scope unchanged (cover letter
  + APC acceptance + submission account remain author-side items).

- **Institutional-requirement check closed (2026-07-10)**: author confirmed Q1 or
  Q2 suffices for the PhD requirement. MDPI Algorithms (WoS Q2, CS Theory &
  Methods; Scopus CiteScore Q1, Numerical Analysis 19/88) satisfies it. No
  residual venue-standing concern; the only open venue item remains the R-0004
  cover-letter rewrite (Phase 9/11).

- **N-021 disposition (2026-07-21)**: The reviewer flagged the recorded JCR/
  CiteScore figures (IF 2.6; CiteScore 4.5) as temporally stale versus a current
  two-index check (reviewer cited CiteScore 5.4, Q1 Computational Mathematics).
  Resolved via the reviewer's acceptable alternative: journal quartile/index
  figures are kept OUT of all manuscript-facing materials (verified - no quartile/
  JCR/CiteScore claim in the main text, sections, or cover letter) and confined to
  this internal record. The figures above are the 2026-07-10 ratification snapshot
  and are NOT auto-refreshed; before submission the author may capture current
  JCR/Scopus figures (with an access date) from the official databases if an
  in-manuscript claim is later desired. Ticket N-021 closed on this basis; no
  figures fabricated.

## D-0011 (2026-07-11) — CR-0006: apgsk CEC2017 per-run recovery (A2-004 data-loss correction)

- **Decision**: Accept CR-0006. The apgsk CEC2017 D10/D30/D50 per-run data — lost
  from `benchmarks/cec_reference_results/cec2017/apgsk/per_run.csv` and recorded as
  anomaly **A2-004** (per_run covered D100 only; run-level quantities vs apgsk at
  the three lower dimensions were disposed *disclosed-unavailable*, never imputed) —
  is **restored** to all four dimensions (1479 → 5916 rows) by a **validated
  deterministic recovery** (`scripts/recover_apgsk_perrun.py`). The recovered
  D10/D30/D50 rows **reproduce the frozen summary CSVs EXACTLY**, which is the
  admissibility proof: this is a **completeness correction of lost data**, not new
  experimental data. No benchmark was re-run; the frozen algorithm and every other
  optimizer's data are immutable.
- **Confirmatory-amendment / outcome-blindness basis (SAP Section 13)**: the SAP
  pre-registered exactly this contingency — `source_resolution_map.csv` disposition
  (iv) and SAP Section 6b anticipate a *registered change request* sanctioning a
  recovered apgsk per-run source as a **logged confirmatory amendment**, not a
  silent change. CR-0006 is that logged amendment. The recovery is validated
  against frozen summaries (not against any inspected outcome), so it preserves the
  confirmatory character of the affected families.
- **Bounded blast radius (verified Stage 1 + Stage 2)**: reopens **Phase 6**
  (run-level analysis recompute), **Phase 7** (exhibit regeneration), and **Phase 11**
  (freeze/parity re-verification) **for apgsk run-level cells only**.
  - Phase 6: 31 bundle files under `papers/analysis/rel-2026-07-10-262fc16c9/`
    changed (apgsk run-level `wilcoxon_run`/`effect_sizes`/`bca_ci`/`headline_bca`,
    `cost`, `exploratory_bh`, robustness r02/r05/r06, `primary_stats`, and
    provenance re-stamps). **0 non-apgsk data cells changed**; all
    `friedman_ranks_*`, `descriptive_stats_*`, function-level `wilcoxon_holm_*`,
    `cross_check.json`, robustness r01/r03/**r04**/r07/r08, and all CEC2013/CEC2011
    run-level files are **byte-identical**.
  - Phase 7: re-ran `generate_latex_tables.py` + `generate_t16_bca.py` — **all 21
    `papers/tables/*.tex` byte-identical** (they read `results/paper_tables/T*.csv`
    and `descriptive_stats_*`, all byte-identical). `results/paper_tables/T*.csv`
    and `artifact_binding.csv` are unchanged (no built exhibit or bound source
    references a changed run-level file). The main-text effect-size table (T15,
    `tab:effect-sizes`) is summary-means-based and **unaffected**; the main
    manuscript was **not** touched.
  - Phase 9 (Word/docx) is **NOT reopened** by this CR; `word_sources/T16_bca.json`
    (which reads the recovered `headline_bca.csv`) and a Word/PDF rebuild are a
    separate downstream stage, recorded as a hand-off.
- **No claim upgraded**: filling a disclosed-unavailable cell with its true measured
  value is a completeness correction. `claims_evidence_matrix.csv` RS-07/RS-08/RS-09/
  LM-04 carry a dated CR-0006 *evidence note* only; permitted/blocked wording and
  `ACCEPTED_PHASE_6`/`READY` status are unchanged; no disclosure wording was
  inflated.
- **Governance updates**: `evidence_release_manifest.json` (size/sha + recovery
  note, Stage 1); `phase2_anomaly_register.csv` A2-004 → **RESOLVED-CR-0006**
  (siblings A2-005/A2-006/A2-007 on seed_schedule/env/gen-log provenance remain
  open — out of scope); `phase_05/{analysis_registry.csv, statistical_analysis_plan.md,
  source_resolution_map.csv}` dispositions annotated RESOLVED (original
  pre-registration text preserved); `change_request_register.csv` CR-0006 APPROVED
  (P1). `evidence_gap_register.md` does not carry the apgsk per-run gap and is
  untouched.
- **Approver**: P1. **Status**: APPROVED.

## D-0012 (2026-07-13) — Submission Phase A0: format + DOCX-field decisions; title recommendation

Governs the consolidated `SUBMISSION_IMPLEMENTATION_PLAN.md` (Phase A0). The
author's directive "decide the best recommended actions then start phase 0"
authorises the two production decisions below; author-side *facts* (ORCID, DOI,
e-mail, CRediT split, GenAI version, licenses, funding, COI) are NOT decided
here and remain open in `administrative_gap_register.md` (AG-0001..0007).

- **Decision A0-1 — Submission artifact = LaTeX; DOCX is a companion.**
  MDPI *Algorithms* is submitted and typeset from LaTeX source (`mdpi.cls`,
  class option `algorithms`; D-0010). The deterministic build + freeze
  governance is LaTeX-native and the PDF is the source of truth. Pixel-exact
  DOCX is provably unattainable through the pandoc pipeline (fidelity audit
  Section 1), so DOCX production furniture (Part B Tiers D2/D3) would yield a
  companion that can never be authoritative. **Consequence:** Part B stops at
  the completed Tier D1; the DOCX remains a clean, self-contained,
  content-faithful companion for co-authors/reviewers. D2/D3 are OPTIONAL and
  DEFERRED (only revisited if the author is required to submit in Word).
- **Decision A0-2 — DOCX `w:updateFields` = false (self-contained).**
  Fulfils the author's explicit requirement that the DOCX "be open in any place
  and self-contained" with no "update fields?" prompt on open. The pipeline
  bakes deterministic cached field results, so `updateFields=false` renders
  correctly everywhere without user action. This is the current build state, so
  no change is required. Trade-off (fields do not auto-refresh) is immaterial
  for a companion whose sources are frozen.
- **Recommendation A0-3 — Title (author prerogative; NOT auto-applied).**
  Keep "An Interaction-Structure Memory for High-Dimensional Gaining-Sharing
  Knowledge Optimization" and preempt reviewer item Q1-004 with a one-sentence
  operating-regime clarification in the Introduction (dimensions up to 100; ISM
  active at the D>=50 tier) rather than retitling. Rationale: D100 is defensibly
  "high-dimensional" in this sub-literature; the established DT-GSK identity,
  PDF metadata, and cover letter all reference the current title; a clarifying
  sentence is cheaper and lower-risk than a retitle. Alternative on offer:
  retitle to drop "High-Dimensional" (e.g. "... for Dimension-Scalable
  Gaining-Sharing Knowledge Optimization"). This recommendation is recorded for
  author confirmation; the edit itself (either path) is a Phase A1.T5 task.

- **Author-facts still open (gate A1.T5 metadata-insertion + Part C packaging
  only; they do NOT gate A1 no-compute science or the A2 experiment):**
  AG-0001 (H.S.M.R. CRediT split), AG-0002 (ORCIDs), AG-0003 (funding),
  AG-0004 (COI wording), AG-0005 (H.S.M.R. e-mail), AG-0006 (cover-letter venue
  rewrite / APC / account; R-0004), AG-0007 (GenAI version/date); plus the
  Zenodo DOI/URL and code/data licenses.
- **Acceptance-gate evidence**: `papers/scripts/check_manifest.py` -> `12/12
  match []` (2026-07-13); `papers/scripts/check_manifest.py` committed
  (d77e49b4a). Unblocked by this decision: Phase A1 (no-compute hardening) and
  Phase A2 (ISM isolation) may both start. Note: an uncommitted, pre-existing
  build artifact `word/field_registry.csv` (section-number formatting from
  earlier Tier-D1 DOCX work; NOT one of the 12 frozen files) will be reconciled
  at the next DOCX rebuild (A1.T6); it does not affect any tracked hash.
- **Approver**: P1. **Status**: A0-1/A0-2 DECIDED; A0-3 RECOMMENDED (author
  confirm); author-facts OPEN.

## D-0013 (2026-07-13) — Submission Phase A1: supplement operator-spec + post-hoc robustness

Governs SUBMISSION_IMPLEMENTATION_PLAN.md Phase A1. Author-approved scope this
session: full operator specification (review-gated) + results-gated post-hoc
statistics. Three read-only mappers first established that the manuscript was
already near-fully specified (NLPSR, BSE/deep-stall, dimension-tier cadence,
D>=50 gate, both RNG seed maps, Reproducibility Appendix S5, BCa CIs, and the
r01--r08 robustness battery all present), so A1 was scoped to close only the
genuine residual, not to regenerate existing content.

- **A1.T1 -- Complete Operator Specification (supplement Section S5.3)**: added
  code-accurate detail for the items the frozen equation registry
  (E6/E9/E10/E11/E12) summarizes but did not fully pin -- the five ACE arms
  (K_F,K_R,K_exp) + initial probabilities; the two-accumulator interaction-graph
  update with per-displacement L1 normalization and improvement weighting; the
  graph->block extraction procedure + confidence/readiness gate; the eigenframe
  compass-search constants (with the correction that DT-GSK's endgame is
  SciPy-free -- SLSQP belongs to eGSK); and the Cauchy-escape scale + RNG
  substream modulus. Every value transcribed from the hash-frozen sources and
  BIND-annotated to code:line; high-visibility values (ACE arms, polish
  fractions, Cauchy scale) directly re-verified against source, which corrected
  a mapper imprecision (Cauchy scale is 0.04 at the active tiers D>=20, disabled
  for D<20, applied as 0.04*D^-0.5*span*Cauchy). The frozen equation registry
  itself was NOT edited; the new subsection references E6/E9/E10/E11/E12.

- **A1.T2 -- Post-hoc robustness (supplement Section S2, sec:supp:posthoc)**:
  results-gated. Two sensitivity checks computed read-only from the frozen
  per-run/descriptive artifacts by the new deterministic script
  papers/scripts/posthoc_robustness_cec2017.py (outputs
  papers/analysis/posthoc_robustness/*.csv): (i) endpoint invariance -- DT-GSK's
  Friedman place is unchanged under raw/median/log10 endpoints (first at
  D=10/50/100, second at D=30 behind eGSK); (ii) exact inference -- an exact
  sign-flip permutation of the signed-rank statistic (2e5 perms, seed 20240620)
  preserves all 24 Holm alpha=0.05 pairwise decisions (0/24 changes). The script
  reproduces the frozen primary Friedman ranks (max |delta| ~ 4e-7) as a
  validation gate. Both checks are labeled post-hoc / non-pre-registered; no
  primary number, rank, or headline was changed.

- **Reproducibility / scope**: supplementary.pdf (986,380 B) and
  supplementary.docx rebuilt deterministically and bit-identical across two
  builds (SOURCE_DATE_EPOCH 1783468800 PDF / 1783641600 DOCX); supplement DOCX
  validator markers_left=0, TOC=0, 0 replacement chars, new content present. The
  12-file main-manuscript freeze manifest is UNAFFECTED (no tracked main file
  changed; check_manifest.py -> 12/12); per established practice supplement
  changes are outside the 12-file manifest scope, and the stale
  pre_ablation_supplement_freeze_manifest.json (Phase-11 snapshot, unmaintained
  since S6) was left unchanged.

- **Deferred / open**: A1.T5 author-fact metadata (DOI/CRediT/GenAI) remains
  blocked on author input (AG-0001..0007); the optional IQR column and proper
  connected-clique CD diagrams are deferred; per-component FES ledgers are out
  of no-compute scope (gap EG-005).

- **Approver**: P1. **Status**: A1 core additions COMPLETE (supplement-only,
  reproducible x2); author-fact items OPEN.

## D-0014 (2026-07-13) — Submission Phase A3: ISM-overlay isolation completed and reported

The direct ISM isolation reviewers requested (pre-registered X-ABL-02) is now
run on the PRIMARY suite and reported. Author ran the 4-cell overlay campaign
(full / no_sgsm / no_adaptive / no_finalpolish), CEC2017 D50+D100, 25 paired
runs, promoted under benchmarks/cec_reference_results/_ablation/overlay. Promotion
verified: 1450 rows/cell (29 funcs x 2 dims x 25 runs), 0 NaN, identical seed
schedule across cells (paired/common-random-numbers), config toggles exact, and
the runner self-verification verdict CONSISTENT (0 hard failures).

- **Result (honest, results-gated).** Across CEC2017 D50/D100 and CEC2013 D50:
  the interaction-structure memory shows **no significant standalone benefit** at
  its active tiers (paired Wilcoxon, Holm p = 0.80 / 0.93 / 0.24; Delta-rank ~
  +0.09; Vargha-Delaney A12 ~ 0.50), while adding a **+54% (D50) / +37% (D100)**
  wall-time overhead; the **eigenframe final polish is a significant contributor**
  (Holm p = 0.010 / 0.006 / 0.002; A12 0.59 / 0.54 / 0.64); the adaptive gate is
  directional but not significant. Friedman omnibus significant on all three.
- **Reporting.** Supplement Section S6.5 (Table A17) converts the prior 'deferred
  to future work' note into the completed result. Per author decision (this
  session), the MAIN TEXT now states the null: performance.tex, proposed_algorithm.tex
  and conclusions.tex updated from 'reserved for a follow-up supplement' to the
  completed isolation with its no-standalone-benefit finding.
- **No claim upgraded.** No primary result, rank, or number changed; DT-GSK's
  family-best standing is unchanged and rests on the full dimension-tiered system.
  This CONFIRMS, not upgrades, the paper's prior cautious framing.
- **Provenance.** generate_ablation_matrix.py (rank/Wilcoxon/Holm) +
  ablation_overlay_effects.py (A12/cost) -> papers/analysis/ablation_overlay/*.csv
  (committed), reproducing every Table A17 number. RAW overlay evidence (~114 MB,
  296 files, mostly convergence curves) remains UNTRACKED pending an author
  provenance decision (commit essential per_run/summary vs full tree vs Zenodo /
  promote_evidence.py release id).
- **Integrity.** 4 artifacts rebuilt deterministic x2; DOCX markers_left=0; main
  manifest refrozen 12/12 (a3_ism_isolation_refreeze) + reproducibility_manifest.
- **Approver**: P1. **Status**: A3 COMPLETE; raw-evidence provenance OPEN.

## D-0015 (2026-07-13) — Submission Phase A4: title reframe + consistency fixes

After an independent read-only adversarial consistency review (which confirmed
the A3 work is clean: S6.5 prose == Table A17, no dangling refs, abstract does
not overclaim ISM, no leftover standalone-benefit claims), the author approved
applying all surfaced fixes.

- **Title reframe (author decision).** "An Interaction-Structure Memory for
  High-Dimensional Gaining-Sharing Knowledge Optimization" -> "DT-GSK: A
  Dimension-Tiered Gaining-Sharing Knowledge Optimizer with Interaction-Structure
  Memory". Fixes TWO reviewer-facing flags at once: drops the "High-Dimensional"
  overclaim (Q1-004; D<=100) and positions ISM as the organizing element of a
  dimension-tiered system rather than the performance driver -- consistent with
  the S6.5 isolation null. Applied to main.tex \Title, DOCX core-props title
  (build_docx.py), and the cover letter (.md + .tex).
- **Consistency fixes.** (i) introduction.tex: "is closed by the memory" ->
  "is targeted by the memory ... whose isolated contribution is examined directly
  in the Supplementary Materials" (removes an efficacy overclaim the null
  undercuts; matches the hedged related_work.tex wording). (ii) main.tex
  back-matter supplement summary now names the direct ISM isolation (S6.5)
  alongside the scaffold ablation (it was invisible there). (iii) conclusions.tex
  "Future work is anchored..." opener -> "Component-level evidence anchors the
  mechanisms and frames the open questions" so the completed S6.5 study is not
  misread as future work. (iv) supplement: Table~A17 now cross-referenced from
  the S6.5 prose.
- **QA ledger.** cross_format_consistency.csv regenerated (was stale, predating
  D1/A1/A3 -- it still certified "Campaign in Progress"). Residual FAILs are
  cross-format parity-check limitations on the D1 native/authored tables + the
  accepted main-text ablation-study mention; NOT content errors (DOCX validators
  markers_left=0). The parity-check tooling has drifted from the native-table
  redesign and warrants a separate modernization (follow-up).
- **Judgment calls (review minors NOT applied, with reason).** Abstract emphasis:
  left as-is -- it already gives the eigenframe polish its own sentence and makes
  no factual overclaim. Dead \sgsm macro in the pandoc shims: left -- never
  invoked, renders nothing.
- **Integrity.** All 4 artifacts rebuilt deterministic x2; DOCX markers_left=0;
  main manifest refrozen 12/12 (a4_title_and_consistency_refreeze). NO primary
  result/rank/number/equation/figure changed.
- **Approver**: P1. **Status**: A4 fixes COMPLETE. Cover-letter venue rewrite
  (R-0004) and A1.T5 author facts remain open; D4 Visio re-test open. *(D4 WITHDRAWN 2026-08-01 - see D-0040; R-0004 and A1.T5 closed earlier.)*

## D-0016 (2026-07-18) — M-026: tie-corrected Friedman adopted after the primary outcome was known

- **Change**: `gsk_family.analysis.statistics.friedman_rank` was changed to use the
  tie-corrected rank variance underlying the Iman-Davenport F, replacing the
  uncorrected form used when the primary results were first computed.
- **Post-outcome disclosure**: this is an analysis change made AFTER the primary
  outcome was known. It is logged here rather than presented as pre-registered.
- **Rationale**: the 1e-8 success floor maps distinct outcomes onto exactly 0, so
  exact ties concentrate in the low-dimensional panels; the uncorrected statistic
  is anti-conservative there. The correction factor C = 0.890 at D=10 (9 of 29
  functions tied) and 0.979 at D=30; C = 1 exactly at D=50 and D=100.
- **Direction is bounded a priori**: because C <= 1 the correction can only
  INCREASE the statistic, and it leaves mean ranks untouched. It therefore cannot
  manufacture a favourable omnibus decision that the uncorrected form would have
  refused.
- **Effect on reported results**: every omnibus decision, rank, and effect
  direction is identical under both forms; both are emitted to the released CSVs
  (`friedman_chi2` / `friedman_chi2_uncorrected`, `iman_davenport_F` /
  `iman_davenport_F_uncorrected`) so a reader can check this directly.
- **Approver**: P1. **Status**: CLOSED-VERIFIED (P4).

## D-0017 (2026-07-18) — M-027: rank-biserial r emitted and promoted to the tabulated effect size

- **Change**: the matched-pairs rank-biserial correlation r = (R+ - R-)/(R+ + R-)
  was added to the released Wilcoxon CSVs and became the effect size tabulated
  beside the across-function test; Vargha-Delaney A12 was demoted to a descriptive
  companion retained in the workbooks.
- **Post-outcome disclosure**: analysis change made after the primary outcome was
  known; logged, not pre-registered.
- **Rationale**: the across-function test is a matched-pairs Wilcoxon, so its
  aligned effect size is the matched-pairs rank-biserial correlation. A12 is an
  UNPAIRED distributional measure and does not align with the test being reported;
  pairing the two was a mismatch of estimand and test.
- **Effect on reported results**: no p-value, decision, or rank changed; this
  changes which effect size is printed next to an unchanged test.
  `claims_evidence_matrix.csv` row RS-08 was aligned to the shipped choice under
  SE-041 (2026-07-22).
- **Approver**: P1. **Status**: CLOSED-VERIFIED (P4).

## D-0018 (2026-07-18) — M-028: Holm family scope stated explicitly in the conclusions

- **Change**: the conclusions were qualified to name the Holm correction family
  the significance statements belong to, rather than asserting significance
  without a family scope.
- **Post-outcome disclosure**: wording change made after the primary outcome was
  known; logged for completeness.
- **Rationale**: Holm adjustment is only interpretable against a declared family.
  The manuscript uses several (six-comparison within-dimension; m24 global across
  dimensions), and an unqualified claim silently invites the reader to assume the
  strongest one.
- **Effect on reported results**: none. No p-value, adjustment, or decision
  changed; only the stated scope of an existing claim.
- **Approver**: P1. **Status**: CLOSED-VERIFIED (P4), triaged PARTIALLY-FIXED at
  entry and completed in P4.

## D-0019 (2026-07-22) — SE-025: awad2016problem role-map row added; citation controls made checkable

- **Change**: `citation_role_map.csv` gained a B.4 row for `awad2016problem` (56
  -> 57 rows); `literature_audit_report.md` gained a supersession banner naming
  CR-0005 / D-0009; a new gate `papers/scripts/validate_citation_controls.py`
  cross-checks the role map, the usage map and the Word tag map.
- **Rationale**: the key was un-blocked by CR-0005 / D-0009 (2026-07-10) but no
  register was re-checked afterwards, so the manuscript's highest-traffic
  suite-definition citation was cited under NO sanctioned role while a superseded
  Phase-1 report still declared it inadmissible. Nothing detected this, because
  the three citation-control files had no cross-check between them.
- **Non-vacuity**: removing the new row reproduces the defect as two failures
  (C1 and C3); restoring it returns the gate to PASS.
- **Approver**: P1. **Status**: CLOSED.

## D-0020 (2026-07-23) - SE-014: selection-exposure count attested at six full-panel candidates

- **Ticket**: SE-014 (Major), also filed as MX-04 - the review register's only
  `essential_before_submission` item. The manuscript disclosed selection exposure
  qualitatively ("several full-panel candidate configurations") without a count,
  so a reader could not judge how much optimistic-selection risk the CEC2017
  headline carries.
- **Author attestation (P1, 2026-07-23)**: **six** full-panel candidate
  configurations were examined during development, **including the configuration
  ultimately promoted**.
- **Definition of the count**: "full panel" means the candidate was run against
  the complete seven-algorithm GSK-family panel on CEC2017, not a smoke test, a
  function or dimension subset, or an isolated component experiment. Excluded:
  preliminary debugging and smoke runs; partial-function or partial-dimension
  pilots; single-component ablations and sensitivity checks; failed or incomplete
  configurations; post-selection validation, correction, and
  evidence-regeneration runs.
- **Provenance status - READ THIS BEFORE CITING THE NUMBER**: the figure is
  **author-attested and NOT independently corroborated by any repository
  artifact**. A search of `papers/governance/` and `docs/development/` returns no
  record of a candidate roster or count. That is consistent with the attestation
  itself: the intermediate candidates predate the immutable evidence release and
  were not retained in it. The number therefore rests on the authors' development
  record, and the manuscript says so explicitly in both places it appears.
- **Applied to**: `papers/supplementary.tex` Section "Configuration Selection and
  Development Protocol" (full statement with the inclusion/exclusion scope) and
  `papers/sections/performance.tex` (one-sentence main-text statement pointing to
  the supplement).
- **Effect on reported results**: NONE. No claim, number, rank, p-value, equation
  or figure changes; this adds a disclosure that was previously absent.
- **Approver**: P1. **Status**: CLOSED.

## D-0021 (2026-07-28) - Final empirical scope, Decision Gate 0, and the CEC2020 pre-registration

- **Decisions recorded**: three author rulings of 2026-07-27/28 that fix the
  paper's final empirical scope, plus the pre-commitment artifacts they require.
- **(1) Scope**: the paper reports the SEVEN GSK-family algorithms on FIVE
  suites - CEC2017 (29 functions, D=10/30/50/100, 51 runs; primary), CEC2011 (22
  problems, native, 25 runs), CEC2013 (28 functions, D=10/30/50, 51 runs),
  CEC2020 (10 functions, D=5/10/15/20, F6/F7 undefined at D=5 -> 38 cells, 30
  runs, MaxFES 50k/1M/3M/10M) and CEC2013LSGO (15 functions, D=1000/905, 25
  runs, 3e6 FES). The eight vendored external optimizers appear in NO panel,
  table, figure, statistic or claim; they stay in-repo as validated tooling with
  their banks documented-but-unpromoted. CEC2013LSGO uses the TRANSFORMED Ackley
  variant only; `ackley_raw` remains permanently unwired. Registered as CR-0019.
- **(2) Decision Gate 0 - CEC2013 is KEPT** (author, 2026-07-28). The five-suite
  branch of `docs/development/FINAL_PUBLICATION_PLAN.md` is in force and every
  task marked [DROP] there is void. Rationale: the evidence is already frozen and
  validated inside `rel-2026-07-20-67d9345f9`, so keeping costs nothing, whereas
  dropping would surrender a suite on which DT-GSK ranks first (2.80 best-of-7),
  weaken the headline from first-on-two to first-on-one, and force a public
  rationale because the cited immutable release permanently ships the CEC2013
  banks.
- **(3) Unified seed policy everywhere** (author, 2026-07-28): every suite runs
  the unified schedule so that runs are paired across optimizers by (dimension,
  function, run) and every run-level test is valid. `configs/agsk_cec2020.yml`
  was the sole exception - it carried `seed_policy: reference` together with a
  `data_root` (`benchmarks/cec_suite`) that does not exist in this repository -
  and `scripts/run_all_cec2020.py` hard-pointed at it, so one accidental
  invocation would have written reference-seeded AGSK rows into the shared output
  tree where they would have looked valid while being unpairable. Both corrected;
  the wrapper now runs `configs/family_cec2020.yml` and forwards CLI arguments.
- **THE PRE-REGISTRATION**: `papers/build_prompt_phases/phase_05/statistical_analysis_plan_addendum_cec2020_lsgo.md`,
  a Section-13 confirmatory amendment to the frozen SAP (the SAP body is
  untouched). **SHA-256
  `4b351008bebf8f41413cca67703fcbad9562dd111befb9e76e81a032429dcea1`**
  (11,584 bytes, 192 lines). The commit that adds this decision-log entry IS the
  pre-registration commit: **`5c9bfae82`** (2026-07-28).
- **Outcome-blindness, verified rather than asserted**: at signing,
  `results/_run_all/*/cec2020` did not exist for any optimizer and no CEC2020
  result bank existed anywhere in the repository. Every CEC2020 hypothesis,
  analysis id, tie rule and outcome sentence in the addendum was therefore
  written without a single datum. The three CEC2020 outcome sentences are
  pre-written in the addendum's Section 9 wording bank - including the one that
  applies if AGSK wins - so the reporting language cannot be tuned to the result.
- **Asymmetry that the addendum makes explicit**: CEC2013LSGO is NOT
  outcome-blind. Its family Friedman ranks and per-function means were inspected
  before registration, and Section 6 of the addendum records exactly what was
  seen. Those quantities are therefore descriptive-after-inspection and may never
  carry a headline; only the run-level paired Wilcoxon + Holm layer, never
  computed before registration, is confirmatory-with-disclosure.
- **Grid verified before signing**: both CEC2020 configs resolve to exactly 38
  protocol cells (8 at D=5; 10 at each of D=10/15/20; F6/F7 at D=5 correctly
  absent), runs 30, seed 20240620, policy unified, generator threefry, overwrite
  false, budgets 50k/1M/3M/10M. The family campaign is 7,980 runs and
  2.948e10 evaluations.
- **Applied to**: the addendum file; the S8 supplement skeleton
  (`papers/build_prompt_phases/phase_05/S8_cec2020_supplement_skeleton.tex`,
  result slots empty, not yet `\input` anywhere); three PENDING_PREREGISTERED
  rows in `claims_evidence_matrix.csv` (RS-12 CEC2020, RS-13 CEC2013LSGO, LM-06
  the large-scale limitation); CR-0019 and CR-0020 in
  `change_request_register.csv`; `_pending_refreeze.json` reopened; review-prompt
  layer 1.5.0-N added, superseding 1.5.0-M's external-baseline mandate and its
  (i) veto on family-internal ranks.
- **Effect on reported results**: NONE yet. No CEC2020 datum exists; no frozen
  bank is touched; `rel-2026-07-20-67d9345f9` is untouched and still authoritative
  for CEC2017, CEC2011 and CEC2013.
- **Known consequence, deliberate**: `main_manuscript_freeze_manifest.json` now
  reports a mismatch on `papers/governance/claims_evidence_matrix.csv`. That is
  expected while `_pending_refreeze.json` is OPEN and is not drift; it clears at
  the pass-24 re-freeze.
- **Approver**: P1 (author decisions 2026-07-27 and 2026-07-28). **Status**: OPEN
  (closes when the registered analyses have been executed and every
  PENDING_PREREGISTERED row is resolved).
- **CLOSED 2026-08-01.** Both stated conditions are met: the registered
  analyses ran and were promoted as `cec2020-rel-2026-07-29-5867abe1e` and
  `lsgo-rel-2026-07-28-ff1a046ef`, and no `PENDING_PREREGISTERED` row
  survives in any register (checked repo-wide). The status line above is
  retained as written; this entry supersedes it.

- **Correction (2026-07-28, later — see D-0025).** Two descriptive phrases above are
  imprecise; the decisions they record are unchanged. (i) "validated tooling"
  over-claims: six of the eight externals' author-code parity records live only in
  the sibling project and are not reproducible here, and DECC-G has no author-code
  oracle at all — the accurate phrasing is runnable tooling whose validation evidence
  is not reproducible in this repository. (ii) "`ackley_raw` remains permanently
  unwired" — the raw kernels ARE implemented and reachable via `ackley_raw_scope`;
  what is unwired is the ACTIVATION (`ackley_raw_active()` returns False and no caller
  outside `benchmarks/` enters the scope), so every committed bank ran the transformed
  chain. The same imprecision was corrected in CR-0019, FINAL_PUBLICATION_PLAN.md and
  review-prompt layer 1.5.0-N on 2026-07-28; this entry was missed in that pass.

## D-0022 (2026-07-28) - LSGO confirmatory layer first computed; SAP Amendment 1; pre-resume runner metadata fixes

- **Context**: the author stopped the CEC2020 campaign at a clean cell boundary
  (gsk/agsk/apgsk complete at 1,140 rows each; fdb-agsk at 1,020 with exactly
  D20 x {F7,F8,F9,F10} outstanding; atmals-gsk/egsk/dt-gsk not started) to
  close every open CEC2013LSGO issue before resuming. An eleven-agent
  verification pass (seven investigators, four adversarial verifiers) audited
  every open item; everything below is its outcome.
- **(1) AN-PW-LSGO-NATIVE and AN-PWRUN-LSGO-NATIVE computed for the first
  time**, exactly as registered in SAP Addendum 1 (signing commit `5c9bfae82`),
  against inputs pinned by SHA-256 in Amendment 1. Suite-level result: NO
  comparator separates from DT-GSK after Holm (smallest adjusted p = 0.2875);
  the registered outcome sentence "tied-first descriptive rank; paired tests do
  not separate DT-GSK from AGSK" is now data-resolved and binding. Run-level
  regularities: DT-GSK Holm-significantly better than all six family members on
  F4 and F8, worse than all six on F7 and F15. Every number was reproduced by a
  second, fully independent implementation (no scipy) before being recorded.
  AN-EFF-LSGO-NATIVE remains registered and not yet computed.
- **(2) SAP Amendment 1** committed as
  `papers/build_prompt_phases/phase_05/statistical_analysis_plan_addendum_cec2020_lsgo_amendment_01.md`
  (SHA-256 `ef56c224c58a855ceff0771bbca133e60bb917795997ce5b8d4ab5d91cddab5b`),
  per Addendum Section 13 (the addendum itself is untouched). It (a) corrects
  Section 6's recorded "omnibus p = 0.0372" to the reproducible chi2 = 15.3143,
  p = 0.0179 - the recorded ranks reproduce exactly and mathematically force
  that p, so the recorded p could not have come from the same computation; an
  exhaustive recipe search (bases x subsets x precisions x statistics x
  historical bank states) found nothing that rounds to 0.0372; (b) scopes the
  outcome-blindness declaration explicitly to CEC2020 results, cross-referencing
  D-0020's CEC2017 selection-exposure attestation; (c) records the first
  computation of (1) with methods and input pins so no later recomputation can
  silently substitute a different procedure.
- **(3) Latent tooling hazard recorded, binding on Phase 3**: the papers-side
  `friedman_rank_test` helper defaults to `excluded=(2,)` (drops F2 - a CEC2017
  convention). Applied blindly to LSGO it yields p = 0.0370 with wrong ranks.
  The phase6b driver must pass the exclusion list explicitly for every suite.
- **(4) Pre-resume runner metadata fixes** (no optimizer/evaluator/seed code
  touched; 584-test suite incl. the 42-pin hex golden matrix green; ruff clean):
  verification verdicts can no longer be vacuous (D-8.1: `NOT_VERIFIED` /
  `NO_REFERENCE` when nothing was comparable) and a zero-new-runs resume can no
  longer rewrite a completed bank's `environment.json` (D-8.5; new regression
  test asserts byte-identity across a full-skip resume). Without the D-8.5 fix,
  the very next resume would have replaced the production commit and nulled
  `statistics_basis` in all three completed CEC2020 banks.
- **(5) D-7 replay initiated**: eight single-run CEC2013LSGO replays at HEAD
  (one per algorithm; two for dt-gsk spanning its F1-F4 / F5-F15 code-version
  split; apgsk included - previously the one member with no full-budget LSGO
  re-verification). Comparison criterion recorded in advance: per_run stores
  best_fitness as %.10e (11 significant digits), so bank agreement is
  representation-exact at that precision plus %.16g agreement of the final
  gen_log checkpoint; hex-exactness against per_run is impossible by format.
  Results are appended to D-7's record when the batch completes.
- **Effect on reported results**: NONE on any frozen suite (frozen-analysis
  byte guard 115/115 green). The LSGO statistical values in (1) are new,
  pre-registered outputs; the CEC2020 banks are untouched.
- **Approver**: P1 (author stop-and-close directive, 2026-07-28). **Status**:
  CLOSED, except the D-7 replay comparison which lands in the deviation record.

## D-0023 (2026-07-28) - CEC2013LSGO promoted to reference results as lsgo-rel-2026-07-28-ff1a046ef

- **What**: the seven family CEC2013LSGO banks were promoted from staging
  (`results/_run_all/<alg>/cec2013lsgo/`) into
  `benchmarks/cec_reference_results/cec2013lsgo/<alg>/` by the new gate-checked
  tool `papers/scripts/promote_suite.py`, minting the separate, non-superseding
  release **`lsgo-rel-2026-07-28-ff1a046ef`** (173 files; manifest
  `papers/governance/evidence_release_manifest_cec2013lsgo.json` with per-file
  SHA-256, file classes, pre-registration bindings and in-manifest exclusions:
  106 curve CSVs, 70 session logs). Authority: REFERENCE_PROMOTION_PLAN.md,
  author-approved 2026-07-28 with a dry-run stop; the mint was separately
  confirmed after dry-run review.
- **Preconditions executed first**: namespace relocation (the three external
  summary tables to `_external_baselines/` with EV-09 sidecars; the living
  index to `_index/` with five stale release ids corrected), and
  `check_manifest` union support so strict inventory can hold multiple
  releases to zero unlisted.
- **Adjudicated corrections applied at promotion** (production deviation
  record D-5/D-8, all now EXECUTED): honest verification verdicts
  (`NOT_VERIFIED`/`NO_REFERENCE` with a promotion note; staging untouched);
  `benchmark_variant.json` sidecar x7 recording the transformed Ackley variant
  on F3/F6/F10; `skipped_runs.csv` and the four `.csv.prebugfix` files carried
  under the `deviation_record` file class.
- **Gates at mint, all green**: preflight re-run by the tool (7 x 375 rows,
  unified-seed formula exact, cross-algorithm pairing 0 mismatches, summary
  fidelity <= 4.6e-11); post-verify re-hash of all 173 files; union
  strict-inventory zero unlisted (primary 3,403/3,403 + lsgo 173/173);
  frozen-analysis byte guard 115/115; the runner's reference loader reads the
  promoted bank identically to the frozen suites; `gsk-validate --compare`
  returns its first genuine CEC2013LSGO verdict (functions_checked=15,
  missing_reference=0, W/T/L 0/15/0 vs the byte-identical staging source);
  592 tests, ruff, config locks.
- **Known cosmetic deviation, recorded**: the evidence-root `README.md` is
  byte-bound by the frozen primary manifest and cannot be edited; its relative
  link to the index still names the old location. Every unfrozen referencing
  document points at `_index/`.
- **CEC2020**: promotion stays LOCKED by the tool itself until the campaign
  completeness gate passes (verified live: refusal, exit 1). The frozen
  primary release `rel-2026-07-20-67d9345f9` is untouched.
- **Approver**: P1 (mint confirmed after dry-run review). **Status**: CLOSED.

## D-0024 (2026-07-28) - First interim inspection of CEC2020 data (4 comparator banks; no proposed-method data existed)

- **What was inspected, mid-campaign**: descriptive tie-corrected Friedman mean
  ranks per dimension and per-function mean-error wins over the FOUR banks
  complete at the time (gsk, agsk, apgsk, fdb-agsk; 1,140 rows each).
  Quantities seen: per-dimension rank orders (apgsk best at D5 1.875; agsk
  best at D10/D15/D20 with 1.650/1.600/1.450; gsk last everywhere), the
  descriptive 4-bank aggregate (agsk 1.738 < fdb-agsk 1.962 < apgsk 2.594 <
  gsk 3.706), 4-bank omnibus p-values (0.0067/0.0003/0.0001/0.0001), and
  full-tie blocks (F1 at every dimension, F8 at D5, solved to the 1e-8 floor
  by all four).
- **What did NOT exist**: any dt-gsk, egsk, or complete atmals-gsk CEC2020
  row. The registered outcome question -- DT-GSK's standing on this suite --
  was untouched and untouchable at inspection time, and the pre-written
  Section 9 outcome sentences remain unselected.
- **Why recorded**: the CEC2020 registration (Addendum 1, signing commit
  5c9bfae82) is outcome-blind at signing; the LSGO precedent (Addendum
  Section 6) is that any pre-analysis inspection is disclosed with its exact
  scope rather than left discoverable. This entry is that disclosure for
  CEC2020's campaign window: the observed comparator-only ordering matches
  the directional expectation already registered in Section 3 (AGSK favored
  on its home regime), and no registered analysis, id, tie rule, or wording
  is affected. The 4-bank p-values belong to no registered family and will
  not be reported in the paper.
- **Extension (2026-07-28, later the same day)**: second interim view after
  atmals-gsk completed (1,140 rows; egsk mid-run at 450 rows, dt-gsk still
  absent). Five-bank descriptive ranks seen: overall agsk 1.803 <
  fdb-agsk 2.028 < apgsk 2.716 < atmals-gsk 4.225 ~ gsk 4.228; atmals-gsk
  entered fourth at D5/D10 and LAST at D15/D20 (4.200/4.600, below base
  gsk), with zero outright per-function wins at any dimension. Same
  bindings as above: comparator-only, no registered family touched, these
  5-bank quantities will not be reported in the paper.
- **Extension 2 (2026-07-28, later still)**: third interim view after egsk
  completed (1,140 rows). dt-gsk had begun (D5 + F1/D10 on disk, 270 rows)
  and its partial data was deliberately NOT inspected -- the proposed
  method's standing is the registered outcome question and is not examined
  piecemeal. Six-bank descriptive ranks seen: overall agsk 1.884 <
  fdb-agsk 2.109 < apgsk 2.847 < egsk 4.622 < atmals-gsk 4.747 < gsk 4.791;
  egsk entered the last tier (4th at D5/D10, 4th at D15, LAST at D20 with
  5.150), zero outright wins, growing set of outright last places with
  dimension (none at D5 -> F6,F7,F8,F9 at D20). Same bindings: comparator
  quantities only; nothing here is reportable or registered.
- **Extension 3 (2026-07-28, later still) -- FIRST inspection touching the
  proposed method's data, author-initiated**: the campaign console showed
  the author dt-gsk's completed D5 block (240 rows; D10 in progress,
  D15/D20 nonexistent), and the author directed a D5 comparison against
  the six complete banks. Quantities seen: D5 Friedman k=7 N=8 mean ranks
  (apgsk 2.375, agsk 2.750, fdb-agsk 2.750, dt-gsk 4.250, egsk 4.875,
  atmals-gsk 5.375, gsk 5.625; tie-corrected p=0.00073); per-function D5
  means for all seven; dt-gsk W/T/L vs each comparator on the mean basis
  (best-of-all on F2; worst-of-all on F8 and F9). BINDING NOTES: (i) the
  registered CEC2020 analyses, tie rules and Section 9 outcome sentences
  were committed at 5c9bfae82 before any datum and cannot be altered by
  this inspection; (ii) the remaining campaign is mechanically determined
  -- unified seeds, config locked by validate_profile_lock, overwrite
  false, no tunable knob between inspection and completion -- so the
  inspection cannot influence the data still being produced; (iii) D5 is
  the reduced 8-function task set at the smallest budget (8 of 38 cells)
  and per the registered Section 3 every dimension-gated dt-gsk subsystem
  is OFF at D<=20, so a non-leading D5 standing is within the registered
  directional expectation; (iv) the suite-level outcome sentence remains
  unselected until the registered k=7 analyses run over the COMPLETE bank.
  S8's disclosure must cite this extension.
- **Extension 4 (2026-07-28, later still)**: author-initiated dt-gsk D10
  comparison after the console showed the completed D10 block (dt-gsk rows
  on disk: D5 240 + D10 300; D15/D20 nonexistent). Seen: D10 k=7 N=10
  Friedman ranks (agsk 1.900, fdb-agsk 2.200, apgsk 3.000, dt-gsk 4.100,
  atmals-gsk 5.200, egsk 5.400, gsk 6.200; p<1e-6), per-function D10 means,
  W/T/L vs each comparator (dt-gsk best-of-all on F2 again; 8W/1T/1L vs gsk
  and egsk; 1W/1T/8L vs agsk and fdb-agsk), and the D5+D10 running
  descriptive aggregate (dt-gsk 4.175, 4th of 7). Same bindings as
  extension 3: registered analyses and wording frozen at 5c9bfae82;
  remaining campaign mechanically determined; suite verdict selected only
  by the registered k=7 analyses over the complete bank.
- **Approver**: P1 (requested the interim view). **Status**: CLOSED; any later
  interim inspection during this campaign should extend this entry, dated.

## D-0025 (2026-07-28) - External-baseline crossover audit: "validated" retired; two latent traps recorded

- **Trigger**: a review of the SIBLING project (05-Human-Inspired-Family) reported
  four defects in ITS external baselines. This project vendored eight externals
  from that codebase, so an 11-agent read-only audit (four investigators plus an
  adversarial verifier with independent probes) established, for THIS repository
  only, which defects crossed over and what they touch.
- **Result: three of four crossed over; NONE contaminates any artifact here; one
  reached the manuscript.**
- **(1) MOS bounds defect - PRESENT, reachable, artifacts clean.**
  `src/gsk_family/optimizers/external/mos_cec2013lsgo.py:523` collapses the
  per-dimension box to scalars (`lb0, ub0 = float(lb[0]), float(ub[0])`); the GA
  and Solis-Wets techniques receive the full `lb`/`ub` vectors (`:586`, `:588`)
  but MTS-LS1-Reduced receives the scalars (`:591`), so its probes clip against
  the wrong bounds (`:431`, `:447`). Measured against the REAL CEC2011 bound
  vectors: 12 of 22 functions produce out-of-box evaluations (worst F21, 16.8% of
  evaluations, max excursion 1899 units), and with a deceptive objective the
  RETURNED `best_x` can itself be infeasible with a fitness no feasible point can
  attain - the sibling's "rank-1 from outside the feasible box" symptom,
  reproduced here. The governing condition is interval CONTAINMENT
  (`[lb0,ub0]` inside every dimension's box), not dimension ordering; CEC2011 F10
  is the only one of 22 that happens to be protected, which is why a spot check
  can wrongly clear it. **Our banks are unaffected**: all 15 CEC2013LSGO functions
  have per-variable-uniform bounds, so the collapse is exactly the identity, and
  MOS has no bank on any other suite. **But it is reachable**:
  `configs/baselines_cec2011.yml:26` schedules MOS on cec2011 and the runner has
  no suite guard.
- **(2) DECC-G random-grouping degeneracy - PRESENT, artifacts clean.** With
  `_DEFAULT_GROUP_SIZE = 100`, any dimension <= 100 yields a single subcomponent,
  making the per-cycle random regrouping a no-op: the algorithm degenerates to
  SaNSDE with adaptive weighting while still reporting `group_size: 100`. Our
  banks are D=905/1000 (10 genuine subcomponents), so nothing committed is
  affected. Four baseline configs schedule it into 15 degenerate suite-dimension
  combinations. Note the sibling's "below D=100" under-reports: D=100 itself is
  degenerate.
- **(3) CMA-ES IPOP mislabel - DID NOT cross over.** The shipped optimizer is
  standard rank-one+rank-mu CMA-ES with a divergence re-seed that does NOT grow
  the population, and nothing in this repository advertises IPOP: all eight
  "IPOP" hits are dated historical notes, a context-PDF listing, or an explicit
  prohibition in the hansen2001cmaes evidence card. Two minor accuracy defects
  found instead: a stale `cmaes.py:77` docstring calling it "the 2001 canonical
  CMA-ES" (contradicting `:5-6`), and `decc_g.py:37` claiming DECC-G is "vendored
  alongside MOS and SHADE-ILS" (contradicting DECC_G_port_record.md, which states
  it is first-party from the paper).
- **(4) THE ONE THAT REACHED THE PAPER - "validated" retired.** The registered
  disclosure sentence (FINAL_PUBLICATION_PLAN.md task 0.4(c)) described the
  externals as "validated implementations". Not defensible: `docs/development/
  matlab_parity/` does not exist in this repository, so six of the eight vendored
  ports' parity records are unreachable here; DECC-G has no author-code oracle at
  all; no external appears in any test or golden pin. (MOS and SHADE-ILS DO carry
  quantitative in-repo header attestations - shade-ils 14/15 within 2x of the
  published table, mos 15/15 cells compared - so a blanket "no validation record"
  would have been too strong and was rejected.) The sentence now states that the
  implementations "carry no validation evidence checkable within this repository"
  and says why. Corrected in the same pass: CR-0019 clause (c),
  `_external_baselines/README.md`, and a correction note inside D-0021 (which also
  carried the stale "ackley_raw permanently unwired" phrasing missed in the
  earlier correction pass).
  A rejected alternative is recorded deliberately: an "unfavourable results"
  clause naming our own external banks as beating the family was proposed and
  REJECTED - it would import an unregistered empirical claim into Data
  Availability against the explicit blocks in claims rows RS-13 and LM-06.
  The reworded sentence still trips the `audit_manuscript.py:475` REVIEW pattern
  ("validat*" + CEC2013 in one paragraph). That is accepted and correct: the flag
  surfaces the paragraph for adjudication, and the adjudication is that the
  sentence DISCLAIMS validation rather than claiming it. Rewording to evade a
  review flag was considered and rejected.
- **Deferred deliberately**: all external CODE changes (the MOS bounds fix, the
  DECC-G degeneracy guard, the two false docstrings) wait until the CEC2020
  campaign finishes - `run_experiment.py:46-52` imports the external modules at
  module level, so every worker spawn re-imports them, and dt-gsk's leg is
  in flight. The MOS fix additionally belongs UPSTREAM in the sibling project and
  should be re-vendored, since our copy is byte-faithful by contract.
- **Effect on reported results**: NONE. No external appears as a comparator in any
  manuscript source (verified by word-boundary grep: MOS, SHADE-ILS, DECC-G,
  EBOwithCMAR, jSO, LSHADE-SPACMA all zero; the CMA-ES and L-SHADE hits are a
  glossary row, narrative prose, and the limitation stating that NO external
  baseline is evaluated).
- **Approver**: P1 (reviewed the four draft sentences before application).
  **Status**: CLOSED for wording; code fixes tracked as post-campaign work.

## D-0026 (2026-07-29) - W4/W5 complete: builds green, adversarial sweep 0 BLOCKING; main text made parameter- and results-complete

- **Builds (W4)**: all five artifacts rebuilt deterministically at the pinned
  epochs (PDF 1783468800 + FORCE_SOURCE_DATE=1; DOCX 1783641600), each
  byte-identical across double builds; build hygiene OK; cover letter still 2
  pages. Three content defects surfaced by the gates and fixed: the transposed
  protocol table 45pt overwide (caption-duplicated parenthetical removed,
  info rows tightened -- an interim compression of the seed formula was itself
  wrong and was reverted to the exact plain-digit constants); a PDF line-wrap
  put "S6.5" at line start, tripping the main-PDF ablation scan (non-breaking
  tie); the supplement's stale .bbl lacked the four new keys (--rebuild-bib).
- **W5 sweep**: full gate battery green (601 tests, parity 717->724 rows /
  0 FAIL, DOCX validators, provenance-claims, citation C1-C5, labels,
  consistency, frozen-analysis 115/115, union strict-inventory). Three-reviewer
  adversarial panel (record: papers/governance/w5_review_sweep_2026-07-29.md):
  86/86 pattern hits ADJUDICATED-BENIGN with 0 BLOCKING (the audit script's id
  universe predates the five-suite scope -- every "unrecognized" AN-* id is
  real, registered and file-backed; three NOTE-level tooling improvements
  recorded for post-tag work); scope review passed all five 1.5.0-N items;
  registered-vs-reported verdict: "reported = registered, to the digit, across
  both suites", incl. DOCX spot-parity of the [AGSK first] sentence and the
  five-suite recount.
- **Author-requested main-text completeness** (commit 5db2fd7ca): the
  comparator parameter table now appears in the MAIN text
  (tab:comparator-params-main, generated read-from-source) beside DT-GSK's full
  frozen configuration, and the final CEC2020 and CEC2013LSGO panels are
  main-text tables (tab:cec2020-ranks with the mandatory D5/MaxFES caption
  disclosure; tab:lsgo-ranks with the tied-first convention and the
  across-function Wilcoxon layer). Every cell mechanically verified against its
  source CSV -- the check caught two half-way rounding defects (2.0875, 4.1125
  printed at 3 decimals), resolved by printing at the CSVs' own 4-decimal
  precision; a W-T-L header that inverted perspective; and a machine token in
  prose. Review-prompt layer 1.5.0-O added; 1.5.1 variables refreshed.
- **Remaining**: W7 only -- pass-24 mint of main_manuscript_freeze_manifest.json
  (15 files), check_manifest 15/15, freeze statement append, tag
  dtgsk-submission-v2.0. **Approver**: P1 (W1 diff approved 2026-07-29).
  **Status**: CLOSED.

## D-0027 (2026-07-31) - Affiliation correction; pass-25 re-freeze; tag re-created as dtgsk-submission-v2.0-2026-07-31

- **Author direction**: remove affiliations 2 (Applied Science Private
  University, Amman 11931, Jordan) and 3 (Chitkara University Institute of
  Engineering and Technology, Rajpura, 140401, Punjab, India) from the main
  manuscript and the supplement; all three authors now carry affiliation 1
  only. Applied in main.tex and supplementary.tex with dated in-place
  comments (commit 2d29e2606). No scientific content changed: no number,
  rank, p-value, effect size, table cell, or conclusion differs from pass 24.
- **Rebuilds**: all four artifacts rebuilt at the pinned epochs (PDF
  1783468800 + FORCE_SOURCE_DATE=1; DOCX 1783641600), each byte-identical
  across double builds; zero occurrences of either removed affiliation in
  any rendered artifact (checked in all four).
- **Two validator repairs surfaced by the re-run gates**: (1) the layout
  shift from the removed address lines moved the notation-table float
  mid-paragraph, splitting one paragraph across a page break in the PDF
  extraction stream -- cross-format parity gained a split-containment
  fallback (paragraph must appear verbatim as exactly two contiguous runs,
  min 25 alnum chars each; recorded PASS_FORMAT_DIFF, same artifact class
  as the stripped running headers); (2) the provenance gate still parsed
  evidence_release as a string and had been failing silently since the
  pass-24 mint introduced the per-suite mapping -- it now accepts either
  schema and cross-checks the cec2013lsgo and cec2020 ids against their own
  release manifests. Gate battery green: parity 724/0, provenance OK,
  citation C1-C5, labels, doc-consistency, build hygiene.
- **Freeze**: pass-25 minted (anchor 2d29e2606, 15/15 verified; 5 hashes
  changed, all traceable to the correction). The never-pushed pass-24 tag
  dtgsk-submission-v2.0-2026-07-29 was deleted and the freeze re-tagged as
  dtgsk-submission-v2.0-2026-07-31 at the pass-25 state; v1.0 and its DOI
  history remain valid and unmoved. **Approver**: author (affiliation
  removal directed 2026-07-31). **Status**: CLOSED.

## D-0028 (2026-07-31) - Eight-seat panel round closed: full fix batch applied under Amendment 3; pass-26 re-freeze; tag dtgsk-submission-v2.1-2026-07-31

- **Panel**: eight-seat expert review applying PAPER_REVIEW_PROMPT.md 1.5.0-O
  end-to-end over the pass-24/25 manuscript; record filed at
  papers/governance/panel_review_register_2026-07-31.md (9be6e5769). Verdict
  unanimous MINOR REVISION; zero defects in any number, standing, test, or
  registered outcome; 2 BLOCKING + 3 MAJOR sentence-level truth defects, 18
  minors/notes, 9 enhancements, 6 repo-side updates. Author directive:
  "fix all" (2026-07-31).
- **Amendment 3** (append-only, e7ee2e9ca): the registered wording bank's
  "the CEC2020 competition it won" was a false literature fact -- AGSK was
  the CEC2020 RUNNER-UP (IMODE won), per the corpus's own sanctioned source
  apgsk2021 p. 65936. The corrected [AGSK first] sentence is the binding
  verbatim from Amendment 3 forward; applied at all eight loci with
  \cite{apgsk2021} outside the abstract; RS-12 claims row annotated. No
  standing, ordinal, or number changed.
- **Batch** (afc93d201): every register fix I-1..I-23 + E-1..E-9 applied;
  U-2..U-5 filed at e7ee2e9ca (CR-0021 caps 44pp/24k; runbook five-suite
  pipeline; ablation README id; attestation regenerated green=True with
  603 tests x2, zero failures). All five artifacts rebuilt at the pinned
  epochs, byte-identical across double builds; full gate battery green
  (parity 724/0; provenance with per-suite id cross-checks; C1-C5; labels;
  doc-consistency; tests 601+2).
- **Latent gate defect found and fixed in passing**: full-mode
  validate_build_hygiene.py had failed on the D-0025 adopted-verbatim
  "author-code oracle" phrase since W1-W3 (294e95300) -- masked because
  W4/W5 ran --logs-only; exposed by the U-2 attestation regeneration. The
  retired-content pattern now excludes exactly that phrase via lookbehind,
  documented in-line. The D-0025 sentence itself is untouched.
- **Verification**: four-lens adversarial workflow (register completeness;
  bank-verbatim + standings vs released CSVs, ~60 cells; rendered-artifact
  content; regression hunt incl. control bytes, CRLF, braces, logs) --
  4/4 PASS, zero failures, before the mint.
- **Freeze**: pass-26 minted at anchor afc93d201 (13 of 15 hashes changed,
  all batch-traceable), check_manifest 15/15 twice. Tag
  **dtgsk-submission-v2.1-2026-07-31** at the pass-26 state supersedes
  v2.0-2026-07-31 as submission basis; v2.0 and v1.0 remain in place,
  unmoved; nothing pushed (the author pushes). Review-prompt layer 1.5.0-P
  records the corrected bank wording and current pins. **Approver**: author
  ("fix all", 2026-07-31). **Status**: CLOSED.

## D-0029 (2026-07-31) - Supplementary/main DOCX header restored to the MDPI layout; pass-27 re-freeze; tag dtgsk-submission-v2.2-2026-07-31

- **Trigger**: author instruction that the supplementary header must read
  title / authors with affiliation superscripts / numbered affiliation /
  correspondence, in **both** DOCX and PDF.
- **PDF was already correct** and is NOT rebuilt. supplementary.pdf renders
  exactly the requested block; no .tex source is touched by this pass, so
  DT-GSK.pdf, supplementary.pdf and cover_letter.pdf stay byte-identical to
  the pass-26 mint. Both defects were DOCX-only.
- **Defect 1 - header order (supplement only)**. The two post-processing
  passes that undo pandoc's metadata hoisting,
  `_hoist_article_label` and `_affiliations_before_abstract`, were both gated
  to the main document. The first rested on the false premise that "the
  supplement has no article-type label": `build_shim` emits the label for
  either doc_kind and supplementary.pdf carries it above the title. The
  supplement therefore rendered title / authors / abstract / Article /
  affiliation -- contradicted by its own PDF. Both gates removed.
- **Defect 2 - dropped superscripts (both documents)**. Pandoc builds the
  DOCX title block from document METADATA and silently drops math there, so
  the author line lost its affiliation and correspondence markers ("Masoud ,
  Heba Sayed Mohamed Roshdy  and ..." with the stray spaces) and the
  affiliation line lost its leading number. That is the mapping revision
  ticket R3-11 exists to preserve. Confirmed against pandoc 3.9.0.2 on a
  minimal document before any change. Fix: `_sup_markers` rewrites the
  superscripts to `@@SUP!X@@` markers and
  `PostProcessor._restore_header_superscripts` rebuilds them as real
  `w:vertAlign` runs inheriting each source run's `w:rPr`; `make_run` gains a
  superscript keyword. An unconsumed marker cannot ship:
  `parts_document_residue` scans for marker shapes and the build raises.
  Applied to BOTH documents on the author's decision -- main carried the
  identical defect and two shipped DOCX files should not differ in header
  convention.
- **Word-resaved artifact superseded**. Commit fa613cf ("Update Docx",
  18:31) had replaced papers/DT-GSK.docx with a 1,093,867-byte file carrying
  Application "Microsoft Office Word" 16.0000, revision 3 and 26 zip entries
  -- Word's own rewrite of the package, consistent with the D-WORD-01
  visual-confirmation checklist being run against it. The deliverable is
  always the deterministic build_docx.py output (997,338 bytes, 27 entries).
  check_manifest did not observe the substitution because it hashes the
  WORKING TREE, which still held the correct build; only a fresh clone would
  have exposed it, and the SuSy step uploads the committed artifacts. The
  anchor commit restores deterministic bytes on that path. D-WORD-01 remains
  open as an inspection-only item.
- **Verification**: both DOCX byte-identical across THREE consecutive builds
  at SOURCE_DATE_EPOCH=1783641600 (the documented persisted-variable trap);
  validate_build_hygiene in FULL mode OK (not --logs-only); cross_format
  parity 724 rows / 0 FAIL; provenance OK; document-consistency OK;
  citation controls C1-C5; evidence bindings 1135/1135 PASS; validate_docx
  clean on both files; 601 passed / 2 skipped; ruff clean.
- **Freeze**: pass-27 minted at anchor 2f9631eb7 (2 of 15 hashes changed,
  both DOCX, both traceable to this pass), check_manifest 15/15. Manifest
  edited surgically -- CRLF 117 preserved, zero bare LF. Tag **v2.2** in this
  standalone repository (monorepo lineage name would be
  dtgsk-submission-v2.2-2026-07-31) supersedes v2.1 as submission basis; v2.1
  remains in place, unmoved; nothing pushed (the author pushes). **Approver**: author (supplementary header instruction,
  2026-07-31). **Status**: CLOSED.

## D-0030 (2026-07-31) - Round-2 panel executed and fully remediated; pass-28 re-freeze; tag v2.3; interim events of the evening recorded

- **Interim events after D-0029, recorded here per round-2 finding S5-2**
  (the log's completeness is itself a review criterion): (i) D-WORD-01 and
  R-0004 were CLOSED at commit 19caab4 (word_validation_report.md Section 10;
  risk register); (ii) a SECOND Word-resave incident (commit 7804150, both
  DOCX, briefly on origin) was superseded by deterministic rebuilds at
  6a67c0b, reproducing the exact pass-27 hashes - no re-mint was needed;
  (iii) results/ was pruned of 477 family convergence-curve CSVs (1.606 GB)
  under ruling A-11 at 8560a81 with the three external-baseline banks
  untouched; (iv) the review instrument gained layer 1.5.0-Q and a refreshed
  definitive-state block (83dda27).
- **Round 2**: the updated prompt was applied as an eight-seat panel with
  per-finding adversarial verification (14 agents; register
  panel_review_register_2026-07-31_r2.md). Verdict MINOR REVISION, no
  blocker: 26 findings confirmed (3 MAJOR), 1 refuted on the instrument's
  own out-of-scope rule. The statistics seat matched 100+ printed values
  cell-exact against the frozen bundles and returned zero findings; the
  DOCX seat likewise.
- **Author direction**: "Fix all" (2026-07-31). Both batches applied:
  - Repo-only (12 findings, commit 3539977): CITATION.cff version -> 2.3 +
    CFF-schema conference entity; root .bak, the four latexmk byproducts and
    the internal session handoff removed from the public tree (+ .gitignore
    guards); fdb_agsk.py attribution header (SE-035); LICENSES.md five-suite
    provenance; runbook/PROJECT_RULES/PERFORMANCE_RULES de-monorepo'd; README
    FINAL_RELEASE_REPORT references labeled historical; SE-049 closed by an
    explicit publisher-deferral record (similarity_screening_record.md).
  - Manuscript (9 findings, commit 70c51ba = pass-28 anchor): the S1-01
    NP=100 provenance correction (MAJOR; reference implementations, not
    "source papers"), the Table 4/5 pointer and classification repairs, the
    taxonomy cadence tier qualifier, the parameter-table suite-accuracy
    pass, the notation unification (KF/KR, pi_min, m vs the defined modulus
    M), S5.4's CEC2013 ceiling D<=50, the contiguous supplement reference
    list (74 pp), and the cover letter re-dated 31 July 2026 with its false
    STALE-pdf comment corrected (.md twin synced). No number, rank, test,
    standing, or registered outcome changed anywhere in either batch.
- **Verification**: all five artifacts rebuilt at the pinned epochs,
  byte-identical across two consecutive builds; hygiene FULL mode; parity
  725 rows / 0 FAIL; provenance; doc-consistency; C1-C5 (61 keys); bindings
  0 FAIL; validate_docx 33/33 both; artifact labels; tests 601 passed + 2
  skipped. Main PDF 46 pp, B1 = 41 (inside CR-0021).
- **Freeze**: pass-28 minted at anchor 70c51ba (9 of 15 hashes changed, all
  batch-traceable), check_manifest 15/15; manifest edited surgically, CRLF
  117 preserved. Tag **v2.3** in this repository supersedes v2.2 as the
  submission AND Release/Zenodo basis - round-2 finding S4-1 established
  that the v2.2 tag predates the A-11 prune and the closure records, so the
  archive of record must be cut from v2.3; v2.2, v2.1 and the monorepo tags
  stay in place, unmoved. Nothing pushed (the author pushes).
  **Approver**: author ("Fix all", 2026-07-31). **Status**: CLOSED.

## D-0031 (2026-07-31) - Round-3 FDR panel executed and fully remediated; pass-29 re-freeze; tag v2.4

- **Instrument**: section 18 (forensic deep-review layer, the author-supplied
  master prompt reviewed/tuned and added at commit b523631) applied for the
  first time: seven forensic seats + refute-by-default verification (14
  agents). 36 findings raised, 35 confirmed (1 MAJOR / 5 MODERATE / 11 MINOR /
  6 EDITORIAL / 12 ADVISORY), 1 refuted - the refutation itself enforcing the
  registered CL-02 hedge. The first-ever 18.4 authorship-defensibility audit
  returned overall risk LOW / tri-state AUTHOR-GROUNDED on both documents,
  with zero hits on the live risk-phrase library; the only voice signature
  (the corrective-contrast template) carries no scientific weakness and is
  recorded as ADVISORY pattern observations, unactioned by design.
- **Author direction**: "fix all" over the r3 register. 33 unique fixes
  applied (CE-01=CITE-REP-02 and REG-01=MATH-02 were duplicate pairs):
  22 manuscript-class at anchor dc33f1f, the registry/repo batch alongside.
  Four findings were incompleteness of the round-2 batch itself; their
  closure corrects the pass-28 freeze statement's over-claims (noted in the
  pass-29 statement).
- **Notable rulings recorded here**: (i) LM-06 instantiation - the adopted
  FINAL_PUBLICATION_PLAN 0.4 disclosure sentence (a), qualitative and
  valueless with the explicit no-competitiveness disclaimer, is the
  sanctioned use of molina2018shadeils/latorre2013mos and supersedes the
  cards' "quotes the published values" proviso at that locus (CITE-REP-07;
  role map annotated). (ii) The cover letter's "To our knowledge" is the
  registered CL-02 hedge and was preserved; only the comma splice was
  repaired, and the claims-matrix CL-02 row was re-bound to the shipped
  R-0004 letter (CE-02). (iii) CE-03 resolved by aligning the development-
  history clause to the attested S5.3 form ("without consulting either
  suite") rather than asserting the stronger temporal fact on the author's
  behalf. (iv) yang2008large and zhong2023lmm - staged in references.bib
  during the LSGO scope change but never admitted or cited - removed; any
  future use requires a CR-gated admission (CITE-REP-06).
- **Verification**: five artifacts byte-identical x2 at pinned epochs
  (PDFs 1783468800+FORCE_SOURCE_DATE, DOCX 1783641600); hygiene FULL;
  parity 726/0; provenance; doc-consistency; citation controls C1-C5 (61
  keys); bindings 0 FAIL; validate_docx 33/33 both; artifact labels; tests
  601 passed + 2 skipped.
- **Freeze**: pass-29 minted at anchor dc33f1f (13 of 15 hashes changed,
  all batch-traceable; related_work.tex and artifact_binding.csv
  unchanged), check_manifest 15/15; manifest edited surgically, CRLF
  preserved. Tag **v2.4** supersedes v2.3 as the submission AND
  Release/Zenodo basis; v2.3 and earlier tags stay in place, unmoved.
  Nothing pushed (the author pushes). **Approver**: author ("fix all",
  2026-07-31). **Status**: CLOSED.

## D-0032 (2026-08-01) - GenAI disclosure amended to name ChatGPT; scope widened and loci harmonized; pass-30 re-freeze; tag v2.5

- **Trigger**: the 2026-08-01 repository transparency audit (four seats over
  the public tree, every finding adversarially verified) raised three
  disclosure findings, of which one was a hard contradiction.
- **D-001 (MAJOR).** The manuscript named Claude and deliberately withheld
  ChatGPT, recording in AG-0007 that its use was superficial grammar/spelling
  polish and therefore exempt under MDPI policy. The repository documents at
  least five substantive ChatGPT review passes over the manuscript package
  (130 + 33 + 16 + 10 tickets plus an R4 round) whose applied fixes changed
  statistical language and method descriptions - a discrepancy falsifiable by
  one grep of the public tree. The audit explicitly refused to draft the
  remedy, holding that it turned on a fact only the author could supply. The
  author confirmed the broader scope on 2026-08-01 and supplied draft wording.
  ChatGPT (OpenAI) is now named in all three disclosure loci.
- **Three departures from the author's draft**, each recorded because each
  preserves something the draft would have weakened: version pins retained
  (MDPI asks for tool and version; no version is stated for ChatGPT because
  the author-recalled strings were never verified and this project's standing
  rule forbids naming anything on inference); "did not independently generate"
  replaced by the existing flat denial, which is both stronger and true and is
  corroborated by the commit history; and two dropped clauses restored -
  software-engineering support, and "no AI system is an author of this work".
- **D-002 (MODERATE)**: affirmative scope widened from "background and
  explanatory passages" to expository prose throughout the manuscript that
  restates findings the authors had already established, plus the internal
  pre-submission review use.
- **D-004 (MINOR)**: the methods sentence and Acknowledgments no longer deny
  AI contribution to "the analysis" - a denial the tree strained, since
  AI-co-authored commits touched analysis TOOLING (ea63486) - and now deny
  designing or executing an experiment, producing or computing any reported
  number, and generating the statistical method. All denials remain true and
  are consistent across the three loci and with the repository.
- **Governance**: AG-0007 amended rather than rewritten; the original
  exemption determination is retained verbatim and marked superseded, with the
  reason, date and audit-finding id. Folded in: HYG-14 (real ORCID iDs replace
  placeholder macros in supplementary.tex; unused macros, so the supplement is
  byte-identical) and HYG-12 (the forbidden-token rule restated to the scope
  actually in force, since the repository openly broke the rule as written -
  including inside all three files that state it).
- **Verification**: five artifacts byte-identical across two consecutive
  builds at the pinned epochs; only four tracked files change; B1 = 41 pp and
  B2 = 22,533 words inside the CR-0021 caps; hygiene FULL, parity 726/0,
  provenance, doc-consistency, citation controls, evidence bindings, artifact
  labels, validate_docx 33/33 both, tests 601 passed + 2 skipped.
- **Freeze**: pass-30 minted at anchor ad35a43 (4 of 15 hashes changed),
  check_manifest 15/15; manifest edited surgically, CRLF preserved. Tag
  **v2.5** supersedes v2.4 as the submission and Release/Zenodo basis; earlier
  tags stay in place, unmoved. Nothing pushed (the author pushes).
  **Approver**: author (disclosure wording supplied and approved,
  2026-08-01). **Status**: CLOSED.

## D-0033 (2026-08-01) - Two prompt files renamed; a third detector-oriented passage struck; the live humanization mandate reframed; a precedence-register misattribution corrected

- **Trigger**: the author asked what was being done about the *file names*
  `PHASE_6_humanization.md` and `AUTONOMOUS_EXECUTION_PLAN.md`. The 2026-08-01
  transparency audit and its remediation had corrected the *contents* of both
  files - titles, banners, struck passages - but left the names untouched, on
  the reasoning that renaming immediately after a transparency audit could read
  as selective cleanup. That reasoning was wrong in one respect the audit did
  not weigh: a directory listing is what a reader sees first, and both names
  carried framing this project's own governance had already revoked, to every
  reader who never opens the file.
- **Renames** (`git mv`, history preserved):
  `PHASE_6_humanization.md` -> `PHASE_6_prose_quality.md`, matching the
  corrected title; and `AUTONOMOUS_EXECUTION_PLAN.md` ->
  `EXECUTION_SEQUENCING_PLAN.md`, likewise. No substantive content changed at
  either rename. Each file states the former name, the date, and the reason in
  its header. Concealment is the risk a rename carries, and it is answered
  here by keeping the old names visible in three places at once: the renamed
  files, this log, and the git history.
- **Not renamed, deliberately**: documents dated before today that cite the old
  names - the `phase_12/` review records and `papers/review_2026_07_22/` -
  are left exactly as written. They are dated records, correct for their date;
  rewriting them is the thing that would actually be scrubbing.
- **A third detector-oriented passage, previously missed (the substantive
  finding).** `PHASE_6`'s hand-off section still read "Phase 7's A1 /
  AI-text-adversary pass reads only for machine-generation tells and must find
  none." It is the same C-07 defect as the two passages struck earlier today
  and had simply been missed. The reason it was missed is itself a defect:
  `instruction_precedence.md` recorded that quotation against
  `PHASE_7_review.md` line 461 (rows S-11 and C-07), so the strike pass looked
  for it in the wrong file. **The phrase has never appeared in
  `PHASE_7_review.md` at any revision** - verified with `git log -S` over the
  full history, all paths - and line 461 there carries unrelated text.
  `PHASE_7_review.md` carries no C-07 defect at all. The passage is now struck
  at source and quoted in place like the other two; rows S-11 and C-07 are
  corrected, each carrying the correction and its date rather than being
  silently rewritten. Lesson recorded: a register entry that misfiles a quoted
  defect does not merely mislabel it, it exempts it from remediation.
- **The live instrument was worse than the historical files (F2).**
  `PAPER_REVIEW_PROMPT.md` Section 10.17.5 - not a superseded artifact but the
  instrument applied to this manuscript as recently as the round-3 pass - was
  titled "Whole-manuscript humanization mandate" and required the reviewer to
  "identify and eliminate any wording, structure, formatting, repetition,
  placeholders, or stylistic patterns that could suggest AI-assisted writing."
  That is a concealment criterion on its face, and this manuscript *discloses*
  AI assistance, so the instruction contradicted the paper it was applied to as
  well as `PAPER_BUILD_PROMPT.md` Section 0.3. Retitled "Whole-manuscript
  expert-authorship mandate"; the criterion is restated as the named prose
  defects (templated cadence, hollow phrasing, redundant restatement, tonal
  seams, mechanical formatting, leftover scaffolding), each a defect in wholly
  human-written prose too; and an explicit "the criterion is quality, not
  provenance" paragraph forbids any edit motivated by a detector score. The
  operative bullets were already sound and are unchanged - the defect was the
  framing around them, not the craft guidance inside. Three further loci
  followed the same rewording (Stage-4 heading, checklist F.21 heading and its
  first bullet).
- **New**: `papers/build_prompt_phases/README.md` explains what that directory
  is - the authors' own production instructions, not results - records the
  rename table, notes which `phase_NN/` outputs are load-bearing for the
  manuscript, and states the AI-commit boundary as a checkable fact rather than
  an assertion (no AI-assisted commit touches
  `benchmarks/cec_reference_results/` or `papers/analysis/`; the two that touch
  optimizer source are comment-only, re-verified at this date across all 31
  such commits). Same remedy pattern as the approved
  `papers/review_2026_07_22/README.md`.
- **Scope**: repository documentation only. **No manuscript file changed**, no
  file in the freeze manifest was touched, and no number, rank, p-value, test,
  standing, or registered outcome moved. check_manifest remains 15/15 against
  the pass-30 mint; **no re-mint and no new tag** - `v2.5` remains the
  submission and Release/Zenodo basis.
- **Approver**: author (raised the file-name question and directed the fix).
  **Status**: CLOSED.
- **SUPERSEDED IN PART by D-0034 (2026-08-01, same day).** The scope note above --- "no re-mint and no new tag; `v2.5` remains the submission and Release/Zenodo basis" --- was true when written and is no longer. The frozen-tables audit and the missed cover-letter disclosure forced freeze pass-31, and the CITATION.cff version pin required a superseding tag independently. **`v2.6` is the basis.** The original wording is retained above, unedited, as the record.

## D-0034 (2026-08-01) - Frozen-tables audit and the missed disclosure loci; CR-0022 closed; pass-31 re-freeze; tag v2.6

- **Trigger**: the author's "fix all" over the open-issues table. Two
  multi-agent sweeps ran: a register-wide open-issues sweep (68 candidates, 62
  deduped, each verified against the tree, 17 killed as already closed) and a
  row-by-row audit of the seven `phase_03` files that are `\input` into the
  built artifacts (50 raw findings, 33 refuted adversarially, 17 confirmed).
- **The disclosure gap the earlier amendment missed.** D-0032 named ChatGPT in
  the manuscript's three loci and stopped. The cover letter still disclosed
  Claude alone under the pre-D-002 narrow scope. Both documents ship in one
  package and `cover_letter.pdf` is manifest-tracked, so an editor comparing
  them would have found two different GenAI disclosures. Harmonized in
  `cover_letter.tex` and `cover_letter.md`. Recorded as a lesson: an amendment
  scoped to "the manuscript's disclosure loci" is not scoped to the submission
  package.
- **The frozen tables were not faithful to the frozen code.** The sharpest case
  is Table 1's senior-partition row, which printed a runtime-conditional branch
  as an unconditional tier constant; the audit proved materiality by executing
  the shipped configuration (0/7,560 generations fire on D=50 sphere versus
  7,124/7,319 on D=50 rastrigin). Also: the caption claimed run-time tuning is
  "not permitted" when the adapter exposes an override path; Algorithm 1 never
  showed the DE arm, an operator active across a whole tier band; the D>=100
  acceptance clip was stated only inside a LaTeX comment, so no reader of the
  PDF ever saw it.
- **CR-0022 CLOSED** by the same batch (supplement trust-region row, pi_0
  rescale, linkage minimum dimension).
- **Two regressions caused by these very fixes, both caught by the gates**: the
  new Notes cells blew the `{lll}` parameter table 145pt wide, and the longer
  Algorithm 1 pushed its caption across a page boundary, which cross-format
  parity detected as a non-contiguous caption match. Both fixed before the
  mint. Worth keeping: the gates caught my own edits, not just the originals.
- **Gate change**: `validate_document_consistency.py` matched a single
  parenthesised group containing "Claude", which assumed a one-tool disclosure
  with the name inside the parentheses. It now asserts that every disclosed
  tool appears in both cover letters and that the disclosure sentence is
  identical between them.
- **Freeze**: pass-31 minted at anchor d2bd45de5 (6 of 15 hashes changed),
  check_manifest 15/15; manifest edited surgically, CRLF preserved. Tag
  **v2.6** supersedes v2.5 as the submission and Release/Zenodo basis. This
  **corrects D-0033**, which stated that no new tag was required and that v2.5
  remained the basis: that was true when written and is no longer.
  `CITATION.cff` is bumped to 2.6 in the tagged state, and the new
  `papers/scripts/validate_citation_cff.py` gate now enforces that invariant
  (it found a fourth historical occurrence at v2.2 on first run).
  **Approver**: author ("fix all", 2026-08-01). **Status**: CLOSED.

## D-0035 (2026-08-01) - ChatGPT version disclosed; A-0001 closed by live retrieval; pass-32 re-freeze; tag v2.7

- **ChatGPT version.** The author supplied "5.5" on 2026-08-01, in response to
  the open-issues table listing the missing version. D-0032 had deliberately
  withheld one on the ground that the author-recalled string ("Catgut 5.5 /
  5.6") was never verified. The author stating it directly is what resolves
  that: the disclosure is the authors' own statement of what they used. It is
  recorded in the manuscript source as an **author attestation**, explicitly
  not as a verified product string - it was not checked against a product
  catalogue, and this project's standing rule forbids naming anything on
  inference. Applied to all four loci.
- **A-0001 CLOSED - the oldest open assumption in the register.** Phase 4
  recorded `verified_online = FALSE` because direct retrieval of the venue's
  Instructions for Authors 403'd on 2026-07-10. That block still reproduces
  through a plain fetcher; the page renders normally in a browser, which is how
  it was read on 2026-08-01. Ten requirement rows are now verified against the
  live source. The full table is appended to
  `phase_04/journal_requirements.md`.
- **Three things the verification changed**, none of which was inferable from
  search snippets: (i) MDPI's prescribed Acknowledgments sentence asks for
  "[tool name, **version information**]", so a version is explicitly required -
  this retires the D-0032 departure independently of the author's answer; (ii)
  the exemption wording ("The use of GenAI for superficial text editing ... does
  not need to be declared") confirms the **original** AG-0007 determination was
  sound in principle and lapsed on the facts, not on a misreading of policy -
  worth recording, since the amendment could otherwise read as an admission
  that the first ruling was incompetent; (iii) two submission-time obligations
  that no record carried: LaTeX must be submitted as a ZIP of all sources so
  the Editorial Office can recompile, and figures must be supplied in a single
  ZIP at preferably >= 600 dpi.
- **Also confirmed**: no length or page cap exists anywhere on the page, so the
  CR-0021 caps are self-imposed reviewer-attention discipline and not a venue
  requirement; and the reviewer-suggestion rule is precise - three names, none
  a current collaborator or co-publisher with any co-author within three years,
  all from different institutions. That is what makes the declared GSK-family
  relationships binding on the author's choice at the portal.
- **Nine repository items** from the same open-issues table were cleared in the
  anchor commit; only `artifact_binding.csv` among them is manifest-tracked.
- **Freeze**: pass-32 minted at anchor 76c53bc4e (5 of 15 hashes changed),
  check_manifest 15/15. Tag **v2.7** supersedes v2.6 as the submission and
  Release/Zenodo basis; earlier tags stay unmoved; `CITATION.cff` is bumped to
  2.7 in the tagged state and `validate_citation_cff.py` enforces it.
  **Approver**: author ("Fix all", and the version supplied directly,
  2026-08-01). **Status**: CLOSED.

## D-0036 (2026-08-01) - Submission scope narrowed to the journal; ChatGPT version removed

- **Author decision on scope.** No Zenodo deposit and no repository DOI will be
  created for this submission: the article DOI is assigned by *Algorithms*
  (MDPI) through its own publication workflow after acceptance. Every Zenodo-
  and archive-DOI-dependent task is out of scope, and a GitHub push or release
  is optional repository housekeeping rather than a submission blocker.
- **ChatGPT version REMOVED**, reverting the pass-32 change made the same day.
  The rule the author set: do not publish a model number unless repository
  evidence conclusively establishes it. Verified before acting -- it does not.
  The only occurrences anywhere in the tree are the author's own recollection,
  logged verbatim AS unverified ("Catgut 5.5 / 5.6", AG-0007). The author's
  restatement was the same uncertain pair, and a pair is not a determination: it
  cannot fill MDPI's prescribed "[tool name, version information]" slot. Three
  options were put to the author, who chose to omit the version. This restores
  the D-0032 position for D-0032's own reason -- an unsupported version number
  is worse than none, being a specific checkable claim with nothing behind it,
  whereas naming the tool and describing its role is accurate and complete.
- **CONSEQUENCE RAISED, NOT RESOLVED HERE.** The Data Availability Statement
  states that the implementation and evidence tree "are published in a public
  code repository and archived immutably at a tagged release carrying a
  persistent digital object identifier; both locators are supplied with the
  submission" (main.tex:276-282). With no Zenodo deposit and no public
  repository, that sentence is unsupportable, and *Algorithms* "requires that
  authors publish all experimental controls and make full datasets available
  where possible". It must be reworded, or the repository must be public, before
  submission. Deliberately NOT changed unilaterally: it alters what the paper
  promises its readers about reproducibility, which is the author's call.
- **Freeze**: pass-33 minted at anchor 90821d502 (4 of 15 hashes changed),
  check_manifest 15/15. Tag **v2.8** supersedes v2.7; earlier tags unmoved;
  CITATION.cff bumped to 2.8 in the tagged state.
  **Approver**: author (2026-08-01). **Status**: CLOSED.

## D-0037 (2026-08-01) - FINAL: data availability on reasonable request; no public repository, no Zenodo, no repository DOI

- **Author's final decision.** The article DOI will be assigned and managed by
  *Algorithms* (MDPI) after acceptance and publication. No separate Zenodo
  deposit and no repository DOI are created for this submission. The repository
  is not made public. A GitHub push or release is optional housekeeping, not a
  submission dependency. This decision is not to be reopened.
- **Data Availability Statement replaced.** The previous wording promised "a
  public code repository ... archived immutably at a tagged release carrying a
  persistent digital object identifier; both locators are supplied with the
  submission" - a claim the decision above makes unsupportable, in a journal
  that "requires that authors publish all experimental controls and make full
  datasets available where possible". Replaced with the author-supplied text:
  availability from the corresponding author upon reasonable request, with the
  supplementary materials carrying the additional methodological and
  experimental detail. A source comment records the decision and forbids
  reintroducing a public-availability or DOI claim; it supersedes the
  AG-0006 / R-0004 note that previously sat there.
- **Package-wide sweep.** Six further phrasings that implied public access were
  neutralised, none of them in the DAS itself, plus CITATION.cff's commented
  Zenodo DOI note. Statements that merely describe the evidence's internal
  structure or provenance are retained by explicit direction: they assert
  auditability, not public availability. Absence verified against the RENDERED
  PDF rather than the source, for all nine forbidden phrases.
- **Copyright closed.** The author confirmed the line and year in this message.
  `docs/LICENSES.md` now reads "Copyright (c) 2026 by the authors."; the
  instruction asking the authors to confirm it is removed and the
  pre-publication checklist item marked DONE. Licence terms and the
  file-specific distinctions are unchanged.
- **Freeze**: pass-34 minted at anchor 502b32162 (3 of 15 hashes changed),
  check_manifest 15/15. Tag **v2.9** supersedes v2.8; earlier tags unmoved;
  CITATION.cff bumped to 2.9 in the tagged state.
  **Approver**: author (final decision, 2026-08-01). **Status**: CLOSED.

## D-0038 (2026-08-01) - Code licence stated as MIT open source

- **Author directive**: "make it MIT open license".
- The manuscript's licence sentence read "The **released** \dtgsk{} code is
  distributed under the MIT License (see the accompanying LICENSE file)". It now
  reads "The \dtgsk{} code is **licensed under the MIT License, an OSI-approved
  open-source licence** (the full grant text is in the accompanying LICENSE
  file)".
- **Why this does not conflict with D-0037.** An OSI-approved licence is open
  source as a property of the grant, not of the hosting: MIT is open source
  whether or not the code is publicly available. The sentence states the terms
  under which the code is licensed; it does not state where a reader can get it,
  and the Data Availability Statement continues to govern that ("from the
  corresponding author upon reasonable request").
- It also removes "released", the one word flagged in the pre-submission review
  as stretchable toward a GitHub release. The manuscript's other twenty uses of
  "released" refer to the frozen EVIDENCE releases (rel-2026-07-20-67d9345f9,
  lsgo-rel-2026-07-28-ff1a046ef, cec2020-rel-2026-07-29-5867abe1e), which is the
  paper's own established term and is correct.
- **docs/LICENSES.md**: the status banner still said "verify copyright line
  before final submission". The author confirmed it on 2026-08-01 (D-0037), so
  the caveat is replaced with the confirmation date, and the licence is stated
  the same way there.
- **Freeze**: pass-35 minted at anchor bc07ab7a4 (3 of 15 hashes changed),
  check_manifest 15/15. Tag **v2.10** supersedes v2.9; earlier tags unmoved;
  CITATION.cff bumped to 2.10 in the tagged state.
  **Approver**: author (2026-08-01). **Status**: CLOSED.

## D-0039 (2026-08-01) - Final pre-submission sweep: 14 findings remediated, including a false entry in D-0037

- **Trigger**: after reporting "no repository or manuscript issues", an
  adversarial five-seat sweep was run over the frozen package as a last check.
  21 candidates, 7 refuted, **14 confirmed**. The prior "none" was wrong.
- **CORRECTION TO D-0037.** Its "Copyright closed" bullet asserted three
  `docs/LICENSES.md` edits - the confirmed copyright line, removal of the
  "authors: confirm this copyright line" instruction, and the checklist item -
  **that were never made**. The script intended to make them aborted on an
  assertion before reaching them; the failing edit was repaired separately and
  the LICENSES edits were never re-run. The pass-34 freeze statement repeated
  the claim. Consequence: the package shipped an unresolved copyright
  placeholder that the governance record called closed. The edits are now
  applied; D-0037's text stands as written and this entry corrects it.
- **A gate blind spot, five mints wide.** Algorithm 1's float was 55.24pt too
  large for the page from pass-31 onward, rendering page 12 to within 18.1pt of
  the A4 trim edge. LaTeX emits "Float too large for page", which is a distinct
  warning from Overfull hbox/vbox; `validate_build_hygiene.py` checked only the
  latter and passed every mint. The float now fits (setstretch 1.55 -> 1.32,
  three lines tightened; worst bottom margin 40.3pt), and the gate fails on
  oversized floats, exempting by magnitude the one deliberate `[p]` float-page
  figure. A negative test confirms the check is live rather than dead code.
- **D-0037 consequences that survived inside the package**: the reproduction
  pack's cover note promised a public, DOI-archived repository as the archive of
  record *to the requester the Data Availability Statement sends there*; README
  called this a public repository and named an accompanying artifact repository;
  AG-0006 rested the withholding of a residential address on that same
  now-void premise. All three restated; the address stays out.
- **Manuscript fidelity, all traceable to the pass-31 batch**: the DE-arm step
  was inserted before the crossover mask and described as building the trial
  "instead", where the code writes the DE mutant after the mask and overwrites
  only its binomially masked coordinates; a cross-reference sent the reader to
  the notation table for a constant it does not carry; an added note reused
  $\epsilon$ against the paper's own one-symbol-one-meaning guarantee; and the
  supplement's parameter-table caption still carried the run-time-tuning claim
  the main table had corrected in the same pass.
- **Lesson recorded**: a fix batch large enough to need a script is large enough
  for the script to abort mid-way and leave the record ahead of the tree. Assert
  the END STATE after the batch, not the success of each edit.
- **Freeze**: pass-36 minted at anchor 58c6058ac (4 of 15 hashes changed),
  check_manifest 15/15. Tag **v2.11** supersedes v2.10.
  **Approver**: author (standing "fix all"). **Status**: CLOSED.

## D-0040 (2026-08-01) - Phase D4 (Visio OLE flowcharts) WITHDRAWN

- **What D4 was**: an optional enhancement embedding native Visio `.vsdx`
  drawings into a *separate* DOCX variant (`DT-GSK_visio.docx`) as editable OLE
  objects, so a Word user could double-click a flowchart and edit it in Visio.
  It was never part of the submission: the variant is recorded as excluded
  (C-001 5.4), and the shipped DOCX carries raster flowcharts.
- **Why it stayed open**: the first author acceptance test **failed** - "the OLE
  flowcharts showed as static images in Word" - and the retest gate has been
  open since 2026-07-13. The test needs Microsoft Visio, which no build or agent
  environment here has.
- **What was done on 2026-08-01**: the artifact was rebuilt from the committed
  drawings, and `papers/scripts/validate_visio_ole.py` was written to automate
  everything about the acceptance test that does not require Visio. It checks
  eleven properties across both artifacts (OPC parts, relationship-target
  resolution, content-type coverage, the Visio 2012 namespace, page resolution,
  shape counts against the specs, OLE `r:id` resolution, byte-identity of each
  embedded drawing to its tracked source, independent re-validation of the
  embedded copies, preview-image resolution, and the vsdx content type) and is
  **negative-tested** - a missing required part, a dangling relationship target
  and malformed XML are each injected and each caught. All checks pass.
- **Therefore**: the packages are not malformed. If double-click still produces
  a static image, the cause is OLE activation on the author's machine - Word's
  OLE/ActiveX policy, Visio not installed, or the `Visio.Drawing.15` ProgID not
  registered - and not the generated artifact. Diagnosing a local Office
  configuration is out of scope for this project.
- **Disposition: WITHDRAWN.** The retest gate, the dependent fold-in and the
  optional extension diagrams are all withdrawn. No visual confirmation was ever
  obtained and none is recorded: the artifact was rebuilt and removed on
  2026-08-01 without a retest result being reported, and inventing a pass would
  repeat the false-record failure this session already had to correct in D-0037.
- **Submission impact: none.** The shipped DOCX is unchanged and validates; MDPI
  requires figures as a single ZIP at >= 600 dpi, which is built and verified.
  The generators, the drawings and the new validator all remain in the
  repository, so D4 can be revived if a future venue wants editable diagrams.
  **Approver**: author (directed the fix, then removed the artifact).
  **Status**: CLOSED (withdrawn).

## D-0041 (2026-08-01) - D4 Visio OLE: root cause found and FIXED; supersedes the D-0040 withdrawal

- **New fact.** After D-0040 withdrew D4 for want of a retest result, the author
  retested and reported the failure directly: the flowchart still opens as a
  static image in Word. D-0040 recorded that "no visual confirmation was ever
  obtained"; that is now superseded - **the retest was performed on 2026-08-01
  and it FAILED**, reproducing the 2026-07-13 result.
- **Root cause, found by inspecting the generated markup.** A `.vsdx` is an OPC
  **package** (a zip), not a legacy OLE compound-file stream.
  `embed_visio_ole.py` attached it with the relationship type
  `.../relationships/oleObject`, under which Word expects a `.bin` compound
  file; handed a zip it cannot activate the object and silently falls back to
  rendering the preview image alone. That is exactly the reported symptom, and
  it was never an Office configuration problem on the author's machine as
  D-0040 speculated.
- **Fix**: modern Office formats (.vsdx/.docx/.xlsx/.pptx) must use
  `.../relationships/package`. One constant. The `<o:OLEObject>` markup was
  correct throughout (`Type="Embed"`, `ProgID="Visio.Drawing.15"`,
  `DrawAspect="Content"`), as were the preview image, the content types and the
  drawings themselves - which is why every structural check passed while the
  object still would not open.
- **The validator had the same blind spot** and passed the broken package. It
  now fails any OPC-package embed attached with a non-`package` relationship
  type, and the check is negative-tested by rebuilding the pre-fix package and
  confirming it is caught.
- **Lesson**: "structurally valid" and "functionally correct" are different
  claims. Eleven passing structural checks said nothing about whether Word could
  activate the object, and the withdrawal in D-0040 attributed the failure to
  the author's environment rather than looking at the generated relationship
  type. Diagnose before disposing.
- **Status**: D4 **REOPENED and FIXED**, pending one more author check. The
  D-0040 withdrawal is superseded; its reasoning about submission impact still
  holds - the OLE DOCX remains excluded from the package (C-001 5.4), so this
  is an enhancement, not a submission dependency.

## D-0042 (2026-08-01) - D4 Visio OLE round-trip PASSED (author-confirmed); phase closed

- **The gate passed.** The author opened `DT-GSK_visio.docx` in Word,
  double-clicked a flowchart, and confirmed it opens in Microsoft Visio for
  editing. This is the **first pass ever recorded** for this gate.
- **The full arc, for the record.** The acceptance test failed on 2026-07-13
  ("the OLE flowcharts showed as static images in Word") and the gate stayed
  open. On 2026-08-01 it was withdrawn unverified (D-0040) - a disposal without
  a diagnosis, which also speculated that the cause was the author's Office
  configuration. The author then retested and it failed again. Inspecting the
  generated markup found the real cause (D-0041): a `.vsdx` is an OPC package,
  and it was attached with the `oleObject` relationship type, under which Word
  expects a legacy compound-file stream and silently falls back to the preview
  image. Changing one constant to the `package` relationship type fixed it, and
  the author's confirmation closes the loop.
- **What this cost, and the lesson.** Eleven structural checks passed against a
  package that could not be activated, because structural validity and
  functional correctness are different claims. The withdrawal in D-0040 was
  premature: the item should have been diagnosed before it was disposed of, and
  attributing the failure to the author's environment was a guess presented as a
  likely cause. `validate_visio_ole.py` now fails any OPC-package embed carrying
  a non-`package` relationship type, negative-tested against a reconstruction of
  the broken package, so this specific defect cannot recur silently.
- **Fold-in deliberately NOT taken.** With the round-trip confirmed, folding OLE
  into the default build is now a live option. It is not taken: the OLE variant
  is excluded from the submission package (C-001 5.4); MDPI asks for figures as
  a separate >=600 dpi ZIP, which is built and verified; embedding OLE objects
  in the *submitted* DOCX would enlarge it and risk an editor without Visio
  meeting an object they cannot open; and changing the shipped artifact now
  would force another freeze pass for no submission benefit.
- **Disposition: D4 CLOSED - objective met.** The capability works and is
  reproducible from `build_visio_flowcharts.py` + `embed_visio_ole.py`, both in
  the repository with the validator. `DT-GSK_visio.docx` itself is a build
  product, not committed, regenerable in one command.
- **Submission impact: none.** The shipped DOCX is unchanged and validates.
  **Approver**: author (confirmed the round-trip, 2026-08-01). **Status**:
  CLOSED (passed).

## D-0043 (2026-08-01) - Figures 1 and 2 ship as editable Visio OLE; the D-0042 fold-in decision reversed

- **Author directive**: the two flowcharts should be Visio OLE in the
  manuscript. D-0042 had recorded the fold-in as deliberately not taken; that is
  reversed here and the OLE path is now default-on
  (`VISIO_OLE_FLOWCHARTS=0` restores raster pictures).
- **Two of my three stated reasons did not survive measurement**, which is why
  this is a correction and not merely compliance:
  - *"it would enlarge the submitted DOCX"* - the delta is **+9,869 bytes**,
    about 1 percent of a 1 MB file. Not material.
  - *"an editor without Visio would meet an object they cannot open"* - **void**:
    each `<w:object>` retains its PNG preview, so the figures render exactly as
    before for a reader without Visio. The OLE is additive.
  - Only the third stands - MDPI asks for figures as a separate >=600 dpi ZIP,
    which is built and shipped - and that is a reason to ALSO provide the ZIP,
    not a reason to withhold editability from the Word deliverable.
- **A build defect fixed while enabling it**: the opt-in block regenerated the
  tracked `flowchart_*.vsdx` on every DOCX build, rewriting validated artifacts
  as a side effect and producing spurious working-tree diffs. They are now
  regenerated only when absent, and were confirmed untouched across two builds.
- **Validator scope widened**: `validate_visio_ole.py` previously checked only
  the standalone `DT-GSK_visio.docx`, which is a build product and usually
  absent. It now checks the **shipped** `DT-GSK.docx` on every run - both
  embedded drawings byte-identical to their tracked sources, both attached with
  the `package` relationship type (the D-0041 defect), each embedded copy
  re-validated independently.
- **Scope**: exactly one tracked file moves, `papers/DT-GSK.docx`. The PDF, the
  supplement in both formats, the cover letter, `main.tex` and all three CSVs
  are byte-identical to pass-36. Same drawings, now editable.
- **Freeze**: pass-37 minted at anchor 01b6a7f2d (1 of 15 hashes changed),
  check_manifest 15/15. Tag **v2.12** supersedes v2.11.
  **Approver**: author (2026-08-01). **Status**: CLOSED.

## D-0044 (2026-08-01) - Repository made PUBLIC; URL cited in the Data Availability Statement

- **Author decision**, reversing ONE limb of D-0037: the repository at
  https://github.com/MostafaMassoud/DT-GSK is public as of 2026-08-01, and the
  URL is cited in the Data Availability Statement and supplied at submission.
  The other D-0037 limbs stand unchanged: no Zenodo deposit, no repository
  DOI; the article DOI is assigned by *Algorithms* (MDPI) after acceptance.
- **Verified before citing**: an anonymous fetch of the URL renders the
  repository and its README - the DAS does not cite an address the reader
  cannot reach.
- **DAS wording**: openly available at the URL; the submitted version
  corresponds to repository tag v2.13 (cut at this mint, so the pointer is
  self-consistent); further materials from the corresponding author on
  reasonable request. The URL is the single archival identifier permitted in
  the statement (review instrument 10.17.4).
- **Consistency sweep in the same anchor commit** - every statement written
  under the superseded limb was corrected: README ("no public artifact
  repository accompanies the article" - now false, replaced), the
  reproduction-pack cover note and its emitted manifest, the
  presentation-conventions adopted posture, and the review instrument's
  archive-of-record definition. The submission kit gained the
  availability-URL field.
- **What a public repository now exposes, stated plainly**: the full
  governance record, including the AI-assisted commit trailers, the production
  prompt files, and the disclosure amendments. All of it was audited for
  exactly this exposure (the 2026-08-01 transparency audit and its
  remediation), the manuscript's disclosure covers the facts, and the
  commit-boundary evidence (no AI-assisted commit touches
  benchmarks/cec_reference_results/ or papers/analysis/) is itself part of
  what the repository now makes checkable by anyone.
- **Freeze**: pass-38 minted at anchor d12989add (3 of 15 hashes changed),
  check_manifest 15/15. Tag **v2.13** supersedes v2.12; earlier tags unmoved;
  CITATION.cff bumped to 2.13 in the tagged state.
  **Approver**: author (2026-08-01). **Status**: CLOSED.

## D-0045 (2026-08-01) - SUBMITTED to Algorithms (MDPI); status "Pending editor decision"

- **The manuscript was submitted** through the MDPI SuSy portal on 2026-08-01
  by the corresponding author. Portal status as reported: **Pending editor
  decision**.
- **Manuscript ID**: **algorithms-4507562** (supplied by the author 2026-08-01;
  placeholder filled). Section: *Evolutionary Algorithms and Machine
  Learning*. Submission date as recorded by the portal: 2026-08-01.
- **STATUS PROGRESSION**: "Pending editor decision" -> **"Under review"**
  (observed 2026-08-01). The manuscript therefore cleared the editorial
  desk gate - the handling editor judged it in scope and complete, and sent
  it to peer reviewers rather than desk-rejecting or returning it. No
  reviewer report has been received at the time of this entry.
- **What was submitted** (LaTeX submission; the Word deliverables were
  deliberately NOT uploaded, since the DOCX is a pandoc companion whose layout
  differs from the canonical PDF):
  - `papers/submission/DT-GSK-latex-source.zip` - collated sources, verified to
    recompile in a clean room to a PDF byte-identical to the shipped one, and
    carrying that PDF inside it;
  - `papers/DT-GSK.pdf` (47 pp), `papers/supplementary.pdf` (75 pp),
    `papers/cover_letter.pdf` (2 pp);
  - `papers/submission/DT-GSK-figures-600dpi.zip` - 7 figures, 600 dpi PNG.
- **Frozen basis**: freeze pass-38, tag **v2.13**, repository anchor b51590790. The
  five deliverables are hash-recorded in
  `papers/governance/submission_package_manifest.json` at that tag; that record
  is the authoritative statement of exactly what was uploaded.
- **Form/manuscript consistency**, the D16.5 obligation: the portal's GenAI
  declaration named both assistants, matching the manuscript's four disclosure
  loci; the conflicts-of-interest field restated the manuscript's COI; the
  data-availability field carried the public repository URL and the v2.13 tag,
  matching the Data Availability Statement (D-0044). Open peer-review was
  elected. No external funding was declared, matching AG-0003.
- **Author biographies**: the corresponding author's is entered; the two
  co-author biographies were deliberately left for those authors to supply,
  and are due before acceptance rather than before submission.
- **STANDING INSTRUCTION from this point**: do NOT rebuild or re-mint anything.
  v2.13 is the frozen record of what was submitted, and any post-submission
  change would break the correspondence between the repository and the file
  under review. A revision request, if one comes, is handled as a new freeze
  pass through change control - never as an edit to the submitted state.
  **Status**: OPEN (awaiting editorial decision).

## D-0046 (2026-08-04) - Preprint submitted to Preprints.org (ID 226790)

- **Preprint ID 226790**, type Article, submission received 2026-08-04. Title
  and author list identical to the journal submission; author emails as
  recorded in the manuscript byline. Subject category: Computer Science and
  Mathematics / Artificial Intelligence and Machine Learning, chosen to match
  the journal section (*Evolutionary Algorithms and Machine Learning*) rather
  than the more generic Applied Mathematics.
- **What it snapshots**: the manuscript as submitted to *Algorithms*
  (algorithms-4507562), i.e. freeze pass-38 / tag **v2.13**. The preprint is
  therefore a PRE-REVIEW snapshot; if peer review produces revisions, the
  posted version does not change unless a new version is posted deliberately.
- **Separate publication act, deliberately logged as one.** Posting a preprint
  is not a by-product of journal submission: it publishes the work under
  CC BY 4.0, permanently, and the platform states that preprints cannot be
  fully removed once announced and assigned a DOI - only marked with a
  withdrawal notice, with title, authors and abstract remaining visible. The
  author was advised of this before the record was filed.
- **Consistency with the rest of the record**: the preprint carries the same
  Data Availability Statement (public repository + tag v2.13, D-0044) and the
  same Use-of-Generative-AI disclosure naming both assistants, so the preprint,
  the journal submission and the public repository state one story.
- **No manuscript change**: nothing in the frozen package was touched to
  produce the preprint; v2.13 remains the single basis for both the journal
  submission and this posting. check_manifest 15/15.
- **WITHDRAWN 2026-08-04, same day.** The author located and used the
  platform's own withdraw option, acting inside the pre-announcement
  screening window - the only interval in which a Preprints.org submission
  can be taken down cleanly, since after announcement and DOI registration
  the platform states a preprint cannot be fully removed and receives only a
  withdrawal notice with its metadata still visible. No DOI had been issued.
- **Net effect**: no preprint of this work is published. The manuscript's
  only public routes remain the journal submission under review
  (algorithms-4507562) and the public repository cited in the Data
  Availability Statement (D-0044). Nothing in the manuscript, the frozen
  package, or the repository referred to a preprint, so no text required
  correction and no re-mint was triggered.
  **Status**: CLOSED (posted and withdrawn same day; no publication).

## D-0047 (2026-08-25) - Journal peer review received: MAJOR REVISION; revision opened as pass-39

- **Supersedes the standing state recorded in D-0045.** That entry closed with
  the submission under review and the instruction not to rebuild or re-mint the
  submitted package. The review has now arrived, so that hold is lifted for the
  revision line only: v2.13 / pass-38 remains frozen history and is never edited
  in place, and all revision work proceeds as a new freeze pass (pass-39, tag
  v2.14) through change control, exactly as D-0045 prescribed.
- **Decision received 2026-08-24**: MAJOR REVISION on algorithms-4507562, two
  reviewers, neither recommending rejection. The reports are NOT kept in this
  repository (D-0049): both reviewers declined to sign, and republishing a
  confidential report is the journal's act at acceptance rather than the
  authors' mid-revision. A verbatim record is retained on disk and, in git, only
  on the never-pushed archive branch; before it existed the only copy of
  Reviewer 1's report was outside version control and Reviewer 2's text existed
  nowhere.
- **Ten distinct points** (R1.1-R1.4, R2.1-R2.7), of which R1.3 and R2.2 are the
  same objection raised independently by both reviewers. Six close with zero
  optimizer runs; four require new experiments totalling ~32,000 runs. Reviewer 2
  flags three for particular emphasis: the uniform-versus-tiered ablation (R2.1),
  population-size control (R2.2), and eigenframe isolation (R2.3).
- **The experiments cannot be declined.** The manuscript concedes in its own
  words that two of them were never run: `sections/proposed_algorithm.tex:166`
  states that "a common-$NP$ replication is identified as future work", and the
  same section records that the tiering is not isolated by a controlled
  uniform-versus-tiered contrast. No rebuttal posture is available on R2.1 or
  R2.2 other than running them.
- **Scope decision on R2.6 (external validation).** The reviewer offered two
  options; the author elects the second - all claims stay explicitly restricted
  to the GSK-family panel. No external algorithm enters the panel, and no
  manuscript edit is required: the restriction is already stated in six places
  (`main.tex:180`, `introduction.tex:89`, `performance.tex:889` and `:1239`,
  `conclusions.tex:110`, `supplementary.tex:1376`). This decision leaves D-0025
  and CR-0019(c) standing rather than reversing them; the exploratory first-party
  non-GSK LSGO banks in the public repository remain unpromoted. A one-sentence
  disclosure of their existence in S7 is recommended but optional, and D-0048 is
  reserved should the scope decision ever be revisited.
- **Title decision (R1.2).** Reviewer 1's second suggested phrasing is adopted:
  "DT-GSK: Dimension-Tiered Adaptive Configuration Selection and Deterministic
  Refinement for Gaining-Sharing Knowledge Optimization". His alternative
  "Operator-State Adaptation" is declined with a stated reason - the tiering keys
  on problem dimension, resolved before the run begins, not on operator state.
  The retained second half preserves contribution C1, which both of the
  reviewer's own proposals dropped. Not yet applied; propagation covers 32 sites.
- **R1.4 APPLIED (this entry's only executed change).** All seven component-study
  omnibus values now report the Iman-Davenport F on the tie-corrected Friedman
  statistic, the convention the main text already used for the primary suites
  (M-026 / D-0016). S6.5: 2.4e-3 -> 1.5e-3, 5.2e-3 -> 3.6e-3, 3.8e-3 -> 1.0e-3.
  Scaffold exhibits SA01/SA02: 1.8e-6 -> 9.8e-9, 2.5e-8 -> 1.2e-10, 5.8e-3 ->
  3.8e-3, 3.5e-2 -> 2.7e-2. Direction is bounded a priori: because the
  tie-correction factor C <= 1 the correction can only increase the statistic, so
  every p-value decreases and no ranking, sign, or Holm decision changes anywhere.
  The historical chi-square values are retained as audit companions in the
  released contrasts JSONs, per the D-0016 precedent. The Holm-corrected paired
  Wilcoxon results that carry the S6.5 findings (Table A25: ISM null 0.983 /
  0.897 / 0.647; polish 0.002 / 0.005 / 0.002) are unaffected by the omnibus
  convention and are byte-identical after the change.
  **The sharper p-values must not be used to strengthen any frozen claim.**
- **Two defects found and fixed while applying R1.4.** (a) A third exhibit,
  `papers/tables/SA02.tex`, reprinted the same four uncorrected values in its
  per-dimension headers and had not been identified in the review; it regenerates
  from the same run. (b) `regen_cec2017_contrasts.py` and
  `promote_cec2017_overlay.py` wrote the ablation manifest as `indent=1` with no
  trailing newline while the file on disk is `indent=2` with one, so either script
  reformatted all ~30 KB on every run and buried the real change. Both writers now
  match the canonical mint serialization; the manifest diff is eight lines.
- **Gate state after the R1.4 change**: `check_frozen_analysis` 115/115
  byte-identical (primary release rel-2026-07-20-67d9345f9 untouched); the
  ablation release self-check reports all 1297 tracked checksums matching disk;
  `check_manifest` 14/15 with only `supplementary.pdf` outstanding, which is
  expected until the pass-39 re-mint; `validate_evidence_bindings`,
  `validate_artifact_labels`, `validate_build_hygiene` and `audit_manuscript` all
  exit 0, with `blocked_wording_hits` unchanged at 2 (pre-existing at HEAD).
- **Note on `check_manifest --manifest`**: it selects its base directory from a
  manifest's `evidence_root` key. The ablation manifest declares none, so the gate
  resolves every path against the repo root and prints "0/1297 match". This is a
  usage artifact, not corruption; the authoritative check is the self-check that
  `regen_cec2017_contrasts.py` prints at the end of its run.
- **Documentation**: three root Markdown files misstated project status and would
  have misled a resuming reader - `FINAL_RELEASE_REPORT.md` closed on "PUBLISH
  READY", `README.md` twice said "not yet peer-reviewed", and `docs/index.md`
  carried a 2026-07-20 pre-submission status block. All three are corrected.
  `CLAUDE.md` and `REVISION_STATUS.md` are added at the author's explicit request
  as the session entry point and the single current-state record; PROJECT_RULES
  2.6, SKILL.md 14 and the README tree are updated from eleven root Markdown
  files to thirteen.
- **Change request**: CR-0023 (sub-items a-f). **Open**: seven author decisions,
  the revision deadline foremost, and the four experiments. `main.tex:156`
  ("eigenframe refinement") is held pending the E1 outcome.
  **Status**: DISCHARGED (updated 2026-08-27). The revision completed: all four
  experiments ran, R1.4 is applied and committed, and `main.tex:156` was resolved
  by the E1 outcome - the abstract now reads "budget-exact final refinement" and
  contribution C1 is claimed basis-neutrally. Of the seven author decisions the
  entry lists, the deadline stopped gating when the campaign completed; the only
  survivor is the SuSy resubmission, tracked in REVISION_STATUS.md section 5.

## D-0048 (2026-08-26) - Round-one revision experiments closed: two submitted claims falsified, both accepted

- **The four reviewer-requested experiments are complete.** Pre-registered
  2026-08-25 in `papers/review_2026_08_24/revision_experiments_preregistration.md`
  before any result existed, executed 2026-08-26 (31 legs, 32,451 optimizer runs,
  22.19 h, zero failures), promoted read-only as evidence release
  `rev-rel-2026-08-26-dd42d37eb`, and written into Supplementary Section S9 as
  Tables A43-A46. The registration fixed the hypotheses, the Holm family
  structure per experiment, the reporting convention, and the manuscript wording
  for each possible outcome INCLUDING the outcomes adverse to the paper. Two
  outcomes were adverse; the registered adverse-branch wording was applied
  unmodified.
- **E1 (R2.3, refinement basis) falsified the value of the learned eigenbasis.**
  Three arms at fixed enablement under one budget: eigenframe (the frozen leg),
  coordinate axes (the new arm, 2,958 runs), no refinement (the existing
  component-isolation overlay). The deterministic endgame is vindicated - it
  beats no refinement at D = 50 (22/2/5) and D = 100 (23/1/5), and the
  coordinate variant beats no refinement 28/1/0 and 25/1/3. The BASIS is not:
  the plain coordinate axes outperform the learned eigenframe at D = 50 on 25 of
  29 functions (Holm 1.4e-4) and are not separated from it at D = 100 (0.0543).
  There is no dimension at which the eigenbasis wins.
  **Decision: contribution C1 is renamed "a deterministic final polish" and is
  claimed basis-neutrally.** The eigenbasis is RETAINED in the method and
  reported as a specified, reproducible negative result rather than removed - a
  documented harmful component with its evidence attached is more useful than a
  quiet deletion. The mechanism description is unchanged throughout: DT-GSK does
  compute an eigenbasis, and E1 falsified its value, not its existence. The C1
  bullet's submitted caveat that the basis question "remains open" is replaced by
  the result, because leaving it would now be false.
- **E3 (R2.1, tiered vs tier-constant) found the mid-dimension tier
  mis-specified.** Two tier-constant transplants against the shipped tiered
  configuration, all four dimensions, 11,832 runs. Tiering is supported against
  the high-dimension transplant at D = 10 (22/4/3, Holm 0.006) and D = 50
  (19/0/10, 0.0284). But at D = 30 the parameter set DT-GSK resolves at D = 10
  outperforms the set it ships, on 20 of 29 functions (0.0055).
  **Decision: contribution C2 is narrowed to the dimensions where tiering was
  demonstrated, and the 20 <= D < 50 tier is disclosed as mis-specified in the
  Conclusions.** Which configuration key carries the effect is NOT resolved and
  is left explicitly open; E3 licenses only per-dimension statements about the
  tiered configuration as a whole, and no cell is attributed to any subsystem.
  This also explains a weakness the submitted paper could only describe: D = 30
  was already where DT-GSK sits second behind eGSK.
- **E2 (R1.3/R2.2, matched population) left the standing intact but not
  unqualified.** At the comparators' NP = 100, DT-GSK is first at D = 10 and
  second at D = 30, 50 and 100 - top two everywhere. The paired difference is
  null at D = 10 and D = 30 (0.517) and significant at D = 50 (0.0064) and
  D = 100 (0.0051), where holding NP at the panel constant costs first place.
  **Decision: the D = 50 and D = 100 rank claims are qualified as resting in
  part on the population rule, wherever they appear.** E2 is reported as an
  ablation of a declared method component, NOT as a correction to a
  mis-specified baseline, and the paper's headline results are not restated at
  NP = 100 - doing so would ablate a component of the contribution and then
  present the ablated method as the contribution.
- **E4 (R2.7, sensitivity) is exploratory and stays that way.** 27 cells, seven
  constants, two levels, D = 30 and D = 100, 15 repetitions per cell. Descriptive
  only: no hypothesis test and no corrected p-value appears in its table or its
  text. 26 of 27 cells leave the panel ordinal unchanged, median error ratios
  span 0.982-1.016, and the single flip is favourable (raising the population
  floor by one at D = 30 moves DT-GSK from second to first). Registration
  amendment A1 is disclosed rather than smoothed: three real-valued constants at
  D = 100 executed levels larger than the registered twenty per cent and
  one-sided, those rows are flagged, and the table prints the levels actually
  executed.
- **Two revision-track corrections found by reading the built PDF.** (a)
  `sections/introduction.tex` still labelled C1 "the eigenframe final polish
  (C1)" in two places, including the closing list of the three principal
  contributions, after the earlier pass renamed only the contribution bullet.
  (b) The cover letter, which `build_submission_bundle.py` ships inside the
  submission package, still carried C1 as an "eigenframe final polish" and the
  basis question as "unresolved". Because an earlier pass had already retitled
  that letter in place, it is the letter that travels with the current version
  rather than a round-1 artifact, so it is converted to revision-1 form. CL-02's
  scientific core and the GenAI disclosure sentence are untouched.
- **Response letter**: `papers/review_2026_08_24/response_to_reviewers.md`,
  point-by-point over all ten reviewer ids, quoting each reviewer sentence from
  the verbatim record and printing every number in the same notation its exhibit
  uses.
- **Evidence integrity**: the PRIMARY release is untouched - `check_frozen_analysis`
  reports 115/115 files byte-identical against `rel-2026-07-20-67d9345f9`, and the
  revision release is additive and non-superseding. Seed pairing was verified by
  seed identity before any statistic was computed (zero mismatches across E1-E4),
  and eleven fail-closed known-answer pins reproduce in the analysis bundle.
- **Change requests**: CR-0023 CLOSED; CR-0024 raised and closed for the
  experiment track and its write-up. **Freeze pass-40 minted**, anchor
  `77f9bc0`, `check_manifest` 15/15. The v2.14 tag hold set by the author on
  2026-08-25 is satisfied - the four experiments are complete, integrated and
  validated - and the tag is cut from this pass.
  **Status**: CLOSED (revision complete; awaiting the author's SuSy resubmission).

## D-0049 (2026-08-27) - What the public repository publishes, and what it withholds

- **Context.** The repository is public and is named in the Data Availability
  Statement, so what it contains is part of the paper's evidentiary claim. An
  audit before publishing the round-one revision found four categories of
  material that must not be in it, one of them already live.
- **Copyrighted third-party PDFs, already public and now removed.** Seven PDFs
  totalling 38.8 MiB - the APA Publication Manual 7th edition, four IEEE
  publishing documents, the Manchester Academic Phrasebank and a USC libguide -
  were added in commit b9846e4 and served publicly from 2026-08-07. The cause is
  mechanical and worth recording: `.gitignore` carried
  `reference_papers/*.pdf`, a SINGLE-LEVEL glob that cannot cross a `/`, so it
  never matched `reference_papers/Academic_Research_Guidelines/` and the
  intended exclusion silently failed from the root commit onward. The glob is
  repaired with a recursive form alongside it. Because b9846e4 changes ONLY
  those eight files and its parent is clean, removal is a REWIND to an
  already-public ancestor, not a history rewrite: no existing commit SHA
  changes, and tag v2.13 - which the submitted manuscript's DAS names - is an
  ancestor of the rewind target and never carried the PDFs.
- **Confidential peer review, withheld.** Both round-one reviewers declined to
  sign. Their reports, and the point-by-point response that reproduces both
  verbatim, are retained locally and untracked. Republishing a confidential
  report is the journal's act at acceptance, in the journal's own form; doing it
  unilaterally mid-revision is a different act on a different consent basis.
  Withholding needs no permission. Reviewer 1's report additionally has no text
  layer - every stream is vector glyph outlines - so it could not be redacted,
  only re-rendered, and re-rendering cannot remove its typographic and timezone
  fingerprint without destroying the artifact.
- **The pre-registration IS published**, deliberately, at
  `papers/review_2026_08_24/revision_experiments_preregistration.md`. It is
  wholly the authors' own document, quotes no reviewer, and carries no date,
  timestamp, report id, score or pronoun. The Supplementary Materials ask
  readers to accept that the manuscript wording for every possible outcome -
  including the two adverse outcomes that occurred - was fixed before any result
  existed. That is uncheckable unless the document is public, and it is the
  claim the revision's honesty rests on.
- **Co-author material, withheld.** `papers/submission/AUTHOR_DATA_HANDOFF.md`
  was public from 2026-08-07. It carries two biographies marked in the file
  itself as "AWAITING HER APPROVAL" and "AWAITING HIS APPROVAL", against the
  file's own rule "ask, do not draft-and-paste", plus privately-supplied
  addresses. It is withheld and the rewind removes it from the public tip. The
  co-authors should be told it was public.
- **Campaign staging output, withheld.** `results/_revision/` duplicates the
  promoted, manifest-hashed release and adds console logs. The promoted release
  is the citable evidence and is published in full.
- **Provenance paths corrected in the revision release.** 61 files in
  `benchmarks/cec_reference_results/_revision/` recorded `data_root`,
  `reference_root`, `output_dir`, `generated_dir` and the driver's `--root`
  argument as ABSOLUTE local paths, against every previously published release,
  which records them relative to the repository root. The campaign driver passed
  relative roots and the runner resolved them before writing provenance. The
  prefix is stripped, the manifest re-minted (61 of 252 entries moved), and the
  correction recorded in the manifest's own `correction` field. No result,
  statistic, seed or checkpoint is affected; the `computer` field is left alone
  because it already appears in the published releases. This was done BEFORE
  first publication, so no external copy of the superseded bytes exists. The
  read-only guard on the release tree was cleared per file for one write each
  and restored; the tree ends as protected as it started.
- **A falsified integrity claim in the public README, corrected.** The
  AI-transparency paragraph asserted that no commit carrying an AI co-authorship
  trailer modifies any file under `benchmarks/cec_reference_results/` or
  `papers/analysis/`. Four such commits now do, one of them the 259-file
  promotion of the revision release; the claim was verifiable as false in two
  commands. Its spirit held - no AI produced data or computed a statistic - but
  a falsified integrity claim in a paper whose third contribution IS evidence
  integrity is the worst possible defect to ship. It now states what is true and
  gate-backed: no trailered commit touches the four hash-gated optimizer
  modules, which `validate_provenance_claims.py` enforces by hash; two touch
  other optimizer files and both are documentation-only; trailered commits do
  appear under the evidence and analysis trees and every one is a promotion or a
  re-derivation, byte-verified against staging before its manifest was minted.
- **Publication mechanism.** One squashed commit on the rewound public branch,
  carrying the audited tree. The 26-commit development history is retained
  locally on `archive/revision-pass-39-full` *(since 2026-08-28: in the private
  bundle kept outside the repository (location in the withheld `papers/review_2026_08_24/PRIVATE_OPS.md`), the branch itself bundled,
  restore-tested and deleted — the retention and the never-publish rule are
  unchanged, only the container moved)* and is NOT published: ten of its
  commit messages characterise a reviewer who declined to sign, including with
  gendered pronouns that were never established, and several intermediate trees
  carry a verbatim reviewer sentence the published tree redacts. Squashing
  removes all three disclosure routes by construction rather than by a
  per-commit scrub whose failure mode is silent.
- **The local v2.14 tag must never be pushed.** Its tree contains all seven
  copyrighted PDFs and both reviewer reports. It is superseded by a tag cut on
  the published commit.
  **Status**: PARTLY DISCHARGED (updated 2026-08-27). The rewind, the push and
  the tag were taken: `v2.14` was cut on the published commit `02d1791` and
  `v2.15` on `ebcdefe` at pass-42, and the never-push local tag it warns about
  is superseded. **The GitHub Support purge request is CLOSED by author decision
  (2026-08-28): it will not be filed.** Deferred on 2026-08-27 and closed the
  following day. It is closed, not discharged - the objects were still served when
  the decision was taken, and nothing about them changes on its own. It covers TWO
  unreachable commits rather than
  one - `b9846e4`, the seven copyrighted PDFs at 38.8 MiB, and its parent
  `bddfe24`, which carries `AUTHOR_DATA_HANDOFF.md` and so the co-authors'
  biographical data. Both are off every ref and both are still served by direct
  SHA: HTTP 206 re-verified 2026-08-27, with the web UI still rendering the tree
  at HTTP 200. Purging only the child would leave the parent serving the personal
  data. The request would succeed if filed - 0 forks, network_count 0 and 0 pull
  requests, so no fork network holds a competing reference.
  **The deferral was taken on a corrected premise.** It was first proposed on the
  belief that the exposure ends on 2026-09-10; that date belongs to the Traffic
  clone counter, which is separately discharged. Unreachable objects carry **no
  expiry date** - GitHub collects on an unannounced schedule with no guarantee -
  so this does not lapse on its own. The author was told so and reaffirmed the
  deferral: the material needs an exact 40-character SHA to reach, the repository
  drew 2 web views in 14 days, and the 2026-09-01 resubmission has priority.
  **Parked, not closed. Do not re-raise it as urgent; do not treat it as done.**
  Full SHAs, the ready-to-send request and the post-purge check:
  `docs/development/github_exposure_traffic_record.md`.
  **The co-authors were told their biographies had been public** (author,
  2026-08-27), discharging the obligation recorded in the co-author limb above;
  `AUTHOR_DATA_HANDOFF.md` remains withheld. **The traffic record is captured**
  (author, 2026-08-27), discharging the expiring limb: 11 clones from 9 unique
  cloners over 08/13-08/26, every one of those 14 days inside the exposure
  window, against 2 web views. The window itself is now dated from the reflog -
  `b9846e4` was the tip of `main` from 2026-08-07 23:45:59 +0300 until the reset
  at 2026-08-27 01:17:02 +0300. Six days of it, 08/07 to 08/12, had already
  rolled off GitHub's 14-day counter before the capture and are permanently
  unmeasured, so those counts are floors and not estimates. Transcription and
  what the counts do not establish (they identify nobody, and do not separate
  automated from human traffic):
  `docs/development/github_exposure_traffic_record.md`. **The remediation limb of
  this decision is therefore closed unfiled. Do not re-raise it as outstanding
  work.** The record is kept rather than deleted because the material is not the
  author's alone - seven third-party copyrighted PDFs and a co-author's
  biographical data - and a considered-and-declined remediation is worth more on
  the record than no trace of one.


## D-0050 (2026-08-27) - Pass-42: correct the published revision before resubmitting

- **Decision.** Apply the nine adjudicated corrections to the published round-one
  revision as an ordinary change-control pass, mint freeze **pass-42**, and cut
  tag **v2.15**, rather than either shipping the defects or deferring them to a
  post-resubmission correction. Registered as **CR-0025**.
- **Why now.** "Published" meant the public repository, not the journal. The
  revision had not been resubmitted through SuSy and the Preprints.org posting
  was withdrawn the same day (D-0046), so every defect was still correctable in
  the version the reviewers will actually read, at the cost of one pass. That
  window closes at resubmission, after which the same edits become a correction
  to a manuscript already under the editor's eye.
- **What was NOT done, deliberately.** C4 is REFUTED and is not edited: its
  proposed fix would have retargeted a sentence at a matched-population
  aggregate that appears nowhere in the shipped record, on a bind-tagged
  paragraph - converting a self-resolving ambiguity into an unsupported
  thin-margin assertion. Contribution **C3 is not narrowed**. The bound claim at
  `supplementary.tex:1254-1267`, that the CR-0013..CR-0018 edits were certified
  bit-identical with zero divergence, is **left standing and flagged**: Table
  A45's D = 100 row is a counterexample to it.
  **Status**: SUPERSEDED by D-0051 (2026-08-27). Two parts of this bullet as
  first written are now withdrawn. (1) The claim that the certification chain
  has "exactly one hole - CR-0015 ... but never cec2017 D100" is **REFUTED**:
  CR-0014 certifies cec2017 D100, CR-0016 certifies cec2017 D10/D50/D100, and
  CR-0018 certifies an eighty-four-cell ledger that includes that cell
  bit-for-bit. A referee following the pointer would find it certified three
  ways, so the disclosure this bullet contemplated was drafted, challenged and
  rejected. (2) The residual itself is no longer unexplained: a pinned
  re-execution under the current build reproduces the transplant arm on all 26
  divergent cells and the archive on none, so the difference is **between
  builds**, demonstrated. What survives is narrower and is recorded in D-0051:
  the campaign's identity evidence samples about one run per (algorithm, suite,
  dimension), so a divergence at this rate sits below its resolution - those
  certifications are underpowered for this question, not wrong. **No paragraph
  edit is owed**; pass-43 reconciled the Supplementary with the response letter
  and that is the whole of what was required.
- **The residual is reported, not explained.** The D = 100 identity control
  prints 2/25/2 and 27 of 1479 run cells differ. Configuration (108/108 resolved
  keys), pairing (seed, nfes and termination on all 1479), threading (both
  drivers pin the numeric stack to one thread) and telemetry are all excluded.
  The two legs are different builds and the earlier one is unrecoverable, so the
  cause is narrowed but NOT established. The caption states the residual and
  asserts no cause.
- **Determinism was tested rather than asserted.** The byte-stability regression
  covered only D <= 30 - below the tier where the interaction graph activates -
  which CR-0007 already recorded as how the C006 defect reached a release. A new
  regression at D = 50 and D = 100 asserts repeat-identity on both
  `best_fitness` and the full `best_x`, guards that the memory and the polish
  are actually enabled at each cell, and was negative-tested. It deliberately
  pins no golden values: at D >= 50 the value follows the BLAS reduction order,
  and one cell was observed at three different values under one thread, eight
  threads and inherited settings, while repeat-identity holds at any fixed
  thread count.
- **A shipped artifact was nearly missed.** The freeze manifest hashes
  `cover_letter.pdf` but not `cover_letter.tex`, so editing the source left the
  render matching its recorded hash while still carrying a retracted phrasing.
  The cover letter ships to the editor. It was caught only when the manifest
  listed which of the fifteen files had moved, and is rebuilt here.
- **Publication differs from pass-41.** This pass was made directly on `main`,
  which already carries only publishable history, so no squash was required and
  no development line was discarded. `anchor_commit` therefore DOES resolve in
  the published history and equals `published_commit`; the pass-41 disclosure
  that it does not resolve remains true of pass-41 and every earlier pass.
- **Anchor.** `4a2291bd6c718e92f5cb39f3329db424562fc64b`.

## D-0051 (2026-08-27) - Pass-43: make the package agree with itself

- **Decision.** Correct one sentence in the Supplementary Material so that it no
  longer contradicts the response letter that ships beside it, mint freeze
  **pass-43**, and cut tag **v2.16**. Registered as **CR-0026**.
- **The defect was package-level, not page-level.** Pass-42 had already made the
  Table A45 caption honest, and the response letter states plainly that the
  D = 100 internal control does not hold and that the residual is unexplained.
  What remained was `supplementary.tex`, 2,500 lines away from that table,
  asserting that no reported number depends on which revision of the optimizer
  source is used. Shipping the letter and the manuscript together would have
  submitted a package in which one document concedes what the other denies. The
  Supplementary now records the exception, points at the table whose caption
  already reports it as unresolved, and bounds it: the archived release from
  which every reported number derives is itself unchanged.
- **A larger disclosure was drafted and REJECTED on challenge. Do not revive
  it.** It would have named CR-0015 as the one bit-identity certification whose
  evidence does not span cec2017 D = 100. That is refutable from the register it
  cites: **CR-0014 certifies cec2017 D100, CR-0016 certifies cec2017
  D10/D50/D100, and CR-0018 certifies an eighty-four-cell ledger that includes
  cec2017 D100 bit-for-bit.** A referee following the pointer would find the
  cell certified three ways. The draft also asserted the divergence was
  "confined to the tier at which the interaction-structure memory and the
  deterministic final polish are active" while disclaiming any cause in the next
  clause - naming a mechanism, and locating it at contribution C1, on no
  evidence: there is no identity control at D = 50 at all, and the repository's
  own thread probe found D = 50 invariant and D = 100 not. **The standing rule
  holds: state the gap, never the causation.**
- **What the certifications actually cannot do, recorded here and claimed
  nowhere.** The campaign's bit-identity evidence samples on the order of one
  run per (algorithm, suite, dimension). A divergence affecting 27 of 1479 run
  cells is below that resolution. The certifications are therefore not wrong;
  they are underpowered for this question. This is stated in the governance
  record rather than in the manuscript, because asserting it in the paper would
  impeach every bit-identity certification in the campaign on the strength of a
  single uncontrolled cross-build comparison. **Status**: ANSWERED 2026-08-27 by
  the re-execution this entry called for.
- **The re-execution, and what it settles.** The five functions carrying the
  divergence (F7, F13, F14, F20, F30) were re-run at CEC2017 D = 100, 51 runs
  each, under the CURRENT build with the numeric stack pinned to one thread as
  `run_campaign.py::pinned_env` does, into `results/_g1_recheck/` (diagnostic
  staging, gitignored, never promoted). 255 cells, **zero seed mismatches**
  against both archived legs. Result, on `best_fitness`: **on the 26 cells where
  the archive and the transplant arm differ, the fresh run reproduces the
  TRANSPLANT ARM on all 26 and the archive on none; on the 229 cells where they
  agree, it reproduces both on all 229 and differs on none.** The current build
  therefore produces the transplant arm's values wherever the two legs disagree,
  and the archive is what the earlier build produced. **The difference is
  between builds, not within one** - inferred by D-0050 and this entry, now
  demonstrated.
- **Method note, so the check is repeatable and not accidentally invalidated.**
  Thread pinning is load-bearing: `run.py` does not pin, only `run_campaign.py`
  does, and D = 100 is thread-sensitive - one cell was observed at three
  different values under one thread, eight threads and inherited settings. And a
  control drawn from the cells where the two legs already AGREE proves nothing
  about which build is which; an early reading of this experiment went wrong for
  exactly that reason. The discriminating cells are the ones where they differ.
- **Independently replicated the same day, and it establishes something extra.**
  The author re-ran the identical command in a separate shell and process and
  obtained the identical verdict: 255 of 255 cells, zero seed mismatches, 26 of
  26 divergent cells matching the transplant arm and none matching the archive,
  229 of 229 agreeing cells matching both. Because both executions matched the
  same fixed reference values on every cell, the two runs produced **byte-
  identical results across separate processes and shells**. That is a stronger
  statement of the determinism claim than the D >= 50 regression test makes:
  `tests/regression/test_dt_gsk_byte_stable_high_dim.py` asserts repeat-identity
  **within one process**, whereas this is repeat-identity **across processes**
  at D = 100 with the numeric stack pinned - which is the form a referee would
  actually check. It is recorded here rather than claimed in the paper, for the
  same reason as everything else in this entry: the run is diagnostic staging,
  not a promoted release.
- **No manuscript change follows, and that is deliberate.** The Supplementary
  already states that the control "re-executes, under the current revision, runs
  archived under the earlier one; it does not reproduce them exactly", and the
  Table A45 caption reports the residual as unresolved *in the paper*. Both stay
  true, and are now evidenced rather than asserted. Stating the stronger claim
  in the manuscript would require **promoting this diagnostic as cited
  evidence** - a new release id, manifest and binding - because every reported
  number is bound to a promoted release and staging is never cited.
  **CLOSED by author decision (2026-08-28): the promotion will not be done.**
  This previously read that the option was available to the author and not taken
  here, which leaves it looking like pending work. It is not pending. The
  diagnostic stays diagnostic: `results/_g1_recheck/` remains gitignored staging,
  it is cited nowhere, and no release id, manifest or binding will be minted for
  it. Nothing is lost by that - the finding it supports is recorded in full in
  this entry, and the two manuscript statements it would have strengthened are
  already true and already shipped. **Do not re-raise this as outstanding work,
  and do not promote the run without the author asking for it.**
- **The blind spot that pass-42 fell into is now gated.** The freeze manifest
  hashes renders but hashed only one of their sources: `main.tex` was tracked,
  `supplementary.tex` and `cover_letter.tex` were not. Editing
  `cover_letter.tex` without rebuilding therefore left `cover_letter.pdf`
  matching its recorded digest, and the gate stayed green while the letter that
  ships to the editor still carried a retracted phrasing. The manifest now
  carries a `source_files` list which `check_manifest.py` verifies and reports
  on its own line, so the tracked-file count and every recorded "15/15" stay
  true. Negative-tested: perturbing a source with its render untouched leaves
  `files` at 15/15 and takes `sources` to 1/2, and the gate exits 1.
- **Anchor.** `ae4d4e76eb27a4e5955ab26818204951e26b0c9d`.

## D-0052 (2026-08-27) - Pass-44: the last three wording items, two relocated by challenge

- **Decision.** Carry the three remaining optional wording items before
  resubmission, mint freeze **pass-44**, cut tag **v2.17**. Registered as
  **CR-0027**. Taken as ONE pass, not three: every manuscript pass forces a tag
  bump that drags `CITATION.cff`, `SUBMISSION_KIT.md` and
  `submission_package_manifest.json` with it.
- **Two of the three were relocated on challenge, and the relocations are the
  point.** The Table A44 caption edit was **dropped**: the body seventeen lines
  below it already says Friedman ranks are relative *and* carries the
  differencing prohibition, so the caption would have duplicated its own page.
  The real hole was Table A46 - grepping every differencing mention in the
  supplement shows the document's **only** such prohibition sits at `:3760`,
  attached to A44 alone. A46's caption now carries the bar rather than the
  premise.
- **The A12 qualifier moved from the prose to the definition.** Adding "mean" at
  `:2280` would have qualified three of the **six** values that one paragraph
  draws from the same column, while a clause two lines earlier calls that column
  "the raw-run effect size" - asserting two conventions where there is one. The
  subsection now declares once, at `:2216`, that $A_{12}$ is computed per
  function and averaged over functions. That sentence is also the one whose
  earlier phrasing ("on the raw runs") collided with Table A43's caption for the
  **pooled** statistic, so fixing it closes the collision at its source.
- **The recorded O1 spec was wrong about the cost, and that is why this shipped
  at all.** It claimed the caption edit "touches a generated exhibit chain
  (generator -> tables/SA0*.tex + word_sources/*.json -> native DOCX table)".
  Verified false: `SA06.json`'s `caption_stub` does **not** render - none of its
  distinctive phrases appear in `supplementary.docx` - and the rendered DOCX
  caption is pandoc's conversion of the `.tex` caption. A `.tex`-only edit
  suffices. The spec's cost estimate had been the main argument for deferring.
- **The pass-43 source guard earned itself.** `source_files` reported
  `supplementary.tex` moved and `cover_letter.tex` unmoved - exactly the
  discrimination it was added to provide after pass-42 edited a source without
  rebuilding its render.
- **Anchor.** `4b5c6ae8f6be20509d3cd95f8357e5633d923b22`.

## D-0053 (2026-08-27) - Pass-45: what a deep review of our own instrument found

- **Decision.** Discharge the reader-facing findings of a 97-agent application of
  `papers/PAPER_REVIEW_PROMPT.md`, mint **pass-45**, cut **v2.18**. Registered as
  **CR-0028**.
- **The finding that justifies the pass.** Section 3.5 - the subsection that
  *defines* contribution C1 - still carried the submitted caveat that whether the
  learned basis outperforms coordinate axes "is not established", and routed the
  reader to the superseded S6.5. The revision's own S9.1 established it, against
  the basis. Four review dimensions found it independently, and it answers the
  exact point reviewer 2 raised. `git diff v2.13..HEAD` shows the revision
  rewrote the two structurally identical caveats at `:163` and `:302` and missed
  this one - a site the revision skipped, not drift from a later edit.
- **The report's own safer remedy was also unsafe, and was not applied.** It
  appended the S9.1 result while leaving "is not established" standing, which
  would have made one paragraph assert both that the question is open and that it
  is settled. The applied text removes the false clause, keeps the true
  S6.5-scoping one, and states the adverse direction **numeral-free** because the
  edit ends inside an inline BIND window whose artifact is a complexity note and
  could not evidence a p-value.
- **And its advice to hand-edit `supplementary_pandoc.tex` was declined.** The
  pandoc shims are generated by `build_docx.py`; a hand edit is clobbered by the
  next build and reads as done. This is the third time that advice has been
  offered and the third time it has been wrong.
- **Calibration worth recording.** Of 82 verified findings, **44 were refuted**
  and **75 of 82 proposed remedies were judged unsafe as written**. The
  instrument finds real defects; its prescriptions are not safe to apply
  unexamined. That ratio is now consistent across four independent rounds.
- **Anchor.** `5fa4d389a77e372acec3c5a133c6f96ac833f483`.

## D-0054 (2026-08-28) - Pass-49: the round-two batch, driven by the external second-round audit

- **Decision.** Apply, as one freeze pass, the second-round corrections the
  external Phase 00-40 audit identified and this project verified against the
  live tree: run and report the missing threshold half of reviewer point R2.7,
  fix the statistical convention the paper stated but the revision analyzer did
  not implement, and retire every remaining pre-revision claim site. Mint
  **pass-49**, tag **v2.22**. Registered as **CR-0029**.
- **Calibration held again.** Every audit P0 checked was CONFIRMED on the live
  tree (the C1 heading, the causal tiering prose, the near-zero mismatch with
  its decision flip reproduced to six decimals, the stale submission manifest,
  the false CFF resubmission date, the public-docs overclaims); its
  prescriptions were still not applied unexamined - the full abstract rewrite
  was declined for a minimal edit (195 texcount words), and the E5 design was
  improved by reusing E3's U-low arm at D = 30 as the fifth registered cell.
- **E5 (Amendment A4, registered before execution).** Four new cells, 1,740
  runs, promoted as the additive release rev2-rel-2026-08-28-203c78744 with the
  fifth cell reused from round one. Result, adverse first: at D = 30 the
  shipped middle profile loses to BOTH neighbouring tiers (Holm 5.5e-3 and
  2.2e-3), each transplant lifting the descriptive ordinal to first; at D = 100
  the T2 set beats the shipped upper profile on paired means (Holm 1.5e-2)
  with the family ordinal unchanged; D = 10 and D = 50 are not separated.
  Contribution C2 as narrowed (D = 10, D = 50) is untouched by every cell.
  S9.5 / Table A47 carry it; the limitations replace the thresholds-untested
  concession with the executed coverage.
- **Canonical near-zero rule (Amendments A5-A6).** The manuscript stated a
  1e-8 tie band the primary pipeline applied but the revision analyzer did
  not. The rule is now implemented once and passed everywhere; regenerating
  E1-E3 moved seven p-values and exactly one decision - E1 D = 100 eigenframe
  vs coordinate, 0.054296 -> 0.048869, not-separated -> separated - all
  recorded in A6 before regeneration, with the analyzer's known-answer pins
  updated to the canonical values and five regression tests pinning the band.
- **Tag incident, recorded rather than hidden.** v2.22 was first cut before
  the CITATION.cff bump, so its tree embedded version 2.21; the cff validator
  caught it. The tag was deleted and re-cut on the bump commit about sixty
  seconds after the first push, while the repository was PRIVATE and before
  any consumer existed. The never-re-point rule protects consumers of
  published tags; a superseding v2.23 would instead have falsified the DAS in
  the freshly built PDF, which names v2.22. Recorded so the reflog surprise
  is a documented decision, not an anomaly. *Addendum, same evening:* the
  rendered-sweep addendum (anchor 112a98c) forced a re-mint, and v2.22 was
  re-cut a second time onto the new mint under the same conditions (repo
  private, zero consumers); the register grew to 84 passages.
- **Package integrity restored.** submission_package_manifest.json was stale
  on all five upload files (48/80/3 recorded pages vs 47/80/2 actual at
  pass-49); regenerated from the final bytes. CITATION.cff no longer claims a
  resubmission that has not happened. The three change documents rebuild
  against v2.22: marked main 48 pp, marked supplementary 80 pp, register 81
  passages / 22 pp, each generator carrying its own guards (S9 mapping
  verified at the target ref; the parity spot-check's pypdf arrow-glyph
  artifact sidestepped by a tier-pair prefix in A47's boundary column).
- **Anchor.** d543c14 (apply); the mint, tag and CFF bump follow it; NEXT
  free ids are CR-0030 and D-0055.

## D-0055 (2026-08-28) - Pass-50: every closed or deferred item reopened and implemented

- **Decision.** On the author's explicit instruction, the items previously
  closed by author decision or deferred as polish were reopened and, where an
  agent can implement them, implemented in one pass. Mint **pass-50**, tag
  **v2.23**. Registered as **CR-0030**. Reversals of earlier decisions in this
  entry are authorized reversals, not drift.
- **D-0051 promotion, previously closed: DONE.** promote_g1_recheck.py
  re-derives the verdict fail-closed from the staged bytes before any copy
  (255 cells; 26/26 divergent cells equal the transplant arm, none the
  archive; 229/229 agreeing cells equal both; 0 seed mismatches) and promotes
  the additive release g1-rel-2026-08-28-65b3d39e6. The Supplementary's
  package-agreement paragraph and the Table A45 caption now report the
  residual as a demonstrated BUILD difference citing that release; the DAS
  names it. The D-0051 standing rule (state the gap, never the causation)
  is satisfied by stating a demonstrated mechanism, not a conjectured one.
- **GitHub purge, previously closed unfiled: REOPENED, to be filed.** While
  the repository is private the objects are not publicly served, so the
  ticket is best filed immediately after the public flip on upload day; the
  ready-to-send text and both full SHAs stay in
  docs/development/github_exposure_traffic_record.md, whose status header now
  says REOPENED. Filing is the author's action (requires their GitHub login).
- **Extension request, previously declined: REVIEWED and DRAFTED, not sent.**
  The work is complete, so the only remaining value is schedule insurance for
  upload day itself (deadline = planned date, zero slack). A ready-to-send
  draft with that honest assessment sits withheld beside the response letter
  (papers/review_2026_08_24/extension_request_draft.md, D-0049 folder).
  Sending is the author's call; nothing is sent on their behalf.
- **P1-06 Figure 4: redesigned.** The within-one-CD-of-best cohort rows are
  shaded as one block and a dashed line marks best+CD, so separation is read
  off the bars; the detached CD ruler that could be mistaken for group
  linkage is removed. Caption and intro sentence updated; all nine figure
  files regenerated from the frozen rel-2026-07-20 bundle with the built-in
  CD cross-check.
- **P1-07 captions: tightened.** The two convergence-figure captions drop
  the shared protocol boilerplate, now stated once in the body; each keeps
  its function selection and mandated unfavorable case.
- **P1-10 cover letter: reframed and corrected.** Two stale facts fixed (it
  still said not-separated at D=100 and counted four experiments); new
  structure leads with closure, then what held, then the three adverse
  findings plainly; enclosures and the latexdiff-invisible retitle named;
  COI/GenAI paragraph verbatim; Markdown twin in parity; dated 1 September
  2026; rebuilt deterministically x2.
- **P2 bibliography: pruned.** The 17 uncited entries removed from
  references.bib (61 -> 44) and from the three citation-control files in the
  same change, re-verified uncited against the current sources first; C1-C5
  pass at 44 keys everywhere. fialho2010adaptive verified correct as recorded
  (ED-8 cosmetic key-year mismatch; entry cites Da Costa et al. 2008, right
  DOI) and deliberately not renamed.
- **Author policy question, answered and applied: the published artifacts no
  longer reference the revision process.** Seventeen sites across main.tex,
  the sections and the supplement dropped reviewer/round/added-in-revision
  language; S9 is retitled Mechanism-Isolation and Sensitivity Experiments
  and every experiment is motivated scientifically; pre-registration and
  amendment language stays as scientific provenance; the reviewer-facing
  documents keep reviewer references by design; the Word caption stubs no
  longer carry reviewer-point tags. The five-experiment enumeration in the
  supplementary-inventory sentence was corrected from four in the sweep.
- **Register redesigned (author request):** title page with a stats band,
  clickable per-file contents, reviewer-point badges, and color-coded
  as-submitted/as-revised panels; 92 passages at v2.23.
- **Process notes.** The v2.23 tag was first cut before the CITATION.cff
  bump - the same sequencing error as v2.22's first cut, caught by the same
  validator and re-cut under the same conditions (private repo, seconds old,
  zero consumers). The lesson is now mechanical: bump CFF, commit, then tag.
- **Anchor.** 095604d (apply); mint, tag v2.23 and the CFF bump follow. NEXT
  free ids: CR-0031 and D-0056.

## D-0056 (2026-08-28) - Pass-51: acceptance-readiness review executed; five verified findings fixed

- **Decision.** The tuned acceptance-readiness review
  (docs/prompt/change-register-acceptance-review.md) was executed as a live
  audit at maximal input: fresh Step-1 sweeps over the rendered PDFs, a
  change-by-change audit of all 92 register passages, and targeted
  re-verification of every claimed number the audit touched. Five findings
  survived self-refutation and were fixed in one batch. Mint **pass-51**,
  tag **v2.24**. Registered as **CR-0031**.
- **CR-F1 (Major, internal contradiction).** supplementary.tex S6.5 still
  asserted that whether the learned eigenbasis outperforms coordinate axes
  'remains unidentified' --- eight lines above the same paragraph's
  parenthetical stating that Section S9.1 answers it directly. Fourth member
  of the stale-open-claim family (S3.5 fixed in pass-45, conclusions in
  pass-50, S6.5 discussion now). The sentence is scoped to phase-level
  attribution with the basis-level pointer to S9.1; the adverse direction
  stays stated where S9.1 reports it.
- **CR-F3a/b/c (policy, three sites).** Three revision-process references
  survived the pass-50 de-process sweep because each wraps across a source
  line break ('added in / revision', 'carried out in / revision', 'the /
  revision's') and none contains the word 'reviewer'. Caught only by the
  rendered-text sweep (pdftotext), not by source grep --- the lesson
  generalises: sweep the RENDER for phrase-level policies. The
  GenAI/Acknowledgments 'preparation and revision' phrasings are the
  mandated MDPI disclosure and are deliberately kept.
- **CR-F2 (stale attestation).** The environment attestation predated
  pass-49's statistics.py zero_tol change and its five KATs: it recorded 613
  tests at head 31fe38d while the shipped suite collects 618. Re-minted
  green (618 tests x2, 616 passed + 2 skipped, six gates exit 0);
  supplementary.tex count corrected 613 -> 618.
- **Refuted findings (recorded per the instrument's calibration doctrine).**
  Every 'superior/dominates' hit in the Step-1 sweep proved to be a negated
  or adverse usage on context check; 'eigenframe final polish' (x6) is
  settled mechanism naming, not a claim of benefit; the supplement's two
  remaining 'revision' tokens are the software-revision sense; the E5/E2
  shared 0.0055 is disclosed cell reuse, not duplication. The #72
  'strictly negative' edit was verified CORRECT against _dt_core.py: the
  s == 0 case returns before the restricted branch, so the branch condition
  is strict --- the as-submitted 'non-positive' was the imprecise version.
- **Register.** The CR-F1 edit adds one hunk: the register is 93 passages
  (supplementary.tex 33 -> 34) at v2.24; counts synced in the response
  letter, the round-one record and REVISION_STATUS. Marked PDFs rebuilt at
  48/80 pages against the pass-51 apply commit.
- **Validation.** check_manifest 15/15 + sources 2/2 after mint; all
  thirteen ladder gates PASS; citation-cff validates all 23 tags with the
  working tree at 2.24 ahead of the v2.24 tag (bump-before-tag, the D-0055
  lesson, followed this time).
- **Anchor.** e8594c5 (apply); mint, close and tag v2.24 follow. NEXT free
  ids: CR-0032 and D-0057.

## D-0057 (2026-08-29) - Pass-52: seven-lens panel review of the response letter; 28 confirmed findings fixed

- **Decision.** A fourteen-agent adversarial review of the reviewer-facing
  response letter ran seven independent lenses (quote fidelity, numerical
  consistency, claims-vs-manuscript, internal consistency, language, layout,
  location lines), each finder's output adversarially verified. 42 findings
  raised; 28 CONFIRMED, 8 DOWNGRADED, 2 REFUTED, 4 verified misses added by
  the verifiers. All confirmed findings fixed. Mint **pass-52**, tag
  **v2.25**. Registered as **CR-0032**.
- **The two findings that mattered most.** (1) The letter quoted the revised
  abstract as 'adapt scalar control ... to a single operating point' - the
  shipped abstract says 'scalar parameters' (renamed in a later pass; the
  quote was never resynced), on the exact sentence R1.1 is about. (2) Two
  E1-table cells carried the superseded exact-zero release values (6.1e-4,
  3.0e-6) instead of the canonical tie-rule values Table A43 prints (6.8e-4,
  4.0e-6) - directly under the letter's own claim that every table carries
  the canonical values. Both corrected from the shipped artifacts.
- **Also fixed in the letter (untracked, rebuilt):** SA01/SA02 renamed to the
  typeset Tables A23-A24 (internal \\input filenames a reviewer cannot find);
  R1.3's Location corrected to Sections 3.2/4.9 (the Conclusions carry no NP
  qualification) and R2.1's to Section 3.3 for the C2-narrowing sentence;
  'elite archive' corrected to the manuscript's 'diversity archive'; the
  reviewer's dropped severity-signal sentence restored (verbatim only in the
  withheld letter); E5's 'before any of its runs executed' scoped to NEW runs (the
  reused fifth cell predates Amendment A4); the load-bearing 'other' restored
  in the build-residual sentence; the protocol-conformance design note no
  longer attributed to the manuscript; the 26-divergent-cells unit glossed as
  run-level; Holm labels completed on E5's insensitive contrasts; 'three
  affected rows' corrected to six; three-companion-documents accounting
  (the marked Supplement exists and ships); plus grammar/tone nits and
  monospace hyphenation disabled (identifier integrity).
- **Tracked changes (the freeze-voiding pair):** the cover letter's stale
  'all 84 revised passages' (register is at 93; the count drifted twice)
  replaced with count-free wording in both twins and rebuilt
  deterministically x2; the DAS names tag v2.25; CFF 2.25 bumped before the
  tag per the D-0055 lesson.
- **Latent defect found and fixed while minting:** the package manifest's
  recorded byte sizes had been stale since pass-51 - the size-update needle
  in the pass-51 updater silently never matched, and no gate checks those
  bytes. All five entries now carry disk-true sha256 AND bytes.
- **Validation.** check_manifest 15/15 + sources 2/2 after mint; thirteen
  ladder gates PASS x2; register unchanged at 93 passages; cover letter
  byte-identical across two independent build pairs.
- **Anchor.** b6a18d1 (apply); mint, close and tag v2.25 follow. NEXT free
  ids: CR-0033 and D-0058.

## D-0058 (2026-08-29) - Pass-53: full remediation of the five-instrument review register

- **Decision.** All five live review instruments were retuned to the current
  state and re-applied; their consolidated findings were then fixed in one
  pass, with only genuine submission-day operational work deferred (public
  flip, GitHub purge ticket, SuSy portal fields). Manuscript fixes were NOT
  deferred on the grounds that they cost a freeze cycle - the author's
  instruction was explicit that a freeze cycle is not a reason to defer.
  Mint **pass-53**, tag **v2.26**. Registered as **CR-0033**.
- **The finding that justified the pass.** The Supplementary's ninth
  limitation asserted that the sweep 'leaves the dimension-tier boundaries
  themselves unvaried, so their sensitivity is untested' - nine pages before
  Section S9.5, which varies exactly those boundaries and finds against the
  shipped profile in two of five cells. Two independent reviewers rated it
  Major; it sits on R2.7, a reviewer's own point, and the clause renders as
  NEW underlined text in the marked-up copy. The main-text Conclusions had
  been updated for E5; the supplement twin had not. Fifth member of the
  stale-claim family (S3.5 pass-45, conclusions pass-50, S6.5 pass-51).
- **The question the paper could not answer.** No published sentence said why
  the interaction-structure memory and its eigenbasis still ship given
  +57.3% wall-clock and no detectable benefit; the argument existed only in
  the response letter. The Conclusions now state it: the evaluated
  configuration was fixed and checksum-locked before the isolations ran, so
  replacing a component in response to the experiment that measured it would
  define a different algorithm and unbind every reported number. The
  isolations correct the claims, not the method.
- **Also fixed in the manuscript.** C2's narrowing carried to the
  Introduction, where C2 is claimed (C1's had reached five sites, C2's one);
  the abstract's separation quantifier scoped to CEC2017, being false for
  CEC2013 D = 10 (p_Holm 0.0017, and favourable - the error was against the
  authors); Section 4.9's first alternative explanation pointed at Section
  S9.1, which now bears on it; the CEC2013LSGO fifty-fold initial-population
  ratio disclosed in the main text and the replication scoped as
  common-INITIAL-NP; Table A46's caption states the registered integer
  convention; the C1 stage named consistently at six sites; four references
  to 'the submitted manuscript' reworded; the Section S5.10 appositive no
  longer mis-attributes the primary release id to Section S9; Section S9.4
  enumerates all seven constants. Figure 4's value labels no longer sit
  under the critical-difference rule.
- **Build reproducibility restored (the quiet one).** `build_pdf.py` and
  `build_supplementary.py` carried NO epoch handling and relied on the
  operator exporting SOURCE_DATE_EPOCH / FORCE_SOURCE_DATE. Pass-51 and
  pass-52 built in shells without them, so the shipped PDFs carried
  wall-clock /CreationDate while the freeze manifest claimed double-build
  byte-identity and the response letter told the reviewers the same. The
  epoch is now pinned INSIDE both builders, as the register and marked-PDF
  builders already do; a double build verifies byte-identical and
  /CreationDate reads D:20260708000000Z. This is the inverse of the DOCX
  trap: there a persisted variable broke determinism, here an absent one.
- **Governance records.** reproducibility_manifest.json recorded wrong
  sha256 AND bytes for all five shipped artifacts, stale since pass-45;
  refreshed. published_commit was four passes stale (matched 4/15 hashes)
  and its note asserted an identity that no longer held; both corrected.
  evidence_release raised from five to the seven the DAS names (rev2 and g1
  were missing). The recorded pytest count corrected to 618. CR-0029 through
  CR-0033 appended to change_request_register.csv, where they had existed
  only in decision-log prose - the 'verify ids free at apply time' rule was
  unusable from the register itself. The dangling-commit full SHA
  abbreviated in both manifests; the private bundle path removed from the
  decision log (the cleanup's ninth site).
- **Documentation.** SUBMISSION_KIT's paste-ready abstract was the v2.21
  wording and would have put three reverted phrasings into the journal's own
  abstract field; resynced with a hardened warning. The gsk-list health
  check told maintainers to expect seven optimizer ids where the runner
  reports fifteen (seven-method panel plus eight external baselines) -
  corrected there and in nine further files. The runbook documented four
  revision experiments where the driver runs five. BENCHMARK_RULES gained
  the rev2 and g1 release blocks. Scripts inventory 19 -> 21 at nine sites;
  six wrong path:line citations; mermaid label quoting; docs/index status
  box; navigation for thirteen unlinked development records.
- **Deliberately NOT done.** `benchmarks/cec_reference_results/README.md`
  carries three stale release ids and one broken relative link, but it is
  hash-bound in the primary evidence release (3403/3403). Evidence releases
  are immutable and non-superseding, so the correction belongs to a
  governance pass that can mint a new release, not to a documentation fix.
  Recorded here so it is not rediscovered as new. Related hazard found while
  proving it: `git checkout --` on that file writes CRLF under
  core.autocrlf=true and breaks its manifest hash, because `.gitattributes`
  protects the papers/ freeze files but not the evidence README.
- **Validation.** check_manifest 15/15 + sources 2/2 after mint; thirteen
  ladder gates PASS twice; ruff clean; package manifest verified sha AND
  bytes post-write for all five entries (the pass-51 silent-staleness class
  is now structurally impossible in that updater).
- **Anchor.** 86411e6 (apply); mint, close and tag v2.26 follow. NEXT free
  ids: CR-0034 and D-0059.

## D-0059 (2026-08-29) - Pass-54: remediation of the merged five-instrument re-review

- **Decision.** Every review instrument was re-applied from scratch after
  pass-53, and three targeted cross-audits were run alongside them. Their
  merged findings were verified against bytes or against the render, then
  fixed in one pass. Mint **pass-54**, tag **v2.27**. Registered as
  **CR-0034**. Only genuine submission-day operations were deferred: the
  public flip, the GitHub purge ticket, and the SuSy portal fields.
- **The finding that justified the pass.** BOTH architecture tables - Table 4
  row 8 and Table 5 row 9 - still read 'Eigenframe final polish' and
  'Eigenframe polish', on pages whose own prose already says 'the one-shot
  deterministic final polish'. Pass-53 renamed the stage at six prose sites
  and recorded it as done; the two table cells were missed, and they are the
  first place an editor checking R2.3 looks, because the response letter tells
  the editor in as many words that C1 was renamed. In the marked-up copy the
  row carries NO diff markup while the adjacent list entry on the same page
  shows the rename applied. Source-side greps had been run against the prose;
  the table cells use the same words in a different grammatical role. **The
  render is what catches this class, and only the render.**
- **The most serious scientific finding.** The Supplementary invited a
  commit-level pre-registration audit that the PUBLIC repository fails. The
  CEC2020 addendum's recorded signing commit 5c9bfae82 does not resolve
  ('Not a valid object name'), and the squashed public history's root commit
  is dated 2026-07-31 - two days AFTER the release cec2020-rel-2026-07-29 it
  registers. A reader accepting the invitation gets the opposite of the claim.
  The content binding is intact: the addendum's SHA-256 recorded in the
  CEC2020 and CEC2013LSGO release manifests matches the file on disk. The
  claim is therefore moved onto that binding, and the squash - which appeared
  nowhere in either PDF - is disclosed as the reason commit dates are
  unavailable. Nothing is softened: the registration still predates the
  outcomes, and for E5 the commit-level check still works (Amendment A4,
  commit 10ef466, 18:42:49, against the first E5 run at 18:43:55).
- **Also fixed in the manuscript.** The abstract's 'on that suite' followed
  TWO named suites, and under the nearest antecedent the next clause was false
  - at CEC2013 D = 30 DT-GSK is third (3.38, behind eGSK 3.07 and ATMALS-GSK
  3.34), not second; scoped to CEC2017 and widened to 'either suite', which is
  verified on both. 'The tie band itself affects no significance decision' is
  removed, contradicted by its own paragraph (ties are discarded before
  ranking, so the band sets n_eff) and by Section S9.1, where the canonical
  rule moves D = 100 from 0.054 to 0.0489, across alpha. 'The single
  Holm-significant unfavorable headline cell in this study' is corrected: the
  pre-registered CEC2020 leg adds two at D = 20. The Conclusions now carry the
  basis negative at BOTH active dimensions, C2's narrowing, and E2's adverse
  result - which had reached neither limitation ledger, though it answers the
  point both reviewers raised. The supplement's seventh limitation joins the
  stale-claim family and is corrected to the main text's approved form.
  Amendment A3 is disclosed as the Section S9 preamble promises. The CEC2020
  runner-up fact cited the APGSK paper at five sites (the supplement's version
  named both papers in one sentence) and now cites the CEC2020 AGSK paper;
  the six APGSK-mechanism citations are correct and untouched.
- **The letters.** cover_letter.md carried two paragraphs that pass-50 deleted
  from cover_letter.tex, and SUBMISSION_KIT tells the author to paste the
  Markdown as 'the plain-text twin of the PDF'. It was not the twin, and one
  orphan said 'four pre-registered experiments ... two of them returned
  results against our submitted claims' where the same file says five and
  three - understating the adverse-finding count on the page carrying the
  letter's credibility argument. The stale closing is deleted; the scope
  paragraph is RESTORED to the .tex instead, because the response letter's
  R2.6 already cites the cover letter as carrying it.
- **The abstract is over the journal's guideline and was NOT trimmed.** It
  renders at 205 words against a 200-word guideline, and was already 204 at
  v2.26 - so the response letter's '195 words by texcount, under the journal's
  200-word limit' was wrong before this pass touched it. The false count is
  removed rather than corrected, and the abstract is left alone: the sentences
  carrying the CEC2020 and CEC2013LSGO outcomes are bound to registered
  wording banks (RS-12, RS-13), and re-drafting registered outcome wording to
  meet a soft cap would damage exactly the pre-registration integrity the
  Section S8/S9 defence rests on. **This is an open author decision:** trim
  the two unregistered opening sentences if the editor objects.
- **Build.** papers/scripts/build_cover_letter.py is added. cover_letter.pdf
  is files[10] and cover_letter.tex one of the two hashed source_files, yet no
  builder existed - a hand-run pdflatex stamps a wall-clock /CreationDate, and
  the natural response to the resulting digest mismatch is to re-mint, which
  silently records a non-reproducible PDF under a manifest asserting
  double-build identity. All three PDFs now double-build byte-identical.
- **Code and documentation.** The five scoped-mypy errors that five documents
  called 'clean' are fixed with provable runtime no-ops (typing.cast and
  annotations); the gate exits 0. Fourteen documents asserted a hosted CI that
  has NEVER existed in any commit - `git log --all -- .github` is empty and
  the path is not ignored - including an unverified 3.10-3.13 matrix claim
  against a single local 3.10.11 interpreter; all now describe the local gate.
- **Governance.** reproducibility_manifest's pass-53 refresh had itself gone
  stale WITHIN pass-53 (it ran at the apply commit; the two main-manuscript
  artifacts were rebuilt afterwards), and its note asserted the very check it
  had failed. Digests, anchors, updated_utc and the evidence_release block
  (four releases and a superseded ablation id, against the seven the DAS
  names) are corrected, and a private monorepo absolute path is redacted from
  this tracked, about-to-be-public file. The package manifest's
  authoritative_commit and release list are resynced and its register note
  made count-free, every earlier numeric copy having gone stale.
- **Validation.** check_manifest 15/15 + sources 2/2 after mint; the ladder
  green; ruff and the scoped mypy clean; package manifest verified sha AND
  bytes post-write for all five entries.
- **Anchor.** 9093e99 (apply); mint, close and tag v2.27 follow. NEXT free
  ids: CR-0035 and D-0060.

## D-0060 (2026-08-29) - Pass-55: author-directed closure of the deferred register items

- **Decision.** The author directed that open issues 4 through 10 of the
  pass-54 register be fixed. A six-agent read-only verification panel ran
  first; every proposed edit was applied only with a byte-verified needle,
  and seven candidate fixes were REFUTED by that panel and not applied.
  Mint **pass-55**, tag **v2.28**. Registered as **CR-0035**.
- **The abstract (issue 4).** Trimmed 205 -> 199 rendered words against the
  journal's 200-word guideline, in UNREGISTERED material only: two article
  deletions, one slash-compound (style already present in sentence one), and
  the basis negative flipped to the active voice the decision log and the
  response letter already use. The RS-12 CEC2020 sentence, the RS-13
  CEC2013LSGO sentence, the reviewer-adopted opening and the closing scope
  sentence are byte-identical before and after, verified against HEAD.
  Two candidate trims were refuted: 'keeping the GSK vector-update equations'
  would attach retention to the final refinement, which does not use those
  equations, and any edit to the opening would break the response letter's
  verbatim self-quote of the one sentence Reviewer 1 personally rewrote.
- **The tier-scope sentence (issue 10).** One ADDITIVE sentence in the
  CEC2020 subsection anchors 'every dimension-gated subsystem is inactive
  (D <= 20)' to Table 4's gating taxonomy and names what the 20-49 tier does
  activate - the optional DE arm joining the ACE pool at 20 <= D < 100, the
  top/bottom credit-memory split, changed tier constants - while the three
  gated subsystems stay off. Every clause was verified against the
  hash-gated _dt_profiles.py; the SAP addendum Section 9 bank pre-writes
  only the outcome sentences, and none was touched. The panel rejected
  adding the sentence at the S8, conclusions or abstract sites: those
  placements are the registered bank's.
- **Supplement refinements (issues 6, 7, 9c).** Six caption/prose fixes,
  each verified against the release bundles: A43's caption states the W/T/L
  direction (matching A45/A47) and why the POOLED A12 statistic compresses
  toward 0.5 (the cross-product is dominated by between-function scale, so
  near-0.5 values do not mean a null contrast); the E3 prose no longer
  counts the D = 10 tie-by-construction among insensitivity outcomes; the
  E5 D = 100 discussion now reports the adverse 2.34 -> 1.97 descriptive
  mean-rank movement beside the unchanged ordinal; S7.1 matches the DAS on
  which LSGO ports are vendored byte-faithful copies; and the false
  'stability under a larger perturbation implies stability under a smaller
  one' is replaced by exactly what Amendment A1 licenses. Of the ten
  allegedly-uncited tables, SEVEN were refuted - they are covered by
  rendered en-dash range references ('Tables A2-A5' covers A3 and A4) and
  the label-level zero-ref count was the artifact; the three genuine
  orphans (acronyms, the CEC2013 Wilcoxon-Holm matrix, the ISM
  conditional-benefit table) gained references in their series' style. The
  three page-order inversions (inline [H] boxes running ahead of deferred
  [p] floats) are cured by three commented clearpage flushes; caption order
  is untouched, so no table renumbers; placement-specifier alternatives
  were examined and declined as non-deterministic without a test build.
  The supplement grew 81 -> 83 pages; dependent page counts were synced and
  the kit's marked-supplement count made count-free after going stale at
  three consecutive passes.
- **Companions and documentation (issues 5, 8, 9a, 9b).** 87 stale
  path:line citations in the four baseline algorithm guides were re-based
  by content verification at BOTH endpoints - an independent recount found
  87, not the prior audit's 46; the deliberate comment-line citation at
  apgsk.md:297 was preserved. build_change_register.py now renders hunk
  context VERBATIM; this activated a latent tex_escape ordering bug (the
  backslash pass ran first and the brace passes corrupted its own
  \textbackslash), fixed via placeholder routing in the same commit -
  output byte-identical for backslash-free input. statistical_analysis.md
  gained its siblings' orientation blockquote. Two anchor-slug divergences
  between the project slugger and GitHub's were cured (the determinism
  heading renamed operator-free; a docs/index link that was dead in the
  BUILT site today fixed); a 99-link sweep found no other linked pair.
- **Refuted and left alone.** Seven table refs (range-covered), two abstract
  trims (above), detokenize routing for the register context (percent signs
  comment out the line), dropping the register's legibility gate, a
  'D 50+' heading variant (operator-class trailing character), and the
  apgsk.md:297 comment-line citation. Recorded so they are not rediscovered.
- **Validation.** check_manifest 15/15 + sources 2/2; both PDFs double-build
  byte-identical at the pinned epoch; the abstract's rendered count verified
  at 199; registered sentences verified byte-identical; float order verified
  in the render (A2 p4 <= A10 p8; A14 <= A15; A37 <= A38). Ladder and
  cross-artifact audit re-run at the close.
- **Anchor.** 1586242 (apply); mint, close and tag v2.28 follow. NEXT free
  ids: CR-0036 and D-0061.

## D-0061 (2026-08-29) - Pass-56: closure of the from-scratch five-instrument re-review

- **Decision.** All five review instruments were re-applied from scratch at
  pass-55/v2.28 by a five-agent panel (one per instrument); 31 findings
  survived the agents' own ~50% refutation calibration (45 candidates were
  agent-refuted). Every fix was verified against bytes before application.
  Ordinary-commit fixes landed first; the four frozen-byte fixes mint
  **pass-56**, tag **v2.29**. Registered as **CR-0036**.
- **The finding that mattered most (cover letter).** The letter's blanket
  claim that all five pre-registered experiments had 'design, statistical
  conventions and adverse-outcome wording committed to the public repository
  before any result existed' is FALSE for E5 on its natural reading:
  Amendment A4 was registered after the E1-E4 results existed, and E5's
  fifth cell reuses executed E3 runs whose adverse D = 30 outcome was known
  at registration. The response letter states the chronology precisely; an
  editor cross-reading the two letters could catch the discrepancy on the
  revision's central integrity claim. The cover letter (both twins) now
  matches: 'four experiments before any result existed, and the fifth
  registered by amendment before any of its new runs executed.'
- **The governance bug this round exposed (and the gate it bought).** The
  pass-55 mint recorded a published_commit whose tail was INVENTED while
  expanding a 9-hex abbreviation - the SHA resolved to nothing, and no gate
  read the field. check_manifest.py now gates the resolvability of
  anchor_commit and published_commit with git cat-file; it caught the
  corrupt value live on its first run and is negative-tested. This mint
  computes the field with git rev-parse; hand-typed SHAs are banned from
  mint scripts.
- **The stale-claim family's FIFTH recurrence (fixed in batch A).** Seven
  documents - README, the plain-language summary, the DT-GSK guide, the
  core reference, the explainer, two glossary rows, the round-one review
  record - still said the E1 eigenframe contrast is 'not separated at
  D = 100', against the manuscript's canonical Amendments-A5/A6 result
  (separated, Holm 0.0489). README and the plain summary are the first two
  documents a referee clicking the DAS reads. All seven now state the
  canonical result; the supplement's E3 sentence ('not separated at D = 50
  or D = 100') is a DIFFERENT contrast and was correctly left alone.
- **Other frozen-byte fixes.** cover_letter.pdf gains the PDF metadata every
  other shipped artifact carries; claims_evidence_matrix RS-12's quoted
  verbatim now matches the abstract locus exactly (it matched no shipped
  locus); artifact_binding gains rows for the three shipped figures that had
  none (the Figure 4 four-panel grid - the bound FIG-CD-D* rows are the
  superseded single panels - and both concept flowcharts), and asset_map
  dates the output_checksum column: labels, not checksums, are the gated
  content.
- **Batch-A highlights (ordinary commits, this round).** The LIVE upload-day
  instructions in REVISION_STATUS still ordered the register from
  git diff v2.13 v2.27 and called v2.27 the frozen record - an author
  following them on 2026-09-01 would have uploaded a register missing every
  pass-55 change; the frozen-record and next-free-id sentences are now
  tag-agnostic/pointer-based. CITATION.cff promised the source of every
  re-implemented baseline and listed five of six - the eGSK article is
  added. The response letter's R2.5 row still described the abstract in its
  pass-53 form ('only at CEC2017 D = 10', false as a data claim - CEC2013
  D = 10 also separates); its markup note now discloses that the abstract
  and keywords, like the title, are preamble-set and appear unmarked.
- **Half-updated freshness blocks are the round's defect class.** Token
  sweeps updated 'pass-55 / v2.28' where those exact strings appeared and
  missed same-sentence companions in another lexical form. Retunes must
  sweep ALL prior-tag tokens and classify each hit, not search-replace the
  current pair; several recurring sentences were made pass-agnostic so they
  cannot go stale the same way again.
- **Validation.** check_manifest 15/15 + sources 2/2 (now including commit
  resolvability); package and reproducibility manifests verified post-write;
  cover letter double-builds byte-identical with full metadata; ladder and
  cross-artifact audit re-run at the close.
- **Anchor.** 33ee170 (apply); mint, close and tag v2.29 follow. NEXT free
  ids: CR-0037 and D-0062.

## D-0062 (2026-08-29) - Pass-57: closure of the optional-queued and immutable-history items

- **Decision.** The author directed that the register's remaining
  optional-queued items and the recorded-immutable items be fixed. Two
  verification agents ran first (the checksum row plan; the protocol-NP
  claim across all five suites). Mint **pass-57**, tag **v2.30**.
  Registered as **CR-0037**.
- **artifact_binding output_checksum re-derived.** 84 stale pairs across 48
  of 71 rows - values dated from the pre-migration monorepo tree while the
  artifacts were regenerated at the 2026-07-31/08-01 imports and later
  passes. TWO independent derivations (the verification agent's row plan and
  the applier's own recomputation from artifact_path) agreed on every pair
  before the write; a structural check proved no other column changed. The
  11 prose-valued rows (native-table n/a entries and the pass-53 revision
  exhibits) are untouched by design. Format conventions preserved:
  basename=hex pairs ';'-joined, never CSV-quoted, CRLF.
- **The protocol-conformance sentence is in the manuscript.** Section 3.2's
  asymmetry paragraph now states: both population settings are
  protocol-conformant - each suite's protocol fixes its evaluation budget
  and run count (the frozen protocol table) and prescribes no population
  size. Generalized beyond the letter's CEC2017 form ONLY after verifying
  every in-repo protocol authority for all five suites (BENCHMARK_RULES,
  the manuscript's own protocol table, the SAP addendum's registered facts,
  the SuiteProtocol dataclass, both protocol audits, all five equivalence
  reviews): none prescribes or mentions a population size. The DOCX shim
  mirrors it; the response letter's 'our observation here, not a manuscript
  statement' aside becomes 'now also stated in Section 3.2' and the letter
  is re-rendered.
- **The immutable-history items are fixed by DISCLOSURE, the only correct
  means.** Rewriting pushed history would move published tags, break the
  Data Availability Statement, and violate D-0045. The freeze manifest now
  carries immutable_history_note recording both blemishes where an auditor
  will look: (1) the pass-54 commit c0028c1's MESSAGE cites anchor 4d6bd1b,
  which resolves to nothing, while the manifest committed in that commit is
  correct - commit messages cannot be corrected without rewriting pushed
  history; (2) the manifest copies frozen inside tags v2.26-v2.28 stand as
  minted, including v2.28's published_commit whose tail was invented while
  expanding an abbreviation - corrected on main at pass-56 and gated by
  check_manifest's resolvability check since.
- **The heredoc backslash trap fired AGAIN during this pass** - a ref macro
  authored through an inline heredoc shipped into the built PDF as a literal
  carriage return plus 'ef', caught only by reading the render. The repair
  added a LONE-CR audit: the standing no-lone-LF purity check cannot see a
  bare 0x0D, which is exactly what a collapsed backslash-r produces. The
  standing rule is unchanged and re-learned: author LaTeX and regex through
  Write-tool scripts, never a heredoc.
- **Validation.** check_manifest 15/15 + sources 2/2 with commit-field
  resolvability; package and reproducibility manifests verified post-write;
  Table 13 reference verified resolving in the render; ladder and
  cross-artifact audit re-run at the close.
- **Anchor.** 87af854 (apply+mint HEAD at close). NEXT free ids: CR-0038
  and D-0063.

## D-0063 (2026-08-29) - Pass-58: second affiliation for A.W.M. (author metadata)

- **Decision.** The author directed (2026-08-29) that Ali Wagdy Mohamed carry
  a second affiliation: University of Science and Technology, Zewail City of
  Science and Technology, 6th of October City, Giza 12588, Egypt. Mint
  **pass-58**, tag **v2.31**. Registered as **CR-0038**.
- **Scope.** Author metadata only: the \\Author line and address block in
  main.tex and supplementary.tex, the DOCX shim's author/center block, the
  A.W.M. affiliation in CITATION.cff, and the kit's portal author table.
  No number, rank, p-value, decision or claim changes. Page counts unchanged
  (49/83); the main PDF was double-built byte-identical; the response
  letter's manuscript page anchors were re-verified against the new render;
  the change register (v2.13..HEAD) records the affiliation passages in both
  documents, so the referees' marked-changes trail covers it.
- **Folded documentation fixes (from the same-day four-lens open-issues
  sweep, all evidence-verified before the write):** the public-flip item's
  anonymous-access sentence, spliced mid-sentence by commit 25236eb, is
  re-seated after the 404 sentence; What-remains items 3-5 are marked done
  (the Pop=100 banner fix, the PAPER_REVIEW_PROMPT old-title mention, and
  the freeze-inventory asymmetry were each verified already discharged);
  CLAUDE.md's two stale next-free id statements and the superseded
  unpushed-cleanup warning are corrected, and rule 6 gains the phase_09
  evidence_binding_verification.csv carve-out (rewritten every pass by
  convention); the package manifest's DAS note (stale at v2.28 since
  pass-55) and hand-typed generated_utc are replaced with computed values;
  the acceptance-readiness P3 purge-ticket pointer is re-aimed at the
  withheld PRIVATE_OPS.md; SKILL.md and runbook.md gate-battery anchors now
  name the pass-56 commit-field-resolvability gate.
- **Validation.** check_manifest 15/15 + sources 2/2; reproducibility and
  package manifests re-minted with computed commit fields and verified
  against disk post-write; validate_citation_cff over all 31 tags at the
  close; provenance gate green once CR-0038 is registered (it correctly
  failed in the window between the source comment citing CR-0038 and this
  registration).
- **Gate amendment (validate_cross_format_parity).** The new author-line
  superscript "1,2" made the affiliation paragraph unmatchable in the PDF
  text channel: the leading address label extracts flush against the
  author superscripts and the second label extracts as a digit-only line
  that normalize_pdf_text strips as a margin number. The paragraph check
  gains a narrowly-scoped PASS_FORMAT_DIFF class
  (affiliation-label-adjacency) that accepts only when the paragraph with
  its superscript address-label digits removed is verbatim in the PDF;
  full battery re-read 774 rows / 0 FAIL after the change.
- **Anchor.** Apply commit 8b83a39 (affiliation + rebuilt renders); the
  close commit carries the manifests, governance pair and doc sync. NEXT
  free ids: CR-0039 and D-0064.

## D-0064 (2026-08-29) - Pass-59: corresponding author's full name (author metadata)

- **Decision.** The author directed (2026-08-29) that the corresponding
  author's byline carry the full name **Mostafa Elsayed Ahmed Masoud**.
  Mint **pass-59**, tag **v2.32**. Registered as **CR-0039**.
- **Scope.** Author metadata only: the byline, PDF metadata, address block,
  CRediT author-contributions statement and Conflicts of Interest statement
  now use the full name and the matching initials **M.E.A.M.** (twelve
  documents: main.tex, supplementary.tex, cover_letter.tex/.md, the
  plain-language summary, CITATION.cff (both author lists), README, the
  submission kit's portal table, the response letter and its technical
  companion, the author-data handoff, and the withheld extension-request
  draft; 54 text edits in all). Historical records - the administrative-gap
  register's dated rows, the journal decision email, the paper-revisions
  snapshot and the append-only trees - are deliberately unchanged.
- **No result changes.** No number, rank, p-value, decision or claim
  changes. Every render rebuilt at its pinned epoch and double-built
  byte-identical (main PDF, supplement, both DOCX, cover letter,
  plain-language summary); page counts unchanged (49/83); the response
  letter's manuscript page anchors re-verified against the new render; the
  change register (v2.13..HEAD, now 138 passages / 33 pages) records the
  name passages in both documents.
- **Order lesson applied.** The DAS was bumped to v2.32 BEFORE the builds,
  so no post-mint main.tex drift occurred (the pass-58 ordering slip that
  check_manifest caught did not recur).
- **Validation.** check_manifest 15/15 + sources 2/2; reproducibility and
  package manifests re-minted with computed commit fields and verified
  against disk post-write; full gate battery at the close.
- **Anchor.** Apply commit ed713a7 (name + rebuilt renders); the close
  commit carries the manifests, governance pair and status sync. NEXT free
  ids: CR-0040 and D-0065.

## D-0065 (2026-08-29) - Pass-60: DAS release-ID compression and pseudocode re-rendering

- **Decision.** The author flagged two presentation defects (2026-08-29):
  the Data Availability Statement's inline enumeration of five hash-suffixed
  auxiliary release identifiers reads as machine output, and the Algorithm 1
  rendering was hard to read (long steps wrapping across lines, orphaned
  equation anchors, a six-line prose note inside the float). Mint
  **pass-60**, tag **v2.33**. Registered as **CR-0040**.
- **DAS.** The primary release rel-2026-07-20-67d9345f9 stays named inline
  (provenance-gated); the five auxiliary additive releases (CEC2013LSGO,
  CEC2020, E1-E4, E5, and the Table A45 identity re-execution) are
  summarized in one sentence deferring their identifiers to the
  Supplementary Materials and the repository's release manifests, where all
  five were already recorded; the no-primary-value-changes and
  own-checksummed-manifest claims are retained verbatim in the compressed
  sentence. The CN-02 evidence binding is unchanged and green.
- **Pseudocode.** New manuscript-owned rendering
  papers/sections/algorithm_pseudocode_render.tex replaces the phase_03
  LaTeX rendering IN THE MANUSCRIPT ONLY: one physical line per numbered
  step, no orphaned right-aligned anchors, the cross-cutting-controllers
  note compressed to a closing pointer at the Section 3 execution-order
  paragraph that carries the same content. Semantics, the step set and the
  frozen loop order (accept -> memory update -> credit/ARGP -> escape ->
  local search -> polish -> global-best -> restart) are unchanged; the
  phase_03 canonical .md and .tex stay untouched in their append-only tree
  (rule 6 respected: superseded in use, never edited).
- **No result changes.** No number, rank, p-value, decision or claim
  changes; page counts unchanged (49/83; the algorithm float keeps page 12
  to itself); the main PDF double-built byte-identical; all eleven
  response-letter page anchors re-verified against the new render; the
  change register (v2.13..HEAD, 138 passages / 33 pages) records both
  presentation changes.
- **Validation.** check_manifest 15/15 + sources 2/2; reproducibility and
  package manifests re-minted and verified post-write; full ladder green
  including cross-format parity, evidence bindings, provenance, and the
  pass-59-era package-contents gate.
- **Anchor.** Apply commit 82e3839 (DAS + pseudocode + rebuilt renders).
  NEXT free ids: CR-0041 and D-0066.

## D-0066 (2026-08-29) - Pass-61: back-matter leading and execution-order list readability

- **Decision.** The author flagged (2026-08-29) that the Acknowledgments
  block renders with crushed line spacing and that the twelve-step
  execution-order list is not eye-friendly. Mint **pass-61**, tag
  **v2.34**. Registered as **CR-0041**.
- **Back matter.** Root cause is the class, not the content: mdpi.cls
  typesets \\acknowledgments, \\authorcontributions, \\funding and
  \\conflictsofinterest at \\fontsize{9}{9} - 9pt text on 9pt leading,
  zero interline space. The manuscript preamble now re-declares all four
  at 9/11.5, keeping the journal's smaller statement size with normal
  leading. The class file itself is untouched.
- **Execution-order list.** The Section 3 list (papers/sections/
  proposed_algorithm.tex) drops noitemsep for itemsep=2pt/topsep=4pt and
  gains a needspace{18} guard, so it renders as one uninterrupted
  twelve-item block (now page 15) instead of leaving items (1)-(2)
  orphaned at a page bottom with the rest across the full-page algorithm
  float.
- **Pagination.** One shift: Section 3.3's C2-narrowing statement moved
  from page 16 to page 15. The response letter's single reference to it
  is updated and the letter rebuilt (9 pp); every other letter page
  anchor (1, 11, 21, 24, 26, 32, 39, 42, 43, 46) verified unchanged.
- **No result changes.** No number, rank, p-value, decision or claim
  changes; page counts unchanged (49/83); main PDF double-built
  byte-identical; DOCX validated; register 138 passages / 34 pages.
- **Validation.** check_manifest 15/15 + sources 2/2; reproducibility and
  package manifests re-minted and verified post-write; full ladder green
  including parity, evidence bindings, provenance and package contents.
- **Anchor.** Apply commit cf332f1. NEXT free ids: CR-0042 and D-0067.

## D-0067 (2026-08-29) - Pass-62: Supplementary Materials and Abbreviations leading

- **Decision.** The author flagged (2026-08-29) that the Supplementary
  Materials statement renders with the same crushed line spacing pass-61
  cured elsewhere. Mint **pass-62**, tag **v2.35**. Registered as
  **CR-0042**.
- **Scope.** The Supplementary Materials and Abbreviations statements were
  the last two users of mdpi.cls's fontsize 9/9 zero-leading back-matter
  style; both are re-declared at 9/11.5 in the manuscript preamble beside
  the four statements fixed at pass-61. The class's remaining 9/9 sites
  (the affiliation block and the references list) were checked and receive
  real leading from their own spacing{1.35}/linespread{1.44} wrappers, so
  this closes the family. The class file itself remains untouched.
- **No result changes.** No number, rank, p-value, decision or claim
  changes; no pagination shift (49/83 pages; all eleven response-letter
  page anchors verified in place, no letter rebuild needed); main PDF
  double-built byte-identical; DOCX validated.
- **Validation.** check_manifest 15/15 + sources 2/2; reproducibility and
  package manifests re-minted and verified post-write; full ladder green.
- **Anchor.** Apply commit 934192a. NEXT free ids: CR-0043 and D-0068.

## D-0068 (2026-08-30) - Pass-63: resubmission re-dated to 2026-08-30

- **Decision.** The author submits TODAY, 2026-08-30 - two days ahead of
  the confirmed 2026-09-01 deadline. Mint **pass-63**, tag **v2.36**.
  Registered as **CR-0043**.
- **Scope.** The cover letter (both twins) and the response letter (and its
  technical companion) are re-dated 30 August 2026 and rebuilt;
  CITATION.cff carries date-released 2026-08-30 and the new planned date
  with the unchanged deadline noted; CLAUDE.md and REVISION_STATUS drop the
  zero-slack framing - submitting early restores the margin the deadline
  confirmation had removed - and the public-flip item moves to upload day
  2026-08-30. The deadline itself (2026-09-01) is unchanged everywhere it
  is cited as a deadline.
- **No result changes.** No number, rank, p-value, decision or claim
  changes; page counts unchanged (49/83, letter 9 pp); the main PDF and
  the cover letter each double-built byte-identical; all letter page
  anchors verified.
- **Validation.** check_manifest 15/15 + sources 2/2; reproducibility and
  package manifests re-minted and verified post-write; full ladder green.
- **Anchor.** Apply commit fcb17f2. NEXT free ids: CR-0044 and D-0069.

## D-0069 (2026-09-01) - Pass-64: supplement made standalone at the editorial office's request

- **Decision.** Comply with the editorial office's email of 2026-09-01: the
  supplementary material must carry no reference content and no highlighted
  markings, and the revised file goes back by email. Mint **pass-64**, tag
  **v2.37**. Registered as **CR-0044**.
- **Scope.** The file the office reviewed was verified byte-identical to the
  latexdiff changes-marked supplement before any edit - the "highlighted
  markings" are diff marks, not shipped styling; the re-sent file is the
  clean supplement. From papers/supplementary.tex: all 30 cite callouts
  (31 key instances, 26 lines) removed as bare markers, and the
  bibliography block (reftitle / externalbibliography / bibliography)
  removed with the float-flush clearpage kept. The three registered or
  verbatim-adopted sentences carrying cites (RS-12 at the S8 locus, the
  adjacency disclosure, the S7 SHADE-ILS/MOS disclosure) lost only the
  marker: every registered word is byte-identical. All 18 supplement keys
  remain cited in the main text, so references.bib and the role/word maps
  are unchanged; citation_usage_map.csv drops its 31 supplement rows.
  Zebra row-striping stays: it is table formatting, not markup, and not
  what the office saw. DAS bumped to v2.37 before the builds.
- **No result changes.** No number, rank, p-value, decision or claim
  changes; supplement 83 -> 82 pp (the reference list's final page);
  every sent-letter page anchor re-verified unmoved in the rebuilt render
  (pp. 53, 56, 59, 60, 76, 77, 78, 79, 81); main PDF unchanged at 49 pp;
  all five auxiliary release identifiers verified present.
- **Validation.** check_manifest 15/15 + sources 2/2; reproducibility and
  package manifests re-minted and verified post-write; all four renders
  double-built byte-identical (PDF epoch 1783468800, DOCX 1783641600);
  full ladder green.
- **Anchor.** Apply commit 725aa82. NEXT free ids: CR-0045 and D-0070.
