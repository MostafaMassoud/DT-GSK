# Production deviation record

Two parts. **Part A (D-1 … D-4)** records typesetting deviations — how the
production toolchain differs from the venue template. **Part B (D-5 … D-7)**
records evidence-production deviations — anything about how the result banks
themselves were produced that a reader reproducing them would otherwise trip
over. Part B was opened 2026-07-28 when the CEC2013LSGO banks were adjudicated
for promotion.

---

# Part A — LaTeX class and Word geometry

Date: 2026-07-22. Opened to close panel tickets **SE-031** (Word page geometry),
**SE-032** (Word deviation record), and **SE-048** (vendored class), which found
that the production toolchain deviates from the venue template in four ways, none
of which was written down anywhere. The defect those tickets identify is the
*absence of a record*, not the deviations themselves.

Nothing here changes a reported number, a claim, an equation, a figure, or the
optimizer core. Each item states what the venue template does, what this
repository does instead, the measured size of the gap, and the disposition.

---

## D-1. Vendored MDPI class is 2020-dated

- **File:** `papers/Definitions/mdpi.cls`, `\ProvidesClass{Definitions/mdpi}[08/17/2020 MDPI paper class]`
- **Deviation:** the class predates the current MDPI template.
- **Disposition:** **ACCEPTED, author decision at submission.** MDPI regenerates
  the typeset article from the submitted sources with its own current class, so a
  dated vendored class affects only the author-side proof PDF. Refreshing it would
  invalidate the 15-file byte freeze for no scientific gain. The author should take
  the current class from the *Algorithms* author centre at submission time if the
  venue requires it.

## D-2. Submit-mode line numbering — **RESOLVED 2026-07-22, deviation removed**

> **This deviation no longer exists.** `\let\linenumbers\relax` is commented out in
> both `papers/main.tex` and `papers/supplementary.tex`, so MDPI submit-mode
> left-margin line numbering is **active** in the shipped review copies.
>
> The concern that motivated keeping it suppressed — that `lineno` margin numbers
> would leak into the `pdftotext` layer and corrupt `validate_cross_format_parity`
> — was **tested and did not occur**: with line numbering on, page 10 of
> `DT-GSK.pdf` yields **0** stray line-number tokens on extraction, the page count
> is unchanged at 40, and the parity gate passes. The gate's PDF side is a
> squash-*containment* check, so additional margin tokens cannot displace the
> values it looks for.
>
> The original analysis is retained below for the record.

- **Where:** `papers/main.tex:15` and the matching line in `papers/supplementary.tex`
  — `\let\linenumbers\relax`.
- **Venue behaviour:** the MDPI class issues `\linenumbers` in `submit` mode, giving
  the left-margin line numbers reviewers use to anchor comments.
- **Why it was suppressed:** the in-file comment records the reason as avoiding
  `accept` mode, which needs a journal logo file this repository does not ship.
  That rationale is about `accept` mode and does **not** justify disabling line
  numbers in `submit` mode; SE-048 is right that the two were conflated.
- **Why it is nonetheless retained here:** enabling `lineno` injects margin numbers
  into the PDF text layer. `validate_cross_format_parity` compares
  `pdftotext`-extracted PDF text against DOCX text row by row (582 rows, 0 FAIL);
  interleaved line numbers would corrupt that extraction and the parity gate would
  no longer be measuring content agreement.
- **Disposition:** **DEFERRED TO THE AUTHOR — reviewer-facing choice.** This is a
  presentation decision for the review copy, not a correctness question. To enable:
  delete `\let\linenumbers\relax` from both `main.tex` and `supplementary.tex`,
  rebuild, and expect `validate_cross_format_parity` to require a line-number
  filter in its PDF extraction step before it will pass again.

## D-3. Submit-mode running header and copyright/license block are suppressed

- **Where:** `papers/main.tex:19` — `\AtBeginDocument{\lhead{}}`; and two local edits
  inside `mdpi.cls` made in commit `574e2deb4`, which replaced the
  "Submitted to <journal>" footer text and the submit-mode CC-BY copyright/license
  block with comments reading "(author request)".
- **Deviation:** the class's submit-mode branding does not appear.
- **Disposition:** **ACCEPTED, author request, now recorded.** These were author
  decisions taken during the R5/R6 review rounds and were previously visible only in
  the git history of a vendored third-party file — which is exactly how they escaped
  every gate. MDPI applies its own branding at typesetting. The right-hand
  page-number header is retained.

## D-4. Word text measure is ~9% wider than the LaTeX class

Measured, not estimated:

| | page size | side margins | text width |
|---|---|---|---|
| LaTeX (`mdpi.cls`, `submit`) | A4, 210 mm | 2.7 cm each | **156.0 mm** (8,845 twips) |
| Word (`word/reference.docx`) | A4, 11,906 twips | 1,134 twips each | **170.1 mm** (9,638 twips) |

Ratio 9,638 / 8,845 = **1.090**, i.e. the Word line measure is 9.0% wider.

- **Consequence:** line breaks, and therefore page breaks, differ between the two
  deliverables. Content is unaffected — the parity gate compares text, not layout.
- **Why it is not simply corrected:** setting `w:pgMar` to 1,531 twips would match
  the class, but `_PORTRAIT_TEXT_TWIPS = 9638` in `build_docx.py:1373` drives the
  column-fitting logic for the dense numeric tables, and `_TBL_CELL_MARGIN` was
  already reduced from Word's ~108-twip default specifically to reclaim width for
  the 28-column Wilcoxon–Holm table. Removing 9% of the measure pushes those tables
  back into per-cell wrapping — degrading the same legibility that SE-005 and SE-013
  were opened to protect, and which SE-018 forbids resolving by shrinking exhibits.
- **Disposition:** **APPROVED DEVIATION.** The DOCX is a convenience and
  parity-checking deliverable; MDPI typesets from the submitted sources. The gap is
  recorded here with its measurement so it is no longer silent. If a future revision
  wants the geometries unified, both `w:pgMar` in `papers/scripts/make_reference_docx.py`
  and `_PORTRAIT_TEXT_TWIPS` must change together, and the dense supplement tables
  must be re-checked for wrapping afterwards.

---

## Verification

`papers/scripts/validate_docx.py` and `papers/scripts/validate_cross_format_parity.py`
are unaffected by every item above: they check content agreement, not page geometry
or margin decoration. The measurements in D-4 are reproducible with:

```bash
python -c "import zipfile,re; x=zipfile.ZipFile('papers/DT-GSK.docx').read('word/document.xml').decode(); print(re.search(r'<w:pgSz[^>]*/>',x).group(0), re.search(r'<w:pgMar[^>]*/>',x).group(0))"
```

---

# Part B — Evidence production (CEC2013LSGO banks)

Date opened: 2026-07-28, before promoting the CEC2013LSGO family banks into an
evidence release. Three items were adjudicated. **None of them contaminates a
reported value**, and the adjudication is recorded here in full precisely
because two of them look alarming until you check them against the raw data.

## D-5. BUG-RESUME-01 — truncated summary tables (`*.csv.prebugfix`)

**What happened.** Four `*.csv.prebugfix` files sit beside the atmals-gsk and
egsk CEC2013LSGO summaries. They are snapshots taken before a defect in
`src/gsk_family/runners/output.py::write_summary_tables` was fixed at commit
`e7f4a1cc1` (2026-07-25 17:58). The defect had two branches: on a **resume**,
the per-dimension writer (a) opened the summary file in `"w"` mode and wrote only
the functions executed in that session, erasing untouched functions, and (b)
summarised a partially-resumed function over the session's runs alone — e.g. 12
runs reported as if they were the full 25.

**Why it looks alarming.** The atmals-gsk F8/D1000 *mean* moves **+29.6%** across
the fix (4.179e13 → 5.415e13), with the worst-case value more than doubling.

**Adjudication: DERIVED-ONLY. No primary datum was ever affected.**

- `write_summary_tables` writes only `{optimizer}_{suite}_D{dim}.csv`. It never
  opens `per_run.csv`. The per-run bank is written by a separate function
  (`write_per_run`) and is a **merge**: `run_experiment.py` reads the existing
  rows off disk and appends the session's rows before writing.
- The pre-fix F8/D1000 block reproduces exactly (all five statistics, rel ≤ 1e-9)
  the statistics over **runs 14–25** of today's `per_run.csv` — a contiguous
  suffix. Its Best and Worst are literal, unchanged rows still in that file. The
  old summary was a *subset view* of data that was already correct.
- Recomputing all five statistics directly from `per_run.csv` for **all seven
  banks × all 15 cells**: Best, Median and Worst deviate from the current
  summaries by **exactly zero** in every cell of every bank. Residual Mean/SD
  deviation is ≤ 8.2e-9 relative — the documented `%.10e` round-trip artifact.

**Disposition.** The `.prebugfix` files are stale views, fully recomputable from
data that never changed. No re-run is owed. Pinned by
`tests/regression/test_resume_summary_not_truncated.py` (added 19 minutes after
the fix). The four banks that were **never** re-run (gsk, agsk, apgsk, fdb-agsk,
produced 2026-07-22/23 under pre-fix code) are equally unaffected — but for the
recomputation reason alone, not the one first recorded here.

**Correction (2026-07-28).** This entry originally argued that those four banks
were each written in a *single session*, so neither defect branch was reachable.
**That argument is false.** The session logs in each summary directory show that
EVERY bank spans multiple runner sessions: gsk 3, agsk 2, apgsk 2, fdb-agsk 3,
atmals-gsk 4, egsk 2, dt-gsk 2. All seven therefore had resume exposure. What
actually establishes correctness is the recomputation: for all seven banks, the
published per-dimension summary agrees with its own `per_run.csv` to a worst
relative deviation of 4.6e-11 — the `%.10e` round-trip artifact and nothing
more. The conclusion stands; the original reasoning did not, and is corrected
here rather than quietly dropped.

## D-6. `skipped_runs.csv` — a recovery record, not a data gap

**What it is.** `results/_run_all/dt-gsk/cec2013lsgo/summary/skipped_runs.csv`,
444 lines. The line count has been quoted as "~443 skipped runs". That is a
**line-count artifact**: the file holds **25 CSV data rows**, because the
`traceback` column embeds multi-line Python tracebacks.

**What the 25 rows are.** All 25 are the single cell **F1 / D1000, runs 1–25**,
each a `MemoryError` raised inside a `concurrent.futures` process worker
(allocations of 1.10–38.1 MiB — pool exhaustion, not one oversized request).
Those attempts produced **no** `per_run.csv` rows; the cell was re-run to
completion about two hours later, and every F1/D1000 seed in `per_run.csv`
matches its counterpart in `skipped_runs.csv` exactly — zero mismatches. The
recovery was protocol-faithful, not a reseeded substitute.

**Completed-run counts, dt-gsk CEC2013LSGO:** 25 runs in every one of the 15
cells (F13/F14 at D=905, the rest at D=1000) — **375/375**. No cell in any of the
seven banks has fewer than 25 completed runs.

**Disposition.** The file is promoted with the banks under the explicit file
class `deviation_record` and cross-referenced to this entry. Promoting the rows
it explains while deleting the file would leave a discoverable, unexplained gap;
keeping it costs nothing and answers the question in advance.

## D-7. Code-identity spread across the LSGO leg — OPEN verification debt

**The situation.** The seven CEC2013LSGO banks were produced across **six
commits** spanning 2026-07-22 → 2026-07-26, and the family optimizer cores were
edited *inside* that window by the acceleration campaign (`7e5a9a32e` touched
gsk/agsk/apgsk/fdb_agsk on 07-25; `dbd71499c` touched atmals_gsk/egsk the same
evening; two `_dt_core.py` commits landed between dt-gsk's F4 and F5 cells).

**Why this is not contamination.** Every one of those edits was engineered and
certified **bit-identical** (dead-copy elimination, buffer reuse, memory layout),
governed by CR-0013 … CR-0017, whose evidence includes full-budget hex
`best_fitness` identity checks — among them gsk, agsk and fdb-agsk on LSGO
D1000, and atmals-gsk and egsk on LSGO D1000. The standing 42-pin golden matrix
includes `cec2013lsgo | F1 | D1000` for all seven algorithms and is green.

**The two residuals, stated plainly rather than rounded away.**

1. **apgsk** is the one family member whose LSGO leg has no full-budget hex
   re-verification: CR-0013's full-budget LSGO checks cover gsk/agsk/fdb-agsk,
   and apgsk was covered at CEC2017 D100 plus the golden pin only.
2. **dt-gsk's own bank is internally split.** Cells F1–F4 (D1000) completed
   before the two `_dt_core.py` edits of 2026-07-25 evening; F5–F15 and the
   D905 cells ran after them.

Additionally, the "full-budget" hex identity checks were run at 300,000
evaluations against a production budget of 3,000,000 — a 10% trajectory prefix.
Any bit-identity break perturbs a trajectory immediately, so this is strong
evidence, but it is not a full-length replay.

**Disposition — DISCHARGED 2026-07-28.** Eight archived runs were re-executed
at HEAD (`5183f0b26` code state; campaign stopped, cores idle): one full-budget
(3,000,000 FES) run per algorithm, chosen to cover the load-bearing cases —
apgsk (previously the one member with no full-budget LSGO re-verification) and
BOTH dt-gsk code-version legs (F3 from the pre-edit F1–F4 leg, F12 from the
post-edit leg). Replays used the campaign path itself (`run.py`, unified seeds,
serial, numba_threads=1; dt-gsk through `configs/dtgsk_cec2013lsgo.yml` so the
22-entry linkage table applies). Comparison criterion fixed in advance:
`per_run.csv` stores best_fitness as `%.10e`, so bank agreement is
representation-exact at 11 significant digits, plus string equality of the
final `%.16g` gen_log checkpoint row (17 significant digits, i.e. float64
round-trip precision).

**Result: 8/8 PASS.** Every replayed seed matched its bank row and every
best_fitness reproduced exactly at both precisions:

| algorithm | cell | bank = replay |
|---|---|---|
| gsk | F12 run 1 | 1.3828640878e+09 |
| agsk | F12 run 1 | 8.0996926250e+07 |
| apgsk | F12 run 1 | 9.3914657773e+09 |
| fdb-agsk | F12 run 1 | 7.4629993606e+08 |
| atmals-gsk | F7 run 1 | 8.1966942344e+07 |
| egsk | F12 run 1 | 1.5648251791e+10 |
| dt-gsk (pre-edit leg) | F3 run 1 | 2.0546067019e+01 |
| dt-gsk (post-edit leg) | F12 run 1 | 3.2983517981e+05 |

The acceleration-campaign edits inside the banks' six-commit window are thereby
confirmed behavior-preserving at FULL production budget on this suite, closing
the 300k-prefix limitation noted above. The "one code base, one harness"
wording is safe for the LSGO leg, stated as: every bank reproduces bit-faithfully
(to full stored precision) under the code at `5183f0b26`. Replay artifacts and
the comparison report are retained in the session scratchpad
(`d7_replay/D7_REPLAY_REPORT.txt`); the procedure is re-runnable from the
commands recorded there.

## D-8. CEC2013LSGO bank labelling, provenance and hygiene (audit of 2026-07-28)

A full integrity audit of all seven CEC2013LSGO banks found **no defect in the
data**: 375 rows per bank (15 cells x 25 runs), correct native dimensions
(F13/F14 at 905), every one of the 2,625 runs terminating at exactly 3,000,000
NFEs, no non-finite or negative values, no cell whose 25 runs are identical, and
**seed identity across all seven algorithms for every (function, dimension, run)
- zero mismatches**, which is the property every paired test on this suite
depends on. Every published summary agrees with its own `per_run.csv` to a worst
relative deviation of 4.6e-11.

Four issues were found that are **not** data defects. Each is recorded with the
point at which it must be fixed, because three of them cannot be fixed in the
bank itself without hand-editing evidence files -- which this project does not
do.

### D-8.1 `verification.json` reports a vacuous `CONSISTENT` verdict

Every LSGO bank carries `"verdict": "CONSISTENT"` while its own `failures` array
holds 15 entries of `{"kind": "missing_reference", "hard": false, "message": "No
matching reference summary row found."}`. There is no GSK-family CEC2013LSGO
reference bank anywhere: `benchmarks/cec_reference_results/cec2013lsgo/` contains
only the external `decc-g`, `mos` and `shade-ils` tables. So `CONSISTENT` here
means "nothing was compared", not "matched a reference" -- and a reader or script
that trusts the top-level verdict field is misled in the most damaging possible
direction.

This is precisely the failure mode the pre-registered SAP addendum Section 11
forbids for CEC2020 ("verification.json entries without a reference table report
NOT_VERIFIED/NO_REFERENCE, never a vacuous CONSISTENT"). The LSGO banks predate
that rule and violate it.

**Disposition (EXECUTED 2026-07-28, release lsgo-rel-2026-07-28-ff1a046ef).** The verdict is corrected **at promotion**, by the promotion tool
writing `NOT_VERIFIED` with `reason: NO_REFERENCE` into the promoted
`verification.json`; the staging bank is left untouched. The writer in the runner
that produces the vacuous verdict must also be fixed so no future suite repeats
it. **Deferral lifted 2026-07-28**: the author stopped the campaign at a clean
cell boundary precisely to close these issues, so the writer was fixed before
resume -- `verification.py` now returns verdict `NOT_VERIFIED` with reason
`NO_REFERENCE` whenever zero functions could be compared and reference rows
were missing (hard failures still dominate). Pinned by the updated
`tests/unit/test_verification.py` no-reference test. The three completed
CEC2020 banks acquire the corrected verdict automatically when the resumed
campaign's finalize pass regenerates their verification.json (their
environment.json is preserved by the D-8.5 guard); the LSGO banks' verdicts
are still normalized at promotion, as originally recorded.

### D-8.2 The Ackley variant is absent from every bank's provenance

F3, F6 and F10 ran the TRANSFORMED Ackley chain (T_osz -> T_asy(0.2) ->
Lambda(10) -> ackley), which is the single most important non-comparability fact
about this suite: published MOS results were measured on the raw form. Yet no
bank's `phase0_protocol.json` mentions `ackley` or `variant` at all. The fact
lives only in prose, so someone reproducing from a bank's own provenance could
silently run the other variant and not know the results are incomparable.

**Disposition (EXECUTED 2026-07-28: benchmark_variant.json x7 in the promoted release).** The promoted provenance must carry the variant explicitly
(`ackley_variant: transformed`, with the three affected function ids named).
Recorded here so the promotion step cannot omit it.

### D-8.3 Non-promotable files in the summary directories

Each bank's `summary/` holds loose `*_log_*.txt` session logs (roughly seventy
across the seven banks), and the atmals-gsk and egsk directories additionally
hold the four `*.csv.prebugfix` files adjudicated in D-5. Neither file class
appears in the addendum Section 11 promotion list, so both would surface as
unlisted files under `check_manifest --strict-inventory`.

**Disposition (EXECUTED 2026-07-28: 70 logs excluded in-manifest; skipped_runs.csv + 4 .prebugfix promoted as deviation_record).** Logs are excluded from promotion with the exclusion recorded
in-manifest. The `.prebugfix` files are promoted under the `deviation_record`
file class, cross-referenced to D-5 -- they are the evidence for that entry, so
deleting them would remove the record that explains itself.

### D-8.4 dt-gsk ran with tuned optimizer options; the six comparators did not
**- OPEN, needs author attestation**

`run_config.json` shows `optimizer_options: {}` for gsk, agsk, apgsk, fdb-agsk,
atmals-gsk and egsk -- all six ran on module defaults. dt-gsk's bank records a
22-entry `linkage_block_size_by_dim` table (including `905 -> 50` and
`1000 -> 50`) plus `strict_profile_dims: true`.

This is consistent with the documented panel protocol -- comparators run their
published constants, DT-GSK runs its frozen tier-resolved configuration -- and the
same asymmetry exists on the frozen suites. What is specific to LSGO is that the
`905` and `1000` entries are values that exist for no other suite in this
project. **Whether those two entries were selected using CEC2013LSGO results is
a question the repository cannot answer**, and it is the first thing a referee
will ask, because the standing selection-exposure attestation (D-0020, six
full-panel candidate configurations) is scoped to CEC2017.

**RESOLVED 2026-07-28 by documentary evidence, not attestation.** The question
is answered by the config's own contemporaneous rationale and by the benchmark
definition, both checkable independently of any result.

`configs/dtgsk_cec2013lsgo.yml` records, in the comment block introduced with
the values themselves: *"block_size=50 is chosen to MATCH THE BENCHMARK'S
DECLARED GROUP STRUCTURE, not fitted to any observed result. No parameter search
was run."* That rationale is verifiable: CEC2013LSGO's own definition builds its
partially-separable functions from groups of 25, 50 or 100 variables -- F8-F11
are 20 groups x 50, and F13/F14 use 50-dimensional overlapping groups
(`benchmarks/cec_suite_python/cec2013lsgo/transforms.py`, `composite.py`,
`_numba.py:546`). 50 is therefore the suite's own structural parameter, not a
value fitted to performance. The same comment records the motive for adding the
two keys at all: without them D=905/1000 fall off the end of the shipped table
and `_resolve_linkage_block_size` falls back to block_size=10 with a warning --
one fifth of the problem's real interaction granularity.

**Timing, disclosed rather than glossed.** The values were introduced on
2026-07-24 (commit `4d5c8dad4`), and dt-gsk CEC2013LSGO results had existed in
the repository since 2026-07-21 (`a11641bde`). Strict outcome-blindness
therefore cannot be asserted: results were available when the keys were added.
What can be asserted, and is what the paper will say, is that the value follows
a stated structural rule tied to the benchmark's own definition, that the config
recorded this at the time rather than retrospectively, and that no parameter
search was run. This is weaker than blindness and stronger than an unsupported
claim; it is disclosed in the LSGO subsection alongside the existing
descriptive-after-inspection tier, which already absorbs inspection-informed
choices on this suite.

**No effect on the confirmatory layer's interpretation, in the conservative
direction.** The registered run-level paired layer (AN-PWRUN-LSGO-NATIVE) found
NO suite-level separation between DT-GSK and any comparator (across-function
exact p vs AGSK = 0.8469, Holm 1.0). A configuration choice that could only have
helped DT-GSK did not produce a win, so the finding is not inflated by it.

**Related reproducibility note.** dt-gsk's LSGO bank reproduces **only** under
`configs/dtgsk_cec2013lsgo.yml`. The seven-algorithm `configs/family_cec2013lsgo.yml`
carries no `optimizer_options`, so dt-gsk would fall back to `block_size = 10`
from the nearest configured dimension (240) and produce different numbers. Both
configs are now pinned by `scripts/validate_profile_lock.py`, including all 22
table entries.

## D-8.5 Zero-new-runs resume rewrote environment.json — hazard found and FIXED before it ever fired

**The hazard.** The runner's finalize block wrote `environment.json`
unconditionally. Re-invoking the identical command over a COMPLETED bank (the
normal resume idiom this project relies on) therefore replaced the bank's
production git commit with resume-time HEAD, set `statistics_basis` to null
(the session had no artifacts), and recorded the no-op invocation's wall time.
A null `statistics_basis` additionally disables the known-optimum hard checks
in later verification passes, which read the basis from this file. Adversarial
code-review confirmed the write was unguarded while `write_summary_tables` was
correctly guarded by `if artifacts:` — an asymmetry with no design rationale.

**Did it ever fire?** No. Every LSGO bank's `environment.json` still records
its original production commit (gsk `a1bb33497` … dt-gsk `62fc49b80`) and a
non-null basis, and the three completed CEC2020 banks were finalized once each
by the (stopped) campaign itself. The hazard was found by audit while planning
the campaign resume — one resume command away from firing seven times.

**Fix (2026-07-28, before any resume).** `environment.json` is now written only
when the session produced new artifacts, or when the file does not exist yet.
Pinned by `tests/regression/test_resume_preserves_environment.py`, which runs a
real bank twice and asserts byte-identity of `environment.json` across the
zero-new-runs second pass. `verification.json` deliberately remains rewritten
on resume: it is derived metadata, and regenerating it is the sanctioned path
by which the three completed CEC2020 banks acquire their corrected verdict
(D-8.1) when the campaign resumes.

**Interaction with the "single commit" campaign intent.** The CEC2020 campaign
is stopped at a clean cell boundary (fdb-agsk complete through (F6, D20)).
This fix and the D-8.1 verdict fix change RUNNER METADATA WRITERS only: no
optimizer, seed, evaluator, or scheduling code is touched, the full 584-test
suite including the 42-pin hex golden matrix passes, and the resumed leg
therefore remains result-identical to the stopped leg. The resumed banks'
environment.json will record the resume commit — with this entry as the
documented explanation of exactly what changed in between.

## D-8.6 External-baseline code defects found by crossover audit — FIXED 2026-07-28

Origin: a review of the sibling project (05-Human-Inspired-Family) reported four
defects in its external baselines. Eight externals were vendored from that
codebase into this one, so an eleven-agent read-only audit established which
crossed over. Three did. **None contaminated any committed artifact here**, but
two were reachable from committed configs. Full adjudication in decision_log
D-0025; this entry records the repairs.

### D-8.6.1 MOS: MTS-LS1-Reduced clipped against dim-0 scalars (feasibility bug)

`mos_cec2013lsgo.py` collapsed the box to `lb0, ub0 = float(lb[0]), float(ub[0])`
and handed those scalars to MTS-LS1-Reduced, while the GA and Solis-Wets
techniques correctly received the `lb`/`ub` vectors. MTS therefore tested and
clipped every probe against dimension 0's bounds.

**Measured before the fix**, against the real CEC2011 bound vectors: 12 of 22
problems evaluated points outside the feasible box — worst F21 at 16.8% of
evaluations with a 1,899-unit excursion; F17 13.6%; F22 10.4%. With a deceptive
objective the RETURNED `best_x` was itself infeasible, reporting a fitness no
feasible point can attain. That is the sibling's "rank-1 result produced by
searching outside the box", reproduced here.

The trigger is interval CONTAINMENT — whether `[lb0, ub0]` sits inside every
dimension's box — not dimension ordering. CEC2011 F10 is the only one of the 22
that is accidentally protected, which is precisely the case a spot check is most
likely to land on and wrongly clear.

**Why no artifact is affected**: all 15 CEC2013LSGO functions have
per-variable-uniform bounds (±100 / ±5 / ±32), so the scalar collapse was exactly
the identity, and MOS has no bank on any other suite. **But it was reachable**:
`configs/baselines_cec2011.yml` schedules MOS on CEC2011 and the runner applies
no suite guard.

**Fix**: `_mtsr_sweep` and `_mtsr_evolve` now take the `lb`/`ub` vectors and index
them per dimension, exactly as the other two techniques always did. Applied
identically in the upstream source and re-vendored, so the bodies remain
byte-identical (the vendor header's contract) and the disclosure sentence's
"byte-faithful copies" clause stays true. The scalar SR seed retains dim 0's
range with a comment explaining why: `SR` is one scalar per genome by the C++
design, and on the validated uniform-box regime dim 0 is exact.

Verified three ways: (a) the five worst-affected CEC2011 problems now produce 0
out-of-box evaluations in 30,000, and 12 of 12 previously-violating problems are
clean; (b) unpatched vs patched under one harness on cec2013lsgo F13/F1/F3 gives
HEX-IDENTICAL best_fitness and equal nfes -- the fix is exactly the identity on a
uniform box; (c) a full campaign-path replay at HEAD of the archived cell
F13/D905 run 1 (3,000,000 FES via run.py) reproduced the bank value exactly:
bank 4.5430382898e+06 == replay 4.5430382898e+06, seed 939243802, nfes 3000000.
That last check also serves as the D-7-style code-identity attestation for the
MOS bank, which the family D-7 pass did not cover. Pinned by
`tests/regression/test_external_bounds_and_grouping.py`.

Note on replay harnesses: a first attempt called `optimize()` directly and did
NOT reproduce the bank. That was a harness defect, not a finding -- the runner
injects a fair-start X0 (`create_fair_start`) that MOS consumes via
`options.initial_population`, so a direct call draws its own initial population
and follows a different trajectory. Replays of this suite must go through
`run.py`.

### D-8.6.2 DECC-G: random grouping silently degenerate at dim <= group_size

With the default `group_size = 100`, any dimension at or below 100 yields a
single subcomponent: the per-cycle random re-permutation changes nothing, the
co-adaptation weight vector has length 1, and what runs is SaNSDE with a scalar
rescale — a different algorithm still reporting `group_size: 100`. Note the
sibling's phrase "below D=100" understates it: **D = 100 itself is degenerate**.

**Why no artifact is affected**: our DECC-G banks are D=905/1000 (10 genuine
subcomponents). **But four committed configs** (`baselines_cec2011/2013/2017/
2020.yml`) schedule it into 15 degenerate suite-dimension combinations.

**Fix**: `_random_groups` raises when `n_groups == 1`, naming the degeneracy and
pointing at the explicit `group_size` escape hatch for a deliberately decomposed
low-dimensional run. Loud failure was chosen over a warning because the output
would otherwise carry the DECC-G label while being another algorithm. The four
configs carry a matching note.

### D-8.6.3 Two false docstrings (no behavioural effect)

- `cmaes.py` `optimize()` said "the 2001 canonical CMA-ES", describing the
  rank-one-only intermediate state superseded on 2026-07-22 and contradicting
  its own module docstring. Now states standard (mu/mu_W, lambda)-CMA-ES with
  rank-one and rank-mu updates.
- `decc_g.py` said DECC-G was "vendored alongside MOS and SHADE-ILS",
  contradicting `DECC_G_port_record.md`, which records it as first-party code
  written from the source paper with no author-code oracle. Now states that,
  which is also what the corrected disclosure sentence relies on.

### Not a crossover: CMA-ES IPOP mislabel

The sibling's fourth defect (CMA-ES dispatched as IPOP-CMA-ES after IPOP was
removed) did NOT cross over. Our implementation's restart is a divergence
re-seed that does not grow the population, and nothing in this repository
advertises IPOP: all eight occurrences are dated historical notes, a
context-PDF listing, or an explicit prohibition in the `hansen2001cmaes`
evidence card.
