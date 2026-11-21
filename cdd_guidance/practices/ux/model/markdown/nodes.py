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

    map_file_suffixes = (".md",)
    holds_screens = False

    def reads_file(self, file: Path, text: str) -> bool:
        """The UX context file, ``ux-context.md``; any other markdown file is another document."""
        return file.name == _CONTEXT_FILE_NAME

    def parse(self, content: str) -> UxMap:
        """A new map of this format, read from a markdown context file."""
        ux_map = type(self).create()
        ux_map._read_context(content)
        return ux_map

    def _read_context(self, content: str) -> None:
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
        now, which the render writes onto instead of replacing: every line a person wrote stays where it is, the
        invariants and notes the file lacks are added after the ones it holds, and the scope line says the scope
        canonical has. A source that holds no scope, invariant, or note, such as the drawing, leaves the file as it is."""
        written = self.copy_of(canonical)
        if not previous:
            return written.save()
        return written._written_onto(previous, self.parse(previous))

    def _written_onto(self, previous: str, held: UxMap) -> str:
        """previous, the context file's text, with what this map holds and held, the map read from that text, lacks."""
        lines = previous.splitlines()
        if self.scope and self.scope != held.scope:
            lines = self._with_scope(lines)
        gained = [item for item in self.context.invariants if item not in held.context.invariants]
        lines = self._with_items(lines, _INVARIANTS, gained)
        known = [*held.context.notes, *held.context.invariants]
        lines = self._with_items(lines, _NOTES, [item for item in self.context.notes if item not in known])
        return "\n".join(lines) + "\n"

    def _with_scope(self, lines: List[str]) -> List[str]:
        """lines with this map's scope on the scope line; with no such line, on a line of its own under the title."""
        at = next((index for index, line in enumerate(lines) if line.strip().startswith(_SCOPE)), -1)
        if at >= 0:
            return [*lines[:at], f"{_SCOPE}{self.scope}", *lines[at + 1:]]
        under = next((index + 1 for index, line in enumerate(lines) if line.strip() == _TITLE), 0)
        return [*lines[:under], "", f"{_SCOPE}{self.scope}", *lines[under:]]

    def _with_items(self, lines: List[str], heading: str, items: List[str]) -> List[str]:
        """lines with items as bullets after the last line under heading; with no such heading, under a new one after
        what the file holds."""
        if not items:
            return lines
        bullets = [f"{_ITEM}{item}" for item in items]
        at = next((index for index, line in enumerate(lines) if line.strip() == f"{_SECTION}{heading}"), -1)
        if at < 0:
            while lines and not lines[-1].strip():
                lines = lines[:-1]
            return [*lines, "", f"{_SECTION}{heading}", *bullets]
        following = next((index for index in range(at + 1, len(lines)) if lines[index].startswith(_SECTION)), len(lines))
        last = max(index for index in range(at, following) if lines[index].strip()) + 1
        return [*lines[:last], *bullets, *lines[last:]]

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
