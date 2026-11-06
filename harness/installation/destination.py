"""Destination mark and Installation write channel — no hook or installer import."""
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Callable

InstallTracker = Callable[[Path], None]


_NO_CATALOG_FLAG = "_no_catalog"
_NO_DEPLOY_FLAG = "_no_deploy"
_DATA_FIELD_FLAG = "_data_field"


class Mark:
    """A decorator that marks the operation or class it decorates, by setting its ``flag`` on it, so install and
    discovery can find what it marks. Each kind of mark is a subclass that names its flag and reads it with
    ``marks``; together the subclasses are the one list of marks."""

    flag = ""
    # A wrapper of a marked operation, such as a collected or markdown property, copies the marks whose kinds say so,
    # so the wrapper installs the way the operation does.
    copied = True
    _kinds: list[type[Mark]] = []

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls.flag and all(kind.flag != cls.flag for kind in Mark._kinds):
            Mark._kinds.append(cls)

    def __new__(cls, target: Any = None):
        mark = object.__new__(cls)
        if callable(target):
            return mark.annotate(target)
        return mark

    @classmethod
    def marks(cls, target: Any) -> bool:
        """True when this kind of mark is on target."""
        return bool(getattr(target, cls.flag, False))

    @classmethod
    def copied_flags(cls) -> tuple[str, ...]:
        """Every attribute a wrapper copies from the operation it wraps: each copied kind's flag and the attributes that
        go with it, such as the name a skill mark gives."""
        flags: list[str] = []
        for kind in Mark._kinds:
            if kind.copied:
                flags.extend((kind.flag, *kind.companion_flags()))
        return tuple(dict.fromkeys(flags))

    @classmethod
    def companion_flags(cls) -> tuple[str, ...]:
        """The other attributes this kind of mark sets beside its flag."""
        return ()

    def annotate(self, target: Any) -> Any:
        setattr(target, self.flag, True)
        return target

    def __call__(self, target: Any) -> Any:
        return self.annotate(target)


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


class LanguageAdapter:
    """Deploy typed code in language for this toolset's MCP operations, so an application outside Python reaches them.

    identity names the data fields (`@data_field`) that hold the object's name, one for each argument its
    `@tool_subject` loader takes, in the same order, so code holding only that data knows which object its operations
    act on. A fidelity's progress is named by its ticket and its slug. An object its tools never load by name, such as
    the one board, has none.
    """

    flag = "_language_adapters"
    identity_flag = "_language_adapter_identity"

    def __init__(self, *, language: str, identity: str | tuple[str, ...] = "") -> None:
        self.language = language
        self.identity = (identity,) if isinstance(identity, str) and identity else tuple(identity or ())

    def __call__(self, toolset: Any) -> Any:
        setattr(toolset, self.flag, (*self.languages_of(toolset), self.language))
        if self.identity:
            setattr(toolset, self.identity_flag, self.identity)
        return toolset

    @classmethod
    def languages_of(cls, toolset: Any) -> tuple[str, ...]:
        """The languages a toolset's class is marked for."""
        return tuple(getattr(toolset, cls.flag, ()))

    @classmethod
    def identity_fields_of(cls, toolset: Any) -> tuple[str, ...]:
        """The fields of the toolset's data that name one object, or none when its tools load none by name."""
        return tuple(getattr(toolset, cls.identity_flag, ()))


language_adapter = LanguageAdapter


class Edits:
    """Name the fields of the object's data this operation changes, when its argument names do not match them.

    A generated view shows a field as an input only where an operation changes it, so this is how an operation whose
    argument is called something else, such as `rename(new_title)`, still makes `title` editable.
    """

    flag = "_language_adapter_edits"

    def __init__(self, *fields: str) -> None:
        self.fields = fields

    def __call__(self, operation: Any) -> Any:
        setattr(operation, self.flag, self.fields)
        return operation

    @classmethod
    def fields_of(cls, operation: Any) -> tuple[str, ...]:
        """The fields an operation's `@edits` mark names, or none."""
        return tuple(getattr(operation, cls.flag, ()))


edits = Edits


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
    """value as plain JSON data: an object with marked properties as its fields, each object it holds as its own data.

    This is the one way an object becomes data, for MCP results and every other JSON answer, so a path reads the same
    wherever it is sent: with forward slashes."""
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


class Destination(Mark):
    """Base annotation to define the installation destination of a tool."""

    def annotate(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        setattr(fn, self.flag, True)
        name = getattr(self, "name", None)
        if name is not None:
            setattr(fn, f"{self.flag}_name", name)
        return fn

    @classmethod
    def name_marked_on(cls, operation: Any) -> str:
        """The name this destination's mark gave the operation, such as the event a hook runs on; empty when the
        operation carries no such mark."""
        return str(getattr(operation, f"{cls.flag}_name", "") or "")

    @classmethod
    def companion_flags(cls) -> tuple[str, ...]:
        return (f"{cls.flag}_name",)


class NamedDestination(Destination):
    """A destination whose mark may name what it installs: ``@skill("name")``, ``@skill(name="name")``, or bare
    ``@skill`` for the operation's own name."""

    def __new__(cls, fn: Any = None, name: str | None = None):
        mark = object.__new__(cls)
        if isinstance(fn, str):
            mark.name = fn
            return mark
        mark.name = name
        if callable(fn):
            return mark.annotate(fn)
        return mark


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
