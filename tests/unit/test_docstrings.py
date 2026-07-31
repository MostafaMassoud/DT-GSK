from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PROJECT_ROOT / "src" / "gsk_family"


# Vendored DT-GSK modules are byte-identical copies of the upstream DT-GSK
# project and are intentionally exempt from the local per-function docstring
# policy. This covers the optimizer core (optimizers/_dt_core.py and
# optimizers/_dt_subsystems/*) and the vendored statistical-analysis modules
# (analysis/statistics.py and analysis/statistical_tests.py).
_VENDORED_ANALYSIS = {"statistics.py", "statistical_tests.py"}


def _is_vendored_ism(path: Path) -> bool:
    if path.name == "_dt_core.py" or "_dt_subsystems" in path.parts:
        return True
    return "analysis" in path.parts and path.name in _VENDORED_ANALYSIS


def test_all_source_modules_classes_functions_and_methods_have_docstrings() -> None:
    missing: list[str] = []

    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        if _is_vendored_ism(path):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        relative = path.relative_to(PROJECT_ROOT)
        if ast.get_docstring(tree) is None:
            missing.append(f"{relative}:1 module")
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if ast.get_docstring(node) is None:
                    missing.append(f"{relative}:{node.lineno} {node.name}")

    assert not missing, "Missing docstrings:\n" + "\n".join(missing)

