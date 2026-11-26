"""Mamba spec for the record of where a canvas version's screen files come from (screen-sources.json)."""

import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import after, before, description, it

from cdd_guidance.practices.ux.model.claude_design.screen_sources import FIXTURES, ScreenSources


with description("the record of where a canvas version's screen files come from") as self:
    with before.each:
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        self.sources = ScreenSources(self.root / "ux" / "design-canvas" / "version-1" / "project")
        self.sources.record({"ds/app": self.root / "packages" / "app" / "assets", "flow.js": self.root / "ux" / "prototype" / "flow.js"}, self.root)

    with after.each:
        self.folder.cleanup()

    with it("should name each copy's source from the project's root"):
        expect(self.sources.origin("flow.js")).to(equal({"from": "ux/prototype/flow.js", "kind": "copy"}))

    with it("should trace a file inside a copied folder to that folder's source"):
        expect(self.sources.origin("ds/app/components/bundle.js")).to(equal({"from": "packages/app/assets", "kind": "copy"}))

    with it("should keep what an earlier render recorded when a later one records more"):
        self.sources.record({"fixtures/canvas-fixtures.js": self.root / "tests" / ".context"}, self.root, FIXTURES)
        expect((self.sources.origin("flow.js")["from"], self.sources.origin("fixtures/canvas-fixtures.js")["kind"])).to(equal(("ux/prototype/flow.js", FIXTURES)))

    with it("should trace nothing it never recorded"):
        expect(self.sources.origin("multiline.js")).to(equal(None))
