"""Module: harness/diagnostics. Model delta (clean-engineering-model, python): *ServerHealth*.
Canonical: harness/.context/editor-apps/.context/editor-apps-model.md#serverhealth-extended
Deleted: kanban_app_port, kanban_app_url, graph_app_port, reports_graph_app_on, reports_kanban_app_on, and the
constructor's graph_ports and kanban_ports parameters."""
from __future__ import annotations

from harness.installation.app import App
from harness.installation.data_class import data_field


class ServerHealth:
    """Report the parts of CDD that run outside this MCP host."""

    @property
    @data_field
    def apps(self) -> list[App]:
        # -> App.registered
        ...
