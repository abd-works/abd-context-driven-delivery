"""Validate and CreateRule — run on each provided context tool."""

from __future__ import annotations

from lifecycle import GuidanceArg, LifecycleAction
from agent_tools import agent_instructions, agent_toolset
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp
from scan.rule import Rule
from workspace import SessionLog

@agent_toolset
class Validate(LifecycleAction):
    """Validate artifacts for provided context tools."""

    @Mcp
    @Skill
    @agent_instructions
    def validate(self, guidance: GuidanceArg, rule: Rule | None = None) -> str:
        """Check artifacts against rules. Pass a string to validate that text once. Pass a list of Guidance to walk each host's rules. Pass a single Rule to check only that rule."""
        def on(item) -> str:
            if rule is not None:
                return rule.validate()
            if isinstance(item, str):
                return item
            return item.rules.validate()

        parts = [part for part in self.run(guidance, on, action="validate") if part]
        report = "Validation report for artifacts under {session.path}/."
        return "\n\n".join(parts + [report])

    @Mcp
    @Skill
    @agent_instructions
    def createRule(self, guidance: GuidanceArg, failed: str, wanted: str) -> str:
        """Add a named rule and matching scanner to each listed Guidance host from a failed example and the wanted behavior. Then scan the asset with that rule so the same mistake is detected. Pass a string to create the rule against that text once."""
        def on(item) -> None:
            if isinstance(item, str):
                return
            item.contexts
            item.examples
            item.templates
            SessionLog.instance().append(
                toolset=item.registration_name,
                name="createRule",
                summary="createRule",
                ok=True,
                role="run",
            )

        self.run(guidance, on, action="createRule")
        return (
            "Write a new named rule and matching scanner into this tool. "
            "Then run that rule via scan on the asset and detect a failure "
            "that matches the Mistake."
        )
