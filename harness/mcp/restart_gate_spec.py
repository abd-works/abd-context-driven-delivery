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

from harness.mcp.restart_gate import RestartGate

# Long enough for the other thread to reach the gate before the holder lets go.
SETTLE_SECONDS = 0.2


def _hold(enter, events: list[str], name: str, seconds: float) -> threading.Thread:
    def run() -> None:
        with enter():
            events.append(f"{name} started")
            time.sleep(seconds)
            events.append(f"{name} ended")

    thread = threading.Thread(target=run)
    thread.start()
    return thread


with description("a restart gate") as self:
    with before.each:
        self.gate = RestartGate()
        self.events = []

    with context("with a tool call running"):
        with it("should start a restart only after the call ends"):
            call = _hold(self.gate.running_call, self.events, "call", SETTLE_SECONDS)
            time.sleep(SETTLE_SECONDS / 4)
            restarting = self.gate.restarting
            with restarting():
                self.events.append("restart started")
            call.join()
            expect(self.events).to(equal(["call started", "call ended", "restart started"]))

    with context("with a restart running"):
        with it("should start a tool call only after the restart ends"):
            restart = _hold(self.gate.restarting, self.events, "restart", SETTLE_SECONDS)
            time.sleep(SETTLE_SECONDS / 4)
            running_call = self.gate.running_call
            with running_call():
                self.events.append("call started")
            restart.join()
            expect(self.events).to(equal(["restart started", "restart ended", "call started"]))

    with context("with two tool calls"):
        with it("should run them at the same time"):
            first = _hold(self.gate.running_call, self.events, "first", SETTLE_SECONDS)
            time.sleep(SETTLE_SECONDS / 4)
            running_call = self.gate.running_call
            with running_call():
                self.events.append("second started")
            first.join()
            expect(self.events).to(equal(["first started", "second started", "first ended"]))
