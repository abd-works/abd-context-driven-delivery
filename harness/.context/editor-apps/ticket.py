"""Module: space/kanban. Model delta (clean-engineering-model, python): *Ticket*, *FidelityProgress*.
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


class FidelityProgress:
    @property
    @data_field
    def editor(self) -> App | None:
        # its practice's editor on the practice's first fidelity row only; none on every other row
        # -> self.practice.editor
        ...
