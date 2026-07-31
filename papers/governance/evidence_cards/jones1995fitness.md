# Evidence card — jones1995fitness

## Verified bibliographic identity
- Title: Fitness Distance Correlation as a Measure of Problem Difficulty for
  Genetic Algorithms
- Authors: Terry Jones, Stephanie Forrest
- Local version: Santa Fe Institute Working Paper 1995-02-022 (cover page,
  PDF p. 1). The BibTeX entry cites the ICGA-6 proceedings version (Morgan
  Kaufmann, pp. 184-192).
- Identity status (reference_inventory.csv): `minor_metadata_mismatch` —
  identity of the work is certain (title and both authors match), but the
  local copy is the working-paper VERSION, so proceedings page numbers
  184-192 MUST NOT be used as locators.
- Local file: `reference_papers/jones1995fitness.pdf`, 10 pages. Text layer is
  character-spaced/garbled but legible.
- Page-locator convention for this card: **PDF page numbers (1-10)**; PDF p. 1
  is the SFI cover, paper body is PDF pp. 2-10. Section numbers are stable
  across versions and preferred.

## Research question and context
Can the correlation between fitness and distance-to-goal predict how difficult
a problem is for a genetic algorithm (GA)? The measure arises from viewing GA
fitness functions as heuristic functions in state-space search (Abstract and
Sect. 1, PDF p. 2; Sect. 3, PDF p. 3).

## Method and experimental scope
- Definition: fitness distance correlation (FDC) is the sample correlation
  coefficient r between the set F of individual fitnesses and the set D of
  distances to the nearest global maximum, r = c_FD / (s_F s_D); Hamming
  distance is used throughout; ideal is r = -1.0 when maximizing (Sect. 3,
  PDF p. 3).
- Computation: exhaustive when the space has <= 2^12 points, otherwise a
  random sample of 4000 points; sampling variance of r reported as very small
  in a spot check (Sect. 4, PDF pp. 3-4).
- Test battery: GA problems of known difficulty — deceptive functions (Deb &
  Goldberg 6-bit; Whitley 4-bit; Goldberg-Korb-Deb 3-bit), Ackley functions
  (One Max, Two Max, Trap, Porcupine, Plateau, Mix), NK landscapes, long path,
  needle-in-a-haystack, busy beaver, De Jong F1-F5 in binary and Gray
  encodings, Tanese functions, royal road R1/R2 (Table 1, PDF p. 6; Figure 1,
  PDF p. 5; scatter plots Figure 2, PDF p. 7).
- Classification rule used: misleading (r >= 0.15), difficult
  (-0.15 < r < 0.15), straightforward (r <= -0.15) (Sect. 4, PDF p. 4).

## Conservative findings (with exact locators)
1. FDC correctly classifies many known-easy and known-hard GA problems,
   including classifying easy deceptive problems as easy and difficult
   non-deceptive problems as difficult (Abstract, PDF p. 2; Sect. 4.1,
   PDF p. 4).
2. FDC is consistent with previously surprising results on Tanese functions
   and royal road functions (Sect. 4.2, PDF pp. 5-6).
3. FDC predicted encoding effects: whether Gray or binary coding is easier
   depends on the number of bits per variable, later matched by GA runs
   (Sect. 4.3.2, PDF pp. 6-8; summary Sect. 6, PDF p. 9).
4. Correlation is explicitly an imperfect summary: cases documented where r
   near 0 hides exploitable structure and a fitness-distance SCATTER PLOT
   reveals it (long path, Sect. 4.1.3, PDF p. 4; De Jong F2 cliffs, Sect.
   4.1.4, PDF pp. 4-5; Liepins-Vose transform, Sect. 4.3.1, PDF pp. 6-7).
5. FDC requires KNOWN global optima (distance to nearest global optimum);
   it "can only indicate how hard it is to locate what one is interested in
   locating" and was not proposed for prediction on unknown-solution
   functions (Sect. 5, PDF p. 8).
6. Hamming distance is only an approximation to distance under the actual
   search operators; operator-aware distances are conjectured to predict
   better (Sect. 3, PDF p. 3; Sect. 5, PDF p. 9).

## Limitations relevant to citation
- Binary/Hamming GA setting; no continuous benchmark functions, no CEC
  suites, no direct transfer to real-parameter optimizers.
- Predictive claims are empirical over the listed problem battery, not
  theoretical guarantees; the authors themselves call FDC "reliable, although
  not infallible" (Sect. 6, PDF p. 9).
- Needs known global optima; sampling-based FDC on subsets of optima can be
  misleading (Sect. 5, PDF p. 8).

## Supported uses in the DT-GSK manuscript
- Citing the concept and definition of fitness-distance correlation as an
  established landscape-difficulty measure (Sect. 3, PDF p. 3).
- Citing the observation that the fitness-distance relationship strongly
  influences search difficulty for evolutionary algorithms (Abstract PDF
  p. 2; Sect. 6, PDF p. 9).
- If any DT-GSK component or any cited family baseline (e.g., the
  fitness-distance-balance lineage in `fdbagsk2023`) is DISCUSSED in terms of
  fitness-distance reasoning, this is the sanctioned root citation for the
  fitness-distance idea — Appendix B.6 restricts use to "fitness-distance
  basis only where verified".

## Unsupported / prohibited overextensions
- Do NOT cite as evidence that any fitness-distance-based mechanism improves
  optimizer performance; the paper measures problem difficulty, it does not
  propose or test an operator.
- Do NOT claim FDC applies as-is to continuous domains or to CEC benchmark
  functions; all evidence is on bit-string problems with Hamming distance.
- Do NOT equate FDC with the "fitness-distance balance" (FDB) selection
  method used in FDB-AGSK; they are different constructs (FDB must be
  grounded in `fdbagsk2023`).
- Do NOT cite ICGA-6 proceedings page numbers (184-192); the local copy is
  the working paper.

## Role in DT-GSK framing (Appendix B.6)
Landscape/fitness-distance conceptual basis only where verified. Expected use
is at most one or two related-work/motivation sentences; it is not evidence
for any DT-GSK mechanism.

## Verification quotation (identity)
"A measure of search difficulty, fitness distance correlation (FDC), is
introduced and examined in relation to genetic algorithm (GA) performance"
(Abstract, PDF p. 2).
