"""BDD spec for HtmlUxMap - the mockup shell, and the map it carries read back."""

import json
import re
import sys
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryModel
from cdd_guidance.practices.ux.model.html.nodes import HtmlUxMap, UxMapNotEmbedded
from cdd_guidance.practices.ux.model.ux_map import UxMap
from cdd_guidance.practices.ux.model.ux_map_spec_fixture import OrderingMap, outline


def story_outline_in(page):
    return json.loads(re.search(r'<script id="story-outline" type="application/json">(.*?)</script>', page).group(1))


def ordering_story_map(graph):
    story_map = StoryModel(graph=graph)
    epic = Epic("Place New Order", 0)
    browse = Epic("Browse", 0)
    browse.append_story(Story("Browse Product Catalog", 0))
    epic.append_epic(browse)
    epic.append_story(Story("Check Out", 1))
    story_map.append_epic(epic)
    return story_map


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

    with it("should leave the story outline empty while no story map is on the map's graph"):
        expect(story_outline_in(self.rendered)).to(equal([]))

    with context("with the story map on the map's graph"):
        with before.each:
            from harness.graph.graph import Graph

            self.source = OrderingMap().build(UxMap.create(Graph()))
            ordering_story_map(self.source.graph)
            self.source.find_screen("Cart").show_story("Check Out")
            self.rendered = HtmlUxMap.create().render(self.source)

        with it("should outline each epic with the sub-epics and stories its screens show"):
            expect(story_outline_in(self.rendered)).to(equal([{
                "name": "Place New Order",
                "groups": [{"name": "Browse", "stories": ["Browse Product Catalog"]}],
                "stories": ["Check Out"],
            }]))

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
