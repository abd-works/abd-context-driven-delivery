"""Render — convert already-generated content on each provided context tool."""

from __future__ import annotations

from lifecycle import LifecycleAction
from primitives.agent_tools.agent_tools import agent_toolset
from agent_tools.agent_tools import agent_tool

@agent_toolset
class Render(LifecycleAction):
    """Render already-generated output for provided context tools."""

    @agent_tool
    def render(self, tools: list, format: str, content: str = "") -> list:
        self.begin(tools, action="render")
        results = []
        for tool in self.listed():
            results.append(tool.render(format, content))
        self.end()
        return results
