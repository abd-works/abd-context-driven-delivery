# @toolset-manifest python -m tools manifest render.render:Render
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Render — convert already-generated content on each provided context tool."""

from __future__ import annotations

from harness.harness_tool import prompt
from lifecycle import LifecycleAction
from primitives.actions.action import agentic_toolset
from tools.tool import agent_tool


@agentic_toolset
class Render(LifecycleAction):
    """Render already-generated output for provided context tools."""

    @prompt
    @agent_tool
    def render(self, tools: list, format: str, content: str = "") -> list:
        self.begin(tools, action="render")
        results = []
        for tool in self.context_tools(tools):
            results.append(tool.render(format, content))
        self.end()
        return results
