"""Base scanner for production code quality checks."""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanner_bases.scanner import Scanner
    from scanner_bases.violation import Violation

_SKIP_DIRS = {"node_modules", ".git", "dist", "build", "coverage", "__pycache__", ".venv", "venv"}


class CodeScanner:
    """Base class for clean code production code scanners."""

    PY_EXTENSIONS = {".py"}

    def __init__(self, rule):
        self.rule = rule

    def scan(self, context) -> list:
        return []

    def _read_and_parse_file(self, file_path: Path):
        """Read and parse a Python file, returning (content, lines, tree) or None."""
        if not file_path.exists():
            return None
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            tree = ast.parse(content, filename=str(file_path))
            return (content, lines, tree)
        except (SyntaxError, UnicodeDecodeError):
            return None

    def _function_line_count(self, node: ast.FunctionDef) -> int:
        """Count lines spanned by a function definition."""
        if not hasattr(node, "end_lineno") or not hasattr(node, "lineno"):
            return 0
        return node.end_lineno - node.lineno + 1


def build_code_context(workspace: Path) -> dict:
    """Collect production Python files under packages/ for scanning."""
    root = workspace.resolve()
    code_files: list[str] = []
    packages = root / "packages"
    if not packages.is_dir():
        return {"code_files": [], "project_root": str(root)}

    for path in packages.rglob("*.py"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        name = path.name.lower()
        if name.startswith("test_") or name.endswith("_test.py"):
            continue
        code_files.append(str(path))

    return {"code_files": sorted(code_files), "project_root": str(root)}


def run_scanner_main(scanner_class, rule_name: str) -> None:
    """CLI entrypoint: --workspace → scan → violations on stderr → exit code."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--story-graph", type=Path, default=None)
    args = parser.parse_args()

    context = build_code_context(args.workspace)
    scanner = scanner_class(rule_name)
    violations = scanner.scan(context)

    for v in violations:
        out = {
            "violation_message": v.get("message", str(v)),
            "severity": v.get("severity", "error"),
            "location": v.get("location", ""),
            "line": v.get("line", 0),
        }
        print(out, file=sys.stderr)

    sys.exit(1 if violations else 0)
