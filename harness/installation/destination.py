"""Destination mark and Installation write channel — no hook or installer import."""
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Callable

InstallTracker = Callable[[Path], None]


_NO_CATALOG_FLAG = "_no_catalog"
_NO_DEPLOY_FLAG = "_no_deploy"
_LANGUAGE_ADAPTERS_FLAG = "_language_adapters"
_IDENTITY_FLAG = "_language_adapter_identity"
_EDITS_FLAG = "_language_adapter_edits"
_DATA_FIELD_FLAG = "_data_field"


def noCatalog(target: Any = None) -> Any:
    """Omit this class or operation from the catalog.

    Install and deploy ignore this mark. Use it when the behavior is real
    but not ready to show in the catalog.
    """

    def mark(obj: Any) -> Any:
        setattr(obj, _NO_CATALOG_FLAG, True)
        return obj

    if target is None:
        return mark
    return mark(target)


def noDeploy(target: Any = None) -> Any:
    """Omit this operation from install.

    Skill, command, MCP, and hook marks on the same operation do not write
    files. The catalog can still list it.
    """

    def mark(obj: Any) -> Any:
        setattr(obj, _NO_DEPLOY_FLAG, True)
        return obj

    if target is None:
        return mark
    return mark(target)


def language_adapter(*, language: str, identity: str | tuple[str, ...] = "") -> Callable[[Any], Any]:
    """Deploy typed code in language for this toolset's MCP operations, so an application outside Python reaches them.

    identity names the data fields (`@data_field`) that hold the object's name, one for each argument its
    `@tool_subject` loader takes, in the same order, so code holding only that data knows which object its operations
    act on. A fidelity's progress is named by its ticket and its slug. An object its tools never load by name, such as
    the one board, has none.
    """

    def mark(toolset: Any) -> Any:
        setattr(toolset, _LANGUAGE_ADAPTERS_FLAG, (*languages_of(toolset), language))
        if identity:
            setattr(toolset, _IDENTITY_FLAG, (identity,) if isinstance(identity, str) else tuple(identity))
        return toolset

    return mark


def languages_of(toolset: Any) -> tuple[str, ...]:
    """The languages a toolset's class is marked for."""
    return tuple(getattr(toolset, _LANGUAGE_ADAPTERS_FLAG, ()))


def identity_fields_of(toolset: Any) -> tuple[str, ...]:
    """The fields of the toolset's data that name one object, or none when its tools load none by name."""
    return tuple(getattr(toolset, _IDENTITY_FLAG, ()))


def edits(*fields: str) -> Callable[[Any], Any]:
    """Name the fields of the object's data this operation changes, when its argument names do not match them.

    A generated view shows a field as an input only where an operation changes it, so this is how an operation whose
    argument is called something else, such as `rename(new_title)`, still makes `title` editable.
    """

    def mark(operation: Any) -> Any:
        setattr(operation, _EDITS_FLAG, fields)
        return operation

    return mark


def edited_fields_of(operation: Any) -> tuple[str, ...]:
    """The fields an operation's `@edits` mark names, or none."""
    return tuple(getattr(operation, _EDITS_FLAG, ()))


def data_field(target: Any = None, *, key: str = "") -> Any:
    """Mark a property as part of the object's data: what its tools answer with and what a language adapter types.

    Put it under `@property`. key is the name the data uses when it differs from the property's, such as a ticket's
    `column_name` sent as `column`, because the property of that name returns the column itself.
    """

    def mark(getter: Any) -> Any:
        setattr(getter, _DATA_FIELD_FLAG, key or getter.__name__)
        return getter

    if target is None:
        return mark
    return mark(target)


def data_fields_of(cls: type) -> dict[str, property]:
    """The properties a class marks as its data, by the name each takes in the data; a base class's come first. A
    subclass that overrides a marked property, such as a card's title, is read through its own."""
    attributes: dict[str, str] = {}
    for klass in reversed(cls.__mro__):
        for attribute, member in vars(klass).items():
            if isinstance(member, property) and hasattr(member.fget, _DATA_FIELD_FLAG):
                attributes[getattr(member.fget, _DATA_FIELD_FLAG)] = attribute
    return {key: inspect.getattr_static(cls, attribute) for key, attribute in attributes.items()}


def data_of(value: Any) -> Any:
    """value as plain JSON data: an object with marked properties as its fields, each object it holds as its own data."""
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {key: data_of(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [data_of(item) for item in value]
    fields = data_fields_of(type(value)) if not isinstance(value, type) else {}
    if fields:
        return {key: data_of(field.fget(value)) for key, field in fields.items()}
    return value


class SourceFile:
    """Marks a data field that holds a path in the session's workspace: `path: Annotated[str, SourceFile]`.

    A generated view draws a marked field as a link that opens the file in the shared source view, at the `line`, or
    the `start_line` to `end_line` range, that the same data holds.
    """


def omitted_from_catalog(obj: Any) -> bool:
    """True when ``obj`` or its underlying function carries ``@noCatalog``."""
    if getattr(obj, _NO_CATALOG_FLAG, False):
        return True
    fn = getattr(obj, "__func__", None)
    return bool(fn is not None and getattr(fn, _NO_CATALOG_FLAG, False))


def omitted_from_deploy(obj: Any) -> bool:
    """True when ``obj`` or its underlying function carries ``@noDeploy``."""
    if getattr(obj, _NO_DEPLOY_FLAG, False):
        return True
    fn = getattr(obj, "__func__", None)
    return bool(fn is not None and getattr(fn, _NO_DEPLOY_FLAG, False))


class Destination:
    """Base annotation to define the installation destination of a tool."""

    flag = ""

    def annotate(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        setattr(fn, self.flag, True)
        name = getattr(self, "name", None)
        if name is not None:
            setattr(fn, f"{self.flag}_name", name)
        return fn

    def __call__(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        return self.annotate(fn)


class Installation:
    """``install(tool)`` writes the channel; subclass ``write``."""

    channel = ""

    def __init__(
        self,
        ide: str,
        path: Path | str,
        toolset_ref: str = "",
        repo: Path | str | None = None,
    ) -> None:
        self.ide = ide
        self.path = Path(path)
        self.toolset_ref = toolset_ref
        self.repo = Path(repo).resolve() if repo is not None else None
        self._install_tracker: InstallTracker | None = None

    def bind_tracker(self, tracker: InstallTracker) -> None:
        self._install_tracker = tracker

    def track_write(self, dest: Path) -> None:
        if self._install_tracker is not None:
            self._install_tracker(dest)

    def folder_for(self, toolset: Any) -> Path:
        """Repo-relative package folder the toolset already knows (practice dir, fidelity leaf)."""
        raw = getattr(toolset, "install_folder", None)
        if raw is None:
            slug = getattr(toolset, "slug", None) or "toolset"
            return Path(str(slug))
        folder = self._guidance_source_folder(Path(raw))
        repo = self.repo
        if repo is None:
            return folder
        try:
            relative = folder.resolve().relative_to(repo)
        except ValueError:
            return Path(folder.name)
        return self._guidance_source_folder(relative)

    def _guidance_source_folder(self, folder: Path) -> Path:
        """Installed skills stay at practices/ and actions/, under the guidance package."""
        if folder.parts[:1] == ("cdd_guidance",):
            rest = folder.parts[1:]
            return Path(*rest) if rest else Path(".")
        return folder

    def install(self, tool: Any) -> None:
        self.write(tool)

    def write(self, tool: Any) -> None:
        raise NotImplementedError
