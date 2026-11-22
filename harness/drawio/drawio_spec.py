"""A draw.io file as every practice that draws a diagram reads and writes it."""
from expects import be_none, equal, expect, raise_error
from mamba import before, context, description, it

from harness.drawio import CellStyle, DrawioFile, UnreadableDrawio
from harness.whiteboard import Box


with description("a draw.io file") as self:
    with before.each:
        self.drawing = DrawioFile()
        self.page = self.drawing.add_page("Story Map", "story-map")
        self.page.add("epic/order", "Order", "epic;rounded=1;", Box(40, 20, 300, 60))
        self.page.add("story/pay", "Pay", "story:user;rounded=1;", Box(40, 120, 152, 152), {"link": "pay.md", "entry": "story-map.md#pay"})
        self.read = DrawioFile.from_text(self.drawing.save())

    with it("should read back each page by its name"):
        expect([page.name for page in self.read.pages]).to(equal(["Story Map"]))

    with it("should read a linked cell's id and words from the UserObject round it"):
        cell = self.read.page("Story Map").cell("story/pay")
        expect((cell.label, cell.link, cell.style.role)).to(equal(("Pay", "pay.md", "story")))

    with it("should read the box each vertex is drawn in"):
        expect(self.read.page("Story Map").boxes()["epic/order"]).to(equal(Box(40.0, 20.0, 300.0, 60.0)))

    with it("should keep a cell's geometry as the file writes it"):
        expect(self.read.page("Story Map").cell("epic/order").geometry["x"]).to(equal("40"))

    with it("should read where each placed vertex sits"):
        expect(self.read.whole.positions()).to(equal({"epic/order": (40.0, 20.0), "story/pay": (40.0, 120.0)}))

    with it("should answer no page it does not hold"):
        expect(self.read.page("Thin Slicing")).to(be_none)

    with context("that is no drawing"):
        with it("should refuse text that is not XML"):
            expect(lambda: DrawioFile.from_text("<mxfile><diagram>")).to(raise_error(UnreadableDrawio))

        with it("should refuse XML that holds no graph model"):
            expect(lambda: DrawioFile.from_text("<svg/>")).to(raise_error(UnreadableDrawio))


with description("a cell's style"):
    with it("should read a value it sets"):
        expect(CellStyle("rounded=1;exitX=0.3;").value("exitX")).to(equal("0.3"))

    with it("should read a number it sets, and none for a word"):
        expect((CellStyle("exitX=0.3;").number("exitX"), CellStyle("kind=open;").number("kind"))).to(equal((0.3, None)))

    with it("should name what a practice's cell draws by its first word"):
        expect((CellStyle("subepic:2;rounded=1;").role, CellStyle("subepic:2;").role_detail)).to(equal(("subepic", "2")))
