"""Markdown channel — optional UxContext / scratch notes; not mandatory generate path."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from context_tools.ux.ux_model.ux_map import UxMap


class MarkdownUxMap(UxMap):
    """Parse/render lightweight markdown context (notes, invariants)."""

    @classmethod
    def parse(cls, content: str) -> UxMap:
        """Minimal parse: treat non-empty markdown as context notes on an empty map."""
        ux_map = cls()
        notes = [line.strip() for line in content.splitlines() if line.strip()]
        ux_map.context.notes = notes
        return ux_map

    @classmethod
    def render(cls, ux_map: UxMap) -> str:
        lines = ["# UX context", ""]
        if ux_map.scope:
            lines.extend([f"Scope: {ux_map.scope}", ""])
        if ux_map.context.invariants:
            lines.append("## Invariants")
            for item in ux_map.context.invariants:
                lines.append(f"- {item}")
            lines.append("")
        if ux_map.context.notes:
            lines.append("## Notes")
            for item in ux_map.context.notes:
                lines.append(f"- {item}")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    @classmethod
    def from_workspace(cls, root: Path) -> Optional[UxMap]:
        root = Path(root)
        for candidate in (
            root / ".context" / "ux-context.md",
            root / "ux-context.md",
            root / ".context" / "context.md",
            root / "context.md",
        ):
            if candidate.is_file():
                return cls.parse(candidate.read_text(encoding="utf-8"))
        return None
