"""MarkdownBoundedContextMap — a map written from templates/bounded-context.md, read as the drawn formats (draw.io,
whiteboard) draw it: the template's own explanation is no context, a member keeps every word its line holds, and the
map keeps the name its heading gives it."""

from xml.etree import ElementTree as ET

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.ddd.model.drawio.drawio_bounded_context_map import DrawIOBoundedContextMap
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap
from cdd_guidance.practices.ddd.model.whiteboard.whiteboard_bounded_context_map import WhiteboardBoundedContextMap

# A map as the template writes it: the title it names, its Map format explanation, then its contexts.
_TITLE = "Bounded Context Map — ASL Call Translator"
_MAP = f"""<!--
  Bounded context map. A context is a module of aggregates.
-->

# {_TITLE}

## Map format

`##` is a bounded context; the text after `|` is the owner. `###` is an aggregate; its first line is the root, indented lines are members.

## Translated Call | custom

The language of one call.

### Translated Call

Translated Call - one call between a Deaf User and a Hearing Caller
  Hearing Caller
  Call Direction (outbound | inbound)
  Call State (dialing | ringing | answered | ended | dropped)

Integrations:
  - → Telephony · Call (by CallSid)
    pattern: Anticorruption Layer

## Telephony | CPaaS vendor

### Call

Call - a phone-network call bridged to the app
  Call Leg
"""


def _title_cell(xml: str) -> str:
    return next(cell.get("value") for cell in ET.fromstring(xml).iter("mxCell") if cell.get("id") == "title")


with description("a bounded context map written from the template"):
    with before.all:
        self.read = MarkdownBoundedContextMap().parse(_MAP)

    with it("should read only the contexts it draws, not its Map format explanation"):
        expect([each.name for each in self.read.contexts]).to(equal(["Translated Call", "Telephony"]))

    with it("should keep each member whole, the choices after a | included"):
        expect(self.read.contexts[0].aggregates[0].drawn_members).to(equal([
            "Hearing Caller",
            "Call Direction (outbound | inbound)",
            "Call State (dialing | ringing | answered | ended | dropped)",
        ]))

    with it("should keep the name its heading gives the map"):
        expect(self.read.title).to(equal(_TITLE))

    with context("drawn in draw.io"):
        with before.all:
            self.xml = DrawIOBoundedContextMap().render(MarkdownBoundedContextMap().parse(_MAP))

        with it("should title the drawing with the map's own heading"):
            expect(_title_cell(self.xml)).to(equal(_TITLE))

        with it("should list each member whole on its aggregate"):
            expect(self.xml).to(contain("Call State (dialing | ringing | answered | ended | dropped)"))

        with it("should draw no context for the Map format explanation"):
            expect("map-format" in self.xml.lower()).to(equal(False))

        with it("should read the title back from the drawing"):
            expect(DrawIOBoundedContextMap().parse(self.xml).title).to(equal(_TITLE))

    with context("drawn on a whiteboard"):
        with before.all:
            self.board = WhiteboardBoundedContextMap().render(MarkdownBoundedContextMap().parse(_MAP))

        with it("should title the board with the map's own heading"):
            expect((_TITLE in self.board, "Modules Context" in self.board)).to(equal((True, False)))

        with it("should list each member whole on its aggregate"):
            expect(self.board).to(contain("Call Direction (outbound | inbound)"))

        with it("should draw no context for the Map format explanation"):
            expect("Map format" in self.board).to(equal(False))
