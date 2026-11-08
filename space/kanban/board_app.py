"""The ports the session board answers on, read from the one file its server also reads."""
from __future__ import annotations

from pathlib import Path

from harness.installation.app_ports import AppPorts

# The session board's ports, as ``app/packages/session-board/ports.json`` gives them: ``board``, the ports its server
# listens on, the first unless ``BOARD_PORT`` names another. The board's server reads this file and the board registers
# these ports with server health, so the port is written once; read once here, when this module is imported.
BOARD_APP_PORTS = AppPorts(Path(__file__).resolve().parent / "app" / "packages" / "session-board" / "ports.json")
