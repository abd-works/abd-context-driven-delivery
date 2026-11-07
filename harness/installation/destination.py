"""What install reads from a toolset beside its destinations: the omission annotations, the data annotations a language adapter
and every MCP answer read, and the Installation that writes one destination's files."""
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Callable

from harness.annotations.annotation import Annotation, OmissionAnnotation

InstallTracker = Callable[[Path], None]


class NoCatalog(OmissionAnnotation):
    """Omit this class or operation from the catalog.

    Install and deploy ignore this annotation. Use it when the behavior is real
    but not ready to show in the catalog.
    """

    flag = "_no_catalog"


class NoDeploy(OmissionAnnotation):
    """Omit this operation from install.

    Skill, command, MCP, and hook annotations on the same operation do not write
    files. The catalog can still list it.
    """

    flag = "_no_deploy"
    omits_install = True


noCatalog = NoCatalog
noDeploy = NoDeploy


class LanguageAdapter:
    """Deploy typed code in language for this toolset's MCP operations, so an application outside Python reaches them.

    The adapter names the object its operations act on by the class's `@identity` fields.
    """

    flag = "_language_adapters"

    def __init__(self, *, language: str) -> None:
        self.language = language

    def __call__(self, toolset: Any) -> Any:
        setattr(toolset, self.flag, (*getattr(toolset, self.flag, ()), self.language))
        return toolset


language_adapter = LanguageAdapter


class Identity:
    """Name the data fields (`@data_field`) that name one object of this class, such as a ticket's `name`; a fidelity's
    progress is named by its `ticket` and its `slug`. A subclass is named as its base is.

    A language adapter reads them as the arguments of the class's `@tool_subject` loader, in the same order, so code
    holding only an object's data knows which object its operations act on. A field annotated as a reference sends an
    object by these fields alone, so a ticket can name the column that holds it without sending the column again. An
    object nothing names, such as the one board, has none.
    """

    flag = "_identity_fields"

    def __init__(self, *fields: str) -> None:
        self.fields = fields

    def __call__(self, data_class: type) -> type:
        setattr(data_class, self.flag, self.fields)
        return data_class


identity = Identity


class ReferenceWithoutIdentityError(TypeError):
    """A field sends an object as a reference, but the object's class has no `@identity` to name it by."""

    def __init__(self, data_class: type) -> None:
        super().__init__(f"{data_class.__name__} is sent as a reference, so annotate the fields that name it with @identity")


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


edits = Edits


class DataField(Annotation):
    """Annotate a property as part of the object's data: what its tools answer with and what a language adapter types.

    Put it under `@property`. key is the name the data uses when it differs from the property's, such as a practice's
    `practice_slug` sent as `slug`. reference sends the object the property returns by its `@identity`
    alone: the object belongs to another, such as the column holding a ticket, which sends it in full.
    """

    flag = "_data_field"
    reference_flag = "_data_field_reference"
    copied = False

    def __new__(cls, target: Any = None, *, key: str = "", reference: bool = False):
        annotation = object.__new__(cls)
        annotation.key = key
        annotation.reference = reference
        if callable(target):
            return annotation.annotate(target)
        return annotation

    def annotate(self, getter: Any) -> Any:
        setattr(getter, self.flag, self.key or getter.__name__)
        setattr(getter, self.reference_flag, self.reference)
        return getter


data_field = DataField


class DataClass:
    """What the annotations on one class declare about its objects' data: the properties that are its data (`@data_field`),
    the fields that name one object (`@identity`), and the languages its operations are typed in
    (`@language_adapter`). A language adapter types the data from it, and `data_of` sends an object's data by it."""

    def __init__(self, data_class: type) -> None:
        self.data_class = data_class

    @property
    def fields(self) -> dict[str, property]:
        """The properties the class annotates as its data, by the name each takes in the data; a base class's come first.
        A subclass that overrides an annotated property, such as a card's title, is read through its own."""
        attributes: dict[str, str] = {}
        for klass in reversed(self.data_class.__mro__):
            for attribute, member in vars(klass).items():
                if isinstance(member, property) and DataField.annotates(member.fget):
                    attributes[getattr(member.fget, DataField.flag)] = attribute
        return {key: inspect.getattr_static(self.data_class, attribute) for key, attribute in attributes.items()}

    @property
    def identity(self) -> tuple[str, ...]:
        """The fields that name one object of the class, or none."""
        return tuple(getattr(self.data_class, Identity.flag, ()))

    @property
    def languages(self) -> tuple[str, ...]:
        """The languages the class's language adapters are written in."""
        return tuple(getattr(self.data_class, LanguageAdapter.flag, ()))

    def edited_by(self, operation: Any) -> tuple[str, ...]:
        """The fields of this class's data that operation's `@edits` annotation names, or none."""
        return tuple(getattr(operation, Edits.flag, ()))

    def sends_by_identity(self, field: property) -> bool:
        """Whether field sends the object it holds by that object's identity alone."""
        return bool(getattr(field.fget, DataField.reference_flag, False))

    def data(self, value: Any) -> dict[str, Any]:
        """value's annotated fields as plain data."""
        return {key: self._field_data(field, value) for key, field in self.fields.items()}

    def reference(self, value: Any) -> dict[str, Any]:
        """value by its identity alone, such as `{"name": "Discovery"}` for a stage, so data can name an object that is
        sent in full elsewhere without sending it again. An identity field that holds an object with an identity of its
        own sends that object by its reference too, so a fidelity's progress is `{ticket: {name}, fidelity: {slug}}`."""
        if not self.identity:
            raise ReferenceWithoutIdentityError(self.data_class)
        fields = self.fields
        return {key: self._identity_data(fields[key].fget(value)) for key in self.identity}

    def _field_data(self, field: property, value: Any) -> Any:
        held = field.fget(value)
        return self._referenced(held) if self.sends_by_identity(field) else data_of(held)

    def _identity_data(self, held: Any) -> Any:
        return DataClass(type(held)).reference(held) if held is not None and DataClass(type(held)).identity else data_of(held)

    def _referenced(self, held: Any) -> Any:
        if held is None:
            return None
        if isinstance(held, (list, tuple)):
            return [self._referenced(item) for item in held]
        return DataClass(type(held)).reference(held)


def data_of(value: Any) -> Any:
    """value as plain JSON data: an object with annotated properties as its fields, each object it holds as its own data.

    This is the one way a value of any type becomes data, for MCP results and every other JSON answer, so a path reads
    the same wherever it is sent: with forward slashes."""
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {key: data_of(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [data_of(item) for item in value]
    data_class = DataClass(type(value))
    return data_class.data(value) if not isinstance(value, type) and data_class.fields else value


class SourceFile:
    """Annotates a data field that holds a path in the session's workspace: `path: Annotated[str, SourceFile]`.

    A generated view draws an annotated field as a link that opens the file in the shared source view, at the `line`, or
    the `start_line` to `end_line` range, that the same data holds.
    """


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

    def track_writes_with(self, tracker: InstallTracker) -> None:
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
