"""Annotations that leave an operation or class out of the catalog or out of install."""

from expects import be_false, be_true, equal, expect
from mamba import before, context, description, it

from harness.installation.destination import NoCatalog, NoDeploy, noCatalog, noDeploy

from harness.installation.data_class import data_field, data_of, identity


class _Shown:
    def explain(self) -> str:
        return "shown"


class _Hidden:
    @noCatalog
    @noDeploy
    def explain(self) -> str:
        return "hidden"

    @classmethod
    @noCatalog
    @noDeploy
    def load(cls) -> "_Hidden":
        return cls()


@noCatalog
class _HiddenClass:
    pass


with description("an operation"):
    with context("that carries no omission annotation"):
        with it("should stay in the catalog"):
            expect(NoCatalog.annotates(_Shown.explain)).to(be_false)

        with it("should stay in install"):
            expect(NoDeploy.annotates(_Shown.explain)).to(be_false)

    with context("that is annotated noCatalog and noDeploy"):
        with it("should be left out of the catalog"):
            expect(NoCatalog.annotates(_Hidden.explain)).to(be_true)

        with it("should be left out of install"):
            expect(NoDeploy.annotates(_Hidden.explain)).to(be_true)

        with context("with the operation read from an instance"):
            with before.each:
                self.bound = _Hidden().explain

            with it("should still be left out of the catalog"):
                expect(NoCatalog.annotates(self.bound)).to(be_true)

    with context("that is a classmethod annotated beneath its classmethod"):
        with it("should be left out of install when read from the class body, through the function it wraps"):
            expect(NoDeploy.annotates(vars(_Hidden)["load"])).to(be_true)


with description("a class"):
    with context("that is annotated noCatalog"):
        with it("should be left out of the catalog"):
            expect(NoCatalog.annotates(_HiddenClass)).to(be_true)

        with it("should still be installed"):
            expect(NoDeploy.annotates(_HiddenClass)).to(be_false)


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
