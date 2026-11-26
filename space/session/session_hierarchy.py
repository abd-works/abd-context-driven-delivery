"""SessionHierarchy - where one session sits among a board's tickets: its parent, its children, and whether it was pulled
out of its parent."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from space.session.session import Session
    from space.session.session_record import SessionFields

class SessionHierarchy:
    """A board ticket's place under another: the session it was split from, kept in its session.json, the children it
    opens, and whether a child moves on the board as a card of its own while keeping its parent."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def parent(self) -> str:
        """The name of the session this one was split from; empty when it was not split from one."""
        return self._session.record.fields.parent

    @property
    def is_pulled_out(self) -> bool:
        """Whether this child moves on the board as a card of its own, still keeping its parent."""
        return bool(self._session.record.fields.pulled_out)

    def set_parent(self, parent: Session | None) -> None:
        """Make parent the session this one is a child of, or none; a child moved to another parent, or to none, is no
        longer pulled out of one."""
        name = parent.name if parent is not None else ""

        def placed_under(fields: SessionFields) -> None:
            fields.parent = name
            fields.pulled_out = False

        self._session.record.update(placed_under, f"parent {name}")

    def open_child(self, name: str, title: str, scope: str) -> Session:
        """A new session called name and titled title, its parent this one, working where this one works. The caller
        gives a name no session has, since a session of that name would be opened again and made its own parent."""
        session = self._session
        return session.sessions.create(name, session.work_root, title=title, scope=scope, parent=session.name)

    @property
    def ancestors(self) -> list[str]:
        """The names of its parent, its parent's parent, and so on, read from each one's record; it stops where a parent
        is not there, or would be met twice."""
        sessions = self._session.sessions
        found: list[str] = []
        name = self.parent
        while name and name != self._session.name and name not in found:
            folder = sessions.folder_named(name)
            if folder is None:
                break
            found.append(name)
            name = sessions.held.at(folder).hierarchy.parent
        return found

    def can_take_parent(self, other: Session) -> bool:
        """Whether other may become this session's parent: never itself, nor a session it is an ancestor of, which
        would make a loop."""
        return self._session.name not in [other.name, *other.hierarchy.ancestors]

    def mark_pulled_out(self) -> None:
        self._session.record.update(lambda fields: setattr(fields, "pulled_out", True), "pulled out")
