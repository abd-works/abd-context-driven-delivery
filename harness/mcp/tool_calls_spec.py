"""Tool calls on worker threads: a slow call keeps running, is reported honestly, and is never started twice."""
import sys
import threading
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import logging
import time
from contextlib import contextmanager
from unittest.mock import patch

import anyio
import anyio._backends._asyncio  # noqa: F401 - the backend anyio.run loads, loaded with the module rather than by the first example
from expects import be_a, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.agent_tools.tool_call import ToolCall, ToolRequest
from harness.mcp import tool_calls
from harness.mcp.tool_calls import ThrottledReporter, _StillRunning, _ToolCalls

# Short enough that a held call outlives it; long enough that a released call finishes inside it.
SHORT_SECONDS = 0.02
LONG_SECONDS = 5


class HeldWork:
    """A tool's work that runs until the spec lets it finish, counting how often it was started."""

    def __init__(self, value: object = "written") -> None:
        self.released = threading.Event()
        self.finished = threading.Event()
        self.starts = 0
        self._value = value

    def __call__(self, _call: ToolCall, _reporter) -> object:
        self.starts += 1
        self.released.wait(LONG_SECONDS)
        self.finished.set()
        return self._value


class FailedWork:
    def __call__(self, _call: ToolCall, _reporter) -> object:
        raise ValueError("graph is corrupt")


async def _until_every_run_ended(calls: _ToolCalls) -> None:
    """Wait for every run whose caller was told it is still running to end, so the event loop does not close on a run
    and stop it."""
    with anyio.fail_after(LONG_SECONDS):
        while not all(running.has_ended for running in calls._promised.values()):
            await anyio.sleep(0.001)


@contextmanager
def _an_hour_later():
    """The clock the tool calls read, an hour on: long after any run that ended has ended."""
    with patch.object(tool_calls.time, "monotonic", lambda: _NOW + 3600):
        yield


_NOW = time.monotonic()


def _call(arguments: dict | None = None) -> ToolCall:
    return ToolCall.sent(arguments or {"paths": ["src"]}, Path("project"), ToolRequest(tool="validate.validate"))


class LoggedFailures(logging.Handler):
    """The failures the tool calls log, kept for the spec to read."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


with description("tool calls on worker threads") as self:
    with before.each:
        self.work = HeldWork()
        self.calls = _ToolCalls(self.work)

    with context("with a call that outlives its time limit"):
        with before.each:
            async def outlive_then_collect():
                self.first = await self.calls.run(_call(), SHORT_SECONDS, None)
                self.work.released.set()
                await anyio.to_thread.run_sync(self.work.finished.wait, LONG_SECONDS)
                self.again = await self.calls.run(_call(), LONG_SECONDS, None)

            anyio.run(outlive_then_collect)

        with it("should tell the caller the call is still running"):
            expect(self.first).to(be_a(_StillRunning))

        with it("should say so as data a client reads, naming the tool"):
            expect(self.first.structured["still_running"]["tool"]).to(equal(self.first.tool))

        # Claude Code shows an agent a result's structuredContent in place of its text, so the data carries the sentence.
        with it("should tell the caller how to get the result in the data too"):
            expect(self.first.structured["still_running"]["message"]).to(equal(self.first.message))

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
                self.joined = await self.calls.run(_call(), LONG_SECONDS, None)

            async def call_twice():
                await self.calls.run(_call(), SHORT_SECONDS, None)
                async with anyio.create_task_group() as group:
                    group.start_soon(join)
                    await anyio.sleep(SHORT_SECONDS)
                    self.work.released.set()

            anyio.run(call_twice)

        with it("should wait for the run already going"):
            expect(self.joined).to(equal("written"))

        with it("should not start the work a second time"):
            expect(self.work.starts).to(equal(1))

    # A read made after a change, such as the board read again once a format chip is pressed, answers from the change,
    # not from an identical read still running that began before it.
    with context("with an identical call made while the first is still within its time limit"):
        with it("should start the work again for it"):
            async def call_twice_at_once():
                async with anyio.create_task_group() as group:
                    group.start_soon(self.calls.run, _call(), LONG_SECONDS, None)
                    await anyio.sleep(SHORT_SECONDS)
                    group.start_soon(self.calls.run, _call(), LONG_SECONDS, None)
                    await anyio.sleep(SHORT_SECONDS)
                    self.work.released.set()

            anyio.run(call_twice_at_once)
            expect(self.work.starts).to(equal(2))

    # The dev lane's server, 2026-11-23: a render whose caller was told it was still running was asked for again ten
    # minutes later; its outcome had been forgotten, so the render started again and its caller heard "still running"
    # once more, on every ask, and never its result or its failure.
    with context("with a call that outlived its time limit, asked for again long after it ended"):
        with before.each:
            async def outlive_then_collect_late():
                self.first = await self.calls.run(_call(), SHORT_SECONDS, None)
                self.work.released.set()
                await anyio.to_thread.run_sync(self.work.finished.wait, LONG_SECONDS)
                await _until_every_run_ended(self.calls)
                with _an_hour_later():
                    self.again = await self.calls.run(_call(), LONG_SECONDS, None)

            anyio.run(outlive_then_collect_late)

        with it("should hand the result to the same call made again"):
            expect(self.again).to(equal("written"))

        with it("should not start the work again"):
            expect(self.work.starts).to(equal(1))

    with context("with a call that failed after its caller was told it is still running"):
        with it("should raise the failure to the same call made again"):
            failing = HeldWork(value=None)

            def fail_when_released(call: ToolCall, reporter) -> object:
                failing(call, reporter)
                raise ValueError("graph is corrupt")

            self.calls = _ToolCalls(fail_when_released)

            async def outlive_then_ask_again():
                await self.calls.run(_call(), SHORT_SECONDS, None)
                failing.released.set()
                await _until_every_run_ended(self.calls)
                with _an_hour_later():
                    await self.calls.run(_call(), LONG_SECONDS, None)

            expect(lambda: anyio.run(outlive_then_ask_again)).to(raise_error(ValueError, "graph is corrupt"))

    # A second identical call within the first's time limit runs again; the first's caller, told its call is still
    # running, then asks for the run it was told about, never for a third.
    with context("with the caller of the first of two identical runs asking again once told it is still running"):
        with before.each:
            async def ask_again_for_the_first():
                async with anyio.create_task_group() as group:
                    group.start_soon(self.calls.run, _call(), SHORT_SECONDS * 2, None)
                    await anyio.sleep(SHORT_SECONDS)
                    group.start_soon(self.calls.run, _call(), LONG_SECONDS, None)
                    await anyio.sleep(SHORT_SECONDS * 2)
                    group.start_soon(self.calls.run, _call(), LONG_SECONDS, None)
                    await anyio.sleep(SHORT_SECONDS)
                    self.work.released.set()

            anyio.run(ask_again_for_the_first)

        with it("should not start the work a third time"):
            expect(self.work.starts).to(equal(2))

    with context("with a different call made while the first is still running"):
        with it("should start the work for it"):
            async def call_two_paths():
                await self.calls.run(_call({"paths": ["src"]}), SHORT_SECONDS, None)
                await self.calls.run(_call({"paths": ["docs"]}), SHORT_SECONDS, None)
                self.work.released.set()
                await _until_every_run_ended(self.calls)

            anyio.run(call_two_paths)
            expect(self.work.starts).to(equal(2))

    with context("with a call that finishes within its time limit"):
        with before.each:
            self.work.released.set()

            async def call_twice_in_turn():
                self.first = await self.calls.run(_call(), LONG_SECONDS, None)
                self.second = await self.calls.run(_call(), LONG_SECONDS, None)

            anyio.run(call_twice_in_turn)

        with it("should answer with the work's value"):
            expect(self.first).to(equal("written"))

        with it("should run the work again for the next identical call"):
            expect(self.work.starts).to(equal(2))

    with context("with a call whose work fails"):
        with it("should raise the failure to the caller"):
            async def call_failing():
                await _ToolCalls(FailedWork()).run(_call(), LONG_SECONDS, None)

            expect(lambda: anyio.run(call_failing)).to(raise_error(ValueError, "graph is corrupt"))

    with context("with identical calls from two chats"):
        with it("should start the work for each chat"):
            async def call_from_two_chats():
                for chat in ("chat-a", "chat-b"):
                    arguments = {"paths": ["src"], "conversation_id": chat, "transcript_path": "transcript.jsonl"}
                    await self.calls.run(_call(arguments), SHORT_SECONDS, None)
                self.work.released.set()
                await _until_every_run_ended(self.calls)

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

            def fail_when_released(call: ToolCall, reporter) -> object:
                failing(call, reporter)
                raise ValueError("graph is corrupt")

            self.calls = _ToolCalls(fail_when_released)

            async def cancel_the_caller():
                with anyio.move_on_after(SHORT_SECONDS) as scope:
                    scope.cancel()
                    await self.calls.run(_call(), LONG_SECONDS, None)
                failing.released.set()
                with anyio.fail_after(LONG_SECONDS):
                    while not self.logged.messages:
                        await anyio.sleep(0.001)

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

