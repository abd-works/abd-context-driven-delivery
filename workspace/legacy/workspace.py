"""Legacy Workspace API — thin adapter over space.session for older toolsets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from space.session.session import Session


class SessionPaths:
    def sessions_root(self, path: Path | str) -> Path:
        return Path(path).resolve() / ".sessions"


class Turn:
    def __init__(self, root: str = "", git: Any = None) -> None:
        self.root = root
        self.git = git

    def turn(self, *args: Any, **kwargs: Any) -> None:
        return None


class WorkSession:
    """Open work span — folder maps to the active space.session folder."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self.open_turn: Turn | None = None
        self.git: Any = None

    @property
    def folder(self) -> Path:
        if self._session.session_path is not None:
            return self._session.session_path
        root = self._session.repo_path or Path(".")
        fallback = SessionPaths().sessions_root(root) / "session"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


class Workspace:
    def __init__(self, path: str) -> None:
        self.path = Path(path).resolve()
        self._work_session: WorkSession | None = None

    def load(self) -> None:
        Session.refresh_current_from_repo(self.path)
        current = Session.current(self.path)
        if current is not None and current.session_path is not None:
            self._work_session = WorkSession(current)

    def open(
        self,
        practice: Any = None,
        *,
        name: str = "",
        path: str = "",
        session: str = "",
    ) -> None:
        session_name = (name or session or "").strip()
        root = Path(path or self.path).resolve()
        if session_name:
            Session.open_named(session_name, repo_path=root)
        Session.refresh_current_from_repo(root)
        current = Session.current(root)
        if current is not None:
            self._work_session = WorkSession(current)

    @property
    def current_work_session(self) -> WorkSession | None:
        if self._work_session is not None:
            return self._work_session
        current = Session.current(self.path)
        if current is None or current.session_path is None:
            return None
        self._work_session = WorkSession(current)
        return self._work_session
