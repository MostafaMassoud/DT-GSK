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
CEC2017 remains PRIMARY (development); CEC2011 and CEC2013 corroborative;
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
(51/51/25/30/25) and basis heterogeneity (error vs raw) therefore never
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
