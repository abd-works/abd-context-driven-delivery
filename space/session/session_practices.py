"""SessionPractices - a session's one instance of each practice."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
from space.session.practice_session_output import PracticeSessionOutput

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
        """The keys of the practices the session works on."""
        return [key for key, output in self.every.items() if output.enabled]

    def forget(self) -> None:
        """The practices were made on the session's old root, so they are made again when next asked for."""
        with self.lock:
            self._outputs = None
