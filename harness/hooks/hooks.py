"""The ``@Hook`` mark, and the files an IDE reads to run hooks: ``hooks.json``, which names the hook command for each
event, and ``hook-handlers.json``, which lists the operations that command may run."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.agent_tools.agent_tools import AgentTool, InstallDestination
from harness.installation.destination import Installation
from harness.marks.mark import Destination

if TYPE_CHECKING:
    from harness.hooks.hook_server import HookServer

# How long the IDE waits for the hook command before it carries on without the hooks' answer.
_HOOK_COMMAND_TIMEOUT_SECONDS = 30
# The hook command, beside this file; every IDE event an install registers runs it.
_HOOK_COMMAND_SCRIPT = Path(__file__).resolve().with_name("hook_server.py")


class Hooks:
    """Class annotation: disable every hook operation on the toolset."""

    def __new__(cls, target: Any = None, *, disabled: bool = False, deploy: bool = True):
        inst = object.__new__(cls)
        inst.disabled = disabled
        inst.deploy = deploy
        if isinstance(target, type):
            return inst.annotate(target)
        return inst

    def __call__(self, cls: type) -> type:
        return self.annotate(cls)

    def annotate(self, cls: type) -> type:
        cls._hooks_disabled = self.disabled
        cls._hooks_deploy = self.deploy
        return cls


class Hook(Destination):
    flag = "_hook"
    channel = InstallDestination.HOOK
    enlists_member = True
    disabled_flag = "_hook_disabled"
    EVENTS = frozenset(
        {
            "sessionStart",
            "beforeSubmitPrompt",
            "afterAgentResponse",
            "afterAgentThought",
            "stop",
            "sessionEnd",
            "preCompact",
            "preToolUse",
            "postToolUse",
            "postToolUseFailure",
            "afterFileEdit",
            "beforeReadFile",
            "subagentStart",
        }
    )

    def __new__(cls, target: Any = None, event: str | None = None, *, disabled: bool = False):
        if isinstance(target, str):
            event = target
            target = None
        if not event:
            raise ValueError(
                'Hook requires a Cursor event: @Hook("sessionStart") or @Hook(event="sessionStart")'
            )
        if event not in cls.EVENTS:
            raise ValueError(
                f"Unknown Cursor event {event!r}. Valid events: {sorted(cls.EVENTS)}"
            )
        inst = object.__new__(cls)
        inst.name = event
        inst.disabled = disabled
        if callable(target):
            return inst.annotate(target)
        return inst

    def annotate(self, target: Any) -> Any:
        marked = super().annotate(target)
        if self.disabled:
            setattr(marked, self.disabled_flag, True)
        return marked

    @classmethod
    def companion_flags(cls) -> tuple[str, ...]:
        return (*super().companion_flags(), cls.disabled_flag)

    @classmethod
    def disabled_on(cls, operation: Any) -> bool:
        """True when ``@Hook(..., disabled=True)`` turned the hook on this operation off."""
        return bool(getattr(operation, cls.disabled_flag, False))


hook = Hook
hooks = Hooks


class HooksFileUnreadable(Exception):
    """A hooks file an install reads is not the JSON object it should be. The install stops rather than write over
    it, because the file can hold hooks the person added by hand."""

    def __init__(self, path: Path, cause: Exception) -> None:
        super().__init__(f"{path} is not readable hook JSON ({cause}); fix or remove it, then install again")
        self.path = path
        self.cause = cause


class _HooksJsonFile:
    """One JSON object file an install keeps in an IDE folder; a missing file reads as empty."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def _read(self) -> dict[str, Any]:
        if not self.path.is_file():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise HooksFileUnreadable(self.path, error) from error
        if not isinstance(data, dict):
            raise HooksFileUnreadable(self.path, TypeError(f"expected an object, found {type(data).__name__}"))
        return data

    def _write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class HookHandlersFile(_HooksJsonFile):
    """``hook-handlers.json``: the hook operations an install registered, each with its event and its toolset's
    reference. The hook server loads those toolsets; the installer's diagnosis counts the operations."""

    NAME = "hook-handlers.json"

    @property
    def handlers(self) -> list[dict[str, str]]:
        return [dict(item) for item in self._read().get("handlers") or [] if isinstance(item, dict)]

    @property
    def refs(self) -> tuple[str, ...]:
        """Each toolset reference the handlers name, once, in order."""
        return tuple(dict.fromkeys(str(item["ref"]) for item in self.handlers if item.get("ref")))

    @property
    def operation_names(self) -> list[str]:
        """Each registered operation's name, once, sorted."""
        return sorted({str(item["operation"]) for item in self.handlers if item.get("operation")})

    def write(self, handlers: list[dict[str, str]]) -> None:
        self._write({"handlers": handlers})


class HooksManifest(_HooksJsonFile):
    """``hooks.json``: the command an IDE runs for each hook event. It may hold the person's own hooks beside CDD's,
    so an install changes only CDD's command and keeps the rest."""

    NAME = "hooks.json"

    @property
    def hooks(self) -> dict[str, list[dict[str, Any]]]:
        hooks = self._read().get("hooks") or {}
        if not isinstance(hooks, dict):
            raise HooksFileUnreadable(self.path, TypeError("its hooks are not an object"))
        return {str(event): list(items) for event, items in hooks.items()}

    @property
    def registered_events(self) -> list[str]:
        return sorted(event for event in self.hooks if event)

    def write(self, hooks: dict[str, list[dict[str, Any]]]) -> None:
        self._write({"version": 1, "hooks": hooks})


class HookInstallation(Installation):
    """Write the IDE's ``hooks.json``, which runs the hook command for each event a hook operation serves, and
    ``hook-handlers.json``, which lists those operations for the hook server."""

    channel = "hook"

    def __init__(
        self,
        ide: str,
        path: Path | str,
        *,
        python: str | None = None,
        repo: Path | str | None = None,
    ) -> None:
        super().__init__(ide, path, repo=repo)
        self.python = python or sys.executable
        self._handlers: list[dict[str, str]] = []
        self.server: HookServer | None = None
        self.diagnosis: dict[str, Any] | None = None

    @property
    def dispatch_command(self) -> str:
        from harness.process.process import PythonInterpreter

        return f"{PythonInterpreter(self.python).console} -u {_HOOK_COMMAND_SCRIPT}"

    @property
    def handlers_file(self) -> HookHandlersFile:
        return HookHandlersFile(self.path / HookHandlersFile.NAME)

    @property
    def manifest(self) -> HooksManifest:
        return HooksManifest(self.path / HooksManifest.NAME)

    @property
    def registered_events(self) -> list[str]:
        """The events the IDE folder's ``hooks.json`` names a command for."""
        return self.manifest.registered_events

    @property
    def registered_operations(self) -> list[str]:
        """The hook operations the IDE folder's ``hook-handlers.json`` lists."""
        return self.handlers_file.operation_names

    def write(self, tool: AgentTool) -> None:
        if not tool.install_to_hook or not tool.hook_event:
            return
        if getattr(type(tool.toolset), "_hooks_deploy", True) is False:
            return
        record = {"event": tool.hook_event, "operation": tool.name, "ref": tool.registration_name}
        if record in self._handlers:
            return
        self._handlers.append(record)
        self.write_hooks_manifest()
        self.write_handlers()

    def write_handlers(self) -> None:
        if not self._handlers:
            return
        self.handlers_file.write(self._handlers)
        self.track_write(self.handlers_file.path)

    def write_hooks_manifest(self) -> None:
        """Point each event a handler serves at the hook command, keeping every other hook the file holds. A file that
        is not hook JSON raises *HooksFileUnreadable* and is left as it is."""
        if not self._handlers:
            return
        hooks = self.manifest.hooks
        self._strip_dispatch_command(hooks)
        self._attach_dispatch_command(hooks)
        self.manifest.write(hooks)
        self.track_write(self.manifest.path)

    def _strip_dispatch_command(self, hooks: dict[str, list[dict[str, Any]]]) -> None:
        for event_name in list(hooks):
            kept = [item for item in hooks[event_name] if item.get("command") != self.dispatch_command]
            if kept:
                hooks[event_name] = kept
            else:
                del hooks[event_name]

    def _attach_dispatch_command(self, hooks: dict[str, list[dict[str, Any]]]) -> None:
        hook_def: dict[str, Any] = {
            "command": self.dispatch_command,
            "timeout": _HOOK_COMMAND_TIMEOUT_SECONDS,
            "failClosed": False,
        }
        events = {item["event"] for item in self._handlers}
        if "postToolUse" in events:
            events.update({"afterFileEdit", "stop", "subagentStop"})
        for event in sorted(events):
            if event == "afterAgentResponse":
                hooks[event] = [dict(hook_def)]
                continue
            bucket = hooks.setdefault(event, [])
            if not any(item.get("command") == hook_def["command"] for item in bucket):
                bucket.append(dict(hook_def))

    def standup(self) -> HookServer:
        from harness.hooks.hook_server import HookServer

        self.server = HookServer.from_handlers(self.handlers_file.path, repo=self.repo or self.path)
        return self.server

    def diagnose(self) -> dict[str, Any]:
        server = self.server if self.server is not None else self.standup()
        self.diagnosis = server.diagnose()
        return self.diagnosis
