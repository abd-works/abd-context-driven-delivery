"""What the Render action answers for one guidance, written as the fields an agent reads."""
from pathlib import Path

from expects import equal, expect
from mamba import description, it

from cdd_guidance.actions.render.render_result import (
    AnsweredContent,
    KeptCodeMember,
    KeptMember,
    SavedBoard,
    SavedCode,
    SavedFile,
    SignatureDiffers,
)
from harness.guidance.practice_formats import Rendered
from harness.installation.data_class import data_of
from harness.markdown.format import Format

_FILE = Path("docs/story-map.drawio")


with description("a render's result") as self:
    with it("should answer a render it saved nothing of with its format and content"):
        expect(data_of(AnsweredContent(Rendered(Format("json"), "{}")))).to(equal({"format": "json", "content": "{}"}))

    with it("should answer a drawing it saved with the file, and the cell only the drawing held"):
        result = SavedFile(Rendered(Format("drawio"), "<mxfile/>"), _FILE, [KeptMember(_FILE, "person-note 'Ask Dana'")])
        expect(data_of(result)).to(equal({"format": "drawio", "path": str(_FILE), "migrate": [{"file": str(_FILE), "kept": "person-note 'Ask Dana'"}]}))

    with it("should answer a whiteboard it saved with its board and the writes that put it there"):
        result = SavedBoard(Rendered(Format("whiteboard"), "{}"), Path("map.whiteboard"), [], "https://claude.ai/artifact/Board", [[{"doc_id": "meta"}]])
        expect(sorted(data_of(result))).to(equal(["batches", "board", "format", "migrate", "path"]))

    with it("should answer code it saved with each file, and each member waiting to be moved"):
        migrate = [KeptCodeMember(Path("cart.py"), "Cart.total", ["Cart.subtotal"]), SignatureDiffers(Path("cart.py"), "Cart.add", "def add(self, book):")]
        result = SavedCode(Rendered(Format("python"), "class Cart: ..."), [Path("cart.py")], migrate)
        expect(data_of(result)).to(equal({
            "format": "python",
            "paths": ["cart.py"],
            "migrate": [
                {"file": "cart.py", "kept": "Cart.total", "may_have_replaced_it": ["Cart.subtotal"]},
                {"file": "cart.py", "signature_differs": "Cart.add", "model_has": "def add(self, book):"},
            ],
        }))

    with it("should name the files it saved"):
        expect(SavedCode(Rendered(Format("python"), ""), [Path("a.py"), Path("b.py")], []).saved).to(equal([Path("a.py"), Path("b.py")]))

    with it("should name the member each migration is about"):
        expect([KeptMember(_FILE, "Cart").member, SignatureDiffers(_FILE, "Cart.add", "x").member]).to(equal(["Cart", "Cart.add"]))
