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
| Decisions D-0001…D-0048 | `papers/governance/decision_log.md` |
| Claim → evidence bindings | `papers/governance/claims_evidence_matrix.csv` |

⚠️ **[FINAL_RELEASE_REPORT.md](FINAL_RELEASE_REPORT.md) is historical** (CEC2017 only, pre-submission).
It ends on "PUBLISH READY", which is no longer the project's state. Do not read it for current status.

## Conventions

- Freeze passes and tags advance together: submitted at **pass-38 / v2.13**; the round-1 revision
  landed at **pass-40 / v2.14**. That tag is cut but **local and unpushed** — `origin/main` still
  carries the submitted state and the remote tags stop at `v2.13`.
- Governance ids are sequential and must be verified free at apply time — next are **CR-0025** and
  **D-0049**.
- Evidence releases are additive and non-superseding. Frozen analysis outputs are never re-minted;
  new findings get a new release id.
- Temporary files go in the session scratchpad, **outside** the repo. Never create scratch trees,
  plan folders, or agent scaffolding directories anywhere under this root.
