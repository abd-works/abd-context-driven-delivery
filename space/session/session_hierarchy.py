"""SessionHierarchy - where one session sits among a board's tickets: its parent, its children, and whether it was pulled
out of its parent."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from space.session.session import Session

# The session.json fields that hold a session's parent and whether it was pulled out of that parent.
PARENT_FIELD = "parent"
_PULLED_OUT_FIELD = "pulled_out"


class SessionHierarchy:
    """A board ticket's place under another: the session it was split from, kept in its session.json, the children it
    opens, and whether a child moves on the board as a card of its own while keeping its parent."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def parent(self) -> str:
        """The name of the session this one was split from; empty when it was not split from one."""
        return self._session.record.fields.get(PARENT_FIELD, "")

    @property
    def is_pulled_out(self) -> bool:
        """Whether this child moves on the board as a card of its own, still keeping its parent."""
        return bool(self._session.record.fields.get(_PULLED_OUT_FIELD, False))

    def set_parent(self, parent: Session | None) -> None:
        """Make parent the session this one is a child of, or none; a child moved to another parent, or to none, is no
        longer pulled out of one."""
        self._session.record.save_fields(**{PARENT_FIELD: parent.name if parent is not None else "", _PULLED_OUT_FIELD: False})

    def open_child(self, name: str, title: str, scope: str) -> Session:
        """A new session called name and titled title, its parent this one, working where this one works. The caller
        gives a name no session has, since a session of that name would be opened again and made its own parent."""
        session = self._session
        return session.sessions.create(name, session.work_root, title=title, scope=scope, parent=session.name)

    def mark_pulled_out(self) -> None:
        self._session.record.save_fields(**{_PULLED_OUT_FIELD: True})
