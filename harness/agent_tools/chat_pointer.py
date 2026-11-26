"""The chat a tool call came from: the chat's id, its transcript file, and the transcript lines the call covers. A
session.log line ends with it, so the chat's words can be read back under the line."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from harness.git.checkout import Checkout
from harness.process.claude_chat_process import claude_config_folder, is_desktop_spare


# A chat id becomes part of a file pattern, so only the letters, digits, and dashes of an id may reach it.
_CHAT_ID = re.compile(r"[0-9A-Za-z-]+")
# What a connect script sends when its IDE names no chat, and what the server writes for a chat it cannot name.
_NOT_A_CHAT = ("unnamed", "unknown", "no-chat")
_IN_LOG_LINE = re.compile(
    r" ([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}) (.+)$",
    re.IGNORECASE,
)
_LINE_RANGE = re.compile(r"^\d+(?:-\d+)?$")
# Each event a Claude Code transcript records names the folder the chat worked in then, as its "cwd".
_RECORDED_FOLDER = re.compile(r'"cwd"\s*:\s*("(?:[^"\\]|\\.)*")')
# The latest folder is near the end of the transcript, so only this much of a long transcript is read for it.
_FOLDER_SEARCH_BYTES = 256 * 1024
# The names a tool call's arguments may give each part of its chat, first choice first.
_ID_ARGUMENTS = ("conversation_id", "_conversation_id")
_TRANSCRIPT_ARGUMENTS = ("transcript_path", "agent_transcript_path", "_transcript_path")
_LINES_ARGUMENTS = ("transcript_lines", "_transcript_lines")
# A value a JSON transcript event holds.
type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]


# Each chat's transcript as found under a Claude projects folder: a chat's transcript stays where it was made, so it is
# searched for once, not on every call the chat makes.
_FOUND_TRANSCRIPTS: dict[tuple[Path, str], Path] = {}


class ChatPointer:
    """Which chat a tool call, and the session.log line it writes, came from, so ``read_loop`` can put that chat's words
    back under the line. Each *ToolCall* carries the chat it came from.

    The pointer is written as ``{id} {transcript} {lines}``: the chat's id, the path of its transcript, and the range
    of transcript lines, such as ``1-40``, that the line covers. A chat the server cannot name is written ``no-chat``.
    """

    def __init__(self, chat_id: str, transcript: Path | None = None, lines: str | None = "") -> None:
        """lines is the range of transcript lines the pointer covers; ``None`` for every line of the transcript so far,
        counted the first time they are asked for."""
        self.id = chat_id
        self.transcript = Path(transcript) if transcript is not None else None
        # A pointer to every line so far counts them only when asked: a transcript can be tens of megabytes, and the
        # server names the chat of every call, a chat's check-in every second among them, but writes few log lines.
        self._lines = lines

    @property
    def lines(self) -> str:
        """The range of transcript lines this pointer covers, such as ``1-40``."""
        if self._lines is None:
            self._lines = self._all_lines() if self.transcript is not None else ""
        return self._lines

    @classmethod
    def of(cls, chat_id: str, transcript: str | Path | None, lines: str = "") -> ChatPointer | None:
        """The pointer for a chat named by its id and transcript; none when either is missing. With no lines given,
        it covers every line of the transcript so far."""
        chat_id = (chat_id or "").strip()
        transcript = str(transcript or "").strip()
        if not chat_id or not transcript:
            return None
        given = (lines or "").strip()
        return cls(chat_id, Path(transcript), given or None)

    @classmethod
    def taken_from(cls, arguments: dict[str, object] | None) -> tuple[ChatPointer | None, dict[str, object]]:
        """The chat a tool call names in its arguments, and the arguments left for the tool itself. A Claude Code chat
        sends only its id, so its transcript is found by that id; a chat whose transcript cannot be found points at
        ``unknown``."""
        sent = _SentArguments(arguments)
        chat_id = sent.taken(_ID_ARGUMENTS)
        transcript = sent.taken(_TRANSCRIPT_ARGUMENTS)
        lines = sent.taken(_LINES_ARGUMENTS)
        if not chat_id and not transcript:
            return None, sent.remaining
        if not transcript:
            found = cls.from_claude_chat(chat_id)
            transcript = str(found.transcript) if found is not None else "unknown"
        return cls.of(chat_id or "unknown", transcript, lines), sent.remaining

    @classmethod
    def from_claude_chat(cls, chat_id: str) -> ChatPointer | None:
        """A Claude Code chat's pointer, found by its id alone: its transcript is the file named for that id under the
        Claude projects folder, in the folder of the project the chat started in. None when no such transcript is there."""
        found = cls.from_claude_session(chat_id)
        return cls.of(chat_id, found.transcript) if found is not None else None

    @classmethod
    def from_request(cls, chat_id: str) -> ChatPointer | None:
        """The chat a request's headers name by its id: with its transcript when one is found, else by its id alone, so
        what the chat keeps open stays its own; none when the id is empty or is not a chat id."""
        cleaned = (chat_id or "").strip()
        if not _CHAT_ID.fullmatch(cleaned) or cleaned in _NOT_A_CHAT:
            return None
        return cls.from_claude_chat(cleaned) or cls(cleaned)

    @classmethod
    def from_claude_session(cls, chat_id: str) -> ChatPointer | None:
        """A Claude Code chat's pointer with its transcript found but not counted: enough to read the folder the chat
        works in, on every call, without reading a long transcript whole. None when no such transcript is there."""
        found = _ClaudeProjects().transcript_of(chat_id)
        return cls(chat_id, found) if found is not None else None

    @property
    def working_folder(self) -> Path | None:
        """The checkout the chat works in now: the folder its transcript recorded last, or the checkout holding it when
        the chat had moved into a subfolder. A chat moved to another folder after it started records the new one, so
        this follows the chat where the folder it started in does not. None when the transcript records no folder that
        is still there."""
        folder = self._latest_recorded_folder()
        return Checkout.holding(folder).folder if folder is not None else None

    def _latest_recorded_folder(self) -> Path | None:
        if self.transcript is None or not self.transcript.is_file():
            return None
        recorded = _RECORDED_FOLDER.findall(self._transcript_end())
        folders = [Path(json.loads(text)) for text in reversed(recorded)]
        return next((folder for folder in folders if folder.is_dir() and not is_desktop_spare(folder)), None)

    def _transcript_end(self) -> str:
        with self.transcript.open("rb") as transcript:
            transcript.seek(0, os.SEEK_END)
            transcript.seek(max(0, transcript.tell() - _FOLDER_SEARCH_BYTES))
            return transcript.read().decode("utf-8", errors="replace")

    @classmethod
    def in_log_line(cls, line: str) -> ChatPointer | None:
        """The pointer at the end of a session.log line; none on a ``no-chat`` line or a line without one."""
        if " no-chat " in line:
            return None
        match = _IN_LOG_LINE.search(line)
        if not match:
            return None
        path_text, _, lines = match.group(2).strip().rpartition(" ")
        if not path_text or not _LINE_RANGE.fullmatch(lines):
            return None
        return cls(match.group(1), Path(path_text), lines)

    @property
    def is_missing(self) -> bool:
        """True for the ``no-chat`` pointer, written when no chat can be named."""
        return self.transcript is None

    @property
    def line_range(self) -> tuple[int, int]:
        """The first and last transcript lines this pointer covers, counting from 1."""
        token = (self.lines or "").strip()
        if "-" in token:
            left, right = token.split("-", 1)
            start = max(1, int(left))
            return start, max(start, int(right))
        line = max(1, int(token or "1"))
        return line, line

    def transcript_text(self) -> list[str]:
        """The transcript lines this pointer covers. A JSONL transcript gives each event's role and text."""
        path = self.transcript
        if path is None or not path.is_file():
            return [f"(missing transcript: {path})"]
        start, end = self.line_range
        raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
        if path.suffix.lower() == ".jsonl":
            formatted = [
                piece
                for index in range(start - 1, min(end, len(raw)))
                if (piece := _TranscriptEvent(raw[index], index + 1).text)
            ]
            return formatted or [f"(empty transcript slice {self.lines} in {path})"]
        return raw[start - 1 : end] or [f"(empty transcript slice {self.lines} in {path})"]

    def __str__(self) -> str:
        if self.transcript is None:
            return self.id
        return f"{self.id} {self.transcript} {self.lines}".strip()

    def __repr__(self) -> str:
        return f"ChatPointer({str(self)!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ChatPointer) and str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))

    def _all_lines(self) -> str:
        """The range of every line of the transcript so far, counted as bytes, so a long transcript is never decoded
        for it."""
        if not self.transcript.is_file():
            return "1"
        body = self.transcript.read_bytes()
        count = body.count(b"\n") + (1 if body and not body.endswith(b"\n") else 0)
        return f"1-{count}" if count > 1 else "1"


class _SentArguments:
    """The arguments a tool call sent, from which the names of its chat are taken, leaving the tool's own."""

    def __init__(self, arguments: dict[str, object] | None) -> None:
        self.remaining = dict(arguments or {})

    def taken(self, names: tuple[str, ...]) -> str:
        """The first of names the arguments give a value, each of names taken out of them."""
        found = ""
        for name in names:
            value = str(self.remaining.pop(name, "") or "").strip()
            found = found or value
        return found


class _ClaudeProjects:
    """The Claude projects folder, where Claude Code keeps each chat's transcript, named for the chat's id, in the
    folder of the project the chat started in."""

    def __init__(self) -> None:
        self._folder = claude_config_folder() / "projects"

    def transcript_of(self, chat_id: str) -> Path | None:
        """The transcript of the chat chat_id names; none when the id is not a chat id or no such transcript is there."""
        if not _CHAT_ID.fullmatch(chat_id or ""):
            return None
        held = _FOUND_TRANSCRIPTS.get((self._folder, chat_id))
        if held is not None and held.is_file():
            return held
        found = next(self._folder.glob(f"*/{chat_id}.jsonl"), None) if self._folder.is_dir() else None
        if found is not None:
            _FOUND_TRANSCRIPTS[(self._folder, chat_id)] = found
        return found


class _TranscriptEvent:
    """One line of a JSONL transcript, as a reader of the log reads it: the role of the event and the text it says."""

    def __init__(self, line: str, line_number: int) -> None:
        self._line = line.strip()
        self._line_number = line_number

    @property
    def text(self) -> str:
        """The event's role and text, headed by its line number; the line as it is when it is not JSON, and empty for
        a blank line."""
        if not self._line:
            return ""
        try:
            event = json.loads(self._line)
        except json.JSONDecodeError:
            return f"L{self._line_number}: {self._line}"
        role = str(event.get("role") or "event")
        body = "\n".join(self._texts_of(event.get("message"))).strip() or self._line
        return f"L{self._line_number} [{role}]\n{body}"

    def _texts_of(self, message: JsonValue) -> list[str]:
        """The text parts of an event's message: its text content parts, or its content when that is text alone."""
        if not isinstance(message, dict):
            return []
        content = message.get("content")
        if isinstance(content, str):
            return [content]
        if not isinstance(content, list):
            return []
        return [str(part.get("text") or "") for part in content if isinstance(part, dict) and part.get("type") == "text"]

# A log line from a chat the server cannot name ends with "no-chat" in place of the chat's id, transcript, and lines.
NO_CHAT = ChatPointer("no-chat")
