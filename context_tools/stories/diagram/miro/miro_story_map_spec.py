"""Mamba spec for `a Miro Story Map`.

Mirrors context_tools/stories/diagram/drawio/drawio_story_map_spec.py one-for-one,
substituting SVG canvas-composer assertions for XML/mxCell assertions.

Covers three description blocks (one per fidelity, one turn each):
  1. story-map fidelity  — render / parse / sync the Epic->SubEpic->Story grid
  2. thin-slice fidelity — render_thin_slice / parse_thin_slice swim-lane table
  3. scenario fidelity   — render_scenario markdown doc
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

_HERE = Path(__file__).resolve()
for _candidate in _HERE.parents:
    if (_candidate / "context_tools" / "stories").is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, expect, raise_error, contain

from context_tools.stories.story_model.nodes import Epic, Story, StoryType, SubEpic
from context_tools.stories.story_model.story_map import StoryMap
from context_tools.stories.story_model.thin_slice import Increment
from context_tools.stories.story_model.scenario import Clause, Interaction, Phase, Scenario
from context_tools.stories.diagram.miro.nodes import (
    MiroParseError,
    MiroStoryMap,
)


# ---------------------------------------------------------------------------
# Shared fixture factory (identical to drawio_story_map_spec.py)
# ---------------------------------------------------------------------------

def _story_map_with_4_epics_and_3_sub_epics_and_1_story() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    first_epic = story_map.epics[0]
    for j in range(1, 4):
        sub = SubEpic(f"SubEpic 1.{j}", j)
        story = Story(f"Story 1.{j}.1", 1, StoryType.USER)
        story.scenarios.append(Scenario(name="scenario step", sequential_order=1))
        sub.stories.append(story)
        first_epic.sub_epics.append(sub)
    return story_map


def _svg_rects_with_role(text: str) -> list:
    """Return all rect elements carrying a data-role attribute."""
    root = ET.fromstring(text.split("\n", 1)[1] if text.startswith("<?") else text)

    def _gather(el):
        tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
        if tag == "rect" and el.get("data-role"):
            yield el
        for child in el:
            yield from _gather(child)

    return list(_gather(root))


def _rects_by_role(text: str, role_prefix: str) -> list:
    return [el for el in _svg_rects_with_role(text) if el.get("data-role", "").startswith(role_prefix)]


# ===========================================================================
# Turn 1 — story-map fidelity
# ===========================================================================

with description("a Miro Story Map (story-map fidelity)") as self:
    with before.each:
        self.miro = MiroStoryMap()

    with context(
        "that holds a rendered diagram Story Map with 4 Epics and 3 SubEpics under the first Epic"
    ):
        with before.each:
            self.source = _story_map_with_4_epics_and_3_sub_epics_and_1_story()
            self.text = self.miro.render(self.source)

        with it("should serialize as a valid SVG document"):
            root = ET.fromstring(
                self.text.split("\n", 1)[1] if self.text.startswith("<?") else self.text
            )
            tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
            expect(tag).to(equal("svg"))

        with context("every node"):
            with it("should appear as a rect with data-role in the SVG"):
                # 4 epics + 3 sub-epics + 3 stories = 10
                expect(_svg_rects_with_role(self.text)).to(have_len(10))

        with context("with an Epic appended and the SVG re-rendered"):
            with before.each:
                self.source.append_epic(Epic("Epic 5", 5))
                self.new_text = self.miro.render(self.source)

            with context("the document"):
                with it(
                    "should contain one additional Epic rect carrying the new Epic's name"
                ):
                    expect("Epic 5" in self.new_text).to(be_true)
                    epic_rects = _rects_by_role(self.new_text, "epic")
                    expect(epic_rects).to(have_len(5))

        with context("with the first Epic renamed and the SVG re-rendered"):
            with before.each:
                self.source.epics[0].name = "Epic 1 (renamed)"
                self.new_text = self.miro.render(self.source)

            with context("the rect for the first Epic"):
                with it("should carry the new name as its data-content"):
                    expect("Epic 1 (renamed)" in self.new_text).to(be_true)

        with context("with a SubEpic deleted and the SVG re-rendered"):
            with before.each:
                self.source.epics[0].sub_epics.pop(0)
                self.new_text = self.miro.render(self.source)

            with context("the document"):
                with it(
                    "should no longer contain the rect for the deleted SubEpic or any of its descendants"
                ):
                    expect("SubEpic 1.1" in self.new_text).to(be_false)
                    expect("Story 1.1.1" in self.new_text).to(be_false)

    with context("that has been edited on the Miro board and synced back"):
        with before.each:
            self.canonical = _story_map_with_4_epics_and_3_sub_epics_and_1_story()
            edited = _story_map_with_4_epics_and_3_sub_epics_and_1_story()
            edited.epics[0].name = "Epic 1 (edited)"
            edited.append_epic(Epic("Epic 5", 5))
            edited_text = self.miro.render(edited)
            self.report = self.miro.sync(edited_text, self.canonical)

        with context("the returned UpdateReport"):
            with it(
                "should list every add, remove, rename, reorder, and move applied to the board"
            ):
                expect(
                    len(self.report.adds()) + len(self.report.renames()) >= 2
                ).to(be_true)

        with context("the reconstructed Story Map"):
            with it("should reflect every edit made to the board"):
                names = [e.name for e in self.canonical.epics]
                expect("Epic 1 (edited)" in names).to(be_true)
                expect("Epic 5" in names).to(be_true)

    with context("that has been rendered and parsed back without edits"):
        with before.each:
            self.original = _story_map_with_4_epics_and_3_sub_epics_and_1_story()
            self.parsed = self.miro.parse(self.miro.render(self.original))

        with it("should preserve Story structure - scenarios are NOT embedded in the story-map view"):
            first_story = self.parsed.epics[0].sub_epics[0].stories[0]
            expect(first_story.scenarios).to(have_len(0))

    with context("that is not a valid Miro story map SVG"):
        with context("the parse"):
            with it("should be rejected"):
                expect(lambda: self.miro.parse("<not-svg/>")).to(
                    raise_error(MiroParseError)
                )

    with context("that stacks nested sub-epics by depth (parent above children)"):
        with before.each:
            self.source = StoryMap()
            epic = Epic("Create Hero", 1)
            compose = SubEpic("Compose Powers", 1)
            attack = SubEpic("Compose Attack Power", 1)
            attack.stories.append(Story("Compose Damage Effect", 1, StoryType.USER))
            extras = SubEpic("Apply Power Extra", 2)
            extras.stories.append(Story("Apply Area Extra", 1, StoryType.USER))
            delivery = SubEpic("Apply Delivery Extra", 1)
            delivery.stories.append(Story("Apply Accurate Extra", 1, StoryType.USER))
            extras.sub_epics.append(delivery)
            compose.sub_epics.extend([attack, extras])
            epic.sub_epics.append(compose)
            self.source.append_epic(epic)
            self.text = self.miro.render(self.source)
            self.root = ET.fromstring(
                self.text.split("\n", 1)[1] if self.text.startswith("<?") else self.text
            )

        with it("should place depth-0 sub-epics above depth-1 children"):
            d0 = [el for el in _svg_rects_with_role(self.text) if el.get("data-role") == "subepic:0"]
            d1 = [el for el in _svg_rects_with_role(self.text) if el.get("data-role") == "subepic:1"]
            expect(len(d0) > 0).to(be_true)
            expect(len(d1) > 0).to(be_true)
            expect(float(d0[0].get("y", 0)) < float(d1[0].get("y", 0))).to(be_true)

        with it("should place depth-1 sub-epics above depth-2 children"):
            d1 = [el for el in _svg_rects_with_role(self.text) if el.get("data-role") == "subepic:1"]
            d2 = [el for el in _svg_rects_with_role(self.text) if el.get("data-role") == "subepic:2"]
            expect(len(d1) > 0).to(be_true)
            expect(len(d2) > 0).to(be_true)
            expect(float(d1[0].get("y", 0)) < float(d2[0].get("y", 0))).to(be_true)

        with it("should round-trip nested hierarchy"):
            parsed = self.miro.parse(self.text)
            compose = parsed.epics[0].sub_epics[0]
            expect(compose.name).to(equal("Compose Powers"))
            expect(compose.sub_epics).to(have_len(2))
            extras = compose.sub_epics[1]
            expect(extras.name).to(equal("Apply Power Extra"))
            expect([s.name for s in extras.stories]).to(equal(["Apply Area Extra"]))
            expect(extras.sub_epics).to(have_len(1))
            expect(extras.sub_epics[0].name).to(equal("Apply Delivery Extra"))

    with context("that lays stories out as a story-map backbone"):
        with before.each:
            self.source = StoryMap()
            epic = Epic("Onboard A Customer", 1)
            capability = SubEpic("Get Sign Up Plan", 1)
            first = Story("Open Plan Deep Link", 1, StoryType.USER)
            first.users = ["Prospect"]
            second = Story("Query Product Offerings", 2, StoryType.SYSTEM)
            second.users = ["System"]
            third = Story("List Product Offerings", 3, StoryType.SYSTEM)
            third.users = ["System"]
            capability.stories.extend([first, second, third])
            epic.sub_epics.append(capability)
            self.source.append_epic(epic)
            self.text = self.miro.render(self.source)
            self.rects = _svg_rects_with_role(self.text)

        with it("should place story cards in distinct left-to-right columns"):
            stories = _rects_by_role(self.text, "story:")
            expect([int(story.get("x")) for story in stories]).to(
                equal([35, 95, 155])
            )

        with it("should use compact square story cards like the DrawIO map"):
            stories = _rects_by_role(self.text, "story:")
            expect(
                [(int(story.get("width")), int(story.get("height"))) for story in stories]
            ).to(equal([(50, 50), (50, 50), (50, 50)]))

        with it("should span the capability and Epic across their story columns"):
            epic = _rects_by_role(self.text, "epic")[0]
            capability = _rects_by_role(self.text, "subepic:0")[0]
            expect((int(epic.get("x")), int(epic.get("width")))).to(equal((20, 180)))
            expect((int(capability.get("x")), int(capability.get("width")))).to(
                equal((30, 170))
            )

        with it("should place actor cards above each change of actor"):
            actors = _rects_by_role(self.text, "actor")
            expect([actor.get("data-content") for actor in actors]).to(
                equal(["Prospect", "System"])
            )
            story_y = int(_rects_by_role(self.text, "story:")[0].get("y"))
            expect(all(int(actor.get("y")) < story_y for actor in actors)).to(be_true)

        with it("should give every rendered card a unique hierarchy-based identity"):
            ids = [rect.get("id") for rect in self.rects]
            expect(len(ids)).to(equal(len(set(ids))))

        with it("should preserve each story actor when parsed back"):
            parsed = self.miro.parse(self.text)
            stories = parsed.epics[0].sub_epics[0].stories
            expect([story.users for story in stories]).to(
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
            self.source = _story_map_with_4_epics_and_3_sub_epics_and_1_story()
            inc_a = Increment(name="Increment A - first outcome", sequential_order=1)
            inc_a.stories = ["Story 1.1.1", "Story 1.2.1"]
            inc_b = Increment(name="Increment B - second outcome", sequential_order=2)
            inc_b.stories = ["Story 1.3.1"]
            self.source.append_increment(inc_a)
            self.source.append_increment(inc_b)
            self.text = self.miro.render_thin_slice(self.source)
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
            self.source = _story_map_with_4_epics_and_3_sub_epics_and_1_story()
            inc_a = Increment(name="Increment A", sequential_order=1)
            inc_a.stories = ["Story 1.1.1"]
            inc_b = Increment(name="Increment B", sequential_order=2)
            inc_b.stories = ["Story 1.2.1", "Story 1.3.1"]
            self.source.append_increment(inc_a)
            self.source.append_increment(inc_b)
            self.text = self.miro.render_thin_slice(self.source)
            self.increments = self.miro.parse_thin_slice(self.text)

        with it("should recover both increments"):
            expect(self.increments).to(have_len(2))

        with it("should recover the correct increment names"):
            expect(self.increments[0].name).to(equal("Increment A"))
            expect(self.increments[1].name).to(equal("Increment B"))

        with it("should recover the stories assigned to each increment"):
            expect(self.increments[0].stories).to(contain("Story 1.1.1"))
            expect(self.increments[1].stories).to(contain("Story 1.2.1"))
            expect(self.increments[1].stories).to(contain("Story 1.3.1"))

    with context("that is not a valid thin-slice SVG"):
        with context("the parse"):
            with it("should be rejected"):
                expect(
                    lambda: self.miro.parse_thin_slice("<not-svg/>")
                ).to(raise_error(MiroParseError))


# ===========================================================================
# Turn 3 — scenario fidelity
# ===========================================================================

with description("a Miro Story Map (scenario fidelity)") as self:
    with before.each:
        self.miro = MiroStoryMap()

    with context("rendering the scenario view for a Story with one Scenario"):
        with before.each:
            self.source = StoryMap()
            epic = Epic("Epic 1", 1)
            sub = SubEpic("SubEpic 1.1", 1)
            story = Story("Submit Order", 1, StoryType.USER)
            scenario = Scenario(
                name="Submit before cutoff settles same day",
                story_name="Submit Order",
            )
            scenario.given = [Clause(text="a Treasurer with a funded Account", phase=Phase.GIVEN)]
            scenario.interactions = [
                Interaction(
                    when=[Clause(text="the Treasurer submits a Transfer", phase=Phase.WHEN)],
                    then=[
                        Clause(text="the System returns a Confirmation", phase=Phase.THEN),
                        Clause(
                            text="And the Transfer is marked same-day",
                            phase=Phase.THEN,
                            is_continuation=True,
                        ),
                    ],
                )
            ]
            story.scenarios.append(scenario)
            sub.stories.append(story)
            epic.sub_epics.append(sub)
            self.source.append_epic(epic)
            self.text = self.miro.render_scenario(self.source)
            self.root = ET.fromstring(
                self.text.split("\n", 1)[1] if self.text.startswith("<?") else self.text
            )

        with it("should serialize as a valid SVG document with a doc foreignObject"):
            tag = (self.root.tag.split("}")[-1] if "}" in self.root.tag else self.root.tag)
            expect(tag).to(equal("svg"))
            fo = None
            for el in self.root.iter():
                t = el.tag.split("}")[-1] if "}" in el.tag else el.tag
                if t == "foreignObject" and el.get("data-type") == "doc":
                    fo = el
                    break
            expect(fo is not None).to(be_true)

        with it("should embed the story name as a heading"):
            expect("Submit Order" in self.text).to(be_true)

        with it("should embed the scenario name"):
            expect("Submit before cutoff settles same day" in self.text).to(be_true)

        with it("should prefix first-of-phase clauses with the phase keyword"):
            expect("Given" in self.text).to(be_true)
            expect("When" in self.text).to(be_true)
            expect("Then" in self.text).to(be_true)

        with it("should leave continuation clauses untouched (no prefix added)"):
            # The continuation clause starts with "And"; no "Then And" prefix
            expect("And the Transfer is marked same-day" in self.text).to(be_true)
            expect("Then And" in self.text).to(be_false)

    with context("rendering a StoryMap with no scenarios"):
        with before.each:
            empty = StoryMap()
            self.text = self.miro.render_scenario(empty)

        with it("should produce a valid SVG with a doc placeholder"):
            root = ET.fromstring(
                self.text.split("\n", 1)[1] if self.text.startswith("<?") else self.text
            )
            fo = None
            for el in root.iter():
                t = el.tag.split("}")[-1] if "}" in el.tag else el.tag
                if t == "foreignObject" and el.get("data-type") == "doc":
                    fo = el
                    break
            expect(fo is not None).to(be_true)
