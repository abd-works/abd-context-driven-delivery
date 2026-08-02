"""BDD spec for MarkdownUxMap - notes and invariants channel."""

import sys
from pathlib import Path

from expects import equal, expect
from mamba import before, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from context_tools.ux.document.markdown.nodes import MarkdownUxMap
from context_tools.ux.ux_model.ux_map import UxMap


with description("MarkdownUxMap"):
    with before.each:
        self.source = UxMap(name="notes")
        self.source.scope = "Place New Order"
        self.source.context.notes = ["Keep chrome shared across tabs"]
        self.source.context.invariants = ["Tab states are separate screens"]
        self.rendered = MarkdownUxMap.render(self.source)
        self.parsed = MarkdownUxMap.parse(self.rendered)

    with it("should render scope and notes into markdown"):
        expect("Place New Order" in self.rendered).to(equal(True))
        expect("Keep chrome shared across tabs" in self.rendered).to(equal(True))
        expect("Tab states are separate screens" in self.rendered).to(equal(True))

    with it("should parse non-empty lines into context notes"):
        expect("Scope: Place New Order" in self.parsed.context.notes).to(equal(True))
        expect(
            "- Keep chrome shared across tabs" in self.parsed.context.notes
            or "Keep chrome shared across tabs" in self.parsed.context.notes
        ).to(equal(True))
