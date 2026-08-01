# Paper Completion Plan — five-suite manuscript to `dtgsk-submission-v2.0`

> **HISTORICAL RECORD — executed and superseded.** The phases in this plan were
> completed; the manuscript has since advanced through several further freeze
> passes (the round-2 and round-3 review batches and the disclosure amendment).
> For the current pass and tag read papers/governance/main_manuscript_freeze_manifest.json (its `phase` field) and the newest entry in papers/governance/decision_log.md; this banner deliberately
> no longer names one, because hardcoding it here is what left it stale across
> two successive re-mints. Retained as process evidence; do not read its status
> statements as current.


Status: **AWAITING AUTHOR APPROVAL — no manuscript file is touched until then.**
Evidence-tree closure: **VERIFIED CLOSED** (see Appendix).
Baseline: all five suites complete, promoted, and analyzed (85,855 runs across 35
banks; releases `rel-2026-07-20-67d9345f9` / `lsgo-rel-2026-07-28-ff1a046ef` /
`cec2020-rel-2026-07-29-5867abe1e`; ablation `abl-rel-2026-07-20`). Registered
statistics computed for every family; outcome sentences data-resolved (SAP
Amendments 1–2). Citation corpus at 61, validator green. Evidence-tree closure
audit: see the verdict appended at the end of this document.

The empirical story the manuscript must now tell, fixed by the registered
pipeline and not negotiable during drafting:

| Suite | DT-GSK standing | Authority |
|---|---|---|
| CEC2017 (primary) | first (2.48 aggregate) | frozen release, unchanged |
| CEC2013 | first (2.80) | frozen release, unchanged |
| CEC2011 | as frozen | frozen release, unchanged |
| CEC2020 | **fourth of seven**; Holm-separated in 5/24 pairwise (3 wins, 2 losses); `[AGSK first]` wording-bank sentence applies verbatim | Amendment 2 §A2.2–A2.3 |
| CEC2013LSGO | tied-first descriptive with AGSK; paired tests separate nothing; effect layer bars any superiority claim over atmals-gsk | Amendment 1 + 2 |

Standing constraints (absolute, unchanged): frozen releases never re-minted;
pre-registration append-only; LaTeX authored via Write/Edit only (heredoc
backslash trap); PDF epoch 1783468800 + FORCE_SOURCE_DATE=1; DOCX epoch
1783641600 (a persisted shell var silently breaks reproducibility — set it
explicitly, verify ×2); no reviewer names/DOIs/metrics fabricated; author
commits nothing mid-phase without coordination (the 01:20 sweep precedent).

---

## Phase W1 — Main-text surgery (owner: agent; gate: author reads the diff)

All sites pre-mapped file:line by the Phase-4 inventory (11-agent audit).

1. **Suite enumerations, 15 sites** (`main.tex:218/289`, `introduction.tex:134/158`,
   `performance.tex:9/106/748/959`, `related_work.tex:221`, abstract, Data
   Availability, plus the supplement mirrors): three-suite wording → five-suite
   wording. Where a site states the *scored* protocol, the CEC2020/LSGO protocol
   facts come from the addendum (38 cells / 30 runs; 15 functions / 25 runs).
2. **Headline recount**: "first overall on CEC2017 and CEC2013; fourth on
   CEC2020 (a comparator's home suite, predicted boundary); tied-first
   descriptive on CEC2013LSGO with no paired separation" — counts filled only
   from `friedman_ranks_*_overall.csv` files, never typed from memory.
3. **Pre-registration surfaced as a strength**: one main-text sentence records
   that the CEC2020 analysis and all outcome wording were committed before any
   CEC2020 result existed (signing commit `5c9bfae82`), pointing to S8.
   NO minute-level margin in the manuscript: the "15m52s" figure is attested
   only in Amendment 1 (line 52, a dated record) and derives from an
   unpromoted file mtime -- the closure audit found a second defensible anchor
   (first session log, 16m39s), which proves minute precision is
   anchor-dependent. The commit-level fact is git-verifiable; minutes are not.
4. **Claims matrix**: LM-05 narrowed (bound-constrained ceiling D=100 → LSGO is
   family-internal, see RS-13/LM-06); RS-12/RS-13/LM-06 resolved from
   PENDING_PREREGISTERED to final wording — RS-12 takes the `[AGSK first]`
   sentence + the 5-of-24 count; RS-13 takes the tied-first ceiling; LM-06 the
   adopted limitation sentence.
5. **Adopted disclosure sentences placed**: (a) LSGO scope sentence in the
   results section + S7 echo (cites `molina2018shadeils`/`latorre2013mos` —
   published values only); (b) conclusions limitation; (c) Data Availability
   sentence (the reworded no-in-repo-validation version) + all three release ids.
6. **`supplementary.tex:1879`** replaced with the drafted accurate wording
   (CR-0006 + ablation A1 history disclosed).
7. **Conflict-adjacency disclosure** (AGSK/CEC2020, co-author) in the CEC2020
   results passage and the conflicts block.
8. False-sentence sweep re-run after edits (grep patterns from the inventory),
   PLUS `supplementary.tex:649-653` ("the complete convergence record ... every
   scored function of every suite") -- true for three suites, false-adjacent for
   five; re-scope the sentence to the suites whose convergence record S3 carries.

Exit gate: every edited sentence traces to a committed CSV or registered text;
`audit_manuscript.py` review-pattern hits adjudicated in writing; author reads
the full diff before W4 builds.

## Phase W2 — Supplements S7 + S8 (owner: agent; parallel with W1)

1. **S8** from the committed skeleton: every FILL slot populated from
   `papers/analysis/cec2020-rel-2026-07-29-5867abe1e/cec2020/*.csv`; outcome
   sentence = the `[AGSK first]` variant verbatim; the D-0024 inspection ledger
   disclosed (what was seen mid-campaign, and that dt-gsk partials were not
   inspected until the author surfaced D5); power disclosure; robustness
   subsection notes the mean-vs-median ordinal movements and that the binding
   instability rule did not fire.
2. **S7** (LSGO): protocol + tier statement (descriptive-after-inspection vs
   the confirmatory paired layer); Friedman/Nemenyi table; both Wilcoxon
   layers; effect sizes with the F1-vs-gsk estimand divergence disclosed;
   the Ackley-variant panel note; the D-8.4 linkage-value provenance sentence
   (structural rule, contemporaneous record, no parameter search, timing
   disclosed); scope sentence echo.
3. Appended after S6 — S1–S6, S6.5–S6.7 never renumbered. `\supplementary{}`
   block and label registry updated; exhibits enter the caption registry.

Exit gate: S7/S8 numbers diff-checked mechanically against their source CSVs
(script, not eyes); no value appears that the bundles do not contain.

## Phase W3 — Exhibits + cross-format plumbing (owner: agent)

1. New-suite table fragments + word_sources JSON generated from the analysis
   bundles (new generators mirror the frozen ones; frozen generators untouched).
   FIRST: reconcile the three-way table-id collision the audit found -- the
   claims matrix says T15=CEC2020/T16=LSGO, FINAL_PUBLICATION_PLAN 4.2(f) says
   T17=LSGO/T18=CEC2020 (suite order reversed), and `_paper_tables/T15.csv`/
   `T16.csv` already exist with CEC2017 content. Ruling to apply: claims-matrix
   tokens are a separate namespace from `_paper_tables` filenames (existing
   precedent: T04 token vs T4.csv), so keep the matrix tokens, assign NEW
   non-colliding filenames (T17/T18 per the plan), and record the mapping in
   the artifact-binding register.
2. DOCX pipeline: new tables registered; `validate_docx` + cross-format parity
   extended to the new exhibits; captions self-contained per registry rules.

Exit gate: parity 0 FAIL including new rows; word_sources round-trip.

## Phase W4 — Builds at pinned epochs (owner: agent)

PDF (epoch 1783468800, FORCE_SOURCE_DATE=1) ×2 byte-compare; DOCX (epoch
1783641600 — exported explicitly in the build command, never inherited) ×2
byte-compare; supplement likewise. Any Overfull >2pt fails per the standing
hygiene gate.

## Phase W5 — Full gate battery + adversarial sweep (owner: agent)

pytest (full), ruff, config locks, frozen-analysis 115/115, union
strict-inventory (3 manifests) zero unlisted, both analysis bundles re-hashed,
citation controls C1–C5, provenance-claims validator on source AND rendered
artifacts, DOCX validators, cross-format parity, build hygiene. Then the
review-prompt panel applied per layer 1.5.0-N (scope review: the three
load-bearing disclosure sentences PRESENT and unhedged; no external appears as
comparator; registered-vs-reported comparison for CEC2020).

## Phase W6 — Governance closure (owner: agent)

Review-prompt §1.5.1 populated variables updated in one pass (EMPIRICAL_SCOPE
five suites, release ids, standings); BENCHMARK_EVIDENCE_INDEX rows for the
cec2020 release AND both analysis bundles (the index currently mentions
cec2020 zero times); `_pending_refreeze.json` tickets flipped as satisfied;
decision-log closure entry; deviation-record dispositions final. Also record
the audit's reproducibility footnote: `generate_trace_figures.py` and
`generate_adaptive_params_panel.py` read `results/dt-gsk/...` inputs that are
UNTRACKED, so two committed figures cannot be regenerated from a clean
checkout -- a pre-existing exposure of the frozen manuscript, disclosed in the
deviation record rather than silently carried.

## Phase W7 — Re-freeze pass 24 + tag (owner: agent mints, author confirms)

Fresh `main_manuscript_freeze_manifest.json` mint (15 files incl. rebuilt
PDF/DOCX); `check_manifest` 15/15; freeze statement pass 24 appended;
annotated tag **`dtgsk-submission-v2.0-<date>`** (v1.0 retained, never moved).

## Phase W8 — Author-side post-tag checklist (owner: YOU)

1. `git push origin main --tags`.
2. COMP-001b resumes: dedicated public repo (snapshot of 02-GSK_Family only —
   never the monorepo), GitHub Release from the v2.0 tag, Zenodo toggle ON
   BEFORE the release, DOI recorded; SuSy submission with committed artifacts
   (never open-save the DOCX first — D-WORD-01).
3. Submission metadata you already supplied (address/phone) goes into SuSy
   only, never into repo files.

Ordering: W1 ∥ W2 → W3 → W4 → W5 → W6 → W7 → W8. Estimated agent time
W1–W7: one focused working day plus the author read of the W1 diff.

---

## Appendix: evidence-tree closure audit verdict (2026-07-29)

**VERDICT: TREE CLOSED.** Four-agent audit (consumer census, staging
classification, integrity re-verification, adversarial break-attempt), all
green at HEAD `e46d0c3f7`:

- Every S7/S8 FILL slot, every Phase-4 sentence input, and every headline
  number sources from a committed, manifest-bound artifact (census table on
  file; 5-of-24 pairwise count and all ordinals independently recomputed).
- Staging classification: everything under `results/_run_all/` is either
  promoted or deliberately excluded under recorded authority (Section 11
  exclusions; CR-0019 externals). Gap list: EMPTY after the sweep.
- Integrity: union strict-inventory 3403/3403 + 173/173 + 336/336, zero
  unlisted; frozen-analysis 115/115; both new bundles re-hashed clean against
  their internal manifests; `_paper_tables` 17/17; `_ablation` sample clean.
- Curves: NO prescribed S7/S8 exhibit needs the excluded curves (verified
  against the plan's exhibit lists and the skeleton's amendment-gated rules).
  The audit additionally corrected its own census: the optional S8 convergence
  figure, if ever amended in, is buildable from the PROMOTED gen_logs -- no
  curve promotion would be needed.

Non-blocking caveats, all absorbed into the phases above: (a) no minute-level
pre-registration margin in the manuscript (W1.3 -- the figure is
anchor-dependent; commit-level fact only); (b) three-way T-id reconciliation
(W3); (c) `supplementary.tex:649-653` added to the false-sentence sweep (W1.8);
(d) untracked trace-figure inputs disclosed (W6); (e) index rows for the
cec2020 release and analysis bundles (W6).
