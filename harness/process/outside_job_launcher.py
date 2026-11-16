"""What a background start outside the caller's Windows job runs, once WMI has created it with the command's folder and
environment: the command, with its output and errors appended to the log, waited for, so this process lives exactly as
long as the command does. It runs as a script with no package on its path, so it imports only the standard library.

Usage: ``pythonw outside_job_launcher.py LOG COMMAND...``
"""
from __future__ import annotations

import subprocess
import sys

# The command opens no console window and gets a process group of its own, as every background start gives it.
_WINDOWLESS = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)


def run_with_log(log_path: str, command: list[str]) -> int:
    """Run command, appending its output and errors to log_path, and answer its exit code."""
    with open(log_path, "a", encoding="utf-8") as log:
        return subprocess.call(command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, creationflags=_WINDOWLESS)


if __name__ == "__main__":
    sys.exit(run_with_log(sys.argv[1], sys.argv[2:]))
