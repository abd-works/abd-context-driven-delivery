"""A Windows job object its starter keeps open, so that what the starter starts ends when the starter does."""
from __future__ import annotations

import ctypes
import subprocess
import sys

# SetInformationJobObject's JobObjectExtendedLimitInformation.
_EXTENDED_LIMIT_INFORMATION = 9
# Windows ends every process in the job when the job's last handle closes, which the starter's end does.
_KILL_ON_JOB_CLOSE = 0x2000
# A process in the job may still start one outside it, as a background server's start asks for (*BackgroundStart*).
_BREAKAWAY_OK = 0x0800


class _BasicLimits(ctypes.Structure):
    """JOBOBJECT_BASIC_LIMIT_INFORMATION."""

    _fields_ = [
        ("per_process_user_time_limit", ctypes.c_int64),
        ("per_job_user_time_limit", ctypes.c_int64),
        ("limit_flags", ctypes.c_uint32),
        ("minimum_working_set_size", ctypes.c_size_t),
        ("maximum_working_set_size", ctypes.c_size_t),
        ("active_process_limit", ctypes.c_uint32),
        ("affinity", ctypes.c_size_t),
        ("priority_class", ctypes.c_uint32),
        ("scheduling_class", ctypes.c_uint32),
    ]


class _ExtendedLimits(ctypes.Structure):
    """JOBOBJECT_EXTENDED_LIMIT_INFORMATION: the basic limits, six input and output counters, and four memory sizes."""

    _fields_ = [
        ("basic", _BasicLimits),
        ("io_counters", ctypes.c_uint64 * 6),
        ("process_memory_limit", ctypes.c_size_t),
        ("job_memory_limit", ctypes.c_size_t),
        ("peak_process_memory_used", ctypes.c_size_t),
        ("peak_job_memory_used", ctypes.c_size_t),
    ]


class JobNotMade(Exception):
    """Windows refused the job object, or refused to put a process in it."""

    def __init__(self, step: str, pid: int = 0) -> None:
        super().__init__(f"Windows refused to {step}" + (f" for process {pid}" if pid else "") + f": {ctypes.WinError(ctypes.get_last_error())}")
        self.step = step
        self.pid = pid


class StarterBoundJob:
    """The processes a starter holds to its own life. Each process it takes in, and every process those start, is
    ended by Windows when the starter ends, however it ends: stopped from a chat, its console closed, or killed. A
    plain child process outlives its starter, and goes on working in a folder the next starter believes is free.
    Outside Windows it holds nothing, and a child is left as the system leaves it."""

    def __init__(self) -> None:
        self._handle = self._made() if sys.platform == "win32" else None

    def take_in(self, process: subprocess.Popen) -> None:
        """Hold process, and what it starts from now on, to this starter's life."""
        if self._handle is None:
            return
        if not self._kernel.AssignProcessToJobObject(self._handle, ctypes.c_void_p(int(process._handle))):
            raise JobNotMade("put a process in the job", process.pid)

    @property
    def _kernel(self) -> ctypes.WinDLL:
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateJobObjectW.restype = ctypes.c_void_p
        kernel.SetInformationJobObject.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
        kernel.AssignProcessToJobObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        return kernel

    def _made(self) -> int:
        handle = self._kernel.CreateJobObjectW(None, None)
        if not handle:
            raise JobNotMade("make a job object")
        limits = _ExtendedLimits()
        limits.basic.limit_flags = _KILL_ON_JOB_CLOSE | _BREAKAWAY_OK
        if not self._kernel.SetInformationJobObject(handle, _EXTENDED_LIMIT_INFORMATION, ctypes.byref(limits), ctypes.sizeof(limits)):
            raise JobNotMade("set the job to end with its starter")
        return handle
