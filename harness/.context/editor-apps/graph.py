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
        # -> practice.session_roots (each practice held; one with none, or whose folders are not written yet, is left out)
        # -> self.reads.practice_roots: the files under every practice's roots, each practice opened on the project
        ...
