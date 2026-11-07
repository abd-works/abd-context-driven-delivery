"""The event loop the cdd server answers chats on: it keeps accepting connections when a caller hangs up early.

On Windows, asyncio accepts connections through an I/O completion port. When a caller closes its connection before the
server accepts it, the accept fails with ``WinError 64`` and asyncio treats that as the listening socket failing: it
closes the socket and stops accepting. The process then lives on, holding the port and answering nobody."""
from __future__ import annotations

import asyncio
import functools
import logging
import socket
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
        loop = asyncio.ProactorEventLoop(_AcceptRetryingProactor()) if sys.platform == "win32" else asyncio.SelectorEventLoop()
        loop.set_exception_handler(self._on_loop_error)
        return loop

    def _on_loop_error(self, loop: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
        loop.default_exception_handler(context)
        if context.get("message") != _ACCEPT_FAILED:
            return
        logger.error("the cdd server stopped accepting connections; it exits so the next connect starts it again")
        self._server.should_exit = True


if sys.platform == "win32":
    from asyncio.windows_events import IocpProactor

    class _AcceptRetryingProactor(IocpProactor):
        """Windows' I/O completion port, accepting the next caller when one hangs up before it is accepted."""

        def accept(self, listener: socket.socket) -> asyncio.Future:
            accepted = self._loop.create_future()
            self._accept_into(listener, accepted)
            return accepted

        def _accept_once(self, listener: socket.socket) -> asyncio.Future:
            return super().accept(listener)

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
