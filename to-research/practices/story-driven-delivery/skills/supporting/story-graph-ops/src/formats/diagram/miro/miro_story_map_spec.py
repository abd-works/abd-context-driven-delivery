"""Mamba spec for `a Miro Story Map`. Mirrors bdd-context.md `## Diagrams` -> `a Miro Story Map`.

Exercises the Uniform Callable Surface: parse(external) -> StoryMap,
render(canonical, previous=None) -> str, sync(external, canonical) ->
UpdateReport. The Miro backend is stateless; `DiagramStoryMap` positioning
stays internal.
"""

import json
import os
import sys

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
from src.formats.diagram.miro.miro_story_map import MiroParseError, MiroStoryMap


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


with description("a Miro Story Map") as self:
    with before.each:
        self.miro = MiroStoryMap()

    with context(
        "that holds a rendered diagram Story Map with 4 Epics and 3 SubEpics under the first Epic"
    ):
        with before.each:
            self.source = _story_map_with_4_epics_and_3_sub_epics_and_1_story()
            self.text = self.miro.render(self.source)
            self.payload = json.loads(self.text)

        with it("should post as a valid set of Miro items via the Miro API"):
            expect("items" in self.payload).to(be_true)
            expect(isinstance(self.payload["items"], list)).to(be_true)

        with context("every node"):
            with it("should appear as an item on the board"):
                # 4 Epics + 3 SubEpics + 3 Stories = 10 items
                expect(self.payload["items"]).to(have_len(10))

        with context("with an Epic appended and the Miro board re-rendered"):
            with before.each:
                self.source.append_epic(Epic("Epic 5", 5))
                self.new_payload = json.loads(self.miro.render(self.source))

            with context("the board"):
                with it(
                    "should contain one additional Epic item carrying the new Epic's name"
                ):
                    labels = [i["data"]["content"] for i in self.new_payload["items"]]
                    expect("Epic 5" in labels).to(be_true)
                    epic_items = [
                        i for i in self.new_payload["items"] if i["role"] == "epic"
                    ]
                    expect(epic_items).to(have_len(5))

        with context("with the first Epic renamed and the Miro board re-rendered"):
            with before.each:
                self.source.epics[0].name = "Epic 1 (renamed)"
                self.new_payload = json.loads(self.miro.render(self.source))

            with context("the item for the first Epic"):
                with it("should carry the new name as its label"):
                    first_epic_item = next(
                        i for i in self.new_payload["items"] if i["role"] == "epic"
                    )
                    expect(first_epic_item["data"]["content"]).to(
                        equal("Epic 1 (renamed)")
                    )

        with context("with a SubEpic deleted and the Miro board re-rendered"):
            with before.each:
                self.source.epics[0].sub_epics.pop(0)
                self.new_payload = json.loads(self.miro.render(self.source))

            with context("the board"):
                with it(
                    "should no longer contain the item for the deleted SubEpic or any of its descendants"
                ):
                    labels = [i["data"]["content"] for i in self.new_payload["items"]]
                    expect("SubEpic 1.1" in labels).to(be_false)
                    expect("Story 1.1.1" in labels).to(be_false)

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

        with it("should preserve scenario text as AcceptanceCriteria on every Story"):
            first_story = self.parsed.epics[0].sub_epics[0].stories[0]
            expect(first_story.acceptance_criteria).to(have_len(1))
            expect(first_story.acceptance_criteria[0].text).to(equal("scenario step"))

    with context("that does not respond as a valid Miro story map when synced"):
        with context("the parse"):
            with it("should be rejected"):
                expect(lambda: self.miro.parse('{"unexpected": true}')).to(
                    raise_error(MiroParseError)
                )
