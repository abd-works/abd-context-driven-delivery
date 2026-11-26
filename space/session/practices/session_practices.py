"""SessionPractices - a session's one instance of each practice."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
from space.session.practices.practice_session_output import PracticeSessionOutput

if TYPE_CHECKING:
    from space.session.session import Session


class SessionPractices:
    """*SessionPractices* are one session's instances of every practice, each working in that session, made once on its
    root. Calls from several chats reach the one session at once; the first to ask makes them and the others wait, so a
    session never holds two. The session's knowledge graph (*SessionGraph*) is made under the same reentrant lock
    (``lock``), because the graph asks for the practices while it is being made."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._outputs: dict[str, PracticeSessionOutput] | None = None
        # The keys of practices switched off for the session that an action was sent to work on.
        self._taken_up: set[str] = set()
        self.lock = threading.RLock()

    @property
    def every(self) -> dict[str, PracticeSessionOutput]:
        """A new instance of every practice, by key, each working in the session: made once on its root."""
        with self.lock:
            if self._outputs is None:
                self._outputs = {practice.key: PracticeSessionOutput(practice, self._session) for practice in PRACTICE_CATALOGUE.create_all()}
                for output in self._outputs.values():
                    output.guidance.work_in(output)
            return self._outputs

    @property
    def working(self) -> list[str]:
        """The keys of the practices switched on for the session, which the board, the Files app, and the chat bar
        show."""
        return [key for key, output in self.every.items() if output.enabled]

    @property
    def held(self) -> list[str]:
        """The keys of the practices the session's graph holds: those switched on, and any switched off that an action
        was sent to work on, since switching a practice off changes only what is shown, never what a command can do."""
        with self.lock:
            return [key for key, output in self.every.items() if output.enabled or key in self._taken_up]

    def take_up(self, key: str) -> None:
        """Hold the practice whose key is key in the session's graph from now on, switched on or off, because an action
        works on it."""
        with self.lock:
            if key in self.every:
                self._taken_up.add(key)

    def forget(self) -> None:
        """The practices were made on the session's old root, so they are made again when next asked for."""
        with self.lock:
            self._outputs = None
