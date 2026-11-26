"""Render saving the diagram it makes beside its source, called by a chat through a real cdd server: the twin of
``render_spec.py``'s in-process examples, run against the server process as an agent calls ``render.render``. Heavy: the
spec starts a cdd server of its own, on its own port, from a throwaway ``~/.cdd``, and works on a throwaway project, so
it runs beside any other spec and never reaches the person's server."""
import asyncio
import json
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.practices.ux.model.html.nodes import HtmlUxMap
from cdd_guidance.practices.ux.model.ux_map import UxMap
from cdd_guidance.practices.ux.model.ux_map_spec_fixture import OrderingMap
from harness.mcp.spec_support import SpecServer
from harness.whiteboard import Whiteboard
from space.session.spec_support.throwaway_project import OPEN_PROJECTS, ThrowawayProject

_RENDER = "cdd_guidance.actions.render.render:Render"
_SESSIONS = "space.session.sessions:Sessions"
_GRAPH = "harness.graph.graph:Graph"
_CALL_SECONDS = 120
_BOARD = "https://claude.ai/artifact/StoryMapBoard"
_STORY_MAP = """\
# (E) Manage Customer Orders

## (E) Place New Order

### (S) Customer --> Browse Product Catalog
"""


_BOOKSHOP_STORY_MAP = """\
# Story Map — Bookshop

**In scope:** orders placed in the shop

# (E) Sell Books

## (E) Take Orders

### (S) Customer --> Place Order
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
_THIN_SLICE = """# Thin Slice

## Increments

### Increment 1: Browse

- *Browse Product Catalog*
"""
_MODULE_CARD = """# src/{module}

- **Purpose:** let a customer work with the {module}
- **Seam (terms):** Book
- **Dependencies (one-way):** none
"""
_CART_SPEC = """from mamba import description, it


with description("a cart"):
    with it("should total its lines"):
        pass
"""
_CLASS_MODEL = """# Ordering

**Module:** `src/ordering`

## Cart

### **Cart** <<Aggregate Root>>

+ Cart(customer_id: str)
------
+ customer_id: str
"""


async def _render(
    server: SpecServer, project: Path, format: str, path: str | list[str] = ".context/story-map.md", source: str | None = "markdown",
    guidance: str = "stories-story-map",
) -> tuple[bool, str]:
    async with server.chat(project, _CALL_SECONDS) as chat:
        paths = [path] if isinstance(path, str) else path
        arguments = {"guidance": guidance, "format": format, "paths": paths, **({"source": source} if source else {})}
        result = await chat.call_tool("render.render", arguments=arguments)
        return bool(result.isError), result.content[0].text


async def _realization_steps(server: SpecServer, project: Path) -> tuple[str, str]:
    """The BDD realization's steps as its guidance writes them, called through the server: load the specs and the code
    with ``graph.load_files``, save the graph with ``graph.save_json``, and render the path the save answers to the
    markdown realization. Answers the path the save named and the file the render saved."""
    async with server.chat(project, _CALL_SECONDS) as chat:
        loaded = {"folder": str(project), "practices": ["bdd", "clean_engineering"], "files": ["src"]}
        await chat.call_tool("graph.load_files", arguments=loaded)
        saved = json.loads((await chat.call_tool("graph.save_json", arguments={})).content[0].text)["path"]
        arguments = {"guidance": "bdd-realization", "format": "markdown", "source": "graph", "paths": [saved]}
        rendered = json.loads((await chat.call_tool("render.render", arguments=arguments)).content[0].text)
        return saved, rendered[0]["path"]


async def _description_of(server: SpecServer, project: Path, tool: str) -> str:
    async with server.chat(project, _CALL_SECONDS) as chat:
        return next(listed.description for listed in (await chat.list_tools()).tools if listed.name == tool)


async def _answer_comment(server: SpecServer, project: Path, board: str) -> tuple[bool, str]:
    async with server.chat(project, _CALL_SECONDS) as chat:
        result = await chat.call_tool("render.answer_board_comment", arguments={"board": board})
        return bool(result.isError), result.content[0].text


def _open_story_map(spec) -> None:
    """Give spec, a context's state, a throwaway project of its own whose .context holds the story map, made once
    before the context's examples: every render a context makes is made once, and its examples only read what it left."""
    spec.project = ThrowawayProject()
    spec.folder = spec.project.root / ".context"
    spec.folder.mkdir()
    (spec.folder / "story-map.md").write_text(_STORY_MAP, encoding="utf-8")
    spec.drawing = spec.folder / "story-map.drawio"


def _card(drawio: str, name: str) -> ET.Element:
    """The cell drawing name in a draw.io story map: the cell itself, or the one inside the link that carries it."""
    for holder in ET.fromstring(drawio).iter():
        if holder.get("value") == name or holder.get("label") == name:
            return holder if holder.tag == "mxCell" else holder.find("mxCell")
    raise AssertionError(f"no cell draws {name}")


with description("Render saving what it makes beside its source, called through a cdd server") as self:
    with before.all:
        self.server = SpecServer((_RENDER, _SESSIONS, _GRAPH))
        self.server.start()

    # Each context renders once, in a project of its own, before its examples, which only read what it saved; every
    # project is closed once the examples are done.
    with after.all:
        OPEN_PROJECTS.close_all()
        self.server.stop()

    with context("a story map rendered to drawio"):
        with before.all:
            _open_story_map(self)
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio"))

        with it("should save the drawing beside the markdown"):
            expect(self.drawing.read_text(encoding="utf-8")).to(contain("Browse Product Catalog"))

        with it("should answer the chat with the saved file rather than the drawing"):
            expect((self.failed, "story-map.drawio" in self.answer, "mxGraphModel" in self.answer)).to(equal((False, True, False)))

    # Exploratory testing, r3-gizmo-03: a mockup rendered to claude_design answered {} and saved nothing, and its canvas
    # could not be read back. The person's answer (2026-11-23): a mockup render to claude_design works and renders back.
    with context("a mockup in html rendered to claude_design, then its canvas rendered back to html"):
        with before.all:
            _open_story_map(self)
            self.mockup = HtmlUxMap.create().render(OrderingMap().build(UxMap.create()))
            (self.project.root / "bookshop").mkdir()
            (self.project.root / "bookshop" / "buy-a-book.html").write_text(self.mockup, encoding="utf-8")
            self.to_canvas = asyncio.run(_render(self.server, self.project.root, "claude_design", "bookshop/buy-a-book.html", "html", "ux-mockup"))
            self.back = asyncio.run(_render(self.server, self.project.root, "html", "design-canvas/version-1/project/canvas.json", "claude_design", "ux-mockup"))

        with it("should save a prototype page for each screen beside the canvas's canvas.json"):
            project = self.project.root / "design-canvas" / "version-1" / "project"
            saved = sorted(path.relative_to(project).as_posix() for path in project.rglob("*") if path.is_file())
            expect(saved).to(equal(["canvas.json", "screens/cart-saved.dc.html", "screens/cart.dc.html", "screens/catalog.dc.html"]))

        with it("should answer the same HTML mockup on the way back"):
            expect(json.loads(self.back[1])[0]["content"]).to(equal(self.mockup))

    # Exploratory testing, r3-bolt-06: a domain model rendered to Python came back as one text and nothing was saved.
    # The person's answer (2026-11-20): every render ends in a saved file.
    with context("a domain model rendered to Python"):
        with before.all:
            _open_story_map(self)
            (self.folder / "domain-model.md").write_text(_DOMAIN_MODEL, encoding="utf-8")
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "python", ".context/domain-model.md", None, "ddd-model"))

        with it("should save a file for each aggregate where the fidelity declares it"):
            saved = sorted(path.relative_to(self.project.root).as_posix() for path in self.project.root.glob("ordering/*/*.py"))
            expect(saved).to(equal(["ordering/cart/cart.py", "ordering/order/order.py"]))

        with it("should answer the chat with the saved files rather than the code"):
            expect((self.failed, "cart.py" in self.answer, "class Cart" in self.answer)).to(equal((False, True, False)))

    # The person's answer (2026-11-21): a render reshapes an existing file and loses nothing. Their example, through
    # the cdd server: a class that already has code, an operation added in the markdown model, rendered again.
    with context("a class model whose class already has code, with an operation added in the markdown, rendered again"):
        with before.all:
            _open_story_map(self)
            self.model = self.project.root / "src" / "ordering" / ".context" / "ordering-model.md"
            self.model.parent.mkdir(parents=True)
            self.model.write_text(_CART_MODEL, encoding="utf-8")
            asyncio.run(_render(self.server, self.project.root, "python", "src/ordering/.context/ordering-model.md", None, "clean-engineering-model"))
            self.code = self.project.root / "src" / "ordering" / "ordering.py"
            self.code.write_text(self.code.read_text(encoding="utf-8").replace(_EMPTY_TOTAL, _TOTAL_WITH_CODE), encoding="utf-8")
            self.model.write_text(_CART_MODEL.replace("+ total(): int", "+ subtotal(): int") + "+ check_out(): int\n", encoding="utf-8")
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "python", "src/ordering/.context/ordering-model.md", None, "clean-engineering-model"))
            self.written = self.code.read_text(encoding="utf-8")

        with it("should keep the code the class had, marked as no longer in the model since total was renamed"):
            expect(self.written.index("no longer in the model: Cart.total") < self.written.index("return sum(line.subtotal for line in self.lines)")).to(equal(True))

        with it("should add the operations the model gained, empty"):
            expect(self.written).to(contain("    def subtotal(self) -> int:\n        raise NotImplementedError", "    def check_out(self) -> int:\n        raise NotImplementedError"))

        with it("should answer the chat what to migrate: total, and the added operations that may have replaced it"):
            migrate = json.loads(self.answer)[0]["migrate"]
            expect([(each["kept"], each["may_have_replaced_it"]) for each in migrate]).to(equal([("Cart.total", ["Cart.check_out", "Cart.subtotal"])]))

    with context("a story map whose drawing a person moved a card on"):
        with before.all:
            _open_story_map(self)
            asyncio.run(_render(self.server, self.project.root, "drawio"))
            root = ET.fromstring(self.drawing.read_text(encoding="utf-8"))
            for holder in root.iter():
                if holder.get("label") == "Browse Product Catalog" or holder.get("value") == "Browse Product Catalog":
                    (holder if holder.tag == "mxCell" else holder.find("mxCell")).find("mxGeometry").set("x", "777")
            self.drawing.write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
            asyncio.run(_render(self.server, self.project.root, "drawio"))

        with it("should keep the card where the person put it"):
            expect(_card(self.drawing.read_text(encoding="utf-8"), "Browse Product Catalog").find("mxGeometry").get("x")).to(equal("777"))

    # Exploratory testing, widget-06: a render of any markdown file in the folder was saved as story-map.drawio.
    with context("a story map whose drawing is there, with another markdown file beside it"):
        with before.all:
            _open_story_map(self)
            asyncio.run(_render(self.server, self.project.root, "drawio"))
            self.drawn = self.drawing.read_text(encoding="utf-8")

        with context("that holds a story map of its own, rendered to drawio"):
            with before.all:
                (self.folder / "returns.md").write_text(_STORY_MAP.replace("Browse Product Catalog", "Return Damaged Item"), encoding="utf-8")
                self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio", ".context/returns.md"))

            with it("should leave the story map's drawing as it was"):
                expect(self.drawing.read_text(encoding="utf-8")).to(equal(self.drawn))

            with it("should save the other file's drawing under that file's own name"):
                expect((self.folder / "returns.drawio").read_text(encoding="utf-8")).to(contain("Return Damaged Item"))

        with context("that is empty, rendered to drawio"):
            with before.all:
                (self.folder / "empty.md").write_text("", encoding="utf-8")
                self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio", ".context/empty.md"))

            with it("should refuse the render, naming the empty file"):
                expect((self.failed, "NothingToRender" in self.answer, "empty.md" in self.answer)).to(equal((True, True, True)))

            with it("should leave the story map's drawing as it was"):
                expect(self.drawing.read_text(encoding="utf-8")).to(equal(self.drawn))

    # Exploratory testing, r3-sparky-01: the thin slice, a file the story map fidelity declares, was drawn over the story
    # map's drawing.
    with context("a story map whose drawing is there, with its thin slice rendered to drawio"):
        with before.all:
            _open_story_map(self)
            asyncio.run(_render(self.server, self.project.root, "drawio"))
            self.drawn = self.drawing.read_text(encoding="utf-8")
            (self.folder / "thin-slice.md").write_text(_THIN_SLICE, encoding="utf-8")
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio", ".context/thin-slice.md"))

        with it("should answer the chat with the thin slice's own drawing"):
            expect((self.failed, "thin-slice.drawio" in self.answer, (self.folder / "thin-slice.drawio").is_file())).to(equal((False, True, True)))

        with it("should leave the story map's drawing as it was"):
            expect(self.drawing.read_text(encoding="utf-8")).to(equal(self.drawn))

    # Exploratory testing, r3-widget-01: one drawing of every module was saved in the first module's own folder.
    with context("the module cards of two modules rendered to one drawing, with no source named"):
        with before.all:
            _open_story_map(self)
            for module in ("catalogue", "ordering"):
                card = self.project.root / "src" / module / ".context" / "module-context.md"
                card.parent.mkdir(parents=True)
                card.write_text(_MODULE_CARD.format(module=module), encoding="utf-8")
            cards = ["src/catalogue/.context/module-context.md", "src/ordering/.context/module-context.md"]
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio", cards, None, "clean-engineering-modules"))

        with it("should save the drawing in the root's .context, where the modules fidelity declares it"):
            expect((self.failed, (self.folder / "modules.drawio").is_file())).to(equal((False, True)))

        with it("should save no drawing in the first module's folder"):
            expect((self.project.root / "src" / "catalogue" / ".context" / "modules.drawio").exists()).to(equal(False))

        # r3-widget-01, step 4: the drawing of every module rendered back to markdown was saved as one modules.md
        # beside it, a name the modules fidelity never writes, holding every card a second time.
        with context("then that drawing rendered back to markdown"):
            with before.all:
                self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "markdown", ".context/modules.drawio", None, "clean-engineering-modules"))

            with it("should write each module's card back to its own module-context.md"):
                saved = sorted(Path(path).relative_to(self.project.root).as_posix() for path in json.loads(self.answer)[0]["paths"])
                expect((self.failed, saved)).to(equal((False, ["src/catalogue/.context/module-context.md", "src/ordering/.context/module-context.md"])))

            with it("should keep each card's own words in its file"):
                card = self.project.root / "src" / "ordering" / ".context" / "module-context.md"
                expect(card.read_text(encoding="utf-8")).to(contain("let a customer work with the ordering"))

            with it("should save no modules.md beside the drawing"):
                expect((self.folder / "modules.md").exists()).to(equal(False))

    # Exploratory testing, r3-widget-05: a .md class model with no source named was read as Python by the worker.
    with context("a class model in markdown rendered to drawio with no source named"):
        with before.all:
            _open_story_map(self)
            self.model = self.project.root / "src" / "ordering" / ".context" / "ordering-model.md"
            self.model.parent.mkdir(parents=True)
            self.model.write_text(_CLASS_MODEL, encoding="utf-8")
            path = "src/ordering/.context/ordering-model.md"
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio", path, None, "clean-engineering-model"))

        with it("should draw the class the markdown holds, beside the model"):
            drawing = self.model.with_suffix(".drawio")
            expect((self.failed, drawing.is_file() and "Cart" in drawing.read_text(encoding="utf-8"))).to(equal((False, True)))

    # Exploratory testing, r3-rivet-08: the realization's steps said graph.save_json writes .context/graph.json and to
    # render that path, while the save writes the session's own folder, so the render drew an older graph a validate
    # had left in .context.
    with context("a spec rendered to its realization by the realization guidance's steps, with an older graph in .context"):
        with before.all:
            _open_story_map(self)
            spec = self.project.root / "src" / "ordering" / "cart_spec.py"
            spec.parent.mkdir(parents=True)
            spec.write_text(_CART_SPEC, encoding="utf-8")
            (self.folder / "graph.json").write_text("{}", encoding="utf-8")
            self.saved, self.rendered = asyncio.run(_realization_steps(self.server, self.project.root))

        with it("should save the graph in the session's own folder, not in the project's .context"):
            expect(Path(self.saved).parent.parent.name).to(equal(".sessions"))

        with it("should say so in the save's description the agent reads"):
            expect(asyncio.run(_description_of(self.server, self.project.root, "graph.save_json"))).to(contain("session's own folder"))

        with it("should save the realization of the loaded spec where the fidelity declares it"):
            expect(Path(self.rendered).relative_to(self.project.root).as_posix()).to(equal(".context/cart-bdd-realization.md"))

        with it("should draw the spec just loaded"):
            expect(Path(self.rendered).read_text(encoding="utf-8")).to(contain("a cart"))

    # Exploratory testing, widget-07: render took ../outside.md and wrote story-map.drawio outside the project.
    with context("a story map outside the project, named from it"):
        with before.all:
            _open_story_map(self)
            self.outside = self.project.root.parent / f"{self.project.root.name}-outside"
            self.outside.mkdir()
            (self.outside / "story-map.md").write_text(_STORY_MAP, encoding="utf-8")
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio", f"../{self.outside.name}/story-map.md"))

        with after.all:
            shutil.rmtree(self.outside, ignore_errors=True)

        with it("should refuse the path by name, as validate does"):
            expect((self.failed, "NamedPathNotFoundError" in self.answer, self.outside.name in self.answer)).to(equal((True, True, True)))

        with it("should write no drawing outside the project"):
            expect((self.outside / "story-map.drawio").exists()).to(equal(False))

    # Exploratory testing, widget-09: a whiteboard file with no source named was read as markdown and failed with the
    # worker's traceback.
    with context("a story map's whiteboard file rendered to drawio with no source named"):
        with before.all:
            _open_story_map(self)
            asyncio.run(_render(self.server, self.project.root, "whiteboard"))
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio", ".context/story-map.whiteboard", source=None))

        with it("should draw the story map the whiteboard holds"):
            expect((self.failed, "Browse Product Catalog" in self.drawing.read_text(encoding="utf-8"))).to(equal((False, True)))

    with context("a file that is no story map, rendered to drawio as markdown"):
        with before.all:
            _open_story_map(self)
            (self.folder / "notes.md").write_text("just some words\n", encoding="utf-8")
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio", ".context/notes.md"))

        with it("should fail in one line, with no traceback"):
            expect((self.failed, "Traceback" in self.answer)).to(equal((True, False)))

    # Exploratory testing, widget-04: the drawing holds no title, so the markdown written back from it took the
    # template's, and the save wrote that over the person's file.
    with context("a story map with its own title and scope, rendered to drawio and back to markdown"):
        with before.all:
            _open_story_map(self)
            (self.folder / "story-map.md").write_text(_BOOKSHOP_STORY_MAP, encoding="utf-8")
            asyncio.run(_render(self.server, self.project.root, "drawio"))
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "markdown", ".context/story-map.drawio", "drawio"))
            self.written_back = (self.folder / "story-map.md").read_text(encoding="utf-8")

        with it("should keep the map's own title"):
            expect((self.failed, "# Story Map — Bookshop" in self.written_back)).to(equal((False, True)))

        with it("should keep the scope the person wrote above the first epic"):
            expect(self.written_back).to(contain("**In scope:** orders placed in the shop"))

        with it("should keep the stories the drawing holds"):
            expect(self.written_back).to(contain("Customer --> Place Order"))

    with context("a story map whose board is kept, rendered to whiteboard again"):
        with before.all:
            _open_story_map(self)
            asyncio.run(_render(self.server, self.project.root, "whiteboard"))
            board_file = self.folder / "story-map.whiteboard"
            board_file.write_text(Whiteboard.published_to(board_file.read_text(encoding="utf-8"), _BOARD), encoding="utf-8")
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "whiteboard"))

        with it("should answer the chat with the board kept for the file"):
            expect((self.failed, _BOARD in self.answer)).to(equal((False, True)))

        with it("should answer with only the board's meta to write, since nothing changed"):
            batches = json.loads(self.answer)
            batches = batches[0]["batches"] if isinstance(batches, list) else batches["batches"]
            expect([entry["doc_id"] for batch in batches for entry in batch]).to(equal(["meta"]))


with description("A comment a person left on a board in Claude, answered through a cdd server") as self:
    with before.all:
        self.server = SpecServer((_RENDER, _SESSIONS))
        self.server.start()

        _open_story_map(self)
        asyncio.run(_render(self.server, self.project.root, "whiteboard"))
        board_file = self.folder / "story-map.whiteboard"
        board_file.write_text(Whiteboard.published_to(board_file.read_text(encoding="utf-8"), _BOARD), encoding="utf-8")

    with after.all:
        OPEN_PROJECTS.close_all()
        self.server.stop()

    with context("on the board the story map's whiteboard file was published to"):
        with before.all:
            self.failed, self.answer = asyncio.run(_answer_comment(self.server, self.project.root, _BOARD))

        with it("should hand the chat the story map fidelity's rules"):
            expect((self.failed, "verb-noun-format" in self.answer)).to(equal((False, True)))

        with it("should name the story map file to change"):
            expect(self.answer).to(contain(".context/story-map.md"))

    with context("on a board no whiteboard file in the project was published to"):
        with before.all:
            self.failed, self.answer = asyncio.run(_answer_comment(self.server, self.project.root, "https://claude.ai/artifact/Elsewhere"))

        with it("should refuse, naming the board"):
            expect((self.failed, "https://claude.ai/artifact/Elsewhere" in self.answer)).to(equal((True, True)))
