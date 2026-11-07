"""BDD spec for MarkdownUxMap - the scope, notes, and invariants channel."""

import sys
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.ux.model.markdown.nodes import MarkdownUxMap
from cdd_guidance.practices.ux.model.ux_map import UxMap


with description("a UX map's context written as markdown"):
    with before.each:
        self.source = UxMap.create(name="notes")
        self.source.scope = "Place New Order"
        self.source.context.notes = ["Keep chrome shared across tabs", "Cart opens from every screen"]
        self.source.context.invariants = ["Tab states are separate screens"]
        self.rendered = MarkdownUxMap.create().render(self.source)

    with it("should write the scope, the invariants, and the notes"):
        expect(self.rendered).to(contain(
            "Scope: Place New Order", "- Tab states are separate screens", "- Keep chrome shared across tabs"
        ))

    with context("that is read back"):
        with before.each:
            self.parsed = MarkdownUxMap.create().parse(self.rendered)

        with it("should read back the scope"):
            expect(self.parsed.scope).to(equal("Place New Order"))

        with it("should read back the notes"):
            expect(self.parsed.context.notes).to(equal(self.source.context.notes))

        with it("should read back the invariants"):
            expect(self.parsed.context.invariants).to(equal(self.source.context.invariants))

    with context("that a person wrote as plain lines"):
        with before.each:
            self.parsed = MarkdownUxMap.create().parse("Cart opens from every screen\n\nTabs share chrome\n")

        with it("should read each line as a note"):
            expect(self.parsed.context.notes).to(equal(["Cart opens from every screen", "Tabs share chrome"]))
