"""Parse session-log chat pointers and read transcript slices."""

from __future__ import annotations

import json
import re
from pathlib import Path

_CHAT_POINTER = re.compile(
    r" ([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}) (.+)$",
    re.IGNORECASE,
)
_LINE_RANGE = re.compile(r"^\d+(?:-\d+)?$")


def parse_line_range(spec: str) -> tuple[int, int]:
    """Return inclusive 1-based start and end line numbers."""
    token = (spec or "").strip()
    if "-" in token:
        left, right = token.split("-", 1)
        start = max(1, int(left))
        end = max(start, int(right))
        return start, end
    line = max(1, int(token or "1"))
    return line, line


def parse_line_chat_pointer(line: str) -> tuple[str, Path, str] | None:
    """Extract chat id, transcript path, and line range from a session.log line."""
    if " no-chat " in line:
        return None
    match = _CHAT_POINTER.search(line)
    if not match:
        return None
    chat_id = match.group(1)
    tail = match.group(2).strip()
    path_text, line_numbers = tail.rsplit(" ", 1)
    if not _LINE_RANGE.fullmatch(line_numbers):
        return None
    return chat_id, Path(path_text), line_numbers


def _format_jsonl_line(line: str, line_no: int) -> str:
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
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    texts.append(str(part.get("text") or ""))
        elif isinstance(content, str):
            texts.append(content)
    body = "\n".join(texts).strip()
    if not body:
        body = stripped
    return f"L{line_no} [{role}]\n{body}"


def read_transcript_slice(path: Path, line_numbers: str) -> list[str]:
    """Read formatted transcript lines for a pointer's line range."""
    if not path.is_file():
        return [f"(missing transcript: {path})"]
    start, end = parse_line_range(line_numbers)
    raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if path.suffix.lower() == ".jsonl":
        formatted: list[str] = []
        for index in range(start - 1, min(end, len(raw))):
            piece = _format_jsonl_line(raw[index], index + 1)
            if piece:
                formatted.append(piece)
        return formatted or [f"(empty transcript slice {line_numbers} in {path})"]
    slice_lines = raw[start - 1 : end]
    return slice_lines or [f"(empty transcript slice {line_numbers} in {path})"]


def expand_log_lines(lines: list[str]) -> str:
    """Interleave session.log lines with transcript slices referenced on each line."""
    parts: list[str] = []
    seen: set[tuple[str, str]] = set()
    for line in lines:
        parts.append(line)
        pointer = parse_line_chat_pointer(line)
        if pointer is None:
            continue
        chat_id, path, line_numbers = pointer
        key = (str(path.resolve()) if path.exists() else str(path), line_numbers)
        if key in seen:
            parts.append(f"    (chat {chat_id} {line_numbers} — see above)")
            continue
        seen.add(key)
        parts.append(f"--- chat {chat_id} {path} {line_numbers} ---")
        parts.extend(read_transcript_slice(path, line_numbers))
    return "\n".join(parts)
