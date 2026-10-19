"""BDD spec - Java runnable-story Story Map."""

import sys
from pathlib import Path

from expects import be_true, contain, equal, expect, have_len, raise_error
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from practices.stories.model.code_story_model import CodeStoryModelError
from practices.stories.model.java.java_story_model import JavaStoryModel
from practices.stories.model.story_model import Epic, Story, StoryType, Epic
from practices.stories.model.story_model import Scenario
from practices.stories.model.story_model import StoryModel


def _story_map_with_stories() -> StoryModel:
    story_map = StoryModel()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    first = story_map.epics[0]
    for j in range(1, 4):
        sub = Epic(f"Epic 1.{j}", j)
        story = Story("Redeem a voucher", 1, StoryType.USER)
        story.actors = ["shopper"]
        story.scenarios.append(Scenario(name="Voucher is active", sequential_order=1))
        sub.stories.append(story)
        first.epics.append(sub)
    return story_map


with description("a Java runnable-story Story Map") as self:
    with before.each:
        self.java = JavaStoryModel()

    with context("that holds rendered stories"):
        with before.each:
            self.tree = self.java.render(_story_map_with_stories())
            self.leaf_paths = self.java.leaf_files_of(self.tree)

        with it("should emit one `*Story.java` for the sub-epic in the parent epic folder"):
            for path in self.leaf_paths:
                expect(path.endswith("Story.java")).to(be_true)
                expect("/epic-1/" in path).to(be_true)
                expect("/redeem-a-voucher/" in path).to(equal(False))

        with it("should name the story and its scenario"):
            for path in self.leaf_paths:
                body = self.tree[path]
                expect(body).to(contain("Story: Redeem a voucher"))
                expect(body).to(contain("SCENARIO: Voucher is active"))

    with context("round-trip"):
        with before.each:
            self.parsed = self.java.parse(self.java.render(_story_map_with_stories()))

        with it("should preserve story and scenario"):
            story = self.parsed.epics[0].epics[0].stories[0]
            expect(story.name).to(equal("Redeem a voucher"))
            expect(story.scenarios).to(have_len(1))

    with context("invalid parse input"):
        with it("should reject"):
            expect(lambda: self.java.parse("not a tree")).to(raise_error(CodeStoryModelError))
