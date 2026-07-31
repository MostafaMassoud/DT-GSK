# Benchmark Adapter Package

The benchmark adapter turns each benchmark suite into a uniform
`BenchmarkProblem` object.

## Files

| File | Purpose |
|---|---|
| `factory.py` | Construct benchmark problems. |
| `problem.py` | Define `BenchmarkProblem` and shape validators. |
| `protocol.py` | Suite metadata, function ids, dimensions, and defaults. |

Optimizers should call only `problem.evaluate(population)` and should not import
suite internals directly.

