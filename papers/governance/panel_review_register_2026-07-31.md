<!-- Filed 2026-07-31. Eight-seat expert review panel applying papers/PAPER_REVIEW_PROMPT.md
     (layer 1.5.0-O) over the pass-24/25 v2.0 manuscript; workflow wf_b55700c9-59e,
     1.66M subagent tokens, 502 tool uses; synthesis seat adversarially verified every
     BLOCKING/MAJOR quote byte-for-byte; both BLOCKING items independently re-verified
     at filing time against HEAD a523a2591. All fixes are PROPOSED and await author
     decision; I-1 is author-gated (Amendment 3 to the registered wording bank). -->

# FINAL REVIEW REGISTER — DT-GSK submission (panel synthesis)

Root for all paths: `D:\AI\PhD-Projects\00-GSK-Family\02-GSK_Family_Python_v1.1\`. Verified against the CURRENT tree (HEAD a523a2591; tag `dtgsk-submission-v2.0-2026-07-31` = pass-25 mint commit 457a9f50f; `check_manifest` 15/15). Line numbers below are re-verified current positions (some seat-reported lines shifted ±2 after the mid-review affiliation correction).

## ADVERSARIAL VERIFICATION LOG (BLOCKING/MAJOR) + DROPS

| Candidate | Verification performed by synthesis seat | Outcome |
|---|---|---|
| SEAT6-1 (AGSK "won" CEC2020) | Grepped all 8 manuscript/letter loci (found verbatim); read `papers/governance/evidence_cards/apgsk2021.md` ("Actually, AGSK [19] is the runner up in CEC2020 competition." Sect. I, p. 65936; "IMODE = winner, AGSK = runner-up, J2020 = third") and `mohamed2020agsk.md` (explicit do-not-miscite warning); grepped `papers/governance/` for "runner" — the W5 sweep (lines 167–184) verified only verbatim-ness and adjudication of disclosure *presence*, never the factual clause | **CONFIRMED — BLOCKING.** Does not contradict the binding standings (fourth; AGSK first-in-panel untouched); the verbatim requirement is satisfied by amending the registered bank (append-only Amendment 3, Amendment-2 precedent) |
| SEAT3-1 (S5.4 denies D=1000 evidence) | Read `papers/supplementary.tex:1345-1347` — exact quote confirmed ("Fifth, the evidence ceiling is $D = 100$..."); read claims matrix LM-05 row (status REVISED_CR-0019; risk field literally predicts "a stale 'no D=1000 evidence exists' statement now contradicted by RS-12/RS-13/LM-06"); read `conclusions.tex:86-167` confirming the conclusions carry the revised LM-05 + LM-06, so S5.4's "moved rather than rewritten" preamble (1305–1309) is also false | **CONFIRMED — BLOCKING** |
| SEAT2-1 / SEAT3-4 / SEAT5-1 (cover-letter Nemenyi) | Read `papers/cover_letter.tex:55` (exact quote); recomputed from `papers/analysis/lsgo-rel-2026-07-28-ff1a046ef/cec2013lsgo/`: eGSK 5.466667 − DT-GSK 3.133333 = 2.333334 > CD 2.326203; manuscript's own `performance.tex:899-902` states the separation | **CONFIRMED — MAJOR (3 seats)** |
| SEAT4-1 / SEAT7-1 (S5.10 provenance) | Read `supplementary.tex:1852-1858` — exact quote confirmed; contradicts DAS (`main.tex`), supplement abstract, S7/S8 provenance sentences | **CONFIRMED — MAJOR (2 seats)** |
| SEAT3-2 (S5.3 three-suite selection disclosure) | Read `supplementary.tex:1273-1301` — "reused across all three suites" and a held-out summary naming only CEC2011/CEC2013, omitting CEC2020 fourth and LSGO tied-first | **CONFIRMED — MAJOR** |

Dropped/reclassified: **SEAT7-2** (superseding tag) — OVERTAKEN mid-review: tag `dtgsk-submission-v2.0-2026-07-31` now exists at the pass-25 commit and D-0027 records the supersession; moved to UPDATES. **SEAT2-3** — consumed by SEAT2-4 (Seat 2's own note). **SEAT3-6** — W5 Item 3 adjudicated the cover-letter paraphrase "not a deviation"; the seat's specificity argument is new, so it survives, but only as an ENHANCEMENT folded into the single cover-letter sentence rewrite. Nothing was refuted as a misquote: every BLOCKING/MAJOR quote matched the files byte-for-byte. Spot-verified minors also all held (escape-gate code at `_dt_core.py:3923/3926`; stale budget parenthetical in both phase_03 exhibits; κ_ls 0.65 at `supplementary.tex:1790`; "low-powered" absent from S7 (sole hit :2923); tie-band variant absent from S7.3; attestation.json = 488 tests ×2 vs printed 474; CR register ends at CR-0020; "favourable/favours" at all 7 sites; singular-release phrasing at `introduction.tex:126-128` and `conclusions.tex:170-172`; release id inline at `performance.tex:225`).

---

## SECTION 1 — ISSUES (defects, severity-ordered)

| # | Seats (agreement) | Severity | Location | Defect | Evidence |
|---|---|---|---|---|---|
| I-1 | SEAT6-1 (1; synthesis-confirmed against corpus) | **BLOCKING** | `papers/main.tex:166` (abstract), `:375` (COI); `papers/sections/performance.tex:800,874`; `papers/sections/conclusions.tex:60`; `papers/supplementary.tex:2827,2854`; `papers/cover_letter.tex:55`; origin `papers/build_prompt_phases/phase_05/statistical_analysis_plan_addendum_cec2020_lsgo.md` | Eight loci assert AGSK **won** the CEC2020 competition; the corpus's own sanctioned source (apgsk2021, p. 65936, a co-author's paper, cited in this manuscript) states AGSK was the **runner-up** (IMODE won) — a false literature fact in the abstract, COI statement, and cover letter, in the direction that flatters the registered fourth place | "On AGSK's strongest suite---the CEC2020 competition it won---DT-GSK places fourth"; card: "Actually, AGSK [19] is the runner up in CEC2020 competition." |
| I-2 | SEAT3-1 (1) | **BLOCKING** | `papers/supplementary.tex:1345-1347` (S5.4 Fifth limitation); block preamble `:1305-1309` | S5.4 denies the paper's fifth suite exists ("evidence ceiling is $D=100$... unknown"), contradicting S7 (D=1000), conclusions LM-05(rev)/LM-06, and the claims matrix's own blocked-risk field; the preamble's "moved rather than rewritten" is false since the conclusions' limitations were revised under CR-0019 | "Fifth, the evidence ceiling is $D = 100$: behavior at the scale of large-scale global optimization is unknown, and no such claim is made." |
| I-3 | SEAT2-1, SEAT3-4, SEAT5-1 (3) | **MAJOR** | `papers/cover_letter.tex:55` | "never Nemenyi-separable at any tested suite or dimension" is falsified by the released LSGO analysis (gap 2.3333 > CD 2.3262) and by the manuscript's own p.34 sentence | quoted above; CSVs recomputed |
| I-4 | SEAT4-1, SEAT7-1 (2) | **MAJOR** | `papers/supplementary.tex:1852-1858` (S5.10 opening); also `:1860-1863` singular "bundle" | Attributes ALL empirical values in both documents to the primary release; false for CEC2020/CEC2013LSGO panels (their own releases) and S6 (ablation release); contradicts the DAS, supplement abstract, S7/S8 | "All empirical values in the main paper and in this Supplementary Material derive from the promoted, read-only evidence release... rel-2026-07-20-67d9345f9" |
| I-5 | SEAT3-2 (1) | **MAJOR** | `papers/supplementary.tex:1273-1301` (S5.3) | Selection-exposure disclosure is three-suite-scoped; its "held-out evidence is mixed" summary silently omits the least favorable held-out results (CEC2020 fourth; LSGO tied-first) — favorable-only framing by staleness on the paper's key honesty surface | "reused across all three suites"; held-out list ends at CEC2013 |
| I-6 | SEAT3-3 (+2 synthesis-found) (1) | MINOR | `papers/supplementary.tex:1172` ("identical across all three suites"), `:1327-1328` (S5.4 Third: "the three suites"), `:1106` ("all three suites" — scoped by "21 (suite, optimizer) cells" but unqualified) | Residual stale three-suite statements; :1172 contradicts the main text's "identical across the four bound-constrained suites" + disclosed LSGO exception | quoted |
| I-7 | SEAT2-2 (1) | MINOR | `papers/main.tex:163-165` (abstract); echo in `cover_letter.tex:55` | "second behind eGSK at $D = 30$ and on CEC2011, where the loss is Holm-significant" is misreadable as covering D=30 (p_Holm=0.199, not significant) | quoted |
| I-8 | SEAT3-5, SEAT5-8 (2) | MINOR | `cover_letter.tex:59` vs `main.tex:338,354` | GenAI version mismatch: letter "(Claude Opus 4.8)" vs manuscript "(Claude Opus 4.6, 4.8 and 5.0)" | quoted |
| I-9 | SEAT5-7 (1) | MINOR | `cover_letter.tex:55` (2 sites) | "CEC2013-LSGO" hyphenated; manuscript writes "CEC2013LSGO" | quoted |
| I-10 | SEAT1-1 (1) | MINOR | `papers/sections/proposed_algorithm.tex:222`; `papers/build_prompt_phases/phase_03/algorithm_pseudocode.tex:59` | "a budget/ROI gate additionally gates the escape and the local search" — code-verified runtime-dead for the escape (`_dt_core.py:3923/3926`: `terra_escape_allowed = True` both branches); contradicts Figure 2's own LS-only label | quoted |
| I-11 | SEAT1-2 (1) | MINOR | `phase_03/algorithm_pseudocode.tex:31` (Algorithm 1 Require); `phase_03/notation_table.tex:40` | Budget parenthetical "($10^4D$; $150{,}000$ on CEC2011)" is three-suite-era; contradicts the five-suite accounting in §3.7 | verified in both files |
| I-12 | SEAT1-3 (1) | MINOR | `papers/supplementary.tex:1790` | Dormant subspace-LS gate stated as 0.65/0.45 tier split; executed profile is 0.45 at both $D\ge50$ tiers (seat-executed `pub_overrides`); contradicts supplement's own :1652 | verified quote |
| I-13 | SEAT1-4 (1) | MINOR | `proposed_algorithm.tex:548-550`; `supplementary.tex:~1714` | Learned-vs-random linkage assignment stated per-block; code commits per-row (a different operator for a reimplementer) | seat code trace `_dt_core.py:1055-1058, 3009-3019` |
| I-14 | SEAT4-6 (1) | MINOR | `sections/introduction.tex:126-128`; `sections/conclusions.tex:170-172`; `cover_letter.tex:55` | Singular-release phrasings ("a versioned, immutable evidence release bind[s] every reported number to that release") false under three coexisting releases | verified quotes |
| I-15 | SEAT2-4 (1) | MINOR | `supplementary.tex:~2479-2491` (S7.4) | Registered low-power disclosure (addendum §7 covers N=15 LSGO families) reproduced only in S8; absent from the LSGO no-separation surface ("low-powered" sole hit :2923) | verified absence |
| I-16 | SEAT7-3 (1) | MINOR | `supplementary.tex:2438-2444` (S7.3) | Of AN-ROB-LSGO's three registered robustness components only two are reported in rendered text; relative-tie-band variant silent (CSV verified all-agree by Seat 7) | verified absence |
| I-17 | SEAT5-2 (1) | MINOR | `performance.tex:861,862,953`; `conclusions.tex:67-68`; `cover_letter.tex:55` (×2) | Seven British spellings against dominant AmE, incl. same-paragraph and same-file mixes | verified all sites |
| I-18 | SEAT5-4, SEAT5-5 (1) | MINOR | `conclusions.tex:31,84,161`; `performance.tex:149,1129,~786,~1125`; `proposed_algorithm.tex:118,691` | Bare "Section~S7/S8/S6.5" refs missing "Supplementary"; raw hash 5c9bfae82 printed twice (second occurrence is a duplicated machine token per F.21) | seat quotes |
| I-19 | SEAT4-7, SEAT5-6 (2) | MINOR | `performance.tex:225` | Primary release id inline in §4.1 prose, second occurrence outside the DAS (F.5) | verified |
| I-20 | SEAT4-4 (1) | MINOR | `main.tex:291-293` vs `supplementary.tex:~1960` | DAS promises the ablation release is "identified and checksummed in the Supplementary Materials"; supplement only identifies it | seat grep |
| I-21 | SEAT5-3 (1) | MINOR | `conclusions.tex:15-19` | Consecutive-sentence "supporting mechanism / interaction-structure memory" repetition | seat quote |
| I-22 | SEAT6-2 (1) | MINOR | `references.bib` (li2013lsgo, yue2020cec2020 note fields) | Protocol-summary annotations on two references, absent from the three sibling suite references — inconsistent entry formatting | seat quote |
| I-23 | SEAT1-5, SEAT2-5, SEAT3-8, SEAT5-16, SEAT5-17, SEAT5-18, SEAT7-4 (1 each) | NOTE | various | D=5 linkage-gate caption note; two p-bound display-precision widenings (≤0.011/≤0.037); "enter no headline" caption gloss; C3-bullet apposition fragment; "does not count" colloquialism (registered echo — optional); three Oxford commas; stale source comments | per seat rows |

## SECTION 2 — ENHANCEMENTS (not defects)

| # | Seat | Suggestion |
|---|---|---|
| E-1 | SEAT3-7 | Append mitigation sentence to the COI block (comparators re-executed mechanically under the optimizer-independent seed schedule; released pipeline re-derives every number) — directly blunts the panel's #1 predicted rejection objection |
| E-2 | SEAT3-6 | Cover letter: "exactly the boundary condition the pre-registered plan predicted" → "consistent with the boundary condition the registered directional expectation predicted" (fold into the I-1/I-3 sentence rewrite) |
| E-3 | SEAT6-3 | Related-work third deficiency: add forward pointer "This paper meets that regime head-on: CEC2020 at $D \le 20$ serves as the pre-registered confirmatory suite (Section~\ref{sec:exp:cec2020})." |
| E-4 | SEAT5-10 | tab:cec2020-ranks caption: one sentence explaining 3-dp cells vs 4-dp aggregate; do NOT re-round cells |
| E-5 | SEAT5-11 | tab:lsgo-ranks: "tied-first" → "1 (tied-first)" to match Table A27 |
| E-6 | SEAT5-12 | Comparator-params caption: append "Bracketed lists are per-arm pools; ranges are written first:step:last." |
| E-7 | SEAT5-13 | Abstract suite-role list → "Suite roles: CEC2017 selection-exposed; CEC2011 and CEC2013 corroborative; ..." |
| E-8 | SEAT5-14 | Tighten the ATMALS effect-layer sentence (single conclusion statement) |
| E-9 | SEAT5-15 | Thin the "registered" drumbeat (2–3 substitutions, e.g. "pre-committed instability rule") |

## SECTION 3 — UPDATES (changed underneath text/tooling; refresh, no manuscript defect)

| # | Source | Update |
|---|---|---|
| U-1 | SEAT7-2 (overtaken) | Tree moved mid-review: affiliation correction (2d29e2606), pass-25 re-freeze (457a9f50f), tag `dtgsk-submission-v2.0-2026-07-31`, D-0027 (a523a2591). Seat reports citing tag v2.0-2026-07-29/7d1fba861 are stale; supplementary.tex line references shifted ±2. No further tag action needed now; next re-mint requires its own tag decision (see fix order) |
| U-2 | SEAT4-2 | Environment attestation predates the five-suite state and records 488 tests ×2 vs the printed "474" (`supplementary.tex:1874-1875`, verified). Regenerate via `papers/scripts/make_environment_attestation.py` at the final state and print its count (text edit is part of the I-batch) |
| U-3 | SEAT4-3 | `runbook.md`: CEC2020 example `--runs 51` → 30 (config is correct; prose wrong); ablation step `--runs 25` → 51; repoint stale `rel-2026-07-10-262fc16c9`; add the two new-suite campaign launchers + `phase6b_run_analysis_newsuites.py --suite both`. Repo-side only, no rebuild |
| U-4 | SEAT4-5 | `benchmarks/cec_reference_results/_ablation/README.md` still titled abl-rel-2026-07-16 vs manifest abl-rel-2026-07-20; refresh as dated A2 documentation-only amendment; refresh SA01/SA02 word-source `notes` at next regeneration |
| U-5 | SEAT5-9 | File **CR-0021** (register verified ending at CR-0020): five-suite build exceeds CR-0008 caps (B1 41pp>40; B2 ~23k>20k); record CR-0019 scope change as cause and re-set caps. Do NOT trim (LM-06 "may not be cut for page budget") |
| U-6 | SEAT1-1/SEAT7-4/SEAT5-19 | Non-rendered comment hygiene: `phase_03/algorithm_pseudocode.md:70` stale gate comment; `supplementary.tex:2,162-163` "S1..S6"/"non-ablation" comments; review-prompt §1.5.1 stale "≈205 source words" note |

## SECTION 4 — PROPOSED FIXES

All I-fixes are textual; none touches a number, standing, test, or datum; none requires any rerun. Every fix marked [REBUILD] edits a freeze-tracked file or a source feeding the built artifacts and therefore **voids the pass-24/25 mint** — apply as ONE batch, rebuild ×2 at pinned epochs (PDF 1783468800; DOCX 1783641600 — beware the persisted-env-var trap), re-run parity + validators, then a **pass-26 re-mint** and a superseding tag (recommend `dtgsk-submission-v2.1`, do not move v2.0, record in decision log per D-0027 precedent). `main_pandoc.tex`/`supplementary_pandoc.tex` are build intermediates — never hand-edit.

| # | Fix | Effort | Rebuild/re-mint |
|---|---|---|---|
| I-1 | **Author-gated.** (i) Append dated **Amendment 3** to the SAP addendum correcting the factual clause, citing apgsk2021 p. 65936. (ii) All four bank loci verbatim-together: "On AGSK's strongest suite --- the CEC2020 competition in which it was the runner-up --- \dtgsk{} places fourth; the family panel corroborates AGSK's published strength in this regime, consistent with the tiering thesis: every dimension-gated \dtgsk{} subsystem is inactive at $D \leq 20$." (add `~\cite{apgsk2021}` after "runner-up" outside the abstract). (iii) `main.tex:375`: "AGSK was the runner-up of the CEC2020 competition whose suite serves...". (iv) `performance.tex:874` / `supplementary.tex:2827`: "\agsk{} was the runner-up of the CEC2020 competition~\cite{apgsk2021}, and its paper is a co-author's." (v) Cover letter: "on CEC2020 --- the competition in which our comparator AGSK was the runner-up --- \dtgsk{} places fourth of seven, ...". (vi) Note the amendment in the claims-matrix RS-12 row. | M | [REBUILD] + amendment (governance, no rebuild itself) |
| I-2 | Replace the Fifth limitation with the revised LM-05 wording (as in the claims matrix / SEAT3-1's replacement text: per-suite ceilings; component-isolation ceiling $D\le100$; no component attribution at D=1000) + append the LM-06 specialist sentence; fix Third's "the three suites" → "the five suites" (covers part of I-6); soften preamble :1305-1309 to "...the wording follows the conclusions of the submitted manuscript" (drop "moved rather than rewritten") | M | [REBUILD] |
| I-3 | `cover_letter.tex:55`: "at any tested suite or dimension" → "at any CEC2017 dimension" | S | [REBUILD] (cover_letter.pdf is freeze-tracked) |
| I-4 | Replace the S5.10 opener with the three-release sentence (SEAT4-1/SEAT7-1 text, file counts 3,403 / 173 / 336 verified): primary release for CEC2017/2011/2013, the two named non-superseding releases for LSGO/CEC2020, ablation release for S6; ":1862 "a checksummed analysis bundle" → "checksummed analysis bundles" | S | [REBUILD] |
| I-5 | `supplementary.tex:1273-1276`: "across all five suites, with the single disclosed CEC2013LSGO linkage-block exception (Section~S7)"; add "No CEC2020 or CEC2013LSGO result existed when the configuration was frozen; the sole later configuration change --- the two CEC2013LSGO linkage-block-size entries --- is disclosed with its timing in Section~S7."; extend the held-out sentence to "...second on CEC2011 (a Holm-significant loss to \egsk{}), third on CEC2013 at $D = 30$ but first overall (2.80), fourth on the pre-registered CEC2020, and tied-first descriptive on CEC2013LSGO; the non-development evidence is therefore mixed --- strongest where the tiered subsystems are active and weakest where they are structurally off --- rather than uniformly favorable or unfavorable." | M | [REBUILD] |
| I-6 | `:1172` → "identical across the four bound-constrained suites (no per-suite tuning), with the single disclosed CEC2013LSGO linkage-block exception (Section~S7)"; `:1106` → "on the primary release's three suites" | S | [REBUILD] |
| I-7 | Abstract: "...it is second behind eGSK at $D = 30$ and on CEC2011; the CEC2011 loss is Holm-significant." Same disambiguation in the cover-letter sentence | S | [REBUILD] |
| I-8 | Cover letter → "(Claude Opus 4.6, 4.8 and 5.0, Anthropic)" | S | [REBUILD] |
| I-9 | "CEC2013-LSGO" → "CEC2013LSGO" (both sites) | S | [REBUILD] |
| I-10 | Both loci: "; a budget/ROI gate additionally gates the local search (a matching hook exists on the escape but never blocks it in the frozen configuration)." + U-6 comment fix | S | [REBUILD] |
| I-11 | Both exhibits: replace parenthetical with "(suite-dependent; Section~\ref{sec:alg:complexity})" | S | [REBUILD] |
| I-12 | `:1790` → "($\kappa_{\mathrm{ls}}=0.45$ at $D\ge 50$, the static warm-up value, thereafter superseded by the same adaptive rolling-median rule as the linkage gate)" | S | [REBUILD] |
| I-13 | SEAT1-4's per-row replacement text in main + supplement (blockwise row draws its block *set* from the learned partition w.p. 0.5) | M | [REBUILD] |
| I-14 | Pluralize: intro "versioned, immutable evidence releases bind every reported number to its release"; conclusions "the versioned evidence releases accompanying this article"; cover letter "read-only evidence releases to which every reported number is bound" | S | [REBUILD] |
| I-15 | Append SEAT2-4's one-sentence pre-committed low-power echo to S7.4 ("...low-powered by construction (Nemenyi critical distance $2.326$ against $1.673$ at the $N=29$ CEC2017 families), so non-significance ... never as equivalence.") | S | [REBUILD] |
| I-16 | S7.3 insert: ", the registered relative-tie-band variant leaves every win/tie/loss split unchanged on the raw basis," | S | [REBUILD] |
| I-17 | favourable→favorable, unfavourable→unfavorable, favours→favors (7 sites; A2.3 mandates content, not spelling — supplement already renders AmE) | S | [REBUILD] |
| I-18 | Prefix "Supplementary " at the seven bare sites; replace the second hash parenthetical with "(the registered addendum's signing commit precedes the first CEC2020 result; Section~\ref{sec:exp:cec2020} and Supplementary Section~S8)" | S | [REBUILD] |
| I-19 | `performance.tex:225` → "released in the primary evidence release (Data Availability Statement)" | S | [REBUILD] |
| I-20 | S6 opening: insert "whose manifest records a SHA-256 checksum for each of its 1{,}297 files," (count verified by Seat 4) | S | [REBUILD] |
| I-21 | Second sentence → "That memory is a decaying, confidence- and evidence-gated coordinate-pair graph learned from the moves the run has already accepted." (MT-01 sentence untouched) | S | [REBUILD] |
| I-22 | Delete the two `note` fields from li2013lsgo/yue2020cec2020 (or keep deliberately); batch only | S | [REBUILD] (references.bib freeze-tracked) |
| I-23 | Apply the seat-specified one-liners (tab:dim-gating caption note; ≤0.011/≤0.037; "enter no confirmatory headline"; ", which together form the seven-algorithm GSK-family panel,"; optional scare quotes; 3 Oxford commas) — all optional, batch if applied | S | [REBUILD] |
| E-1..E-9 | Apply seat replacement texts; all wording-local, batch with the I-fixes | S each | [REBUILD] |
| U-2..U-6 | Repo-side regenerations/filings as specified | S–M | No rebuild (except U-2's "(488 tests)"/regenerated-count sentence, which is inside the I-batch) |

---

## PANEL VERDICT: **MINOR REVISION** — unanimous, 7/7

Tally: Seat 1 minor; Seat 2 minor; Seat 3 minor; Seat 4 minor; Seat 5 minor; Seat 6 minor (with one mandatory submission-blocking wording correction); Seat 7 minor. No seat found any defect in a number, standing, test, or registered outcome; the two BLOCKING items and three MAJORs are all sentence-level truth-maintenance failures — one false literature fact inherited by the registered wording bank (I-1), and four passages of pre-five-suite text the W1–W3 surgery missed (I-2, I-4, I-5) plus one over-generalization in the cover letter (I-3). Every fix is textual, requires no rerun, and preserves all binding standings verbatim-after-amendment.

**Recommended fix order:**
1. **Author decision + Amendment 3** to `papers/build_prompt_phases/phase_05/statistical_analysis_plan_addendum_cec2020_lsgo.md` (append-only) — gates I-1; no rebuild by itself.
2. **Governance filings with no rebuild:** CR-0021 (U-5), runbook (U-3), ablation README A2 amendment (U-4), regenerate environment attestation at the final state (U-2).
3. **Single manuscript batch:** all I-fixes (I-1 through I-22, discretionary I-23) + accepted enhancements + the "(488 tests)"/attestation-count sentence, editing `main.tex`, the five section files, `supplementary.tex`, `cover_letter.tex`, the two phase_03 exhibits, `references.bib`, and the RS-12 claims-matrix note.
4. **Rebuild ×2** (PDFs at epoch 1783468800; DOCX at 1783641600; verify DOCX epoch twice), re-run cross-format parity, citation/word validators, and the freeze schema checks.
5. **Pass-26 re-mint** of `papers/governance/main_manuscript_freeze_manifest.json` (this batch voids the pass-25 mint: 14 of the 15 tracked files change or are rebuilt), verify 15/15 twice.
6. **Tag decision:** mint `dtgsk-submission-v2.1-<date>` at the pass-26 state, record supersession of v2.0-2026-07-31 in the decision log (D-0028), leave prior tags in place; user pushes tags per standing practice.

---

## ADDENDUM (2026-07-31, author-directed) — algorithm-level limitations tracked alongside the issues

These two rows were added at the author's direction. They are REGISTERED EMPIRICAL OUTCOMES, not manuscript defects: the manuscript already discloses both (abstract, S5.3/S5.4-as-fixed, wording bank), no text change is sought here, and neither row joins the I-batch. A-2 is marked TO BE FIXED as a post-submission research objective; nothing about it may alter the frozen releases or the registered standings of this submission.

| # | Status | Finding | Disposition |
|---|---|---|---|
| A-1 | ACCEPTED (structural) | Below D~20 every dimension-gated subsystem is structurally off and DT-GSK runs as essentially base machinery — hence fourth of seven on CEC2020. This is the tiering thesis's predicted boundary condition, confirmed by the pre-registered suite. | Disclosed limitation; structurally explained (the low-D weakness was falsified as local-search waste and shown to be subsystem gating). No fix planned within this algorithm design. |
| A-2 | **TO BE FIXED** (post-submission research) | On real-world CEC2011 DT-GSK loses to eGSK, and that loss is the one Holm-significant result against it. | Author-directed follow-up research objective: close the eGSK gap on CEC2011. Existing lead: the frozen candidate-A survivor (opt-in ism_profile) from the tuning investigation, which needs wider-panel runs; prior dev-split findings (polish/restart tweaks insufficient; absolute mid-D gains did not convert to rank gains) bound the search space. MUST NOT touch the frozen releases, the registered outcomes, or this submission's manuscript. |
