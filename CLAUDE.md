# CLAUDE.md

Auto-loaded every session, so it is deliberately short. It carries only what a session cannot
cheaply re-derive, and points at the one file the task actually needs. **Do not read the root
documents speculatively** — they total ~300 KB.

## What this repo is

DT-GSK (Dimension-Tiered Gaining-Sharing Knowledge): a single-algorithm research repo built around
one manuscript. Seven optimizers behind one contract — `gsk`, `agsk`, `apgsk`, `fdb-agsk`,
`atmals-gsk`, `egsk`, and the proposed `dt-gsk` — evaluated on five CEC suites (`cec2011`,
`cec2013`, `cec2013lsgo`, `cec2017`, `cec2020`) under one locked, budget-fair paired protocol.
Python package: `gsk_family` (under `src/`). Console entry points are `gsk-*`.

The repository exists to support a **published claim**, not to be a general framework. Most files
are frozen or hash-bound. Assume nothing is casually editable.

## Right now (2026-08-27)

The round-1 revision is **done and published**. `origin/main` carries it, `v2.14` is pushed, and
`v2.13` still resolves — so both tags the Data Availability Statement names are live.

**Work on `main`.** It tracks origin. The development history lives on
`archive/revision-pass-39-full` and **must never be pushed**: some of its commit messages gender an
anonymous reviewer, and its intermediate trees carry the reviewers' reports.

**A pass-42 is owed against the published paper, and the fix list is now adjudicated.** Twelve
alleged defects were verified independently and then challenged in the opposite direction. **Six
need an edit** (C1, C2, C3, C6, C8+C9 merged, C10), **two are refuted** (C4, C11 — C4's proposed
"fix" is a regression; do not apply it), and three are optional wording (C5, C7, C12). The anchor
defect: Table A45's caption says the two identity controls are confirmed by their tie counts, but
the D = 100 control prints 2/25/2, and 27 of 1479 run cells differ by up to 5.3 % relative under an
identical configuration, environment and budget.

**"Published" here means the public repository, not the journal.** The round-1 revision has **not**
been resubmitted through SuSy, and the Preprints.org posting was withdrawn the same day (D-0046).
So these six edits can still land in the version the reviewers will read, as an ordinary pass-42.
That window closes the moment the author resubmits, after which the same edits become a correction
to a manuscript already under the editor's eye. **Fix before resubmitting.**

**All twelve are now verified and adversarially challenged, and there is a written work order.**
[REVISION_STATUS.md](REVISION_STATUS.md) **§2b** carries edits E1–E12 with every FROM anchor
verified byte-exact and unique. Three things must survive into the next session:

1. **The work order covers C6–C12 only.** C1 (the anchor caption defect), C2 and C3 have no
   specified edits, and C1 waits on an author decision. Do not read §2b as complete.
2. **The diagnoses held; the prescriptions did not.** 7 of 7 challenged verdicts survived, but
   **7 of 7 proposed fixes were rejected as written** — several would have made the paper worse.
   Treat any un-audited draft fix as a first draft, C2's and C3's included.
3. **`main_pandoc.tex` and `supplementary_pandoc.tex` are GENERATED shims**, overwritten by
   `build_docx.py` on every run. Never hand-edit them — the edit is clobbered and reads as done.
   Edit canonical sources and rebuild. (An earlier version of this file said the opposite and
   reached `origin/main`; it is corrected in §2a.)

**Author-only, still outstanding:** the SuSy resubmission; a GitHub Support ticket to
garbage-collect commit `b9846e4` (seven copyrighted PDFs are off every ref but still served by
direct SHA — verified HTTP 206); GitHub Insights → Traffic → Clones, which expires on a 14-day
window; and telling the co-authors their biographies were public for twenty days.

## Read this first

**➡ [REVISION_STATUS.md](REVISION_STATUS.md) — current state, always.** The manuscript is under
**major revision** at *Algorithms* (MDPI) — the round-1 revision is complete and awaits author
resubmission. That file holds the review outcome, how each of the ten reviewer points was answered,
what each revision phase applied, the decisions already made, the open author decisions, and the
full trap table. Start there; it exists so you do not have to read the decision log end to end.

**Two submitted claims were falsified by the round-1 experiments and corrected in the paper.** The
learned ISM eigenbasis is *harmful*, not neutral — plain coordinate axes beat it at D = 50 — so C1
is renamed "a deterministic final polish" and claimed basis-neutrally. The polish itself survives: it
still beats no refinement at both active dimensions. And the 20 ≤ D < 50 tier is *mis-specified*, so
C2 is narrowed to the dimensions where tiering was shown, D = 10 and D = 50. Describing the mechanism
as computing an eigenbasis is still correct; presenting the eigenbasis as a contribution or a benefit
is not. Details: [REVISION_STATUS.md](REVISION_STATUS.md) §3, Phase 7.

Everything else in this file is a pointer.

## Never break these

1. **Four shipped DT-GSK modules are hash-gated**, not just one: `dt_gsk.py`, `_dt_core.py`,
   `_dt_profiles.py`, `_dt_rng.py` under `src/gsk_family/optimizers/`.
   `papers/scripts/validate_provenance_claims.py` hashes them on a SHIPPED list — **even a comment
   edit fails the gate.**
2. **`benchmarks/cec_reference_results/` is READ-ONLY** frozen evidence. Never "regenerate" it.
   Runners write under `results/` and nowhere else — `_run_all/` for the campaign, `_revision/` for
   the revision driver (`scripts/run_revision_experiments.py`), `_ablation*/` for ablations.
   `results/_revision/` is **untracked** (D-0049): it duplicates the promoted release, which is the
   citable evidence.
3. **`papers/` is a frozen manuscript under change control.** Any edit voids the freeze manifest and
   belongs to a new freeze pass (see D-0045). Never edit the submitted state in place.
4. **Never author LaTeX or regex through a bash heredoc** — backslash collapse has already shipped
   corrupted macros into a released PDF. Use exact-match file editing.
5. **Line endings are per file**, and multi-line edits fail silently against the wrong one. Both
   freeze manifests and several `.tex` files are CRLF; others are LF. Check before editing.
6. **Append-only trees:** `papers/build_prompt_phases/`, `papers/review_2026_07_22/`,
   `papers/governance/remediation_2026_07_18/`. Stale content there is correct — do not "fix" it.
7. **Never run `papers/scripts/finalize_evidence.py`** (standing instruction).
8. **Work only in `D:/AI/Research-Lab/DT-GSK`.** A divergent copy lives in the PhD-Projects monorepo;
   each freeze manifest hashes only its own tree, so both can report "15/15" while disagreeing.
9. **The repository is PUBLIC and some files are deliberately untracked** (D-0049). Pinned in
   `.gitignore`, present on disk, retained in git only on the never-pushed archive branch: both
   reviewers' reports, the point-by-point response (it quotes them), the co-author handoff
   (biographies marked as awaiting their subjects' approval), and seven copyrighted third-party
   PDFs. The **pre-registration is public on purpose** — the Supplementary Materials' claim that
   adverse-outcome wording predates the outcomes is uncheckable without it. Do not re-add any of
   the others, and never push a branch whose history contains them.
10. **A `.gitignore` glob that does not cross `/` is not an exclusion.** `reference_papers/*.pdf`
   silently matched nothing under `Academic_Research_Guidelines/` for the life of the repo, and
   38.8 MiB of copyrighted PDFs reached the public remote. Recursive form alongside it now; check
   `git check-ignore -v <path>` rather than trusting the pattern.

Full detail and the remaining traps: [REVISION_STATUS.md](REVISION_STATUS.md) §7.

## Where detail lives

| Need | File |
|---|---|
| **Current state, review, next steps** | **[REVISION_STATUS.md](REVISION_STATUS.md)** |
| Orientation, directory tree | [REPO_MAP.md](REPO_MAP.md) |
| Agent operating contract, commands | [SKILL.md](SKILL.md) |
| Step-by-step procedures | [runbook.md](runbook.md) |
| Project constitution, governance | [PROJECT_RULES.md](PROJECT_RULES.md) |
| Module structure, data flow | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Design principles, how to extend | [DESIGN_GUIDE.md](DESIGN_GUIDE.md) |
| Suite protocols, budgets, seeds | [BENCHMARK_RULES.md](BENCHMARK_RULES.md) |
| Style, determinism, KATs | [CODING_STANDARD.md](CODING_STANDARD.md) |
| Numba, threading, serial kernels | [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md) |
| Runtime-acceleration method | `docs/development/ACCELERATION_CAMPAIGN_PROMPT.md` (Appendix A) |
| Decisions D-0001…D-0049 | `papers/governance/decision_log.md` |
| What is published vs withheld, and why | `papers/governance/decision_log.md` **D-0049** |
| Claim → evidence bindings | `papers/governance/claims_evidence_matrix.csv` |

⚠️ **[FINAL_RELEASE_REPORT.md](FINAL_RELEASE_REPORT.md) is historical** (CEC2017 only, pre-submission).
It ends on "PUBLISH READY", which is no longer the project's state. Do not read it for current status.

## Conventions

- Freeze passes and tags advance together: submitted at **pass-38 / v2.13**; the round-1 revision
  landed at **pass-41 / v2.14**, both **published**. A revision is always a new pass through change
  control, never an edit to a tagged state (D-0045).
- **Publication is a squash.** The public history is one commit per published state, because the
  development history cannot be published. So a commit SHA recorded by a governance record —
  including `anchor_commit` in the freeze manifest — does **not** resolve in the public history.
  `published_commit` sits alongside it and does. This is disclosed in `README.md`.
- Governance ids are sequential and must be verified free at apply time — next are **CR-0025** and
  **D-0050**.
- Evidence releases are additive and non-superseding. Frozen analysis outputs are never re-minted;
  new findings get a new release id.
- Temporary files go in the session scratchpad, **outside** the repo. Never create scratch trees,
  plan folders, or agent scaffolding directories anywhere under this root.
