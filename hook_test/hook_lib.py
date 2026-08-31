"""Shared helpers for the hook_test tester scripts.

The tester is invoked once per hook event by Cursor. Each invocation:

1. Reads JSON from stdin (Cursor's hook payload).
2. Records the event to ``hook_test/logs/events.jsonl`` and ``hook_test/logs/pretty.log``.
3. Optionally emits a *visible* notification (permission decision, agent message,
   additional_context, followup_message, stderr line) so the running Cloud Agent
   can actually observe that a hook fired.

Design rules:

* **Never block real work.** The default response for every hook is passive:
  ``permission: "allow"`` / ``continue: true`` / no follow-up. Visible
  notifications only fire when the payload contains an explicit marker such as
  ``HOOK_TEST_MARKER_DENY``, ``HOOK_TEST_MARKER_CTX``, or when a special sentinel
  file is edited.
* **Fail open.** Any exception is swallowed and we emit a permissive response.
  The hook config uses the default ``failClosed: false`` so even if the process
  crashes the agent keeps going.
* **Small.** The log file rotates when it exceeds a soft cap so a long-running
  agent doesn't fill the disk.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from pathlib import Path
from typing import Any

HOOK_TEST_DIR = Path(__file__).resolve().parent
LOG_DIR = HOOK_TEST_DIR / "logs"
EVENTS_PATH = LOG_DIR / "events.jsonl"
PRETTY_PATH = LOG_DIR / "pretty.log"
MAX_LOG_BYTES = 512 * 1024

MARKER_DENY = "HOOK_TEST_MARKER_DENY"
MARKER_CTX = "HOOK_TEST_MARKER_CTX"
MARKER_FOLLOWUP = "HOOK_TEST_MARKER_FOLLOWUP"
MARKER_STDERR = "HOOK_TEST_MARKER_STDERR"
SENTINEL_EDIT_NAME = "hook_test_sentinel.txt"


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="milliseconds")


def _rotate_if_needed(path: Path) -> None:
    try:
        if path.exists() and path.stat().st_size > MAX_LOG_BYTES:
            backup = path.with_suffix(path.suffix + ".1")
            if backup.exists():
                backup.unlink()
            path.rename(backup)
    except OSError:
        pass


def _write_event(record: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    _rotate_if_needed(EVENTS_PATH)
    _rotate_if_needed(PRETTY_PATH)
    try:
        with EVENTS_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    except OSError:
        pass
    try:
        summary = record.get("summary") or ""
        line = f"[{record['ts']}] {record['hook']:<22} {summary}\n"
        with PRETTY_PATH.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError:
        pass


def read_payload() -> dict[str, Any]:
    """Read the hook payload JSON from stdin. Returns an empty dict on failure."""
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return {"__raw__": raw[:500]}


def build_summary(hook: str, payload: dict[str, Any]) -> str:
    """One-line human-readable summary for the pretty log."""
    if hook in {"beforeShellExecution", "afterShellExecution"}:
        cmd = str(payload.get("command", ""))[:120]
        return f"cmd={cmd!r}"
    if hook in {"beforeReadFile", "afterFileEdit"}:
        return f"file={payload.get('file_path')!r}"
    if hook in {"preToolUse", "postToolUse", "postToolUseFailure"}:
        return f"tool={payload.get('tool_name')!r}"
    if hook in {"subagentStart", "subagentStop"}:
        return f"subagent={payload.get('subagent_type')!r} status={payload.get('status', '-')}"
    if hook == "beforeSubmitPrompt":
        prompt = str(payload.get("prompt", ""))[:120]
        return f"prompt={prompt!r}"
    if hook == "preCompact":
        return f"tokens={payload.get('context_tokens')} pct={payload.get('context_usage_percent')}"
    if hook == "stop":
        return f"status={payload.get('status')!r} loop={payload.get('loop_count')}"
    if hook == "afterAgentResponse":
        return f"text={str(payload.get('text', ''))[:80]!r}"
    if hook == "afterAgentThought":
        return f"duration_ms={payload.get('duration_ms')}"
    return ""


def payload_haystack(payload: dict[str, Any]) -> str:
    """Concatenated searchable text from the fields most likely to contain markers."""
    parts: list[str] = []
    for key in ("command", "prompt", "text", "task", "file_path", "output"):
        val = payload.get(key)
        if isinstance(val, str):
            parts.append(val)
    edits = payload.get("edits")
    if isinstance(edits, list):
        for edit in edits:
            if isinstance(edit, dict):
                for k in ("old_string", "new_string"):
                    v = edit.get(k)
                    if isinstance(v, str):
                        parts.append(v)
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        for v in tool_input.values():
            if isinstance(v, str):
                parts.append(v)
    elif isinstance(tool_input, str):
        parts.append(tool_input)
    return "\n".join(parts)


def emit(response: dict[str, Any]) -> None:
    """Print JSON response to stdout for Cursor to consume."""
    sys.stdout.write(json.dumps(response, ensure_ascii=False))
    sys.stdout.write("\n")
    sys.stdout.flush()


def note_stderr(message: str) -> None:
    """Write to stderr so the message can appear in the Cursor Hooks output channel."""
    try:
        sys.stderr.write(f"[hook_test] {message}\n")
        sys.stderr.flush()
    except OSError:
        pass


def record(hook: str, payload: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """Log the event and return the record so the caller can enrich it."""
    rec = {
        "ts": _now_iso(),
        "hook": hook,
        "pid": os.getpid(),
        "conversation_id": payload.get("conversation_id"),
        "generation_id": payload.get("generation_id"),
        "cursor_version": payload.get("cursor_version"),
        "workspace_roots": payload.get("workspace_roots"),
        "summary": build_summary(hook, payload),
        "payload_keys": sorted(payload.keys()),
        "payload": _truncate_payload(payload),
    }
    if extra:
        rec.update(extra)
    _write_event(rec)
    return rec


def _truncate_payload(payload: dict[str, Any], limit: int = 2000) -> dict[str, Any]:
    """Truncate long string fields so the log stays readable."""
    out: dict[str, Any] = {}
    for k, v in payload.items():
        if isinstance(v, str) and len(v) > limit:
            out[k] = v[:limit] + f"... <truncated {len(v) - limit} chars>"
        else:
            out[k] = v
    return out
