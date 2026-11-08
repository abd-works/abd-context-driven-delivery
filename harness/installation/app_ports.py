"""*AppPorts*, the ports an app's servers answer on, read from the one ports file those servers also read."""
from __future__ import annotations

from pathlib import Path

from harness.installation.json_file import JsonFile


class AppPorts:
    """The ports an app's servers answer on, as the one ``ports.json`` beside them gives them: each server's ports, in
    the order it tries them. The app's own servers read that file too, so a port is written once. Read when made; the
    module that names the app makes it once and keeps it."""

    def __init__(self, file: Path) -> None:
        self.file = JsonFile(file)
        self._ports = {server: tuple(int(port) for port in ports) for server, ports in self.file.read().items()}

    def of(self, server: str) -> tuple[int, ...]:
        """The ports of the app's server called server in its ports file, such as ``web``, in the order it tries them."""
        return self._ports[server]
