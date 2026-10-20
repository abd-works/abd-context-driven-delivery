"""Session MCP diagnostics — deployable alongside ``Session``, not mixed into practice toolsets."""

from __future__ import annotations

from typing import Any

from harness.agent_tools.agent_tools import agent_instructions, agent_tool, agent_toolset
from harness.installation.files import command, skill
from harness.mcp.mcp_server import mcp


def write_session_diagnostics(installer: Any) -> str:
    from space.session.session_probe import probe_session_log

    payload = probe_session_log()
    installer.write_diagnostics_section("session", payload)
    color = str(payload.get("color", "red"))
    return f"{color}\n{payload.get('report', '')}"


@agent_toolset
class SessionDiagnostics:
    """Probe session logging (generate, validate, loops, chat pointers)."""

    @mcp
    @skill
    @command("session-diagnostics")
    @agent_tool
    @agent_instructions
    def session_diagnostics(self) -> str:
        """Probe session action logging in a temp session; append results under ``session`` in ``diagnostics.json``.

        Run via MCP ``session-diagnostics.session_diagnostics`` or slash ``/session-diagnostics``.
        Read ``.cursor/diagnostics.json`` → ``session`` for pass/fail and log tail."""
        from harness.installation.installer import Installer

        return write_session_diagnostics(Installer())
