"""Subprocess helpers for hook and daemon processes — no console windows on Windows."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def hook_python_executable(python: str | None = None) -> str:
    """Return pythonw.exe on Windows so Cursor hook CLIs do not open consoles."""
    exe = Path(python or sys.executable)
    if sys.platform == "win32":
        pythonw = exe.with_name("pythonw.exe")
        if pythonw.is_file():
            return str(pythonw)
    return str(exe)


_CREATE_BREAKAWAY_FROM_JOB = 0x01000000


def detached_creationflags() -> int:
    """Flags that keep a daemon alive without opening a console window.

    DETACHED_PROCESS makes Windows ignore CREATE_NO_WINDOW, so a console
    subsystem child allocates a visible console. Break away from the parent
    job instead, and hide the window.
    """
    if sys.platform != "win32":
        return 0
    flags = 0
    flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    flags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
    flags |= _CREATE_BREAKAWAY_FROM_JOB
    return flags


def hidden_process_startupinfo() -> subprocess.STARTUPINFO | None:
    if sys.platform != "win32":
        return None
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = subprocess.SW_HIDE
    return info
