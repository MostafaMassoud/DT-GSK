# CLI Package

This package contains console entry points registered in `pyproject.toml`.

## Commands

| Command | Module | Purpose |
|---|---|---|
| `gsk-list` | `list.py` | List optimizers, benchmark suites, and references. |
| `gsk-run` | `run.py` | Run YAML or direct experiment configs. |
| `gsk-stats` | `stats.py` | Compute family statistics and render analysis tables and figures. |
| `gsk-validate` | `validate.py` | Validate references or compare generated results. |

CLI modules should remain thin wrappers around package APIs.

