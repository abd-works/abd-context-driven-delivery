"""Mamba spec for a Python runnable-story Story Map."""

import ast
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _candidate in _HERE.parents:
    if (_candidate / "contexts" / "stories").is_dir() and (
        _candidate / "contexts"
    ).is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from mamba import description, context, it, before
from expects import equal, have_len, be_true, contain, expect, raise_error

from contexts.stories.story_model.nodes import Epic, Story, StoryType, SubEpic
from contexts.stories.story_model.scenario import Scenario
from contexts.stories.story_model.story_map import StoryMap
from contexts.stories.code.code_story_map import CodeStoryMapError, to_kebab
from contexts.stories.code.python.python_story_map import PythonStoryMap


def _story_map_with_stories() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    first = story_map.epics[0]
    for j in range(1, 4):
        sub = SubEpic(f"SubEpic 1.{j}", j)
        story = Story("Book a room", 1, StoryType.USER)
        story.users = ["guest"]
        story.domain_terms = ["Room", "Reservation"]
        story.scenarios.append(
            Scenario(name="a room is available", sequential_order=1)
        )
        sub.stories.append(story)
        first.sub_epics.append(sub)
    return story_map


with description("a Python runnable-story Story Map") as self:
    with context(
        "that holds a rendered code Story Map with 4 Epics and 3 SubEpics under the first Epic"
    ):
        with before.each:
            self.py = PythonStoryMap()
            self.canonical = _story_map_with_stories()
            self.tree = self.py.render(self.canonical)
            self.leaf_paths = self.py.leaf_files_of(self.tree)
            self.leaf_contents = [self.tree[p] for p in self.leaf_paths]

        with context("every leaf file"):
            with it("should be named `<story_snake>_story.py` under a story folder"):
                for path in self.leaf_paths:
                    expect(path.endswith("_story.py")).to(be_true)
                    expect("/book-a-room/" in path).to(be_true)

            with it("should parse as a valid Python module"):
                for content in self.leaf_contents:
                    ast.parse(content)

            with it("should export create_<story>_story(mode)"):
                for content in self.leaf_contents:
                    expect(content).to(contain("def create_book_a_room_story(mode"))

            with it("should wire fake mode at module level"):
                for content in self.leaf_contents:
                    expect(content).to(contain('create_book_a_room_story("fake")'))

            with it("should carry domain terms for markdown round-trip"):
                for content in self.leaf_contents:
                    expect(content).to(contain("Domain terms: Room, Reservation"))

        with context("every Epic folder"):
            with it("should hold an `<epic_snake>_helper.py` with Helper class"):
                helper_paths = [p for p in self.tree if p.endswith("_helper.py")]
                expect(helper_paths).to(have_len(4))
                for path in helper_paths:
                    expect("class " in self.tree[path]).to(be_true)
                    expect("Helper:" in self.tree[path]).to(be_true)

        with context("every Scenario"):
            with it("should be a test_* stub with SCENARIO docstring"):
                for content in self.leaf_contents:
                    expect(content).to(contain("def test_a_room_is_available()"))
                    expect(content).to(contain("SCENARIO: a room is available"))

    with context("that has been rendered and parsed back without edits"):
        with before.each:
            self.canonical = _story_map_with_stories()
            self.parsed = PythonStoryMap().parse(PythonStoryMap().render(self.canonical))

        with it("should preserve Story and Scenario counts under each SubEpic"):
            first_sub = self.parsed.epics[0].sub_epics[0]
            expect(first_sub.stories).to(have_len(1))
            expect(first_sub.stories[0].scenarios).to(have_len(1))

        with it("should restore the Story name and actor"):
            story = self.parsed.epics[0].sub_epics[0].stories[0]
            expect(story.name).to(equal("Book a room"))
            expect(story.users).to(equal(["guest"]))

    with context("that is not a valid Python story-spec tree"):
        with it("should reject parse"):
            expect(lambda: PythonStoryMap().parse("not a tree")).to(
                raise_error(CodeStoryMapError)
            )

    with context("for an Epic that declares CartExampleFactory"):
        with before.each:
            story_map = _story_map_with_stories()
            story_map.epics[0].example_factories = ["CartExampleFactory"]
            self.tree = PythonStoryMap().render(story_map)
            helper_paths = [
                p
                for p in self.tree
                if p.endswith("_helper.py") and to_kebab("Epic 1") in p
            ]
            self.helper = self.tree[helper_paths[0]]

        with it("should import CartExampleFactory in the epic helper"):
            expect(self.helper).to(contain("CartExampleFactory"))

        with it("should mention fake mode not Fake subclasses"):
            expect(self.helper).to(contain("fake mode"))
