# @toolset-manifest python -m tools manifest satisfy.satisfy:Satisfy
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Satisfy — validate then generate fixes on each provided context tool."""

from __future__ import annotations

from harness.harness_tool import prompt
from lifecycle import LifecycleAction
from primitives.actions.action import agent_instructions, agentic_toolset
from workspace import SessionLog


@agentic_toolset
class Satisfy(LifecycleAction):
    """Satisfy artifacts for provided context tools."""

    @prompt
    @agent_instructions
    def satisfy(self, tools: list) -> str:
        """satisfy"""
        self.begin(tools, action="satisfy")
        from validate.validate import Validate

        for tool in self.context_tools(tools):
            Validate().validate(tools=[tool])
            tool.generate_fixes_from_validate()
            SessionLog.instance().append(
                toolset=type(tool).manifest_path,
                name="satisfy",
                summary="satisfy",
                ok=True,
                role="run",
            )
        self.end()
        return "When done, run validate on artifacts under {session.path}/."
