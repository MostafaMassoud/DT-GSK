# DT-GSK — Consolidated Submission Implementation Plan

**Owner:** author team (👤) + Claude (🤖) · **Target venue:** MDPI *Algorithms* (JCR Q2) · **Prepared:** 2026-07-12
**Ground rules:** commit at every phase boundary, **never `git push`** (author-gated). No number, rank, statistic, or claim is invented. Determinism and the freeze manifest are re-established after every artifact rebuild.

---

## 0. Conventions (apply to every phase)

### 0.1 Shell & parallelism
- All commands are **Windows PowerShell 5.1**. Chain with `;` (not `&&`). Set env vars with `$env:NAME="value"`.
- **Every parallel command uses 12 workers** (`--workers 12`) unless a step explicitly overrides it.

### 0.2 Canonical deterministic build commands (memorise these — they recur)
```powershell
# Main PDF  (pdfTeX consumes the epoch + FORCE flag)
$env:SOURCE_DATE_EPOCH="1783468800"; $env:FORCE_SOURCE_DATE="1"; python papers/scripts/build_pdf.py
# Main DOCX
Remove-Item Env:FORCE_SOURCE_DATE -ErrorAction SilentlyContinue; $env:SOURCE_DATE_EPOCH="1783641600"; python papers/scripts/build_docx.py
# Supplement PDF  (4-pass, rebuild bib; MUST run BEFORE the supplement DOCX so supplementary.aux is populated)
$env:SOURCE_DATE_EPOCH="1783468800"; $env:FORCE_SOURCE_DATE="1"; python papers/scripts/build_supplementary.py --rebuild-bib
# Supplement DOCX
Remove-Item Env:FORCE_SOURCE_DATE -ErrorAction SilentlyContinue; $env:SOURCE_DATE_EPOCH="1783641600"; python papers/scripts/build_docx.py --supplementary
```

### 0.3 Canonical validation commands
```powershell
# DOCX structural validators (0 markers, header/field/table checks)
python papers/scripts/validate_docx.py papers/DT-GSK.docx
python papers/scripts/validate_docx.py papers/supplementary.docx
# Freeze-manifest recompute (expect "12/12 match []")
python papers/scripts/check_manifest.py            # created in Phase A0.T3 (below)
# Reproducibility: build the same artifact twice, hashes must match
(Get-FileHash papers/DT-GSK.docx -Algorithm SHA256).Hash
```

### 0.4 Fixed protocol constants (never change without re-freezing everything)
| Constant | Value |
|---|---|
| Seed base | `20240620` |
| CEC2017 (primary) | 29 scored functions (F1, F3–F30), D∈{10,30,50,100}, 51 runs, MaxFES=10⁴·D |
| CEC2011 | 22 problems, native dims, 25 runs, MaxFES=150,000 |
| CEC2013 | 28 functions, D∈{10,30,50}, 51 runs |
| ISM-active tiers | D ≥ 50 (`interaction_graph_min_dim=50`) |
| Freeze manifest | `papers/governance/main_manuscript_freeze_manifest.json` (12 tracked files) |
| Reproducibility manifest | `papers/governance/reproducibility_manifest.json` |
| Workers | **12** |

### 0.5 Global rollback primitive (available to every phase)
```powershell
git status --short                       # inspect
git stash                                # park uncommitted work
git checkout -- <path>                   # revert one file to HEAD
git revert --no-edit <commit-sha>        # undo a committed phase (keeps history)
```
Every phase below also lists a phase-specific rollback.

---

# PART A — Manuscript (science + review response), Q2-calibrated

> Scope decision already made: for a Q2 (Algorithms) LaTeX submission, the boundary-dimension sweep (Q1-043), non-family baselines (Q1-007), and second-environment replication (Q1-052) are **out of scope**. The only compute worth running is the ISM isolation.

## Phase A0 — Decisions, prerequisites & tooling

**Objective.** Resolve every author-only decision and install the small helper scripts the later phases depend on, so no downstream phase blocks on a missing input.

**Prerequisites.** Clean working tree (`git status --short` empty). Python 3.10 env active. MiKTeX + pandoc on PATH.

**Dependencies.** None (this is the root phase).

**Step-by-step tasks.**
1. **T1 — Venue & title decision (👤).** Confirm target = *Algorithms* (Q2). Choose title treatment: retitle "High-Dimensional" → "up to 100 dimensions"/"dimension-tiered" **or** keep and justify. Record the choice in `papers/governance/administrative_gap_register.md`.
2. **T2 — Author-side data (👤).** Provide: H.S.M.R. CRediT roles + institutional e-mail; GenAI product/version/date; code/data licenses; the Zenodo DOI/URL (or a decision to defer to "available upon publication").
3. **T3 — Install `check_manifest.py` (🤖).** A read-only recompute helper (no network, no writes) that prints `N/12 match` and lists mismatches. Used as the manifest gate in every rebuild phase.
4. **T4 — `updateFields` decision (👤).** DOCX `updateFields` = **false** (no "update fields?" prompt, current state) **or** **true** (auto-update on open). Mutually exclusive; record the choice.
5. **T5 — DOCX-is-submission-artifact decision (👤).** LaTeX submission (DOCX is a companion → Part B stops at D1) **or** Word submission (→ execute D2, then the manual D3 pass).

**Validation procedure.** `git status --short` is clean after T3 is committed. Run:
```powershell
python papers/scripts/check_manifest.py
```
Expected: `12/12 match []`.

**Testing requirements.** None beyond T3's validation command above.

**Deliverables.** Decisions recorded in `administrative_gap_register.md`; `papers/scripts/check_manifest.py` committed.

**Acceptance criteria.** All five decisions recorded; `check_manifest.py` prints `12/12 match []`; tree clean.

**Risks.** (R1) Decisions deferred → downstream phases stall. (R2) Wrong DOI inserted later.
**Mitigation.** Treat A0 as a hard gate; do not start A1 edits that depend on undecided items (title, DOI) until T1/T2 land.
**Rollback.** `git revert` the A0 commit; decisions are additive so reversion is safe.

**Completion checklist.** *(status 2026-07-13 — decisions in decision_log.md D-0012)*
- [x] Venue confirmed (Algorithms, D-0010); title **recommendation** recorded — keep + clarify (A0-3, author-confirm) (T1)
- [ ] Author data supplied — OPEN, author-side facts AG-0001..0007 + DOI/licenses (T2)
- [x] `check_manifest.py` committed (d77e49b4a) and prints `12/12 match []` (T3)
- [x] `updateFields` decision recorded — **false / self-contained** (A0-2) (T4)
- [x] DOCX-format decision recorded — **LaTeX submission; DOCX = companion** (A0-1) → Part B stops at D1 (T5)
- [x] Decisions committed (no push); A1 + A2 unblocked

---

## Phase A1 — No-compute manuscript hardening

**Objective.** Apply every improvement that needs **no new experiment**: a complete specification appendix, statistical re-analysis of the *existing* per-run data, proper critical-difference diagrams, the remaining VERIFY item, and the A0 author-decision edits.

**Prerequisites.** A0 complete (title/DOI/CRediT available). Frozen per-run CSVs present under `papers/analysis/rel-2026-07-10-262fc16c9/`.

**Dependencies.** A0.

**Step-by-step tasks.**
1. **T1 — Specification appendix (🤖).** Add "Appendix: Complete Specification" to `papers/sections/` lifting from the frozen code: full Algorithm-1 pseudocode with every constant; ACE arm table (all arms, probabilities, floors); ARGP state machine; BSE/archive/restart rules; the exact two-accumulator graph equations + ℓ₁-normalisation; graph→block extraction; eigenframe polish; RNG child-seed map; per-tier cadence table. Bind each block to its `src/gsk_family/optimizers/*.py` line. Closes review Gate-F cluster (Q1-011/018–032/144–146/155).
2. **T2 — Statistical re-analysis, existing data only (🤖).** Regenerate: scale-invariant endpoint (log-error ratio) alongside raw (Q1-060/054); exact/permutation p-values for small effective-n cells (Q1-062); tie-corrected Friedman + sensitivity (Q1-069); median/IQR + bootstrap CIs (Q1-074); the complete robustness-transition matrix (Q1-077); per-run FES ledgers by component (Q1-038). No new runs.
3. **T3 — Critical-difference diagrams (🤖).** Regenerate Nemenyi CD figures as standard connected-clique diagrams (Q1-070/123).
4. **T4 — VERIFY items (🤖).** Rename supplement "Extended Diagnostics" if it overstates (Q1-085); apply any remaining low-risk wording.
5. **T5 — Author-decision edits (🤖).** Insert DOI/repo URL in Data Availability (Q1-102/106); title change per A0.T1 (Q1-004); H.S.M.R. CRediT + e-mail (Q1-107/154); GenAI version/date (Q1-108); licenses (Q1-115); supplement numbering if venue requires (Q1-111/112).
6. **T6 — Rebuild all four deliverables** (§0.2), PDF-before-DOCX for the supplement.
7. **T7 — Re-freeze** the manifest for every changed tracked file; append an `a1_review_hardening_refreeze` block; refresh `reproducibility_manifest.json`.

**Validation procedure (run manually).**
```powershell
# after T6 rebuild:
python papers/scripts/validate_docx.py papers/DT-GSK.docx
python papers/scripts/validate_docx.py papers/supplementary.docx
# reproducibility (run each build twice, hashes must match):
$env:SOURCE_DATE_EPOCH="1783468800"; $env:FORCE_SOURCE_DATE="1"; python papers/scripts/build_pdf.py; (Get-FileHash papers/DT-GSK.pdf).Hash
$env:SOURCE_DATE_EPOCH="1783468800"; $env:FORCE_SOURCE_DATE="1"; python papers/scripts/build_pdf.py; (Get-FileHash papers/DT-GSK.pdf).Hash
# manifest gate:
python papers/scripts/check_manifest.py
# no reader-facing machine tokens / unresolved refs (expect 0):
python -c "import zipfile,re; d=zipfile.ZipFile('papers/DT-GSK.docx').read('word/document.xml').decode('utf-8','ignore'); print('at-ref', d.count('@@REF'), 'fffd', d.count(chr(0xFFFD)))"
```

**Testing requirements.** Two identical consecutive PDF hashes and two identical DOCX hashes; `check_manifest.py` = 12/12; validators report `markers_left: 0`.

**Deliverables.** Spec appendix; regenerated stats tables + CD figures; DOI/CRediT/GenAI edits; four rebuilt deterministic deliverables; refreeze block.

**Acceptance criteria.** All above test commands pass; the review's IN_RELEASE Gate-F cluster and the cheap statistical tickets are answered *in the paper*; no primary number changed.

**Risks.** (R1) Re-analysis contradicts a headline number. (R2) Spec appendix drifts from code. (R3) Non-reproducible rebuild.
**Mitigation.** (R1) Re-analysis is *additive* (new columns/robustness), never replaces the frozen primary — if a transition appears, disclose it, do not overwrite. (R2) Every appendix constant carries a `% BIND:` to its code line; diff against `_dt_profiles.py`. (R3) Bisect the offending part with the two-build hash diff (`zipfile` part-by-part).
**Rollback.** `git revert` the A1 commit; restore the manifest via `git checkout -- papers/governance/*.json`; rebuild.

**Completion checklist.** *(status 2026-07-13 — reframed after investigation; decision_log.md D-0013, commit b319d844b)*
- [x] Operator spec added + BIND-mapped (T1) — as supplement **§S5.3** (surgical: ACE arms, graph update, block extraction, eigenframe/Cauchy/M); most spec already existed
- [x] Post-hoc stats added from existing data (T2) — **§S2 sec:supp:posthoc**: endpoint-invariance + exact-inference, results-gated (both favorable); tie-corrected Friedman / BCa / r01–r08 were **already present**, not regenerated
- [ ] CD diagrams as connected-clique (T3) — **deferred (optional)**; current Demšar bar-chart form is defensible
- [ ] VERIFY/wording item Q1-085 (T4) — **deferred (optional)**
- [ ] DOI/CRediT/GenAI/licenses/title (T5) — **BLOCKED on author facts** (AG-0001..0007)
- [x] Supplement rebuilt, reproducible ×2 (T6) — PDF+DOCX bit-identical; DOCX markers_left=0
- [x] Main 12-file manifest preserved (T7) — supplement is out-of-scope; `check_manifest.py` → 12/12 (no refreeze needed)
- [x] Committed (no push) — b319d844b

---

## Phase A2 — ISM-isolation experiment (harness READY)

**Objective.** Generate the direct ISM-on-vs-off evidence on the primary suite at the active tiers — the single experiment that answers the review's central objection (Q1-001/002/088/142/093).

**Prerequisites.** A0 complete. Configs present and verified: `configs/_ablation/overlay_{full,no_sgsm,no_adaptive,no_finalpolish}_cec2017.yml` (committed 22abf30ee; each already confirmed runnable).

**Dependencies.** A0 (not A1 — A2 can run in parallel with A1).

**Step-by-step tasks.**
1. **T1 — Smoke test (👤 ⚙️, ~minutes).** Confirm the pipeline and gauge wall-time on one cell / small slice.
2. **T2 — Full four-cell isolation (👤 ⚙️, heavy).** Run all four overlay cells on CEC2017 D50+D100. Cells are independent → may run in four terminals to parallelise across cells.
3. **T3 — (Optional) scaffold ablation at active tiers (👤 ⚙️).** Complements the overlay by re-confirming the scaffold remove-one contrasts at D50/D100 (Q1-089/090/091).
4. **T4 — (Optional) diagnostics traces (👤 ⚙️).** For Q1-093; enable `generation_logs`/`ism_diagnostics` on a representative slice.
5. **T5 — Promote results into the reference tree (👤).** Move staged results into `benchmarks/cec_reference_results/_ablation/overlay/` (read-only evidence tree).

**Exact commands (run manually, 12 workers).**
```powershell
# T1 smoke (one cell, D50, 3 runs, ~minutes):
python run.py --config configs/_ablation/overlay_full_cec2017.yml --dimensions 50 --runs 3 --workers 12 --output-root results/_smoke

# T2 full isolation (all four cells; add --runs 51 for primary-panel power, or omit for the pre-registered 25):
python run.py --config configs/_ablation/overlay_full_cec2017.yml         --workers 12 ; `
python run.py --config configs/_ablation/overlay_no_sgsm_cec2017.yml      --workers 12 ; `
python run.py --config configs/_ablation/overlay_no_adaptive_cec2017.yml  --workers 12 ; `
python run.py --config configs/_ablation/overlay_no_finalpolish_cec2017.yml --workers 12

# T3 optional scaffold ablation at active tiers:
python scripts/run_ablation.py --suite cec2017 --dimension 50,100 --runs 25 --workers 12

# T5 promote staged results into the read-only reference tree:
robocopy results\_ablation_sgsm_cec2017 benchmarks\cec_reference_results\_ablation\overlay /E
```

**Validation procedure (run manually).**
```powershell
# every expected cell produced a summary CSV (expect one per cell x dim):
Get-ChildItem results\_ablation_sgsm_cec2017 -Recurse -Filter "dt-gsk_cec2017_D*.csv" | Select-Object FullName
# per-run row counts are complete (29 funcs x runs) — inspect per_run.csv per cell:
Get-ChildItem results\_ablation_sgsm_cec2017 -Recurse -Filter "per_run.csv" | ForEach-Object { "$($_.FullName): $((Import-Csv $_.FullName).Count) rows" }
```

**Testing requirements.** All four cells present for D50 and D100; per-run row counts equal (29 × runs) with no failed/NaN rows; the `full` cell reproduces the committed main-panel DT-GSK at the shared seeds (spot-check a known value, e.g. a D50 mean).

**Deliverables.** `results/_ablation_sgsm_cec2017/{full,no_sgsm,no_adaptive,no_finalpolish}/dt-gsk/cec2017/…`; promoted copies under the reference tree.

**Acceptance criteria.** Four complete cells × two dims; validation commands list the expected files; promotion mirrors the CEC2013 overlay layout.

**Risks.** (R1) Very long wall-clock at D100 (DT-GSK 5–13× slower). (R2) A run crashes mid-cell. (R3) Promotion writes to the read-only tree incorrectly.
**Mitigation.** (R1) Run D50 first; interleave cells across terminals; the smoke test in T1 sets expectations. (R2) `--output-root` isolates cells; re-run only the failed cell (`overwrite: true` in the config). (R3) `robocopy` merges non-destructively; verify with the file-count command before committing.
**Rollback.** Delete `results/_ablation_sgsm_cec2017/` and the promoted `…/overlay/…/cec2017/` subtrees; nothing in the manuscript changes until A3.

**Completion checklist.**
- [ ] Smoke test passed, wall-time gauged (T1)
- [ ] Four cells × D50+D100 complete (T2)
- [ ] (opt) scaffold ablation done (T3)
- [ ] (opt) diagnostics traces captured (T4)
- [ ] Results promoted to the reference tree (T5)
- [ ] File-count + per-run validation commands pass
- [ ] Staging committed (results are git-ignored; promotion committed) — no push

---

## Phase A3 — Integration of isolation results

**Objective.** Turn the A2 data into paper evidence: paired contrasts, effect sizes, CIs, cost accounting; then **upgrade or soften** the ISM-efficacy language to exactly match what the data shows.

**Prerequisites.** A2 complete and promoted; A1 complete (spec appendix + stats framework in place).

**Dependencies.** A1, A2.

**Step-by-step tasks.**
1. **T1 — Aggregate (🤖).** Build the isolation matrix: full vs {no_sgsm, no_adaptive, no_finalpolish} per-function paired Wilcoxon + Holm, Friedman over the 4 cells, Vargha–Delaney A₁₂ with CIs, FES/wall-time/activation-rate per cell.
2. **T2 — Author-facing exhibits (🤖).** New supplement table(s) + a main-text sentence reporting the isolated ISM contribution; fold in diagnostics if T4 was run.
3. **T3 — Claim calibration (🤖).** If ISM shows a significant, stable benefit → strengthen the abstract/conclusion accordingly. If not → keep the "isolated ISM utility not established / future work" framing and ensure no headline attributes an inactive-tier result to ISM (Q1-142). Convert the supplement "Deferred to Future Work" section into a "Completed direct isolation" section (removing the deferral).
4. **T4 — Rebuild + re-freeze** (§0.2, §0.3).

**Exact commands (run manually, 12 workers where applicable).**
```powershell
# T1 aggregate the promoted overlay isolation (per dimension):
python papers/scripts/generate_ablation_matrix.py --ablation-root benchmarks/cec_reference_results/_ablation/overlay --suite cec2017 --dimension 50  --full-cell full
python papers/scripts/generate_ablation_matrix.py --ablation-root benchmarks/cec_reference_results/_ablation/overlay --suite cec2017 --dimension 100 --full-cell full
# T4 rebuild all four deliverables (see 0.2), then:
python papers/scripts/check_manifest.py
python papers/scripts/validate_docx.py papers/DT-GSK.docx
python papers/scripts/validate_docx.py papers/supplementary.docx
```

**Testing requirements.** Aggregated contrasts reproduce from the promoted CSVs; every new number carries a `% BIND:` to its source; 4 deliverables reproducible ×2; manifest 12/12.

**Deliverables.** Isolation matrix + exhibits; calibrated claims; rebuilt deliverables; `a3_isolation_integration_refreeze` block.

**Acceptance criteria.** Every ISM-efficacy sentence maps to a direct-isolation contrast or is labelled design rationale; abstract/conclusion contain no wording stronger than the data; deterministic + 12/12.

**Risks.** (R1) Isolation shows ISM does **not** help significantly. (R2) A new exhibit breaks pagination/reproducibility.
**Mitigation.** (R1) That is a legitimate scientific outcome — report it honestly; the paper already frames ISM as a fully-specified mechanism, so the contribution stands on specification + scaffold performance. (R2) Re-run the two-build hash diff; keep exhibits inside the existing float/table machinery.
**Rollback.** `git revert` the A3 commit; restore manifests; rebuild.

**Completion checklist.**
- [x] Isolation matrix aggregated (T1) — CEC2017 D50/D100 via `generate_ablation_matrix.py` + A₁₂/cost via `ablation_overlay_effects.py`; committed CSVs in `papers/analysis/ablation_overlay/`
- [x] Exhibits + main-text sentence added (T2) — supplement **S6.5** (Table A17) + main-text null stated in performance/proposed_algorithm/conclusions
- [x] Claims calibrated; deferral resolved (T3) — **honest null**: ISM no significant standalone benefit (Holm 0.80/0.93, A₁₂≈0.50) + `+54%/+37%` cost; final-polish significant; no primary claim upgraded
- [x] Rebuilt, reproducible ×2, manifest 12/12 (T4) — all 4 artifacts bit-identical ×2; refrozen (`a3_ism_isolation_refreeze`, 12/12). Raw overlay evidence committed by author (`770bd6e72`, full 296-file tree incl. curves) — **provenance complete**
- [ ] Committed (no push)

---

## Phase A4 — Final manuscript verification

**Objective.** Independent, adversarial confirmation that the manuscript is internally consistent, reproducible, and free of the defects the reviews raised.

**Prerequisites.** A1 + A3 complete.

**Dependencies.** A1, A2, A3.

**Step-by-step tasks.**
1. **T1 — Multi-panel re-review (🤖).** Re-run the internal adversarial review (math/stats/consistency/citations) against the *current* PDFs; verify every finding against code/tables before acting.
2. **T2 — Register refresh (🤖).** Re-disposition the ChatGPT 155-ticket register against the new state; regenerate `ISM_GSK_Comprehensive_Issue_Register_UPDATED.csv` + addendum.
3. **T3 — Full artifact integrity sweep (🤖).** Determinism ×2 for all four deliverables; manifest 12/12; 0 machine tokens; supplement DOCX 0 "??".

**Exact commands (run manually).**
```powershell
# full reproducibility sweep — build each artifact twice, compare hashes:
$env:SOURCE_DATE_EPOCH="1783468800"; $env:FORCE_SOURCE_DATE="1"; python papers/scripts/build_pdf.py; (Get-FileHash papers/DT-GSK.pdf).Hash
$env:SOURCE_DATE_EPOCH="1783468800"; $env:FORCE_SOURCE_DATE="1"; python papers/scripts/build_supplementary.py --rebuild-bib; (Get-FileHash papers/supplementary.pdf).Hash
Remove-Item Env:FORCE_SOURCE_DATE -ErrorAction SilentlyContinue; $env:SOURCE_DATE_EPOCH="1783641600"; python papers/scripts/build_docx.py; (Get-FileHash papers/DT-GSK.docx).Hash
$env:SOURCE_DATE_EPOCH="1783641600"; python papers/scripts/build_docx.py --supplementary; (Get-FileHash papers/supplementary.docx).Hash
python papers/scripts/check_manifest.py
python papers/scripts/validate_docx.py papers/DT-GSK.docx
python papers/scripts/validate_docx.py papers/supplementary.docx
```
(Run each build command a second time and confirm identical hashes.)

**Testing requirements.** Two identical hashes per artifact; 12/12; both validators pass; no reviewer finding survives verification.

**Deliverables.** Refreshed review report + updated register; a signed-off "camera-ready modulo author-side items" statement in the governance log.

**Acceptance criteria.** All gates green; the residual open items are only author-side administrative (ORCIDs, real submission dates).

**Risks.** (R1) A late finding forces a re-loop.
**Mitigation.** Treat A4 as iterative — fix, re-freeze, re-verify until clean; each fix is its own small commit.
**Rollback.** Per-fix `git revert`.

**Completion checklist.**
- [x] Re-review clean (T1) — adversarial consistency review done; A3 confirmed clean; surfaced fixes all applied (title reframe + 4 consistency edits); see D-0015
- [x] Register refreshed (T2) — 19 tickets re-dispositioned (explicit/verified, no over-claim): ISM-isolation cluster (Q1-001/002/088/142) + title (Q1-004) + ACE arms (Q1-012) RESOLVED; S5.3 spec + S2 stats items ADDRESSED; Q1-093 PARTIAL (EG-005). Register + addendum refreshed in `Downloads/` (07-13 supersedes 07-12)
- [x] Determinism ×2 + 12/12 + validators (T3) — all 4 artifacts bit-identical ×2; manifest 12/12; DOCX `markers_left:0`; zero repair-triggers; Table A17 ↔ CSVs consistent
- [ ] Governance sign-off recorded; committed (no push)

---

# PART B — DOCX fidelity (only if the DOCX is the submission artifact)

> Gate: **RESOLVED (D-0012, A0-1) → LaTeX submission.** Part B **stops at the completed D1**; the DOCX is a clean, self-contained companion. D2/D3 are DEFERRED and only revisited if the author is later required to submit in Word.

## Phase D1 — Content-fidelity fixes — **COMPLETE ✅**

**Status.** Done and committed (abe6f4355, 06d02ad02, 209e2f753, 7b8d3f026), reproducible ×2, manifest 12/12.
**Delivered:** G-012 real author metadata + subject/keywords; G-008 MDPI-blue links `#0875B7`; G-014 two-tier merged grouped table headers; G-015/G-016 figure↔caption binding + row `cantSplit`; G-006 heading terminal periods. (Audit P0 blockers G-009 corrupted math, G-010 `@@REF` tokens confirmed already 0 in the current build.)
**Regression command (run manually to re-confirm):**
```powershell
python papers/scripts/validate_docx.py papers/DT-GSK.docx
python papers/scripts/validate_docx.py papers/supplementary.docx
```

## Phase D2 — MDPI production furniture

**Objective.** Give the DOCX the PDF's page furniture and geometry so it reads as an MDPI Word document.

**Prerequisites.** A0.T5 = Word; A0.T4 `updateFields` decision; D1 complete.

**Dependencies.** D1.

**Step-by-step tasks (🤖, `build_docx.py` post-processing).**
1. **T1 — Headers/footers (G-002/G-013).** Create `word/header*.xml` / `word/footer*.xml`: first-page footer ("pages 1–N", journal URL, "Article" italic label); continuation `PAGE " of " NUMPAGES`; enable `titlePg` (Different First Page). MDPI logo optional (embed as image if licensed).
2. **T2 — Page geometry (G-003).** A4 (`pgSz` 11906×16838); side margins ≈ 1.06 in; header/footer distances so body begins ≈ y=90.6 pt.
3. **T3 — Style consolidation (G-019).** Fold direct run formatting into named styles (Normal, Heading 1–3, Caption, TableText, etc.); remove ad-hoc overrides.
4. **T4 — `updateFields`** per A0.T4.
5. **T5 — Rebuild + re-freeze.**

**Validation / testing (run manually).**
```powershell
Remove-Item Env:FORCE_SOURCE_DATE -ErrorAction SilentlyContinue; $env:SOURCE_DATE_EPOCH="1783641600"; python papers/scripts/build_docx.py
$env:SOURCE_DATE_EPOCH="1783641600"; python papers/scripts/build_docx.py --supplementary
python papers/scripts/validate_docx.py papers/DT-GSK.docx
python papers/scripts/validate_docx.py papers/supplementary.docx
python papers/scripts/check_manifest.py
# header/footer parts now exist (expect > 0):
python -c "import zipfile,re; z=zipfile.ZipFile('papers/DT-GSK.docx'); print(sum(1 for n in z.namelist() if re.search(r'word/(header|footer)\d*\.xml', n)))"
```
Then a **manual Word check**: open in Microsoft Word, confirm running header, first-page footer, "Article" label, page numbers, and body start position.

**Deliverables.** Header/footer parts; A4/margins; consolidated styles; `d2_docx_furniture_refreeze`.

**Acceptance criteria.** Header/footer parts present; geometry within 1–2 pt of PDF; validators pass; reproducible ×2; 12/12.

**Risks.** (R1) Header/footer XML corrupts the package. (R2) `updateFields=true` reintroduces the prompt.
**Mitigation.** (R1) Validate OOXML after each part; keep a pre-D2 tag. (R2) Only set true if A0.T4 chose it; otherwise leave false.
**Rollback.** `git revert` D2; rebuild.

**Completion checklist.** [ ] headers/footers [ ] geometry [ ] styles [ ] updateFields per decision [ ] reproducible ×2 + 12/12 [ ] Word visual check [ ] committed (no push)

## Phase D3 — Pixel pagination + vector figures (manual Word pass)

**Objective.** Best-effort page-for-page match to the PDF. **The pandoc pipeline cannot guarantee pixel pagination** (renderer-dependent); this is a documented manual finishing pass.

**Prerequisites.** D2 complete; Microsoft Word available.

**Dependencies.** D2.

**Step-by-step tasks.**
1. **T1 — Resize oversized figures (🤖).** Cap supplement B1–B12 image width (~5.7 in, preserved aspect) so image+caption share a page (remaining half of G-016). Prefer EMF/SVG where a vector source exists (G-015).
2. **T2 — Page-lock (👤, manual in Word).** Working from the audit's §6–§7 page maps, insert justified manual breaks to hit exactly 39 (main) / 37 (supplement) pages, including the blank final main page.
3. **T3 — Field update + link check (👤).** Ctrl+A → F9; confirm links are `#0875B7` and resolve.

**Validation / testing (manual, in Microsoft Word).**
- Export to PDF twice on a clean machine; confirm identical page counts and element placement.
- Overlay exported Word pages on the reference PDF at 150–200 dpi.
- Search export for `¿`, `@@REF`, "Error! Reference source not found", `#800000` → all zero.

**Deliverables.** Resized figures; a page-locked Word master; an export matching 39/37 pages.

**Acceptance criteria.** The audit's §13 closure gates pass in Microsoft Word (not only LibreOffice).

**Risks.** (R1) Pixel pagination is inherently fragile. (R2) Manual edits drift from the automated pipeline.
**Mitigation.** (R1) Accept "visual parity within Word's renderer" as the real target (the audit's own §1); do not chase literal pixels. (R2) Keep the Word master separate from the pipeline output; re-apply only figure-sizing in the pipeline.
**Rollback.** Discard the manual Word master; the D2 pipeline output remains valid.

**Completion checklist.** [ ] figures resized [ ] page-locked to 39/37 [ ] fields updated [ ] closure gates pass in Word [ ] committed (pipeline parts only; no push)

## Phase D4 — Visio-editable embedded flowcharts

**Objective.** Deliver the paper's process **flowcharts** inside the DOCX as **native Microsoft Visio drawings** that (a) open for full editing in Visio, (b) are extractable directly from the DOCX package, and (c) preserve each flowchart's semantic structure (shapes + connectors), text/content, formatting (line weights, incl. the bold "ISM-adds" outline convention), and layout. **Current state:** the DOCX flattens these flowcharts to raster PNG via `_rewrite_includegraphics` → `.docx.png` (non-editable bitmaps); this phase replaces that for the flowchart figures only.

**Scope.**
- **In scope (primary):** the two process flowcharts `fig:gsk-flowchart`, `fig:ismgsk-flowchart` (TikZ sources `papers/figures/concept/fig_{gsk,ismgsk}_flowchart_src.tex`; the DT-GSK one is 20 nodes with clean terminal/process/decision/`new` styles + arrows — cleanly Visio-mappable).
- **In scope (extension, optional):** schematic diagrams `tab:architecture`, `tab:dim-gating`, `tab:sgsm-mechanism`, `tab:taxonomy` (inline TikZ; less strictly flowchart-shaped).
- **Out of scope:** all data plots (`fig:cd-*`, `fig:conv-*`, `fig:*-ranks`, `fig:nlpsr-schedule`, `fig:rank-vs-dim`, `fig:abl-rankdelta`) — charts, not editable diagrams; they stay vector/raster images.

**Prerequisites.** A0.T5 = Word submission **or** an explicit decision that a Visio-editable DOCX is wanted regardless (note: A0-1 set **LaTeX** as the submission format, so this serves the DOCX companion / author editing workflow — the journal typesets the LaTeX/PDF vector figures, not these). D1 complete. **Microsoft Visio available for verification** (the generator needs no Visio license; confirming round-trip editability does).

**Dependencies.** D1 (and D2 if furniture is also applied). Independent of the A-phases.

**Approach decision (recommended → alternatives).**
- **Tier V-A (recommended) — native VSDX authored from a flowchart spec, OLE-embedded.** Meets every clause. Heaviest build; **self-contained generation** (no external converter, no Visio license to generate).
- **Tier V-B (fallback) — EMF vector embed.** Replace flowchart PNGs with EMF vector; Visio imports + "Ungroup" to editable primitives. Lighter, but **lossy on structure** (geometric primitives, not semantic shapes/connectors) and needs a PDF→EMF converter (Inkscape/LibreOffice — **not currently installed**). Does not fully satisfy "preserving structure."
- **Tier V-C (interim) — standalone `.vsdx` companions.** Ship editable `.vsdx` beside the DOCX. Full editability but **not** "extracted directly from the DOCX" — fails that clause; useful as a stepping stone.

**Step-by-step tasks (Tier V-A).**
1. **T1 — Flowchart spec (single source of truth).** Author `papers/figures/concept/flowchart_specs/{gsk,ismgsk}.json`: ordered nodes (`id`, `type∈{terminal,process,decision,ism_added}`, `text`, `x`, `y`, `w`, `h`), edges (`from`, `to`, optional `label`/routing), and a style block (line weights incl. the 1.3 pt bold ISM-adds outline, fonts, colors). Derive positions from the compiled `fig_ismgsk_flowchart_src.pdf` (or by parsing the TikZ `below=/right=of` graph) so the Visio layout matches the PDF.
2. **T2 — VSDX generator.** New `papers/scripts/build_visio_flowcharts.py`: read a spec, emit a valid `.vsdx` (OPC ZIP: `visio/document.xml`, `visio/pages/page1.xml` with `Shapes`/`Connects`, masters mapped to Visio flowchart shape types, per-shape text/geometry/format), written through a **deterministic zip** mirroring `_word_ooxml.write_deterministic_zip` (fixed epoch).
3. **T3 — OLE embedding in the DOCX.** Extend `build_docx.py` PostProcessor: for each in-scope flowchart, replace the `<w:drawing>` image with a `<w:object>` carrying an `o:OLEObject` (ProgID `Visio.Drawing.15`) → `word/embeddings/flowchart_<name>.vsdx`, plus an **EMF/PNG preview** (the existing render) so the DOCX displays without Visio; add the relationship, `[Content_Types].xml` override, and keep the caption/anchor binding from D1.
4. **T4 — PDF/DOCX consistency.** Render the LaTeX PDF flowchart and the VSDX from the *same* spec (keep TikZ as the PDF source and treat the spec as a transcription verified against it, or regenerate both from the spec) so structure/layout match across formats.
5. **T5 — Rebuild + reproducibility + freeze.** Rebuild DOCX ×2 (must stay bit-identical — embedded VSDX/OLE parts go through deterministic zipping); validate; manifests handled as in D1/A1 (main DOCX is a tracked file → refreeze; supplement out-of-scope).

**Validation procedure (run manually).**
```powershell
# rebuild main DOCX (and supplement if flowcharts appear there):
$env:SOURCE_DATE_EPOCH="1783641600"; python papers/scripts/build_docx.py
# generator self-test (OPC-valid package):
python papers/scripts/build_visio_flowcharts.py --check papers/figures/concept/flowchart_specs/ismgsk.json
# DOCX contains extractable Visio objects (expect >=1 .vsdx under word/embeddings):
python -c "import zipfile; z=zipfile.ZipFile('papers/DT-GSK.docx'); print([n for n in z.namelist() if n.startswith('word/embeddings/') and n.endswith('.vsdx')])"
# extract one to open directly in Visio:
python -c "import zipfile; z=zipfile.ZipFile('papers/DT-GSK.docx'); open('flowchart_ismgsk.vsdx','wb').write(z.read('word/embeddings/flowchart_ismgsk.vsdx'))"
# reproducibility (build twice, hashes identical):
$env:SOURCE_DATE_EPOCH="1783641600"; python papers/scripts/build_docx.py; (Get-FileHash papers/DT-GSK.docx).Hash
python papers/scripts/validate_docx.py papers/DT-GSK.docx
```
Then a **manual Visio check** (only the author can do this — no Visio in the build environment): open the DOCX in Word, double-click a flowchart → it opens in Visio; confirm shapes/connectors/text/line-weights are individually editable and the layout matches the PDF; also open the extracted `flowchart_ismgsk.vsdx` standalone.

**Testing requirements.** Generator emits OPC-valid `.vsdx` (Visio opens without repair); DOCX carries one extractable `.vsdx` per in-scope flowchart under `word/embeddings/`; DOCX rebuilds **bit-identical ×2**; `validate_docx.py` stays `markers_left: 0`; the embedded preview renders in Word without Visio; Visio round-trip preserves shapes/connectors/text/formatting/layout (manual).

**Deliverables.** `flowchart_specs/*.json`; `build_visio_flowcharts.py`; per-flowchart `.vsdx` embedded in and extractable from the DOCX; updated `build_docx.py` OLE path; refreeze/commit.

**Acceptance criteria.** Each in-scope flowchart is fully editable in Microsoft Visio both in-place (double-click in Word) and as an extracted `.vsdx`; semantic structure (shapes + connectors), text, formatting (incl. the bold ISM-adds convention), and layout are preserved and match the PDF; DOCX deterministic ×2; validators pass.

**Risks.** (R1) VSDX authoring is intricate — Visio is strict and may reject a malformed OPC package. (R2) OLE/VSDX binary parts can carry timestamps/GUIDs that break byte-reproducibility. (R3) No in-environment Visio → editability is author-verified only. (R4) Heavy effort on a companion artifact (submission is LaTeX per A0-1). (R5) Spec-derived positions may drift from the TikZ/PDF layout.
**Mitigations.** (R1) Template the XML from a minimal known-good `.vsdx` authored once in Visio and unzipped, so the package shape is Visio-blessed; the flowcharts' clean term/proc/decision styles map to Visio flowchart masters. (R2) Route all zipping through `write_deterministic_zip` (fixed epoch); strip/fix GUID/timestamp fields; verify with the two-build hash diff, bisecting parts. (R3) Gate acceptance on the author's manual Visio confirmation (like D3's Word pass); deliver the extractable `.vsdx` so it is one double-click. (R4) Offer **Tier V-C** as a cheaper interim (standalone `.vsdx`) and escalate to V-A only if in-DOCX extraction is required. (R5) Derive positions from the compiled PDF coordinates and diff the VSDX render against the PDF at 150 dpi.
**Rollback.** `git revert` the D4 commit → DOCX reverts to raster-PNG flowcharts (D1 state); the `.json` specs and generator are additive and can stay for a later retry.

**Completion checklist.** *(status 2026-07-13)*
- [x] Flowchart specs authored (T1) — **ismgsk + gsk** both done (gsk adds `dx` fork/join + left-placed End)
- [x] VSDX generator emits deterministic, structurally-valid `.vsdx` (T2) — `build_visio_flowcharts.py`; ismgsk 17+17, gsk 11+12; both bit-identical ×2; OPC/XML valid; handles vertical/elbow/fork/join/horizontal/right-rail routes. **Visio round-trip NOT yet confirmed (no Visio in build env)**
- [x] DOCX embeds extractable `.vsdx` + preview per flowchart (T3) — both `.vsdx` under `word/embeddings/`, 2 `w:object` OLE (ProgID `Visio.Drawing.15`), PNG previews preserved, 0 leftover bitmaps, validator `markers_left:0`/no warnings
- [x] PDF/DOCX structure consistent (T4) — specs are faithful transcriptions of the TikZ (same nodes/edges/text/order); exact pixel-match to the PDF not attempted (editable diagram, acceptable). PDF flowcharts stay TikZ (unchanged)
- [~] Reproducible ×2; validators pass (T5) — OLE build is **OPT-IN** (`VISIO_OLE_FLOWCHARTS` env). **First author test FAILED: the OLE flowcharts showed as static images in Word.** Submission `DT-GSK.docx` **reverted to known-good PNG** (12/12, back to pre-D4 `5a508ea6`); OLE debugged on separate `DT-GSK_visio.docx`. **Fix applied:** canonical `_x0000_t75` VML shapetype (the likely cause Word rendered it as an image) — **awaiting re-test**
- [ ] **Word+Visio round-trip on `DT-GSK_visio.docx`** ← retest gate: does double-click now open Visio? (need author diagnostics if still failing)
- [ ] fold OLE into default build + refreeze — only AFTER the round-trip is confirmed
- [ ] (opt) extension diagrams (architecture, dim-gating, sgsm-mechanism, taxonomy)

---

# PART C — Submission packaging & final gate

**Objective.** Assemble the exact files the venue requires and run the last integrity gate.

**Prerequisites.** A4 complete; Part B complete or explicitly out of scope.

**Dependencies.** All prior phases.

**Step-by-step tasks.**
1. **T1 — Author-side closure (👤).** Real ORCIDs, submission account, cover-letter `[AUTHOR TO FILL]`, suggested reviewers.
2. **T2 — Package (🤖).** Assemble: main PDF/DOCX, supplement PDF/DOCX, cover letter, source bundle + DOI, and the reproducibility/freeze manifests.
3. **T3 — Final gate (run manually).**
```powershell
$env:SOURCE_DATE_EPOCH="1783468800"; $env:FORCE_SOURCE_DATE="1"; python papers/scripts/build_pdf.py
$env:SOURCE_DATE_EPOCH="1783468800"; $env:FORCE_SOURCE_DATE="1"; python papers/scripts/build_supplementary.py --rebuild-bib
Remove-Item Env:FORCE_SOURCE_DATE -ErrorAction SilentlyContinue; $env:SOURCE_DATE_EPOCH="1783641600"; python papers/scripts/build_docx.py
$env:SOURCE_DATE_EPOCH="1783641600"; python papers/scripts/build_docx.py --supplementary
python papers/scripts/check_manifest.py
python papers/scripts/validate_docx.py papers/DT-GSK.docx
python papers/scripts/validate_docx.py papers/supplementary.docx
```

**Deliverables / acceptance / rollback.** Complete submission package; final gate green (12/12, validators pass, determinism ×2); residual items author-side only. Rollback = `git revert` the packaging commit (artifacts regenerate deterministically).

**Completion checklist.** [ ] author-side items filled [ ] package assembled [ ] final gate green [ ] committed (no push) [ ] 👤 submit

---

## Appendix — Command quick-reference (all with 12 workers where parallel)

| Purpose | Command |
|---|---|
| Smoke test isolation | `python run.py --config configs/_ablation/overlay_full_cec2017.yml --dimensions 50 --runs 3 --workers 12 --output-root results/_smoke` |
| Full ISM isolation (4 cells) | `python run.py --config configs/_ablation/overlay_full_cec2017.yml --workers 12` (repeat for `no_sgsm`, `no_adaptive`, `no_finalpolish`; add `--runs 51` for full power) |
| Scaffold ablation | `python scripts/run_ablation.py --suite cec2017 --dimension 50,100 --runs 25 --workers 12` |
| Boundary dims *(out of scope for Q2)* | `python run.py --optimizer dt-gsk --suite cec2017 --dimensions 20,40,49,51,75,99,101 --runs 51 --workers 12 --output-root results/_boundary` |
| Aggregate isolation | `python papers/scripts/generate_ablation_matrix.py --ablation-root benchmarks/cec_reference_results/_ablation/overlay --suite cec2017 --dimension 50 --full-cell full` |
| Promote to reference tree | `robocopy results\_ablation_sgsm_cec2017 benchmarks\cec_reference_results\_ablation\overlay /E` |
| Main PDF | `$env:SOURCE_DATE_EPOCH="1783468800"; $env:FORCE_SOURCE_DATE="1"; python papers/scripts/build_pdf.py` |
| Main DOCX | `$env:SOURCE_DATE_EPOCH="1783641600"; python papers/scripts/build_docx.py` |
| Supplement PDF | `$env:SOURCE_DATE_EPOCH="1783468800"; $env:FORCE_SOURCE_DATE="1"; python papers/scripts/build_supplementary.py --rebuild-bib` |
| Supplement DOCX | `$env:SOURCE_DATE_EPOCH="1783641600"; python papers/scripts/build_docx.py --supplementary` |
| DOCX validators | `python papers/scripts/validate_docx.py papers/DT-GSK.docx` |
| Manifest gate | `python papers/scripts/check_manifest.py` |
| Repro hash | `(Get-FileHash papers/DT-GSK.docx -Algorithm SHA256).Hash` |

**Dependency graph:** A0 → {A1 ∥ A2} → A3 → A4 → C. Part B (D1✅ → D2 → D3; **D4 Visio-flowcharts** branches off D1, independent of D2/D3) branches from A0.T5 and merges at C.
