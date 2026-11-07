"""Every module in the repository is imported under one name: its full name from the repository root.

The spec runners and the MCP host put folders such as ``cdd_guidance/actions`` and ``tools`` on the import path, so
``validate.validate`` and ``cdd_guidance.actions.validate.validate`` both resolve to one file. Python loads that file
twice under the two names, and its classes, ``isinstance`` checks, and class-level state split into two copies."""

import ast
import collections
import importlib
import sys
from pathlib import Path

from expects import be_empty, expect
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[1]
_PACKAGES = ("harness", "space", "tools", "cdd_guidance")
# Folders whose files are copied into other projects, read as data, or run by another runner.
_NOT_MODULES = {"retired", "node_modules", "__pycache__", "_examples", "templates", "seeds", "fixtures", "sandbox", "app"}
# Folders put on the import path beside the repository root; a top-level name found in one is a short name.
_SHORT_ROOTS = ("tools", "cdd_guidance", "cdd_guidance/actions", "cdd_guidance/practices", "cdd_guidance/patterns",
                "cdd_guidance/builders")


def _python_files() -> list[Path]:
    found = []
    for package in _PACKAGES:
        for path in sorted((_REPO / package).rglob("*.py")):
            folders = path.relative_to(_REPO).parts[:-1]
            if not any(part in _NOT_MODULES or part.startswith(".") for part in folders):
                found.append(path)
    return found


def _full_name(path: Path) -> str | None:
    """The module's full name from the repository root; none for a file Python cannot import by name."""
    parts = [*path.relative_to(_REPO).parts[:-1], path.stem]
    if not all(part.isidentifier() for part in parts):
        return None
    return ".".join(parts[:-1] if path.stem == "__init__" else parts)


def _production_modules() -> list[str]:
    names = (_full_name(path) for path in _python_files() if not path.stem.endswith("_spec") and path.stem != "conftest")
    return [name for name in names if name]


def _short_names() -> set[str]:
    short = set()
    for root in _SHORT_ROOTS:
        for child in (_REPO / root).iterdir():
            name = child.stem if child.suffix == ".py" else child.name
            if (child.is_dir() or child.suffix == ".py") and name.isidentifier() and name not in _PACKAGES:
                short.add(name)
    return short


def _short_name_imports(path: Path, short: set[str]) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    found = []
    for node in ast.walk(tree):
        names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else []
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module]
        found.extend(f"{path.relative_to(_REPO).as_posix()}:{node.lineno} {name}" for name in names if name.split(".")[0] in short)
    return found


def _files_loaded_twice() -> list[str]:
    by_file = collections.defaultdict(list)
    for name, module in list(sys.modules.items()):
        file = getattr(module, "__file__", None)
        if file and any(Path(file).resolve().is_relative_to(_REPO / package) for package in _PACKAGES):
            by_file[Path(file).resolve()].append(name)
    return [f"{file.relative_to(_REPO).as_posix()}: {sorted(names)}" for file, names in by_file.items() if len(names) > 1]


with description("the repository's modules") as self:
    with context("with every production module imported by its full name"):
        with before.all:
            for name in _production_modules():
                try:
                    importlib.import_module(name)
                except ImportError:
                    continue

        with it("should load each module file under one name"):
            expect(_files_loaded_twice()).to(be_empty)

    with context("with every Python file read"):
        with it("should import nothing by a short name from a folder on the import path"):
            short = _short_names()
            found = [line for path in _python_files() for line in _short_name_imports(path, short)]
            expect(found).to(be_empty)
