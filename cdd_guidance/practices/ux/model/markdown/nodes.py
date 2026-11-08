"""Markdown channel - the map's scope and its UxContext notes and invariants; it carries no screens."""

from __future__ import annotations

from typing import List, Optional

from cdd_guidance.practices.ux.model.ux_map import UxMap

_TITLE = "# UX context"
_SCOPE = "Scope: "
_INVARIANTS = "Invariants"
_NOTES = "Notes"
_SECTION = "## "
_ITEM = "- "


class MarkdownUxMap(UxMap):
    """Writes and reads the scope, then the invariants and notes as bullet lists under their own headings.

    A hand-written context file reads too: any other line, or a bullet under any other heading, is a note.
    """

    workspace_files = (".context/ux-context.md", "ux-context.md", ".context/context.md", "context.md")

    def parse(self, content: str) -> UxMap:
        """A new map of this format, read from a markdown context file."""
        ux_map = type(self).create()
        ux_map.read_text(content)
        return ux_map

    def read_text(self, content: str) -> None:
        """Read the file line by line into this map's scope and context: a bullet goes in the list of the heading it
        is under, and any other line is a note."""
        under: Optional[List[str]] = None
        for line in content.splitlines():
            text = line.strip()
            if not text or text == _TITLE:
                continue
            if text.startswith(_SCOPE) and not self.scope:
                self.scope = text[len(_SCOPE):]
            elif text.startswith(_SECTION):
                under = self._list_under(text[len(_SECTION):].strip())
            elif text.startswith(_ITEM) and under is not None:
                under.append(text[len(_ITEM):])
            else:
                self.context.notes.append(text)

    def _list_under(self, heading: str) -> List[str]:
        return self.context.invariants if heading == _INVARIANTS else self.context.notes

    def render(self, canonical: UxMap) -> str:
        """canonical's context: copied into a markdown map, which writes itself."""
        return self.copy_of(canonical).save()

    def save(self) -> str:
        lines = [_TITLE, ""]
        if self.scope:
            lines.extend([f"{_SCOPE}{self.scope}", ""])
        lines.extend(self._section(_INVARIANTS, self.context.invariants))
        lines.extend(self._section(_NOTES, self.context.notes))
        return "\n".join(lines).rstrip() + "\n"

    def _section(self, heading: str, items: List[str]) -> List[str]:
        if not items:
            return []
        return [f"{_SECTION}{heading}", *(f"{_ITEM}{item}" for item in items), ""]
