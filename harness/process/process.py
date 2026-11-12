"""Processes on this computer: how the hook server, the MCP server, and the scripts start one, in the background with
no console window on Windows or with a Python whose console output a caller reads, and how they ask whether one named by
its process id still runs, or stop it."""
from __future__ import annotations

import os
import re
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import IO

# Windows' CREATE_BREAKAWAY_FROM_JOB: the child leaves the starter's job, so it outlives the chat that started it.
_CREATE_BREAKAWAY_FROM_JOB = 0x01000000
# The access right that lets Windows open a process only to ask about it.
_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
# The exit code Windows reports for a process that has not exited.
_STILL_ACTIVE = 259
# How long a stop waits between looks at whether the process has ended.
_POLL_SECONDS = 0.05
# How long a connect to a port of this computer waits. A listening server accepts at once; where nothing listens,
# Windows retries the connect for about two seconds (four for ``localhost``, tried as ::1 and then 127.0.0.1) before it
# reports it refused, so a caller waiting longer only waits out those retries.
LOOPBACK_CONNECT_SECONDS = 0.5


class ListeningPorts:
    """Which process on this computer listens on which TCP port, as ``netstat -ano`` (Windows) or ``ss -ltnp``
    (elsewhere) reports it now. A server that finds its port held asks it for the holder, and the instances script asks
    it which ports each of its processes listens on."""

    def by_process(self) -> dict[int, list[int]]:
        """Each listening process's id, with the ports it listens on."""
        heard: dict[int, set[int]] = {}
        for pid, port in self._listeners():
            heard.setdefault(pid, set()).add(port)
        return {pid: sorted(ports) for pid, ports in heard.items()}

    def holder(self, port: int) -> StoppableProcess | None:
        """The process listening on port; none when no process does, or none this computer reports."""
        return next((StoppableProcess(pid) for pid, heard in self._listeners() if heard == port), None)

    def _listeners(self) -> list[tuple[int, int]]:
        if sys.platform == "win32":
            return self._netstat_listeners()
        return self._ss_listeners()

    def _netstat_listeners(self) -> list[tuple[int, int]]:
        found: list[tuple[int, int]] = []
        for line in self._output(["netstat", "-ano", "-p", "TCP"]).splitlines():
            parts = line.split()
            if len(parts) < 5 or parts[3].upper() != "LISTENING":
                continue
            port_text = parts[1].rsplit(":", 1)[-1]
            if port_text.isdigit() and parts[4].isdigit():
                found.append((int(parts[4]), int(port_text)))
        return found

    def _ss_listeners(self) -> list[tuple[int, int]]:
        found: list[tuple[int, int]] = []
        for line in self._output(["ss", "-ltnp"]).splitlines():
            pid_match = re.search(r"pid=(\d+)", line)
            port_match = re.search(r":(\d+)\s", line)
            if pid_match is not None and port_match is not None:
                found.append((int(pid_match.group(1)), int(port_match.group(1))))
        return found

    def _output(self, command: list[str]) -> str:
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return completed.stdout or ""


class ExclusivePort:
    """The one port a long-running server of this computer may listen on, claimed by binding it exclusively: two
    servers cannot both hold one port, and no lock file can promise that once its holder is killed without cleanup."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    def holder(self) -> StoppableProcess | None:
        """The process listening on this port now; none when none is."""
        return ListeningPorts().holder(self.port)

    def connect(self, reply_seconds: float) -> socket.socket:
        """A connection to the server listening on this port, which then waits up to reply_seconds for each reply.
        Raises ``OSError`` within ``LOOPBACK_CONNECT_SECONDS`` when no server listens here."""
        connection = socket.create_connection((self.host, self.port), timeout=LOOPBACK_CONNECT_SECONDS)
        connection.settimeout(reply_seconds)
        return connection

    def claim(self) -> socket.socket | None:
        """A listening socket on the port; none when another server already holds it, so the loser exits."""
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sys.platform == "win32":
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        try:
            listener.bind((self.host, self.port))
        except OSError:
            listener.close()
            return None
        listener.listen(socket.SOMAXCONN)
        return listener


class PythonInterpreter:
    """One Python on this computer. A background server runs it without a console window; a hook command, whose JSON
    the IDE reads from stdout, runs it on a console, because ``pythonw.exe`` drops stdout."""

    def __init__(self, executable: str | Path | None = None) -> None:
        self.executable = Path(executable or sys.executable)

    @property
    def windowless(self) -> str:
        """``pythonw.exe`` beside this Python on Windows, so a background server opens no console; this Python
        elsewhere, or when there is no ``pythonw.exe``."""
        if sys.platform == "win32":
            pythonw = self.executable.with_name("pythonw.exe")
            if pythonw.is_file():
                return str(pythonw)
        return str(self.executable)

    @property
    def console(self) -> str:
        """``python.exe`` beside this Python when it is ``pythonw.exe``, so what it prints reaches its caller."""
        if sys.platform == "win32" and self.executable.name.lower() == "pythonw.exe":
            console = self.executable.with_name("python.exe")
            if console.is_file():
                return str(console)
        return str(self.executable)


class BackgroundStart:
    """How a background server is started so it keeps running without a console window. On Windows it gets a process
    group of its own and no window, and it breaks away from the starter's job unless it is started inside that job.
    ``DETACHED_PROCESS`` is never used: Windows then ignores ``CREATE_NO_WINDOW`` and opens a console."""

    def __init__(self, breaks_away: bool = True) -> None:
        self.breaks_away = breaks_away

    def inside_starters_job(self) -> BackgroundStart:
        """The same start without breaking away, for a Windows job that refuses to let its children leave."""
        return BackgroundStart(breaks_away=False)

    @property
    def creationflags(self) -> int:
        if sys.platform != "win32":
            return 0
        flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        return flags | _CREATE_BREAKAWAY_FROM_JOB if self.breaks_away else flags

    @property
    def startupinfo(self) -> subprocess.STARTUPINFO | None:
        """Windows' instruction to hide the window; none elsewhere."""
        if sys.platform != "win32":
            return None
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = subprocess.SW_HIDE
        return startup

    def run(self, command: list[str], *, cwd: str | Path, env: dict[str, str], log: IO[str]) -> subprocess.Popen:
        """Start command in the background in cwd, writing its output and errors to log."""
        return subprocess.Popen(
            command,
            cwd=str(cwd),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=self.creationflags,
            startupinfo=self.startupinfo,
            close_fds=True,
        )


class RunningProcess:
    """A process by its id, to ask whether it is still running. A hook server's lock file, a daemon's address file,
    and the instances script all name a process this way."""

    def __init__(self, pid: int) -> None:
        self.pid = int(pid or 0)

    @property
    def alive(self) -> bool:
        """True while the process runs. Windows is asked through ``OpenProcess``, because ``os.kill(pid, 0)`` on
        Windows ends the process rather than asking about it; elsewhere a process this user may not signal still
        counts as running."""
        if self.pid <= 0:
            return False
        if sys.platform == "win32":
            import ctypes

            kernel = ctypes.windll.kernel32
            handle = kernel.OpenProcess(_PROCESS_QUERY_LIMITED_INFORMATION, False, self.pid)
            if not handle:
                return False
            # A process that has exited can still be opened while another process holds a handle to it.
            code = ctypes.c_ulong()
            try:
                answered = kernel.GetExitCodeProcess(handle, ctypes.byref(code))
            finally:
                kernel.CloseHandle(handle)
            return not answered or code.value == _STILL_ACTIVE
        try:
            os.kill(self.pid, 0)
        except PermissionError:
            return True
        except OSError:
            return False
        return True


class ProcessNotStopped(Exception):
    """A process was asked to stop and is still running."""

    def __init__(self, pid: int, cause: BaseException | None = None) -> None:
        reason = f": {cause}" if cause is not None else ""
        super().__init__(f"process {pid} is still running after it was asked to stop{reason}")
        self.pid = pid
        self.cause = cause


class StoppableProcess(RunningProcess):
    """A process by its id that this one may end, such as the server an address file names. An id of 0 and this
    process's own id are never signalled: a blank or stale file must not end the process that reads it."""

    def stop(self, wait_seconds: float) -> None:
        """End the process and wait up to ``wait_seconds`` for it to exit. A process already gone needs nothing."""
        if self.pid <= 0 or self.pid == os.getpid():
            return
        try:
            os.kill(self.pid, signal.SIGTERM)
        except OSError as refused:
            if self.alive:
                raise ProcessNotStopped(self.pid, refused) from refused
            return
        self._wait_until_ended(wait_seconds)

    def _wait_until_ended(self, wait_seconds: float) -> None:
        deadline = time.monotonic() + wait_seconds
        while self.alive:
            if time.monotonic() >= deadline:
                raise ProcessNotStopped(self.pid)
            time.sleep(_POLL_SECONDS)
