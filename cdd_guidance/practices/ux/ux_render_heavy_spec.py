"""A mockup rendered to its diagram by a chat through a real cdd server: the drawing and the whiteboard, saved beside
each other in the epic's ``.context``. Heavy: the spec starts a cdd server of its own, on its own port, from a
throwaway ``~/.cdd``, and works on a throwaway project, so it never reaches the person's server."""
import asyncio
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect  # noqa: E402
from mamba import after, before, context, description, it  # noqa: E402

from harness.mcp.spec_support import SpecServer  # noqa: E402
from space.session.throwaway_project import OPEN_PROJECTS, ThrowawayProject  # noqa: E402

import cdd_guidance.practices  # noqa: E402, F401
from cdd_guidance.practices.ux.model.drawio.nodes import DrawioUxMap  # noqa: E402
from cdd_guidance.practices.ux.model.html.nodes import HtmlUxMap  # noqa: E402
from cdd_guidance.practices.ux.model.nodes import Control, Region, Screen  # noqa: E402
from cdd_guidance.practices.ux.model.ux_map import UxMap  # noqa: E402
from cdd_guidance.practices.ux.model.whiteboard.nodes import WhiteboardUxMap  # noqa: E402

_RENDER = "cdd_guidance.actions.render.render:Render"
_SESSIONS = "space.session.sessions:Sessions"
_CALL_SECONDS = 120
_MOCKUP = "bookshop/buy-a-book.html"
_SCENARIO_LINK = "[Add Book To Cart › Add one book](../story_tests/shop/fill_cart_story.test.md#scenario-add-one-book)"


def mockup_page() -> str:
    """The mockup of Book Details, which serves the story Add Book To Cart, and whose control Quantity serves a
    scenario by a link."""
    ux_map = UxMap.create("Bookshop")
    screen = Screen("Book Details", 0)
    screen.show_story("Add Book To Cart")
    region = Region("Add To Cart", 0)
    quantity = Control("Quantity", 0)
    quantity.control_type = "number"
    quantity.show_scenario(_SCENARIO_LINK)
    region.append_control(quantity)
    screen.append_region(region)
    ux_map.append_screen(screen)
    return HtmlUxMap.create().render(ux_map)


async def _render(server: SpecServer, project: Path, format: str) -> tuple[bool, str]:
    async with server.chat(project, _CALL_SECONDS) as chat:
        arguments = {"guidance": "ux-mockup", "format": format, "paths": [_MOCKUP], "source": "html"}
        result = await chat.call_tool("render.render", arguments=arguments)
        return bool(result.isError), result.content[0].text


def served_by_quantity(ux_map: UxMap) -> list[str]:
    return ux_map.find_screen("Book Details").regions[0].controls[0].scenario_keys


with description("a mockup rendered to its diagram through a cdd server") as self:
    with before.all:
        self.server = SpecServer((_RENDER, _SESSIONS))
        self.server.start()
        self.project = ThrowawayProject()
        (self.project.root / "bookshop").mkdir()
        (self.project.root / _MOCKUP).write_text(mockup_page(), encoding="utf-8")
        self.saved = self.project.root / "bookshop" / ".context"
        self.drawn = asyncio.run(_render(self.server, self.project.root, "drawio"))
        self.boarded = asyncio.run(_render(self.server, self.project.root, "whiteboard"))

    with after.all:
        OPEN_PROJECTS.close_all()
        self.server.stop()

    with context("to drawio"):
        with it("should answer the chat with the drawing saved in the epic's .context"):
            failed, answer = self.drawn
            expect((failed, json.loads(answer)[0]["path"].replace("\\", "/"))).to(equal((False, (self.saved / "buy-a-book.drawio").as_posix())))

        with it("should save a drawing that reads back the scenario a control serves, with its link"):
            drawing = (self.saved / "buy-a-book.drawio").read_text(encoding="utf-8")
            expect(served_by_quantity(DrawioUxMap.create().parse(drawing))).to(equal([_SCENARIO_LINK]))

    with context("to whiteboard"):
        with it("should answer the chat with the board saved beside the drawing"):
            failed, answer = self.boarded
            expect((failed, json.loads(answer)[0]["path"].replace("\\", "/"))).to(equal((False, (self.saved / "buy-a-book.whiteboard").as_posix())))

        with it("should answer the writes that put the board in Claude, the control's card among them"):
            writes = [write for batch in json.loads(self.boarded[1])[0]["batches"] for write in batch]
            expect([write["data"]["text"] for write in writes if write["doc_id"].startswith("control.")]).to(
                equal([f"**Quantity**\n*number*\nScenarios: {_SCENARIO_LINK}"])
            )

        with it("should save a board that reads back the scenario a control serves, with its link"):
            board = (self.saved / "buy-a-book.whiteboard").read_text(encoding="utf-8")
            expect(served_by_quantity(WhiteboardUxMap.create().parse(board))).to(equal([_SCENARIO_LINK]))

        with it("should leave the mockup page as it was"):
            expect((self.project.root / _MOCKUP).read_text(encoding="utf-8")).to(contain("Book Details"))
