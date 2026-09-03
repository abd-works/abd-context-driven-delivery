"""Mamba spec for `a DrawIO Story Map`. Mirrors ../../bdd-context.md `## Diagrams` -> `a DrawIO Story Map`.

Exercises the Uniform Callable Surface: parse(external) -> StoryMap,
render(canonical, previous=None) -> str, sync(external, canonical) ->
UpdateReport. The DrawIO backend is stateless - every call passes the canonical
StoryMap explicitly, and `DiagramStoryMap` positioning stays an internal detail
of the backend.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

_HERE = Path(__file__).resolve()
for _candidate in _HERE.parents:
    if (_candidate / "context_tools" / "stories" / "src" / "context_tools" / "stories").is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, expect, raise_error

from context_tools.stories.story_model.nodes import Epic, Story, StoryType, SubEpic
from context_tools.stories.story_model.story_map import StoryMap
from context_tools.stories.story_model.thin_slice import Increment
from context_tools.stories.story_model.scenario import Clause, Interaction, Phase, Scenario
from context_tools.stories.diagram.drawio.nodes import (
    DrawIOParseError,
    DrawIOStoryMap,
    LEFT_MARGIN_X,
    SUBEPIC_DEPTH_GAP,
    SUBEPIC_HEIGHT,
)


def _story_map_with_4_epics_and_3_sub_epics_and_1_story() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    first_epic = story_map.epics[0]
    for j in range(1, 4):
        sub = SubEpic(f"SubEpic 1.{j}", j)
        story = Story(f"Story 1.{j}.1", 1, StoryType.USER)
        story.scenarios.append(
            Scenario(name="scenario step", sequential_order=1)
        )
        sub.stories.append(story)
        first_epic.sub_epics.append(sub)
    return story_map


with description("a DrawIO Story Map") as self:
    with before.each:
        self.drawio = DrawIOStoryMap()

    with context(
        "that holds a rendered diagram Story Map with 4 Epics and 3 SubEpics under the first Epic"
    ):
        with before.each:
            self.source = _story_map_with_4_epics_and_3_sub_epics_and_1_story()
            self.text = self.drawio.render(self.source)

        with it("should serialize as a valid DrawIO document"):
            tree = ET.fromstring(self.text)
            expect(tree.tag).to(equal("mxfile"))
            expect(tree.find(".//mxGraphModel") is not None).to(be_true)

        with context("every node"):
            with it("should appear as an mxCell in the document"):
                tree = ET.fromstring(self.text)
                cells = tree.findall(".//mxCell[@vertex='1']")
                expect(cells).to(have_len(10))

        with context("with an Epic appended and the DrawIO document re-rendered"):
            with before.each:
                self.source.append_epic(Epic("Epic 5", 5))
                self.new_text = self.drawio.render(self.source)

            with context("the document"):
                with it(
                    "should contain one additional Epic shape carrying the new Epic's name"
                ):
                    expect("Epic 5" in self.new_text).to(be_true)
                    tree = ET.fromstring(self.new_text)
                    epic_cells = [
                        c
                        for c in tree.findall(".//mxCell[@vertex='1']")
                        if c.attrib.get("style", "").startswith("epic")
                    ]
                    expect(epic_cells).to(have_len(5))

        with context("with the first Epic renamed and the DrawIO document re-rendered"):
            with before.each:
                self.source.epics[0].name = "Epic 1 (renamed)"
                self.new_text = self.drawio.render(self.source)

            with context("the shape for the first Epic"):
                with it("should carry the new name as its label"):
                    expect("Epic 1 (renamed)" in self.new_text).to(be_true)

        with context("with a SubEpic deleted and the DrawIO document re-rendered"):
            with before.each:
                self.source.epics[0].sub_epics.pop(0)
                self.new_text = self.drawio.render(self.source)

            with context("the document"):
                with it(
                    "should no longer contain the shape for the deleted SubEpic or any of its descendants"
                ):
                    expect('value="SubEpic 1.1"' in self.new_text).to(be_false)
                    expect('value="Story 1.1.1"' in self.new_text).to(be_false)

    with context("that has been edited in the DrawIO document and synced back"):
        with before.each:
            self.canonical = _story_map_with_4_epics_and_3_sub_epics_and_1_story()
            edited = _story_map_with_4_epics_and_3_sub_epics_and_1_story()
            edited.epics[0].name = "Epic 1 (edited)"
            edited.append_epic(Epic("Epic 5", 5))
            edited_text = self.drawio.render(edited)
            self.report = self.drawio.sync(edited_text, self.canonical)

        with context("the returned UpdateReport"):
            with it(
                "should list every add, remove, rename, reorder, and move applied to the document"
            ):
                expect(
                    len(self.report.adds()) + len(self.report.renames()) >= 2
                ).to(be_true)

        with context("the reconstructed Story Map"):
            with it("should reflect every edit made to the document"):
                names = [e.name for e in self.canonical.epics]
                expect("Epic 1 (edited)" in names).to(be_true)
                expect("Epic 5" in names).to(be_true)

    with context("that has been rendered and parsed back without edits"):
        with before.each:
            self.original = _story_map_with_4_epics_and_3_sub_epics_and_1_story()
            self.parsed = self.drawio.parse(self.drawio.render(self.original))

        with it("should preserve Story structure - scenarios are NOT embedded in the story-map view"):
            first_story = self.parsed.epics[0].sub_epics[0].stories[0]
            expect(first_story.scenarios).to(have_len(0))

    with context("that is not a valid DrawIO document"):
        with context("the parse"):
            with it("should be rejected"):
                expect(lambda: self.drawio.parse("<not-drawio/>")).to(
                    raise_error(DrawIOParseError)
                )

    with context("rendering the thin-slice view for a StoryMap with 2 increments"):
        with before.each:
            self.source = _story_map_with_4_epics_and_3_sub_epics_and_1_story()
            inc_a = Increment(name="Increment A - first outcome", sequential_order=1)
            inc_a.stories = ["Story 1.1.1", "Story 1.2.1"]
            inc_b = Increment(name="Increment B - second outcome", sequential_order=2)
            inc_b.stories = ["Story 1.3.1"]
            self.source.append_increment(inc_a)
            self.source.append_increment(inc_b)
            self.text = self.drawio.render_thin_slice(self.source)

        with it("should serialize as a valid DrawIO document with mxfile envelope"):
            root_el = ET.fromstring(self.text)
            expect(root_el.tag).to(equal("mxfile"))
            graph_model = root_el.find(".//mxGraphModel")
            expect(graph_model is not None).to(be_true)

        with it("should render epic column headers, inc-lane label + bg cells, and story cells"):
            all_cells = [c for c in ET.fromstring(self.text).findall(".//mxCell[@vertex='1']")]
            epic_cells = [
                c for c in all_cells if c.attrib.get("style", "").startswith("epic")
            ]
            inc_labels = [
                c for c in all_cells if c.attrib.get("style", "").startswith("inc-lane-label;")
            ]
            inc_bgs = [
                c for c in all_cells if c.attrib.get("style", "").startswith("inc-lane;")
            ]
            increment_stories = [
                c for c in all_cells if c.attrib.get("style", "").startswith("increment-story;")
            ]
            expect(len(epic_cells) > 0).to(be_true)
            expect(inc_labels).to(have_len(2))
            expect(inc_bgs).to(have_len(2))
            expect(increment_stories).to(have_len(3))

        with it("should position the second increment lane below the first"):
            tree = ET.fromstring(self.text)
            labels = sorted(
                (
                    c for c in tree.findall(".//mxCell[@vertex='1']")
                    if c.attrib.get("style", "").startswith("inc-lane-label;")
                ),
                key=lambda c: int(c.find("mxGeometry").attrib["y"]),
            )
            expect(labels).to(have_len(2))
            first_y = int(labels[0].find("mxGeometry").attrib["y"])
            second_y = int(labels[1].find("mxGeometry").attrib["y"])
            expect(second_y > first_y).to(be_true)

        with it("should position label cells to the left of the story grid"):
            tree = ET.fromstring(self.text)
            label = next(
                c for c in tree.findall(".//mxCell[@vertex='1']")
                if c.attrib.get("style", "").startswith("inc-lane-label;")
            )
            label_x = int(label.find("mxGeometry").attrib["x"])
            expect(label_x < LEFT_MARGIN_X).to(be_true)

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
            self.text = self.drawio.render_scenario(self.source)

        with it("should serialize as a valid DrawIO document"):
            tree = ET.fromstring(self.text)
            expect(tree.tag).to(equal("mxGraphModel"))

        with it("should render one story cell, one scenario cell, and one clause cell per Clause"):
            tree = ET.fromstring(self.text)
            story_cells = [
                c for c in tree.findall(".//mxCell[@vertex='1']")
                if c.attrib.get("style", "").startswith("story:")
            ]
            scenario_cells = [
                c for c in tree.findall(".//mxCell[@vertex='1']")
                if c.attrib.get("style") == "scenario"
            ]
            clause_cells = [
                c for c in tree.findall(".//mxCell[@vertex='1']")
                if c.attrib.get("style", "").startswith("clause:")
            ]
            expect(story_cells).to(have_len(1))
            expect(scenario_cells).to(have_len(1))
            expect(clause_cells).to(have_len(4))

        with it("should prefix first-of-phase clauses with the phase keyword and leave continuations untouched"):
            expect("Given a Treasurer with a funded Account" in self.text).to(be_true)
            expect("When the Treasurer submits a Transfer" in self.text).to(be_true)
            expect("Then the System returns a Confirmation" in self.text).to(be_true)
            expect("And the Transfer is marked same-day" in self.text).to(be_true)

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
            self.text = self.drawio.render(self.source)
            self.tree = ET.fromstring(self.text)
            self.row_pitch = SUBEPIC_HEIGHT + SUBEPIC_DEPTH_GAP

            self.compose_geo = None
            self.attack_geo = None
            self.extras_geo = None
            self.delivery_geo = None
            for c in self.tree.findall(".//mxCell[@vertex='1']"):
                cid = c.attrib.get("id", "")
                style = c.attrib.get("style", "")
                if not style.startswith("subepic:"):
                    continue
                geo = c.find("mxGeometry")
                if cid.endswith("/compose-powers") and cid.count("/") == 1:
                    self.compose_geo = geo
                elif cid.endswith("/compose-attack-power"):
                    self.attack_geo = geo
                elif cid.endswith("/apply-power-extra") and "delivery" not in cid:
                    self.extras_geo = geo
                elif cid.endswith("/apply-delivery-extra"):
                    self.delivery_geo = geo

        with it("should place depth-0 sub-epics above depth-1 children"):
            expect(self.compose_geo is not None).to(be_true)
            expect(self.attack_geo is not None).to(be_true)
            expect(int(self.compose_geo.attrib["y"])).to(
                equal(int(self.attack_geo.attrib["y"]) - self.row_pitch)
            )

        with it("should place depth-1 sub-epics above depth-2 children"):
            expect(self.extras_geo is not None).to(be_true)
            expect(self.delivery_geo is not None).to(be_true)
            expect(int(self.extras_geo.attrib["y"])).to(
                equal(int(self.delivery_geo.attrib["y"]) - self.row_pitch)
            )

        with it("should span parent width across own stories plus nested children"):
            # Apply Power Extra: 1 own story + Apply Delivery Extra (1 story) = 2 cols
            # width = 2 * 60 - 10 = 110
            expect(int(self.extras_geo.attrib["width"])).to(equal(110))

        with it("should place own stories left of nested child sub-epics"):
            expect(int(self.extras_geo.attrib["x"])).to(
                equal(int(self.delivery_geo.attrib["x"]) - 60)
            )

        with it("should round-trip nested hierarchy"):
            parsed = self.drawio.parse(self.text)
            compose = parsed.epics[0].sub_epics[0]
            expect(compose.name).to(equal("Compose Powers"))
            expect(compose.sub_epics).to(have_len(2))
            extras = compose.sub_epics[1]
            expect(extras.name).to(equal("Apply Power Extra"))
            expect([s.name for s in extras.stories]).to(equal(["Apply Area Extra"]))
            expect(extras.sub_epics).to(have_len(1))
            expect(extras.sub_epics[0].name).to(equal("Apply Delivery Extra"))

    with context("that renders a shaping outline with estimates and no phantom stories"):
        with before.each:
            self.source = StoryMap()
            epic = Epic("Move money", 1)
            epic.estimate = "approx 22-27 total stories"
            compose = SubEpic("Compose transfer", 1)
            compose.stories.append(Story("Draft transfer details", 1, StoryType.USER))
            compose.estimate = "approx 2-3 more stories (validation)"
            approve = SubEpic("Approve transfer", 2)
            approve.estimate = "approx 4-6 more stories (review)"
            epic.sub_epics.extend([compose, approve])
            self.source.append_epic(epic)
            self.text = self.drawio.render(self.source)
            self.tree = ET.fromstring(self.text)

        with it("should render * estimate labels below sub-epics beside stories"):
            estimate_cells = [
                c for c in self.tree.findall(".//mxCell[@vertex='1']")
                if c.attrib.get("style", "").startswith("estimate")
            ]
            expect(estimate_cells).to(have_len(2))
            expect(estimate_cells[0].attrib.get("value", "").startswith("* ")).to(be_true)

        with it("should place epic estimate as plain text above the epic bar"):
            epic_estimate = [
                c for c in self.tree.findall(".//mxCell[@vertex='1']")
                if c.attrib.get("id", "").endswith("/epic-estimate")
            ]
            expect(epic_estimate).to(have_len(1))
            expect(epic_estimate[0].attrib.get("style", "").startswith("text;")).to(be_true)
            expect(epic_estimate[0].attrib.get("value")).to(
                equal("* approx 22-27 total stories")
            )
            geo = epic_estimate[0].find("mxGeometry")
            expect(int(geo.attrib["y"])).to(equal(100))

        with it("should not invent stories that are not on the model"):
            story_cells = [
                c for c in self.tree.findall(".//mxCell[@vertex='1']")
                if c.attrib.get("style", "").startswith("story:")
            ]
            expect(story_cells).to(have_len(1))

        with context("parsed back from the diagram"):
            with before.each:
                self.parsed = self.drawio.parse(self.text)

            with it("should round-trip estimates on epic and sub-epics"):
                expect(self.parsed.epics[0].estimate).to(
                    equal("approx 22-27 total stories")
                )
                expect(self.parsed.epics[0].sub_epics[0].estimate).to(
                    equal("approx 2-3 more stories (validation)")
                )
                expect(self.parsed.epics[0].sub_epics[1].estimate).to(
                    equal("approx 4-6 more stories (review)")
                )
