"""*BoardAppPorts*, the ports the session board answers on, read from the one file its server also reads."""
from __future__ import annotations

import json
from pathlib import Path


class BoardAppPorts:
    """The ports of the session board, as ``app/packages/session-board/ports.json`` gives them: ``board``, the ports its
    server listens on, the first unless ``BOARD_PORT`` names another. The board's server reads this file and the board
    registers these ports with server health, so the port is written once."""

    FILE = Path(__file__).resolve().parent / "app" / "packages" / "session-board" / "ports.json"

    def __init__(self, file: Path = FILE) -> None:
        self.board: tuple[int, ...] = tuple(int(port) for port in json.loads(file.read_text(encoding="utf-8"))["board"])