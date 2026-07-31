# External baseline tables — out of paper scope, no in-repo validation

Status: these tables support no claim, panel, figure, or statistic in the
DT-GSK manuscript. The paper's analyzed scope is the seven GSK-family
algorithms only (CR-0019, author decision 2026-07-27/28); the external
optimizers remain in the repository as runnable tooling with no validation
evidence reproducible here — six of the eight vendored ports carry their
author-code parity records only in the sibling project, and DECC-G is
first-party code written from its source paper with no author-code oracle.
These imported summary tables remain here as context. **No comparability
audit against the family is claimed for them.**

Why they live under an underscore tree: the plain
`cec2013lsgo/` name inside this evidence root is reserved for the promoted
seven-algorithm family release; these tables previously sat there unlisted by
any manifest, which is exactly the state `check_manifest --strict-inventory`
exists to prevent. Each subdirectory carries a `provenance.json` sidecar
(import history, checksum, related publication, and comparability caveats).

Two caveats bind every use of these numbers:

1. **Objective-variant mismatch (F3/F6/F10).** The family's CEC2013LSGO banks
   ran the TRANSFORMED Ackley chain. Published MOS results were measured on the
   raw `benchmark_func.m` form, so on F3/F6/F10 the MOS column is a different
   objective function, not a performance comparison. SHADE-ILS used the
   transformed package form and is variant-comparable on all 15 functions.
2. **Unverified transcriptions.** These are summary-only imports (3–4
   significant figures, no per-run data, no environment records). The
   transcriptions have not been re-verified against the source tables inside
   this repository; `papers/governance/data_ledger.csv` carries them as
   context-only and inadmissible for any panel.
