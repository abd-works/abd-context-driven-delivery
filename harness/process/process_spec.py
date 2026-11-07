"""Specs for how the framework starts a process: a background server with no console, a hook command on a console."""
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import context, description, it

from harness.process.process import BackgroundStart, PythonInterpreter

_BREAKAWAY = 0x01000000


with description("a background start"):
    with context("that breaks away from the starter's job"):
        with it("should hide the window on Windows"):
            flags = BackgroundStart().creationflags
            expect(bool(flags & getattr(subprocess, "CREATE_NO_WINDOW", 0))).to(equal(sys.platform == "win32"))

        with it("should never detach, which would open a console on Windows"):
            expect(bool(BackgroundStart().creationflags & getattr(subprocess, "DETACHED_PROCESS", 0))).to(equal(False))

        with it("should break away on Windows"):
            expect(bool(BackgroundStart().creationflags & _BREAKAWAY)).to(equal(sys.platform == "win32"))

    with context("that starts inside the starter's job"):
        with it("should not break away"):
            expect(bool(BackgroundStart().inside_starters_job().creationflags & _BREAKAWAY)).to(equal(False))


with description("a Python interpreter"):
    with context("that is pythonw.exe"):
        with it("should run a hook command on the console Python beside it"):
            pythonw = Path(sys.executable).with_name("pythonw.exe")
            console = PythonInterpreter(pythonw).console
            expected = str(Path(sys.executable).with_name("python.exe")) if sys.platform == "win32" else str(pythonw)
            expect(console).to(equal(expected))
