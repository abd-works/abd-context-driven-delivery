"""Data that refers to an object sends that object by its identity."""

from dataclasses import dataclass

from expects import equal, expect
from mamba import context, description, it

from harness.installation.data_class import DataClass, data_field, data_fields, data_of, identity


@identity("name")
class _Card:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    @data_field
    def name(self) -> str:
        return self._name

    @property
    @data_field
    def title(self) -> str:
        return self._name.replace("-", " ").title()


@identity("card", "step")
class _Progress:
    def __init__(self, card: _Card, step: str) -> None:
        self._card = card
        self._step = step

    @property
    @data_field
    def card(self) -> _Card:
        return self._card

    @property
    @data_field
    def step(self) -> str:
        return self._step


class _Holder:
    def __init__(self, progress: _Progress) -> None:
        self._progress = progress

    @property
    @data_field(reference=True)
    def progress(self) -> _Progress:
        return self._progress


class _Tag(str):
    """A string of a kind of its own, as a board element's id is."""


@data_fields
@dataclass(frozen=True)
class _Corner:
    x: float
    y: float


@data_fields
@dataclass
class _Pin:
    tag: _Tag
    corner: _Corner
    note: str = ""

    @property
    @data_field
    def is_noted(self) -> bool:
        return bool(self.note)


@dataclass
class _Plain:
    name: str


with description("a record whose dataclass fields are its data"):
    with it("should send every field, each record it holds as that record's data, then the properties it annotates"):
        expect(data_of(_Pin(_Tag("start"), _Corner(1, 2)))).to(
            equal({"tag": "start", "corner": {"x": 1, "y": 2}, "note": "", "is_noted": False})
        )

    with it("should type each field as the dataclass declares it"):
        typed = {key: field.fget.__annotations__["return"] for key, field in DataClass.of(_Pin).fields.items()}
        expect(typed).to(equal({"tag": _Tag, "corner": _Corner, "note": str, "is_noted": bool}))

    with context("that is not annotated"):
        with it("should send no field of a dataclass as data"):
            expect(DataClass.of(_Plain).fields).to(equal({}))


with description("data that refers to an object"):
    with context("whose identity field is itself an object with an identity"):
        with it("should send that field by the object's own identity"):
            expect(data_of(_Holder(_Progress(_Card("pet-visits"), "story-map")))).to(
                equal({"progress": {"card": {"name": "pet-visits"}, "step": "story-map"}})
            )
