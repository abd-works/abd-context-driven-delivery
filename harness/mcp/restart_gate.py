"""Keep tool calls and a cdd restart apart.

A restart drops every module of the checkout and imports it again. A call still running on the old classes then finds
their modules gone, so it fails halfway; a call that starts while the modules are being imported again sees half of
them. Calls run side by side; a restart waits for the running ones to end and holds new ones until it is done."""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager


class RestartGate:
    """Let any number of tool calls run at once, or one restart alone."""

    def __init__(self) -> None:
        self._changed = threading.Condition()
        self._running_calls = 0
        self._is_restarting = False

    @contextmanager
    def running_call(self) -> Iterator[None]:
        with self._changed:
            self._changed.wait_for(lambda: not self._is_restarting)
            self._running_calls += 1
        try:
            yield
        finally:
            with self._changed:
                self._running_calls -= 1
                self._changed.notify_all()

    @contextmanager
    def restarting(self) -> Iterator[None]:
        with self._changed:
            self._changed.wait_for(lambda: not self._is_restarting)
            self._is_restarting = True
            self._changed.wait_for(lambda: self._running_calls == 0)
        try:
            yield
        finally:
            with self._changed:
                self._is_restarting = False
                self._changed.notify_all()
