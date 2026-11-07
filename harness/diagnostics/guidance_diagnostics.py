"""Deployable guidance MCP diagnostics — not inherited by practice toolsets."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.installation.files import command, skill
from harness.mcp.mcp_server import mcp


@agent_toolset
class GuidanceDiagnostics:
    """Probe installed guidance instructions and guidance-action MCP operations."""

    @mcp
    @skill
    @command("guidance-diagnostics")
    @agent_tool
    def guidance_diagnostics(self, guidance: list[str] | None = None) -> str:
        """Probe installed guidance instruction prompts and guidance-action MCP tools; append results under ``guidance`` in ``diagnostics.json``.

        guidance: practice and fidelity slugs to filter (for example ``stories`` and ``clean-engineering-model``). Omit to use the default probe pair.

        Run via MCP ``guidance-diagnostics.guidance_diagnostics`` or slash ``/guidance-diagnostics``. Read ``.cursor/diagnostics.json`` → ``guidance`` for pass/fail per MCP name. Session logging uses ``/session-diagnostics``."""
        from harness.diagnostics.guidance_probe import GuidanceProbe
        from harness.installer.installer import Installer

        probe = GuidanceProbe.filtered_by(Installer(), guidance)
        return "\n\n".join((probe.instructions(), probe.actions()))
