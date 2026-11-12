"""Deployable MCP diagnostics for the full installed tool catalog — not inherited by practice toolsets."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.diagnostics.call_diagnostics import CallDiagnostics
from harness.installation.files import command, skill
from harness.mcp.mcp_annotations import long_call, mcp


@agent_toolset
class AgentToolsDiagnostics(CallDiagnostics):
    """Probe workspace MCP tools on the install host (space, harness, tools — ping + invoke). Made for one call, so
    it probes through the MCP host answering that call, the install of the project that call names."""

    @mcp
    @long_call
    @skill
    @command("agent-tools-diagnostics")
    @agent_tool
    def agent_tools_diagnostics(self, guidance: list[str] | None = None) -> str:
        """Probe space, harness, and tools MCP tools through the live host; append results under ``agent_tools`` in ``diagnostics.json``.

        guidance: optional slugs when a harness tool needs ``guidance`` probe arguments. Practices, patterns, builders, and ``harness.guidance`` / ``harness.guidance_actions`` base toolsets are out of scope — use ``/guidance-diagnostics`` for those.

        All probes use the live CDD MCP host already loaded in the IDE. Diagnostics do not run git clean/switch on the repo (avoids lock hangs). Light invoke uses ``_cdd-diagnostic-probe`` args where needed. It pings and does not call ``repo.push_commit`` (git), or ``installer.install`` and ``installer.clean`` (use the ``/install`` and ``/clean`` shell commands); it leaves the ``session.``, ``sessions.``, ``graph.``, ``partition.``, ``catalog.``, and ``repo.`` tools to the heavy phase or skips them as mutating. Heavy session/graph uses ``cdd-diagnostic``. Progress on stderr: ``[agent-tools] phase tool: detail``. Slash or MCP ``agent-tools-diagnostics.agent_tools_diagnostics``. Read ``diagnostics.json`` in the IDE folder the install wrote (such as ``.claude/`` or ``.cursor/``) → ``agent_tools``."""
        from harness.diagnostics.agent_tools_probe import AgentToolsProbe

        return AgentToolsProbe(self._installer, guidance, mcp_host=self.call.mcp_host, project=self.call.project).run()
