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

# How far up the process tree the connect script looks for the Claude Code process it was started by: Claude Code may
# run it through a shell or two.
_ANCESTORS_SEARCHED = 8


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
    def from_ancestors(cls) -> ClaudeChatProcess | None:
        """The nearest process above this one that Claude Code records as a chat; none when no ancestor is one."""
        pid = os.getpid()
        for _ in range(_ANCESTORS_SEARCHED):
            pid = _ProcessTree().parent_of(pid)
            if pid is None:
                return None
            if cls(pid).session_file.is_file():
                return cls(pid)
        return None

    @property
    def session_file(self) -> Path:
        """The file Claude Code keeps for this process while it runs."""
        config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
        return config / "sessions" / f"{self.pid}.json"

    @property
    def working_folder(self) -> Path | None:
        """The checkout holding the folder this process's session works in now; none when the process records no folder
        that is still there."""
        folder = self._recorded_folder()
        if folder is None or not folder.is_dir():
            return None
        resolved = folder.resolve()
        return next((above for above in (resolved, *resolved.parents) if (above / ".git").exists()), resolved)

    def _recorded_folder(self) -> Path | None:
        if not self.session_file.is_file():
            return None
        try:
            recorded = json.loads(self.session_file.read_text(encoding="utf-8")).get("cwd")
        except (OSError, ValueError):
            return None
        return Path(recorded) if isinstance(recorded, str) and recorded else None


class _ProcessTree:
    """The parent of a running process, read from the operating system."""

    def parent_of(self, pid: int) -> int | None:
        if pid == os.getpid():
            return os.getppid() or None
        return self._windows_parent(pid) if sys.platform == "win32" else self._posix_parent(pid)

    def _posix_parent(self, pid: int) -> int | None:
        answer = subprocess.run(["ps", "-o", "ppid=", "-p", str(pid)], capture_output=True, text=True, check=False)
        text = answer.stdout.strip()
        return int(text) if text.isdigit() and int(text) > 0 else None

    def _windows_parent(self, pid: int) -> int | None:
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
                    return entry.th32ParentProcessID or None
                found = kernel.Process32Next(snapshot, ctypes.byref(entry))
            return None
        finally:
            kernel.CloseHandle(snapshot)
