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

from harness.mcp.listening_loop import ListeningLoop, caller_hung_up

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


if sys.platform == "win32":
    from harness.mcp.listening_loop import AcceptRetryingProactor

    class FirstCallerHangsUp(AcceptRetryingProactor):
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
            expect(caller_hung_up(NETNAME_DELETED)).to(equal(True))

        with it("should count a reset connection as the caller's doing"):
            expect(caller_hung_up(ConnectionResetError())).to(equal(True))

        with it("should count any other failure as the listening socket's"):
            expect(caller_hung_up(OSError(9, "bad file descriptor"))).to(equal(False))

    with context("that has closed its listening socket after a failed accept"):
        with before.each:
            self.server = SimpleNamespace(should_exit=False)
            loop = ListeningLoop(self.server).new_event_loop()
            try:
                loop.call_exception_handler({"message": "Accept failed on a socket", "exception": OSError(9, "closed")})
            finally:
                loop.close()

        with it("should stop the server so the next connect starts one that accepts"):
            expect(self.server.should_exit).to(equal(True))

    with context("that reports some other error"):
        with it("should keep the server running"):
            server = SimpleNamespace(should_exit=False)
            loop = ListeningLoop(server).new_event_loop()
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
