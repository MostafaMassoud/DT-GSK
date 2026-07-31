# Stage 15 — Scientific writing, natural scholarly voice, and authorship-integrity audit

**Seat:** `s15_writing` (T5-WRITE lead, T6-INTEG on authorship integrity)
**Governing mandate:** `papers/PAPER_REVIEW_PROMPT.md` §15 (lines 2393–2514), ticket schema §5.4
(lines 1104–1148), DT-GSK profile §10 (lines 3160–3522), esp. §10.17.1–10.17.7.
**Date:** 2026-07-22 · **Mode:** read-only (no manuscript, code, or build file was modified)

**Package audited (verified against the repo, not from memory):**

| item | verified value | how verified |
|---|---|---|
| git HEAD | `45248eb31af7b01567c251f2a5da4f36e92d6030` | `git rev-parse HEAD` |
| main PDF | `papers/DT-GSK.pdf`, 39 pp | `fitz` page count / rendered footer `39 of 39` |
| supplement PDF | `papers/supplementary.pdf`, 61 pp | rendered footer `61 of 61` |
| cover letter | `papers/cover_letter.pdf`, 2 pp | rendered |
| DOCX build sources | `papers/main_pandoc.tex`, `papers/supplementary_pandoc.tex` | inspected for the same prose defects |
| evidence release | `rel-2026-07-20-67d9345f9` | `papers/analysis/rel-2026-07-20-67d9345f9/` present and read |

Surfaces read in full: `main.tex`, `sections/{introduction,related_work,proposed_algorithm,performance,conclusions}.tex`,
`cover_letter.tex`, structural + prose passes over `supplementary.tex`, plus `pdftotext -layout` extractions
of all three rendered PDFs and page-image renders where layout mattered.

---

## 0. Verdict for Gate N

**Gate N — Writing and Authorship Integrity: PASS WITH REQUIRED CORRECTIONS.**

The failure conditions of Gate N are: *language obscures science*, *formulaic text materially harms
credibility*, *claims become stronger during editing*, or *detector-evasion tactics are used*.

- Claims-strengthening: **not observed.** Every wording change I sampled against the R-01…R-14 diffs
  (`git diff abd2fa2f2~1 abd2fa2f2`, `git show 45248eb31`) preserved or narrowed scope.
- Detector-evasion: **not observed.** No homoglyphs, zero-width characters, synonym-spinning, or
  randomised variation. See §8.
- Formulaic text materially harming credibility: **not at the level of the canonical AI tells** — those
  are essentially absent (§2). The residual problem is different in kind and is described in §1.
- Language obscuring science: **one Major instance** — W15-01, in which the prose names an effect-size
  column that the referenced table does not contain and quotes four effect-size values with no printed
  source. That defect must be corrected before submission; it is a correction, not a gate failure of the
  whole writing layer.

Category score (§6.1) for *scientific writing and presentation*: **4 — strong**; minor non-blocking
weaknesses only, except W15-01 which is blocking-at-P1 and is a localized text↔exhibit repair.

---

## 1. Overall prose profile

This manuscript has clearly already been through a de-formulaic pass, and it worked. The canonical
machine-cadence markers §15.2 asks me to hunt are **at or near zero across the whole package**
(0 × *Moreover*, 0 × *Furthermore*, 0 × *Additionally*, 0 × *Notably*, 0 × *It is worth noting*,
0 × *delve*, 0 × *leverage*, 0 × *paves the way*, 0 × *sheds light*, 0 × *crucial/pivotal role*,
0 × *comprehensive*, 0 × *remarkable*). Sentence openings vary; transitions are earned by the argument
rather than bolted on; the technical density is real density, not padding. Under §10.17.1's explicit
warning that *"a false 'this is AI' flag on sound expert writing is itself a review error"*, I record
that finding first and without qualification.

What remains is a distinctive, self-consistent **authorial voice with four measurable tics**, none of
which is an AI tell and all of which a Q1/Q2 reviewer will notice:

1. **Defensive-compliance register.** The paper's dominant lexical field is governance, not science:
   *frozen* ×88, *disclosed* ×45, *bounded* ×18, *descriptive* ×29, *scoped* ×20, *never* ×35. Almost
   every affirmative sentence is immediately followed by a disclaiming clause. Individually each
   disclaimer is correct and should stay; collectively they read as a compliance document rather than
   an argument, and they dilute the force of the disclaimers that carry real information.
2. **Sentence over-packing.** Mean prose sentence length is 32–35 words with a long tail
   (`performance.tex` 46 sentences > 40 words, 19 > 55; `proposed_algorithm.tex` 39 > 40 words, 21 > 55;
   longest main-text sentence 106 words). 38 sentences across the package carry ≥ 2 semicolons, 13 carry
   ≥ 3. The typical construction is *clause — em-dashed parenthetical — clause; clause; clause*. Em-dash
   density is 178 in the five main-text section files and 87 in the supplement (0.47 per sentence in
   `performance.tex`).
3. **Transparency meta-commentary.** ~16 sentences announce the paper's own honesty rather than
   exercising it (*"The unfavorable case is discussed rather than skipped"*, *"One evidence gap is
   disclosed up front"*, *"labeled honestly"*, *"rather than hidden"*, *"rather than absorbed silently"*,
   *"reports its outcome transparently"* ×2 in a two-page cover letter). The disclosures they introduce
   are excellent; the announcements add no scientific content and read as protesting too much.
4. **Announce-scaffolds.** 18 instances of *"Two X matter/apply/define…"*, *"One provenance
   qualification applies/is…"*, *"Three contrasts matter here"* — the same rhetorical device reused as a
   paragraph opener across every section and the supplement.

Structural strengths worth recording: the argument is genuinely traceable (gap → mechanism → panel →
tier-resolved result → bounded conclusion); unfavourable cells are consistently stated *alongside*
favourable ones as §10.7's loss-visibility-parity control requires; hedging is calibrated rather than
inflated (no "state-of-the-art", no unqualified "robust" applied to the method, no causal language for
component effects); and the §15.3 authentic-reasoning test passes — the prose names actual functions,
dimensions, suites, thresholds, and comparators and could not be transplanted into another paper.

---

## 2. Recurring-pattern frequency table

Counts are over the LaTeX sources with `%` comments stripped (build annotations excluded), across
`main.tex`, the five section files, `supplementary.tex`, and `cover_letter.tex`.
Reproduce with the scratchpad scripts noted in §11.

### 2.1 Canonical AI-tell markers — the negative result

| pattern (§15.2 / §10.17.5 list) | occurrences |
|---|---|
| Moreover / Furthermore / Additionally / Notably / Importantly | **0** |
| It is worth noting / It is important to note / In conclusion | **0** |
| delve / leverage / seamless / holistic / intricate / myriad / realm / tapestry | **0** |
| plays a crucial (pivotal) role / paves the way / sheds light on | **0** |
| remarkably / considerably / comprehensive / cutting-edge / testament | **0** |
| "significant improvement" (unquantified) | **0** |
| paradigm shift / in today's world | **0** |
| "Overall," as a paragraph opener | **0** |

### 2.2 The patterns that *are* present

| pattern | intro | rel-work | method | results | concl | suppl | cover | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| em-dash `---` | 18 | 30 | 56 | 62 | 12 | 87 | 6 | **271** |
| sentences ≥ 2 semicolons | 3 | 1 | 8 | 12 | 1 | 10 | 0 | **35** |
| sentences ≥ 3 semicolons | 1 | 1 | 3 | 2 | 0 | 3 | 0 | **10** |
| sentences > 40 words | 7 | 16 | 39 | 46 | 6 | 92 | 3 | **209** |
| sentences > 55 words | 3 | 9 | 21 | 19 | 3 | 41 | 2 | **98** |
| "rather than" | 2 | 4 | 5 | 11 | 3 | 21 | 0 | **46** |
| contrastive ", not X" | 1 | 2 | 6 | 9 | 1 | 9 | 0 | **28** |
| *frozen* | 1 | 2 | 30 | 9 | 3 | 39 | 1 | **85** |
| *disclosed* | 2 | 0 | 2 | 4 | 0 | 35 | 0 | **43** |
| *descriptive* + noun | 0 | 0 | 0 | 8 | 1 | 2 | 1 | **12** |
| transparency meta-commentary | 0 | 0 | 2 | 5 | 1 | 4 | 4 | **~16** |
| announce-scaffold openers | 0 | 3 | 3 | 3 | 2 | 7 | 0 | **18** |

### 2.3 Restated-qualification frequency (the redundancy signal)

| qualification | main PDF | suppl | cover | note |
|---|---:|---:|---:|---|
| head-to-head triple `11--2--16 / 13--0--16 / 12--0--17` | 3 | 1 | 0 | §4.2.2, §4.6, Conclusions |
| 24-cell Holm tally (17 / 7 / 0) | 3 | 0 | 0 | §4.2.3, §4.6, Conclusions |
| "never Nemenyi-separable" | 3 | 1 | 0 | abstract, §4.2.3, Conclusions |
| CEC2011 eGSK loss `p_Holm = 4.2e-2` | 4 | 7 | 0 | |
| eGSK SLSQP-substitutes-fmincon | 5 | 5 | 0 | §3.7, §4.1, §4.7, Concl., S5.4 |
| "no runtime-superiority claim" | 3 | 2 | 0 | |
| APGSK per-run gap | 4 | 4 | 0 | + 16 identical supplement captions (§4) |
| panel-scope disclaimer | 6 | 3 | 2 | abstract, intro C3, §4 opener, §4.3, §4.4, §4.6, Concl. |
| A12 unit-of-analysis caveat | 3 | 0 | 0 | twice inside one paragraph (W15-01/W15-05) |

Legitimate repetition (abstract ↔ conclusions) is expected and is **not** counted as a defect; the
finding is the *third and fourth* restatement inside the body.

---

## 3. Terminology inconsistency list

### 3.1 The titular C1 mechanism is named nine ways (W15-02) — CONFIRMED

Non-overlapping, case-insensitive counts in the rendered main PDF:

| surface form | count | where |
|---|---:|---|
| "Deterministic Refinement" | 1 | **title** |
| "deterministic, budget-exact eigenframe refinement" | 1 | **abstract** |
| "the budget-exact refinement" | 1 | **abstract, contributions sentence** |
| "eigenframe final polish" | 13 | §3.5 heading + body |
| "eigenframe polish" | 10 | body, tables |
| "deterministic final polish" | 3 | §1, Conclusions |
| "compass endgame" | 3 | §1 C1, §3.5, Conclusions |
| "(deterministic) compass search" | 4 | §1 C1, §3.5 |
| "terminal polish" | 1 | §3.4 |

The title's second half — *Deterministic Refinement* — and the abstract's two "refinement" forms **never
recur anywhere in the body**, where the same object is the *eigenframe final polish*. A reader arriving
from the title cannot locate the named contribution by name. This is §15.2's "unnatural synonym
variation for the same technical concept" with a real navigational cost, not a stylistic preference.

### 3.2 The headline null is worded two different ways (W15-07) — CONFIRMED

| wording | main PDF | suppl | cover |
|---|---:|---:|---:|
| "no **detectable** standalone benefit" | 2 | 1 | 1 |
| "no **significant** standalone benefit" | 3 | 1 | 1 |

These are not synonyms in statistical writing: *no significant* names a test outcome at α; *no
detectable* is a capability statement. The two-page cover letter uses **both**, 2 paragraphs apart, for
the identical result. The manuscript elsewhere is scrupulous about this distinction (S6.6: *"This is a
failure to detect an effect under this design, not a demonstration that none exists"*), which makes the
drift more conspicuous, not less.

### 3.3 ISM role label

Abstract: "An **exploratory** interaction-structure memory". §3.4 heading, Conclusions, cover letter,
related work: "**supporting mechanism**". Introduction ¶ (line 135) uses both: "secondary **exploratory**
mechanism". Both labels are defensible and neither over-claims; pick one primary label and let the
other appear once as a gloss. **Advisory, not a defect.**

### 3.4 Non-findings (checked, no ticket)

- *panel* naming ("seven-algorithm GSK-family panel" / "GSK-family panel" / "family panel"): these are
  nested abbreviations of one term, correctly graded from full form to short form. **Not** an
  inconsistency.
- *ISM* naming: "interaction-structure memory" (34) / "ISM" (33) / bare "structure memory" (4) is a
  correct full-form → acronym → short-form pattern with the acronym defined in the abbreviations table.
  **Not** an inconsistency.
- "second comparison suite" (CEC2013) is used consistently; "corroborative" appears once as a role
  descriptor, not as a competing name. **Not** an inconsistency.

---

## 4. Paragraph-level coherence issues

**C-1 — Introduction, `sections/introduction.tex:135` (tonal seam + redundancy).** The ISM paragraph
that follows the C1–C3 bullet list shifts register: the surrounding introduction is concrete, active and
em-dash-driven with named mechanisms; this paragraph is abstract-noun-heavy and evaluative
("*is therefore positioned as*", "*Its inclusion provides a fully specified and reproducible
investigation of…*" — an inflated abstract noun where a direct verb is clearer, §15.2). It also
re-states, three lines after the bullets, the entire contribution list it just read ("*the paper's
principal contributions remain the dimension-tiered adaptive scaffold (C2), the eigenframe final polish
(C1), and the controlled, budget-fair evaluation framework (C3)*" — where "controlled, budget-fair
evaluation framework" is itself a *fourth* naming of C3, whose bullet reads "a controlled, reproducible
family evaluation"). Corroborating (not load-bearing) evidence that this block was inserted later: it is
the only paragraph in any section file that is a single unwrapped source line, and it was untouched by
the R-01…R-14 remediation.

**C-2 — `sections/performance.tex:196–231` (statistical protocol) — the same caveat stated twice in one
paragraph.** Lines 209–213 define the aligned effect size as the matched-pairs rank-biserial `r` with
its formula; lines 227–231 define it again, with the same formula and the same "A12 retained as the
descriptive companion" clause. Between them, lines 221–226 add a third statement of the A12
unit-of-analysis caveat, which §4.2.3 (lines 365–368) then states a fourth time. One paragraph, one
point, four statements.

**C-3 — subsection codas.** Three consecutive results subsections close on a near-identical
scope-limiting coda: §4.3 "*…and does not corroborate first place; no headline claim in this paper rests
on CEC2011 alone*" (l. 560); §4.4 "*…not as evidence of generalization beyond the suites tested*"
(l. 649); §4.6 "*…none of these findings is offered as evidence of field-wide superiority: every
comparative claim in this paper is bounded to…*" (l. 872). The section already opens with the same
disclaimer (l. 16). This is §15.2's "conclusion-like summaries repeated at the end of every subsection".
The remedy is **consolidation, never deletion** — the scope bound must remain stated in the abstract,
§4.1, and the Conclusions.

**C-4 — cover letter ¶1 (255 words, 7 sentences, longest 73 words) and ¶2 (100 words, 2 sentences,
longest 75 words).** ¶1 carries the headline number, all three contributions, and the supporting
mechanism with its null. ¶2 then restates the ISM null in near-identical terms, using "transparently"
for the second time. An editor reads a cover letter in under a minute; this one asks for a re-read.

**C-5 — `supplementary.tex:1173–1177` self-description is inaccurate.** S5.4 opens: *"The wording is the
wording of the conclusions in the submitted manuscript — moved rather than rewritten, so that nothing is
softened in transit."* The printed Conclusions say "**Eleven** limitations bound these findings … In
outline:"; S5.4 says "**Several** limitations bound these findings. First… Eighth…". The two texts are
demonstrably not the same wording. The *provenance* claim (moved from an earlier draft) may be true; the
sentence as printed asserts identity with the current Conclusions and is false on inspection.

---

## 5. Review tickets (§5.4 schema)

---

```text
ticket_id: W15-01
review_stage: 15 (Scientific writing / evidence-citation integrity)
reviewer_role: RW (T5-WRITE), cross-referred to T3-STAT and T5-WRITE-exhibits
severity: Major
priority: P1
confidence: Confirmed
issue_type: writing (text-to-exhibit referent; also exhibit/statistics)
manuscript_location: papers/sections/performance.tex:362, :365-368, :409, :426 and :221-226
  (rendered: DT-GSK.pdf p.1401, p.1516-1519, p.1574, p.1581 of pdftotext extraction;
  DOCX source papers/main_pandoc.tex:2105, :2248)
claim_id_or_artifact_id: TAB-T15 / tab:wilcoxon-holm (Table 14 in the rendered PDF); RS-08
concise_issue: The prose describes, interprets, and quotes numbers from an "A12 column" of
  Table 14 that Table 14 does not contain; the table prints matched-pairs rank-biserial r.
  The statistical-protocol paragraph additionally contradicts itself about which quantity is
  "the tabulated" effect size, and the four A12 values quoted in the text appear nowhere in
  the paper, the supplement, or the released Wilcoxon/effect-size CSVs.
exact_evidence_or_observation:
  - papers/tables/T15.tex header row: "& $p$ & $p_{\mathrm{Holm}}$ & $+$ & $\approx$ & $-$ &
    $r$ & Dec." -- seven columns, effect size is r. Rendered Table 14 confirms (r values
    +0.865, -0.140, ..., -0.057). There is NO A12 column.
  - Caption (performance.tex:381-383) is CORRECT: "the matched-pairs rank-biserial effect
    size $r$ ($> 0$ favors \dtgsk{})".
  - performance.tex:362 (prose): "Table~\ref{tab:wilcoxon-holm} reports the across-function
    Wilcoxon tests with Holm correction, win/tie/loss counts, $A_{12}$ effect sizes, and Holm
    decisions..."
  - performance.tex:365: "The $A_{12}$ column is computed over the 29 per-function means..."
  - performance.tex:221: "The tabulated $A_{12}$ is computed over the 29 per-function mean
    errors..." -- while performance.tex:211-213 in the SAME paragraph says "the tabulated
    effect size is the matched-pairs rank-biserial correlation $r$".
  - performance.tex:409: "with $A_{12}$ of 0.490, 0.505, and 0.472"; :426: "($A_{12} =
    0.712$)". Neither value is printed in any exhibit of either document (grep of the
    rendered supplement for 0.490/0.505/0.472/0.712: 0 hits).
  - Released artifacts: papers/analysis/rel-2026-07-20-67d9345f9/cec2017/
    wilcoxon_holm_cec2017_D*.csv columns = (...,outcome,availability,rank_biserial,w_plus,
    w_minus,n_zero,direction) -- no a12 column at all.
    effect_sizes_cec2017_D*.csv columns = (...,n_runs,a12,cliffs_delta,magnitude,...) but
    these are PER-FUNCTION RUN-LEVEL rows (n_runs=51), i.e. the workbook the text explicitly
    says is a DIFFERENT quantity.
  - I independently recomputed the across-function A12 over the 29 per-function means from
    descriptive_stats_cec2017_D{30,50,100}.csv: eGSK 0.49049 / 0.50535 / 0.47206 and APGSK
    D100 0.71225. The NUMBERS ARE CORRECT; only their stated location is wrong.
root_cause: Residual prose from the M-027 migration that replaced the tabulated A12 with the
  matched-pairs rank-biserial r. The table generator and the caption were updated; three
  prose passages (and the two value-quoting sentences) were not.
scientific_or_editorial_justification: PAPER_REVIEW_PROMPT.md Sec.15.3 ("cites the correct
  evidence"), Sec.15.1 ("consistent technical terminology", "readable equation and figure
  integration"), and the Sec.5.5 calibration example for a defect that "misdirects the reader
  to a non-existent or wrong referent" (rated Major there).
impact_on_validity_or_acceptance: No reported inference changes -- the Holm decisions, ranks
  and the recomputed A12 values are all correct. But a reviewer who follows the text to
  Table 14 to check "A12 = 0.490" will not find it, will find a differently-signed statistic
  (r = -0.286) in its place, and will reasonably conclude the effect-size reporting is not
  under control. It also leaves four printed numbers with no visible source, which is exactly
  what Sec.10.11 (source binding) exists to prevent.
required_correction:
  (a) performance.tex:362 -- "..., win/tie/loss counts, matched-pairs rank-biserial effect
      sizes $r$, and Holm decisions...".
  (b) performance.tex:365-368 -- retarget the caveat to the column that exists, e.g.
      "The tabulated effect size is the matched-pairs rank-biserial correlation $r$, aligned
      with the paired across-function Wilcoxon; it is distinct from the per-function
      run-level Vargha--Delaney $A_{12}$ in the released effect-size workbook, and the two
      are not interchangeable."
  (c) performance.tex:221-226 -- delete the "The tabulated $A_{12}$..." sentence (it
      contradicts :211-213) and fold its one unique fact (which unit the quoted A12 values
      use) into the sentence introducing those values.
  (d) performance.tex:409 and :426 -- either name the source explicitly, e.g. "with
      across-function $A_{12}$ (computed over the 29 per-function means, released with the
      analysis bundle) of 0.490, 0.505, and 0.472", or report the tabulated $r$ instead
      (-0.286, -0.002, -0.057 at D=30/50/100; APGSK D100 r = +0.977) and drop A12 here.
      Choice (d) is an AUTHOR decision because it changes which statistic carries the
      sentence's interpretation -- it is NOT a style-only edit and I do not prescribe it.
acceptable_alternatives: Add the across-function A12 as an extra column of T15 (regenerated,
  not hand-entered) so the text's referent exists; or emit an across-function effect-size CSV
  into the analysis bundle and cite it. Both require a generator change, not a prose edit.
additional_evidence_needed: Author confirmation of which effect size should carry the
  §4.2.3 interpretation sentences. Nothing else -- values are verified.
dependencies: T3-STAT (which effect size is the frozen plan's primary), T5-WRITE-exhibits
  (whether T15 is regenerated).
expected_improvement: Every printed effect size resolves to a visible, released source; the
  statistical-protocol paragraph stops contradicting itself.
post_revision_verification: (1) grep the rebuilt PDF and DOCX for "A_{12} column" / "tabulated
  A12" -> 0 hits; (2) every effect-size number in §4.2.3 traces to either a T15 cell or a
  named released CSV; (3) re-run validate_evidence_bindings.py and the cross-format parity
  check.
status: open
```

---

```text
ticket_id: W15-02
review_stage: 15
reviewer_role: RW (T5-WRITE)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: writing (terminology consistency)
manuscript_location: main.tex:90-91 (title), :135 and :148 (abstract); sections/
  proposed_algorithm.tex:565 (§3.5 heading) and passim; sections/introduction.tex:87;
  sections/conclusions.tex:17, :23; cover_letter.tex:43, :55, :57
claim_id_or_artifact_id: MT-09 / contribution C1
concise_issue: The titular C1 mechanism is referred to by nine distinct surface names, and the
  two names used in the TITLE and ABSTRACT never appear anywhere in the body.
exact_evidence_or_observation: Non-overlapping case-insensitive counts in the rendered main
  PDF: "Deterministic Refinement" 1 (title only); "deterministic, budget-exact eigenframe
  refinement" 1 (abstract only); "budget-exact refinement" 1 (abstract only); "eigenframe
  final polish" 13; "eigenframe polish" 10; "deterministic final polish" 3; "compass
  endgame" 3; "(deterministic) compass search" 4; "terminal polish" 1. Section 3.5 is headed
  "Eigenframe Final Polish (Contribution C1)"; the string "refinement" as a name for it does
  not occur in §3.
root_cause: Successive retitles and contribution restructures ("Deterministic Refinement" in
  the title, "eigenframe final polish" in the frozen method text) were never reconciled into
  one canonical term.
scientific_or_editorial_justification: Sec.15.1 (consistent technical terminology),
  Sec.15.2 (unnatural synonym variation for the same technical concept), Sec.10.17.6
  (notation/terminology consistent across prose, pseudocode, equations and exhibits).
impact_on_validity_or_acceptance: A reader who comes for "Deterministic Refinement" cannot
  find a section, equation, or table with that name. Reviewers routinely read this as a sign
  that the paper was assembled rather than written.
required_correction: Adopt ONE canonical name -- the frozen method text's "eigenframe final
  polish" is the natural choice -- and bind the title/abstract to it once. Concretely:
  (i) abstract main.tex:134-135 "a deterministic, budget-exact eigenframe final polish"
      (adds one word, changes no claim);
  (ii) abstract contributions main.tex:148 "the budget-exact eigenframe final polish";
  (iii) keep the short forms "eigenframe polish" and "the polish" as deliberate second
      references, and RETIRE "terminal polish" (1 use) and "deterministic final polish"
      (3 uses) in favour of the canonical form;
  (iv) keep "compass search / compass endgame" ONLY where the sentence is genuinely about
      the search's *type* (§3.5's direct-search framing, §1 C1's isolation-scope clause) --
      those uses are legitimate and should not be flattened.
  The title itself may stay as it is: "Deterministic Refinement" is a defensible
  title-register generalisation PROVIDED the abstract makes the binding explicit.
acceptable_alternatives: Rename §3.5 to "Deterministic Eigenframe Refinement (Final Polish)"
  and make "final polish" the short form everywhere. Either direction is acceptable; mixing
  is not.
additional_evidence_needed: none
dependencies: none (style-only under Sec.15.4: no number, equation, claim, or scope changes)
expected_improvement: Title -> abstract -> §3.5 -> Table 3 -> Conclusions read as one term.
post_revision_verification: Re-run the non-overlapping name tally on the rebuilt PDF; expect
  at most three surface forms (canonical, short, and the "compass search" type-descriptor).
status: open
```

---

```text
ticket_id: W15-03
review_stage: 15
reviewer_role: RW (T5-WRITE)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: writing (sentence over-packing; incomplete closure of remediation R-13)
manuscript_location: package-wide; worst instances at sections/related_work.tex:284-297
  (106 words), sections/proposed_algorithm.tex:740-750 (104 words), sections/
  introduction.tex:26-32 (96 words), sections/proposed_algorithm.tex:482-489 (80 words),
  sections/performance.tex:429-437 (79 words), sections/introduction.tex:101-112 (C2 bullet,
  4 semicolons)
claim_id_or_artifact_id: R-13 (post-review remediation, closed 2026-07-21)
concise_issue: R-13 ("sentence de-packing") was applied to exactly two paragraphs; the same
  defect remains widespread and untouched everywhere else. This is an INCOMPLETE closure of
  an already-accepted ticket, not a new objection.
exact_evidence_or_observation:
  - `git diff abd2fa2f2~1 abd2fa2f2 -- papers/sections/` shows the de-packing edits touched
    only (a) the Conclusions limitations outline (semicolon chain -> sentences) and (b) two
    sentences of the introduction C3 bullet. Nothing else.
  - Post-remediation measurements (comments stripped, floats/equations removed):
    performance.tex mean 34.7 w/sentence, 46 sentences > 40 w, 19 > 55 w;
    proposed_algorithm.tex mean 31.9, 39 > 40 w, 21 > 55 w;
    related_work.tex mean 35.4, 16 > 40 w, 9 > 55 w;
    supplementary.tex mean 34.6, 92 > 40 w, 41 > 55 w.
    38 sentences package-wide carry >= 2 semicolons; 13 carry >= 3.
  - The C2 bullet that R-13 edited (introduction.tex:101) still contains four
    semicolon-separated mechanism clauses in one sentence; the edit fixed only a duplicated
    word ("credit credit-based") in it.
root_cause: R-13 was scoped to the two paragraphs the prior review named rather than to the
  pattern it exemplified.
scientific_or_editorial_justification: Sec.15.1 (sentence-length and syntactic variety driven
  by meaning; economy without loss of necessary detail), Sec.10.17.5 (require varied,
  purposeful sentence structure). Note the counter-control: information density is NOT the
  defect and must not be reduced.
impact_on_validity_or_acceptance: Reviewer fatigue and re-reading; in the worst cases
  (related_work.tex:284-297, proposed_algorithm.tex:740-750) a single sentence carries three
  independent factual assertions with three citations, so a reader cannot tell which citation
  supports which clause without re-parsing.
required_correction: Split the ~20 sentences over 55 words in the five main-text section
  files at their existing semicolon and em-dash boundaries. No content may be removed. Worked
  examples are given in §6 below (R-05 ... R-12).
acceptable_alternatives: Convert the two longest enumerative sentences (related_work.tex:284,
  proposed_algorithm.tex:184-202) into short displayed lists, which the MDPI class supports
  and the GSK exemplar uses.
additional_evidence_needed: none
dependencies: style-only (Sec.15.4): no numerical value, equation, claim scope, citation,
  method behaviour, or limitation may change. Every split below is verified to preserve these.
expected_improvement: Mean sentence length in the main-text sections falls toward the 24-28
  word band typical of accepted Algorithms articles, with the > 55-word tail eliminated.
post_revision_verification: Re-run the sentence-length scan; target 0 sentences > 55 words
  and <= 5 sentences with >= 2 semicolons in the five main-text section files. Then diff the
  claim set: every numeral, citation key, and scope word present before must be present after.
status: open
```

---

```text
ticket_id: W15-04
review_stage: 15
reviewer_role: RW (T5-WRITE), RI (T6-INTEG)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: writing (self-referential virtue commentary; hollow prose)
manuscript_location: sections/performance.tex:124, :126, :405, :678;
  sections/proposed_algorithm.tex:263, :788; sections/conclusions.tex:34;
  supplementary.tex:1162, :1175-1176, :1160, :2133; cover_letter.tex:55 (x2), :57 (x2)
claim_id_or_artifact_id: n/a (voice)
concise_issue: ~16 sentences announce the manuscript's own honesty instead of exercising it.
  The disclosures they introduce are substantive and must stay; the announcements carry no
  scientific content.
exact_evidence_or_observation: Verbatim instances --
  performance.tex:124 "...the exception is recorded in the protocol exhibit and the pairing
    audit rather than hidden."
  performance.tex:126 "One evidence gap is disclosed up front."
  performance.tex:405 "The unfavorable and borderline cells are stated plainly."
  performance.tex:678 "The unfavorable case is discussed rather than skipped."
  proposed_algorithm.tex:263 "Its five sub-mechanisms are labeled honestly: ..."
  conclusions.tex:34 "...and the unfavorable cells are stated with the favorable ones."
  supplementary.tex:1162 "...rather than absorbed silently."
  supplementary.tex:1175 "...moved rather than rewritten, so that nothing is softened in
    transit."
  supplementary.tex:2133 "...are recorded here for provenance."
  cover_letter.tex:55 "...its direct isolation is reported transparently as a controlled
    negative result..."
  cover_letter.tex:57 "...and reports its outcome transparently: ..." (second use of
    "transparently" in a 2-page letter)
  cover_letter.tex:55 "...presented as an honestly labeled modified/original composite..."
root_cause: An honesty-first drafting policy that surfaced in the prose as narration of the
  policy rather than as its product.
scientific_or_editorial_justification: Sec.15.2 ("polished but empty prose that provides no
  evidence or reasoning"; "generic statements that could appear unchanged in any paper"),
  Sec.10.17.5 ("cut hollow phrasing", "throat-clearing preambles").
impact_on_validity_or_acceptance: Referees read repeated self-certification as defensiveness
  and start looking for what is being defended. The paper's actual disclosure record is
  excellent and speaks for itself; the narration weakens it.
required_correction: Delete the meta-clause; keep every disclosure sentence that follows it,
  unchanged. Worked before/after pairs in §6 (R-13 ... R-17). This is a strict deletion of
  self-assessment: no fact, number, limitation, or disclosure is removed anywhere.
acceptable_alternatives: Retain ONE such framing sentence at the head of §4.1
  ("Evidence discipline") where it functions as a genuine methodological statement.
additional_evidence_needed: none
dependencies: MUST be executed as deletion-of-framing only. Any edit that also removes the
  following disclosure violates Sec.2.1 / Sec.15.4 and must be rejected.
expected_improvement: The disclosures land harder; the voice reads as confident rather than
  anxious.
post_revision_verification: Re-run the meta-commentary scan (§11) -> <= 2 hits package-wide;
  then verify that the count of DISCLOSED items (APGSK gap, self-init exception, eGSK port,
  F26 adverse case, mixed-session runtime, 11 limitations) is unchanged.
status: open
```

---

```text
ticket_id: W15-05
review_stage: 15
reviewer_role: RW (T5-WRITE)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: writing (near-duplicate content / repeated codas)
manuscript_location: sections/performance.tex:209-231 (intra-paragraph duplication);
  sections/performance.tex:16, :560, :649, :872 (scope codas);
  sections/performance.tex:362-368 vs :221-226 (third statement of the A12 caveat);
  sections/performance.tex:319-323 vs :843-846 vs sections/conclusions.tex:46-50
  (head-to-head triple stated three times)
claim_id_or_artifact_id: RS-01 NARROWED, RS-08, LM-03
concise_issue: Several qualifications are restated three or four times in the body beyond the
  legitimate abstract/conclusions pair, including one point stated twice inside a single
  paragraph.
exact_evidence_or_observation:
  - performance.tex:209-213 "Every test is accompanied by its \emph{aligned} effect size:
    because the across-function test is a matched-pairs Wilcoxon, the tabulated effect size
    is the matched-pairs rank-biserial correlation $r = (R^{+} - R^{-})/(R^{+} + R^{-})$,
    with $r > 0$ favoring \dtgsk{}."
    vs performance.tex:227-231 "Because the Wilcoxon test is \emph{paired} by function, its
    aligned effect size --- the matched-pairs rank-biserial correlation
    $r = (R^{+} - R^{-})/(R^{+} + R^{-})$ --- is reported alongside $R^{+}/R^{-}$ ... with
    $A_{12}$ retained as the descriptive distributional summary."
    Same definition, same formula, same companion clause, 18 lines apart, one paragraph.
  - Scope disclaimer appears at abstract (main.tex:152), intro C3 (introduction.tex:125),
    §4 opener (performance.tex:16), §4.3 close (:560), §4.4 close (:649), §4.6 close (:872),
    and Conclusions (conclusions.tex:32, :71): 8 sites.
  - Head-to-head triple 11--2--16 / 13--0--16 / 12--0--17 appears at performance.tex:320-322,
    performance.tex:844, conclusions.tex:47, and once more in the supplement.
root_cause: Independent per-section drafting against the same claim rows, each section made
  self-contained.
scientific_or_editorial_justification: Sec.15.2 (conclusion-like summaries repeated at the
  end of every subsection), Sec.10.17.5 ("Remove near-duplicate content ... consolidate to
  one clear statement").
impact_on_validity_or_acceptance: Contributes materially to the page budget and to the
  defensive register; a reviewer counting restatements of the same caveat questions whether
  the paper trusts its own disclosure.
required_correction:
  (a) performance.tex:221-231 -- collapse the three effect-size statements into one (see
      W15-01(c) and §6 R-03; the two tickets share this edit).
  (b) Keep the scope disclaimer at: abstract, §4.1 (setup), and Conclusions. Delete the
      subsection-closing repeats at :560, :649, :872 ONLY where the identical bound is
      already stated in §4.1 -- verify sentence by sentence; §4.3's "does not corroborate
      first place" carries UNIQUE information (which suite supports which claim) and MUST be
      kept.
  (c) Keep the head-to-head triple at its first full statement (§4.2.2) and in the
      Conclusions; in §4.6 replace the repeated numerals with a back-reference.
acceptable_alternatives: none needed.
additional_evidence_needed: none
dependencies: This ticket has a HARD constraint: no scope bound, limitation, or unfavourable
  cell may disappear. Any consolidation that removes the last statement of a bound is a
  Sec.2.1 violation and must be reverted.
expected_improvement: ~15-25 lines recovered against the page limit and a measurably less
  repetitive results section, with every bound still stated.
post_revision_verification: Re-run the restated-qualification tally (§2.3); confirm each row
  still has >= 1 main-text occurrence and >= 1 occurrence in either abstract or conclusions.
status: open
```

---

```text
ticket_id: W15-06
review_stage: 15
reviewer_role: RW (T5-WRITE)
severity: Minor
priority: P2
confidence: Confirmed
issue_type: writing (terminology / claim-wording consistency)
manuscript_location: main.tex:146 (abstract, "no DETECTABLE") and main.tex:198
  (\supplementary{} block, "no SIGNIFICANT") -- BOTH forms in one file;
  sections/conclusions.tex:89-90 ("no detectable standalone benefit"), :98-99 ("no detectable
  standalone improvement"); sections/proposed_algorithm.tex:271 ("no significant");
  sections/performance.tex:827 ("no significant"); cover_letter.tex:55 ("no significant") and
  :57 ("no detectable") -- BOTH forms in a two-page letter; supplementary.tex:2032
  ("no significant standalone benefit"), :2116 ("no standalone benefit is detected")
claim_id_or_artifact_id: X-ABL-02 (S6.5 isolation null)
concise_issue: The same headline null is worded "no DETECTABLE standalone benefit" in three
  places and "no SIGNIFICANT standalone benefit" in five. Both forms occur inside main.tex
  itself (abstract vs supplementary-materials description) and inside the two-page cover
  letter.
exact_evidence_or_observation: Rendered-PDF counts -- main: detectable 2 / significant 3;
  supplement: significant 1 + "no detectable benefit" 1; cover letter: detectable 1 /
  significant 1. Source grep for "standalone benefit|standalone improvement" over all .tex
  returns the eight sites listed above. The supplement itself draws the distinction
  explicitly (S6.6: "This is a failure to detect an effect under this design, not a
  demonstration that none exists"), which is why the drift is conspicuous.
root_cause: Two drafting passes over the same claim row, neither harmonised.
scientific_or_editorial_justification: Sec.15.1 (consistent technical terminology), Sec.4.6
  (do not treat failure to reject as proof of equivalence -- the looser "detectable" is the
  form that drifts toward that reading).
impact_on_validity_or_acceptance: Low individually; but a statistics-literate reviewer who
  sees both forms for one result will check whether the paper knows the difference.
required_correction: Choose ONE form and apply it everywhere. The defensible choice is the
  test-outcome form: "no statistically significant standalone benefit was detected at the
  memory's active tiers", which is simultaneously the accurate test statement and the
  accurate capability statement, and matches S6.6's own careful sentence.
acceptable_alternatives: Keep "no detectable standalone benefit" everywhere PROVIDED the
  first occurrence in each document defines it as "not significant under the prespecified
  Holm-corrected paired test".
additional_evidence_needed: none
dependencies: Coordinate with the seat auditing §10.9 wording so the abstract sentence is
  changed once, not twice.
expected_improvement: One wording for one result across abstract, method, results,
  conclusions, supplement and cover letter.
post_revision_verification: grep both forms across the rebuilt PDF, DOCX and cover letter;
  expect a single form.
status: open
```

---

```text
ticket_id: W15-07
review_stage: 15
reviewer_role: RW (T5-WRITE)
severity: Minor
priority: P2
confidence: Confirmed
issue_type: writing / exhibit (repeated caption boilerplate)
manuscript_location: papers/supplementary.tex, Section S3 figure captions (49 captions
  scanned); rendered supplementary.pdf pp. 20-44
claim_id_or_artifact_id: FIG-CONV-SUPP-* ; [APGSK-GAP] caption token
concise_issue: One identical sentence is appended to 16 supplement captions, another to 4,
  another to 3, and a fourth appears in TWO different wordings for the same fact.
exact_evidence_or_observation: Caption-sentence tally over supplementary.tex --
  16 x "\apgsk{} checkpoint evidence at this dimension derives from per-generation logs
       (disclosed limitation)."
   7 x "All panels carry 7/7 series."
   4 x "All panels carry the full 7/7 series."   <-- same fact, two wordings
   4 x "Two-algorithm detail behind the family-panel exhibits --- no panel-wide claim."
   3 x "Suite-level outcome context: \dtgsk{} significantly loses to \egsk{} across problems
       on this suite (Holm-corrected $p = 4.2 \times 10^{-2}$)."
root_cause: Caption generation appends a fixed qualification string per figure class.
scientific_or_editorial_justification: Sec.10.17.4 ("mechanically repeated provenance stamps
  ... No human author stamps thirty captions with an identical build tag"), Sec.10.17.5
  ("flag boilerplate repeated across captions"), Sec.15.2 (unnatural synonym variation).
impact_on_validity_or_acceptance: The repetition reads unmistakably as generated output, and
  the 7/7-series wording split is a visible inconsistency across adjacent pages.
required_correction:
  (a) Harmonise "All panels carry 7/7 series." / "All panels carry the full 7/7 series." to a
      single wording (pure editorial, zero claim change).
  (b) Move the 16-times-repeated APGSK qualification into ONE conventions paragraph at the
      head of Section S3 ("Throughout this section, APGSK checkpoint curves derive from
      per-generation logs; see Section S5.4"), and either delete it from the individual
      captions or reduce it to a short parenthetical marker.
  (c) Same treatment for the 4x "Two-algorithm detail..." string.
  (d) The 3x CEC2011 eGSK-loss sentence MUST be retained wherever it qualifies a figure that
      could otherwise be read as favourable (Sec.10.7 loss-visibility parity). Do not
      consolidate this one away; harmonise its wording only.
acceptable_alternatives: Keep the per-caption stamps but shorten each to <= 8 words.
additional_evidence_needed: none
dependencies: Caption generator (papers/scripts/generate_full_convergence.py and siblings) --
  this is a generator edit, not a hand edit of the .tex, per Sec.10.11 (no hand-edited
  exhibit content).
expected_improvement: Section S3 stops reading as machine output; the APGSK limitation is
  stated once, prominently, instead of 16 times invisibly.
post_revision_verification: Re-run the caption-boilerplate tally on the rebuilt supplement;
  no non-trivial sentence should repeat more than twice, and the APGSK qualification must
  still be discoverable from Section S3's opening paragraph.
status: open
```

---

```text
ticket_id: W15-08
review_stage: 15
reviewer_role: RW (T5-WRITE), RI (T6-INTEG)
severity: Minor
priority: P2
confidence: Confirmed
issue_type: writing (inaccurate self-description)
manuscript_location: papers/supplementary.tex:1173-1177 (rendered supplementary.pdf S5.4,
  p.48) vs papers/sections/conclusions.tex:65-81 (rendered DT-GSK.pdf §5)
claim_id_or_artifact_id: N-020 (limitations relocation)
concise_issue: S5.4 asserts that its limitations text is verbatim the Conclusions' wording,
  "moved rather than rewritten". The two printed texts are demonstrably different.
exact_evidence_or_observation:
  supplementary.tex:1174-1176 "The wording is the wording of the conclusions in the submitted
    manuscript --- moved rather than rewritten, so that nothing is softened in transit."
  conclusions.tex:66 "Eleven limitations bound these findings, stated in full with their
    numeric evidence in the Supplementary Material, Section~S5. In outline: ..."
  supplementary.tex:1180 "Several limitations bound these findings. First, ..."
  The Conclusions paragraph is a compressed outline; S5.4 is a differently-worded full
  statement. They are not the same text. (The eleven-item count IS reconcilable -- seven
  singles + three attribution gaps + statistical scope -- but a reader counting the printed
  ordinals in S5.4 finds "First...Eighth" plus "Beyond these", i.e. nine blocks, and must
  decompose the eighth to reach eleven.)
root_cause: The provenance sentence was written when the limitations were first relocated and
  was not updated when the Conclusions were rewritten into an outline (R-13 touched exactly
  this paragraph on 2026-07-21 without revisiting the supplement's claim about it).
scientific_or_editorial_justification: Sec.15.3 (a passage must cite the correct evidence,
  including about itself); Sec.2.1 honesty controls apply to the manuscript's statements about
  its own construction as much as to its results.
impact_on_validity_or_acceptance: Small but corrosive: it is the one sentence in the package
  a reviewer can falsify in ten seconds, and it is a sentence about the paper's own integrity.
required_correction: Replace with an accurate provenance statement that makes the same
  guarantee without asserting textual identity, e.g.: "The Conclusions state these limitations
  in outline; this section gives each in full with its numeric evidence. Nothing is narrowed
  in the move: every bound asserted in the Conclusions is restated here with its supporting
  values." (Facts preserved; the no-softening guarantee is preserved and is now checkable.)
  Consider also aligning the opener to the Conclusions' count: "Eleven limitations bound
  these findings." -- this is verifiable and removes the "Several"/"Eleven" mismatch.
acceptable_alternatives: Make S5.4 literally verbatim-consistent by numbering it 1-11.
additional_evidence_needed: none
dependencies: Coordinate with whichever seat owns LM-01..LM-05 wording so the count is set
  once.
expected_improvement: The self-description becomes true and the eleven-limitation count
  becomes countable in both documents.
post_revision_verification: Diff the Conclusions outline against S5.4 item by item; confirm
  11 bounds in both and that no bound is weaker in either.
status: open
```

---

```text
ticket_id: W15-09
review_stage: 15
reviewer_role: RW (T5-WRITE)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: writing (tonal seam, redundancy, inflated abstract nouns)
manuscript_location: sections/introduction.tex:135 (rendered DT-GSK.pdf p.4, the paragraph
  immediately after the C1-C3 bullets)
claim_id_or_artifact_id: MT-08, X-ABL-02
concise_issue: A register seam: this paragraph reads in a different, more abstract voice than
  the introduction around it, restates the contribution list three lines after the bullets,
  and introduces a FOURTH naming of C3.
exact_evidence_or_observation: Printed text -- "...ISM is therefore positioned as a secondary
  exploratory mechanism rather than as the primary source of \dtgsk{}'s performance standing.
  Its inclusion provides a fully specified and reproducible investigation of structure
  learning from strictly improving accepted moves, while the paper's principal contributions
  remain the dimension-tiered adaptive scaffold (C2), the eigenframe final polish (C1), and
  the controlled, budget-fair evaluation framework (C3)."
  - "Its inclusion provides ... an investigation" is an inflated abstract-noun construction
    for "we investigate" (Sec.15.2).
  - "is therefore positioned as" is an agentless framing verb in a section that is otherwise
    active and concrete.
  - The C1/C2/C3 list is repeated 3 lines after the bullet list states it.
  - C3 is called "the controlled, budget-fair evaluation framework" here; its own bullet
    (introduction.tex:113) calls it "a controlled, reproducible family evaluation"; the
    abstract calls it "a reproducible within-family evaluation"; the cover letter calls it
    "the evaluation-integrity infrastructure". Four names for one contribution.
  - Corroborating (not load-bearing): it is the only paragraph in any section file written as
    a single unwrapped source line, and it was not touched by R-01..R-14.
root_cause: Later insertion to demote ISM after the contribution restructure, drafted
  independently of the surrounding paragraphs.
scientific_or_editorial_justification: Sec.10.17.5 ("Read for a single human voice. Flag
  tonal seams where the register shifts between paragraphs ... a symptom of stitched-together
  generation"), Sec.15.2 (inflated abstract nouns; excessive self-reference).
impact_on_validity_or_acceptance: The introduction's last substantive paragraph is its
  weakest, immediately before the roadmap. It also blunts the ISM demotion, which is one of
  the paper's genuinely strong honesty moves.
required_correction: Rewrite in the surrounding register, keeping every fact and both
  supplement pointers. Suggested revision in §6 (R-01). Also settle on ONE name for C3.
acceptable_alternatives: Fold the paragraph's first two sentences into the C1 bullet (where
  ISM is already introduced as the polish's basis) and keep only the demotion sentence here.
additional_evidence_needed: none (the S6.5/S6.6 pointers and both stated findings were
  verified against the rendered supplement, pp. 58-60)
dependencies: style-only; must preserve the two supplement cross-references, the "no
  consistent standalone performance contribution" scope, and the "no systematic advantage on
  the hybrid or composition categories" scope exactly.
expected_improvement: One voice through §1; the ISM demotion reads as a considered judgement
  rather than a disclaimer.
post_revision_verification: Read §1 aloud end-to-end; the paragraph should not be identifiable
  as an insertion. Confirm S6.5 and S6.6 pointers and both null scopes survive verbatim.
status: open
```

---

```text
ticket_id: W15-10
review_stage: 15
reviewer_role: RW (T5-WRITE)
severity: Minor
priority: P2
confidence: Confirmed
issue_type: writing (cover letter: misplaced hedge, over-packing, duplication)
manuscript_location: papers/cover_letter.tex:55, :57 (rendered cover_letter.pdf p.1)
claim_id_or_artifact_id: CL-02, RS-01 NARROWED
concise_issue: The letter opens by hedging a computed fact with "To our knowledge", packs 255
  words into one paragraph, and states the ISM null twice using "transparently" both times.
exact_evidence_or_observation:
  - cover_letter.tex:55 "To our knowledge, \dtgsk{} attains the best overall CEC2017 Friedman
    mean rank on the seven-algorithm GSK-family panel (2.48, ...)". The rank is a value the
    authors computed from their own frozen evidence; "to our knowledge" hedges either nothing
    or an implicit and unsupported priority claim over the literature.
  - Paragraph 1 = 255 words / 7 sentences, longest sentence 73 words (the "Second, ..."
    contribution sentence with a nested em-dash list of four mechanisms).
  - Paragraph 2 = 100 words / 2 sentences, longest 75 words, and restates the ISM null already
    given in paragraph 1: ":55 ...its direct isolation is reported transparently as a
    controlled negative result (no significant standalone benefit at its active tiers)" vs
    ":57 ...reports its outcome transparently: the isolation finds no detectable standalone
    benefit from the memory at its active tiers".
root_cause: Two drafting passes over one letter; the hedge is a habit imported from novelty
  statements, where it belongs.
scientific_or_editorial_justification: Sec.15.1 (calibrated hedging), Sec.4.6 (do not
  generalize beyond tested comparators -- "to our knowledge" invites exactly that reading),
  Sec.10.17.5 (remove near-duplicate content; cut hollow phrasing).
impact_on_validity_or_acceptance: An editor's first sentence of substance should be a
  bounded, checkable claim. As written it is a hedged claim that could be read as a
  literature-priority assertion the paper does not make anywhere else.
required_correction:
  (a) Replace the hedge with the paper's own scope, NOT with a bare assertion (deleting the
      hedge alone would strengthen the claim, which Gate N forbids):
      "In the seven-algorithm GSK-family panel evaluated here, DT-GSK attains the best overall
       CEC2017 Friedman mean rank (2.48, the unweighted mean of the four per-dimension ranks
       --- a descriptive aggregate; eGSK is second at 2.96), under a release-locked protocol,
       with byte-stable determinism for DT-GSK in the declared supported environment."
      Verified: 2.48 and 2.96 match main.tex:140-141 and conclusions.tex:36-38; the
      byte-stability narrowing to DT-GSK (R-09) is preserved verbatim.
  (b) Split paragraph 1 after "The paper makes three contributions." and split the 73-word
      "Second, ..." sentence at its em-dash boundary.
  (c) Delete the ISM-null restatement in paragraph 2, keeping paragraph 2's UNIQUE content
      (the non-over-attribution statement about the compass endgame and the unresolved
      learned-basis question). Keep exactly one "transparently".
acceptable_alternatives: Keep both mentions but make paragraph 2's a back-reference
  ("as noted above").
additional_evidence_needed: none
dependencies: none; all numbers verified against the manuscript.
expected_improvement: A letter an editor can absorb in one pass, with the headline claim
  stated at exactly the scope the manuscript supports.
post_revision_verification: Re-read the rebuilt cover_letter.pdf; confirm 2.48/2.96 unchanged,
  the DT-GSK-only byte-stability narrowing intact, the null disclosed once, and no new
  strengthening of any claim.
status: open
```

---

```text
ticket_id: W15-11
review_stage: 15
reviewer_role: RW (T5-WRITE)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: writing (internal engineering identifiers in reader-facing text)
manuscript_location: papers/supplementary.tex, S6.5 body and Tables A22/A23 captions
  (rendered supplementary.pdf pp. 58-59): "no_sgsm" x5, "no_finalpolish", "no_adaptive";
  S6.1/S6.3 scaffold cells "no_bse" x4, "no_arch" x4, "no_ace", "no_psr", "no_linkage",
  "no_localsearch"; "_dt_profiles" x3
claim_id_or_artifact_id: X-ABL-01, X-ABL-02; S5.6 Legacy Identifiers table
concise_issue: Ablation cells are named in body prose and captions by their raw config
  toggle strings, and "no_sgsm" re-exposes the retired SGSM identifier that the paper's own
  Legacy-Identifiers section exists to retire.
exact_evidence_or_observation:
  - supplementary.pdf S6.5: "...three single-toggle variants that disable, in turn, the
    interaction-structure memory itself (no_sgsm), its adaptive confidence gate (no_adaptive),
    and the ISM-dependent final polish (no_finalpolish)."
  - Table A23 caption: "...the memory-off (no_sgsm) cell, by CEC2017 function class..."
  - S5.6 (Legacy Identifiers, supplementary.tex:1294-1307) states the method and its
    structure-memory subsystem were renamed and that legacy ids are retained only "wherever a
    hash or a directory name would otherwise change" -- yet S6.5/S6.6 print the legacy token
    in narrative prose and a caption.
root_cause: Ablation cell ids were carried from the run configuration into the write-up
  verbatim.
scientific_or_editorial_justification: Sec.10.17.4 ("internal engineering nouns leaking into
  prose: internal profile/config names, dataclass/field names ... presented as prose rather
  than as a deliberate reproducibility reference").
impact_on_validity_or_acceptance: Low scientific impact; moderate presentation impact,
  compounded because the legacy acronym the paper retired reappears in a figure caption.
required_correction: Use human-readable cell names in prose and captions and give the machine
  id once, in the S6.1 design table, as a "cell id" column -- e.g. "the memory-off cell
  (release id `no_sgsm`)" at first use only, thereafter "the memory-off cell".
acceptable_alternatives: Keep the ids but add them to the S5.6 Legacy Identifiers table so a
  reader can resolve "sgsm" -> ISM at the point of use.
additional_evidence_needed: none
dependencies: If the ids appear in generated tables, fix the generator, not the .tex
  (Sec.10.11).
expected_improvement: No retired identifier appears in reader-facing narrative; cell naming
  reads as authored.
post_revision_verification: grep the rebuilt supplement for "sgsm" outside the Legacy
  Identifiers table -> 0 hits.
NOTE (calibration): the 27 `*.py` module names in S5.2/S5.9/S5.10 are NOT flagged. They are
  deliberate reproducibility references in a reproducibility appendix, which Sec.10.17.4
  explicitly permits. Do not remove them.
status: open
```

---

```text
ticket_id: W15-12
review_stage: 15
reviewer_role: RW (T5-WRITE)
severity: Editorial
priority: P2
confidence: Confirmed
issue_type: writing (spelling-variety inconsistency)
manuscript_location: papers/sections/performance.tex:744 and :766 ("characterise");
  papers/supplementary.tex:1634 ("behaviour"); papers/supplementary.tex:2108 ("favourable").
  Propagated to the DOCX build sources: papers/main_pandoc.tex:2620, :2642;
  papers/supplementary_pandoc.tex:1614, :2086.
claim_id_or_artifact_id: n/a
concise_issue: Three British-spelling strays in an otherwise consistently American-spelled
  package, one of them the same verb spelled both ways in the main manuscript.
exact_evidence_or_observation:
  - "characterise" x2 (performance.tex:744 "the figures characterise \dtgsk{}'s own cost";
    :766 same phrase in the tab:runtime caption) vs "characterizes" x1
    (conclusions.tex:33 "the study characterizes the algorithm's standing tier by tier").
  - "behaviour" x1 (supplementary.tex:1634) vs "behavior" x8.
  - "favourable" x1 (supplementary.tex:2108, rendered on supplementary.pdf p.59) vs
    "favorable" x8, "favors" x6, "favoring" x1.
  - All other -ize/-ization forms are American throughout (optimization x17,
    initialization x8, normalized x6, symmetrized x4, ...).
root_cause: Multi-pass drafting without a spelling-variety lock.
scientific_or_editorial_justification: Sec.10.17.5 ("fix mechanical formatting tells ...
  inconsistent hyphen/dash/quote styles"); MDPI accepts either variety but requires internal
  consistency.
impact_on_validity_or_acceptance: None scientifically; a copy-editor catch that is cheaper to
  fix now, and one of the three sits in a table caption.
required_correction: performance.tex:744, :766 -> "characterize"; supplementary.tex:1634 ->
  "behavior"; supplementary.tex:2108 -> "favorable". Then rebuild both DOCX sources so the
  Word deliverables inherit the fix.
acceptable_alternatives: Switch the whole package to British spelling (far more edits; not
  recommended).
additional_evidence_needed: none
dependencies: DOCX rebuild + cross-format parity re-run.
expected_improvement: One spelling variety across PDF and Word, main and supplement.
post_revision_verification: Re-run the BrE/AmE scan on all four .tex sources and both rendered
  PDFs -> 0 British forms.
status: open
```

---

```text
ticket_id: W15-13
review_stage: 15
reviewer_role: RW (T5-WRITE)
severity: Editorial
priority: P3
confidence: Confirmed
issue_type: writing (abstract length and packing)
manuscript_location: papers/main.tex:127-153 (rendered DT-GSK.pdf p.1)
claim_id_or_artifact_id: RS-01 NARROWED (abstract headline number)
concise_issue: The rendered abstract is 201 whitespace-delimited tokens against the file's own
  stated "<=200 words" constraint, and its second sentence is 50 words carrying the entire
  method description.
exact_evidence_or_observation:
  - main.tex:123 (build comment): "Abstract (<=200 words; no citations; one headline result
    number ...)".
  - Rendered abstract token count = 201 (whitespace tokenization of the pdftotext extraction
    between "Abstract:" and "Keywords:"). Note that counters differ on math tokens such as
    "D = 50"; the journal's own counter should be treated as authoritative.
  - Sentence word counts: 15, 50, 20, 39, 21, 9, 15, 24, 8. The 50-word sentence is
    "Dimension-Tiered Gaining-Sharing Knowledge (DT-GSK) instead resolves control by
    dimension: a dimension-tiered adaptive scaffold---credit-based operator selection with
    acceptance-gated pruning, a tier-floored population schedule, and a budget-safe
    escape---serves every tier, and a deterministic, budget-exact eigenframe refinement runs
    once in the final slice from D = 50 upward, retaining the GSK vector-update equations."
root_cause: Successive additions (the narrowed null advertisement, the selection-exposure
  sentence) against a fixed budget.
scientific_or_editorial_justification: Sec.15.1 (economy without loss of necessary detail);
  Sec.10.14 (page/limit discipline resolved by migration, never by compressing claims).
impact_on_validity_or_acceptance: Low; but a one-token overrun on a hard limit is a desk-check
  item, and the 50-word sentence is the first prose an editor reads.
required_correction: Split the 50-word sentence at its second em-dash (see §6 R-02). If the
  journal counter also returns >200, recover the token in the same sentence rather than by
  deleting any scope or qualification. Under no circumstances recover length by removing
  "a descriptive across-dimension mean", "a Holm-significant loss", "never
  Nemenyi-separable", "configuration-selection exposed", or "All findings are scoped to the
  GSK-family panel".
acceptable_alternatives: none.
additional_evidence_needed: The journal's own word count at submission.
dependencies: W15-02 (canonical name for the C1 mechanism appears in this same sentence).
expected_improvement: Two readable sentences; comfortably inside the limit.
post_revision_verification: Re-count the rendered abstract; verify every bound listed above is
  still present.
status: open
```

---

```text
ticket_id: W15-14
review_stage: 15
reviewer_role: RW (T5-WRITE)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: writing (editorializing self-assessment in a results subsection)
manuscript_location: papers/supplementary.tex:2120 (rendered supplementary.pdf S6.6, p.60)
claim_id_or_artifact_id: X-ABL-02
concise_issue: A results subsection ends by asserting the finding's own importance in the
  first person, and uses a colloquial verb three lines earlier.
exact_evidence_or_observation:
  - supplementary.tex:2119-2120 "We accordingly report the interaction-structure memory as a
    controlled negative result on cheap accepted-move structure-learning --- a boundary we
    believe is itself informative for the GSK family."
  - S6.5 (rendered p.59) "...so it costs a third to well over half again in wall-clock and
    buys no measurable accuracy return." ("buys" is a register drop in an otherwise formal
    supplement.)
root_cause: Value framing migrated from the Conclusions, where it belongs, into a results
  subsection.
scientific_or_editorial_justification: Sec.15.1 (distinction among evidence, inference, and
  speculation; stable authorial voice), Sec.15.2 (generic statements; polished but empty
  prose).
impact_on_validity_or_acceptance: Minor. The null is a genuine contribution and the paper is
  entitled to say so -- in the Conclusions, which already does ("a boundary on the idea that
  structure can be learned cheaply").
required_correction: End S6.6 on the evidence: "We accordingly report the interaction-structure
  memory as a controlled negative result on cheap accepted-move structure-learning." (delete
  the "we believe" clause -- the Conclusions already carries the value statement). Replace
  "buys no measurable accuracy return" with "yields no measurable accuracy return".
acceptable_alternatives: Keep the clause but state it impersonally and bound it: "-- a
  boundary for the GSK family at the dimensions evaluated."
additional_evidence_needed: none
dependencies: style-only; the null, the overhead percentages, and the not-an-equivalence-test
  caveat all remain untouched.
expected_improvement: One register through the supplement; evidence and appraisal separated.
post_revision_verification: Confirm the Conclusions still carries the value framing so nothing
  is lost.
status: open
```

---

```text
ticket_id: W15-15
review_stage: 15
reviewer_role: RW (T5-WRITE)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: writing (repeated sentence scaffold)
manuscript_location: sections/related_work.tex:182, :195, :216; sections/
  proposed_algorithm.tex:69, :587, :788; sections/performance.tex:32, :126, :364;
  sections/conclusions.tex:66, :77; supplementary.tex (7 further instances)
claim_id_or_artifact_id: n/a (voice)
concise_issue: The same paragraph-opening scaffold -- a cardinal number plus a plural noun
  plus a copula ("Three contrasts matter here.", "Two properties define it.", "One provenance
  qualification applies.", "Two qualifications apply to how that table should be read.") -- is
  used 18 times across the package, three times each in three different sections.
exact_evidence_or_observation: Regex tally over the comment-stripped sources: related_work 3,
  proposed_algorithm 3, performance 3, conclusions 2, supplementary 7 = 18. Near-identical
  pairs across documents: "One provenance qualification applies" (performance.tex:32) and
  "One provenance qualification is" (supplement).
root_cause: A useful device adopted as a default.
scientific_or_editorial_justification: Sec.10.17.5 ("repeated sentence scaffolds ... require
  varied, purposeful sentence and paragraph structure"), Sec.15.2 (over-regular rhythm).
impact_on_validity_or_acceptance: Cumulative rather than local; it is the most visible
  remaining cadence tic once the classic connectives are gone.
required_correction: Keep the scaffold where the enumeration is genuinely load-bearing
  (related_work.tex:182 "Three contrasts matter here" governs a real three-way comparison;
  conclusions.tex:66 "Eleven limitations bound these findings" is a real count). Recast the
  ~8 uses where the number is 1 or 2 and adds nothing -- e.g. performance.tex:32
  "One provenance qualification applies:" -> "The eGSK panel cells carry one provenance
  qualification:" (the same content, with an agent).
acceptable_alternatives: none needed.
additional_evidence_needed: none
dependencies: style-only.
expected_improvement: Paragraph openings vary with the argument.
post_revision_verification: Re-run the scaffold tally; target <= 8 package-wide.
status: open
```

---

```text
ticket_id: W15-16
review_stage: 15 (recording a governing-prompt defect, per the seat brief and Sec.1.4)
reviewer_role: RW (T5-WRITE)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: compliance (stale governing document)
manuscript_location: papers/PAPER_REVIEW_PROMPT.md:118-120 (Sec.1.5 snapshot) and :3299
  (Sec.10.7 final bullet, "Runtime-table single-environment refresh (RT-001, IN PROGRESS)")
claim_id_or_artifact_id: RT-001; papers/governance/remediation_2026_07_18/ticket_status.csv
concise_issue: The review prompt's own snapshot and its Sec.10.7 RT-001 control describe a
  project state that no longer exists, and following Sec.10.7 literally would cause a reviewer
  to mis-assess the current runtime table.
exact_evidence_or_observation:
  - Prompt Sec.1.5 (:120): "the 80-ticket remediation ledger ... stands at 73/80 fully closed
    ... and seven terminal / machine-gated / author-gated tickets remain open (RT-001 the live
    runtime blocker; ...)".
    ACTUAL: papers/governance/remediation_2026_07_18/ticket_status.csv, 80 rows,
    lifecycle_status = closed_verified 70 + superseded_with_evidence 10 = 80/80 resolved.
  - Prompt Sec.10.7 (:3299): "the runtime table (tab:runtime) and its source (cost_cec2017.csv)
    are being brought into single-environment comparability by RE-TIMING ALL SIX COMPARATORS on
    one idle machine (scripts/retime_comparators.py) ... the current table MIXES TWO
    MEASUREMENT SESSIONS and is PROVISIONALLY FROZEN ... The review MUST treat the current
    runtime cells as in-progress, not final".
    ACTUAL (ticket_status.csv, RT-001, lifecycle_status = closed_verified, closed_utc
    2026-07-21): "RESOLVED via Decision 7 Option 3 (DT-GSK-only fallback). Option 2 (re-time
    the six comparators) was executed 2026-07-21 ... but FAILED the determinism gate: 3,772
    scientific-column diffs ... tab:runtime re-scoped to DT-GSK-only with corrected post-fix
    numbers (4.93/13.04/23.30/41.59)".
    ACTUAL manuscript (sections/performance.tex:759-784, rendered Table 8): a two-column table
    with FOUR DT-GSK rows and no comparator rows; caption states "Comparator wall-clock was
    measured in a separate session and is not tabulated here, so no cross-algorithm runtime
    comparison is made."
root_cause: Sec.1.5 is dated 2026-07-20 and Sec.10.7's RT-001 bullet was written while the
  re-timing was still planned; both predate the 2026-07-21 resolution.
scientific_or_editorial_justification: Sec.1.4 precedence -- current project state outranks
  the prompt's embedded snapshot. Recording the staleness is required so downstream seats do
  not certify or fail the runtime table against a superseded description.
impact_on_validity_or_acceptance: A reviewer following Sec.10.7 verbatim would look for a
  mixed-session six-comparator table, fail to find it, and could raise a false finding either
  way (either "the promised re-timing is missing" or "the mixed table is still shipped").
required_correction: Update Sec.1.5 to 80/80 resolved and rewrite the Sec.10.7 RT-001 bullet
  to record the actual disposition: Option 2 attempted and rejected on determinism grounds;
  Option 3 (DT-GSK-only table, cross-algorithm runtime comparison withdrawn) adopted and
  verified; the control for reviewers becomes "confirm no cross-algorithm runtime claim is
  made anywhere" rather than "treat the cells as in-progress".
acceptable_alternatives: Mark Sec.10.7's RT-001 bullet HISTORICAL in the same way Sec.1.5.0 is
  marked superseded, with a pointer to the ticket row.
additional_evidence_needed: none
dependencies: Prompt maintenance only; no manuscript change.
expected_improvement: The governing document stops contradicting the artifact it governs.
post_revision_verification: Re-read Sec.1.5 and Sec.10.7 against ticket_status.csv and
  Table 8.
status: open
```

---

### Advisory observations (recorded, deliberately not ticketed)

**A-1 — rendered author-metadata placeholder.** Page 1 of `DT-GSK.pdf` prints
`[H.S.M.R. institutional e-mail -- to be added at submission] (H.S.M.R.)` (source
`main.tex:112`). Under §10.17.4 a bracketed editorial note in reader-facing text is normally a
Gate-N item; however §1.5.4 of the governing prompt places the corresponding-author
institutional e-mail explicitly **out of scope** for this cycle with the instruction *"ignore
it, raise no ticket, fail no gate"*. I therefore raise **no ticket** and record only that it is
still rendered and must not reach the submission portal. The ORCID placeholders
(`0000-0000-0000-0000`, `main.tex:96-98`) were checked and do **not** render — no ORCID string
or `orcid.org` link appears in the PDF.

**A-2 — ISM role label.** "exploratory" (abstract) vs "supporting mechanism" (everywhere else).
Both are accurate; harmonise opportunistically.

**A-3 — supplement cross-reference precision.** `performance.tex:753` and the `tab:runtime`
caption point the reader to Section S6.7 for the isolated ISM compute cost. S6.7 is titled
"Implementation Caveats: Two Corrected Defects and Their Evidence Trail" and does restate the
overhead figures, so the pointer is not dangling — but the numbers are *reported in context* in
S6.5. Consider "Sections S6.5 and S6.7".

---

## 6. Highest-impact example revisions (§15.4 protocol)

Each entry gives location, excerpt, problem, the scientific meaning that must survive, the
revision, and whether facts/numbers/citations were verified. **No revision below changes a
numerical value, a statistical interpretation, a claim scope, a citation, an equation, a method
behaviour, an experimental-design statement, an exhibit, or a limitation.** Where I could not
verify which quantity the authors intend (R-04), I give a template with placeholders, as §15.4
requires.

---

**R-01 — `sections/introduction.tex:135`**
*Original (excerpt):* "…ISM is therefore positioned as a secondary exploratory mechanism rather
than as the primary source of DT-GSK's performance standing. Its inclusion provides a fully
specified and reproducible investigation of structure learning from strictly improving accepted
moves, while the paper's principal contributions remain the dimension-tiered adaptive scaffold
(C2), the eigenframe final polish (C1), and the controlled, budget-fair evaluation framework (C3)."
*Problem:* Register seam; agentless framing verb; inflated abstract noun ("Its inclusion
provides … an investigation"); restates the C1–C3 list three lines after the bullets; introduces a
fourth name for C3.
*Meaning to preserve:* ISM is secondary/exploratory, not the source of the standing; it is fully
specified and reproducible; the principal contributions are C1–C3; the two supplement pointers
(S6.5, S6.6) and both null scopes.
*Suggested revision:* "We therefore treat ISM as a secondary, exploratory mechanism rather than
as the source of DT-GSK's standing: we specify it fully and release it so the question can be
re-tested, but the contributions we claim are C1–C3."
*Why better:* Restores the active, first-person-plural register of the surrounding paragraphs;
removes the redundant list; one verb replaces the abstract-noun chain; C3 keeps its bullet name.
*facts_numbers_citations_verified:* yes (S6.5/S6.6 pointers and both scope statements are
retained in the preceding two sentences, which are unchanged).

---

**R-02 — `main.tex:129–137` (abstract sentence 2, 50 words)**
*Original:* "Dimension-Tiered Gaining-Sharing Knowledge (DT-GSK) instead resolves control by
dimension: a dimension-tiered adaptive scaffold---credit-based operator selection with
acceptance-gated pruning, a tier-floored population schedule, and a budget-safe
escape---serves every tier, and a deterministic, budget-exact eigenframe refinement runs once in
the final slice from $D = 50$ upward, retaining the GSK vector-update equations."
*Problem:* 50 words; two coordinate clauses separated by a nested em-dash list; the mechanism
name here ("eigenframe refinement") is not the name used in the body.
*Meaning to preserve:* control resolved by dimension; the three scaffold components; the polish
is deterministic, budget-exact, one-shot, final-slice, $D \ge 50$; GSK vector updates retained.
*Suggested revision:* "Dimension-Tiered Gaining-Sharing Knowledge (DT-GSK) instead resolves
control by dimension. A dimension-tiered adaptive scaffold---credit-based operator selection with
acceptance-gated pruning, a tier-floored population schedule, and a budget-safe escape---serves
every tier, and a deterministic, budget-exact eigenframe final polish runs once in the final
slice from $D = 50$ upward. The GSK vector-update equations are retained unchanged."
*Why better:* Three readable sentences; binds the abstract to the body's canonical name (W15-02);
the "retained" clause becomes a claim rather than a trailing participle.
*facts_numbers_citations_verified:* yes ($D = 50$ gate verified at
`proposed_algorithm.tex:585` and Table 2 row "Eigenframe polish … off/off/on/on").

---

**R-03 — `sections/performance.tex:209–231` (statistical protocol, duplicated definition)**
*Original:* two separate sentences defining the matched-pairs rank-biserial correlation with the
same formula (lines 209–213 and 227–231), plus a third statement of the A12 unit caveat
(221–226).
*Problem:* One point stated three times in one paragraph.
*Meaning to preserve:* (i) the aligned effect size for the paired across-function Wilcoxon is the
matched-pairs rank-biserial $r=(R^{+}-R^{-})/(R^{+}+R^{-})$, $r>0$ favouring DT-GSK; (ii) $R^{+}/R^{-}$
are released per comparison; (iii) A12 is a *descriptive companion*; (iv) the tabulated/released
A12 units differ (function-mean vs run-level) and are not interchangeable; (v) the 0.56/0.64/0.71
labels are descriptive only.
*Suggested revision:* "Every test is reported with its aligned effect size. Because the
across-function test is a matched-pairs Wilcoxon, that effect size is the matched-pairs
rank-biserial correlation $r=(R^{+}-R^{-})/(R^{+}+R^{-})$, with $r>0$ favouring DT-GSK; the
signed-rank sums $R^{+}/R^{-}$ are released per comparison. The Vargha--Delaney $A_{12}$ is
retained as a descriptive companion only, under the conventional 0.56/0.64/0.71 magnitude
labels. Two $A_{12}$ variants exist in the released artifacts and are not interchangeable: an
across-function value computed on the 29 per-function means (the same unit as the Wilcoxon) and
the per-function run-level values in the effect-size workbook."
*Why better:* Five facts, one statement each; the distinction the paragraph cares about becomes
the paragraph's clearest sentence.
*facts_numbers_citations_verified:* yes — released columns inspected:
`wilcoxon_holm_cec2017_D*.csv` carries `rank_biserial`, `w_plus`, `w_minus`;
`effect_sizes_cec2017_D*.csv` carries per-function `a12`/`cliffs_delta` at `n_runs=51`.

---

**R-04 — `sections/performance.tex:362`, `:365–368`, `:409`, `:426` (W15-01) — TEMPLATE, not a
definitive rewrite**
*Original:* "…win/tie/loss counts, $A_{12}$ effect sizes, and Holm decisions…"; "The $A_{12}$
column is computed over the 29 per-function means…"; "with $A_{12}$ of 0.490, 0.505, and 0.472…";
"the largest effect is against APGSK at $D=100$ ($A_{12}=0.712$)".
*Problem:* Table 14 has no $A_{12}$ column (it prints $r$); the quoted $A_{12}$ values are printed
nowhere in either document.
*Meaning to preserve:* the effect direction and magnitude statements attached to each cell, and
the unit-of-analysis warning.
*Suggested revision (template):*
- `:362` → "…win/tie/loss counts, matched-pairs rank-biserial effect sizes $r$, and Holm
  decisions…" **(definitive — the column was verified).**
- `:365–368` → "The tabulated effect size is the matched-pairs rank-biserial correlation $r$,
  aligned with the paired across-function Wilcoxon. It is distinct from the per-function
  run-level $A_{12}$ in the released effect-size workbook; the two are not interchangeable."
  **(definitive.)**
- `:409` → "…with «EFFECT-SIZE NAME» of «V1», «V2», and «V3» — negligible magnitudes, two of which
  ($D=30$ and $D=100$) lean marginally toward eGSK." **(placeholder: the authors must decide
  whether this sentence reports the tabulated $r$ (−0.286, −0.002, −0.057) or the across-function
  $A_{12}$ (0.490, 0.505, 0.472); if $A_{12}$ is kept, the sentence must name the released source.)**
- `:426` → "…the largest effect is against APGSK at $D=100$ («EFFECT-SIZE NAME» = «V4»)."
  **(placeholder: $r=+0.977$ tabulated, or $A_{12}=0.712$ from the across-function computation.)**
*Why better:* Every printed statistic resolves to a visible referent.
*facts_numbers_citations_verified:* **partly.** I verified the table columns and independently
recomputed all four $A_{12}$ values from `descriptive_stats_cec2017_D{30,50,100}.csv`
(0.49049 / 0.50535 / 0.47206; APGSK D100 0.71225) — the numbers are right. I did **not** verify
which statistic the frozen analysis plan designates for this sentence, so I give a template.

---

**R-05 — `sections/related_work.tex:284–297` (106 words, 3 semicolons)**
*Original:* "Third, *regime-limited adaptation evidence*. AGSK's and APGSK's adaptive machinery
was evaluated on CEC2020 at $D\le20$; FDB-AGSK at a $1000\times D$ budget without $D=10$; and the
two strongest variants share a low-dimension weakness on CEC2017 (eGSK significantly worse than
AGSK at $D=10$; ATMALS-GSK competitive-only there). DT-GSK responds with a dimension-tiered
adaptive scaffold --- the ACE credit-based selector with ARGP pruning, the tier-floored NLPSR
schedule (a variant of the APGSK NLPSR schedule, not claimed as new), the budget-safe escape in
the JADE/SHADE archive lineage, and a deep-stall restart that preserves the global best ---
resolved from a single frozen configuration per dimension tier."
*Problem:* Two independent arguments (the deficiency, and the response) in one 106-word span with
four citations whose attachment must be re-parsed.
*Meaning to preserve:* every regime bound ($D\le20$, $1000\times D$, no $D=10$), both
low-dimension weaknesses with their citations, the four scaffold components, the NLPSR
non-novelty disclaimer, the JADE/SHADE lineage, the global-best-preserving restart, and the
single-configuration statement.
*Suggested revision:* "Third, *regime-limited adaptation evidence*. AGSK's and APGSK's adaptive
machinery was evaluated on CEC2020 at $D\le20$, and FDB-AGSK at a $1000\times D$ budget with
$D=10$ untested. The two strongest variants also share a low-dimension weakness on CEC2017: eGSK
is significantly worse than AGSK at $D=10$, and ATMALS-GSK is competitive-only there. DT-GSK
responds with a dimension-tiered adaptive scaffold resolved from a single frozen configuration
per tier: the ACE credit-based selector with ARGP pruning; the tier-floored NLPSR schedule (a
variant of the APGSK schedule, not claimed as new); the budget-safe escape, in the JADE/SHADE
archive lineage; and a deep-stall restart that preserves the global best."
*Why better:* Deficiency and response separate; each citation sits beside its own clause; the
component list becomes a genuine list rather than an em-dashed interruption.
*facts_numbers_citations_verified:* yes — all values and citation keys retained unchanged from
`related_work.tex:284–297`.

---

**R-06 — `sections/proposed_algorithm.tex:740–750` (104 words)**
*Original:* "The dimension-gated structures dominate only at upper tier: the three $O(D^{2})$
interaction matrices are decayed at $O(D^{2})$ per update (the $O(D)$ activity vector at $O(D)$),
and each strictly-improving accepted move contributes a rank-one outer product over its
active-coordinate set $J$ ($O(|J|^{2})$, $|J|\le D$), summing to $O(NP\cdot D^{2})$ worst case and
less when the per-move support is sparse; this runs every generation at $D=50$–$99$ but is thinned
at $D\ge100$ (updated every tenth generation, from a capped sample of accepted moves), its linkage
blocks re-extracted on a slower multi-generation cadence, and the eigenframe polish performs a
single $O(D^{3})$ eigendecomposition once per run."
*Problem:* Three distinct cost statements (per-update decay, per-move accumulation, cadence
thinning) plus the one-shot eigendecomposition in one sentence.
*Meaning to preserve:* every complexity term and every cadence value, verbatim.
*Suggested revision:* "The dimension-gated structures dominate only at upper tier. Each update
decays the three $O(D^{2})$ interaction matrices at $O(D^{2})$ and the $O(D)$ activity vector at
$O(D)$. Each strictly-improving accepted move then contributes a rank-one outer product over its
active-coordinate set $J$ ($O(|J|^{2})$, $|J|\le D$), summing to $O(NP\cdot D^{2})$ in the worst
case and less when the per-move support is sparse. This runs every generation at $D=50$–$99$; at
$D\ge100$ it is thinned to every tenth generation from a capped sample of accepted moves, with the
linkage blocks re-extracted on a slower multi-generation cadence. The eigenframe polish adds one
$O(D^{3})$ eigendecomposition per run."
*Why better:* Five statements, five sentences; a reader can check each complexity term against
Table 4 without re-parsing.
*facts_numbers_citations_verified:* yes — all terms retained; matches
`phase_03/complexity_analysis.md` binding comment on the same lines.

---

**R-07 — `sections/proposed_algorithm.tex:716–728` (3-semicolon enumeration)**
*Original:* "Three distinct reproducibility levels should be kept apart: (i) *RNG-substream
isolation* --- the structural guarantee just stated, which makes component-level re-evaluation
well defined and is test-enforced in the repository's regression suite; (ii)
*same-environment trajectory repeatability* --- bit-for-bit identical runs under the same
single-threaded build with a fixed floating-point reduction order (the shipped configuration; it
is not a cross-thread or cross-platform guarantee, as noted in Section 4); and (iii) *artifact
byte-identity* --- the released result files reproduce byte-for-byte after the documented
normalization."
*Problem:* A three-item definition list rendered as one 90-word sentence with nested
parentheticals.
*Meaning to preserve:* all three level definitions, the test-enforcement statement, the
single-thread/fixed-reduction-order precondition, the explicit non-guarantee across threads and
platforms, the normalization qualifier, and the following sentence's DT-GSK-only scope.
*Suggested revision:* Convert to a three-item `itemize` (the class already uses `itemize` for the
contributions), one level per item, keeping every clause verbatim.
*Why better:* This is exactly the content §10.17.2/§10.17.7 want laid out as a list; it also lets
the "no byte-stability claim is made for the comparator implementations" sentence stand alone,
which is a limitation and should be conspicuous.
*facts_numbers_citations_verified:* yes — no wording inside the three definitions changes.

---

**R-08 — `sections/introduction.tex:101–112` (C2 bullet, 4 semicolons)**
*Problem:* The bullet is one sentence with four semicolon-separated mechanism clauses followed by
a novelty-labelling sentence.
*Meaning to preserve:* ACE (EMA credit-based selector over complete operator settings) + ARGP;
tier-floored NLPSR *explicitly not claimed as new*; hard-capped BSE from a distance-filtered
diversity archive; deep-stall full restart preserving the global best; and the MOD/ORI labelling
sentence with its "we did not find ARGP's rule among the surveyed GSK variants" bound.
*Suggested revision:* Keep the semicolon list — it is a genuine four-item enumeration — but break
after the second item: "…with Acceptance-Rate Gated Pruning (ARGP) of unproductive arms. It also
adds a tier-floored Nonlinear Population-Size Reduction (NLPSR) schedule — a variant of the APGSK
NLPSR schedule, explicitly not claimed as new; a hard-capped Budget-Safe Escape (BSE) seeded from
a distance-filtered diversity archive; and a deep-stall full restart (multi-start) that preserves
the global best."
*Why better:* Halves the longest clause chain without dissolving a real enumeration.
*facts_numbers_citations_verified:* yes — the non-novelty disclaimer and the ARGP survey bound are
retained verbatim.

---

**R-09 — `sections/performance.tex:429–437`**
*Problem:* 79-word sentence carrying the BCa method caveat, then four bracketed intervals, then
the overlap statement.
*Suggested revision:* "Seeded bootstrap BCa rank-stability intervals accompany the Friedman mean
ranks (Supplementary Material, Section S2). They resample the fixed per-function midranks rather
than recomputing ranks within each resample, so they are read descriptively as a spread on the
mean rank, not as a formal overlap test. DT-GSK's intervals are [2.29, 3.43], [2.07, 3.10],
[1.86, 2.69], and [1.90, 2.83] at $D=10/30/50/100$; they overlap eGSK's at $D\in\{30,50,100\}$,
consistent with the pairwise non-significant cells above."
*facts_numbers_citations_verified:* yes — all four intervals and the dimension set copied
unchanged.

---

**R-10 — `sections/performance.tex:9–17` (section opener)**
*Problem:* Reproduces the abstract's headline sentence and then adds the scope coda that recurs
five more times.
*Suggested revision:* Keep the first sentence and the "reported at that resolution" rationale;
delete "Every comparative statement is scoped to this panel; no field-wide claim is made." here
**only if** the identical bound is retained in §4.1's *Evidence discipline* paragraph — which it
is, and which is the better home for it.
*facts_numbers_citations_verified:* yes — bound verified present at `performance.tex:36–38`
("no runtime-superiority claim is made anywhere in this paper") and `:871–874` (NFL/panel bound).
**Constraint:** at least one panel-scope statement must remain in §4; do not execute this deletion
without that check.

---

**R-11 — `sections/performance.tex:678`**
*Original:* "The unfavorable case is discussed rather than skipped. On F26 at $D=30$, …"
*Suggested revision:* "On F26 at $D=30$, …" (delete the first sentence; the discussion that
follows *is* the demonstration).
*facts_numbers_citations_verified:* yes — the entire F26 discussion, including the higher mean
error, the unreached attractor, and the smallest SD, is untouched.

---

**R-12 — `sections/performance.tex:405`**
*Original:* "The unfavorable and borderline cells are stated plainly. Against eGSK, …"
*Suggested revision:* "Against eGSK, …"
*facts_numbers_citations_verified:* yes — all six adverse/borderline cells that follow are
retained.

---

**R-13 — `sections/performance.tex:124–126`**
*Original:* "…the exception is recorded in the protocol exhibit and the pairing audit rather than
hidden. One evidence gap is disclosed up front. At the time of the frozen analysis, APGSK per-run
records…"
*Suggested revision:* "…the exception is recorded in the protocol exhibit and the pairing audit.
At the time of the frozen analysis, APGSK per-run records…"
*Why better:* Removes two self-certifications; the disclosure itself is unaffected.
*facts_numbers_citations_verified:* yes — the APGSK-gap paragraph and its footnote are untouched.

---

**R-14 — `sections/proposed_algorithm.tex:263`**
*Original:* "Its five sub-mechanisms are labeled honestly: ACE, NLPSR, BSE, the diversity archive,
and the deep-stall restart are modifications of cited antecedents; we did not find ARGP's
acceptance-rate-gated arm-freezing rule among the surveyed GSK variants."
*Suggested revision:* "ACE, NLPSR, BSE, the diversity archive, and the deep-stall restart are
modifications of cited antecedents; we did not find ARGP's acceptance-rate-gated arm-freezing rule
among the surveyed GSK variants."
*Why better:* The labelling *is* honest; saying so is what weakens it.
*facts_numbers_citations_verified:* yes — MOD/ORI attributions unchanged.

---

**R-15 — `sections/conclusions.tex:32–35`**
*Original:* "The empirical findings are panel-scoped and dimension-resolved --- the study
characterizes the algorithm's standing tier by tier rather than claiming uniform dominance ---
and the unfavorable cells are stated with the favorable ones."
*Suggested revision:* "The empirical findings are panel-scoped and dimension-resolved: the study
characterizes DT-GSK's standing tier by tier rather than claiming uniform dominance."
*Why better:* Deletes the third self-certification; the following two paragraphs state the
unfavourable cells, which demonstrates the point. Also replaces "the algorithm" with the named
subject.
*facts_numbers_citations_verified:* yes — every adverse cell in the following paragraph
(11–2–16 / 13–0–16 / 12–0–17, the CD non-separability, the CEC2011 Holm loss, the CEC2013 $D=30$
third place) is retained.

---

**R-16 — `papers/supplementary.tex:1173–1177`** — see W15-08 for the full before/after.
*facts_numbers_citations_verified:* yes (Conclusions and S5.4 texts compared line by line).

---

**R-17 — `papers/cover_letter.tex:55` opening** — see W15-10(a) for the full before/after.
*facts_numbers_citations_verified:* yes (2.48 / 2.96 verified against `main.tex:140–141` and
`conclusions.tex:36–38`).

---

**R-18 — `papers/cover_letter.tex:55`, the 73-word "Second," sentence**
*Suggested revision:* "Second, a **dimension-tiered adaptive scaffold**: a bandit-style
operator-configuration selector with acceptance-gated arm pruning, a tier-floored population-size
reduction schedule, a hard-capped stagnation escape, and a deep-stall restart that preserves the
global best. We present it as a labelled modified/original composite over published GSK-family
mechanisms, never as a new base operator."
*facts_numbers_citations_verified:* yes — all four components and the never-a-new-base-operator
bound retained; "honestly" dropped per W15-04.

---

**R-19 — `papers/cover_letter.tex:57`**
*Suggested revision:* Delete the restatement of the null and keep the unique content: "We are
careful not to over-attribute performance to any mechanism the isolation does not separate: the
deterministic compass endgame is evaluated as a whole, and the added value of the learned basis
over coordinate or random directions remains unresolved."
*facts_numbers_citations_verified:* yes — the null remains stated once, in ¶1.

---

**R-20 — `papers/supplementary.tex:2119–2120`** — see W15-14.
*facts_numbers_citations_verified:* yes.

---

**R-21 — `sections/performance.tex:32`**
*Original:* "One provenance qualification applies: the eGSK panel cells derive from…"
*Suggested revision:* "The eGSK panel cells carry one provenance qualification: they derive
from…"
*Why better:* Gives the sentence a subject and removes one of the 18 announce-scaffolds.
*facts_numbers_citations_verified:* yes.

---

**R-22 — `sections/performance.tex:744` and `:766`; `supplementary.tex:1634`, `:2108`**
`characterise` → `characterize`; `behaviour` → `behavior`; `favourable` → `favorable`. Rebuild
`main_pandoc.tex` / `supplementary_pandoc.tex`.
*facts_numbers_citations_verified:* yes (spelling only).

---

## 7. Generic sentences to remove or replace with evidence

These are sentences that could appear unchanged in another paper, or that assert a property the
adjacent text already demonstrates. **In every case the fix is to delete the sentence, not the
content it introduces.**

| # | location | sentence | disposition |
|---|---|---|---|
| G-1 | `performance.tex:678` | "The unfavorable case is discussed rather than skipped." | delete; the discussion follows |
| G-2 | `performance.tex:405` | "The unfavorable and borderline cells are stated plainly." | delete; the cells follow |
| G-3 | `performance.tex:126` | "One evidence gap is disclosed up front." | delete; the gap follows |
| G-4 | `performance.tex:124` | "…rather than hidden." | delete the clause only |
| G-5 | `proposed_algorithm.tex:263` | "Its five sub-mechanisms are labeled honestly:" | delete the framing |
| G-6 | `conclusions.tex:34` | "…and the unfavorable cells are stated with the favorable ones." | delete the clause |
| G-7 | `supplementary.tex:1162` | "…rather than absorbed silently." | delete the clause |
| G-8 | `supplementary.tex:2133` | "…are recorded here for provenance." | delete or replace with the reason they matter |
| G-9 | `cover_letter.tex:57` | "…and reports its outcome transparently:" | delete (duplicate of ¶1) |
| G-10 | `supplementary.tex:2120` | "…a boundary we believe is itself informative for the GSK family." | delete; the Conclusions carry the appraisal |
| G-11 | `introduction.tex:135` | "Its inclusion provides a fully specified and reproducible investigation of…" | replace with a direct verb (R-01) |
| G-12 | `performance.tex:13–17` | "The evidence below is reported at that resolution…" | keep the rationale; drop the trailing scope coda if §4.1 retains it |

**Deliberately NOT listed** (checked and judged legitimate): the roadmap paragraph
(`introduction.tex:137–148`) — conventional in this venue and present in the GSK exemplar; the
"First…Eighth" ladder in S5.4 and the "First/Second/Third" ladder in the cover letter — genuine
enumerations of distinct items, which §10.17.5 explicitly protects; "Hypotheses are stated once
here." (`performance.tex:197`) — real procedural signposting that tells the reader the hypotheses
will not be restated per test.

---

## 8. Style-only revision checklist

Every item below is confined to wording, order, sentence boundaries, and transitions. Under §15.4
none of them may change a numerical value, a statistical interpretation, a claim scope, a
citation, an equation, a method behaviour, an experimental-design statement, a table/figure, or a
limitation.

- [ ] **Terminology lock.** One canonical name for the C1 mechanism (W15-02); one wording for the
      ISM null (W15-06); one name for C3; one spelling variety (W15-12).
- [ ] **De-pack.** Split the ~20 main-text sentences over 55 words at existing semicolon/em-dash
      boundaries (W15-03, R-05…R-09). Target: 0 sentences > 55 words; ≤ 5 with ≥ 2 semicolons.
- [ ] **De-certify.** Delete the ~16 transparency meta-clauses (W15-04, G-1…G-10). **Verify after
      each deletion that the disclosure it introduced is still present.**
- [ ] **De-duplicate.** Collapse the intra-paragraph effect-size triplication (R-03); reduce the
      scope coda from 8 sites to 3 (abstract, §4.1, Conclusions) **after** confirming no bound is
      lost; back-reference rather than re-print the head-to-head triple in §4.6.
- [ ] **Fix referents.** Table 14 effect-size column naming and the four A12 values (W15-01/R-04)
      — this one is **not** style-only and needs author input.
- [ ] **Vary openings.** Recast the ~8 low-value announce-scaffolds (W15-15).
- [ ] **Captions.** Harmonise "7/7 series" wording; move the 16× APGSK stamp into an S3
      conventions paragraph; keep the CEC2011 loss disclosure everywhere it qualifies a figure
      (W15-07).
- [ ] **Identifiers.** Replace `no_sgsm`/`no_bse`/… in supplement prose and captions with reader
      names, machine id once (W15-11). Leave the `*.py` reproducibility references alone.
- [ ] **Abstract.** Split sentence 2; recheck the journal word count (W15-13).
- [ ] **Cover letter.** Rescope the opening hedge, split ¶1, delete the duplicated null (W15-10).
- [ ] **Rebuild + re-verify.** PDF and DOCX; re-run `check_manifest.py`,
      `validate_cross_format_parity.py`, `validate_document_consistency.py`,
      `validate_provenance_claims.py`, `validate_evidence_bindings.py`.
- [ ] **Post-edit claim diff.** Confirm that no numeral, citation key, scope word ("panel",
      "descriptive", "corroborative", "development-exposed"), or limitation present before the
      edits is absent after them.

---

## 9. Authorship-integrity and disclosure note (§15.5)

Stated explicitly, as §15.5 requires:

- **Automated AI-text detectors are not a reliable scientific quality or authorship standard**, and
  no detector result can prove who wrote any passage. No detector was run for this audit, no
  detector score is used as a gate, and none should be. Every finding above is grounded in a
  quoted excerpt with a file:line or a reproducible count.
- **The goal is clarity, originality, specificity, and intellectual ownership — never deceiving a
  detector.** Nothing in §6 or §8 is an evasion tactic. I did not recommend, and the authors must
  not apply, deliberate errors, random variation, synonym spinning, hidden or zero-width
  characters, paraphraser loops, or invented anecdotes.
- **I make no prediction that this manuscript will "pass AI detection"** and no prediction of
  acceptance.
- **The authors remain responsible for every claim, citation, calculation, and sentence**,
  including every revision suggested above. The suggestions are drafts for author judgement, not
  edits to be applied unread. Where I could not verify which statistic a sentence intends
  (R-04), I supplied a placeholder template rather than a definitive rewrite, per §15.4.

**Disclosure-policy compliance (verified as written, not merely present):**

- `main.tex:261–273` carries a methods-level *Use of Generative Artificial Intelligence*
  statement naming the tool and version (Claude Opus 4.8, Anthropic), describing the use
  (language editing, rephrasing, drafting of descriptive and expository prose), and asserting
  that no scientific content — algorithm design, implementation, protocol, or any reported
  number — was AI-generated, with authors taking full responsibility. This satisfies MDPI
  requirement (ii).
- `main.tex:277–284` repeats the tool and version in the Acknowledgments — MDPI requirement (iii).
- `sections/performance.tex:189–193` repeats the disclosure at the point of experimental
  description, which is stronger than required and is appropriate.
- `cover_letter.tex:59` carries the same disclosure to the editor.
- The four statements are **mutually consistent** in tool, version, scope of use, and the
  no-scientific-content boundary. I found no place where the disclosure is narrower in one
  surface than another.
- **One consistency note for the authors (not a defect):** the disclosure says the AI system
  "generated no scientific claim, result, or conclusion." That is a strong and specific claim about
  provenance. It is the authors' to make and I take it at face value; I record only that the
  writing-quality findings above (which concern human-editable style, terminology, and
  cross-reference hygiene) neither support nor undermine it.
- Conflicts of interest (`main.tex:288–297`) disclose that A.W.M. originated GSK and co-authored
  four of the six comparators and that H.S.M.R. co-authored eGSK. This is repeated in the cover
  letter and reflected in S5.4's seventh limitation. Consistent across all three surfaces.

**Detector-evasion scan (negative result):** I checked the rendered text of both PDFs for
zero-width characters, homoglyph substitutions, and unnatural synonym alternation on technical
terms. The only synonym alternations found are the ones ticketed above (W15-02, W15-06, W15-07),
and each is plainly drafting drift with a coherent explanation, not evasion: the variants cluster
by document section and by remediation date, which is the opposite of the randomised distribution
evasion produces.

---

## 10. Explicit non-findings (calibration record)

Recorded so downstream seats do not re-raise them, and so the panel can see where I declined to
manufacture an issue.

1. **Classic AI connectives are absent** (§2.1). This is a genuine strength of the current draft.
2. **Table A23 renders correctly.** The `pdftotext -layout` extraction scrambles it into
   misaligned rows; a 110-dpi page render of `supplementary.pdf` p.59 shows a correctly aligned
   booktabs table with all class rows, `n`, and both W/T/L columns intact. **No defect.**
3. **ORCID placeholders do not render.** `0000-0000-0000-0000` appears only in `main.tex:96–98`;
   no ORCID string or `orcid.org` link is present in the PDF (link extraction returns only the two
   MDPI journal URLs). **No reader-facing defect.**
4. **`*.py` module names in the reproducibility appendix** (S5.2, S5.9, S5.10) are deliberate
   reproducibility references and are permitted by §10.17.4's "what is legitimate" carve-out.
   **Not flagged.**
5. **Enumerated ladders are genuine.** S5.4's "First…Eighth", the cover letter's
   "First/Second/Third", and the introduction's C1/C2/C3 all enumerate distinct items. §10.17.5
   protects these. **Not flagged.**
6. **The 24-cell tally is internally consistent.** I counted the Decision columns of `T15.tex`
   directly: 3+5+5+4 = 17 significant wins, 3+1+1+2 = 7 no-difference, 0 losses — matching the
   prose at `performance.tex:391–396`, `:838–840` and `conclusions.tex:41–45`.
7. **Information density is not a defect.** The method and statistics sections are dense because
   the content is dense. My over-packing finding (W15-03) is about *syntax*, and every suggested
   split preserves 100% of the content.
8. **Remediation spot-checks that read correctly** (verified as prose, within my seat's scope):
   R-01 sign convention now in rendered text with a notation row; R-04 restart invariant reads
   correctly at `proposed_algorithm.tex:203–210` and `:411–428` (elitist except the deep-stall
   restart; separately held global best returned); R-05 budget-crossing disclosure at
   `performance.tex:164–178` reads naturally and states the fairness verification without
   over-claiming; R-08 the null is explicitly "rather than as a fourth claimed contribution"
   (`conclusions.tex:101–102`) and the abstract lists exactly three contributions; R-09 the cover
   letter's byte-stability claim is narrowed to DT-GSK and the reviewer block is a non-rendered
   LaTeX comment after `\end{document}`.
9. **R-13 is the one remediation I judge incompletely closed** — see W15-03. The two named
   paragraphs were fixed; the pattern was not.

---

## 11. Reproducing the measurements in this audit

All counts were produced by read-only scripts in the session scratchpad
(`…/scratchpad/s15/`): `scan.py` (AI-tell frequency), `scan2.py` (sentence length, em-dash
density), `scan3.py`/`scan4.py` (contrastive scaffolds, restated qualifications), `semis.py`
(semicolon packing), `term.py`/`term2.py` (non-overlapping terminology tallies), `caps.py`
(caption boilerplate), `spell.py` (BrE/AmE), `scaffold.py` (announce-scaffolds), `virtue.py`
(transparency meta-commentary), `a12.py` (independent recomputation of the four across-function
A12 values). All strip `%` comments so build annotations are never counted, and all operate on
copies; **no file under `papers/` was modified by this audit except this artifact.**
