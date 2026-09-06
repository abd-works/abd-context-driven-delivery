"""Cursor hook annotation and deployment.

Usage::

    from hooks.hook import hook, HookHarness

    @toolset
    class Turn:
        @prompt(name="turn")
        @agent_tool
        def turn(self, *, message: str = "") -> TurnCommit | None:
            ...

        @hook(event="beforeSubmitPrompt")
        def auto_turn(self, payload: dict) -> dict:
            return {"permission": "allow"}

    HookHarness(script="primitives/hooks/run.py").deploy(Path(".cursor/hooks.json"))
"""
from __future__ import annotations

import functools
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

CURSOR_EVENTS: frozenset[str] = frozenset({
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
})


def _balloon_notify(event: str) -> None:
    """Fire a non-blocking Windows balloon-tip notification for *event*."""
    script = Path(__file__).resolve().parent / "_notify_test.ps1"
    if script.exists():
        subprocess.Popen(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-Message",
                f"Hook fired: {event}",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


class Hook:
    """Decorator that registers a callable as a Cursor hook handler.

    Apply to a method on a toolset class. Harness deploy discovers ``@hook``
    / ``@Hook`` and wires entries into ``.cursor/hooks.json``.

    Parameters
    ----------
    event:
        A valid ``CURSOR_EVENTS`` name.
    matcher:
        Optional regex matched against the tool name (``preToolUse`` only).
    timeout:
        Seconds before Cursor abandons the hook process.
    fail_closed:
        When ``True`` Cursor blocks the action if the hook times out.
    notify:
        When ``True`` fire a desktop notification each time the handler runs.
    notifier:
        Override the notification callable (default: ``_balloon_notify``).
        Receives the event name string.  Useful for testing.
    """

    _registry: list[dict[str, Any]] = []

    def __init__(
        self,
        *,
        event: str,
        matcher: str | None = None,
        timeout: int = 10,
        fail_closed: bool = False,
        notify: bool = False,
        notifier: Callable[[str], None] | None = None,
    ) -> None:
        if event not in CURSOR_EVENTS:
            raise ValueError(
                f"Unknown Cursor event {event!r}. "
                f"Valid events: {sorted(CURSOR_EVENTS)}"
            )
        self.event = event
        self.matcher = matcher
        self.timeout = timeout
        self.fail_closed = fail_closed
        self.notify = notify
        self.notifier: Callable[[str], None] = notifier or _balloon_notify

    def __call__(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        writes = list(getattr(fn, "_harness_writes", []))
        writes.append(("hook", self.event))
        fn._harness_writes = writes

        if self.notify:
            _notifier = self.notifier
            _event = self.event

            @functools.wraps(fn)
            def _wrapped(*args: Any, **kwargs: Any) -> Any:
                _notifier(_event)
                return fn(*args, **kwargs)

            _wrapped._hook_event = _event  # type: ignore[attr-defined]
            _wrapped._hook_meta = {  # type: ignore[attr-defined]
                "event": self.event,
                "matcher": self.matcher,
                "timeout": self.timeout,
                "fail_closed": self.fail_closed,
            }
            _wrapped._harness_writes = fn._harness_writes
            target = _wrapped
        else:
            fn._hook_event = self.event  # type: ignore[attr-defined]
            fn._hook_meta = {  # type: ignore[attr-defined]
                "event": self.event,
                "matcher": self.matcher,
                "timeout": self.timeout,
                "fail_closed": self.fail_closed,
            }
            target = fn

        Hook._registry.append(
            {
                "event": self.event,
                "handler": target,
                "matcher": self.matcher,
                "timeout": self.timeout,
                "fail_closed": self.fail_closed,
                "owner": None,
                "method": getattr(fn, "__name__", ""),
            }
        )
        return target

    @classmethod
    def attach_owners(cls, toolset_cls: type) -> None:
        """Bind registered handlers to *toolset_cls* after ``@toolset`` merges."""
        import inspect

        for name, member in inspect.getmembers(toolset_cls, predicate=inspect.isfunction):
            meta = getattr(member, "_hook_meta", None)
            event = getattr(member, "_hook_event", None)
            if not event and not meta:
                continue
            matched = False
            for entry in cls._registry:
                if entry.get("owner") is not None:
                    continue
                handler = entry["handler"]
                if entry.get("method") != name:
                    continue
                declared = vars(toolset_cls).get(name)
                if declared is None:
                    continue
                if declared is handler or getattr(declared, "_hook_event", None) == entry["event"]:
                    entry["owner"] = toolset_cls
                    entry["method"] = name
                    matched = True
            if matched:
                continue
            if meta is None:
                continue
            cls._registry.append(
                {
                    **meta,
                    "handler": member,
                    "owner": toolset_cls,
                    "method": name,
                }
            )

    @staticmethod
    def normalize_event(event: str) -> str:
        import re

        normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", event)
        return normalized.replace("-", "_").lower()

    @classmethod
    def toggle_flag(cls, owner: type, method: str, event: str) -> Path:
        slug = owner.__name__.lower()
        norm = cls.normalize_event(event)
        root = Path(__file__).resolve().parents[2]
        return root / ".context" / "hooks" / slug / f"{method}_{norm}.enabled"

    @classmethod
    def is_enabled(cls, owner: type, method: str, event: str) -> bool:
        return cls.toggle_flag(owner, method, event).is_file()

    @classmethod
    def set_enabled(cls, owner: type, method: str, event: str, *, enabled: bool) -> Path:
        path = cls.toggle_flag(owner, method, event)
        path.parent.mkdir(parents=True, exist_ok=True)
        if enabled:
            path.write_text("", encoding="utf-8")
        elif path.is_file():
            path.unlink()
        return path

    @classmethod
    def bindings_for(cls, event: str) -> list[dict[str, Any]]:
        return [
            entry
            for entry in cls._registry
            if entry["event"] == event and entry.get("owner") is not None
        ]

    @classmethod
    def registered(cls) -> list[dict[str, Any]]:
        """Return a snapshot of all currently registered hook entries."""
        return list(cls._registry)

    @classmethod
    def clear(cls) -> None:
        """Remove all registered entries (useful between tests)."""
        cls._registry.clear()


def hook(
    fn: Callable[..., Any] | None = None,
    *,
    event: str,
    matcher: str | None = None,
    timeout: int = 10,
    fail_closed: bool = False,
    notify: bool = False,
    notifier: Callable[[str], None] | None = None,
) -> Callable[..., Any]:
    """Register a Cursor hook handler (lowercase alias for ``Hook``)."""
    deco = Hook(
        event=event,
        matcher=matcher,
        timeout=timeout,
        fail_closed=fail_closed,
        notify=notify,
        notifier=notifier,
    )
    return deco if fn is None else deco(fn)


class HookHarness:
    """Writes registered Hook handlers into a Cursor ``hooks.json`` file.

    Parameters
    ----------
    script:
        Path (or command fragment) used as the ``command`` in hooks.json.
    python:
        Python executable to prefix the script with.
    """

    def __init__(
        self,
        script: str,
        *,
        python: str = ".venv/Scripts/python.exe",
    ) -> None:
        self.script = script
        self.python = python

    def deploy(
        self,
        hooks_json_path: Path,
        registry: list[dict[str, Any]] | None = None,
        *,
        merge: bool = False,
    ) -> None:
        """Write or update *hooks_json_path* with entries for every registered hook.

        Parameters
        ----------
        hooks_json_path:
            Destination file (usually ``.cursor/hooks.json``).
        registry:
            Override the global ``Hook.registered()`` snapshot; useful in tests.
        merge:
            When ``True``, preserve existing hook entries and append new ones.
        """
        entries = registry if registry is not None else Hook.registered()
        hooks: dict[str, list[dict[str, Any]]] = {}

        if merge and hooks_json_path.is_file():
            try:
                existing = json.loads(hooks_json_path.read_text(encoding="utf-8"))
                hooks = dict(existing.get("hooks") or {})
            except (OSError, json.JSONDecodeError):
                hooks = {}

        for entry in entries:
            event = entry["event"]
            hook_def: dict[str, Any] = {
                "command": f"{self.python} {self.script}",
                "timeout": entry["timeout"],
                "failClosed": entry["fail_closed"],
            }
            if entry["matcher"] is not None:
                hook_def["matcher"] = entry["matcher"]
            bucket = hooks.setdefault(event, [])
            if not any(item.get("command") == hook_def["command"] for item in bucket):
                bucket.append(hook_def)

        data = {"version": 1, "hooks": hooks}
        hooks_json_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def ensure_dispatch(
        self,
        hooks_json_path: Path,
        events: set[str] | frozenset[str],
    ) -> None:
        """Wire dispatch entries for *events* and drop stale dispatch entries elsewhere."""
        self.sync_dispatch(hooks_json_path, events)

    def sync_dispatch(
        self,
        hooks_json_path: Path,
        events: set[str] | frozenset[str],
    ) -> None:
        """Set dispatch wiring exactly to *events*; preserve other hook commands."""
        dispatch_cmd = f"{self.python} {self.script}"
        hooks: dict[str, list[dict[str, Any]]] = {}

        if hooks_json_path.is_file():
            try:
                existing = json.loads(hooks_json_path.read_text(encoding="utf-8"))
                hooks = dict(existing.get("hooks") or {})
            except (OSError, json.JSONDecodeError):
                hooks = {}

        for event_name in list(hooks.keys()):
            bucket = hooks[event_name]
            kept = [item for item in bucket if item.get("command") != dispatch_cmd]
            if kept:
                hooks[event_name] = kept
            else:
                del hooks[event_name]

        hook_def: dict[str, Any] = {
            "command": dispatch_cmd,
            "timeout": 30,
            "failClosed": False,
        }
        for event in sorted(events):
            bucket = hooks.setdefault(event, [])
            if not any(item.get("command") == dispatch_cmd for item in bucket):
                bucket.append(hook_def)

        data = {"version": 1, "hooks": hooks}
        hooks_json_path.parent.mkdir(parents=True, exist_ok=True)
        hooks_json_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
