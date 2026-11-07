"""Session MCP diagnostics — deployable alongside ``Session``, not mixed into practice toolsets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness.agent_tools.agent_tools import agent_instructions, agent_tool, agent_toolset
from harness.installation.files import command, skill
from harness.mcp.mcp_server import mcp


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
        from harness.installer.installer import Installer

        return self.write_to(Installer(repo=Path(__file__).resolve().parents[2]))

    def write_to(self, installer: Any) -> str:
        """Run the session-log probe and write its result as the ``session`` section of installer's diagnostics.json;
        the result's colour and report."""
        from space.session.session_probe import SessionProbe

        payload = SessionProbe().run()
        installer.diagnostics.write_section("session", payload)
        return f"{payload['color']}\n{payload['report']}"
