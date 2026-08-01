<!-- Provenance: produced 2026-07-28 by a six-lens expert panel (campaign
engineering, statistics, evidence/governance, manuscript architecture,
adversarial integrity, build pipeline) + synthesis, grounded in the repository
at commit 45b1d35e8. Verified first-hand before installation:
  (1) scripts/run_all_cec2020.py hard-points at configs/agsk_cec2020.yml whose
      seed_policy is `reference`, NOT `unified` -- one accidental invocation
      poisons the paired design. Confirmed at run_all_cec2020.py:9 and
      agsk_cec2020.yml:19.
  (2) configs/family_cec2020.yml has no workers key and default_worker_count()
      returns 2 -- the --workers 14 flag is mandatory or the campaign runs
      ~7x longer.
  (3) Campaign cost independently measured (150k-eval probes, extrapolated):
      gsk ~10.7 CPU-h; dt-gsk 10.2x gsk (fixed per-generation subsystem cost
      dominates at cheap evals); 7-algorithm total ~250-270 CPU-h, ~20-30 h
      wall at 14 workers -- consistent with the panel's independent estimate
      from frozen CEC2017 runtime banks.
Everything else carries the panel's own confidence. -->

# FINAL PUBLICATION PLAN — DT-GSK, Four(/Five)-Suite Scope

> **HISTORICAL RECORD — partially superseded.** Status statements in this plan
> (including any manuscript-freeze tag it names) describe the state when it was
> written. For the current freeze pass and tag, read papers/governance/main_manuscript_freeze_manifest.json (its `phase` field) and the newest entry in papers/governance/decision_log.md ---
> this banner deliberately no longer names one, because hardcoding the tag here
> is what left it stale across two successive re-mints. Its rulings remain in
> force unless a later governance record supersedes them.


**Document:** `docs/development/FINAL_PUBLICATION_PLAN.md`
**Programme baseline:** clean tree at `45b1d35e8e54b4daf0fc0caeab148305fc563e14` (verified 2026-07-28). Manuscript frozen at tag `dtgsk-submission-v1.0-2026-07-25` (commit `41726c544`), pass 23. Primary evidence release `rel-2026-07-20-67d9345f9` (3,403 files, digests verified) — **never re-run, never re-minted, never superseded**. CEC2020: zero result banks. CEC2013LSGO: family banks 375/375 complete in `results/_run_all/`, unpromoted. CR register ends at CR-0018.
**Authority:** the three author scope decisions of 2026-07-27 (externals out of the paper; seven family algorithms on CEC2017/CEC2011/CEC2020/CEC2013LSGO; transformed Ackley only) plus the Decision Gate 0 outcome recorded in Phase 0.
**Standing constraints (absolute):** the author runs all campaigns (agent provides commands, never launches); never re-run cec2017/cec2011/cec2013 frozen banks; `overwrite: false` everywhere; never fabricate reviewer names/DOIs/metrics; the author commits/pushes (agent commits only when explicitly authorized); never run `finalize_evidence.py` end-to-end against the primary release.

---

## How to read this plan

Nine phases, 0–8. Each phase lists objective, entry criteria, exit criteria, and numbered tasks with owner (**author** / **agent** / either), effort, and dependencies. Tasks marked **[PARALLEL]** may run concurrently with the campaign compute window in Phase 1. Tasks marked **[HARD-HONESTY]** implement adversarial-lens rulings and are non-negotiable: they may not be weakened, deferred past their stated gate, or cut for page budget.

Branch notation: **[KEEP]** = CEC2013 stays (five-suite paper); **[DROP]** = CEC2013 removed (four-suite paper); unmarked = both branches.

---

## Inter-lens conflict rulings (binding for the rest of this document)

The six lenses disagreed on nine points. Programme-lead rulings, with reasoning:

**R1 — Gate 0 recommendation: KEEP CEC2013 (five suites).** Manuscript-architecture, evidence-governance, and the adversarial lens favor keep; only the build lens prices drop as cheaper (word budget). Ruling: keep. The drop branch's sole benefit — ~1.2pp/word relief — is achievable in the keep branch by the harvest list (Phase 4.2) plus, if needed, a CR raising the internal cap (CR-0008 precedent). Drop costs ~14 extra rewrite sites, surrenders a **favorable** first-place suite (DT-GSK 2.80 best-of-7 overall), weakens the headline from first-on-two to first-on-one, forces a public-facing rationale because the cited immutable release permanently ships the CEC2013 banks, and orphans the X-ABL-02 CEC2013-D50 ablation panel. Both branches remain fully priced below; the author decides.

**R2 — Campaign command: `python run.py --config configs/family_cec2020.yml --workers 14`.** The build lens's `scripts/run_all_cec2020.py` is **overruled**: verified this session, that wrapper hard-points at `configs/agsk_cec2020.yml` (`scripts/run_all_cec2020.py:9`) — AGSK-only, `seed_policy: reference` (not unified), workers 2, stale data root. One accidental invocation injects reference-schedule seeds into `results/_run_all/agsk/cec2020/per_run.csv` and silently breaks the paired design. The wrapper is neutralized in Phase 0 (task 0.7). `--workers 14` is mandatory (`src/gsk_family/runners/parallel.py:54-64` defaults to 2).

**R3 — Analysis driver: a physically separate `phase6b`, not in-place extension of `phase6_run_analysis.py`.** The statistics lens wins over EG-08/T11. Verified: `phase6_run_analysis.py:74` defaults `GSK_REL_ID` to the **stale** `rel-2026-07-16-78f075cb0`, and lines 84–95 hardcode the three frozen suites — a bare invocation is a live footgun. A sibling driver (`papers/scripts/phase6b_run_analysis_newsuites.py`) that imports `src/gsk_family/analysis/statistics.py` primitives **without editing them**, cannot write under any `rel-2026-07-20` path, and carries the k-parameterized Nemenyi plus exact/permutation additions, eliminates the frozen-suite regression channel by construction. The byte-identity guard (task 0.5) still runs after every phase as defense in depth. `phase6_run_analysis.py` is never edited.

**R4 — Re-freeze tag: `dtgsk-submission-v2.0-<date>`.** EG-17 over T17's v1.1. A scope change (suites added, external baselines removed from the paper, headline recomputed) is a major version; v1.0 is retained as historical, never moved or deleted. Zenodo gets a **new DOI version** via a new GitHub Release; the v1.0 DOI is never re-pointed.

**R5 — `skipped_runs.csv` (dt-gsk LSGO, 443 MemoryError rows): promoted under an explicit `deviation_record` file class** (EG-06), overruling CE-7's exclusion. Erasing the file while promoting the per_run rows it explains would recreate a discoverable gap. Sequence: adjudicate first (Phase 2.3), record in `production_deviation_record.md`, then promote with in-manifest annotation. The author ratifies this disposition (author decision A9).

**R6 — One pre-registration artifact, not four.** S1, EG-04, INT-01/INT-02, PREREG-01 and T03 merge into a single file: `papers/build_prompt_phases/phase_05/statistical_analysis_plan_addendum_cec2020_lsgo.md` (frozen SAP body untouched; governed as a Section-13 confirmatory amendment). Its SHA-256 and commit hash are recorded in `decision_log.md`; both future release manifests carry a `preregistration` field binding that hash. The same commit carries the S8 supplement skeleton and the PENDING claims-matrix rows. Verbatim text in Phase 0.3.

**R7 — External-baseline relocation target: `benchmarks/cec_reference_results/_external_baselines/cec2013lsgo/<alg>/`** (EG-02 naming wins over T08's `_external_context/`), with EV-09 provenance sidecars and a status README. One name, used everywhere.

**R8 — Citation keys: SHADE-ILS and MOS keys ARE admitted.** EG-01 left this conditional ("only if the limitations sentence cites them"); the adversarial lens's INT-03(a) **mandates** citing published SHADE-ILS/MOS results (never our banks). The condition therefore resolves to yes. Corpus reopens 57 → 61: (1) CEC2013LSGO suite definition (Li/Tang/Omidvar/Yang/Qin 2013 — no key exists; `liang2013cec2013` is the wrong suite), (2) `yue2020cec2020` (in `references.bib:694`, not in the allowed set), (3) SHADE-ILS (Molina et al.), (4) MOS (LaTorre et al.). DECC-G is **not** admitted (not named in the disclosure sentence). Each key costs the full lockstep (bib + PDF + evidence card + 4 CSV maps + `allowed_citation_keys.txt` + PAPER_BUILD_PROMPT Appendix A/B.4).

**R9 — LSGO evidential status (binding tier assignment).** The family Friedman (3.133 tie, p=0.0372) and per-function means were inspected before any registration: they are **descriptive-after-inspection**, disclosed as such, never confirmatory, never headline. The never-computed run-level Wilcoxon+Holm + A12 + BCa layer is **confirmatory-with-disclosure**; the across-function Wilcoxon is **supporting-with-disclosure** (inputs seen, p-values not). Statistics and adversarial lenses aligned; adopted verbatim.

Also settled without conflict: two separate non-superseding underscore releases (`_cec2013lsgo/` mintable now, `_cec2020/` after the campaign) — never one combined release, never a primary re-mint; the 1.5.0-N review-prompt supersession layer lands in **Phase 0** (adversarial sequencing) with only its populated variables updated in Phase 6; S7 = LSGO and S8 = CEC2020 are **appended** after S6, S1–S6 and S6.5/S6.6/S6.7 never renumbered.

---

## PHASE 0 — Decision Gate 0, pre-commitment, and campaign preflight

**Objective:** rule keep/drop for CEC2013; land every artifact that must exist **before** the first CEC2020 run — above all the pre-registration commit, whose timestamp is the single cheapest credibility purchase in the project and which expires the instant the campaign starts; open the parallel forensic and citation tracks.

**Entry:** clean tree at `45b1d35e8`; this plan approved.
**Exit:** Gate 0 recorded; pre-registration commit pushed with hash logged; preflight checklist green; parallel tracks (0.8–0.10) opened. **The campaign may not launch until exit criteria 0.2–0.7 are met.**

### 0.1 — Decision Gate 0: CEC2013 keep vs drop (owner: **author**; effort: trivial; blocking for Phase 4 wording only — does NOT block the campaign)

Zero compute either way: the frozen bank `benchmarks/cec_reference_results/cec2013/` stays inside the immutable release in **both** branches (a release may legitimately be a superset of the paper). Priced side by side:

| Dimension | KEEP (five suites) | DROP (four suites) |
|---|---|---|
| Compute | 0 | 0 |
| Evidence-tree ops | 0 | 0 (release never re-minted) |
| Rewrite sites | ~35 shared scope sites only | shared sites **+ ~14 more**: delete `performance.tex:649-725` (subsection 4.4 + `tab:friedman-cec2013`), supplement S2.3 (`supplementary.tex:421-510`) and S3.3 (`942-997`), T11–T14 + SA03 fragments and word_sources, `conclusions.tex:54-57`/`71-73`, early-stop tally rescope (`performance.tex:173-175`), every AN-\*-2013 BIND id |
| Claims matrix | rows untouched | PR-03, RS-11 → `RETIRED_SCOPE` with date (never deleted); MT-02/MT-06/AB-02 rewordings |
| Headline | "first overall on CEC2017 and CEC2013" survives; recounted over five suites | strictly weaker ("first overall on CEC2017"); note CEC2013 **favors** DT-GSK (2.80 best-of-7) so drop is against-interest, not cherry-picking |
| Page/word budget | ~+0.5pp over the 40pp cap after full harvest → harvest a second figure or CR the cap | ~−1.2pp relief; abstract frees ~2 words |
| Public optics | none | **mandatory** stated-rationale sentence in Data Availability (the cited release permanently contains the CEC2013 banks; the public v1.0 tag claims first-overall on it) — silent drop is **vetoed** by the adversarial lens |
| Ablation coupling | S6.5 CEC2013-D50 panels untouched | S6.5 panels kept but need a local CEC2013 protocol note inside S6 |

**Recommendation (R1): KEEP.** If the author rules DROP, the drop-only tasks are 4.7-D and 5.1-D below, plus the vetoed-unless-present disclosure sentence in 4.6.

### 0.2 — Governance reopening (owner: agent drafts, author approves; effort: small; blocking)

1. Register **CR-0019** in `papers/governance/change_request_register.csv` (register verified ending at CR-0018): final empirical scope = 7 family algorithms × 4(/5) suites; the eight vendored externals appear in no panel/table/claim and remain in-repo as validated tooling; CEC2013LSGO transformed-Ackley only (the raw kernels exist behind `ackley_raw_scope` but are never activated; `ackley_raw_active()` is False for every bank); records the Gate 0 outcome. This CR formally **supersedes** LSGO campaign ruling A-4 (external descriptive-context layer) and amends `comparability_audit.md` §3 and the `data_ledger.csv` context rows to "out of paper scope".
2. Register **CR-0020**: citation corpus reopened for exactly the four keys of ruling R8.
3. Write **PAPER_REVIEW_PROMPT.md layer 1.5.0-N** now (adversarial sequencing): supersedes 1.5.0-M(i) (`papers/PAPER_REVIEW_PROMPT.md:1277-1285`, which currently *vetoes* family-internal-only ranks) and 1.5.0-M's external-baseline mandate; records the compensating mechanism (the 0.4 disclosure sentences + the `_external_baselines/` status package); marks 1.5.0-M partially superseded. Populated variables (1.5.1) are updated later, in Phase 6.4.
4. Reopen `papers/governance/_pending_refreeze.json` (currently CLOSED) with standing constraints: no optimizer-core edit; no re-run of frozen banks; frozen-suite analysis outputs byte-identical. Move `phase_gate_register.csv` rows FROZEN → reopened. `decision_log.md` entries for all of the above.

### 0.3 — The pre-registration commit (owner: agent drafts, **author signs and commits**; effort: medium; **HARD ordering constraint: must precede the first `run.py` invocation — worthless once a single `per_run.csv` row exists**)

One commit containing: (a) the SAP addendum below, verbatim; (b) the S8 supplement skeleton with empty result slots (Phase 5.2 shape); (c) PENDING rows RS-13 and LM-07 in `claims_evidence_matrix.csv` carrying the wording-bank templates; (d) `configs/family_cec2020.yml` untouched as-is at the pinned commit. Record the addendum file's SHA-256 + the commit hash in `decision_log.md`. The commit timestamp **is** the pre-registration evidence.

**Verbatim addendum text, ready to commit as `papers/build_prompt_phases/phase_05/statistical_analysis_plan_addendum_cec2020_lsgo.md`:**

```markdown
# Statistical Analysis Plan — Addendum 1 (pre-registered):
# CEC2020 and CEC2013LSGO suites

Status: CONFIRMATORY AMENDMENT under SAP Section 13. The frozen SAP body is
untouched; this addendum extends it by strict analogy. This file is committed
BEFORE any CEC2020 result exists; its commit hash and SHA-256 are recorded in
decision_log.md and bound into the manifests of both future evidence releases.

## 0. Declaration of data state at signing
At the commit carrying this file: (i) ZERO CEC2020 result banks exist anywhere
in the repository or on any machine used by this project — every CEC2020
hypothesis, family definition, and wording template below is therefore
outcome-blind; (ii) CEC2013LSGO family banks are complete (7 algorithms x 15
functions x 25 runs) and HAVE been partially inspected — the exact prior
exposure is declared in Section 6 and governs the evidential tier of every
LSGO analysis.

## 1. Scope and suite roles
Panel: the seven GSK-family algorithms (gsk, agsk, apgsk, fdb-agsk,
atmals-gsk, egsk, dt-gsk); proposed = dt-gsk; comparators m=6. External
(non-GSK) optimizers appear in no analysis under this addendum. Suite roles:
CEC2017 remains PRIMARY (development); CEC2011[, CEC2013] corroborative;
CEC2020 = secondary, pre-registered confirmatory (budget-scaling breadth);
CEC2013LSGO = secondary, large-scale, family-internal only, post-hoc
exploratory/confirmatory per Section 6. No suite is ever labeled "validation".

## 2. Endpoints and bases
CEC2020: error = f(x_best) - f* with floor 1e-8; error basis throughout;
protocol = 10 functions, dims 5/10/15/20, F6/F7 undefined at D5 (38 protocol
cells), runs = 30 (Yue et al. 2019, Sec. 2.1), MaxFES 50,000 / 1,000,000 /
3,000,000 / 10,000,000 by dimension, unified seed policy, base seed 20240620.
CEC2013LSGO: raw best_fitness basis (CEC2011-style; the error column is not
populated on this suite); 15 functions, D=1000 (F13/F14 overlapping at 905),
runs = 25, budget 3e6 FES; F3/F6/F10 use the TRANSFORMED Ackley variant —
results on those functions are NOT comparable to published values obtained on
the raw variant, and no such comparison will be drawn.

## 3. Hypotheses
H1 (CEC2020, per dimension): the k=7 family members differ in central rank
    (four families, one per dimension).
H2 (CEC2020): DT-GSK vs each comparator, per dimension — across-function
    Wilcoxon and run-level paired Wilcoxon, Holm-corrected, two-sided,
    alpha = 0.05.
H3 (LSGO): family omnibus — DEMOTED to descriptive-after-inspection
    (Section 6); reported, never treated as confirmatory.
H4 (LSGO): DT-GSK vs each comparator, run-level paired Wilcoxon + Holm over
    the 25 unified-seed runs — never yet computed; CONFIRMATORY-WITH-
    DISCLOSURE; this layer alone can support or refute any family-standing
    sentence about LSGO.
Directional expectation stated in advance for CEC2020: AGSK and APGSK are
favored on their home regime (AGSK won the CEC2020 competition; Mohamed et
al. 2020 is a co-author's paper). All of DT-GSK's dimension-gated subsystems
(ISM channels, eigenframe polish, raised floor) are structurally OFF at
D<=20, so DT-GSK runs its adaptive scaffold tier only; a non-leading CEC2020
result is a predicted boundary finding of the dimension-tiering thesis, and
will be reported as such — never as "does not count".

## 4. Analysis families (registered ids)
CEC2020 —
AN-OMNI-2020-D5/D10/D15/D20: tie-corrected Friedman (M-026) + Iman-Davenport;
  N=8 blocks at D5 (F1-F5, F8-F10), N=10 at D10/15/20; decision criterion =
  Iman-Davenport at alpha=.05 PLUS a seeded within-block Monte-Carlo
  permutation p, B=100000, rng SeedSequence([20240620, 2020, dim, 0, 99]);
  the permutation p governs boundary disagreements (disclosed per row).
AN-RANKAGG-2020-OVERALL: descriptive unweighted mean of the four
  per-dimension mean ranks; caption MUST disclose the D5 reduced task set and
  the MaxFES regime change; no test is ever attached.
AN-PW-2020-D5..D20: across-function Wilcoxon on per-function mean errors,
  n=8/10; decision p = EXACT sign-flip enumeration (2^n); the normal-
  approximation value is also recorded for continuity with the frozen suites;
  method recorded per row (SAP 6a). Zero differences |d| < 1e-8 discarded;
  if n_eff < 6 the row reports verbatim: "not decidable at alpha=0.05 (exact
  two-sided floor 2/2^5 = 0.0625)".
AN-PWRUN-2020-D*: per-function run-level Wilcoxon over the 30 unified-seed
  paired runs; Holm across functions per (dimension, comparator), m=8 at D5,
  m=10 otherwise; supplement exhibit.
AN-EFF-2020-D*: A12/Cliff's delta (run level) + BCa 95% CIs, B=10000, on
  paired mean-error differences; rng SeedSequence([20240620, 2020, dim, func,
  comparator_P1_index]). Suite ordinal 2020 is pinned here.
AN-ROB-2020: (1) mean-vs-median re-rank; (2) across-dimension aggregate
  variants — D10/15/20-only mean AND common-8-function-subset mean at all
  four dims; if either flips DT-GSK's ordinal vs the primary aggregate, the
  headline carries the instability disclosure (SAP Section 10 binding rule);
  (3) floor sensitivity 1e-6 vs 1e-8.
CEC2013LSGO —
AN-OMNI-LSGO-NATIVE: tie-corrected Friedman over 15 function blocks;
  DESCRIPTIVE-AFTER-INSPECTION (Section 6).
AN-PW-LSGO-NATIVE: across-function Wilcoxon, n=15, exact 2^15 enumeration,
  Holm m=6; SUPPORTING-WITH-DISCLOSURE.
AN-PWRUN-LSGO-NATIVE: run-level paired Wilcoxon over 25 unified-seed runs,
  Holm m=15 per comparator; CONFIRMATORY-WITH-DISCLOSURE (never computed
  before this addendum).
AN-EFF-LSGO-NATIVE: A12/Cliff + BCa B=10000; suite ordinal pinned = 2113
  (documented: "cec2013lsgo, distinct from 2013").
AN-ROB-LSGO: mean-vs-median; relative vs absolute tie band on the raw basis;
  leave-one-function-out Friedman (the F7/F15 deletions are inspection-
  informed and labeled exploratory).
Explicitly NOT registered, now or ever: AN-RANKAGG-LSGO; any cross-suite
pooled statistic. AN-RANKAGG-2017-OVERALL remains CEC2017-only.

## 5. Tie and degeneracy rules
Tie band |d| < 1e-8 absolute everywhere (SAP Section 4 consistency); LSGO raw
magnitudes additionally get the pre-registered relative-band robustness
variant. Fully-tied Friedman blocks are RETAINED (midrank to all; M-026
absorbs them); a fully-tied family reports "statistic undefined", never a
fabricated value. Degenerate BCa cells reuse the SAP Section 7 disclosure
strings verbatim. n_eff is reported after zero-discard for every test.

## 6. LSGO prior-inspection disclosure (verbatim, dated at signing)
Before this addendum was written, the following LSGO quantities were
inspected informally: family-only Friedman mean ranks — dt-gsk 3.133 (tied
with agsk 3.133), atmals-gsk 3.533, gsk 3.867, fdb-agsk 3.933, apgsk 4.933,
egsk 5.467; omnibus p = 0.0372; Nemenyi CD separating only egsk; per-function
means showing dt-gsk winning F4 and F8 outright and placing last on F7 and
F15. Additionally, an all-native Friedman including three external LSGO
specialists was inspected (shade-ils 1.600, mos 2.467, dt-gsk 5.133 best of
the family). CONSEQUENCES: AN-OMNI-LSGO-NATIVE and all LSGO W/T/L
descriptives are DESCRIPTIVE-AFTER-INSPECTION — they may be reported with
this disclosure but carry no confirmatory weight and never enter a headline;
AN-PWRUN-LSGO-NATIVE and AN-EFF-LSGO-NATIVE have never been computed and are
registered here, before computation, as the confirmatory LSGO layer.

## 7. Power disclosure
At k=7 the Nemenyi critical distance is 3.185 (N=8), 2.849 (N=10), 2.327
(N=15) versus 1.673 at N=29: the CEC2020 and LSGO omnibus families are
low-powered by construction. Non-significance is worded "no separation
demonstrated", never "equivalent" or "no difference".

## 8. Pooling prohibition (absolute)
No statistic pools suites. No cross-suite Friedman, no pooled runs, no
cross-suite rank averaging, no cross-suite multiplicity family, no
"Holm-significant on k suites" arithmetic. Run-count heterogeneity
(51/[51]/25/30/25) and basis heterogeneity (error vs raw) therefore never
enter any test. The ONLY cross-suite statement permitted anywhere in the
manuscript is the count of independent per-suite descriptive standings.

## 9. Wording bank (pre-committed before any CEC2020 datum exists)
Suite standing = strictly lowest descriptive aggregate rank -> "first".
Exact tie -> "tied-first", a SEPARATE category never absorbed into "first on
X of Y". Headline template: "first on n1, tied-first on n2, second on n3 of
the Y suites' descriptive family-rank aggregates", with counts filled only
from pipeline output and per-suite inferential results enumerated suite by
suite. CEC2020 outcome sentences, all three pre-written:
  [DT-GSK first] "DT-GSK attains the best descriptive family rank on
  CEC2020; per-dimension pairwise tests are reported in S8."
  [AGSK first] "On AGSK's strongest suite — the CEC2020 competition it won —
  DT-GSK places <ordinal>; the family panel corroborates AGSK's published
  strength in this regime, consistent with the tiering thesis: every
  dimension-gated DT-GSK subsystem is inactive at D<=20."
  [tie] "DT-GSK and AGSK share the best descriptive family rank on CEC2020;
  paired tests (S8) do not separate them."
LSGO claim ceiling (regardless of how the confirmatory layer falls):
"DT-GSK and AGSK share the best descriptive family mean rank; no member
except eGSK (worse) is separable by the omnibus procedure; DT-GSK is last on
F7 and F15." Prohibited on LSGO: "leads", "first", "scales to D=1000",
"competitive" without a named supporting test, and any statement of the
F4/F8 wins unaccompanied by the F7/F15 last places. If the paired layer does
NOT yield Holm-significant separations in DT-GSK's favor, the binding
wording is: "tied-first descriptive rank; paired tests do not separate
DT-GSK from AGSK."

## 10. Conflict-adjacency disclosure
AGSK won the CEC2020 competition and Mohamed et al. (2020) is a co-author's
paper. This adjacency is disclosed here, in the manuscript wherever CEC2020
results are interpreted, and in the conflicts block — stated by the authors,
not discovered by reviewers.

## 11. Promotion and file-class policy (both future releases)
Promoted per cell: per_run.csv, per-dimension summary CSVs, the five
provenance files (environment.json, phase0_protocol.json, run_config.json,
seed_schedule.csv, verification.json), gen_logs/. Curves EXCLUDED with the
exclusion recorded in-manifest. dt-gsk's LSGO skipped_runs.csv is promoted
under the explicit file class "deviation_record", cross-referenced to
production_deviation_record.md. Expected row counts enforced: LSGO 375 per
cell; CEC2020 1,140 per cell (38 protocol cells x 30). Releases are separate,
non-superseding, underscore-prefixed; the primary release
rel-2026-07-20-67d9345f9 is never touched. CEC2020 verification.json entries
without a reference table report NOT_VERIFIED/NO_REFERENCE, never a vacuous
CONSISTENT.

## 12. Seeds and provenance
Unified seed policy, base seed 20240620, seed = get_cec_seed(20240620, dim,
func, run), identical across the seven algorithms per (dim, func, run) —
this identity is what makes every run-level test paired — and injective
within each algorithm. runs=30 for CEC2020 per Yue et al. 2019 Sec. 2.1;
runs=25 for LSGO per the campaign config. A pairing audit replicating
seed_and_pairing_audit.md Sections 1-4 over the native banks is a
precondition for every paired statistic on both suites.

## 13. Amendment integrity
This file is append-only after the signing commit. Any later change is a new,
dated, separately justified amendment; silent edits void the pre-registration.
```

### 0.4 — [HARD-HONESTY] Author approval of the three disclosure sentences (owner: **author**; effort: trivial; blocking for Phase 4)

Exact text (adversarial lens INT-03; load-bearing, must survive every page harvest):

- **(a) LSGO subsection scope sentence** (main text, S7 echo) — **ADOPTED as drafted 2026-07-28**, citations resolved to `molina2018shadeils` / `latorre2013mos` under CR-0020: *"The CEC2013LSGO analysis in this paper is family-internal: it ranks the seven GSK-family variants against one another under a common protocol. Dedicated large-scale optimizers — for example SHADE-ILS \cite{molina2018shadeils} and MOS \cite{latorre2013mos} — report substantially stronger published results on this suite than any GSK-family member, and no competitiveness with such specialists is claimed here; cross-paradigm comparison is outside this paper's scope."* Rationale for adopting unchanged: it cites PUBLISHED specialist results, never our own transformed-Ackley banks (which are non-comparable on F3/F6/F10), so it survives the RS-13 and LM-06 blocks; and the registered claim ceiling already prevents any competitiveness wording elsewhere. (Cites **published** results only — our transformed-Ackley F3/F6/F10 banks are not comparable to published MOS and are never cited as comparators.)
- **(b) Conclusions limitation sentence — ADOPTED as drafted 2026-07-28:** *"At D = 1000 no member of the family, DT-GSK included, approaches the performance that dedicated large-scale specialists report in the literature; the family's evidence of competitiveness therefore ends at the dimensionalities of the bound-constrained suites."* Rationale: the computed confirmatory layer strengthens rather than softens it — the registered run-level paired Wilcoxon found NO suite-level separation between DT-GSK and ANY family comparator on this suite, so even the family-internal standing is a tie, and the sentence remains the honest ceiling. Load-bearing per LM-06; may not be cut for page budget.
- **(c) Data Availability / supplement S5 sentence** (reworded 2026-07-28 after the external crossover audit; "validated" was not defensible — see decision_log D-0025): *"Beyond the analyzed suites, the repository also contains runnable implementations of eight non-GSK baseline optimizers and, for three of them (SHADE-ILS, MOS and DECC-G), complete result banks on CEC2013LSGO produced under this paper’s protocol. These implementations carry no validation evidence checkable within this repository: the vendored ports are byte-faithful copies whose author-code parity records reside in a separate project, and DECC-G is first-party code written from its source paper with no author-code oracle. They fall outside this paper’s analyzed scope, enter no panel, table, figure or claim, and no comparability audit against the family is claimed for them."*
- **[DROP only] Data Availability rationale sentence:** *"The archived evidence release additionally contains the complete CEC2013 (bound-constrained) result banks for all seven algorithms; that suite falls outside this paper's analyzed scope and was removed to reduce same-paradigm redundancy with CEC2017 in favor of regime breadth."*

Also fix, in Phase 4, the two sentences **already false today**: `supplementary.tex:1879` ("no evidence file was hand-edited") and the stale `rel-2026-07-16` ids in `BENCHMARK_EVIDENCE_INDEX.md`'s ledger.

### 0.5 — Byte-identity guard on frozen analysis outputs (owner: agent; effort: small; blocking)

Snapshot SHA-256 of every file under `papers/analysis/rel-2026-07-20-67d9345f9/**` into a manifest plus a standalone read-only re-check script. Re-run after **every** subsequent phase. This is the executable protection for the abstract's 2.48 (`main.tex:162`, AN-RANKAGG-2017-OVERALL), the ~599-row parity table, and the verbatim release id at `main.tex:267`.

### 0.6 — Campaign preflight hygiene (owner: either; effort: small; blocking for launch)

On the campaign machine, in order:
1. `git status` clean; record `git rev-parse HEAD` — the **entire** 7-algorithm campaign runs at this single commit (never repeat the LSGO six-commit spread).
2. **Numba cache purge** (documented trap — CEC2020 files were restored by copy on 2026-07-26 and `fp_regime.py:64` routes cec2020 through the numba backend): `find benchmarks/cec_suite_python -name __pycache__ -exec rm -rf {} +`
3. `python -m pytest tests/regression/test_family_golden_values.py tests/regression/test_cec2020_restored_cells.py -q` — expect 42/42 hex-identical + the F1/F8 D5/D15 oracle pins green.
4. Grid dry-check: `configs/family_cec2020.yml` resolves exactly 38 cells (8 at D5; (F6,D5)/(F7,D5) absent), budgets 50k/1M/3M/10M, runs=30, unified seed 20240620, `overwrite: false`, output root `results/_run_all` (writes only to `results/_run_all/<alg>/cec2020/`, which must not exist yet; `benchmarks/cec_reference_results` is write-refused by `ensure_output_root_allowed`).
5. ~2 GB free disk; Windows power plan set to never sleep.

### 0.7 — Neutralize `scripts/run_all_cec2020.py` (owner: **author** decides disposition, agent executes; effort: trivial; blocking for launch)

Verified: the wrapper invokes `configs/agsk_cec2020.yml` (reference seed policy, workers 2, stale data root). Repoint it at `configs/family_cec2020.yml` or rename/guard it so an accidental invocation cannot contaminate the AGSK bank with reference-schedule seeds. Record the change under CR-0019's umbrella.

### 0.8 — [PARALLEL] LSGO `.prebugfix` forensics — Track 0C-1 closure (owner: either; effort: medium; **blocks Phase 2 LSGO promotion and every LSGO claim; start immediately — it can invalidate the whole LSGO leg**)

Adjudicate the four `*.csv.prebugfix` siblings (`results/_run_all/atmals-gsk/cec2013lsgo/summary/`, `.../egsk/.../summary/`; the atmals F8/D1000 mean moved +29.6% across the fix). Identify the defect by name and commit; determine whether it touches the four pre-fix banks (gsk/agsk/apgsk/fdb-agsk, run 2026-07-22/23, never re-run); record the finding **either way** in `papers/governance/production_deviation_record.md`. If contamination is found: the LSGO leg is NO-GO pending an author-authorized >100 h re-run or the leg is dropped (author decision A7). Also in this task: the Track 0C-2 code-identity attestation (the seven family banks span six commits — re-verify one exact `best_fitness` triple per algorithm at HEAD, or scope the "one code base, one harness" claim to exclude the LSGO leg) and the `skipped_runs.csv` adjudication feeding ruling R5.

### 0.9 — [PARALLEL] Citation corpus lockstep — the long pole (owner: **author** supplies PDFs, agent does lockstep; effort: medium; blocks Phase 4)

Start in hour 1. Four keys per ruling R8. The CEC2013LSGO suite-definition PDF (Li/Tang/Omidvar/Yang/Qin 2013) is the critical item: the corpus is closed at 57 keys, `liang2013cec2013` (`references.bib:497-502`) is the **wrong** suite, and metadata must never be reconstructed from memory. If that PDF is genuinely unobtainable, the LSGO leg drops to deferred-with-disclosure while CEC2020 proceeds. `validate_citation_controls` C1–C5 gates all admissions.

### 0.10 — [PARALLEL] Evidence-namespace hygiene: the four unlisted files (owner: agent; effort: small; **blocks any mint, Phase 2**)

Verified live: `check_manifest.py --strict-inventory` reports exactly 4 unlisted files in the primary namespace. (1) Move `benchmarks/cec_reference_results/cec2013lsgo/{mos,decc-g,shade-ils}/*.csv` → `benchmarks/cec_reference_results/_external_baselines/cec2013lsgo/<alg>/` (ruling R7), each with an EV-09 provenance sidecar (publication + citation key, table/page, run count, FES budget, dims, objective-variant flag — MOS's published table is raw-Ackley — upstream SHA-256, source path) and a README: validated tooling, out of paper scope per CR-0019, transformed-Ackley non-comparability caveat, no comparability audit claimed. This simultaneously empties the plain `cec2013lsgo/` name that `finalize_evidence.py` P6 (`:1048-1049`) would silently absorb, removes the collision with the future promoted suite, and creates the disclosure surface. (2) Move `BENCHMARK_EVIDENCE_INDEX.md` → `benchmarks/cec_reference_results/_index/`; update the ~10 referencing files; fix its stale `rel-2026-07-16` ledger ids. (3) Exit gate: `python papers/scripts/check_manifest.py --manifest papers/governance/evidence_release_manifest.json --strict-inventory` → 3403/3403, **zero unlisted**; primary manifest untouched.

### 0.11 — [PARALLEL] Executable never-remint guard (owner: agent; effort: trivial)

Add a hard abort at the top of `phase_P2` and `phase_P6` in `papers/scripts/finalize_evidence.py`: refuse unless `GSK_ALLOW_PRIMARY_REMINT=1`, message naming `rel-2026-07-20-67d9345f9` as frozen-and-cited (P6 re-mints with a NEW release id at `:1118-1121` and its drift guard `:1091-1109` iterates old files only). Record in `docs/development/evidence_rerun_runbook.md`.

### 0.12 — [PARALLEL] Config lock gate (owner: agent; effort: small; blocking for launch)

Extend `scripts/validate_profile_lock.py` REQUIRED_LOCKS with `configs/family_cec2020.yml` pins (runs 30; dims [5,10,15,20]; budget map 50k/1M/3M/10M; `overwrite: false`; unified seed policy; protocol-aware F6/F7@D5 drop) plus the retroactive `configs/family_cec2013lsgo.yml` / `configs/dtgsk_cec2013lsgo.yml` locks (Track 0H, including the 22-key `linkage_block_size_by_dim` table). Nothing else prevents a silent edit between pre-registration and run.

---

## PHASE 1 — CEC2020 campaign execution (author-run)

**Objective:** produce the only missing compute in the entire scope: 7 algorithms × 38 protocol cells × 30 runs = 7,980 runs, ~2.95e10 evaluations.

**Entry:** Phase 0 tasks 0.2–0.7 and 0.12 complete; **pre-registration commit pushed**.
**Exit:** all seven banks complete and mechanically verified (1.6); heritage audit passed (1.7).

### 1.1 — Launch (owner: **author**; effort: large — ~20–30 h wall)

From `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1`, single command (ruling R2):

```
python run.py --config configs/family_cec2020.yml --workers 14
```

`--workers 14` is **mandatory** (harness default is 2). Optional tranche split — same bank, resume-safe, gives sanity data within ~2 h before committing to the long tranche:

```
python run.py --config configs/family_cec2020.yml --workers 14 --dimension 5,10   # ~1.5–2 h,  ~7% of compute
python run.py --config configs/family_cec2020.yml --workers 14 --dimension 15     # ~4–5 h
python run.py --config configs/family_cec2020.yml --workers 14 --dimension 20     # ~13–18 h, ~72% — run overnight/weekend
```

**Cost model** (from frozen CEC2017 runtime banks on this machine, cross-checked by a 36-run serial probe): per-algorithm core-hours gsk 9.0, agsk 34.3, apgsk 50.6, fdb-agsk 30.2, atmals-gsk 23.4, egsk 44.8, dt-gsk 54.9; **total 247–265 core-h ≈ 18–19 h ideal at 14 workers; plan 20–30 h** (JIT compiles, pool restarts; dt-gsk's fixed ISM cost may stretch toward 40 h worst case — a scheduling inconvenience, not a data risk). Disk ~0.5–1.5 GB (dominated by the unconditional median-run `Figure_F*_D*_Run#N.csv` per cell). Memory is a non-issue at D≤20.

### 1.2 — Interruption/resume protocol (owner: author; effort: trivial)

On sleep/crash/stop: **re-issue the identical command**. Resume is keyed on (function, dimension, run, seed) against `per_run.csv` (`run_experiment.py:1424-1434`), flushed after every cell (`:1695`); maximum loss = the in-flight cell (worst ~17 min). **Never** add `--overwrite`; never run a second `run.py` against `results/_run_all` while one writes; if the console reports repeated pool rebuilds (built-in recovery, `:1598-1655`), note it for the QA record and let it finish. If an interruption forces a code change mid-campaign: stop, record a deviation, re-run the affected algorithms entirely at the new commit.

### 1.3 — Prohibitions during the window

Do not invoke `scripts/run_all_cec2020.py` (even after 0.7's neutralization, prefer the direct command). Do not run `configs/baselines_cec2020.yml` — fresh external CEC2020 banks after the externals-out decision would manufacture new undisclosed public comparisons.

### 1.4 — [PARALLEL] Agent work during the compute window

Close 0.8–0.12 if still open; build the promotion tool (2.4); build the `phase6b` skeleton (3.1); run the LSGO pairing audit (2.5); draft S7 protocol prose and the Phase 4 claims surgery (nothing binding numbers).

### 1.5 — Post-run completeness verification (owner: agent writes ~40-line read-only script, author runs; effort: small; blocking)

Assert over `results/_run_all/<alg>/cec2020/` for all seven algorithms: (1) `per_run.csv` exactly 1,140 rows/alg, 7,980 total; (2) exactly 30 runs per cell, no duplicate (function,dimension,run) keys; (3) **zero** rows for (F6,D5)/(F7,D5); (4) every row `nfes` equals its dimension budget and `termination == 'max_evaluations'`; (5) `best_fitness` and `error` finite, `error >= 0`; (6) seeds match `seed_schedule.csv` and `get_cec_seed(20240620, dim, func, run)` (`seed_policy.py:31-38`), **identical across the 7 algorithms per (dim,func,run)** and injective within each — this is the paired-design guarantee; (7) **no** `skipped_runs.csv` in any cec2020 summary dir; (8) five provenance files per bank; (9) `environment.json` `git_commit` identical across all 7 banks and equal to the 0.6 pinned commit; (10) four summary tables per alg (`<alg>_cec2020_D{5,10,15,20}.csv`, 8/10/10/10 functions).

### 1.6 — BUG-RESUME-01 heritage audit (owner: agent; effort: small; blocking)

Recompute Best/Median/Mean/Worst/SD per (dim, function) from `per_run.csv` and compare to the summary tables: Best/Median/Worst exact; Mean/SD within rel 1e-8 (the 0C-3 precedent tolerance — resumed sessions summarize from `%.10e`-rounded values; pre-declare the tolerance so a habitual exact-match standard doesn't fail correct data). Record pass/fail per algorithm; only if a cell exceeds tolerance, regenerate that summary from `per_run.csv` and document the deviation — never silently rewrite.

---

## PHASE 2 — Evidence promotion: two separate immutable releases

**Objective:** promote the LSGO family banks (available now) and the CEC2020 banks (after Phase 1) into two non-superseding underscore-prefixed releases beside — never inside — the frozen primary.

**Entry (LSGO half):** 0.8 forensics closed clean; 0.10 hygiene green; 0.11 guard in place. **Entry (CEC2020 half):** Phase 1 exit.
**Exit:** both releases minted and digest-verified; `check_manifest --strict-inventory` green on the primary **and** both new manifests; `validate_provenance_claims.py --self-test` confirms the primary is not reclassified; documented-but-unpromoted package (2.8) complete.

### 2.1 — Release architecture (settled; no conflict)

Two releases: `lsgo-rel-<date>-<anchor9>` under `benchmarks/cec_reference_results/_cec2013lsgo/` and `cec2020-rel-<date>-<anchor9>` under `.../_cec2020/`. Ids deliberately do **not** match the glob `rel-*` — `validate_provenance_claims.py` builds its superseded set from `(papers/analysis).glob('rel-*')` (`:148-155`); a `rel-*` name would reclassify the primary as superseded. `supersedes_release: null` in both. Rationale for two, not one: LSGO is promotable today while CEC2020 does not yet exist; a combined release either blocks LSGO for weeks or forces a re-mint violating release-id immutability; the `_ablation/` precedent already establishes one manifest per evidence body.

### 2.2 — LSGO staging-ledger closure (owner: either; effort: folded into 0.8; blocking for 2.6)

Confirm on record: prebugfix adjudication finding (0.8), `skipped_runs.csv` disposition per ruling R5 (author ratifies), six-commit code-identity attestation (0.8), and the `production_deviation_record.md` entries for all three.

### 2.3 — Pairing audits (owner: agent; effort: small each; block every paired statistic)

`seed_and_pairing_audit.md:67` currently places cec2013lsgo **outside** the pairing framework (text refers to the old imported reference summaries). Replicate the audit's Sections 1–4 over the native banks: (a) **LSGO now** — 7 algs × 15 funcs × 25 runs: recompute `get_cec_seed`, verify injectivity, shared runner-generated X0, identical function sets, 0 mismatches; (b) **CEC2020 after Phase 1** — same over 38 cells × 30 runs. Publish both as audit addenda.

### 2.4 — Build `papers/scripts/promote_suite.py` (owner: agent; effort: medium; blocking)

One generic, suite-parameterized promotion tool; `phase_P2`/`phase_P6` untouched. It: stages cells from `results/_run_all/<alg>/<suite>/` into the underscore tree; whitelists exactly the Section-11 file classes of the pre-registration (per_run, per-dim summaries, five provenance files, seed_schedule, gen_logs); **excludes** `curves/` (~360 MB, ruling A-11 — exclusion recorded in-manifest), runner `.txt` logs, and every `*.prebugfix`; promotes dt-gsk's `skipped_runs.csv` under the explicit `deviation_record` class (R5); enforces per_run row counts (LSGO 375 = 325@D1000 + 50@D905; CEC2020 1,140 protocol-aware — never a naive 40×30); refuses to run if the target tree already holds a manifest; writes manifests LF + indent-2 + trailing newline (the in-tree `_ablation` convention — CRLF/2-space belongs only to the three `papers/governance` freeze manifests).

### 2.5 — Manifest field spec (both releases)

Beyond the frozen schema: `evidence_root` (the `_ablation` manifest lacks one and is invisible to `check_manifest --manifest`; deliberate improvement), `preregistration` (hash from 0.3), `per_cell_run_commit`, curve-exclusion record with rationale, and per-suite fields — LSGO: schema `lsgo_evidence_manifest/v1`, `objective_variant: ackley_transformed`, `endpoint_column: best_fitness`, `statistics_basis: raw_objective`, `runs: 25`; CEC2020: schema `cec2020_evidence_manifest/v1`, `statistics_basis: error`, `runs: 30`, budget map, `protocol_cells: 38` with (F6,D5)/(F7,D5) explicitly recorded as undefined. CEC2020 `verification.json` entries without a reference table report `NOT_VERIFIED/NO_REFERENCE` (the 0D-2 lesson); optionally (author decision A10) wire AGSK's published Mohamed et al. 2020 tables as a real reference for the one algorithm that has them.

### 2.6 — Mint `lsgo-rel-*` (owner: either; effort: medium; can complete **during** Phase 1)

Promote the **seven family cells only** — externals are never promoted (2.8). Post-mint gates: `check_manifest --manifest _cec2013lsgo/manifest.json` green; `--strict-inventory` on the primary still 3403/3403 zero-unlisted; `validate_provenance_claims.py --self-test`. Update the `_index/BENCHMARK_EVIDENCE_INDEX.md` §0 ledger; add 7 `data_ledger.csv` rows carrying `evidence_release_id lsgo-rel-*`.

### 2.7 — Mint `cec2020-rel-*` (owner: either; effort: medium; after 1.6)

Same path, same gates, same ledger updates.

### 2.8 — [HARD-HONESTY] External LSGO banks: documented-but-unpromoted (owner: agent; effort: small; blocking for submission)

Ruling (evidence-governance + adversarial, aligned): (a) do **not** promote the three native external banks (`results/_run_all/{shade-ils,mos-cec2013lsgo,decc-g}/cec2013lsgo`, 375/375 each, git-tracked and public) — a "context release" of an unfavorable comparison reads as prepared-then-buried; (b) do **not** delete or untrack them — removing public unfavorable data is the one move worse than either alternative; (c) formalize their status: an `_index` section listing paths, completeness, provenance, an explicit out-of-paper-scope declaration citing CR-0019, and the honest one-line direction of the informal result — *"an informal all-native Friedman places the two LSGO specialists (SHADE-ILS 1.600, MOS 2.467) decisively ahead of every family member (best family rank: DT-GSK 5.133)"*; (d) complete the two `data_ledger.csv` rows currently MISSING/PENDING-RELEASE-ID and add shade-ils, all marked `source_type context / comparability out-of-scope / evidence_release_id "none (unpromoted, CR-0019)"`; (e) a status README beside the banks; (f) the paper-side sentences of 0.4 point readers at the repository **before** a reviewer runs `ls`.

---

## PHASE 3 — Formal statistics

**Objective:** compute, for the first time, the confirmatory layers of both new suites exactly as pre-registered, from promoted releases only.

**Entry:** Phase 2 exit (both releases); 2.3 pairing audits green; 0.5 byte-guard baseline in place.
**Exit:** both analysis bundles complete under `papers/analysis/lsgo-rel-*/` and `papers/analysis/cec2020-rel-*/`; byte-guard re-check green; registries wired; exhibit fragments generated.

### 3.1 — Build `papers/scripts/phase6b_run_analysis_newsuites.py` (owner: agent; effort: large; blocking; skeleton buildable during Phase 1)

Per ruling R3. Reuse `statistics.py` primitives untouched: `friedman_rank` (M-026, `:650-766`), `holm_correction` (`:462`), `wilcoxon_paired` (`:304`, method string `normal_approx_continuity` as recorded at `phase6_run_analysis.py:428`). Add: exact sign-flip enumeration for across-function tests (n = 8/10/15; 2^15 trivial); the seeded permutation-Friedman companion (Section 4 seeds); Nemenyi parameterized by k with an assertion (phase6's k=7/q=2.949 hardcode is a silent wrong-direction error if panel size changes); the exact-Wilcoxon docstring/code contradiction (`statistics.py:332-334` vs `:379-398`) resolved by the addendum's per-row method recording. Mirror phase6 determinism: C-locale, `%.6e`, fixed sort orders, no timestamps. Hardcode PANEL/COMPARATORS identical to `phase6:84-86`; `SUITE_DIMS {'cec2020':[5,10,15,20],'cec2013lsgo':[native 1000/905]}`; CEC2020 D5 function list [1,2,3,4,5,8,9,10]; suite ordinals 2020/2113; two-summary-CSV loader for the LSGO D1000/D905 split. Runs only in strict-source mode (`GSK_STRICT_SOURCE=1`) against the Phase 2 releases; **cannot write into any `rel-2026-07-20` path**. Extend the orphan check to audit both `statistical_results.csv` files against the frozen `analysis_registry.csv` (81 lines, never edited) **plus** a new addendum registry file.

### 3.2 — Execute the confirmatory batteries (owner: agent; effort: medium)

(a) **LSGO decisive layer:** AN-PWRUN-LSGO-NATIVE (25 paired runs, Holm m=15 per comparator) + AN-EFF-LSGO-NATIVE — the only analysis that can support or refute the 3.133/3.133 tie; the pre-committed wording of addendum Section 9 binds the outcome either way. Plus AN-OMNI/AN-PW-LSGO-NATIVE at their disclosed tiers. (b) **Full CEC2020 battery:** all AN-\*-2020-\* families; expect heavy exact-zero cells at low dims — report n_eff after zero-discard, use the SAP Section 7 degenerate-cell strings verbatim, let M-026 absorb tied blocks. (c) Robustness: AN-ROB-2020 and AN-ROB-LSGO as registered — the mandatory median-basis re-rank (`performance.tex:548-560` makes it mandatory for every rank statement; the LSGO family order is already known **not** to be fully robust under it and must be reported as such). (d) Immediately re-run the 0.5 byte-guard and `validate_provenance_claims.py --self-test`.

### 3.3 — Registry and matrix wiring (owner: agent; effort: medium)

Register all new AN ids (addendum registry; LSGO descriptives at their disclosed tier); flip the 0.3 PENDING claims rows to READY with bound evidence ids; regenerate `artifact_binding.csv` **passing `GSK_REL_ID` explicitly per release** (`generate_artifact_binding.py` defaults to the stale `rel-2026-07-16-78f075cb0`; grep all governance CSVs for the stale id afterwards); new rows in `requirements_traceability_matrix.csv`, `experiment_matrix.csv`, `table_figure_source_map.csv`; `benchmark_protocol_audit.md` §6.2 rows for both suites (correcting part2:120's "(context) not used by the primary panel" mislabel of the 3e6 budget).

### 3.4 — Exhibit fragment generation (owner: agent; effort: medium)

Clone `generate_cec2013_pairwise.py` / `gen_wilcoxon_cec2011|cec2013` patterns (`generate_latex_tables.py:421/450`): CEC2020 per-dimension rank tables (D5-asymmetry + budget footnotes), Wilcoxon/Holm tables, W/T/L; LSGO native tables; `generate_nemenyi_cd.py` calls **only** for families whose omnibus is significant (pre-registered display condition — with CD 2.85–3.19 expect "CD diagram omitted" cells, and say so); `lsgo_ranks` / `cec2020_mean_ranks` figures via the `generate_rank_charts.py` pattern. All fragments read **only** the new underscore releases, never `results/` staging. Six-point registration completes in Phase 5.4.

---

## PHASE 4 — Manuscript surgery (main text)

**Objective:** rewrite the main text to the new scope with every claim bound to pipeline output, both branches specified.

**Entry:** Phase 3 exit (numbers exist); Gate 0 ruled; 0.9 citation keys admitted; 0.4 sentences approved.
**Exit:** all ~35 shared scope sites (plus 14 drop-branch sites if DROP) rewritten; claims matrix consistent; disclosure sentences placed; no templated placeholder remains.

**Ordering rule:** claims-matrix surgery (4.1) strictly first — three existing rows currently make **any** LSGO sentence a governance violation.

### 4.1 — Claims-matrix surgery (owner: agent; effort: medium; blocking everything below)

Repair the rows broken in **both** branches: LM-05 (row 43: "Evidence tops out at D=100… no LSGO claim is made"; blocked "Any LSGO or n~1000 claim"), MT-08 (row 15 blocked "LSGO claim"), IN-01 (row 36 blocked "any LSGO claim" + "Extrapolation beyond D=100") — re-scope the prohibitions to extrapolation beyond *tested* dimensions. New rows: PR-07 (LSGO protocol incl. transformed-Ackley disclosure), PR-08 (CEC2020 protocol, 38 cells), RS-12 (LSGO family-internal standing; blocked: any MOS/DECC-G comparison on F3/F6/F10, any published-value comparison presented as comparable, any "competitive at D=1000" without a supporting test), RS-13 + LM-07 (from 0.3, now READY), LM-06 (repo-bank disclosure), IN-04 (tiering thesis vs the D=1000 finding). Unchanged: RS-01 (2.48), LM-03, BG-05; AB-02 kept in both branches.

### 4.2 — Section 4.1 protocol + heterogeneity + page budget (owner: agent; effort: medium)

(a) Transpose `tab:protocol` (`performance.tex:85-98`) to suite-per-row (5(/4) rows × problems/dims/runs/MaxFES/endpoint columns; shared seed/pairing block below). (b) Add the heterogeneity-and-pooling paragraph: runs 51/[51]/25/30/25; error vs raw bases; budget conventions (10^4·D vs 150k vs 50k–10M vs 3e6); the absolute no-pooling rule; AN-RANKAGG-2017-OVERALL stays CEC2017-only. (c) Extend the evidence taxonomy (`performance.tex:107-112`) to four categories: development (CEC2017), corroborative (CEC2011[, CEC2013]), **pre-registered confirmatory** (CEC2020 — name it as the paper's strongest methodological card, citing the 0.3 commit), post-hoc exploratory (LSGO). (d) Update `proposed_algorithm.tex:813` budget enumeration. (e) Rescope the early-stop tally (`performance.tex:173-175`) explicitly to the primary release. (f) **Page budget** (41pp vs 40pp cap): new subsections 4.5 LSGO + 4.6 CEC2020 (~0.75pp prose + ONE table each: T17 LSGO family Friedman + scope sentence; T18 CEC2020 per-dimension Friedman). Harvest in priority order: `fig:conv-cec2017-d30` (`:776-793`) → S3 (~−1pp); `tab:runtime` (`:842-866`) → prose (~−0.4pp); [KEEP] `tab:friedman-cec2013` (`:667-693`) → S2.3 keeping the two-sentence summary (~−0.5pp). If still over in KEEP: harvest the second convergence figure or CR the cap (author decision A8) — never cut disclosure prose.

### 4.3 — Synthesis, abstract, introduction, conclusions, cover letter (owner: agent; effort: medium)

Headline (`performance.tex:953-974`) recomputed by the addendum Section 9 template — strict-first count over per-suite descriptive standings, ties reported as tied-first, never absorbed; counts filled **only** from Phase 3 output. Abstract (`main.tex:148-174`): 2.48 stays the ONE bound number, CEC2017-fenced; suite enumeration at 159–161/166 rewritten; at most one qualitative sentence per new suite (LSGO sentence written only after 3.2(a) exists; CEC2020 from the wording bank). Introduction: C3 bullet (`introduction.tex:129-144`) + roadmap (`157-159`). Conclusions: findings paragraph extended with unfavorable cells stated first-class; limitation `conclusions.tex:83` rewritten (evidence ceiling now D=1000, caveated to the LSGO protocol); `89-93` external sentence → sentence 0.4(b) + LM-06; future work `125-133` (D=100-ceiling motivation stale — INT-11: report the D=1000 standing as **consistent with** the S6.5 ISM null, never as a new measured isolation; isolation evidence explicitly stops at D≤100; no ISM/eigenframe attribution at D=1000 in either direction). Cover letter (`cover_letter.tex:55`): new suite count + LSGO honesty clause, bound by CL-01/CL-02. Related work (`related_work.tex:56-59, 65-69, 154-162, 288-291`): defuse the boomerang **before results are known** — reframe the AGSK/APGSK "regime-limited" critique as "their published evidence is confined to that regime; we now evaluate the whole family at home and away, including that regime."

### 4.4 — False-sentence sweep (owner: agent; effort: large)

Complete file:line checklist (both branches): `main.tex:159-161, 166, 213-227, 261-270, 273-274, 289`; `introduction.tex:134-137, 157-159`; `performance.tex:9, 70-74, 85-98, 103-116, 173-175, 649-725 [branch-dependent], 747-749, 832-834, 880-882, 953-974`; `conclusions.tex:50-57, 71-73, 83, 89-93, 125-133`; `proposed_algorithm.tex:813`; `supplementary.tex:119-138, 175-190, 1829-1836 [add companion sentence naming the new releases; "21 (suite,optimizer) cells" stays true of the primary], 1879 [reworded — currently literally false]`; `cover_letter.tex:55`. Data Availability (`main.tex:261-270`) enumerates **four** release ids — primary (verbatim, unchanged), `abl-rel-2026-07-20`, `lsgo-rel-*`, `cec2020-rel-*` — reusing the "distinct from — and held separately in the repository from — the primary evidence release" pattern already validated at `supplementary.tex:~1904-1917`. Every new empirical sentence carries a BIND comment to an AN id minted in Phase 3 (never invented in prose); verify with `phase_08/audit_manuscript.py validate_bind_token` using **explicit** ids (the compact-expansion regex can't parse 2013LSGO infixes or non-10/30/50/100 dims). Title: unchanged in both branches. Author all LaTeX with Write/Edit, never a bash heredoc (the literal-"oindent" incident).

### 4.5 — [HARD-HONESTY] Disclosure placement (owner: agent; effort: trivial; sentences verbatim from 0.4)

(a) in the LSGO main-text subsection; (b) in conclusions; (c) in Data Availability and supplement S5; [DROP] the rationale sentence in Data Availability. These survive every harvest.

### 4.6 — [KEEP] branch delta (owner: agent; effort: small)

`performance.tex:959` recounted arithmetically over five suites (numerator from Phase 3 only); SA03 and AN-\*-2013 ids untouched; "CEC2013 (bound-constrained)" vs "CEC2013LSGO" disambiguation applied everywhere (two suites named CEC2013 otherwise collide); `tab:friedman-cec2013` harvested to S2.3 per 4.2(f).

### 4.7-D — [DROP] branch delta (owner: agent; effort: large)

Execute the full excision of Gate 0's DROP column: delete subsection 4.4 + SA03 + supplement S2.3/S3.3 (S2.4–S2.6 auto-renumber verified safe — only S6.x is hard-coded anywhere); retire PR-03/RS-11 by status `RETIRED_SCOPE` with date; rewrite the headline and every AN-\*-2013 citation; recount the early-stop tally CEC2017-only (recount from released banks, no rerun); keep S6.5's CEC2013-D50 cells and add a local one-paragraph CEC2013 protocol note inside S6; re-check LM-01 so the D30 concession reads correctly with CEC2017 alone; the mandatory Data Availability rationale sentence (0.4); evidence tree untouched (the release legitimately remains a superset of the paper); parity/count snapshots shrink — reconcile in Phase 6.

---

## PHASE 5 — Supplement construction (S7, S8) and cross-format plumbing

**Objective:** build the two new supplement sections and wire every exhibit through the dual-format chain.

**Entry:** Phase 3 fragments exist; Phase 4 main-text state stable.
**Exit:** S7/S8 complete; `\supplementary{}` block S1..S8; M-003 and no_ablation_scan green; word_sources/parity rows regenerated.

### 5.1 — S7: CEC2013LSGO (owner: agent; effort: large)

Append `\section` after `supplementary.tex:2286ff` — **never renumber S1–S6, never insert before S6.5/S6.6/S6.7** (hard-coded at `main.tex:227`, `introduction.tex:147`, `performance.tex:831-834/925-927`, `conclusions.tex:104`). Contents: (1) protocol statement incl. transformed-Ackley + explicit not-comparable-to-published-MOS/DECC-G statement + **post-hoc protocol disclosure in those words** (per 1.5.0-M(f)); (2) per-function 7-algorithm mean±SD as two portrait half-tables (F1–F8 | F9–F15) — the zero-landscape mandate holds (1.5.0-K); (3) family Friedman table + `lsgo_ranks` figure, at the descriptive-after-inspection tier with the Section-6 disclosure; (4) the **new** paired Wilcoxon+Holm matrix (the confirmatory layer); (5) rank-biserial/A12 + W/T/L; (6) the honesty block: the repository's complete external banks, the informal direction (specialists decisively ahead), family-internal scope and why. Add the companion release-id sentence at `supplementary.tex:1829-1833`.

### 5.2 — S8: CEC2020 (owner: agent; effort: large)

Populate the 0.3 skeleton: (1) protocol statement (38 cells, runs=30 per Yue et al. §2.1, budgets, error basis, F1/F8 D5/D15 restoration note pinned by `tests/regression/test_cec2020_restored_cells.py`); (2) per-dimension mean±SD as two portrait pairs (D5|D10, D15|D20); (3) Friedman per dimension + descriptive overall column (tab:friedman-cec2017 convention) + Nemenyi where significant; (4) Wilcoxon+Holm matrices per dimension; (5) **the pre-registered framing paragraphs verbatim** — AGSK home-suite disclosure and scaffold-tier interpretation, so the framing provably predates the data; (6) convergence optional — if included, prespecify the dimension before rendering (S3 frozen-selection precedent).

### 5.3 — `\supplementary{}` block and gate discipline (owner: agent; effort: small)

`main.tex:213-227` → S1..S8 ([DROP]: also revise the S2/S3 clauses); `validate_document_consistency.py:100-122` (M-003) requires contiguous S1..SN matching actual sections — both files change in the same pass. **Reflow discipline:** after every `\supplementary{}` touch, rebuild the main PDF and run no_ablation_scan **first** — no line in the main PDF may begin with "S6" (`main.tex:210-212`). Update the supplement abstract (`supplementary.tex:119-138`) and shared protocol block (`175-190`); supplement grows ~10–16pp → ~70–80pp (unconstrained by B1).

### 5.4 — Six-point exhibit registration + cross-format regeneration (owner: agent; effort: medium; atomic)

For every new exhibit: (1) `build_docx.py:1250` `_RESULTS_TEX_IDS` gains every new main-text T-id (T17, T18) — omission makes the DOCX silently render a raw word_sources dump (ruling A-9; no gate names it); (2) `generate_word_sources.py` TABLES dict; (3) `generate_latex_tables.py`; (4) `generate_artifact_binding.py` table_spec with explicit `GSK_REL_ID`; (5) `_paper_tables` provenance chain; (6) `artifact_binding.csv` rows (`validate_artifact_labels` resolves every label). Layout law: portrait only; real `table`+`tabular` envs (never bare longtable — `build_docx:437` walks table envs only); zero `\texttt`; overfull hbox ≤ 2.0 pt; captions_registry entries; DOCX figure variants (`*.docx.png`); parity rows regenerated.

---

## PHASE 6 — Build, gates, governance layers

**Objective:** two consecutive identical green sweeps of the full gate battery at the correct epochs.

**Entry:** Phases 4–5 exit.
**Exit:** all gates green twice; all four artifacts byte-identical across double builds; count snapshots reconciled; adversarial re-sweep clean.

### 6.1 — Build chain (owner: agent; effort: medium)

Order: table/figure generators → `generate_word_sources` → `build_supplementary.py` → `build_pdf.py` (self-gates `validate_build_hygiene --logs-only`) → `build_docx.py` and `build_docx.py --supplementary` → cover letter. **Epoch discipline:** PDF `SOURCE_DATE_EPOCH=1783468800` + `FORCE_SOURCE_DATE=1`; DOCX `SOURCE_DATE_EPOCH=1783641600` set **explicitly in the DOCX shell** (a persisted PDF-epoch variable yields a non-reproducible DOCX that still passes every gate); hash-compare both DOCX artifacts **twice** before trusting `check_manifest`.

### 6.2 — Gate sweep (owner: agent; effort: medium)

`validate_build_hygiene` (full) → `validate_cross_format_parity` (**no_ablation_scan first**; regenerates `cross_format_consistency.csv` — row count moves off the ~599/615 snapshot family; update ALL disagreeing snapshots in the same pass: freeze manifest, PAPER_REVIEW_PROMPT §1.5 ×2 + §1.5.6, PAPER_BUILD_PROMPT §15.0) → `validate_docx` → `validate_document_consistency` (**expected terminal exit 2** = author-pending; not red) → `validate_evidence_bindings` (every changed count is a dual-format obligation; M-029 precedent was 20 failures) → `validate_citation_controls` (61-key corpus) → `validate_artifact_labels` → `validate_provenance_claims --self-test` → `validate_runtime_provenance` → `check_manifest` (N/15 until Phase 7 re-mint, then N/N + `--strict-inventory` over primary + both new manifests) → the 0.5 byte-guard once more.

### 6.3 — [HARD-HONESTY] Adversarial re-sweep (owner: agent; effort: medium; blocking)

Grep the built manuscript for prohibited wordings: "leads at D=1000", "competitive" (unsupported), [DROP] "first overall on … CEC2013", un-scoped "three suites", any MOS/SHADE-ILS/DECC-G **number from our banks** in a table or claim, any LSGO comparative not scoped "within the GSK family", any F4/F8 win without the F7/F15 lasts. Verify: abstract carries exactly one bound number and it is CEC2017-scoped; the AGSK adjacency disclosure appears wherever CEC2020 results are interpreted; the three 0.4 sentences are present verbatim; claims matrix has a row for every CEC2020/LSGO sentence; D5's 8-block count is stated wherever CEC2020 Friedman appears.

### 6.4 — Governance doc closure (owner: agent; effort: small)

1.5.0-N populated variables (§1.5.1: EMPIRICAL_SCOPE rewritten to the executed scope, page/word counts re-measured, release-id table extended to four ids); PAPER_BUILD_PROMPT: §2.2 corpus 57→61, §4.2/4.3 expected inventory, §15.0 parity snapshot, Appendix A/B.4; `captions_registry.md`; the [DROP] `cross_format_consistency.csv` reconciliation if applicable.

---

## PHASE 7 — Re-freeze, freeze statement, tag

**Objective:** re-freeze the manuscript state, write the first freeze pass in project history that owns changed numbers, and tag v2.0.

**Entry:** Phase 6 exit (two identical green sweeps).
**Exit:** tag `dtgsk-submission-v2.0-<date>` pushed at the freeze anchor; all manifests verified.

1. **(agent)** Byte-surgically re-mint `papers/governance/main_manuscript_freeze_manifest.json`: CRLF + 2-space indent; update **both** `sha256` and `bytes` per file (`check_manifest.py:70-77` gates both); read/write **bytes**, never `sed -i` or `read_text()/write_text()` (they normalize EOLs and break every hash); preserve each file's own trailing-byte convention (reproducibility + primary-freeze end with a trailing CRLF newline; main-manuscript + submission-package do not).
2. **(agent)** Append **freeze pass 24** — unlike all 23 predecessors it must NOT claim "no reported number changed". It records: the re-opening and CR-0019/CR-0020 authority; the Gate 0 outcome; the two new release ids and their pre-registration hash; the externals-out decision **with** the public-banks disclosure posture; the actual CEC2020 and LSGO results, favorable or not; both build epochs. `scientific_content_status` transitions out of and back into a frozen value; `validator_outputs_at_freeze` rewritten wholesale from the Phase 6 sweep.
3. **(agent)** Update `reproducibility_manifest.json` + `submission_package_manifest.json` naming all four releases without dropping the primary id; bump `manuscript_version_id`; close `_pending_refreeze.json` against its exit criteria; return phase-gate rows to FROZEN with fresh evidence.
4. **(either)** Reconcile the three authorities to ONE commit: freeze-manifest `anchor_commit` == submission-package commit == the commit the tag resolves to (the v1.0 state had three different "authoritative" commits cross-checked by no gate).
5. **(agent)** Final `check_manifest` N/N + `--strict-inventory` green on every manifest; `validate_docx`; double-build verification once more.
6. **(author)** Commit, tag `dtgsk-submission-v2.0-<date>` at exactly the anchor commit (ruling R4), retain v1.0 as historical (recorded as superseded in the freeze statement; never deleted or moved), push branch + tag; verify `git ls-remote --tags` shows the tag at the anchor.

---

## PHASE 8 — Author-side post-tag checklist (in order)

1. Confirm the pushed tag resolves to the freeze anchor.
2. Cut a **GitHub Release from the v2.0 tag** so the Zenodo integration mints a **new DOI version** (COMP-001b). Never re-point the existing DOI. No manuscript rebuild is needed (AG-0006/R-0004: the manuscript deliberately prints no identifier; locators are supplied with the submission).
3. Record the DOI in governance, not in any `.tex`.
4. SuSy submission (per AG-0006, account `moustafa.masoud@gmail.com`): MDPI Algorithms / Article; abstract + keywords pasted from the rebuilt `main.tex`; upload DT-GSK.pdf, DT-GSK.docx, supplementary.pdf/.docx, cover_letter.pdf; mailing address + telephone entered directly in the portal (deliberately not in the public repo); APC with personal invoice, affiliation unchanged (Giza 12613); repository URL + new DOI in the data-availability fields; **never fabricate reviewer names, DOIs, or journal metrics** in the suggested-reviewer fields.

---

## Risk register (severity-ordered, deduplicated across lenses)

| # | Sev | Risk | Mitigation (task) |
|---|---|---|---|
| 1 | CRITICAL | End-to-end `finalize_evidence.py` run re-mints the primary (P6 new id at `:1118-1121`), absorbs stray files (drift guard `:1091-1109` checks old files only), voids `rel-2026-07-20-67d9345f9` cited at ten sites | 0.10 hygiene first; 0.11 executable abort guard; all promotion via `promote_suite.py`; strict-inventory at every phase boundary |
| 2 | CRITICAL | Campaign launches before the pre-registration commit — the only genuine pre-outcome moment, on AGSK's home suite, is destroyed forever | 0.3 is a hard ordering gate; commit hash logged; manifests bind the hash |
| 3 | CRITICAL | `.prebugfix` forensics finds the defect touched the four pre-fix LSGO banks → the six-comparator ranking under the tie claim is invalid | 0.8 blocking closure with recorded finding either way; NO-GO for the LSGO leg until resolved; author decision A7 on the re-run |
| 4 | CRITICAL | Public adverse external banks (shade-ils 1.600 / mos 2.467 vs dt-gsk 5.133) + family-only paper with no acknowledgment = concealment discoverable in one `ls`; retroactively discredits the ISM null and eGSK-loss honesty record | 0.4 sentences (HARD) + 2.8 documented-but-unpromoted package + 5.1(6) honesty block + 6.3 re-sweep |
| 5 | CRITICAL | Regeneration/absorption of frozen analysis outputs breaks the abstract's 2.48, the parity table, the verbatim release id (phase6's stale default rel id makes a bare invocation live) | 0.5 byte-guard after every phase; R3 separate driver; phase6 never invoked without explicit env overrides |
| 6 | HIGH | `run_all_cec2020.py`/`agsk_cec2020.yml` injects reference-policy seeds into the AGSK bank → mixed-schedule rows silently break the paired design | 0.7 neutralization; R2 single command; 1.5 check (6) catches contamination after the fact |
| 7 | HIGH | Campaign spans multiple commits / dirty tree (LSGO precedent: six commits + mid-window acceleration) | 0.6 single pinned commit; 1.5 check (9); mid-campaign code change ⇒ stop, deviation, full re-run of affected algorithms |
| 8 | HIGH | Numba cache poisoning (suite files restored by copy 2026-07-26; the 2026-07-27 incident faked 7/42 pin failures) | 0.6 purge + 42/42 pins before launch and after any future suite-file copy |
| 9 | HIGH | DOCX epoch trap: persisted PDF epoch → non-reproducible DOCX that passes every gate | 6.1 explicit epochs; double-build hash compare ×2; both epochs in pass 24 |
| 10 | HIGH | Manifest byte-convention corruption (CRLF/2-space, per-file trailing bytes; `sed`/`read_text` normalize and break all hashes while JSON parses green) | 7.1 byte-surgical edits only; `check_manifest` immediately after each manifest touch; new manifests written only by `promote_suite.py` |
| 11 | HIGH | Page/word budget collision (41pp vs 40pp cap; 197/200-word abstract; two suites of new prose) | 4.2(f) harvest ledger; CR raising the cap (A8) rather than cutting disclosure prose; [DROP] frees ~1.2pp |
| 12 | HIGH | LSGO suite-definition PDF unobtainable → suite cannot be cited → LSGO leg blocked | 0.9 starts hour 1; fallback: LSGO deferred-with-disclosure while CEC2020 proceeds |
| 13 | HIGH | LSGO overclaim: tie + p=0.0372 + egsk-only separation supports only the descriptive ceiling; formal unrounded pipeline could flip the informal tie | Addendum §9 claim ladder pre-committed; confirmatory weight only on the never-run paired layer; 6.3 wording grep |
| 14 | HIGH | Cross-suite heterogeneity attack (51/25/30/25 runs, error-vs-raw, budget regimes) | Addendum §8 absolute pooling ban; 4.2 heterogeneity paragraph + four-category taxonomy; headline = descriptive per-suite count only |
| 15 | MEDIUM | Wall-time underestimate (dt-gsk probe rate above model; JIT overhead) → 20–30 h stretches toward 40 h | Tranche split; D20 overnight; resume-safe — scheduling risk only |
| 16 | MEDIUM | CR-0012 resumed-session Mean/SD drift fails a habitual exact-match audit | 1.6 pre-declared rel 1e-8 tolerance (0C-3 precedent), exact only for Best/Median/Worst |
| 17 | MEDIUM | Promotion debris: `.prebugfix` siblings, stale `skipped_runs.csv`, runner `.txt` logs ride into an immutable tree | 2.4 whitelist + explicit exclusions + `deviation_record` class (R5); strict-inventory before/after each mint |
| 18 | MEDIUM | `rel-*` glob trap: an analysis bundle named `rel-*` reclassifies the primary as superseded (`validate_provenance_claims.py:155`) | Bundle names `lsgo-rel-*`/`cec2020-rel-*`; `--self-test` immediately after each bundle dir is created |
| 19 | MEDIUM | Stale default release ids in generators (`generate_artifact_binding.py` → `rel-2026-07-16-78f075cb0`) bind new artifacts to a dead release | 3.3 explicit `GSK_REL_ID` per invocation + post-regeneration grep |
| 20 | MEDIUM | New T-id missing from `_RESULTS_TEX_IDS` → DOCX silently diverges from PDF; no gate names it | 5.4 atomic six-point registration; parity + `validate_docx` right after first DOCX build |
| 21 | MEDIUM | `\supplementary{}` reflow pushes "S6" to a line start (no_ablation_scan); M-003 contiguity break | 5.3 edit→rebuild→scan-first discipline; both files in one pass; append-only sections |
| 22 | MEDIUM | [DROP] optics: cited release ships CEC2013 banks; public v1.0 tag claims first-overall on it | 0.4 [DROP] rationale sentence (vetoed if absent); rows retired by status, never deleted |
| 23 | MEDIUM | ISM-null scope creep to D=1000; stale "D=100 evidence ceiling" sentence (`conclusions.tex:127-129`) | 4.3 consistency framing; isolation scope explicit |
| 24 | MEDIUM | Governance self-contradiction: 1.5.0-M(i) mandates the external context the new scope removes | 0.2(3) 1.5.0-N supersession **before** any manuscript edit + CR-0019 + comparability/data-ledger re-adjudication |
| 25 | LOW | Gate-status misreads (validate_document_consistency exit 2 is expected; five historical parity-count snapshots disagree) | 6.2 documents expected exit codes; all snapshots updated in one pass |
| 26 | LOW | Vacuous CONSISTENT verification verdicts on CEC2020 (no reference tables for 6/7 algorithms) | 2.5 `NOT_VERIFIED/NO_REFERENCE`; optional AGSK published-table wiring (A10) |
| 27 | LOW | [DROP] S6.5 references a suite the paper no longer defines | 4.7-D local protocol note inside S6; AB-02 unchanged |

---

## Decisions ONLY the author can make

- **A1 — Gate 0:** keep or drop CEC2013 (recommendation: KEEP, ruling R1). Wording-blocking only; does not delay the campaign.
- **A2 — Sign and commit the pre-registration** (0.3). The commit timestamp is the evidence; hard expiry at first run.
- **A3 — Approve the three disclosure sentences + wording bank verbatim** (0.4). Adversarial-veto items.
- **A4 — Launch the campaign and drive resume decisions** (1.1/1.2). Agent never launches.
- **A5 — Disposition of `scripts/run_all_cec2020.py`** (0.7): repoint vs guard vs delete.
- **A6 — Supply the four citation PDFs** and ratify the corpus admissions (0.9/R8) — the LSGO suite-definition PDF is the schedule long pole.
- **A7 — If 0.8 finds pre-fix contamination:** authorize the >100 h LSGO re-run, or drop the LSGO leg to deferred-with-disclosure.
- **A8 — Page-cap CR** if the KEEP branch still exceeds 40pp after the full harvest.
- **A9 — Ratify the `skipped_runs.csv` `deviation_record` promotion** (ruling R5).
- **A10 — Optional:** wire AGSK's published Mohamed et al. 2020 tables as a real CEC2020 verification reference.
- **A11 — Commit, tag `dtgsk-submission-v2.0-<date>`, push** (7.6); cut the GitHub Release → new Zenodo DOI version (8.2).
- **A12 — SuSy submission** with portal-only personal data (8.4).

---

## Calendar estimate

Assumes one campaign machine (22 logical cores), agent sessions of a working half-day, author available for decisions/launches daily.

| Window | Work | Wall time |
|---|---|---|
| Day 1 | Phase 0 core (Gate 0, CR-0019/20, 1.5.0-N, pre-registration drafted+signed+committed, byte-guard, preflight, config lock, wrapper neutralized); parallel tracks 0.8–0.10 opened | 1 day (2 sessions) |
| Days 2–3 | **Phase 1 compute: 247–265 core-h ≈ 20–30 h wall** (D5/D10 sanity ~2 h, D15 ~4–5 h, D20 overnight). In parallel: forensics closure, namespace hygiene, promote-tool build, phase6b skeleton, LSGO pairing audit, LSGO mint (2.6), citation lockstep | 1.5–2 days |
| Day 4 | 1.5 completeness verification + 1.6 heritage audit; CEC2020 pairing audit; 2.7 cec2020-rel mint; 2.8 disclosure package | 1 day (2 sessions) |
| Days 5–6 | Phase 3: phase6b completion, confirmatory batteries, robustness, registries, exhibit fragments | 2 days (3–4 sessions) |
| Days 7–9 | Phase 4 manuscript surgery (claims first) + Phase 5 supplement S7/S8 + cross-format plumbing ([DROP] adds ~1 day) | 2.5–3.5 days (4–6 sessions) |
| Day 10 | Phase 6 build + double gate sweep + adversarial re-sweep + snapshot reconciliation | 1 day (1–2 sessions) |
| Day 11 | Phase 7 re-freeze, pass-24 statement, tag v2.0, push | 0.5 day |
| Day 11+ | Phase 8: GitHub Release → Zenodo DOI (minutes + Zenodo latency), SuSy submission | 0.5 day |

**Totals:** ~13–17 agent/author working sessions over **10–12 working days at steady pace; 2–3 calendar weeks realistic** with author availability slack. Compute: one resumable 247–265 core-hour campaign (~20–30 h wall, worst case ~40 h) — the only compute in the entire endgame; everything else is analysis, prose, and governance. The critical path is: pre-registration commit → CEC2020 D20 tranche → phase6b confirmatory output → headline/abstract wording → gate sweep → re-freeze. The schedule long poles outside compute are the LSGO suite-definition PDF (A6) and the `.prebugfix` adjudication (0.8) — both start on Day 1.