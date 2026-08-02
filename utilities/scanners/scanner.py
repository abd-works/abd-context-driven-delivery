from __future__ import annotations

from abc import ABC
from pathlib import Path

from .violation import Violation

# Directory names excluded from every scan (fixtures, demos, tooling noise).
SKIP_DIR_NAMES = frozenset(
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
    }
)


class Scanner(ABC):
    """Scan a named rule over files under *root*."""

    def __init__(self, rule: str) -> None:
        self.rule = rule

    @staticmethod
    def is_skipped_path(path: Path) -> bool:
        """True when *path* sits under a skipped directory name (e.g. ``examples/``)."""
        return any(part in SKIP_DIR_NAMES for part in Path(path).parts)

    @staticmethod
    def filter_scan_files(files: list[Path]) -> list[Path]:
        """Drop paths under skipped directories so demos do not inflate module metrics."""
        return [path for path in files if not Scanner.is_skipped_path(path)]

    def scan(self, root: Path, files: list[Path]) -> list[Violation]:
        root = root.resolve()
        violations: list[Violation] = []
        for file_path in Scanner.filter_scan_files(files):
            path = file_path if file_path.is_absolute() else root / file_path
            if not path.is_file():
                continue
            if Scanner.is_skipped_path(path):
                continue
            violations.extend(self.scan_file(root, path))
        return violations

    def scan_file(self, root: Path, file_path: Path) -> list[Violation]:
        return []

    def violation(
        self,
        message: str,
        *,
        location: str = "",
        line: int | None = None,
        severity: str = "error",
    ) -> Violation:
        return Violation(
            self.rule,
            message,
            location=location,
            line=line,
            severity=severity,
        )
