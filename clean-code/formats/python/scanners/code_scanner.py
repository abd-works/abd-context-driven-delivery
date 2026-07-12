"""Base scanner for production Python code quality checks."""
from __future__ import annotations

import ast
from pathlib import Path

from scanners import Scanner, Violation

_SKIP_DIRS = {"node_modules", ".git", "dist", "build", "coverage", "__pycache__", ".venv", "venv"}


class CodeScanner(Scanner):
    PY_EXTENSIONS = {".py"}

    def _read_and_parse_file(self, file_path: Path):
        if not file_path.exists():
            return None
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            tree = ast.parse(content, filename=str(file_path))
            return content, lines, tree
        except (SyntaxError, UnicodeDecodeError):
            return None

    def _function_line_count(self, node: ast.FunctionDef) -> int:
        if not hasattr(node, "end_lineno") or not hasattr(node, "lineno"):
            return 0
        return node.end_lineno - node.lineno + 1


def collect_python_files(root: Path) -> list[Path]:
    root = root.resolve()
    code_files: list[Path] = []
    packages = root / "packages"
    if not packages.is_dir():
        return code_files

    for path in packages.rglob("*.py"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        name = path.name.lower()
        if name.startswith("test_") or name.endswith("_test.py"):
            continue
        code_files.append(path)

    return sorted(code_files)
