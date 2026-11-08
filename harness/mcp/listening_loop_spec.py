"""The cdd server's event loop: a caller hanging up before it is accepted must not stop the server accepting."""
import asyncio
import socket
import sys
from pathlib import Path
from types import SimpleNamespace

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import before, context, description, it

from harness.mcp.listening_loop import _AcceptFailure, _ListeningLoop

# Windows reports a caller that hung up before its accept completed this way: a plain OSError, WinError 64.
NETNAME_DELETED = OSError(22, "The specified network name is no longer available", None, 64)


def _listener() -> socket.socket:
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    return listener


class Greeting(asyncio.Protocol):
    def connection_made(self, transport) -> None:
        transport.write(b"hello")
        transport.close()


async def _greeting_through(listener: socket.socket) -> bytes:
    server = await asyncio.get_running_loop().create_server(Greeting, sock=listener)
    async with server:
        reader, writer = await asyncio.open_connection(*listener.getsockname())
        reply = await asyncio.wait_for(reader.read(), 5)
        writer.close()
        return reply


class ResetSocket:
    """A connected socket whose caller has already reset the connection, so shutdown raises the way Windows does."""

    closed = False

    def fileno(self) -> int:
        return 7

    def shutdown(self, how: int) -> None:
        raise ConnectionResetError(10054, "An existing connection was forcibly closed by the remote host")

    def close(self) -> None:
        self.closed = True


if sys.platform == "win32":
    from harness.mcp.listening_loop import _AcceptRetryingProactor

    class FirstCallerHangsUp(_AcceptRetryingProactor):
        """Fails the first accept the way Windows does when that caller hangs up, then accepts for real."""

        hung_up = False

        def _accept_once(self, listener):
            if self.hung_up:
                return super()._accept_once(listener)
            self.hung_up = True
            failed = self._loop.create_future()
            failed.set_exception(NETNAME_DELETED)
            return failed


with description("the cdd server's listening loop") as self:
    with context("with a failed accept"):
        with it("should count a caller that hung up as the caller's doing"):
            expect(_AcceptFailure(NETNAME_DELETED).caller_hung_up).to(equal(True))

        with it("should count a reset connection as the caller's doing"):
            expect(_AcceptFailure(ConnectionResetError()).caller_hung_up).to(equal(True))

        with it("should count any other failure as the listening socket's"):
            expect(_AcceptFailure(OSError(9, "bad file descriptor")).caller_hung_up).to(equal(False))

    with context("that has closed its listening socket after a failed accept"):
        with before.each:
            self.server = SimpleNamespace(should_exit=False)
            loop = _ListeningLoop(self.server).new_event_loop()
            try:
                loop.call_exception_handler({"message": "Accept failed on a socket", "exception": OSError(9, "closed")})
            finally:
                loop.close()

        with it("should stop the server so the next connect starts one that accepts"):
            expect(self.server.should_exit).to(equal(True))

    with context("that reports some other error"):
        with it("should keep the server running"):
            server = SimpleNamespace(should_exit=False)
            loop = _ListeningLoop(server).new_event_loop()
            try:
                loop.call_exception_handler({"message": "Task exception was never retrieved"})
            finally:
                loop.close()
            expect(server.should_exit).to(equal(False))

    if sys.platform == "win32":
        with context("on Windows, with a caller that hung up before it was accepted"):
            with before.each:
                self.listener = _listener()
                loop = asyncio.ProactorEventLoop(FirstCallerHangsUp())
                try:
                    self.reply = loop.run_until_complete(_greeting_through(self.listener))
                finally:
                    loop.close()

            with it("should answer the next caller"):
                expect(self.reply).to(equal(b"hello"))

        with context("on Windows, with a connection the caller reset before the server closed it"):
            with before.each:
                from harness.mcp.listening_loop import _DropTolerantSocketTransport

                self.sock = ResetSocket()
                self.protocol = SimpleNamespace(lost=[], connection_lost=lambda exc: self.protocol.lost.append(exc))
                self.server = SimpleNamespace(detached=0)
                self.server._detach = lambda: setattr(self.server, "detached", self.server.detached + 1)
                transport = _DropTolerantSocketTransport.__new__(_DropTolerantSocketTransport)
                transport._called_connection_lost = False
                transport._protocol = self.protocol
                transport._sock = self.sock
                transport._server = self.server
                transport._call_connection_lost(None)

            with it("should tell the server's protocol the connection ended"):
                expect(self.protocol.lost).to(equal([None]))

            with it("should close the socket"):
                expect(self.sock.closed).to(equal(True))

            with it("should free the connection on the listening server"):
                expect(self.server.detached).to(equal(1))
