"""One call of a tool: the arguments its caller sent and the project it works on."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from space.session.session import Session


class ToolCall:
    """One call of a tool as its caller made it: the arguments it sent, and the checkout of the project the calling chat
    works on. One cdd server answers every chat, so a tool reads its project, and the session open there, from its own
    call; read from whatever the process worked on last, a call from one chat would act on another chat's project. A
    call that names no project, such as one a spec makes in process, works in no session."""

    def __init__(self, arguments: dict[str, Any] | None = None, project: Path | str | None = None) -> None:
        self.arguments = dict(arguments or {})
        self.project = Path(project).resolve() if project is not None else None
        self._session: Session | None = None

    @property
    def session(self) -> Session | None:
        """The session saved as open in the project's ``.sessions/session.json``, main when none is, read once for this
        call; none when the call names no project. Each call reads its own, so what one call does to it, such as the
        fidelity an action works at, is never seen by another."""
        if self.project is None:
            return None
        if self._session is None:
            # WHY: space sits above the framework, so the session is imported when a call first asks for it.
            from space.repo.repo import Repo

            self._session = Repo(self.project).current_session
            # WHY: a project's main session has no folder until something is written in it, and the call logs there.
            self._session.session_path.mkdir(parents=True, exist_ok=True)
        return self._session
