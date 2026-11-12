"""The running parts of CDD that a person needs to see are up: the Kanban app, the graph app, and the hook server."""
from __future__ import annotations

import socket
from pathlib import Path
from typing import ClassVar

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.graph.graph_app import GRAPH_APP_PORTS
from harness.hooks.hook_daemon import HookDaemon
from harness.installation.data_class import data_field, language_adapter
from harness.mcp.mcp_annotations import mcp

PROBE_SECONDS = 0.2
_HOST = "127.0.0.1"


@language_adapter(language="typescript")
@agent_toolset
class ServerHealth:
    """Report the parts of CDD that run outside this MCP host, so a person can see what is up without opening a terminal."""

    # The server health band reads this after every cdd call and every prompt, so its tool stays out of the session log.
    # This tool answers only while the MCP host is up, so the band itself works out that the host is lost.

    # The ports each app a report probes listens on, which the module that knows the app registers from the app's own
    # ports file, the one its servers read: the graph app's below, the session board's from space/kanban, so harness
    # names no port of either and neither app's ports are written twice.
    _registered_graph_ports: ClassVar[tuple[int, ...]] = ()
    _registered_kanban_ports: ClassVar[tuple[int, ...]] = ()

    @classmethod
    def reports_graph_app_on(cls, ports: tuple[int, ...]) -> None:
        """Have every report probe the graph app on ports, the ones its Vite server tries in turn."""
        ServerHealth._registered_graph_ports = tuple(ports)

    @classmethod
    def reports_kanban_app_on(cls, ports: tuple[int, ...]) -> None:
        """Have every report probe the Kanban app (the session board) on ports, the ones its server listens on."""
        ServerHealth._registered_kanban_ports = tuple(ports)

    def __init__(
        self,
        repo_root: Path | str,
        graph_ports: tuple[int, ...] | None = None,
        kanban_ports: tuple[int, ...] | None = None,
        hook_daemon: HookDaemon | None = None,
    ) -> None:
        self._repo_root = Path(repo_root).resolve()
        self._kanban_ports = kanban_ports if kanban_ports is not None else ServerHealth._registered_kanban_ports
        self._graph_ports = graph_ports if graph_ports is not None else ServerHealth._registered_graph_ports
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
        """Return whether the Kanban app, the graph app, and the hook server are running, and which port each app answers on."""
        return self

    @property
    @data_field
    def kanban_app_port(self) -> int | None:
        return self._first_answering(self._kanban_ports)

    @property
    @data_field
    def kanban_app_url(self) -> str:
        """Where a chat reaches the Kanban app: on the port it answers on, else on the port its server starts on; empty
        when the board registered no port."""
        port = self.kanban_app_port or next(iter(self._kanban_ports), None)
        return f"http://{_HOST}:{port}" if port is not None else ""

    @property
    @data_field
    def graph_app_port(self) -> int | None:
        return self._first_answering(self._graph_ports)

    @property
    @data_field
    def is_hook_server_running(self) -> bool:
        return self._hook_daemon.is_running()

    def _first_answering(self, ports: tuple[int, ...]) -> int | None:
        return next((port for port in ports if self._answers(port)), None)

    def _answers(self, port: int) -> bool:
        with socket.socket() as probe:
            probe.settimeout(PROBE_SECONDS)
            return probe.connect_ex((_HOST, port)) == 0


# Server health probes the graph app where its servers listen, registered as the session board registers its own.
ServerHealth.reports_graph_app_on(GRAPH_APP_PORTS.of("app"))
