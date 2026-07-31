"""CEC benchmark suites — five suites, all runnable through the adapter.

Every suite here is served to optimizers by
``gsk_family.benchmark_adapter.factory.make_problem`` and can be
run via ``run.py``; JIT kernels are warmed per spawned worker by
``gsk_family.runners.run_experiment._init_process_worker`` for
whichever suite a run selects.

Paper-campaign suites (the three the publication protocol runs;
``configs/hbi_*.yml``):

* **cec2017** — 29 functions (F1-F30 excl. F2), D in {10, 30, 50, 100}
* **cec2011** — 22 real-world problems, per-function fixed dimensions
* **cec2013lsgo** — 15 large-scale global optimisation functions (D=1000)

Non-campaign suites (importable and runnable, retained for validation and
future campaign work):

* **cec2013** — 28 functions (F1-F28), D in {10, 30, 50}
* **cec2020** — 10 functions (basic + simple + hybrid + composition)
"""
