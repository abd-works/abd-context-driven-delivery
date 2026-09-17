"""Validate and CreateRule — run on each provided context tool."""

from __future__ import annotations

from typing import Any

from installer.installer_tool import prompt
from lifecycle import LifecycleAction
from agent_tools import agent_instructions, agent_toolset, instructions
from scan.rule import Rule
from workspace import SessionLog
from primitives.installer.installation import toolset_ref_for_type


@agent_toolset
class Validate(LifecycleAction):
    """Validate artifacts for provided context tools."""

    @prompt
    @agent_instructions
    def validate(self, tools: Any, rule: Rule | None = None) -> str:
        """validate"""
        if rule is not None:
            instructions(rule.validate)
        else:
            host_rules = getattr(tools, "rules", None)
            if host_rules is not None and not isinstance(tools, list):
                instructions(host_rules.validate)
            else:
                self.begin(tools, action="validate")
                for tool in self.listed():
                    instructions(tool.rules.validate)
                self.end()
        return "Validation report for artifacts under {session.path}/."


@agent_toolset
class CreateRule(LifecycleAction):
    """Write a named rule and scanner into the provided context tool."""

    @prompt(name="createRule")
    @agent_instructions
    def createRule(self, tools: list, failed: str, wanted: str) -> str:
        """createRule"""
        self.begin(tools, action="createRule")
        for tool in self.listed():
            tool.contexts
            tool.examples
            tool.templates
            SessionLog.instance().append(
                toolset=toolset_ref_for_type(type(tool)),
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
