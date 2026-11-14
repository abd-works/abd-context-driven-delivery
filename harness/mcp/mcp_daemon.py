"""The one cdd server process: started on demand, found through ``~/.cdd/server.json``, answering every chat over HTTP."""
from __future__ import annotations

import http.client
import json
import os
import socket
import sys
import threading
import time
from pathlib import Path

from harness.mcp.cdd_home import CddHome
from harness.process.process import BackgroundStart, ExclusivePort, RunningProcess, StoppableProcess

SERVER_PORT_ENV = "CDD_SERVER_PORT"
# The process a throwaway server belongs to, such as the spec run that started it on a port of its own. The server ends
# when that process does, so a run that is killed or hangs leaves no server behind; the person's own server names none.
SERVER_OWNER_ENV = "CDD_SERVER_OWNER"
# How often a throwaway server checks that the process it belongs to still runs.
OWNER_CHECK_SECONDS = 2
DEFAULT_SERVER_PORT = 47800
PROJECT_HEADER = "X-CDD-Project"
# The Claude Code chat a request comes from, so the server can follow that chat into whatever folder it works in now.
CHAT_HEADER = "X-CDD-Chat"
# The Claude Code process a request comes from. Its session file names the folder the session works in now, which stays
# right after the desktop app moves a chat out of the spare folder it started in.
CHAT_PROCESS_HEADER = "X-CDD-Chat-Process"
PING_PATH = "/ping"
MCP_PATH = "/mcp"
_PING_SECONDS = 2
_START_SECONDS = 60
_STOP_SECONDS = 10
_LOG_LINES_SHOWN = 20
# The command an IDE runs before it connects; an install copies it into ``~/.cdd``.
CONNECT_SCRIPT = Path(__file__).resolve().parent / "scripts" / "connect.py"
# How often a start looks again for the server's answer while it waits for the server to come up.
_PING_RETRY_SECONDS = 0.25


class ServerDidNotStart(Exception):
    """The cdd server was started but never answered a ping."""

    def __init__(self, url: str, log: str) -> None:
        super().__init__(f"the cdd server at {url} did not answer within {_START_SECONDS} seconds. Last log lines:\n{log}")
        self.url = url


class RunningServer:
    """The cdd server answering on the port, as its ping describes it: its process, the checkout it serves code from,
    and the projects its chats have worked on."""

    def __init__(self, answer: dict) -> None:
        self.pid = int(answer.get("pid") or 0)
        self.source = str(answer.get("source") or "")
        self.projects = [str(project) for project in answer.get("projects") or []]
        self.process = StoppableProcess(self.pid)


class McpDaemon:
    """Start, find, and stop the one cdd server. Every IDE connects to its URL, so no chat starts a copy of its own.

    Holding the port exclusively is the claim: two servers cannot both hold it, so a second start exits quietly."""

    HOST = "127.0.0.1"

    def __init__(self, home: CddHome, port: int | None = None) -> None:
        self.home = home
        self.port = port or int(os.environ.get(SERVER_PORT_ENV) or DEFAULT_SERVER_PORT)

    @property
    def url(self) -> str:
        return f"http://{self.HOST}:{self.port}{MCP_PATH}"

    def ping(self) -> RunningServer | None:
        """Ask the running server about itself over HTTP: the server it describes, or ``None`` when nothing answers on
        the port."""
        connection = http.client.HTTPConnection(self.HOST, self.port)
        try:
            connection.sock = ExclusivePort(self.HOST, self.port).connect(_PING_SECONDS)
            connection.request("GET", PING_PATH)
            reply = connection.getresponse()
            answer = json.loads(reply.read().decode("utf-8")) if reply.status == 200 else None
        except (OSError, http.client.HTTPException, json.JSONDecodeError):
            return None
        finally:
            connection.close()
        return RunningServer(answer) if isinstance(answer, dict) and answer.get("ok") else None

    def is_running(self) -> bool:
        return self.ping() is not None

    def ensure(self) -> RunningServer:
        """The running server, starting it first when none answers."""
        answer = self.ping()
        if answer is not None:
            return answer
        self.spawn()
        return self._wait_for_ping()

    def restart(self) -> RunningServer:
        """Stop the running server and start it again on the code ``~/.cdd/runtime.json`` names now."""
        self.stop()
        return self.ensure()

    def stop(self) -> None:
        running = self.ping()
        if running is not None:
            running.process.stop(_STOP_SECONDS)

    def ensure_from(self, checkout: Path) -> str:
        """Install ``~/.cdd/`` from checkout on first use and start the server when none answers. A server already
        running is left, with the code it serves, alone."""
        self.home.install(checkout, CONNECT_SCRIPT)
        return self._status(self.ensure())

    def pin_from(self, checkout: Path) -> str:
        """Serve checkout's current commit from ``~/.cdd/runtime``, restarting the server onto it."""
        self.home.install(checkout, CONNECT_SCRIPT)
        self.home.pin(checkout)
        return self._status(self.restart())

    def serve_checkout(self, checkout: Path) -> str:
        """Serve checkout as it is on disk, for working on CDD itself, restarting the server onto it."""
        self.home.install(checkout, CONNECT_SCRIPT)
        self.home.serve_from(checkout)
        return self._status(self.restart())

    def _status(self, running: RunningServer) -> str:
        return f"running (pid {running.pid}, {self.home.mode} {running.source})"

    def spawn(self) -> None:
        self.home.folder.mkdir(parents=True, exist_ok=True)
        with open(self.home.log_path, "a", encoding="utf-8") as log:
            try:
                self._start_process(log, BackgroundStart())
            except PermissionError:
                # Some Windows jobs refuse to let a child break away; the server then lives in its starter's job, and
                # the next connect starts it again if that job ends.
                log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} breakaway refused; starting inside the caller's job\n")
                log.flush()
                self._start_process(log, BackgroundStart().inside_starters_job())

    def _start_process(self, log, start: BackgroundStart) -> None:
        command = [self.home.interpreter.windowless, "-m", "harness.mcp", "--port", str(self.port)]
        start.run(command, cwd=self.home.source, env={**os.environ, **self.home.server_environment}, log=log)

    def claim_port(self) -> socket.socket | None:
        """A listening socket on the server port, or ``None`` when another server already holds it."""
        return ExclusivePort(self.HOST, self.port).claim()

    def publish(self, source: Path) -> None:
        """Write the address and pid for tools that look for the server without calling it."""
        self.home.state_file.write({"url": self.url, "port": self.port, "pid": os.getpid(), "source": str(source)})

    def end_with_owner(self) -> None:
        """When ``CDD_SERVER_OWNER`` names the process this server belongs to, end this server once that process has
        ended, withdrawing its address first; a server that names no owner runs until it is stopped."""
        owner = RunningProcess(int(os.environ.get(SERVER_OWNER_ENV) or 0))
        if owner.pid <= 0:
            return
        threading.Thread(target=self._end_after, args=(owner,), name="cdd-server-owner", daemon=True).start()

    def _end_after(self, owner: RunningProcess) -> None:
        while owner.alive:
            time.sleep(OWNER_CHECK_SECONDS)
        self.withdraw()
        os._exit(0)

    def withdraw(self) -> None:
        if self.runs_this_process():
            self.home.state_path.unlink(missing_ok=True)

    def runs_this_process(self) -> bool:
        """True when the server this home publishes is this process, as it is for code a tool call runs inside it."""
        return self.home.state_file.read().get("pid") == os.getpid()

    def _wait_for_ping(self) -> RunningServer:
        deadline = time.time() + _START_SECONDS
        while time.time() < deadline:
            answer = self.ping()
            if answer is not None:
                return answer
            time.sleep(_PING_RETRY_SECONDS)
        raise ServerDidNotStart(self.url, self._log_tail())

    def _log_tail(self) -> str:
        if not self.home.log_path.is_file():
            return "(no log)"
        lines = self.home.log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-_LOG_LINES_SHOWN:])
