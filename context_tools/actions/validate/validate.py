# @toolset-manifest python -m tools manifest validate.validate:Validate
# @toolset-manifest python -m tools manifest validate.validate:CreateRule
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Validate and CreateRule — run on each provided context tool."""

from __future__ import annotations

from harness.harness_tool import prompt
from lifecycle import LifecycleAction
from primitives.actions.action import agent_instructions, agentic_toolset
from workspace import SessionLog


@agentic_toolset
class Validate(LifecycleAction):
    """Validate artifacts for provided context tools."""

    @prompt
    @agent_instructions
    def validate(self, tools: list) -> str:
        """validate"""
        self.begin(tools, action="validate")
        for tool in self.context_tools(tools):
            tool.contexts
            tool.scanner.scan()
            SessionLog.instance().append(
                toolset=type(tool).manifest_path,
                name="validate",
                summary="validate",
                ok=True,
                role="run",
            )
        self.end()
        return "Validation report for artifacts under {session.path}/."


@agentic_toolset
class CreateRule(LifecycleAction):
    """Write a named rule and scanner into the provided context tool."""

    @prompt(name="createRule")
    @agent_instructions
    def createRule(self, tools: list, failed: str, wanted: str) -> str:
        """createRule"""
        self.begin(tools, action="createRule")
        for tool in self.context_tools(tools):
            tool.contexts
            tool.examples
            tool.templates
            SessionLog.instance().append(
                toolset=type(tool).manifest_path,
                name="createRule",
                summary="createRule",
                ok=True,
                role="run",
            )
        self.end()
        return (
            "Write a new named rule and matching scanner into this tool. "
            "Then run that rule via scan on the asset and detect a failure "
            "that matches the Mistake."
        )
