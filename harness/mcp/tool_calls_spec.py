"""Tool calls on worker threads: a slow call keeps running, is reported honestly, and is never started twice."""
import sys
import threading
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import logging

import anyio
from expects import be_a, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.agent_tools.tool_call import ToolCall
from harness.mcp.tool_calls import ThrottledReporter, _StillRunning, _ToolCalls, answering_a_chat, is_answering_a_chat

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


def _call(arguments: dict | None = None) -> ToolCall:
    return ToolCall.sent(arguments or {"paths": ["src"]}, Path("project"), tool="validate.validate")


class LoggedFailures(logging.Handler):
    """The failures the tool calls log, kept for the spec to read."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


with description("tool calls on worker threads") as self:
    with before.each:
        self.calls = _ToolCalls()
        self.work = HeldWork()

    with context("with a call that outlives its time limit"):
        with before.each:
            async def outlive_then_collect():
                self.first = await self.calls.run(_call(), SHORT_SECONDS, self.work, None)
                self.work.released.set()
                await anyio.to_thread.run_sync(self.work.finished.wait, LONG_SECONDS)
                self.again = await self.calls.run(_call(), LONG_SECONDS, self.work, None)

            anyio.run(outlive_then_collect)

        with it("should tell the caller the call is still running"):
            expect(self.first).to(be_a(_StillRunning))

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
                self.joined = await self.calls.run(_call(), LONG_SECONDS, self.work, None)

            async def call_twice():
                await self.calls.run(_call(), SHORT_SECONDS, self.work, None)
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
                await self.calls.run(_call({"paths": ["src"]}), SHORT_SECONDS, self.work, None)
                await self.calls.run(_call({"paths": ["docs"]}), SHORT_SECONDS, self.work, None)
                self.work.released.set()
                # Let both runs end before the event loop closes, which would stop them.
                await anyio.sleep(SHORT_SECONDS * 4)

            anyio.run(call_two_paths)
            expect(self.work.starts).to(equal(2))

    with context("with a call that finishes within its time limit"):
        with before.each:
            self.work.released.set()

            async def call_twice_in_turn():
                self.first = await self.calls.run(_call(), LONG_SECONDS, self.work, None)
                self.second = await self.calls.run(_call(), LONG_SECONDS, self.work, None)

            anyio.run(call_twice_in_turn)

        with it("should answer with the work's value"):
            expect(self.first).to(equal("written"))

        with it("should run the work again for the next identical call"):
            expect(self.work.starts).to(equal(2))

    with context("with a call whose work fails"):
        with it("should raise the failure to the caller"):
            async def call_failing():
                await self.calls.run(_call(), LONG_SECONDS, FailedWork(), None)

            expect(lambda: anyio.run(call_failing)).to(raise_error(ValueError, "graph is corrupt"))

    with context("with identical calls from two chats"):
        with it("should start the work for each chat"):
            async def call_from_two_chats():
                for chat in ("chat-a", "chat-b"):
                    arguments = {"paths": ["src"], "conversation_id": chat, "transcript_path": "transcript.jsonl"}
                    await self.calls.run(_call(arguments), SHORT_SECONDS, self.work, None)
                self.work.released.set()
                await anyio.sleep(SHORT_SECONDS * 4)

            anyio.run(call_from_two_chats)
            expect(self.work.starts).to(equal(2))

    with context("with a call whose caller stopped waiting before it failed"):
        with before.each:
            self.logged = LoggedFailures()
            logging.getLogger("harness.mcp.tool_calls").addHandler(self.logged)

        with after.each:
            logging.getLogger("harness.mcp.tool_calls").removeHandler(self.logged)

        with it("should log the failure nobody heard"):
            failing = HeldWork(value=None)

            def fail_when_released(reporter) -> object:
                failing(reporter)
                raise ValueError("graph is corrupt")

            async def cancel_the_caller():
                with anyio.move_on_after(SHORT_SECONDS) as scope:
                    scope.cancel()
                    await self.calls.run(_call(), LONG_SECONDS, fail_when_released, None)
                failing.released.set()
                await anyio.sleep(SHORT_SECONDS * 4)

            anyio.run(cancel_the_caller)
            expect(self.logged.messages).to(contain("MCP tool validate.validate failed after its caller stopped waiting"))


with description("a tool's progress reports passed on to its caller"):
    with before.each:
        self.heard: list[str] = []
        self.reporter = ThrottledReporter(self.heard.append, seconds=60)

    with context("that come faster than a caller is told them"):
        with before.each:
            for index in range(1000):
                self.reporter(f"node {index}")

        with it("should pass on the first"):
            expect(self.heard).to(equal(["node 0"]))

    with context("that come further apart than a caller is told them"):
        with before.each:
            spaced = ThrottledReporter(self.heard.append, seconds=0)
            spaced("reading stories")
            spaced("checking rules")

        with it("should pass on each"):
            expect(self.heard).to(equal(["reading stories", "checking rules"]))


with description("code a chat's call runs"):
    with it("should know it answers a chat"):
        with answering_a_chat():
            expect(is_answering_a_chat()).to(equal(True))

    with it("should know nothing of a chat once the call is answered"):
        with answering_a_chat():
            pass
        expect(is_answering_a_chat()).to(equal(False))
