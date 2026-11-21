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


_VIEW = "bookshop/src/CheckoutView.tsx"
_VIEW_MODEL = '''import { useState } from "react";

export function CheckoutView({ cart, onPaid }: CheckoutProps) {
  const [city, setCity] = useState<string>("");

  async function handlePay(): Promise<void> {
    onPaid(city);
  }

  return (
    <main>
      <button onClick={handlePay}>Pay {cart.total}</button>
    </main>
  );
}
'''
_PERSONS_LINE = '    track("paid");'


async def _render_view(server: SpecServer, project: Path) -> tuple[bool, str]:
    async with server.chat(project, _CALL_SECONDS) as chat:
        arguments = {"guidance": "ux-front-end-code", "format": "javascript", "paths": [_VIEW], "source": "typescript"}
        result = await chat.call_tool("render.render", arguments=arguments)
        return bool(result.isError), result.content[0].text


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


with description("a view rendered to JavaScript through a cdd server, onto the JavaScript file a person wrote into") as self:
    with before.all:
        self.server = SpecServer((_RENDER, _SESSIONS))
        self.server.start()
        self.project = ThrowawayProject()
        self.source = self.project.root / _VIEW
        self.source.parent.mkdir(parents=True)
        self.source.write_text(_VIEW_MODEL, encoding="utf-8")
        self.first = asyncio.run(_render_view(self.server, self.project.root))
        self.file = self.source.with_suffix(".jsx")
        self.file.write_text(self.file.read_text(encoding="utf-8").replace("    onPaid(city);", f"{_PERSONS_LINE}\n    onPaid(city);"), encoding="utf-8")
        # The model gains the handler handleClear, and its handler handlePay is renamed handleCheckout.
        changed = _VIEW_MODEL.replace("handlePay", "handleCheckout").replace("  return (", '  function handleClear(): void {\n    setCity("");\n  }\n\n  return (')
        self.source.write_text(changed, encoding="utf-8")
        self.failed, self.answer = asyncio.run(_render_view(self.server, self.project.root))
        self.text = self.file.read_text(encoding="utf-8")
        self.again = asyncio.run(_render_view(self.server, self.project.root))

    with after.all:
        OPEN_PROJECTS.close_all()
        self.server.stop()

    with it("should have saved the view beside its source the first time"):
        expect((self.first[0], json.loads(self.first[1])[0]["paths"][0].replace("\\", "/"))).to(equal((False, self.file.as_posix())))

    with it("should keep the line the person wrote in the handler the model renamed"):
        expect(self.text).to(contain(f"  async function handlePay() {{\n{_PERSONS_LINE}\n    onPaid(city);"))

    with it("should mark that handler as no longer in the model"):
        expect(self.text).to(contain("no longer in the model: CheckoutView.handlePay"))

    with it("should write each handler the model gained empty, before what the component returns"):
        expect(self.text).to(contain("  async function handleCheckout() {}\n\n  function handleClear() {}\n\n  return ("))

    with it("should answer what to migrate: the kept handler, and the added ones that may have replaced it"):
        migrate = json.loads(self.answer)[0]["migrate"]
        expect([(entry["kept"], entry["may_have_replaced_it"]) for entry in migrate]).to(
            equal([("CheckoutView.handlePay", ["CheckoutView.handleCheckout", "CheckoutView.handleClear"])])
        )

    with it("should change nothing when the same view is rendered again"):
        expect((self.again[0], self.file.read_text(encoding="utf-8"))).to(equal((False, self.text)))
