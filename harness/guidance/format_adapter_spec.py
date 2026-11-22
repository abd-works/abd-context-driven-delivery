"""The one contract every format's adapter meets, and what a render answers."""
import tempfile
from pathlib import Path

from expects import be_none, equal, expect, raise_error
from mamba import before, context, description, it

from harness.guidance.practice_formats import FormatAdapter, Rendered, RenderRequest, Written
from harness.installation.data_class import data_of
from harness.markdown.format import Format


class _Lines(FormatAdapter):
    """A format of lines, as small as an adapter can be: it reads lines and writes them back, each line naming the
    file it was read from."""

    def __init__(self, lines: list[str] | None = None, file: str = "") -> None:
        self.lines = list(lines or [])
        self.file = file
        self.sources: dict[str, str] = {}

    def parse(self, text, file=""):
        return _Lines(str(text).splitlines(), file)

    def render(self, model, written=Written()):
        return "\n".join([*model.lines, f"(was {len(str(written.previous).splitlines())} lines)"])

    def placed_in(self, file, text):
        self.sources[file] = text
        return self


with description("a format's adapter") as self:
    with before.each:
        self.project = Path(tempfile.mkdtemp())
        (self.project / "notes").mkdir()
        self.file = self.project / "notes" / "cart.lines"
        self.file.write_text("add a book\ncheck out\n", encoding="utf-8")
        self.heard: list[str] = []

    with context("that opens a file with the read every format has"):
        with before.each:
            self.read = _Lines().read_file(self.file, self.project, self.heard.append)

        with it("should read the file's text"):
            expect(self.read.lines).to(equal(["add a book", "check out"]))

        with it("should name the file as a path from the project"):
            expect(self.read.file).to(equal("notes/cart.lines"))

        with it("should be placed in the file it was read from"):
            expect(self.read.sources).to(equal({"notes/cart.lines": "add a book\ncheck out\n"}))

        with it("should tell who listens of the file as it is read"):
            expect(self.heard).to(equal(["notes/cart.lines"]))

    with it("should leave writing onto a file already there to the Render action"):
        expect(_Lines().reshape("new", "old")).to(be_none)

    with it("should be handed the file as it is now when it renders"):
        expect(_Lines().render(_Lines(["a"]), Written("one\ntwo\n"))).to(equal("a\n(was 2 lines)"))

    with context("that names no parse of its own"):
        with it("should refuse to read text"):
            expect(lambda: FormatAdapter().parse("text")).to(raise_error(NotImplementedError))


with description("what a render answers") as self:
    with before.each:
        self.rendered = Rendered(Format("markdown"), "# Cart\n")

    with it("should write itself as the two fields a render has always answered"):
        expect(data_of(self.rendered)).to(equal({"format": "markdown", "content": "# Cart\n"}))

    with it("should read itself back from those fields"):
        expect(Rendered.from_data({"format": "markdown", "content": "# Cart\n"})).to(equal(self.rendered))


with description("a render request") as self:
    with context("that names the folder its links point into"):
        with it("should hand the adapter the file as it is now and that folder"):
            request = RenderRequest(Format("drawio"), "text", previous="<mxfile/>", folder="docs")
            expect(request.written).to(equal(Written("<mxfile/>", Path("docs"))))

    with context("that names no folder"):
        with it("should hand the adapter no folder"):
            expect(RenderRequest(Format("drawio"), "text").written.folder).to(be_none)

    with context("that works at no fidelity"):
        with it("should refuse to render, since no practice's formats are named"):
            expect(lambda: RenderRequest(Format("drawio"), "text").render()).to(raise_error(ValueError))
