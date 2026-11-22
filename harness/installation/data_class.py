"""The data annotations on a class and its members, and what they declare about its objects' data: the fields that are
its data, the fields that name one object, the languages its operations are typed in, the fields an operation edits,
and the fields that hold a path in the workspace. A language adapter types the data from them, and every MCP answer
sends an object's data by them (`data_of`)."""
from __future__ import annotations

import dataclasses
import functools
import inspect
from enum import Enum
from pathlib import Path
from collections.abc import Mapping, Sequence
from typing import Any, Generic, TypeAlias, TypeVar, Union, get_type_hints

from harness.agent_tools.parameter_schema import is_built_in
from harness.annotations.annotation import Annotatable, Annotation, NamesAnnotation

# The class a *DataClass* describes: its instances are what it sends as data. Any class can annotate its data
# (`@data_field`), so a DataClass is generic in the class it describes.
Described = TypeVar("Described")
# A value an answer sends as data: a plain value, a path, an enum, a mapping or sequence of them, or an object of a
# class that describes its data.
SentValue: TypeAlias = Union[str, int, float, bool, None, Enum, Path, Mapping[str, "SentValue"], Sequence["SentValue"], Described]


class LanguageAdapter(Annotation):
    """Deploy typed code in language for this toolset's MCP operations, so an application outside Python reaches them.

    The adapter names the object its operations act on by the class's `@identity` fields. `shares_file_views=True`
    marks the toolset whose generated client the shared file views import to read files, the file manager's.
    """

    flag = "_language_adapters"
    copied = False

    def __new__(cls: type[LanguageAdapter], *, language: str, shares_file_views: bool = False) -> LanguageAdapter:
        return object.__new__(cls)

    def __init__(self, *, language: str, shares_file_views: bool = False) -> None:
        self.language = language
        self.languages: tuple[str, ...] = (language,)
        self.shares_file_views = shares_file_views

    def annotate(self, toolset: type) -> type:
        """Record itself on toolset, after the languages of any adapter the class already carries."""
        earlier = LanguageAdapter.recorded_on(toolset)
        if earlier is not None:
            self.languages = (*earlier.languages, self.language)
        return super().annotate(toolset)


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
    copied = False

    def __new__(
        cls: type[DataField], target: Annotatable | None = None, *, key: str = "", reference: bool = False
    ) -> DataField | Annotatable:
        annotation = object.__new__(cls)
        annotation.key = key
        annotation.reference = reference
        if callable(target):
            return annotation.annotate(target)
        return annotation

    def annotate(self, getter: Annotatable) -> Annotatable:
        """Record itself on getter, sent by the key it names, else by the getter's own name."""
        self.key = self.key or getter.__name__
        return super().annotate(getter)


data_field = DataField


class DataFields(Annotation):
    """Annotate a dataclass whose fields are all its data, as `@data_field` marks each property of any other class: a
    record such as a board element, whose fields are what it is, so naming each again as a property would only copy
    it. A subclass's own fields are its data too, and a property it annotates `@data_field` joins them."""

    flag = "_data_fields"
    copied = False


data_fields = DataFields


def _field_reader(name: str, hint: Any) -> property:
    """A property reading the dataclass field name, typed hint, so a dataclass field is read and typed as an annotated
    property is."""

    def read(instance: Any) -> Any:
        return getattr(instance, name)

    read.__name__ = name
    read.__annotations__ = {"return": hint}
    return property(DataField(read))


class DataClass(Generic[Described]):
    """What the annotations on one class declare about its objects' data: the properties that are its data (`@data_field`),
    the fields that name one object (`@identity`), and the languages its operations are typed in
    (`@language_adapter`). A language adapter types the data from it, and `data_of` sends an object's data by it. A class's
    annotations are fixed once it is defined, and every answer an MCP tool sends reads them, so the class holds its
    DataClass (``DataClass.of``) and its fields are read once."""

    _HELD_AS = "_data_class"

    def __init__(self, data_class: type[Described]) -> None:
        self.data_class = data_class

    @classmethod
    def of(cls, data_class: type[Described]) -> DataClass[Described]:
        """The DataClass data_class holds, made and kept on data_class itself the first time it is asked for. A subclass
        holds its own, since it may annotate more fields."""
        if not isinstance(data_class, type):  # a generic alias such as list[str] holds nothing of its own
            return cls(data_class)
        held = data_class.__dict__.get(cls._HELD_AS)
        if held is None:
            held = cls(data_class)
            if not is_built_in(data_class):
                setattr(data_class, cls._HELD_AS, held)
        return held

    @functools.cached_property
    def fields(self) -> dict[str, property]:
        """The properties the class annotates as its data, by the name each takes in the data; a base class's come first.
        A subclass that overrides an annotated property, such as a card's title, is read through its own. A dataclass
        annotated `@data_fields` sends its fields first, each typed as the dataclass declares it."""
        attributes: dict[str, str] = {}
        for klass in reversed(self.data_class.__mro__):
            for attribute, member in vars(klass).items():
                if isinstance(member, property) and DataField.annotates(member.fget):
                    attributes[DataField.recorded_on(member.fget).key] = attribute
        annotated = {key: inspect.getattr_static(self.data_class, attribute) for key, attribute in attributes.items()}
        return {**self._dataclass_fields, **annotated}

    @property
    def _dataclass_fields(self) -> dict[str, property]:
        """The fields of a dataclass annotated `@data_fields`, each read through a property typed as the field is; none
        for any other class. A field whose name starts with an underscore is the class's own."""
        if not (isinstance(self.data_class, type) and DataFields.annotates(self.data_class) and dataclasses.is_dataclass(self.data_class)):
            return {}
        hints = get_type_hints(self.data_class, include_extras=True)
        return {item.name: _field_reader(item.name, hints[item.name]) for item in dataclasses.fields(self.data_class) if not item.name.startswith("_")}

    @property
    def identity(self) -> tuple[str, ...]:
        """The fields that name one object of the class, or none."""
        return Identity.names_on(self.data_class)

    @property
    def languages(self) -> tuple[str, ...]:
        """The languages the class's language adapters are written in."""
        adapter = LanguageAdapter.recorded_on(self.data_class)
        return adapter.languages if adapter is not None else ()

    @property
    def shares_file_views(self) -> bool:
        """Whether the shared file views read files through this class's generated client."""
        adapter = vars(self.data_class).get(LanguageAdapter.flag)
        return adapter is not None and adapter.shares_file_views

    def edited_by(self, operation: Annotatable) -> tuple[str, ...]:
        """The fields of this class's data that operation's `@edits` annotation names, or none."""
        return Edits.names_on(operation)

    def sends_by_identity(self, field: property) -> bool:
        """Whether field sends the object it holds by that object's identity alone."""
        recorded = DataField.recorded_on(field.fget)
        return recorded is not None and recorded.reference

    @functools.cached_property
    def _sent(self) -> tuple[tuple[str, Any, bool], ...]:
        """Each field as `data` sends it: its key, its getter, and whether it sends what it holds by identity alone. Every
        answer sends thousands of objects, so this is read once per class rather than once per object."""
        return tuple((key, field.fget, self.sends_by_identity(field)) for key, field in self.fields.items())

    def data(self, instance: Described) -> dict[str, Any]:
        """instance's annotated fields as plain data."""
        sent: dict[str, Any] = {}
        for key, getter, by_identity in self._sent:
            held = getter(instance)
            sent[key] = self._referenced(held) if by_identity else data_of(held)
        return sent

    def reference(self, instance: Described) -> dict[str, Any]:
        """instance by its identity alone, such as `{"name": "Discovery"}` for a stage, so data can name an object that is
        sent in full elsewhere without sending it again. An identity field that holds an object with an identity of its
        own sends that object by its reference too, so a fidelity's progress is `{ticket: {name}, fidelity: {slug}}`."""
        if not self.identity:
            raise ReferenceWithoutIdentityError(self.data_class)
        fields = self.fields
        return {key: self._identity_data(fields[key].fget(instance)) for key in self.identity}

    def _identity_data(self, held: SentValue[Described]) -> Any:
        if held is None:
            return data_of(held)
        held_class = DataClass.of(type(held))
        return held_class.reference(held) if held_class.identity else data_of(held)

    def _referenced(self, held: SentValue[Described]) -> Any:
        if held is None:
            return None
        if isinstance(held, (list, tuple)):
            return [self._referenced(item) for item in held]
        return DataClass.of(type(held)).reference(held)


# The types data_of sends as they are, matched exactly.
_PLAIN_TYPES = frozenset({str, int, float, bool, type(None)})


def data_of(subject: SentValue[Described]) -> Any:
    """subject as plain JSON data: an object with annotated properties as its fields, each object it holds as its own data.

    This is the one way a value of any type becomes data, for MCP results and every other JSON answer, so a path reads
    the same wherever it is sent: with forward slashes."""
    if type(subject) in _PLAIN_TYPES:  # most of an answer's values; an Enum built on str is no plain str, so it is sent below
        return subject
    if isinstance(subject, Enum):
        return subject.value
    if subject is None or isinstance(subject, (str, int, float, bool)):
        return subject
    if isinstance(subject, Path):
        return subject.as_posix()
    if isinstance(subject, dict):
        return {key: data_of(item) for key, item in subject.items()}
    if isinstance(subject, (list, tuple)):
        return [data_of(item) for item in subject]
    data_class = DataClass.of(type(subject))
    return data_class.data(subject) if not isinstance(subject, type) and data_class.fields else subject


class SourceFile(Annotation):
    """Annotates a data field that holds a path in the session's workspace: `path: Annotated[str, SourceFile]`.

    A generated view draws an annotated field as a link that opens the file in the shared source view, at the `line`, or
    the `start_line` to `end_line` range, that the same data holds. The class itself is the mark the field's type
    carries, so it is read with ``SourceFile in`` the type's metadata rather than set on a member.
    """

    flag = "_source_file"
    copied = False
