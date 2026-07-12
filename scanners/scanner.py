from __future__ import annotations

from abc import ABC
from pathlib import Path

from .violation import Violation


class Scanner(ABC):
    """Scan a named rule over files under *root*."""

    def __init__(self, rule: str) -> None:
        self.rule = rule

    def scan(self, root: Path, files: list[Path]) -> list[Violation]:
        root = root.resolve()
        violations: list[Violation] = []
        for file_path in files:
            path = file_path if file_path.is_absolute() else root / file_path
            if not path.is_file():
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
