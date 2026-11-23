"""The one contract every format's adapter meets, and what a render answers."""
import tempfile
from pathlib import Path
from types import SimpleNamespace

from expects import be_false, be_none, be_true, equal, expect, raise_error
from mamba import before, context, description, it

from harness.guidance.declared_outputs import DeclaredOutputs
from harness.guidance.format_trip import (
    FAILS_ON_THE_WAY,
    HOLDS_LESS_UNSAID,
    NOT_HELD_BY_THIS_FORMAT,
    RETURNS_WHAT_WENT_IN,
    ExampleNotThere,
    FidelityExample,
    FormatTrip,
)
from harness.guidance.guidance import FidelityGuidance
from harness.guidance.practice_formats import ExistingText, FormatAdapter, PracticeFormats, Rendered, RenderRequest, Written, lead_of
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


with description("the text a file holds before a render is written onto it") as self:
    with before.each:
        self.existing = ExistingText("class Cart:\n    pass\n\nNOTE = 'keep me'\n")

    with it("should name each line a text would lose"):
        expect(self.existing.lines_not_in("class Cart:\n    pass\n")).to(equal(["NOTE = 'keep me'"]))

    with it("should lose nothing to a text that holds every line"):
        expect(self.existing.lines_not_in("class Cart:\n    pass\nNOTE = 'keep me'\nmore\n")).to(equal([]))

    with context("whose lines a rendered shape cannot place"):
        with before.each:
            self.reshaped = self.existing.set_apart_below("class Basket:\n    pass\n", "#")

        with it("should keep the lines the shape does not hold below it as comments"):
            expect(self.reshaped.text.splitlines()[-2:]).to(equal(["# class Cart:", "# NOTE = 'keep me'"]))

        with it("should count the lines set apart"):
            expect(self.reshaped.set_apart).to(equal(2))

        with it("should say how many lines wait to be moved"):
            expect(self.reshaped.left_to_move).to(equal(["2 line(s) set apart"]))

        with it("should carry them over as they are when rendered again"):
            again = ExistingText(self.reshaped.text).set_apart_below("class Basket:\n    pass\n", "#")
            expect(again.text).to(equal(self.reshaped.text))


with description("a member a reshaper outlines") as self:
    with it("should start at the comments and decorators written directly above it, at its indent"):
        lines = ["class Cart:", "    # adds a book", "    @staticmethod", "    def add():", "        pass"]
        expect(lead_of(lines, 3, "    ", ("#", "@"))).to(equal(1))

    with it("should go no higher than the floor it is given"):
        lines = ["# about", "# the file", "def add():"]
        expect(lead_of(lines, 2, "", ("#",), floor=1)).to(equal(1))


class _ReadsOnly(FormatAdapter):
    """An adapter that reads its format and writes nothing."""

    def parse(self, text, file=""):
        return self


def _lacking(outputs: dict, adapters: dict) -> list[str]:
    """What the formats made with adapters lack of the outputs a fidelity declares."""
    return PracticeFormats(None, adapters).lacking(DeclaredOutputs(outputs))


with description("the formats a fidelity declares in its outputs") as self:
    with context("each with an adapter that reads it and writes it"):
        with it("should lack nothing"):
            expect(_lacking({"lines": "notes/{cart}.lines"}, {"lines": _Lines})).to(equal([]))

    with context("one with no adapter"):
        with it("should name the format"):
            expect(_lacking({"lines": "notes/{cart}.lines", "drawio": "notes/{cart}.drawio"}, {"lines": _Lines})).to(
                equal(["drawio: no adapter"])
            )

    with context("one whose adapter writes nothing"):
        with it("should name the format and what its adapter cannot do"):
            expect(_lacking({"lines": "notes/{cart}.lines"}, {"lines": _ReadsOnly})).to(equal(["lines: its adapter writes no text"]))

    with context("one whose adapter reads nothing"):
        with it("should name the format and what its adapter cannot do"):
            expect(_lacking({"lines": "notes/{cart}.lines"}, {"lines": FormatAdapter})).to(
                equal(["lines: its adapter reads no text", "lines: its adapter writes no text"])
            )

    with context("an output named for what it holds, written in a format with an adapter"):
        with it("should lack nothing"):
            expect(_lacking({"thin_slice": ["notes/thin-slice.lines"]}, {"lines": _Lines})).to(equal([]))

    with context("an output named for what it holds, with a file in a format that has no adapter"):
        with it("should name the output and the file's format"):
            expect(_lacking({"thin_slice": ["notes/thin-slice.lines", "notes/thin-slice.drawio"]}, {"lines": _Lines})).to(
                equal(["thin_slice (drawio): no adapter"])
            )

    with context("a folder, which names no file"):
        with it("should ask for the format's adapter all the same"):
            expect(_lacking({"python": "{module}/"}, {"lines": _Lines})).to(equal(["python: no adapter"]))

    with context("of every practice CDD ships"):
        # The practices are made once; the example only reads what each fidelity lacks.
        with before.all:
            import cdd_guidance.practices  # noqa: F401 - registers the practices CDD ships
            from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE

            fidelities = [fidelity for practice in PRACTICE_CATALOGUE.create_all() for fidelity in practice.fidelities]
            self.lacking = {fidelity.slug: fidelity.formats_without_an_adapter for fidelity in fidelities}

        with it("should each have an adapter that reads it and writes it"):
            expect({slug: lacking for slug, lacking in self.lacking.items() if lacking}).to(equal({}))

        with it("should be asked of every fidelity of the five practices"):
            expect(len(self.lacking)).to(equal(15))



class _Titles(FormatAdapter):
    """A format that holds less than lines: it writes only the lines that open with ``#`` and reads them back."""

    def parse(self, text, file=""):
        return _Lines(str(text).splitlines(), file)

    def render(self, model, written=Written()):
        return "\n".join(line for line in model.lines if line.startswith("#"))


class _Poster(_Titles):
    """A format that is written and never read back."""

    def parse(self, text, file=""):
        raise NotImplementedError("a poster is printed, and nothing reads a print")


class _Torn(_Titles):
    """A format whose writing fails."""

    def render(self, model, written=Written()):
        raise ValueError("the page tore")


class _Broken(_Titles):
    """A format whose writing has a bug: it adds a number to a text."""

    def render(self, model, written=Written()):
        return "lines: " + len(model.lines)


class _Tidy(_Lines):
    """A format of lines that writes every quote as a double quote."""

    def render(self, model, written=Written()):
        return "\n".join(line.replace("'", '"') for line in model.lines)


_ADAPTERS = {"lines": _Lines, "titles": _Titles, "poster": _Poster, "torn": _Torn, "broken": _Broken, "tidy": _Tidy}
_EXAMPLE = "# Cart\nadd a book\ncheck out\n"


def _trip(leaves_out: dict | None = None, outputs: dict | None = None, example: str = _EXAMPLE, written_in: str = "lines") -> FormatTrip:
    """The example of a fidelity of notes, written in lines, ready to be taken to the fidelity's other formats."""
    practice = SimpleNamespace(format=Format("lines"), working_set=SimpleNamespace(extended=None), default_workspace_folder="")
    practice.formats = PracticeFormats(practice, _ADAPTERS)
    declared = DeclaredOutputs(outputs or {"lines": "notes/{cart}.lines", "titles": "notes/{cart}.titles"})
    fidelity = SimpleNamespace(practice_guidance=practice, leaves_out=leaves_out or {}, declared=declared)
    return FormatTrip(fidelity, example, written_in)


with description("a fidelity's example taken to one of its formats and back") as self:
    with context("through a format that holds every line"):
        with it("should return what went in"):
            expect(_trip().through("lines").status).to(equal(RETURNS_WHAT_WENT_IN))

        with it("should pass"):
            expect(_trip().through("lines").passes).to(be_true)

    with context("whose own format spells a line another way than the example does"):
        with it("should count the line as returned, since its own format wrote it so"):
            expect(_trip(example="# Cart\nadd 'a book'\n", written_in="tidy").through("lines").status).to(equal(RETURNS_WHAT_WENT_IN))

    with context("through a format that holds less, whose fidelity says what it leaves out and where that is kept"):
        with before.each:
            self.outcome = _trip({"titles": "the steps, which stay in the lines file"}).through("titles")

        with it("should be not held by this format"):
            expect(self.outcome.status).to(equal(NOT_HELD_BY_THIS_FORMAT))

        with it("should name each line that did not come back"):
            expect(self.outcome.lost).to(equal(("add a book", "check out")))

        with it("should pass, since whoever picks the format is told"):
            expect(self.outcome.passes).to(be_true)

    with context("through a format that holds less, whose fidelity says nothing of it"):
        with before.each:
            self.outcome = _trip().through("titles")

        with it("should hold less and not say what"):
            expect(self.outcome.status).to(equal(HOLDS_LESS_UNSAID))

        with it("should fail"):
            expect(self.outcome.passes).to(be_false)

    with context("through a format nothing reads back, whose fidelity says so"):
        with it("should be not held by this format"):
            outcome = _trip({"poster": "everything: a poster is printed from the lines file, which keeps it all"}).through("poster")
            expect(outcome.status).to(equal(NOT_HELD_BY_THIS_FORMAT))

    with context("through a format nothing reads back, whose fidelity says nothing of it"):
        with it("should hold less and not say what"):
            expect(_trip().through("poster").status).to(equal(HOLDS_LESS_UNSAID))

    with context("through a format that fails on the way"):
        with before.each:
            self.outcome = _trip({"torn": "the steps"}).through("torn")

        with it("should fail on the way, whatever its fidelity says it leaves out"):
            expect(self.outcome.status).to(equal(FAILS_ON_THE_WAY))

        with it("should say what failed"):
            expect(self.outcome.refused).to(equal("ValueError: the page tore"))

    with context("through a format whose writing has a bug"):
        with it("should raise the bug rather than report it as the format's outcome"):
            expect(lambda: _trip().through("broken")).to(raise_error(TypeError))

    with context("whose own format reads nothing from the example"):
        with it("should fail on the way, since an empty example loses nothing in any format"):
            outcome = _trip(example="add a book\n", written_in="titles").through("lines")
            expect((outcome.status, outcome.refused)).to(equal((FAILS_ON_THE_WAY, "titles reads nothing from the example")))

    with context("through each format its fidelity declares"):
        with it("should go through every declared format but the one the example is written in"):
            outputs = {"lines": "notes/{cart}.lines", "titles": "notes/{cart}.titles", "poster": "notes/{cart}.poster"}
            expect(list(_trip(outputs=outputs).through_each())).to(equal(["titles", "poster"]))

        with it("should leave out an output named for what it holds, whose files are in formats the trip already takes"):
            outputs = {"lines": "notes/{cart}.lines", "titles": "notes/{cart}.titles", "thin_slice": ["notes/thin.lines", "notes/thin.titles"]}
            expect(list(_trip(outputs=outputs).through_each())).to(equal(["titles"]))


with description("the example a fidelity names in its practice document") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp())
        (self.folder / "_examples" / "cart").mkdir(parents=True)
        (self.folder / "_examples" / "cart.md").write_text("# Cart\n", encoding="utf-8")
        (self.folder / "_examples" / "cart" / "cart.py").write_text("class Cart: ...\n", encoding="utf-8")

    with context("that is a file"):
        with before.each:
            self.example = FidelityExample(self.folder, "_examples/cart.md", Format("python"))

        with it("should be the file's text"):
            expect(self.example.content).to(equal("# Cart\n"))

        with it("should be written in the format of the file's extension"):
            expect(self.example.written_in).to(equal(Format("markdown")))

    with context("that is a folder of code"):
        with before.each:
            self.example = FidelityExample(self.folder, "_examples/cart", Format("typescript"))

        with it("should be the folder's files by their paths"):
            expect(self.example.content).to(equal({"cart.py": "class Cart: ...\n"}))

        with it("should be written in the code format most of its files are in"):
            expect(self.example.written_in).to(equal(Format("python")))

    with context("that names a file that is not there"):
        with it("should refuse, naming the file"):
            expect(lambda: FidelityExample(self.folder, "_examples/basket.md", Format("python")).content).to(
                raise_error(ExampleNotThere, f"the example _examples/basket.md is not in {self.folder}")
            )

    with context("of a fidelity whose block names one"):
        with before.each:
            self.fidelity = FidelityGuidance.from_block(
                "notes", '```yaml\nexample: "_examples/cart.md"\nleaves_out:\n  drawio: "the steps, which stay in cart.md"\n```\n'
            )

        with it("should be named by the fidelity"):
            expect(self.fidelity.example).to(equal("_examples/cart.md"))

        with it("should keep what each format leaves out"):
            expect(self.fidelity.leaves_out).to(equal({"drawio": "the steps, which stay in cart.md"}))

    with context("of a fidelity whose block names none"):
        with it("should be no example"):
            expect(FidelityGuidance.from_block("notes", "```yaml\nstage: discovery\n```\n").example).to(equal(""))
