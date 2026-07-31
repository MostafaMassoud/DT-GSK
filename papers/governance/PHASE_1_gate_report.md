# PHASE 1 gate report — Closed literature-corpus audit and evidence-card construction

Gate run: 2026-07-10. Anchor commit `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21` (Gate 0
FROZEN; HEAD verified == anchor at gate time). Authority: closed corpus only —
`reference_papers/*.pdf` + `papers/references.bib`. Master framework Phase 1
(Validation procedures, Verification procedures, QA checkpoints, Acceptance criteria,
Review gate) executed as written; master read in the working tree carrying CR-0001/0002/0003.

**VERDICT: GATE 1 PASS — Phase 1 FROZEN.** Approvers per the master's Review gate:
P2 + P3 + P4 + P9 (Section 7 below). No intended rendered citation lacks a verified
local source (the one unverifiable key is excluded from the runtime set and hard-blocked
in every downstream artifact).

---

## 1. Headline numbers (Deliverables requirement)

| Quantity | Value |
|---|---|
| BibTeX entries (`papers/references.bib`) | 57 (0 duplicates; 0 non-ASCII bytes — file is pure ASCII) |
| Appendix A expected keys | 57; exact 1:1 match with bib keys (0 missing, 0 extras) |
| `reference_inventory.csv` rows | 57 — every BibTeX key counted exactly once |
| **Admissible runtime set (`allowed_citation_keys.txt`)** | **56** |
| Missing expected keys (admissible) | 1 — `awad2016problem` (WRONG local document; blocked) |
| Evidence cards | 57 files (56 full admissible cards + 1 inadmissible stub) |
| `citation_role_map.csv` | 56 rows (admissible keys only), 9 columns |
| `word_citation_tag_map.csv` | 57 rows (56 ready + 1 `BLOCKED_do_not_generate_word_source`) |
| Major evidence gaps | 13 seeded (EG-001 … EG-013); EG-001 is the sole blocking literature gap |
| Approved source roles | 56 role rows across Appendix B groups: B.1=6, B.2=13, B.3=8, B.4=4 (of 5; blocked key excluded), B.5=8, B.6=4, B.7=2, B.8=8, B.9=3 |

## 2. Validation procedures (master Phase 1) — all PASS

Independent re-execution at gate time (scripted; scratchpad only, no repo pollution):

1. **CSV schema validation.**
   - `reference_inventory.csv`: header == the 19-column Section 3.3 schema, byte-exact. PASS.
   - `citation_role_map.csv`: 9 columns (`citation_key, appendix_b_group, appendix_b_role,
     sanctioned_uses, prohibited_overextensions, usage_condition, evidence_card,
     identity_status, notes`); required cells non-empty; every `evidence_card` path resolves. PASS.
   - `word_citation_tag_map.csv`: 9 columns; 57 unique tags, all matching
     `^[A-Za-z][A-Za-z0-9_]*$` (bibkey-identity scheme); entry-type → Word-source-type map present. PASS.
   - `allowed_citation_keys.txt`: 56 keys, sorted, unique. PASS.
2. **Every BibTeX key exactly once:** 57 bib keys == 57 inventory `citation_key` values,
   no duplicates, no omissions (set-diff empty both directions). PASS.
3. **Every admissible key has one readable source + one evidence card:** all 56
   `admissible=yes` rows have `readability_status` recorded, a present local file, and a
   card in `evidence_cards/<key>.md`; all 56 cards carry the Section 3.4 required
   elements (identity, research question, method/scope, findings, limitations,
   unsupported uses, DT-GSK relevance) and exact locators. PASS.
   (Readability qualifications preserved: `nelder1965simplex` image-only — card forbids
   verbatim quotes; `david_order_statistics` partial-text excerpt — visual locators,
   Ch. 7 pp. 159–170 only. Both consolidated in EG-009.)
4. **Locator resolution:** card locator schemes are pinned to the local copies'
   pagination; independently exercised on the stratified sample (Section 3). PASS.
5. **Identity-status vocabulary:** all values within the Section 3.3 allowed set
   (40 `verified`, 16 `minor_metadata_mismatch`, 1 `major_mismatch`); every
   `major_mismatch` row is `admissible=no`; every mismatch row carries a disposition
   in `notes`. PASS.

## 3. Verification procedures — all PASS

### 3.1 P9 stratified identity/locator sample (8 keys, 12 locators — 12/12 resolve)

Sample stratification per the gate instruction: 2 statistics + 2 GSK family + 1 book +
3 further groups (benchmark, variant/hybrid, local search). Each PDF re-opened with
pypdf; the quoted content confirmed on the stated page of the local copy.

| Key (group) | Locator checked | Result |
|---|---|---|
| demsar2006statistical (B.8 statistics) | Abstract quote, p. 1 (both halves of the ellipsised quotation) | PASS (p. 1) |
| demsar2006statistical (B.8 statistics) | "Holm's procedure is more powerful than the Bonferroni-Dunn's…", p. 13 | PASS (p. 13) |
| holm1979simple (B.8 statistics) | Title header, printed p. 65 / PDF p. 2 | PASS (PDF p. 2) |
| mohamed2020gaining (B.1 family) | "GSK gets the first ranking among all algorithms", Sect. 4, PDF p. 21 | PASS (p. 21) |
| mohamed2020gaining (B.1 family) | f2-exclusion sentence, PDF p. 11 | PASS (p. 11) |
| apgsk2021 (B.1 family) | "runner up in CEC2020 competition", Sect. I, printed p. 65936 | PASS (PDF p. 2) |
| apgsk2021 (B.1 family) | source-code URL, Sect. V, printed p. 65944 | PASS (PDF p. 11; printed page number 65944 confirmed on the same page) |
| efron1993introduction (book) | Title page + series-list entry, PDF pp. 3–5 | PASS (PDF p. 3) |
| liang2013cec2013 (B.4 benchmark) | 51 runs / MaxFES 10000\*D / 1e-8 termination, PDF p. 35 | PASS (p. 35, both needles) |
| pogsk2023 (B.2 variant) | Abstract quote (subpopulation + OBL design), p. 1 | PASS (p. 1) |
| gao2012implementing (B.6 local search) | Abstract quote (dimension-dependent NM parameters), PDF p. 1 | PASS (p. 1) |

Note: two needles initially failed a naive character-normalized match because the PDFs
encode fi/fl ligatures (U+FB01 etc.) in the text layer; with ligature-aware
normalization both match on the exact stated pages. Extraction artifact only — no
locator defect.

### 3.2 External-URL / snippet contamination scan

`grep` of `evidence_cards/` for `http://` and `https://`:

- 2 hits on `doi.org` (del2019bio.md, hussain2019metaheuristic.md) — both inside
  identity verification quotations of what is printed on p. 1 of the local PDFs.
  DOI-in-metadata mentions: fine per the gate instruction.
- 1 hit `https://sites.google.com/view/optimization-project/files` (apgsk2021.md) —
  verified at gate time to be the APGSK paper's own printed source-code link
  (PDF p. 11 = printed p. 65944, Sect. V), quoted with locator. This is corpus
  content, not external material. **No external scientific URL, snippet, or
  unapproved source contaminates any card. PASS.**

### 3.3 Checksum verification

- Required 10-file sample re-hashed (SHA-256) against `reference_inventory.csv`:
  demsar2006statistical, holm1979simple, mohamed2020gaining, apgsk2021,
  efron1993introduction, liang2013cec2013, pogsk2023, gao2012implementing,
  awad2016problem, nelder1965simplex — 10/10 match. PASS.
- Strengthened at gate time: full 57-file re-hash — 57/57 match, 0 missing files. PASS.

### 3.4 Explicit status for every expected key

All 57 inventory rows carry non-empty `identity_status`, `readability_status`, and
`admissible`; the one inadmissible key (`awad2016problem`) additionally carries the
WRONG-DOCUMENT disposition in `notes`, a stub card, a BLOCKED Word-tag row, and gap
EG-001. PASS.

## 4. QA checkpoints — persona sign-offs

- **P2 (algorithm theorist) — method-lineage cards (B.1/B.2/B.3): APPROVE.**
  Spot-reviewed `mohamed2020gaining` (full read), `storn1997differential`,
  `pogsk2023` role rows. The foundational GSK card reconstructs the exact junior/senior
  mechanics (Eq. 1, Figs. 7–10, Table 6 parameters) with per-claim locators, pins the
  locator convention to the online-first PDF (no journal pagination — correctly
  forbidden), and scopes the "first ranking" claim to the 10-comparator panel. Variant
  cards gate use to verified-mechanism discussion (no decorative citations).
- **P3 (statistics lead) — statistical cards (B.8): APPROVE.**
  Spot-reviewed `demsar2006statistical` (full read), `holm1979simple`,
  `david_order_statistics`, `efron1993introduction`. Test formulas, applicability
  assumptions, and prohibited overextensions (no Nemenyi for control designs, no
  per-run pseudo-replication into Friedman, BCa attribution-only per EG-003,
  excerpt-bounded book use per EG-009) are correctly and conservatively recorded.
- **P4 (benchmark/data engineer) — benchmark-source cards (B.4): APPROVE.**
  Spot-reviewed `das2011cec2011` (2010 title-page date correctly dispositioned),
  `liang2013cec2013` (protocol locators verified on PDF p. 35), and the
  `awad2016problem` stub (wrong-document finding is accurate: local file is the CEC2017
  CONSTRAINED report by Wu/Mallipeddi/Suganthan, not the cited single-objective report).
  The interim narrow path (participant protocol descriptions via `awad2017ensemble` /
  `brest2017single`, never as suite definition) is sound.
- **P6 (scientific writer/editor) — citation-role wording: APPROVE.**
  `citation_role_map.csv` wording stays within Appendix B boundaries; every row pairs
  sanctioned uses with explicit prohibited overextensions; conditional keys carry usage
  gates; the "no key is required to appear in final prose" rule is encoded, defusing
  the all-57 decorative-citation risk.
- **P8 (Word/OOXML specialist) — stable Word tags: APPROVE.**
  57 deterministic bibkey-identity tags, unique, `^[A-Za-z][A-Za-z0-9_]*$`-valid,
  stable across builds; entry-type → `b:Sources` type mapping recorded; generation
  correctly deferred to the Word build phase; the blocked key cannot silently reach the
  Word source store (`BLOCKED_do_not_generate_word_source`).
- **P9 (research-integrity auditor) — identity sample + closed-corpus compliance: APPROVE.**
  Section 3 results; additionally: no memory-completed or fictional metadata found —
  every bib-metadata correction in the audit report is sourced to printed pages of the
  local files, bib fixes are queued for change control (references.bib untouched), and
  the two low-fidelity copies carry explicit no-verbatim-quote restrictions.

## 5. Acceptance criteria walk — 7/7 PASS

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | All BibTeX entries audited | PASS | 57/57 keys in inventory exactly once; strict parse 0 problems (audit report Sect. 7; independent 57-entry re-parse at gate time) |
| 2 | All literature files inventoried | PASS | 57 PDFs enumerated with format/page_count/SHA-256; 57/57 hashes re-verified at gate time |
| 3 | Runtime citation set explicit | PASS | `allowed_citation_keys.txt` = 56 keys == inventory `admissible=yes` set, sorted/unique |
| 4 | Every admissible source has a complete evidence card | PASS | 56/56 cards with all Section 3.4 elements + exact locators (scripted check + persona spot-reads) |
| 5 | Every mismatch has a disposition | PASS | 16 minor mismatches resolved from printed pages (inventory notes; audit report Sect. 4); 1 major mismatch blocked (stub card Sect. 6 resolution path; EG-001) |
| 6 | Unsupported claims entered in gap register | PASS | 13 gaps EG-001…EG-013 with Section 3.6 fields and allowed-vocabulary dispositions; empirical gaps EG-004/005/006 artifact-verified |
| 7 | No fictional or externally completed metadata | PASS | Closed-corpus discipline verified: URL scan clean (Sect. 3.2), corrections sourced to local printed pages, no web access, references.bib unmodified (pure ASCII, 57 entries, byte-identical to anchor expectations) |

## 6. Traceability-patch outcome (Backbone phase — CR-0001/0002 rerun evidence)

Recorded per the gate instruction as the CR-0001/0002 rerun evidence:

- **CR-0001/0002 re-patch: DONE and verified.** After the two approved post-Gate-0
  master amendments (D-0005 second entry: master 7,472 → 7,585 lines),
  `source_line_traceability.csv` was re-patched from 5,880 to **5,985 rows** with
  `max(line_no) = 7,585` — exactly the amended master's final line. Gate-time checks:
  0 duplicate `line_no`, 0 `unmapped`/`partial`/`unknown` classifications, 0 dangling
  requirement references. `requirements_traceability_matrix.csv` grew 2,105 → **2,126
  unique requirement IDs** (21 requirements added by the CR-0001/0002 ranges), 0
  duplicates, 0 orphans.
- **CR-0003 re-patch: OUTSTANDING (open item, not a Phase 1 criterion).** CR-0003
  (approved, D-0006) further amended the master to its current working-tree state of
  7,759 total / 6,146 nonblank lines; the traceability files still index the 7,585-line
  post-CR-0001/0002 version (1,404 current nonblank lines uncovered / 1,243 rows now
  pointing at shifted line numbers — pure line-shift effect of the CR-0003 insertions).
  CR-0003's own `rerun_plan` ("traceability re-patch after application") must be
  executed by the backbone owner before any consumer resolves `line_text` by `line_no`
  against the current master. This is CR-0003 rerun debt against the Phase 0 backbone,
  outside Phase 1's validation/acceptance scope; it does not gate Phase 1 freezing and
  does not touch Phase 2's entry criteria, but it is flagged here so it cannot silently
  age. Until re-patched, `line_no` resolution MUST use the post-CR-0001/0002 master
  revision recorded in D-0005/D-0006.

## 7. Review gate — Gate 1 decision

Master Phase 1 Review gate: "P2 + P3 + P4 + P9 approve. Any intended rendered citation
without a verified local source is a hard failure."

- P2 APPROVE, P3 APPROVE, P4 APPROVE, P9 APPROVE (Section 4).
- Hard-failure check: the only unverifiable source (`awad2016problem`) is excluded from
  the runtime set, stripped from the role map, BLOCKED in the Word tag map, and gap-
  registered (EG-001) — no rendering path can cite it. No hard failure.
- Register note: the Phase 1 `gate_approvers` seed value (`P1;P2;P5`) predates the gate
  and is corrected to the master's Review-gate signatories `P2;P3;P4;P9` in this run.

**Phase 1 state: FROZEN (2026-07-10).** Reopening requires a
`change_request_register.csv` row per Section 12.2.

## 8. Open items carried forward (non-blocking for Gate 1)

1. **EG-001 / awad2016problem** — supply the correct Awad et al. (2016) NTU
   single-objective report locally, re-inventory, replace the stub, extend the allowed
   set to 57. Needed before CEC2017 suite-definition prose (Phase 4/8); interim narrow
   path documented.
2. **references.bib metadata corrections** (16 minor mismatches, audit report Sect. 4) —
   queued for the change-request pipeline; references.bib is a scientific artifact and
   was not edited in Phase 1.
3. **CR-0003 traceability re-patch** (Section 6) — backbone owner; before any
   line_no-based consumption of the current master.
4. **EG-004/005/006** (memory harness, GenLog release, parametric sweep) — pre-declared
   empirical known gaps; Phase 2 tooling window.
