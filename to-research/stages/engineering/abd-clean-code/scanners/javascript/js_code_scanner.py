"""Base scanner for JavaScript/TypeScript production code quality checks."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


class JsCodeScanner:
    """Base class for clean code JS scanners using regex analysis."""

    JS_EXTENSIONS = {".js", ".mjs", ".ts", ".tsx", ".jsx"}

    def __init__(self, rule):
        self.rule = rule

    def scan(self, context) -> list:
        return []

    def _get_js_files(self, context) -> list:
        return [
            f for f in context.get("code_files", [])
            if Path(f).suffix in self.JS_EXTENSIONS
        ]

    def _read_file(self, file_path: Path):
        if not file_path.exists():
            return None
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return None

    def _count_function_lines(self, content: str, func_start: int) -> int:
        """Estimate line count of a function starting at func_start (0-indexed)."""
        lines = content.split("\n")
        depth = 0
        for i, line in enumerate(lines[func_start:], start=func_start):
            depth += line.count("{") - line.count("}")
            if i > func_start and depth <= 0:
                return i - func_start + 1
        return len(lines) - func_start


# Backward-compatible alias (agile_bots uses JSCodeScanner).
JSCodeScanner = JsCodeScanner

_SKIP_DIRS = {"node_modules", ".git", "dist", "build", "coverage", "__pycache__"}


def build_code_context(workspace: Path) -> dict:
    """Collect production source files under packages/ for scanning."""
    root = workspace.resolve()
    code_files: list[str] = []
    packages = root / "packages"
    if not packages.is_dir():
        return {"code_files": [], "project_root": str(root)}

    for path in packages.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in JsCodeScanner.JS_EXTENSIONS:
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        name = path.name.lower()
        if ".test." in name or ".spec." in name:
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


if __name__ == "__main__":
    print("js_code_scanner: import this module; run a * _scanner.py file directly.", file=sys.stderr)
    sys.exit(2)
