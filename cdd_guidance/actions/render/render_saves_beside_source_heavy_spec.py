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

from harness.mcp.spec_support import SpecServer
from harness.whiteboard import Whiteboard
from space.session.throwaway_project import OPEN_PROJECTS, ThrowawayProject

_RENDER = "cdd_guidance.actions.render.render:Render"
_SESSIONS = "space.session.sessions:Sessions"
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


async def _answer_comment(server: SpecServer, project: Path, board: str) -> tuple[bool, str]:
    async with server.chat(project, _CALL_SECONDS) as chat:
        result = await chat.call_tool("render.answer_board_comment", arguments={"board": board})
        return bool(result.isError), result.content[0].text


def _card(drawio: str, name: str) -> ET.Element:
    """The cell drawing name in a draw.io story map: the cell itself, or the one inside the link that carries it."""
    for holder in ET.fromstring(drawio).iter():
        if holder.get("value") == name or holder.get("label") == name:
            return holder if holder.tag == "mxCell" else holder.find("mxCell")
    raise AssertionError(f"no cell draws {name}")


with description("Render saving what it makes beside its source, called through a cdd server") as self:
    with before.all:
        self.server = SpecServer((_RENDER, _SESSIONS))
        self.server.start()

    with after.all:
        self.server.stop()

    with before.each:
        self.project = ThrowawayProject()
        self.folder = self.project.root / ".context"
        self.folder.mkdir()
        (self.folder / "story-map.md").write_text(_STORY_MAP, encoding="utf-8")
        self.drawing = self.folder / "story-map.drawio"

    with after.each:
        OPEN_PROJECTS.close_all()

    with context("a story map rendered to drawio"):
        with before.each:
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio"))

        with it("should save the drawing beside the markdown"):
            expect(self.drawing.read_text(encoding="utf-8")).to(contain("Browse Product Catalog"))

        with it("should answer the chat with the saved file rather than the drawing"):
            expect((self.failed, "story-map.drawio" in self.answer, "mxGraphModel" in self.answer)).to(equal((False, True, False)))

    # Exploratory testing, r3-bolt-06: a domain model rendered to Python came back as one text and nothing was saved.
    # The person's answer (2026-11-20): every render ends in a saved file.
    with context("a domain model rendered to Python"):
        with before.each:
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
        with before.each:
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
        with before.each:
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
        with before.each:
            asyncio.run(_render(self.server, self.project.root, "drawio"))
            self.drawn = self.drawing.read_text(encoding="utf-8")

        with context("that holds a story map of its own, rendered to drawio"):
            with before.each:
                (self.folder / "returns.md").write_text(_STORY_MAP.replace("Browse Product Catalog", "Return Damaged Item"), encoding="utf-8")
                self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio", ".context/returns.md"))

            with it("should leave the story map's drawing as it was"):
                expect(self.drawing.read_text(encoding="utf-8")).to(equal(self.drawn))

            with it("should save the other file's drawing under that file's own name"):
                expect((self.folder / "returns.drawio").read_text(encoding="utf-8")).to(contain("Return Damaged Item"))

        with context("that is empty, rendered to drawio"):
            with before.each:
                (self.folder / "empty.md").write_text("", encoding="utf-8")
                self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio", ".context/empty.md"))

            with it("should refuse the render, naming the empty file"):
                expect((self.failed, "NothingToRender" in self.answer, "empty.md" in self.answer)).to(equal((True, True, True)))

            with it("should leave the story map's drawing as it was"):
                expect(self.drawing.read_text(encoding="utf-8")).to(equal(self.drawn))

    # Exploratory testing, r3-sparky-01: the thin slice, a file the story map fidelity declares, was drawn over the story
    # map's drawing.
    with context("a story map whose drawing is there, with its thin slice rendered to drawio"):
        with before.each:
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
        with before.each:
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

    # Exploratory testing, r3-widget-05: a .md class model with no source named was read as Python by the worker.
    with context("a class model in markdown rendered to drawio with no source named"):
        with before.each:
            self.model = self.project.root / "src" / "ordering" / ".context" / "ordering-model.md"
            self.model.parent.mkdir(parents=True)
            self.model.write_text(_CLASS_MODEL, encoding="utf-8")
            path = "src/ordering/.context/ordering-model.md"
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio", path, None, "clean-engineering-model"))

        with it("should draw the class the markdown holds, beside the model"):
            drawing = self.model.with_suffix(".drawio")
            expect((self.failed, drawing.is_file() and "Cart" in drawing.read_text(encoding="utf-8"))).to(equal((False, True)))

    # Exploratory testing, widget-07: render took ../outside.md and wrote story-map.drawio outside the project.
    with context("a story map outside the project, named from it"):
        with before.each:
            self.outside = self.project.root.parent / f"{self.project.root.name}-outside"
            self.outside.mkdir()
            (self.outside / "story-map.md").write_text(_STORY_MAP, encoding="utf-8")
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio", f"../{self.outside.name}/story-map.md"))

        with after.each:
            shutil.rmtree(self.outside, ignore_errors=True)

        with it("should refuse the path by name, as validate does"):
            expect((self.failed, "NamedPathNotFoundError" in self.answer, self.outside.name in self.answer)).to(equal((True, True, True)))

        with it("should write no drawing outside the project"):
            expect((self.outside / "story-map.drawio").exists()).to(equal(False))

    # Exploratory testing, widget-09: a whiteboard file with no source named was read as markdown and failed with the
    # worker's traceback.
    with context("a story map's whiteboard file rendered to drawio with no source named"):
        with before.each:
            asyncio.run(_render(self.server, self.project.root, "whiteboard"))
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio", ".context/story-map.whiteboard", source=None))

        with it("should draw the story map the whiteboard holds"):
            expect((self.failed, "Browse Product Catalog" in self.drawing.read_text(encoding="utf-8"))).to(equal((False, True)))

    with context("a file that is no story map, rendered to drawio as markdown"):
        with before.each:
            (self.folder / "notes.md").write_text("just some words\n", encoding="utf-8")
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "drawio", ".context/notes.md"))

        with it("should fail in one line, with no traceback"):
            expect((self.failed, "Traceback" in self.answer)).to(equal((True, False)))

    # Exploratory testing, widget-04: the drawing holds no title, so the markdown written back from it took the
    # template's, and the save wrote that over the person's file.
    with context("a story map with its own title and scope, rendered to drawio and back to markdown"):
        with before.each:
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
        with before.each:
            asyncio.run(_render(self.server, self.project.root, "whiteboard"))
            board_file = self.folder / "story-map.whiteboard"
            Whiteboard.links_beside(board_file).record(board_file.name, _BOARD)
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

    with after.all:
        self.server.stop()

    with before.each:
        self.project = ThrowawayProject()
        folder = self.project.root / ".context"
        folder.mkdir()
        (folder / "story-map.md").write_text(_STORY_MAP, encoding="utf-8")
        asyncio.run(_render(self.server, self.project.root, "whiteboard"))
        board_file = folder / "story-map.whiteboard"
        Whiteboard.links_beside(board_file).record(board_file.name, _BOARD)

    with after.each:
        OPEN_PROJECTS.close_all()

    with context("on the board the story map's whiteboard file was published to"):
        with before.each:
            self.failed, self.answer = asyncio.run(_answer_comment(self.server, self.project.root, _BOARD))

        with it("should hand the chat the story map fidelity's rules"):
            expect((self.failed, "verb-noun-format" in self.answer)).to(equal((False, True)))

        with it("should name the story map file to change"):
            expect(self.answer).to(contain(".context/story-map.md"))

    with context("on a board no whiteboard file in the project was published to"):
        with before.each:
            self.failed, self.answer = asyncio.run(_answer_comment(self.server, self.project.root, "https://claude.ai/artifact/Elsewhere"))

        with it("should refuse, naming the board"):
            expect((self.failed, "https://claude.ai/artifact/Elsewhere" in self.answer)).to(equal((True, True)))
