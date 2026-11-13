"""The two Python tiers the scenarios of Integrate Practice Content Editor Apps In Chat Bar replay on.

The domain tier hands a scenario's steps *App* and *ServerHealth* themselves. The server tier hands them the same
operations through the cdd server, as the chat bar's status row reaches them: `app.open` and `server-health.report` by
their published names, JSON in and out. Each scenario registers a throwaway app in place of the real one of its label
(`ThrowawayApp`), so no scenario touches the person's own apps.

A press then does what the chat bar does with the answer (`app-client.ts`): while the app is not running, it starts
the app's server with its command in its folder and waits for its port, and the chat's end stops it. `ChatLaunch` plays
that part, so the scenarios prove the command each app answers starts its server.
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

from harness.diagnostics.app import App
from harness.diagnostics.server_health import ServerHealth
from harness.installation.data_class import data_of
from harness.mcp.mcp_server import McpServer

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


class DomainTier:
    """*App* and *ServerHealth* on a throwaway project, with nothing between a step and the domain."""

    name = "domain"

    def open(self) -> SimpleNamespace:
        project = Path(tempfile.mkdtemp(prefix="editor-apps-"))
        chat = ChatLaunch()
        report = lambda: data_of(ServerHealth.load(project=project).report())  # noqa: E731
        return SimpleNamespace(
            project=project,
            apps=[],
            chat=chat,
            open_app=lambda label: chat.opened(data_of(App.load(label, project=project).open()), report),
            report=report,
        )

    def close(self, world: SimpleNamespace) -> None:
        _close(world)


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
    for app in world.apps:
        app.close()
    shutil.rmtree(world.project, ignore_errors=True)
