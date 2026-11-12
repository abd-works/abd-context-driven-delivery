"""The running parts of CDD that a person needs to see are up: each registered app, and the hook server."""
from __future__ import annotations

from pathlib import Path

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.diagnostics.app import App
from harness.hooks.hook_daemon import HookDaemon
from harness.installation.data_class import data_field, language_adapter
from harness.mcp.mcp_server import mcp


@language_adapter(language="typescript")
@agent_toolset
class ServerHealth:
    """Report the parts of CDD that run outside this MCP host, so a person can see what is up without opening a terminal."""

    # The server health band reads this after every cdd call and every prompt, so its tool stays out of the session log.
    # This tool answers only while the MCP host is up, so the band itself works out that the host is lost.

    def __init__(self, repo_root: Path | str, hook_daemon: HookDaemon | None = None) -> None:
        self._repo_root = Path(repo_root).resolve()
        self._hook_daemon = hook_daemon if hook_daemon is not None else HookDaemon(self._repo_root)

    @classmethod
    @tool_subject
    def load(cls, *, project: Path | str) -> ServerHealth:
        """The health of project, the folder the call names."""
        return cls(project)

    @mcp
    @agent_tool
    @noSessionLog
    def report(self) -> ServerHealth:
        """Return each registered app with its status and the port it answers on, and whether the hook server is running."""
        return self

    @property
    @data_field
    def apps(self) -> list[App]:
        """Every app a module registered, each read as it is now."""
        return App.registered()

    @property
    @data_field
    def is_hook_server_running(self) -> bool:
        return self._hook_daemon.is_running()
