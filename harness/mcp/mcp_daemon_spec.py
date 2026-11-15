"""Stopping the cdd server, including one that holds its port and never answers, such as a deadlocked one.

The server's address and the machine's listening ports are stubbed at the boundaries *McpDaemon* asks them through, so
this spec opens no socket and starts and stops no process. ``mcp_daemon_heavy_spec.py`` states the same behaviors
against a real closed port and a real port that never answers."""

from expects import equal, expect
from mamba import before, context, description, it

from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_daemon import McpDaemon
from harness.mcp.mcp_daemon_doubles import ListeningPortsStub, RecordingProcess, SilentAddress

PORT = 47999


with description("the cdd server stopped") as self:
    with before.each:
        self.address = SilentAddress(PORT)

    def daemon_with(self, holder: RecordingProcess | None) -> McpDaemon:
        self.listening = ListeningPortsStub(holder)
        return McpDaemon(CddHome(), listening=self.listening, address=self.address)

    with context("that holds its port without answering"):
        with it("should stop the process listening on its port"):
            hung = RecordingProcess()
            self.daemon_with(hung).stop()
            expect((hung.stopped, self.listening.asked)).to(equal((True, [PORT])))

    with context("that is not running at all"):
        with it("should stop nothing"):
            self.daemon_with(None).stop()
            expect(self.listening.asked).to(equal([PORT]))
