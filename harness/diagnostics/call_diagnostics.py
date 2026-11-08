"""CallDiagnostics: what every diagnostics toolset holds for the one call it answers."""

from __future__ import annotations

from functools import cached_property

from harness.agent_tools.tool_call import ToolCall
from harness.installation.installer import Installer


class DiagnosticsNeedACall(Exception):
    """A diagnostics toolset was asked to probe without the call it answers, so it cannot tell which project's install
    to probe or which MCP host to probe through."""

    def __init__(self, toolset: object) -> None:
        super().__init__(f"{type(toolset).__name__} probes only for a call; the MCP server makes it with for_call(call)")


class CallDiagnostics:
    """A diagnostics toolset made for one call: it holds the call, so it probes through the MCP host answering it, and
    the install of the project the call names, made once, whose published files the probe reads and whose diagnostics
    it writes its section into. The toolset an install publishes is made with no call; it answers each call with
    ``for_call``, and refuses to probe without one rather than probe whatever folder the server runs in."""

    def __init__(self, call: ToolCall | None = None) -> None:
        self._call = call

    def for_call(self, call: ToolCall) -> CallDiagnostics:
        return type(self)(call)

    @property
    def call(self) -> ToolCall:
        """The call this toolset answers; raises *DiagnosticsNeedACall* for the toolset an install publishes."""
        if self._call is None:
            raise DiagnosticsNeedACall(self)
        return self._call

    @cached_property
    def _installer(self) -> Installer:
        return Installer(repo=self.call.project)
