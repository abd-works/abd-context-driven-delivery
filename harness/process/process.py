"""Processes on this computer: how the hook server, the MCP server, and the scripts start one, in the background with
no console window on Windows or with a Python whose console output a caller reads, and how they ask whether one named by
its process id still runs, or stop it."""
from __future__ import annotations

import base64
import ctypes
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
# What a start outside the caller's job runs once WMI has created it: the command, its output appended to the log.
OUTSIDE_JOB_LAUNCHER = Path(__file__).resolve().parent / "outside_job_launcher.py"
# The environment variables that carry WMI's command line and folder to PowerShell; the process WMI creates gets every
# other variable PowerShell has, which is the started command's environment.
_WMI_COMMAND_LINE_ENV = "CDD_WMI_COMMAND_LINE"
_WMI_FOLDER_ENV = "CDD_WMI_FOLDER"
# Win32_Process.Create, with no window (ShowWindow 0) and the environment PowerShell runs with; it prints WMI's return
# value and the id of the process it created.
_WMI_CREATE = """
$vars = [string[]]@(Get-ChildItem env: | Where-Object { $_.Name -notlike 'CDD_WMI_*' } | ForEach-Object { "$($_.Name)=$($_.Value)" })
$startup = New-CimInstance -CimClass (Get-CimClass -ClassName Win32_ProcessStartup) -ClientOnly -Property @{ ShowWindow = [uint16]0; EnvironmentVariables = $vars }
$created = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $env:CDD_WMI_COMMAND_LINE; CurrentDirectory = $env:CDD_WMI_FOLDER; ProcessStartupInformation = $startup }
Write-Output "$($created.ReturnValue) $($created.ProcessId)"
"""
# How long PowerShell may take to ask WMI for the process; it answers in well under a second.
_WMI_SECONDS = 60
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

# GetExtendedTcpTable's TCP_TABLE_OWNER_PID_LISTENER: only listening sockets, each with its process id.
_TCP_TABLE_OWNER_PID_LISTENER = 3
# The table's leading socket count, a DWORD, before its rows.
_TCP_TABLE_COUNT_BYTES = 4
# A row's local port sits in the low 16 bits of its DWORD, in network byte order.
_PORT_BITS = 0xFFFF
# How long ``ss`` may take to list this computer's listening sockets before the answer is taken as empty.
_LISTENER_QUERY_SECONDS = 30


class _TcpRowOwnerPid(ctypes.Structure):
    """One socket of Windows' TCP table: MIB_TCPROW_OWNER_PID."""

    _fields_ = [
        ("state", ctypes.c_uint32),
        ("local_address", ctypes.c_uint32),
        ("local_port", ctypes.c_uint32),
        ("remote_address", ctypes.c_uint32),
        ("remote_port", ctypes.c_uint32),
        ("owning_pid", ctypes.c_uint32),
    ]


class _ListeningPorts:
    """Which process on this computer listens on which TCP port, as Windows' TCP table or ``ss -ltnp`` (elsewhere)
    reports it now. An *ExclusivePort* asks it for the process holding the port, and a *RunningProcess* for the ports
    it listens on."""

    def by_process(self) -> dict[int, list[int]]:
        """Each listening process's id, with the ports it listens on."""
        heard: dict[int, set[int]] = {}
        for pid, port in self._listeners():
            heard.setdefault(pid, set()).add(port)
        return {pid: sorted(ports) for pid, ports in heard.items()}

    def holder(self, port: int) -> RunningProcess | None:
        """The process listening on port; none when no process does, or none this computer reports."""
        return next((RunningProcess(pid) for pid, heard in self._listeners() if heard == port), None)

    def _listeners(self) -> list[tuple[int, int]]:
        if sys.platform == "win32":
            return self._windows_listeners()
        return self._ss_listeners()

    def _windows_listeners(self) -> list[tuple[int, int]]:
        """Windows' own table of listening IPv4 sockets. It asks for listeners by kind rather than by each socket's
        state, because some Windows builds report a listener's state as 0, and ``netstat`` then leaves it out."""
        table = self._windows_listener_table()
        count = ctypes.cast(table, ctypes.POINTER(ctypes.c_uint32))[0]
        rows = ctypes.cast(ctypes.addressof(table) + _TCP_TABLE_COUNT_BYTES, ctypes.POINTER(_TcpRowOwnerPid * count))[0]
        return [(row.owning_pid, socket.ntohs(row.local_port & _PORT_BITS)) for row in rows]

    def _windows_listener_table(self) -> ctypes.Array:
        get_table = ctypes.windll.iphlpapi.GetExtendedTcpTable
        size = ctypes.c_uint32(0)
        get_table(None, ctypes.byref(size), False, socket.AF_INET, _TCP_TABLE_OWNER_PID_LISTENER, 0)
        table = ctypes.create_string_buffer(size.value)
        if get_table(table, ctypes.byref(size), False, socket.AF_INET, _TCP_TABLE_OWNER_PID_LISTENER, 0) != 0:
            return ctypes.create_string_buffer(_TCP_TABLE_COUNT_BYTES)
        return table

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
            completed = subprocess.run(command, capture_output=True, text=True, timeout=_LISTENER_QUERY_SECONDS, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return completed.stdout or ""


class ExclusivePort:
    """The one port a long-running server of this computer may listen on, claimed by binding it exclusively: two
    servers cannot both hold one port, and no lock file can promise that once its holder is killed without cleanup."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    def holder(self) -> RunningProcess | None:
        """The process listening on this port now; none when none is."""
        return _ListeningPorts().holder(self.port)

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


class OutsideJobStartFailed(Exception):
    """WMI did not create the process a background start asked it for."""

    def __init__(self, command_line: str, answer: str) -> None:
        super().__init__(f"WMI did not start {command_line}: {answer.strip() or 'no answer'}")
        self.command_line = command_line


class Wmi:
    """Windows Management Instrumentation, reached through PowerShell. A process ``Win32_Process.Create`` makes is
    created by the WMI service, so no job of the caller's holds it, and it outlives the chat that asked for it."""

    def create(self, command_line: str, folder: str, env: dict[str, str]) -> int:
        """Create command_line in folder with env as its environment and no window; answer the new process's id."""
        script = base64.b64encode(_WMI_CREATE.encode("utf-16-le")).decode("ascii")
        completed = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-EncodedCommand", script],
            env={**env, _WMI_COMMAND_LINE_ENV: command_line, _WMI_FOLDER_ENV: folder},
            capture_output=True, text=True, timeout=_WMI_SECONDS, check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        answer = completed.stdout.split()
        if len(answer) != 2 or answer[0] != "0":
            raise OutsideJobStartFailed(command_line, completed.stdout + completed.stderr)
        return int(answer[1])


class BackgroundStart:
    """How a background server is started so it keeps running without a console window, past the chat that started it.
    On Windows it gets a process group of its own and no window, and it breaks away from the starter's job; where that
    job refuses breakaway, as a chat's does, WMI creates it outside every job instead (*Wmi*), through a launcher that
    appends its output to the log. ``DETACHED_PROCESS`` is never used: Windows then ignores ``CREATE_NO_WINDOW`` and
    opens a console. The process writes its output and errors to the start's log, or nowhere when it has none."""

    def __init__(self, log: IO[str] | None = None, wmi: Wmi | None = None) -> None:
        self.log = log
        self._wmi = wmi or Wmi()

    @property
    def creationflags(self) -> int:
        if sys.platform != "win32":
            return 0
        return getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0) | _CREATE_BREAKAWAY_FROM_JOB

    @property
    def startupinfo(self) -> subprocess.STARTUPINFO | None:
        """Windows' instruction to hide the window; none elsewhere."""
        if sys.platform != "win32":
            return None
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = subprocess.SW_HIDE
        return startup

    def run(self, command: list[str], cwd: str | Path, env: dict[str, str]) -> RunningProcess:
        """Start command in the background in cwd, with env as its environment, and answer the process started. A
        start through WMI answers the launcher, which runs exactly as long as command does."""
        try:
            return RunningProcess(self._start_breaking_away(command, cwd, env).pid)
        except PermissionError:
            if sys.platform != "win32":
                raise
            return self._start_outside_job(command, cwd, env)

    def _start_breaking_away(self, command: list[str], cwd: str | Path, env: dict[str, str]) -> subprocess.Popen:
        return subprocess.Popen(
            command,
            cwd=str(cwd),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=self.log if self.log is not None else subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            creationflags=self.creationflags,
            startupinfo=self.startupinfo,
            close_fds=True,
        )

    def _start_outside_job(self, command: list[str], cwd: str | Path, env: dict[str, str]) -> RunningProcess:
        log_path = os.devnull if self.log is None else self.log.name
        if self.log is not None:
            self.log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} breakaway refused; starting outside the caller's job through WMI\n")
            self.log.flush()
        launcher = [PythonInterpreter().windowless, str(OUTSIDE_JOB_LAUNCHER), log_path, *command]
        return RunningProcess(self._wmi.create(subprocess.list2cmdline(launcher), str(cwd), env))


class RunningProcess:
    """A process by its id, to ask whether it is still running and which ports it listens on, and to stop it. A hook
    server's lock file, a daemon's address file, and the instances script all name a process this way. An id of 0 and
    this process's own id are never signalled: a blank or stale file must not end the process that reads it."""

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
            return self._alive_on_windows()
        try:
            os.kill(self.pid, 0)
        except PermissionError:
            return True
        except OSError:
            return False
        return True

    def _alive_on_windows(self) -> bool:
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

    @property
    def listening_ports(self) -> list[int]:
        """The TCP ports the process listens on now, in order."""
        return _ListeningPorts().by_process().get(self.pid, [])

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


class SpawnLock:
    """The file that lets one caller start a server while the others wait for it: the hook daemon's hook commands, and
    the chats and installs that ensure the cdd server. It names the process holding it, so a lock left by a process
    that has ended is taken over rather than waited on forever."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def claim(self) -> bool:
        """Take the lock; False when a running process already holds it."""
        self._release_if_holder_died()
        self._path.parent.mkdir(parents=True, exist_ok=True)
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


class ProcessNotStopped(Exception):
    """A process was asked to stop and is still running."""

    def __init__(self, pid: int, cause: BaseException | None = None) -> None:
        reason = f": {cause}" if cause is not None else ""
        super().__init__(f"process {pid} is still running after it was asked to stop{reason}")
        self.pid = pid
        self.cause = cause

