"""The data annotations on a class and its members, and what they declare about its objects' data: the fields that are
its data, the fields that name one object, the languages its operations are typed in, the fields an operation edits,
and the fields that hold a path in the workspace. A language adapter types the data from them, and every MCP answer
sends an object's data by them (`data_of`)."""
from __future__ import annotations

import functools
import inspect
from enum import Enum
from pathlib import Path
from typing import Any

from harness.annotations.annotation import Annotation, NamesAnnotation


class LanguageAdapter(Annotation):
    """Deploy typed code in language for this toolset's MCP operations, so an application outside Python reaches them.

    The adapter names the object its operations act on by the class's `@identity` fields. `shares_file_views=True`
    marks the toolset whose generated client the shared file views import to read files, the file manager's.
    """

    flag = "_language_adapters"
    file_views_flag = "_language_adapter_file_views"
    copied = False

    def __new__(cls, *, language: str, shares_file_views: bool = False):
        return object.__new__(cls)

    def __init__(self, *, language: str, shares_file_views: bool = False) -> None:
        self.language = language
        self.shares_file_views = shares_file_views

    def annotate(self, toolset: Any) -> Any:
        setattr(toolset, self.flag, (*getattr(toolset, self.flag, ()), self.language))
        if self.shares_file_views:
            setattr(toolset, self.file_views_flag, True)
        return toolset


language_adapter = LanguageAdapter


class Identity(NamesAnnotation):
    """Name the data fields (`@data_field`) that name one object of this class, such as a ticket's `name`; a fidelity's
    progress is named by its `ticket` and its `slug`. A subclass is named as its base is.

    A language adapter reads them as the arguments of the class's `@tool_subject` loader, in the same order, so code
    holding only an object's data knows which object its operations act on. A field annotated as a reference sends an
    object by these fields alone, so a ticket can name the column that holds it without sending the column again. An
    object nothing names, such as the one board, has none.
    """

    flag = "_identity_fields"


identity = Identity


class ReferenceWithoutIdentityError(TypeError):
    """A field sends an object as a reference, but the object's class has no `@identity` to name it by."""

    def __init__(self, data_class: type) -> None:
        super().__init__(f"{data_class.__name__} is sent as a reference, so annotate the fields that name it with @identity")


class Edits(NamesAnnotation):
    """Name the fields of the object's data this operation changes, when its argument names do not match them.

    A generated view shows a field as an input only where an operation changes it, so this is how an operation whose
    argument is called something else, such as `rename(new_title)`, still makes `title` editable.
    """

    flag = "_language_adapter_edits"


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
    (`@language_adapter`). A language adapter types the data from it, and `data_of` sends an object's data by it. A class's
    annotations are fixed once it is defined, and every answer an MCP tool sends reads them, so the class holds its
    DataClass (``DataClass.of``) and its fields are read once."""

    _HELD_AS = "_data_class"

    def __init__(self, data_class: type) -> None:
        self.data_class = data_class

    @classmethod
    def of(cls, data_class: type) -> DataClass:
        """The DataClass data_class holds, made and kept on data_class itself the first time it is asked for. A subclass
        holds its own, since it may annotate more fields."""
        if not isinstance(data_class, type):  # a generic alias such as list[str] holds nothing of its own
            return cls(data_class)
        held = data_class.__dict__.get(cls._HELD_AS)
        if held is None:
            held = cls(data_class)
            try:
                setattr(data_class, cls._HELD_AS, held)
            except TypeError:  # a built-in type keeps no attributes, so its data is read for this value alone
                pass
        return held

    @functools.cached_property
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
        return Identity.names_on(self.data_class)

    @property
    def languages(self) -> tuple[str, ...]:
        """The languages the class's language adapters are written in."""
        return tuple(getattr(self.data_class, LanguageAdapter.flag, ()))

    @property
    def shares_file_views(self) -> bool:
        """Whether the shared file views read files through this class's generated client."""
        return bool(vars(self.data_class).get(LanguageAdapter.file_views_flag, False))

    def edited_by(self, operation: Any) -> tuple[str, ...]:
        """The fields of this class's data that operation's `@edits` annotation names, or none."""
        return Edits.names_on(operation)

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
        return DataClass.of(type(held)).reference(held) if held is not None and DataClass.of(type(held)).identity else data_of(held)

    def _referenced(self, held: Any) -> Any:
        if held is None:
            return None
        if isinstance(held, (list, tuple)):
            return [self._referenced(item) for item in held]
        return DataClass.of(type(held)).reference(held)


def data_of(value: Any) -> Any:
    """value as plain JSON data: an object with annotated properties as its fields, each object it holds as its own data.

    This is the one way a value of any type becomes data, for MCP results and every other JSON answer, so a path reads
    the same wherever it is sent: with forward slashes."""
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {key: data_of(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [data_of(item) for item in value]
    data_class = DataClass.of(type(value))
    return data_class.data(value) if not isinstance(value, type) and data_class.fields else value


class SourceFile(Annotation):
    """Annotates a data field that holds a path in the session's workspace: `path: Annotated[str, SourceFile]`.

    A generated view draws an annotated field as a link that opens the file in the shared source view, at the `line`, or
    the `start_line` to `end_line` range, that the same data holds. The class itself is the mark the field's type
    carries, so it is read with ``SourceFile in`` the type's metadata rather than set on a member.
    """

    flag = "_source_file"
    copied = False
