"""AnswerReads — what a session reads from its files is read once for each answer the process gives."""

from __future__ import annotations

import itertools
import threading
from typing import Callable, Generic, TypeVar

_Value = TypeVar("_Value")


class AnswerReads:
    """The answers this process gives, counted, so a value a session reads from its files, such as its
    ``session.json``, is read once for an answer however often that answer asks for it. One board answer asks a
    session's ``session.json`` thousands of times. A new answer begins each time a call or a hook event finds its
    sessions (*CallSessions*), so a change another process wrote is seen by the next answer, and each write a session
    makes begins one too, so no read in this process ever answers what was there before its own write."""

    def __init__(self) -> None:
        self._numbers = itertools.count(1)
        self._lock = threading.Lock()
        self._current = 0

    def begin(self) -> int:
        """Begin a new answer: every value held for an earlier one is read again when next asked for."""
        with self._lock:
            self._current = next(self._numbers)
            return self._current

    @property
    def current(self) -> int:
        return self._current


# The one count of answers in this process: every session it serves reads against it.
ANSWER_READS = AnswerReads()


class HeldForAnswer(Generic[_Value]):
    """One value read from a session's files, held for the answer it was read in. A session that serves no answer,
    such as one a spec loads from sessions it made itself, holds nothing and reads the value on every ask."""

    def __init__(self) -> None:
        # The answer the value was read in, and the value.
        self._held: tuple[int, _Value] | None = None

    def get(self, answer: int | None, read: Callable[[], _Value]) -> _Value:
        """The value held for answer, else read and held for it; read every time when answer is none."""
        held = self._held
        if answer is not None and held is not None and held[0] == answer:
            return held[1]
        value = read()
        if answer is not None:
            self._held = (answer, value)
        return value

    def drop(self) -> None:
        self._held = None
