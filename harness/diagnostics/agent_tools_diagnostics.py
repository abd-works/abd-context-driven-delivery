"""Deployable MCP diagnostics for the full installed tool catalog — not inherited by practice toolsets."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.tool_call import ToolCall
from harness.installation.files import command, skill
from harness.mcp.mcp_server import long_call, mcp

if TYPE_CHECKING:
    from harness.installation.installer import Installer


@agent_toolset
class AgentToolsDiagnostics:
    """Probe workspace MCP tools on the install host (space, harness, tools — ping + invoke). Made for one call, so
    it probes through the MCP host answering that call, the install of the project that call names."""

    def __init__(self, call: ToolCall | None = None) -> None:
        self._call = call or ToolCall()

    def for_call(self, call: ToolCall) -> AgentToolsDiagnostics:
        return type(self)(call)

    @mcp
    @long_call
    @skill
    @command("agent-tools-diagnostics")
    @agent_tool
    def agent_tools_diagnostics(self, guidance: list[str] | None = None) -> str:
        """Probe space, harness, and tools MCP tools through the live host; append results under ``agent_tools`` in ``diagnostics.json``.

        guidance: optional slugs when a harness tool needs ``guidance`` probe arguments. Practices, patterns, builders, and ``harness.guidance`` / ``harness.guidance_actions`` base toolsets are out of scope — use ``/guidance-diagnostics`` for those.

        All probes use the live CDD MCP host already loaded in the IDE. Diagnostics do not run git clean/switch on the repo (avoids lock hangs). Light invoke uses ``_cdd-diagnostic-probe`` args where needed; only ``repo.push_commit`` and ``repo.close_*`` are skipped. Heavy session/graph uses ``cdd-diagnostic``. Progress on stderr: ``[agent-tools] phase tool: detail``. Slash or MCP ``agent-tools-diagnostics.agent_tools_diagnostics``. Read ``.cursor/diagnostics.json`` → ``agent_tools``."""
        from harness.diagnostics.agent_tools_probe import AgentToolsProbe

        return AgentToolsProbe(self._installer, guidance, mcp_host=self._call.mcp_host, project=self._call.project).run()

    @cached_property
    def _installer(self) -> Installer:
        """The install of the project this call names, made once for the call: the probe reads what it published and
        writes its section into the install's diagnostics."""
        from harness.installation.installer import Installer

        return Installer(repo=self._call.project)
