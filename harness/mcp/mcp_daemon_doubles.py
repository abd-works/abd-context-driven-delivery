"""Test doubles for *McpDaemon*'s boundaries, shared by its unit spec and its heavy spec: the server's address, which
answers no ping or answers once a server has started, the server's port, which names the process holding it, and a
daemon whose start of the server process is only recorded."""
from __future__ import annotations

import time

from harness.mcp.mcp_address import McpAddress
from harness.mcp.mcp_daemon import McpDaemon


class SilentAddress(McpAddress):
    """The server's address with nothing answering on it: a ping finds no server, at once, without opening a socket."""

    def ping_answer(self, reply_seconds: float) -> dict | None:
        return None


class StartingAddress(McpAddress):
    """The server's address, where nothing answers until a server has started on it; then a ping finds that server."""

    def __init__(self, port: int) -> None:
        super().__init__(port)
        self.started = False

    def ping_answer(self, reply_seconds: float) -> dict | None:
        return {"pid": 4242, "source": "checkout", "projects": []} if self.started else None


class RecordingProcess:
    """A process that records that it was asked to stop, and, given a list of events, when."""

    def __init__(self, events: list[str] | None = None) -> None:
        self.stopped = False
        self._events = events if events is not None else []

    def stop(self, wait_seconds: float) -> None:
        self.stopped = True
        self._events.append("stop")


class PortStub:
    """The server's port, naming one holder and recording each time it was asked who holds it."""

    def __init__(self, port: int, holder: RecordingProcess | None) -> None:
        self.port = port
        self._holder = holder
        self.asked: list[int] = []

    def holder(self) -> RecordingProcess | None:
        self.asked.append(self.port)
        return self._holder


class RecordedStartDaemon(McpDaemon):
    """A daemon whose start of the server process is recorded instead of run: the server answers on the address once it
    has been started, after ``start_seconds``, and it looks again for the answer without pausing."""

    ping_retry_seconds = 0.001

    def __init__(self, *arguments, events: list[str], start_seconds: float = 0, **keywords) -> None:
        super().__init__(*arguments, **keywords)
        self._events = events
        self._start_seconds = start_seconds

    def spawn(self) -> None:
        self._events.append("spawn")
        time.sleep(self._start_seconds)
        self.address.started = True
