"""The apps the session board's server serves, made once and registered here: the CDD Kanban, from the ports file its
server also reads, and the Story UI editor, which the board's server serves at /story-map from the Stories practice's
app folder."""
from __future__ import annotations

from pathlib import Path

from cdd_guidance.practices.stories.stories import Stories
from harness.diagnostics.app import App, AppServer
from harness.installation.app_ports import AppPorts

APP_FOLDER = Path(__file__).resolve().parent / "app"
# The Story UI editor's code sits with the practice it edits; space may name that folder, the practice imports no space.
STORY_UI_FOLDER = Path(__file__).resolve().parents[2] / "cdd_guidance" / "practices" / "stories" / "app"

# The session board's ports, as ``app/packages/session-board/ports.json`` gives them: ``board``, the ports its server
# listens on, the first unless ``BOARD_PORT`` names another. The board's server reads this file too, so the port is
# written once; read once here, when this module is imported.
BOARD_APP_PORTS = AppPorts(APP_FOLDER / "packages" / "session-board" / "ports.json")

# The board's server, which serves the CDD Kanban and the Story UI editor alike, so a chat starts it once for both.
BOARD_SERVER = AppServer(APP_FOLDER, "packages/session-board/serve.ts", BOARD_APP_PORTS.of("board"))
KANBAN_APP = App("Kanban", APP_FOLDER, BOARD_SERVER).register()
STORY_UI_APP = App("Story UI", STORY_UI_FOLDER, BOARD_SERVER, page="/story-map").register()
# The Story UI editor edits the Stories practice's files, so every Stories file the chat bar and the board show opens in it.
Stories.edit_with(STORY_UI_APP)
