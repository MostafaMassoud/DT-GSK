<!--
  papers/PAPER_BUILD_PROMPT.md  (current filename)
  Historical filename: ism_gsk_q1_evidence_locked_master_prompt.md
    -- retained for provenance only. The file and its subject algorithm were
    renamed ISM-GSK -> DT-GSK on 2026-07-14. "ISM-GSK" / `ism_gsk` are NOT
    current identifiers; "ISM" survives only as the interaction-structure
    memory MECHANISM name. See the Current-status note in Section 0.
  ================================================================
  Single authoritative implementation framework for auditing, executing,
  writing, validating, and packaging the DT-GSK study under a closed
  literature corpus and an immutable empirical-evidence boundary.

  Revision date: 2026-07-20  (previous revision: 2026-07-10)
  Supersedes: all earlier manuscript-construction prompts and any companion
  phase text that conflicts with this document.

  Execute this document from beginning to end. Do not draft scientific prose
  before the evidence, method, protocol, claim, and analysis-plan gates pass.
  Do not execute ablation until the final phase and its entry gate pass.
-->

# DT-GSK — Evidence-Locked Q1 Publication Production Framework

## 0. Executive mandate

Act as a coordinated multidisciplinary research team with expert competence in
continuous optimization, metaheuristics, evolutionary computation, algorithm
engineering, CEC benchmark suites, experimental design, non-parametric
statistics, scientific reproducibility, research methodology, scientific
visualization, academic writing, editorial review, LaTeX, Microsoft Word OOXML,
OMML mathematics, bibliography management, and high-impact journal submission.

Your objective is to autonomously produce a scientifically defensible,
publication-ready DT-GSK article and its complete publication package. The
framework must govern the entire research lifecycle: source audit, method and
code verification, benchmark governance, analysis-plan freeze, primary
statistical analysis, exhibit generation, manuscript drafting, dual-format
production, adversarial review, final ablation, supplementary assembly,
reproducibility verification, and submission packaging.

The target is **Q1-level rigor and presentation**, not an unsupported guarantee
of acceptance and not an unverified claim about a journal's current quartile.
Every scientific statement must remain within the evidence available in the
approved local literature corpus and the immutable empirical evidence release.

---

**Current status (2026-07-20 — read this first).** This framework has already
been **executed end-to-end**. The DT-GSK manuscript is **built** (dual-format
PDF + native Word, the pre-ablation supplement, the promoted evidence release,
and the governance package all exist). The project is therefore in **final
pre-submission remediation**, not a from-scratch run. Read this document as the
authoritative *maintenance and remediation* reference for that manuscript: where
a phase describes producing an artifact that already exists, treat it as the
acceptance contract that artifact must continue to satisfy. Every normative
requirement below still governs.

- **Remediation ledger:** the 80-ticket ledger
  (`papers/governance/remediation_2026_07_18/ticket_status.csv`) stands at
  **73/80 fully closed** (`closed_verified` / `superseded_with_evidence`). The
  remaining 7 are terminal, machine-gated, or author-gated (see below).
- **Current evidence releases (fill the `<release_id>` placeholders below with
  these):** primary **`rel-2026-07-20-67d9345f9`** (anchor commit `67d9345f9`);
  ablation **`abl-rel-2026-07-20`**; derived analysis bundle
  `papers/analysis/rel-2026-07-20-67d9345f9/`. Superseded ids
  (`rel-2026-07-16-78f075cb0`, `rel-2026-07-10-262fc16c9`, `abl-rel-2026-07-16`,
  `abl-rel-2026-07-13`) MUST NOT be cited as current — they belong only in
  explicit provenance history.
- **Live blocker — RT-001 (Major, IN PROGRESS):** re-time the six comparators
  on CEC2017 on one idle machine (`scripts/retime_comparators.py --workers 15`)
  so `tab:runtime` is a single-environment comparison. The M038 backend fix
  activated the compiled (numba) interaction-graph kernels, which reproduce the
  NumPy path bit-for-bit but dropped DT-GSK wall-clock (e.g. CEC2017 D100
  69.04 -> 41.59 s). Only `runtime_seconds` changed; every scientific column is
  byte-identical, so the runtime table is frozen until the refresh lands and is
  deliberately promoted.
- **Terminal sequence (pending, in strict order), after RT-001 and any author
  edits land:** **C-008** — mint a *fresh* `main_manuscript_freeze_manifest.json`
  (`papers/governance/main_manuscript_freeze_manifest.json`; it is **CRLF +
  2-space** — edit it in place, never via `read_text()`/`sed`, which normalize
  to LF and break the hashes) -> **C-001** — a single authoritative commit plus
  the manuscript version id.
- **Author-supplied residue (never auto-generate):** suggested reviewer names
  (author-pending), JCR/Scopus quartile figures (N-021), and benchmark-report
  access dates (N-009, bib carries zero `urldate` fields).
- **Quality gates:** all **GREEN** as of 2026-07-20, via the now-implemented
  `papers/scripts/validate_*.py` suite (see Section 15.0) plus the deterministic
  citation-usage map and the environment attestation.

Naming reminder: the algorithm and its data-id are **DT-GSK** / `dt-gsk`; the
optimizer adapter is `src/gsk_family/optimizers/dt_gsk.py`. "ISM" appears below
only as the interaction-structure memory mechanism (a supporting component, not
a contribution, whose direct-isolation overlay shows no significant standalone
benefit) or in explicit "renamed FROM ISM-GSK" history. There is no `ism_gsk.py`.

---

### 0.1 Normative language

The terms **MUST**, **MUST NOT**, **SHALL**, **SHALL NOT**, **REQUIRED**,
**SHOULD**, **SHOULD NOT**, and **MAY** are normative:

- **MUST / SHALL / REQUIRED**: mandatory; failure blocks the relevant gate.
- **MUST NOT / SHALL NOT**: prohibited.
- **SHOULD**: expected unless a documented, evidence-based exception exists.
- **MAY**: optional and non-blocking.

### 0.2 Single-authority and precedence rule

This file is the only project-wide implementation guide. Earlier prompts,
phase companions, addenda, notes, draft prose, and remembered project history
are non-authoritative when they conflict with it.

Use the following precedence hierarchy:

1. the latest explicit human requirement;
2. this master framework;
3. immutable evidence metadata and the code/configuration actually used to
   produce that evidence, for factual protocol questions;
4. the current repository runbook for exact executable command syntax, after
   verifying that it does not violate this framework;
5. companion phase files and historical addenda, for examples only;
6. manuscript prose, comments, filenames, and project memory.

A conflict between this framework and immutable evidence metadata is not solved
by silently choosing one. Record the conflict, stop the affected claim or
analysis, and resolve it through a documented correction. Never edit evidence
to make it agree with prose.

### 0.3 Explicitly superseded instructions

The following earlier instructions are superseded:

- `results/_run_all/` is **not** a publication-evidence fallback. It is a
  staging or independent-reproduction area only.
- All publishable empirical analyses, tables, plots, comparisons, discussions,
  conclusions, and numerical claims MUST read exclusively from a validated,
  immutable release inside `benchmarks/cec_reference_results/`.
- The ablation study MUST NOT appear in the main manuscript.
- The ablation study MUST be executed only in the final implementation phase,
  after algorithm freeze, primary benchmarking, primary statistical
  validation, dual-format manuscript completion, adversarial review, and main
  manuscript finalization.
- No phase after the final ablation phase is permitted. Supplementary
  integration, final reproducibility verification, and submission packaging
  are completed inside that final phase.
- Wording intended to evade AI-text detectors is prohibited. The writing goal
  is genuine academic clarity, specificity, and integrity.
- A requirement to cite all bibliography entries never overrides semantic
  correctness. Decorative citations and `\\nocite{*}` are prohibited.

### 0.4 Core operating law

**No claim may outrun its evidence.**

When evidence is absent, incomplete, non-comparable, contradictory, or outside
the permitted sources, the agent MUST do one of the following:

1. omit the claim;
2. narrow the claim to the supported scope;
3. label it explicitly as a hypothesis or unresolved limitation, when that is
   scientifically useful;
4. add a pre-specified analysis using already admissible evidence; or
5. record the gap and block the affected deliverable.

The agent MUST NOT replace missing evidence with plausible wording, estimated
numbers, remembered findings, invented metadata, or an unsupported inference
presented as fact.

### 0.5 Autonomous operating model

The agent SHALL operate autonomously and shall not require routine user
instructions between phases. It MUST:

- make mechanical, organizational, formatting, and evidence-preserving choices
  independently;
- choose the repository-wired journal template as the provisional target when
  no target is explicitly supplied, then verify current official instructions;
- choose conservative scientific wording when several phrasings are possible;
- continue all unblocked work when one item is blocked;
- document every assumption, rationale, decision, risk, mitigation,
  intermediate artifact, command, validation result, and review outcome;
- use explicit defaults only when they do not fabricate scientific or
  administrative facts; and
- fail closed when a missing fact could alter a result or submission statement.

The agent MUST NOT invent author names, affiliations, ORCIDs, funding,
conflicts, ethics approvals, reviewer identities, data-availability URLs, or
other administrative facts. Missing administrative metadata does not stop
scientific work; it is entered in `administrative_gap_register.md` and blocks
only the final upload-ready acceptance gate.

### 0.6 Idempotence, resumability, and change control

- Every phase MUST be safe to rerun.
- Every generated artifact MUST have a deterministic path and provenance.
- Every phase MUST leave the repository buildable or restore the prior state.
- Raw and immutable evidence MUST never be edited in place.
- Changes to algorithm code, benchmark evaluators, seed policy, stopping rules,
  or analysis definitions after their freeze gate require a formal change
  request recorded in `change_request_register.csv` (Sections 3.1 and 12.2),
  impact analysis, invalidation list, and rerun of every affected gate.
- The final ablation phase may toggle only pre-approved frozen components. It
  MUST NOT introduce algorithm modifications.

### 0.7 Definition of completion

The project is complete only when every acceptance criterion in this framework
has a linked artifact, command output, checksum, or review record. A polished
PDF without the evidence, Word, source, supplementary, reproducibility, and
validation packages is incomplete.

---

# 1. Required publication package and output contract

## 1.1 Mandatory publication outputs

The final phase MUST produce all of the following:

1. a publication-ready main manuscript PDF;
2. a fully editable Microsoft Word manuscript (`.docx`);
3. journal-ready LaTeX source, class/style files, bibliography, and build
   instructions;
4. a standalone supplementary PDF containing the complete ablation study and
   all other approved supplementary evidence;
5. a fully editable supplementary Word document when the journal accepts or
   requests Word supplementary files;
6. publication-quality figures in final vector/raster formats plus source data
   and generator scripts;
7. native editable Word tables, never screenshots or flattened table images;
8. editable diagrams and flowcharts where applicable, with native DrawingML,
   SmartArt, or an editable source such as `.drawio`, `.pptx`, or equivalent;
9. bibliography and in-text citations formatted for the selected journal;
10. a complete reproducibility package containing code/configuration hashes,
    environment records, seeds, commands, checksums, and evidence bindings;
11. machine-readable statistical outputs and claim/evidence governance files;
12. cover letter, highlights, declarations, data/code availability statement,
    and other journal-required administrative files, using verified metadata
    only;
13. a source archive sufficient for future revisions; and
14. a final compliance, integrity, and residual-risk report.

## 1.2 Canonical output layout

Use the existing repository layout where compatible. Otherwise create this
logical package without duplicating authoritative data:

```text
papers/
  main.tex
  main.pdf
  main.docx
  supplementary.tex
  supplementary.pdf
  supplementary.docx
  references.bib
  sections/
  tables/
  figures/
  diagrams/
  word/
    reference.docx
    source_store.xml
    field_registry.csv                # word_validation_report.md lives in
                                      # papers/governance/ (Section 3.1); word/
                                      # may hold only a pointer to it
  build/
  build_prompt_phases/
  governance/
  submission_package/
    manuscript/
    supplementary/
    figures/
    source/
    reproducibility/
    administrative/
```

If existing paths differ, record the mapping in `project_configuration.md`.
Do not create two competing sources of truth.

**Derived-output equivalence (CR-0003).** The externally proposed
`paper_outputs/` tree is satisfied by the frozen equivalent mapping and MUST
NOT be created as a separate root: data inventory and validation ->
`papers/governance/` (Phase 2 artifacts); derived data, statistics, and
rankings -> `papers/analysis/<release_id>/`; tables -> `papers/tables/` (with
`results/paper_tables/` as rendered-input staging); figures ->
`papers/figures/`; traceability and QA -> `papers/governance/`; manuscript and
supplementary -> `papers/`; release package -> the Phase 12 submission and
reproducibility package. Strict separation from
`benchmarks/cec_reference_results/` is the invariant; relocating these frozen
roots mid-run is prohibited (decision D-0006).

## 1.3 Main-manuscript ablation prohibition

The main manuscript, abstract, highlights, graphical abstract, conclusion, and
cover letter MUST NOT contain:

- ablation tables or figures;
- ablation p-values, ranks, effect sizes, overhead values, or convergence
  results;
- claims that a component is necessary, sufficient, independently causal, or
  quantitatively contributory based on ablation; or
- detailed ablation interpretation.

During the final phase, after ablation evidence is promoted and analyzed and
under the Phase 12 correction-exception workflow (task 12.15), the main
manuscript MAY gain one neutral sentence pointing readers to the Supplementary
Materials for the complete ablation study, provided the target journal permits
such a pointer. That sentence MUST contain no ablation result or promotional
conclusion, and the main manuscript is re-frozen after it is inserted.

## 1.4 Target-journal rule

The repository may currently be wired for MDPI `Algorithms`, while IEEE TEC or
another leading optimization/evolutionary-computation journal may be a fallback.
Do not assume current quartile, page limits, article structure, or file
requirements from historical notes.

At runtime, verify current official author instructions and record:

- journal and article type;
- instruction URL or official source identifier;
- access date;
- template/version;
- abstract, word, figure, supplementary, and source-file rules;
- reference style;
- anonymization and declaration requirements;
- Word-versus-LaTeX submission rules; and
- any generative-AI disclosure requirement.

Official journal guidance is administrative evidence only; it cannot support
scientific claims.

## 1.5 Provisional page budget

Until current journal guidance is verified, use these internal ceilings:

| Block | Provisional ceiling | Required content |
|---|---:|---|
| Title, abstract, keywords | abstract ≤ 250 words | problem, gap, method, verified scope, one bounded result |
| Introduction | 1.5–2.0 pages | motivation, gap, contributions, roadmap |
| Related work | 2.0–2.5 pages | GSK family, adaptive control, structure-aware methods |
| Problem and baseline | 0.75–1.25 pages | formulation and inherited GSK mechanics |
| Proposed method | 4.0–5.0 pages | formal definition, pseudocode, complexity, safeguards |
| Experimental setup | 1.0–1.5 pages | suites, panel, runs, seeds, MaxFES, statistics |
| Primary results | 3.5–4.5 pages | summaries, inference, convergence, secondary evidence, overhead |
| Discussion, limitations | 1.5–2.0 pages | interpretation and threats to validity |
| Conclusion | 0.75–1.0 page | evidence-bounded recap and future work |
| Main total | approximately 16–22 typeset pages | excluding references; no ablation content |
| Supplement | as needed | full tables, full curves, final ablation, reproducibility details |

**Hard page-limit rule.** The main manuscript MUST NOT exceed the page limit
(or the typical accepted article length, when no hard limit is published) of
the verified Q1/Q2 target journal, as recorded during the Phase 4 journal
verification — never an assumed or remembered limit. Overflow MUST be resolved
only by migrating non-essential material to the Supplementary Materials:
extended tables, additional figures, detailed derivations, comprehensive
per-function experimental results, and supporting analyses all default to the
supplement (Section 8.6). Overflow MUST NOT be resolved by shrinking figures or
tables below legibility, deleting required declarations, or compressing prose
past comprehensibility. The main text remains concise, focused, and
publication-ready: it carries only what a reviewer needs to judge the claims.
Compliance is measured, not estimated — the typeset page count is read from
the compiled PDF at the Phase 8 draft gate, the Phase 9 build, and the Phase 11
finalization gate, and a page-count row is recorded in
`papers/governance/phase_gate_register.csv` at each of those gates.

---

# 2. Evidence constitution

## 2.1 Admissible evidence classes

Use evidence according to its class. One class cannot silently substitute for
another.

### L — Approved literature evidence

Only a readable source inside `reference_papers/` with a matching, valid entry
in `papers/references.bib` may support external scientific statements,
definitions, prior methods, benchmark methodology, statistical methods,
motivations, or findings.

### E — Immutable empirical evidence

The sole admissible empirical source for publishable numbers and empirical
claims is a validated release inside:

```text
benchmarks/cec_reference_results/
```

This includes raw/per-run finals, convergence records, provenance files, and
derived outputs only when their derivation is recorded and reproducible.

Files under `results/`, temporary analysis directories, notebooks, manuscript
tables, and plots are **working artifacts**, not publication evidence. They
become admissible only after validation and controlled promotion into a new,
versioned, checksummed location under `benchmarks/cec_reference_results/`.

### M — Method, evaluator, and implementation evidence

Source code, configurations, tests, benchmark evaluator code, pseudocode,
version history, and execution logs may support statements about what the
algorithm and protocol do. Code comments and filenames are not sufficient;
executed behavior must be verified.

### J — Journal and administrative evidence

Official journal guidance may determine formatting, declarations, and package
structure. It MUST NOT support scientific claims.

### A — Author-supplied administrative evidence

Verified author metadata, funding, conflicts, ethics statements, and reviewer
suggestions may populate submission forms. They MUST NOT be inferred or
invented.

## 2.2 Closed literature corpus

The scientific citation universe is the runtime intersection of:

1. valid BibTeX entries in `papers/references.bib`; and
2. verified matching, readable sources in `reference_papers/`.

Appendix A lists the expected 61 keys, but expected does not mean admissible.
For every expected key:

- verify title, authors, year, venue, and DOI when present;
- record any mismatch;
- reject missing, unreadable, duplicated, or materially mismatched sources;
- never reconstruct missing metadata from memory or the web;
- never use an abstract or search snippet as a substitute for a local full
  source; and
- never cite an outside scientific source, even when it would improve the paper.

When the corpus lacks support, enter the gap and omit or narrow the claim.

## 2.3 Empirical source lock and strict-source guard

Every analysis process MUST enforce all of the following:

```text
resolved_source_path starts with benchmarks/cec_reference_results/
source_release_id is recorded
source checksum matches the release manifest
no result loader fallback path is used
no data value is read from results/, papers/tables/, or a prior manuscript
```

If the current loader automatically falls back to `results/_run_all/`, create or
activate a strict reference-only mode that fails loudly whenever a requested
cell is missing. Do not alter numerical logic merely to add the guard.

A publication analysis MUST emit a source-use audit listing every opened data
file. The gate fails if any empirical input lies outside the immutable evidence
release.

**Explicit immutability prohibitions (CR-0003).** For the selected release —
and for `benchmarks/cec_reference_results/` generally — the following actions
are prohibited without exception:

- modifying, overwriting, renaming, moving, or deleting files;
- in-place normalization or manual correction;
- substituting recalculated or re-run values;
- misleading smoothing;
- fabricating or silently interpolating missing values;
- silently removing outliers; and
- changing numerical precision, seeds, run identifiers, function identifiers,
  dimensions, evaluation budgets, or convergence checkpoints.

All transformations operate on read-only inputs, with outputs written outside
the reference tree. Display-only log floors per Section 6.7 remain permitted
and disclosed.

## 2.4 Controlled staging-to-evidence promotion

New or independently reproduced runs MAY be created in `results/` as staging.
They MUST NOT enter the paper until promoted through this process:

1. generate candidate outputs using frozen code, configuration, seeds, and
   environment;
2. validate completeness, schema, checksums, run counts, MaxFES, seed schedule,
   function set, dimensions, floating-point sentinel, and failure handling;
3. compare against the intended protocol and document every deviation;
4. generate a promotion manifest and immutable release identifier;
5. copy through a scripted ingestion process — the named promotion tool
   `scripts/promote_evidence.py`, built as a Phase 2 tooling task (task 10) —
   into a new versioned subtree under `benchmarks/cec_reference_results/`;
6. prohibit manual edits during or after ingestion;
7. verify the promoted copy byte-for-byte against the accepted staging bundle;
8. make the release read-only; and
9. rerun all affected analyses strictly from the promoted release.

Existing immutable evidence is never overwritten. Corrections create a new
release and an explicit supersession record.

## 2.5 Source precedence within a claim

When sources disagree, use this evidentiary order and document the discrepancy:

1. immutable raw/per-run records and evaluator inputs in the selected evidence
   release;
2. frozen code and configuration used for those records;
3. verified derived machine-readable outputs;
4. generated tables and figures;
5. manuscript prose;
6. comments, filenames, planning notes, and memory.

Never change evidence to match the manuscript. Regenerate derivatives or
correct the claim.

## 2.6 Claim-level traceability

Every substantive statement MUST have a row in
`claims_evidence_matrix.csv` before final prose is accepted. The row MUST
contain:

```text
claim_id,normalized_claim,claim_type,manuscript_location,
literature_keys,literature_locators,empirical_artifact_ids,
code_or_protocol_locators,analysis_id,support_strength,
permitted_wording,prohibited_wording,scope,assumptions,
reviewer_risk,mitigation,status,review_status
```

Allowed claim types include:

```text
BACKGROUND, DEFINITION, PRIOR_METHOD, PRIOR_FINDING, GAP,
ORIGINAL_METHOD, IMPLEMENTATION, PROTOCOL, EMPIRICAL_RESULT,
STATISTICAL_RESULT, INTERPRETATION, LIMITATION, RECOMMENDATION,
ADMINISTRATIVE
```

Support strength is `direct`, `partial`, `indirect`, or `unavailable`.
Unavailable claims are omitted or explicitly blocked.

## 2.7 Scientific-paragraph evidence rule

Every scientific paragraph MUST contain an appropriate evidence anchor.

- Literature, definition, comparison, motivation, and prior-work paragraphs
  MUST cite one or more semantically relevant approved sources.
- Original-method paragraphs MUST identify the original contribution and refer
  to its defining equation, algorithm, parameter specification, code mapping,
  or design record. Cite inherited or closest prior work only when it genuinely
  supports the relationship.
- Empirical paragraphs MUST cite the relevant table, figure, or supplementary
  artifact and map to immutable data provenance. They MUST also cite benchmark
  or statistical-method literature when that literature is invoked.
- Interpretive paragraphs MUST separate observation from interpretation and
  cite literature when an external mechanism or prior finding is invoked.
- Limitation paragraphs MUST anchor each limitation to tested scope, observed
  evidence, protocol, or a verified method property.

The requirement for paragraph evidence MUST NOT cause decorative citations. If
a paragraph cannot satisfy both evidence coverage and semantic citation
correctness, split, rewrite, narrow, or omit it. A paragraph containing only an
original procedure or an empirical observation may rely on internal evidence
anchors under the explicit original-contribution exception, but it may not make
external claims without literature support.

The abstract may omit rendered citations when required by the journal, but every
sentence still requires a claim-matrix entry.

## 2.8 Original-contribution rule

Original content is not exempt from scientific support. Every proposed
contribution MUST have:

- a precise formal definition;
- an inherited/modified/original decomposition;
- executable implementation evidence;
- equation/pseudocode/code correspondence;
- complexity and resource analysis;
- a direct, appropriately designed empirical test; and
- a bounded statement of what the evidence establishes.

Mark original content `[ORIGINAL]` in working notes, not in final prose.
Novelty claims MUST be bounded to the reviewed closed corpus unless stronger
evidence exists inside that corpus.

## 2.9 Quantitative integrity

Every number in prose, equations, tables, figures, captions, highlights, cover
letter, Word fields, supplementary material, and response documents MUST be
generated from or verified against admissible evidence.

The following are prohibited:

- estimating a value from a plot;
- copying a number from an old draft without rebinding it;
- inventing, interpolating, extrapolating, or rounding a missing value;
- silent rounding that changes ordering, ties, significance, or interpretation;
- pooling incompatible metrics or scales without a justified transformation;
- excluding unfavorable or failed runs without a pre-specified rule;
- using a best run as representative unless the protocol requires it;
- treating missing values as zeros, ties, wins, or successful convergence;
- computing a percentage with an unstable, zero, negative, or unsuitable
  denominator;
- claiming monotonicity without checking every relevant point; and
- manually changing a generated table cell or figure point.

## 2.10 Citation integrity

- Cite only verified admissible keys.
- Keep citations adjacent to the claims they support.
- Prefer direct primary sources when available in the corpus.
- Do not cite a source for a stronger statement than it makes.
- Do not use one citation as blanket support for unrelated claims.
- Do not infer non-existence from absence in the corpus.
- Do not fabricate authors, years, venues, DOIs, titles, or keys.
- Do not use `\\nocite{*}` or irrelevant text to force every BibTeX entry into the
  rendered bibliography.
- The locked BibTeX file may contain admissible but unused entries. The rendered
  bibliography MUST contain no undefined or illegitimate entry.
- If a project policy insists that all 61 admitted entries be used, each occurrence MUST
  pass semantic review; otherwise the policy is rejected as incompatible with
  citation integrity.

## 2.11 Honest comparison and interpretation

- Report wins, ties, losses, regressions, failures, and uncertainty.
- Define suite, function set, dimension, run count, seed design, MaxFES, metric,
  algorithm panel, parameter settings, and evidence release for every
  comparison.
- Use “statistically significant” only when the named test, valid unit,
  hypothesis family, correction, adjusted result, and direction support it.
- Report effect size and uncertainty alongside significance.
- Do not call imported evidence “reproduced.”
- Do not use paired inference without valid pairing.
- Do not imply general superiority from a same-family panel.
- Do not call an algorithm state-of-the-art without direct evidence against an
  adequate contemporary panel inside the admissible evidence.
- Distinguish measurement, interpretation, mechanism hypothesis, and causal
  claim.

## 2.12 Reproducibility and assumptions

For every headline result preserve:

- evidence release ID, repository commit, and dirty-state flag;
- source paths and SHA-256 checksums;
- suite/evaluator version and hashes;
- function set, dimensions, and run count;
- seed formula and exact schedule;
- MaxFES and all objective-call accounting;
- parameters, boundary handling, and stopping rule;
- environment and floating-point sentinel;
- analysis script, command, version, parameters, and outputs;
- exclusions, repairs, failures, and deviations; and
- Word/LaTeX artifact bindings.

Any assumption that can affect a conclusion MUST be verified, explicitly stated,
subjected to sensitivity analysis, or used to narrow the claim. Silent
assumptions are prohibited.

---

# 3. Mandatory governance artifacts

Create each artifact no later than the phase that first populates it;
pre-drafting phases MUST create every artifact their gates consume. Artifacts
first populated during or after drafting (for example
`citation_usage_map.csv` in Phase 8, `cross_format_consistency.csv` and
`word_validation_report.md` in Phase 9, `revision_log.md` in Phase 10, and
`final_integrity_audit.md` in Phase 12) MUST NOT be created as empty
placeholders earlier. The full governance set is mandatory by the final gate.
Use machine-readable formats for validation and Markdown for reviewer-facing
explanation.

`papers/governance/` is the canonical home of every governance artifact named
in this framework — the Section 3.1 table and governance artifacts introduced
in later sections (for example `contribution_matrix.md`,
`algorithm_freeze_manifest.json`, and `evidence_release_manifest.json`) —
unless the defining row or section explicitly names another canonical path.
Per-phase snapshots written under `papers/build_prompt_phases/phase_<NN>/`
(Section 12.4) are copies for gate evidence, never the master.
`word_validation_report.md` lives in `papers/governance/` and is only
referenced from `papers/word/`.

## 3.1 Core governance files

| Artifact | Minimum purpose |
|---|---|
| `project_configuration.md` | paths, target journal, release ID, phase state, defaults |
| `requirements_traceability_matrix.csv` | every mandatory source requirement mapped to implementation, validation, and status |
| `source_line_traceability.csv` | every nonblank line of the updated prompt classified as integrated, superseded, structural, or non-operative |
| `decision_log.md` | every autonomous decision, rationale, evidence, impact |
| `assumption_register.csv` | assumption, verification, sensitivity, status |
| `risk_register.csv` | risk, probability, impact, owner, mitigation, residual risk |
| `phase_gate_register.csv` | entry, validation, acceptance, exit evidence per phase |
| `change_request_register.csv` | formal post-freeze change requests, one row per request (Section 12.2 schema) |
| `administrative_gap_register.md` | missing non-scientific metadata |
| `reference_inventory.csv` | BibTeX-to-local-source identity audit |
| `evidence_cards/` | claim-ready source summaries with exact locators |
| `allowed_citation_keys.txt` | verified runtime citation set |
| `claims_evidence_matrix.csv` | claim-level literature/data/code traceability |
| `evidence_gap_register.md` | unsupported or partial claims and disposition |
| `citation_usage_map.csv` | every rendered citation occurrence and role |
| `asset_map.md` | every manuscript/data/code/table/figure artifact and action |
| `data_ledger.csv` | immutable evidence coverage and provenance |
| `experiment_matrix.csv` | run-level design and status |
| `comparability_audit.md` | comparator fairness and admissible inference level |
| `reproducibility_manifest.json` | environment, seeds, hashes, commands, outputs |
| `statistical_analysis_plan.md` | frozen estimands, endpoints, tests, corrections |
| `primary_stats/statistical_results.csv` | one machine-readable row per reported statistic (Section 7.14 schema); written inside the controlled analysis bundle (Section 7.13), not the governance root |
| `exhibit_plan.csv` | question-to-exhibit-to-source mapping |
| `artifact_binding.csv` | table/figure/equation/Word binding and checksums |
| `implementation_correspondence.md` | equations/pseudocode/code mapping |
| `complexity_analysis.md` | derived and measured resource costs |
| `cross_format_consistency.csv` | LaTeX/PDF/Word equality checks |
| `word_validation_report.md` | OOXML, OMML, fields, native tables, references |
| `revision_log.md` | review tickets, changes, and verification |
| `final_integrity_audit.md` | complete acceptance evidence and residual caveats |

## 3.2 Requirements and source-line traceability

Wherever this framework says "the updated prompt" or "the updated construction
brief", the referent IS this master file, `papers/PAPER_BUILD_PROMPT.md`,
unless a separate brief path is explicitly recorded in
`project_configuration.md` at Phase 0. Source-line classification therefore
targets this master file by default.

`requirements_traceability_matrix.csv` schema:

```text
requirement_id,source_document,source_line_start,source_line_end,
requirement_text,master_section,phase,implementation_artifact,
validation_method,verification_owner,status,notes
```

`source_line_traceability.csv` schema:

```text
source_document,source_line,line_text,line_classification,destination_section,
resolution,requirement_id,review_status,notes
```

Allowed line classifications are `integrated`, `superseded_by_later_requirement`,
`structural_heading`, `example_or_comment`, `duplicate`, and `nonoperative`. Every
nonblank source line MUST receive exactly one classification. A line classified
as superseded MUST name the conflicting later requirement and the section that
implements the resolution. A line classified as duplicate MUST point to the
retained requirement. No line may remain `unmapped`, `partial`, or `unknown` at
the final gate.

## 3.3 `reference_inventory.csv`

Required schema:

```text
citation_key,bib_title,bib_authors,bib_year,bib_venue,bib_doi,
source_file,source_title,source_authors,source_year,source_venue,source_doi,
format,page_count,source_checksum,identity_status,readability_status,
admissible,notes
```

Identity status is one of `verified`, `minor_metadata_mismatch`,
`major_mismatch`, `missing_source`, `unreadable`, or `duplicate`.
`format`, `page_count`, and `source_checksum` carry the Phase 1 file
inventory (Phase 1 task 2) so that checksum verification runs against this
inventory.

## 3.4 Evidence cards

Each evidence card MUST record:

- verified bibliographic identity;
- research question and context;
- method and experimental scope;
- conservative findings;
- limitations;
- exact page/section/table/figure locators for every usable claim;
- unsupported interpretations;
- relevance to DT-GSK; and
- brief verification quotations only when necessary.

Do not rely on an abstract when full text is available.

## 3.5 `claims_evidence_matrix.csv`

In addition to Section 2.6, every contribution bullet, abstract statement,
headline result, novelty statement, design rationale, method definition,
limitation, recommendation, conclusion, highlight, and cover-letter scientific
statement MUST have a row.

## 3.6 `evidence_gap_register.md`

For each gap, record:

- desired claim;
- reason it matters;
- closed-corpus sources checked;
- empirical artifacts checked;
- why support is insufficient;
- allowed disposition: omit, narrow, hypothesis, additional analysis,
  additional experiment, or blocked;
- affected sections and deliverables; and
- responsible phase.

Do not clutter the manuscript with repeated “evidence unavailable” sentences.
Usually omit or narrow; disclose the gap when it changes interpretation.

## 3.7 `citation_usage_map.csv`

Required schema:

```text
source_document,paragraph_or_label,citation_key,claim_id,
source_locator,support_type,semantic_check_status,reviewer_notes
```

## 3.8 Data and exhibit schemas

### Data ledger

```text
algorithm,algorithm_version,suite,suite_version,dimension,function_set,
n_runs,pairing_design,seed_policy,seed_schedule_path,max_fes,stopping_rule,
parameter_file,boundary_handling,evidence_release_id,raw_path,raw_checksum,
source_type,environment_id,fp_sentinel,commit_sha,completeness,
comparability_status,notes
```

### Experiment matrix

```text
algorithm,suite,dimension,function,run,seed,max_fes,config_hash,
raw_output_path,raw_checksum,status,failure_reason,wall_time,
objective_calls,commit_sha,environment_id,evidence_release_id
```

### Artifact binding

```text
artifact_id,artifact_path,artifact_type,manuscript_label,
generator_script,generator_command,source_paths,source_checksums,
analysis_id,evidence_release_id,commit_sha,output_checksum,scope,
latex_location,word_location,validation_status
```

### Revision ticket

```text
ticket_id,severity,reviewer,phase,section,claim_id,issue,
evidence_needed,action,owner,status,verification
```

### Exhibit plan

```text
exhibit_id,exhibit_type,research_question,claim_ids,
manuscript_location,main_or_supplement,generator_script,
generator_command,source_paths,evidence_release_id,status,notes
```

### Assumption register

```text
assumption_id,assumption,phase,affected_claims_or_artifacts,
verification_method,verification_status,sensitivity_plan,
disposition,notes
```

### Risk register

```text
risk_id,risk,probability,impact,owner,mitigation,residual_risk,
status,notes
```

### Phase gate register

```text
phase_id,phase_name,state,entry_evidence,validation_evidence,
acceptance_evidence,exit_evidence,gate_approvers,timestamp,notes
```

The `state` column uses the Section 12.2 state values.

### Cross-format consistency

```text
check_id,artifact_id,check_type,latex_value_or_hash,
pdf_value_or_hash,word_value_or_hash,match_status,resolution,notes
```

## 3.9 Audit-trail rule

Every phase MUST append to:

- `decision_log.md`;
- `risk_register.csv`;
- `phase_gate_register.csv`;
- `change_request_register.csv` whenever a frozen phase or artifact is
  reopened; and
- `reproducibility_manifest.json` when commands or artifacts change.
  (Both registers are initialized in Phase 0 task 3 so this rule is
  satisfiable from the first phase.)

No acceptance gate may rely on an undocumented manual judgment.

---

# 4. Expected repository and evidence inventory

The following paths and values are expected from the updated project brief.
They are audit targets, not permission to assume that the current checkout is
correct. Phase 0 and Phase 2 MUST verify every item.

## 4.1 Expected manuscript assets

Expected under `papers/`:

- `main.tex`, using the repository's journal class and including the section
  spine;
- `supplementary.tex` and `sections/supplementary_content.tex`;
- `references.bib`, expected to contain the 61 admitted locked entries of
  Appendix A, plus `yang2008large` and `zhong2023lmm` — two large-scale
  related-work entries that are present in the file but are **not** in the
  admitted set and MUST NOT be cited (63 BibTeX entries in total);
- source PDFs in `reference_papers/` at the repository root (a sibling of
  `papers/`, not inside it), expected to be named `<bibkey>.pdf`;
- macros for `\dtgsk` (the DT-GSK name macro), `\sgsm` (the ISM mechanism
  macro), algorithm names, `\bestval`, `\wmark`, `\lmark`, and `\emark`;
- table fragments `T01.tex` through `T16.tex` and `T16_bca.tex`, under
  `papers/tables/` (the former `T21.tex`/`T22.tex` were removed as prohibited —
  2026-07-15 status note);
- no `T17.tex` through `T20.tex` unless a future, documented numbering decision
  deliberately creates them; do not invent or renumber them merely to close the
  gap;
- generated ablation table fragments only after the final phase;
- figure directories `convergence/`, `diagrams/`, `flowchart/`, `ranks/`,
  `taxonomy/`, and `traces/`, under `papers/figures/`;
- journal class/support files such as `Definitions/mdpi.cls` and
  `Definitions/journalnames.tex` where present;
- `cover_letter.tex`; and
- companion phase files under `build_prompt_phases/`, which are examples only.

> **[2026-07-15 status note]** Three generators named in this framework were
> REMOVED by the post-freeze independent review (commit `16ce59439`):
> `generate_parametric_tables.py` (deleted together with the prohibited
> favorable component-ablation tables T21/T22 — never regenerate them),
> and `generate_flowchart.py` / `generate_taxonomy_figure.py` (their figures
> were converted to native tables; the DOCX flowcharts come from
> `build_visio_flowcharts.py`). Any instruction below that invokes these
> three is historical and MUST be skipped; the surviving generator set is
> the one in the root `runbook.md` Full Paper Pipeline.

Expected generator/build scripts include:

```text
papers/scripts/generate_latex_tables.py
papers/scripts/generate_t16_bca.py
papers/scripts/generate_full_convergence.py
papers/scripts/generate_cec2011_convergence.py
papers/scripts/generate_cec2013_convergence.py
papers/scripts/generate_nemenyi_cd.py
papers/scripts/generate_rank_charts.py
papers/scripts/generate_trace_figures.py
papers/scripts/generate_nlpsr_trajectory.py
papers/scripts/generate_adaptive_params_panel.py
papers/scripts/generate_ablation_matrix.py
papers/scripts/build_pdf.py
papers/scripts/build_supplementary.py
papers/scripts/generate_review_pack.py
papers/scripts/build_docx.py
```

Map emitted filenames by inspecting code. Never infer a generator solely from a
filename. `papers/scripts/build_docx.py` already exists in the repository; the
Phase 0/2 audit MUST map its current interface (its `main()` parses no CLI
arguments, so the `--supplementary` entry point expected by Appendix D.6 is not
yet supported) so its true state is recorded before Phase 9 depends on it.

## 4.2 Expected benchmark evaluator inventory

Expected evaluator/data roots:

```text
benchmarks/cec_suite_python/cec2011/
benchmarks/cec_suite_python/cec2013/
benchmarks/cec_suite_python/cec2013lsgo/
benchmarks/cec_suite_python/cec2017/
benchmarks/cec_suite_python/cec2020/
```

Evaluator code supports protocol verification and controlled reproduction. It
is not a substitute for immutable empirical evidence.

## 4.3 Expected immutable empirical layout

The expected flat layout per optimizer is:

```text
benchmarks/cec_reference_results/<suite>/<optimizer>/
  <opt>_<suite>_D<dim>.csv
  <opt>_cec2011.csv                       # CEC2011 rollup when applicable
  per_run.csv
  environment.json
  run_config.json
  seed_schedule.csv
  verification.json
  phase0_protocol.json
  curves/Figure_F<f>_D<d>_Run#<r>.csv
  gen_logs/CheckpointErrors_<opt>_F<f>_D<d>.csv
  gen_logs/GenLog_<opt>_F<f>_D<d>_Run<r>.csv   # optional per-generation
                                               # diagnostic bundle; present only
                                               # after Section 2.4 promotion
```

Expected seven-optimizer panel:

```text
gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk
```

Expected panel coverage:

| Suite | Expected algorithms | Expected dimensions | Expected runs | Expected function scope |
|---|---:|---|---:|---|
| CEC2017 | 7 | 10, 30, 50, 100 | 51 | F2 excluded; 29 functions |
| CEC2011 | 7 | native per problem | 25 | 22 problems |
| CEC2013 | 7 | 10, 30, 50 | 51 | 28 functions; no CEC2017-style exclusion |
| CEC2020 | partial/context | verify | verify | not a seven-method panel unless evidence proves otherwise |
| CEC2013-LSGO | partial/context | verify | verify | not a seven-method panel unless evidence proves otherwise |

Expected context-only optimizers may include `agsk` for CEC2020 and `decc-g`,
`mos` for CEC2013-LSGO. Do not promote a context suite to a formal panel without
complete comparable evidence.

Confirm there are no accidental nested paths such as:

```text
<suite>/<optimizer>/<suite>/
```

## 4.4 Expected working/staging layout

Working outputs may exist at:

```text
results/_run_all/<optimizer>/<suite>/
results/_run_all/_analysis/<suite>/
results/_ablation/<cell>/dt-gsk/<suite>/
results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv
results/paper_tables/
results/dt-gsk/sweeps/parametric-study/
configs/_ablation/<cell>.yml
```

These paths are not publication evidence. Use them only for staging,
independent reproduction, generator intermediates, or candidate ablation output
before controlled promotion.

`results/paper_tables/` is rendered-input staging for the table generators
(`generate_latex_tables.py`,
`generate_rank_charts.py`; historically also the since-removed
`generate_parametric_tables.py`). Nothing in the current toolchain produces it: it is
materialized by the named Phase 6 exporter task, which exports the T1–T16
(and, conditional on sensitivity admissibility, T21/T22) input CSVs from the
authoritative controlled analysis bundle (Section 7.13). Every exported CSV
MUST carry bundle provenance (release ID, source paths, checksums). The
directory may be absent before Phase 6; the Phase 0/2 audit records it as
`missing` without failing.

The parameter study is expected to have `n = 3`; it is sensitivity evidence,
not ablation evidence and not definitive performance evidence.
`results/dt-gsk/sweeps/parametric-study/` may be absent from the current
checkout, and no sweep-runner tooling exists in `scripts/`; Phase 0/2 MUST
therefore either locate the original sweep artifacts (or document their
historical provenance in `assumption_register.csv`) or record the sweep-runner
command/configuration needed to regenerate them before any T21/T22
regeneration is attempted. Because Section 2.1-E admits staging only after
controlled promotion, T21/T22 may carry parametric numbers only after the
sweep bundle is promoted via `scripts/promote_evidence.py` into a versioned
subtree, default `benchmarks/cec_reference_results/parametric/<release_id>/`,
before Phase 7 (mirroring the Phase 12.10 ablation pattern). If no validated
parametric release exists, T21/T22 are marked unavailable and the gap is
recorded in `evidence_gap_register.md`; `results/` staging is never read.

## 4.5 Expected protocol anchors

Verify rather than assume:

- seed formula:
  `get_cec_seed(20240620, dim, func, run) % 2147483646 + 1`;
- seed policy label: `unified`;
- CEC2017 floating-point sentinel prefix: `8bda40d8...`;
- suite-level sentinel consistency for CEC2011 and CEC2013;
- exact MaxFES and objective-call accounting;
- the `egsk` evidence provenance and whether it uses MATLAB `fmincon` or a local
  SciPy substitute;
- `per_run.csv` row counts and key uniqueness;
- all environment, run, seed, verification, and protocol files;
- no rendered PNG or log file is treated as raw numerical evidence; and
- imported and locally reproduced sources are never mixed inside one inferential
  exhibit.

## 4.6 Expected engineering gates

Locate and run the actual project commands. Expected forms are:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
python scripts\validate_profile_lock.py --root .
python scripts\build_docs_html.py
python run.py --root . --help
gsk-list --optimizers --benchmarks --references benchmarks/cec_reference_results
python -m gsk_family.cli.list
python -m gsk_family.cli.validate --references benchmarks/cec_reference_results
```

The updated project note expects 324 tests, but a hard-coded count is not a
scientific truth. Record the actual count and investigate any unexpected change.
A missing command is not a pass.

## 4.7 Conditional reproduction commands

The following commands are preserved as expected runbook forms for independent
reproduction or candidate evidence generation. They MUST NOT feed the paper
until the resulting bundle passes promotion into `cec_reference_results/`:

```powershell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 15 --convergence-graphs --overwrite
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2011 --function 1:22 --dimension native --runs 25 --parallel --workers 15 --convergence-graphs --overwrite
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --parallel --workers 15 --convergence-graphs --overwrite
```

Use fewer workers or serial execution when required by memory; never reduce run
count, MaxFES, or function scope to save time. Resume without `--overwrite` when
supported. Record every retry and failure.

Expected comparison command:

```powershell
python -m gsk_family.cli.validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

A local `egsk` implementation using SciPy must not silently replace committed
MATLAB/fmincon evidence in the publication panel.

## 4.8 Runbook rule

`runbook.md`, when present, is the copy-paste command source only after its
commands pass consistency review against this framework. A runbook command that
uses empirical fallback, runs ablation early, or writes directly over immutable
evidence MUST be corrected or wrapped before use.

---

# 5. DT-GSK scientific and implementation contract

## 5.1 Expected method spine

Verify the evaluated code for each expected component:

- inherited GSK junior and senior gaining–sharing phases;
- ACE knowledge control;
- nonlinear population-size reduction (NLPSR);
- budget-safe or stagnation escape (BSE), potentially using a Cauchy rescue;
- acceptance-gated pool pruning (ARGP);
- SGSM interaction-structure memory;
- linkage-aware block crossover;
- eigenframe-based final search or polish;
- Nelder–Mead endgame;
- archives, cadence, gates, boundary handling, and termination logic.

For each component determine:

1. whether it exists in the evaluated algorithm;
2. whether it is inherited, adapted, combined, or original;
3. exact inputs, state, initialization, update order, outputs, and reset logic;
4. parameters, defaults, ranges, and selection rationale;
5. objective-evaluation cost and non-evaluation overhead;
6. intended purpose, framed as a testable design rationale; and
7. the final-phase ablation or other direct evidence that tests it.

If code and prose disagree, the frozen executed code is authoritative for the
reported experiments. Correct the prose and record the discrepancy.

## 5.2 Contribution decomposition

Create `contribution_matrix.md`:

| ID | Category | Contribution | Inherited basis | Exact difference | Closest approved sources | Code location | Primary evidence | Final ablation evidence | Supported wording | Prohibited wording |
|---|---|---|---|---|---|---|---|---|---|---|

Categories:

- **Inherited** — used without a scientifically material change;
- **Modified** — an existing idea changed in a precisely specified way;
- **Original in this work** — not found in the reviewed closed corpus, with the
  novelty statement explicitly bounded to that corpus.

A new acronym is not a contribution.

## 5.3 Required positioning boundaries

- Position DT-GSK relative to the verified original GSK source.
- Compare SGSM with differential grouping only on supported dimensions:
  information source, objective-evaluation cost, update timing, granularity,
  and intended use.
- Compare linkage-aware crossover with eigenvector crossover only after
  mechanism-level verification.
- Compare eigenframe polish with covariance adaptation or direct search only at
  the conceptual level supported by approved sources.
- Do not imply equivalence among a support graph, covariance matrix,
  decomposition, and eigenbasis.
- Replace “learned for free” with the narrower verified statement “requires no
  additional objective evaluations” unless measured overhead supports a
  stronger claim.
- Do not call overhead negligible without measured evidence.
- Use exact dimensions instead of “high-dimensional” or “large-scale” when the
  literature and tested scope do not support those labels.
- A seven-method GSK-family panel supports family-scoped conclusions only.
- NFL may motivate adaptive bias but does not prove that DT-GSK should win.

## 5.4 Contribution acceptance test

Every contribution MUST pass:

1. **Definition** — precise and reimplementable;
2. **Distinction** — accurately separated from closest approved prior work;
3. **Implementation** — present in frozen evaluated code;
4. **Primary evidence** — supported by valid non-ablation benchmarking or
   implementation evidence where appropriate;
5. **Final ablation evidence** — directly tested in the final phase when the
   contribution concerns a component;
6. **Cost** — evaluation and non-evaluation cost accounted for; and
7. **Scope** — wording matches suites, dimensions, panel, and uncertainty.

A contribution that fails after the final ablation is removed or narrowed. The
algorithm is not modified to rescue the claim.

## 5.5 Mathematical and algorithmic completeness

Create:

- notation table;
- complete top-level pseudocode;
- mechanism-level pseudocode where needed;
- parameter table with default, range, source, and tuning status;
- equation registry;
- implementation correspondence map;
- complexity derivation;
- evaluation-accounting proof or test;
- deterministic trace/micro-test for update order; and
- algorithm freeze manifest.

Define unambiguously:

- objective, domain, bounds, and optimization direction;
- initialization and random variables;
- junior/senior phases and selection rules;
- parameter update timing;
- all memories, pools, archives, graph states, and initial values;
- SGSM representation, support update, smoothing/decay, confidence gate,
  thresholding, reset, and numerical safeguards;
- block construction and crossover semantics;
- eigenbasis construction, order/sign handling, cadence, degeneracy fallback,
  and cost;
- local-search trigger, budget, acceptance, and termination;
- stagnation and rescue definitions;
- ties, boundary repair, population reduction, and minimum size;
- objective-call accounting including local search and polish;
- stopping condition and returned solution; and
- deterministic behavior under a fixed seed to the supported extent.

## 5.6 Equation discipline

- Define every symbol before or at first use.
- Use one symbol per concept and state vector/matrix dimensions.
- State index ranges, counters, and random distributions.
- Distinguish equality, assignment, approximation, and sampling.
- State safeguards for division, normalization, graph degeneracy, and
  eigendecomposition.
- Ensure LaTeX equations, OMML equations, pseudocode, and code express the same
  update order.
- Do not add equations merely to appear formal.

## 5.7 Complexity and overhead

Expected claims such as `O(D^2)` memory and `O(D^3)` eigendecomposition are
hypotheses until derived from code. Report:

- time complexity by mechanism;
- memory complexity by persistent and temporary state (analytic derivation in
  `complexity_analysis.md`; measured peak memory is reported only when the
  optional pre-freeze measurement harness of Section 6.9 produced a validated
  cost record, otherwise the measurement gap is recorded in
  `evidence_gap_register.md`);
- cadence and amortized complexity;
- objective-evaluation cost;
- measured runtime from the admissible evidence (`per_run.csv`
  `runtime_seconds`), with non-objective overhead reported as measured only
  when a validated cost record separating it exists; otherwise report the
  derived overhead accounting and record the gap in
  `evidence_gap_register.md`;
- scaling with dimension and population size; and
- numerical library and hardware limitations.

All local-search and polish evaluations count toward MaxFES unless the verified
benchmark protocol explicitly states otherwise.

## 5.8 Algorithm freeze

Before primary analysis, create `algorithm_freeze_manifest.json` containing:

- commit SHA;
- source/config hashes;
- evaluator hashes;
- enabled components and parameters;
- seed policy;
- MaxFES accounting;
- known numerical dependencies; and
- tests proving the frozen profile.

After freeze, algorithm changes are permitted only through the Section 0.6
change-control process (formal change request in
`change_request_register.csv`, impact analysis, invalidation list) and
invalidate Phase 3 onward. Final-phase ablation toggles approved components
only; it does not change their implementation.

---

# 6. Benchmark, experimental, and provenance governance

## 6.1 Benchmark roles to verify and freeze

The expected study design is:

- **CEC2017** — primary family-comparison suite;
- **CEC2011** — real-world or applied benchmark suite;
- **CEC2013** — secondary comparison suite;
- **CEC2020** and **CEC2013-LSGO** — contextual only unless a complete,
  comparable panel exists in the selected evidence release.

These roles MUST be confirmed before analysis. A suite is not “independent
confirmation” or a “holdout” when it influenced algorithm design, parameter
selection, debugging, or stopping decisions. Use `secondary evidence` when
independence cannot be demonstrated.

## 6.2 Protocol verification matrix

For each suite × algorithm × dimension cell, verify:

- suite implementation and data hashes;
- objective definitions, shifts, rotations, optima, and bounds;
- function inclusion/exclusion rule;
- dimension set;
- run count;
- seed schedule and pairing key;
- initialization;
- boundary handling;
- MaxFES and all local-search/polish evaluation accounting;
- parameter configuration and tuning provenance;
- failure, timeout, and missing-data handling;
- floating-point sentinel and environment;
- raw/per-run completeness;
- convergence-checkpoint completeness; and
- immutable source checksum.

Expected anchors requiring confirmation:

| Suite | Functions/problems | Dimensions | Runs | Special rule |
|---|---:|---|---:|---|
| CEC2017 | 29 analyzed | 10, 30, 50, 100 | 51 | exclude F2 only if verified protocol requires it |
| CEC2011 | 22 | native | 25 | use native problem dimensions |
| CEC2013 | 28 | 10, 30, 50 | 51 | no CEC2017 F2 exclusion |

## 6.3 Comparator-fairness audit

Before any table or inferential test combines algorithms, verify:

- identical objective definitions and benchmark data;
- identical function sets and dimensions;
- identical or demonstrably equivalent evaluation budgets;
- matching endpoint/error definitions and numerical floors;
- compatible run and seed designs;
- valid pairing when paired tests are planned;
- comparable initialization, boundary handling, and failure policy;
- transparent parameter-tuning effort;
- objective-call accounting for all local-search operations;
- algorithm version and implementation provenance; and
- whether evidence is imported, locally reproduced, or independently verified.

Assign one status per comparison cell:

- `A — directly comparable, same frozen protocol, complete per-run evidence`;
- `B — directly comparable immutable imported evidence with verified protocol`;
- `C — descriptively comparable, not valid for the planned paired inference`;
- `D — non-comparable; exclude from formal comparison`.

Status C evidence may appear only in a clearly labeled descriptive context.
Status D evidence MUST not enter the manuscript's formal comparison.

## 6.4 Pairing and seed governance

- Verify that common seeds represent a meaningful pairing for each algorithm.
- A shared numeric seed is not automatically a valid pair when initialization,
  random-number consumption, or task definitions differ materially.
- Record the exact pairing key, normally suite × function × dimension × run.
- Do not pair summary means or medians as if they were raw run pairs.
- Do not treat repeated runs on one function as independent benchmark tasks.
- Preserve `seed_schedule.csv` and test uniqueness, cardinality, and formula.
- Never change the base seed or mix seed policies inside an exhibit.

## 6.5 Raw, derived, and rendered separation

Classify every artifact:

- **raw immutable evidence** — per-run final values, checkpoint logs, evaluator
  inputs, seeds, run metadata;
- **verified derived evidence** — summaries, ranks, tests, effects, intervals,
  curve aggregates produced by a recorded script from raw immutable evidence;
- **rendered artifacts** — LaTeX tables, Word tables, figures, PDFs, and prose.

Rendered artifacts never become a source for data regeneration. Derived values
must be reproducible from raw evidence. If multiple derived files contain the
same statistic, designate one authoritative output and test exact equality.

## 6.6 Strict evidence release manifest

Each selected empirical release MUST provide or be accompanied by a manifest —
the governance artifact `evidence_release_manifest.json` produced in Phase 2
and stored in the governance root — containing:

```text
release_id
creation_timestamp
supersedes_release_id
repository_commit
algorithm_hashes
evaluator_hashes
configuration_hashes
source_file_manifest
source_sha256
schema_version
seed_policy
suite_protocols
known_deviations
validation_commands
validation_results
write_protection_status
```

The selected release ID MUST appear in every data ledger row, analysis output,
caption provenance record, and final reproducibility statement.

The currently selected releases (2026-07-20) are primary
`rel-2026-07-20-67d9345f9` (anchor commit `67d9345f9`) and ablation
`abl-rel-2026-07-20`; the derived analysis bundle is
`papers/analysis/rel-2026-07-20-67d9345f9/`. These are the values that fill the
`<release_id>` placeholders throughout this framework. Superseded releases
(`rel-2026-07-16-78f075cb0`, `rel-2026-07-10-262fc16c9`, `abl-rel-2026-07-16`,
`abl-rel-2026-07-13`) may appear only in the `supersedes_release_id` provenance
chain, never as an active publication source.

## 6.7 Convergence evidence

- Use only curves and checkpoint logs in the selected immutable release.
- Verify checkpoint definitions and identical evaluation coordinates.
- Aggregate with a declared statistic and uncertainty band.
- Do not smooth away failures or unfavorable behavior.
- Do not extrapolate beyond a terminated run.
- Pre-specify the main-text curve selection rule before viewing final plots.
  The rule MUST be derived from summary statistics (for example median final
  error, rank position, or failure counts), not visual inspection, and the
  pre-registration record MUST document prior exposure to existing repository
  figures (unavoidable during the Phase 2 asset audit) as a known limitation
  of the pre-specification.
- The main-text representative subset MUST be chosen by pre-defined,
  summary-statistic-derived criteria covering the benchmark categories,
  easy/moderate/difficult cases, and cases where DT-GSK performs strongly,
  comparably, and weakly; the criteria are recorded before inspecting any
  rendered figure (CR-0003).
- Include at least one difficult or unfavorable case.
- Put complete function grids in the supplement.

**Family-overlay panel design (REQUIRED; CR-0001).** Every per-function
convergence panel MUST contain all seven GSK-family algorithms — one curve per
algorithm (`gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`, `egsk`,
`dt-gsk`) — at each pre-registered dimension, so the reader can directly
compare optimization behavior throughout the search. Rules:

- The default aggregation is the per-checkpoint **mean error across all runs**,
  computed from each optimizer's `gen_logs/CheckpointErrors_<opt>_F<f>_D<d>.csv`
  in the selected release — the same basis for all seven curves. Mixing
  aggregation bases across curves in one panel is prohibited unless disclosed
  in the caption.
- The frozen exhibit plan MAY instead pre-register the median best-so-far with
  an interquartile band (or the mean with a confidence band) when the run
  distribution justifies it; exactly one aggregation is chosen before
  rendering, applied to all seven curves in all panels, and documented (runs
  included, statistic, uncertainty representation, checkpoint alignment,
  missing-checkpoint and zero-value treatment, display-only log floor).
  Selecting a best or visually favorable run is prohibited (CR-0003).
- A representative-run fallback (from `curves/`) for an algorithm is permitted
  only when its checkpoint logs are absent from the release, and MUST be
  disclosed in the caption.
- A missing algorithm is reported as missing in the caption and the exhibit
  register — never fabricated, interpolated, or silently dropped.
- One fixed algorithm-to-color/linestyle map applies identically to every
  panel in the manuscript and supplement (Section 8.4).

Expected source patterns:

```text
curves/Figure_F<f>_D<d>_Run#<r>.csv
gen_logs/CheckpointErrors_<opt>_F<f>_D<d>.csv
gen_logs/GenLog_<opt>_F<f>_D<d>_Run<r>.csv   # diagnostic; only in a promoted
                                             # diagnostic release (Section 8.5)
```

## 6.8 Parameter sensitivity

Parameter sensitivity and ablation are separate studies.

- Label the expected three-run parameter study as exploratory sensitivity.
- State grid/range, tasks, dimensions, runs, seeds, metric, and selection rule.
- Disclose whether the same cases influenced final parameter choices.
- Do not use a three-run sweep as definitive evidence of robustness.
- Do not convert sensitivity results into component-causality claims.
- Include full sensitivity evidence in the supplement when scientifically
  useful; keep main-text treatment concise and non-promotional.

## 6.9 Computational cost study

The primary study SHOULD include a controlled cost analysis before final
ablation:

- objective-evaluation count and budget compliance;
- wall time under a fixed environment, from the admissible runtime evidence
  (`per_run.csv` `runtime_seconds`);
- non-objective overhead, as measured only when a validated cost record exists,
  otherwise as documented accounting with a gap entry;
- peak memory only when the OPTIONAL pre-freeze measurement harness below
  produced a validated cost record;
- cost by dimension and mechanism cadence;
- comparison limitations across languages or external solvers; and
- deterministic instrumentation overhead checks where instrumented
  measurements are used.

Peak-memory measurement is an OPTIONAL pre-freeze tooling task: a
tracemalloc/peak-RSS harness around a fixed repetition protocol (environment,
repetitions, and warm-up per Section 7.12), whose outputs are promoted into a
validated immutable cost record through the Section 2.4 process before use. If
the harness is not built before the analysis freeze, RQ7 and Sections 5.7,
6.9, and 7.12 report runtime and overhead only, and the memory measurement gap
is recorded in `evidence_gap_register.md`.

A wall-time comparison is invalid when hardware, language, parallelism,
termination, or objective-call counts differ materially. Runtime comparisons
MUST use measurements from comparable environments; values from incompatible
environments MUST NOT be compared without explicit qualification in both prose
and captions (CR-0003).

## 6.10 No early ablation

Before the final phase, the agent MAY:

- audit existing ablation scripts without executing them;
- execute `scripts/run_ablation.py --dry-run` before the final phase only
  after code inspection proves the `--dry-run` path performs zero objective
  evaluations (it only writes configuration files and prints paths); the
  authoritative dry-run generation is re-run and recorded after the signed
  Gate 11 (the pre-ablation hard gate) per task 12.7;
- verify toggle definitions and expected output schema;
- pre-register the final ablation design; and
- reserve compute resources.

Before the final phase, the agent MUST NOT:

- execute ablation objective evaluations;
- inspect existing unvalidated ablation outcomes to shape the primary paper;
- generate ablation tables, figures, claims, or prose;
- tune the algorithm based on ablation; or
- include ablation content in the main manuscript.

Existing historical ablation outputs under `results/` are quarantined from the
primary workflow. They may be archived or used only to test parsers with values
masked, not to determine the final design or claims.

---

# 7. Pre-registered statistical analysis plan

Create and freeze `statistical_analysis_plan.md` before interpreting primary
results. If analyses already exist, reconstruct the intended plan, identify
outcome-driven choices, and label any unavoidable post hoc analysis as
exploratory.

## 7.1 Research questions

Use a small, explicit set. The default primary questions are:

- **RQ1:** How does frozen DT-GSK compare with the verified GSK-family panel on
  the primary suite at each dimension?
- **RQ2:** Are observed differences statistically reliable under the declared
  unit of analysis and multiplicity family?
- **RQ3:** Are statistically reliable differences practically meaningful?
- **RQ4:** How does the result vary across dimensions, functions, and verified
  function classes?
- **RQ5:** What convergence behavior is visible under the pre-specified curve
  selection rule?
- **RQ6:** Does secondary-suite or real-world evidence support, qualify, or
  contradict the primary result?
- **RQ7:** What runtime cost and non-objective overhead accompany the method,
  based on the admissible runtime evidence (`per_run.csv` `runtime_seconds`)?
  Measured memory is answered only if the optional pre-freeze memory harness
  (Section 6.9) produced a validated cost record; otherwise memory is covered
  by the analytic derivation in `complexity_analysis.md` and a documented gap
  entry in `evidence_gap_register.md`.
- **RQ8:** How sensitive are conclusions to reasonable analysis choices?

Ablation research questions are pre-registered separately but answered only in
the final phase and only in the supplement.

## 7.2 Primary endpoint and estimands

Define before analysis:

- primary endpoint, normally final objective error under verified optimum
  subtraction;
- numerical floor and zero handling;
- transformation, if any;
- comparison estimand by suite and dimension;
- central tendency and dispersion;
- success threshold, if used, and its approved source;
- ranking direction;
- failure/timeout encoding;
- primary algorithm panel; and
- primary and secondary analysis families.

Do not average raw errors across heterogeneous functions unless the
transformation produces a defensible comparable scale.

## 7.3 Units of analysis and independence

For every analysis, state:

- observation unit;
- experimental unit;
- aggregation performed before testing;
- pairing key;
- independence assumptions;
- treatment of ties, zeros, failures, and missing observations;
- one- or two-sided alternative and rationale;
- number of observations; and
- correction family.

Avoid pseudoreplication. Run-level variability and across-function variability
answer different questions and MUST not be silently mixed.

## 7.4 Descriptive reporting

For each function × dimension × algorithm cell, retain at least:

- best;
- median;
- mean;
- worst;
- standard deviation;
- variance;
- interquartile range when raw runs permit;
- success rate and failure rate against the protocol target error (the 1e-8
  convention, as verified in the protocol audit) where per-run evidence
  defines them (CR-0003);
- failure count; and
- run count.

Every descriptive statistic is computed only from admissible evidence. The
primary ranking statistic MUST be named and justified in the frozen analysis
plan (CR-0003).

Use unrounded values for ranks, tests, and tie decisions. Apply display rounding
only after calculations and store the formatting policy.

## 7.5 Omnibus comparison

When design assumptions hold:

1. compute per-task algorithm ranks using the frozen primary endpoint;
2. apply the Friedman test for the declared task unit;
3. report statistic, degrees of freedom where applicable, observation count,
   and p-value precision;
4. use a Nemenyi critical-difference diagram only when its design matches the
   actual algorithms and tasks; and
5. ensure narrative claims follow formal inference, not visual rank order alone.

The frozen plan MAY pre-register the Iman–Davenport F-distribution correction
as the refinement of the Friedman test; when pre-registered, it is reported
alongside the Friedman statistic (CR-0003).

Do not pool dimensions into one omnibus test unless the estimand and weighting
are pre-specified and defensible.

## 7.6 Pairwise comparisons and multiplicity

- Use Wilcoxon signed-rank only for valid paired observations.
- Define the primary family, normally DT-GSK versus each comparator within one
  suite and dimension.
- Use Holm adjustment for primary family-wise error control when supported by
  the approved corpus.
- Report raw p-value, adjusted p-value, test statistic, direction, observation
  count, and tie/zero method.
- Do not report `p = 0`; use a bound or software precision.
- Benjamini–Hochberg MAY appear only as a distinctly labeled exploratory FDR
  analysis with a separate family and interpretation.
- Never mix Holm and BH results inside one claim.

## 7.7 Effect size and uncertainty

- Report Vargha–Delaney A12 with groups and direction defined.
- Rank-biserial correlation and Cliff's delta are sanctioned alternative or
  companion nonparametric effect sizes to A12; the frozen plan names which
  measures are reported (CR-0003).
- State explicit interpretation thresholds for whichever effect-size measures
  are frozen, in the plan and before analysis (CR-0003).
- Avoid qualitative effect labels unless supported by the local source and
  appropriate to the design.
- Attach an uncertainty interval to every headline effect.
- For BCa bootstrap intervals, state statistic, resampling unit, hierarchy,
  number of resamples, seed, confidence level, and failure handling.
- Use a deterministic analysis RNG. The current repository default, to be
  verified by inspection of `papers/scripts/generate_t16_bca.py`, is a
  per-cell derivation `np.random.default_rng(20260422 + dim * 7 + i)` from
  `BASE_SEED = 20260422`; the frozen plan MUST record whatever seed scheme the
  actual generator uses after inspection. Do not confuse this analysis seed
  with the experiment run-seed base `20240620`.
- Do not bootstrap individual runs when the claim concerns variation across
  benchmark functions unless the hierarchy is explicitly modeled.

## 7.8 Win/tie/loss and rankings

Define:

- whether counts use final means, medians, or paired test decisions;
- numerical and statistical tie rules;
- whether correction is applied before a win/loss mark;
- the function set denominator; and
- treatment of missing/non-comparable cases.

Never infer significance from a win/tie/loss count unless the count is defined
by the inferential test.

## 7.9 Convergence analysis

- Use identical checkpoints or a documented alignment method.
- Pre-register representative cases in `curve_selection.csv` before rendering.
- Include one hard/adverse case.
- State aggregation and uncertainty.
- Separate descriptive convergence shape from causal mechanism explanation.
- Do not select the best-looking run or function.

## 7.10 Function-class analysis

A function-class analysis is permitted only when:

- the class labels are verified from an approved benchmark source;
- class definitions are not reconstructed from memory;
- the analysis was pre-specified or labeled exploratory;
- multiplicity is addressed; and
- small class sizes are acknowledged.

Do not claim a mechanism “works because of” a class-level pattern without direct
evidence.

## 7.11 Robustness checks

Where admissible evidence permits, pre-specify checks for:

- mean versus median summaries;
- error floor and log transform;
- failed-run encoding;
- exclusion of disputed comparator cells;
- pairing assumptions;
- function influence or leave-one-function-out ranks;
- correction-family definition;
- secondary-suite inclusion; and
- dimension aggregation.

A headline conclusion that reverses under a reasonable choice MUST be reported
as unstable.

## 7.12 Primary cost analysis

Pre-specify:

- environment and repetition count;
- warm-up policy;
- objective-cost normalization;
- wall-time metric (from `per_run.csv` `runtime_seconds`);
- memory metric only if the optional Section 6.9 measurement harness exists
  before the analysis freeze; otherwise pre-specify the analytic memory
  derivation and the `evidence_gap_register.md` entry instead;
- dimensions/tasks;
- confidence interval; and
- invalid cross-language comparisons.

## 7.13 Primary analysis commands

Expected project commands are preserved, but they MUST be executed in strict
reference-only mode and write derived results to the controlled analysis area.
The controlled analysis area is the analysis bundle root
`papers/analysis/<release_id>/`, recorded in `project_configuration.md` at
Phase 0. Every `gsk_family.cli.stats` command in this framework carries
`--out papers/analysis/<release_id>/<suite>/` so publication analyses never
default into `results/_run_all/_analysis/`:

```powershell
python -m gsk_family.cli.stats --suite CEC2017 --dims 10,30,50,100 --out papers/analysis/<release_id>/cec2017/
python -m gsk_family.cli.stats --suite CEC2011 --out papers/analysis/<release_id>/cec2011/
python -m gsk_family.cli.stats --suite CEC2013 --dims 10,30,50 --out papers/analysis/<release_id>/cec2013/
```

Before use, verify or implement a guard proving that every empirical source path
belongs to the selected `cec_reference_results` release. The expected loader
locations include `src/gsk_family/analysis/result_loader.py::load_algorithm`
and `src/gsk_family/analysis/family_report.py` (entry point
`generate_family_report`); inspect actual paths.

Expected outputs may include:

```text
<suite>_statistical_report.txt
<suite>_friedman_ranks.csv
<suite>_friedman_ranks.tex
<suite>_wilcoxon_summary.tex
figures/
```

These derived outputs remain working artifacts until their inputs, commands,
checksums, and release ID are bound in the governance package. Publication
numbers must still trace to immutable source data.

## 7.14 Statistical output bundle

Every reported statistic MUST have a machine-readable row in
`primary_stats/statistical_results.csv`, written inside the controlled
analysis bundle (Section 7.13) and listed in the Section 3.1 governance table.
The Phase 6 orphan check audits this file. Row schema:

```text
analysis_id,rq_id,suite,dimension,function_set,algorithms,metric,
unit_of_analysis,n_observations,pairing_key,test,test_statistic,
p_raw,p_adjusted,correction,effect_size,effect_direction,
ci_low,ci_high,ci_level,resampling_unit,n_resamples,seed,
source_paths,source_checksums,evidence_release_id,script,command,
commit_sha,interpretation,status
```

No statistic may exist only in prose, a LaTeX fragment, a Word table, or a plot.

## 7.15 Analysis freeze and post hoc control

After the plan is frozen:

- changes require a revision entry with rationale and affected claims;
- outcome-driven changes are exploratory;
- primary and exploratory results must be separated;
- all code and parameters are versioned; and
- deterministic rerun-and-diff checks are mandatory for critical outputs.

---

# 8. Exhibits, visualization, and manuscript architecture

## 8.1 General exhibit rules

Every table, figure, diagram, flowchart, and algorithm block MUST:

- answer a named research or explanatory question;
- be generated from a named source or be explicitly classified as authored
  conceptual art;
- have a generator, command, source paths, checksums, release ID, and output
  checksum;
- be discussed at the correct location;
- have a self-contained caption;
- agree with prose, LaTeX, Word, and the claims matrix;
- remain legible at final publication size; and
- avoid redundant presentation of the same evidence.

Never hand-edit a data-backed number or plotted point.

## 8.2 Main-text table set

The main manuscript may include:

- protocol/comparator summary;
- compact per-dimension primary performance summaries;
- ranks and win/tie/loss summaries with exact definitions;
- primary adjusted pairwise results with effect sizes and intervals;
- a compact secondary-suite summary;
- parameter sensitivity only at an appropriately modest level; and
- computational overhead summary.

The main manuscript MUST NOT contain an ablation table.

Full per-function tables, complete pairwise matrices, full convergence grids,
large sensitivity grids, and all ablation evidence belong in the supplement.

## 8.3 Table formatting

- State statistic and dispersion explicitly.
- State minimization/maximization direction.
- Define bolding, significance, effect, win/tie/loss, imported evidence, and
  missingness symbols.
- Use unrounded values for decisions.
- Do not bold rounded ties incorrectly.
- Do not mark significance from unadjusted values when adjusted inference is
  claimed.
- Distinguish exact zero from below-precision values.
- Include run count and function denominator where needed.
- Preserve a machine-readable source for every table.

Expected LaTeX macros such as `\bestval`, `\wmark`, `\lmark`, and
`\emark` must be audited before use.

## 8.4 Figures

Expected useful families:

- method architecture/data-flow diagram;
- related-work taxonomy;
- Nemenyi critical-difference diagram when justified;
- representative convergence panels, including a hard case — every panel in
  the seven-curve family-overlay format of Section 6.7, with one fixed
  algorithm-to-color/linestyle map used identically across all panels and a
  single shared legend per grid;
- rank summaries;
- parameter-sensitivity visualization;
- SGSM/trace diagnostics when they explain behavior; and
- final-phase ablation effects in the supplement only.

Additional analysis figure families MAY be produced where the frozen exhibit
plan justifies them from admissible evidence (CR-0003): boxplots or violin
plots of final-error distributions; heatmaps (for example rank-by-function);
average-rank plots; performance profiles and data profiles; success-rate
plots; scalability/dimension-scaling plots; error-distribution plots; and
effect-size plots. Radar charts appear only when they add genuine analytical
value without distorting interpretation. Decorative visualizations MUST NOT
substitute for statistically meaningful analyses; every optional figure binds
to the same evidence, traceability, and QA rules as required figures.

Requirements:

- vector output where practical;
- embedded fonts (CR-0003);
- stable deterministic filenames (CR-0003);
- publication-size labels;
- accessible palette and non-color encodings;
- consistent marker styles (CR-0003);
- consistent algorithm ordering in legends (CR-0003);
- grayscale distinguishability;
- no misleading truncated axes;
- uncertainty where appropriate;
- identical scales for comparable panels;
- explicit log-scale and zero handling;
- no decorative 3-D effects;
- captions stating suite, dimension, metric, aggregation, run count, and
  uncertainty; and
- source scripts and data included in the reproducibility package.

## 8.5 Expected non-ablation generators

Expected commands, to be verified against the runbook and strict source guard:

```powershell
python papers/scripts/generate_latex_tables.py
python papers/scripts/generate_t16_bca.py
python papers/scripts/generate_full_convergence.py
python papers/scripts/generate_cec2011_convergence.py
python papers/scripts/generate_cec2013_convergence.py --dimension 30
python papers/scripts/generate_nemenyi_cd.py
python papers/scripts/generate_rank_charts.py
python papers/scripts/generate_trace_figures.py
python papers/scripts/generate_nlpsr_trajectory.py
python papers/scripts/generate_adaptive_params_panel.py
```

(The former `generate_parametric_tables.py` / `generate_flowchart.py` /
`generate_taxonomy_figure.py` steps are retired — 2026-07-15 status note,
Section 7.)

Any generator that reads `results/` as empirical input MUST be changed or
wrapped to read the selected immutable release. Conceptual-art generators may
read authored specifications but no unverified result values.

**Family-overlay tooling task (CR-0001).** The three per-suite convergence
generators (`generate_full_convergence.py`, `generate_cec2011_convergence.py`,
`generate_cec2013_convergence.py`) currently render two-series panels (GSK vs
DT-GSK). Before Phase 7 rendering, a named tooling task MUST extend them (or
introduce a shared `generate_family_convergence.py`) to the seven-curve
family-overlay design of Section 6.7, computing each algorithm's per-checkpoint
mean across runs from the release's `CheckpointErrors` logs.
`papers/scripts/generate_review_pack.py` already implements seven-algorithm
overlay grids and is the reference implementation pattern (including its
log-missing-never-fabricate behavior). Phase 7 validation MUST assert that
every rendered convergence panel contains exactly seven series or a disclosed
caption-level absence note.

The required CEC2013 convergence scope is D30, matching the commanded
invocation above; CEC2013 evidence also covers D10 and D50, but
`generate_cec2013_convergence.py` writes dimension-less output filenames
(`cec2013_{a..d}.pdf`), so a second run at another dimension silently
overwrites the D30 grids. If more than D30 is required by the frozen exhibit
plan, a tooling task MUST first extend the script to embed the dimension in
its output filenames, and the extra invocations MUST be recorded.

`generate_trace_figures.py` and `generate_adaptive_params_panel.py` consume
per-generation `GenLog_*` diagnostic logs that exist only in `results/`
staging; the immutable release contains none. These two generators MAY run
only against a validated diagnostic release: regenerate the GenLog bundle with
frozen code (`run.py --gen-logs`) and promote it through the Section 2.4
process (via `scripts/promote_evidence.py`) into a versioned release subtree
matching the `gen_logs/GenLog_<opt>_F<f>_D<d>_Run<r>.csv` pattern of Sections
4.3 and 6.7, as a Phase 2 task or Phase 7 prerequisite. If no validated
diagnostic release exists, the SGSM/trace diagnostic figures are marked
unavailable and the gap is recorded in `evidence_gap_register.md`.

## 8.6 Main/supplement split

The main paper MUST independently support its central conclusion without
ablation. The supplement contains:

- complete per-function tables for all claimed suites and dimensions;
- complete pairwise matrices;
- full per-function convergence grids for the dimension set pre-registered in
  the exhibit plan, every panel in the seven-curve family-overlay format of
  Section 6.7 (CEC2013 defaults to D30 unless the plan and the tooling
  extension of Section 8.5 support more) — the complete per-function
  collection, all seven curves per figure, consistent ordering and styling,
  and a navigable function-by-function organization; vector output (PDF) is
  primary, with high-resolution PNG alternates where the journal requires
  (CR-0003);
- full parameter-sensitivity evidence;
- detailed reproducibility appendix;
- extended method traces and derivations;
- final-phase ablation design, raw-result index, summaries, inferential tests,
  convergence, overhead, sensitivity, and interpretation; and
- proof sketches when used.

**Default-to-supplement rule.** Any material that is not essential to judging
the paper's central claims — extended tables, additional figures, detailed
derivations, comprehensive experimental results beyond the headline exhibits,
and supporting analyses — defaults to the Supplementary Materials. The main
text retains only the concise, reviewer-facing core: the headline summary
tables, the critical-difference figure, representative convergence evidence,
the method definition, and the primary inference. When the Section 1.5 page
limit binds, migration to the supplement is the only permitted relief valve.

Two guards bound this rule in both directions:

- Contrary primary results must not be hidden in the supplement. Ablation is in
  the supplement because of the explicit project requirement, not because
  adverse results may be concealed.
- No result that the main text's conclusion depends on may exist only in the
  supplement; every conclusion-critical number appears (at least in summary
  form) in the main text.

## 8.7 Manuscript section architecture

Use the target journal's required headings while preserving this scientific
logic:

1. Title
2. Abstract
3. Introduction
4. Related work
5. Problem formulation and baseline GSK
6. Proposed DT-GSK method
7. Experimental setup
8. Primary results
9. Discussion
10. Limitations and threats to validity
11. Conclusion
12. Declarations and availability
13. References

Ablation is absent from the main sequence.

**Presentation exemplars and Q1 calibration (CR-0002, CR-0003).** The
manuscript's structure and presentation are calibrated against three named
exemplars from the closed corpus, all present in `reference_papers/`:

- `mohamed2020gaining` — the original GSK paper (Int. J. Machine Learning &
  Cybernetics, 2020): the family's thematic arc, empirical density, and
  per-dimension reporting conventions;
- `alfadli2025atmals` — ATMALS-GSK (Algorithms, 2025): the family's most recent
  Q-journal presentation, including its table layouts (Best/Median/Worst/
  Mean/SD with best-in-row bolding), Wilcoxon `+/=/-` summary conventions,
  convergence-figure styling, and adaptive-parameter study framing; and
- `jawad2024egsk` — the eGSK paper ("Enhanced Gaining-Sharing Knowledge-Based
  Algorithm for Global Optimization"): the family's most recent journal-style
  presentation of an enhanced GSK variant; its venue metadata follows the
  Phase 1 evidence card (the corpus record is a preprint/in-press entry) and
  is never invented (CR-0003).

Requirements:

- The Phase 4 register task (task 12) performs a **structured comparative
  review of all three exemplars** (CR-0003), recorded in the
  presentation-conventions register
  (`papers/governance/presentation_conventions.md`) and covering at least:
  paper structure; section ordering; introduction strategy; research-gap
  formulation; contribution presentation; literature-review organization;
  algorithm explanation; mathematical notation; pseudocode design; parameter
  documentation; experimental setup; benchmark reporting; statistical
  testing; table density and readability; convergence-plot design; figure
  placement; discussion depth; limitations; reproducibility;
  supplementary-material usage; conclusion structure; and overall visual and
  editorial quality. For each dimension the register records each exemplar's
  practice, the adopted best practice, and any weakness to avoid (overcrowded
  tables, repetitive text, weak interpretation, inconsistent notation,
  underspecified experiments, excessive visual density, unsupported claims).
  Exemplars are calibration references, never content templates: no
  mechanical copying; combine the strongest practices and improve where
  justified.
- Beyond the three named exemplars, the register SHOULD incorporate presentation
  best practices observable in the closed corpus's other leading venue papers
  (for example `apgsk2021` in IEEE Access, `tanabe2014improving`,
  `hansen2001cmaes`, `demsar2006statistical` for statistical reporting) —
  conventions are derived only from corpus documents, never from remembered
  or external style claims.
- The manuscript plan (Phase 4) maps every main-text section to the exemplar
  convention it follows, or records a deliberate, justified improvement.
  Deviations without recorded justification fail the Phase 10 editorial
  review.
- The quality bar is explicit: professionalism, clarity, mathematical
  presentation, and exhibit design comparable to the strongest papers in the
  evolutionary-computation and metaheuristic-optimization literature as
  represented in the corpus — enforced through the Phase 10 exemplar-parity
  editorial check (Section 14 rubrics), not asserted.

## 8.8 Title

The title MUST:

- name DT-GSK and the central verified mechanism;
- avoid unsupported superlatives;
- avoid “large-scale,” “high-dimensional,” “efficient,” “robust,” and
  “state-of-the-art” unless directly supported; and
- remain accurate when read with only the tested suites and dimensions.

## 8.9 Abstract

Default ceiling: 250 words, subject to current journal rules.

Include:

- problem and precise gap;
- central mechanism;
- verified evaluation scope;
- one or two primary numerical results with exact scope and uncertainty where
  concise;
- an important boundary where needed; and
- concise reproducibility/data availability.

Do not include ablation, citations when prohibited, every mechanism, or a
number without an accepted claim row.

## 8.10 Introduction

Include:

- evidence-backed real-parameter optimization context;
- verified GSK description;
- specific limitation addressed, not a generic difficulty statement;
- online interaction-structure rationale framed as a hypothesis until tested;
- bounded literature gap;
- three to five contribution bullets, each with evidence; and
- roadmap.

The expected limitation set may include fixed parameters, absent local search,
weak stagnation recovery, and absent linkage awareness, but each must be
verified and fairly worded.

The manuscript follows an explicit scientific narrative arc (CR-0003): define
the problem; establish why it matters; identify the limitations of existing
GSK-family methods; formulate the research gap; present DT-GSK as the
motivated response; explain the method rigorously; validate it experimentally;
interpret the results critically; state limitations honestly; and close with
an unexaggerated contribution statement. The introduction states the research
questions (Section 7.1) or hypotheses explicitly and presents contributions as
evidence-based.

## 8.11 Related work

Organize by relationship:

1. GSK and verified family variants;
2. adaptive population/operator control;
3. structure-aware optimization, differential grouping, eigenvector operators,
   and covariance adaptation;
4. local search/endgame refinement;
5. benchmark and statistical practice.

For every source, explain its role. Avoid chronology-only catalogues and claims
of exhaustive coverage.

## 8.12 Problem formulation and baseline GSK

Separate inherited GSK mechanics from the proposed extension. Define the
optimization problem, notation, bounds, objective, and minimum inherited
operators needed to understand DT-GSK. Cite the verified original GSK source.

## 8.13 Proposed method

For each mechanism use:

```text
problem addressed → design rationale → formal mechanism → update timing →
evaluation accounting → computational cost → expected behavior → planned test
```

Include inherited/modified/original labels, complete SGSM definition,
interactions among scaffold components, pseudocode, parameters, safeguards,
complexity, and code correspondence. Do not report final ablation results.

## 8.14 Experimental setup

State:

- research questions and primary endpoint;
- evidence release ID;
- suites, functions, dimensions, and exact run counts;
- seed formula and pairing;
- bounds, initialization, boundary handling, and MaxFES;
- algorithm panel and versions;
- parameter sources and tuning budget;
- environment and floating-point regime;
- failure handling;
- strict reference-only data rule;
- statistical plan and correction families;
- per-function versus per-run resolution by exhibit; and
- code/data availability.

Explicitly explain why a same-family panel is a controlled scope rather than a
field-wide competitiveness claim.

## 8.15 Primary results

Recommended order:

1. evidence completeness and protocol verification;
2. primary-suite performance;
3. omnibus and pairwise inference;
4. effect sizes and intervals;
5. convergence behavior;
6. secondary-suite and real-world evidence;
7. parameter sensitivity;
8. computational overhead;
9. robustness checks.

For each subsection: state the question, identify the evidence, report the
measurement, interpret conservatively, and state an exception or limitation.
Do not narrate every table cell.

## 8.16 Discussion

Address:

- what primary evidence suggests about interaction-structure memory;
- alternative explanations;
- dimension/function concentration;
- same-family panel limits;
- development/tuning bias;
- imported evidence comparability;
- time and memory trade-offs;
- external validity; and
- analysis-choice sensitivity.

A mechanism explanation inferred only from performance curves remains a
hypothesis until final ablation or direct diagnostic evidence supports it.

## 8.17 Limitations and threats to validity

Include a visible section considering:

- closed and potentially incomplete literature corpus;
- benchmark scope and limited real-world evidence;
- tested dimensions;
- baseline scope;
- tuning leakage;
- comparator implementation differences;
- stochastic variability and power;
- multiplicity and analytical flexibility;
- absence of main-manuscript ablation evidence;
- computational overhead; and
- hardware/numerical reproducibility.

Do not dilute candid limitations with promotional counterclaims.

## 8.18 Conclusion

Restate only primary evidence established before final ablation. Tie conclusions
to tested scope and contributions. Do not introduce new results, citations, or
mechanisms. Final ablation outcomes remain in the supplement and may cause a
main-text claim to be narrowed during the final-phase correction exception, but
they do not become main-text evidence.

## 8.19 Declarations

Prepare current journal-required declarations using verified information only:

- data/code availability;
- funding;
- conflicts of interest;
- author contributions;
- ethics statements where applicable;
- tool/generative-AI disclosure where required;
- acknowledgments; and
- anonymization statements.

---

# 9. Dual-format LaTeX, PDF, and Microsoft Word production

## 9.1 Canonical content model

Maintain one semantic manuscript model and two renderings. The LaTeX and Word
files MUST NOT evolve as independent manuscripts.

At minimum maintain registries for:

- paragraph/claim IDs (`claims_evidence_matrix.csv`);
- equation IDs (the equation registry, Section 5.5);
- table, figure, and algorithm IDs and cross-reference labels
  (`artifact_binding.csv` and `word/field_registry.csv`); and
- citation keys (`citation_usage_map.csv` and `allowed_citation_keys.txt`).

Section IDs, captions, footnotes, and supplementary identifiers are tracked
through the canonical content model and the existing registry columns
(`manuscript_label`, `latex_location`, `word_location` in
`artifact_binding.csv`; field IDs in `word/field_registry.csv`), not through
additional separate registry files.

Every content change is made in the canonical source or synchronized through a
recorded transformation. After each build, run cross-format consistency checks.

## 9.2 LaTeX and PDF requirements

- Use the verified target-journal class/template.
- Build from a clean state.
- Use vector figures where accepted.
- Resolve undefined references/citations, missing files, harmful overfull boxes,
  broken links, and font substitution.
- Embed required fonts according to journal rules.
- Verify metadata, bookmarks, accessibility options where supported, and PDF
  page rendering.
- Inspect every page visually at 100% and print-scale zoom.
- Preserve source, class files, bibliography, figures, and build command.

Expected build commands, subject to repository verification:

```powershell
python papers/scripts/build_pdf.py
python papers/scripts/build_supplementary.py
python papers/scripts/generate_review_pack.py
```

## 9.3 Word manuscript requirement

The `.docx` manuscript MUST be fully editable and suitable for direct journal
submission with little or no manual repair.

### 9.3.1 Native OMML mathematics

Every displayed and inline equation MUST use native Office Math Markup Language
(OMML):

- `m:oMath` for inline equations;
- `m:oMathPara` for displayed equations;
- native equation characters, fractions, roots, scripts, matrices, operators,
  accents, and delimiters;
- editable equation content in Microsoft Word Equation Editor.

Equations MUST NOT be inserted as PNG, JPEG, SVG snapshots, PDF objects,
OLE objects, screenshots, or flattened text.

The validation process MUST inspect the DOCX package and prove:

- every equation registry ID has an OMML element;
- no equation image placeholder exists;
- equation text and structure match the LaTeX source;
- symbols, indices, matrices, and numbering are consistent; and
- equations remain editable after open-save-open testing.

### 9.3.2 Equation numbering and references

- Use native Word `SEQ Equation` fields or an equivalent journal-compatible
  field mechanism.
- Use `REF` fields for equation cross-references.
- Keep equation labels in the field registry.
- Ensure field codes are not converted to static text.
- Set document update-on-open behavior where appropriate and verify an update
  does not corrupt numbering.

### 9.3.3 Native Word tables

Every manuscript table MUST be a native `w:tbl` Word table:

- editable cells and text;
- no table screenshots or embedded PDFs;
- proper header rows and repeat-header properties where useful;
- accessible reading order;
- native footnotes/notes where supported;
- consistent decimal alignment and scientific notation;
- no merged-cell design that prevents journal editing unless necessary; and
- dimensions appropriate for the target page size.

Verify that the value in every Word cell equals the authoritative machine-
readable table source.

### 9.3.4 Figures and captions

- Embed publication-quality vector graphics when Word and the journal support
  them; otherwise use journal-compliant high-resolution raster output.
- Captions MUST remain editable Word paragraphs using the journal's caption
  style.
- Figure and table numbering MUST use `SEQ` fields.
- Cross-references MUST use `REF` fields.
- Alt text MUST be added where required or useful.
- No caption may be baked into the image.

### 9.3.5 Editable diagrams and flowcharts

Method diagrams and flowcharts SHOULD use native Word DrawingML shapes,
connectors, and grouped objects, or SmartArt when it preserves the intended
layout. When native construction is impractical:

- embed a vector rendering in Word;
- include the editable `.drawio`, `.pptx`, or equivalent source;
- preserve labels as editable objects in the source;
- include fonts and style instructions without distributing proprietary font
  files; and
- verify consistency between embedded rendering and editable source.

### 9.3.6 Automatic section and object numbering

Use Word styles and multilevel lists for section numbering. Use fields for:

- sections/subsections when the template requires numbering;
- figures;
- tables;
- algorithms;
- equations;
- appendices and supplementary objects.

Manual typed numbering is prohibited where Word supports an automatic field or
style mechanism.

### 9.3.7 Table of contents and lists

The following MUST be native and updateable:

- table of contents;
- list of figures;
- list of tables;
- list of algorithms when required; and
- list of abbreviations when used.

Set appropriate heading/caption styles and verify field updates after document
reopening.

### 9.3.8 Native citations and bibliography

The Word version MUST preserve automatically updateable citations and
bibliography. Preferred compliant approaches are:

1. native Word `CITATION` fields plus a valid Word bibliography source store in
   `customXml/`, with a native `BIBLIOGRAPHY` field; or
2. journal-accepted dynamic Zotero, EndNote, or Mendeley fields, with the source
   library and conversion instructions included.

Flattened citation text is not acceptable when the requirement is an editable,
automatically updateable bibliography. The pipeline MUST verify:

- every rendered citation key maps to a verified local source;
- field tags are unique and stable;
- bibliography entries agree with `references.bib`;
- citation order/style matches the target journal;
- fields update without losing content; and
- no citation is converted to an image or static object.

### 9.3.9 Word package validation

Inspect the unzipped DOCX OOXML and report at least:

```text
count(m:oMath)
count(m:oMathPara)
count(w:tbl)
count(SEQ fields by type)
count(REF fields)
count(CITATION fields)
count(BIBLIOGRAPHY fields)
TOC field presence
LOF/LOT field presence
customXml bibliography source presence
broken bookmark count
missing relationship count
embedded image inventory
alt-text coverage
updateFields setting
```

Also perform visual inspection in Microsoft Word when available. LibreOffice or
other renderers may be used for secondary compatibility checks but do not prove
native Word behavior.

## 9.4 Cross-format consistency

For every main and supplementary artifact, verify that LaTeX/PDF and Word agree
on:

- title, authors, affiliations, abstract, keywords;
- section order and wording;
- equations and numbering;
- algorithms and pseudocode;
- table values and notes;
- figures and captions;
- citations and bibliography;
- cross-references;
- benchmark scope, runs, dimensions, and panel;
- headline statistics;
- limitations and availability statements; and
- supplementary pointers.

Any divergence blocks the phase gate.

**Reproducibility levels (CR-0003).** The determinism contract distinguishes
three reproducibility levels:

1. analytical — identical numbers and statistics;
2. visual — identical rendered content; and
3. byte-for-byte — identical files after timestamp normalization.

Rebuilding twice from the same immutable release, environment, and
configuration MUST achieve analytical reproducibility everywhere and visual
reproducibility for all exhibits, and byte-for-byte reproducibility wherever
the normalization defined in this section (Phase 9 determinism contract:
`SOURCE_DATE_EPOCH` set, PDF and DOCX timestamp metadata normalized) applies.
The achieved level per artifact class is recorded in
`reproducibility_manifest.json`.

## 9.5 Word source strategy

The preferred strategy is a deterministic generator from the canonical content
model using a verified `reference.docx`, OOXML-aware filters, and post-build
validators. A PDF-to-Word conversion is prohibited. A LaTeX-to-Word converter
is acceptable only when OMML, fields, tables, citations, and cross-references
pass the native OOXML checks.

The expected Word entry points are those of Appendix D.6 (`build_docx.py`,
`build_docx.py --supplementary`, `validate_docx.py`,
`validate_cross_format_parity.py`, `validate_evidence_bindings.py`). The
existing pandoc-based `papers/scripts/build_docx.py` is a non-compliant
starting point under this section's own converter-acceptability rule: it emits
no SEQ/REF/CITATION/BIBLIOGRAPHY fields and no customXml bibliography source
store, and it rasterizes figures — failing 9.3.2, 9.3.6, 9.3.7, and 9.3.8
as-is. Phase 9 MUST upgrade or replace it as a named tooling-implementation
task (an OOXML post-processing stage plus the missing validators), not adopt
it unmodified.

## 9.6 Future-revision source package

Preserve:

- canonical manuscript source;
- LaTeX source and build files;
- Word reference template;
- Word generator/filter code;
- field and label registries;
- editable diagram sources;
- figure scripts and data;
- bibliography source store;
- validation scripts and reports; and
- versioned build instructions.

---

# 10. Scientific writing, citation, and editorial standard

## 10.1 Voice and precision

- Use professional academic English.
- Use a consistent first-person plural voice where appropriate.
- Prefer concrete subjects and active verbs.
- Use one term per concept and one acronym per term.
- Define acronyms in the abstract and main text as journal rules require.
- Use calibrated verbs: `shows` for direct evidence, `suggests` for plausible
  interpretation, `is consistent with` for non-exclusive explanations, and
  `does not establish` for boundaries.
- Separate observation, inference, and speculation.
- Calibrate register and density against the Section 8.7 presentation
  exemplars (`mohamed2020gaining`, `alfadli2025atmals`): the manuscript should
  read as a peer of the family's strongest published papers — comparable
  professionalism, clarity, and presentation quality — as verified by the
  Phase 10 exemplar-parity editorial check, never by self-assertion in the
  prose.

## 10.2 Paragraph construction

A useful default is:

```text
focused claim → evidence → interpretation → boundary or transition
```

No paragraph may contain a chain of unsupported assertions. Keep citations and
internal evidence references adjacent to the supported content.

## 10.3 Natural expert prose

Write genuinely clear, specific, non-formulaic prose. Improve rhythm and flow
without changing facts. Useful practices include:

- varied sentence length driven by meaning;
- varied but logical openings;
- concrete references to the actual method, suite, dimension, or result;
- local, earned hedging;
- precise domain terminology; and
- paragraphs of natural length rather than mechanically symmetric blocks.

The objective is readability and scholarly voice, not detector evasion.

## 10.4 Prohibited rhetoric

Avoid unless directly supported and precisely scoped:

```text
state-of-the-art
universally superior
consistently outperforms
significantly better
robust
highly efficient
negligible overhead
for free
large-scale
high-dimensional
first-ever
novel in the literature
proves
guarantees
solves the exploration-exploitation dilemma
applicable to all real-world problems
```

Also avoid empty stock transitions, marketing language, repetitive tricolons,
abstract nouns where a clear verb works, anthropomorphic claims, and generic
sentences that could belong unchanged to any optimization paper.

## 10.5 Preferred specificity

Prefer formulations such as:

- “on the verified CEC2017 D = 50 panel” rather than “in high dimensions”;
- “lower median final error on X of 29 functions” rather than “better overall”;
- “Holm-adjusted p = ..., A12 = ..., 95% CI [...]” rather than “significantly
  outperformed”; and
- “the tested evidence does not cover D > 100” rather than a vague scalability
  disclaimer.

Use actual values only after binding them.

## 10.6 Citation placement

- Cite immediately after the supported clause or sentence.
- Group sources only when every source supports the grouped claim.
- For contrasts, cite each side where needed.
- Cite benchmark/statistical definitions at first material use.
- Avoid unnecessary repetition within a tightly scoped paragraph.
- Every citation occurrence must have a `citation_usage_map.csv` row.

## 10.7 Style-only revision integrity

A prose polish pass MAY change wording, sentence order, paragraph breaks, and
transitions. It MUST NOT change:

- numbers;
- claim scope;
- citation keys;
- references;
- equations;
- table/figure content;
- algorithm behavior; or
- statistical interpretation.

Review the diff. Any factual correction uses the normal claim/evidence and
review workflow, not the style-only path.

---

# 11. Team roles, review lenses, and sign-off responsibilities

The agent SHALL explicitly adopt these roles in working notes. One agent may
perform multiple roles, but each lens requires a separate pass.

## 11.1 Research and engineering roles

- **P1 — Principal investigator / lead author:** thesis, contribution boundary,
  scope, decisions, final scientific sign-off.
- **P2 — Algorithm theorist:** formal method, inherited/modified/original
  separation, pseudocode, equations, complexity.
- **P3 — Experimental design and statistics lead:** estimands, units, pairing,
  multiplicity, effects, intervals, robustness.
- **P4 — Benchmark and data engineer:** evidence release, suite protocol,
  seeds, MaxFES, provenance, comparability.
- **P5 — Reproducibility engineer:** manifests, hashes, deterministic commands,
  clean rebuilds, artifact bindings.
- **P6 — Scientific writer/editor:** structure, clarity, evidence-aware prose,
  journal style.
- **P7 — LaTeX/PDF and visualization specialist:** template, build, figures,
  tables, accessibility, print quality.
- **P8 — Microsoft Word/OOXML specialist:** OMML, native tables, fields,
  citations, cross-references, Word QA.
- **P9 — Research-integrity auditor:** closed-corpus compliance, claim and
  citation traceability, unsupported-content detection.
- **P10 — Submission editor:** current journal compliance, declarations,
  package integrity, administrative gaps.

## 11.2 Adversarial review roles

- **R1 — Q1 scientific reviewer:** importance, novelty boundary, method rigor,
  baseline strength, statistics, external validity, limitations.
- **R2 — methodological/statistical reviewer:** design, unit, pairing,
  multiplicity, effect, interval, robustness, ablation identifiability.
- **R3 — reproducibility reviewer:** release integrity, seeds, commands, hashes,
  code/evidence correspondence.
- **R4 — editorial and presentation reviewer:** clarity, narrative, figures,
  tables, journal compliance.
- **R5 — Word submission reviewer:** OMML, fields, native tables, updateability,
  cross-references, visual fidelity.
- **R6 — skeptical domain reviewer:** mechanism distinction, same-family scope,
  benchmark overfitting, cost, failure cases.

## 11.3 Quality bar

A deliverable passes only when:

- R1 finds no critical or major scientific issue;
- R2 finds no invalid inferential claim;
- R3 can trace every result to immutable evidence;
- R4 finds no material clarity or presentation defect;
- R5 confirms native Word editability and field behavior; and
- R6 cannot identify an unacknowledged scope or mechanism overclaim.

Every reviewer category must score at least 4/5, with explicit evidence for the
score.

---

# 12. Phase execution model

## 12.1 Mandatory phase fields

Every phase below is self-contained and includes:

- objective;
- expected outcomes;
- entry criteria;
- prerequisites;
- required inputs;
- dependencies;
- detailed implementation tasks;
- generated outputs;
- validation procedures;
- verification procedures;
- quality-assurance checkpoints;
- acceptance criteria;
- exit criteria;
- risks;
- assumptions;
- mitigation strategies;
- deliverables; and
- review gate.

A phase may begin only after its entry criteria are demonstrated in
`phase_gate_register.csv` (schema in Section 3.8). Phase 0 is exempt from this
rule for bootstrap: its first actions create the register and backfill Phase
0's own entry evidence. A failed acceptance criterion keeps the phase open.

## 12.2 Phase-state machine

Use these states:

```text
NOT_STARTED → ENTRY_CHECK → IN_PROGRESS → VALIDATION → REVIEW →
ACCEPTED → FROZEN
```

A frozen phase may be reopened only through a change request, recorded as a
row in `change_request_register.csv` (Section 3.1; created in Phase 0 in the
governance root), containing:

```text
change_id,reason,evidence,affected_phases,affected_claims,
affected_artifacts,rerun_plan,approver,status
```

## 12.3 Autonomous decision protocol

For every nontrivial decision:

1. identify the decision and alternatives;
2. list admissible evidence;
3. choose the option that best preserves validity, reproducibility, and journal
   compliance;
4. document rationale and consequences;
5. update assumptions and risks; and
6. continue without requesting user input unless the decision requires unknown
   human identity, legal, ethical, or administrative information.

When evidence is tied or incomplete, choose the more conservative claim or
analysis.

## 12.4 Phase artifact location

Governance artifacts (Section 3) live in the canonical governance root
`papers/governance/`; create it if absent. Automated validators (for example
Section 15.1) read governance artifacts from that root. Phase-scoped reports
and per-phase snapshots of governance state — copies for gate evidence, never
the master (Section 3 preamble) — are written under:

```text
papers/build_prompt_phases/phase_<NN>/
```

The legacy flat `build_prompt_phases/PHASE_<n>_*.md` companion files remain
untouched siblings; they are examples only (Section 0.2, Appendix D.8) and
never receive authoritative outputs. Use immutable snapshots or hashes for
files consumed by later phases.

---

# 13. Detailed implementation phases

## Phase 0 — Governance preflight, repository state, and authority freeze

### Objective

Establish the repository root, authoritative instructions, current commit,
write-protected evidence boundaries, toolchain state, and complete work plan
before modifying scientific artifacts.

### Expected outcomes

- one authoritative project configuration;
- clean or explicitly reconciled repository state;
- recorded anchor commit and branch;
- verified location of all expected source classes;
- identified instruction conflicts and their resolution;
- initialized decision, assumption, risk, and phase-gate registers; and
- no scientific manuscript change.

### Entry criteria

- this master file is available in the working context;
- repository access is available; and
- the agent can read file metadata and execute non-destructive inspection
  commands.

### Prerequisites

None beyond repository access. Do not assume that any historical prompt,
companion file, runbook, path, or expected count is correct.

### Required inputs

- entire repository, read-only for inspection;
- this master framework;
- current user requirements;
- any local runbook, addendum, or phase companions; and
- target-journal template files when present.

### Dependencies

No prior phase. Later phases depend on every Phase 0 governance artifact.

### Detailed implementation tasks

1. **Locate and fingerprint the repository.**
   - Determine the project root. For this framework the "repository root" IS
     the project directory containing `pyproject.toml` and this master file's
     parent (`papers/..`), not the enclosing Git root: every framework path
     (`papers/`, `benchmarks/`, `scripts/`, `results/`) resolves against the
     project root. Record the project root and the enclosing Git repository
     root (`git rev-parse --show-toplevel`) as two separate fields in
     `project_configuration.md`.
   - Record branch, HEAD, remotes, submodules, tags, and dirty state.
   - Run:

     ```powershell
     git status --porcelain
     git rev-parse HEAD
     git branch --show-current
     git submodule status
     ```

   - Store `anchor_commit=<sha>` and a dirty-path list.
   - A dirty path under the project root touching benchmark evidence, source
     code, configuration, tables, figures, or analysis blocks freezing until
     reconciled. Dirty paths in sibling projects that share the enclosing Git
     repository are recorded but are not blocking.

2. **Resolve instruction precedence.**
   - Inventory this master, prior prompts, `runbook.md`, companions, and
     addenda.
   - Create `instruction_precedence.md` with conflicts and disposition.
   - Explicitly mark obsolete statements about incomplete panels, empirical
     fallback, early/main-text ablation, CEC2013 run count, or detector evasion.

3. **Initialize governance records.**
   - Create `project_configuration.md`,
     `requirements_traceability_matrix.csv`, `source_line_traceability.csv`,
     `decision_log.md`, `assumption_register.csv`, `risk_register.csv`,
     `phase_gate_register.csv`, `change_request_register.csv`,
     `reproducibility_manifest.json` (initialized with its Section 3.1 schema
     so the Section 3.9 append rule is satisfiable from the first phase), and
     `administrative_gap_register.md`.
   - Classify every nonblank line of the updated prompt using Section 3.2 and
     map each operative requirement to this master, a phase, an artifact, a
     validation method, and an owner. Per Section 3.2, "the updated prompt" is
     this master file, `papers/PAPER_BUILD_PROMPT.md`, unless a separate brief
     path is recorded here in `project_configuration.md`.
   - Record the provisional target journal from the repository template without
     claiming current quartile or page limits.
   - Record the controlled analysis bundle root
     `papers/analysis/<release_id>/` (Section 7.13) in
     `project_configuration.md`; the `<release_id>` placeholder is bound when
     the evidence release is selected in Phase 2.

4. **Locate source boundaries.**
   - Confirm or mark missing:
     `reference_papers/`, `papers/references.bib`,
     `benchmarks/cec_reference_results/`,
     `benchmarks/cec_suite_python/`, `results/`, source/configuration paths,
     manuscript paths, scripts, figures, and tables.
   - Mark `benchmarks/cec_reference_results/` read-only.
   - Mark `results/` staging-only.

5. **Toolchain discovery.**
   - Determine Python, package manager, LaTeX, Word/OOXML tooling, Pandoc or
     alternative converter, archive tools, and checksum utilities.
   - Record versions without installing unapproved software that could modify
     evidence.

6. **Run non-destructive engineering preflight.**
   - Verify expected command forms:

     ```powershell
     python -m pip install -e ".[dev]"
     python -m pytest -q
     python -m ruff check .
     python scripts\validate_profile_lock.py --root .
     python scripts\build_docs_html.py
     python run.py --root . --help
     gsk-list --optimizers --benchmarks --references benchmarks/cec_reference_results
     ```

   - If installation changes lock files, revert or document before continuing.
   - Record command, working directory, timestamp, exit code, and output hash.

7. **Create the top-level asset inventory.**
   - Enumerate files by class and count.
   - Do not yet decide scientific admissibility; only locate and classify.

8. **Create the phase schedule.**
   - Populate all Phase 0–12 rows in `phase_gate_register.csv`.
   - Mark Phase 12 as the sole final implementation phase and ablation phase.

### Generated outputs

- `project_configuration.md`
- `instruction_precedence.md`
- `requirements_traceability_matrix.csv`
- `source_line_traceability.csv`
- `decision_log.md`
- `assumption_register.csv`
- `risk_register.csv`
- `phase_gate_register.csv`
- `change_request_register.csv`
- `reproducibility_manifest.json`
- `administrative_gap_register.md`
- `preflight_inventory.csv`
- `engineering_preflight.md`

### Validation procedures

- Confirm every governance file parses and has required fields.
- Confirm every nonblank updated-prompt line has exactly one accepted
  classification and every operative requirement has an implementation and
  validation destination.
- Confirm all expected path checks have explicit `present`, `missing`, or
  `not_applicable` status.
- Confirm the repository commit in every Phase 0 artifact is identical.
- Confirm no scientific source file changed during preflight.

### Verification procedures

- Re-run `git status --porcelain` and compare with the initial snapshot.
- Verify the anchor SHA independently with two Git commands where practical.
- Verify protected evidence permissions or document technical limitations.
- Verify instruction conflicts are explicitly resolved, not merely listed.

### Quality-assurance checkpoints

- P1 checks authority and scope.
- P5 checks audit reproducibility.
- P9 checks source boundaries.
- P10 checks administrative gaps and journal-template status.

### Acceptance criteria

- repository root and anchor commit are recorded;
- every expected source class is located or marked missing;
- empirical evidence and staging paths are clearly separated;
- no unresolved instruction conflict remains;
- engineering preflight is recorded;
- governance registers exist and are usable;
- source-line and requirement traceability contain no unmapped or partial row;
  and
- no scientific artifact was modified.

### Exit criteria

Set Phase 0 to `FROZEN` only after P1, P5, and P9 sign-off. Missing repository
paths may remain only when they are explicitly blocking and later work that does
not depend on them can continue.

### Risks

| Risk | Impact |
|---|---|
| dirty evidence or code tree | provenance invalidation |
| obsolete companion overrides master | contradictory execution |
| missing toolchain | build or validation failure |
| assumed target-journal rules | noncompliant package |

### Assumptions

- repository inspection is non-destructive;
- Git metadata is available or an equivalent source snapshot can be hashed; and
- the master file reflects the latest user requirement.

### Mitigation strategies

- quarantine dirty changes and create a clean worktree;
- write explicit precedence decisions;
- use containerized or documented tooling where available;
- defer journal-specific formatting until current official verification.

### Deliverables

All generated outputs above plus a one-page `PHASE_0_readiness.md` summarizing
anchor, source boundaries, toolchain, critical risks, and Phase 1 entry status.

### Review gate

**Gate 0:** P1 + P5 + P9 approve. Any unexplained dirty scientific path, unclear
evidence boundary, or unresolved authority conflict is a hard failure.

---

## Phase 1 — Closed literature-corpus audit and evidence-card construction

### Objective

Create a verified, claim-ready literature evidence base using only
`reference_papers/` and matching entries in `papers/references.bib`.

### Expected outcomes

- verified runtime citation set;
- one evidence card per admissible source;
- exact claim locators;
- documented missing/mismatched sources;
- no citation based on memory, web content, or unverified metadata.

### Entry criteria

- Phase 0 is frozen;
- `reference_papers/` and `papers/references.bib` are located or the absence is
  formally blocking; and
- source files can be read.

### Prerequisites

- project configuration;
- authority and source-boundary records;
- anchor commit.

### Required inputs

- `papers/references.bib`;
- all files in `reference_papers/`;
- Appendix A expected-key list;
- expected citation-role map in Appendix B.

### Dependencies

Phase 0. Every literature-dependent phase depends on Phase 1 outputs.

### Detailed implementation tasks

1. **Parse the BibTeX registry.**
   - Enumerate keys and required fields.
   - Detect duplicate keys, malformed entries, non-ASCII issues, and missing
     required metadata.
   - Expected count is 63 BibTeX entries, of which 61 are the admitted corpus of
     Appendix A; report the actual counts without forcing them.

2. **Inventory local literature files.**
   - Enumerate filenames, formats, readability, page count, and checksum.
   - Prefer `<bibkey>.pdf` naming but match by verified identity, not filename
     alone.

3. **Identity match.**
   - Compare title, authors, year, venue, DOI, and version.
   - Assign the identity status defined in Section 3.3.
   - Resolve minor mismatches using only the local source and BibTeX record.

4. **Read every admissible source.**
   - Extract research question, method, scope, findings, limitations, and exact
     usable locators.
   - Inspect tables/figures when relevant.
   - Do not rely only on abstracts.

5. **Create evidence cards.**
   - Record supported and unsupported uses.
   - Include the exact role in DT-GSK framing, method lineage, benchmark
     protocol, or statistical practice.

6. **Build runtime admissible set.**
   - Write `allowed_citation_keys.txt` from verified matches only.
   - Compare with Appendix A.
   - Record missing expected keys and unexpected extras.

7. **Build citation role map.**
   - For each admissible key, record sanctioned uses and prohibited
     overextensions.
   - Do not require every key to appear in final prose.

8. **Seed evidence gaps.**
   - Identify desired claims that the local corpus cannot support.
   - Apply omit/narrow/hypothesis/block dispositions.

9. **Citation-system readiness.**
   - Validate BibTeX parsing for LaTeX.
   - Prepare stable Word citation tags and a mapping to the Word source store.
   - Do not generate citations yet.

### Generated outputs

- `reference_inventory.csv`
- `allowed_citation_keys.txt`
- `evidence_cards/`
- `citation_role_map.csv`
- `evidence_gap_register.md`
- `word_citation_tag_map.csv`
- `literature_audit_report.md`

### Validation procedures

- Schema validation for all CSVs.
- Count every BibTeX key exactly once.
- Confirm every admissible key has one readable source and one evidence card.
- Confirm every evidence-card locator resolves to the local source.

### Verification procedures

- P9 independently checks a stratified sample of source identities and locators.
- Verify no external scientific URL, snippet, or unapproved source appears in
  evidence cards.
- Verify source checksums match inventory.
- Verify every expected key has an explicit status.

### Quality-assurance checkpoints

- P2 reviews algorithm/method lineage cards.
- P3 reviews statistical-method cards.
- P4 reviews benchmark-source cards.
- P6 reviews citation roles and wording boundaries.
- P8 verifies stable Word tags.

### Acceptance criteria

- all BibTeX entries audited;
- all literature files inventoried;
- runtime citation set is explicit;
- every admissible source has a complete evidence card;
- every mismatch has a disposition;
- unsupported claims are entered in the gap register; and
- no fictional or externally completed metadata exists.

### Exit criteria

Phase 1 freezes when every source intended for use is verified and claim-ready.
An expected but inadmissible source may remain excluded; the paper must not rely
on it.

### Risks

| Risk | Impact |
|---|---|
| missing or unreadable PDF | citation/claim blocked |
| BibTeX-source mismatch | incorrect attribution |
| abstract-only reading | distorted support |
| all-61 citation pressure | decorative citation |

### Assumptions

- local full texts are the sole scientific literature authority;
- a missing source cannot be reconstructed externally; and
- evidence cards can be created without changing source files.

### Mitigation strategies

- exclude unverified sources;
- narrow claims;
- prefer direct primary sources in the admissible set;
- reject citation quotas that conflict with semantic correctness.

### Deliverables

All generated outputs, plus `PHASE_1_gate_report.md` listing admissible count,
missing expected keys, major evidence gaps, and approved source roles.

### Review gate

**Gate 1:** P2 + P3 + P4 + P9 approve. Any intended rendered citation without a
verified local source is a hard failure.

---

## Phase 2 — Immutable empirical evidence, benchmark, and provenance audit

### Objective

Prove that the selected `cec_reference_results` release is complete,
self-consistent, comparable, immutable, and sufficient for the planned primary
study.

### Expected outcomes

- verified evidence release and manifest;
- complete data ledger and experiment matrix;
- suite, run, seed, FP, and MaxFES verification;
- strict-source guard;
- comparator-fairness classifications;
- asset-to-generator map;
- explicit defects and blocked comparisons.

### Entry criteria

- Phase 0 and Phase 1 are frozen;
- `benchmarks/cec_reference_results/` and evaluator code are available; and
- the selected release can be read without modification.

### Prerequisites

- anchor commit;
- project configuration;
- expected inventory from Section 4;
- literature evidence for suite definitions where available.

### Required inputs

- complete `benchmarks/cec_reference_results/` tree;
- `benchmarks/cec_suite_python/`;
- source/configuration code;
- result loader/statistics code;
- manuscript tables/figures and generators for provenance mapping;
- expected panel and protocol anchors.

### Dependencies

Phases 0–1. Phase 2 outputs are prerequisites for all empirical work.

### Detailed implementation tasks

1. **Verify evidence-tree layout.**
   - For CEC2017, CEC2011, and CEC2013, verify all seven optimizer directories.
   - Verify flat layout and required summary, per-run, environment, run-config,
     seed, verification, protocol, curve, and checkpoint files.
   - Confirm no doubled-suite directories.
   - Verify context-suite scope separately.

2. **Run machine validation.**

   ```powershell
   python -m gsk_family.cli.validate --references benchmarks/cec_reference_results
   ```

   - Archive complete output.
   - Do not hand-edit a failing cell.
   - In addition to the missing/empty/corrupt/NaN/Inf/truncated checks,
     explicitly detect (CR-0003): duplicate records and duplicate seeds;
     inconsistent run counts across cells; mixed numerical precision;
     unexpected algorithm names; and values outside protocol ranges.
   - Log, classify, trace to its source file, impact-evaluate, and report
     every anomaly before any dependent artifact is generated; never silently
     repair an anomaly.

3. **Verify expected coverage.**
   - CEC2017: seven algorithms × D10/D30/D50/D100 × 51 runs × verified 29
     functions.
   - CEC2011: seven algorithms × 25 runs × verified 22 native problems.
   - CEC2013: seven algorithms × D10/D30/D50 × 51 runs × 28 functions.
   - Calculate expected row counts and compare with actual per-run and seed
     schedules.

4. **Verify seeds and pairing.**
   - Test the expected seed formula against schedules.
   - Confirm uniqueness and deterministic mapping.
   - Determine whether pairing is valid for each comparator.

5. **Verify FP and environment.**
   - Read every `environment.json`.
   - Check suite-internal sentinel consistency.
   - Confirm expected CEC2017 prefix only as an audit target.
   - Record hardware, libraries, solver provenance, and known numerical
     variation.

6. **Verify evaluator equivalence.**
   - Hash shifts, rotations, bounds, optima, and evaluator code.
   - Cross-check suite metadata with approved benchmark literature.
   - Confirm function exclusions and dimension rules.

7. **Verify MaxFES and objective-call accounting.**
   - Inspect run configs and code.
   - Confirm local search and polish evaluations are counted.
   - Identify any algorithm-specific budget difference.

8. **Audit comparator provenance.**
   - Classify each cell A–D.
   - Record imported versus locally produced origin.
   - Verify `egsk` solver provenance and prevent SciPy/MATLAB substitution
     inside one exhibit.

9. **Build data ledger and experiment matrix.**
   - One ledger row per algorithm × suite × dimension × function set.
   - One experiment row per run when feasible.
   - Include release ID and checksums.

10. **Build strict-source guard and promotion tool.**
    - Inspect `result_loader.py` and report loaders.
    - Disable or block `results/_run_all/` fallback for publication analyses.
    - Add automated tests that fail when a resolved path is outside the selected
      evidence release.
    - Log every file opened by analysis.
    - Build the named promotion tool `scripts/promote_evidence.py` (tooling to
      build; it does not yet exist): it generates a release identifier and
      promotion manifest, copies an accepted staging bundle to a new versioned
      subtree under `benchmarks/cec_reference_results/`, verifies the promoted
      copy byte-for-byte against staging, and marks the release read-only
      (Section 2.4). Phases 11 and 12 gate-check and use this tool by name.
    - Test the promotion tool on a scratch bundle before Gate 2.

11. **Audit manuscript assets.**
    - Enumerate `papers/`, tables, figures, scripts, section inputs, class files,
      and cover letter.
    - Classify `keep`, `verify`, `regenerate`, `rewrite`, `move`, `archive`, or
      `remove`.
    - Map every existing table/figure to generator and empirical input.
    - Mark the runbook's claim that the `results/paper_tables/` T-CSVs come
      "from the stats pass" as stale in `instruction_precedence.md` and
      `asset_map.md`: their sole sanctioned producer is the Phase 6 task 23
      export from the controlled analysis bundle (Section 7.13).
    - Record T17–T20 as an intentional gap unless verified otherwise.

12. **Audit raw/derived separation.**
    - Ensure no manuscript table or figure is the only source for a number.
    - Identify stale or orphan derivative files.
    - Verify read-only evidence permissions and checksums.

13. **Audit staging data without admitting it.**
    - Inventory `results/` for reproducibility and later final ablation staging.
    - Mark every path non-admissible.
    - Quarantine historical ablation outputs from primary interpretation.

14. **Run engineering gates at the anchor commit.**
    - Repeat tests, lint, profile lock, and docs build.
    - Record actual pass counts and failures.

### Generated outputs

- `evidence_release_manifest.json`
- `data_ledger.csv`
- `experiment_matrix.csv`
- `comparability_audit.md`
- `benchmark_protocol_audit.md`
- `seed_and_pairing_audit.md`
- `fp_environment_audit.md`
- `strict_source_guard_report.md`
- `scripts/promote_evidence.py` and its scratch-bundle test evidence
- `asset_map.md`
- `table_figure_source_map.csv`
- `engineering_gates.md`
- `evidence_readiness_report.md`

### Validation procedures

- Run schema and row-count checks.
- Recompute checksums and compare with release manifest.
- Validate seed formula against a sample and full schedule when practical.
- Test strict-source guard with an intentional missing cell and forbidden
  fallback path.
- Verify every planned panel cell is present and comparable.

### Verification procedures

- Independently inspect at least one cell per suite and algorithm family.
- Cross-check run counts from `run_config.json`, `seed_schedule.csv`, and
  `per_run.csv`.
- Cross-check generator source maps against source code, not filenames.
- Confirm no evidence file changed during audit.

### Quality-assurance checkpoints

- P3 reviews inferential suitability.
- P4 owns benchmark/provenance verification.
- P5 reviews release immutability and strict-source guard.
- P9 reviews evidence admissibility.

### Acceptance criteria

- selected release is uniquely identified and checksummed;
- every primary panel cell is present or the scope is reduced;
- protocols, seeds, FP, MaxFES, and failures are verified;
- every comparison has A–D status;
- strict publication analysis cannot use `results/` fallback;
- every existing exhibit has a source map or is marked conceptual/stale; and
- no unexplained anomaly remains.

### Exit criteria

Phase 2 freezes when the empirical evidence required for the primary paper is
complete and admissible. A broken or missing cell must be corrected through a
new immutable release or removed from scope; it cannot be silently replaced.

### Risks

| Risk | Impact |
|---|---|
| incomplete panel | invalid comparison |
| invalid pairing | invalid Wilcoxon inference |
| FP mismatch | non-poolable evidence |
| loader fallback | evidence-boundary violation |
| stale tables/figures | manuscript-data inconsistency |
| solver provenance mismatch | unfair comparator claim |

### Assumptions

- immutable evidence metadata truthfully describes executed runs;
- validator can inspect the selected release; and
- evaluator inputs are locally available.

### Mitigation strategies

- fail closed and rescope;
- create a new validated evidence release rather than editing;
- use descriptive comparison when paired inference is invalid;
- instrument source-path logging;
- regenerate derivatives from authoritative raw evidence.

### Deliverables

All generated outputs plus `PHASE_2_gate_report.md` with a complete panel table,
critical anomalies, strict-source test result, and P3/P4/P5/P9 sign-offs.

### Review gate

**Gate 2:** P3 + P4 + P5 + P9 approve. Any source outside
`cec_reference_results`, unexplained run mismatch, invalid budget, or unresolved
comparability defect blocks the gate.

---

## Phase 3 — Method reconstruction, code correspondence, and algorithm freeze

### Objective

Reconstruct the evaluated DT-GSK method precisely, verify every mechanism
against code and configuration, derive complexity, and freeze the algorithm
before claims or primary analyses are finalized.

### Expected outcomes

- reimplementable mathematical specification;
- inherited/modified/original decomposition;
- equation/pseudocode/code correspondence;
- verified evaluation accounting;
- frozen parameters and toggles;
- algorithm freeze manifest;
- no unresolved prose-code conflict.

### Entry criteria

- Phases 0–2 are frozen;
- frozen evidence release and executed code/configuration hashes are known; and
- source code/tests are available.

### Prerequisites

- data ledger and release manifest;
- literature evidence cards for GSK and closest methods;
- evaluator and algorithm source.

### Required inputs

- DT-GSK and comparator source/configuration;
- profile lock and tests;
- run configs from immutable evidence;
- relevant approved papers;
- historical method prose for discrepancy audit only.

### Dependencies

Phases 1–2. Phase 3 freeze is required before statistical claim freeze and all
later experiments.

### Detailed implementation tasks

1. **Trace the executed algorithm.**
   - Locate entry point, configuration merge, initialization, generation loop,
     evaluation accounting, stopping, and return path.
   - Trace every expected component and all hidden defaults.

2. **Classify each mechanism.**
   - Inherited, modified, original, optional, dormant, or absent.
   - Record closest approved literature and exact difference.

3. **Define the optimization problem and notation.**
   - Objective, domain, bounds, population, evaluations, indices, states,
     archives, graph matrices, and random variables.

4. **Specify GSK inheritance.**
   - Junior/senior phases, knowledge factor/ratio/rate, selection, and update
     order.

5. **Specify scaffold mechanisms.**
   - ACE selector and reward/update timing.
   - NLPSR schedule and minimum population.
   - BSE trigger, Cauchy or other rescue distribution, budget safety.
   - ARGP pool update and acceptance gating.
   - Archive and local-search behavior.

6. **Specify SGSM.**
   - Graph representation and dimensionality.
   - Observation source.
   - Support update, decay/EMA, confidence, threshold, and reset.
   - How linkage blocks and eigenframe directions are obtained.
   - Numerical safeguards and fallback.
   - Objective-evaluation and computational cost.

7. **Specify endgame and polish.**
   - Trigger, cadence, basis, direct-search behavior, Nelder–Mead behavior,
     acceptance, budget, and termination.

8. **Write pseudocode and equations.**
   - Top-level algorithm.
   - Mechanism-level blocks where ambiguity remains.
   - Equation registry and label plan for LaTeX and Word.

9. **Build implementation correspondence.**
   - Map each equation/pseudocode line to code files/functions/line ranges or
     stable symbols.
   - Identify dead code, undocumented behavior, and prose-only mechanisms.

10. **Verify objective-call accounting.**
    - Add or inspect tests proving all calls count toward MaxFES.
    - Verify budget-safe exits and partial generations.

11. **Derive complexity.**
    - Time and memory by mechanism.
    - Expected `O(D^2)`/`O(D^3)` terms only if code supports them.
    - Amortize by cadence.
    - Separate objective cost and overhead.

12. **Create deterministic traces.**
    - Use fixed small dimension and seed.
    - Source traces from the DT-GSK opt-in per-generation diagnostic telemetry
      (`DTTrace_<suite>_F<f>_D<d>_R<r>_S<seed>.jsonl`, emitted by the DT-GSK
      adapter `dt_gsk.py` only when its `dt_diagnostics` option is set — off by
      default, drawing no RNG and numerically identical to the default path for
      a given seed) or from wrappers at the runner/evaluator layer; do not
      instrument the profile-locked DT-GSK core files.
    - Record state transitions, graph update, population change, and evaluation
      count.
    - Compare trace against pseudocode.

13. **Define ablation toggles without running them.**
    - Audit `run_ablation.py` and config keys.
    - Verify toggle semantics for `ace_enabled`, `psr_enabled`, `bse_enabled`,
      `linkage_blockwise_enabled`, `local_search_enabled`, `arch_enabled`, and
      `interaction_graph_enabled` or actual equivalents.
    - Ensure toggles disable only the intended component.
    - Do not inspect ablation outcomes.

14. **Freeze algorithm.**
    - Create `algorithm_freeze_manifest.json`.
    - Tag or record the frozen commit/config.
    - Set change-control rule.

### Generated outputs

- `notation_table.tex`
- `notation_table_word.omml.xml` (the Word-ready notation source)
- `algorithm_pseudocode.tex`
- `algorithm_pseudocode.md` (the canonical pseudocode source)
- `parameter_table.tex`
- `equation_registry.csv`
- `implementation_correspondence.md`
- `complexity_analysis.md`
- `evaluation_accounting_report.md`
- `deterministic_trace/`
- `contribution_matrix.md`
- `ablation_toggle_audit.md`
- `algorithm_freeze_manifest.json`

The Word-ready notation source and the canonical pseudocode source are files
with deterministic paths (Section 0.6), not descriptions: write them under
`papers/build_prompt_phases/phase_03/` (Section 12.4) using the names above so
the Word-production phases can bind them.

### Validation procedures

- Execute deterministic traces and unit tests.
- Validate every symbol and parameter appears in the registry.
- Compare pseudocode branches with code coverage.
- Confirm evaluation-count tests at exact budget boundaries.
- Recompute complexity formulas from dimensions of actual data structures.

### Verification procedures

- P2 independently follows one complete iteration from code to pseudocode.
- P4 verifies evaluator-call accounting.
- P5 verifies hashes and freeze manifest.
- P9 verifies inherited/modified/original claims against evidence cards.

### Quality-assurance checkpoints

- no undefined symbol;
- no mechanism without purpose, timing, cost, and fallback;
- no prose-only mechanism;
- no code behavior omitted when scientifically material;
- no unsupported “free” or “negligible” wording.

### Acceptance criteria

- a competent reader can reimplement the frozen core;
- code, configuration, equations, pseudocode, and trace agree;
- all objective calls are accounted for;
- complexity is derived and scoped;
- contribution boundaries are evidence-based; and
- algorithm and parameters are frozen.

### Exit criteria

Phase 3 freezes with P2/P4/P5/P9 sign-off and a clean profile-lock/test result.
Any algorithm change after this point invalidates Phases 3 onward.

### Risks

| Risk | Impact |
|---|---|
| hidden configuration default | irreproducible method |
| pseudocode/code drift | false method description |
| toggle disables multiple components | invalid ablation |
| uncounted local-search calls | unfair MaxFES |
| unsupported novelty wording | reviewer rejection |

### Assumptions

- source at the evidence commit is available;
- run configuration reflects executed behavior; and
- deterministic micro-tests can exercise key branches.

### Mitigation strategies

- instrument only outside the profile-locked files without changing algorithm
  semantics (the byte-identical DT-GSK core sources are hash-locked in
  `algorithm_freeze_manifest.json`, so even semantics-preserving in-file
  instrumentation breaks the freeze and fails the clean profile-lock exit
  criterion): use the opt-in `DTTrace_*.jsonl` telemetry or
  runner/evaluator-layer wrappers;
- add regression tests;
- narrow mechanism claims;
- redesign toggle configs before freeze, not after primary results;
- document any unavoidable implementation ambiguity.

### Deliverables

All generated outputs plus `PHASE_3_gate_report.md` and the signed algorithm
freeze manifest.

### Review gate

**Gate 3:** P2 + P4 + P5 + P9 approve. Any material equation/code mismatch,
unknown evaluation cost, or ambiguous ablation toggle is a hard failure.

---

## Phase 4 — Thesis, contributions, journal, claims, and manuscript-plan freeze

### Objective

Define exactly what the primary manuscript can defend, choose the verified
submission target and structure, and freeze all planned claims and exhibits
before computing or rewriting headline conclusions.

### Expected outcomes

- evidence-bounded thesis;
- three to five accepted contributions;
- closest-work and novelty boundary;
- target-journal decision and current requirements;
- complete claim inventory;
- section outline and page budget;
- explicit no-ablation main-manuscript plan.

### Entry criteria

- Phases 0–3 are frozen;
- literature, empirical release, and algorithm specification are verified; and
- no algorithm change is pending.

### Prerequisites

- evidence cards;
- contribution matrix;
- data ledger/comparability audit;
- algorithm freeze manifest;
- current official journal guidance access.

### Required inputs

- all accepted Phase 1–3 artifacts;
- existing manuscript outline/prose for audit only;
- journal template and current instructions;
- provisional page budget.

### Dependencies

Phases 1–3. Phase 4 outputs drive the analysis plan, exhibits, and writing.

### Detailed implementation tasks

1. **Verify current target journal.**
   - Use the repository-wired target by default.
   - Check current official instructions and article type.
   - Record source, access date, template version, limits, declarations,
     anonymization, Word/LaTeX rules, and supplement rules.
   - Verify current quartile only when needed and from an appropriate current
     source; do not state it in the manuscript unless relevant.

2. **Draft contribution candidates.**
   - Candidate mechanisms may include SGSM, linkage use, eigenframe polish,
     adaptive scaffold, controlled family evaluation, and reproducibility.
   - For each: category, exact difference, code location, primary evidence,
     final-phase ablation need, scope, and reviewer risk.

3. **Apply contribution acceptance test.**
   - Keep three to five load-bearing contributions.
   - Remove duplicates, implementation trivia, and unsupported novelty.
   - Do not claim component contribution before final ablation; frame it as a
     proposed mechanism to be tested in the supplement.

4. **Write the primary thesis.**
   - Problem → bounded gap → central mechanism → primary evaluation design →
     strongest expected claim type → reproducibility.
   - Do not insert an unverified number at this stage.
   - Do not mention ablation results.

5. **Define evidence roles.**
   - Primary, secondary, descriptive, exploratory, or context-only.
   - Do not call CEC2013 independent or holdout without development-history
     evidence.

6. **Build complete claims matrix.**
   - Seed all background, method, protocol, primary result, interpretation,
     limitation, conclusion, highlight, and cover-letter claim templates.
   - Assign evidence IDs, risk, permitted wording, and blocked wording.
   - Mark future ablation claims `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`.

7. **Create manuscript outline.**
   - Use Section 8 architecture and current journal requirements.
   - Assign section/subsection objectives, evidence, citations, exhibits,
     page/word budget, and reviewer risks.
   - Define the canonical manuscript source concretely (Section 9.1):
     `papers/main.tex` plus `papers/sections/*.tex` (and
     `papers/supplementary.tex` for the supplement), together with the
     Section 9.1 registries, constitute the canonical content model. Record
     this binding in `project_configuration.md`; Phases 8–9 consume and freeze
     exactly this source set.
   - Explicitly exclude an ablation subsection from the main manuscript.

8. **Create exhibit plan.**
   - One row per table/figure/algorithm/equation.
   - Map to research question, source, generator, main/supplement destination,
     and claim IDs.
   - Pre-register the Section 6.7 family-overlay convergence design (CR-0001):
     the seven-algorithm panel composition, the per-checkpoint mean-across-runs
     aggregation, the fixed algorithm-to-color/linestyle map, the dimension
     set per suite, and the summary-statistic-derived main-text selection
     rule.
   - Assign each planned exhibit its canonical cross-reference label; these
     labels initialize the Section 9.1 label tracking and seed
     `artifact_binding.csv` (`manuscript_label`) when Phase 7 task 11 creates
     that file.
   - For every exhibit classified as authored conceptual art (Section 8.1),
     write an approval-level specification (message, required elements,
     labels, and an explicit no-empirical-source statement) in
     `conceptual_figure_specs.md`; Gate 4 approval of the exhibit plan
     approves these specifications, and Phase 7 consumes them as the approved
     conceptual-art specifications.
   - Reserve ablation exhibit IDs for Phase 12 supplement only.

9. **Create closest-work comparison.**
   - Compare SGSM, differential grouping, eigenvector crossover, covariance
     adaptation, and direct search only along verified dimensions.
   - Avoid exhaustive or universal novelty claims.

10. **Freeze terminology.**
    - Method name, component names, acronyms, symbols, suite names, algorithm
      labels, and evidence terminology.
    - The algorithm name is written **eGSK** (lowercase e, uppercase GSK)
      everywhere except where an official cited title differs; freeze the
      capitalization of every GSK-family name (CR-0003).

11. **Risk review.**
    - Every high-risk claim needs a concrete mitigation: scope reduction,
      planned analysis, cost measurement, limitation, or removal.

12. **Extract the presentation-conventions register (CR-0002, CR-0003).**
    - Read the three Section 8.7 exemplars (`reference_papers/
      mohamed2020gaining.pdf`, `reference_papers/alfadli2025atmals.pdf`,
      `reference_papers/jawad2024egsk.pdf`) and the corpus's other leading
      venue papers as needed.
    - Perform a structured comparative review of all three exemplars covering
      at least: paper structure; section ordering; introduction strategy;
      research-gap formulation; contribution presentation; literature-review
      organization; algorithm explanation; mathematical notation; pseudocode
      design; parameter documentation; experimental setup; benchmark
      reporting; statistical testing; table density and readability;
      convergence-plot design; figure placement; discussion depth;
      limitations; reproducibility; supplementary-material usage; conclusion
      structure; and overall visual and editorial quality.
    - Write `papers/governance/presentation_conventions.md` with, per
      dimension, each exemplar's practice, the adopted best practice, and any
      weakness to avoid (overcrowded tables, repetitive text, weak
      interpretation, inconsistent notation, underspecified experiments,
      excessive visual density, unsupported claims). Exemplars are
      calibration references, never content templates: no mechanical copying;
      combine the strongest practices and improve where justified.
    - In `outline.md`, map every main-text section to the convention it
      follows or the recorded, justified improvement.

### Generated outputs

- `journal_requirements.md`
- `journal_decision.md`
- `thesis.md`
- final `contribution_matrix.md`
- `novelty_scope.md`
- initial `claims_evidence_matrix.csv`
- `outline.md`
- `page_budget.md`
- `exhibit_plan.csv`
- `conceptual_figure_specs.md`
- `terminology_glossary.md`
- `presentation_conventions.md`
- updated risk/decision registers

### Validation procedures

- Check every contribution against definition/distinction/implementation/
  evidence/scope.
- Check every outline subsection has objective, evidence, citations, and budget.
- Sum page/word budget.
- Check no ablation result is planned for main text.
- Check all citation shortlists are subsets of the runtime admissible set.

### Verification procedures

- P1 traces each contribution to evidence and code.
- P6 verifies narrative coherence and no overpromise.
- P10 verifies journal rules against current official instructions.
- P9 checks novelty wording and citation roles.

### Quality-assurance checkpoints

- no contribution without evidence;
- no headline result invented before analysis;
- no field-wide claim from same-family panel;
- no hidden ablation promise in abstract/conclusion plan;
- page budget closes without illegible exhibits.

### Acceptance criteria

- target journal and current requirements are recorded;
- thesis and contributions are evidence-bounded;
- every planned claim has a matrix row;
- every high-risk claim has mitigation;
- outline and exhibit plan fit budget;
- ablation is supplement-only and Phase-12-only; and
- terminology is frozen.

### Exit criteria

Phase 4 freezes after P1/P6/P9/P10 sign-off. Later empirical results may narrow
or remove claims but may not silently expand them.

### Risks

| Risk | Impact |
|---|---|
| journal rules change | package rework |
| contribution depends on future ablation | overclaim in main paper |
| same-family scope overstated | invalid generalization |
| page budget ignores Word layout | inconsistent submissions |

### Assumptions

- a provisional journal can be selected autonomously from repository context;
- current official guidance is available; and
- scientific framing can proceed without missing author metadata.

### Mitigation strategies

- record access date and recheck in final phase;
- keep component-causality claims out of main manuscript;
- use exact panel scope;
- budget and inspect both PDF and Word layouts.

### Deliverables

All generated outputs plus `PHASE_4_gate_report.md` containing the signed thesis,
contributions, target, scope, no-ablation rule, and claim-risk summary.

### Review gate

**Gate 4:** P1 + P6 + P9 + P10 approve. Unsupported novelty, unbounded
superiority, unverified journal requirements, or planned main-text ablation
fails the gate.

---

## Phase 5 — Statistical-analysis, protocol, and exhibit-design freeze

### Objective

Translate the accepted claims and verified experimental design into a complete,
pre-specified statistical analysis plan and exhibit specification before
primary results are interpreted.

### Expected outcomes

- frozen research questions and endpoints;
- valid units of analysis and pairing rules;
- declared hypothesis families and multiplicity controls;
- effect-size and interval plan;
- convergence, robustness, sensitivity, and cost plans;
- deterministic analysis commands and schemas;
- pre-specified curve selection;
- no outcome-driven primary choice.

### Entry criteria

- Phases 0–4 are frozen;
- the empirical release and comparability statuses are accepted;
- the algorithm and primary claims are frozen; and
- no unresolved protocol defect affects the planned analyses.

### Prerequisites

- `claims_evidence_matrix.csv`;
- `data_ledger.csv` and `comparability_audit.md`;
- `algorithm_freeze_manifest.json`;
- evidence cards for statistical methods;
- journal/outline/exhibit plan.

### Required inputs

- raw/per-run and summary schema from the selected evidence release;
- analysis code and current CLI;
- exact panel, functions, dimensions, runs, and pairing status;
- proposed table/figure list.

### Dependencies

Phases 1–4. Phase 6 may not inspect headline outcomes before Phase 5 freezes.

### Detailed implementation tasks

1. **Finalize research questions.**
   - Adopt or refine RQ1–RQ8 from Section 7.
   - Separate primary, secondary, descriptive, and exploratory questions.
   - Pre-register supplement-only ablation questions without running ablation.

2. **Define primary endpoint.**
   - Specify optimum subtraction, error floor, transform, central tendency,
     dispersion, ranking direction, and failure encoding.
   - Verify definitions against benchmark evidence and release schema.

3. **Define units and estimands.**
   - For every claim, specify experimental unit, observation unit, task unit,
     aggregation, pairing key, and independence assumptions.
   - Prohibit run-level pseudoreplication for across-function claims.

4. **Define descriptive outputs.**
   - Exact summaries, precision, missingness, tie rules, win/tie/loss basis, and
     ordering.

5. **Define omnibus analyses.**
   - Friedman design per suite/dimension when valid.
   - Nemenyi display conditions and task count.
   - No cross-dimension pooling unless separately justified.

6. **Define pairwise families.**
   - DT-GSK versus six comparators per suite/dimension by default.
   - Valid pairing requirement.
   - Holm as primary correction when supported.
   - BH only as separately labeled exploratory analysis, if retained.

7. **Define effect and interval analyses.**
   - A12 direction, data level, and reporting.
   - BCa statistic, resampling unit, hierarchy, seed, resample count, confidence
     level, and failure handling.
   - Attach to every planned significance/headline claim.

8. **Define convergence analysis.**
   - Checkpoint alignment, aggregation, uncertainty, failure rule.
   - Create selection rubric before rendering:
     primary performance representativeness, function-class coverage, one hard
     case, and no favorable cherry-picking.
   - Write `curve_selection_rule.md` and reserve `curve_selection.csv`.

9. **Define secondary-suite analysis.**
   - Role of CEC2013 and CEC2011.
   - No “independent” or “holdout” language unless verified.
   - Same tests only when design supports them.

10. **Define parameter-sensitivity treatment.**
    - Exploratory status, n = 3 limitation, grid/range, tasks, and claims.
    - Do not mix with ablation.

11. **Define cost analysis.**
    - Metrics, environment, dimensions, repetitions, normalization, and
      confidence interval.
    - Separate objective and algorithmic cost.

12. **Define robustness checks.**
    - Error floor, summary statistic, disputed cells, influence, pairing,
      correction family, and dimension aggregation.

13. **Define source-resolution policy.**
    - Per-function versus per-run input for each exhibit.
    - Record in `exhibit_plan.csv` and manuscript setup.
    - Reject any analysis whose resolution is unavailable or invalid.

14. **Define strict-source execution.**
    - Configure source guard and release ID.
    - Specify the output directory — the controlled analysis area
      `papers/analysis/<release_id>/<suite>/` (Section 7.13) — and the
      source-use log.
    - Require failure if any empirical input is outside the release.

15. **Define deterministic outputs.**
    - File names, schemas, sort order, floating-point formatting, RNG seeds,
      locale, and software versions.

16. **Write claim-to-analysis bindings.**
    - Every planned numerical/statistical claim receives an analysis ID.
    - Every analysis ID has a source, method, and output row.

17. **Pre-register final ablation plan at design level only.**
    - Define component toggles, remove-one, direct SGSM, incremental/add-one or
      cumulative design, statistical family, overhead, convergence, and
      sensitivity requirements.
    - Mark every output `PHASE_12_ONLY`.
    - Do not execute objective evaluations or inspect historical results.

### Generated outputs

- `statistical_analysis_plan.md`
- `analysis_registry.csv`
- updated `claims_evidence_matrix.csv`
- updated `exhibit_plan.csv`
- `curve_selection_rule.md`
- `source_resolution_map.csv`
- `robustness_plan.md`
- `cost_analysis_plan.md`
- `ablation_preregistration.md` marked Phase 12 only
- `analysis_output_schemas/`

### Validation procedures

- Validate each claim has a compatible analysis ID or non-empirical evidence.
- Check every paired test against comparability/pairing status.
- Check every correction family is explicitly enumerated.
- Check every headline result has effect-size and interval definitions.
- Check no analysis reads a forbidden source.
- Check final ablation design is registered but not executed.

### Verification procedures

- P3 independently re-derives units and hypothesis families.
- P4 verifies data resolution and pairing availability.
- P5 verifies deterministic source-guarded command design.
- P9 verifies planned wording matches method capability.

### Quality-assurance checkpoints

- no post hoc primary choice;
- no pseudo-replication;
- no invalid pairing;
- no mixed correction families;
- no unseeded bootstrap;
- no convergence cherry-picking;
- no ablation result inspection.

### Acceptance criteria

- research questions and endpoints are frozen;
- units, pairing, tests, corrections, effects, and intervals are valid;
- every exhibit and claim has an analysis binding;
- robustness and cost plans are complete;
- source guard and deterministic outputs are specified;
- final ablation is fully pre-registered but untouched.

### Exit criteria

Phase 5 freezes after P3/P4/P5/P9 sign-off. Any later primary analysis change is
logged and classified as confirmatory amendment or exploratory deviation.

### Risks

| Risk | Impact |
|---|---|
| outcome-driven analysis | biased conclusions |
| invalid per-run pairing | false significance |
| unclear hypothesis family | multiplicity error |
| bootstrap wrong hierarchy | invalid CI |
| early ablation exposure | development leakage |

### Assumptions

- the immutable release contains sufficient resolution;
- approved statistical sources support the planned methods; and
- analysis code can be made deterministic.

### Mitigation strategies

- rescope to descriptive evidence;
- use valid task-level analysis;
- narrow hypothesis families before execution;
- label amendments exploratory;
- quarantine historical ablation results.

### Deliverables

All generated outputs plus `PHASE_5_gate_report.md` summarizing RQs, endpoints,
units, families, effects, intervals, strict-source proof plan, and ablation
quarantine.

### Review gate

**Gate 5:** P3 + P4 + P5 + P9 approve. Invalid pairing, undefined multiplicity,
unbound claim, forbidden source, or early ablation access fails the gate.

---

## Phase 6 — Primary evidence computation and statistical validation

### Objective

Execute the frozen non-ablation analysis plan strictly from the selected
`cec_reference_results` release and produce every primary numerical result in a
machine-readable, reproducible bundle.

### Expected outcomes

- complete primary descriptive and inferential outputs;
- deterministic ranks, tests, effects, intervals, convergence summaries, cost,
  and robustness checks;
- source-use audit proving reference-only inputs;
- claim statuses updated from actual evidence;
- no manuscript number without an authoritative output.

### Entry criteria

- Phases 0–5 are frozen;
- source guard tests pass;
- selected evidence release is immutable and complete;
- analysis plan and schemas are frozen;
- algorithm remains unchanged.

### Prerequisites

- `statistical_analysis_plan.md`;
- analysis registry and output schemas;
- selected evidence release and manifest;
- strict-source guard;
- deterministic software environment.

### Required inputs

- immutable evidence release only;
- frozen analysis code;
- frozen claim and exhibit plans;
- approved statistical literature for method descriptions.

### Dependencies

Phases 2, 3, and 5. No ablation input is permitted.

### Detailed implementation tasks

1. **Create clean analysis environment.**
   - Record software/library versions, locale, thread settings, RNG behavior,
     and working directory.
   - Confirm anchor and algorithm freeze hashes.

2. **Activate strict source guard.**
   - Set selected release root and ID.
   - Disable `results/_run_all/` fallback.
   - Start file-open/source-use logging.
   - Execute a negative test proving a forbidden path fails.

3. **Validate source completeness immediately before analysis.**
   - Recompute manifest hashes.
   - Recheck run counts, seed schedules, FP sentinels, and cell schemas.
   - Abort affected analysis on drift.

4. **Run primary suite analysis.**

   ```powershell
   python -m gsk_family.cli.stats --suite CEC2017 --dims 10,30,50,100 --out papers/analysis/<release_id>/cec2017/
   ```

   - Confirm expected function denominator from release metadata.
   - Capture stdout, stderr, command, environment, and output hashes.

5. **Run CEC2011 analysis.**

   ```powershell
   python -m gsk_family.cli.stats --suite CEC2011 --out papers/analysis/<release_id>/cec2011/
   ```

   - Respect native dimensions and task definitions.

6. **Run CEC2013 analysis.**

   ```powershell
   python -m gsk_family.cli.stats --suite CEC2013 --dims 10,30,50 --out papers/analysis/<release_id>/cec2013/
   ```

   - Do not apply the CEC2017 F2 exclusion.

7. **Compute descriptive summaries.**
   - Best, median, mean, worst, SD, IQR, failures, and n.
   - Verify against source summaries and per-run reconstruction.
   - Resolve any discrepancy through code/provenance audit, never manual edits.

8. **Compute omnibus ranks/tests.**
   - One frozen design per suite/dimension.
   - Emit tasks, algorithms, ranks, statistic, p-value, and CD inputs.

9. **Compute pairwise analyses.**
   - DT-GSK versus each valid comparator.
   - Wilcoxon only with valid pairing.
   - Holm-adjust within declared families.
   - Emit raw/adjusted p, statistic, direction, n, ties, and status.

10. **Compute effect sizes.**
    - A12 with direction and data unit explicit.
    - Bind each significance claim to an effect.

11. **Compute BCa intervals.**
    - Use frozen RNG seed, resampling unit, and number of resamples.
    - Emit `headline_bca.csv` or registry-defined equivalent.
    - Record convergence/failure of interval computation.

12. **Create curve selection.**
    - Apply the pre-specified rule without viewing final chart aesthetics.
    - Record selected suite/function/dimension and reason.
    - Include hard/adverse case.

13. **Compute convergence aggregates.**
    - Validate checkpoints.
    - Emit central trajectory, uncertainty, n, failures, and source list.

14. **Compute parameter sensitivity summaries.**
    - Use only admitted immutable evidence if a validated sensitivity release
      exists.
    - Otherwise mark sensitivity unavailable; do not use `results/` staging.
    - Label n = 3 evidence exploratory.

15. **Compute primary overhead/cost.**
    - Use a validated immutable cost record or promote candidate measurements
      before use.
    - Separate objective cost, wall time, and memory.

16. **Execute robustness checks.**
    - Run every pre-specified check.
    - Flag reversals or material sensitivity.

17. **Cross-implementation verification.**
    - Independently recompute a sample of ranks, p-value adjustment, A12, and
      interval using a second implementation or direct formula when practical.
    - Resolve discrepancies.

18. **Determinism check.**
    - Rerun each suite to a scratch directory.
    - Compare machine-readable outputs byte-for-byte or with a documented
      deterministic tolerance where unavoidable.
    - Delete or quarantine scratch outputs.

19. **Source-use audit.**
    - Parse file-open log.
    - Assert every empirical input is under selected release root.
    - Assert no `results/` input.

20. **Build source-of-truth bundle.**
    - One authoritative machine-readable source per planned exhibit.
    - Write analysis manifest and SHA-256 checksums.
    - Create `table_to_csv_map.md` and figure bindings.

21. **Update claims.**
    - Accept, narrow, omit, or block each planned empirical claim.
    - Record negative and unstable findings.
    - Do not create ablation claims.

22. **Orphan checks.**
    - Every planned number has a row in
      `primary_stats/statistical_results.csv` (Section 7.14 schema).
    - Every output intended for publication maps to a claim/exhibit.
    - No number exists only in stdout or prose.

23. **Export paper-table staging CSVs.**
    - From the authoritative controlled analysis bundle
      (`papers/analysis/<release_id>/`, Section 7.13), export the T1–T16 input
      CSVs — and, conditional on sensitivity admissibility (task 14 and
      Section 4.4), T21/T22 — into `results/paper_tables/`, the rendered-input
      staging area consumed by the table generators.
    - Record bundle provenance (release ID, source paths, checksums) with
      every exported CSV.
    - Never populate `results/paper_tables/` from any other source.

### Generated outputs

- suite analysis bundles for CEC2017, CEC2011, and CEC2013 under
  `papers/analysis/<release_id>/`;
- `primary_stats/` machine-readable registry outputs, including the
  authoritative `primary_stats/statistical_results.csv` (Section 7.14 schema);
- `results/paper_tables/` exported table-input CSVs with bundle provenance;
- `headline_bca.csv`;
- effect-size outputs;
- `curve_selection.csv`;
- convergence aggregate data;
- robustness outputs;
- cost outputs when admissible;
- `analysis_source_use.log`;
- `analysis_manifest.json`;
- `analysis_checksums.sha256`;
- `table_to_csv_map.md`;
- updated claims/exhibit plans;
- `results_validation_report.md`.

### Validation procedures

- schema and range validation;
- task/function denominator checks;
- raw-to-summary reconstruction;
- paired-key alignment checks;
- correction-family checks;
- effect direction checks;
- interval seed/resampling checks;
- deterministic rerun comparison;
- orphan number/output checks.

### Verification procedures

- P3 independently verifies critical statistics.
- P4 verifies source rows, task scope, and denominators.
- P5 verifies source-use log, hashes, commands, and determinism.
- P9 checks claim wording against actual outputs.

### Quality-assurance checkpoints

- no forbidden input path;
- no p-value without test design and family;
- no significance without effect and uncertainty where planned;
- no rank from rounded values;
- no cherry-picked curve;
- no hidden unfavorable result;
- no ablation analysis.

### Acceptance criteria

- all primary analyses execute from immutable reference evidence only;
- outputs are deterministic and checksummed;
- every headline claim has valid statistics/effect/interval as planned;
- every exhibit has one authoritative data source;
- robustness outcomes are disclosed;
- claims matrix reflects actual evidence;
- no orphan or fabricated number exists.

### Exit criteria

Phase 6 freezes after P3/P4/P5/P9 sign-off. Any later change to source release,
algorithm, endpoint, or analysis plan invalidates affected outputs and claims.

### Risks

| Risk | Impact |
|---|---|
| source guard bypass | evidence violation |
| analysis-code bug | false results |
| invalid pairing discovered | inferential scope loss |
| deterministic drift | irreproducible statistics |
| unfavorable results | contribution narrowing |

### Assumptions

- selected release contains required raw/per-run data;
- statistical libraries are available and versioned; and
- deterministic sorting and RNG control are feasible.

### Mitigation strategies

- fail closed on source path;
- independent recomputation;
- shift invalid tests to descriptive reporting;
- record version/seed/thread controls;
- narrow claims rather than altering algorithm or data.

### Deliverables

All generated outputs plus `PHASE_6_gate_report.md` with source-only proof,
analysis summary, determinism result, negative findings, and accepted/narrowed
claims.

### Review gate

**Gate 6:** P3 + P4 + P5 + P9 approve. Any empirical input outside the evidence
release, unreconciled statistic discrepancy, invalid inferential design, or
orphan number is a hard failure.

---

## Phase 7 — Primary tables, figures, equations, and method-artifact production

### Objective

Generate every non-ablation scientific exhibit and formal method artifact from
accepted Phase 6 outputs and frozen Phase 3 specifications, with complete source
bindings and publication-quality presentation.

### Expected outcomes

- regenerated primary tables and figures;
- complete equations, algorithms, notation, and method diagrams;
- source-to-artifact bindings and checksums;
- clear main/supplement split;
- no hand-edited data;
- no ablation output.

### Entry criteria

- Phases 0–6 are frozen;
- authoritative primary analysis bundle exists;
- `results/paper_tables/` inputs exist and carry bundle provenance (Phase 6
  task 23);
- claims and exhibit plans are updated to actual evidence;
- algorithm remains frozen.

### Prerequisites

- source-of-truth CSV/JSON files;
- artifact generators;
- method registries;
- target-journal figure/table requirements;
- canonical cross-reference label tracking (Section 9.1): the labels assigned
  in the Phase 4 task 8 exhibit plan, carried forward in
  `artifact_binding.csv` (`manuscript_label`) once task 11 below creates it.

### Required inputs

- Phase 3 method artifacts;
- Phase 6 primary analysis bundle;
- immutable curve/checkpoint evidence;
- approved conceptual-art specifications (`conceptual_figure_specs.md`,
  Phase 4 task 8);
- journal template dimensions.

### Dependencies

Phases 3, 4, and 6. No Phase 12 ablation source is available or allowed.

### Detailed implementation tasks

1. **Audit generators before execution.**
   - Inspect empirical inputs.
   - Import/smoke-check every generator before execution; a missing input MUST
     fail hard, never be silently skipped or defaulted.
   - Replace or wrap any non-authoritative input with strict
     reference/authoritative analysis input. Non-authoritative inputs include
     any `results/` path (`results/paper_tables/` exports from Phase 6 task 23
     are the sole admissible rendered-input staging) and any value parsed from
     a rendered `.tex` or other manuscript artifact.
   - Verify each generator's output destination resolves inside the framework
     layout (`papers/tables/`, `papers/figures/`); repair any stray
     destination (a historical `generate_parametric_tables.py` defect wrote to
     `paper/tables/`) as named tooling work before execution.
   - Confirm deterministic output naming and sorting.

2. **Regenerate primary LaTeX tables.**

   ```powershell
   python papers/scripts/generate_latex_tables.py
   python papers/scripts/generate_t16_bca.py
   ```

   - Suppress or disable ablation-table generation until Phase 12 by an
     explicit mechanism: before invoking `generate_latex_tables.py`, assert
     that `results/ablation/` contains no `ablation_matrix_rank_summary*.csv`
     (the script has no skip flag and emits `ablation_<tag>.tex` for every
     matrix it finds) and quarantine any found matrices per Phase 2 task 13,
     or add a `--skip-ablation` flag as named tooling work.
   - **[RETIRED 2026-07-15]** T21/T22 and their generator
     `generate_parametric_tables.py` were REMOVED as prohibited favorable
     component-ablation exhibits (commit `16ce59439`). Do not regenerate or
     re-admit them under any condition; record the disposition in
     `exhibit_plan.csv` and `evidence_gap_register.md`.
   - Preserve expected T01–T16, T16_bca, T21, T22 mapping only when verified.
   - Do not create T17–T20 merely to fill numbering.

3. **Generate primary performance figures.**

   ```powershell
   python papers/scripts/generate_full_convergence.py
   python papers/scripts/generate_cec2011_convergence.py
   python papers/scripts/generate_cec2013_convergence.py --dimension 30
   python papers/scripts/generate_nemenyi_cd.py
   python papers/scripts/generate_rank_charts.py
   ```

   - Bind to Phase 6 curve selection and analysis outputs.
   - Before rendering, complete the Section 8.5 family-overlay tooling task
     (CR-0001): extend the three per-suite convergence generators from
     two-series (GSK vs DT-GSK) to the seven-curve family overlay of
     Section 6.7, following `generate_review_pack.py`'s implementation
     pattern; then validate that every rendered convergence panel contains
     exactly seven series or a disclosed caption-level absence note.
   - Rewire `generate_nemenyi_cd.py` (named tooling work) to read unrounded
     mean ranks from the authoritative Phase 6 bundle (the
     `<suite>_friedman_ranks.csv` outputs, Section 7.13) instead of parsing
     the 2-decimal rounded values from `papers/tables/T16.tex`; one rendered
     exhibit MUST NOT be the data source of another.
   - Log missing inputs; never interpolate.

4. **Generate conceptual/method figures.**

   ```powershell
   python papers/scripts/generate_trace_figures.py
   python papers/scripts/generate_nlpsr_trajectory.py
   python papers/scripts/generate_adaptive_params_panel.py
   ```

   (The architecture flowchart and taxonomy exhibits are native tables now;
   their matplotlib generators were removed — 2026-07-15 status note.)

   - Verify every label against frozen terminology.
   - Data-backed traces must use admissible evidence; conceptual diagrams must
     not imply unverified behavior.

5. **Finalize equations and pseudocode.**
   - Use canonical equation registry.
   - Check every symbol, number, update order, and code mapping.
   - Prepare LaTeX and Word semantic representations.

6. **Finalize table selection.**
   - Main: concise protocol, primary summaries, inference/effect, secondary
     evidence, sensitivity if valid, cost.
   - Supplement: complete per-function tables, matrices, full curves, extended
     primary diagnostics.
   - No ablation table or figure yet.

7. **Apply visual standards.**
   - Final-size fonts, accessible palette, grayscale line styles, vector output,
     units, log labels, consistent scales, uncertainty, and no misleading axes.

8. **Write self-contained captions.**
   - Suite, dimension, metric, aggregation, n, uncertainty, significance rule,
     source release, and limitation where needed.
   - Do not put unsupported interpretation in captions.

9. **Create native table data for Word.**
   - Export semantic table JSON/CSV with headers, notes, styles, and field IDs.
   - Do not convert LaTeX-rendered tables to images.

10. **Create editable diagram sources.**
    - DrawingML/SmartArt plan or `.drawio`/`.pptx` source.
    - Ensure embedded render and source are synchronized.

11. **Bind artifacts.**
    - Create `artifact_binding.csv` in the governance root (Section 3.8
      schema; this phase first populates it, per the Section 3 preamble) or
      update it with generator, command, sources, checksums, label,
      main/supplement destination, and Word destination.
    - Maintain the Section 9.1 cross-reference labels here: seed
      `manuscript_label` from the Phase 4 exhibit plan and keep it current.

12. **Value-level validation.**
    - Compare every displayed table value with authoritative source.
    - Sample or fully validate figure points against source arrays.
    - Check ranks/significance use unrounded data.

13. **Legibility review.**
    - Inspect at target column/page size and grayscale.
    - Correct layout, not data.

14. **Orphan and duplication review.**
    - Every artifact has a planned discussion.
    - Remove redundant exhibits.
    - Route missing evidence back to Phase 6 rather than hand-authoring.

### Generated outputs

- final non-ablation `papers/tables/*.tex`;
- semantic Word table sources;
- final non-ablation `papers/figures/**`;
- editable diagram sources;
- notation, equation, algorithm, and parameter artifacts;
- created/updated `artifact_binding.csv`;
- `exhibit_validation_report.md`;
- `visual_qa_report.md`.

### Validation procedures

- full table cell comparison;
- figure source/point and metadata checks;
- label uniqueness and cross-reference registry checks;
- caption completeness;
- vector/raster resolution checks;
- grayscale/accessibility review;
- automated figure-QA checks (CR-0003) for horizontal/vertical overflow,
  clipped text, illegible or cropped legends, inconsistent fonts,
  inconsistent algorithm ordering, wrong function/dimension labels, missing
  curves, duplicate curves, empty panels, inappropriate scaling, and
  excessive raster compression;
- a recorded visual inspection pass over every figure (CR-0003);
- no-ablation artifact scan.

### Verification procedures

- P2 verifies method artifacts.
- P3 verifies statistical marks and captions.
- P5 verifies generators and source bindings.
- P7 performs final-size visual inspection.
- P8 verifies Word-native source suitability.

### Quality-assurance checkpoints

- zero hand-typed result values;
- zero unbound exhibit;
- zero unexplained missing input;
- zero illegible main-text artifact;
- no ablation artifact;
- consistent terminology and labels.

### Acceptance criteria

- every primary exhibit regenerates from named authoritative inputs;
- every value/point is validated;
- captions are self-contained and scoped;
- method equations/pseudocode/code agree;
- main/supplement split is appropriate;
- Word-native sources exist;
- no ablation appears.

### Exit criteria

Phase 7 freezes after P2/P3/P5/P7/P8 sign-off. A later changed analysis output
requires exhibit regeneration and revalidation.

### Risks

| Risk | Impact |
|---|---|
| generator reads staging data | evidence violation |
| stale LaTeX fragment | wrong manuscript value |
| figure cherry-picking | biased presentation |
| inaccessible graphics | editorial failure |
| LaTeX-only table design | non-editable Word output |

### Assumptions

- generators can be modified without changing analysis logic;
- source data are complete; and
- target journal accepts the chosen figure formats.

### Mitigation strategies

- strict source assertions;
- regenerate every data-backed artifact;
- pre-specified curve selection;
- semantic table/figure source model;
- visual inspection and accessible encodings.

### Deliverables

All generated outputs plus `PHASE_7_gate_report.md` with full artifact inventory,
source-binding coverage, visual QA, and no-ablation confirmation.

### Review gate

**Gate 7:** P2 + P3 + P5 + P7 + P8 approve. A hand-edited result, unbound
artifact, illegible exhibit, or ablation content fails the gate.

---

## Phase 8 — Evidence-first main-manuscript and pre-ablation supplement drafting

### Objective

Draft the complete main manuscript and all non-ablation supplementary content
using only accepted claims, approved citations, frozen method artifacts, and
validated primary exhibits.

### Expected outcomes

- complete evidence-bound main manuscript;
- complete non-ablation supplement;
- updated claims and citation maps;
- consistent title, abstract, contributions, results, limitations, and
  conclusion;
- no unsupported or ablation content.

### Entry criteria

- Phases 0–7 are frozen;
- every planned primary number and exhibit is validated;
- citation set/evidence cards are complete;
- journal structure is verified.

### Prerequisites

- outline/page budget;
- accepted claims matrix;
- citation role map;
- primary artifacts and bindings;
- method specification;
- journal instructions.

### Required inputs

- canonical manuscript source (`papers/main.tex` plus `papers/sections/*.tex`
  and `papers/supplementary.tex`, together with the Section 9.1 registries, as
  defined in Phase 4 task 7 and recorded in `project_configuration.md`);
- existing draft prose for audit/rewrite only;
- Phase 1 literature evidence;
- Phase 6–7 outputs;
- target template and style rules.

### Dependencies

Phases 1, 3, 4, 6, and 7.

### Detailed implementation tasks

1. **Use the deliberate drafting order.**
   1. Problem formulation and baseline GSK.
   2. Proposed method.
   3. Experimental setup.
   4. Primary results.
   5. Discussion and limitations.
   6. Related work.
   7. Introduction.
   8. Conclusion.
   9. Abstract and title.
   10. Declarations and cover letter scientific core.

2. **Run the per-section evidence loop.**
   - Select accepted claim IDs.
   - Build paragraph skeleton with claim/evidence anchors.
   - Insert citations only from approved keys and sanctioned roles.
   - Bind every number to an analysis/artifact ID while writing.
   - Add cross-references immediately.
   - Update claims and citation-usage maps.
   - Check scope, limitations, terminology, and budget.

3. **Draft problem/baseline section.**
   - Separate inherited GSK from new material.
   - Define notation and optimization problem.

4. **Draft proposed method.**
   - Follow problem → rationale → mechanism → timing → cost → expected behavior
     → planned test.
   - Mark contribution boundaries.
   - Do not report ablation outcomes.

5. **Draft experimental setup.**
   - Evidence release, suites, function sets, dimensions, runs, seeds, pairing,
     MaxFES, panel, parameters, environment, FP, source-resolution, failures,
     statistical plan, availability.
   - State strict reference-only empirical rule.

6. **Draft primary results.**
   - Measurement before interpretation.
   - Primary suite, inference, effects/intervals, convergence, secondary suites,
     sensitivity, cost, robustness.
   - Report exceptions and losses.
   - No ablation subsection or result.

7. **Draft discussion and limitations.**
   - Interpret within evidence.
   - Label mechanism hypotheses.
   - Address same-family, benchmark, dimension, tuning, comparator, statistical,
     and cost limits.
   - State that component-level ablation is reserved for Supplementary Materials
     after final algorithm freeze only if a neutral pointer is appropriate; do
     not preview results.

8. **Draft related work from evidence cards.**
   - Comparative synthesis, not bibliography catalogue.
   - Use exact source locators and role map.

9. **Draft introduction and contributions.**
   - Do not promise more than primary evidence and final contribution matrix.
   - Contributions about components describe the mechanism and evaluation
     framework, not unobserved ablation benefits.

10. **Draft conclusion.**
    - Primary evidence only.
    - No ablation claim or new result.

11. **Draft abstract last.**
    - Journal limit.
    - One or two bound primary numbers.
    - Honest scope.
    - No citation if prohibited and no ablation.

12. **Draft non-ablation supplementary content.**
    - Complete tables, curves, pairwise matrices, sensitivity, reproducibility,
      derivations, traces.
    - Reserve a clearly marked internal placeholder section ID for Phase 12
      ablation, but do not include result text, tables, or guessed conclusions.
      The placeholder MUST not appear in released drafts.

13. **Draft declarations.**
    - Use verified metadata only.
    - Populate administrative gaps without invention.

14. **Perform claim/citation audit.**
    - Every scientific paragraph has appropriate evidence anchor.
    - Every citation has usage-map row and evidence-card support.
    - Every number has authoritative binding.

15. **Perform writing-quality pass.**
    - Specific, calibrated, non-promotional prose.
    - Remove stock transitions and generic claims.
    - Preserve facts/citations/numbers.

16. **Check page budget (Section 1.5 hard rule).**
    - Read the measured typeset page count from the compiled draft PDF's build
      log ("Output written on ... pages") — never estimate.
    - Compare against the verified target-journal limit recorded at Phase 4
      (or the Section 1.5 provisional ceiling when verification is pending).
    - On overflow: migrate non-essential material (extended tables, additional
      figures, detailed derivations, comprehensive experimental results,
      supporting analyses) to the supplement per Section 8.6 — the only
      permitted relief valve.
    - Do not shrink artifacts below legibility, delete required declarations,
      or compress prose past comprehensibility.
    - Record the page-count row in
      `papers/governance/phase_gate_register.csv`.

### Generated outputs

- complete canonical main manuscript draft;
- `papers/main.tex` draft;
- pre-ablation `papers/supplementary.tex` draft;
- section files;
- updated `claims_evidence_matrix.csv`;
- `citation_usage_map.csv`;
- `drafting_decisions.md`;
- `paragraph_evidence_audit.csv`;
- `administrative_gap_register.md` updates.

### Validation procedures

- claim coverage check;
- citation-set and semantic-role checks;
- number-binding scan;
- cross-reference/label scan;
- acronym/terminology/symbol checks;
- no-ablation keyword/artifact scan;
- page/word budget estimate.

### Verification procedures

- P2 verifies method prose.
- P3 verifies setup/results/statistical wording.
- P4 verifies protocol/provenance statements.
- P6 performs evidence-aware editorial review.
- P9 independently samples paragraphs against claims/evidence cards.

### Quality-assurance checkpoints

- every scientific paragraph evidence-anchored;
- no unsupported novelty/superiority;
- no orphan number/citation;
- losses and limitations visible;
- no main-text ablation;
- abstract written last and scoped.

### Acceptance criteria

- complete main and non-ablation supplementary source;
- all scientific claims accepted and bound;
- all citations semantically valid;
- all numbers traceable;
- manuscript fits provisional/verified budget;
- no ablation content or guessed result;
- administrative gaps explicit.

### Exit criteria

Phase 8 freezes after P2/P3/P4/P6/P9 sign-off. Subsequent changes occur through
review tickets and preserve evidence bindings.

### Risks

| Risk | Impact |
|---|---|
| prose copied from stale draft | unbound claims |
| paragraph citation quota | decorative citations |
| abstract overclaim | editorial/reviewer rejection |
| ablation preview | phase-order violation |
| generic writing | weak scientific communication |

### Assumptions

- accepted claims are sufficient for a coherent primary paper;
- non-ablation primary evidence supports the central thesis; and
- missing administrative data can remain isolated.

### Mitigation strategies

- write from claim IDs, not old prose;
- split/rewrite paragraphs for semantic citations;
- bind abstract numbers last;
- automated no-ablation scan;
- dedicated scientific editor pass.

### Deliverables

All generated outputs plus `PHASE_8_gate_report.md` with claim/citation/number
coverage, page budget, no-ablation proof, and section sign-offs.

### Review gate

**Gate 8:** P2 + P3 + P4 + P6 + P9 approve. Unsupported prose, semantic
citation failure, orphan number, hidden loss, or any ablation result fails the
gate.

---

## Phase 9 — Dual-format LaTeX/PDF and native Microsoft Word production

### Objective

Render the complete pre-ablation manuscript and non-ablation supplement into
publication-quality LaTeX/PDF and fully editable native Word documents, then
prove semantic and numerical equality across formats.

### Expected outcomes

- clean main PDF and pre-ablation supplementary PDF;
- fully editable main DOCX and pre-ablation supplementary DOCX;
- native OMML equations, Word tables, captions, fields, citations, and
  cross-references;
- complete Word/OOXML validation report;
- cross-format consistency registry;
- no ablation content.

### Entry criteria

- Phases 0–8 are frozen;
- canonical manuscript source is complete;
- equation, exhibit, and citation registries exist (`equation_registry.csv`,
  `artifact_binding.csv`, and the Phase 1 citation maps); the canonical label
  registry is constructed from these registries and the Phase 7
  label-uniqueness checks during task 1 — it is not assumed to pre-exist;
- journal template and Word requirements are known.

### Prerequisites

- canonical source;
- LaTeX class/template;
- `reference.docx` or approved Word template;
- bibliography and Word citation-tag map;
- semantic table and equation sources;
- editable diagram sources;
- build and validation tooling.

### Required inputs

- main and pre-ablation supplementary sources;
- all non-ablation artifacts;
- `artifact_binding.csv`;
- `equation_registry.csv`;
- `word_citation_tag_map.csv`;
- journal requirements.

### Dependencies

Phases 7–8. Phase 9 outputs are reviewed and finalized in Phases 10–11.

### Detailed implementation tasks

1. **Freeze the canonical source snapshot.**
   - Record content hash, label registry, citation set, figure/table inventory,
     and claim-matrix version.

2. **Build LaTeX main manuscript.**

   ```powershell
   python papers/scripts/build_pdf.py
   ```

   - Capture complete logs and output checksum.
   - Resolve undefined references/citations, missing figures, fatal warnings,
     and harmful overfull boxes.

3. **Build pre-ablation supplement.**

   ```powershell
   python papers/scripts/build_supplementary.py
   ```

   - Ensure it is standalone.
   - Do not emit a visible empty ablation section.

4. **Build review pack when supported.**

   ```powershell
   python papers/scripts/generate_review_pack.py
   ```

   - Treat missing-curve logs as defects unless explicitly explained.
   - The review pack is an internal advisor artifact: it reads staging inputs
     (`results/_run_all/...`, `results/gsk/...`), is excluded from publication
     evidence and from the submission package, and MUST NOT be cited as the
     source of any manuscript value.

5. **Create or verify Word reference template.**
   - Journal page size, margins, fonts, styles, headings, captions, lists,
     tables, equations, code/algorithm styles, references, and metadata.
   - Do not distribute proprietary font files.

6. **Implement or extend the Word pipeline tooling (tooling to build).**
   - Extend `papers/scripts/build_docx.py` (Sections 4.1 and 9.5, Appendix
     D.6): add a `--supplementary` entry point consuming
     `papers/supplementary.tex`, wire the task 5 `word/reference.docx` into
     the pandoc invocation via `--reference-doc`, and add an OOXML
     post-processing stage over the pandoc output that injects `SEQ` and
     `REF` fields, bookmarks with stable IDs, a native TOC field, and
     `CITATION` fields plus a `customXml` bibliography source store.
   - Implement the missing validators `papers/scripts/validate_docx.py`,
     `papers/scripts/validate_cross_format_parity.py`, and
     `papers/scripts/validate_evidence_bindings.py` (Appendix D.6).
   - Record the implemented commands and the output-filename mapping
     (`build_docx.py` writes `papers/DT-GSK.docx`, not `papers/main.docx`)
     in `project_configuration.md`.

7. **Generate main DOCX from canonical source.**

   ```powershell
   python papers/scripts/build_docx.py
   ```

   - Use the OOXML-aware deterministic pipeline from task 6; the output maps
     to `papers/DT-GSK.docx` per the recorded filename mapping.
   - Do not convert the PDF.
   - Preserve section structure, fields, citations, tables, equations, figures,
     footnotes, and hyperlinks.

8. **Generate pre-ablation supplementary DOCX.**

   ```powershell
   python papers/scripts/build_docx.py --supplementary
   ```

   - Use the task 6 `--supplementary` entry point with the same semantic
     registries and style system.
   - Preserve independent numbering as journal rules require.

9. **Generate native OMML.**
   - Convert every equation registry entry to `m:oMath` or `m:oMathPara`.
   - Verify inline/display distinction, matrices, scripts, operators, accents,
     delimiters, and special symbols.
   - Keep numbering as fields, not equation images.

10. **Generate native Word tables.**
   - Build `w:tbl` from semantic table sources.
   - Apply header, alignment, width, note, and accessibility properties.
   - Preserve exact values and display precision.

11. **Generate captions, numbering, and references.**
    - `SEQ` fields for figures, tables, algorithms, and equations.
    - `REF` fields for every cross-reference.
    - bookmarks with stable IDs.
    - multilevel lists for section numbering.

12. **Generate updateable citations and bibliography.**
    - Native Word `CITATION` fields and source store, or approved dynamic
      reference-manager fields.
    - Native `BIBLIOGRAPHY` field.
    - Verify source metadata against the closed corpus and BibTeX.

13. **Generate TOC and lists.**
    - Native TOC, list of figures, list of tables, and list of algorithms if
      required.
    - Set update-on-open behavior.

14. **Embed figures and diagrams.**
    - Vector where supported.
    - Editable captions and alt text.
    - Native DrawingML or linked editable source for diagrams/flowcharts.

15. **Inspect OOXML package.**
    - Unzip DOCX to a temporary validation directory.
    - Count and validate OMML, tables, fields, bookmarks, relationships, images,
      source store, and update fields.
    - Verify no equation/table screenshot.

16. **Open-save-open validation.**
    - When Microsoft Word is available, open, update fields, save, reopen, and
      rerun OOXML checks.
    - Record version and any repair message.
    - A document that Word repairs on open fails.

17. **Cross-format text and structure comparison.**
    - Compare normalized headings, paragraphs, equations, table values,
      captions, citations, bibliography entries, labels, and cross-references.
    - Record intentional format-only differences.

18. **Visual inspection.**
    - Every PDF page.
    - Every Word page/section in print layout.
    - Check equation wrapping, table breaks, figure placement, captions,
      headings, widows/orphans, references, and accessibility.

19. **No-ablation scan.**
    - Search main and supplement outputs, fields, captions, and hidden text for
      ablation results or historical ablation values.
    - Neutral internal placeholders must not be rendered.

20. **Create build reports and hashes.**
    - Source hash, command, environment, output hash, warnings, page count,
      field counts, and validation status.

### Generated outputs

- pre-ablation main PDF: `papers/DT-GSK.pdf` (`build_pdf.py` moves `main.pdf`
  to `DT-GSK.pdf` on success — record this mapping in
  `project_configuration.md` per Section 1.2 and validate against the mapped
  name, not `papers/main.pdf`);
- pre-ablation main DOCX: `papers/DT-GSK.docx` (same recorded mapping);
- pre-ablation `papers/supplementary.pdf`;
- pre-ablation `papers/supplementary.docx` (task 6 `--supplementary` entry
  point);
- `word/reference.docx`;
- Word bibliography source store;
- `word/field_registry.csv`;
- `word_validation_report.md`;
- `cross_format_consistency.csv`;
- `latex_build_report.md`;
- `word_build_report.md`;
- `visual_inspection_report.md`.

### Validation procedures

- LaTeX log scan;
- PDF file/font/figure checks;
- DOCX OOXML schema/relationship checks;
- OMML equation registry comparison;
- native Word table value comparison;
- field, bookmark, TOC/list, citation, and bibliography checks;
- cross-format content hashes by logical artifact;
- no-ablation scan.

### Verification procedures

- P7 independently reviews PDF/build quality.
- P8 independently reviews DOCX/OOXML and editability.
- P5 verifies deterministic builds and hashes. The determinism contract is
  normalized-content equality (text, OMML, table values, field inventory)
  with `SOURCE_DATE_EPOCH` set and PDF (`CreationDate`/`ModDate`/`ID`) and
  DOCX (`docProps` timestamps) metadata normalized before hashing — not raw
  byte identity (Section 9.4).
- P6 verifies wording/structure equality.
- P9 verifies citation and number integrity.

### Quality-assurance checkpoints

- zero equation image;
- zero table image;
- all captions editable;
- all required fields updateable;
- all cross-references functional;
- Word opens without repair;
- PDF and Word content equivalent;
- no ablation content.

### Acceptance criteria

- clean main and pre-ablation supplementary PDFs;
- fully editable main and supplementary DOCX;
- all equations native OMML;
- all tables native Word tables;
- automatic numbering, cross-references, TOC/lists, citations, and bibliography
  work;
- cross-format consistency passes;
- visual quality meets journal requirements;
- no ablation is present.

### Exit criteria

Phase 9 freezes after P5/P6/P7/P8/P9 sign-off. Any later content revision
requires rebuilding and revalidating both formats.

### Risks

| Risk | Impact |
|---|---|
| converter rasterizes equations | Word requirement failure |
| static citation text | non-updateable bibliography |
| Word field update changes numbering | broken cross-references |
| PDF/Word divergence | inconsistent submission |
| complex tables overflow | poor editability |

### Assumptions

- an OOXML-aware generation path is available or can be implemented;
- Microsoft Word validation is available before final submission or a documented
  compatible test environment exists; and
- target journal accepts Word equation fields and native tables.

### Mitigation strategies

- post-process OOXML with verified transformations;
- generate tables/equations from semantic sources;
- use native Word bibliography source store;
- maintain stable label/field registry;
- simplify layout without flattening content.

### Deliverables

All generated outputs plus `PHASE_9_gate_report.md` with PDF/Word checks,
field/OMML/table counts, cross-format status, page counts, and no-ablation proof.

### Review gate

**Gate 9:** P5 + P6 + P7 + P8 + P9 approve. Rasterized mathematics, image
 tables, static required fields, broken references, format divergence, or any
ablation result is a hard failure. As the sole exception, a journal-approved
static-field fallback is acceptable when the journal's approval is documented
and the fallback is recorded as a deviation in `word_validation_report.md`
(in `papers/governance/`).

---

## Phase 10 — Adversarial scientific, statistical, reproducibility, editorial, and Word review

### Objective

Subject the complete pre-ablation publication to independent hostile review,
resolve every critical or major issue, and produce a scientifically final main
manuscript candidate without changing the frozen algorithm.

### Expected outcomes

- independent reviewer reports;
- complete revision-ticket trail;
- corrected analyses/artifacts/prose where needed;
- no open critical/major issue;
- updated dual-format builds;
- main manuscript ready for final pre-ablation freeze.

### Entry criteria

- Phases 0–9 are frozen;
- both formats build and validate;
- claims, citations, and numbers are fully bound;
- no ablation content exists.

### Prerequisites

- all reviewer rubrics;
- current main/supplement PDF and Word files;
- governance, evidence, analysis, and build artifacts;
- claims matrix and predicted reviewer risks.

### Required inputs

- complete pre-ablation publication package;
- source and validation reports;
- current journal requirements;
- risk and decision registers.

### Dependencies

All preceding phases.

### Detailed implementation tasks

1. **Run R1 scientific review.**
   - Importance and problem specificity.
   - Contribution novelty boundary.
   - Same-family scope.
   - Mechanism distinction.
   - Baseline strength.
   - External validity.
   - Losses and limitations.

2. **Run R2 methodology/statistics review.**
   - Endpoint, units, pairing, independence.
   - Multiplicity families.
   - Friedman/Nemenyi validity.
   - Wilcoxon validity.
   - A12 and BCa design.
   - Robustness checks.
   - No causal component claims before ablation.

3. **Run R3 reproducibility review.**
   - Evidence release.
   - Source-only audit.
   - seeds, MaxFES, FP, environment.
   - command determinism.
   - code/equation/prose correspondence.
   - artifact bindings.

4. **Run R4 editorial/presentation review.**
   - narrative, clarity, section balance.
   - figure/table legibility.
   - captions and cross-references.
   - journal structure and language.
   - unsupported rhetoric.
   - exemplar parity (CR-0002, CR-0003): section-by-section comparison
     against `papers/governance/presentation_conventions.md` and the three
     Section 8.7 exemplars; every unjustified deviation from the registered
     conventions is a ticket.

5. **Run R5 Word review.**
   - OMML editability.
   - native tables.
   - fields, bookmarks, citations, bibliography.
   - TOC/lists.
   - update/open/save behavior.
   - visual parity with PDF.

6. **Run R6 skeptical domain review.**
   - challenge SGSM versus differential grouping.
   - challenge linkage/eigenframe positioning.
   - challenge “no additional objective evaluations” and overhead.
   - challenge dimension labels.
   - challenge CEC2013 role and development leakage.
   - identify likely failure cases and missing limitations.

7. **Score every rubric category 1–5.**
   - Any score below 4 creates a mandatory ticket.
   - A score of 5 requires explicit evidence.

8. **Create revision tickets.**
   - `critical`, `major`, `minor`, or `editorial`.
   - Include claim/evidence IDs, affected phases, fix, verification, and owner.

9. **Resolve tickets in severity order.**
   - Prose-only fix: preserve evidence and rebuild both formats.
   - Analysis fix: reopen Phase 5/6 through change control, rerun, regenerate
     exhibits, update claims, rebuild both formats.
   - Method description fix: reconcile with frozen code; do not change code.
   - Missing primary evidence: narrow/remove claim; do not run early ablation.
   - Journal/Word fix: update template/generator and revalidate.

10. **Maintain response log.**
    - Quote issue, action, exact section/artifact, evidence, and verification.
    - Declined suggestions need principled reason.

11. **Rerun affected reviewers.**
    - Review touched sections and dependent artifacts.
    - Repeat until no critical/major issue.

12. **Run post-revision integrity checks.**
    - Citation semantic check.
    - Number binding.
    - source-only audit.
    - cross-format consistency.
    - no-ablation scan.
    - engineering gates.

13. **Perform style-only final edit.**
    - Improve clarity and cadence.
    - Verify diff changes no facts, numbers, citations, equations, or scope.

14. **Prepare main-manuscript finalization candidate.**
    - Resolve all primary scientific content.
    - Ensure final ablation cannot be used to justify existing main claims.
    - Identify claims that final ablation could contradict and define correction
      triggers for Phase 12.

### Generated outputs

- `review_R1_scientific.md`
- `review_R2_statistics.md`
- `review_R3_reproducibility.md`
- `review_R4_editorial.md`
- `review_R5_word.md`
- `review_R6_domain.md`
- `revision_tickets.csv`
- `revision_log.md`
- `response_to_reviewers_seed.md`
- revised canonical/LaTeX/Word sources and builds;
- updated validation reports;
- `ablation_correction_triggers.md`.

### Validation procedures

- all reviewer scores recorded;
- all critical/major tickets closed with verification;
- dependent phases rerun when required;
- citation/number/source/cross-format/no-ablation checks repeated;
- style diff verified.

### Verification procedures

- P1 verifies scientific resolution.
- P3 verifies statistical fixes.
- P5 verifies reproducibility after changes.
- P6/P7/P8 verify editorial/PDF/Word output.
- P9 checks research integrity.

### Quality-assurance checkpoints

- no silent ticket closure;
- no algorithm change;
- no new unregistered analysis;
- no early ablation;
- no claim expansion after results;
- all formats synchronized.

### Acceptance criteria

- every reviewer category scores at least 4/5;
- zero open critical or major ticket;
- all fixes verified;
- primary claims remain evidence-bounded;
- both formats build and validate;
- no ablation content;
- correction triggers are explicit.

### Exit criteria

Phase 10 freezes after P1/P3/P5/P6/P7/P8/P9 sign-off. Minor/editorial tickets
may remain only if non-material, documented, and scheduled before Phase 11 gate.

### Risks

| Risk | Impact |
|---|---|
| review fix expands scope | new unsupported claim |
| analysis fix changes headline | narrative drift |
| Word fix alters content | cross-format mismatch |
| reviewer requests ablation early | phase-order violation |
| unresolved major issue | invalid finalization |

### Assumptions

- reviewers can access all evidence/governance artifacts;
- algorithm changes are unnecessary after freeze; and
- primary paper can stand without ablation.

### Mitigation strategies

- use change-control reruns;
- narrow claims;
- synchronize from canonical source;
- reject early-ablation request and explain supplement-final design;
- keep gate closed until major issues resolve.

### Deliverables

All generated outputs plus `PHASE_10_gate_report.md` with reviewer scores,
closed-ticket evidence, remaining minor issues, and finalization readiness.

### Review gate

**Gate 10:** P1 + P3 + P5 + P6 + P7 + P8 + P9 approve. Any open critical/major
issue, algorithm change, analysis without change control, or ablation leakage
fails the gate.

---

## Phase 11 — Primary manuscript finalization and pre-ablation freeze

### Objective

Complete all non-ablation research, statistical validation, editorial work,
current journal compliance, and dual-format manuscript finalization; freeze the
main manuscript and primary evidence baseline before any ablation run begins.

### Expected outcomes

- scientifically finalized main manuscript;
- finalized non-ablation supplementary core;
- clean PDF and native Word builds;
- current journal-compliance proof;
- frozen primary evidence/analysis/artifact package;
- signed Phase 12 entry certificate;
- no open material issue.

### Entry criteria

- Phases 0–10 are frozen;
- zero critical/major review ticket;
- all primary analyses and artifacts are stable;
- both main formats and pre-ablation supplement formats validate;
- algorithm remains frozen.

### Prerequisites

- current official journal instructions;
- final review reports;
- all governance, evidence, analysis, source, and build artifacts;
- administrative metadata available or explicitly blocked.

### Required inputs

- finalization candidate main manuscript;
- pre-ablation supplement;
- journal template/checklist;
- evidence and algorithm freeze manifests;
- build/Word validation reports;
- correction-trigger plan.

### Dependencies

All previous phases. Phase 12 cannot start without Phase 11 acceptance.

### Detailed implementation tasks

1. **Reverify current journal instructions.**
   - Record new access date and detect changes since Phase 4.
   - Apply current structure, limits, artwork, Word/LaTeX, supplement,
     anonymization, declaration, and AI-disclosure rules.

2. **Finalize all minor/editorial tickets.**
   - Close or document non-material residuals.
   - Rebuild both formats after changes.

3. **Run complete primary integrity audit.**
   - citations;
   - claims;
   - numbers;
   - source-only evidence;
   - equations/pseudocode/code;
   - tables/figures;
   - cross-document consistency;
   - Word native fields/editability;
   - journal compliance.

4. **Run clean builds.**

   ```powershell
   python papers/scripts/build_pdf.py
   python papers/scripts/build_supplementary.py
   python papers/scripts/build_docx.py
   python papers/scripts/build_docx.py --supplementary
   python papers/scripts/generate_review_pack.py
   ```

   - Clean build directory first.
   - Use the DOCX commands and output-filename mapping recorded in
     `project_configuration.md` (Phase 9 task 6 tooling) so the freeze
     manifests hash freshly rebuilt DOCX files, never stale Phase 9/10
     outputs.
   - The review pack remains an internal advisor artifact (Phase 9 task 4);
     it is excluded from publication evidence and the submission package.
   - Record page counts and warnings; verify the measured main-manuscript
     page count still satisfies the Section 1.5 hard page-limit rule against
     the verified target-journal limit, and append the page-count row to
     `papers/governance/phase_gate_register.csv`. A violation here is a
     Gate 11 blocker resolved only by supplement migration (Section 8.6).

5. **Run repository engineering gates.**

   ```powershell
   python -m pytest -q
   python -m ruff check .
   python scripts\validate_profile_lock.py --root .
   python scripts\build_docs_html.py
   ```

6. **Finalize Word validation.**
   - Open/update/save/reopen.
   - Recheck OMML, native tables, fields, citations, bibliography, TOC/lists,
     bookmarks, relationships, and visual layout.

7. **Freeze main manuscript scientifically.**
   - Record canonical, LaTeX, PDF, DOCX, claim matrix, citation map, and artifact
     hashes.
   - Mark main scientific content `FROZEN_BEFORE_ABLATION`.
   - No algorithm or primary experiment change is permitted after this point.

8. **Freeze primary evidence and analysis.**
   - Record release ID, analysis bundle hashes, source-use audit, and artifact
     bindings.

9. **Freeze pre-ablation supplementary core.**
   - Hash all non-ablation content.
   - Reserve final ablation insertion points in source only, not visible output.

10. **Verify main-manuscript ablation prohibition.**
    - Scan text, captions, hidden fields, metadata, highlights, cover letter,
      and figures.
    - No ablation result or claim.

11. **Verify final-phase prerequisites.**
    - Algorithm freeze manifest intact.
    - Ablation preregistration complete.
    - Toggle audit complete.
    - Compute/environment available.
    - Staging paths ready and the promotion tool `scripts/promote_evidence.py`
      (built in Phase 2 task 10) verified operational.
    - No historical result leakage.

12. **Create Phase 12 entry certificate.**
    - List every required gate and checksum.
    - State that algorithm development, primary benchmarking, statistical
      validation, manuscript preparation, dual-format production, and
      manuscript finalization are complete.

13. **Create correction-exception protocol.**
    - Define material contradiction thresholds.
    - Permit text-only narrowing/correction in Phase 12.
    - Prohibit algorithm redesign, new primary tuning, or main-text ablation
      results.

### Generated outputs

- finalized pre-ablation main PDF and DOCX;
- finalized pre-ablation supplementary core PDF and DOCX;
- `primary_freeze_manifest.json`;
- `main_manuscript_freeze_manifest.json`;
- `pre_ablation_supplement_freeze_manifest.json`;
- `journal_compliance.md`;
- `final_primary_integrity_audit.md`;
- `phase12_entry_certificate.md`;
- `correction_exception_protocol.md`;
- final pre-ablation build/Word/engineering reports.

### Validation procedures

- complete acceptance checklist;
- clean build and OOXML validation;
- hash comparison with frozen registries;
- journal rule cross-check;
- no-ablation scan;
- Phase 12 prerequisite validation.

### Verification procedures

- P1 signs scientific finalization.
- P3 signs primary statistical validity.
- P5 signs evidence/reproducibility freeze.
- P6 signs editorial finalization (closure of the minor/editorial tickets
  deferred from Gate 10).
- P7 signs PDF.
- P8 signs Word.
- P9 signs integrity/no-ablation.
- P10 signs journal compliance.

### Quality-assurance checkpoints

- zero open material ticket;
- zero build error;
- zero broken Word field;
- zero source drift;
- zero main-text ablation content;
- all Phase 12 prerequisites green.

### Acceptance criteria

- all algorithm development is complete and frozen;
- all primary benchmarking and statistics are complete and validated;
- main manuscript is scientifically and editorially finalized;
- PDF and Word are publication-ready;
- non-ablation supplement core is finalized;
- current journal requirements are met;
- Phase 12 entry certificate is signed;
- no material unresolved issue remains.

### Exit criteria

Phase 11 freezes only when every signatory approves. This is the mandatory entry
gate for final ablation. No ablation objective evaluation may start before the
certificate is complete.

### Risks

| Risk | Impact |
|---|---|
| journal instruction change | compliance rework |
| hidden ablation value in draft | requirement violation |
| unresolved administrative metadata | upload readiness blocked |
| algorithm/profile drift | ablation invalid |
| primary freeze too early | later correction burden |

### Assumptions

- primary manuscript is defensible without ablation;
- current official journal rules can be verified; and
- final ablation infrastructure is ready but unused.

### Mitigation strategies

- repeat official-guidance check;
- automated deep scan including OOXML/metadata;
- isolate administrative gaps;
- revalidate hashes/profile lock;
- keep Phase 11 open until truly final.

### Deliverables

All generated outputs, especially the signed `phase12_entry_certificate.md`.

### Review gate

**Gate 11 — Pre-ablation hard gate:** P1 + P3 + P5 + P6 + P7 + P8 + P9 + P10
must all approve. Any open material issue, missing signature, algorithm drift,
primary-analysis uncertainty, Word defect, or ablation content prevents Phase
12 from starting.

---

## Phase 12 — FINAL IMPLEMENTATION PHASE: frozen-algorithm ablation, supplementary integration, final verification, and publication packaging

### Objective

Execute the complete pre-registered ablation study with the finalized algorithm,
promote validated ablation evidence into `cec_reference_results`, produce the
complete supplementary ablation record, apply any scientifically mandatory
text-only correction to the already finalized main manuscript, and assemble the
entire publication and reproducibility package. This is the final phase of the
project. No later phase exists.

### Expected outcomes

- complete, reproducible final ablation evidence;
- individual, conditional, isolated, incremental, and targeted interaction
  analyses with honest identifiability limits;
- statistical significance, effect size, uncertainty, convergence, runtime,
  and sensitivity evidence (memory evidence only when the optional pre-freeze
  peak-memory harness of Section 6.9 was built; otherwise the memory gap is
  recorded in `evidence_gap_register.md`);
- immutable ablation evidence release under `cec_reference_results`;
- complete supplementary PDF and editable Word document;
- final main PDF and editable Word document with no ablation results;
- complete submission and reproducibility package;
- final integrity and completion report.

### Entry criteria

Every item in `phase12_entry_certificate.md` MUST be green:

- algorithm and parameters frozen;
- primary benchmarks complete;
- primary statistics validated;
- main manuscript finalized in PDF and Word;
- non-ablation supplement core finalized;
- no open critical/major issue;
- ablation preregistration and toggle audit complete;
- strict source/promotion workflow ready;
- compute environment and storage verified;
- no ablation objective evaluation previously executed in the current governed
  workflow.

### Prerequisites

- signed Phase 11 gate;
- `algorithm_freeze_manifest.json`;
- `ablation_preregistration.md`;
- `ablation_toggle_audit.md`;
- frozen code/configuration/evaluator/seed policy;
- selected primary evidence release;
- staging paths and the immutable promotion tool `scripts/promote_evidence.py`
  (Phase 2 task 10);
- supplementary source and Word pipeline;
- correction-exception protocol.

### Required inputs

- finalized algorithm implementation;
- frozen ablation configuration templates;
- CEC suite evaluators and immutable primary release metadata;
- exact seeds, MaxFES, dimensions, functions, and environment;
- statistical methods and output schemas;
- final main and supplementary source snapshots;
- target journal's final package checklist.

### Dependencies

All Phases 0–11. No subsequent phase is permitted.

### Detailed implementation tasks

#### 12.1 Reconfirm freeze and create ablation execution snapshot

1. Recompute and compare:
   - algorithm source/configuration hashes;
   - evaluator hashes;
   - profile lock;
   - seed policy;
   - MaxFES accounting;
   - environment and FP sentinel;
   - main manuscript freeze hashes.
2. Abort if any material hash differs.
3. Create `ablation_execution_manifest.json` with study ID, commit, environment,
   frozen toggles, cells, suites, dimensions, runs, seeds, functions, budgets,
   analysis plan, and expected outputs.
4. Create a clean branch/worktree or immutable execution container.

#### 12.2 Finalize the ablation estimands and interpretation boundaries

The final ablation study MUST distinguish these questions:

1. **Conditional remove-one contribution:** How does disabling one component
   from the full frozen scaffold change performance, conditional on all other
   enabled scaffold components?
2. **Isolated add-one contribution:** How does enabling one component on a
   frozen minimal/base configuration change performance?
3. **Order-conditional incremental contribution:** How does adding each module
   in a pre-specified dependency-respecting cumulative chain change
   performance?
4. **Direct SGSM overlay contribution:** What changes when SGSM is disabled
   while the remaining frozen algorithm is held constant?
5. **Targeted interaction effects:** Do pre-specified dependent component pairs
   show non-additive behavior?
6. **Cost contribution:** What runtime and objective-accounting overhead does
   each configuration impose? Memory overhead is in scope only when the
   optional pre-freeze peak-memory harness (Section 6.9) was built before the
   analysis freeze; otherwise the memory gap remains a documented entry in
   `evidence_gap_register.md`.
7. **Convergence contribution:** At what evaluation stages do differences
   emerge?
8. **Sensitivity:** Are ablation conclusions stable under approved nearby
   configuration values, without modifying algorithm code?

Do not call a conditional or order-dependent delta an independent causal effect.
Do not average across dimensions when signs or magnitudes differ materially.

#### 12.3 Required core scaffold remove-one design

Verify the existing script and execute the approved remove-one matrix. The
cell set is conditional on the Phase 3 frozen-profile toggle audit: baseline
plus one remove-one cell per scaffold mechanism active in the frozen profile.
A mechanism confirmed active MUST be included, or excluded with a
preregistered justification recorded in the ablation plan. Expected cells
currently are:

```text
baseline
no_ace
no_psr
no_bse
no_linkage
no_localsearch
no_arch
no_argp
no_finalpolish
no_deepstall
```

Expected component flags include actual equivalents of:

```text
ace_enabled
psr_enabled
bse_enabled
linkage_blockwise_enabled
local_search_enabled
arch_enabled
argp_enabled
final_polish_enabled
deep_stall_restart_enabled
```

The last three mechanisms are active in the current frozen profile (Appendix
D.7.6) and their remove-one configs already exist under `configs/_ablation/`
(`no_argp.yml`, `no_finalpolish.yml`, `no_deepstall.yml`). They are not in
`run_ablation.py`'s built-in `MECHANISMS` list, so run them from those frozen
configs via `python run.py --config <cell>.yml`, or extend the `MECHANISMS`
list as a preregistered tooling change. `final_polish` interacts with the
SGSM overlay; excluding it here in favor of the Section 12.4 overlay design is
admissible only as a preregistered justification recorded in the ablation
plan.

For this scaffold design, SGSM/interaction graph is expected to be disabled in
every cell. Verify this from generated configs. Every table, caption, and
interpretation MUST state that scope. This study cannot establish SGSM's effect.

Expected core protocol, subject to preregistered verification:

- suite: CEC2017;
- dimensions: 10, 30, 50, 100;
- runs: 25;
- same function scope, seeds, MaxFES, environment, and failure policy across
  cells;
- full frozen implementation; only one approved toggle differs per remove-one
  cell.

#### 12.4 Required direct SGSM design

Run a direct SGSM comparison with all other relevant components held constant.
The design comprises cells equivalent to:

```text
full         (frozen profile with SGSM/interaction graph enabled)
no_adaptive  (exact toggle set defined in the ablation plan before execution)
no_sgsm      (frozen profile with interaction_graph_enabled: false only)
```

These configuration names do not exist in the repository yet, and
`scripts/run_ablation.py` cannot produce an SGSM-on cell: it merges
`interaction_graph_enabled: false` (`_SGSM_OFF`) into every generated cell
config. This design is therefore an explicit tooling task, preregistered in
Phase 5: either hand-author frozen YAML cell configs with the exact toggle
lists (full-with-SGSM / `no_sgsm` / `no_adaptive`), executed via
`python run.py --config <cell>.yml`, or extend `run_ablation.py` with an
SGSM-overlay mode that omits the `_SGSM_OFF` override. The exact toggle
composition of `no_adaptive` MUST be defined in the ablation plan before
execution. Name the suite explicitly in the preregistration, and include at
least one dimension `>= 50`: SGSM activates only at
`interaction_graph_min_dim = 50` in the frozen profile, so a lower-dimension
contrast compares identical algorithms. Verify whether CEC2013 was involved in
development; do not call it a holdout or independent confirmation unless proven.
The direct SGSM comparison MUST report both performance and overhead.

#### 12.5 Required isolated and incremental designs

1. **Isolated add-one panel.**
   - Use a frozen base configuration and one `only_<component>` cell per
     approved component when scientifically meaningful.
   - Components with dependencies that cannot operate in isolation are marked
     not identifiable and excluded with rationale.

2. **Cumulative incremental chain.**
   - Define the order before running, based on code dependencies and scientific
     rationale, not expected performance.
   - Example logical structure, replaced by verified component names:

     ```text
     base_gsk
     +ACE
     +NLPSR
     +BSE
     +ARGP/archive
     +linkage block crossover
     +local search/endgame
     +SGSM/eigenframe overlay
     ```

   - Each cell differs from the previous by exactly one approved module.
   - Report each delta as **order-conditional**.
   - Preserve identical budgets, seeds, and implementation.

3. If the existing runner lacks cumulative mode, generate explicit frozen config
   files through the existing toggle system. Do not modify algorithm logic.

#### 12.6 Required targeted interaction analysis

At minimum evaluate interactions required by the method dependency graph, when
supported by the preregistration and compute budget. Expected candidates are:

- SGSM × linkage/eigenframe use;
- ACE × population reduction;
- archive/pool × local search or rescue.

Use a limited factorial or contrast design sufficient for the stated question.
Do not claim untested interactions are absent. A full 2^k factorial is not
required unless pre-registered and computationally feasible.

Interaction cells that require SGSM enabled are subject to the same tooling
constraint as Section 12.4: `run_ablation.py` merges
`interaction_graph_enabled: false` into every generated cell, so hand-author
frozen YAML configs for the interaction pairs (run via
`python run.py --config <cell>.yml`) or use the extended SGSM-overlay mode,
pre-registered before execution.

#### 12.7 Required dry-run and configuration validation

Re-run and record the authoritative dry-run generation after the signed Gate
11 — the pre-ablation hard gate, evidenced by an all-green
`phase12_entry_certificate.md` (earlier inspection-gated dry runs are
permitted under Section 6.10):

```powershell
python scripts/run_ablation.py --dimension 30 --dry-run
python scripts/run_ablation.py --mode add-one --dry-run
```

Warning: both invocations rewrite the committed `configs/_ablation/*.yml`
files in place. Diff the result, then deliberately commit or restore those
files so the Phase 0 dirty-configuration rule is not tripped; a pre-gate
Section 6.10 inspection run MUST restore them.

For every generated config, verify:

- algorithm/config hash relationship;
- exactly intended toggles;
- frozen non-toggled parameters;
- suite, dimension, function, runs, seeds, MaxFES;
- output path isolation;
- SGSM scope;
- no accidental parameter retuning;
- no evidence overwrite.

Render and manually inspect a configuration-difference matrix. Any unexpected
change blocks execution.

#### 12.8 Execute core ablation runs

Expected core command:

```powershell
python scripts/run_ablation.py --dimension 10,30,50,100 --runs 25 --workers 15
```

Execution rules:

- output to staging only, expected under
  `results/_ablation/<cell>/dt-gsk/<suite>/...`;
- preserve seed `20240620` and exact run count;
- use `--workers 2` or serial when memory constrained;
- resume incomplete cells without changing protocol;
- rerun only failed/corrupt cells using `--only <cell>`;
- never reduce runs, dimensions, functions, or MaxFES;
- never change a parameter after observing outcomes;
- record retries, worker failures, timeouts, and hardware events;
- verify no source/config file changed during execution.

Execute direct SGSM, isolated, cumulative, targeted interaction, overhead,
convergence, and approved sensitivity cells using separate, preregistered
configuration IDs and staging roots.

#### 12.9 Validate every ablation run before analysis

For each cell verify:

- all expected functions × dimensions × runs exist;
- seed schedule matches exactly;
- per-run key uniqueness;
- MaxFES and objective-call counts;
- environment and FP sentinel;
- frozen code/config hashes;
- failure/timeout policy;
- convergence checkpoints;
- wall-time instrumentation (`runtime_seconds` in `per_run.csv`), plus memory
  instrumentation only when the optional pre-freeze peak-memory harness
  (Section 6.9) was built before the analysis freeze — otherwise validate
  runtime only and confirm the memory gap is recorded in
  `evidence_gap_register.md`; do not add instrumentation during Phase 12,
  which would break the frozen code/config hashes;
- no NaN/Inf/schema corruption unless scientifically valid and explicitly
  handled;
- no cross-cell file contamination.

A partial matrix is not analyzed or reported as complete.

#### 12.10 Promote validated raw ablation evidence

1. Create a versioned release path, default:

   ```text
   benchmarks/cec_reference_results/ablation/<ablation_release_id>/
   ```

2. Include per-cell/per-suite raw/per-run outputs, convergence logs, configs,
   environment, seeds, verification, protocol, and checksums. The promoted
   release MUST mirror the staging tree byte-for-byte with the cell-first
   layout preserved — `results/_ablation/<cell>/dt-gsk/<suite>/...` becomes
   `<release_root>/<cell>/dt-gsk/<suite>/...` — so
   `generate_ablation_matrix.py --ablation-root` can read the release
   directly and item 4's byte-equality check is well-defined.
3. Use the scripted ingestion process `scripts/promote_evidence.py`
   (Phase 2 task 10; Section 2.4).
4. Verify promoted bytes equal accepted staging bytes.
5. Write `ablation_release_manifest.json` and supersession policy.
6. Set the promoted release read-only.
7. From this point onward, all ablation analyses MUST read exclusively from the
   promoted path. Staging output is no longer an analytical input.

#### 12.11 Aggregate and analyze from the promoted release

Expected scaffold aggregation commands. `--ablation-root` defaults to the
staging tree (`results/_ablation`), so after promotion the release-rooted
invocation below is mandatory (12.10 item 7 — staging is no longer an
analytical input):

```powershell
python papers/scripts/generate_ablation_matrix.py --ablation-root benchmarks/cec_reference_results/ablation/<ablation_release_id> --suite cec2017 --dimension 10
python papers/scripts/generate_ablation_matrix.py --ablation-root benchmarks/cec_reference_results/ablation/<ablation_release_id> --suite cec2017 --dimension 30
python papers/scripts/generate_ablation_matrix.py --ablation-root benchmarks/cec_reference_results/ablation/<ablation_release_id> --suite cec2017 --dimension 50
python papers/scripts/generate_ablation_matrix.py --ablation-root benchmarks/cec_reference_results/ablation/<ablation_release_id> --suite cec2017 --dimension 100
```

Expected outputs include:

```text
ablation_matrix_rank_summary_cec2017_D10.csv
ablation_matrix_rank_summary_cec2017_D30.csv
ablation_matrix_rank_summary_cec2017_D50.csv
ablation_matrix_rank_summary_cec2017_D100.csv
```

Extend or wrap the aggregator for direct SGSM, isolated, cumulative, targeted
interaction, cost, convergence, and sensitivity analyses without changing raw
evidence.

For each pre-registered family compute, as valid:

- descriptive per-function and per-dimension summaries;
- Friedman ranks when the design supports them;
- paired full-versus-cell tests with declared Holm families;
- raw and adjusted p-values;
- Vargha–Delaney A12 or another approved effect with direction;
- seeded BCa confidence intervals at the correct resampling level;
- best-case counts with explicit definition;
- conditional delta versus full;
- isolated delta versus base;
- order-conditional incremental delta;
- interaction contrasts;
- runtime overhead, plus memory overhead only when the optional pre-freeze
  peak-memory harness was built (otherwise report runtime and objective-call
  overhead only and cite the `evidence_gap_register.md` entry);
- objective-call equality;
- convergence trajectories and uncertainty;
- dimension-specific sign/magnitude changes; and
- sensitivity/robustness of ablation conclusions.

Do not collapse a sign-changing effect into one overall average.

#### 12.12 Interpret ablation with identifiability discipline

Every component discussion MUST state:

- design used: remove-one, add-one, cumulative, direct, or interaction;
- conditioning configuration;
- suite, dimensions, functions, runs, seeds, and budget;
- test/effect/interval;
- performance and cost impact;
- convergence timing;
- negative or inconsistent effects;
- interaction/dependency limitations;
- whether the result supports necessity, isolated utility, order-conditional
  increment, or only association.

Prohibited inferences include:

- claiming SGSM effect from an SGSM-off scaffold matrix;
- claiming independent causality from remove-one alone;
- claiming universal component benefit from one suite/dimension;
- ignoring overhead or adverse effects;
- treating three-run sensitivity as definitive;
- modifying the algorithm because a component performs poorly.

#### 12.13 Generate final ablation tables and figures

Use the validated promoted-release analyses to generate:

- complete design table;
- per-dimension scaffold matrices;
- direct SGSM table;
- isolated add-one table;
- cumulative incremental table;
- targeted interaction table;
- adjusted inference/effect/CI tables;
- runtime/objective-call table, with memory columns only when the optional
  pre-freeze peak-memory harness was built (otherwise the table reports
  runtime and objective calls and cites the recorded memory gap);
- convergence figures;
- component-effect plots with uncertainty;
- sensitivity figures where appropriate;
- raw-result and configuration indexes.

Expected table generator may include:

```powershell
python papers/scripts/generate_latex_tables.py
```

Ablation fragments may follow `ablation_<tag>.tex`. Bind every cell/point to a
promoted evidence source. Generate native Word tables from the same semantic
sources.

#### 12.14 Write the complete supplementary ablation section

The supplementary document MUST include:

1. objectives and preregistered research questions;
2. finalized frozen-algorithm statement;
3. design rationale and configuration matrix;
4. suites, functions, dimensions, runs, seeds, MaxFES, and environment;
5. component toggle definitions;
6. remove-one analysis;
7. direct SGSM analysis;
8. isolated add-one analysis;
9. order-conditional incremental analysis;
10. targeted interactions;
11. statistical significance, effects, and intervals;
12. runtime and objective-call overhead (memory overhead when the optional
    pre-freeze peak-memory harness was built; otherwise the documented
    memory-evidence gap);
13. convergence comparisons;
14. approved sensitivity analysis;
15. negative and inconsistent findings;
16. identifiability and causal-inference limitations;
17. raw and summarized result index;
18. release ID, checksums, commands, and reproduction instructions; and
19. exact links/cross-references to supplementary tables and figures.

All scientific paragraphs follow the evidence rules. No result is invented or
estimated.

#### 12.15 Apply the scientific-correction exception when required

Compare final ablation evidence against every component-related main-text claim
and rationale.

A **material contradiction** includes:

- a component described as beneficial that shows consistent harm or no support
  under the direct relevant design;
- a claimed mechanism boundary contradicted by configuration evidence;
- a cost claim contradicted by measured overhead;
- a limitation that materially understates observed risk.

When triggered:

1. open a Phase 12 correction ticket;
2. narrow or correct the main text, abstract, conclusion, highlights, and cover
   letter as scientifically required;
3. do not insert ablation numbers, tables, figures, or detailed interpretation
   into the main manuscript;
4. do not modify the algorithm, parameters, primary benchmarks, or primary
   analysis to rescue the claim;
5. rebuild and re-review both formats;
6. record the exact reason and diff; and
7. re-freeze the main manuscript.

A neutral pointer to Supplementary Materials may be added if allowed.

#### 12.16 Assemble the final supplementary PDF and Word document

1. Integrate ablation with the frozen non-ablation supplement core.
2. Compile standalone supplementary PDF:

   ```powershell
   python papers/scripts/build_supplementary.py
   ```

3. Generate supplementary DOCX with:
   - native OMML;
   - native Word tables;
   - editable captions;
   - automatic S-numbering and cross-references;
   - updateable citations and bibliography;
   - editable diagrams where applicable.
4. Validate OOXML, fields, citations, values, and visual layout.
5. Verify every main-to-supplement pointer resolves.

#### 12.17 Rebuild final main PDF and Word document

- Rebuild from the re-frozen canonical source.
- Confirm no ablation results appear.
- Confirm any neutral supplement pointer is correct.
- Rerun citation, number, source, field, Word, and cross-format checks.

#### 12.18 Assemble the reproducibility package

Include:

- the final updated `reproducibility_manifest.json` (Section 3.1; appended by
  every phase per Section 3.9);
- selected primary evidence release manifest;
- ablation evidence release manifest;
- raw-result access/index information;
- frozen algorithm/evaluator/config hashes;
- seed formula and schedules;
- environments and FP sentinels;
- all run/analysis/generator/build commands;
- analysis plans and preregistration;
- machine-readable primary and ablation statistics;
- table/figure semantic sources;
- figure scripts and editable diagram sources;
- LaTeX and Word generation/validation code;
- claims, citation, data, artifact, decision, assumption, risk, and review
  records;
- checksums and archive manifest;
- README with one-command or staged reproduction instructions.

#### 12.19 Assemble the final submission package

Include, subject to the verified journal checklist:

- final main PDF;
- final fully editable main DOCX;
- final LaTeX source and required class/style files;
- final supplementary PDF;
- final fully editable supplementary DOCX;
- all journal-ready figure files;
- editable diagram/flowchart sources;
- native-table source data;
- bibliography and Word source store;
- cover letter;
- highlights and graphical abstract only if required;
- declarations and availability statements;
- reproducibility package or repository link manifest;
- response-to-reviewers template;
- package manifest and checksums.

Author/administrative metadata must be verified. Missing human metadata blocks
the upload-ready label but does not justify invention.

#### 12.20 Final clean-room rebuild

1. Copy only packaged source into a clean location.
2. Build main and supplement PDF.
3. Generate main and supplement DOCX.
4. Update Word fields and reopen.
5. Verify all paths are package-relative.
6. Verify nothing referenced is missing and nothing unnecessary is included.
7. Recompute checksums.

#### 12.21 Final adversarial and compliance review

Repeat targeted R1–R6 review on:

- ablation design and interpretation;
- supplementary completeness;
- correction-exception changes;
- final PDF/Word quality;
- package reproducibility;
- journal compliance;
- administrative truthfulness.

All categories must score at least 4/5; no critical/major issue may remain.

#### 12.22 Final completion and freeze

- Record submission commit/SHA and evidence release IDs.
- Make final manifests immutable.
- Record PI/scientific sign-off and available author administrative sign-offs.
- Create `final_integrity_audit.md` (Section 3.1) consolidating the complete
  acceptance evidence and residual caveats, extending the Phase 11
  `final_primary_integrity_audit.md` with the ablation and packaging scope.
- Create `completion_report.md` with verified achievements, omitted claims,
  residual caveats, and any administrative blocker.
- Declare the project complete only if every final acceptance criterion passes.
- No additional implementation phase follows.

### Generated outputs

- complete staged and promoted ablation data;
- `ablation_execution_manifest.json`;
- `ablation_release_manifest.json`;
- raw/per-run/config/environment/seed/checkpoint records under the immutable
  ablation release;
- complete machine-readable ablation statistics;
- ablation tables and figures;
- complete supplementary source, PDF, and DOCX;
- final main source, PDF, and DOCX;
- updated claims/citation/artifact/cross-format records;
- reproducibility package;
- submission package;
- final review and compliance reports;
- `final_integrity_audit.md`;
- `completion_report.md`.

### Validation procedures

- configuration-difference validation;
- run completeness and seed/MaxFES checks;
- code/config/evaluator hash checks;
- FP/environment consistency;
- staging-to-release byte equality;
- strict promoted-source analysis audit;
- statistical schema, family, effect, interval, and determinism checks;
- table/figure value binding;
- supplement cross-reference and standalone build;
- main no-ablation scan;
- Word OMML/native table/field/citation checks;
- clean-room package rebuild;
- checksum and manifest validation.

### Verification procedures

- P2 verifies toggle semantics and component interpretation.
- P3 verifies final ablation estimands, tests, effects, intervals, interactions,
  and causal wording.
- P4 verifies run protocol and evidence release.
- P5 verifies promotion, commands, hashes, reproducibility, and clean-room build.
- P6 verifies supplementary writing and main correction scope.
- P7 verifies final PDFs/figures.
- P8 verifies final Word documents and editable sources.
- P9 verifies evidence/citation/integrity and no main ablation.
- P10 verifies journal and package compliance.
- R1–R6 independently review the final package.

### Quality-assurance checkpoints

- no pre-freeze algorithm change;
- no partial ablation matrix;
- no mixed seed/run/budget design;
- no analysis from staging after promotion;
- no SGSM misattribution;
- no independent-causality claim from an inadequate design;
- all negative effects reported;
- all overhead/convergence/sensitivity evidence included;
- main manuscript contains no ablation result;
- supplementary Word is fully editable;
- final package rebuilds cleanly.

### Acceptance criteria

- ablation starts only after signed Phase 11 gate;
- all runs use the frozen finalized implementation;
- core remove-one, direct SGSM, isolated/incremental, targeted interaction,
  significance/effect/CI, overhead, convergence, and sensitivity requirements
  are completed or any scientifically impossible item is explicitly blocked and
  claims narrowed;
- every ablation value derives from promoted immutable evidence;
- complete raw and summarized evidence is available;
- supplementary materials are comprehensive, transparent, reproducible, and
  independently compilable;
- main manuscript remains ablation-free except a neutral pointer;
- any material contradiction is corrected without algorithm redesign;
- final PDF and Word documents pass all native/editability checks;
- reproducibility and submission packages are complete;
- no critical/major review issue remains;
- all final manifests and checksums agree.

### Exit criteria

Set Phase 12 to `FROZEN` and the project to `COMPLETE` only when every acceptance
criterion is proven. If scientific work passes but author/admin metadata is
missing, set project status `SCIENTIFICALLY_COMPLETE_ADMIN_BLOCKED` and identify
exact missing fields. Do not invent them.

### Risks

| Risk | Impact |
|---|---|
| ablation reveals adverse component behavior | main claim correction required |
| toggle changes multiple mechanisms | invalid attribution |
| incomplete cells or compute failure | incomplete supplement |
| interaction confounding | overclaimed component effect |
| staging used after promotion | evidence violation |
| ablation modifies algorithm | invalid final study |
| Word supplementary flattening | editability failure |
| late journal-rule change | packaging rework |

### Assumptions

- frozen toggles can express required cells without code changes;
- compute resources can complete the preregistered design;
- promotion into `cec_reference_results` is permitted through a scripted new
  release;
- the target journal allows supplementary materials; and
- the main paper remains scientifically coherent if component claims are
  narrowed.

### Mitigation strategies

- validate config diffs before runs;
- use resume/retry without protocol changes;
- report conditional/order-dependent effects honestly;
- fail closed on incomplete matrices;
- promote and reanalyze from immutable evidence;
- apply text-only correction exception;
- regenerate Word from semantic sources;
- recheck official journal guidance immediately before packaging.

### Deliverables

Every generated output in this phase, including the final main and supplementary
PDF/DOCX files, ablation release, reproducibility package, submission package,
final integrity audit, completion report, submission SHA, and sign-off record.

### Review gate

**Gate 12 — Final project gate:** P1–P10 and R1–R6 approve all applicable
criteria. No critical/major issue, evidence-boundary violation, algorithm drift,
main-text ablation result, invalid component attribution, Word editability
failure, or package rebuild failure may remain. This gate ends the project.

---

# 14. Adversarial review rubrics

## 14.1 Scoring rule

Score each applicable item from 1 to 5:

- **5:** exemplary; no material weakness;
- **4:** strong; minor non-blocking improvements;
- **3:** adequate but reviewer concern remains;
- **2:** major weakness;
- **1:** invalid, absent, or misleading.

Any score ≤3 creates a ticket. A score ≤2 is a blocking major unless the item is
formally not applicable with evidence.

Rubric-to-role mapping follows the Section 11.2 role definitions: R1 scores
14.2–14.4; R2 (methodological/statistical) scores 14.5 and the statistical
items of 14.11; R3 (reproducibility) scores 14.6; R4 (editorial/presentation)
scores 14.8–14.9; R5 (Word submission) scores 14.10; R6 (skeptical domain)
scores the mechanism-distinction, same-family scope, benchmark-overfitting,
cost, and failure-case items of 14.2 and 14.4 together with 14.11; P9
(research-integrity auditor) scores 14.7 in support of R1 and R6. Phase 10
review outputs are named after the Section 11.2 roles.

## 14.2 R1 scientific-contribution rubric

- Is the problem specific and important within the approved literature scope?
- Is the contribution boundary explicit?
- Is SGSM distinguished accurately from differential grouping, eigenvector
  crossover, covariance adaptation, and direct search?
- Are inherited, modified, combined, and original elements separated?
- Are novelty statements bounded to the closed corpus?
- Does the same-family panel support the exact claims made?
- Does the paper avoid field-wide superiority claims?
- Are negative and null results visible?
- Does the supplementary ablation test components at the correct level without
  causal overstatement?

## 14.3 R1 method-completeness rubric

- Can a competent reader reimplement the core?
- Are all symbols, distributions, parameters, states, and update orders defined?
- Do equations, pseudocode, code, and Word OMML agree?
- Are evaluation budgets and local-search calls fully counted?
- Are numerical safeguards and fallback behaviors specified?
- Are time and memory complexity derived from actual code?
- Is the final frozen implementation identical across primary and ablation
  experiments?

## 14.4 R1 experimental-validity rubric

- Are suite definitions, dimensions, functions, and run counts verified?
- Are seeds and pairing available?
- Are comparator budgets, parameter tuning, boundary handling, and failure rules
  fair?
- Are imported and reproduced results distinguished?
- Is eGSK provenance handled correctly?
- Is CEC2013's role pre-specified rather than outcome-driven?
- Are convergence cases selected by a defensible rule?
- Are results generated exclusively from the approved evidence root?

## 14.5 R2 statistical-validity rubric

- Is the estimand clear?
- Are observation and experimental units distinguished?
- Is pseudoreplication avoided?
- Are Friedman/Nemenyi assumptions and task counts valid?
- Is Wilcoxon pairing valid and zero handling reported?
- Are multiplicity families pre-defined and Holm applied correctly?
- Are effect measures compatible with design?
- Are BCa intervals resampled at the correct level?
- Are p-values, effects, intervals, and direction consistent?
- Are robustness reversals disclosed?

## 14.6 R3 reproducibility rubric

- Can every headline number be regenerated from an immutable evidence release?
- Are source paths, checksums, commit, evaluator, configuration, seeds, MaxFES,
  and environment recorded?
- Does strict publication mode fail rather than fall back?
- Are raw and derived releases immutable and versioned?
- Do table/figure generators use named commands and sources?
- Does the clean package rebuild without repository-only paths?
- Do software tests, lint, profile lock, and documentation build pass?

## 14.7 P9 evidence and citation rubric

- Does every scientific paragraph have appropriate support?
- Does every citation support the nearby claim?
- Are source locators available?
- Are empirical claims bound to approved evidence?
- Are unsupported claims omitted or narrowed?
- Are all bibliography entries and citation fields consistent across formats?
- Is decorative citation avoided even if fewer than 61 sources are ultimately
  used?
- Are conclusions and cover-letter claims within the claims ceiling?

## 14.8 R4 writing and editorial rubric

- Is the narrative coherent and evidence-led?
- Are paragraphs focused and transitions logical?
- Is terminology stable?
- Are generic and promotional phrases absent?
- Are losses and limitations clear?
- Are sections within the verified journal budget?
- Are tables and captions self-contained?
- Are figures readable at final size and accessible?
- Is the main manuscript free of ablation results?
- Is the supplement complete but not a dumping ground?

## 14.9 Natural-prose integrity rubric

This is a prose-quality audit, not an attempt to evade authorship detection.
Check:

- varied but controlled sentence rhythm;
- no repeated hollow transitions;
- no compulsive tricolons;
- no more than one `First/Second/Third` ladder per section;
- concrete paper-specific detail;
- local, earned hedging;
- irregular but coherent paragraph lengths;
- no three consecutive generic sentences;
- no banned stock vocabulary except literal technical uses;
- style-only revisions do not change facts, numbers, citations, labels, or
  claim scope.

## 14.10 R5 Word deliverable rubric

- Are all equations native OMML and editable?
- Are all tables native Word tables?
- Are captions field-numbered and editable?
- Are cross-references functional after field update?
- Are section, figure, table, algorithm, and equation numbers automatic?
- Are TOC, list of figures, and list of tables updateable?
- Are citations and bibliography live/updateable?
- Are styles used consistently?
- Are diagrams vector/editable with native sources included?
- Are tracked changes, comments, hidden text, and placeholders absent?
- Does content match LaTeX/PDF exactly?

## 14.11 Final-ablation rubric

- Did ablation begin only after final algorithm, primary benchmark, statistics,
  and main manuscript freezes?
- Was the frozen implementation unchanged?
- Are all audited scaffold cells complete at all four dimensions and n=25
  (baseline plus one remove-one cell per mechanism active in the frozen
  profile, per Section 12.3 and the Phase 3 toggle audit — currently ten
  expected)?
- Is SGSM-off scope explicit for the scaffold matrix?
- Is the direct SGSM/adaptive overlay design separate and controlled?
- Are marginal, incremental, and interaction claims distinguished?
- Are effects reported per dimension without hiding sign reversals?
- Are statistical tests, effects, intervals, runtime, convergence, and
  sensitivity reported (memory when the optional pre-freeze peak-memory
  harness was built, otherwise the recorded `evidence_gap_register.md`
  entry)?
- Are negative/null component results retained?
- Is every ablation result supplementary only and generated from promoted
  evidence-root data?

---

# 15. Automated validation, acceptance gates, and definition of done

## 15.0 Current gate implementations (verified 2026-07-20)

The abstract validators specified in 15.1–15.8 are now realized by concrete,
committed scripts. This subsection records the current mapping and their
verified state. The normative requirements in 15.1–15.9 remain authoritative;
the row counts below are a 2026-07-20 status snapshot, not invariants, and MUST
be re-verified by running the scripts rather than quoted from here.

| Gate (this section) | Concrete script / artifact | Verified state (2026-07-20) |
|---|---|---|
| Build hygiene | `papers/scripts/validate_build_hygiene.py` | 0 unresolved refs / control chars / retired content |
| Cross-format parity (15.5) | `papers/scripts/validate_cross_format_parity.py` | 0 FAIL across 577 rows (PDF <-> DOCX <-> JSON) |
| Document consistency (15.5) | `papers/scripts/validate_document_consistency.py` | exit 2 = only author-pending fields remain (suggested reviewer names) |
| Provenance claims (15.7) | `papers/scripts/validate_provenance_claims.py` | prose matches the freeze manifests |
| Runtime provenance (`tab:runtime`) | `papers/scripts/validate_runtime_provenance.py` | gated on the RT-001 re-timing refresh (Section 0 status note) |
| Exhibit binding (15.4) | `papers/scripts/validate_evidence_bindings.py` | green |
| Word / OOXML (15.6.2) | `papers/scripts/validate_docx.py` | green |
| Citation-set (15.1) | `papers/governance/citation_usage_map.csv` | deterministic; 0 cite-key failures across 117 rows |
| Engineering / profile lock (15.8) | `scripts/validate_profile_lock.py` (+ `pytest`, `ruff`) | green |
| Environment attestation | recorded per ledger ticket M-030 | green |

`validate_document_consistency.py` exiting 2 is the expected terminal state: the
only residue is author-supplied (suggested reviewer names), which MUST NOT be
auto-generated (Section 15.9 and the Section 0 status note).

## 15.1 Citation-set validation

The validation system shall:

1. parse `papers/references.bib`;
2. compare it with `papers/governance/reference_inventory.csv` (the canonical
   governance root, Sections 3 and 12.4);
3. scan LaTeX, canonical source, and Word citation fields;
4. verify every used key is admissible;
5. verify no undefined citation;
6. verify every rendered bibliography entry has a legitimate role;
7. verify main and supplement bibliographies are consistent;
8. reject decorative all-key forcing.

## 15.2 Claim-coverage validation

- Every substantive sentence or paragraph shall map to one or more claim IDs.
- Every accepted claim shall have direct or appropriately bounded support.
- Every abstract, conclusion, highlight, and cover-letter claim shall exist in
  the claims matrix.
- Every blocked/omitted claim shall be absent from final outputs.

## 15.3 Number-binding validation

For each number in main, supplement, PDF, Word, captions, highlights, and cover
letter:

```text
assert display_value == round(source-derived full_precision_value,
                              declared_rounding_rule)
```

The validator shall also check units, directions, ties, significance marks,
effect values, intervals, and ranks.

## 15.4 Exhibit-binding validation

For every table/figure:

- source evidence release exists and is immutable;
- source files and generator exist;
- command is recorded;
- checksum matches;
- caption claim IDs exist;
- artifact is referenced in the correct document;
- no unexplained output is orphaned;
- no ablation artifact appears in main.

## 15.5 Cross-document consistency validation

Compare main and supplement across LaTeX, PDF, and Word for:

- title, abstract, section names, terminology, acronyms;
- suite names, dimensions, functions, runs, seeds, MaxFES;
- algorithm names and mechanism definitions;
- table/figure/equation numbering;
- citations and bibliography;
- conclusions and limitations;
- evidence release IDs and commit hashes.

## 15.6 Build validation

### 15.6.1 LaTeX/PDF

```powershell
python papers/scripts/build_pdf.py
python papers/scripts/build_supplementary.py
```

Inspect logs for:

```text
undefined
Citation ... undefined
Reference ... undefined
Overfull
missing figure
missing curve
```

Resolve every scientifically or visually material issue.

Additionally, read the measured main-manuscript page count from the build log
("Output written on ... pages") and assert it satisfies the Section 1.5 hard
page-limit rule against the verified target-journal limit. A violation fails
this gate; the only permitted resolution is supplement migration per
Section 8.6.

### 15.6.2 Word/OOXML

Validate:

- OMML presence and registry equality;
- native tables;
- required fields;
- field update;
- styles;
- relationships;
- editable captions/diagrams;
- no images substituted for equations/tables;
- no broken cross-references;
- no tracked changes/comments/placeholders.

## 15.7 Evidence-release validation

- Every reportable empirical source resides under the selected evidence
  release root recorded in `project_configuration.md` (an immutable release
  under `benchmarks/cec_reference_results/`).
- No publication generator reads `results/`.
- Release manifests and checksums match.
- Previous releases remain unchanged.
- Promotion source and destination hashes match.
- Primary and ablation release IDs are explicit.

## 15.8 Engineering validation

At final submission commit:

```powershell
python -m pytest -q
python -m ruff check .
python scripts\validate_profile_lock.py --root .
python scripts\build_docs_html.py
```

Any unexplained failure blocks submission.

## 15.9 Definition of done checklist

The project is done only when all boxes have evidence.

**External gate nomenclature mapping (CR-0003).** Externally specified
Gates 1–14 map onto the framework's existing anchors as follows; the framework
anchors remain authoritative and no separate gate machinery is created:

| External gate | Framework anchor |
|---|---|
| 1 Reference availability | Gate 1 (Phase 1 closed literature-corpus audit) |
| 2 Dataset inventory | Phase 2 tasks 1–3 and 9 (`data_ledger.csv`, `experiment_matrix.csv`) |
| 3 Dataset integrity | Gate 2 (Phase 2 review gate) |
| 4 Reference immutability (initial checksums) | Phase 2 `evidence_release_manifest.json` (Sections 2.3 and 6.6) |
| 5 Statistical validation | Gate 6 (Phase 6) plus the Section 7.14 statistical output bundle |
| 6 Table validation | Sections 15.3 and 15.4 plus Gate 7 (Phase 7 review gate) |
| 7 Convergence validation (every function, seven curves) | Phase 7 validation procedures plus the Section 15.9.4 seven-curve family-overlay checkbox (CR-0001; Section 6.7) |
| 8 Figure QA | Phase 7 validation procedures and Phase 10 R4 review plus the Section 8.4 requirements |
| 9 Traceability | Section 2.6 claim-level traceability plus Sections 15.3 and 15.4 |
| 10 Scientific review | Phase 10 tasks 1 and 6 (R1, R6) plus Gate 10 |
| 11 Editorial review | Phase 10 task 4 (R4) plus Gates 10–11 |
| 12 Final immutability audit | Phase 12 task 12.22 `final_integrity_audit.md` plus Section 15.7 |
| 13 Reproducibility build | Section 15.6 plus Phase 12 task 12.20 final clean-room rebuild |
| 14 Submission readiness | Phase 12 tasks 12.18–12.19 packaging plus Gate 12 and this Section 15.9 definition of done |

### 15.9.1 Literature and claims

- [ ] Closed corpus identity audit complete.
- [ ] Every used citation is verified and semantically correct.
- [ ] No fictional or external scientific reference.
- [ ] Every scientific paragraph is appropriately supported.
- [ ] Claims matrix covers all manuscript and submission claims.
- [ ] Evidence gaps are omitted, narrowed, or explicitly managed.
- [ ] Novelty wording is bounded to the reviewed corpus.

### 15.9.2 Method and implementation

- [ ] Inherited/modified/original decomposition complete.
- [ ] Equations, pseudocode, code, and configuration agree.
- [ ] All objective evaluations count toward MaxFES.
- [ ] Complexity and overhead are verified.
- [ ] Final algorithm freeze manifest is complete.
- [ ] No post-freeze implementation drift.

### 15.9.3 Primary data and statistics

- [ ] CEC2017, CEC2011, and CEC2013 protocols verified.
- [ ] Seven-algorithm panel provenance complete.
- [ ] Seeds, run counts, functions, dimensions, and sentinels verified.
- [ ] Comparator fairness matrix complete.
- [ ] Statistical plan frozen before final analysis.
- [ ] Tests, corrections, effects, and intervals valid.
- [ ] Convergence selection pre-specified.
- [ ] Every primary result resides in an immutable evidence release.
- [ ] No publication fallback to `results/`.

### 15.9.4 Main manuscript

- [ ] All sections satisfy Part IX.
- [ ] Every number/citation/exhibit is bound.
- [ ] Losses and limitations are candid.
- [ ] No ablation result, table, figure, or component-effect claim appears.
- [ ] Journal scope and page/word requirements are verified.
- [ ] Measured main-manuscript page count satisfies the Section 1.5 hard
  page-limit rule; all non-essential material (extended tables, additional
  figures, detailed derivations, comprehensive experimental results,
  supporting analyses) resides in the supplement per Section 8.6.
- [ ] Every convergence panel is a seven-curve family overlay per Section 6.7
  (one curve per GSK-family algorithm, uniform aggregation, fixed style map),
  or carries a disclosed absence note (CR-0001).
- [ ] Optional analysis figures (if any) are justified in the frozen exhibit
  plan, evidence-bound, and QA-passed (CR-0003).
- [ ] `presentation_conventions.md` exists and the manuscript passed the
  Phase 10 exemplar-parity editorial check against `mohamed2020gaining` and
  `alfadli2025atmals` (CR-0002).
- [ ] Three-exemplar comparative review complete; the manuscript passes
  exemplar parity against GSK, eGSK, and ATMALS-GSK (CR-0003).
- [ ] Main PDF builds cleanly.
- [ ] Main Word document is fully editable and updateable.

### 15.9.5 Supplement and final ablation

- [ ] Non-ablation supplement is complete and independent.
- [ ] Ablation began only after all required freezes.
- [ ] Audited-cell CEC2017 scaffold design complete at D10/D30/D50/D100,
  n=25 (baseline plus one remove-one cell per mechanism active in the frozen
  profile, per Section 12.3 and the Phase 3 toggle audit; currently ten cells
  expected, with any exclusion preregistered in the ablation plan).
- [ ] Direct SGSM/adaptive overlay analysis complete.
- [ ] Statistical, effect, interval, runtime, convergence, and sensitivity
  analyses complete (memory analyses when the optional pre-freeze peak-memory
  harness was built; otherwise the gap recorded in
  `evidence_gap_register.md`).
- [ ] Negative/null effects retained.
- [ ] Raw and derived ablation evidence promoted immutably.
- [ ] All ablation content is supplementary only.
- [ ] Supplement PDF and Word build cleanly and independently.

### 15.9.6 Word and cross-format quality

- [ ] Every equation is native OMML.
- [ ] Every table is a native Word table.
- [ ] Captions and numbering use live fields.
- [ ] Cross-references remain functional.
- [ ] TOC, lists, citations, and bibliography update.
- [ ] Diagrams have editable native sources.
- [ ] Cross-format parity passes.
- [ ] No tracked changes, comments, hidden text, or placeholders.

### 15.9.7 Reproducibility and packaging

- [ ] Evidence, algorithm, evaluator, environment, seeds, commands, and hashes
  are recorded.
- [ ] Every exhibit regenerates from packaged materials.
- [ ] Clean-location package rebuild succeeds.
- [ ] Reproducibility level recorded per artifact class
  (analytical/visual/byte-for-byte, Section 9.4) (CR-0003).
- [ ] Repository gates are green.
- [ ] Package contains every referenced file and no unexplained artifact.
- [ ] Cover letter and highlights stay within accepted claims.
- [ ] Submission SHA and PI sign-off are recorded.

---

# APPENDIX A — Expected admissible citation keys

Only verified keys in the runtime intersection may be cited. Expected set:

```text
GSK family (6):
  mohamed2020gaining  mohamed2020agsk  apgsk2021  fdbagsk2023
  alfadli2025atmals   jawad2024egsk

GSK variants/hybrids (13):
  hpe_agsk2025  epd_gsk2024  pogsk2023  chalabi2023mogsk
  ma2023mgskdpmo  apgsk_imode2024  nabahat2024hybrid
  nomer2021gskrl  zhong2021gskhho  navaneetha2022gskde
  liang2024gskwoa  jalali2021opposition  mohamed2021novel

DE/ES lineage and structure-aware operators (8):
  storn1997differential  zhang2009jade  tanabe2013shade
  tanabe2014improving  mohamed2017lshadespacma  hansen2001cmaes
  omidvar2014dg  guo2015eig

CEC benchmarks and competition context (9):
  awad2016problem  das2011cec2011  liang2013cec2013  li2013lsgo
  yue2020cec2020   awad2017ensemble  brest2017single
  molina2018shadeils  latorre2013mos

Other metaheuristics (8):
  chen2020cbo  kaveh2021pgo  arini2022gjojos  hu2022qcsca
  khalfi2023csm  tang2024fowfo  zhou2021iade  yao1999evolutionary

Local search and landscape (4):
  nelder1965simplex  gao2012implementing  jones1995fitness
  kolda2003directsearch

Adaptive operator selection and bandits (2):
  auer2002finite  fialho2010adaptive

Statistics (8):
  demsar2006statistical  friedman1937use  wilcoxon1945individual
  holm1979simple  benjamini1995controlling  vargha2000critique
  efron1993introduction  david_order_statistics

Foundations and surveys (3):
  wolpert1997nfl  del2019bio  hussain2019metaheuristic
```

Expected count: `6 + 13 + 8 + 9 + 8 + 4 + 2 + 8 + 3 = 61`.

The corpus was reopened from 57 to 61 by **CR-0020 (ruling R8, 2026-07-28)** for
exactly four admissions, all forced by the five-suite scope: `li2013lsgo` (the
CEC2013-LSGO suite definition — `liang2013cec2013` is the *wrong*, bound-constrained
CEC2013 suite), `yue2020cec2020` (the CEC2020 protocol source, already in
`references.bib` but previously outside the admitted set), and `molina2018shadeils`
and `latorre2013mos`, required because the mandatory large-scale limitation sentence
names published SHADE-ILS and MOS results. DECC-G was **not** admitted. All four sit
in group B.4; see the group-assignment rationale in Appendix B.4.

---

# APPENDIX B — Citation usage map

## B.1 Foundation and GSK family

- `mohamed2020gaining` — GSK origin, inherited mechanics, thematic comparison.
- `mohamed2020agsk` — AGSK method and family baseline.
- `apgsk2021` — APGSK/adaptive-parameter family baseline.
- `fdbagsk2023` — FDB-AGSK and fitness-distance-balance family baseline.
- `alfadli2025atmals` — ATMALS-GSK and memory/local-search family baseline.
- `jawad2024egsk` — eGSK family baseline and verified mechanism scope.

## B.2 GSK variants and hybrids — related-work breadth only

- `hpe_agsk2025`;
- `epd_gsk2024`;
- `pogsk2023`;
- `chalabi2023mogsk`;
- `ma2023mgskdpmo`;
- `apgsk_imode2024`;
- `nabahat2024hybrid`;
- `nomer2021gskrl`;
- `zhong2021gskhho`;
- `navaneetha2022gskde`;
- `liang2024gskwoa`;
- `jalali2021opposition`;
- `mohamed2021novel`.

Use each only where its verified mechanism is actually discussed. Do not insert
one sentence per source solely to force bibliography usage.

## B.3 DE/ES lineage and structure-aware operators

- `storn1997differential` — DE origin.
- `zhang2009jade` — adaptive DE and external-archive lineage.
- `tanabe2013shade`, `tanabe2014improving` — SHADE/L-SHADE and population-size
  reduction lineage.
- `mohamed2017lshadespacma` — hybrid competitive context.
- `hansen2001cmaes` — covariance-adaptation conceptual comparison.
- `omidvar2014dg` — differential grouping and decomposition comparison/future
  work.
- `guo2015eig` — eigenvector crossover comparison.

## B.4 CEC benchmarks and competition context

Suite definitions — one key per suite the manuscript reports, each the sole
admissible anchor for its own suite's functions, dimensions and protocol:

- `awad2016problem` — verified CEC2017 definition role.
- `das2011cec2011` — verified CEC2011 definition role.
- `liang2013cec2013` — verified CEC2013 definition role (the **bound-constrained**
  real-parameter suite).
- `li2013lsgo` — verified CEC2013-**LSGO** definition role: 15 functions, D = 1000
  with F13/F14 at 905, 25 runs, MaxFE = 3e6, milestones 1.2e5/6.0e5/3.0e6, ranked
  on the median. Never interchange with `liang2013cec2013`; they are different
  benchmarks that share a year.
- `yue2020cec2020` — verified CEC2020 definition role: 10 functions, 30 runs, the
  per-dimension MaxFES schedule, the 1e-8 floor, and the F6/F7 restriction to
  D = 10/15/20 (38 protocol cells, not 40).

Competition context — cited only for what the source's own tables print:

- `awad2017ensemble`, `brest2017single` — competition context only where the
  source supports the stated claim.
- `molina2018shadeils` — published **SHADE-ILS** results on CEC2013-LSGO
  (Tables IV–VII). Note it used **51 runs** where the suite specifies 25; the
  deviation must be disclosed wherever its numbers appear.
- `latorre2013mos` — published **MOS** results on CEC2013-LSGO (Table IV), produced
  under the suite's own 25-run / 3e6-FE protocol.

**Why SHADE-ILS and MOS belong in B.4 (CR-0020 / ruling R8).** Neither fits an
existing group. B.3 (DE/ES lineage) would suit SHADE-ILS's DE core but not MOS,
whose final configuration is a GA + Solis-and-Wets + MTS-LS1-Reduced hybrid with no
DE member at all; splitting the pair across two groups would also fracture the
single limitation sentence that cites them together. B.5 (other metaheuristics) is
scoped to *taxonomy and positioning only*, which is the wrong licence: what the
limitation sentence needs is the published numbers, not a positioning mention. B.4
already carries exactly this role for `awad2017ensemble` and `brest2017single` —
CEC competition-track papers cited for their own reported results — and it is the
group the four new keys' suite anchor (`li2013lsgo`) sits in. Both keys therefore
take the existing B.4 role string "competition context only where the source
supports the stated claim", and neither licenses any comparison against the GSK
family or against this project's own banks.

## B.5 Other metaheuristics

- `chen2020cbo`, `kaveh2021pgo`, `arini2022gjojos`, `hu2022qcsca`,
  `khalfi2023csm`, `tang2024fowfo`, `zhou2021iade` — taxonomy/positioning only.
- `yao1999evolutionary` — Cauchy-mutation basis when relevant to BSE.

## B.6 Local search and landscape

- `nelder1965simplex`, `gao2012implementing` — Nelder–Mead.
- `kolda2003directsearch` — compass/direct-search basis.
- `jones1995fitness` — fitness-distance basis only where verified.

## B.7 Adaptive control

- `auer2002finite`, `fialho2010adaptive` — bandit/adaptive operator-selection
  grounding, not proof that the exact ACE mechanism is inherited.

## B.8 Statistics

- `friedman1937use`, `demsar2006statistical` — Friedman/rank/post-hoc practice.
- `wilcoxon1945individual` — signed-rank test.
- `holm1979simple` — family-wise multiplicity control.
- `benjamini1995controlling` — exploratory FDR only when used.
- `vargha2000critique` — A12.
- `efron1993introduction` — BCa bootstrap.
- `david_order_statistics` — order-statistics argument only if actually used.

## B.9 Foundations and surveys

- `wolpert1997nfl` — bounded NFL premise, never proof of expected superiority.
- `del2019bio`, `hussain2019metaheuristic` — field framing and taxonomy only as
  supported.

---

# APPENDIX C — Prohibited actions and formulations

## C.1 Prohibited actions

The agent MUST NOT:

- cite scientific material outside `reference_papers/`;
- complete references, DOIs, authors, venues, or years from memory;
- cite a source that has not passed identity/readability audit;
- add decorative citations to satisfy a paragraph or bibliography quota;
- use `\\nocite{*}` to force bibliography entries;
- use `results/`, manuscript tables, figures, or old prose as publication data;
- allow an empirical loader to fall back outside `cec_reference_results`;
- edit an immutable evidence release;
- promote candidate evidence without validation, manifest, and checksum proof;
- fabricate, estimate, interpolate, or visually read a numerical result;
- select favorable functions, runs, dimensions, or curves after viewing results;
- change tests, endpoints, correction families, or effect definitions after
  outcomes without labeling the change exploratory;
- claim paired inference without valid pairing;
- treat repeated runs as independent benchmark functions;
- use rounded values to determine ranks, ties, or significance;
- exclude local-search/polish evaluations from MaxFES;
- claim general superiority from a same-family panel;
- claim universal novelty from a closed corpus;
- call CEC2013 a holdout or independent confirmation without documented
  development independence;
- execute ablation before the Phase 11 gate;
- include ablation results in the main manuscript, abstract, conclusion,
  highlights, or cover letter;
- alter the frozen algorithm during final ablation;
- infer SGSM benefit from an SGSM-off scaffold design;
- infer independent causality from remove-one or order-dependent increments;
- hide adverse primary or ablation results;
- insert equations as images in Word;
- insert tables as images in Word;
- flatten captions, numbering, cross-references, citations, or bibliography when
  native updateable Word fields are required;
- convert the PDF into Word as the manuscript-generation method;
- invent author, affiliation, ORCID, funding, conflict, ethics, reviewer, or
  availability metadata;
- distribute proprietary font files; or
- write to evade automated authorship detectors.

## C.2 Formulations requiring direct evidence or replacement

Avoid these unless the exact wording is supported and scoped:

```text
state-of-the-art
best-performing
universally superior
consistently outperforms
significantly better
robust
highly efficient
negligible overhead
for free
large-scale
high-dimensional
first-ever
novel in the literature
proves
guarantees
solves the exploration-exploitation dilemma
applicable to all real-world problems
independent confirmation
holdout
causal contribution
```

Use exact suite, dimension, panel, test, effect, interval, cost, and limitation
instead.

## C.3 Stock prose to remove when empty

```text
Moreover
Furthermore
Additionally
It is worth noting that
Importantly
Notably
Overall
In conclusion
a myriad of
plays a crucial role
paves the way
sheds light on
cutting-edge
paradigm shift
seamless
holistic
```

Literal or technically necessary use is permitted only when the term carries
real meaning.

---

# APPENDIX D — Command and artifact reference

All commands are expected forms and MUST be reconciled with the current
runbook, repository paths, strict evidence rule, and operating system.

## D.1 Preflight and engineering

```powershell
git status --porcelain
git rev-parse HEAD
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
python scripts\validate_profile_lock.py --root .
python scripts\build_docs_html.py
python run.py --root . --help
gsk-list --optimizers --benchmarks --references benchmarks/cec_reference_results
python -m gsk_family.cli.validate --references benchmarks/cec_reference_results
```

## D.2 Conditional independent reproduction

```powershell
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2017 --function 1:30 --dimension 10,30,50,100 --runs 51 --parallel --workers 15 --convergence-graphs --overwrite
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2011 --function 1:22 --dimension native --runs 25 --parallel --workers 15 --convergence-graphs --overwrite
python run.py --root . --optimizer gsk,agsk,apgsk,fdb-agsk,atmals-gsk,egsk,dt-gsk --suite cec2013 --function 1:28 --dimension 10,30,50 --runs 51 --parallel --workers 15 --convergence-graphs --overwrite
python -m gsk_family.cli.validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
python scripts\run_all_cec2017.py
```

The repository may provide analogous suite launchers. Audit them against the
explicit campaigns before use. These outputs remain staging until promoted
into a new immutable release. Use `--seed-policy reference` only when the
verified runner supports it and a reproduction is intentionally aligned to the
canonical seed schedule.

## D.3 Primary statistics

```powershell
python -m gsk_family.cli.stats --suite CEC2017 --dims 10,30,50,100 --out papers/analysis/<release_id>/cec2017/
python -m gsk_family.cli.stats --suite CEC2011 --out papers/analysis/<release_id>/cec2011/
python -m gsk_family.cli.stats --suite CEC2013 --dims 10,30,50 --out papers/analysis/<release_id>/cec2013/
```

The source guard MUST prove that no fallback path is opened. Derived results
go to the controlled analysis area (Section 7.13), never the
`results/_run_all/_analysis/` default.

## D.4 Primary table and figure generation

```powershell
python papers/scripts/generate_latex_tables.py
python papers/scripts/generate_t16_bca.py
python papers/scripts/generate_full_convergence.py
python papers/scripts/generate_cec2011_convergence.py
python papers/scripts/generate_cec2013_convergence.py --dimension 30
python papers/scripts/generate_nemenyi_cd.py
python papers/scripts/generate_rank_charts.py
python papers/scripts/generate_trace_figures.py
python papers/scripts/generate_nlpsr_trajectory.py
python papers/scripts/generate_adaptive_params_panel.py
```

(The former `generate_parametric_tables.py` / `generate_flowchart.py` /
`generate_taxonomy_figure.py` steps are retired — 2026-07-15 status note,
Section 7.)

## D.5 Final-phase ablation

```powershell
python scripts/run_ablation.py --dimension 30 --dry-run
python scripts/run_ablation.py --mode add-one --dry-run
python scripts/run_ablation.py --dimension 10,30,50,100 --runs 25 --workers 15
python papers/scripts/generate_ablation_matrix.py --ablation-root benchmarks/cec_reference_results/ablation/<ablation_release_id> --suite cec2017 --dimension 10
python papers/scripts/generate_ablation_matrix.py --ablation-root benchmarks/cec_reference_results/ablation/<ablation_release_id> --suite cec2017 --dimension 30
python papers/scripts/generate_ablation_matrix.py --ablation-root benchmarks/cec_reference_results/ablation/<ablation_release_id> --suite cec2017 --dimension 50
python papers/scripts/generate_ablation_matrix.py --ablation-root benchmarks/cec_reference_results/ablation/<ablation_release_id> --suite cec2017 --dimension 100
```

`--ablation-root` defaults to the staging tree (`results/_ablation`); after
promotion (Section 12.10) the release-rooted invocation shown above is
mandatory, because staging is no longer an analytical input.

Additional direct SGSM, cumulative, interaction, cost, convergence, and
sensitivity commands MUST be generated from the frozen preregistration and
recorded in the final manifest.

## D.6 Builds

```powershell
python papers/scripts/build_pdf.py
python papers/scripts/build_supplementary.py
python papers/scripts/generate_review_pack.py
```

The Word pipeline MUST expose deterministic equivalents of the following
expected entry points. If these scripts do not yet exist with the required
interface and behavior, Phase 9 MUST implement or extend them — auditing the
existing pandoc-based `papers/scripts/build_docx.py` first (it takes no CLI
arguments today, so `--supplementary` is unsupported, and it writes
`papers/DT-GSK.docx`, not `papers/main.docx` — record the actual
filename mapping in `project_configuration.md`; Sections 4.1 and 9.5),
then extending or wrapping it and adding the missing `validate_docx.py`,
`validate_cross_format_parity.py`, and `validate_evidence_bindings.py` —
document the actual commands in `project_configuration.md`, and preserve the
required behavior:

```powershell
python papers/scripts/build_docx.py
python papers/scripts/build_docx.py --supplementary
python papers/scripts/validate_docx.py papers/main.docx
python papers/scripts/validate_docx.py papers/supplementary.docx
python papers/scripts/validate_cross_format_parity.py
python papers/scripts/validate_evidence_bindings.py
```

The updated project expects a review artifact equivalent to
`papers/DT-GSK-CEC2017-review.pdf`. Verify the configured filename. Any
associated `..._missing.log` must contain no unexplained missing-curve or
missing-input line.

## D.7 Exact project-specific implementation and output audit targets

The updated construction brief names the following exact implementation
symbols, files, options, and output contracts. They are mandatory audit targets.
They do not override the strict-source, final-ablation, or current-repository
verification rules.

### D.7.1 Source-code and analysis entry points

Verify the existence, actual signatures, and publication-mode behaviour of:

```text
src/gsk_family/analysis/result_loader.py::load_algorithm
src/gsk_family/analysis/family_report.py
family_report.generate_family_report
src/gsk_family/analysis/statistics.py
src/gsk_family/runners/seed_policy.py
figures.nemenyi_critical_difference
wilcoxon_paired
holm_correction
benjamini_hochberg
statistics.vargha_delaney
statistics.bootstrap_bca_ci
```

The historical analysis defaults named by the source include:

```text
--reference-root benchmarks/cec_reference_results
--results-root results/_run_all
--proposed dt-gsk
--alpha 0.05
--no-figures
--out <scratch-directory>
```

For publication, `--results-root` fallback MUST be disabled by the strict source
guard. `--out` is the required mechanism for writing publication analyses to
the controlled analysis area `papers/analysis/<release_id>/<suite>/`
(Section 7.13); a scratch `--out` run may additionally be used for
deterministic comparison and must then be deleted or clearly marked
non-evidence afterward.

### D.7.2 Exact provenance fields and expected counts

Audit these fields and values from actual files:

```text
run_config.json: runs, base_seed: 20240620, seed_policy: unified, max_nfes_override
seed_schedule.csv: one unique row per planned run/function/dimension
information in environment.json: fp_regime.sentinel
```

`MaxFES` is not a `run_config.json` key: the budget is suite/dimension-derived
and the only budget-related key is `max_nfes_override`. Per-run MaxFES
accounting is verified from the `nfes` column of `per_run.csv`.

Expected arithmetic audit targets include:

```text
CEC2013 per optimizer: 51 × 28 × 3 = 4284 run/function/dimension records
CEC2017 per optimizer: 51 × 29 × 4 = 5916 run/function/dimension records
```

The seed is expected to be a pure function of `(base_seed, dim, func, run)`.
Verify the implementation in `src/gsk_family/runners/seed_policy.py`.

The updated source also reports an expected CEC2011 layout of 16
native-dimension summary CSVs plus `<opt>_cec2011.csv`; verify the actual
problem/dimension schema rather than forcing the count when repository evidence
differs.

The runner's expected path rule is
`<output_root>/<optimizer>/<suite>/`. Therefore `output_root` must be the tree
that contains suite folders, not a suite folder itself; otherwise a doubled
path such as `cec2017/<opt>/cec2017/...` can be created. Reject and correct this
trap before evidence admission.

### D.7.3 Exact source assertions that require verification, not assumption

Treat the following as explicit audit targets:

- a historical D30 second-place case behind eGSK;
- low-dimensional regressions or function classes where structure exploitation
  misfires;
- SGSM activation only at `D >= 50` in the relevant frozen profile;
- the CEC2017 sentinel prefix `8bda40d8...`;
- `egsk` canonical provenance from MATLAB `fmincon` versus local SciPy/SLSQP;
- the bibliography-key census — how many of the 61 admitted keys are actually
  cited in the build, and that zero undefined keys remain (do not assume the
  census equals the corpus: `citation_usage_map.csv` currently records citation
  sites for a strict subset); and
- rendered PNG and `*_log_*.txt` files absent from the immutable result release
  because they are regenerable.

No manuscript statement may use these assertions until the corresponding
canonical/code check passes.

### D.7.4 Exact statistical-output contracts

Verify or deliberately migrate these expected names and schemas:

```text
<category>_statistical_report.txt
<category>_friedman_ranks.csv
<category>_friedman_ranks.tex
<category>_wilcoxon_summary.tex
D<dim>: N=<n_funcs> Friedman p=<p> best=<alg> (<rank>)
headline_bca.csv:
  gap_id,dimension,point,ci_lo,ci_hi,n_boot,alpha,seed
```

The full authoritative schema SHOULD additionally include suite, estimand,
unit/resolution, canonical evidence IDs, software commit, and resampling unit.
The `rng` argument for BCa computation is required and must be seeded with the
frozen analysis seed.

### D.7.5 Exact table-generation contracts

Audit mappings in code, including expected examples:

```text
results/paper_tables/T1.csv -> papers/tables/T01.tex
...
T16.csv -> T16.tex
generate_t16_bca.py -> T16_bca.tex
gen_ablation_table() -> papers/tables/ablation_<tag>.tex
example final tag: ablation_cec2017_D30.tex
```

Expected role anchors from the source include T06 for a CEC2011 Wilcoxon view,
T11–T13 for CEC2013 head-to-head views, T14 for a CEC2013 Wilcoxon summary,
T15 for a Wilcoxon summary, and T16 for Friedman ranks. Verify actual generator
code and retire stale mappings rather than hand-authoring a table.

### D.7.6 Exact ablation options and legacy script variables

Audit support for the following, each on its owning script — absence of a
flag on a different script is expected, not a defect:

```text
scripts/run_ablation.py:                     --serial
scripts/run_ablation.py:                     --workers 2
scripts/run_ablation.py:                     --only baseline,no_linkage,no_bse
scripts/run_ablation.py:                     --seed <frozen-seed>
scripts/run_ablation.py:                     --mode add-one
scripts/run_ablation.py:                     --dry-run / --output-root <root>
scripts/run_ablation.py:                     MECHANISMS
papers/scripts/generate_ablation_matrix.py:  --full-cell baseline
papers/scripts/generate_ablation_matrix.py:  --ablation-root <root>
run.py / gsk_family.cli.run:                 --seed-policy reference
run.py / gsk_family.cli.run:                 --max-evaluations <frozen-MaxFES>
generated cell names:                        only_<component> / no_<component>
```

`run_ablation.py` accepts neither `--seed-policy` nor `--max-evaluations`: it
hardcodes `seed_policy: unified` into every generated cell config and never
sets `max_evaluations` (the budget derives from the suite protocol).

The legacy source identifies optional/commented mechanisms named `argp`,
`finalpolish`, and `deepstall`. All three are active in the current frozen
profile (`argp_enabled`, `final_polish_enabled`, and
`deep_stall_restart_enabled` are `True`), and their remove-one configs already
exist under `configs/_ablation/` (`no_argp.yml`, `no_finalpolish.yml`,
`no_deepstall.yml`). A mechanism the Phase 3 frozen-profile toggle audit
confirms active MUST be included in the final Phase-12 design, or excluded
with a preregistered justification recorded in the ablation plan (Section
12.3; `final_polish` may justifiably move to the Section 12.4 SGSM-overlay
design). If a mechanism is inactive, record that fact and do not imply it was
evaluated.

Expected legacy aggregate path:

```text
results/ablation/ablation_matrix_rank_summary_cec2017_D<dim>.csv
```

This path is a derived/staging artifact; final analysis must read the promoted
immutable ablation release.

### D.7.7 Exact review and governance compatibility names

Where existing project tooling expects these legacy names, generate them as
views or aliases of the authoritative governance artifacts rather than creating
conflicting sources of truth:

```text
outline.md
claims.md
decisions.md
_bibkeys.txt
review_R1.md
review_R2.md
revision_log.md
table_to_csv_map.md
curve_selection.csv
PHASE_0_readiness.md
```

The status token `pending-phase-2` from an older ablation workflow is
superseded. Final ablation rows use a status such as `planned-phase-12` until
Gate 11 authorizes execution.

## D.8 Legacy companion-file inventory

Audit but do not require these subordinate files:

```text
build_prompt_phases/PHASE_0_audit.md
build_prompt_phases/PHASE_1_scope.md
build_prompt_phases/PHASE_2_data_stats.md
build_prompt_phases/PHASE_3_tables_figures.md
build_prompt_phases/PHASE_4_drafting.md
build_prompt_phases/PHASE_5_supplementary.md
build_prompt_phases/PHASE_6_humanization.md
build_prompt_phases/PHASE_7_review.md
build_prompt_phases/PHASE_8_compliance.md
build_prompt_phases/PHASE_9_submission.md
build_prompt_phases/ADDENDUM_R2_cec2013_and_ablation.md
```

Every operative requirement from these files that remains valid must already be
represented in this master. A reader must not need a companion to execute the
project.

## D.9 Exact legacy schemas, path patterns, and failure messages

The following strings and compact schemas appeared in the updated construction
brief — per Section 3.2, that brief IS this master file,
`papers/PAPER_BUILD_PROMPT.md`, unless a separate brief path is recorded in
`project_configuration.md` at Phase 0. Preserve them as compatibility audit
targets. The richer schemas in Section 3 remain authoritative; these aliases
MUST NOT create a second source of truth.

```text
asset-map legacy view:
  path | class(keep/rewrite/regenerate) | generator | source | current?

data-ledger legacy view:
  optimizer,suite,dimension,n_runs,seed_policy,source_path,commit_sha,status

revision-ticket legacy view:
  id | severity | section | objection | planned fix | evidence needed

exhibit-binding legacy view:
  table/figure id -> source CSV -> producing command
```

Audit these exact path/glob patterns when they exist:

```text
results/_run_all/**
results/_ablation/**
benchmarks/cec_suite_python/**
benchmarks/cec_reference_results/cec2013/
results/_run_all/<optimizer>/<suite>/...
results/_ablation/<cell>/dt-gsk/<suite>/...
results/_ablation/<cell>/dt-gsk/cec2017/...
benchmarks/cec_reference_results/<suite>/<optimizer>/curves/
benchmarks/cec_reference_results/<suite>/<optimizer>/gen_logs/
papers/**.tex
sections/*.tex
figures/ranks/
figures/{convergence,diagrams,flowchart,ranks,taxonomy,traces}/
```

Compatibility patterns for generated cells and LaTeX bindings include:

```text
no_<m>
only_<m>
T01.tex ... T16.tex
results/paper_tables/T1.csv -> T01.tex
T16.csv -> T16.tex
results/ablation/ablation_matrix_rank_summary*.csv
\input{...}
\ref{...}
\wmark / \lmark / \emark
```

Treat the historical CLI messages below as hard configuration/input failures,
not permission to fall back or continue silently:

```text
no reproduced '<proposed>' summaries found
reference directory not found
```

The historical phase range `PHASE_0 ... PHASE_9` and pattern
`build_prompt_phases/PHASE_<n>_*.md` are superseded by the self-contained Phase
0–12 model in this master. They remain searchable compatibility identifiers
only.

---

# APPENDIX E — Validation algorithms

## E.1 Strict empirical source guard

```python
for opened_path in empirical_file_open_log:
    resolved = opened_path.resolve()
    assert resolved.is_relative_to(selected_cec_reference_release.resolve())
    assert not resolved.is_relative_to(results_root.resolve())
```

Use an equivalent safe implementation on Python versions without
`Path.is_relative_to`.

## E.2 Citation validation

```python
bib_keys = parse_bibtex("papers/references.bib")
admissible = load_verified_keys("reference_inventory.csv")
latex_keys = scan_latex_citations()
word_keys = scan_word_citation_fields()
used = latex_keys | word_keys

assert used <= bib_keys
assert used <= admissible
assert no_undefined_citations()
assert semantic_usage_map_complete(used)
assert not uses_nocite_star()
```

## E.3 Claim coverage

```python
for paragraph in scientific_paragraphs:
    assert paragraph.claim_ids
    assert every_claim_has_accepted_support(paragraph.claim_ids)
    assert paragraph_has_required_evidence_anchor(paragraph)
```

## E.4 Number binding

```python
for displayed_number in all_outputs:
    source = binding_registry[displayed_number.binding_id]
    full_precision = recompute(source)
    expected = apply_declared_rounding(full_precision)
    assert displayed_number.value == expected
```

Exclude page numbers, years in verified citations, labels, and other
non-result numerals through an explicit allowlist.

## E.5 Exhibit binding

```python
for artifact in artifact_registry:
    assert artifact.generator_exists
    assert all_inputs_exist(artifact)
    assert checksums_match(artifact.inputs)
    assert artifact.output_checksum == sha256(artifact.path)
    assert label_resolves(artifact.label)
    assert caption_scope_matches_source(artifact)
    assert artifact.document_destination_is_correct
```

## E.6 OMML validation

```python
for equation in equation_registry:
    node = find_omml_node(equation.word_id)
    assert node is not None
    assert node.tag in {"m:oMath", "m:oMathPara"}
    assert semantic_math_equal(node, equation.canonical_math)
    assert not equation_is_represented_by_image(equation.word_id)
```

## E.7 Native Word table validation

```python
for table in table_registry:
    node = find_word_table(table.word_id)
    assert node.tag == "w:tbl"
    assert extract_cells(node) == table.authoritative_display_values
    assert not table_is_image(table.word_id)
```

## E.8 Word field validation

```python
required = {
    "TOC", "SEQ Figure", "SEQ Table", "SEQ Equation",
    "REF", "CITATION", "BIBLIOGRAPHY"
}
assert required <= detected_field_types()
assert all_bookmarks_resolve()
assert update_fields_enabled()
assert word_open_save_open_has_no_repair()
```

Adjust required fields only when the verified journal explicitly does not need
a list or field type.

## E.9 Cross-format validation

```python
for logical_artifact in canonical_registry:
    assert normalize(extract_from_latex(logical_artifact)) == \
           normalize(extract_from_docx(logical_artifact))
```

Numbers, equations, labels, captions, and citation keys require exact semantic
comparison; line wrapping and layout may differ.

## E.10 Ablation phase-order validation

```python
assert phase12_entry_certificate.is_green
assert gate11.is_signed
assert algorithm_hash == frozen_algorithm_hash
assert primary_analysis_hash == frozen_primary_analysis_hash
assert main_manuscript_hash == pre_ablation_freeze_hash
assert ablation_start_timestamp > gate11_signature_timestamp
```

## E.11 Main-manuscript ablation prohibition scan

Scan canonical, LaTeX, PDF text extraction, DOCX XML, hidden text, captions,
figures, highlights, and cover letter for:

- ablation cell names;
- ablation table/figure labels;
- ablation p-values/effects/ranks;
- component-contribution conclusions.

Allow only the approved neutral supplementary pointer.

---

# APPENDIX F — Reviewer-response template

For each reviewer point:

```text
Reviewer / ticket ID:
Quoted concern:
Severity:
Affected claim(s):
Affected section/artifact:
Evidence reviewed:
Action taken:
Exact change:
Reanalysis or rebuild performed:
Verification result:
Reason if declined:
Status:
```

Keep responses factual, courteous, and evidence-led. Never claim a change that
is not present in both final formats.

---

# APPENDIX G — Final package manifest

The final package manifest MUST include at least:

```text
package_path,artifact_type,required_by_journal,source_of_truth,
source_hash,output_hash,evidence_release_id,build_command,
validation_report,editable,status,notes
```

Mandatory artifact groups:

1. main PDF, DOCX, LaTeX/canonical source;
2. supplementary PDF, DOCX, source;
3. figure finals and editable sources;
4. native-table semantic sources;
5. bibliography, Word source store, citation map;
6. primary and ablation evidence manifests;
7. statistical outputs and analysis plan;
8. reproducibility manifests and commands;
9. Word/OOXML and cross-format validators/reports;
10. governance, review, risk, and completion records;
11. cover letter, declarations, highlights when required;
12. checksums and clean-build README.

---

# APPENDIX H — Revision-integration and conflict-resolution ledger

This master was produced by reviewing the updated construction brief and the
prior evidence-locked master. The following source ranges and requirement
families are explicitly integrated:

| Updated-source range | Requirement family | Destination in this master | Resolution |
|---|---|---|---|
| opening comment and title | self-contained authoritative use | Sections 0, 12–13 | retained and strengthened |
| operating contract | evidence-first, no overclaim, reproducibility, resumability | Sections 0, 2, all phase gates | retained; autonomy expanded |
| personas and quality bar | multidisciplinary roles and adversarial review | Section 11, Section 14 | expanded for Word/OOXML and integrity |
| C1 citation rules | locked corpus, semantic citations | Sections 2–3, Appendices A–B/E | corrected to reject decorative all-key forcing |
| C2 data rules | reference panel and repository evidence | Sections 2, 4, 6; Phases 2/6/12 | strengthened to strict `cec_reference_results` only |
| C3 page budget | journal-aware length | Sections 1 and 8; Phases 4/11 | retained as provisional; current rules must be verified |
| C4 main/supplement | content split | Sections 1 and 8; Phases 8/12 | modified: ablation is supplement-only and final-phase-only |
| C5–C7 | theme, prose, honesty | Sections 5, 8, 10, 14 | retained; detector-evasion language removed |
| original GSK/theme analysis | narrative and method positioning | Sections 5, 8, Appendix B | retained with evidence-bound claims |
| asset inventory | exact paths, tables, scripts, figures | Section 4; Phase 2 | retained and converted to audit targets |
| benchmark inventory | panel layout, runs, dims, seed, FP | Sections 4 and 6; Phase 2 | retained; factual values must be verified |
| Phase 0 details | preflight, panel audit, ledger, citation snapshot | Phase 0 and Phase 2 | split into governance and evidence audits |
| Phase 1 details | contributions, thesis, outline, journal, claims | Phase 4 | retained and strengthened |
| Phase 2 primary statistics | commands, tests, effect/CI, source bundle | Phases 5–6 | retained; fallback prohibited |
| Phase 2 ablation | early ablation pipeline | Phase 12 only | relocated to final phase per latest requirement |
| Phase 3 tables/figures | exact generators and exhibit QA | Phase 7 | retained; ablation generation disabled until Phase 12 |
| Phase 4 drafting | evidence-first section order | Phase 8 | retained; main ablation subsection removed |
| Phase 5 supplement | full evidence and reproducibility | Phases 8 and 12 | split into pre-ablation core and final ablation integration |
| Phase 6 prose pass | natural expert writing | Section 10, Phase 8/10 | retained as integrity-preserving editing |
| Phase 7 review | R1/R2 and revision tickets | Phase 10, Section 14 | expanded to six reviewer lenses |
| Phase 8 build | PDF/build/repo gates | Phases 9 and 11 | expanded with native Word requirements |
| Phase 9 package | cover letter, metadata, source package | Phase 12 | moved into final phase so no work follows ablation |
| per-section specs | abstract through supplement | Section 8 | retained; ablation excluded from main |
| citation usage map | 61 expected roles | Appendices A–B | retained with runtime-admissibility guard |
| quality rubrics | scientific/statistical/reproducibility/editorial | Section 14 | expanded |
| acceptance gates | completion criteria | Section 15 | expanded for Word and final-phase ablation |
| new execution-model requirement | self-contained phase fields | Section 12 and every Phase 0–12 | fully implemented |
| new empirical-source requirement | all empirical outputs from `cec_reference_results` | Sections 2/6, Phases 2/6/12 | implemented through strict guard and promotion |
| new Word requirements | OMML, native tables, fields, references, updateability | Section 9, Phases 7/9/11/12, Appendix E | fully implemented |
| new final-ablation requirement | final phase, frozen algorithm, supplement only | Sections 1/6, Phases 11–12 | fully implemented |
| final deliverables | PDF, DOCX, figures, editable sources, reproducibility | Section 1, Phase 12, Appendix G | fully implemented |

A machine-readable line-by-line review matrix MUST accompany this master and
map every nonblank source line to a destination, a deliberate supersession, a
duplicate, an example/comment classification, or a structural/non-operative
classification. The required files and schemas are defined in Section 3.2 and
are initialized in Phase 0. No line may remain unmapped or partially mapped.

---

# APPENDIX I — First action when this framework is executed

Begin with Phase 0. The first work product MUST contain:

- detected repository root, branch, commit, and dirty state;
- verified locations for literature, evidence, evaluator, source, manuscript,
  script, table, figure, Word, and journal assets;
- protected read-only paths;
- instruction-precedence conflicts and resolutions;
- toolchain and engineering-preflight results;
- immediate evidence, Word, journal, and administrative risks;
- initialized governance registers; and
- exact next artifacts for Phase 1.

Do not draft manuscript prose, run primary analyses, render final exhibits, or
execute any ablation in the first work product.

<!-- END OF AUTHORITATIVE MASTER FRAMEWORK -->
