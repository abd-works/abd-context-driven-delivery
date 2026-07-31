"""BDD spec - Epics that declare ExampleFactories emit factory links in helpers and markdown."""

import sys
from pathlib import Path

from expects import contain, equal, expect, have_len
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from context_tools.stories.code.example_factories import collect_example_factories
from context_tools.stories.code.javascript.tree import render_js_tree
from context_tools.stories.code.python.python_story_map import PythonStoryMap
from context_tools.stories.document.markdown.example_factories import (
    parse_md_factory_line,
    render_md_factory_line,
)
from context_tools.stories.document.markdown.nodes import MarkdownStoryMap
from context_tools.stories.story_model.nodes import Epic, Story, SubEpic
from context_tools.stories.story_model.scenario import Scenario
from context_tools.stories.story_model.story_map import StoryMap


def _map_with_factory() -> StoryMap:
    story_map = StoryMap()
    epic = Epic("Connect Story Examples", 1)
    epic.example_factories = ["CartExampleFactory"]
    sub = SubEpic("Generate Stories That Import Factories", 1)
    story = Story("Generate Epic That Imports Factories", 1)
    story.scenarios.append(
        Scenario(name="epic helper imports factories", sequential_order=1)
    )
    sub.stories.append(story)
    epic.sub_epics.append(sub)
    story_map.epics.append(epic)
    return story_map


with description("an Epic that declares example factories") as self:
    with context("that names CartExampleFactory"):
        with before.each:
            self.epic = Epic("Connect Story Examples", 1)
            self.epic.example_factories = ["CartExampleFactory"]

        with it("should collect CartExampleFactory"):
            expect(collect_example_factories(self.epic)).to(
                equal(["CartExampleFactory"])
            )

    with context("that names a bare type Cart"):
        with before.each:
            self.epic = Epic("Connect Story Examples", 1)
            self.epic.example_factories = ["Cart"]

        with it("should collect CartExampleFactory"):
            expect(collect_example_factories(self.epic)).to(
                equal(["CartExampleFactory"])
            )


with description("a Python epic helper") as self:
    with context("for an Epic that declares CartExampleFactory"):
        with before.each:
            tree = PythonStoryMap().render(_map_with_factory())
            helper_paths = [p for p in tree if p.endswith("_helper.py")]
            self.helper = tree[helper_paths[0]]

        with it("should import CartExampleFactory"):
            expect(self.helper).to(
                contain("from example_factories import CartExampleFactory")
            )

        with it("should expose a cart_example_factory accessor"):
            expect(self.helper).to(contain("def cart_example_factory(self)"))

        with it(
            "should instruct helpers to use ExampleFactory fake mode (not Fake subclasses)"
        ):
            expect(self.helper).to(contain("fake mode"))


with description("a JavaScript epic helper") as self:
    with context("for an Epic that declares CartExampleFactory"):
        with before.each:
            tree = render_js_tree(_map_with_factory(), include_shared=False)
            helper_paths = [p for p in tree if p.endswith("-helper.js")]
            expect(helper_paths).to(have_len(1))
            self.helper = tree[helper_paths[0]]

        with it("should import CartExampleFactory"):
            expect(self.helper).to(contain("import { CartExampleFactory }"))

        with it("should expose a ConnectStoryExamplesHelper with cartExampleFactory"):
            expect(self.helper).to(contain("export class ConnectStoryExamplesHelper"))
            expect(self.helper).to(contain("cartExampleFactory()"))


with description("a Markdown Story Map") as self:
    with context("that holds an Epic declaring CartExampleFactory"):
        with before.each:
            self.md = MarkdownStoryMap().render(_map_with_factory())

        with it("should list CartExampleFactory on an Example factories line"):
            expect(self.md).to(
                contain(render_md_factory_line(["CartExampleFactory"]))
            )

        with it("should restore CartExampleFactory on the Epic when parsed"):
            parsed = MarkdownStoryMap().parse(self.md)
            expect(parsed.epics[0].example_factories).to(
                equal(["CartExampleFactory"])
            )


with description("an Example factories markdown line") as self:
    with context(
        "that lists CartExampleFactory and ProductExampleFactory in backticks"
    ):
        with it("should parse both factory names"):
            expect(
                parse_md_factory_line(
                    "Example factories: `CartExampleFactory`, `ProductExampleFactory`"
                )
            ).to(equal(["CartExampleFactory", "ProductExampleFactory"]))
