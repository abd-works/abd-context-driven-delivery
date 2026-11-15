"""Stopping the cdd server, including one that holds its port and never answers, such as a deadlocked one.

The machine's listening ports are stubbed at the one boundary *McpDaemon* asks them through, so this spec starts and
stops no process."""

import shutil
import socket
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_daemon import McpDaemon


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class RecordingProcess:
    def __init__(self) -> None:
        self.stopped = False

    def stop(self, wait_seconds: float) -> None:
        self.stopped = True


class ListeningPortsStub:
    def __init__(self, holder: RecordingProcess | None) -> None:
        self._holder = holder
        self.asked: list[int] = []

    def holder(self, port: int) -> RecordingProcess | None:
        self.asked.append(port)
        return self._holder


with description("the cdd server stopped") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="mcp-daemon-"))
        # Nothing listens on a port just freed, so the ping finds no answer, as it finds none from a deadlocked server.
        self.port = free_port()

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    def daemon_with(self, holder: RecordingProcess | None) -> McpDaemon:
        self.listening = ListeningPortsStub(holder)
        return McpDaemon(CddHome(self.root / ".cdd"), port=self.port, listening=self.listening)

    with context("that holds its port without answering"):
        with it("should stop the process listening on its port"):
            hung = RecordingProcess()
            self.daemon_with(hung).stop()
            expect((hung.stopped, self.listening.asked)).to(equal((True, [self.port])))

    with context("that is not running at all"):
        with it("should stop nothing"):
            self.daemon_with(None).stop()
            expect(self.listening.asked).to(equal([self.port]))
