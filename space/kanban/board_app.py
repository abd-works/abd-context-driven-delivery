"""The session board's app: the ports it answers on, read from the one file its server also reads, and the page its
server serves, rebuilt from the code."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from harness.installation.app_ports import AppPorts

APP_FOLDER = Path(__file__).resolve().parent / "app"

# The session board's ports, as ``app/packages/session-board/ports.json`` gives them: ``board``, the ports its server
# listens on, the first unless ``BOARD_PORT`` names another. The board's server reads this file and the board registers
# these ports with server health, so the port is written once; read once here, when this module is imported.
BOARD_APP_PORTS = AppPorts(APP_FOLDER / "packages" / "session-board" / "ports.json")


class BoardPage:
    """The page the board's server serves from its app folder's ``dist``. A pull or a merge changes the code but not the
    built page, so an install rebuilds it; the open board sees the new build and reloads itself."""

    def __init__(self, app_folder: Path = APP_FOLDER) -> None:
        self._app_folder = app_folder

    @property
    def _vite(self) -> Path:
        return self._app_folder / "node_modules" / "vite" / "bin" / "vite.js"

    def rebuild(self) -> str:
        """Build the page from the app's code and say how it went. The board is a convenience on top of the install, so
        a miss is told, never raised."""
        node = shutil.which("node")
        if not self._vite.is_file() or node is None:
            return f"not rebuilt: run npm install in {self._app_folder}"
        built = subprocess.run(
            [node, str(self._vite), "build"], cwd=self._app_folder, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if built.returncode != 0:
            return f"not rebuilt: {(built.stderr or built.stdout).strip()}"
        return "rebuilt"
