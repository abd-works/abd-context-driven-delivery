"""The one cdd server process: started on demand, found through ``~/.cdd/server.json``, answering every chat over HTTP."""
from __future__ import annotations

import os
import shutil
import socket
import threading
import time
from pathlib import Path

from harness.git.checkout import Checkout
from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_address import McpAddress
from harness.process.capped_log_file import CappedLogFile
from harness.process.process import ExclusivePort, RunningProcess
from harness.process.server_daemon import RunningServer, ServerDaemon

# The process a throwaway server belongs to, such as the spec run that started it on a port of its own. The server ends
# when that process does, so a run that is killed or hangs leaves no server behind; the person's own server names none.
SERVER_OWNER_ENV = "CDD_SERVER_OWNER"
# How often a throwaway server checks that the process it belongs to still runs.
OWNER_CHECK_SECONDS = 2
_PING_SECONDS = 2
# The command an IDE runs before it connects; an install copies it into ``~/.cdd``.
CONNECT_SCRIPT = Path(__file__).resolve().parent / "scripts" / "connect.py"


class McpDaemon(ServerDaemon):
    """The one cdd server, a *ServerDaemon*. Every IDE connects to its URL, so no chat starts a copy of its own.

    Holding the port exclusively is the claim: two servers cannot both hold it, so a second start exits quietly."""

    def __init__(self, home: CddHome, address: McpAddress | None = None, port: ExclusivePort | None = None) -> None:
        self.home = home
        self.address = address or McpAddress()
        # The server's port, asked which process holds it when the server there does not answer.
        super().__init__(port or ExclusivePort(self.address.HOST, self.address.port), CappedLogFile(home.log_path))
        # This process, when it is the server: the port it claims and the address it publishes.
        self.this_process = ServingProcess(home, self.address)

    def __str__(self) -> str:
        return f"the cdd server at {self.url}"

    @property
    def url(self) -> str:
        return self.address.url

    def running(self) -> RunningServer | None:
        """Ask the running server about itself over HTTP: its process, the checkout it serves code from, and its chats'
        projects; none when nothing answers on the port."""
        answer = self.address.ping_answer(_PING_SECONDS)
        if answer is None:
            return None
        source = str(answer.get("source") or "")
        projects = tuple(str(project) for project in answer.get("projects") or [])
        return RunningServer(RunningProcess(int(answer.get("pid") or 0)), Path(source) if source else None, projects=projects)

    def status(self, running: RunningServer) -> str:
        """How the server runs, as an install reports it: its process, and the code it serves, pinned or on disk."""
        return f"running (pid {running.pid}, {self.home.mode} {running.serves or ''})"

    def _command(self) -> list[str]:
        return [self.home.interpreter.windowless, "-m", "harness.mcp", "--port", str(self.port)]

    def _folder(self) -> Path:
        return self.home.source

    def _environment(self) -> dict[str, str]:
        return {**os.environ, **self.home.server_environment}


class ServedCheckout:
    """The checkout the one cdd server is installed from and serves, and the ways an install switches the server onto
    its code: ``~/.cdd/`` is installed from it on first use, and the server serves either its current commit, pinned
    in ``~/.cdd/runtime``, or the checkout as it is on disk."""

    def __init__(self, daemon: McpDaemon, checkout: Path) -> None:
        self.daemon = daemon
        self._home = daemon.home
        self.checkout = checkout

    @property
    def home(self) -> CddHome:
        """The home this checkout is installed into: the stable lane's for a main checkout, the dev lane's otherwise."""
        return self._home

    def ensure(self) -> str:
        """Install ``~/.cdd/`` from the checkout on first use and start the server when none answers. A server already
        running is left, with the code it serves, alone."""
        self._installed_home()
        return self.daemon.status(self.daemon.ensure())

    def pin(self) -> str:
        """Serve the checkout's current commit from ``~/.cdd/runtime``, restarting the server onto it."""
        self._installed_home().pin(self.checkout)
        return self._restarted_status()

    def update(self) -> str:
        """Serve the checkout's current code the way the server already serves it, pinned or as it is on disk,
        restarting the server onto it."""
        self._installed_home().serve_current(self.checkout)
        return self._restarted_status()

    def serve_on_disk(self) -> str:
        """Serve the checkout as it is on disk, for working on CDD itself, restarting the server onto it."""
        self._installed_home().serve_from(self.checkout)
        return self._restarted_status()

    def _installed_home(self) -> CddHome:
        """The home, once ``~/.cdd/`` is installed from the checkout, which every way of serving it starts with."""
        self._home.install(self.checkout, CONNECT_SCRIPT)
        return self._home

    def _restarted_status(self) -> str:
        """The server's status after it restarts onto the code the home now names."""
        return self.daemon.status(self.daemon.restart())

    def take_language_adapters(self, written: Path, ide_folder: str) -> Path:
        """Copy the language adapters an install wrote, the folder written, into the pinned runtime under its IDE folder
        ide_folder, in place of any an earlier pin left. The apps the home's server launches run from the runtime and
        import the CDD domain through those adapters, which git never copies there. A server started from the runtime
        keeps its folders open on Windows, so they outlive the removal empty and the copy writes into them. Answers
        where they went."""
        target = self._home.pinned_checkout / ide_folder / "language-adapters"
        shutil.rmtree(target, ignore_errors=True)
        shutil.copytree(written, target, dirs_exist_ok=True)
        return target

    def keep_pinned_current(self) -> str | None:
        """After a plain install, serve the checkout's current commit when the server is pinned to an older one, so
        every chat runs the code just installed. Left alone: a server serving a checkout on disk, an install run from
        a linked worktree (its commit is not what every chat should run), and an install run inside the server itself.
        Returns the server's status when it was restarted, else None."""
        if self.daemon.this_process.is_this_process() or Checkout(self.checkout).is_linked_worktree:
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
