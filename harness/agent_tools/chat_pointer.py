"""The chat a tool call came from: the chat's id, its transcript file, and the transcript lines the call covers. A
session.log line ends with it, so the chat's words can be read back under the line."""

from __future__ import annotations

import json
import os
import re
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
    """Which chat a tool call, and the session.log line it writes, came from, so ``read_loop`` can put that chat's words
    back under the line. Each *ToolCall* carries the chat it came from.

    The pointer is written as ``{id} {transcript} {lines}``: the chat's id, the path of its transcript, and the range
    of transcript lines, such as ``1-40``, that the line covers. A chat the server cannot name is written ``no-chat``.
    """

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
        if not transcript:
            found = cls.from_claude_chat(chat_id)
            transcript = str(found.transcript) if found is not None else "unknown"
        return cls.of(chat_id or "unknown", transcript, lines), remaining

    @classmethod
    def from_claude_chat(cls, chat_id: str) -> ChatPointer | None:
        """A Claude Code chat's pointer, found by its id alone: its transcript is the file named for that id under the
        Claude projects folder, in the folder of the project the chat started in. None when no such transcript is there."""
        if not _CHAT_ID.fullmatch(chat_id or ""):
            return None
        projects = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "projects"
        found = next(projects.glob(f"*/{chat_id}.jsonl"), None) if projects.is_dir() else None
        return cls.of(chat_id, found) if found is not None else None

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

    @staticmethod
    def _lines_of(body: str) -> str:
        count = len(body.splitlines()) if body else 1
        return f"1-{count}" if count > 1 else "1"

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

    @classmethod
    def _all_lines_of(cls, path: Path) -> str:
        return cls._lines_of(path.read_text(encoding="utf-8")) if path.is_file() else "1"

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
