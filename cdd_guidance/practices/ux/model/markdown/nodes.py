"""Markdown channel - the map's scope and its UxContext notes and invariants; it carries no screens, so a render
from a source that holds only screens leaves the context file already there as it is."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from cdd_guidance.practices.ux.model.ux_map import UxMap

_TITLE = "# UX context"
_CONTEXT_FILE_NAME = "ux-context.md"
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
    map_file_suffixes = (".md",)
    holds_screens = False

    def reads_file(self, file: Path, text: str) -> bool:
        """The UX context file, ``ux-context.md``; any other markdown file is another document."""
        return file.name == _CONTEXT_FILE_NAME

    def parse(self, content: str) -> UxMap:
        """A new map of this format, read from a markdown context file."""
        ux_map = type(self).create()
        ux_map.read_context(content)
        return ux_map

    def read_context(self, content: str) -> None:
        """Read the file line by line into this map's scope and context: a bullet goes in the list of the heading it
        is under, and any other line is a note."""
        under: Optional[List[str]] = None
        for line in content.splitlines():
            under = self._read_line(line.strip(), under)

    def _read_line(self, text: str, under: Optional[List[str]]) -> Optional[List[str]]:
        """Read one line into the scope or the context; returns the list a bullet after it goes in, which a heading
        changes."""
        if not text or text == _TITLE:
            return under
        if text.startswith(_SCOPE) and not self.scope:
            self.scope = text[len(_SCOPE):]
        elif text.startswith(_SECTION):
            return self._list_under(text[len(_SECTION):].strip())
        elif text.startswith(_ITEM) and under is not None:
            under.append(text[len(_ITEM):])
        else:
            self.context.notes.append(text)
        return under

    def _list_under(self, heading: str) -> List[str]:
        return self.context.invariants if heading == _INVARIANTS else self.context.notes

    def render(self, canonical: UxMap, previous: Optional[str] = None) -> str:
        """canonical's context: copied into a markdown map, which writes itself. previous is the context file as it is
        now: a source that holds no scope, invariant, or note, such as the drawing, leaves it as it is, and the scope,
        invariants, or notes a source lacks stay as the file holds them, so a render never empties what a person wrote."""
        written = self.copy_of(canonical)
        if not previous:
            return written.save()
        if written.holds_no_context:
            return previous
        written.keep_missing_from(self.parse(previous))
        return written.save()

    @property
    def holds_no_context(self) -> bool:
        """Whether this map has nothing a context file writes: no scope, no invariant, and no note."""
        return not (self.scope or self.context.invariants or self.context.notes)

    def keep_missing_from(self, kept: UxMap) -> None:
        """Take from kept, the context file as it was, the scope, the invariants, and the notes this map has none of."""
        self.scope = self.scope or kept.scope
        self.context.invariants = self.context.invariants or list(kept.context.invariants)
        self.context.notes = self.context.notes or list(kept.context.notes)

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
