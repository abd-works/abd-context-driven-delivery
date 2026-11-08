"""The event loop the cdd server answers chats on: it keeps accepting connections when a caller hangs up early, and frees
every connection a caller drops.

On Windows, asyncio accepts connections through an I/O completion port. When a caller closes its connection before the
server accepts it, the accept fails with ``WinError 64`` and asyncio treats that as the listening socket failing: it
closes the socket and stops accepting. The process then lives on, holding the port and answering nobody. The socket
asyncio made for that accept is never closed either, and when a caller resets a connection the server is closing,
asyncio's ``shutdown`` raises ``WinError 10054`` before it closes the socket or tells the server the connection ended.
Under a burst of dropped calls, such as several chats giving up on slow validates at once, those leaked sockets pile up
until the process stops answering."""
from __future__ import annotations

import asyncio
import functools
import logging
import socket
import struct
import sys
from typing import Any

logger = logging.getLogger(__name__)
# Windows' ERROR_NETNAME_DELETED: the caller closed its connection before the server accepted it.
_ERROR_NETNAME_DELETED = 64
# The message asyncio's event loop reports with when it has closed a listening socket after a failed accept.
_ACCEPT_FAILED = "Accept failed on a socket"


class _AcceptFailure:
    """What made one accept of a caller's connection fail, if anything did."""

    def __init__(self, error: BaseException | None) -> None:
        self.error = error

    @property
    def caller_hung_up(self) -> bool:
        """True when the accept failed only because the caller went away, so the listening socket is still sound."""
        if isinstance(self.error, (ConnectionResetError, ConnectionAbortedError)):
            return True
        return isinstance(self.error, OSError) and getattr(self.error, "winerror", None) == _ERROR_NETNAME_DELETED


class _ListeningLoop:
    """Makes the event loop for one uvicorn server. A failed accept that leaves the listening socket closed stops the
    server, so the process exits and frees the port, and the next connect starts a server that accepts again."""

    def __init__(self, server: Any) -> None:
        self._server = server

    def new_event_loop(self) -> asyncio.AbstractEventLoop:
        loop = _DropTolerantProactorLoop(_AcceptRetryingProactor()) if sys.platform == "win32" else asyncio.SelectorEventLoop()
        loop.set_exception_handler(self._on_loop_error)
        return loop

    def _on_loop_error(self, loop: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
        loop.default_exception_handler(context)
        if context.get("message") != _ACCEPT_FAILED:
            return
        logger.error("the cdd server stopped accepting connections; it exits so the next connect starts it again")
        self._server.should_exit = True


if sys.platform == "win32":
    import _overlapped
    from asyncio import proactor_events
    from asyncio.windows_events import NULL, IocpProactor

    class _AcceptRetryingProactor(IocpProactor):
        """Windows' I/O completion port, accepting the next caller when one hangs up before it is accepted, and closing
        the socket it made for a failed accept."""

        def accept(self, listener: socket.socket) -> asyncio.Future:
            accepted = self._loop.create_future()
            self._accept_into(listener, accepted)
            return accepted

        def _accept_once(self, listener: socket.socket) -> asyncio.Future:
            """One accept of the next caller, as ``IocpProactor.accept`` makes it, except that the socket made for the
            caller is closed when the accept fails or is cancelled, rather than only when it is cancelled."""
            self._register_with_iocp(listener)
            conn = self._get_accept_socket(listener.family)
            overlapped = _overlapped.Overlapped(NULL)
            overlapped.AcceptEx(listener.fileno(), conn.fileno())

            def finish_accept(_transferred: Any, _key: Any, done: Any) -> tuple[socket.socket, Any]:
                done.getresult()
                # SO_UPDATE_ACCEPT_CONTEXT makes getsockname() and the like work on the accepted socket.
                conn.setsockopt(
                    socket.SOL_SOCKET, _overlapped.SO_UPDATE_ACCEPT_CONTEXT, struct.pack("@P", listener.fileno())
                )
                conn.settimeout(listener.gettimeout())
                return conn, conn.getpeername()

            attempt = self._register(overlapped, listener, finish_accept)
            attempt.add_done_callback(lambda done: conn.close() if done.cancelled() or done.exception() else None)
            return attempt

        def _accept_into(self, listener: socket.socket, accepted: asyncio.Future) -> None:
            attempt = self._accept_once(listener)
            attempt.add_done_callback(functools.partial(self._settle, listener, accepted))
            # The event loop cancels the future it was given when it stops serving; the pending accept goes with it.
            accepted.add_done_callback(lambda done: attempt.cancel() if done.cancelled() else None)

        def _settle(self, listener: socket.socket, accepted: asyncio.Future, attempt: asyncio.Future) -> None:
            if accepted.done():
                return
            if attempt.cancelled():
                accepted.cancel()
                return
            failure = attempt.exception()
            if _AcceptFailure(failure).caller_hung_up and listener.fileno() != -1:
                logger.warning("a caller hung up before its connection was accepted (%s); accepting the next one", failure)
                self._accept_into(listener, accepted)
                return
            if failure is not None:
                accepted.set_exception(failure)
                return
            accepted.set_result(attempt.result())

    class _DropTolerantSocketTransport(proactor_events._ProactorSocketTransport):
        """A connection to one caller that is always freed when it ends, even when the caller reset it first."""

        def _call_connection_lost(self, exc: BaseException | None) -> None:
            if self._called_connection_lost:
                return
            try:
                self._protocol.connection_lost(exc)
            finally:
                self._shut_down_quietly()
                self._sock.close()
                self._sock = None
                server = self._server
                if server is not None:
                    server._detach()
                    self._server = None
                self._called_connection_lost = True

        def _shut_down_quietly(self) -> None:
            """Shut the socket down before closing it, so a pending read on the caller's end ends cleanly. A caller
            that already reset the connection makes shutdown raise; the socket is closed all the same."""
            if not hasattr(self._sock, "shutdown") or self._sock.fileno() == -1:
                return
            try:
                self._sock.shutdown(socket.SHUT_RDWR)
            except OSError as gone:
                logger.debug("a caller reset its connection before the server closed it: %s", gone)

    class _DropTolerantProactorLoop(asyncio.ProactorEventLoop):
        """The proactor event loop, with connections that are freed however the caller drops them."""

        def _make_socket_transport(
            self, sock: socket.socket, protocol: Any, waiter: Any = None, extra: Any = None, server: Any = None
        ) -> _DropTolerantSocketTransport:
            return _DropTolerantSocketTransport(self, sock, protocol, waiter, extra, server)
