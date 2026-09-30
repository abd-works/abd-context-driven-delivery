"""Mamba spec for a Python runnable-story Story Map."""

import ast
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _candidate in _HERE.parents:
    if (_candidate / "practices" / "stories").is_dir() and (
        _candidate / "contexts"
    ).is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from mamba import description, context, it, before
from expects import equal, have_len, be_true, contain, expect, raise_error

from practices.stories.model.story_model import Epic, Story, StoryType, Epic
from practices.stories.model.story_model import Scenario
from practices.stories.model.story_model import StoryModel
from practices.stories.model.code_story_model import CodeStoryModelError
from practices.stories.model.python.python_story_model import PythonStoryModel


def _story_map_with_stories() -> StoryModel:
    story_map = StoryModel()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    first = story_map.epics[0]
    for j in range(1, 4):
        sub = Epic(f"Epic 1.{j}", j)
        story = Story("Book a room", 1, StoryType.USER)
        story.actors = ["guest"]
        story.domain_terms = ["Room", "Reservation"]
        story.scenarios.append(
            Scenario(name="a room is available", sequential_order=1)
        )
        sub.stories.append(story)
        first.epics.append(sub)
    return story_map


with description("a Python runnable-story Story Map") as self:
    with context(
        "that holds a rendered code Story Map with 4 Epics and 3 Epics under the first Epic"
    ):
        with before.each:
            self.py = PythonStoryModel()
            self.canonical = _story_map_with_stories()
            self.tree = self.py.render(self.canonical)
            self.leaf_paths = self.py.leaf_files_of(self.tree)
            self.leaf_contents = [self.tree[p] for p in self.leaf_paths]

        with context("every leaf file"):
            with it("should be named `<sub_epic_snake>_story.test.py` in the parent epic folder"):
                for path in self.leaf_paths:
                    expect(path.endswith("_story.test.py")).to(be_true)
                    expect("/epic-1/epic_1_" in path).to(be_true)
                    expect("/book-a-room/" in path).to(equal(False))

            with it("should parse as a valid Python module"):
                for content in self.leaf_contents:
                    ast.parse(content)

            with it("should open the story"):
                for content in self.leaf_contents:
                    expect(content).to(contain('with story("Book a room")'))

            with it("should carry domain terms for markdown round-trip"):
                for content in self.leaf_contents:
                    expect(content).to(contain("Domain terms: Room, Reservation"))

        with context("every Scenario"):
            with it("should name the scenario"):
                for content in self.leaf_contents:
                    expect(content).to(contain('with scenario("a room is available")'))

    with context("that has been rendered and parsed back without edits"):
        with before.each:
            self.canonical = _story_map_with_stories()
            self.parsed = PythonStoryModel().parse(PythonStoryModel().render(self.canonical))

        with it("should preserve Story and Scenario counts under each Epic"):
            first_sub = self.parsed.epics[0].epics[0]
            expect(first_sub.stories).to(have_len(1))
            expect(first_sub.stories[0].scenarios).to(have_len(1))

        with it("should restore the Story name and actor"):
            story = self.parsed.epics[0].epics[0].stories[0]
            expect(story.name).to(equal("Book a room"))
            expect(story.actors).to(equal(["guest"]))

    with context("that is not a valid Python story-spec tree"):
        with it("should reject parse"):
            expect(lambda: PythonStoryModel().parse("not a tree")).to(
                raise_error(CodeStoryModelError)
            )
