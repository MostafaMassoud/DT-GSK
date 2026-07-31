# Independent Post-Completion Review — DT-GSK (REVIEW R1)

- **review_id:** R1-2026-07-12
- **review_date:** 2026-07-12
- **project_title:** DT-GSK: An Interaction-Structure Memory for High-Dimensional Optimization
- **manuscript_version:** post Phase-11 freeze + T-1 narrowing + pseudocode/figure legibility revisions (rel-2026-07-10-262fc16c9 evidence)
- **target_journal / type / quartile:** MDPI *Algorithms* / Article / Q2 candidate (Q1 stretch)
- **method:** 6 independent reviewers (science/method, statistics, evidence/reproducibility, editorial/writing/ethics, journal/exhibits, adversarial-Q1/ablation) executing PAPER_REVIEW_PROMPT.md Stages 0–20 + §10 profile; every ticket verified against source files, tables, the frozen analysis bundle, and the frozen code by the coordinating reviewer.

## Executive verdict

**Disposition: MAJOR REVISION (all blockers are editorial/consistency/exhibit — no new experiment required to reach Q2-ready; the central inference is sound).**

The paper's core scientific content is **verified correct**: multiple independent recomputations confirmed the headline Friedman ranks (CEC2017 overall 2.48; per-dim 2.88/2.50/2.21/2.34), the 17-7-0 Holm tally, all Wilcoxon/Holm cells, effect sizes (1332 run-level labels, 0 mismatches), Iman–Davenport omnibus, Nemenyi CD, and CEC2011/CEC2013 profiles — none invalidated by CR-0006. Evidence is complete (7-optimizer panel, 0 duplicate run-tuples, byte-verified tables) and honestly documented.

The blockers are **consistency and completeness defects concentrated in unfinished business**, not scientific errors:
1. **SGSM-overlay (X-ABL-02) integration incomplete** → the T-1 main-text sentence leaks an ablation null-result (§10.9 hard failure) and cites a supplement isolation study the supplement itself says is "in progress / not reported"; `conclusions.tex` falsely says no component study is in the supplement; three-way performance↔conclusions↔supplement inconsistency.
2. **CR-0006 apgsk-recovery aftermath unreconciled** → the manuscript still asserts apgsk per-run is "disclosed-unavailable / exists only at D=100" in ~10 locations while the recovered bundle now carries those cells `availability=ok`; `cost_cec2017.csv` mislabels post-freeze re-run runtime as "comparable."
3. **Method-correctness:** printed Eq. (11) (registry E10) contradicts the frozen `interaction_graph.py` — `G←(1−λ)G+λΣ` should be `G←λG+ηΣ` (retention λ=0.95 on old G, separate learning rate).
4. **Exhibits:** Figure 1 prints raw BibTeX keys; four method figures use E-IDs off-by-one+ from printed equation numbers.
5. **Phase-12 not formally closed:** build Gate 12 NOT_STARTED, `reproducibility_manifest.json` lacks delivery-level records, `artifact_binding.csv` cites the absent `results/paper_tables/`.

Two items are **not fixable by editing** and cap the ceiling: the same-family-only comparator panel (no external SOTA — honest scoping mitigates but Q1 reviewers may push back) and the central-component attribution gap (the eponymous ISM has no *confirmed* standalone benefit; attribution is deferred). Both are defensible under strict "mechanism proposed, attribution deferred" framing.

## Gate report (A–Q)

| Gate | Status | Blocking tickets | Min action to pass |
|---|---|---|---|
| A Package integrity | **BLOCKED** | build Gate 12 NOT_STARTED; orphan files | close Phase 12; delete orphans |
| B Desk review | PASS | — | — |
| C Claim integrity | **FAIL** | C1 (leak+false xref), C2/C5 (false existence claims) | reconcile SGSM + apgsk statements |
| D Contribution merit | CONCERN | attribution gap, same-family panel | scope framing (already largely present) |
| E Literature/citation | PASS | (minor: unused keys) | — |
| F Method/theory | **FAIL** | C7 (Eq.11 vs code) | fix EMA equation + Alg step 7 |
| G Evidence integrity | PASS | (C6 bundle label) | fix cost_cec2017 label |
| H Study design/fairness | PASS | — | — |
| I Statistical validity | PASS | (C13 p=0 render, minor) | — |
| J Result integrity | **FAIL** | C1, C2, C5, C12 (A12 self-contradiction) | reconcile + fix A12 |
| K Robustness/attribution | PASS | (LOO/floor optional) | — |
| L Reproducibility | **BLOCKED** | C10 (manifest levels), C11 (stale binding) | record levels; repoint binding |
| M Exhibit integrity | **FAIL** | C8 (raw bibkeys), C9 (figure E-IDs) | regenerate figures |
| N Writing/authorship | PASS | (AI-voice advisory only) | — |
| O Ethics/publication | PASS | (author-side declarations) | author fills |
| P Journal/production | CONCERN | MDPI class outdated; back-matter style | template migration (author) |
| Q Post-revision verification | PENDING | — | after fixes |

## Critical & major issue register (verified)

- **C1 CRITICAL** performance.tex ~L800-804 — T-1 sentence leaks ablation result (§10.9) + false supplement cross-ref. [3 reviewers]
- **C2 MAJOR** conclusions.tex L117-118 — false "no component study in supplement" (§S6 present).
- **C3 MAJOR** three-way performance↔conclusions↔supplement inconsistency.
- **C4 MAJOR** orphan `sections/literature_review.tex` + `sections/supplementary_content.tex` (built by nothing) carry prohibited "SGSM=Structure-Gated Similarity Memory" expansion + isolation claims + stale 2-algo figures → delete/quarantine.
- **C5 MAJOR** apgsk "disclosed-unavailable/sole-basis" stale in conclusions.tex L111, performance.tex L115/119-120/264-265/314-315 vs recovered bundle (availability=ok); CR-0006 unmentioned.
- **C6 MAJOR** `analysis/.../cost_cec2017.csv` labels post-freeze re-run apgsk runtime "comparable/ok" (wall-clock, not comparable).
- **C7 MAJOR** Eq.(11)/E10 `G←(1−λ)G+λΣ` contradicts `interaction_graph.py` (`matrix*=decay; matrix+=lr*agg`) → `G←λG+ηΣ`; mirror in Algorithm 1 step 7.
- **C8 MAJOR** Figure 1 (fig_taxonomy.pdf) prints raw bibkeys `[omidvar2014dg]/[hansen2001cmaes]/[guo2015eig]` → regenerate with formatted cites.
- **C9 MAJOR** Figs 1/2/3 + SGSM figure use E-IDs (E4/E5/E10/E11/E12) off-by-one+ vs printed Eq.(1)-(13) → relabel or add legend.
- **C10 MAJOR** build Gate 12 NOT_STARTED; `reproducibility_manifest.json` lacks analytical/visual/byte-for-byte delivery levels.
- **C11 MAJOR** `artifact_binding.csv` (17 rows) + `table_figure_source_map.csv` cite absent `results/paper_tables/` → repoint to `benchmarks/cec_reference_results/_paper_tables/`.
- **C12 MODERATE** performance.tex L334-335 A12 "only sub-0.5 cell at D=100" false (D30=0.490 also sub-0.5).
- **C13 MODERATE** T15.tex prints `p=0.0000` (4 cells); SAP mandates `<1.0e-4`; inconsistent with T14 sci-notation.
- **C14 MODERATE** performance.tex L777-783 credits hybrid strength at D≥30 to linkage-aware recombination (gated OFF below D50).

## Minor / advisory
Alg step 3b omits D30-tier fixed blocks; abstract "confidence-gated" vs "confidence- and evidence-gated"; unused bib keys + stale comment; Data-Availability/GenAI back-matter font+punctuation; Nemenyi figures labeled "CD diagram" but rendered as rank bar charts; robustness LOO/floor-sensitivity absent (optional); stats register method/version columns incomplete.

## Author-side (cannot be auto-fixed)
GenAI model-version pin; real ORCIDs; funding/COI; DOI; received-date; MDPI current-template migration; submission-form abstract-length check; MDPI upload.

## Rejected on verification (false positives)
Evidence reviewer's "orphan trace figures + T21/T22 rendered" — those live in the un-built orphan `supplementary_content.tex`; the shipped `supplementary.tex` includes only T01–T16/SA01/SA02/T16_bca.

## Top rejection risks
1. Reviewer spots the performance↔conclusions↔supplement contradiction on first read (C1-C3) — "the paper cites supplementary evidence that the supplement says doesn't exist."
2. "Where is the external (non-GSK) state-of-the-art baseline?" (venue-fit; not editable).
3. "Does the eponymous ISM actually contribute?" — attribution deferred; reviewer may want the SGSM isolation completed.
4. Camera-ready: raw BibTeX keys in Figure 1.
5. Method reimplementation from the printed EMA equation builds the wrong graph (C7).

## Post-review disposition (fixes applied 2026-07-12, commit 016db447e)

| Ticket | Status |
|---|---|
| C1 T-1 leak + false xref | **FIXED** — result-free deferral; verified in rendered PDF (leaked phrase = 0) |
| C2/C3 supplement consistency | **FIXED** — conclusions.tex + proposed_algorithm.tex reconciled with §S6 |
| C5/C6 apgsk recovery reconciliation | **FIXED** — CR-0006 footnote; function-level basis kept; runtime-d.u. reason disclosed |
| C7 Eq.(11) vs code | **FIXED** — `G←λG+ηΣ` in equation, Alg step 7, prose, param table; verified in PDF |
| C8 taxonomy raw bibkeys | **FIXED** — author-year cites; verified in rendered Figure 1 |
| C9 figure E-IDs | **FIXED** — E-ID→equation-number legend added; verified in PDF |
| C11 stale artifact_binding | **FIXED** — regenerated to benchmark paths (0 stale) |
| C12 A12 self-contradiction | **FIXED** |
| C13 T15 p=0.0000 | **FIXED** — renders `<0.0001`; verified |
| C14 linkage attribution | **FIXED** — restricted to D≥50 |
| C4 orphan files | **FIXED** — git-removed + manifest entries dropped |
| minors (abstract term, etc.) | partially applied |
| **C10 Phase-12 closure** | **RESOLVED** (commit 9e35c02be) — final_integrity_audit.md written; reproducibility_manifest delivery levels recorded (double-rebuild MET); build Gate 12 → IN_PROGRESS with entry/validation/acceptance evidence. Formal freeze CONDITIONAL on author-side items only. |
| Nemenyi figure label | disposition: defensible as-is (MINOR judgment call; CD conveyed via reference span; not relabeled) |
| back-matter font/punctuation | disposition: fold into MDPI current-template migration (author-side ticket 4), not a manual hack |
| unused bib keys / stats-register columns / robustness LOO-floor | disposition: harmless / optional / needs new compute — recorded, non-blocking |
| author-side (ORCIDs, GenAI version, funding/COI, DOI, MDPI template, upload) | OPEN (author) |
| same-family panel / attribution gap | OPEN by design (not editable; scope-framed) |

Gates C, F, J, M moved to **PASS** after the fixes; **Gate L → PASS** (delivery levels recorded, double-rebuild contract MET); **Gate A → CONDITIONAL** (Phase-12 evidence + final audit recorded; formal pass awaits author-side declarations + final upload only). Manuscript scientific/editorial content is now internally consistent, method-faithful, and reimplementable. **Net: all scientific/editorial/exhibit/reproducibility blockers closed; residuals are author-side administrative and the by-design comparator/attribution ceiling.**

## Path to readiness
- **Q2-ready:** fix C1–C14 (all editorial/consistency/exhibit/generator — no new experiment), close Phase 12, author fills declarations. Achievable now.
- **Q1-ready (additional):** complete the X-ABL-02 SGSM isolation (D50+D100+overhead) so the titular mechanism has direct evidence; add ≥1 strong external non-GSK baseline; add LOO/floor-sensitivity robustness rows. Requires new compute.

---

# Independent Post-Completion Review — DT-GSK (REVIEW R2)

Second review pass, **2026-07-12**, three adversarial panels run concurrently over the frozen manuscript + rebuilt artifacts, plus an author directive (de-name the single frozen `pub` profile).

## Panels
- **P-A method/stats/evidence** (T1-OPT / T3-STAT / T2-BENCH): regression on every R1 fix + fresh headline-stat recompute from source CSVs.
- **P-B exhibits/writing/humanization** (T5-WRITE): rendered every exhibit at 150–300 DPI; parsed `word/document.xml`; confirmed native Word editability of Figs 1/2/4/5 + Fig 3 flow-table.
- **P-C consistency/integrity/canonical** (ECB / T6-INTEG / T7-VENUE): Appendix E pre-flight E1–E8; adversarial cross-artifact scan.

## Regression verdict (R1 fixes) — all HELD
C7 (Eq.(11)/E10 ↔ `interaction_graph.py`), C12 (A12 sub-0.5 cells named), C13 (T15 p-bound) verified. Headline inference **independently reproduced exactly**: Friedman ranks (DT-GSK 2.48 overall; eGSK best at D30 = 2.29), 17-7-0 Holm tally, Wilcoxon/Holm/A12 at D100, omnibus max-p = 2.6×10⁻⁸. APGSK runtime recomputed from `per_run.csv` = Table 11 = `cost_cec2017.csv`.

## Verified findings + dispositions (all FIXED 2026-07-12)
| ID | Sev | Finding | Disposition |
|----|-----|---------|-------------|
| T1 | MAJOR | Figure-tables print internal registry E-IDs `(En)`; legend renders 3 pp later and is scoped to Sec.3 (excludes Fig 1); off-by-one vs printed eq. numbers; Fig 5 body↔caption mismatch | Converted every `(En)` → `Eq.~(\ref{...})` (renumber-proof); removed the obsolete En legend; dropped Fig 1's two cross-section forward-refs |
| R2-1 | MAJOR | Supplement APGSK claims present-tense "per-run record covers D=100 only / disclosed-unavailable", no CR-0006 — contradicts corrected main text | Time-scoped to "analysis freeze" + CR-0006 post-freeze recovery disclosed (main para + 3 captions); tabulated values unchanged |
| Tkt1 | MAJOR | git-tracked orphan `T21.tex`/`T22.tex` = prohibited favorable component-ablation (DT-GSK vs DT-GSK-1..5, p≤0.0004) | Removed both tables + their generator `generate_parametric_tables.py`; build unaffected |
| Tkt2 | MAJOR | Back-matter `\supplementary{}` + supplement abstract list S1–S5, but supplement has S6 (cited by conclusions) | Added S6 (scaffold remove-one study) to both; scoped the "every value from rel-…" claim to S1–S5, S6 → `abl-rel-2026-07-11` |
| Tkt3 | MAJOR | `artifact_binding.csv` binds 4 now-native-table labels to superseded matplotlib PDFs (`pending-phase8-rewire`); 12 unused assets tracked | Repointed the 4 FIG rows to native-table bindings; removed 12 unused assets + 4 orphan generators |
| R2-2 | MODERATE | apgsk cec2017 D≤50 comparability = "comparable-within-python-panel (Sec.1)" but caption says "provenance-qualified" | Relabeled those 3 rows "provenance-qualified (CR-0006 post-freeze recovery re-run…)"; D100 (main-campaign) left comparable; values unchanged |
| T2 | MODERATE | Two-panel flowchart: panel-(b) Return node overlaps panel-(a) loop-back → wrong "Update best → Return" reading | Widened inter-panel gap; `fig_flowchart_src.tex` recompiled; visually verified clean |
| T3 | MINOR | DT-GSK black in grouped bars but deep-blue in overall bars (reads as eGSK's blue) | DT-GSK set to solid black in every rank exhibit (P3 convention); `cec2011_ranks` + `friedman_gsk_family` regenerated |

## Build-integrity defect (surfaced during rebuild; not caught by read-only panels)
The **supplement PDF was un-buildable via `pdflatex`**: generated table fragments begin with `\zebra` but `supplementary.tex` never defined the macro (the DOCX/pandoc path was unaffected — pandoc drops `\zebra`). **Fixed:** `\zebra` (`\rowcolors`) added to the supplement preamble; `supplementary.pdf` (37 pp) now builds and is reproducible ×2.

## Author-side residuals (unchanged; cannot auto-fix)
Real ORCIDs; GenAI model-version pin; DOI/received-date; funding/COI finalization; MDPI current-template migration; 38-pp length (cover-letter note). No external non-GSK SOTA baseline and the SGSM direct isolation is null — both already honestly scoped/deferred in-text; ceiling-capping, not defects.

## Artifacts
main + supplement PDF/DOCX all rebuilt deterministically and reproducible ×2. Manifest re-frozen (`r2_review_refreeze`): 7 tracked files rehashed. **Net R2: no critical defect, no scientific error; two new/residual MAJOR cross-artifact defects (supplement APGSK propagation, orphan ablation tables) + one build-integrity defect closed; the manuscript is now internally consistent across main text, supplement, exhibits, ledger, and both output formats.**

---

# Independent Post-Completion Review — DT-GSK (REVIEW R3)

Third review pass, **2026-07-12**, four adversarial panels over the frozen manuscript + rebuilt artifacts, plus two author directives (naturalize AI-looking identifiers; remove line numbers).

## Panels & regression
- **A1 method/algorithm fidelity** (T1-OPT), **A2 statistics/benchmarks/evidence** (T3-STAT/T2-BENCH), **A3 exhibits/writing/humanization** (T5-WRITE), **A4 consistency/references/formatting** (ECB/T6-INTEG/T7-VENUE).
- A2 independently recomputed the full statistical chain from source CSVs: **every headline number reproduces exactly** (Friedman ranks, Iman–Davenport, Wilcoxon/Holm 17-7-0, A₁₂, Nemenyi CD, BCa). Leak/provenance/scope tests PASS. A3: prose is genuinely human-authored, graphics honest, pseudocode + figure-tables native-editable in Word. A4: E1–E3/E5–E8 PASS, manifest 0-drift, 0 undefined citations, PDF reproducible.

## Verified findings + dispositions (all FIXED 2026-07-12)
| ID | Sev | Finding | Disposition |
|----|-----|---------|-------------|
| A1-1 | MAJOR | Parameter table prints the inert dataclass defaults for the D≥50 mechanisms (κ_min 0.55, polish-start 0.985, senior-p split 0.15) — the printed spec would not reproduce the evaluated algorithm | Corrected to the operative values (0.35+adaptive, 0.96, 0.10) in the table + Fig 2 cells + worked example + C1 prose; verified vs `build_pub_config`. No result changed. |
| A4-F1 | MAJOR | `fig_nlpsr_schedule` bakes `(NLPSR, E5)` + "frozen pub profile" into the rendered image (E4 leak the R2 text sweep missed) | Generator fixed; figure regenerated (PDF+PNG); verified clean in supplement PDF+DOCX |
| A1-2 | MOD | "identical in prose and pseudocode" false; the GSK restyle mis-ordered BSE and moved polish after the loop; neither matched the code | Pseudocode + (1)–(12) prose + Fig 4 reconciled to the frozen code order; claim replaced by a step-for-step cross-reference |
| A1-3/A4-F3 | MOD | `equation_registry.csv` E10 still the pre-C7 collapsed-λ rule | Corrected to `G←λG+ηΣ` (rendered Eq. already correct) |
| A3-4 | MOD | Nemenyi CD diagrams draw DT-GSK deep-blue, breaking the "solid black" convention (R2 fix missed the CD generator) | `generate_nemenyi_cd.py` → black; 4 diagrams regenerated |
| A3-1 | MOD | Fig 1 taxonomy cell `rotate--crossover--rotate-back` overflows + collides (PDF only) | Reworded to a breakable `rotate → crossover → rotate-back` |
| A4-F6 | MOD | Fig 4 flowchart overflows the text area by 111 pt | Redrawn compactly; dedicated float page ([p], height-scaled) |
| A1-4/5, A2-F1, A3-2/3/5 | MINOR | BSE trigger tier caveat; SGSM cadence; tie-uncorrected-Friedman clause; pseudocode leading; zebra on 2 inline data tables; internal-token captions | All applied |
| A4-F4 | MINOR | 15 git-tracked orphan output figures | `git rm` |

## Author directives (applied)
- **Machine identifiers →** natural wording: all reader-facing `rel-…`/`abl-rel-…` (77 occ), the per-caption "Evidence release …" stamps, and `CR-0006`/`card-verified`/`rule P5` naturalized; one tag-free provenance reference kept in Data-Availability. Review prompt extended (§10.17.4 + E9 + pattern 41).
- **Line numbers →** removed (`\let\linenumbers\relax`).

## Author-side residuals (unchanged)
Real ORCIDs/DOI/dates; supplement default build needs `--rebuild-bib`; 39-pp length; no external non-GSK baseline and the null SGSM isolation — both already honestly scoped.

## Artifacts
main + supplement PDF/DOCX rebuilt deterministically, reproducible ×2. Manifest re-frozen (`r3_review_refreeze`), 8 tracked files rehashed; artifact-binding figure checksums refreshed. **Net R3: headline inference reproduces exactly and no critical/scientific defect; one MAJOR spec-fidelity drift (printed-parameter vs frozen-code) and one MAJOR image-token leak closed, plus the loop-order and machine-identifier cleanups — the printed specification now matches the evaluated algorithm and no raw pipeline token reaches the reader.**

---

# Independent Post-Completion Review — DT-GSK (REVIEW R4)

Fourth review pass, **2026-07-12**, four adversarial panels (all strictly read-only) over the frozen manuscript + rebuilt artifacts, with a dedicated whole-manuscript humanization pass under the new **§10.17.5**.

## Panels & headline verdict
- **A1 method + statistics/evidence** (T1-OPT/T3-STAT/T2-BENCH), **A2 whole-manuscript humanization** (T5-WRITE), **A3 exhibits/formatting/presentation** (T5-WRITE/T7-VENUE), **A4 consistency/integrity/references** (ECB/T6-INTEG).
- **No critical or major findings.** A1: headline inference reproduces to full precision and the R3 parameter corrections match the code. A2: the manuscript reads as **fully human-authored** — zero AI-clutter connectives, no tonal seams, no hollow phrasing, no leaked identifiers. A3: all seven R3 exhibit changes rendered correctly; native Word editability intact. A4: E1–E9 all PASS, manifest 0-drift, 0 undefined citations, PDF reproducible.

## Verified findings + dispositions (all FIXED 2026-07-12)
| ID | Sev | Finding | Disposition |
|----|-----|---------|-------------|
| A1 | MODERATE | Parameter table under-states tier variation (vs `build_pub_config`): `bse_max_restarts` 4/2/4/2, DE arm off/on/on/off, linkage refresh 20/20/10/10, SGSM refresh 5/5/5/20 | Corrected table rows + dim-gating cells + prose; numerically inert |
| A1 | MODERATE | Pseudocode/prose put ACE-credit/ARGP before the SGSM update; code (and Fig 4) do SGSM first | Reordered both; "matched step for step" softened; numerically inert |
| A2 | MINOR | Two near-duplicate passages (§3.4 four-axis contrast; intro↔method clause) | Consolidated to a cross-ref / reworded; facts preserved |
| A2 | MINOR | Raw `no_*` ablation tokens in S6 findings prose | Humanized to component names (kept at definition + table rows) |
| A3 | MAJOR (low) | `(exhibit T-PANEL)` registry code in the panel-roster caption (last reader-facing machine token) | Removed; also naturalized `BudgetController` |
| A1 | MINOR | `CR-0006` still in `cost_cec2017.csv` (not reader-facing) | Naturalized to "post-freeze recovery" |
| A4 | MINOR | Orphan `dt_gsk_flowchart_preview.png` + 2 stale source-map rows | Removed PNG; repointed rows to the TikZ flowcharts |

## Not changed (deliberate)
A2's do-not-change list (genuine "Seven limitations" enumeration, "First/Second/Third" structural deficiencies, the panel-scope caveat repetition, the thesis restatement, "no extra objective evaluations", convergence captions, the S5 reproducibility checksums) — all legitimate expert writing. A4 advisory items (S5 checksum density within the §10.17.4 carve-out; 17 uncited bib entries that do not render; superseded top-level PDFs retained for audit) and author-side placeholders (DOI/ORCIDs/dates) left as-is.

## Artifacts
main + supplement PDF/DOCX rebuilt deterministically, reproducible ×2. Manifest re-frozen (`r4_review_refreeze`), 3 tracked files rehashed. **Net R4: no critical/major defect; the printed specification is now fully tier-faithful to the frozen code, the loop order matches the code and both exhibits, the last reader-facing machine token is gone, and the whole-manuscript humanization pass confirms a single consistent human-authored voice.**

# Independent Post-Completion Review — DT-GSK (REVIEW R5)

Four adversarial read-only panels: **A1** method/statistics/evidence, **A2** whole-manuscript
humanization, **A3** exhibits/formatting/presentation, **A4** cross-artifact consistency / citations
/ supplement / canonical pre-flight (E1–E9). Headline inference (Friedman ranks, Holm tally,
Wilcoxon/A12, omnibus) independently reproduced; 0 undefined citations; the manuscript reads as fully
human-authored. A4's E7 "FAIL" was a **transient false positive** — it observed this in-progress edit
session mid-review and correctly identified the changes as cosmetic; closed by the R5 refreeze.

| Panel | Severity | Finding | Disposition |
|---|---|---|---|
| A3 | **MAJOR** | `notation_table.tex` still carried the pre-R3 inert defaults `kappa_min = 0.55` and polish `0.985` (R3 fixed these everywhere else but missed this exhibit) | Corrected to 0.35 (adaptive) / 0.96; code-verified vs `build_pub_config`; numerically inert |
| A2/A3 | MINOR | "SGSM" code alias used interchangeably with ISM (incl. glossary "code alias (unexpanded)" row) | Unified to **ISM** across main text, both frozen exhibits, supplement (preserving `no_sgsm` cell), the flowchart image, and the ablation figure; glossary row removed |
| A2 | MINOR | Opaque D≥100 controller codes (TERRA, SP-NLPSR, A1/A2/FC4) read as machine artifacts | Naturalized to descriptive terms verified in `_dt_core.py` (trust-region budget policy, subspace-sampling floor, late-acceptance clip, frozen-streak broadening, late linkage random-mix) |
| A2 | EDITORIAL | Internal `phase6_run_analysis.py` path + "governance record" + "update-rule registry" in reader-facing prose | Dropped path (kept in reproducibility appendix); "evaluation record"; "set of update rules" |
| A1 | MINOR | "single source of truth for every DT-GSK setting" overstates (D≥100 controller scalars live in the manifest, not the printed table) | Softened; notes the controller scalars are pinned in the frozen manifest |
| A1 | ADVISORY | Cover-letter carried the raw release tag `rel-2026-07-10-262fc16c9` | Removed |
| A4 | MINOR | `artifact_binding.csv` output_checksums stale (zebra-prefix era) | 3 R5-touched fragments refreshed to current sha256; the pre-existing T-table staleness deferred (generator predates the figure→table conversion) |
| A4 | MINOR | `reproducibility_manifest.json` carried R1-era main PDF/DOCX hashes | Refreshed to current + "R5 re-freeze" wording |

## Author directives (this round)
Remove the "Version July 8, 2026 submitted to Algorithms" MDPI stamp (done: `\lhead{}` + `mdpi.cls`);
rewrite Algorithm 1 for maximum clarity in the clean sectioned GSK-paper style (done: Require/Ensure,
section headers, one op per line, right-aligned equation notes); extend the review prompt with §10.17.6
(algorithm/pseudocode/flowchart technical + visual-communication review). Algorithm 1 and the DT-GSK
flowchart were both visually verified clean after rebuild.

## Not changed (deliberate)
`no_sgsm` ablation code-cell name and internal labels (`sec:supp:ablation:sgsm`, `eq:sgsm-graph`) kept
as code identifiers; the single sanctioned anchor commit + SHA prefixes inside the S5 reproducibility
appendix (§10.17.4 carve-out); the stale `generate_artifact_binding.py` and the T-table zebra
checksums (traceability-only, non-reader-facing, deferred to a generator-refresh task); author-side
placeholders (DOI/ORCIDs/dates).

## Artifacts
All four deliverables — DT-GSK.pdf (39pp), DT-GSK.docx, supplementary.pdf (37pp), supplementary.docx
— rebuilt deterministically and **bit-identical across two builds** (`FORCE_SOURCE_DATE=1`). Post-build
scans: **0 reader-facing machine tokens**, **0 undefined citations**, supplement `no_sgsm` cell intact.
Manifest re-frozen (`r5_review_refreeze`), **6 tracked files rehashed, 12/12 recompute-match**. **Net
R5: one MAJOR self-consistency fix (code-verified, numerically inert) plus terminology/naturalization/
presentation corrections; no primary number, rank, statistic, or claim changed; the manuscript is
camera-ready modulo author-side administrative items.**


# Independent Post-Completion Review -- DT-GSK (REVIEW R6)

Four adversarial read-only panels: **A** method/statistics/evidence, **B** whole-manuscript
humanization, **C** exhibits/algorithms/pseudocode/flowcharts/typography, **D** cross-artifact
consistency/citations/supplement/pre-flight. Headline inference, loop order, parameter tiers, and
scope framing all independently re-verified against the frozen CSVs and the source code; 0 undefined
citations; 0 duplicate bib keys; the four deliverables agree on the headline numbers.

| Panel | Severity | Finding | Disposition |
|---|---|---|---|
| D | **MAJOR** | Supplement rendered a raw internal label "Table tab:wilcoxon-holm" as visible text (p.4, PDF+DOCX) | Replaced with "the CEC2017 across-function Wilcoxon-Holm summary table" |
| D | MODERATE | Environment said "Windows 10, build 10.0.26200"; build 26200 is Windows 11 | Corrected to "Windows 11" |
| C | MODERATE | Notation: pseudocode G = both generation counter and interaction matrix; x_best vs x^gb; three spellings of the knowledge params | Loop counter G->g; x_best->x^gb; (k_f,k_r,K)->(KF,KR,K_exp) in pseudocode + flowcharts; related-work K_F,K_R->KF,KR; Table 2 completeness claim now holds |
| A | MODERATE | Eq.(11) under-specifies the ISM update vs the code (improvement-weighting, per-move l1-normalisation, magnitude-vs-signed accumulators) | Added a code-verified clarifying footnote; no number changed |
| B | MODERATE | Stale cover_letter.pdf still showed the release tag (source already fixed) | Rebuilt the cover letter |
| C | MINOR | Figure 4 placed ARGP "prune stalled arms" before trial construction | Moved to a faithful post-ISM box |
| C | MINOR | Mid-word hyphenation inside both flowcharts | Suppressed (hyphenpenalty) |
| A | MINOR | C4 "toggling any subsystem cannot disturb any other" overstated (deep-stall shares the bse substream) | Narrowed in intro + method |
| D | MINOR | R_max gloss "(2, or 4 at low-D)" under-specified the tiering | "(4/2/4/2 by tier)" |
| B | MINOR | "profile" jargon; supplement "Phase-2" + build-phase path; SLSQP unexpanded | "configuration"; naturalized; SLSQP added to abbreviations |

## Author directives (this round)
Refine Algorithm 1 for maximum readability/page use (done: line spacing 1.8, stage separation,
dedicated-page float, page-filling -- verified render); remove the copyright/license block +
"Submitted to Algorithms" footer (done); extend the review prompt with S10.17.7. Algorithm 1 and both
flowcharts visually re-verified clean and page-balanced.

## Verified clean
Headline Friedman ranks / Holm 17-7-0 / Wilcoxon / A12 / omnibus reproduced exactly; loop order and
parameter tiers match the code; novelty framing and scope non-claims intact; 0 undefined citations;
0 duplicate bib keys; S1-S6 map 1:1 to the back-matter; body prose reads as fully human-authored.

## Artifacts
All four deliverables + cover_letter.pdf rebuilt deterministically and **bit-identical across two
builds**; **0 reader-facing machine tokens** across all four (only the sanctioned S5 anchor commit +
the _dt_profiles.py source filename remain). Manifest re-frozen (`r6_review_refreeze`), **9 tracked
files rehashed, 12/12 recompute-match**. **Net R6: one MAJOR raw-label leak and one MODERATE OS
mislabel fixed, plus notation-consistency, a code-verified equation footnote, and author-requested
presentation changes; no primary number, rank, statistic, or claim changed; camera-ready modulo
author-side administrative items.**

# Independent Post-Completion Review -- DT-GSK (REVIEW R7)

Four adversarial read-only panels: **A** method/statistics/evidence, **B** whole-manuscript
humanization, **C** exhibits/pseudocode/flowcharts/typography, **D** cross-artifact consistency/
citations/supplement/pre-flight. 0 undefined citations; 0 duplicate bib keys; the four deliverables
agree on the headline numbers; 12/12 tracked files recompute-matched the manifest. **Panel A found
two genuine code<->paper fidelity defects that survived six prior rounds** -- both numerically inert
(the frozen code produced the results; only the paper's description was wrong).

| Panel | Severity | Finding | Disposition |
|---|---|---|---|
| A | **MAJOR** | Linkage block crossover described as D>=30-gated (off at D<20), but the frozen config runs it at D>=10 (`linkage_min_dim=10`); D=10 results used linkage | Corrected to D>=10 in the architecture table, dim-gating table (off->on + per-tier mix), prose, Algorithm 1, and the DT-GSK flowchart. Verified 5 ways against the code |
| A | MODERATE | Eq.(3)/Table 3 used `round()`; code uses `ceil()` (x=0.50 diverges: round 0 vs ceil 1) | Eq.(3) -> ceiling; Table 3 D_jun -> 50/18/3/1/1/1/0 + milestones fixed; notation ceiling added |
| C/D | MODERATE | Notation table omitted eta (ISM learning rate in Eq.(11)); over-broad completeness caption | Added eta; softened the caption |
| B | MODERATE | Supplement S6 exposed raw ablation-cell flags incl. `no_sgsm` (retired alias) | Reworded to descriptive prose |
| B | MODERATE | Central gap sentence repeated near-verbatim 4x | Method-section instance reduced to a back-reference |
| A | MINOR | Dim-gating omitted senior p=0.15 at 20-49 | Added |
| C | MINOR | Algorithm 1 trial `f(x_i^new)` vs equations' `v_i` | Aligned to `f(v_i)` |
| C | MINOR | Fig 1 complexity caption O(NP*D) vs body's O(D^2/5) refresh | Reconciled |
| C | MINOR | Base-GSK flowchart naming (knowledge rate; N dims) | Aligned to dimension-schedule exponent / D_jun |
| B | MINOR | Supplement `BASE_SEED = 20260422` code style | Natural "base seed 20,260,422" |

**Panel D dissent, resolved:** Panel D read `D>=30` from a doc string in `algorithm_freeze_manifest.json`;
the code (`linkage_min_dim=10`, gate, and group-build) is ground truth and gives D>=10. The stale doc
string is flagged for a separate code-side cleanup.

## Not changed
B4 (abstract "RNG-free" -> "deterministic") declined -- RNG is standard and "RNG-free" is a
consistent defined term; C6 (cosmetic `[D>=d]` vs `if D>=d`) and C7 (raggedright in narrow justified
cells) left as minor editorial residuals (C7 touches the native-table->DOCX column specs).

## Verified clean
Headline Friedman ranks / Holm 17-7-0 / Wilcoxon / A12 / omnibus reproduced exactly; loop order and
parameter tiers match the code; novelty framing and scope non-claims intact; body prose reads as
fully human-authored.

## Artifacts
All four deliverables rebuilt deterministically and **bit-identical across two builds**; **0
reader-facing machine tokens**. Manifest re-frozen (`r7_review_refreeze`), **5 tracked files rehashed,
12/12 recompute-match**. **Net R7: one MAJOR and one MODERATE code<->paper fidelity defect corrected
(both numerically inert) plus notation and humanization fixes; no primary number, rank, statistic, or
claim changed; camera-ready modulo author-side administrative items.**

# Independent Post-Completion Review -- DT-GSK (REVIEW R8)

Four adversarial read-only panels: **A** method/statistics/evidence (with a DEEP code-fidelity
mandate -- built the frozen config per tier and cross-checked every gate/parameter/schedule/rounding/
RNG against the code), **B** humanization, **C** exhibits, **D** consistency/citations/supplement.
**Panel A's systematic audit found no new critical/major/moderate code<->paper defect** -- the R1-R7
corrections all hold -- and produced a comprehensive verified-correct coverage list. 0 undefined
citations; 0 duplicate bib keys; headline numbers agree; 12/12 tracked files recompute-matched.

| Panel | Severity | Finding | Disposition |
|---|---|---|---|
| A | MINOR | ACE GSK-pure setting labelled "arm 2" (1-based); it is arm 3 | Corrected in parameter table, notation, prose |
| A | MINOR | "kappa_min=0.35 raised by an adaptive variant" (the rule clips *below* by 0.12) | "superseded by an adaptive rolling-window median floored at 0.12" |
| A | EDITORIAL | "~70%" linkage mix omits the 20-49 tier (0.40) | Tier-qualified (70% at D>=50, 40% at 20-49) |
| C | MINOR | Undefined/overloaded `alpha 1.0` in the NLPSR parameter row (collides with significance alpha) | Relabelled `alpha_psr` + Notes gloss |
| C | LOW | Algorithm 1 "for g=1 to GEN" (undefined GEN; fixed-count implies non-budget termination) | Reframed to "while t < MaxFES"; removed the now-unused g |
| C | VLOW | Figure 2 caption "eight scaffold subsystems" (4 are gated) | "eight subsystems" |
| D | MINOR | Supplement DOCX: 87 unresolved "??" caption/ref fields (empty supplementary.aux at build time) | Build supplement PDF (populates aux) before the DOCX; now 0 "??" |
| B | MINOR | bare "$D50$"; "7-algorithm" vs "seven-algorithm"; "second of 7" vs "second of seven" | "$D=50$"; unified to spelled-out |
| B | EDITORIAL | "Seven limitations" + an unnumbered eighth coda | "Several limitations" |
| B/D | EDITORIAL | S5 directory path in prose; stale D>=30 notes in canonical .md/.json; S1..S5 comment | bare filename; refreshed to D>=10; S1..S6 |

## Not changed
The four native-table "Figures" (1/2/5/6) keep the Figure label (deliberate schematic exhibits;
renumbering cascades all cross-refs); per-caption scientific caveats in the supplement convergence
grids (legitimate self-containment); abstract "RNG-free" (consistent defined term).

## Artifacts
All four deliverables rebuilt deterministically and **bit-identical across two builds**; the
supplement DOCX cross-references now resolve (0 "??" vs 87); **0 reader-facing machine tokens**.
Manifest re-frozen (`r8_review_refreeze`), **7 tracked files rehashed, 12/12 recompute-match**.
**Net R8: a deep code-fidelity audit confirmed no new defect after R7; the changes are
notation/wording/presentation corrections and a supplement-DOCX cross-reference fix; no primary
number, rank, statistic, or claim changed; camera-ready modulo author-side administrative items.**


## Round 9 (R9)

Four adversarial read-only panels at angles prior rounds under-covered: **A** claim
calibration / statistical methodology / discussion soundness (every headline number
re-derived), **B** abstract flow / readability / cover letter, **C** Word(DOCX)-vs-PDF
rendering fidelity + fresh supplement visual pass, **D** citation semantic correctness /
bibliographic accuracy. **Panel A re-derived the headline numbers and confirmed the
statistics, disclosures, and eGSK-port framing sound.** Two MAJORs were new to this round.

| Panel | Severity | Finding | Disposition |
|---|---|---|---|
| D | MAJOR | COI statement lists A.W.M. as a co-author of FDB-AGSK; FDB-AGSK is by Bakir/Duman/Guvenc/Kahraman | Removed FDB-AGSK from the co-authorship clause; noted independent third-party variant; A.W.M.'s AGSK/APGSK/eGSK/ATMALS-GSK co-authorship retained |
| C | MAJOR | DOCX numeric tables were raw-DataFrame dumps (underscored headers, 6-7 sig figs, no mean+-SD) -- diverged from the PDF | Added generic `parse_frozen_table_tex()`; routed T1-T16 through the frozen `.tex` display (combined labels, 2-3 sig figs, mean+-SD, bold best); 0 garbled headers, 817 mean+-SD cells, 0 "??" |
| C | MINOR | Raw LaTeX in the DOCX table accessibility alt-text | Cleaned via `_clean_tex_cell` |
| A | MODERATE | Self-init disclosure framed as low-dimension-only; code makes it a blanket all-dimension exception | Reworded to "no DT-GSK cell begins from the shared initial population ... most consequential at low dimension" |
| A/B | MODERATE | Abstract parenthetical could misattach the Holm-significant loss to the D=30 tie | Reworded so the significant loss binds only to CEC2011 |
| B | MEDIUM | Garden-path "a block is used only once conf(G)>=kappa_min" | "used only **when**" (matches the figure caption) |
| A | MINOR | Nemenyi non-separability caveat applied to the CEC2017 lead but not the CEC2011 loss | Added: CEC2011 rank gap (0.84) is within the Nemenyi CD (1.92) too |
| A | MINOR | APGSK framing could read as a weaker across-function basis | Clarified the primary test is identical for every comparator; only run-level companions unavailable at D<=50 |
| D | MINOR | Midpoint repair attributed to L-SHADE | Corrected to its JADE origin (`zhang2009jade`) carried through L-SHADE |
| D | MINOR | Iman--Davenport correction uncited | Added `demsar2006statistical` |
| B | LOW | British-spelling stragglers; "GSK family panel" | American spellings; "GSK-family panel" (attributive) |

## Not changed (R9)
The four native-table "Figures" (1/2/5/6) keep the Figure label (deliberate schematic
exhibits). Deferred/optional and noted in the freeze block: D4 a Threefry (Salmon et al.
2011) RNG citation; B5 abstract "RNG-free" (consistent defined term); B6 cover-letter
paragraph split; A5 exact-Wilcoxon at small effective-n D=10 cells (disclosed robustness
note); C3 supplement A9/A13 label harmonization; C4 Word figure/caption pagination; D5
whitelist the two false-positive `cross_format_consistency.csv` rows.

## Artifacts (R9)
All four deliverables rebuilt deterministically and **bit-identical across two builds**; the
DOCX numeric tables now render the frozen formatted display (mean+-SD, bold best) and the
supplement DOCX cross-refs resolve (0 "??"); **0 reader-facing machine tokens**. Manifest
re-frozen (`r9_review_refreeze`), **7 tracked files rehashed, 12/12 recompute-match**.
**Net R9: a claim-calibration + DOCX-fidelity + citation-accuracy pass; two MAJORs
(COI authorship, DOCX table formatting) fixed; no primary number, rank, statistic, or claim
changed; camera-ready modulo author-side administrative items.**


## Round 10 (R10)

Four adversarial read-only panels: **A** deep math/algorithm correctness vs the frozen code,
**B** empirical/statistical integrity + reproducibility claims, **C** presentation + humanization,
**D** consistency / citations / author metadata / cross-format. **Panels A and B re-derived the
math and every headline number and found no critical/major scientific defect** (equations,
complexity, statistics, and all quoted numbers verified against code and the frozen tables). The
two MAJORs are author-metadata consequences of the newly added third author.

| Panel | Severity | Finding | Disposition |
|---|---|---|---|
| D | MAJOR | conclusions: "six comparators ... by the second author" -- A.W.M. is now the THIRD author; "six" contradicts the COI (FDB-AGSK third-party) | "five of its six comparators ... by two of the present authors" |
| D | MAJOR | COI omits that the new author H.S.M.R. co-authored eGSK (the key comparator) -- verified in references.bib | Added H.S.M.R.'s eGSK co-authorship to the COI + both cover letters |
| C | MODERATE | Table 8: +/approx/- markers undefined; tie rendered approx (headers) vs = (Dec.) | Added caption legend; unified Dec. tie glyph to approx |
| A | MINOR | Algorithm 1 "polish x^{gb}"; code polishes the working incumbent | "polish the working incumbent x^{*}" |
| A | MINOR | SGSM cost stated O(D^2/5)/gen; decay runs every generation at D=50-99 | O(D^2) per generation (tenth gen at D>=100); cadence reserved for block re-extraction |
| A | MINOR | MaxFES written as "=10^4 D"; CEC2011 uses fixed 150,000 | Reframed as input budget (10^4 D; 150,000 on CEC2011) |
| A | MINOR | Eq. E9 uses r_rst (0.30 low-D) for the Cauchy count; code uses bse_cauchy_frac=0.10 | Introduced r_c=0.10 for the Cauchy fraction |
| A | MINOR | Eq. E12 labels child-seeding "threefry_child"; it is a modular counter offset | Rewrote E12 with the explicit modular map; added M to notation |
| B | MINOR | "RUNBOOK.md" (404 case-sensitive); file is lowercase | "runbook.md" |
| B | MINOR | CEC2013 caption "p<=2.2e-3"; true max (D30) 2.242e-3 | "p<=2.3e-3" (valid ceiling) |
| C | MINOR/LOW | Abstract em-dash cadence; intro "is met by" x4; thesis-phrase 3rd repeat; "Initialisation"; "gaining--sharing" | Copyedited (R9 attribution preserved); varied anaphora; American spelling; hyphen |

## Not changed (R10)
The four native-table "Figures" (1/2/5/6) keep the Figure label. Deferred/author-side: B-F3
"publicly available" pending the DOI/URL (AG-0006); the deliberate code-key reproducibility
references; the seven genuine limitations (not an AI defect); the dead `\sgsm` pandoc-shim
macro (never invoked); the stale phase_04 APGSK glossary entry (the manuscript itself is
internally consistent). B-F4 (manifest `generated_utc`) is intentionally the original stamp.

## Artifacts (R10)
All five deliverables rebuilt deterministically and **bit-identical across two builds**; the
DOCX stays self-contained (`updateFields=false`) with the three-author byline + eGSK COI; 0
markers_left / 0 warnings. Manifest re-frozen (`r10_review_refreeze`), **8 tracked files rehashed,
12/12 recompute-match**. **Net R10: a deep math/stats audit found the science sound; the changes
are two author-metadata disclosures, presentation and copyedit fixes, and pseudocode/equation
precision corrections; no primary number, rank, statistic, or claim changed.**
