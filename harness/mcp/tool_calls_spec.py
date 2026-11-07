"""Tool calls on worker threads: a slow call keeps running, is reported honestly, and is never started twice."""
import sys
import threading
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import anyio
from expects import be_a, contain, equal, expect, raise_error
from mamba import before, context, description, it

from harness.mcp.tool_calls import StillRunning, ToolCalls, ToolRequest

# Short enough that a held call outlives it; long enough that a released call finishes inside it.
SHORT_SECONDS = 0.05
LONG_SECONDS = 5


class HeldWork:
    """A tool's work that runs until the spec lets it finish, counting how often it was started."""

    def __init__(self, value: object = "written") -> None:
        self.released = threading.Event()
        self.finished = threading.Event()
        self.starts = 0
        self._value = value

    def __call__(self, _reporter) -> object:
        self.starts += 1
        self.released.wait(LONG_SECONDS)
        self.finished.set()
        return self._value


class FailedWork:
    def __call__(self, _reporter) -> object:
        raise ValueError("graph is corrupt")


def _request(seconds: float, arguments: dict | None = None) -> ToolRequest:
    return ToolRequest("validate.validate", Path("project"), arguments or {"paths": ["src"]}, seconds)


with description("tool calls on worker threads") as self:
    with before.each:
        self.calls = ToolCalls()
        self.work = HeldWork()

    with context("with a call that outlives its time limit"):
        with before.each:
            async def outlive_then_collect():
                self.first = await self.calls.run(_request(SHORT_SECONDS), self.work, None)
                self.work.released.set()
                await anyio.to_thread.run_sync(self.work.finished.wait, LONG_SECONDS)
                self.again = await self.calls.run(_request(LONG_SECONDS), self.work, None)

            anyio.run(outlive_then_collect)

        with it("should tell the caller the call is still running"):
            expect(self.first).to(be_a(StillRunning))

        with it("should tell the caller how to get the result"):
            expect(self.first.message).to(contain("Call validate.validate again with the same arguments"))

        with it("should keep running the work to the end"):
            expect(self.work.finished.is_set()).to(equal(True))

        with it("should hand the result to the same call made again"):
            expect(self.again).to(equal("written"))

        with it("should not start the work again"):
            expect(self.work.starts).to(equal(1))

    with context("with an identical call made while the first is still running"):
        with before.each:
            async def join():
                self.joined = await self.calls.run(_request(LONG_SECONDS), self.work, None)

            async def call_twice():
                await self.calls.run(_request(SHORT_SECONDS), self.work, None)
                async with anyio.create_task_group() as group:
                    group.start_soon(join)
                    await anyio.sleep(SHORT_SECONDS)
                    self.work.released.set()

            anyio.run(call_twice)

        with it("should wait for the run already going"):
            expect(self.joined).to(equal("written"))

        with it("should not start the work a second time"):
            expect(self.work.starts).to(equal(1))

    with context("with a different call made while the first is still running"):
        with it("should start the work for it"):
            async def call_two_paths():
                await self.calls.run(_request(SHORT_SECONDS, {"paths": ["src"]}), self.work, None)
                await self.calls.run(_request(SHORT_SECONDS, {"paths": ["docs"]}), self.work, None)
                self.work.released.set()
                # Let both runs end before the event loop closes, which would stop them.
                await anyio.sleep(SHORT_SECONDS * 4)

            anyio.run(call_two_paths)
            expect(self.work.starts).to(equal(2))

    with context("with a call that finishes within its time limit"):
        with before.each:
            self.work.released.set()

            async def call_twice_in_turn():
                self.first = await self.calls.run(_request(LONG_SECONDS), self.work, None)
                self.second = await self.calls.run(_request(LONG_SECONDS), self.work, None)

            anyio.run(call_twice_in_turn)

        with it("should answer with the work's value"):
            expect(self.first).to(equal("written"))

        with it("should run the work again for the next identical call"):
            expect(self.work.starts).to(equal(2))

    with context("with a call whose work fails"):
        with it("should raise the failure to the caller"):
            async def call_failing():
                await self.calls.run(_request(LONG_SECONDS), FailedWork(), None)

            expect(lambda: anyio.run(call_failing)).to(raise_error(ValueError, "graph is corrupt"))
