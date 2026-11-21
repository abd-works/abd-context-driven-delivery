"""One call of a tool: the arguments its caller sent, the project it works on, and the chat it came from."""

from __future__ import annotations

import json
from contextlib import contextmanager
from dataclasses import dataclass, replace
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Iterator, Protocol

from harness.agent_tools.chat_pointer import ChatPointer

# The arguments of a tool call that name a file or folder it works on, in every IDE's tools and CDD's own; ``paths``
# names several.
_PATH_ARGUMENTS = ("path", "file_path", "target_notebook", "target_directory", "working_directory", "transcript_path", "agent_transcript_path")
_PATHS_ARGUMENT = "paths"
# The argument naming the folder the calling chat works in now. Claude Code fills in the X-CDD-Project header once, when
# the chat connects, so the header goes stale when the chat later moves to another folder, branch, or worktree.
CHAT_FOLDER_ARGUMENT = "chat_folder"
# The chat id a call names when the server cannot name its chat.
_NO_CHAT = "unknown"


class CallSession(Protocol):
    """The session a call works in, as agent_tools and mcp use it: they log each tool a call ran in it, and each
    failure. space/session's *Session* answers it; each framework module that reads more of a session declares what it
    reads in a protocol of its own that extends this one (*HookSession*, *WorkedSession*)."""

    def log_tool(self, call: ToolCall, tool: str) -> None:
        """Log that call ran tool, with the paths it named, as a line pointing at the call's chat."""

    def log_failure(self, call: ToolCall, failure: BaseException) -> None:
        """Log that call failed with failure, its trace kept beside the session's log."""


class SessionOpener(Protocol):
    """How a call finds the sessions it works in. The framework keeps no sessions of its own: the module that does
    registers its opener with ``SESSION_OPENING.open_with`` when it is imported, so the framework never imports it."""

    def saved_in(self, project: Path) -> CallSession | None:
        """The session saved as open in project's checkout, read for one caller that serves no call, such as a hook
        event or a diagnostics probe."""

    def open_in(self, call: ToolCall) -> CallSession | None:
        """The session saved as open in the call's project."""

    def named_in(self, session_file: str, call: ToolCall) -> CallSession | None:
        """The session whose session.json is session_file, a path from the call's project or an absolute one."""


class AnsweringMcpHost(Protocol):
    """The MCP host answering a call the cdd server serves, which a diagnostics tool probes: the server of the checkout
    it serves from, and each tool it runs by its published name. The host is harness/mcp, which depends on this module,
    so a call names only what it asks of the host."""

    @property
    def checkout_toolsets(self) -> Any: ...

    def dispatch(self, name: str, arguments: dict[str, object] | None = None, project: Path | None = None) -> object: ...


class SessionsNotLoaded(LookupError):
    """A call named a session, and no module that keeps sessions has registered how to open one in this process."""

    def __init__(self, session_file: str) -> None:
        super().__init__(f"cannot open {session_file!r}: no sessions are registered with SESSION_OPENING in this process")
        self.session_file = session_file


@dataclass(frozen=True)
class ToolRequest:
    """The request a call answers: the chat that sent it and, for a call the cdd server answers, the tool it names by its
    published name, the MCP host answering it, and whether that host answers it for a chat. A call made in process, by
    a spec or a script, answers an empty request: no tool, no host, and no chat unless it names one.

    Every chat shares the server's one interpreter, so work a call that answers a chat starts that would hold the
    interpreter for minutes, such as a graph build, runs in a worker process; a call made in process does that work in
    its own process."""

    chat: ChatPointer | None = None
    tool: str = ""
    mcp_host: AnsweringMcpHost | None = None
    answers_a_chat: bool = False

    def sent_by(self, chat: ChatPointer | None) -> ToolRequest:
        """This request as chat sent it; the chat it names already when chat is none."""
        return self if chat is None else replace(self, chat=chat)


class CallsBeingAnswered:
    """The call a tool is answering on each thread, so code deep under it, such as a board switching its session, keeps
    the open session of the call's own chat without each layer passing the chat on. The process keeps one
    (``CALLS_BEING_ANSWERED``): the MCP host and an in-process answer mark the call they run, and code under them asks
    for it."""

    def __init__(self) -> None:
        self._answering: ContextVar[ToolCall | None] = ContextVar("answering_call", default=None)

    @property
    def current(self) -> ToolCall | None:
        """The call a tool is answering now on this thread; none outside a call."""
        return self._answering.get()

    @contextmanager
    def answering(self, call: ToolCall) -> Iterator[ToolCall]:
        """Mark call as the one being answered on this thread while its tool runs."""
        token = self._answering.set(call)
        try:
            yield call
        finally:
            self._answering.reset(token)


CALLS_BEING_ANSWERED = CallsBeingAnswered()


class SessionOpening:
    """How the process's calls open their sessions: the one *SessionOpener* the module that keeps sessions
    (space/session) registers when it is imported (``SESSION_OPENING.open_with(opener)``), so the framework opens a
    call's session without importing it. The process keeps one (``SESSION_OPENING``); where no opener is registered,
    a call works in no session."""

    def __init__(self) -> None:
        self._opener: SessionOpener | None = None

    def open_with(self, opener: SessionOpener) -> None:
        """Have every call find its sessions through opener."""
        self._opener = opener

    def saved_in(self, project: Path | str) -> CallSession | None:
        """The session saved as open in the ``.sessions/session.json`` of the checkout holding project, main when none
        is, for work on a project that serves no call, such as the agent BDD harness or a diagnostics probe; none when
        no sessions are registered. It is read again on each ask, so a switch or a close made through MCP is seen at
        once."""
        return self._opener.saved_in(Path(project).resolve()) if self._opener is not None else None

    def open_in(self, call: ToolCall) -> CallSession | None:
        """The session saved as open in the call's project; none when no sessions are registered."""
        return self._opener.open_in(call) if self._opener is not None else None

    def named_in(self, session_file: str, call: ToolCall) -> CallSession | None:
        """The session whose session.json is session_file, for call."""
        if self._opener is None:
            raise SessionsNotLoaded(session_file)
        return self._opener.named_in(session_file, call)


SESSION_OPENING = SessionOpening()


class ToolCall:
    """One call of a tool as its caller made it: the arguments it sent, the folder of the project the calling chat
    works on, and the request it answers (``request``): the chat it came from, and for a call the cdd server answers,
    the tool it names and the MCP host answering it. One cdd server answers every chat, so a tool reads its project, its
    chat, and the session open there from its own call; read from whatever the process worked on last, a call from one
    chat would act on another chat's project. A call that names no project, such as one a spec makes in process, works
    in no session."""

    def __init__(
        self,
        arguments: dict[str, Any] | None = None,
        project: Path | str | None = None,
        request: ToolRequest = ToolRequest(),
    ) -> None:
        self.arguments = dict(arguments or {})
        self.project = Path(project).resolve() if project is not None else None
        self.request = request
        self._session: CallSession | None = None

    @classmethod
    def sent(cls, arguments: dict[str, Any] | None, project: Path | str | None, request: ToolRequest = ToolRequest()) -> ToolCall:
        """A call as a chat sent it: the chat its arguments name is taken out of them and kept as the request's chat, so
        the tool is handed only its own arguments; the chat the request itself names is the call's chat when the
        arguments name none. A ``chat_folder`` argument names the folder the chat works in now, and is the call's
        project in place of project, so its sessions are read from that folder's checkout."""
        chat, remaining = ChatPointer.taken_from(arguments)
        chat_folder = str(remaining.pop(CHAT_FOLDER_ARGUMENT, "") or "").strip()
        return cls(remaining, chat_folder or project, request.sent_by(chat))

    @property
    def chat_id(self) -> str:
        """The id of the chat the call came from; empty when it names none."""
        chat = self.request.chat.id if self.request.chat is not None else ""
        return "" if chat == _NO_CHAT else chat

    @property
    def identity(self) -> str:
        """Two calls with the same identity ask for the same work: the same tool, on the same project, with the same
        arguments, from the same chat."""
        return json.dumps([self.request.tool, str(self.project), self.arguments, self.chat_id], sort_keys=True, default=str)

    @property
    def named_paths(self) -> list[str]:
        """The files and folders the call's arguments name, each once, as the caller wrote them: the one place a tool
        call's input is read for its paths, so the session log, the hook server, and the hooks that log or toast a call
        all read the same ones."""
        listed = self.arguments.get(_PATHS_ARGUMENT)
        values = [self.arguments.get(key) for key in _PATH_ARGUMENTS] + (listed if isinstance(listed, list) else [])
        return list(dict.fromkeys(str(value).strip() for value in values if isinstance(value, str) and value.strip()))

    @property
    def session(self) -> CallSession | None:
        """The session saved as open in the ``.sessions/session.json`` of the checkout holding the project, main when
        none is, read once for this call; none when the call names no project or no sessions are registered. Every call
        in a session works on the one object its sessions hold for it; the lines a call logs point at this call's
        chat."""
        if self.project is None:
            return None
        if self._session is None:
            self._session = SESSION_OPENING.open_in(self)
        return self._session

    def session_named(self, session_file: str) -> CallSession | None:
        """The session whose session.json is session_file, a path from the project or an absolute one, for this call.
        A board command names its ticket's session this way, because it runs in whichever chat it is sent to."""
        return SESSION_OPENING.named_in(session_file, self)
