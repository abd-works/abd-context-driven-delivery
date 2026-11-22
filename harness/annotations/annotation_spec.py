"""Annotations that leave an operation or class out of the catalog or out of install."""

from expects import be_false, be_true, expect
from mamba import before, context, description, it

from harness.annotations.annotation import NoCatalog, NoDeploy, noCatalog, noDeploy


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


with description("an annotation on an operation"):
    with before.each:
        from harness.hooks.hooks import Hook
        from harness.installation.data_class import DataField, Identity

        self.Hook, self.DataField, self.Identity = Hook, DataField, Identity

        def stop(payload: dict) -> dict:
            return {}

        def title(self) -> str:
            return "a title"

        self.stop = Hook("stop", disabled=True)(stop)
        self.title = DataField(title)
        self.named = Identity("name", "slug")(type("Named", (), {}))

    with it("should record itself, holding the name it gave the operation"):
        expect(self.Hook.recorded_on(self.stop).name == "stop").to(be_true)

    with it("should record that it is turned off on the operation"):
        expect(self.Hook.recorded_on(self.stop).disabled).to(be_true)

    with it("should record the key a data field is sent by, its getter's name when it names none"):
        expect(self.DataField.recorded_on(self.title).key == "title").to(be_true)

    with it("should record the names it was given"):
        expect(self.Identity.recorded_on(self.named).names == ("name", "slug")).to(be_true)

    with it("should leave nothing on the operation beside its one flag"):
        expect([name for name in vars(self.stop) if name.startswith("_hook")] == ["_hook"]).to(be_true)
