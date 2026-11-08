"""*HookInstallation*, the hook channel of an install: it writes the IDE's ``hooks.json`` and ``hook-handlers.json``,
then starts and reports the checkout's hook daemon. Importing this module registers it with the Installer; importing the
``harness.hooks`` package imports it."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from harness.agent_tools.agent_tools import AgentTool
from harness.hooks.hook_daemon import HookDaemon
from harness.hooks.hook_server import HookServer
from harness.hooks.hooks import Hook, HookHandlersFile, Hooks, HooksManifest
from harness.installation.destination import ServerInstallation
from harness.installation.ide_layout import IdeLayout
from harness.installation.installer import Installer
from harness.process.process import PythonInterpreter

# How long the IDE waits for the hook command before it carries on without the hooks' answer.
_HOOK_COMMAND_TIMEOUT_SECONDS = 30


class HookServerNotRunning(Exception):
    """The install finished but the checkout's hook daemon does not answer, so hooks would not run."""

    def __init__(self, repo: Path) -> None:
        super().__init__(f"install failed: the hook server of {repo} is not running")
        self.repo = repo




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
        return f"{self.interpreter.console} -u {HookDaemon.COMMAND_SCRIPT}"

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
        events = {served for item in self._handlers for served in Hook.events_served(item["event"])}
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

    def standup(self) -> HookServer:
        self.server = HookServer.from_handlers(self.handlers_file.path, repo=self.repo or self.path)
        return self.server

    def diagnose(self) -> dict[str, Any]:
        server = self.server if self.server is not None else self.standup()
        self.diagnosis = server.diagnose()
        return self.diagnosis


Installer.installs_through(HookInstallation)
