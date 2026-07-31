# benchmarks/cec_reference_results — the paper's evidence tree

**Every number, table, and figure in the DT-GSK manuscript resolves from this
folder.** It is read-only promoted evidence: no run ever writes here; changes
arrive only through the controlled promotion pipeline
(`scripts/run_campaign.py` → `papers/scripts/finalize_evidence.py`), which
replaces whole bundles and re-mints the manifests that bind them.

**Current release ids** (resolve programmatically, never hardcode):

| Evidence class | Release id | Manifest (checksum authority) |
|---|---|---|
| Primary suites (flat tree below) | `rel-2026-07-16-78f075cb0` | `papers/governance/evidence_release_manifest.json` |
| Ablation + overlay (`_ablation/`) | `abl-rel-2026-07-16` (51 runs) | `_ablation/manifest.json` |
| Paper-table export (`_paper_tables/`) | `rel-2026-07-16-78f075cb0` | `_paper_tables/manifest.json` |

**For "where does paper number X come from?" open
[`BENCHMARK_EVIDENCE_INDEX.md`](BENCHMARK_EVIDENCE_INDEX.md)** — the resolver
with the full release ledger, per-class read paths, and the pinned exceptions.

## Layout — two conventions, both frozen

Two nesting conventions coexist; each is frozen by manifest hashes and
hardcoded consumer read paths (~28 scripts), so **files are never moved or
renamed** — the conventions are documented instead:

```text
1. FLAT SUITE TREE (what gsk-stats and the paper pipeline read)
   <suite>/<optimizer>/                       suites: cec2011, cec2013, cec2017
     <optimizer>_<suite>_D<dim>.csv           aggregate per-dimension tables
     per_run.csv                              every (function, dim, run) row
     curves/  gen_logs/                       representative curves + checkpoint logs
     environment.json, phase0_protocol.json,  run provenance (5 files)
     run_config.json, seed_schedule.csv,
     verification.json
   optimizers: gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk (7-algorithm panel)
   cec2011 additionally splits per-problem native-dim tables (…_D1.csv … _D240.csv)

2. ABLATION CELLS (component studies; read by generate_ablation_matrix & co.)
   _ablation/scaffold/<cell>/dt-gsk/cec2017/{summary/, curves/}      7 remove-one cells
   _ablation/overlay/<cell>/dt-gsk/<suite>/{summary/, curves/}       4 isolation cells x 2 suites
   _ablation/overlay/analysis/                                        promoted analysis outputs

```

Naming quirks that are **source-faithful, not errors**: curve files use
`Figure_F<f>_D<d>_Run#<r>.csv` (curated human-readable evidence — no script
parses them); cec2011 keeps both a combined table and 16 per-dimension slices.

## Hash basis (verifiers, read this)

Manifest SHA-256 values bind **mint-time working-tree bytes**. On this
repository (Windows, `core.autocrlf=true`, no `.gitattributes` pin yet) that
means most text files hash in their **CRLF** form. A checkout that materializes line endings differently must
verify with EOL tolerance (raw, CRLF→LF, LF→CRLF — as `finalize_evidence.py`
P4 does). A repository-wide `-text` pin plus a one-time re-mint is planned
post-submission.

## Rules

1. **Never edit, overwrite, or write generated results here.** Runs write under
   `results/`; promotion is deliberate and tool-mediated.
2. **Corrections are supersessions.** A corrected bundle gets a new release id
   and a supersession record in its manifest; the old bytes stay recoverable
   via git history.
4. Comparator provenance, citation practice, and the column schema for the
   aggregate tables are documented in `docs/reference/result_schema.md` and the
   index.
