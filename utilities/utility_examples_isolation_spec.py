"""Static BDD: each utility uses its own examples; sibling-utility examples are off-limits.

Production imports between utilities (e.g. diagnose → sub_agent) are allowed.
Only ``*.examples`` imports from a different utilities/ package are violations.
"""

import ast
from pathlib import Path

from expects import equal, expect
from mamba import context, description, it

_UTILITIES_ROOT = Path(__file__).resolve().parent
_SKIP_DIR_NAMES = frozenset({"__pycache__", ".sessions", "_retired"})


def _utility_names() -> frozenset[str]:
    return frozenset(
        p.name
        for p in _UTILITIES_ROOT.iterdir()
        if p.is_dir() and not p.name.startswith(".") and p.name not in _SKIP_DIR_NAMES
    )


def _iter_utility_py_files():
    for utility_dir in sorted(_UTILITIES_ROOT.iterdir()):
        if not utility_dir.is_dir() or utility_dir.name.startswith("."):
            continue
        if utility_dir.name in _SKIP_DIR_NAMES:
            continue
        for py_file in sorted(utility_dir.rglob("*.py")):
            if any(part in _SKIP_DIR_NAMES for part in py_file.parts):
                continue
            yield utility_dir.name, py_file


def _imported_modules(tree: ast.AST) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def _foreign_example_imports(owner: str, py_file: Path, utility_names: frozenset[str]) -> list[str]:
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    except SyntaxError:
        return [f"{py_file}: unparseable"]
    bad: list[str] = []
    for module in _imported_modules(tree):
        parts = module.split(".")
        if len(parts) < 2 or parts[1] != "examples":
            continue
        other = parts[0]
        if other in utility_names and other != owner:
            rel = py_file.relative_to(_UTILITIES_ROOT)
            bad.append(f"{rel} imports {module}")
    return bad


def _all_foreign_example_imports() -> list[str]:
    names = _utility_names()
    found: list[str] = []
    for owner, py_file in _iter_utility_py_files():
        found.extend(_foreign_example_imports(owner, py_file, names))
    return found


with description("a utility under utilities"):
    with context("that imports an examples module"):
        with it("should only import examples from its own package"):
            expect(_all_foreign_example_imports()).to(equal([]))
