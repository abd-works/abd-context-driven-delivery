"""A note: the smallest marked toolset that draws every kind of generated view, for the language adapter's spec.

It lives under `_examples/`, which the install scan skips, so it never reaches a real install.
"""

from __future__ import annotations

from typing import TypedDict

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, tool_subject
from harness.installation.destination import edits, language_adapter
from harness.mcp.mcp_server import mcp


class NoteData(TypedDict):
    name: str
    title: str
    text: str
    is_pinned: bool


@language_adapter(language="typescript", identity="name")
@agent_toolset
class Note:
    """Hold one note: a title, its text, and whether it is pinned."""

    def __init__(self, name: str = "note", title: str = "", text: str = "", is_pinned: bool = False) -> None:
        self._name = name
        self._title = title
        self._text = text
        self._is_pinned = is_pinned

    @classmethod
    @tool_subject
    def load(cls, note: str) -> Note:
        return cls(note)

    @classmethod
    @mcp
    @agent_tool
    def new(cls, title: str) -> Note:
        """Write a new note with this title."""
        return cls(title.lower(), title)

    @mcp
    @agent_tool
    def update_text(self, text: str) -> Note:
        """Replace the note's text; its argument shares the field's name, so the view edits text inline."""
        self._text = text
        return self

    @mcp
    @agent_tool
    @edits("title")
    def rename(self, new_title: str) -> Note:
        """Give the note a new title; @edits says it changes title, since its argument is named differently."""
        self._title = new_title
        return self

    @mcp
    @agent_tool
    def pin(self) -> Note:
        """Pin the note; it takes no arguments, so the view draws a button."""
        self._is_pinned = True
        return self

    @mcp
    @agent_tool
    def word_count(self) -> int:
        """Count the note's words; it answers with something other than the note, so the view shows the answer."""
        return len(self._text.split())

    def to_json(self) -> NoteData:
        return {"name": self._name, "title": self._title, "text": self._text, "is_pinned": self._is_pinned}
