"""Scanner: `missing-module-context` — every Python package that owns a class or
toolset must have a `.context/module-context.md`.

Rule: missing-module-context

A Python package folder is considered a CE module when it contains at least one
non-spec, non-example `.py` file that defines a class at the top level. If that
folder has no `.context/module-context.md`, the module has no documented seam,
purpose, or dependency contract — a hard CE violation.

FP profile: LOW. Structural check; only fires on folders with real class definitions.
"""
from __future__ import annotations

import ast
from pathlib import Path

from scanners import Scanner

_SKIP_DIR_NAMES = frozenset(
    {
        "node_modules",
        ".git",
        "dist",
        "build",
        "coverage",
        "__pycache__",
        ".venv",
        "venv",
        "examples",
        "scanners",
        "templates",
    }
)

_CONTEXT_DIR = ".context"
_CONTEXT_FILENAME = "module-context.md"


class MissingModuleContextScanner(Scanner):
    """Flag Python package folders that define classes but have no module-context.md."""

    def scan(self, root: Path, files: list[Path]) -> list:
        root = root.resolve()
        candidate_dirs: set[Path] = set()
        for file_path in files:
            path = file_path if file_path.is_absolute() else root / file_path
            if not path.is_file():
                continue
            if self._is_skipped(path):
                continue
            if self._is_spec_or_init(path):
                continue
            if self._has_class_definition(path):
                candidate_dirs.add(path.parent)

        violations = []
        for folder in sorted(candidate_dirs):
            context_file = folder / _CONTEXT_DIR / _CONTEXT_FILENAME
            if not context_file.is_file():
                violations.append(
                    self.violation(
                        f"Module folder '{folder.name}' defines classes but has no "
                        f".context/module-context.md. "
                        f"Add one with at minimum: Purpose, Seam, Dependencies.",
                        location=str(folder),
                    )
                )
        return violations

    def _is_skipped(self, path: Path) -> bool:
        return any(part in _SKIP_DIR_NAMES for part in path.parts)

    def _is_spec_or_init(self, path: Path) -> bool:
        name = path.name
        return (
            name == "__init__.py"
            or name.endswith("_spec.py")
            or name.startswith("test_")
            or name.endswith("_test.py")
            or name == "register.py"
        )

    def _has_class_definition(self, path: Path) -> bool:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError, UnicodeDecodeError):
            return False
        return any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))


if __name__ == "__main__":
    from scanners import run_scanner_main
    from code_scanner import collect_python_files

    raise SystemExit(
        run_scanner_main(
            MissingModuleContextScanner,
            "missing-module-context",
            collect_python_files,
        )
    )
