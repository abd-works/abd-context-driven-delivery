"""A Claude Code chat the cdd-board mod connects: who it is, whether a turn is running, and the commands waiting for it."""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Callable, Literal, TypedDict, TypeVar

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.destination import language_adapter
from harness.mcp.mcp_server import mcp

# The mod checks in every second, so a chat silent for this long has gone.
CHAT_GONE_SECONDS = 5
# A person can rename a chat at any time, so its title is read again this often.
TITLE_READ_SECONDS = 30
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

CommandKind = Literal["submit", "fill", "command", "restart_cdd"]
MessageState = Literal["waiting", "taken", "shown", "done", "failed"]
T = TypeVar("T")


class ChatData(TypedDict):
    id: str
    name: str
    is_busy: bool


class ChatCommandData(TypedDict):
    message: str
    kind: str
    text: str


class ChatMessageData(TypedDict):
    message: str
    kind: str
    text: str
    sent_at: float
    state: MessageState
    reason: str


class ChatNotConnectedError(LookupError):
    """Raised when a command is sent to a chat whose mod has not checked in lately."""

    def __init__(self, chat: str) -> None:
        super().__init__(f"chat {chat!r} is not connected: is the cdd-board mod loaded in it?")


def _chats_folder() -> Path:
    return Path(os.environ.get("CDD_CHATS_FOLDER") or Path.home() / ".claude" / "cdd-chats")


def _claude_projects() -> Path:
    return Path(os.environ.get("CDD_CLAUDE_PROJECTS") or Path.home() / ".claude" / "projects")


@language_adapter(language="typescript", identity="id")
@agent_toolset
class Chat:
    """Reach a Claude Code chat from outside it: list the chats that are connected, and send one a command.

    Every chat runs its own cdd server and the board runs another, so a chat is a folder every process can read: the
    chat alone writes its state when it checks in, and a sender adds one file per command to its waiting folder.
    """

    # Seconds since the epoch; a spec sets its own.
    clock = staticmethod(time.time)

    def __init__(self, folder: Path) -> None:
        self._folder = folder

    @classmethod
    @tool_subject
    def load(cls, chat: str) -> Chat:
        return cls(_chats_folder() / chat)

    @classmethod
    @mcp
    @agent_tool
    @noSessionLog
    def list(cls) -> list[ChatData]:
        """List the chats whose cdd-board mod has checked in lately: each one's id, the title the app shows for it, and whether a turn is running."""
        folder = _chats_folder()
        chats = [cls(entry) for entry in sorted(folder.iterdir())] if folder.is_dir() else []
        return [chat.to_json() for chat in chats if chat.is_connected]

    @mcp
    @agent_tool
    @noSessionLog
    def send(self, kind: CommandKind, text: str) -> ChatData:
        """Send chat a command: a fill puts text in its prompt for the person to review, a submit sends it, a command runs a slash command, and restart_cdd restarts the chat's own cdd server on the code as it is now. A fill waits until the chat's turn has ended."""
        if not self.is_connected:
            raise ChatNotConnectedError(self.id)
        waiting = self._folder / WAITING
        waiting.mkdir(parents=True, exist_ok=True)
        (waiting / self._next_file_name()).write_text(json.dumps({"kind": kind, "text": text, "sent_at": self.clock()}), encoding="utf-8")
        return self.to_json()

    @mcp
    @agent_tool
    @noSessionLog
    def messages(self) -> list[ChatMessageData]:
        """List the latest messages sent to chat, newest first: what each one said, when it was sent, whether it waits, was taken, was shown in the chat, or failed, and why it failed."""
        sent = [(path, state) for state in MESSAGE_STATES for path in self._sent_in(state)]
        newest = sorted(sent, key=lambda entry: entry[0].name, reverse=True)[:KEPT_MESSAGES]
        return [self._message(path, state) for path, state in newest]

    @mcp
    @agent_tool
    @noSessionLog
    def check_in(self, is_busy: bool = False, name: str = "") -> list[ChatCommandData]:
        """Check chat in, as its cdd-board mod does every second: say whether a turn is running and what to call the chat, and take the commands ready for it. A fill stays waiting while a turn runs, because one made during a turn can report success and show nothing."""
        self._folder.mkdir(parents=True, exist_ok=True)
        state = self._state
        title, title_read = (_latest_title(self._transcript), self.clock()) if self.clock() - state.get("title_read", 0) > TITLE_READ_SECONDS else (state.get("title", ""), state["title_read"])
        self._write({"name": name, "title": title, "is_busy": is_busy, "seen": self.clock(), "title_read": title_read})
        self._finish_worked_on(is_busy)
        return self._take_ready(is_busy)

    @mcp
    @agent_tool
    @noSessionLog
    def confirm(self, message: str, is_shown: bool, reason: str = "") -> ChatData:
        """Say whether chat showed a message it took, as its cdd-board mod does once the message has entered the chat or been refused; reason says why it was refused."""
        taken = self._folder / TAKEN / f"{message}.json"
        if not taken.is_file():
            return self.to_json()
        if not is_shown:
            taken.write_text(json.dumps({**json.loads(taken.read_text(encoding="utf-8")), "reason": reason}), encoding="utf-8")
        self._move(taken, SHOWN if is_shown else FAILED)
        return self.to_json()

    @mcp
    @agent_tool
    @noSessionLog
    def finish(self, message: str) -> ChatData:
        """Say chat has finished working on a message it showed, as its cdd-board mod does once the chat's turn has ended."""
        shown = self._folder / SHOWN / f"{message}.json"
        if shown.is_file():
            self._move(shown, DONE)
        return self.to_json()

    @mcp
    @agent_tool
    @noSessionLog
    def resend(self, message: str) -> ChatData:
        """Put a message chat took but did not show back in its queue, so the chat takes it again at its next check-in."""
        for state in (TAKEN, FAILED):
            unshown = self._folder / state / f"{message}.json"
            if unshown.is_file():
                sent = json.loads(unshown.read_text(encoding="utf-8"))
                unshown.write_text(json.dumps({key: value for key, value in sent.items() if key != "reason"}), encoding="utf-8")
                self._move(unshown, WAITING)
        return self.to_json()

    @mcp
    @agent_tool
    @noSessionLog
    def remove(self, message: str) -> ChatData:
        """Remove a message sent to chat, whatever its state; one still waiting is never given to the chat."""
        for state in MESSAGE_STATES:
            (self._folder / state / f"{message}.json").unlink(missing_ok=True)
        return self.to_json()

    @property
    def id(self) -> str:
        return self._folder.name

    @property
    def is_connected(self) -> bool:
        return self.clock() - self._state.get("seen", 0) < CHAT_GONE_SECONDS

    def to_json(self) -> ChatData:
        """The chat goes by the title the app shows for it, and by the name its mod sent until the app has given it one."""
        state = self._state
        return {"id": self.id, "name": state.get("title") or state.get("name", ""), "is_busy": bool(state.get("is_busy", False))}

    @property
    def _state(self) -> dict:
        path = self._folder / STATE_FILE
        return _while_windows_holds(lambda: json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {})

    # A mod that reloads can check in twice at once, so the state is written beside the file and renamed over it whole.
    def _write(self, state: dict) -> None:
        written = self._folder / f"{STATE_FILE}.{os.getpid()}.{threading.get_ident()}"
        written.write_text(json.dumps(state), encoding="utf-8")
        _while_windows_holds(lambda: written.replace(self._folder / STATE_FILE))

    # Oldest first. Each sent command is its own file, so a sender never writes a file the chat is reading. A taken command
    # waits in the taken folder until the chat confirms it, so the board can show what the chat never showed.
    def _take_ready(self, is_busy: bool) -> list[ChatCommandData]:
        taken: list[ChatCommandData] = []
        for path in self._sent_in(WAITING):
            command = json.loads(path.read_text(encoding="utf-8"))
            if command["kind"] == "fill" and is_busy:
                continue
            self._move(path, TAKEN)
            taken.append({"message": path.stem, "kind": command["kind"], "text": command["text"]})
        self._forget_old_messages()
        return taken

    # The mod finishes what it runs, but a mod that reloads mid-turn forgets it, so a shown message the chat has been busy
    # with is also done once the chat checks in idle.
    def _finish_worked_on(self, is_busy: bool) -> None:
        for path in self._sent_in(SHOWN):
            sent = json.loads(path.read_text(encoding="utf-8"))
            if is_busy and not sent.get("is_worked_on"):
                path.write_text(json.dumps({**sent, "is_worked_on": True}), encoding="utf-8")
            elif not is_busy and sent.get("is_worked_on"):
                self._move(path, DONE)

    # Windows' clock repeats within a quick burst of sends, so the name moves past every one already sent; it still
    # sorts in the order sent.
    def _next_file_name(self) -> str:
        latest = max((int(path.stem) for state in MESSAGE_STATES for path in self._sent_in(state)), default=0)
        return f"{max(time.time_ns(), latest + 1)}.json"

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

    def _message(self, path: Path, state: MessageState) -> ChatMessageData:
        sent = json.loads(path.read_text(encoding="utf-8"))
        return {"message": path.stem, "kind": sent["kind"], "text": sent["text"], "sent_at": sent.get("sent_at", 0.0), "state": state, "reason": sent.get("reason", "")}

    # The app writes a chat's transcript under the folder of the project the chat started in.
    @property
    def _transcript(self) -> Path | None:
        projects = _claude_projects()
        found = projects.glob(f"*/{self.id}.jsonl") if projects.is_dir() else []
        return next(iter(found), None)


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
