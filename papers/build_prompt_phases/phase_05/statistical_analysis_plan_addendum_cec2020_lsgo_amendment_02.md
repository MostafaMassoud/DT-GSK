# Statistical Analysis Plan — Addendum 1, Amendment 2
# (dated, separately justified, per Addendum Section 13)

Date: 2026-07-29. Addendum 1 signing commit `5c9bfae82`; Amendment 1 recorded the
first computation of the two LSGO Wilcoxon families. This amendment changes NO
registered hypothesis, analysis id, tie rule, evidential tier or wording-bank
sentence. It records, as Section 13 requires, the FIRST COMPUTATION of the
remaining registered families — the LSGO effect-size family and the entire
CEC2020 confirmatory battery — together with the outcome sentence that the
pre-committed wording bank selects, so that no later recomputation can silently
substitute a different method and no later draft can silently substitute
different wording.

## A2.1 First computation of AN-EFF-LSGO-NATIVE

Computed 2026-07-28 against the promoted release `lsgo-rel-2026-07-28-ff1a046ef`
(inputs are the same seven banks pinned by SHA-256 in Amendment 1 §A1.3;
re-verified byte-identical). 90 cells = 15 functions x 6 comparators.

Method, exactly as executed. A12 and Cliff's delta at RUN level over the 25
seed-paired runs, using the frozen SAP Section 7 tie band |d| < 1e-8 counted
half; BCa 95% CIs with B = 10000 on the paired mean differences. Three seeding
decisions a future driver MUST match, recorded because the registered text fixes
the scheme but not these instantiations:

  1. suite ordinal **2113**, the addendum's own registered override of the frozen
     `{2017, 2013, 2011}` enumeration (Addendum Section 4);
  2. the **native** dimension in the entropy list — 1000, and **905 for F13/F14**
     — following the frozen CEC2011 precedent in `phase6_run_analysis.py`;
  3. the comparator index is the **0-based P1 position** (gsk 0 … egsk 5).

Per-cell RNG therefore = `SeedSequence([20240620, 2113, <native dim>, <function>,
<0-based comparator index>])`, one independent reproducible stream per cell.

Degeneracy: **0 of 90 cells degenerate.** n_eff = 25 in every cell (no tied pairs
exist at LSGO raw magnitudes). The SAP Section 7 disclosure strings were
therefore not emitted; they remain wired and reachable.

Result. Effects are bimodal rather than graded: 86 of 90 cells are "large" and 52
are saturated at A12 exactly 0.0000 or 1.0000 (complete sample separation). Mean
A12 by comparator: gsk 0.5885, agsk 0.6097, apgsk 0.7830, fdb-agsk 0.7060,
atmals-gsk 0.4988, egsk 0.7261. **Against atmals-gsk the mean effect favours the
comparator** (mean Cliff -0.0025); no superiority over atmals-gsk on this suite is
supportable from the effect layer. F4 and F8 are complete separations in DT-GSK's
favour against all six comparators; F7 and F15 are near-complete separations
against it. 85 of 90 BCa intervals exclude zero.

Cross-check against AN-PWRUN-LSGO-NATIVE: all 86 Holm-significant cells agree on
BOTH the A12 direction and the sign of the paired mean difference — zero
disagreements. One disclosed divergence of estimand, not of direction: F1 vs gsk
has A12 = 0.1456 (large, favouring gsk) while its BCa interval on the mean
difference straddles zero, because F1's raw distribution is heavy-tailed. Both are
reported; neither is suppressed.

Independent verification before recording: a second implementation (own A12/Cliff
loops, own BCa, own exact signed-rank, no shared primitives) reproduced all 90
A12 and Cliff values to exact zero gap and all BCa endpoints to <= 3.6e-05
relative, and independently recomputed AN-PWRUN from the raw runs, matching
Amendment 1 line for line.

## A2.2 First computation of the CEC2020 confirmatory battery

Computed 2026-07-29 against the promoted release
`cec2020-rel-2026-07-29-5867abe1e` (7 banks x 1,140 rows = 7,980 runs; 38
protocol cells; completeness and cross-algorithm seed pairing verified before
promotion, 0 mismatches). Error basis, floor 1e-8, exactly as registered.

**AN-OMNI-2020** (tie-corrected Friedman + Iman-Davenport + seeded permutation,
B = 100000). All four dimensions separate the panel decisively, and the
permutation p agrees with the parametric p at every dimension:

| dim | N | chi2 | F_ID | p | permutation p | C |
|---|---|---|---|---|---|---|
| 5  | 8  | 23.217 | 6.558  | 6.099e-05 | 7.0e-05 | 0.821 |
| 10 | 10 | 40.238 | 18.325 | 1.795e-11 | 1.0e-05 | 0.900 |
| 15 | 10 | 37.661 | 15.173 | 4.337e-10 | 1.0e-05 | 0.800 |
| 20 | 10 | 42.524 | 21.899 | 7.215e-13 | 1.0e-05 | 0.900 |

Mean ranks (lower is better):

| dim | order |
|---|---|
| 5  | apgsk 2.375, agsk 2.750, fdb-agsk 2.750, **dt-gsk 4.250**, egsk 4.875, atmals-gsk 5.375, gsk 5.625 |
| 10 | agsk 1.900, fdb-agsk 2.200, apgsk 3.000, **dt-gsk 4.100**, atmals-gsk 5.200, egsk 5.400, gsk 6.200 |
| 15 | agsk 2.100, fdb-agsk 2.300, apgsk 3.500, **dt-gsk 3.500**, gsk 5.500, egsk 5.500, atmals-gsk 5.600 |
| 20 | agsk 1.600, fdb-agsk 2.000, apgsk 3.500, gsk 4.500, **dt-gsk 4.600**, atmals-gsk 5.800, egsk 6.000 |

**AN-RANKAGG-2020-OVERALL** (descriptive, no test attached): agsk 2.0875,
fdb-agsk 2.3125, apgsk 3.0938, **dt-gsk 4.1125**, egsk 5.4437, gsk 5.4562,
atmals-gsk 5.4938. DT-GSK places **fourth of seven**.

**AN-PW-2020** (across-function Wilcoxon, exact sign-flip enumeration, Holm m = 6
per dimension). DT-GSK is Holm-separated in five cells of twenty-four:

- **wins** — D15 vs atmals-gsk (Holm 0.0469) and vs egsk (0.0469); D20 vs egsk (0.0469);
- **losses** — D20 vs agsk (Holm 0.0234) and vs fdb-agsk (0.0234);
- all other nineteen comparisons are ties, including every comparison at D5 and D10.

**AN-ROB-2020.** The binding Section 10 instability rule does **not** fire: under
both registered across-dimension aggregate variants (D10/15/20-only, and the
common-8-function subset at all four dimensions) DT-GSK's ordinal is stable, so
the headline carries no instability disclosure. The mean-vs-median re-rank does
move several per-dimension ordinals (recorded in full in the robustness digest);
those are reported as registered and do not touch the aggregate standing.

## A2.3 Outcome sentence selected by the pre-committed wording bank

AGSK attains the best descriptive family rank (2.0875) and DT-GSK places fourth.
Section 9 fixed three sentences before any datum existed; the applicable one is
the **[AGSK first]** variant, reproduced here with its single slot filled and
nothing else altered:

> On AGSK's strongest suite — the CEC2020 competition it won — DT-GSK places
> **fourth**; the family panel corroborates AGSK's published strength in this
> regime, consistent with the tiering thesis: every dimension-gated DT-GSK
> subsystem is inactive at D <= 20.

This is the outcome Section 3 predicted in advance and registered as a *boundary
finding of the dimension-tiering thesis*, not as a result that "does not count".
The conflict-adjacency disclosure of Section 10 accompanies every interpretation
of this suite: AGSK won this competition and its paper is a co-author's.

Two further wording constraints follow from the numbers and are binding: the
suite-level statement must record that DT-GSK is Holm-separated in only five of
twenty-four pairwise comparisons (three favourable, two unfavourable), and no
CEC2020 sentence may claim superiority over AGSK or FDB-AGSK at any dimension —
at D20 both separate from DT-GSK in their favour.

## A2.4 Disclosed text slip in the addendum (not corrected in place)

Addendum Section 7 states the Nemenyi critical distance at N = 15 as 2.327; the
value implied by the registered constants is 2.326203 (q_0.05(k=7) = 2.949). The
N = 8 and N = 10 values quoted there reproduce exactly. This is a last-digit
transcription slip in the pre-registered text, disclosed here and emitted as a run
note by the analysis driver, which does not edit the pre-registration. No reported
statistic depends on the quoted digit.

## A2.5 Amendment integrity

This file is append-only after its signing commit, under the same rule as
Addendum 1 Section 13. The analyses recorded above were executed by
`papers/scripts/phase6b_run_analysis_newsuites.py`, which carries a self-check
that reproduces Amendment 1's pinned LSGO values and fails loudly on any
digit-level difference; any future recomputation must reproduce both amendments
exactly or be recorded as a further dated amendment.
