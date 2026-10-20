"""Chat id and transcript pointer for mandatory session log lines."""

from __future__ import annotations

import os
from contextvars import ContextVar
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from space.session.session import Session

_chat_id: ContextVar[str | None] = ContextVar("cdd_chat_id", default=None)
_transcript_path: ContextVar[str | None] = ContextVar("cdd_transcript_path", default=None)
_line_numbers: ContextVar[str | None] = ContextVar("cdd_transcript_lines", default=None)


def set_chat_context(
    chat_id: str,
    transcript_path: str | Path,
    line_numbers: str = "",
) -> None:
    _chat_id.set((chat_id or "").strip() or None)
    _transcript_path.set(str(transcript_path).strip() or None)
    _line_numbers.set((line_numbers or "").strip() or None)


def clear_chat_context() -> None:
    _chat_id.set(None)
    _transcript_path.set(None)
    _line_numbers.set(None)


def chat_from_environ() -> tuple[str, Path, str] | None:
    chat_id = (
        (_chat_id.get() or "")
        or os.environ.get("CDD_CONVERSATION_ID", "")
        or os.environ.get("CDD_CHAT_ID", "")
    ).strip()
    transcript = (_transcript_path.get() or "") or os.environ.get("CDD_TRANSCRIPT_PATH", "")
    transcript = transcript.strip()
    if not chat_id or not transcript:
        return None
    path = Path(transcript)
    lines = (_line_numbers.get() or "") or os.environ.get("CDD_TRANSCRIPT_LINES", "")
    lines = lines.strip()
    if not lines and path.is_file():
        count = len(path.read_text(encoding="utf-8").splitlines()) or 1
        lines = f"1-{count}" if count > 1 else "1"
    if not lines:
        lines = "1"
    return chat_id, path, lines


MISSING_CHAT_DETAIL = (
    "session log missing chat id and transcript path "
    "(CDD_CONVERSATION_ID and CDD_TRANSCRIPT_PATH, or set_chat_context / note_chat)"
)


def apply_chat_context(session: Session) -> bool:
    """Bind chat metadata on the session before writing a log line."""
    resolved = chat_from_environ()
    if resolved is None:
        return False
    chat_id, path, lines = resolved
    session.note_chat(chat_id, path, lines)
    return True


def pop_chat_fields(arguments: dict[str, object] | None) -> dict[str, object]:
    """Remove chat metadata from MCP tool arguments before invoking the tool."""
    args = dict(arguments or {})
    chat_id = str(args.pop("conversation_id", "") or args.pop("_conversation_id", "") or "").strip()
    transcript = str(
        args.pop("transcript_path", "")
        or args.pop("agent_transcript_path", "")
        or args.pop("_transcript_path", "")
        or ""
    ).strip()
    lines = str(args.pop("transcript_lines", "") or args.pop("_transcript_lines", "") or "").strip()
    if chat_id or transcript:
        set_chat_context(chat_id or "unknown", transcript or "unknown", lines)
    return args
