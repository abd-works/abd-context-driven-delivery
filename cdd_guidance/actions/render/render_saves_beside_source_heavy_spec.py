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
from harness.whiteboard import BoardLinks
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


async def _render(server: SpecServer, project: Path, format: str, path: str = ".context/story-map.md", source: str | None = "markdown") -> tuple[bool, str]:
    async with server.chat(project, _CALL_SECONDS) as chat:
        arguments = {"guidance": "stories-story-map", "format": format, "paths": [path], **({"source": source} if source else {})}
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

    with context("a story map whose board is kept, rendered to whiteboard again"):
        with before.each:
            asyncio.run(_render(self.server, self.project.root, "whiteboard"))
            board_file = self.folder / "story-map.whiteboard"
            BoardLinks.beside(board_file).record(board_file, _BOARD)
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
        BoardLinks.beside(board_file).record(board_file, _BOARD)

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
