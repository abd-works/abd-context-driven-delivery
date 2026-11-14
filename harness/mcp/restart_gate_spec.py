"""BDD spec — the gate that keeps tool calls and a cdd restart apart."""
import sys
import threading
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, description, context, it

from harness.mcp.restart_gate import _RestartGate

# How long the holder stays inside the gate: long enough for this thread, which goes to the gate as soon as the holder
# is inside, to reach it before the holder lets go.
HOLD_SECONDS = 0.05


def _hold(enter, events: list[str], name: str, seconds: float) -> threading.Thread:
    """Go through the gate on another thread and stay inside for seconds; answers once that thread is inside."""
    inside = threading.Event()

    def run() -> None:
        with enter():
            events.append(f"{name} started")
            inside.set()
            time.sleep(seconds)
            events.append(f"{name} ended")

    thread = threading.Thread(target=run)
    thread.start()
    inside.wait(5)
    return thread


with description("a restart gate") as self:
    with before.each:
        self.gate = _RestartGate()
        self.events = []

    with context("with a tool call running"):
        with it("should start a restart only after the call ends"):
            call = _hold(self.gate.running_call, self.events, "call", HOLD_SECONDS)
            restarting = self.gate.restarting
            with restarting():
                self.events.append("restart started")
            call.join()
            expect(self.events).to(equal(["call started", "call ended", "restart started"]))

    with context("with a restart running"):
        with it("should start a tool call only after the restart ends"):
            restart = _hold(self.gate.restarting, self.events, "restart", HOLD_SECONDS)
            running_call = self.gate.running_call
            with running_call():
                self.events.append("call started")
            restart.join()
            expect(self.events).to(equal(["restart started", "restart ended", "call started"]))

    with context("with two tool calls"):
        with it("should run them at the same time"):
            first = _hold(self.gate.running_call, self.events, "first", HOLD_SECONDS)
            running_call = self.gate.running_call
            with running_call():
                self.events.append("second started")
            first.join()
            expect(self.events).to(equal(["first started", "second started", "first ended"]))
