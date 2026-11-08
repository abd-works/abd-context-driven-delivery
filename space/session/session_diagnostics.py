"""Session MCP diagnostics — deployable alongside ``Session``, not mixed into practice toolsets."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.agent_tools.agent_tools import agent_instructions, agent_tool, agent_toolset
from harness.diagnostics.call_diagnostics import CallDiagnostics
from harness.installation.files import command, skill
from harness.mcp.mcp_server import mcp

if TYPE_CHECKING:
    from harness.installation.install_diagnostics import InstallDiagnostics


@agent_toolset
class SessionDiagnostics(CallDiagnostics):
    """Probe session logging (generate, validate, loops, chat pointers). Made for one call, as every diagnostics
    toolset is, so it writes the report into the install of the project that call names."""

    @mcp
    @skill
    @command("session-diagnostics")
    @agent_tool
    @agent_instructions
    def session_diagnostics(self) -> str:
        """Probe session action logging in a temp session; append results under ``session`` in ``diagnostics.json``.

        Run via MCP ``session-diagnostics.session_diagnostics`` or slash ``/session-diagnostics``.
        Read ``.cursor/diagnostics.json`` → ``session`` for pass/fail and log tail."""
        return self.write_to(self._installer.diagnostics)

    def write_to(self, diagnostics: InstallDiagnostics) -> str:
        """Run the session-log probe and write its result as the ``session`` section of diagnostics, an install's
        diagnostics.json; the result's colour and report."""
        from space.session.session_probe import SessionProbe

        payload = SessionProbe().run()
        diagnostics.write_section("session", payload)
        return f"{payload['color']}\n{payload['report']}"
