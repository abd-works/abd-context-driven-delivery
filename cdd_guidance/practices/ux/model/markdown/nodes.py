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
        ux_map = type(self).create()
        MarkdownContextReader(ux_map).read(content)
        return ux_map

    def render(self, ux_map: UxMap) -> str:
        lines = [_TITLE, ""]
        if ux_map.scope:
            lines.extend([f"{_SCOPE}{ux_map.scope}", ""])
        lines.extend(self._section(_INVARIANTS, ux_map.context.invariants))
        lines.extend(self._section(_NOTES, ux_map.context.notes))
        return "\n".join(lines).rstrip() + "\n"

    def _section(self, heading: str, items: List[str]) -> List[str]:
        if not items:
            return []
        return [f"{_SECTION}{heading}", *(f"{_ITEM}{item}" for item in items), ""]


class MarkdownContextReader:
    """Reads one markdown file line by line into a map's scope and context, remembering the heading it is under."""

    def __init__(self, ux_map: UxMap) -> None:
        self.ux_map = ux_map
        self._under: Optional[List[str]] = None

    def read(self, content: str) -> None:
        for line in content.splitlines():
            self._read_line(line.strip())

    def _read_line(self, text: str) -> None:
        if not text or text == _TITLE:
            return
        if text.startswith(_SCOPE) and not self.ux_map.scope:
            self.ux_map.scope = text[len(_SCOPE):]
            return
        if text.startswith(_SECTION):
            self._under = self._list_under(text[len(_SECTION):].strip())
            return
        if text.startswith(_ITEM) and self._under is not None:
            self._under.append(text[len(_ITEM):])
            return
        self.ux_map.context.notes.append(text)

    def _list_under(self, heading: str) -> List[str]:
        context = self.ux_map.context
        return context.invariants if heading == _INVARIANTS else context.notes
