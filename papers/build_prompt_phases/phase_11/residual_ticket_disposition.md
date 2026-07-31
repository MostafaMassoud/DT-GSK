# Phase 11 — Residual (Gate-10 Deferred) Ticket Disposition

- **Phase:** 11 (Primary manuscript finalization + pre-ablation freeze)
- **Date:** 2026-07-11
- **Author/runner:** Phase 11 finalization workflow
- **Inputs:** `papers/governance/revision_tickets.csv` (35 deduped Gate-10 tickets),
  `papers/build_prompt_phases/phase_10/PHASE_10_gate_report.md` Section 5 (carry-forward),
  `papers/build_prompt_phases/phase_10/revision_log.md`.
- **Binding constraint:** Phases 0–10 FROZEN. The frozen algorithm, evidence release
  `rel-2026-07-10-262fc16c9`, and every bound number are IMMUTABLE. Phase 11 closes/records
  residuals only; it performs **NO** new experiments and adds **NO** ablation content.
  None of the residuals below blocks the Phase-11 content freeze.

## 0. Disposition legend

| Class | Meaning | Timing / owner |
|---|---|---|
| **figure-refresh** | Fix baked into a pre-rendered, checksum-bound figure/notation asset; requires re-render + rebind of the asset (change-control on a bound artifact). | Post-Phase-12 controlled figure-refresh pass |
| **author-side** | Needs a human decision or an artifact only the author can supply (persistent DOI, title identity, Word open-save). Must NOT be fabricated. | Author, pre-submission |
| **resolves-on-commit** | Repo-hygiene item that clears when the finalization commit lands (clean working tree). | This phase's commit (or accepted-as-is) |
| **Phase-12 (analysis/evidence)** | Requires new analysis or a new baseline run on the immutable evidence = change-control; explicitly the sole final implementation phase's scope. | Phase 12 |
| **RECORDED (Word cosmetic)** | Current shipped output is correct; a low-value/high-regression-risk generator tweak is recorded, not applied. | Build-tooling pass / author Word finalization |

All figure-refresh items were already given a **turn-key remap** in Gate 10 (recorded below and in
`revision_tickets.csv`) so the post-Phase-12 pass is mechanical.

## 1. Master disposition table (every Gate-10 deferred / recorded ticket)

| Ticket | Sev | Location | Defect (short) | Disposition | Blocks freeze? |
|---|---|---|---|---|---|
| **R4-T1** | major | Figs 1–4; Fig.4 caption vs graphic | Conceptual figures label equations with an `E#` scheme misaligned with Eq.(1)–(13); Fig.4 graphic `(E10)/(E4)/(E11)/(E8)` contradicts its own caption Eq.(11)/(5)/(12). | **figure-refresh** (post-Phase-12) | No |
| **R4-T2** | major | Fig.1 (taxonomy) header | Prints raw BibTeX keys `[omidvar2014dg]/[hansen2001cmaes]/[guo2015eig]` instead of numeric `[22]/[23]/[24]`. | **figure-refresh** (post-Phase-12) | No |
| R4-T3 | minor | Figs 1/3/4; Table 4 caption | Internal repo paths (`novelty_scope.md`, `phase_03/complexity_analysis.md`, `algorithm_freeze_manifest.json`) baked into figure text. | **figure-refresh** (post-Phase-12) | No |
| **R4-T4** | minor | Table 2 header; Figs 2/3/4; Abbrev. | `SGSM` code alias duplicated alongside `ISM` in bound exhibits (Abbreviations list already discloses SGSM correctly). | **figure-refresh** (post-Phase-12) | No |
| **R4-T6** | minor | Figs 7–10 (Nemenyi CD) | Titled "Nemenyi Critical Difference" / cite Demšar but are bar+band charts, not canonical CD diagrams with clique bars. | **figure-refresh** (post-Phase-12; retitle graphic+caption together) | No |
| **R1-3** | minor | main.tex Title; CL-02/LM-05 | "High-Dimensional" vs the D=100 evidence ceiling. Title is bound across cover letter, PDF metadata, running head — an identity change. | **author-side** (softened alt. recorded for sign-off) | No |
| **R3-4** | minor | main.tex Data Availability; AG-0006/R-0004 | No persistent citable locator (DOI/Zenodo/URL). main.tex already carries "do not fabricate a URL here." | **author-side** (mint DOI at submission; MUST NOT fabricate) | No |
| **R3-5** | minor | governance/artifact_binding.csv | All 55 bindings stamp `commit_sha 010f6d72…-dirty` (uncommitted tree); numbers are `output_checksum`-pinned so values are locked, provenance commit is not clean. | **resolves-on-commit** (regenerate from clean commit, or accept-as-is) | No |
| R5-1 | minor | DT-GSK.docx TOC vs PDF | DOCX carries a "Contents" TOC the PDF lacks. Native field, `updateFields=true`; author deletes at finalization. | **RECORDED** (Word cosmetic; D-WORD-01 author surface) | No |
| R5-2 | minor | DT-GSK.docx customXml citation DB | Citation DB stamped `StyleName='IEEE'` on an MDPI-numeric manuscript. IEEE `[n]` ≡ MDPI `[n]`; reference list is static text; no MDPI `.xsl` exists. | **RECORDED** (Word cosmetic; changing risks cache breakage) | No |
| R5-4 | minor | DT-GSK.docx footnotes.xml.rels | Orphaned DOI hyperlink Relationship entries the empty footnotes never reference (package bloat). | **RECORDED** (Word cosmetic; no content/validation impact) | No |
| R1-1 | major | performance.tex Discussion; IN-02; AB-01..03 | Named central mechanism's causal payoff deferred; main text says only "consistent with" design intent. | **Phase-12** (component study = new analysis; prose already hedged R2-6) | No |
| R1-5 / R6-T04 | major | tab:panel; conclusions Limitations; LM-03 | No external non-GSK / structure-learning baseline; panel is within-family. | **Phase-12** (evidence); **prose FIXED** (Limitation Seventh states the absence as a scientific threat) | No |
| R6-T01 | major | IN-02 sites | Central primitive credited for high-D gains while its only direct isolation (orphan 4-cell) is null. | **Phase-12** (isolation ships in S6); **prose hedged** (R2-6); orphan pointer would dangle | No |
| R6-T03 | major | CEC2017 headline; S5 | CEC2017 6-config selection exposure not surfaced beside the headline. | **Phase-12** (tuning-protocol disclosure); shipped text makes no "development suite" claim | No |
| R6-T05 | minor | proposed_algorithm nlpsr | NLPSR (C3) D100 justification cell not run. | **Phase-12** (cell); **RESOLVED-already-scoped** in shipped prose (no empirical NLPSR-superiority claim) | No |
| R6-T06 | minor | conclusions Limitations; PR-06 | Self-init shared-X0 fairness asymmetry not bounded by a control run. | **Phase-12** (control run); **prose FIXED** (Limitation Seventh) | No |

Cross-check: 17 tickets above == the 12 DEFERRED + 3 RECORDED + 2 of the "prose-fixed / evidence-deferred"
split rows in `revision_tickets.csv`. The remaining 18 Gate-10 tickets were FIXED (15) or
REJECTED-INVALID (3) in Phase 10 and are not residuals.

## 2. figure-refresh bundle (R4-T1/T2/T3/T4/T6) — why deferred, and the turn-key remap

The four conceptual figures (Fig.1 taxonomy, Fig.2 architecture, Fig.3 dim-gating, Fig.4 SGSM
mechanism) and the Nemenyi panels (Figs 7–10) are **pre-rendered PDF/PNG assets bound with SHA-256
chains in `papers/governance/artifact_binding.csv`**. Fig.2 (architecture) is exported from a
`.drawio` source that is not regenerable in this non-interactive environment, so regenerating a
subset would leave an internally inconsistent figure set. Editing a caption alone would desync the
caption from the baked graphic. Therefore all five are correctly **change-controlled to a single
post-Phase-12 figure-refresh pass** — the standing directive schedules the two majors (R4-T1/T2) as
the priority items there. **Content freeze is not blocked:** every equation/number the figures
gloss is stated correctly in the manuscript body; the defects are asset-label cosmetics.

Recorded turn-key remap (from Gate 10, ready for the refresh pass):

- **Equation labels (R4-T1):** E4→Eq.5, E5→Eq.6, E7→Eq.8, E8→Eq.9, E9→Eq.10, E10→Eq.11,
  E11→Eq.12, E12→Eq.13; reconcile Fig.4 graphic labels to its caption Eq.(11)/(5)/(12)/(9).
- **Taxonomy keys (R4-T2):** `[omidvar2014dg]`→[22], `[hansen2001cmaes]`→[23], `[guo2015eig]`→[24].
- **Repo paths (R4-T3):** strip `*.md`/`*.json`/module paths; e.g. "per phase_03/complexity_analysis.md" → "(Section 3.8)".
- **Alias (R4-T4):** render `ISM` uniformly in reader-facing exhibits; keep `SGSM` only as the disclosed code alias.
- **CD diagrams (R4-T6):** retitle graphic + caption together to "mean-rank chart with a critical-difference reference band," or render true Demšar clique-bar diagrams.

## 3. R3-5 — resolves-on-commit (explicit note per Phase-11 task 2)

`artifact_binding.csv` currently stamps `commit_sha = 010f6d7224784347e5872578c1687f2f1b5093ab-dirty`
across all 55 rows (verified 2026-07-11). The `-dirty` suffix records that the generator tree was
uncommitted when the bindings were minted. **Numbers are not at risk:** each exhibit is pinned by its
`output_checksum` to the immutable release `rel-2026-07-10-262fc16c9`, so values are byte-locked
regardless of the generator commit state (the four validators in this phase confirm PDF↔DOCX↔source
value identity).

Two acceptable closures, both non-blocking:

1. **Regenerate on commit** — after the Phase-11/12 finalization commit lands (clean working tree),
   re-run `papers/scripts/generate_artifact_binding.py` so `commit_sha` re-stamps to the clean HEAD
   (currently `cffcbb481`). This is repo-hygiene, not a number change.
2. **Accept as-is** — because `output_checksum` already guarantees byte-identical regeneration of every
   value, the `-dirty` provenance stamp may be accepted and the re-stamp folded into the Phase-12
   governance cleanup.

Recommendation: **accept-as-is for the Phase-11 freeze**; fold the clean re-stamp into Phase 12 so the
binding manifest is regenerated once, after the ablation exhibits are added, rather than twice.

## 4. author-side items (R1-3 title, R3-4 DOI) and Word cosmetics

- **R1-3 (title):** "High-Dimensional" is standard usage for D≤100 in the DE/GSK/CEC literature and the
  body already bounds it (explicit D=100 ceiling, no LSGO claim). The title is the paper's identity
  (cover letter CL-02, PDF metadata, running head), so it is not altered unilaterally on a frozen
  artifact; a softened alternative is recorded for author sign-off.
- **R3-4 (DOI):** the durable archive DOI/URL and submission account are author-side (AG-0006 / R-0004);
  main.tex already comments "do not fabricate a URL here." Recorded for author insertion at submission.
- **Word cosmetics (R5-1/2/4):** the current DOCX output is correct and `validate_docx.py` reports
  `"ok": true` on both documents. These are low-value/high-regression-risk generator tweaks (or the
  D-WORD-01 author Word-finalization surface), recorded rather than applied.

## 5. Freeze impact

**None of the residuals blocks the Phase-11 content freeze.** The figure defects are pre-rendered
checksum-bound asset cosmetics; the author-side items require a human or a locator that must not be
fabricated; R3-5 is provenance hygiene with numbers already checksum-pinned; the analysis/evidence
majors are the explicit, change-controlled scope of Phase 12 (the sole final implementation and sole
ablation phase). Every FIXED Gate-10 ticket is verified in the shipped PDF/DOCX (Phase 10), and the
Phase-11 primary integrity audit (`final_primary_integrity_audit.md`) re-confirms citations, claims,
numbers, source-only discipline, cross-format parity, and Word native fields all PASS.
