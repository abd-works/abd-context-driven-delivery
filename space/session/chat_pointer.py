"""The chat a session.log line points at: the chat's id, its transcript file, and the transcript lines it covers."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

# A chat id becomes part of a file pattern, so only the letters, digits, and dashes of an id may reach it.
_CHAT_ID = re.compile(r"[0-9A-Za-z-]+")
_IN_LOG_LINE = re.compile(
    r" ([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}) (.+)$",
    re.IGNORECASE,
)
_LINE_RANGE = re.compile(r"^\d+(?:-\d+)?$")
# The names a tool call's arguments may give each part of its chat, first choice first.
_ID_ARGUMENTS = ("conversation_id", "_conversation_id")
_TRANSCRIPT_ARGUMENTS = ("transcript_path", "agent_transcript_path", "_transcript_path")
_LINES_ARGUMENTS = ("transcript_lines", "_transcript_lines")


class ChatPointer:
    """Which chat a session.log line came from, so ``read_loop`` can put that chat's words back under the line.

    The pointer is written as ``{id} {transcript} {lines}``: the chat's id, the path of its transcript, and the range
    of transcript lines, such as ``1-40``, that the line covers. A chat the server cannot name is written ``no-chat``.
    """

    # The chat of the tool call being served. One cdd server serves every chat at once, so each call keeps its own.
    _serving: ContextVar[ChatPointer | None] = ContextVar("cdd_chat_pointer", default=None)

    def __init__(self, id: str, transcript: Path | None = None, lines: str = "") -> None:
        self.id = id
        self.transcript = Path(transcript) if transcript is not None else None
        self.lines = lines

    @classmethod
    def of(cls, chat_id: str, transcript: str | Path | None, lines: str = "") -> ChatPointer | None:
        """The pointer for a chat named by its id and transcript; none when either is missing. With no lines given,
        it covers every line of the transcript so far."""
        chat_id = (chat_id or "").strip()
        transcript = str(transcript or "").strip()
        if not chat_id or not transcript:
            return None
        path = Path(transcript)
        return cls(chat_id, path, (lines or "").strip() or cls._all_lines_of(path))

    @classmethod
    def taken_from(cls, arguments: dict[str, object] | None) -> tuple[ChatPointer | None, dict[str, object]]:
        """The chat a tool call names in its arguments, and the arguments left for the tool itself. A Claude Code chat
        sends only its id, so its transcript is found by that id; a chat whose transcript cannot be found points at
        ``unknown``."""
        remaining = dict(arguments or {})
        chat_id = cls._taken(remaining, _ID_ARGUMENTS)
        transcript = cls._taken(remaining, _TRANSCRIPT_ARGUMENTS)
        lines = cls._taken(remaining, _LINES_ARGUMENTS)
        if not chat_id and not transcript:
            return None, remaining
        transcript = transcript or cls._claude_transcript_of(chat_id) or "unknown"
        return cls.of(chat_id or "unknown", transcript, lines), remaining

    @classmethod
    def current(cls) -> ChatPointer | None:
        """The chat of the tool call being served, or else the chat the environment names (``CDD_CONVERSATION_ID``,
        ``CDD_TRANSCRIPT_PATH``, ``CDD_TRANSCRIPT_LINES``, which hooks and agent runs set)."""
        serving = cls._serving.get()
        if serving is not None:
            return serving
        chat_id = os.environ.get("CDD_CONVERSATION_ID", "") or os.environ.get("CDD_CHAT_ID", "")
        return cls.of(chat_id, os.environ.get("CDD_TRANSCRIPT_PATH", ""), os.environ.get("CDD_TRANSCRIPT_LINES", ""))

    @classmethod
    @contextmanager
    def serving(cls, chat: ChatPointer | None) -> Iterator[None]:
        """Make chat the current chat while one tool call runs, and put back the one before it when the call ends,
        so a call never leaves its chat behind for the next chat's call."""
        token = cls._serving.set(chat)
        try:
            yield
        finally:
            cls._serving.reset(token)

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

    @classmethod
    def in_chat_file(cls, path: Path) -> tuple[ChatPointer, str]:
        """The pointer for a chat saved as a file, and the chat's text. The file may start with ``chat-id:`` and
        ``lines:`` headers and a blank line; without them the file's name is the id and the text is every line."""
        if not path.is_file():
            return cls(path.stem, path, ""), ""
        lines = path.read_text(encoding="utf-8").splitlines()
        chat_id = ""
        line_numbers = ""
        body_start = 0
        for index, line in enumerate(lines):
            if not line.strip():
                body_start = index + 1
                break
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            token = key.strip().lower().replace("_", "-")
            if token in {"chat-id", "conversation-id"}:
                chat_id = value.strip()
            elif token == "lines":
                line_numbers = value.strip()
        else:
            body_start = len(lines)
        body = "\n".join(lines[body_start:]).strip()
        if not line_numbers:
            count = len(body.splitlines()) if body else 1
            line_numbers = f"1-{count}" if count > 1 else "1"
        return cls(chat_id or path.stem, path, line_numbers), body

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
                if (piece := self._event_text(raw[index], index + 1))
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

    @staticmethod
    def _taken(arguments: dict[str, object], names: tuple[str, ...]) -> str:
        found = ""
        for name in names:
            value = str(arguments.pop(name, "") or "").strip()
            found = found or value
        return found

    @staticmethod
    def _all_lines_of(path: Path) -> str:
        if not path.is_file():
            return "1"
        count = len(path.read_text(encoding="utf-8").splitlines()) or 1
        return f"1-{count}" if count > 1 else "1"

    @staticmethod
    def _claude_transcript_of(chat_id: str) -> str:
        """A Claude Code chat's id is its transcript's file name under the Claude projects folder."""
        if not _CHAT_ID.fullmatch(chat_id or ""):
            return ""
        projects = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "projects"
        found = next(projects.glob(f"*/{chat_id}.jsonl"), None) if projects.is_dir() else None
        return str(found) if found else ""

    @staticmethod
    def _event_text(line: str, line_no: int) -> str:
        stripped = line.strip()
        if not stripped:
            return ""
        try:
            event = json.loads(stripped)
        except json.JSONDecodeError:
            return f"L{line_no}: {stripped}"
        role = str(event.get("role") or "event")
        message = event.get("message")
        texts: list[str] = []
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, list):
                texts.extend(
                    str(part.get("text") or "")
                    for part in content
                    if isinstance(part, dict) and part.get("type") == "text"
                )
            elif isinstance(content, str):
                texts.append(content)
        body = "\n".join(texts).strip() or stripped
        return f"L{line_no} [{role}]\n{body}"


# A log line from a chat the server cannot name ends with "no-chat" in place of the chat's id, transcript, and lines.
NO_CHAT = ChatPointer("no-chat")
