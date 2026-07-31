"""BDD spec - Java runnable-story Story Map."""

import sys
from pathlib import Path

from expects import be_true, contain, equal, expect, have_len, raise_error
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from context_tools.stories.code.code_story_map import CodeStoryMapError
from context_tools.stories.code.java.java_story_map import JavaStoryMap
from context_tools.stories.story_model.nodes import Epic, Story, StoryType, SubEpic
from context_tools.stories.story_model.scenario import Scenario
from context_tools.stories.story_model.story_map import StoryMap


def _story_map_with_stories() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    first = story_map.epics[0]
    for j in range(1, 4):
        sub = SubEpic(f"SubEpic 1.{j}", j)
        story = Story("Redeem a voucher", 1, StoryType.USER)
        story.users = ["shopper"]
        story.scenarios.append(Scenario(name="Voucher is active", sequential_order=1))
        sub.stories.append(story)
        first.sub_epics.append(sub)
    return story_map


with description("a Java runnable-story Story Map") as self:
    with before.each:
        self.java = JavaStoryMap()

    with context("that holds rendered stories"):
        with before.each:
            self.tree = self.java.render(_story_map_with_stories())
            self.leaf_paths = self.java.leaf_files_of(self.tree)

        with it("should emit `*Story.java` under story folders"):
            for path in self.leaf_paths:
                expect(path.endswith("Story.java")).to(be_true)
                expect("/redeem-a-voucher/" in path).to(be_true)

        with it("should expose create(String mode) and fake main"):
            for path in self.leaf_paths:
                body = self.tree[path]
                expect(body).to(contain("public static void create(String mode)"))
                expect(body).to(contain('create("fake")'))

    with context("round-trip"):
        with before.each:
            self.parsed = self.java.parse(self.java.render(_story_map_with_stories()))

        with it("should preserve story and scenario"):
            story = self.parsed.epics[0].sub_epics[0].stories[0]
            expect(story.name).to(equal("Redeem a voucher"))
            expect(story.scenarios).to(have_len(1))

    with context("invalid parse input"):
        with it("should reject"):
            expect(lambda: self.java.parse("not a tree")).to(raise_error(CodeStoryMapError))
