# Stage 17 — LaTeX/PDF build and production report

**Seat:** `s17_journal_production` (JCO / PROD-PDF / PROD-WORD co-leads; teams T7-VENUE, T4-SOFT)
**Review date:** 2026-07-22
**Package under review (verified against the repo, not from memory):**

| Item | Verified value |
|---|---|
| git HEAD | `45248eb31af7b01567c251f2a5da4f36e92d6030` |
| freeze anchor (`main_manuscript_freeze_manifest.json` → `anchor_commit`) | `abd2fa2f25c8426247b43c85bcb3d82041d00976` |
| `check_manifest.py` | `15/15 match []` (exit 0) |
| evidence release | `rel-2026-07-20-67d9345f9` |
| `papers/DT-GSK.pdf` | 39 pp, 695,943 B, sha256 `3436276946abd7dd…` |
| `papers/supplementary.pdf` | 61 pp, 1,155,151 B, sha256 `9d0d3cf9e64b8156…` |
| `papers/cover_letter.pdf` | 2 pp, 113,413 B, sha256 `7313e38fe62a0771…` |
| `papers/governance/submission_package_manifest.json` | page counts 39/61/2 and all five SHA-256 values recomputed **identical** on 2026-07-22 |

All statements below are **CONFIRMED** (independently verified in this review) unless
explicitly marked **SUSPECTED**.

---

## 1. Build integrity — PASS

| Check | Result | Evidence |
|---|---|---|
| Correct class wired | PASS (but see §5) | `papers/main.tex` L9 `\documentclass[algorithms,article,submit,moreauthors,pdftex]{Definitions/mdpi}` |
| Undefined citations | **0** | `papers/main.log`, `papers/supplementary.log` — no `LaTeX Warning: Citation` |
| Undefined references | **0** | same logs — no `LaTeX Warning: Reference` |
| Missing figures/fonts/files | **0** | logs clean; all 11 (main) / 10 (supplement) fonts are embedded subsets (`URWPalladioL-*`, `CMR10`, `CMMI`, `CMSY`) |
| Overfull `\hbox` | main **0**; supplement **1** | see §2 — the single supplement box is a real defect |
| Underfull boxes | main 107, supplement 14 | benign: `mdpi.cls` L209 loads `\RequirePackage[none]{hyphenat}`, so justified text produces loose lines by construction. **Not ticketed.** |
| Deterministic build | PASS | `SOURCE_DATE_EPOCH=1783468800`; freeze manifest records double-build byte-identity for all three PDFs |
| PDF metadata | PASS | `/Title` carries the full title, `/Author` all three authors, `/Keywords` all ten, `/Subject` the full abstract |
| Bookmarks | PASS | 32 (main), 33 (supplement) |
| Figure resolution in PDF | PASS | all body figures are **vector**; the only raster XObjects are 4 page-1 MDPI logos at 613 dpi in each PDF |
| Hidden template instructions/comments in output | PASS | rendered scan finds no `TODO`/`TBD`/`FIXME`/`lorem ipsum`/dummy DOI/all-zero ORCID in any of the three PDFs |

Validators executed read-only, all exit 0:
`check_manifest.py` (15/15), `validate_build_hygiene.py`, `validate_provenance_claims.py`,
`validate_document_consistency.py`, `validate_cross_format_parity.py` (579 rows / 0 FAIL),
`validate_docx.py` on both DOCX (33 PASS / 0 FAIL each).

---

## 2. **S17-02 (Major, P1, CONFIRMED)** — supplement Table A19 runs off the page and loses content

**Location:** `papers/supplementary.pdf` p.48 of 61 (Table A19, "Frozen run parameters of the
shipped configuration (per-subsystem detail)"); source
`papers/build_prompt_phases/phase_03/parameter_table_detail.tex` L9–L68.

**Exact evidence:**

* `papers/supplementary.log` L1647:
  `Overfull \hbox (218.9852pt too wide) in paragraph at lines 19--68`, emitted while
  typesetting `build_prompt_phases/phase_03/parameter_table_detail.tex`, shipped on page `[48]`.
* Measured text bounding box on p.48: right edge **x = 598.8 pt** on a page **595.276 pt** wide —
  the table extends **3.5 pt past the physical paper edge** and **80.1 pt past the right text
  margin** (limit 518.7 pt). Every other page of both PDFs stays inside the paper
  (worst other case: supplement p.10 at 527.3 pt; main worst case 520.7 pt, i.e. 2.0 pt of
  normal microtype protrusion).
* **All seven** non-empty `Notes` cells in the source are lost in the rendered PDF. Probe of the
  rendered page-48 text for each source string returns `False` for every one:
  `cooldown 0.15; stop 0.9`, `interaction_graph_min_dim=50`, `interaction_graph_decay`,
  `interaction_graph_lr`, `window 30, percentile 0.50, floor 0.12`, `final_polish_start_frac`,
  `redundant guard; not an active mechanism`.
  The same seven strings probe `True` in `papers/supplementary.docx`.
* Visual confirmation (rendered at 110 dpi): the third column is sheared off mid-token —
  `interaction_grap`, `final_polish_sta`, `cooldown 0.15; stop`, `redundant guard; r` — and the
  booktabs rules run past the paper edge.

**Root cause:** the table is `\begin{tabular}{lll}` with no width-constrained (`p{}`) column and
no `\resizebox`. The header comment (L3–L5) records that this file was **split out of
`parameter_table.tex` under ticket N-013** precisely because the combined 48-row table had been
scaled to 5.3 pt; the split fixed the font size and introduced this overflow instead.

**Why it matters:** a submitted supplement in which a whole column of the frozen-parameter table
is unreadable is a reproducibility-relevant content loss, not a cosmetic nit — these are exactly
the constants the Data Availability statement promises make the configuration reproducible from
the text. It is also a genuine PDF↔Word content divergence (§4 of
`cross_format_consistency_report.md`).

**Required correction:** convert column 3 to `p{...}` (or the whole table to `tabularx`/`longtable`
with a fixed total width), rebuild, and re-verify that p.48's text bbox is ≤ 518.7 pt and that all
seven `Notes` strings are recoverable from the rendered PDF text.

**Post-revision verification:** `grep -c "Overfull" papers/supplementary.log` → 0; per-page max-x
scan ≤ 518.7 pt for every page; the seven-probe test above returns `True` in the PDF.

---

## 3. **S17-01 (Major, P1, CONFIRMED)** — the profile 10.14 page-limit rule is breached and unrecorded

**Governing rule:** `papers/PAPER_REVIEW_PROMPT.md` §10.14 — the main manuscript must not exceed
the limit in the Phase-4 verified journal record or, where the journal publishes none, the
self-imposed budget; page counts must be measured from the compiled PDF **with a page-count row
recorded in `papers/governance/phase_gate_register.csv`**; overflow may be resolved *only* by
migrating material to the supplement, never by shrinking figures below legibility.

**The binding caps** (`papers/build_prompt_phases/phase_04/page_budget.md` §2, §8, restated as
gate conditions in §8): **B1 ≤ 34** typeset pages (main text including exhibits, excluding
references and back matter) and **B2 ≤ 12,000** prose words (including abstract and captions,
excluding references).

**Measured on the shipped `papers/DT-GSK.pdf` (39 pp):**

| Quantity | Measurement | Cap | Verdict |
|---|---|---|---|
| Total pages | 39 | — | +4 vs the last recorded gate measurement (35) |
| Back matter begins | p.35 (`Supplementary Materials:` after the Conclusions text ends mid-page) | — | — |
| References | pp.37–39 (3 pages) | — | — |
| **B1**, Phase-8 convention (pp. 1–N, N shared with the back-matter start; `phase_08/build_record.md` L157) | **35 pp** | 34 | **FAIL (+1)** |
| **B1**, Phase-11 arithmetic (total − reference pages; `PHASE_11_gate_report.md` L11: 35 − 3 = 32) | **36 pp** | 34 | **FAIL (+2)** |
| **B2** = body prose 12,007 + abstract 197 + captions ≈ 1,164 | **≈ 13,368 words** | 12,000 | **FAIL (+≈1,370, ≈11 %)** |

Method for B2: LaTeX-stripped word count over `papers/sections/*.tex` with float, equation,
`\label`/`\ref`/`\cite` payloads removed and non-alphabetic tokens discarded (12,007); abstract
counted from the rendered PDF (197); caption words counted from rendered ~9.0 pt spans on
pp. 1–34 (1,164). Back matter and references are excluded, as the budget specifies. The
measurement is an estimate at the ±5 % level; the breach exceeds that margin.

**Recording failure.** `papers/governance/phase_gate_register.csv` contains page-count rows only
for Phase 8 (`main.pdf 34 pages (B1=31)`) and Phase 11 (`main DT-GSK.pdf 35 pages total /
B1=32 … ≤34 hard cap PASS, ~2pp headroom`). **No row records the current 39-page build.** The
§6 overflow valve (a fixed six-step supplement-migration order) was never invoked. This is a
straightforward §10.14 non-compliance independent of the numbers.

**Aggravating interaction with §10.14's second clause.** While over the cap, the build also
carries exhibit text below legible size (§4), which is the specific remedy §10.14 forbids.

**Required correction (no rerun, no new evidence needed):** re-measure B1/B2 on the current
build, record the page-count row in `phase_gate_register.csv`, and either (a) apply the §6 valve
until B1 ≤ 34 and B2 ≤ 12,000, or (b) raise a change request in
`papers/governance/change_request_register.csv` that re-baselines the caps with a stated
justification — the budget document itself says the caps "change only via a change-request entry".
Silently exceeding them is the one option the governance forbids.

---

## 4. **S17-09 (Moderate, P2, CONFIRMED)** — main-text figure text below legible size

`papers/DT-GSK.pdf` p.28 is **Figure 4** (four-panel Nemenyi critical-difference plots). Measured
span sizes on that page: **4.2 pt** (112 chars — the bar value labels `2.88`, `2.50`, `2.21`,
`2.34` …), **4.7 pt** (196 chars — algorithm names on the category axis), **5.2 pt** (450 chars —
axis ticks and axis titles). Whole-document histogram for the main PDF: 4.2 pt ×112, 4.7 pt ×196,
5.0 pt ×6, 5.1 pt ×14, 5.2 pt ×450, 5.5 pt ×9, 5.6 pt ×28, 5.8 pt ×20, 6.0 pt ×306, 6.2 pt ×27.

The project's own note in `papers/build_prompt_phases/phase_03/parameter_table_detail.tex` L4
cites "**the journal's 8 pt table guidance**" as the reason a 5.3 pt table was unacceptable. The
same standard applied to Figure 4 fails: the numbers a reader must read off the CD panels are at
half that size.

Rendered inspection of p.28 also shows roughly the top third of the page empty above the float,
so the figure could be enlarged without costing a page — the shrinkage buys nothing.

**Required correction:** regenerate the CD panels with in-figure text at ≥ 8 pt at final size
(increase the figure's physical width or the generator's font size), and re-render. Purely a
presentation regeneration: no value changes.

---

## 5. **S17-07 (Moderate, P2, CONFIRMED)** — the vendored MDPI class is six years old and locally modified

**Age.** `papers/Definitions/mdpi.cls` L23:
`\ProvidesClass{Definitions/mdpi}[08/17/2020 MDPI paper class]`. Phase 4 recorded
"VERIFY-BEFORE-SUBMISSION: confirm the vendored `mdpi.cls` matches the CURRENT template version"
(`phase_04/journal_requirements.md` §3); that check has never been performed (it depends on the
same blocked live-page access, §7). A direct consequence is measurable: the class provides
**no** `\dataavailability`, `\institutionalreview` or `\informedconsent` macro (only
`\sampleavailability`, L870), which is why three declarations are hand-coded and mis-set (§6).

**Local modification.** Commit `574e2deb4` ("review(R6): … copyright removal …", 2026-07-12)
edits the class to remove two submit-mode elements:

```
-					Submitted to {\em\journalname}, %
+					%% "Submitted to <journal>" footer text suppressed (author request)
```
```
-			\noindent \copyright{} {\@ \the\year} by the \@authornum. %
-			Submitted to {\em \journalname} for possible open access publication …
+			%% submit-mode copyright/license block suppressed (author request)
```

**Suppressed peer-review line numbering.** `papers/main.tex` L15
(`\let\linenumbers\relax`) and L15 (`\AtBeginDocument{\lhead{}}`) neutralise the class's
`lineno`-based continuous line numbering and the submit-mode running header. Verified in the
output: **no line numbers appear on any of the 39 pages**.

**Why it matters:** MDPI's `submit` mode exists to give reviewers and the editorial office a
stable reference frame. Submitting a `submit`-mode manuscript with the line numbers removed
predictably produces a "please add line numbers" request, and a class file that differs from the
journal's own will be replaced at production — so anything that depends on the local edits is
fragile. This is a **compliance and workflow** finding, not a scientific one.

**Required correction:** restore `\linenumbers` for the submitted build (the two `\let`/`\lhead`
overrides can be kept in a separate reading build), and either refresh `mdpi.cls` from MDPI's
current distribution or record a change request documenting the deliberate divergence and its
scope.

---

## 6. **S17-08 (Moderate, P2, CONFIRMED)** — back-matter declaration typography is inconsistent

Measured span sizes and fonts on `papers/DT-GSK.pdf` p.35–36:

| Declaration | Rendered size | Label form | Set by |
|---|---|---|---|
| Supplementary Materials | 9.06 pt | `Label:` bold run-in | class macro `\supplementary` |
| Author Contributions | 9.06 pt | `Label:` bold run-in | class macro `\authorcontributions` |
| Funding | 8.97 pt | `Label:` bold run-in | class macro `\funding` |
| Institutional Review Board Statement**.** | **9.96 pt** | `Label.` | hand-coded in `main.tex` |
| Informed Consent Statement**.** | **9.96 pt** | `Label.` | hand-coded in `main.tex` |
| Data Availability Statement**.** | **9.87 pt** | `Label.` | hand-coded in `main.tex` |
| Use of Generative Artificial Intelligence**.** (p.36) | body size | `Label.` | hand-coded in `main.tex` |

Four of the seven back-matter blocks are set one point larger than the other three and terminate
their label with a period instead of a colon. In the MDPI house style the back matter is uniform
9 pt with a bold `Label:` run-in. A production editor will flag this; it also visually implies the
hand-coded blocks are body text rather than declarations.

**Required correction:** define local `\newcommand`s mirroring `mdpi.cls` L850–868
(`\par\vspace{6pt}\noindent{\fontsize{9}{9}\selectfont\textbf{Data Availability Statement:} …}`)
for the four hand-coded declarations, or upgrade the class (§5) and use its native macros.

---

## 7. **S17-16 (BLOCKED)** — Gate P journal-instruction axis

Direct retrieval of the official Instructions-for-Authors page failed in this review:

* `WebFetch https://www.mdpi.com/journal/algorithms/instructions` → **HTTP 403 Forbidden**
  (2026-07-22) — the same block Phase 4 hit on 2026-07-10.
* Browser route unavailable in this environment (`preview_start` timed out after 300 s).

`papers/build_prompt_phases/phase_04/journal_requirements.md` therefore still carries
`verified_online = FALSE` and its §11 four-item blocking checklist, and
`phase_11/journal_reverification_note.md` §4 explicitly carries it forward as an unclosed
author-side pre-submission step. Every venue-specific row in `journal_compliance_matrix.csv`
marked `SEARCH-DERIVED` rests on official-page text returned through web search, not on a
retrieved page.

Per Stage 17's gate clause, **Gate P is `BLOCKED`, not `FAIL`, on this axis.**

**Minimum evidence required to unblock (all author-side, browser, ~15 minutes):**

1. Open `https://www.mdpi.com/journal/algorithms/instructions` in a browser; record the access
   date and archive the page.
2. Confirm no journal-specific hard page/word cap (else re-bind §10.14 to the published cap and
   update `page_budget.md`).
3. Confirm the peer-review model (single- vs double-blind) and whether an anonymised build is
   required.
4. Confirm the current `mdpi.cls` template version against the vendored 2020 copy (§5).
5. Confirm the mandatory declaration-block list and ordering, and the figure
   resolution/format requirements.
6. Confirm the current APC (recorded CHF 1800; currently reported ≈ CHF 1600).
7. Flip `verified_online = true` with the new access date and reconcile any divergence via
   `change_request_register.csv`, not a silent edit.

---

## 8. Exact list of upload-blocking defects

Ordered by what stops the submission form, not by scientific severity.

| # | Defect | Location | Owner | Status |
|---|---|---|---|---|
| 1 | Second author's e-mail is a rendered placeholder: `[H.S.M.R. institutional e-mail — to be added at submission]` | `DT-GSK.pdf` p.1 **and** `DT-GSK.docx` author block | author (AG-0002) | **OPEN** — MDPI requires an e-mail per author. Declared out of *review* scope by `PAPER_REVIEW_PROMPT.md` §1.5.4, so it is listed here as an upload action, not as a review ticket. |
| 2 | ORCID iDs are `0000-0000-0000-0000` placeholders in `main.tex` (never rendered) | `papers/main.tex` `\orcidauthorA/B/C` | author (AG-0002) | **OPEN** — required in the submission system. |
| 3 | Data Availability statement names no repository URL and no DOI | `DT-GSK.pdf` pp.35–36 | author (AG-0006 / R-0004) | **OPEN** — correctly not fabricated; must be supplied. |
| 4 | Supplement Table A19 truncated off the page edge (all seven `Notes` cells lost) | `supplementary.pdf` p.48 | production | **OPEN** — ticket S17-02. |
| 5 | Live journal-instruction re-verification not performed (`verified_online = false`) | `phase_04/journal_requirements.md` | author | **OPEN** — ticket S17-16; blocks Gate P. |
| 6 | Word open → update fields → save → reopen validation never executed (deviation **D-WORD-01**) | `papers/governance/word_validation_report.md` §1 | author | **OPEN** — see `word_validation_report.md` §T5. |
| 7 | Reviewer suggestions / exclusions not yet prepared | submission system | author | **OPEN** — advisable given the eGSK/GSK co-authorship overlap declared in the COI statement. |
| 8 | Page/word budget breach unrecorded and unresolved | `phase_gate_register.csv`; `page_budget.md` §6 | production/governance | **OPEN** — ticket S17-01. Administrative, not scientific. |

Items 1–3 and 5–7 are **administrative** blockers. Items 4 and 8 are **production** blockers.
**No scientific blocker was found by this seat.**

---

## 9. Ticket register (schema §5.4) — PDF/venue tickets

```text
ticket_id: S17-01
review_stage: 17
reviewer_role: JCO / T7-VENUE
severity: Major
priority: P1
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/DT-GSK.pdf (whole); papers/governance/phase_gate_register.csv; papers/build_prompt_phases/phase_04/page_budget.md
claim_id_or_artifact_id: profile 10.14 page-limit rule; budget B1/B2
concise_issue: The binding self-imposed page and word caps are exceeded and no page-count row records the current build.
exact_evidence_or_observation: DT-GSK.pdf is 39 pp; back matter starts p.35; references pp.37-39. B1 = 35 pp (Phase-8 convention) or 36 pp (Phase-11 arithmetic) against a 34-page hard cap. B2 = 12,007 body-prose words + 197 abstract + ~1,164 caption words ~= 13,368 against a 12,000 cap. phase_gate_register.csv records page counts only for Phase 8 (34 pp / B1 31) and Phase 11 (35 pp / B1 32).
root_cause: Post-Phase-11 content growth (R-01..R-14 remediation plus earlier additions) was never re-measured against the frozen budget, and the section 6 overflow valve was never invoked.
scientific_or_editorial_justification: Profile 10.14 makes measurement-and-recording a gate condition, and permits overflow to be resolved only by supplement migration.
impact_on_validity_or_acceptance: No effect on validity. MDPI publishes no hard cap, so acceptance risk is low; the defect is governance non-compliance and a length signal (>12,000 words triggers MDPI's contact-the-office guidance).
required_correction: Re-measure B1/B2 on the current build, record a page-count row in phase_gate_register.csv, and either apply the section 6 valve or re-baseline the caps through change_request_register.csv.
acceptable_alternatives: A change request that re-baselines B1/B2 with justification, provided the new caps are measured and recorded.
additional_evidence_needed: None.
dependencies: S17-09 (do not close by shrinking exhibits further); S17-16 (a published journal cap would supersede the self-imposed one).
expected_improvement: Restores the 10.14 audit trail; removes an easily-checked governance inconsistency from the package.
post_revision_verification: A phase_gate_register.csv row stating the measured page count for the submitted PDF, with B1 <= cap and B2 <= cap, or an APPROVED change-request row.
status: open
```

```text
ticket_id: S17-02
review_stage: 17
reviewer_role: PROD-PDF / T4-SOFT
severity: Major
priority: P1
confidence: Confirmed
issue_type: exhibit
manuscript_location: papers/supplementary.pdf p.48 (Table A19); papers/build_prompt_phases/phase_03/parameter_table_detail.tex L9-L68
claim_id_or_artifact_id: tab:parameters-detail
concise_issue: Table A19 overflows the page by 218.99 pt; all seven Notes cells are cut off the paper edge and lost from the PDF.
exact_evidence_or_observation: supplementary.log L1647 "Overfull \hbox (218.9852pt too wide) in paragraph at lines 19--68"; measured p.48 text bbox right edge 598.8 pt on a 595.276 pt page (80.1 pt past the 518.7 pt text margin); all seven source Notes strings probe False in the rendered PDF text and True in supplementary.docx.
root_cause: \begin{tabular}{lll} with no p{} column and no \resizebox; the N-013 split of parameter_table.tex traded a 5.3 pt font for an unconstrained width.
scientific_or_editorial_justification: A submitted supplement must be legible and complete; these are the frozen constants the Data Availability statement promises make the configuration reproducible from the text.
impact_on_validity_or_acceptance: Reproducibility-relevant content loss in a submitted artifact and a real PDF/Word divergence; a production editor or careful reviewer will see it immediately.
required_correction: Make column 3 a p{} column (or use tabularx/longtable at a fixed total width), rebuild, and re-verify.
acceptable_alternatives: Move the Notes column to a following paragraph, or split the table by subsystem.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Removes the only off-page overflow in the package and the only confirmed PDF/Word content divergence.
post_revision_verification: grep -c "Overfull" papers/supplementary.log == 0; per-page max text x <= 518.7 pt on every page; all seven Notes strings recoverable from the rendered PDF text.
status: open
```

```text
ticket_id: S17-07
review_stage: 17
reviewer_role: PROD-PDF / T7-VENUE
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/Definitions/mdpi.cls L23, L500, L1140; papers/main.tex L15, L19
claim_id_or_artifact_id: journal template compliance
concise_issue: The vendored MDPI class is dated 2020 and has been locally modified; the class's peer-review line numbering, submit-mode footer and CC-BY block are suppressed.
exact_evidence_or_observation: \ProvidesClass{Definitions/mdpi}[08/17/2020 MDPI paper class]; commit 574e2deb4 replaces the "Submitted to <journal>" footer and the copyright/licence block with comments; main.tex L15 "\let\linenumbers\relax"; rendered PDF has no line numbers on any of 39 pages; the class provides no \dataavailability/\institutionalreview/\informedconsent macros (only \sampleavailability, L870).
root_cause: Class vendored once and never refreshed; submit-mode furniture removed for reading comfort.
scientific_or_editorial_justification: Stage 17 requires the correct current template/class; MDPI submit mode supplies the line numbers reviewers cite.
impact_on_validity_or_acceptance: No effect on validity; a predictable editorial revision request and a production-side risk if local class edits are relied on.
required_correction: Restore \linenumbers for the submitted build and refresh mdpi.cls against MDPI's current distribution (or record the divergence as a change request).
acceptable_alternatives: Keep the reading build unnumbered and produce a separate numbered submission build.
additional_evidence_needed: The current MDPI template version - depends on S17-16.
dependencies: S17-16; S17-08 (a current class removes the hand-coded declaration blocks).
expected_improvement: Removes a near-certain editorial request and re-aligns the build with the journal template.
post_revision_verification: Rendered PDF shows continuous line numbers; mdpi.cls \ProvidesClass date matches the distributed template or a change-request row exists.
status: open
```

```text
ticket_id: S17-08
review_stage: 17
reviewer_role: PROD-PDF
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: production
manuscript_location: papers/DT-GSK.pdf pp.35-36; papers/main.tex back-matter block
claim_id_or_artifact_id: back-matter declarations
concise_issue: Four back-matter declarations are set at body size with a period-terminated label while the other three are set by the class at 9 pt with a colon run-in.
exact_evidence_or_observation: Measured span sizes on p.35 - Supplementary Materials 9.06 pt, Author Contributions 9.06 pt, Funding 8.97 pt versus Institutional Review Board Statement. 9.96 pt, Informed Consent Statement. 9.96 pt, Data Availability Statement. 9.87 pt.
root_cause: The vendored 2020 class has no macro for these declarations, so main.tex hand-codes them with \noindent\textbf{...}\quad at body size.
scientific_or_editorial_justification: MDPI back matter is uniform; inconsistent sizing reads as an unfinished document.
impact_on_validity_or_acceptance: Cosmetic but immediately visible to a production editor.
required_correction: Define local macros mirroring mdpi.cls L850-868 (9 pt, bold "Label:") for the four hand-coded declarations.
acceptable_alternatives: Refresh the class (S17-07) and use its native macros.
additional_evidence_needed: None.
dependencies: S17-07.
expected_improvement: Uniform, house-style back matter.
post_revision_verification: All back-matter declaration labels render at ~9 pt with a colon run-in.
status: open
```

```text
ticket_id: S17-09
review_stage: 17
reviewer_role: PROD-PDF / T5-WRITE
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: exhibit
manuscript_location: papers/DT-GSK.pdf p.28 (Figure 4, Nemenyi CD panels)
claim_id_or_artifact_id: F01 / fig:nem-grid
concise_issue: In-figure text is 4.2-5.2 pt, roughly half the 8 pt guidance the project itself cites, in a manuscript already over its page cap.
exact_evidence_or_observation: Page-28 span histogram - 4.2 pt x112 chars (bar value labels), 4.7 pt x196 (algorithm names), 5.2 pt x450 (axis ticks/titles). parameter_table_detail.tex L4 cites "the journal's 8 pt table guidance". Roughly the top third of p.28 is empty above the float.
root_cause: Four CD panels packed into one float without enlarging the generator's font size.
scientific_or_editorial_justification: Stage 17 requires legible final-size exhibits; profile 10.14 forbids resolving overflow by shrinking figures below legibility.
impact_on_validity_or_acceptance: The reader cannot read the mean-rank values that carry the paper's headline comparison.
required_correction: Regenerate the CD panels with in-figure text at >= 8 pt at final size and re-render.
acceptable_alternatives: Split the four panels across two floats at larger size.
additional_evidence_needed: None.
dependencies: S17-01 (enlargement must not be paid for by exceeding the cap further).
expected_improvement: The headline rank figure becomes readable in print.
post_revision_verification: Minimum span size within Figure 4 >= 8 pt in the rendered PDF.
status: open
```

```text
ticket_id: S17-16
review_stage: 17
reviewer_role: JCO / T7-VENUE
severity: Major
priority: P1
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/build_prompt_phases/phase_04/journal_requirements.md; phase_11/journal_reverification_note.md section 4
claim_id_or_artifact_id: Gate P journal-instruction axis
concise_issue: Current official journal guidance could not be retrieved, so the journal-instruction axis of Gate P is BLOCKED rather than passed.
exact_evidence_or_observation: WebFetch of https://www.mdpi.com/journal/algorithms/instructions returned HTTP 403 on 2026-07-22 (identical to 2026-07-10); browser route timed out. verified_online = FALSE persists with four unclosed re-verification items.
root_cause: mdpi.com blocks automated clients; the author-side browser re-verification step has never been executed.
scientific_or_editorial_justification: Section 15 forbids declaring compliance from remembered or unofficial instructions; the Stage 17 gate clause mandates BLOCKED in this situation.
impact_on_validity_or_acceptance: Any undetected instruction change (length cap, review model, template version, declaration list) becomes a desk-check risk.
required_correction: Perform the seven-step browser re-verification listed in section 7 of this report and flip verified_online to true with an access date.
acceptable_alternatives: None - this is the sole exception mechanism's own precondition.
additional_evidence_needed: The live page.
dependencies: S17-07 (template currency) and S17-14 (APC) resolve with it.
expected_improvement: Converts Gate P from BLOCKED to a decidable PASS/FAIL.
status: blocked
```

---

## 10. Gate P — PDF/venue axis verdict

**`Gate P — Journal and Production Compliance`: BLOCKED (journal-instruction axis) with two
Major production findings open (S17-01, S17-02).**

The build itself is clean and deterministic — zero undefined references or citations, zero
missing assets, all fonts embedded, correct metadata and bookmarks, vector figures, and a
byte-verified submission manifest. The gate does not pass because (a) current official journal
guidance is unavailable, (b) the profile 10.14 page-limit rule is breached and unrecorded, and
(c) one supplement table loses content off the page edge.
