"""Base scanner for production code quality — uses the language channel parse only."""
from __future__ import annotations

from pathlib import Path

from scanners import Scanner

from clean_engineering.class_model.base_class_model import OoadClass, Operation
from clean_engineering.class_model.java_class_model import JavaCleanEngineeringModel
from clean_engineering.class_model.javascript_class_model import JavaScriptCleanEngineeringModel
from clean_engineering.class_model.python_class_model import ParsedPython, PythonCleanEngineeringModel
from clean_engineering.class_model.typescript_class_model import TypeScriptCleanEngineeringModel

_SKIP_DIRS = {"node_modules", ".git", "dist", "build", "coverage", "__pycache__", ".venv", "venv"}

_CHANNEL_BY_EXT = {
    ".py": PythonCleanEngineeringModel,
    ".ts": TypeScriptCleanEngineeringModel,
    ".tsx": TypeScriptCleanEngineeringModel,
    ".js": JavaScriptCleanEngineeringModel,
    ".jsx": JavaScriptCleanEngineeringModel,
    ".java": JavaCleanEngineeringModel,
}

CODE_EXTENSIONS = frozenset(_CHANNEL_BY_EXT)


class CodeScanner(Scanner):
    """Scanners read the CleanEngineering model filled by the active language channel."""

    PY_EXTENSIONS = {".py"}

    def _parse_file(self, file_path: Path) -> ParsedPython | None:
        channel = _CHANNEL_BY_EXT.get(file_path.suffix.lower())
        if channel is None:
            return None
        return channel.parse_file(file_path)

    def _iter_operations(self, file_path: Path) -> list[tuple[Operation, ParsedPython]]:
        parsed = self._parse_file(file_path)
        if parsed is None:
            return []
        pairs: list[tuple[Operation, ParsedPython]] = []
        for module in parsed.model.modules:
            for oclass in module.classes:
                for op in oclass.operations:
                    pairs.append((op, parsed))
        return pairs

    def _iter_classes(self, file_path: Path) -> list[tuple[OoadClass, ParsedPython]]:
        parsed = self._parse_file(file_path)
        if parsed is None:
            return []
        return [
            (oclass, parsed)
            for module in parsed.model.modules
            for oclass in module.classes
            if oclass.name != "_module"
        ]


def collect_python_files(root: Path) -> list[Path]:
    return collect_code_files(root, extensions={".py"})


def collect_code_files(
    root: Path,
    *,
    extensions: frozenset[str] | set[str] | None = None,
) -> list[Path]:
    """Collect production source files under packages/ (or root) by extension."""
    root = root.resolve()
    exts = {e.lower() for e in (extensions or CODE_EXTENSIONS)}
    search_roots = [root / "packages"] if (root / "packages").is_dir() else [root]
    code_files: list[Path] = []
    for search in search_roots:
        if not search.is_dir():
            continue
        for path in search.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in exts:
                continue
            if any(part in _SKIP_DIRS for part in path.parts):
                continue
            name = path.name.lower()
            if name.startswith("test_") or name.endswith("_test.py"):
                continue
            if ".test." in name or name.endswith("_test.ts") or name.endswith("_test.js"):
                continue
            code_files.append(path)
    return sorted(code_files)
