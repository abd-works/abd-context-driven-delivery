"""BoardPractices — the practices a checkout's session board works through, as the catalog shows them."""
from __future__ import annotations

import threading
from pathlib import Path
from typing import TYPE_CHECKING

from harness.catalog_generator.catalog_practice import CatalogPractice
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE

if TYPE_CHECKING:
    from space.session.sessions import Sessions


class PracticeNotFoundError(LookupError):
    """Raised when a caller names a practice, such as clean_engineering, that the board or ticket does not have. It
    names the practice and what was searched for it."""

    def __init__(self, practice: str, within: str) -> None:
        self.practice = practice
        self.within = within
        super().__init__(f"no practice named {practice!r} on {within}")


class BoardPractices:
    """*BoardPractices* are the practices a checkout's session board works through, each as the catalog shows it: its
    name, colour, fidelities, pages, and skills. They are the same for every session, so they are made once for the
    checkout (*HeldBoardPractices*); every board read asks them for a practice by its class, which the board's own
    instance and each session's share, rather than searching the list again."""

    def __init__(self, catalogued: list[CatalogPractice]) -> None:
        # Each practice's catalog view by the practice's class, in the order the board shows them.
        self._by_class = {type(entry.practice): entry for entry in catalogued}

    @property
    def catalogued(self) -> list[CatalogPractice]:
        """The catalog's view of each practice, in the order the board shows them."""
        return list(self._by_class.values())

    def of(self, kind: type) -> CatalogPractice:
        """The catalog's view of the practice of class kind, the class of the board's own instance and of every
        session's."""
        found = self._by_class.get(kind)
        if found is None:
            raise PracticeNotFoundError(kind.__name__, "the board")
        return found

    def works_through(self, kind: type) -> bool:
        """Whether the practice of class kind is one the board works through."""
        return kind in self._by_class

    def keyed(self, key: str) -> CatalogPractice:
        """The catalog's view of the board's practice whose folder name is key, such as clean_engineering, as a tool
        names it."""
        found = next((entry for entry in self._by_class.values() if entry.practice.key == key), None)
        if found is None:
            raise PracticeNotFoundError(key, "the board")
        return found


class HeldBoardPractices:
    """Every practice CDD has, as the catalog shows it, made once for each checkout's board with the one skill install
    their slash commands are named by: what the board shows of a practice, its name, colour, fidelities, pages, and
    skills, is the same for every session, so no single session's instances stand for it, and no other reader changes
    these. The board is made again for every call, so they are held here, for each checkout's sessions, for as long as
    the process runs."""

    def __init__(self) -> None:
        self._held: dict[Path, BoardPractices] = {}
        self._lock = threading.Lock()

    def of(self, sessions: Sessions) -> BoardPractices:
        """The practices the board of sessions' checkout works through, made the first time a board there asks."""
        with self._lock:
            held = self._held.get(sessions.root)
            if held is None:
                held = self._held[sessions.root] = BoardPractices(CatalogPractice.of_practices(PRACTICE_CATALOGUE.create_all()))
            return held


# The practices each checkout's boards work through in this process, unless a board is handed fewer.
BOARD_PRACTICES = HeldBoardPractices()
