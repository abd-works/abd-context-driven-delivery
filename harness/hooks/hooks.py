"""The ``@Hook``, ``@Hooks`` and ``@Toast`` annotations, and the files an IDE reads to run hooks: ``hooks.json``, which names the hook
command for each event, and ``hook-handlers.json``, which lists the operations that command may run."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from harness.agent_tools.agent_tools import ToolsetReference
from harness.annotations.annotation import Annotation, Destination
from harness.installation.ide_layout import IdeLayout
from harness.installation.json_file import JsonFile, JsonFileUnreadable


class Hooks(Annotation):
    """Class annotation on a toolset: ``@Hooks(disabled=True)`` turns off every hook operation on it, and
    ``deploy=False`` keeps them out of install. The hook server and the hook install read it through
    ``Hooks.from_toolset_class``, so a subclass carries its base's setting."""

    flag = "_hooks"
    copied = False

    def __new__(cls: type[Hooks], target: type | None = None, *, disabled: bool = False, deploy: bool = True) -> Hooks | type:
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
    def from_toolset_class(cls, toolset_class: type) -> Hooks:
        """The ``@Hooks`` annotation on toolset_class or a class it derives from; a class annotated with none has every
        hook on and deployed."""
        return getattr(toolset_class, cls.flag, None) or cls()


class Toast(Destination):
    """Annotate an operation or instructions so the IDE shows a toast naming it when an agent calls it. The notifier
    the hook server shows toasts with reads this annotation; the operation names no notifier."""

    flag = "_toast"


class Hook(Destination):
    """``@Hook("event")``: the IDE runs the operation on that event; ``disabled=True`` keeps the hook there but turned
    off, which the destination records on the operation."""

    flag = "_hook"
    channel = "hook"
    enlists_member = True
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

    def __new__(
        cls: type[Hook], target: Callable[..., object] | str | None = None, event: str | None = None, *, disabled: bool = False
    ) -> Hook | Callable[..., object]:
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


hook = Hook
hooks = Hooks

# Cursor reports a file edit under afterFileEdit as well as postToolUse, so a postToolUse hook answers both.
_ALSO_SERVES = {"postToolUse": ("afterFileEdit",)}


def events_served(event: str) -> tuple[str, ...]:
    """The IDE events a hook annotated for event answers: event itself, and those the IDE reports the same thing
    under."""
    return (event, *_ALSO_SERVES.get(event, ()))


class HooksFileUnreadable(JsonFileUnreadable):
    """A hooks file an install reads is not the JSON object it should be. The install stops rather than write over
    it, because the file can hold hooks the person added by hand."""

    def message(self, path: Path, cause: Exception) -> str:
        return f"{path} is not readable hook JSON ({cause}); fix or remove it, then install again"


class _HooksJsonFile:
    """One JSON object file an install keeps in an IDE folder; a missing file reads as empty."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._file = JsonFile(self.path, HooksFileUnreadable)


class HookHandlersFile(_HooksJsonFile):
    """``hook-handlers.json``: the hook operations an install registered, each with its event and its toolset's
    reference. The hook server loads those toolsets; the installer's diagnosis counts the operations."""

    NAME = "hook-handlers.json"

    @property
    def handlers(self) -> list[dict[str, str]]:
        return [dict(item) for item in self._file.read().get("handlers") or [] if isinstance(item, dict)]

    @property
    def refs(self) -> tuple[ToolsetReference, ...]:
        """Each toolset reference the handlers name, once, in order, parsed from the text the file holds."""
        return tuple(dict.fromkeys(ToolsetReference.parsed(str(item["ref"])) for item in self.handlers if item.get("ref")))

    @property
    def operation_names(self) -> list[str]:
        """Each registered operation's name, once, sorted."""
        return sorted({str(item["operation"]) for item in self.handlers if item.get("operation")})

    def write(self, handlers: list[dict[str, str]]) -> None:
        self._file.write({"handlers": handlers})


class HooksManifest(_HooksJsonFile):
    """``hooks.json``: the command an IDE runs for each hook event. It may hold the person's own hooks beside CDD's,
    so an install changes only CDD's command and keeps the rest."""

    NAME = "hooks.json"

    @property
    def hooks(self) -> dict[str, list[dict[str, Any]]]:
        hooks = self._file.read().get("hooks") or {}
        if not isinstance(hooks, dict):
            raise HooksFileUnreadable(self.path, TypeError("its hooks are not an object"))
        return {str(event): list(items) for event, items in hooks.items()}

    @property
    def registered_events(self) -> list[str]:
        return sorted(event for event in self.hooks if event)

    def write(self, hooks: dict[str, list[dict[str, Any]]]) -> None:
        self._file.write({"version": 1, "hooks": hooks})


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
    def refs(self) -> tuple[ToolsetReference, ...]:
        """Each toolset reference any install's handlers name, once, in order."""
        return tuple(dict.fromkeys(ref for handlers in self.files for ref in handlers.refs))
