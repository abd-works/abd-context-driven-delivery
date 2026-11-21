"""Specs for a document or a drawing rendered onto one that is already there: what only the file held stays in it. The
Render action that calls it is in render_spec.py; the same rule for code is in reshaped_code_spec.py."""
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.actions.render.kept_document import KeptDocument
from harness.markdown.format import Format

NOTE = "Ask Dana before changing this"
MODEL = "# Domain Model\n\n## Cart\n\nA cart holds lines.\n"
MODEL_WITH_NOTES = f"# Domain Model\n\n## Cart\n\nA cart holds lines.\n\n{NOTE}.\n\n## Open questions\n\n- Who owns returns?\n"


def _drawing(cart_x: str, *more: str) -> str:
    cart = f'<mxCell id="cart" value="Cart" vertex="1" parent="1"><mxGeometry x="{cart_x}" y="40" width="120" height="60" as="geometry" /></mxCell>'
    return f'<mxfile><diagram name="Model" id="model"><mxGraphModel><root><mxCell id="0" /><mxCell id="1" parent="0" />{cart}{"".join(more)}</root></mxGraphModel></diagram></mxfile>'


def _drawing_of(*cells: str) -> str:
    return f'<mxfile><diagram name="Model" id="model"><mxGraphModel><root><mxCell id="0" /><mxCell id="1" parent="0" />{"".join(cells)}</root></mxGraphModel></diagram></mxfile>'


ARROW_CELL = '<mxCell id="person-arrow" style="endArrow=classic;" edge="1" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>'
NOTE_CELL = f'<mxCell id="person-note" value="{NOTE}" style="text;html=1;" vertex="1" parent="1"><mxGeometry x="900" y="900" width="200" height="40" as="geometry" /></mxCell>'
ORDER_CELL = '<mxCell id="order" value="Order" vertex="1" parent="1"><mxGeometry x="200" y="40" width="120" height="60" as="geometry" /></mxCell>'


def _board(cart_x: int, **more: dict) -> str:
    elements = {"cart": {"type": "shape", "text": "Cart", "x": cart_x, "y": 40, "w": 120, "h": 60}, **more}
    return json.dumps({"v": 1, "title": "Model", "order": list(elements), "elements": elements})


NOTE_ELEMENT = {"type": "text", "text": NOTE, "x": 900, "y": 900, "w": 200, "h": 40}

with description("a document rendered onto one that is already there") as self:
    with context("in markdown, whose file holds a line and a section the render does not write"):
        with before.each:
            self.kept = KeptDocument(Format("markdown")).onto(MODEL_WITH_NOTES, MODEL)

        with it("should write the rendered document first, as rendered"):
            expect(self.kept.text.startswith(MODEL)).to(equal(True))

        with it("should keep the file's own lines below it, under a heading saying they are no longer in the model"):
            below = self.kept.text[len(MODEL):]
            expect(below).to(contain("no longer in the model", f"{NOTE}.", "## Open questions", "- Who owns returns?"))

        with it("should name how many lines wait to be placed"):
            expect(self.kept.kept).to(equal(["3 line(s) set apart"]))

        with context("rendered a second time"):
            with it("should change nothing"):
                expect(KeptDocument(Format("markdown")).onto(self.kept.text, MODEL).text).to(equal(self.kept.text))

    with context("in markdown, whose file holds nothing the render does not write"):
        with it("should write the rendered document as rendered, with nothing kept"):
            kept = KeptDocument(Format("markdown")).onto(MODEL, MODEL_WITH_NOTES)
            expect((kept.text, kept.kept)).to(equal((MODEL_WITH_NOTES, [])))

    with context("as a draw.io drawing, whose file holds a note a person added and a card they moved"):
        with before.each:
            self.kept = KeptDocument(Format("drawio")).onto(_drawing("7777", NOTE_CELL), _drawing("20", ORDER_CELL))

        with it("should keep the note in the drawing"):
            expect(self.kept.text).to(contain('id="person-note"', NOTE))

        with it("should keep the card where the person moved it"):
            expect(self.kept.text).to(contain('x="7777"'))

        with it("should hold the card the render added"):
            expect(self.kept.text).to(contain('id="order"'))

        with it("should name the note as kept, by its id and what it says"):
            expect(self.kept.kept).to(equal([f"person-note '{NOTE}'"]))

        with context("rendered a second time"):
            with it("should change nothing"):
                twice = KeptDocument(Format("drawio")).onto(self.kept.text, _drawing("20", ORDER_CELL))
                expect(twice.text).to(equal(self.kept.text))

    with context("as a draw.io drawing, whose file holds nothing the render does not draw, where the render drew it"):
        with it("should write the drawing exactly as rendered"):
            rendered = _drawing("20", ORDER_CELL)
            expect(KeptDocument(Format("drawio")).onto(_drawing("20"), rendered).text).to(equal(rendered))

    with context("as a draw.io drawing whose file holds only a note a person wrote, and none of the render's cells"):
        with before.each:
            self.kept = KeptDocument(Format("drawio")).onto(_drawing_of(NOTE_CELL), _drawing("20", ORDER_CELL))

        with it("should keep the note, since a cell the render does not draw is the person's"):
            expect(self.kept.text).to(contain('id="person-note"', 'id="cart"', 'id="order"'))

        with it("should name the note as kept"):
            expect(self.kept.kept).to(equal([f"person-note '{NOTE}'"]))

    with context("as a draw.io drawing rendered by a format that names its cells anew, whose file holds a note a person wrote"):
        with before.each:
            self.rendered = _drawing("20", ORDER_CELL).replace('id="cart"', 'id="cart-2"').replace('id="order"', 'id="order-2"')
            self.kept = KeptDocument(Format("drawio")).onto(_drawing("7777", ORDER_CELL, NOTE_CELL), self.rendered)

        with it("should keep the note"):
            expect(self.kept.kept).to(equal([f"person-note '{NOTE}'"]))

        with it("should not draw a second time the cards the render drew under other names"):
            expect((self.kept.text.count('value="Cart"'), self.kept.text.count('value="Order"'))).to(equal((1, 1)))

    with context("as a draw.io drawing whose file holds an arrow with no words on it, which the render does not draw"):
        with it("should keep the arrow when the render drew the file's other cells under the names the file gives them"):
            kept = KeptDocument(Format("drawio")).onto(_drawing("20", ARROW_CELL), _drawing("20", ORDER_CELL))
            expect(kept.kept).to(equal(["person-arrow ''"]))

        with it("should leave the arrow out when the render named every cell anew, since it is then the format's own earlier arrow"):
            rendered = _drawing("20").replace('id="cart"', 'id="cart-2"')
            expect(KeptDocument(Format("drawio")).onto(_drawing("20", ARROW_CELL), rendered).kept).to(equal([]))

    with context("as a whiteboard whose file holds only a note a person wrote, and none of the render's elements"):
        with it("should keep the note"):
            only_note = json.dumps({"v": 1, "title": "Model", "order": ["note"], "elements": {"note": NOTE_ELEMENT}})
            expect(KeptDocument(Format("whiteboard")).onto(only_note, _board(20)).kept).to(equal([f"note '{NOTE}'"]))

    with context("as a whiteboard, whose file holds a note a person added and a card they moved"):
        with before.each:
            self.kept = KeptDocument(Format("whiteboard")).onto(_board(7777, note=NOTE_ELEMENT), _board(20, order={"type": "shape", "text": "Order", "x": 200, "y": 40, "w": 120, "h": 60}))
            self.board = json.loads(self.kept.text)

        with it("should keep the note on the board, drawn after what the render drew"):
            expect((self.board["elements"]["note"], self.board["order"])).to(equal((NOTE_ELEMENT, ["cart", "order", "note"])))

        with it("should keep the card where the person moved it"):
            expect(self.board["elements"]["cart"]["x"]).to(equal(7777))

        with it("should name the note as kept, by its id and what it says"):
            expect(self.kept.kept).to(equal([f"note '{NOTE}'"]))

    with context("as a whiteboard, whose file holds nothing the render does not draw, where the render drew it"):
        with it("should write the board exactly as rendered"):
            rendered = _board(20, order={"type": "shape", "text": "Order", "x": 200, "y": 40, "w": 120, "h": 60})
            expect(KeptDocument(Format("whiteboard")).onto(_board(20), rendered).text).to(equal(rendered))
