"""A process on this computer, named by its process id."""

from __future__ import annotations

import os
import sys

# The access right that lets Windows open a process only to ask about it.
_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
# The exit code Windows reports for a process that has not exited.
_STILL_ACTIVE = 259


class RunningProcess:
    """A process by its id, to ask whether it is still running. A hook server's lock file, a daemon's address file,
    and the instances script all name a process this way."""

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
            import ctypes

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
        try:
            os.kill(self.pid, 0)
        except PermissionError:
            return True
        except OSError:
            return False
        return True
