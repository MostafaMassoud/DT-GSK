# DT-GSK — Conceptual Figure Specifications (Phase 4, task 8)

**Phase 4 deliverable (approval-level specs for authored conceptual art; PAPER_BUILD_PROMPT
Section 8.1).** Date: 2026-07-10. Companions: `phase_04/exhibit_plan.csv` (rows F-ARCH,
F-SGSM-MECH, F-GATING), `phase_03/algorithm_pseudocode.md`, `phase_03/equation_registry.csv`,
`phase_03/parameter_table.md`, `phase_04/contribution_matrix.md` (C1–C4).

**Global constraints (all three figures, binding).**

- **Authored conceptual art only.** These figures encode the *specified design* of DT-GSK.
  They contain **no empirical values whatsoever** — no fitness numbers, ranks, p-values,
  errors, runtimes, or anything derived from `results/` or from the evidence release.
  Frozen *configuration constants* from `phase_03/parameter_table.md` (e.g. λ = 0.95,
  NP_init = 5·D, tier thresholds) MAY appear as design labels; nothing measured may.
- Vector output (PDF primary), embedded fonts, deterministic filenames, publication-size
  labels, grayscale-distinguishable, no decorative 3-D effects (Section 8.4 / CR-0003).
- Terminology per the frozen glossary: "DT-GSK", "SGSM" only as the code alias of the
  interaction-structure memory, "eGSK" lowercase e. Never the word "free" for ISM cost —
  always "no extra objective evaluations".
- No component-causality wording in any figure text or caption; mechanisms are *proposed
  and specified* (ablation is `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`).
- Captions state that the figure is a schematic of the frozen `pub`-profile design
  (hash-frozen in `phase_03/algorithm_freeze_manifest.json`).

---

## (a) DT-GSK architecture / pipeline diagram

- **Exhibit:** `F-ARCH` · label `tab:architecture` · destination main · claims C1–C3.
- **Generator:** `papers/scripts/generate_flowchart.py` (authored spec input only; the
  script must not read any result file).

**Message (one sentence the reader should take away).** DT-GSK is the *unchanged*
gaining-sharing operator core wrapped by eight dimension-gated subsystems — control and
budget scaffolding at every tier, structure memory and deterministic polish at high
dimension — inside an outer loop whose deep-stall restart can never lose the global best.

**Required elements (all mandatory).**

1. **Central inherited core** (visually distinct, e.g. neutral fill, labeled "inherited
   [GSK]"): junior/senior gaining-sharing trial construction (E1–E4), midpoint bound
   repair (E7), strictly-greedy selection (E8), single `BudgetController` charging every
   `f(·)` call.
2. **The 8 subsystems**, each a named block with its equation/registry anchor:
   1. NLPSR population-size schedule (E5, tier-floored);
   2. ACE bandit operator-pool control with ARGP arm pruning (E6);
   3. linkage-aware block crossover mask (E4; SGSM-fed blocks at D ≥ 50);
   4. SGSM interaction-structure memory (E10; accepted-move EMA graph, λ = 0.95);
   5. SGSM top-k-block subspace local search (charged evaluations);
   6. BSE budget-safe escape with elite archive seeding (E9; hard-capped);
   7. D ≥ 100 controllers (TERRA budget policy, basin memory, SP-NLPSR floor,
      A1/A2/FC4) — drawn as one grouped block, annotated "method-level protections";
   8. eigenframe final polish (E11; one-shot, RNG-free, final budget slice).
3. **Dimension gating**: visible gate annotations on the affected blocks —
   linkage blockwise per tier (D ≥ 30/50 per `pub` profile), SGSM + subspace LS +
   polish (D ≥ 50), upper-tier controllers (D ≥ 100); gate thresholds transcribed from
   `phase_03/parameter_table.md`, not invented.
4. **Global-best / deep-stall loop**: the outer iteration loop with the global-best
   shadow `(x_gb, f_gb)` updated every generation, and the deep-stall full restart branch
   (resample population, preserve global best) annotated with the invariant
   "restart never loses ground"; return arrow labeled "returns global best".
5. **Cross-cutting rails** (thin horizontal bands or side rails): the 13-substream
   append-only RNG layer (E12) feeding every stochastic block by named substream, and the
   `BudgetController` accounting rail through which *all* evaluations (including LS and
   polish probes) are charged.
6. **Data-flow arrows**: accepted-move deltas → SGSM; SGSM → linkage blocks → crossover
   mask; SGSM → top-k blocks → subspace LS; SGSM signed matrix → eigenbasis → final
   polish; acceptance signal → ACE credit and ARGP pruning; elite archive → BSE seeding.

**Labels.** Block labels use glossary names + registry anchors ("NLPSR (E5)", "SGSM (E10)");
gates as "D ≥ 50" badges; substream rail labeled "13 RNG substreams (E12)"; caption cites
`phase_03/algorithm_pseudocode.md` step numbers 1–11.

**No-empirical-source statement (must appear in the spec handoff and be honored).** This
figure is authored solely from `phase_03/algorithm_pseudocode.md`,
`phase_03/equation_registry.csv`, and `phase_03/parameter_table.md`. It reads no file
under `results/` or `benchmarks/cec_reference_results/` and displays no empirical value;
it makes no performance or component-contribution statement.

---

## (b) SGSM mechanism illustration (accepted move → graph → linkage/LS exploitation)

- **Exhibit:** `F-SGSM-MECH` · label `tab:sgsm-mechanism` · destination main · claims C1, C2.
- **Generator:** authored vector art (TikZ/SVG) per this spec; no script reads result data.

**Message.** Every *accepted* move the run already made is recycled — at no extra
objective evaluations — into a decaying coordinate-pair interaction graph, and that one
learned graph is exploited through three channels: crossover linkage blocks, a top-k-block
subspace for local search, and the eigenbasis of the final deterministic polish.

**Required elements (all mandatory).**

1. **Stage 1 — accepted moves:** two or three schematic population members with
   accepted-move delta vectors Δx (rejected trials shown crossed out and explicitly *not*
   feeding the graph); annotation "acceptance signal only — zero extra objective
   evaluations (compute cost per `phase_03/complexity_analysis.md`)".
2. **Stage 2 — graph update (E10):** the EMA update G ← (1−λ)·G + λ·outer(Δx_accepted)
   with λ = 0.95 shown as decay of stale edges; signed edge weights (reinforcing vs
   opposing coordinate pairs, two line styles); the confidence/evidence gate κ_min drawn
   as a threshold filter ("act only when confidence ≥ κ_min"); resulting sparse
   coordinate-pair graph over a small illustrative coordinate set (e.g. 8 abstract
   coordinates — abstract indices, not any benchmark function's true structure).
3. **Stage 3 — three exploitation channels**, each an arrow out of the same graph:
   (i) linkage blocks → block crossover mask (E4), replacing the per-coordinate KR mask
   for the linkage share of the population at D ≥ 50;
   (ii) top-k blocks → subspace local search (annotated "charged through
   `BudgetController`");
   (iii) signed matrix → eigenbasis → eigenframe final polish (E11), annotated
   "one-shot, RNG-free, final budget slice; coordinate axes when no graph signal".
4. **Timeline strip** (bottom): run progress 0 → MaxFES with the D ≥ 50 activation gate,
   continuous graph updating, and the polish firing once in the final slice.

**Labels.** Stage headers "learn from accepted moves", "decaying signed pair graph",
"exploit ×3"; equation anchors (E10), (E4), (E11); glossary spelling "interaction-structure
memory (ISM; code alias SGSM)".

**No-empirical-source statement.** Authored solely from `phase_04/contribution_matrix.md`
(C1, C2), `phase_03/equation_registry.csv` (E4, E10, E11), and
`phase_03/complexity_analysis.md` for the cost wording. The illustrated graph is an
abstract didactic example — it does not depict any measured interaction structure, any
benchmark function, or any run from any release; no empirical value appears.

---

## (c) Dimension-tier gating chart

- **Exhibit:** `F-GATING` · label `tab:dim-gating` · destination main · claim C3.
- **Generator:** authored vector art (TikZ/SVG or matplotlib from a hand-authored spec
  table); no script reads result data.

**Message.** DT-GSK is one frozen algorithm with one tier-resolved `pub` configuration:
which subsystems are active is a deterministic function of dimension alone — control and
budget scaffolding everywhere, structure memory and polish from D ≥ 50, protective
controllers only at D ≥ 100 — with no per-suite or per-function tuning.

**Required elements (all mandatory).**

1. **Matrix layout:** rows = subsystems (the same 8 named blocks as figure (a), plus the
   deep-stall restart row and the inherited GSK core row for completeness); columns = the
   four CEC2017 `pub` tiers D10, D30, D50, D100 (caption notes CEC2011 problems resolve
   to the tier of their native dimension).
2. **Cell semantics:** ON / OFF markers that survive grayscale (filled vs empty, not
   color-only); where a subsystem is ON with tier-specific parameter values (e.g. NLPSR
   floor, linkage block size), the cell carries the frozen value.
3. **Binding rule (mandatory):** every cell value is transcribed from
   `phase_03/parameter_table.md` / `_dt_profiles.build_pub_config(dim)` (hash-frozen,
   Gate 3 APPROVED). Gates known from the pseudocode notes — linkage blockwise ON from
   D ≥ 30/50 per tier, SGSM + subspace LS + eigenframe polish at D ≥ 50, high-D
   controllers at D ≥ 100, scaffold + deep-stall per profile at all tiers — must match
   the transcription; any discrepancy blocks rendering and is escalated, never resolved
   by editing the figure.
4. **Threshold callouts:** vertical divider annotations "D ≥ 50: structure memory +
   polish activate" and "D ≥ 100: protective controllers activate".
5. **Footnote row:** "single frozen configuration; no per-suite tuning
   (`algorithm_freeze_manifest.json`)".

**Labels.** Row labels use glossary names + registry anchors; column headers "D10 / D30 /
D50 / D100 (`pub` tiers)"; caption states the chart is the *specified* activation
schedule, not an observed one.

**No-empirical-source statement.** Authored solely from `phase_03/parameter_table.md`,
`_dt_profiles.build_pub_config` as documented in phase_03, and
`phase_03/algorithm_pseudocode.md`. Displays configuration constants only — no empirical
value, no performance implication, no component-contribution statement (all such content
is `DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY`).

---

## Approval checklist (Gate 4 input)

- [ ] Three specs above approved as the complete Section 8.1 conceptual-art scope for the
      main text (`tab:architecture`, `tab:sgsm-mechanism`, `tab:dim-gating`; the
      related-work taxonomy `tab:taxonomy` is planned in `exhibit_plan.csv` and sourced
      from `phase_04/novelty_scope.md`, not from this file).
- [ ] Each rendered figure ships with its authored spec source in the reproducibility
      package (Section 8.4).
- [ ] Phase 7 validation re-checks: no empirical value present; gate thresholds match
      `phase_03/parameter_table.md`; terminology matches the frozen glossary.
