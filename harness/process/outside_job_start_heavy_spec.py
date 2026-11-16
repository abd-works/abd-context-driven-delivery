"""Heavy: a real background start through WMI's Win32_Process.Create, from a starter inside a Windows job that kills
every process it holds when it closes, as a chat's does when the chat ends. The starter refuses breakaway the way a
chat's job does (*StartInsideAJobRefusingBreakaway*), so the start goes through WMI, and the started process outlives
the job and the starter it killed. It starts a trivial Python that prints a variable of its environment and its folder,
then ends on its own. Windows only.

A job made here does not make breakaway raise: a breakaway child of a nested job is created, and stays in the job. So
the refusal is the example's, and everything after it, WMI, the launcher, the log, and the job, is real.

Story: story_tests/register-and-install-toolsets/serve-cdd-code-in-lanes/keep-a-lanes-server-running-after-its-chat-ends/
"""
import ctypes
import json
import os
import subprocess
import sys
import tempfile
import time
from ctypes import wintypes
from pathlib import Path

from expects import be_true, contain, equal, expect, raise_error
from mamba import before, description, it

from harness.process.process import OutsideJobStartFailed, RunningProcess, Wmi

# A job whose processes all end when its last handle closes, and which lets none of them break away.
_KILL_ON_JOB_CLOSE = 0x2000
_EXTENDED_LIMIT_INFORMATION = 9
# How long the started process runs, and how long the spec waits on it.
_RUN_SECONDS = 4
_WAIT_SECONDS = 15
_PROBE = "started-outside-the-job"
# The starter: inside the job, it starts the command in the background, prints the started id, and waits to be killed.
_STARTER = """
import json, sys
from harness.process.examples.outside_job_examples import StartInsideAJobRefusingBreakaway
log_path, folder, command = json.loads(sys.stdin.readline())
with open(log_path, "a", encoding="utf-8") as log:
    print(StartInsideAJobRefusingBreakaway(log).run(command, folder, dict(__import__("os").environ, CDD_PROBE="%s")).pid, flush=True)
sys.stdin.readline()
""" % _PROBE


class _IoCounters(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in ("reads", "writes", "others", "read_bytes", "written_bytes", "other_bytes")]


class _BasicLimits(ctypes.Structure):
    _fields_ = [
        ("process_time", ctypes.c_longlong), ("job_time", ctypes.c_longlong), ("flags", wintypes.DWORD),
        ("minimum_working_set", ctypes.c_size_t), ("maximum_working_set", ctypes.c_size_t), ("process_limit", wintypes.DWORD),
        ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD), ("scheduling", wintypes.DWORD),
    ]


class _ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("basic", _BasicLimits), ("io", _IoCounters), ("process_memory", ctypes.c_size_t), ("job_memory", ctypes.c_size_t),
        ("peak_process_memory", ctypes.c_size_t), ("peak_job_memory", ctypes.c_size_t),
    ]


class ChatJob:
    """A Windows job like a chat's: closing it kills every process it holds."""

    def __init__(self) -> None:
        kernel = ctypes.windll.kernel32
        kernel.CreateJobObjectW.restype = wintypes.HANDLE
        self.handle = kernel.CreateJobObjectW(None, None)
        limits = _ExtendedLimits()
        limits.basic.flags = _KILL_ON_JOB_CLOSE
        kernel.SetInformationJobObject(wintypes.HANDLE(self.handle), _EXTENDED_LIMIT_INFORMATION, ctypes.byref(limits), ctypes.sizeof(limits))

    def hold(self, process: subprocess.Popen) -> None:
        ctypes.windll.kernel32.AssignProcessToJobObject(wintypes.HANDLE(self.handle), wintypes.HANDLE(int(process._handle)))

    def close(self) -> None:
        ctypes.windll.kernel32.CloseHandle(wintypes.HANDLE(self.handle))


def _wait_for(done, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while not done():
        if time.monotonic() > deadline:
            return False
        time.sleep(0.1)
    return True


with description("a background start from a chat's Windows job that refuses breakaway") as self:
    with before.all:
        self.windows = sys.platform == "win32"
        if self.windows:
            self.folder = Path(tempfile.mkdtemp(prefix="outside-job-"))
            self.log_path = self.folder / "server.log"
            command = [sys.executable, "-c", f"import os,time; print(os.environ['CDD_PROBE'], os.getcwd(), flush=True); time.sleep({_RUN_SECONDS})"]
            self.job = ChatJob()
            self.starter = subprocess.Popen([sys.executable, "-c", _STARTER], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            self.job.hold(self.starter)
            self.starter.stdin.write(json.dumps([str(self.log_path), str(self.folder), command]) + "\n")
            self.starter.stdin.flush()
            self.started = RunningProcess(int(self.starter.stdout.readline()))
            self.job.close()
            self.starter.wait(_WAIT_SECONDS)

    with it("should keep the started process running after the job killed its starter"):
        expect(not self.windows or (self.starter.returncode is not None and self.started.alive)).to(be_true)

    with it("should append its output, from its own environment and folder, to the log"):
        if self.windows:
            _wait_for(lambda: _PROBE in self.log_path.read_text(encoding="utf-8"), _WAIT_SECONDS)
            expect(self.log_path.read_text(encoding="utf-8")).to(contain(f"{_PROBE} {self.folder}"))

    with it("should say in the log that breakaway was refused"):
        if self.windows:
            expect(self.log_path.read_text(encoding="utf-8")).to(contain("breakaway refused; starting outside the caller's job through WMI"))

    with it("should end when the command ends, leaving nothing running"):
        expect(not self.windows or _wait_for(lambda: not self.started.alive, _WAIT_SECONDS)).to(equal(True))


with description("WMI asked to create a process"):
    with it("should refuse with OutsideJobStartFailed when the folder it would run in is not there"):
        if sys.platform == "win32":
            missing = str(Path(tempfile.mkdtemp(prefix="outside-job-")) / "not-there")
            command_line = subprocess.list2cmdline([sys.executable, "-c", "pass"])
            expect(lambda: Wmi().create(command_line, missing, dict(os.environ))).to(raise_error(OutsideJobStartFailed))
