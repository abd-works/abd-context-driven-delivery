"""The one cdd server process: started on demand, found through ``~/.cdd/server.json``, answering every chat over HTTP."""
from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from harness.mcp.cdd_home import CddHome

SERVER_PORT_ENV = "CDD_SERVER_PORT"
DEFAULT_SERVER_PORT = 47800
PROJECT_HEADER = "X-CDD-Project"
PING_PATH = "/ping"
MCP_PATH = "/mcp"
_PING_SECONDS = 2
_START_SECONDS = 60
_STOP_SECONDS = 10
_LOG_LINES_SHOWN = 20


class ServerDidNotStart(Exception):
    """The cdd server was started but never answered a ping."""

    def __init__(self, url: str, log: str) -> None:
        super().__init__(f"the cdd server at {url} did not answer within {_START_SECONDS} seconds. Last log lines:\n{log}")
        self.url = url


class McpDaemon:
    """Start, find, and stop the one cdd server. Every IDE connects to its URL, so no chat starts a copy of its own.

    The exclusive bind on the port is the claim: two servers cannot both hold it, so a second start exits quietly."""

    HOST = "127.0.0.1"

    def __init__(self, home: CddHome | None = None, port: int | None = None) -> None:
        self.home = home or CddHome()
        self.port = port or int(os.environ.get(SERVER_PORT_ENV) or DEFAULT_SERVER_PORT)

    @property
    def url(self) -> str:
        return f"http://{self.HOST}:{self.port}{MCP_PATH}"

    @property
    def ping(self) -> dict | None:
        """What the running server says about itself, or ``None`` when nothing answers on the port."""
        try:
            with urllib.request.urlopen(f"http://{self.HOST}:{self.port}{PING_PATH}", timeout=_PING_SECONDS) as reply:
                answer = json.loads(reply.read().decode("utf-8"))
        except (OSError, urllib.error.URLError, json.JSONDecodeError):
            return None
        return answer if isinstance(answer, dict) and answer.get("ok") else None

    @property
    def is_running(self) -> bool:
        return self.ping is not None

    def ensure(self) -> dict:
        """The running server's ping, starting it first when none answers."""
        answer = self.ping
        if answer is not None:
            return answer
        self.spawn()
        return self._wait_for_ping()

    def restart(self) -> dict:
        """Stop the running server and start it again on the code ``~/.cdd/runtime.json`` names now."""
        self.stop()
        return self.ensure()

    def stop(self) -> None:
        answer = self.ping
        if answer is None:
            return
        self._end_process(int(answer.get("pid") or 0))

    def spawn(self) -> None:
        from harness.hooks.process import detached_creationflags, hidden_process_startupinfo, hook_python_executable

        self.home.folder.mkdir(parents=True, exist_ok=True)
        log = open(self.home.log_path, "a", encoding="utf-8")
        subprocess.Popen(
            [hook_python_executable(self.home.python), "-m", "harness.mcp", "--port", str(self.port)],
            cwd=str(self.home.source),
            env={**os.environ, **self.home.server_environment},
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=detached_creationflags(),
            startupinfo=hidden_process_startupinfo(),
            close_fds=True,
        )

    def claim_port(self) -> socket.socket | None:
        """A listening socket on the server port, or ``None`` when another server already holds it."""
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sys.platform == "win32":
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        try:
            listener.bind((self.HOST, self.port))
        except OSError:
            listener.close()
            return None
        listener.listen(socket.SOMAXCONN)
        return listener

    def publish(self, source: Path) -> None:
        """Write the address and pid for tools that look for the server without calling it."""
        state = {"url": self.url, "port": self.port, "pid": os.getpid(), "source": str(source)}
        self.home.folder.mkdir(parents=True, exist_ok=True)
        self.home.state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    def withdraw(self) -> None:
        try:
            state = json.loads(self.home.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if state.get("pid") == os.getpid():
            self.home.state_path.unlink(missing_ok=True)

    def _wait_for_ping(self) -> dict:
        deadline = time.time() + _START_SECONDS
        while time.time() < deadline:
            answer = self.ping
            if answer is not None:
                return answer
            time.sleep(0.25)
        raise ServerDidNotStart(self.url, self._log_tail())

    def _end_process(self, pid: int) -> None:
        if pid <= 0 or pid == os.getpid():
            return
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            return
        deadline = time.time() + _STOP_SECONDS
        while time.time() < deadline and self.is_running:
            time.sleep(0.1)

    def _log_tail(self) -> str:
        if not self.home.log_path.is_file():
            return "(no log)"
        lines = self.home.log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-_LOG_LINES_SHOWN:])
