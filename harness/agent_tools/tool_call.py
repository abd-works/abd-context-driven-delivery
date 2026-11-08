"""One call of a tool: the arguments its caller sent, the project it works on, and the chat it came from."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar, Protocol

from harness.agent_tools.chat_pointer import ChatPointer


class SessionOpener(Protocol):
    """How a call finds the sessions it works in. The framework keeps no sessions of its own: the module that does
    registers its opener with ``ToolCall.open_sessions_with`` when it is imported, so the framework never imports it."""

    def saved_in(self, project: Path) -> Any:
        """The session saved as open in project's checkout, read for one caller that serves no call, such as a hook
        event or a diagnostics probe."""

    def open_in(self, call: ToolCall) -> Any:
        """The session saved as open in the call's project."""

    def named_in(self, session_file: str, call: ToolCall) -> Any:
        """The session whose session.json is session_file, a path from the call's project or an absolute one."""


class SessionsNotLoaded(LookupError):
    """A call named a session, and no module that keeps sessions has registered how to open one in this process."""

    def __init__(self, session_file: str) -> None:
        super().__init__(f"cannot open {session_file!r}: no sessions are registered with ToolCall in this process")
        self.session_file = session_file


class ToolCall:
    """One call of a tool as its caller made it: the arguments it sent, the folder of the project the calling chat
    works on, and that chat. One cdd server answers every chat, so a tool reads its project, its chat, and the session
    open there from its own call; read from whatever the process worked on last, a call from one chat would act on
    another chat's project. A call that names no project, such as one a spec makes in process, works in no session.

    A call the cdd server answers also names the tool it calls, by its published name, and the MCP host answering it,
    which a diagnostics tool probes; a call made in process names neither. A call the server answers for a chat says so
    (``answers_a_chat``): every chat shares the server's one interpreter, so work the call starts that would hold it for
    minutes, such as a graph build, runs in a worker process. A call made in process, by a spec or a script, does that
    work in its own process."""

    _sessions: ClassVar[SessionOpener | None] = None

    def __init__(
        self,
        arguments: dict[str, Any] | None = None,
        project: Path | str | None = None,
        chat: ChatPointer | None = None,
        *,
        tool: str = "",
        mcp_host: Any = None,
        answers_a_chat: bool = False,
    ) -> None:
        self.arguments = dict(arguments or {})
        self.project = Path(project).resolve() if project is not None else None
        self.chat = chat
        self.tool = tool
        self.mcp_host = mcp_host
        self.answers_a_chat = answers_a_chat
        self._session: Any = None

    @classmethod
    def sent(
        cls,
        arguments: dict[str, Any] | None,
        project: Path | str | None,
        *,
        tool: str = "",
        mcp_host: Any = None,
        answers_a_chat: bool = False,
    ) -> ToolCall:
        """A call as a chat sent it: the chat its arguments name is taken out of them and kept as the call's chat, so
        the tool is handed only its own arguments."""
        chat, remaining = ChatPointer.taken_from(arguments)
        return cls(remaining, project, chat, tool=tool, mcp_host=mcp_host, answers_a_chat=answers_a_chat)

    @property
    def identity(self) -> str:
        """Two calls with the same identity ask for the same work: the same tool, on the same project, with the same
        arguments, from the same chat."""
        chat = self.chat.id if self.chat is not None else ""
        return json.dumps([self.tool, str(self.project), self.arguments, chat], sort_keys=True, default=str)

    @classmethod
    def open_sessions_with(cls, opener: SessionOpener) -> None:
        """Have every call find its sessions through opener."""
        ToolCall._sessions = opener

    @property
    def session(self) -> Any:
        """The session saved as open in the ``.sessions/session.json`` of the checkout holding the project, main when
        none is, read once for this call; none when the call names no project or no sessions are registered. Every call
        in a session works on the one object its sessions hold for it; the lines a call logs point at this call's
        chat."""
        if self.project is None or ToolCall._sessions is None:
            return None
        if self._session is None:
            self._session = ToolCall._sessions.open_in(self)
        return self._session

    @classmethod
    def session_in(cls, project: Path | str) -> Any:
        """The session saved as open in the ``.sessions/session.json`` of the checkout holding project, main when none
        is, for work on a project that serves no call, such as a hook event or a diagnostics probe; none when no sessions
        are registered. It is read again on each ask, so a switch or a close made through MCP is seen at once."""
        if ToolCall._sessions is None:
            return None
        return ToolCall._sessions.saved_in(Path(project).resolve())

    def session_named(self, session_file: str) -> Any:
        """The session whose session.json is session_file, a path from the project or an absolute one, for this call.
        A board command names its ticket's session this way, because it runs in whichever chat it is sent to."""
        if ToolCall._sessions is None:
            raise SessionsNotLoaded(session_file)
        return ToolCall._sessions.named_in(session_file, self)
