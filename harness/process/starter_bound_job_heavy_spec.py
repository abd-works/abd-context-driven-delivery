"""Specs for holding a started process to its starter's life. Heavy: a starter process starts a child, is killed, and
the child is watched."""
import subprocess
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_true, expect
from mamba import after, context, description, it

from harness.process.process import RunningProcess

# A starter that starts a long-lived child, takes it into its job when asked to, prints the child's id, and waits.
STARTER = """import subprocess, sys, time
from harness.process.starter_bound_job import StarterBoundJob
child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
if sys.argv[1] == "bound":
    StarterBoundJob().take_in(child)
print(child.pid, flush=True)
time.sleep(60)
"""
# How long Windows has to end the child once its starter is killed.
ENDED_SECONDS = 10


with description("a process its starter holds to its own life") as self:
    def child_of_killed_starter(self, hold: str) -> RunningProcess:
        starter = subprocess.Popen([sys.executable, "-c", STARTER, hold], cwd=_REPO_ROOT, stdout=subprocess.PIPE, text=True)
        self.child = RunningProcess(int(starter.stdout.readline()))
        starter.kill()
        starter.wait()
        return self.child

    def ended(self, process: RunningProcess) -> bool:
        deadline = time.monotonic() + ENDED_SECONDS
        while process.alive and time.monotonic() < deadline:
            time.sleep(0.1)
        return not process.alive

    with after.each:
        if self.child.alive:
            subprocess.run(["taskkill", "/F", "/PID", str(self.child.pid)], capture_output=True, check=False)

    with context("whose starter is killed"):
        with it("should end with it"):
            expect(self.ended(self.child_of_killed_starter("bound"))).to(be_true)

    with context("that its starter did not take in, the starter killed"):
        with it("should go on running"):
            expect(self.child_of_killed_starter("plain").alive).to(be_true)
