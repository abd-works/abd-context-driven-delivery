"""BDD spec - TypeScript runnable-story Story Map."""

import sys
from pathlib import Path

from expects import be_true, contain, equal, expect, have_len, raise_error
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from context_tools.stories.code.code_story_map import CodeStoryMapError
from context_tools.stories.code.typescript.typescript_story_map import TypeScriptStoryMap
from context_tools.stories.story_model.nodes import Epic, Story, StoryType, SubEpic
from context_tools.stories.story_model.scenario import Clause, Interaction, Phase, Scenario
from context_tools.stories.story_model.story_map import StoryMap


def _make_scenario(name: str, order: int) -> Scenario:
    sc = Scenario(name=name, sequential_order=order)
    sc.given = [Clause(text="a context", phase=Phase.GIVEN)]
    sc.interactions = [
        Interaction(
            when=[Clause(text="the action occurs", phase=Phase.WHEN)],
            then=[Clause(text="the outcome is observed", phase=Phase.THEN)],
        )
    ]
    return sc


def _story_map_with_stories() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    first = story_map.epics[0]
    for j in range(1, 4):
        sub = SubEpic(f"SubEpic 1.{j}", j)
        story = Story("Redeem a voucher", 1, StoryType.USER)
        story.users = ["shopper"]
        story.scenarios.append(_make_scenario("Voucher is active", 1))
        sub.stories.append(story)
        first.sub_epics.append(sub)
    return story_map


with description("a TypeScript runnable-story Story Map") as self:
    with before.each:
        self.ts = TypeScriptStoryMap()

    with context("that holds rendered stories"):
        with before.each:
            self.tree = self.ts.render(_story_map_with_stories())
            self.leaf_paths = self.ts.leaf_files_of(self.tree)

        with it("should emit `{story}.{tier}.ts` under epic/sub-epic, not a story folder"):
            for path in self.leaf_paths:
                expect(path.endswith(".front-end.ts") or path.endswith(".back-end.ts")).to(
                    be_true
                )
                expect("/redeem-a-voucher/" in path).to(equal(False))
                expect("redeem-a-voucher." in path).to(be_true)

        with it("should include givens.ts at epic and sub-epic"):
            expect(any(p.endswith("/givens.ts") for p in self.tree)).to(be_true)

        with it("should export createRedeemAVoucherStory"):
            for path in self.leaf_paths:
                expect(self.tree[path]).to(contain("export function createRedeemAVoucherStory("))

        with it("should include examples/ at epic and sub-epic"):
            expect(any("/examples/" in p for p in self.tree)).to(be_true)

        with it("should include story-test shared helper"):
            expect("tests/story-test.ts" in self.tree).to(be_true)

    with context("a scenario with two Then outcomes"):
        with it("should chain the second outcome with .and()"):
            story = Story("Select Plan", 1, StoryType.USER)
            sc = Scenario(name="catalog listed", sequential_order=1)
            sc.given = [Clause(text="plans exist", phase=Phase.GIVEN)]
            sc.interactions = [
                Interaction(
                    when=[Clause(text="they view the catalog", phase=Phase.WHEN)],
                    then=[
                        Clause(text="names are shown", phase=Phase.THEN),
                        Clause(text="prices are shown", phase=Phase.THEN),
                    ],
                )
            ]
            story.scenarios.append(sc)
            from context_tools.stories.code.typescript.story_file import render_story_file

            src = render_story_file(story)
            expect(".and(" in src).to(be_true)
            expect(src.count("then(")).to(equal(1))

    with context("round-trip"):
        with before.each:
            self.parsed = self.ts.parse(self.ts.render(_story_map_with_stories()))

        with it("should preserve story and scenario"):
            story = self.parsed.epics[0].sub_epics[0].stories[0]
            expect(story.name).to(equal("Redeem a voucher"))
            expect(story.scenarios).to(have_len(1))

    with context("invalid parse input"):
        with it("should reject"):
            expect(lambda: self.ts.parse("not a tree")).to(raise_error(CodeStoryMapError))
