# Remediation decisions — DTGSK-Q2-2026-07-18-R1

Author instruction (2026-07-18): *"Execute the DT-GSK Submission Remediation Plan. On each of the six
open decisions, adopt the recommended option... do not take any action that would require re-running the
optimizer or regenerating the evidence releases."*

## Standing constraint

**NO RERUN.** All work is confined to prose, equations, analysis derived from already-frozen per-run
evidence, manifests, validators, and production artifacts. Triage confirmed 0 of 79 tickets require an
optimizer rerun. If any task is found to require one — including a Phase-4 tie correction that flips a
significance, rank, or sign — execution stops and the author is notified.

## Decisions adopted

| # | Decision | Adopted option |
|---|---|---|
| 1 | Authoritative manuscript state | The **current source tree**. Both review-named candidates (39 pp `31887100…`, 40 pp `4f9e9cf8…`) are recorded as superseded; the 39/40-page fork is moot. Preservation tag `dtgsk-pre-remediation-2026-07-18` at `06353caea`. |
| 2 | Statistics | **Re-analysis only, no rerun.** Tie-corrected Friedman/Iman–Davenport and paired rank-biserial are re-derived from frozen per-run data. Hard stop if any significance, rank, or sign flips. |
| 3 | C-006 (ACE Eq. 7) | **Correct the paper, not the code.** Default rule: make the paper describe the frozen code. Editing `_dt_core.py` would break the hash pin and force a rerun. |
| 4 | Missing experiments | **EXP-004 only** (supported-environment attestation). EXP-001/002/003/006 avoided by *narrowing the corresponding claims*. EXP-007/009 are future work. External non-GSK baselines remain out of scope this cycle. |
| 5 | Algorithm freeze manifest (C-007) | **Mint fresh.** The 2026-07-10 file is obsolete in every field; mark historical and repoint its citations. |
| 6 | Minor/Editorial scope | Land the blocking path first; Minor/Editorial before the terminal freeze, since anything landed after it re-opens the freeze. |

## Derived sequencing constraint

The manuscript freeze decays with every content edit (4/12 → 3/12 → **1/12** observed across three edit
rounds). The re-freeze is therefore **terminal**: performed once, byte-surgically (CRLF + 2-space indent
preserved — normalizing to LF breaks every hash), after all content phases land.

## Disposition rule

`ticket_status.csv` records a verified triage verdict per ticket. Tickets marked
`superseded_with_evidence` (9) were confirmed closed against the live repository and **must not be
re-edited** by any later phase.

---

## Decision 7 — runtime provenance after the post-fix promotion (2026-07-18)

**Context.** The post-fix campaign re-ran DT-GSK on the three primary suites and the results were
promoted into `benchmarks/cec_reference_results`. Byte-level comparison of the promoted `per_run.csv`
against the previous evidence shows that **every scientific column is identical across all 5,916
CEC2017 rows** — `error`, `best_fitness`, `seed`, `nfes`, `termination` — and that **only
`runtime_seconds` changed**:

| Dimension | Previous (paper, Table `tab:runtime`) | Promoted | Δ |
|---|---|---|---|
| D10  | 5.63 s  | 4.93 s  | −12.4% |
| D30  | 14.68 s | 13.04 s | −11.2% |
| D50  | 25.78 s | 23.30 s | −9.6%  |
| D100 | 69.04 s | 41.59 s | **−39.8%** |

The cause is defect **M038**: the earlier release silently executed the bit-for-bit-equivalent NumPy
reference path for the interaction graph. The compiled kernels are now active, so the drop is a genuine
speed-up of the shipped artifact, not a measurement artifact.

**Problem.** The comparators were **not** re-run. `tab:runtime` would therefore mix today's DT-GSK
timings with the original campaign's comparator timings. Wall-clock is the only reported quantity that
is a property of the machine and build rather than of the algorithm, so a mixed-provenance runtime
table is not a valid comparison — and no other number in the paper is affected, since the scientific
columns are unchanged.

**Options considered.**

1. *Revert `runtime_seconds` to the pre-campaign values.* Rejected: it puts the manuscript behind its
   own promoted evidence, and the reverted figures describe a code path that no longer ships.
2. *Re-time the six comparators on the same machine.* **Adopted.**
3. *Keep the new timings and re-scope `tab:runtime` as DT-GSK-only, explicitly non-comparative.*
   Held as the fallback if the re-timing cannot be scheduled.

**Adopted: Option 2, scoped to CEC2017.** That is the suite `tab:runtime` reports. Rationale: it is the
only option that leaves the paper on the latest data *and* preserves a valid cross-algorithm
comparison. Retaining the old DT-GSK timings would state a cost the released artifact does not incur,
understating the method by ~40% at D=100 — a factual error about the shipped software, even though it
errs against the authors' own interest.

Measured cost from the existing evidence: 227.7 core-hours for the six comparators (vs 34.0 for
DT-GSK), ≈ 15–25 h wall-clock at 15 workers. A full three-suite re-timing (~44 h) is **not** taken:
CEC2013 and CEC2011 carry no cross-algorithm runtime table.

**Two conditions.**

1. **The machine must be idle.** Timing runs that contend with the ablation/overlay campaign are
   contaminated, and the comparison would be invalid again. `scripts/retime_comparators.py` refuses to
   start while a campaign staging tree has been written within the last 10 minutes.
2. **Determinism must be re-proven per comparator.** The verify stage asserts that every scientific
   column reproduces exactly, so the refresh is provably *timing-only*. A single differing `error` value
   is treated as a correctness defect, not a timing one, and blocks promotion.

**Interim state (in force until the re-timing lands).** The promoted `per_run.csv` stays as-is — it is
the latest data. `tab:runtime` and the runtime prose are **frozen and must not be regenerated**: a
mixed-provenance table is worse than either endpoint. Tracked as ticket **RT-001**. No other phase is
blocked, because no other reported quantity depends on runtime.

**Expected effect on the manuscript.** The re-timing likely *improves* the reported position — DT-GSK
moves from "most expensive panel member at D ≤ 50" toward parity, and from fourth of seven at D = 100
toward the faster end. That is the honest consequence of a disclosed bug fix, and the supplementary
S6.7 note explaining M038 already sets it up. The ISM overhead figures (+54%/+37%) were measured on the
un-accelerated path and must be re-derived in the same pass.

**Amendment (2026-07-21) — Option 2 attempted and failed; Option 3 adopted.** The comparator re-timing
(Option 2) was run on an idle machine via `scripts/retime_comparators.py` (all six comparators, CEC2017,
51 runs, ≈22 h). It **failed the determinism gate**: the re-timed comparators did not reproduce the
frozen scientific columns — **3,772 differences** across the six, from ~1 ULP (`gsk`, 88 diffs, D100
only) to large chaos-amplified shifts in the scipy/local-search members (`atmals-gsk` 1,832 diffs
≈31% of runs, `egsk` 1,733 ≈29%). Root cause: the comparator frozen evidence is from **2026-07-08
(commit `31c5a04c4`)** and is not bit-reproducible under the current code (`dc924dc48`) — a shared
numeric kernel's FP path shifted across the intervening commits and, on a few runs per cell, crossed a
branch boundary. This was confirmed to be **version/FP drift, not a determinism bug and not data
corruption**: a fresh re-run at the current commit reproduced tonight's re-run **30/30** (including the
diverging runs) while differing from the 2026-07-08 evidence only where the code drifted. The frozen
evidence and every scientific claim are therefore intact; only a bit-identical *re-timing* is
impossible.

Option 2 is thus unachievable, and **Option 3 (DT-GSK-only, explicitly non-comparative) is adopted.**
Actions: `tab:runtime` re-scoped to DT-GSK-only with the correct post-fix CEC2017 timings
(4.93 / 13.04 / 23.30 / 41.59 s ± SD); the runtime prose and the supplement's LM-04 limitation
reconciled to make no cross-algorithm runtime claim; `validate_runtime_provenance.py` re-scoped to
verify DT-GSK's own single-session provenance (passes); ticket **RT-001 closed**. This pass also
corrected a latent error: the frozen table had been shipping the **pre-fix** DT-GSK numbers
(D100 = 69.04 s) while its prose claimed post-fix provenance — the re-scope fixes both the
mixed-provenance issue and the stale figures in one move. The backend-corrected ISM overhead
(+57.3% / +36.3% / +30.3%) noted above was re-derived earlier and already stands in Supplement S6.7.

---

## Terminal freeze / submission finalization (2026-07-21)

Author instruction: *"finalize open tickets in paper except lsgo."* The five open tickets reduced to
the terminal freeze chain plus two author-side items. Actions this pass (LSGO explicitly out of scope —
a separate campaign is running):

**Pre-freeze drift (B1).** Four stale evidence-release ids corrected to the authoritative
`rel-2026-07-20-67d9345f9`: provenance-header comments in `main.tex:6`, `sections/performance.tex:5`,
`sections/conclusions.tex:7`, and the present-tense re-derivability claim **CN-02** in
`claims_evidence_matrix.csv`. **LM-01**'s two `rel-2026-07-10-262fc16c9` references were **preserved**
as legitimate Phase-6 provenance history (the rank was re-derived from 07-10 when it was current; the
scientific columns are identical across releases per Decision 7). `DT-GSK_visio.docx` is a Visio working
file, **excluded** from both manifests and flagged for author `git rm` (not deleted — tracked file).

**Deterministic rebuild (B3/B4).** `DT-GSK.pdf` (38 pp), `supplementary.pdf` (60 pp), and the stale
`cover_letter.pdf` (2 pp) rebuilt under `SOURCE_DATE_EPOCH=1783468800 FORCE_SOURCE_DATE=1`, each
**double-built byte-identical**; PDF text content verified unchanged vs the prior builds (B1 was
comment-only). The two DOCX are the committed deterministic renders, pinned as-is (canonical P10 tooling
double-builds PDFs only). The full `finalize_evidence.py` orchestrator was **not** run — its P3 would
rebuild ablation cells (51 runs), violating the NO-RERUN constraint; only the P10 build steps were
replicated manually.

**Terminal re-freeze (C-008 — closed).** A **fresh** `main_manuscript_freeze_manifest.json` was minted
(not patched): 15 files — the 6 source `.tex`, main PDF/DOCX, supplement PDF/DOCX, cover-letter PDF, the
three governance CSVs, and `references.bib` — with the 68 accumulated `*_refreeze` history blocks
retired. `check_manifest.py` now reports **15/15 (exit 0)**. Byte format preserved (no BOM, CRLF,
2-space indent, no trailing newline). `_pending_refreeze.json` formally **CLOSED** (prior state retained
for audit). A companion **`submission_package_manifest.json`** (C-001) records per-file SHA-256, page
counts, build epochs, evidence-release id, and `manuscript_version_id=v1.0`.

**Ledger.** **C-008, M-007, N-009 → closed_verified** (M-007's three preconditions — parity 0-FAIL
M-029, green attestation M-030, terminal freeze — all met; N-009's access-dates author-resolved). Ledger
**78/80**. The two remaining are author-side: **C-001** (the single authoritative git commit + push —
everything else prepared and staged) and **N-021** (JCR/Scopus figures — acceptable alternative of
keeping quartile out of manuscript-facing materials already in place). All six gates green;
`check_manifest` 15/15.

---

## Post-review remediation and re-freeze (2026-07-22)

An external adversarial review returned **D2 - major pre-submission revision**. Independent
verification against the current sources re-scoped it materially, and the corrections were applied
as a single consolidated pass.

**The pivotal finding: no rerun.** The review's most serious claim - that several comparator ports
evaluate past `MaxFES` - is factually correct as an *observation* but wrong in its conclusion. The
six comparator ports are deliberate MATLAB-faithful reimplementations that evaluate the terminal
batch in full and charge only the in-budget prefix; the overrun is structurally bounded to at most
`NP - 1` rows on a single terminal generation, the discarded rows are never read back (prefix-only
incumbent scan) and the loop exits immediately. No reported value can depend on them. Evidence
release `rel-2026-07-20-67d9345f9` therefore stands unchanged, and **no optimizer code was edited**
(Decision 3: correct the paper, not the code).

**What was actually wrong.** (i) The supplement presented the superseded release
`rel-2026-07-16-78f075cb0` as current - the current id appeared *nowhere* in its rendered body;
(ii) `validate_provenance_claims.py` passed anyway, via four independent false-negative defects
including an unconditional `ok()` and a regex that captured the pronoun in "drawn from it";
(iii) Eq. (4) used one shared sign `s` for two phases that compare *different* donors (junior vs
`R_3`, senior vs `R_2`), and the sign convention lived only in a `%` comment, reaching neither PDF
nor DOCX; (iv) the stated no-worsening population invariant was false for the deep-stall restart;
(v) a governance audit asserted "no truncated boundary generation occurs in any panel cell";
(vi) the conclusion counted the ISM null as a fourth contribution against a three-item list; and
(vii) - missed by the review - the DOCX carried literal `&` alignment markers, so Word rendered
Eq. (4) as "junior: u_i **&**= ...".

**Freeze discipline.** The 2026-07-21 terminal freeze (`383d7896b`) was re-opened. Its
`validate_provenance_claims = 0` attestation was recorded as **void, not stale**: the gate attested
exactly the property that was violated and could not fail. The validator was therefore hardened
*first* and required to go **RED on the unfixed bytes** before the fix was applied, and GREEN after
- a gate that passes both before and after proves nothing. It now also reads the rendered PDFs and
DOCX, which it never opened before.

**Outcome.** Tickets R-01..R-13 closed (R-14, counting/equivalence probes, remains open and
optional). `check_manifest` 15/15 against a freshly minted manifest; cross-format parity 578 rows /
0 FAIL; both DOCX 33 PASS / 0 FAIL with zero literal `&` math runs; all gates exit 0. Document,
governance and tooling changes only - no evaluations re-run, no reported value altered.
