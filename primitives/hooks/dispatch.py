"""Dispatch Cursor hook stdin payloads to ``@hook`` handlers on toolsets."""

from __future__ import annotations

import json
import re
import sys
from typing import Any

from hooks.bootstrap import load
from hooks.hook import Hook


def parse_payload(raw: bytes) -> dict[str, Any]:
    text = raw.decode("utf-8-sig")
    while text.startswith("\ufeff"):
        text = text[1:]
    return json.loads(text)


def _merge_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    merged: dict[str, Any] = {"permission": "allow"}
    messages: list[str] = []
    for item in results:
        if not item:
            continue
        if item.get("permission") == "deny":
            merged["permission"] = "deny"
        for key in ("agent_message", "user_message"):
            value = item.get(key)
            if value:
                messages.append(str(value))
    if messages:
        merged["agent_message"] = "\n".join(messages)
    return merged


def _matcher_ok(matcher: str | None, payload: dict[str, Any]) -> bool:
    if not matcher:
        return True
    tool_name = str(payload.get("tool_name") or "")
    return re.search(matcher, tool_name) is not None


def dispatch(payload: dict[str, Any]) -> dict[str, Any]:
    event = str(payload.get("hook_event_name") or "")
    if not event:
        return {"permission": "allow"}

    results: list[dict[str, Any]] = []
    for entry in Hook.bindings_for(event):
        if not _matcher_ok(entry.get("matcher"), payload):
            continue
        owner = entry["owner"]
        method = entry["method"]
        if not Hook.is_enabled(owner, method, event):
            continue
        instance = owner()
        handler = getattr(instance, method)
        results.append(handler(payload))
    return _merge_results(results)


def main() -> None:
    load()
    raw = sys.stdin.buffer.read()
    if not raw.strip():
        print(json.dumps({"permission": "allow"}))
        return
    payload = parse_payload(raw)
    print(json.dumps(dispatch(payload)))


if __name__ == "__main__":
    main()
