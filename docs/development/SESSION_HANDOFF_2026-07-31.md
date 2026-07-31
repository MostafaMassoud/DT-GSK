# DT-GSK — session handoff, 2026-07-31

Written at the end of the session that closed the eight-seat review round and
minted the pass-26 / v2.1 submission freeze. Read this first in any new
session; every fact below was verified against the working trees at the time
of writing, and the "verify on arrival" commands at the end re-check the
load-bearing ones in about a minute.

---

## 1. One-paragraph status

The manuscript is **finished and frozen**, not yet submitted. A five-suite,
seven-algorithm GSK-family study is complete; all evidence is promoted into
immutable releases; the statistics are computed under a pre-registered
analysis plan; an eight-seat expert review panel returned a unanimous MINOR
REVISION and its **entire fix batch has been applied, verified, and
re-frozen**. What remains is publication logistics the author performs by
hand (Zenodo DOI, journal portal upload) plus optional public-repo polish.

---

## 2. Repo topology — read before editing anything

The project now exists in **two unlinked git repositories**:

| | Standalone (this one) | Monorepo (original) |
|---|---|---|
| Path | `D:/AI/Research-Lab/DT-GSK` | `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1` |
| Git root | itself | `D:/AI/PhD-Projects` |
| Remote | `MostafaMassoud/DT-GSK` | `MostafaMassoud/PhD-Projects` |
| History | one squashed commit (`5d5aebc`) | full history, freeze passes 1–26 |
| Tags | none | submission lineage `dtgsk-submission-v2.1-2026-07-31`, v2.0, v1.0, plus `dtgsk-pass-22-2026-07-25` and `dtgsk-pre-remediation-2026-07-18` (10 tags total incl. legacy, all pushed) |

As of this handoff the two `papers/` trees are **content-identical** (recursive
diff clean except `__pycache__`), and both verify `check_manifest` 15/15 at the
pass-26 freeze. They do not sync. A commit in one never reaches the other, and
each freeze manifest hashes only its own copy — so **both can report "15/15"
while disagreeing**. Before any manuscript edit or re-mint, establish which
tree is authoritative for that change. For history, provenance, or "how did we
get here" questions, read the monorepo; its decision log is the record.

---

## 3. The frozen state

- **Freeze**: pass-26, `PASS-26 panel-fix-batch re-freeze (dtgsk-submission-v2.1 basis)`
- **Anchor commit** (monorepo): `afc93d201` — the fix-batch commit
- **Tag target** (monorepo): `878856201` — mint + D-0028
- **Tag**: `dtgsk-submission-v2.1-2026-07-31` (monorepo only; v2.0 and v1.0
  retained and unmoved)
- `check_manifest` 15/15, verified twice; the manifest tracks `main.tex`, the
  five section files, four rendered artifacts, the cover letter PDF, three
  governance CSVs, and `references.bib`. **`supplementary.tex` is deliberately
  outside the manifest's source scope** (only its rendered PDF/DOCX are frozen)
  — that is by design since pass 1; do not "fix" it.

### Evidence releases (immutable — never re-run, never re-mint)

| Release | Scope | Files |
|---|---|---|
| `rel-2026-07-20-67d9345f9` | CEC2017, CEC2011, CEC2013 (primary) | 3,403 |
| `lsgo-rel-2026-07-28-ff1a046ef` | CEC2013LSGO | 173 |
| `cec2020-rel-2026-07-29-5867abe1e` | CEC2020 | 336 |
| `abl-rel-2026-07-20` | component ablation (S6) | 1,297 |

### Binding standings — never restate these from memory, check the CSVs

| Suite | Standing (of 7) | Mean rank |
|---|---|---|
| CEC2017 (primary, selection-exposed) | first | 2.48 |
| CEC2013 (corroborative) | first overall | 2.80 |
| CEC2013LSGO (post-hoc, family-internal) | tied-first with AGSK, no paired separation | 3.133 |
| CEC2011 (corroborative, real-world) | second behind eGSK, Holm-significant loss | 3.36 |
| CEC2020 (pre-registered confirmatory) | fourth; AGSK first at 2.0875 | 4.1125 |

Registered recount sentence: *first on two, tied-first on one, second on one,
and fourth on one* of the five suites' descriptive family-rank aggregates.

### Amendment 3 — the wording correction that must not regress

The pre-registered wording bank originally claimed **AGSK won the CEC2020
competition**. That is false: AGSK was the **runner-up**; IMODE won
(source: `apgsk2021`, IEEE Access 9, p. 65936 — a co-author's own paper, cited
in the manuscript). Amendment 3 (dated, append-only, at
`papers/build_prompt_phases/phase_05/statistical_analysis_plan_addendum_cec2020_lsgo_amendment_03.md`)
corrects it. The corrected `[AGSK first]` sentence is now the binding verbatim
and appears identically at four loci (abstract, §4.5, conclusions, S8) with
`\cite{apgsk2021}` attached everywhere **except** the abstract. If any future
edit reintroduces "it won" at those four compiled loci or in
`cover_letter.tex`, it is a factual error, not a style choice.

**But the false wording deliberately survives elsewhere and must NOT be
"fixed".** A repo-wide grep will hit
`papers/build_prompt_phases/phase_05/S8_cec2020_supplement_skeleton.tex`
(lines 49, 66 — an uncompiled skeleton, never `\input`), the original addendum
(3 hits), and Amendments 1–2 (6 and 2 hits). Those hits are **expected**:
Amendment 3 §A3.4 states that prior text "is NOT edited in place" and that the
amendment "is the sole authority for the corrected wording". Editing them
would void the append-only pre-registration — a hard constraint in §6.

---

## 4. What the last session did (for context, not to redo)

1. Removed affiliations 2 and 3 at the author's direction → pass-25, tag v2.0.
2. Ran an eight-seat review panel over the whole manuscript → register at
   `papers/governance/panel_review_register_2026-07-31.md` (unanimous MINOR
   REVISION; 2 BLOCKING, 3 MAJOR, 18 minor, 9 enhancements, 6 repo updates).
3. Applied the batch **in full** on the author's "fix all": Amendment 3;
   S5.4's stale "evidence ceiling is D=100" replaced with per-suite ceilings;
   cover-letter Nemenyi claim re-fenced to CEC2017; S5.10 three-release
   provenance; S5.3 five-suite selection disclosure; ~30 minor repairs; all
   nine enhancements.
4. Filed CR-0021 (page/word caps re-set to 44 pp / 24,000), refreshed the
   runbook and ablation README, regenerated the environment attestation
   (green, 603 tests ×2).
5. Fixed a **latent gate defect**: full-mode `validate_build_hygiene.py` had
   been failing since the W1–W3 surgery on the legitimate D-0025 phrase
   "author-code oracle", masked because every flow ran `--logs-only`.
6. Rebuilt all five artifacts ×2 at pinned epochs, ran the full gate battery,
   ran a four-lens adversarial verification workflow (4/4 PASS), minted
   pass-26, filed D-0028, tagged v2.1.

No number, rank, p-value, effect size, or registered standing changed in any
of it — the whole batch was textual.

---

## 5. Remaining work

| # | Item | Owner | Notes |
|---|---|---|---|
| 1 | Confirm the GitHub repo's visibility | author | Must be **public** before Zenodo can archive it |
| 2 | Turn the **Zenodo toggle ON** | author | Must happen *before* the release is created, or no DOI is minted |
| 3 | Create the GitHub Release | author | From this repo at the v2.1 content state |
| 4 | Capture the Zenodo DOI | author | — |
| 5 | SuSy submission (MDPI *Algorithms*) | author | Upload the **committed** artifacts: `papers/DT-GSK.pdf`, `DT-GSK.docx`, `supplementary.pdf`, `supplementary.docx`, `cover_letter.pdf`. Repo URL + DOI go in the portal fields — the Data Availability Statement deliberately prints neither, so **no rebuild is needed**. Personal address/phone go in the portal only, never in repo files. |
| 6 | Optional: tag this standalone repo | either | It has no tags; a `v2.1` tag here would make the Release point at a named state |
| 7 | Optional: public-facing `README.md` + `CITATION.cff` | Claude, on request | Both are stale for a public audience: the README opens with internal workspace/agent instructions and pre-rename naming; CITATION.cff says "GSK Family Python v0.1.0", lists one author, and marks the paper "forthcoming" with no venue |
| 8 | Optional: repo hygiene | Claude, on request | `results/` has 1,363 tracked files totalling **~1.51 GB** in the working tree, of which 522 convergence-curve CSVs account for ~1.50 GB (largest single file 18.8 MB); `.git` is only 281 MB because dense numeric CSVs compress ~5×, so size any cleanup on the working tree, not on `.git`. The curves are excluded from every release manifest by design (`FINAL_PUBLICATION_PLAN.md` ruling A-11) and are the only genuinely prunable mass. **Hard exclusion — never delete or untrack:** `results/_run_all/{shade-ils,mos-cec2013lsgo,decc-g}/cec2013lsgo/` (144 tracked files) are the native external-baseline banks, deliberately unpromoted but deliberately public per `FINAL_PUBLICATION_PLAN.md` §2.8 ruling (b) ("removing public unfavorable data is the one move worse than either alternative"); `_external_baselines/` holds only transcribed summary tables, and the shipped Data Availability Statement advertises these banks by name. Only the *promoted* family evidence is duplicated in `benchmarks/cec_reference_results/` and `papers/analysis/`. Confirmed safe: `reference_papers/` tracks only 3 text files — the third-party PDFs are gitignored, so there is **no copyright exposure** in what was pushed |
| 9 | Post-submission research: **A-2** | later | Close the CEC2011 gap to eGSK — the one Holm-significant loss. Lead: the frozen candidate-A survivor (opt-in `ism_profile`) needing wider-panel runs. Must not touch the frozen releases, registered outcomes, or this submission. Filed in the panel register's addendum |
| 10 | Close the stale **CR-0020** row in `papers/governance/change_request_register.csv` | Claude, on request | The only non-APPROVED row of 21 still reads `OPEN 2026-07-28`, but its closure criteria are met: all four keys are in `allowed_citation_keys.txt` (61 keys), `validate_citation_controls.py` reports `PASS: C1-C5 hold`, and `_pending_refreeze.json` P0-CITATIONS is DONE. Status-only edit — but the register ships inside the DOI-archived record, so it should not go out reading OPEN |
| 11 | **D-WORD-01 visual-confirmation checklist** (author-side) | author | Still open: on re-opening the DOCX in Word, confirm fields, TOC/SEQ/REF/CITATION rendering, and landscape sections (`papers/governance/word_validation_report.md` §1 and §9.5). Inspect only — the file that ships is the deterministic build (see §6) |

---

## 6. Hard constraints (violating any of these breaks the submission)

- **Frozen releases are never re-run or re-minted.** Do not run
  `papers/scripts/finalize_evidence.py` end-to-end (P2/P6 are guarded behind
  `GSK_ALLOW_PRIMARY_REMINT=1` for this reason).
- **The pre-registration is append-only.** Corrections are new dated
  amendments (now up to Amendment 3); silent edits void it.
- **Build epochs are pinned**: PDFs at `SOURCE_DATE_EPOCH=1783468800` with
  `FORCE_SOURCE_DATE=1`; DOCX at `1783641600` set **explicitly** — a persisted
  shell variable silently yields a non-reproducible DOCX that still passes
  `check_manifest`. Always build ×2 and byte-compare.
- **Author LaTeX and regex with Write/Edit, never a heredoc.** Heredocs
  collapse `\\` → `\`, which once shipped literal "oindent"/"imes" into the PDF.
- **Never ship a Word-resaved DOCX.** The committed and uploaded bytes must
  always be the deterministic `build_docx.py` output — Word rewrites the
  package on save, so a re-saved file is a compatibility probe, never the
  deliverable. Note D-WORD-01 is *not* a prohibition on opening the file: it
  is the **prescribed** desktop-Word open-save-open compatibility check, a
  documented Gate-9 exception because Word was unavailable in the build
  environment. The author ran it on 2026-07-23 and the DOCX was regenerated
  afterwards. Its residual visual-confirmation checklist is still open (row 11
  of §5).
- **No `\texttt`** anywhere in the manuscript; line numbering stays disabled.
- **Run hygiene in full mode**, not `--logs-only` — that is exactly how a
  real failure hid for several passes.
- **The user runs campaigns and pushes.** Do not push, and do not launch
  long compute, without being asked.
- Any manuscript edit voids pass-26 → requires a pass-27 re-mint plus a **new**
  superseding tag (keep earlier tags in place).

---

## 7. Verify state on arrival

```bash
cd D:/AI/Research-Lab/DT-GSK
python papers/scripts/check_manifest.py --manifest papers/governance/main_manuscript_freeze_manifest.json
python papers/scripts/validate_provenance_claims.py
python papers/scripts/validate_cross_format_parity.py
python papers/scripts/validate_document_consistency.py
git status -sb && git log --oneline -3
```

Expected: `15/15 match`, `[provenance] OK`, `TOTAL rows=724 FAIL=0`,
`[doc-consistency] OK` (all four exit 0), and `## main...origin/main` with no
tracked modifications. `git status -sb` shows exactly one extra line —
`?? docs/development/SESSION_HANDOFF_2026-07-31.md`, this file, untracked and
present only in the standalone repo; that is expected, not post-freeze drift.
`git log --oneline -3` prints a single line (`5d5aebc DT-GSK`) because the
repo has exactly one commit.

Key files to read for orientation:

- `papers/governance/panel_review_register_2026-07-31.md` — the review round
  and its addendum (A-1 structural low-D limitation, A-2 the CEC2011 objective)
- `papers/governance/decision_log.md` — tail entries D-0026, D-0027, D-0028
- `papers/governance/main_manuscript_freeze_manifest.json` — the pass-26 freeze
  statement. Note it is a *fresh mint*: it opens at the 2026-07-22 review pass
  and chronicles only that chain forward (earlier statements were replaced, not
  appended). For anything before 2026-07-22, use the monorepo's git history of
  this same path plus `decision_log.md`
- `papers/PAPER_REVIEW_PROMPT.md` — layer 1.5.0-P carries the current binding
  wording and pins
- `docs/development/FINAL_PUBLICATION_PLAN.md` — the phased plan this work
  executed

---

## 8. Where the algorithm actually stands

Useful when writing or defending any claim: DT-GSK is the strongest
general-purpose member of its family, but its strength is **dimension-tiered
and family-internal**, and it is **not monotone in dimension** — do not say
"its advantage grows with dimension".

It is top-two on four of five suites, and its per-dimension standing is first
at every tier **except D=30**, which is its weak tier on both general suites:

| | D=10 | D=30 | D=50 | D=100 |
|---|---|---|---|---|
| CEC2017 | first (2.879) | **second** — eGSK 2.293, DT-GSK 2.500 | first (2.207) | first (2.345) |
| CEC2013 | first (2.411) | **third** — eGSK 3.071, ATMALS 3.339, DT-GSK 3.375 | first (2.607) | — |

The shipped manuscript says exactly this (`main.tex` abstract: "second behind
eGSK at $D = 30$"; `conclusions.tex`: "first/third/first --- third at $D = 30$").
There is a **second**, separate weak regime: below D≈20 every dimension-gated
subsystem is structurally off and DT-GSK runs as base machinery — hence fourth
on CEC2020, which the pre-registration predicted in advance as a boundary
condition. At D=1000 it is tied-first with AGSK; the only Nemenyi separation
on that suite is against eGSK (gap 2.3333 > CD 2.3262 — AGSK, tied, separates
identically), while the paired Wilcoxon separates **no** comparator at all
(all six Holm outcomes are ties). Never cite the Nemenyi separation as if the
paired layer supported it.

All standings are family-internal: on LSGO, MOS beats all six GSK *baselines*
on 9 of 12 objective-comparable functions — against the full seven-member panel
the figure is 8 of 12, because DT-GSK itself beats MOS on F5, F8 and F9
(F3/F6/F10 are excluded: the family ran the transformed Ackley, MOS's published
table the raw form). That count lives only in
`docs/development/LSGO_INTEGRATION_CAMPAIGN.md`; no external appears as a
comparator anywhere in the manuscript, which states only that MOS and SHADE-ILS
report substantially stronger published results and claims no competitiveness
with such specialists. CEC2020's real champions (IMODE first, AGSK runner-up)
likewise sit outside the panel. The paper claims neither more nor less than
this, which is why the panel found no defect in any standing.
