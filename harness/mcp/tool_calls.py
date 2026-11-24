"""Tool calls running on worker threads, kept by what was asked, so a slow call is never started twice.

A worker thread cannot be stopped. A call that outlives its time limit therefore keeps running: its caller hears that
it is still running, an identical call made after that waits for the same run instead of starting a second one, and the
outcome, its value or its failure, waits for the next identical call to collect it, however long that call is in coming.
An identical call made while the first is still within its time limit runs again, so it answers from anything that
changed after the first began."""
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
        reading the message's words, which an agent reads and which may be reworded. The data carries the message too,
        since a client such as Claude Code shows an agent the data in place of the text."""
        return {"still_running": {"tool": self.tool, "seconds": self.seconds, "message": self.message}}


class _RunningCall:
    """One run of a tool on a worker thread, and its outcome once it ends: the value the run returned, or the failure it
    raised, which a waiting caller hears raised as it was. A run the server stopped before it ended failed with
    *ToolCallStopped*."""

    def __init__(self, call: ToolCall, reporter: Reporter | None) -> None:
        self.call = call
        self.callers_waiting = 0
        self._ended = anyio.Event()
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
        self._ended.set()

    @property
    def has_ended(self) -> bool:
        return self._ended.is_set()

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
            return _StillRunning(self.call.request.tool, seconds)
        failure = self._failure
        if failure is not None:
            raise failure
        return self._task.result()


class _ToolCalls:
    """Every tool call whose caller was told it is still running, by call identity, whether its run is still going or
    has ended and keeps its outcome for that caller to collect."""

    def __init__(self, work: ToolWork) -> None:
        # What answers a call on its worker thread, with a reporter for its progress.
        self._work = work
        # The run each caller told its call is still running will ask for again, kept until that caller hears its
        # outcome: an outcome dropped before then is a run started again, which answers "still running" once more.
        self._promised: dict[str, _RunningCall] = {}

    async def run(self, call: ToolCall, seconds: float, reporter: Reporter | None) -> SentValue | _StillRunning:
        """The work's value for call, run on a worker thread with reporter for its progress, waiting up to seconds. An
        identical call whose caller was told it is still running joins that run, or collects its outcome once it has
        ended, instead of starting the work again; an identical call still within its time limit does not, because it
        began before whatever changed since, so a read made after a change answers from that change."""
        identity = call.identity
        running = self._promised.get(identity) or self._start(call, reporter)
        try:
            outcome = await running.answer(seconds)
        finally:
            if running.has_ended and self._promised.get(identity) is running:
                del self._promised[identity]
        if isinstance(outcome, _StillRunning):
            self._promised[identity] = running
        return outcome

    def _start(self, call: ToolCall, reporter: Reporter | None) -> _RunningCall:
        running = _RunningCall(call, reporter)
        running.start(self._work, self._end)
        return running

    def _end(self, running: _RunningCall) -> None:
        running.end()
        if not running.callers_waiting:
            running.log_unheard_failure()
