"""Processes on this computer: how the hook server, the MCP server, and the scripts start one, in the background with
no console window on Windows or with a Python whose console output a caller reads, and how they ask whether one named by
its process id still runs, or stop it."""
from __future__ import annotations

import os
import signal
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
