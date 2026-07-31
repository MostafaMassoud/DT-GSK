# CEC2017-PREC — adjudication (CLOSED 2026-07-25)

**Ticket.** During the BUG-RESUME-01 work (2026-07-25) a spot probe found frozen
CEC2017 summary CSVs whose values disagreed with a full-precision recompute from
the release's own `per_run.csv` at around the 9th–10th significant digit. The
flag was carried as "3 frozen cec2017 summaries, root cause unknown, author
decision needed".

**Correction of the original flag.** The "3 files" count was an artifact of the
spot probe's scope. A systematic sweep of the *entire* frozen CEC2017 evidence
(release `rel-2026-07-20-67d9345f9`, all 7 algorithms x 4 dimensions = 28
summary files, 812 function cells, 4,060 fields) finds **340 mismatched fields
spread across all 28 files**. Every one of the 340 falls into one of three
signatures; none is unexplained.

## Method

For every `(algorithm, dimension, function)` cell, recompute
Best/Median/Mean/Worst/SD from the release's own `per_run.csv` (error basis,
n=51, `statistics.stdev`, `math.fsum` mean), format with the summary writer's
`%.10E`, and compare textually against the frozen summary row. Classify every
mismatch; require zero unclassified.

## Result — three signatures, all release-serialization properties

| Class | Count | Max rel. delta | What it is | Which side is more precise |
|---|---|---|---|---|
| A | 8 | (SD ~1e-13 vs 0) | Frozen SD is the full-precision floating-point residue of 51 near-identical values; `per_run.csv` serializes all 51 as the *same* text, so a recompute collapses SD to exactly 0 | **Frozen** |
| B | 294 | 3.9e-10 | Frozen stats were computed from full-precision in-memory float64 and printed `%.10E`; `per_run.csv` stores `%.10e` (11 sig digits), so recomputation from it necessarily drifts in the 10th–11th significant digit | **Frozen** |
| C | 38 | 1.1e-06 | Frozen Best/Median/Worst cells at small magnitudes (~1e-7..1e-8) carry exactly-6-significant-digit values with trailing zeros (e.g. `1.8957600000E-08` vs per_run `1.8957621251e-08`); a formatting property of the original release writer for these cells, origin predating this project's audits | per_run |
| unclassified | **0** | — | — | — |

Class A and the Class-C signature were both independently documented by the
Phase 6 source-and-schema audit
(`papers/build_prompt_phases/phase_06/source_and_schema_audit.md`, Category 4)
on the predecessor release `rel-2026-07-10-262fc16c9`, with the same
adjudication: a storage-precision property of the release files themselves,
"below the %.6e reporting precision", "0 substantive discrepancies". This sweep
extends that adjudication to the current release with full coverage.

## Impact on reported values — zero, by three independent barriers

1. **Statistics never touch the summaries.** Every rank, Wilcoxon/Holm p-value,
   Friedman rank, and effect size is computed from run-level `per_run.csv`
   (Phase 6 audited the denominators and sources); summary rounding cannot
   reach them.
2. **Rendered precision is 3 significant digits.** The supplement panel tables
   (`papers/tables/T*.tex`) print `X.YZE+NN` Mean±SD cells. The worst
   discrepancy in any class is in the 7th significant digit — three orders of
   magnitude below rendered precision.
3. **Machine-checked parity.** The cross-format parity gate (599 rows, 0 FAIL)
   verifies rendered values against their CSV sources on every sweep.

## Decision

**The frozen bytes stand.** In Classes A and B the frozen values are the *more*
accurate side, and "correcting" them toward a per_run recompute would make the
release strictly worse while breaking every file hash. In Class C the frozen
value is the less precise side, but it is the immutable source of record, the
loss is invisible at 300x the rendered precision, and the property was already
disclosed by the Phase 6 audit. No file is changed, no hash is re-minted, no
rerun is needed, and no manuscript text is affected.

**CEC2017-PREC is CLOSED as adjudicated-benign.**
