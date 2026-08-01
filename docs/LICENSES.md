# Licenses and Provenance

This file records the license and provenance of the Python implementation of the
GSK optimizer family. It is one of the two `license-files` targets declared in
`pyproject.toml` (`license = "MIT"`, `license-files = ["LICENSE", "docs/LICENSES.md"]`).

> **License status: settled and final (author-confirmed 2026-07-14; copyright
> line confirmed 2026-08-01).** The code is licensed under the MIT License, an
> OSI-approved open-source licence; the authors' own derived data and analysis
> artifacts are licensed under CC BY 4.0.
> Third-party benchmark definitions remain under their upstream terms (below).

## Project license

- **Code:** MIT License. The full grant text and copyright line are in the
  root `LICENSE` file; `pyproject.toml` declares `license = "MIT"` and points
  `license-files` at both `LICENSE` and this document.
- **Copyright:** Copyright (c) 2026 by the authors.
- **Data and derived artifacts (authored by us):** the per-run result CSVs, seed
  schedules, analysis bundles, and verification manifests we produced are
  released under the Creative Commons Attribution 4.0 International
  (CC BY 4.0) License.
- **Benchmark definitions (third party):** the CEC2017/CEC2011/CEC2013/
  CEC2020/CEC2013LSGO problem definitions are the property of their respective
  authors and are used under their original terms; we do not relicense them. The CC BY 4.0 grant above
  applies only to our own derived data, not to these upstream definitions.
- The manuscript Data Availability Statement is written to match this record.

## Third-party dependencies

The runtime depends on the packages below, each distributed under its own
upstream license (consult each project for the authoritative text):

| Package | Usual license |
|---|---|
| NumPy | BSD-3-Clause |
| SciPy | BSD-3-Clause |
| pandas | BSD-3-Clause |
| matplotlib | Matplotlib (BSD-style) |
| PyYAML | MIT |
| Numba | BSD-2-Clause |

These are well-known permissive licenses; redistribution of this project must
preserve their notices. Version ranges are pinned in `pyproject.toml` and
`requirements.txt` (with the dev tooling in `requirements-dev.txt`). "Usual
license" reflects the customary upstream license at the time of writing;
maintainers should confirm the exact license shipped with the pinned version of
each package before redistribution, because upstream projects can relicense.

## Benchmark and reference evidence provenance

- The active benchmark runtime is the bundled Python benchmark suite under
  `benchmarks/cec_suite_python/`. It is the default evaluator for all normal
  runs (benchmark backend `auto`).
- Imported reference summary tables under `benchmarks/cec_reference_results/`
  are **read-only** validation evidence with their own provenance, organized as
  `<suite>/<optimizer>/`. The runner refuses to write generated output into this
  tree, and it must not be edited to make generated output pass validation.
- The `egsk` data under `benchmarks/cec_reference_results/<suite>/egsk/` is the
  committed comparator of record: it is one of the GSK-family comparators used by
  the statistical suite and the paper review pack, and the statistical panel
  reports `egsk` from these committed CSVs, which are the **Python (`scipy`-SLSQP)
  port run** (`src/gsk_family/optimizers/egsk.py`, a MATLAB port whose
  interior-point refinement uses `scipy`-SLSQP in place of `fmincon`), not a
  MATLAB `fmincon` reference. The panel reads these committed CSVs, not a fresh
  local run, so panel numbers are fixed and reproducible.
- Generated experiment output belongs under `results/` (default
  `results/_run_all/<optimizer>/<suite>/`, or another user-selected output root)
  outside the reference evidence.
- The **cited literature** is indexed under `reference_papers/` (the table there
  is generated from `papers/references.bib`). Those source PDFs are third-party
  copyrighted works and are **not committed** to the repository; obtain each via
  its DOI and keep only copies your license permits redistributing.

## Reproduction scope (no over-claim)

The optimizer kernels are **behavior-compatible** with the originating research
codebase at the algorithm and experiment-contract level. This project does
**not** claim bit-exact replay across platforms, nor full statistical
equivalence to published tables: reduced-budget runs are consistency checks
only, and statistical-equivalence reporting is listed as outstanding work. See
  [Validation Report](research/validation_report.md) and
  [Reproducibility](research/reproducibility.md) for the exact evidence and its
  limits.

## Attribution

Code author: **Mostafa Masoud** (`moustafa.masoud@gmail.com`).

Citation metadata for this software package is in `CITATION.cff` at the
repository root. Algorithm papers should be cited according to the optimizer
used in an experiment:

| Optimizer ID | Reference |
|---|---|
| `gsk` | Mohamed, A. W.; Hadi, A. A.; Mohamed, A. K. "Gaining-sharing knowledge based algorithm for solving optimization problems: a novel nature-inspired algorithm." International Journal of Machine Learning and Cybernetics, 11, 1501-1529, 2020. DOI: [10.1007/s13042-019-01053-x](https://doi.org/10.1007/s13042-019-01053-x). |
| `agsk` | Mohamed, A. W.; Hadi, A. A.; Mohamed, A. K.; Awad, N. H. "Evaluating the performance of adaptive gaining-sharing knowledge based algorithm on CEC 2020 benchmark problems." 2020 IEEE Congress on Evolutionary Computation (CEC), 1-8, 2020. DOI: [10.1109/CEC48606.2020.9185901](https://doi.org/10.1109/CEC48606.2020.9185901). |
| `apgsk` | Mohamed, A. W.; Abutarboush, H. F.; Hadi, A. A.; Mohamed, A. K. "Gaining-sharing knowledge based algorithm with adaptive parameters for engineering optimization." IEEE Access, 9, 65934-65946, 2021. DOI: [10.1109/ACCESS.2021.3076091](https://doi.org/10.1109/ACCESS.2021.3076091). |
| `fdb-agsk` | Bakir, H.; Duman, S.; Guvenc, U.; Kahraman, H. T. "Improved adaptive gaining-sharing knowledge algorithm with FDB-based guiding mechanism for optimization of optimal reactive power flow problem." Electrical Engineering, 105, 3121-3160, 2023. DOI: [10.1007/s00202-023-01803-9](https://doi.org/10.1007/s00202-023-01803-9). |
| `atmals-gsk` | Alfadli, N. M.; Oun, E. M.; Mohamed, A. W. "Auto-Tuning Memory-Based Adaptive Local Search Gaining-Sharing Knowledge-Based Algorithm for Solving Optimization Problems." Algorithms, 18(7), 398, 2025. DOI: [10.3390/a18070398](https://doi.org/10.3390/a18070398). |
| `egsk` | Jawad, M. A.; Roshdy, H. S. M.; Mohamed, A. W. "Enhanced Gaining-Sharing Knowledge-Based Algorithm." Results in Control and Optimization, 19, 100542, 2025. DOI: [10.1016/j.rico.2025.100542](https://doi.org/10.1016/j.rico.2025.100542). |
| `dt-gsk` | DT-GSK (Dimension-Tiered Gaining-Sharing Knowledge), this project's proposed method. Forthcoming; until it is published, cite the software metadata in `CITATION.cff` at the repository root. |

## Before publication or redistribution

1. ~~Confirm the copyright line and year.~~ **DONE 2026-08-01** - confirmed by
   the author; the **Project license** section reads "Copyright (c) 2026 by the
   authors." (the MIT grant text is in the root `LICENSE`).
2. Confirm third-party license notices are preserved in the distribution.
3. Reconcile the **Attribution** section with the originating research codebase
   and benchmark suite license/citation statements.
4. Re-check the **Reproduction scope** wording against the latest
   [Validation Report](research/validation_report.md).
