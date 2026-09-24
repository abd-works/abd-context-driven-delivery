"""Hook server — run enabled Cursor hooks and return one merged result."""
from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_READY_WAIT_SECONDS = 90
_READY_POLL_SECONDS = 0.2

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _category in ("tools", "practices", "actions"):
    _entry = str(_REPO_ROOT / _category)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.agent_tools.agent_tools import AgentToolSet, InstallDestination
from installation.installer import Installer
from harness.hooks.hooks import Hook

Installer(repo=_REPO_ROOT).ensure_import_path()

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
        user_message: Any = None,
        agent_message: Any = None,
        followup_message: Any = None,
        additional_context: Any = None,
    ) -> None:
        self.permission = permission
        self.continue_flag = continue_flag
        self.user_message = self._optional_text(user_message)
        self.agent_message = self._optional_text(agent_message)
        self.followup_message = self._optional_text(followup_message)
        self.additional_context = self._optional_text(additional_context)

    def _optional_text(self, value: Any) -> str | None:
        if not value:
            return None
        return str(value)

    @classmethod
    def from_handler(cls, raw: dict[str, Any] | None) -> HookResult:
        if not raw:
            return cls()
        continue_flag = False if raw.get("continue") is False else None
        return cls(
            permission=str(raw.get("permission") or "allow"),
            continue_flag=continue_flag,
            user_message=raw.get("user_message"),
            agent_message=raw.get("agent_message"),
            followup_message=raw.get("followup_message"),
            additional_context=raw.get("additional_context"),
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

    def merge(self, other: HookResult) -> HookResult:
        permission = "deny" if "deny" in (self.permission, other.permission) else "allow"
        continue_flag = False if False in (self.continue_flag, other.continue_flag) else None
        return HookResult(
            permission,
            continue_flag,
            self._join_lines(self.user_message, other.user_message),
            self._join_lines(self.agent_message, other.agent_message),
            other.followup_message or self.followup_message,
            self._join_unique_context(other),
        )

    def _join_lines(self, first: str | None, second: str | None) -> str | None:
        parts = [part for part in (first, second) if part]
        return "\n".join(parts) or None

    def _join_unique_context(self, other: HookResult) -> str | None:
        parts: list[str] = []
        for item in (self.additional_context, other.additional_context):
            if item and item not in parts:
                parts.append(item)
        return "\n\n".join(parts) or None

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
        toolset = self.tool.toolset
        operation = self._bound_operation(toolset)
        raw = operation(payload.as_dict())
        result = HookResult.from_handler(raw)
        if result.additional_context or not raw:
            return result
        return result.with_description(self.tool.docstring)

    def _bound_operation(self, toolset: Any) -> Any:
        if self.operation == "inject_rules":
            rules = getattr(toolset, "rules", None)
            bound = getattr(rules, "inject_rules", None)
            if bound is not None:
                return bound
        return getattr(toolset, self.operation, None) or self.tool.callable


class HandlerCatalog:
    """Loaded AgentToolSets. Hook operations come from ``toolset.tools``."""

    def __init__(
        self,
        toolsets: list[Any] | None = None,
        repo_root: Path | None = None,
        *,
        handlers: Path | str | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.failures: list[tuple[str, BaseException]] = []
        self.toolsets: list[Any] = []
        self._load_items(self._source_items(toolsets, handlers))

    def _source_items(
        self, toolsets: list[Any] | None, handlers: Path | str | None
    ) -> list[Any]:
        if handlers is not None:
            return list(self.refs_from_handlers(handlers))
        if toolsets is None:
            return self._refs_from_file() or self._collect_refs()
        return list(toolsets)

    def _load_items(self, items: list[Any]) -> None:
        for item in items:
            try:
                loaded = AgentToolSet.from_items([item])
            except Exception as error:
                self.failures.append((self.ref_label(item), error))
                continue
            self._append_loaded(loaded)

    def _append_loaded(self, loaded: list[Any]) -> None:
        for instance in loaded:
            if type(instance).__name__ in {"RulesCollection", "FidelityGuidance"}:
                continue
            self.toolsets.append(instance)

    def refs_from_handlers(self, handlers: Path | str) -> tuple[str, ...]:
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

    def ref_label(self, item: Any) -> str:
        if isinstance(item, str):
            return item
        if isinstance(item, dict):
            return str(item.get("toolset") or item)
        registration = getattr(item, "registration_name", None)
        if isinstance(registration, str) and registration:
            return registration
        typ = item if isinstance(item, type) else type(item)
        return f"{typ.__module__}:{typ.__name__}"

    def _refs_from_file(self) -> list[str]:
        return list(self.refs_from_handlers((self.repo_root or Path()) / ".cursor" / "hook-handlers.json"))

    def _collect_refs(self) -> list[str]:
        from installation.installer import Installer

        return list(Installer(repo=self.repo_root).collect_toolsets())

    def for_event(self, event: CursorEvent) -> list[HookHandler]:
        handlers: list[HookHandler] = []
        seen: set[tuple[str, str]] = set()
        repo_root = self.repo_root or Path()
        for toolset in self.toolsets:
            try:
                tools = toolset.tools_for(InstallDestination.HOOK)
            except Exception as error:
                self.failures.append((self.ref_label(toolset), error))
                continue
            for tool in tools:
                if getattr(tool.callable, "_hook_name", None) != event.name:
                    continue
                key = (type(toolset).__name__, tool.name)
                if key in seen:
                    continue
                seen.add(key)
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
    """Long-lived daemon that holds one Session across Cursor hook runs."""

    def __init__(
        self,
        repo_root: Path,
        catalog: HandlerCatalog | None = None,
        *,
        host: str | None = None,
        port: int | None = None,
    ) -> None:
        self._repo_root = repo_root
        self.exceptions: list[HookIllegitimateHandler] = []
        self._host = host
        self._port = port
        self._catalog = catalog
        self._session = None
        self._payload: HookPayload | None = None
        self._injected: dict[str, list[str]] = {"practices": [], "fidelities": []}
        if catalog is not None:
            self._absorb_catalog_failures()

    @classmethod
    def state_path(cls, repo: Path) -> Path:
        return Path(repo).resolve() / ".cursor" / "hook-server.json"

    @classmethod
    def ensure(cls, repo: Path) -> HookServer:
        path = cls.state_path(repo)
        connected = cls._connect(repo, path)
        if connected is not None:
            return connected
        cls._spawn(repo, path)
        connected = cls(repo)._wait_until_connected(path)
        if connected is None:
            raise HookStandupFailed(
                "ensure", None, "hook server daemon did not become ready"
            )
        return connected

    @classmethod
    def _connect(cls, repo: Path, path: Path) -> HookServer | None:
        from harness.hooks.hook_daemon import HookDaemon

        address = HookDaemon().live_address(path)
        if address is None:
            return None
        host, port, _pid = address
        return cls(repo, host=host, port=port)

    def _wait_until_connected(self, path: Path) -> HookServer | None:
        attempts = int(_READY_WAIT_SECONDS / _READY_POLL_SECONDS)
        for _ in range(attempts):
            connected = type(self)._connect(self._repo_root, path)
            if connected is not None:
                return connected
            time.sleep(_READY_POLL_SECONDS)
        return None

    @classmethod
    def _spawn(cls, repo: Path, path: Path) -> None:
        from harness.hooks.hook_daemon import HookDaemon

        HookDaemon().spawn(repo, path)

    def _absorb_catalog_failures(self) -> None:
        if self._catalog is None:
            return
        for tool, error in self._catalog.failures:
            self.skip(tool, error)
        self._catalog.failures.clear()

    @property
    def session(self):
        if self._session is None:
            from harness.session import Session

            self._session = Session()
        return self._session

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
        self._payload = payload
        self._injected = {"practices": [], "fidelities": []}
        event = CursorEvent(payload.hook_event_name)
        fields = payload.as_dict()
        raw = fields.get("tool_input") or {}
        path = ""
        if isinstance(raw, dict):
            path = str(raw.get("path") or raw.get("file_path") or "")
        self._append_debug(
            f"EVENT {event.name!r} tool={fields.get('tool_name')!r} path={path!r} "
            f"conversation_id={payload.conversation_id!r} "
            f"payload_keys={sorted(fields.keys())}"
        )
        if not event.name:
            self._append_debug("NO_EVENT merged={}")
            return HookResult()
        results = self._invoke_enabled(event, payload)
        merged = HookResult()
        for item in results:
            merged = merged.merge(item)
        merged = self._merge_work_session(merged)
        self._append_debug(f"MERGED {json.dumps(merged.as_dict())}")
        return merged

    def _invoke_enabled(
        self, event: CursorEvent, payload: HookPayload
    ) -> list[HookResult]:
        enabled: list[str] = []
        results: list[HookResult] = []
        if self._catalog is None:
            return results
        for handler in self._catalog.for_event(event):
            self._absorb_catalog_failures()
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
            self._record_injected(handler, result)
            self._append_debug(f"HANDLER {label} result={json.dumps(result.as_dict())}")
        self._absorb_catalog_failures()
        self._append_debug(f"ENABLED {enabled or ['(none)']}")
        return results

    def handle_stdin(self, raw: bytes) -> HookResult:
        if self._port is not None:
            from harness.hooks.hook_daemon import HookDaemon

            return HookResult.from_handler(
                HookDaemon(self._host or "127.0.0.1", self._port).call_handle_stdin(raw)
            )
        from harness.hooks.session_logs import SessionLogs

        SessionLogs(self._repo_root).ensure_default_session()
        if not raw.strip():
            return HookResult()
        try:
            payload = HookPayload.from_stdin(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return HookResult()
        result = self.dispatch(payload)
        self._publish_context(result)
        self._write_last_chat_injected(result)
        if payload.hook_event_name == "stop":
            followup = self._consume_followup()
            if followup:
                result.followup_message = followup
        return result

    def run(self) -> None:
        print(json.dumps(self.handle_stdin(sys.stdin.buffer.read()).as_dict()))

    def _record_injected(self, handler: HookHandler, result: HookResult) -> None:
        if not result.additional_context or self._payload is None:
            return
        practice, fidelities = self._injected_tags(handler, self._payload)
        if practice and practice not in self._injected["practices"]:
            self._injected["practices"].append(practice)
        for name in fidelities:
            if name not in self._injected["fidelities"]:
                self._injected["fidelities"].append(name)

    def _injected_tags(
        self, handler: HookHandler, payload: HookPayload
    ) -> tuple[str, list[str]]:
        practice = handler.owner.__module__.rsplit(".", 1)[-1]
        rules = getattr(handler.tool.toolset, "rules", None)
        path = self._tool_path(payload)
        if rules is None or not path or not hasattr(rules, "_bags_for_path"):
            return practice, []
        fidelities: list[str] = []
        for bag in rules._bags_for_path(path):
            name = self._bag_fidelity(bag)
            if name:
                fidelities.append(name)
        return practice, fidelities

    def _bag_fidelity(self, bag: Any) -> str | None:
        parent = getattr(bag, "parent", None)
        if parent is None or getattr(parent, "fidelities", None) is not None:
            return None
        return getattr(parent, "name", None) or getattr(parent, "fidelity", None)

    def _tool_path(self, payload: HookPayload) -> str:
        raw = payload.as_dict().get("tool_input") or {}
        if not isinstance(raw, dict):
            return ""
        return str(raw.get("path") or raw.get("file_path") or "")

    def _merge_work_session(self, merged: HookResult) -> HookResult:
        if not merged.additional_context or self._payload is None:
            return merged
        rules = self._work_session_rules()
        if rules is None:
            return merged
        data = self._payload.as_dict()
        data["additional_context"] = merged.additional_context
        data["injected_practices"] = self._injected.get("practices") or []
        data["injected_fidelities"] = self._injected.get("fidelities") or []
        body = (rules.inject_rules(data).get("additional_context") or "").strip()
        if not body:
            return merged
        return HookResult(
            merged.permission,
            merged.continue_flag,
            merged.user_message,
            merged.agent_message,
            merged.followup_message,
            body,
        )

    def _work_session_rules(self) -> Any:
        from types import SimpleNamespace

        from harness.hooks.session_logs import SessionLogs
        from workspace.workspace import WorkSessionRulesCollection

        logs = SessionLogs(self._repo_root)
        path = logs.session_folder(logs.active_session_name()) / "work-guidelines.md"
        if not path.is_file():
            return None
        return WorkSessionRulesCollection.from_markdown(
            path.read_text(encoding="utf-8"),
            parent=SimpleNamespace(path=path),
        )

    def _write_last_chat_injected(self, result: HookResult) -> None:
        from harness.hooks.session_logs import SessionLogs

        logs = SessionLogs(self._repo_root)
        folder = logs.session_folder(logs.active_session_name())
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / "last-chat-injected-rules.md"
        dest.write_text(result.additional_context or "", encoding="utf-8")

    def _inject_path(self) -> Path:
        return self._repo_root / ".cursor" / "rules" / "practices" / "chat-inject.mdc"

    def _publish_context(self, result: HookResult) -> None:
        body = (result.additional_context or "").strip()
        if not body:
            return
        dest = self._inject_path()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(f"---\nalwaysApply: true\n---\n\n{body}\n", encoding="utf-8")

    def _consume_followup(self) -> str | None:
        dest = self._inject_path()
        if not dest.is_file():
            return None
        body = dest.read_text(encoding="utf-8")
        if self._already_sent(dest, body):
            return None
        self._mark_sent(dest, body)
        return "Injected rules for the edit you just made. Honor them on the next change.\n\n" + body

    def _already_sent(self, dest: Path, body: str) -> bool:
        stamp = dest.with_suffix(".sent")
        return stamp.is_file() and stamp.read_text(encoding="utf-8").strip() == self._digest(body)

    def _mark_sent(self, dest: Path, body: str) -> None:
        dest.with_suffix(".sent").write_text(self._digest(body), encoding="utf-8")

    def _digest(self, body: str) -> str:
        return hashlib.sha256(body.encode("utf-8")).hexdigest()

    def ping(self) -> str:
        return "pong"

    def _event_names(self) -> list[str]:
        if self._catalog is None:
            return []
        names: list[str] = []
        for toolset in self._catalog.toolsets:
            try:
                tools = toolset.tools_for(InstallDestination.HOOK)
            except Exception as error:
                self.skip(self._catalog.ref_label(toolset), error)
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
    def from_toolsets(
        cls, repo_root: Path, toolsets: list[Any] | None = None
    ) -> HookServer:
        return cls(repo_root, HandlerCatalog(toolsets, repo_root))

    @classmethod
    def from_handlers(cls, handlers: Path | str, *, repo: Path | str | None = None) -> HookServer:
        resolved = Path(repo).resolve() if repo is not None else Path(__file__).resolve().parents[2]
        try:
            server = cls(resolved, HandlerCatalog(repo_root=resolved, handlers=handlers))
        except Exception as error:
            raise HookStandupFailed("standup", None, str(error), error) from error
        return server.standup()

    def standup(self) -> HookServer:
        self.notify_exceptions()
        return self

    def _append_debug(self, message: str) -> None:
        from harness.hooks.session_logs import SessionLogs

        path = SessionLogs(self._repo_root).session_log_path("dispatch.debug")
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(path, "a", encoding="utf-8") as log:
            log.write(f"{stamp} {message}\n")


def main() -> None:
    os.chdir(_REPO_ROOT)
    raw = sys.stdin.buffer.read()
    if not raw.strip():
        print(json.dumps(HookResult().as_dict()))
        return
    print(json.dumps(HookServer.ensure(_REPO_ROOT).handle_stdin(raw).as_dict()))


if __name__ == "__main__":
    main()
