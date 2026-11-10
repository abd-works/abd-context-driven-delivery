"""SourceLocation - file:line citation used by scanners for violation messages."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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


def path_from(base: Path, path: Path) -> str:
    """*path* as a path from *base*, the way a node names its file; its bare name when it sits outside *base*."""
    resolved = Path(path).resolve()
    if base != resolved and base not in resolved.parents:
        return resolved.name
    return resolved.relative_to(base).as_posix()
