"""Mamba spec for `an Increment`.

Mirrors the `## Increment` block of bdd-context.md 1:1.
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _candidate in _HERE.parents:
    if (_candidate / "stories" / "src" / "stories").is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from mamba import description, context, it, before
from expects import equal, have_len, be_true, expect

from stories.src.stories.model.nodes import Epic, Story, StoryType, SubEpic
from stories.src.stories.model.story_map import StoryMap
from stories.src.stories.model.thin_slice import Increment


with description("an Increment") as self:
    with it("should report itself as a leaf StoryNode"):
        inc = Increment("Move money same-day", 1)
        expect(inc.semantic_type()).to(equal("Increment"))

    with it("should return an empty list from childCollections"):
        inc = Increment("Move money same-day", 1)
        expect(inc.child_collections(inc)).to(equal([]))

    with context(
        "that has been translated from another Increment of the same semantic type"
    ):
        with before.each:
            source = Increment("Source Increment", 2)
            source.outcome = "Transfers clear same day"
            source.slicing_notes = "Manual dual-control step for first release"
            source.stories = ["Route transfer before cutoff", "Display transfer status"]
            source.decision_prompt = "Did same-day transfers increase retention?"

            self.target = Increment("placeholder", 99)
            self.target.translate_from(source)
            self.source = source

        with it(
            "should carry every field from the source "
            "(name, sequentialOrder, outcome, slicingNotes, stories, decisionPrompt)"
        ):
            expect(self.target.name).to(equal("Source Increment"))
            expect(self.target.sequential_order).to(equal(2))
            expect(self.target.outcome).to(equal("Transfers clear same day"))
            expect(self.target.slicing_notes).to(
                equal("Manual dual-control step for first release")
            )
            expect(self.target.stories).to(
                equal(["Route transfer before cutoff", "Display transfer status"])
            )
            expect(self.target.decision_prompt).to(
                equal("Did same-day transfers increase retention?")
            )

        with context("its stories list"):
            with it(
                "should be a value copy of story-name strings, not object references "
                "to Story nodes"
            ):
                self.source.stories.append("Extra story")
                # Target must not grow
                expect(self.target.stories).to(have_len(2))

    with context(
        "that references a story name not present in any Story on the StoryMap"
    ):
        with before.each:
            self.story_map = StoryMap()
            epic = Epic("Route transfer", 1)
            sub = SubEpic("Route inside window", 1)
            sub.stories.append(Story("Route transfer before cutoff", 1))
            epic.sub_epics.append(sub)
            self.story_map.append_epic(epic)
            orphan = Increment("Orphan increment", 1)
            orphan.stories = ["Non-existent story name"]
            self.story_map.append_increment(orphan)

        with context("the model"):
            with it("should not raise"):
                # Building the model with orphan references is allowed —
                # scanners detect the inconsistency, not the model.
                expect(len(self.story_map.increments)).to(equal(1))

        with context("a scanner walking the StoryMap"):
            with it(
                "should be able to detect the orphan reference by comparing name lists"
            ):
                all_story_names = {
                    story.name
                    for epic in self.story_map.epics
                    for sub in epic.sub_epics
                    for story in sub.all_stories_recursive()
                }
                orphan_refs = [
                    name
                    for inc in self.story_map.increments
                    for name in inc.stories
                    if name not in all_story_names
                ]
                expect(orphan_refs).to(equal(["Non-existent story name"]))
