"""What the Render action answers for one guidance, written as the fields an agent reads."""
from pathlib import Path

from expects import contain, equal, expect
from mamba import context, description, it

from cdd_guidance.actions.render.render_result import (
    AnsweredContent,
    KeptMember,
    SavedBoard,
    SavedCode,
    SavedFile,
    SignatureDiffers,
)
from cdd_guidance.actions.render.render_result import DECIDE_EACH
from harness.guidance.practice_formats import Rendered
from harness.installation.data_class import data_of
from harness.markdown.format import Format

_FILE = Path("docs/story-map.drawio")


with description("a render's result") as self:
    with it("should answer a render it saved nothing of with its format and content"):
        expect(data_of(AnsweredContent(Rendered(Format("json"), "{}")))).to(equal({"format": "json", "content": "{}"}))

    with it("should answer a drawing it saved with the file, and the cell only the drawing held"):
        result = SavedFile(Rendered(Format("drawio"), "<mxfile/>"), _FILE, [KeptMember(_FILE, "person-note 'Ask Dana'", ["order 'Order'"])])
        expect(data_of(result)).to(equal({
            "format": "drawio",
            "path": str(_FILE),
            "migrate": [{"file": str(_FILE), "kept": "person-note 'Ask Dana'", "may_have_replaced_it": ["order 'Order'"]}],
            "decide": DECIDE_EACH,
        }))

    with it("should answer a whiteboard it saved with its board and the writes that put it there"):
        result = SavedBoard(Rendered(Format("whiteboard"), "{}"), Path("map.whiteboard"), [], "https://claude.ai/artifact/Board", [[{"doc_id": "meta"}]])
        expect(sorted(data_of(result))).to(equal(["batches", "board", "decide", "format", "migrate", "path", "publish"]))

    with it("should answer code it saved with each file, and each member waiting to be moved"):
        migrate = [KeptMember(Path("cart.py"), "Cart.total", ["Cart.subtotal"]), SignatureDiffers(Path("cart.py"), "Cart.add", "def add(self, book):")]
        result = SavedCode(Rendered(Format("python"), "class Cart: ..."), [Path("cart.py")], migrate)
        expect(data_of(result)).to(equal({
            "format": "python",
            "paths": ["cart.py"],
            "migrate": [
                {"file": "cart.py", "kept": "Cart.total", "may_have_replaced_it": ["Cart.subtotal"]},
                {"file": "cart.py", "signature_differs": "Cart.add", "model_has": "def add(self, book):"},
            ],
            "decide": DECIDE_EACH,
        }))

    with it("should name the files it saved"):
        expect(SavedCode(Rendered(Format("python"), ""), [Path("a.py"), Path("b.py")], []).saved).to(equal([Path("a.py"), Path("b.py")]))

    with it("should name the member each migration is about"):
        expect([KeptMember(_FILE, "Cart").member, SignatureDiffers(_FILE, "Cart.add", "x").member]).to(equal(["Cart", "Cart.add"]))

    # The person's ruling, 2026-11-22: what the source no longer holds is handed to an AI pass that decides by reading;
    # no rule tells what a render drew from what a person added, and who added or removed it plays no part.
    with it("should hand nothing to decide when it kept nothing"):
        expect(SavedFile(Rendered(Format("drawio"), "<mxfile/>"), _FILE, []).decide).to(equal(""))

    with context("that kept something the source no longer holds"):
        with it("should tell the agent to go through each entry and decide by reading it against what the source now holds"):
            expect(DECIDE_EACH).to(contain("Go through every entry of migrate", "decide by reading", "against what the source now holds"))

        with it("should name the four ways an entry can go"):
            expect(DECIDE_EACH).to(contain(
                "moved somewhere, so move it there and take the leftover out",
                "merged into something else, so fold it in and take the leftover out",
                "no longer needed, so remove it",
                "still wanted and the source is behind, so put it back in the source",
            ))

        with it("should say that who added or removed it plays no part"):
            expect(DECIDE_EACH).to(contain("who added it or who removed it plays no part"))

        with it("should say to ask the person where reading cannot tell"):
            expect(DECIDE_EACH).to(contain("ask the person"))

        with it("should say the entry stays where it is until it is decided"):
            expect(DECIDE_EACH).to(contain("Until you have decided an entry, it stays where it is"))
