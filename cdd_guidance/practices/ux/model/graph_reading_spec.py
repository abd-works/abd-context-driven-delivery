"""How UX reads the files of a UX map into its graph: a node for each screen, region, control, interaction, and
transition, with edges to the stories a screen shows and the domain terms it names."""

import json
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, equal, expect  # noqa: E402
from mamba import before, context, description, it  # noqa: E402

from harness.graph.graph import Graph  # noqa: E402

import cdd_guidance.practices  # noqa: E402, F401
from cdd_guidance.practices.ux.rules import BY_SLUG  # noqa: E402

_STORY_MAP = "# (E) Sell Books\n## (E) Browse Books\n### (S) Customer --> Browse Book List\n### (S) Customer --> View Book\n"

_DOMAIN_MODEL = (
    "# Domain Model — Bookshop\n\n## Catalog | custom\n\n### Book\n\n"
    "#### Book <<Aggregate Root>> <<Entity>>\n\n------\n+ title: str\n----\n+ rename(title: str): Book\n"
)

_STORY_FILE = "story_tests/sell-books/browse-books/browse_books_story.test.md"
# Each association as a mockup writes it: a markdown link whose target is taken from the folder of the file it is in.
_STORY_LINK = f"[Browse Book List](../{_STORY_FILE}#story-browse-book-list)"
_SCENARIO_LINK = f"[Browse Book List › List every book](../{_STORY_FILE}#scenario-list-every-book)"
_STEP_LINK = f"[Browse Book List › List every book › every book is listed](../{_STORY_FILE}#scenario-list-every-book)"
# The same scenario's name with a target no story file is at, and with the heading of another scenario.
_LINK_TO_NO_FILE = "[Browse Book List › List every book](../story_tests/sell-books/none_story.test.md#scenario-list-every-book)"
_LINK_TO_NO_HEADING = f"[Browse Book List › List every book](../{_STORY_FILE}#scenario-list-no-book)"
# A target written from the project's folder, and one that names the story's file with no heading.
_LINK_FROM_PROJECT = f"[Browse Book List]({_STORY_FILE}#story-browse-book-list)"
_LINK_TO_FILE = f"[Browse Book List › List every book](../{_STORY_FILE})"

_UX_MAP = {
    "name": "Bookshop",
    "scope": "Browse Books",
    "notes": ["A Customer reaches the Cart from every screen."],
    "invariants": [],
    "screens": [
        {
            "name": "Book List",
            "layout": "list",
            "story_names": ["Browse Book List"],
            "domain_terms": ["Book"],
            "regions": [
                {
                    "name": "Books",
                    "area": "body",
                    "controls": [
                        {
                            "name": "Open book",
                            "control_type": "button",
                            "label": "Open",
                            "story_names": [_STORY_LINK],
                            "scenario_names": [_SCENARIO_LINK, _LINK_TO_NO_FILE, _LINK_TO_NO_HEADING],
                            "step_names": [_STEP_LINK],
                            "interactions": [{"name": "open", "trigger": "click", "effect": "shows the book", "destination": "Book Details"}],
                        },
                        {
                            "name": "Titles",
                            "kind": "StoryDemoControl",
                            "control_type": "bound-list",
                            "bound_field": "book.title",
                            "story_steps": [
                                {"kind": "when", "label": "the Customer opens the book list"},
                                {"kind": "then", "label": "a step no story holds"},
                            ],
                        },
                    ],
                }
            ],
        },
        {"name": "Home", "layout": "stack", "story_names": ["View Book", "Wish For Book"], "domain_terms": ["Shelf"], "regions": []},
        {"name": "Book Details", "layout": "stack", "story_names": [_LINK_FROM_PROJECT], "scenario_names": [_LINK_TO_FILE], "regions": []},
    ],
    "transitions": [{"name": "Open book", "from_screen": "Book List", "to_screen": "Book Details", "trigger": "Open book", "nav_type": "action"}],
    "content_types": [{"name": "Book Card", "hierarchy": "Book List > Book"}],
    "nav_components": [{"name": "Main Nav", "ux_type": "top nav", "destinations": ["Book List"]}],
}

_IA_DRAWING = (
    '<mxfile host="drawio-ux"><diagram id="site-map" name="Site Map"><mxGraphModel><root>\n'
    '<mxCell id="0"/><mxCell id="1" parent="0"/>\n'
    '<mxCell id="2" value="Cart" style="rounded=1;" vertex="1" parent="1"><mxGeometry x="40" y="40" width="200" height="48" as="geometry"/></mxCell>\n'
    "</root></mxGraphModel></diagram></mxfile>\n"
)

_STORY_MAP_DRAWING = (
    '<mxfile host="app.diagrams.net"><diagram id="map" name="Story Map"><mxGraphModel><root>\n'
    '<mxCell id="0"/><mxCell id="1" parent="0"/>\n'
    '<mxCell id="2" value="Sell Books" style="rounded=1;" vertex="1" parent="1"><mxGeometry x="40" y="40" width="200" height="48" as="geometry"/></mxCell>\n'
    "</root></mxGraphModel></diagram></mxfile>\n"
)

_SCENARIOS = (
    "# Sub-epic: Browse Books\n\n## Story: Browse Book List\n\n#### Scenario: List every book\n\n"
    "*Given* a Customer\n*When* the Customer opens the book list\n*Then* every book is listed\n"
)

# A mockup's board: the screen Book List, whose region Books holds the control Search, which serves a scenario.
_MOCKUP_BOARD = json.dumps({
    "v": 1, "title": "Browse Books", "order": ["screen.a", "region.body.b", "control.c"],
    "elements": {
        "screen.a": {"type": "container", "text": "Book List", "x": 0, "y": 0, "w": 400, "h": 400},
        "region.body.b": {"type": "container", "text": "Books", "x": 20, "y": 60, "w": 360, "h": 300},
        "control.c": {"type": "shape", "text": f"**Search**\n*text*\nScenarios: {_SCENARIO_LINK}", "x": 40, "y": 120, "w": 300, "h": 80},
    },
}, indent=1)
_BOARD_FILE = "bookshop/browse-books.whiteboard"
# The same board as the mockup fidelity saves it, in the epic's .context, its links still written from the epic's folder.
_SAVED_BOARD_FILE = "bookshop/.context/browse-books.whiteboard"

_BOOK_CODE = "class Book:\n    @property\n    def title(self) -> str:\n        return self._title\n"

_FILES = {
    ".context/story-map.md": _STORY_MAP,
    "story_tests/sell-books/browse-books/browse_books_story.test.md": _SCENARIOS,
    "src/book.py": _BOOK_CODE,
    ".context/domain-model.md": _DOMAIN_MODEL,
    "bookshop/ux-map.json": json.dumps(_UX_MAP, indent=2) + "\n",
    "bookshop/.context/information-architecture.drawio": _IA_DRAWING,
    "bookshop/.context/ux-context.md": "# UX context\n\nScope: Browse Books\n\n## Notes\n- Deferred epic: Review Books.\n",
    "bookshop/.context/story-map.drawio": _STORY_MAP_DRAWING,
    "bookshop/package.json": '{"name": "bookshop"}\n',
    _BOARD_FILE: _MOCKUP_BOARD,
    _SAVED_BOARD_FILE: _MOCKUP_BOARD,
}
_MAP_FILE = "bookshop/ux-map.json"


class Bookshop:
    """The bookshop project in a folder of its own, read into one graph by the practices named."""

    def __init__(self, practices: tuple[str, ...]) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.root = Path(self._folder.name).resolve()
        for relative, text in _FILES.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        self.graph = Graph()
        self.graph.load_working_copy(str(self.root), {key: str(self.root) for key in practices}, force=True)
        self.ux = self.graph.practice("ux").reading.in_graph

    def names(self, node_type: str, file: str = _MAP_FILE) -> list[str]:
        return [node.name for node in self.ux.nodes(node_type) if node.source.file == file]

    def node(self, node_type: str, name: str, file: str = _MAP_FILE):
        return next(node for node in self.ux.nodes(node_type) if node.name == name and node.source.file == file)

    def linked(self, kind: str, node) -> list[tuple[str, str]]:
        """The type and name of each node an edge of kind leads to from node."""
        return [(edge.child.type, edge.child.name) for edge in self.graph.edges.from_parent(kind, node)]

    def hits(self, slug: str) -> list[str]:
        self.ux.rule_run.check()
        return [
            violation.message
            for node in self.ux.nodes()
            for violation in getattr(node.rules.entries.get(slug), "violations", [])
        ]


with description("a UX map read into the graph") as self:
    with context("from a project that holds the map as JSON, its drawing, and its UX context"):
        with before.all:
            self.shop = Bookshop(("ux",))

        with it("should hold a map for each file a UX map is written in"):
            expect(sorted(node.source.file for node in self.shop.ux.nodes("UxMap"))).to(equal([
                _SAVED_BOARD_FILE, "bookshop/.context/information-architecture.drawio", "bookshop/.context/ux-context.md", _BOARD_FILE, _MAP_FILE,
            ]))

        with it("should hold the screen, region and control a mockup's board draws"):
            expect((self.shop.names("Screen", _BOARD_FILE), self.shop.names("Region", _BOARD_FILE), self.shop.names("Control", _BOARD_FILE))).to(
                equal((["Book List"], ["Books"], ["Search"]))
            )

        with it("should keep what a control serves as the file writes it"):
            expect(self.shop.node("Control", "Open book").get_fact("scenario_keys")).to(equal([_SCENARIO_LINK, _LINK_TO_NO_FILE, _LINK_TO_NO_HEADING]))

        with it("should join a control to no scenario while the graph reads no Stories"):
            expect(self.shop.linked("showsScenarios", self.shop.node("Control", "Open book"))).to(equal([]))

        with it("should read no map from a drawing or a JSON file of another kind"):
            files = {node.source.file for node in self.shop.ux.nodes()}
            expect(files & {"bookshop/.context/story-map.drawio", "bookshop/package.json"}).to(equal(set()))

        with it("should hold each screen of the map"):
            expect(self.shop.names("Screen")).to(equal(["Book List", "Home", "Book Details"]))

        with it("should hold the screen a drawing draws"):
            expect(self.shop.names("Screen", "bookshop/.context/information-architecture.drawio")).to(equal(["Cart"]))

        with it("should hold each region, control, and interaction under its screen"):
            expect((self.shop.names("Region"), self.shop.names("Control"), self.shop.names("StoryDemoControl"), self.shop.names("Interaction"))).to(
                equal((["Books"], ["Open book"], ["Titles"], ["open"]))
            )

        with it("should hold each transition, content type, and nav component of the map"):
            expect((self.shop.names("Transition"), self.shop.names("ContentType"), self.shop.names("NavComponent"))).to(
                equal((["Open book"], ["Book Card"], ["Main Nav"]))
            )

        with it("should hold the notes of the UX context file"):
            notes = self.shop.node("UxContext", "context", "bookshop/.context/ux-context.md")
            expect(notes.get_fact("notes")).to(equal(["Deferred epic: Review Books."]))

        with it("should hang each map under the practice"):
            expect(self.shop.linked("owns", self.shop.ux.root)).to(contain(("UxMap", "Bookshop")))

        with it("should hang a region under its screen and a control under its region"):
            screen, region = self.shop.node("Screen", "Book List"), self.shop.node("Region", "Books")
            expect((self.shop.linked("regions", screen), self.shop.linked("controls", region))).to(
                equal(([("Region", "Books")], [("Control", "Open book"), ("StoryDemoControl", "Titles")]))
            )

        with it("should join a transition to the screens it goes from and to"):
            transition = self.shop.node("Transition", "Open book")
            expect((self.shop.linked("from", transition), self.shop.linked("to", transition))).to(
                equal(([("Screen", "Book List")], [("Screen", "Book Details")]))
            )

        with it("should join an interaction to the screen it goes to"):
            expect(self.shop.linked("destination", self.shop.node("Interaction", "open"))).to(equal([("Screen", "Book Details")]))

        with it("should place each screen at the line of its file that names it"):
            lines = (self.shop.root / _MAP_FILE).read_text(encoding="utf-8").splitlines()
            screen = self.shop.node("Screen", "Book Details")
            expect(lines[screen.source.start_line - 1]).to(contain('"name": "Book Details"'))

        with it("should report a screen named with a generic label"):
            expect(self.shop.hits(BY_SLUG["screen-names-use-domain-terms"].slug)).to(
                equal(["Screen 'Home' should use a domain term, not a generic label."])
            )

    with context("from a project whose story map and domain model the graph reads too"):
        with before.all:
            self.shop = Bookshop(("ux", "stories", "ddd", "clean_engineering"))

        with it("should join a screen to each story it shows"):
            expect(self.shop.linked("shows", self.shop.node("Screen", "Book List"))).to(equal([("Story", "Browse Book List")]))

        with it("should join each story to the screens it is shown on"):
            story = next(node for node in self.shop.graph.practice("stories").reading.in_graph.nodes("Story") if node.name == "View Book")
            expect(self.shop.linked("shownOn", story)).to(equal([("Screen", "Home")]))

        with it("should join no screen to a story the story map does not hold"):
            expect(self.shop.linked("shows", self.shop.node("Screen", "Home"))).to(equal([("Story", "View Book")]))

        with it("should join a control to the story its link is written at"):
            expect(self.shop.linked("shows", self.shop.node("Control", "Open book"))).to(equal([("Story", "Browse Book List")]))

        with it("should join a control to the scenario its link is written at, and to none for a link to no file or to no heading"):
            expect(self.shop.linked("showsScenarios", self.shop.node("Control", "Open book"))).to(equal([("Scenario", "List every book")]))

        with it("should join a control to the step with its text under the scenario its link is written at"):
            steps = self.shop.graph.edges.from_parent("showsSteps", self.shop.node("Control", "Open book"))
            expect([(edge.child.type, edge.child.get_fact("text")) for edge in steps]).to(equal([("Then", "every book is listed")]))

        with it("should join each scenario to the controls and screens it is shown on"):
            scenario = next(node for node in self.shop.graph.practice("stories").reading.in_graph.nodes("Scenario") if node.name == "List every book")
            expect(sorted(self.shop.linked("shownOn", scenario))).to(equal([("Control", "Open book"), ("Control", "Search"), ("Control", "Search"), ("Screen", "Book Details")]))

        with it("should join a screen to the story a link written from the project's folder names"):
            expect(self.shop.linked("shows", self.shop.node("Screen", "Book Details"))).to(equal([("Story", "Browse Book List")]))

        with it("should join a screen to the scenario of a linked file that has its key, when the link names no heading"):
            expect(self.shop.linked("showsScenarios", self.shop.node("Screen", "Book Details"))).to(equal([("Scenario", "List every book")]))

        with it("should join a control drawn on a mockup's board to the scenario it serves"):
            expect(self.shop.linked("showsScenarios", self.shop.node("Control", "Search", _BOARD_FILE))).to(equal([("Scenario", "List every book")]))

        with it("should follow a link in a board saved in the epic's .context from the epic's folder, where the mockup it was drawn from wrote it"):
            expect(self.shop.linked("showsScenarios", self.shop.node("Control", "Search", _SAVED_BOARD_FILE))).to(equal([("Scenario", "List every book")]))

        with it("should join a screen to the domain class each of its domain terms names"):
            expect([name for _kind, name in self.shop.linked("domainTerms", self.shop.node("Screen", "Book List"))]).to(equal(["Book"]))

        with it("should join no screen to a domain term no class is named for"):
            expect(self.shop.linked("domainTerms", self.shop.node("Screen", "Home"))).to(equal([]))

        with it("should join a Story Demo control to the story step it runs, of a story its screen shows"):
            steps = self.shop.graph.edges.from_parent("storySteps", self.shop.node("StoryDemoControl", "Titles"))
            expect([(edge.child.type, edge.child.get_fact("text")) for edge in steps]).to(
                equal([("When", "the Customer opens the book list")])
            )

        with it("should join a Story Demo control to the property its bound field names on that property's class"):
            bound = self.shop.graph.edges.from_parent("boundField", self.shop.node("StoryDemoControl", "Titles"))
            expect([(edge.child.get_fact("owner"), edge.child.name) for edge in bound]).to(equal([("Book", "title")]))

    with context("from a project of which only the map's file is read again"):
        with before.all:
            self.shop = Bookshop(("ux", "stories"))
            changed = dict(_UX_MAP, screens=[*_UX_MAP["screens"], {"name": "Cart", "story_names": ["View Book"], "regions": []}])
            (self.shop.root / _MAP_FILE).write_text(json.dumps(changed, indent=2) + "\n", encoding="utf-8")
            self.shop.graph.refresh([_MAP_FILE])

        with it("should hold the screens the file holds now, each once"):
            expect(self.shop.names("Screen")).to(equal(["Book List", "Home", "Book Details", "Cart"]))

        with it("should join the new screen to the story it shows"):
            expect(self.shop.linked("shows", self.shop.node("Screen", "Cart"))).to(equal([("Story", "View Book")]))
