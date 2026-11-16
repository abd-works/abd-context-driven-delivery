"""The one cdd server process: started on demand, found through ``~/.cdd/server.json``, answering every chat over HTTP."""
from __future__ import annotations

import os
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Any

from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_address import McpAddress
from harness.process.process import BackgroundStart, ExclusivePort, ListeningPorts, RunningProcess, StoppableProcess

# The process a throwaway server belongs to, such as the spec run that started it on a port of its own. The server ends
# when that process does, so a run that is killed or hangs leaves no server behind; the person's own server names none.
SERVER_OWNER_ENV = "CDD_SERVER_OWNER"
# How often a throwaway server checks that the process it belongs to still runs.
OWNER_CHECK_SECONDS = 2
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


PingAnswer = dict[str, Any]
"""What the cdd server's ``/ping`` answers, as JSON: its pid, the checkout it serves, and its chats' projects."""


class RunningServer:
    """The cdd server answering on the port, as its ping describes it: its process, the checkout it serves code from,
    and the projects its chats have worked on."""

    def __init__(self, answer: PingAnswer) -> None:
        self.pid = int(answer.get("pid") or 0)
        self.source = str(answer.get("source") or "")
        self.projects = [str(project) for project in answer.get("projects") or []]
        self.process = StoppableProcess(self.pid)


class McpDaemon:
    """Start, find, and stop the one cdd server. Every IDE connects to its URL, so no chat starts a copy of its own.

    Holding the port exclusively is the claim: two servers cannot both hold it, so a second start exits quietly."""

    def __init__(self, home: CddHome, address: McpAddress | None = None, listening: ListeningPorts | None = None) -> None:
        self.home = home
        self.address = address or McpAddress()
        self._listening = listening or ListeningPorts()
        # This process, when it is the server: the port it claims and the address it publishes.
        self.this_process = ServingProcess(home, self.address)

    @property
    def port(self) -> int:
        return self.address.port

    @property
    def url(self) -> str:
        return self.address.url

    def ping(self) -> RunningServer | None:
        """Ask the running server about itself over HTTP: the server it describes, or ``None`` when nothing answers on
        the port."""
        answer = self.address.ping_answer(_PING_SECONDS)
        return RunningServer(answer) if answer is not None else None

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
        """Stop the server on the port. One that holds the port but does not answer, such as a deadlocked one, is found
        by the port it listens on and stopped too: left running, it would keep every new server from claiming the
        port."""
        running = self.ping()
        process = running.process if running is not None else self._listening.holder(self.port)
        if process is not None:
            process.stop(_STOP_SECONDS)

    def status(self, running: RunningServer) -> str:
        """How the server runs, as an install reports it: its process, and the code it serves, pinned or on disk."""
        return f"running (pid {running.pid}, {self.home.mode} {running.source})"

    def spawn(self) -> None:
        self.home.folder.mkdir(parents=True, exist_ok=True)
        with open(self.home.log_path, "a", encoding="utf-8") as log:
            try:
                self._start_process(BackgroundStart(log))
            except PermissionError:
                # Some Windows jobs refuse to let a child break away; the server then lives in its starter's job, and
                # the next connect starts it again if that job ends.
                log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} breakaway refused; starting inside the caller's job\n")
                log.flush()
                self._start_process(BackgroundStart(log).inside_starters_job())

    def _start_process(self, start: BackgroundStart) -> None:
        command = [self.home.interpreter.windowless, "-m", "harness.mcp", "--port", str(self.port)]
        start.run(command, self.home.source, {**os.environ, **self.home.server_environment})

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


class ServedCheckout:
    """The checkout the one cdd server is installed from and serves, and the ways an install switches the server onto
    its code: ``~/.cdd/`` is installed from it on first use, and the server serves either its current commit, pinned
    in ``~/.cdd/runtime``, or the checkout as it is on disk."""

    def __init__(self, daemon: McpDaemon, checkout: Path) -> None:
        self.daemon = daemon
        self._home = daemon.home
        self.checkout = checkout

    def ensure(self) -> str:
        """Install ``~/.cdd/`` from the checkout on first use and start the server when none answers. A server already
        running is left, with the code it serves, alone."""
        self._home.install(self.checkout, CONNECT_SCRIPT)
        return self.daemon.status(self.daemon.ensure())

    def pin(self) -> str:
        """Serve the checkout's current commit from ``~/.cdd/runtime``, restarting the server onto it."""
        self._home.install(self.checkout, CONNECT_SCRIPT)
        self._home.pin(self.checkout)
        return self.daemon.status(self.daemon.restart())

    def update(self) -> str:
        """Serve the checkout's current code the way the server already serves it, pinned or as it is on disk,
        restarting the server onto it."""
        self._home.install(self.checkout, CONNECT_SCRIPT)
        self._home.serve_current(self.checkout)
        return self.daemon.status(self.daemon.restart())

    def serve_on_disk(self) -> str:
        """Serve the checkout as it is on disk, for working on CDD itself, restarting the server onto it."""
        self._home.install(self.checkout, CONNECT_SCRIPT)
        self._home.serve_from(self.checkout)
        return self.daemon.status(self.daemon.restart())

    def keep_pinned_current(self) -> str | None:
        """After a plain install, serve the checkout's current commit when the server is pinned to an older one, so
        every chat runs the code just installed. Left alone: a server serving a checkout on disk, an install run from
        a linked worktree (its commit is not what every chat should run), and an install run inside the server itself.
        Returns the server's status when it was restarted, else None."""
        if self.daemon.this_process.is_this_process() or (self.checkout / ".git").is_file():
            return None
        if self._home.is_installed and self._home.mode != self._home.PINNED:
            return None
        if self._home.is_installed and self._home.is_pinned_to(self.checkout) and self.daemon.is_running():
            return None
        return self.pin()


class ServingProcess:
    """The cdd server as the process that runs it: it claims the server port, publishes its address for tools that
    look for the server without calling it, withdraws that address when it ends, and ends with the process it belongs
    to when one is named."""

    def __init__(self, home: CddHome, address: McpAddress) -> None:
        self.home = home
        self.address = address

    def claim_port(self) -> socket.socket | None:
        """A listening socket on the server port, or ``None`` when another server already holds it."""
        return ExclusivePort(self.address.HOST, self.address.port).claim()

    def publish(self, source: Path) -> None:
        """Write the address and pid for tools that look for the server without calling it."""
        self.home.state_file.write({"url": self.address.url, "port": self.address.port, "pid": os.getpid(), "source": str(source)})

    def end_with_owner(self) -> None:
        """When ``CDD_SERVER_OWNER`` names the process this server belongs to, end this server once that process has
        ended, withdrawing its address first; a server that names no owner runs until it is stopped."""
        owner = RunningProcess(int(os.environ.get(SERVER_OWNER_ENV) or 0))
        if owner.pid <= 0:
            return
        threading.Thread(target=self._end_after, args=(owner,), name="cdd-server-owner", daemon=True).start()

    def withdraw(self) -> None:
        if self.is_this_process():
            self.home.state_path.unlink(missing_ok=True)

    def is_this_process(self) -> bool:
        """True when the server this home publishes is this process, as it is for code a tool call runs inside it."""
        return self.home.state_file.read().get("pid") == os.getpid()

    def _end_after(self, owner: RunningProcess) -> None:
        while owner.alive:
            time.sleep(OWNER_CHECK_SECONDS)
        self.withdraw()
        # The server's threads would keep the process alive past its owner; nothing is left to clean up after withdraw.
        os._exit(0)
