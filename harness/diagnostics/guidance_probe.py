"""Probe the installed guidance for ``/guidance-diagnostics``: read each practice's and fidelity's instructions, and call
each guidance action with arguments made for the probe."""

from __future__ import annotations

from typing import Any

from harness.agent_tools.agent_tools import ToolsetReference
from harness.diagnostics.probe_arguments import ProbeArguments
from harness.guidance.action_catalogue import ActionCatalogue
from harness.diagnostics.probe_outcome import ProbeOutcome, ProbeSection

# The guidance probed when the caller names none: one practice and one fidelity of another practice.
GUIDANCE_PROBE = ["stories", "clean-engineering-model"]
GUIDANCE_SECTION = "guidance"
# Operations that write under the session's root; the probe calls them in a session of its own.
_WRITES_UNDER_SESSION_ROOT = frozenset({"sketch.save_sketch", "grill-context.write_grill_answer"})
# Actions the probe never calls, by the name each is published under, with the reason the report gives.
_LEFT_ALONE = {
    "improvement.repair": "opens a repair on real work",
    "improvement.verify_fix": "re-runs a repair's regression check on real work",
}


class GuidanceProbe:
    """A probe of the guidance one install deployed, made for its Installer and the guidance slugs that filter what it
    calls. Its arguments make the temporary files and folders the actions it calls need, and remove them after."""

    def __init__(self, installer: Any, slugs: list[str]) -> None:
        self.installer = installer
        self.slugs = list(slugs)
        self.arguments = ProbeArguments(installer.repo, self.slugs)

    @classmethod
    def from_filter(cls, installer: Any, guidance: list[str] | None) -> GuidanceProbe:
        """The probe for a diagnostics call, which probes ``GUIDANCE_PROBE`` when it names no guidance."""
        return cls(installer, list(guidance or GUIDANCE_PROBE))

    @property
    def prefixes(self) -> list[str]:
        """Each slug, then the slug of the practice it names or whose fidelity it names: `stories-story-map` adds
        `stories`, so the practice's own instructions are probed with its fidelity's."""
        from harness.guidance.practice_catalogue import PracticeCatalogue

        prefixes: list[str] = []
        for slug in self.slugs:
            practice = PracticeCatalogue.practice_named(slug)
            for prefix in (slug, practice.slug if practice is not None else ""):
                if prefix and prefix not in prefixes:
                    prefixes.append(prefix)
        return prefixes

    def matches(self, mcp_name: str) -> bool:
        """True when the MCP operation is the instructions of a practice or fidelity this probe's slugs name."""
        return any(
            mcp_name == prefix or mcp_name == f"{prefix}.instructions" or mcp_name.startswith(f"{prefix}-")
            for prefix in self.prefixes
        )

    def instructions(self) -> str:
        """Read the installed practice and fidelity instructions the slugs name, and write the result under
        ``guidance`` in diagnostics.json."""
        names = self.installer.diagnostics.installed_items("mcp")
        section = ProbeSection("instructions", [self._instructions_of(name) for name in names if self.matches(name)], self.slugs)
        self.installer.diagnostics.write_section(GUIDANCE_SECTION, {"filter": self.slugs, "instructions": section.record})
        return section.reply

    def actions(self) -> str:
        """Call each installed guidance action's MCP operations, and write the result under ``guidance`` in
        diagnostics.json."""
        published = set(self.installer.diagnostics.installed_items("mcp"))
        installed = set(self.installer.diagnostics.installed_items("toolset"))
        outcomes: list[ProbeOutcome] = []
        try:
            for toolset_class in ActionCatalogue.toolsets():
                if str(ToolsetReference.of(toolset_class)) in installed:
                    outcomes.extend(self._action_toolset(toolset_class, published))
        finally:
            self.arguments.cleanup()
        section = ProbeSection("actions", outcomes, self.slugs)
        self.installer.diagnostics.write_section(GUIDANCE_SECTION, {"filter": self.slugs, "actions": section.record})
        return section.reply

    def _instructions_of(self, mcp_name: str) -> ProbeOutcome:
        from harness.agent_tools.agent_tools import AgentToolSet
        from harness.guidance.practice_catalogue import PracticeCatalogue

        slug = mcp_name[: -len(".instructions")] if mcp_name.endswith(".instructions") else mcp_name
        ref = PracticeCatalogue.toolset_ref(slug)
        if ref is None:
            return ProbeOutcome.from_refusal(mcp_name, "not a guidance slug")
        try:
            text = AgentToolSet.instantiate(ref).instructions
        except Exception as failure:
            # A probe reports what failed: the failure is its red outcome.
            return ProbeOutcome.from_failure(mcp_name, failure)
        return ProbeOutcome.from_answer(mcp_name, text)

    def _action_toolset(self, toolset_class: type, published: set[str]) -> list[ProbeOutcome]:
        try:
            toolset = toolset_class()
        except Exception as failure:
            return [ProbeOutcome.from_failure(str(ToolsetReference.of(toolset_class)), failure)]
        return [self._action(toolset, tool) for tool in toolset.tools.values() if tool.install_to_mcp and tool.mcp_name in published]

    def _action(self, toolset: Any, tool: Any) -> ProbeOutcome:
        if tool.mcp_name in _LEFT_ALONE:
            return ProbeOutcome.from_skip(tool.mcp_name, _LEFT_ALONE[tool.mcp_name])
        if tool.mcp_name in _WRITES_UNDER_SESSION_ROOT:
            toolset = type(toolset)(session=self.arguments.work_session())
        member = getattr(toolset, tool.name)
        arguments, missing = self.arguments.for_operation(tool.mcp_name, member)
        if missing:
            return ProbeOutcome.from_refusal(tool.mcp_name, "needs " + ", ".join(missing))
        try:
            answer = member(**arguments) if tool.kind == "tool" else tool.invoke(arguments)
        except Exception as failure:
            return ProbeOutcome.from_failure(tool.mcp_name, failure)
        return ProbeOutcome.from_answer(tool.mcp_name, answer).called_on(arguments.get("paths") or [])
