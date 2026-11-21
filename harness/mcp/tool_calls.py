"""Tool calls running on worker threads, kept by what was asked, so a slow call is never started twice.

A worker thread cannot be stopped. A call that outlives its time limit therefore keeps running: its caller hears that
it is still running, an identical call made meanwhile waits for the same run instead of starting a second one, and the
result waits for the next identical call to collect it."""
from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass

import anyio

from harness.agent_tools.tool_call import ToolCall
from harness.installation.data_class import SentValue

logger = logging.getLogger(__name__)
# How long a result is kept for the caller who was told its call was still running; after that it is stale.
_UNCOLLECTED_RESULT_SECONDS = 600

Reporter = Callable[[str], None]
# What answers a call on its worker thread, with a reporter for its progress: the value its operation returns, which the
# server sends as data (a string as it is, anything else as JSON).
ToolWork = Callable[[ToolCall, Reporter], SentValue]
# The fewest seconds between two progress reports a caller hears; the reports in between are dropped.
_REPORT_SECONDS = 0.25

class ThrottledReporter:
    """Passes a tool's progress reports on to reporter, at most one each quarter second; the reports in between are
    dropped. A graph build reports each node it checks, and every report a caller hears is a message the event loop
    sends, so passing on every one would keep the loop from answering anyone else."""

    def __init__(self, reporter: Reporter, seconds: float = _REPORT_SECONDS) -> None:
        self._reporter = reporter
        self._seconds = seconds
        self._last = -seconds

    def __call__(self, message: str) -> None:
        now = time.monotonic()
        if now - self._last < self._seconds:
            return
        self._last = now
        self._reporter(message)


class ToolCallStopped(Exception):
    """The server stopped while a tool call was still running on its worker thread."""

    def __init__(self, tool: str) -> None:
        super().__init__(f"{tool} was stopped before it finished, because the server stopped")
        self.tool = tool


@dataclass(frozen=True)
class _StillRunning:
    """The answer to a caller whose call outlived the seconds it waited."""

    tool: str
    seconds: float

    @property
    def message(self) -> str:
        tool = self.tool
        return (
            f"{tool} is still running after {self.seconds:g} seconds; it was not started again. Call {tool} "
            "again with the same arguments to get its result: an identical call waits for the run already going "
            "instead of starting another."
        )

    @property
    def structured(self) -> dict[str, dict[str, object]]:
        """The same answer as data, beside the message: a client tells a call still running by this field, never by
        reading the message's words, which an agent reads and which may be reworded."""
        return {"still_running": {"tool": self.tool, "seconds": self.seconds}}


class _RunningCall:
    """One run of a tool on a worker thread, and its outcome once it ends: the value the run returned, or the failure it
    raised, which a waiting caller hears raised as it was. A run the server stopped before it ended failed with
    *ToolCallStopped*."""

    def __init__(self, call: ToolCall, reporter: Reporter | None) -> None:
        self.call = call
        self.callers_waiting = 0
        self.told_still_running = False
        self._ended = anyio.Event()
        self._ended_at = 0.0
        self._reporter = reporter
        self._task: asyncio.Task | None = None

    def report(self, message: str) -> None:
        """Pass a progress report to the caller who started the run, while that caller still waits for it."""
        reporter = self._reporter
        if reporter is not None:
            reporter(message)

    def start(self, work: ToolWork, on_end: Callable[[_RunningCall], None]) -> None:
        """Run work on a worker thread; on_end hears when the run is over. The run is its own task, so a caller that
        stops waiting does not cancel it."""
        self._task = asyncio.get_running_loop().create_task(anyio.to_thread.run_sync(work, self.call, self.report))
        self._task.add_done_callback(lambda _: on_end(self))

    def end(self) -> None:
        """The run is over, with whatever outcome it had; every caller waiting for it hears it now."""
        self._ended_at = time.monotonic()
        self._ended.set()

    @property
    def _failure(self) -> BaseException | None:
        """What the run raised; none when it returned."""
        task = self._task
        if task is None or task.cancelled():
            return ToolCallStopped(self.call.request.tool)
        return task.exception()

    def log_unheard_failure(self) -> None:
        """Log the run's failure when no caller is left to hear it, so it is never lost."""
        if self._failure is not None:
            logger.error("MCP tool %s failed after its caller stopped waiting", self.call.request.tool, exc_info=self._failure)

    async def answer(self, seconds: float) -> SentValue | _StillRunning:
        """The outcome, when the run ends within seconds; otherwise ``_StillRunning``."""
        self.callers_waiting += 1
        try:
            with anyio.move_on_after(seconds):
                await self._ended.wait()
        finally:
            self.callers_waiting -= 1
        if not self._ended.is_set():
            self._reporter = None
            self.told_still_running = True
            return _StillRunning(self.call.request.tool, seconds)
        failure = self._failure
        if failure is not None:
            raise failure
        return self._task.result()

    @property
    def is_stale(self) -> bool:
        return time.monotonic() - self._ended_at > _UNCOLLECTED_RESULT_SECONDS


class _ToolCalls:
    """Every tool call this server is running on a worker thread, by call identity, and the results kept for callers
    who were told their call was still running."""

    def __init__(self, work: ToolWork) -> None:
        # What answers a call on its worker thread, with a reporter for its progress.
        self._work = work
        self._running: dict[str, _RunningCall] = {}
        self._uncollected: dict[str, _RunningCall] = {}

    async def run(self, call: ToolCall, seconds: float, reporter: Reporter | None) -> SentValue | _StillRunning:
        """The work's value for call, run on a worker thread with reporter for its progress, waiting up to seconds. An
        identical call already running is joined, and a kept result is collected, instead of starting the work again."""
        self._forget_stale_results()
        running = self._uncollected.pop(call.identity, None) or self._running.get(call.identity)
        if running is None:
            running = self._start(call, reporter)
        return await running.answer(seconds)

    def _start(self, call: ToolCall, reporter: Reporter | None) -> _RunningCall:
        running = _RunningCall(call, reporter)
        self._running[call.identity] = running
        running.start(self._work, self._end)
        return running

    def _end(self, running: _RunningCall) -> None:
        identity = running.call.identity
        self._running.pop(identity, None)
        running.end()
        if running.callers_waiting:
            return
        running.log_unheard_failure()
        if running.told_still_running:
            # Nobody is waiting, but a caller was promised this result.
            self._uncollected[identity] = running

    def _forget_stale_results(self) -> None:
        for identity, running in list(self._uncollected.items()):
            if running.is_stale:
                del self._uncollected[identity]
