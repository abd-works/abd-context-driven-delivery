"""Deployable guidance MCP diagnostics — not inherited by practice toolsets."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.tool_call import ToolCall
from harness.installation.files import command, skill
from harness.mcp.mcp_server import long_call, mcp


@agent_toolset
class GuidanceDiagnostics:
    """Probe installed guidance instructions and guidance-action MCP operations. Made for one call, so it probes the
    install of the project that call names."""

    def __init__(self, call: ToolCall | None = None) -> None:
        self._call = call or ToolCall()

    def for_call(self, call: ToolCall) -> GuidanceDiagnostics:
        return type(self)(call)

    @mcp
    @long_call
    @skill
    @command("guidance-diagnostics")
    @agent_tool
    def guidance_diagnostics(self, guidance: list[str] | None = None) -> str:
        """Probe installed guidance instruction prompts and guidance-action MCP tools; append results under ``guidance`` in ``diagnostics.json``.

        guidance: practice and fidelity slugs to filter (for example ``stories`` and ``clean-engineering-model``). Omit to use the default probe pair.

        Run via MCP ``guidance-diagnostics.guidance_diagnostics`` or slash ``/guidance-diagnostics``. Read ``.cursor/diagnostics.json`` → ``guidance`` for pass/fail per MCP name. Session logging uses ``/session-diagnostics``."""
        from harness.diagnostics.guidance_probe import GuidanceProbe
        from harness.installation.installer import Installer

        probe = GuidanceProbe.from_filter(Installer(repo=self._call.project), guidance)
        return "\n\n".join((probe.instructions(), probe.actions()))
