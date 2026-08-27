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

**Pass-44 is applied, minted, tagged and pushed.** `origin/main` carries it, **`v2.17` is live**,
and `v2.13` through `v2.17` all resolve — the Data Availability Statement names `v2.17` for the
revised version, and `main.tex` was edited to say so in the same pass. **Pass-44 carried the last
three optional wording items and the open list is now empty of agent work** — what remains is the
author's alone (D-0052). **Every tag bump drags
`CITATION.cff`, `SUBMISSION_KIT.md` and `submission_package_manifest.json` with it**; the citation
file is gated and carries no leading `v`, so a `v2.1x` sweep misses it.

**Work on `main`.** It tracks origin. The development history lives on
`archive/revision-pass-39-full` and **must never be pushed**: some of its commit messages gender an
anonymous reviewer, and its intermediate trees carry the reviewers' reports, the co-author handoff
and the seven copyrighted PDFs. `revision/pass-39` carries the reports too. **Never merge either
into `main`** — `main` is the published line and is clean; `public/squash-candidate` holds nothing
that is not already on `main`.

**What pass-42 did.** Twelve alleged defects were verified and then challenged in the opposite
direction; nine survived and are corrected (C1, C2, C3, C6, C7, C8+C9 merged, C10, C11, C12).
**C4 is refuted and deliberately not edited** — its proposed "fix" was a regression.
**Contribution C3 is NOT narrowed.** No number, rank, p-value or decision changed. Freeze pass-42,
CR-0025 / D-0050, `check_manifest` 15/15, thirteen gates green, all five artifacts byte-reproducible.

**The lesson that generalises:** the diagnoses were reliable, the prescriptions were not — 10 of 11
audited fixes were unsafe as written and had to be repaired before use. **Challenge a proposed fix,
not just the finding.** And read the built PDF: every defect this project has shipped was caught
there and nowhere else.

**The two author decisions that were open are now RESOLVED (pass-43, D-0051).**

1. The Supplementary no longer contradicts the response letter. The letter concedes the D = 100
   internal control does not hold; `supplementary.tex` had still asserted that no reported number
   depends on which revision is used. Both ship in one package, so both would have reached the
   referees. The exception is now recorded, pointed at the caption that already reports it as
   unresolved, and bounded — the archived release every reported number derives from is unchanged.
2. **A larger disclosure was drafted and REJECTED on challenge. Do not revive it.** It would have
   named CR-0015 as the one bit-identity certification not spanning cec2017 D = 100 — refutable
   from the register it cites, since **CR-0014, CR-0016 and CR-0018 all certify that cell**, the
   last in an 84-cell bit-for-bit ledger. It also named a cause while disclaiming one, and located
   it at contribution **C1**. **The standing rule holds: state the gap, never the causation.**

**ANSWERED 2026-08-27 by re-execution (D-0051): the residual is a BUILD difference, demonstrated.**
The five functions carrying it were re-run at CEC2017 D = 100, 51 runs each, under the current build
with threads pinned as the campaign driver pins them. 255 cells, zero seed mismatches. **On the 26
cells where the archive and the transplant arm differ, the fresh run reproduces the transplant arm
on all 26 and the archive on none; on the 229 where they agree it reproduces both.** So the current
build makes the transplant arm's values and the archive is what the earlier build made — between
builds, not within one.

**Two traps this experiment sets for anyone repeating it.** `run.py` does **not** pin threads (only
`run_campaign.py` does) and D = 100 is thread-sensitive, so an unpinned re-run is meaningless. And a
control drawn from cells where the two legs already *agree* cannot distinguish the builds — an early
reading here went wrong exactly that way; the discriminating cells are the ones that differ.

**No manuscript change follows.** The Supplementary already says the control re-executes archived
runs and does not reproduce them exactly, and the caption reports the residual as unresolved *in the
paper*; both stay true and are now evidenced. Claiming more would mean **promoting a diagnostic
staging run as cited evidence** — new release id, manifest, binding — since every reported number is
bound to a promoted release. That option is the author's and is not taken. Still recorded, and still
true: the campaign's identity evidence samples ~one run per (algorithm, suite, dimension), so a
27-in-1479 divergence sits below its resolution — those certifications are underpowered here, not
wrong.

**The hashed-render / unhashed-source blind spot is now gated.** The freeze hashed renders but only
`main.tex` among their sources, which is how pass-42 edited `cover_letter.tex`, skipped the rebuild,
and left the render matching its digest while the gate stayed green — on a letter that ships to the
editor. The manifest now carries `source_files` and `check_manifest` reports
`sources N/N` on its own line, so every recorded "15/15" stays true. Negative-tested: perturb a
source, leave its render, and `files` still reads 15/15 while `sources` drops and the gate exits 1.

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
