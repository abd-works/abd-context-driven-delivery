"""A project laid out as pml-web is: its story map in tests/.context, one markdown file of scenarios for each story in
tests/story_tests/{sub-epic}/{story}/{story}_story.test.md, and a TypeScript shared story file of the same stories in
the sub-epic's folder beside them. The story tests in code are no map of their own, and a story's own markdown file,
named for it, specifies it: the graph reads each story, scenario and step from the markdown files, as a validate of one
of them reads it, so every scenario graph rule runs on them."""

import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices a graph holds
from harness.graph.graph import Graph
from harness.graph.saved_graph import SavedGraph

_MAP = """\
# Story Map — Paradise Mobile

# (E) Choose Lines
## (S) Customer --> [Display Plans](../story_tests/choose-lines/display-plans/display_plans_story.test.md#story-display-plans)
## (S) Customer --> [Add Line To Cart](../story_tests/choose-lines/add-line-to-cart/add_line_to_cart_story.test.md#story-add-line-to-cart)
"""

_DISPLAY_PLANS = "tests/story_tests/choose-lines/display-plans/display_plans_story.test.md"

_DISPLAY_PLANS_TEXT = """\
---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Display Plans

#### Scenario: See the plan catalog

*Given* the **Customer** has an ++empty cart++
  *And* the ++[plan](../../../../src/.context/domain-model.md#plan)++ repository holds ++Atlas++

```realization
cart = new Cart(null, cart_empty_cart)
```

*When* the **Customer** opens My Paradise

```realization
plans = PlanRepository.list()
```

*Then* the catalog shows ++[plan](../../../../src/.context/domain-model.md#plan)++ ++Atlas++
  *And* the cart shows the ++no lines++ nudge
"""

_ADD_LINE = "tests/story_tests/choose-lines/add-line-to-cart/add_line_to_cart_story.test.md"

_ADD_LINE_TEXT = """\
# Story: Add Line To Cart

#### Scenario: Add a first line

*Given* the **Customer** has an ++empty cart++
*When* the **Customer** adds ++Atlas++
*Then* the cart holds one line
"""

_SHARED = "tests/story_tests/choose-lines/choose_lines.story.shared.ts"

_SHARED_TEXT = """\
import { scenario, shareStory } from 'test-utils/story-test/story-test';

shareStory('Display Plans', () => {
  scenario('See the plan catalog in code', ({ given, when, then }) => {
    given('the Customer has an empty cart', () => {});
    when('the Customer opens My Paradise', () => {});
    then('the catalog shows plan Atlas', () => {});
  });
});

shareStory('Add Line To Cart', () => {
  scenario('Add a first line in code', ({ given, when, then }) => {
    given('the Customer has an empty cart', () => {});
    when('the Customer adds Atlas', () => {});
    then('the cart holds one line', () => {});
  });
});
"""


def _write(root: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text, encoding="utf-8")


def _scenarios(graph: Graph, story: str) -> list[str]:
    stories = graph.practices.named("stories").reading.in_graph
    found = next(node for node in stories.nodes("Story") if node.name == story)
    return [edge.child.name for edge in graph.edges.from_parent("scenarios", found)]


with description("a project's markdown story files beside a shared story file in code, at the scenarios fidelity") as self:
    with before.all:
        self.folder = tempfile.TemporaryDirectory()
        root = Path(self.folder.name)
        _write(root, {"tests/.context/story-map.md": _MAP, _DISPLAY_PLANS: _DISPLAY_PLANS_TEXT, _ADD_LINE: _ADD_LINE_TEXT, _SHARED: _SHARED_TEXT})
        self.graph = Graph()
        stories = self.graph.practices.named("stories")
        stories.fidelities.current = stories.fidelities.entries["scenarios"]
        self.graph.load_working_copy(str(root), {"stories": "."}, force=True)
        checked = root / "checked.json"
        self.graph.reads.refreshed([_DISPLAY_PLANS], checked)
        self.checked = SavedGraph.from_file(checked).practices["stories"]

    with after.all:
        self.folder.cleanup()

    with it("should place each story where the story map puts it, not where the code's folders do"):
        epics = [node.name for node in self.graph.practices.named("stories").reading.in_graph.nodes("Epic")]
        expect(epics).to(equal(["Choose Lines"]))

    with it("should read a story's scenarios from its markdown file"):
        expect(_scenarios(self.graph, "Display Plans")).to(equal(["See the plan catalog"]))

    with it("should read no scenario of a story its markdown file specifies from the code"):
        expect(_scenarios(self.graph, "Add Line To Cart")).not_to(contain("Add a first line in code"))

    with it("should read each step of a scenario from its markdown file"):
        steps = [node.name for node in self.checked.nodes if node.type in ("Given", "When", "Then")]
        expect(steps).to(contain("when the **Customer** opens My Paradise"))

    with it("should give a validate of the markdown file the nodes read from it"):
        files = {node.file for node in self.checked.nodes}
        expect(files).to(contain(_DISPLAY_PLANS))

    with it("should give a validate of the markdown file the scenarios written there, and none of the code's"):
        names = [node.name for node in self.checked.nodes if node.type == "Scenario"]
        expect(names).to(equal(["See the plan catalog"]))
