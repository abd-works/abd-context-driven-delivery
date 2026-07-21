"""SourceLocation — file:line citation used by scanners for violation messages."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceLocation:
    """Where a node came from — for violation citations."""

    file: str  # relative path from workspace root
    line: int = 0  # 1-indexed; 0 = unknown

    def render(self) -> str:
        if self.line > 0:
            return f"{self.file}:{self.line}"
        return self.file
