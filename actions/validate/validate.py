"""Validate and CreateRule — run on each provided context tool."""

from __future__ import annotations

from typing import Any

from lifecycle import LifecycleAction
from agent_tools import agent_instructions, agent_toolset, instructions
from installation.harness_files.harness_files import skill
from installation.mcp.mcp_server import mcp
from scan.rule import Rule
from workspace import SessionLog

@agent_toolset
class Validate(LifecycleAction):
    """Validate artifacts for provided context tools."""

    @mcp
    @skill
    @agent_instructions
    def validate(self, tools: Any, rule: Rule | None = None) -> str:
        """Check the listed context tools' artifacts against their rules. Pass a single Rule to check only that rule; otherwise walk each tool's rules collection and return a validation report."""
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

    @mcp
    @skill
    @agent_instructions
    def createRule(self, tools: list, failed: str, wanted: str) -> str:
        """Add a named rule and matching scanner to each listed context tool from a failed example and the wanted behavior. Then scan the asset with that rule so the same mistake is detected."""
        self.begin(tools, action="createRule")
        for tool in self.listed():
            tool.contexts
            tool.examples
            tool.templates
            SessionLog.instance().append(
                toolset=tool.registration_name,
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
