"""SourceLocation - file:line citation used by scanners for violation messages."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceLocation:
    """Where a node came from — file and line range."""

    file: str  # relative path from workspace root
    line: int = 0  # 1-indexed; 0 = unknown
    end_line: int = 0
    text: str = ""

    def render(self) -> str:
        start = self.line
        end = self.end_line or self.line
        if start > 0 and end > start:
            return f"{self.file}:{start}-{end}"
        if start > 0:
            return f"{self.file}:{start}"
        return self.file
