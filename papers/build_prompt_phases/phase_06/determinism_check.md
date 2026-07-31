# Phase 6 Task 18 — Determinism Check

Release: `rel-2026-07-10-262fc16c9` (anchor `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21`)
Driver: `papers/scripts/phase6_run_analysis.py` (invoked exactly as documented: `python papers/scripts/phase6_run_analysis.py`, cwd = project root, `PYTHONIOENCODING=utf-8`, interpreter `C:\AI\Python\Python310\python.exe` — matching the original run's `environment_record.json`)
Git HEAD at both runs: `17fdefe3e1a823d90ca9f246b57fe5112e866d94` (identical).

## Verdict: PASS — fully deterministic

Every statistical/analytical output byte reproduced exactly. The only raw-byte
differences were the wall-clock timestamps that `source_use_log.json` carries by
design (`started_utc`/`finished_utc`) and the sha256 lines those two-field changes
induce in the two manifest files. No numerical, ordering, or formatting
difference anywhere.

## Finding (pre-registered fallback branch taken)

The driver has **no configurable output root**: no `PHASE6_OUT_OVERRIDE` env var,
no `--out` argument, no documented scratch mode. `OUT_ROOT` is hard-coded at
`papers/scripts/phase6_run_analysis.py:74`
(`OUT_ROOT = PAPER_DIR / "analysis" / REL_ID`) and the header documents only the
plain invocation. Per the task instruction ("if it is not [configurable], report
that as a finding instead of hacking"), nothing was added to src or the script.

## Method (deviation, logged)

Because no scratch output mode exists, the comparison roles were inverted — the
script itself was not modified in any way:

1. Snapshotted the canonical bundle `papers/analysis/rel-2026-07-10-262fc16c9/`
   (115 files) and the staging export `results/paper_tables/` (17 files) to the
   session scratchpad (`determinism_scratch/`).
2. Re-ran the driver exactly as documented (it deterministically cleans and
   rewrites its own outputs via `clean_outputs()`).
   Run completed exit 0: 129 manifest outputs, 4987 statistical rows, 1239
   audited opens (all under `benchmarks/cec_reference_results/`), all 3
   strict-source negative tests PASS.
3. Compared every file byte-for-byte (sha256) between the re-run outputs and the
   pre-run snapshot.
4. Restored the pre-run snapshot to the canonical locations (verified
   byte-identical afterwards: 115/115 and 17/17), so the frozen bundle is exactly
   as it was before this task.
5. Deleted the scratch directory.

## Comparison results — analysis bundle (115 files vs 115 files, 0 missing, 0 extra)

| Class | Count | Files |
|---|---|---|
| Byte-identical | 108 | all CSVs, all robustness digests/audits, `cross_check.json`, `source_precheck.json`, all 4 `run_manifest.json`, `table_to_csv_map.md`, `README.md`, `primary_stats/statistical_results.csv`, ... |
| Excluded by task, but in fact byte-identical | 2 | `environment_record.json` (reproduced byte-identically — it contains no timestamp), `run_stdout.txt` (orchestrator capture; not touched by the script) |
| Timestamp-only differences | 5 | see below |
| **Real differences** | **0** | — |

Timestamp-only differences (all vanish once `started_utc`/`finished_utc` are
stripped / the corresponding sha256 entries are masked):

- `cec2017/source_use_log.json` — differs ONLY in `started_utc`/`finished_utc`; all 1239-entry audit content identical
- `cec2013/source_use_log.json` — same two fields only
- `cec2011/source_use_log.json` — same two fields only
- `analysis_checksums.sha256` — exactly 3 lines changed: the sha256 of the 3 `source_use_log.json` files (verified by line diff; `environment_record.json`'s checksum line was unchanged because that file reproduced byte-identically)
- `analysis_manifest.json` — only the 3 sha256 entries for the `source_use_log.json` files

## Comparison results — results/paper_tables staging export (bonus check)

17 files vs 17 files: **17 byte-identical, 0 differences** (T1-T20 exports +
`provenance.json`).

## Recommendation

If a future revision of the driver is permitted, moving `started_utc`/
`finished_utc` out of `source_use_log.json` (e.g., into `run_stdout.txt` or a
separate untracked timing file) would make the entire bundle byte-reproducible
with zero carve-outs. Not applied now (script is frozen for Phase 6).
