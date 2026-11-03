"""The running parts of CDD that a person needs to see are up: the Kanban app, the graph app, and the hook server."""
from __future__ import annotations

import os
import socket
from pathlib import Path
from typing import TypedDict

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.hooks.hook_daemon import HookDaemon
from harness.hooks.hook_server import HookServer
from harness.installation.destination import language_adapter
from harness.mcp.mcp_server import mcp
from scripts.instances import GRAPH_APP_PORTS

PROBE_SECONDS = 0.2
# The session board's own port, set in harness/kanban/app/packages/session-board/serve.ts.
KANBAN_APP_PORTS = (8778,)


class ServerHealthData(TypedDict):
    kanban_app_port: int | None
    graph_app_port: int | None
    is_hook_server_running: bool


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
        """The health of the project being worked on: `CDD_PROJECT`, else the current folder."""
        return cls(Path(os.environ.get("CDD_PROJECT") or os.getcwd()))

    @mcp
    @agent_tool
    @noSessionLog
    def report(self) -> ServerHealth:
        """Return whether the Kanban app, the graph app, and the hook server are running, and which port each app answers on."""
        return self

    @property
    def kanban_app_port(self) -> int | None:
        return self._first_answering(self._kanban_ports)

    @property
    def graph_app_port(self) -> int | None:
        return self._first_answering(self._graph_ports)

    @property
    def is_hook_server_running(self) -> bool:
        return HookDaemon().live_address(HookServer.state_path(self._repo_root)) is not None

    def to_json(self) -> ServerHealthData:
        return {
            "kanban_app_port": self.kanban_app_port,
            "graph_app_port": self.graph_app_port,
            "is_hook_server_running": self.is_hook_server_running,
        }

    def _first_answering(self, ports: tuple[int, ...]) -> int | None:
        return next((port for port in ports if self._answers(port)), None)

    def _answers(self, port: int) -> bool:
        with socket.socket() as probe:
            probe.settimeout(PROBE_SECONDS)
            return probe.connect_ex(("127.0.0.1", port)) == 0
