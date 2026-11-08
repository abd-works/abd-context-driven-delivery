"""The hook daemon of one checkout: the process that keeps the hook server loaded between hook commands, and the address
a hook command reaches it at."""
from __future__ import annotations

import hashlib
import json
import logging
import os
import socket
import sys
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.installation.repository_toolsets import RepositoryToolsets
from harness.process.process import BackgroundStart, PythonInterpreter
from harness.process.running_process import RunningProcess
from harness.process.stoppable_process import ProcessNotStopped, StoppableProcess

if TYPE_CHECKING:
    from harness.hooks.hook_server import HookServer

logger = logging.getLogger(__name__)

_PORT_RANGE_START = 20000
_PORT_RANGE_SIZE = 10000
# How long a daemon that loaded older hook code gets to exit before the replacement gives up on it.
_STOP_SECONDS = 3
# A hook command waits this long for a daemon it started; the first start imports every toolset in the checkout.
_READY_WAIT_SECONDS = 90
_READY_POLL_SECONDS = 0.2
# One dispatch can run a hook that renders guidance; the caller waits for it rather than giving the IDE no answer.
_CALL_TIMEOUT_SECONDS = 600
# A ping answers at once from a live daemon, so a dead or busy address is found quickly.
_PING_TIMEOUT_SECONDS = 5
_SOURCE_STAMP_FILES = (
    Path("harness/hooks/hook_daemon.py"),
    Path("harness/hooks/hook_server.py"),
    Path("harness/process/running_process.py"),
    Path("harness/process/stoppable_process.py"),
    Path("harness/guidance/rule.py"),
    Path("harness/guidance_actions/guidance_actions.py"),
)


class HookDaemonNotReady(Exception):
    """The hook daemon this checkout started did not answer in time."""

    def __init__(self, repo: Path, seconds: float) -> None:
        super().__init__(f"the hook daemon of {repo} did not answer within {seconds} seconds")
        self.repo = repo


class HookDaemonAddress:
    """Where a running hook daemon answers, as it publishes it: its host, port, process, and the stamp of the hook code
    it loaded. A hook command sends its event here; a daemon on older code is stopped through its process."""

    def __init__(self, host: str, port: int, pid: int | None = None, stamp: str = "") -> None:
        self.host = host
        self.port = port
        self.pid = pid
        self.stamp = stamp
        self.process = StoppableProcess(pid or 0)

    def answers(self) -> bool:
        """Whether a daemon answers a ping at this address."""
        try:
            return bool(self._call({"method": "ping"}, _PING_TIMEOUT_SECONDS).get("ok"))
        except OSError:
            return False

    def handle_stdin(self, raw: bytes) -> dict[str, Any]:
        """The fields the daemon's hook server answers for the event an IDE wrote on stdin."""
        return self._call({"method": "handle_stdin", "raw": raw.decode("utf-8-sig")}, _CALL_TIMEOUT_SECONDS)

    def _call(self, payload: dict, timeout: float) -> dict:
        with socket.create_connection((self.host, self.port), timeout=timeout) as conn:
            _Wire(conn).write(payload)
            return _Wire(conn).read()


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


class HookDaemon:
    """The hook daemon of one checkout. It listens on the one port this checkout's daemon may hold, publishes its
    address in ``.cursor/hook-server.json``, and serves every hook command for the checkout with one loaded hook
    server. A hook command asks it for that address, starting the daemon first when none answers."""

    HOST = "127.0.0.1"

    def __init__(self, repo: Path | str, port: int | None = None) -> None:
        self.repo = Path(repo).resolve()
        self.toolsets = RepositoryToolsets(self.repo)
        self._port = port
        self._dispatch = threading.Lock()

    @property
    def state_path(self) -> Path:
        """The address file a running daemon publishes."""
        return self.repo / ".cursor" / "hook-server.json"

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
        address = self._published_address()
        return address if address is not None and address.answers() else None

    def is_running(self) -> bool:
        """Whether this checkout's hook daemon answers."""
        return self.live_address() is not None

    @property
    def source_stamp(self) -> str:
        """Identity of the hook code this checkout holds now. A daemon that loaded older files is a different daemon."""
        parts: list[str] = []
        for relative in _SOURCE_STAMP_FILES:
            path = self.repo / relative
            if path.is_file():
                parts.append(f"{relative.as_posix()}:{path.stat().st_mtime_ns}")
        return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()

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
        published = self._published_address()
        if published is None or published.stamp == self.source_stamp:
            return
        try:
            published.process.stop(_STOP_SECONDS)
        except ProcessNotStopped as still_running:
            # Its address file stays, so hooks keep reaching the older daemon rather than none.
            logger.warning("the hook daemon on older code keeps running: %s", still_running)
            return
        try:
            self.state_path.unlink()
        except OSError:
            return

    def spawn(self) -> None:
        """Start this checkout's daemon in the background, importing from the checkout, with its output in
        ``.cursor/hook-server.log``."""
        toolsets = self.toolsets
        existing = os.environ.get("PYTHONPATH", "")
        env = {
            **os.environ,
            "PYTHONPYCACHEPREFIX": toolsets.pycache_prefix(),
            "PYTHONPATH": os.pathsep.join(part for part in (toolsets.pythonpath(), existing) if part),
        }
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path.parent / "hook-server.log", "a", encoding="utf-8") as log:
            BackgroundStart().run(
                [PythonInterpreter().windowless, "-m", "harness.hooks.hook_daemon", str(self.repo)], cwd=self.repo, env=env, log=log
            )

    def serve(self, server: HookServer | None = None) -> None:
        """Listen on this checkout's port and answer hook commands with server, until the process ends; with no
        server, the hook server of every toolset the checkout defines. Return at once when another daemon holds the
        port."""
        listener = self._claim_port()
        if listener is None:
            return
        try:
            server = server if server is not None else self._loaded_server()
            self._publish_address(listener.getsockname()[1])
            self._serve_until_stopped(listener, server)
        finally:
            listener.close()

    def _loaded_server(self) -> HookServer:
        from harness.hooks.hook_server import HookServer

        return HookServer.from_repository(self.toolsets)

    def _start_once(self) -> None:
        """Start the daemon unless another hook command is starting it; either way, it is starting when this returns."""
        lock = _SpawnLock(self.state_path.parent / "hook-server.spawn.lock")
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
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

    def _published_address(self) -> HookDaemonAddress | None:
        """The address the daemon last published; none when there is none, or none readable."""
        if not self.state_path.is_file():
            return None
        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            # A daemon writing its address, or one killed while writing it; the next start writes it again.
            return None
        if not isinstance(state, dict) or not state.get("port"):
            return None
        return HookDaemonAddress(state.get("host") or self.HOST, int(state["port"]), state.get("pid"), str(state.get("stamp") or ""))

    def _claim_port(self) -> socket.socket | None:
        """None when a daemon already holds this checkout's port, so the loser exits.

        An exclusive bind is the claim — two daemons cannot both hold one port, and
        no lock file can promise that once the holder is killed without cleanup.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sys.platform == "win32":
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        try:
            sock.bind((self.HOST, self.port))
        except OSError:
            sock.close()
            return None
        sock.listen(socket.SOMAXCONN)
        return sock

    def _publish_address(self, port: int) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"host": self.HOST, "port": port, "pid": os.getpid(), "stamp": self.source_stamp}
        self.state_path.write_text(json.dumps(payload), encoding="utf-8")

    def _serve_until_stopped(self, listener: socket.socket, server: HookServer) -> None:
        """Answer every caller off the accept loop.

        A caller served inline holds the loop for the whole dispatch, so the backlog
        fills, Windows refuses the rest, and each refused hook starts another daemon
        wait instead of being answered.
        """
        while True:
            conn, _ = listener.accept()
            threading.Thread(target=self._answer, args=(conn, server), daemon=True).start()

    def _answer(self, conn: socket.socket, server: HookServer) -> None:
        try:
            self._handle(_Wire(conn), server)
        finally:
            conn.close()

    def _handle(self, wire: _Wire, server: HookServer) -> None:
        message = wire.read()
        method = message.get("method")
        if method == "ping":
            wire.write({"ok": True})
            return
        if method != "handle_stdin":
            wire.write({"error": f"unknown method {method}"})
            return
        with self._dispatch:
            result = server.handle_stdin((message.get("raw") or "").encode("utf-8"))
        wire.write(result.as_dict())


if __name__ == "__main__":
    HookDaemon(Path(sys.argv[1] if len(sys.argv) > 1 else ".")).serve()
