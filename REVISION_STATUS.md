# REVISION_STATUS.md — where this project is right now

**Read this first if you are resuming work.** It is the single source of truth for *current state*.
Architecture, rules, and how-to live elsewhere (see [REPO_MAP.md](REPO_MAP.md)); this file records only
what is happening, what is done, and what is next.

| | |
|---|---|
| **Last updated** | 2026-08-29 |
| **Manuscript** | `algorithms-4507562` — *Algorithms* (MDPI) |
| **Submitted** | 2026-08-01 from freeze **pass-38 / tag v2.13** (anchor `b515907`) |
| **Editorial status** | **MAJOR REVISION** — 2 reviewers, received 2026-08-24 |
| **Branch** | `main` — **published** at `02d1791`, tracking `origin/main`, and since 2026-08-28 the **only** branch: the development-history branches were bundled to the author's private history bundle outside the repository (restore-tested; location in the withheld `papers/review_2026_08_24/PRIVATE_OPS.md`) and deleted. Never fetch that bundle into a repo with a public remote. |
| **Progress** | **COMPLETE** — all ten reviewer points answered; phases 1–7 applied; five experiments run, analysed and written up (E5 added ahead of resubmission, pass-49); the reopened-items batch (pass-50), the acceptance-readiness review (pass-51) and the seven-lens panel review of the response letter (pass-52) are all applied. |
| **Freeze** | **pass-58 / tag v2.31** (anchor `8b83a39`) · `check_manifest` 15/15 + `sources 2/2` (gating commit-field resolvability) · **PUSHED 2026-08-29** — all 31 tags on `origin`; v2.13 and v2.31, the two the DAS names, verified resolving there. Repo is **PRIVATE until upload day** — flip public before SuSy upload. Next free ids **CR-0039 / D-0064**. |
| **Revision deadline** | **2026-09-01 CONFIRMED** — also the planned resubmission date, so **zero slack**; the extension-request draft is the only margin (§5) |

---

## 1. The review in one paragraph

Two reviewers, neither recommending rejection. Every substantive criticism is about
**attribution, not validity**: the paper bundles several mechanisms and never isolates the
dimension-tiered design the title is named after. Both reviewers independently raised the
population-size confound, which makes addressing it effectively mandatory.

**The reports are not in this repository** (D-0049). Both reviewers declined to sign, and
republishing a confidential report is the journal's act at acceptance, in the journal's own form —
not the authors' to take unilaterally, mid-revision. The verbatim record, Reviewer 1's original PDF
and the point-by-point response are on disk, ignored by `.gitignore`; their git history lives only in
the author's private history bundle outside the repository (the never-push branches were
bundled and deleted 2026-08-28). Read the verbatim record on disk before drafting
any rebuttal sentence; the summaries below are lossy by design.

**The pre-registration is public**, at
[`papers/review_2026_08_24/revision_experiments_preregistration.md`](papers/review_2026_08_24/revision_experiments_preregistration.md).
It was signed before any of the four experiments produced a result and fixed the manuscript wording for
each possible outcome — including the outcomes adverse to the paper, two of which occurred. That
document is what the revision's honesty claim rests on, so it belongs in public.

## 2. The ten reviewer points and their disposition

| # | Ask | Status | Cost |
|---|---|---|---|
| **R1.1** | Abstract sentence "adapt … at one operating point" is ungrammatical | ✅ **DONE** (§3) | Text |
| **R1.2** | "Adaptive control" misleading → retitle | ✅ **DONE** (§3) | Text, 20 files |
| **R1.3 / R2.2** | NP = 5D vs NP = 100 confound → run DT-GSK at NP = 100 | ✅ **RUN + ANALYSED** — standing survives; top-2 at every D | 5,916 runs done |
| **R1.4** | S6.5 uses χ² while main text uses Iman–Davenport | ✅ **DONE** (§3) | 0 runs |
| **R2.1** | No tiered-vs-uniform ablation | ✅ **RUN + ANALYSED** — tiering shown at D10/D50; D30 tier mis-specified | 11,832 runs done |
| **R2.3** | Eigenframe not isolated (want none / coordinate / eigenframe) | ✅ **RUN + ANALYSED** — polish works; eigenbasis harmful at D50 | 2,958 runs done |
| **R2.4** | ISM shows no standalone benefit → strengthen or demote | ✅ **DONE** (§3) — demoted; E1 upgrades the finding from null to **harm** | Text |
| **R2.5** | Don't read best aggregate rank as superiority over eGSK | ✅ **DONE** (§3) — body + abstract | Text |
| **R2.6** | Panel is GSK-family only | ✅ **DONE** (§3) — scope limb + defusal | 0 runs |
| **R2.7** | No sensitivity analysis on thresholds/constants | ✅ **RUN + ANALYSED** — ordinal stable 26/27 cells; no knife-edge | 11,745 runs done |

**All ten reviewer points now have their evidence.** The campaign completed 2026-08-26 20:44 (31 legs,
32,451 runs, 22.19 h, zero failures). Results promoted as release **`rev-rel-2026-08-26-dd42d37eb`**
(`benchmarks/cec_reference_results/_revision/`, 252 files, non-superseding) with the self-manifested
analysis bundle at `papers/analysis/rev-rel-2026-08-26-dd42d37eb/` — pairing seed-verified, eleven
known-answer pins reproduced, Holm family structure recorded per experiment.

**The write-up is done too.** Supplementary Section S9 carries all five experiments as Tables
A43--A47, the pre-committed C1/ISM/C2 manuscript edits are applied, the point-by-point response letter
is written (and has since been through the pass-51/52 review instruments), every gate is green, and
the current freeze is **pass-58 / v2.31** at 15/15 + sources 2/2 — push, then verify both
DAS-named tags resolve on the remote. What is left is the
author's upload day — public flip, purge ticket, SuSy resubmission (Section 5).

## 2a. Open against the published paper

**[HISTORICAL — every item below was discharged by pass-42 (CR-0025 / D-0050); §7's trap table
carries what generalises. Kept as the verification record of that pass.]**

**One confirmed defect, and a verification pass over eleven more.**

**Scope note — read this before deciding urgency.** "Published" throughout this section means
published to the **public repository** at `v2.14`. The manuscript itself is still in round-1
revision at *Algorithms* and has **not** been resubmitted through SuSy; the Preprints.org posting
was withdrawn the same day it went up (D-0046). Every defect below is therefore still correctable
in the version the reviewers will actually read, at the cost of one ordinary change-control pass.
After resubmission the same edits become a correction to a live submission. **Fix before
resubmitting.**

**CONFIRMED — Table A45 caption.** Supplementary S9.3's caption says the two identity controls
"coincide with the tiered configuration by construction, which the tie counts confirm". The
U-low/D = 10 control does (0/29/0). The U-high/D = 100 control prints **2/25/2**. Traced: the
resolved configuration, the execution environment and the evaluation budget are **identical**
between the two legs (the one apparent config difference was a `json.dump` artifact — YAML parsed
the integer keys correctly), and NP was not transplanted, so E3 is budget-fair. Yet **27 of 1479**
run cells differ at D = 100, median relative 1.6e-4, **max 5.3e-2** — not floating-point noise.

**INVESTIGATED 2026-08-27 — contribution C3 is NOT falsified, and the residual's cause is narrowed
to one uncertified link but is NOT resolved.** Corrected after adversarial challenge; two steps of
the first write-up of this block were wrong and are marked below.

*Ruled out.* **Configuration:** identical — all 108 resolved keys match `pub_overrides(100)`; the
apparent difference is a `json.dump` artifact, and the generated YAML at
`_configs/e3_uniform_high_cec2017.yml:36` carries genuine unquoted integer keys. **Pairing:** seed,
`nfes` and termination match on all 1479 cells; zero seed mismatches. **Threading:** both drivers
pin `OMP`/`MKL`/`OPENBLAS`/`NUMEXPR`/`NUMBA` to 1, and `numba_threads_active` is 1 in both records.
**Telemetry:** ruled out, but **not for the reason first recorded here.** The first write-up said
`generation_logs_enabled` gates the coverage kernel through `_need_coverage`. **That is wrong — do
not repeat it.** `generation_callback` is set only by the opt-in `dt_diagnostics` path
(`dt_gsk.py:107-128`), which the campaign never used; those two YAML flags are consumed only in
post-run persistence (`run_experiment.py:1736-1737`). The conclusion survives by a **stronger**
route: the flags never reach the optimizer at all.

*Measured directly this session.* Two probes, threads pinned before `numpy` import, `dt_gsk.optimize`
in-process, 60k evaluations, seed 12345:

| Probe | Result |
|---|---|
| Same build, 1 thread, repeated — cec2017 F13/F20/F7 at D = 50 and F13 at D = 100 | **Bit-identical**, including on the functions that diverge across builds |
| Same build, 8 threads vs 1 thread | D = 50 identical; **D = 100 F13 differs** (`…10924.327439041834` vs `…041108`, ~7e-14 relative) |

So **byte-stability holds at D ≥ 50 for a fixed build in the pinned environment** — the tier the
regression KAT never covered — and it is genuinely thread-sensitive at D = 100.

*The paper already says this.* `performance.tex:250-258` states that "byte-identical reproduction at
$D \geq 50$ requires single-threaded numerical kernels", that the shipped runs use one thread, and
that determinism "is established for \dtgsk{} in its declared single-threaded environment"; it
further records that reproduction **across producer commits** is not claimed, citing a comparator
re-execution where "a floating-point path shifted between" commits. **C3 is therefore already
correctly scoped, and must NOT be narrowed.**

*Where it actually stands.* The two legs are not the same binary: shipped ran 2026-07-18 at
`251fc8cb` (unrecoverable — squashed off every ref), revision 2026-08-26 at `63bd484`. But a
cross-build explanation **collides with a printed, bound claim**: `supplementary.tex:1254-1267`
(bound at `:1268`) says the CR-0013…CR-0018 edits to `_dt_core.py` were "certified *bit-identical*",
re-verified "with zero divergence", and that "No reported number, rank, $p$-value or decision …
depends on which of the two revisions is used." Table A45's D = 100 row is a counterexample to that
sentence.

**⚠ WITHDRAWN — an earlier revision of this section claimed the certification chain has "exactly one
hole", CR-0015, because its hex-identity evidence omits cec2017 D100. That is REFUTED**: CR-0014
certifies cec2017 D100, CR-0016 certifies D10/D50/D100, and CR-0018 certifies an 84-cell ledger
including that cell bit-for-bit. CR-0015's list is indeed shorter, but the cell is covered three
other ways, so nothing rests on it. **Do not revive that reading** (D-0050 status, D-0051).

**ANSWERED by re-execution (D-0051).** The five carrier functions were re-run at D = 100, 51 runs
each, current build, threads pinned: on the 26 divergent cells the fresh run reproduces the
transplant arm on all 26 and the archive on none; on the 229 agreeing cells it reproduces both.
Independently replicated in a separate process, byte-identically. **The residual is a difference
between builds, demonstrated.** What survives is narrower: the campaign's identity evidence samples
about one run per (algorithm, suite, dimension), so a divergence at this rate is below its
resolution — underpowered for this question, not wrong.

*Proven vs probable.* That the residual is cross-build is now **demonstrated**. What caused the two
builds to differ is
**unproven** — state the gap, never the causation. And the first write-up's appeal to
`np.linalg.eigh` as the *cause* is **withdrawn**: given identical input on identical LAPACK it is
deterministic, so it can **amplify** a divergence but never originate one. The thread probe above is
what it actually demonstrates.

**Consequence.** The caption fix (§2c E13a) is deliberately **decision-independent**: it deletes the
false clause and asserts no cause, so it ships regardless. Correcting `:1254-1267` is a **body**
edit needing scope, the three CR ids, an evidence binding and an **author decision** — it cannot be
smuggled into a caption. **The real remedy is Phase 3: extend the byte-stability KAT to D ≥ 50**,
which converts C3 from asserted to demonstrated; the probes above are a working prototype.

**Why every gate passed over it:** `validate_cross_format_parity` was green because the PDF and the
DOCX agree — both carrying the same wrong caption — and `validate_evidence_bindings` excludes
`% BIND:` comment text from token extraction by design. This is the third defect in this project
caught only by reading the built PDF rather than the sources. **Read the PDF.**

**VERIFICATION COMPLETE — all 12 claims verified and adversarially challenged.** Two runs: the
first was interrupted after 11 verdicts and 4 challenges; the second supplied the missing 7
challenges and a merged work order. Every verdict below has been attacked from the opposite
direction at least once.

| # | The charge | Final verdict | Severity | Act? |
|---|---|---|---|---|
| C1 | Table A45 caption contradicts its own tie counts | **CONFIRMED** | serious | **yes** |
| C2 | "this is stated wherever those claims appear" — self-audit is false | **VERIFIED** | serious | **yes** |
| C3 | "as on the other suites, the population rule was not a controlled variable" | **VERIFIED — stale text** (challenge *overturned* AMBIGUOUS) | moderate | **yes** |
| C4 | "the population rule is not the source of the reported standing" | **REFUTED** | cosmetic | **no — and its proposed fix is a regression** |
| C5 | "no constant tested here is knife-edge" vs the n_min 2→1 flip | AMBIGUOUS-NOT-FALSE | cosmetic | deferred |
| C6 | "perturbs no tier threshold" vs `argp_threshold` and S5.9 | **VERIFIED** — internal contradiction | serious | **yes** |
| C7 | "identical in every variant reported here" | AMBIGUOUS-NOT-FALSE | moderate | **yes** — 2 sites, not 1 |
| C8 | "only fitness-affecting channel" vs two active channels | **VERIFIED** (*upgraded* from PARTLY) | serious | **yes** |
| C9 | the same two sentences, framed as a contradiction | **VERIFIED** | serious | **merged into C8** |
| C10 | "four orders of magnitude behind" on the worst function | **VERIFIED** (*upgraded* from PARTLY) | serious | **yes** |
| C11 | S9.3 transplant leaves the disclosure incomplete | AMBIGUOUS-NOT-FALSE (*changed* from REFUTED) | moderate | deferrable |
| C12 | Overall column at matched NP is never reported | PARTLY-VERIFIED | moderate | **yes** — but not as proposed |

**The diagnoses held; the prescriptions did not.** Of the 7 claims challenged in the second run,
**7 of 7 verdicts survived** — but **7 of 7 proposed fixes were judged unsafe as written**. Add the
first run and the count is 11 of 12 verdicts standing while nearly every minimal fix needed
rewriting. Treat a verifier's *diagnosis* as strong evidence and its *proposed replacement* as a
first draft. Every rejected replacement, with its reason, is in §2b §3 — do not re-litigate them.

**⚠ CORRECTION — earlier guidance in this file was wrong and reached `origin/main`.** An earlier
revision of this section said the fixes "undercount their sites" because they miss the
`_pandoc.tex` mirrors, and listed those files as sites to edit. **That remedy is wrong.**
`papers/main_pandoc.tex` and `papers/supplementary_pandoc.tex` are **generated shims**:
`papers/scripts/build_docx.py:2910` does `spec["shim"].write_text(build_shim(doc_kind))`, and its
docstring at line 46 states "the shim files are overwritten on every run." **Hand-editing them is
clobbered on the next build and yields false completion.** The underlying worry was real — a
`.tex`-only edit with no rebuild does leave the DOCX carrying the defect and does fail
`validate_cross_format_parity` — but the obligation is to **rebuild**, not to edit the mirror. Both
the C8 and C9 dossiers made this same error, and so did this file. Edit canonical sources only;
regenerate everything downstream (§2b §6).

**New trap, found this pass: the BIND window truncates silently — and it is smaller than 6 lines.**
`validate_evidence_bindings.py` sets `budget = 2 if inline else 6`, so a standalone `% BIND:` reaches
back at most **6 non-blank lines** — but the walk **also stops early** at a blank line and at any
`STOP_LINE`, which matches `\section`/`\subsection`, `\paragraph`, `\caption`, and
`\begin{`/`\end{` of `figure|table|equation|algorithm`. Adding lines to a bound paragraph can push
its earliest lines out of the window, un-binding the numbers they carry — **and the gate still
exits 0**. This is the fourth defect class here that no gate detects.

⚠ **The early stop cuts both ways, and it invalidated one of this file's own constraints.** The
Table A45 caption was assumed to be inside BIND@`:3788`'s window; it is not — the walk hits
`\end{table}` immediately, so the context is that single line and `extract_tokens` returns `[]`.
Growing that caption to 8 lines changes 0 of 192 BIND contexts. **The line-count caps recorded for
E1–E12 in §2b were computed without `STOP_LINE`; re-verify each against the real algorithm before
treating a cap as binding.** A cap that is too tight only costs wording quality — but the reasoning
behind it should not be trusted as stated.

**C4's proposed fix is a trap, and the challenge caught it.** Inserting "overall" would retarget the
sentence at a four-dimension aggregate under NP = 100 that appears nowhere in the shipped record —
`SA06.tex` has no Overall row, `e2_np100.json` has no aggregate key — on a bind-tagged paragraph. It
would convert a self-resolving ambiguity into an unsupported thin-margin assertion on the exact page
a reviewer is auditing. **C4 needs no edit at all.**

**C12's contested number is settled by recomputation.** Independently recomputed here over the
7-algorithm panel, 29 functions x 51 runs, Friedman mean rank per dimension, Overall = unweighted
mean of the four. The method reproduces the paper's own printed shipped values exactly (2.4828 →
"2.48"; 2.9612 → "2.96"), then gives at matched NP = 100: **DT-GSK 2.7802, eGSK 2.8578**, margin
**0.078**. So **2.8578 is right and 2.8621 is wrong.** The surviving margin is carried entirely by
D = 10 (+0.379) against −0.302 from the other three combined — at matched population eGSK holds the
better mean rank at D = 30, D = 50 **and** D = 100. That asymmetry is why the work order's C12 edit
is a *relativity warning*, not a restatement of aggregate superiority.

**C10 is confirmed by recomputation.** From the strict source — coordinate arm
`benchmarks/cec_reference_results/_revision/e1_basis_coordinate/dt-gsk/cec2017/summary/per_run.csv`
against the shipped eigenframe arm `benchmarks/cec_reference_results/cec2017/dt-gsk/per_run.csv`,
29 functions x 51 runs at D = 50. Worst function F6: eigenframe 8.345e-05 vs coordinate 7.716e-07,
ratio **108.2 = 2.03 orders of magnitude**, where the Supplementary says "four orders". Next worst
is F29 at 1.245x, so "the single worst function" stays a correct referent. The bound artifact
`e1_basis_contrast.json` carries no per-function means and line 3700 has never sat inside a BIND
window — two independent reasons no gate could have caught it.

**Where the raw verdicts live.** Run 1 (11 verdicts + 4 challenges) was `wf_31d2bb3d-9ef` under
session `fa6ff0bb-d40d-4a30-8407-92084aef9ddc`; run 2 (7 challenges + the work order) was
`wf_b1409a58-c62` under session `143653b9-1268-4566-b408-14f8572a63c2`. Both journals sit at
`~/.claude/projects/D--AI-Research-Lab-DT-GSK/<session>/subagents/workflows/<run>/journal.jsonl`,
one `{"type":"result"}` line per agent, each carrying evidence and reasoning far longer than the
summary above. **Session scratch is transient** — the decision-relevant content has been distilled
into §2b; copy the journals out if the full argument is ever needed.

**A leaked meta-note was published and is now removed.** An agent's instruction to the applier
("[APPLY NOTE: join these two lines with CRLF...]") was written into this file verbatim and reached
`origin/main`. The applier matched and wrote proposed text without checking the *replacement* for
meta-content. A tree-wide scan found no others. If you apply agent-proposed edits, scan the
replacements, not just the anchors.

## 2b. Pass-42 work order — verified, not yet applied

Produced by the challenge run and **checked here before being recorded**: all 21 FROM anchors were
confirmed to exist byte-exactly and **exactly once** in their files, with the line endings stated;
`build_docx.py`'s shim overwrite, the 6-line BIND window, and every per-file line ending in §0 were
re-verified against the working tree. **Nothing below has been applied.** Line numbers are as of
`60708a0`; this section's own edits to `REVISION_STATUS.md` (E11e) shift with any edit to §2a, so
re-locate by anchor text, never by line number.

**⚠ COVERAGE GAP — this work order covers C6–C12 only.** E1–E12 discharge C6, C7, C8, C9, C10,
C11 and C12. **C1, C2 and C3 have no specified edits here.** Their draft fixes exist only in the
run-1 dossiers, and those were never safety-audited — which matters, because when the run-2
challenge did audit prescriptions it rejected **7 of 7**. Before applying anything for C1/C2/C3,
draft and challenge their edits the same way:

- **C1 (Table A45 caption)** — the anchor defect, and the only one that is not a wording fix. It
  needs the author decision in §6 item 2 first, because what the caption should say depends on
  which of the three responses is chosen. No edit can be drafted until then.
- **C2** — run-1 proposed naming the two sections that actually carry the qualification
  (Sections 3.2 and 4.9) at `supplementary.tex:3749`, plus `DT-GSK-plain-summary.tex:273`.
  Anchor unverified, wording unaudited.
- **C3** — run-1 proposed replacing the universal "as on the other suites" clause at
  `supplementary.tex:2481–2482` with a scoped statement pointing at S9.2. Anchor unverified,
  wording unaudited.

**⚠ NAMING COLLISION — do not conflate two different C1/C2/C3.** The defect ids in §2a/§2b
(C1…C12) are unrelated to the manuscript's **contribution** ids C1/C2/C3 (deterministic final
polish / dimension-tiered scaffold / evaluation-integrity infrastructure). When §2a says the
Table A45 residual "sits in tension with contribution C3", that is the *byte-stable determinism*
contribution — **not** defect C3, which is the stale population-rule sentence. Read every C-number
in context.

**Scope:** 7 challenged claims (C6–C12) + C1/C2/C3 carried from the earlier settlement. **C4 = NO EDIT** (fix rejected as a regression). **C5 = cosmetic, deferred.**
**Governance:** new freeze pass **pass-42**, tag **v2.15**, ids **CR-0025 / D-0050** — verify both free at apply time (`papers/governance/decision_log.md`). Never edit the tagged pass-41 state in place (D-0045).

---

### 0. Verified facts that govern every edit

| Fact | Value (verified on disk this session) |
|---|---|
| LF files | `papers/sections/conclusions.tex` (203/0), `sections/introduction.tex` (165/0), `papers/cover_letter.tex`, `papers/cover_letter.md`, `papers/DT-GSK-plain-summary.tex`, `README.md`, `docs/**/*.md` |
| CRLF files | `papers/sections/performance.tex` (1258/1258), `papers/supplementary.tex` (3869/3869), `papers/main_pandoc.tex` (3852/3852), `papers/supplementary_pandoc.tex` (3863/3863), `REVISION_STATUS.md` (666/666), `papers/tables/SA06.tex`, `papers/tables/word_sources/SA06.json` |
| `*_pandoc.tex` | **DERIVED.** `papers/scripts/build_docx.py:2910` does `spec["shim"].write_text(build_shim(doc_kind))`; docstring line 46: "the shim files are overwritten on every run." **Regenerate, never hand-edit.** |
| BIND window | `validate_evidence_bindings.py:103` — `budget = 2 if inline else 6`. A standalone `% BIND:` annotates the **6 preceding non-blank lines**. Adding lines to a paragraph silently evicts its earliest lines. Gate still exits 0 — the loss is invisible. |
| Freeze manifest | `papers/governance/main_manuscript_freeze_manifest.json` hashes **15** files: `main.tex`, the 5 `sections/*.tex`, `DT-GSK.pdf`, `DT-GSK.docx`, `supplementary.pdf`, `supplementary.docx`, `cover_letter.pdf`, 3 governance CSVs, `references.bib`. **`supplementary.tex` and `cover_letter.tex` are NOT hashed; their renders are.** |
| Submission zip | `papers/submission/DT-GSK-latex-source.zip` bundles `main.tex`, `sections/{introduction,related_work,proposed_algorithm,performance,conclusions}.tex`, `DT-GSK.pdf`. **It does NOT contain `supplementary.tex`** — supplement-only edits do not require re-zipping; main-document edits do. |
| Build epochs | PDF `SOURCE_DATE_EPOCH=1783468800`; **DOCX `1783641600`** (`papers/build_prompt_phases/cr_0006_apgsk_recovery/cr0006_verification.md:5`). A persisted shell var yields a non-reproducible DOCX that still passes `check_manifest`. |

**Apply order within each file: highest line number first**, so cited line numbers stay valid.

---

### 1. Ordered edit list

#### E1 — C6 · main text · `papers/sections/conclusions.tex:92–93` **(LF)**

FROM (2 lines, LF newline):
```
and perturbs no
tier threshold; the tier constants themselves remain frozen and hash-locked.
```
TO (2 lines, LF newline):
```
and leaves the
dimension-tier boundaries themselves unvaried, so their sensitivity is untested.
```
**Discharges:** C6 (VERIFIED / serious). Removes a clause that is false under the only sense the paper defines for "tier threshold" (`tau_argp`, main p.16/p.17, supp pp.46/48 — E4 ran it at 0.016/0.024) and a second clause the E4 sweep also falsifies (it perturbed `local_search_eval_budget_frac` and `local_search_elite_count`, two rows of S5.9's own tier-constants table).
**Line count 2→2 by design** — preserves the 6-line window of `% BIND: E4 …` at `:96`. Do not use a 3-line variant: it evicts line 90 (`$D = 30$`, `$D = 100$`).

#### E2 — C6 · supplement · `papers/supplementary.tex:1413–1414` **(CRLF)**

FROM (2 lines, CRLF newline):
```
and it perturbs no tier threshold; the tier constants
themselves remain frozen and hash-locked.
```
TO (2 lines, CRLF newline):
```
and it leaves the dimension-tier boundaries
themselves unvaried, so their sensitivity is untested.
```
**Discharges:** C6, second canonical site.
⚠ The match **must stop at `hash-locked.`** — the file has **two spaces** before `Neither ARGP`. Do not absorb them.
⚠ The two C6 sites are **not** identical text (the dossier said they were). Supp has `it`, wraps after `constants`, is CRLF, and double-spaces the sentence break. Two separate exact-match edits, never one shared string.

#### E3 — C7 · `papers/sections/performance.tex:618–619` **(CRLF)**

FROM (2 lines, CRLF newline):
```
are identical in
every variant reported here, but
```
TO (2 lines, CRLF newline):
```
are identical under
both of these robustness variants, but
```
**Discharges:** C7 (AMBIGUOUS-NOT-FALSE / moderate). `under` matches the existing restatements at `conclusions.tex:79-81` and `performance.tex:1249-1251`. Line count 2→2; `% BIND: AN-ROB-2017-01, AN-ROB-2017-04` at `:616` unaffected.

#### E4 — C7 · `papers/supplementary.tex:562–563` **(CRLF)**

FROM (2 lines, CRLF newline):
```
is identical in every
variant reported here, but
```
TO (2 lines, CRLF newline):
```
is identical under both of these
robustness variants, but
```
**Discharges:** C7, second site. The C7 dossier said "No change needed in supplementary.tex line 562" — **wrong**: this is the one document that prints both counterexamples (Table A44 supp p.75; Table A46 supp p.77), and the phrase **wraps the 562/563 break**, so a single-line matcher finds nothing. Line count 2→2; `% BIND: RANK-ROBUSTNESS` at `:566` unaffected.

#### E5 — **C8 + C9 MERGED** · four sites, one replacement string

**Chosen wording: C9's `terminal exploitation channel`.** *Justification (one sentence): it keeps the possessive frame `the memory's ___ channel` so the ISM attribution survives at the sentence carrying the ISM verdict, both halves already render in the shipped PDFs (`terminally, the eigenframe polish` main p.19; `exploitation channels` main p.3; `this exploitation channel` supp p.74), its definite article now picks out something genuinely unique, and one identical string serves every site — whereas C8's `the channel that experiment isolates` drops `the memory's`, uses a bare demonstrative, is not shipped vocabulary, and is itself mildly false (E1 isolated the direction set *inside* a channel that ran live in all three arms).*

**E5a — `papers/sections/introduction.tex:152` (LF, single long line)**
FROM: `in the memory's only fitness-affecting channel, the polish basis,`
TO: `in the memory's terminal exploitation channel, the polish basis,`

**E5b — `papers/sections/conclusions.tex:170` (LF, whole line)**
FROM: `memory's only fitness-affecting channel --- the basis the final polish searches`
TO: `memory's terminal exploitation channel --- the basis the final polish searches`

**E5c — `papers/cover_letter.tex:57` (LF, single long line)**
FROM: `active harm in its only fitness-affecting channel`
TO: `active harm in its terminal exploitation channel`

**E5d — `papers/cover_letter.md:23` (LF, single long line)**
FROM: `active harm in its only fitness-affecting channel`
TO: `active harm in its terminal exploitation channel`

**Discharges:** C8 **and** C9 (both VERIFIED / serious) in one pass. The claim is refuted by the paper's own `proposed_algorithm.tex:548-552` ("two active channels"), shipped Table 4/9 stage header ("3. Exploit (two active channels)"), Section 5's own opening two pages earlier ("consumed twice"), and the roadmap sentence *on page 3 itself* ("its exploitation channels", plural).
All four edits are single-line, line count unchanged. `conclusions.tex` BINDs at `:168` (covers 162-167) and `:178` (covers 172-177) both unaffected — line 170 sits between them.

#### E6 — C8 secondary · S6.5 parenthetical · `papers/supplementary.tex:2283–2286` **(CRLF)**

FROM (4 lines, CRLF newline):
```
(and the no\_sgsm row, in which the
polish runs on coordinate axes rather than the learned eigenbasis, is itself
null, so the significant effect is the compass endgame, not the learned basis
specifically).
```
TO (4 lines, CRLF newline):
```
(the no\_sgsm row is itself null, but it
disables the memory entirely --- removing its linkage channel as well as its
eigenbasis --- so it cannot separate the basis from the endgame;
Section~S9.1 does that directly).
```
**Discharges:** C8's same-root secondary defect — the current parenthetical reaches a correct destination by an invalid route and contradicts "remains unidentified" eight lines above at `:2276-2277`.
⚠ **`local-search` clause deliberately omitted.** C8's proposed replacement said the memory's "local-search channels"; the ISM-block subspace LS is **not enabled** (`proposed_algorithm.tex:550-552`, `:570-574`, Table 4; `_dt_core.py:4175` gates on `local_search_auto_subspace`, which `pub_overrides()` returns `False` at every tier). Applying it as written would ship a new falsehood and raise the active-channel count from 2 to 3.
`linkage channel` is verbatim shipped (`supplementary.tex:3666-3668`). Line count 4→4. This text lies *after* the BIND at `:2256-2258`, so it is in no BIND window; no bind change needed.

#### E7 — C10 · `papers/supplementary.tex:3699–3700` **(CRLF)**

FROM (2 lines, CRLF newline):
```
and the single worst
function shows the eigenframe arm four orders of magnitude behind.
```
TO (2 lines, CRLF newline):
```
and the single worst
function shows the eigenframe arm two orders of magnitude behind.
```
**Discharges:** C10 (VERIFIED / serious). F6 at D=50: eigenframe `8.345223e-05` vs coordinate `7.715655e-07` = **108.16× = 2.034 orders**. Wrong by ~100×. No statistic reaches 4 orders under any like-for-like per-function convention at either dimension. `two` is true and conservative; `the single worst function` remains a correct referent (next worst is F29 at 1.245×). Asserts strictly *less* than the current text, so it needs no new binding. Line count 2→2. (Note: the E1 headline BIND is at **`:3711`**, not `:3712` as the C10 report stated; line 3700 has never been inside any BIND window — the second reason no gate caught this.)

#### E8 — C11 · `papers/supplementary.tex:3758–3762` **(CRLF)** — lowest priority, deferrable

**E8a** — FROM: `comparison by transplant: the parameter set resolved at $D = 10$, and separately`
TO: `comparison by transplant: the $D = 10$ tier's parameter dictionary, and separately`

**E8b** — FROM: `the set resolved at $D = 100$, are applied unchanged at every dimension and`
TO: `the $D = 100$ tier's dictionary, are applied unchanged at every dimension and`

**E8c** — insert **exactly 3 lines** after `differ between them.` (line 3762), before the `% BIND: E3 design …` at `:3763`:
```
  Each arm applies its tier's dictionary over the
configuration the profile resolves at the target dimension, so any field the
carried dictionary does not name keeps that dimension's value.
```
**Discharges:** C11, corrected to **AMBIGUOUS-NOT-FALSE / moderate** (`verdict_holds: false` on the original REFUTED). Nothing shipped is untrue — `88 keys differ` reconciles only under the override-dictionary reading — but the verb *resolved* points at `build_pub_config`, which is the resolution function, and a competent reader already drew the false inference that the transplant disables the polish and the ISM. It does not: `dt_gsk.py:242-256` does a **partial** `dataclasses.replace` overlay, and the U-low YAML carries 40 keys with **no** `final_polish_*` and **no** `interaction_*` key.
⚠ **Hard cap: ≤3 added lines.** At +3 the E3 BIND window becomes 3760-3765 and `88` (line 3761) survives. At +5 (the rejected fix's length) `88` is evicted silently.
⚠ **`13 of the 72` from the C11 dossier is REJECTED** — 13 resolved fields differ at D=50 but only **12** are in `pub_overrides(50)` (`bse_restart_frac` is not); at D=100 it is **11 of 108**, not a constant over `$D \ge 50$`.

#### E9 — C12 · `papers/supplementary.tex` · append at end of S9.2 closing paragraph, after line 3750, **before** `% BIND: E2 headline` at `:3751` **(CRLF)**

Insert (8 lines, CRLF newline):
```
  Friedman ranks are relative:
substituting the \dtgsk{} column re-ranks the whole panel, so the six
comparator columns move as well.  No entry here may be differenced against the
corresponding entry in the main-text rank table, and no descriptive aggregate
formed from this table is comparable with the one reported there.  $D = 10$ is
also the one dimension at which $NP = 5D$ falls below the panel constant, so
the control raises rather than lowers \dtgsk{}'s initial population there; the
paired difference at that dimension is nonetheless indistinguishable from zero
(Holm $p = 0.517$).
```
**Discharges:** C12 (PARTLY-VERIFIED / moderate). Kills the wrong completion the printed exhibits currently license: averaging Table A44's four re-ranked ranks gives 2.780, differenced against Table 14's 2.961 gives 0.181 — **2.3× the true 0.078**, because all six comparator columns also move (eGSK alone shifts 0.103, larger than the surviving margin).
✅ Every numeric token is shipped: `0.517` prints in `papers/tables/SA06.tex:9` (Table A44), `$NP = 5D$` is that table's own header, `$D = 10$` is everywhere. Placing this *before* the BIND puts those tokens **inside** the E2 window — deliberate.
⚠ Uses **"the main-text rank table"**, never `Table~14`: the supplement never hardcodes main-text table numbers (`supplementary.tex:545`, `:1119`, `:2380` all use the descriptive form).
⚠ **C12's own proposed sentence is REJECTED**: `still panel-best, but a margin of 0.08 rather than Table 14's 0.48` re-asserts aggregate superiority in the supplement answering **R2.5**, which the authors already marked *accepted and applied*; and `2.858` is in no bound artifact (`e2_np100.json` carries no comparator rank), while the remediation it prescribes emits `2.862`. Also rejected: `improves its mean rank from 2.879 to 2.724` — causal register, contradicted three sentences later by the paper's own Holm p = 0.517 (W/T/L 10/4/15).

#### E10 — C9 extension · `papers/DT-GSK-plain-summary.tex` **(LF)** — plain register, not the manuscript wording

**E10a — lines 488–489**
FROM: `In the one`⏎`place it could change the answer, it subtracted`
TO: `In the route`⏎`that was tested, it subtracted`

**E10b — lines 482–483**
FROM: `The pair-map's only route to affecting the`⏎`answer is the basis it hands the deterministic polish,`
TO: `The route this test could isolate is the`⏎`basis the pair-map hands the deterministic polish,`

**Discharges:** C9's two sites that **neither C8 nor the REVISION_STATUS site table found**. This shipped PDF (p.5) carries the falsehood in its starkest form and **self-refutes it on p.4** (line 377: "Nor is the crossover the memory's only route into the search"). `terminal exploitation channel` is the wrong register for a deliberately jargon-free document — do not transplant E5's string here. No `_pandoc` mirror exists; two lines in one LF file. Line counts preserved.

#### E11 — non-manuscript tranche (public at v2.14) · same claim as E5

| # | File (ending) | FROM | TO |
|---|---|---|---|
| E11a | `README.md:115-116` (LF) | `in the memory's only`⏎`fitness-affecting channel -- the basis` | `in the memory's terminal`⏎`exploitation channel -- the basis` |
| E11b | `docs/algorithms/dt-gsk.md:516` (LF) | `the memory's only fitness-affecting channel — the basis the deterministic final` | `the memory's terminal exploitation channel — the basis the deterministic final` |
| E11c | `docs/getting-started/explainer.md:79-80` (LF) | `in the memory's only fitness-affecting`⏎`channel — the basis` | `in the memory's terminal exploitation`⏎`channel — the basis` |
| E11d | `docs/reference/glossary.md:36` (LF, long line) | `in the memory's only fitness-affecting channel, the polish basis,` | `in the memory's terminal exploitation channel, the polish basis,` |
| E11e | `REVISION_STATUS.md:485-486` (**CRLF**) | `to harm in its only`⏎`fitness-affecting channel;` | `to harm in its terminal`⏎`exploitation channel;` |

⚠ E11b/c/d use a real **em dash U+2014**, not `---`. Match bytes exactly.
⚠ `docs/html/algorithms_dt-gsk.html:337`, `docs/html/getting-started_explainer.html:190`, `docs/html/reference_glossary.html:165` are **generated** — run `python scripts/build_docs_html.py`, never hand-edit.

#### E12 — reviewer-facing, untracked · `papers/review_2026_08_24/response_to_reviewers.md` **(LF, gitignored at `.gitignore:56` per D-0049)**

**E12a — lines 366–367** — the strongest form of the falsehood anywhere in the record
FROM: `ISM has exactly one`⏎`fitness-affecting channel — the basis it supplies to the final polish — and in that channel it is`
TO: `ISM's terminal exploitation`⏎`channel is the basis it supplies to the final polish, and in that channel it is`

**E12b — line 526**
FROM: `harmful in its only fitness-affecting channel`
TO: `harmful in its terminal exploitation channel`

**Why it matters:** this file is invisible to any tracked-files sweep but **goes to the reviewers with the resubmission**, and it tells them flatly something the methods section they are reading refutes.

---

### 2. OPTIONAL — specify, but defer unless the author asks

#### O1 — C12 caption relativity note (2 renders + 1 generator)
- `papers/supplementary.tex:3733` (CRLF): `column substituted.  The paired test compares` → `column substituted; because Friedman ranks are relative, the comparator columns`⏎`re-rank as well.  The paired test compares` **(+1 line; BIND at `:3739` shifts — acceptable, tokens are trivial)**
- `papers/scripts/generate_revision_exhibits.py:164-165`: append the same clause to the `caption=` string, then re-run to regenerate `papers/tables/word_sources/SA06.json:4` `caption_stub` (the string the **native DOCX** caption is built from).
- `papers/supplementary.tex:3835` (Table A46, identical wording) + `SA08` caption in the same generator — consistency only.

**Cost:** touches a generated exhibit chain (generator → `tables/SA0*.tex` + `word_sources/*.json` → native DOCX table) and re-runs `validate_cross_format_parity`'s generated-table check. **The E9 body append already discharges the harm.** Give this its own ticket if wanted.

#### O2 — C9 addendum (linkage channel live in all E1 arms)
Insert **after** the existing `% BIND: E1 (rev-rel-2026-08-26-dd42d37eb); C1 basis-neutral` at `conclusions.tex:178`, then add a fresh standalone BIND below it:
```
All three arms of that contrast ran with the memory and its linkage channel
live, so the comparison isolates the direction set the polish searches along,
not the memory as a whole.
% BIND: E1 (rev-rel-2026-08-26-dd42d37eb); linkage channel live in all arms
```
Placing it **after** line 178 leaves that BIND's window (172-177, carrying `$D = 50$`, `1.4\times10^{-4}`, `25`, `29`) intact. Inserting it *before* line 178 — as C9 directed — silently evicts line 172 and un-binds the passage's own numbers while the gate still exits 0. Content is true and number-free (verified: all three E1 `run_config.json` carry `interaction_graph_enabled: true`; the coordinate arm's note reads "ISM live, linkage live").

---

### 3. REJECTED / DEFERRED replacements — do not re-litigate

| Source | Rejected text | Reason |
|---|---|---|
| C6 dossier | `the … cuts themselves remain frozen and hash-locked` | Reproduces the vacuity it diagnoses (E4 edited no file — every perturbation is a runtime `optimizer_options` override, so "frozen and hash-locked" is true of every constant swept or not); converts a Limitations disclosure into a provenance **boast** about the paper's largest untested design choice; `cuts` appears nowhere in either document; its four-cut enumeration collides with `supplementary.tex:1539`'s three-boundaries-plus-extension (S14-016). Same failure class as the rejected C4 fix. |
| C7 dossier | `every variant of this prespecified battery` | CEC2020 has a prespecified battery too, and its median re-rank **does** move a DT-GSK ordinal (D=15, third→second; supp p.68, stated main p.41). Reopens the ambiguity across suites. |
| C8 dossier | `removes the memory's linkage **and local-search** channels` | The ISM-block subspace LS is not enabled in the frozen configuration; would ship a new falsehood and a fresh main-vs-supp contradiction. |
| C8 dossier | `In the channel that experiment isolates` | Superseded by E5; drops `the memory's`, bare demonstrative, unshipped vocabulary, and E1 isolated the *direction set*, not the channel. |
| C10 dossier | `(F6: $8.3\times10^{-5}$ versus $7.7\times10^{-7}$)` | Two numeric literals present in **no** exhibit and **not** in `e1_basis_contrast.json` (which carries no per-function value of any kind). Admissible only by extending the BIND at `:3711` to name `_revision/e1_basis_coordinate` + `cec2017/dt-gsk` per-run CSVs. Deferred. |
| C10 dossier "Fix 2" | A12-conventions sentence in the S9 preamble | Out of C10's scope; falls **inside** the `rev-rel-…` BIND window, making 0.5/0.56/0.64/0.71 gate-enforced; and S9's preamble contains no conventions sentence. **Raise separately** — there is a real defect: the same contrast prints `0.59` in Table A25 (mean-per-function, `regen_cec2017_contrasts.py:125`) and `0.511` in Table A43 (pooled all-pairs, `analyze_revision_experiments.py:126/131`), same data, same precision, no distinguishing note. |
| C11 dossier | `differs from it on 13 of the 72 fields` | Wrong: 13 resolved fields differ at D=50 but only 12 are in `pub_overrides(50)`; at D=100 it is 11 of 108. Also filed under a BIND naming a key-diff artifact that holds no resolved-config data, and its 5 added lines evict `88`. |
| C11 dossier | `retains the tiered leg's final polish and interaction-structure memory **unchanged**` | The ISM's own 29 params survive, but its consumers do not (`linkage_min_dim` 30→10, `linkage_block_refresh_period` 10→20, four `local_search_*`). "Unchanged" invites the over-reading the next paragraph forbids. |
| C12 dossier | `still panel-best, but a margin of 0.08 rather than Table 14's 0.48`; `2.858`; `improves … from 2.879 to 2.724` | R2.5 regression; `2.858` unbindable and its own prescribed remediation emits `2.862`; causal claim contradicted by Holm p = 0.517. |
| C12 dossier | Add an eGSK column + Overall row to `SA06` | New evidence release + 2 generator edits + reshaped native DOCX table + 2 more validators. Not "a regeneration, not a retype." |
| C4 (settled) | its proposed fix | Already rejected as a regression. **NO EDIT.** |

---

### 4. DO-NOT-EDIT — with reasons, so nobody reopens them

1. **`src/gsk_family/optimizers/_dt_core.py:2035, 4765, 4828, 4844`** — `only fitness-affecting` here means the **FC4 lift-EMA telemetry**, a different and *correct* sense. The module is on the SHIPPED hash list at `papers/scripts/validate_provenance_claims.py:54`; **even a comment edit fails the gate** (CLAUDE.md rule 1). A global find/replace on `only fitness-affecting` hits this file — do not do a global replace.
2. **`docs/development/dt_gsk_core_reference.md:121`** and **`docs/html/development_dt_gsk_core_reference.html:202`** — same telemetry sense, correct as written.
3. **`papers/review_2026_08_24/revision_experiments_preregistration.md:170`** (`ISM's fitness-affecting channel`, singular) — D-0049 keeps the pre-registration public *precisely* so adverse-outcome wording can be shown to predate the outcomes. Editing it destroys the property it exists to prove.
4. **`REVISION_STATUS.md:111`** — must keep quoting the defective phrase to track C8. (Line 485-486 *is* edited: E11e — it asserts the claim as fact.)
5. **`papers/review_2026_07_22/desk_screening_report.md:409, 772`**; **`papers/build_prompt_phases/phase_07/captions_registry.md:49`**; **`papers/build_prompt_phases/phase_08/paragraph_evidence_audit.csv:328`** — append-only trees (CLAUDE.md rule 6). Stale content there is correct.
6. **`papers/main_pandoc.tex`, `papers/supplementary_pandoc.tex`** — generated shims, overwritten every `build_docx.py` run. Hand-editing is clobbered and yields **false completion**. Both C8 ("mirrors") and C9 ("if they are re-issued") got this wrong in the same direction. Regenerate.
7. **`papers/tables/SA0*.tex`, `papers/tables/word_sources/*.json`, `docs/html/*.html`** — generated (`SA06.tex:1` says so explicitly). Regenerate via their generators.
8. **`papers/analysis/rev-rel-2026-08-26-dd42d37eb/*.json`** and **`benchmarks/cec_reference_results/**`** — frozen evidence (CLAUDE.md rule 2). No number in this pass changes; nothing here is touched.
9. **`papers/sections/conclusions.tex:101`**, **`papers/supplementary.tex:1331`**, **`papers/supplementary.tex:1706`** — TRUE statements that *invite* the C11 misreading ("gated to $D \geq 50$", "base-configuration defaults are 0.985, full budget and disabled"). They are true of DT-GSK's own profile. **Do not "fix" them.**
10. **`papers/supplementary.tex:1539`** — the three-boundaries-plus-extension sentence that collides with main Table 5's four dimension tiers. Pre-existing (S14-016), out of scope for pass-42, and E1/E2's wording deliberately enumerates nothing so as not to make it conspicuous.
11. **`papers/scripts/finalize_evidence.py`** — standing instruction: never run it.

---

### 5. New numbers / terms — BIND audit (requirement 5)

| Edit | Introduces | Shipped? | Action |
|---|---|---|---|
| E1/E2 | `dimension-tier boundaries` | `dimension tiers` (main Table 5 caption) + `tier boundaries` (`supplementary.tex:1539`, supp PDF p.45) | **Composed from shipped vocabulary. No numeral. No BIND.** |
| E1/E2 | — no numeral — | — | The E4 BIND at `conclusions.tex:96` keeps its window (line count held at 2). |
| E3/E4 | `robustness variants` | `the prespecified r01/r04 robustness variants` (supp p.11); `All three registered robustness variants` (p.68) | **Shipped. No numeral. No BIND.** Text moves *toward* both binds (`AN-ROB-2017-01/04`; `RANK-ROBUSTNESS`), which name exactly the r01/r04 pair. |
| E5 | `terminal exploitation channel` | `terminally, the eigenframe polish` (main p.19), `exploitation channels` (main p.3), `this exploitation channel` (supp p.74) | **Composed from rendered vocabulary. No numeral. No BIND.** Both `conclusions.tex` BIND windows unaffected. |
| E6 | `linkage channel`; `Section~S9.1` | verbatim `supplementary.tex:3666-3668`; S9.1 is a shipped label | **No BIND** — the text sits after the `:2256-2258` BIND, inside no window. |
| E7 | `two orders of magnitude` | word, not a numeric token; asserts strictly **less** than current text | **No BIND** (line 3700 has never been in a BIND window — noted as a residual, not fixed here). |
| E8 | `parameter dictionary` | `parameter set` (:3758) + `dictionaries` (:3760), same paragraph | **No numeral. No BIND.** ⚠ `override` does not render in supplement prose — do **not** write "override dictionary". |
| E8c | — no numeral by construction — | — | **≤3 lines is a hard constraint**; at +3 `88` (line 3761) stays inside the E3 BIND window. |
| **E9** | `0.517`, `$D = 10$`, `$NP = 5D$` | **`0.517` prints in `papers/tables/SA06.tex:9`** → Table A44, both renders; `$NP = 5D$` is that table's header | **All shipped. No new BIND.** Deliberately placed *inside* the existing `% BIND: E2 headline` window at `:3751` so the tokens are gate-enforced in both formats. |
| E10 | `the route that was tested` | plain register, no term of art | **No BIND** (plain summary carries none). |
| O2 | — none — | — | Requires its **own** standalone BIND line, placed *after* the existing one at `:178`. |

**Nothing in this pass adds an unbindable number.** Every rejected item in §3 that does add one is rejected for that reason.

---

### 6. Rebuild, re-mint, validate

**Files edited → downstream obligations:**

| Edited | Rebuild |
|---|---|
| `sections/introduction.tex`, `sections/conclusions.tex`, `sections/performance.tex` | `DT-GSK.pdf` (epoch **1783468800**) → `build_docx.py` (epoch **1783641600**, regenerates `main_pandoc.tex`) → `DT-GSK.docx` → **re-run `papers/scripts/build_submission_zips.py`** (the zip bundles all three edited section files **and** `DT-GSK.pdf`) |
| `supplementary.tex` | `supplementary.pdf` (1783468800) → `build_docx.py --supplementary` (1783641600, regenerates `supplementary_pandoc.tex`) → `supplementary.docx`. **Not** in the submission zip. |
| `cover_letter.tex` (+ `.md` mirror) | `cover_letter.pdf` |
| `DT-GSK-plain-summary.tex` | `DT-GSK-plain-summary.pdf` (not manifest-hashed) |
| `docs/**/*.md` | `python scripts/build_docs_html.py` |

**Freeze manifest re-mint** — `papers/governance/main_manuscript_freeze_manifest.json`, **8 of 15 hashed entries change**: `sections/introduction.tex`, `sections/performance.tex`, `sections/conclusions.tex`, `DT-GSK.pdf`, `DT-GSK.docx`, `supplementary.pdf`, `supplementary.docx`, `cover_letter.pdf`. Manifest is **CRLF + 2-space** — re-mint surgically per its own `remint_note`; `sed -i` / `read_text()` normalise to LF and break the hashes. Set `published_commit` alongside `anchor_commit` (publication is a squash; the anchor does not resolve publicly).

**Validators (all must pass before tagging):**
```
validate_provenance_claims.py      # must still pass — NO src/ file is touched
validate_evidence_bindings.py      # exit 0; also eyeball the windows named above
validate_cross_format_parity.py    # PDF vs DOCX body paragraphs, both documents
validate_document_consistency.py   # M-003 main/conclusion/supplement drift
validate_docx.py  validate_artifact_labels.py  validate_build_hygiene.py
check_manifest                     # then verify with `git cat-file -s`, not the worktree
```

---

### 7. What can still go wrong

1. **Line endings, per file.** `conclusions.tex` and `introduction.tex` are **LF**; `performance.tex` and `supplementary.tex` are **CRLF**. Every multi-line FROM above spans a newline — a matcher built with `\n` against a CRLF file **matches nothing and fails silently**. Verified counts in §0. Confirm with a byte read before each multi-line edit, never with a text-mode read.
2. **Never author LaTeX or regex through a bash heredoc.** Backslash collapse has already shipped `oindent` and `imes` into a released PDF. E1/E2/E6/E8c/E9 all contain `\dtgsk{}`, `\_`, `\times`, `---`. Use exact-match file editing (Write/Edit) only. One of the C11 challengers hit this trap again *this week* while writing a read-only sweep script.
3. **The double space at `supplementary.tex:1414`.** `hash-locked.` is followed by **two** spaces before `Neither ARGP`. The FROM string must stop at the period. Same convention throughout `supplementary.tex` sentence breaks (`:3700`, `:3762`).
4. **Em dash vs `---`.** E11b/c/d are U+2014 in Markdown; E1/E5b/E6 are ASCII `---` in LaTeX. Do not normalise.
5. **Cross-format parity.** `validate_cross_format_parity.py` compares canonical `.tex` body paragraphs against the **DOCX**, which is built from the `_pandoc` shim. Editing `sections/*.tex` or `supplementary.tex` **without rebuilding the DOCX produces a FAIL row** — and worse, its `split_containment` rule (a key appearing as exactly two contiguous runs) can record a *mid-paragraph* insertion like E9 as `PASS_FORMAT_DIFF` rather than FAIL, so a stale DOCX may pass while missing the disclosure. Verify the DOCX by reading `word/document.xml`, not by re-grepping the `.tex`.
6. **DOCX epoch.** `1783641600`, **not** the PDF's `1783468800`. A persisted `SOURCE_DATE_EPOCH` in the shell silently yields a non-reproducible DOCX that still passes `check_manifest`. Unset it between builds; build twice and diff.
7. **`check_manifest` hashes the working tree, not the committed blob.** A Word-resaved DOCX once passed 15/15. Verify with `git cat-file -s` after committing.
8. **BIND-window drift is silent.** `validate_evidence_bindings.py` only checks that each extracted token's digits appear in both renders — it never reports tokens that *left* a window. Three edits change paragraph line counts (E8c +3, E9 +8, O1 +1). E8c is capped at 3 specifically to keep `88` bound; E9's shift only evicts trivially-present dimension labels. Re-read the six lines above each touched `% BIND:` after applying.
9. **Wrong repo.** Work only in this repository checkout. The divergent PhD-Projects copy hashes only its own tree — both can report "15/15" while disagreeing.
10. **Branch.** Work on `main` — the only branch since 2026-08-28. The private history (reviewer reports, co-author handoff, seven copyrighted PDFs, commit messages unsuitable for publication) lives in the author's private history bundle outside the repository: **never fetch it into a repo with a public remote, never merge its refs into `main`, never copy the bundle into the repo tree.** Restore only into a detached private clone.
11. **Untracked-by-design files.** E12 edits `response_to_reviewers.md`, which is gitignored at `.gitignore:56` (D-0049, verified `rc=0`). It will not show in `git status` and will not be reviewed by any tracked-files sweep — but it ships to the reviewers. Do not re-add it to git.
12. **Residuals accepted, not fixed, in pass-42** — record them in the decision log so they are not re-discovered as new defects:
 - `supplementary.tex:1539` three-vs-four tier boundaries (S14-016).
 - The A12 convention collision (0.59 in Table A25 vs 0.511 in Table A43 for the same contrast) — needs its own id.
 - `conclusions.tex:104` still says "the parameter set \dtgsk{} resolves at $D = 10$", the same verb E8a replaces in the supplement — a mild main/supplement drift if E8 is applied and this is not.
 - `validate_cross_format_parity.py`'s `table_value_precision` note claims the DOCX renders full semantic precision (`2.879310`); `DT-GSK.docx` contains zero such occurrences. Unconditional `PASS_FORMAT_DIFF`, not a gate — stale convention, triage separately.

## 2c. Pass-42 work order addendum — E13–E17 (C1, C2, C3, DAS)

Produced by the second challenge run and **checked here before being recorded**. All four drafts had
real defects behind them; **three of four drafted fixes were unsafe** and were repaired — E13's
replacement was non-discriminating and would have falsified a bound claim elsewhere in the document;
E14/E15's replaced a false universal with a *false specific*; E17's named 1 site where 24 exist,
including `CITATION.cff:9`, which carries `version: "2.14"` with no leading `v` and so is invisible
to a `v2.14` sweep while being gated by `validate_citation_cff.py`. **Nothing below has been
applied.**

Companion to §2b (E1–E12). **Nothing below has been applied.** Every FROM anchor was re-verified in this session on **raw bytes**: byte-exact, exactly one occurrence, correct line ending, zero occurrences under LF normalisation where the file is CRLF. Every BIND claim was recomputed by re-implementing `validate_evidence_bindings.py:96–119` (`collect_bind_contexts` + `extract_tokens`) against in-memory copies — the validator itself was **not** run (it writes `evidence_binding_verification.csv`).

**Scope:** discharges **C1 (partially), C2, C3** and the DAS tag pointer. With §2b this closes all six adjudicated defects except the C1 body correction, which stays author-gated (§2 below).

**Governance:** pass-**42**, tag **v2.15**, **CR-0025 / D-0050**. All three verified free this session (`git tag` → v2.1…v2.14 only, no gaps; register ends CR-0024; decision log ends D-0049).

---

#### 0. Facts governing these five edits — including three corrections to the drafts' own mechanics

| Fact | Verified value |
|---|---|
| `papers/supplementary.tex` | **CRLF**, 3869/3869, 0 bare LF |
| `papers/main.tex` | **CRLF**, 454/454, 0 bare LF |
| `papers/DT-GSK-plain-summary.tex` | **LF**, 964 LF / 0 CR |
| `CITATION.cff` | **LF**, 170 LF / 0 CR |
| `papers/submission/SUBMISSION_KIT.md` | **CRLF**, 169/169 |
| `papers/governance/submission_package_manifest.json` | **CRLF**, 78/78 |
| `papers/review_2026_08_24/response_to_reviewers.md` | **LF**, 541 LF / 0 CR (gitignored `.gitignore:56`, D-0049) |
| **CORRECTION 1** | The Table A45 BIND is at **`supplementary.tex:3788`, not `:3789`** (3789 is blank). Its window is the **single line `\end{table}`** (STOP_LINE fires immediately), and `extract_tokens` on it returns **`[]`**. |
| **CORRECTION 2** | The draft's "keep the caption at 4 lines or it un-binds its numbers" is **false**. Stress-tested 4 → 1,2,3,4,5,6,7,8 lines: **0 of 192** BIND contexts changed at every value. The caption is in no window and annotates no token. |
| **CORRECTION 3** | The E16 site is in **no** BIND window at **any** delta. Nearest windows recomputed: BIND@2449 → 2443–2448; BIND@2458 → 2452–2457; BIND@2497 → 2491–2496. Stress-tested 2 → 10 lines: **0 of 192** contexts changed. |
| Merged apply order, `supplementary.tex`, highest line first | **E13 (3782) → E8 (3758) → E9 (insert after 3750) → E14 (3749) → E7 (3699) → E16 (2481) → E6 (2283) → E2 (1413) → E4 (562)** |
| ⚠ E14 × §2b-E9 interaction | Both touch the S9.2 closing paragraph. Apply **E14 first, then E9**. After E9's +8 insert the `% BIND: E2 headline` window becomes the last six lines of the E9 block, so E14's lines leave the window entirely — harmless (E14 introduces and removes no numeral either way), and §2b §7.8 already adjudicated that eviction. |

**Never author these strings through a bash heredoc** (CLAUDE.md rule 4). E13/E16 contain `\ge`, `\label`, `\ref`; E17c:114 contains a real **em dash U+2014**. Reproducing E16 through a heredoc during the audit produced `Section~ef{sec:supp:rev:np}` — the exact failure mode that shipped `oindent`/`imes`.

---

#### 1. Ordered edit list

#### E13a — C1 · Table A45 caption · `papers/supplementary.tex:3782–3785` **(CRLF)** · delta **0**

FROM (4 lines, CRLF; 1 exact occurrence at byte offset **229321**, 0 under LF):
```
$A_{12}$ takes it as reference.  At $D = 10$ the U-low arm and at $D = 100$ the
U-high arm coincide with the tiered configuration by construction, which the
tie counts confirm and which serves as the design's internal
control.}\label{tab:rev-e3}
```
TO (4 lines, CRLF — **challenger text, use verbatim**):
```
$A_{12}$ takes it as reference.  At $D = 10$ the U-low arm and at $D = 100$ the
U-high arm carry the tiered configuration by construction and serve as the
design's internal control.  Below the $D \ge 50$ gate the $D = 10$ arm ties
throughout; at $D = 100$ it does not, and that residual is not resolved here.}\label{tab:rev-e3}
```

**Discharges:** C1's anchor defect — the caption is refuted by the table printed beneath it on the same rendered page (`SA07.tex` row 8: `U-high & $100$ & 1.000 & 2/25/2 & 0.500 & not separated`; `e3_uniform_vs_tiered.json` `arms.U_high.dimensions.D100.wtl_ref_vs_cmp = {W:2,T:25,L:2}`). Four of 29 functions are not ties, so "which the tie counts confirm" is false for one of the two controls it covers. Self-refuting in print, in the document whose C3 is a determinism claim.

**Why the challenger's text beats the draft (one sentence):** it deletes the one false clause and asserts no cause, where the draft's "at $D = 100$ the reference cells predate the current build" is **non-discriminating** — both controls take their reference from the same file `benchmarks/cec_reference_results/cec2017/dt-gsk/per_run.csv` (one run, one `environment.json`, 1479 cells at each of D=10/30/50/100, verified this session), so the drafted contrast explains the clean D=10 result away as readily as the dirty D=100 one — **and** it falsifies a printed, BIND-annotated claim 2500 lines earlier (see E13c).

**BIND:** cannot evict. BIND@3788's window is the single line `\end{table}`; `extract_tokens` → `[]`. Caption growth to 8 lines changes 0 of 192 contexts (verified). Delta 0 regardless.
**Cosmetic option:** TO line 4 is 96 chars against a 60–81 caption convention. Re-wrapping the **identical words** over 5 lines is equally safe.

#### E13b — C1 companion, reviewer-facing · `papers/review_2026_08_24/response_to_reviewers.md:216–217` and `:230` **(LF)** — ⚠ **SITE VERIFIED, TEXT NOT AUDITED**

Missed by the draft. Same defect, sharper, in the document the reviewers actually read:
- `:216–217` — `Each arm coincides with the tiered configuration by construction at its own home dimension, which gives` ⏎ `the experiment a built-in null control.`
- `:230` — `| U-high | 100 | 1.000 | 2/25/2 | not separated (construction control) |`

Both anchors verified unique. Precedent for editing this file: §2b **E12**. Constraint set for the drafter: (i) the D=100 row must stop being presented as a *null* control while printing 2/25/2 in the same row; (ii) assert no cause — the vintage explanation is not available until E13c is decided; (iii) the file carries **no** BIND, so line delta is free.
**Candidate (mechanical mirror of the approved E13a wording — challenge before applying):** replace `:216–217` with `Each arm carries the tiered configuration by construction at its own home dimension, which gives` ⏎ `the experiment an internal control. Below the D >= 50 gate the D = 10 arm ties throughout; at` ⏎ `D = 100 it does not, and that residual is not resolved here.`, and re-label the `:230` Reading cell to match.

#### E13c — C1 body correction · `papers/supplementary.tex:1254–1267` **(CRLF)** — 🚫 **DO NOT APPLY. AUTHOR DECISION.** See §2.

#### E14 — C2 · supplement · `papers/supplementary.tex:3749–3750` **(CRLF)** · delta **0**

FROM (2 lines, CRLF; 1 occurrence, byte offset 227245):
```
sense that they rest in part on a component of the method, and this is stated
wherever those claims appear.
```
TO (2 lines, CRLF — **challenger text**):
```
sense that they rest in part on a component of the method, and the main text
records this where the asymmetry is introduced and again in its discussion.
```

**Discharges:** C2. The universal is false: the qualification is carried at exactly **two** main-text sites, both identifiable by their `Section~S9.2` citation — `proposed_algorithm.tex:169–170` (§3.2) and `performance.tex:1132–1133` (§4.9). Exhaustive in source (2 hits) and in the rendered PDF (2 hits). The D=50/D=100 rank claims are given in §4.2.2 / Table 14 / Figure 3 (p.30) and restated in §5 (p.41), and **none** of those carries it — Table 14's caption names two qualifications and not this one.

**Why the challenger's text beats the draft:** the draft's "where the ranks are given" is *also false*, and falsifiable in one page-turn to Table 14 — a referee following it lands on the rank table and finds nothing; "again in its discussion" points at §4.9, the main text's one section titled Discussion, which does carry it.

**BIND:** the edit sits **inside** BIND@3751's window (3745–3750). Verified by recomputation: window stays 6 lines, and the annotated token set is **identical before and after** — `[('int','10'),('int','30'),('int','50'),('int','100')]`. Nothing evicted, nothing un-bound. Delta 0 by design; do not use a 3-line variant.

#### E15 — C2 · plain summary · `papers/DT-GSK-plain-summary.tex:273` **(LF)** · delta **0**

FROM (1 line, LF; 1 occurrence):
```
claims as resting in part on this rule, wherever those claims appear.
```
TO (1 line, LF — **challenger text**):
```
claims as resting in part on this rule.
```

**Discharges:** C2 in the plain register. Full sentence becomes "The paper therefore qualifies its 50- and 100-unknown rank claims as resting in part on this rule." — true (it does, twice), asserts no universal.
**Why it beats the draft:** the draft transplanted the same false locative into a document whose lay reader is not holding the paper, so a structural pointer earns nothing there even when true; deleting the clause is both true and shorter. Delta **0** rather than the draft's +1.
**BIND:** `grep -c "% BIND"` on this file = **0**. No window exists at any delta.

#### E15b — C2 · reviewer-facing · `papers/review_2026_08_24/response_to_reviewers.md:141–142` **(LF, gitignored `.gitignore:56`, D-0049)** · delta **0**

**Missed by the draft.** Highest-stakes instance: a **bolded** representation to the referee who raised R1.3/R2.2. Wraps the line break, so single-line grep misses it.

FROM (2 lines, LF; 1 occurrence):
```
We report that plainly rather than minimising it: **the D = 50 and D = 100 rank claims are now
qualified as resting in part on the population rule**, wherever those claims appear.
```
TO (2 lines, LF — **challenger text**):
```
We report that plainly rather than minimising it: **the D = 50 and D = 100 rank claims are now
qualified as resting in part on the population rule**, where the asymmetry is introduced and in the discussion.
```
**BIND:** file carries none. TO line 2 is 110 chars against a p90 of 103 (file max 197) — acceptable; a 3-line rewrap of the identical words is equally safe.

#### E16 — C3 · `papers/supplementary.tex:2481–2482` **(CRLF)** · delta **+2** (2 → 4)

FROM (2 lines, CRLF; 1 occurrence, byte offset 147773):
```
larger initial population buys proportionally fewer generations; as on the
other suites, the population rule was not a controlled variable.
```
TO (4 lines, CRLF — **challenger re-wrap; not one word differs from the draft**):
```
larger initial population buys proportionally fewer generations; the
population rule is not a controlled variable on this suite, and the
matched-population control of Section~\ref{sec:supp:rev:np} covers
CEC2017 only.
```

**Discharges:** C3. **This is the only one of the four whose draft wording was judged safe.** The decisive evidence for the defect is the paper's own already-corrected parallel sentence at `performance.tex:1131–1133`: "The asymmetry was not a controlled variable **at submission**; it was **controlled in revision** (Supplementary Materials, Section S9.2)". The revision qualified exactly this proposition in the main text and missed the LSGO instance in the supplement — a missed site in the revision's own sweep, not a register choice. The bare universal now self-contradicts S9.2 inside one document.
**Truth of clause 2, checked against the bound release not the prose:** `e2_np100.json` `strict_sources` = `_revision/`, `cec2017/`, `_ablation/overlay/` only, D10/D30/D50/D100, n_funcs 29, 5916 shared cells, 0 seed mismatches; `_revision/manifest.json` — of 252 released files, 224 carry a `cec2017` token and **zero** carry `cec2011`, `cec2013`, `cec2013lsgo` or `cec2020`; the config is literally `_configs/e2_np100_cec2017.yml`.
**Why the re-wrap beats the draft (one sentence):** identical words, but wrapped to 68/67/66/13 columns to match this paragraph's own 54–74 hand-wrap, where the draft's first line was 79.
**BIND:** in no window at any delta (Correction 3). Delta is irrelevant here, which is why +2 costs nothing. The edit does not cross a paragraph boundary — 2481–2496 is one LaTeX paragraph ending at the `:2497` BIND.

#### E17a — DAS · `papers/main.tex:279` **(CRLF)** · delta **0**

FROM (**single line** — narrower than the draft's 2-line anchor, and still unique: `tag v2.14,` occurs exactly once in the file; this removes all exposure to the CRLF multi-line failure mode):
```
tag v2.14, and any further materials are
```
TO:
```
tag v2.15, and any further materials are
```

**Discharges:** the DAS pointer. "This revised version" denotes the document in the reader's hand; after pass-42 that document lives at v2.15, so the pointer becomes **false**, not merely stale. The invariant is empirical, not discretionary: `git show v2.13:papers/main.tex` names v2.13, `git show v2.14:papers/main.tex` names v2.14 — every published tag of this manuscript names the tag it ships inside. D-0044 constrains **which identifiers** the DAS may carry (one URL, no DOI, no Zenodo); it does not freeze the tag number, and E17 adds no identifier. The defect renders: `DT-GSK.pdf` extracted line 2539.
**Tag-agnostic rewording rejected:** `archive/v2.14-original` (26ea4b28) vs `v2.14` (02d17910) looks like a re-pointed tag but is not — the archive tree still contains the seven copyrighted PDFs; decision_log.md:2124 records it as publication hygiene, not tag reuse. v2.15 is the plan of record (REVISION_STATUS.md:256, :1051). Residual risk is procedural and is discharged by cutting and pushing v2.15 **in the same mint**.
**BIND:** lines 278–279 are covered by **no** BIND. Recomputed windows in the region: BIND@296 (inline) → 294–296; BIND@307 → 305–307; BIND@320 → 318–320. ⚠ Because the DAS sits outside every window, `validate_evidence_bindings.py` will **not** catch a botched application here; the gates that react are `check_manifest` and `validate_cross_format_parity.py`.

#### E17b — 🔴 **COUPLED, GATED, INVISIBLE TO A `v2.14` SWEEP** · `CITATION.cff:9` **(LF)** · delta 0

FROM: `version: "2.14"` → TO: `version: "2.15"`

No leading `v`, so the draft's own "no validator matches v2.1x" sweep misses it. `papers/scripts/validate_citation_cff.py` check (1) requires the `CITATION.cff` committed **inside** tag `vN.M` to declare exactly `N.M`. Cutting v2.15 with `2.14` inside is precisely the S8-01 defect that gate exists for (recurred at v2.3, v2.4, v2.5). D-0044 set the precedent: "CITATION.cff bumped to 2.13 in the tagged state."
✅ Check (3) verified clean after the bump: `COMMENT_VERSION_RE` finds **zero** version-naming comments in the file.
✅ Check (2) permits the transient tree-ahead-of-tag state; it fails only when the tree is *behind*.
Also move `date-released: 2026-08-26` (`:10`) to the pass-42 mint date — ungated, but stale otherwise.

#### E17c — 🔴 **COUPLED, UNGATED, EDITOR-FACING** · `papers/submission/SUBMISSION_KIT.md` **(CRLF)**

Hand-maintained: `grep` for `SUBMISSION_KIT` across all `.py` returns nothing. `papers/scripts/build_submission_bundle.py` writes `dtgsk_reproduction_pack_manifest.json`, a different file. **Must be hand-edited.** `:113–114` is the literal text the author pastes into the SuSy code/data-availability field — apply E17a alone and the author types v2.14 into the journal form while the PDF says v2.15, and the kit's claim of exact match becomes false. All six anchors verified unique.

| Line | FROM | TO |
|---|---|---|
| `:3` | `Regenerated 2026-08-26 from the pass-40 / v2.14 REVISION-1 sources (the` | `Regenerated <pass-42 mint date> from the pass-42 / v2.15 REVISION-1 sources (the` |
| `:114` | `this revised version to tag v2.14 — matching the manuscript's own Data` | `this revised version to tag v2.15 — matching the manuscript's own Data` (**em dash U+2014**, match bytes) |
| `:159` | `   hash-recorded in \`submission_package_manifest.json\` at **v2.14**, and that` | `…at **v2.15**, and that` |
| `:160–161` | `   record is what makes the submitted bytes checkable. Freeze pass-41 and tag`⏎`   v2.14 are the frozen state of this resubmission, exactly as pass-38 / v2.13` | `…Freeze pass-42 and tag`⏎`   v2.15 are the frozen state…` |
| `:163`, `:165` | `3. If a SECOND revision is requested, it becomes pass-42 through change` … `   v2.14 in place (D-0045).` | `…it becomes pass-43 through change` … `   v2.15 in place (D-0045).` |
| `:169` | `   \`git diff v2.13 v2.14\` over the manuscript sources.` | `   \`git diff v2.13 v2.15\` over the manuscript sources.` |

⚠ `:163` is a real label collision, not bookkeeping: the kit reserves "pass-42" for a *second journal revision*, which this pass consumes.
⚠ Pre-existing drift, fix while here: `:3` says "pass-40" where `:160` says "pass-41" for the same state.

#### E17d — 🔴 **COUPLED, UNGATED** · `papers/governance/submission_package_manifest.json` **(CRLF)**

No generator (confirmed). Not among the 15 manifest-hashed files.

| Line | Action |
|---|---|
| `:3` | `"generated_utc"` → mint timestamp |
| `:4` | `"manuscript_version_id": "v2.14"` → `"v2.15"` |
| `:5` | **Rewrite the note at mint.** Two load-bearing falsehoods, both verified unique: `"Freeze pass-41, tag v2.14 (D-0049).` (→ pass-42 / v2.15; cite **D-0050** if that is the decision authorising this pass's tag, verified free at apply time) and `which now names v2.13 for the submitted version and v2.14 for this revised one` — **falsified outright by E17a the instant it lands**. Also reconcile "Supersedes v2.13 as the submission basis". |
| `:75` | `differs between v2.13 and v2.14` → `differs between v2.13 and v2.15` |

---

#### 2. DO NOT APPLY

**No edit in E13–E17 was judged unsafe *and* left unrepaired.** All four challenged drafts were repaired (E13/E14/E15 by replacement text, E17 by an expanded site list; E16 needed only a re-wrap). Two follow-ons are nevertheless blocked:

🚫 **E13c — `papers/supplementary.tex:1254–1267` (CRLF) — AUTHOR DECISION, NO AUDITED TEXT.**
The paragraph states in print, bound by the `% BIND:` at `:1268`, that `_dt_core.py` changed after `rel-2026-07-20-67d9345f9` by CR-0013…CR-0018, that "the release was produced by dc2d59db91a288ee", that "Every one of those edits was certified *bit-identical*", that the cross-suite ledger was re-verified "with zero divergence", and that "No reported number, rank, $p$-value or decision in this paper or this Supplementary Material depends on which of the two revisions is used." **Table A45's D=100 row (2/25/2) is a counterexample to that last sentence.** It also silently reopens three APPROVED change requests: CR-0014, CR-0015 and CR-0016 all carry `rerun_plan "NONE - bit-identical"` and `affected_claims "NONE"`; CR-0016 states "Output bit-identical; rel-2026-07-20-67d9345f9 remains valid" — the release supplying every DT-GSK number in the paper. The certification gap is documented: **cec2017 D=100 is absent from exactly one link's hex-identity list (CR-0015)**, and that link is dead-work removal inside the per-generation loop.
Correcting this belongs in the **body**, with scope, with the three CRs named, with an evidence binding, and behind an author decision. It cannot be smuggled into a caption. E13a is deliberately decision-independent, so it ships now regardless of how this lands.

🚫 **E13b text** — site required, prose unaudited. Draft and challenge before applying (§1).

⚠ **E17a alone** — do not apply without E17b/c/d. Shipping the manuscript at v2.15 with `CITATION.cff` at 2.14 is the exact defect `validate_citation_cff.py` was written to catch.

---

#### 3. REJECTED — do not re-litigate

| Source | Rejected text / claim | Reason |
|---|---|---|
| E13 draft | `…resolve to the tiered configuration by construction and serve as the design's internal control; the $D = 10$ tie count reflects that, while at $D = 100$ the reference cells predate the current build.` | Four independent disqualifiers. (1) **Non-discriminating**: both controls take their reference from the same `cec2017/dt-gsk/per_run.csv` (one run, `environment.json` 2026-07-18T18:23:52, git_commit 251fc8cb), so the clause is equally true of the clean D=10 arm and explains nothing; the real discriminator is the **D ≥ 50 gate** (`interaction_graph_enabled`/`final_polish_enabled` False at D=10/30, True at D=50/100), already in print at `supplementary.tex:1331` and `proposed_algorithm.tex:150/223/244`. (2) **Falsifies `supplementary.tex:1254–1267`** and reopens CR-0014/15/16, with no discussion and no binding — a caption cannot carry that. (3) **Term collision**: "resolve" is the paper's technical verb for DT-GSK resolving a configuration by dimension, used twice in the very next paragraph (`:3794`, `:3797`); and "the current build" appears nowhere in the rendered supplement. "coincide" was never the defective word — the false clause was "which the tie counts confirm". (4) Its stated 4-line constraint is **false** (Correction 2). |
| E13 draft rationale | "the standalone BIND at `:3789` covers the 6 preceding non-blank lines … growing it evicts the opening line" | BIND is at `:3788`; window is one line (`\end{table}`); zero tokens; growth to 8 lines changes 0 of 192 contexts. |
| E14 / E15 drafts | `…records this where the asymmetry is introduced and where the ranks are given.` / `both where the asymmetry is introduced and where the ranks are given.` | Replaces a false universal with a **false specific**, which is worse — falsifiable in one page-turn. Ranks are given at §4.2.2 / Table 14 / Figure 3 (p.30) and §5 (p.41); the qualification is at §3.2 (p.16) and §4.9 (p.40), ten PDF pages away. Table 14's caption names two qualifications and not this one. |
| E14 draft rationale | "the supplement never hardcodes main-text section numbers (see `supplementary.tex:545`, `:1119`, `:2380`)" | Those three are **table** references ("the main-text rank table" etc.) and support only §2b-E9's already-recorded table-number fact. Generalised to sections it is false: `supplementary.tex:261` reads "the statistical exhibits of the main paper (Section~4)". The design choice (stay descriptive) stands; the stated reason does not. |
| E17 draft rationale | "No gate greps the tag string" | True but misleading. Confirmed: **zero** literal `v2.1x` strings in any `.py/.yml/.toml/Makefile` in the tree. But `validate_citation_cff.py` gates the tag via `git tag` + the cff `version` field; `check_manifest` hashes the **working tree**, so `main.tex`, `DT-GSK.pdf`, `DT-GSK.docx` go red until rebuilt; and `validate_cross_format_parity.py` does alnum-containment on body paragraphs, so an un-rebuilt `DT-GSK.docx` is **expected to FAIL** parity. The edit mandates a full rebuild. |
| E17 draft scope | one site (`main.tex`) | Three coupled sites omitted, two of them ungated and one invisible to a `v2.14` sweep. |
| §6 Phase 1 (REVISION_STATUS.md:1010–1014) | "state that the controls compare against a reference produced by an earlier build, and that the D ≥ 50 learned-basis path is sensitive to that" | **Superseded by the E13 challenge.** The vintage explanation is the only surviving one — but it is a correction to `:1254–1267`, not a caption clause. Update §6 Phase 1 when this addendum is recorded. |
| C1 fallout | narrowing **contribution C3** | **Not falsified and must not be narrowed.** C3 is byte-stable determinism *in the declared environment*, which pins the build (four hash-gated modules, config-lock validator, byte-stability regression). Two runs of the same build under those pins are byte-stable; the 27 cells are a **cross-build** comparison C3 never claimed to cover. |
| Diagnosis chain, for the record | "`generation_logs_enabled` / `convergence_graphs_enabled` gate the coverage kernel via `_need_coverage` at `_dt_core.py:2644`" | **Factually wrong; do not repeat.** `_need_coverage` = `_cfg_ace_coverage_weighted or (generation_callback is not None)`, and `generation_callback` is set only by the opt-in `dt_diagnostics` path (`dt_gsk.py:107–128`, `:278–287`), which the campaign did not use. Those two YAML flags are consumed only at `run_experiment.py:1736–1737` → `runners/output.py:314–358`, i.e. post-run persistence. The conclusion (telemetry ruled out) holds — by a **stronger** route: the flags never reach the optimizer. |
| Diagnosis chain, for the record | `np.linalg.eigh` (`_dt_core.py:1904–1916`) as the *cause* of the residual | It is deterministic given identical input on identical LAPACK: it can **amplify** a divergence, never originate one. Sensitivity argument only. |

---

#### 4. BIND / vocabulary audit (requirement 4)

| Edit | Introduces | Shipped? | BIND status |
|---|---|---|---|
| **E13a** | `$D \ge 50$`; `gate`; `residual` | Gate in print: `supplementary.tex:1331` (`$D \geq 50$`), `proposed_algorithm.tex:150/223/244` (`$D{\ge}100$`, `$D\ge50$`). `\ge` is the dominant macro in `supplementary.tex` (23 vs 3 `\geq`). `gate`/`gated` = 21/5 occurrences. `residual` = 3, incl. `:3707` in the same section. | **In no window; annotates no token.** |
| **E13a** | numeral `50` (only numeral not already in the FROM) | Prints in the U-low/U-high D=50 rows of the same table, in **both** renders (PDF p.76, DOCX) | Not gate-enforced (no window). ✅ |
| **E14** | `the main text`; `again in its discussion` | Supplement's own descriptive idiom (`:545`, `:1119`, `:2380`); §4.9 is the main text's one section titled Discussion | **Inside BIND@3751's window.** Token set verified **identical** before/after: `10, 30, 50, 100`. **No numeral added or removed.** |
| **E15 / E15b** | — none — | — | No BIND in either file. |
| **E16** | `matched-population control`; `Section~\ref{sec:supp:rev:np}` | `main.tex:234` "matched-population-size control"; `README.md:80` "A matched-population control"; `PROJECT_RULES.md:207`. Label defined **once**, `supplementary.tex:3713`, currently zero references; renders **S9.2**, matching the main text's hardcoded "Section S9.2" and `cross_format_consistency.csv:419`. Forward `Section~\ref` is the supplement's dominant idiom (51 forward / 16 back), and `:1411–1413` is a near-exact stylistic clone ("The sweep of Section~\ref{…} covers seven constants … at $D = 30$ and $D = 100$ only"). | **`extract_tokens` on the replacement returns `[]` — zero numeric tokens.** `CEC2017` yields nothing under the `int` pattern (digits preceded by `C`); `\ref{…}` args are stripped by `_STRIP_ARGS`. This matters: S7.1 (`:2429–2431`) declares every number in the section derives from `lsgo-rel-2026-07-28-ff1a046ef`. The replacement **points instead of quoting**, so that declaration survives. |
| **E17** | `v2.15` | Recorded plan at REVISION_STATUS.md:256, :1051; sentence pattern unchanged from v2.13/v2.14 | Lines 278–279 in **no** window. ✅ |

**Nothing in E13–E17 adds an unbindable number.** E13a is the only replacement introducing a numeral absent from its FROM (`50`), and it is both already rendered on the same page and outside every window.

---

#### 5. Sites the drafts missed

**MUST MOVE with E17 (tag hardcodes):**

| Site | Why the drafts missed it |
|---|---|
| `CITATION.cff:9` | `version: "2.14"` — **no leading `v`**, invisible to a `v2\.14` sweep; the only one an actual gate enforces |
| `papers/submission/SUBMISSION_KIT.md:3, 114, 159, 160–161, 163, 165, 169` | Hand-maintained, ungated, and `:113–114` is the literal SuSy paste text |
| `papers/governance/submission_package_manifest.json:3, 4, 5, 75` | Ungated; `:5` is falsified outright by E17a |

**MUST NOT MOVE — historical records; append CR-0025 / D-0050 instead:**

- `papers/governance/change_request_register.csv` **CR-0023, CR-0024** — record what those CRs did at the time.
- `papers/governance/decision_log.md:1759, :1872, :2040, :2124` — same.
- `papers/submission/AUTHOR_DATA_HANDOFF.md:129` — **untracked** (D-0049), generated 2026-08-07 from v2.13; its "must run as a new freeze pass (v2.14)" was true then.
- `papers/review_2026_08_24/reviewer_reports_verbatim.md` — untracked verbatim reviewer text.
- `README.md:65` — "DT-GSK **v2.1** optimizer" is an **optimizer** version, not a repo tag. A loose `v2\.1` sweep false-positives here. README carries no repository-tag string at all.
- `docs/index.md:11`, `docs/html/index.html:167` — name only pass-38 / v2.13; unaffected.
- `REVISION_STATUS.md:111` and the C-defect quotations — must keep quoting the defective strings to track them.
- `papers/review_2026_08_24/revision_experiments_preregistration.md` — "The headline rank claims will be qualified accordingly" is a future-tense pre-registration commitment; public and append-only **by design** (D-0049).

**VERIFIED CLEAN — no repository-tag string:** `supplementary.tex`, `supplementary.pdf`, `supplementary.docx`, `cover_letter.*`, `DT-GSK-plain-summary.*`, `papers/governance/claims_evidence_matrix.csv`, `artifact_binding.csv`.

**Other missed carriers (already folded in above):** `response_to_reviewers.md:141–142` (E15b), `:216–217` and `:230` (E13b), `supplementary.tex:1254–1267` (E13c).

---

#### 6. Generated — regenerate, never hand-edit (requirement 6)

**`papers/main_pandoc.tex` and `papers/supplementary_pandoc.tex` are GENERATED SHIMS.** `papers/scripts/build_docx.py:2910` does `spec["shim"].write_text(build_shim(doc_kind))`; docstring line 46: "the shim files are overwritten on every run." A hand-edit is clobbered on the next build **and reads as done**. Confirmed carriers of these five defects, none of which is an edit site:

| Shim line | Carries |
|---|---|
| `supplementary_pandoc.tex:3736–3739` | E13's caption verbatim |
| `supplementary_pandoc.tex:3704` | E14's sentence verbatim |
| `supplementary_pandoc.tex:2461–2462` | E16's sentence verbatim |
| `main_pandoc.tex:3580` | E17's DAS sentence verbatim |

Also generated, **not** edit sites:
- `papers/tables/word_sources/SA07.json:84` — provenance note; its `notes` array does **not** reach `supplementary.docx`, and it **omits** "which the tie counts confirm", so its claim stays true after E13a. Leave it. Its generator is `papers/scripts/generate_revision_exhibits.py:201–202` — touch only if the note text is to change (it need not).
- `papers/submission/DT-GSK-latex-source.zip!main.tex:279` — rebuilt by `build_submission_zips.py`, which walks `\input` transitively from `main.tex`.
- `papers/DT-GSK.pdf:2539` (extracted), `papers/DT-GSK.docx!word/document.xml`, `papers/supplementary.pdf` p.76 / S9.2 / S7.2, `papers/supplementary.docx!word/document.xml:489`, `papers/DT-GSK-plain-summary.pdf` p.9 — rendered carriers, fixed by rebuild only.

---

#### 7. Rebuild / re-mint delta on top of §2b §6

| Newly edited | Downstream |
|---|---|
| `papers/main.tex` (E17a) | `DT-GSK.pdf` (epoch **1783468800**) → `build_docx.py` (epoch **1783641600**, regenerates `main_pandoc.tex`) → `DT-GSK.docx` → **re-run `build_submission_zips.py`** (the zip bundles `main.tex` **and** `DT-GSK.pdf`) |
| `papers/supplementary.tex` (E13a, E14, E16) | already in §2b's list — `supplementary.pdf` + `build_docx.py --supplementary` + `supplementary.docx` |
| `papers/DT-GSK-plain-summary.tex` (E15) | `DT-GSK-plain-summary.pdf` (not manifest-hashed) |
| `CITATION.cff`, `SUBMISSION_KIT.md`, `submission_package_manifest.json` | none — not manifest-hashed, no generator |
| `response_to_reviewers.md` (E15b, E13b) | none — untracked, ships to reviewers as-is |

**Freeze manifest:** §2b's 8 changed entries become **9 of 15** — add `main.tex`. Manifest is **CRLF + 2-space**; re-mint surgically per its own `remint_note`. Set `published_commit` alongside `anchor_commit`.
**Extra validator to run for this addendum:** `papers/scripts/validate_citation_cff.py` (gates E17b).
**Tag:** cut and push **v2.15 in the same mint** as the DAS edit, so the pointer is self-consistent as D-0044 requires; confirm v2.13, v2.14 and v2.15 all resolve.

---

#### 8. Adjacent defects surfaced, not prescribed

1. **`CITATION.cff:87`** — "revised version resubmitted 2026-08-26" is **already false**; the revision has not gone through SuSy. Same file as E17b, so it is free to fix — but the replacement wording is an author call.
2. **A cheap decisive test, worth running before any vintage claim is printed anywhere.** Re-run the tiered pub profile under the **current** build at D=100 on the five affected functions (**F7, F13, F14, F20, F30**) with the recorded seeds and compare against the revision U-high D=100 cells. **Match** ⇒ the current build is self-consistent, the residual is purely cross-vintage, and `:1254–1267` is what needs correcting. **Mismatch** ⇒ a live determinism problem at D ≥ 50 and contribution C3 is genuinely at risk. ~27–255 runs; minutes to an hour, against a permanent claim in a frozen manuscript. This is the cheapest way to close E13c.
3. **`supplementary.tex:2477`** (two lines above E16) — "against the comparators' reference-implementation value of $100$", vs `papers/governance/comparability_audit.md:28` (CR-0023, 2026-08-25): "the resulting NP = 100 is a panel normalization traceable to eGSK's published CEC2017 panel, **NOT** each comparator's own published rule (AGSK specifies 20D, APGSK 200D, FDB-AGSK 40n)". S9.2 at `:3715–3717` repeats it. The main text's "the family's reference-implementation setting" (`performance.tex:1130`) is more defensible. Unadjudicated; same paragraph as E16, so pass-42 is the cheapest moment.
4. **Extend the byte-stability KAT to D ≥ 50.** `tests/regression/test_dt_gsk_byte_stable.py:10–11` states its cells are D ≤ 30 "below the D ≥ 50 SGSM/parallel-kernel tier", so C3's machine-checked support does not currently reach the tier where the residual lives.
5. **Number-reporting caution for whoever writes the E13c correction:** the residual is **27 of 1479 cells, max 5.282 % relative**, measured on the **`error`** column (`statistics_basis = error_vs_optimum`). Re-deriving from `best_fitness` gives **26 and 2.514 %**. If either figure is printed, **name the column**. Distribution on `error`: F7 ×9, F13 ×8, F14 ×1, F20 ×7, F30 ×2 (F13/F14/F20 are CEC2017 hybrids). D=10 is exactly clean: **0 of 1479**, 0 seed mismatches. Every other recorded difference between the two D=100 legs is eliminated — configuration 108/108 keys, seeds 0/1479, nfes and termination 0/1479, threading (`numba_threads_active` 1 both), platform, Python 3.10.11, numba 0.64.0, backend, fp regime, X0 policy, 15 workers.

## 3. What has already been applied

All six zero-run reviewer points are closed. The commits were on `revision/pass-39`, whose history
now lives in the private bundle (see §1); the applied state itself is what `main` publishes.

### Phase 1 (R1.4 — statistics convention) — applied 2026-08-25

13 files, 259 insertions / 42 deletions.

All seven component-study omnibus p-values now report the **Iman–Davenport F on the tie-corrected
Friedman statistic** — the same convention the main text uses for the primary suites (M-026 / D-0016).
Every p-value *decreased*; **no ranking and no Holm decision anywhere changed**.

| Panel | New | Was |
|---|---|---|
| S6.5 CEC2017 D50 | F(3,84) = 5.59, p = 1.5e-3 | 2.4e-3 |
| S6.5 CEC2017 D100 | F(3,84) = 4.87, p = 3.6e-3 | 5.2e-3 |
| S6.5 CEC2013 D50 | F(3,81) = 5.96, p = 1.0e-3 | 3.8e-3 |
| SA01 + SA02 D10 | F(6,168) = 9.23, p = 9.8e-9 | 1.8e-6 |
| SA01 + SA02 D30 | F = 11.35, p = 1.2e-10 | 2.5e-8 |
| SA01 + SA02 D50 | F = 3.36, p = 3.8e-3 | 5.8e-3 |
| SA01 + SA02 D100 | F = 2.45, p = 2.7e-2 | 3.5e-2 |

Files changed: three scripts (`regen_cec2017_contrasts.py`, `promote_cec2017_overlay.py`,
`generate_ablation_exhibits.py`), three overlay contrasts JSONs (**additive only** — every pre-existing
key byte-identical), the `_ablation` manifest (8-line checksum refresh), `phase_12/ablation_exhibits_manifest.json`,
`supplementary.tex` (3 prose edits), `SA01.tex`, `SA02.tex`, `word_sources/SA01.json`, `supplementary.pdf`.

**Gate state after Phase 1:**

- `check_frozen_analysis.py` → **115/115 byte-identical** (primary release `rel-2026-07-20-67d9345f9` untouched)
- `regen_cec2017_contrasts.py` self-check → **all 1297 ablation checksums match disk**
- `check_manifest.py` → **14/15**; only `supplementary.pdf` outstanding, expected until the pass-39 re-mint
- `validate_evidence_bindings`, `validate_artifact_labels`, `validate_build_hygiene` → exit 0
- `audit_manuscript.py` → exit 0; `blocked_wording_hits: 2` **pre-existing** (identical at pristine HEAD)

**Two things discovered while doing it, both now fixed or recorded:**

1. **Latent manifest-writer bug.** `regen_cec2017_contrasts.py` and `promote_cec2017_overlay.py` wrote
   `benchmarks/cec_reference_results/_ablation/manifest.json` as `indent=1` with no trailing newline,
   while the file on disk is `indent=2` **with** one. Running either reformatted all ~30 KB, burying the
   real change. Both writers were corrected; the manifest diff is now 8 clean lines. Exact reproduction:
   `json.dumps(man, indent=2, ensure_ascii=False) + "\n"`, UTF-8, LF.
2. **`check_manifest.py --manifest` does not work on the ablation manifest.** It takes its base directory
   from the manifest's `evidence_root` key, which that manifest lacks, so every path resolves against the
   repo root and it prints `0/1297 match`. This is a usage artifact, **not corruption**. The real gate is
   the self-check the regen script prints at the end of its run.

**Deliberately reverted, do not redo yet:** `citation_usage_map.csv`, `phase_08/paragraph_evidence_audit.csv`,
`phase_09/evidence_binding_verification.csv`. The gates rewrite these, but they are line-number-keyed and
the Phase 3 title edits will shift those line numbers again. They belong in the Phase 5 build tail.

### Phase 2 (R2.5 + R2.4 body edits) — applied 2026-08-25

Three body edits; **abstract edits deliberately deferred to Phase 3**, where R1.1 + R2.4 + R2.5 merge
into a single word-counted edit.

| Site | Change |
|---|---|
| `performance.tex:12` | Results opener now qualifies the headline rank: "a descriptive summary, not evidence of overall superiority", naming the D=10-only separation and the Nemenyi non-separation |
| `performance.tex:1080` | ISM wall-clock overhead surfaced in the main text: **+57.3 % / +36.3 % / +30.3 %**, "against no detectable standalone accuracy return" |
| `conclusions.tex:47` | Caveat upgraded from W/T/L counts to the explicit Holm p-values **0.0035 / 0.199 / 1.0 / 0.795** |

**Finding: the manuscript was already more conservative than Reviewer 2 realised.** Both
`conclusions.tex` and `performance.tex:1196` already stated the Nemenyi non-separation, and the honest
per-cell numbers were already at `performance.tex:525-532`. The gap was *placement* — the openers led
with the aggregate rank unqualified. The third planned edit (`performance.tex:1193-1199`) was
**skipped as redundant**; it already carries the point.

Gates: main PDF rebuilt (47 pages, unchanged from HEAD), `validate_evidence_bindings` exit 0,
`validate_build_hygiene` OK, `audit_manuscript` exit 0 with `blocked_wording_hits` still 2 and
`unbound_number_candidates` still 8 (both pre-existing). `check_frozen_analysis` **115/115**.
`check_manifest` is now **11/15** — `performance.tex`, `conclusions.tex`, `DT-GSK.pdf`,
`supplementary.pdf` — all expected until the pass-39 re-mint.

Sentence spacing is **per file**: `performance.tex` and `conclusions.tex` are single-space after a
period; `supplementary.tex` is double-space (202 vs 73). Match the file you are editing.

### Phase 3 (R1.2 title + R1.1/R2.4/R2.5 merged abstract) — applied 2026-08-25

**New title, live everywhere:** *DT-GSK: Dimension-Tiered **Adaptive Configuration Selection** and
Deterministic Refinement for Gaining-Sharing Knowledge Optimization*. Verified: the built PDF contains
**zero** occurrences of "Adaptive Control", and the fatal cover-letter drift gate passes.

Propagated across **20 files**: `main.tex` (header + `\Title`), `supplementary.tex`, both cover letters,
`DT-GSK-plain-summary.tex`, `build_docx.py` (docProps title/subject/keywords ×2 blocks),
`build_submission_bundle.py`, `CITATION.cff`, `README.md`, `SUBMISSION_KIT.md`,
`AUTHOR_DATA_HANDOFF.md` (author-local; withheld from the public repository), the live
`PROJECT_TITLE` field, and 30 rows of `citation_usage_map.csv`.

**ACE re-glossed** "Adaptive Control Engine" → "Adaptive **Configuration** Engine" — acronym unchanged,
so every "ACE" in the text stays valid; 7 expansion sites moved. `related_work.tex:29` renamed to
"…From Fixed Parameters to Adaptive Configuration".

**Keywords:** "dimension-tiered adaptive control" → "…adaptive configuration selection", and
"interaction-structure memory" dropped (R2.4). Mirrored in all five places: `main.tex`,
`supplementary.tex`, `SUBMISSION_KIT.md`, `CITATION.cff`, and both `build_docx.py` blocks.

**Merged abstract** — R1.1 + R2.4 + R2.5 in one edit, as planned:

| | raw tokens | math-as-one |
|---|---|---|
| Before | 208 | 202 |
| After | **206** | **198** |

The 200-word cap was **already breached before the review**. The merged edit *adds* the R2.5
non-separation qualifier, fixes the R1.1 grammar, and drops R2.4's costless-ISM implication while
coming in shorter. Bound values `(2.48)`, `(2.80)`, "fourth", "tied-first" verified byte-identical;
the RS-12/RS-13 registered verbatims and the Suite-roles sentence untouched.

Rebuilt: `DT-GSK.pdf`, `supplementary.pdf`, `cover_letter.pdf`, `DT-GSK-plain-summary.pdf`. **The
cover-letter PDF was the trap here** — it still matched its manifest hash while containing the old
title, because `validate_document_consistency` compares `.md` against `.tex`, never the PDF.

Gates: `check_frozen_analysis` **115/115**, `validate_provenance_claims`, `validate_citation_cff`,
`validate_artifact_labels`, `validate_build_hygiene` all exit 0; `audit_manuscript` exit 0 with
`terminology_hits: 0` and `blocked_wording_hits` still 2 (pre-existing). `\texttt` count still 0.

**Three "adaptive control" survivals, all deliberate:**

1. **MT-01 bound trio** — "adaptive control-and-budget scaffold" at `introduction.tex:86`,
   `conclusions.tex:16`, `related_work.tex:322` is **frozen contribution wording**. Changing it needs
   explicit sign-off (see §5 decision 8). Reviewer 1 objected to "the title *and text*", so leaving
   these three only partially satisfies him — the case for changing them is strong.
2. **`_dt_core.py:16,204`** expands ACE as "Adaptive Control **of Evolution**" — a different expansion
   from the manuscript's, and the file is **hash-gated**; it cannot be touched. Pre-existing mismatch.
3. **`docs/getting-started/*`** carry incidental mentions; a separate docs pass with
   `scripts/build_docs_html.py`.

**Still owed from Phase 3:** the DOCX pair is now stale (its docProps come from the patched
`build_docx.py`). Rebuilding it belongs to the Phase 5 tail — fresh shell, epoch **1783641600**,
built twice and byte-compared.

### MT-01 settled + Phase 4 (R2.6 defusal) — applied 2026-08-25

**MT-01 resolved: renamed.** Reading the actual governance row settled it. MT-01's
`claim_template` binds that "DT-GSK inherits the GSK junior/senior gaining-sharing operator …
unchanged; **no new base operator is claimed**", its `blocked_wording` is "'Novel operator'; describing
the gaining-sharing operator as novel", and its `risk` is "Reviewer reads novelty into inherited parts".
**None of that constrains the name of the layered scaffold.** So "adaptive control-and-budget scaffold"
→ "adaptive **configuration**-and-budget scaffold" at `introduction.tex:86`, `conclusions.tex:16`,
`related_work.tex:322`, with the inheritance clause verified intact in all three ("leaving that core
unchanged" / "retains the … equations" / "layered on those inherited equations"). The matrix's
`permitted_wording` was updated in the same pass so the record and the prose agree.

**Result: the built PDF now contains zero occurrences of "adaptive control" in any case.**

**Phase 4 — R2.6 needed no manuscript edit**, as decided; the scope restriction was already stated in
six places and the visibility wording rode along inside the Phase 2 edits. What was added is *defusal*
of the two things a reviewer could discover independently:

| Added to §S7 | Why |
|---|---|
| The repository holds exploratory first-party SHADE-ILS / MOS / DECC-G ports, outside the registered panel, analysed nowhere in the paper | They sit in the public repo cited in the Data Availability Statement; silence would read as concealment |
| **The fifty-fold initial-population ratio** — NP = 5D gives **5,000** at D = 1000 against the comparators' **100**, versus five-fold at D = 100 | §S7 previously contained *zero* occurrences of "NP"; answering R1.3/R2.2 only for CEC2017 would leave a 50× version of the same objection live |

Both were added *after* the registered-verbatim scope sentence, never by editing it.

**Three housekeeping corrections**, each a live inaccuracy:

1. `comparability_audit.md` claimed baselines run "reference constants (pop_size 100 where applicable)"
   and marked it PASS. NP = 100 is in fact a **panel normalization traceable to eGSK's published
   CEC2017 panel**, not each comparator's own rule — AGSK specifies 20D, APGSK 200D, FDB-AGSK 40n. The
   PASS rested on a false premise; now corrected and cross-referenced to R1.3/R2.2.
2. `_ablation/manifest.json` called the `no_localsearch` cell "baseline minus eigenframe local-search
   polish". Verified against source: `local_search_method` defaults to `"coordinate"`
   (`_dt_core.py:313`), so that cell removes a **coordinate** search — the eigenframe polish is the
   separate `no_finalpolish` cell. This was exactly the conflation R2.3 alleges.
3. `scripts/run_ablation.py` labelled the same toggle "Nelder-Mead endgame" — also wrong for the frozen
   profile. `evidence_gap_register.md` claimed `T21.tex`/`T22.tex` were "committed … stale-excluded";
   they are neither on disk nor tracked.

**Two findings worth carrying into the experiment track:**

- **EG-006 already registers R2.7 as a known gap.** The parameter-sensitivity tables T21/T22 were
  registered as unavailable long before the review. The reviewer asked for precisely the thing the
  repository had already booked as missing.
- **The final polish is a compass search whose direction set is the eigenbasis, "falling back to the
  coordinate axes when no graph signal exists"** (`_dt_core.py:1890-1900`). That is the mechanism E1
  must separate, and it is why an E1 null is plausible.

*Line-ending note:* the `_ablation` manifest worktree copy had drifted to CRLF via git's autocrlf during
an earlier stash cycle (the committed blob stayed LF). Normalized back to LF; the release self-check
reports all 1297 checksums matching.

### Phase 5 (build tail) — applied 2026-08-25

Every artifact rebuilt and **verified reproducible by building it twice and byte-comparing**:

| Artifact | Bytes | Epoch | ×2 identical |
|---|---|---|---|
| `DT-GSK.pdf` | 818,824 | 1783468800 + `FORCE_SOURCE_DATE=1` | ✅ |
| `supplementary.pdf` | 1,724,326 | same | ✅ |
| `cover_letter.pdf` | 125,722 | same | ✅ |
| `DT-GSK.docx` | 1,010,122 | **1783641600**, `FORCE_SOURCE_DATE` unset | ✅ |
| `supplementary.docx` | 9,611,967 | same | ✅ |

**The epoch trap was avoided deliberately.** `_word_ooxml.py:55` reads `SOURCE_DATE_EPOCH` from the
environment and only falls back to 1783641600 when it is absent — so a shell still carrying the PDF's
1783468800 silently produces a non-reproducible DOCX that still passes every gate. The DOCX pair was
built in a shell where the PDF vars were never exported. Confirmed in the output: both DOCX files carry
`dcterms:created = 2026-07-10T00:00:00Z`, which is 1783641600; the PDF epoch would have read 2026-07-08.

**Manual docProps check** (no validator covers this): both DOCX files carry the new title and subject,
the renamed keyword list with ISM dropped, and **zero** occurrences of "Adaptive Control".

**Reproducibility confirmed across invocations:** the three PDFs rebuilt in this phase are
byte-identical to the ones committed in Phase 3 — the same inputs give the same bytes from a separate
build run, not merely twice in a row.

Also in this phase: `SUBMISSION_KIT.md` abstract and keywords re-copied and its stale "pass-37 / v2.12"
header advanced; submission zips rebuilt (3.9 MB, well under MDPI's 120 MB cap); and the
line-number-keyed audit CSVs (`citation_usage_map.csv`, `phase_08`, `phase_09`,
`cross_format_consistency.csv`) regenerated now that line numbers are final — verified to carry the
rename (30 rows) rather than revert it.

> **Do not regenerate the kit's abstract from `pdftotext`.** The PDF text layer drops the `≥`/`≤`
> glyphs ("runs once at D 50") and hyphenates across wraps ("DT-\nGSK"). The kit is generated from
> `main.tex` with explicit symbol conversion and `break_on_hyphens=False`, then cross-checked against
> the PDF for wording.

Gate battery, all green: `validate_document_consistency`, `validate_docx` (both files),
`validate_cross_format_parity` (**729 rows, 0 FAIL**), `validate_build_hygiene`,
`validate_artifact_labels`, `validate_citation_cff`, `validate_citation_controls`,
`validate_provenance_claims`, `check_frozen_analysis` (**115/115**), `validate_evidence_bindings`.
`audit_manuscript`: `terminology_hits 0`, `blocked_wording_hits 2` (pre-existing).

`check_manifest` is **2/15** — 13 tracked files moved. That is the expected pre-re-mint state and is
exactly what Phase 6 exists to reconcile.

### Phase 6 (governance + re-mint) — applied 2026-08-25 · ~~**TAG WITHHELD**~~ → **superseded: `v2.14` was cut and pushed 2026-08-27**

**Freeze pass-39 is minted; `check_manifest` reads 15/15.** Thirteen of the fifteen tracked files
moved; the manifest was re-minted surgically after verifying it round-trips byte-exactly
(`json.dumps(indent=2, ensure_ascii=False)`, `\n`→`\r\n`, trailing CRLF — 6,758 bytes, 118 CRLF,
zero bare LF). Anchor commit `2bdd9bc`; pre-freeze base `b9846e4`, the submitted state.

> *Correction to an earlier note:* the freeze manifest **does** reproduce byte-exactly from a full
> `json.dumps` round-trip, given `indent=2`, `ensure_ascii=False`, CRLF and a trailing CRLF. A prior
> memo claimed it did not and prescribed regex surgery. The re-mint verifies the round-trip against
> the original bytes *before* rewriting, so the check is enforced rather than assumed.

**⚠️ Historical — true on 2026-08-25, no longer true.** At the time of Phase 6 no tag had been
cut: by author directive **v2.14 was held** until all four experiments were complete and their
results integrated and validated, and the repository was left *tag-ready*, not tagged. The
condition was met, and `v2.14` is now cut and published — see §2. Retained because the Phase 6
record is a history, not a status.

`CITATION.cff` is nonetheless advanced to **2.14** (date-released 2026-08-25). That is deliberate and
is what the gate wants: `validate_citation_cff` enforces that the working tree is *not behind* the
newest tag "so the next tag starts from a correct file". It reports, precisely:
`working tree embeds version 2.14; newest tag is v2.13` → **PASS**. Zenodo reads the version from the
file, not the tag name, so shipping 2.13 inside a future `v2.14` is the exact defect that gate exists
to prevent (it recurred three times before it was automated).

**CR-0023 filed** with sub-items (a)–(f), status *APPROVED AND EXECUTED … OPEN until experimental
closure*. The manifest records `scientific_content_status: REVISION_IN_PROGRESS — text track frozen,
experimental track OPEN`, naming the four outstanding experiments, and its `build_environment` now
carries the DOCX epoch and a note on why the environment variable must not leak.

Final battery, all exit 0: `check_manifest` **15/15**, `check_frozen_analysis` **115/115**,
`validate_cross_format_parity` **729 rows / 0 FAIL**, `validate_document_consistency`,
`validate_build_hygiene`, `validate_artifact_labels`, `validate_citation_cff`,
`validate_citation_controls`, `validate_provenance_claims`, `validate_evidence_bindings`,
`validate_docx` (both files), documentation smoke **7/7**.

### ⚠️ Hazard for the E2 write-up: the runner banner lies about DT-GSK's population

Every DT-GSK run prints **`Pop=100`** in its console banner, at every dimension, whatever the
configuration. It is cosmetic and wrong: `runners/run_experiment.py:345`
(`_optimizer_population_size`) only recognises the `np` / `np_init` keys the AGSK family uses and
falls through to a hardcoded `return 100`. DT-GSK's knob is `pop_size`. The number describes the
runner's shared fair-start payload, which DT-GSK does not consume — it self-initialises
`np_init_mult × dim`, the documented fair-start exception.

Verified against resolved configs (2026-08-25): D=50 → **250**, D=30 → **150**, D=10 → **50**, and
D=10 with `pop_size: 100` → **100**. All correct; only the banner is wrong.

**Why this matters now.** R1.3/R2.2 is *precisely* about NP = 5D vs NP = 100. A reviewer who runs
the released code and sees DT-GSK print `Pop=100` could reasonably conclude the paper's NP = 5D
claim is false. The same hardcoded fallback is what fills the comparator column of Table A19 — it
happens to be right there only because all six comparators genuinely default to 100.

**The campaign has landed, so the hold is discharged** — `run_experiment.py` is not hash-gated and
the one-line fix is now safe. Two things are still owed: the banner correction itself, and the
disclosure of the display defect in the E2 answer. **The response letter does not carry it** — the
R1.3/R2.2 section of `papers/review_2026_08_24/response_to_reviewers.md` never mentions the banner —
so a reviewer who runs the released code can still read `Pop=100` as contradicting the NP = 5D claim.

### Phase 7 (write-up, rebuttal, pass-40) --- applied 2026-08-26

**The revision is complete.** All ten reviewer points are answered, all four experiments are written
into the manuscript, the response letter is written, and freeze **pass-40** is minted at 15/15.

**Supplementary Section S9** carries the four experiments, each bound to the release-locked bundle:

| Section | Experiment | Exhibit | Headline |
|---|---|---|---|
| S9.1 | E1 refinement basis (R2.3) | SA05 / Table A43 | polish beats no refinement at both tiers; **eigenbasis beaten by coordinate axes at D = 50** (Holm 1.4e-4, 4/0/25) |
| S9.2 | E2 matched population (R1.3/R2.2) | SA06 / Table A44 | first at D = 10, second elsewhere; significant only at D = 50 (0.0064) and D = 100 (0.0051) |
| S9.3 | E3 tiered vs tier-constant (R2.1) | SA07 / Table A45 | tiering wins vs U-high at D = 10 and D = 50; **U-low beats tiered at D = 30** (0.0055, 6/3/20) |
| S9.4 | E4 sensitivity (R2.7, exploratory) | SA08 / Table A46 | 26/27 ordinals unchanged, ratios 0.982--1.016; sole flip favourable |

**Main text**, exactly the wording pre-registered for these outcome branches: C1 renamed *a
deterministic final polish* and claimed basis-neutrally; its "remains open" caveat replaced by the
E1 result that closed it; ISM strengthened from "no standalone benefit" to harm in its terminal
exploitation channel; C2 narrowed with the 20 <= D < 50 tier disclosed as mis-specified; the
D = 50 / D = 100 rank claims qualified as resting in part on the NP = 5D rule.

**Response letter:** `papers/review_2026_08_24/response_to_reviewers.md`. Every reviewer sentence is
quoted from the verbatim record; every number is printed in the same notation its exhibit uses.
(Restyled 2026-08-29 to the professor-supplied short-answer format — several comments now appear
as labeled excerpts, and the fully-detailed version this paragraph describes is preserved beside
it as `response_to_reviewers_full_technical.md`.)

**Two things this phase found by reading the built PDF rather than the sources:**

1. `introduction.tex` still labelled C1 "the eigenframe final polish (C1)" in two places --- including
   the closing list of the three principal contributions --- after the earlier pass renamed only the
   bullet. Both fixed. Mechanism descriptions elsewhere keep "eigenframe final polish", correctly:
   E1 falsified the eigenbasis's *value*, not its existence.
2. The **cover letter ships inside the submission bundle** (`build_submission_bundle.py:89`) and still
   carried the pre-E1 claims --- C1 as an "eigenframe final polish", the basis question as one that
   "remains unresolved". Since an earlier pass had already retitled it in place, it is the letter that
   travels with the *current* version, not a round-1 artifact. Converted to revision-1 form: dated
   26 August 2026, marked `algorithms-4507562, revision 1`, C1 basis-neutral, ISM's harm named, closing
   rewritten. CL-02's scientific core and the GenAI disclosure sentence are untouched.

> **Cover-letter date trap.** `validate_document_consistency` matches the TeX date with an
> end-of-line-anchored pattern, so a trailing "(revision 1)" makes the field *unfindable* and the gate
> reports `date: not found in tex`. Keep the date bare in both copies; the revision marker belongs on
> the Manuscript line.

**One validator was extended**, narrowly. `validate_cross_format_parity` now accepts a display cell
that reproduces a semantic value of its own row VERBATIM. That is *stricter* than the per-number check
it short-circuits --- exact equality, not a display-rounded match --- and is what admits a win/tie/loss
triple such as `22/2/5`, whose `/` separators the numeric decomposition otherwise reads as residual
text. The four new exhibits are also rendered strictly rectangular in **both** formats (no spanned
group header), so every LaTeX display row pairs to its semantic row by key; the Word twins render from
the same plain data as the LaTeX rather than being parsed back out of it.

**Freeze pass-40 minted**, anchor `77f9bc0`. Eleven of the fifteen tracked files moved. The manifest
round-trip was verified against the original bytes *before* rewriting (2-space indent, CRLF, trailing
CRLF), so the encoding is enforced rather than assumed. `check_manifest` reads **15/15**.
`CITATION.cff` advanced its release date to 2026-08-26 and its `preferred-citation` note now records
the actual state (submitted 2026-08-01, major revision 2026-08-24, revised 2026-08-26).

Final battery, all exit 0: `check_manifest` **15/15**, `check_frozen_analysis` **115/115**,
`validate_cross_format_parity` **761 rows / 0 FAIL**, `validate_document_consistency`,
`validate_build_hygiene`, `validate_artifact_labels`, `validate_citation_cff`,
`validate_citation_controls`, `validate_provenance_claims`, `validate_evidence_bindings`,
`validate_docx` (both). `audit_manuscript` exit 0, `terminology_hits 0`, `blocked_wording_hits 2`
(pre-existing). Every artifact rebuilt and verified reproducible by double build and byte-compare;
`DT-GSK.pdf` and `DT-GSK.docx` also reproduced on a third invocation. Committed blob sizes checked
against disk with `git cat-file -s` for all ten content files, closing the `check_manifest`
worktree blind spot.

### What remains

1. ~~Tag v2.14~~ --- **DONE and PUBLISHED** 2026-08-27, on the squashed publication commit
   `02d1791`. Verified from the public internet: the `v2.14` and `v2.13` trees both resolve, so
   both tags the Data Availability Statement names are live, and the pre-registration resolves ---
   which is what makes the claim that adverse-outcome wording predates the outcomes checkable
   rather than asked-on-trust. The reviewers' reports, the response letter, the co-author handoff
   and seven copyrighted PDFs all return 404 (D-0049).
2. **SuSy portal (author only)** --- the one thing left. Re-enter the new title and the revised
   keyword list in the revision form; portal metadata does not update from the PDF. Upload the
   revised manuscript, the supplementary, the figures and LaTeX-source zips, the cover letter,
   the response letter (`papers/submission/response_to_reviewers.pdf`, rendered
   2026-08-29 from the current source), both changes-marked manuscripts and the change register
   (`DT-GSK-change-register.pdf`, every changed passage as-submitted vs
   as-revised --- read the live page and passage counts off the register's own front page; every
   numeric copy of them recorded elsewhere has gone stale). All four sit staged in
   `papers/submission/`, deliberately NOT in the repository
   (pinned in `.gitignore`) and regenerable --- the letter from its Markdown source on disk, the
   marked copies and the register from `git diff v2.13 v2.31`. Paste text and the full
   upload table are in `papers/submission/SUBMISSION_KIT.md`.
3. **`runners/run_experiment.py` `Pop=100` banner** --- **DONE** (verified 2026-08-29): the
   `_optimizer_options_line` dt-gsk branch now prints the `NP_init=5D` rule with an explanatory
   comment; nothing remains here.
4. **`papers/PAPER_REVIEW_PROMPT.md` old-title mention** --- **DONE**: the only remaining "Adaptive
   Control" occurrence is the deliberate confirm-none-survives verification instruction.
5. **Freeze inventory** --- **DONE** (pass-43): the manifest's `source_files` records `supplementary.tex`
   and `cover_letter.tex`, and `check_manifest` reports `sources 2/2` on its own line, closing the
   asymmetry this item described.

## 4. Decisions already made (do not relitigate)

| Decision | Resolution |
|---|---|
| **New title** | `DT-GSK: Dimension-Tiered Adaptive Configuration Selection and Deterministic Refinement for Gaining-Sharing Knowledge Optimization` — Reviewer 1's own second suggestion. Keeps "Deterministic Refinement" (contribution C1), which both of his proposals dropped. **Applied in Phase 3** across 20 files; the built PDF carries zero occurrences of "Adaptive Control". |
| **"Operator-State Adaptation"** | Declined, with reason: tiering keys on problem dimension, resolved before the run (`_dt_profiles.py:253`), not on operator state. Declining one of two offered options reads as engagement. |
| **R2.6 external baselines** | Take the reviewer's **second limb**: claims stay explicitly GSK-family-only. No external algorithm enters the panel. This requires **zero manuscript edits** — the restriction already exists in six places. Recommended (optional) defusal: one sentence in §S7 disclosing the repository's exploratory SHADE-ILS / MOS / DECC-G LSGO ports. |

## 5. Open decisions — blocking, author only

1. **Revision deadline — CONFIRMED 2026-09-01 (author, 2026-08-27). This is the binding
   constraint and there is no slack in it.** This entry previously read "never answered, no
   longer gating", then carried **2026-09-03** as an *inference* from the letter's ten-day
   window. The confirmed date is **two days earlier than that inference** and falls **on the
   author's planned resubmission date**, so planned and required now coincide: a slip of one
   day is a missed deadline, not a late-but-safe upload. Five days remain from 2026-08-27.
   It is the only dated constraint left — the GitHub Traffic → Clones expiry these documents
   had been treating as the most urgent item was discharged by capture on 2026-08-27 (row 0a),
   and the purge request is closed unfiled (row 0b). The letter is withheld under D-0049 and transcribed
   at `papers/review_2026_08_24/journal_decision_email.md`.
   ~~**Request more time.**~~ — **CLOSED 2026-08-28: will not be requested.** The e-mail invites
   one, and with plan and deadline on the same day it was the only available source of margin.
   The author declined on 2026-08-27 and closed it on 2026-08-28. **Not a to-do; do not re-raise
   it.** The consequence is accepted knowingly: resubmission is on 2026-09-01 and a one-day slip
   is a missed deadline. The invitation remains in the letter should the author ever choose to
   use it, but no agent should propose it again.
   ✅ **Check-list item (II) is DISCHARGED (2026-08-27).** The letter asks that revisions be
   *highlighted in the manuscript*, and the project now produces exactly that:
   `DT-GSK-changes-marked.pdf`, a latexdiff marked-up manuscript with additions underlined and
   deletions struck through in place, from `papers/scripts/build_change_marked_pdf.py` (48 pp; 47
   added and 40 deleted blocks). Beside it `DT-GSK-change-register.pdf`, from
   `build_change_register.py`, lists all 102 changed passages as-submitted against as-revised with
   the reviewer point each answers (21 pp). Both are derived and gitignored; both rebuild from the
   tags, over the same 7 files — read the passage count off the register's own
   front page; the clause has carried five different numbers (54, 75, 93, 102,
   115) and every copy of it has gone stale in turn.
   **Two claims this entry previously made were false and are withdrawn.** It said the manuscript
   already uses `\hl`, so a blanket pass would collide with existing markup: it carries **no
   highlighting at all** — no `\hl`, no `soul`, no `colorbox`, nowhere in `main.tex`,
   `supplementary.tex` or the six section files. And the kit said latexdiff was unusable because
   MiKTeX ships only a Perl shim: half right. Plain `latexdiff` does fail, on a missing
   `Algorithm::Diff`, but **`latexdiff-so` bundles it and works**; with `ulem` added the four-pass
   build is clean. The cheaper option had been made to look like the only option.
   ⚠ **One caveat survives, and it is author-side at upload.** latexdiff records preamble changes
   as comments, so **the retitle does not appear marked** in the PDF although it was made. That is
   stated twice in the point-by-point response — in the artifact overview and under R1.2 itself —
   so it is covered; it is recorded here only so nobody re-discovers it as a defect. Whether MDPI
   accepts these two documents remains an editorial question that has not been put to the journal.
2. ~~MT-01 bound wording~~ — **SETTLED and applied.** MT-01 binds the *no-novel-operator* claim, not
   the layer's name; renamed in all three sites with the inheritance clause intact, and the matrix
   `permitted_wording` updated to match.
3. ~~`main.tex:156` "eigenframe refinement"~~ — **RESOLVED by E1 and applied.** The abstract now
   reads "budget-exact final refinement"; zero occurrences of "eigenframe refinement" survive in
   `main.tex` or any section. C1 is basis-neutral throughout.
4. ~~`PAPER_REVIEW_PROMPT.md` names the OLD title as "CURRENT"~~ — **DONE 2026-08-27.** All four
   stale occurrences retired, including the two inside the residual-gap audit step. The one
   surviving mention of the old fragment is deliberate: Section 1.5.3-J instructs a reviewer to confirm
   none survives.
5. **SuSy portal (author-only)** — the new title and the revised keyword list must be re-entered in the
   revision form. Portal metadata does not update from the PDF.
6. **Make the repository PUBLIC again before uploading (author-only, 2026-09-01).** The author set it
   private on 2026-08-28 to finalize; verified private (API 404). The Data Availability Statement in
   the revised manuscript names the repo URL and tags v2.13/v2.31, and the Supplementary's
   pre-registration claim depends on public checkability — a reviewer clicking during round 2 must
   not hit a 404. Flip visibility BEFORE the SuSy upload. After the flip, verify from a
   LOGGED-OUT/private browser window that the repository, both DAS-named tags and the
   pre-registration file are anonymously accessible — the letter's present-tense
   availability claims are checked by exactly that test. Side effect while private: the two
   GitHub-exposed commits are not publicly served; public serving resumes with visibility.

*Resolved in Phase 3:* keyword drop (done, five places), ACE re-gloss (done, acronym kept),
`related_work.tex:29` heading (done), `citation_usage_map.csv` 30-row rename (done).

## 6. What to do next

Ordered. Phase 0 is author-only and one item **expires**; everything else is agent work.

### Phase 0 — today, in parallel, nothing depends on them

| | Action | Why now |
|---|---|---|
| ~~0a~~ | ~~**GitHub → Insights → Traffic → Clones** — capture the count~~ — **DONE 2026-08-27** | Captured: 11 clones, 9 unique cloners, 08/13–08/26 — all 14 days inside the exposure window; 2 web views. **Six days (08/07–08/12) had already rolled off and are permanently lost**, so the counts are floors. Record: `docs/development/github_exposure_traffic_record.md`. |
| 0b | **GitHub Support ticket** — garbage-collect **`b9846e4` *and* `bddfe24`** — **REOPENED 2026-08-28 (author instruction), to be FILED** | Closed unfiled earlier the same day; the author then instructed it be treated as an active task. While the repository is PRIVATE the objects are not publicly served, so the ticket is best filed immediately AFTER the public flip on upload day, when the served-by-SHA claim is verifiable again. The ready-to-send request text and both full SHAs: the withheld `papers/review_2026_08_24/PRIVATE_OPS.md` (moved there by the 2026-08-29 public-release cleanup; the tracked exposure record keeps the incident narrative with short prefixes only). |
| ~~0c~~ | ~~Tell the co-authors their biographies were public~~ — **DONE 2026-08-27** | Discharged by the author; D-0049's co-author limb is closed. |

### Phase 1 — C1, resolved for the caption; one author decision left

§2a settles what matters: **contribution C3 is not falsified and must not be narrowed**, and the
caption fix (§2c **E13a**) is deliberately **decision-independent** — it deletes the false clause
and asserts no cause, so it ships now. Do **not** put a vintage explanation in the caption: it is
non-discriminating (both controls share one reference file) and it would falsify the bound claim at
`supplementary.tex:1254-1267`.

**~~The author decision is §2c E13c~~ — CLOSED (D-0051).** The "one hole at CR-0015" reading that
motivated it is **refuted** (CR-0014, CR-0016 and CR-0018 all certify cec2017 D100), and the
residual is now **demonstrated to be a build difference** by a pinned re-execution, independently
replicated. Pass-43 reconciled the Supplementary with the response letter, which is the whole of
what was owed. **No body edit to `:1254-1267` is required.**

### Phase 2 — close the specification gap

**Done — the drafts exist, were challenged, and are recorded as §2c (E13–E17).** What remains
inside Phase 2 is only what §2c marks unfinished: **E13b**'s prose (site verified, text not
audited) and the **E13c** author decision. Note that "no gate checks the tag" was **wrong as
scoped**: `validate_citation_cff.py` gates `CITATION.cff`, which must move to `2.15` in the same
mint, and three further files hardcode the tag — see §2c §5.

### Phase 3 — DONE (2026-08-27)

**A12 convention discrepancy — REFUTED as a defect.** The alleged collision was that the same
contrast prints `0.59` and `0.511` with no distinguishing note. It does not hold: the S6.5 table
header at `supplementary.tex:2238` reads **"mean $A_{12}$"**, which distinguishes it from S9.1's
pooled statistic, and the two are drawn from **different releases** (`abl-rel-2026-07-20` vs
`rev-rel-2026-08-26`) — different runs, not the same data. Different conventions legitimately give
different values, so there is no factual error. **One residual, optional and cosmetic:** the prose
at `:2275` writes "$A_{12} = 0.59$, $0.53$, $0.64$" *without* the "mean" qualifier the table
carries, which is the one place a reader could collide it with Table A43's `0.511`. Adding "mean"
there is a one-word edit. Not worth a pass on its own; take it only if the pass is open anyway.

**Byte-stability KAT extended to D ≥ 50 — APPLIED.** New file
`tests/regression/test_dt_gsk_byte_stable_high_dim.py` (LF, matching its sibling), 5 cec2017 cells
at D = 50 and D = 100 on F7/F13/F20 — among the functions that diverged across builds, so it
exercises the sensitive path rather than a quiet one. **10 passed in 14 s**; the full regression
suite is **278 passed**; `check_manifest` remains **15/15** (nothing under `papers/` is touched).

Three design decisions worth keeping:

1. **It asserts repeat-identity, not golden values.** At D ≥ 50 the polish basis is an
   eigendecomposition, so the *value* depends on BLAS reduction order: one cell was observed at
   three different values under one thread, eight threads and inherited settings. Repeat-identity
   holds at **any fixed thread count** (verified at 1 and at 8), so the test is portable and needs
   no thread pinning and no new dependency. **Do not add expected constants to that file** — they
   would encode one machine's LAPACK.
2. **It guards its own activation.** A companion test asserts `interaction_graph_enabled`,
   `final_polish_enabled` and `dim >= interaction_graph_min_dim` at each cell, so a profile change
   cannot leave it passing while covering nothing — which is exactly how the D ≤ 30 cells silently
   covered nothing.
3. **It was negative-tested.** Perturbing the seed on the second run makes both assertions fail
   (`best_fitness` and the `best_x` byte comparison), so neither is dead code.

**This is what turns C3 from asserted into demonstrated**, and it closes the gap CR-0007 named when
it recorded that the byte-stability KAT "could not catch this because its cells are D<=30". It does
**not** resolve the Table A45 residual, which is a cross-build question (§2a).

### Phases 4–6 — DONE (2026-08-27)

Applied, built, verified, minted, tagged and pushed. 43 edits across 17 files; every FROM anchor
verified byte-exact and unique before any write; per-file line endings preserved. All five
artifacts rebuilt **twice** and byte-compared — reproducible, so the DOCX-epoch trap is cleared.
The `_pandoc` shims and `docs/html` were **regenerated**, never hand-edited. Thirteen gates green,
`check_manifest` 15/15, `check_frozen_analysis` 115/115. Every edit verified in the **built PDF**
and in the DOCX. Freeze **pass-42**, **CR-0025 / D-0050**, tag **v2.15** pushed; anchor `4a2291bd`,
published `ebcdefe`.

Three things worth carrying forward:

- **The cover letter was nearly missed.** The manifest hashes `cover_letter.pdf` but not
  `cover_letter.tex`, so editing the source left the render matching its recorded hash while still
  carrying a retracted phrasing — and it **ships to the editor**. Caught only when the manifest
  listed which of the fifteen files had moved. If you edit a `.tex` whose render is hashed, rebuild
  the render.
- **The last unaudited draft was rejected on challenge.** Mirroring the approved caption wording
  into the reviewer letter would have asserted that the D = 10 arm ties "below the D ≥ 50 gate",
  which in that document reads as covering D = 10 **and D = 30** — directly above a table printing
  the D = 30 arm at 6/3/20, Holm-significant. It would have read as retracting the revision's own
  tier mis-specification finding.
- **Two pre-existing defects were fixed alongside**, both verified pre-existing at HEAD: a
  generated-docs link emitted at the wrong relative depth, and two ruff findings — one genuinely
  dead, one **load-bearing** (its subscript is a fail-closed guard, kept with a `noqa`).

### Phase 6b — pass-43, DONE (2026-08-27)

Cut because pass-42 left the **package** self-contradictory: the response letter concedes the
D = 100 internal control does not hold, while `supplementary.tex` still asserted no reported number
depends on which revision is used. Both ship to the referees together. One prose edit reconciles
them; tag **v2.16**, **CR-0026 / D-0051**, anchor `ae4d4e76`, published `fe813ff`. All four main and
supplementary renders rebuilt twice and byte-compared; eleven gates green; the edit read back out of
the built PDF, where the reference resolves to Table A45.

**A larger disclosure was drafted and REJECTED on challenge — do not revive it.** It would have
named CR-0015 as the one bit-identity certification not spanning cec2017 D = 100. The register
refutes that three times over: **CR-0014 certifies cec2017 D100, CR-0016 certifies D10/D50/D100,
and CR-0018 certifies an 84-cell ledger including that cell bit-for-bit.** It also asserted the
divergence was confined to the tier where the memory and the polish are active — a cause — while
disclaiming any cause in the next clause, and there is no identity control at D = 50 at all.

**The real limitation is recorded in governance, not in the paper — and D-0051 is ANSWERED, not
open.** The campaign's identity evidence samples about one run per (algorithm, suite, dimension),
so a divergence in 27 of 1479 cells sits below its resolution. The certifications are underpowered
here, not wrong. Claiming that in the manuscript would impeach every certification in the campaign
on one uncontrolled cross-build comparison.

This paragraph used to end "the route to closing it is a re-execution, not prose" and to label
D-0051 **OPEN**. **The re-execution was then run, on 2026-08-27, and it closed the question**:
the five carrier functions re-run at CEC2017 $D = 100$, 51 runs each, threads pinned as
`run_campaign.py::pinned_env` pins them; 255 cells, zero seed mismatches; on the 26 cells where
the archive and the transplant arm differ the fresh run reproduces the transplant arm on all 26
and the archive on none, and on the 229 where they agree it reproduces both. The difference is
**between builds, not within one** — inferred before, demonstrated now, and independently
replicated the same day in a separate process and shell. D-0051 records **"ANSWERED 2026-08-27 by
the re-execution this entry called for"**; only this sentence still said otherwise.

**What is not taken is a separate thing, and it is a closed decision rather than an open item.**
Stating the stronger claim in the manuscript would mean **promoting a diagnostic staging run as
cited evidence** — new release id, manifest and binding — because every reported number is bound
to a promoted release. **That promotion is CLOSED by author decision (2026-08-28) and will not be
done** - the diagnostic stays diagnostic, `results/_g1_recheck/` stays gitignored staging, and no
release id, manifest or binding will be minted for it. The Supplementary and the Table A45 caption
both already say the control does not reproduce the archived runs exactly, both stay true, and the
finding itself is recorded in full at D-0051. Do not re-raise this as work outstanding.

**H1 is done, and gated.** `source_files` now records `supplementary.tex` and `cover_letter.tex`;
`check_manifest` reports `sources N/N` separately, so `files` stays at 15 and every recorded
"15/15" remains true. Negative-tested: perturb a source, leave its render, and `files` reads 15/15
while `sources` drops to 1/2 and the gate exits 1 — exactly the pass-42 failure, now caught.

### Phase 6c — pass-44, DONE (2026-08-27)

The three optional wording items (C5, O1, the A12 qualifier) carried as **one** pass, not three,
because every manuscript pass forces a tag bump that drags `CITATION.cff`, `SUBMISSION_KIT.md` and
`submission_package_manifest.json` with it. Tag **v2.17**, **CR-0027 / D-0052**, anchor `4b5c6ae`.

**Two of the three were relocated on challenge, and the relocations are the point.**

- The **Table A44 caption** edit was **dropped**: the body seventeen lines below already states that
  Friedman ranks are relative *and* carries the differencing prohibition. The real hole was **Table
  A46** — the supplement's only differencing prohibition sat at `:3760`, attached to A44 alone. A46
  now carries the bar rather than the premise.
- The **A12 qualifier moved from the prose to the definition.** Adding "mean" at `:2280` would have
  qualified three of the six values that paragraph draws from one column, while a clause two lines
  earlier called it "the raw-run effect size" — asserting two conventions where there is one. S6.5
  now declares once at `:2216` that $A_{12}$ is per-function, averaged over functions.
- **The recorded O1 cost estimate was wrong, which is why the item had been deferred at all.** It
  claimed the edit touched the generated exhibit chain; verified false — `SA06.json`'s
  `caption_stub` does not render, and the DOCX caption is pandoc's conversion of the `.tex`. A
  `.tex`-only edit sufficed.
- **The pass-43 source guard earned itself**, reporting `supplementary.tex` moved and
  `cover_letter.tex` unmoved — exactly the discrimination it was added for.

✅ **The A12 collision is CLOSED — pass-45 (`5fa4d38`) did it; the flag was simply never retired.**
This paragraph pointed *forward* to the pass-45 ticket list, pass-45 executed it, and nobody came
back to strike the warning. Re-verified 2026-08-27: both conventions now declare themselves, and
the caption disambiguates against the other **by name**. S6.5 at `supplementary.tex:2227` reads
"computed per function on the raw runs and averaged over functions"; Table A43's caption at
`:3708` reads "$A_{12}$ over the paired runs of all scored functions pooled --- *not* the
per-function-averaged $A_{12}$ of Section~S6.5". So 0.511 and 0.59 on the identical contrast are
now two **named** statistics rather than one self-contradicting one — which is the correct
resolution, since both values are right under their own convention and neither needed changing.
The `:2216` / `:3688` line numbers above are pre-pass-46 and no longer resolve; the current ones
are given here.

### Phase 7 — resubmit (author-only; the point of no return)

**Deadline CONFIRMED 2026-09-01, and the planned resubmission date is the same day.** Everything
agent-side is complete at pass-58 / `v2.31` (pass-51's acceptance-readiness fixes plus the
seven-lens panel review: the response letter's stale abstract quote and two superseded E1
p-values corrected, SA01/SA02 renamed to the typeset Tables A23–A24, and the cover letter's
stale 84-passage count made count-free — D-0057 / CR-0032); nothing in the repository blocks that date. The
earlier **2026-09-03** figure was an *inference* from the letter's ten-day window and is
**superseded** — the real date is two days tighter, so the margin the documents assumed does not
exist. Plan and deadline now coincide and the resubmission has **zero slack**. The letter invites
a request for more time; that request is now the only source of margin there is.

**Confirmed from the portal 2026-08-27:** it still carries the **submitted** title
("… Adaptive **Control** …"), 26 days after submission. That is direct evidence for the standing
warning that portal metadata does not update from the PDF. Re-enter both by hand:

- Title: `DT-GSK: Dimension-Tiered Adaptive Configuration Selection and Deterministic Refinement for
  Gaining-Sharing Knowledge Optimization`
- Keywords (9, semicolon-separated) — note the third one moved with the title:
  `metaheuristic optimization; gaining-sharing knowledge; dimension-tiered adaptive configuration
  selection; deterministic final refinement; adaptive operator selection; population-size reduction;
  CEC benchmark suites; nonparametric statistical comparison; reproducibility`

**Generate both companion PDFs fresh.** The response letter's source was edited in passes 42, 43 and
50, 53, 54, 56, 57 and 58, and the change register must come from `git diff v2.13 v2.31`. Read its passage count
off its own front page — no figure for it should be quoted anywhere, because every copy has gone stale.

**After upload, no rebuilds.** The DAS-named tag becomes the frozen record of what was resubmitted
(read it off `papers/main.tex` at upload time); any later revision is a new pass with a new
superseding tag, never an edit to the submitted tag in place (D-0045).


SuSy upload; **re-enter the new title and revised keywords by hand** — portal metadata does not
update from the PDF. After this, **no rebuilds**: v2.15 becomes the frozen record of what was
resubmitted, and any further defect becomes a correction to a live submission.

### Phase 8 — housekeeping, DONE (2026-08-27)

- `PAPER_REVIEW_PROMPT.md` — four occurrences of the pre-Phase-3 title retired, two of them
  asserting it as FINAL/CURRENT inside the residual-gap audit step.
- `run_experiment.py` — the console banner announced `Pop=100` for DT-GSK, a value no run ever
  used: DT-GSK carries no `np` option, the population is `np_init_mult * dim` = 5D. Now prints the
  rule. Display-only; nothing parses it.
- Generated-docs link depth and two ruff findings — fixed earlier the same day, both verified
  pre-existing at HEAD. One ruff finding was **load-bearing** and kept with a `noqa`: its subscript
  is a fail-closed guard on the manifest key.

**Do not** re-run the experiment track, re-derive the phases, or regenerate
`benchmarks/cec_reference_results/`. If you are reading this for a plan of the revision *itself*,
you are one section too late — that history is §3.

## 7. Traps — every one verified in this repository

| Trap | Rule |
|---|---|
| **LaTeX via bash heredocs** | **Never.** Backslash collapse has already shipped literal "oindent" and "imes" into a released PDF. Use exact-match file editing. |
| **Line endings are per file** | CRLF: `main.tex`, `performance.tex`, `proposed_algorithm.tex`, `supplementary.tex`, `decision_log.md`, `citation_usage_map.csv`, both freeze manifests (CRLF + 2-space). LF: `introduction.tex`, `related_work.tex`, `conclusions.tex`, `SUBMISSION_KIT.md`, the `_ablation` manifest (LF + 2-space + trailing newline). Multi-line edits must join with the file's own ending or the match silently fails. |
| **DOCX epoch** | DOCX = `1783641600`; PDF = `1783468800` (PDF also needs `FORCE_SOURCE_DATE=1`). The builder *prefers* a lingering env var, so a stale shell silently produces a non-reproducible DOCX that still passes the gate. Fresh shell, explicit epoch, build twice, byte-compare. |
| **`check_manifest` blind spots** | Hashes the **working tree**, not the committed blob (a Word re-save once passed 15/15 in commit `fa613cf`). It also walks manifest→disk only, so a file on disk but absent from the manifest is invisible. Verify committed blobs with `git cat-file -s`. |
| **Untracked-but-changed** | `supplementary.tex`, `cover_letter.tex`, `cover_letter.md`, `SA01.tex` are **not** in the 15-file freeze manifest — `check_manifest` will never notice edits to them. |
| **`_dt_core.py` is hash-gated** | `validate_provenance_claims.py` hashes it on a SHIPPED list. **Even a comment edit fails the gate.** Never touch it during the revision. |
| **Cover-letter title gate** | `validate_document_consistency.py:153-156` exits **1 (DRIFT)** — fatal — if `cover_letter.md` and `cover_letter.tex` titles disagree. They must move together. |
| **docProps is ungated** | `build_docx.py:110-111 / :130-131` hard-code the DOCX title; nothing validates it against `\Title{}`. Check by hand. |
| **Multi-line wraps** | `main.tex:95-96` (title), `:152-153` (abstract), `CITATION.cff:71-72`, `README.md:5-6`, `SUBMISSION_KIT.md:48-49`, `DT-GSK-plain-summary.tex:74-75`. Single-line find-and-replace misses all of them. |
| **Pandoc shims** | `main_pandoc.tex` / `supplementary_pandoc.tex` are regenerated by `build_docx.py` — never hand-edit. |
| **Reading the built PDF: use `pdftotext`, not pypdf** | The standing rule is *read the built PDF*, so the extractor is part of the rule. **pypdf silently drops the space between a word and adjacent inline math**, rendering `the $20 \leq D < 50$ tier` as `the20 ≤D< 50tier` — 5 such manglings in `DT-GSK.pdf`, against 1 under `pdftotext`, which is installed. A defect was reported against the manuscript on that basis on 2026-08-28; the LaTeX was correct and the PDF was correct. **Verify any suspected rendering defect with a second extractor before believing it.** The live gates are unaffected and were checked: `validate_provenance_claims.py` uses pypdf but matches release identifiers after `re.sub(r"\s+", "", sent)`, so lost spaces cannot change its verdict, and it passes; `validate_build_hygiene.py` already uses `pdftotext`. The hazard is a **future** check that searches rendered prose containing math. |
| **Append-only trees** | `papers/build_prompt_phases/`, `papers/review_2026_07_22/`, `papers/governance/remediation_2026_07_18/`. The **old title should remain** in these. |
| **No monospace** | `\texttt` count stays 0 — and `audit_manuscript.py` has **no** `\texttt` gate, so grep separately. Line numbering stays off (`\let\linenumbers\relax`). |
| **Blocked phrases** | "state-of-the-art", "best algorithm" — enforced by `audit_manuscript.py`. |
| **Do not run** | `papers/scripts/finalize_evidence.py` (standing instruction). Drive promotion manually. |
| **Dual-repo hazard** | Work only in this repository checkout. A divergent copy lives in the PhD-Projects monorepo; each freeze manifest hashes only its own tree, so both can report "15/15" while disagreeing. |
| **v2.13 is frozen history** | Per D-0045, a revision is a **new freeze pass through change control** — never an edit to the submitted state. |

## 8. Where state actually lives

| What | Where |
|---|---|
| Decisions — 46 ids, D-0001…D-0046 | `papers/governance/decision_log.md` (48 `## D-` headings: D-0005 and D-0010 each appear twice) |
| Claim → evidence bindings | `papers/governance/claims_evidence_matrix.csv`, `artifact_binding.csv` |
| Change requests (22 rows; next is **CR-0023**) | `papers/governance/change_request_register.csv` |
| Freeze manifest (15 tracked files) | `papers/governance/main_manuscript_freeze_manifest.json` |
| Frozen primary evidence | `benchmarks/cec_reference_results/` — release `rel-2026-07-20-67d9345f9` |
| Ablation evidence (1297 files) | `benchmarks/cec_reference_results/_ablation/` |
| Analysis outputs | `papers/analysis/rel-2026-07-20-67d9345f9/` |
| Manuscript sources | `papers/main.tex`, `papers/sections/*.tex`, `papers/supplementary.tex` |
| Development plans | `docs/development/*.md` |

**Governance ids:** D-**0047** is **filed** (2026-08-25, `decision_log.md:1865`) — it records the review,
the scope and title decisions, the applied R1.4 change, and supersedes D-0045's "do not rebuild" hold for
the revision line. Still to file: CR-**0023** (sub-items a–f). D-**0048** is reserved for R2.6 should the
family-scope decision ever be revisited. Re-verify any id is free at apply time.

---

*Maintenance rule: update the header table and §3 whenever a phase lands. Keep this file dense — its
purpose is to let a fresh session reconstruct status without reading the decision log end to end.*
