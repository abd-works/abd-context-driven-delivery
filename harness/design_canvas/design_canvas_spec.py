"""Mamba spec for a Claude Design canvas: pages and boards become canvas.json; artboards land under project/."""

import json
import tempfile
from pathlib import Path

from mamba import description, context, it, before, after
from expects import equal, expect, have_keys

from harness.design_canvas.canvas import DesignCanvas, stem, camel


with description("Design canvas") as self:
    with before.each:
        self.canvas = DesignCanvas("Story Map")
        self.canvas.add_page("story-map", "Story map")
        self.canvas.add_page("screens", "Screens")
        self.canvas.add_board("Main.dc.html", {"x": 0, "y": 0, "page": "story-map"}, "<map>")
        self.canvas.add_board("screens/pick-number.dc.html", {"x": 0, "y": 1100, "page": "screens"})

    with context("its files"):
        with it("writes the artboards it was given text for, and canvas.json"):
            expect(self.canvas.files()).to(have_keys("project/Main.dc.html", "project/canvas.json"))
            expect(list(self.canvas.files())).to(equal(["project/Main.dc.html", "project/canvas.json"]))

        with it("places every board, in the order added, and launches on the first page"):
            canvas = json.loads(self.canvas.files()["project/canvas.json"])
            expect(canvas["order"]).to(equal(["Main.dc.html", "screens/pick-number.dc.html"]))
            expect(canvas["launch"]).to(equal({"view": "canvas", "page": "story-map"}))
            expect([page["name"] for page in canvas["pages"]]).to(equal(["Story map", "Screens"]))

    with context("writing to a folder"):
        with before.each:
            self.folder = tempfile.TemporaryDirectory()

        with after.each:
            self.folder.cleanup()

        with it("puts each file under the folder at its project path"):
            self.canvas.write(self.folder.name)
            expect((Path(self.folder.name) / "project" / "Main.dc.html").read_text(encoding="utf-8")).to(equal("<map>"))

    with context("artboard names"):
        with it("names a dc-import by the file's stem, and its live flag in camel case"):
            expect(stem("screens/verify-ported-number.dc.html")).to(equal("verify-ported-number"))
            expect(camel("verify-ported-number")).to(equal("verifyPortedNumber"))
