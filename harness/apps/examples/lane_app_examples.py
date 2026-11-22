"""The examples the Serve Dev Lane Apps On Their Own Ports story shares: the Files app's server as one lane or the other
makes it, with nothing listening on this computer's ports.

Scenarios: story_tests/register-and-install-toolsets/serve-cdd-code-in-lanes/serve-dev-lane-apps-on-their-own-ports/
"""
from __future__ import annotations

from pathlib import Path

from harness.apps.app import AppServer, NodeScript, PortProbe
from harness.mcp.server_lanes import ServerLane

# Seed: the Files app's folder and script, and the port its ports file gives it, as harness/files_app/app holds them.
FILES_FOLDER = Path("harness") / "files_app" / "app"
FILES_SCRIPT = "serve.ts"
FILES_PORTS = (8783,)


class NothingAnswers(PortProbe):
    """A stub of this computer's ports: nothing answers on any of them, so no app server is running."""

    def answers(self, port: int) -> bool:
        return False


def seed_files_server(lane: ServerLane) -> AppServer:
    """The Files app's server as the cdd server of lane makes it."""
    return AppServer(NodeScript(FILES_FOLDER, FILES_SCRIPT), FILES_PORTS, NothingAnswers(), lane)
