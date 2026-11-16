"""The examples the Keep A Lane's Server Running After Its Chat Ends story shares: a background start from inside a chat's
Windows job, which refuses to let its children break away, and WMI as a stub that creates nothing.

Scenarios: story_tests/register-and-install-toolsets/serve-cdd-code-in-lanes/keep-a-lanes-server-running-after-its-chat-ends/
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from harness.process.process import BackgroundStart, Wmi

# Seed: the cdd server a lane starts, the folder it runs in, and the environment it needs.
SERVER_COMMAND = ["pythonw.exe", "-m", "harness.mcp", "--port", "47801"]
SERVER_FOLDER = Path("C:/Users/dev/.cdd/dev/runtime")
SERVER_ENVIRONMENT = {"CDD_HOME": "C:/Users/dev/.cdd/dev", "PYTHONIOENCODING": "utf-8"}
# Seed: the process id WMI answers for the process it created.
CREATED_PID = 4242


class WmiStub(Wmi):
    """A stub of WMI's Win32_Process.Create: it creates nothing, keeps what it was asked, and answers CREATED_PID."""

    def __init__(self) -> None:
        self.created: list[tuple[str, str, dict[str, str]]] = []

    def create(self, command_line: str, folder: str, env: dict[str, str]) -> int:
        self.created.append((command_line, folder, env))
        return CREATED_PID


class StartInsideAJobRefusingBreakaway(BackgroundStart):
    """A background start from inside a chat's Windows job, which refuses CREATE_BREAKAWAY_FROM_JOB as Windows does:
    creating the process breaking away raises *PermissionError*."""

    def _start_breaking_away(self, command: list[str], cwd: str | Path, env: dict[str, str]) -> subprocess.Popen:
        raise PermissionError(5, "Access is denied")
