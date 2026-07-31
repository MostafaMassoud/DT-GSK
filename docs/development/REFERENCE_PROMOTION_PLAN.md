# Reference Promotion Plan — CEC2013LSGO now, CEC2020 behind its completeness gate

Status: **AWAITING AUTHOR APPROVAL — nothing has been copied.**
Authority: author directive 2026-07-28 (full prompt on file); SAP Addendum 1
Section 11 (pre-registered promotion and file-class policy, signing commit
`5c9bfae82`); production_deviation_record.md D-5/D-8; CR-0019; plan ruling R7.
Verified inputs: the 11-agent closure audit (strict-inventory state, relocation
map, promotion requirements), plus the layout probes recorded below.

---

## 1. Target tree (exact)

Mirrors the frozen suites' flat per-algorithm layout byte-for-byte in
conventions (verified against `cec2017/gsk/` and `cec2011/gsk/`):

```text
benchmarks/cec_reference_results/
|-- cec2017/ cec2011/ cec2013/          (FROZEN -- untouched, primary manifest)
|-- cec2013lsgo/                        (NEW -- Stage 1)
|   `-- <alg>/                          x7: gsk agsk apgsk fdb-agsk atmals-gsk egsk dt-gsk
|       |-- per_run.csv                 375 rows
|       |-- <alg>_cec2013lsgo_D1000.csv
|       |-- <alg>_cec2013lsgo_D905.csv
|       |-- environment.json  phase0_protocol.json  run_config.json
|       |-- seed_schedule.csv  verification.json    (rewritten: NOT_VERIFIED/NO_REFERENCE)
|       |-- benchmark_variant.json      (NEW sidecar: ackley_variant=transformed, F3/F6/F10)
|       |-- gen_logs/                   15 checkpoint CSVs
|       `-- [dt-gsk only] skipped_runs.csv          (file class: deviation_record)
|       `-- [atmals-gsk, egsk only] *.csv.prebugfix (file class: deviation_record)
|-- cec2020/                            (NEW -- Stage 2, LOCKED until completeness gate)
|   `-- <alg>/  same shape: per_run.csv (1,140), 4 per-dim summaries, 5 provenance,
|               benchmark-variant sidecar not needed, gen_logs/ (38)
|-- _external_baselines/                (relocated in Stage 1.1)
|   `-- cec2013lsgo/{mos,decc-g,shade-ils}/  each: table CSV + EV-09 provenance sidecar
|   `-- README.md                       (status: validated tooling, out of paper scope per CR-0019)
`-- _index/BENCHMARK_EVIDENCE_INDEX.md  (moved; stale rel-2026-07-16 ids fixed; links re-based)
```

Deviations from cosmetic parity with the frozen suites, both **pre-registered**
(SAP Section 11) and recorded in-manifest:
- `curves/` is **excluded** (the frozen suites carry it; the registered policy
  for both new releases excludes it — no registered exhibit consumes new-suite
  curves; convergence data lives in `gen_logs/`). Staging keeps the curves.
- session logs `*_log_*.txt` are **excluded** (D-8.3).

Downstream compatibility is guaranteed by construction: analysis discovery
(`statistics._result_leaf_dir`) resolves a bank by the presence of `gen_logs/`
(promoted) and reads `<alg>_<suite>_D<dim>.csv` flat names (promoted);
verification lookup uses `reference_root/<suite>/<alg>/` (the plain suite name,
freed by the Stage 1.1 relocation). No consumer is special-cased.

## 2. Release identities and manifests

| Release | id pattern | Manifest file | Covers |
|---|---|---|---|
| Primary (frozen) | `rel-2026-07-20-67d9345f9` | `papers/governance/evidence_release_manifest.json` | cec2017/cec2011/cec2013 + README (3,403 files) — **byte-identical, never re-minted** |
| LSGO (Stage 1) | `lsgo-rel-<date>-<anchor9>` | `papers/governance/evidence_release_manifest_cec2013lsgo.json` | everything under `cec2013lsgo/` |
| CEC2020 (Stage 2) | `cec2020-rel-<date>-<anchor9>` | `papers/governance/evidence_release_manifest_cec2020.json` | everything under `cec2020/` |

Same schema and serialization as the primary manifest (`json.dumps(indent=2,
ensure_ascii=False)` + CRLF), plus per-file `file_class` annotations
(`result_data` / `provenance` / `deviation_record` / `variant_sidecar`), the
in-manifest exclusion records (curves, session logs), a `preregistration` field
binding the SAP addendum SHA-256
(`4b351008bebf8f41413cca67703fcbad9562dd111befb9e76e81a032429dcea1`) and
Amendment 1 SHA-256, and the staging source paths + source commit.

**Tooling change required (small, tested): `check_manifest.py` gains a
repeatable `--manifest` flag.** Strict inventory currently checks disk against
ONE manifest, so any second suite on disk would count as unlisted. Union mode:
every non-underscore file under the evidence root must belong to at least one
supplied manifest; each manifest's own byte checks are unchanged. Exit
criterion everywhere below: **zero unlisted under the union**. (Underscore
trees are already outside inventory scope — verified live: `_ablation/` and
`_paper_tables/` are not reported.)

## 3. Stage 1 — CEC2013LSGO (executes on approval)

**S1.0 Preflight gates (all must pass before any write):**
1. Re-run bank audit: 7×375 rows, cells 15/15, dims 905/1000 correct, all runs
   at 3,000,000 NFEs, no non-finite/negative, no duplicate run ids.
2. Seed-pairing audit per SAP Section 12 (replicating
   seed_and_pairing_audit.md Sections 1–4): unified-formula compliance per row
   + cross-algorithm seed identity, 0 mismatches — precondition for every
   paired statistic on the promoted bank.
3. Summary-vs-raw fidelity: per-dim summary means match per_run recomputation
   (tolerance = the documented %.10e round-trip, ≤ ~5e-11 rel).
4. Frozen-analysis byte guard 115/115; full test suite green; clean tree.

**S1.1 Namespace relocation (constraint 4):** move the three external tables to
`_external_baselines/cec2013lsgo/<alg>/` with EV-09 sidecars (publication,
citation key, table/page, run count, FES budget, dims, objective-variant flag —
MOS's published table is raw-Ackley — upstream sha256, prior path) and the
status README; add the missing shade-ils row to `data_ledger.csv` (sha256
prefix `07cc993304c0db81` per the LSGO campaign record) and repoint the
decc-g/mos rows; move `BENCHMARK_EVIDENCE_INDEX.md` → `_index/`, fix its 7
stale `rel-2026-07-16` references, re-base its relative links; update the ~9
live referencing files from the audit's relocation map (README link, runbook,
finalize step-string, review-prompt layer 1.5.0-N note, `_pending_refreeze`
ticket) — historical/append-only records untouched. Gate: primary manifest
still 3,403/3,403; unlisted count drops 4 → 0.

**S1.2 Build `papers/scripts/promote_suite.py`.** Behavior checklist:
- inputs: `--suite {cec2013lsgo|cec2020} [--dry-run]`; refuses unknown suites;
  **refuses cec2020 while its completeness gate fails** (see Stage 2) — the
  refusal is a hard SystemExit naming the failing condition, mirroring the
  `finalize_evidence.py` P2/P6 guard style;
- runs every S1.0 gate itself before copying (self-contained, re-runnable);
- byte-copies the whitelist per algorithm: per_run.csv, per-dim summaries,
  environment/phase0/run_config/seed_schedule (bytes untouched), gen_logs/;
- REWRITES the promoted `verification.json` only: verdict `NOT_VERIFIED`,
  `reason: NO_REFERENCE`, plus a `promotion_note` citing D-8.1 (staging copy
  untouched);
- WRITES the `benchmark_variant.json` sidecar (D-8.2) for cec2013lsgo;
- carries `skipped_runs.csv` + `*.csv.prebugfix` as `deviation_record`
  cross-referenced to D-5/D-6 (D-8.3);
- records exclusions (curves count, log count) in-manifest;
- mints the manifest (schema §2), verifies its own output: re-hash every
  promoted file against the manifest, row-count re-check from the PROMOTED
  tree, union strict-inventory zero-unlisted;
- `--dry-run` prints the full copy/rewrite/exclusion plan and gate results,
  writes nothing.
Unit-tested against a tmp fixture (gate refusal paths included) before first
real use.

**S1.3 Dry run** against the real staging banks; review output.

**S1.4 Mint** `lsgo-rel-*`; then the post gates: union strict-inventory 0
unlisted; primary manifest byte-identical; frozen-analysis 115/115; full test
suite; `gsk-validate` smoke over the promoted suite (should now find the
family banks and report the honest NOT_VERIFIED verdicts).

**S1.5 Commits** (separate, reviewable):
1. `check_manifest` union support + tests.
2. Relocation (S1.1) — message lists moved files and edited referents.
3. `promote_suite.py` + tests.
4. The promotion itself: all promoted files + the new manifest in ONE commit;
   message records release id, source commit of the staging banks, per-bank row
   counts, gate results, and the D-8 corrections applied.
5. Governance follow-through: deviation-record dispositions flipped to DONE,
   `_pending_refreeze.json` ticket P0-NAMESPACE → DONE, decision-log entry.

## 4. Stage 2 — CEC2020 (pre-written, LOCKED)

Unlock condition, ALL required, evaluated by `promote_suite.py --suite cec2020`
itself at every invocation:
1. seven banks present, each exactly 1,140 rows, 38/38 cells × 30 runs;
2. each bank has `environment.json` AND `verification.json` (finalize ran);
3. no `skipped_runs.csv` anywhere under `results/_run_all/*/cec2020`;
4. cross-algorithm seed identity 0 mismatches; unified-formula compliance;
5. nfes ≤ budget per dim with every short row `target_error_reached`;
6. the author's single end-of-campaign commit exists (staging tree clean in
   git, superseding the partial bank in `38df6936b`).

Until then the tool refuses; no CEC2020 file is copied, no manifest minted.
On unlock: identical pipeline (S1.0-analogue gates → dry run → mint
`cec2020-rel-*` → post gates → the same commit protocol). The only
suite-specific differences: no variant sidecar, no deviation-record files
expected (their presence FAILS the gate), budgets 50k/1M/3M/10M.

## 5. Validation gate summary

| Gate | When | Criterion |
|---|---|---|
| Bank audit + seed pairing | pre-copy, both stages | counts exact; 0 seed mismatches |
| Summary fidelity | pre-copy | ≤ %.10e round-trip tolerance |
| Manifest round-trip | post-mint | every promoted file re-hashes to its manifest entry |
| Union strict-inventory | post-mint | 0 unlisted, all manifests |
| Primary release | always | 3,403/3,403 byte-identical; never re-minted |
| Frozen analysis | always | 115/115 byte-identical |
| Test suite + ruff + config locks | every commit | green |

Rollback: any post-gate failure → revert the promotion commit (one commit =
clean revert); staging is never modified, so retry is always possible.
