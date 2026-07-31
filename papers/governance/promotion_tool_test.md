# Promotion tool scratch-bundle test — `scripts/promote_evidence.py`

| Field | Value |
|---|---|
| Phase / task | Phase 2, task 10 (promotion tool; Section 2.4 controlled staging-to-evidence promotion) |
| Date | 2026-07-10 |
| Anchor commit | `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21` (HEAD verified at test time) |
| Tool under test | `scripts/promote_evidence.py` (created this phase; Copyright header matches `run_ablation.py` style) |
| Test driver | session scratchpad `test_promote_evidence.py` (batched; full stdout reproduced below in summary form) |
| Evidence-tree safety | The REAL tree `benchmarks/cec_reference_results/` was only **read** (to source the scratch bundle); scoped `git status --porcelain -- benchmarks/cec_reference_results` verified EMPTY after the test. The promotion destination was a TEMP dir in the session scratchpad, deleted at the end. |

## Tool design (as tested)

- CLI: `--staging <dir> --suite <s> --optimizer <o> --release-id <id> [--dest benchmarks/cec_reference_results] [--dry-run]`.
- Promotes into a **new versioned subtree** `<dest>/_releases/<release-id>/<suite>/<optimizer>/` (Section 2.4 step 5); the flat live layout `<dest>/<suite>/<optimizer>/` is never written, so the loader-visible panel is undisturbed.
- Generates a promotion manifest (`promotion_manifest/v1`: per-file SHA-256 + size, creation record with tool/git-head/UTC timestamp, byte-verification result) written **beside** the promoted subtree (`<optimizer>_promotion_manifest.json`) so the subtree itself stays a byte-identical mirror of staging.
- Byte-verifies every promoted file (size + independent SHA-256 re-hash) against the accepted staging bundle (step 7); sets every promoted file and the manifest read-only via `os.chmod` (`attrib +R` equivalent — verified with `attrib` below) (step 8).
- Refuses: unsafe suite/optimizer/release-id path components; empty/missing staging; overlapping staging/target; and any re-promotion under an existing release id (immutability — corrections require a NEW release id + supersession record, Section 2.4).

## Test procedure and results (all 22 checks PASS)

Scratch bundle: the 23 top-level summary-set files (`*.csv` + `*.json`: 16 per-dim
summaries + `gsk_cec2011.csv` rollup + `per_run.csv` + `seed_schedule.csv` +
4 metadata JSONs) of `benchmarks/cec_reference_results/cec2011/gsk/`, copied to a
scratchpad staging dir (68,740 bytes). Test release id `rel-test-2026-07-10-scratch`;
dest = TEMP dir (never the real tree).

| # | Check | Result |
|---|---|---|
| 1 | Staging bundle built (23 files) and byte-identical to its evidence source | PASS |
| 2 | `--dry-run` exits 0 and writes **nothing** (temp dest not even created) | PASS |
| 3 | Real promotion exits 0 | PASS |
| 4 | Versioned subtree `<dest>/_releases/rel-test-2026-07-10-scratch/cec2011/gsk/` created | PASS |
| 5 | Live flat layout untouched: `<dest>/cec2011/` absent; dest top level == `["_releases"]` | PASS |
| 6 | Promoted file census == staging census (23/23) | PASS |
| 7 | Promoted copy byte-identical to staging (independent SHA-256 re-hash by the test driver, not the tool) | PASS |
| 8 | Every promoted file read-only (`os.access W_OK` false); `attrib` shows `A R` on sample (`environment.json`) | PASS |
| 9 | Manifest written beside subtree, itself read-only | PASS |
| 10 | Manifest schema/id fields correct; per-file SHA-256 for all 23 files; hashes equal staging hashes; `byte_verified: true, mismatches: 0` | PASS |
| 11 | Re-promotion under the same release id refused (exit 2) with explicit immutability message | PASS |
| 12 | Scoped git status of the REAL evidence tree empty after the test | PASS |
| 13 | Temp dest and scratch staging deleted (read-only bits cleared first — also exercises that the +R flag was really set) | PASS |

## Verdict

`scripts/promote_evidence.py` satisfies the Section 2.4 scripted-ingestion
contract (manifest, versioned subtree, byte verification, read-only marking,
immutability refusal) and is safe by construction with respect to the live flat
layout. Ready for gate-check use by Phases 11–12. No file under
`benchmarks/cec_reference_results/` was written, renamed, or touched.
