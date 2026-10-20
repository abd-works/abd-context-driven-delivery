"""Deployable MCP diagnostics for the full installed tool catalog — not inherited by practice toolsets."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.installation.files import command, skill
from harness.mcp.mcp_server import mcp


@agent_toolset
class AgentToolsDiagnostics:
    """Probe workspace MCP tools on the install host (space, harness, tools — ping + invoke)."""

    @mcp
    @skill
    @command("agent-tools-diagnostics")
    @agent_tool
    def agent_tools_diagnostics(self, guidance: list[str] | None = None) -> str:
        """Probe space, harness, and tools MCP tools through the live host; append results under ``agent_tools`` in ``diagnostics.json``.

        guidance: optional slugs when a harness tool needs ``guidance`` probe arguments. Practices, patterns, builders, and ``harness.guidance`` / ``harness.guidance_actions`` base toolsets are out of scope — use ``/guidance-diagnostics`` for those.

        All probes use the live CDD MCP host already loaded in Cursor. Diagnostics do not run git clean/switch on the repo (avoids lock hangs). Light invoke uses ``_cdd-diagnostic-probe`` args where needed; only ``repo.push`` and ``repo.close_*`` are skipped. Heavy session/graph uses ``cdd-diagnostic``. Progress on stderr: ``[agent-tools] phase tool: detail``. Slash or MCP ``agent-tools-diagnostics.agent_tools_diagnostics``. Read ``.cursor/diagnostics.json`` → ``agent_tools``."""
        from harness.agent_tools.agent_tools_probe import probe_agent_tools
        from harness.installation.installer import Installer

        return probe_agent_tools(Installer(), guidance)
