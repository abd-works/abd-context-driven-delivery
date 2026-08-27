# @toolset-manifest python -m tools manifest primitives.examples.reporter:Reporter
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Integrated example - @toolset, @agent_tool, @resource, @instruction (all three forms), @agent_instructions."""
from __future__ import annotations

import inspect
from pathlib import Path

from primitives.actions.action import agent_instructions, agentic_toolset
from primitives.instructions import Instruction, instruction
from tools.tool import resource, agent_tool


@agentic_toolset
class Reporter:
    """Gather notes and file field reports.

    Resources expose live state. Tools are called by the AI directly.
    Instruction slots load prose from markdown assets. Actions are
    recipes interpreted by the AI - the body is never executed by Python.
    """

    def __init__(self, beat: str) -> None:
        self._beat = beat
        self._notes: list[str] = []
        super().__init__()

    # -- module_dir: required by @instruction to resolve markdown assets ------
    @property
    def module_dir(self) -> Path:
        """Directory containing this class's source - used by @instruction to locate assets."""
        return Path(inspect.getfile(type(self))).resolve().parent

    # -- @resource - observable state -----------------------------------------
    # The AI reads these between tool calls to inform its decisions.

    @property
    @resource
    def beat(self) -> str:
        """The news beat this reporter covers."""
        return self._beat

    @property
    @resource
    def note_count(self) -> int:
        """Number of field notes collected so far."""
        return len(self._notes)

    # -- @agent_tool - directly callable by the AI ----------------------------------
    # Python executes these; results are returned to the AI as tool outputs.

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

    # -- @instruction - content slots -----------------------------------------
    # Three forms - all resolved automatically; bodies are always `...`.

    # Form B - section: "style" -> title-case "Style" -> ## Style in reporter.md
    @instruction
    def style(self) -> Instruction: ...

    # Form C - file: label= required because the filename contains a hyphen
    @instruction(label="house-guidelines")
    def guidelines(self) -> Instruction: ...

    # -- @agent_instructions - AI-orchestrated recipes ------------------------------------
    # Body is AST-parsed into AI instructions; Python never runs it.
    # String literals -> prose. self.tool() -> tool call. self.slot() -> expanded content.

    # Form A - inline prose: each string literal in the body IS the instruction text
    @agent_instructions
    def gather(self, topic: str) -> str:
        """Gather notes on {{topic}} for the {{self.beat}} beat."""
        """Find 3-5 distinct facts or quotes. Record each with add_note."""
        self.add_note()
        return f"gathered notes on {topic}"

    # Named slots in an action: expanded and injected before the AI sees the recipe
    @agent_instructions
    def file_report(self, headline: str) -> str:
        """Write a field report with the headline: {{headline}}."""
        self.style()        # -> expands # Style section from reporter.md
        self.guidelines()   # -> expands house-guidelines.md
        self.read_notes()
        self.clear_notes()
        return f"report filed: {headline}"
