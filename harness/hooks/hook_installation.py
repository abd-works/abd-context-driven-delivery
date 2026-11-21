"""*HookInstallation*, the hook channel of an install: it writes the IDE's ``hooks.json`` and ``hook-handlers.json``.
The channel holds no server: the hook command starts the checkout's hook daemon on the first event, and replaces one
that loaded older hook code. Importing this module registers it with the Installer's registered channels
(``SERVER_CHANNELS``); importing the ``harness.hooks`` package imports it."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from harness.agent_tools.agent_tools import AgentTool
from harness.hooks.hook_daemon import HookDaemon
from harness.hooks.hooks import Hook, HookHandlersFile, Hooks, HooksManifest, events_served
from harness.installation.destination import RegisteredChannel
from harness.installation.installer import SERVER_CHANNELS
from harness.process.process import PythonInterpreter

if TYPE_CHECKING:
    from harness.installation.install_record import InstallRecord
    from harness.installation.install_target import InstallTarget
    from harness.installation.repository_toolsets import RepositoryToolsets

# How long the IDE waits for the hook command before it carries on without the hooks' answer.
_HOOK_COMMAND_TIMEOUT_SECONDS = 30


class HookInstallation(RegisteredChannel):
    """Write the IDE's ``hooks.json``, which runs the hook command for each event a hook operation serves, and
    ``hook-handlers.json``, which lists those operations for the hook server. The hook command starts that server on the
    first event, so the channel holds no server. An IDE whose layout runs no hooks gets none."""

    destination = Hook

    def __init__(self, target: InstallTarget, record: InstallRecord, repository: RepositoryToolsets | None = None) -> None:
        super().__init__(target, record, repository)
        # The Python the hook command runs on: the one running this install.
        self.interpreter = PythonInterpreter()
        self.handlers_file = HookHandlersFile(self.path / HookHandlersFile.NAME)
        self.manifest = HooksManifest(self.path / HooksManifest.NAME)
        self._handlers: list[dict[str, str]] = []

    @property
    def dispatch_command(self) -> str:
        return f"{self.interpreter.console} -u {HookDaemon.COMMAND_SCRIPT}"

    def accepts(self, tool: AgentTool) -> bool:
        return super().accepts(tool) and self.layout.runs_hooks

    @property
    def published(self) -> list[str]:
        return self.registered_operations

    def status(self) -> list[str]:
        return [
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
        event = Hook.name_given(tool.callable)
        if not tool.is_published_to(Hook) or not event:
            return
        if not Hooks.from_toolset_class(type(tool.toolset)).deploy:
            return
        record = {"event": event, "operation": tool.name, "ref": str(tool.toolset.reference)}
        if record in self._handlers:
            return
        self._handlers.append(record)
        self.write_hooks_manifest()
        self.write_handlers()

    def write_handlers(self) -> None:
        if not self._handlers:
            return
        self.handlers_file.write(self._handlers)
        self.wrote(self.handlers_file.path)

    def write_hooks_manifest(self) -> None:
        """Point each event a handler serves at the hook command, keeping every other hook the file holds. A file that
        is not hook JSON raises *HooksFileUnreadable* and is left as it is."""
        if not self._handlers:
            return
        hooks = self.manifest.hooks
        self._strip_dispatch_command(hooks)
        self._attach_dispatch_command(hooks)
        self.manifest.write(hooks)
        self.wrote(self.manifest.path)

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
        events = {served for item in self._handlers for served in events_served(item["event"])}
        if "postToolUse" in events:
            # The hook server keeps the rules a postToolUse hook gave each chat and answers its stop events with them.
            events.update({"stop", "subagentStop"})
        for event in sorted(events):
            if event == "afterAgentResponse":
                hooks[event] = [dict(hook_def)]
                continue
            bucket = hooks.setdefault(event, [])
            if not any(item.get("command") == hook_def["command"] for item in bucket):
                bucket.append(dict(hook_def))


SERVER_CHANNELS.register(HookInstallation)
