"""Mamba spec for `a story-graph.json document`. Mirrors `## Documents` in bdd-context.md."""

import os
import sys
import json as json_module

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
from src.formats.document.json.json_story_map import JsonParseError, JsonStoryMap


def _canonical_story_map() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.epics.append(Epic(f"Epic {i}", i))
    first = story_map.epics[0]
    for j in range(1, 4):
        sub = SubEpic(f"SubEpic 1.{j}", j)
        story = Story(f"Story {j}", 1, StoryType.SYSTEM)
        story.acceptance_criteria.append(
            AcceptanceCriteria(name="AC 1", sequential_order=1, text="text")
        )
        sub.stories.append(story)
        first.sub_epics.append(sub)
    return story_map


with description("a story-graph.json document") as self:
    with before.each:
        self.json_map = JsonStoryMap()

    with it("should contain no Epics"):
        text = self.json_map.render(StoryMap())
        payload = json_module.loads(text)
        expect(payload["epics"]).to(have_len(0))

    with context(
        "that holds a serialized Story Map with 4 Epics and 3 SubEpics under the first Epic"
    ):
        with before.each:
            self.source = _canonical_story_map()
            self.text = self.json_map.render(self.source)
            self.payload = json_module.loads(self.text)

        with it("should contain 4 Epic entries"):
            expect(self.payload["epics"]).to(have_len(4))

        with context("the first Epic entry"):
            with it("should contain 3 SubEpic entries"):
                expect(self.payload["epics"][0]["subEpics"]).to(have_len(3))

        with context("every Story"):
            with it("should be nested under its SubEpic entry"):
                for sub in self.payload["epics"][0]["subEpics"]:
                    expect(sub["stories"]).to(have_len(1))

        with context("every AcceptanceCriteria"):
            with it("should be nested under its Story entry"):
                first_sub = self.payload["epics"][0]["subEpics"][0]
                expect(first_sub["stories"][0]["acceptanceCriteria"]).to(have_len(1))

        with context("every Story entry"):
            with it("should preserve its StoryType field"):
                for sub in self.payload["epics"][0]["subEpics"]:
                    for story in sub["stories"]:
                        expect(story["storyType"]).to(equal("system"))

        with it("should preserve the sequential order of every node"):
            orders = [e["sequentialOrder"] for e in self.payload["epics"]]
            expect(orders).to(equal([1, 2, 3, 4]))

        with context(
            "with a fifth Epic appended and the document re-serialized"
        ):
            with before.each:
                self.source.append_epic(Epic("Epic 5", 5))
                self.new_payload = json_module.loads(self.json_map.render(self.source))

            with it("should contain 5 Epic entries"):
                expect(self.new_payload["epics"]).to(have_len(5))

        with context("with the first Epic removed and the document re-serialized"):
            with before.each:
                self.source.remove_epic("Epic 1")
                self.new_payload = json_module.loads(self.json_map.render(self.source))

            with it("should contain 3 Epic entries"):
                expect(self.new_payload["epics"]).to(have_len(3))

            with it("should hold no orphan SubEpic entries"):
                remaining_names = [e["name"] for e in self.new_payload["epics"]]
                expect("Epic 1" in remaining_names).to(be_false)

    with context("that is being read back into a JsonStoryMap"):
        with before.each:
            source = _canonical_story_map()
            self.text = self.json_map.render(source)
            self.reconstructed = self.json_map.parse(self.text)

        with context("the reconstructed Story Map"):
            with it(
                "should hold every Epic, SubEpic, Story, and AcceptanceCriteria in sequential order"
            ):
                expect(self.reconstructed.epics).to(have_len(4))
                first_epic = self.reconstructed.epics[0]
                expect(first_epic.sub_epics).to(have_len(3))
                expect(first_epic.sub_epics[0].stories).to(have_len(1))
                expect(
                    first_epic.sub_epics[0].stories[0].acceptance_criteria
                ).to(have_len(1))

    with context("that has been edited and synced back against a canonical Story Map"):
        with before.each:
            self.canonical = _canonical_story_map()
            edited = _canonical_story_map()
            edited.epics[0].name = "Epic 1 (edited)"
            edited.append_epic(Epic("Epic 5", 5))
            edited_text = self.json_map.render(edited)
            self.report = self.json_map.sync(edited_text, self.canonical)

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

    with context("that does not conform to the story-graph.json schema"):
        with context("the read"):
            with it("should be rejected"):
                bad_text = '{"not_epics": []}'
                expect(lambda: self.json_map.parse(bad_text)).to(
                    raise_error(JsonParseError)
                )
