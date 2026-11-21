"""The hook daemon of one checkout: the process that keeps the hook server loaded between hook commands, and the address
a hook command reaches it at.

An IDE runs this file as its hook command: ``python -u harness/hooks/hook_daemon.py`` with the event's fields on stdin.
The command hands the event to the checkout's hook daemon, started with ``serve <checkout>``, and prints its answer."""
from __future__ import annotations

import sys
from pathlib import Path

if __name__ == "__main__":
    # Run by path, this file's folder is on the import path and the checkout is not; put the checkout first so the
    # imports below resolve. The hook command sets the rest of the checkout's import path through RepositoryToolsets.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import hashlib
import json
import logging
import os
import socket
import threading
import time
from typing import Any

import harness.hooks.hook_server as hook_server_module
import harness.hooks.hooks as hooks_module
import harness.process.process as process_module
import harness.process.server_daemon as server_daemon_module
from harness.agent_tools.agent_tools import ToolsetReference
from harness.hooks.hook_server import HookResult, HookServer
from harness.hooks.hooks import InstalledHookHandlers
from harness.installation.json_file import JsonFile, JsonFileUnreadable
from harness.installation.repository_toolsets import RUNNING_CHECKOUT, RepositoryToolsets
from harness.process.capped_log_file import CappedLogFile
from harness.process.process import ExclusivePort, ProcessNotStopped, PythonInterpreter, RunningProcess
from harness.process.server_daemon import RunningServer, ServerDaemon

logger = logging.getLogger(__name__)

_PORT_RANGE_START = 20000
_PORT_RANGE_SIZE = 10000
# A stopped daemon's port can stay bound for a moment after its process ends; the replacement tries this many times.
_CLAIM_TRIES = 20
_CLAIM_POLL_SECONDS = 0.1
# One dispatch can run a hook that renders guidance; the caller waits for it rather than giving the IDE no answer.
_CALL_TIMEOUT_SECONDS = 600
# A ping answers at once from a live daemon, so a dead or busy address is found quickly.
_PING_TIMEOUT_SECONDS = 5
# One message a hook command and its daemon exchange: a JSON object naming the method and its fields, or the answer.
DaemonMessage = dict[str, Any]
# The hook server's own code: a daemon that loaded older copies of these is a different daemon.
_HOOK_SERVER_FILES = (
    Path(__file__).resolve(),
    Path(hook_server_module.__file__).resolve(),
    Path(hooks_module.__file__).resolve(),
    Path(process_module.__file__).resolve(),
    Path(server_daemon_module.__file__).resolve(),
)


class HookPortTaken(Exception):
    """This checkout's hook port is held by a process that is not a hook daemon of this checkout, or by a daemon that
    would not stop, so no hook daemon can serve the checkout until that process ends."""

    def __init__(self, repo: Path, port: int, holder: str) -> None:
        super().__init__(f"the hook port {port} of {repo} is held by {holder}; end that process and run a hook again")
        self.repo = repo
        self.port = port


def _server_named_by(fields: dict[str, Any]) -> RunningServer:
    """The running daemon fields name: its process, checkout, and code stamp; a daemon of the older layout names none."""
    pid = fields.get("pid")
    repo = str(fields.get("repo") or "")
    return RunningServer(RunningProcess(pid if isinstance(pid, int) and pid > 0 else 0), Path(repo) if repo else None, str(fields.get("stamp") or ""))


def _fields_of(address: HookDaemonAddress, server: RunningServer) -> dict[str, Any]:
    """What a daemon publishes in its address file and answers to a ping: where it answers, and who it is."""
    pid = server.pid or None
    return {"host": address.host, "port": address.port, "pid": pid, "stamp": server.code, "repo": str(server.serves or "")}


class HookDaemonAddress:
    """Where a hook daemon answers: its host and port. A hook command sends its event here; `running()` asks the daemon
    here who it is."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    @classmethod
    def from_fields(cls, fields: dict[str, Any], host: str) -> HookDaemonAddress | None:
        """The address fields name; none when they name no port."""
        if not isinstance(fields, dict) or not fields.get("port"):
            return None
        return cls(str(fields.get("host") or host), int(fields["port"]))

    def running(self) -> RunningServer | None:
        """The daemon answering here, as it reports itself; none when no daemon answers a ping. A daemon started by the
        older layout answers with no process, stamp, or checkout."""
        try:
            reply = self._call({"method": "ping"}, _PING_TIMEOUT_SECONDS)
        except (OSError, ValueError):
            return None
        return _server_named_by(reply) if reply.get("ok") else None

    def handle_stdin(self, raw: bytes) -> dict[str, Any]:
        """The fields the daemon's hook server answers for the event an IDE wrote on stdin."""
        return self._call({"method": "handle_stdin", "raw": raw.decode("utf-8-sig")}, _CALL_TIMEOUT_SECONDS)

    def _call(self, request: DaemonMessage, timeout: float) -> DaemonMessage:
        with ExclusivePort(self.host, self.port).connect(timeout) as conn:
            _Wire(conn).write(request)
            return _Wire(conn).read()


class HookDaemonAddressFile:
    """The file a hook daemon publishes its address in. The daemon of this layout writes ``.hook-server/address.json``;
    a daemon started by the older layout wrote ``.cursor/hook-server.json``, which a replacement reads once to find and
    stop that daemon, then removes."""

    def __init__(self, path: Path, host: str) -> None:
        self.path = path
        self._host = host
        self._file = JsonFile(path)

    def address(self) -> HookDaemonAddress | None:
        """The address last published here; none when there is none, or none readable."""
        return HookDaemonAddress.from_fields(self._fields(), self._host)

    def server(self) -> RunningServer | None:
        """The daemon last published here: its process, checkout, and code stamp; none when no address is published."""
        fields = self._fields()
        return _server_named_by(fields) if fields.get("port") else None

    def write(self, address: HookDaemonAddress, server: RunningServer) -> None:
        self._file.write(_fields_of(address, server))

    def _fields(self) -> dict[str, Any]:
        if not self._file.exists():
            return {}
        try:
            return self._file.read()
        except JsonFileUnreadable:
            # A daemon writing its address, or one killed while writing it; the next start writes it again.
            return {}

    def remove(self) -> None:
        try:
            self.path.unlink(missing_ok=True)
        except OSError as held:
            logger.warning("could not remove the hook daemon address %s: %s", self.path, held)


class _Wire:
    """One connection to or from a daemon, carrying length-prefixed JSON messages."""

    def __init__(self, conn: socket.socket) -> None:
        self._conn = conn

    def write(self, message: DaemonMessage) -> None:
        raw = json.dumps(message).encode("utf-8")
        self._conn.sendall(f"{len(raw)}\n".encode("ascii") + raw)

    def read(self) -> DaemonMessage:
        header = b""
        while not header.endswith(b"\n"):
            header += self._received(1)
        length = int(header.decode("ascii"))
        body = b""
        while len(body) < length:
            body += self._received(length - len(body))
        return json.loads(body)

    def _received(self, size: int) -> bytes:
        chunk = self._conn.recv(size)
        if not chunk:
            raise OSError("hook daemon closed")
        return chunk


class _Serving:
    """What a serving daemon answers with: its own address, and the hook server it loads once it holds the port. A ping
    answers at once with the address, so a starting daemon is found by the next hook command and by a second start; an
    event waits until the hook server has loaded."""

    def __init__(self, address: HookDaemonAddress, running: RunningServer) -> None:
        self.address = address
        self.running = running
        self._server: HookServer | None = None
        self._loaded = threading.Event()
        self._dispatch = threading.Lock()

    def load(self, server: HookServer) -> None:
        self._server = server
        self._loaded.set()

    def handle(self, wire: _Wire) -> None:
        message = wire.read()
        method = message.get("method")
        if method == "ping":
            wire.write({"ok": True, **_fields_of(self.address, self.running)})
            return
        if method != "handle_stdin":
            wire.write({"error": f"unknown method {method}"})
            return
        self._loaded.wait(_CALL_TIMEOUT_SECONDS)
        with self._dispatch:
            result = self._server.handle_stdin((message.get("raw") or "").encode("utf-8"))
        wire.write(result.as_dict())


class HookDaemon(ServerDaemon):
    """The hook daemon of one checkout, a *ServerDaemon*. It listens on the one port this checkout's daemon may hold,
    publishes its address in the checkout's ``.hook-server/`` folder, and serves every hook command for the checkout,
    whichever IDE sent it, with one loaded hook server. A hook command ensures it is running, starting it first when none
    answers, and sends its event to its `address`. A daemon that finds the port held by this checkout's daemon on older
    code, including one the older layout started, stops it and takes the port. The folder belongs to no IDE, so a
    checkout that installs for VS Code or Kilo gets no ``.cursor`` folder."""

    HOST = "127.0.0.1"
    FOLDER_NAME = ".hook-server"
    # The hook command every IDE event an install registers runs: this file.
    COMMAND_SCRIPT = Path(__file__).resolve()
    # A hook command waits this long for a daemon it started; the first start imports every toolset in the checkout.
    START_SECONDS = 90
    # How long a daemon that loaded older hook code gets to exit before the replacement gives up on it.
    STOP_SECONDS = 3

    def __init__(self, repo: Path | str, port: int | None = None) -> None:
        self.repo = Path(repo).resolve()
        super().__init__(ExclusivePort(self.HOST, port or self._port_of(self.repo)), CappedLogFile(self.folder / "server.log"))
        self.toolsets = RepositoryToolsets(self.repo)
        self.address = HookDaemonAddress(self.HOST, self.port)
        self.address_file = HookDaemonAddressFile(self.folder / "address.json", self.HOST)
        # Where a daemon started by the older layout published its address; read only to stop that daemon.
        self._older_layout_file = HookDaemonAddressFile(self.repo / ".cursor" / "hook-server.json", self.HOST)

    def __str__(self) -> str:
        return f"the hook daemon of {self.repo}"

    @staticmethod
    def _port_of(repo: Path) -> int:
        """The one port the daemon of repo may listen on, the same every start."""
        key = str(repo).casefold().encode("utf-8")
        offset = int.from_bytes(hashlib.sha256(key).digest()[:4], "big")
        return _PORT_RANGE_START + offset % _PORT_RANGE_SIZE

    @property
    def folder(self) -> Path:
        """The checkout's folder for the daemon's address, log, and start lock."""
        return self.repo / self.FOLDER_NAME

    def running(self) -> RunningServer | None:
        """This checkout's daemon when it answers on its port; none when none does, or another checkout's does."""
        server = self.address.running()
        return server if server is not None and server.is_serving(self.repo) else None

    @property
    def source_stamp(self) -> str:
        """Identity of the hook code this checkout holds now. A daemon that loaded older files is a different daemon."""
        parts: list[str] = []
        for path in self._stamped_files():
            if path.is_file():
                parts.append(f"{path.as_posix()}:{path.stat().st_mtime_ns}")
        return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()

    def _stamped_files(self) -> list[Path]:
        """The hook server's own code, each hook install's ``hook-handlers.json``, and the module of each toolset those
        files list: the code and the list a loaded daemon answers with."""
        installed = InstalledHookHandlers(self.repo)
        found = [*_HOOK_SERVER_FILES, *(handlers.path for handlers in installed.files)]
        for ref in installed.refs:
            try:
                found.append(ToolsetReference(ref).module_file())
            except (ModuleNotFoundError, ValueError):
                continue
        return found

    def ensure(self) -> RunningServer:
        """This checkout's daemon, replacing one on older code and starting one when none answers."""
        self._replace_stale()
        return super().ensure()

    def _replace_stale(self) -> None:
        """Stop a daemon that loaded older hook code. A Cursor reload does not restart it."""
        published = self.address_file.server()
        if published is None or published.code == self.source_stamp:
            return
        try:
            self._stop_process(published.process)
        except ProcessNotStopped as still_running:
            # Its address file stays, so hooks keep reaching the older daemon rather than none.
            logger.warning("the hook daemon on older code keeps running: %s", still_running)
            return
        self.address_file.remove()

    def stop(self) -> None:
        """Stop this checkout's daemon, whichever layout started it, and remove its address files, so no daemon outlives
        its checkout. Closing the checkout's worktree calls this. Only the daemon that answers on this checkout's port as
        this checkout's, or as one of the older layout, is stopped; a daemon that will not stop is logged and left, so
        the close goes on and reports the folder it could not remove."""
        try:
            super().stop()
        except (ProcessNotStopped, HookPortTaken) as still_running:
            logger.warning("the hook daemon of %s keeps running after its checkout closed: %s", self.repo, still_running)
        self.address_file.remove()
        self._older_layout_file.remove()

    def _process_to_stop(self) -> RunningProcess | None:
        holder = self.address.running()
        return self._process_of(holder) if holder is not None and self._is_ours(holder) else None

    def _command(self) -> list[str]:
        return [PythonInterpreter().windowless, "-m", "harness.hooks.hook_daemon", "serve", str(self.repo)]

    def _folder(self) -> Path:
        return self.repo

    def _environment(self) -> dict[str, str]:
        """This process's environment, importing from the checkout."""
        existing = os.environ.get("PYTHONPATH", "")
        return {
            **os.environ,
            "PYTHONPYCACHEPREFIX": self.toolsets.pycache_prefix(),
            "PYTHONPATH": os.pathsep.join(part for part in (self.toolsets.pythonpath(), existing) if part),
        }

    def serve(self, server: HookServer | None = None) -> None:
        """Listen on this checkout's port and answer hook commands with server, until the process ends; with no
        server, the hook server of every toolset the checkout defines. A daemon on older code that holds the port is
        stopped and the port taken over. Return at once, saying so in the log, when this checkout's daemon on the
        current code already holds it; raise *HookPortTaken* when anything else holds it."""
        listener = self.claim_port()
        if listener is None:
            return
        serving = _Serving(
            HookDaemonAddress(self.HOST, listener.getsockname()[1]),
            RunningServer(RunningProcess(os.getpid()), self.repo, self.source_stamp),
        )
        acceptor = threading.Thread(target=self._accept_until_stopped, args=(listener, serving), daemon=True)
        try:
            acceptor.start()
            serving.load(server if server is not None else HookServer.from_repository(self.toolsets))
            self.address_file.write(serving.address, serving.running)
            acceptor.join()
        finally:
            listener.close()

    def claim_port(self) -> socket.socket | None:
        """A listening socket on this checkout's port, taken from the daemon holding it when that daemon is this
        checkout's on older code; none when this checkout's daemon on the current code holds it. Raises *HookPortTaken*
        when a process that is not this checkout's daemon holds it, or one that would not stop."""
        listener = self._port.claim()
        if listener is not None:
            return listener
        holder = self.address.running()
        if holder is None:
            raise HookPortTaken(self.repo, self.port, self._named(self._port.holder(), "a process that answers no hook ping"))
        if not self._is_ours(holder):
            raise HookPortTaken(self.repo, self.port, f"the hook daemon of {holder.serves}")
        if holder.code == self.source_stamp:
            logger.warning("the hook daemon of %s on this code already serves port %s (pid %s)", self.repo, self.port, holder.pid)
            return None
        return self._taken_over_from(holder)

    def _taken_over_from(self, holder: RunningServer) -> socket.socket:
        """The port, claimed once this checkout's daemon on older code that holds it has stopped."""
        older = self._process_of(holder)
        try:
            self._stop_process(older)
        except ProcessNotStopped as still_running:
            raise HookPortTaken(self.repo, self.port, f"process {older.pid}, which would not stop") from still_running
        for _ in range(_CLAIM_TRIES):
            listener = self._port.claim()
            if listener is not None:
                logger.warning("took hook port %s of %s over from the daemon on older code", self.port, self.repo)
                return listener
            time.sleep(_CLAIM_POLL_SECONDS)
        raise HookPortTaken(self.repo, self.port, "a process that still holds it after it was stopped")

    def _is_ours(self, holder: RunningServer) -> bool:
        """Whether the daemon that answered as holder is this checkout's: it says so, or it is of the older layout,
        which names no checkout and holds the port this checkout's daemon may hold."""
        return holder.serves is None or holder.is_serving(self.repo)

    def _process_of(self, holder: RunningServer) -> RunningProcess:
        """The process of this checkout's daemon that answered as holder: the one it reports, or, for a daemon of the
        older layout, which reports none, the one its address file names, else the port's holder."""
        if holder.pid > 0:
            return holder.process
        published = self._older_layout_file.server()
        older_address = self._older_layout_file.address()
        if published is not None and older_address is not None and older_address.port == self.port and published.pid > 0:
            self._older_layout_file.remove()
            return published.process
        found = self._port.holder()
        if found is None:
            raise HookPortTaken(self.repo, self.port, "a hook daemon of the older layout whose process cannot be found")
        return found

    def _named(self, process: RunningProcess | None, what: str) -> str:
        return f"{what} (pid {process.pid})" if process is not None else what

    def _stop_process(self, process: RunningProcess) -> None:
        """Stop a daemon process of this checkout; raises *ProcessNotStopped* when it keeps running."""
        logger.warning("stopping hook daemon process %s of %s", process.pid, self.repo)
        process.stop(self.STOP_SECONDS)

    def _accept_until_stopped(self, listener: socket.socket, serving: _Serving) -> None:
        """Answer every caller off the accept loop.

        A caller served inline holds the loop for the whole dispatch, so the backlog
        fills, Windows refuses the rest, and each refused hook starts another daemon
        wait instead of being answered.
        """
        while True:
            try:
                conn, _ = listener.accept()
            except OSError:
                return
            threading.Thread(target=self._answer, args=(conn, serving), daemon=True).start()

    def _answer(self, conn: socket.socket, serving: _Serving) -> None:
        try:
            serving.handle(_Wire(conn))
        finally:
            conn.close()


def run_hook_command() -> None:
    """The hook command: hand the event on stdin to this checkout's hook daemon and print its answer for the IDE."""
    toolsets = RepositoryToolsets(RUNNING_CHECKOUT)
    daemon = HookDaemon(toolsets.root)
    daemon.toolsets.use_for_this_process()
    os.chdir(toolsets.root)
    raw = sys.stdin.buffer.read()
    if not raw.strip():
        print(json.dumps(HookResult().as_dict()))
        return
    daemon.ensure()
    answer = daemon.address.handle_stdin(raw)
    print(json.dumps(HookResult.from_handler(answer).as_dict()))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "serve":
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
        HookDaemon(Path(sys.argv[2])).serve()
    else:
        run_hook_command()
