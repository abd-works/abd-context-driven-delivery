"""The running parts of CDD that a person needs to see are up: the Kanban app, the graph app, and the hook server."""
from __future__ import annotations

import socket
from pathlib import Path

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.hooks.hook_daemon import HookDaemon
from harness.hooks.hook_server import HookServer
from harness.installation.destination import data_field, language_adapter
from harness.mcp.mcp_server import mcp
from scripts.instances import GRAPH_APP_PORTS

PROBE_SECONDS = 0.2
# The session board's own port, set in harness/kanban/app/packages/session-board/serve.ts.
KANBAN_APP_PORTS = (8778,)


@language_adapter(language="typescript")
@agent_toolset
class ServerHealth:
    """Report the parts of CDD that run outside this MCP host, so a person can see what is up without opening a terminal."""

    # The server health band reads this after every cdd call and every prompt, so its tool stays out of the session log.
    # This tool answers only while the MCP host is up, so the band itself works out that the host is lost.

    def __init__(
        self,
        repo_root: Path | str,
        graph_ports: tuple[int, ...] = GRAPH_APP_PORTS,
        kanban_ports: tuple[int, ...] = KANBAN_APP_PORTS,
    ) -> None:
        self._repo_root = Path(repo_root).resolve()
        self._kanban_ports = kanban_ports
        self._graph_ports = graph_ports

    @classmethod
    @tool_subject
    def current(cls) -> ServerHealth:
        """The health of the project being worked on."""
        from space.work_state import project_checkout

        return cls(project_checkout())

    @mcp
    @agent_tool
    @noSessionLog
    def report(self) -> ServerHealth:
        """Return whether the Kanban app, the graph app, and the hook server are running, and which port each app answers on."""
        return self

    @property
    @data_field
    def kanban_app_port(self) -> int | None:
        return self._first_answering(self._kanban_ports)

    @property
    @data_field
    def graph_app_port(self) -> int | None:
        return self._first_answering(self._graph_ports)

    @property
    @data_field
    def is_hook_server_running(self) -> bool:
        return HookDaemon().live_address(HookServer.state_path(self._repo_root)) is not None

    def _first_answering(self, ports: tuple[int, ...]) -> int | None:
        return next((port for port in ports if self._answers(port)), None)

    def _answers(self, port: int) -> bool:
        with socket.socket() as probe:
            probe.settimeout(PROBE_SECONDS)
            return probe.connect_ex(("127.0.0.1", port)) == 0
