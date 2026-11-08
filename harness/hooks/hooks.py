"""The ``@Hook`` annotation, and the files an IDE reads to run hooks: ``hooks.json``, which names the hook command for each
event, and ``hook-handlers.json``, which lists the operations that command may run. Importing this module registers the
hook channel's installation with the Installer."""
from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.agent_tools.agent_tools import AgentTool, InstallDestination
from harness.annotations.annotation import Annotation, Destination
from harness.hooks.hook_daemon import HookDaemon
from harness.installation.destination import ServerInstallation
from harness.installation.ide_layout import IdeLayout
from harness.installation.installer import Installer
from harness.process.process import PythonInterpreter

if TYPE_CHECKING:
    from harness.hooks.hook_server import HookServer

# How long the IDE waits for the hook command before it carries on without the hooks' answer.
_HOOK_COMMAND_TIMEOUT_SECONDS = 30
# The hook command, beside this file; every IDE event an install registers runs it.
_HOOK_COMMAND_SCRIPT = Path(__file__).resolve().with_name("hook_server.py")


class Hooks(Annotation):
    """Class annotation on a toolset: ``@Hooks(disabled=True)`` turns off every hook operation on it, and
    ``deploy=False`` keeps them out of install. The hook server and the hook install read it through ``disabled_on``
    and ``deploys``, so a subclass carries its base's setting."""

    flag = "_hooks"
    copied = False

    def __new__(cls, target: Any = None, *, disabled: bool = False, deploy: bool = True):
        annotation = object.__new__(cls)
        annotation.disabled = disabled
        annotation.deploy = deploy
        if isinstance(target, type):
            return annotation.annotate(target)
        return annotation

    def annotate(self, toolset_class: type) -> type:
        setattr(toolset_class, self.flag, self)
        return toolset_class

    @classmethod
    def _on(cls, toolset: Any) -> Hooks | None:
        return getattr(type(toolset), cls.flag, None)

    @classmethod
    def disabled_on(cls, toolset: Any) -> bool:
        """True when ``@Hooks(disabled=True)`` turned off every hook of toolset's class."""
        annotation = cls._on(toolset)
        return annotation is not None and annotation.disabled

    @classmethod
    def deploys(cls, toolset: Any) -> bool:
        """False when ``@Hooks(deploy=False)`` keeps the hooks of toolset's class out of install."""
        annotation = cls._on(toolset)
        return annotation is None or annotation.deploy


class HookServerNotRunning(Exception):
    """The install finished but the checkout's hook daemon does not answer, so hooks would not run."""

    def __init__(self, repo: Path) -> None:
        super().__init__(f"install failed: the hook server of {repo} is not running")
        self.repo = repo


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
        annotated = super().annotate(target)
        if self.disabled:
            setattr(annotated, self.disabled_flag, True)
        return annotated

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


class HookInstallation(ServerInstallation):
    """Write the IDE's ``hooks.json``, which runs the hook command for each event a hook operation serves, and
    ``hook-handlers.json``, which lists those operations for the hook server; then stand up, start, and report the hook
    server of the checkout. An IDE whose layout runs no hooks gets none."""

    channel = "hook"

    def __init__(
        self,
        layout: IdeLayout,
        path: Path | str,
        *,
        python: str | None = None,
        repo: Path | str | None = None,
    ) -> None:
        super().__init__(layout, path, repo=repo)
        self.interpreter = PythonInterpreter(python)
        self.handlers_file = HookHandlersFile(self.path / HookHandlersFile.NAME)
        self.manifest = HooksManifest(self.path / HooksManifest.NAME)
        self.daemon = HookDaemon(self.repo or self.path)
        self._handlers: list[dict[str, str]] = []
        self.server: HookServer | None = None
        self.diagnosis: dict[str, Any] | None = None

    @property
    def dispatch_command(self) -> str:
        return f"{self.interpreter.console} -u {_HOOK_COMMAND_SCRIPT}"

    def accepts(self, tool: AgentTool) -> bool:
        return tool.install_to_hook and self.layout.runs_hooks

    @property
    def published(self) -> list[str]:
        return self.registered_operations

    def ensure_running(self) -> dict[str, str]:
        """Start the checkout's hook daemon when none answers; an IDE that runs no hooks gets none."""
        if not self.layout.runs_hooks:
            return {"hook": "not installed"}
        self.daemon.ensure()
        if self.daemon.live_address() is None:
            raise HookServerNotRunning(self.daemon.repo)
        return {"hook": "running"}

    def status(self) -> list[str]:
        address = self.daemon.live_address()
        return [
            f"hook server: {f'running (pid {address.pid})' if address is not None else 'not running'}",
            f"hooks registered (events): {', '.join(self.registered_events) or 'none'}",
            f"hook handlers (operations): {', '.join(self.registered_operations) or 'none'}",
        ]

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
        if not Hooks.deploys(tool.toolset):
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


Installer.installs_through(HookInstallation)
