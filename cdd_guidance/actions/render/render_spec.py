"""BDD spec for the Render action — Guidance refs, fidelity, and source format."""

import json
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, end_with, equal, expect, have_key, raise_error
from mamba import after, before, context, description, it

from cdd_guidance.actions.render.render import BoardNotKept, FormatNotDeclared, Render
from cdd_guidance.actions.render.rendered_canvas import CanvasFileNotRendered
from cdd_guidance.actions.render.rendered_code import RenderHasNoDeclaredPlace
from cdd_guidance.practices.ux.model.html.nodes import HtmlUxMap
from cdd_guidance.practices.ux.model.ux_map import UxMap
from cdd_guidance.practices.ux.model.ux_map_spec_fixture import OrderingMap
from harness.design_canvas.versions import CanvasVersions, PublishedVersion
from cdd_guidance.actions.render.rendered_file import NothingToRender
from cdd_guidance.actions.render.source_files import SourceFormatRefused
from cdd_guidance.actions.render.render_order import RenderFailed
from cdd_guidance.practices.bdd.model.bdd_model import SpecBodiesNotKept
from cdd_guidance.practices.stories.stories import Stories
from harness.agent_tools.agent_tools import AgentInstructions
from harness.agent_tools.recipe import RecipeLineFailed
from harness.agent_tools.tool_call import ToolCall
from harness.graph.saved_graph import SavedGraph
from harness.installation.data_class import data_of
from space.session import Sessions
from space.session.files.session_files import NamedPathNotFoundError
from space.session.spec_support.throwaway_project import ThrowawayProject
from harness.whiteboard import Whiteboard

_REF = "cdd_guidance.practices.clean_engineering.clean_engineering:CleanEngineering"
_STORIES = "cdd_guidance.practices.stories.stories:Stories"
_PYTHON = '''\
class Cart:
    """Cart holds line items and places orders."""

    def __init__(self, owner: str) -> None:
        self.owner = owner
'''
_STORY_MAP = """\
(E) Manage Customer Orders
    (E) Place New Order
        (S) Customer --> Browse Product Catalog
"""
_MARKDOWN_STORY_MAP = """\
# (E) Manage Customer Orders

## (E) Place New Order

### (S) Customer --> Browse Product Catalog
"""
_OTHER_STORY_MAP = """# (E) Manage Customer Returns

## (E) Accept Return

### (S) Customer --> Return Damaged Item
"""
_DOMAIN_MODEL = """# Domain Model — Bookshop

---

## Ordering | custom

### Cart

A cart holds one line per book.

#### Cart <<Aggregate Root>> <<Entity>>

------
+ cartId: CartId
----
+ total(): Money

### Order

An order is a cart a customer submitted.

#### Order <<Aggregate Root>> <<Entity>>

------
+ orderId: OrderId
----
+ submit(): void
"""
_CART_SPEC = """from mamba import description, it


with description("a cart"):
    with it("should total its lines"):
        pass
"""
_FINISHED_SPEC = """from expects import equal, expect
from mamba import description, it

from shop.cart import Cart


with description("a cart"):
    with it("should total its lines"):
        expect(Cart().total).to(equal(0))
"""
_CART_SPEC_IN_TYPESCRIPT = """describe('a cart', () => {
  it('should total its lines', () => {
  });
});
"""
_REALIZATION = """# Bookshop BDD realization

## a cart

### it should total its lines

```
Cart.total()
```
"""
_CART_MODEL = """# Ordering

**Module:** `src/ordering`

## Cart

### **Cart** <<Aggregate Root>>

+ Cart(customer_id: str)
------
+ customer_id: str
----
+ total(): int
"""
_EMPTY_TOTAL = "    def total(self) -> int:\n        raise NotImplementedError"
_TOTAL_WITH_CODE = "    def total(self) -> int:\n        # tax is added at checkout\n        return sum(line.subtotal for line in self.lines)"
_NOTE_CELL = '<mxCell id="person-note" value="Ask Dana before changing this" style="text;html=1;" vertex="1" parent="1"><mxGeometry x="900" y="900" width="200" height="40" as="geometry" /></mxCell>'


def _story_map_project() -> ThrowawayProject:
    """A project of its own whose .context holds the markdown story map."""
    project = ThrowawayProject()
    (project.root / ".context").mkdir()
    (project.root / ".context" / "story-map.md").write_text(_MARKDOWN_STORY_MAP, encoding="utf-8")
    return project


def _render_story_map(project: ThrowawayProject) -> list:
    """The project's story map rendered to drawio, as a session in it asks."""
    return Render().for_call(ToolCall({}, project.root)).render("stories-story-map", format="drawio", paths=[".context/story-map.md"], source="markdown")
_NOTE_ONLY_DRAWING = f'<mxfile><diagram name="Story Map" id="story-map"><mxGraphModel><root><mxCell id="0" /><mxCell id="1" parent="0" />{_NOTE_CELL}</root></mxGraphModel></diagram></mxfile>'
_WORKER_TRACEBACK = """Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "nodes.py", line 535, in parse
    raise MarkdownParseError("Not a valid Markdown story map: no recognised structure found")
MarkdownParseError: Not a valid Markdown story map: no recognised structure found
"""
_STORY_TEST = '''\
from story_test import given, scenario, story, then, when

with story("Browse Product Catalog"):
    with scenario("Show the products in stock"):
        with given("the catalog holds a kettle in stock"):
            pass
        with when("the Customer opens the catalog"):
            pass
        with then("the kettle is listed"):
            pass
'''
_THIN_SLICE = """# Thin Slice

## Increment 1: Browse

- Customer --> Browse Product Catalog
"""
_MODULE_CARD = """# src/{module}

- **Purpose:** let a customer work with the {module}
- **Seam (terms):** Book
- **Dependencies (one-way):** none
"""
_CLASS_MODEL = """# Ordering

**Module:** `src/ordering`

## Cart

### **Cart** <<Aggregate Root>>

+ Cart(customer_id: str)
------
+ customer_id: str
"""


with description("Render"):
    with it("should convert python on a Guidance ref string when source is python"):
        results = Render().render(
            _REF,
            format="markdown",
            paths=[],
            content=_PYTHON,
            source="python",
        )
        expect(len(results)).to(equal(1))
        expect(str(results[0].content)).to(contain("Cart"))

    with it("should construct the Guidance at the given fidelity"):
        results = Render().render(
            {"toolset": _REF, "fidelity": "model"},
            format="markdown",
            paths=[],
            content=_PYTHON,
        )
        expect(str(results[0].content)).to(contain("Cart"))

    with it("should convert each guidance slug you type"):
        results = Render().render(
            ["clean-engineering-model", "bdd-behavior"],
            format="python",
            paths=[],
            content="### **Cart**\n+ owner: str\n",
            source="sketch",
        )
        expect(len(results)).to(equal(2))
        expect(results[0].format).to(equal("python"))
        expect(results[1].format).to(equal("python"))

    with it("should convert a story map when source is md"):
        results = Render().render(
            _STORIES,
            format="drawio",
            paths=[],
            content=_STORY_MAP,
            source="md",
        )
        expect(str(results[0].content)).to(contain("mxGraphModel"))

    with it("should read a sketch from a file path and leave the document body off the call"):
        folder = Path(tempfile.mkdtemp(prefix="render-paths-"))
        sketch = folder / "orders-sketch.md"
        sketch.write_text(_STORY_MAP, encoding="utf-8")
        results = Render().render(_STORIES, format="markdown", paths=[str(sketch)], source="sketch")
        expect(Path(results[0].path).read_text(encoding="utf-8")).to(contain("Browse Product Catalog"))

    with it("should read the sketches in a folder"):
        folder = Path(tempfile.mkdtemp(prefix="render-folder-"))
        (folder / "orders-sketch.md").write_text(_STORY_MAP, encoding="utf-8")
        results = Render().render(_STORIES, format="markdown", paths=str(folder), source="sketch")
        expect(Path(results[0].path).read_text(encoding="utf-8")).to(contain("Browse Product Catalog"))

    with it("should read the story tests in a folder under their story map"):
        folder = Path(tempfile.mkdtemp(prefix="render-story-tests-"))
        (folder / "story-map.md").write_text(_MARKDOWN_STORY_MAP, encoding="utf-8")
        story_test = folder / "manage-customer-orders" / "place-new-order" / "browse-product-catalog"
        story_test.mkdir(parents=True)
        (story_test / "browse_product_catalog_story.test.py").write_text(_STORY_TEST, encoding="utf-8")
        rendered = Stories(fidelity="scenarios").fidelities.current.render_files("markdown", str(folder), "python")
        expect(str(rendered.content)).to(contain("Scenario: Show the products in stock"))

    with it("should link a rendered story map to the story files beside the map it reads"):
        folder = Path(tempfile.mkdtemp(prefix="render-links-"))
        story_map = folder / "story-map.md"
        story_map.write_text(_MARKDOWN_STORY_MAP, encoding="utf-8")
        story_file = folder / "orders" / "browse_product_catalog_story.test.md"
        story_file.parent.mkdir(parents=True)
        story_file.write_text("## Story: Browse Product Catalog\n", encoding="utf-8")
        Render().render(
            _STORIES,
            format="drawio",
            paths=[str(story_map)],
            source="markdown",
        )
        expect((folder / "story-map.drawio").read_text(encoding="utf-8")).to(contain('link="orders/browse_product_catalog_story.test.md"'))


with description("Render publishing a whiteboard file to its board in Claude") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="render-board-"))
        self.file = self.folder / "story-map.whiteboard"
        self.file.write_text(Whiteboard("Story Map").save(), encoding="utf-8")

    with context("that the agent created a board for"):
        with it("should keep the board's address beside the file, so the Files app opens the board"):
            Render().record_board(str(self.file), "https://claude.ai/artifact/StoryMapBoard")
            expect(Whiteboard.links_beside(self.file).of(self.file.name)).to(equal("https://claude.ai/artifact/StoryMapBoard"))

    with context("that was published before"):
        with before.each:
            self.other = self.folder / "modules.whiteboard"
            Whiteboard.links_beside(self.file).record(self.other.name, "https://claude.ai/artifact/ModulesBoard")
            Whiteboard.links_beside(self.file).record(self.file.name, "https://claude.ai/artifact/OldBoard")

        with it("should keep only the new address"):
            Render().record_board(str(self.file), "https://claude.ai/artifact/NewBoard")
            expect(Whiteboard.links_beside(self.file).of(self.file.name)).to(equal("https://claude.ai/artifact/NewBoard"))

        with it("should leave the other files' addresses as they were"):
            Render().record_board(str(self.file), "https://claude.ai/artifact/NewBoard")
            expect(Whiteboard.links_beside(self.other).of(self.other.name)).to(equal("https://claude.ai/artifact/ModulesBoard"))

    with context("that is not a whiteboard file"):
        with before.each:
            self.drawio = self.folder / "story-map.drawio"
            self.drawio.write_text("<mxfile/>", encoding="utf-8")

        with it("should refuse to record a board for it"):
            expect(lambda: Render().record_board(str(self.drawio), "https://claude.ai/artifact/X")).to(raise_error(ValueError, contain(".whiteboard")))

        with it("should keep no address"):
            try:
                Render().record_board(str(self.drawio), "https://claude.ai/artifact/X")
            except ValueError:
                pass
            expect((self.folder / Whiteboard.LINKS).exists()).to(equal(False))

    with context("rendered to the whiteboard format"):
        with it("should tell the agent to publish the board after the conversion returns"):
            expect(Render.render.__doc__).to(contain("publish_board"))

        with it("should tell the agent to create a Whiteboard artifact when no address is kept, and record its address"):
            text = AgentInstructions.for_callable(Render.publish_board, Render()).expand({}).instructions
            expect(text).to(contain("Whiteboard artifact"))
            expect(text).to(contain("record_board"))

        with it("should tell the agent to write only the changed elements to a board already kept"):
            text = AgentInstructions.for_callable(Render.publish_board, Render()).expand({}).instructions
            expect(text).to(contain("batches"))


def _card_holding(drawio: str, name: str) -> ET.Element:
    """The cell drawing name in a draw.io story map: the cell itself, or the one inside the link that carries it."""
    for holder in ET.fromstring(drawio).iter():
        if holder.get("value") == name or holder.get("label") == name:
            return holder if holder.tag == "mxCell" else holder.find("mxCell")
    raise AssertionError(f"no cell draws {name}")


def _moved_card(drawio: str, name: str, x: str) -> str:
    """drawio with the card drawing name moved to x, as draw.io saves it after a person drags the card."""
    root = ET.fromstring(drawio)
    for holder in root.iter():
        if holder.get("value") == name or holder.get("label") == name:
            cell = holder if holder.tag == "mxCell" else holder.find("mxCell")
            cell.find("mxGeometry").set("x", x)
    return ET.tostring(root, encoding="unicode")


def _written_ids(result: dict) -> list:
    return [entry["doc_id"] for batch in result.batches for entry in batch]


with description("Render saving what it makes beside its source") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="render-beside-")) / ".context"
        self.folder.mkdir()
        self.story_map = self.folder / "story-map.md"
        self.story_map.write_text(_MARKDOWN_STORY_MAP, encoding="utf-8")

    with context("a story map rendered to drawio from its markdown"):
        with before.each:
            self.results = Render().render(_STORIES, format="drawio", paths=[str(self.story_map)], source="markdown")
            self.drawing = self.folder / "story-map.drawio"

        with it("should save the drawing beside the markdown, under the name the story map fidelity writes it to"):
            expect(self.drawing.read_text(encoding="utf-8")).to(contain("Browse Product Catalog"))

        with it("should answer with the file it saved"):
            expect(self.results[0].path).to(equal(str(self.drawing)))

        with it("should leave the drawing out of its answer, so the agent has nothing to place"):
            expect(data_of(self.results[0])).not_to(have_key("content"))

    with context("a story map whose drawing a person moved a card on"):
        with before.each:
            Render().render(_STORIES, format="drawio", paths=[str(self.story_map)], source="markdown")
            self.drawing = self.folder / "story-map.drawio"
            moved = _moved_card(self.drawing.read_text(encoding="utf-8"), "Browse Product Catalog", "777")
            self.drawing.write_text(moved, encoding="utf-8")
            Render().render(_STORIES, format="drawio", paths=[str(self.story_map)], source="markdown")

        with it("should keep the card where the person put it"):
            card = _card_holding(self.drawing.read_text(encoding="utf-8"), "Browse Product Catalog")
            expect(card.find("mxGeometry").get("x")).to(equal("777"))

    with context("a story map whose drawing a person laid out, with another markdown file beside it"):
        with before.each:
            Render().render(_STORIES, format="drawio", paths=[str(self.story_map)], source="markdown")
            self.drawing = self.folder / "story-map.drawio"
            self.laid_out = _moved_card(self.drawing.read_text(encoding="utf-8"), "Browse Product Catalog", "777")
            self.drawing.write_text(self.laid_out, encoding="utf-8")
            self.other = self.folder / "returns.md"

        with context("that holds a story map of its own, rendered to drawio"):
            with before.each:
                self.other.write_text(_OTHER_STORY_MAP, encoding="utf-8")
                self.results = Render().render(_STORIES, format="drawio", paths=[str(self.other)], source="markdown")

            with it("should leave the story map's drawing as the person laid it out"):
                expect(self.drawing.read_text(encoding="utf-8")).to(equal(self.laid_out))

            with it("should save the other file's drawing under that file's own name"):
                expect((self.folder / "returns.drawio").read_text(encoding="utf-8")).to(contain("Return Damaged Item"))

            with it("should answer with the file it saved"):
                expect(self.results[0].path).to(equal(str(self.folder / "returns.drawio")))

        with context("that is empty, rendered to drawio"):
            with before.each:
                self.other.write_text("  ", encoding="utf-8")
                self.render = lambda: Render().render(_STORIES, format="drawio", paths=[str(self.other)], source="markdown")

            with it("should refuse the render, naming the empty file"):
                expect(self.render).to(raise_error(NothingToRender, contain("returns.md")))

            with it("should leave the story map's drawing as the person laid it out"):
                try:
                    self.render()
                except NothingToRender:
                    pass
                expect(self.drawing.read_text(encoding="utf-8")).to(equal(self.laid_out))

    with context("a story map with its own title, rendered to drawio and back to markdown"):
        with before.each:
            self.story_map.write_text("# Story Map — Bookshop\n\n" + _MARKDOWN_STORY_MAP, encoding="utf-8")
            Render().render(_STORIES, format="drawio", paths=[str(self.story_map)], source="markdown")
            Render().render(_STORIES, format="markdown", paths=[str(self.folder / "story-map.drawio")], source="drawio")

        with it("should keep the map's own title"):
            expect(self.story_map.read_text(encoding="utf-8")).to(contain("# Story Map — Bookshop"))

        with it("should keep the stories the drawing holds"):
            expect(self.story_map.read_text(encoding="utf-8")).to(contain("Browse Product Catalog"))

    with context("a story map rendered to markdown from its sketch"):
        with before.each:
            self.sketch = self.folder / "orders-sketch.md"
            self.sketch.write_text(_STORY_MAP, encoding="utf-8")
            self.story_map.unlink()
            Render().render(_STORIES, format="markdown", paths=[str(self.sketch)], source="sketch")

        with it("should save the document beside the sketch"):
            expect(self.story_map.read_text(encoding="utf-8")).to(contain("Browse Product Catalog"))

        with it("should leave the sketch as it was"):
            expect(self.sketch.read_text(encoding="utf-8")).to(equal(_STORY_MAP))

    with context("a model rendered to code in no session"):
        with before.each:
            self.sketch = self.folder / "cart-sketch.md"
            self.sketch.write_text("Cart\n  owner\n", encoding="utf-8")
            self.render = lambda: Render().render(["clean-engineering-model"], format="python", paths=[str(self.sketch)], source="sketch")

        with it("should refuse, since no session says where the code is written"):
            expect(self.render).to(raise_error(RenderHasNoDeclaredPlace, contain("in a session")))

        with it("should save no file"):
            try:
                self.render()
            except RenderHasNoDeclaredPlace:
                pass
            expect(sorted(path.name for path in self.folder.iterdir())).to(equal(["cart-sketch.md", "story-map.md"]))

    with context("a story map rendered to whiteboard"):
        with before.each:
            self.results = Render().render(_STORIES, format="whiteboard", paths=[str(self.story_map)], source="markdown")
            self.board_file = self.folder / "story-map.whiteboard"

        with it("should save the board file beside the markdown"):
            expect(Whiteboard.from_text(self.board_file.read_text(encoding="utf-8")).title).to(equal("Story Map"))

        with it("should answer with the writes that put the whole board on a new board in Claude"):
            saved = Whiteboard.from_text(self.board_file.read_text(encoding="utf-8"))
            expect(len(_written_ids(self.results[0]))).to(equal(len(saved.elements) + 1))

        with it("should answer with no board, since none is kept for the file yet"):
            expect(self.results[0].board).to(equal(""))

    with context("a story map whose board is kept and a person moved a card on"):
        with before.each:
            Render().render(_STORIES, format="whiteboard", paths=[str(self.story_map)], source="markdown")
            self.board_file = self.folder / "story-map.whiteboard"
            Whiteboard.links_beside(self.board_file).record(self.board_file.name, "https://claude.ai/artifact/StoryMapBoard")
            board = json.loads(self.board_file.read_text(encoding="utf-8"))
            self.card = next(key for key, record in board["elements"].items() if "Browse Product Catalog" in str(record.get("text")))
            board["elements"][self.card]["x"] = 777
            self.board_file.write_text(json.dumps(board), encoding="utf-8")
            self.results = Render().render(_STORIES, format="whiteboard", paths=[str(self.story_map)], source="markdown")

        with it("should keep the card where the person put it"):
            expect(json.loads(self.board_file.read_text(encoding="utf-8"))["elements"][self.card]["x"]).to(equal(777))

        with it("should answer with the board kept for the file"):
            expect(self.results[0].board).to(equal("https://claude.ai/artifact/StoryMapBoard"))

        with it("should write none of the elements the render left as they were"):
            expect(_written_ids(self.results[0])).to(equal(["meta"]))

    with context("a story map's whiteboard file rendered to drawio with no source named"):
        with before.each:
            Render().render(_STORIES, format="whiteboard", paths=[str(self.story_map)], source="markdown")
            Render().render(_STORIES, format="drawio", paths=[str(self.folder / "story-map.whiteboard")])

        with it("should read the file as the whiteboard its name says it is"):
            expect((self.folder / "story-map.drawio").read_text(encoding="utf-8")).to(contain("Browse Product Catalog"))

    with context("rendered from content, with no paths"):
        with it("should answer with what it made, since it has no source to save beside"):
            results = Render().render(_STORIES, format="drawio", paths=[], content=_STORY_MAP, source="md")
            expect(str(results[0].content)).to(contain("mxGraphModel"))


with description("A render whose worker process failed"):
    with it("should say what failed in one line, the worker's own last word"):
        failure = RenderFailed(1, _WORKER_TRACEBACK)
        expect(str(failure)).to(equal("the render's worker process exited with 1: MarkdownParseError: Not a valid Markdown story map: no recognised structure found"))

    with it("should keep the worker's whole error output for whoever debugs it"):
        expect(RenderFailed(1, _WORKER_TRACEBACK).errors).to(equal(_WORKER_TRACEBACK))


with description("Render asked for a path, in a session") as self:
    # The first story map a process renders to a drawing imports the drawing's format adapter and every practice's
    # graph reading, which each later render uses as it is; rendered once here, so no example pays for that first import.
    with before.all:
        warmed = ThrowawayProject()
        (warmed.root / "story-map.md").write_text(_MARKDOWN_STORY_MAP, encoding="utf-8")
        Render().for_call(ToolCall({}, warmed.root)).render("stories-story-map", format="drawio", paths=["story-map.md"], source="markdown")
        warmed.close()

    with before.each:
        self.project = ThrowawayProject()
        self.folder = self.project.root / ".context"
        self.folder.mkdir()
        (self.folder / "story-map.md").write_text(_MARKDOWN_STORY_MAP, encoding="utf-8")
        self.action = Render().for_call(ToolCall({}, self.project.root))

    with after.each:
        self.project.close()

    with context("that is outside the session's root"):
        with before.each:
            self.outside = Path(tempfile.mkdtemp(prefix="render-outside-")) / "story-map.md"
            self.outside.write_text(_MARKDOWN_STORY_MAP, encoding="utf-8")
            self.render = lambda: self.action.render("stories-story-map", format="drawio", paths=[str(self.outside)], source="markdown")

        with it("should refuse the path by name, as validate does"):
            expect(self.render).to(raise_error(NamedPathNotFoundError, contain("under the session's root")))

        with it("should write no drawing beside it"):
            try:
                self.render()
            except NamedPathNotFoundError:
                pass
            expect((self.outside.parent / "story-map.drawio").exists()).to(equal(False))

    with context("that is not there"):
        with it("should refuse the path by name"):
            render = lambda: self.action.render("stories-story-map", format="drawio", paths=["nope/missing.md"], source="markdown")
            expect(render).to(raise_error(NamedPathNotFoundError, contain("nope/missing.md")))

    with context("that is under the session's root"):
        with it("should save the drawing beside it"):
            self.action.render("stories-story-map", format="drawio", paths=[".context/story-map.md"], source="markdown")
            expect((self.folder / "story-map.drawio").read_text(encoding="utf-8")).to(contain("Browse Product Catalog"))

        # A path named from the project's root is the project's, never the folder the process happens to run in.
        with it("should link each story to its own file in the project"):
            story_file = self.folder / "orders" / "browse_product_catalog_story.test.md"
            story_file.parent.mkdir()
            story_file.write_text("## Story: Browse Product Catalog\n", encoding="utf-8")
            self.action.render("stories-story-map", format="drawio", paths=[".context/story-map.md"], source="markdown")
            expect((self.folder / "story-map.drawio").read_text(encoding="utf-8")).to(contain('link="orders/browse_product_catalog_story.test.md"'))

    # Exploratory testing, r3-gizmo-03: a mockup rendered to claude_design answered {} and saved nothing, and a canvas
    # could not be read back. The person's answer (2026-11-23): a mockup render to claude_design works and renders back.
    with context("that is a mockup in html, rendered to claude_design"):
        with before.each:
            self.mockup = HtmlUxMap.create().render(OrderingMap().build(UxMap.create()))
            (self.project.root / "bookshop").mkdir()
            (self.project.root / "bookshop" / "buy-a-book.html").write_text(self.mockup, encoding="utf-8")
            self.canvas = self.project.root / "design-canvas"
            self.to_canvas = lambda: self.action.render("ux-mockup", format="claude_design", paths=["bookshop/buy-a-book.html"], source="html")

        with it("should save canvas.json and a prototype page for each screen in the canvas's first version"):
            self.to_canvas()
            saved = sorted(path.relative_to(self.canvas).as_posix() for path in self.canvas.rglob("*") if path.is_file())
            expect(saved).to(equal(["version-1/project/canvas.json", "version-1/project/screens/cart-saved.dc.html",
                                    "version-1/project/screens/cart.dc.html", "version-1/project/screens/catalog.dc.html"]))

        with it("should render back to the same HTML mockup from its canvas.json"):
            self.to_canvas()
            back = self.action.render("ux-mockup", format="html", paths=["design-canvas/version-1/project/canvas.json"], source="claude_design")
            expect(back[0].content).to(equal(self.mockup))

        with context("whose canvas's latest version is published"):
            with it("should refuse to write into it"):
                self.to_canvas()
                CanvasVersions.in_practice_root(self.project.root).latest.publish_at("https://claude.ai/artifact/canvas")
                expect(self.to_canvas).to(raise_error(PublishedVersion))

        with context("whose canvas holds a screen people ported where a prototype page goes"):
            with it("should refuse to write over it"):
                self.to_canvas()
                (self.canvas / "version-1" / "project" / "screens" / "cart.dc.html").write_text("<html>ported cart</html>", encoding="utf-8")
                expect(self.to_canvas).to(raise_error(CanvasFileNotRendered, contain("cart.dc.html")))

    # Exploratory testing, r3-rivet-08: a realization rendered from a saved graph was saved as graph.md beside the graph,
    # a name no fidelity writes, while the fidelity declares .context/{scope}-bdd-realization.md. The person's answer
    # (2026-11-20): every render ends in a saved file, so its scope is named from what the graph was read from.
    with context("that is a saved graph read from one spec, rendered to the markdown realization"):
        with before.each:
            (self.project.root / "src" / "ordering").mkdir(parents=True)
            (self.project.root / "src" / "ordering" / "cart_spec.py").write_text(_CART_SPEC, encoding="utf-8")
            graph = self.action.session.graph
            graph.load_files(str(self.project.root), ["bdd"], ["src/ordering/cart_spec.py"])
            self.graph_file = Path(graph.save_json().path)
            self.results = self.action.render("bdd-realization", format="markdown", source="graph", paths=[str(self.graph_file)])

        with it("should save the realization where the fidelity declares it, its scope named for the spec"):
            expect(Path(self.results[0].path).relative_to(self.project.root).as_posix()).to(equal(".context/cart-bdd-realization.md"))

        with it("should write the spec's subject into it"):
            expect((self.folder / "cart-bdd-realization.md").read_text(encoding="utf-8")).to(contain("a cart"))

        with it("should answer no content for the agent to save"):
            expect(data_of(self.results[0])).not_to(have_key("content"))

    with context("that is a saved graph holding no spec, rendered to the markdown realization"):
        with before.each:
            self.graphs = self.project.root / "graphs"
            self.graphs.mkdir()
            (self.graphs / "graph.json").write_text(SavedGraph.from_violations([]).text, encoding="utf-8")
            self.render = lambda: self.action.render("bdd-realization", format="markdown", source="graph", paths=["graphs/graph.json"])

        with it("should refuse, since nothing in the graph names the realization's scope"):
            expect(self.render).to(raise_error(RenderHasNoDeclaredPlace, contain("{scope}")))

        with it("should save no file named after the graph"):
            try:
                self.render()
            except RenderHasNoDeclaredPlace:
                pass
            expect(sorted(path.name for path in self.graphs.iterdir())).to(equal(["graph.json"]))

    with context("that is a spec in Python, rendered to TypeScript"):
        with before.each:
            (self.project.root / "src" / "ordering").mkdir(parents=True)
            (self.project.root / "src" / "ordering" / "cart_spec.py").write_text(_CART_SPEC, encoding="utf-8")
            self.results = self.action.render("bdd-behavior", format="typescript", paths=["src/ordering/cart_spec.py"])

        with it("should save the spec beside it under the name TypeScript specs carry"):
            saved = [Path(path).relative_to(self.project.root).as_posix() for path in self.results[0].paths]
            expect(saved).to(equal(["src/ordering/cart.spec.ts"]))

    with context("that is a realization in markdown, rendered to Python"):
        with before.each:
            (self.folder / "bookshop-bdd-realization.md").write_text(_REALIZATION, encoding="utf-8")
            self.results = self.action.render("bdd-realization", format="python", paths=[".context/bookshop-bdd-realization.md"])

        with it("should save one spec named for the realization's scope, in the folder its .context sits in"):
            saved = [Path(path).relative_to(self.project.root).as_posix() for path in self.results[0].paths]
            expect(saved).to(equal(["bookshop_spec.py"]))

    # The person's decision (2026-11-22): nobody fills the record of a module's test tiers by hand; the render that
    # writes the module's tests fills it.
    with context("that is a TypeScript spec in a module's folder, rendered to the Python spec BDD development fills"):
        with before.each:
            module = self.project.root / "shop" / ".context"
            module.mkdir(parents=True)
            (module / "module-context.md").write_text("# shop\n", encoding="utf-8")
            (self.project.root / "shop" / "cart.spec.ts").write_text(_CART_SPEC_IN_TYPESCRIPT, encoding="utf-8")
            self.results = self.action.render("bdd-development", format="python", paths=["shop/cart.spec.ts"])
            self.session = Sessions(self.project.root).current()

        with it("should record the unit tier, with its test tool, for the module the spec was saved in"):
            expect(self.session.test_tiers.recorded).to(equal({"shop": {"unit": "mamba"}}))

        with it("should answer what it recorded and what is left for the agent to decide"):
            expect(data_of(self.results[0])["test_tiers"]).to(contain("shop: unit (mamba)", "cannot tell whether shop"))

    with context("that is a realization in markdown, rendered to the Python spec of a fidelity that keeps no test tiers"):
        with it("should answer nothing about test tiers"):
            (self.folder / "bookshop-bdd-realization.md").write_text(_REALIZATION, encoding="utf-8")
            results = self.action.render("bdd-realization", format="python", paths=[".context/bookshop-bdd-realization.md"])
            expect(data_of(results[0])).not_to(have_key("test_tiers"))

    # Exploratory testing, r3-bolt-06 and r3-sparky-07: a render to code answered its content and saved nothing. The
    # person's answer (2026-11-20): every render ends in a saved file.
    # Each render here reads the domain model into a graph, so each context renders once, in a project of its own, and
    # its examples only read what that left.
    with context("that is a domain model in markdown, rendered to Python"):
        with before.all:
            self.domain_project = ThrowawayProject()
            (self.domain_project.root / ".context").mkdir()
            (self.domain_project.root / ".context" / "domain-model.md").write_text(_DOMAIN_MODEL, encoding="utf-8")
            self.domain_render = Render().for_call(ToolCall({}, self.domain_project.root))
            self.domain_results = self.domain_render.render("ddd-model", format="python", paths=[".context/domain-model.md"])
            self.cart = self.domain_project.root / "ordering" / "cart" / "cart.py"
            self.cart_first_text = self.cart.read_text(encoding="utf-8")

        with after.all:
            self.domain_project.close()

        with it("should save a file for each aggregate where the fidelity declares it"):
            saved = sorted(Path(path).relative_to(self.domain_project.root).as_posix() for path in self.domain_results[0].paths)
            expect(saved).to(equal(["ordering/cart/cart.py", "ordering/order/order.py"]))

        with it("should write the aggregate's classes into its file"):
            expect(self.cart_first_text).to(contain("class Cart"))

        with it("should answer no code for the agent to save"):
            expect(data_of(self.domain_results[0])).not_to(have_key("content"))

        with context("whose code a person then changed, rendered again"):
            with before.all:
                self.cart.write_text("class Cart:" + chr(10) + "    def total(self):" + chr(10) + "        return 5" + chr(10), encoding="utf-8")
                self.rerendered = self.domain_render.render("ddd-model", format="python", paths=[".context/domain-model.md"])
                self.cart_kept_text = self.cart.read_text(encoding="utf-8")

            with it("should keep the code the person wrote"):
                expect(self.cart_kept_text).to(contain("return 5"))

            with it("should name the file among those that hold the render"):
                expect("cart.py" in [Path(path).name for path in self.rerendered[0].paths]).to(equal(True))

    # The person's answer (2026-11-21): a render reshapes an existing file and loses nothing. Their example: a class
    # that already has code, an operation added in the markdown model, rendered again.
    with context("that is a class model whose class already has code, with an operation added in the markdown, rendered again"):
        with before.all:
            self.added_project = ThrowawayProject()
            rendering = Render().for_call(ToolCall({}, self.added_project.root))
            model = self.added_project.root / "src" / "ordering" / ".context" / "ordering-model.md"
            model.parent.mkdir(parents=True)
            model.write_text(_CART_MODEL, encoding="utf-8")
            rendering.render("clean-engineering-model", format="python", paths=["src/ordering/.context/ordering-model.md"])
            code = self.added_project.root / "src" / "ordering" / "ordering.py"
            code.write_text(code.read_text(encoding="utf-8").replace(_EMPTY_TOTAL, _TOTAL_WITH_CODE), encoding="utf-8")
            model.write_text(_CART_MODEL + "+ check_out(): int" + chr(10), encoding="utf-8")
            self.added_results = rendering.render("clean-engineering-model", format="python", paths=["src/ordering/.context/ordering-model.md"])
            self.written = code.read_text(encoding="utf-8")

        with after.all:
            self.added_project.close()

        with it("should put the code back in the class"):
            expect(self.written).to(contain(_TOTAL_WITH_CODE))

        with it("should add the new operation empty"):
            expect(self.written).to(contain("    def check_out(self) -> int:" + chr(10) + "        raise NotImplementedError"))

        with it("should name the file as holding the render, with nothing to migrate"):
            expect((len(self.added_results[0].paths), self.added_results[0].migrate)).to(equal((1, [])))

    # The same class model, its code written, then total renamed to subtotal in the markdown and rendered again: three
    # renders, made once in a project of their own so each example only reads what they left.
    with context("that is a class model whose class has code, with total then renamed to subtotal in the markdown, rendered again"):
        with before.all:
            self.renamed_project = ThrowawayProject()
            rendering = Render().for_call(ToolCall({}, self.renamed_project.root))
            model = self.renamed_project.root / "src" / "ordering" / ".context" / "ordering-model.md"
            model.parent.mkdir(parents=True)
            model.write_text(_CART_MODEL, encoding="utf-8")
            rendering.render("clean-engineering-model", format="python", paths=["src/ordering/.context/ordering-model.md"])
            self.renamed_code = self.renamed_project.root / "src" / "ordering" / "ordering.py"
            self.renamed_code.write_text(self.renamed_code.read_text(encoding="utf-8").replace(_EMPTY_TOTAL, _TOTAL_WITH_CODE), encoding="utf-8")
            model.write_text(_CART_MODEL.replace("+ total(): int", "+ subtotal(): int"), encoding="utf-8")
            self.renamed_migrate = rendering.render("clean-engineering-model", format="python", paths=["src/ordering/.context/ordering-model.md"])[0].migrate

        with after.all:
            self.renamed_project.close()

        with it("should list total as kept, and subtotal among what may have replaced it"):
            kept = next(each for each in self.renamed_migrate if each.kept == "Cart.total")
            expect("Cart.subtotal" in kept.may_have_replaced_it).to(equal(True))

        with it("should keep total's code in the file, marked as no longer in the model"):
            written = self.renamed_code.read_text(encoding="utf-8")
            expect(written.index("no longer in the model: Cart.total") < written.index("return sum(line.subtotal for line in self.lines)")).to(equal(True))

    with context("that tells the agent what to do after a render kept members no longer in the model"):
        with it("should tell it to move each kept body into the member that replaced it, and only then delete it"):
            expect(Render.place_rendered.__doc__).to(contain("migrate as your next step", "move its body into the member that replaced it", "Delete the kept member and its marking line only once"))

    with context("that is the class model of one module in markdown, rendered to Python"):
        with before.each:
            (self.project.root / "src" / "ordering" / ".context").mkdir(parents=True)
            (self.project.root / "src" / "ordering" / ".context" / "ordering-model.md").write_text(_CLASS_MODEL, encoding="utf-8")
            self.results = self.action.render("clean-engineering-model", format="python", paths=["src/ordering/.context/ordering-model.md"])

        with it("should save the module's code in the module's own folder, where the model's .context sits"):
            saved = [Path(path).relative_to(self.project.root).as_posix() for path in self.results[0].paths]
            expect(saved).to(equal(["src/ordering/ordering.py"]))

    # The heavy tier, 2026-11-20: the guidance diagnostics probe renders a file of its own, which no fidelity
    # declares, into the format it is already in, and was refused. A document or a drawing is never refused.
    with context("that is a markdown file no fidelity declares, rendered to markdown by two fidelities"):
        with before.each:
            self.notes = self.project.root / "notes" / "probe.md"
            self.notes.parent.mkdir()
            self.notes.write_text(_MARKDOWN_STORY_MAP, encoding="utf-8")
            self.results = self.action.render(["stories", "clean-engineering-model"], format="markdown", source="markdown", paths=["notes/probe.md"])

        with it("should name the file itself for each, since it is already in that format"):
            expect([Path(result.path) for result in self.results]).to(equal([self.notes, self.notes]))

        with it("should keep the file as it was"):
            expect(self.notes.read_text(encoding="utf-8")).to(equal(_MARKDOWN_STORY_MAP))

    with context("that is a sketch no fidelity's file is named for, rendered to markdown"):
        with before.each:
            (self.project.root / "design").mkdir()
            (self.project.root / "design" / "cart-sketch.md").write_text("Cart\n  owner\n", encoding="utf-8")
            self.results = self.action.render("clean-engineering-model", format="markdown", source="sketch", paths=["design/cart-sketch.md"])

        with it("should save the document beside the sketch under the sketch's own name"):
            expect(Path(self.results[0].path).relative_to(self.project.root).as_posix()).to(equal("design/cart.md"))

        with it("should write the sketch's class into it"):
            expect((self.project.root / "design" / "cart.md").read_text(encoding="utf-8")).to(contain("Cart"))

    # The heavy tier, 2026-11-20: a sketch of Cart rendered to Python was saved as knowledge_graph/knowledge_graph.py,
    # after the module name the sketch reader gives a sketch that names none.
    with context("that is a sketch naming no module, rendered to Python"):
        with before.each:
            (self.project.root / "design").mkdir()
            (self.project.root / "design" / "cart-sketch.md").write_text("Cart\n  owner\n", encoding="utf-8")
            self.results = self.action.render("clean-engineering-model", format="python", source="sketch", paths=["design/cart-sketch.md"])

        with it("should save the code beside the sketch, as a module named for the sketch"):
            saved = [Path(path).relative_to(self.project.root).as_posix() for path in self.results[0].paths]
            expect(saved).to(equal(["design/cart/cart.py"]))

    # The person's answer (2026-11-21): a render must not ever remove what is already there. On the Bookshop a note a
    # person added to a story map's drawing was gone after the next render.
    # Each render below happens once, in a project of its context's own, and the examples read what it left: a render
    # in an example or its setup ran a few milliseconds over the unit tier's budget for one example.
    with context("that is a story map rendered to drawio"):
        with before.all:
            self.drawn_project = _story_map_project()
            _render_story_map(self.drawn_project)

        with after.all:
            self.drawn_project.close()

        with it("should save the drawing beside the story map"):
            expect((self.drawn_project.root / ".context" / "story-map.drawio").read_text(encoding="utf-8")).to(contain("<mxfile"))

    with context("that is a story map whose drawing a person added a note to, rendered to drawio again"):
        with before.all:
            self.noted_again = _story_map_project()
            _render_story_map(self.noted_again)
            self.drawing = self.noted_again.root / ".context" / "story-map.drawio"
            self.drawing.write_text(self.drawing.read_text(encoding="utf-8").replace("</root>", _NOTE_CELL + "</root>", 1), encoding="utf-8")
            self.results = _render_story_map(self.noted_again)

        with after.all:
            self.noted_again.close()

        with it("should keep the note in the drawing"):
            expect(self.drawing.read_text(encoding="utf-8")).to(contain('id="person-note"', "Ask Dana before changing this"))

        with it("should name the note as kept, for whoever decides where it belongs"):
            expect([(Path(each.file).name, each.kept) for each in self.results[0].migrate]).to(equal([("story-map.drawio", "person-note 'Ask Dana before changing this'")]))

        # The person's ruling, 2026-11-22: what the source no longer holds goes to an agent who decides by reading.
        with it("should tell the agent to decide what becomes of the note by reading it against the story map"):
            expect(data_of(self.results[0])["decide"]).to(contain("decide by reading the leftover against what the source now holds"))

    # The coordinator, 2026-11-21: a drawing that held only a person's note, and no card of the map, was saved as
    # rendered and the note was gone.
    # The render happens once, in a project of the context's own, and both examples read what it left: a render in
    # each example's setup ran a few milliseconds over the unit tier's budget for one example.
    with context("that is a story map whose drawing holds only a note a person wrote, rendered to drawio"):
        with before.all:
            self.noted = ThrowawayProject()
            noted_folder = self.noted.root / ".context"
            noted_folder.mkdir()
            (noted_folder / "story-map.md").write_text(_MARKDOWN_STORY_MAP, encoding="utf-8")
            self.noted_drawing = noted_folder / "story-map.drawio"
            self.noted_drawing.write_text(_NOTE_ONLY_DRAWING, encoding="utf-8")
            rendering = Render().for_call(ToolCall({}, self.noted.root))
            self.noted_results = rendering.render("stories-story-map", format="drawio", paths=[".context/story-map.md"], source="markdown")

        with after.all:
            self.noted.close()

        with it("should keep the note beside the cards the render drew"):
            expect(self.noted_drawing.read_text(encoding="utf-8")).to(contain('id="person-note"', "Browse Product Catalog"))

        with it("should name the note as kept"):
            expect([each.kept for each in self.noted_results[0].migrate]).to(equal(["person-note 'Ask Dana before changing this'"]))

    with context("that tells the agent what to do with what it rendered"):
        with it("should not tell the agent to write rendered content itself"):
            expect(Render.place_rendered.__doc__).not_to(contain("write it yourself"))

    # Exploratory testing, r3-sparky-01: the thin slice, a file the story map fidelity declares, was drawn over the story
    # map's drawing.
    # The two renders happen once, in a project of the context's own, and every example reads what they left.
    with context("that is the story map's thin slice, beside the story map's drawing"):
        with before.all:
            self.sliced = ThrowawayProject()
            self.sliced_folder = self.sliced.root / ".context"
            self.sliced_folder.mkdir()
            (self.sliced_folder / "story-map.md").write_text(_MARKDOWN_STORY_MAP, encoding="utf-8")
            rendering = Render().for_call(ToolCall({}, self.sliced.root))
            rendering.render("stories-story-map", format="drawio", paths=[".context/story-map.md"], source="markdown")
            self.drawn = (self.sliced_folder / "story-map.drawio").read_text(encoding="utf-8")
            (self.sliced_folder / "thin-slice.md").write_text(_THIN_SLICE, encoding="utf-8")
            self.sliced_results = rendering.render("stories-story-map", format="drawio", paths=[".context/thin-slice.md"], source="markdown")

        with after.all:
            self.sliced.close()

        with it("should save the thin slice's drawing under the name the fidelity declares for it"):
            expect(Path(self.sliced_results[0].path).name).to(equal("thin-slice.drawio"))

        with it("should leave the story map's drawing as it was"):
            expect((self.sliced_folder / "story-map.drawio").read_text(encoding="utf-8")).to(equal(self.drawn))

    # Exploratory testing, r3-widget-01: one drawing of every module was saved in the first module's own folder.
    with context("that is the module card of each of two modules, rendered to one drawing"):
        with before.each:
            for module in ("catalogue", "ordering"):
                card = self.project.root / "src" / module / ".context" / "module-context.md"
                card.parent.mkdir(parents=True)
                card.write_text(_MODULE_CARD.format(module=module), encoding="utf-8")
            cards = ["src/catalogue/.context/module-context.md", "src/ordering/.context/module-context.md"]
            self.results = self.action.render("clean-engineering-modules", format="drawio", paths=cards)

        with it("should save the drawing in the root's .context, where the modules fidelity declares it"):
            expect(Path(self.results[0].path)).to(equal(self.folder / "modules.drawio"))

        with it("should save no drawing in the first module's folder"):
            expect((self.project.root / "src" / "catalogue" / ".context" / "modules.drawio").exists()).to(equal(False))

    # Exploratory testing, r3-widget-05 and widget-09: a .md file with no source named was read in the format the
    # fidelity works in, Python for a class model, and refused as Python that does not parse.
    with context("that is a class model in markdown, with no source named, at a fidelity that works in Python"):
        with before.each:
            model = self.project.root / "src" / "ordering" / ".context" / "ordering-model.md"
            model.parent.mkdir(parents=True)
            model.write_text(_CLASS_MODEL, encoding="utf-8")
            self.results = self.action.render("clean-engineering-model", format="drawio", paths=["src/ordering/.context/ordering-model.md"])

        with it("should read the file as the markdown its name says it is"):
            expect(Path(self.results[0].path).read_text(encoding="utf-8")).to(contain("Cart"))

        with it("should save the drawing beside the model, under the name the fidelity declares for the module"):
            expect(Path(self.results[0].path)).to(equal(self.project.root / "src" / "ordering" / ".context" / "ordering-model.drawio"))

    # The dev lane's server, 2026-11-22: a render read a module card's `**Purpose:**` line as Python, because the files
    # it read in the format the fidelity works in were named by a folder, a sketch's name, or a source the call named.
    with context("that is a module's .context folder of markdown, with no source named, at a fidelity that works in Python"):
        with before.each:
            folder = self.project.root / "src" / "ordering" / ".context"
            folder.mkdir(parents=True)
            (folder / "ordering-model.md").write_text(_CLASS_MODEL, encoding="utf-8")
            (folder / "module-context.md").write_text(_MODULE_CARD.format(module="ordering"), encoding="utf-8")
            self.results = self.action.render("clean-engineering-model", format="drawio", paths=["src/ordering/.context"])

        with it("should read the folder's files as the markdown their names say they are"):
            expect(Path(self.results[0].path).read_text(encoding="utf-8")).to(contain("Cart"))

    with context("that is a sketch, with no source named, at a fidelity that works in Python"):
        with before.each:
            (self.project.root / "design").mkdir()
            (self.project.root / "design" / "cart-sketch.md").write_text("Cart\n  owner\n", encoding="utf-8")
            self.results = self.action.render("clean-engineering-model", format="drawio", paths=["design/cart-sketch.md"])

        with it("should read the file as the sketch its name says it is"):
            expect(Path(self.results[0].path).read_text(encoding="utf-8")).to(contain("Cart"))

    with context("that is a class model in markdown, with python named as its source"):
        with before.each:
            model = self.project.root / "src" / "ordering" / ".context" / "ordering-model.md"
            model.parent.mkdir(parents=True)
            model.write_text(_CLASS_MODEL, encoding="utf-8")
            self.render = lambda: self.action.render("clean-engineering-model", format="drawio", paths=["src/ordering/.context/ordering-model.md"], source="python")

        with it("should refuse the render, naming the file and the format its name says it is in"):
            expect(self.render).to(raise_error(SourceFormatRefused, contain("ordering-model.md", "markdown", "python")))

    # The heavy tier, 2026-11-24: a UX view in CheckoutView.tsx, named as typescript, was refused as a tsx file.
    with context("that is code in a .tsx file, with typescript named as its source"):
        with before.each:
            (self.project.root / "src").mkdir()
            (self.project.root / "src" / "Cart.tsx").write_text("export class Cart {\n  total(): number {\n    return 0;\n  }\n}\n", encoding="utf-8")
            self.results = self.action.render("clean-engineering-model", format="markdown", paths=["src/Cart.tsx"], source="typescript")

        with it("should read the file as the TypeScript its extension says it is"):
            expect(Path(self.results[0].path).read_text(encoding="utf-8")).to(contain("Cart"))

    with context("that is a file in a format the fidelity reads none of"):
        with before.each:
            (self.project.root / "design").mkdir()
            (self.project.root / "design" / "cart.png").write_bytes(b"\x89PNG\r\n")
            self.render = lambda: self.action.render("clean-engineering-model", format="drawio", paths=["design/cart.png"])

        with it("should refuse the render, naming the file and its format"):
            expect(self.render).to(raise_error(SourceFormatRefused, contain("cart.png", "png", "clean-engineering-model")))

        with it("should save no drawing beside it"):
            try:
                self.render()
            except SourceFormatRefused:
                pass
            expect((self.project.root / "design" / "cart.drawio").exists()).to(equal(False))

    with context("that is two files in different formats, with no source named"):
        with before.each:
            (self.folder / "story-map.drawio").write_text("<mxfile></mxfile>", encoding="utf-8")
            paths = [".context/story-map.md", ".context/story-map.drawio"]
            self.render = lambda: self.action.render("stories-story-map", format="whiteboard", paths=paths)

        with it("should refuse the render, naming each file's format"):
            expect(self.render).to(raise_error(SourceFormatRefused, contain("story-map.md", "markdown", "story-map.drawio", "drawio")))

    # Exploratory testing, widget-16: one render of the story map and the scenarios to drawio wrote the scenarios'
    # drawing over the story map's, though the scenarios fidelity declares no drawing.
    with context("that is the story map, rendered to drawio at the story map and at the scenarios at once"):
        with before.each:
            self.render = lambda: self.action.render(["stories-story-map", "stories-scenarios"], format="drawio", paths=[".context/story-map.md"], source="markdown")

        with it("should refuse the fidelity that declares no drawing, naming it and the format"):
            expect(self.render).to(raise_error(FormatNotDeclared, contain("stories-scenarios", "drawio")))

        with it("should save no drawing for either fidelity"):
            try:
                self.render()
            except FormatNotDeclared:
                pass
            expect((self.folder / "story-map.drawio").exists()).to(equal(False))

    with context("that is the story map, rendered to drawio at the story map alone"):
        with it("should save the drawing under the story map fidelity's own name for it"):
            results = self.action.render(["stories-story-map"], format="drawio", paths=[".context/story-map.md"], source="markdown")
            expect([Path(result.path).name for result in results]).to(equal(["story-map.drawio"]))

    # Exploratory testing, widget-15: a class model rendered from code to markdown was saved beside the code under the
    # code's own name, not under the name the model fidelity writes markdown to.
    with context("that is TypeScript code in a module's folder, named for none of its classes, rendered to markdown at the class model"):
        with before.each:
            code = self.project.root / "src" / "ordering" / "cart.ts"
            code.parent.mkdir(parents=True)
            code.write_text("export class Cart {\n  total(): number {\n    return 0;\n  }\n}\n", encoding="utf-8")
            self.results = self.action.render("clean-engineering-model", format="markdown", paths=["src/ordering/cart.ts"])

        with it("should save the model in the module's .context, under the name the fidelity writes markdown to"):
            expect(Path(self.results[0].path).relative_to(self.project.root).as_posix()).to(equal("src/ordering/.context/ordering-model.md"))

    # Exploratory testing, r3-rivet-11: a finished spec rendered to a tree format came back as signatures only.
    with context("that is a finished Python spec, rendered to the markdown realization"):
        with before.each:
            spec = self.project.root / "src" / "cart_spec.py"
            spec.parent.mkdir()
            spec.write_text(_FINISHED_SPEC, encoding="utf-8")
            self.render = lambda: self.action.render("bdd-realization", format="markdown", paths=["src/cart_spec.py"])

        with it("should refuse the render, naming the test whose body would be lost"):
            expect(self.render).to(raise_error(SpecBodiesNotKept, contain("should total its lines")))

    with context("that is a finished Python spec, rendered to markdown at development, which declares none"):
        with it("should refuse the render, naming the fidelity and the format"):
            (self.project.root / "src").mkdir()
            (self.project.root / "src" / "cart_spec.py").write_text(_FINISHED_SPEC, encoding="utf-8")
            render = lambda: self.action.render("bdd-development", format="markdown", paths=["src/cart_spec.py"])
            expect(render).to(raise_error(FormatNotDeclared, contain("bdd-development", "markdown")))


with description("A comment a person left on a board in Claude") as self:
    with before.each:
        self.project = ThrowawayProject()
        self.folder = self.project.root / ".context"
        self.folder.mkdir()
        (self.folder / "story-map.md").write_text(_MARKDOWN_STORY_MAP, encoding="utf-8")
        self.board_file = self.folder / "story-map.whiteboard"
        self.board_file.write_text(Whiteboard("Story Map").save(), encoding="utf-8")
        self.action = Render().for_call(ToolCall({}, self.project.root))

    with after.each:
        self.project.close()

    with context("on the board the story map's whiteboard file was published to"):
        with before.each:
            Whiteboard.links_beside(self.board_file).record(self.board_file.name, "https://claude.ai/artifact/StoryMapBoard")
            answer = AgentInstructions.for_callable(Render.answer_board_comment, self.action)
            self.text = answer.expand({"board": "https://claude.ai/artifact/StoryMapBoard"}).instructions

        with it("should hand the agent the rules of the fidelity that draws the board"):
            expect(self.text).to(contain("verb-noun-format"))

        with it("should name the whiteboard file the board was published from"):
            expect(self.text).to(contain(".context/story-map.whiteboard"))

        with it("should name the story map file to change, which the board is drawn from"):
            expect(self.text).to(contain(".context/story-map.md"))

    with context("on a board no whiteboard file in the project was published to"):
        with it("should refuse, naming the board, rather than let the agent answer without the guidance"):
            answer = AgentInstructions.for_callable(Render.answer_board_comment, self.action)
            expanded = lambda: answer.expand({"board": "https://claude.ai/artifact/Elsewhere"})
            expect(expanded).to(raise_error(RecipeLineFailed, contain(BoardNotKept.__name__, "keeps the board https://claude.ai/artifact/Elsewhere")))
