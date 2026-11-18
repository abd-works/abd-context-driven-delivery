"""Stopping and starting the cdd server, including past one that holds its port and never answers, such as a
deadlocked one.

The server's address and its port are stubbed at the boundaries *McpDaemon* asks them through, so
this spec opens no socket and starts and stops no process. ``mcp_daemon_heavy_spec.py`` states the same behaviors
against a real closed port and a real port that never answers."""

import shutil
import tempfile
import threading

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_daemon import McpDaemon
from harness.mcp.mcp_daemon_doubles import (
    PortStub,
    RecordedStartDaemon,
    RecordingProcess,
    SilentAddress,
    StartingAddress,
)

PORT = 47999


with description("the cdd server stopped") as self:
    with before.each:
        self.address = SilentAddress(PORT)

    def daemon_with(self, holder: RecordingProcess | None) -> McpDaemon:
        self.port_stub = PortStub(PORT, holder)
        return McpDaemon(CddHome(), self.address, self.port_stub)

    with context("that holds its port without answering"):
        with it("should stop the process listening on its port"):
            hung = RecordingProcess()
            self.daemon_with(hung).stop()
            expect((hung.stopped, self.port_stub.asked)).to(equal((True, [PORT])))

    with context("that is not running at all"):
        with it("should stop nothing"):
            self.daemon_with(None).stop()
            expect(self.port_stub.asked).to(equal([PORT]))


with description("the cdd server ensured") as self:
    with before.each:
        self.folder = tempfile.mkdtemp(prefix="cdd-daemon-spec-")
        self.address = StartingAddress(PORT)
        self.events: list[str] = []

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    def daemon_with(self, holder: RecordingProcess | None, start_seconds: float = 0) -> McpDaemon:
        port = PortStub(PORT, holder)
        return RecordedStartDaemon(CddHome(self.folder), self.address, port, events=self.events, start_seconds=start_seconds)

    with context("when a port holder does not answer"):
        with it("should replace the port holder that does not answer"):
            hung = RecordingProcess(self.events)
            running = self.daemon_with(hung).ensure()
            expect((self.events, running.pid)).to(equal((["stop", "spawn"], 4242)))

    with context("when nothing holds the port"):
        with it("should start the server without stopping anything"):
            self.daemon_with(None).ensure()
            expect(self.events).to(equal(["spawn"]))

    with context("when several ensures on one home run at once"):
        with it("should start the server only once"):
            daemons = [self.daemon_with(None, start_seconds=0.02) for _ in range(5)]
            calls = [threading.Thread(target=daemon.ensure) for daemon in daemons]
            for call in calls:
                call.start()
            for call in calls:
                call.join()
            expect(self.events).to(equal(["spawn"]))
