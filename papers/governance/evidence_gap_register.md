# Evidence gap register

Phase 1 task 8 seed (2026-07-10). Master framework Section 3.6 schema; anchor commit
`262fc16c91fbe5608a1a0b0c5df3cbcd009edc21`. Dispositions use the allowed vocabulary:
**omit / narrow / hypothesis / additional analysis / additional experiment / blocked**.

Register discipline (Section 3.6): usually omit or narrow; disclose a gap in prose only
when it changes interpretation. Do not clutter the manuscript with repeated
"evidence unavailable" sentences. Later phases append; they do not silently rewrite
seeded entries (append a dated resolution note instead).

Sources of this seed: `reference_inventory.csv`, all 57 cards in `evidence_cards/`
(unsupported-uses sections), master Sections 4.4, 6.9, 7.12, 8.5, and Appendix C.

---

## EG-001 — CEC2017 suite-definition citation (RESOLVED CR-0005, 2026-07-10)

- **Desired claim:** The CEC2017 single-objective bound-constrained suite (30 functions,
  unimodal/multimodal/hybrid/composition categories, search range, shift/rotation data,
  51 runs, MaxFES = 10,000·D, error-value recording, complexity protocol) as defined by
  Awad et al. (2016), cited as `awad2016problem`.
- **Why it matters:** This key anchors the entire CEC2017 experimental section (Appendix
  B.4 assigns it the "verified CEC2017 definition role"); CEC2017 is the primary suite.
- **Closed-corpus sources checked:** `reference_papers/awad2016problem.pdf` (identity
  audit), `awad2017ensemble`, `brest2017single`, `liang2013cec2013`, GSK-family cards.
- **Empirical artifacts checked:** n/a (literature gap).
- **Why support is insufficient:** The local PDF under this key is the WRONG DOCUMENT —
  the CEC2017 *constrained* competition report by Wu/Mallipeddi/Suganthan
  (`reference_inventory.csv`: `major_mismatch`, admissible = no). The cited NTU report is
  not in the corpus and may not be reconstructed from memory or the web.
- **Disposition:** **RESOLVED 2026-07-10 (CR-0005).** The correct Awad et al. (2016) NTU
  bound-constrained report was supplied and content-verified (34 pp., F1–F30,
  unimodal/multimodal/hybrid/composition, search range [-100,100], MaxFES = 10000·D, no
  constraint g/h functions; sha256 `b69f52f0…`). `awad2016problem` is now **ADMISSIBLE** and
  carries the CEC2017 suite-definition role; `awad2017ensemble` (Sect. III.A/III.D) and
  `brest2017single` (Sects. IV-A/IV-B) revert from interim substitute to corroborating
  participant descriptions. See `evidence_cards/awad2016problem.md` and CR-0005.
- **Affected sections/deliverables:** Methods/benchmark-protocol section; every
  `claims_evidence_matrix.csv` row that would use `awad2016problem`; references.bib fix
  is a scientific-artifact change (change-request pipeline, not Phase 1).
- **Responsible phase:** Phase 1 flagged; resolution before Phase 4 prose; re-inventory
  on supply (see `evidence_cards/awad2016problem.md` Section 6 resolution path).

## EG-002 — Official CEC competition rankings / winner placements

- **Desired claim:** Statements of the form "LSHADE-cnEpSin won CEC2017", "jSO placed
  second at CEC2017", "SHADE placed N-th at CEC2013 (official)", or any organizer-certified
  ranking of competition entrants.
- **Why it matters:** Competition pedigree is standard positioning language for the
  comparative-context narrative around the DE/GSK families.
- **Closed-corpus sources checked:** `awad2017ensemble`, `brest2017single`,
  `mohamed2017lshadespacma`, `tanabe2013shade`, `tanabe2014improving`, `apgsk2021`,
  `das2011cec2011`, `liang2013cec2013`.
- **Empirical artifacts checked:** n/a (literature gap).
- **Why support is insufficient:** No document in the corpus contains an official CEC2017
  (or CEC2011/CEC2013) results table; organizer announcements are outside the corpus.
  Supported EXCEPTIONS with locators: L-SHADE "winner of the 2014 competition" and SHADE
  3rd in 2013 (authors' framing, `mohamed2017lshadespacma`); LSHADE-EpSin/UMOEAsII joint
  CEC2016 winners (authors' claim, `awad2017ensemble`); AGSK CEC2020 runner-up
  (`apgsk2021`, p. 65936); APGSK-IMODE described as a GSK-family CEC-2021 winner only as
  worded in `apgsk_imode2024`.
- **Disposition:** **narrow** — attribute placements only as the cited authors' own
  claims, with locators; otherwise use "winner-class / competition-grade" phrasing
  without specific ranks.
- **Affected sections/deliverables:** Introduction/related work; comparability_audit.md.
- **Responsible phase:** Phases 4/8 (prose); Phase 10 review enforcement.

## EG-003 — BCa bootstrap mechanics

- **Desired claim:** Technical description of the BCa interval (z0 bias correction,
  acceleration constant, second-order accuracy, recommended B for intervals) attributed
  to `efron1993introduction`.
- **Why it matters:** The statistical suite reports BCa bootstrap confidence intervals;
  the methods section normally explains the estimator it uses.
- **Closed-corpus sources checked:** `efron1993introduction` (local file is a 60-page
  excerpt: front matter + early chapters through ~p. 43; Ch. 14 absent).
- **Empirical artifacts checked:** n/a (literature gap).
- **Why support is insufficient:** The BCa chapter is not in the local excerpt; only a
  table-of-contents-level attribution is verifiable.
- **Disposition:** **narrow** — cite BCa as "the BCa method of Efron & Tibshirani (1993,
  Ch. 14)" (attribution only) and keep any mechanics wording out of the manuscript, or
  supply a fuller copy and re-inventory (which would close this gap). General bootstrap
  resampling methodology IS supported by the excerpt.
- **Affected sections/deliverables:** statistical_analysis_plan.md wording; methods
  subsection on effect sizes/intervals.
- **Responsible phase:** Phase 5 (SAP freeze) / Phase 8 prose.

## EG-004 — Measured peak-memory cost (KNOWN GAP; master Sections 6.9, 7.12, RQ7)

- **Desired claim:** "DT-GSK's peak memory overhead is X MB (measured) vs the family
  baselines" — measured memory cost as part of the RQ7 cost analysis.
- **Why it matters:** RQ7 covers runtime cost and overhead; memory is a natural reviewer
  question for a memory/archive-bearing algorithm family.
- **Closed-corpus sources checked:** `alfadli2025atmals` (qualitative overhead admission
  only, no memory measurements); no other corpus source measures memory.
- **Empirical artifacts checked:** `scripts/` contains no tracemalloc/peak-RSS harness
  (checked 2026-07-10: no sweep/memory/genlog tooling present); admissible runtime
  evidence is `per_run.csv` `runtime_seconds` only; no validated memory cost record in
  `benchmarks/cec_reference_results`.
- **Why support is insufficient:** Master Section 6.9 admits peak memory ONLY from an
  optional pre-freeze measurement harness promoted into a validated immutable cost
  record; none exists.
- **Disposition:** **additional experiment** (build the optional tracemalloc/peak-RSS
  harness before the analysis freeze and promote per Section 2.4) — otherwise **narrow**:
  RQ7 and Sections 5.7/6.9/7.12 report runtime and overhead only, memory is covered by
  the analytic derivation in `complexity_analysis.md`, and this entry is cited as the
  documented gap.
- **Affected sections/deliverables:** RQ7 answer, complexity_analysis.md,
  statistical_analysis_plan.md Section 7.12 block, cost tables/captions.
- **Responsible phase:** Phase 2 (tooling window, pre-freeze) / Phase 5 (SAP) / Phase 8.

## EG-005 — GenLog per-generation diagnostic release (KNOWN GAP; master Section 8.5)

- **Desired claim:** SGSM/trace diagnostic figures and the adaptive-parameters panel
  (`generate_trace_figures.py`, `generate_adaptive_params_panel.py`) showing
  per-generation internal dynamics of DT-GSK.
- **Why it matters:** These exhibits visualize mechanism behavior (SGSM traces, adaptive
  parameter trajectories) that supports the design-rationale narrative.
- **Closed-corpus sources checked:** n/a (empirical gap).
- **Empirical artifacts checked:** 0 files matching `GenLog_*` anywhere in
  `benchmarks/cec_reference_results` (the release `gen_logs/` directories contain only
  `CheckpointErrors_*.csv`) and 0 in `results/` staging (verified 2026-07-10; raw-log
  thinning removed historical per-generation logs).
- **Why support is insufficient:** The generators consume per-generation
  `GenLog_<opt>_F<f>_D<d>_Run<r>.csv` inputs; no validated diagnostic release exists,
  and `results/` staging (even if repopulated) is inadmissible without promotion.
- **Disposition:** **additional experiment** — regenerate the GenLog bundle with frozen
  code (`run.py --gen-logs`) and promote via `scripts/promote_evidence.py` into a
  versioned release subtree (Phase 2 task or Phase 7 prerequisite) — otherwise **omit**:
  mark the SGSM/trace diagnostic figures unavailable and cite this entry.
- **Affected sections/deliverables:** exhibit_plan.csv, Phase 7 figure set, supplement.
- **Responsible phase:** Phase 2 / Phase 7 prerequisite.
- **Phase 7 resolution note (2026-07-11, appended):** the **omit** branch is
  exercised. No promoted GenLog diagnostic release exists at exhibit-production
  time, so `generate_trace_figures.py` and `generate_adaptive_params_panel.py`
  were NOT run (diagnostic-release-gated per exhibit_plan.csv P7).
  `fig:trace-sgsm` (F-TRACE) and `fig:adaptive-params` (F-ADAPT) are
  **unavailable** and must not be referenced by the supplement; the committed
  legacy PDFs under `papers/figures/traces/` (ace_probability_F14_D10.pdf,
  accept_diversity_F14_D10.pdf, adaptive_params_all_D10.pdf) are orphan
  derivatives of vanished staging data and remain excluded from the exhibit
  set. This entry is the citation for both absences.

## EG-006 — Parametric-sweep validated release for T21/T22 (KNOWN GAP; master Section 4.4)

- **Desired claim:** Parameter-sensitivity tables T21/T22 (parametric study, n = 3
  sensitivity evidence) in the supplement.
- **Why it matters:** Sensitivity evidence pre-empts reviewer questions on parameter
  robustness; it is explicitly scoped as NOT ablation and NOT definitive performance
  evidence.
- **Closed-corpus sources checked:** n/a (empirical gap).
- **Empirical artifacts checked:** `results/dt-gsk/sweeps/` is ABSENT from the current
  checkout (verified 2026-07-10); no sweep-runner tooling exists in `scripts/`; no
  `parametric/` subtree exists under `benchmarks/cec_reference_results/` (root lists
  only README.md, cec2011, cec2013, cec2013lsgo, cec2017, cec2020).
- **Why support is insufficient:** Section 2.1-E admits staging only after controlled
  promotion; there is no validated parametric release, no staged sweep data, and no
  recorded sweep-runner command/configuration yet.
- **Disposition:** **additional experiment** — locate the original sweep artifacts or
  record the sweep-runner command/configuration, regenerate, and promote into
  `benchmarks/cec_reference_results/parametric/<release_id>/` before Phase 7 — otherwise
  **omit**: T21/T22 marked unavailable, this entry cited; `results/` staging is never read.
- **Affected sections/deliverables:** T21/T22, exhibit_plan.csv, supplement;
  assumption_register.csv (historical provenance if artifacts are located).
- **Responsible phase:** Phase 0/2 (provenance/tooling), promotion before Phase 7.
- **Phase 7 resolution note (2026-07-11, appended):** the **omit** branch is
  exercised. No admissible parametric-sensitivity release exists (Phase 6
  disposition; `results/paper_tables/provenance.json` records that T21/T22
  were NOT exported). `generate_parametric_tables.py` was NOT run for output;
  the parameter-sensitivity tables T21/T22 (T-SENS, `tab:sensitivity`) remain
  **unavailable**, no Word-native source was emitted for them, and the
  committed `papers/tables/T21.tex` / `T22.tex` fragments stay stale-excluded.
  This entry is the citation for the absence.

## EG-007 — ACE controller as an inherited bandit mechanism

- **Desired claim:** "DT-GSK's adaptive knowledge control (ACE) is a UCB1/D-MAB
  operator-selection mechanism and inherits its regret guarantees."
- **Why it matters:** A formal-inheritance claim would upgrade the design rationale from
  motivation to theory.
- **Closed-corpus sources checked:** `auer2002finite`, `fialho2010adaptive` (cards:
  grounding only, per Appendix B.7 "not proof that the exact ACE mechanism is inherited").
- **Empirical artifacts checked:** none yet — mechanism-level verification against the
  frozen `src/` code has not been performed (Phase 3 implementation-correspondence task).
- **Why support is insufficient:** The bandit theorems assume stationary reward
  distributions; an evolutionary run is non-stationary, and no corpus source connects
  the exact ACE policy to a proven bandit policy.
- **Disposition:** **narrow** — cite the bandit keys as conceptual grounding for
  "principled adaptive allocation among discrete options"; any stronger wording requires
  **additional analysis** (frozen-code correspondence proof) before use.
- **Affected sections/deliverables:** Method/design-rationale prose,
  implementation_correspondence.md.
- **Responsible phase:** Phase 3 (correspondence) / Phase 8 (prose).

## EG-008 — Superiority beyond the GSK family panel ("state of the art", CEC winners)

- **Desired claim:** "DT-GSK outperforms state-of-the-art optimizers / CEC competition
  winners (jSO, LSHADE-cnEpSin, LSHADE-SPACMA, EBLSHADE ...)."
- **Why it matters:** Reviewers routinely ask how a family-improvement compares outside
  its family; the strongest desirable headline would be cross-family.
- **Closed-corpus sources checked:** `jawad2024egsk` (its SOTA table reuses numbers from
  original papers, not a common-environment rerun), `mohamed2020gaining` (no LSHADE-class
  comparators), `alfadli2025atmals`, `apgsk2021` (CEC2020 only, mostly non-significant vs
  winners), `khalfi2023csm`, `zhou2021iade` (context: winner-class algorithms dominate).
- **Empirical artifacts checked:** immutable evidence release covers the seven-algorithm
  GSK-family panel (gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk); no
  winner-class comparator runs exist in the admissible evidence.
- **Why support is insufficient:** Appendix C prohibits claiming general superiority from
  a same-family panel; no admissible common-environment cross-family data exists, and the
  corpus contains no DT-GSK-vs-winner comparison.
- **Disposition:** **narrow** — all superiority claims scoped to the verified GSK-family
  panel, exact suites/dimensions; cross-family positioning stays qualitative
  (competition-context sentences per EG-002). Cross-family runs would be **additional
  experiment** and are out of scope for the frozen design.
- **Affected sections/deliverables:** Abstract, contributions, conclusions, cover letter;
  claims_evidence_matrix.csv; comparability_audit.md.
- **Responsible phase:** Phases 4/8 (prose), Phase 10 adversarial review.

## EG-009 — Locator/version fidelity limits of local copies

- **Desired claim:** Citations carrying published-version pagination/venue detail for all
  sources (journal page numbers, official proceedings pagination, verbatim quotes).
- **Why it matters:** Locator precision is required for every cited claim
  (claims_evidence_matrix.csv); wrong pagination is a verifiable citation error.
- **Closed-corpus sources checked (10 affected keys):** `mohamed2020gaining` (online-first,
  no journal pagination), `omidvar2014dg` (accepted manuscript), `khalfi2023csm` (author
  manuscript), `wolpert1997nfl` (1996 preprint; TEVC pagination absent), `zhou2021iade`
  (preprint; TGCN venue/DOI unconfirmable locally), `nomer2021gskrl` (author version;
  NILES venue/DOI unconfirmable locally), `jones1995fitness` (SFI working paper, not the
  cited ICGA-6 pagination), `efron1993introduction` (60-page excerpt),
  `david_order_statistics` (12-page excerpt; text layer on title page only),
  `nelder1965simplex` (image-only scan; no extractable text).
- **Empirical artifacts checked:** n/a (literature gap).
- **Why support is insufficient:** Local copies are preprints/author versions/excerpts or
  image-only scans; published pagination and verbatim machine-verifiable quotes are not
  locally verifiable for these keys.
- **Disposition:** **narrow** — locators use the local copy's pagination (as recorded in
  each evidence card); no verbatim quotations from the two image-only/partial-text files;
  venue metadata stays as in references.bib (bib is the citation of record; card notes
  document the version difference). Optional **additional experiment** (supply text-native
  copies, e.g., OCR for nelder1965simplex) if heavy citation use is needed.
- **Affected sections/deliverables:** citation_usage_map.csv, claims_evidence_matrix.csv,
  Phase 10 citation verification.
- **Responsible phase:** Phase 1 (documented), enforced Phases 4-10.

## EG-010 — NFL refinements and continuous-domain caveats

- **Desired claim:** Discussion of sharpened/focused NFL results, NFL for non-closed
  function classes, or continuous-domain NFL caveats beyond Wolpert & Macready (1997).
- **Why it matters:** A rigorous NFL framing sentence might otherwise invite reviewer
  pushback that the original theorems address finite discrete spaces.
- **Closed-corpus sources checked:** `wolpert1997nfl` (preprint; original theorems only).
- **Empirical artifacts checked:** n/a (literature gap).
- **Why support is insufficient:** All NFL refinement literature is outside the corpus.
- **Disposition:** **omit** — keep NFL to the single bounded-premise use sanctioned by
  Appendix B.9 (motivate structure-exploiting design and bounded claims); no refinement
  discussion.
- **Affected sections/deliverables:** Introduction/discussion framing.
- **Responsible phase:** Phase 8.

## EG-011 — EGSK port equivalence (MATLAB fmincon/SQP vs SciPy-SLSQP)

- **Desired claim:** "The Python EGSK panel member is equivalent to the published eGSK
  reference implementation."
- **Why it matters:** EGSK is a family-panel comparator; its published mechanism uses an
  SQP escape (MATLAB fmincon), while the local runnable port substitutes scipy-SLSQP
  (master Section 4.5 lists the egsk evidence provenance as a protocol anchor to verify).
- **Closed-corpus sources checked:** `jawad2024egsk` (documents the SQP mechanism and
  reference implementation; says nothing about SciPy or port equivalence).
- **Empirical artifacts checked:** verification of which provenance (fmincon reference
  CSVs vs SciPy port runs) backs the admissible egsk evidence is a Phase 2 protocol-anchor
  task, not yet performed.
- **Why support is insufficient:** No corpus source or validated artifact establishes
  numerical equivalence between the two solver backends.
- **Disposition:** **narrow** — disclose the substitution and the exact provenance of the
  egsk rows used (per the Phase 2 anchor check); make no equivalence claim. If both
  provenances exist, an **additional analysis** comparing them may be pre-registered.
- **Affected sections/deliverables:** Methods (panel description), comparability_audit.md,
  data_ledger.csv.
- **Responsible phase:** Phase 2 (provenance verification) / Phase 8 (disclosure prose).

## EG-012 — Cross-budget numeric comparison with FDB-AGSK's published results

- **Desired claim:** Direct numeric comparison of published FDBAGSK error values with
  family results computed at the 10,000·D budget.
- **Why it matters:** FDB-AGSK is a family baseline; readers may expect its published
  numbers to be commensurable with the panel tables.
- **Closed-corpus sources checked:** `fdbagsk2023` (its CEC2017/CEC2020 evidence uses a
  1000·D budget — 10x smaller; D = 30/50/100 only, no D = 10).
- **Empirical artifacts checked:** the admissible panel evidence for fdb-agsk in
  `benchmarks/cec_reference_results` is the in-house rerun at the unified protocol (the
  panel comparison itself is therefore unaffected).
- **Why support is insufficient:** Budgets differ by 10x; Appendix C prohibits comparing
  values across materially different termination budgets without qualification.
- **Disposition:** **narrow** — cite `fdbagsk2023` for mechanism and for its qualitative
  diagnosis (AGSK premature convergence) "at its budget"; never place its published
  numbers next to 10,000·D panel numbers.
- **Affected sections/deliverables:** Related work, panel-table captions,
  comparability_audit.md.
- **Responsible phase:** Phases 4/8.

## EG-013 — Universal novelty claims

- **Desired claim:** "DT-GSK's mechanisms are novel in the literature / first-ever."
- **Why it matters:** Novelty statements are expected in contributions lists; unbounded
  novelty is a desk-reject risk and is prohibited wording (Appendix C.2).
- **Closed-corpus sources checked:** the whole 57-key corpus (the 13 B.2 variant cards
  document which GSK modifications already exist: OBL, Cauchy mutation, multi-population,
  RL parameter control, FDB guides, archives, negative kf, SQP escapes, etc.).
- **Empirical artifacts checked:** n/a (literature gap).
- **Why support is insufficient:** A closed corpus cannot establish absence of prior art;
  Appendix C prohibits claiming universal novelty from a closed corpus.
- **Disposition:** **narrow** — describe differences from the specific, verified
  mechanisms in the corpus ("differs from the surveyed GSK variants in ..."); no
  "first-ever"/"novel in the literature" wording.
- **Affected sections/deliverables:** Contributions, abstract, highlights, cover letter.
- **Responsible phase:** Phases 4/8, Phase 10 review.

---

*Seeded gaps: 13 (EG-001 ... EG-013). EG-001 RESOLVED 2026-07-10 (CR-0005) — NO remaining blocking literature gap;
EG-004/005/006 are the pre-declared empirical known gaps (memory cost, GenLog release,
parametric sweep); the remainder are narrowing constraints harvested from the evidence
cards' unsupported-uses sections.*
