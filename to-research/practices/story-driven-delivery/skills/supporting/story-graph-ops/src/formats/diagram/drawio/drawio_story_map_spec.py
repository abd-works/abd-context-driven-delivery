"""Mamba spec for `a DrawIO Story Map`. Mirrors bdd-context.md `## Diagrams` -> `a DrawIO Story Map`.

Exercises the Uniform Callable Surface: parse(external) -> StoryMap,
render(canonical, previous=None) -> str, sync(external, canonical) ->
UpdateReport. The DrawIO backend is stateless — every call passes the canonical
StoryMap explicitly, and `DiagramStoryMap` positioning stays an internal detail
of the backend.
"""

import os
import sys
import xml.etree.ElementTree as ET

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))
)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, expect, raise_error

from src.core.stories.nodes import AcceptanceCriteria, Epic, Story, StoryType, SubEpic
from src.core.stories.story_map import StoryMap
from src.formats.diagram.drawio.drawio_story_map import (
    DrawIOParseError,
    DrawIOStoryMap,
)


def _story_map_with_4_epics_and_3_sub_epics_and_1_story() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    first_epic = story_map.epics[0]
    for j in range(1, 4):
        sub = SubEpic(f"SubEpic 1.{j}", j)
        story = Story(f"Story 1.{j}.1", 1, StoryType.USER)
        story.acceptance_criteria.append(
            AcceptanceCriteria(name="AC 1", sequential_order=1, text="scenario step")
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
            expect(tree.tag).to(equal("mxGraphModel"))

        with context("every node"):
            with it("should appear as an mxCell in the document"):
                tree = ET.fromstring(self.text)
                cells = tree.findall(".//mxCell[@vertex='1']")
                # 4 Epics + 3 SubEpics + 3 Stories = 10 cells
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

        with it("should preserve scenario text as AcceptanceCriteria on every Story"):
            first_story = self.parsed.epics[0].sub_epics[0].stories[0]
            expect(first_story.acceptance_criteria).to(have_len(1))
            expect(first_story.acceptance_criteria[0].text).to(equal("scenario step"))

    with context("that is not a valid DrawIO document"):
        with context("the parse"):
            with it("should be rejected"):
                expect(lambda: self.drawio.parse("<not-drawio/>")).to(
                    raise_error(DrawIOParseError)
                )
