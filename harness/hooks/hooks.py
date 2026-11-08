"""The ``@Hook`` and ``@Hooks`` annotations, and the files an IDE reads to run hooks: ``hooks.json``, which names the hook
command for each event, and ``hook-handlers.json``, which lists the operations that command may run."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from harness.agent_tools.agent_tools import InstallDestination
from harness.annotations.annotation import Annotation, Destination
from harness.installation.ide_layout import IdeLayout


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


class InstalledHookHandlers:
    """The ``hook-handlers.json`` of every IDE folder in one checkout whose IDE runs hooks, read together: the toolsets
    the checkout's hook installs registered, whichever IDE each install was for."""

    def __init__(self, checkout: Path) -> None:
        self.files = [
            HookHandlersFile(checkout / layout.folder_name / HookHandlersFile.NAME)
            for layout in IdeLayout.every()
            if layout.runs_hooks
        ]

    @property
    def refs(self) -> tuple[str, ...]:
        """Each toolset reference any install's handlers name, once, in order."""
        return tuple(dict.fromkeys(ref for handlers in self.files for ref in handlers.refs))
