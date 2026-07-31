# Phase 12 — Final Integrity and Completion Audit

- **date_utc:** 2026-07-12
- **phase:** 12 (final implementation phase)
- **evidence release:** `rel-2026-07-10-262fc16c9` (primary); `abl-rel-2026-07-11` (ablation)
- **freeze manifest:** `papers/governance/main_manuscript_freeze_manifest.json` (12 tracked files)
- **determinism contract:** `SOURCE_DATE_EPOCH=1783468800` (PDF) / `1783641600` (DOCX)

**Verdict: COMPLETE on the scientific, method, evidence, statistics, exhibit, reproducibility, and internal-consistency dimensions. Two residual classes remain and are recorded honestly: (a) author-side administrative declarations, and (b) the by-design comparator/attribution ceiling. No fabricated evidence; no scientific blocker.**

---

## 1. Ablation execution and promotion (12.1–12.13)

| Item | Result |
|---|---|
| Scaffold remove-one X-ABL-01 (CEC2017, 7 cells, D10/30/50/100, 25 runs, SGSM off) | executed, validated, promoted to `_ablation/scaffold/` (7×2900 rows, 0 dupes) |
| SGSM overlay X-ABL-02 (CEC2013 D50, 4 cells) | executed at D50, promoted to `_ablation/overlay/`; the full pre-registered D∈{50,100}+overhead design is **deferred** (a follow-up supplement revision) — disclosed in §S6.6 and consistent across the manuscript |
| Convergence curves | 924 promoted (scaffold + overlay), manifested |
| Ablation manifest | `_ablation/manifest.json` = 1,032 files, every SHA-256 recomputes |
| Correction-exception check (12.15) | scaffold: no correction; overlay T-1 (IN-02): text-only narrowing applied then **reduced to a result-free deferral** after the R1 review (see §5) |

## 2. Method ⇄ code correspondence (§10.6)

Verified against the frozen `interaction_graph.py`. The one defect found — printed Eq. (11)/E10 wrote `G←(1−λ)G+λΣ` while the code computes `decay·G + lr·agg` — was **corrected** to `G←λG+ηΣ` (λ=0.95 retention, η=1.0 learning rate) in the equation, Algorithm 1 step 7, prose, and the parameter table. All other mechanisms (ACE, NLPSR, BSE, linkage, polish, deep-stall, determinism layer) reconcile with the code and the parameter table.

## 3. Evidence integrity (§10.3)

- 7-optimizer panel complete: CEC2017 5,916 rows/optimizer, CEC2013 4,284, CEC2011 550; **0 duplicate (function,dim,run) tuples**; gen_logs/CheckpointErrors present for every cell.
- apgsk CR-0006 recovery complete (per_run 1,479→5,916), reproduces frozen summaries exactly; the manuscript's prior "disclosed-unavailable" wording was reconciled to the recovery via a footnote while retaining the frozen function-level basis.
- All 16 paper tables byte-verified to `benchmarks/cec_reference_results/_paper_tables/`; **no paper artifact reads `results/` staging** (audited across all generators).
- No immutable evidence edited in place; corrected evidence is a versioned release with a supersession record.

## 4. Statistics (§10.7)

Independent recomputation reproduced every headline statistic exactly: CEC2017 overall rank 2.48 (2.88/2.50/2.21/2.34), 17-7-0 Holm tally, all Wilcoxon/Holm cells, 1,332 run-level effect-size labels (0 mismatches), Iman–Davenport omnibus, Nemenyi CD, CEC2011/2013 profiles. Overall rank is a **descriptive** mean of per-dimension ranks (not a pooled test). Sub-1e-4 p-values now render as a bound (`<0.0001`), never `0.0000`.

## 5. Main-text ablation prohibition (§10.9)

Strict scan of the rebuilt `DT-GSK.pdf`: **0 ablation result tokens** (no p-value, rank, win/tie/loss, or component-effect conclusion) adjacent to any ablation mention. The two "remove-one" occurrences are **neutral pointers** to the supplementary study that state no result — permitted under §10.9. The R1 review found and corrected a prior violation (a leaked null-result + false cross-reference); it is now a result-free deferral.

## 6. Exhibits (§10.11)

- Figure 1 (taxonomy): raw BibTeX keys replaced with author-year citations.
- Concept-figure equation anchors: an E-registry-ID → printed-equation-number legend added.
- Algorithm 1: renders cleanly (Require/Ensure, numbered steps, tier badges, no raw macros).
- Equation numbering (1)–(13) sequential and matches all in-text refs.
- Cross-format: 14 figures in PDF ↔ 14 media in DOCX; all R1 fixes present in both.

## 7. Reproducibility — achieved delivery levels (double rebuild, 2026-07-12)

| Artifact class | Achieved level | Evidence |
|---|---|---|
| Immutable primary evidence (`rel-2026-07-10-262fc16c9`) | byte-for-byte | SHA-256 manifests; not regenerated |
| Derived analysis bundle (`papers/analysis/<release>/`) | analytical + byte-for-byte | `phase_06/determinism_check.md` PASS (0 real diffs / 5 timestamp-only across 115 files) |
| LaTeX tables (`papers/tables/T*.tex`) | visual + byte-for-byte | regenerate byte-identical from `_paper_tables/` |
| Figures (rank charts, concept) | visual + byte-for-byte | `CreationDate` suppressed → deterministic |
| Main `DT-GSK.pdf` | byte-for-byte after timestamp normalization | reproducible across 2 builds (`6792a0d5…`) |
| Main `DT-GSK.docx` | byte-for-byte after timestamp normalization | reproducible across 2 builds (`8a275461…`) |
| Ablation evidence (`_ablation/`) | byte-for-byte | 1,032-file manifest |

Double-rebuild from the immutable release achieves **analytical reproducibility everywhere, visual for all exhibits, and byte-for-byte where timestamp normalization applies** — the build-framework contract is met. Recorded in `reproducibility_manifest.json:phase12_reproducibility`.

## 8. Independent review (R1) disposition

6-reviewer post-completion review (`independent_review_report.md`): core science verified correct; 14 critical/major/moderate tickets identified, all **editorial/consistency/exhibit/method-labeling** — none a fabricated-evidence or invalid-analysis defect. All 14 fixed and verified in the rendered PDF (commit `016db447e`). Review Gates C, F, J, M → PASS after fixes.

## 9. Residuals (recorded, not hidden)

- **Author-side (administrative):** real ORCIDs, GenAI model-version pin, funding/COI text, DOI, received-date, MDPI current-template migration, submission-form abstract-length check, final upload. None is a scientific blocker.
- **By design (ceiling):** same-family (7-method) comparator panel — supports GSK-family conclusions only, honestly scoped, no field-wide/SOTA claim; and the ISM standalone-attribution is deferred (the full SGSM-overlay isolation is a follow-up study). Both cap Q1 without new experiments; both are candidly disclosed.

## 10. Completion status

Scientific content: **FROZEN + R1-corrected**. Evidence, statistics, method-code correspondence, exhibits, cross-format parity, determinism: **PASS**. Formal Gate-12 freeze is **conditional on the author-side administrative items and final submission-package assembly**; all engineering and scientific obligations of Phase 12 are discharged.
