# Evidence card: awad2016problem — ADMISSIBLE (resolved CR-0005)

**Status: ADMISSIBLE. The correct CEC2017 bound-constrained problem-definitions report is
now in the corpus.** Supersedes the prior BLOCKED stub (wrong document). Resolution:
change_request_register.csv CR-0005 (2026-07-10); evidence gap EG-001 CLOSED.

## 1. Verified bibliographic identity
- **identity_status (reference_inventory.csv): `verified` — admissible = yes.**
- **BibTeX** (`references.bib`, key `awad2016problem`): Awad, N. H.; Ali, M. Z.; Liang, J. J.;
  Qu, B. Y.; Suganthan, P. N., "Problem Definitions and Evaluation Criteria for the CEC 2017
  Special Session and Competition on Single Objective Real-Parameter Numerical Optimization,"
  Technical Report, Nanyang Technological University, Singapore, 2016.
- **Local file** `reference_papers/awad2016problem.pdf` — 34 pp., sha256
  `b69f52f047f6bca888787ac19f3f1224293000c0a2446bdd5c355795efa9684a`.
- **Title page** (p.1) reads: "Problem Definitions and Evaluation Criteria for the CEC 2017
  Special Session and Competition on Single Objective Real-Parameter Numerical Optimization";
  authors N. H. Awad, M. Z. Ali, P. N. Suganthan, J. J. Liang, B. Y. Qu (NTU Singapore /
  Jordan Univ. of Science and Technology / Zhengzhou University); "Modified on October 15th
  2016." Title-page author order lists Suganthan third; the bib uses the conventional
  citation order (Awad, Ali, Liang, Qu, Suganthan) — acceptable, same authors.
- **Distinguished from the wrong document:** title contains **no** "Constrained"; it is the
  **bound-constrained** (box-constrained) single-objective suite, not the constrained-
  optimization competition report by Wu/Mallipeddi/Suganthan that previously occupied this key.

## 2. Content verification (full-text, this session)
Certified by full-text scan of all 34 pages:
- **F1–F30** benchmark functions present.
- Function **categories**: unimodal, multimodal, hybrid, composition (all four present).
- **Search range** [-100, 100]^D present.
- **MaxFES = 10000·D** protocol present.
- **No** constraint functions (no inequality/equality g/h constraint machinery) — confirming
  bound-constrained, not constrained.

## 3. Admissible citation uses (CEC2017 suite-definition role, Appendix B.4)
This report is now the authoritative source for the DT-GSK CEC2017 experimental section:
- the 30-function single-objective **bound-constrained** benchmark and its
  unimodal/multimodal/hybrid/composition taxonomy;
- the **search range** [-100,100]^D and shift/rotation transformation scheme;
- the **evaluation protocol**: 51 runs, dimensions D ∈ {10,30,50,100}, MaxFES = 10000·D,
  error-value recording, the error < 1e-8 → 0 convention, and the algorithm-complexity
  protocol (T0/T1/T2 timing).

> Locators to confirm at prose time (Phase 8): cite specific page numbers for the function
> table, search range, and protocol paragraphs when the exact claim is written; the whole-
> document markers above are verified, page-precise locators are added per claim in Phase 8.

## 4. Relationship to other admissible cards
- `awad2017ensemble` and `brest2017single` remain valid for **participant-side** protocol
  descriptions and the CEC2017 scoring formula; with EG-001 closed they are now
  *corroborating* sources rather than the *interim substitute* the block previously forced.

## 5. Provenance of resolution
- Prior state: STUB / INADMISSIBLE (local PDF was Wu/Mallipeddi/Suganthan constrained
  report, sha `5a18eb76…`, 16 pp.). See EG-001 history and CR-0005.
- Correct report supplied by the user 2026-07-10; identity + content verified above;
  `reference_inventory.csv` updated to `verified`; key added to
  `allowed_citation_keys.txt` (56 → 57).
