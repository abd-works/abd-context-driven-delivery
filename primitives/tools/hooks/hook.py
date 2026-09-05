"""Cursor hook annotation and deployment harness.

Usage::

    from tools.hooks.hook import Hook, HookHarness

    class MyHooks:
        @Hook(event="preToolUse", matcher="Write|StrReplace")
        def on_write(self, payload: dict) -> dict:
            return {"permission": "allow"}

    HookHarness(script="primitives/hooks/my_hooks.py").deploy(
        Path(".cursor/hooks.json")
    )
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
    script = Path(__file__).resolve().parents[2] / "hooks" / "_notify_test.ps1"
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

    Apply to a method to bind it to a Cursor lifecycle event.  Call
    ``Hook.registered()`` to inspect the full registry or pass it to
    ``HookHarness.deploy()``.

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
        if self.notify:
            _notifier = self.notifier
            _event = self.event

            @functools.wraps(fn)
            def _wrapped(*args: Any, **kwargs: Any) -> Any:
                _notifier(_event)
                return fn(*args, **kwargs)

            _wrapped._hook_event = _event  # type: ignore[attr-defined]
            target = _wrapped
        else:
            fn._hook_event = self.event  # type: ignore[attr-defined]
            target = fn

        Hook._registry.append(
            {
                "event": self.event,
                "handler": target,
                "matcher": self.matcher,
                "timeout": self.timeout,
                "fail_closed": self.fail_closed,
            }
        )
        return target

    @classmethod
    def registered(cls) -> list[dict[str, Any]]:
        """Return a snapshot of all currently registered hook entries."""
        return list(cls._registry)

    @classmethod
    def clear(cls) -> None:
        """Remove all registered entries (useful between tests)."""
        cls._registry.clear()


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
    ) -> None:
        """Write or update *hooks_json_path* with entries for every registered hook.

        Parameters
        ----------
        hooks_json_path:
            Destination file (usually ``.cursor/hooks.json``).
        registry:
            Override the global ``Hook.registered()`` snapshot; useful in tests.
        """
        entries = registry if registry is not None else Hook.registered()
        hooks: dict[str, list[dict[str, Any]]] = {}

        for entry in entries:
            event = entry["event"]
            hook_def: dict[str, Any] = {
                "command": f"{self.python} {self.script}",
                "timeout": entry["timeout"],
                "failClosed": entry["fail_closed"],
            }
            if entry["matcher"] is not None:
                hook_def["matcher"] = entry["matcher"]
            hooks.setdefault(event, []).append(hook_def)

        data = {"version": 1, "hooks": hooks}
        hooks_json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
