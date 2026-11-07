"""How the hook server, the MCP server, and the scripts start a process on this computer: in the background with no
console window on Windows, or with a Python whose console output a caller reads."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import IO

# Windows' CREATE_BREAKAWAY_FROM_JOB: the child leaves the starter's job, so it outlives the chat that started it.
_CREATE_BREAKAWAY_FROM_JOB = 0x01000000


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
