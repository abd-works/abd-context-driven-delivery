"""Hook server — run enabled Cursor hooks and return one merged result."""
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _category in ("harness", "tools", "practices", "actions"):
    _entry = str(_REPO_ROOT / _category)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.agent_tools.agent_tools import AgentToolSet, InstallDestination
from installation.hooks.hooks import Hook

logger = logging.getLogger(__name__)


class CursorEvent:
    """Named Cursor hook moment. Identity is the event string."""

    def __init__(self, name: str) -> None:
        self.name = name

    def normalize(self) -> str:
        return Hook.normalize_event(self.name)


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
        additional_context: str | None = None,
    ) -> None:
        self.permission = permission
        self.continue_flag = continue_flag
        self.user_message = user_message
        self.agent_message = agent_message
        self.followup_message = followup_message
        self.additional_context = additional_context

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
            additional_context=_text(raw.get("additional_context")),
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
            self.additional_context,
        )

    @classmethod
    def merged(cls, results: list[HookResult]) -> HookResult:
        permission = "allow"
        continue_flag: bool | None = None
        user_parts: list[str] = []
        agent_parts: list[str] = []
        context_parts: list[str] = []
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
            if item.additional_context:
                context_parts.append(item.additional_context)
            if item.followup_message:
                followup = item.followup_message
        return cls(
            permission,
            continue_flag,
            "\n".join(user_parts) or None,
            "\n".join(agent_parts) or None,
            followup,
            "\n\n".join(context_parts) or None,
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
        if self.additional_context:
            payload["additional_context"] = self.additional_context
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
        *,
        skip: Callable[[str, BaseException], None] | None = None,
    ) -> None:
        self.repo_root = repo_root
        self._skip = skip
        if toolsets is None:
            items: list[Any] = self._refs_from_file()
            if not items:
                items = self._collect_refs()
        else:
            items = list(toolsets)
        self.toolsets: list[Any] = []
        for item in items:
            try:
                loaded = AgentToolSet.load_toolsets([item])
            except Exception as error:
                if self._skip is not None:
                    self._skip(_ref_label(item), error)
                continue
            self.toolsets.extend(loaded)

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
            try:
                tools = toolset.tools_for(InstallDestination.HOOK)
            except Exception as error:
                if self._skip is not None:
                    self._skip(_ref_label(toolset), error)
                continue
            for tool in tools:
                if getattr(tool.callable, "_hook_name", None) != event.name:
                    continue
                handlers.append(HookHandler(tool, event, repo_root))
        return handlers


class HookStandupFailed(Exception):
    """The hook server could not stand up or failed diagnose."""

    def __init__(
        self,
        operation: str,
        server: Any,
        message: str,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message)
        self.operation = operation
        self.server = server
        self.cause = cause


class HookIllegitimateHandler(Exception):
    """One hook handler was skipped so the hook server could finish standup."""

    def __init__(self, tool: str, reason: str, cause: BaseException | None = None) -> None:
        super().__init__(f"{tool}: {reason}")
        self.tool = tool
        self.reason = reason
        self.cause = cause


class HookServer:
    """Cursor process for every hooked event."""

    def __init__(
        self, repo_root: Path, toolsets: list[Any] | None = None
    ) -> None:
        self._repo_root = repo_root
        self.exceptions: list[HookIllegitimateHandler] = []
        self._catalog = HandlerCatalog(toolsets, repo_root, skip=self.skip)

    def skip(self, tool: str, error: BaseException) -> None:
        skipped = (
            error
            if isinstance(error, HookIllegitimateHandler)
            else HookIllegitimateHandler(tool, str(error), error)
        )
        self.exceptions.append(skipped)
        logger.error(
            "hook standup exception: skipped %s: %s",
            skipped.tool,
            skipped.reason,
            exc_info=skipped.cause,
        )

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
            try:
                result = handler.invoke(payload)
            except Exception as error:
                self.skip(label, error)
                continue
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

    def ping(self) -> str:
        return "pong"

    def _event_names(self) -> list[str]:
        names: list[str] = []
        for toolset in self._catalog.toolsets:
            try:
                tools = toolset.tools_for(InstallDestination.HOOK)
            except Exception as error:
                self.skip(_ref_label(toolset), error)
                continue
            for tool in tools:
                event = getattr(tool.callable, "_hook_name", None)
                if event and event not in names:
                    names.append(str(event))
        return names

    def diagnose(self) -> dict[str, Any]:
        reply = self.ping()
        if reply != "pong":
            raise HookStandupFailed("diagnose", self, "hook server ping failed")
        self.dispatch(HookPayload({}))
        exceptions = [
            {"tool": item.tool, "reason": item.reason} for item in self.exceptions
        ]
        return {
            "ok": True,
            "ping": reply,
            "events": self._event_names(),
            "exceptions": exceptions,
            "notice": self.notice(),
        }

    def notice(self) -> str:
        if not self.exceptions:
            return ""
        lines = ["hook standup skipped illegitimate handlers and continued:"]
        for item in self.exceptions:
            lines.append(f"- {item.tool}: {item.reason}")
        return "\n".join(lines)

    def notify_exceptions(self) -> None:
        text = self.notice()
        if text:
            print(text, file=sys.stderr)

    @classmethod
    def refs_from_handlers(cls, handlers: Path | str) -> tuple[str, ...]:
        path = Path(handlers)
        if not path.is_file():
            return ()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return ()
        refs: list[str] = []
        for item in payload.get("handlers") or []:
            ref = item.get("ref")
            if ref and str(ref) not in refs:
                refs.append(str(ref))
        return tuple(refs)

    @classmethod
    def standup(cls, handlers: Path | str, *, repo: Path | str | None = None) -> HookServer:
        resolved = Path(repo).resolve() if repo is not None else Path(__file__).resolve().parents[2]
        refs = cls.refs_from_handlers(handlers)
        try:
            server = cls(resolved, toolsets=list(refs))
        except Exception as error:
            raise HookStandupFailed("standup", None, str(error), error) from error
        server.notify_exceptions()
        return server

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


def _ref_label(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return str(item.get("toolset") or item)
    registration = getattr(item, "registration_name", None)
    if isinstance(registration, str) and registration:
        return registration
    typ = item if isinstance(item, type) else type(item)
    return f"{typ.__module__}:{typ.__name__}"


def main() -> None:
    os.chdir(_REPO_ROOT)
    HookServer(_REPO_ROOT).run()


if __name__ == "__main__":
    main()
