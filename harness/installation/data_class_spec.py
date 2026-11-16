"""Data that refers to an object sends that object by its identity."""

from expects import equal, expect
from mamba import context, description, it

from harness.installation.data_class import data_field, data_of, identity


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


with description("data that refers to an object"):
    with context("whose identity field is itself an object with an identity"):
        with it("should send that field by the object's own identity"):
            expect(data_of(_Holder(_Progress(_Card("pet-visits"), "story-map")))).to(
                equal({"progress": {"card": {"name": "pet-visits"}, "step": "story-map"}})
            )
