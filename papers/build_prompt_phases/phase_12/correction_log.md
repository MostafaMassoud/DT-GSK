# Phase 12 - Correction-Exception Check Log (X-ABL-01 scaffold ablation)

**Verdict: NO CORRECTION REQUIRED.** The scaffold remove-one ablation contradicts no shipped
main-text claim; the G0 one-directional guard is **not** triggered; no claim is upgraded; the
frozen primary manuscript stays **byte-identical**.

- **Date:** 2026-07-11
- **Study checked:** X-ABL-01 scaffold remove-one (7 cells: `baseline`, `no_ace`, `no_psr`,
  `no_bse`, `no_linkage`, `no_localsearch`, `no_arch`), CEC2017, D10/30/50/100, 25 runs, 29
  functions, **SGSM off in every cell**.
- **Immutable source:** `benchmarks/cec_reference_results/_ablation/abl-rel-2026-07-11`
  (rank-summary CSVs reproduce byte-for-byte from this release; verified).
- **Governing authorities:** `phase_11/correction_exception_protocol.md` (G0),
  `phase_10/ablation_correction_triggers.md` (trigger table T-1..T-8),
  `phase_05/ablation_preregistration.md` (design + interpretation boundary).
- **Deferred this phase (not evaluable now):** X-ABL-02 SGSM overlay (`AB-02`) and the polish
  toggle `AB-03` (`no_finalpolish`) — campaign execution-in-progress; to be checked in the
  supplement revision that reports them, under the same register.

## G0 invariant (restated)

A Phase-12 ablation result may only (1) ship as new supplement findings, or (2) force a
**text-only narrowing** of a pre-registered claim **iff the result is unfavorable** (contradicts
current wording). **Favorable -> supplement-only, never back-ported; never upgrades a claim.**
The shipped main text contains **zero** component-causality/efficacy statements, so no result can
retroactively justify an existing claim.

## Per-trigger evaluation (only triggers reachable by X-ABL-01)

| Trigger | Claim at risk | Contradiction condition (unfavorable) | Observed in X-ABL-01 | Fires? |
|---|---|---|---|---|
| **T-2** | LM-02 low-D gating | a scaffold component is shown to **materially cause** the low-D weakness | Every Holm-significant low-D effect is a component **helping**: `no_ace@D10` rank change **+2.53** (removing ACE *degrades*). No component causes the low-D deficit. | **No** |
| **T-3** | MT-03 / §3.3.3 NLPSR D100 floor | at **D100**, NLPSR is **dominated by** plain LPSR (removing NLPSR helps) | `no_psr@D100` rank change **+1.29** (removing NLPSR *degrades*; Holm p = 0.44, ns). NLPSR is not dominated by its removal. Floor rationale stands. | **No** |
| **T-4** | MT-06 / MT-07 BSE & restart | BSE/restart shown **harmful** to the shipped config | `no_bse` rank change **positive at all four D** (+0.59..+0.88); BSE is weakly beneficial, never harmful. (Deep-stall restart untested here; no claim.) | **No** |
| **T-5** | MT-09 / C2 eigenframe polish | polish toggle shows **no measurable effect at any tier** | The C2 polish is the SGSM-dependent **final polish**, isolated by the deferred `AB-03` toggle — **not** the AB-01 `no_localsearch` (Nelder--Mead endgame) cell. AB-03 is not available this phase, so C2's presentation is untouched. The AB-01 `no_localsearch` favorable result (Holm-sig at D30/D50) is supplement-only and does not upgrade C2. | **No** (AB-03 deferred) |

**Triggers not reachable by X-ABL-01 this phase:** T-1 (IN-02, needs `AB-02` SGSM overlay), T-6
(RS-01/HL-01/CN-01 selection-exposure — a tuning-disclosure deliverable, not an ablation result),
T-7 (eGSK head-to-head — enforce G0, no text change; the ablation cannot be cited for eGSK
dominance), T-8 (external anchor — n/a). None is affected by the scaffold study.

## Direction check (G0)

All four Holm-significant scaffold contrasts are **favorable** (removing a component degrades
performance): `no_ace@D10`, `no_psr@D30`, `no_localsearch@D30`, `no_localsearch@D50`. Under G0,
favorable component results are **supplement-only** and may never upgrade, strengthen, or convert
a frozen claim. No unfavorable, statistically-supported, identifiable contradiction of any
pre-registered target is observed. Therefore **no text-only narrowing is authorized or applied**,
and (a fortiori) **no upgrade** is performed.

## Cross-reference reconciliation (not a correction)

Two shipped main-text sentences forward-reference the component study:

- `sections/proposed_algorithm.tex` (~L186-190): "...reserved for a component-level study in a
  **follow-up supplement after the final freeze** (no such component study is included in the
  present Supplementary Materials)...".
- `sections/conclusions.tex` (~L116-119): "...reserved for a **follow-up supplement after the
  final algorithm freeze**; no such component study appears in the present Supplementary
  Materials.".

These are **not** empirical claims subject to a G0 result-contradiction trigger; they are
structural forward references. They are **not contradicted** by adding S6, because they scope the
component study to a *follow-up supplement after the final freeze* and describe the *present*
(pre-ablation, frozen) Supplementary Materials — the artifact pinned by
`pre_ablation_supplement_freeze_manifest.json`. Phase-12 integration of S6 transitions
`supplementary.tex` into exactly that anticipated **follow-up / revised** supplement, which is the
authorized destination for ablation content per `correction_exception_protocol.md` Section 2
(reserved S6 slot). S6's opening sentence states this bridge explicitly, so the revised supplement
is self-consistent with the frozen main text. **No main-text edit is required or made.**

## Enforcement-hook outcomes

- Shipped main `DT-GSK.pdf` / `DT-GSK.docx` re-scanned for ablation tokens (`ablat`,
  `phase_12_placeholder`, `do not release`): **0 hits** in both (baseline and post-S6; the main is
  untouched, so its hashes are unchanged from `main_manuscript_freeze_manifest.json`).
- Ablation prose lives in the **supplement build only** (new Section S6 of `supplementary.tex`);
  the primary release and its analysis bundle are unmodified.
- IN-02 blocked-wording: no component-causality/efficacy wording introduced anywhere in the main
  text (main text not edited).

## Classification

**Confirmatory** (Phase-5 exit rule): the outcome matches the pre-registered expectation that a
favorable scaffold ablation is supplement-only and non-correcting. No exploratory deviation; no
change-request entry required against the frozen main manuscript (it is untouched).

---

# Addendum — X-ABL-02 SGSM overlay (`AB-02`) + polish (`AB-03`) determination

**Verdict: ONE text-only narrowing APPLIED to the main manuscript (T-1 / IN-02). C2 left intact.**

- **Date:** 2026-07-12
- **Study checked:** X-ABL-02 SGSM overlay (4 cells: `full`, `no_sgsm`, `no_adaptive`,
  `no_finalpolish`), CEC2013 **D50**, 25 runs, 28 functions, fair-paired (seed schedule
  byte-identical across cells).
- **Immutable source:** `benchmarks/cec_reference_results/_ablation/overlay/`
  (analysis under `overlay/analysis/`; rank matrix, contrasts JSON, per-function means; every
  Wilcoxon p reproduced exactly under `scipy.stats.wilcoxon`).
- **Supersedes:** the "Deferred this phase (`AB-02`, `AB-03`)" note in the header — those toggles
  are now evaluated here under the same register.

## Result (honest, one-directional)

| Contrast (isolates) | W/T/L | Holm p | sig. | direction |
|---|---|---|---|---|
| `full` vs `no_sgsm` — **direct SGSM** | 10/3/15 | **0.2345** | **no** | point estimate mildly favours SGSM-**off** (`no_sgsm` holds best mean rank 1.95 < full 2.18; mean A12 0.429) |
| `full` vs `no_adaptive` — adaptive gate | 15/5/8 | 0.2345 | no | directional only |
| `full` vs `no_finalpolish` — **final polish** | 20/4/4 | **0.00213** | **yes** | polish **significantly helps** (Δrank +1.07, A12 0.64 medium) |

The SGSM null replicates the quarantined 4-cell pilot (pilot p≈0.056, same "more losses than
wins for SGSM-on" direction).

## Per-trigger evaluation (triggers reachable by X-ABL-02 / AB-03)

| Trigger | Claim at risk | Contradiction condition (unfavorable) | Observed | Fires? |
|---|---|---|---|---|
| **T-1** | IN-02 / LM-02 / MT-05·C1 "ISM intended role at D≥50" | direct SGSM isolation shows **no significant D≥50 benefit** *or* net-negative | Holm p=0.235 (null), point estimate net-negative (`no_sgsm` best rank). **Condition met.** | **YES → narrow IN-02** |
| **T-5** | MT-09 / C2 eigenframe polish | polish shows **no measurable effect at any tier** | polish is **significant** at D50 (Holm p=0.00213). Condition **not** met. | **No** (C2 intact) |

## Correction applied (T-1) — text-only narrowing, G0-compliant

**Locus:** `sections/performance.tex` (the single frozen sentence instantiating IN-02, exhibits
F02 D50/D100 / T05 D50/D100 / Table 7). **Before → after:**

- **Removed** the efficacy-implying clause *"is consistent with the intended role of the
  interaction-structure memory, which is active at D≥50 under the `pub` profile"*.
- **Restated** the high-dimension behavior as *arising under the `pub` profile in which the ISM
  and several subsystems co-activate at D≥50* — associating it with the **bundled tier
  configuration rather than any isolated component** (unchanged hedge, retained).
- **Added** the mandated disclosure sentence: *"A direct isolation of the interaction-structure
  memory at its active tier, reported in the Supplementary Material, did not confirm a standalone
  benefit, so per-component attribution is deferred."*
- BIND comment updated to `IN-02 NARROWED (X-ABL-02 T-1: …)`.

**G0 compliance:** narrow-only (the claim is weakened, never upgraded); **no numeric ablation
result** is placed in the main text (the added sentence is a qualitative null-disclosure with a
pointer to the Supplement, so the "main text carries no ablation results" invariant holds); the
favorable polish result (AB-03) is **not** back-ported and does **not** upgrade C1/IN-02/C2.

## Claims NOT changed (verified null-safe)

- **C1** (`introduction.tex` §C1; `proposed_algorithm.tex` §5.x): describes the ISM **mechanism**
  ("records a decaying interaction graph … supplies linkage blocks … active from D≥50") at the
  frozen "proposed-and-fully-specified" hedge level. A null on *benefit* does not contradict a
  *mechanism specification*. **No change.**
- **LM-02** (`performance.tex` low-D sentence; `conclusions.tex` Limitation 2): frames D≤30 as
  running "essentially the adaptive scaffold" — gating as a **design fact** + mechanism failure
  modes, no high-D efficacy assertion. **No change.**
- **C2 / MT-09** (eigenframe polish): T-5 not triggered (polish significant); C2 stays as shipped,
  its positive isolation confined to the Supplement (G0). **No change.**
- Triggers **T-2/T-3/T-4** (scaffold) resolved in the main log above; **T-6/T-7/T-8** unaffected by
  the overlay.

## Downstream actions

- Main manuscript **re-frozen after rebuild**: `main_manuscript_freeze_manifest.json` hashes for
  `sections/performance.tex` (and rebuilt `main.pdf` / `main.docx`) are updated to the post-T-1
  state; all other sections stay byte-identical.
- Ablation-token scan re-run on the rebuilt main (expect 0 hits: the added sentence contains no
  ablation numbers, only a qualitative pointer).

## Classification

**Corrective (unfavorable-triggered narrowing).** Unlike the scaffold study, X-ABL-02 produces one
identifiable, pre-registered, unfavorable contradiction (T-1), so the G0 safety net fires in its
narrowing direction exactly once. This is the sole main-text change authorized in Phase 12; it
weakens no evidence and strengthens no claim.

---

# R2 review + author directive (2026-07-12)

Second independent review (three adversarial panels) + author directive to de-name the single
frozen `pub` profile. Full itemized record with per-file hash deltas is in
`main_manuscript_freeze_manifest.json → r2_review_refreeze`; the review findings + dispositions are
in `independent_review_report.md → REVIEW R2`. Summary of changes:

- **Author directive — remove `pub` profile name.** The rendered manuscript no longer names a `pub`
  profile; the single frozen configuration is referred to generically ("the frozen configuration").
  Editorial only; **no scientific content changed**. (main.tex, performance.tex,
  proposed_algorithm.tex, parameter_table.tex, algorithm_pseudocode.tex, notation_table.tex,
  supplementary.tex.)
- **T1 (MAJOR, exhibits).** Internal registry E-IDs `(En)` in Figs 1/2/4/5 replaced with reader-facing
  `Eq.~(\ref{...})` equation numbers; obsolete En legend removed. Presentation only; no values change.
- **R2-1 (MAJOR, consistency).** Supplement APGSK per-run existence claims time-scoped to the analysis
  freeze and the CR-0006 post-freeze recovery disclosed, removing the main-text↔supplement
  contradiction. Tabulated APGSK values are unchanged (recovery verified equivalent).
- **Ticket 1 (MAJOR, integrity).** Removed the git-tracked orphan prohibited component-ablation tables
  T21/T22 and their generator (favorable DT-GSK-vs-variant contrasts; component attribution is
  deferred by policy, so this content must not ship).
- **Ticket 2 (MAJOR, consistency).** S6 (scaffold remove-one study, immutable release
  `abl-rel-2026-07-11`) added to the `\supplementary{}` back-matter and the supplement abstract; the
  "every value from `rel-2026-07-10-...`" scope narrowed to S1–S5.
- **Ticket 3 (MAJOR, integrity).** Four `artifact_binding.csv` FIG rows repointed from superseded
  matplotlib PDFs to their native-table sources; 12 unused figure assets + 4 orphan generators removed.
- **R2-2 (MODERATE, provenance).** `cost_cec2017.csv` apgsk cec2017 D10/30/50 comparability relabeled
  `provenance-qualified (CR-0006 recovery re-run)` to match the runtime caption; D100 (main campaign)
  stays comparable. **No runtime value changed.**
- **T2 (MODERATE, exhibits).** Two-panel flowchart control-flow overlap fixed (wider inter-panel gap).
- **T3 (MINOR, exhibits).** DT-GSK unified to solid black in every rank exhibit.
- **Build-integrity.** `\zebra` macro added to the supplement preamble (the generated tables begin with
  `\zebra`; the supplement PDF was otherwise un-buildable via pdflatex).

## Classification (R2)

**Editorial / consistency / integrity corrections + one author-directed rename.** No primary number,
rank, p-value, effect size, or claim changed. All four deliverables (main + supplement PDF/DOCX)
rebuilt deterministically and reproducible ×2; the main-manuscript manifest re-frozen with 7 tracked
files rehashed.

---

# R3 review + author directives (2026-07-12)

Third independent review (four adversarial panels) plus two author directives (naturalize
AI-looking machine identifiers; remove MDPI line numbers). Full itemized record with per-file
hash deltas is in `main_manuscript_freeze_manifest.json → r3_review_refreeze`; findings and
dispositions are in `independent_review_report.md → REVIEW R3`. Summary:

- **MAJOR — parameter-table↔code drift (verified).** The table printed the inert dataclass
  defaults for the D≥50-active mechanisms; corrected to the operative values: κ_min 0.55→0.35
  (+adaptive), polish-start 0.985→0.96, senior-p split-bottom 0.10 at D≥50 (0.15 is the D=30 p).
  Propagated to the Fig 2 cells, the worked example, and the C1 prose. **No result changed** —
  the *reported numbers were always generated with the correct code values*; only the printed
  specification was wrong.
- **MAJOR — rendered image leak.** `fig_nlpsr_schedule` had `(NLPSR, E5)` and "frozen pub
  profile" baked into the image; generator fixed and figure regenerated.
- **MODERATE — loop order.** Pseudocode, the (1)–(12) prose, and Fig 4 reconciled to the frozen
  code order (…accept → SGSM-update → BSE → subspace → controllers → polish → global-best →
  deep-stall); false "identical in prose and pseudocode" claim replaced by a step-for-step ref.
- **MODERATE** — equation_registry.csv E10 corrected to `λG+ηΣ`; CD diagrams recoloured DT-GSK
  black; Fig 1 cell overflow reworded; Fig 4 overflow fixed (dedicated page).
- **MINOR** — BSE trigger/D<20 caveat; SGSM cadence corrected; tie-uncorrected-Friedman clause;
  pseudocode leading opened; zebra added to two inline data tables; 15 orphan figures removed.
- **Author directive — machine identifiers.** All reader-facing raw release tags
  (`rel-2026-07-10-262fc16c9` ×76, `abl-rel-2026-07-11`), the mechanical per-caption "Evidence
  release …" stamps, and internal IDs (`CR-0006`, `card-verified`, `rule P5`) replaced with
  natural academic wording; one deliberate provenance reference kept (tag-free) in
  Data-Availability. Review prompt extended with §10.17.4 + pre-flight E9 + pattern 41.
- **Author directive — line numbers.** `\let\linenumbers\relax` added to main.tex.

## Classification (R3)

**Editorial / consistency / spec-fidelity corrections + two author-directed presentation
changes.** No primary number, rank, p-value, effect size, or claim changed. All four
deliverables rebuilt deterministically and reproducible ×2; the manifest re-frozen with 8 tracked
files rehashed.

---

# R4 review + humanization pass (2026-07-12)

Fourth independent review (four adversarial panels, strictly read-only) with a dedicated
whole-manuscript humanization pass under the new §10.17.5. Verdict: no critical/major; headline
inference reproduces exactly; the prose reads as fully human-authored. Full record with hash
deltas is in `main_manuscript_freeze_manifest.json → r4_review_refreeze`; findings and dispositions
in `independent_review_report.md → REVIEW R4`. Summary:

- **Parameter-table tier completeness** (code-verified against `build_pub_config`): the table
  under-stated tier variation — `bse_max_restarts` is 4/2/4/2 (not "2, 4 at D<20"); the DE arm is
  off/on/on/off (not "on at D≥20"); linkage block refresh is 20/20/10/10 (not flat 20); SGSM
  refresh is 5/5/5/20 (table row was flat 5). Corrected in the table + dim-gating cells + prose.
  **Numerically inert** — results used the correct code values; only the printed spec was incomplete.
- **Loop order** (numerically inert): the pseudocode/prose placed the ACE-credit/ARGP step before
  the SGSM update; the code (and Fig 4) do SGSM first. Reordered both; softened the
  "matched step for step" claim to "which Algorithm 1 lists and Figure 4 charts".
- **Humanization (§10.17.5):** consolidated two near-duplicate passages (§3.4 four-axis contrast →
  cross-reference + non-claims; intro↔method "accepted move is evidence" clause reworded);
  humanized the raw `no_*` ablation tokens in the S6 findings prose (kept at their definition).
  A2's do-not-change list (genuine enumerations, load-bearing repetition) respected.
- **Last machine tokens:** removed "(exhibit T-PANEL)" from the panel-roster caption; naturalized
  `BudgetController` → "budget controller"; removed `CR-0006` from `cost_cec2017.csv`.
- **Governance hygiene:** removed the orphan `dt_gsk_flowchart_preview.png`; repointed two stale
  `table_figure_source_map.csv` rows to the current TikZ flowcharts.

## Classification (R4)

**Spec-fidelity + humanization + hygiene corrections.** No primary number, rank, p-value, effect
size, or claim changed. All four deliverables rebuilt deterministically and reproducible ×2; the
manifest re-frozen with 3 tracked files rehashed.

# R5 review + author directives (2026-07-12)

Fifth independent review (R5): four adversarial read-only panels — (A1) method/statistics/evidence,
(A2) whole-manuscript humanization, (A3) exhibits/formatting/presentation, (A4) cross-artifact
consistency/citations/supplement/canonical pre-flight. Verdict: scientifically clean and
camera-ready; the manuscript reads as fully human-authored. A4's E7 "FAIL" was a transient false
positive — it observed this in-progress edit session mid-review and correctly judged the changes
cosmetic; it is closed by this refreeze. Full deltas in
`main_manuscript_freeze_manifest.json → r5_review_refreeze`. Summary:

- **Notation-table residual (MAJOR, R3 miss):** `notation_table.tex` still carried the inert
  dataclass defaults the R3 parameter-drift fix corrected everywhere else — `kappa_min` 0.55 → 0.35
  (now "(adaptive at D≥50)") and polish start 0.985 → 0.96. Verified against `build_pub_config` and
  consistent with `parameter_table.tex`. **Numerically inert** (results used the correct code values).
- **Version-stamp header (author directive):** removed the repeated "Version July 8, 2026 submitted
  to Algorithms" MDPI submit-mode stamp (`main.tex \AtBeginDocument{\lhead{}}` + four suppressions in
  `mdpi.cls`). The `\lhead` approach is submission-safe on its own; the class edit is local/reversible.
- **Pseudocode clarity rewrite (author directive):** Algorithm 1 rewritten in the clean sectioned
  GSK-paper style — Require/Ensure signature, four italic section headers, one operation per numbered
  line (24 steps), equation refs as short right-aligned notes. Rendering-only; semantics unchanged.
- **ISM terminology unification:** dropped the "SGSM" code alias in favour of "ISM" throughout the
  main text, the two frozen phase_03 exhibits, the supplement (case-sensitive sweep preserving the
  `no_sgsm` code-cell name), the DT-GSK flowchart node (recompiled), and the baked-in ablation
  figure title (regenerated; numbers re-verified byte-identical against the abl-rel manifest).
- **Controller-code naturalization:** the opaque D≥100 codes → accurate descriptive terms verified in
  `_dt_core.py` (TERRA → trust-region budget policy; SP-NLPSR → subspace-sampling floor; A1 →
  late-acceptance clip; A2 → frozen-streak broadening; FC4 → late linkage random-mix).
- **Remaining machine tokens / overstatement:** dropped the internal `phase6_run_analysis.py` path
  from the methods prose; "governance record" → "evaluation record"; "update-rule registry" → "set of
  update rules"; removed the cover-letter raw release tag; softened "single source of truth for every
  setting" (controller scalars live in the frozen manifest, not the printed table).

## Classification (R5)

**Exhibit-fidelity + humanization + presentation corrections.** One MAJOR self-consistency fix
(notation `kappa_min`/polish, code-verified, numerically inert); the rest are terminology,
naturalization, and author-requested presentation changes. No primary number, rank, p-value, effect
size, or claim changed. All four deliverables rebuilt deterministically and **bit-identical across
two builds**; post-build scans show **0 reader-facing machine tokens** and **0 undefined citations**;
the manifest re-frozen with 6 tracked files rehashed (12/12 recompute-match).


# R6 review + author directives (2026-07-12)

Sixth independent review (R6): four adversarial read-only panels -- (A) method/statistics/evidence,
(B) whole-manuscript humanization, (C) exhibits/algorithms/pseudocode/flowcharts/typography, (D)
cross-artifact consistency/citations/supplement/pre-flight. All headline inference, loop order,
parameter tiers, and scope framing independently re-verified against the frozen CSVs and the source
code; 0 undefined citations; 0 duplicate bib keys. Full deltas in
`main_manuscript_freeze_manifest.json -> r6_review_refreeze`. Summary:

- **Pseudocode readability (author directive):** Algorithm 1 re-laid-out for an open, page-balanced
  look -- line spacing 1.3 -> 1.8, blank-line separation between the four stages, one compound init
  step split, dedicated-page float placement. It now fills the page from just under the header; still
  one page; semantics unchanged.
- **Copyright/footer removal (author directive):** suppressed the MDPI submit-mode copyright/license
  block and the residual "Submitted to Algorithms" page-1 footer text, keeping the page range. Local,
  reversible; the venue expects the stock class.
- **MAJOR (D1):** the supplement rendered a raw internal label -- "Table tab:wilcoxon-holm" -- as
  visible text; replaced with a descriptive phrase.
- **MODERATE (D2):** environment disclosure said "Windows 10, build 10.0.26200"; build 26200 is
  Windows 11. Corrected.
- **MODERATE (C1):** cross-artifact notation reconciled to the notation-table canonical set -- the
  pseudocode generation counter G -> g (it collided with the interaction matrix G), x_best -> x^gb,
  (k_f,k_r,K) -> (KF,KR,K_exp); the flowcharts and related-work K_F,K_R aligned too. Every Algorithm 1
  symbol is now defined in Table 2.
- **MODERATE (A1):** a footnote now records how the implementation refines Eq.(11) (improvement-
  weighted, per-move l1-normalised outer products; magnitude graph drives linkage/gate, signed graph
  the polish basis), code-verified -- closing a reimplementation gap. No number changed.
- **MODERATE (B1):** the stale cover_letter.pdf (still carrying the release tag) rebuilt from the
  already-fixed source.
- **Minor:** flowchart ARGP step moved to its faithful post-ISM position (C2) and mid-word
  hyphenation suppressed (C3); the C4 RNG-independence claim narrowed (deep-stall shares the escape
  substream, A2); R_max gloss -> "4/2/4/2 by tier" (D3); "profile" jargon -> "configuration" (B4);
  supplement "Phase-2 evidence audit" and the build-phase manifest path naturalized (B3/D4); SLSQP
  added to the abbreviations table (B6).

## Classification (R6)

**Exhibit/notation-fidelity + humanization + presentation corrections.** One MAJOR reader-facing
raw-label leak and one MODERATE factual OS mislabel fixed; the rest are notation-consistency, a
code-verified equation-specification footnote, and author-requested presentation changes. No primary
number, rank, p-value, effect size, or claim changed. All four deliverables + the cover letter
rebuilt deterministically and **bit-identical across two builds**; **0 reader-facing machine tokens**
and **0 undefined citations**; the manifest re-frozen with 9 tracked files rehashed (12/12
recompute-match).

# R7 review (2026-07-12)

Seventh independent review (R7): four adversarial read-only panels (method/statistics/evidence;
whole-manuscript humanization; exhibits/pseudocode/flowcharts/typography; consistency/citations/
supplement/pre-flight). 0 undefined citations; 0 duplicate bib keys; headline numbers agree across
all four deliverables. Panel A surfaced two genuine code<->paper fidelity defects that survived
R1-R6. Full deltas in `main_manuscript_freeze_manifest.json -> r7_review_refreeze`. Summary:

- **MAJOR (A1) linkage tier:** the linkage-aware block crossover was described as gated to D>=30
  (off at D<20) in four places, but the frozen config activates it at D>=10 (`_PUB_D_LT_20`:
  `linkage_min_dim=10`, block size 5, mix 0.70). Verified five ways (profile dicts, escape overrides,
  a built `build_pub_config(10)`, the runtime gate `D>=linkage_min_dim`, and `_make_linkage_groups(10,5)`
  building 2 groups). A reimplementer following the paper would have disabled linkage at D=10 and
  failed to reproduce the D=10 results. Corrected in the architecture table, the dim-gating table
  (off->on, with the per-tier mix 0.70/0.40/0.70/0.70), the gating prose, Algorithm 1, and the
  DT-GSK flowchart. (Panel D's dissenting "D>=30" came from a stale doc string in
  `algorithm_freeze_manifest.json`, not the code.) Numerically inert.
- **MODERATE (A2) round vs ceil:** Eq.(3) and the Table 3 worked example used `round()`, but the code
  uses `ceil()` (`_dt_core.py:2909`); at x=0.50 they diverge (round=0 vs ceil=1), so the "all
  coordinates senior at x=0.50" milestone was false. Changed Eq.(3) to the ceiling, corrected the
  Table 3 D_jun column to 50/18/3/1/1/1/0 and its milestones, and added the ceiling to the notation.
- **MODERATE (C1/D):** the notation table omitted eta (the ISM learning rate used in Eq.(11)); added
  it and softened the caption's universal-completeness claim.
- **MODERATE (B1):** the supplement S6 sentence exposed the raw ablation-cell flags (incl. `no_sgsm`,
  reviving the retired "SGSM" alias); reworded to descriptive prose.
- **MODERATE (B2):** the central gap sentence (repeated near-verbatim 4x) had its method-section
  instance reduced to a back-reference.
- **Minor:** dim-gating senior p=0.15 at 20-49 added (A3); Algorithm 1 trial f(x_i^new)->f(v_i) (C2);
  Fig 1 complexity caption reconciled to O(NP*D)+O(D^2/5) (C3); base-GSK flowchart naming aligned to
  D_jun / dimension-schedule exponent (C4); supplement BASE_SEED -> natural "base seed 20,260,422" (B3).

## Classification (R7)

**Code<->paper fidelity + notation + humanization corrections.** One MAJOR and one MODERATE
code-fidelity defect (both numerically inert -- the results were produced by the frozen code; only
the paper's description was corrected), plus notation-completeness and presentation fixes. No primary
number, rank, p-value, effect size, or claim changed. All four deliverables rebuilt deterministically
and **bit-identical across two builds**; **0 reader-facing machine tokens** and **0 undefined
citations**; the manifest re-frozen with 5 tracked files rehashed (12/12 recompute-match).

# R8 review (2026-07-12)

Eighth independent review (R8): four adversarial read-only panels, with Panel A running a DEEP
code-fidelity mandate (it built `build_pub_config(D)` per tier and cross-checked every gate,
parameter, schedule, rounding, and the RNG rail against the code). **Panel A found no new
critical/major/moderate code<->paper defect -- the R1-R7 corrections all hold**, with a comprehensive
verified-correct coverage list. 0 undefined citations; 0 duplicate bib keys; headline numbers agree.
Full deltas in `main_manuscript_freeze_manifest.json -> r8_review_refreeze`. All fixes are
notation/wording/presentation only; no reported number, rank, statistic, or claim changed. Summary:

- **ACE arm index (A1):** the GSK-pure setting was labelled "arm 2" but is 1-based arm 3 (0-based
  index 2; the 0.45 anchor probability sits at position 3). Corrected in the parameter table,
  notation table, and prose.
- **Adaptive gate wording (A2):** "kappa_min=0.35 raised by an adaptive variant" was wrong -- the
  adaptive rule is a windowed median clipped *below* by 0.12 (< 0.35), so it can lower the gate.
  Reworded to "superseded by an adaptive rolling-window median ... floored at 0.12".
- **NLPSR alpha (C1):** a bare, undefined `alpha 1.0` row that collided with the significance level
  alpha=0.05 was relabelled `alpha_psr` with a Notes gloss (reduction-shape exponent; 1.0 = standard
  schedule).
- **Algorithm 1 loop (C2):** "for g=1 to GEN" used an undefined bound and implied a fixed generation
  count; reframed to the budget-based "while t < MaxFES" (matching the flowcharts); the now-unused
  symbol g removed from the notation table.
- **Supplement DOCX cross-refs (D1):** the supplement DOCX shipped 87 unresolved "??" caption/ref
  fields because `supplementary.aux` was empty at DOCX-build time; building the supplement PDF (which
  populates the aux) before the DOCX resolves all fields (0 "??"). These rendered literally in
  non-Word viewers.
- **Copyedit:** tier-qualified the "~70%" linkage mix (A3); bare "$D50$" -> "$D=50$" (B1); unified
  "7-algorithm"->"seven-algorithm" and "second of 7"->"second of seven" (B2); "Seven limitations"
  (with an unnumbered eighth) -> "Several limitations" (B3); S5 directory path -> bare filename (B6);
  Figure 2 caption "eight scaffold subsystems" -> "eight subsystems" (C3); refreshed the two stale
  D>=30 linkage notes in the canonical `.md`/`.json` source docs to D>=10 (D2); supplement comment
  S1..S5 -> S1..S6 (D3).

## Classification (R8)

**Notation/wording/presentation corrections; zero code-fidelity defects.** Panel A's systematic
config audit confirms the manuscript is faithful to the frozen code after R7. No primary number,
rank, p-value, effect size, or claim changed. All four deliverables rebuilt deterministically and
**bit-identical across two builds**; the supplement DOCX cross-references now resolve (0 "??"); **0
reader-facing machine tokens**; the manifest re-frozen with 7 tracked files rehashed (12/12
recompute-match).


# Round 9 (R9) -- claim calibration, readability, DOCX fidelity, citation accuracy

Ninth independent review: four adversarial read-only panels aimed at angles prior
rounds under-covered -- **(A)** claim calibration / statistical methodology / discussion
soundness (every headline number re-derived), **(B)** abstract flow / sentence-level
readability / cover letter, **(C)** Word (DOCX)-vs-PDF rendering fidelity + a fresh
supplement visual pass, **(D)** citation semantic correctness / bibliographic accuracy /
scholarly completeness. Panel A confirmed the statistics, disclosures, and eGSK-port
framing **sound**; two MAJORs were new to this round.

- **COI authorship (D1, MAJOR):** the Conflict-of-Interest statement wrongly listed the
  second author (A.W.M.) as a co-author of **FDB-AGSK**. FDB-AGSK is by Bakir, Duman,
  Guvenc & Kahraman (verified in `references.bib`, consistent with the related-work
  framing) -- not A.W.M. Removed FDB-AGSK from the co-authorship clause and noted it is an
  independent third-party variant. A.W.M. IS confirmed a co-author of
  AGSK/APGSK/eGSK/ATMALS-GSK (retained).
- **DOCX numeric tables (C1, MAJOR):** the DOCX numeric results tables (main Tables 7/8/9;
  supplement A1-A12) were raw-DataFrame dumps -- underscored headers (`Best_GSK`,
  `D10_MeanRank`), 6-7 sig figs, no mean$\pm$SD -- diverging from the PDF, because
  `build_docx.py` rendered `tables/word_sources/*.json` verbatim (only `T16_bca` parsed its
  `.tex`). Added a generic `parse_frozen_table_tex()` and routed the numeric tables (T1-T16)
  through the frozen `tables/T*.tex` display: grouped headers flattened to combined labels
  (Best GSK / Best DT-GSK), 2-3 sig figs, mean$\pm$SD cells, `\bestval`->bold. Post-build:
  0 garbled underscored headers, 817 mean$\pm$SD cells in the supplement DOCX, 0 unresolved
  "??". Also cleaned raw LaTeX out of the table accessibility alt-text (C2).
- **Self-init scope (A1, MODERATE):** the self-initialization fairness disclosure
  (conclusions) said "the low-dimension cells do not begin from byte-identical populations",
  but the code (`dt_gsk.py` draws its own initial population) and the protocol make it a
  **blanket all-dimension** exception. Corrected to "no DT-GSK cell begins from the shared
  initial population -- the self-init applies at every dimension -- ... most consequential at
  low dimension". This also stops under-disclosing the D50/D100 headline cells.
- **Abstract attribution (A2/B2, MODERATE):** the abstract parenthetical could misattach the
  Holm-significant loss to the D=30 result (a tie, $p_{Holm}=0.199$). Reworded to
  "... and on CEC2011 -- the latter a Holm-significant pairwise loss --" so the significant
  loss binds only to CEC2011.
- **Garden-path "once" (B1, MEDIUM):** "a block is used only once $\mathrm{conf}(G)\ge\kappa_{\min}$"
  -> "used only **when**", matching the companion figure caption.
- **Nemenyi even-handedness (A3, MINOR):** the Nemenyi non-separability caveat was applied to
  the CEC2017 lead but not the CEC2011 loss; added that the ISM-eGSK CEC2011 Friedman-rank gap
  (0.84) is within the Nemenyi CD (1.92) here as well.
- **APGSK framing (A4, MINOR):** clarified that the primary across-function per-function-mean
  test is identical for every comparator (not a weaker basis for APGSK); only APGSK's run-level
  companion analyses are unavailable at D<=50.
- **Midpoint-repair citation (D2, MINOR):** the parent-bound midpoint repair was attributed to
  L-SHADE; corrected to its origin in **JADE** (`zhang2009jade`) carried through the L-SHADE
  lineage (`tanabe2014improving`).
- **Iman-Davenport citation (D3, MINOR):** added a citation for the Iman--Davenport correction
  (`demsar2006statistical`, who recommends it).
- **Copyedit (B3/B4, LOW):** three British-spelling stragglers -> American
  (normalised/optimisation/amortised, one clashing within a single figure); unified
  "GSK family panel" -> "GSK-family panel" (attributive).

## Classification (R9)

**Wording / disclosure / citation / presentation corrections; zero code-fidelity number
changes.** Panel A re-derived every headline number and confirmed the statistics and
disclosures sound. No reported number, rank, p-value, effect size, or claim changed. All four
deliverables rebuilt deterministically and **bit-identical across two builds**; the DOCX
numeric tables now render the frozen formatted display (mean$\pm$SD, bold best), the supplement
DOCX cross-refs resolve (0 "??"); **0 reader-facing machine tokens**; the manifest re-frozen
(`r9_review_refreeze`) with 7 tracked files rehashed (**12/12 recompute-match**).


# Round 10 (R10) -- math/stats audit, author-metadata consequences, presentation

Tenth independent review: four adversarial read-only panels -- **(A)** deep
mathematical/algorithmic correctness vs the frozen code, **(B)** empirical/statistical
integrity + reproducibility-claim verification, **(C)** presentation / figures / tables /
pseudocode visual communication + humanization, **(D)** global consistency / citations /
author metadata / cross-format. Panels A and B re-derived the math and every headline
number and found **no critical or major defect** in the science; the two MAJORs this round
are author-metadata consequences of the newly added third author.

- **Stale author ordinal (D-F1, MAJOR):** the conclusions said the panel's "six comparators
  were authored or co-authored by *the second author*". Adding the third author (2026-07-12)
  made A.W.M. the **third** author, so "the second author" now mispointed to H.S.M.R.; and
  "six" contradicted the corrected COI (FDB-AGSK is an independent third-party variant).
  Fixed to "five of its six comparators were authored or co-authored by two of the present
  authors".
- **COI completeness (D-F2, MAJOR):** the Conflict-of-Interest statement did not disclose
  that the new second author (H.S.M.R.) is a **co-author of eGSK** -- the single most
  consequential comparator (out-ranks DT-GSK at $D=30$; holds the one Holm-significant
  CEC2011 loss). Verified in `references.bib` (`jawad2024egsk`: Jawad, Roshdy, Mohamed).
  Added "Author H.S.M.R. is a co-author of the eGSK variant used as a comparator" to the COI
  and mirrored it in both cover letters. A citable co-authorship, not a fabricated relationship.
- **Wilcoxon table legend (C-M1, MODERATE):** Table 8 (T15) never defined the $+$/$\approx$/$-$
  markers and rendered ties two ways ($\approx$ in the count headers, $=$ in the Dec. column).
  Added a caption legend and unified the Dec. tie glyph to $\approx$ (7 cells).
- **Pseudocode polish symbol (A-M1, MINOR):** Algorithm 1 said "polish $x^{gb}$", but the code
  polishes the **working** incumbent (`pop[best_idx]`) and only then updates the preserved
  global best. Changed to "polish the working incumbent $x^{*}$".
- **Complexity precision (A-M2, MINOR):** the SGSM per-generation cost was stated as
  $O(D^2/5)$, but the graph decay+update runs **every** generation at $D=50$--$99$
  (`interaction_update_period=1`; 10 at $D\ge100$). Corrected to $O(D^2)$ per generation,
  reserving the multi-generation cadence for block re-extraction. Headline unchanged.
- **MaxFES framing (A-N3, MINOR):** MaxFES was written as an equality "$10^4 D$", contradicting
  the paper's own CEC2011 protocol (fixed 150,000). Reframed as an input budget
  ($10^4 D$ for CEC2017/CEC2013; 150,000 on CEC2011) in the notation table, Algorithm 1, and prose.
- **Cauchy-fraction symbol (A-N4, MINOR):** Eq. (E9) used $r_{\text{rst}}$ (the archive-reseed
  fraction, 0.30 at low $D$) for the Cauchy-perturbation row count, but the code perturbs
  `round(bse_cauchy_frac*NP)` with `bse_cauchy_frac`=0.10 at every tier. Introduced $r_c=0.10$
  for the Cauchy fraction; $r_{\text{rst}}$ retained for the reseed.
- **RNG child-seed (A-N5, MINOR):** Eq. (E12) labeled the child-seed derivation "threefry\_child",
  but child seeds are a modular counter offset then feed an independent Threefry stream. Rewrote
  E12 to show the modular map ($\text{stream}_0$ = seed verbatim) and added $M$ to the notation.
- **runbook case (B-F1, MINOR):** the Data-Availability reference used "RUNBOOK.md" (404 on
  case-sensitive hosting); the tracked file is lowercase "runbook.md". Fixed.
- **CEC2013 p-bound (B-F2, MINOR):** the omnibus caption stated "$p\le2.2\times10^{-3}$", but
  the true D=30 maximum is 2.242258e-3 $>$ 2.2e-3. Corrected to the valid ceiling "$p\le2.3\times10^{-3}$".
- **Copyedit / humanization (C-N1/N2/N3/N6/N7, MINOR/LOW):** reduced the abstract's uniform
  em-dash cadence (preserving the R9 Holm-loss attribution); broke the four-fold "is met by"
  anaphora in the intro; varied the third repetition of the thesis phrase; "Initialisation/
  Initialise" -> American in Algorithm 1; "gaining--sharing" (en-dash) -> "gaining-sharing" (4x).

## Classification (R10)

**Wording / disclosure / notation / citation / presentation corrections; zero science-number
changes.** Panels A and B independently re-derived the math and every headline number and
confirmed them sound. No reported number, rank, p-value, effect size, or claim changed. All
five deliverables rebuilt deterministically and **bit-identical across two builds**; the DOCX
stays self-contained (`updateFields=false`) with the three-author byline + eGSK COI; the
manifest re-frozen (`r10_review_refreeze`) with 8 tracked files rehashed (**12/12 recompute-match**).


# External review disposition (ChatGPT "Comprehensive Top-Q1" register, 2026-07-12)

An external adversarial review (155 tickets) was supplied. It was conducted WITHOUT
the source code, evidence release, manifests, or editable manuscript (its own stated
limitation), so the bulk of its tickets are either (a) "could not verify" -- blocked
gates already satisfied by the released repository it never saw -- or (b) demands for
NEW experiments/reanalysis that the paper already scopes as future work and that were
NOT fabricated (direct ISM isolation, extra non-family baselines, statistical
redesign, shared-X0 rerun, CEC2011 constraint data). Those are recorded for the
authors, not actioned here.

It did, however, surface genuine cross-document inconsistencies that the internal
code-having panels had missed (they trusted the code and did not adversarially
cross-check the prose provenance). Confirmed against ground truth and fixed in the
supplement:
- **Q1-047 (eGSK panel provenance):** the supplement said the eGSK panel data was
  "committed reference results whose final polish is fmincon-based", contradicting the
  main text and the ground truth (`comparability_audit.md`: all 21 panel cells LOCALLY
  PRODUCED; `data_ledger.csv`: eGSK CEC2017 = python-backend, commit c35c26de742d;
  eGSK F5 D10 mean 4.8160948761 = the SLSQP port, not fmincon 4.9943). Corrected the
  supplement to state the panel cells are produced in-repository by the runnable eGSK
  port whose polish substitutes SciPy-SLSQP for fmincon -- matching the main paper.
- **Q1-048 (eGSK runtime wording):** the supplement's "no runtime claim involving eGSK"
  over-stated the main (which reports a provenance-qualified eGSK wall-clock row but
  makes no runtime-superiority claim). Aligned the supplement to "no runtime-superiority
  claim involving eGSK".
- **Q1-096 (seed-audit count basis):** the "70,813 schedule rows" figure is short of the
  full-protocol 75,250 by exactly APGSK's three recovered CEC2017 dimensions (29x3x51 =
  4,437); this is the disclosed anomaly A1 (APGSK CEC2017 single-file sidecars overwritten
  by a later run; D10/D30/D50 seeds recovered and verified from generation logs). Added
  that clarification to the supplement seed-audit sentence.
- **Q1-097 (seed-value uniqueness):** "zero duplicate seed values" was imprecise -- the
  schedule is intentionally optimizer-independent (the same key maps to the same seed
  across all seven algorithms), so seeds ARE shared across schedules; uniqueness holds
  WITHIN each schedule. Qualified accordingly.

No primary number, rank, statistic, or claim changed; only the main paper was already
correct on eGSK provenance, so only the supplement was rebuilt (PDF then DOCX,
bit-identical across two builds). Verdict-level tickets (ISM isolation, venue tier,
added baselines, statistical redesign) are author/research decisions and remain open.
