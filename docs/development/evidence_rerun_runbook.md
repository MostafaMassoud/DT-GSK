# DT-GSK re-run runbook — corrected implementation (C006 + graph backend)

**Written:** 2026-07-14
**Why:** two source defects were found and fixed. One of them changes DT-GSK's
trajectory at `D >= 50`, so the evidence produced by the old binary can no longer be
attributed to the shipped code. This is the exact command sequence to regenerate it.

> ### ✅ Status (2026-07-20): the `D >= 50` regeneration described here is COMPLETE
> This runbook drove the C006 + M038 regeneration, and that work has **landed**. The
> corrected `D >= 50` evidence was re-minted as the current release
> **`rel-2026-07-20-67d9345f9`** (ablation **`abl-rel-2026-07-20`**), the manuscript was
> rebuilt on it, and every build / cross-format-parity / provenance gate is green. The page
> is retained as the **procedure of record** — follow it verbatim if a future `D >= 50` core
> change forces another regeneration.
>
> **RT-001 is CLOSED (2026-07-20) — do NOT re-run it.** The six-comparator re-timing was
> executed and *failed* its determinism gate (3,772 differing rows), so it was not adopted.
> Under Decision 7 Option 3 the runtime table (`tab:runtime`) was instead narrowed to a
> **DT-GSK-only, single-session** table, and the manuscript makes no cross-algorithm
> wall-clock claim anywhere. No timing refresh is outstanding: do not request one, do not
> run `scripts\retime_comparators.py`, and do not re-freeze the runtime table on comparator
> timings. `benchmarks/cec_reference_results/` remains read-only.
>
> **No evidence task is open.** Every empirical number in the manuscript derives from
> `rel-2026-07-20-67d9345f9` (ablation `abl-rel-2026-07-20`); reproduction means re-deriving
> the analysis and artifacts from that release, not re-optimizing.

> ### One-command finalization
> Once every staging bundle is complete (primary suites + scaffold + overlay), the
> entire promotion → stats → analysis-bundle → tables → figures → builds → gates chain
> in Sections 5–7 is automated by **`papers/scripts/finalize_evidence.py`**:
>
> ```powershell
> python papers\scripts\finalize_evidence.py --dry-run   # preflight only
> python papers\scripts\finalize_evidence.py             # full chain (checkpointed)
> ```
>
> It is resumable (`--from-phase P6`), mints the new release ids, and ends with
> `results/_finalize/finalize_report.md` — the old-vs-new headline diff plus the
> remaining HUMAN steps (manuscript prose, freeze-manifest refreeze). Section 6 of this
> runbook remains the authority for those manual manuscript edits.

---

## 1. What changed, and what it does

| Fix | Effect on results | Effect on runtime |
|---|---|---|
| **C006** — final polish received a stale incumbent vector paired with a newer incumbent's fitness (`_dt_core.py`, polish entry). Now `best_idx`/`best_f`/`best_x` are re-materialised atomically. | **Changes trajectories where the polish fires** | negligible |
| **M038** — the interaction graph imported `gsk_family._numba_accel` (does not exist), so the compiled kernels silently fell back to NumPy. Now imports `._numba_accel`. | **None — bit-identical** (verified at D50/D100; kernels are `fastmath=False`, no parallel reduction) | **~1.34× faster** at D50 on the memory-on arm |

Both are locked by new regression tests, each of which **fails on the old code**:

* `tests/regression/test_dt_polish_incumbent_consistent.py` (C006)
* `tests/regression/test_dt_graph_backend_parity.py` (M038 — also asserts the two
  backends are bit-identical; the pre-existing byte-stability KAT could never catch this,
  as its cells are `D <= 30`, below the tier where the graph activates)

### Set expectations before spending the compute

On a 14-cell probe, **only 2 cells changed**, and both changed *slightly worse*
(F1 D50 by ~1e-13; F3 D100 by 0.13%). C006 only bites when a local-search improvement
lands in the same generation as the polish. **This is a correctness fix, not a
performance win** — the polish now searches the neighbourhood it claims to search. Do
not assume the headline ranks survive; they must be re-derived and re-checked.

---

## 2. Blast radius — what must be re-run (and what must not)

The polish is enabled **only at `D >= 50`** (`final_polish_enabled` is `False` at D10/D30
in the `pub` profile), and the interaction graph activates only at `D >= 50`. Therefore:

**Unaffected — do NOT re-run (provably byte-identical):**
* every **comparator** (`gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`, `egsk`) — their
  code did not change at all; their frozen reference CSVs stay valid;
* `dt-gsk` at **CEC2017 D10/D30**, **CEC2013 D10/D30**, **CEC2020** (all dims ≤ 20);
* `dt-gsk` on **CEC2011** problems whose native dimension is < 50.

**Affected — must be re-run:**

| Evidence | Cells |
|---|---|
| CEC2017 primary | `dt-gsk`, **D50 + D100**, 51 runs |
| CEC2013 primary | `dt-gsk`, **D50**, 51 runs |
| CEC2011 primary | `dt-gsk`, **F9, F11, F12, F17, F18, F19, F20** (native D = 126, 120, 240, 140, 96, 96, 96) |
| SGSM overlay ablation | all 4 cells (`full`, `no_sgsm`, `no_adaptive`, `no_finalpolish`), CEC2017 D50/D100 + CEC2013 D50 |
| Scaffold ablation | the **D50/D100** cells |
| Runtime table + §S6.5 overhead | re-measured directly by the above (the `+54%/+37%` figures were the un-accelerated NumPy path) |

---

## 3. Determinism setup (do this in every shell, before Python starts)

`D >= 50` uses `prange`/SGSM, so thread count changes floating-point reduction order.
Pin **all six** variables *before* Python imports numpy/numba — setting them inside
Python has no effect.

```powershell
$env:OMP_NUM_THREADS=1; $env:MKL_NUM_THREADS=1; $env:OPENBLAS_NUM_THREADS=1
$env:VECLIB_MAXIMUM_THREADS=1; $env:NUMEXPR_NUM_THREADS=1; $env:NUMBA_NUM_THREADS=1
```

With Numba pinned to one thread per process, **process-level parallelism is still safe**:
each cell's seed is a pure function of `(base_seed, dim, func, run)`, independent of worker
count or execution order. So use `--parallel --workers N --numba-threads 1`.

Sanity-check the toolchain before committing hours:

```powershell
python -m pytest tests\regression\test_dt_polish_incumbent_consistent.py tests\regression\test_dt_graph_backend_parity.py tests\regression\test_dt_gsk_byte_stable.py -q
```

---

## 4. The commands, in dependency order

Run from the repository root. Everything writes to `results/` — **never** to
`benchmarks/cec_reference_results/`.

### 4.1 Primary evidence (`dt-gsk` only — comparators are untouched)

```powershell
# CEC2017 -- the affected tiers
python run.py --root . --optimizer dt-gsk --suite cec2017 --function 1:30 --dimension 50,100 --runs 51 --parallel --workers 15 --numba-threads 1 --convergence-graphs --overwrite

# CEC2013 -- D50 only
python run.py --root . --optimizer dt-gsk --suite cec2013 --function 1:28 --dimension 50 --runs 51 --parallel --workers 15 --numba-threads 1 --convergence-graphs --overwrite

# CEC2011 -- only the seven native-D>=50 problems
python run.py --root . --optimizer dt-gsk --suite cec2011 --function 9,11,12,17,18,19,20 --dimension native --runs 25 --parallel --workers 15 --numba-threads 1 --convergence-graphs --overwrite
```

> If you prefer a **coherent full DT-GSK campaign** over a surgical one (the external
> review recommends this, to avoid any mixed-binary question), drop the `--dimension`
> restriction and re-run all dims/suites for `dt-gsk`. It costs more but removes the need
> to argue that D10/D30 was unaffected. The comparators still never need re-running.

### 4.2 Ablation evidence

```powershell
# SGSM overlay -- the 4-cell direct isolation (this is what S6.5 reports)
python scripts\run_overlay_ablation_51.py --suite cec2017
python scripts\run_overlay_ablation_51.py --suite cec2013

# Scaffold remove-one ablation -- the D>=50 cells
python scripts\run_ablation.py --dimension 50,100 --runs 25 --workers 15
```

### 4.3 Statistics, tables, figures

```powershell
python -m gsk_family.cli.stats --suite CEC2017 --dims 10,30,50,100
python -m gsk_family.cli.stats --suite CEC2013 --dims 10,30,50
python -m gsk_family.cli.stats --suite CEC2011

python papers\scripts\generate_ablation_matrix.py --dimension 50
python papers\scripts\generate_ablation_matrix.py --dimension 100
python papers\scripts\ablation_overlay_effects.py

python papers\scripts\generate_latex_tables.py
python papers\scripts\generate_full_convergence.py
python papers\scripts\generate_nemenyi_cd.py
python papers\scripts\generate_rank_charts.py
```

### 4.4 Gates

```powershell
python -m pytest -q
python -m ruff check src tests scripts
python scripts\validate_profile_lock.py --root .
python scripts\build_docs_html.py
```

---

## 5. Promote to a NEW immutable release — never overwrite the old one

> **Executed.** The regenerated evidence was promoted as **`rel-2026-07-20-67d9345f9`** /
> **`abl-rel-2026-07-20`** (superseding the interim `rel-2026-07-16-78f075cb0` /
> `abl-rel-2026-07-16`). The pre-fix `rel-2026-07-10-262fc16c9` / `abl-rel-2026-07-13`
> remains the honest record of the *old* binary — kept, never overwritten. The steps below
> are the procedure that was followed and that a future regeneration repeats.

The pre-fix release (`rel-2026-07-10-262fc16c9`, ablation `abl-rel-2026-07-13`) is the
honest record of what the **old** binary produced. Keep it. Promote the regenerated
evidence as a **new** release, recording:

* the git commit of the corrected source (commit the C006 + backend fixes **before**
  launching, so the release binds to an exact SHA);
* the configuration hash, environment lock, and **the selected graph backend**
  (`numba`, now that it actually loads — the old release ran NumPy);
* the seed schedule, raw run files, analysis scripts, and a checksum inventory.

### 5.1 Promotion is TWO steps — the tool alone does not update what the stats read

`scripts/promote_evidence.py` can write a versioned audit copy under `_releases/`, but
**per-release audit copies are no longer retained** (removed 2026-07-18 — git history is
the audit record). It **never touches the flat live layout** `<suite>/<optimizer>/` — by
design; `gsk-stats`, the loaders, and every paper script read the **flat layout only**.
Therefore:

1. **Versioned promotion (optional; git history is the audit record)** — one call per suite bundle:

   ```powershell
   python scripts\promote_evidence.py --staging results/_run_all/dt-gsk/cec2017 --suite cec2017 --optimizer dt-gsk --release-id rel-<date>-<sha> --dry-run
   # inspect the plan, then re-run without --dry-run; repeat for cec2011, cec2013
   ```

2. **Flat-layout refresh (what the stats actually read)** — an explicit,
   user-sanctioned maintenance step: replace the contents of
   `benchmarks/cec_reference_results/<suite>/dt-gsk/` with the accepted staging
   bundle for each of cec2017/cec2011/cec2013 (the old flat cells remain recoverable
   via git history and the prior release bundle). Comparator directories are NOT
   touched. Rename the summary CSVs if staging names differ from the reference
   convention (`dt-gsk_<suite>_D<dim>.csv`; cec2011 rollup `dt-gsk_cec2011.csv`).

3. **Ablation + overlay** land under `_ablation/` as a NEW additively-minted release
   id (keep `abl-rel-2026-07-13`; add a supersession record in the manifest). The
   51-run overlay staging roots are `results/_ablation_sgsm_cec2017_51/` and
   `results/_ablation_sgsm_51/`; the scaffold cells are `results/_ablation/<cell>/`.

4. **The paper-tables layer has one more hop**: `generate_latex_tables.py` reads the
   promoted export `benchmarks/cec_reference_results/_paper_tables/`, which is
   produced by the Phase-6 exporter from the controlled analysis bundle
   (`papers/analysis/<release>/`). After `gsk-stats` produces the new panels, the
   analysis bundle and the `_paper_tables` export must be regenerated and promoted
   before the table generators run — otherwise the tables silently rebuild from the
   old release's CSVs.

6. Update `_index/BENCHMARK_EVIDENCE_INDEX.md` and re-run the release self-checks; only
   then run stats -> tables -> figures -> builds.

---

## 6. Mandatory manuscript edits after the re-run

These were **not optional** — the pre-fix text was true only of the *old* binary — and they
**landed in the `rel-2026-07-20` manuscript build**. They are recorded here as the edit
checklist a future `D >= 50` regeneration must repeat:

1. **Supplement §S6.6 ("Implementation Caveats")** — the pre-fix text disclosed the polish
   defect and *"[left] the frozen numbers intact rather than mix corrected and uncorrected
   cells."* It now states the defect was **identified and corrected**, and all `D >= 50`
   evidence was **regenerated** under the corrected implementation.
2. **Supplement §S6.5** — the `+54%` / `+37%` memory overhead (the un-accelerated NumPy
   cost) was replaced with the values re-measured on the accelerated numba backend:
   **+57.3 %** (CEC2017 D50), **+36.3 %** (D100), **+30.3 %** (CEC2013 D50). These are final
   (RT-001 closed; no further timing refresh is pending).
3. **Main-text runtime table + Conclusions limitation** — the "upper estimate" qualifier
   about the NumPy backend was removed; the numbers are the accelerated path. `tab:runtime`
   carries **no comparator columns**: RT-001 closed without adoption, so the table was
   narrowed to DT-GSK-only, single-session, and no cross-algorithm wall-clock claim is made.
4. **Every headline claim was re-verified** against the regenerated statistics — the overall
   CEC2017 mean rank, the per-dimension standings, the D30 / CEC2011 eGSK contrasts, and the
   §S6.5 interaction-graph isolation null. None were carried over on faith.
5. Re-run the binding/parity checks (all green as of 2026-07-20): `papers\scripts\check_manifest.py`,
   `papers\scripts\validate_evidence_bindings.py`,
   `papers\scripts\validate_cross_format_parity.py`.

---

## 7. Rough cost

With `--workers 15` and Numba pinned to 1 thread per process, and the graph now compiled
(~1.34× faster at D50 on the memory-on arm):

| Stage | Order of magnitude |
|---|---|
| CEC2017 `dt-gsk` D50 + D100 (51 runs) | ~2–3 h |
| CEC2013 D50 + CEC2011 (7 problems) | ~1–2 h |
| Overlay ablation (4 cells × 51 runs, both suites) | ~4–6 h |
| Scaffold ablation (D50/D100) | ~2–4 h |
| Oracle study | minutes |
| Stats + figures + rebuild | ~1 h |

Budget roughly **one to two days** of wall-clock on a 16-core workstation.
