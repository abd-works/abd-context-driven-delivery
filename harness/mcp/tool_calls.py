"""Tool calls running on worker threads, kept by what was asked, so a slow call is never started twice.

A worker thread cannot be stopped. A call that outlives its time limit therefore keeps running: its caller hears that
it is still running, an identical call made meanwhile waits for the same run instead of starting a second one, and the
result waits for the next identical call to collect it."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import anyio

logger = logging.getLogger(__name__)
# How long a result is kept for the caller who was told its call was still running; after that it is stale.
_UNCOLLECTED_RESULT_SECONDS = 600

Reporter = Callable[[str], None]


class ToolCallStopped(Exception):
    """The server stopped while a tool call was still running on its worker thread."""

    def __init__(self, tool: str) -> None:
        super().__init__(f"{tool} was stopped before it finished, because the server stopped")
        self.tool = tool


@dataclass(frozen=True)
class ToolRequest:
    """One tool call as a chat asked for it: the tool, the project it works on, its arguments, and how long the caller
    waits for an answer."""

    tool: str
    project: Path | None
    arguments: dict[str, object] | None
    seconds: float

    @property
    def identity(self) -> str:
        """Two requests with the same identity ask for the same work, whatever their time limits."""
        return json.dumps([self.tool, str(self.project), self.arguments or {}], sort_keys=True, default=str)


@dataclass(frozen=True)
class StillRunning:
    """The answer to a caller whose call outlived its time limit."""

    request: ToolRequest

    @property
    def message(self) -> str:
        tool = self.request.tool
        return (
            f"{tool} is still running after {self.request.seconds:g} seconds; it was not started again. Call {tool} "
            "again with the same arguments to get its result: an identical call waits for the run already going "
            "instead of starting another."
        )


class _RunningCall:
    """One run of a tool on a worker thread, and its outcome once it ends."""

    def __init__(self, request: ToolRequest, reporter: Reporter | None) -> None:
        self.request = request
        self.ended = anyio.Event()
        self.value: object = None
        self.failure: BaseException | None = ToolCallStopped(request.tool)
        self.ended_at = 0.0
        self.callers_waiting = 0
        self.told_still_running = False
        self._reporter = reporter
        self._task: asyncio.Task | None = None

    def report(self, message: str) -> None:
        """Pass a progress report to the caller who started the run, while that caller still waits for it."""
        reporter = self._reporter
        if reporter is not None:
            reporter(message)

    def start(self, run: Callable[[_RunningCall], object]) -> None:
        # The run is its own task, so a caller that stops waiting does not cancel it.
        self._task = asyncio.get_running_loop().create_task(run(self))

    async def answer(self, request: ToolRequest) -> object:
        """The outcome, when the run ends within ``request``'s time limit; otherwise ``StillRunning``."""
        self.callers_waiting += 1
        try:
            with anyio.move_on_after(request.seconds):
                await self.ended.wait()
        finally:
            self.callers_waiting -= 1
        if not self.ended.is_set():
            self._reporter = None
            self.told_still_running = True
            return StillRunning(request)
        if self.failure is not None:
            raise self.failure
        return self.value

    @property
    def is_stale(self) -> bool:
        return time.monotonic() - self.ended_at > _UNCOLLECTED_RESULT_SECONDS


class ToolCalls:
    """Every tool call this server is running on a worker thread, by request identity, and the results kept for
    callers who were told their call was still running."""

    def __init__(self) -> None:
        self._running: dict[str, _RunningCall] = {}
        self._uncollected: dict[str, _RunningCall] = {}

    async def run(self, request: ToolRequest, work: Callable[[Reporter], object], reporter: Reporter | None) -> object:
        """``work``'s value for ``request``, run on a worker thread with a reporter for its progress. An identical
        request already running is joined, and a kept result is collected, instead of starting ``work`` again."""
        self._forget_stale_results()
        call = self._uncollected.pop(request.identity, None) or self._running.get(request.identity)
        if call is None:
            call = self._start(request, work, reporter)
        return await call.answer(request)

    def _start(self, request: ToolRequest, work: Callable[[Reporter], object], reporter: Reporter | None) -> _RunningCall:
        call = _RunningCall(request, reporter)
        self._running[request.identity] = call

        async def run(running: _RunningCall) -> None:
            try:
                running.value = await anyio.to_thread.run_sync(work, running.report)
                running.failure = None
            except Exception as failure:
                running.failure = failure
            finally:
                self._end(running)

        call.start(run)
        return call

    def _end(self, call: _RunningCall) -> None:
        identity = call.request.identity
        self._running.pop(identity, None)
        call.ended_at = time.monotonic()
        call.ended.set()
        if call.callers_waiting or not call.told_still_running:
            return
        # Nobody is waiting, but a caller was promised this result.
        self._uncollected[identity] = call
        if call.failure is not None:
            logger.error("MCP tool %s failed after its caller stopped waiting", call.request.tool, exc_info=call.failure)

    def _forget_stale_results(self) -> None:
        for identity, call in list(self._uncollected.items()):
            if call.is_stale:
                del self._uncollected[identity]
