"""A process this one may stop, named by its process id. The hook daemon and the cdd server both stop an older copy of
themselves this way."""

from __future__ import annotations

import os
import signal
import time

from harness.hooks.running_process import RunningProcess

# How long a stop waits between looks at whether the process has ended.
_POLL_SECONDS = 0.05


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
