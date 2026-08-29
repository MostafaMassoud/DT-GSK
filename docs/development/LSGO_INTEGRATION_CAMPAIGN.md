<!-- Provenance: produced 2026-07-25 by a six-lens expert panel (evidence
engineering, statistics, manuscript architecture, supplement architecture,
adversarial review, governance) plus a synthesis pass. The two blocking findings
in the box below were re-verified first-hand against the repository before this
document was written; everything else is panel analysis and carries the panel's
own confidence, not an independent check. -->

# CEC2013LSGO Integration — Campaign Plan

> **Internal quality-assurance instrument.** This is a work-sequencing and
> execution prompt the authors used on their own project. It is **not** the
> journal's peer review and did not substitute for it, and it governs tooling
> and campaign ordering rather than scientific judgement. It may be executed by
> a human team or with AI assistance; the authors used the latter, disclosed in
> the manuscript's *Use of Generative Artificial Intelligence* statement, which
> is the authoritative account. See the README section "Internal
> Quality-Assurance Instruments".


> **HISTORICAL RECORD — executed.** This plan was written while the campaign was
> still being scoped, and its status line below is preserved as written. It is
> **not** current: the CEC2013LSGO leg ran to completion, was promoted as the
> immutable evidence release `lsgo-rel-2026-07-28-ff1a046ef`, and is reported in
> the manuscript and in Supplementary Section S7. The manuscript freeze it names
> (`dtgsk-submission-v1.0-2026-07-25`) has been superseded many times; for the
> current pass and tag read papers/governance/main_manuscript_freeze_manifest.json (its `phase` field) and the newest entry in papers/governance/decision_log.md.
>
> *Status as written, retained for the record:* PLANNING. The manuscript remains
> frozen at `dtgsk-submission-v1.0-2026-07-25` (commit `41726c544`). Nothing in
> this plan has been executed. The dt-gsk LSGO run is in progress (125/375 runs;
> F1-F5 complete; roughly 11 h wall remaining at 13 workers, from a measured
> dt-gsk/agsk cost ratio of 2.08x).

## Two blocking findings, verified first-hand

**BLOCKER 1 — the Ackley variant makes F3/F6/F10 non-comparable to MOS.**
`ackley_raw_scope` exists in `benchmarks/cec_suite_python/cec2013lsgo/_kernel_mode.py`
but is **unwired**: no reference to it exists anywhere in `src/`, `configs/`,
`tests/` or `papers/scripts/`. Every family cell therefore ran the **transformed**
Ackley (T_osz, T_asy(0.2), Lambda(10)) - Molina's package form, the same one
SHADE-ILS used - while LaTorre's published MOS table was measured on the **raw**
`benchmark_func.m` form. The numbers confirm it decisively: on F3 the family spans
2.001e+01..2.159e+01 against SHADE-ILS 2.01e+01 and MOS 1.69e-12; on F6, family
1.052e+06..1.061e+06 against SHADE-ILS 1.02e+06 and MOS 1.43e+05; on F10, family
9.281e+07..9.401e+07 against SHADE-ILS 9.18e+07 and MOS 9.38e+05. The family lands
on top of SHADE-ILS and one to thirteen orders away from MOS on precisely the three
Ackley-based functions. That is the signature of a different objective, not a
performance gap.

*Correction to the record:* the earlier statement "MOS beats all six family members
simultaneously on 12 of 15 functions" is **not admissible as stated**. Over the 12
objective-comparable functions the correct figure is **9**, and F3/F6/F10 must be
reported as "not comparable (objective variant)". Ruling A-6 governs: disclose and
restrict, do not wire the raw scope, do not re-run.

**BLOCKER 2 — the evidence tree holds three files its own manifest does not list.**
The primary namespace of `benchmarks/cec_reference_results/` contains 3,406 files
while `evidence_release_manifest.json` lists 3,403. The extras are
`BENCHMARK_EVIDENCE_INDEX.md`, `cec2013lsgo/mos/mos_cec2013lsgo.csv` and
`cec2013lsgo/decc-g/decc-g_cec2013lsgo.csv`. `check_manifest.py` walks
manifest-to-disk only, so no gate can see a disk-to-manifest extra - which is why
the release verified "3403/3403" earlier and still does. Two consequences: the
README's "no run ever writes here" and the supplement's "no evidence file was
hand-edited" are literally false today, and because `cec2013lsgo/` is **not**
underscore-prefixed, `finalize_evidence.py` P6 would silently absorb those baseline
tables into the primary manifest on the next mint. Fix before any promotion
(tracks 0D and EV-00/EV-02).

---

# CEC2013LSGO Integration — Programme Campaign Plan

**Project:** `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1`
**From:** manuscript frozen at `dtgsk-submission-v1.0-2026-07-25` (41726c544), 10/10 gates green, check_manifest 15/15, four artifacts byte-reproducible; LSGO campaign live.
**To:** re-frozen, gate-green, submission-ready manuscript with CEC2013LSGO in main paper + supplement — *or* a deliberately deferred suite with a one-sentence disclosure and the freeze substantially intact.
**Status at time of writing (verified, not reported):** `results/_run_all/dt-gsk/cec2013lsgo/summary/per_run.csv` = **150 data rows** (F1–F6 complete at D1000), ahead of the 125 in the tasking. Six comparators at **375 data rows each**. Nine function-cells remain for dt-gsk: F7–F12 and F15 at D1000, F13/F14 at D905 = **225 runs**.

---

## How to read this document

- **§A** rules on every place two lenses disagreed. These rulings are binding for the rest of the plan; each carries its evidence.
- **§B** is the honesty contract. These are hard constraints with veto power, not editorial preferences.
- **§C–§K** are the phases, dependency-ordered. Each phase states objective / entry / exit / steps / parallelism.
- **§F** is the GO/NO-GO gate with both branch plans.
- **§L** is the page-and-word budget ledger.
- **§M** is the severity-ordered risk register.
- **§N** is the list of decisions no agent may make.

Task ids from the six lenses (EV-*, SM-*, MM-*, SUP-*, LSGO-*, G*) are carried through so the source analysis stays traceable.

---

# §A. Standing rulings — where the lenses disagreed

## A-1. Supplement placement: **APPEND as S7.** Reject the S2-fold-in.

**The disagreement.** The supplement lens ruled append-as-S7 (three gates hardcode `S6` as the ablation; 41 hand-typed `Section~S<n>` strings outside `supplementary.tex` have no validator). The governance lens ruled fold-into-S2.7/S3.4 (keeps the section count at six, avoids editing `main.tex`'s `\supplementary{}` block, avoids the documented reflow trap).

**Verified facts.** `papers/supplementary.tex` has exactly six line-initial `\section{}` at lines 206, 308, 646, 1001, 1037, 1904. The `\supplementary{}` block in `papers/main.tex` (~lines 209–227) carries the standing warning verbatim — *"Do NOT lengthen this opening sentence: it reflows the paragraph and can push an 'S6.x' cross-reference to the start of a line, which trips the main-PDF no_ablation_scan gate"* — and the paragraph ends `... S6.5, S6.6, and S6.7 (S6).`

**Why governance loses.** Its central argument is that the fold-in avoids touching that paragraph. It does not. The S2 clause reads *"pairwise matrices and additional-suite detail for **CEC2011 and the CEC2013 second comparison suite**"* and the S3 clause reads *"the convergence figure sets for **all three suites**"*. Both are falsified by an LSGO subsection inside S2/S3, so the paragraph must be edited under either option. The fold-in therefore buys nothing structural while paying the adversarial lens's burial cost in full.

**Ruling.** New top-level `\section{Large-Scale Extension: CEC2013 LSGO at D = 1000}` appended **after** the S6 ablation, labelled `sec:supp:lsgo`. Subsections S7.1 scope/protocol, S7.2 per-function record, S7.3 statistical treatment, S7.4 convergence, S7.5 external context, S7.6 what this does and does not establish. Zero renumbering; zero edits to the 41 external `Section~S<n>` literals; `S6` stays the ablation so `validate_cross_format_parity.py:589` and `validate_docx.py:475` keep testing what they claim. Budget two to three rebuild/parity iterations for the reflow trap (§I).

## A-2. Release architecture: **second, non-superseding release under an underscore-prefixed path.**

**The disagreement.** Three answers were offered: (i) evidence lens — mint `lsgo-rel-*` under `benchmarks/cec_reference_results/_cec2013lsgo/`, non-superseding, following the `_ablation` / `abl-rel-2026-07-20` precedent; (ii) main-manuscript lens — populate the primary manifest's empty `release_scope.context_suites`; (iii) governance and statistics lenses — mint a new release with `supersedes_release = rel-2026-07-20-67d9345f9`.

**Verified facts.** `papers/scripts/finalize_evidence.py:1089` filters the evidence walk on `not p.name.startswith("_")`. A plain `cec2013lsgo/` directory *will* be silently absorbed into the primary manifest at the next P6 mint — which is exactly how the two unlisted `mos/` and `decc-g/` CSVs entered the tree (EV-00).

**Why (ii) and (iii) lose.** (ii) is self-defeating: editing `evidence_release_manifest.json` to populate `context_suites` *is* re-minting the release whose identifier the option exists to preserve. (iii) voids the identifier printed at ten sites (`main.tex:267`, `supplementary.tex:1193/1202/1225/1829/1896`, `conclusions.tex:7`, `performance.tex:5`, plus three governance manifests) and trips `validate_provenance_claims.py`'s AUTHORITY check on every authority block.

**Ruling.** Evidence lens wins. Mint `lsgo-rel-<date>-<anchor9>` with its own `manifest.json` at `benchmarks/cec_reference_results/_cec2013lsgo/`. `supersedes_release: null`. The primary manifest is **not touched** — `release_scope.context_suites` stays `[]`.

**Bonus resolution (verified this session).** `validate_provenance_claims.py`'s `release_universe()` builds its superseded set from `(PAPERS/"analysis").glob("rel-*")`. A bundle directory named **`papers/analysis/lsgo-rel-<date>-<anchor9>/`** does not match that glob, so the primary release is not reclassified as superseded and every existing authority sentence survives. This single naming choice dissolves the governance lens's largest predicted gate failure (G17). **Mandatory: run `validate_provenance_claims.py --self-test` immediately after the bundle directory is created to confirm empirically.**

## A-3. Analysis pipeline: **extend `phase6_run_analysis.py` in place, behind a byte-identity guard.**

**The disagreement.** Evidence lens: do not touch it, write `phase6_lsgo_analysis.py`. Statistics, supplement and governance lenses: extend it.

**Ruling.** Extend in place, **with byte-identity of the three frozen suites as a hard, blocking acceptance gate**: after the extension, re-run into a *new* output directory and `diff -r` every file of `papers/analysis/<new>/{cec2011,cec2013,cec2017}` against `papers/analysis/rel-2026-07-20-67d9345f9/`. Zero differences or the extension is rejected and reverted. Rationale: the frozen bundle on disk is immutable and cannot be perturbed by a re-run into a new directory; the only real hazard is that a refactor *would* change what the script produces, and the diff detects that with certainty. A clone cannot detect it — it would silently diverge. Extension + guard is strictly more informative than cloning. Constraint: add LSGO **by new dictionary entries and a new suite branch only**; never edit shared statistics code in `src/gsk_family/analysis/statistics.py`.

## A-4. External baselines: **all three (MOS, SHADE-ILS, DECC-G) or none — and the ruling is all three, confined to descriptive supplement exhibits, with the loss stated in the main text and abstract.**

**The disagreement.** Governance lens: family-only, MOS out (Class D prohibition in `comparability_audit.md` §3; `PAPER_REVIEW_PROMPT.md` §1.5.4 out-of-scope directive). Main-manuscript lens: out of the main text entirely (four self-refuting sites). Statistics lens: family-only for inference, externals in a captioned context table. Evidence lens: SHADE-ILS as the primary anchor. Adversarial lens: all three or none, and omission reads as concealment because `decc-g` is already committed in this repo.

**Ruling — a composite that satisfies all five.**
1. **Admit all three.** SHADE-ILS is the *stronger* external result (lens-measured mean rank 1.533/8 vs MOS 2.200; beats all six family members on 13/15 vs MOS's 12/15) **and** runs the same transformed-Ackley objective path as our port, making it the only objective-comparable external across all 15 functions. Including MOS while omitting SHADE-ILS is selective reporting on the exact axis a referee checks. DECC-G is physically present at `benchmarks/cec_reference_results/cec2013lsgo/decc-g/` and beats all six family members on 5/15; excluding it is cherry-picking a reviewer can verify in one `ls`.
2. **No external enters any inferential exhibit.** MOS/DECC-G are 5-statistic published tables; SHADE-ILS has only the `Mean` column populated. Wilcoxon, Holm, rank-biserial, A12 and BCa all require paired per-run values and are therefore *impossible*. Externals appear in (a) one descriptive per-function context table, (b) one descriptive Friedman-on-per-function-means rank row explicitly labelled non-inferential. Never in a ranked column mixed with locally-produced cells without a label.
3. **Exhibits live in the supplement (S7.5).** The main-manuscript lens is right that a MOS *panel exhibit* in the main text simultaneously falsifies `proposed_algorithm.tex:719`, `performance.tex:27-30`, `introduction.tex:138-140` and `conclusions.tex:85-89`.
4. **The finding lives in the main text and the abstract.** A *sentence* is not a panel exhibit. §B-1 makes the abstract sentence non-negotiable. The four self-refuting sites are **rewritten to own the reversal**, not quietly softened (§A-5).
5. **Overturn the prohibitions through their own mechanism.** `comparability_audit.md` §3 Class D and `PAPER_REVIEW_PROMPT.md` §1.5.4 are amended by change request (CR-0019/CR-0020), not ignored. Governance's objection is procedural and the procedure exists.

## A-5. `conclusions.tex:85-89` — **own the reversal explicitly; do not paper over it.**

The paper states it deliberately declined a wider roster because *"values quoted across source publications would carry uncontrolled implementation and environment differences."* Quoting MOS does that. **Ruling:** the replacement text must state that the cross-publication comparison declined for the primary panel is admitted for LSGO **only**, as a descriptive scope check, **precisely because the unfavourable direction makes the uncontrolled-differences objection self-limiting** — the caveats can only make the family look better, never worse. That is a genuine, defensible asymmetry and it is the only honest way to reverse a stated methodological principle.

## A-6. Ackley variant on F3/F6/F10: **disclose and restrict; do not wire `ackley_raw_scope`; do not re-run.**

**The disagreement.** Evidence lens: blocking; 3 of 15 MOS comparisons are a different objective function; choose disclose-and-restrict (a) or wire-and-rerun (b). Adversarial lens: measured the divergence (transformed vs raw ≈ 1.004–1.006× at random points, ≈1.94× near the optimum) and ran the sensitivity — excluding F3/F6/F10 changes nothing material (MOS still beats all six on 9/12, SHADE-ILS on 11/12).

**Ruling — take option (a), and bind it to the sensitivity.** Both lenses are correct and their findings compose: the divergence is *real and must be disclosed*, **and** it is *small and cannot be used as an excuse*. Required together:
- Per-cell footnote on F3/F6/F10 in every MOS-bearing exhibit: "not objective-comparable — the family and SHADE-ILS ran the transformed Ackley (`_kernel_mode.py:61-72`), MOS's published table is on the raw form."
- The restated MOS count reported over the **12 objective-comparable functions**.
- The bounding sensitivity reported in the same paragraph, so the caveat is closed rather than left open: excluding F3/F6/F10 does not change the conclusion, and the ~13-order F3 gap (family 20.007 vs MOS 1.69e-12) is *not* explained by the variant.
- SHADE-ILS designated the **primary external anchor** because it is comparable on all 15.
- Do **not** wire `ackley_raw_scope` through `benchmark_adapter/factory.py` and do **not** run a raw-Ackley leg. That is 3 funcs × 7 algs × 25 runs plus new code plus a new regression pin, to answer a question the sensitivity already answers.

## A-7. Statistical family definition: **one native-dimension LSGO family over 15 functions (the CEC2011 precedent).**

**The disagreement.** Adversarial lens: test at D=1000 only (13 functions), D905 descriptive, because the paper's within-dimension rule makes a 2-block D905 test degenerate. Statistics lens: adopt `AN-*-LSGO-NATIVE` by exact analogy with CEC2011, which already runs one family over 22 problems spanning 16 distinct dimensions.

**Ruling.** Statistics lens wins. Friedman and the across-function Wilcoxon rank **within** each function block, and every block is internally dimension-homogeneous (all algorithms at the same D for that function), so heterogeneous D never enters a comparison. The adversarial concern is fully addressed by the two prose prohibitions the statistics lens attaches: **never** write "the suite at D = 1000", and **never** pool raw objective values across functions. `SUITE_DIMS['cec2013lsgo'] = [0]` mirroring cec2011, plus a `_NATIVE_DIMS`-style per-function map so output rows carry 905 or 1000.

## A-8. Page vs word budget: **B1 has ~3 pp headroom; B2 (words) is the binding constraint.**

**The disagreement.** Governance lens read the freeze manifest's *"DT-GSK.pdf 41 pp (B1<=40, CR-0008)"* as already at cap. Main-manuscript lens measured back matter beginning p.38 and References p.39, giving **B1 = 37 pp against a 40 pp cap**.

**Ruling.** Main-manuscript lens's decomposition is the correct reading of CR-0008's own definition (main text incl. exhibits, **excl.** references and back matter). B1 has ~3 pp of headroom. **B2 is the constraint: ~19,370–19,536 words against 20,000, i.e. ~460–630 words of headroom against a realistic LSGO cost of 1,300–1,900.** This inverts the usual instinct: figures are cheap, prose is expensive. See §L for the harvest ledger.

## A-9. Table identifiers: **main-text table = T17; supplement tables = SA05+.**

**Verified.** `_TTABLE_INPUT = re.compile(r"\\input\{tables/(T\d+(?:_bca)?|SA\d+)\}")` is duplicated at `build_docx.py:426` and `validate_cross_format_parity.py:70` — both accept T17 and SA05. But `build_docx.py:1250-1251` defines `_RESULTS_TEX_IDS = {"T1"…"T16"}`, and at `:1458` that set decides whether the DOCX renders the **frozen `.tex` formatting** or falls through to a raw `word_sources` DataFrame dump. **T17 must be added to `_RESULTS_TEX_IDS`** or the main-text LSGO table will silently render differently in Word than in the PDF — a parity defect that no gate names clearly. The supplement lens's warning was right on the mechanism; the governance lens's naming was right on the series.

## A-10. Inference depth: **run the full family-internal protocol; report the function-level layer as primary; state the power arithmetic a priori.**

Main-manuscript lens argued descriptive-only plus one sentence (cheaper and equally honest). Statistics lens argued the full protocol is available family-internally (25 paired runs per cell) and pre-wrote the saturation disclosure. **Ruling:** run everything family-internal (it is seconds of compute), but allocate main-text space by information content: **main text** = descriptive rank table + one sentence of pre-declared power arithmetic; **supplement S7.3** = the full Wilcoxon/Holm/effect-size/BCa layer with the statistics lens's mandatory non-discrimination note (A12 saturating at 0.000/1.000 in 24 of 30 measured cells; 24 of 30 raw p at the n=25 approximation floor 1.308e-05). **Do not ship a Nemenyi CD diagram for LSGO** — the pipeline constant is k=7-only and at n=15 the CD separates essentially nothing (k=6 → 1.947, k=7 → 2.326, k=8 → 2.711, against an observed six-algorithm rank span of 2.200).

## A-11. Curves: **exclude from promotion; promote `gen_logs`.**

Unanimous where the lenses overlapped. ~360 MB of curve CSVs (individual files to 5,897,667 bytes / 107,485 rows) against a 712 MB release, for evidence `BENCHMARK_EVIDENCE_INDEX.md:105-107` already records that no script parses. Convergence figures come from `gen_logs/CheckpointErrors_*.csv` (~124 KB per algorithm). Promote per_run + two summary CSVs + five provenance files + gen_logs ≈ 154 files, ~3 MB. **Record the exclusion and its rationale in the LSGO manifest so it is a documented decision, not a gap.** Guard: `finalize_evidence.py` `_classify` raises `RuntimeError` on unclassifiable extensions — a stray `curves/graphs/*.png` under the evidence tree aborts the mint.

## A-12. `block_size` disclosure vs re-run: **disclose (mandatory) AND run the block_size=10 contrast (strongly recommended, author-decided).**

Every lens demanded disclosure. Main-manuscript and adversarial additionally recommended running the shipped-default cell. **Ruling:** disclosure is a hard constraint (§B-2). The contrast run is **the single highest-value optional compute in this campaign** because it converts the campaign's largest liability into its scientific contribution — "a dimension-tiered design fails outside its calibrated tier range, and here is the rung that runs out" is a falsifiable finding; "DT-GSK placed mid-pack" is not. Costed as optional Phase M (§J), decided by the author at the GO/NO-GO gate.

---

# §B. Hard honesty constraints (veto power)

These bind every phase. Violating any one is a stop-work condition, not a review comment.

**H1 — The negative headline appears in the ABSTRACT.** Not only in Section 4, not only in Conclusions, not only in S7. The abstract currently enumerates every unfavourable headline cell (D=30 second place, the Holm-significant CEC2011 loss, the selection-exposure statement). A fourth suite where DT-GSK does not lead is a strictly worse cell than anything in that ledger; omitting it converts an honest ledger into a selectively favourable one. **If the author will not put it in the abstract while the abstract still says "best overall Friedman mean rank (2.48)", the suite is not added** — see the defer branch.

**H2 — The `linkage_block_size` override is disclosed in the MAIN text**, alongside the existing eGSK-port and self-initialisation exceptions — not in a supplement footnote and not only in a YAML comment. It must state: the parameter, the value (905→50, 1000→50 against the shipped table topping out at 240→10), that **only DT-GSK** received it, that it encodes the benchmark's declared 20×50 group structure, that `configs/dtgsk_cec2013lsgo.yml` records "No parameter search was run" (an author assertion a reviewer cannot verify — say so), and that DT-GSK still places mid-pack **with** it.

**H3 — Loss-visibility parity.** Every unfavourable LSGO cell material to a headline is stated **alongside**, never after, the favourable ones. The main-text LSGO subsection states DT-GSK's actual placement in its first two sentences, before any mechanism explanation.

**H4 — Banned vocabulary in all LSGO prose.** "competitive", "comparable", "on par", "near", "state-of-the-art", "best algorithm". Family-to-MOS mean ratios include 74.5×, 98.9×, 380×, 3.16e3×, 1.18e13×, and infinite on F1 where MOS = 0.000e+00. DT-GSK's F4 — its single strong cell — is 16.1× MOS and 9.5× SHADE-ILS: write *"an order of magnitude behind both external references, but the best in the family"*, never *"the only algorithm near MOS"*.

**H5 — No fabricated measurement, ever.** Specifically: **never** write "no statistically significant difference" about MOS, SHADE-ILS or DECC-G. No test is possible against a summary-only table; such a sentence would invent a measurement. Write *"no inferential comparison against the external references is possible; the ordering is descriptive"* and give the raw per-function ratios so the reader sees the magnitudes are 10¹–10³, not marginal. Never fabricate a DOI, a table number, a page locator, an access date, or a reviewer name.

**H6 — No partial-suite rank is ever typeset**, even with a caveat. The F1–F6 preview has been seen and is burned: it may not be a selection input and may not be reported as a rank. Its omnibus is non-significant (statistics lens: k=8, n=5, Iman-Davenport F = 1.949, p = 0.099) and the 5-function subset is demonstrably unrepresentative (agsk moves from rank 1 over 15 functions to rank 3 over 5).

**H7 — No LSGO number reaches any `.tex` file before promotion completes.** Every LSGO value today lives in `results/_run_all/` (staging, forbidden by `PAPER_BUILD_PROMPT.md` §2.3) or in the sibling project `05-Human-Inspired-Family_Python_v0.1/` (outside this project's evidence tree entirely). No gate re-derives table values from the release, so a staging-sourced table is an integrity defect **no gate will catch**.

**H8 — Silence is now the worst option.** A 375-run × 6-algorithm campaign sits in a repository `main.tex:266-270` promises to publish, in a paper whose central claim is dimension-tiered control. A reader who finds `results/_run_all/*/cec2013lsgo/` with zero mention of it has found an omission that looks deliberate. Both branches of the GO/NO-GO gate therefore disclose the campaign; they differ only in how much.

---

# §C. PHASE 0 — Parallel work while dt-gsk runs (~20 h remaining)

**Objective.** Land every item that is independent of the run finishing, so that Phase 1 exit → Phase 4 gate is measured in hours rather than days. Nine of the fourteen work-streams below can start immediately.

**Entry criteria.** None. Start now.

**Exit criteria.** All of 0A–0I complete; 0J–0N complete or explicitly deferred with a named owner. `check_manifest.py --strict-inventory` implemented and passing. No `.tex` file modified.

**Hard rule for this phase: no `.tex` edits.** Phase 0 is governance, tooling, forensics and citation work only. Prose starts at Phase 5.

---

### Track 0A — Governance authority (BLOCKS everything else; do first)
*Lenses: G01, G23, SM-01, SM-03, LSGO-03, MM-01*

1. **CR-0019** in `papers/governance/change_request_register.csv` (register currently ends at CR-0018; every entry since CR-0008 declares `affected_claims: NONE` — this one cannot). Nine columns. `affected_phases`: 1,2,4,5,6,7,8,9,10,11,12 (**Phase 3 does NOT reopen** — no optimizer-core edit is required or permitted). `affected_claims`: IN-01, LM-03, LM-05, MT-08, CN-01, CN-02, PR-03, PR-04, RS-01, RS-11 + new rows. `rerun_plan`: no re-run of the three frozen suites; new LSGO evidence promotion + extended analysis into a separately-named bundle.
2. **Reopen `papers/governance/_pending_refreeze.json`** (currently CLOSED) as a live control document *before touching any source*, mirroring the 2026-07-22 precedent: `opened_utc`, `reason`, `standing_constraints` (no optimizer-core edit; no comparator edit; no re-run of the three frozen suites; frozen-suite analysis outputs byte-identical), `exit_criteria`.
3. **Move eleven `phase_gate_register.csv` rows** FROZEN → reopened, with fresh entry evidence. Phase 3 untouched.
4. **`decision_log.md`** entries from D-0021.
5. **Amend the four frozen texts that forbid this suite** (SM-03), each as an explicit dated amendment block, never an in-place overwrite:
   - `phase_04/novelty_scope.md:101-102` non-claim #4 and `:129` evidence-role table ("Not run … not citable").
   - `phase_05/statistical_analysis_plan.md:229` ("CEC2013-LSGO = context-only, no claims, not citable").
   - `governance/comparability_audit.md` §3 Class D (`cec2013lsgo × decc-g, mos` — *"prohibited: any appearance in a panel table, rank, test, or effect-size computation"*). Re-adjudicate: family LSGO cells → Class A; mos/decc-g/shade-ils → Class C, descriptive only.
   - `governance/data_ledger.csv:174-175` ("context-only: NOT admissible for seven-method panel").
6. **`PAPER_REVIEW_PROMPT.md` §1.5.4** — the standing directive putting non-GSK baselines out of scope. Replace it and re-scope Stages 8 and 18 accordingly, accepting that external-baseline fairness becomes fully in scope for the review panel.

> **Parallelism:** 0A-1 through 0A-4 are sequential (~2 h). 0A-5 and 0A-6 can run in parallel once CR-0019 exists.

---

### Track 0B — Pre-commitment (HARD ~20 h DEADLINE — highest value per hour in the campaign)
*Lens: SM-02, SM-06, SM-15, SM-16*

This is the only mechanism that makes any part of this analysis blind, and the window closes when F7–F15 land. After that, any comparator-set choice is unfalsifiably outcome-contingent and a referee is entitled to assume the most flattering set was chosen.

1. **Write and date a SAP amendment** (new block; do not edit the frozen body — the file preserves original pre-registration text with inline `[RESOLVED CR-xxxx]` annotations) recording:
   - The comparator set, decided **now**, per §A-4: family-7 for all inferential families; MOS + SHADE-ILS + DECC-G as a separately-labelled descriptive external-context layer with its own (non-inferential) treatment.
   - The family definition per §A-7 (`AN-*-LSGO-NATIVE`, 15 functions, native dims).
   - The exact exhibit templates.
   - **An explicit statement that the DT-GSK 15-function result was not observable at the time of writing.**
   - **The F1–F6 preview declared burned** (H6), with the statistics lens's non-significance arithmetic recorded so it cannot be re-quoted later.
   - The a-priori power statement (A-10 numbers), stated as a prediction, not later as an excuse.
   - **The cross-suite aggregation prohibition** (SM-16): no `AN-RANKAGG-LSGO` family is created, so there is no artifact for a later editorial pass to "harmonize".
2. **Label the entire LSGO treatment EXPLORATORY.** SAP §13 item 2 makes this mandatory once the outcome has been inspected. Do not fight it: it costs a headline the suite was never going to yield and buys the credibility to report an unfavourable result. The *methods* are legitimately inherited from a plan frozen 2026-07-10 before any outcome was seen — say exactly that, and separate it cleanly from the post-hoc decision to run the suite.
3. **Write the post-hoc / HARKing disclosure paragraph** (LSGO-04) naming, with dates: that `rel-2026-07-20-67d9345f9` predates and is unaltered by the LSGO campaign; that the LSGO protocol is exploratory and carries no family-wise guarantee shared with the primary suite; that the six comparators were complete before the protocol was written; the config deviation; and every interim look. Introduce a **fourth evidence category** in the `performance.tex:107-112` taxonomy — *post-freeze exploratory* — rather than smuggling LSGO into "corroborative".

> **This track blocks nothing and is blocked by nothing. Start it in the first hour.**

---

### Track 0C — Data forensics on the six complete cells (BLOCKING; may invalidate the campaign)
*Lenses: SM-05, LSGO-08, EV-04*

**0C-1 — The `.prebugfix` question. This outranks every methodological item in the plan.**
`atmals-gsk` and `egsk` carry undocumented `*.csv.prebugfix` siblings. Joined on Function, the only material change is **atmals-gsk F8/D1000 mean 4.1786968587E+13 → 5.4149023801E+13 (+29.6%)**; egsk moves in the last digit only. Those two algorithms ran **last** (2026-07-23/24). `gsk`, `agsk`, `apgsk`, `fdb-agsk` ran **2026-07-22/23, before the fix, and were never re-run.**
- Identify the defect by name and commit.
- Determine whether it touches the four earlier cells.
- **If it does, four "complete" cells are invalid, the campaign is not 375/375 × 6, and the six-algorithm ranking on which this entire analysis rests is wrong.** That is an automatic NO-GO trigger (§F) unless the author authorises >100 h of re-run compute.
- Record the finding either way in `papers/governance/production_deviation_record.md`.

**0C-2 — Code-identity attestation across six run commits** (EV-04). Per-cell `environment.json` `git_commit`: gsk `a1bb33497`, agsk `45248eb31`, apgsk/fdb-agsk `593d598dcc`, atmals-gsk `e04e20a0dc`, egsk `385f5ad465`, dt-gsk ≥ `cf5083bb7`. Between `a1bb33497` and HEAD, **all six comparator optimizer sources changed**, plus `common/threefry_rng.py` (+100/−19), `common/reference_rng.py`, `benchmark_adapter/{factory,problem}.py`, `runners/{output,parallel,run_experiment}.py`; and the LSGO objective code changed twice (`81c08bb85`, `5dc4d906a`).
- Extend `tests/regression/test_family_golden_values.py` to cover `cec2013lsgo` at reduced budget.
- Re-verify at HEAD **one exact `best_fitness` triple per comparator** against the value recorded in its own `per_run.csv` at its run commit.
- If any cell fails: re-run that cell at a single pinned commit, or the LM-03 attribution claim (*"one code base, one protocol and one harness"*, `supplementary.tex:1301-1308`) must be **explicitly scoped to exclude the LSGO leg** and the six revisions named in S5.

**0C-3 — Summary↔per_run recomputation audit with a documented tolerance.** Recomputing the five-statistic set reproduces the summaries except 1–2 SD cells per algorithm at the 10th significant digit (gsk F6 SD 1348.7076781 recomputed vs 1348.7076764 stored, rel 1.3e-9) — catastrophic cancellation at O(1e13). The CEC2017/CEC2013 exact-match standard (435/435, 580/580) **cannot** be applied. Declare a **relative tolerance of 1e-8** in the SAP amendment, or the audit reads as a failure.

**0C-4 — Re-verify against the CR-0012 resume-corruption bug** (BUG-RESUME-01: *"resume mode silently corrupted the per-dimension summary CSV"*, reported from the sibling shade-ils LSGO campaign). Row-by-row summary-vs-per_run verification for **all seven** algorithms, recorded in `verification.json`.

---

### Track 0D — Evidence-tree integrity (must land before promotion)
*Lenses: EV-00, EV-05, EV-06, EV-08, EV-14, EV-18*

1. **Close the 3,405-vs-3,403 divergence.** `benchmarks/cec_reference_results/` holds two files absent from its own manifest: `cec2013lsgo/mos/mos_cec2013lsgo.csv` and `cec2013lsgo/decc-g/decc-g_cec2013lsgo.csv`, both committed 2026-07-22, **after** the 2026-07-20 mint. `check_manifest.py` walks manifest→disk only (loop at :49-63) and defaults to the 15-file freeze manifest, so "15/15" and "all digests verified" are both green while `README.md:4-7` ("no run ever writes here") and `supplementary.tex:1879` ("no evidence file was hand-edited") are literally false today.
   - Relocate both into the new `_cec2013lsgo/` context tree with provenance sidecars.
   - **Add `--strict-inventory` to `check_manifest.py`**: a disk→manifest direction that fails on any unlisted file under a non-underscore evidence directory. This class of drift must never pass again.
   - Record the episode in the deviation register rather than quietly correcting it.
2. **Fix the vacuous `verification.json`.** Every LSGO cell reports `verdict: CONSISTENT` with `functions_checked: 0`, `missing_reference: 15`, `win_tie_loss: [0,0,0]`, while `supplementary.tex:1832-1833` advertises verification records as checksummed evidence. Emit `NOT_VERIFIED` / `NO_REFERENCE` for zero-coverage cells, **or** point the LSGO verifier at the vendored external tables so it compares something real. Disclose whichever is chosen in S5.
3. **Endpoint column.** `error` is NaN in all 2,625 LSGO per-run rows (by design: `statistics_basis: raw_objective`, no LSGO optimum offsets). `phase6_run_analysis.py:254` hardcodes `endpoint_col = "best_fitness" if suite == "cec2011" else "error"`, and `:850` likewise. **cec2013lsgo must join the `best_fitness` branch.** Add a hard assertion in the new table generator that no emitted cell is NaN. Document in `docs/reference/result_schema.md` that curve columns `BestError`/`Log10Error` and the `CheckpointErrors_*.csv` filenames carry **raw objective**, not error-to-optimum — a reviewer reading "BestError 6.44e+06" for F1 would conclude the run failed. Separately verify from the shipped suite definition whether f\* = 0 makes the two numerically identical, and **state the answer**; do not assume it.
4. **Commit the config drift.** `git diff` shows `configs/dtgsk_cec2013lsgo.yml` with an uncommitted `overwrite: true → false`. The config that produced the existing rows is not the config on disk, and neither is committed. Commit it; make the promoted `run_config.json` the authority for what actually ran. *(Author action — the agent does not commit.)*
5. **Correct the stale promotion-tool citation.** `supplementary.tex:1862-1868` names `scripts/promote_evidence.py`, whose own docstring says it writes `<dest>/_releases/<release-id>/…` and that "the flat live layout is never written" — but `_releases` does not exist (retired 2026-07-18) and actual promotion is `finalize_evidence.py` `phase_P2`'s `copy_cell_tree`. A reviewer tracing the new suite walks into a dead tool. Fix the prose to the real chain (`scripts/run_campaign.py` → `papers/scripts/finalize_evidence.py`, as `README.md:5-7` states).

---

### Track 0E — Tooling build (offline; no data required)
*Lenses: SM-10, SM-11, SM-12, SM-13, EV-11, EV-16, G07, G08, SUP-03*

1. **`phase6_run_analysis.py` extension** per A-3 and A-7: `SUITE_ORDER`/`SUITE_ORDINAL`/`SUITE_DIMS`/`SUITE_FUNCS`/`SUITE_FSET`/`N_RUNS` (:87-95); `summary_path()` (:228-231) — LSGO has **two** summary CSVs per algorithm which the current one-file-per-dim signature cannot express; `load_per_run()` endpoint branch (:254, :850); `_NATIVE_DIMS` analogue; `expected_funcs` (:609); `expected_rows` (:635); an LSGO branch in `_rq_secondary()` (:844). Also `src/gsk_family/analysis/result_loader.py:177` `SUITE_DIMS` and `:193` `SUITE_EXCLUDED_FUNCS`.
2. **Parameterise the Nemenyi constant.** `NEMENYI_Q_005_K7 = 2.949` (:92/:101) and the formula at :993 hardcode `sqrt(7*8/(6*n))`, and :996 writes the literal `"7"` into the k column. At k=8 this understates CD by 3.031·√72 / (2.949·√56) = **1.166×** — a silent wrong-direction error that manufactures separations. Demsar Table 5(a): k=6 → 2.850, k=7 → 2.949, k=8 → 3.031, k=9 → 3.102. Assert k against panel size in the row writer. Check `generate_nemenyi_cd.py` for the same constant (it is separately hardcoded to CEC2017 paths).
3. **LSGO separability taxonomy** as a distinct `CATEGORIES` set: fully separable F1–F3, partially separable F4–F11, overlapping F12–F14, non-separable F15. Do **not** reuse the CEC2017 unimodal/multimodal/hybrid/composition taxonomy (:99-104).
4. **Exact-Wilcoxon decision.** `statistics.py:332-334` docstrings an exact distribution for n ≤ 25 that `:379-398` does not implement. At n=15 the approximation inflates the floor p 11.9× (6.104e-05 exact vs 7.266e-04) and moves the Holm boundary by one rank unit. Either add `scipy.stats.wilcoxon(..., method="exact")` for n ≤ 25, or formally waive it in the SAP amendment for continuity with the frozen suites. **Either way, fix the docstring/code contradiction.** Also ticket the latent defect at `statistics.py:509` (`labels.index(str(c['label']))` raises `ValueError` on non-str labels).
5. **BCa entropy for LSGO.** SAP §7:130 admits `suite_ordinal ∈ {2017, 2013, 2011}` only. Declare `suite_ordinal = 20131000` by amendment and the dimension slot as the function's actual native dim (905 or 1000). ~900k resamples; seconds.
6. **LSGO promotion path** — a self-contained phase or a separate `promote_lsgo.py`. `finalize_evidence.py` `SUITES` (:108-121) has three entries; `STAGE_RUNALL` (:89) is dt-gsk only; `phase_P2` (:546-558) refreshes only `REF/<suite>/dt-gsk`, so **the six LSGO comparator cells have no promotion path at all**. New code must: stage all seven cells into `_cec2013lsgo/`, enforce per_run row counts (375 = 325 at D1000 + 50 at D905), enforce five provenance files per cell, refuse non-CSV/JSON, exclude curves, and mint the LSGO manifest. **Leave `phase_P2`/`phase_P6` untouched** so the frozen primary mint is provably unaffected. Note `phase_P6`'s comparator drift guard (:1085-1108) iterates `old['files']` only, so any *new* file is absorbed silently — that is how the mos/decc-g files got in.
7. **Table generators.** New `papers/scripts/generate_cec2013lsgo_tables.py` (clone `generate_cec2013_pairwise.py`, which writes `SA03.tex` **and** `word_sources/SA03.json` in one pass at :37/:123-144). New `papers/scripts/generate_cec2013lsgo_convergence.py` (clone `generate_cec2013_convergence.py`, 4×2 grids, groups a = F1–F8, b = F9–F15 with one blanked axis; resolve per-function dim via `_convergence_common.native_dim_for()` at :123, so F13/F14 titles read "F13 (D=905)").
8. **Registration plumbing** for T17: `generate_word_sources.py` `TABLES` dict (:69), `generate_latex_tables.py` generator fn, `generate_artifact_binding.py` `table_spec` (:168-204), `_paper_tables/provenance.json` `exports`, `_paper_tables/manifest.json` `table_provenance_chain`, and **`build_docx.py:1250` `_RESULTS_TEX_IDS`** (§A-9). Pass `GSK_REL_ID` explicitly — `generate_artifact_binding.py` defaults to the stale `rel-2026-07-16-78f075cb0`.

> **Parallelism:** 0E-1/2/3 are one work-stream; 0E-4/5 another; 0E-6 another; 0E-7/8 another. Four parallel lanes. All are offline and none touches `.tex`.

---

### Track 0F — Citation corpus (LONG POLE — author-dependent, not parallelisable by an agent)
*Lenses: MM-03, SUP-12, G04, LSGO-05*

`papers/governance/allowed_citation_keys.txt` is a **closed 57-key set**; `references.bib` has 57 entries; `governance/evidence_cards/` has 57 hand-written cards; `reference_papers/` holds the matching PDFs. `assumption_register.csv` A-0006 records the one-to-one correspondence. There is **no key** for:
- the **CEC2013 LSGO benchmark definition** (Li/Tang/Omidvar/Yang/Qin 2013) — **mandatory under both branches**. `liang2013cec2013` is *not* it: `references.bib:497-502` shows its title is the CEC 2013 **Real-Parameter** special session, the 28-function bound-constrained suite.
- **MOS** (LaTorre et al.), **SHADE-ILS** (Molina et al. 2018), **DECC-G** (Yang/Tang/Yao 2008) — required only if externals are admitted (they are, per A-4).

Per key, in lockstep or `validate_citation_controls.py` fails C1/C2/C3/C5: `references.bib` entry with a **verified** DOI; the PDF in `reference_papers/`; an evidence card **that exists on disk** (check C2); rows in `citation_role_map.csv`, `citation_usage_map.csv`, `word_citation_tag_map.csv`, `reference_inventory.csv`; a line in `allowed_citation_keys.txt` (57 → 61); `PAPER_BUILD_PROMPT.md` Appendix A and Appendix B.4 updates.

The existing 57 cards are deep hand reads (see `evidence_cards/alfadli2025atmals.md`). Four new cards means four papers obtained and read end to end.

> **The author must supply the four PDFs. Never reconstruct bibliographic metadata from memory or the web.** Precedent: CEC2013 could be added by ADDENDUM_R2 *because* `liang2013cec2013` already existed and its role was upgraded. LSGO has no key to upgrade — this is a genuine reopening of the closed corpus (CR-0020).

**Start this in hour 1. It is the only item that can be blocked by an external dependency.**

---

### Track 0G — Page/word budget harvest (no results dependency)
*Lens: MM-09; see §L*

Draft the migrations now, apply them at Phase 5. All four donors are in `performance.tex` and all are supplement-eligible under `PAPER_BUILD_PROMPT.md` §1.5's own overflow rule.

---

### Track 0H — Config lock gate
*Lenses: EV-13, EV-15, SM-08, SUP-08*

`scripts/validate_profile_lock.py` `REQUIRED_LOCKS` (:63) covers three smoke configs only. `configs/dtgsk_cec2013lsgo.yml` is entirely ungated — nothing prevents an edit to the linkage table, the seed, the run count or `overwrite`. Add an entry pinning `seed: 20240620`, `seed_policy: unified`, `rand_generator: threefry`, `runs: 25`, `dimensions: [905, 1000]`, `overwrite: false`, `strict_profile_dims: true` and the **full 22-key `linkage_block_size_by_dim` table**. This is the gate that must exist before the paper can call the LSGO configuration locked.

Note *why* no existing gate can see the change: the override travels through `DTGSKConfig` (`_dt_core.py:186`, resolved at `:2216-2219`) rather than editing `_dt_profiles.py`, so that file's SHA-256 `7baadf228d356394` (printed at `supplementary.tex:1215`) stays valid and `test_dt_gsk_byte_stable.py` still passes while the effective configuration has changed. Also confirm in prose that the commented-out `arch_max_size: 50` lever — which the config itself labels *"CHANGES RESULTS … never enable for a frozen paper cell"* — stayed commented for every promoted run.

---

### Track 0I — Register scaffolding
*Lenses: G25, G26, SUP-13, EV-09*

Prepare (do not yet populate with results): `data_ledger.csv` rows for seven algorithm cells + completion of the two external rows whose checksums read `MISSING` and release id reads `PENDING-RELEASE-ID`; `benchmark_protocol_audit.md` §6.2 matrix row (15 functions, D1000 with F13/F14 at D905, 25 runs, MaxFES 3,000,000, raw-objective endpoint, boundary handling, seed schedule, evaluator hash — `benchmark_protocol_audit_part2.md:26` already records `data.pkl` hash `1b79d4caa2b4…`, and `:120` mislabels the 3e6 budget as "(context) … not used by the primary panel", which must be corrected); `seed_and_pairing_audit.md`; `fp_environment_audit.md` (`runners/fp_regime.py:62` maps cec2013lsgo to the numba backend, `:74` pins threads to 1); `risk_register.csv` and `assumption_register.csv` new rows; `evidence_gap_register.md` (MOS/DECC-G have no per-run data; SHADE-ILS has only `Mean`); `captions_registry.md`; `table_figure_source_map.csv`.

**External-baseline provenance** (EV-09): per baseline, a `provenance.json` recording publication + citation key, table/page, run count, FES budget, dimension set, the **objective-variant flag** from A-6, the upstream file SHA-256, and the source path + commit. The provenance trail lives in project 05 (`docs/development/matlab_parity/verdict_{mos,shade_ils}_cec2013lsgo.md`, `MATLAB_PARITY_REGISTER.md`, `reference_code/external_baseline_algorithms/mos/VERSION_FREEZE.md`) and must travel with the tables. Note the two copies already in project 02 have **no provenance sidecar** and a different directory name than the source (`mos` vs `mos-cec2013lsgo`).

---

**Phase 0 parallelism map.** 0A is a prerequisite for 0A-5/0A-6 only. 0B, 0C, 0D, 0E, 0F, 0G, 0H, 0I all run concurrently and none blocks another. **Critical path through Phase 0 is 0F (citation PDFs) if the author is slow, otherwise 0C-1 (the prebugfix forensics).**

---

# §D. PHASE 1 — Run completion and dt-gsk cell closure

**Objective.** A promotable seventh cell, structurally identical to the six comparators.

**Entry criteria.** Phase 0 tracks 0C and 0D complete. dt-gsk campaign finished (F7–F12, F15 at D1000; F13, F14 at D905).

**Exit criteria.** `results/_run_all/dt-gsk/cec2013lsgo/` holds 375 per_run data rows, two summary CSVs (`_D1000.csv` and `_D905.csv`), 15 gen_logs, and **all five** provenance files. All seven cells pass the 0C-3 recomputation audit at 1e-8 and the 0C-4 resume-bug verification. The MemoryError episode is recorded.

**Steps.**

1. **Wait for the run.** Do not shortcut. Current: 150/375.
2. **Emit the four missing provenance files** (EV-03, SUP-02, LSGO-01): `environment.json`, `phase0_protocol.json`, `run_config.json`, `verification.json`. All six comparators have them. Without `run_config.json` there is no record of the dt-gsk leg's resolved `benchmark_backend`, worker count, `numba_threads`, `git_commit` or `optimizer_options` — and it is the **only artifact that records the contested `linkage_block_size_by_dim` table**, which today is provable solely from an uncommitted working-tree YAML.
3. **Assert `benchmark_backend` equality.** All six comparators resolved `"auto"` → `"python"`. A different resolved backend for dt-gsk means a different objective-evaluation code path. Assert equal or disclose.
4. **Dispose of `skipped_runs.csv`** (EV-08, LSGO-01, SUP-02). 25 rows, all `(F1, D1000, runs 1–25)`, all `MemoryError: Unable to allocate 1.10 MiB for an array with shape (144, 1000)` at `_dt_core.py:3408` (`accepted_displacements = ui[idx_imp,:] - pop[idx_imp,:]`) and `_dt_subsystems/interaction_graph.py:346`. All 25 were re-completed (skipped-but-now-present = 25, still-missing = 0), so the data is whole. But:
   - `skipped_runs.csv` is **not a promoted file class**; `copy_cell_tree`'s whitelist would treat it as an ignored staging extra and it would vanish without trace.
   - Decide explicitly: promote under a new file class with an S5 disclosure sentence, or exclude with a recorded exclusion. **Do not let the whitelist silently erase it.**
   - Record in `papers/governance/production_deviation_record.md` together with the resource change that made the re-run succeed (`workers: 13`, `parallel_backend: process`).
   - **Consequence for prose:** the DT-GSK leg ran under a different effective memory/parallelism condition than its first attempt, so **no LSGO runtime comparison involving dt-gsk is sound** (see §D-5).
5. **Runtime policy — closed now, not later** (G22, LSGO-12). `validate_runtime_provenance.py` defaults `PANEL = ['dt-gsk']` and enforces same host / same workers / ≤72 h gap. The LSGO campaign fails a panel-wide session audit on its face: gsk logged 2026-07-22, dt-gsk still running 2026-07-26. Decisively, **CR-0013–CR-0018 applied a family-wide acceleration campaign mid-window**, with CR-0018 recording paired-interleaved speedups of gsk LSGO D1000 **1.718×**, dt-gsk **1.440×**, agsk **1.205×** — different algorithms were timed under different code speeds. **Ruling: no cross-algorithm LSGO runtime is reported, at all.** But `performance.tex:821-822` currently publishes a cost curve stopping at 41.59 s at D=100; the measured dt-gsk D=1000 figure is ~1,696 s/run, a ~41× jump. Publishing the curve while omitting the point once D=1000 data is in the same paper is an omission. **Add DT-GSK's own D=1000 per-run cost as a single-algorithm, explicitly non-comparative point.**

**Parallelism.** Nothing in Phase 1 parallelises with itself; everything in Phase 0 continues alongside.

---

# §E. PHASE 2 — Evidence promotion and second-release mint

**Objective.** Every LSGO number readable by the analysis pipeline from an immutable, digest-verified, separately-identified release.

**Entry criteria.** Phase 1 exit. Phase 0 tracks 0D and 0E-6 complete. **0C-1 answered favourably** (or the campaign is already in the defer branch).

**Exit criteria.** `benchmarks/cec_reference_results/_cec2013lsgo/` holds seven cells + `manifest.json`; all digests verified; `check_manifest.py --strict-inventory` green; no LSGO file remains referenced from `results/`.

**Steps.**

1. **Relocate the two external tables** out of `cec2013lsgo/` into the new `_cec2013lsgo/external/` subtree, with the A-4 / 0I provenance sidecars, resolving the path collision *before* promotion so the underscore rule holds.
2. **Vendor SHADE-ILS** from project 05 (`benchmarks/cec_reference_results/cec2013lsgo/shade-ils/shade-ils_cec2013lsgo.csv`, sha256 prefix `07cc993304c0db81`) with full provenance. MOS and DECC-G are already byte-identical across projects (`0716596c45e30166`, `426c793165bd0b3c`) so they need release-scope inclusion, not import. **Never read project 05 at analysis time** — §2.3 forbids it.
3. **Promote seven cells** via the new `promote_lsgo.py` / dedicated phase: per_run.csv, two summary CSVs, five provenance files, 15 gen_logs per cell. **Exclude curves** (A-11). Verify no `curves/graphs/*.png` reaches the tree.
4. **Mint `_cec2013lsgo/manifest.json`**, schema `lsgo_evidence_manifest/v1`, mirroring `evidence_release_manifest/v1` plus four fields the frozen schema has no slot for and without which the leg cannot be read:
   - `objective_variant: "ackley_transformed"` (A-6)
   - `endpoint_column: "best_fitness"`
   - `statistics_basis: "raw_objective"`
   - `per_cell_run_commit`: the seven distinct `git_commit` values (0C-2)
   Plus an `external_baselines` block with the three provenance digests, and the **documented curve exclusion**. `supersedes_release: null`. Hash basis per `README.md:50-57`: SHA-256 over mint-time working-tree bytes, CRLF on this Windows checkout, verified EOL-tolerantly elsewhere.
5. **Do not run `finalize_evidence.py` end-to-end.** Its P0 preflight will pass while LSGO is absent; P2 refreshes dt-gsk only across three suites; P6 regenerates the whole analysis bundle **and re-mints the primary release**. Drive only the new LSGO phase.
6. **`check_manifest.py --strict-inventory`** over both trees.

---

# §F. PHASE 3 — Analysis execution

**Objective.** A complete, strict-source LSGO analysis bundle, with the frozen suites provably unperturbed.

**Entry criteria.** Phase 2 exit; Phase 0 track 0E complete.

**Exit criteria.** `papers/analysis/lsgo-rel-<date>-<anchor9>/` exists with `analysis_manifest.json` + `analysis_checksums.sha256`; **`diff -r` of the three frozen suites against `papers/analysis/rel-2026-07-20-67d9345f9/` returns zero differences**; `validate_provenance_claims.py --self-test` green; all AN-* LSGO ids minted by the bundle, not invented in prose.

**Steps.**

1. Run the extended `phase6_run_analysis.py` under `GSK_STRICT_SOURCE=1` with `GSK_REL_ID`/`GSK_ANCHOR` pointed at the LSGO release, output to the `lsgo-rel-*` directory (naming per A-2).
2. **Byte-identity guard (blocking).** Zero differences on cec2011/cec2013/cec2017, or revert the extension.
3. **Mint the analysis families**, all stamped EXPLORATORY:
   - `AN-DESC-LSGO-NATIVE` — five-statistic set + W/T/L on per-function means, 15 functions, no test.
   - `AN-OMNI-LSGO-NATIVE` — tie-corrected Friedman + Iman-Davenport, k=7 family; CD **conditional on omnibus significance** and **not rendered** (A-10).
   - `AN-PW-LSGO-NATIVE` — across-function Wilcoxon on per-function means, n=15, Holm m=6.
   - `AN-PWRUN-LSGO-NATIVE` — per-function run-level Wilcoxon on 25 seed-paired runs, Holm m=15 within comparator.
   - `AN-EFF-LSGO-NATIVE` — A12 + Cliff's delta + BCa 95% CI, B=10000.
   - `AN-COST-LSGO-NATIVE` — single-algorithm descriptives only (§D-5).
   - `AN-CONV-LSGO-NATIVE` — descriptive.
   - `AN-EXT-LSGO-CONTEXT` — descriptive external layer, `unit_of_analysis = "function"`, explicitly non-inferential.
   - **No `AN-RANKAGG-LSGO`** (SM-16).
   Verify each id resolves under `phase_08/audit_manuscript.py` `validate_bind_token()` (:336). Note the compact-expansion regex `DIM_LIST` (:304) will not match a `2013LSGO` infix and the range branch hardcodes `10/30/50/100`, so **write explicit ids, never ranges**.
4. **Register in `analysis_registry.csv`** (21 comment lines precede the header; 59 data rows today), all EXPLORATORY.
5. **Compute and record the mandatory robustness variant** — median re-ranking (`performance.tex:548-560` makes it mandatory for every rank statement). Lens-measured: on median basis the family order shifts (gsk and fdb-agsk tie at 3.267; atmals to 3.067), so the family-internal order is **not fully robust** and must be reported as such, exactly as for CEC2017.

---

# §G. PHASE 4 — GO / NO-GO GATE

**This gate is not "did DT-GSK win."** The honest negative is publishable — arguably the most scientifically interesting sentence available to this paper. The gate tests **admissibility and honesty-capacity**.

**Entry criteria.** Phase 3 exit. Phase 0 tracks 0A, 0B, 0F, 0H complete.

### G-1. Blocking criteria — ALL must be YES for GO

| # | Criterion | Evidence |
|---|---|---|
| **B1** | The `.prebugfix` defect does **not** invalidate gsk/agsk/apgsk/fdb-agsk | 0C-1 written finding |
| **B2** | Code-identity attestation passes across the seven run commits, **or** the LM-03 attribution claim is explicitly scoped to exclude the LSGO leg with the seven revisions named in S5 | 0C-2 |
| **B3** | All seven cells at 375/375 with five provenance files; recomputation audit passes at 1e-8; resume-bug verification clean | Phase 1 exit |
| **B4** | Second release minted and digest-verified; analysis reproduces strict-source; frozen suites byte-identical | Phase 2/3 exit |
| **B5** | **Author has signed the honesty package** — the abstract sentence (H1), the main-text config disclosure (H2), the external-baseline disposition (A-4), and the `conclusions.tex:85-89` reversal text (A-5) | Author sign-off, in writing |
| **B6** | Citation keys landed: LSGO suite definition **mandatory**; MOS/SHADE-ILS/DECC-G present, each with a real evidence card and a verified DOI | 0F |
| **B7** | A costed prose plan fits **B2 ≤ 20,000 words** and **B1 ≤ 40 pp**, or **CR-0021** raising the cap is approved | §L |

### G-2. Automatic NO-GO triggers (any one)

- **B1 fails** — four comparator cells invalid; the six-algorithm ranking underpinning everything is wrong. Recovery requires >100 h of re-run compute.
- **B2 fails and cells cannot be re-run at a pinned commit in the available time.**
- **Author declines H1 or H2.** A suite whose result is buried while the abstract advertises 2.48 is strictly worse for the author than never running it, because the data is discoverable and the omission is then deliberate.
- **The LSGO suite-definition PDF cannot be obtained.** Shipping a fourth suite uncited is not an option, and the metadata may not be reconstructed.
- **CR-0021 declined AND the §L harvest cannot free the required words.**

### G-3. Explicitly NOT decision criteria

DT-GSK's rank. Whether the family beats MOS. Whether anything separates under Nemenyi (it will not — CD 2.326 at k=7, n=15, against an observed six-algorithm span of 2.200). Whether MOS is Holm-significantly better than all six family members on per-function means (lens-measured: it is, p_holm 0.00436–0.02298). **None of these vetoes inclusion.** Recording them accurately is the deliverable.

---

## G-4. BRANCH A — INCLUDE (GO)

Proceed to Phases 5, 6, 7. Positioning, decided now and not renegotiated later:

> LSGO is a **post-freeze exploratory scope-limit result**, reported as the matched pair to the ISM isolation null: two honest negatives, one about a component and one about a scale limit, both bound to a locked protocol. The paper's identity becomes *"a dimension-tiered design with a measured competence boundary"* — a stronger and more defensible identity than a fourth suite where the method places third.

**Mandatory framing (adversarial lens, adopted in full).** Lead the LSGO subsection with the **mechanism**, not the rank — the tier ladder terminates at D = 100, so at D = 1000 every tier-indexed constant sits on its last configured rung. `configs/dtgsk_cec2013lsgo.yml` documents this precisely for linkage block size (the shipped step-function fallback yields block_size = 10 at D = 1000: 1.0 % coordinate coverage vs 4.2 % at D = 240, one fifth of the suite's designed 50-variable granularity). Reinforce with the population-policy point: `proposed_algorithm.tex:152-162` already discloses that comparators use NP = 100 while DT-GSK self-inits NP = 5D — *"at D = 100 that is 500 against 100"*. **At D = 1000 that is 5,000 against 100, a fifty-fold difference**, and the paper must state the ratio (the FES cost is negligible at 0.17 % of 3e6, but the head start on a separable function at D = 1000 is material and not attributable to the search mechanism). This asymmetry is an order of magnitude larger on LSGO than anywhere the paper currently discloses it.

**Reject the alternative framing** that LSGO is "a different problem class, outside scope." That contradicts the paper's own differentiator, which *is* dimension.

## G-5. BRANCH B — DEFER (NO-GO)

**Do not simply drop the suite.** H8 makes silence the worst option.

1. **Add one paragraph to `conclusions.tex:78-95`** naming the CEC2013LSGO campaign, its status, its staging path, and that it is deferred to a follow-up study. Include the direction honestly — the family does not lead published large-scale specialists at n = 1000 — so the deferral is a scope statement, not a concealment.
2. **Correct the three falsified sentences anyway**, because they will be falsified by the *repository*, not by the paper: `related_work.tex:221-222`, `conclusions.tex:82-83`, `supplementary.tex:1319-1322`. Narrow them from "unknown / no claim" to "not reported in this paper; a large-scale campaign is deferred to a companion study."
3. **Keep everything Phase 0 produced.** The governance amendments, the tooling, the promoted release, the analysis bundle, the citation cards — all of it is the companion paper's Phase 0. Nothing is wasted.
4. **Cost:** one paragraph, all 15 freeze-manifest files still change (the paragraph touches `conclusions.tex`, forcing a rebuild of four artifacts), one gate sweep, one manifest re-mint, one new tag. Roughly 1 day versus 6–9 for Branch A.
5. **Do not re-freeze at v1.0.** Even Branch B produces a new manuscript version (v1.1) and therefore a new tag and a new Zenodo DOI version.

---

# §H. PHASE 5 — Prose, exhibits and governance (Branch A only)

**Objective.** All content edits landed, all registers consistent, nothing built yet.

**Entry criteria.** Branch A selected at Phase 4.

**Exit criteria.** All `.tex` edits complete; all governance CSVs updated; measured word count within budget; no build has yet run.

---

### 5.1 — Claim-set surgery (do this FIRST; it makes drafting mechanical)
*Lenses: MM-02, G12, LSGO-03*

Three rows in `claims_evidence_matrix.csv` (50 rows) have `blocked_wording` that **forbids exactly the new content**. Rewrite wholesale, do not append; supersede rather than overwrite so the audit trail shows the prohibition was lifted deliberately.

- **LM-05** — *"Evidence tops out at D=100 … no LSGO claim is made"*, `blocked_wording: "Any LSGO or n~1000 claim"`, `risk: "LSGO over-claim"`. Its replacement's `permitted_wording` must **carry the unfavourable finding**; its `blocked_wording` must forbid any leadership phrasing.
- **LM-03** — `blocked_wording: "Comparisons to DE/ES/PSO fields or competition winners as claims"`. MOS is the CEC2013 LSGO competition winner.
- **MT-08** — `blocked_wording` includes "LSGO claim" for ISM, and ISM is **active** at D=1000 (`interaction_graph_min_dim = 50`, not overridden).

**Amend:** PR-04 (run counts/budgets, three suites only), IN-01 (`blocked_wording: "Extrapolation beyond D=100"` — a fifth data point must be kept out of the CEC2017 trend narrative), RS-01 (fence 2.48 to CEC2017), CN-01, CN-02, PR-03/RS-11 (the "second comparison suite" naming pin).

**New rows:** PR-07 LSGO protocol; PR-08 the config override; PR-09 external-baseline evidence class; RS-12 DT-GSK's LSGO rank; **RS-13 the family-only order is led by AGSK, not DT-GSK** (an explicit non-first-place primary result); RS-14 external context; RS-15 LSGO inferential statistics; IN-04 interpretation of a non-leading placement at the tier where C1/C2 are maximally active; LM-06 the 3000·D budget vs the paper's own 10⁴·D rule; LM-07 the block-size override; LM-08 the cross-implementation comparison.

---

### 5.2 — Supplement S7 (append; §A-1)

- **S7.1 Scope and protocol** — 15 functions, native D=1000 (905 for F13/F14), 25 runs, MaxFES 3,000,000; the raw-objective endpoint and the f\*=0 verification; the EXPLORATORY label; the post-hoc disclosure (0B-3); the config override (H2, repeated here); the MemoryError deviation.
- **S7.2 Per-function record** — **SA05 (+SA06 "Cont.")**, transposed 10-column form: rows = 15 functions × 5 statistics = 75 data rows; columns = Function | Statistic | 7 family + MOS + DECC-G. Portrait, `\resizebox{\textwidth}`, E-notation, best value per row in bold, two `table`+`tabular` parts. **Never a bare `longtable`** — `build_docx.py:437` `replace_generated_table_envs` walks only `table` environments, so a naked longtable bypasses native-table rendering into pandoc. **SHADE-ILS is excluded from this table** (only `Mean` is populated).
  - *Landscape is forbidden*: `PAPER_REVIEW_PROMPT.md` §1.5.0-K records all twelve `\begin{landscape}` wrappers removed and "0 landscape pages/sections in any deliverable"; reintroducing it re-breaks the Word blank-page fix.
  - *Rejected:* three tables × three algorithms (16 columns). SA03 overran the portrait block by 15 pt at only 13 columns.
- **S7.3 Statistical treatment** — **SA07** panel Mean±SD (9 columns); **SA08** across-function Wilcoxon + Holm, DT-GSK vs 6 family comparators, n=15 paired per-function means, with the n=15 power caveat in the caption; **SA09** Friedman mean ranks, **both panels in one table** — family-only and with-externals. Printing only one is selective reporting. Plus the run-level layer with the mandatory non-discrimination note (A-10).
- **S7.4 Convergence** — two 4×2 sub-grids, `cec2013lsgo_a` (F1–F8) and `_b` (F9–F15, one blanked axis). **7 curves, 8–9 table columns**: MOS/SHADE-ILS/DECC-G have no per-checkpoint data. Both captions and `papers/figures/convergence/cec2013lsgo_missing.log` must state the membership mismatch. **Never interpolate or synthesise an external curve.**
- **S7.5 External context** — the descriptive table, the cross-implementation caveat block, the A-6 Ackley footnote **plus its bounding sensitivity**, the SHADE-ILS mean-only limitation, the "no p-value, no effect size, no CI against any external" statement (H5), and a small hand-authored provenance table (source, run count, FES budget, hardware, what is and is not comparable).
- **S7.6 What this does and does not establish.**

**New labels:** `sec:supp:lsgo`, `sec:supp:lsgo:{protocol,tables,stats,conv,external,limits}`, `tab:lsgo-*`, `fig:sconv-cec2013lsgo-{a,b}`.

---

### 5.3 — Supplement corrections outside S7

- **`supplementary.tex:1143-1146` (S5.2)** — *"identical across all three suites (no per-suite tuning)"* is **falsified**. Rewrite to: one dimension-aware configuration tier-resolved over D ∈ {10,30,50,100}, identical across the **three frozen suites**; for the large-scale extension a single structure-matched, opt-in linkage-block override applied to **DT-GSK only**, disclosed here, comparators at defaults. Lift the config header's own justification. Mirror in **S5.3** (Configuration Selection) so the selection exposure appears where a reviewer looks for it.
- **Shared frozen protocol block (~176-200)** — add the LSGO paragraph; correct the error-endpoint sentence; **amend the panel-order invariant** at ~198 with a narrowly scoped S7 exception, since MOS is the first non-family, non-re-run, literature-sourced column in the entire document.
- **S5.1 (`:1073-1080`)** — 70,813 schedule rows / 21 cells → re-run the audit for the new totals (never arithmetic). *Good news:* `seed_schedule.csv` is **byte-identical across all seven optimizers** (md5 `55fc85f6ca24f1d55b20bdccf0a47997`, 8,188 bytes) and the LSGO formula matches Eq. (S-seed) exactly — `seed(1000,1,1) = 20240620 + 1000003·1000 + 1000033·1 + 1000037·1 + 1 = 1022243691`. The fair cross-family pairing claim transfers cleanly and is the one genuinely clean thing about this comparison. Say so.
- **S5.4 Limitations in Full (`:1278`)** — add: cross-implementation externals; 25 runs; n=15 with Holm (low power); no external per-run data; the block-size override; the MemoryError re-run; the absent 1.2e5-FES milestone (the grid is E30000…E3000000 with **no** E120000; nearest is E150000, 25 % high — disclose the substitution, do **not** re-run, which would invalidate all six completed comparator legs).
- **S5.11 (`:1826-1834`)** — name the second release, its file count, and that it does **not** supersede `rel-2026-07-20-67d9345f9`.
- **`supplementary.tex:1319-1322` (LM-05), `:1301-1308` (LM-03), `:1331-1337`** — all three are BIND-annotated and checked against both rendered formats. Rewrite per 5.1.
- **`:1862-1868`** — the dead promotion-tool citation (0D-5).

---

### 5.4 — Main text
*Lenses: MM-06 … MM-13, G13, LSGO-12*

**Title (`main.tex:95-96`) survives verbatim** — it contains no dimension range, no "high-dimensional", no suite names. This is luck, not design: the Phase-8 title in `phase_gate_register.csv` was *"An Interaction-Structure Memory for High-Dimensional…"*, which would have needed rewriting. **Keywords also need no change** — the list is already at 10 and "CEC benchmark suites" covers LSGO. Spend no effort here.

**Abstract (`main.tex:148-174`, 197 words against a hard ≤200 declared at `:144` — 3 words of headroom).** The **2.48 number survives unchanged**: it is `AN-RANKAGG-2017-OVERALL`, the unweighted mean of four CEC2017 per-dimension Friedman ranks, and LSGO adds no CEC2017 cell. What breaks is the framing: `:159-160`'s suite list, and the implicature that 2.48 is the study's overall standing. Required: fence 2.48 explicitly to CEC2017; add one clause naming LSGO as an out-of-tier extension at D=1000 where DT-GSK does not lead **and** the family is outperformed by published large-scale specialists (H1). Budget the deletion from the ISM sentence at `:157-158`.

**Section 4.1 setup (`performance.tex:46-107`).**
- H2 disclosure as a first-class protocol exception alongside the eGSK-port and self-initialisation exceptions.
- Rewrite `performance.tex:106-107` (*"identical across all three suites, with no per-suite tuning"*), `conclusions.tex:28-29`, `proposed_algorithm.tex:682-683`, `main.tex:280-283`.
- **`tab:protocol` (`:76-100`)**: currently `lccc` at `\footnotesize` with three `\multicolumn{3}{c}` spanning rows. A fourth data column is a real hygiene risk — the current build has **zero** overfull hboxes and `validate_build_hygiene.py` fails above `OVERFULL_TOL_PT = 2.0`. **Transpose (suites as rows) or split**; do not add a fifth column at reduced size (§1.5 forbids resolving overflow by pushing exhibits below legibility).
- MaxFES row shows 3,000,000 for LSGO, breaking the uniform 10⁴·D pattern.

**New LSGO subsection** — inserted in `performance.tex` between `:725` (end of `sec:exp:cec2013`) and `:727-728` (start of `sec:exp:convergence`). Contents in order: (1) suite definition + budget deviation; (2) the H2 config disclosure; (3) **the family-only Friedman ranking with DT-GSK's actual placement, stated first** (H3); (4) the statistical status + the a-priori power sentence; (5) the mechanism explanation (G-4); (6) the external-baseline sentence pointing to S7.5; (7) reconciliation with the rewritten LM-05. **Exhibit budget: exactly one table (T17) and at most one rank bar figure.** Calibration: the entire CEC2011 subsection is ~365 tokens and the CEC2013 subsection ~406; budget **550–750 tokens plus ~140 for captions**.

**Suite naming (MM-04).** Two suites named "CEC2013" in one paper. Fix once, everywhere: *"CEC2013 (bound-constrained)"* and *"CEC2013 LSGO"*, applied uniformly across all five section files, `main.tex`, `terminology_sheet.md`, and `phase_04/terminology_glossary.md`. `main.tex:359-381` `\abbreviations{}` has 17 rows and no LSGO row — add "LSGO — Large-Scale Global Optimization" (and MOS if named).

**Other main-text loci:**
- `introduction.tex:133-137` C3 (three-suite enumeration), `:138-140` the re-execution pledge (**broken by any external table** — rewrite in the same pass as A-5), `:141-144` the exception list, `:157-159` roadmap, `:36`, `:88-91`.
- `related_work.tex:221-222` (*"the evidence ceiling is D = 100, so no claim is made at differential grouping's n = 1000 scale"* — flatly false, **and** it is the paper's stated reason for not benchmarking the decomposition line, so the reviewer's next question is "why is there no DG/CC baseline?"); `:309-312`.
- `proposed_algorithm.tex`: `:682-683`, `:719` (*"No literature-copied numbers appear in any panel exhibit"* — stays true only because externals are supplement-only; verify), `:277`, `:244-246` (**no new tier is needed** — D=1000 falls inside the existing D≥100 tier, a genuine simplification — but "tier representatives" becomes incomplete), `:812-813`, `:793-802` (the memory paragraph: "about half a megabyte at D=100" — at D=1000 the three persistent D×D ISM matrices are ~24 MB and the eigendecomposition is O(D³)=10⁹; the MemoryError tracebacks confirm the D×D machinery really allocates), `:152-162` (the NP asymmetry — G-4), `:566-568`.
- `conclusions.tex`: `:27-29`, `:31-63` (add the LSGO movement; note `:56-57` reports "the overall descriptive aggregate is again the panel's best (2.80)" for CEC2013 — the parallel LSGO sentence reports a **non-best** aggregate, which is the intended honest contrast), `:82-83`, `:84-91` (**A-5**), `:126-129` (future work becomes partly present work; keep the `omidvar2014dg` citation, which is bound to LM-05's `evidence_ids`).
- `performance.tex:9` ("Across the three suites"), `:911-916` (*"relative standing improves from D=10 to D=50 and remains first at D=100"* — the sentence a reviewer will quote back; note the CEC2017 trend 2.88, 2.50, 2.21, 2.34 is **already dipping at D=100** and LSGO extends the dip), `:953-964` ("two of the three suites" → "two of the four"), `:821-822` (the cost curve, §D-5).
- **`main.tex:213-227` `\supplementary{}`** — add the "(S7)" clause, change "S1--S6" → "S1--S7", fix "all three suites" → four, extend the S2 clause. **Expect the documented reflow trap to fire** (§I).
- `main.tex:261-270` Data Availability (three-suite harness enumeration; the LSGO release name), `:289` upstream-terms sentence (needs the LSGO suite's own upstream licence terms named).
- **`cover_letter.md` + `cover_letter.tex`** (`:5`, `:55`) — cross-checked by `validate_document_consistency` check 2; `cover_letter.pdf` is one of the 15 tracked files; claim CL-02 pins the letter's novelty summary to the headline family-panel result. Edit both in step.

> **Authoring rule:** LaTeX and regex are authored with `Write`/`Edit`, **never a bash heredoc** — heredocs collapse `\\` → `\` and have already shipped literal "oindent"/"imes" into a released PDF. Also: `main.tex`, all five sections and `supplementary.tex` currently contain **zero** `\texttt` (159 stripped 2026-07-24). Do not reintroduce it.

---

### 5.5 — Register and manifest updates

`artifact_binding.csv` (61 rows, 16 columns) — one row per new exhibit; **`validate_artifact_labels.py` resolves every `manuscript_label` against `\label{}`s reachable from the two document roots** and caught 52 of 59 rotted rows at the 2026-07-22 review. `table_figure_source_map.csv`; `citation_usage_map.csv`; `citation_role_map.csv`; `captions_registry.md`; `cross_format_consistency.csv` (regenerate — currently 615 rows / 0 FAIL, and **five recorded counts disagree** across the freeze manifest (601), `PAPER_REVIEW_PROMPT` §1.5 (599), §1.5.0-K(d) (599), §1.5.6 (596) and `PAPER_BUILD_PROMPT` §15.0 (577); fix all five and add the standing note that the count is a snapshot).

`reproducibility_manifest.json` and `submission_package_manifest.json` — extend to **name the second release without dropping the first**.

---

# §I. PHASE 6 — Build and gate sweep

**Objective.** Four artifacts rebuilt reproducibly; eleven gates green twice.

**Entry criteria.** Phase 5 exit.

**Exit criteria.** Two consecutive identical green sweeps; all artifact hashes bit-identical across a double build.

**Build order.** generate tables → generate figures → `generate_word_sources` for T17/SA05–SA09 → `build_supplementary.py` → `build_pdf.py` (runs `validate_build_hygiene.py --logs-only` as an M-001 self-gate) → `build_docx.py` and `build_docx.py --supplementary` → cover letter (two-pass).

**Epochs — the recorded trap.** PDF `SOURCE_DATE_EPOCH=1783468800` with `FORCE_SOURCE_DATE=1`. DOCX `SOURCE_DATE_EPOCH=1783641600`. **A persisted shell variable carrying the PDF epoch silently yields a non-reproducible DOCX that still passes every gate.** Build the DOCX in a shell where the variable is explicitly set to 1783641600, and **verify the two DOCX hashes twice** before trusting `check_manifest`.

**Predicted failures, with their mechanisms — budget iterations for each:**

1. **`validate_cross_format_parity` `no_ablation_scan` on the MAIN PDF.** `:589` runs `re.search(r"(?m)^\s*S6[.\s:]", pdf_text)`; the main must have `not s6`. The `\supplementary{}` paragraph ends `… S6.5, S6.6, and S6.7 (S6).` and the source carries an explicit warning that lengthening the opening sentence reflows it. **After every `\supplementary{}` touch: rebuild the main PDF and run this gate before any other.** Fix by rewording to keep the S6.x run mid-line (e.g. move the trailing "(S6)" earlier), not by shortening the S7 clause.
2. **`validate_build_hygiene`** — Overfull `\hbox` > 2.0 pt in *either* log. Two likely sources: the reworked `tab:protocol`, and the reflowed `\supplementary{}` paragraph. Current state is zero overfull boxes and that is the bar.
3. **`validate_document_consistency`** check 1 — supplement inventory. `:97` counts `^\section{...}` (now 7); `:111` parses `\(S(\d+)\)` from `\supplementary{}`; `:116/121/128` require contiguity from S1, `max(label) == count`, and any "S1--SN" range to agree. Note this validator's expected terminal state is **exit 2 (author-pending)**.
4. **`validate_cross_format_parity` `table_inventory`** — if T17 is not in `_RESULTS_TEX_IDS` the DOCX renders a raw word_sources dump instead of the frozen `.tex` formatting (§A-9).
5. **`validate_docx` `table_count_vs_source`** — `source_expectations()` counts table envs + longtables + standalone tabulars from the flattened `.tex` and must equal the `w:tbl` count.
6. **`validate_provenance_claims`** — run with `--self-test`. Confirm empirically that the `lsgo-rel-*` bundle name does not enter `release_universe`'s superseded set (§A-2). `check_change_register()` also fails on any `CR-\d{4}` cited in prose but absent from the register, and requires C006 and M038 to stay registered.
7. **`audit_manuscript.py`** — unknown AN-* BIND ids; `REVIEW_PATTERNS` flags "'validat\*' + CEC2013 in same paragraph" and "'independent' + suite words in same paragraph" (LSGO prose trips both unless worded carefully); `BLOCKED_PATTERNS` hard-blocks "state-of-the-art" and "best algorithm" — precisely the vocabulary an honest MOS sentence attracts (H4). Accepted baseline is `blocked_wording_hits = 2` (both negations of "state-of-the-art").
8. **`validate_evidence_bindings`** — every numeric token in BIND-annotated visible text must appear identically in **both** PDF and DOCX. Every changed count (schedule rows, file counts, cell counts) is a cross-format obligation. Ticket M-029 previously needed a dedicated pass to clear 20 such failures.
9. **`validate_citation_controls`** C1–C5 against the four new keys.
10. **`validate_artifact_labels`** — every new exhibit's row must resolve.
11. **`check_manifest.py`** — N/15 until Phase 7.

**Also re-measure:** B1 pages and B2 words by CR-0008's own method (`pdftotext`), and the DOCX separately — its text measure is 9.0 % wider (9,638 vs 8,845 twips, recorded deviation D-4), so its page count moves differently from the PDF's. Supplement is expected to go ~56 pp → ~64–65 pp (back to its pre-compaction size); no MDPI supplement page cap applies. `supplementary.docx` grows ~0.7–1.0 MB for the two rasterised grids.

---

# §J. PHASE M (optional, parallel) — the `block_size = 10` mechanism cell

**Objective.** Convert the campaign's largest liability into its scientific contribution.

**Entry criteria.** Author authorisation at the GO/NO-GO gate. Can start the moment Phase 1 completes, in parallel with Phases 2–6.

**Cost.** One dt-gsk LSGO leg at the shipped default (15 function-cells × 25 runs = 375 runs); at the measured ~1,696 s/run under the campaign's parallelism that is roughly the same wall-clock as the leg now finishing.

**Value.** It answers, with data, the one question every reviewer will ask about H2: *what did the override buy?* It turns "DT-GSK placed mid-pack at D=1000" into "a dimension-tiered design fails outside its calibrated tier range, and the linkage-block rung is the one that runs out" — a falsifiable finding, the natural bridge to the decomposition future work at `conclusions.tex:126-129`, and the reason IN-04 exists.

**Two acceptable dispositions:**
- **(a) Recommended.** Keep block_size=50 as the primary LSGO cell (structure-matched, disclosed) and report block_size=10 as the mechanism contrast in S7.
- **(b) Cleanest for the config claim.** Make block_size=10 the *primary* LSGO cell so the "one hash-frozen configuration" sentence survives verbatim in all three places, PR-08 and LM-07 become unnecessary, CN-02 needs no carve-out, and the reviewer never sees the proposed algorithm receiving a suite-matched parameter its competitors did not get. The block_size=50 run becomes a disclosed sensitivity cell. This is the strictly safer integrity posture and costs the same compute.

**If Phase M is declined**, H2's disclosure must additionally concede that the override's effect is **unquantified** — which is honest but weaker, and invites the reviewer to ask for exactly this run.

---

# §K. PHASE 7 — Re-freeze, tag, DOI

**Objective.** A defensible, auditable new frozen state.

**Entry criteria.** Phase 6 exit (two green sweeps).

**Exit criteria.** `check_manifest` 15/15; all four manifests consistent; new tag; new Zenodo DOI version.

**Steps.**

1. **Reconcile the three "authoritative" commits.** Today `main_manuscript_freeze_manifest.json` anchors `abd2fa2f2`, the FINAL tag `dtgsk-submission-v1.0-2026-07-25` resolves to `a621c45b3`, HEAD is `cf5083bb7`, and `submission_package_manifest.json` records `abd2fa2f2`. Three commits described as authoritative in three places, cross-checked by no gate. Set the freeze anchor and the package manifest to the **same** new commit; record `a621c45b3` + the v1.0 tag as superseded.
2. **Re-mint `main_manuscript_freeze_manifest.json`** — all 15 files, **both `sha256` and `bytes`** (`check_manifest.py:61-62` gates both). Set `scientific_content_status` to a re-opened/re-frozen value; it **cannot** remain `FROZEN_FOR_SUBMISSION` through a scope change. Write a `freeze_statement` that — unlike every prior pass, all of which asserted the mint *"alters no reported number, rank, p-value, equation, figure"* — **explicitly records the re-opening, the fourth suite, the CR-0019 authority, the unfavourable finding, and the second release.** Rewrite `validator_outputs_at_freeze` wholesale.
   > **Mechanics: this manifest is CRLF with 2-space indent. Edit it byte-surgically. `sed -i` and `Path.read_text()/write_text()` normalise to LF and break every hash.**
3. Update `reproducibility_manifest.json` and `submission_package_manifest.json`; bump `manuscript_version_id` from v1.0.
4. Close `_pending_refreeze.json` against its exit criteria; move the eleven phase-gate rows back to FROZEN with fresh exit evidence and a Phase-12 page-count row.
5. **Author** commits, tags `dtgsk-submission-v1.1-<date>` (retaining v1.0 as historical), pushes, and cuts a new GitHub Release so Zenodo issues a **new DOI version**. **Do not re-point the existing DOI at changed content.**

---

# §L. The page-and-word budget, concretely

**Ruling (§A-8): B2 words is binding; B1 pages is not.**

| Metric | Cap (CR-0008) | Measured now | Headroom |
|---|---|---|---|
| **B1** main text incl. exhibits, excl. references + back matter | 40 pp | **37 pp** (DT-GSK.pdf is 41 pp total; back matter p.38, References p.39) | **~3 pp** |
| **B2** words | 20,000 | **~19,370** (pypdf, pp 1–37); CR-0008's own `pdftotext` measure of the 2026-07-22 build was 19,536 | **~460–630** |

**LSGO cost:** minimum ~1,300 tokens (subsection 550 + captions 140 + `tab:protocol` 45 + setup prose 180 + abstract 25 + intro 45 + related work 30 + proposed_algorithm 120 + discussion 130 + conclusions 200); realistic **1,700–1,900** with proper hedging.

**Deficit: ~700–1,400 words.** Any plan that reasons about *pages* concludes LSGO is affordable and then blows the word cap silently, because the word count does not appear in the build log.

**Harvest ledger — all in `performance.tex`, all supplement-eligible under §1.5's own overflow rule:**

| Lines | Content | Tokens | Verdict |
|---|---|---|---|
| **216-311** | Long `\paragraph{Statistical protocol.}` — **substantially duplicated** by the shorter same-named paragraph at `:403-424` (~181 tokens). Two paragraphs with the same name in the same section. | **~846** | **Harvest ~600 to S5.** Best single move: pays for the whole LSGO subsection, touches no result, and removes a genuine duplication defect. |
| **547-582** | "Robustness of the rank statements" | ~329 | Harvest |
| **166-188** | Budget-crossing controlled-cell narrative — already fully documented in `benchmark_protocol_audit_part2.md` §7.5 | ~190 | Compress to two sentences + pointer |
| **842-866** | `tab:runtime` float — its numeric range is already stated in prose at `:821-822` and `:832-834` | ~102 | Migrate the float, keep the prose |
| *456-492* | *Cell-by-cell Holm p-value enumeration* | *~259* | **Do not cut** — bound to negative_findings 1/3/5/6; cutting weakens the honesty posture |
| *752-774* | *F26 unfavourable-case discussion* | *~156* | **Do not cut** — honesty-bound |

**Available without touching any result: ~1,467 tokens. Target harvest: ~1,000–1,100.**

**If that is insufficient after measurement, raise CR-0021** superseding CR-0008's B2 cap, with a measured page count and `pdftotext` word count. Note the constraint direction: §8.6 says *"When the Section 1.5 page limit binds, migration to the supplement is the only permitted relief valve"*, and CR-0008 forbids shrinking exhibits (SE-005/SE-013 require the opposite). Also update `phase_04/page_budget.md` §2 with the supersession block.

**Corollary for exhibit allocation:** figures are cheap (a rank bar chart ≈ 0.35 page and ~60 caption tokens), prose is expensive. **One compact table + one figure with a tight caption in the main text; all reasoning to S7.**

---

# §M. Risk register (severity-ordered)

| # | Risk | Sev | Trigger / evidence | Mitigation |
|---|---|---|---|---|
| **R1** | **The `.prebugfix` defect invalidates four comparator cells.** atmals-gsk F8/D1000 moved +29.6 % under an unnamed mid-campaign fix; only atmals-gsk and egsk (the last two, 07-23/24) carry `.prebugfix` files; gsk/agsk/apgsk/fdb-agsk ran 07-22/23 and were never re-run. If affected, the six-algorithm ranking underpinning the entire analysis is wrong and no statistics repair it. | **Critical** | Phase 0C-1 | Answer before anything else. Automatic NO-GO if positive and re-run is unaffordable. |
| **R2** | **Undisclosed asymmetric advantage to the proposed method.** `configs/dtgsk_cec2013lsgo.yml` gives DT-GSK alone `linkage_block_size 905/1000 → 50` (benchmark group-structure knowledge) while six comparators run defaults. Falsifies three published sentences. No existing gate can detect it — the override travels through `DTGSKConfig`, so `_dt_profiles.py`'s hash `7baadf228d356394` stays valid and the byte-stability test still passes. | **Critical** | H2 | Main-text disclosure (H2) + `validate_profile_lock` entry (0H) + CR + Phase M contrast, or make block_size=10 the primary cell (§J-b). |
| **R3** | **The negative result is softened, buried, or omitted from the abstract** under submission pressure. | **Critical** | H1, H3 | Claim rows with `permitted_wording`/`blocked_wording` written **before** any prose; author sign-off is a blocking GO criterion (B5). |
| **R4** | **Staging data reaches a `.tex` file.** Every LSGO number is in `results/_run_all/` or project 05 today. **No gate re-derives table values from the release**, so this is undetectable after the fact. | **Critical** | H7 | Absolute prohibition on LSGO numbers in prose before Phase 2 exit; add a source-use assertion that every LSGO input path resolves under `_cec2013lsgo/`. |
| **R5** | **Self-refutation across four sites.** `conclusions.tex:85-89`, `introduction.tex:138-140`, `proposed_algorithm.tex:719`, `performance.tex:27-30` all pledge no literature-quoted comparators. | **Critical** | A-4, A-5 | Externals confined to supplement exhibits; all four sites rewritten in the same pass, owning the reversal (A-5) — never merely qualified. |
| **R6** | **Cross-implementation comparability.** Externals are published tables from three papers, different hardware, different environments, no per-run data; plus F3/F6/F10 ran a **different objective variant** than MOS's table. | **High** | A-6, EV-01 | Per-cell footnote + the 12-function restatement + the bounding sensitivity; SHADE-ILS as primary anchor; caveat block in S7.5. |
| **R7** | **Code identity across seven run commits.** All six comparator optimizer sources plus `threefry_rng.py` (+100/−19), `reference_rng.py`, `benchmark_adapter` and `runners` changed inside the campaign window; the LSGO objective changed twice. The LM-03 "one code base, one protocol, one harness" claim does not automatically hold. | **High** | 0C-2 | Golden-value regression at HEAD; `per_cell_run_commit` in the manifest; if it fails, re-run at a pinned commit or scope LM-03 to exclude LSGO and name the revisions. |
| **R8** | **Re-minting or superseding the primary release** voids the id at ten sites and trips every AUTHORITY block. | **High** | §A-2 | Second non-superseding release under `_cec2013lsgo/`; analysis bundle named `lsgo-rel-*` (verified not matched by `glob("rel-*")`); primary manifest untouched; `--self-test` after. |
| **R9** | **The evidence tree is already un-sealed** — 3,405 files on disk vs 3,403 in the manifest, while every gate reports green and the paper claims twice that no evidence file was hand-edited. | **High** | 0D-1 | Relocate + provenance sidecars + `check_manifest --strict-inventory` + deviation record. |
| **R10** | **Refactoring `phase6_run_analysis.py` perturbs the frozen suites.** Every headline number, including the abstract's 2.48, is transcribed from that bundle. | **High** | A-3 | Byte-identity diff of all three frozen suites as a blocking acceptance gate; extend by addition only; never touch `statistics.py`. |
| **R11** | **Silent wrong numbers, not crashes.** k=7-hardcoded Nemenyi (understates CD 1.166× at k=8, manufacturing separations); missing exact-Wilcoxon branch its own docstring promises (11.9× p inflation at n=15, one Holm rank unit); undefined LSGO `suite_ordinal` in the frozen BCa entropy list; `error`-column default producing all-NaN LSGO tables that typeset cleanly. | **High** | 0E-2/4/5, 0D-3 | Fix all four **before** any LSGO number is generated. Add a no-NaN assertion in the table generator. |
| **R12** | **B2 word cap breached silently.** ~500 words of headroom against a 1,300–1,900 word cost; the word count is not in the build log. | **High** | §L | Treat B2 as binding from the start; harvest ~1,000 words from the four donors; re-measure by CR-0008's own method after every rebuild. |
| **R13** | **The freeze re-opens but never cleanly re-closes** — some manifests on the new release, some on the old; some gates green, some stale. This has happened before (`_pending_refreeze.json` records "check_manifest 1/12 match"). | **High** | Phase 7 | Re-open `_pending_refreeze.json` with written exit criteria *before* touching source; do not re-mint until every gate is green twice. |
| **R14** | **dt-gsk cell promoted structurally incomplete** — four provenance files missing, no D905 summary, an unpromotable `skipped_runs.csv` recording 25 MemoryError skips, and an uncommitted config. Structurally the same defect that put apgsk CEC2017 into provisional Class C. | **High** | Phase 1 | Hard block on 375/375 + five provenance files; deviation record; commit the config. |
| **R15** | **Publishing on the partial subset.** F1–F6 includes DT-GSK's single strong cell (F4) and its 5-function omnibus is non-significant; restricting the six complete algorithms to F1–F5 moves agsk from rank 1 to rank 3. | **High** | H6 | Hard block; the preview is declared burned in the 0B pre-commitment. |
| **R16** | **Reflow trap on `\supplementary{}`** pushes "S6.x" to a PDF line start and fails `no_ablation_scan`. Documented in the source; the paragraph already ends on the triggering string. | **Medium** | §I-1 | Rebuild main PDF + run parity before any other gate, after every touch; reword mid-line rather than shorten the S7 clause. |
| **R17** | **Layout overflow.** A fourth `tab:protocol` column or the transposed 75-row S7 table exceeds `\textwidth`; the tempting fix (shrink) is forbidden. Current build has zero overfull hboxes and `OVERFULL_TOL_PT = 2.0`. | **Medium** | §H-5.4 | Transpose or split `tab:protocol`; `\resizebox{\textwidth}` on wide tables; clean-aux rebuild + grep for "Overfull". |
| **R18** | **Table-id plumbing.** T17 absent from `_RESULTS_TEX_IDS` renders a raw word_sources dump in Word instead of the frozen formatting — a parity defect no gate names clearly. | **Medium** | §A-9 | Register T17 in all six places in one commit. |
| **R19** | **Closed citation corpus reopened under deadline pressure**, creating an incentive to invent bibliographic data. No key exists for the LSGO suite definition, MOS, SHADE-ILS or DECC-G; `validate_citation_controls` C2 requires an evidence card on disk. | **Medium** | 0F | Author supplies four PDFs; four hand-written cards; **never fabricate a DOI, page, or date**. If a source cannot be verified, drop that baseline rather than cite it. |
| **R20** | **Vacuous verification records** — every LSGO cell ships `verdict: CONSISTENT` with `functions_checked: 0`, while the supplement advertises verification records as checksummed evidence. | **Medium** | 0D-2 | `NOT_VERIFIED`/`NO_REFERENCE`, or wire the verifier to the vendored tables. Disclose either way. |
| **R21** | **Unvalidated benchmark port.** No cell-by-cell LSGO validation exists, versus the CEC2017 precedent of 116/116 cells agreeing to 2.2e-14. A reviewer may conclude the gap is our benchmark, not our algorithms. | **Medium** | LSGO-07 | Validate against the checkable probes (MOS F1 Best/Mean = 0; F3 ≈1.7e-12; the full 15×5 DECC-G table), or state the gap symmetrically. |
| **R22** | **Cross-suite rank harmonization** in a later editorial pass — incommensurable on dimension, budget, run count, endpoint semantics, block count and panel cardinality. Note ties, which drive the CEC2017 tie-correction (C = 0.890 at D10), are **entirely absent** on LSGO (tie_correction = 1.000, 0 tied blocks). | **Medium** | SM-16 | Prohibition in the amendment **and** in `blocked_wording`; deliberately mint no `AN-RANKAGG-LSGO`, so there is no artifact to aggregate. |
| **R23** | **DOCX epoch trap** — a persisted shell variable yields a non-reproducible DOCX that still passes every gate. Has already occurred. | **Medium** | §I | Explicit epoch in the command; double build; compare hashes twice before trusting `check_manifest`. |
| **R24** | **DOI/version mishandling** — the archived record the Data Availability Statement cites no longer matches what is submitted. | **Medium** | Phase 7 | Bump `manuscript_version_id`, new tag, new Release, **new DOI version**; never re-point the existing DOI. |
| **R25** | **Runtime comparison leaks in.** CR-0013–CR-0018 changed per-algorithm speed by different factors mid-campaign (1.718× / 1.440× / 1.205×) and cells span 07-22 to 07-26. | **Medium** | §D-5 | No cross-algorithm LSGO runtime, reported explicitly as a policy. Add DT-GSK's own D=1000 point as single-algorithm, non-comparative. |
| **R26** | **~90 Holm-significant run-level tests read as overwhelming to a casual reader and as noise to a competent one** (A12 exactly 0.000/1.000 in 24 of 30 measured cells; 24 of 30 raw p at the n=25 floor 1.308e-05). | **Medium** | A-10 | Pre-written framing: at D=1000 run-level significance certifies only that the algorithms differ, which is not in doubt; direction and the 15-block function-level layer carry the information. Report magnitude labels with an explicit non-discriminating note. |
| **R27** | **Missing 1.2e5-FES milestone.** The grid has no E120000 (nearest E150000, 25 % high), so the community-standard three-milestone table cannot be built at its first column. | **Low** | 0D / S5.4 | Disclose the substitution in the caption and S5. Do **not** re-run — that would invalidate all six completed comparator legs. |
| **R28** | **Convergence panels carry 7 curves while tables carry 8–9 columns.** | **Low** | §H-5.2 | Caption note + `cec2013lsgo_missing.log`. **Never synthesise an external curve from a summary row.** |

---

# §N. Decisions only the author can make

Each is blocking. None can be made by an agent. Numbered for sign-off.

| # | Decision | Why it is the author's | Recommended | Blocks |
|---|---|---|---|---|
| **AD-01** | **Include LSGO, or defer to a companion paper?** | Career/publication strategy against a frozen, gate-green, submission-ready manuscript. | **Include** — but only if AD-02 and AD-03 are also yes. The three standing objections to the current paper (family-only panel, no external baseline, D≤100 ceiling) are all conceded in `conclusions.tex:84-86`; LSGO answers all three at once, and H8 means silence is no longer neutral. | Everything |
| **AD-02** | **Will the negative headline go in the ABSTRACT?** | It changes what the paper claims. | **Yes.** If no, take Branch B. | GO criterion B5 |
| **AD-03** | **Will the `linkage_block_size` override be disclosed in the MAIN text?** | It concedes a per-suite advantage to the proposed method and falsifies three published sentences. | **Yes.** If no, take Branch B — this is the single reddest flag in the expansion. | GO criterion B5 |
| **AD-04** | **External baselines: all three, or none?** | Reverses a written scoping decision (`PAPER_REVIEW_PROMPT` §1.5.4) and a Class-D prohibition. | **All three**, supplement-only exhibits, main-text sentence. Omitting SHADE-ILS (the stronger, more comparable result) while including MOS is indefensible; omitting DECC-G, which is committed in this repo, is checkable cherry-picking. | Phases 0F, 2, 5 |
| **AD-05** | **Run Phase M (`block_size = 10` contrast)? If yes, disposition (a) or (b)?** | ~375 additional runs of compute and a scientific-framing choice. | **Yes, disposition (b)** if schedule allows (block_size=10 primary, 50 as sensitivity) — it retires R2 entirely; otherwise **(a)**. | R2 severity, S7 content |
| **AD-06** | **Supply four reference PDFs** (CEC2013 LSGO suite definition **mandatory**; MOS, SHADE-ILS, DECC-G if AD-04 = all three), with verified bibliographic data. | Metadata may never be reconstructed from memory or the web. | Start hour 1 — the only externally-blockable item. | GO criterion B6 |
| **AD-07** | **Approve CR-0021 raising the B2 word cap**, or accept the §L harvest (~1,000 words migrated from `performance.tex` to S5). | CR-0008 states any build exceeding the caps requires a further change request. | **Accept the harvest** — `performance.tex:216-311` is duplicated by `:403-424`, so the migration also fixes a real defect. Hold CR-0021 in reserve. | GO criterion B7 |
| **AD-08** | **If the code-identity attestation fails (0C-2): re-run the affected cell(s) at a pinned commit, or scope LM-03 to exclude the LSGO leg?** | Compute versus a narrowed attribution claim. | Re-run if one cell; scope-and-disclose if several. | GO criterion B2 |
| **AD-09** | **If the `.prebugfix` defect touches the four earlier comparators (0C-1): re-run four cells (>100 h) or defer the suite?** | Large compute versus scope. | Defer. Four re-run cells plus the dt-gsk leg is a second campaign. | GO criterion B1 |
| **AD-10** | **`skipped_runs.csv`: promote under a new file class, or exclude with a recorded exclusion?** | It is a production-deviation record on the proposed method's own cell. | **Promote**, with an S5 disclosure sentence. Excluding it invites the "failed runs were repeated until they succeeded" inference from a file a reviewer can find in git history anyway. | Phase 1 exit |
| **AD-11** | **Commit `configs/dtgsk_cec2013lsgo.yml`** (currently uncommitted `overwrite: true → false`) and all subsequent work. | The agent does not commit, tag or push. | Commit before promotion so the promoted `run_config.json` has a committed counterpart. | Phase 2 |
| **AD-12** | **Version and DOI strategy: v1.1 or v2.0?** | A scope change adding a benchmark suite is arguably major. | **v1.1** if Branch B, **v2.0** if Branch A — Branch A changes what the paper claims. Retain `dtgsk-submission-v1.0-2026-07-25` as historical either way. | Phase 7 |

---

## Critical path and indicative schedule (Branch A)

```
NOW ──┬─ 0A governance authority ..................... 0.5 d
      ├─ 0B PRE-COMMITMENT ....... HARD 20 h DEADLINE  0.5 d  ← do tonight
      ├─ 0C data forensics (0C-1 may abort campaign) .. 1.0 d
      ├─ 0D evidence integrity ....................... 0.5 d
      ├─ 0E tooling (4 parallel lanes) ............... 1.5 d
      ├─ 0F CITATION PDFs ......... author-dependent .. ? d   ← long pole
      ├─ 0G/0H/0I ................................... 0.5 d
      └─ [dt-gsk run: ~20 h remaining, 150/375]
                 │
Phase 1 cell closure ............................. 0.5 d  (blocks on run)
Phase 2 promotion + LSGO release mint ............ 0.5 d
Phase 3 analysis + byte-identity guard ........... 0.5 d
─────────── PHASE 4  GO / NO-GO ───────────
Phase 5 prose + exhibits + registers ............. 2.0 d
Phase 6 build + 11 gates × 2 sweeps .............. 1.0 d  (+ reflow iterations)
Phase 7 re-freeze + tag + DOI .................... 0.5 d
                                    ─────────────
                    Branch A total  ≈ 6–7 working days after the run lands,
                                       IF 0F lands in parallel.
                    Branch B total  ≈ 1 working day.
```

**The critical path is not the compute.** It is (1) the citation PDFs (AD-06), (2) the author's honesty sign-off (AD-02/AD-03), and (3) the `.prebugfix` forensics (0C-1). All three can be resolved **today**, while the run is still executing. Every hour spent on Phase 0 is an hour removed from the post-run critical path — and Track 0B in particular has a hard expiry the moment F7–F15 land.