"""Test doubles for *McpDaemon*'s boundaries, shared by its unit spec and its heavy spec: the server's address, which
answers no ping, and the machine's listening ports, which name the process holding a port."""
from __future__ import annotations

from harness.mcp.mcp_address import McpAddress


class SilentAddress(McpAddress):
    """The server's address with nothing answering on it: a ping finds no server, at once, without opening a socket."""

    def ping_answer(self, reply_seconds: float) -> dict | None:
        return None


class RecordingProcess:
    """A process that records that it was asked to stop."""

    def __init__(self) -> None:
        self.stopped = False

    def stop(self, wait_seconds: float) -> None:
        self.stopped = True


class ListeningPortsStub:
    """The machine's listening ports, naming one holder for any port and recording the ports asked about."""

    def __init__(self, holder: RecordingProcess | None) -> None:
        self._holder = holder
        self.asked: list[int] = []

    def holder(self, port: int) -> RecordingProcess | None:
        self.asked.append(port)
        return self._holder
