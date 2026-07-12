"""Base scanner for JavaScript/TypeScript production code quality checks."""
from __future__ import annotations

from pathlib import Path

from scanners import Scanner, Violation

_SKIP_DIRS = {"node_modules", ".git", "dist", "build", "coverage", "__pycache__"}


class JsCodeScanner(Scanner):
    JS_EXTENSIONS = {".js", ".mjs", ".ts", ".tsx", ".jsx"}

    def scan(self, root: Path, files: list[Path]) -> list[Violation]:
        js_files = [path for path in files if path.suffix in self.JS_EXTENSIONS]
        return super().scan(root, js_files)

    def _read_file(self, file_path: Path):
        if not file_path.exists():
            return None
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return None

    def _count_function_lines(self, content: str, func_start: int) -> int:
        lines = content.split("\n")
        depth = 0
        for i, line in enumerate(lines[func_start:], start=func_start):
            depth += line.count("{") - line.count("}")
            if i > func_start and depth <= 0:
                return i - func_start + 1
        return len(lines) - func_start


JSCodeScanner = JsCodeScanner


def collect_javascript_files(root: Path) -> list[Path]:
    root = root.resolve()
    code_files: list[Path] = []
    packages = root / "packages"
    if not packages.is_dir():
        return code_files

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
        code_files.append(path)

    return sorted(code_files)
