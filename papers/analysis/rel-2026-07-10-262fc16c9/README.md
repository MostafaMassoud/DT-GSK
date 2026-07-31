# Controlled analysis bundle — release `rel-2026-07-10-262fc16c9`

Created in Phase 2 (2026-07-10) when the evidence release was selected
(PAPER_BUILD_PROMPT.md Section 7.13; `papers/governance/project_configuration.md`
Section 5).

- **Release**: `benchmarks/cec_reference_results/` at anchor commit
  `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21`; per-file SHA-256 ledger in
  `papers/governance/evidence_release_manifest.json` (3409 files).
- **Contents**: empty at creation. Populated exclusively by controlled
  publication analyses (Phase 6 onward) invoked in strict-source mode
  (`gsk-stats --strict-source` / `GSK_STRICT_SOURCE=1`), which refuse any
  data source outside the immutable release and emit a source-use audit.
- **Never** place staging outputs (`results/`) or manually edited files here.
