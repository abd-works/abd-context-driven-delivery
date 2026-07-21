"""Base scanner for CleanEngineering module-level rules.

Module rules operate on a *module* — a folder containing `.context/module-context.md`.
Scanners here identify modules from an input file list, then evaluate rules across
the whole folder rather than per-file.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from scanners import Scanner

_SKIP_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    ".venv",
    "venv",
    "examples",  # fixtures / demos — not production seam
}
_CONTEXT_FILENAME = "module-context.md"
_CONTEXT_DIR = ".context"


@dataclass(frozen=True)
class Module:
    """A folder identified as an CleanEngineering module."""

    folder: Path
    context_file: Path
    python_files: tuple[Path, ...]


class ModuleScanner(Scanner):
    """Scanner that evaluates rules once per module folder.

    Subclasses override :meth:`scan_module` — one call per module folder discovered
    among the files under scan.
    """

    def scan(self, root: Path, files: list[Path]) -> list:
        root = root.resolve()
        files = [
            path
            for path in files
            if not any(part in _SKIP_DIRS for part in Path(path).parts)
        ]
        modules = self._collect_modules(root, files)
        violations: list = []
        for module in modules:
            violations.extend(self.scan_module(root, module))
        return violations

    def scan_module(self, root: Path, module: Module) -> list:
        return []

    def _collect_modules(self, root: Path, files: list[Path]) -> list[Module]:
        module_folders: set[Path] = set()
        for file_path in files:
            path = file_path if file_path.is_absolute() else root / file_path
            module_folder = self._enclosing_module(root, path)
            if module_folder is not None:
                module_folders.add(module_folder)
        for context_file in root.rglob(f"{_CONTEXT_DIR}/{_CONTEXT_FILENAME}"):
            if not context_file.is_file():
                continue
            if any(part in _SKIP_DIRS for part in context_file.parts):
                continue
            module_folders.add(context_file.parent.parent)
        return [self._build_module(folder) for folder in sorted(module_folders)]

    @staticmethod
    def _enclosing_module(root: Path, file_path: Path) -> Path | None:
        try:
            file_path = file_path.resolve()
        except OSError:
            return None
        for candidate in [file_path, *file_path.parents]:
            if candidate == root.parent:
                return None
            context_file = candidate / _CONTEXT_DIR / _CONTEXT_FILENAME
            if context_file.is_file():
                return candidate
        return None

    @staticmethod
    def _build_module(folder: Path) -> Module:
        context_file = folder / _CONTEXT_DIR / _CONTEXT_FILENAME
        python_files = tuple(sorted(_collect_module_python_files(folder)))
        return Module(folder=folder, context_file=context_file, python_files=python_files)

    @staticmethod
    def parse_python(file_path: Path) -> ast.AST | None:
        try:
            content = file_path.read_text(encoding="utf-8")
            return ast.parse(content, filename=str(file_path))
        except (OSError, SyntaxError, UnicodeDecodeError):
            return None


def _collect_module_python_files(module_folder: Path) -> list[Path]:
    files: list[Path] = []
    for path in module_folder.rglob("*.py"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if _is_test_file(path):
            continue
        if _in_nested_module(path, module_folder):
            continue
        files.append(path)
    return files


def _is_test_file(path: Path) -> bool:
    name = path.name.lower()
    return name.startswith("test_") or name.endswith("_test.py") or "_spec." in name


def _in_nested_module(file_path: Path, module_folder: Path) -> bool:
    for parent in file_path.parents:
        if parent == module_folder:
            return False
        if (parent / _CONTEXT_DIR / _CONTEXT_FILENAME).is_file():
            return True
    return False


def collect_module_files(root: Path) -> list[Path]:
    """Collector for scanner-runner CLI: every .py file under any module folder."""
    root = root.resolve()
    context_files = list(root.rglob(f"{_CONTEXT_DIR}/{_CONTEXT_FILENAME}"))
    module_folders = [context.parent.parent for context in context_files if context.is_file()]
    seen: set[Path] = set()
    out: list[Path] = []
    for folder in sorted(module_folders):
        for python_file in _collect_module_python_files(folder):
            resolved = python_file.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            out.append(python_file)
    return out
