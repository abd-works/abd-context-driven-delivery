"""*GraphAppPorts*, the ports the graph explorer app answers on, read from the one file its servers also read."""
from __future__ import annotations

import json
from pathlib import Path


class GraphAppPorts:
    """The ports of the graph explorer app, as ``app/ports.json`` gives them: ``app``, the ports its Vite server tries in
    turn, and ``web``, the port of its web server. The Vite config, the web server, the server health report, and the
    instance scripts all read this one file, so the ports are written once."""

    FILE = Path(__file__).resolve().parent / "app" / "ports.json"

    def __init__(self, file: Path = FILE) -> None:
        fields = json.loads(file.read_text(encoding="utf-8"))
        self.app: tuple[int, ...] = tuple(int(port) for port in fields["app"])
        self.web: tuple[int, ...] = tuple(int(port) for port in fields["web"])
