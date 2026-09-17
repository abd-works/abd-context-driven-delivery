"""Cursor hook runtime — stdin JSON to marked ``@hook`` operations."""

from __future__ import annotations

import importlib
import inspect
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HANDLERS_JSON = _REPO_ROOT / ".cursor" / "hook-handlers.json"
_DEFAULT_HOST_REFS = (
    "workspace.workspace:Turn",
    "primitives.hooks.prompt_log.prompt_log:PromptLog",
    "primitives.hooks.skill_inject:SkillInject",
    "primitives.hooks.prompt_echo.prompt_echo:PromptEcho",
)


def _hook_debug_path(filename: str) -> Path:
    from hooks.session_logs import session_log_path

    return session_log_path(_REPO_ROOT, filename)


for _category in ("primitives", "utilities", "primitives/hooks"):
    _entry = str(_REPO_ROOT / _category)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from installer.marks import normalize_event


def toggle_flag(owner: type, method: str, event: str) -> Path:
    slug = owner.__name__.lower()
    norm = normalize_event(event)
    return _REPO_ROOT / ".context" / "hooks" / slug / f"{method}_{norm}.enabled"


def disabled_flag(owner: type, method: str, event: str) -> Path:
    return toggle_flag(owner, method, event).with_suffix(".disabled")


def is_enabled(owner: type, method: str, event: str) -> bool:
    member = getattr(owner, method, None)
    always = bool(getattr(member, "_hook_always", False))
    if always:
        return not disabled_flag(owner, method, event).is_file()
    return toggle_flag(owner, method, event).is_file()


def set_enabled(owner: type, method: str, event: str, *, enabled: bool) -> Path:
    path = toggle_flag(owner, method, event)
    path.parent.mkdir(parents=True, exist_ok=True)
    if enabled:
        path.write_text("", encoding="utf-8")
    elif path.is_file():
        path.unlink()
    return path


def _load_ref(ref: str) -> type | None:
    module_name, _, class_name = ref.partition(":")
    if not module_name or not class_name:
        return None
    try:
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except (ImportError, AttributeError):
        return None


def load_hosts(hosts: list[type] | None = None) -> list[type]:
    if hosts is not None:
        return hosts
    refs: list[str] = []
    if _HANDLERS_JSON.is_file():
        try:
            payload = json.loads(_HANDLERS_JSON.read_text(encoding="utf-8"))
            refs = [
                str(item["ref"])
                for item in payload.get("handlers") or []
                if item.get("ref")
            ]
        except (OSError, json.JSONDecodeError):
            refs = []
    if not refs:
        refs = list(_DEFAULT_HOST_REFS)
    loaded: list[type] = []
    seen: set[str] = set()
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        cls = _load_ref(ref)
        if cls is not None:
            loaded.append(cls)
    return loaded


def _hook_methods(owner: type, event: str) -> list[str]:
    names: list[str] = []
    for name, member in inspect.getmembers(owner, predicate=inspect.isfunction):
        if not getattr(member, "_hook", False):
            continue
        if getattr(member, "_hook_name", None) != event:
            continue
        names.append(name)
    return names


def parse_payload(raw: bytes) -> dict[str, Any]:
    text = raw.decode("utf-8-sig")
    while text.startswith("\ufeff"):
        text = text[1:]
    return json.loads(text)


def _dispatch_debug(msg: str) -> None:
    with open(_hook_debug_path("dispatch.debug"), "a", encoding="utf-8") as f:
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


def dispatch(
    payload: dict[str, Any],
    hosts: list[type] | None = None,
) -> dict[str, Any]:
    event = str(payload.get("hook_event_name") or "")
    conv = payload.get("conversation_id")
    _dispatch_debug(
        f"EVENT {event!r} conversation_id={conv!r} payload_keys={sorted(payload.keys())}"
    )
    if not event:
        _dispatch_debug("NO_EVENT merged={}")
        return {"permission": "allow"}

    results: list[dict[str, Any]] = []
    enabled: list[str] = []
    for owner in load_hosts(hosts):
        for method in _hook_methods(owner, event):
            if not is_enabled(owner, method, event):
                continue
            label = f"{owner.__name__}.{method}"
            enabled.append(label)
            instance = owner()
            handler = getattr(instance, method)
            result = handler(payload)
            results.append(result)
            result_keys = sorted((result or {}).keys())
            _dispatch_debug(
                f"HANDLER {label} result_keys={result_keys} result={json.dumps(result or {})}"
            )
    _dispatch_debug(f"ENABLED {enabled or ['(none)']}")
    merged = _merge_results(results)
    _dispatch_debug(f"MERGED {json.dumps(merged)}")
    return merged


def main() -> None:
    os.chdir(_REPO_ROOT)
    from hooks.session_logs import ensure_default_session

    ensure_default_session(_REPO_ROOT)
    raw = sys.stdin.buffer.read()
    if not raw.strip():
        print(json.dumps({"permission": "allow"}))
        return
    try:
        payload = parse_payload(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        print(json.dumps({"permission": "allow"}))
        return
    print(json.dumps(dispatch(payload)))


if __name__ == "__main__":
    main()
