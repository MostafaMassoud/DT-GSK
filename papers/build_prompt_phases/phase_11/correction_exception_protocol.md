# Correction-Exception Protocol — Phase-12 Rules for the Frozen Primary Manuscript

**Phase / task:** Phase 11, task 13 — define, *before* the Phase-12 ablation runs, the only
conditions under which the `FROZEN_BEFORE_ABLATION` primary manuscript may be touched, and the
things Phase 12 may never do. This protocol mirrors and operationalizes the G0 guard of
`papers/build_prompt_phases/phase_10/ablation_correction_triggers.md`.

- **Anchor commit:** `cffcbb48153fd6395c67bb35ece0107269c15694`
- **Evidence release:** `rel-2026-07-10-262fc16c9`
- **Governs:** `main.tex`, `sections/*.tex`, `DT-GSK.{pdf,docx}`, `claims_evidence_matrix.csv`,
  `citation_usage_map.csv`, `artifact_binding.csv`, `references.bib` (the
  `main_manuscript_freeze_manifest.json` set) and the supplement freeze set.

---

## G0 — Governing invariant (one-directional safety net)

The Phase-12 component ablation is deferred, immutable-evidence-reopening analysis. When its
results land they may do **only one** of two things:

1. **Ship as new Phase-12 supplement findings** (exhibits AB-01/02/03, S6 slot), scoped to the
   supplement build; **or**
2. **Trigger a text-only narrowing/correction** of a frozen main-text claim, **if and only if the
   result is unfavorable** (contradicts current wording) per the trigger table in
   `ablation_correction_triggers.md`.

**Direction is fixed:** *unfavorable → narrow the identified claim; favorable → supplement-only,
never back-ported.* A favorable ablation can never be used to strengthen or upgrade a shipped
claim inside this paper.

---

## 1. Material-contradiction thresholds (when correction is PERMITTED)

A Phase-12 result crosses the correction threshold for a frozen claim only when **all** hold:

1. **Pre-registered target.** The claim is one listed in the `ablation_correction_triggers.md`
   trigger table (T-1…T-8: e.g. IN-02, LM-02, MT-03/§3.3.3, MT-06/07, MT-09/C2, RS-01/HL-01/CN-01).
   Claims not in that table are not correctable by ablation.
2. **Contradiction condition met.** The specific unfavorable outcome registered for that claim is
   observed — a **statistically supported** contrast under the pre-registered machinery (paired
   Wilcoxon + **Holm** within the (study, dimension) family, α = 0.05, with its effect size and BCa
   interval), computed from the **Section-2.4-promoted immutable ablation release** via the
   strict-source guard. A single unadjusted p-value, a descriptive rank flip, or a staging-only
   number is **not** a material contradiction.
3. **Identifiability satisfied.** The mechanism was ON in `baseline`/`full` at the dimension in
   question (per-dimension baseline-ON check); "null contrast" cells (mechanism inactive in the
   reference) never trigger a correction.
4. **Direction is unfavorable.** The result narrows, not strengthens, the claim.

When the threshold is crossed, the mandated edit is the **exact correction trigger** registered for
that claim (narrow/drop clause / add caveat / editorial demotion) — nothing broader.

---

## 2. PERMITTED in Phase 12 (text-only)

- **Narrowing or correcting** a triggered frozen claim by the registered edit — deleting an
  over-reaching clause, restating an effect as bundled/tier-scoped, or adding a limitations/caveat
  sentence. Text only; the shipped **numbers, equations, labels, figures, and bundle stay
  unchanged**.
- **Disclosure additions** required by Phase-12 deliverables (e.g. the R6-T03 tuning /
  selection-exposure caveat beside the CEC2017 headline) — a pointer/caveat, not a number change.
- **Shipping ablation findings in the supplement build only** — the reserved S6 slot
  (`supplementary.tex`), with AB-01/02/03 exhibits, full identifiability and overhead disclosures.
- **Applying the deferred, change-controlled editorial fixes** already scheduled (figure defects
  R4-T1/T2) under their own change-control tickets — independent of ablation sign.

Any permitted correction is logged in `change_request_register.csv` (Section 12.2), re-runs the
integrity checks (number-binding, citation, cross-format parity, no-ablation scan against the
*shipped main* artifact — which must remain PASS), and updates the affected freeze manifest hash.

---

## 3. PROHIBITED in Phase 12 (hard stops)

- **Algorithm redesign** of any kind. The frozen core hashes
  (`algorithm_freeze_manifest.json` = `88dbabd4…`; `dt_gsk.py` a274e0f8 / `_dt_core.py` 1ef815ce
  / `_dt_profiles.py` c3dcdce3 / `_dt_rng.py` db1cc028) are immutable; no code/config change "in
  response to any result."
- **New primary tuning** or any new primary benchmarking run. The primary release
  `rel-2026-07-10-262fc16c9` and its analysis bundle are frozen; Phase 12 adds only a *separate*
  ablation release.
- **Main-text ablation results.** No ablation number, rank, p-value, effect size, overhead value,
  cell result, or component-causality/efficacy statement may enter `DT-GSK.{pdf,docx}` or its
  sources. Ablation content is admissible in the **supplement build only**.
- **Upgrading any existing claim from a Phase-12 result.** A **favorable** ablation may **not**
  convert IN-02's "consistent with the intended role … per-component attribution deferred" into a
  causal/efficacy claim, nor upgrade IN-01, RS-01…11, CN-01, HL-01, or contributions C1–C4, nor
  assert eGSK head-to-head dominance at D50/D100. Such an upgrade would require re-opening the
  frozen artifact under full change-control **and** a fresh integrity review — it is **not** a
  Phase-12 deliverable.
- **Back-porting** any Phase-12 number into the shipped PDF/DOCX. The frozen manuscript stands on
  its current non-causal, within-family evidence regardless of Phase-12 sign.

---

## 4. Enforcement hooks (run at Phase 12)

- Re-run the `no_ablation_tokens_any_part` guard (`validate_docx.py`) and the parity
  `no_ablation_scan` against the **shipped main** artifact; both must remain PASS (ablation prose
  lives only in the supplement build).
- Keep the IN-02 blocked-wording guard active in Phase-12 review.
- Every correction classified as **confirmatory amendment** or **exploratory deviation** (Phase-5
  exit rule); silent deviation invalidates the affected analysis.
- Any frozen-artifact touch updates the corresponding entry in the Phase-11 freeze manifests and
  is recorded in `change_request_register.csv` with the crossing threshold that authorized it.

**Invariant restated:** the shipped main text contains **zero** component-causality or
component-efficacy statements today; therefore no Phase-12 result can retroactively justify an
existing claim — it can only leave the claim intact (supplement adds new causal analysis) or force
a one-directional narrowing.
