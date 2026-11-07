"""One call of a tool: the arguments its caller sent, the project it works on, and the chat it came from."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar, Protocol

from harness.agent_tools.chat_pointer import ChatPointer


class SessionOpener(Protocol):
    """How a call finds the sessions it works in. The framework keeps no sessions of its own: the module that does
    registers its opener with ``ToolCall.open_sessions_with`` when it is imported, so the framework never imports it."""

    def open_in(self, call: ToolCall) -> Any:
        """The session saved as open in the call's project, opened for this call alone."""

    def named_in(self, session_file: str, call: ToolCall) -> Any:
        """The session whose session.json is session_file, a path from the call's project or an absolute one, opened
        for this call alone."""


class SessionsNotLoaded(LookupError):
    """A call named a session, and no module that keeps sessions has registered how to open one in this process."""

    def __init__(self, session_file: str) -> None:
        super().__init__(f"cannot open {session_file!r}: no sessions are registered with ToolCall in this process")
        self.session_file = session_file


class ToolCall:
    """One call of a tool as its caller made it: the arguments it sent, the folder of the project the calling chat
    works on, and that chat. One cdd server answers every chat, so a tool reads its project, its chat, and the session
    open there from its own call; read from whatever the process worked on last, a call from one chat would act on
    another chat's project. A call that names no project, such as one a spec makes in process, works in no session."""

    _sessions: ClassVar[SessionOpener | None] = None

    def __init__(
        self,
        arguments: dict[str, Any] | None = None,
        project: Path | str | None = None,
        chat: ChatPointer | None = None,
    ) -> None:
        self.arguments = dict(arguments or {})
        self.project = Path(project).resolve() if project is not None else None
        self.chat = chat
        self._session: Any = None

    @classmethod
    def sent(cls, arguments: dict[str, Any] | None, project: Path | str | None) -> ToolCall:
        """A call as a chat sent it: the chat its arguments name is taken out of them and kept as the call's chat, so
        the tool is handed only its own arguments."""
        chat, remaining = ChatPointer.taken_from(arguments)
        return cls(remaining, project, chat)

    @classmethod
    def open_sessions_with(cls, opener: SessionOpener) -> None:
        """Have every call find its sessions through opener."""
        ToolCall._sessions = opener

    @property
    def session(self) -> Any:
        """The session saved as open in the ``.sessions/session.json`` of the checkout holding the project, main when
        none is, opened for this call and read once; none when the call names no project or no sessions are registered.
        Each call reads its own, so what one call does to it, such as the fidelity an action works at, is never seen by
        another."""
        if self.project is None or ToolCall._sessions is None:
            return None
        if self._session is None:
            self._session = ToolCall._sessions.open_in(self)
        return self._session

    def session_named(self, session_file: str) -> Any:
        """The session whose session.json is session_file, a path from the project or an absolute one, opened for this
        call. A board command names its ticket's session this way, because it runs in whichever chat it is sent to."""
        if ToolCall._sessions is None:
            raise SessionsNotLoaded(session_file)
        return ToolCall._sessions.named_in(session_file, self)
