"""The two Python tiers the scenarios of Integrate Practice Content Editor Apps In Chat Bar replay on.

The domain tier hands a scenario's steps *App* and *ServerHealth* themselves. The server tier hands them the same
operations through the cdd server, as the chat bar's status row reaches them: `app.open` and `server-health.report` by
their published names, JSON in and out. Each scenario registers a throwaway app in place of the real one of its label
(`ThrowawayApp`), so no scenario touches the person's own apps.

A press then does what the chat bar does with the answer (`app-client.ts`): while the app is not running, it starts
the app's server with its command in its folder and waits for its port, and the chat's end stops it. On the heavy
specs `ChatLaunch` plays that part, so they prove the command each app answers starts its server. The quick specs use
`StubbedLaunch`, which records the command and answers on the app's port from the test's own process, so they prove a
press installs, launches, and opens each app only when its status needs it, without starting a server.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from harness.agent_tools.tool_call import ToolCall
from harness.diagnostics.app import App
from harness.diagnostics.server_health import ServerHealth
from harness.installation.data_class import data_of
from harness.mcp.mcp_server import McpServer
from space.kanban.editor_apps_examples import AppExample, ThrowawayApp, ThrowawayPorts
from space.kanban.session_board_examples import SessionsProject
from space.session.sessions import Sessions

TOOLSETS = ("harness.diagnostics.app:App", "harness.diagnostics.server_health:ServerHealth")
# As long as the chat bar waits for a server it started to answer, and how often it looks.
LAUNCH_SECONDS = 20
LAUNCH_CHECK_SECONDS = 0.5


class ChatLaunch:
    """The chat bar's part of a press: start the opened app's server while it is not running, and stop it when the chat
    ends, as /board did."""

    def __init__(self) -> None:
        self._servers: list[subprocess.Popen] = []

    def opened(self, app: dict, report: Any) -> dict:
        """The app as the side panel opens it: its server started first when it was not running."""
        if app["status"] == "running":
            return app
        server = app["server"]
        self._servers.append(subprocess.Popen(server["command"], cwd=server["folder"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        deadline = time.monotonic() + LAUNCH_SECONDS
        while time.monotonic() < deadline:
            answered = next(listed for listed in report()["apps"] if listed["label"] == app["label"])
            if answered["status"] == "running":
                return answered
            time.sleep(LAUNCH_CHECK_SECONDS)
        return app

    def end(self) -> None:
        for server in self._servers:
            server.kill()
            server.wait()


class StubbedLaunch:
    """The chat bar's part of a press with no server started: an app that is not running gets its command recorded,
    and its throwaway app answers on its port from this process."""

    def __init__(self, apps: list) -> None:
        self._apps = apps
        self.started: list[tuple[list[str], str]] = []

    def opened(self, app: dict, report: Any) -> dict:
        """The app as the side panel opens it: launched first when it was not running."""
        if app["status"] == "running":
            return app
        self.started.append((app["server"]["command"], app["server"]["folder"]))
        next(throwaway for throwaway in reversed(self._apps) if throwaway.example.label == app["label"]).listen()
        return next(listed for listed in report()["apps"] if listed["label"] == app["label"])

    def end(self) -> None:
        """Each throwaway app stops answering when it closes."""


class DomainTier:
    """*App* and *ServerHealth* on a throwaway project, with nothing between a step and the domain. The project keeps
    sessions, as the Graph app's and the Story UI's calls work in the session open in it (`app_call`). A press launches
    each app's real server only when starts_servers is set, as the heavy specs do. Otherwise the machine's ports are
    stubbed too (`ThrowawayPorts`), and a stand-in replaces every registered app, so no check asks a real port."""

    name = "domain"

    def __init__(self, starts_servers: bool = False) -> None:
        self._starts_servers = starts_servers

    def open(self) -> SimpleNamespace:
        sessions_project = SessionsProject(mocks_git=True)
        project = sessions_project.root
        ports = None if self._starts_servers else ThrowawayPorts()
        apps = [] if ports is None else [ThrowawayApp(AppExample(app.label, app.page), ports) for app in App.registered()]
        chat = ChatLaunch() if self._starts_servers else StubbedLaunch(apps)
        report = lambda: data_of(ServerHealth.load(project=project).report())  # noqa: E731
        return SimpleNamespace(
            project=project,
            sessions_project=sessions_project,
            sessions=Sessions.of_project(project),
            app_call=lambda: ToolCall(project=project),
            ports=ports,
            apps=apps,
            chat=chat,
            open_app=lambda label: chat.opened(data_of(App.load(label, project=project).open()), report),
            report=report,
        )

    def close(self, world: SimpleNamespace) -> None:
        _close(world)
        world.sessions_project.close()


class ServerTier:
    """The same operations through the cdd server started on a throwaway project."""

    name = "cdd tools"

    def open(self) -> SimpleNamespace:
        project = Path(tempfile.mkdtemp(prefix="editor-apps-"))
        server = McpServer(project=project)
        server.start(TOOLSETS)
        chat = ChatLaunch()
        report = lambda: _answer(server, "server-health.report")  # noqa: E731
        return SimpleNamespace(
            project=project,
            ports=None,
            apps=[],
            chat=chat,
            open_app=lambda label: chat.opened(_answer(server, "app.open", app=label), report),
            report=report,
        )

    def close(self, world: SimpleNamespace) -> None:
        _close(world)


def _answer(server: McpServer, tool: str, **arguments: Any) -> Any:
    return json.loads(json.dumps(server.invoke_tool(tool, arguments), default=data_of))


def _close(world: SimpleNamespace) -> None:
    world.chat.end()
    # Each app puts back the one it replaced, so the last registered closes first and the real apps come back last.
    for app in reversed(world.apps):
        app.close()
    shutil.rmtree(world.project, ignore_errors=True)
