"""A Claude Code chat the cdd-board mod connects: who it is, whether a turn is running, and the commands waiting for it."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Callable, Literal, TypeVar
from urllib.parse import quote

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.data_class import data_field, identity, language_adapter
from harness.installation.json_file import JsonFile, JsonFileUnreadable
from harness.mcp.mcp_server import mcp
from harness.agent_tools.chat_pointer import ChatPointer

# The mod checks in every second, so a chat silent for this long has gone.
CHAT_GONE_SECONDS = 5
# A person can rename a chat at any time, so its title is read again this often.
TITLE_READ_SECONDS = 30
NANOSECONDS_PER_SECOND = 1_000_000_000
TITLE_MARK = "custom-title"
STATE_FILE = "chat.json"
# Windows refuses to open or rename over a file another process is renaming, for a moment.
HELD_FILE_ATTEMPTS = 20
HELD_FILE_PAUSE_SECONDS = 0.01
# A message waits until the chat takes it, then the chat says whether it showed it or why it could not. Each state is a
# folder, and a message moves from one to the next.
WAITING = "waiting"
TAKEN = "taken"
SHOWN = "shown"
DONE = "done"
FAILED = "failed"
MESSAGE_STATES = (WAITING, TAKEN, SHOWN, DONE, FAILED)
# The board shows a chat's latest messages; older ones are not worth keeping.
KEPT_MESSAGES = 20
# The Claude app opens a new chat on a folder from this link, with its prompt filled in for the person to send.
NEW_CHAT_LINK = "claude://code/new"
# How long the system may take to hand a link to the app registered for its scheme.
OPEN_LINK_SECONDS = 30
# A file that keeps every link a new chat was opened with instead of opening the Claude app, as a test run names it.
OPENED_CHATS_VARIABLE = "CDD_OPENED_CHATS"

CommandKind = Literal["submit", "fill", "command", "open_file"]
MessageState = Literal["waiting", "taken", "shown", "done", "failed"]
T = TypeVar("T")


class ChatCommand:
    """A command a chat takes at its check-in: the message it came in, and what to do with its text."""

    def __init__(self, message: str, kind: str, text: str) -> None:
        self._message = message
        self._kind = kind
        self._text = text

    @property
    @data_field
    def message(self) -> str:
        return self._message

    @property
    @data_field
    def kind(self) -> str:
        return self._kind

    @property
    @data_field
    def text(self) -> str:
        return self._text


class ChatMessage(ChatCommand):
    """A message sent to a chat, as the board lists it: when it was sent, where it stands, and why it failed."""

    def __init__(self, message: str, kind: str, text: str, sent_at: float, state: MessageState, reason: str) -> None:
        super().__init__(message, kind, text)
        self._sent_at = sent_at
        self._state = state
        self._reason = reason

    @property
    @data_field
    def sent_at(self) -> float:
        return self._sent_at

    @property
    @data_field
    def state(self) -> MessageState:
        return self._state

    @property
    @data_field
    def reason(self) -> str:
        return self._reason


class ChatNotConnectedError(LookupError):
    """Raised when a command is sent to a chat whose mod has not checked in lately."""

    def __init__(self, chat: str) -> None:
        super().__init__(f"chat {chat!r} is not connected: is the cdd-board mod loaded in it?")


def _chats_folder() -> Path:
    return Path(os.environ.get("CDD_CHATS_FOLDER") or Path.home() / ".claude" / "cdd-chats")


class ChatLinks:
    """Opens a new chat in the Claude app by handing its link to the system, which passes it to the app registered for
    its scheme. A page in the app's Browser pane cannot, so the board opens a ticket's chat through the cdd server."""

    def open_new(self, folder: str, prompt: str) -> str:
        """Open a new chat on folder with prompt filled in, and answer the link it opened."""
        link = self.link_to_new(folder, prompt)
        self.hand_over(link)
        return link

    def link_to_new(self, folder: str, prompt: str) -> str:
        """The link that opens a new chat on folder with prompt filled in."""
        return f"{NEW_CHAT_LINK}?folder={quote(folder, safe='')}&q={quote(prompt, safe='')}"

    def hand_over(self, link: str) -> None:
        if sys.platform == "win32":
            os.startfile(link)  # noqa: S606 - the link names the desktop app's own scheme
        else:
            subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", link], check=True, timeout=OPEN_LINK_SECONDS)


class RecordedChatLinks(ChatLinks):
    """Keeps each link in a file, one a line, instead of opening the Claude app: a test run's chats open through it, so
    no spec opens a chat on this machine, and the spec reads the links back."""

    def __init__(self, file: Path) -> None:
        self._file = file

    def hand_over(self, link: str) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        with self._file.open("a", encoding="utf-8") as kept:
            kept.write(f"{link}\n")

    @property
    def links(self) -> list[str]:
        return self._file.read_text(encoding="utf-8").splitlines() if self._file.is_file() else []


@identity("id")
@language_adapter(language="typescript")
@agent_toolset
class Chat:
    """Reach a Claude Code chat from outside it: list the chats that are connected, and send one a command.

    Every chat runs its own cdd server and the board runs another, so a chat is a folder every process can read: the
    chat alone writes its state when it checks in, and a sender adds one file per command to its waiting folder.
    """

    # Seconds since the epoch; a spec sets its own.
    clock = staticmethod(time.time)
    # What a new chat's link is handed to: the system's, unless the run names a file to keep the links in.
    opener: ChatLinks = RecordedChatLinks(Path(os.environ[OPENED_CHATS_VARIABLE])) if os.environ.get(OPENED_CHATS_VARIABLE) else ChatLinks()

    def __init__(self, folder: Path) -> None:
        self._folder = folder
        # What the chat's mod last said at check-in: its name, whether a turn runs, its folder, and its title.
        self._state_file = JsonFile(folder / STATE_FILE)

    @classmethod
    @tool_subject
    def load(cls, chat: str) -> Chat:
        return cls(_chats_folder() / chat)

    @classmethod
    @mcp
    @agent_tool
    @noSessionLog
    def list(cls) -> list[Chat]:
        """List the chats whose cdd-board mod has checked in lately: each one's id, the title the app shows for it, and whether a turn is running."""
        folder = _chats_folder()
        chats = [cls.load(entry.name) for entry in sorted(folder.iterdir())] if folder.is_dir() else []
        return [chat for chat in chats if chat.is_connected]

    @classmethod
    @mcp
    @agent_tool
    def open(cls, folder: str, prompt: str) -> str:
        """Open a new chat in the Claude app on folder, with prompt filled in; the app asks the person to confirm the folder and send. Answers the link it opened."""
        return cls.opener.open_new(folder, prompt)

    @mcp
    @agent_tool
    @noSessionLog
    def send(self, kind: CommandKind, text: str) -> Chat:
        """Send chat a command: a fill puts text in its prompt for the person to review, a submit sends it, a command runs a slash command, and an open_file shows the file text names, a path from the project, in its chat bar's file viewer. A fill waits until the chat's turn has ended."""
        if not self.is_connected:
            raise ChatNotConnectedError(self.id)
        waiting = self._folder / WAITING
        waiting.mkdir(parents=True, exist_ok=True)
        JsonFile(waiting / self._next_file_name()).write({"kind": kind, "text": text, "sent_at": self.clock()})
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def messages(self) -> list[ChatMessage]:
        """List the latest messages sent to chat, newest first: what each one said, when it was sent, whether it waits, was taken, was shown in the chat, or failed, and why it failed."""
        sent = [(path, state) for state in MESSAGE_STATES for path in self._sent_in(state)]
        newest = sorted(sent, key=lambda entry: entry[0].name, reverse=True)[:KEPT_MESSAGES]
        return [self._message(path, state) for path, state in newest]

    @mcp
    @agent_tool
    @noSessionLog
    def check_in(self, is_busy: bool = False, name: str = "", folder: str = "") -> list[ChatCommand]:
        """Check chat in, as its cdd-board mod does every second: say whether a turn is running, what to call the chat, and the folder it works in, and take the commands ready for it. A fill stays waiting while a turn runs, because one made during a turn can report success and show nothing."""
        with _checking_in(self._folder):
            return self._check_in(is_busy, name, folder)

    def _check_in(self, is_busy: bool, name: str, folder: str) -> list[ChatCommand]:
        self._folder.mkdir(parents=True, exist_ok=True)
        self._write({"name": name, "is_busy": is_busy, "seen": self.clock(), "folder": folder, **self._title_state(self._state)})
        self._finish_worked_on(is_busy)
        return self._take_ready(is_busy)

    @mcp
    @agent_tool
    @noSessionLog
    def confirm(self, message: str, is_shown: bool, reason: str = "") -> Chat:
        """Say whether chat showed a message it took, as its cdd-board mod does once the message has entered the chat or been refused; reason says why it was refused."""
        taken = self._folder / TAKEN / f"{message}.json"
        if not taken.is_file():
            return self
        if not is_shown:
            record = JsonFile(taken)
            record.write({**record.read(), "reason": reason})
        self._move(taken, SHOWN if is_shown else FAILED)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def finish(self, message: str) -> Chat:
        """Say chat has finished working on a message it showed, as its cdd-board mod does once the chat's turn has ended."""
        shown = self._folder / SHOWN / f"{message}.json"
        if shown.is_file():
            self._move(shown, DONE)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def resend(self, message: str) -> Chat:
        """Put a message chat took but did not show back in its queue, so the chat takes it again at its next check-in."""
        for state in (TAKEN, FAILED):
            unshown = self._folder / state / f"{message}.json"
            if unshown.is_file():
                record = JsonFile(unshown)
                record.write({key: value for key, value in record.read().items() if key != "reason"})
                self._move(unshown, WAITING)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def remove(self, message: str) -> Chat:
        """Remove a message sent to chat, whatever its state; one still waiting is never given to the chat."""
        for state in MESSAGE_STATES:
            (self._folder / state / f"{message}.json").unlink(missing_ok=True)
        return self

    @property
    @data_field
    def id(self) -> str:
        return self._folder.name

    @property
    @data_field
    def name(self) -> str:
        """The chat goes by the title the app shows for it, and by the name its mod sent until the app has given it one."""
        state = self._state
        return state.get("title") or state.get("name", "")

    @property
    @data_field
    def is_busy(self) -> bool:
        return bool(self._state.get("is_busy", False))

    @property
    @data_field
    def folder(self) -> str:
        return self._state.get("folder", "")

    @property
    def is_connected(self) -> bool:
        return self.clock() - self._state.get("seen", 0) < CHAT_GONE_SECONDS

    @property
    def _state(self) -> dict:
        return _while_windows_holds(self._state_read)

    def _state_read(self) -> dict:
        """The state a chat last wrote; none when it never checked in, or when two check-ins written over each other
        left a file that does not read, so the chat's next check-in writes it afresh. A file Windows holds for another
        process's rename is read again (``_while_windows_holds``)."""
        try:
            return self._state_file.read()
        except JsonFileUnreadable as unreadable:
            if isinstance(unreadable.cause, PermissionError):
                raise unreadable.cause from unreadable
            return {}

    # A mod that reloads can check in twice at once; the state file is swapped in whole, so neither reads half of it.
    def _write(self, state: dict) -> None:
        _while_windows_holds(lambda: self._state_file.write(state))

    # Oldest first. Each sent command is its own file, so a sender never writes a file the chat is reading. A taken command
    # waits in the taken folder until the chat confirms it, so the board can show what the chat never showed.
    def _take_ready(self, is_busy: bool) -> list[ChatCommand]:
        taken: list[ChatCommand] = []
        for path in self._sent_in(WAITING):
            command = JsonFile(path).read()
            if command["kind"] == "fill" and is_busy:
                continue
            self._move(path, TAKEN)
            taken.append(ChatCommand(path.stem, command["kind"], command["text"]))
        self._forget_old_messages()
        return taken

    # The mod finishes what it runs, but a mod that reloads mid-turn forgets it, so a shown message the chat has been busy
    # with is also done once the chat checks in idle.
    def _finish_worked_on(self, is_busy: bool) -> None:
        for path in self._sent_in(SHOWN):
            record = JsonFile(path)
            sent = record.read()
            if is_busy and not sent.get("is_worked_on"):
                record.write({**sent, "is_worked_on": True})
            elif not is_busy and sent.get("is_worked_on"):
                self._move(path, DONE)

    def _title_state(self, state: dict) -> dict:
        """The chat's title, when it was read, and the transcript it was read from: read again once the last read is
        older than TITLE_READ_SECONDS, since reading a long transcript on every check-in is slow. The transcript is
        found once and kept in the chat's state, so a later read does not search the Claude projects folder again."""
        if self.clock() - state.get("title_read", 0) <= TITLE_READ_SECONDS:
            return {"title": state.get("title", ""), "title_read": state["title_read"], "transcript": state.get("transcript", "")}
        transcript = self._transcript_kept_in(state)
        return {"title": _latest_title(transcript), "title_read": self.clock(), "transcript": str(transcript or "")}

    def _transcript_kept_in(self, state: dict) -> Path | None:
        kept = Path(state["transcript"]) if state.get("transcript") else None
        if kept is not None and kept.is_file():
            return kept
        found = ChatPointer.from_claude_chat(self.id)
        return found.transcript if found is not None else None

    # Windows' clock repeats within a quick burst of sends, so the name moves past every one already sent; it still
    # sorts in the order sent.
    def _next_file_name(self) -> str:
        latest = max((int(path.stem) for state in MESSAGE_STATES for path in self._sent_in(state)), default=0)
        return f"{max(int(self.clock() * NANOSECONDS_PER_SECOND), latest + 1)}.json"

    def _sent_in(self, state: str) -> list[Path]:
        folder = self._folder / state
        return sorted(folder.glob("*.json")) if folder.is_dir() else []

    def _move(self, path: Path, state: str) -> None:
        folder = self._folder / state
        folder.mkdir(exist_ok=True)
        path.replace(folder / path.name)

    def _forget_old_messages(self) -> None:
        handled = sorted((path for state in (TAKEN, SHOWN, DONE, FAILED) for path in self._sent_in(state)), key=lambda path: path.name)
        for path in handled[:-KEPT_MESSAGES]:
            path.unlink()

    def _message(self, path: Path, state: MessageState) -> ChatMessage:
        sent = JsonFile(path).read()
        return ChatMessage(path.stem, sent["kind"], sent["text"], sent.get("sent_at", 0.0), state, sent.get("reason", ""))


# A mod that reloads checks in twice at once, and one cdd server answers every chat, so both arrive in this process. Each
# chat checks in one call at a time, so a waiting command is taken once and never moved while the other call reads it.
_CHECK_IN_LOCKS: dict[Path, threading.Lock] = {}
_CHECK_IN_LOCKS_GUARD = threading.Lock()


def _checking_in(folder: Path) -> threading.Lock:
    with _CHECK_IN_LOCKS_GUARD:
        return _CHECK_IN_LOCKS.setdefault(folder.resolve(), threading.Lock())


def _while_windows_holds(operation: Callable[[], T]) -> T:
    """Run operation on the state file, again while Windows holds the file for another process's rename."""
    for _ in range(HELD_FILE_ATTEMPTS - 1):
        try:
            return operation()
        except PermissionError:
            time.sleep(HELD_FILE_PAUSE_SECONDS)
    return operation()


def _latest_title(transcript: Path | None) -> str:
    """The latest title in a transcript, or nothing; a renamed chat writes a new title line, so the last one counts."""
    if transcript is None:
        return ""
    title = ""
    with transcript.open(encoding="utf-8", errors="replace") as lines:
        # Most lines are messages; only a line naming the title is parsed.
        for line in lines:
            if TITLE_MARK in line:
                entry = json.loads(line)
                title = entry.get("customTitle", title) if entry.get("type") == TITLE_MARK else title
    return title
