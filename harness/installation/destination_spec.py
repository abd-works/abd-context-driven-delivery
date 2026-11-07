"""Marks that leave an operation or class out of the catalog or out of install."""

from expects import be_false, be_true, expect
from mamba import before, context, description, it

from harness.installation.destination import NoCatalog, NoDeploy, noCatalog, noDeploy


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
    with context("that carries no omission mark"):
        with it("should stay in the catalog"):
            expect(NoCatalog.marks(_Shown.explain)).to(be_false)

        with it("should stay in install"):
            expect(NoDeploy.marks(_Shown.explain)).to(be_false)

    with context("that is marked noCatalog and noDeploy"):
        with it("should be left out of the catalog"):
            expect(NoCatalog.marks(_Hidden.explain)).to(be_true)

        with it("should be left out of install"):
            expect(NoDeploy.marks(_Hidden.explain)).to(be_true)

        with context("with the operation read from an instance"):
            with before.each:
                self.bound = _Hidden().explain

            with it("should still be left out of the catalog"):
                expect(NoCatalog.marks(self.bound)).to(be_true)

    with context("that is a classmethod marked beneath its classmethod"):
        with it("should be left out of install when read from the class body, through the function it wraps"):
            expect(NoDeploy.marks(vars(_Hidden)["load"])).to(be_true)


with description("a class"):
    with context("that is marked noCatalog"):
        with it("should be left out of the catalog"):
            expect(NoCatalog.marks(_HiddenClass)).to(be_true)

        with it("should still be installed"):
            expect(NoDeploy.marks(_HiddenClass)).to(be_false)
