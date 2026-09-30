"""Mamba spec for `a Miro Story Map`.

Mirrors practices/stories/model/drawio/drawio_story_model_spec.py one-for-one,
substituting SVG canvas-composer assertions for XML/mxCell assertions.

Covers two description blocks (one per fidelity, one turn each):
  1. story-map fidelity  — render / parse / sync the Epic->Epic->Story grid
  2. thin-slice fidelity — MiroIncrement.save / MiroIncrement.load swim-lane table
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

_HERE = Path(__file__).resolve()
for _candidate in _HERE.parents:
    if (_candidate / "practices" / "stories").is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, expect, raise_error, contain

from practices.stories.model.story_model import StoryMap, StoryType
from practices.stories.model.story_model import Scenario
from practices.stories.model.miro.nodes import (
    MiroEpic,
    MiroIncrement,
    MiroParseError,
    MiroStory,
    MiroStoryMap,
    MiroEpic,
)


# ---------------------------------------------------------------------------
# Shared fixture factory (identical to drawio_story_model_spec.py)
# ---------------------------------------------------------------------------

class SpecFixture:
    def story_map_with_4_epics_and_3_epics_and_1_story(self) -> StoryMap:
        story_map = MiroStoryMap()
        for i in range(1, 5):
            story_map.append_epic(MiroEpic(f"Epic {i}", i))
        first_epic = story_map.epics[0]
        for j in range(1, 4):
            sub = MiroEpic(f"Epic 1.{j}", j)
            story = MiroStory(f"Story 1.{j}.1", 1, StoryType.USER)
            story.scenarios.append(Scenario(name="scenario step", sequential_order=1))
            sub.append_story(story)
            first_epic.append_epic(sub)
        return story_map

    def svg_rects_with_role(self, text: str) -> list:
        root = ET.fromstring(text.split("\n", 1)[1] if text.startswith("<?") else text)
        return list(self._gather_rects(root))

    def _gather_rects(self, element):
        tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag
        if tag == "rect" and element.get("data-role"):
            yield element
        for child in element:
            yield from self._gather_rects(child)

    def rects_by_role(self, text: str, role_prefix: str) -> list:
        return [
            el
            for el in self.svg_rects_with_role(text)
            if el.get("data-role", "").startswith(role_prefix)
        ]


fixture = SpecFixture()


# ===========================================================================
# Turn 1 — story-map fidelity
# ===========================================================================

with description("a Miro Story Map (story-map fidelity)") as self:
    with before.each:
        self.miro = MiroStoryMap()

    with context(
        "that holds a rendered diagram Story Map with 4 Epics and 3 Epics under the first Epic"
    ):
        with before.each:
            self.source = fixture.story_map_with_4_epics_and_3_epics_and_1_story()
            self.text = self.source.clone()

        with it("should serialize as a valid SVG document"):
            root = ET.fromstring(
                self.text.split("\n", 1)[1] if self.text.startswith("<?") else self.text
            )
            tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
            expect(tag).to(equal("svg"))

        with context("every node"):
            with it("should appear as a rect with data-role in the SVG"):
                # 4 epics + 3 sub-epics + 3 stories = 10
                expect(fixture.svg_rects_with_role(self.text)).to(have_len(10))

        with context("with an Epic appended and the SVG re-rendered"):
            with before.each:
                self.source.append_epic(MiroEpic("Epic 5", 5))
                self.new_text = self.source.clone()

            with context("the document"):
                with it(
                    "should contain one additional Epic rect carrying the new Epic's name"
                ):
                    expect("Epic 5" in self.new_text).to(be_true)
                    epic_rects = fixture.rects_by_role(self.new_text, "epic")
                    expect(epic_rects).to(have_len(5))

        with context("with the first Epic renamed and the SVG re-rendered"):
            with before.each:
                self.source.epics[0].name = "Epic 1 (renamed)"
                self.new_text = self.source.clone()

            with context("the rect for the first Epic"):
                with it("should carry the new name as its data-content"):
                    expect("Epic 1 (renamed)" in self.new_text).to(be_true)

        with context("with a Epic deleted and the SVG re-rendered"):
            with before.each:
                self.source.epics[0].epics.pop(0)
                self.new_text = self.source.clone()

            with context("the document"):
                with it(
                    "should no longer contain the rect for the deleted Epic or any of its descendants"
                ):
                    expect("Epic 1.1" in self.new_text).to(be_false)
                    expect("Story 1.1.1" in self.new_text).to(be_false)

    with context("that has been rendered and parsed back without edits"):
        with before.each:
            self.original = fixture.story_map_with_4_epics_and_3_epics_and_1_story()
            self.parsed = self.miro.load(self.original.clone())

        with it("should preserve Story structure - scenarios are NOT embedded in the story-map view"):
            first_story = self.parsed.epics[0].epics[0].stories[0]
            expect(first_story.scenarios).to(have_len(0))

    with context("that is not a valid Miro story map SVG"):
        with context("the parse"):
            with it("should be rejected"):
                expect(lambda: self.miro.load("<not-svg/>")).to(
                    raise_error(MiroParseError)
                )

    with context("that stacks nested sub-epics by depth (parent above children)"):
        with before.each:
            self.source = MiroStoryMap()
            epic = MiroEpic("Create Hero", 1)
            compose = MiroEpic("Compose Powers", 1)
            attack = MiroEpic("Compose Attack Power", 1)
            attack.append_story(MiroStory("Compose Damage Effect", 1, StoryType.USER))
            extras = MiroEpic("Apply Power Extra", 2)
            extras.append_story(MiroStory("Apply Area Extra", 1, StoryType.USER))
            delivery = MiroEpic("Apply Delivery Extra", 1)
            delivery.append_story(MiroStory("Apply Accurate Extra", 1, StoryType.USER))
            extras.append_epic(delivery)
            compose.append_epic(attack)
            compose.append_epic(extras)
            epic.append_epic(compose)
            self.source.append_epic(epic)
            self.text = self.source.clone()
            self.root = ET.fromstring(
                self.text.split("\n", 1)[1] if self.text.startswith("<?") else self.text
            )

        with it("should place depth-0 sub-epics above depth-1 children"):
            d0 = [el for el in fixture.svg_rects_with_role(self.text) if el.get("data-role") == "subepic:0"]
            d1 = [el for el in fixture.svg_rects_with_role(self.text) if el.get("data-role") == "subepic:1"]
            expect(len(d0) > 0).to(be_true)
            expect(len(d1) > 0).to(be_true)
            expect(float(d0[0].get("y", 0)) < float(d1[0].get("y", 0))).to(be_true)

        with it("should place depth-1 sub-epics above depth-2 children"):
            d1 = [el for el in fixture.svg_rects_with_role(self.text) if el.get("data-role") == "subepic:1"]
            d2 = [el for el in fixture.svg_rects_with_role(self.text) if el.get("data-role") == "subepic:2"]
            expect(len(d1) > 0).to(be_true)
            expect(len(d2) > 0).to(be_true)
            expect(float(d1[0].get("y", 0)) < float(d2[0].get("y", 0))).to(be_true)

        with it("should round-trip nested hierarchy"):
            parsed = self.miro.load(self.text)
            compose = parsed.epics[0].epics[0]
            expect(compose.name).to(equal("Compose Powers"))
            expect(compose.epics).to(have_len(2))
            extras = compose.epics[1]
            expect(extras.name).to(equal("Apply Power Extra"))
            expect([s.name for s in extras.stories]).to(equal(["Apply Area Extra"]))
            expect(extras.epics).to(have_len(1))
            expect(extras.epics[0].name).to(equal("Apply Delivery Extra"))

    with context("that lays stories out as a story-map backbone"):
        with before.each:
            self.source = MiroStoryMap()
            epic = MiroEpic("Onboard A Customer", 1)
            capability = MiroEpic("Get Sign Up Plan", 1)
            first = MiroStory("Open Plan Deep Link", 1, StoryType.USER)
            first.actors = ["Prospect"]
            second = MiroStory("Query Product Offerings", 2, StoryType.SYSTEM)
            second.actors = ["System"]
            third = MiroStory("List Product Offerings", 3, StoryType.SYSTEM)
            third.actors = ["System"]
            capability.append_story(first)
            capability.append_story(second)
            capability.append_story(third)
            epic.append_epic(capability)
            self.source.append_epic(epic)
            self.text = self.source.clone()
            self.rects = fixture.svg_rects_with_role(self.text)

        with it("should place story cards in distinct left-to-right columns"):
            stories = fixture.rects_by_role(self.text, "story:")
            expect([int(story.get("x")) for story in stories]).to(
                equal([35, 95, 155])
            )

        with it("should use compact square story cards like the DrawIO map"):
            stories = fixture.rects_by_role(self.text, "story:")
            expect(
                [(int(story.get("width")), int(story.get("height"))) for story in stories]
            ).to(equal([(50, 50), (50, 50), (50, 50)]))

        with it("should span the capability and Epic across their story columns"):
            epic = fixture.rects_by_role(self.text, "epic")[0]
            capability = fixture.rects_by_role(self.text, "subepic:0")[0]
            expect((int(epic.get("x")), int(epic.get("width")))).to(equal((20, 180)))
            expect((int(capability.get("x")), int(capability.get("width")))).to(
                equal((30, 170))
            )

        with it("should place actor cards above each change of actor"):
            actors = fixture.rects_by_role(self.text, "actor")
            expect([actor.get("data-content") for actor in actors]).to(
                equal(["Prospect", "System"])
            )
            story_y = int(fixture.rects_by_role(self.text, "story:")[0].get("y"))
            expect(all(int(actor.get("y")) < story_y for actor in actors)).to(be_true)

        with it("should give every rendered card a unique hierarchy-based identity"):
            ids = [rect.get("id") for rect in self.rects]
            expect(len(ids)).to(equal(len(set(ids))))

        with it("should preserve each story actor when parsed back"):
            parsed = self.miro.load(self.text)
            stories = parsed.epics[0].epics[0].stories
            expect([story.actors for story in stories]).to(
                equal([["Prospect"], ["System"], ["System"]])
            )


# ===========================================================================
# Turn 2 — thin-slice fidelity
# ===========================================================================

with description("a Miro Story Map (thin-slice fidelity)") as self:
    with before.each:
        self.miro = MiroStoryMap()

    with context("rendering the thin-slice view for a StoryMap with 2 increments"):
        with before.each:
            self.source = fixture.story_map_with_4_epics_and_3_epics_and_1_story()
            inc_a = MiroIncrement(
                "Increment A - first outcome",
                1,
                [MiroStory("Story 1.1.1", 1), MiroStory("Story 1.2.1", 2)],
            )
            inc_b = MiroIncrement("Increment B - second outcome", 2, [MiroStory("Story 1.3.1", 1)])
            self.source.append_increment(inc_a)
            self.source.append_increment(inc_b)
            self.text = MiroIncrement.save(self.source)
            self.root = ET.fromstring(
                self.text.split("\n", 1)[1] if self.text.startswith("<?") else self.text
            )

        with it("should serialize as a valid SVG document with a table foreignObject"):
            tag = (self.root.tag.split("}")[-1] if "}" in self.root.tag else self.root.tag)
            expect(tag).to(equal("svg"))
            fo = None
            for el in self.root.iter():
                t = el.tag.split("}")[-1] if "}" in el.tag else el.tag
                if t == "foreignObject" and el.get("data-type") == "table":
                    fo = el
                    break
            expect(fo is not None).to(be_true)

        with it("should render increment names in the first column"):
            expect("Increment A - first outcome" in self.text).to(be_true)
            expect("Increment B - second outcome" in self.text).to(be_true)

        with it("should render epic/subepic column headers"):
            expect("Epic 1" in self.text).to(be_true)

        with it("should render story names in the correct increment rows"):
            expect("Story 1.1.1" in self.text).to(be_true)
            expect("Story 1.2.1" in self.text).to(be_true)
            expect("Story 1.3.1" in self.text).to(be_true)

    with context("parsing the thin-slice SVG back into increment nodes"):
        with before.each:
            self.source = fixture.story_map_with_4_epics_and_3_epics_and_1_story()
            inc_a = MiroIncrement("Increment A", 1, [MiroStory("Story 1.1.1", 1)])
            inc_b = MiroIncrement(
                "Increment B",
                2,
                [MiroStory("Story 1.2.1", 1), MiroStory("Story 1.3.1", 2)],
            )
            self.source.append_increment(inc_a)
            self.source.append_increment(inc_b)
            self.text = MiroIncrement.save(self.source)
            self.increments = MiroIncrement.load(self.text)

        with it("should recover both increments"):
            expect(self.increments).to(have_len(2))

        with it("should recover the correct increment names"):
            expect(self.increments[0].name).to(equal("Increment A"))
            expect(self.increments[1].name).to(equal("Increment B"))

        with it("should recover the stories assigned to each increment"):
            expect([story.name for story in self.increments[0].stories]).to(equal(["Story 1.1.1"]))
            expect([story.name for story in self.increments[1].stories]).to(
                equal(["Story 1.2.1", "Story 1.3.1"])
            )

    with context("that is not a valid thin-slice SVG"):
        with context("the parse"):
            with it("should be rejected"):
                expect(
                    lambda: MiroIncrement.load("<not-svg/>")
                ).to(raise_error(MiroParseError))
