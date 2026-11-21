"""Hook server — run the enabled hooks for one IDE event and return one merged result.

The checkout's hook daemon (``hook_daemon.py``) keeps one *HookServer* loaded between events and hands it each event
the IDE's hook command receives."""
from __future__ import annotations

import functools
import json
import logging
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, fields as dataclass_fields, replace
from pathlib import Path
from typing import Any, Callable, Protocol

from harness.agent_tools.agent_tools import AgentTool, AgentToolSet, InstallDestination, ToolsetConfiguration, ToolsetReference
from harness.agent_tools.tool_call import CallSession, ToolCall
from harness.annotations.annotation import hosted_only
from harness.hooks.hooks import HookHandlersFile, Hooks, InstalledHookHandlers, events_served
from harness.installation.destination import SkippedTools
from harness.installation.context_config import ContextConfig
from harness.installation.repository_toolsets import RepositoryToolsets

logger = logging.getLogger(__name__)

# What loading a toolset by its ``module:Class`` reference raises when the reference is wrong or the class cannot be
# made: a malformed reference, a missing module or class, a class that is no toolset, or a constructor it cannot call.


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

    @functools.cached_property
    def call(self) -> ToolCall:
        """The tool call this event reports: the tool's input, in the project the event happened in, else in the
        checkout that received it, made once, so every handler of the event reads the same call and the session it
        opens."""
        return ToolCall(self.tool_input, self.project or self._checkout)

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
    def session(self) -> HookSession | None:
        """The session the event works in: the one saved as open in the event's project, else in the checkout that
        received it, main when none is; none when the event names neither or no sessions are registered. It is read
        once for the event, the way a tool call reads its session, so every hook of one event works in the same session,
        and the next event follows a switch or a close made through MCP."""
        return self.call.session  # type: ignore[return-value] - the registered sessions answer HookSession

    # The IDE event and the tools that report a file the agent just edited: Cursor's file-edit event and its edit
    # tools, and Claude Code's edit tools.
    _EDIT_EVENTS = frozenset({"afterFileEdit"})
    _EDIT_TOOLS = frozenset({"Write", "StrReplace", "EditNotebook", "Edit", "MultiEdit", "NotebookEdit"})

    @property
    def is_edit(self) -> bool:
        """Whether the event reports a file the agent just edited, whichever IDE sent it."""
        return self.hook_event_name in self._EDIT_EVENTS or self.tool_name in self._EDIT_TOOLS

    def edited_path(self) -> str:
        """The file the event says the agent edited: the one Cursor's file-edit event names, else the first its tool
        call names."""
        for key in ("file_path", "path", "uri"):
            value = self._fields.get(key)
            if isinstance(value, str) and value.strip():
                return value
        return next(iter(self.call.named_paths), "")

    @property
    def invoked_tool(self) -> str:
        """The tool the agent called: the one an IDE's MCP wrapper, such as Cursor's ``CallMcpTool``, names in its input,
        else the event's own tool."""
        name = self.tool_name
        nested = self.tool_input.get("toolName") or self.tool_input.get("tool_name") or self.tool_input.get("name")
        if not isinstance(nested, str) or not nested.strip():
            return name
        wrapped = "mcp" in name.lower() or name in {"CallMcpTool", "call_mcp_tool"}
        return nested.strip() if wrapped or "." in nested or "-" in nested else name


# A toast that names its source writes it before this arrow, such as `generate → rules : stories scenarios`, so the
# notifier can join the toasts of one burst.
TOAST_ARROW = " \u2192 "


def rules_toast(source: str, labels: list[str]) -> str:
    """The toast for the rules a hook gave the agent: what injected them, then each rule set's label."""
    return f"{source}{TOAST_ARROW}rules : {', '.join(labels)}"


class ChatRuleInjections(Protocol):
    """The rules a session keeps for each of its chats, so a rule a hook injected once is given to that chat again when
    it submits a prompt. A session of space/session keeps them; the framework names only what it calls."""

    def keep(self, result: HookResult, payload: HookPayload) -> None: ...

    def replay(self, payload: HookPayload, result: HookResult) -> HookResult: ...

    def is_rules_dump(self, body: str) -> bool: ...


class HookSession(CallSession, Protocol):
    """The session a hook event works in, as the hook server uses it: the rules it keeps for each of its chats, and the
    dispatch log each handler's result is written to."""

    chat_injections: ChatRuleInjections

    def log_hook_dispatch(self, text: str) -> None:
        """Stamp text in the session's hook dispatch log."""


@dataclass(frozen=True)
class HookMessages:
    """What a hook says back, each part none when it says nothing there: a line for the person, a note for the agent,
    a prompt Cursor sends next, context added to the agent's model, and a toast the person sees beside the chat."""

    user_message: str | None = None
    agent_message: str | None = None
    followup_message: str | None = None
    additional_context: str | None = None
    toast: str | None = None

    @classmethod
    def from_handler(cls, raw: Mapping[str, Any]) -> HookMessages:
        """The messages a handler's answer names, each read as text; an empty one is none."""
        return cls(*(str(raw[field.name]) if raw.get(field.name) else None for field in dataclass_fields(cls)))


class HookResult:
    """Fields Cursor reads back from the hook process, and the toast the person sees beside the chat. The toast is not
    sent to Cursor: the hook server hands it to the notifier that shows toasts."""

    def __init__(self, permission: str = "allow", continue_flag: bool | None = None, messages: HookMessages = HookMessages()) -> None:
        self.permission = permission
        self.continue_flag = continue_flag
        self.user_message = messages.user_message
        self.agent_message = messages.agent_message
        self.followup_message = messages.followup_message
        self.additional_context = messages.additional_context
        self.toast = messages.toast
        self.followup_only = False

    @property
    def messages(self) -> HookMessages:
        return HookMessages(self.user_message, self.agent_message, self.followup_message, self.additional_context, self.toast)

    @classmethod
    def from_handler(cls, raw: Mapping[str, Any] | None) -> HookResult:
        if not raw:
            return cls()
        continue_flag = False if raw.get("continue") is False else None
        result = cls(str(raw.get("permission") or "allow"), continue_flag, HookMessages.from_handler(raw))
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
        return HookResult(self.permission, self.continue_flag, replace(self.messages, agent_message=text))

    def merge(self, other: HookResult) -> HookResult:
        permission = "deny" if "deny" in (self.permission, other.permission) else "allow"
        continue_flag = False if False in (self.continue_flag, other.continue_flag) else None
        merged = HookMessages(
            self._join_lines(self.user_message, other.user_message),
            self._join_lines(self.agent_message, other.agent_message),
            other.followup_message or self.followup_message,
            self._join_unique_context(other),
            self._join_lines(self.toast, other.toast),
        )
        return HookResult(permission, continue_flag, merged)

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
        # The project configuration of each folder an event's edits fall under, made the first time that folder is
        # asked about and kept; each read of a guideline still reads the file, so a change to it holds at once.
        self._configs: dict[Path, ContextConfig] = {}

    @property
    def label(self) -> str:
        """``{toolset class}.{operation}``, the name the dispatch log and skipped handlers report."""
        return f"{type(self.tool.toolset).__name__}.{self.tool.name}"

    def is_enabled(self, payload: HookPayload | None = None) -> bool:
        if Hooks.from_toolset_class(type(self.tool.toolset)).disabled:
            return False
        pattern = self._pattern_name()
        if not pattern:
            return True
        return self._pattern_enabled(pattern, payload)

    def _pattern_name(self) -> str:
        return self.tool.toolset.pattern.strip()

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
            if self._config_of(parent).exists():
                return [parent]
        return []

    def _guideline_value(self, root: Path, pattern: str) -> str:
        return self._config_of(root).guideline(pattern)

    def _config_of(self, root: Path) -> ContextConfig:
        if root not in self._configs:
            self._configs[root] = ContextConfig(root)
        return self._configs[root]

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
    ``module:Class`` reference; one that cannot be loaded is kept in ``failures`` and the rest still serve. A toolset
    whose hooks ``@Hooks(deploy=False)`` keeps out of install is left out here too, so the hooks an install leaves out
    never run, however the catalog was named."""

    def __init__(self, toolsets: list[ToolsetConfiguration], repo_root: Path | None = None) -> None:
        self.repo_root = repo_root
        self.failures: list[tuple[str, BaseException]] = []
        self.toolsets: list[AgentToolSet] = []
        self._load_items(toolsets)
        self._handlers = self._handlers_by_event()

    def _load_items(self, items: list[ToolsetConfiguration]) -> None:
        for configured in items:
            try:
                loaded = AgentToolSet.from_items([configured])
            except AgentToolSet.LOAD_FAILURES as error:
                self.failures.append((self.ref_label(configured), error))
                continue
            self.toolsets.extend(
                instance for instance in loaded if not hosted_only.annotates(instance) and Hooks.from_toolset_class(type(instance)).deploy
            )

    def ref_label(self, configured: ToolsetConfiguration) -> str:
        if isinstance(configured, str):
            return configured
        if isinstance(configured, dict):
            return str(configured.get("toolset") or configured)
        registration = getattr(configured, "registration_name", None)
        if isinstance(registration, str) and registration:
            return registration
        return str(ToolsetReference.of(configured if isinstance(configured, type) else type(configured)))

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
            for event in events_served(tool.hook_event):
                handlers = by_event.setdefault(event, {})
                key = (type(tool.toolset).__name__, tool.name)
                if key not in handlers:
                    handlers[key] = HookHandler(tool, self.repo_root or Path())
        return {event: list(handlers.values()) for event, handlers in by_event.items()}

    def _hook_tools(self) -> list[AgentTool]:
        return [tool for toolset in self.toolsets for tool in toolset.tools_for(InstallDestination.HOOK)]



class HookToasts:
    """How the process shows the toast a hook gives in its result: the one notifier, which registers itself when it is
    loaded (``HOOK_TOASTS.show_with(show)``, tools/prompt_notify), so a hook names its toast in its result and never the
    notifier. The process keeps one (``HOOK_TOASTS``); with no notifier registered, no toast is shown."""

    def __init__(self) -> None:
        self._show: Callable[[str, list[Path]], Any] | None = None

    def show_with(self, show: Callable[[str, list[Path]], Any] | None) -> None:
        """Have show(toast, workspace_roots) show each toast a dispatched event's hooks give; none shows no toast."""
        self._show = show

    @property
    def shown_by(self) -> Callable[[str, list[Path]], Any] | None:
        """The notifier that shows toasts now; none when no notifier registered."""
        return self._show

    def show(self, toast: str, workspace_roots: list[Path]) -> None:
        """Show toast in the chat's workspace folders, when there is a toast and a notifier to show it."""
        if toast and self._show is not None:
            self._show(toast, workspace_roots)


HOOK_TOASTS = HookToasts()


class HookServer:
    """The hooks of one checkout, loaded once: it runs the enabled handlers for each event and merges their answers.
    The checkout's hook daemon holds one and hands it every event its hook commands receive."""

    def __init__(self, repo_root: Path, catalog: HandlerCatalog) -> None:
        self._repo_root = repo_root
        self._catalog = catalog
        self.skipped = SkippedTools("hook", "handlers")
        self._absorb_catalog_failures()

    @classmethod
    def from_repository(cls, toolsets: RepositoryToolsets) -> HookServer:
        """The hook server of a checkout: the toolsets the ``hook-handlers.json`` of its hook installs list, whichever
        IDE each was for, else every toolset it defines whose hooks deploy. Every toolset module is imported either way,
        so the registrations those modules make, such as how a call opens its session, hold in the hook process."""
        classes = toolsets.classes()
        installed = InstalledHookHandlers(toolsets.root).refs
        server = cls(toolsets.root, HandlerCatalog(list(installed) or classes, toolsets.root))
        for unloadable in toolsets.unloadable:
            server.skipped.skip(unloadable.reference, unloadable.cause)
        return server

    @classmethod
    def from_handlers(cls, handlers: Path | str, *, repo: Path | str) -> HookServer:
        """The hook server of the toolsets a ``hook-handlers.json`` lists, for the checkout at repo."""
        resolved = Path(repo).resolve()
        server = cls(resolved, HandlerCatalog(list(HookHandlersFile(handlers).refs), resolved))
        server.skipped.notify()
        return server

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

    def _with_chat_injections(self, injections: ChatRuleInjections, payload: HookPayload, result: HookResult) -> HookResult:
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
        HOOK_TOASTS.show(merged.toast, payload.workspace_roots)
        return merged

    def diagnose(self) -> dict[str, Any]:
        self.dispatch(HookPayload({}))
        return {
            "ok": True,
            "ping": "pong",
            "events": self._catalog.event_names,
            "exceptions": self.skipped.as_data,
            "notice": self.skipped.notice,
        }

    def _absorb_catalog_failures(self) -> None:
        for tool, error in self._catalog.failures:
            self.skipped.skip(tool, error)
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
                self.skipped.skip(handler.label, error)
                continue
            results.append(result)
            self._append_debug(payload, f"HANDLER {handler.label} result={json.dumps(result.as_dict())}")
        self._append_debug(payload, f"ENABLED {enabled or ['(none)']}")
        return results

    def _append_debug(self, payload: HookPayload, message: str) -> None:
        """Append message to the dispatch log of the session payload's event works in."""
        session = payload.session
        if session is not None:
            session.log_hook_dispatch(message)

