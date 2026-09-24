"""Persistent CodeQL query-server2 — one JVM, compile once, reuse across reports."""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
for _entry in (_REPO, _REPO / "tools", _REPO / "practices", _REPO / "actions"):
    _text = str(_entry)
    if _text not in sys.path:
        sys.path.insert(0, _text)

from harness.knowledge_graph.model.codeql import CodeQL, CodeQLRunError
from harness.mcp.codeql_server import CodeQLQueryServer

_HOST = "127.0.0.1"
_WAIT_SECONDS = 90


class QueryServerClient:
    alive = True

    def __init__(self, host: str = _HOST, port: int = 0, pid: int | None = None) -> None:
        self.host = host
        self.port = port
        self.pid = pid

    def state_path(self, repo: Path) -> Path:
        return CodeQL(repo).repo_root() / ".codeql" / "query-server.json"

    def ensure_query_server(self, repo: Path):
        """Return a client to a long-lived query daemon; spawn it if needed."""
        path = self.state_path(repo)
        client = self._connect(path)
        if client is not None:
            return client
        self._spawn(repo, path)
        deadline = time.time() + _WAIT_SECONDS
        while time.time() < deadline:
            client = self._connect(path)
            if client is not None:
                return client
            time.sleep(0.2)
        raise CodeQLRunError("codeql query daemon did not become ready")

    def _connect(self, path: Path) -> QueryServerClient | None:
        if not path.is_file():
            return None
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        host = state.get("host") or _HOST
        port = state.get("port")
        if not port:
            return None
        try:
            result = _rpc(host, int(port), {"method": "ping"})
        except OSError:
            return None
        if not result.get("ok"):
            return None
        return QueryServerClient(host, int(port), state.get("pid"))

    def _spawn(self, repo: Path, path: Path) -> None:
        root = str(CodeQL(repo).repo_root())
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
        log = path.parent / "query-server.log"
        stream = open(log, "a", encoding="utf-8")
        subprocess.Popen(
            [sys.executable, "-m", "harness.mcp.codeql_query_daemon", root],
            cwd=root,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stream,
            stderr=subprocess.STDOUT,
            creationflags=flags,
            close_fds=True,
        )

    def run_queries(self, queries, database: Path, on_line) -> dict[str, Path]:
        result = _rpc(
            self.host,
            self.port,
            {
                "method": "runQueries",
                "queries": [str(Path(query).resolve()) for query in queries],
                "database": str(Path(database).resolve()),
            },
        )
        for line in result.get("log") or []:
            if on_line is not None:
                on_line(line)
        if result.get("error"):
            raise CodeQLRunError(result["error"])
        return {
            key: Path(value)
            for key, value in (result.get("produced") or {}).items()
        }

    def start(self) -> None:
        return

    def stop(self) -> None:
        return


def serve(repo: Path, inner: CodeQLQueryServer | None = None) -> None:
    server = inner if inner is not None else CodeQLQueryServer.from_repo(repo)
    if inner is None:
        server.start()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((_HOST, 0))
    sock.listen(8)
    port = sock.getsockname()[1]
    path = QueryServerClient().state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"host": _HOST, "port": port, "pid": os.getpid()}),
        encoding="utf-8",
    )
    while True:
        conn, _ = sock.accept()
        try:
            _handle(conn, server)
        finally:
            conn.close()


def _handle(conn: socket.socket, server: CodeQLQueryServer) -> None:
    raw = _read_json(conn)
    method = raw.get("method")
    if method == "ping":
        _write_json(conn, {"ok": True})
        return
    if method != "runQueries":
        _write_json(conn, {"error": f"unknown method {method}"})
        return
    log: list[str] = []
    try:
        produced = server.run_queries(
            [Path(path) for path in raw.get("queries") or []],
            Path(raw["database"]),
            log.append,
        )
        _write_json(
            conn,
            {
                "produced": {key: str(value) for key, value in produced.items()},
                "log": log,
            },
        )
    except Exception as error:
        _write_json(conn, {"error": str(error), "log": log})


def _rpc(host: str, port: int, payload: dict) -> dict:
    with socket.create_connection((host, port), timeout=600) as conn:
        _write_json(conn, payload)
        return _read_json(conn)


def _write_json(conn: socket.socket, payload: dict) -> None:
    raw = json.dumps(payload).encode("utf-8")
    conn.sendall(f"{len(raw)}\n".encode("ascii") + raw)


def _read_json(conn: socket.socket) -> dict:
    header = b""
    while not header.endswith(b"\n"):
        chunk = conn.recv(1)
        if not chunk:
            raise OSError("query daemon closed")
        header += chunk
    length = int(header.decode("ascii"))
    body = b""
    while len(body) < length:
        chunk = conn.recv(length - len(body))
        if not chunk:
            raise OSError("query daemon closed")
        body += chunk
    return json.loads(body)


if __name__ == "__main__":
    serve(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
