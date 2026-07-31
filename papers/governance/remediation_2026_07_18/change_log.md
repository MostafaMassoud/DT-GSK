# Remediation change log — DTGSK-Q2-2026-07-18-R1

## Phase 0 — authority, ledger, baseline  [COMPLETE]
- Preservation tag `dtgsk-pre-remediation-2026-07-18` at `06353caea` (local; author pushes).
- Control directory created; `decisions.md` records the six adopted decisions.
- `ticket_status.csv` seeded with 79 verified triage verdicts; 9 marked
  `superseded_with_evidence` and fenced against re-editing.
- Baseline archived as-is under `baseline/`: check_manifest 1/12 (exit 1), evidence
  bindings 0 FAIL (exit 0), both DOCX exit 0, cross-format exit 2.

## Phase 1 — method-code correspondence  [CORE COMPLETE]
- **C-006** Eq. (7) rewritten from the frozen operator as an explicit piecewise map:
  net-improving (S>0) credits the FULL arm pool d/S; non-improving (S<0) with at least
  one improving arm credits that subset; S=0 / non-finite / no improving arm holds pi.
  The target is projected BEFORE the EMA mix and the mixture projected again, and the
  projection is the Euclidean projection onto the floored simplex (not floor-and-renormalize).
  Closed by `tests/regression/test_ace_equation_conformance.py` (74 tests, both backends).
- **M-010** Eq. (11) is now an update rule only; the confidence gate is consumption.
- **M-015/016/017** Algorithm 1 caption + crossover step + evaluation step corrected.
- **M-024** Trust-region governor stated as REMOVED (matches `_dt_core.py:3345`).
- Rebuilt: 0 undefined references, evidence bindings 30/30.

## Phase 4 — statistical re-analysis  [STOP-CONDITION AUDIT COMPLETE]
Tie-corrected Friedman + Iman-Davenport recomputed for all 8 reported panels from the
frozen per-function means. **No decision flips.** See `phase4_tie_correction_audit.md`.

## Phase 4b — statistics implemented in the pipeline  [CODE COMPLETE, RELEASE PENDING]

Implemented in the pipeline rather than as one-off outputs, so `finalize` emits them
natively and nothing gets overwritten on the next run.

- **M-026.** Tie correction is now first-class in `statistics.friedman_rank`
  (`tie_correction`, `statistic_tie_corrected`, `p_value_tie_corrected`,
  `n_tied_problems`); the uncorrected fields are retained unchanged so published values
  keep reproducing. `friedman_with_id` reports the corrected χ² and Iman–Davenport F
  with `*_uncorrected` companions; `friedman_ranks_*.csv` gains 5 columns.
  49 unit tests, including **exact agreement with `scipy.stats.friedmanchisquare`**
  (rel 1e-12) across tie regimes and a hand-computed closed-form C.
  Real-data control: uncorrected χ² reproduces the published 41.4975 at D10.
  The prose justification was **doubly wrong** and is replaced: the paper claimed the
  statistic was tie-uncorrected *and* that "ties are rare". Measured: C = 0.890 at D10
  (9 of 29 functions tied), 0.979 at D30, **exactly 1.0 at D50 and D100**. Ties
  concentrate precisely in the panels the old sentence waved away, because the 1e-8
  success floor maps distinct outcomes onto exactly 0.
- **M-027.** `wilcoxon_holm_*.csv` gains `rank_biserial`/`w_plus`/`w_minus`/`n_zero`/
  `direction`, and `statistical_results.csv` `effect_size` now *always* carries the
  paired rank-biserial. It was previously suppressed whenever run-level data existed,
  deferring to AN-EFF's A₁₂ — an **unpaired** statistic. Deferring a paired test's
  effect size to an unpaired one from another family is what left the primary table
  reporting A₁₂ for a Wilcoxon signed-rank result.
- **M-028.** The conclusions tally is now qualified (Section 4 already was; abstract and
  both cover letters verified to carry no tally). The optional sensitivity is also
  implemented: `AN-GHOLM-2017` re-runs Holm across all 24 hypotheses at once —
  **15 of 24 survive**, only `atmals-gsk@D10` and `gsk@D30` do not, and the count of
  significant losses stays **zero under either correction**. Independently reproduced
  before adoption.

**One dependency, shared by all three: the bundle must be regenerated once.** The
promoted release still carries the old CSV schemas, so three manuscript binds
(`tie_correction_C`, `rank_biserial`, and the whole `AN-GHOLM-2017` artifact) reference
columns that do not exist yet. In particular the performance.tex claim that r is
"reported alongside R+/R− in the released per-comparison workbooks" **remains
unsupported and must not ship before regeneration**. All three tickets are therefore
`partially_closed_gated`, not closed.

Regeneration is now safe with respect to RT-001: `runtime_session_split()` stamps
`comparability=NOT-COMPARABLE-ACROSS-ALGORITHMS` on every cost row while the panel is
session-split, so the cost artifact tells the truth about itself instead of silently
publishing a mixed-provenance comparison. Deferred to a single pass after the
ablation/overlay campaigns finish and RT-001 lands, so the release is regenerated once
rather than twice.

## Blocks C & D — Minor and Editorial  [CLOSED except 4 gated + 1 author-only]

**65/80 closed.** Everything still open either needs the running campaign, needs the
one bundle regeneration, or needs the author.

### Layout — three defects that were all the same bug

A recurring pattern surfaced: **an exhibit generated larger than the box it is placed
in, silently scaled down to fit.** LaTeX and matplotlib both do this without warning,
so the symptom (unreadable text) never points at the cause (a size mismatch), and
raising font sizes cannot fix it — the shrink happens *after* fonts are set, which is
why an earlier font bump had no effect.

- **N-013** — the parameter table rendered at **5.3 pt**, not the ~7 pt estimated,
  because `\resizebox{\textwidth}` shrank a 48-row table to fit. Split by audience:
  15-row core in the main text (no scaling), 33 per-subsystem rows to Supplement S5.
  **5.3 → 8.0 pt.**
- **N-011** — convergence grids at 0.656 scale. Fixing the figure size was not enough:
  `bbox_inches="tight"` **re-crops on save**, so a figure declared 6.165 in came out
  7.364 in and was still scaled to 0.837. Sizing a figure to its box is futile while
  the save step resizes it. **Placement scale now exactly 1.000**; supplement pages
  with ≥200 characters below 7.9 pt went **18 → 1**.
- **N-014** — Algorithm 1 overflowed by **84 pt**, not the ticket's 7.36. Caption trim
  recovered 36; the rest was `\setstretch{1.8}`, set for a "page-balanced look" it
  defeated by overflowing the page. **0 float-too-large warnings.**

### N-010 — a conversion that deleted code

Converting the four table-like figures to real table floats made
`build_docx.py::_rebuild_collapsed_authored_tables` **obsolete**: ~100 lines existing
only because pandoc collapses a figure-wrapped tabular into a 1×1 cell. Its hard
assertion failed the build; relaxed to accept 0 as the expected state while still
catching a partial count. `tables_native` 6 → 2 confirms the path is unused.

### Judgement calls, recorded rather than silently taken

- **N-005** — the relative-tie-band sensitivity changes direction in exactly two cells,
  both eGSK at upper tiers. Reported with the honest reading: those are precisely the
  cells whose Holm tests are *not* significant, so it argues for reading them as ties
  **in both directions**, not as evidence for DT-GSK.
- **N-012** — **declined** with rationale. The three rank views answer different
  questions; dropping the CD view would remove the evidence for the paper's own
  non-separability claim.
- **E-011** — 9 occurrences of "no extra objective evaluations" reduced to 6, not swept.
  Each survivor does work; `related_work.tex:190` was left alone because it describes
  **CMA-ES**, not ISM.
- **N-020** — the eleven limitations **moved verbatim** to Supplement S5 rather than
  trimmed. Conclusion 1468 → 862 words, 7 → 4 paragraphs, with every limitation class
  still named in the conclusion itself.
- **E-015** — the audit found a real gap: the `\acknowledgments{}` block omitted the
  exclusion of scientific content. Added. The declaration and acknowledgment stay
  separate — MDPI requires both.

### Shortfalls stated, not hidden

- **E-010** reached 374 words against a ~250 target. Further cuts would have deleted
  content carrying a BIND anchor or a non-claim.
- **E-014** leaves one 1.48 pt overfull box — in the notation table, not Table 1, with
  no text content.
- **E-001** reached 18 sentences over 64 words from a baseline of 31.
- **N-015** and **E-003** are **not done**, and are recorded as such.

### A defect I introduced

Authoring LaTeX through shell-embedded Python collapsed `\ref` into **CR + "ef"** —
byte-for-byte the corruption `validate_build_hygiene.py` was written to catch. The gate
caught it; repaired at byte level. Since then all LaTeX edits go through the Edit tool
or a written script file, never nested shell quoting.

## Block B — M-003, M-033 cross-stated facts  [CLOSED]  ·  M-007 re-scoped

Both tickets are the same failure mode: a fact written in more than one place, with
nothing linking the copies, so they agree only while whoever edits one remembers the
others. New gate `papers/scripts/validate_document_consistency.py` compares the copies.

- **M-033.** `cover_letter.md` still carried `[submission date — author to fill]` while
  `cover_letter.tex` read *25 July 2026*. Markdown set to match. Rather than generate one
  file from the other — which fights the two formats' different front matter — the gate
  now cross-checks title, date, corresponding author, GenAI tool/version and
  contribution-scope markers.
- **M-003.** Closed via the ticket's stated alternative (drift validator) rather than the
  full machine-readable registry: generating the supplement overview, main-text locators,
  cover letter and package manifest from a registry is a build restructure, and the
  terminal-freeze constraint makes a late refactor the wrong trade. The gate checks that
  main.tex's `\supplementary{}` back matter claims exactly the sections
  `supplementary.tex` contains, that labels are contiguous S1..SN, and that any `S1--SN`
  range agrees with the itemised labels. Current state verified in agreement (S1..S6, six
  actual sections).

**Three exit codes, deliberately.** 0 = clean, **1 = drift** (a real defect), **2 = an
author-supplied field is unfilled**. Pooling them would leave the drift gate permanently
red on an author action — which is precisely how a gate stops being read. Wired into the
attestation with `accepted_exit_codes {0,2}`, so drift breaks the attestation while
author-pending does not, and the pending state is still recorded per gate.

**Self-tested:** five injected drifts — date, title, GenAI version 4.8→4.7, an unclaimed
7th supplement section, and a range/label mismatch — all caught with exit 1, every file
restored byte-exact. One bug in the gate itself surfaced and was fixed: the TeX capture
stopped at the first backslash, comparing a name against an email and reporting a
difference that was not there.

**Genuine finding, author action required.** Both cover letters still contain
`[AUTHOR TO FILL — suggested reviewer names, affiliations, and institutional email
addresses]`. The block's own comment says *"Do not auto-generate names"*, and this is not
a decision tooling can make. It blocks submission and is now reported by the gate on
every run.

**M-007 re-scoped, not closed.** Two of its three preconditions are now met — the parity
FAILs are resolved (M-029) and the supported-environment attestation is green (M-030). It
is gated solely on the terminal re-freeze (C-008).

**Attestation note.** Adding the document-consistency gate means the stored
`attestation.json` predates the current gate set. It is regenerated once as the final
pre-freeze step rather than after each change; the record is not cited as current until
then.

## Phase 5b — M-030 environment attestation  [CLOSED]

`papers/scripts/make_environment_attestation.py` produces a machine-checkable record in
`papers/governance/environment_attestation/` (`attestation.json`, both JUnit XMLs, a
README stating what it does and does not establish).

**Not stored in the analysis bundle.** `phase6_run_analysis.py` `rmtree`s that directory
on every regeneration, and RT-001 guarantees one is coming — an attestation archived
there would be silently deleted. Governance is the durable home.

**The generator refuses to write `green: true` unless three conditions hold:**

1. The installed interpreter and numpy/scipy/pandas/matplotlib versions lie inside the
   ranges declared in `pyproject.toml`.
2. The full suite runs **twice** with zero failures and the same test count both times —
   which also rules out a result that depends on ordering or on leftover state.
3. Every release gate exits 0.

Condition 1 is the load-bearing one. "The tests pass" is not the claim the manuscript
makes; the claim is that they pass *on the supported configuration*, and a green suite on
an out-of-envelope stack attests nothing about that. The version-range comparator was
unit-checked against 8 boundary cases before being trusted — including `1.15.3 < 1.16` and
`3.13.9 < 3.14`, where the operands differ in precision and a naive tuple compare is wrong.

Result: **474 tests, 0 failures on both runs**, counts agree, all five gates exit 0, whole
stack in-envelope (Python 3.10.11, numpy 2.2.6, scipy 1.15.3, pandas 2.3.3,
matplotlib 3.10.8). Referenced from `sec:repro:release`.

Two limits recorded rather than glossed:
- `git.dirty` is honest about whether the commit identifies the tested tree. While the
  working tree is uncommitted, `git.head` does **not** fully identify what was tested.
- Any subsequent `.tex` edit invalidates the cross-format-parity gate and therefore the
  record. This bit immediately: the M-030 supplement edit invalidated the attestation
  generated minutes earlier, so it was rebuilt and regenerated rather than left stale.
  **Regenerate once more as the final pre-freeze step** (~10 min; the suite runs twice).

## Phase 6a — M-029 cross-format parity  [CLOSED, gate green]

`validate_cross_format_parity.py` now **exits 0**: 544 rows, 494 PASS, 50
PASS_FORMAT_DIFF, **0 FAIL**. Both DOCX validators exit 0.

**First: the count was wrong.** Re-measured, it was 31 FAIL, not the ticket's 20 — the
rendered artifacts predated this session's `.tex` edits (the DOCX by ~12 h). Rebuilding
dropped it to 24 and every paragraph/heading/caption failure vanished as pure staleness.
Worth noting `build_docx.py` needs **two** invocations; running it once leaves
`supplementary.docx` stale, which briefly looked like catastrophic content loss.

**Option (a), not (b).** The ticket offered teaching the validator the real contract or
converting the disposition doc into a signed exception manifest. (b) would have stopped
verifying the 18 rows it exempted — a permanently amber gate people learn to ignore.

**Root cause.** Check (a) compared DOCX cells to the semantic `word_sources` JSON, but
`build_docx` emits *some* tables natively from that JSON and routes the rest through
pandoc from the rendered LaTeX. For the pandoc-routed tables the check could never pass.
It now accepts either legitimate source, which together with check (b) chains
DOCX → `.tex` → semantic source → evidence.

Six defects fixed, each verified against real data first:
1. **Only the first `tabular` was parsed.** T15 stacks two (D10/D30 above D50/D100), so
   the D10/D30 half was compared against the DOCX's D50/D100 tail — and worse, **T15's
   D50/D100 values were never verified against the semantic source at all.**
2. LaTeX `\times10^{n}` vs Word `e-04` notation.
3. Word drops trailing zeros LaTeX prints (`1.0000` vs `1`).
4. `\addlinespace[2pt]` leaked into the first cell, hiding each group's first data row.
5. Composite semantic values (`3.22 (ref)`) made `float()` throw inside `display_match`.
6. `detex` dropped `\log`, leaving `10 error` for `$\log_{10}$ error`.

Plus two genuine format artifacts: the MDPI **`pages 1 - 53`** running footer interleaving
mid-paragraph at page breaks, and `\textsc` small-caps rendered as capitals in the PDF only.

**Soundness proven, not assumed.** Relaxing six checks earns the obligation to show the
gate still bites. Three real content errors were injected through the validator's own code
path — a wrong numeric value, a dropped data row, two transposed rows — and **all three
were caught**, with the clean tree green. An earlier injection reported no failures; it
matched whole cells while the cells are composite `mean±SD` strings, so it never fired.
That result was discarded rather than read as a pass.

One self-inflicted regression caught and reverted: adding `\min`/`\max` to the macro map
broke the notation table, where they occur as subscripts in symbol names (`\pi_{\min}`)
rather than in operator position. The addition was narrowed to `\log`/`\ln`/`\exp`.

`cross_format_disposition.md` is marked SUPERSEDED: its root-cause analysis was correct
and led to this fix, but its verdict — waive them as an unfixable expectation defect — no
longer describes the tree.

## Phase 5a — M-031 freeze provenance  [CLOSED]

`sec:repro:freeze` asserted *"no such change occurred for the results reported in this
paper"* — while three artifacts in the same repository recorded two post-freeze source
fixes and a full evidence regeneration. The supplement already carried an honest,
detailed account of both defects in `sec:supp:ablation:caveats`; the two sections simply
contradicted each other.

Rewritten as a six-step chronological record: original freeze (2026-07-10, anchor
`708a927bf`) → post-freeze audit finds C006 and M038 → source fixes, each locked by a
regression test that **fails on the pre-fix code** → module rename `ism_*`→`dt_*` → full
51-run regeneration with comparators verified byte-identical (so scope is DT-GSK only) →
current release `rel-2026-07-16-78f075cb0`. It cross-references the existing caveats
subsection rather than duplicating it.

Two further corrections in the same subsection:
- The four recorded hashes are now stated plainly as **historical** — they pin pre-fix
  sources under pre-rename filenames — with the current shipped prefixes printed
  alongside. All four differ (`a274e0f83b4efd3c`→`51b12194a3962a20`, and so on).
- The **"byte-identical" rename parenthetical is dropped.** It implied the shipped
  modules still match the frozen hashes; they do not.

The change register jumped from CR-0006 to nothing, which is precisely why the
no-change claim could survive: there was no record to contradict it. **CR-0007** now
registers both corrections with their measured consequences (C006 changes trajectories
where the polish fires; M038 is result-neutral and affects wall-clock only) and the
regeneration scope they forced.

New reusable gate: `papers/scripts/validate_provenance_claims.py` cross-checks release
ids, anchor commits, printed hashes, no-change assertions, and change-request citations
against the manifests — the check M-031 asked for, and the one C-007 and C-008 will need.
Self-tested by injecting all three defect classes; each was caught and the file restored
byte-identical. Worth recording that **the gate's own first hash check was defective**: a
proximity heuristic that accepted any hash near the word "historical", which can never
fail inside a subsection *about* historical hashes. The self-test caught it passing a
frozen hash substituted for a live one. Replaced with two structural rules keyed on the
module each hash is attributed to.

Note: the freeze manifest itself is still stale — that is C-007 (mint fresh), still open.
This ticket makes the manuscript honest about that in the meantime rather than papering
over it.

## Phase 13 — runtime provenance after the post-fix promotion  [PREPARED, RUN PENDING]
Post-promotion byte audit: every scientific column of the DT-GSK CEC2017 evidence
reproduced exactly across all 5,916 rows; **only `runtime_seconds` changed** (D100
69.04 -> 41.59 s, -39.8%), tracing to defect M038. Comparators were not re-run, so
`tab:runtime` currently mixes two measurement sessions. Decision 7 adopts a
CEC2017-scoped comparator re-timing (~227.7 core-h, 15-25 h wall-clock); ticket
**RT-001** registered as blocking with `requires_rerun=yes`.

Landed this phase (no optimizer run performed):
- `scripts/retime_comparators.py` — re-timing driver. Reuses the campaign's exact
  command and pinned single-threaded numeric stack, refuses to start while a campaign
  staging tree has been written in the last 10 min (contended CPU invalidates timing),
  and ends in a determinism gate asserting that every scientific column reproduces so
  the refresh is provably timing-only. Self-tested: an injected one-cell `error`
  perturbation was caught and localized (`f1 D10 run8`) while a uniform -40% timing
  shift passed, and an empty comparison now reports INCOMPLETE rather than a false
  green.
- `papers/scripts/validate_runtime_provenance.py` — gate for regenerating the runtime
  table. Reads per-cell `environment.json` and fails unless the panel was measured as
  one session (same host, same worker count, all cells within 72 h). Current verdict:
  **FAIL**, isolating `dt-gsk (+9.7 d)` against a comparator block spanning ±14.2 h.
  Commit equality is deliberately not required — a sequential campaign advances commits
  between cells, so commit inequality carries no signal.

Interim rule in force: `tab:runtime` and the runtime prose are frozen; no other phase
is blocked, since no other reported quantity depends on wall-clock.

**Observation flagged, not actioned:** the `tab:runtime` caption states APGSK's
D<=50 cells were measured in a post-freeze recovery "about three days later", but the
promoted `apgsk/environment.json` timestamp (2026-07-08T21:53) sits *inside* the main
comparator block, 4.7 h from its median. Either the caption is stale with respect to
the currently promoted cell or the block itself is the recovery. Not chased: a
successful re-timing places all seven cells in one session and dissolves the caveat
entirely. If the fallback option is taken instead, this needs resolving first.
