"""BDD spec for HtmlUxMap - the mockup shell, and the map it carries read back."""

import json
import re
import sys
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

_REPO = Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.stories.model.story_model import Epic, Scenario, Step, StepType, Story, StoryModel
from cdd_guidance.practices.ux.model.html.nodes import HtmlUxMap, UxMapNotEmbedded
from cdd_guidance.practices.ux.model.ux_map import UxMap
from cdd_guidance.practices.ux.model.ux_map_spec_fixture import OrderingMap, outline


def explorer_tree_in(page):
    return json.loads(re.search(r'<script id="story-explorer-tree" type="application/json">(.*?)</script>', page).group(1))


_STORY_TESTS = _REPO / "cdd_guidance/practices/stories/model/_examples/actual/from-typescript/to-typescript/tests/onboard-a-customer/create-customer"


def render_showing_first_story(graph):
    """The ordering map on graph, its Cart screen showing the first story the graph's Stories holds, as HTML."""
    story = graph.practice("stories").reading.in_graph.nodes("Story")[0]
    ux_map = OrderingMap().build(UxMap.create(graph))
    ux_map.find_screen("Cart").show_story(story.name)
    return HtmlUxMap.create().render(ux_map)


def ordering_story_map(graph):
    story_map = StoryModel(graph=graph)
    epic = Epic("Place New Order", 0)
    browse = Epic("Browse", 0)
    browse.append_story(Story("Browse Product Catalog", 0))
    epic.append_epic(browse)
    check_out = Story("Check Out", 1)
    pay = Scenario("pay with a saved card", 0)
    pay.steps.append(Step("a saved card", StepType.GIVEN, 0))
    pay.steps.append(Step("the customer pays", StepType.WHEN, 1))
    check_out.scenarios.append(pay)
    epic.append_story(check_out)
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

    with it("should hold the explorer tree for the story explorer to draw"):
        expect(self.rendered).to(contain('<script id="story-explorer-tree" type="application/json">'))

    with it("should mark each region with the layout area it fills"):
        expect(self.rendered).to(contain('data-area="body" data-region="product list"'))

    with it("should escape control labels"):
        expect(self.rendered).to(contain("Browse &lt;all&gt;"))

    with it("should list the screens flat, each with the stories it names, while no story map is on the map's graph"):
        expect(explorer_tree_in(self.rendered)["nodes"]).to(equal([
            {"kind": "screen", "name": "catalog", "key": "screen:catalog", "children": [
                {"kind": "story", "name": "Browse Product Catalog", "screenName": "catalog",
                 "key": "story:catalog/Browse Product Catalog", "children": []},
            ]},
            {"kind": "screen", "name": "cart", "key": "screen:cart", "children": []},
            {"kind": "screen", "name": "cart-saved", "key": "screen:cart-saved", "children": []},
        ]))

    with it("should name the keys that open each screen"):
        expect(explorer_tree_in(self.rendered)["screenKeys"]["catalog"]).to(equal(["screen:catalog"]))

    with context("with the story map on the map's graph"):
        with before.each:
            from harness.graph.graph import Graph

            self.source = OrderingMap().build(UxMap.create(Graph()))
            ordering_story_map(self.source.graph)
            self.source.find_screen("Cart").show_story("Check Out")
            self.rendered = HtmlUxMap.create().render(self.source)

        with it("should place each screen under the epic and sub-epic of the stories it shows"):
            epic = explorer_tree_in(self.rendered)["nodes"][0]
            expect([(epic["key"], [(child["kind"], child["key"]) for child in epic["children"]])]).to(equal([(
                "epic:Place New Order",
                [("subepic", "subepic:Place New Order/Browse"), ("screen", "screen:Place New Order//cart")],
            )]))

        with it("should place a screen under a sub-epic by the stories it shows there"):
            browse = explorer_tree_in(self.rendered)["nodes"][0]["children"][0]
            expect([child["key"] for child in browse["children"]]).to(equal(["screen:Place New Order/Browse/catalog"]))

        with it("should hold each story's scenarios, each with its steps"):
            cart = explorer_tree_in(self.rendered)["nodes"][0]["children"][1]
            expect(cart["children"][0]["children"]).to(equal([{
                "kind": "scenario", "name": "pay with a saved card", "screenName": "cart",
                "key": "scenario:cart/Check Out/pay with a saved card", "storyName": "Check Out", "scenarioIndex": 0,
                "children": [
                    {"kind": "step", "screenName": "cart", "stepKind": "given", "label": "a saved card", "domainTerms": [],
                     "storyName": "Check Out", "scenarioIndex": 0, "scenarioKey": "scenario:cart/Check Out/pay with a saved card"},
                    {"kind": "step", "screenName": "cart", "stepKind": "when", "label": "the customer pays", "domainTerms": [],
                     "storyName": "Check Out", "scenarioIndex": 0, "scenarioKey": "scenario:cart/Check Out/pay with a saved card"},
                ],
            }]))

        with it("should name the keys that open a screen: its epic, its sub-epic, and itself"):
            expect(explorer_tree_in(self.rendered)["screenKeys"]["catalog"]).to(equal(
                ["epic:Place New Order", "subepic:Place New Order/Browse", "screen:Place New Order/Browse/catalog"]
            ))

        with it("should leave a screen that shows no story on the map off the tree"):
            expect("cart-saved" in explorer_tree_in(self.rendered)["screenKeys"]).to(equal(False))

        # Which words are the domain's terms is the model's to say; the page only marks the terms it is given.
        with context("whose screen names its domain terms"):
            with before.each:
                self.source.find_screen("Cart").attach_domain_term("saved card")
                self.rendered = HtmlUxMap.create().render(self.source)

            with it("should give each step the domain terms of the screen it is on"):
                cart = explorer_tree_in(self.rendered)["nodes"][0]["children"][1]
                steps = cart["children"][0]["children"][0]["children"]
                expect([step["domainTerms"] for step in steps]).to(equal([["saved card"], ["saved card"]]))

            with it("should leave no list of one project's nouns in the explorer's script"):
                script = (_REPO / "cdd_guidance/practices/ux/story-demo/screen-tree.js").read_text(encoding="utf-8")
                expect("Mavenir" in script).to(equal(False))

    # A graph opened from its save holds Stories' nodes as plain nodes, with only their saved facts and edges.
    with context("with a story map read from story tests, on a graph opened again from its save"):
        with before.all:
            import shutil
            import tempfile

            from harness.graph.graph import Graph

            self.working_copy = Path(tempfile.mkdtemp())
            shutil.copytree(_STORY_TESTS, self.working_copy / "tests" / "onboard-a-customer" / "create-customer")
            fresh = Graph()
            fresh.load_working_copy(str(self.working_copy), {"stories": "."})
            fresh.save_json()
            reopened = Graph()
            reopened.open_saved(self.working_copy)
            self.fresh_tree = explorer_tree_in(render_showing_first_story(fresh))
            self.reopened_tree = explorer_tree_in(render_showing_first_story(reopened))

        with after.all:
            import shutil

            shutil.rmtree(self.working_copy, ignore_errors=True)

        with it("should place the screen under the epic of the story it shows"):
            expect([node["key"] for node in self.reopened_tree["nodes"]]).to(equal(["epic:Onboard A Customer"]))

        with it("should write the explorer tree a fresh build of the graph writes"):
            expect(self.reopened_tree).to(equal(self.fresh_tree))

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
