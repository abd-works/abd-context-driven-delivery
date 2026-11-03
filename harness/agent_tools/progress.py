"""Progress of a long tool call: an operation says what it is doing, and whatever called the tool hears it.

An operation calls `report_progress(message)` as it works. Over MCP, the server turns each report into a progress
notification for the call that asked for one; called any other way, a report goes nowhere."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar

_reporter: ContextVar[Callable[[str], None] | None] = ContextVar("progress_reporter", default=None)


def report_progress(message: str) -> None:
    """Tell whoever called the running tool what it is doing now."""
    reporter = _reporter.get()
    if reporter is not None:
        reporter(message)


@contextmanager
def reporting_to(reporter: Callable[[str], None] | None) -> Iterator[None]:
    """Send the reports of the call run inside this block to reporter."""
    token = _reporter.set(reporter)
    try:
        yield
    finally:
        _reporter.reset(token)
