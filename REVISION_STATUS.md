# REVISION_STATUS.md — where this project is right now

**Read this first if you are resuming work.** It is the single source of truth for *current state*.
Architecture, rules, and how-to live elsewhere (see [REPO_MAP.md](REPO_MAP.md)); this file records only
what is happening, what is done, and what is next.

| | |
|---|---|
| **Last updated** | 2026-08-27 |
| **Manuscript** | `algorithms-4507562` — *Algorithms* (MDPI) |
| **Submitted** | 2026-08-01 from freeze **pass-38 / tag v2.13** (anchor `b515907`) |
| **Editorial status** | **MAJOR REVISION** — 2 reviewers, received 2026-08-24 |
| **Branch** | `main` — **published** at `02d1791`, tracking `origin/main`. Work continues here. `archive/revision-pass-39-full` holds the development history and must never be pushed |
| **Progress** | **COMPLETE** — all ten reviewer points answered; phases 1–7 applied; four experiments run, analysed and written up. |
| **Freeze** | pass-41 re-minted, `check_manifest` 15/15 · anchor `6fb0506` · **v2.14 PUBLISHED** on the squashed commit; `v2.13` still resolves, so both tags the DAS names are live |
| **Revision deadline** | Still unstated, but no longer gating — the experiment track is complete |

---

## 1. The review in one paragraph

Two reviewers, neither recommending rejection. Every substantive criticism is about
**attribution, not validity**: the paper bundles several mechanisms and never isolates the
dimension-tiered design the title is named after. Both reviewers independently raised the
population-size confound, which makes addressing it effectively mandatory.

**The reports are not in this repository** (D-0049). Both reviewers declined to sign, and
republishing a confidential report is the journal's act at acceptance, in the journal's own form —
not the authors' to take unilaterally, mid-revision. The verbatim record, Reviewer 1's original PDF
and the point-by-point response are on disk, ignored by `.gitignore`, and retained in git only on the
never-pushed branch `archive/revision-pass-39-full`. Read the verbatim record on disk before drafting
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

**The write-up is done too.** Supplementary Section S9 carries all four experiments as Tables
A43--A46, the pre-committed C1/ISM/C2 manuscript edits are applied, the point-by-point response letter
is written, every gate is green, freeze pass-41 is minted at 15/15, and **v2.14 is published**.
`origin/main` carries the squashed revision commit and both `v2.13` and `v2.14` resolve publicly, so
the Data Availability Statement works for the submitted and the revised version alike. What is left is
the author's SuSy resubmission, the GitHub Support ticket, and one confirmed defect — see §2a.

## 2a. Open against the published paper

**One confirmed defect, and a verification pass over eleven more.**

**CONFIRMED — Table A45 caption.** Supplementary S9.3's caption says the two identity controls
"coincide with the tiered configuration by construction, which the tie counts confirm". The
U-low/D = 10 control does (0/29/0). The U-high/D = 100 control prints **2/25/2**. Traced: the
resolved configuration, the execution environment and the evaluation budget are **identical**
between the two legs (the one apparent config difference was a `json.dump` artifact — YAML parsed
the integer keys correctly), and NP was not transplanted, so E3 is budget-fair. Yet **27 of 1479**
run cells differ at D = 100, median relative 1.6e-4, **max 5.3e-2** — not floating-point noise.

Two things follow. The caption states something its own table falsifies, on the same page. And the
residual sits in tension with contribution **C3**, which claims byte-stable determinism in the
declared environment. The cause is not established; do not assert one.

**Why every gate passed over it:** `validate_cross_format_parity` was green because the PDF and the
DOCX agree — both carrying the same wrong caption — and `validate_evidence_bindings` excludes
`% BIND:` comment text from token extraction by design. This is the third defect in this project
caught only by reading the built PDF rather than the sources. **Read the PDF.**

**UNDER VERIFICATION when this was written.** A prior assessment alleged eleven further defects.
Spot-checking already refuted one (the claim that the NP qualification appears nowhere — the main
text mentions matched population 11 times and cites S9.2 twice) and downgraded another ("ordinals
identical in every variant reported here" is scoped to rank-computation robustness variants, so it
is ambiguous rather than false). **Do not act on that assessment unverified.** The remaining claims
concern: an S6.5-vs-S9.1 arithmetic contradiction on the ISM channel; "only fitness-affecting
channel" versus "two active channels"; "perturbs no tier threshold" versus `argp_threshold`;
"no constant is knife-edge" versus the n_min flip; effect-size language against A12 values in
[0.493, 0.518]; and an Overall-column recomputation at matched NP.

**A leaked meta-note was published and is now removed.** An agent's instruction to the applier
("[APPLY NOTE: join these two lines with CRLF...]") was written into this file verbatim and reached
`origin/main`. The applier matched and wrote proposed text without checking the *replacement* for
meta-content. A tree-wide scan found no others. If you apply agent-proposed edits, scan the
replacements, not just the anchors.

## 3. What has already been applied

All six zero-run reviewer points are closed. Commits are on `revision/pass-39`.

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

### Phase 6 (governance + re-mint) — applied 2026-08-25 · **TAG WITHHELD**

**Freeze pass-39 is minted; `check_manifest` reads 15/15.** Thirteen of the fifteen tracked files
moved; the manifest was re-minted surgically after verifying it round-trips byte-exactly
(`json.dumps(indent=2, ensure_ascii=False)`, `\n`→`\r\n`, trailing CRLF — 6,758 bytes, 118 CRLF,
zero bare LF). Anchor commit `2bdd9bc`; pre-freeze base `b9846e4`, the submitted state.

> *Correction to an earlier note:* the freeze manifest **does** reproduce byte-exactly from a full
> `json.dumps` round-trip, given `indent=2`, `ensure_ascii=False`, CRLF and a trailing CRLF. A prior
> memo claimed it did not and prescribed regex surgery. The re-mint verifies the round-trip against
> the original bytes *before* rewriting, so the check is enforced rather than assumed.

**⚠️ No tag was cut. `v2.13` is still the newest tag.** By author directive (2026-08-25), **v2.14 is
held until all four experiments are complete and their results integrated and validated.** The
repository is left *tag-ready*, not tagged.

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
E1 result that closed it; ISM strengthened from "no standalone benefit" to harm in its only
fitness-affecting channel; C2 narrowed with the 20 <= D < 50 tier disclosed as mis-specified; the
D = 50 / D = 100 rank claims qualified as resting in part on the NP = 5D rule.

**Response letter:** `papers/review_2026_08_24/response_to_reviewers.md`. Every reviewer sentence is
quoted from the verbatim record; every number is printed in the same notation its exhibit uses.

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
   the response letter (`response_to_reviewers.pdf`, 10 pages) and the changes-marked register
   (`change_register.pdf`, 17 pages, all 54 changed passages as-submitted vs as-revised). The
   last two are deliberately NOT in the repository and are regenerable --- the letter from its
   Markdown source on disk, the register from `git diff v2.13 v2.14`. Paste text and the full
   upload table are in `papers/submission/SUBMISSION_KIT.md`.
3. **`runners/run_experiment.py:725`** (and `:714`) --- the cosmetic `Pop=100` banner defect, in
   `_optimizer_options_line`; **not** `_optimizer_population_size` at `:345`, which only sizes the
   shared fair-start payload DT-GSK never consumes. Safe to fix now that the campaign has landed,
   and still undisclosed in the response letter; see the hazard note above.
4. **`papers/PAPER_REVIEW_PROMPT.md:1774`** --- still names the OLD title as "CURRENT". Low priority.
5. **Freeze inventory** --- `papers/supplementary.tex` is *not* among the fifteen tracked files even
   though `main.tex` is. Its rendered PDF and DOCX are tracked, so the content is hashed, but the
   asymmetry is worth a decision at the next pass rather than a silent change now.

## 4. Decisions already made (do not relitigate)

| Decision | Resolution |
|---|---|
| **New title** | `DT-GSK: Dimension-Tiered Adaptive Configuration Selection and Deterministic Refinement for Gaining-Sharing Knowledge Optimization` — Reviewer 1's own second suggestion. Keeps "Deterministic Refinement" (contribution C1), which both of his proposals dropped. **Applied in Phase 3** across 20 files; the built PDF carries zero occurrences of "Adaptive Control". |
| **"Operator-State Adaptation"** | Declined, with reason: tiering keys on problem dimension, resolved before the run (`_dt_profiles.py:253`), not on operator state. Declining one of two offered options reads as engagement. |
| **R2.6 external baselines** | Take the reviewer's **second limb**: claims stay explicitly GSK-family-only. No external algorithm enters the panel. This requires **zero manuscript edits** — the restriction already exists in six places. Recommended (optional) defusal: one sentence in §S7 disclosing the repository's exploratory SHADE-ILS / MOS / DECC-G LSGO ports. |

## 5. Open decisions — blocking, author only

1. ~~Revision deadline~~ — **no longer gating.** It was never answered, but the ~32,000-run
   experiment track completed anyway on 2026-08-26. Worth confirming before resubmission only so
   the author knows how much slack remains.
2. ~~MT-01 bound wording~~ — **SETTLED and applied.** MT-01 binds the *no-novel-operator* claim, not
   the layer's name; renamed in all three sites with the inheritance clause intact, and the matrix
   `permitted_wording` updated to match.
3. ~~`main.tex:156` "eigenframe refinement"~~ — **RESOLVED by E1 and applied.** The abstract now
   reads "budget-exact final refinement"; zero occurrences of "eigenframe refinement" survive in
   `main.tex` or any section. C1 is basis-neutral throughout.
4. **`PAPER_REVIEW_PROMPT.md:1771`** still names the OLD title as "CURRENT". The live `PROJECT_TITLE`
   field at :1621 *is* updated; :1771 is an audit instruction and remains a false-alarm source for any
   future review run. Low priority.
5. **SuSy portal (author-only)** — the new title and the revised keyword list must be re-entered in the
   revision form. Portal metadata does not update from the PDF.

*Resolved in Phase 3:* keyword drop (done, five places), ACE re-gloss (done, acronym kept),
`related_work.tex:29` heading (done), `citation_usage_map.csv` 30-row rename (done).

## 6. What to do next

**Zero-compute track (start any time, nothing gated on experiments):**

- **Phase 2** — R2.5 + R2.4 body softening. R2.5: insert the non-separation qualifier at
  `performance.tex:9-12`, `conclusions.tex:47-51`, optionally `performance.tex:1193-1199`. The honest
  numbers already exist at `performance.tex:525-532` (Holm 0.0035 / 0.199 / 1.000 / 0.795) and
  `:569-575` ("never Nemenyi-separable at any CEC2017 dimension") — this is a *placement* problem, not a
  new-evidence problem. R2.4: surface the ISM overhead triple **+57.3 % / +36.3 % / +30.3 %** at
  `performance.tex:1073-1076`.
- **Phase 3** — R1.2 title across **32 sites in 15 files** + one 30-row CSV replace-all, and the
  **merged abstract** (R1.1 + R2.4 + R2.5 in ONE edit — see the warning in §7).
- **Phase 4** — R2.6 scope visibility (rides along free inside the Phase 2 edits) + the optional S7
  disclosures + three housekeeping corrections.
- **Phase 5** — single build + validate tail. **Phase 6** — CR-0023, D-0047, re-mint pass-39 / tag v2.14.
- **Phase 7** — rebuttal letter: six complete answers + four placeholders.

**Experiment track (needs the deadline answered first):**

Run order is deliberate — cheapest P0 first, riskiest not last:

| # | Experiment | Runs | Wall-h @15 |
|---|---|---|---|
| E1 | Refinement-basis contrast (only the coordinate arm is new) | 2,958 | 2–3.5 |
| E2 | DT-GSK at NP = 100 | 5,916 | 4–6 |
| E3 | Uniform vs tiered (2 arms) | 11,832 | 8–11 |
| E4 | Parameter sensitivity (26 cells) | 11,310 | 9–12 |

**These experiments can backfire, and the author must accept that before compute is spent.** If DT-GSK's
advantage shrinks at matched NP, or a uniform configuration matches the tiered one, or the eigenframe
matches coordinate axes, the paper's central claims weaken. Pre-commit the null-result wording *before*
running — the project's own pre-registration discipline is otherwise the next reviewer's target.

⚠️ **E1 is expected to return null.** The repo's own config comment at
`configs/_ablation/dtgsk_cec2017_51_no_ism.yml:18` states the ISM "learned basis == coordinate axes to
5e-05, i.e. the estimator carries no information." That measurement has **no backing artifact anywhere** —
its provenance is an open question for the author. If E1 is null, the honest response is to rename
contribution C1 basis-neutral; the Holm-significant polish effect (p = 0.0018 / 0.0052 / 0.0017) survives
regardless, because it is the compass endgame, not the basis.

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
| **Append-only trees** | `papers/build_prompt_phases/`, `papers/review_2026_07_22/`, `papers/governance/remediation_2026_07_18/`. The **old title should remain** in these. |
| **No monospace** | `\texttt` count stays 0 — and `audit_manuscript.py` has **no** `\texttt` gate, so grep separately. Line numbering stays off (`\let\linenumbers\relax`). |
| **Blocked phrases** | "state-of-the-art", "best algorithm" — enforced by `audit_manuscript.py`. |
| **Do not run** | `papers/scripts/finalize_evidence.py` (standing instruction). Drive promotion manually. |
| **Dual-repo hazard** | Work only in `D:/AI/Research-Lab/DT-GSK`. A divergent copy lives in the PhD-Projects monorepo; each freeze manifest hashes only its own tree, so both can report "15/15" while disagreeing. |
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
