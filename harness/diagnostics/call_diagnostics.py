"""CallDiagnostics: what every diagnostics toolset holds for the one call it answers."""

from __future__ import annotations

from functools import cached_property

from harness.agent_tools.tool_call import ToolCall
from harness.installation.installer import Installer


class CallDiagnostics:
    """A diagnostics toolset made for one call: it holds the call, so it probes through the MCP host answering it, and
    the install of the project the call names, made once, whose published files the probe reads and whose diagnostics
    it writes its section into."""

    def __init__(self, call: ToolCall | None = None) -> None:
        self._call = call or ToolCall()

    def for_call(self, call: ToolCall) -> CallDiagnostics:
        return type(self)(call)

    @cached_property
    def _installer(self) -> Installer:
        return Installer(repo=self._call.project)
