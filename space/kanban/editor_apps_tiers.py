"""The two Python tiers the scenarios of Integrate Practice Content Editor Apps In Chat Bar replay on.

The domain tier hands a scenario's steps *App* and *ServerHealth* themselves. The server tier hands them the same
operations through the cdd server, as the chat bar's status row reaches them: `app.open` and `server-health.report` by
their published names, JSON in and out. Each scenario registers a throwaway app in place of the real one of its label
(`ThrowawayApp`), so no scenario touches the person's own apps.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from harness.diagnostics.app import App
from harness.diagnostics.server_health import ServerHealth
from harness.installation.data_class import data_of
from harness.mcp.mcp_server import McpServer

TOOLSETS = ("harness.diagnostics.app:App", "harness.diagnostics.server_health:ServerHealth")


class DomainTier:
    """*App* and *ServerHealth* on a throwaway project, with nothing between a step and the domain."""

    name = "domain"

    def open(self) -> SimpleNamespace:
        project = Path(tempfile.mkdtemp(prefix="editor-apps-"))
        return SimpleNamespace(
            project=project,
            apps=[],
            open_app=lambda label: data_of(App.load(label, project=project).open()),
            report=lambda: data_of(ServerHealth.load(project=project).report()),
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
        return SimpleNamespace(
            project=project,
            apps=[],
            open_app=lambda label: _answer(server, "app.open", app=label),
            report=lambda: _answer(server, "server-health.report"),
        )

    def close(self, world: SimpleNamespace) -> None:
        _close(world)


def _answer(server: McpServer, tool: str, **arguments: Any) -> Any:
    return json.loads(json.dumps(server.invoke_tool(tool, arguments), default=data_of))


def _close(world: SimpleNamespace) -> None:
    for app in world.apps:
        app.close()
    shutil.rmtree(world.project, ignore_errors=True)
