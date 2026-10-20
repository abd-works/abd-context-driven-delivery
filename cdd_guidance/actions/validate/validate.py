"""Validate and CreateRule — run on each provided context tool."""

from __future__ import annotations

from pathlib import Path

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset, instructions
from harness.installation.destination import noDeploy
from harness.installation.files import Skill
from harness.mcp.mcp_server import Mcp
from harness.guidance import Rule

_VALIDATE_MARKDOWN = Path(__file__).with_name("validate.md").read_text(encoding="utf-8")

@agent_toolset
class Validate(GuidanceAction):
    """Validate artifacts for provided context tools."""

    @Mcp
    @Skill
    @agent_instructions
    def validate(self, guidance: GuidanceArg, rule: Rule | None = None) -> str:
        """Check artifacts against rules.
        rule: one Rule to check. Omit it to walk each guidance's rules."""
        instructions(_VALIDATE_MARKDOWN)

        def on(item) -> str:
            if rule is not None:
                return rule.validate()
            if isinstance(item, str):
                return item
            return self._rules_for(item)

        self._bind_guidance(guidance)
        parts = [part for part in self.each(on) if part]
        self._log_validation_to_session()
        report = "Validation report for artifacts under {session.path}/."
        return "\n\n".join([_VALIDATE_MARKDOWN, *parts, report])

    def _log_validation_to_session(self) -> None:
        from space.session import Session

        session = Session.current()
        if session is None or session.session_path is None or self._guidance_text is not None:
            return
        for item in self.listed():
            session.log_validation(item, [])

    def _rules_for(self, item) -> str:
        """Shared rules plus the active fidelity's rules. Every fidelity when none is active."""
        sections: list[str] = []
        seen: set[int] = set()
        for collection in (getattr(item, "rules", None), *self._fidelity_rule_collections(item)):
            if collection is None or id(collection) in seen:
                continue
            seen.add(id(collection))
            text = self._validate_text(collection)
            if text:
                sections.append(text)
        return "\n\n".join(sections)

    def _fidelity_rule_collections(self, item) -> list:
        fidelities = getattr(item, "fidelities", None)
        if fidelities is None:
            return []
        current = getattr(fidelities, "current", None)
        if current is not None:
            rules = getattr(current, "rules", None)
            return [rules] if rules is not None else []
        return [
            rules
            for child in fidelities
            if (rules := getattr(child, "rules", None)) is not None
        ]

    def _validate_text(self, collection) -> str:
        for accessor in ("validate", "markdown_block", "markdown"):
            text = getattr(collection, accessor, None)
            if text is None:
                continue
            if callable(text):
                text = text()
            if isinstance(text, str) and text.strip():
                return text.strip()
        return ""

    @noDeploy
    @Mcp
    @Skill
    @agent_instructions
    def createRule(self, guidance: GuidanceArg, failed: str = "", wanted: str = "") -> str:
        """Add a named rule to each listed guidance from a failed example and the wanted behavior. Then validate the asset with that rule so the same mistake is detected.
        failed: path to the example that broke. Pass the file. Do not paste its body.
        wanted: path to the behavior the rule must require. Pass the file. Do not paste its body."""
        def on(item) -> None:
            if isinstance(item, str):
                return
            item.contexts
            item.examples
            item.templates

        self.run(guidance, on, action="createRule")
        return (
            "Write a new named rule into this tool. "
            "Then run collection validate on the asset and detect a failure "
            "that matches the Mistake."
        )
