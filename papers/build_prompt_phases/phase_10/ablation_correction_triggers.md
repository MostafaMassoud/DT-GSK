# Phase 10 — Ablation Correction Triggers (pre-ablation registration)

**Purpose.** The Phase-12 component ablation (`AB-01` scaffold, `AB-02` SGSM-overlay,
`AB-03` polish toggle) is deferred, immutable-evidence-reopening analysis. This register
fixes, *before any ablation is run*, (i) which frozen main-text claims a Phase-12 result
could **contradict**, (ii) the exact **correction trigger** for each, and (iii) the
**governance guard** that prevents the ablation from being retro-fitted to *strengthen*
existing claims. It is written now so that the sign of the Phase-12 outcome cannot be used
to author-launder the deferral.

**Authorities.** `papers/governance/claims_evidence_matrix.csv` (claim IDs + permitted/blocked
wording), `papers/build_prompt_phases/phase_06/negative_findings.md`, evidence release
`rel-2026-07-10-262fc16c9`. The 4-cell CEC2013-D50 pilot cited in ticket **R6-T01**
(reported null: p≈0.056, W/T/L 5/10/13) lives **only** in the unbuilt orphan
`sections/supplementary_content.tex` and is **not** on the shipped record; it is treated here
as a *prior expectation of a possible null*, never as evidence.

---

## G0 — Governance guard (the deferral must stay a genuine open question)

Component causality is deferred by `IN-02`, `LM-02`, and `AB-01/02/03`
(`DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`). Therefore, when the Phase-12 ablation lands, its
results may do **only** one of two things:

1. **Ship as new Phase-12 supplement findings** (`AB-01/02/03`), scoped to the supplement; or
2. **Trigger a narrowing/correction** of a claim listed in the table below, **if unfavorable**.

They may **NOT**:

- be cited to *upgrade* any existing main-text claim (`IN-01`, `IN-02`, `RS-01..11`,
  `CN-01`, `HL-01`, contributions `C1–C4`) from "consistent with / proposed and specified"
  to a causal/efficacy claim. A **favorable** ablation does **not** convert `IN-02`'s
  "consistent with the intended role of the interaction-structure memory" into "the ISM
  causes the D≥50 gain" inside *this* paper. Any such upgrade requires re-opening the frozen
  artifact under full change-control and a fresh integrity review — it is not a Phase-12
  deliverable.
- be back-ported into the shipped PDF/DOCX numbers. The frozen manuscript stands on its
  current non-causal evidence regardless of Phase-12 sign.

**Verification hook.** At Phase 12, re-run the `no_ablation_tokens_any_part` guard
(`validate_docx.py`) and the parity `no_ablation_scan` against the *shipped* main artifact;
both must remain PASS. Ablation prose is admissible in the *supplement build only*.

---

## Trigger table

Legend — **Contradiction condition**: the Phase-12 outcome that would make the current
wording an over-statement. **Correction trigger**: the mandated edit **if** that condition
holds. Directionality (G0) governs the favorable case.

### T-1 · IN-02 — central "ISM intended role at D≥50"
- **Claim (shipped):** high-D behavior is *consistent with the intended role of the
  interaction-structure memory … the D≥50 tier activates several subsystems together … the
  bundled tier configuration rather than any isolated component … per-component attribution
  deferred (Sec. 5).* (Exhibits F02 D50/D100, T05 D50/D100, Table 7.)
- **Phase-12 test:** `AB-02` SGSM-overlay cells (full / no-adaptive / no-sgsm).
- **Contradiction condition:** the SGSM-overlay isolation shows **no significant D≥50
  benefit** (replicates the quarantined-pilot null), *or* a **net-negative** SGSM effect.
- **Correction trigger:** *narrow IN-02* — delete "consistent with the intended role of the
  interaction-structure memory"; restate high-D behavior as associated with the bundled
  D≥50 tier only, and add an explicit sentence that the direct SGSM isolation did **not**
  confirm a standalone benefit. Mirror into `LM-02` and the `C1` framing.
- **Favorable case (G0):** a positive isolated SGSM benefit ships in the Phase-12 supplement
  (`AB-02`); `IN-02` is **not** upgraded to causal in this paper.

### T-2 · LM-02 — low-D gating attribution
- **Claim (shipped):** structure-memory/polish gated to D≥50; low-D "reflects this
  structural gating rather than the headline mechanisms"; *per-component attribution is not
  claimed* (line ~3165).
- **Phase-12 test:** `AB-01` scaffold cells at D10/D30 (ACE, ARGP, NLPSR, BSE, linkage,
  archive, LS toggles).
- **Contradiction condition:** a scaffold component is shown to *materially cause* the low-D
  weakness (i.e., low-D deficit is a specific component's fault, not gating).
- **Correction trigger:** replace the "structural gating" explanation with the identified
  component attribution **in the supplement**, and add a limitations caveat in the main text
  that the low-D account is refined by the Phase-12 study. Do **not** retro-edit the shipped
  low-D numbers.

### T-3 · MT-03 / §3.3.3 — NLPSR tier-floor rationale (R6-T05 residual)
- **Claim (shipped):** NLPSR is *explicitly not claimed as new* (lines 178, 646, 1327); the
  tier floor is justified as *preserving parallel samples for the structure memory at high
  dimension*. No empirical NLPSR-superiority is claimed.
- **Phase-12 test:** `AB-01` scaffold **D100** cell — the sole justification tier for NLPSR
  (never run; R6-T05).
- **Contradiction condition:** at D100, NLPSR is **dominated by** plain LPSR (as the
  quarantined pilot suggested for D10/30/50).
- **Correction trigger:** remove the high-D floor *justification* clause (keep NLPSR as a
  described, not-new schedule). Because the shipped text makes **no** NLPSR benefit claim,
  a null result at D≤50 needs **no** correction (already scoped) — only a **D100** null
  touches the rationale.

### T-4 · MT-06 / MT-07 — BSE escape & deep-stall restart (effectiveness pre-blocked)
- **Claim (shipped):** BSE and the deep-stall restart are described as design/budget-safety
  facts; `MT-06`/`MT-07` **already block** any effectiveness claim ahead of Phase 12.
- **Phase-12 test:** `AB-01` BSE / restart toggles.
- **Contradiction condition:** *none for a null* — a null or negative BSE/restart result is
  already consistent with the shipped text (no efficacy claimed). This row exists to enforce
  the **G0 direction**: a **positive** BSE/restart result must **not** be added to the main
  text as a benefit; it is supplement-only.
- **Correction trigger:** only if a Phase-12 result shows BSE/restart is **harmful** to the
  shipped configuration — then add a limitations note; otherwise no change.

### T-5 · MT-09 / C2 — eigenframe polish contribution
- **Claim (shipped):** the polish is *proposed and specified*, RNG-free, budget-charged;
  `AB-03` blocks "the polish improves results."
- **Phase-12 test:** `AB-03` `final_polish_enabled` toggle (full-vs-cell Wilcoxon/Holm).
- **Contradiction condition:** the polish toggle shows **no measurable effect at any tier**.
- **Correction trigger:** a null does **not** falsify any efficacy claim (none is made), but
  it bears on *presentation*: flag for a Phase-12 editorial decision whether `C2` remains a
  **headline** contribution or is demoted to a specified-but-unvalidated mechanism. A
  positive effect is supplement-only (G0) and does not upgrade `C2` in this paper.

### T-6 · RS-01 / HL-01 / CN-01 — CEC2017 "#1 overall" selection exposure (R6-T03)
- **Claim (shipped):** overall CEC2017 Friedman mean rank 2.48 of 7 (descriptive
  across-dimension mean; single frozen pub profile; panel-scoped). The shipped paper makes
  **no** "development suite" claim.
- **Phase-12 deliverable:** the tuning-protocol disclosure (6-config selection exposure) that
  R6-T03 defers.
- **Contradiction condition:** Phase-12 discloses that CEC2017 was the development suite and
  the headline rests on a 6-configuration selection.
- **Correction trigger:** attach a **selection-exposure caveat/pointer** beside the CEC2017
  headline (`RS-01`, `HL-01`, `CN-01`) and beside the uncontaminated suites (CEC2011 2nd with
  a Holm loss; CEC2013 3rd at D30). This is a *disclosure* addition, not a number change.

### T-7 · IN-02 / RS-04 / RS-05 — "#1 at D50/D100" vs eGSK head-to-head
- **Claim (shipped):** D50/D100 first places are earned against the whole panel, **not** by
  dominating eGSK (negative_findings §3; per-function W/T/L vs eGSK 13-0-16 at D50, 12-0-17
  at D100; Holm ties). No head-to-head superiority over eGSK is claimed.
- **Phase-12 test:** any ablation that re-partitions D50/D100 wins by component.
- **Contradiction condition:** a component ablation is (mis)read to imply DT-GSK beats eGSK
  head-to-head at D50/D100.
- **Correction trigger:** none to the frozen text (it already blocks this); enforce **G0** —
  the ablation cannot be cited to assert eGSK dominance. Keep the `IN-02` blocked-wording
  guard active in Phase-12 review.

### T-8 · LM-03 / R1-5 — external, non-GSK baseline (evidence deferred)
- **Claim (shipped):** all comparisons are *within the 7-algorithm GSK family*; no
  state-of-the-art claim (`LM-03`, `BG-05`); Limitation Seventh states the absence of an
  external L-SHADE/CMA-ES/structure-learning anchor as a scientific threat.
- **Phase-12 deliverable:** optional external anchor under the locked protocol.
- **Contradiction condition:** an external baseline, if added, materially beats DT-GSK.
- **Correction trigger:** none to existing claims (all are panel-scoped and already
  bounded). A new external result is **additive context** in Phase-12; it can only tighten,
  not falsify, the frozen within-family standings.

---

## Summary of at-risk claims

| Ablation deliverable | Primary claim(s) at risk | Correction sign |
|---|---|---|
| `AB-02` SGSM-overlay | `IN-02`, `LM-02`, `MT-05`/`C1` | narrow on **null/negative** |
| `AB-01` scaffold (D10/D30) | `LM-02` | refine on **component-caused** low-D deficit |
| `AB-01` scaffold **D100** cell | `MT-03` / §3.3.3 floor rationale | drop rationale on **D100 NLPSR≤LPSR** |
| `AB-01` BSE / restart | `MT-06`, `MT-07` | note only on **harmful**; positive is supplement-only |
| `AB-03` polish toggle | `MT-09` / `C2` presentation | editorial demotion on **no-effect** |
| Phase-12 tuning disclosure | `RS-01`, `HL-01`, `CN-01` | add selection-exposure caveat |
| external anchor (opt.) | `LM-03` (bounded) | additive; no falsification |

**Invariant.** Every row above is a *one-directional* safety net: **unfavorable → narrow the
identified claim; favorable → supplement-only, never back-ported (G0).** Because the shipped
main text contains zero component-causality or component-efficacy statements (verified: 0
blocked-pattern hits; `IN-02` reads "consistent with … per-component attribution deferred";
NLPSR "not claimed as new"; BSE/restart/polish carry no efficacy claim), no Phase-12 result
can *retroactively justify* an existing claim — it can only leave the claim intact
(supplement adds new causal analysis) or force a narrowing.
