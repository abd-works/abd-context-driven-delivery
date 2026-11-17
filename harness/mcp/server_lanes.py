"""The two cdd servers: the stable lane runs main for chats in a main checkout, the dev lane runs the one served feature
for every other chat (``.context/cdr/0003-two-lanes-main-stable-features-dev.md``)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from harness.agent_tools.tool_call import ToolCall
from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_address import BUILTIN_LIST_TOOLS, DEV_LANE_FOLDER, DEV_PORT_AFTER_STABLE, McpAddress
from harness.mcp.mcp_daemon import McpDaemon, ServedCheckout

# How long the stable lane waits for the dev lane to answer one tool call. The chat is told a call is still running at
# the tool's own time limit; this only bounds how long the stable lane's worker thread keeps waiting after that.
LANE_CALL_SECONDS = 60 * 60


class LaneCallFailed(Exception):
    """The dev lane's server answered a tool call with a failure; the failure keeps the kind and message it had there."""

    def __init__(self, lane: str, tool: str, failure: dict[str, str]) -> None:
        super().__init__(f"{tool} failed on the {lane} lane: {failure.get('kind', 'Exception')}: {failure.get('message', '')}")
        self.lane = lane
        self.tool = tool
        self.kind = failure.get("kind", "")


class LaneCall:
    """A chat's tool call as one lane hands it to another: the tool, its arguments, the project it works on, and the
    chat that sent it. The receiving lane builds its own *ToolCall* from it."""

    def __init__(self, tool: str, arguments: dict[str, Any], project: str, chat: str) -> None:
        self.tool = tool
        self.arguments = arguments
        self.project = project
        self.chat = chat

    @classmethod
    def from_call(cls, call: ToolCall) -> LaneCall:
        return cls(call.request.tool, dict(call.arguments), str(call.project or ""), call.chat_id)

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> LaneCall:
        return cls(str(data.get("tool") or ""), dict(data.get("arguments") or {}), str(data.get("project") or ""), str(data.get("chat") or ""))

    @property
    def as_data(self) -> dict[str, Any]:
        return {"tool": self.tool, "arguments": self.arguments, "project": self.project, "chat": self.chat}


class ServerLane:
    """One cdd server: the home whose runtime record names the code it runs, the port it answers on, and how far the
    app servers its chats start sit from the ports their ports files give them, so the two lanes' apps never meet."""

    def __init__(self, name: str, home: CddHome, address: McpAddress, app_port_offset: int = 0) -> None:
        self.name = name
        self.daemon = McpDaemon(home, address)
        self._app_port_offset = app_port_offset

    @classmethod
    def from_home(cls, home: CddHome | None = None) -> ServerLane:
        """The lane the server running from home serves, by default the home this process runs from: the dev lane when
        home is the dev lane's, else the stable lane."""
        running_from = home or CddHome()
        lanes = ServerLanes.from_serving(running_from)
        return lanes.dev if lanes.dev.home.folder == running_from.folder else lanes.stable

    @property
    def home(self) -> CddHome:
        return self.daemon.home

    @property
    def port(self) -> int:
        return self.daemon.port

    def app_ports(self, ports: tuple[int, ...]) -> tuple[int, ...]:
        """The ports an app server whose ports file gives it ports answers on in this lane."""
        return tuple(port + self._app_port_offset for port in ports)

    def served_checkout(self, checkout: Path) -> ServedCheckout:
        """``checkout`` as this lane installs and serves it."""
        return ServedCheckout(self.daemon, checkout)

    def tools_for(self, project: Path) -> list[dict[str, Any]]:
        """The tools this lane's server serves, as data, listed for a chat working on project, starting the server first
        when none answers."""
        self.daemon.ensure()
        reply = self.daemon.address.send_lane_call(LaneCall(BUILTIN_LIST_TOOLS, {}, str(project), "").as_data, LANE_CALL_SECONDS)
        if reply.get("failure"):
            raise LaneCallFailed(self.name, BUILTIN_LIST_TOOLS, reply["failure"])
        return list(reply.get("answer") or [])

    def answer(self, call: ToolCall) -> object:
        """Have this lane's server answer call, starting it first when none answers."""
        self.daemon.ensure()
        reply = self.daemon.address.send_lane_call(LaneCall.from_call(call).as_data, LANE_CALL_SECONDS)
        if reply.get("failure"):
            raise LaneCallFailed(self.name, call.request.tool, reply["failure"])
        return reply.get("answer")


class ServerLanes:
    """Which lane a project's chats run on. A main checkout, the folder whose ``.git`` is a directory, runs on the stable
    lane; every other project, a ticket's worktree or a folder outside any checkout, runs on the dev lane. The lane
    follows from the folder, so no chat has to choose it."""

    STABLE = "stable"
    DEV = "dev"
    # The dev lane's app servers answer this far above the stable lane's, on ports no app's ports file names, so a
    # feature's Files, board, and Graph servers run beside main's.
    DEV_APP_PORT_OFFSET = 1000

    def __init__(self, home: CddHome | None = None, address: McpAddress | None = None, dev_address: McpAddress | None = None) -> None:
        stable_home = home or CddHome()
        stable_address = address or McpAddress()
        self.stable = ServerLane(self.STABLE, stable_home, stable_address)
        self.dev = ServerLane(
            self.DEV,
            CddHome(stable_home.folder / DEV_LANE_FOLDER),
            dev_address or McpAddress(stable_address.port + DEV_PORT_AFTER_STABLE),
            self.DEV_APP_PORT_OFFSET,
        )

    @classmethod
    def from_serving(cls, home: CddHome, address: McpAddress | None = None) -> ServerLanes:
        """The lanes as the server running from home on address sees them, whichever of the two it is; with no address,
        on the lanes' own ports."""
        if home.folder.name != DEV_LANE_FOLDER:
            return cls(home, address)
        stable_address = McpAddress(address.port - DEV_PORT_AFTER_STABLE) if address is not None else None
        return cls(CddHome(home.folder.parent), stable_address)

    def for_project(self, project: Path) -> ServerLane:
        if self._is_in_main_checkout(Path(project).resolve()):
            return self.stable
        return self.dev

    def other_lane_answering(self, serving: CddHome, project: Path | None) -> ServerLane | None:
        """The lane that answers project's calls instead of the server running from serving: the dev lane, when serving
        is the stable lane, project belongs to the dev lane, and a feature is served there. Until one is, the dev
        lane's chats run on main, so the stable lane answers them itself."""
        if project is None or serving.folder != self.stable.home.folder:
            return None
        if self.for_project(project) is not self.dev or not self.dev.home.is_installed:
            return None
        return self.dev

    def _is_in_main_checkout(self, project: Path) -> bool:
        for folder in (project, *project.parents):
            marker = folder / ".git"
            if marker.exists():
                return marker.is_dir()
        return False
