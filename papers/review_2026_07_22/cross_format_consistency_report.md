# Stage 17 — Cross-format consistency report (canonical source ↔ PDF ↔ Word ↔ cover letter)

**Seat:** `s17_journal_production`
**Review date:** 2026-07-22
**Formats compared:** frozen `.tex` sources (canonical) · `papers/DT-GSK.pdf` (39 pp) ·
`papers/DT-GSK.docx` · `papers/supplementary.pdf` (61 pp) · `papers/supplementary.docx` ·
`papers/cover_letter.pdf` (2 pp) / `.tex` / `.md`

All statements are **CONFIRMED** unless marked **SUSPECTED**.

---

## 1. Single-frozen-state check (profile §10.12 first bullet; top-risk item 39) — PASS

There is exactly one canonical scientific state and all deliverables resolve to it:

* `papers/scripts/check_manifest.py` → `15/15 match []` (exit 0) against the freshly minted
  `main_manuscript_freeze_manifest.json` (anchor `abd2fa2f25c8…`).
* `papers/governance/submission_package_manifest.json` records SHA-256, byte size and page count
  for all five submission files; **all five hashes and both page counts recomputed identical**
  in this review (39 / 61 / 2 pp).
* The last commit `45248eb31` changed `papers/sections/performance.tex`, `main_pandoc.tex`,
  `DT-GSK.pdf` **and** `DT-GSK.docx` together — i.e. the source, PDF and Word deliverables moved
  as one unit. Verified below (§3) that the added sentence is present in **all three**.
* `validate_document_consistency.py` (exit 0) confirms the supplement inventory claimed in the
  main text matches the supplement's own sections (S1–S6, contiguous), and that
  `cover_letter.md` and `cover_letter.tex` agree on title, date, corresponding author, GenAI
  disclosure and contribution-scope markers.

**No three-way source↔PDF↔Word desync exists.**

## 2. Machine parity run

`python papers/scripts/validate_cross_format_parity.py` → **579 rows, 0 FAIL** (exit 0).

| Document | Class | PASS | PASS_FORMAT_DIFF | FAIL |
|---|---|---:|---:|---:|
| DT-GSK.docx | heading | 38 | 0 | 0 |
| DT-GSK.docx | heading_runin | 12 | 0 | 0 |
| DT-GSK.docx | caption | 23 | 1 | 0 |
| DT-GSK.docx | paragraph | 130 | 5 | 0 |
| DT-GSK.docx | table_authored | 8 | 7 | 0 |
| DT-GSK.docx | table_generated | 0 | 2 | 0 |
| DT-GSK.docx | table_pdf_spot | 2 | 0 | 0 |
| DT-GSK.docx | equation_display | **0** | **8** | 0 |
| DT-GSK.docx | bibliography_entry / inventory | 40 / 1 | 0 | 0 |
| DT-GSK.docx | citation_keys / numbers / pdf_render | 1 / 1 / 1 | 0 | 0 |
| DT-GSK.docx | toc | 0 | **1** | 0 |
| supplementary.docx | heading | 33 | 0 | 0 |
| supplementary.docx | caption | 50 | 0 | 0 |
| supplementary.docx | paragraph | 123 | 7 | 0 |
| supplementary.docx | table_generated | 1 | 16 | 0 |
| supplementary.docx | table_pdf_spot | 17 | 0 | 0 |
| supplementary.docx | equation_display | **0** | **2** | 0 |
| supplementary.docx | toc | 0 | **1** | 0 |
| both PDFs | no_ablation_scan | 2 | 0 | 0 |

`validate_evidence_bindings.py` (per the governance record) covers 267 `% BIND:` comments and
721 numeric tokens found identically in both rendered formats.

**The 0-FAIL headline is real but narrower than it looks.** Three of the rows above are
structurally incapable of failing, and one confirmed content divergence sits outside what the
validator inspects. Those are §§4–6.

## 3. Post-remediation propagation — R-01 … R-14 verified in BOTH formats

Independent verification that the 2026-07-21/22 remediation reached the rendered artifacts,
not just the sources:

| Ticket | Check | PDF | DOCX | Verdict |
|---|---|---|---|---|
| **R-01** Eq. (4) per-phase signs | OMML linearisation of the numbered display equation `(4)` | eq. (4) rendered | `junior: uᵢ = xᵢ + KF(x_R1−x_R2) + s_J(x_R3−xᵢ)`, `senior: uᵢ = xᵢ + KF(x_R1−x_R3) + s_S(x_R2−xᵢ)`, `s_J = +1 if f(xᵢ) > f(x_R3), else −1`, `s_S = +1 if f(xᵢ) > f(x_R2), else −1` | **CLOSED — both formats carry the signs** |
| **R-03** DOCX OMML literal `&` alignment markers | scan of every `m:t` run | n/a | main: 3,610 `m:t` runs, **0** literal `&` (28 hits are XML-escaped `&lt;`/`&gt;`); supplement: 2,220 runs, **0** (39 escaped) | **CLOSED — 0 alignment markers in both DOCX** |
| **R-05/R-14** budget-crossing semantics | the new sentence added in commit `45248eb31` | present (`performance.tex` → PDF) | probes `terminal generation`, `bit-identical for all seven`, `no search advantage`, `uncounted` all **True** in `DT-GSK.docx` | **CLOSED — source, PDF and Word in sync** |
| **R-06** supplement release identity | rendered release-tag inventory | `rel-2026-07-20-67d9345f9` ×3, `rel-2026-07-16-78f075cb0` ×2, `rel-2026-07-10-262fc16c9` ×2 | **identical counts** | **CLOSED — and cross-format identical** |
| **R-06** authority statement | `validate_provenance_claims.py` (hardened, exit 0) | "supplementary.pdf: no superseded authority claim; states the current release" | "supplementary.docx: no superseded authority claim; states the current release" | **CLOSED** |
| **R-07** hardened provenance gate | re-run in this review | exit 0, 12 `ok` lines including the rendered-artifact block `[1b]` | — | **CLOSED — the gate now reads rendered PDF *and* DOCX** |
| **R-08** three contributions | cover letter vs manuscript | abstract: "The contributions are the dimension-tiered adaptive control, the budget-exact refinement, and a reproducible within-family evaluation"; conclusions p.35: ISM "presented … rather than as a fourth claimed contribution" | cover letter p.1: "The paper makes three contributions" | **CLOSED — consistent across all three documents** |
| **R-09** cover letter | reviewer placeholder / byte-stability scope | no reviewer block; `cover_letter.tex` L74–75 documents that reviewer suggestions go through the submission system; "byte-stable determinism **for DT-GSK in the declared supported environment**" | — | **CLOSED** |

**Note on the two remaining superseded release tags.** `rel-2026-07-10-262fc16c9` and
`rel-2026-07-16-78f075cb0` still appear in the supplement, but each is explicitly framed as
historical ("*It has since been superseded in turn … and is retained*", "*which supersedes
rel-2026-07-16-78f075cb0*"). That is a legitimate supersession chain in a reproducibility
appendix, not a stale authority claim, and the hardened `validate_provenance_claims.py` agrees.
Whether seven hash-suffixed tags in reader-facing prose sits well against profile §10.17.4's
"one deliberately placed archival identifier" is an **authorship-presentation** question owned by
the Stage 13/15 seats; from the cross-format standpoint the two formats are identical and correct.

## 4. **S17-02 (Major) — the one confirmed content divergence: supplement Table A19**

Full detail in `pdf_build_report.md` §2. In cross-format terms:

| Source string (`parameter_table_detail.tex`) | in `supplementary.docx` | in `supplementary.pdf` |
|---|---|---|
| `cooldown 0.15; stop 0.9` | **yes** | **no** |
| `interaction_graph_min_dim=50` | **yes** | **no** |
| `interaction_graph_decay` | **yes** | **no** |
| `interaction_graph_lr` | **yes** | **no** |
| `window 30, percentile 0.50, floor 0.12` | **yes** | **no** |
| `final_polish_start_frac` | **yes** | **no** |
| `redundant guard; not an active mechanism` | **yes** | **no** |

Seven of seven `Notes` cells are present in Word and lost in the PDF, because the table overruns
the page by 218.99 pt (log) and its text extends to x = 598.8 pt on a 595.276 pt-wide page.

**Why the parity gate scored 0 FAIL on it.** The validator compares DOCX cells against the
**LaTeX source** (`check_authored_table` / `check_generated_table`), which agree — the DOCX is
faithful. Its only PDF-side table check, `spot_pdf` (L744–L760, emitting the `table_pdf_spot` rows),
samples **at most six purely numeric tokens per table** — from three rows only (first, middle,
last), first six cells each, filtered by `re.fullmatch(r"-?[\d.,]+(?:[eE][+-]?\d+)?%?", tok)` —
and tests containment in the PDF text. Table A19's `Notes` cells are prose, so they are never
probed. **The gate is structurally blind to non-numeric PDF truncation.** Fixing the table fixes
the divergence; hardening the probe would prevent the next one.

## 5. **S17-05 (Moderate, P2, CONFIRMED)** — the parity CSV publishes a false, unfailable TOC row

`papers/scripts/validate_cross_format_parity.py` L554–558 emits, **unconditionally, once per
document**, under the heading *"intentional format-only differences"*:

```python
rows.add(doc_id, "toc", "Contents (native TOC field)", "PASS_FORMAT_DIFF",
         "inventory",
         format_only="TOC exists only in DOCX (update-on-open); "
                     "PDF (MDPI submission layout) carries none")
```

`papers/governance/cross_format_consistency.csv` therefore carries two rows asserting that a
native, update-on-open TOC field exists in each DOCX. **Neither DOCX contains one.**
`validate_docx.py` on the same artifacts reports
`toc_field_absent: PASS — 0 TOC fields (expected 0: DOCX matches the no-TOC PDF)`, and the
field inventory confirms `field_TOC: 0` for both.

Two independent problems:

1. **The published statement is false.** A governance CSV that Gate P consumes now asserts a
   feature the artifact does not have.
2. **The row cannot fail.** It takes no measurement — status and text are literals. This is the
   same defect class that voided the 2026-07-21 freeze under ticket R-07 ("*A gate that cannot
   fail is not evidence*", `_pending_refreeze.json`), surviving in a sibling validator that
   R-07's hardening did not touch.

The same construction is used for `heading_number_typography` and `table_value_precision`. Those
two are genuine *recorded conventions* that remain true, so they are defensible as documentation
rows — but they share the property of being unfalsifiable and should be labelled as conventions
rather than scored as parity results.

**Required correction:** make the TOC row conditional on the measured field count (emit
`toc_absent_both` when 0/0, `FAIL` when the DOCX has a TOC the PDF lacks *and* the convention has
not been recorded), and relabel the two convention rows so they are not counted as parity
verdicts. **Post-revision verification:** the emitted TOC row's text matches the measured field
count; deliberately injecting a TOC field into a test copy flips the row.

## 6. **S17-06 (Moderate, P2, CONFIRMED)** — display-equation *content* parity is not verified

`validate_cross_format_parity.py` L451–L468 handles display-equation paragraphs as follows:

```python
mnum   = re.search(r"\((\w{1,4})\)\s*$", text.strip())
num_ok = bool(mnum) and f"({mnum.group(1)})" in pdf_squash
rows.add(doc_id, "equation_display", …,
         "PASS_FORMAT_DIFF" if (num_ok or not mnum) else "FAIL", …)
```

That is: the check verifies only that the **equation number** appears somewhere in the PDF text,
and **auto-passes any unnumbered display equation** (`or not mnum`). No comparison of the OMML
content against the LaTeX source or the PDF glyphs is performed. Consistent with this, every
equation row in the CSV is `PASS_FORMAT_DIFF` and **none is `PASS`**: 8/8 (main) and 2/2
(supplement).

The stated rationale — "*content equality is per-source: both formats render the same frozen
LaTeX math*" — is a reasonable design argument, but it is an argument, not a measurement, and it
does not hold when the two formats are produced by different toolchains. Ticket **R-03** is the
proof: a build-path defect had injected literal `&` alignment markers into the OMML, i.e. an
OMML-only content corruption. This check would not have caught it.

I verified the current state by hand instead (§3, R-01/R-03), and the OMML is correct. The
finding is that **the gate does not establish what its 0-FAIL headline implies**.

**Required correction (validator-only, no manuscript change):** compare a normalised symbol
channel — the ordered sequence of alphanumeric tokens and operator glyphs from the `m:t` runs
against the same channel extracted from the frozen LaTeX math — and score `PASS` on match,
`FAIL` on divergence; keep `PASS_FORMAT_DIFF` only for ordering/spacing differences. At minimum,
stop auto-passing unnumbered display equations.

## 7. Other cross-format checks — PASS

| Item | Result |
|---|---|
| Title | Identical in `main.tex`, PDF p.1, DOCX `dc:title`, PDF `/Title`, and the cover letter |
| Abstract | 197 words, identical text in the PDF, the DOCX and the PDF `/Subject` metadata |
| Keywords | 10 terms, identical in the PDF and PDF `/Keywords` |
| Section order | 38 headings matched (main) and 33 (supplement), plus 100 % PDF-outline coverage |
| Captions | 23 + 50 matched; one main-text `PASS_FORMAT_DIFF` (math glyph order in a caption) |
| Citations | 40 keys / 86 CITATION fields (main), 8 / 16 (supplement); cached numbers equal the frozen `.aux`; rendered forms found in the PDF |
| Bibliography | 40 + 8 entries matched entry-by-entry against the PDF |
| Declarations | All back-matter blocks present in both formats (content identical; **typography differs within the PDF itself** — `pdf_build_report.md` §6) |
| Supplement pointers | Main-text `Section S…` references (S2, S3, S5, S6.5, S6.7) all resolve; the supplement contains S1–S6 |
| Ablation scan | 0 hits in both PDFs and across all 26 / 46 DOCX parts; S6 renders in the supplement only |
| Numbers | 721/721 BIND-annotated numeric tokens found in both formats |

## 8. Minor cross-artifact inconsistencies

### 8.1 **S17-12 (Minor, P3, CONFIRMED)** — freeze manifest contradicts its own commit

`papers/governance/main_manuscript_freeze_manifest.json` →
`build_environment.docx_note`: *"committed deterministic renders via papers/scripts/build_docx.py;
**not re-emitted this pass**"*. The same commit `45248eb31` that re-minted this manifest changed
`papers/DT-GSK.docx` (**1,036,876 → 1,037,004 bytes**) and updated the manifest's own
`DT-GSK.docx` hash (`647028d5…` → `1ad8c3b2…`). The DOCX *was* re-emitted; only the note was
carried forward unchanged. The hashes are correct (`check_manifest` 15/15) — the prose is not.
**Correction:** update `docx_note` when the DOCX changes, or derive it from the diff.

### 8.2 **S17-11 (Minor, P3, CONFIRMED)** — three parallel numbering prefixes in the supplement

The supplement numbers its **sections** `S1`–`S6`, its **tables** `A1`–`A23`, and its **figures**
`B1`–`B27`. MDPI's supplementary convention is a single `S` prefix throughout
(`Table S1`, `Figure S1`). No dangling reference results — the main text cites supplement
*sections* only (0 occurrences of `Table A#`, `Figure B#`, `Table S#` or `Figure S#` in
`DT-GSK.pdf`) — but the A/B/S mix reads as an internal registry scheme rather than journal style
and will confuse a reader who tries to cite a supplement exhibit.
**Correction:** renumber supplement exhibits to `Table S1…` / `Figure S1…`, or state the scheme
in the supplement's opening paragraph.

### 8.3 Cover letter vs. abstract — scope wording (Minor, **SUSPECTED**, deferred)

The cover letter scopes the headline number explicitly — *"the best overall **CEC2017** Friedman
mean rank … (2.48 …; eGSK is second at 2.96)"* — while the abstract states *"Against six
GSK-family baselines on CEC2017 (primary), CEC2011, and CEC2013 … DT-GSK attains the best
overall Friedman mean rank in the seven-algorithm GSK-family panel (2.48, a descriptive
across-dimension mean)"*, where the three-suite preamble makes the suite scope of `2.48`
inferable rather than explicit. The abstract does immediately disclose the CEC2011 second place
and the Holm-significant loss, so nothing is concealed. Flagged as a **claim-scope wording**
observation for the claims seat, not a cross-format defect: the two documents state consistent
facts.

---

## 9. Ticket register (schema §5.4) — cross-format tickets

```text
ticket_id: S17-05
review_stage: 17
reviewer_role: PROD-WORD / T4-SOFT
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/scripts/validate_cross_format_parity.py L554-558; papers/governance/cross_format_consistency.csv (2 toc rows)
claim_id_or_artifact_id: cross-format parity attestation
concise_issue: The parity validator emits an unconditional TOC row asserting a native TOC field that neither DOCX contains, so a governance artifact publishes a false statement through a check that cannot fail.
exact_evidence_or_observation: L554-558 calls rows.add(doc_id,"toc","Contents (native TOC field)","PASS_FORMAT_DIFF","inventory", format_only="TOC exists only in DOCX (update-on-open); PDF (MDPI submission layout) carries none") with no measurement. validate_docx.py on the same artifacts reports toc_field_absent PASS "0 TOC fields (expected 0: DOCX matches the no-TOC PDF)" and field_TOC 0 for both packages.
root_cause: The row was written when a TOC existed and became a hard-coded literal; the TOC was later removed and validate_docx.py was updated to expect its absence, but the parity emitter and the CSV were not.
scientific_or_editorial_justification: Ticket R-07 voided a whole freeze on the principle that a gate which cannot fail is not evidence; the same construction survives here and now publishes a factually wrong statement.
impact_on_validity_or_acceptance: No effect on reported science. It degrades the parity attestation Gate P relies on and contradicts a sibling validator.
required_correction: Make the row conditional on the measured TOC field count and relabel the sibling convention rows (heading_number_typography, table_value_precision) so they are not scored as parity verdicts.
acceptable_alternatives: Delete the row and rely on validate_docx.py's toc_field_absent check.
additional_evidence_needed: None.
dependencies: S17-04 (the governance Word report repeats the same false TOC claim).
expected_improvement: The parity CSV states only measured facts; the R-07 defect class is eliminated from the sibling validator.
post_revision_verification: The emitted TOC row text matches the measured field count, and injecting a TOC field into a test copy flips the row.
status: open
```

```text
ticket_id: S17-06
review_stage: 17
reviewer_role: PROD-WORD / T4-SOFT
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/scripts/validate_cross_format_parity.py L451-L468
claim_id_or_artifact_id: equation_display parity rows (8 main + 2 supplement)
concise_issue: Display-equation parity verifies only that the equation NUMBER appears in the PDF and auto-passes unnumbered equations; no OMML content is ever compared, so the 0-FAIL headline overstates what was checked.
exact_evidence_or_observation: status = "PASS_FORMAT_DIFF" if (num_ok or not mnum) else "FAIL", where num_ok tests only that "(n)" occurs in the PDF text. Every equation row in cross_format_consistency.csv is PASS_FORMAT_DIFF and none is PASS (8/8 main, 2/2 supplement). Ticket R-03 is the counterexample: literal "&" alignment markers had been injected into the OMML by the build path - an OMML-only corruption this check cannot see.
root_cause: The check was designed around the argument that both formats derive from the same frozen LaTeX, so content equality was assumed rather than measured.
scientific_or_editorial_justification: Stage 17 requires cross-format comparison of equations; profile 10.12 requires the formats to agree on all scientific content. An assumption is not a comparison, and the toolchains differ.
impact_on_validity_or_acceptance: No current defect - I verified Eq.(4) and the absence of "&" markers by hand and both are correct. The risk is that the next OMML regression ships undetected.
required_correction: Compare a normalised symbol channel (ordered alphanumeric tokens and operator glyphs from m:t runs versus the same channel from the frozen LaTeX math), scoring PASS on match and FAIL on divergence; at minimum stop auto-passing unnumbered display equations.
acceptable_alternatives: Keep the current check but relabel these rows as "not content-verified" so the 0-FAIL total is not read as equation parity.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Equation content becomes machine-verified across formats rather than assumed.
post_revision_verification: Equation rows report PASS on the current build, and a deliberately corrupted OMML run turns them FAIL.
status: open
```

```text
ticket_id: S17-11
review_stage: 17
reviewer_role: JCO / T5-WRITE
severity: Minor
priority: P3
confidence: Confirmed
issue_type: production
manuscript_location: papers/supplementary.pdf and .docx (all exhibit captions)
claim_id_or_artifact_id: supplementary exhibit numbering
concise_issue: The supplement uses three parallel prefixes - sections S1-S6, tables A1-A23, figures B1-B27 - against MDPI's single S-prefixed supplementary convention.
exact_evidence_or_observation: Rendered supplement caption inventory: Table A1..A23 and Figure B1..B27 within sections S1..S6. The main text cites supplement sections only (0 occurrences of "Table A#", "Figure B#", "Table S#", "Figure S#" in DT-GSK.pdf), so no dangling reference exists.
root_cause: Appendix-style A/B counters inherited from the build scaffolding rather than the journal's supplementary convention.
scientific_or_editorial_justification: MDPI supplementary materials number exhibits with an S prefix; three prefixes read as an internal registry scheme.
impact_on_validity_or_acceptance: Low; a reader wanting to cite a supplement exhibit has to guess the scheme.
required_correction: Renumber supplement exhibits as Table S1.. / Figure S1.., or state the scheme explicitly in the supplement's opening paragraph.
acceptable_alternatives: Keep A/B and add one sentence defining it.
additional_evidence_needed: Confirmation of the journal's supplementary numbering rule - depends on S17-16.
dependencies: S17-16.
expected_improvement: Supplement matches house style and becomes citable without ambiguity.
post_revision_verification: All supplement exhibits carry a single consistent prefix, or the scheme is stated.
status: open
```

```text
ticket_id: S17-12
review_stage: 17
reviewer_role: PROD-WORD
severity: Minor
priority: P3
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/governance/main_manuscript_freeze_manifest.json -> build_environment.docx_note
claim_id_or_artifact_id: freeze provenance record
concise_issue: The freeze manifest states the DOCX renders were "not re-emitted this pass" in the same commit that re-emitted DT-GSK.docx.
exact_evidence_or_observation: git show --stat 45248eb31 lists papers/DT-GSK.docx Bin 1036876 -> 1037004 bytes, and the manifest diff in that commit updates the DT-GSK.docx sha256 from 647028d5.. to 1ad8c3b2..; docx_note is unchanged and still reads "committed deterministic renders via papers/scripts/build_docx.py; not re-emitted this pass".
root_cause: A carried-forward free-text field in a hand-minted manifest.
scientific_or_editorial_justification: The freeze manifest is the provenance record of record; a false statement in it undermines the audit trail even when the hashes are right.
impact_on_validity_or_acceptance: None on the science; the recorded hashes are correct and check_manifest passes 15/15.
required_correction: Update docx_note whenever the DOCX bytes change, or derive it from the commit diff.
acceptable_alternatives: Delete the free-text note and rely on the per-file hashes.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: The freeze record stops contradicting its own commit.
post_revision_verification: docx_note describes the actual emission state of the DOCX in the minting commit.
status: open
```

---

## 10. Cross-format verdict

**One confirmed content divergence (S17-02, PDF-side truncation of supplement Table A19) and one
confirmed typographic divergence (S17-03, page margins). Everything else the review could measure
agrees across source, PDF and Word — including all eight remediation tickets checked in §3.**

The residual concern is not that the formats disagree, but that **two of the checks that certify
they agree cannot fail** (S17-05, S17-06) and a third is blind to non-numeric PDF truncation
(§4). Those are validator-only fixes; none requires a rerun, a new evidence release, or any change
to a reported number.
