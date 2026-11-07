"""BDD spec for HtmlUxMap - the mockup shell, and the map it carries read back."""

import sys
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.ux.model.html.nodes import HtmlUxMap, UxMapNotEmbedded
from cdd_guidance.practices.ux.model.ux_map import UxMap
from cdd_guidance.practices.ux.model.ux_map_spec_fixture import OrderingMap, outline


with description("a UX map written as an HTML mockup"):
    with before.each:
        self.source = OrderingMap().build(UxMap.create())
        self.rendered = HtmlUxMap.create().render(self.source)

    with it("should show each screen as an article"):
        expect(self.rendered).to(contain('<article class="screen" data-slug="catalog"'))

    with it("should import the story JavaScript"):
        expect(self.rendered).to(contain('src="stories/place_order.js" data-ux-story-ref'))

    with it("should hold the story outline and the screen stories for the explorer"):
        expect(self.rendered).to(contain('id="story-outline"', 'id="screen-stories"'))

    with it("should mark each region with the layout area it fills"):
        expect(self.rendered).to(contain('data-area="body" data-region="product list"'))

    with it("should escape control labels"):
        expect(self.rendered).to(contain("Browse &lt;all&gt;"))

    with context("that is read back"):
        with before.each:
            self.parsed = HtmlUxMap.create().parse(self.rendered)

        with it("should read back the same map it wrote"):
            expect(outline(self.parsed)).to(equal(outline(self.source)))

        with it("should keep a note that holds a comment end"):
            expect(self.parsed.context.notes).to(equal(["Keep chrome shared across tabs --> always"]))

    with context("that was not rendered from a UX map"):
        with it("should refuse it as HTML with no map embedded"):
            expect(lambda: HtmlUxMap.create().parse("<html><body><h1>Catalog</h1></body></html>")).to(
                raise_error(UxMapNotEmbedded)
            )
