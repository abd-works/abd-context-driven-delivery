"""Integrated example - @toolset, @agent_tool, @resource, @markdown, @agent_instructions."""
from __future__ import annotations

import inspect
from pathlib import Path

from harness.agent_tools import agent_instructions, agent_tool, agent_toolset
from harness.markdown import markdown


@agent_toolset
class Reporter:
    """Gather notes and file field reports.

    Tools are called by the AI directly. @markdown properties extract
    co-located prose. Actions are recipes interpreted by the AI.
    """

    def __init__(self, beat: str) -> None:
        self._beat = beat
        self._notes: list[str] = []
        super().__init__()

    @property
    def module_dir(self) -> Path:
        return Path(inspect.getfile(type(self))).resolve().parent

    @property
    def beat(self) -> str:
        """The news beat this reporter covers."""
        return self._beat

    @property
    def note_count(self) -> int:
        """Number of field notes collected so far."""
        return len(self._notes)

    @agent_tool
    def add_note(self, note: str) -> str:
        """Record a field note."""
        self._notes.append(note)
        return f"Note added: {note}"

    @agent_tool
    def read_notes(self) -> str:
        """Return all collected notes as a numbered list."""
        if not self._notes:
            return "No notes yet."
        return "\n".join(f"{i + 1}. {n}" for i, n in enumerate(self._notes))

    @agent_tool
    def clear_notes(self) -> None:
        """Discard all notes and start fresh."""
        self._notes.clear()

    @markdown
    def style(self) -> str: ...

    @markdown(label="house-guidelines")
    def guidelines(self) -> str: ...

    @agent_instructions
    def gather(self, topic: str) -> str:
        """Gather notes on {{topic}} for the {{self.beat}} beat."""
        """Find 3-5 distinct facts or quotes. Record each with add_note."""
        self.add_note()
        return f"gathered notes on {topic}"

    @agent_instructions
    def file_report(self, headline: str) -> str:
        """Write a field report with the headline: {{headline}}."""
        self.style
        self.guidelines
        self.read_notes()
        self.clear_notes()
        return f"report filed: {headline}"
