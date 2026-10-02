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


def detached_creationflags() -> int:
    if sys.platform != "win32":
        return 0
    flags = 0
    flags |= getattr(subprocess, "DETACHED_PROCESS", 0)
    flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    flags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return flags
