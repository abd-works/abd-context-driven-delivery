"""Hook server — run the enabled hooks for one IDE event and return one merged result.

An IDE runs this file as its hook command: ``python -u harness/hooks/hook_server.py`` with the event's fields on stdin.
The command hands the event to the checkout's hook daemon, which keeps one *HookServer* loaded between events."""
from __future__ import annotations

import sys
from pathlib import Path

if __name__ == "__main__":
    # Run by path, this file's folder is on the import path and the checkout is not; put the checkout first so the
    # imports below resolve. main() sets the rest of the checkout's import path through RepositoryToolsets.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
import logging
import os
from collections.abc import Iterator, Mapping
from typing import Any, Callable, ClassVar

from harness.agent_tools.agent_tools import AgentTool, AgentToolSet, InstallDestination, ToolsetReference
from harness.agent_tools.tool_call import ToolCall
from harness.annotations.annotation import HostedOnly
from harness.hooks.hooks import HookHandlersFile, Hooks
from harness.installation.context_config import ContextConfig
from harness.installation.repository_toolsets import RepositoryToolsets

logger = logging.getLogger(__name__)

# What loading a toolset by its ``module:Class`` reference raises when the reference is wrong or the class cannot be
# made: a malformed reference, a missing module or class, a class that is no toolset, or a constructor it cannot call.
_TOOLSET_LOAD_FAILURES = (ImportError, AttributeError, TypeError, ValueError)


class HookPayload(Mapping[str, Any]):
    """The fields an IDE sends on stdin for one firing of a hook, such as the tool that just ran and its input, and the
    checkout of the hook server that received them. Its handlers read them through the named properties; it reads as a
    mapping of those fields too."""

    def __init__(self, fields: Mapping[str, Any], checkout: Path | None = None) -> None:
        self._fields = dict(fields)
        self._checkout = checkout

    def __getitem__(self, key: str) -> Any:
        return self._fields[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._fields)

    def __len__(self) -> int:
        return len(self._fields)

    @classmethod
    def from_stdin(cls, raw: bytes, checkout: Path | None = None) -> HookPayload:
        """The event an IDE wrote on stdin, as the hook server of checkout received it."""
        text = raw.decode("utf-8-sig")
        while text.startswith("\ufeff"):
            text = text[1:]
        return cls(json.loads(text), checkout)

    def received_in(self, checkout: Path) -> HookPayload:
        """This event as the hook server of checkout received it: itself when it already names the checkout that
        received it."""
        return self if self._checkout is not None else type(self)(self._fields, checkout)

    @property
    def hook_event_name(self) -> str:
        return str(self._fields.get("hook_event_name") or "")

    @property
    def conversation_id(self) -> str:
        return str(self._fields.get("conversation_id") or "")

    @property
    def generation_id(self) -> str:
        return str(self._fields.get("generation_id") or "")

    @property
    def tool_name(self) -> str:
        """The tool the event is about, such as ``mcp__cdd__generate_generate``; empty for an event about no tool."""
        return str(self._fields.get("tool_name") or "")

    @property
    def tool_input(self) -> dict[str, Any]:
        """The arguments the tool was called with; none when the IDE sent none or sent text that is no JSON object."""
        raw = self._fields.get("tool_input") or {}
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                return {}
        return raw if isinstance(raw, dict) else {}

    @property
    def workspace_roots(self) -> list[Path]:
        """The folders Cursor names as the chat's workspace."""
        raw = self._fields.get("workspace_roots") or []
        if isinstance(raw, str):
            raw = [raw]
        if not isinstance(raw, list):
            return []
        return [Path(item) for item in raw if isinstance(item, str) and item.strip()]

    @property
    def project(self) -> Path | None:
        """The folder of the project the event happened in: Cursor's first workspace root, else the folder Claude Code
        ran in; none when the event names neither."""
        roots = self.workspace_roots
        if roots:
            return roots[0]
        folder = str(self._fields.get("cwd") or "").strip()
        return Path(folder) if folder else None

    @property
    def call(self) -> ToolCall:
        """The tool call this event reports: the tool's input, in the project the event happened in, else in the
        checkout that received it, made once, so every handler of the event reads the same call and the session it
        opens."""
        made = self.__dict__.get("_call")
        if made is None:
            made = self.__dict__["_call"] = ToolCall(self.tool_input, self.project or self._checkout)
        return made

    @property
    def chat_id(self) -> str:
        """The chat whose rules this event's injection belongs to: for ``subagentStop``, the subagent's own
        transcript; for any other event, the conversation."""
        if self.hook_event_name == "subagentStop":
            stem = Path(str(self._fields.get("agent_transcript_path") or "")).stem.strip()
            if stem:
                return stem
        return self.conversation_id.strip()

    @property
    def session(self) -> Any:
        """The session the event works in: the one saved as open in the event's project, else in the checkout that
        received it, main when none is; none when the event names neither or no sessions are registered. It is read
        once for the event, the way a tool call reads its session, so every hook of one event works in the same session,
        and the next event follows a switch or a close made through MCP."""
        return self.call.session

    def edited_path(self) -> str:
        for key in ("file_path", "path", "uri"):
            value = self._fields.get(key)
            if isinstance(value, str) and value.strip():
                return value
        tool_input = self.tool_input
        return str(tool_input.get("path") or tool_input.get("file_path") or tool_input.get("target_notebook") or "")


# A toast that names its source writes it before this arrow, such as `generate → rules : stories scenarios`, so the
# notifier can join the toasts of one burst.
TOAST_ARROW = " \u2192 "


def rules_toast(source: str, labels: list[str]) -> str:
    """The toast for the rules a hook gave the agent: what injected them, then each rule set's label."""
    return f"{source}{TOAST_ARROW}rules : {', '.join(labels)}"


class HookResult:
    """Fields Cursor reads back from the hook process, and the toast the person sees beside the chat. The toast is not
    sent to Cursor: the hook server hands it to the notifier that shows toasts."""

    def __init__(
        self,
        permission: str = "allow",
        continue_flag: bool | None = None,
        user_message: Any = None,
        agent_message: Any = None,
        followup_message: Any = None,
        additional_context: Any = None,
        toast: Any = None,
    ) -> None:
        self.permission = permission
        self.continue_flag = continue_flag
        self.user_message = self._optional_text(user_message)
        self.agent_message = self._optional_text(agent_message)
        self.followup_message = self._optional_text(followup_message)
        self.additional_context = self._optional_text(additional_context)
        self.toast = self._optional_text(toast)
        self.followup_only = False

    def _optional_text(self, value: Any) -> str | None:
        if not value:
            return None
        return str(value)

    @classmethod
    def from_handler(cls, raw: Mapping[str, Any] | None) -> HookResult:
        if not raw:
            return cls()
        continue_flag = False if raw.get("continue") is False else None
        result = cls(
            permission=str(raw.get("permission") or "allow"),
            continue_flag=continue_flag,
            user_message=raw.get("user_message"),
            agent_message=raw.get("agent_message"),
            followup_message=raw.get("followup_message"),
            additional_context=raw.get("additional_context"),
            toast=raw.get("toast"),
        )
        if "permission" not in raw and result.followup_message:
            result.followup_only = True
        return result

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
            self.toast,
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
            self._join_lines(self.toast, other.toast),
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
        if self.followup_only:
            if self.followup_message:
                return {"followup_message": self.followup_message}
            return {}
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
    """One hook tool that may run for an event. It reads the tool's name, toolset, callable, and description from the
    ``AgentTool`` it holds."""

    def __init__(self, tool: AgentTool, repo_root: Path) -> None:
        self.tool = tool
        self.repo_root = repo_root

    @property
    def label(self) -> str:
        """``{toolset class}.{operation}``, the name the dispatch log and skipped handlers report."""
        return f"{type(self.tool.toolset).__name__}.{self.tool.name}"

    def is_enabled(self, payload: HookPayload | None = None) -> bool:
        if Hooks.disabled_on(self.tool.toolset):
            return False
        pattern = self._pattern_name()
        if not pattern:
            return True
        return self._pattern_enabled(pattern, payload)

    def _pattern_name(self) -> str:
        toolset = self.tool.toolset
        name = getattr(toolset, "pattern", None) or getattr(type(toolset), "pattern", None)
        return str(name or "").strip()

    def _pattern_enabled(self, pattern: str, payload: HookPayload | None) -> bool:
        if payload is None:
            return False
        return any(
            self._guideline_value(root, pattern) == "enabled"
            for root in self._guideline_roots(payload)
        )

    def _guideline_roots(self, payload: HookPayload) -> list[Path]:
        edited = payload.edited_path()
        roots = payload.workspace_roots
        if not edited:
            return roots or [self.repo_root]
        edited_path = Path(edited)
        if edited_path.is_absolute():
            containing = [root for root in roots if self._contains(root, edited_path)]
            if containing:
                return containing
            return self._context_parents(edited_path)
        existing = [root for root in roots if (root / edited_path).exists()]
        if existing:
            return existing
        if roots:
            return roots
        return [self.repo_root]

    def _contains(self, root: Path, edited: Path) -> bool:
        try:
            edited.resolve().relative_to(root.resolve())
        except (OSError, ValueError):
            return False
        return True

    def _context_parents(self, edited: Path) -> list[Path]:
        for parent in edited.resolve().parents:
            if ContextConfig(parent).exists():
                return [parent]
        return []

    def _guideline_value(self, root: Path, pattern: str) -> str:
        return ContextConfig(root).guideline(pattern)

    def invoke(self, payload: HookPayload) -> HookResult:
        raw = self.tool.callable(payload)
        fields = raw if isinstance(raw, Mapping) else None
        result = HookResult.from_handler(fields)
        if result.additional_context or not fields:
            return result
        return result.with_description(self.tool.docstring)


class HandlerCatalog:
    """The toolsets whose hook operations may run, and the handlers of each event they serve, made once when the
    toolsets load. Each toolset is named by its class, its instance, or, as ``hook-handlers.json`` lists it, its
    ``module:Class`` reference; one that cannot be loaded is kept in ``failures`` and the rest still serve."""

    def __init__(self, toolsets: list[Any], repo_root: Path | None = None) -> None:
        self.repo_root = repo_root
        self.failures: list[tuple[str, BaseException]] = []
        self.toolsets: list[Any] = []
        self._load_items(toolsets)
        self._handlers = self._handlers_by_event()

    def _load_items(self, items: list[Any]) -> None:
        for item in items:
            try:
                loaded = AgentToolSet.from_items([item])
            except _TOOLSET_LOAD_FAILURES as error:
                self.failures.append((self.ref_label(item), error))
                continue
            self.toolsets.extend(
                instance for instance in loaded if not HostedOnly.annotates(instance)
            )

    def ref_label(self, item: Any) -> str:
        if isinstance(item, str):
            return item
        if isinstance(item, dict):
            return str(item.get("toolset") or item)
        registration = getattr(item, "registration_name", None)
        if isinstance(registration, str) and registration:
            return registration
        return ToolsetReference.from_class(item if isinstance(item, type) else type(item)).text

    @property
    def event_names(self) -> list[str]:
        """Every event some loaded hook operation serves, each once."""
        return list(dict.fromkeys(tool.hook_event for tool in self._hook_tools() if tool.hook_event))

    def for_event(self, event_name: str) -> list[HookHandler]:
        """The handlers of the hook operations that serve event_name, one for each operation."""
        return list(self._handlers.get(event_name, ()))

    def _handlers_by_event(self) -> dict[str, list[HookHandler]]:
        by_event: dict[str, dict[tuple[str, str], HookHandler]] = {}
        for tool in self._hook_tools():
            for event in self._events_served(tool):
                handlers = by_event.setdefault(event, {})
                key = (type(tool.toolset).__name__, tool.name)
                if key not in handlers:
                    handlers[key] = HookHandler(tool, self.repo_root or Path())
        return {event: list(handlers.values()) for event, handlers in by_event.items()}

    def _hook_tools(self) -> list[AgentTool]:
        return [tool for toolset in self.toolsets for tool in toolset.tools_for(InstallDestination.HOOK)]

    def _events_served(self, tool: AgentTool) -> list[str]:
        """A tool serves the event its annotation names. Rule injection annotated for ``postToolUse`` also serves
        ``afterFileEdit``, because Cursor reports a file edit under that event as well as ``postToolUse``."""
        if tool.hook_event == "postToolUse" and tool.name == "inject_rules":
            return [tool.hook_event, "afterFileEdit"]
        return [tool.hook_event]


class HookIllegitimateHandler(Exception):
    """One hook handler was skipped: its toolset could not be loaded, or it raised while answering an event. The
    server keeps answering every event with the other handlers, and diagnose reports this one."""

    def __init__(self, tool: str, reason: str, cause: BaseException | None = None) -> None:
        super().__init__(f"{tool}: {reason}")
        self.tool = tool
        self.reason = reason
        self.cause = cause


class HookServer:
    """The hooks of one checkout, loaded once: it runs the enabled handlers for each event and merges their answers.
    The checkout's hook daemon holds one and hands it every event its hook commands receive."""

    # Shows a merged result's toast in the chat's workspace folders. The notifier registers itself when it is loaded,
    # so a hook names its toast in its result and never the notifier; with none registered, no toast is shown.
    _toast_shown_by: ClassVar[Callable[[str, list[Path]], Any] | None] = None

    @classmethod
    def show_toasts_with(cls, show: Callable[[str, list[Path]], Any]) -> None:
        """Have show(toast, workspace_roots) show each toast a dispatched event's hooks give."""
        cls._toast_shown_by = show

    def __init__(self, repo_root: Path, catalog: HandlerCatalog) -> None:
        self._repo_root = repo_root
        self._catalog = catalog
        self.exceptions: list[HookIllegitimateHandler] = []
        self._absorb_catalog_failures()

    @classmethod
    def from_repository(cls, toolsets: RepositoryToolsets) -> HookServer:
        """The hook server of a checkout: the toolsets its installed ``.cursor/hook-handlers.json`` lists, else every
        toolset it defines. Every toolset module is imported either way, so the registrations those modules make,
        such as how a call opens its session, hold in the hook process."""
        classes = toolsets.classes()
        installed = HookHandlersFile(toolsets.root / ".cursor" / HookHandlersFile.NAME).refs
        server = cls(toolsets.root, HandlerCatalog(list(installed) or classes, toolsets.root))
        for unloadable in toolsets.unloadable:
            server.skip(unloadable.reference, unloadable.cause)
        return server

    @classmethod
    def from_handlers(cls, handlers: Path | str, *, repo: Path | str) -> HookServer:
        """The hook server of the toolsets a ``hook-handlers.json`` lists, for the checkout at repo."""
        resolved = Path(repo).resolve()
        server = cls(resolved, HandlerCatalog(list(HookHandlersFile(handlers).refs), resolved))
        server.notify_exceptions()
        return server

    def skip(self, tool: str, error: BaseException) -> None:
        skipped = error if isinstance(error, HookIllegitimateHandler) else HookIllegitimateHandler(tool, str(error), error)
        self.exceptions.append(skipped)
        logger.error("hook standup exception: skipped %s: %s", skipped.tool, skipped.reason, exc_info=skipped.cause)

    def handle_stdin(self, raw: bytes) -> HookResult:
        """The answer to the event an IDE wrote on stdin, with the rules kept for its chat."""
        if not raw.strip():
            return HookResult()
        try:
            payload = HookPayload.from_stdin(raw, self._repo_root)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return HookResult()
        result = self.dispatch(payload)
        session = payload.session
        if session is not None:
            result = self._with_chat_injections(session.chat_injections, payload, result)
        if payload.hook_event_name in ("stop", "subagentStop"):
            result.followup_only = result.followup_message is not None
        return result

    def _with_chat_injections(self, injections: Any, payload: HookPayload, result: HookResult) -> HookResult:
        """result with the rules kept for the event's chat, through the chat injections its session keeps."""
        if injections.is_rules_dump(result.additional_context or ""):
            result.additional_context = None
        injections.keep(result, payload)
        if payload.hook_event_name == "beforeSubmitPrompt":
            return injections.replay(payload, result)
        return result

    def dispatch(self, payload: HookPayload) -> HookResult:
        """The merged answer of the enabled handlers of payload's event, received by this hook server's checkout."""
        payload = payload.received_in(self._repo_root)
        event = payload.hook_event_name
        self._append_debug(
            payload,
            f"EVENT {event!r} tool={payload.tool_name!r} path={payload.edited_path()!r} "
            f"conversation_id={payload.conversation_id!r} payload_keys={sorted(payload)}"
        )
        if not event:
            self._append_debug(payload, "NO_EVENT merged={}")
            return HookResult()
        merged = HookResult()
        for result in self._invoke_enabled(event, payload):
            merged = merged.merge(result)
        self._append_debug(payload, f"MERGED {json.dumps(merged.as_dict())}")
        self._show_toast(merged, payload)
        return merged

    def diagnose(self) -> dict[str, Any]:
        self.dispatch(HookPayload({}))
        return {
            "ok": True,
            "ping": "pong",
            "events": self._catalog.event_names,
            "exceptions": [{"tool": item.tool, "reason": item.reason} for item in self.exceptions],
            "notice": self.notice(),
        }

    def notice(self) -> str:
        if not self.exceptions:
            return ""
        lines = ["hook standup skipped illegitimate handlers and continued:"]
        lines.extend(f"- {item.tool}: {item.reason}" for item in self.exceptions)
        return "\n".join(lines)

    def notify_exceptions(self) -> None:
        text = self.notice()
        if text:
            print(text, file=sys.stderr)

    def _absorb_catalog_failures(self) -> None:
        for tool, error in self._catalog.failures:
            self.skip(tool, error)
        self._catalog.failures.clear()

    def _invoke_enabled(self, event: str, payload: HookPayload) -> list[HookResult]:
        enabled: list[str] = []
        results: list[HookResult] = []
        for handler in self._catalog.for_event(event):
            if not handler.is_enabled(payload):
                continue
            enabled.append(handler.label)
            try:
                result = handler.invoke(payload)
            # Hooks are other toolsets' code. One handler's failure must not cost the person the other handlers'
            # answers or the IDE's event, so it is recorded as a skipped handler, with its traceback in the log, and
            # diagnose reports it.
            except Exception as error:  # noqa: BLE001
                self.skip(handler.label, error)
                continue
            results.append(result)
            self._append_debug(payload, f"HANDLER {handler.label} result={json.dumps(result.as_dict())}")
        self._append_debug(payload, f"ENABLED {enabled or ['(none)']}")
        return results

    def _show_toast(self, result: HookResult, payload: HookPayload) -> None:
        show = type(self)._toast_shown_by
        if result.toast and show is not None:
            show(result.toast, payload.workspace_roots)

    def _append_debug(self, payload: HookPayload, message: str) -> None:
        """Append message to the dispatch log of the session payload's event works in."""
        session = payload.session
        if session is not None:
            session.append_hook_log("dispatch.debug", message)


def main() -> None:
    """The hook command: hand the event on stdin to this checkout's hook daemon and print its answer for the IDE."""
    from harness.hooks.hook_daemon import HookDaemon

    checkout = Path(__file__).resolve().parents[2]
    daemon = HookDaemon(checkout)
    daemon.toolsets.use_for_this_process()
    os.chdir(checkout)
    raw = sys.stdin.buffer.read()
    if not raw.strip():
        print(json.dumps(HookResult().as_dict()))
        return
    answer = daemon.ensure().handle_stdin(raw)
    print(json.dumps(HookResult.from_handler(answer).as_dict()))


if __name__ == "__main__":
    main()
