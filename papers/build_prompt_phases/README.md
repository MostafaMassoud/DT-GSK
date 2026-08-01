# Manuscript production instructions — phase files

**These files are the authors' own production instrumentation: the written
procedure the manuscript was built under. They are not part of the submission,
they are not results, and nothing in them was used to produce, select, or alter
a number reported in the paper.**

## What this directory is

[`papers/PAPER_BUILD_PROMPT.md`](../PAPER_BUILD_PROMPT.md) is the master
specification for producing the manuscript. It is long, so each of its phases is
expanded here into an executable procedure — what that phase may touch, what it
must not, what it hands to the next phase, and the gate it has to pass before
the project moves on. The `PHASE_N_*.md` files are those instructions; the
numbered `phase_NN/` subdirectories are the corresponding *outputs* (gate
reports, registries, notation and parameter tables, pre-registration documents,
review records).

The work was carried out with AI assistance, so these instructions read as
prompts. The manuscript's *Use of Generative Artificial Intelligence* statement
is the authoritative disclosure of that use; the top-level
[`README.md`](../../README.md) section "Internal Quality-Assurance Instruments"
gives the fuller framing, including which parts of the project AI touched and
which it did not.

The boundary that matters is recorded in the history rather than asserted here,
and it is checkable with `git log`: of the AI-assisted commits in this
repository, none modifies `benchmarks/cec_reference_results/` or
`papers/analysis/` — the frozen evidence and the analysis outputs the paper's
numbers come from. Two touch optimizer source, and both are comment-only: one
repoints a documentation cross-reference, the other adds a citation docstring.
Neither changes an executable line. Experiments were designed, executed, and
frozen before the manuscript-production phases in this directory began, and
every phase terminates in an author-gated freeze.

Several `phase_NN/` outputs are load-bearing for the paper and are not merely
historical: `phase_03/` supplies seven `.tex` files that the manuscript
`\input`s directly (notation and parameter tables, the equation set, the
algorithm pseudocode), and `phase_05/` holds the statistical pre-registration
that the manuscript cites throughout.

## Renamed files

Two files were renamed on 2026-08-01 because their names carried framing this
project's own governance had already revoked, and a directory listing is the
first thing a reader sees:

| Current name | Former name | Why |
|---|---|---|
| `PHASE_6_prose_quality.md` | `PHASE_6_humanization.md` | The document was written as a "Humanization Pass" with detector-oriented framing. That framing was revoked before submission under [`PAPER_BUILD_PROMPT.md`](../PAPER_BUILD_PROMPT.md) §0.3 ("Wording intended to evade AI-text detectors is prohibited"), logged as conflict **C-07** in [`instruction_precedence.md`](../governance/instruction_precedence.md). The file now opens with a SUPERSEDED banner and the revoked sentences are struck but quoted in place. |
| `EXECUTION_SEQUENCING_PLAN.md` | `AUTONOMOUS_EXECUTION_PLAN.md` | "Autonomous" meant proceeding through production phases without pausing for approval at each step. It never described the science, but the old name invited that reading. |

Git history preserves both original names and every prior revision; the renames
are recorded as decision **D-0033** in
[`decision_log.md`](../governance/decision_log.md). Documents dated before
2026-08-01 — the review records under `phase_12/` and
[`papers/review_2026_07_22/`](../review_2026_07_22/) — still cite the old names,
which is correct for their date and was left alone deliberately.

## Reading these files

They are historical instructions, and several are superseded. Where an
instruction here conflicts with the master prompt, the master wins: the full
conflict table, with the ruling on each, is
[`papers/governance/instruction_precedence.md`](../governance/instruction_precedence.md).
Do not read any file here as a live directive without checking that table first.
