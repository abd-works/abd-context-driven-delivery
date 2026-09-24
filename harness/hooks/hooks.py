"""Cursor hook mark and hook install — one destination packager."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from installation.destination import Destination, Installation


class Hooks:
    """Class annotation: disable every hook operation on the toolset."""

    def __new__(cls, target: Any = None, *, disabled: bool = False):
        inst = object.__new__(cls)
        inst.disabled = disabled
        if isinstance(target, type):
            return inst.annotate(target)
        return inst

    def __call__(self, cls: type) -> type:
        return self.annotate(cls)

    def annotate(self, cls: type) -> type:
        cls._hooks_disabled = self.disabled
        return cls


class Hook(Destination):
    flag = "_hook"
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
            "beforeReadFile",
            "subagentStart",
        }
    )

    def __new__(cls, fn: Any = None, event: str | None = None):
        if isinstance(fn, str):
            event = fn
            fn = None
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
        if callable(fn):
            return inst.annotate(fn)
        return inst

    @classmethod
    def normalize_event(cls, event: str) -> str:
        stepped = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", event)
        return stepped.replace("-", "_").lower()


hook = Hook
hooks = Hooks

class HookInstallation(Installation):
    """Write Cursor ``hooks.json`` dispatch and ``hook-handlers.json`` refs."""

    channel = "hook"
    DISPATCH_SCRIPT = "harness/hooks/hook_server.py"

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
        self.server: Any = None
        self.diagnosis: dict[str, Any] | None = None

    @property
    def dispatch_command(self) -> str:
        repo = self.repo or Path(__file__).resolve().parents[2]
        script = (repo / self.DISPATCH_SCRIPT).resolve()
        return f"{self.python} -u {script}"

    def write(self, tool: Any) -> None:
        if not tool.install_to_hook:
            return
        if tool.name == "inject_rules":
            host = type(getattr(tool, "toolset", None)).__name__
            if host in {"RulesCollection", "FidelityGuidance"}:
                return
        event = getattr(tool.callable, "_hook_name", None)
        if not event:
            return
        self._handlers.append(
            {
                "event": str(event),
                "operation": tool.name,
                "ref": tool.registration_name,
            }
        )
        self.write_hooks_manifest()
        self.write_handlers()

    def write_handlers(self) -> None:
        if not self._handlers:
            return
        dest = self.path / "hook-handlers.json"
        dest.write_text(
            json.dumps({"handlers": self._handlers}, indent=2) + "\n",
            encoding="utf-8",
        )
        self.track_write(dest)

    def write_hooks_manifest(self) -> None:
        if not self._handlers:
            return
        dest = self.path / "hooks.json"
        hooks = self._existing_hooks(dest)
        self._strip_dispatch_command(hooks)
        self._attach_dispatch_command(hooks)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(
            json.dumps({"version": 1, "hooks": hooks}, indent=2) + "\n",
            encoding="utf-8",
        )
        self.track_write(dest)

    def _existing_hooks(self, dest: Path) -> dict[str, list[dict[str, Any]]]:
        if not dest.is_file():
            return {}
        try:
            existing = json.loads(dest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return dict(existing.get("hooks") or {})

    def _strip_dispatch_command(self, hooks: dict[str, list[dict[str, Any]]]) -> None:
        dispatch_cmd = self.dispatch_command
        for event_name in list(hooks.keys()):
            kept = [item for item in hooks[event_name] if item.get("command") != dispatch_cmd]
            if kept:
                hooks[event_name] = kept
            else:
                del hooks[event_name]

    def _attach_dispatch_command(self, hooks: dict[str, list[dict[str, Any]]]) -> None:
        hook_def: dict[str, Any] = {
            "command": self.dispatch_command,
            "timeout": 30,
            "failClosed": False,
        }
        for event in sorted({item["event"] for item in self._handlers}):
            if event == "afterAgentResponse":
                hooks[event] = [dict(hook_def)]
                continue
            bucket = hooks.setdefault(event, [])
            if not any(item.get("command") == hook_def["command"] for item in bucket):
                bucket.append(dict(hook_def))

    def standup(self) -> Any:
        from harness.hooks.hook_server import HookServer

        self.server = HookServer.from_handlers(
            self.path / "hook-handlers.json", repo=self.repo
        )
        return self.server

    def diagnose(self) -> dict[str, Any]:
        server = self.server if self.server is not None else self.standup()
        self.diagnosis = server.diagnose()
        return self.diagnosis
