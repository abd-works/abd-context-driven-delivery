"""Mamba spec for `a Story Map`.

Mirrors the `## Story Model` -> `a Story Map` block of bdd-context.md 1:1.
Uses Epic / SubEpic / Story / Scenario / Increment from this same package.
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _candidate in _HERE.parents:
    if (_candidate / "contexts" / "stories" / "src" / "contexts" / "stories").is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, expect

from contexts.stories.story_model.nodes import Epic, Story, StoryType, SubEpic
from contexts.stories.story_model.scenario import Scenario
from contexts.stories.story_model.story_map import StoryMap
from contexts.stories.story_model.thin_slice import Increment


def _fresh_story_map_with_4_epics() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    return story_map


def _fresh_sub_epics(count: int) -> list:
    return [SubEpic(f"SubEpic {i}", i) for i in range(1, count + 1)]


def _fresh_stories(count: int) -> list:
    return [Story(f"Story {i}", i, StoryType.USER) for i in range(1, count + 1)]


def _fresh_scenarios(count: int) -> list:
    return [Scenario(f"Scenario {i}", i) for i in range(1, count + 1)]


def _fresh_increments(count: int) -> list:
    return [Increment(f"Increment {i}", i) for i in range(1, count + 1)]


with description("a Story Map") as self:
    with it("should hold no Epics"):
        story_map = StoryMap()
        expect(story_map.epics).to(have_len(0))

    with it("should hold no Increments"):
        story_map = StoryMap()
        expect(story_map.increments).to(have_len(0))

    with context("with 4 Epics in sequential order"):
        with before.each:
            self.story_map = _fresh_story_map_with_4_epics()

        with it("should hold 4 Epics"):
            expect(self.story_map.epics).to(have_len(4))

        with it("should list the Epics in sequential order"):
            orders = [epic.sequential_order for epic in self.story_map.epics]
            expect(orders).to(equal([1, 2, 3, 4]))

        with context("with a fifth Epic appended"):
            with before.each:
                self.story_map.append_epic(Epic("Epic 5", 5))

            with it("should hold 5 Epics"):
                expect(self.story_map.epics).to(have_len(5))

            with context("the last Epic in sequential order"):
                with it("should be the appended Epic"):
                    expect(self.story_map.epics[-1].name).to(equal("Epic 5"))

        with context("with the first Epic removed"):
            with before.each:
                first_epic = self.story_map.epics[0]
                first_epic.sub_epics.extend(_fresh_sub_epics(2))
                self.story_map.remove_epic("Epic 1")

            with it("should hold 3 Epics"):
                expect(self.story_map.epics).to(have_len(3))

            with it("should discard the SubEpics that lived under the removed Epic"):
                remaining_names = [e.name for e in self.story_map.epics]
                expect("Epic 1" in remaining_names).to(be_false)

            with it("should renumber the remaining Epics"):
                orders = [e.sequential_order for e in self.story_map.epics]
                expect(orders).to(equal([1, 2, 3]))

        with context("with the first Epic renamed"):
            with before.each:
                self.story_map.epics[0].name = "Epic 1 (renamed)"

            with it("should preserve the sequential order of the Epics"):
                orders = [e.sequential_order for e in self.story_map.epics]
                expect(orders).to(equal([1, 2, 3, 4]))

            with context("the first Epic"):
                with it("should carry the new name"):
                    expect(self.story_map.epics[0].name).to(equal("Epic 1 (renamed)"))

        with context("with the Epics reordered"):
            with before.each:
                self.story_map.reorder_epics(["Epic 4", "Epic 2", "Epic 3", "Epic 1"])

            with it("should list the Epics in the new order"):
                names = [e.name for e in self.story_map.epics]
                expect(names).to(equal(["Epic 4", "Epic 2", "Epic 3", "Epic 1"]))

            with it("should reflect each Epic's new position in its sequential order"):
                orders = [e.sequential_order for e in self.story_map.epics]
                expect(orders).to(equal([1, 2, 3, 4]))

        with context("with the first Epic holding 3 SubEpics"):
            with before.each:
                self.first_epic = self.story_map.epics[0]
                self.first_epic.sub_epics.extend(_fresh_sub_epics(3))

            with context("the first Epic"):
                with it("should hold 3 SubEpics"):
                    expect(self.first_epic.sub_epics).to(have_len(3))

            with context("with a SubEpic appended to the first Epic"):
                with before.each:
                    self.first_epic.sub_epics.append(SubEpic("SubEpic 4", 4))

                with context("the first Epic"):
                    with it("should hold 4 SubEpics"):
                        expect(self.first_epic.sub_epics).to(have_len(4))

            with context("with the first SubEpic of the first Epic removed"):
                with before.each:
                    self.first_epic.sub_epics[0].stories.extend(_fresh_stories(2))
                    self.first_epic.sub_epics.pop(0)

                with context("the first Epic"):
                    with it("should hold 2 SubEpics"):
                        expect(self.first_epic.sub_epics).to(have_len(2))

                    with it("should discard the Stories that lived under the removed SubEpic"):
                        remaining_names = [s.name for s in self.first_epic.sub_epics]
                        expect("SubEpic 1" in remaining_names).to(be_false)

            with context("with the first SubEpic of the first Epic renamed"):
                with before.each:
                    self.first_epic.sub_epics[0].name = "SubEpic 1 (renamed)"

                with context("the first SubEpic of the first Epic"):
                    with it("should carry the new name"):
                        expect(self.first_epic.sub_epics[0].name).to(
                            equal("SubEpic 1 (renamed)")
                        )

            with context("with a nested SubEpic added under the first SubEpic"):
                with before.each:
                    self.first_epic.sub_epics[0].sub_epics.append(
                        SubEpic("Nested SubEpic", 1)
                    )

                with context("the first SubEpic of the first Epic"):
                    with it("should hold 1 nested SubEpic"):
                        expect(self.first_epic.sub_epics[0].sub_epics).to(have_len(1))

                    with it("should report hasSubEpics as true"):
                        expect(self.first_epic.sub_epics[0].has_sub_epics).to(be_true)

            with context(
                "with the first SubEpic moved from the first Epic to the second Epic"
            ):
                with before.each:
                    self.first_epic.sub_epics[0].stories.extend(_fresh_stories(1))
                    self.first_epic.sub_epics[0].stories[0].scenarios.extend(
                        _fresh_scenarios(1)
                    )
                    self.second_epic = self.story_map.epics[1]
                    self.original_second_epic_size = len(self.second_epic.sub_epics)
                    self.moved = self.first_epic.sub_epics.pop(0)
                    self.second_epic.sub_epics.append(self.moved)

                with context("the first Epic"):
                    with it("should hold 2 SubEpics"):
                        expect(self.first_epic.sub_epics).to(have_len(2))

                with context("the second Epic"):
                    with it("should hold one additional SubEpic"):
                        expect(self.second_epic.sub_epics).to(
                            have_len(self.original_second_epic_size + 1)
                        )

                with context("the moved SubEpic"):
                    with it("should keep its Stories and their Scenarios"):
                        moved_story = self.moved.stories[0]
                        expect(self.moved.stories).to(have_len(1))
                        expect(moved_story.scenarios).to(have_len(1))

            with context("with the first SubEpic of the first Epic holding 2 Stories"):
                with before.each:
                    self.first_sub_epic = self.first_epic.sub_epics[0]
                    self.first_sub_epic.stories.extend(_fresh_stories(2))

                with context("the first SubEpic of the first Epic"):
                    with it("should hold 2 Stories"):
                        expect(self.first_sub_epic.stories).to(have_len(2))

                with context("with a Story appended to the first SubEpic"):
                    with before.each:
                        self.first_sub_epic.stories.append(
                            Story("Story 3", 3, StoryType.USER)
                        )

                    with context("the first SubEpic of the first Epic"):
                        with it("should hold 3 Stories"):
                            expect(self.first_sub_epic.stories).to(have_len(3))

                with context("with the first Story of the first SubEpic removed"):
                    with before.each:
                        self.first_sub_epic.stories[0].scenarios.extend(
                            _fresh_scenarios(2)
                        )
                        self.first_sub_epic.stories.pop(0)

                    with context("the first SubEpic of the first Epic"):
                        with it("should hold 1 Story"):
                            expect(self.first_sub_epic.stories).to(have_len(1))

                        with it("should discard the Scenarios that lived under the removed Story"):
                            remaining_names = [
                                s.name for s in self.first_sub_epic.stories
                            ]
                            expect("Story 1" in remaining_names).to(be_false)

                with context("with the first Story of the first SubEpic renamed"):
                    with before.each:
                        self.first_sub_epic.stories[0].name = "Story 1 (renamed)"

                    with context("the first Story of the first SubEpic"):
                        with it("should carry the new name"):
                            expect(self.first_sub_epic.stories[0].name).to(
                                equal("Story 1 (renamed)")
                            )

                with context("with the first Story typed as system"):
                    with before.each:
                        self.first_sub_epic.stories[0].story_type = StoryType.SYSTEM

                    with context("the first Story of the first SubEpic"):
                        with it("should carry the StoryType system"):
                            expect(self.first_sub_epic.stories[0].story_type).to(
                                equal(StoryType.SYSTEM)
                            )

                with context(
                    "with the first Story moved from the first SubEpic to the second SubEpic"
                ):
                    with before.each:
                        self.first_sub_epic.stories[0].scenarios.extend(
                            _fresh_scenarios(1)
                        )
                        self.second_sub_epic = self.first_epic.sub_epics[1]
                        self.original_second_sub_epic_stories = len(
                            self.second_sub_epic.stories
                        )
                        self.moved_story = self.first_sub_epic.stories.pop(0)
                        self.second_sub_epic.stories.append(self.moved_story)

                    with context("the first SubEpic of the first Epic"):
                        with it("should hold 1 Story"):
                            expect(self.first_sub_epic.stories).to(have_len(1))

                    with context("the second SubEpic of the first Epic"):
                        with it("should hold one additional Story"):
                            expect(self.second_sub_epic.stories).to(
                                have_len(self.original_second_sub_epic_stories + 1)
                            )

                    with context("the moved Story"):
                        with it("should keep its Scenarios"):
                            expect(self.moved_story.scenarios).to(have_len(1))

                with context(
                    "with the first Story of the first SubEpic holding 3 Scenarios"
                ):
                    with before.each:
                        self.first_story = self.first_sub_epic.stories[0]
                        self.first_story.scenarios.extend(_fresh_scenarios(3))

                    with context("the first Story of the first SubEpic"):
                        with it("should hold 3 Scenarios"):
                            expect(self.first_story.scenarios).to(have_len(3))

                    with context("with a Scenario appended to the first Story"):
                        with before.each:
                            self.first_story.scenarios.append(Scenario("Scenario 4", 4))

                        with context("the first Story of the first SubEpic"):
                            with it("should hold 4 Scenarios"):
                                expect(self.first_story.scenarios).to(have_len(4))

                        with context("the last Scenario in sequential order"):
                            with it("should be the appended Scenario"):
                                expect(self.first_story.scenarios[-1].name).to(
                                    equal("Scenario 4")
                                )

                    with context("with the first Scenario of the first Story removed"):
                        with before.each:
                            self.first_story.scenarios.pop(0)
                            for i, sc in enumerate(self.first_story.scenarios, start=1):
                                sc.sequential_order = i

                        with context("the first Story of the first SubEpic"):
                            with it("should hold 2 Scenarios"):
                                expect(self.first_story.scenarios).to(have_len(2))

                            with it("should renumber the remaining Scenarios"):
                                orders = [
                                    sc.sequential_order
                                    for sc in self.first_story.scenarios
                                ]
                                expect(orders).to(equal([1, 2]))

                    with context("with the first Scenario of the first Story renamed"):
                        with before.each:
                            self.first_story.scenarios[0].name = "Scenario 1 (renamed)"

                        with context("the first Scenario of the first Story"):
                            with it("should carry the new name"):
                                expect(self.first_story.scenarios[0].name).to(
                                    equal("Scenario 1 (renamed)")
                                )

                    with context(
                        "with the given clauses of the first Scenario updated"
                    ):
                        with before.each:
                            from contexts.stories.story_model.scenario import Clause, Phase
                            self.new_given = [Clause("a new given clause", Phase.GIVEN)]
                            self.first_story.scenarios[0].given = self.new_given

                        with context("the first Scenario of the first Story"):
                            with it("should carry the new given clauses"):
                                expect(
                                    self.first_story.scenarios[0].given
                                ).to(equal(self.new_given))

                            with it("should preserve its name and sequentialOrder"):
                                expect(self.first_story.scenarios[0].name).to(
                                    equal("Scenario 1")
                                )
                                expect(
                                    self.first_story.scenarios[0].sequential_order
                                ).to(equal(1))

                    with context(
                        "with the interactions of the first Scenario replaced"
                    ):
                        with before.each:
                            from contexts.stories.story_model.scenario import (
                                Clause,
                                Interaction,
                                Phase,
                            )
                            self.new_interactions = [
                                Interaction(
                                    when=[Clause("new when", Phase.WHEN)],
                                    then=[Clause("new then", Phase.THEN)],
                                )
                            ]
                            self.first_story.scenarios[0].interactions = (
                                self.new_interactions
                            )

                        with context("the first Scenario of the first Story"):
                            with context("its when and then clauses"):
                                with it("should reflect the new interactions"):
                                    expect(
                                        self.first_story.scenarios[0].when_clauses[0].text
                                    ).to(equal("new when"))
                                    expect(
                                        self.first_story.scenarios[0].then_clauses[0].text
                                    ).to(equal("new then"))

                    with context("with the Scenarios of the first Story reordered"):
                        with before.each:
                            self.first_story.scenarios = [
                                self.first_story.scenarios[2],
                                self.first_story.scenarios[0],
                                self.first_story.scenarios[1],
                            ]

                        with context("the first Story of the first SubEpic"):
                            with it("should list the Scenarios in the new order"):
                                names = [sc.name for sc in self.first_story.scenarios]
                                expect(names).to(
                                    equal(["Scenario 3", "Scenario 1", "Scenario 2"])
                                )

    with context("with 2 Increments in sequential order"):
        with before.each:
            self.story_map = StoryMap()
            for inc in _fresh_increments(2):
                self.story_map.append_increment(inc)

        with it("should hold 2 Increments"):
            expect(self.story_map.increments).to(have_len(2))

        with it("should list the Increments in sequential order"):
            orders = [inc.sequential_order for inc in self.story_map.increments]
            expect(orders).to(equal([1, 2]))

        with context("with an Increment appended"):
            with before.each:
                self.story_map.append_increment(Increment("Increment 3", 3))

            with it("should hold 3 Increments"):
                expect(self.story_map.increments).to(have_len(3))

            with context("the last Increment in sequential order"):
                with it("should be the appended Increment"):
                    expect(self.story_map.increments[-1].name).to(equal("Increment 3"))

        with context("with the first Increment removed"):
            with before.each:
                self.story_map.remove_increment("Increment 1")

            with it("should hold 1 Increment"):
                expect(self.story_map.increments).to(have_len(1))

            with it("should renumber the remaining Increment"):
                expect(self.story_map.increments[0].sequential_order).to(equal(1))

        with context("with the first Increment renamed"):
            with before.each:
                self.story_map.increments[0].name = "Increment 1 (renamed)"

            with context("the first Increment"):
                with it("should carry the new name"):
                    expect(self.story_map.increments[0].name).to(
                        equal("Increment 1 (renamed)")
                    )

        with context("with the outcome of the first Increment updated"):
            with before.each:
                self.story_map.increments[0].outcome = "Transfers clear same day"

            with context("the first Increment"):
                with it("should carry the new outcome"):
                    expect(self.story_map.increments[0].outcome).to(
                        equal("Transfers clear same day")
                    )

                with it("should preserve its name and sequentialOrder"):
                    expect(self.story_map.increments[0].name).to(equal("Increment 1"))
                    expect(self.story_map.increments[0].sequential_order).to(equal(1))

        with context("with a story name added to the first Increment"):
            with before.each:
                self.story_map.increments[0].stories.append("Route transfer before cutoff")

            with context("the first Increment"):
                with it("should hold one additional story name"):
                    expect(self.story_map.increments[0].stories).to(have_len(1))

                with context("its story-name list"):
                    with it("should remain a list of name strings, not Story object references"):
                        item = self.story_map.increments[0].stories[0]
                        expect(isinstance(item, str)).to(be_true)

        with context("with the Increments reordered"):
            with before.each:
                self.story_map.reorder_increments(["Increment 2", "Increment 1"])

            with it("should list the Increments in the new order"):
                names = [inc.name for inc in self.story_map.increments]
                expect(names).to(equal(["Increment 2", "Increment 1"]))
