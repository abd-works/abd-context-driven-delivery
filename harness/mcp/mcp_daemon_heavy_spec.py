"""Stopping the cdd server against a real port: the stubbed address in ``mcp_daemon_spec.py`` stands in for these.

A real ping goes to a port nothing listens on, and to one a socket holds without ever answering, as a deadlocked server
does. Only the question of who holds the port stays stubbed, so the spec never stops a real process."""

import socket

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_address import McpAddress
from harness.mcp.mcp_daemon import McpDaemon
from harness.mcp.mcp_daemon_doubles import PortStub, RecordingProcess


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind((McpAddress.HOST, 0))
        return probe.getsockname()[1]


with description("the cdd server stopped") as self:
    def daemon_with(self, holder: RecordingProcess | None) -> McpDaemon:
        self.port_stub = PortStub(self.port, holder)
        return McpDaemon(CddHome(), McpAddress(self.port), self.port_stub)

    with context("that holds its port without answering"):
        with before.each:
            self.hung_socket = socket.socket()
            self.hung_socket.bind((McpAddress.HOST, 0))
            self.hung_socket.listen()
            self.port = self.hung_socket.getsockname()[1]

        with after.each:
            self.hung_socket.close()

        with it("should stop the process listening on its port"):
            hung = RecordingProcess()
            self.daemon_with(hung).stop()
            expect((hung.stopped, self.port_stub.asked)).to(equal((True, [self.port])))

    with context("that is not running at all"):
        with before.each:
            self.port = free_port()

        with it("should stop nothing"):
            self.daemon_with(None).stop()
            expect(self.port_stub.asked).to(equal([self.port]))
