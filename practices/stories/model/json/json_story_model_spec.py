"""Mamba spec for `a story-graph.json document`. Mirrors `## Documents` in ../../bdd-context.md."""

import json as json_module
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _candidate in _HERE.parents:
    if (_candidate / "practices" / "stories" / "src" / "practices" / "stories").is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, expect, raise_error

from practices.stories.model.story_model import Epic, Story, StoryType, Epic
from practices.stories.model.story_model import Scenario
from practices.stories.model.story_model import StoryModel
from practices.stories.model.json.nodes import JsonParseError, JsonStoryModel


class SpecFixture:
    def canonical_story_map(self) -> StoryModel:
        story_map = StoryModel()
        for i in range(1, 5):
            story_map.epics.append(Epic(f"Epic {i}", i))
        first = story_map.epics[0]
        for j in range(1, 4):
            sub = Epic(f"Epic 1.{j}", j)
            story = Story(f"Story {j}", 1, StoryType.SYSTEM)
            story.scenarios.append(
                Scenario(name="scenario text", sequential_order=1)
            )
            sub.stories.append(story)
            first.epics.append(sub)
        return story_map


fixture = SpecFixture()


with description("a story-graph.json document") as self:
    with before.each:
        self.json_map = JsonStoryModel()

    with it("should contain no Epics"):
        text = self.json_map.render(StoryModel())
        payload = json_module.loads(text)
        expect(payload["epics"]).to(have_len(0))

    with context(
        "that holds a serialized Story Map with 4 Epics and 3 Epics under the first Epic"
    ):
        with before.each:
            self.source = fixture.canonical_story_map()
            self.text = self.json_map.render(self.source)
            self.payload = json_module.loads(self.text)

        with it("should contain 4 Epic entries"):
            expect(self.payload["epics"]).to(have_len(4))

        with context("the first Epic entry"):
            with it("should contain 3 Epic entries"):
                expect(self.payload["epics"][0]["subEpics"]).to(have_len(3))

        with context("every Story"):
            with it("should be nested under its Epic entry"):
                for sub in self.payload["epics"][0]["subEpics"]:
                    expect(sub["stories"]).to(have_len(1))

        with context("every Scenario"):
            with it("should be nested under its Story entry"):
                first_sub = self.payload["epics"][0]["subEpics"][0]
                expect(first_sub["stories"][0]["scenarios"]).to(have_len(1))

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
                self.source.epics.pop(0)
                self.new_payload = json_module.loads(self.json_map.render(self.source))

            with it("should contain 3 Epic entries"):
                expect(self.new_payload["epics"]).to(have_len(3))

            with it("should hold no orphan Epic entries"):
                remaining_names = [e["name"] for e in self.new_payload["epics"]]
                expect("Epic 1" in remaining_names).to(be_false)

    with context("that is being read back into a JsonStoryModel"):
        with before.each:
            source = fixture.canonical_story_map()
            self.text = self.json_map.render(source)
            self.reconstructed = self.json_map.parse(self.text)

        with context("the reconstructed Story Map"):
            with it(
                "should hold every Epic, Epic, Story, and Scenario in sequential order"
            ):
                expect(self.reconstructed.epics).to(have_len(4))
                first_epic = self.reconstructed.epics[0]
                expect(first_epic.epics).to(have_len(3))
                expect(first_epic.epics[0].stories).to(have_len(1))
                expect(
                    first_epic.epics[0].stories[0].scenarios
                ).to(have_len(1))

    with context("that does not conform to the story-graph.json schema"):
        with context("the read"):
            with it("should be rejected"):
                bad_text = '{"not_epics": []}'
                expect(lambda: self.json_map.parse(bad_text)).to(
                    raise_error(JsonParseError)
                )
