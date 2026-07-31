# Phase 7 — Method artifacts, conceptual figures, Word-native sources (Task C report)

Date: 2026-07-11. Anchor commit `262fc16c9`; evidence release
`rel-2026-07-10-262fc16c9`. Binding inputs: Phase 6 analysis bundle
(`papers/analysis/rel-2026-07-10-262fc16c9/`) and `results/paper_tables/`
(sole admissible `results/` input). No file under `results/_run_all` or
`results/_ablation` was read; no rendered `.tex` was parsed as a data source;
zero hand-typed result values (all table cells transcribed verbatim by
script; all figures are authored conceptual art or analytic E5 plots).

---

## 1. Files produced per category

### C.1 Method `.tex` renderings (canonical phase_03 sources) — 4 files

| File | Rendered from | Label(s) |
|---|---|---|
| `papers/build_prompt_phases/phase_03/notation_table.tex` | `notation_table.md` (canonical) | `tab:notation` |
| `papers/build_prompt_phases/phase_03/algorithm_pseudocode.tex` | `algorithm_pseudocode.md` (frozen loop steps 1–11) | `alg:dt-gsk` |
| `papers/build_prompt_phases/phase_03/parameter_table.tex` | `parameter_table.md` (tier-resolved `pub` freeze) | `tab:parameters` |
| `papers/build_prompt_phases/phase_03/equations.tex` | `equation_registry.csv` rows E1a–E12 | `eq:junior-idx` … `eq:rng-substreams` (one `\begin{equation}\label{eq:...}` block per registry row, registry `label_tex` column) |

MDPI compatibility: article class, standard `amsmath`, `booktabs` tables,
`algorithm` + `algpseudocode` for the pseudocode float. The pseudocode
transcription preserves the frozen ordering, the dimension gating
(D≥50 / D≥100 no-op wording), the charged-evaluation notes, and the
global-best return semantics ("restart never loses ground"; returns
`(x_gb, f_gb)`).

### C.2 Conceptual figures (authored; NO empirical values) — 10 artifact files

All under `papers/figures/concept/` (deterministic filenames; vector PDF
primary + PNG alternate at 220 dpi ≥ 200 dpi):

| Exhibit / label | PDF + PNG | Generator |
|---|---|---|
| F-ARCH `tab:architecture` | `fig_architecture.pdf/.png` | `papers/scripts/generate_flowchart.py` (REWRITTEN, see §3.1) |
| F-SGSM-MECH `tab:sgsm-mechanism` | `fig_sgsm_mechanism.pdf/.png` | `papers/scripts/generate_sgsm_mechanism.py` (NEW — no generator existed) |
| F-GATING `tab:dim-gating` | `fig_dim_gating.pdf/.png` | `papers/scripts/generate_dim_gating.py` (NEW — no generator existed) |
| F-TAXONOMY `tab:taxonomy` | `fig_taxonomy.pdf/.png` | `papers/scripts/generate_taxonomy_figure.py` (REWRITTEN, see §3.2) |
| F-NLPSR `fig:nlpsr-schedule` | `fig_nlpsr_schedule.pdf/.png` | `papers/scripts/generate_nlpsr_trajectory.py` (ADAPTED, see §3.3) |

Spec conformance (checked against `phase_04/conceptual_figure_specs.md` and
the frozen glossary): 8 subsystems with registry anchors; central inherited
[GSK] core; dimension-gate badges (linkage D≥30/50 per tier, SGSM + subspace
LS + polish D≥50, controllers D≥100) transcribed from
`phase_03/parameter_table.md`; global-best/deep-stall loop with the
"restart never loses ground" invariant and "returns global best" arrow;
13-substream RNG rail (E12) + BudgetController rail; the six mandated
data-flow arrows; SGSM graph drawn over 8 abstract coordinate indices
(didactic, no measured structure); gating chart ON/OFF as filled-vs-empty
(grayscale-safe) with frozen tier values in ON cells and both threshold
callouts + freeze footnote; taxonomy limited to the four verified comparison
dimensions vs DG / CMA-ES / eigenvector-crossover, card-bounded, with the
non-claim footnote ("no extra objective evaluations", never "free");
terminology "ISM (code alias SGSM)", "eGSK" not referenced, no ablation or
component-causality wording anywhere.

### C.3 Gated figures — NOT run (dispositions recorded)

- `generate_trace_figures.py` and `generate_adaptive_params_panel.py` were
  **not executed**: no promoted GenLog diagnostic release exists (0
  `GenLog_*` files in the admissible tree). Disposition appended as a dated
  Phase 7 resolution note to **EG-005** in
  `papers/governance/evidence_gap_register.md` (omit branch;
  `fig:trace-sgsm` / `fig:adaptive-params` marked unavailable; legacy orphan
  PDFs in `papers/figures/traces/` remain excluded).
- `generate_parametric_tables.py` was **not executed** for output: no
  admissible sensitivity release (EG-006; T21/T22 not exported by Phase 6).
  Disposition appended as a dated Phase 7 resolution note to **EG-006**
  (omit branch; T21/T22 unavailable, no word source emitted, committed
  `T21.tex`/`T22.tex` stay stale-excluded).

### C.4 Word-native semantic table sources — 17 JSON files + 1 generator

`papers/tables/word_sources/T1.json … T16.json, T16_bca.json`, emitted by
the new deterministic script `papers/scripts/generate_word_sources.py`
(fixed key order `{table_id, manuscript_label, caption_stub, headers,
rows, notes, number_format, source_csv, source_sha256}`, no timestamps,
verbatim cell transcription, HARD FAIL on missing input).

- T1–T16: sourced from `results/paper_tables/T{1..16}.csv` (Phase 6 task 23
  export; provenance chain in `results/paper_tables/provenance.json`).
- **T16_bca**: no staged CSV exists in `results/paper_tables/`. Sourced from
  the bundle's registry-defined T-BCA union companion
  `papers/analysis/rel-2026-07-10-262fc16c9/cec2017/headline_bca.csv`
  (bundle `table_to_csv_map.md`; Phase 6 audit verified it byte-equal to the
  concatenation of `bca_ci_cec2017_D10..D100.csv`) — 696 data rows,
  availability flags preserved (`ok` / `no CI (degenerate cell)` /
  `disclosed-unavailable` for apgsk). The legacy `papers/tables/T16_bca.tex`
  semantics (BCa CIs on Friedman mean ranks) are STALE and its generator is
  inadmissible (§3.4); the JSON `notes` disclose this.

### C.5 Editable diagram sources — 2 files

- `papers/figures/concept/sources/fig_architecture.drawio` — draw.io XML
  matching the rendered architecture figure (same blocks, badges, rails,
  control/data edges, palette).
- `papers/figures/concept/sources/diagram_word_plan.md` — DrawingML build
  plan for Phase 9 (tab:sgsm-mechanism as shape groups; tab:dim-gating and
  tab:taxonomy as native Word tables; fig:nlpsr-schedule embedded as vector
  image with rationale).

### C.6 Tooling hygiene

`ruff check --fix` clean on all six touched scripts (`generate_flowchart.py`,
`generate_sgsm_mechanism.py`, `generate_dim_gating.py`,
`generate_taxonomy_figure.py`, `generate_nlpsr_trajectory.py`,
`generate_word_sources.py`).

---

## 2. Dispositions recorded

| Item | Disposition |
|---|---|
| F-TRACE / F-ADAPT (`fig:trace-sgsm`, `fig:adaptive-params`) | UNAVAILABLE — omit; EG-005 dated note appended (generators diagnostic-release-gated; not run) |
| T21 / T22 (`tab:sensitivity`) | NOT GENERATED — omit; EG-006 dated note appended (no admissible sensitivity release; generator not run for output) |
| T16_bca regeneration via `generate_t16_bca.py` | NOT RUN — inadmissible source path (§3.4); Word source built from the bundle T-BCA companion instead |
| Ablation artifacts | NONE produced (P6 binding; `results/_ablation` never read) |
| Legacy figure outputs (`papers/figures/flowchart/dt_gsk_flowchart.pdf`, `papers/figures/taxonomy/metaheuristic_tree.pdf`, `papers/figures/traces/nlpsr_trajectory.pdf`) | SUPERSEDED by `papers/figures/concept/*`; left in place untouched — Phase 8 must repoint `\includegraphics` (legacy committed `.tex` is stale per Phase 6 finding) |

---

## 3. Spec mismatches found in the pre-existing generators

### 3.1 `generate_flowchart.py` (tab:architecture) — REPLACED (6 defects)

1. Drew a **"Nelder–Mead endgame"** stage — not part of the frozen design
   (the frozen endgame is the eigenframe compass polish, E11, one-shot,
   RNG-free); NM appears in the corpus only as motivation, not mechanism.
2. Terminal box **returned the working incumbent `x*`**, contradicting the
   frozen return-global-best semantics (`(x_gb, f_gb)`).
3. **No deep-stall restart branch and no global-best shadow** (spec (a)
   required element 4 missing entirely).
4. **No D≥100 controllers block**, no RNG-substream rail, no
   BudgetController rail (required elements 2/5 incomplete).
5. SGSM gate annotated `open iff c ≥ max(med30, 0.12)` — this threshold does
   not exist in the frozen parameter table (confidence gate is
   κ_min = 0.55); un-provenanced constant.
6. Selection stated `f(v_i) ≤ f(x_i)` — E8 is strictly greedy (`<`).

### 3.2 `generate_taxonomy_figure.py` (tab:taxonomy) — REPLACED

Drew a generic metaheuristic-inspiration tree (GA/PSO/WOA/QCSCA/NRO/BSO...)
— does not match exhibit F-TAXONOMY, which is the four-dimension
structure-learning positioning (update trigger / evaluation cost / what is
learned / how exploited) sourced from `phase_04/novelty_scope.md`
Sections 1.1–1.3; the tree also named many algorithms with no allowed
citation key (corpus-violation risk).

### 3.3 `generate_nlpsr_trajectory.py` (fig:nlpsr-schedule) — ADAPTED

Plotted formula matched E5 (verified), but only two tiers were shown and
output went to `papers/figures/traces/`. Extended to all four `pub` tiers
(NP0 = 5D; N_min = 12/12/25/25 per the frozen tier floors), moved to
`papers/figures/concept/fig_nlpsr_schedule.pdf/.png`, PNG alternate added.

### 3.4 `generate_t16_bca.py` — NOT RUN (admissibility defect, pre-existing)

Loads data via `gsk_family.analysis.result_loader.load_algorithm`, which
carries a `results/_run_all` fallback (prohibited) and reads the reference
tree without release pinning; the Phase 2 strict-source guard is not applied
in this path (already flagged in
`papers/governance/table_figure_source_map.csv` row T16_bca). Recorded here;
no output of this script was produced or consumed.

### 3.5 Observation (non-blocking, recorded per spec (c) escalation rule)

`phase_03/parameter_table.md` lists a linkage mix-probability value for
D<20 (0.70) although the frozen pseudocode gating note switches blockwise
linkage OFF below the D≥30/50 tiers. The gating chart renders D10 = OFF
(per-coordinate KR mask, E4) per the pseudocode note — the authoritative
gate statement that spec (c) itself cites — while all ON-cell values are
verbatim parameter-table transcriptions. Not treated as a rendering-blocking
discrepancy because the parameter table contains no enable/disable row for
linkage (the D<20 value is a dormant config default), but it is recorded
here for the Gate 7 reviewer.

---

## 4. Determinism / QA notes

- All artifact filenames fixed; no timestamps inside any artifact content.
- PNG alternates rendered at 220 dpi (≥ 200 dpi requirement).
- Word-source JSONs carry `source_sha256` for byte-level re-verification;
  regeneration is idempotent (`python papers/scripts/generate_word_sources.py`).
- Conceptual generators read no file at run time (all content authored in
  the script from the frozen phase_03/phase_04 sources quoted in their
  docstrings) — strict source guard trivially satisfied.
