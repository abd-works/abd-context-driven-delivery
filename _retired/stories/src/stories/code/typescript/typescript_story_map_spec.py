"""Mamba spec for `a TypeScript story-spec Story Map`.

Exercises the Uniform Callable Surface — stateless backend, canonical StoryMap
passed to every call.
"""

import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _candidate in _HERE.parents:
    if (_candidate / "stories" / "src" / "stories").is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, expect, raise_error

from stories.src.stories.model.nodes import Epic, Story, StoryType, SubEpic
from stories.src.stories.model.scenario import Clause, Interaction, Phase, Scenario
from stories.src.stories.model.story_map import StoryMap
from stories.src.stories.code.code_story_map import (
    CodeStoryMapError,
    to_kebab,
    to_upper_snake,
)
from stories.src.stories.code.typescript.typescript_story_map import TypeScriptStoryMap


def _make_scenario(name: str, order: int, given_text: str = "a context") -> Scenario:
    sc = Scenario(name=name, sequential_order=order)
    sc.given = [Clause(text=given_text, phase=Phase.GIVEN)]
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
        story.scenarios.append(_make_scenario("Voucher is active", 1, "an active voucher exists"))
        story.scenarios.append(_make_scenario("Paid order is placed", 2, "a paid order is placed"))
        sub.stories.append(story)
        first.sub_epics.append(sub)
    return story_map


with description("a TypeScript story-spec Story Map") as self:
    with before.each:
        self.ts = TypeScriptStoryMap()

    with context(
        "that holds a rendered code Story Map with 4 Epics and 3 SubEpics under the first Epic"
    ):
        with before.each:
            self.canonical = _story_map_with_stories()
            self.tree = self.ts.render(self.canonical)
            self.leaf_paths = self.ts.leaf_files_of(self.tree)
            self.leaf_contents = [self.tree[p] for p in self.leaf_paths]

        with context("every leaf file"):
            with it("should be named `<sub-epic-slug>-stories.ts`"):
                for path in self.leaf_paths:
                    filename = path.split("/")[-1]
                    expect(filename.endswith("-stories.ts")).to(be_true)

            with it(
                "should import the Story type from the shared story-types module using a relative path matching its folder depth"
            ):
                for content in self.leaf_contents:
                    expect("import type { Story }" in content).to(be_true)
                    expect(re.search(r'from "(\.\./)+story-types"', content) is not None).to(be_true)

            with it("should parse as syntactically valid TypeScript (balanced braces and brackets)"):
                for content in self.leaf_contents:
                    expect(content.count("{")).to(equal(content.count("}")))
                    expect(content.count("[")).to(equal(content.count("]")))

        with context("every Story block"):
            with it("should be an exported const named after the Story in UPPER_SNAKE_CASE, closed with `as const satisfies Story`"):
                for content in self.leaf_contents:
                    expected_name = to_upper_snake("Redeem a voucher")
                    expect(f"export const {expected_name} = {{" in content).to(be_true)
                    expect("as const satisfies Story" in content).to(be_true)

            with it("should carry a `story` field holding the Story name as a template-string literal"):
                for content in self.leaf_contents:
                    expect("story: `Redeem a voucher`" in content).to(be_true)

            with it("should carry an `actor` field holding the Story's actor as a template-string literal"):
                for content in self.leaf_contents:
                    expect("actor: `shopper`" in content).to(be_true)

            with it("should carry `domainTerms` and `evidence` fields, empty when the Story declares none"):
                for content in self.leaf_contents:
                    expect("domainTerms: []" in content).to(be_true)
                    expect("evidence: []" in content).to(be_true)

            with it(
                "should expose one Scenario property per Scenario, keyed by a camelCased slug derived from the Scenario name"
            ):
                for content in self.leaf_contents:
                    expect("voucherIsActive:" in content).to(be_true)
                    expect("paidOrderIsPlaced:" in content).to(be_true)

        with context("every Scenario property inside a Story block"):
            with it("should hold a `name` field carrying the human-readable Scenario name"):
                for content in self.leaf_contents:
                    expect("name: `Voucher is active`" in content).to(be_true)

            with it("should hold a `given` array carrying the given clauses"):
                for content in self.leaf_contents:
                    expect("given: [`an active voucher exists`] as const," in content).to(be_true)

            with it("should hold an `interactions` array with when/then pairs"):
                for content in self.leaf_contents:
                    expect("when:" in content).to(be_true)
                    expect("then:" in content).to(be_true)

    with context("that has been edited in the TypeScript source and synced back against a canonical code Story Map"):
        with before.each:
            self.canonical = _story_map_with_stories()
            edited = _story_map_with_stories()
            edited.epics[0].sub_epics[0].name = "SubEpic 1.1 (edited)"
            edited.epics[0].sub_epics.append(SubEpic("SubEpic 1.4", 4))
            edited_tree = self.ts.render(edited)
            self.report = self.ts.sync(edited_tree, self.canonical)

        with context("the returned UpdateReport"):
            with it("should list every add, remove, rename, reorder, and move applied to the source"):
                total = (
                    len(self.report.adds())
                    + len(self.report.renames())
                    + len(self.report.removes())
                    + len(self.report.reorders())
                )
                expect(total >= 1).to(be_true)

        with context("the reconstructed code Story Map"):
            with it("should reflect every edit made to the source"):
                sub_names = [
                    to_kebab(s.name) for s in self.canonical.epics[0].sub_epics
                ]
                expect("subepic-1-1-edited" in sub_names or "subepic-1-4" in sub_names).to(
                    be_true
                )

    with context("that is not a valid TypeScript story-spec tree"):
        with context("the parse"):
            with it("should be rejected"):
                expect(lambda: self.ts.parse("not a tree")).to(raise_error(CodeStoryMapError))

    with context("that has been rendered and parsed back without edits"):
        with before.each:
            self.canonical = _story_map_with_stories()
            self.parsed = self.ts.parse(self.ts.render(self.canonical))

        with it("should preserve Story and Scenario counts under each SubEpic"):
            first_sub = self.parsed.epics[0].sub_epics[0]
            expect(first_sub.stories).to(have_len(1))
            expect(first_sub.stories[0].scenarios).to(have_len(2))

    with context("that includes backticks in Scenario names"):
        with before.each:
            self.canonical = _story_map_with_stories()
            story = self.canonical.epics[0].sub_epics[0].stories[0]
            sc = Scenario(name="the `maintenance` flag is enabled", sequential_order=3)
            story.scenarios.append(sc)
            self.roundtrip = self.ts.parse(self.ts.render(self.canonical))

        with it("should preserve backtick content without dropping scenarios"):
            story = self.roundtrip.epics[0].sub_epics[0].stories[0]
            expect(story.scenarios).to(have_len(3))
