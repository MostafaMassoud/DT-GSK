# Evidence, Provenance and Reproducibility Audit

**Seat:** `s7-12_evidence_repro` (Stages 7 + 12) · Lead role R5 · Lead team T3-STAT
**Governing prompt:** `papers/PAPER_REVIEW_PROMPT.md` — Stage 7 (L1689–1740), Stage 12 (L2081–2154), ticket schema §5.4 (L1104–1148), DT-GSK profile §10 (L3160–3522), prohibited shortcuts §15 (L3977)
**Date:** 2026-07-22
**Mode:** read-only on manuscript, code and evidence. Every write went to `papers/review_2026_07_22/` or the session scratchpad.

---

## 0. Package state as verified (not as asserted)

| Item | Asserted in brief | Verified in repo | Status |
|---|---|---|---|
| git HEAD | `45248eb31` | `45248eb31af7b01567c251f2a5da4f36e92d6030` — *"papers: state budget-crossing fairness verification in the manuscript; re-mint freeze"* (2026-07-22) | OK |
| manuscript freeze anchor | `abd2fa2f25c8` | manifest field says `abd2fa2f25c8…`, **but the frozen bytes are at `45248eb31`** | **DEFECT — E-01** |
| `check_manifest` | 15/15 | `15/15 match []` (exit 0) against the working tree | OK (working tree only — see E-02) |
| evidence release | `rel-2026-07-20-67d9345f9` | `evidence_release_manifest.json` `release_id`/`anchor_commit` match; 3,403 files / 712,437,624 B | OK |
| DT-GSK.pdf / supplementary.pdf / cover_letter.pdf | 39 / 61 / 2 pp | 39 / 61 / 2 pp (pypdf) | OK |
| DOCX main + supplement | present | `DT-GSK.docx` 1,037,004 B; `supplementary.docx` 8,735,071 B | OK |

Rendered-artifact SHA-256 (recomputed):

```
DT-GSK.pdf         3436276946abd7ddb44eb0ca58ded930751d031041bcc689fb60b70430b14450
supplementary.pdf  9d0d3cf9e64b8156002926e6600fa4a29000386aa9f32f8b622f0daa1f20dc75
cover_letter.pdf   7313e38fe62a07717c47597b7fd4fe023654a849af242707279b7be572353abd
DT-GSK.docx        1ad8c3b2129b1f652e975729339eb1a299abcd596d319b56b1a287ac11f124da
supplementary.docx a9a64295278f67db5d713b5c803677e0a3cdfe41476a345abf5239fddb30618d
```

---

## 1. Reproducibility scorecard

### 1.1 Scholarly levels (Stage 12 §"Reproducibility levels")

| Level | Verdict | Evidence |
|---|---|---|
| 1. Computational repeatability | **Supported for the evidence and analysis layers; NOT supported for the source-freeze layer** | 3,403/3,403 release checksums recompute; 130/130 analysis-bundle checksums recompute; but a clean-room materialization reproduces only 10/15 freeze-manifest files (E-02) |
| 2. Independent analytical replication | **Not attempted by the project; not claimed** | No independent reimplementation of the statistics exists in the package. Correctly not claimed. |
| 3. Method reproducibility | **Supported** | Seed formula, strides, generator, budgets, run counts, F2 exclusion and pairing all specified and independently re-derived here (§3.3) |
| 4. Empirical replicability | **Partially supported** | `runbook.md` §1 documents the three campaigns with exact flags; but the documented pipeline does not regenerate the controlled analysis bundle, the tables, or the Word deliverable (E-04) |
| 5. Generalizability | **Correctly not claimed** | Manuscript bounds itself to the family panel, suites, budgets and D ≤ 100 |

### 1.2 Project determinism contract (§10.3 / Stage 12 determinism-contract audit)

`papers/governance/reproducibility_manifest.json` exists and records per-artifact-class delivery levels — **but the record is bound to `rel-2026-07-10-262fc16c9`, two releases behind the shipped package, and its recorded artifact hashes are superseded** (E-03).

| Artifact class | Recorded level | Recorded evidence | Holds at review time? |
|---|---|---|---|
| immutable primary evidence | byte_for_byte | SHA-256 manifests | **YES** — independently re-verified, 0/3403 mismatch |
| derived analysis bundle | analytical + byte_for_byte | `phase_06/determinism_check.md` | Plausible, but the recorded evidence is for the 07-10 bundle, not the shipped 07-20 bundle |
| latex tables | visual + byte_for_byte | `generate_latex_tables.py` regenerates T01–T16 | Not re-run here (would write to the repo); `artifact_binding.csv` output checksums all match on disk |
| figures | visual + byte_for_byte | deterministic vector PDFs | Not re-run here; binding checksums match |
| main_pdf | byte_for_byte after ts-normalization, sha `503692de…` | double build 2026-07-12 | **NO** — shipped PDF is `3436276946…`; the recorded hash is three rebuilds stale |
| main_docx | byte_for_byte, sha `993fe08a…` | double build 2026-07-12 | **NO** — shipped DOCX is `1ad8c3b2…` |
| ablation evidence | byte_for_byte | `_ablation/manifest.json`, 1032 files | Manifest now lists 1,297 files (51-run re-mint); record stale |

`double_rebuild_contract.status = "MET"`, `verified_2026_07_12: true` — i.e. the double-rebuild attestation predates **two** evidence releases, the C006/M038 code fixes, the 51-run regeneration and the 2026-07-21/22 remediation. Under Stage 12 Gate L (*"fails when … the producing project's recorded delivery levels are missing or unsupported by rebuild evidence"*) this is a **FAIL as recorded**, remediable by a refresh rather than by new science.

---

## 2. Verified-clean findings (recorded so the panel does not re-litigate them)

These are the strongest parts of the package. Each was independently recomputed, not accepted on assertion.

1. **Full release checksum re-verification.** All 3,403 files / 712,437,624 bytes of `rel-2026-07-20-67d9345f9` re-hashed against `evidence_release_manifest.json`: **0 missing, 0 mismatch** (3.1 s).
2. **Analysis-bundle checksum re-verification.** All 130 entries of `papers/analysis/rel-2026-07-20-67d9345f9/analysis_checksums.sha256`: **0 mismatch**.
3. **Exhibit binding integrity.** All 59 rows of `papers/governance/artifact_binding.csv`: **0 source-checksum mismatches, 0 output-checksum mismatches**; 50/59 rows carry `evidence_release_id = rel-2026-07-20-67d9345f9`, the remaining 9 are `n/a (authored; no empirical source)`.
4. **Evidence-boundary proof (§10.3).** `source_use_log.json` for all three suites: 847 + 224 + 168 = **1,239 file opens, 0 outside `benchmarks/cec_reference_results/`**, `strict_source: true`, `status: ok`. `source_precheck.json` records passing negative tests (a `results/_run_all` open raises `StrictSourceViolation`). No silent staging fallback in the publication analysis path.
5. **Coverage and count reconciliation (§10.4).** Recomputed from `per_run.csv` for all 21 (suite × optimizer) cells:
   - CEC2017: 116 cells (29 functions × D10/30/50/100) × 51 runs = **5,916 rows for each of the seven optimizers**; function set `{1,3..30}` confirms the **F2 exclusion**.
   - CEC2013: 84 cells (28 × D10/30/50) × 51 = **4,284 rows each**.
   - CEC2011: 22 native problems × 25 = **550 rows each**; native dimensions D∈{1,6,7,12,13,15,20,22,26,30,40,96,120,126,140,240}.
   - **0 duplicate seeds** in any cell; **0 NaN/Inf** in `error` for CEC2017/CEC2013. CEC2011 `error = NaN` for all rows is by design (no known optimum; `statistics_basis` is raw best fitness) — consistent with the manuscript's stated CEC2011 endpoint.
6. **Pairing-key validity (§10.7).** For every suite, the seed at each `(function, dimension, run)` key is **identical across all seven optimizers** (0 differences over 5,916 + 4,284 + 550 keys). Paired tests are legitimately paired.
7. **Seed schedule.** The printed supplement formula (Eq. `eq:supp-seed`, `supplementary.tex:998–1002`) — `(20240620 + 1000003·D + 1000033·f + 1000037·r) mod 2147483646 + 1` — was re-derived against 32,250 released rows: **exact match, 0 deviations**. The released `run_config.json` `seed_scheme` string carries the same formula including the `+ 1`. *(I initially flagged an off-by-one; that was my own truncation of the JSON string. Withdrawn — no defect.)*
8. **RNG uniformity.** All 36 `run_config.json` and all 36 `environment.json` in the release record `rand_generator = threefry`. The supplement's *"the counter-based threefry generator in every panel cell"* is exact.
9. **R-03 closed correctly.** OMML scan of both DOCX: `DT-GSK.docx` 3,610 `<m:t>` runs, `supplementary.docx` 2,220 — **0 containing a literal `&`**. Native tables present (17 and 26 `w:tbl`).
10. **R-07 closed correctly.** `validate_provenance_claims.py` exits 0 with 15 explicit `ok` lines, and `--self-test` passes 4/4 including two designed-to-fail shapes (pronoun escape, derive-from + anchor). The gate can fail.
11. **R-14 closed correctly.** `tests/regression/test_budget_crossing_semantics.py` is tracked, 5,901 B, **14 tests pass**.
12. **Other gates re-run green:** `validate_build_hygiene` exit 0; `validate_document_consistency` exit 0 (the attestation's whitelisting of exit 2 is not exercised today); `validate_runtime_provenance` exit 0 (single host, single worker count, 0.0 h panel span — the DT-GSK-only runtime table is genuinely single-session, so RT-001 is discharged by scoping the table to DT-GSK); `validate_cross_format_parity` **579 rows, 0 FAIL**.
13. **No provenance-token leakage into the main deliverables (§10.17.4).** Text extraction of `DT-GSK.pdf` and `cover_letter.pdf`: **0 `rel-…` identifiers, 0 `-dirty` strings**. The supplement carries the release ids deliberately and in one place (§S "Evidence provenance"), which §10.17.4 expressly permits.

---

## 3. Findings

Severity/priority/confidence per §§5.1–5.3; schema per §5.4.

### E-01 — Freeze anchor commit does not contain the frozen bytes

```text
ticket_id: E-01
review_stage: 7 / 12
reviewer_role: R5 (T3-STAT)
severity: Major
priority: P1
confidence: High — CONFIRMED
issue_type: reproducibility
manuscript_location: papers/governance/main_manuscript_freeze_manifest.json:5 ; papers/governance/submission_package_manifest.json:8
claim_id_or_artifact_id: main_manuscript_freeze_manifest / submission_package_manifest
concise_issue: Both manifests name abd2fa2f25c8… as the anchor/authoritative commit, but four of the fifteen frozen files were changed by the LATER commit 45248eb31 and exist in their frozen form only there.
exact_evidence_or_observation: |
  Normalized (line-ending-insensitive) comparison of each manifest file against the declared anchor:
      papers/sections/performance.tex          CONTENT-DIFFERS-AT-ANCHOR (anchor 6d7b62580e22 vs frozen fd7dbbaca981)
      papers/DT-GSK.pdf                        CONTENT-DIFFERS-AT-ANCHOR (anchor 5d1f095b1963 vs frozen 3436276946ab)
      papers/DT-GSK.docx                       CONTENT-DIFFERS-AT-ANCHOR (anchor 647028d53474 vs frozen 1ad8c3b2129b)
      papers/governance/citation_usage_map.csv CONTENT-DIFFERS-AT-ANCHOR (anchor c68c4d2829b6 vs frozen 45798b35b522)
  All four match HEAD (45248eb31). `git show --stat HEAD` confirms 45248eb31 rewrote DT-GSK.pdf, DT-GSK.docx,
  citation_usage_map.csv, performance.tex, main_manuscript_freeze_manifest.json and submission_package_manifest.json.
  The manifest's own freeze_statement acknowledges the change ("Amended 2026-07-22: performance.tex states …")
  but the anchor_commit field was not advanced.
root_cause: The R-14 amendment commit re-minted the file hashes inside the manifest but left the commit-identity fields at their pre-amendment value.
scientific_or_editorial_justification: §10.3 requires the source release ID and checksums to be recorded; Stage 12 requires "repository cleanliness and release tags" and archived source sufficient for future revision. An anchor that does not materialize the artifact it anchors is not a provenance record.
impact_on_validity_or_acceptance: No reported number changes. But an editor or archivist checking out the declared anchor obtains a manuscript that fails the project's own check_manifest 4/15, and the submission package manifest points at the wrong commit. This is the exact "contradictory source metadata" pattern Stage 7 check 14 exists to catch.
required_correction: Set anchor_commit / authoritative_commit to the commit that contains the frozen bytes (or re-freeze at a new commit and stamp it), and re-run check_manifest plus a `git show <anchor>` spot check of at least performance.tex, DT-GSK.pdf and DT-GSK.docx before stamping.
acceptable_alternatives: Add an explicit `amended_at_commit` field naming 45248eb31 and state in freeze_statement that anchor_commit refers to the pre-amendment freeze; this is weaker but auditable.
additional_evidence_needed: none
dependencies: E-02 (the byte-identity check itself must be made platform-stable first, or the corrected anchor will still not verify off this machine)
expected_improvement: Gate A / Gate L package-integrity evidence becomes checkable by a third party.
post_revision_verification: `git show <anchor>:…` reproduces all 15 manifest hashes (binary files exactly; text files after the E-02 fix).
status: open
```

### E-02 — The freeze manifest is not reproducible from the repository (clean-room 10/15)

```text
ticket_id: E-02
review_stage: 12
reviewer_role: R5 (T3-STAT)
severity: Major
priority: P1
confidence: High — CONFIRMED
issue_type: reproducibility
manuscript_location: papers/governance/main_manuscript_freeze_manifest.json (files[]) ; repository root (.gitattributes absent)
claim_id_or_artifact_id: byte-for-byte delivery level for the source/governance artifact class
concise_issue: The 15 freeze-manifest SHA-256 values pin the working tree's byte state, which the repository does not restore. A clean-room materialization of HEAD reproduces only 10 of 15.
exact_evidence_or_observation: |
  Clean-room test (git archive HEAD -- papers | tar -x into the scratchpad; nothing written to the repo):
      CLEAN-ROOM (git archive HEAD) check_manifest equivalent: 10/15 match
         papers/main.tex                     HASH-MISMATCH
         papers/sections/introduction.tex    HASH-MISMATCH
         papers/sections/related_work.tex    HASH-MISMATCH
         papers/sections/performance.tex     HASH-MISMATCH
         papers/sections/conclusions.tex     HASH-MISMATCH
  Mechanism: `git config core.autocrlf` = true and there is NO .gitattributes anywhere in the repo
  (checked repo root and project root). The working tree is in a MIXED state:
      main.tex                      crlf=0   lf=336    <- LF on disk
      sections/proposed_algorithm.tex crlf=793 lf=0    <- CRLF on disk
      references.bib                crlf=675 lf=0
      governance/*.csv (3 files)    CRLF on disk
  git archive emits CRLF for every text file, so the five LF-on-disk files mismatch; a Linux/macOS
  checkout emits LF for every text file, so the OTHER five (proposed_algorithm.tex, references.bib,
  claims_evidence_matrix.csv, citation_usage_map.csv, artifact_binding.csv) would mismatch instead.
  All five binary artifacts (DT-GSK.pdf/.docx, supplementary.pdf/.docx, cover_letter.pdf) match in
  every materialization — the defect is confined to text sources and governance CSVs.
  Content check: every one of the 15 files is normalized-equal to HEAD, so no content is lost.
root_cause: SHA-256 pins were taken over a working tree whose line endings are an accident of edit history, with no .gitattributes to make the checked-out byte state deterministic.
scientific_or_editorial_justification: Stage 12 requires "archived source sufficient for future revision", "source/evidence checksums" and a clean-room build that works outside the authors' workspace ("A process that works only in the authors' original workspace is not independently reproducible"). §10.3 requires a recorded byte-for-byte delivery level to be supported by rebuild evidence.
impact_on_validity_or_acceptance: No scientific content is affected — the shipped PDFs and DOCX are byte-reproducible and content is preserved. But the project's headline integrity control (check_manifest 15/15) is a machine-local property, and the recorded byte-for-byte level for the source class is unsupported off this host.
required_correction: Add a repository .gitattributes fixing the eol of the manifest-pinned text files (e.g. `*.tex text eol=lf`, `*.bib text eol=lf`, `papers/governance/*.csv text eol=crlf` — whichever matches the minted hashes), normalize the working tree to that policy, re-mint the manifest, then re-run the clean-room extraction and require 15/15.
acceptable_alternatives: Narrow the manifest's recorded delivery level for the text class from byte-for-byte to "byte-for-byte after line-ending normalization", and change check_manifest to hash text files after normalizing CRLF→LF. This preserves the guarantee that matters (content identity) and is honest about what is pinned.
additional_evidence_needed: none
dependencies: E-01 (fix together — one re-mint should settle both)
expected_improvement: The reproducibility manifest's byte-for-byte claim becomes true for a third party on any platform; Gate L clean-room criterion becomes satisfiable.
post_revision_verification: `git archive HEAD -- papers | tar -x` into a clean directory, run check_manifest there, require 15/15; repeat with `core.autocrlf=input` to prove platform independence.
status: open
```

### E-03 — The determinism-contract record is bound to a superseded release and superseded hashes

```text
ticket_id: E-03
review_stage: 12 (§10.3 determinism contract)
reviewer_role: R5 (T3-STAT)
severity: Major
priority: P1
confidence: High — CONFIRMED
issue_type: reproducibility
manuscript_location: papers/governance/reproducibility_manifest.json:435–488 (phase12_reproducibility block)
claim_id_or_artifact_id: REPRODUCIBILITY_PACKAGE (§10.1 binding)
concise_issue: The mandated per-artifact-class delivery-level record names evidence_release rel-2026-07-10-262fc16c9, ablation_release abl-rel-2026-07-11, and PDF/DOCX hashes that are three rebuilds stale; its double-rebuild attestation is dated 2026-07-12.
exact_evidence_or_observation: |
  reproducibility_manifest.json (last block, no later block supersedes it):
      "evidence_release": "rel-2026-07-10-262fc16c9"     (current: rel-2026-07-20-67d9345f9)
      "ablation_release": "abl-rel-2026-07-11"           (current: abl-rel-2026-07-20)
      main_pdf.sha256  = 503692de16b6ef5b…                (shipped: 3436276946abd7dd…)
      main_docx.sha256 = 993fe08ab784b543…                (shipped: 1ad8c3b2129b1f65…)
      ablation_evidence evidence = "_ablation/manifest.json = 1032 files"
                                                          (actual manifest: files list len=1297)
      "double_rebuild_contract": {"status":"MET","verified_2026_07_12": true}
  Meanwhile §10.3 requires this file to "agree with the release checksums recorded under section 10.3",
  and papers/governance/evidence_release_manifest.json + main_manuscript_freeze_manifest.json both
  correctly carry rel-2026-07-20-67d9345f9.
root_cause: The Phase-12 delivery-level block was written once (2026-07-12) and was not refreshed by the two subsequent evidence re-mints or by the 2026-07-21/22 remediation re-freezes.
scientific_or_editorial_justification: Stage 12 Gate L fails when "the producing project's recorded delivery levels (analytical / visual / byte-for-byte) are missing or unsupported by rebuild evidence." §10.3 makes agreement with the release checksums an explicit obligation.
impact_on_validity_or_acceptance: The one artifact a reviewer would open to check the determinism contract disagrees with every other manifest in the package. It is also the file that would be cited if the journal asked for a reproducibility statement.
required_correction: Add a phase-13 (or "post-remediation") block recording, for the SHIPPED release: evidence_release rel-2026-07-20-67d9345f9, ablation abl-rel-2026-07-20, the current PDF/DOCX SHA-256 values, the current _ablation file count, and a dated double-rebuild result for the current artifacts. Retain the 07-12 block marked superseded (never edit it in place — §10.3 supersession rule).
acceptable_alternatives: none — this is the mandated record for the mandated control.
additional_evidence_needed: A fresh double build of DT-GSK.pdf and DT-GSK.docx under SOURCE_DATE_EPOCH=1783468800 / 1783641600 to substantiate the byte-for-byte level for the current artifacts. This is a rebuild, not a re-run, and does not violate the "no rerun / no new evidence release" constraints.
dependencies: E-01, E-02
expected_improvement: Gate L moves from FAIL-as-recorded to PASS.
post_revision_verification: Every release id and hash in reproducibility_manifest.json resolves to a file that exists on disk with that hash; double-build evidence carries a 2026-07-2x date.
status: open
```

### E-04 — The reproduction runbook named by the Data Availability Statement does not reproduce the paper

```text
ticket_id: E-04
review_stage: 12
reviewer_role: R5 (T3-STAT)
severity: Major
priority: P1
confidence: High — CONFIRMED
issue_type: reproducibility
manuscript_location: runbook.md:60–115 ("Full Paper Pipeline (in order)") ; cited from papers/main.tex:246–248
claim_id_or_artifact_id: CN-02 (Data Availability / reproducibility pointer)
concise_issue: The manuscript directs readers to runbook.md as "the commands that reproduce the experiment grid and the analysis outputs". That pipeline names a superseded release, omits the three commands that actually produce the shipped statistics, tables and Word file, and includes three commands that cannot run.
exact_evidence_or_observation: |
  (a) Superseded release id in an authority position:
      runbook.md:100  "# --- 6. Tables (read frozen, checked-in evidence: benchmarks/cec_reference_results/_paper_tables/
                       #     and papers/analysis/rel-2026-07-10-262fc16c9/ — not results/ staging) ---"
      The shipped tables bind to papers/analysis/rel-2026-07-20-67d9345f9/ (artifact_binding.csv, 50 rows).
      This is the same defect class as R-06, un-remediated in runbook.md.
  (b) Missing from the "complete data-to-PDF sequence" (grep count over runbook.md = 2 hits total for the
      four names, both incidental):
        - papers/scripts/phase6_run_analysis.py   <- the SOLE sanctioned producer of papers/analysis/<release_id>/
                                                     (source_use_log/analysis_manifest both record it as the generator)
        - papers/scripts/build_docx.py            <- the Word deliverable required by §10.12
        - papers/scripts/check_manifest.py and every papers/scripts/validate_*.py gate
          (runbook §8 "Quality gates" lists only pytest, ruff, validate_profile_lock, build_docs_html)
  (c) Step 3 "Statistical panels" documents `python -m gsk_family.cli.stats …`, which writes the analysis PNGs/CSVs
      to results/_run_all/_analysis/ — staging, explicitly inadmissible under §10.3/§10.11. Following the runbook
      therefore produces staging statistics and never regenerates the controlled bundle the tables read.
  (d) Commands that cannot run: runbook.md:95 generate_trace_figures.py and :97 generate_adaptive_params_panel.py
      read `results/dt-gsk/...`. Verified: `ls results/dt-gsk` -> "No such file or directory"; results/ contains only
      _ablation, _ablation_sgsm_51, _ablation_sgsm_cec2017_51, _finalize, _run_all, paper_tables. Their outputs are
      absent (papers/figures/traces/ contains only .gitkeep) and governance already marks them BLOCKED/ORPHAN
      (table_figure_source_map.csv rows FIG-trace-ace / FIG-trace-adaptive). runbook.md carries no such note.
  (e) runbook.md:76 documents the ablation campaign at `--runs 25`; the promoted ablation release abl-rel-2026-07-20
      is the 51-run re-mint (§10.10). Tracked as a pending narrative edit, but shipped as-is.
  (f) runbook.md:97 also documents generate_review_pack.py, which the project's own Phase-11 gate note describes as
      "reads staging; excluded from submission evidence chain".
root_cause: runbook.md is an engineering-era document that was never re-cut against the Phase-6/7/9 publication pipeline, while the manuscript began citing it as the reproduction record.
scientific_or_editorial_justification: Stage 12 requires "exact commands for experiments, analyses, figures, tables, PDF, and Word" and "clean-room build or execution instructions"; §10.11 forbids exhibit generators reading staging; §10.3 forbids any publication analysis resolving outside the immutable release.
impact_on_validity_or_acceptance: A referee who tries the documented path gets staging statistics, no controlled analysis bundle, no Word file, two hard failures, and a pointer to a two-generation-old release. This is the single most likely reproducibility complaint a Q1/Q2 referee will raise, and it is cheap to fix.
required_correction: |
  Add a short, authoritative "Reproduce the published artifacts" section (in runbook.md or a new
  papers/REPRODUCE.md that the DAS cites instead), listing exactly:
      python papers/scripts/phase6_run_analysis.py
      python papers/scripts/generate_latex_tables.py --skip-ablation
      python papers/scripts/generate_t16_bca.py
      python papers/scripts/build_pdf.py
      python papers/scripts/build_supplementary.py
      python papers/scripts/build_docx.py
      python papers/scripts/check_manifest.py
      python papers/scripts/validate_provenance_claims.py
      python papers/scripts/validate_cross_format_parity.py
      python papers/scripts/validate_document_consistency.py
      python papers/scripts/validate_docx.py papers/DT-GSK.docx
      python papers/scripts/validate_docx.py papers/supplementary.docx
  Correct runbook.md:100 to rel-2026-07-20-67d9345f9; correct :76 to --runs 51; delete or explicitly mark
  BLOCKED the three staging commands at :95, :97 and the review-pack line; label the §3 cli.stats block as
  "engineering/staging analysis — NOT the published statistics".
acceptable_alternatives: Keep runbook.md as the engineering runbook and have the DAS cite the new REPRODUCE.md, provided runbook.md's stale release id and n=25 are still corrected.
additional_evidence_needed: none
dependencies: none
expected_improvement: Gate L clean-room criterion becomes satisfiable from documentation alone.
post_revision_verification: A reader following only the new section reaches papers/analysis/rel-2026-07-20-67d9345f9/, papers/tables/T01–T16.tex, all three PDFs, both DOCX, and 15/15 on check_manifest.
status: open
```

### E-05 — Data Availability Statement asserts public availability with no locator

```text
ticket_id: E-05
review_stage: 12
reviewer_role: R5 (T3-STAT)
severity: Major
priority: P2
confidence: High — CONFIRMED (the absence); Medium — SUSPECTED (whether the repository is in fact public)
issue_type: compliance
manuscript_location: papers/main.tex:227–235 (Data Availability Statement); rendered DT-GSK.pdf p.35–36
claim_id_or_artifact_id: CN-02
concise_issue: The statement says the implementation, harness, per-run CSVs, seed schedules and manifests "are publicly available in the DT-GSK repository", but no URL, DOI, accession or repository name appears anywhere in the manuscript, supplement or cover letter.
exact_evidence_or_observation: |
  Text extraction of DT-GSK.pdf and cover_letter.pdf: 0 matches for any URL, DOI, github, zenodo or OSF token.
  grep over papers/supplementary.tex: the word "repository" appears at :1136, :1722, :1767, :1797 — always
  as a bare noun, never with a locator.
  papers/main.tex:232 carries the author-side marker in a comment:
      "% AG-0006 / R-0004: the durable archive URL/DOI and the submission account
       % are author-side items; do not fabricate a URL here."
  The underlying data IS present and tracked: git ls-files counts 4,724 tracked files under
  benchmarks/cec_reference_results and 347 under papers/analysis — so the claim is substantively
  true IF the repository is public. I cannot verify the repository's visibility from here; the only
  remote recorded is https://github.com/MostafaMassoud/PhD-Projects.git, a multi-project repository.
root_cause: The durable archive step (Zenodo/OSF deposit) is deliberately deferred to the author, but the present-tense availability sentence was written as if it had already happened.
scientific_or_editorial_justification: Stage 12 requires verifying "whether data/code availability claims are true at review time"; §10.17.4 expressly sanctions ONE precise archival identifier in the Data-Availability statement as the correct place for it. MDPI Algorithms requires a Data Availability Statement with a link or accession for a "publicly available" declaration.
impact_on_validity_or_acceptance: As written the statement is unverifiable and, at review time, unsupported. Editors routinely desk-query this. Note also that the evidence lives inside a large multi-project repository, so even a public URL should point at a tagged release or a deposited archive, not the repository root.
required_correction: Before submission, mint a durable archive (Zenodo/OSF DOI or a tagged GitHub release restricted to the paper's artifacts) and insert exactly one identifier into the Data Availability Statement. Until then the sentence must read in the conditional/at-acceptance form rather than the present indicative.
acceptable_alternatives: "…will be deposited in a public archive upon acceptance; the DOI will be supplied at proof stage" — acceptable to most MDPI editors, and honest.
additional_evidence_needed: Author confirmation of the repository's visibility and of the intended archive.
dependencies: E-04 (the archive must contain the corrected reproduction instructions)
expected_improvement: Removes the most common desk-stage query and satisfies §10.17.4's sanctioned single-identifier pattern.
post_revision_verification: The rendered PDF contains exactly one archival identifier, resolvable, inside the Data Availability Statement.
status: open
```

### E-06 — "All seven optimizers are held to exactly the same MaxFES charge" is contradicted by the released evidence

```text
ticket_id: E-06
review_stage: 7
reviewer_role: R5 (T3-STAT)
severity: Major
priority: P2
confidence: High — CONFIRMED
issue_type: evidence
manuscript_location: papers/sections/performance.tex:169–170 and :179 ("Runs are budget-exact")
claim_id_or_artifact_id: MT-11 / PR-06 (budget fairness), R-05 remediation
concise_issue: The R-05 remediation sentence asserts a universal equal-budget charge, but AGSK and APGSK stop early on the CEC target rule in 1,845 released runs, with nfes well below MaxFES.
exact_evidence_or_observation: |
  Recomputed from the released per_run.csv termination/nfes columns:
      cec2017/agsk     target_error_reached = 404 / 5916   (max_evaluations 5512)
      cec2017/apgsk    target_error_reached = 338 / 5916
      cec2013/agsk     target_error_reached = 558 / 4284
      cec2013/apgsk    target_error_reached = 545 / 4284
      atmals-gsk, dt-gsk, egsk, fdb-agsk, gsk: max_evaluations for 100% of runs, all three suites.
  Depth of the shortfall (agsk, cec2017):
      D10   351 / 1479 early, mean nfes = 69.5% of MaxFES
      D30    53 / 1479 early, mean nfes = 50.0% of MaxFES
      D50/D100  0 early
  The project's own governance documents this and mandates disclosure:
      benchmark_protocol_audit.md:195  "1507 runs across agsk/apgsk reached error <= 1e-8 and stopped early"
      benchmark_protocol_audit.md:189  A2-003 "…also feeds the comparator-fairness/budget audit … since the
                                        other five optimizers always run to MaxFES"
      benchmark_protocol_audit_part2.md:140–144  "…it only saves wall time. The remaining five optimizers are
                                        reference-faithful full-budget runners … the cost-analysis caveat:
                                        runtime comparisons on solved cells must note agsk/apgsk early [stops]"
      benchmark_protocol_audit_part2.md:237  P2-A4 disposition: "Note in cost-analysis captions"
  grep over papers/sections/*.tex and papers/supplementary.tex for "target error", "early stop", "1e-8"
  termination: no disclosure of the asymmetric stopping rule anywhere in the manuscript.
root_cause: The R-05 fix correctly resolved the *terminal-batch overrun* question and then generalized its conclusion ("therefore held to exactly the same MaxFES charge") over a second, unrelated budget asymmetry that the governance audit had already recorded.
scientific_or_editorial_justification: §10.4 requires verifying "MaxFES and all local-search/polish objective calls" against the evidence rather than assuming the protocol; §15 forbids accepting "standard protocol" without verifying the actual protocol. A blanket fairness sentence that the shipped data contradicts is a Stage-7 prose/evidence mismatch regardless of whether it favours the authors.
impact_on_validity_or_acceptance: |
  Final-error inference is unaffected — every early stop occurs at error <= 1e-8, i.e. at the reporting floor,
  so ranks, Wilcoxon, A12, Cliff's delta and BCa are all untouched. Two real consequences remain:
    (1) the sentence is literally false and a referee who opens per_run.csv will find it in one minute;
    (2) the two disclosures the project's own audit mandated (cost-analysis note; convergence curves that end
        before MaxFES, 34 curve files across agsk/apgsk) are absent from the manuscript. The cost half is
        largely defused because tab:runtime was scoped to DT-GSK only and makes no cross-algorithm claim
        (verified: performance.tex:766 "no cross-algorithm runtime comparison is made"), but the convergence-
        caption half (§10.8: missing/short curves must never be silently omitted) is still owed.
required_correction: |
  Replace the blanket sentence with the accurate one, e.g.:
    "No optimizer is charged more than MaxFES. DT-GSK truncates before evaluating; the six reference-faithful
     ports evaluate the terminal batch in full and count only its in-budget prefix, which was verified inert
     (…). AGSK and APGSK additionally retain the CEC target-error stopping rule and therefore terminate below
     MaxFES on cells already solved to the 1e-8 floor (N runs); because those runs are at the reporting floor,
     no reported error, rank or test is affected, and no wall-clock comparison is drawn across algorithms."
  Add the §10.8 caption note wherever an AGSK/APGSK convergence curve ends before MaxFES.
acceptable_alternatives: A footnote carrying the same content, provided the false universal sentence itself is removed from the body.
additional_evidence_needed: none — the counts above are recomputed from the release.
dependencies: none
expected_improvement: Removes a checkable false statement about comparator fairness and discharges two standing governance dispositions (A2-003/A2-031/A2-034 and P2-A4).
post_revision_verification: No sentence in the manuscript asserts a universal equal-charge; the per-run counts quoted in the revised sentence reproduce from benchmarks/cec_reference_results/*/{agsk,apgsk}/per_run.csv.
status: open
```

### E-07 — Page-count gate evidence is stale by four pages; no row records the shipped artifact

```text
ticket_id: E-07
review_stage: 12 (§10.14)
reviewer_role: R5 (T3-STAT)
severity: Moderate
priority: P2
confidence: High — CONFIRMED
issue_type: compliance
manuscript_location: papers/governance/phase_gate_register.csv (Phase 8, Phase 11 rows; Phase 12 row has none)
claim_id_or_artifact_id: §10.14 page-limit hard rule
concise_issue: The register's page-count evidence describes a 35-page main PDF with B1 = 32 and "~2pp headroom" against a <=34 cap, and pins four artifact byte sizes that no longer exist. The shipped main PDF is 39 pages.
exact_evidence_or_observation: |
  Phase-11 row (timestamp 2026-07-11):
     "main DT-GSK.pdf 35 pages total / B1=32 main-text pages (excl. references pp.33-35 + back matter;
      <=34 hard cap PASS, ~2pp headroom); supplementary.pdf 32 pages. All four artifacts byte-identical to
      frozen Phase-9/10 (DT-GSK.pdf 928688; supplementary.pdf 889540; DT-GSK.docx 3061644;
      supplementary.docx 12837665)."
  Measured now:
     DT-GSK.pdf 39 pages / 695,943 B      supplementary.pdf 61 pages / 1,155,151 B
     DT-GSK.docx 1,037,004 B              supplementary.docx 8,735,071 B
  Structure of the shipped PDF (pypdf page scan): body runs to p.34; Data Availability p.35;
  Conflicts of Interest p.36; abbreviations + References begin p.37; last page 39.
  => current B1 is ~34 pages, i.e. AT the recorded <=34 cap with zero headroom, and 2 pages above the
  last recorded measurement. The Phase-12 row (state FROZEN, timestamp 2026-07-22) contains no
  page-count measurement at all.
root_cause: The page-count rows were written at the pre-ablation freeze and were not re-measured when Phase 12 added the ablation supplement, the CEC2013 material and the 2026-07-21/22 remediation content.
scientific_or_editorial_justification: §10.14 requires page counts "measured from the compiled PDF at the Phase 8/9/11 gates, with a page-count row recorded in phase_gate_register.csv for each of those gates" and requires "the measured page-count evidence is recorded in the review record".
impact_on_validity_or_acceptance: No scientific impact. But the register currently attests a headroom that no longer exists, and if the <=34 B1 cap is a real constraint the manuscript is now sitting exactly on it, with no gate row demonstrating compliance.
required_correction: Add a page-count row to the Phase-12 register entry recording the shipped measurement (39 pp total, B1 as measured, supplement 61 pp) and the four current byte sizes, and re-state the cap verdict against it. Mark the Phase-11 numbers as historical rather than current.
acceptable_alternatives: none
additional_evidence_needed: Author confirmation of whether the <=34 B1 cap remains binding (Algorithms publishes no hard page limit; the cap appears to be a project self-imposed budget from the Phase-4 page budget).
dependencies: none
expected_improvement: §10.14 evidence becomes checkable against the artifact actually being submitted.
post_revision_verification: The register's most recent page-count row matches `len(pypdf.PdfReader('papers/DT-GSK.pdf').pages)`.
status: open
```

### E-08 — The all-green environment attestation predates the frozen state

```text
ticket_id: E-08
review_stage: 12
reviewer_role: R5 (T3-STAT)
severity: Moderate
priority: P2
confidence: High — CONFIRMED
issue_type: reproducibility
manuscript_location: papers/governance/environment_attestation/attestation.json
claim_id_or_artifact_id: M-030 (EXP-004) environment attestation
concise_issue: The attestation certifies "two identical all-green suite runs" of 474 tests at git head c11fc86fe with dirty:true, dated 2026-07-20. The frozen tree collects 488 tests, including the R-14 probe that the freeze itself introduced.
exact_evidence_or_observation: |
  attestation.json: "green": true, "generated_utc": "2026-07-20T18:36:48+00:00",
                    "git": {"head":"c11fc86fe02fc616f0695630be99745601036274","branch":"main","dirty":true},
                    test_runs: 474 passed / 474 passed.
  Now: `python -m pytest --collect-only -q -p no:cacheprovider` -> "488 tests collected".
  tests/regression/test_budget_crossing_semantics.py (the R-14 evidence) is dated 2026-07-22 13:58 and
  contributes 14 tests: 474 + 14 = 488. It is tracked and passes (verified: 14 passed in 4.33 s).
  The attestation also whitelists a non-zero exit for one gate:
      {"gate":"document-consistency", "exit_code":2, "accepted_exit_codes":[0,2], "ok":true}
  I re-ran that gate today: it exits 0 with all checks ok, so the whitelist is not currently load-bearing —
  but a gate whose failure code is pre-accepted is weak evidence, and this is the same "a gate that cannot
  fail is not evidence" reasoning the project itself applied when voiding the 383d7896b attestation
  (papers/governance/_pending_refreeze.json).
root_cause: The attestation is a point-in-time artifact that was not regenerated after the remediation added tests and changed sources.
scientific_or_editorial_justification: Stage 12 requires a "complete environment specification", "package versions and numerical libraries", and repository cleanliness; the attestation is the package's environment evidence and must describe the state being shipped.
impact_on_validity_or_acceptance: The envelope check (Python 3.10.11, NumPy 2.2.6, SciPy 1.15.3, pandas 2.3.3, matplotlib 3.10.8, all in-envelope) is still accurate and useful. What is not evidenced is that the FROZEN tree is all-green, and the recorded git head is a dirty, superseded commit.
required_correction: Regenerate the attestation at the freeze commit with a clean tree (papers/scripts/make_environment_attestation.py), require 488/488 twice, and either drop the exit-2 whitelist for document-consistency or record why exit 2 is an acceptable outcome.
acceptable_alternatives: none — regeneration is cheap and involves no rerun of experiments.
additional_evidence_needed: none
dependencies: E-01 (regenerate after the anchor is corrected, so head/dirty are meaningful)
expected_improvement: The environment evidence describes the submitted state.
post_revision_verification: attestation.json git.head equals the freeze anchor, dirty:false, tests == the collected count, all gates exit 0 with no whitelisted non-zero codes.
status: open
```

### E-09 — Every exhibit's provenance stamp records a dirty working tree

```text
ticket_id: E-09
review_stage: 7 (§10.11)
reviewer_role: R5 (T3-STAT)
severity: Moderate
priority: P2
confidence: High — CONFIRMED
issue_type: reproducibility
manuscript_location: papers/governance/artifact_binding.csv (all 59 rows, commit_sha column)
claim_id_or_artifact_id: §10.11 exhibit source binding
concise_issue: All 59 exhibit rows record commit_sha = e3e618e6c1695dbd76d93ac47eb971c55d159b23-dirty. The tree state that produced every table and figure is therefore not archived.
exact_evidence_or_observation: |
  Counter over artifact_binding.csv: {'e3e618e6c1695dbd76d93ac47eb971c55d159b23-dirty': 59}
  e3e618e6c is "Merge branch 'main' …" (2026-07-21), an ancestor of HEAD but neither the release anchor
  (67d9345f9) nor the freeze anchor. The "-dirty" suffix means uncommitted modifications were present.
  Mitigating: I re-verified every row's checksums — 0 source-checksum mismatches and 0 output-checksum
  mismatches against the files on disk. The artifacts themselves are internally consistent and bind to
  the correct release (50 rows rel-2026-07-20-67d9345f9, 9 rows authored/no-empirical-source).
root_cause: Exhibits were regenerated during the remediation window without an intervening commit.
scientific_or_editorial_justification: §10.11 requires "all figures and tables have source paths, commands, release IDs, and checksums"; Stage 12 requires archived source sufficient for future revision. A -dirty stamp defeats the "commit" element of that record.
impact_on_validity_or_acceptance: Low scientific risk (checksums prove what was produced), but a third party cannot reconstruct the generating tree, and §10.17.4 names "-dirty suffixes" as a provenance smell — here confined to a governance CSV, so not a reader-facing violation.
required_correction: Re-stamp commit_sha to the freeze commit after E-01 is fixed (the exhibit bytes are unchanged, so this is a metadata correction, not a regeneration), or add a note recording that the exhibits were produced in the remediation working tree whose content is pinned by the recorded checksums.
acceptable_alternatives: The note form is acceptable given the checksums verify.
additional_evidence_needed: none
dependencies: E-01
expected_improvement: Exhibit provenance becomes resolvable to an archived tree.
post_revision_verification: No "-dirty" appears in any commit_sha field; `git show <sha>` resolves.
status: open
```

### E-10 — `table_figure_source_map.csv` contradicts the authoritative binding registry

```text
ticket_id: E-10
review_stage: 7 (checks 12 and 14)
reviewer_role: R5 (T3-STAT)
severity: Moderate
priority: P2
confidence: High — CONFIRMED
issue_type: evidence
manuscript_location: papers/governance/table_figure_source_map.csv (46 data rows)
claim_id_or_artifact_id: exhibit source-binding registry
concise_issue: A second, stale exhibit registry sits alongside the correct artifact_binding.csv and binds every main table to a staging path it simultaneously marks MISSING, and points at a section file that does not exist.
exact_evidence_or_observation: |
  Rows T01..T16 and FIG-friedman:
      empirical_inputs = "results/paper_tables/T<n>.csv"
      input_status     = "MISSING (sole sanctioned producer = Phase 6 task 23 export …)"
  The shipped tables in fact bind to benchmarks/cec_reference_results/_paper_tables/T<n>.csv plus
  papers/analysis/rel-2026-07-20-67d9345f9/… (artifact_binding.csv, checksums verified).
  manuscript_location fields point at "supplement:sections/supplementary_content.tex:492/500/508".
  `ls papers/sections/` returns only conclusions.tex, introduction.tex, performance.tex,
  proposed_algorithm.tex, related_work.tex — there is no supplementary_content.tex anywhere.
  Rows FIG-conv-2017-D50-a/b/c carry exists=yes with manuscript_location "none (not referenced by any .tex)".
root_cause: The file is a Phase-2/5-era registry that was superseded by artifact_binding.csv (the §10.1-mandated binding artifact) and never retired.
scientific_or_editorial_justification: Stage 7 check 12 requires each table and figure to have a source binding and generator; check 14 requires contradictory source metadata to be resolved through a new release or documented correction, never left standing.
impact_on_validity_or_acceptance: An auditor who opens the governance directory finds two registries that disagree about where every main table comes from, one of which says the sources are MISSING. Nothing in the file marks it superseded.
required_correction: Either refresh table_figure_source_map.csv to the current bindings, or mark it SUPERSEDED-BY artifact_binding.csv in a header row / companion note and stop shipping it as a live registry.
acceptable_alternatives: Move it to papers/governance/parts/ or an archive subdirectory with a dated supersession record.
additional_evidence_needed: none
dependencies: none
expected_improvement: One authoritative answer to "where does this table come from".
post_revision_verification: Every exhibit resolves to exactly one non-contradictory binding row whose source paths exist.
status: open
```

### E-11 — R-06 residual: two stale release assertions remain in the supplement source

```text
ticket_id: E-11
review_stage: 7
reviewer_role: R5 (T3-STAT)
severity: Minor
priority: P3
confidence: High — CONFIRMED
issue_type: reproducibility
manuscript_location: papers/supplementary.tex:6 and papers/supplementary.tex:1780
claim_id_or_artifact_id: R-06 (supplement release identity)
concise_issue: The rendered R-06 fix is complete and correct, but two source-level assertions still name the superseded release rel-2026-07-16-78f075cb0 as the supplement's binding release.
exact_evidence_or_observation: |
  supplementary.tex:1-6 (file header):
     "%% … and papers/governance/artifact_binding.csv. Every empirical value traces to
      %% evidence release rel-2026-07-16-78f075cb0."
  supplementary.tex:1780 (S6 header block):
     "% separate from the primary release rel-2026-07-16-78f075cb0."
  Rendered side is CLEAN and correct: pypdf extraction of supplementary.pdf shows the full provenance chain
  (07-10 -> 07-16 superseded -> 07-20 current, anchor 67d9345f9502a9a584e645fa8948f60a61d70e29) at
  supplementary.tex:1086-1120, and validate_provenance_claims reports
     "supplementary.pdf: no superseded authority claim; states the current release".
  The hardened gate cannot see these lines by design — validate_provenance_claims.py:88 strip_tex_comments,
  docstring: "Comments are not rendered, so they can neither make [nor break] a claim." That is a defensible
  design for a rendered-claim gate; it simply means source hygiene needs a different check.
root_cause: The R-06 fix targeted the rendered enumerate block; the file-header and section-header comments were not swept.
scientific_or_editorial_justification: §10.3 requires the source release ID to be recorded correctly; Stage 7 check 14 requires contradictory source metadata to be resolved.
impact_on_validity_or_acceptance: Zero reader impact. Real maintenance impact: the next author to read the file header will believe the supplement binds to 07-16.
required_correction: Update both comment lines to rel-2026-07-20-67d9345f9 (and to abl-rel-2026-07-20 at :1780 where the ablation release is meant).
acceptable_alternatives: none — one-line edits.
additional_evidence_needed: none
dependencies: none
expected_improvement: R-06 becomes complete across source and rendered artifacts, as the seat mandate requires.
post_revision_verification: `grep -n "rel-2026-07-16" papers/supplementary.tex` returns only the deliberate supersession-history lines at :1106, :1107, :1113.
status: open
```

### E-12 — Three files inside the immutable evidence root are covered by no manifest

```text
ticket_id: E-12
review_stage: 7
reviewer_role: R5 (T3-STAT)
severity: Minor
priority: P3
confidence: High — CONFIRMED
issue_type: evidence
manuscript_location: benchmarks/cec_reference_results/{BENCHMARK_EVIDENCE_INDEX.md, cec2013lsgo/decc-g/decc-g_cec2013lsgo.csv, cec2013lsgo/mos/mos_cec2013lsgo.csv}
claim_id_or_artifact_id: CN-02 ("manifest records a SHA-256 checksum for every released file")
concise_issue: 4,724 files sit under the immutable evidence root; 3,403 are in the primary release manifest, 1,299 in the ablation manifest and 19 in the paper-tables manifest, leaving three covered by nothing.
exact_evidence_or_observation: |
  Set difference (on-disk under benchmarks/cec_reference_results vs. all three manifests):
      BENCHMARK_EVIDENCE_INDEX.md
      cec2013lsgo/decc-g/decc-g_cec2013lsgo.csv   (837 B, dated 2026-04-30, git-tracked)
      cec2013lsgo/mos/mos_cec2013lsgo.csv         (837 B, dated 2026-04-30, git-tracked)
  The two LSGO CSVs are external third-party reference results for DECC-G and MOS. They are NOT used
  by the paper: grep for "lsgo|decc-g|MOS" over papers/sections/*.tex, main.tex, supplementary.tex and
  cover_letter.tex returns zero hits. §10.4 asks the review to determine whether CEC2013-LSGO is
  context-only; here it is not used at all, which is the cleanest possible answer.
  Note also that a live CEC2013-LSGO staging campaign is running concurrently (git status shows new
  untracked results/_run_all/{gsk,agsk}/cec2013lsgo/ trees). That is staging-only and non-blocking under
  §0.3, but it means the evidence root's directory mtimes move during the submission window.
root_cause: Legacy third-party reference files predating the release-manifest discipline.
scientific_or_editorial_justification: §10.3 requires source release IDs and checksums to be recorded and the evidence boundary to be provable; the Data Availability Statement claims a checksum "for every released file".
impact_on_validity_or_acceptance: No headline result is affected. But the DAS's universal quantifier is slightly stronger than the manifests support, and an uncovered file inside an "immutable" root is exactly what an evidence auditor looks for.
required_correction: Either move the two LSGO CSVs out of the immutable root (they belong with the unused third-party reference material), or add them plus BENCHMARK_EVIDENCE_INDEX.md to a small index manifest so that every file under the root is covered.
acceptable_alternatives: A one-line note in BENCHMARK_EVIDENCE_INDEX.md declaring the LSGO directory out of scope for the primary release and unused by the paper.
additional_evidence_needed: none
dependencies: none
expected_improvement: The "checksum for every released file" claim becomes literally true.
post_revision_verification: Set difference between the evidence root and the union of the manifests is empty (or the exceptions are declared).
status: open
```

### E-13 — Orphan staging-reading exhibit generators still ship, with a silent-fallback loader

```text
ticket_id: E-13
review_stage: 7 (check 11) / 12
reviewer_role: R5 (T3-STAT)
severity: Minor
priority: P3
confidence: High — CONFIRMED
issue_type: reproducibility
manuscript_location: papers/scripts/generate_adaptive_params_panel.py:63-65 ; papers/scripts/generate_trace_figures.py:49-53
claim_id_or_artifact_id: §10.11 exhibit generators / Stage 7 check 11 (no silent staging fallback)
concise_issue: Two shipped generators read staging paths and select between them with a silent existence test; both are governance-marked BLOCKED, their input root does not exist, and their outputs are absent — yet they remain in papers/scripts/ and in the documented pipeline.
exact_evidence_or_observation: |
  generate_adaptive_params_panel.py:63-65
      _BULK_DIR   = _REPO / "results" / "dt-gsk" / "dt-gsk" / "cec2017" / "gen_logs"
      _LOCKED_DIR = _REPO / "results" / "dt-gsk" / "pub-lock-sgsm-adaptive" / "cec2017" / "gen_logs"
      _GEN_LOG_DIR = _BULK_DIR if _BULK_DIR.is_dir() else _LOCKED_DIR      <- silent fallback
  generate_trace_figures.py:49-53 uses the same three staging roots.
  `ls results/dt-gsk` -> "No such file or directory"; papers/figures/traces/ contains only .gitkeep.
  Governance already records the correct disposition:
      table_figure_source_map.csv row FIG-trace-adaptive: input_status "BLOCKED (same GenLog promotion
      condition)", notes "ORPHAN derivative - same condition as FIG-trace-ace".
  Confirmed NOT in the shipped manuscript: grep "adaptive_params" over all .tex returns only the
  governance CSV row, so no manuscript exhibit is sourced from staging. §10.11 is not breached in the paper.
root_cause: Superseded exhibits whose generators were left in the tree when the exhibits were dropped.
scientific_or_editorial_justification: §5.5 calibrates orphan/superseded artefacts left in the tree as a real defect because they can be submitted or run by accident; Stage 7 check 11 targets silent staging fallbacks specifically.
impact_on_validity_or_acceptance: No effect on the shipped paper. It becomes a real defect only in combination with E-04, because runbook.md still lists both scripts inside the "complete data-to-PDF sequence".
required_correction: Delete both scripts (with a decision-log entry), or move them under a clearly named archive/ subdirectory and remove them from runbook.md.
acceptable_alternatives: Keep them but make the fallback explicit — raise a StrictSourceViolation-style error instead of silently switching directories.
additional_evidence_needed: none
dependencies: E-04
expected_improvement: No shipped generator can read staging, silently or otherwise.
post_revision_verification: grep over papers/scripts/*.py for "results/" returns only finalize_evidence.py (the promotion tool, which legitimately reads staging) and the ablation-matrix CLI defaults.
status: open
```

### E-14 — Remediation closure record is internally inconsistent and pre-dates the final commit

```text
ticket_id: E-14
review_stage: 12
reviewer_role: R5 (T3-STAT)
severity: Minor
priority: P3
confidence: High — CONFIRMED
issue_type: production
manuscript_location: papers/governance/_pending_refreeze.json
claim_id_or_artifact_id: R-01..R-14 closure record
concise_issue: The record is stamped status CLOSED while one of its own tickets is recorded as only partially done, and its verification numbers are one commit stale.
exact_evidence_or_observation: |
  "status": "CLOSED", "closed_utc": "2026-07-22T00:00:00Z"
  "R-13": "sentence de-packing / S5 ledger tokens / resizebox - partially DONE (style)"
  resolution string: "cross-format parity 578 rows / 0 FAIL"
  Re-run today: validate_cross_format_parity -> "TOTAL rows=579  FAIL=0".
  The +1 row is consistent with commit 45248eb31 having modified
  papers/governance/cross_format_consistency.csv after the record was written.
root_cause: The closure record was written at abd2fa2f2 and not refreshed by the subsequent 45248eb31 amendment.
scientific_or_editorial_justification: §5.4 — "Do not close a ticket because text was changed. Close it only when the required verification passes." A CLOSED record containing a partially-done ticket does not meet that bar.
impact_on_validity_or_acceptance: Governance hygiene only. It is, however, the same failure mode the project itself diagnosed when it voided the 383d7896b attestation, so leaving it uncorrected is conspicuous.
required_correction: Either finish R-13 and restate it as DONE, or reopen it as a separately tracked P3 style ticket and note in the closure resolution that R-13 remains open; refresh the parity row count to 579.
acceptable_alternatives: none
additional_evidence_needed: none
dependencies: none
expected_improvement: The remediation record is self-consistent and re-verifiable.
post_revision_verification: No ticket inside a CLOSED record reads "partially DONE"; the quoted gate counts reproduce on a fresh run.
status: open
```

### E-15 — The governing review prompt's embedded snapshot is stale (recorded as instructed)

```text
ticket_id: E-15
review_stage: 0 / 12
reviewer_role: R5 (T3-STAT)
severity: Minor
priority: P3
confidence: High — CONFIRMED
issue_type: compliance
manuscript_location: papers/PAPER_REVIEW_PROMPT.md §1.5 (L118-602), and §10.7 RT-001 (L3299)
claim_id_or_artifact_id: review governing prompt
concise_issue: §1.5 is dated 2026-07-20 and predates the 2026-07-21/22 remediation; §10.7 RT-001 describes the runtime table as "IN PROGRESS … mixes two measurement sessions and is provisionally frozen", which the repo has since resolved by a different route.
exact_evidence_or_observation: |
  RT-001 (L3299) anticipates re-timing all six comparators onto one idle machine
  (scripts/retime_comparators.py). The shipped resolution is different and better: tab:runtime was
  scoped to DT-GSK only ("no cross-algorithm runtime comparison is made", performance.tex:766), and
  validate_runtime_provenance.py now reports a single cell, single host, 0.0 h panel span:
      "OK - single host, single worker count, all cells within 72 h.
       The DT-GSK-only runtime table is single-session and may be regenerated."
  A reviewer applying §10.7 RT-001 literally would look for a mixed-session six-comparator table that
  no longer exists.
root_cause: The prompt's snapshot was frozen before the last two remediation rounds, as the seat brief itself states.
scientific_or_editorial_justification: §1.4 precedence — the current project state outranks the prompt's embedded snapshot. The brief directs that the staleness be recorded.
impact_on_validity_or_acceptance: Review-process only. Risk is that a seat reads §1.5/RT-001 as current and either re-raises a closed issue or misses the real one.
required_correction: Re-cut §1.5 against the state at 45248eb31 and mark RT-001 RESOLVED-BY-SCOPING rather than IN PROGRESS.
acceptable_alternatives: A dated "superseded from here" banner at the head of §1.5.
additional_evidence_needed: none
dependencies: none
expected_improvement: Future review rounds start from the true state.
status: open
```

---

## 4. Stage 7 evidence-anomaly report

| anomaly_id | source_path_or_record | anomaly_type | expected | observed | scope | possible_causes | impact | repair scientifically permissible? | required disposition |
|---|---|---|---|---|---|---|---|---|---|
| AN-01 | `main_manuscript_freeze_manifest.json:5` | contradictory provenance metadata | anchor commit materializes the 15 frozen files | 4/15 differ at the anchor; they exist at `45248eb31` | package integrity | field not advanced by the amendment commit | no number affected; anchor unusable | Yes — metadata correction | Advance anchor / add `amended_at_commit` (E-01) |
| AN-02 | freeze manifest `files[]` vs repository | non-reproducible byte pin | clean-room checkout reproduces 15/15 | 10/15 (`git archive HEAD`) | 5 text files | `core.autocrlf=true`, no `.gitattributes`, mixed working tree | byte-for-byte level unsupported off-host; content identical | Yes — add `.gitattributes`, re-mint | E-02 |
| AN-03 | `reproducibility_manifest.json:435-488` | stale immutable identifier + stale hashes | current release + current artifact hashes | `rel-2026-07-10-262fc16c9`; `503692de…` / `993fe08a…`; `_ablation … 1032 files` | determinism contract | never refreshed after 2 re-mints | Gate L FAIL as recorded | Yes — append a new dated block; do not edit the old one | E-03 |
| AN-04 | `runbook.md:100` | superseded release in an authority position | `rel-2026-07-20-67d9345f9` | `rel-2026-07-10-262fc16c9` | reproduction doc cited by the DAS | doc not re-cut for the publication pipeline | referee reproduces the wrong bundle | Yes — text correction | E-04 |
| AN-05 | `performance.tex:169-170` vs `*/{agsk,apgsk}/per_run.csv` | prose/evidence mismatch | all seven charged exactly MaxFES | 1,845 runs terminate `target_error_reached`, `nfes` down to ~50% MaxFES | fairness sentence + convergence captions | R-05 conclusion over-generalized | statements false; two mandated disclosures absent; no reported statistic affected | Yes — correct the prose (never the evidence) | E-06 |
| AN-06 | `phase_gate_register.csv` (Phase 8/11 rows) | stale gate measurement | page counts + byte sizes of the shipped artifacts | 35 pp / B1 32 and four superseded byte sizes vs 39 pp shipped | §10.14 evidence | not re-measured at Phase 12 | headroom claim no longer true; no row for the shipped PDF | Yes — add a current row | E-07 |
| AN-07 | `environment_attestation/attestation.json` | stale attestation | green at the freeze commit, clean tree | `c11fc86fe`, `dirty:true`, 474 tests (tree now collects 488) | environment evidence | not regenerated after remediation | frozen state not attested | Yes — regenerate | E-08 |
| AN-08 | `artifact_binding.csv` (59/59 rows) | unrecoverable generating state | a committed SHA | `e3e618e6c…-dirty` | all exhibits | regeneration without an intervening commit | checksums verify; tree unrecoverable | Yes — re-stamp after E-01 | E-09 |
| AN-09 | `table_figure_source_map.csv` | superseded registry left live | one authoritative binding per exhibit | T01–T16 bound to `results/paper_tables/*` marked MISSING; `sections/supplementary_content.tex` does not exist | governance | Phase-2 artifact never retired | contradicts `artifact_binding.csv` | Yes — refresh or mark superseded | E-10 |
| AN-10 | `supplementary.tex:6`, `:1780` | stale release assertion in source | current release | `rel-2026-07-16-78f075cb0` | source comments only | R-06 sweep missed comments (gate strips them by design) | zero reader impact | Yes — one-line edits | E-11 |
| AN-11 | evidence root vs manifests | uncovered files inside an immutable root | every file covered | 3 uncovered (`BENCHMARK_EVIDENCE_INDEX.md`, 2 LSGO CSVs) | evidence lock | legacy third-party files | DAS universal quantifier slightly overstated; files unused by the paper | Yes — declare or relocate | E-12 |

No anomaly in this table requires new experiments, a new evidence release, or any change to the byte-locked optimizer core. **Every one is a metadata, documentation or prose correction.**

---

## 5. Clean-room verification result

Procedure actually executed (Stage 12 §"Clean-room verification"):

1. Materialized the declared package from the repository alone — `git archive HEAD -- papers | tar -x` into the session scratchpad. Nothing was written to the repository.
2. Ran the project's own integrity check in that clean location against the shipped freeze manifest.

**Result: 10 / 15.** The five failures are `main.tex`, `introduction.tex`, `related_work.tex`, `performance.tex`, `conclusions.tex` — all line-ending, none content (every file is normalized-equal to HEAD). All five binary deliverables reproduce exactly.

Steps 3–5 (regenerate critical statistics, rebuild manuscript outputs, compare) were **not executed**, because every available path writes into the repository (`phase6_run_analysis.py` → `papers/analysis/`, `generate_latex_tables.py` → `papers/tables/`, `build_pdf.py` → `papers/`) and this seat is read-only. They were substituted with non-destructive equivalents of equal or greater strength:

- full re-hash of the immutable release (3,403 files) and of the analysis bundle (130 files) — the inputs the statistics would be regenerated from;
- full re-hash of every declared exhibit source and output in `artifact_binding.csv` (59 rows) — the outputs a regeneration would have to match;
- re-execution of all five read-only gates (`check_manifest`, `validate_provenance_claims` incl. `--self-test`, `validate_document_consistency`, `validate_build_hygiene`, `validate_runtime_provenance`) and of `validate_cross_format_parity` with its CSV redirected to the scratchpad.

**Undocumented manual steps observed** (Stage 12 requires these be recorded):

1. Minting/refreshing `main_manuscript_freeze_manifest.json` is a hand step — the project's own record states it: *"Refreeze is a HUMAN byte-surgical step (CRLF + 2-space indent; edit hashes in place, never rewrite the file)"* (`_pending_refreeze.json`). There is no tool that mints it.
2. Producing the controlled analysis bundle (`phase6_run_analysis.py`) is nowhere in the documented pipeline (E-04).
3. Producing the Word deliverables (`build_docx.py`, `generate_word_sources.py`) is nowhere in the documented pipeline (E-04).
4. Running the release gates (`check_manifest`, `validate_*`) is nowhere in the documented "Quality gates" step (E-04).
5. The line-ending policy required to make the freeze manifest verify is undocumented and unenforced (E-02).

---

## 6. Minimum release package needed for submission

Files a third party needs to verify every reported number, with nothing extraneous:

| Component | Path | Size / count | Status |
|---|---|---|---|
| Immutable primary evidence | `benchmarks/cec_reference_results/{cec2011,cec2013,cec2017,README.md}` | 3,403 files / 712 MB | Ready — checksums verified |
| Primary release manifest | `papers/governance/evidence_release_manifest.json` | — | Ready |
| Ablation evidence + manifest | `benchmarks/cec_reference_results/_ablation/` | 1,297 files | Ready |
| Table-input export + manifest | `benchmarks/cec_reference_results/_paper_tables/` | 17 CSV + manifests | Ready |
| Controlled analysis bundle | `papers/analysis/rel-2026-07-20-67d9345f9/` | 114 files + `analysis_checksums.sha256` | Ready — checksums verified |
| Analysis + build code | `src/`, `papers/scripts/` (minus the two orphan generators, E-13) | — | Ready after E-13 |
| Environment specification | `papers/governance/environment_attestation/`, `requirements*.txt`, `pyproject.toml` | — | **Needs regeneration (E-08)** |
| Determinism-contract record | `papers/governance/reproducibility_manifest.json` | — | **Needs a current block (E-03)** |
| Exhibit bindings | `papers/governance/artifact_binding.csv` | 59 rows | Ready after commit re-stamp (E-09) |
| Freeze + submission manifests | `papers/governance/{main_manuscript_freeze_manifest,submission_package_manifest}.json` | 15 + 5 files | **Needs correct anchors (E-01) and a platform-stable byte policy (E-02)** |
| Reproduction instructions | `runbook.md` / new `papers/REPRODUCE.md` | — | **Needs rewrite (E-04)** |
| Licences | `LICENSE` (MIT), `docs/LICENSES.md` | present | Ready — both exist, matching the DAS |
| Durable archive identifier | — | — | **ABSENT (E-05)** |

Excluded, correctly: `results/` in all forms (staging, and a live LSGO campaign is running in it); `papers/DT-GSK_visio.docx` (already registered for exclusion in `submission_package_manifest.json`); `reference_papers/*.pdf` (git-ignored copyrighted acquisitions).

---

## 7. Gate verdicts for this seat

| Gate | Verdict | Basis |
|---|---|---|
| **Gate G — Evidence Integrity** | **PASS** | No untraceable headline result, no edited immutable evidence, no unresolved run/sample discrepancy, no data leakage, no prohibited source. 3,403/3,403 + 130/130 + 59/59 checksums verify; 1,239 source opens all inside the release; counts, seeds and pairing all reconcile exactly. E-06 is a prose defect over correctly-recorded evidence, and E-12 concerns three unused files — neither meets the Gate G failure conditions. |
| **Gate L — Reproducibility** | **FAIL (remediable without new science)** | Four independent failure conditions are met: recorded delivery levels are bound to a superseded release and superseded hashes with a 2026-07-12 rebuild attestation (E-03); the clean-room materialization does not reproduce the declared package (E-02); the declared anchor does not contain the frozen bytes (E-01); the documented reproduction commands do not regenerate the statistics, tables or Word deliverable and cite a superseded bundle (E-04). The availability statement is additionally unverifiable at review time (E-05). |

**Every Gate L failure is closable by metadata, documentation and prose corrections. None requires a rerun, a new evidence release, or any change to the byte-locked optimizer core.**

Minimum path to clearing Gate L: E-01 + E-02 + E-03 + E-04 (+ E-05 at submission time). E-06 is a Gate-F/Gate-G-adjacent prose correction that should ride along in the same pass.

---

## 8. Re-verification of the 2026-07-21/22 remediation (as tasked)

| Ticket | Closed correctly? | Evidence |
|---|---|---|
| R-03 (DOCX OMML `&`) | **Yes** | 0 literal `&` across 3,610 + 2,220 `<m:t>` runs in both DOCX |
| R-05 (budget-crossing semantics) | **Partially — over-generalized** | The terminal-batch disclosure is correct and now machine-checked; the accompanying universal claim "*All seven optimizers are therefore held to exactly the same MaxFES charge*" is contradicted by 1,845 released runs → **E-06** |
| R-06 (supplement release identity) | **Yes in the rendered artifacts; two source comments remain** | `supplementary.pdf`/`.docx` state the current release and no superseded authority claim; `supplementary.tex:6` and `:1780` still name 07-16 → **E-11**. The same defect class survives untouched in `runbook.md:100` → **E-04(a)** |
| R-07 (provenance gate hardening) | **Yes** | Gate exits 0 with 15 explicit checks; `--self-test` passes 4/4 including two shapes designed to fail. Note the by-design blind spot: `strip_tex_comments` means the gate cannot see E-11. |
| R-12 (phase-gate write-back) | **Partially** | Phase 12 row is FROZEN with a 2026-07-22 timestamp, but carries no page-count measurement → **E-07** |
| R-13 (sentence de-packing) | **No — self-declared partial inside a CLOSED record** | → **E-14** |
| R-14 (budget-crossing probe) | **Yes** | `tests/regression/test_budget_crossing_semantics.py` tracked, 14 tests pass |
| R-01, R-02, R-04, R-08..R-11 | Out of this seat's scope (equations, restart invariant, contribution count, cover-letter scope) — referred to the method and claims seats |

---

## 9. Method note

Everything above was recomputed from the repository during this session. No finding rests on an author assurance where an artifact could be checked (§15). Commands used: full-tree SHA-256 re-hashing (Python `hashlib`), `git show` / `git archive` / `git merge-base` for provenance, `pypdf` for rendered-artifact extraction, `zipfile` + regex for OOXML inspection, direct CSV reduction of the released `per_run.csv` files, and the project's own read-only validators. The single claim I initially drafted and then withdrew — an apparent off-by-one in the released seed formula — was withdrawn after re-reading the untruncated `seed_scheme` string; it is recorded in §2 item 7 so the panel does not rediscover it as a phantom.
