# CEC2011 Python Benchmark Suite

Pure Python/NumPy implementation of the IEEE CEC2011 real-world
single-objective optimization suite.

## Role

CEC2011 is the real-world validation and campaign suite.

Paper settings:

- 22 fixed-dimension engineering problems.
- n=25 independent runs.
- fixed 150000 function evaluations per run.
- no function exclusions.
- comparison panel: discovered at runtime from committed reference results (currently GSK).

## Problems

| ID | Problem | D |
|---|---|---:|
| F1 | FM sound parameter estimation | 6 |
| F2 | Lennard-Jones potential | 30 |
| F3 | bifunctional catalyst blend control | 1 |
| F4 | stirred tank reactor control | 1 |
| F5-F6 | Tersoff potential | 30 |
| F7 | spread spectrum radar polyphase | 20 |
| F8 | transmission network expansion planning | 7 |
| F9 | large-scale energy brokerage | 126 |
| F10 | circular antenna array design | 12 |
| F11-F12 | dynamic economic load dispatch | 120, 240 |
| F13-F17 | static economic load dispatch | 6-140 |
| F18-F20 | hydrothermal scheduling | 96 |
| F21 | Messenger spacecraft trajectory | 26 |
| F22 | Cassini-Huygens spacecraft trajectory | 22 |

Use `cec2011_dim(func_id)` and `cec2011_bounds(func_id)` to retrieve each
problem's native dimension and bounds.  Do not pass a shared dimension.

## Special Handling

- F5 and F6 convert NaN Tersoff potential results to 0.0, matching the original
  reference behavior.
- The problems are not vectorized internally; the dispatcher loops over rows.
- Negative raw objective values are valid and must not be clamped.

## Implementation Map

```text
cec2011/
  __init__.py
  functions.py
  _constants.py
  _numba.py
  problems_basic.py
  problems_power.py
  problems_antenna.py
  problems_hydrothermal.py
  problems_spacecraft.py
  orbital_mechanics.py
  reference_results.py
```
