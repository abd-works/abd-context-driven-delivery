"""Module: space/kanban. Model delta (clean-engineering-model, python): *Ticket*, *BoardPractice*, *BoardFidelity*.
Canonical: harness/.context/editor-apps/.context/editor-apps-model.md#ticket-extended
Deleted: BoardPage and its rebuild (now App.install of the CDD Kanban's App)."""
from __future__ import annotations

from harness.agent_tools import agent_tool
from harness.diagnostics.app import App
from harness.installation.data_class import data_field
from harness.mcp.mcp_server import mcp


class Ticket:
    @mcp
    @agent_tool
    def choose_formats(self, fidelities: list[str], label: str, is_chosen: bool) -> list[FormatChoice]:
        # -> fidelity.session_output.choose_format (each fidelity the chip covers)
        ...


class BoardPractice:
    @property
    @data_field
    def editor(self) -> App | None:
        # the app that edits the practice's files, which the chat bar's file viewer opens every file of the practice in
        # -> self._practice.editor
        ...


class BoardFidelity:
    @property
    @data_field
    def editor(self) -> App | None:
        # its practice's editor on the practice's first fidelity only; none on every other fidelity
        # -> self._catalogued.practice.editor
        ...
