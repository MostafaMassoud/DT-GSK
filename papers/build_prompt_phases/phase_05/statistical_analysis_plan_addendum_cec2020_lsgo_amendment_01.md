# Statistical Analysis Plan — Addendum 1, Amendment 1
# (dated, separately justified, per Addendum Section 13)

Date: 2026-07-28. The signing commit of Addendum 1 is `5c9bfae82`; this
amendment changes NO registered hypothesis, analysis id, tie rule, wording-bank
sentence, or evidential tier. It does three things Section 13 requires be done
in a new dated amendment rather than by silent edit: (1) corrects one
previously-inspected number recorded in Section 6 that does not reproduce;
(2) tightens the outcome-blindness declaration of Section 0 with a
cross-reference the original text should have carried; (3) records the FIRST
computation of two registered LSGO analysis families, with input pins, so no
later recomputation can silently substitute a different method.

## A1.1 Correction to Section 6 (prior-inspection disclosure)

Section 6 records, among the quantities informally inspected before signing,
"omnibus p = 0.0372". Recomputation from the seven banks on 2026-07-28 gives,
for the family-only tie-corrected Friedman on per-function means (the recipe
whose mean ranks Section 6 reports and which DO reproduce exactly):

    chi2 = 15.3143, df = 6, p = 0.01795   (tie correction C = 1.0; no tied blocks)
    Iman-Davenport F(6, 84) = 2.8707, p = 0.01358
    (cross-checked against scipy.stats.friedmanchisquare: identical)

The recorded value could not be reproduced, and is structurally inconsistent
with the ranks recorded beside it: a Friedman p is a function of the mean ranks
alone, and the recorded ranks (which reproduce exactly) force chi2 = 15.314,
p = 0.0179. p = 0.0372 at df = 6 would require chi2 = 13.393. An exhaustive
mechanical search (4 bases x {full, 3-significant-digit, 10-digit inputs} x
{all seven algorithms, each drop-one subset, the six-without-dt-gsk panel} x
{all 15 functions, each drop-one subset} x {chi-square, tie-corrected,
Iman-Davenport}, plus Friedman over the 375 per-run blocks, run-prefix/suffix
means, and every committed historical state of the seven banks) found NO recipe
that rounds to 0.0372. The nearest mechanistic candidate is the repository
helper `friedman_rank_test` (papers-side `statistical_tests.py`), whose default
`excluded=(2,)` silently drops F2 -- a CEC2017-era default -- giving p = 0.0370
on the LSGO means; its ranks do not match the recorded ones, so it is not the
source either. Verdict: the recorded p was a transcription or tooling error in
the informal inspection; the ranks were the accurate part. The corrected value
is recorded above. LATENT HAZARD, binding on Phase 3: the `excluded=(2,)`
default must never be allowed to touch a non-CEC2017 suite -- the phase6b
driver passes the exclusion list explicitly for every suite.

The registered consequence is unchanged and unchangeable: this omnibus layer is
DESCRIPTIVE-AFTER-INSPECTION whatever its p-value, and no headline may rest on
it. The correction matters only for accuracy of the disclosure itself.

## A1.2 Scope tightening of Section 0 (outcome-blindness)

Section 0 declares the CEC2020 registration outcome-blind. That declaration is
about CEC2020 RESULTS and remains true (verified at signing: zero CEC2020 banks
existed; first CEC2020 datum written 2026-07-28 01:08:08, 15m52s after the
signing commit). It does not, and was never meant to, assert that the PROPOSED
ALGORITHM is development-blind: DT-GSK was developed and selected on CEC2017
across six full-panel candidate configurations, as attested in decision_log.md
entry D-0020 (2026-07-23). Section 3's directional expectation already builds on
this. This amendment makes the cross-reference explicit so "outcome-blind"
cannot be read wider than registered.

## A1.3 First computation of AN-PW-LSGO-NATIVE and AN-PWRUN-LSGO-NATIVE

Both families were computed for the first time on 2026-07-28, after the signing
commit and exactly as registered. Input data pinned by SHA-256 of the seven
per_run.csv files:

    gsk         8cc973e546f82bbe897d86172f0e76daf83c5eeeb26a8809af51208d62d8a723
    agsk        bf4ae39eeb619a51d366e067a1620175093d0244c73691dc965de18caf5c1c71
    apgsk       5b1e6fc6520c265031a79570be0dea6f2cce8bd49b41dd24adddd60ff7c45175
    fdb-agsk    8dcfb4b265ef65b335515e8c840566654018fb963b190298c5d076499e7810df
    atmals-gsk  422aedd640115743844bf6d386ec7eddf471045952bd5fdb020f8f232d8191e6
    egsk        b11ee3a564b5891d37f7224d56d0f06a2e5617b5b7ff06d299d7e6ed1ca07f97
    dt-gsk      091340735e0be7d3d0a48d5c5ed92fcb36de405e6e41e0d993ea7605d1fe7500

Methods, exactly as executed (and independently re-verified by a second
implementation before this amendment was committed
: a fully independent implementation
(own CSV parsing, own midrank computation, own full 2^15 enumeration, own exact
signed-rank null distribution, own Holm, no scipy) reproduced every Layer-1
exact p to six decimals, every Layer-2 Holm-significant win/loss count, and all
24 cells of the F4/F8 win-all and F7/F15 lose-all regularities. Fragility note
for the record: the single significant cell nearest the boundary is the gsk/F13
loss at Holm-adjusted p = 0.0472; every other significant cell sits at or below
0.020):

AN-PW-LSGO-NATIVE (supporting-with-disclosure): per-function MEAN of raw
best_fitness over 25 runs; d = dt-gsk minus comparator; zeros |d| < 1e-8
discarded (none occurred; n_eff = 15 for all six); two-sided p by EXACT
sign-flip enumeration over all 2^15 signed-rank patterns; the
normal-approximation p (repo wilcoxon_paired) recorded alongside; Holm m = 6.
Result: NO comparator separates from DT-GSK at alpha = 0.05 after Holm.
    comparator   W-L   p_exact  p_normal  p_Holm
    gsk          8-7   0.7615   0.7548    1.0000
    agsk         9-6   0.8469   0.8424    1.0000
    apgsk       11-4   0.0554   0.0571    0.2875
    fdb-agsk    11-4   0.0833   0.0832    0.3330
    atmals-gsk   8-7   0.1688   0.1641    0.5065
    egsk        11-4   0.0479   0.0501    0.2875

AN-PWRUN-LSGO-NATIVE (confirmatory-with-disclosure; never computed before
registration): per-function run-level Wilcoxon over the 25 seed-paired runs
(pairing key = run id; seed identity across all seven algorithms re-verified,
zero mismatches); scipy.stats.wilcoxon method="exact"; zeros |d| < 1e-8
discarded per function; Holm ACROSS THE 15 FUNCTIONS per comparator (m = 15);
NO additional correction across the six comparators (as registered — the six
columns are not jointly error-controlled and must not be summed into one claim).
Holm-significant per-function outcomes (dt-gsk wins / losses / n.s.):
    gsk         8 / 6 / 1    won F2,F3,F4,F6,F8,F10,F12,F14      lost F1,F5,F7,F9,F13,F15
    agsk        9 / 6 / 0    won F2,F3,F4,F5,F6,F8,F9,F10,F12    lost F1,F7,F11,F13,F14,F15
    apgsk      11 / 3 / 1    won F1,F2,F3,F4,F5,F6,F8,F9,F11,F12,F14   lost F7,F13,F15
    fdb-agsk   11 / 4 / 0    won F1,F3,F4,F5,F6,F8,F9,F10,F11,F12,F14  lost F2,F7,F13,F15
    atmals-gsk  7 / 6 / 2    won F4,F5,F8,F9,F10,F11,F14         lost F1,F2,F3,F7,F12,F15
    egsk       11 / 4 / 0    won F1,F2,F3,F4,F6,F8,F10,F11,F12,F13,F14 lost F5,F7,F9,F15

Cross-comparator regularities (descriptive): DT-GSK is Holm-significantly
better than every family member on F4 and F8, and Holm-significantly worse than
every family member on F7 and F15.

BINDING WORDING CONSEQUENCE (Section 9 ceiling, now data-resolved): the paired
layer does NOT separate DT-GSK from AGSK (across-function exact p = 0.8469,
Holm 1.0), so the registered sentence applies verbatim: "tied-first descriptive
rank; paired tests do not separate DT-GSK from AGSK."

Pipeline note: these values were computed by a standalone script against the
pinned inputs. The Phase 3 driver (phase6b) MUST reproduce them exactly from
the promoted release; any digit-level difference is a defect in the driver, not
a new result. AN-EFF-LSGO-NATIVE (A12/Cliff + BCa) remains registered and NOT
yet computed.
