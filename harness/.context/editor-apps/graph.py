"""Module: harness/graph. Model delta (clean-engineering-model, python): *Graph*.
Canonical: harness/.context/editor-apps/.context/editor-apps-model.md#graph-extended"""
from __future__ import annotations

from harness.agent_tools import agent_tool
from harness.agent_tools.tool_call import ToolCall
from harness.mcp.mcp_server import mcp


class Graph:
    # a session's graph holds only the practices its session enabled, so this never reads a practice turned off

    @mcp
    @agent_tool
    def load_practice_roots(self, call: ToolCall | None = None) -> GraphLoaded:
        # -> practice.session_root (each practice held; one with none, or whose folder is not written yet, is left out)
        # -> self.build.load
        ...
