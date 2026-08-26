# @toolset-manifest python -m tools manifest satisfy.satisfy:Satisfy
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Satisfy — validate then generate fixes on each provided context tool."""

from __future__ import annotations

from lifecycle import LifecycleAction
from primitives.actions.action import agent_instructions, agentic_toolset
from workspace import SessionLog


@agentic_toolset
class Satisfy(LifecycleAction):
    """Satisfy artifacts for provided context tools."""

    @agent_instructions
    def satisfy(self, tools: list) -> str:
        """runs on each provided context tool"""
        self.begin(tools, action="satisfy")
        for tool in self.context_tools(tools):
            tool.mode = "tool"
            validate = getattr(tool, "validate", None)
            if validate is not None:
                validate()
            generate_fixes = getattr(tool, "generate_fixes_from_validate", None)
            if generate_fixes is not None:
                generate_fixes()
            SessionLog.instance().append(
                toolset=type(tool).manifest_path,
                name="satisfy",
                summary="satisfy",
                ok=True,
                role="run",
            )
        self.end()
        return "When done, run validate on artifacts under {session.path}/."
