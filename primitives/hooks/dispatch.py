"""Dispatch Cursor hook stdin payloads to ``@hook`` handlers on toolsets."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hooks.bootstrap import load
from hooks.hook import Hook

_DEBUG_LOG = Path(__file__).with_suffix(".debug")


def parse_payload(raw: bytes) -> dict[str, Any]:
    text = raw.decode("utf-8-sig")
    while text.startswith("\ufeff"):
        text = text[1:]
    return json.loads(text)


def _debug(msg: str) -> None:
    with open(_DEBUG_LOG, "a", encoding="utf-8") as f:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        f.write(f"{ts} {msg}\n")


def _merge_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    merged: dict[str, Any] = {"permission": "allow"}
    agent_messages: list[str] = []
    user_messages: list[str] = []
    followup_message: str | None = None
    for item in results:
        if not item:
            continue
        if item.get("permission") == "deny":
            merged["permission"] = "deny"
        if item.get("continue") is False:
            merged["continue"] = False
        value = item.get("user_message")
        if value:
            user_messages.append(str(value))
        value = item.get("agent_message")
        if value:
            agent_messages.append(str(value))
        value = item.get("followup_message")
        if value:
            followup_message = str(value)
    if user_messages:
        merged["user_message"] = "\n".join(user_messages)
    if agent_messages:
        merged["agent_message"] = "\n".join(agent_messages)
    if followup_message:
        merged["followup_message"] = followup_message
    return merged


def _matcher_ok(matcher: str | None, payload: dict[str, Any]) -> bool:
    if not matcher:
        return True
    tool_name = str(payload.get("tool_name") or "")
    return re.search(matcher, tool_name) is not None


def dispatch(payload: dict[str, Any]) -> dict[str, Any]:
    event = str(payload.get("hook_event_name") or "")
    conv = payload.get("conversation_id")
    _debug(
        f"EVENT {event!r} conversation_id={conv!r} payload_keys={sorted(payload.keys())}"
    )
    if not event:
        _debug("NO_EVENT merged={}")
        return {"permission": "allow"}

    results: list[dict[str, Any]] = []
    enabled: list[str] = []
    for entry in Hook.bindings_for(event):
        if not _matcher_ok(entry.get("matcher"), payload):
            continue
        owner = entry["owner"]
        method = entry["method"]
        if not Hook.is_enabled(owner, method, event):
            continue
        label = f"{owner.__name__}.{method}"
        enabled.append(label)
        instance = owner()
        handler = getattr(instance, method)
        result = handler(payload)
        results.append(result)
        result_keys = sorted((result or {}).keys())
        _debug(f"HANDLER {label} result_keys={result_keys} result={json.dumps(result or {})}")
    _debug(f"ENABLED {enabled or ['(none)']}")
    merged = _merge_results(results)
    _debug(f"MERGED {json.dumps(merged)}")
    return merged


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    os.chdir(repo_root)
    load()
    raw = sys.stdin.buffer.read()
    _debug(f"ENTRY raw_len={len(raw)} raw={raw[:200]!r}")
    if not raw.strip():
        _debug("empty stdin, allowing")
        print(json.dumps({"permission": "allow"}))
        return
    payload = parse_payload(raw)
    event = str(payload.get("hook_event_name") or "")
    if event == "afterAgentResponse":
        try:
            from hooks.prompt_log.prompt_log import append_log, format_after_agent_response

            append_log(format_after_agent_response(payload))
        except OSError:
            pass
    out = dispatch(payload)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
