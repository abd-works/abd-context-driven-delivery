"""Hook server — run enabled Cursor hooks and return one merged result."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _category in ("harness", "tools"):
    _entry = str(_REPO_ROOT / _category)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.agent_tools.agent_tools import AgentToolSet, InstallDestination
from installation.hooks.hooks import hook


class CursorEvent:
    """Named Cursor hook moment. Identity is the event string."""

    def __init__(self, name: str) -> None:
        self.name = name

    def normalize(self) -> str:
        return hook.normalize_event(self.name)


class HookPayload:
    """Cursor stdin JSON for one firing."""

    def __init__(self, fields: dict[str, Any]) -> None:
        self._fields = dict(fields)

    @classmethod
    def from_stdin(cls, raw: bytes) -> HookPayload:
        text = raw.decode("utf-8-sig")
        while text.startswith("\ufeff"):
            text = text[1:]
        return cls(json.loads(text))

    @property
    def hook_event_name(self) -> str:
        return str(self._fields.get("hook_event_name") or "")

    @property
    def conversation_id(self) -> str:
        return str(self._fields.get("conversation_id") or "")

    def as_dict(self) -> dict[str, Any]:
        return dict(self._fields)


class HookResult:
    """Fields Cursor reads back from the hook process."""

    def __init__(
        self,
        permission: str = "allow",
        continue_flag: bool | None = None,
        user_message: str | None = None,
        agent_message: str | None = None,
        followup_message: str | None = None,
    ) -> None:
        self.permission = permission
        self.continue_flag = continue_flag
        self.user_message = user_message
        self.agent_message = agent_message
        self.followup_message = followup_message

    @classmethod
    def from_handler(cls, raw: dict[str, Any] | None) -> HookResult:
        if not raw:
            return cls()
        continue_flag = False if raw.get("continue") is False else None
        return cls(
            permission=str(raw.get("permission") or "allow"),
            continue_flag=continue_flag,
            user_message=_text(raw.get("user_message")),
            agent_message=_text(raw.get("agent_message")),
            followup_message=_text(raw.get("followup_message")),
        )

    def with_description(self, description: str) -> HookResult:
        text = description.strip()
        if not text:
            return self
        existing = (self.agent_message or "").strip()
        if existing == text:
            return self
        if existing:
            text = f"{text}\n{existing}"
        return HookResult(
            self.permission,
            self.continue_flag,
            self.user_message,
            text,
            self.followup_message,
        )

    @classmethod
    def merged(cls, results: list[HookResult]) -> HookResult:
        permission = "allow"
        continue_flag: bool | None = None
        user_parts: list[str] = []
        agent_parts: list[str] = []
        followup: str | None = None
        for item in results:
            if item.permission == "deny":
                permission = "deny"
            if item.continue_flag is False:
                continue_flag = False
            if item.user_message:
                user_parts.append(item.user_message)
            if item.agent_message:
                agent_parts.append(item.agent_message)
            if item.followup_message:
                followup = item.followup_message
        return cls(
            permission,
            continue_flag,
            "\n".join(user_parts) or None,
            "\n".join(agent_parts) or None,
            followup,
        )

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"permission": self.permission}
        if self.continue_flag is False:
            payload["continue"] = False
        if self.user_message:
            payload["user_message"] = self.user_message
        if self.agent_message:
            payload["agent_message"] = self.agent_message
        if self.followup_message:
            payload["followup_message"] = self.followup_message
        return payload


class HookHandler:
    """One marked operation that may run for an event."""

    def __init__(self, tool: Any, event: CursorEvent, repo_root: Path) -> None:
        self.tool = tool
        self.event = event
        self.operation = tool.name
        self.owner = type(tool.toolset)

    def is_enabled(self) -> bool:
        return not bool(getattr(self.owner, "_hooks_disabled", False))

    def invoke(self, payload: HookPayload) -> HookResult:
        raw = getattr(self.tool.toolset, self.operation)(payload.as_dict())
        return HookResult.from_handler(raw).with_description(self.tool.docstring)


class HandlerCatalog:
    """Loaded AgentToolSets. Hook operations come from ``toolset.tools``."""

    def __init__(
        self,
        toolsets: list[Any] | None = None,
        repo_root: Path | None = None,
    ) -> None:
        self.repo_root = repo_root
        skip_errors = False
        if toolsets is None:
            toolsets = self._refs_from_file()
            if not toolsets:
                toolsets = self._collect_refs()
                skip_errors = True
        self.toolsets = AgentToolSet.load_toolsets(toolsets, skip_errors=skip_errors)

    def _refs_from_file(self) -> list[str]:
        handlers_path = (self.repo_root or Path()) / ".cursor" / "hook-handlers.json"
        if not handlers_path.is_file():
            return []
        try:
            payload = json.loads(handlers_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return [
            str(item["ref"])
            for item in payload.get("handlers") or []
            if item.get("ref")
        ]

    def _collect_refs(self) -> list[str]:
        from installation.installer import Installer

        return list(Installer(repo=self.repo_root).collect_toolsets())

    def for_event(self, event: CursorEvent) -> list[HookHandler]:
        handlers: list[HookHandler] = []
        repo_root = self.repo_root or Path()
        for toolset in self.toolsets:
            for tool in toolset.tools_for(InstallDestination.HOOK):
                if getattr(tool.callable, "_hook_name", None) != event.name:
                    continue
                handlers.append(HookHandler(tool, event, repo_root))
        return handlers


class HookServer:
    """Cursor process for every hooked event."""

    def __init__(
        self, repo_root: Path, toolsets: list[Any] | None = None
    ) -> None:
        self._repo_root = repo_root
        self._catalog = HandlerCatalog(toolsets, repo_root)

    def dispatch(self, payload: HookPayload) -> HookResult:
        event = CursorEvent(payload.hook_event_name)
        self._append_debug(
            f"EVENT {event.name!r} conversation_id={payload.conversation_id!r} "
            f"payload_keys={sorted(payload.as_dict().keys())}"
        )
        if not event.name:
            self._append_debug("NO_EVENT merged={}")
            return HookResult()
        results = self._invoke_enabled(event, payload)
        merged = HookResult.merged(results)
        self._append_debug(f"MERGED {json.dumps(merged.as_dict())}")
        return merged

    def _invoke_enabled(
        self, event: CursorEvent, payload: HookPayload
    ) -> list[HookResult]:
        enabled: list[str] = []
        results: list[HookResult] = []
        for handler in self._catalog.for_event(event):
            if not handler.is_enabled():
                continue
            label = f"{handler.owner.__name__}.{handler.operation}"
            enabled.append(label)
            result = handler.invoke(payload)
            results.append(result)
            self._append_debug(f"HANDLER {label} result={json.dumps(result.as_dict())}")
        self._append_debug(f"ENABLED {enabled or ['(none)']}")
        return results

    def run(self) -> None:
        from installation.hooks.session_logs import ensure_default_session

        ensure_default_session(self._repo_root)
        raw = sys.stdin.buffer.read()
        if not raw.strip():
            print(json.dumps(HookResult().as_dict()))
            return
        try:
            payload = HookPayload.from_stdin(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(json.dumps(HookResult().as_dict()))
            return
        print(json.dumps(self.dispatch(payload).as_dict()))

    def _append_debug(self, message: str) -> None:
        from installation.hooks.session_logs import session_log_path

        path = session_log_path(self._repo_root, "dispatch.debug")
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(path, "a", encoding="utf-8") as log:
            log.write(f"{stamp} {message}\n")


def _text(value: Any) -> str | None:
    if not value:
        return None
    return str(value)


def main() -> None:
    os.chdir(_REPO_ROOT)
    HookServer(_REPO_ROOT).run()


if __name__ == "__main__":
    main()
