"""WorkerProcess: a Python module run in a process of its own for work that would hold the interpreter for minutes.

Every chat shares the cdd server's one interpreter, so work a chat's call starts that is minutes of CPU-bound Python,
such as a graph build or the routing of a large class diagram's arrows, runs in a worker process
(``call.request.answers_a_chat``). The worker reports its progress one line at a time on its stdout, which goes on to
``report_progress`` for the call that started it."""

from __future__ import annotations

import os
import subprocess
import sys
from typing import IO

from harness.agent_tools.progress import report_progress

# Windows' CREATE_NO_WINDOW: the worker opens no console window beside a windowless server.
_CREATE_NO_WINDOW = 0x08000000


class WorkerProcess:
    """The module a worker process runs (``python -m module``), started with this interpreter, this import path, and
    this folder, so it imports the same code the server runs."""

    def __init__(self, module: str) -> None:
        self.module = module

    def run(self, arguments: list[str], errors: IO[str]) -> int:
        """Run the module on arguments until it exits, passing each line it prints on to report_progress and writing
        its error output to errors; answers its exit code."""
        process = subprocess.Popen(
            [sys.executable, "-m", self.module, *arguments],
            cwd=os.getcwd(),
            env={**os.environ, "PYTHONPATH": os.pathsep.join(path for path in sys.path if path), "PYTHONIOENCODING": "utf-8"},
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=errors,
            encoding="utf-8",
            errors="replace",
            creationflags=_CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        assert process.stdout is not None
        for line in process.stdout:
            message = line.rstrip("\n")
            if message:
                report_progress(message)
        return process.wait()
