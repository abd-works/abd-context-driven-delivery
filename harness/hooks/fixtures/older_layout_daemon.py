"""A hook daemon as the older layout ran it, for specs: it holds a checkout's hook port exclusively, answers a ping with
``ok`` alone, naming neither its process nor its checkout, and published its address in ``.cursor/hook-server.json``.
Run as a script, this file is that daemon: ``python older_layout_daemon.py <port>``."""
from __future__ import annotations

import json
import socket
import subprocess
import sys
from pathlib import Path


class OlderLayoutDaemon:
    """One such daemon, started on a port in its own process."""

    def __init__(self, repo: Path, port: int) -> None:
        self.repo = repo
        self.port = port
        self.process: subprocess.Popen | None = None

    @property
    def published_file(self) -> Path:
        return self.repo / ".cursor" / "hook-server.json"

    def start(self, publishes: bool = True) -> OlderLayoutDaemon:
        """Start it and wait until it listens; with publishes, it writes its address file as the older layout did."""
        self.process = subprocess.Popen([sys.executable, __file__, str(self.port)], stdout=subprocess.PIPE)
        self.process.stdout.readline()
        if publishes:
            self.published_file.parent.mkdir(parents=True, exist_ok=True)
            fields = {"host": "127.0.0.1", "port": self.port, "pid": self.process.pid, "stamp": "older"}
            self.published_file.write_text(json.dumps(fields), encoding="utf-8")
        return self

    def ended(self) -> bool:
        """Whether its process has ended, waiting a few seconds for it."""
        try:
            self.process.wait(5)
        except subprocess.TimeoutExpired:
            return False
        return True

    def kill(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.kill()


def _serve(port: int) -> None:
    listener = socket.socket()
    if sys.platform == "win32":
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    listener.bind(("127.0.0.1", port))
    listener.listen()
    print("ready", flush=True)
    while True:
        conn, _ = listener.accept()
        header = b""
        while not header.endswith(b"\n"):
            header += conn.recv(1)
        length = int(header)
        body = b""
        while len(body) < length:
            body += conn.recv(length - len(body))
        raw = json.dumps({"ok": True}).encode("utf-8")
        conn.sendall(str(len(raw)).encode("ascii") + b"\n" + raw)
        conn.close()


if __name__ == "__main__":
    _serve(int(sys.argv[1]))
