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
from harness.agent_tools.agent_tools import ToolsetReference
from harness.hooks.hook_server import HookResult, HookServer
from harness.hooks.hooks import InstalledHookHandlers
from harness.installation.json_file import JsonFile, JsonFileUnreadable
from harness.installation.repository_toolsets import RepositoryToolsets
from harness.process.process import (
    BackgroundStart,
    ExclusivePort,
    ProcessNotStopped,
    PythonInterpreter,
    RunningProcess,
    StoppableProcess,
)

logger = logging.getLogger(__name__)

_PORT_RANGE_START = 20000
_PORT_RANGE_SIZE = 10000
# How long a daemon that loaded older hook code gets to exit before the replacement gives up on it.
_STOP_SECONDS = 3
# A stopped daemon's port can stay bound for a moment after its process ends; the replacement tries this many times.
_CLAIM_TRIES = 20
_CLAIM_POLL_SECONDS = 0.1
# A hook command waits this long for a daemon it started; the first start imports every toolset in the checkout.
_READY_WAIT_SECONDS = 90
_READY_POLL_SECONDS = 0.2
# One dispatch can run a hook that renders guidance; the caller waits for it rather than giving the IDE no answer.
_CALL_TIMEOUT_SECONDS = 600
# A ping answers at once from a live daemon, so a dead or busy address is found quickly.
_PING_TIMEOUT_SECONDS = 5
# The hook server's own code: a daemon that loaded older copies of these is a different daemon.
_HOOK_SERVER_FILES = (
    Path(__file__).resolve(),
    Path(hook_server_module.__file__).resolve(),
    Path(hooks_module.__file__).resolve(),
    Path(process_module.__file__).resolve(),
)


class HookDaemonNotReady(Exception):
    """The hook daemon this checkout started did not answer in time."""

    def __init__(self, repo: Path, seconds: float) -> None:
        super().__init__(f"the hook daemon of {repo} did not answer within {seconds} seconds")
        self.repo = repo


class HookPortTaken(Exception):
    """This checkout's hook port is held by a process that is not a hook daemon of this checkout, or by a daemon that
    would not stop, so no hook daemon can serve the checkout until that process ends."""

    def __init__(self, repo: Path, port: int, holder: str) -> None:
        super().__init__(f"the hook port {port} of {repo} is held by {holder}; end that process and run a hook again")
        self.repo = repo
        self.port = port


class HookDaemonAddress:
    """Where a running hook daemon answers, and who it is: its host and port, its process, the stamp of the hook code
    it loaded, and its checkout. A daemon publishes this in its address file and answers it to a ping. A hook command
    sends its event here; a daemon on older code is stopped through its process. A daemon started by the older layout
    answers a ping with no process, stamp, or checkout."""

    def __init__(self, host: str, port: int, pid: int | None = None, stamp: str = "", repo: str = "") -> None:
        self.host = host
        self.port = port
        self.pid = pid
        self.stamp = stamp
        self.repo = repo
        self.process = StoppableProcess(pid or 0)

    @classmethod
    def from_fields(cls, fields: dict[str, Any], host: str) -> HookDaemonAddress | None:
        """The address fields name; none when they name no port."""
        if not isinstance(fields, dict) or not fields.get("port"):
            return None
        pid = fields.get("pid")
        return cls(
            str(fields.get("host") or host),
            int(fields["port"]),
            int(pid) if isinstance(pid, int) and pid > 0 else None,
            str(fields.get("stamp") or ""),
            str(fields.get("repo") or ""),
        )

    def as_fields(self) -> dict[str, Any]:
        return {"host": self.host, "port": self.port, "pid": self.pid, "stamp": self.stamp, "repo": self.repo}

    def serves(self, repo: Path) -> bool:
        """Whether the daemon here says it serves repo; a daemon of the older layout says nothing."""
        return bool(self.repo) and os.path.normcase(self.repo) == os.path.normcase(str(repo))

    def answers(self) -> bool:
        """Whether a daemon answers a ping at this address."""
        return self.reported() is not None

    def reported(self) -> HookDaemonAddress | None:
        """The address as the daemon answering here reports itself; none when no daemon answers a ping."""
        try:
            reply = self._call({"method": "ping"}, _PING_TIMEOUT_SECONDS)
        except (OSError, ValueError):
            return None
        if not reply.get("ok"):
            return None
        return HookDaemonAddress.from_fields({**reply, "host": self.host, "port": self.port}, self.host)

    def handle_stdin(self, raw: bytes) -> dict[str, Any]:
        """The fields the daemon's hook server answers for the event an IDE wrote on stdin."""
        return self._call({"method": "handle_stdin", "raw": raw.decode("utf-8-sig")}, _CALL_TIMEOUT_SECONDS)

    def _call(self, payload: dict, timeout: float) -> dict:
        with ExclusivePort(self.host, self.port).connect(timeout) as conn:
            _Wire(conn).write(payload)
            return _Wire(conn).read()


class HookDaemonAddressFile:
    """The file a hook daemon publishes its address in. The daemon of this layout writes ``.hook-server/address.json``;
    a daemon started by the older layout wrote ``.cursor/hook-server.json``, which a replacement reads once to find and
    stop that daemon, then removes."""

    def __init__(self, path: Path, host: str) -> None:
        self.path = path
        self._host = host
        self._file = JsonFile(path)

    def read(self) -> HookDaemonAddress | None:
        """The address last published here; none when there is none, or none readable."""
        if not self._file.exists():
            return None
        try:
            fields = self._file.read()
        except JsonFileUnreadable:
            # A daemon writing its address, or one killed while writing it; the next start writes it again.
            return None
        return HookDaemonAddress.from_fields(fields, self._host)

    def write(self, address: HookDaemonAddress) -> None:
        self._file.write(address.as_fields())

    def remove(self) -> None:
        try:
            self.path.unlink(missing_ok=True)
        except OSError as held:
            logger.warning("could not remove the hook daemon address %s: %s", self.path, held)


class _Wire:
    """One connection to or from a daemon, carrying length-prefixed JSON messages."""

    def __init__(self, conn: socket.socket) -> None:
        self._conn = conn

    def write(self, payload: dict) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self._conn.sendall(f"{len(raw)}\n".encode("ascii") + raw)

    def read(self) -> dict:
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


class _SpawnLock:
    """The file that lets one hook command start the daemon while the others wait for it."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def claim(self) -> bool:
        self._release_if_holder_died()
        try:
            fd = os.open(str(self._path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return False
        try:
            os.write(fd, str(os.getpid()).encode("ascii"))
        finally:
            os.close(fd)
        return True

    def release(self) -> None:
        try:
            self._path.unlink(missing_ok=True)
        except OSError:
            return

    def _release_if_holder_died(self) -> None:
        if not self._path.is_file() or RunningProcess(self._holder()).alive:
            return
        self.release()

    def _holder(self) -> int:
        try:
            return int(self._path.read_text(encoding="ascii").strip())
        except (OSError, ValueError):
            return 0


class _Serving:
    """What a serving daemon answers with: its own address, and the hook server it loads once it holds the port. A ping
    answers at once with the address, so a starting daemon is found by the next hook command and by a second start; an
    event waits until the hook server has loaded."""

    def __init__(self, address: HookDaemonAddress) -> None:
        self.address = address
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
            wire.write({"ok": True, **self.address.as_fields()})
            return
        if method != "handle_stdin":
            wire.write({"error": f"unknown method {method}"})
            return
        self._loaded.wait(_CALL_TIMEOUT_SECONDS)
        with self._dispatch:
            result = self._server.handle_stdin((message.get("raw") or "").encode("utf-8"))
        wire.write(result.as_dict())


class HookDaemon:
    """The hook daemon of one checkout. It listens on the one port this checkout's daemon may hold, publishes its
    address in the checkout's ``.hook-server/`` folder, and serves every hook command for the checkout, whichever IDE
    sent it, with one loaded hook server. A hook command asks it for that address, starting the daemon first when none
    answers. A daemon that finds the port held by this checkout's daemon on older code, including one the older layout
    started, stops it and takes the port. The folder belongs to no IDE, so a checkout that installs for VS Code or Kilo
    gets no ``.cursor`` folder."""

    HOST = "127.0.0.1"
    FOLDER_NAME = ".hook-server"
    # The hook command every IDE event an install registers runs: this file.
    COMMAND_SCRIPT = Path(__file__).resolve()

    def __init__(self, repo: Path | str, port: int | None = None) -> None:
        self.repo = Path(repo).resolve()
        self.toolsets = RepositoryToolsets(self.repo)
        self._port = port
        self.address_file = HookDaemonAddressFile(self.folder / "address.json", self.HOST)
        # Where a daemon started by the older layout published its address; read only to stop that daemon.
        self._older_layout_file = HookDaemonAddressFile(self.repo / ".cursor" / "hook-server.json", self.HOST)

    @property
    def folder(self) -> Path:
        """The checkout's folder for the daemon's address, log, and start lock."""
        return self.repo / self.FOLDER_NAME

    @property
    def log_path(self) -> Path:
        """The file a started daemon writes its output to."""
        return self.folder / "server.log"

    @property
    def port(self) -> int:
        """The one port this checkout's daemon may listen on, the same every start."""
        if self._port is not None:
            return self._port
        key = str(self.repo).casefold().encode("utf-8")
        offset = int.from_bytes(hashlib.sha256(key).digest()[:4], "big")
        return _PORT_RANGE_START + offset % _PORT_RANGE_SIZE

    def live_address(self) -> HookDaemonAddress | None:
        """The address of this checkout's daemon when one answers there; none when none does."""
        address = self.address_file.read()
        return address if address is not None and address.answers() else None

    def is_running(self) -> bool:
        """Whether this checkout's hook daemon answers."""
        return self.live_address() is not None

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

    def ensure(self) -> HookDaemonAddress:
        """The address of this checkout's daemon, replacing one on older code and starting one when none answers."""
        self.replace_stale()
        address = self.live_address()
        if address is not None:
            return address
        self._start_once()
        return self._wait_until_live(time.time() + _READY_WAIT_SECONDS)

    def replace_stale(self) -> None:
        """Stop a daemon that loaded older hook code. A Cursor reload does not restart it."""
        published = self.address_file.read()
        if published is None or published.stamp == self.source_stamp:
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
        holder = HookDaemonAddress(self.HOST, self.port).reported()
        if holder is not None and self._is_ours(holder):
            try:
                self._stop_process(self._process_of(holder, ExclusivePort(self.HOST, self.port)))
            except (ProcessNotStopped, HookPortTaken) as still_running:
                logger.warning("the hook daemon of %s keeps running after its checkout closed: %s", self.repo, still_running)
        self.address_file.remove()
        self._older_layout_file.remove()

    def spawn(self) -> None:
        """Start this checkout's daemon in the background, importing from the checkout, with its output in
        ``log_path``."""
        toolsets = self.toolsets
        existing = os.environ.get("PYTHONPATH", "")
        env = {
            **os.environ,
            "PYTHONPYCACHEPREFIX": toolsets.pycache_prefix(),
            "PYTHONPATH": os.pathsep.join(part for part in (toolsets.pythonpath(), existing) if part),
        }
        self.folder.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as log:
            BackgroundStart().run(
                [PythonInterpreter().windowless, "-m", "harness.hooks.hook_daemon", "serve", str(self.repo)],
                cwd=self.repo,
                env=env,
                log=log,
            )

    def serve(self, server: HookServer | None = None) -> None:
        """Listen on this checkout's port and answer hook commands with server, until the process ends; with no
        server, the hook server of every toolset the checkout defines. A daemon on older code that holds the port is
        stopped and the port taken over. Return at once, saying so in the log, when this checkout's daemon on the
        current code already holds it; raise *HookPortTaken* when anything else holds it."""
        listener = self.claim_port()
        if listener is None:
            return
        serving = _Serving(HookDaemonAddress(self.HOST, listener.getsockname()[1], os.getpid(), self.source_stamp, str(self.repo)))
        acceptor = threading.Thread(target=self._accept_until_stopped, args=(listener, serving), daemon=True)
        try:
            acceptor.start()
            serving.load(server if server is not None else HookServer.from_repository(self.toolsets))
            self.address_file.write(serving.address)
            acceptor.join()
        finally:
            listener.close()

    def claim_port(self) -> socket.socket | None:
        """A listening socket on this checkout's port, taken from the daemon holding it when that daemon is this
        checkout's on older code; none when this checkout's daemon on the current code holds it. Raises *HookPortTaken*
        when a process that is not this checkout's daemon holds it, or one that would not stop."""
        port = ExclusivePort(self.HOST, self.port)
        listener = port.claim()
        if listener is not None:
            return listener
        holder = HookDaemonAddress(self.HOST, self.port).reported()
        if holder is None:
            raise HookPortTaken(self.repo, self.port, self._named(port.holder(), "a process that answers no hook ping"))
        if not self._is_ours(holder):
            raise HookPortTaken(self.repo, self.port, f"the hook daemon of {holder.repo}")
        if holder.stamp == self.source_stamp:
            logger.warning("the hook daemon of %s on this code already serves port %s (pid %s)", self.repo, self.port, holder.pid)
            return None
        older = self._process_of(holder, port)
        try:
            self._stop_process(older)
        except ProcessNotStopped as still_running:
            raise HookPortTaken(self.repo, self.port, f"process {older.pid}, which would not stop") from still_running
        for _ in range(_CLAIM_TRIES):
            listener = port.claim()
            if listener is not None:
                logger.warning("took hook port %s of %s over from the daemon on older code", self.port, self.repo)
                return listener
            time.sleep(_CLAIM_POLL_SECONDS)
        raise HookPortTaken(self.repo, self.port, "a process that still holds it after it was stopped")

    def _is_ours(self, holder: HookDaemonAddress) -> bool:
        """Whether the daemon that answered as holder is this checkout's: it says so, or it is of the older layout,
        which names no checkout and holds the port this checkout's daemon may hold."""
        return not holder.repo or holder.serves(self.repo)

    def _process_of(self, holder: HookDaemonAddress, port: ExclusivePort) -> StoppableProcess:
        """The process of this checkout's daemon that answered as holder: the one it reports, or, for a daemon of the
        older layout, which reports none, the one its address file names, else the port's holder."""
        if holder.pid is not None:
            return holder.process
        published = self._older_layout_file.read()
        if published is not None and published.port == self.port and published.pid is not None:
            self._older_layout_file.remove()
            return published.process
        found = port.holder()
        if found is None:
            raise HookPortTaken(self.repo, self.port, "a hook daemon of the older layout whose process cannot be found")
        return found

    def _named(self, process: StoppableProcess | None, what: str) -> str:
        return f"{what} (pid {process.pid})" if process is not None else what

    def _stop_process(self, process: StoppableProcess) -> None:
        """Stop a daemon process of this checkout; raises *ProcessNotStopped* when it keeps running."""
        logger.warning("stopping hook daemon process %s of %s", process.pid, self.repo)
        process.stop(_STOP_SECONDS)

    def _start_once(self) -> None:
        """Start the daemon unless another hook command is starting it; either way, it is starting when this returns."""
        lock = _SpawnLock(self.folder / "spawn.lock")
        self.folder.mkdir(parents=True, exist_ok=True)
        deadline = time.time() + _READY_WAIT_SECONDS
        while time.time() < deadline:
            if self.live_address() is not None:
                return
            if not lock.claim():
                time.sleep(_READY_POLL_SECONDS)
                continue
            try:
                self.spawn()
                self._wait_until_live(deadline)
            finally:
                lock.release()
            return

    def _wait_until_live(self, deadline: float) -> HookDaemonAddress:
        while time.time() < deadline:
            address = self.live_address()
            if address is not None:
                return address
            time.sleep(_READY_POLL_SECONDS)
        raise HookDaemonNotReady(self.repo, _READY_WAIT_SECONDS)

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
    toolsets = RepositoryToolsets.of_running_checkout()
    daemon = HookDaemon(toolsets.root)
    daemon.toolsets.use_for_this_process()
    os.chdir(toolsets.root)
    raw = sys.stdin.buffer.read()
    if not raw.strip():
        print(json.dumps(HookResult().as_dict()))
        return
    answer = daemon.ensure().handle_stdin(raw)
    print(json.dumps(HookResult.from_handler(answer).as_dict()))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "serve":
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
        HookDaemon(Path(sys.argv[2])).serve()
    else:
        run_hook_command()
