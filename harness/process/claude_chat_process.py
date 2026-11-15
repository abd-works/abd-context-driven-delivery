"""The Claude Code process a chat runs in, and the folder its session works in now.

Claude Code writes ``sessions/<pid>.json`` under its config folder for every chat process while it runs, holding the
session's id and the folder it works in (``cwd``). The desktop app starts a chat in a spare folder and moves it into
the project later, in the same process, so the process id stays right where the folder a chat started in does not."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# The name Claude Code's own executable runs under, without its extension.
CLAUDE_EXECUTABLE = "claude"
# How far up the process tree the connect script looks for the Claude Code process it was started by: Claude Code may
# run it through a shell or two.
_ANCESTORS_SEARCHED = 8


def claude_config_folder() -> Path:
    """Claude Code's own settings folder: ``CLAUDE_CONFIG_DIR``, else ``~/.claude``."""
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def is_desktop_spare(folder: Path) -> bool:
    """Whether folder is one of the desktop app's spare folders (``<config>/spares/...``), which a chat starts in before
    the app moves it to its project. It is never a project: work done there is lost when the app reuses it."""
    spares = (claude_config_folder() / "spares").resolve()
    resolved = folder.resolve()
    return resolved == spares or spares in resolved.parents


class ClaudeChatProcess:
    """A running Claude Code chat process, known by its process id."""

    def __init__(self, pid: int) -> None:
        self.pid = pid

    @classmethod
    def from_header(cls, text: str | None) -> ClaudeChatProcess | None:
        """The process a request's header names; none when the header is missing or is not a process id."""
        value = (text or "").strip()
        return cls(int(value)) if value.isdigit() else None

    @classmethod
    def from_ancestors(cls, processes: _ProcessTree | None = None) -> ClaudeChatProcess | None:
        """The nearest process above this one that is a Claude Code chat: one Claude Code records in its sessions folder,
        or one running Claude Code's own executable before that record is written. The desktop app runs a chat's header
        helpers while the chat still waits in a spare folder, before the record exists; the server reads the record on
        every call, so a process named that early still leads to the chat's folder. None when no ancestor is one."""
        tree = processes or _ProcessTree()
        pid = os.getpid()
        for _ in range(_ANCESTORS_SEARCHED):
            pid = tree.parent_of(pid)
            if pid is None:
                return None
            if cls(pid).session_file.is_file() or tree.runs_claude(pid):
                return cls(pid)
        return None

    @classmethod
    def from_connection(cls, client_port: int | None) -> ClaudeChatProcess | None:
        """The chat process that opened a loopback connection itself, known by the port its own end of the connection
        uses. None when no port is given, or the process holding it is not one Claude Code records as a chat: a tool a
        chat started, such as the session board, connects on its own behalf, not the chat's."""
        owner = _ProcessTree().owner_of_port(client_port) if client_port else None
        if owner is None or not cls(owner).session_file.is_file():
            return None
        return cls(owner)

    @property
    def session_file(self) -> Path:
        """The file Claude Code keeps for this process while it runs."""
        config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
        return config / "sessions" / f"{self.pid}.json"

    @property
    def working_folder(self) -> Path | None:
        """The checkout holding the folder this process's session works in now; none when the process records no folder
        that is still there."""
        recorded = self._recorded("cwd")
        folder = Path(recorded) if recorded else None
        if folder is None or not folder.is_dir() or is_desktop_spare(folder):
            return None
        resolved = folder.resolve()
        return next((above for above in (resolved, *resolved.parents) if (above / ".git").exists()), resolved)

    @property
    def session_id(self) -> str:
        """The id of the session this process runs now, which names the chat's transcript; empty when it records none."""
        return self._recorded("sessionId")

    def _recorded(self, field: str) -> str:
        """One field of the session file; empty when the file is gone, unreadable, or does not hold it."""
        if not self.session_file.is_file():
            return ""
        try:
            value = json.loads(self.session_file.read_text(encoding="utf-8")).get(field)
        except (OSError, ValueError):
            return ""
        return value if isinstance(value, str) else ""


class _ProcessTree:
    """The parent of a running process, the executable it runs, and the process holding a loopback TCP port, read from
    the operating system."""

    def parent_of(self, pid: int) -> int | None:
        if pid == os.getpid():
            return os.getppid() or None
        if sys.platform == "win32":
            entry = self._windows_entry(pid)
            return (entry.th32ParentProcessID or None) if entry is not None else None
        text = self._posix_field(pid, "ppid=")
        return int(text) if text.isdigit() and int(text) > 0 else None

    def owner_of_port(self, port: int) -> int | None:
        """The process whose end of an IPv4 TCP connection uses port; none when no process holds it."""
        return self._windows_owner_of_port(port) if sys.platform == "win32" else self._posix_owner_of_port(port)

    def _posix_owner_of_port(self, port: int) -> int | None:
        # lsof lists both ends of a loopback connection; the client's end is the one whose own address ends in port.
        try:
            answer = subprocess.run(["lsof", "-nP", f"-iTCP:{port}", "-Fpn"], capture_output=True, text=True, check=False)
        except FileNotFoundError:
            return None
        pid = None
        for line in answer.stdout.splitlines():
            if line.startswith("p"):
                pid = int(line[1:])
            elif line.startswith("n") and line[1:].split("->")[0].endswith(f":{port}"):
                return pid
        return None

    def _windows_owner_of_port(self, port: int) -> int | None:
        import ctypes
        import socket
        from ctypes import wintypes

        class TcpRow(ctypes.Structure):
            _fields_ = [("state", wintypes.DWORD), ("local_address", wintypes.DWORD), ("local_port", wintypes.DWORD),
                        ("remote_address", wintypes.DWORD), ("remote_port", wintypes.DWORD), ("owning_pid", wintypes.DWORD)]

        table = self._windows_tcp_table()
        if table is None:
            return None
        count = ctypes.cast(table, ctypes.POINTER(wintypes.DWORD))[0]
        rows = ctypes.cast(ctypes.addressof(table) + ctypes.sizeof(wintypes.DWORD), ctypes.POINTER(TcpRow * count)).contents
        wanted = socket.htons(port)
        return next((row.owning_pid for row in rows if row.local_port & 0xFFFF == wanted), None)

    def _windows_tcp_table(self) -> object | None:
        """Every IPv4 TCP connection with the process that owns it (``TCP_TABLE_OWNER_PID_CONNECTIONS``); none when
        Windows will not give it. The table can grow between asking its size and reading it, so it is asked again."""
        import ctypes
        from ctypes import wintypes

        ipv4, connections_with_owner, buffer_too_small = 2, 4, 122
        size = wintypes.DWORD(0)
        get_table = ctypes.windll.iphlpapi.GetExtendedTcpTable
        get_table(None, ctypes.byref(size), False, ipv4, connections_with_owner, 0)
        for _ in range(3):
            table = ctypes.create_string_buffer(size.value)
            status = get_table(table, ctypes.byref(size), False, ipv4, connections_with_owner, 0)
            if status == 0:
                return table
            if status != buffer_too_small:
                return None
        return None

    def runs_claude(self, pid: int) -> bool:
        """Whether pid runs Claude Code's own executable, ``claude`` or ``claude.exe``."""
        return Path(self._executable_of(pid)).stem.lower() == CLAUDE_EXECUTABLE

    def _executable_of(self, pid: int) -> str:
        if sys.platform != "win32":
            return self._posix_field(pid, "comm=")
        entry = self._windows_entry(pid)
        return entry.szExeFile.decode(errors="replace") if entry is not None else ""

    def _posix_field(self, pid: int, field: str) -> str:
        answer = subprocess.run(["ps", "-o", field, "-p", str(pid)], capture_output=True, text=True, check=False)
        return answer.stdout.strip()

    def _windows_entry(self, pid: int) -> Any:
        import ctypes
        from ctypes import wintypes

        class ProcessEntry(ctypes.Structure):
            _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ProcessID", wintypes.DWORD),
                        ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", wintypes.DWORD),
                        ("cntThreads", wintypes.DWORD), ("th32ParentProcessID", wintypes.DWORD),
                        ("pcPriClassBase", ctypes.c_long), ("dwFlags", wintypes.DWORD), ("szExeFile", ctypes.c_char * 260)]

        every_process = 0x00000002
        kernel = ctypes.windll.kernel32
        kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        kernel.Process32First.argtypes = kernel.Process32Next.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessEntry)]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        snapshot = kernel.CreateToolhelp32Snapshot(every_process, 0)
        entry = ProcessEntry()
        entry.dwSize = ctypes.sizeof(ProcessEntry)
        try:
            found = kernel.Process32First(snapshot, ctypes.byref(entry))
            while found:
                if entry.th32ProcessID == pid:
                    return entry
                found = kernel.Process32Next(snapshot, ctypes.byref(entry))
            return None
        finally:
            kernel.CloseHandle(snapshot)
