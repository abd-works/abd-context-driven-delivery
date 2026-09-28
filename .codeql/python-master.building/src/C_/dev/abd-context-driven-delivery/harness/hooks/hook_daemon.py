"""Persistent HookServer process — stdin CLI connects through HookServer.ensure."""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
for _entry in (_REPO, _REPO / "tools", _REPO / "practices", _REPO / "actions"):
    _path = str(_entry)
    if _path not in sys.path:
        sys.path.insert(0, _path)


class HookDaemon:
    """Local socket process that holds one HookServer for Cursor stdin CLI."""

    HOST = "127.0.0.1"

    def __init__(self, host: str | None = None, port: int | None = None) -> None:
        self.host = host or self.HOST
        self.port = port

    def live_address(self, path: Path) -> tuple[str, int, int | None] | None:
        if not path.is_file():
            return None
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        host = state.get("host") or self.HOST
        port = state.get("port")
        if not port:
            return None
        probe = HookDaemon(host, int(port))
        try:
            result = probe._rpc({"method": "ping"})
        except OSError:
            return None
        if not result.get("ok"):
            return None
        return host, int(port), state.get("pid")

    def call_handle_stdin(self, raw: bytes) -> dict:
        return self._rpc(
            {"method": "handle_stdin", "raw": raw.decode("utf-8-sig")}
        )

    def spawn(self, repo: Path, path: Path) -> None:
        root = str(Path(repo).resolve())
        env = os.environ.copy()
        extra = [
            root,
            str(Path(root) / "tools"),
            str(Path(root) / "practices"),
            str(Path(root) / "actions"),
        ]
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = os.pathsep.join(
            [*extra, *(existing.split(os.pathsep) if existing else ())]
        )
        flags = 0
        if sys.platform == "win32":
            flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(
                subprocess, "CREATE_NEW_PROCESS_GROUP", 0
            )
        log = path.parent / "hook-server.log"
        stream = open(log, "a", encoding="utf-8")
        subprocess.Popen(
            [sys.executable, "-m", "harness.hooks.hook_daemon", root],
            cwd=root,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stream,
            stderr=subprocess.STDOUT,
            creationflags=flags,
            close_fds=True,
        )

    def serve(self, repo: Path, inner=None) -> None:
        from harness.hooks.hook_server import HookServer

        server = inner if inner is not None else HookServer.from_toolsets(repo)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.HOST, 0))
        sock.listen(8)
        port = sock.getsockname()[1]
        path = HookServer.state_path(repo)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"host": self.HOST, "port": port, "pid": os.getpid()}),
            encoding="utf-8",
        )
        while True:
            conn, _ = sock.accept()
            try:
                self._handle(conn, server)
            finally:
                conn.close()

    def _handle(self, conn: socket.socket, server) -> None:
        raw = self._read_json(conn)
        method = raw.get("method")
        if method == "ping":
            self._write_json(conn, {"ok": True})
            return
        if method != "handle_stdin":
            self._write_json(conn, {"error": f"unknown method {method}"})
            return
        result = server.handle_stdin((raw.get("raw") or "").encode("utf-8"))
        self._write_json(conn, result.as_dict())

    def _rpc(self, payload: dict) -> dict:
        with socket.create_connection((self.host, self.port), timeout=600) as conn:
            self._write_json(conn, payload)
            return self._read_json(conn)

    def _write_json(self, conn: socket.socket, payload: dict) -> None:
        raw = json.dumps(payload).encode("utf-8")
        conn.sendall(f"{len(raw)}\n".encode("ascii") + raw)

    def _read_json(self, conn: socket.socket) -> dict:
        header = b""
        while not header.endswith(b"\n"):
            chunk = conn.recv(1)
            if not chunk:
                raise OSError("hook daemon closed")
            header += chunk
        length = int(header.decode("ascii"))
        body = b""
        while len(body) < length:
            chunk = conn.recv(length - len(body))
            if not chunk:
                raise OSError("hook daemon closed")
            body += chunk
        return json.loads(body)


if __name__ == "__main__":
    HookDaemon().serve(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
