# Source Tree

Python source code lives under `src/gsk_family`.

The package uses a stable optimizer contract:

```text
BenchmarkProblem + OptimizerOptions -> optimizer.optimize -> OptimizerResult
```

See `docs/reference/api.md`, `docs/reference/module_dependencies.md`, and
`docs/reference/python_optimizer_interface.md` for the full contract.

